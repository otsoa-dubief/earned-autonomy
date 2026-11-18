"""Rejeu, phase 1 : épreuves jouées à blanc, variantes tirées dans des parties enregistrées (PLAN_EXPERIENCE.md,
5.9 ; Q3).

Replis (même tâche, puis même outil, puis même type), partie fautive exclue, « épreuve impossible », réussite d'une
variante, tirage reproductible et apparié entre règles, attente de 50 écritures, charge de 3 validations par essai.
"""
from collections import Counter
from types import SimpleNamespace

import numpy as np

from rejeu import epreuves as EP
from rejeu import essais as ES
from rejeu import moteur as MO
from rejeu import regles as RG
from rejeu import rejeu as RJ
from rejeu import suites as SU
from rejeu import types_regle as TY


def faux_jeu(spec):
    """spec : [(tâche, [(type, outil, réussite, erreur), ...]), ...] -> objet lu par PoolEpreuves."""
    typ, outil, reu, errp, debut = [], [], [], [], [0]
    parties = []
    for tache, ecritures in spec:
        parties.append(SimpleNamespace(partie=SimpleNamespace(tache=tache)))
        for k, o, r, e in ecritures:
            typ.append(k), outil.append(o), reu.append(r), errp.append(e)
        debut.append(len(typ))
    return SimpleNamespace(n_parties=len(spec), parties=parties, debut=np.array(debut), typ=np.array(typ, np.int8),
                           outil=np.array(outil, np.int32),
                           attrs={"reu": np.array(reu, bool), "errp": np.array(errp, bool)})


D, A = TY.DUR, TY.ARG


def test_splitmix_python_et_numpy():
    assert EP.melanger(0) == 0xE220A8397B1DCDAF   # première sortie de SplitMix64 pour la graine 0
    x = np.random.default_rng(1).integers(0, 2 ** 63, size=50, dtype=np.uint64)
    assert [EP.melanger(int(v)) for v in x] == [int(v) for v in EP.melanger_tableau(x)]


def test_replis_meme_tache_puis_meme_outil_puis_meme_type():
    spec = [("t1", [(D, 0, True, False)]),            # 0 : partie fautive
            ("t1", [(D, 0, True, False)]),            # 1 : même tâche
            ("t2", [(D, 0, True, False)]),            # 2 : même outil
            ("t3", [(D, 1, True, False)]),            # 3 : même type
            ("t4", [(D, 1, True, False)]),            # 4 : même type
            ("t5", [(A, 2, True, False)])]            # 5 : rien de commun
    pool = EP.PoolEpreuves(faux_jeu(spec))
    cas = EP.Cas(0, 0, 0)
    n1, n2, n3 = pool.niveaux(D, cas)
    assert n1.tolist() == [1] and n2.tolist() == [2] and set(n3.tolist()) == {3, 4}
    for cle in range(30):
        v = pool.tirer(cle, D, cas)
        assert v[:2] == (1, 2) and v[2] in (3, 4) and 0 not in v
    # moins de 3 candidats : épreuve impossible
    assert EP.PoolEpreuves(faux_jeu(spec[:3])).tirer(5, D, cas) is None
    f = EP.FournisseurParties(EP.PoolEpreuves(faux_jeu(spec[:3])), [7])
    iss = f.issue(0, 0, 0, D, cas, 0)
    assert iss.statut == EP.IMPOSSIBLE and iss.validations == 0


def test_tirage_uniforme_dans_la_meme_tache_et_reproductible():
    spec = [("t1", [(D, 0, True, False)]) for _ in range(9)]
    pool = EP.PoolEpreuves(faux_jeu(spec))
    cas = EP.Cas(4, 0, 0)
    vus = Counter()
    for cle in range(3000):
        v = pool.tirer(EP.combiner(99, cle), D, cas)
        assert len(set(v)) == 3 and 4 not in v and all(pool.tache[i] == "t1" for i in v)
        vus.update(v)
    assert set(vus) == set(range(9)) - {4}
    assert max(abs(c / 3000 - 3 / 8) for c in vus.values()) < 0.04
    f = EP.FournisseurParties(pool, [11, 12])
    assert f.issue(0, 0, 1, D, cas, 0) == f.issue(57, 9, 1, D, cas, 0)   # même essai du même cas : apparié
    autres = {f.issue(0, 0, 1, D, cas, n).variantes for n in range(20)}
    assert len(autres) > 5                                             # un nouvel essai tire de nouvelles variantes


