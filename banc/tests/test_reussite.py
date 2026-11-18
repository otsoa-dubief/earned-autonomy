"""Tests de banc/reussite.py : taux de tâches réussies (état final, sans juge IA, sans appel de modèle)."""
import csv
import json
import os

import pytest

import reussite as r

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WB_PY = os.path.join(RACINE, "externe", "WorkBench", ".venv", "bin", "python")
TAU2_PY = os.path.join(RACINE, "externe", "tau2-bench", ".venv", "bin", "python")

GT_BON = ['email.delete_email.func(email_id="00000479")']
GT_AUTRE = ['email.delete_email.func(email_id="00000070")']


# ---------------------------------------------------------------- τ-bench : choix du champ
def test_tau2_lit_db_match_vrai():
    ri = {"reward": 1.0, "db_check": {"db_match": True, "db_reward": 1.0}, "reward_basis": ["DB"]}
    ok, source = r.verdict_tau2(ri)
    assert ok is True and "db_match" in source


def test_tau2_lit_db_match_faux():
    ri = {"reward": 0.0, "db_check": {"db_match": False, "db_reward": 0.0}, "reward_basis": ["DB"]}
    assert r.verdict_tau2(ri)[0] is False


def test_tau2_ignore_reward_vide_de_sens_quand_base_action_seule():
    # reward vaut 1.0 par produit vide si la base ne contient pas DB ; db_match, lui, dit la vérité
    ri = {"reward": 1.0, "db_check": {"db_match": False, "db_reward": 0.0}, "reward_basis": ["ACTION"]}
    assert r.verdict_tau2(ri)[0] is False


def test_tau2_terminaison_prematuree_sans_db_check_a_recalculer():
    ri = {"reward": 0.0, "db_check": None, "reward_basis": None, "info": {"note": "Simulation terminated prematurely"}}
    assert r.verdict_tau2(ri)[0] is None
    assert r.verdict_tau2(None)[0] is None


# ---------------------------------------------------------------- WorkBench : calcul d'état sur bac à sable
def ecrire_pred(chemin, lignes):
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(["task", "function_calls", "full_response", "error"])
        for tache, appels, err in lignes:
            w.writerow([tache, repr(appels), "AgentResult(output='x')", err])


def ecrire_gt(chemin, lignes):
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(["task", "outcome", "base_template", "chosen_template", "domains"])
        for tache, gt in lignes:
            w.writerow([tache, repr(gt), tache, tache, "['email']"])


@pytest.mark.skipif(not os.path.exists(WB_PY), reason="venv WorkBench absent")
def test_workbench_tache_juste_et_tache_fausse(tmp_path):
    pred, gt = tmp_path / "p.csv", tmp_path / "g.csv"
    ecrire_gt(gt, [("Delete my last email from nadia", GT_BON), ("Delete my other email", GT_BON)])
    ecrire_pred(pred, [
        ("Delete my last email from nadia", ['email.search_emails.func(query="nadia")'] + GT_BON, ""),  # juste (état identique)
        ("Delete my other email", GT_AUTRE, ""),  # fausse (mauvais e-mail supprimé)
    ])
    res = r.etat_workbench([(str(pred), str(gt))])
    assert res[0] == {"Delete my last email from nadia": True, "Delete my other email": False}


@pytest.mark.skipif(not os.path.exists(WB_PY), reason="venv WorkBench absent")
def test_workbench_erreur_ou_aucune_action_est_un_echec(tmp_path):
    pred, gt = tmp_path / "p.csv", tmp_path / "g.csv"
    ecrire_gt(gt, [("t1", GT_BON), ("t2", GT_BON)])
    ecrire_pred(pred, [("t1", GT_BON, "Context window exceeded"), ("t2", [], "")])
    assert r.etat_workbench([(str(pred), str(gt))])[0] == {"t1": False, "t2": False}


