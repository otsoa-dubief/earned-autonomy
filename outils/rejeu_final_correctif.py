"""Rejeu final avec un seul correctif en mémoire, sans modifier le code figé (17/11/2026).

Le rejeu final lancé le 17/11 avec la commande déposée sur OSF (cusv6) a échoué au moment d'écrire `resistance.csv` :
`simulation/rejeu/sorties.py`, `lignes_resistance`, passe à `dict()` deux clés `mode` à la fois, le nom du test de
résistance et le champ `mode` de `_fam()` (TypeError). Le cas n'apparaît que lorsque des cellules des tests de
résistance sont jugées, ce qui n'arrivait jamais au pilote.

Le code figé n'est pas modifié (`bout_en_bout.py` refuse de tourner si le dépôt diffère du manifeste du gel du plan).
Ce script remplace en mémoire la seule fonction `lignes_resistance` par une copie où le champ `mode` de `_fam()`
s'appelle `mode_scenario`, puis appelle `rejeu.bout_en_bout.main` avec exactement les arguments de la commande
déposée. Le correctif ne touche que les lignes de `resistance.csv`, qui sont sans effet sur l'étiquette (plan 5.11).

    cd ROOT/simulation; .venv/bin/python ../outils/rejeu_final_correctif.py <arguments de la commande déposée>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "simulation"))
from rejeu import bout_en_bout as BE  # noqa: E402
from rejeu import sorties as SO  # noqa: E402

DE = SO.DE


def lignes_resistance(modes: dict, alertes: list) -> list:
    lignes = []
    for mode, (an, e) in modes.items():
        for regle in an.reglages.noms_regles:
            for c in DE.cellules(an, regle, e):
                if c["statut"] != DE.JUGEE:
                    continue
                fam = {("mode_scenario" if k == "mode" else k): v for k, v in SO._fam(c["famille"]).items()}
                lignes.append(dict(mode=mode, **fam, regle=regle, e=e, niveau=c["niveau"],
                                   exces_100_ecritures=c["centre"], budget=c["budget"], lo=c["lo"], hi=c["hi"],
                                   verdict=c["verdict"], etabli=c.get("etabli", ""),
                                   rapport_hi=c["hi"] / c["budget"] if c["hi"] == c["hi"] else float("nan")))
        for regle, (n, w) in DE.bilan_mode(an, e).items():
            lignes.append(dict(mode=mode, type_suite="bilan du mode", regle=regle, echecs=n, pire_rapport_hi=w,
                               alerte=any(a["mode"] == mode for a in alertes) if regle == "B-tout" else ""))
    return lignes


SO.lignes_resistance = lignes_resistance

if __name__ == "__main__":
    sys.exit(BE.main(sys.argv[1:]))
