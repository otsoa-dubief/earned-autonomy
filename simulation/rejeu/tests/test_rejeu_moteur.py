"""Rejeu, phase 1 : tests du moteur avant le gel (PLAN_EXPERIENCE.md, 5.16), points 1, 2, 3, 4 et 7.

1. Non-régression d'E1 : les tests d'E1 restent verts (tests/test_e1.py) ; en plus, le moteur du rejeu, réglé comme
   E1, refait `regle_e1.simuler_e1` palier par palier sur des flux d'E1 (sans doutes ; LEC et PLA retirés), avec les
   issues d'épreuve du journal d'E1, et la même comptabilité des dégâts en plus.
2. Équivalence : moteur vectorisé et références par type donnent le même palier, écriture par écriture, sur des suites
   du pilote et des suites synthétiques, épreuves comprises (journal, comme `rejouer_reference_e1`).
3. Suites piège avec les N réels (E1, mesure 8 ; `executer_e1.suite_piege`).
4. Erreurs plantées.
7. Déterminisme : mêmes graines, mêmes sorties, vérifiées par empreinte.
"""
import numpy as np
import pytest

import config as C
import config_e1 as E
import executer_e1 as X
import regle_e1 as RE
from rejeu import config_rejeu as CR
from rejeu import entrees as EN
from rejeu import epreuves as EP
from rejeu import essais as ES
from rejeu import moteur as MO
from rejeu import preuves as PR
from rejeu import regles as RG
from rejeu import rejeu as RJ
from rejeu import suites as SU
from rejeu import temoins as TM
from rejeu import types_regle as TY

ENVS = CR.ENVIRONNEMENTS


