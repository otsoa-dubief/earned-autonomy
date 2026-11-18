"""Rejeu, phase 2 : Clopper-Pearson sur la taille effective, ρ̂ et son repli, modèle bêta-binomial
(PLAN_EXPERIENCE.md, 5.12, point 4 ; 5.13 ; contrôle 1, B4 et M8).
"""
import numpy as np
import pytest

from rejeu import classes as CL
from rejeu import config_rejeu as CR
from rejeu import essais as ES
from rejeu import suites as SU
from rejeu import types_regle as TY


def test_rho_anova_cas_connus():
    assert CL.rho_anova([5, 5, 5, 5], [5, 0, 5, 0]) == pytest.approx(1.0)        # erreurs groupées par tâche
    rng = np.random.default_rng(1)
    m = np.full(400, 20)
    x = rng.binomial(m, 0.1)
    assert abs(CL.rho_anova(m, x)) < 0.02                                         # indépendantes : près de 0
    assert CL.rho_anova([5, 5], [0, 0]) is None                                   # aucune erreur : non calculable
    assert CL.rho_anova([5], [2]) is None                                         # une seule tâche
    assert CL.rho_anova([1, 1, 1], [1, 0, 0]) is None                             # tâches d'une écriture
    # loi bêta-binomiale de corrélation 0,3 : estimation proche
    p = rng.beta(0.1 * 0.7 / 0.3, 0.9 * 0.7 / 0.3, size=3000)
    x = rng.binomial(20, p)
    assert CL.rho_anova(np.full(3000, 20), x) == pytest.approx(0.3, abs=0.03)


def test_taille_effective_et_bornes():
    n, mbar, ne = CL.taille_effective([10, 10, 10, 10], 0.0)
    assert (n, mbar, ne) == (40.0, 10.0, 40.0)
    n, mbar, ne = CL.taille_effective([1, 3, 6], 1.0)
    assert ne == pytest.approx(10 ** 2 / (1 + 9 + 36))                            # nombre effectif de tâches
    n, mbar, ne = CL.taille_effective([2, 8], 0.5)
    assert mbar == pytest.approx((4 + 64) / 10) and ne == pytest.approx(10 / (1 + (6.8 - 1) * 0.5))
    c = CL.classer(0, 100, 0.05, n_eff=40.0)
    assert c["hi"] == pytest.approx(1 - 0.05 ** (1 / 40)) and c["x_eff"] == 0     # zéro erreur : 1 − 0,05^(1/n_eff)
    c = CL.classer(10, 100, 0.5, n_eff=20.0)
    assert c["p"] == pytest.approx(0.1) and c["x_eff"] == pytest.approx(2.0)      # taux estimé inchangé
    lo, hi = CL.bornes_cp(2.0, 20.0)
    assert (c["lo"], c["hi"]) == pytest.approx((lo, hi))
    # la taille effective rend la classe plus prudente qu'avec les effectifs bruts
    b = 0.06
    assert CL.classer(0, 60, b)["classe"] == CL.SOUS
    assert CL.classer(0, 60, b, n_eff=20.0)["classe"] == CL.INDETERMINE


def test_volume_de_certification_en_taille_effective():
    b = ES.config().barres[("aviation", "faible")]
    n = CR.certification(b)
    assert CL.classer(0, 10 * n, float(b), n_eff=float(n))["classe"] == CL.SOUS
    assert CL.classer(0, 10 * n, float(b), n_eff=float(n - 1))["classe"] != CL.SOUS


def test_regle_n3_de_rho():
    """Règle de ρ̂ N3 (06/11 ; remplace G1) : valeur commune à toutes les configurations (Fleiss–Cuzick stratifié par
    configuration et type), plancher 0,3, configuration riche ; preuves à 95 % sur la taille effective à ρ = 1."""
    assert CL.rho_avec_repli(0.2, 0.5) == (0.2, CL.SOURCES_RHO[0])          # fonction de la phase 2, inchangée
    e, prep, cfg = ES.entrees_pilote(), ES.preparees_pilote(), ES.config()
    jeux_par_env = {env: {m: SU.jeu_configuration(prep, e, env, m, ES.taches_pilote(env), "developpement")
                          for m in CR.MODELES} for env in ("aviation", "WorkBench")}
    rc = CL.rho_commun(jeux_par_env)
    assert rc == CL.rho_fc_strates(CL.strates_par_type([j for jx in jeux_par_env.values() for j in jx.values()]))
    base = (max(0.3, rc), CL.SOURCES_G1[1]) if rc is not None else (0.3, CL.SOURCES_G1[2])
    cls = CL.classes_tous_environnements(jeux_par_env, cfg)
    for env, jeux in jeux_par_env.items():
        for m, c in cls[env].items():
            x, t = CL.erreurs_et_taches(jeux[m])
            rconf = CL.rho_fc_strates(CL.strates_par_type([jeux[m]])) if (x >= 10 and t >= 5) else None
            attendu = (rconf, CL.SOURCES_G1[0]) if rconf is not None and rconf > base[0] else base
            for k, v in c.items():
                assert v["rho"] == pytest.approx(attendu[0]) and v["source_rho"] == attendu[1]
                assert v["rho"] >= 0.3                                         # plancher
                if v["n"]:
                    ms = [y[0] for y in CL.comptes_par_tache(jeux[m], (k,)).values()]
                    assert v["n_eff"] == pytest.approx(CL.taille_effective(ms, attendu[0])[2])
                    assert v["n_eff_preuve"] == pytest.approx(CL.taille_effective(ms, 1.0)[2])   # ρ = 1 (N3)
                    # Q14 et N1 : taux médian (borne haute à 50 %) au plus la barre ; jugeable : zéro erreur suffirait
                    assert v["estime_sous"] == (CL.mediane_haute(v["x_eff"], v["n_eff"]) <= v["barre"])
                    assert v["jugeable"] == (CL.mediane_haute(0.0, v["n_eff"]) <= v["barre"])
                    # classe : bornes à 95 % sur la taille effective à ρ = 1 ; sous hypothèse : sur ρ̂
                    xp = v["x"] * v["n_eff_preuve"] / v["n"]
                    assert v["hi"] == pytest.approx(CL.bornes_cp(xp, v["n_eff_preuve"])[1])
                    assert v["hi_hyp"] == pytest.approx(CL.bornes_cp(v["x_eff"], v["n_eff"])[1])
    # sans erreur nulle part : le plancher
    sans = {m: SU.jeu_configuration(prep, e, "commerce", m, [], "developpement") for m in CR.MODELES}
    assert set(CL.rho_par_configuration(sans, CL.rho_commun({"commerce": sans})).values()) == {(0.3, CL.SOURCES_G1[2])}


