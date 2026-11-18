"""Contrôles du code obligatoires (PLAN_SIMULATION.md, section 8), adaptés à l'amendement A1
(score réfléchi, REGLE.md, section « Amendements »).

Les nombres de référence viennent de lectures/wald_test_sequentiel.md, vérifiés dans
lectures/_verification.md. La v1 (première passe) reste testée par le contrôle de cohérence
entre le moteur et la version de référence, pour pouvoir reproduire resultats_v1/.
"""
import math

import numpy as np
import pytest

import config as C
import flux as F
import regle as RG
import sprt
import temoins as TM


def type_faible(pb, pm, alpha=0.05, beta=0.05, a_palier2=False):
    """Un type à enjeu faible, sans palier 2 (score réfléchi) : la descente suit le seul score."""
    a = math.log(pm / pb)
    b = -math.log((1 - pm) / (1 - pb))
    lnB = math.log(beta / (1 - alpha))
    return RG.RegleUnTypeV2(0.0, 0.0, a, b, lnB, a_palier2, False)


def au_plancher(rg, n=1000):
    for _ in range(n):
        rg.succes()
    assert rg.L3 == pytest.approx(rg.plancher3)
    return rg


P_DEP = C.params_regle("depart", 0.05)


# --------------------------------------------------------------------------
# Les nombres de référence (amendement A1)
# --------------------------------------------------------------------------
def test_35_reussites_depuis_L_zero():
    assert sprt.reussites_pour_monter(0.02, 0.10, 0.05, 0.05) == 35
    assert P_DEP.pb3[C.DUR] == pytest.approx(0.02) and P_DEP.pm3[C.DUR] == pytest.approx(0.10)
    rg = RG.RegleUnTypeV2.depuis_params(P_DEP, C.DUR)
    assert rg.L3 == 0.0
    n = 0
    while rg.palier < 3:
        rg.succes()
        n += 1
        assert n < 1000
    assert n == 35


def test_54_reussites_apres_une_erreur_a_enjeu_moyen_ou_fort():
    assert sprt.reussites_pour_monter(0.02, 0.10, 0.05, 0.05, s=1) == 54
    for depart_au_plancher in (False, True):
        rg = RG.RegleUnTypeV2.depuis_params(P_DEP, C.DUR)
        if depart_au_plancher:
            au_plancher(rg)
            assert rg.palier == 3
        rg.erreur()
        assert rg.L3 == pytest.approx(rg.a3)  # L = max(L, 0) + a : le crédit de réussites est effacé
        assert rg.palier == 1 and rg.epreuves_ouvertes() == 1
        assert rg.epreuve_due()
        rg.resultat_epreuve(True)
        n = 0
        while rg.palier < 3:
            rg.succes()
            n += 1
            assert n < 1000
        assert n == 54


@pytest.mark.parametrize("pb,pm", [(0.05, 0.20), (0.10, 0.30), (0.02, 0.10), (0.01, 0.05),
                                   (0.025, 0.10), (0.075, 0.30)])
def test_erreur_au_plancher_absorbee_en_a_sur_b_reussites(pb, pm):
    rg = au_plancher(type_faible(pb, pm))
    rg.erreur()
    assert rg.L3 == pytest.approx(rg.lnB)
    attendu = math.ceil(rg.a3 / rg.b3 - 1e-12)
    n = 0
    while rg.L3 > rg.plancher3 + 1e-12:
        rg.succes()
        n += 1
    assert n == attendu


def test_absorption_sur_les_vrais_types_a_enjeu_faible():
    # LEC : les deux scores (palier 3 et palier 2) ; REGLE.md, A1 : « environ 8 réussites à enjeu faible »
    lec = RG.RegleUnTypeV2.depuis_params(P_DEP, C.LEC)
    for _ in range(1000):
        lec.succes()
    lec.erreur()
    assert lec.palier == 3
    n3 = n2 = None
    for i in range(1, 100):
        lec.succes()
        if n3 is None and lec.L3 <= lec.plancher3 + 1e-12:
            n3 = i
        if n2 is None and lec.L2 <= lec.plancher2 + 1e-12:
            n2 = i
    assert lec.a3 / lec.b3 == pytest.approx(8.07, abs=0.01)
    assert n3 == math.ceil(lec.a3 / lec.b3) == 9
    assert n2 == math.ceil(lec.a2 / lec.b2) == 5


