"""Lots de colonnes du rejeu, phase 2 (PLAN_EXPERIENCE.md, 5.5, 5.10, 5.11 et 5.13).

Un lot est une suite (`suites.Suite`) dont les colonnes sont rangées en groupes : la couche R0 (un seul groupe, les R0
répétitions), une tranche de répétitions bootstrap (un groupe par répétition, K ordres chacun), ou le jackknife (un
groupe par tâche retirée, K ordres chacun). Chaque écriture porte sa grappe : l'occurrence de tâche à laquelle elle
appartient (la tâche dans R0 et le jackknife ; le rang du tirage dans le bootstrap), pour l'écart type linéarisé du
bootstrap-t (5.13).

Choix de la phase 2 (CHOIX_PHASE2.md) :
- le tirage des tâches d'une répétition bootstrap est commun aux trois modèles d'un environnement et aux deux
  segments d'un scénario (5.10 : « les deux segments utilisent le même tirage de tâches ») : graine
  SeedSequence([G0, usage 1, environnement, code « tous modèles » = 3, scénario 0, couche 1, b, jeu, 0]). Les
  moyennes sur les configurations et le max-T voient ainsi la corrélation par les tâches (5.13 : l'unité est la tâche) ;
- les ordres, les tirages du validateur et les clés des épreuves gardent la disposition de la phase 1 (choix 20) ;
- jackknife : la tâche g est retirée des K premières colonnes de la couche R0 (mêmes ordres, mêmes tirages attachés aux
  écritures restantes : nombres aléatoires communs) ; la relance (5.13) prend 4 K colonnes ;
- scénario (env, X, Y) : numéro 1 à 6 (couple ordonné), le même pour les deux modes ; segment de X dans un ordre tiré
  avec la graine « ordre » de X, puis segment de Y avec celle de Y ; validateur et épreuves avec la graine de X et le
  numéro du scénario ;
- sensibilités à l'ordre (Q5) : « par passage » (scénario 100) et « ordre réel de jeu » (scénario 101).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Optional

import numpy as np

from . import config_rejeu as CR
from . import epreuves as EP
from . import suites as SU
from . import temoins as TM
from . import types_regle as TY

CODE_TOUS_MODELES = len(CR.MODELES)
SCENARIO_PAR_PASSAGE, SCENARIO_ORDRE_REEL = 100, 101
PART_RATEE = 0.10            # rate10 et ratées groupées (5.11)
RETARD = 10                  # retard10 (5.11)
MODES_RESISTANCE = ("rate10", "retard10", "groupees")
CHAMPS_TR = ("typ", "plaf", "ver", "reu", "errp", "errd", "den", "apart", "partie", "rang", "outil", "u_val",
             "grappe", "u_hasard", "u_res", "rate")


# --------------------------------------------------------------------------
# Tâches canoniques, tirage commun
# --------------------------------------------------------------------------
def taches_canoniques(jeu) -> tuple:
    """(liste des tâches dans l'ordre des strates triées puis des tâches triées, {tâche: indice}, strate de chaque
    tâche (indice), noms des strates)."""
    noms = list(jeu.strates)
    taches, strate = [], []
    for h, s in enumerate(noms):
        for t in jeu.strates[s]:
            taches.append(t)
            strate.append(h)
    return taches, {t: i for i, t in enumerate(taches)}, np.array(strate, dtype=np.int64), noms


def tirage_commun(G0: int, environnement: str, b: int, nom_jeu: str, strates: dict) -> dict:
    """{strate: indices tirés} de la répétition bootstrap b, commun aux modèles et aux segments (graine sans modèle)."""
    ss = np.random.SeedSequence([int(G0), CR.USAGES["reechantillonnage"], CR.ENVIRONNEMENTS.index(environnement),
                                 CODE_TOUS_MODELES, 0, CR.COUCHES["bootstrap"], int(b), CR.JEUX[nom_jeu], 0])
    rng = np.random.default_rng(ss)
    return {s: rng.integers(0, len(t), size=len(t)) for s, t in strates.items()}


def unites_tirage(jeu, tirage: dict) -> list:
    """Unités (partie, copie, grappe) d'un tirage : rangées par strate, tirage, ordre canonique (comme la phase 1)."""
    unites, decal = [], 0
    for s, taches in jeu.strates.items():
        for copie, j in enumerate(tirage[s].tolist()):
            unites += [(i, copie, decal + copie) for i in jeu.parties_par_tache.get(taches[j], ())]
        decal += len(taches)
    return unites


