"""Rejeu, phase 2 : scénarios de changement de modèle (PLAN_EXPERIENCE.md, 5.10) et constat différé (5.11, retard10).

- Équivalence (5.16, point 2) : le moteur vectorisé et les références par type donnent le même palier, écriture par
  écriture, avec une jonction annoncée (changement_configuration des références) ou silencieuse, et avec le constat
  différé de 10 écritures du type (logique d'E1 : file par type).
- Suivi après la jonction : palier à la jonction, perte du palier 3, délai, erreurs passées, périodes d'autonomie.
- Suites des scénarios : X puis Y, jonction, même tirage des tâches pour les deux segments, épreuves jouées par le
  modèle courant ; oracle qui change de classes à la jonction.
"""
from collections import deque
from types import SimpleNamespace

import numpy as np
import pytest

from rejeu import analyse as AN
from rejeu import classes as CL
from rejeu import config_rejeu as CR
from rejeu import epreuves as EP
from rejeu import essais as ES
from rejeu import lots as LO
from rejeu import moteur as MO
from rejeu import regles as RG
from rejeu import suites as SU
from rejeu import types_regle as TY


def reference_scenario(s, r, c, issues, jonction=None, annonce=False, retard=0):
    """Paliers d'une colonne avec les références par type, jonction et constat différé compris."""
    regs = {k: RG.reference_un_type(r, k) for k in TY.TYPES_SUITE}
    files = {k: deque() for k in TY.TYPES_SUITE}
    out = np.zeros(s.T, dtype=np.int8)
    for t in range(s.T):
        if jonction is not None and t == jonction and annonce:
            for rg in regs.values():
                rg.changement_configuration()
            # audit du moteur (09/11, point 5) : les preuves en attente de l'ancien modèle sont abandonnées
            files = {k: deque([0] * len(f)) for k, f in files.items()}
        k = int(s.typ[t, c])
        if k < 0:
            continue
        rg = regs[k]
        plaf = bool(s.plaf[t, c])
        if plaf:
            out[t] = 1
        else:
            if rg.epreuve_due():
                st = issues[(t, k)]
                if st == EP.REUSSIE:
                    rg.resultat_epreuve(True)
                elif st == EP.RATEE:
                    rg.resultat_epreuve(False)
            out[t] = rg.palier
        code = 1 if (s.ver[t, c] and s.reu[t, c] and not plaf) else (2 if s.errp[t, c] else 0)
        if retard:
            files[k].append(code)
            code = files[k].popleft() if len(files[k]) > retard else 0
        if code == 1:
            rg.succes()
        elif code == 2:
            rg.erreur()
        else:
            rg.neutre()
    return out


