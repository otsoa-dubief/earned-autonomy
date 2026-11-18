"""Construire les suites (PLAN_EXPERIENCE.md, 5.5). Code nouveau : E1 tirait des flux fictifs de longueur fixe
(`regle_e1.flux_e1`).

Pour une configuration c (modèle m, environnement e) et un jeu S :
1. G(c, S) : les parties de m dans e, sur les tâches de S ; on retire les tâches retirées et les parties en échec
   technique (une partie arrêtée par les 100 tours ou les 30 minutes est gardée) ;
2. une répétition : (i) rééchantillonnage, couche bootstrap seulement : dans chaque strate, on tire avec remise autant
   de tâches que S en compte, chaque tâche tirée apporte toutes ses parties ; (ii) ordre : permutation uniforme des
   parties (Q5) ; (iii) mise bout à bout, chaque partie garde l'ordre de ses actions ; (iv) tri : lectures,
   préparations et doutes retirés et comptés par partie (`preuves`) ; (v) la suite : les écritures et les actions
   « inconnu » qui restent ;
3. tirages de chaque répétition : u_val par écriture (validateur), tirages des épreuves, du hasard ; les mêmes pour
   toutes les règles et tous les témoins ;
4. graines : `graine` (disposition dans CHOIX_PHASE1.md) ;
5. couches : R0 répétitions sans rééchantillonnage ; B répétitions bootstrap de K ordres chacune (intervalles :
   phase 2) ;
6. longueurs variables : complétées par le code VIDE, qui ne change aucun état et n'est compté nulle part.

Ordre de rejeu figé et sa reconstitution (section 8, « Tranché par Claude ») : les parties de G(c, S) sont rangées
dans un ordre canonique (tâche, passage, identifiant) ; une répétition est une liste d'« unités » (partie, copie) — la
copie distingue les tirages répétés d'une même tâche dans le bootstrap — rangées par strate, puis par tirage, puis
dans l'ordre canonique ; la permutation de l'usage « ordre » s'applique à cette liste. `ordre_unites` refait cette
liste à partir de G0 et des indices, sans rien d'autre.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from . import config_rejeu as CR
from . import types_regle as TY
from .entrees import strate as strate_de

ATTRIBUTS = ("plaf", "ver", "reu", "errp", "errd", "den", "apart")


# --------------------------------------------------------------------------
# Graines (5.5, point 4)
# --------------------------------------------------------------------------
def graine(G0: int, usage: str, environnement: str, modele: str, scenario: int = 0, couche: str = "R0",
           repetition: int = 0, jeu: str = "confirmation", ordre: int = 0) -> np.random.SeedSequence:
    """SeedSequence([G0, usage, environnement, modèle, scénario, couche, répétition, jeu, ordre]).

    Les sept premiers champs sont ceux du plan (5.5, point 4) ; « jeu » distingue les jeux rejoués (confirmation,
    calibration, réserve, développement) et « ordre » l'ordre k d'une répétition bootstrap (0 dans la couche R0)."""
    return np.random.SeedSequence([int(G0), CR.USAGES[usage], CR.ENVIRONNEMENTS.index(environnement),
                                   CR.MODELES.index(modele), int(scenario), CR.COUCHES[couche], int(repetition),
                                   CR.JEUX[jeu], int(ordre)])


def entier_64(ss: np.random.SeedSequence) -> int:
    return int(ss.generate_state(1, np.uint64)[0])


# --------------------------------------------------------------------------
# G(c, S)
# --------------------------------------------------------------------------
@dataclass
class JeuConfiguration:
    """G(c, S) et ses écritures, à plat : la partie i occupe les positions debut[i]:debut[i + 1]."""
    environnement: str
    modele: str
    jeu: str
    taches: tuple             # tâches de S gardées (hors tâches retirées), triées
    strates: dict             # strate -> tâches de S gardées, triées
    parties: list             # EcrituresPartie, dans l'ordre canonique
    debut: np.ndarray
    typ: np.ndarray
    attrs: dict               # ATTRIBUTS -> tableau à plat
    rang: np.ndarray
    outil: np.ndarray         # code d'outil (index dans `outils`)
    outils: tuple
    n_lectures: np.ndarray
    n_preparations: np.ndarray
    n_doutes: np.ndarray
    n_actions: np.ndarray
    parties_par_tache: dict = field(default_factory=dict)

    @property
    def n_parties(self) -> int:
        return len(self.parties)

    @property
    def longueurs(self) -> np.ndarray:
        return np.diff(self.debut)


def _cle_canonique(e) -> tuple:
    p = e.partie
    return (p.tache, p.passage, p.id)


def jeu_configuration(preparees: dict, entrees, environnement: str, modele: str, taches, jeu: str) -> \
        JeuConfiguration:
    """G(c, S) (5.5, point 1) : parties du modèle dans l'environnement, sur les tâches données, hors tâches retirées et
    parties en échec technique."""
    taches = {str(t) for t in taches}
    gardees = sorted(t for t in taches if (environnement, t) not in entrees.taches_retirees)
    parties = sorted((preparees[p.id] for p in entrees.parties
                      if p.environnement == environnement and p.modele == modele and p.tache in taches
                      and p.statut_ok and not entrees.retiree(p)), key=_cle_canonique)
    strates: dict = {}
    for t in gardees:
        strates.setdefault(strate_de(environnement, t), []).append(t)
    outils = tuple(sorted({o for e in parties for o in e.outils}))
    code_outil = {o: i for i, o in enumerate(outils)}
    longueurs = np.array([e.n_ecritures for e in parties], dtype=np.int64)
    debut = np.concatenate([[0], np.cumsum(longueurs)]).astype(np.int64)

    def cat(nom, dtype):
        return np.concatenate([getattr(e, nom) for e in parties]).astype(dtype) if parties else np.zeros(0, dtype)

    par_tache: dict = {}
    for i, e in enumerate(parties):
        par_tache.setdefault(e.partie.tache, []).append(i)
    return JeuConfiguration(
        environnement=environnement, modele=modele, jeu=jeu, taches=tuple(gardees),
        strates={s: tuple(v) for s, v in sorted(strates.items())}, parties=parties, debut=debut,
        typ=cat("typ", np.int8), attrs={a: cat(a, bool) for a in ATTRIBUTS}, rang=cat("rang", np.int32),
        outil=np.array([code_outil[o] for e in parties for o in e.outils], dtype=np.int32),
        outils=outils, n_lectures=np.array([e.n_lectures for e in parties], dtype=np.int64),
        n_preparations=np.array([e.n_preparations for e in parties], dtype=np.int64),
        n_doutes=np.array([e.n_doutes for e in parties], dtype=np.int64),
        n_actions=np.array([e.n_actions for e in parties], dtype=np.int64),
        parties_par_tache={t: tuple(v) for t, v in par_tache.items()})


# --------------------------------------------------------------------------
# La suite (temps d'abord, comme regle_e1.FluxE1) : colonnes = répétitions (ou ordres d'une répétition bootstrap)
# --------------------------------------------------------------------------
@dataclass
class Suite:
    T: int
    R: int
    typ: np.ndarray        # (T, R) int8, VIDE en remplissage
    plaf: np.ndarray       # (T, R) bool, et de même pour les attributs de 5.4
    ver: np.ndarray
    reu: np.ndarray
    errp: np.ndarray
    errd: np.ndarray
    den: np.ndarray
    apart: np.ndarray
    partie: np.ndarray     # (T, R) int32 : index de la partie dans G(c, S) (−1 : VIDE) ; cas d'une épreuve
    rang: np.ndarray       # (T, R) int32
    outil: np.ndarray      # (T, R) int32
    u_val: np.ndarray      # (T, R) float64 : le validateur laisse passer l'erreur si u_val < e (1.0 : VIDE)
    n_doutes: np.ndarray   # (R,) : une validation chacun, hors suite
    n_lectures: np.ndarray
    n_preparations: np.ndarray
    n_actions: np.ndarray
    cles_epreuves: tuple   # (R,) entiers de 64 bits : graine « épreuves » de chaque colonne
    meta: dict = field(default_factory=dict)
    # Phase 2 (facultatifs) : grappe (occurrence de tâche) de chaque écriture, −1 pour VIDE (bootstrap-t, 5.13) ;
    # premier pas du second segment d'un scénario (5.10) ; tirages attachés aux écritures (hasard apparié, résistance),
    # pour que le jackknife retire une tâche des mêmes ordres sans changer les autres tirages ; erreurs non vues (5.11).
    grappe: Optional[np.ndarray] = None
    jonction: Optional[np.ndarray] = None
    u_hasard: Optional[np.ndarray] = None
    u_res: Optional[np.ndarray] = None
    rate: Optional[np.ndarray] = None

    @property
    def n_ecritures(self) -> np.ndarray:
        """Écritures de la suite (actions hors lectures, préparations et doutes), par colonne."""
        return (self.typ >= 0).sum(axis=0).astype(np.int64)

    @property
    def n_den(self) -> np.ndarray:
        """Écritures au dénominateur (Q4 a), tous niveaux, par colonne : le dénominateur des « 100 écritures »."""
        return self.den.sum(axis=0).astype(np.int64)

    def n_den_niveau(self) -> np.ndarray:
        """(R, 3) écritures au dénominateur de chaque niveau d'enjeu."""
        niv = TY.ENJEU[np.where(self.typ >= 0, self.typ, 0)]
        return np.stack([(self.den & (niv == j)).sum(axis=0) for j in range(3)], axis=1).astype(np.int64)

    def graine(self, usage: str, colonne: int) -> np.random.SeedSequence:
        m = self.meta
        return graine(m["G0"], usage, m["environnement"], m["modele"], m.get("scenario", 0), m["couche"],
                      m["repetitions"][colonne], m["jeu"], m["ordres"][colonne])


