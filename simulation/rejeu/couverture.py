"""Simulation de couverture des trois méthodes d'intervalle candidates (PLAN_EXPERIENCE.md, 5.13 ; 5.16, point 5 ;
contrôle 1, B4). Données synthétiques seulement : aucune donnée d'agent n'est lue.

Usage (depuis simulation/) :
    .venv/bin/python -m rejeu.couverture --lancer      une seule fois ; écrit rejeu/resultats_couverture/
    .venv/bin/python -m rejeu.couverture --verifier    compare l'empreinte du code à celle des résultats écrits

Paramètres écrits et figés AVANT le lancement (5.16, point 5 : « les taux, les tailles de tâches et le nombre de jeux
sont écrits dans le code avant de lancer la simulation, et figés avec lui ») ; raisons dans CHOIX_PHASE2.md :
- grille du plan : ρ ∈ {0 ; 0,1 ; 0,3 ; 0,5 ; 0,7 ; 0,9}, G ∈ {20 ; 40 ; 90} grappes (tâches), une strate ;
- taux d'erreur par écriture qui décide du choix : 0,05 (l'ordre du taux d'alertes du pilote, 7 pour 148 écritures,
  plan 4.1) ; taux rapportés sans effet sur le choix : 0,01 et 0,20 ;
- tailles des tâches (écritures par tâche) : la tâche g en compte TAILLES[g mod 10], de 1 à 32 (moyenne 10,8) ;
- 5 000 jeux par case (au moins 1 000, plan) ; B = 2 000 répétitions bootstrap, K = 10 tirages du validateur ;
  e = 5 % ; graine maîtresse GRAINE.

Modèle d'un jeu : taux de la tâche g, p_g ~ Bêta(μ(1 − ρ) ÷ ρ ; (1 − μ)(1 − ρ) ÷ ρ) (corrélation ρ entre deux écritures
d'une même tâche ; p_g = μ si ρ = 0) ; erreurs x_g ~ Binomiale(m_g ; p_g). Quantité : les dégâts en plus pour 100
écritures de « tout approuver », 100 × Σ y ÷ Σ m, où y compte les erreurs exécutées que le validateur aurait
arrêtées (u_val ≥ e) ; valeur vraie connue : 100 × (1 − e) × μ. La quantité ne dépend pas de l'ordre : les K « ordres »
d'une répétition se réduisent à K tirages du validateur. Valeur centrale : 100 × (1 − e) × Σ x ÷ Σ m, limite exacte
de la moyenne des R0 répétitions. Jackknife : chaque tâche retirée des K mêmes tirages (nombres aléatoires communs,
comme le rejeu, qui retire la tâche des K mêmes ordres).
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

from . import intervalles as IC  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.path.join(ICI, "resultats_couverture")

# ---- paramètres figés (voir l'en-tête et CHOIX_PHASE2.md)
GRAINE = 2026110521
RHOS = (0.0, 0.1, 0.3, 0.5, 0.7, 0.9)
GS = (20, 40, 90)
TAUX_CRITERE = 0.05
TAUX_RAPPORTES = (0.01, 0.20)
TAILLES = (1, 2, 3, 4, 6, 8, 12, 16, 24, 32)
N_JEUX = 5000
B = 2000
K = 10
E_VALIDATEUR = 0.05
PAQUET = 10            # jeux tirés ensemble (fixe : il règle la consommation des nombres aléatoires)
METHODES_RAPPORTEES = ("i", "ii", "iii", "percentile")
FICHIERS_CODE = ("couverture.py", "intervalles.py")


def tailles(G: int) -> np.ndarray:
    return np.array([TAILLES[g % len(TAILLES)] for g in range(G)], dtype=np.int64)


def valeur_vraie(taux: float, e: float = E_VALIDATEUR) -> float:
    return 100.0 * (1 - e) * taux


def _taux_taches(rng, taux: float, rho: float, forme: tuple) -> np.ndarray:
    if rho == 0:
        return np.full(forme, taux)
    a, b = taux * (1 - rho) / rho, (1 - taux) * (1 - rho) / rho
    return rng.beta(a, b, size=forme)


def intervalles_paquet(rng, taux: float, rho: float, G: int, J: int, B_: int = B, K_: int = K,
                       e: float = E_VALIDATEUR) -> dict:
    """J jeux synthétiques et leurs intervalles par les quatre méthodes rapportées : {méthode: (lo, hi)} (J,)."""
    m = tailles(G)
    M = int(m.sum())
    p = _taux_taches(rng, taux, rho, (J, G))
    x = rng.binomial(np.broadcast_to(m, (J, G)), p)
    centre = 100.0 * (1 - e) * x.sum(axis=1) / M
    se = 100.0 * IC.se_rapport((1 - e) * x, np.broadcast_to(m, (J, G)))
    # bootstrap par grappes : G tâches tirées avec remise ; K tirages du validateur par occurrence
    idx = rng.integers(0, G, size=(J, B_, G))
    xo = np.take_along_axis(np.broadcast_to(x[:, None, :], (J, B_, G)), idx, axis=2)
    mo = m[idx]
    yo = rng.binomial(K_ * xo, 1 - e) / K_
    Mb = mo.sum(axis=2)
    boot = 100.0 * yo.sum(axis=2) / Mb
    se_boot = 100.0 * IC.se_rapport(yo, mo)
    # jackknife : la tâche g retirée des K mêmes tirages
    Y = rng.binomial(K_ * x, 1 - e)
    jack = 100.0 * (Y.sum(axis=1, keepdims=True) - Y) / (K_ * (M - m[None, :]))
    out = {"i": IC.ic_bootstrap_reuni(centre, boot), "ii": IC.ic_bootstrap_t(centre, se, boot, se_boot),
           "iii": IC.ic_jackknife_t(centre, jack), "percentile": IC.ic_percentile(boot)}
    out["_centre"] = centre
    out["_sans_erreur"] = x.sum(axis=1) == 0
    return out


def simuler_case(taux: float, rho: float, G: int, n_jeux: int = N_JEUX, graine: int = GRAINE, B_: int = B,
                 K_: int = K, e: float = E_VALIDATEUR, paquet: int = PAQUET) -> list:
    """Lignes de couverture d'une case (taux, ρ, G), une par méthode."""
    ss = np.random.SeedSequence([int(graine), int(round(taux * 10000)), int(round(rho * 1000)), int(G)])
    rng = np.random.default_rng(ss)
    vrai = valeur_vraie(taux, e)
    acc = {mth: dict(couvre=0, bas=0, haut=0, infinie=0, reduite=0, largeurs=[]) for mth in METHODES_RAPPORTEES}
    centres, sans_erreur, fait = [], 0, 0
    while fait < n_jeux:
        J = min(paquet, n_jeux - fait)
        res = intervalles_paquet(rng, taux, rho, G, J, B_, K_, e)
        for mth in METHODES_RAPPORTEES:
            lo, hi = (np.asarray(v, dtype=float) for v in res[mth])
            a = acc[mth]
            a["couvre"] += int(((lo <= vrai) & (vrai <= hi)).sum())
            a["bas"] += int((hi < vrai).sum())
            a["haut"] += int((lo > vrai).sum())
            inf = ~np.isfinite(lo) | ~np.isfinite(hi)
            a["infinie"] += int(inf.sum())
            a["reduite"] += int((lo == hi).sum())
            a["largeurs"] += (hi - lo)[~inf].tolist()
        centres += res["_centre"].tolist()
        sans_erreur += int(res["_sans_erreur"].sum())
        fait += J
    lignes = []
    for mth in METHODES_RAPPORTEES:
        a = acc[mth]
        c = a["couvre"] / n_jeux
        z2 = IC.Z95 ** 2
        den = 1 + z2 / n_jeux
        ctr = (c + z2 / (2 * n_jeux)) / den
        demi = IC.Z95 * math.sqrt(c * (1 - c) / n_jeux + z2 / (4 * n_jeux ** 2)) / den
        larg = np.array(a["largeurs"]) if a["largeurs"] else np.array([np.nan])
        lignes.append(dict(taux=taux, rho=rho, G=G, methode=mth, n_jeux=n_jeux, couverture=c,
                           couverture_mc_lo=max(0.0, ctr - demi), couverture_mc_hi=min(1.0, ctr + demi),
                           part_trop_bas=a["bas"] / n_jeux, part_trop_haut=a["haut"] / n_jeux,
                           part_infinie=a["infinie"] / n_jeux, part_reduite=a["reduite"] / n_jeux,
                           largeur_mediane=float(np.nanmedian(larg)), valeur_vraie=vrai,
                           centre_moyen=float(np.mean(centres)), part_jeux_sans_erreur=sans_erreur / n_jeux,
                           critere=bool(taux == TAUX_CRITERE)))
    return lignes


