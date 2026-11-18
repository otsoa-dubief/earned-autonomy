"""Contrôles du code de l'exploration E1 (PLAN_EXPLORATION_E1.md, section 5).

- N et barres épinglés (fractions exactes) ;
- référence RegleUnTypeB, et cohérence du moteur avec les références, action par action (A et B,
  modes de résistance compris) ;
- le moteur E1, réglé comme la v2, refait exactement le moteur v2 ;
- suites piège de la mesure 8 ; oracle avec palier 2 ; LEC hors des dégâts ; graine à part du
  contrôle imparfait ; comptabilité ; étalonnage d'A-dégâts.
"""
import dataclasses
import json
import math
import os
from fractions import Fraction

import numpy as np
import pytest

import config as C
import config_e1 as E
import etalonnage_e1 as ET
import executer_e1 as X
import flux as F
import regle as RG
import regle_e1 as RE

ICI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# --------------------------------------------------------------------------
# Barres et N exacts
# --------------------------------------------------------------------------
def test_barres_exactes():
    attendu = {("bureau", "faible"): Fraction(10, 399), ("bureau", "moyen"): Fraction(1, 304),
               ("bureau", "fort"): Fraction(1, 2584), ("service_client", "faible"): Fraction(5, 76),
               ("service_client", "moyen"): Fraction(1, 418), ("service_client", "fort"): Fraction(1, 4408)}
    assert E.BARRES == attendu


def test_N_epingles():
    breg = [15, 118, 1001, 6, 162, 1707]
    btout = [41, 319, 2719, 15, 439, 4639]
    cellules = [(m, n) for m in ("bureau", "service_client") for n in ("faible", "moyen", "fort")]
    assert [E.N_B_REGULIER[c] for c in cellules] == breg
    assert [E.N_B_TOUT[c] for c in cellules] == btout
    for c in cellules:
        db = E.D_CONSTAT * E.BARRES[c]
        assert E.N_B_TOUT[c] + 1 == 1 / db  # entier exact : pas d'arrondi de flottant
        n = E.N_B_REGULIER[c]
        assert Fraction(n ** n, (n + 1) ** (n + 1)) <= db < Fraction((n - 1) ** (n - 1), n ** n)
    assert [E.n_allonge(n) for n in (15, 118, 1001)] == [19, 148, 1252]


def test_parametres_des_regles():
    for m in E.MELANGES:
        a12, a14, ad = (E.regle_e1(n, m) for n in ("A½", "A¼", "A-dégâts"))
        for k in (C.ECR, C.DUR, C.EXE, C.MSG, C.SOR, C.ARG):
            b = float(E.BARRES[(m, E.niveau_type(k))])
            assert a12.params.pm3[k] == pytest.approx(b) and a12.params.pb3[k] == pytest.approx(b / 2)
            assert a14.params.pm3[k] == pytest.approx(b) and a14.params.pb3[k] == pytest.approx(b / 4)
            assert ad.params.pb3[k] == pytest.approx(ad.params.pm3[k] / 2)
            assert a12.params.alpha == 0.05
        dep = C.params_regle("depart", 0.05)
        for r in E.regles_e1(m):  # le palier 2 garde les réglages de départ
            np.testing.assert_allclose(r.params.pb2, dep.pb2)
            np.testing.assert_allclose(r.params.pm2, dep.pm2)
    # nombres de la relecture (table des formules)
    r = E.regle_e1("A½", "bureau")
    assert math.ceil(-r.params.lnB / r.params.b3[C.SOR] - 1e-12) == 15213
    assert math.ceil((r.params.a3[C.DUR] - r.params.lnB) / r.params.b3[C.DUR] - 1e-12) == 2207


def test_etalonnage_recopie_et_documente():
    with open(os.path.join(ICI, "etalonnage_e1.json")) as f:
        et = json.load(f)
    for c in et["cellules"]:
        assert E.PM3_A_DEGATS[(c["melange"], c["niveau"])] == c["pm3"]
        assert abs(c["E_sur_barre"] - 1) < 0.003
        assert not c["bord_de_grille"]
    assert len(et["cellules"]) == 6