def ordre_unites(jeu: JeuConfiguration, G0: int, couche: str = "R0", repetition: int = 0, ordre: int = 0,
                 scenario: int = 0) -> list:
    """Liste des unités (partie, copie) d'une répétition, dans l'ordre de rejeu (reconstitution de l'ordre figé).

    Couche R0 : toutes les parties de G(c, S), copie 0. Couche bootstrap : tirage avec remise de autant de tâches que
    S en compte dans chaque strate (usage « rééchantillonnage », ordre 0), chaque tâche tirée apportant toutes ses
    parties, la copie étant le rang du tirage dans la strate."""
    env, mod, nom_jeu = jeu.environnement, jeu.modele, jeu.jeu
    if couche == "R0":
        unites = [(i, 0) for i in range(jeu.n_parties)]
    elif couche == "bootstrap":
        rng_b = np.random.default_rng(graine(G0, "reechantillonnage", env, mod, scenario, couche, repetition,
                                             nom_jeu, 0))
        unites = []
        for s, taches in jeu.strates.items():  # strates triées
            tirees = rng_b.integers(0, len(taches), size=len(taches))
            for copie, j in enumerate(tirees.tolist()):
                unites += [(i, copie) for i in jeu.parties_par_tache.get(taches[j], ())]
    else:
        raise ValueError(couche)
    rng_o = np.random.default_rng(graine(G0, "ordre", env, mod, scenario, couche, repetition, nom_jeu, ordre))
    perm = rng_o.permutation(len(unites))
    return [unites[i] for i in perm.tolist()]


