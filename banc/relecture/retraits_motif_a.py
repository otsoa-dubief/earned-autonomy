"""Retraits du motif a, à montrer à Otsoa avant le gel des verdicts (plan, 4.5 ; relecture C13, P9).

Pour chaque vague : `decisions.csv` (registre de Claude, validé par `decisions.py`) et `alertes.json` (correspondance
identifiant -> environnement, tâche). Chaque tâche retirée pour le motif a est listée avec ses alertes, leur cas (a1 à
a4), la preuve et la justification. Aucun nom de modèle et aucun décompte par modèle : le critère du motif a ne porte
que sur la tâche.

Otsoa répond en remplissant `oppositions_motif_a.json` : [[environnement, tâche], …], les tâches qu'il garde. Ce
fichier est inscrit au manifeste du gel des verdicts et lu par le rejeu final (`--oppositions`) : une tâche gardée n'est
pas retirée, et ses alertes levées pour le motif a deviennent des erreurs confirmées. Une tâche dont une alerte est levée
pour le motif a est retirée pour tous les modèles, même si une autre de ses alertes est confirmée (plan, 4.5).

Usage : retraits_motif_a.py --vague <decisions.csv>,<alertes.json> [--vague …] --sortie <dossier>
Sorties : retraits_motif_a.json, retraits_motif_a.md, oppositions_motif_a.json (liste vide, jamais écrasée).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decisions  # noqa: E402


def lister(vagues) -> list:
    """[{environnement, tache, alertes: [{alerte, cas, preuve, justification, vague}]}], trié."""
    par = {}
    for k, (chemin_dec, chemin_alertes) in enumerate(vagues, 1):
        reg = decisions.lire(chemin_dec)
        alertes = {a["id"]: a for a in json.loads(Path(chemin_alertes).read_text(encoding="utf-8"))}
        for aid, d in reg.items():
            if d["decision"] != decisions.LEVEE or d["motif"] != "a":
                continue
            a = alertes[aid]
            cas = re.match(r"\s*(a[1-4])\s*:", d["preuve"], re.I).group(1).lower()
            par.setdefault((a["environnement"], str(a["tache"])), []).append(
                dict(alerte=aid, cas=cas, preuve=d["preuve"], justification=d["justification"], vague=k))
    return [dict(environnement=e, tache=t, alertes=sorted(l, key=lambda x: x["alerte"]))
            for (e, t), l in sorted(par.items())]


def ecrire(sortie: Path, liste: list) -> None:
    sortie.mkdir(parents=True, exist_ok=True)
    (sortie / "retraits_motif_a.json").write_text(json.dumps(liste, ensure_ascii=False, indent=1), encoding="utf-8")
    lignes = ["# Retraits du motif a, à relire avant le gel des verdicts", "",
              f"{len(liste)} tâche(s). Pour en garder une, l'inscrire dans `oppositions_motif_a.json` : "
              "[[environnement, tâche], …].", "",
              "| Environnement | Tâche | Alerte | Cas | Preuve | Justification |", "|---|---|---|---|---|---|"]
    for t in liste:
        for a in t["alertes"]:
            cel = [t["environnement"], t["tache"], a["alerte"], a["cas"], a["preuve"], a["justification"]]
            lignes.append("| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in cel) + " |")
    (sortie / "retraits_motif_a.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    opp = sortie / "oppositions_motif_a.json"
    if not opp.exists():
        opp.write_text("[]\n", encoding="utf-8")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--vague", action="append", required=True, help="decisions.csv,alertes.json")
    p.add_argument("--sortie", required=True, type=Path)
    a = p.parse_args(argv)
    vagues = [tuple(v.split(",", 1)) for v in a.vague]
    liste = lister(vagues)
    ecrire(a.sortie, liste)
    print(f"{len(liste)} tâche(s) retirée(s) pour le motif a : {a.sortie / 'retraits_motif_a.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
