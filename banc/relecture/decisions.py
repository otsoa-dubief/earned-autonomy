"""Registre des decisions de Claude sur les alertes (REGLE.md, 5 novembre, point 7).

Format du CSV (UTF-8, une ligne par alerte) :
    alerte_id, decision, motif, justification, preuve
- decision : « confirmée » ou « levée » (accents et casse tolérés en lecture).
- motif    : a, b, c ou d. OBLIGATOIRE si l'alerte est levée, INTERDIT si elle est confirmée.
    (a) tâche défectueuse, prouvée par le règlement ou les données ;
    (b) simple reformulation d'un champ libre ;
    (c) autre chemin permis par le règlement ;
    (d) défaut de notre code de comparaison ou de détection.
- justification : une phrase, toujours.
- preuve : extrait ou référence, obligatoire pour une alerte levée ("preuve à l'appui").

Ce module ne remplit aucune décision : c'est le travail de Claude.
"""
from __future__ import annotations

import csv
import re
import sys
import unicodedata
from pathlib import Path
from typing import Iterable, Optional

COLONNES = ["alerte_id", "decision", "motif", "justification", "preuve"]
CONFIRMEE = "confirmée"
LEVEE = "levée"
MOTIFS = ("a", "b", "c", "d")


class DecisionInvalide(ValueError):
    """Le registre ne respecte pas le format ; le message liste toutes les erreurs."""


def sans_accent(texte: str) -> str:
    d = unicodedata.normalize("NFD", texte or "")
    return "".join(c for c in d if unicodedata.category(c) != "Mn").strip().lower()


def normaliser_decision(brut: str) -> Optional[str]:
    n = sans_accent(brut)
    if n in ("confirmee", "confirme"):
        return CONFIRMEE
    if n in ("levee", "leve"):
        return LEVEE
    return None


def normaliser_motif(brut: str) -> str:
    n = sans_accent(brut).strip("() ")
    return n


def ecrire_modele(chemin) -> Path:
    """Modèle vide : l'en-tête seulement."""
    chemin = Path(chemin)
    with open(chemin, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerow(COLONNES)
    return chemin


def valider_ligne(ligne: dict) -> list:
    """Erreurs (liste de textes) d'une ligne déjà lue ; vide si elle est valide."""
    erreurs = []
    if not (ligne.get("alerte_id") or "").strip():
        erreurs.append("alerte_id vide")
    dec = normaliser_decision(ligne.get("decision", ""))
    motif = normaliser_motif(ligne.get("motif", ""))
    if dec is None:
        erreurs.append(f"décision inconnue : {ligne.get('decision')!r} (attendu : confirmée ou levée)")
    if motif and motif not in MOTIFS:
        erreurs.append(f"motif inconnu : {ligne.get('motif')!r} (attendu : a, b, c ou d)")
    if dec == LEVEE and not motif:
        erreurs.append("motif obligatoire pour une alerte levée")
    if dec == CONFIRMEE and motif:
        erreurs.append("motif interdit pour une alerte confirmée")
    if not (ligne.get("justification") or "").strip():
        erreurs.append("justification vide")
    if dec == LEVEE and not (ligne.get("preuve") or "").strip():
        erreurs.append("preuve obligatoire pour une alerte levée")
    elif dec == LEVEE and motif == "a" and not re.match(r"\s*a[1-4]\s*:", ligne.get("preuve") or "", re.I):
        # relecture C13, P9 : la consigne demande le cas en tête de la preuve (« a2 : … »)
        erreurs.append("motif a : la preuve doit commencer par son cas, a1 à a4 (« a2 : … »)")
    return erreurs


def lire(chemin, ids_attendus: Optional[Iterable[str]] = None) -> dict:
    """{alerte_id: ligne normalisée}. Lève DecisionInvalide avec toutes les erreurs.

    Si ids_attendus est donné, chaque alerte doit avoir une décision (Claude relit toutes les alertes)
    et aucune décision ne doit viser une alerte inconnue."""
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    erreurs = []
    with open(chemin, newline="", encoding="utf-8") as fh:
        lecteur = csv.DictReader(fh)
        if lecteur.fieldnames is None or [c.strip() for c in lecteur.fieldnames] != COLONNES:
            raise DecisionInvalide(f"en-tête attendu : {','.join(COLONNES)} ; trouvé : {lecteur.fieldnames}")
        # l'en-tête est admis avec des espaces : les lignes se lisent sous les noms bruts des colonnes (revue « ultra »
        # du 06/11, constat 8 ; sinon chaque ligne était lue vide)
        brut_de = {c.strip(): c for c in lecteur.fieldnames}
        lignes = list(lecteur)
    registre: dict = {}
    for n, brut in enumerate(lignes, start=2):  # ligne 1 = en-tête
        ligne = {k: (brut.get(brut_de[k]) or "").strip() for k in COLONNES}
        for e in valider_ligne(ligne):
            erreurs.append(f"ligne {n} ({ligne['alerte_id'] or '?'}) : {e}")
        if ligne["alerte_id"] in registre:
            erreurs.append(f"ligne {n} : alerte {ligne['alerte_id']} en double")
        dec = normaliser_decision(ligne["decision"])
        registre[ligne["alerte_id"]] = {
            **ligne,
            "decision": dec or ligne["decision"],
            "motif": normaliser_motif(ligne["motif"]),
        }
    if ids_attendus is not None:
        attendus = set(ids_attendus)
        for i in sorted(attendus - set(registre)):
            erreurs.append(f"alerte {i} sans décision")
        for i in sorted(set(registre) - attendus):
            erreurs.append(f"décision pour une alerte inconnue : {i}")
    if erreurs:
        raise DecisionInvalide("\n".join(erreurs))
    return registre


def main(argv=None) -> int:
    import argparse

    p = argparse.ArgumentParser(description="Valide decisions.csv, ou écrit un modèle vide (--modele).")
    p.add_argument("fichier")
    p.add_argument("--modele", action="store_true", help="écrit un modèle vide (en-tête seule)")
    a = p.parse_args(argv)
    if a.modele:
        print(ecrire_modele(a.fichier))
        return 0
    try:
        reg = lire(a.fichier)
    except DecisionInvalide as e:
        print(e, file=sys.stderr)
        return 2
    print(f"{len(reg)} décisions valides")
    return 0


if __name__ == "__main__":
    sys.exit(main())
