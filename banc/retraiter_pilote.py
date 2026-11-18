"""Recalcule hors ligne les verdicts, le typage et le résumé d'un dossier de pilote après un changement déclaré de
l'instrument (JOURNAL_CHANGEMENTS.md). Aucun appel payant : on relit les parties enregistrées.

Usage :
    python banc/retraiter_pilote.py --dossier pilote/etape2/2026-11-05_07-50-58 --etiquette avant_payment_id

Les quatre fichiers actuels (actions.csv, actions_typees.csv, resume.json, resume.txt) sont d'abord copiés dans
<dossier>/<etiquette>/ (refus si ce sous-dossier existe). Le script affiche ensuite chaque action dont le verdict
ou le motif a changé. Il s'arrête si la liste des actions elle-même a changé.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pilote_etape1 as pe  # noqa: E402
import pilote_etape2 as p2  # noqa: E402

FICHIERS = ("actions.csv", "actions_typees.csv", "resume.json", "resume.txt")


def _lignes(chemin: Path) -> list:
    csv.field_size_limit(sys.maxsize)
    with open(chemin, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def comptable(cout: dict) -> pe.Comptable:
    c = pe.Comptable(cout["plafond_usd"])
    c.cumul, c.arret = cout["cumul_usd"], cout["arret"]
    return c


def retraiter(dossier: Path, etiquette: str) -> list:
    """Retourne [(ligne d'avant, ligne d'après)] pour chaque action dont le verdict ou le motif a changé."""
    sauvegarde = dossier / etiquette
    if sauvegarde.exists():
        raise SystemExit(f"{sauvegarde} existe déjà : choisir une autre étiquette")
    sauvegarde.mkdir()
    for f in FICHIERS:
        shutil.copy2(dossier / f, sauvegarde / f)
    cout = json.loads((dossier / "cout.json").read_text(encoding="utf-8"))
    resume = json.loads((dossier / "resume.json").read_text(encoding="utf-8"))
    compta = comptable(cout)
    if "etape" in cout:  # étape 2 ou 2a
        p2.post_traitement(dossier, cout["parties"], compta, resume["mode"], cout["etape"], resume["cache"],
                           resume["liste_taches_factice"])
    else:  # étape 1
        pe.post_traitement(dossier, cout["parties"], compta, resume["mode"], resume["liste_taches_factice"])
    avant, apres = _lignes(sauvegarde / "actions.csv"), _lignes(dossier / "actions.csv")
    cle = lambda l: (l["partie"], l["rang"], l["outil"], l["arguments"])  # noqa: E731
    if [cle(l) for l in avant] != [cle(l) for l in apres]:
        raise SystemExit("la liste des actions a changé, pas seulement les verdicts : vérifier avant d'aller plus loin")
    return [(a, b) for a, b in zip(avant, apres) if (a["verdict"], a["motif"]) != (b["verdict"], b["motif"])]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dossier", required=True, help="dossier d'un pilote (contient parties/, cout.json, resume.json)")
    p.add_argument("--etiquette", required=True, help="nom du sous-dossier de sauvegarde, par exemple avant_payment_id")
    a = p.parse_args(argv)
    changes = retraiter(Path(a.dossier), a.etiquette)
    print(f"{len(changes)} action(s) changée(s)")
    for av, ap in changes:
        print(f"- {ap['domaine']} tâche {ap['tache']} {ap['modele']} rang {ap['rang']} {ap['outil']} : "
              f"{av['verdict'] or '-'} -> {ap['verdict'] or '-'}" + (f" ({ap['motif']})" if ap["motif"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
