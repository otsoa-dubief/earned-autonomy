"""Recalcul hors ligne du contrôle d'état final τ-bench d'une partie (évaluation ENV, aucun juge, aucun appel de modèle).

À lancer avec le python de externe/tau2-bench/.venv, clés retirées :  python reussite_tau2_etat.py <results.json>
Affiche une ligne JSON : {"db_match": true|false}. Sert seulement quand reward_info.db_check est absent
(terminaison prématurée : le banc met reward=0 sans contrôler la base).
"""
import json
import sys
from pathlib import Path

from tau2.data_model.simulation import Results
from tau2.evaluator.evaluator_env import EnvironmentEvaluator
from tau2.registry import registry


def recalculer(chemin):
    res = Results.load(Path(chemin))
    sim = res.simulations[0]
    task = next(t for t in res.tasks if str(t.id) == str(sim.task_id))
    domaine = res.info.environment_info.domain_name
    kwargs = {}
    rc = getattr(res.info, "retrieval_config", None)
    if rc is not None:
        kwargs["retrieval_variant"] = rc
        kwargs["task"] = task
        rk = dict(getattr(res.info, "retrieval_config_kwargs", None) or {})
        if rk:
            kwargs["retrieval_kwargs"] = rk
    ri = EnvironmentEvaluator.calculate_reward(
        environment_constructor=registry.get_env_constructor(domaine),
        task=task, full_trajectory=sim.messages, env_kwargs=kwargs, strict_replay=False,
    )
    return {"db_match": bool(ri.db_check.db_match)}


if __name__ == "__main__":
    print(json.dumps(recalculer(sys.argv[1])))
