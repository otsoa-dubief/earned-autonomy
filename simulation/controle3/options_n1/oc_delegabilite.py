"""Courbes d'efficacité (OC) des règles de délégabilité candidates pour N1 (contrôle 3, second passage).

Mêmes mondes que l'étude de délégabilité du contrôle 3 (controle3.harnais.monde_delegabilite : agents à `multiple`
fois la barre sur tous les types, corrélation intra-tâche ρ, témoins en défaut ou non), mêmes classes calibrées
(rejeu.classes), graines distinctes. Pour chaque répétition : la configuration est délégable si au moins un de ses types
passe la règle. Deux estimations de ρ̂ : celle du moteur, et une variante sans les grappes d'une écriture (résidu de G1).
Aucune règle n'est rejouée ; aucun appel payant.
"""
import csv
import json
import os
import sys
from multiprocessing import get_context

SIM = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, SIM)

import numpy as np  # noqa: E402
from scipy.stats import beta  # noqa: E402

GRAINE = 20261106
MULTIPLES = (0.0, 0.1, 0.3, 0.5, 1.0, 2.0, 5.0, 10.0)
RHOS = (0.0, 0.3, 0.7)
REPS = 150
REGLES = ("est", "obs1", "obs2", "obs3", "jeff", "ub50", "ub80", "prouve", "faible")


def regles_type(v, faible):
    n, ne, xe, b = v["n"], v["n_eff"], v["x_eff"], v["barre"]
    if not n or n <= 0 or not ne or ne <= 0:
        return {r: False for r in REGLES}
    from rejeu import classes as CL
    est = bool(CL.estime_sous(v))
    m_bar = ne * b  # erreurs attendues à la barre, en taille effective
    return {
        "est": est,
        "obs1": est and m_bar >= 1,
        "obs2": est and m_bar >= 2,
        "obs3": est and m_bar >= 3,
        "jeff": float(beta.median(xe + 0.5, ne - xe + 0.5)) <= b,
        "ub50": CL.bornes_cp(xe, ne, 0.5)[1] <= b,
        "ub80": CL.bornes_cp(xe, ne, 0.2)[1] <= b,
        "prouve": v["classe"] == CL.SOUS,
        "faible": est and faible,
    }


def evaluer(cls, TY):
    """{règle: (au moins une configuration délégable, nombre de configurations délégables)}."""
    par_regle = {r: 0 for r in REGLES}
    for env, mods in cls.items():
        for m, c in mods.items():
            ok = {r: False for r in REGLES}
            for k, v in c.items():
                rt = regles_type(v, TY.ENJEU[k] == TY.FAIBLE)
                for r in REGLES:
                    ok[r] = ok[r] or rt[r]
            for r in REGLES:
                par_regle[r] += int(ok[r])
    return par_regle


def une(args):
    multiple, rho, temoins, rep, case = args
    from controle3 import harnais as H
    from rejeu import classes as CL
    from rejeu import suites as SU
    cfg = H.config()
    monde = H.monde_delegabilite(multiple, rho, temoins)
    rng = np.random.default_rng(np.random.SeedSequence([GRAINE, 2000 + case, rep]))
    g = H.MD.generer(monde, rng, cfg)
    e = g["entrees"]
    prep = H.PR.preparer(e, "confirmes")
    jks = {env: {m: SU.jeu_configuration(prep, e, env, m, g["cal"][env], "calibration") for m in H.CR.MODELES}
           for env in H.MD.ENVS}
    sortie = {"moteur": evaluer(CL.classes_tous_environnements(jks, cfg), H.TY)}
    origine = CL.rho_anova

    def rho_sans_grappes_d_une(m, x):
        m = np.asarray(m, dtype=float)
        x = np.asarray(x, dtype=float)
        garde = m > 1
        return origine(m[garde], x[garde])
    CL.rho_anova = rho_sans_grappes_d_une
    try:
        sortie["sans_grappes_1"] = evaluer(CL.classes_tous_environnements(jks, cfg), H.TY)
    finally:
        CL.rho_anova = origine
    return (multiple, rho, temoins, sortie)


def main():
    os.chdir(SIM)
    taches, case = [], 0
    for temoins in (False, True):
        for rho in RHOS:
            for mult in MULTIPLES:
                taches += [(mult, rho, temoins, r, case) for r in range(REPS)]
                case += 1
    agg = {}
    with get_context("spawn").Pool(int(os.environ.get("PROCESSUS", "8"))) as pool:
        for k, (mult, rho, tem, s) in enumerate(pool.imap_unordered(une, taches, chunksize=4), 1):
            for var, par in s.items():
                a = agg.setdefault((var, tem, rho, mult), {"n": 0, **{f"{r}_une": 0 for r in REGLES},
                                                             **{f"{r}_nb": 0 for r in REGLES}})
                a["n"] += 1
                for r in REGLES:
                    a[f"{r}_une"] += int(par[r] > 0)
                    a[f"{r}_nb"] += par[r]
            if k % 500 == 0:
                print(f"{k}/{len(taches)}", flush=True)
    ici = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(ici, "oc_delegabilite.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rho_estime", "temoins", "rho", "multiple", "n"] + [f"{r}_au_moins_une" for r in REGLES]
                   + [f"{r}_nb_moyen" for r in REGLES])
        for (var, tem, rho, mult), a in sorted(agg.items()):
            w.writerow([var, int(tem), rho, mult, a["n"]] + [round(a[f"{r}_une"] / a["n"], 3) for r in REGLES]
                       + [round(a[f"{r}_nb"] / a["n"], 2) for r in REGLES])
    print("fini", flush=True)


if __name__ == "__main__":
    main()
