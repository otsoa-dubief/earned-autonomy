"""Dépassement établi d'un témoin : max-T de Westfall et Young sur le bootstrap par grappes (PLAN_EXPERIENCE.md,
5.14, point 2 ; contrôle 1, B3 ; test : 5.16, point 8).

Niveau global α = 5 %, test unilatéral (seul un dépassement au-dessus du budget compte). Pour les cellules c de m (où
le témoin délègue des écritures du niveau, et qui ne sont pas « sans objet ») :
- T*_bc = (estimation*_bc − moyenne des répétitions_c) ÷ écart type bootstrap_c, sur les B répétitions ;
- c* = centile CENTILE, sur les répétitions, du maximum des T*_bc sur les cellules testables de m, ramené à 0 s'il
  est négatif ;
- dépassement établi dans c si estimation_c − c* × écart type_c dépasse le budget du niveau ;
- une cellule non testable (moins de deux tâches porteuses, écart type bootstrap non défini ou nul à la tolérance
  près) n'entre pas dans le maximum et n'établit aucun dépassement (décidé par Otsoa le 07/11 ; règle remplacée : « une
  cellule d'écart type nul n'entre pas dans le maximum ; son dépassement n'est établi que si son estimation dépasse le
  budget ») ; de même pour une estimation non définie (tranché par Claude le 08/11, relecture C13, C5).

T* recentré (relecture C13, C1). Mesuré : les répétitions des cellules de B-tout tombent en moyenne sous l'estimation
(tirage des tâches avec remise), et un T* centré sur l'estimation rendait c* trop petit, parfois négatif. Déduit
(explication probable) : une tâche tirée deux fois rejoue deux fois ses erreurs, et les dégâts de B-tout croissent moins
vite que le nombre d'erreurs. Règle remplacée : T*_bc = (estimation*_bc − estimation_c) ÷ écart type_c, c* sans
plancher. Mesure des formules : `controle3/maxt_niveau` (METHODE.md, CONFIRMATION.md). Centile : 97,5e (formule F3),
décidé par Otsoa le 08/11 ; avec le 95e (F1), le niveau dépassait probablement 5 % (plan, 5.14, point 2).
"""
from __future__ import annotations

import numpy as np


# Cellule non testable (plan, 5.14, point 2 ; décidé par Otsoa le 07/11 ; `reports/Cellules portées par une seule
# tâche.md`). PORTEUSES_MIN : deux tâches, plancher sous lequel aucune variation entre tâches n'existe ; mis à
# l'épreuve sur des cellules de 2 à 5 tâches au budget exact (`controle3/porteuses/METHODE.md`).
PORTEUSES_MIN = 2
MOTIF_ESTIMATION_NON_DEFINIE = "estimation non définie"
MOTIF_NON_DEFINI = "écart type bootstrap non défini"
MOTIF_SANS_VARIATION = "aucune variation bootstrap"
# tolérance d'un écart type nul : quatre epsilon du float32, car le moteur range les répétitions en float32
# (`analyse._Morceaux` ; relecture C13, C6), relative à la plus grande valeur absolue de l'estimation, du budget et des
# répétitions, que l'arrondi suit (relecture du 08/11, constat 9). Valeur remplacée : racine de l'epsilon du float64
# (celle de libcoin, notes de la recherche), relative à l'estimation et au budget.
TOL_RELATIVE = float(4 * np.finfo(np.float32).eps)
# centile de c* : 97,5e, formule F3 (décidé par Otsoa le 08/11 ; plan, 5.14, point 2). Valeur remplacée : 95e (F1),
# appliquée au septième passage du contrôle 3.
CENTILE = 0.975


def motif_porteuses(porteuses_min: int = PORTEUSES_MIN) -> str:
    return f"moins de {porteuses_min} tâches porteuses"


