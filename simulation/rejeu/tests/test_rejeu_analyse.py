"""Rejeu, phase 2 : lots de colonnes, valeurs par répétition, écarts types par grappe, jackknife à nombres aléatoires
communs, tirage commun des tâches (PLAN_EXPERIENCE.md, 5.5 et 5.13).
"""
import numpy as np
import pytest

from rejeu import analyse as AN
from rejeu import config_rejeu as CR
from rejeu import epreuves as EP
from rejeu import essais as ES
from rejeu import intervalles as IC
from rejeu import lots as LO
from rejeu import rejeu as RJ
from rejeu import suites as SU
from rejeu import types_regle as TY


def jeu(env="commerce", modele="claude-haiku-5-5"):
    e, prep = ES.entrees_pilote(), ES.preparees_pilote()
    return SU.jeu_configuration(prep, e, env, modele, ES.taches_pilote(env), "developpement")


def rejouer(lot, env="commerce", grappes=True):
    j = lot.jeu
    pool = EP.PoolEpreuves(j)
    f = EP.FournisseurParties(pool, lot.suite.cles_epreuves)
    return AN.rejouer_lot(lot, ES.regles_test(env), (0.05, 0.0), f, grappes=grappes)


def test_jackknife_retire_une_tache_des_memes_ordres():
    base = LO.lot_r0(jeu(), 4, 3)
    jl = LO.lot_jackknife(base)
    s, sj = base.suite, jl.suite
    assert jl.n_groupes == base.G and sj.R == base.G * s.R
    for c in range(sj.R):
        g, k = int(jl.groupe[c]), c % s.R
        garde = (s.grappe[:, k] != g) & (s.typ[:, k] >= 0)
        n = int(garde.sum())
        for nom in ("typ", "u_val", "u_hasard", "u_res", "errp", "den", "partie"):
            np.testing.assert_array_equal(getattr(sj, nom)[:n, c], getattr(s, nom)[garde, k])
        assert (sj.typ[n:, c] == TY.VIDE).all()
        assert sj.cles_epreuves[c] == s.cles_epreuves[k]
        assert sj.n_den[c] == s.n_den[k] - base.par_grappe["den"][0, g]
        assert sj.n_doutes[c] == s.n_doutes[k] - base.par_grappe["dou"][0, g]


def test_r0_de_la_phase_2_egale_la_phase_1():
    e, prep, cfg = ES.entrees_pilote(), ES.preparees_pilote(), ES.config()
    t = ES.taches_pilote("commerce")
    rs = RJ.rejouer_configuration(prep, e, cfg, "commerce", "claude-haiku-5-5", t, R=30, jeu="developpement",
                                  taches_calibration=t, G0=4)
    j = SU.jeu_configuration(prep, e, "commerce", "claude-haiku-5-5", t, "developpement")
    lot = LO.lot_r0(j, 4, 30)
    np.testing.assert_array_equal(lot.suite.typ, rs.suite.typ)
    f = EP.FournisseurParties(EP.PoolEpreuves(j), lot.suite.cles_epreuves)
    rl = AN.rejouer_lot(lot, rs.moteur.regles, cfg.valeurs_e, f, (rs.classes_calibration, None),
                        (rs.classes_retro, None))
    assert rl.noms == rs.noms
    for nom in rl.noms:
        v = AN.valeurs_groupes(rl, nom)
        pr = rs.mesures["par_repetition"][nom]
        np.testing.assert_allclose(v["budget"][:, :, 0], np.nanmean(pr["exces_100_ecritures"], axis=1))
        np.testing.assert_allclose(v["charge"][:, 0], np.nanmean(pr["charge_hors_lec"], axis=1))


