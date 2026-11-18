"""Les règles rejouées (PLAN_EXPERIENCE.md, 5.6) et leurs références par type.

- B-tout (principal) : N = N_tout(environnement, enjeu du type) ; B-régulier : N = N_rég (config figée, point 9).
- A½ et A¼ : le Wald de la v2 (amendement A1), pm3 = barre, pb3 = barre ÷ 2 ou ÷ 4.
- Sous le palier 3, le palier 2 des types réversibles suit le score de Wald de la v2, réglages de départ :
  (pb, pm) = (0,10 ; 0,30) à enjeu faible et (0,05 ; 0,20) à enjeu moyen, α = β = 5 % (`config.REGLAGES_DEPART`,
  `config.BETA`, `config_e1.ALPHA_A`).

Les références par type sont celles d'E1, telles quelles : `regle_e1.RegleUnTypeB` (B) et `regle.RegleUnTypeV2` (A),
construites ici pour la table de types du rejeu (`types_regle`), puisque `depuis_regle` et `depuis_params` lisent la
table d'E1 (`config.ENJEU_HAUT`). `rejouer_reference` est adaptée de `regle_e1.rejouer_reference_e1` (épreuves lues
dans un journal, plafonnées, VIDE).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

import config as C
import config_e1 as E
import regle as RG
import regle_e1 as RE

from . import epreuves as EP
from . import types_regle as TY

NOMS_REGLES = ("B-tout", "B-régulier", "A½", "A¼")
FAMILLE = {"B-tout": "B", "B-régulier": "B", "A½": "A", "A¼": "A", "B-tout-lettre": "B"}
# « B-tout-lettre » : B-tout avec les N du point 8 (lettre d'origine, Q8 A), en analyse secondaire (phase 3).
ORDRE_SIMPLICITE = tuple(n for n in E.ORDRE_SIMPLICITE if n in NOMS_REGLES)
GRAND = RE.GRAND  # « N » d'une règle de la famille A : jamais atteint


@dataclass
class RegleRejeu:
    """Réglages d'une règle, type par type (tableaux de longueur TY.NT), comme `config_e1.RegleE1`."""
    nom: str
    famille: str               # "A" (Wald, amendement A1) ou "B" (séries)
    params: C.ParamsRegle      # palier 2 (réglages de départ) ; palier 3 pour A
    N: np.ndarray              # B : longueur par type (0 pour LEC) ; A : zéros
    enjeu_haut: np.ndarray = field(default_factory=lambda: TY.ENJEU_HAUT.copy())
    epreuves: bool = True

    @property
    def N_allonge(self) -> np.ndarray:
        return np.array([E.n_allonge(int(n)) for n in self.N], dtype=np.int64)


def _params(nom, pb2, pm2, pb3, pm3, a_palier2, alpha=E.ALPHA_A) -> C.ParamsRegle:
    return C.ParamsRegle(nom=nom, reglage="rejeu", alpha=alpha, pb2=np.asarray(pb2, float), pm2=np.asarray(pm2, float),
                         pb3=np.asarray(pb3, float), pm3=np.asarray(pm3, float),
                         a_palier2=np.asarray(a_palier2, bool), version="v2")


def regle(nom: str, environnement: str, config) -> RegleRejeu:
    """Une des quatre règles, réglée pour un environnement (barres et N de la configuration figée)."""
    famille = FAMILLE[nom]
    pb2, pm2 = np.ones(TY.NT), np.ones(TY.NT)
    pb3, pm3 = np.full(TY.NT, 0.01), np.full(TY.NT, 0.05)  # LEC : valeurs neutres, jamais utilisées
    N = np.zeros(TY.NT, dtype=np.int64)
    for k in TY.TYPES_SUITE:
        niv = int(TY.ENJEU[k])
        cle = (environnement, TY.NIVEAUX[niv])
        if TY.A_PALIER2[k]:
            pb2[k], pm2[k] = C.REGLAGES_DEPART[(niv, 2)]
        pb3[k], pm3[k] = C.REGLAGES_DEPART[(niv, 3)]  # inutilisés par la famille B (comme regle_e1.regle_e1)
        if nom in ("A½", "A¼"):
            b = float(config.barres[cle])
            pm3[k], pb3[k] = b, b / (2 if nom == "A½" else 4)
        elif nom == "B-tout":
            N[k] = config.n_tout[cle]
        elif nom == "B-régulier":
            N[k] = config.n_regulier[cle]
        elif nom == "B-tout-lettre":
            N[k] = config.n_tout_lettre[cle]
        else:
            raise ValueError(nom)
    return RegleRejeu(nom, famille, _params(nom, pb2, pm2, pb3, pm3, TY.A_PALIER2), N)