# ---------------------------------------------------------------- résumé
def lignes():
    return [
        {"partie": "a", "environnement": "aviation", "modele": "haiku", "tache": "1", "reussie": "oui", "source": "s"},
        {"partie": "b", "environnement": "aviation", "modele": "haiku", "tache": "2", "reussie": "non", "source": "s"},
        {"partie": "c", "environnement": "aviation", "modele": "opus", "tache": "1", "reussie": "oui", "source": "s"},
        {"partie": "d", "environnement": "banque", "modele": "haiku", "tache": "3", "reussie": "non", "source": "s"},
    ]


def test_resume_par_environnement_et_modele():
    s = r.resumer(lignes())
    assert s["total"] == {"parties": 4, "reussies": 2, "part": 0.5}
    assert s["par_environnement_modele"]["aviation"]["haiku"] == {"parties": 2, "reussies": 1, "part": 0.5}
    assert s["par_environnement_modele"]["aviation"]["opus"] == {"parties": 1, "reussies": 1, "part": 1.0}
    assert s["par_environnement"]["aviation"] == {"parties": 3, "reussies": 2, "part": round(2 / 3, 4)}
    assert s["par_modele"]["haiku"] == {"parties": 3, "reussies": 1, "part": round(1 / 3, 4)}
    assert s["par_environnement_modele"]["banque"]["haiku"]["reussies"] == 0


def test_texte_du_resume_contient_les_parts():
    t = r.texte_resume(r.resumer(lignes()))
    assert "aviation" in t and "50" in t


# ---------------------------------------------------------------- bout en bout sur une fausse sortie de pilote
def fausse_sortie(tmp_path):
    d = tmp_path / "sortie"
    ri = lambda ok: {"reward": 1.0 if ok else 0.0, "db_check": {"db_match": ok, "db_reward": 1.0 if ok else 0.0}, "reward_basis": ["DB"]}
    for pid, ok in (("aviation-haiku-1", True), ("aviation-haiku-2", False)):
        p = d / "parties" / f"tau2-{pid}"
        p.mkdir(parents=True)
        (p / "results.json").write_text(json.dumps({"simulations": [{"task_id": "x", "termination_reason": "user_stop", "reward_info": ri(ok)}]}))
    cout = {"parties": [
        {"id": "aviation-haiku-1", "env": "aviation", "modele": "claude-haiku-5-5", "tache": "11", "ok": True},
        {"id": "aviation-haiku-2", "env": "aviation", "modele": "claude-haiku-5-5", "tache": "13", "ok": True},
    ]}
    (d / "cout.json").write_text(json.dumps(cout))
    return d


def test_bout_en_bout_ecrit_les_trois_fichiers(tmp_path):
    d = fausse_sortie(tmp_path)
    assert r.main(["--dossier", str(d)]) == 0
    rows = list(csv.DictReader(open(d / "reussite.csv", encoding="utf-8")))
    assert [(x["partie"], x["reussie"]) for x in rows] == [("tau2-aviation-haiku-1", "oui"), ("tau2-aviation-haiku-2", "non")]
    assert rows[0]["modele"] == "claude-haiku-5-5" and rows[0]["environnement"] == "aviation" and rows[0]["tache"] == "11"
    js = json.load(open(d / "reussite.json", encoding="utf-8"))
    assert js["par_environnement"]["aviation"] == {"parties": 2, "reussies": 1, "part": 0.5}
    assert "aviation" in (d / "reussite.txt").read_text(encoding="utf-8")


def test_modele_de_premier_niveau_quand_la_partie_n_en_porte_pas(tmp_path):
    d = fausse_sortie(tmp_path)
    c = json.load(open(d / "cout.json"))
    for p in c["parties"]:
        del p["modele"]
    c["modele"] = "anthropic/claude-haiku-5-5"
    json.dump(c, open(d / "cout.json", "w"))
    r.main(["--dossier", str(d)])
    rows = list(csv.DictReader(open(d / "reussite.csv", encoding="utf-8")))
    assert rows[0]["modele"] == "claude-haiku-5-5"
