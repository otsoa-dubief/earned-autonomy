"""Contrôle 3 : le générateur des mondes fictifs respecte les volumes du plan (2.3, 2.4, 3.2) et les taux écrits, et
une répétition passe par toute la chaîne jusqu'à l'étiquette."""
import dataclasses

import numpy as np
import pytest

from controle3 import harnais as HA
from controle3 import lancer as LA
from controle3 import mondes as MD
from rejeu import classes as CL
from rejeu import config_rejeu as CR
from rejeu import decision as DE
from rejeu import preuves as PR
from rejeu import suites as SU
from rejeu import types_regle as TY


@pytest.fixture(scope="module")
def generation():
    cfg = HA.config()
    g = MD.generer(MD.MONDES_PAR_NOM["C"], np.random.default_rng(1), cfg)
    return g, PR.preparer(g["entrees"]), cfg


def test_parties_et_partage_du_plan(generation):
    g, _prep, _cfg = generation
    e = g["entrees"]
    assert len(e.parties) == 14266                                        # 2.3 : total des parties
    par = {}
    for p in e.parties:
        par[(p.modele, p.environnement)] = par.get((p.modele, p.environnement), 0) + 1
    for m in MD.MODELES:
        for env in MD.ENVS:
            assert par[(m, env)] == MD.PASSAGES[m][env] * sum(MD.RESERVE[env].values())
    attendu = {"aviation": (20, 20), "commerce": (45, 46), "banque": (38, 39), "WorkBench": (276, 276)}   # 3.2
    for env, (nc, nf) in attendu.items():
        assert (len(g["cal"][env]), len(g["conf"][env])) == (nc, nf)
    wb_cal = {}
    for t in g["cal"]["WorkBench"]:
        wb_cal[t.split(":")[0]] = wb_cal.get(t.split(":")[0], 0) + 1
    assert wb_cal == {s: n // 2 for s, n in MD.RESERVE["WorkBench"].items()}


def test_ecritures_par_partie_de_2_4(generation):
    g, prep, _cfg = generation
    e = g["entrees"]
    for env, mel in MD.MELANGE.items():
        ids = [p.id for p in e.parties if p.environnement == env and p.modele == MD.HAIKU and p.passage == 1]
        for k, r in mel.items():
            # écritures non neutres (les doublons sans effet de la banque et les fausses alertes levées sont neutres)
            n = sum(int(((prep[i].typ == k) & ~prep[i].plaf & (prep[i].reu | prep[i].errp)).sum()) for i in ids)
            # écart type d'une proportion de tâches porteuses ; « inconnu » (1 %) retiré de son type
            sd = np.sqrt(r * (1 - min(r, 1)) / len(ids)) + 0.01
            assert n / len(ids) == pytest.approx(r * 0.99, abs=4 * sd), (env, TY.SIGLES[k])


def _jeu_wb_haiku(monde, graine, cfg):
    g = MD.generer(monde, np.random.default_rng(graine), cfg)
    prep = PR.preparer(g["entrees"])
    return SU.jeu_configuration(prep, g["entrees"], "WorkBench", MD.HAIKU,
                                g["cal"]["WorkBench"] + g["conf"]["WorkBench"], "reserve")


def test_taux_d_erreur_et_correlation():
    cfg = HA.config()
    # taux : monde à 5 × barre, sans hétérogénéité (erreurs binomiales)
    m0 = MD.Monde("essai-rho0", "", "", 5.0, rho=0.0)
    n, x = CL.compter(_jeu_wb_haiku(m0, 1, cfg))[TY.ECR]
    p = m0.taux("WorkBench", MD.HAIKU, TY.ECR, cfg)
    assert p == pytest.approx(5 * float(cfg.barres[("WorkBench", "faible")]))
    assert x / n == pytest.approx(p, abs=4 * np.sqrt(p * (1 - p) / n))
    # ρ intra-tâche du générateur (estimateur d'analyse de variance du moteur), monde à ρ = 0,7
    m7 = MD.Monde("essai-rho7", "", "", 5.0, rho=0.7)
    m_, x_ = zip(*CL.comptes_par_tache(_jeu_wb_haiku(m7, 2, cfg), (TY.ECR,)).values())
    assert CL.rho_anova(m_, x_) == pytest.approx(0.7, abs=0.15)


def test_multiple_du_pire_agent_regulier_en_commerce():
    cfg = HA.config()
    b = float(cfg.barres[("commerce", "faible")])
    N = cfg.n_tout[("commerce", "faible")]
    assert MD.MULTIPLE_PIRE_REGULIER_COMMERCE * b == pytest.approx(1 / (N + 1), rel=0.01)


MONDES_PREMIER_PASSAGE = ("A", "A-tf", "A4", "A-rho0", "A-rho7", "B", "B100", "C", "D", "D-piege", "E", "E-fort", "F1",
                          "F2", "K")


def test_parametres_figes_du_lancement():
    assert (LA.R0, LA.B, LA.K) == (200, 200, 10)
    assert set(LA.REPETITIONS) == {m.nom for m in MD.MONDES}
    assert len(LA.taches_mondes()) == sum(LA.REPETITIONS.values())
    assert all(LA.REPETITIONS[m] >= 20 for m in ("A", "B", "C", "D", "E"))
    # second passage : les mondes du premier gardent leur rang, donc leurs graines (comparaison appariée)
    assert tuple(m.nom for m in MD.MONDES[:len(MONDES_PREMIER_PASSAGE)]) == MONDES_PREMIER_PASSAGE
    assert LA.DOSSIER.endswith("resultats_v8")    # huitième passage (max-T recentré, F3 ; v7 : F1)
    assert not LA.ETUDES_POINT4    # délégabilité et cases critiques : `passage5_r4/` (07/11)
    assert len(LA.taches_critiques()) == len(LA.CRITIQUES) * LA.CRITIQUE_REPETITIONS
    assert len({c for c in LA.cases_deleg()}) == len(LA.cases_deleg())   # une graine par case


def test_generateur_deterministe():
    cfg = HA.config()
    monde = MD.MONDES_PAR_NOM["A"]
    a, b = (PR.resume(PR.preparer(MD.generer(monde, np.random.default_rng(9), cfg)["entrees"])) for _ in range(2))
    assert a == b


def test_une_repetition_de_bout_en_bout():
    """Toute la chaîne aux volumes de l'expérience, en petit (R0 = 4, B = 6, K = 2) : la vague 2 n'a aucun bilan
    d'accord, donc R5 (point 0), et tout le reste est quand même calculé."""
    a = HA.repetition("F2", 0, HA.Parametres(R0=4, B=6, K=2, tranche=6, graine=7))
    assert a["etiquette"] == "R5" and not a["p0"]["relecture_ok"] and a["mention"] == ""
    assert a["volumes"]["parties"] == 14266 and a["p1"]["m"] > 0
    assert set(a["p2"]) == {"tout_valider", "liste_fixe", "tri_risque"}          # Q15 : trois témoins
    assert set(a["oracle"]) == {"cellules_moyen_fort_deleguees", "max_centre_sur_budget"}
    # cinquième passage : valeur centrale ÷ budget de chaque cellule de configuration jugée (lecture de B-seuil)
    assert a["p1"]["centres_config"] and all(isinstance(v, float) for v in a["p1"]["centres_config"].values())


def test_mecanismes_du_quatrieme_passage():
    """N3 (quatrième passage) : ρ = 1 donne des tâches qui échouent toujours ou jamais ; le logit-normal garde la
    moyenne ; le ρ différent d'un type à l'autre est tiré seulement dans les mondes qui le demandent."""
    u = np.random.default_rng(3).random(200_000)
    t1 = MD.taux_par_tache(0.05, 1.0, u)
    assert set(np.unique(t1)) <= {0.0, 1.0} and abs(t1.mean() - 0.05) < 0.003
    for r in (0.3, 0.7, 0.9):
        assert abs(MD.taux_par_tache(0.004, r, u, "logit_normal").mean() - 0.004) < 0.0004
    assert np.array_equal(MD.taux_par_tache(0.004, 0.3, u), MD.taux_par_tache(0.004, 0.3, u, "beta"))
    cfg = HA.config()
    het = MD.MONDES_PAR_NOM["A-het"]
    g1, g2 = (MD.generer(het, np.random.default_rng(5), cfg) for _ in range(2))
    assert g1["verite"]["rho"] == g2["verite"]["rho"]
    assert set(g1["verite"]["rho"].values()) <= set(het.rhos_heterogenes) and len(set(g1["verite"]["rho"].values())) > 1
    # les mondes des passages précédents : rien de tiré en plus, mêmes données qu'avant l'ajout
    a = MD.MONDES_PAR_NOM["A"]
    assert set(MD.generer(a, np.random.default_rng(9), cfg)["verite"]["rho"].values()) == {a.rho}


MONDES_QUATRIEME_PASSAGE = MONDES_PREMIER_PASSAGE + ("D-inerte", "A-rho9", "A-logit", "A-het")


def test_mondes_du_cinquieme_passage():
    """Cinquième passage (07/11) : C attend « R4 ou preuves insuffisantes » (amendement R4) ; B-seuil (dépassement vrai
    d'une fois le budget, RAPPORT 9.3, point 2) et V (volumes réduits, 9.3, point 3) sont ajoutés en dernier : les
    graines des autres mondes ne bougent pas."""
    assert tuple(m.nom for m in MD.MONDES) == MONDES_QUATRIEME_PASSAGE + ("B-seuil", "V")
    c = MD.MONDES_PAR_NOM["C"]
    assert MD.conforme("R4", "", c.attendu) and MD.conforme(DE.PREUVES_INSUFFISANTES, DE.MOTIF_NON_ETABLI, c.attendu)
    assert not MD.conforme("R2", "délégation inférieure à un témoin", c.attendu)
    v = MD.MONDES_PAR_NOM["V"]
    assert v.fraction_reserve == 0.1 and MD.conforme(DE.PREUVES_INSUFFISANTES, DE.MOTIF_AUCUN_JUGEABLE, v.attendu)
    assert not MD.conforme(DE.PREUVES_INSUFFISANTES, DE.MOTIF_NON_ETABLI, v.attendu)
    e, b = MD.MONDES_PAR_NOM["E-fort"], MD.MONDES_PAR_NOM["B-seuil"]
    assert dataclasses.replace(b, nom=e.nom, titre=e.titre, attendu=e.attendu, note=e.note, melange=e.melange) == e
    assert b.melange[0][:2] == ("commerce", "ECR") and 1.0 <= b.melange[0][2] < 4.0 and b.attendu == "confirmée"
    assert all(m.fraction_reserve == 1.0 for m in MD.MONDES if m.nom != "V")


def test_conforme_lit_l_etiquette_et_la_mention_attendues():
    assert MD.conforme("confirmée", "", "confirmée + garantie hors hypothèse")
    assert MD.conforme("R2", "aucune délégation établie", "R2 (aucune délégation établie)")
    assert not MD.conforme("R2", "délégation inférieure à un témoin", "R2 (aucune délégation établie)")
    assert MD.conforme("R1", "", "R1") and not MD.conforme("R4", "", "R1")


def test_reserve_reduite():
    """Monde V : une fraction des tâches de chaque strate de la réserve (au moins deux), partagées moitié-moitié ; à
    fraction 1, le partage et les tirages sont ceux d'avant."""
    toutes, cal, conf = MD.partager(np.random.default_rng(4), "WorkBench", 0.1)
    assert len(toutes) == sum(max(2, round(n * 0.1)) for n in MD.RESERVE["WorkBench"].values())
    assert set(cal).isdisjoint(conf) and set(cal) | set(conf) == set(toutes)
    for s in MD.RESERVE["WorkBench"]:
        assert sum(t.startswith(s + ":") for t in cal) >= 1 and sum(t.startswith(s + ":") for t in conf) >= 1
    r1, r2 = np.random.default_rng(4), np.random.default_rng(4)
    assert MD.partager(r1, "commerce") == MD.partager(r2, "commerce", 1.0) and r1.random() == r2.random()
    g = MD.generer(MD.MONDES_PAR_NOM["V"], np.random.default_rng(2), HA.config())
    assert len(g["cal"]["commerce"]) + len(g["conf"]["commerce"]) == max(2, round(91 * 0.1))


def test_monde_v_de_bout_en_bout():
    """Monde V (un dixième de la réserve), toute la chaîne en petit (R0 = 4, B = 6, K = 2) : aucun type jugeable, donc
    « preuves insuffisantes » avec ce motif ; le point 4 nomme les douze configurations hors du constat de R4."""
    a = HA.repetition("V", 0, HA.Parametres(R0=4, B=6, K=2, tranche=6, graine=7))
    assert a["etiquette"] == DE.PREUVES_INSUFFISANTES and a["mention"] == DE.MOTIF_AUCUN_JUGEABLE
    assert len(a["p4"]["sans_type_jugeable"]) == 12 and not a["p4"]["delegables"]
