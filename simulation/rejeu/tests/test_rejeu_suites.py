"""Rejeu, phase 1 : construction des suites (PLAN_EXPERIENCE.md, 5.5).

G(c, S), ordre canonique, permutations, mise bout à bout, tri, graines, reconstitution de l'ordre figé, couche
bootstrap par grappes de tâches (rééchantillonnage par strate, copies, remplissage VIDE).
"""
import dataclasses
from collections import Counter

import numpy as np

from rejeu import entrees as EN
from rejeu import essais as ES
from rejeu import suites as SU
from rejeu import types_regle as TY

G0 = 123456789


def jeu(env="banque", modele="claude-haiku-5-5", entrees=None, preparees=None):
    e = entrees or ES.entrees_pilote()
    p = preparees or ES.preparees_pilote()
    return SU.jeu_configuration(p, e, env, modele, ES.taches_pilote(env), "developpement")


def test_G_de_c_S_ordre_canonique_et_exclusions():
    jc = jeu()
    assert jc.n_parties == 10
    assert [e.partie.tache for e in jc.parties] == sorted(e.partie.tache for e in jc.parties)
    assert jc.debut[-1] == jc.typ.size == sum(e.n_ecritures for e in jc.parties)
    # une partie en échec technique sort de G(c, S) ; une tâche retirée aussi, avec toutes ses parties
    e = ES.entrees_pilote()
    victime = jc.parties[3].partie
    parties = [dataclasses.replace(p, statut_ok=False) if p.id == victime.id else p for p in e.parties]
    e2 = EN.Entrees(parties, e.actions, e.jointure, {("banque", "task_017"): "essai"}, {}, e.developpement)
    jc2 = jeu(entrees=e2)
    gardees = {x.partie.id for x in jc2.parties}
    assert victime.id not in gardees and "task_017" not in jc2.taches
    assert all(x.partie.tache != "task_017" for x in jc2.parties)
    assert jc2.n_parties == 10 - 1 - (victime.tache != "task_017")


def test_suite_R0_mise_bout_a_bout_et_tri():
    jc = jeu()
    s = SU.suite_r0(jc, G0, 40)
    assert s.T == jc.typ.size and (s.typ >= 0).all()  # même longueur à chaque répétition, aucun VIDE
    for c in range(s.R):
        unites = s.meta["unites"][c]
        assert sorted(u[0] for u in unites) == list(range(jc.n_parties))   # chaque partie une fois
        # chaque partie garde l'ordre de ses écritures (le rang)
        pos = 0
        for i, _copie in unites:
            e = jc.parties[i]
            n = e.n_ecritures
            assert (s.rang[pos:pos + n, c] == e.rang).all() and (s.partie[pos:pos + n, c] == i).all()
            assert (s.typ[pos:pos + n, c] == e.typ).all()
            pos += n
    # lectures, préparations et doutes retirés de la suite et comptés par partie
    assert (s.n_doutes == jc.n_doutes.sum()).all() and (s.n_lectures == jc.n_lectures.sum()).all()
    assert (s.n_actions == jc.n_actions.sum()).all()
    assert (s.n_ecritures + s.n_doutes + s.n_lectures + s.n_preparations == s.n_actions).all()
    assert len({tuple(u[0] for u in col) for col in s.meta["unites"]}) > 30  # permutations différentes


def test_permutation_uniforme():
    jc = jeu("aviation", "claude-sonnet-5-5")
    premiers = Counter(SU.ordre_unites(jc, G0, "R0", r)[0][0] for r in range(3000))
    assert len(premiers) == jc.n_parties
    assert max(abs(v / 3000 - 1 / jc.n_parties) for v in premiers.values()) < 0.03


def test_graines_et_reconstitution_de_l_ordre():
    ss = SU.graine(G0, "validateur", "banque", "claude-opus-5-5", 0, "bootstrap", 17, "calibration", 3)
    assert ss.entropy == [G0, 3, 2, 2, 0, 1, 17, 1, 3]
    jc = jeu()
    s = SU.suite_r0(jc, G0, 5, premiere=10)
    for c, r in enumerate(range(10, 15)):
        assert SU.ordre_unites(jc, G0, "R0", r) == [tuple(u) for u in s.meta["unites"][c]]
        n = int((s.typ[:, c] >= 0).sum())
        attendu = np.random.default_rng(SU.graine(G0, "validateur", "banque", "claude-haiku-5-5", 0, "R0", r,
                                                  "developpement", 0)).random(n)
        assert (s.u_val[:n, c] == attendu).all()
        assert s.cles_epreuves[c] == SU.entier_64(SU.graine(G0, "epreuves", "banque", "claude-haiku-5-5", 0, "R0", r,
                                                            "developpement", 0))
    assert SU.suite_r0(jc, G0, 3).meta["unites"] == SU.suite_r0(jc, G0, 3).meta["unites"]
    assert SU.suite_r0(jc, G0 + 1, 3).meta["unites"] != SU.suite_r0(jc, G0, 3).meta["unites"]


def test_couche_bootstrap_par_grappes_de_taches():
    jc = jeu("WorkBench", "claude-haiku-5-5")
    assert len(jc.strates) == 6   # WorkBench : une strate par fichier
    vus_doubles = 0
    longueurs = set()
    jb = jeu("banque", "claude-sonnet-5-5")   # parties de 1 à 3 écritures : longueurs variables
    assert len({x.n_ecritures for x in jb.parties}) > 1
    for b in range(25):
        longueurs.add(SU.suite_bootstrap(jb, G0, b, K=1).T)
        s = SU.suite_bootstrap(jc, G0, b, K=4)
        unites = [sorted(col) for col in s.meta["unites"]]
        assert all(u == unites[0] for u in unites)  # même tirage de tâches pour les K ordres
        # autant de tirages que de tâches de S dans chaque strate ; une tâche tirée apporte toutes ses parties
        rng = np.random.default_rng(SU.graine(G0, "reechantillonnage", "WorkBench", "claude-haiku-5-5", 0,
                                              "bootstrap", b, "developpement", 0))
        attendu = []
        for st, taches in jc.strates.items():
            tirees = rng.integers(0, len(taches), size=len(taches))
            assert len(tirees) == len(taches)
            for copie, j in enumerate(tirees.tolist()):
                attendu += [(i, copie) for i in jc.parties_par_tache.get(taches[j], ())]
            vus_doubles += len(tirees) - len(set(tirees.tolist()))
        assert sorted(attendu) == unites[0]
        # longueur variable, complétée par VIDE en fin de colonne
        for c in range(s.R):
            n = int((s.typ[:, c] >= 0).sum())
            assert (s.typ[:n, c] >= 0).all() and (s.typ[n:, c] == TY.VIDE).all()
            assert not s.den[n:, c].any() and not s.errp[n:, c].any() and (s.partie[n:, c] == -1).all()
    assert vus_doubles > 0 and len(longueurs) > 1