def test_deux_erreurs_faibles_rapprochees_font_descendre_d_un_palier_depuis_le_plancher():
    lec = RG.RegleUnTypeV2.depuis_params(P_DEP, C.LEC)
    for _ in range(1000):
        lec.succes()
    assert lec.palier == 3
    lec.erreur()
    assert lec.palier == 3  # la 1re ramène le score exactement à ln B
    lec.erreur()
    assert lec.palier == 2  # la 2e fait descendre d'un seul palier
    msg = RG.RegleUnTypeV2.depuis_params(P_DEP, C.MSG)  # irréversible : du palier 3 au palier 1
    for _ in range(1000):
        msg.succes()
    msg.erreur()
    assert msg.palier == 3
    msg.erreur()
    assert msg.palier == 1
    # deux erreurs séparées par a/b réussites ne font plus descendre : la première est absorbée
    lec = RG.RegleUnTypeV2.depuis_params(P_DEP, C.LEC)
    for _ in range(1000):
        lec.succes()
    for _ in range(20):
        lec.erreur()
        assert lec.palier == 3
        for _ in range(math.ceil(lec.a3 / lec.b3)):
            lec.succes()


def part_sans_validation(P, debut, fin):
    return float((P[:, debut:fin] >= 2).mean())


def test_agent_stable_a_2pc_l_autonomie_ne_s_eteint_plus():
    """Critère fixé avant de voir la v2 : la part d'actions exécutées sans validation préalable
    (palier 2 ou 3) sur les 500 dernières actions reste à moins de 10 % (relatifs) de celle des
    500 actions du milieu de l'horizon. La même mesure, sous la v1, montre l'extinction."""
    agent = C.AGENTS_PAR_NOM["A2"]
    fl = F.generer_flux("bureau", 1000, seed=[C.GRAINE, 87])
    milieu = (1250, 1750)
    fin = (2500, 3000)
    res = RG.simuler_regle(fl, agent, [C.params_regle("depart", 0.05)])
    m, f = part_sans_validation(res.P, *milieu), part_sans_validation(res.P, *fin)
    assert m > 0.05
    assert abs(f / m - 1) <= 0.10, (m, f)
    res1 = RG.simuler_regle(fl, agent, [C.params_regle("depart", 0.05, version="v1")])
    m1, f1 = part_sans_validation(res1.P, *milieu), part_sans_validation(res1.P, *fin)
    assert f1 / m1 < 0.6, (m1, f1)  # le test sépare bien les deux versions


def test_risques_reels_du_test_sans_borne():
    _, rej2, asn2 = sprt.sprt_exact(0.02, 0.02, 0.10, 0.05, 0.05)
    acc10, _, asn10 = sprt.sprt_exact(0.10, 0.02, 0.10, 0.05, 0.05)
    assert round(100 * rej2, 2) == 2.97
    assert round(100 * acc10, 2) == 4.89
    assert asn2 == pytest.approx(54.58, abs=0.01)
    assert asn10 == pytest.approx(38.30, abs=0.01)
    rng = np.random.default_rng([C.GRAINE, 99])
    _, rej2_mc, _ = sprt.sprt_monte_carlo(0.02, 0.02, 0.10, 0.05, 0.05, 400_000, rng)
    acc10_mc, _, _ = sprt.sprt_monte_carlo(0.10, 0.02, 0.10, 0.05, 0.05, 400_000, rng)
    assert abs(rej2_mc - 0.0297) < 0.0015
    assert abs(acc10_mc - 0.0489) < 0.0015


def test_enchainer_n_reussites_vaut_p_puissance_n():
    assert 0.95 ** 20 == pytest.approx(0.358, abs=0.0005)
    agent = C.agent_q_constant(0.05)
    R = 20000
    fl = F.generer_flux("bureau", R, 200, seed=[C.GRAINE, 98])
    err = F.erreurs(fl, agent)
    lec = fl.type == C.LEC
    m = lec & (np.cumsum(lec, axis=1) <= 20)
    assert (m.sum(axis=1) == 20).all()
    p = float((~(err & m).any(axis=1)).mean())
    se = math.sqrt(0.95 ** 20 * (1 - 0.95 ** 20) / R)
    assert abs(p - 0.95 ** 20) < 4 * se


