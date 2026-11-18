"""Gel de l'exploration E1 (PLAN_EXPLORATION_E1.md, section 6) : empreintes sha256 du plan et du code.

Usage : .venv/bin/python gel_e1.py            écrit GEL_E1.txt (date, heure, empreintes)
        .venv/bin/python gel_e1.py --verifier  compare le dossier à GEL_E1.txt (code de sortie 1 si écart)
executer_e1.py --verifier-gel refuse de lancer la grille si le code a changé depuis le gel.
"""
import glob
import hashlib
import os
import sys
import time

ICI = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ICI, "GEL_E1.txt")


def fichiers():
    """Le plan, tout le code Python (tests et explorations compris) et l'étalonnage d'A-dégâts."""
    noms = ["PLAN_EXPLORATION_E1.md", "etalonnage_e1.json"]
    for motif in ("*.py", "tests/*.py", "explorations/*.py"):
        noms += sorted(os.path.relpath(p, ICI) for p in glob.glob(os.path.join(ICI, motif)))
    return noms


def empreinte(rel):
    with open(os.path.join(ICI, rel), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def ecrire():
    lignes = [f"# Gel de l'exploration E1 : {time.strftime('%Y-%m-%d %H:%M:%S %z')}",
              "# sha256 du plan et du code, écrit avant la grille complète (PLAN_EXPLORATION_E1.md, section 6).",
              "# Vérification : .venv/bin/python gel_e1.py --verifier"]
    lignes += [f"{empreinte(n)}  {n}" for n in fichiers()]
    with open(FICHIER, "w") as f:
        f.write("\n".join(lignes) + "\n")
    print(f"écrit {FICHIER} ({len(lignes) - 3} fichiers)")


def lire():
    att = {}
    with open(FICHIER) as f:
        for l in f:
            if l.startswith("#") or not l.strip():
                continue
            h, n = l.rstrip("\n").split("  ", 1)
            att[n] = h
    return att


def verifier() -> list:
    att = lire()
    ecarts = [f"modifié : {n}" for n, h in att.items() if not os.path.exists(os.path.join(ICI, n)) or empreinte(n) != h]
    ecarts += [f"nouveau, hors gel : {n}" for n in fichiers() if n not in att]
    return ecarts


if __name__ == "__main__":
    if "--verifier" in sys.argv:
        e = verifier()
        print("\n".join(e) if e else "conforme au gel")
        sys.exit(1 if e else 0)
    ecrire()
