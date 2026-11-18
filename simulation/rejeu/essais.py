"""Outils des tests du moteur (PLAN_EXPERIENCE.md, 5.16) : entrées du pilote, suites synthétiques, fournisseur
d'issues aléatoires, règles « petites ». Rien ici ne sert au rejeu final.

Les sorties du pilote (`pilote/etape2/2026-11-05_07-50-58/`) ne portent que sur des tâches de développement : elles
servent aux tests, et leurs chiffres n'ont aucune valeur de preuve (3.1 ; 5.16, point 6).
"""
from __future__ import annotations

import functools
import os

import numpy as np

import config as C

from . import RACINE
from . import config_rejeu as CR
from . import entrees as EN
from . import epreuves as EP
from . import preuves as PR
from . import regles as RG
from . import suites as SU
from . import types_regle as TY

DOSSIER_PILOTE = os.path.join(RACINE, "pilote", "etape2", "2026-11-05_07-50-58")


@functools.lru_cache(maxsize=None)
def entrees_pilote():
    return EN.charger_entrees(DOSSIER_PILOTE)


@functools.lru_cache(maxsize=None)
def preparees_pilote(mode: str = "confirmes"):
    return PR.preparer(entrees_pilote(), mode)


@functools.lru_cache(maxsize=None)
def config():
    return CR.charger_config()


def taches_pilote(environnement: str) -> list:
    return sorted({p.tache for p in entrees_pilote().parties if p.environnement == environnement})


# --------------------------------------------------------------------------
# Règles des tests
# --------------------------------------------------------------------------
def regles_test(environnement: str, cfg=None) -> list:
    """Les quatre règles, plus des variantes rapides qui atteignent le palier 3 sur des suites courtes (comme
    `regles_test` de tests/test_e1.py) : B à N ÷ 40 (au moins 2), et un Wald « souple, α = 20 % »."""
    cfg = cfg or config()
    rs = RG.regles(environnement, cfg)
    petits = [RG.variante(r, r.nom + "-petit", N=np.where(r.N > 0, np.maximum(2, r.N // 40), 0))
              for r in rs if r.famille == "B"]
    s = C.params_regle("souple", 0.20)
    ext = lambda x, neutre: np.concatenate([np.asarray(x[:7], float), [neutre, neutre]])  # noqa: E731
    pb3, pm3 = ext(s.pb3, 0.0), ext(s.pm3, 0.0)
    pb3[TY.GAR], pm3[TY.GAR] = pb3[TY.SOR], pm3[TY.SOR]
    pb3[TY.ILL], pm3[TY.ILL] = pb3[TY.SOR], pm3[TY.SOR]
    params = RG._params("A-rapide", ext(s.pb2, 1.0), ext(s.pm2, 1.0), pb3, pm3, TY.A_PALIER2, alpha=0.20)
    rapide = RG.RegleRejeu("A-rapide", "A", params, np.zeros(TY.NT, dtype=np.int64))
    return rs + petits + [rapide]


# --------------------------------------------------------------------------
# Suites synthétiques
# --------------------------------------------------------------------------
def suite_synthetique(graine, T: int = 300, R: int = 6, types=TY.TYPES_SUITE, p_err: float = 0.12,
                      p_inv: float = 0.05, p_plaf: float = 0.15, p_neutre: float = 0.05, p_refusee: float = 0.2,
                      vide: bool = True, n_parties: int = 20) -> SU.Suite:
    """Suite aléatoire cohérente avec 5.4 : erreurs (dont refusées, sans dégât), neutres, invérifiables, plafonnées
    (sur SOR, ARG et ILL seulement, comme les plafonds de la pièce 3), ILL à part ; colonnes de longueurs variables
    complétées par VIDE si `vide`."""
    rng = np.random.default_rng(graine)
    typ = rng.choice(np.array(types, dtype=np.int8), size=(T, R))
    if vide:
        longueurs = rng.integers(T // 2, T + 1, size=R)
        for r, L in enumerate(longueurs):
            typ[L:, r] = TY.VIDE
    actif = typ >= 0
    ver = rng.random((T, R)) >= p_inv
    errp = ver & (rng.random((T, R)) < p_err)
    neutre = ver & ~errp & (rng.random((T, R)) < p_neutre)
    reu = ver & ~errp & ~neutre
    refusee = errp & (rng.random((T, R)) < p_refusee)
    errd = errp & ~refusee
    plafonnable = np.isin(typ, (TY.SOR, TY.ARG, TY.ILL))
    plaf = plafonnable & (rng.random((T, R)) < p_plaf)
    apart = typ == TY.ILL
    den = (reu | errd | (neutre & (rng.random((T, R)) < 0.5))) & ~apart
    partie = rng.integers(0, n_parties, size=(T, R))
    rang = np.tile(np.arange(T, dtype=np.int32)[:, None], (1, R))
    return SU.suite_depuis_tableaux(typ, plaf=plaf, ver=ver, reu=reu, errp=errp, errd=errd, den=den, apart=apart,
                                    u_val=rng.random((T, R)), partie=partie, rang=rang,
                                    outil=rng.integers(0, 5, size=(T, R)), n_doutes=rng.integers(0, 10, size=R),
                                    n_lectures=rng.integers(0, 50, size=R), cles_epreuves=rng.integers(0, 2 ** 62, R))


class FournisseurAleatoire:
    """Issues aléatoires mais reproductibles, fonction de (ligne, t, type) : épreuves réussies, ratées ou impossibles
    (tests d'équivalence sur suites synthétiques)."""

    def __init__(self, graine: int, p_reussie: float = 0.6, p_impossible: float = 0.1):
        self.graine, self.p_reussie, self.p_impossible = int(graine), p_reussie, p_impossible

    def issue(self, ligne, t, colonne, type_, cas, tentative) -> EP.Issue:
        u = EP.combiner(self.graine, ligne, t, type_) / 2.0 ** 64
        if u < self.p_impossible:
            return EP.Issue(EP.IMPOSSIBLE)
        if u < self.p_impossible + self.p_reussie:
            return EP.Issue(EP.REUSSIE, (0, 1, 2))
        return EP.Issue(EP.RATEE, (0, 1, 2))
