"""Les épreuves, jouées à blanc (PLAN_EXPERIENCE.md, 5.9 ; Q3 tranchée par Claude). Code nouveau : E1 tirait l'issue
d'une loi binomiale à partir du taux des cas difficiles de l'agent fictif (`simuler_e1`, étape 2).

- Une épreuve, ce sont 3 variantes du cas fautif (pièces 7 et 8) : 3 parties enregistrées, tirées (graine
  « épreuves ») dans le jeu d'origine G(c, S) — même dans la couche bootstrap —, jouées par le modèle courant, sur la
  même tâche que le cas, sans la partie fautive. S'il y en a moins de 3, on complète par des parties où le modèle a
  utilisé le même outil, puis le même type. Si les replis ne donnent pas 3 variantes, l'épreuve est impossible : elle
  reste ouverte et le type reste au palier 1 jusqu'à la fin de la suite (M7).
- Réussite d'une variante : au moins une écriture du type jugée « juste », et aucune erreur confirmée du type.
  L'épreuve est réussie si les 3 variantes le sont.
- À blanc : les écritures des variantes ne font aucun dégât et n'entrent pas dans la suite ; chaque essai compte 3
  validations dans la charge des épreuves (décision 6). Les effets sur la règle sont ceux de `resultat_epreuve` des
  références (moteur).

Tirage (CHOIX_PHASE1.md) : rang de hachage SplitMix64 de chaque candidat, sous une clé qui combine la graine
« épreuves » de la répétition, le type, le cas (partie et rang de l'écriture fautive) et le numéro de l'essai sur
l'épreuve ouverte de ce cas. Les règles qui passent le même essai du même cas reçoivent donc les mêmes
variantes (appariement), et le résultat d'une règle ne dépend pas des autres règles rejouées avec elle.
"""
from __future__ import annotations

from collections import namedtuple
from dataclasses import dataclass

import numpy as np

from . import types_regle as TY

REUSSIE, RATEE, IMPOSSIBLE = "réussie", "ratée", "impossible"
N_VARIANTES = 3
Cas = namedtuple("Cas", "partie rang outil")  # l'écriture fautive : partie (index dans G(c, S)), rang, code d'outil


@dataclass(frozen=True)
class Issue:
    statut: str
    variantes: tuple = ()

    @property
    def validations(self) -> int:
        """Charge de l'essai : 3 validations s'il a été joué (rien pour une épreuve impossible)."""
        return len(self.variantes)


# --------------------------------------------------------------------------
# SplitMix64 (mêmes nombres en Python pur et en numpy)
# --------------------------------------------------------------------------
_MASQUE = (1 << 64) - 1
_GAMMA, _M1, _M2 = 0x9E3779B97F4A7C15, 0xBF58476D1CE4E5B9, 0x94D049BB133111EB


def melanger(x: int) -> int:
    z = (x + _GAMMA) & _MASQUE
    z = ((z ^ (z >> 30)) * _M1) & _MASQUE
    z = ((z ^ (z >> 27)) * _M2) & _MASQUE
    return z ^ (z >> 31)


def melanger_tableau(x: np.ndarray) -> np.ndarray:
    z = np.asarray(x, dtype=np.uint64) + np.uint64(_GAMMA)
    z = (z ^ (z >> np.uint64(30))) * np.uint64(_M1)
    z = (z ^ (z >> np.uint64(27))) * np.uint64(_M2)
    return z ^ (z >> np.uint64(31))


def combiner(*parts) -> int:
    h = 0
    for p in parts:
        h = melanger(h ^ (int(p) & _MASQUE))
    return h


