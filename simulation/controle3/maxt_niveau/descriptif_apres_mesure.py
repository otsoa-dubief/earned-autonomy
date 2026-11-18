"""Descriptif, calculé après la mesure (hors de la règle de choix de METHODE.md) : d'où vient l'excès restant de F1.

1. Taille des familles testables par répétition (N1, N2), et taille des familles où F1 et F3 établissent à tort.
2. Par cellule de N1 testable dans au moins 60 répétitions : rapport entre l'écart type bootstrap moyen et l'écart type
   réel de la valeur centrale entre répétitions, et décalage moyen des répétitions sous la valeur centrale, en écarts
   types.
3. Cellules établies à tort dans chaque répétition où F1 ou F3 rejette la famille (N1, N2).
4. Cellules seules (m = 1) qui rejettent le plus : rejets, répétitions où la cellule est jugée, répétitions où elle est
   testable ; part des répétitions testables et valeur centrale moyenne des répétitions testables ÷ θ_G (la
   testabilité dépend des erreurs : une cellule sans erreur n'est pas testable).
5. Plancher de c* : répétitions où le centile brut est négatif, en famille et pour les cellules seules (F1, F3).

Relecture indépendante du 08/11 (points 2, 3, 6 et 8) : sections 3 à 5 ajoutées.

Usage (depuis simulation/) :
    env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/maxt_niveau/descriptif_apres_mesure.py
Sortie : `descriptif_apres_mesure.txt`.
"""
from __future__ import annotations

import collections
import importlib.util
import os
import pickle
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, SIM)

import numpy as np  # noqa: E402


