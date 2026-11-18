"""Rejeu, phase 2 : tests de résistance (PLAN_EXPERIENCE.md, 5.11) — rate10 et ratées groupées (le constat différé
retard10 est testé avec les scénarios, contre les références).
"""
import math

import numpy as np

from rejeu import epreuves as EP
from rejeu import essais as ES
from rejeu import lots as LO
from rejeu import moteur as MO
from rejeu import suites as SU
from rejeu import types_regle as TY


def lot_pilote(env="banque", modele="claude-haiku-5-5", R=40):
    e, prep = ES.entrees_pilote(), ES.preparees_pilote()
    j = SU.jeu_configuration(prep, e, env, modele, ES.taches_pilote(env), "developpement")
    return LO.lot_r0(j, 3, R)


def test_rate10_erreurs_non_vues_comptees_comme_reussites():
    lot = lot_pilote("commerce", R=200)
    s = lot.suite
    t = LO.transformer_resistance(lot, "rate10")
    ts = t.suite
    nv = ts.rate
    assert (nv == (s.errp & (s.u_res < LO.PART_RATEE))).all()
    assert 0.03 < nv.sum() / s.errp.sum() < 0.2                     # environ 10 % des erreurs confirmées
    assert (ts.errd == s.errd).all() and (ts.den == s.den).all()    # elles restent des dégâts
    assert (ts.reu[nv]).all() and not (ts.errp[nv]).any()           # la règle les compte comme des réussites
    assert (ts.errp == (s.errp & ~nv)).all()
    # mêmes tirages pour toutes les règles : u_res attaché aux écritures, fonction de la graine de la colonne
    c = 3
    n = int((s.typ[:, c] >= 0).sum())
    attendu = np.random.default_rng(s.graine("resistance", c)).random(s.T)[:n]
    assert (s.u_res[:n, c] == attendu).all()


def test_ratees_groupees_toutes_les_erreurs_de_10_pour_cent_des_taches():
    lot = lot_pilote("banque", R=30)
    rat = LO.taches_ratees(lot)
    assert all(len(r) == max(1, math.ceil(0.1 * lot.G)) for r in rat)
    assert rat == LO.taches_ratees(lot)                               # reproductible
    t = LO.transformer_resistance(lot, "groupees", rat)
    s, ts = lot.suite, t.suite
    tache_partie = [e.partie.tache for e in lot.jeu.parties]
    for c in range(s.R):
        for i in range(s.T):
            if s.typ[i, c] < 0:
                continue
            dans = tache_partie[int(s.partie[i, c])] in rat[c]
            assert ts.rate[i, c] == (bool(s.errp[i, c]) and dans)


def test_epreuves_sous_erreurs_non_vues():
    lot = lot_pilote("commerce", R=4)
    j = lot.jeu
    pool = EP.PoolEpreuves(j)
    tout_vu = lambda col, p, v, r: False       # noqa: E731
    f0 = EP.FournisseurParties(pool, lot.suite.cles_epreuves)
    f1 = EP.FournisseurParties(pool, lot.suite.cles_epreuves, tout_vu)
    # sans erreur non vue, le prédicat redonne la réussite précalculée
    for v in range(pool.n):
        for k in TY.TYPES_SUITE:
            assert pool.succes_non_vues(v, k, lambda r: False) == bool(pool.succes[v, k])
    nv = LO.non_vues_epreuves(lot, "rate10")
    assert isinstance(nv, EP.NonVuesTaux)
    assert isinstance(LO.non_vues_epreuves(lot, "groupees"), EP.NonVuesTaches)


def test_rate10_dans_le_moteur_baisse_les_erreurs_vues():
    s = ES.suite_synthetique(9, T=500, R=8, p_err=0.1)
    s.u_res = np.random.default_rng(1).random((s.T, s.R))
    lot = LO.Lot(suite=s, couche="R0", groupe=np.zeros(s.R, dtype=np.int64), n_groupes=1, G=1,
                 strate_grappe=np.zeros(1, dtype=np.int64), par_grappe={}, taches=("t",))
    t = LO.transformer_resistance(lot, "rate10")
    r = [x for x in ES.regles_test("WorkBench") if x.nom == "B-tout-petit"]
    m0 = MO.simuler(s, r, ES.FournisseurAleatoire(2))
    m1 = MO.simuler(t.suite, r, ES.FournisseurAleatoire(2))
    assert m1.n_retraits3.sum() <= m0.n_retraits3.sum()
    assert m1.cpt.exc.sum() >= m0.cpt.exc.sum()                     # plus d'autonomie, mêmes dégâts possibles