def test_reussite_d_une_variante():
    spec = [("t", [(D, 0, True, False)]),                      # 0 fautive
            ("t", [(D, 0, True, False), (A, 1, False, True)]),  # 1 : réussie (l'erreur est d'un autre type)
            ("t", [(D, 0, True, False), (D, 0, False, True)]),  # 2 : une erreur confirmée du type : ratée
            ("t", [(D, 0, False, False)]),                      # 3 : seulement un neutre du type : ratée
            ("t", [(A, 1, True, False)]),                       # 4 : aucune écriture du type : ratée
            ("t", [(D, 0, True, False), (D, 0, True, False)])]  # 5 : réussie
    pool = EP.PoolEpreuves(faux_jeu(spec))
    assert pool.succes[:, D].tolist() == [True, True, False, False, False, True]
    f = EP.FournisseurParties(pool, [3])
    statuts = {}
    for n in range(60):
        iss = f.issue(0, 0, 0, D, EP.Cas(0, 0, 0), n)
        attendu = EP.REUSSIE if set(iss.variantes) <= {1, 5} else EP.RATEE
        assert iss.statut == attendu and iss.validations == 3
        statuts[iss.statut] = 1
    assert len(statuts) == 1  # {1, 5} ne fait que 2 parties : 3 variantes en contiennent toujours une ratée


def suite_dur(n_succes_avant, n_apres, erreur=True):
    """Un seul type (DUR, moyen) : réussites, une erreur, puis des réussites."""
    errp = [False] * n_succes_avant + ([True] if erreur else []) + [False] * n_apres
    return SU.suite_depuis_tableaux(np.full(len(errp), TY.DUR), errp=errp)


def regle_dur(N):
    r = RG.regle("B-tout", "WorkBench", ES.config())
    return RG.variante(r, "B-petit", N=np.where(r.N > 0, N, 0))


def test_epreuve_impossible_garde_le_type_au_palier_1():
    s = suite_dur(5, 200)
    r = regle_dur(5)
    m = MO.simuler(s, [r], EP.FournisseurConstant(EP.IMPOSSIBLE), garder_P=True)
    P = m.P[:, 0]
    assert P[5] == 3 and (P[6:] == 1).all()   # palier 3, l'erreur le retire, puis plus jamais
    assert m.ep_impossibles[0] == 200 and m.ep_validations[0] == 0 and m.ep_reussies[0] == 0
    m2 = MO.simuler(s, [r], EP.FournisseurConstant(EP.REUSSIE), garder_P=True)
    P2 = m2.P[:, 0]
    # épreuve réussie à l'écriture suivante (elle compte comme réussite), puis ⌈1,25 N⌉ = 7 réussites
    assert (P2[6:6 + 7] == 1).all() and P2[6 + 7] == 3
    assert m2.ep_tentatives[0] == 1 and m2.ep_validations[0] == 3


def test_attente_de_50_ecritures_apres_une_epreuve_ratee():
    s = suite_dur(0, 300)
    m = MO.simuler(s, [regle_dur(5)], EP.FournisseurConstant(EP.RATEE), journal=True)
    ts = [t for (_l, t, _k, _s, _v, _c) in m.journal]
    assert ts == list(range(1, 301, 51))     # essais aux arrivées 1, 52, 103… (attente de 50, E1)
    assert m.ep_tentatives[0] == len(ts) and m.ep_validations[0] == 3 * len(ts) and m.ep_ratees[0] == len(ts)
    assert m.ep_ouvertes[0] == 1


def test_variantes_tirees_dans_G_d_origine_meme_en_bootstrap():
    e, prep, cfg = ES.entrees_pilote(), ES.preparees_pilote(), ES.config()
    for env, mod in (("aviation", "claude-sonnet-5-5"), ("commerce", "claude-haiku-5-5")):
        cf = RJ.preparer_configuration(prep, e, cfg, env, mod, ES.taches_pilote(env), jeu="developpement",
                                       regles=ES.regles_test(env))
        vus = 0
        for b in range(6):
            rs = RJ.rejouer_bootstrap(cf, b, K=3, journal=True)
            for (_l, _t, k, st, variantes, cas) in rs.moteur.journal:
                assert st in (EP.REUSSIE, EP.RATEE)
                assert len(variantes) == 3 and cas.partie not in variantes
                assert all(0 <= v < cf.jeu.n_parties for v in variantes)
                vus += 1
        assert vus > 0