# --------------------------------------------------------------------------
# Les propriétés de la règle (v2)
# --------------------------------------------------------------------------
@pytest.mark.parametrize("k", [C.DUR, C.EXE, C.SOR, C.ARG])
def test_erreur_enjeu_moyen_ou_fort_ramene_au_palier_1_et_ouvre_une_epreuve(k):
    rg = RG.RegleUnTypeV2.depuis_params(P_DEP, k)
    for _ in range(1000):
        rg.succes()
    assert rg.palier == 3
    rg.erreur()
    assert (rg.palier, rg.s, rg.epreuves_ouvertes()) == (1, 1, 1)
    assert rg.L3 == pytest.approx(rg.a3)
    if rg.a_palier2:
        assert rg.L2 == pytest.approx(rg.a2)
    rg.succes()
    assert rg.L3 == pytest.approx(rg.a3)  # le score ne bouge pas tant que l'épreuve est ouverte
    assert rg.epreuve_due()
    rg.resultat_epreuve(False)
    for _ in range(C.EPREUVE_ATTENTE):
        assert not rg.epreuve_due()
    assert rg.epreuve_due()
    rg.resultat_epreuve(True)
    assert rg.epreuves_ouvertes() == 0 and rg.s == 1
    rg.succes()
    assert rg.L3 == pytest.approx(rg.a3 - rg.b3)


def test_erreur_enjeu_moyen_dans_le_moteur():
    agent = C.AGENTS_PAR_NOM["A3"]
    fl = F.generer_flux("service_client", 60, 1500, seed=[C.GRAINE, 96])
    res = RG.simuler_regle(fl, agent, [C.params_regle()])
    err = F.erreurs(fl, agent)
    vu = 0
    for rep in range(fl.R):
        typ = fl.type[rep]
        deja = set()
        for t in np.nonzero(fl.verifiable[rep] & err[rep] & C.ENJEU_HAUT[typ])[0]:
            k = typ[t]
            suite = np.nonzero(typ[t + 1:] == k)[0]
            if suite.size == 0:
                continue
            t2 = t + 1 + suite[0]
            assert res.P[rep, t2] == 1
            if k not in deja:
                assert res.ep_var[rep, t2] >= C.EPREUVE_VARIANTES
                vu += 1
            deja.add(k)
    assert vu > 50


def test_plafonnes_jamais_autonomes():
    fl = F.generer_flux("bureau", 200, 3000, seed=[C.GRAINE, 95])
    pla = fl.type == C.PLA
    variantes = [C.params_regle()] + [C.params_regle(**kw) for kw in C.ABLATIONS.values()]
    for nom in ["A1", "A7", "A2-abusif"]:
        agent = C.AGENTS_PAR_NOM[nom]
        res = RG.simuler_regle(fl, agent, variantes)
        for i in range(len(variantes)):
            assert (res.P[res.lignes(i)][pla] == 1).all()
        cpt = res.extraire(0)["comptes"]
        assert (TM.paliers_hasard(fl.type, cpt, np.random.default_rng(0))[pla] == 1).all()
        assert (TM.paliers_oracle(fl.type, agent, variantes[0])[pla] == 1).all()
        tr = TM.simuler_trois_reussites(fl, F.erreurs(fl, agent), F.doutes(fl, agent))
        assert (tr["P"][pla] == 1).all()
    assert (TM.paliers_liste_fixe(fl.type)[pla] == 1).all()
    assert (TM.paliers_tri_risque(fl.type)[pla] == 1).all()


def rejouer_score(issues, rg_type):
    """Le score réfléchi rejoué à la main sur une suite d'issues jugées (True = réussite)."""
    L3 = 0.0
    for ok in issues:
        L3 = max(L3 - rg_type.b3, rg_type.plancher3) if ok else L3 + rg_type.a3
    return L3