def regles(environnement: str, config, noms=NOMS_REGLES) -> list:
    return [regle(n, environnement, config) for n in noms]


def depuis_regle_e1(r: E.RegleE1) -> RegleRejeu:
    """La même règle qu'une règle d'E1 (types communs LEC … ARG ; GAR et ILL neutres) : test de non-régression."""
    def etendre(x, neutre, dtype=float):
        out = np.full(TY.NT, neutre, dtype=dtype)
        out[:7] = np.asarray(x)[:7]
        return out
    p = r.params
    params = _params(r.nom, etendre(p.pb2, 1.0), etendre(p.pm2, 1.0), etendre(p.pb3, 0.01), etendre(p.pm3, 0.05),
                     etendre(p.a_palier2, False, bool), alpha=p.alpha)
    enjeu_haut = TY.ENJEU_HAUT.copy()
    enjeu_haut[:7] = C.ENJEU_HAUT[:7]
    return RegleRejeu(r.nom, r.famille, params, etendre(r.N, 0, np.int64), enjeu_haut, bool(p.epreuves))


def variante(r: RegleRejeu, nom: str, N=None, params=None) -> RegleRejeu:
    """Copie d'une règle avec d'autres N ou réglages (règles « petites » des tests, comme regles_test d'E1)."""
    return RegleRejeu(nom, r.famille, r.params if params is None else params,
                      r.N.copy() if N is None else np.asarray(N, dtype=np.int64), r.enjeu_haut.copy(), r.epreuves)


# --------------------------------------------------------------------------
# Références par type (telles quelles) et rejeu écriture par écriture
# --------------------------------------------------------------------------
def reference_un_type(r: RegleRejeu, k: int):
    p = r.params
    if r.famille == "B":
        return RE.RegleUnTypeB(r.N[k], p.a2[k], p.b2[k], p.lnB, p.a_palier2[k], r.enjeu_haut[k], r.epreuves)
    return RG.RegleUnTypeV2(p.a2[k], p.b2[k], p.a3[k], p.b3[k], p.lnB, p.a_palier2[k], r.enjeu_haut[k], r.epreuves)


def rejouer_reference(suite, r: RegleRejeu, colonne: int, issues: dict) -> np.ndarray:
    """Paliers d'une colonne de la suite, rejoués avec les références par type (5.16, point 2).

    issues : {(t, type): statut} des épreuves passées par le moteur sur cette ligne (journal). Lecture des preuves de
    5.6 : réussite si l'écriture est vérifiable, juste et non plafonnée (Q4 b) ; erreur si `erreur_preuve`, plafonnée
    comprise ; neutre sinon. Une écriture plafonnée est au palier 1, ne déclenche pas d'épreuve et ne fait pas avancer
    l'attente (5.8). VIDE : palier 0, rien ne change."""
    regs = {k: reference_un_type(r, k) for k in TY.TYPES_SUITE}
    T = suite.T
    out = np.zeros(T, dtype=np.int8)
    for t in range(T):
        k = int(suite.typ[t, colonne])
        if k < 0:
            continue
        rg = regs[k]
        if suite.plaf[t, colonne]:
            out[t] = 1
        else:
            if rg.epreuve_due():
                statut = issues[(t, k)]
                if statut == EP.REUSSIE:
                    rg.resultat_epreuve(True)
                elif statut == EP.RATEE:
                    rg.resultat_epreuve(False)
            out[t] = rg.palier
        if suite.ver[t, colonne] and suite.reu[t, colonne] and not suite.plaf[t, colonne]:
            rg.succes()
        elif suite.errp[t, colonne]:
            rg.erreur()
        else:
            rg.neutre()
    return out
