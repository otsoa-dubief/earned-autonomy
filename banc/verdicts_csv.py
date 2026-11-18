"""Transforme un dossier de parties enregistrees en CSV d'actions avec verdicts.

Usage :
    python banc/verdicts_csv.py --dossier PARTIES --tau2 CLONE_TAU2 \
        [--workbench CLONE_WORKBENCH] [--domaine retail] --sortie actions.csv
"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import verdicts  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dossier", required=True, help="dossier de parties (.json, recursif)")
    p.add_argument("--tau2", help="racine du clone tau-bench (taches et types d'outils)")
    p.add_argument("--workbench", help="racine du clone WorkBench")
    p.add_argument("--domaine", help="domaine tau-bench pour une simulation seule sans info")
    p.add_argument("--sortie", required=True, help="fichier CSV a ecrire")
    a = p.parse_args(argv)
    try:
        lignes = verdicts.marquer_doublons_sans_effet(verdicts.actions_dossier(a.dossier, a.tau2, a.workbench, a.domaine))
    except (ValueError, FileNotFoundError) as e:
        print(f"erreur: {e}", file=sys.stderr)
        return 2
    with open(a.sortie, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=verdicts.CHAMPS)
        w.writeheader()
        w.writerows(lignes)
    print(f"{len(lignes)} actions -> {a.sortie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
