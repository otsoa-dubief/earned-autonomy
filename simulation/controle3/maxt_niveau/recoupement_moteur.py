"""Recoupement après la mesure : le moteur corrigé (`rejeu/maxt.py`) contre la formule mesurée qu'il applique, sur les
mêmes répétitions (`donnees/<régime>.pkl`, empreintes dans `meta.json`).

Pour chaque régime de la mesure, on compte les répétitions où au moins un dépassement est établi, selon la formule
mesurée (`maxt_niveau.formule`) et selon le moteur ; puis les écarts de décision et de testabilité, cellule par cellule.
Les budgets sont ceux de la mesure : θ_G de chaque cellule sous l'hypothèse nulle complète (N1, N2), les vrais budgets
ailleurs (P1, P2, P3, P4). La tolérance d'un écart type nul diffère (moteur : quatre epsilon du float32, relecture C13,
C6 ; mesure : racine de l'epsilon du float64) : un écart de testabilité le montrerait.

Usage (depuis simulation/) :
    env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/maxt_niveau/recoupement_moteur.py
Sortie : `recoupement_moteur.txt`.
"""
from __future__ import annotations

import importlib.util
import os
import pickle
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, SIM)

import numpy as np  # noqa: E402

from rejeu import maxt as MX  # noqa: E402

FORMULE = "F3"   # formule appliquée par le moteur (plan, 5.14, point 2 ; F1 jusqu'au commit 5e87ae0)
REGIMES = (("N1", "N1", True), ("N2", "N2", True), ("P3", "N2", False), ("P2", "P2", False), ("P1", "P1", False),
           ("P4", "P4", False))


def _mesure():
    spec = importlib.util.spec_from_file_location("maxt_niveau", os.path.join(ICI, "maxt_niveau.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def recouper() -> list:
    MN = _mesure()
    lignes = [f"Formule mesurée : {FORMULE} ; tolérance du moteur {MX.TOL_RELATIVE:.3e}, de la mesure {MN.TOL:.3e}"]
    for nom, fichier, nulle in REGIMES:
        with open(os.path.join(ICI, "donnees", f"{fichier}.pkl"), "rb") as f:
            reps = pickle.load(f)
        theta = {}
        if nulle:
            acc = {}
            for r in reps:
                for c in r["cellules"]:
                    acc.setdefault(c["cle"], []).append(c["centre"])
            theta = {k: float(np.mean(v)) for k, v in acc.items()}
        fam_mesure = fam_moteur = ecarts_rep = ecarts_cel = ecarts_test = 0
        for r in reps:
            cel = r["cellules"]
            if not cel:
                continue
            est = np.array([c["centre"] for c in cel])
            bud = np.array([theta[c["cle"]] if nulle else c["budget"] for c in cel])
            boot = np.stack([c["boot"] for c in cel], axis=1)
            por = np.array([c["porteuses"] for c in cel])
            mesure = MN.formule(FORMULE, est, boot, bud, por)
            moteur = MX.depassement_etabli(est, boot, bud, porteuses=por)
            fam_mesure += bool(mesure.any())
            fam_moteur += bool(moteur["etabli"].any())
            d = int((mesure != moteur["etabli"]).sum())
            ecarts_cel += d
            ecarts_rep += d > 0
            ecarts_test += int((MN._testables(por, boot.std(axis=0, ddof=1), est, bud) != moteur["testable"]).sum())
        lignes.append(f"{nom} : {len(reps)} répétitions ; au moins un dépassement établi : mesure {fam_mesure}, moteur "
                      f"{fam_moteur} ; écarts de décision : {ecarts_rep} répétitions, {ecarts_cel} cellules ; "
                      f"testabilité différente : {ecarts_test} cellules")
    return lignes


def main() -> int:
    lignes = recouper()
    with open(os.path.join(ICI, "recoupement_moteur.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    print("\n".join(lignes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
