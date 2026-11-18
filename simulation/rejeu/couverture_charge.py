"""Simulation de couverture refaite sur ce qui décide désormais le point 2 (PLAN_EXPERIENCE.md, 5.13, « Verdict d'une
cellule », Q13) : la différence appariée de charge (règle moins témoin, pour 100 écritures), groupée par tâche. Données
synthétiques seulement. La première simulation (`couverture.py`, `resultats_couverture/`) reste comme historique.

Usage (depuis simulation/) :
    .venv/bin/python -m rejeu.couverture_charge --lancer      une seule fois ; écrit rejeu/resultats_couverture_charge/
    .venv/bin/python -m rejeu.couverture_charge --verifier    empreintes du code, pour les deux dossiers

Paramètres écrits et figés AVANT le lancement (raisons : CHOIX_PHASE3.md) :
- grille, critère, ordre et repli du plan (5.13) : ρ ∈ {0 ; 0,1 ; 0,3 ; 0,5 ; 0,7 ; 0,9}, G ∈ {20 ; 40 ; 90}, 93 %,
  (i), (ii), (iii), repli sur la meilleure pire couverture et zone qui échoue ;
- modèle d'une tâche g de m_g écritures (les mêmes tailles que la première simulation, de 1 à 32) : chaque écriture est
  validée par la règle seule (+1), par le témoin seul (−1) ou par les deux ou aucun (0) ; p⁺_g ~ Bêta de moyenne μ⁺ et
  de corrélation ρ ; p⁻_g = (1 − p⁺_g) r_g, r_g ~ Bêta de moyenne μ⁻ ÷ (1 − μ⁺) et de corrélation ρ (espérance μ⁻) ;
  y⁺_g ~ Binomiale(m_g ; p⁺_g), y⁻_g ~ Binomiale(m_g − y⁺_g ; r_g) ;
- quantité : 100 × Σ (y⁺ − y⁻) ÷ Σ m ; valeur vraie 100 × (μ⁺ − μ⁻) ; elle ne dépend ni de l'ordre ni du validateur
  (les validations au palier 1 n'en dépendent pas ; les corrections au palier 2, rares, ne sont pas simulées) ;
- réglage qui décide : μ⁺ = 0,25, μ⁻ = 0,15 (quantité fréquente : 40 % des écritures diffèrent) ; réglages rapportés
  sans effet sur le choix : (0,45 ; 0,05) et (0,10 ; 0,10) (différence nulle) ;
- 5 000 jeux par case, B = 2 000 ; graine 2026110531.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import csv  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import platform  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import numpy as np  # noqa: E402
import scipy  # noqa: E402

from . import couverture as CO  # noqa: E402
from . import intervalles as IC  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(ICI, "resultats_couverture_charge")

# ---- paramètres figés
GRAINE = 2026110531
RHOS = CO.RHOS
GS = CO.GS
REGLAGE_CRITERE = (0.25, 0.15)
REGLAGES_RAPPORTES = ((0.45, 0.05), (0.10, 0.10))
N_JEUX = 5000
B = 2000
PAQUET = 10
FICHIERS_CODE = ("couverture_charge.py", "couverture.py", "intervalles.py")


def valeur_vraie(reglage) -> float:
    return 100.0 * (reglage[0] - reglage[1])


def _beta(rng, mu: float, rho: float, forme) -> np.ndarray:
    if rho == 0 or mu <= 0:
        return np.full(forme, mu)
    return rng.beta(mu * (1 - rho) / rho, (1 - mu) * (1 - rho) / rho, size=forme)


def intervalles_paquet(rng, reglage, rho: float, G: int, J: int, B_: int = B) -> dict:
    mp, mm = reglage
    m = CO.tailles(G)
    M = int(m.sum())
    pp = _beta(rng, mp, rho, (J, G))
    r = _beta(rng, mm / (1 - mp), rho, (J, G))
    yp = rng.binomial(np.broadcast_to(m, (J, G)), pp)
    ym = rng.binomial(np.broadcast_to(m, (J, G)) - yp, r)
    a = (yp - ym).astype(float)
    centre = 100.0 * a.sum(axis=1) / M
    se = 100.0 * IC.se_rapport(a, np.broadcast_to(m, (J, G)))
    idx = rng.integers(0, G, size=(J, B_, G))
    ao = np.take_along_axis(np.broadcast_to(a[:, None, :], (J, B_, G)), idx, axis=2)
    mo = m[idx]
    boot = 100.0 * ao.sum(axis=2) / mo.sum(axis=2)
    se_boot = 100.0 * IC.se_rapport(ao, mo)
    jack = 100.0 * (a.sum(axis=1, keepdims=True) - a) / (M - m[None, :])
    return {"i": IC.ic_bootstrap_reuni(centre, boot), "ii": IC.ic_bootstrap_t(centre, se, boot, se_boot),
            "iii": IC.ic_jackknife_t(centre, jack), "percentile": IC.ic_percentile(boot), "_centre": centre}


def simuler_case(reglage, rho: float, G: int, n_jeux: int = N_JEUX, graine: int = GRAINE, B_: int = B,
                 paquet: int = PAQUET) -> list:
    ss = np.random.SeedSequence([int(graine), int(round(reglage[0] * 1000)), int(round(reglage[1] * 1000)),
                                 int(round(rho * 1000)), int(G)])
    rng = np.random.default_rng(ss)
    vrai = valeur_vraie(reglage)
    acc = {mth: dict(couvre=0, bas=0, haut=0, infinie=0, largeurs=[]) for mth in CO.METHODES_RAPPORTEES}
    centres, fait = [], 0
    while fait < n_jeux:
        J = min(paquet, n_jeux - fait)
        res = intervalles_paquet(rng, reglage, rho, G, J, B_)
        for mth in CO.METHODES_RAPPORTEES:
            lo, hi = (np.asarray(v, dtype=float) for v in res[mth])
            a = acc[mth]
            a["couvre"] += int(((lo <= vrai) & (vrai <= hi)).sum())
            a["bas"] += int((hi < vrai).sum())
            a["haut"] += int((lo > vrai).sum())
            inf = ~np.isfinite(lo) | ~np.isfinite(hi)
            a["infinie"] += int(inf.sum())
            a["largeurs"] += (hi - lo)[~inf].tolist()
        centres += res["_centre"].tolist()
        fait += J
    lignes = []
    for mth in CO.METHODES_RAPPORTEES:
        a = acc[mth]
        c = a["couvre"] / n_jeux
        larg = np.array(a["largeurs"]) if a["largeurs"] else np.array([np.nan])
        lignes.append(dict(mu_plus=reglage[0], mu_moins=reglage[1], rho=rho, G=G, methode=mth, n_jeux=n_jeux,
                           couverture=c, part_trop_bas=a["bas"] / n_jeux, part_trop_haut=a["haut"] / n_jeux,
                           part_infinie=a["infinie"] / n_jeux, largeur_mediane=float(np.nanmedian(larg)),
                           valeur_vraie=vrai, centre_moyen=float(np.mean(centres)),
                           critere=bool(tuple(reglage) == REGLAGE_CRITERE)))
    return lignes


def _travail(args):
    return simuler_case(*args)


def cases() -> list:
    return [(rg, r, g) for rg in (REGLAGE_CRITERE,) + REGLAGES_RAPPORTES for r in RHOS for g in GS]


def empreinte_code() -> dict:
    out = {}
    for n in FICHIERS_CODE:
        with open(os.path.join(ICI, n), "rb") as f:
            out[n] = hashlib.sha256(f.read()).hexdigest()
    return out


def choix_depuis_lignes(lignes: list, reglage=REGLAGE_CRITERE) -> dict:
    couv = {(l["methode"], l["rho"], l["G"]): l["couverture"] for l in lignes
            if (l["mu_plus"], l["mu_moins"]) == tuple(reglage)}
    return IC.choisir_methode(couv, RHOS, GS)


def lancer(dossier: str = DOSSIER, travailleurs: int = None, remplacer: bool = False) -> dict:
    if os.path.exists(os.path.join(dossier, "couverture.csv")) and not remplacer:
        raise SystemExit(f"{dossier} contient déjà des résultats : la simulation se lance une fois")
    os.makedirs(dossier, exist_ok=True)
    debut = time.time()
    travailleurs = travailleurs or min(len(cases()), os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=travailleurs) as ex:
        lignes = [l for r in ex.map(_travail, cases()) for l in r]
    with open(os.path.join(dossier, "couverture.csv"), "w", newline="", encoding="utf-8") as f:
        f.write("# Simulation de couverture, différence appariée de charge, données synthétiques "
                "(PLAN_EXPERIENCE.md, 5.13, Q13). Aucune donnée d'agent.\n")
        w = csv.DictWriter(f, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)
    choix = choix_depuis_lignes(lignes)
    inf = lambda v: "inf" if isinstance(v, float) and math.isinf(v) else v  # noqa: E731
    sortie = dict(methode_retenue=choix["methode"], nom=IC.NOMS_METHODES[choix["methode"]], repli=choix["repli"],
                  seuil=choix["seuil"], G_sur=inf(choix["G_sur"]), zone_echec=choix["zone_echec"],
                  pire_couverture=choix["pire"], methode_seconde=IC.methode_seconde(choix["methode"]),
                  reglage_critere=REGLAGE_CRITERE,
                  rapportes_sans_effet={str(rg): {k: inf(v) for k, v in choix_depuis_lignes(lignes, rg).items()}
                                        for rg in REGLAGES_RAPPORTES})
    with open(os.path.join(dossier, "choix.json"), "w", encoding="utf-8") as f:
        json.dump(sortie, f, ensure_ascii=False, indent=1)
        f.write("\n")
    meta = dict(objet="simulation de couverture, différence appariée de charge (PLAN_EXPERIENCE.md, 5.13, Q13)",
                donnees="synthétiques seulement", graine=GRAINE, rhos=RHOS, G=GS, reglage_critere=REGLAGE_CRITERE,
                reglages_rapportes=REGLAGES_RAPPORTES, tailles=CO.TAILLES, n_jeux=N_JEUX, B=B, paquet=PAQUET,
                seuil=IC.SEUIL_COUVERTURE, empreinte_code=empreinte_code(), python=sys.version.split()[0],
                numpy=np.__version__, scipy=scipy.__version__, machine=platform.platform(),
                debut=time.strftime("%Y-%m-%d %H:%M:%S %z", time.localtime(debut)),
                duree_s=round(time.time() - debut, 1), travailleurs=travailleurs)
    with open(os.path.join(dossier, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return sortie


def verifier(dossier: str = DOSSIER) -> list:
    with open(os.path.join(dossier, "meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    return [f"{n} a changé depuis la simulation" for n, h in empreinte_code().items()
            if meta["empreinte_code"].get(n) != h]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--lancer", action="store_true")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--travailleurs", type=int, default=None)
    a = p.parse_args(argv)
    if a.lancer:
        print(json.dumps(lancer(travailleurs=a.travailleurs), ensure_ascii=False, indent=1))
    if a.verifier:
        ecarts = [f"première simulation : {e}" for e in CO.verifier()] + \
                 [f"différence de charge : {e}" for e in verifier()]
        print("\n".join(ecarts) if ecarts else "code conforme aux résultats des deux simulations")
        return 1 if ecarts else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
