"""Rejeu, phase 3 : critère de B-tout (Q13 : dépassement établi par max-T, borne de construction, s ÷ q, « démontrée »),
simulation de couverture refaite sur la différence de charge, lettre d'origine (Q8 A), rejeu final branché
(parallélisation déterministe, entrée de l'expérience réelle).
"""
import json
import os

import numpy as np
import pytest

from rejeu import analyse as AN
from rejeu import bout_en_bout as BE
from rejeu import classes as CL
from rejeu import config_rejeu as CR
from rejeu import couverture as CO
from rejeu import couverture_charge as CC
from rejeu import decision as DE
from rejeu import essais as ES
from rejeu import maxt as MX
from rejeu import pipeline as PL
from rejeu import regles as RG
from rejeu import types_regle as TY

import config_e1 as E


def _analyse_petite(envs=("commerce", "banque"), processus=1, N=2):
    e, prep, cfg = ES.entrees_pilote(), ES.preparees_pilote(), ES.config()
    cal, conf = BE.partage_par_env(BE.partage_pilote(e))
    regles = {env: [RG.variante(RG.regles(env, cfg, ("B-tout",))[0], "B-tout", N=np.where(TY.MERITE, N, 0))]
              for env in envs}
    reg = AN.Reglages(G0=11, R0=8, B=12, K=2, tranche=6, noms_regles=("B-tout",),
                      choix=dict(methode="iii", repli=False, G_sur=20, methode_seconde="percentile"))
    an = PL.analyser(e, prep, cfg, reg, {k: conf[k] for k in envs}, {k: cal[k] for k in envs}, processus=processus,
                     regles_imposees=regles)
    return an, cfg


def test_q13_meme_mesure_pour_b_tout():
    an, cfg = _analyse_petite()
    cel = DE.cellules(an, "B-tout")
    jug = [c for c in cel if c["statut"] == DE.JUGEE]
    assert jug, "B-tout à N = 2 atteint le palier 3 sur le pilote"
    assert all(c["verdict"] in (DE.ETABLI, DE.NON_REFUTEE) for c in jug)
    assert all(c["verdict"] == c["statut"] for c in cel if c["statut"] != DE.JUGEE)
    # le max-T est celui des témoins, sur les seules cellules jugées
    B = an.reglages.B
    qs = [an.magasin[("budget",) + c["famille"] + ("B-tout", c["e"], c["niveau"])] for c in jug]
    r = MX.depassement_etabli(np.array([q.centre for q in qs]), np.stack([q.boot.tableau()[:B] for q in qs], axis=1),
                              np.array([c["budget"] for c in jug]))
    assert [c["etabli"] for c in jug] == r["etabli"].tolist()
    p1 = DE.point1(an)
    assert p1["tenu"] == (not any(c["etabli"] for c in jug))
    # borne de construction, s ÷ q (calcul direct) et « démontrée » (Clopper-Pearson sur la taille effective)
    for c in jug[:6]:
        cm, niv = c["famille"], c["niveau"]
        jeu = DE.jeu_famille(an, cm)
        j = TY.NIVEAUX.index(niv)
        niv_e = TY.ENJEU[np.where(jeu.typ >= 0, jeu.typ, 0)]
        den = jeu.attrs["den"] & (jeu.typ >= 0)
        s = (den & ~jeu.attrs["plaf"] & (niv_e == j)).sum() / den.sum()
        sq = s / float(cfg.q[(cm[1], niv)])
        assert c["s_sur_q"] == pytest.approx(sq)
        assert c["borne_construction"] == pytest.approx(0.95 * c["budget"] * sq)
        m = list(_den_taches(jeu).values())
        rho = DE.rho_cellule(an, cm)[0]
        n, _, ne = CL.taille_effective(m, rho)
        hi = 100 * CL.bornes_cp(c["centre"] * n / 100 * ne / n, ne)[1]
        assert c["borne_cp_haute"] == pytest.approx(hi) and c["demontree"] == (hi <= c["budget"])
        assert c["garantie_hors_hypothese"] == (c["s_sur_q_lo"] > 1 / 0.95)
    # plus de passe, échoue ou indécise, ni de relance
    assert not hasattr(PL, "relancer_indecises")


def _den_taches(jeu):
    t = CL.taches_ecritures(jeu)
    out = {}
    for x in t[jeu.attrs["den"] & (jeu.typ >= 0)].tolist():
        out[x] = out.get(x, 0) + 1
    return out


