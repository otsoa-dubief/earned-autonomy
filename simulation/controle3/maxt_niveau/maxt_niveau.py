"""Niveau du max-T de B-tout : cinq formules comparées (méthode : `METHODE.md`, ce dossier, écrite avant le calcul).

Usage (depuis simulation/) :
    env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/maxt_niveau/maxt_niveau.py --lancer
    … --evaluer      (relit les données, refait les tableaux)
Sorties : `donnees/<régime>.pkl` (non versionné, empreinte dans `meta.json`), `maxt_niveau.csv`, `maxt_niveau.md`.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import csv  # noqa: E402
import dataclasses  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import pickle  # noqa: E402
import platform  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import get_context  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, SIM)

import numpy as np  # noqa: E402

GRAINE = 2026110705
ALPHA = 0.05
TIRAGES_Z = 20_000
PORTEUSES_MIN = 2
TOL = float(np.sqrt(np.finfo(float).eps))
PROCESSUS = 12
DONNEES = os.path.join(ICI, "donnees")
FORMULES = ("F0", "F1", "F2", "F3", "F4")
# (nom, monde, répétitions, hypothèse nulle complète) ; le rang dans cette liste entre dans la graine
REGIMES = (("N1", "A", 200, True), ("N2", "E-fort", 100, True), ("P2", "B-seuil-1.40", 120, False),
           ("P1", "B-seuil", 60, False), ("P4", "B", 30, False))


# --------------------------------------------------------------------------- formules
def _testables(porteuses, sd, est, bud) -> np.ndarray:
    sd = np.asarray(sd, dtype=float)
    ok = np.isfinite(sd) & (np.where(np.isfinite(sd), sd, 0.0) > TOL * np.maximum(np.abs(est), np.abs(bud)))
    return ok & (np.asarray(porteuses) >= PORTEUSES_MIN)


def _quantile(T, q) -> float:
    with np.errstate(invalid="ignore"):
        m = np.max(np.clip(T, -1e6, 1e6), axis=1)
    return float(np.quantile(m, q))


def formule(nom: str, est, boot, bud, porteuses, se=None, se_boot=None, jack=None, groupes=None, rng=None) -> np.ndarray:
    """Cellules où le dépassement est établi, selon la formule (METHODE.md, section 2)."""
    est, boot, bud = np.asarray(est, float), np.asarray(boot, float), np.asarray(bud, float)
    m = est.size
    etabli = np.zeros(m, dtype=bool)
    if m == 0:
        return etabli
    with np.errstate(invalid="ignore"):
        sd = boot.std(axis=0, ddof=1)
    if nom in ("F0", "F1", "F3"):
        t = _testables(porteuses, sd, est, bud)
        if not t.any():
            return etabli
        centre = est[t] if nom == "F0" else boot[:, t].mean(axis=0)
        T = (boot[:, t] - centre) / sd[t]
        c = _quantile(T, 1 - (ALPHA / 2 if nom == "F3" else ALPHA))
        if nom != "F0":
            c = max(c, 0.0)
        etabli[t] = est[t] - c * sd[t] > bud[t]
        return etabli
    if nom == "F2":
        se, se_boot = np.asarray(se, float), np.asarray(se_boot, float)
        t = _testables(porteuses, se, est, bud) & _testables(porteuses, sd, est, bud)
        if not t.any():
            return etabli
        with np.errstate(invalid="ignore", divide="ignore"):
            T = (boot[:, t] - boot[:, t].mean(axis=0)) / se_boot[:, t]
        T = np.where(np.isfinite(T), T, np.where(boot[:, t] > boot[:, t].mean(axis=0), 1e6, -1e6))
        c = max(_quantile(T, 1 - ALPHA), 0.0)
        etabli[t] = est[t] - c * se[t] > bud[t]
        return etabli
    if nom == "F4":
        sdj = np.full(m, np.nan)
        cov_blocs = []
        for idx in groupes:                       # cellules d'un même environnement : mêmes tâches retirées
            J = np.stack([np.asarray(jack[i], float) for i in idx], axis=1)
            G = J.shape[0]
            D = J - J.mean(axis=0)
            C = (G - 1) / G * D.T @ D
            sdj[idx] = np.sqrt(np.clip(np.diag(C), 0, None))
            cov_blocs.append((idx, C))
        t = _testables(porteuses, sdj, est, bud)
        if not t.any():
            return etabli
        Z = np.zeros((TIRAGES_Z, m))
        for idx, C in cov_blocs:
            s = np.sqrt(np.clip(np.diag(C), 0, None))
            with np.errstate(invalid="ignore", divide="ignore"):
                R = C / np.outer(s, s)
            R = np.where(np.isfinite(R), R, 0.0)
            np.fill_diagonal(R, 1.0)
            w, V = np.linalg.eigh(R)
            L = V * np.sqrt(np.clip(w, 0, None))
            Z[:, idx] = rng.standard_normal((TIRAGES_Z, len(idx))) @ L.T
        c = max(_quantile(Z[:, t], 1 - ALPHA), 0.0)
        etabli[t] = est[t] - c * sdj[t] > bud[t]
        return etabli
    raise ValueError(nom)


# --------------------------------------------------------------------------- collecte
def monde(nom: str):
    from controle3 import mondes as MD
    if nom == "B-seuil-1.40":
        return dataclasses.replace(MD.MONDES_PAR_NOM["B-seuil"], nom="B-seuil-1.40", melange=(("commerce", "ECR", 1.40),))
    return MD.MONDES_PAR_NOM[nom]


def une(args) -> dict:
    regime, rang, nom_monde, rep = args
    from controle3 import harnais as H
    from controle3 import lancer as L
    from controle3 import mondes as MD
    from rejeu import analyse as AN
    from rejeu import config_rejeu as CR
    from rejeu import decision as DE
    from rejeu import pipeline as PL
    from rejeu import preuves as PR
    m, p, cfg = monde(nom_monde), L.parametres(), H.config()
    g_gen, g_moteur = np.random.SeedSequence([GRAINE, rang, rep]).spawn(2)
    g = MD.generer(m, np.random.default_rng(g_gen), cfg)
    e = g["entrees"]
    prep = PR.preparer(e, "confirmes")
    G0 = int(g_moteur.generate_state(1, np.uint64)[0] >> np.uint64(1))
    reg = AN.Reglages(G0=G0, R0=p.R0, B=p.B, K=p.K, tranche=p.tranche, valeurs_e=(CR.E_PRINCIPAL,),
                      noms_regles=("B-tout",), choix=H.choix_methode())
    an = PL.analyser(e, prep, cfg, reg, g["conf"], g["cal"], processus=1, regles_imposees=H.regles_monde(m, cfg))
    cel = []
    for c in DE.cellules(an, "B-tout"):
        if c["statut"] != DE.JUGEE:
            continue
        q = an.magasin[("budget",) + tuple(c["famille"]) + ("B-tout", CR.E_PRINCIPAL, c["niveau"])]
        cel.append(dict(cle=(tuple(c["famille"]), c["niveau"]), centre=float(c["centre"]), budget=float(c["budget"]),
                        porteuses=int(c["porteuses"]), se=float(q.se),
                        boot=np.asarray(q.boot.tableau()[:p.B], dtype=np.float64),
                        se_boot=np.asarray(q.se_boot.tableau()[:p.B], dtype=np.float64),
                        jack=None if q.jack is None else np.asarray(q.jack, dtype=np.float64)))
    return dict(regime=regime, rep=int(rep), cellules=cel)


def _sha(chemin: str) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def lancer() -> None:
    os.makedirs(DONNEES, exist_ok=True)
    meta_chemin = os.path.join(ICI, "meta.json")
    if os.path.exists(meta_chemin):
        sys.exit("meta.json existe : la mesure ne se relance pas par-dessus.")
    meta = dict(statut="en cours", debut=time.strftime("%Y-%m-%d %H:%M:%S"), graine=GRAINE,
                regimes=[list(r) for r in REGIMES], python=platform.python_version(), numpy=np.__version__,
                empreintes={n: _sha(os.path.join(ICI, n)) for n in ("METHODE.md", "maxt_niveau.py")})
    with open(meta_chemin, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    taches = [(r, rang, mo, rep) for rang, (r, mo, n, _nulle) in enumerate(REGIMES) for rep in range(n)]
    par = {r[0]: [] for r in REGIMES}
    t0 = time.time()
    with get_context("spawn").Pool(PROCESSUS) as pool:
        for i, res in enumerate(pool.imap_unordered(une, taches), 1):
            par[res["regime"]].append(res)
            if i % 12 == 0 or i == len(taches):
                print(f"[{time.time() - t0:6.0f} s] {i}/{len(taches)}", flush=True)
    meta["donnees"] = {}
    for r, l in par.items():
        chemin = os.path.join(DONNEES, f"{r}.pkl")
        with open(chemin, "wb") as f:
            pickle.dump(sorted(l, key=lambda x: x["rep"]), f)
        meta["donnees"][r] = _sha(chemin)
    meta.update(statut="terminé", fin=time.strftime("%Y-%m-%d %H:%M:%S"), duree_s=round(time.time() - t0, 1))
    with open(meta_chemin, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    evaluer()


# --------------------------------------------------------------------------- évaluation
def _wilson(k, n, z=1.96):
    if not n:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def decisions(reps: list, budgets_theta: bool, rang: int) -> dict:
    """{formule: [rep : au moins un établi]} et {formule: {cellule: rejets}} (cellule seule, m = 1)."""
    theta = {}
    if budgets_theta:
        acc = {}
        for r in reps:
            for c in r["cellules"]:
                acc.setdefault(c["cle"], []).append(c["centre"])
        theta = {k: float(np.mean(v)) for k, v in acc.items()}
    fam = {f: [] for f in FORMULES}
    seule = {f: {} for f in FORMULES}
    for r in reps:
        cel = r["cellules"]
        if not cel:
            for f in FORMULES:
                fam[f].append(False)
            continue
        est = np.array([c["centre"] for c in cel])
        bud = np.array([theta[c["cle"]] if budgets_theta else c["budget"] for c in cel])
        boot = np.stack([c["boot"] for c in cel], axis=1)
        sb = np.stack([c["se_boot"] for c in cel], axis=1)
        se = np.array([c["se"] for c in cel])
        por = np.array([c["porteuses"] for c in cel])
        jack = [c["jack"] for c in cel]
        envs = {}
        for i, c in enumerate(cel):
            envs.setdefault((c["cle"][0][1], len(c["jack"]) if c["jack"] is not None else -1), []).append(i)
        groupes = [v for k, v in envs.items() if k[1] > 1]
        for f in FORMULES:
            rng = np.random.default_rng(np.random.SeedSequence([GRAINE, 99, rang, r["rep"]]))
            et = formule(f, est, boot, bud, por, se, sb, jack, groupes, rng)
            fam[f].append(bool(et.any()))
            if budgets_theta:
                for i, c in enumerate(cel):
                    e1 = formule(f, est[i:i + 1], boot[:, i:i + 1], bud[i:i + 1], por[i:i + 1], se[i:i + 1],
                                 sb[:, i:i + 1], [jack[i]], [[0]] if jack[i] is not None and len(jack[i]) > 1 else [],
                                 np.random.default_rng(np.random.SeedSequence([GRAINE, 98, rang, r["rep"], i])))
                    d = seule[f].setdefault(c["cle"], [0, 0])
                    d[0] += int(e1[0])
                    d[1] += 1
    return dict(famille=fam, seule=seule)


def evaluer() -> None:
    lignes, choix = [], {}
    parts = {}
    for rang, (r, mo, n, nulle) in enumerate(REGIMES):
        chemin = os.path.join(DONNEES, f"{r}.pkl")
        if not os.path.exists(chemin):
            continue
        with open(chemin, "rb") as f:
            reps = pickle.load(f)
        d = decisions(reps, nulle, rang)
        regs = [(r, d)] + ([("P3", decisions(reps, False, rang))] if r == "N2" else [])
        for nom, dd in regs:
            for fo in FORMULES:
                k, nn = sum(dd["famille"][fo]), len(dd["famille"][fo])
                lo, hi = _wilson(k, nn)
                pire = ""
                if dd["seule"][fo]:
                    cle, (a, b) = max(dd["seule"][fo].items(), key=lambda kv: kv[1][0] / max(kv[1][1], 1))
                    pire = f"{a}/{b} ({'/'.join(map(str, cle[0]))} {cle[1]})"
                lignes.append(dict(regime=nom, formule=fo, n=nn, rejets=k, part=k / nn if nn else float("nan"),
                                   wilson_bas=lo, wilson_haut=hi, pire_cellule_seule=pire))
                parts[(nom, fo)] = k / nn if nn else float("nan")
    with open(os.path.join(ICI, "maxt_niveau.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0].keys()))
        w.writeheader()
        w.writerows(lignes)
    niveau = ("N1", "N2", "P2")
    acceptables = [fo for fo in FORMULES if all(parts.get((r, fo), 1.0) <= 0.05 for r in niveau)]
    ordre_simple = {"F1": 0, "F3": 1, "F2": 2, "F4": 3, "F0": 4}
    if acceptables:
        retenue = sorted(acceptables, key=lambda fo: (-parts.get(("P1", fo), 0), -parts.get(("P3", fo), 0),
                                                       -parts.get(("P4", fo), 0), ordre_simple[fo]))[0]
        motif = "acceptable (au plus 5 % observés en N1, N2 et P2), la plus puissante"
    else:
        retenue = min(FORMULES, key=lambda fo: max(parts.get((r, fo), 1.0) for r in niveau))
        motif = "aucune formule acceptable : la pire part observée la plus basse ; niveau mesuré à déclarer"
    out = ["# Niveau du max-T de B-tout : sorties de `maxt_niveau.py`", "",
           "| Régime | Formule | Répétitions | Au moins un dépassement établi | Part | IC 95 % (Wilson) | Pire cellule seule |",
           "|---|---|---|---|---|---|---|"]
    out += [f"| {l['regime']} | {l['formule']} | {l['n']} | {l['rejets']} | {100 * l['part']:.1f} % | "
            f"{100 * l['wilson_bas']:.1f}–{100 * l['wilson_haut']:.1f} % | {l['pire_cellule_seule']} |" for l in lignes]
    out += ["", f"Formules acceptables : {', '.join(acceptables) or 'aucune'}.",
            f"**Formule retenue par la règle (section 4) : {retenue}** ({motif})."]
    with open(os.path.join(ICI, "maxt_niveau.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
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