def unites_r0(jeu) -> list:
    _, index, _, _ = taches_canoniques(jeu)
    return [(i, 0, index[e.partie.tache]) for i, e in enumerate(jeu.parties)]


def permuter(unites: list, ss: np.random.SeedSequence) -> list:
    perm = np.random.default_rng(ss).permutation(len(unites))
    return [unites[i] for i in perm.tolist()]


# --------------------------------------------------------------------------
# Le lot
# --------------------------------------------------------------------------
@dataclass
class Lot:
    suite: SU.Suite
    couche: str                 # « R0 », « bootstrap », « jackknife »
    groupe: np.ndarray          # (R,) groupe de chaque colonne
    n_groupes: int
    G: int                      # grappes : tâches de S gardées
    strate_grappe: np.ndarray   # (G,) strate de chaque grappe
    par_grappe: dict            # {nom: (n_groupes, G)} : den, ecr, dou, lec, pre, act (une colonne du groupe)
    taches: tuple               # tâches canoniques
    repetitions: list = field(default_factory=list)   # numéro de chaque groupe (b, ou la tâche retirée)
    nX: int = 0                 # scénarios : parties de X (numérotées d'abord)
    outils: tuple = ()
    jeu: object = None          # le JeuConfiguration (combiné pour un scénario)

    def grappes_moteur(self) -> dict:
        return dict(groupe=self.groupe, n_groupes=self.n_groupes, G=self.G)

    @property
    def K_groupe(self) -> np.ndarray:
        return np.bincount(self.groupe, minlength=self.n_groupes)


def _par_partie(jeu) -> dict:
    """Comptes par partie : écritures au dénominateur, écritures, doutes, lectures, préparations, actions."""
    n = jeu.n_parties
    L = jeu.longueurs.astype(np.int64)
    part_de = np.repeat(np.arange(n), L) if n else np.zeros(0, dtype=np.int64)
    den = np.bincount(part_de, weights=jeu.attrs["den"].astype(float), minlength=n).astype(np.int64) if n \
        else np.zeros(0, dtype=np.int64)
    return dict(den=den, ecr=L, dou=np.asarray(jeu.n_doutes, dtype=np.int64),
                lec=np.asarray(jeu.n_lectures, dtype=np.int64), pre=np.asarray(jeu.n_preparations, dtype=np.int64),
                act=np.asarray(jeu.n_actions, dtype=np.int64))


def _par_grappe_colonne(pp: dict, unites: list, G: int) -> dict:
    """Comptes d'une colonne, par grappe (pp : comptes par partie)."""
    if not unites:
        return {k: np.zeros(G, dtype=np.int64) for k in pp}
    p = np.fromiter((u[0] for u in unites), dtype=np.int64, count=len(unites))
    g = np.fromiter((u[2] for u in unites), dtype=np.int64, count=len(unites))
    return {k: np.bincount(g, weights=v[p].astype(float), minlength=G).astype(np.int64) for k, v in pp.items()}


def _grappe_colonnes(jeu, colonnes: list, T: int) -> np.ndarray:
    gr = np.full((T, len(colonnes)), -1, dtype=np.int32)
    Lp = jeu.longueurs
    for c, col in enumerate(colonnes):
        if not col:
            continue
        L = Lp[[u[0] for u in col]]
        v = np.repeat(np.array([u[2] for u in col], dtype=np.int32), L)
        gr[:v.size, c] = v
    return gr


def _attacher_tirages(suite: SU.Suite) -> SU.Suite:
    """Tirages du hasard apparié et de la résistance, attachés aux écritures (graines de la colonne)."""
    suite.u_hasard = TM.tirages_hasard(suite)
    u = np.ones((suite.T, suite.R))
    for c in range(suite.R):
        u[:, c] = np.random.default_rng(suite.graine("resistance", c)).random(suite.T)
    suite.u_res = u
    return suite


