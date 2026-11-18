"""Contrôle 3, test manquant de 5.16, point 3 : la suite piège « rafale » avec les N réels, dans le moteur vectorisé.

Les tests du moteur couvrent « N réussites puis une erreur » dans le moteur et dans les références par type, mais la
« rafale » seulement dans les références, et seulement pour N ≤ 170 (`test_rejeu_moteur.py`, point 3). Ici : réussites
vérifiées jusqu'à l'autonomie, puis des erreurs, chacune constatée avec la probabilité d = 0,95 (une erreur non
constatée est neutre pour la règle et reste un dégât), jusqu'au retrait ; épreuves toujours réussies (comme
`executer_e1.suite_piege`). Pour tous les environnements et les trois niveaux, avec le N de B-tout de la configuration
figée :
- le moteur vectorisé donne, écriture par écriture, le même palier que les références par type (5.16, point 2) ;
- chaque erreur plantée est exécutée au palier 3, chaque réussite en dessous ; dégâts en plus = erreurs plantées ;
- dégâts en plus par écriture du type ≈ 0,95 ÷ (d × N_e + 1) (borne de la rafale, `executer_e1.lignes_bornes_b`),
  N_e étant N, ou ⌈1,25 × N⌉ après une erreur à enjeu moyen ou fort.
"""
import numpy as np
import pytest

import config_e1 as E
from rejeu import config_rejeu as CR
from rejeu import epreuves as EP
from rejeu import essais as ES
from rejeu import moteur as MO
from rejeu import regles as RG
from rejeu import suites as SU
from rejeu import types_regle as TY

D = float(CR.D_CONSTAT)
CYCLES = {"faible": 300, "moyen": 60, "fort": 5}
TOLERANCE = {"faible": 0.06, "moyen": 0.12}   # environ 4 écarts types du nombre moyen d'erreurs par cycle
CAS = [(env, k) for env in CR.ENVIRONNEMENTS for k in (TY.ECR, TY.MSG, TY.DUR, TY.ARG)]


def suite_rafale(N: int, Ne: int, k: int, cycles: int, rng) -> tuple:
    reu, errp, errd = [], [], []
    for c in range(cycles):
        L = N if c == 0 else Ne
        reu += [True] * L
        errp += [False] * L
        errd += [False] * L
        while True:
            vue = bool(rng.random() < D)
            reu.append(False)
            errp.append(vue)
            errd.append(True)
            if vue:
                break
    typ = np.full(len(reu), k)
    suite = SU.suite_depuis_tableaux(typ, reu=reu, errp=errp, errd=errd, den=np.ones(len(reu), bool))
    return suite, np.array(reu), np.array(errd)


@pytest.mark.parametrize("env,k", CAS)
def test_rafale_avec_les_N_reels_dans_le_moteur(env, k):
    cfg = ES.config()
    niv = TY.niveau(k)
    r = RG.regle("B-tout", env, cfg)
    N = int(r.N[k])
    assert N == cfg.n_tout[(env, niv)]
    Ne = E.n_allonge(N) if TY.ENJEU_HAUT[k] else N
    cycles = CYCLES[niv]
    suite, reu, err = suite_rafale(N, Ne, k, cycles, np.random.default_rng([2026, CR.ENVIRONNEMENTS.index(env), k]))
    m = MO.simuler(suite, [r], EP.FournisseurConstant(EP.REUSSIE), valeurs_e=(0.05,), journal=True, garder_P=True)
    P = m.P[:, 0]
    # équivalence avec les références par type (épreuves du journal)
    np.testing.assert_array_equal(RG.rejouer_reference(suite, r, 0, m.issues_ligne(0)), P)
    assert (P[err] == 3).all() and (P[reu] < 3).all()
    assert m.cpt.exc[0, 0, TY.ENJEU[k]] == err.sum()            # u_val = 1 : toutes les erreurs au palier 3
    assert m.n_prom3[0, k] == cycles and m.n_retraits3[0, k] == cycles
    taux = 0.95 * err.sum() / len(err)
    attendu = 0.95 / (D * Ne + 1)
    if niv in TOLERANCE:
        assert taux == pytest.approx(attendu, rel=TOLERANCE[niv]), (env, TY.SIGLES[k], taux, attendu)
    # la rafale dépasse la borne de B à constat immédiat, 0,95 ÷ (N + 1), d'au plus le facteur 1 ÷ d environ
    assert taux <= 0.95 / (N + 1) / D * (1 + 3 * TOLERANCE.get(niv, 0.5))
