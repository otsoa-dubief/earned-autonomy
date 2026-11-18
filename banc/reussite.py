"""Taux de tâches réussies d'un dossier de sortie du pilote (REGLE.md, 5 novembre, point 10). Hors ligne, sans juge IA.

    python banc/reussite.py --dossier pilote/etape2/<horodatage>/

Lit parties/ et cout.json ; écrit reussite.csv, reussite.json, reussite.txt dans le dossier (rien d'autre n'est touché).

Verdicts :
- τ-bench : `reward_info.db_check.db_match`, le contrôle d'état de la base du banc (évaluation ENV forcée par tau2_sans_juge.py).
  On n'utilise pas `reward` : il vaut 1.0 à vide quand la base de récompense ne contient pas DB (ex. ACTION seule), et 0.0 sans
  contrôle de base quand la partie s'arrête prématurément (max_steps). Si db_check est absent, l'état final est recalculé avec
  EnvironmentEvaluator du banc installé (reussite_tau2_etat.py).
- WorkBench : `correct` de src.evals.metrics (rejeu des appels prédits et attendus sur bac à sable remis à zéro, comparaison
  d'état, aucune erreur), via reussite_workbench_etat.py.
Limite : « réussie » = l'état final égale celui du chemin attendu par le banc (un seul chemin attendu).
"""
import argparse
import csv
import glob
import json
import os
import subprocess
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANC = os.path.dirname(os.path.abspath(__file__))
WB_DIR = os.path.join(RACINE, "externe", "WorkBench")
WB_PY = os.path.join(WB_DIR, ".venv", "bin", "python")
TAU2_PY = os.path.join(RACINE, "externe", "tau2-bench", ".venv", "bin", "python")
CLES = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "OPENAI_API_KEY", "OPENROUTER_API_KEY", "GOOGLE_API_KEY")

SRC_TAU2 = "τ-bench reward_info.db_check.db_match (contrôle d'état ENV, sans juge)"
SRC_TAU2_RECALCUL = "τ-bench état final recalculé (EnvironmentEvaluator du banc ; db_check absent, terminaison {t})"
SRC_WB = "WorkBench is_correct (rejeu des appels sur bac à sable remis à zéro, comparaison d'état)"
CHAMPS = ["partie", "environnement", "modele", "tache", "reussie", "source"]


def env_sans_cles():
    return {k: v for k, v in os.environ.items() if k not in CLES}


# ---------------------------------------------------------------- τ-bench
def verdict_tau2(reward_info):
    """(True|False|None, source). None = db_check absent : à recalculer."""
    db = (reward_info or {}).get("db_check")
    if db and db.get("db_match") is not None:
        return bool(db["db_match"]), SRC_TAU2
    return None, ""


def recalcul_tau2(results_path):
    p = subprocess.run([TAU2_PY, os.path.join(BANC, "reussite_tau2_etat.py"), os.path.abspath(results_path)],
                       capture_output=True, text=True, env=env_sans_cles(), cwd=os.path.join(RACINE, "externe", "tau2-bench"))
    if p.returncode != 0:
        return None
    return bool(json.loads(p.stdout.strip().splitlines()[-1])["db_match"])


def lire_tau2(results_path):
    with open(results_path, encoding="utf-8") as f:
        sim = json.load(f)["simulations"][0]
    ok, source = verdict_tau2(sim.get("reward_info"))
    if ok is None:
        ok = recalcul_tau2(results_path)
        t = sim.get("termination_reason")
        source = SRC_TAU2_RECALCUL.format(t=t) if ok is not None else f"non évaluable (db_check absent, terminaison {t}) : compté non réussi"
        ok = bool(ok)
    return ok, source


# ---------------------------------------------------------------- WorkBench
def etat_workbench(paires):
    """paires : [(predictions.csv, taches_et_resultats.csv)] -> [{tâche: bool}] (code du banc, venv WorkBench)."""
    sortie = []
    for pred, gt in paires:
        p = subprocess.run([WB_PY, os.path.join(BANC, "reussite_workbench_etat.py"), os.path.abspath(pred), os.path.abspath(gt)],
                           capture_output=True, text=True, env=env_sans_cles(), cwd=WB_DIR)
        if p.returncode != 0:
            raise RuntimeError(f"calcul WorkBench en échec ({pred}) : {p.stderr[-500:]}")
        sortie.append(json.loads(p.stdout.strip().splitlines()[-1]))
    return sortie


