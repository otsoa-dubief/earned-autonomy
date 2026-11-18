"""Contre-vérification (choix 28) : une exception WorkBench SANS message est vue comme une partie terminée.

WorkBench écrit `str(e)` dans le champ `error` (src/evals/inference.py:122). Pour une exception sans message
(AssertionError nu, par exemple `assert tc.type == "function"` dans _call_llm_structured, src/evals/agent.py:256), ce
texte est vide : le lanceur classe la partie « terminée » et la garde, alors que WorkBench a perdu ses actions. Aucun
déclencheur trouvé dans les outils (leurs `assert` et `[0]` sont gardés par des contrôles) : limite théorique.

    cd ROOT/externe/WorkBench
    env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u OPENROUTER_API_KEY PILOTE_HORS_LIGNE=2 \
        .venv/bin/python ../../revues/code/lanceur/demo_workbench_exception_muette.py
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
    raise AssertionError()  # réponse d'API inattendue, sans message


inf.run_agent_structured = agent_factice
r = inf._run_single_task(0, "tâche", "claude-haiku-5-5", [], "préfixe", False, True)
print("WorkBench : error =", repr(r["error"]), "; function_calls =", r["function_calls"], "; actions faites :", agies)
print("lanceur.classer :", L.classer({"env": "WorkBench"}, {"ok": True, "terminaison": r["error"], "trace": True}))