# --------------------------------------------------------------------------
# Le vivier des variantes : G(c, S) d'une configuration
# --------------------------------------------------------------------------
class PoolEpreuves:
    """Parties candidates aux variantes, pour un jeu `suites.JeuConfiguration` (un modèle, un environnement)."""

    def __init__(self, jeu):
        n = jeu.n_parties
        self.n = n
        self.tache = [e.partie.tache for e in jeu.parties]
        par_tache, par_outil, par_type = {}, {}, {}
        succes = np.zeros((n, TY.NT), dtype=bool)
        for i in range(n):
            sl = slice(int(jeu.debut[i]), int(jeu.debut[i + 1]))
            typ, out = jeu.typ[sl], jeu.outil[sl]
            reu, errp = jeu.attrs["reu"][sl], jeu.attrs["errp"][sl]
            par_tache.setdefault(self.tache[i], []).append(i)
            for o in set(out.tolist()):
                par_outil.setdefault(o, []).append(i)
            for k in set(typ.tolist()):
                par_type.setdefault(k, []).append(i)
                m = typ == k
                succes[i, k] = bool(reu[m].any()) and not bool(errp[m].any())
        a = lambda d: {k: np.array(v, dtype=np.int64) for k, v in d.items()}  # noqa: E731
        self.par_tache, self.par_outil, self.par_type = a(par_tache), a(par_outil), a(par_type)
        self.succes = succes
        self._niveaux: dict = {}   # les niveaux ne dépendent que du vivier, du type et du cas : calculés une fois
        # Phase 2 : noms des outils (scénarios : un cas d'un modèle rejoué sur les parties d'un autre) et écritures de
        # chaque partie (réussite d'une variante quand des erreurs ne sont pas vues, 5.11).
        self.outils = tuple(getattr(jeu, "outils", ()))
        self.code_outil = {o: i for i, o in enumerate(self.outils)}
        self.ident = 0
        self._jeu = jeu

    def niveaux_tache(self, type_: int, tache, outil: int, exclues: frozenset = frozenset()) -> list:
        """Les trois niveaux pour un cas venu d'un autre vivier (scénarios, 5.10 : épreuve passée sur les parties du
        modèle courant) : même tâche, même outil (code de ce vivier, −1 s'il n'y figure pas), même type ; aucune partie
        à exclure, la partie fautive n'étant pas dans ce vivier."""
        cle = ("tache", int(type_), str(tache), int(outil), exclues)
        if cle in self._niveaux:
            return self._niveaux[cle]
        vides = np.zeros(0, dtype=np.int64)
        exclus: set = {i for i in range(self.n) if self.tache[i] in exclues}
        sortie = []
        for cands in (self.par_tache.get(tache, vides), self.par_outil.get(int(outil), vides),
                      self.par_type.get(int(type_), vides)):
            c = np.array([i for i in cands.tolist() if i not in exclus], dtype=np.int64)
            exclus.update(c.tolist())
            sortie.append(c)
        self._niveaux[cle] = sortie
        return sortie

    def tirer_tache(self, cle: int, type_: int, tache, outil: int, exclues: frozenset = frozenset()):
        return self._choisir(cle, self.niveaux_tache(type_, tache, outil, exclues))

    def succes_non_vues(self, v: int, type_: int, non_vue) -> bool:
        """Réussite de la variante v quand des erreurs ne sont pas vues (5.11) : non_vue(rang) dit si l'erreur de
        l'écriture de ce rang passe inaperçue ; une erreur non vue compte comme une réussite."""
        j = self._jeu
        sl = slice(int(j.debut[v]), int(j.debut[v + 1]))
        m = j.typ[sl] == type_
        if not m.any():
            return False
        reu, errp = j.attrs["reu"][sl][m], j.attrs["errp"][sl][m]
        rangs = j.rang[sl][m] if getattr(j, "rang", None) is not None else np.arange(int(m.sum()))
        invisible = np.array([bool(e) and bool(non_vue(int(r))) for e, r in zip(errp.tolist(), rangs.tolist())],
                             dtype=bool)
        vues = errp & ~invisible
        return bool((reu | invisible).any()) and not bool(vues.any())

    def niveaux(self, type_: int, cas: Cas, exclues: frozenset = frozenset()) -> list:
        """Les trois niveaux de candidats (même tâche, même outil, même type), sans la partie fautive ni les parties
        d'un niveau précédent ; en jackknife, sans aucune partie des tâches retirées de la colonne (`exclues`, audit
        du moteur, 09/11), à tous les niveaux."""
        cle = (int(type_), int(cas.partie), int(cas.outil), exclues)
        if cle in self._niveaux:
            return self._niveaux[cle]
        vides = np.zeros(0, dtype=np.int64)
        exclus = {int(cas.partie)} | {i for i in range(self.n) if self.tache[i] in exclues}
        sortie = []
        for cands in (self.par_tache.get(self.tache[cas.partie], vides), self.par_outil.get(int(cas.outil), vides),
                      self.par_type.get(int(type_), vides)):
            c = np.array([i for i in cands.tolist() if i not in exclus], dtype=np.int64)
            exclus.update(c.tolist())
            sortie.append(c)
        self._niveaux[cle] = sortie
        return sortie

    def tirer(self, cle: int, type_: int, cas: Cas, exclues: frozenset = frozenset()):
        """Les 3 variantes (index de parties), ou None si l'épreuve est impossible."""
        return self._choisir(cle, self.niveaux(type_, cas, exclues))

    def _choisir(self, cle: int, niveaux: list):
        choisies = []
        for cands in niveaux:
            besoin = N_VARIANTES - len(choisies)
            if besoin == 0:
                break
            if cands.size <= besoin:
                choisies += cands.tolist()
            else:
                rangs = melanger_tableau(np.uint64(cle) ^ cands.astype(np.uint64))
                choisies += cands[np.argsort(rangs, kind="stable")[:besoin]].tolist()
        return tuple(choisies) if len(choisies) == N_VARIANTES else None


