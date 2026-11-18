"""Cinquième passage du contrôle 3, partie R4 : la règle amendée le 07/11 (moteur au commit 6c02d69), confirmée sur de
nouveaux tirages. Méthode écrite et figée avant le lancement : `METHODE.md` (ce dossier).

Usage (depuis simulation/) :
    env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/passage5_r4/passage5_r4.py --tester
    … --pilote      quelques tirages chronométrés (rien n'est écrit)
    … --lancer      une seule fois ; écrit meta.json, tirages.csv, passage5_r4.csv, tailles_inegales.csv, passage5_r4.md
    … --resumer     refait les tableaux à partir des tirages (aucun calcul du moteur)
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import csv  # noqa: E402
import hashlib  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import platform  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import types  # noqa: E402
from multiprocessing import get_context  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.abspath(os.path.join(ICI, "..", ".."))
OPTIONS = os.path.join(SIM, "controle3", "options_r4")
sys.path.insert(0, SIM)
sys.path.insert(0, OPTIONS)

import numpy as np  # noqa: E402

import options_r4 as O  # noqa: E402  (mondes mixtes M1-bis et M2, cas du 06/11 pour le recoupement)
from controle3 import harnais as H  # noqa: E402
from controle3 import lancer as L  # noqa: E402
from controle3 import mondes as MD  # noqa: E402
from rejeu import classes as CL  # noqa: E402
from rejeu import config_rejeu as CR  # noqa: E402
from rejeu import decision as DE  # noqa: E402
from rejeu import preuves as PR  # noqa: E402
from rejeu import suites as SU  # noqa: E402

# ---- paramètres figés (METHODE.md)
GRAINE = 2026110701
PROCESSUS = 12
RHOS = (0.0, 0.3, 0.7, 0.9, 1.0)
TEMOINS = (False, True)
MULT_A, MULT_B = (0.0, 0.2, 0.5, 1.0), (2.0, 3.0, 5.0, 10.0)
LOGIT_RHOS, LOGIT_A, LOGIT_B = (0.3, 0.7, 0.9), (0.0, 0.5, 1.0), (2.0, 3.0, 5.0)
HET_A, HET_B = (0.0, 0.5, 1.0), (2.0, 3.0)
REPS_A, REPS_B, REPS_CRIT, REPS_VOL = 1000, 300, 10_000, 300
FRACTIONS, VOL_MULT, VOL_RHO = (0.1, 1 / 3), (0.2, 1.0, 5.0), 0.3
SEUIL_ETAPE2_1X, SEUIL_ETAPE2_BAS = 0.03, 0.005
CIBLE_1X, CIBLE_BAS = 0.05, 0.01
N_TAILLES = 200_000
BARRES_TAILLES = (("WorkBench faible", 947 / 125020), ("commerce faible", 88 / 3325), ("WorkBench moyen", 947 / 549100))
PROFILS = ("300 tâches de 7", "300 tâches géométriques (moyenne 3)", "300 tâches de Pareto (1,5 ; max 200)",
           "100 tâches de 1 et 1 de 100", "100 tâches de 1 et 3 de 100")
VALIDATION_CAS = ("grille 5x rho=0 tenus", "grille 5x rho=0 defaut", "grille 1x rho=1 tenus", "grille 3x rho=0.3 tenus",
                  "grille 2x rho=0.7 tenus", "grille 1x rho=0.9 defaut")
CONFIGS = [(env, m) for env in MD.ENVS for m in CR.MODELES]
HAIKU = CR.MODELES[0]
OUI = dict(tenu=True)
MOTIFS = {"": 0, DE.MOTIF_AUCUN_JUGEABLE: 1, DE.MOTIF_NON_ETABLI: 2, DE.MOTIF_RHO_PROPRE: 3}

METHODE = os.path.join(ICI, "METHODE.md")
META = os.path.join(ICI, "meta.json")
TIRAGES = os.path.join(ICI, "tirages.csv")
SORTIE = os.path.join(ICI, "passage5_r4.csv")
TAILLES = os.path.join(ICI, "tailles_inegales.csv")
RESUME = os.path.join(ICI, "passage5_r4.md")
COLONNES = ["cas", "nom", "groupe", "rep", "issue", "motif", "deleg", "jug", "etab", "etab_rp", "commerce_jug",
            "wb_haiku_bascule", "wb_haiku_rho_propre"]


# --------------------------------------------------------------------------
# Cases (METHODE.md, 3 et 5)
# --------------------------------------------------------------------------
def _tem(t: bool) -> str:
    return "defaut" if t else "tenus"


def _case(groupe, mec, r, m, t, reps, indice, fraction=None, monde="grille", nom=None) -> dict:
    nom = nom or f"{groupe} {mec} {m:g}x rho={r:g} {_tem(t)}"
    return dict(nom=nom, groupe=groupe, monde=monde, mecanisme=mec, multiple=m, rho=r, temoins=t, reps=reps,
                indice=indice, fraction=fraction)


def construire_cas() -> list:
    cas = []
    spec_a = ([("beta", r, m, t) for t in TEMOINS for r in RHOS for m in MULT_A]
              + [("logit_normal", r, m, t) for t in TEMOINS for r in LOGIT_RHOS for m in LOGIT_A]
              + [("heterogene", 0.0, m, t) for t in TEMOINS for m in HET_A])
    cas += [_case("A", mec, r, m, t, REPS_A, 1000 + i) for i, (mec, r, m, t) in enumerate(spec_a)]
    spec_b = ([("beta", r, m, t) for t in TEMOINS for r in RHOS for m in MULT_B]
              + [("logit_normal", r, m, t) for t in TEMOINS for r in LOGIT_RHOS for m in LOGIT_B]
              + [("heterogene", 0.0, m, t) for t in TEMOINS for m in HET_B])
    cas += [_case("B", mec, r, m, t, REPS_B, 2000 + i) for i, (mec, r, m, t) in enumerate(spec_b)]
    spec_c = ([("beta", r, 1.0, t) for r in (0.7, 0.9, 1.0) for t in TEMOINS] + [("logit_normal", 0.9, 1.0, False)]
              + [("beta", 1.0, 0.5, t) for t in TEMOINS])
    cas += [_case("critique", mec, r, m, t, REPS_CRIT, 3000 + i) for i, (mec, r, m, t) in enumerate(spec_c)]
    n = len(spec_c)
    cas.append(_case("critique", "beta", 0.0, 1.0, False, REPS_CRIT, 3000 + n, monde="M1-bis", nom="critique M1-bis"))
    cas.append(_case("critique", "beta", 0.3, 0.2, False, REPS_CRIT, 3000 + n + 1, monde="M2", nom="critique M2"))
    spec_v = [(f, m) for f in FRACTIONS for m in VOL_MULT]
    cas += [_case("volumes", "beta", VOL_RHO, m, False, REPS_VOL, 5000 + i, fraction=f,
                  nom=f"volumes f={f:.3g} beta {m:g}x rho={VOL_RHO:g} tenus") for i, (f, m) in enumerate(spec_v)]
    return cas


CAS = construire_cas()


def cases_ajoutees(parts_a: dict) -> list:
    """Deuxième étape (METHODE.md, 3.4) : parts_a = {nom de case de grille A: part de R4}. Une case au multiple 1 au-dessus
    de 3 %, ou aux multiples 0 à 0,5 au-dessus de 0,5 %, devient une case critique si elle ne l'est pas déjà."""
    deja = {(c["mecanisme"], c["rho"], c["multiple"], c["temoins"]) for c in CAS if c["groupe"] == "critique"
            and c["monde"] == "grille"}
    out = []
    for i, c in enumerate(x for x in CAS if x["groupe"] == "A"):
        part = parts_a[c["nom"]]
        seuil = SEUIL_ETAPE2_1X if c["multiple"] >= 1.0 else SEUIL_ETAPE2_BAS
        if part > seuil and (c["mecanisme"], c["rho"], c["multiple"], c["temoins"]) not in deja:
            out.append(_case("ajoutée", c["mecanisme"], c["rho"], c["multiple"], c["temoins"], REPS_CRIT, 4000 + i,
                             nom="ajoutée " + c["nom"][2:]))
    return out