def _construire(jeu, colonnes: list, G0: int, couche: str, reps: list, ordres: list, scenario: int,
                groupe: np.ndarray, n_groupes: int, repetitions: list, nX: int = 0) -> Lot:
    taches, _, strate, _ = taches_canoniques(jeu)
    G = len(taches)
    cols2 = [[(u[0], u[1]) for u in col] for col in colonnes]
    suite = SU.assembler(jeu, cols2, G0, couche if couche != "jackknife" else "R0", reps, ordres, scenario)
    suite.grappe = _grappe_colonnes(jeu, colonnes, suite.T)
    _attacher_tirages(suite)
    L = jeu.longueurs.astype(np.int64)
    if nX:
        suite.jonction = np.array([int(L[[u[0] for u in col if u[0] < nX]].sum()) for col in colonnes],
                                  dtype=np.int64)
    pp = _par_partie(jeu)
    par = {k: np.zeros((n_groupes, G), dtype=np.int64) for k in pp}
    vus = set()
    for c, col in enumerate(colonnes):
        g = int(groupe[c])
        if g in vus:
            continue
        vus.add(g)
        for k, v in _par_grappe_colonne(pp, col, G).items():
            par[k][g] = v
    return Lot(suite=suite, couche=couche, groupe=np.asarray(groupe, dtype=np.int64), n_groupes=n_groupes, G=G,
               strate_grappe=strate, par_grappe=par, taches=tuple(taches), repetitions=list(repetitions), nX=nX,
               outils=tuple(jeu.outils), jeu=jeu)


# --------------------------------------------------------------------------
# Configurations constantes
# --------------------------------------------------------------------------
def lot_r0(jeu, G0: int, R: int, scenario: int = 0) -> Lot:
    """Couche R0 : les mêmes colonnes que `suites.suite_r0` (phase 1), avec leurs grappes."""
    _, index, _, _ = taches_canoniques(jeu)
    colonnes = []
    for r in range(R):
        col = SU.ordre_unites(jeu, G0, "R0", r, 0, scenario)
        colonnes.append([(p, c, index[jeu.parties[p].partie.tache]) for p, c in col])
    return _construire(jeu, colonnes, G0, "R0", list(range(R)), [0] * R, scenario, np.zeros(R, dtype=np.int64), 1,
                       [0])


def lot_bootstrap(jeu, G0: int, reps, K: int, scenario: int = 0) -> Lot:
    """Répétitions bootstrap `reps` (tirage commun des tâches), K ordres chacune."""
    env, mod, nom = jeu.environnement, jeu.modele, jeu.jeu
    colonnes, rr, oo, groupe = [], [], [], []
    for gi, b in enumerate(reps):
        un = unites_tirage(jeu, tirage_commun(G0, env, b, nom, jeu.strates))
        for k in range(K):
            colonnes.append(permuter(un, SU.graine(G0, "ordre", env, mod, scenario, "bootstrap", b, nom, k)))
            rr.append(b)
            oo.append(k)
            groupe.append(gi)
    return _construire(jeu, colonnes, G0, "bootstrap", rr, oo, scenario, np.array(groupe), len(reps), list(reps))


def lot_ordre_impose(jeu, G0: int, R: int, ordre: str, scenario: int) -> Lot:
    """Sensibilités à l'ordre des parties (Q5 ; 5.14, point 6) : « par_passage » (chaque passage mélangé, les passages
    dans l'ordre) ou « reel » (l'ordre réel de jeu, par heure de début : une seule suite, R tirages du validateur)."""
    env, mod, nom = jeu.environnement, jeu.modele, jeu.jeu
    base = unites_r0(jeu)
    colonnes = []
    for r in range(R):
        if ordre == "reel":
            col = sorted(base, key=lambda u: (jeu.parties[u[0]].partie.debut, jeu.parties[u[0]].partie.id))
        elif ordre == "par_passage":
            passages = sorted({jeu.parties[u[0]].partie.passage for u in base})
            col = []
            for p in passages:
                sous = [u for u in base if jeu.parties[u[0]].partie.passage == p]
                col += permuter(sous, SU.graine(G0, "ordre", env, mod, scenario, "R0", r, nom, int(p)))
        else:
            raise ValueError(ordre)
        colonnes.append(col)
    return _construire(jeu, colonnes, G0, "R0", list(range(R)), [0] * R, scenario, np.zeros(R, dtype=np.int64), 1,
                       [0])