def test_rho_fc_strates_les_deux_faces_de_n3():
    """N3 : l'estimateur standardise strate par strate (pas de gonflement par l'écart des taux entre configurations) et
    lit chaque type dans sa grappe (pas de dilution par les écritures d'autres types de la même tâche)."""
    rng = np.random.default_rng(11)
    # face 1 : erreurs indépendantes à 10 % dans des grappes de 2 à 3 écritures (une configuration qui se trompe
    # beaucoup) ; grandes grappes sans erreur ailleurs. L'analyse de variance réunie lit l'écart comme une corrélation.
    m_a = rng.integers(2, 4, 300).astype(float)
    y_a = rng.binomial(m_a.astype(int), 0.1).astype(float)
    m_b = np.full(40, 100.0)
    y_b = np.zeros(40)
    assert CL.rho_anova(np.r_[m_a, m_b], np.r_[y_a, y_b]) > 0.2
    assert CL.rho_fc_strates([(m_a, y_a), (m_b, y_b)]) < 0.05
    # face 2 : erreurs parfaitement groupées d'un type (toutes les écritures de 4 tâches sur 20) ; l'autre type de la
    # même tâche ne se trompe jamais. Réunir les deux types dans la grappe dilue la corrélation.
    m1 = np.full(20, 5.0)
    y1 = np.r_[np.full(4, 5.0), np.zeros(16)]
    m2 = np.full(20, 5.0)
    y2 = np.zeros(20)
    assert CL.rho_fc_strates([(m1, y1), (m2, y2)]) == pytest.approx(1.0)
    assert CL.rho_anova(m1 + m2, y1 + y2) < 0.5
    # une erreur dans une grappe d'une écriture ne dit rien de ρ (résidu de G1) ; aucune strate informative : None
    assert CL.rho_fc_strates([(np.array([1.0, 5.0, 5.0]), np.array([1.0, 0.0, 0.0]))]) is None
    assert CL.rho_fc_strates([(np.full(10, 1.0), np.ones(10))]) is None
    # ρ = 1 : taille effective = nombre effectif de tâches, (Σ m)² ÷ Σ m²
    assert CL.taille_effective([5, 5, 10], CL.RHO_PREUVE)[2] == pytest.approx(400 / 150)


def test_beta_binomiale_descriptive():
    rng = np.random.default_rng(4)
    mu, rho = 0.15, 0.2
    s = (1 - rho) / rho
    p = rng.beta(mu * s, (1 - mu) * s, size=2000)
    m = rng.integers(5, 30, size=2000)
    x = rng.binomial(m, p)
    r = CL.beta_binomiale(m, x)
    assert r["mu"] == pytest.approx(mu, abs=0.01) and r["rho"] == pytest.approx(rho, abs=0.03)
    r0 = CL.beta_binomiale([5, 5], [0, 0])
    assert r0["mu"] == 0.0 and r0["rho"] != r0["rho"]


def test_n1_taux_median_jugeable_et_lecture_sans_cle():
    """N1 (06/11) : un type compte si son taux médian (borne haute de Clopper-Pearson à 50 %) est au plus la barre ; il
    est jugeable si zéro erreur suffirait. Le taux observé ne suffit plus."""
    b = 1 / 132
    assert CL.mediane_haute(0, 100) == pytest.approx(1 - 0.5 ** (1 / 100))
    oui, non = CL.classer(0, 100, b), CL.classer(0, 80, b)
    assert oui["jugeable"] and oui["estime_sous"] and not non["jugeable"] and not non["estime_sous"]
    assert non["p"] == 0 <= b                                   # le taux observé disait « sous la barre » (défaut N1)
    une = CL.classer(1, 300, b)                                  # environ deux tiers d'erreur de plus que le compte
    assert une["hi50"] == pytest.approx(1.68 / 300, rel=0.02) and une["estime_sous"]
    assert not CL.classer(2, 300, b)["estime_sous"]
    vide = CL.classer(0, 0, b)
    assert not vide["estime_sous"] and not vide["jugeable"]
    # lecture d'une classe sans les clés calculées (sorties relues) : même règle ; faute de comptes, la preuve seule
    assert CL.estime_sous(dict(n=100, x=0, x_eff=0.0, n_eff=100.0, barre=b))
    assert not CL.estime_sous(dict(n=80, x=0, x_eff=0.0, n_eff=80.0, barre=b))
    assert CL.jugeable(dict(n=100, n_eff=100.0, barre=b)) and not CL.jugeable(dict(n=80, n_eff=80.0, barre=b))
    assert CL.estime_sous(dict(classe=CL.SOUS)) and not CL.estime_sous(dict(classe=CL.INDETERMINE))
