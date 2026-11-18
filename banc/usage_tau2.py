"""Capture précise de l'usage des appels LiteLLM de tau2 (jetons de cache compris).

tau2 n'enregistre par appel que `prompt_tokens` et `completion_tokens`. `callback_succes` est un callback de succès
LiteLLM : si la variable PILOTE_USAGE_FILE est définie, il ajoute UNE ligne JSON par appel à ce fichier :
{"modele", "modele_renvoye", "prompt_tokens", "completion_tokens", "cache_creation_input_tokens",
"cache_read_input_tokens", "horodatage"}.
Jamais de contenu de message, jamais de clé. Une réponse sans usage lisible donne des null (lus ensuite comme « usage
illisible » par banc/cout_v2.py : arrêt). La capture ne casse jamais l'appel.

`modele` est le modèle demandé ; `modele_renvoye` est le nom que l'API a renvoyé (`response.model`, null s'il manque),
noté pour repérer un changement silencieux chez le fournisseur (PLAN_EXPERIENCE.md, 2.2 et 2.5, point 6 ; lu par
banc/lanceur.py). Pour Anthropic, LiteLLM 1.81.11 le recopie de la réponse (llms/anthropic/chat/transformation.py,
`model_response.model = completion_response["model"]`) ; avec `mock_response` (essai à blanc), il y met le modèle demandé.

Contrat vérifié dans litellm 1.81.11 (llms/anthropic/chat/transformation.py, calculate_usage) : pour Anthropic,
`usage.prompt_tokens` = input_tokens + cache_creation_input_tokens + cache_read_input_tokens, donc il INCLUT déjà les
jetons de cache (taille totale de l'invite) ; le reste non caché = prompt_tokens - écriture - lecture. Module sans
dépendance à litellm ni à tau2 : testable hors du venv des bancs.
"""
import json
import os
import threading
from datetime import datetime

_VERROU = threading.Lock()


def _entier(x):
    return x if isinstance(x, int) and not isinstance(x, bool) and x >= 0 else None


def _cache(usage, nom, detail):
    v = getattr(usage, nom, None)
    if v is None:
        v = getattr(getattr(usage, "prompt_tokens_details", None), detail, None)
    return 0 if v is None else _entier(v)


def _nom(x):
    return x if isinstance(x, str) and x else None


def ligne_usage(modele, reponse) -> dict:
    usage = getattr(reponse, "usage", None)
    return {
        "modele": modele if isinstance(modele, str) else None,
        "modele_renvoye": _nom(getattr(reponse, "model", None)),
        "prompt_tokens": _entier(getattr(usage, "prompt_tokens", None)),
        "completion_tokens": _entier(getattr(usage, "completion_tokens", None)),
        "cache_creation_input_tokens": _cache(usage, "cache_creation_input_tokens", "cache_creation_tokens"),
        "cache_read_input_tokens": _cache(usage, "cache_read_input_tokens", "cached_tokens"),
        "horodatage": datetime.now().isoformat(timespec="milliseconds"),
    }


def callback_succes(kwargs, reponse, debut=None, fin=None) -> None:
    chemin = os.environ.get("PILOTE_USAGE_FILE")
    if not chemin:
        return
    try:
        ligne = json.dumps(ligne_usage((kwargs or {}).get("model"), reponse))
        with _VERROU:
            with open(chemin, "a", encoding="utf-8") as fh:
                fh.write(ligne + "\n")
    except Exception:  # l'absence de ligne sera détectée au croisement avec results.json
        pass


def installer(litellm) -> None:
    """Enregistre le callback une seule fois."""
    if callback_succes not in litellm.success_callback:
        litellm.success_callback.append(callback_succes)