# --------------------------------------------------------------------------
# Agents
# --------------------------------------------------------------------------
def test_agents_ajoutes_en_fin_de_liste():
    for a in C.AGENTS:
        assert E.ID_AGENT_E1[a.nom] == C.ID_AGENT[a.nom]
    assert E.ID_AGENT_E1["A0"] == 13 and E.ID_AGENT_E1["A0d"] == 14
    assert min(E.ID_AGENT_E1[n] for n in E.NOMS_BORD + E.NOMS_BORD_D) == 15
    for h, T in (("court", 3000), ("long", 150_000)):
        for m in E.MELANGES:
            ags = {a.nom: a for a in E.agents_horizon(h, m)}
            for a in ags.values():
                if a.t_change is not None:
                    assert a.t_change == T // 2
            assert ("A0d" in ags) == (h == "long")
    bords = {a.nom: a for a in E.agents_bord("bureau")}
    a = bords["bord_moyen_pireBreg"]
    assert a.q_avant[C.DUR] == pytest.approx(1 / 119) and a.q_avant[C.SOR] == E.TAUX_A0
    a = bords["bordD_fort_3barre"]
    assert a.q_avant[C.SOR] == E.TAUX_A0 and a.q_apres[C.SOR] == pytest.approx(3 / 2584) and a.evenement is None


# --------------------------------------------------------------------------
# Référence de la règle B
# --------------------------------------------------------------------------
def regle_b(k, mix="bureau", nom="B-régulier"):
    return RE.RegleUnTypeB.depuis_regle(E.regle_e1(nom, mix), k)


def monter(rg, n_max=100_000):
    n = 0
    while rg.palier < 3:
        if rg.epreuve_due():
            rg.resultat_epreuve(True)
        rg.succes()
        n += 1
        assert n < n_max
    return n


def test_B_monte_apres_N_reussites_et_toute_erreur_remet_a_zero():
    rg = regle_b(C.MSG)  # N = 15, enjeu faible, irréversible
    for _ in range(14):
        rg.succes()
    assert rg.palier == 1 and rg.c == 14
    rg.erreur()
    assert rg.c == 0 and rg.palier == 1 and rg.epreuves_ouvertes() == 0
    assert monter(rg) == 15
    for _ in range(50):
        rg.succes()
    assert rg.c == 15  # plafonné à N
    rg.neutre()
    assert rg.palier == 3
    rg.erreur()
    assert rg.palier == 1 and rg.c == 0  # irréversible : palier 1
    ecr = regle_b(C.ECR)
    monter(ecr)
    ecr.erreur()
    assert ecr.palier == 2  # réversible, enjeu faible : palier 2


def test_B_erreur_moyenne_ou_forte_epreuve_et_allongement_de_la_piece_7_3():
    for k, N in ((C.DUR, 118), (C.EXE, 118), (C.SOR, 1001)):
        rg = regle_b(k)
        assert monter(rg) == N
        rg.erreur()
        assert (rg.palier, rg.c, rg.epreuves_ouvertes(), rg.allonge) == (1, 0, 1, True)
        rg.succes()
        assert rg.c == 0  # le compteur ne bouge pas tant que l'épreuve est ouverte
        assert rg.epreuve_due()
        rg.resultat_epreuve(False)
        for _ in range(C.EPREUVE_ATTENTE):
            assert not rg.epreuve_due()
            rg.succes()
        assert rg.c == 0
        assert monter(rg) == E.n_allonge(N)  # ⌈1,25 N⌉ (l'épreuve réussie au même pas compte)
        assert not rg.allonge and rg.c == N
        # une erreur pendant la montée (à n'importe quel palier) remet à 0 et garde l'allongement
        rg.erreur()
        rg.resultat_epreuve(True)
        for _ in range(N):
            rg.succes()
        rg.erreur()
        assert rg.c == 0 and rg.allonge
        rg.resultat_epreuve(True)
        assert monter(rg) == E.n_allonge(N)


def test_B_consigne_et_changement_de_modele():
    rg = regle_b(C.SOR)
    monter(rg)
    rg.consigne_modifiee()
    assert rg.c == 1001 // 2 and rg.palier == 1  # ⌊N/2⌋ : le palier 3 est perdu
    assert monter(rg) == 1001 - 500  # sans nouvelle erreur, la montée suivante exige N
    rg.erreur()
    rg.resultat_epreuve(True)
    rg.erreur()
    assert rg.s == 2
    rg.changement_configuration()
    assert (rg.c, rg.allonge, rg.E_conv, rg.E_desc, rg.palier) == (0, False, 2, 0, 1)
    rg.resultat_epreuve(True)
    assert rg.s == 1
    rg.resultat_epreuve(True)
    assert rg.s == 0
    assert monter(rg) == 1001  # nouvel agent : N, pas d'allongement
    ecr = regle_b(C.ECR)
    monter(ecr)
    ecr.erreur()
    ecr.changement_configuration()
    assert ecr.s == 0 and ecr.epreuves_ouvertes() == 0 and ecr.c == 0


