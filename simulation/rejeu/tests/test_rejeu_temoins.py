"""Rejeu, phase 1 : règles témoins (PLAN_EXPERIENCE.md, 5.7), classes provisoires de l'oracle (5.12, point 4) et
mesures de base par cellule (5.12, sans intervalles).
"""
import numpy as np
import pytest

from rejeu import classes as CL
from rejeu import config_rejeu as CR
from rejeu import entrees as EN
from rejeu import essais as ES
from rejeu import mesures as ME
from rejeu import moteur as MO
from rejeu import rejeu as RJ
from rejeu import suites as SU
from rejeu import temoins as TM
from rejeu import types_regle as TY


# --------------------------------------------------------------------------
# Témoins
# --------------------------------------------------------------------------
def test_temoins_fixes_types_generalises():
    s = ES.suite_synthetique(21, T=300, R=4)
    actif, plaf = s.typ >= 0, s.plaf
    lf, tr = TM.paliers_fixes("liste_fixe", s), TM.paliers_fixes("tri_risque", s)
    assert ((lf == 3) == (actif & (s.typ == TY.ECR) & ~plaf)).all()
    assert ((tr == 3) == (actif & np.isin(s.typ, (TY.ECR, TY.MSG)) & ~plaf)).all()
    assert ((lf == 1) == (actif & ~((s.typ == TY.ECR) & ~plaf))).all()
    tv, ta = TM.paliers_fixes("tout_valider", s), TM.paliers_fixes("tout_approuver", s)
    assert ((tv == 1) == actif).all() and ((ta == 3) == actif).all()   # tout approuver : plafonnées comprises
    for P in (lf, tr, tv, ta):
        assert (P[~actif] == 0).all()


def trois_reussites_simple(s, c):
    serie, pal, out = {}, {}, []
    for t in range(s.T):
        k = int(s.typ[t, c])
        if k < 0:
            out.append(0)
            continue
        out.append(1 if s.plaf[t, c] else pal.get(k, 1))
        if s.ver[t, c] and s.reu[t, c] and not s.plaf[t, c]:
            serie[k] = serie.get(k, 0) + 1
            if serie[k] >= 3:
                pal[k] = 3
        elif s.errp[t, c]:
            serie[k], pal[k] = 0, 1
    return np.array(out)


def test_trois_reussites():
    s = SU.suite_depuis_tableaux([TY.DUR] * 8, errp=[0, 0, 0, 0, 1, 0, 0, 0], plaf=[0, 0, 0, 0, 0, 1, 0, 0])
    assert TM.paliers_trois_reussites(s)[:, 0].tolist() == [1, 1, 1, 3, 3, 1, 1, 1]
    for g in (31, 32):
        s = ES.suite_synthetique(g, T=300, R=3)
        P = TM.paliers_trois_reussites(s)
        for c in range(s.R):
            np.testing.assert_array_equal(P[:, c], trois_reussites_simple(s, c))


def test_hasard_apparie_garde_la_part_de_la_regle():
    s = ES.suite_synthetique(41, T=300, R=300, p_err=0.03, vide=False)
    s.meta.update(G0=5, environnement="banque", modele="claude-haiku-5-5", jeu="developpement", couche="R0",
                  scenario=0, repetitions=list(range(s.R)), ordres=[0] * s.R)
    r = [x for x in ES.regles_test("banque") if x.nom == "B-régulier-petit"][0]
    m = MO.simuler(s, [r], ES.FournisseurAleatoire(1), garder_P=True)
    f3, f23 = TM.parts_regle(m.cpt.comptes)
    u = TM.tirages_hasard(s)
    assert (u == TM.tirages_hasard(s)).all()   # mêmes tirages pour toutes les règles
    Ph = TM.paliers_hasard(s, f3, f23, u)
    for k in (TY.ECR, TY.DUR, TY.MSG, TY.EXE):
        m_k = (s.typ == k) & ~s.plaf
        assert abs((Ph[m_k] == 3).mean() - (m.P[m_k] == 3).mean()) < 0.01
        assert abs((Ph[m_k] >= 2).mean() - (m.P[m_k] >= 2).mean()) < 0.01
    assert (Ph[s.plaf] == 1).all()


