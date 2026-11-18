"""Coût précis (v2) d'un appel ou d'une partie : prix par modèle, palier Haiku, jetons de cache.

Prix officiels (référence claude-api du 06/10/2026, communiqués par le coordinateur), USD par million de jetons :
- claude-haiku-5-5 : 0,10 entrée / 0,50 sortie pour une invite d'au plus 100 000 jetons ; au-delà 0,50 / 2,50 ;
- claude-sonnet-5-5 : 2 / 10 ; claude-opus-5-5 : 4 / 20.
Cache (durée 5 minutes) : écriture 1,25 x le prix d'entrée ; lecture 0,1 x (Haiku, Sonnet) ou 0,05 x (Opus), appliqués
au prix d'entrée du palier. Taille totale de l'invite = input_tokens + écriture + lecture ; avec LiteLLM,
`prompt_tokens` est déjà cette taille totale (voir usage_tau2.py) : non caché = prompt_tokens - écriture - lecture.
Le palier Haiku se juge sur la taille totale de l'invite (cache compris). Modèle inconnu : ModeleInconnu (ValueError),
donc arrêt. Longueur minimale cachable sur les modèles 5.5 : 512 jetons (en dessous, le cache n'agit pas).
"""
import json
from pathlib import Path

PRIX = {
    # entree, sortie : USD / M jetons ; palier : (seuil d'invite, entree_haut, sortie_haut) ou None ; lecture : multiplicateur
    "claude-haiku-5-5": {"entree": 0.10, "sortie": 0.50, "palier": (100_000, 0.50, 2.50), "lecture": 0.1},
    "claude-sonnet-5-5": {"entree": 2.0, "sortie": 10.0, "palier": None, "lecture": 0.1},
    "claude-opus-5-5": {"entree": 4.0, "sortie": 20.0, "palier": None, "lecture": 0.05},
}
ECRITURE_CACHE = 1.25
CACHE_MIN_JETONS = 512


class ModeleInconnu(ValueError):
    """Modèle absent de la table des prix : le pilote s'arrête."""


def normaliser_modele(nom) -> str:
    if not isinstance(nom, str):
        raise ModeleInconnu(f"modèle inconnu : {nom!r}")
    court = nom[len("anthropic/"):] if nom.startswith("anthropic/") else nom
    if court not in PRIX:
        raise ModeleInconnu(f"modèle inconnu : {nom!r}")
    return court


def _entier_ok(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool) and x >= 0


def cout_appel(modele, prompt_tokens, completion_tokens, cache_ecriture=0, cache_lecture=0) -> dict:
    """{cout, palier_haut, non_caches}. ValueError si une valeur n'est pas un entier >= 0 ou si cache > invite."""
    m = PRIX[normaliser_modele(modele)]
    for v in (prompt_tokens, completion_tokens, cache_ecriture, cache_lecture):
        if not _entier_ok(v):
            raise ValueError(f"usage invalide : {v!r}")
    non_caches = prompt_tokens - cache_ecriture - cache_lecture
    if non_caches < 0:
        raise ValueError("usage incohérent : cache supérieur à l'invite")
    entree, sortie, haut = m["entree"], m["sortie"], False
    if m["palier"] and prompt_tokens > m["palier"][0]:
        entree, sortie, haut = m["palier"][1], m["palier"][2], True
    cout = (non_caches * entree + cache_ecriture * entree * ECRITURE_CACHE + cache_lecture * entree * m["lecture"]
            + completion_tokens * sortie) / 1e6
    return {"cout": cout, "palier_haut": haut, "non_caches": non_caches}


def _appel(l, k) -> dict:
    if not isinstance(l, dict):
        raise ValueError(f"ligne {k} : objet attendu")
    if not isinstance(l.get("modele"), str) or not l["modele"]:
        raise ValueError(f"ligne {k} : modèle absent")
    a = {"modele": l["modele"]}
    for nom, defaut in (("prompt_tokens", None), ("completion_tokens", None),
                        ("cache_creation_input_tokens", 0), ("cache_read_input_tokens", 0)):
        v = l.get(nom, defaut) if nom in l or defaut is not None else None
        if not _entier_ok(v):
            raise ValueError(f"ligne {k} : {nom} illisible")
        a[nom] = v
    return a


def normaliser_appels(lignes) -> list:
    return [_appel(l, k) for k, l in enumerate(lignes)]


def lire_usage_jsonl(chemin) -> list:
    """Appels du JSONL (callback tau2 ou usage_wrap WorkBench). ValueError si absent, vide ou illisible (une ligne
    partielle compte comme illisible). Les champs de cache absents (format WorkBench) valent 0."""
    try:
        texte = Path(chemin).read_text(encoding="utf-8")
        lignes = [json.loads(x) for x in texte.splitlines() if x.strip()]
    except (OSError, ValueError):
        raise ValueError("fichier d'usage illisible ou absent")
    if not lignes:
        raise ValueError("fichier d'usage vide")
    return normaliser_appels(lignes)


def bilan(appels: list, estime: bool = False) -> dict:
    cout, hauts, ent, nc, ce, cl, sor = 0.0, 0, 0, 0, 0, 0, 0
    for a in appels:
        r = cout_appel(a["modele"], a["prompt_tokens"], a["completion_tokens"],
                       a["cache_creation_input_tokens"], a["cache_read_input_tokens"])
        cout += r["cout"]
        hauts += int(r["palier_haut"])
        ent += a["prompt_tokens"]
        nc += r["non_caches"]
        ce += a["cache_creation_input_tokens"]
        cl += a["cache_read_input_tokens"]
        sor += a["completion_tokens"]
    return {"appels": len(appels), "appels_hauts": hauts, "jetons_entree": ent, "jetons_non_caches": nc,
            "cache_ecriture": ce, "cache_lecture": cl, "jetons_sortie": sor, "cout_usd": round(cout, 8), "estime": estime}


def croiser(appels_usage: list, appels_tau2: list) -> None:
    """Contrôle de complétude : le JSONL (facturation réelle) doit couvrir au moins tous les appels que tau2 a enregistrés
    (autant de lignes, au moins autant de jetons d'invite). Plus de lignes = tentatives relancées, permis."""
    if len(appels_usage) < len(appels_tau2):
        raise ValueError(f"usage incomplet : {len(appels_usage)} lignes pour {len(appels_tau2)} appels enregistrés par tau2")
    if sum(a["prompt_tokens"] for a in appels_usage) < sum(p for p, _, _ in appels_tau2):
        raise ValueError("usage incomplet : moins de jetons d'invite que dans results.json")
    if sum(a["completion_tokens"] for a in appels_usage) < sum(c for _, c, _ in appels_tau2):
        raise ValueError("usage incomplet : moins de jetons de sortie que dans results.json")