def monde_du_cas(c: dict):
    if c["monde"] == "grille":
        return H.monde_delegabilite(c["multiple"], c["rho"], c["temoins"], c["mecanisme"])
    return O.monde_du_cas(dict(monde=c["monde"]))


def sous_echantillon(cal: dict, f: float, indice: int, rep: int) -> dict:
    """Volumes réduits (METHODE.md, 3.5) : une fraction f des tâches de calibration de chaque environnement, tirées au
    hasard sans remise."""
    rng = np.random.default_rng(np.random.SeedSequence([GRAINE, int(indice), int(rep), 1]))
    out = {}
    for env in sorted(cal):
        t = list(cal[env])
        k = max(1, int(round(f * len(t))))
        out[env] = sorted(t[i] for i in rng.choice(len(t), size=k, replace=False))
    return out


# --------------------------------------------------------------------------
# Un tirage : la règle du moteur, et ses contrôles (METHODE.md, 2 et 6.2)
# --------------------------------------------------------------------------
_CFG = None


def config():
    global _CFG
    if _CFG is None:
        _CFG = CR.charger_config()
    return _CFG


def _bits(d: dict) -> str:
    return "".join("1" if d[c] else "0" for c in CONFIGS)


def motif_attendu(st: dict) -> str:
    """Le motif recalculé à la main, dans l'ordre écrit (contrôle de `decision.point4`)."""
    if any(s["delegable"] for s in st.values()):
        return ""
    jug = [c for c in CONFIGS if st[c]["jugeable"]]
    if not jug:
        return DE.MOTIF_AUCUN_JUGEABLE
    non = [c for c in jug if not st[c]["etablie"]]
    if not non:
        return ""
    return DE.MOTIF_RHO_PROPRE if all(st[c]["etablie_rho_propre"] for c in non) else DE.MOTIF_NON_ETABLI


