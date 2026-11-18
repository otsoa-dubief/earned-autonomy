"""Contrôle à part de la simulation de couverture de la charge : scénarios presque nuls (PLAN_EXPERIENCE.md, 5.16,
point 9, Q15). Rapporté seulement : il ne change pas le choix de méthode (`resultats_couverture_charge/`).

Usage (depuis simulation/) :
    .venv/bin/python -m rejeu.controle_presque_nul --lancer     une seule fois ; écrit rejeu/resultats_presque_nul/
    .venv/bin/python -m rejeu.controle_presque_nul --verifier

Paramètres écrits et figés avant le lancement : G = 20 tâches (tailles de la première simulation) ; dans chaque jeu, k
tâches tirées au hasard, k de 1 à 5, portent une délégation : chacune de leurs écritures est validée par le témoin et
pas par la règle (−1) avec la probabilité p_g ~ Bêta (moyenne 0,5, corrélation ρ) ; les autres tâches ont une
différence nulle. Valeur vraie : −100 × 0,5 × k ÷ 20. ρ de la grille du plan ; 2 000 jeux par case ; B = 2 000 ;
graine 2026110641. Mesuré pour (i), (ii), (iii) : couverture, part des intervalles entièrement et strictement sous 0
(« baisse établie »), part des intervalles [0, 0].
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import csv  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import numpy as np  # noqa: E402

from . import couverture as CO  # noqa: E402
from . import intervalles as IC  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(ICI, "resultats_presque_nul")
GRAINE = 2026110641
G = 20
KS = (1, 2, 3, 4, 5)
MU = 0.5
N_JEUX = 2000
B = 2000
PAQUET = 10
FICHIERS_CODE = ("controle_presque_nul.py", "couverture.py", "intervalles.py")


def valeur_vraie(k: int) -> float:
    return -100.0 * MU * k / G


def paquet_jeux(rng, k: int, rho: float, J: int, B_: int = B) -> dict:
    m = CO.tailles(G)
    M = int(m.sum())
    porte = np.zeros((J, G), dtype=bool)
    for j in range(J):
        porte[j, rng.choice(G, size=k, replace=False)] = True
    p = CO._taux_taches(rng, MU, rho, (J, G))
    y = rng.binomial(np.broadcast_to(m, (J, G)), p) * porte
    a = -y.astype(float)
    centre = 100.0 * a.sum(axis=1) / M
    se = 100.0 * IC.se_rapport(a, np.broadcast_to(m, (J, G)))
    idx = rng.integers(0, G, size=(J, B_, G))
    ao = np.take_along_axis(np.broadcast_to(a[:, None, :], (J, B_, G)), idx, axis=2)
    mo = m[idx]
    boot = 100.0 * ao.sum(axis=2) / mo.sum(axis=2)
    se_boot = 100.0 * IC.se_rapport(ao, mo)
    jack = 100.0 * (a.sum(axis=1, keepdims=True) - a) / (M - m[None, :])
    return {"i": IC.ic_bootstrap_reuni(centre, boot), "ii": IC.ic_bootstrap_t(centre, se, boot, se_boot),
            "iii": IC.ic_jackknife_t(centre, jack)}


def simuler_case(k: int, rho: float, n_jeux: int = N_JEUX, graine: int = GRAINE, B_: int = B) -> list:
    rng = np.random.default_rng(np.random.SeedSequence([graine, k, int(round(rho * 1000))]))
    vrai = valeur_vraie(k)
    acc = {m: dict(couvre=0, sous=0, nul=0) for m in IC.METHODES}
    fait = 0
    while fait < n_jeux:
        J = min(PAQUET, n_jeux - fait)
        res = paquet_jeux(rng, k, rho, J, B_)
        for m in IC.METHODES:
            lo, hi = (np.asarray(v, dtype=float) for v in res[m])
            acc[m]["couvre"] += int(((lo <= vrai) & (vrai <= hi)).sum())
            acc[m]["sous"] += int((hi < 0).sum())
            acc[m]["nul"] += int(((lo == 0) & (hi == 0)).sum())
        fait += J
    return [dict(k=k, G=G, rho=rho, methode=m, n_jeux=n_jeux, valeur_vraie=vrai, couverture=a["couvre"] / n_jeux,
                 part_baisse_etablie=a["sous"] / n_jeux, part_intervalle_nul=a["nul"] / n_jeux)
            for m, a in acc.items()]


def _travail(args):
    return simuler_case(*args)


def empreinte_code() -> dict:
    out = {}
    for n in FICHIERS_CODE:
        with open(os.path.join(ICI, n), "rb") as f:
            out[n] = hashlib.sha256(f.read()).hexdigest()
    return out


def lancer(dossier: str = DOSSIER) -> list:
    if os.path.exists(os.path.join(dossier, "controle.csv")):
        raise SystemExit(f"{dossier} contient déjà des résultats : le contrôle se lance une fois")
    os.makedirs(dossier, exist_ok=True)
    debut = time.time()
    cases = [(k, r) for k in KS for r in CO.RHOS]
    with ProcessPoolExecutor(max_workers=min(len(cases), os.cpu_count() or 1)) as ex:
        lignes = [l for res in ex.map(_travail, cases) for l in res]
    with open(os.path.join(dossier, "controle.csv"), "w", newline="", encoding="utf-8") as f:
        f.write("# Contrôle des scénarios presque nuls (PLAN_EXPERIENCE.md, 5.16, point 9), données synthétiques ; "
                "rapporté seulement, sans effet sur le choix de méthode.\n")
        w = csv.DictWriter(f, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)
    with open(os.path.join(dossier, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(dict(objet="scénarios presque nuls (5.16, point 9)", graine=GRAINE, G=G, ks=KS, mu=MU,
                       rhos=CO.RHOS, tailles=CO.TAILLES, n_jeux=N_JEUX, B=B, empreinte_code=empreinte_code(),
                       duree_s=round(time.time() - debut, 1)), f, ensure_ascii=False, indent=1)
        f.write("\n")
    return lignes


def verifier(dossier: str = DOSSIER) -> list:
    with open(os.path.join(dossier, "meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    return [f"{n} a changé depuis le contrôle" for n, h in empreinte_code().items()
            if meta["empreinte_code"].get(n) != h]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--lancer", action="store_true")
    p.add_argument("--verifier", action="store_true")
    a = p.parse_args(argv)
    if a.lancer:
        lancer()
    if a.verifier:
        e = verifier()
        print("\n".join(e) if e else "code conforme aux résultats du contrôle")
        return 1 if e else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
