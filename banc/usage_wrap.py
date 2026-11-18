"""Capture de l'usage en jetons des appels WorkBench, sans changer leur comportement.

WorkBench ne garde ni jetons ni coût. `envelopper(original, chemin)` rend une fonction qui appelle
`original` à l'identique (mêmes arguments, même valeur rendue, même exception) et ajoute une ligne
JSON au fichier `chemin` après chaque réponse : {"modele", "modele_renvoye", "prompt_tokens", "completion_tokens"}.
Une réponse sans usage lisible donne des valeurs null (le pilote l'interprète comme « usage illisible »).
`modele_renvoye` est le nom de modèle renvoyé par l'API (`model` de la réponse au format OpenAI, null s'il manque),
noté pour repérer un changement silencieux chez le fournisseur (PLAN_EXPERIENCE.md, 2.2 et 2.5, point 6).
Aucune clé ni contenu de message n'est écrit. Module sans dépendance aux bancs : testable hors du venv WorkBench.
"""
import json
import threading

_VERROU = threading.Lock()


def _entier(x):
    return x if isinstance(x, int) and not isinstance(x, bool) and x >= 0 else None


def _nom(x):
    return x if isinstance(x, str) and x else None


def ligne_usage(modele, reponse):
    usage = getattr(reponse, "usage", None)
    return {
        "modele": modele,
        "modele_renvoye": _nom(getattr(reponse, "model", None)),
        "prompt_tokens": _entier(getattr(usage, "prompt_tokens", None)),
        "completion_tokens": _entier(getattr(usage, "completion_tokens", None)),
    }


def envelopper(original, chemin):
    def enveloppe(client, **kwargs):
        reponse = original(client, **kwargs)
        try:
            ligne = json.dumps(ligne_usage(kwargs.get("model"), reponse))
            with _VERROU:
                with open(chemin, "a", encoding="utf-8") as fh:
                    fh.write(ligne + "\n")
        except Exception:  # la capture ne doit jamais casser l'appel ; l'absence de ligne sera détectée
            pass
        return reponse

    enveloppe.__wrapped__ = original
    return enveloppe