def evaluer(jks: dict, cfg) -> dict:
    cls = CL.classes_tous_environnements(jks, cfg)
    st = {(env, m): CL.statut_configuration(cls[env][m], CL.rho_propre(jks[env][m])) for env, m in CONFIGS}
    an = types.SimpleNamespace(delegables={c: s["delegable"] for c, s in st.items()},
                               jugeables={c: s["jugeable"] for c, s in st.items()}, statuts=st)
    p4 = DE.point4(an)
    et = DE.etiquette(OUI, OUI, OUI, p4)
    # contrôles (6.2) : un écart arrête le script
    if et == "R4" and (p4["tenu"] or not any(s["jugeable"] for s in st.values())
                       or not all(s["etablie"] for s in st.values() if s["jugeable"])):
        raise AssertionError("R4 sans dépassement établi dans chaque configuration jugeable")
    for c, s in st.items():
        if s["etablie"] and not (s["etablie_rho_propre"] and s["rho_bascule"] == 1.0):
            raise AssertionError(f"{c} : établie sans lecture au ρ̂ propre ou sans ρ* = 1")
    if p4["motif"] != motif_attendu(st):
        raise AssertionError(f"motif {p4['motif']!r} au lieu de {motif_attendu(st)!r}")
    if p4["tenu"] != (et == "confirmée") or (not p4["tenu"] and et not in ("R4", DE.PREUVES_INSUFFISANTES)):
        raise AssertionError(f"étiquette {et} incohérente avec le point 4")
    wb = st[("WorkBench", HAIKU)]
    return dict(issue="D" if p4["tenu"] else ("R4" if et == "R4" else "PI"), motif=MOTIFS[p4["motif"]],
                deleg=_bits({c: s["delegable"] for c, s in st.items()}),
                jug=_bits({c: s["jugeable"] for c, s in st.items()}),
                etab=_bits({c: s["etablie"] for c, s in st.items()}),
                etab_rp=_bits({c: s["etablie_rho_propre"] for c, s in st.items()}),
                commerce_jug=int(any(st[("commerce", m)]["jugeable"] for m in CR.MODELES)),
                wb_haiku_bascule="" if wb["rho_bascule"] is None else round(wb["rho_bascule"], 6),
                wb_haiku_rho_propre="" if wb["rho_propre"] is None else round(wb["rho_propre"], 6))


def jeux_calibration(g: dict, cal: dict) -> dict:
    e = g["entrees"]
    prep = PR.preparer(e, "confirmes")
    return {env: {m: SU.jeu_configuration(prep, e, env, m, cal[env], "calibration") for m in CR.MODELES}
            for env in MD.ENVS}


def tirage(args) -> dict:
    c, rep = args
    cfg = config()
    rng = np.random.default_rng(np.random.SeedSequence([GRAINE, int(c["indice"]), int(rep)]))
    g = O.generer(monde_du_cas(c), rng, cfg)
    cal = sous_echantillon(g["cal"], c["fraction"], c["indice"], rep) if c["fraction"] else g["cal"]
    r = evaluer(jeux_calibration(g, cal), cfg)
    r.update(cas=c["indice"], nom=c["nom"], groupe=c["groupe"], rep=int(rep))
    return r


