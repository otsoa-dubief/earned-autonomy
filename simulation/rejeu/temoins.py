"""Les règles témoins du rejeu (PLAN_EXPERIENCE.md, 5.7). Elles tournent sur les mêmes suites et avec les mêmes
tirages que les règles. Chaque fonction rend les paliers (T, R) : 1, 2 ou 3, et 0 pour VIDE.

Toutes gardent les lectures au palier 3 (hors suite) et les plafonnées au palier 1, sauf « tout approuver ».

- tout faire valider : palier 1 partout ; référence du dégât en plus (E1 : `paliers_fixes`) ;
- tout approuver : palier 3 partout, plafonnées comprises (E1 : `paliers_fixes`) ;
- liste fixe : LEC et ECR au palier 3, le reste au palier 1 (E1 : `paliers_fixes`, types généralisés) ;
- tri par le risque : types à enjeu faible (LEC, ECR, MSG) au palier 3, le reste au palier 1 (idem) ;
- trois réussites : palier 3 après 3 réussites vérifiées d'affilée, retrait à la première erreur
  (E1 : `paliers_trois_reussites`) ;
- hasard apparié, un par règle : même part des écritures du type aux paliers 2 et 3 que la règle
  (E1 : `paliers_hasard`) ;
- oracle avec palier 2 : « sous la barre » au jeu de calibration, palier 3 ; sinon palier 2 si le type est réversible,
  palier 1 sinon (E1 : `paliers_oracle_p2`, adapté : classes au lieu du taux vrai d'un agent fictif) ;
- oracle rétrospectif : le même, avec les classes mesurées sur la suite de confirmation elle-même (nouveau).
"""
from __future__ import annotations

import numpy as np

from . import classes as CL
from . import types_regle as TY

NOMS_FIXES = ("tout_valider", "tout_approuver", "liste_fixe", "tri_risque")


def _finir(P: np.ndarray, suite, plafonnees_au_1: bool = True) -> np.ndarray:
    actif = suite.typ >= 0
    if plafonnees_au_1:
        P = np.where(suite.plaf, 1, P)
    return np.where(actif, P, 0).astype(np.int8)


def paliers_fixes(nom: str, suite) -> np.ndarray:
    typ = suite.typ
    if nom == "tout_approuver":
        return _finir(np.full(typ.shape, 3, dtype=np.int8), suite, plafonnees_au_1=False)
    if nom == "tout_valider":
        P = np.ones(typ.shape, dtype=np.int8)
    elif nom == "liste_fixe":
        P = np.where(typ == TY.ECR, 3, 1)
    elif nom == "tri_risque":
        faible = (TY.ENJEU == TY.FAIBLE) & TY.MERITE
        P = np.where(faible[np.where(typ >= 0, typ, 0)], 3, 1)
    else:
        raise ValueError(nom)
    return _finir(P, suite)


def paliers_trois_reussites(suite) -> np.ndarray:
    """Palier 3 après 3 réussites vérifiées d'affilée sur le type, quel que soit l'enjeu ; retrait à la première
    erreur. Mêmes preuves que les règles (Q4 b : réussites plafonnées ignorées, erreurs plafonnées comptées)."""
    T, R = suite.T, suite.R
    serie = np.zeros(R * TY.NT, dtype=np.int32)
    pal = np.ones(R * TY.NT, dtype=np.int8)
    base = np.arange(R, dtype=np.int64) * TY.NT
    P = np.zeros((T, R), dtype=np.int8)
    for t in range(T):
        k = suite.typ[t].astype(np.int64)
        actif = k >= 0
        idx = base + np.where(actif, k, 0)
        P[t] = np.where(actif, pal[idx], 0)
        ok = actif & ~suite.plaf[t] & suite.ver[t] & suite.reu[t]
        ko = actif & suite.errp[t]
        io = idx[ok]
        serie[io] += 1
        pal[io[serie[io] >= 3]] = 3
        ik = idx[ko]
        serie[ik] = 0
        pal[ik] = 1
    return _finir(P, suite)


def parts_regle(comptes: np.ndarray) -> tuple:
    """(f3, f23) par type : part des écritures non plafonnées du type exécutées au palier 3, et aux paliers 2 ou 3, sous
    la règle (comptes (lignes, NT, 3), sommés sur les répétitions)."""
    tot = comptes.sum(axis=(0, 2)).astype(np.float64)
    tot[tot == 0] = 1.0
    f3 = comptes[:, :, 2].sum(axis=0) / tot
    f23 = (comptes[:, :, 2] + comptes[:, :, 1]).sum(axis=0) / tot
    return f3, f23


def tirages_hasard(suite) -> np.ndarray:
    """u (T, R) du hasard apparié : graine « hasard apparié » de chaque colonne, les mêmes pour toutes les règles
    (ceux attachés aux écritures, s'ils sont donnés : suites du jackknife, phase 2)."""
    if getattr(suite, "u_hasard", None) is not None:
        return suite.u_hasard
    u = np.ones((suite.T, suite.R))
    for c in range(suite.R):
        u[:, c] = np.random.default_rng(suite.graine("hasard_apparie", c)).random(suite.T)
    return u


def paliers_hasard(suite, f3: np.ndarray, f23: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Hasard apparié : chaque type passe, au hasard, la même part de ses écritures aux paliers 2 et 3 que la règle
    (couche R0 : moyenne des répétitions de la suite, 5.7 ; bootstrap : ses K ordres, 5.5, point 7)."""
    k = np.where(suite.typ >= 0, suite.typ, 0)
    P = np.where(u < f3[k], 3, np.where(u < f23[k], 2, 1))
    return _finir(P, suite)


def paliers_par_type(suite, pal_type: np.ndarray) -> np.ndarray:
    k = np.where(suite.typ >= 0, suite.typ, 0)
    return _finir(pal_type[k], suite)


def paliers_oracle(suite, classes: dict) -> np.ndarray:
    """Oracle avec palier 2 : palier 3 si le type est « sous la barre » ; « indéterminé », « au-dessus » ou sans
    donnée :
    palier 2 s'il est réversible, palier 1 sinon (5.7 ; contrôle 1, B1).

    Ancien oracle (phase 1), sur la classe prouvée : le rejeu final ne l'appelle pas ; son oracle est
    `analyse.palier_par_type`, sur le taux médian (Q14 et N1, 06/11 ; relecture C13, P5). Gardé pour `rejeu.py`,
    que seuls des tests de la phase 1 appellent."""
    pal = np.ones(TY.NT, dtype=np.int8)
    for k in TY.TYPES_SUITE:
        c = classes.get(k, {}).get("classe", CL.SANS_DONNEE)
        pal[k] = 3 if c == CL.SOUS else (2 if TY.A_PALIER2[k] else 1)
    return paliers_par_type(suite, pal)