def _positions(jeu: JeuConfiguration, sequence: np.ndarray) -> np.ndarray:
    """Positions à plat des écritures des parties `sequence`, mises bout à bout (rang conservé)."""
    if sequence.size == 0:
        return np.zeros(0, dtype=np.int64)
    L = jeu.longueurs[sequence]
    tot = int(L.sum())
    depart = jeu.debut[sequence]
    decal = np.concatenate([[0], np.cumsum(L)[:-1]])
    return np.repeat(depart - decal, L) + np.arange(tot, dtype=np.int64)


def assembler(jeu: JeuConfiguration, colonnes: list, G0: int, couche: str, repetitions: list, ordres: list,
              scenario: int = 0) -> Suite:
    """Assemble les colonnes (listes d'unités) en une Suite, avec les tirages du validateur et les clés des épreuves."""
    env, mod, nom_jeu = jeu.environnement, jeu.modele, jeu.jeu
    R = len(colonnes)
    seqs = [np.array([u[0] for u in col], dtype=np.int64) for col in colonnes]
    pos = [_positions(jeu, s) for s in seqs]
    T = max((p.size for p in pos), default=0)
    typ = np.full((T, R), TY.VIDE, dtype=np.int8)
    att = {a: np.zeros((T, R), dtype=bool) for a in ATTRIBUTS}
    partie = np.full((T, R), -1, dtype=np.int32)
    rang = np.zeros((T, R), dtype=np.int32)
    outil = np.zeros((T, R), dtype=np.int32)
    u_val = np.ones((T, R), dtype=np.float64)
    part_de = np.repeat(np.arange(jeu.n_parties, dtype=np.int32), jeu.longueurs) if jeu.n_parties else \
        np.zeros(0, np.int32)
    cles = []
    for r, (p, s) in enumerate(zip(pos, seqs)):
        n = p.size
        typ[:n, r] = jeu.typ[p]
        for a in ATTRIBUTS:
            att[a][:n, r] = jeu.attrs[a][p]
        partie[:n, r] = part_de[p]
        rang[:n, r] = jeu.rang[p]
        outil[:n, r] = jeu.outil[p]
        u_val[:n, r] = np.random.default_rng(graine(G0, "validateur", env, mod, scenario, couche, repetitions[r],
                                                    nom_jeu, ordres[r])).random(n)
        cles.append(entier_64(graine(G0, "epreuves", env, mod, scenario, couche, repetitions[r], nom_jeu, ordres[r])))
    somme = lambda x: np.array([int(x[s].sum()) for s in seqs], dtype=np.int64)  # noqa: E731
    return Suite(T=T, R=R, typ=typ, partie=partie, rang=rang, outil=outil, u_val=u_val,
                 n_doutes=somme(jeu.n_doutes), n_lectures=somme(jeu.n_lectures),
                 n_preparations=somme(jeu.n_preparations), n_actions=somme(jeu.n_actions), cles_epreuves=tuple(cles),
                 meta=dict(G0=int(G0), environnement=env, modele=mod, jeu=nom_jeu, couche=couche, scenario=scenario,
                           repetitions=list(repetitions), ordres=list(ordres),
                           unites=[list(c) for c in colonnes]),
                 **att)