# ---------------------------------------------------------------- lecture d'un dossier
def _modele(cout, partie):
    m = partie.get("modele") or cout.get("modele") or ""
    return m.split("/")[-1]


def calculer(dossier):
    with open(os.path.join(dossier, "cout.json"), encoding="utf-8") as f:
        cout = json.load(f)
    par_id = {p["id"]: p for p in cout["parties"]}
    lignes = []
    for chemin in sorted(glob.glob(os.path.join(dossier, "parties", "*"))):
        nom = os.path.basename(chemin)
        pid = nom.split("-", 1)[1]
        meta = par_id.get(pid)
        if meta is None:
            raise ValueError(f"partie {nom} absente de cout.json")
        base = {"partie": nom, "environnement": meta["env"], "modele": _modele(cout, meta), "tache": meta["tache"]}
        if nom.startswith("tau2-"):
            ok, source = lire_tau2(os.path.join(chemin, "results.json"))
        elif nom.startswith("workbench-"):
            csvs = [c for c in glob.glob(os.path.join(chemin, "*.csv"))]
            gts = glob.glob(os.path.join(dossier, "taches", pid, "*_tasks_and_outcomes.csv"))
            if len(csvs) != 1 or len(gts) != 1:
                raise ValueError(f"{nom} : {len(csvs)} prédictions, {len(gts)} fichiers de tâches")
            res = etat_workbench([(csvs[0], gts[0])])[0]
            if len(res) != 1:
                raise ValueError(f"{nom} : {len(res)} tâches (une attendue)")
            ok, source = next(iter(res.values())), SRC_WB
        else:
            raise ValueError(f"partie inconnue : {nom}")
        lignes.append({**base, "reussie": "oui" if ok else "non", "source": source})
    return lignes


# ---------------------------------------------------------------- résumé
def _cpt(rows):
    n = len(rows)
    k = sum(1 for x in rows if x["reussie"] == "oui")
    return {"parties": n, "reussies": k, "part": round(k / n, 4) if n else 0.0}


def resumer(lignes):
    def groupe(*cles):
        out = {}
        for x in lignes:
            d = out
            for c in cles[:-1]:
                d = d.setdefault(x[c], {})
            d.setdefault(x[cles[-1]], []).append(x)
        return out

    def calc(d):
        return {k: (_cpt(v) if isinstance(v, list) else calc(v)) for k, v in sorted(d.items())}

    return {
        "total": _cpt(lignes),
        "par_environnement": calc(groupe("environnement")),
        "par_modele": calc(groupe("modele")),
        "par_environnement_modele": calc(groupe("environnement", "modele")),
    }


def texte_resume(s):
    def f(c):
        return f"{c['reussies']}/{c['parties']} ({c['part'] * 100:.1f} %)"

    out = [f"Taux de tâches réussies (état final, sans juge IA) : {f(s['total'])}", "", "Par environnement :"]
    out += [f"  {e:<10} {f(c)}" for e, c in s["par_environnement"].items()]
    out += ["", "Par modèle :"] + [f"  {m:<20} {f(c)}" for m, c in s["par_modele"].items()]
    out += ["", "Par environnement et modèle :"]
    for e, ms in s["par_environnement_modele"].items():
        out += [f"  {e:<10} {m:<20} {f(c)}" for m, c in ms.items()]
    out += ["", "Réussie = état final identique à celui du chemin unique attendu par le banc."]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dossier", required=True)
    a = ap.parse_args(argv)
    d = os.path.abspath(a.dossier)
    lignes = calculer(d)
    with open(os.path.join(d, "reussite.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CHAMPS)
        w.writeheader()
        w.writerows(lignes)
    s = resumer(lignes)
    with open(os.path.join(d, "reussite.json"), "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
    with open(os.path.join(d, "reussite.txt"), "w", encoding="utf-8") as f:
        f.write(texte_resume(s))
    print(texte_resume(s))
    return 0


if __name__ == "__main__":
    sys.exit(main())