def test_parallelisation_deterministe():
    a1, _ = _analyse_petite(("commerce", "aviation"), processus=1)
    a2, _ = _analyse_petite(("commerce", "aviation"), processus=2)
    assert list(a1.magasin) == list(a2.magasin)
    for k, q in a1.magasin.items():
        r = a2.magasin[k]
        np.testing.assert_array_equal(np.asarray([q.centre, q.se], float), np.asarray([r.centre, r.se], float))
        np.testing.assert_array_equal(q.boot.tableau(), r.boot.tableau())
        np.testing.assert_array_equal(q.se_boot.tableau(), r.se_boot.tableau())
        if q.jack is not None:
            np.testing.assert_array_equal(q.jack, r.jack)
    assert a1.resume_r0.keys() == a2.resume_r0.keys()


def test_simulation_de_la_difference_de_charge():
    a = CC.simuler_case((0.25, 0.15), 0.3, 20, n_jeux=30, graine=3, B_=100, paquet=10)
    assert a == CC.simuler_case((0.25, 0.15), 0.3, 20, n_jeux=30, graine=3, B_=100, paquet=10)
    assert CC.valeur_vraie((0.25, 0.15)) == pytest.approx(10.0)
    for l in a:
        assert abs(l["centre_moyen"] - l["valeur_vraie"]) < 3.0
    c = CO.lire_choix(CC.DOSSIER)                 # le choix écrit par la simulation, lu par le rejeu
    assert c["methode"] in ("i", "ii", "iii") and c["seuil"] == 0.93
    assert CC.verifier() == [] and CO.verifier() == []   # empreintes conformes, pour les deux dossiers


def test_lettre_d_origine_point_8():
    e, prep = ES.entrees_pilote(), ES.preparees_pilote()
    tot = {}
    for pid, x in prep.items():
        t = tot.setdefault(e.partie(pid).environnement, [0, 0, 0, 0])
        for i, v in enumerate((x.n_lectures, x.n_preparations, x.n_doutes, x.n_actions)):
            t[i] += v
    assert {k: tuple(v) for k, v in tot.items()} == CR.COMPTES_PILOTE      # recompté sur le pilote
    cfg = ES.config()
    for env in CR.ENVIRONNEMENTS:
        for niv in TY.NIVEAUX:
            b8, sec = CR.barre_lettre(env, niv)
            if sec:
                assert b8 == E.barre(CR.PROFIL_SECOURS[env], niv)
            else:
                assert b8 == cfg.barres[(env, niv)] / (1 - CR.part_hors_ecritures(env))
            assert cfg.n_tout_lettre[(env, niv)] == CR.n_b_tout(b8)
    assert cfg.n_tout_lettre[("aviation", "faible")] == 1               # « une erreur tolérée sur 1,3 » (point 9)
    r = RG.regle("B-tout-lettre", "banque", cfg)
    assert r.N[TY.ECR] == cfg.n_tout_lettre[("banque", "faible")]


def test_entree_de_l_experience_reelle(tmp_path):
    if BE.CR.charger_config().G0 is None:      # G0 vaut null avant le gel : refusé
        with pytest.raises(SystemExit):
            BE.executer_experience(BE.DOSSIER_PILOTE, str(tmp_path / "p.json"), [], str(tmp_path / "s"))
    else:                                     # après le gel : plus refusé pour G0 ; s'arrête sur le partage absent
        with pytest.raises(FileNotFoundError):
            BE.executer_experience(BE.DOSSIER_PILOTE, str(tmp_path / "p.json"), [], str(tmp_path / "s"))
    v = BE.vague_depuis_texte("v1=dec.csv,al.json,accord.json")
    assert (v.nom, v.decisions, v.alertes, v.bilan_otsoa) == ("v1", "dec.csv", "al.json", "accord.json")
    v2 = BE.vague_depuis_texte("v2=dec.csv")
    assert v2.alertes is None and v2.bilan_otsoa is None
    bilan = tmp_path / "accord.json"
    bilan.write_text(json.dumps(dict(conclusion="Relecture gardée", desaccord_persistant=False,
                                     decisions_otsoa={"a": "confirmée"}, fortes={"relues": 1})), encoding="utf-8")
    m = BE.meta_bilans([BE.EN.VagueRelecture("v1", str(bilan), None, str(bilan))])
    assert m["v1"]["fortes"] == {"relues": 1} and m["v1"]["decisions_otsoa"] == 1
