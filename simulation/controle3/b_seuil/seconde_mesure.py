"""Monde B-seuil, seconde mesure (méthode : `METHODE.md`, section 4, ce dossier, écrite avant le calcul).

Usage (depuis simulation/) :
    env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/b_seuil/seconde_mesure.py --lancer
    … --resumer
Sorties : `seconde_mesure.jsonl` (une ligne par répétition), `seconde_mesure.md` (refait à chaque appel),
`seconde_mesure_meta.json` (graine, dérive, empreintes du code, durées). Avec `--suffixe v6` : mêmes graines, sorties
`seconde_mesure_v6.*` (sixième passage, moteur des cellules non testables ; comparaison appariée avec la première) ; de
même `--suffixe v7` (max-T recentré, F1) et `--suffixe v8` (F3, 97,5e centile).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import dataclasses  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import platform  # noqa: E402
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
from controle3 import rapport_tableaux as RT  # noqa: E402
from rejeu import analyse as AN  # noqa: E402
from rejeu import config_rejeu as CR  # noqa: E402
from rejeu import decision as DE  # noqa: E402
from rejeu import pipeline as PL  # noqa: E402
from rejeu import preuves as PR  # noqa: E402

GRAINE = 2026110703        # distincte du contrôle 3 (2026110503), de la partie R4 (2026110701), de l'étalonnage (2026110702)
DERIVE = 1.40              # METHODE.md, section 4 : la cellule la plus haute (Haiku) visée à 0,99-1,00 du budget
REPETITIONS = 120
PROCESSUS = 8   # 12 jusqu'à la mesure v7 ; 8 depuis le 08/11, pour laisser la machine utilisable
SORTIE = os.path.join(ICI, "seconde_mesure.jsonl")
META = os.path.join(ICI, "seconde_mesure_meta.json")
RESUME = os.path.join(ICI, "seconde_mesure.md")


def chemins(suffixe: str = "") -> None:
    """Sorties d'une mesure : sans suffixe, la première (moteur du commit 258bd4f) ; « v6 », le sixième passage."""
    global SORTIE, META, RESUME
    s = f"_{suffixe}" if suffixe else ""
    SORTIE = os.path.join(ICI, f"seconde_mesure{s}.jsonl")
    META = os.path.join(ICI, f"seconde_mesure{s}_meta.json")
    RESUME = os.path.join(ICI, f"seconde_mesure{s}.md")
BORNES_SEUIL = (0.98, 1.02)  # lecture fixée d'avance (section 4)


def monde() -> MD.Monde:
    """B-seuil, dérive du commerce ramenée à DERIVE écritures réversibles par partie."""
    return dataclasses.replace(MD.MONDES_PAR_NOM["B-seuil"], nom="B-seuil-bis", melange=(("commerce", "ECR", DERIVE),))


def une_repetition(m: MD.Monde, ss: np.random.SeedSequence, params: H.Parametres) -> dict:
    """Le chemin de `harnais.repetition` (génération, analyse, décision, désaccord persistant), pour un monde et une
    graine donnés ; garde en plus toutes les cellules du point 1 du commerce à enjeu faible."""
    t0 = time.time()
    cfg = H.config()
    g_gen, g_moteur = ss.spawn(2)
    g = MD.generer(m, np.random.default_rng(g_gen), cfg)
    e = g["entrees"]
    t1 = time.time()
    prep = PR.preparer(e, "confirmes")
    G0 = int(g_moteur.generate_state(1, np.uint64)[0] >> np.uint64(1))
    reg = AN.Reglages(G0=G0, R0=params.R0, B=params.B, K=params.K, tranche=params.tranche,
                      valeurs_e=(CR.E_PRINCIPAL,), noms_regles=("B-tout",), choix=H.choix_methode())
    regles = H.regles_monde(m, cfg)
    an = PL.analyser(e, prep, cfg, reg, g["conf"], g["cal"], processus=1, regles_imposees=regles)
    p0 = DE.point0(e, prep)
    dec = DE.decider(an, p0)
    out = H.resume_decision(dec, an)
    out["etiquette_principale"] = out["etiquette"]
    if p0["persistantes"]:
        prep_bv = PR.preparer(e, "bruts_vague", p0["persistantes"])
        an_bv = PL.analyser(e, prep_bv, cfg, reg, g["conf"], g["cal"], processus=1, regles_imposees=regles)
        e_bv = DE.decider(an_bv, DE.point0(e, prep_bv))["etiquette"]
        out["etiquette"] = DE.moins_favorable(out["etiquette"], e_bv)
        out["b2"] = dict(vagues=p0["persistantes"], etiquette_bruts_vague=e_bv)
    res = PR.resume(prep)
    out["cellules_commerce_faible"] = [
        dict(famille="/".join(map(str, c["famille"])), statut=c["statut"], centre=float(c["centre"]),
             budget=float(c["budget"]), borne=float(c.get("borne_maxt", float("nan"))), verdict=c.get("verdict"),
             porteuses=int(c.get("porteuses", 0)))
        for c in dec["point1"]["cellules"] if c["famille"][1] == "commerce" and c["niveau"] == "faible"]
    out.update(monde=m.nom, G0=G0, attendu=m.attendu,
               volumes=dict(parties=res["parties"], ecritures=res["ecritures"], erreurs=res["erreurs_preuve"],
                            plafonnees=res["plafonnees"], doutes=res["doutes"], lectures=res["lectures"]),
               duree_generation=round(t1 - t0, 2), duree=round(time.time() - t0, 2))
    return out


