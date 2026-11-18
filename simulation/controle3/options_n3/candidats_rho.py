"""N3 : estimateurs candidats de ρ, comparés sur le générateur du contrôle 3 (hors moteur, avant de coder la règle).

Recherche : `reports/Corrélation intra tâche par strates.md` (06/11). Grappe = (tâche, type) dans chaque configuration ;
strate = (configuration, type), avec son propre taux ; mise en commun sur toutes les configurations.
- `g1` : la règle actuelle du moteur (référence, `rejeu.classes.rho_jeux` sur tous les environnements réunis) ;
- `fc` : Fleiss–Cuzick stratifié, ρ̂ = 1 − Σ_s SSW_s ÷ Σ_s (N_s − K_s) p̂_s (1 − p̂_s), SSW_s = Σ y (m − y) ÷ m, borné à
  [0, 1] après la mise en commun ; une strate sans erreur et une grappe d'une écriture pèsent zéro d'office ;
- `fc_corr` : le même, corrigé du biais de petit échantillon (E[p̂(1 − p̂)] = p(1 − p)(1 − deff ÷ N), point fixe) ;
- `bb` : maximum de vraisemblance bêta-binomial joint, taux propre à chaque strate, ρ commun (profil) ;
- `moteur` : l'estimateur retenu dans le moteur (`rejeu.classes.rho_fc_strates`) : `fc_corr` sur les seules grappes
  d'au moins deux écritures, taux compris (une erreur dans une grappe d'une écriture ne dit rien de ρ).
Dans le générateur (`controle3.mondes`), la difficulté d'une tâche est tirée par type : la corrélation vraie vaut ρ
entre écritures d'un même type dans une même tâche, et 0 entre types différents.

Usage : cd simulation && .venv/bin/python controle3/options_n3/candidats_rho.py   (quelques minutes sur 12 processus)
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
from scipy.optimize import minimize_scalar  # noqa: E402
from scipy.special import betaln  # noqa: E402

from controle3 import harnais as H  # noqa: E402
from controle3 import lancer as L  # noqa: E402
from controle3 import mondes as MD  # noqa: E402
from rejeu import classes as CL  # noqa: E402
from rejeu import config_rejeu as CR  # noqa: E402
from rejeu import preuves as PR  # noqa: E402
from rejeu import suites as SU  # noqa: E402
from rejeu import types_regle as TY  # noqa: E402

REPS = 40
# (multiple de la barre, ρ vrai, témoins en défaut)
CASES = [(0.0, r, True) for r in (0.0, 0.3, 0.7, 0.9)] + [(0.2, r, False) for r in (0.0, 0.3, 0.7, 0.9)] + \
        [(0.5, r, False) for r in (0.3, 0.7, 0.9)] + [(0.2, 0.7, True)]
ESTIMATEURS = ("g1", "fc", "fc_corr", "bb", "moteur")


def strates(jeux) -> list:
    """[(m, y)] par strate (configuration, type) : une grappe par tâche où le type est écrit."""
    out = []
    for j in jeux:
        for k in TY.TYPES_SUITE:
            c = CL.comptes_par_tache(j, (k,))
            if c:
                m = np.array([v[0] for v in c.values()], dtype=float)
                y = np.array([v[1] for v in c.values()], dtype=float)
                out.append((m, y))
    return out


def rho_fc(st, correction: bool = False, iterations: int = 30):
    ssw, d0, info = 0.0, [], []
    for m, y in st:
        N, K, Y = m.sum(), m.size, y.sum()
        p = Y / N
        if N <= K or p <= 0.0 or p >= 1.0:
            continue
        ssw += float(np.sum(y * (m - y) / m))
        mstar = float(np.sum(m ** 2) / N)
        d0.append((N - K) * p * (1 - p))
        info.append((N, mstar))
    if not d0:
        return None
    rho = 1.0 - ssw / sum(d0)
    if correction:
        for _ in range(iterations):
            r = min(max(rho, 0.0), 1.0)
            d = sum(di / max(1.0 - (1.0 + (ms - 1.0) * r) / N, 0.1) for di, (N, ms) in zip(d0, info))
            nouveau = 1.0 - ssw / d
            if abs(nouveau - rho) < 1e-9:
                break
            rho = nouveau
    return float(min(max(rho, 0.0), 1.0))


def _ll_bb(m, y, p, rho):
    a, b = p * (1 - rho) / rho, (1 - p) * (1 - rho) / rho
    return float(np.sum(betaln(y + a, m - y + b) - betaln(a, b)))


def rho_bb(st):
    st = [(m, y) for m, y in st if y.sum() > 0 and (m > 1).any()]
    if not st:
        return None

    def moins_profil(rho):
        tot = 0.0
        for m, y in st:
            p0 = y.sum() / m.sum()
            r = minimize_scalar(lambda p: -_ll_bb(m, y, p, rho), bounds=(max(p0 / 50, 1e-9), min(0.999, p0 * 50)),
                                method="bounded", options=dict(xatol=1e-7))
            tot += r.fun
        return tot
    r = minimize_scalar(moins_profil, bounds=(1e-4, 0.999), method="bounded", options=dict(xatol=1e-4))
    return float(r.x)


def un_tirage(args) -> dict:
    multiple, rho, temoins, rep = args
    cases_lancer = [(m, r, t) for t in L.DELEG_TEMOINS for r in L.DELEG_RHOS for m in L.DELEG_MULTIPLES]
    i = cases_lancer.index((multiple, rho, temoins)) if (multiple, rho, temoins) in cases_lancer else \
        10_000 + int(round(multiple * 100)) * 10 + int(round(rho * 10)) + (1000 if temoins else 0)
    rng = np.random.default_rng(np.random.SeedSequence([int(L.GRAINE), 1000 + i, int(rep)]))
    cfg = H.config()
    g = MD.generer(H.monde_delegabilite(multiple, rho, temoins), rng, cfg)
    e = g["entrees"]
    prep = PR.preparer(e, "confirmes")
    jks = [SU.jeu_configuration(prep, e, env, m, g["cal"][env], "calibration") for env in g["cal"] for m in CR.MODELES]
    st = strates(jks)
    return dict(multiple=multiple, rho=rho, temoins=temoins, rep=rep, g1=CL.rho_jeux(jks), fc=rho_fc(st),
                fc_corr=rho_fc(st, correction=True), bb=rho_bb(st), moteur=CL.rho_fc_strates(CL.strates_par_type(jks)))


def main() -> int:
    taches = [(m, r, t, rep) for (m, r, t) in CASES for rep in range(REPS)]
    with get_context("spawn").Pool(L.PROCESSUS) as pool:
        lignes = pool.map(un_tirage, taches, chunksize=2)
    with open(os.path.join(ICI, "candidats_rho.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["multiple", "rho", "temoins", "rep", *ESTIMATEURS])
        w.writeheader()
        w.writerows(lignes)
    print(f"ρ̂ de tous les environnements réunis : médiane [quartiles] sur {REPS} tirages (calculables)")
    print("| multiple | ρ vrai | témoins en défaut | " + " | ".join(ESTIMATEURS) + " |")
    print("|---|---|---|" + "---|" * len(ESTIMATEURS))
    for (m, r, t) in CASES:
        cel = []
        for est in ESTIMATEURS:
            v = sorted(l[est] for l in lignes if (l["multiple"], l["rho"], l["temoins"]) == (m, r, t)
                       and l[est] is not None)
            if v:
                q = statistics.quantiles(v, n=4) if len(v) > 1 else [v[0]] * 3
                cel.append(f"{statistics.median(v):.2f} [{q[0]:.2f}–{q[2]:.2f}] ({len(v)})")
            else:
                cel.append("—")
        print(f"| {m:g} | {r:g} | {'oui' if t else 'non'} | " + " | ".join(cel) + " |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