def test_ecart_type_par_grappe_egal_au_calcul_direct():
    j = jeu("banque")
    lot = LO.lot_bootstrap(j, 5, [0, 1, 2, 3], 3)
    rl = rejouer(lot, "banque")
    s = lot.suite
    num = AN.numerateurs_grappes(rl, "tout_approuver")
    # calcul direct : tout approuver exécute tout au palier 3 ; dégât en plus si erreur avec dégât et u_val ≥ e
    niv = TY.ENJEU[np.where(s.typ >= 0, s.typ, 0)]
    for gi in range(lot.n_groupes):
        cols = np.nonzero(lot.groupe == gi)[0]
        for jn in range(3):
            a = np.zeros(lot.G)
            for c in cols:
                m = (s.typ[:, c] >= 0) & s.errd[:, c] & ~s.apart[:, c] & (niv[:, c] == jn) & (s.u_val[:, c] >= 0.05)
                np.add.at(a, s.grappe[m, c], 1.0)
            a /= cols.size
            np.testing.assert_allclose(num["budget"][0, gi, jn], a)
            se = 100 * IC.se_rapport(a, lot.par_grappe["den"][gi], lot.strate_grappe)
            assert AN.se_budget(num["budget"], num["den"], lot.strate_grappe)[0, jn, gi] == pytest.approx(se)
            v = AN.valeurs_groupes(rl, "tout_approuver")["budget"][0, jn, gi]
            assert v == pytest.approx(100 * a.sum() / lot.par_grappe["den"][gi].sum())
    # les dénominateurs par grappe redonnent ceux des colonnes
    for c in range(s.R):
        assert lot.par_grappe["den"][lot.groupe[c]].sum() == s.n_den[c]
        assert (lot.par_grappe["ecr"][lot.groupe[c]] + lot.par_grappe["dou"][lot.groupe[c]]).sum() == \
            s.n_ecritures[c] + s.n_doutes[c]


def test_charge_par_grappe_et_difference():
    j = jeu("commerce")
    lot = LO.lot_bootstrap(j, 6, [0, 1], 4)
    rl = rejouer(lot)
    for nom in ("B-tout-petit", "tout_valider"):
        num = AN.numerateurs_grappes(rl, nom)
        v = AN.valeurs_groupes(rl, nom)["charge"][0]
        np.testing.assert_allclose(v, 100 * num["charge"][0].sum(axis=1) / num["hors_lec"].sum(axis=1))


def test_tirage_commun_aux_modeles():
    ja, jb = jeu("WorkBench", "claude-haiku-5-5"), jeu("WorkBench", "claude-sonnet-5-5")
    assert ja.strates == jb.strates
    for b in range(5):
        la, lb = LO.lot_bootstrap(ja, 8, [b], 1), LO.lot_bootstrap(jb, 8, [b], 1)
        occ = lambda lot: {(int(g), lot.jeu.parties[int(p)].partie.tache)  # noqa: E731
                           for g, p in zip(lot.suite.grappe[:, 0], lot.suite.partie[:, 0]) if g >= 0}
        oa, ob = occ(la), occ(lb)
        ta = {g: t for g, t in oa}
        assert all(ta.get(g, t) == t for g, t in ob)   # une occurrence désigne la même tâche pour les deux modèles


def test_hasard_par_groupe_garde_la_part_du_groupe():
    s = ES.suite_synthetique(41, T=300, R=40, p_err=0.03, vide=False)
    s.meta.update(G0=5, environnement="banque", modele="claude-haiku-5-5", jeu="developpement", couche="R0",
                  scenario=0, repetitions=list(range(s.R)), ordres=[0] * s.R)
    from rejeu import moteur as MO
    r = [x for x in ES.regles_test("banque") if x.nom == "B-régulier-petit"]
    m = MO.simuler(s, r, ES.FournisseurAleatoire(1), garder_P=True)
    groupe = np.repeat(np.arange(4), 10)
    u = np.random.default_rng(3).random((s.T, s.R))
    Ph = AN.paliers_hasard_groupes(s, m.cpt.comptes, groupe, 4, u)
    for g in range(4):
        cols = groupe == g
        for k in (TY.ECR, TY.DUR):
            mk = (s.typ[:, cols] == k) & ~s.plaf[:, cols]
            assert abs((Ph[:, cols][mk] == 3).mean() - (m.P[:, cols][mk] == 3).mean()) < 0.06