# --------------------------------------------------------------------------
# Classes provisoires (Clopper-Pearson simple) et oracle
# --------------------------------------------------------------------------
def test_classes_provisoires_clopper_pearson():
    lo, hi = CL.bornes_cp(0, 100)
    assert lo == 0.0 and hi == pytest.approx(1 - 0.05 ** (1 / 100))   # zéro erreur : 1 − 0,05^(1/n) (5.13)
    assert CL.classer(0, 100, 0.03)["classe"] == CL.SOUS
    assert CL.classer(0, 100, 0.02)["classe"] == CL.INDETERMINE
    assert CL.classer(10, 20, 0.1)["classe"] == CL.AU_DESSUS
    assert CL.classer(0, 0, 0.1)["classe"] == CL.SANS_DONNEE
    lo, hi = CL.bornes_cp(3, 40)
    assert lo < 3 / 40 < hi
    # volume de certification (annexe A2) : à zéro erreur, n = certification -> « sous la barre » (M8)
    b = ES.config().barres[("aviation", "faible")]
    n = CR.certification(b)
    assert CL.classer(0, n, float(b))["classe"] == CL.SOUS and CL.classer(0, n - 1, float(b))["classe"] != CL.SOUS


def test_oracle_avec_palier_2():
    s = ES.suite_synthetique(51, T=200, R=2)
    classes = {TY.ECR: {"classe": CL.INDETERMINE}, TY.DUR: {"classe": CL.SOUS}, TY.EXE: {"classe": CL.AU_DESSUS},
               TY.MSG: {"classe": CL.SOUS}}
    P = TM.paliers_oracle(s, classes)
    attendu = {TY.ECR: 2, TY.DUR: 3, TY.EXE: 2, TY.MSG: 3, TY.SOR: 1, TY.ARG: 1, TY.GAR: 1, TY.ILL: 1}
    for k, p in attendu.items():
        m = (s.typ == k) & ~s.plaf
        assert (P[m] == p).all(), TY.SIGLES[k]   # SOR, ARG, GAR, ILL sans donnée : au-dessus, irréversibles


def test_oracle_calibre_et_retrospectif_sur_un_partage_du_pilote():
    e, prep, cfg = ES.entrees_pilote(), ES.preparees_pilote(), ES.config()
    taches = ES.taches_pilote("commerce")
    part = EN.partage_factice({"commerce": taches}, "cd" * 32)
    cal, conf = part["calibration"]["commerce"], part["confirmation"]["commerce"]
    assert len(cal) == 5 and len(conf) == 5
    rs = RJ.rejouer_configuration(prep, e, cfg, "commerce", "claude-haiku-5-5", conf, R=20, jeu="confirmation",
                                  taches_calibration=cal, garder_P=True)
    jcal = SU.jeu_configuration(prep, e, "commerce", "claude-haiku-5-5", cal, "calibration")
    jconf = SU.jeu_configuration(prep, e, "commerce", "claude-haiku-5-5", conf, "confirmation")
    resume = lambda cl: {k: (v["n"], v["x"], v["classe"]) for k, v in cl.items()}  # noqa: E731 (p vaut nan si n = 0)
    assert resume(rs.classes_calibration) == resume(CL.classes_jeu(jcal, cfg))
    assert resume(rs.classes_retro) == resume(CL.classes_jeu(jconf, cfg))
    np.testing.assert_array_equal(rs.P_temoins["oracle_p2"], TM.paliers_oracle(rs.suite, rs.classes_calibration))
    np.testing.assert_array_equal(rs.P_temoins["oracle_retro"], TM.paliers_oracle(rs.suite, rs.classes_retro))
    # avec quelques écritures et une barre faible de 1/38, aucun type n'est « sous la barre » : l'oracle valide
    assert all(c["classe"] != CL.SOUS for c in rs.classes_calibration.values())