def test_le_doute_ne_change_ni_le_score_ni_s():
    rg = RG.RegleUnTypeV2.depuis_params(P_DEP, C.LEC)
    for _ in range(5):
        rg.succes()
    rg.erreur()
    avant = (rg.L3, rg.L2, rg.s, rg.palier)
    rg.neutre()
    assert (rg.L3, rg.L2, rg.s, rg.palier) == avant
    agent = C.AGENTS_PAR_NOM["A2"]
    fl = F.generer_flux("bureau", 50, 3000, seed=[C.GRAINE, 94])
    tout = np.ones((fl.R, fl.T), dtype=bool)
    res = RG.simuler_regle(fl, agent, [P_DEP], dou=tout)
    assert (res.L3_final == 0).all() and (res.s_final == 0).all() and (res.P == 1).all()
    agent = C.AGENTS_PAR_NOM["A2-abusif"]
    res = RG.simuler_regle(fl, agent, [P_DEP])
    err = F.erreurs(fl, agent)
    dou = F.doutes(fl, agent)
    juge = (fl.type == C.LEC) & fl.verifiable & ~dou
    assert dou[fl.type == C.LEC].mean() > 0.25
    np.testing.assert_array_equal(res.s_final[:, C.LEC], (juge & err).sum(axis=1))
    ref = RG.RegleUnTypeV2.depuis_params(P_DEP, C.LEC)
    for rep in range(fl.R):
        issues = (~err[rep])[juge[rep]]
        assert res.L3_final[rep, C.LEC] == pytest.approx(rejouer_score(issues, ref))


def test_remises_a_zero_amendement_A1():
    # consigne modifiée : L divisé par deux seulement s'il est négatif
    rg = RG.RegleUnTypeV2.depuis_params(P_DEP, C.SOR)
    for _ in range(80):
        rg.succes()
    L = rg.L3
    assert L < 0
    rg.consigne_modifiee()
    assert rg.L3 == pytest.approx(L / 2) and rg.s == 0
    rg = RG.RegleUnTypeV2.depuis_params(P_DEP, C.SOR)
    rg.erreur()
    rg.resultat_epreuve(True)
    L = rg.L3
    assert L > 0
    rg.consigne_modifiee()
    assert rg.L3 == pytest.approx(L)
    # changement de modèle, type à enjeu fort : L = 0, les erreurs deviennent des épreuves
    rg = RG.RegleUnTypeV2.depuis_params(P_DEP, C.ARG)
    rg.erreur()
    rg.resultat_epreuve(True)  # épreuve de descente réussie : s intact (même configuration)
    assert rg.s == 1
    rg.erreur()
    assert rg.s == 2
    rg.changement_configuration()
    assert (rg.L3, rg.s, rg.E_conv, rg.E_desc, rg.palier) == (0.0, 2, 2, 0, 1)
    assert rg.epreuve_due()
    rg.resultat_epreuve(False)
    assert rg.s == 2  # épreuve ratée : l'erreur reste
    for _ in range(C.EPREUVE_ATTENTE):
        rg.epreuve_due()
    assert rg.epreuve_due()
    rg.resultat_epreuve(True)
    assert rg.s == 1  # épreuve réussie après changement : l'erreur est effacée
    rg.resultat_epreuve(True)
    assert rg.s == 0 and rg.epreuves_ouvertes() == 0
    # changement de modèle, type à enjeu faible : L = 0 et les erreurs disparaissent (A1)
    lec = RG.RegleUnTypeV2.depuis_params(P_DEP, C.LEC)
    for _ in range(30):
        lec.succes()
    lec.erreur()
    lec.erreur()
    lec.changement_configuration()
    assert (lec.L3, lec.L2, lec.s, lec.palier) == (0.0, 0.0, 0, 1)
    assert lec.epreuves_ouvertes() == 0
    # moteur, A8 : la consigne modifiée ne touche jamais s
    agent = C.AGENTS_PAR_NOM["A8"]
    fl = F.generer_flux("bureau", 100, 3000, seed=[C.GRAINE, 93])
    res = RG.simuler_regle(fl, agent, [P_DEP, C.params_regle(remises=False)])
    err = F.erreurs(fl, agent)
    attendu = ((fl.type == C.SOR) & fl.verifiable & err).sum(axis=1)
    np.testing.assert_array_equal(res.s_final[res.lignes(0), C.SOR], attendu)
    np.testing.assert_array_equal(res.s_final[res.lignes(1), C.SOR], attendu)
    # moteur, A6a : après le changement de modèle, les erreurs faibles d'avant ne comptent plus
    agent = C.AGENTS_PAR_NOM["A6a"]
    res = RG.simuler_regle(fl, agent, [P_DEP])
    err = F.erreurs(fl, agent)
    apres = np.arange(fl.T)[None, :] >= agent.t_change
    attendu = ((fl.type == C.LEC) & fl.verifiable & err & apres).sum(axis=1)
    np.testing.assert_array_equal(res.s_final[:, C.LEC], attendu)


