"""Rejeu, phase 2 : méthodes d'intervalle candidates, règle de choix et simulation de couverture
(PLAN_EXPERIENCE.md, 5.13 ; 5.16, point 5). Petites tailles : la simulation complète est un script à part
(`python -m rejeu.couverture --lancer`).
"""
import math

import numpy as np
import pytest
from scipy.stats import t as student

from rejeu import couverture as CO
from rejeu import intervalles as IC


def test_methode_i_percentile_reuni_avec_normal():
    boot = np.array([1.0, 2.0, 3.0, 4.0, 10.0])
    lp, hp = IC.ic_percentile(boot)
    ln, hn = IC.ic_normal(3.0, boot)
    lo, hi = IC.ic_bootstrap_reuni(3.0, boot)
    assert lo == min(lp, ln) and hi == max(hp, hn)
    assert ln == pytest.approx(3.0 - IC.Z95 * boot.std(ddof=1))
    # plusieurs quantités à la fois (dernier axe : répétitions)
    lo2, hi2 = IC.ic_bootstrap_reuni(np.array([3.0, 3.0]), np.stack([boot, boot]))
    assert (lo2 == lo).all() and (hi2 == hi).all()


def test_jackknife_t_d_une_moyenne_redonne_l_intervalle_de_student():
    rng = np.random.default_rng(1)
    x = rng.normal(size=25)
    jack = (x.sum() - x) / (x.size - 1)          # moyenne sans la tâche g
    lo, hi = IC.ic_jackknife_t(x.mean(), jack)
    demi = student.ppf(0.975, x.size - 1) * x.std(ddof=1) / math.sqrt(x.size)
    assert lo == pytest.approx(x.mean() - demi) and hi == pytest.approx(x.mean() + demi)
    # strates : une strate d'une seule tâche n'apporte rien
    v = IC.variance_jackknife(np.array([1.0, 2.0, 3.0, 9.0]), strates=[0, 0, 0, 1])
    assert v == pytest.approx(2 / 3 * 2.0)


def test_se_rapport_lineaire_et_moyenne():
    rng = np.random.default_rng(2)
    a = rng.random(30)
    se = IC.se_rapport(a, np.ones(30))           # rapport à dénominateurs égaux : la moyenne
    assert se == pytest.approx(a.std(ddof=1) / math.sqrt(30))
    assert IC.se_rapport(np.zeros(5), np.ones(5)) == 0.0


def test_bootstrap_t_cas_limites():
    boot = np.array([1.0, 1.1, 0.9, 1.0])
    lo, hi = IC.ic_bootstrap_t(1.0, 0.0, boot, np.full(4, 0.1))
    assert lo == hi == 1.0                               # se nul : intervalle réduit au centre
    t = IC.studentiser(np.array([0.0, 1.0, 2.0]), 1.0, np.array([0.0, 0.0, 0.5]))
    assert t[0] == -np.inf and t[1] == 0.0 and t[2] == 2.0
    # beaucoup de répétitions sans erreur (se* nul, q* < q) : borne haute infinie
    boot = np.array([0.0] * 10 + [2.0] * 10)
    lo, hi = IC.ic_bootstrap_t(1.0, 0.5, boot, np.array([0.0] * 10 + [0.5] * 10))
    assert hi == np.inf and np.isfinite(lo)
    rng = np.random.default_rng(3)
    b = rng.normal(5.0, 1.0, size=4000)
    lo, hi = IC.ic_bootstrap_t(5.0, 1.0, b, np.ones(4000))
    assert lo == pytest.approx(5.0 - (np.quantile(b, 0.975) - 5.0)) and hi == pytest.approx(5.0 + (5.0 - np.quantile(b, 0.025)))


def test_verdict_d_une_cellule():
    assert IC.verdict(0.0, 0.4, 0.5) == IC.PASSE
    assert IC.verdict(0.6, 0.9, 0.5) == IC.ECHOUE
    assert IC.verdict(0.3, 0.6, 0.5) == IC.INDECISE
    assert IC.verdict(0.0, 0.5, 0.5) == IC.PASSE          # borne haute au plus le budget
    assert IC.verdict(0.0, float("inf"), 0.5) == IC.INDECISE
    assert IC.verdict(float("nan"), 0.1, 0.5) == IC.INDECISE


def test_regle_de_choix_et_repli():
    rhos, gs = (0.0, 0.9), (20, 90)
    couv = {(m, r, g): 0.95 for m in IC.METHODES for r in rhos for g in gs}
    assert IC.choisir_methode(couv, rhos, gs)["methode"] == "i"
    couv[("i", 0.9, 20)] = 0.92
    c = IC.choisir_methode(couv, rhos, gs)
    assert c["methode"] == "ii" and not c["repli"]
    for m in IC.METHODES:
        couv[(m, 0.9, 20)] = {"i": 0.80, "ii": 0.86, "iii": 0.84}[m]
    c = IC.choisir_methode(couv, rhos, gs)
    assert c["methode"] == "ii" and c["repli"] and c["zone_echec"] == [20] and c["G_sur"] == 90
    assert IC.fragile_par_grappes(20, c) and IC.fragile_par_grappes(40, c) and not IC.fragile_par_grappes(276, c)
    couv[("ii", 0.0, 90)] = 0.90                           # échoue aussi au plus grand G : tout est fragile
    c = IC.choisir_methode(couv, rhos, gs)
    assert c["methode"] == "ii" and c["G_sur"] == math.inf and IC.fragile_par_grappes(276, c)
    assert IC.methode_seconde("i") == "iii" and IC.methode_seconde("iii") == "percentile"


def test_parametres_figes_de_la_simulation():
    assert CO.RHOS == (0.0, 0.1, 0.3, 0.5, 0.7, 0.9) and CO.GS == (20, 40, 90)
    assert CO.N_JEUX >= 1000 and CO.B == 2000 and CO.K == 10
    assert CO.tailles(20).tolist() == list(CO.TAILLES) * 2
    assert CO.valeur_vraie(0.05) == pytest.approx(4.75)


def test_simulation_de_couverture_petite_et_deterministe():
    a = CO.simuler_case(0.2, 0.0, 40, n_jeux=60, graine=7, B_=200, K_=2, paquet=20)
    b = CO.simuler_case(0.2, 0.0, 40, n_jeux=60, graine=7, B_=200, K_=2, paquet=20)
    assert a == b
    assert {l["methode"] for l in a} == {"i", "ii", "iii", "percentile"}
    for l in a:
        assert 0.7 <= l["couverture"] <= 1.0                 # ρ = 0, taux 0,2 : la couverture est près du nominal
        assert l["part_trop_bas"] + l["part_trop_haut"] + l["couverture"] == pytest.approx(1.0)
        assert abs(l["centre_moyen"] - l["valeur_vraie"]) < 1.0   # valeur centrale sans biais
    # ρ = 0,9 et taux faible : des jeux sans erreur, intervalles réduits à zéro, couverture dégradée
    c = CO.simuler_case(0.05, 0.9, 20, n_jeux=60, graine=8, B_=100, K_=2, paquet=20)
    assert c[0]["part_jeux_sans_erreur"] > 0.1


def test_choix_lu_dans_les_resultats_de_la_simulation():
    lignes = [dict(taux=CO.TAUX_CRITERE, rho=r, G=g, methode=m, couverture=0.96)
              for r in CO.RHOS for g in CO.GS for m in IC.METHODES]
    assert CO.choix_depuis_lignes(lignes)["methode"] == "i"
