"""N3 (contrôle 3, troisième passage) : ρ̂ de la règle G1 comparé à trois variantes, hors moteur.

Mêmes mondes et mêmes graines que l'étude de délégabilité du contrôle 3 (`controle3.harnais.monde_delegabilite`,
cases numérotées comme dans `controle3.lancer`), mêmes jeux de calibration, même estimateur
d'analyse de variance (`rejeu.classes.rho_anova`, grappes d'une écriture écartées). Pour chaque tirage, le ρ̂ de tous
les environnements réunis (celui qu'emprunte un environnement sans erreur) est estimé de quatre façons :
- `g1` : la règle du moteur, chaque (environnement, modèle, tâche) est une grappe, tous types mérités réunis ;
- `ss_conf` : sommes de carrés réunies par configuration (analyse de variance stratifiée) ;
- `moy_conf` : ρ̂ estimé configuration par configuration, puis moyenne pondérée par les erreurs ;
- `ss_type` : sommes de carrés réunies par configuration × type (chaque tâche, un type : une grappe).
Rend aussi les deux répétitions des mondes où R4 sort alors que « confirmée » est attendue (A-rho7 n° 18, E n° 25).
Aucune règle n'est rejouée, le moteur n'est pas modifié ; aucun appel payant.

Usage : cd simulation && .venv/bin/python controle3/options_n3/rho_estimateurs.py (environ 5 minutes sur 12 processus)
"""
from __future__ import annotations

import csv
import os
import statistics
import sys
from multiprocessing import get_context

ICI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, SIM)

import numpy as np  # noqa: E402

from controle3 import harnais as H  # noqa: E402
from controle3 import lancer as L  # noqa: E402
from controle3 import mondes as MD  # noqa: E402
from rejeu import classes as CL  # noqa: E402
from rejeu import config_rejeu as CR  # noqa: E402
from rejeu import preuves as PR  # noqa: E402
from rejeu import suites as SU  # noqa: E402
from rejeu import types_regle as TY  # noqa: E402

REPS = 40
CASES = ((0.0, 0.0, True), (0.0, 0.3, True), (0.0, 0.7, True), (0.2, 0.3, False), (0.2, 0.7, False),
         (0.5, 0.3, False), (0.5, 0.7, False))
ESTIMATEURS = ("g1", "ss_conf", "moy_conf", "ss_type")


def rho_ss(strates) -> float | None:
    """Analyse de variance à grappes emboîtées dans des strates : carrés entre grappes autour de la moyenne de leur
    strate ; variance interne, effectifs et taille moyenne réunis sur toutes les strates. Grappes d'une écriture
    écartées, comme `rho_anova`."""
    sb = n_tot = x_tot = x2m = m2n = 0.0
    k = s = 0
    for m, x in strates:
        m = np.asarray(m, dtype=float)
        x = np.asarray(x, dtype=float)
        garde = m > 1
        m, x = m[garde], x[garde]
        if m.size == 0:
            continue
        ns, xs = m.sum(), x.sum()
        sb += np.sum(x ** 2 / m) - xs ** 2 / ns
        x2m += np.sum(x ** 2 / m)
        x_tot += xs
        n_tot += ns
        m2n += np.sum(m ** 2) / ns
        k += m.size
        s += 1
    if k - s < 1 or n_tot <= k:
        return None
    msb = sb / (k - s)
    msw = (x_tot - x2m) / (n_tot - k)
    m0 = (n_tot - m2n) / (k - s)
    den = msb + (m0 - 1) * msw
    return float(min(1.0, max(0.0, (msb - msw) / den))) if den > 0 else None


def comptes(jeu, types=None) -> tuple:
    c = CL.comptes_par_tache(jeu, types)
    return (tuple(v[0] for v in c.values()), tuple(v[1] for v in c.values())) if c else ((), ())


