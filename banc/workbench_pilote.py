"""Pilote WorkBench : enregistre les modèles Claude 5.5 et, au besoin, coupe tout appel réseau.

À lancer depuis externe/workbench-run/ (données en lien symbolique, sorties dans ./data/results/,
séparées des résultats publiés du dépôt) avec le python de externe/WorkBench/.venv :

    PILOTE_HORS_LIGNE=1 python banc/workbench_pilote.py --model_name claude-haiku-5-5 --tasks_path ... --workers 1
        -> essai à blanc : réponses factices, aucun appel réseau, aucune clé lue.
    python banc/workbench_pilote.py ...      (sans PILOTE_HORS_LIGNE) -> appels réels, ANTHROPIC_API_KEY requise.

Capture de l'usage : si PILOTE_USAGE_FILE est défini, chaque appel au modèle ajoute une ligne JSON
(modele, modele_renvoye, prompt_tokens, completion_tokens) à ce fichier (banc/usage_wrap.py) ; le comportement ne
change pas.
PILOTE_HORS_LIGNE=2 : hors ligne au niveau de l'appel HTTP (fausse réponse avec usage factice), de sorte que la
capture d'usage est exercée de bout en bout sans réseau ni clé.

Réglage supports_temperature : inconnu pour les modèles 5.5 (voir INSTALLATION.md). Valeur par défaut False
(le paramètre temperature n'est pas envoyé) ; PILOTE_TEMPERATURE=1 pour l'envoyer.
"""
import json
import os
import sys

import src.evals.agent as agent

_TEMP = os.environ.get("PILOTE_TEMPERATURE") == "1"
for _nom in ("claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"):
    agent.MODEL_REGISTRY[_nom] = agent.ModelConfig(f"anthropic/{_nom}", _TEMP, "anthropic")

if os.environ.get("PILOTE_HORS_LIGNE") == "1":
    # Aucun client HTTP n'est créé : on remplace la résolution de route et les deux fonctions d'appel.
    agent.resolve_route = lambda m: agent.Route(m, "hors-ligne", "aucune", "hors-ligne", _TEMP)

    def _react(route, system_prompt, human_msg, temperature):
        if "Observation:" not in human_msg:
            return ('Action:```{"action": "company_directory.find_email_address", '
                    '"action_input": {"name": "nadia"}}```')
        return 'Action:```{"action": "Final Answer", "action_input": "fait (réponse factice)"}```'

    def _struct(route, system_prompt, messages, tools_schema, temperature):
        if not any(m.get("role") == "tool" for m in messages):
            return {"content": "", "tool_calls": [{"id": "c1", "name": "company_directory_find_email_address",
                                                   "arguments": {"name": "nadia"}}]}
        return {"content": "fait (réponse factice)", "tool_calls": []}

    agent._call_llm_with_retry = _react
    agent._call_llm_structured_with_retry = _struct

if os.environ.get("PILOTE_HORS_LIGNE") == "2":
    from types import SimpleNamespace as _NS

    agent.resolve_route = lambda m: agent.Route(m, "hors-ligne", "aucune", "hors-ligne", _TEMP)
    agent._get_openai_client = lambda api_key, base_url: None

    def _fausse_reponse(client, **kwargs):
        msgs = kwargs["messages"]
        usage = _NS(prompt_tokens=sum(len(str(m.get("content", ""))) for m in msgs) // 4 + 1, completion_tokens=20)
        if "tools" in kwargs:
            if not any(m.get("role") == "tool" for m in msgs):
                tc = _NS(type="function", id="c1",
                         function=_NS(name="company_directory_find_email_address", arguments='{"name": "nadia"}'))
                msg = _NS(content="", tool_calls=[tc])
            else:
                msg = _NS(content="fait (réponse factice)", tool_calls=None)
        elif "Observation:" not in msgs[-1]["content"]:
            msg = _NS(content='Action:```{"action": "company_directory.find_email_address", '
                              '"action_input": {"name": "nadia"}}```', tool_calls=None)
        else:
            msg = _NS(content='Action:```{"action": "Final Answer", "action_input": "fait (réponse factice)"}```',
                      tool_calls=None)
        # `model` : le nom qu'une vraie API renverrait (ici, le modèle demandé), capté par usage_wrap.py.
        return _NS(choices=[_NS(message=msg)], usage=usage, model=kwargs.get("model"))

    agent._create_with_deadline = _fausse_reponse

if os.environ.get("PILOTE_USAGE_FILE"):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from usage_wrap import envelopper  # noqa: E402

    agent._create_with_deadline = envelopper(agent._create_with_deadline, os.environ["PILOTE_USAGE_FILE"])

from src.cli import inference  # noqa: E402

if __name__ == "__main__":
    sys.exit(inference())