def tirage_options(args) -> tuple:
    """Validation 1 : un tirage de l'étude du 06/11, avec sa graine, évalué par le moteur amendé."""
    i_cas, rep = args
    c = O.CAS[i_cas]
    cfg = config()
    rng = np.random.default_rng(np.random.SeedSequence([int(O.GRAINE), 1000 + int(c["indice"]), int(rep)]))
    g = O.generer(O.monde_du_cas(c), rng, cfg)
    r = evaluer(jeux_calibration(g, g["cal"]), cfg)
    return i_cas, r["issue"], r["motif"]


# --------------------------------------------------------------------------
# Tâches de tailles inégales (METHODE.md, 4)
# --------------------------------------------------------------------------
def profil(nom: str, rng) -> np.ndarray:
    if nom == PROFILS[0]:
        return np.full(300, 7.0)
    if nom == PROFILS[1]:
        return rng.geometric(1 / 3, size=300).astype(float)
    if nom == PROFILS[2]:
        return np.minimum(np.floor(rng.pareto(1.5, size=300) + 1.0), 200.0)
    if nom == PROFILS[3]:
        return np.array([1.0] * 100 + [100.0])
    if nom == PROFILS[4]:
        return np.array([1.0] * 100 + [100.0] * 3)
    raise ValueError(nom)


def etabli_x(tailles: np.ndarray, barre: float, cache: dict, x: float) -> bool:
    """Dépassement établi, par le moteur, pour x erreurs (tâches ratées en entier) sur ce profil."""
    if x not in cache:
        n = float(tailles.sum())
        ne1 = n ** 2 / float((tailles ** 2).sum())
        cache[x] = CL.depassement_etabli(CL.classer(int(x), int(n), barre, n_eff=ne1, n_eff_preuve=ne1))
    return cache[x]


def part_etablie(tailles: np.ndarray, barre: float, p: float, n_sim: int, rng, tranche: int = 20_000) -> int:
    cache, k = {}, 0
    for debut in range(0, n_sim, tranche):
        m = min(tranche, n_sim - debut)
        x = (rng.random((m, tailles.size)) < p) @ tailles
        vals, nb = np.unique(x, return_counts=True)
        k += int(sum(int(c) for v, c in zip(vals, nb) if etabli_x(tailles, barre, cache, float(v))))
    return k


def part_etablie_exacte(tailles: np.ndarray, barre: float, p: float) -> float:
    """Calcul exact par énumération (petits profils, auto-tests)."""
    cache, tot = {}, 0.0
    for b in itertools.product((0, 1), repeat=tailles.size):
        b = np.array(b)
        if etabli_x(tailles, barre, cache, float(b @ tailles)):
            tot += p ** b.sum() * (1 - p) ** (tailles.size - b.sum())
    return tot


def tache_tailles(args) -> dict:
    i_prof, i_barre, mult = args
    nom, (nb, barre) = PROFILS[i_prof], BARRES_TAILLES[i_barre]
    rng_p = np.random.default_rng(np.random.SeedSequence([GRAINE, 6000 + i_prof]))
    t = profil(nom, rng_p)
    rng = np.random.default_rng(np.random.SeedSequence([GRAINE, 6000 + i_prof, i_barre, int(mult * 10)]))
    k = part_etablie(t, barre, mult * barre, N_TAILLES, rng)
    n = float(t.sum())
    return dict(profil=nom, barre=nb, multiple=mult, taches=int(t.size), ecritures=int(n),
                n_eff_preuve=round(n ** 2 / float((t ** 2).sum()), 3), etablis=k, n=N_TAILLES)


# --------------------------------------------------------------------------
# Lancement
# --------------------------------------------------------------------------
def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple:
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def sha256(chemin: str) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def _ecrire_meta(meta: dict) -> None:
    with open(META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1, default=str)