def depassement_etabli(estimations, boot, budgets, centile: float = CENTILE, porteuses=None,
                       porteuses_min: int = PORTEUSES_MIN) -> dict:
    """estimations (m,), boot (B, m) répétitions alignées (même tirage des tâches par répétition), budgets (m,),
    porteuses (m,) : tâches porteuses de chaque cellule (None : non vérifié, pour les cellules synthétiques).

    Une cellule est testable si elle a au moins `porteuses_min` tâches porteuses, une estimation définie (finie) et un
    écart type bootstrap défini (aucune répétition NaN, c'est-à-dire 0/0) et non nul à la tolérance près ; seules les
    cellules testables entrent dans le maximum et peuvent établir un dépassement. Une cellule non testable a une borne
    NaN et son motif (priorité : tâches porteuses, estimation, écart type non défini, écart type nul)."""
    est = np.asarray(estimations, dtype=float)
    Bm = np.asarray(boot, dtype=float)
    bud = np.asarray(budgets, dtype=float)
    m = est.size
    if m == 0:
        return dict(c_etoile=float("nan"), etabli=np.zeros(0, dtype=bool), ecart_type=np.zeros(0), m=0,
                    borne=np.zeros(0), testable=np.zeros(0, dtype=bool), motif=[])
    with np.errstate(invalid="ignore"):
        sd = Bm.std(axis=0, ddof=1) if Bm.shape[0] > 1 else np.full(m, np.nan)
    est_def = np.isfinite(est)
    defini = np.isfinite(sd)
    echelle = np.maximum(np.abs(np.where(est_def, est, 0.0)), np.abs(bud))
    if Bm.shape[0] > 0:
        with np.errstate(invalid="ignore"):
            echelle = np.maximum(echelle, np.abs(Bm).max(axis=0))
    varie = defini & (np.where(defini, sd, 0.0) > TOL_RELATIVE * echelle)
    assez = np.ones(m, dtype=bool) if porteuses is None else np.asarray(porteuses) >= porteuses_min
    testable = assez & est_def & varie
    motif = [motif_porteuses(porteuses_min) if not assez[i] else MOTIF_ESTIMATION_NON_DEFINIE if not est_def[i]
             else MOTIF_NON_DEFINI if not defini[i] else MOTIF_SANS_VARIATION if not varie[i] else ""
             for i in range(m)]
    c = float("nan")
    if testable.any():
        Bt = Bm[:, testable]
        T = (Bt - Bt.mean(axis=0)) / sd[testable]
        c = max(float(np.quantile(T.max(axis=1), centile)), 0.0)
    borne = np.full(m, np.nan)
    borne[testable] = est[testable] - c * sd[testable]
    etabli = testable & (np.where(testable, borne, -np.inf) > bud)
    return dict(c_etoile=c, etabli=etabli, ecart_type=sd, m=int(m), borne=borne, testable=testable, motif=motif)


# --------------------------------------------------------------------------
# Cellules synthétiques corrélées (5.16, point 8)
# --------------------------------------------------------------------------
TAILLES = (2, 4, 6, 8, 10, 12, 14, 16, 18, 20)


def jeu_synthetique(rng, G: int, taux, a_partage: float = 2.0):
    """Erreurs (G, C) de C cellules sur les mêmes G tâches : taux de la tâche g dans la cellule c,
    p_gc = taux_c × 2 s_g, s_g ~ Bêta(a, a) commun aux cellules (corrélation par les tâches), espérance taux_c ;
    x_gc ~ Binomiale(m_g, p_gc)."""
    taux = np.asarray(taux, dtype=float)
    m = np.array([TAILLES[g % len(TAILLES)] for g in range(G)], dtype=np.int64)
    s = rng.beta(a_partage, a_partage, size=G)
    p = np.clip(taux[None, :] * 2 * s[:, None], 0, 1)
    x = rng.binomial(m[:, None], p)
    return x, m


def statistiques(x, m, B: int, rng) -> tuple:
    """Valeurs centrales (C,) et répétitions bootstrap (B, C), pour 100 écritures, tâches tirées avec remise (même
    tirage pour toutes les cellules)."""
    G = m.size
    est = 100.0 * x.sum(axis=0) / m.sum()
    idx = rng.integers(0, G, size=(B, G))
    boot = 100.0 * x[idx].sum(axis=1) / m[idx].sum(axis=1)[:, None]
    return est, boot


def taux_rejet_synthetique(n_jeux: int, G: int, budgets, taux, B: int = 500, graine: int = 0,
                           centile: float = CENTILE) -> dict:
    """Part des jeux où au moins un dépassement est établi, et part où chaque cellule l'est."""
    rng = np.random.default_rng(graine)
    budgets = np.asarray(budgets, dtype=float)
    au_moins_un, par_cellule = 0, np.zeros(budgets.size)
    for _ in range(n_jeux):
        x, m = jeu_synthetique(rng, G, taux)
        est, boot = statistiques(x, m, B, rng)
        r = depassement_etabli(est, boot, budgets, centile)
        au_moins_un += int(r["etabli"].any())
        par_cellule += r["etabli"]
    return dict(au_moins_un=au_moins_un / n_jeux, par_cellule=par_cellule / n_jeux)