# --------------------------------------------------------------------------
# Point 1 : non-régression d'E1
# --------------------------------------------------------------------------
def regles_test_e1(mix):
    regles = E.regles_e1(mix)
    petits = [E.RegleE1(r.nom + "-petit", "B", r.params, np.where(r.N > 0, np.maximum(2, r.N // 40), 0))
              for r in regles if r.famille == "B"]
    return regles + petits + [E.RegleE1("A-rapide", "A", C.params_regle("souple", 0.20), np.zeros(8, np.int64))]


@pytest.mark.parametrize("mix", ["bureau", "service_client"])
@pytest.mark.parametrize("nom", ["A2", "A3", "A4", "bord_moyen_3barre", "bord_fort_3barre", "bord_faible_pireBreg"])
def test_point_1_moteur_du_rejeu_refait_simuler_e1(nom, mix):
    ag = C.AGENTS_PAR_NOM.get(nom) or next(a for a in E.agents_bord(mix) if a.nom == nom)
    ag = E.agent_horizon(ag, 3000)
    fx = RE.flux_e1("court", mix, ag, [7], taille_bloc=3)
    assert not fx.dou.any()
    regles_e1 = regles_test_e1(mix)
    res = RE.simuler_e1(fx, ag, [(r, "base") for r in regles_e1], {"base": [5, 0]}, journal=True, garder_P=True)
    R = fx.R
    garde = (fx.typ != C.LEC) & (fx.typ != C.PLA)   # LEC autonome et PLA au palier 1 : sans effet sur les autres
    Tm = int(garde.sum(axis=0).max())
    typ = np.full((Tm, R), TY.VIDE, np.int8)
    ver, err, uv = np.zeros((Tm, R), bool), np.zeros((Tm, R), bool), np.ones((Tm, R))
    tmap, pas = {}, []
    for r in range(R):
        ts = np.nonzero(garde[:, r])[0]
        pas.append(ts)
        n = len(ts)
        typ[:n, r], ver[:n, r], err[:n, r] = fx.typ[ts, r], fx.ver[ts, r], fx.err[ts, r]
        uv[:n, r] = np.where(fx.rate[ts, r], 0.0, 1.0)   # u_val < 0,05 exactement là où E1 tirait « raté »
        tmap.update({(r, t): j for j, t in enumerate(ts.tolist())})
    suite = SU.suite_depuis_tableaux(typ, ver=ver, reu=ver & ~err, errp=ver & err, errd=err, u_val=uv)
    issues = {(li, tmap[(li % R, t)], k): (EP.REUSSIE if ok else EP.RATEE) for (li, t, k, ok) in res.journal_epreuves}
    regles = [RG.depuis_regle_e1(r) for r in regles_e1]
    m = MO.simuler(suite, regles, EP.FournisseurImpose(issues), valeurs_e=(0.05,), garder_P=True)
    for i in range(len(regles)):
        for r in range(R):
            li = i * R + r
            n = len(pas[r])
            np.testing.assert_array_equal(m.P[:n, li], res.P[pas[r], li], err_msg=f"{nom} {regles[i].nom} {r}")
    # même comptabilité : dégâts en plus par niveau et corrections au palier 2 (ni LEC ni PLA n'en font, en E1)
    np.testing.assert_array_equal(m.cpt.exc[0], res.cpt.exc)
    np.testing.assert_array_equal(m.cpt.cor[0], res.cpt.cor_nl)
    if nom in ("A2", "A3", "A4"):   # agents à erreurs fréquentes : des épreuves sont rejouées
        assert len(res.journal_epreuves) > 0


# --------------------------------------------------------------------------
# Point 2 : équivalence avec les références par type
# --------------------------------------------------------------------------
def comparer_aux_references(suite, m):
    for i, r in enumerate(m.regles):
        for c in range(suite.R):
            li = i * suite.R + c
            ref = RG.rejouer_reference(suite, r, c, m.issues_ligne(li))
            np.testing.assert_array_equal(ref, m.P[:, li], err_msg=f"{r.nom} colonne {c}")


@pytest.mark.parametrize("env", ENVS)
def test_point_2_equivalence_sur_les_suites_du_pilote(env):
    e, prep, cfg = ES.entrees_pilote(), ES.preparees_pilote(), ES.config()
    essais = 0
    for mod in CR.MODELES:
        cf = RJ.preparer_configuration(prep, e, cfg, env, mod, ES.taches_pilote(env), jeu="developpement",
                                       regles=ES.regles_test(env, cfg))
        for suite in (SU.suite_r0(cf.jeu, cf.G0, 25), SU.suite_bootstrap(cf.jeu, cf.G0, 3, K=8)):
            m = MO.simuler(suite, cf.regles, EP.FournisseurParties(cf.pool, suite.cles_epreuves), journal=True,
                           garder_P=True)
            comparer_aux_references(suite, m)
            essais += len(m.journal)
    if env in ("aviation", "commerce"):   # les erreurs fortes du pilote ouvrent des épreuves
        assert essais > 0


@pytest.mark.parametrize("graine", [1, 2, 3, 4])
def test_point_2_equivalence_sur_des_suites_synthetiques(graine):
    env = ENVS[graine % 4]
    suite = ES.suite_synthetique(graine, T=400, R=5)
    regles = ES.regles_test(env)
    m = MO.simuler(suite, regles, ES.FournisseurAleatoire(graine), journal=True, garder_P=True, paquet=37)
    comparer_aux_references(suite, m)
    statuts = {st for (_l, _t, _k, st, _v, _c) in m.journal}
    assert statuts == {EP.REUSSIE, EP.RATEE, EP.IMPOSSIBLE}
    assert (m.n_prom3.sum(axis=1) > 0).any() and (m.P == 2).any()   # paliers 3 et 2 atteints
    # comptabilité du moteur = comptabilité des mêmes paliers recalculée à part
    c = MO.compter_paliers(m.P, suite)
    for a in ("exc", "dmg", "cor", "exc_part", "val", "inv3", "comptes"):
        np.testing.assert_array_equal(getattr(m.cpt, a), getattr(c, a), err_msg=a)


# --------------------------------------------------------------------------
# Point 3 : suites piège avec les N réels
# --------------------------------------------------------------------------
@pytest.mark.parametrize("env", ENVS)
def test_point_3_suites_piege_references(env):
    cfg, rng = ES.config(), np.random.default_rng(0)
    d = float(CR.D_CONSTAT)
    for nom in ("B-tout", "B-régulier"):
        r = RG.regle(nom, env, cfg)
        for k in (TY.ECR, TY.MSG, TY.DUR, TY.EXE, TY.SOR, TY.ARG, TY.GAR):
            N = int(r.N[k])
            assert N == (cfg.n_tout if nom == "B-tout" else cfg.n_regulier)[(env, TY.niveau(k))]
            Ne = E.n_allonge(N) if TY.ENJEU_HAUT[k] else N
            cycles = max(3, min(60, 150_000 // N))
            p1 = X.suite_piege(RG.reference_un_type(r, k), cycles)
            attendu = 0.95 * cycles / (N + 1 + (cycles - 1) * (Ne + 1))   # épreuves réussies : allongement ensuite
            assert p1 == pytest.approx(attendu, rel=1e-12), (nom, env, TY.SIGLES[k])
            assert p1 <= 0.95 / (N + 1) + 1e-15   # borne de B (UAOQL adaptée) : au plus 0,95 ÷ (N + 1)
            if N <= 170:
                p2 = X.suite_piege(RG.reference_un_type(r, k), 2000, rafale=True, d=d, rng=rng)
                assert p2 == pytest.approx(0.95 / (d * Ne + 1), rel=0.05), (nom, env, TY.SIGLES[k], p2)


@pytest.mark.parametrize("env,niveau", [(e, n) for e in ENVS for n in ("faible", "moyen")] + [("banque", "fort")])
def test_point_3_suites_piege_dans_le_moteur(env, niveau):
    """« N réussites puis une erreur » avec le N réel de B-tout, dans le moteur vectorisé : chaque erreur est exécutée
    au palier 3, puis retire l'autonomie ; dégâts en plus = 1 erreur par cycle."""
    cfg = ES.config()
    k = {"faible": TY.ECR, "moyen": TY.DUR, "fort": TY.ARG}[niveau]
    N = cfg.n_tout[(env, niveau)]
    Ne = E.n_allonge(N) if TY.ENJEU_HAUT[k] else N
    cycles = 3 if niveau == "fort" else 5
    errp = []
    for c in range(cycles):
        errp += [False] * (N if c == 0 else Ne) + [True]
    suite = SU.suite_depuis_tableaux(np.full(len(errp), k), errp=errp)
    r = RG.regle("B-tout", env, cfg)
    m = MO.simuler(suite, [r], EP.FournisseurConstant(EP.REUSSIE), valeurs_e=(0.05,), garder_P=True)
    P, err = m.P[:, 0], np.array(errp)
    assert (P[err] == 3).all() and (P[~err] < 3).all()
    assert m.cpt.exc[0, 0, TY.ENJEU[k]] == cycles   # u_val = 1 : aucune erreur ratée par le validateur
    assert m.cpt.exc[0, 0, TY.ENJEU[k]] / len(errp) <= 1 / (N + 1)
    assert m.n_prom3[0, k] == cycles and m.n_retraits3[0, k] == cycles


# --------------------------------------------------------------------------
# Point 4 : erreurs plantées
# --------------------------------------------------------------------------
def suites_et_resultats():
    for g in (11, 12, 13):
        env = ENVS[g % 4]
        suite = ES.suite_synthetique(g, T=500, R=4, p_err=0.04)
        regles = ES.regles_test(env)
        m = MO.simuler(suite, regles, ES.FournisseurAleatoire(g, p_reussie=0.9, p_impossible=0.0), garder_P=True)
        yield suite, regles, m


def test_point_4_erreur_moyenne_ou_forte_au_palier_3_retire_l_autonomie_a_l_ecriture_meme():
    vues = 0
    for suite, regles, m in suites_et_resultats():
        for i, r in enumerate(regles):
            for c in range(suite.R):
                li = i * suite.R + c
                P = m.P[:, li]
                for k in TY.TYPES_SUITE:
                    if not TY.ENJEU_HAUT[k]:
                        continue
                    ts = np.nonzero((suite.typ[:, c] == k) & ~suite.plaf[:, c])[0]
                    for a, b in zip(ts[:-1], ts[1:]):
                        if P[a] == 3 and suite.errp[a, c]:
                            assert P[b] == 1, (r.nom, c, TY.SIGLES[k], a)   # retrait à l'écriture même
                            vues += 1
                    # décision 5 : au plus une erreur constatée passe au palier 3 avant le retrait
                    e3 = [suite.errp[t, c] and P[t] == 3 for t in ts]
                    assert not any(x and y for x, y in zip(e3[:-1], e3[1:]))
    assert vues > 20


def test_point_4_tout_faire_valider_n_a_aucun_degat_en_plus():
    for suite, _r, _m in suites_et_resultats():
        cpt = MO.compter_paliers(TM.paliers_fixes("tout_valider", suite), suite, valeurs_e=(0.0, 0.02, 0.05, 0.1))
        assert (cpt.exc == 0).all() and (cpt.exc_part == 0).all() and (cpt.inv3 == 0).all()
        assert (cpt.dmg[0] == 0).all() and cpt.dmg[3].sum() > 0   # e = 0 : aucun dégât ; e = 10 % : quelques-uns
    e, prep, cfg = ES.entrees_pilote(), ES.preparees_pilote(), ES.config()
    rs = RJ.rejouer_configuration(prep, e, cfg, "aviation", "claude-sonnet-5-5", ES.taches_pilote("aviation"), R=50,
                                  jeu="developpement")
    tv = rs.agregats("tout_valider")
    assert (tv["exc"] == 0).all()
    assert (rs.agregats("tout_approuver")["exc"][0].sum(axis=1) > 0).all()


def test_point_4_une_refusee_ne_fait_aucun_degat():
    T = 60
    typ = np.full(T, TY.ARG)
    errp = np.zeros(T, bool)
    errp[::7] = True
    suite = SU.suite_depuis_tableaux(typ, errp=errp, errd=np.zeros(T, bool), den=~errp)  # toutes refusées
    cpt = MO.compter_paliers(TM.paliers_fixes("tout_approuver", suite), suite, valeurs_e=(0.0, 0.05, 0.5))
    assert (cpt.exc == 0).all() and (cpt.dmg == 0).all() and (cpt.cor == 0).all()
    # la refusée reste une erreur pour la règle (remise à zéro, épreuve)
    r = RG.variante(RG.regle("B-tout", "commerce", ES.config()), "B-2", N=np.where(TY.MERITE, 2, 0))
    m = MO.simuler(suite, [r], EP.FournisseurConstant(EP.REUSSIE), garder_P=True)
    assert m.ep_ouvertes[0] == errp.sum() and m.cpt.exc[0].sum() == 0
    # sur le pilote : la refusée d'aviation (Sonnet) ne compte pas dans les dégâts de « tout approuver »
    jc = SU.jeu_configuration(ES.preparees_pilote(), ES.entrees_pilote(), "aviation", "claude-sonnet-5-5",
                              ES.taches_pilote("aviation"), "developpement")
    refusees = jc.attrs["errp"] & ~jc.attrs["errd"]
    assert refusees.sum() == 1 and not jc.attrs["den"][refusees].any()


def test_point_4_un_doublon_sans_effet_ne_coupe_pas_une_serie():
    """De l'action (verdicts.py) à la suite : N − 1 justes, un doublon sans effet, une juste -> palier 3."""
    N = 4
    base = dict(partie="p", tache="t", banc="workbench", domaine="email", outil="o", kind="écriture", motif="",
                type="écriture réversible", enjeu="faible", plafonnee=False, montant=None)

    def suite_de(verdicts):
        ps = [PR.preuve(EN.Action(rang=i, verdict=v, **base), EN.DecisionRetenue("x", EN.CONFIRMEE, "", "v", False)
                        if v == "fausse" else None) for i, v in enumerate(verdicts)]
        return SU.suite_depuis_tableaux([p.type for p in ps], ver=[p.verifiable for p in ps],
                                        reu=[p.reussite for p in ps], errp=[p.erreur_preuve for p in ps],
                                        errd=[p.erreur_degat for p in ps], den=[p.au_denominateur for p in ps])

    r = RG.variante(RG.regle("B-tout", "WorkBench", ES.config()), "B-4", N=np.where(TY.MERITE, N, 0))
    suite = suite_de(["juste"] * (N - 1) + ["doublon sans effet", "juste", "juste"])
    P = MO.simuler(suite, [r], EP.FournisseurConstant(), garder_P=True).P[:, 0]
    assert P.tolist() == [1, 1, 1, 1, 1, 3]   # la série continue à travers le doublon sans effet
    assert (suite.den[:, 0].tolist(), bool(suite.ver[N - 1, 0])) == ([True] * (N - 1) + [False, True, True], True)
    coupee = suite_de(["juste"] * (N - 1) + ["fausse", "juste", "juste"])
    assert MO.simuler(coupee, [r], EP.FournisseurConstant(), garder_P=True).P[:, 0].max() == 1


def test_point_4_une_plafonnee_reste_au_palier_1():
    T = 400
    rng = np.random.default_rng(5)
    typ = np.full(T, TY.ARG)
    plaf = rng.random(T) < 0.2
    suite = SU.suite_depuis_tableaux(typ, plaf=plaf)   # aucune erreur : ARG non plafonné atteint vite le palier 3
    regles = ES.regles_test("commerce")
    m = MO.simuler(suite, regles, EP.FournisseurConstant(), garder_P=True)
    assert (m.P[plaf] == 1).all()
    assert (m.P[~plaf] == 3).any()
    for nom in ("tout_valider", "liste_fixe", "tri_risque"):
        assert (TM.paliers_fixes(nom, suite)[plaf] == 1).all()
    assert (TM.paliers_trois_reussites(suite)[plaf] == 1).all()
    assert (TM.paliers_oracle(suite, {TY.ARG: {"classe": "sous la barre"}})[plaf] == 1).all()
    assert (TM.paliers_hasard(suite, np.ones(TY.NT), np.ones(TY.NT), np.zeros((T, 1)))[plaf] == 1).all()
    assert (TM.paliers_fixes("tout_approuver", suite)[plaf] == 3).all()   # sauf « tout approuver »
    # Q4 b : les réussites plafonnées ne font pas avancer la série ; une erreur plafonnée la remet à zéro
    r = RG.variante(RG.regle("B-tout", "commerce", ES.config()), "B-3", N=np.where(TY.MERITE, 3, 0))
    s2 = SU.suite_depuis_tableaux(np.full(9, TY.ARG), plaf=[0, 1, 1, 1, 0, 0, 1, 0, 0],
                                  errp=[0, 0, 0, 0, 0, 0, 1, 0, 0])
    m2 = MO.simuler(s2, [r], EP.FournisseurConstant(EP.REUSSIE), garder_P=True)
    assert m2.P[:, 0].tolist() == [1, 1, 1, 1, 1, 1, 1, 1, 1]
    assert m2.ep_ouvertes[0] == 1 and m2.ep_tentatives[0] == 1   # ouverte par la plafonnée, passée à t = 7


# --------------------------------------------------------------------------
# Point 7 : déterminisme
# --------------------------------------------------------------------------
def test_point_7_memes_graines_memes_sorties_par_empreinte():
    e, prep, cfg = ES.entrees_pilote(), ES.preparees_pilote(), ES.config()
    taches = ES.taches_pilote("commerce")
    kw = dict(R=40, jeu="developpement", taches_calibration=taches)
    a = RJ.rejouer_configuration(prep, e, cfg, "commerce", "claude-haiku-5-5", taches, **kw)
    b = RJ.rejouer_configuration(prep, e, cfg, "commerce", "claude-haiku-5-5", taches, **kw)
    c = RJ.rejouer_configuration(prep, e, cfg, "commerce", "claude-haiku-5-5", taches, G0=1, **kw)
    assert RJ.empreinte(a) == RJ.empreinte(b)
    assert RJ.empreinte(a) != RJ.empreinte(c)
    cf = RJ.preparer_configuration(prep, e, cfg, "commerce", "claude-haiku-5-5", taches, jeu="developpement")
    assert RJ.empreinte(RJ.rejouer_bootstrap(cf, 4, 5)) == RJ.empreinte(RJ.rejouer_bootstrap(cf, 4, 5))
    assert RJ.empreinte(RJ.rejouer_bootstrap(cf, 4, 5)) != RJ.empreinte(RJ.rejouer_bootstrap(cf, 5, 5))
    # le résultat d'une règle ne dépend pas des autres règles rejouées avec elle
    seule = RJ.rejouer_configuration(prep, e, cfg, "commerce", "claude-haiku-5-5", taches, R=40, jeu="developpement",
                                     noms_regles=("B-tout",))
    np.testing.assert_array_equal(seule.moteur.cpt.exc, a.moteur.cpt.exc[:, :40])
    np.testing.assert_array_equal(seule.moteur.ep_reussies, a.moteur.ep_reussies[:40])
