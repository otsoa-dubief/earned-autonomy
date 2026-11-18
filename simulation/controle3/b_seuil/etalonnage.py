"""Monde B-seuil : étalonnage de la dérive du commerce (méthode : `METHODE.md`, ce dossier, écrite avant le calcul).

Usage (depuis simulation/) :
    env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/b_seuil/etalonnage.py --grille
    … --verifier D [--rang 10]   12 répétitions à la dérive D
Sorties : `etalonnage.jsonl` (une ligne par répétition, ajoutée), `etalonnage.md` (refait à chaque appel).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import dataclasses  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import get_context  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, SIM)

import numpy as np  # noqa: E402

from controle3 import harnais as H  # noqa: E402
from controle3 import lancer as L  # noqa: E402
from controle3 import mondes as MD  # noqa: E402
from rejeu import analyse as AN  # noqa: E402
from rejeu import config_rejeu as CR  # noqa: E402
from rejeu import decision as DE  # noqa: E402
from rejeu import pipeline as PL  # noqa: E402
from rejeu import preuves as PR  # noqa: E402

GRAINE = 2026110702
GRILLE = (1.0, 1.75, 2.5, 3.25)
REPS_GRILLE, REPS_VERIF = 6, 12
PROCESSUS = 12
SORTIE = os.path.join(ICI, "etalonnage.jsonl")


def monde(d: float) -> MD.Monde:
    """E-fort, dérive du commerce remplacée par d écritures réversibles par partie."""
    return dataclasses.replace(MD.MONDES_PAR_NOM["E-fort"], nom=f"etalonnage-{d:g}", melange=(("commerce", "ECR", d),))


def une(args) -> dict:
    d, rang, rep = args
    t0 = time.time()
    m = monde(d)
    cfg = H.config()
    g_gen, g_moteur = np.random.SeedSequence([GRAINE, int(rang), int(rep)]).spawn(2)
    g = MD.generer(m, np.random.default_rng(g_gen), cfg)
    e = g["entrees"]
    prep = PR.preparer(e, "confirmes")
    G0 = int(g_moteur.generate_state(1, np.uint64)[0] >> np.uint64(1))
    reg = AN.Reglages(G0=G0, R0=L.R0, B=L.B, K=L.K, tranche=L.TRANCHE, valeurs_e=(CR.E_PRINCIPAL,),
                      noms_regles=("B-tout",), choix=H.choix_methode())
    an = PL.analyser(e, prep, cfg, reg, g["conf"], g["cal"], processus=1, regles_imposees=H.regles_monde(m, cfg))
    dec = DE.decider(an, DE.point0(e, prep))
    cel = []
    for c in dec["point1"]["cellules"]:
        f = c["famille"]
        if f[0] == "config" and f[1] == "commerce" and c["niveau"] == "faible":
            cel.append(dict(modele=f[2], statut=c["statut"], centre=float(c.get("centre", float("nan"))),
                            budget=float(c["budget"]), borne=float(c.get("borne_maxt", float("nan"))),
                            verdict=c.get("verdict")))
    return dict(derive=d, rang=int(rang), rep=int(rep), etiquette=dec["etiquette"], p1_tenu=bool(dec["point1"]["tenu"]),
                cellules=cel, duree=round(time.time() - t0, 1))


def rapport(c: dict) -> float:
    return c["centre"] / c["budget"]


def moyenne_rep(r: dict) -> float:
    v = [rapport(c) for c in r["cellules"] if math.isfinite(c["centre"])]
    return float(np.mean(v)) if v else float("nan")


def lancer(taches: list) -> None:
    with get_context("spawn").Pool(PROCESSUS) as pool, open(SORTIE, "a", encoding="utf-8") as f:
        t0 = time.time()
        for i, r in enumerate(pool.imap_unordered(une, taches), 1):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            print(f"[{time.time() - t0:6.0f} s] {i}/{len(taches)} d={r['derive']:g} rep={r['rep']} "
                  f"{moyenne_rep(r):.3f} {r['etiquette']}", flush=True)
    resumer()


def resumer() -> None:
    with open(SORTIE, encoding="utf-8") as f:
        rs = [json.loads(l) for l in f if l.strip()]
    par = {}
    for r in rs:
        par.setdefault((r["derive"], r["rang"]), []).append(r)
    out = ["# Monde B-seuil : étalonnage (sorties de `etalonnage.py`)", "",
           "| d | rang | répétitions | valeur centrale ÷ budget (moyenne) | ± 1,96 erreur type | R1 |", "|---|---|---|---|---|---|"]
    pts = []
    for (d, rang), l in sorted(par.items()):
        v = np.array([moyenne_rep(r) for r in l])
        se = float(v.std(ddof=1) / math.sqrt(len(v))) if len(v) > 1 else float("nan")
        out.append(f"| {d:g} | {rang} | {len(v)} | {v.mean():.3f} | {1.96 * se:.3f} | "
                   f"{sum(not r['p1_tenu'] for r in l)} |")
        if rang < 10:
            pts.append((d, float(v.mean())))
    pts.sort()
    for (d0, y0), (d1, y1) in zip(pts, pts[1:]):
        if (y0 - 1.0) * (y1 - 1.0) <= 0 and y1 != y0:
            dstar = d0 + (1.0 - y0) * (d1 - d0) / (y1 - y0)
            out += ["", f"Interpolation linéaire entre d = {d0:g} et d = {d1:g} : d* = {dstar:.4f}, arrondi "
                        f"{round(dstar, 2):.2f}."]
            break
    else:
        out += ["", "1,0 n'est pas encadré par la grille : prolonger (méthode, section 2)."]
    with open(os.path.join(ICI, "etalonnage.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--grille", action="store_true")
    g.add_argument("--etendre", type=float, help="un point de grille de plus (rang suivant)")
    g.add_argument("--verifier", type=float)
    g.add_argument("--resumer", action="store_true")
    p.add_argument("--rang", type=int, default=10)
    a = p.parse_args(argv)
    if a.grille:
        lancer([(d, i, rep) for rep in range(REPS_GRILLE) for i, d in enumerate(GRILLE)])
    elif a.etendre is not None:
        lancer([(a.etendre, len(GRILLE) + a.rang - 10, rep) for rep in range(REPS_GRILLE)])
    elif a.verifier is not None:
        lancer([(a.verifier, a.rang, rep) for rep in range(REPS_VERIF)])
    else:
        resumer()
    return 0


if __name__ == "__main__":
    sys.exit(main())