@pytest.mark.parametrize("annonce,retard,graine", [(True, 0, 1), (False, 0, 2), (True, 10, 3), (False, 10, 4)])
def test_equivalence_jonction_et_constat_differe(annonce, retard, graine):
    s = ES.suite_synthetique(100 + graine, T=400, R=5, p_err=0.08)
    rng = np.random.default_rng(graine)
    longueurs = (s.typ >= 0).sum(axis=0)
    s.jonction = np.array([int(rng.integers(L // 4, 3 * L // 4)) for L in longueurs], dtype=np.int64)
    regles = ES.regles_test("WorkBench")
    m = MO.simuler(s, regles, ES.FournisseurAleatoire(graine), journal=True, garder_P=True, annonce=annonce,
                   retard=retard)
    for i, r in enumerate(regles):
        for c in range(s.R):
            li = i * s.R + c
            ref = reference_scenario(s, r, c, m.issues_ligne(li), int(s.jonction[c]), annonce, retard)
            np.testing.assert_array_equal(m.P[:, li], ref, err_msg=f"{r.nom} colonne {c}")
    assert m.suivi.all()


def test_jonction_annoncee_remet_a_zero_et_convertit_les_erreurs_en_epreuves():
    # DUR (moyen) : 3 réussites (N = 2 : palier 3), une erreur au palier 3 (épreuve ouverte, palier 1), réussites...
    typ = [TY.DUR] * 10
    errp = [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    s = SU.suite_depuis_tableaux(typ, errp=errp)
    s.jonction = np.array([6])
    r = RG.variante(RG.regles("banque", ES.config(), ("B-tout",))[0], "B2", N=np.where(TY.MERITE, 2, 0))
    for annonce in (True, False):
        m = MO.simuler(s, [r], EP.FournisseurConstant(EP.RATEE), journal=True, garder_P=True, annonce=annonce)
        assert m.snap[0, TY.DUR] == 1        # l'épreuve ouverte au pas 3 n'est pas réussie : palier 1
    # erreur gardée en mémoire avant la jonction, épreuve réussie entre-temps (s reste 1) : convertie à la jonction
    s2 = SU.suite_depuis_tableaux([TY.DUR] * 8, errp=[1, 0, 0, 0, 0, 0, 0, 0])
    s2.jonction = np.array([5])
    m = MO.simuler(s2, [r], EP.FournisseurConstant(EP.REUSSIE), journal=True, garder_P=True, annonce=True)
    essais = [t for (_l, t, _k, st, _v, _c) in m.journal]
    assert essais[0] == 1 and 5 in essais       # épreuve due à l'arrivée suivante, puis épreuve convertie (Ec)
    assert m.P[5, 0] == 1 and m.P[4, 0] == 3    # palier 3 juste avant la jonction ; palier 1 à la jonction
    m2 = MO.simuler(s2, [r], EP.FournisseurConstant(EP.REUSSIE), journal=True, garder_P=True, annonce=False)
    assert 5 not in [t for (_l, t, _k, _s, _v, _c) in m2.journal] and m2.P[5, 0] == 3   # silencieux : rien


def test_suivi_apres_la_jonction_retrait_delai_et_periodes():
    # palier 3 sur DUR avant la jonction ; après : 2 réussites puis une erreur avec dégât au palier 3
    typ = [TY.DUR] * 8
    errp = [0, 0, 0, 0, 0, 0, 1, 0]
    s = SU.suite_depuis_tableaux(typ, errp=errp)
    s.jonction = np.array([4])
    r = RG.variante(RG.regles("banque", ES.config(), ("B-tout",))[0], "B2", N=np.where(TY.MERITE, 2, 0))
    m = MO.simuler(s, [r], EP.FournisseurConstant(EP.RATEE), garder_P=True, annonce=False)
    k = TY.DUR
    assert m.snap[0, k] == 3 and m.perte3[0, k] == 6 and m.delai3[0, k] == 3   # 3 écritures du type (4, 5, 6)
    assert m.err_delai[0, k] == 1 and m.n_periodes[0, k] == 1 and m.max_constatees[0, k] == 1
    assert m.cpt.exc_w[0, 0, TY.MOYEN] == 1 and m.cpt.exc[0, 0, TY.MOYEN] == 1
    ma = MO.simuler(s, [r], EP.FournisseurConstant(EP.RATEE), garder_P=True, annonce=True)
    assert ma.perte3[0, k] == 4 and ma.delai3[0, k] == 0                        # annoncé : retrait à la jonction


def test_critere_de_retrait_tenu_par_construction():
    # constat immédiat : au plus une erreur constatée par période d'autonomie à enjeu moyen ou fort (RF1)
    s = ES.suite_synthetique(77, T=600, R=6, p_err=0.15, types=(TY.DUR, TY.ARG, TY.ECR))
    s.jonction = np.full(s.R, 50)
    regles = [r for r in ES.regles_test("WorkBench") if r.nom.endswith("-petit")]
    m = MO.simuler(s, regles, ES.FournisseurAleatoire(5), annonce=False)
    haut = [k for k in TY.TYPES_SUITE if TY.ENJEU_HAUT[k]]
    assert (m.max_constatees[:, haut] <= 1).all()
    assert m.n_periodes[:, haut].sum() > 0
    md = MO.simuler(s, regles, ES.FournisseurAleatoire(5), annonce=False, retard=10)
    assert md.max_constatees[:, haut].max() >= 2      # constat différé : plusieurs erreurs passent (rapporté)


def test_suites_des_scenarios_sur_le_pilote():
    e, prep, cfg = ES.entrees_pilote(), ES.preparees_pilote(), ES.config()
    t = ES.taches_pilote("aviation")
    jX = SU.jeu_configuration(prep, e, "aviation", "claude-haiku-5-5", t, "developpement")
    jY = SU.jeu_configuration(prep, e, "aviation", "claude-opus-5-5", t, "developpement")
    lot = LO.lot_scenario_r0(jX, jY, 9, 5)
    s = lot.suite
    nX = jX.n_parties
    for c in range(s.R):
        n = int((s.typ[:, c] >= 0).sum())
        j = int(s.jonction[c])
        assert j == int(jX.longueurs.sum()) and n == j + int(jY.longueurs.sum())
        assert (s.partie[:j, c] < nX).all() and (s.partie[j:n, c] >= nX).all()
    assert len(LO.couples()) == 6 and LO.numero_scenario("claude-haiku-5-5", "claude-opus-5-5") == 2
    # bootstrap : les deux segments utilisent le même tirage de tâches
    lb = LO.lot_scenario_bootstrap(jX, jY, 9, [0, 1, 2], 2)
    jc = lb.jeu
    for c in range(lb.suite.R):
        sb = lb.suite
        j = int(sb.jonction[c])
        n = int((sb.typ[:, c] >= 0).sum())
        gx = sorted(set(sb.grappe[:j, c].tolist()))
        gy = sorted(set(sb.grappe[j:n, c].tolist()))
        taches = lambda rows: {jc.parties[p].partie.tache for p in sb.partie[rows, c].tolist()}  # noqa: E731
        occ_x = {(g, jc.parties[int(sb.partie[i, c])].partie.tache) for i, g in zip(range(j), sb.grappe[:j, c])}
        occ_y = {(g, jc.parties[int(sb.partie[i, c])].partie.tache) for i, g in
                 zip(range(j, n), sb.grappe[j:n, c])}
        par_g = {}
        for g, tt in occ_x | occ_y:
            par_g.setdefault(g, set()).add(tt)
        assert all(len(v) == 1 for v in par_g.values())      # une occurrence = une seule tâche, dans X comme dans Y
        assert set(gx) | set(gy) <= set(range(lb.G))
    # même tirage que les configurations constantes de la même répétition (tirage commun, sans le modèle)
    tir = LO.tirage_commun(9, "aviation", 1, "developpement", jX.strates)
    for j_ in (jX, jY):
        lc = LO.lot_bootstrap(j_, 9, [1], 2)
        attendu = sorted((p, c) for p, c, _g in LO.unites_tirage(j_, tir))
        for c in range(2):
            assert sorted(tuple(u) for u in lc.suite.meta["unites"][c]) == attendu


def faux_jeu(taches, outils_noms):
    parties = [SimpleNamespace(partie=SimpleNamespace(tache=t)) for t, _ in taches]
    typ, outil, reu, errp, debut = [], [], [], [], [0]
    for _t, ecr in taches:
        for k, o, r_, e_ in ecr:
            typ.append(k), outil.append(o), reu.append(r_), errp.append(e_)
        debut.append(len(typ))
    return SimpleNamespace(n_parties=len(taches), parties=parties, debut=np.array(debut),
                           typ=np.array(typ, np.int8), outil=np.array(outil, np.int32), outils=outils_noms,
                           rang=np.arange(len(typ), dtype=np.int32),
                           attrs={"reu": np.array(reu, bool), "errp": np.array(errp, bool)})


def test_epreuves_jouees_par_le_modele_courant():
    D = TY.DUR
    jX = faux_jeu([("t1", [(D, 0, 0, 1)]), ("t1", [(D, 0, 1, 0)]), ("t2", [(D, 0, 1, 0)]), ("t3", [(D, 0, 1, 0)])],
                  ("outilA",))
    jY = faux_jeu([("t1", [(D, 0, 1, 0)]), ("t1", [(D, 0, 1, 0)]), ("t1", [(D, 0, 0, 1)]), ("t9", [(D, 0, 1, 0)])],
                  ("outilA",))
    pX, pY = EP.PoolEpreuves(jX), EP.PoolEpreuves(jY)
    f = EP.FournisseurScenario(pX, pY, 4, [11], np.array([10]), ("outilA",))
    cas = EP.Cas(0, 0, 0)                       # cas de X, tâche t1
    avant = f.issue(0, 5, 0, D, cas, 0)
    assert set(avant.variantes) == {1, 2, 3}     # X : même tâche (partie 1), puis même outil
    apres = f.issue(0, 12, 0, D, cas, 0)
    assert set(apres.variantes) == {0, 1, 2}     # Y : ses trois parties de t1 (aucune à exclure)
    assert apres.statut == EP.RATEE              # la partie 2 de Y a une erreur
    # erreur non vue (rate10 des épreuves) : la variante devient réussie
    nv = lambda col, pool, v, rang: True        # noqa: E731
    assert pY.succes_non_vues(2, D, lambda r: True) and not pY.succes[2, D]


def test_oracle_change_de_classes_a_la_jonction():
    s = SU.suite_depuis_tableaux([TY.ECR, TY.DUR, TY.ECR, TY.DUR])
    s.jonction = np.array([2])
    sous = {"classe": CL.SOUS}
    au = {"classe": CL.AU_DESSUS}
    P = AN.paliers_oracle_segments(s, {TY.ECR: sous, TY.DUR: au}, {TY.ECR: au, TY.DUR: sous})
    assert P[:, 0].tolist() == [3, 1, 2, 3]      # ECR réversible au-dessus : palier 2 (B1)