# --------------------------------------------------------------------------
# Cohérence du moteur vectorisé avec la version de référence (v2, et v1 pour resultats_v1/)
# --------------------------------------------------------------------------
@pytest.mark.parametrize("version", ["v2", "v1"])
@pytest.mark.parametrize("nom", ["A2", "A3", "A4", "A6a", "A6b", "A7", "A8", "A2-calibre", "A4-abusif"])
def test_moteur_identique_a_la_reference(nom, version):
    agent = C.AGENTS_PAR_NOM[nom]
    fl = F.generer_flux("service_client", 4, 3000, seed=[C.GRAINE, 92, C.ID_AGENT[nom]])

    def pr(*a, **kw):
        return C.params_regle(*a, version=version, **kw)

    variantes = [pr(), pr("stricte", 0.20), pr("souple", 0.05)]
    variantes += [pr(**kw) for kw in C.ABLATIONS.values()]
    if version == "v1":
        variantes += [pr(oubli_faibles_au_changement=True), pr(plancher_glissant=True)]
    res = RG.simuler_regle(fl, agent, variantes, journal=True)
    for i, p in enumerate(variantes):
        for rep in range(fl.R):
            ref = RG.rejouer_reference(fl, agent, p, rep, res.journal_epreuves, i * fl.R + rep)
            np.testing.assert_array_equal(ref, res.P[i * fl.R + rep],
                                          err_msg=f"{nom} {version} variante {i} rép {rep}")


# --------------------------------------------------------------------------
# Le tirage et les témoins
# --------------------------------------------------------------------------
def test_moyenne_des_erreurs_vaut_q_et_les_erreurs_se_concentrent():
    fl = F.generer_flux("bureau", 1000, 3000, seed=[C.GRAINE, 91])
    for q in [0.005, 0.02, 0.05, 0.15]:
        err = F.erreurs(fl, C.agent_q_constant(q))
        n = err.size
        assert abs(err.mean() - q) < 5 * math.sqrt(q * (1 - q) / n)
        qd = min(0.9, 6 * q)
        nd = fl.difficile.sum()
        assert abs(err[fl.difficile].mean() - qd) < 5 * math.sqrt(qd * (1 - qd) / nd)


def test_temoins_fixes():
    fl = F.generer_flux("bureau", 10, 500, seed=[C.GRAINE, 90])
    lf = TM.paliers_liste_fixe(fl.type)
    tr = TM.paliers_tri_risque(fl.type)
    for k in range(C.N_TYPES):
        m = fl.type == k
        assert (lf[m] == (3 if k in (C.LEC, C.ECR) else 1)).all()
        assert (tr[m] == (3 if k in (C.LEC, C.ECR, C.MSG) else 1)).all()


def test_trois_reussites():
    fl = F.generer_flux("bureau", 20, 3000, seed=[C.GRAINE, 89])
    agent = C.AGENTS_PAR_NOM["A3"]
    err = F.erreurs(fl, agent)
    dou = F.doutes(fl, agent)
    out = TM.simuler_trois_reussites(fl, err, dou)
    for rep in range(fl.R):
        serie = np.zeros(8, dtype=int)
        pal = np.ones(8, dtype=int)
        for t in range(fl.T):
            k = fl.type[rep, t]
            assert out["P"][rep, t] == (1 if k == C.PLA else pal[k])
            if k == C.PLA or not fl.verifiable[rep, t]:
                continue
            if err[rep, t]:
                serie[k] = 0
                pal[k] = 1
            else:
                serie[k] += 1
                if serie[k] >= 3:
                    pal[k] = 3


def test_hasard_garde_la_part_du_temps():
    fl = F.generer_flux("bureau", 300, 3000, seed=[C.GRAINE, 88])
    agent = C.AGENTS_PAR_NOM["A1"]
    res = RG.simuler_regle(fl, agent, [C.params_regle()])
    Ph = TM.paliers_hasard(fl.type, res.comptes, np.random.default_rng(1))
    for k in [C.LEC, C.ECR, C.EXE, C.SOR]:
        m = fl.type == k
        assert abs((Ph[m] == 3).mean() - (res.P[m] == 3).mean()) < 0.01
        assert abs((Ph[m] == 2).mean() - (res.P[m] == 2).mean()) < 0.01
