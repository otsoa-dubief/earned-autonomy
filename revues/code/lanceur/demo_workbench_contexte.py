"""R11 : une partie WorkBench finie sur « Context window exceeded » perd toutes ses actions, et le lanceur la garde.

WorkBench (src/evals/inference.py, _run_single_task) ne recopie les actions (`_collect_result`) que si l'agent rend un
résultat ; sur une exception, dont le dépassement de contexte, `function_calls` reste vide, alors que les outils
appelés avant ont déjà agi. Le lanceur classe ce texte en « arrêtée (fenêtre de contexte) » et garde la partie
(classer, choix 14) : une partie gardée sans aucune de ses actions.

Aucun appel : l'agent est remplacé par une fonction qui note une action puis lève l'erreur de contexte.

    cd ROOT/externe/WorkBench
    env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u OPENROUTER_API_KEY PILOTE_HORS_LIGNE=2 \
        .venv/bin/python ../../revues/code/lanceur/demo_workbench_contexte.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.getcwd())
import src.evals.inference as inf  # noqa: E402

RACINE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RACINE / "banc"))
import lanceur as L  # noqa: E402

agies = []


def agent_factice(model_name, tools, task, datetime_prefix, **kw):
    agies.append("email.send_email")  # l'agent a déjà écrit
    raise Exception("Error code: 400 - prompt is too long: 210000 tokens > 200000 maximum")


inf.run_agent_structured = agent_factice
r = inf._run_single_task(0, "tâche", "claude-haiku-5-5", [], "préfixe", False, True)
print("WorkBench : error =", repr(r["error"]), "; function_calls =", r["function_calls"], "; actions faites :", agies)
print("lanceur.classer :", L.classer({"env": "WorkBench"}, {"ok": True, "terminaison": r["error"], "trace": True}))