def moyenne_par_conf(jeux) -> float | None:
    """ρ̂ de chaque configuration (`rho_anova`), moyenne pondérée par ses erreurs en grappes de plus d'une écriture."""
    num = den = 0.0
    for j in jeux:
        m, x = (np.asarray(v, dtype=float) for v in comptes(j))
        if m.size == 0:
            continue
        r = CL.rho_anova(m, x)
        w = float(x[m > 1].sum())
        if r is not None and w > 0:
            num += r * w
            den += w
    return num / den if den > 0 else None


def estimations(jeux) -> dict:
    return dict(g1=CL.rho_jeux(jeux), ss_conf=rho_ss([comptes(j) for j in jeux]), moy_conf=moyenne_par_conf(jeux),
                ss_type=rho_ss([comptes(j, (k,)) for j in jeux for k in TY.TYPES_SUITE]))


def jeux_calibration(monde, rng) -> dict:
    cfg = H.config()
    g = MD.generer(monde, rng, cfg)
    e = g["entrees"]
    prep = PR.preparer(e, "confirmes")
    return {env: {m: SU.jeu_configuration(prep, e, env, m, g["cal"][env], "calibration") for m in CR.MODELES}
            for env in g["cal"]}


def un_tirage(args) -> dict:
    multiple, rho, temoins, rep = args
    cases = [(m, r, t) for t in L.DELEG_TEMOINS for r in L.DELEG_RHOS for m in L.DELEG_MULTIPLES]   # ordre de lancer.py
    i = cases.index((multiple, rho, temoins))
    rng = np.random.default_rng(np.random.SeedSequence([int(L.GRAINE), 1000 + i, int(rep)]))
    jks = jeux_calibration(H.monde_delegabilite(multiple, rho, temoins), rng)
    return dict(multiple=multiple, rho=rho, temoins=temoins, rep=rep,
                **estimations([j for jeux in jks.values() for j in jeux.values()]))


def repetition_monde(nom: str, rep: int) -> dict:
    """ρ̂ de WorkBench selon les quatre estimations, dans une répétition d'un monde (mêmes graines que `lancer.py`)."""
    monde = MD.MONDES_PAR_NOM[nom]
    g_gen, _ = H.graine_repetition(L.parametres(), monde, rep).spawn(2)
    jks = jeux_calibration(monde, np.random.default_rng(g_gen))
    return dict(monde=nom, rep=rep, **estimations(list(jks["WorkBench"].values())))


def main() -> int:
    taches = [(m, r, t, rep) for (m, r, t) in CASES for rep in range(REPS)]
    with get_context("spawn").Pool(L.PROCESSUS) as pool:
        lignes = pool.map(un_tirage, taches, chunksize=4)
    with open(os.path.join(ICI, "rho_estimateurs.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["multiple", "rho", "temoins", "rep", *ESTIMATEURS])
        w.writeheader()
        w.writerows(lignes)
    print(f"ρ̂ de tous les environnements réunis, médiane sur {REPS} tirages (calculables) :")
    print("| multiple | ρ vrai | témoins en défaut | " + " | ".join(ESTIMATEURS) + " |")
    print("|---|---|---|" + "---|" * len(ESTIMATEURS))
    for (m, r, t) in CASES:
        cel = []
        for est in ESTIMATEURS:
            v = [l[est] for l in lignes if (l["multiple"], l["rho"], l["temoins"]) == (m, r, t) and l[est] is not None]
            cel.append(f"{statistics.median(v):.2f} ({len(v)})" if v else "—")
        print(f"| {m:g} | {r:g} | {'oui' if t else 'non'} | " + " | ".join(cel) + " |")
    print("\nρ̂ de WorkBench dans les deux répétitions R4 hors du monde C :")
    for nom, rep in (("A-rho7", 18), ("E", 25)):
        d = repetition_monde(nom, rep)
        print(f"- {nom} n° {rep} : " + ", ".join(f"{e} {d[e]:.3f}" if d[e] is not None else f"{e} —" for e in ESTIMATEURS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
