"""Cellules de 2 à 5 tâches porteuses : niveau du max-T au budget exact (méthode : `METHODE.md`, ce dossier, écrite et
commitée avant le calcul, commit 9a229c6).

Usage (depuis simulation/) :
    env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/porteuses/porteuses.py --lancer
    … --resumer
Sorties : `porteuses.csv` (une ligne par case), `porteuses.md` (refait à chaque appel), `meta.json`. Avec
`--suffixe v7` : mêmes graines et mêmes cases, avec le moteur du septième passage du contrôle 3 (max-T recentré, relecture
C13, C1) ; sorties `porteuses_v7.csv`, `porteuses_v7.md`, `meta_v7.json`, la première mesure restant en place.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import csv  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import platform  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import get_context  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, SIM)

import numpy as np  # noqa: E402

from controle3 import rapport_tableaux as RT  # noqa: E402
from rejeu import maxt as MX  # noqa: E402

# METHODE.md, sections 2 et 3
GRAINE = 2026110704
G = 20                 # tâches du cadre (aviation dans le contrôle 3)
O_AUTRES = 20          # écritures des autres niveaux, par tâche
L_EGALES = 40          # écritures du niveau par tâche porteuse, tailles égales
L_INEGALES = (20, 60)  # bornes du tirage uniforme, tailles inégales
BUDGET = 0.5           # enjeu faible, pour 100 écritures (config_rejeu)
N_CELLULES = 11        # une configuration et dix scénarios portés par les mêmes tâches
B = 2000               # répétitions bootstrap (valeur du plan)
TIRAGES, TIRAGES_PUISSANCE = 10_000, 2_000
KS, RHOS, TAILLES = (1, 2, 3, 4, 5), (0.0, 0.3, 0.7, 1.0), ("égales", "inégales")
CIBLE = 0.05
PROCESSUS = 12
SORTIE = os.path.join(ICI, "porteuses.csv")
META = os.path.join(ICI, "meta.json")
RESUME = os.path.join(ICI, "porteuses.md")


def chemins(suffixe: str = "") -> None:
    """Sorties d'une mesure : sans suffixe, la première (moteur du commit 0a908cf) ; « v7 », le septième passage (F1) ;
    « v8 », le huitième (F3)."""
    global SORTIE, META, RESUME
    s = f"_{suffixe}" if suffixe else ""
    SORTIE = os.path.join(ICI, f"porteuses{s}.csv")
    META = os.path.join(ICI, f"meta{s}.json")
    RESUME = os.path.join(ICI, f"porteuses{s}.md")


def cases() -> list:
    out = [dict(k=k, rho=r, tailles=t, multiple=1.0, tirages=TIRAGES) for k in KS for r in RHOS for t in TAILLES]
    out += [dict(k=k, rho=0.3, tailles="égales", multiple=m, tirages=TIRAGES_PUISSANCE)
            for k in (2, 3, 4, 5) for m in (2.0, 5.0)]
    for i, c in enumerate(out):
        c["rang"] = i
    return out


def _taches(rng, k: int, tailles: str, multiple: float):
    """Écritures du niveau L (G,), dénominateur D (G,), taux moyen p (valeur vraie = multiple × budget)."""
    L = np.zeros(G)
    L[:k] = L_EGALES if tailles == "égales" else rng.integers(L_INEGALES[0], L_INEGALES[1] + 1, size=k)
    D = O_AUTRES + L
    p = min(1.0, multiple * BUDGET / 100.0 * D.sum() / L.sum())
    return L, D, p


def _taux(rng, p: float, rho: float, k: int) -> np.ndarray:
    """Taux des k tâches porteuses : loi bêta de moyenne p et de corrélation intra-tâche rho."""
    if rho <= 0:
        return np.full(k, p)
    if rho >= 1:
        return (rng.random(k) < p).astype(float)
    s = (1 - rho) / rho
    return rng.beta(p * s, (1 - p) * s, size=k)


def _erreurs(rng, k: int, rho: float, tailles: str, multiple: float):
    L, D, p = _taches(rng, k, tailles, multiple)
    pt = np.zeros(G)
    pt[:k] = _taux(rng, p, rho, k)
    x = rng.binomial(L.astype(np.int64)[:, None], pt[:, None], size=(G, N_CELLULES)).astype(float)
    return x, D


def estimation(rng, k: int, rho: float, tailles: str, multiple: float) -> np.ndarray:
    """Valeurs centrales des 11 cellules : dégâts en plus du niveau pour 100 écritures, tous niveaux au dénominateur."""
    x, D = _erreurs(rng, k, rho, tailles, multiple)
    return 100.0 * x.sum(axis=0) / D.sum()


def un_tirage(rng, k: int, rho: float, tailles: str, multiple: float) -> tuple:
    """Un tirage : (au moins une cellule établie, nombre de cellules testables)."""
    x, D = _erreurs(rng, k, rho, tailles, multiple)
    est = 100.0 * x.sum(axis=0) / D.sum()
    idx = rng.integers(0, G, size=(B, G))
    cnt = np.bincount((np.arange(B)[:, None] * G + idx).ravel(), minlength=B * G).reshape(B, G).astype(float)
    den = cnt @ D
    with np.errstate(invalid="ignore", divide="ignore"):
        boot = 100.0 * (cnt @ x) / den[:, None]
    r = MX.depassement_etabli(est, boot, np.full(N_CELLULES, BUDGET), porteuses=np.full(N_CELLULES, k))
    return bool(r["etabli"].any()), int(r["testable"].sum())


def une_case(c: dict) -> dict:
    t0 = time.time()
    n_et, n_test = 0, 0
    for i in range(c["tirages"]):
        rng = np.random.default_rng(np.random.SeedSequence([GRAINE, c["rang"], i]))
        et, te = un_tirage(rng, c["k"], c["rho"], c["tailles"], c["multiple"])
        n_et += et
        n_test += te
    lo, hi = RT.ic_wilson(n_et, c["tirages"])
    return dict(c, etablis=n_et, part=n_et / c["tirages"], wilson_bas=lo, wilson_haut=hi,
                tient=bool(hi <= CIBLE) if c["multiple"] == 1.0 else "", testables_moyen=n_test / c["tirages"],
                duree_s=round(time.time() - t0, 1))


def _sha(chemin: str) -> str:
    with open(chemin, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def lancer() -> None:
    if os.path.exists(SORTIE):
        sys.exit(f"{SORTIE} existe déjà : la mesure ne se relance pas par-dessus.")
    meta = dict(statut="en cours", debut=time.strftime("%Y-%m-%d %H:%M:%S"), graine=GRAINE, B=B, G=G,
                tirages=TIRAGES, tirages_puissance=TIRAGES_PUISSANCE, processus=PROCESSUS,
                python=platform.python_version(), numpy=np.__version__,
                empreintes={n: _sha(os.path.join(d, n)) for d, n in ((ICI, "METHODE.md"), (ICI, "porteuses.py"),
                                                                      (os.path.join(SIM, "rejeu"), "maxt.py"))})
    with open(META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    t0 = time.time()
    res = []
    with get_context("spawn").Pool(PROCESSUS) as pool:
        for r in pool.imap_unordered(une_case, cases()):
            res.append(r)
            print(f"[{time.time() - t0:6.0f} s] case {r['rang']} k={r['k']} rho={r['rho']} {r['tailles']} "
                  f"x{r['multiple']:g} : {r['etablis']}/{r['tirages']}", flush=True)
    res.sort(key=lambda r: r["rang"])
    with open(SORTIE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(res[0].keys()))
        w.writeheader()
        w.writerows(res)
    meta.update(statut="terminé", fin=time.strftime("%Y-%m-%d %H:%M:%S"), duree_s=round(time.time() - t0, 1))
    with open(META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    resumer()


def seuil(niveau: list):
    """Section 4 : le plus petit k ≥ 2 tel que toutes les cases au budget de k et des k plus grands tiennent ; 5 sinon."""
    tient = {k: all(r["tient"] for r in niveau if r["k"] == k) for k in (2, 3, 4, 5)}
    k = next((k for k in (2, 3, 4, 5) if all(tient[j] for j in range(k, 6))), None)
    return (k, True) if k is not None else (5, False)


def resumer() -> None:
    with open(SORTIE, encoding="utf-8") as f:
        rs = list(csv.DictReader(f))
    for r in rs:
        for cle in ("k", "tirages", "etablis", "rang"):
            r[cle] = int(r[cle])
        for cle in ("rho", "multiple", "part", "wilson_bas", "wilson_haut", "testables_moyen"):
            r[cle] = float(r[cle])
        r["tient"] = r["tient"] == "True"
    niveau = [r for r in rs if r["multiple"] == 1.0]
    out = ["# Cellules de 2 à 5 tâches porteuses : sorties de `porteuses.py`", "",
           "## Au budget exact (10 000 tirages par case)", "",
           "| k | ρ | tailles | établi (au moins une cellule) | part | borne haute de Wilson | tient | cellules "
           "testables (moyenne sur 11) |", "|---|---|---|---|---|---|---|---|"]
    out += [f"| {r['k']} | {r['rho']:g} | {r['tailles']} | {r['etablis']} | {100 * r['part']:.2f} % | "
            f"{100 * r['wilson_haut']:.2f} % | {'oui' if r['tient'] else 'non'} | {r['testables_moyen']:.2f} |"
            for r in niveau]
    defaut = [r for r in niveau if r["k"] == 1 and r["etablis"]]
    k, tenu = seuil(niveau)
    out += ["", "Contrôle de cohérence (k = 1, jamais établi) : " + ("tenu." if not defaut else
            f"**DÉFAUT DU CODE** ({len(defaut)} cases avec un dépassement établi)."),
            "", f"**Seuil retenu (méthode, section 4) : {k} tâches porteuses**"
            + ("." if tenu else " ; les cases de k = 5 ne tiennent pas toutes : limite rapportée, sans autre itération.")]
    pu = [r for r in rs if r["multiple"] != 1.0]
    if pu:
        out += ["", "## Puissance, à titre descriptif (ρ = 0,3, tailles égales, 2 000 tirages par case)", "",
                "| k | multiple du budget | établi | part |", "|---|---|---|---|"]
        out += [f"| {r['k']} | {r['multiple']:g} | {r['etablis']} | {100 * r['part']:.1f} % |" for r in pu]
    with open(RESUME, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--lancer", action="store_true")
    g.add_argument("--resumer", action="store_true")
    p.add_argument("--suffixe", default="", help="v7 : septième passage (mêmes graines, autres fichiers)")
    a = p.parse_args(argv)
    chemins(a.suffixe)
    lancer() if a.lancer else resumer()
    return 0


if __name__ == "__main__":
    sys.exit(main())