def recoupement(pool) -> dict:
    """Validation 1 (METHODE.md, 6.1)."""
    attendu = {r["nom"]: r for r in csv.DictReader(open(os.path.join(OPTIONS, "diagnostic_types.csv"),
                                                        encoding="utf-8"))}
    idx = {c["nom"]: i for i, c in enumerate(O.CAS) if c["nom"] in VALIDATION_CAS}
    taches = [(idx[n], r) for n in VALIDATION_CAS for r in range(int(attendu[n]["n"]))]
    res = pool.map(tirage_options, taches, chunksize=10)
    out = {}
    for n in VALIDATION_CAS:
        rs = [(iss, mo) for i, iss, mo in res if i == idx[n]]
        r4 = sum(iss == "R4" for iss, _ in rs)
        m3 = sum(iss == "PI" and mo == MOTIFS[DE.MOTIF_RHO_PROPRE] for iss, mo in rs)
        out[n] = dict(n=len(rs), R4=r4, C_rho1_J=int(attendu[n]["C-rho1-J"]), R4_plus_motif3=r4 + m3,
                      C_hybride_J=int(attendu[n]["C-hybride-J"]))
        out[n]["ecart"] = not (r4 == out[n]["C_rho1_J"] and r4 + m3 == out[n]["C_hybride_J"])
    return out


def phase(pool, cases: list, ecrivain, t0: float, nom: str, chunksize: int) -> dict:
    """Tire toutes les répétitions des cases ; rend {nom de case: [issues]} et écrit chaque tirage."""
    taches = [(c, r) for c in cases for r in range(c["reps"])]
    par_cas = {c["nom"]: [] for c in cases}
    for i, r in enumerate(pool.imap(tirage, taches, chunksize=chunksize), 1):
        ecrivain.writerow({k: r[k] for k in COLONNES})
        par_cas[r["nom"]].append(r["issue"])
        if i % 20_000 == 0 or i == len(taches):
            print(f"[{time.time() - t0:7.0f} s] {nom} : {i}/{len(taches)}", flush=True)
    return par_cas


def lancer() -> int:
    if os.path.exists(META):
        raise SystemExit("meta.json existe déjà : ce passage se lance une seule fois")
    if not os.path.exists(METHODE):
        raise SystemExit("METHODE.md manque : la méthode doit être écrite avant le lancement")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=SIM, capture_output=True, text=True).stdout.strip()
    sale = subprocess.run(["git", "status", "--porcelain", "--", "rejeu", "controle3/mondes.py", "controle3/harnais.py",
                           "controle3/options_r4/options_r4.py"], cwd=SIM, capture_output=True, text=True).stdout
    if sale.strip():
        raise SystemExit("le moteur a des modifications non commitées :\n" + sale)
    t0 = time.time()
    meta = dict(statut="en cours", debut=time.strftime("%Y-%m-%d %H:%M:%S"), commit=commit, graine=GRAINE,
                methode_sha256=sha256(METHODE), script_sha256=sha256(os.path.abspath(__file__)),
                empreintes_moteur=L.empreintes(), processus=PROCESSUS,
                cases=[{k: v for k, v in c.items()} for c in CAS], seuils_etape2=[SEUIL_ETAPE2_1X, SEUIL_ETAPE2_BAS],
                python=sys.version.split()[0], numpy=np.__version__, machine=platform.platform())
    _ecrire_meta(meta)
    ctx = get_context("spawn")
    with ctx.Pool(PROCESSUS) as pool:
        val = recoupement(pool)
        meta["validation_recoupement"] = val
        meta["duree_validation_s"] = round(time.time() - t0, 1)
        _ecrire_meta(meta)
        if any(v["ecart"] for v in val.values()):
            meta["statut"] = "arrêté : écart au recoupement"
            _ecrire_meta(meta)
            print(json.dumps(val, ensure_ascii=False, indent=1))
            return 1
        print(f"[{time.time() - t0:7.0f} s] recoupement : 0 écart", flush=True)
        with open(TIRAGES, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLONNES)
            w.writeheader()
            grille_a = [c for c in CAS if c["groupe"] == "A"]
            res_a = phase(pool, grille_a, w, t0, "grille A", 20)
            parts_a = {n: sum(i == "R4" for i in v) / len(v) for n, v in res_a.items()}
            ajoutees = cases_ajoutees(parts_a)
            meta["cases_ajoutees"] = ajoutees
            meta["duree_grille_a_s"] = round(time.time() - t0, 1)
            _ecrire_meta(meta)
            print(f"[{time.time() - t0:7.0f} s] deuxième étape : {len(ajoutees)} case(s) ajoutée(s) : "
                  + "; ".join(c["nom"] for c in ajoutees), flush=True)
            phase(pool, [c for c in CAS if c["groupe"] == "critique"] + ajoutees, w, t0, "cases critiques", 50)
            meta["duree_critiques_s"] = round(time.time() - t0, 1)
            phase(pool, [c for c in CAS if c["groupe"] in ("B", "volumes")], w, t0, "grille B et volumes", 20)
        lignes = pool.map(tache_tailles, [(i, j, m) for i in range(len(PROFILS)) for j in range(len(BARRES_TAILLES))
                                          for m in (1.0, 0.5)])
    with open(TAILLES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)
    with open(TIRAGES + ".sha256", "w", encoding="utf-8") as f:
        f.write(f"{sha256(TIRAGES)}  tirages.csv\n")
    meta.update(statut="terminé", fin=time.strftime("%Y-%m-%d %H:%M:%S"), duree_s=round(time.time() - t0, 1))
    _ecrire_meta(meta)
    resumer()
    return 0