# --------------------------------------------------------------------------
# Jackknife : une tâche retirée des K premières colonnes de R0
# --------------------------------------------------------------------------
def lot_jackknife(base: Lot) -> Lot:
    """Une colonne par (tâche retirée g, colonne k du lot de base), mêmes ordres et tirages attachés ; groupes = g."""
    s = base.suite
    Kb, G = s.R, base.G
    cols, groupe, keep_cols = [], [], []
    for g in range(G):
        for k in range(Kb):
            garde = (s.grappe[:, k] != g) & (s.typ[:, k] >= 0)
            cols.append(np.nonzero(garde)[0])
            groupe.append(g)
            keep_cols.append(k)
    T = max((c.size for c in cols), default=0)
    R = len(cols)
    arr = {}
    for nom in CHAMPS_TR:
        x = getattr(s, nom)
        if x is None:
            arr[nom] = None
            continue
        rem = {"typ": TY.VIDE, "partie": -1, "grappe": -1, "u_val": 1.0, "u_hasard": 1.0, "u_res": 1.0}.get(nom, 0)
        out = np.full((T, R), rem, dtype=x.dtype)
        for c, (rows, k) in enumerate(zip(cols, keep_cols)):
            out[:rows.size, c] = x[rows, k]
        arr[nom] = out
    pg = base.par_grappe
    kc = np.array(keep_cols)
    grp = np.array(groupe)
    moins = lambda tot, cle: tot[kc] - pg[cle][0, grp]  # noqa: E731
    jonction = None
    if s.jonction is not None:
        jonction = np.array([int(((rows < s.jonction[k])).sum()) for rows, k in zip(cols, keep_cols)],
                            dtype=np.int64)
    meta = dict(s.meta)
    meta.update(repetitions=[s.meta["repetitions"][k] for k in keep_cols], ordres=[s.meta["ordres"][k]
                                                                                   for k in keep_cols],
                unites=None, jackknife=True)
    suite = SU.Suite(T=T, R=R, typ=arr["typ"], plaf=arr["plaf"], ver=arr["ver"], reu=arr["reu"], errp=arr["errp"],
                     errd=arr["errd"], den=arr["den"], apart=arr["apart"], partie=arr["partie"], rang=arr["rang"],
                     outil=arr["outil"], u_val=arr["u_val"], n_doutes=moins(s.n_doutes, "dou"),
                     n_lectures=moins(s.n_lectures, "lec"), n_preparations=moins(s.n_preparations, "pre"),
                     n_actions=moins(s.n_actions, "act"), cles_epreuves=tuple(s.cles_epreuves[k] for k in keep_cols),
                     meta=meta, grappe=arr["grappe"], jonction=jonction, u_hasard=arr["u_hasard"],
                     u_res=arr["u_res"], rate=arr["rate"])
    par = {}
    for cle, v in pg.items():
        tot = v[0]
        par[cle] = np.stack([np.where(np.arange(G) == g, 0, tot) for g in range(G)])
    return Lot(suite=suite, couche="jackknife", groupe=grp, n_groupes=G, G=G, strate_grappe=base.strate_grappe,
               par_grappe=par, taches=base.taches, repetitions=list(base.taches), nX=base.nX, outils=base.outils,
               jeu=base.jeu)


# --------------------------------------------------------------------------
# Scénarios de changement de modèle (5.10)
# --------------------------------------------------------------------------
def couples(modeles=CR.MODELES) -> list:
    """Les 6 couples ordonnés (X, Y), numérotés 1 à 6."""
    return [(x, y) for x in modeles for y in modeles if x != y]


def numero_scenario(X: str, Y: str) -> int:
    return couples().index((X, Y)) + 1


def jeu_combine(jX, jY):
    """G(c, S) de X puis de Y, mis bout à bout (parties de Y décalées de nX), outils recodés sur leur réunion."""
    outils = tuple(sorted(set(jX.outils) | set(jY.outils)))
    code = {o: i for i, o in enumerate(outils)}
    recode = lambda j: np.array([code[j.outils[o]] for o in j.outil.tolist()], dtype=np.int32)  # noqa: E731
    nX = jX.n_parties
    par_tache: dict = {}
    for t, v in jX.parties_par_tache.items():
        par_tache.setdefault(t, []).extend(v)
    for t, v in jY.parties_par_tache.items():
        par_tache.setdefault(t, []).extend(i + nX for i in v)
    debut = np.concatenate([jX.debut, jY.debut[1:] + jX.debut[-1]])
    if jX.strates != jY.strates:
        raise ValueError("scénario : X et Y n'ont pas les mêmes tâches (strates)")
    return replace(jX, parties=list(jX.parties) + list(jY.parties), debut=debut,
                   typ=np.concatenate([jX.typ, jY.typ]),
                   attrs={a: np.concatenate([jX.attrs[a], jY.attrs[a]]) for a in jX.attrs},
                   rang=np.concatenate([jX.rang, jY.rang]), outil=np.concatenate([recode(jX), recode(jY)]),
                   outils=outils, n_lectures=np.concatenate([jX.n_lectures, jY.n_lectures]),
                   n_preparations=np.concatenate([jX.n_preparations, jY.n_preparations]),
                   n_doutes=np.concatenate([jX.n_doutes, jY.n_doutes]),
                   n_actions=np.concatenate([jX.n_actions, jY.n_actions]),
                   parties_par_tache={t: tuple(v) for t, v in par_tache.items()}), nX


