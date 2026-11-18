"""R12 : une erreur de l'agent dans WorkBench devient un « échec technique » : relancée, puis exclue.

Les outils de WorkBench ne rattrapent pas les exceptions Python (src/tools/tool.py, Tool.__call__ ; run_agent_structured
appelle t(**str_input) sans try). Un argument mal formé (date illisible pour calendar.search_events, durée non numérique
écrite plus tôt par calendar.create_event, nom d'argument inventé) lève une exception ; WorkBench écrit son texte dans
le champ `error` ; le lanceur classe tout texte inconnu de ce champ en échec technique (choix 14) : la partie est
rejouée (une seconde chance donnée à l'agent), puis exclue. L'erreur de l'agent disparaît des données.

Aucun appel : la réponse du modèle est simulée comme dans banc/workbench_pilote.py (PILOTE_HORS_LIGNE=2).

    cd ROOT/externe/WorkBench
    env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u OPENROUTER_API_KEY \
        .venv/bin/python ../../revues/code/lanceur/demo_workbench_exception_outil.py
"""
import os
import sys
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.insert(0, os.getcwd())
import src.evals.agent as agent  # noqa: E402
import src.evals.inference as inf  # noqa: E402

RACINE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RACINE / "banc"))
import lanceur as L  # noqa: E402

agent.MODEL_REGISTRY["claude-haiku-5-5"] = agent.ModelConfig("anthropic/claude-haiku-5-5", False, "anthropic")
agent.resolve_route = lambda m: agent.Route(m, "hors-ligne", "aucune", "hors-ligne", False)
agent._get_openai_client = lambda api_key, base_url: None


def reponse_factice(client, **kwargs):
    """Premier tour : l'agent cherche les rendez-vous « à partir de la semaine prochaine » (date en toutes lettres)."""
    if not any(m.get("role") == "tool" for m in kwargs["messages"]):
        tc = NS(type="function", id="c1",
                function=NS(name="calendar_search_events", arguments='{"time_min": "next week"}'))
        msg = NS(content="", tool_calls=[tc])
    else:
        msg = NS(content="fait", tool_calls=None)
    return NS(choices=[NS(message=msg)], usage=NS(prompt_tokens=10, completion_tokens=2), model=kwargs.get("model"))


agent._create_with_deadline = reponse_factice
outils = inf.get_toolkits(list(inf._TOOLKIT_MAP))
r = inf._run_single_task(0, "Quels sont mes rendez-vous la semaine prochaine ?", "claude-haiku-5-5", outils, "p",
                         False, True)
print("WorkBench : error =", repr(r["error"][:120]), "; function_calls =", r["function_calls"])
print("lanceur.classer :", L.classer({"env": "WorkBench"}, {"ok": True, "terminaison": r["error"], "trace": True}))