# --------------------------------------------------------------------------
# Tableaux
# --------------------------------------------------------------------------
def lire_tirages() -> dict:
    par = {}
    with open(TIRAGES, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            par.setdefault(r["nom"], []).append(r)
    return par


def pc(x: float, d: int = 2) -> str:
    return f"{100 * x:.{d}f}".replace(".", ",")


def stats(c: dict, rs: list) -> dict:
    n = len(rs)
    r4 = sum(r["issue"] == "R4" for r in rs)
    tort = sum(r["issue"] == "R4" and r["commerce_jug"] == "1" for r in rs) if c["monde"] == "M2" else r4
    d = dict(nom=c["nom"], groupe=c["groupe"], mecanisme=c["mecanisme"], rho=c["rho"], multiple=c["multiple"],
             temoins=c["temoins"], fraction=c["fraction"] or "", n=n,
             delegable=sum(r["issue"] == "D" for r in rs), R4=r4, R4_a_tort=tort,
             PI_aucun_jugeable=sum(r["motif"] == "1" for r in rs), PI_non_etabli=sum(r["motif"] == "2" for r in rs),
             PI_rho_propre=sum(r["motif"] == "3" for r in rs))
    lo, hi = wilson(r4, n)
    lt, ht = wilson(tort, n)
    d.update(part_R4=r4 / n if n else float("nan"), R4_bas=lo, R4_haut=hi,
             part_a_tort=tort / n if n else float("nan"), a_tort_haut=ht)
    if c["groupe"] in ("critique", "ajoutée"):
        cible = CIBLE_BAS if (c["monde"] == "grille" and c["multiple"] <= 0.5) else CIBLE_1X
        d.update(cible=cible, tenue=ht <= cible)
    return d


def resumer() -> None:
    with open(META, encoding="utf-8") as f:
        meta = json.load(f)
    par = lire_tirages()
    cases = CAS + meta.get("cases_ajoutees", [])
    st = [stats(c, par.get(c["nom"], [])) for c in cases]
    with open(SORTIE, "w", newline="", encoding="utf-8") as f:
        cols = sorted({k for d in st for k in d}, key=lambda k: list(st[0]).index(k) if k in st[0] else 99)
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(st)
    tailles = list(csv.DictReader(open(TAILLES, encoding="utf-8"))) if os.path.exists(TAILLES) else []
    lignes = imprimer(meta, st, tailles)
    with open(RESUME, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    print("\n".join(lignes))


def monotonie(st: list) -> list:
    """Séries (mécanisme, ρ, témoins) des grilles A et B, multiples croissants : baisse de R4, hausse du délégable, de
    plus de deux erreurs types."""
    alertes = []
    series = {}
    for d in st:
        if d["groupe"] in ("A", "B"):
            series.setdefault((d["mecanisme"], d["rho"], d["temoins"]), []).append(d)
    for cle, ds in series.items():
        ds = sorted(ds, key=lambda d: d["multiple"])
        for a, b in zip(ds, ds[1:]):
            for champ, sens in (("R4", -1), ("delegable", 1)):
                pa, pb = a[champ] / a["n"], b[champ] / b["n"]
                se = math.sqrt(pa * (1 - pa) / a["n"] + pb * (1 - pb) / b["n"]) or 1e-12
                if sens * (pb - pa) > 2 * se:
                    alertes.append(f"{cle} : {champ} {pc(pa, 1)} % à {a['multiple']:g} fois, {pc(pb, 1)} % à "
                                   f"{b['multiple']:g} fois")
    return alertes


def imprimer(meta: dict, st: list, tailles: list) -> list:
    out = ["# Cinquième passage, partie R4 : résultats", "",
           f"Moteur au commit {meta.get('commit', '?')[:7]} ; graine {meta['graine']} ; méthode `METHODE.md` "
           f"(sha256 {meta['methode_sha256'][:12]}…) ; durée {meta.get('duree_s', '?')} s.", ""]
    val = meta.get("validation_recoupement", {})
    out += ["## Validation", "", f"Recoupement avec options_r4 : {sum(v['ecart'] for v in val.values())} écart(s) sur "
            f"{sum(v['n'] for v in val.values())} tirages ; cohérence interne contrôlée à chaque tirage (un écart "
            "aurait arrêté le script).", ""]
    out += ["## Cases critiques (R4 à tort, borne haute de Wilson à 95 %)", "",
            "| Case | n | R4 à tort | borne haute | cible | tenue |", "|---|---|---|---|---|---|"]
    for d in st:
        if d["groupe"] in ("critique", "ajoutée"):
            out.append(f"| {d['nom']} | {d['n']} | {d['R4_a_tort']} ({pc(d['part_a_tort'])} %) | {pc(d['a_tort_haut'])} % "
                       f"| {pc(d['cible'], 0)} % | {'oui' if d['tenue'] else '**non**'} |")
    tenue = all(d["tenue"] for d in st if d["groupe"] in ("critique", "ajoutée"))
    out += ["", f"**Cibles {'tenues' if tenue else 'NON tenues'}** dans toutes les cases critiques.", ""]
    out += ["## Grille A (R4 à tort, 1 000 tirages par case) : les cinq parts les plus hautes par multiple", ""]
    for m in sorted({d["multiple"] for d in st if d["groupe"] == "A"}):
        ds = sorted((d for d in st if d["groupe"] == "A" and d["multiple"] == m), key=lambda d: -d["part_R4"])[:5]
        out.append(f"- {m:g} fois : " + " ; ".join(f"{d['nom'][2:]} {pc(d['part_R4'], 1)} %" for d in ds))
    out += ["", f"Cases ajoutées à la deuxième étape : {len(meta.get('cases_ajoutees', []))}.", ""]
    out += ["## Puissance (grille B, 300 tirages par case) et motifs", "",
            "| Mécanisme, ρ, témoins | 2 × | 3 × | 5 × | 10 × | motif « établi sous ρ̂ propre » à 5 × |",
            "|---|---|---|---|---|---|"]
    series = {}
    for d in st:
        if d["groupe"] == "B":
            series.setdefault((d["mecanisme"], d["rho"], d["temoins"]), {})[d["multiple"]] = d
    for (mec, r, t), ds in sorted(series.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
        cel = [pc(ds[m]["part_R4"], 1) + " %" if m in ds else "—" for m in MULT_B]
        m5 = ds.get(5.0)
        out.append(f"| {mec}, ρ = {r:g}, {_tem(t)} | " + " | ".join(cel) + " | "
                   + (pc(m5["PI_rho_propre"] / m5["n"], 1) + " %" if m5 else "—") + " |")
    out += ["", "## Volumes réduits (300 tirages par case)", "",
            "| Case | délégable | R4 | aucun type jugeable | non établi | établi sous ρ̂ propre |", "|---|---|---|---|---|---|"]
    for d in st:
        if d["groupe"] == "volumes":
            out.append(f"| {d['nom']} | {d['delegable']} | {d['R4']} | {d['PI_aucun_jugeable']} | {d['PI_non_etabli']} | "
                       f"{d['PI_rho_propre']} |")
    out += ["", "## Tâches de tailles inégales (ρ = 1, 200 000 répétitions par ligne)", "",
            "| Profil | barre | p ÷ barre | n_eff à ρ = 1 | dépassement établi | borne haute |", "|---|---|---|---|---|---|"]
    for t in tailles:
        k, n = int(t["etablis"]), int(t["n"])
        out.append(f"| {t['profil']} | {t['barre']} | {float(t['multiple']):g} | {t['n_eff_preuve']} | "
                   f"{pc(k / n)} % | {pc(wilson(k, n)[1])} % |")
    al = monotonie(st)
    out += ["", "## Monotonie", "", ("Aucune alerte." if not al else "\n".join("- " + a for a in al))]
    return out


# --------------------------------------------------------------------------
# Auto-tests et pilote
# --------------------------------------------------------------------------
def tester() -> int:
    cal = {"WorkBench": [f"f:{i}" for i in range(276)], "commerce": [str(i) for i in range(57)]}
    a, b = sous_echantillon(cal, 0.1, 5000, 3), sous_echantillon(cal, 0.1, 5000, 3)
    assert a == b and len(a["WorkBench"]) == 28 and len(a["commerce"]) == 6
    assert len(set(a["WorkBench"])) == 28 and set(a["WorkBench"]) <= set(cal["WorkBench"])
    assert sous_echantillon(cal, 0.1, 5000, 4) != a
    rng = np.random.default_rng(1)
    for t, barre, p in [(np.array([1.0] * 8 + [6.0, 9.0]), 0.02, 0.02), (np.array([3.0] * 10), 0.05, 0.05),
                        (np.array([1.0] * 11 + [12.0]), 0.03, 0.03)]:
        exact = part_etablie_exacte(t, barre, p)
        k = part_etablie(t, barre, p, 400_000, rng)
        se = math.sqrt(exact * (1 - exact) / 400_000)
        assert abs(k / 400_000 - exact) < 4 * se + 1e-9, (t, exact, k / 400_000)
    parts = {c["nom"]: 0.0 for c in CAS if c["groupe"] == "A"}
    un = next(c for c in CAS if c["groupe"] == "A" and c["multiple"] == 1.0 and c["rho"] == 0.3)
    bas = next(c for c in CAS if c["groupe"] == "A" and c["multiple"] == 0.5 and c["rho"] == 0.0)
    deja = next(c for c in CAS if c["groupe"] == "A" and c["multiple"] == 1.0 and c["rho"] == 1.0
                and c["mecanisme"] == "beta" and not c["temoins"])
    parts.update({un["nom"]: 0.031, bas["nom"]: 0.006, deja["nom"]: 0.2})
    aj = cases_ajoutees(parts)
    assert sorted(c["nom"] for c in aj) == sorted(["ajoutée " + bas["nom"][2:], "ajoutée " + un["nom"][2:]])
    assert all(c["reps"] == REPS_CRIT and c["indice"] >= 4000 for c in aj)
    parts.update({un["nom"]: 0.03, bas["nom"]: 0.005})
    assert cases_ajoutees(parts) == []
    assert len({c["indice"] for c in CAS}) == len(CAS) and len({c["nom"] for c in CAS}) == len(CAS)
    assert sum(c["groupe"] == "A" for c in CAS) == 64 and sum(c["groupe"] == "B" for c in CAS) == 62
    assert sum(c["groupe"] == "critique" for c in CAS) == 11 and sum(c["groupe"] == "volumes" for c in CAS) == 6
    print("auto-tests : tout passe")
    return 0


def pilote() -> int:
    """Quelques tirages chronométrés, hors des graines du passage (indice 9 000 + rang)."""
    essais = [dict(c, indice=9000 + i, reps=12) for i, c in enumerate(
        [next(c for c in CAS if c["groupe"] == "A" and c["multiple"] == 1.0 and c["rho"] == 1.0),
         next(c for c in CAS if c["nom"] == "critique M1-bis"), next(c for c in CAS if c["groupe"] == "volumes")])]
    t0 = time.time()
    with get_context("spawn").Pool(PROCESSUS) as pool:
        res = pool.map(tirage, [(c, r) for c in essais for r in range(c["reps"])])
    dt = time.time() - t0
    print(f"{len(res)} tirages en {dt:.1f} s sur {PROCESSUS} processus, soit {len(res) / dt:.1f} tirages par seconde")
    for c in essais:
        rs = [r for r in res if r["cas"] == c["indice"]]
        print(f"  {c['nom']} : " + ", ".join(f"{r['issue']}/{r['motif']}" for r in rs))
    total = sum(c["reps"] for c in CAS) + 1800
    print(f"tirages prévus (hors deuxième étape) : {total}, soit environ {total / (len(res) / dt) / 3600:.1f} h")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = p.add_mutually_exclusive_group(required=True)
    for a in ("--tester", "--pilote", "--lancer", "--resumer"):
        g.add_argument(a, action="store_true")
    a = p.parse_args(argv)
    if a.tester:
        return tester()
    if a.pilote:
        return pilote()
    if a.lancer:
        return lancer()
    resumer()
    return 0


if __name__ == "__main__":
    sys.exit(main())