# --------------------------------------------------------------------------
# Fournisseurs d'issues (le moteur les appelle quand une épreuve est due)
# --------------------------------------------------------------------------
def _issue(pool: PoolEpreuves, variantes, type_: int, colonne: int, non_vues) -> Issue:
    if variantes is None:
        return Issue(IMPOSSIBLE)
    if non_vues is None:
        ok = all(bool(pool.succes[v, type_]) for v in variantes)
    else:
        ok = all(pool.succes_non_vues(v, type_, lambda r, v=v: non_vues(colonne, pool, v, r)) for v in variantes)
    return Issue(REUSSIE if ok else RATEE, variantes)


class FournisseurParties:
    """Issues tirées dans des parties enregistrées (production). non_vues(colonne, vivier, partie, rang) : erreurs non
    vues des tests de résistance (5.11), None sinon."""

    def __init__(self, pool: PoolEpreuves, cles_colonnes, non_vues=None, exclues=None):
        self.pool = pool
        self.cles = [int(c) for c in cles_colonnes]
        self.non_vues = non_vues
        self.exclues = exclues   # jackknife : tâches retirées, une liste par colonne (audit du moteur, 09/11)

    def _exclues(self, colonne: int) -> frozenset:
        return self.exclues[colonne] if self.exclues is not None else frozenset()

    def issue(self, ligne: int, t: int, colonne: int, type_: int, cas: Cas, tentative: int) -> Issue:
        cle = combiner(self.cles[colonne], type_, cas.partie, cas.rang, tentative)
        return _issue(self.pool, self.pool.tirer(cle, type_, cas, self._exclues(colonne)), type_, colonne,
                      self.non_vues)