# --------------------------------------------------------------------------
# Mesures de base par cellule
# --------------------------------------------------------------------------
def test_mesures_sur_une_suite_faite_a_la_main():
    # ECR juste ; ECR erreur ; DUR juste ; ARG refusée ; ARG plafonnée juste ; ILL inconnu (invérifiable)
    typ = [TY.ECR, TY.ECR, TY.DUR, TY.ARG, TY.ARG, TY.ILL]
    s = SU.suite_depuis_tableaux(typ, ver=[1, 1, 1, 1, 1, 0], reu=[1, 0, 1, 0, 1, 0], errp=[0, 1, 0, 1, 0, 0],
                                 errd=[0, 1, 0, 0, 0, 0], den=[1, 1, 1, 0, 1, 0], apart=[0, 0, 0, 0, 0, 1],
                                 plaf=[0, 0, 0, 0, 1, 0], u_val=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5], n_doutes=[2],
                                 n_lectures=[10], n_preparations=[1])
    assert (s.n_den[0], s.n_ecritures[0], s.n_actions[0]) == (4, 6, 19)
    cpt = MO.compter_paliers(np.concatenate([TM.paliers_fixes("tout_approuver", s),
                                             TM.paliers_fixes("tout_valider", s)], axis=1), s, (0.05,))
    ta = ME.lignes_groupe("tout_approuver", "témoin", cpt.lignes(slice(0, 1)), s, (0.05,), "banque")
    tv = ME.lignes_groupe("tout_valider", "témoin", cpt.lignes(slice(1, 2)), s, (0.05,), "banque")
    d = {x["niveau"]: x for x in ta["degats"]}
    assert d["faible"]["exces_100_ecritures"] == pytest.approx(100 / 4)    # 1 erreur ECR ÷ 4 écritures
    assert d["faible"]["exces_100_actions"] == pytest.approx(100 / 19)     # secondaire : lectures comprises
    assert d["fort"]["exces_100_ecritures"] == 0                           # la refusée ne fait aucun dégât
    c_ta, c_tv = ta["charges"][0], tv["charges"][0]
    assert c_ta["charge_hors_lec"] == pytest.approx(100 * 2 / 8)   # seulement les 2 doutes, ÷ (6 écritures + 2 doutes)
    assert c_tv["charge_hors_lec"] == pytest.approx(100.0)         # 6 validations + 2 doutes
    assert c_tv["charge_100_ecritures"] == pytest.approx(100 * 8 / 4)
    assert c_ta["inverifiables_seules"] == 1 and c_tv["inverifiables_seules"] == 0
    assert all(x["exces_100_ecritures"] == 0 for x in tv["degats"])
    # palier 2 : l'erreur ECR est corrigée (charge) si u_val ≥ e ; dégât sinon
    P2 = np.where(s.typ == TY.ECR, 2, 1).astype(np.int8)
    for u, cor, dmg in ((0.5, 1, 0), (0.01, 0, 1)):
        s.u_val[1, 0] = u
        c = MO.compter_paliers(P2, s, (0.05,))
        assert (c.cor[0, 0], c.dmg[0, 0, 0], c.exc[0, 0, 0]) == (cor, dmg, 0)


def test_rejeu_d_une_configuration_toutes_les_cellules():
    e, prep, cfg = ES.entrees_pilote(), ES.preparees_pilote(), ES.config()
    taches = ES.taches_pilote("commerce")
    rs = RJ.rejouer_configuration(prep, e, cfg, "commerce", "claude-haiku-5-5", taches, R=30, jeu="developpement",
                                  taches_calibration=taches)
    noms = ["B-tout", "B-régulier", "A½", "A¼", "tout_valider", "tout_approuver", "liste_fixe", "tri_risque",
            "trois_reussites", "hasard_B-tout", "hasard_B-régulier", "hasard_A½", "hasard_A¼", "oracle_p2",
            "oracle_retro"]
    assert rs.noms == noms
    assert len(rs.mesures["degats"]) == len(noms) * 4 * 3 and len(rs.mesures["charges"]) == len(noms) * 4
    ch = {(x["regle"], x["e"]): x for x in rs.mesures["charges"]}
    assert ch[("tout_valider", 0.05)]["charge_hors_lec"] == pytest.approx(100.0)
    # B-tout n'atteint aucun palier 3 sur ce volume (N = 39 à enjeu faible) : même charge que « tout faire valider »
    assert ch[("B-tout", 0.05)]["charge_hors_lec"] == pytest.approx(100.0)
    assert ch[("B-tout", 0.05)]["ouvertes"] > 0   # l'erreur forte ouvre une épreuve
    dg = {(x["regle"], x["e"], x["niveau"]): x for x in rs.mesures["degats"]}
    assert dg[("tout_approuver", 0.05, "fort")]["exces_100_ecritures"] > 0
    assert dg[("B-tout", 0.05, "fort")]["exces_100_ecritures"] == 0
    assert set(rs.mesures["par_repetition"]) == set(noms)