def _mesure():
    spec = importlib.util.spec_from_file_location("maxt_niveau", os.path.join(ICI, "maxt_niveau.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _charger(regime: str):
    with open(os.path.join(ICI, "donnees", f"{regime}.pkl"), "rb") as f:
        reps = pickle.load(f)
    acc = collections.defaultdict(list)
    for r in reps:
        for c in r["cellules"]:
            acc[c["cle"]].append(c["centre"])
    return reps, {k: float(np.mean(v)) for k, v in acc.items()}


def _nom(cle) -> str:
    return "/".join(map(str, cle[0])) + " " + cle[1]


def familles(MN) -> list:
    out = ["## 1. Taille des familles testables (hypothèse nulle complète)"]
    for regime in ("N1", "N2"):
        reps, theta = _charger(regime)
        tailles, rejet = [], {"F1": [], "F3": []}
        for r in reps:
            cel = r["cellules"]
            if not cel:
                tailles.append(0)
                continue
            est = np.array([c["centre"] for c in cel])
            bud = np.array([theta[c["cle"]] for c in cel])
            boot = np.stack([c["boot"] for c in cel], axis=1)
            por = np.array([c["porteuses"] for c in cel])
            m = int(MN._testables(por, boot.std(axis=0, ddof=1), est, bud).sum())
            tailles.append(m)
            for f in rejet:
                if MN.formule(f, est, boot, bud, por).any():
                    rejet[f].append(m)
        t = np.array(tailles)
        out.append(f"{regime} : {t.size} répétitions ; cellules testables : min {t.min()}, médiane {np.median(t):g}, "
                   f"max {t.max()} ; répétitions à 0, 1 et 2 cellules : {(t == 0).sum()}, {(t == 1).sum()}, "
                   f"{(t == 2).sum()}")
        for f, ms in rejet.items():
            out.append(f"  {f} : familles des répétitions où au moins un dépassement est établi : {sorted(ms)}")
    return out


def dispersion() -> list:
    reps, _ = _charger("N1")
    par = collections.defaultdict(lambda: dict(centre=[], sd=[], decalage=[]))
    for r in reps:
        for c in r["cellules"]:
            b = c["boot"]
            sd = float(np.std(b, ddof=1))
            if not np.isfinite(sd) or sd <= 0 or c["porteuses"] < 2:
                continue
            d = par[c["cle"]]
            d["centre"].append(c["centre"])
            d["sd"].append(sd)
            d["decalage"].append((float(np.mean(b)) - c["centre"]) / sd)
    lignes = []
    for cle, d in par.items():
        if len(d["centre"]) < 60:
            continue
        lignes.append((float(np.mean(d["sd"]) / np.std(d["centre"], ddof=1)), float(np.mean(d["decalage"])),
                       len(d["centre"]), _nom(cle)))
    lignes.sort()
    out = ["## 2. Écart type bootstrap contre écart type réel (N1, cellules testables dans au moins 60 répétitions)",
           "rapport (écart type bootstrap moyen ÷ écart type réel de la valeur centrale) ; décalage moyen des "
           "répétitions (en écarts types) ; répétitions ; cellule"]
    out += [f"{a:.2f} ; {b:+.2f} ; {n} ; {nom}" for a, b, n, nom in lignes]
    for titre, garde in (("WorkBench, enjeu faible", lambda nom: "WorkBench" in nom and nom.endswith("faible")),
                         ("autres cellules", lambda nom: not ("WorkBench" in nom and nom.endswith("faible")))):
        g = [x for x in lignes if garde(x[3])]
        if g:
            out.append(f"{titre} : {len(g)} cellules ; rapport de {min(x[0] for x in g):.2f} à "
                       f"{max(x[0] for x in g):.2f}, médiane {np.median([x[0] for x in g]):.2f} ; décalage médian "
                       f"{np.median([x[1] for x in g]):+.2f}")
    return out


def _rep_arrays(cel, theta, nulle=True):
    est = np.array([c["centre"] for c in cel])
    bud = np.array([theta[c["cle"]] if nulle else c["budget"] for c in cel])
    boot = np.stack([c["boot"] for c in cel], axis=1)
    por = np.array([c["porteuses"] for c in cel])
    return est, bud, boot, por


def _centile_brut(boot, t, q):
    """Centile du maximum des T* recentrés sur les cellules t, avant le plancher (F1 : 0,95 ; F3 : 0,975)."""
    b = boot[:, t]
    T = (b - b.mean(axis=0)) / b.std(axis=0, ddof=1)
    return float(np.quantile(T.max(axis=1), q))


def etablies(MN) -> list:
    out = ["## 3. Cellules établies à tort, par répétition rejetée (hypothèse nulle complète)"]
    for regime in ("N1", "N2"):
        reps, theta = _charger(regime)
        for f in ("F1", "F3"):
            for r in reps:
                cel = r["cellules"]
                if not cel:
                    continue
                est, bud, boot, por = _rep_arrays(cel, theta)
                e = MN.formule(f, est, boot, bud, por)
                if e.any():
                    noms = sorted(_nom(cel[i]["cle"]) for i in np.flatnonzero(e))
                    out.append(f"{regime} {f} répétition {r['rep']} : {len(noms)} cellule(s) : " + " | ".join(noms))
    return out


def seules(MN) -> list:
    out = ["## 4. Cellules seules (m = 1) : rejets ÷ jugée ÷ testable ; part testable ; valeur centrale moyenne des "
           "répétitions testables ÷ θ_G"]
    for regime in ("N1", "N2"):
        reps, theta = _charger(regime)
        compte = collections.defaultdict(lambda: dict(F1=0, F3=0, jugee=0, testable=0, centres_t=[]))
        for r in reps:
            for c in r["cellules"]:
                est, bud, boot, por = _rep_arrays([c], theta)
                d = compte[c["cle"]]
                d["jugee"] += 1
                if MN._testables(por, boot.std(axis=0, ddof=1), est, bud)[0]:
                    d["testable"] += 1
                    d["centres_t"].append(c["centre"])
                for f in ("F1", "F3"):
                    d[f] += int(MN.formule(f, est, boot, bud, por)[0])
        pires = sorted(compte.items(), key=lambda kv: -kv[1]["F1"])[:6]
        for cle, d in pires:
            ratio = np.mean(d["centres_t"]) / theta[cle] if d["centres_t"] and theta[cle] > 0 else float("nan")
            out.append(f"{regime} {_nom(cle)} : F1 {d['F1']}, F3 {d['F3']} ; jugée {d['jugee']}, testable "
                       f"{d['testable']} ; valeur centrale testable ÷ θ_G {ratio:.2f}")
    return out


def plancher(MN) -> list:
    out = ["## 5. Plancher de c* : centile brut négatif (répétitions)"]
    for regime, nulle in (("N1", True), ("N2", True), ("P2", False), ("P1", False), ("P4", False)):
        reps, theta = _charger(regime)
        fam = {0.95: 0, 0.975: 0}
        seul = {0.95: 0, 0.975: 0}
        n_fam = n_seul = 0
        for r in reps:
            cel = r["cellules"]
            if not cel:
                continue
            est, bud, boot, por = _rep_arrays(cel, theta, nulle)
            t = MN._testables(por, boot.std(axis=0, ddof=1), est, bud)
            if t.any():
                n_fam += 1
                for q in fam:
                    fam[q] += _centile_brut(boot, t, q) < 0
            for i in np.flatnonzero(t):
                n_seul += 1
                for q in seul:
                    seul[q] += _centile_brut(boot, np.array([i]), q) < 0
        out.append(f"{regime} : familles {fam[0.95]} (F1) et {fam[0.975]} (F3) sur {n_fam} ; cellules seules "
                   f"{seul[0.95]} (F1) et {seul[0.975]} (F3) sur {n_seul}")
    return out


def main() -> int:
    MN = _mesure()
    lignes = (["# Descriptif après la mesure (hors règle de choix)", ""] + familles(MN) + [""] + dispersion() + [""]
              + etablies(MN) + [""] + seules(MN) + [""] + plancher(MN))
    with open(os.path.join(ICI, "descriptif_apres_mesure.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    print("\n".join(lignes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
