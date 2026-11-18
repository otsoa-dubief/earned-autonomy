"""Cellules jugées de B-tout portées par une seule tâche, aux volumes du plan (rapport du contrôle 3, 9.3, point 5).

Diagnostic sans effet sur le moteur : rejoue des répétitions du contrôle 3 (mêmes graines que `resultats_v5/`, donc
mêmes étiquettes) et relève, pour chaque cellule jugée du point 1 de B-tout, le nombre de tâches porteuses, si le
bootstrap y varie, et le verdict.

Usage (depuis simulation/) :
    env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/une_tache/une_tache.py --lancer
    … --resumer
Sorties : `une_tache.jsonl`, `une_tache.md`.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import Counter, defaultdict  # noqa: E402
from multiprocessing import get_context  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(ICI, "..", "..")))

import numpy as np  # noqa: E402

from controle3 import harnais as H  # noqa: E402
from controle3 import lancer as L  # noqa: E402
from controle3 import mondes as MD  # noqa: E402
from rejeu import analyse as AN  # noqa: E402
from rejeu import config_rejeu as CR  # noqa: E402
from rejeu import decision as DE  # noqa: E402
from rejeu import pipeline as PL  # noqa: E402
from rejeu import preuves as PR  # noqa: E402

# mondes aux volumes du plan où B-tout tient son budget, répétitions 0 à 11 de chacun (appariées à resultats_v5/)
MONDES = ("A", "E", "D-piege")
REPS = 12
PROCESSUS = 12
SORTIE = os.path.join(ICI, "une_tache.jsonl")


def une(args) -> dict:
    nom, rep = args
    t0 = time.time()
    m, p, cfg = MD.MONDES_PAR_NOM[nom], L.parametres(), H.config()
    g_gen, g_moteur = H.graine_repetition(p, m, rep).spawn(2)
    g = MD.generer(m, np.random.default_rng(g_gen), cfg)
    e = g["entrees"]
    prep = PR.preparer(e, "confirmes")
    G0 = int(g_moteur.generate_state(1, np.uint64)[0] >> np.uint64(1))
    reg = AN.Reglages(G0=G0, R0=p.R0, B=p.B, K=p.K, tranche=p.tranche, valeurs_e=(CR.E_PRINCIPAL,),
                      noms_regles=("B-tout",), choix=H.choix_methode())
    an = PL.analyser(e, prep, cfg, reg, g["conf"], g["cal"], processus=1, regles_imposees=H.regles_monde(m, cfg))
    dec = DE.decider(an, DE.point0(e, prep))
    cel = [dict(famille="/".join(map(str, c["famille"])), niveau=c["niveau"], porteuses=int(c["porteuses"]),
                G=int(c["G"]), ecritures=int(c["ecritures_niveau"]), centre_sur_budget=float(c["centre"] / c["budget"]),
                sans_variation=bool(abs(c.get("borne_maxt", np.nan) - c["centre"]) < 1e-12),
                verdict=c["verdict"])
           for c in dec["point1"]["cellules"] if c["statut"] == DE.JUGEE]
    return dict(monde=nom, rep=int(rep), etiquette=dec["etiquette"], cellules=cel, duree=round(time.time() - t0, 1))


def lancer() -> None:
    taches = [(n, r) for r in range(REPS) for n in MONDES]
    with get_context("spawn").Pool(PROCESSUS) as pool, open(SORTIE, "w", encoding="utf-8") as f:
        t0 = time.time()
        for i, r in enumerate(pool.imap_unordered(une, taches), 1):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            print(f"[{time.time() - t0:6.0f} s] {i}/{len(taches)} {r['monde']} {r['rep']} {r['etiquette']}", flush=True)
    resumer()


def resumer() -> None:
    with open(SORTIE, encoding="utf-8") as f:
        rs = [json.loads(l) for l in f if l.strip()]
    out = ["# Cellules jugées de B-tout portées par une seule tâche (sorties de `une_tache.py`)", ""]
    par_monde = defaultdict(list)
    for r in rs:
        par_monde[r["monde"]].append(r)
    out += ["| Monde | répétitions | avec ≥ 1 cellule jugée à une tâche porteuse | dont sans variation bootstrap | "
            "dont estimation > 0 | dépassement établi sur une telle cellule |", "|---|---|---|---|---|---|"]
    lieux = Counter()
    ecr = []
    for nom in MONDES:
        l = par_monde.get(nom, [])
        une_t = [r for r in l if any(c["porteuses"] == 1 for c in r["cellules"])]
        sv = [r for r in une_t if any(c["porteuses"] == 1 and c["sans_variation"] for c in r["cellules"])]
        pos = [r for r in une_t if any(c["porteuses"] == 1 and c["centre_sur_budget"] > 0 for c in r["cellules"])]
        et = [r for r in une_t if any(c["porteuses"] == 1 and c["verdict"] == DE.ETABLI for c in r["cellules"])]
        out.append(f"| {nom} | {len(l)} | {len(une_t)} | {len(sv)} | {len(pos)} | {len(et)} |")
        for r in une_t:
            for c in r["cellules"]:
                if c["porteuses"] == 1:
                    lieux[(c["famille"].split("/")[0], c["famille"].split("/")[1], c["niveau"])] += 1
                    ecr.append(c["ecritures"])
    out += ["", "Lieux des cellules jugées à une tâche porteuse (genre, environnement, niveau : cellules) : "
            + ", ".join(f"{g} {e} {n} : {k}" for (g, e, n), k in sorted(lieux.items())) + "."]
    if ecr:
        out += ["", f"Écritures du niveau dans ces cellules : médiane {int(np.median(ecr))}, de {min(ecr)} à {max(ecr)}."]
    with open(os.path.join(ICI, "une_tache.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--lancer", action="store_true")
    g.add_argument("--resumer", action="store_true")
    a = p.parse_args(argv)
    lancer() if a.lancer else resumer()
    return 0


if __name__ == "__main__":
    sys.exit(main())
