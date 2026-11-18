"""Réussite WorkBench par comparaison d'état, avec le code du banc (aucun appel de modèle).

À lancer avec le python de externe/WorkBench/.venv, depuis externe/WorkBench (données relatives), clés retirées :
    python reussite_workbench_etat.py <predictions.csv> <taches_et_resultats.csv>
Rejoue les appels prédits et attendus sur un bac à sable remis à zéro (src.evals.metrics.load_and_score_results :
is_correct, et pas d'erreur). Affiche une ligne JSON {tâche: true|false}.
"""
import json
import os
import sys

sys.path.insert(0, os.getcwd())

from src.evals.metrics import load_and_score_results  # noqa: E402

if __name__ == "__main__":
    df = load_and_score_results(sys.argv[1], sys.argv[2])
    print(json.dumps({str(t): bool(c) for t, c in zip(df["task"], df["correct"])}))