def _une(rep: int) -> dict:
    p = H.Parametres(R0=L.R0, B=L.B, K=L.K, tranche=L.TRANCHE, graine=GRAINE)
    out = une_repetition(monde(), np.random.SeedSequence([GRAINE, int(rep)]), p)
    out.update(rep=int(rep), derive=DERIVE)
    return out


def lancer() -> None:
    if os.path.exists(SORTIE):
        sys.exit(f"{SORTIE} existe déjà : la mesure ne se relance pas par-dessus.")
    meta = dict(statut="en cours", debut=time.strftime("%Y-%m-%d %H:%M:%S"), graine=GRAINE, derive=DERIVE,
                repetitions=REPETITIONS, R0=L.R0, B=L.B, K=L.K, tranche=L.TRANCHE, processus=PROCESSUS,
                python=platform.python_version(), numpy=np.__version__, empreintes=L.empreintes())
    with open(META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    t0 = time.time()
    with get_context("spawn").Pool(PROCESSUS) as pool, open(SORTIE, "w", encoding="utf-8") as f:
        for i, r in enumerate(pool.imap_unordered(_une, range(REPETITIONS)), 1):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            print(f"[{time.time() - t0:6.0f} s] {i}/{REPETITIONS} rep={r['rep']} {r['etiquette']}", flush=True)
    meta.update(statut="terminé", fin=time.strftime("%Y-%m-%d %H:%M:%S"), duree_s=round(time.time() - t0, 1))
    with open(META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    resumer()


def lecture(plus_haute: float) -> str:
    lo, hi = BORNES_SEUIL
    if plus_haute > hi:
        return "au-dessus du seuil : la part de R1 se lit comme une puissance"
    if plus_haute < lo:
        return "sous le seuil : la part de R1 se lit comme un niveau sous le seuil (attendu au plus 5 %)"
    return "au seuil : la part de R1 se lit comme le niveau du max-T au seuil (attendu au plus 5 %)"


def resumer() -> None:
    with open(SORTIE, encoding="utf-8") as f:
        rs = sorted((json.loads(l) for l in f if l.strip()), key=lambda r: r["rep"])
    n = len(rs)
    et = {}
    for r in rs:
        et[r["etiquette"]] = et.get(r["etiquette"], 0) + 1
    k1 = sum(not r["p1"]["tenu"] for r in rs)
    lo, hi = RT.ic_wilson(k1, n)
    par = {}
    for r in rs:
        for c in r["cellules_commerce_faible"]:
            if c["statut"] == DE.JUGEE:
                par.setdefault(c["famille"], []).append((c["centre"] / c["budget"], c["verdict"] == DE.ETABLI))
    lignes = []
    for fam, v in par.items():
        x = np.array([a for a, _ in v])
        se = float(x.std(ddof=1) / math.sqrt(len(x))) if len(x) > 1 else float("nan")
        lignes.append((float(x.mean()), fam, len(x), 1.96 * se, sum(b for _, b in v)))
    lignes.sort(reverse=True)
    out = ["# Monde B-seuil, seconde mesure (sorties de `seconde_mesure.py`)", "",
           f"Dérive {DERIVE:g}, graine {GRAINE}, {n} répétitions sur {REPETITIONS}.", "",
           "Étiquettes : " + ", ".join(f"{k} {v}" for k, v in sorted(et.items())) + ".", "",
           f"R1 (point 1 non tenu) : {k1} sur {n} ({100 * k1 / n:.1f} %, IC 95 % de Wilson "
           f"{100 * lo:.1f}–{100 * hi:.1f} %).", "",
           "| Cellule jugée (commerce, enjeu faible) | répétitions | valeur centrale ÷ budget (moyenne) | ± 1,96 erreur "
           "type | dépassement établi |", "|---|---|---|---|---|"]
    out += [f"| {fam} | {k} | {m:.3f} | {e:.3f} | {b} |" for m, fam, k, e, b in lignes]
    if lignes:
        m, fam, _, e, _ = lignes[0]
        out += ["", f"Plus haute : {fam}, {m:.3f} ± {e:.3f}. Lecture fixée d'avance ({BORNES_SEUIL[0]:g} à "
                    f"{BORNES_SEUIL[1]:g}) : {lecture(m)}."]
    with open(RESUME, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--lancer", action="store_true")
    g.add_argument("--resumer", action="store_true")
    p.add_argument("--suffixe", default="", help="v6 : sixième passage (mêmes graines, autres fichiers)")
    a = p.parse_args(argv)
    chemins(a.suffixe)
    lancer() if a.lancer else resumer()
    return 0


if __name__ == "__main__":
    sys.exit(main())
