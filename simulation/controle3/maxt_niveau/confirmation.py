"""Niveau du max-T : mesure de confirmation dans N1 (méthode : `CONFIRMATION.md`, ce dossier, écrite avant le calcul).

Usage (depuis simulation/) :
    env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/maxt_niveau/confirmation.py --lancer
    … --evaluer      (relit les données, refait les tableaux)
Sorties : `donnees/N1c.pkl` (non versionné, empreinte dans `confirmation_meta.json`), `confirmation.csv`,
`confirmation_resultats.md` (jamais `confirmation.md` : sur un disque insensible à la casse, c'est `CONFIRMATION.md`, la méthode).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import csv  # noqa: E402
import json  # noqa: E402
import pickle  # noqa: E402
import platform  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import get_context  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

import numpy as np  # noqa: E402

import maxt_niveau as MN  # noqa: E402

# CONFIRMATION.md, sections 2 et 3
RANG = 10
REPETITIONS = 400
REGIME, MONDE = "N1c", "A"
DONNEES = os.path.join(MN.DONNEES, f"{REGIME}.pkl")
PROCESSUS = 8   # au lieu des 12 de la mesure, pour laisser la machine utilisable (résultats inchangés : graine par tirage)
META = os.path.join(ICI, "confirmation_meta.json")
# tirages antérieurs, mêmes conditions (monde A, hypothèse nulle complète, réglages du contrôle 3), sur 200 répétitions
ANTERIEURS = {"F0": ((42, 200, "relecture C13, C1, preuve 4"), (37, 200, "vérification du coordinateur")),
              "F1": ((15, 200, "relecture C13, C1, preuve 4 (T* recentré)"),
                     (15, 200, "vérification du coordinateur (T* recentré)"))}


def taches() -> list:
    return [(REGIME, RANG, MONDE, rep) for rep in range(REPETITIONS)]


def mesure_n1() -> dict:
    """Rejets de chaque formule en N1 dans la mesure préenregistrée (maxt_niveau.csv)."""
    with open(os.path.join(ICI, "maxt_niveau.csv"), encoding="utf-8") as f:
        return {r["formule"]: (int(r["rejets"]), int(r["n"])) for r in csv.DictReader(f) if r["regime"] == "N1"}


def cumuls(nouveaux: dict, mesure: dict) -> list:
    """Une ligne par formule : tirage neuf, puis cumul (mesure, tirages antérieurs, tirage neuf)."""
    lignes = []
    for fo in MN.FORMULES:
        k, n = nouveaux[fo]
        sources = [(mesure[fo][0], mesure[fo][1], "mesure préenregistrée")] + list(ANTERIEURS.get(fo, ()))
        kc, nc = k + sum(s[0] for s in sources), n + sum(s[1] for s in sources)
        lo, hi = MN._wilson(k, n)
        clo, chi = MN._wilson(kc, nc)
        lignes.append(dict(formule=fo, rejets=k, n=n, part=k / n, wilson_bas=lo, wilson_haut=hi, rejets_cumul=kc,
                           n_cumul=nc, part_cumul=kc / nc, cumul_wilson_bas=clo, cumul_wilson_haut=chi,
                           sources_cumul=" ; ".join(f"{a}/{b} ({c})" for a, b, c in sources)))
    return lignes


def lancer() -> None:
    if os.path.exists(META):
        sys.exit("confirmation_meta.json existe : la mesure ne se relance pas par-dessus.")
    os.makedirs(MN.DONNEES, exist_ok=True)
    meta = dict(statut="en cours", debut=time.strftime("%Y-%m-%d %H:%M:%S"), graine=MN.GRAINE, rang=RANG,
                repetitions=REPETITIONS, monde=MONDE, python=platform.python_version(), numpy=np.__version__,
                empreintes={n: MN._sha(os.path.join(ICI, n)) for n in ("CONFIRMATION.md", "confirmation.py",
                                                                       "maxt_niveau.py")})
    with open(META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    t0 = time.time()
    res = []
    with get_context("spawn").Pool(PROCESSUS) as pool:
        for i, r in enumerate(pool.imap_unordered(MN.une, taches()), 1):
            res.append(r)
            if i % 12 == 0 or i == REPETITIONS:
                print(f"[{time.time() - t0:6.0f} s] {i}/{REPETITIONS}", flush=True)
    with open(DONNEES, "wb") as f:
        pickle.dump(sorted(res, key=lambda x: x["rep"]), f)
    meta.update(statut="terminé", fin=time.strftime("%Y-%m-%d %H:%M:%S"), duree_s=round(time.time() - t0, 1),
                donnees=MN._sha(DONNEES))
    with open(META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    evaluer()


def ecrire_sortie(nom: str, contenu: str) -> str:
    """Écrit `nom` dans ce dossier ; refuse tout nom égal, sans tenir compte de la casse, à un autre fichier existant."""
    for existant in os.listdir(ICI):
        if existant.lower() == nom.lower() and existant != nom:
            raise RuntimeError(f"refus d'écrire {nom} : le fichier {existant} existe déjà (noms égaux à la casse près)")
    with open(os.path.join(ICI, nom), "w", encoding="utf-8") as f:
        f.write(contenu)
    return os.path.join(ICI, nom)


def evaluer() -> None:
    with open(DONNEES, "rb") as f:
        reps = pickle.load(f)
    d = MN.decisions(reps, True, RANG)
    nouveaux = {fo: (sum(d["famille"][fo]), len(d["famille"][fo])) for fo in MN.FORMULES}
    lignes = cumuls(nouveaux, mesure_n1())
    with open(os.path.join(ICI, "confirmation.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
        w.writeheader()
        w.writerows(lignes)
    out = ["# Niveau du max-T : confirmation dans N1 (sorties de `confirmation.py`)", "",
           "| Formule | Tirage neuf | Part | IC 95 % (Wilson) | Cumul | Part cumulée | IC 95 % (Wilson) |",
           "|---|---|---|---|---|---|---|"]
    out += [f"| {l['formule']} | {l['rejets']}/{l['n']} | {100 * l['part']:.1f} % | {100 * l['wilson_bas']:.1f}–"
            f"{100 * l['wilson_haut']:.1f} % | {l['rejets_cumul']}/{l['n_cumul']} | {100 * l['part_cumul']:.1f} % | "
            f"{100 * l['cumul_wilson_bas']:.1f}–{100 * l['cumul_wilson_haut']:.1f} % |" for l in lignes]
    out += ["", "Sources du cumul :"] + [f"- {l['formule']} : {l['sources_cumul']} ; tirage neuf {l['rejets']}/{l['n']}"
                                         for l in lignes]
    ecrire_sortie("confirmation_resultats.md", "\n".join(out) + "\n")
    print("\n".join(out))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--lancer", action="store_true")
    g.add_argument("--evaluer", action="store_true")
    a = p.parse_args(argv)
    lancer() if a.lancer else evaluer()
    return 0


if __name__ == "__main__":
    sys.exit(main())