def suite_r0(jeu: JeuConfiguration, G0: int, R: int, premiere: int = 0, scenario: int = 0) -> Suite:
    """Couche R0 (valeur centrale) : R répétitions sans rééchantillonnage, numérotées à partir de `premiere`."""
    reps = list(range(premiere, premiere + R))
    colonnes = [ordre_unites(jeu, G0, "R0", r, 0, scenario) for r in reps]
    return assembler(jeu, colonnes, G0, "R0", reps, [0] * R, scenario)


def suite_bootstrap(jeu: JeuConfiguration, G0: int, b: int, K: int, scenario: int = 0) -> Suite:
    """Répétition bootstrap b (5.5, point 2.i) : un tirage de tâches par strate, puis K ordres (colonnes)."""
    colonnes = [ordre_unites(jeu, G0, "bootstrap", b, k, scenario) for k in range(K)]
    return assembler(jeu, colonnes, G0, "bootstrap", [b] * K, list(range(K)), scenario)


def suite_depuis_tableaux(typ, plaf=None, ver=None, reu=None, errp=None, errd=None, den=None, apart=None,
                          u_val=None, partie=None, rang=None, outil=None, n_doutes=None, n_lectures=None,
                          n_preparations=None, cles_epreuves=None, meta: Optional[dict] = None) -> Suite:
    """Suite construite directement à partir de tableaux (T, R) : suites synthétiques des tests, suites piège."""
    typ = np.asarray(typ, dtype=np.int8)
    if typ.ndim == 1:
        typ = typ[:, None]
    T, R = typ.shape
    actif = typ >= 0

    def b(x, defaut=False):
        if x is None:
            return np.full((T, R), defaut, dtype=bool) & actif
        x = np.asarray(x, dtype=bool)
        return (x[:, None] if x.ndim == 1 else x) & actif

    def entier(x, defaut):
        if x is None:
            return np.full((T, R), defaut, dtype=np.int32)
        x = np.asarray(x, dtype=np.int32)
        return x[:, None] if x.ndim == 1 else x

    ver_ = b(ver, True)
    reu_ = b(reu, True) if reu is not None else (ver_ & ~b(errp))
    errp_ = b(errp)
    uv = np.ones((T, R)) if u_val is None else np.asarray(u_val, dtype=float).reshape(T, R)
    zr = np.zeros(R, dtype=np.int64)

    def par_col(x):
        return zr.copy() if x is None else np.asarray(x, dtype=np.int64).reshape(R)

    n_ecr = actif.sum(axis=0).astype(np.int64)
    nd, nl, npr = par_col(n_doutes), par_col(n_lectures), par_col(n_preparations)
    return Suite(T=T, R=R, typ=typ, plaf=b(plaf), ver=ver_, reu=reu_ & ver_, errp=errp_,
                 errd=b(errd) if errd is not None else errp_.copy(), den=b(den) if den is not None else (reu_ | errp_),
                 apart=b(apart), partie=entier(partie, 0), rang=entier(rang, 0), outil=entier(outil, 0),
                 u_val=np.where(actif, uv, 1.0), n_doutes=nd, n_lectures=nl, n_preparations=npr,
                 n_actions=n_ecr + nd + nl + npr,
                 cles_epreuves=tuple(cles_epreuves) if cles_epreuves is not None else tuple(range(R)),
                 meta=dict(meta or {}))
