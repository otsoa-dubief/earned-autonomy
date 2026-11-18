"""Lance `tau2 run` en forçant l'évaluation ENV (état de la base) : aucun juge IA n'est appelé.

Le CLI de tau2 n'expose pas le type d'évaluation ; en mode ALL, les tâches retail
(reward_basis NL_ASSERTION) appelleraient un juge OpenAI codé en dur (gpt-5.4-mini).
Usage : <venv tau2>/bin/python banc/tau2_sans_juge.py run --domain retail ... (mêmes arguments que `tau2`).

Capture de l'usage : un callback de succès LiteLLM (banc/usage_tau2.py) ajoute une ligne JSON par appel (jetons, jetons de
cache, jamais de contenu) au fichier désigné par PILOTE_USAGE_FILE, si cette variable est définie. Sans elle : aucun effet.
"""
import functools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tau2.runner.batch as batch
from tau2.evaluator.evaluator import EvaluationType

batch.run_tasks = functools.partial(batch.run_tasks, evaluation_type=EvaluationType.ENV)

from tau2.cli import main  # noqa: E402

import litellm  # noqa: E402
import usage_tau2  # noqa: E402

usage_tau2.installer(litellm)  # après l'import de tau2, qui remet litellm.success_callback à []

if __name__ == "__main__":
    sys.argv[0] = "tau2"
    main()