def test_B_palier_2_garde_le_score_de_wald():
    exe = regle_b(C.EXE)
    p = E.regle_e1("B-régulier", "bureau").params
    n2 = math.ceil(-p.lnB / p.b2[C.EXE] - 1e-12)
    for _ in range(n2 - 1):
        exe.succes()
    assert exe.palier == 1
    exe.succes()
    assert exe.palier == 2


# --------------------------------------------------------------------------
# Cohérence du moteur avec les références, action par action
# --------------------------------------------------------------------------
def regles_test(mix):
    regles = E.regles_e1(mix)
    petits = [E.RegleE1(r.nom + "-petit", "B", r.params, np.where(r.N > 0, np.maximum(2, r.N // 40), 0))
              for r in regles if r.famille == "B"]
    petitsA = [E.RegleE1("A-rapide", "A", C.params_regle("souple", 0.20), np.zeros(8, np.int64))]
    return regles + petits + petitsA


@pytest.mark.parametrize("mix", ["bureau", "service_client"])
@pytest.mark.parametrize("nom", ["A2", "A3", "A6a", "A6b", "A7", "A8", "A2-calibre", "A4-abusif",
                                 "bord_faible_pireBreg", "bordD_moyen_3barre"])
def test_moteur_identique_aux_references(nom, mix):
    ag = C.AGENTS_PAR_NOM.get(nom) or next(a for a in E.agents_bord(mix) if a.nom == nom)
    ag = E.agent_horizon(ag, 3000)
    fx = RE.flux_e1("court", mix, ag, [7], taille_bloc=2)
    var = [(r, m) for m in E.MODES for r in regles_test(mix)]
    res = RE.simuler_e1(fx, ag, var, {m: [5, i] for i, m in enumerate(E.MODES)}, journal=True, garder_P=True)
    for i, (r, m) in enumerate(var):
        for rep in range(fx.R):
            ref = RE.rejouer_reference_e1(fx, ag, r, m, rep, res.journal_epreuves, i * fx.R + rep, res.tc)
            np.testing.assert_array_equal(ref, res.P[:, i * fx.R + rep], err_msg=f"{nom} {r.nom} {m} {rep}")


def fx_depuis_flux(fl, agent):
    err, dou = F.erreurs(fl, agent), F.doutes(fl, agent)
    z = np.zeros((fl.T, fl.R), bool)
    tr = lambda x: np.ascontiguousarray(x.T)  # noqa: E731
    return RE.FluxE1(fl.melange, fl.R, fl.T, tr(fl.type), tr(fl.verifiable), tr(fl.difficile), tr(err), tr(dou),
                     tr(fl.u_val < 0.05), z)


@pytest.mark.parametrize("nom", ["A2", "A6a", "A7", "A8", "A4-calibre"])
def test_moteur_E1_regle_comme_la_v2_refait_le_moteur_v2(nom):
    """A½ « est la règle v2 » : avec les réglages et les interrupteurs de la v2, le moteur E1 rend
    exactement les paliers du moteur v2 (mêmes tirages d'épreuve)."""
    agent = C.AGENTS_PAR_NOM[nom]
    fl = F.generer_flux("service_client", 30, 3000, seed=[C.GRAINE, 92, C.ID_AGENT[nom]])
    ps = [C.params_regle(), C.params_regle("stricte", 0.20)]
    g = RG.graine_regle(agent.nom, fl.melange, 0)
    res = RG.simuler_regle(fl, agent, ps, graine=g)
    var = [(E.RegleE1("v2", "A", p, np.zeros(8, np.int64), lec_autonome=False), "base") for p in ps]
    r2 = RE.simuler_e1(fx_depuis_flux(fl, agent), agent, var, {"base": g}, tc=1500, garder_P=True,
                       lec_sans_effet=False)
    np.testing.assert_array_equal(r2.P.T, res.P)


# --------------------------------------------------------------------------
# Mesure 8 : suites piège
# --------------------------------------------------------------------------
@pytest.mark.parametrize("mix", ["bureau", "service_client"])
def test_suites_piege(mix):
    rng = np.random.default_rng(0)
    d = 0.95
    for nom in ("B-régulier", "B-tout"):
        r = E.regle_e1(nom, mix)
        for k in (C.ECR, C.MSG, C.DUR, C.SOR):
            N = int(r.N[k])
            Ne = E.n_allonge(N) if C.ENJEU_HAUT[k] else N
            # « N réussites puis une erreur » : 0,95 ÷ (N + 1) à enjeu faible ; à enjeu moyen ou fort,
            # l'allongement donne 0,95 ÷ (⌈1,25 N⌉ + 1) une fois le premier cycle passé
            p1 = X.suite_piege(RE.RegleUnTypeB.depuis_regle(r, k), 60)
            if not C.ENJEU_HAUT[k]:
                assert p1 == pytest.approx(0.95 / (N + 1), rel=1e-12)
            else:
                assert p1 <= 0.95 / (N + 1)
                assert p1 == pytest.approx(0.95 / (Ne + 1), rel=0.01)
            # « rafale » : N réussites puis des erreurs jusqu'au retrait, constatées avec la proba d
            if N <= 170:
                p2 = X.suite_piege(RE.RegleUnTypeB.depuis_regle(r, k), 2000, rafale=True, d=d, rng=rng)
                attendu = 0.95 / (d * Ne + 1)
                assert p2 == pytest.approx(attendu, rel=0.05), (nom, k, p2, attendu)
                assert p2 > 0.95 / (Ne + 1)


# --------------------------------------------------------------------------
# Oracle avec palier 2, témoins, LEC hors des dégâts
# --------------------------------------------------------------------------
def test_oracle_avec_palier_2():
    fl = F.generer_flux("bureau", 5, 400, seed=[C.GRAINE, 70])
    typ = np.ascontiguousarray(fl.type.T)
    ag = E.agent_horizon(E.A0D, 400)  # 1/10 000 puis 1/200 à t = 200
    P = RE.paliers_oracle_p2(typ, ag, "bureau", 200)
    av, ap = P[:200], P[200:]
    for k in range(C.N_TYPES):
        m_av, m_ap = typ[:200] == k, typ[200:] == k
        if k == C.LEC:
            assert (av[m_av] == 3).all() and (ap[m_ap] == 3).all()
        elif k == C.PLA:
            assert (av[m_av] == 1).all() and (ap[m_ap] == 1).all()
        else:
            assert (av[m_av] == 3).all()  # 1/10 000 : sous toutes les barres
            b = float(E.BARRES[("bureau", E.niveau_type(k))])
            att = 3 if 1 / 200 <= b else (2 if C.A_PALIER2[k] else 1)
            assert (ap[m_ap] == att).all(), (C.TYPES[k], att)
    # 1/200 : sous la barre faible (ECR, MSG au palier 3) ; EXE réversible au palier 2 ; DUR, SOR, ARG au palier 1
    assert {C.TYPES[k]: int(ap[typ[200:] == k][0]) for k in (C.ECR, C.MSG, C.EXE, C.DUR, C.SOR, C.ARG)} == \
        dict(ECR=3, MSG=3, EXE=2, DUR=1, SOR=1, ARG=1)


def test_temoins_E1_lec_autonome():
    fl = F.generer_flux("bureau", 4, 300, seed=[C.GRAINE, 71])
    typ = np.ascontiguousarray(fl.type.T)
    lec = typ == C.LEC
    for nom in ("tout_valider", "liste_fixe", "tri_risque", "tout_approuver"):
        P = RE.paliers_fixes(nom, typ)
        assert (P[lec] == 3).all()
        P0 = RE.paliers_fixes(nom, typ, lec_autonome=False)
        if nom == "tout_valider":
            assert (P0 == 1).all() and (P[~lec] == 1).all()
    ag = C.AGENTS_PAR_NOM["A3"]
    fx = fx_depuis_flux(fl, ag)
    P3 = RE.paliers_trois_reussites(fx, lec_autonome=False)
    import temoins as TM
    ref = TM.simuler_trois_reussites(fl, F.erreurs(fl, ag), F.doutes(fl, ag))["P"]
    np.testing.assert_array_equal(P3.T, ref)
    assert (RE.paliers_trois_reussites(fx)[lec] == 3).all()


def test_lec_hors_des_degats_et_autonome_des_le_depart():
    ag = E.agent_horizon(C.AGENTS_PAR_NOM["A4"], 3000)
    fx = RE.flux_e1("court", "bureau", ag, [3], taille_bloc=20)
    regles = E.regles_e1("bureau")
    res = RE.simuler_e1(fx, ag, [(r, "base") for r in regles], {"base": [1]}, garder_P=True)
    lec = np.tile(fx.typ == C.LEC, len(regles))
    assert (res.P[lec] == 3).all()
    # une erreur de lecture au palier 3 n'est pas un dégât (interrupteur E1) ; elle l'est sans l'interrupteur
    P = np.where(fx.typ == C.LEC, 3, 1).astype(np.int8)
    avec = RE.compter_temoin(P, fx, 1500, lec_sans_effet=True)
    sans = RE.compter_temoin(P, fx, 1500, lec_sans_effet=False)
    n_lec = (fx.err & (fx.typ == C.LEC) & ~fx.rate & ~fx.dou).sum(axis=0)
    assert (avec.exc == 0).all()
    np.testing.assert_array_equal(sans.exc[:, C.FAIBLE], n_lec)
    assert n_lec.sum() > 100


# --------------------------------------------------------------------------
# Comptabilité
# --------------------------------------------------------------------------
def test_comptabilite_du_moteur_et_exces_apparie():
    ag = E.agent_horizon(C.AGENTS_PAR_NOM["A6b"], 3000)
    fx = RE.flux_e1("court", "service_client", ag, [4], taille_bloc=30)
    regles = E.regles_e1("service_client")
    var = [(r, m) for m in ("base", "retard10") for r in regles]
    res = RE.simuler_e1(fx, ag, var, {"base": [1], "retard10": [2]}, garder_P=True, paquet=37)
    V = len(var)
    for i in range(V):
        sl = res.lignes(i)
        c = RE.compter_temoin(np.ascontiguousarray(res.P[:, sl]), fx, res.tc)
        for att in ("exc", "exc_w", "dmg", "val_nl", "dou_nl", "cor_nl", "val_tot", "comptes", "comptes_w"):
            np.testing.assert_array_equal(getattr(res.cpt, att)[sl], getattr(c, att), err_msg=att)
    tv = RE.compter_temoin(RE.paliers_fixes("tout_valider", fx.typ), fx, res.tc)
    for i in range(V):  # excès = dégâts de la règle − dégâts de « tout faire valider », ligne par ligne
        sl = res.lignes(i)
        np.testing.assert_array_equal(res.cpt.dmg[sl] - tv.dmg, res.cpt.exc[sl])
    assert (tv.exc == 0).all()


def test_hasard_apparie_garde_la_part_du_temps():
    ag = E.agent_horizon(C.AGENTS_PAR_NOM["A1"], 3000)
    fx = RE.flux_e1("court", "bureau", ag, [5], taille_bloc=300)
    r = E.regle_e1("B-régulier", "bureau")
    res = RE.simuler_e1(fx, ag, [(r, "base")], {"base": [3]}, garder_P=True)
    Ph = RE.paliers_hasard(fx.typ, res.cpt.comptes, np.random.default_rng(1))
    for k in (C.ECR, C.MSG, C.DUR, C.EXE):
        m = fx.typ == k
        assert abs((Ph[m] == 3).mean() - (res.P[m] == 3).mean()) < 0.01
        assert abs((Ph[m] == 2).mean() - (res.P[m] == 2).mean()) < 0.01


# --------------------------------------------------------------------------
# Tests de résistance : graine à part, erreur ratée = réussite
# --------------------------------------------------------------------------
def test_graine_a_part_du_controle_imparfait():
    ag = E.agent_horizon(C.AGENTS_PAR_NOM["A3"], 3000)
    fx = RE.flux_e1("court", "bureau", ag, [6], taille_bloc=40)
    fl = F.generer_flux("bureau", 40, 3000, seed=RE.graine_bloc("court", "bureau", 6))
    np.testing.assert_array_equal(fx.typ, fl.type.T)  # le flux ne dépend pas de la graine du contrôle
    np.testing.assert_array_equal(fx.err, F.erreurs(fl, ag).T)
    rng = np.random.default_rng(RE.graine_ratees("court", "bureau", 6))
    np.testing.assert_array_equal(fx.rat10, (rng.random((40, 3000), dtype=np.float32) < 0.10).T)
    assert RE.graine_ratees("court", "bureau", 6) != RE.graine_bloc("court", "bureau", 6)
    assert abs(fx.rat10.mean() - 0.10) < 0.005
    # les lignes « base » ne dépendent pas des modes de résistance lancés dans le même moteur
    regles = E.regles_e1("bureau")
    gm = {m: [9, i] for i, m in enumerate(E.MODES)}
    seul = RE.simuler_e1(fx, ag, [(r, "base") for r in regles], gm, garder_P=True)
    tous = RE.simuler_e1(fx, ag, [(r, m) for m in E.MODES for r in regles], gm, garder_P=True)
    np.testing.assert_array_equal(seul.P, tous.P[:, :len(regles) * fx.R])
    np.testing.assert_array_equal(seul.cpt.exc, tous.cpt.exc[:len(regles) * fx.R])


def test_erreur_ratee_compte_comme_une_reussite():
    """Un seul type (MSG, N = 15 en bureau) : les erreurs ratées font monter le compteur."""
    T = 40
    typ = np.full((T, 1), C.MSG, dtype=np.int8)
    err = np.zeros((T, 1), bool)
    err[[5, 20], 0] = True
    rat = np.zeros((T, 1), bool)
    rat[5, 0] = True  # l'erreur du pas 5 est ratée par le contrôle
    un = np.ones((T, 1), bool)
    zero = np.zeros((T, 1), bool)
    fx = RE.FluxE1("bureau", 1, T, typ, un, zero, err, zero, zero, rat)
    ag = C.AGENTS_PAR_NOM["A2"]
    r = E.regle_e1("B-régulier", "bureau")
    res = RE.simuler_e1(fx, ag, [(r, "base"), (r, "rate10")], {"base": [1], "rate10": [2]}, garder_P=True)
    base, rate = res.P[:, 0], res.P[:, 1]
    assert base[15] == 1 and rate[15] == 3  # 15 réussites d'affilée, l'erreur ratée comprise
    assert rate[20] == 3 and rate[21] == 1  # l'erreur constatée du pas 20 retire l'autonomie
    assert base[21 + 14] == 1 and base[21 + 15] == 3


def test_simulateur_d_etalonnage_fidele_a_la_reference():
    """Le simulateur à un type d'etalonnage_e1 suit RegleUnTypeV2 pas à pas, sur les mêmes tirages."""
    for haut in (False, True):
        pm3 = 0.06 if haut else 0.3
        q = np.array([0.004, 0.01, 0.02] if haut else [0.05, 0.12, 0.2])
        n, T = q.size, 3000
        rng = np.random.default_rng(42)
        tir = [(rng.random(n), rng.random(n), rng.random(n)) for _ in range(T)]
        journal = []
        ET.simuler_un_type(q, pm3, haut, T, 0, tirages=tir, journal=journal)
        a, b, f = ET.constantes(pm3)
        for i in range(n):
            rg = RG.RegleUnTypeV2(0.0, 0.0, a, b, ET.LNB, False, haut)
            qd = min(C.PLAFOND_DIFFICILE, C.FACTEUR_DIFFICILE * q[i])
            vu3 = 0
            for t in range(T):
                uv, ue, up = (x[i] for x in tir[t])
                if rg.epreuve_due():
                    rg.resultat_epreuve(bool(up < (1 - qd) ** C.EPREUVE_VARIANTES))
                assert (rg.palier == 3) == bool(journal[t][i]), (haut, i, t)
                vu3 += rg.palier == 3
                if uv >= C.PART_INVERIFIABLE:
                    rg.erreur() if ue < q[i] else rg.succes()
            assert vu3 > 0


# --------------------------------------------------------------------------
# Verdicts et intervalles
# --------------------------------------------------------------------------
def test_verdicts_et_intervalles():
    assert X.verdict(0.0, 0.004, 0.005) == "passe"
    assert X.verdict(0.006, 0.01, 0.005) == "échoue"
    assert X.verdict(0.004, 0.006, 0.005) == "indécis"
    rng = np.random.default_rng(0)
    x = (rng.random((4000, 1)) < 0.002).astype(float)  # événement rare
    W = X.poids_bootstrap(4000, [1])
    I = X.intervalles(x, W)
    assert I["lo"][0] <= min(I["lo_n"][0], I["lo_b"][0]) and I["hi"][0] >= max(I["hi_n"][0], I["hi_b"][0])
    z = X.intervalles(np.zeros((500, 2)), X.poids_bootstrap(500, [2]))
    assert (z["hi"] == 0).all() and X.verdict(z["lo"][0], z["hi"][0], 0.005) == "passe"


# --------------------------------------------------------------------------
# Amendement E1-a : au plus une erreur constatée avant le retrait (décision 5)
# --------------------------------------------------------------------------
def compter_episodes(P, fx, tc, mode, rep, k):
    """Recompte, à partir des paliers, les épisodes au palier 3 après tc pour un type d'une répétition."""
    ts = [t for t in range(tc, fx.T) if fx.typ[t, rep] == k]
    n, mx, cst, inv, rat, cur, dedans = 0, 0, 0, 0, 0, 0, False
    for t in ts:
        if P[t] == 3:
            if not dedans:
                n, cur, dedans = n + 1, 0, True
            if fx.err[t, rep] and not fx.dou[t, rep]:
                vu = not (mode == "rate10" and fx.rat10[t, rep]) and not (mode == "difficiles" and fx.dif[t, rep])
                if not fx.ver[t, rep]:
                    inv += 1
                elif vu:
                    cur += 1
                    cst += 1
                    mx = max(mx, cur)
                else:
                    rat += 1
        else:
            dedans = False
    return n, mx, cst, inv, rat


@pytest.mark.parametrize("nom", ["A6b", "A6a", "bordD_moyen_3barre", "bordD_faible_pireBreg"])
def test_compteurs_de_derive_du_moteur(nom):
    mix = "bureau"
    ag = C.AGENTS_PAR_NOM.get(nom) or next(a for a in E.agents_bord(mix) if a.nom == nom)
    ag = E.agent_horizon(ag, 3000)
    fx = RE.flux_e1("court", mix, ag, [8], taille_bloc=3)
    var = [(r, m) for m in E.MODES for r in regles_test(mix)]
    res = RE.simuler_e1(fx, ag, var, {m: [6, i] for i, m in enumerate(E.MODES)}, garder_P=True)
    vus = 0
    for i, (r, m) in enumerate(var):
        for rep in range(fx.R):
            li = i * fx.R + rep
            for k in (C.ECR, C.DUR, C.EXE, C.MSG, C.SOR, C.ARG):
                n, mx, cst, inv, rat = compter_episodes(res.P[:, li], fx, res.tc, m, rep, k)
                assert (res.n_stints[li, k], res.max_cst[li, k], res.tot_cst[li, k], res.tot_inv[li, k],
                        res.tot_rat[li, k]) == (n, mx, cst, inv, rat), (nom, r.nom, m, rep, C.TYPES[k])
                vus += n
                if m == "base" and C.ENJEU_HAUT[k]:
                    assert mx <= 1  # pièce 7 : retrait à la première erreur constatée, pour A comme pour B
    assert vus > 0


def test_decision_5_erreur_invérifiable_et_constat_differe():
    """Un type DUR au palier 3 au moment d'une dérive (B-tout réduit à N = 3)."""
    T, tc = 40, 20
    typ = np.full((T, 1), C.DUR, dtype=np.int8)
    ver = np.ones((T, 1), bool)
    err = np.zeros((T, 1), bool)
    err[[21, 22, 23], 0] = True
    ver[21, 0] = False  # erreur sur une action invérifiable : passe sans déclencher le retrait
    z = np.zeros((T, 1), bool)
    fx = RE.FluxE1("bureau", 1, T, typ, ver, z, err, z, z, z)
    ag = dataclasses.replace(C.AGENTS_PAR_NOM["A6b"], t_change=tc)
    r = E.regle_e1("B-tout", "bureau")
    r = E.RegleE1("B-3", "B", r.params, np.where(r.N > 0, 3, 0))
    res = RE.simuler_e1(fx, ag, [(r, "base"), (r, "retard10")], {"base": [1], "retard10": [2]}, tc=tc,
                        garder_P=True)
    assert res.P[20, 0] == 3 and res.P[22, 0] == 3 and res.P[23, 0] == 1
    assert (res.max_cst[0, C.DUR], res.tot_inv[0, C.DUR], res.n_stints[0, C.DUR]) == (1, 1, 1)
    # constat 10 actions plus tard : les erreurs des pas 22 et 23 passent toutes deux avant le retrait
    assert res.max_cst[1, C.DUR] == 2 and res.tot_inv[1, C.DUR] == 1


def ligne_budget(regle, horizon, fenetre, verdict, hi=0.001):
    return dict(regle=regle, mode="base", epreuves="à blanc", horizon=horizon, fenetre=fenetre, niveau="moyen",
                agent="bordD_moyen_3barre", melange="bureau", exces=hi / 2, exces_hi=hi, budget=0.05, verdict=verdict,
                verdict_final=verdict, relance=False)


def test_regle_de_choix_amendement_E1a():
    import ecrire_resultats_e1 as W
    budget, charges, derive = [], [], []
    for i, r in enumerate(E.NOMS_REGLES):
        for h in ("court", "long"):
            budget.append(ligne_budget(r, h, "tout", "passe"))
            budget.append(ligne_budget(r, h, "apres", "passe"))
        charges.append(dict(regle=r, horizon="court", delegable=True, charge_hors_lec=50.0 + 5 * i))
        charges.append(dict(regle=r, horizon="long", delegable=True, charge_hors_lec=50.0 + 5 * i))
    # A½ (la moins chère) échoue seulement dans la fenêtre courte : éliminée avant l'amendement, plus après
    budget[1]["verdict_final"] = budget[1]["verdict"] = "échoue"
    budget[1]["exces_hi"] = 0.08
    am, anc = W.choisir(budget, charges, derive), W.choisir(budget, charges, derive, lecture="ancienne")
    assert am["retenue"] == "A½" and anc["retenue"] == "A¼"
    # l'échec de la fenêtre longue élimine toujours
    budget[3]["verdict_final"] = "échoue"
    assert W.choisir(budget, charges, derive)["retenue"] == "A¼"
    budget[3]["verdict_final"] = "passe"
    # plus d'une erreur constatée dans un épisode de dérive, à enjeu moyen : éliminatoire
    derive.append(dict(regle="A½", mode="base", critere=True, verdict="échoue", max_constatees=2))
    derive.append(dict(regle="A¼", mode="base", critere=False, verdict="", max_constatees=3))  # enjeu faible
    assert W.choisir(budget, charges, derive)["retenue"] == "A¼"
    assert W.choisir(budget, charges, derive, lecture="ancienne")["retenue"] == "A¼"


# --------------------------------------------------------------------------
# Correctif E1-b (après la grille) : figure 1 et mesure 3 suivent la lecture E1-a
# --------------------------------------------------------------------------
def test_figure_1_suit_les_cellules_eliminatoires():
    import ecrire_resultats_e1 as W
    budget = [ligne_budget("B-régulier", "court", "tout", "passe", hi=0.02),
              ligne_budget("B-régulier", "long", "apres", "passe", hi=0.0475),
              ligne_budget("B-régulier", "court", "apres", "échoue", hi=0.083)]  # fenêtre courte : mesurée seulement
    assert W.pire_rapport(budget, "B-régulier") == pytest.approx(0.95)
    assert W.pire_rapport(budget, "B-régulier", "ancienne") == pytest.approx(1.66)
    assert W.pire_rapport(budget, "B-tout") is None


def test_mesure_3_ne_compte_plus_la_fenetre_courte():
    import ecrire_resultats_e1 as W
    budget, charges, comparaisons = [], [], []
    for r, ch in (("B-régulier", 60.0), ("liste_fixe", 80.0), ("tri_risque", 75.0), ("oracle_p2", 40.0)):
        budget.append(ligne_budget(r, "court", "tout", "passe"))
        charges.append(dict(regle=r, horizon="court", melange="bureau", agent="bordD_moyen_3barre",
                            delegable=True, charge_hors_lec=ch, charge_hors_lec_avec_ep=ch + 2))
    for t in ("liste_fixe", "tri_risque"):
        for mes in ("charge_hors_lec", "charge_hors_lec_avec_ep"):
            comparaisons.append(dict(horizon="court", melange="bureau", agent="bordD_moyen_3barre", regle="B-régulier",
                                     contre=t, mesure=mes, hi=-5.0))
    budget.append(ligne_budget("B-régulier", "court", "apres", "échoue", hi=0.083))  # fenêtre courte hors budget
    ap = W.reussites(budget, charges, comparaisons)[("B-régulier", "court")]
    av = W.reussites(budget, charges, comparaisons, "ancienne")[("B-régulier", "court")]
    assert (ap["couples"], ap["ok"], ap["ok_ep"]) == (1, 1, 1)
    assert (av["ok"], av["ok_ep"]) == (0, 0)  # le rapport d'origine la comptait comme hors budget
    assert ap["parts"] == [pytest.approx(40 / 60)]
    # une cellule éliminatoire hors budget empêche toujours la réussite
    budget.append(ligne_budget("B-régulier", "court", "tout", "échoue", hi=0.08))
    assert W.reussites(budget, charges, comparaisons)[("B-régulier", "court")]["ok"] == 0
    # un témoin hors budget dans la seule fenêtre courte n'est plus « battu » d'office
    budget = budget[:-1]
    budget.append(ligne_budget("liste_fixe", "court", "apres", "échoue", hi=0.2))
    comparaisons[0]["hi"] = 1.0  # la règle ne bat pas la liste fixe en charge
    assert W.reussites(budget, charges, comparaisons)[("B-régulier", "court")]["ok"] == 0
    assert W.reussites(budget, charges, comparaisons, "ancienne")[("B-régulier", "court")]["ok"] == 0