def _unites_scenario(jX, jY, nX: int, unX: list, unY: list, G0: int, s: int, couche: str, rep: int, k: int):
    env, nom = jX.environnement, jX.jeu
    a = permuter(unX, SU.graine(G0, "ordre", env, jX.modele, s, couche, rep, nom, k))
    b = permuter(unY, SU.graine(G0, "ordre", env, jY.modele, s, couche, rep, nom, k))
    return a + [(p + nX, c, g) for p, c, g in b]


def lot_scenario_r0(jX, jY, G0: int, R: int) -> Lot:
    jc, nX = jeu_combine(jX, jY)
    s = numero_scenario(jX.modele, jY.modele)
    unX, unY = unites_r0(jX), unites_r0(jY)
    colonnes = [_unites_scenario(jX, jY, nX, unX, unY, G0, s, "R0", r, 0) for r in range(R)]
    return _construire(jc, colonnes, G0, "R0", list(range(R)), [0] * R, s, np.zeros(R, dtype=np.int64), 1, [0],
                       nX=nX)


def lot_scenario_bootstrap(jX, jY, G0: int, reps, K: int) -> Lot:
    jc, nX = jeu_combine(jX, jY)
    s = numero_scenario(jX.modele, jY.modele)
    colonnes, rr, oo, groupe = [], [], [], []
    for gi, b in enumerate(reps):
        t = tirage_commun(G0, jX.environnement, b, jX.jeu, jX.strates)
        unX, unY = unites_tirage(jX, t), unites_tirage(jY, t)
        for k in range(K):
            colonnes.append(_unites_scenario(jX, jY, nX, unX, unY, G0, s, "bootstrap", b, k))
            rr.append(b)
            oo.append(k)
            groupe.append(gi)
    return _construire(jc, colonnes, G0, "bootstrap", rr, oo, s, np.array(groupe), len(reps), list(reps), nX=nX)


# --------------------------------------------------------------------------
# Tests de résistance (5.11)
# --------------------------------------------------------------------------
def taches_ratees(lot: Lot, part: float = PART_RATEE) -> list:
    """Ratées groupées : ⌈part × G⌉ tâches par colonne, tirées sans remise avec la graine « résistance » de la colonne
    (dans le jackknife, celles de la colonne de base)."""
    s = lot.suite
    n = max(1, math.ceil(part * lot.G)) if lot.G else 0
    out = []
    for c in range(s.R):
        rng = np.random.default_rng(s.graine("resistance", c).spawn(1)[0])   # flux enfant, distinct de u_res
        out.append(frozenset(lot.taches[i] for i in rng.choice(lot.G, size=n, replace=False).tolist()) if n else
                   frozenset())
    return out


def transformer_resistance(lot: Lot, mode: str, ratees: Optional[list] = None) -> Lot:
    """rate10 : 10 % des erreurs confirmées, tirées avec u_res, ne sont pas vues ; ratées groupées : toutes les erreurs
    des tâches tirées. La règle les compte comme des réussites ; elles restent des dégâts (`errd` inchangé)."""
    s = lot.suite
    if mode == "rate10":
        non_vue = s.errp & (s.u_res < PART_RATEE)
    elif mode == "groupees":
        ratees = ratees if ratees is not None else taches_ratees(lot)
        idx_t = {t: i for i, t in enumerate(lot.taches)}
        tache_partie = np.array([idx_t.get(e.partie.tache, -1) for e in lot.jeu.parties], dtype=np.int64)
        tache_ecr = np.where(s.partie >= 0, tache_partie[np.maximum(s.partie, 0)], -1)
        masque = np.zeros(s.typ.shape, dtype=bool)
        for c in range(s.R):
            ids = [idx_t[t] for t in ratees[c]]
            masque[:, c] = np.isin(tache_ecr[:, c], ids)
        non_vue = s.errp & masque
    else:
        raise ValueError(mode)
    suite = replace(s, reu=s.reu | non_vue, errp=s.errp & ~non_vue, rate=non_vue)
    return replace(lot, suite=suite)


def non_vues_epreuves(lot: Lot, mode: str, ratees: Optional[list] = None):
    """Le prédicat des erreurs non vues dans les variantes d'épreuve (même mode que la suite)."""
    s = lot.suite
    if mode == "rate10":
        cles = [SU.entier_64(s.graine("resistance", c)) for c in range(s.R)]
        return EP.NonVuesTaux(cles, PART_RATEE)
    if mode == "groupees":
        return EP.NonVuesTaches(ratees if ratees is not None else taches_ratees(lot))
    return None