def _travail(args):
    return simuler_case(*args)


def cases() -> list:
    return [(t, r, g) for t in (TAUX_CRITERE,) + TAUX_RAPPORTES for r in RHOS for g in GS]


def empreinte_code() -> dict:
    out = {}
    for n in FICHIERS_CODE:
        with open(os.path.join(ICI, n), "rb") as f:
            out[n] = hashlib.sha256(f.read()).hexdigest()
    return out


def choix_depuis_lignes(lignes: list, taux: float = TAUX_CRITERE) -> dict:
    couv = {(l["methode"], l["rho"], l["G"]): l["couverture"] for l in lignes if l["taux"] == taux}
    return IC.choisir_methode(couv, RHOS, GS)


def lancer(dossier: str = DOSSIER, travailleurs: int = None, remplacer: bool = False) -> dict:
    if os.path.exists(os.path.join(dossier, "couverture.csv")) and not remplacer:
        raise SystemExit(f"{dossier} contient déjà des résultats : la simulation se lance une fois (--remplacer pour "
                         "écraser, à déclarer)")
    os.makedirs(dossier, exist_ok=True)
    debut = time.time()
    travailleurs = travailleurs or min(len(cases()), os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=travailleurs) as ex:
        resultats = list(ex.map(_travail, cases()))
    lignes = [l for r in resultats for l in r]
    champs = list(lignes[0])
    with open(os.path.join(dossier, "couverture.csv"), "w", newline="", encoding="utf-8") as f:
        f.write("# Simulation de couverture sur données synthétiques (PLAN_EXPERIENCE.md, 5.16, point 5). "
                "Aucune donnée d'agent.\n")
        w = csv.DictWriter(f, fieldnames=champs)
        w.writeheader()
        w.writerows(lignes)
    choix = choix_depuis_lignes(lignes)
    choix_rapportes = {str(t): choix_depuis_lignes(lignes, t) for t in TAUX_RAPPORTES}
    nettoyer = lambda c: {k: (v if not (isinstance(v, float) and math.isinf(v)) else "inf")  # noqa: E731
                          for k, v in c.items()}
    sortie = dict(
        methode_retenue=choix["methode"], nom=IC.NOMS_METHODES[choix["methode"]], repli=choix["repli"],
        seuil=choix["seuil"], G_sur=choix["G_sur"] if not math.isinf(choix["G_sur"]) else "inf",
        zone_echec=choix["zone_echec"], pire_couverture=choix["pire"], methode_seconde=IC.methode_seconde(
            choix["methode"]), taux_critere=TAUX_CRITERE,
        rapportes_sans_effet={t: nettoyer(c) for t, c in choix_rapportes.items()})
    with open(os.path.join(dossier, "choix.json"), "w", encoding="utf-8") as f:
        json.dump(sortie, f, ensure_ascii=False, indent=1)
        f.write("\n")
    meta = dict(
        objet="simulation de couverture des méthodes d'intervalle (PLAN_EXPERIENCE.md, 5.13 ; 5.16, point 5)",
        donnees="synthétiques seulement", graine=GRAINE, rhos=RHOS, G=GS, taux_critere=TAUX_CRITERE,
        taux_rapportes=TAUX_RAPPORTES, tailles=TAILLES, n_jeux=N_JEUX, B=B, K=K, e=E_VALIDATEUR, paquet=PAQUET,
        seuil=IC.SEUIL_COUVERTURE, empreinte_code=empreinte_code(), python=sys.version.split()[0],
        numpy=np.__version__, scipy=scipy.__version__, machine=platform.platform(),
        debut=time.strftime("%Y-%m-%d %H:%M:%S %z", time.localtime(debut)), duree_s=round(time.time() - debut, 1),
        travailleurs=travailleurs)
    with open(os.path.join(dossier, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return sortie


def lire_choix(dossier: str = DOSSIER) -> dict:
    """Le choix écrit par la simulation (méthode retenue, repli, zone qui échoue)."""
    with open(os.path.join(dossier, "choix.json"), encoding="utf-8") as f:
        c = json.load(f)
    c["G_sur"] = math.inf if c["G_sur"] == "inf" else c["G_sur"]
    return dict(methode=c["methode_retenue"], repli=c["repli"], G_sur=c["G_sur"], zone_echec=c["zone_echec"],
                pire=c["pire_couverture"], seuil=c["seuil"], methode_seconde=c["methode_seconde"])


def verifier(dossier: str = DOSSIER) -> list:
    with open(os.path.join(dossier, "meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    ecarts = [f"{n} a changé depuis la simulation" for n, h in empreinte_code().items()
              if meta["empreinte_code"].get(n) != h]
    return ecarts


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--lancer", action="store_true")
    p.add_argument("--verifier", action="store_true")
    p.add_argument("--remplacer", action="store_true")
    p.add_argument("--travailleurs", type=int, default=None)
    a = p.parse_args(argv)
    if a.lancer:
        s = lancer(travailleurs=a.travailleurs, remplacer=a.remplacer)
        print(json.dumps(s, ensure_ascii=False, indent=1))
    if a.verifier:
        e = verifier()
        print("\n".join(e) if e else "code conforme aux résultats de la simulation")
        return 1 if e else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