class FournisseurScenario:
    """Épreuves d'un scénario de changement de modèle (5.10) : jouées par le modèle courant. Avant la jonction de la
    colonne, sur les parties de X ; à partir de la jonction (épreuves converties comprises, et épreuves restées
    ouvertes en mode silencieux), sur celles de Y, pour la tâche du cas. Les parties de la suite sont numérotées X
    d'abord (0 … nX − 1), puis Y ; les codes d'outil sont ceux de la suite (`outils`, noms)."""

    def __init__(self, pool_X: PoolEpreuves, pool_Y: PoolEpreuves, nX: int, cles_colonnes, jonction, outils,
                 non_vues=None, exclues=None):
        self.pool_X, self.pool_Y, self.nX = pool_X, pool_Y, int(nX)
        self.cles = [int(c) for c in cles_colonnes]
        self.jonction = np.asarray(jonction, dtype=np.int64)
        self.outils = tuple(outils)
        self.non_vues = non_vues
        self.exclues = exclues   # jackknife : tâches retirées, une liste par colonne (audit du moteur, 09/11)

    def _outil(self, pool: PoolEpreuves, code: int) -> int:
        nom = self.outils[code] if 0 <= code < len(self.outils) else None
        return pool.code_outil.get(nom, -1)

    def issue(self, ligne: int, t: int, colonne: int, type_: int, cas: Cas, tentative: int) -> Issue:
        cle = combiner(self.cles[colonne], type_, cas.partie, cas.rang, tentative)
        ex = self.exclues[colonne] if self.exclues is not None else frozenset()
        if t < self.jonction[colonne]:
            pool = self.pool_X
            v = pool.tirer(cle, type_, Cas(cas.partie, cas.rang, self._outil(pool, cas.outil)), ex)
        else:
            pool = self.pool_Y
            if cas.partie >= self.nX:
                v = pool.tirer(cle, type_, Cas(cas.partie - self.nX, cas.rang, self._outil(pool, cas.outil)), ex)
            else:
                v = pool.tirer_tache(cle, type_, self.pool_X.tache[cas.partie], self._outil(pool, cas.outil), ex)
        return _issue(pool, v, type_, colonne, self.non_vues)


class NonVuesTaux:
    """rate10 (5.11) : chaque erreur passe inaperçue avec la probabilité `part`, par un hachage de la graine
    « résistance » de la colonne, du vivier, de la partie et du rang (les mêmes pour toutes les règles)."""

    def __init__(self, cles_colonnes, part: float = 0.10):
        self.cles = [int(c) for c in cles_colonnes]
        self.part = float(part)

    def __call__(self, colonne: int, pool: PoolEpreuves, partie: int, rang: int) -> bool:
        return combiner(self.cles[colonne], pool.ident, partie, rang) / 2.0 ** 64 < self.part


class NonVuesTaches:
    """Ratées groupées (5.11) : toutes les erreurs des tâches tirées pour la colonne passent inaperçues."""

    def __init__(self, taches_par_colonne):
        self.taches = [frozenset(t) for t in taches_par_colonne]

    def __call__(self, colonne: int, pool: PoolEpreuves, partie: int, rang: int) -> bool:
        return pool.tache[partie] in self.taches[colonne]


class FournisseurImpose:
    """Issues imposées {(ligne, t, type): statut} : rejeu d'un journal (tests d'équivalence et de non-régression)."""

    def __init__(self, issues: dict):
        self.issues = dict(issues)

    def issue(self, ligne: int, t: int, colonne: int, type_: int, cas: Cas, tentative: int) -> Issue:
        statut = self.issues[(ligne, t, type_)]
        if statut is True or statut == REUSSIE:
            return Issue(REUSSIE, (0,) * N_VARIANTES)
        if statut is False or statut == RATEE:
            return Issue(RATEE, (0,) * N_VARIANTES)
        return Issue(IMPOSSIBLE)


class FournisseurConstant:
    """Toujours la même issue (suites piège : épreuves toujours réussies, comme executer_e1.suite_piege)."""

    def __init__(self, statut: str = REUSSIE):
        self.statut = statut

    def issue(self, ligne, t, colonne, type_, cas, tentative) -> Issue:
        return Issue(self.statut, () if self.statut == IMPOSSIBLE else (0,) * N_VARIANTES)
