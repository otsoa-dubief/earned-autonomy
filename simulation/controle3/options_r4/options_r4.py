"""Cinquième passage, R4 : cinq règles comparées sur l'étude de délégabilité (point 4 seul) du contrôle 3.

Méthode, cibles et graines : METHODE.md, écrit et figé avant le lancement (son empreinte va dans meta.json).
Règles : A (moteur), C-ρ1, C-ρ̂, C-hybride, C-porte (METHODE.md, section 3). Tout vient du moteur : génération
(`controle3.mondes`), classes (`rejeu.classes.classes_tous_environnements`), bornes (`rejeu.classes.bornes_cp`),
taille effective (`rejeu.classes.taille_effective`), étiquette de A (`rejeu.decision`). Aucun fichier existant n'est
modifié ; les surcharges de ρ des mondes mixtes vivent ici (METHODE.md, 4.3). Aucun appel payant.

Usage (depuis simulation/) :
    env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/options_r4/options_r4.py --tester
    env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/options_r4/options_r4.py --pilote
    env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/options_r4/options_r4.py --lancer
    env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/options_r4/options_r4.py --resumer
--tester : auto-tests de la porte ; --pilote : quelques tirages, validation et durée seulement (aucune issue de
règle affichée) ; --lancer : une seule fois, écrit meta.json, tirages.csv, options_r4.csv ; --resumer : tableaux
refaits à partir de tirages.csv, sans calcul du moteur.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import csv  # noqa: E402
import functools  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import platform  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import types  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from multiprocessing import get_context  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, SIM)

import numpy as np  # noqa: E402
import scipy  # noqa: E402
from scipy.stats import binom  # noqa: E402

from controle3 import harnais as H  # noqa: E402
from controle3 import lancer as L  # noqa: E402
from controle3 import mondes as MD  # noqa: E402
from rejeu import classes as CL  # noqa: E402
from rejeu import config_rejeu as CR  # noqa: E402
from rejeu import decision as DE  # noqa: E402
from rejeu import preuves as PR  # noqa: E402
from rejeu import suites as SU  # noqa: E402
from rejeu import types_regle as TY  # noqa: E402

# ---- paramètres figés (METHODE.md)
GRAINE = L.GRAINE                    # 2026110503, graine maîtresse du quatrième passage
PROCESSUS = 12
REPS_GRILLE, REPS_CRITIQUE, REPS_MIXTE = 300, 10_000, 2_000
RHOS = (0.0, 0.3, 0.7, 0.9, 1.0)
MULTIPLES = (0.2, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0)
TEMOINS = (False, True)
INDICE_NOUVEAU = 60_000              # cases nouvelles : 60 000 + j (METHODE.md, 5)
REGLES = ("A", "C-rho1", "C-rhohat", "C-hybride", "C-porte")
PORTE_MULTIPLE, PORTE_PROBA = 5.0, 0.80
PLAFOND_TAUX = 0.5                   # plafond du générateur (mondes.Monde.plafond_p)
CIBLE_BARRE, CIBLE_DEMI = 0.05, 0.01
HAIKU, SONNET, OPUS = MD.MODELES
CONFIGS = [(env, m) for env in MD.ENVS for m in CR.MODELES]   # ordre des chaînes de bits (12 configurations)

METHODE = os.path.join(ICI, "METHODE.md")
META = os.path.join(ICI, "meta.json")
TIRAGES = os.path.join(ICI, "tirages.csv")
SORTIE = os.path.join(ICI, "options_r4.csv")
V4 = os.path.join(SIM, "controle3", "resultats_v4")


# --------------------------------------------------------------------------
# Mondes mixtes : ρ propre à un couple (environnement, modèle, type) (METHODE.md, 4.3)
# --------------------------------------------------------------------------
class TauxMarque(float):
    """Taux moyen d'une configuration et d'un type, qui porte son ρ propre."""

    def __new__(cls, valeur, rho):
        o = super().__new__(cls, valeur)
        o.rho = float(rho)
        return o


@dataclass(frozen=True)
class MondeMixte(MD.Monde):
    """`rhos` : surcharges ((environnement|None, modèle|None, sigle|None, ρ), …), appliquées dans l'ordre après `rho`."""
    rhos: tuple = ()

    def rho_de(self, env: str, modele: str, k: int) -> float:
        r = self.rho
        for e, m, s, v in self.rhos:
            if (e is None or e == env) and (m is None or m == modele) and (s is None or s == TY.SIGLES[k]):
                r = v
        return float(r)

    def taux(self, env, modele, k, config):
        return TauxMarque(MD.Monde.taux(self, env, modele, k, config), self.rho_de(env, modele, k))


_TAUX_PAR_TACHE_MOTEUR = MD.taux_par_tache


def _taux_par_tache_mixte(p, rho, u, mecanisme="beta"):
    if isinstance(p, TauxMarque):
        return _TAUX_PAR_TACHE_MOTEUR(float(p), p.rho, u, mecanisme)
    return _TAUX_PAR_TACHE_MOTEUR(p, rho, u, mecanisme)


def generer(monde, rng, cfg) -> dict:
    """`mondes.generer` tel quel ; pour un monde mixte seulement, `taux_par_tache` lit le ρ porté par le taux."""
    if not isinstance(monde, MondeMixte):
        return MD.generer(monde, rng, cfg)
    MD.taux_par_tache = _taux_par_tache_mixte
    try:
        return MD.generer(monde, rng, cfg)
    finally:
        MD.taux_par_tache = _TAUX_PAR_TACHE_MOTEUR


def monde_du_cas(c: dict):
    if c["monde"] == "grille":
        return H.monde_delegabilite(c["multiple"], c["rho"], c["temoins"], "beta")
    if c["monde"] == "M1":
        return MondeMixte("M1", "Haiku WorkBench, écriture réversible à la barre et ρ = 1 ; le reste à 0,2 × et ρ = 0",
                          "", 0.2, (("WorkBench", HAIKU, "ECR", 1.0),), rho=0.0,
                          rhos=(("WorkBench", HAIKU, "ECR", 1.0),))
    if c["monde"] == "M1-bis":
        return MondeMixte("M1-bis", "Haiku WorkBench à la barre (écriture réversible à ρ = 1) ; le reste à 10 × et ρ = 0",
                          "", 10.0, (("WorkBench", HAIKU, None, 1.0),), rho=0.0,
                          rhos=(("WorkBench", HAIKU, "ECR", 1.0),))
    if c["monde"] == "M2":
        return MD.Monde("M2", "commerce à 0,2 × la barre, le reste à 5 ×, ρ = 0,3", "", 5.0,
                        (("commerce", None, None, 0.2),), rho=0.3)
    raise ValueError(c["monde"])


def rho_vrai_wb_haiku_ecr(c: dict) -> float:
    return {"M1": 1.0, "M1-bis": 1.0, "M2": 0.3}.get(c["monde"], c["rho"])


# --------------------------------------------------------------------------
# Cases (METHODE.md, 4 et 5)
# --------------------------------------------------------------------------
def _tem(t: bool) -> str:
    return "defaut" if t else "tenus"


def construire_cas() -> list:
    v4 = L.cases_deleg()
    cas = []
    for t in TEMOINS:
        for r in RHOS:
            for m in MULTIPLES:
                cle = (m, r, t, "beta")
                if cle in v4:
                    indice, ref = v4.index(cle), "v4"
                else:
                    indice, ref = INDICE_NOUVEAU + 5 * int(t) + RHOS.index(r), "moteur"
                cas.append(dict(nom=f"grille {m:g}x rho={r:g} {_tem(t)}", groupe="grille", monde="grille", multiple=m,
                                rho=r, temoins=t, reps=REPS_GRILLE, indice=indice, ref=ref))
    for r in (0.9, 1.0):
        for t in TEMOINS:
            cas.append(dict(nom=f"critique 1x rho={r:g} {_tem(t)}", groupe="critique", monde="grille", multiple=1.0,
                            rho=r, temoins=t, reps=REPS_CRITIQUE, indice=50_000 + L.CRITIQUES.index((1.0, r, t, "beta")),
                            ref="v4-critiques"))
    for t in TEMOINS:
        cas.append(dict(nom=f"critique 0.5x rho=1 {_tem(t)}", groupe="critique", monde="grille", multiple=0.5, rho=1.0,
                        temoins=t, reps=REPS_CRITIQUE, indice=INDICE_NOUVEAU + 10 + int(t), ref=""))
    cas.append(dict(nom="M1", groupe="critique", monde="M1", multiple="", rho="", temoins=False, reps=REPS_CRITIQUE,
                    indice=INDICE_NOUVEAU + 12, ref=""))
    cas.append(dict(nom="M1-bis", groupe="critique", monde="M1-bis", multiple="", rho="", temoins=False,
                    reps=REPS_CRITIQUE, indice=INDICE_NOUVEAU + 13, ref=""))
    cas.append(dict(nom="M2", groupe="mixte", monde="M2", multiple="", rho="", temoins=False, reps=REPS_MIXTE,
                    indice=INDICE_NOUVEAU + 14, ref=""))
    cas.append(dict(nom="M3", groupe="mixte", monde="grille", multiple=5.0, rho=0.0, temoins=False, reps=REPS_MIXTE,
                    indice=INDICE_NOUVEAU + 15, ref=""))
    return cas


CAS = construire_cas()
NOMS = [c["nom"] for c in CAS]


# --------------------------------------------------------------------------
# Porte de détectabilité (METHODE.md, 3)
# --------------------------------------------------------------------------
@functools.lru_cache(maxsize=20_000)
def puissance_porte(tailles: tuple, barre: float, multiple: float = PORTE_MULTIPLE) -> float:
    """Probabilité que la borne basse à 95 % à ρ = 1 d'un type dépasse sa barre si chaque tâche porteuse est ratée en
    entier, indépendamment, avec la probabilité p = min(0,5 ; multiple × barre). tailles : écritures par tâche porteuse.
    Exact : X = Σ m_i B_i ; seuil = plus petit X établi (la borne croît avec X) ; P(X ≥ seuil) par dénombrement."""
    ms = [int(v) for v in tailles if v > 0]
    n = sum(ms)
    if n <= 0:
        return 0.0
    _n, _mb, ne1 = CL.taille_effective(ms, CL.RHO_PREUVE)

    def lo(X):
        return CL.bornes_cp(X * ne1 / n, ne1)[0]
    if not lo(n) > barre:
        return 0.0
    a, z = 0, n
    while z - a > 1:
        mil = (a + z) // 2
        if lo(mil) > barre:
            z = mil
        else:
            a = mil
    seuil = z
    p = min(PLAFOND_TAUX, multiple * barre)
    dist = np.zeros(seuil)
    dist[0] = 1.0
    tl, cnt = np.unique(np.asarray(ms), return_counts=True)
    for s, c in zip(tl.tolist(), cnt.tolist()):
        jmax = min(c, (seuil - 1) // s)
        pmf = binom.pmf(np.arange(jmax + 1), c, p)
        nouv = np.zeros(seuil)
        for j in range(jmax + 1):
            nouv[s * j:] += pmf[j] * dist[:seuil - s * j]
        dist = nouv
    return float(min(1.0, max(0.0, 1.0 - dist.sum())))


# --------------------------------------------------------------------------
# Un tirage
# --------------------------------------------------------------------------
def sorties_harnais(cls: dict) -> tuple:
    """(types estimés sous la barre, configurations délégables, détail des types faibles) : mêmes expressions que
    `harnais.delegabilite`, pour la validation contre le moteur."""
    dele, estimes, faibles = [], [], {}
    for env in MD.ENVS:
        for m, c in cls[env].items():
            cm = f"{env}/{m.split('-')[1]}"
            if any(CL.estime_sous(v) for v in c.values()):
                dele.append(cm)
            for k, v in c.items():
                if v["n"] <= 0:
                    continue
                if CL.estime_sous(v):
                    estimes.append(f"{cm}/{TY.SIGLES[k]}")
                if TY.ENJEU[k] == TY.FAIBLE:
                    faibles[f"{cm}/{TY.SIGLES[k]}"] = [H.CODES_CLASSE.get(v["classe"], "?"), int(v["x"]), int(v["n"]),
                                                      round(float(v["hi"] / v["barre"]), 4), round(float(v["rho"]), 4),
                                                      CL.SOURCES_G1.index(v["source_rho"])
                                                      if v["source_rho"] in CL.SOURCES_G1 else -1,
                                                      H.CODES_CLASSE.get(v.get("classe_sous_hypothese"), "?")]
    return estimes, dele, faibles


def _bits(d: dict) -> str:
    return "".join("1" if d[c] else "0" for c in CONFIGS)


def evaluer(jks: dict, cls: dict, monde) -> dict:
    deleg, jug, det, e1, eh, ehy, fiable, hyb_propre = {}, {}, {}, {}, {}, {}, {}, {}
    controles = 0
    wb = [0, 0, None, None, None, None, None, None, 0]
    ws = [0, 0]
    co = [0, 0]
    for env in MD.ENVS:
        types_env = list(monde.melange_de(env))
        for m in CR.MODELES:
            cle = (env, m)
            c, j = cls[env][m], jks[env][m]
            deleg[cle] = bool(c) and any(CL.estime_sous(v) for v in c.values())
            jug[cle] = bool(c) and any(CL.jugeable(v) for v in c.values())
            fiable[cle] = max(monde.multiple_de(env, m, k) for k in types_env) <= 1.0
            x_c, t_c = CL.erreurs_et_taches(j)
            r_prop = (CL.rho_fc_strates(CL.strates_par_type([j]))
                      if (x_c >= CL.SEUIL_ERREURS_CONF and t_c >= CL.SEUIL_TACHES_CONF) else None)
            rho_h = max(CL.PLANCHER_RHO, r_prop) if r_prop is not None else 1.0
            hyb_propre[cle] = r_prop is not None
            et1 = eth = ethy = False
            pas_etabli = 1.0
            for k, v in c.items():
                if v["n"] <= 0:
                    continue
                par_t = CL.comptes_par_tache(j, (k,))
                ms = [mm for mm, _x in par_t.values()]
                x = sum(xx for _m, xx in par_t.values())
                n = sum(ms)
                if n != v["n"] or x != v["x"]:
                    controles += 1
                b = float(v["barre"])
                et1 = et1 or v["lo"] > b
                eth = eth or v["lo_hyp"] > b
                _n, _mb, ne_h = CL.taille_effective(ms, rho_h)
                lo_h = CL.bornes_cp(x * ne_h / n, ne_h)[0]
                ethy = ethy or lo_h > b
                if rho_h == 1.0 and lo_h != v["lo"]:
                    controles += 1
                if rho_h == float(v["rho"]) and lo_h != v["lo_hyp"]:
                    controles += 1
                pas_etabli *= 1.0 - puissance_porte(tuple(sorted(ms)), b)
                if (env, m, k) == ("WorkBench", HAIKU, TY.ECR):
                    partielles = sum(1 for mm, xx in par_t.values() if 0 < xx < mm)
                    wb = [x, n, round(float(v["rho"]), 4), CL.SOURCES_G1.index(v["source_rho"])
                          if v["source_rho"] in CL.SOURCES_G1 else -1, round(rho_h, 4),
                          round(v["lo"] / b, 4), round(v["lo_hyp"] / b, 4), round(lo_h / b, 4), partielles]
                elif (env, m, k) == ("WorkBench", SONNET, TY.ECR):
                    ws = [x, n]
                elif (env, m, k) == ("commerce", HAIKU, TY.ECR):
                    co = [x, n]
            det[cle] = 1.0 - pas_etabli >= PORTE_PROBA
            e1[cle], eh[cle], ehy[cle] = et1, eth, ethy
    # étiquette de A : décision du moteur (points 0 à 2 tenus)
    p4 = DE.point4(types.SimpleNamespace(delegables=deleg, jugeables=jug))
    lab = DE.etiquette({"tenu": True}, {"tenu": True}, {"tenu": True}, p4)
    une_deleg = any(deleg.values())
    r4a = lab == "R4"
    if r4a != ((not une_deleg) and any(jug.values())):
        controles += 1
    jugs = [c for c in CONFIGS if jug[c]]
    dj = [c for c in CONFIGS if det[c] and jug[c]]
    r4 = {"A": r4a,
          "C-rho1": r4a and all(e1[c] for c in jugs),
          "C-rhohat": r4a and all(eh[c] for c in jugs),
          "C-hybride": r4a and all(ehy[c] for c in jugs),
          "C-porte": r4a and bool(dj) and all(e1[c] for c in dj)}
    out = {r: ("D" if une_deleg else ("R4" if r4[r] else "PI")) for r in REGLES}
    rc = CL.rho_commun(jks)
    out.update(fiable_jug=int(any(jug[c] and fiable[c] for c in CONFIGS)), det_sans_jug=int(any(det.values()) and not dj),
               conf_deleg=_bits(deleg), conf_jug=_bits(jug), conf_det=_bits(det), etab_rho1=_bits(e1),
               etab_rhohat=_bits(eh), etab_hyb=_bits(ehy), hyb_propre=_bits(hyb_propre),
               rho_commun="" if rc is None else round(rc, 4),
               wb_x=wb[0], wb_n=wb[1], wb_rho=wb[2], wb_src=wb[3], wb_rho_hyb=wb[4], wb_lo1_b=wb[5],
               wb_lohyp_b=wb[6], wb_lohyb_b=wb[7], wb_partielles=wb[8], ws_x=ws[0], ws_n=ws[1], co_x=co[0], co_n=co[1],
               controles=controles)
    return out


def tirage(args) -> dict:
    i_cas, rep = args
    c = CAS[i_cas]
    cfg = H.config()
    monde = monde_du_cas(c)
    rng = np.random.default_rng(np.random.SeedSequence([int(GRAINE), 1000 + int(c["indice"]), int(rep)]))
    g = generer(monde, rng, cfg)
    e = g["entrees"]
    prep = PR.preparer(e, "confirmes")
    jks = {env: {m: SU.jeu_configuration(prep, e, env, m, g["cal"][env], "calibration") for m in CR.MODELES}
           for env in MD.ENVS}
    cls = CL.classes_tous_environnements(jks, cfg)
    out = dict(cas=i_cas, rep=int(rep))
    out.update(evaluer(jks, cls, monde))
    if c["ref"] in ("v4", "v4-critiques"):
        out["_estimes"], out["_dele"], out["_faibles"] = sorties_harnais(cls)
    elif c["ref"] == "moteur":
        ref = H.delegabilite(c["multiple"], c["rho"], c["temoins"], rep, GRAINE, c["indice"], "beta")
        est, dele, fai = sorties_harnais(cls)
        out["_ecart_moteur"] = [int(est != ref["estimes_sous"]), int(dele != ref["delegables"]),
                                int(fai != ref["faibles"])]
    return out


# --------------------------------------------------------------------------
# Validation contre le moteur (METHODE.md, 6)
# --------------------------------------------------------------------------
def sha256(chemin: str) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def verifier_sha_v4() -> None:
    for nom in ("delegabilite.jsonl", "critiques.jsonl"):
        with open(os.path.join(V4, nom + ".sha256"), encoding="utf-8") as f:
            attendu = f.read().split()[0]
        if sha256(os.path.join(V4, nom)) != attendu:
            raise SystemExit(f"resultats_v4/{nom} : empreinte différente de {nom}.sha256")


def charger_v4() -> tuple:
    grille, crit = {}, {}
    mults = set(MULTIPLES)
    with open(os.path.join(V4, "delegabilite.jsonl"), encoding="utf-8") as f:
        for ligne in f:
            r = json.loads(ligne)
            if r.get("mecanisme", "beta") == "beta" and r["multiple"] in mults:
                grille[(r["multiple"], r["rho"], r["temoins"], r["rep"])] = (r["estimes_sous"], r["delegables"],
                                                                            r["faibles"])
    with open(os.path.join(V4, "critiques.jsonl"), encoding="utf-8") as f:
        for ligne in f:
            r = json.loads(ligne)
            if r["mecanisme"] == "beta" and r["multiple"] == 1.0 and r["rho"] in (0.9, 1.0):
                crit[(r["rho"], r["temoins"], r["rep"])] = r["faibles"]
    return grille, crit


def nouvelle_validation() -> dict:
    return dict(v4_grille_tirages=0, v4_grille_ecarts_estimes=0, v4_grille_ecarts_delegables=0,
                v4_grille_ecarts_faibles=0, v4_grille_absents=0, moteur_tirages=0, moteur_ecarts_estimes=0,
                moteur_ecarts_delegables=0, moteur_ecarts_faibles=0, v4_critiques_tirages=0,
                v4_critiques_ecarts_faibles=0, v4_critiques_absents=0, controles_internes=0,
                rho1_tirages=0, rho1_taches_partielles=0)


def valider(r: dict, val: dict, v4g: dict, v4c: dict) -> None:
    """Compare un tirage au moteur et retire les champs de validation (préfixe « _ »)."""
    c = CAS[r["cas"]]
    if c["ref"] == "v4":
        val["v4_grille_tirages"] += 1
        ref = v4g.get((c["multiple"], c["rho"], c["temoins"], r["rep"]))
        if ref is None:
            val["v4_grille_absents"] += 1
        else:
            val["v4_grille_ecarts_estimes"] += int(r["_estimes"] != ref[0])
            val["v4_grille_ecarts_delegables"] += int(r["_dele"] != ref[1])
            val["v4_grille_ecarts_faibles"] += int(r["_faibles"] != ref[2])
    elif c["ref"] == "moteur":
        val["moteur_tirages"] += 1
        a, b, f = r["_ecart_moteur"]
        val["moteur_ecarts_estimes"] += a
        val["moteur_ecarts_delegables"] += b
        val["moteur_ecarts_faibles"] += f
    elif c["ref"] == "v4-critiques":
        val["v4_critiques_tirages"] += 1
        ref = v4c.get((c["rho"], c["temoins"], r["rep"]))
        if ref is None:
            val["v4_critiques_absents"] += 1
        else:
            val["v4_critiques_ecarts_faibles"] += int(r["_faibles"] != ref)
    val["controles_internes"] += int(r["controles"])
    if rho_vrai_wb_haiku_ecr(c) == 1.0:
        val["rho1_tirages"] += 1
        val["rho1_taches_partielles"] += int(r["wb_partielles"])
    for k in [k for k in r if k.startswith("_")]:
        del r[k]


def nb_ecarts(val: dict) -> int:
    return sum(v for k, v in val.items() if "ecarts" in k or "absents" in k) + val["controles_internes"] + \
        val["rho1_taches_partielles"]


COLONNES = ["cas", "nom", "rep", *REGLES, "fiable_jug", "det_sans_jug", "conf_deleg", "conf_jug", "conf_det",
            "etab_rho1", "etab_rhohat", "etab_hyb", "hyb_propre", "rho_commun", "wb_x", "wb_n", "wb_rho", "wb_src",
            "wb_rho_hyb", "wb_lo1_b", "wb_lohyp_b", "wb_lohyb_b", "wb_partielles", "ws_x", "ws_n", "co_x", "co_n",
            "controles"]


def taches_de(groupes: tuple) -> list:
    """(cas, répétition) entrelacés par répétition : un arrêt laisse une couverture équilibrée des cases."""
    idx = [i for i, c in enumerate(CAS) if c["groupe"] in groupes]
    n = max(CAS[i]["reps"] for i in idx)
    return [(i, rep) for rep in range(n) for i in idx if rep < CAS[i]["reps"]]


def _ecrire_meta(meta: dict) -> None:
    with open(META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1, default=str)
        f.write("\n")


def phase(pool, taches, val, v4g, v4c, ecrivain, t0, etiquette) -> int:
    fait = 0
    for r in pool.imap_unordered(tirage, taches, chunksize=20):
        valider(r, val, v4g, v4c)
        r["nom"] = NOMS[r["cas"]]
        ecrivain.writerow(r)
        fait += 1
        if fait % 2000 == 0 or fait == len(taches):
            print(f"[{time.time() - t0:7.0f} s] {etiquette} : {fait}/{len(taches)} tirages ; écarts {nb_ecarts(val)}",
                  flush=True)
    return fait


def lancer() -> int:
    if not os.path.exists(METHODE):
        raise SystemExit("METHODE.md manquant : la méthode s'écrit avant le lancement")
    if os.path.exists(META):
        raise SystemExit("meta.json existe déjà : ce passage se lance une seule fois")
    ecarts = L.verifier()
    if ecarts:
        raise SystemExit("empreintes du moteur changées : " + ", ".join(ecarts))
    verifier_sha_v4()
    debut = time.time()
    meta = dict(statut="en cours", debut=time.strftime("%Y-%m-%d %H:%M:%S"), graine=GRAINE, processus=PROCESSUS,
                regles=REGLES, porte=dict(multiple=PORTE_MULTIPLE, proba=PORTE_PROBA, plafond=PLAFOND_TAUX),
                cibles=dict(barre=CIBLE_BARRE, demi=CIBLE_DEMI), cas=CAS,
                methode_sha256=sha256(METHODE),
                methode_modifie=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(METHODE))),
                script_sha256=sha256(os.path.abspath(__file__)), empreintes_moteur=L.empreintes(),
                python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__,
                machine=platform.platform())
    _ecrire_meta(meta)
    print(f"METHODE.md sha256 {meta['methode_sha256']} (modifié le {meta['methode_modifie']})", flush=True)
    v4g, v4c = charger_v4()
    val = nouvelle_validation()
    with open(TIRAGES, "w", newline="", encoding="utf-8") as f, \
            get_context("spawn").Pool(PROCESSUS) as pool:
        w = csv.DictWriter(f, fieldnames=COLONNES)
        w.writeheader()
        t0 = time.time()
        phase(pool, taches_de(("grille",)), val, v4g, v4c, w, t0, "grille")
        f.flush()
        meta["duree_grille_s"] = round(time.time() - t0, 1)
        meta["validation_grille"] = dict(val)
        if nb_ecarts(val):
            meta.update(statut="arrêté : écarts de validation sur la grille", validation=val)
            _ecrire_meta(meta)
            print("ÉCARTS DE VALIDATION sur la grille : arrêt avant tout résultat", json.dumps(val), flush=True)
            return 1
        print("validation de la grille : 0 écart", json.dumps(val), flush=True)
        t1 = time.time()
        phase(pool, taches_de(("critique", "mixte")), val, v4g, v4c, w, t1, "critiques et mixtes")
        meta["duree_critiques_mixtes_s"] = round(time.time() - t1, 1)
    meta.update(validation=val, duree_s=round(time.time() - debut, 1), fin=time.strftime("%Y-%m-%d %H:%M:%S"))
    if nb_ecarts(val):
        meta["statut"] = "arrêté : écarts de validation"
        _ecrire_meta(meta)
        print("ÉCARTS DE VALIDATION : aucun tableau", json.dumps(val), flush=True)
        return 1
    meta["statut"] = "terminé"
    _ecrire_meta(meta)
    print("validation complète : 0 écart", json.dumps(val), flush=True)
    resumer()
    return 0


# --------------------------------------------------------------------------
# Tableaux (aucun calcul du moteur)
# --------------------------------------------------------------------------
def wilson(k: int, n: int) -> tuple:
    if not n:
        return (float("nan"), float("nan"))
    z, p = 1.959964, k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, c - h), min(1.0, c + h))


def pc(x: float, d: int = 1) -> str:
    return f"{100 * x:.{d}f}".replace(".", ",")


def lire_tirages() -> dict:
    par_cas = {}
    with open(TIRAGES, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            par_cas.setdefault(int(r["cas"]), []).append(r)
    return par_cas


def stats_cas(rs: list) -> dict:
    n = len(rs)
    s = dict(n=n, D=sum(r["A"] == "D" for r in rs))
    for g in REGLES:
        s[g] = dict(R4=sum(r[g] == "R4" for r in rs), PI=sum(r[g] == "PI" for r in rs),
                    tort=sum(r[g] == "R4" and r["fiable_jug"] == "1" for r in rs))
    return s


def resumer() -> None:
    par_cas = lire_tirages()
    st = {i: stats_cas(rs) for i, rs in par_cas.items()}
    lignes = []
    for i, s in sorted(st.items()):
        c = CAS[i]
        for g in REGLES:
            d = dict(cas=i, nom=c["nom"], groupe=c["groupe"], multiple=c["multiple"], rho=c["rho"],
                     temoins=_tem(c["temoins"]) if c["monde"] == "grille" else "", graine_indice=c["indice"], n=s["n"],
                     regle=g)
            for cle, k in (("delegable", s["D"]), ("R4", s[g]["R4"]), ("preuves_insuffisantes", s[g]["PI"]),
                           ("R4_a_tort", s[g]["tort"])):
                lo, hi = wilson(k, s["n"])
                d.update({cle: round(k / s["n"], 5), f"{cle}_bas": round(lo, 5), f"{cle}_haut": round(hi, 5)})
            lignes.append(d)
    with open(SORTIE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)
    imprimer(st, par_cas)


def _part(s, g, cle="R4") -> float:
    return s[g][cle] / s["n"]


def imprimer(st: dict, par_cas: dict) -> None:
    gr = {(c["multiple"], c["rho"], c["temoins"]): i for i, c in enumerate(CAS) if c["groupe"] == "grille"}
    nom = {c["nom"]: i for i, c in enumerate(CAS)}
    print("\n## R4 par règle : grille (300 tirages), plus petite et plus grande part sur ρ × témoins")
    print("| règle | " + " | ".join(f"{m:g} ×" for m in MULTIPLES) + " |")
    print("|---|" + "---|" * len(MULTIPLES))
    for g in REGLES:
        cel = []
        for m in MULTIPLES:
            v = [(_part(st[gr[(m, r, t)]], g), r, t) for r in RHOS for t in TEMOINS if gr.get((m, r, t)) in st]
            if not v:
                cel.append("—")
                continue
            lo, hi = min(v), max(v)
            cel.append(f"{pc(lo[0])}–{pc(hi[0])} (max ρ={hi[1]:g} {_tem(hi[2])})")
        print(f"| {g} | " + " | ".join(cel) + " |")
    print("\n## Délégable (identique pour toutes les règles), grille")
    print("| ρ \\ multiple | " + " | ".join(f"{m:g} ×" for m in MULTIPLES) + " |")
    print("|---|" + "---|" * len(MULTIPLES))
    for t in TEMOINS:
        for r in RHOS:
            cel = [pc(st[gr[(m, r, t)]]["D"] / st[gr[(m, r, t)]]["n"], 0) if gr.get((m, r, t)) in st else "—"
                   for m in MULTIPLES]
            print(f"| {r:g} {_tem(t)} | " + " | ".join(cel) + " |")
    print("\n## Cases critiques et mondes mixtes : R4 [Wilson 95 %] ; délégable ; preuves insuffisantes")
    print("| case | n | délégable | " + " | ".join(REGLES) + " |")
    print("|---|---|---|" + "---|" * len(REGLES))
    for i, c in enumerate(CAS):
        if c["groupe"] == "grille" or i not in st:
            continue
        s = st[i]
        cel = []
        for g in REGLES:
            lo, hi = wilson(s[g]["R4"], s["n"])
            cel.append(f"{pc(_part(s, g), 2)} [{pc(lo, 2)}–{pc(hi, 2)}] ; PI {pc(_part(s, g, 'PI'), 1)}")
        print(f"| {c['nom']} | {s['n']} | {pc(s['D'] / s['n'], 1)} | " + " | ".join(cel) + " |")
    print("\n## R4 à tort (R4 avec une configuration jugeable fiable) dans M2")
    if "M2" in nom and nom["M2"] in st:
        s = st[nom["M2"]]
        print(" ; ".join(f"{g} {pc(s[g]['tort'] / s['n'], 2)} % [{pc(wilson(s[g]['tort'], s['n'])[0], 2)}–"
                         f"{pc(wilson(s[g]['tort'], s['n'])[1], 2)}]" for g in REGLES))
    print("\n## Cibles (METHODE.md, 7)")
    crit_barre = [nom[k] for k in ("critique 1x rho=0.9 tenus", "critique 1x rho=0.9 defaut", "critique 1x rho=1 tenus",
                                   "critique 1x rho=1 defaut", "M1") if nom.get(k) in st]
    crit_demi = [nom[k] for k in ("critique 0.5x rho=1 tenus", "critique 0.5x rho=1 defaut") if nom.get(k) in st]
    g_barre = [gr[(1.0, r, t)] for r in RHOS for t in TEMOINS if gr.get((1.0, r, t)) in st]
    g_demi = [gr[(0.5, r, t)] for r in RHOS for t in TEMOINS if gr.get((0.5, r, t)) in st]
    for g in REGLES:
        hb = max((wilson(st[i][g]["R4"], st[i]["n"])[1], CAS[i]["nom"]) for i in crit_barre)
        hd = max((wilson(st[i][g]["R4"], st[i]["n"])[1], CAS[i]["nom"]) for i in crit_demi)
        pb = max((_part(st[i], g), CAS[i]["nom"]) for i in g_barre)
        pd = max((_part(st[i], g), CAS[i]["nom"]) for i in g_demi)
        ok_b = hb[0] <= CIBLE_BARRE and pb[0] <= CIBLE_BARRE
        ok_d = hd[0] <= CIBLE_DEMI and pd[0] <= CIBLE_DEMI
        mb = ""
        if "M1-bis" in nom and nom["M1-bis"] in st:
            hm = wilson(st[nom["M1-bis"]][g]["R4"], st[nom["M1-bis"]]["n"])[1]
            mb = f" ; M1-bis : borne haute {pc(hm, 2)} % ({'tient' if hm <= CIBLE_BARRE else 'échoue'})"
        print(f"- {g} : barre {'TIENT' if ok_b else 'ÉCHOUE'} (critiques : borne haute max {pc(hb[0], 2)} % "
              f"[{hb[1]}] ; grille : max {pc(pb[0], 1)} % [{pb[1]}]) ; 0,5 × {'TIENT' if ok_d else 'ÉCHOUE'} "
              f"(critiques : borne haute max {pc(hd[0], 2)} % [{hd[1]}] ; grille : max {pc(pd[0], 1)} % [{pd[1]}])"
              + mb)
    print("\n## Puissance : R4 à 3 et 5 × la barre (grille, min–max sur ρ × témoins) et M3")
    for g in REGLES:
        txt = []
        for m in (3.0, 5.0):
            v = [_part(st[gr[(m, r, t)]], g) for r in RHOS for t in TEMOINS if gr.get((m, r, t)) in st]
            txt.append(f"{m:g} × : {pc(min(v), 0)}–{pc(max(v), 0)} %")
        if "M3" in nom and nom["M3"] in st:
            s = st[nom["M3"]]
            lo, hi = wilson(s[g]["R4"], s["n"])
            txt.append(f"M3 : {pc(_part(s, g), 1)} % [{pc(lo, 1)}–{pc(hi, 1)}]")
        print(f"- {g} : " + " ; ".join(txt))
    print("\n## R4 par case de la grille (ρ, témoins × multiple), règle par règle")
    for g in REGLES:
        print(f"\n### {g}")
        print("| ρ \\ multiple | " + " | ".join(f"{m:g} ×" for m in MULTIPLES) + " |")
        print("|---|" + "---|" * len(MULTIPLES))
        for t in TEMOINS:
            for r in RHOS:
                cel = [pc(_part(st[gr[(m, r, t)]], g), 1) if gr.get((m, r, t)) in st else "—" for m in MULTIPLES]
                print(f"| {r:g} {_tem(t)} | " + " | ".join(cel) + " |")
    print("\n## Monotonie (R4 ne baisse pas quand les agents empirent ; z > 2 sur deux multiples voisins)")
    for g in REGLES:
        viol = []
        for t in TEMOINS:
            for r in RHOS:
                v = [(st[gr[(m, r, t)]][g]["R4"], st[gr[(m, r, t)]]["n"], m) for m in MULTIPLES if gr.get((m, r, t)) in st]
                for (k1, n1, m1), (k2, n2, m2) in zip(v, v[1:]):
                    p1, p2 = k1 / n1, k2 / n2
                    pp = (k1 + k2) / (n1 + n2)
                    se = math.sqrt(max(pp * (1 - pp) * (1 / n1 + 1 / n2), 1e-12))
                    if (p1 - p2) / se > 2:
                        viol.append(f"ρ={r:g} {_tem(t)} {m1:g}→{m2:g} : {pc(p1)}→{pc(p2)}")
        print(f"- {g} : " + ("aucune baisse significative" if not viol else " ; ".join(viol)))
    print("\n## Diagnostics par case non-grille : ρ̂ commun, Haiku WorkBench (écriture réversible), porte, taux")
    print("| case | ρ̂ commun médian | ρ̂ Haiku WB médian | source propre | ρ hybride Haiku WB médian | "
          "configurations détectables (moyenne) | WB Haiku x/n ÷ barre | WB Sonnet ÷ barre | commerce Haiku ÷ barre |")
    print("|---|---|---|---|---|---|---|---|---|")
    cfg = H.config()
    b_wb = float(cfg.barres[("WorkBench", "faible")])
    b_co = float(cfg.barres[("commerce", "faible")])
    for i, c in enumerate(CAS):
        if (c["groupe"] == "grille" and not (c["multiple"] == 1.0 and c["rho"] in (0.9, 1.0))) or i not in par_cas:
            continue
        rs = par_cas[i]
        rc = [float(r["rho_commun"]) for r in rs if r["rho_commun"] != ""]
        wr = [float(r["wb_rho"]) for r in rs if r["wb_rho"] not in ("", "None")]
        wh = [float(r["wb_rho_hyb"]) for r in rs if r["wb_rho_hyb"] not in ("", "None")]
        src = sum(r["wb_src"] == "0" for r in rs) / len(rs)
        ndet = statistics.mean(r["conf_det"].count("1") for r in rs)
        tx = lambda a, b, barre: (sum(int(r[a]) for r in rs) / max(1, sum(int(r[b]) for r in rs))) / barre  # noqa
        print(f"| {c['nom']} | {statistics.median(rc) if rc else float('nan'):.3f} | "
              f"{statistics.median(wr) if wr else float('nan'):.3f} | {pc(src, 1)} % | "
              f"{statistics.median(wh) if wh else float('nan'):.3f} | {ndet:.2f} | {tx('wb_x', 'wb_n', b_wb):.3f} | "
              f"{tx('ws_x', 'ws_n', b_wb):.3f} | {tx('co_x', 'co_n', b_co):.3f} |")
    print("\n## Porte : part des tirages où chaque configuration est détectable (grille, tous ρ et témoins réunis ;"
          " M2)")
    tous = [r for i, rs in par_cas.items() if CAS[i]["groupe"] == "grille" for r in rs]
    m2 = par_cas.get(nom.get("M2"), [])
    for lot, rs in (("grille", tous), ("M2", m2)):
        if rs:
            parts = [sum(r["conf_det"][j] == "1" for r in rs) / len(rs) for j in range(len(CONFIGS))]
            print(f"- {lot} : " + " ; ".join(f"{e}/{m.split('-')[1]} {pc(p, 1)} %" for (e, m), p in zip(CONFIGS, parts)
                                             if p > 0) + f" ; détectable sans jugeable : "
                  f"{sum(r['det_sans_jug'] == '1' for r in rs)} tirages")
            jp = [sum(r["conf_jug"][j] == "1" for r in rs) / len(rs) for j in range(len(CONFIGS))]
            print(f"  jugeables : " + " ; ".join(f"{e}/{m.split('-')[1]} {pc(p, 1)} %"
                                                 for (e, m), p in zip(CONFIGS, jp) if p > 0))


# --------------------------------------------------------------------------
# Auto-tests et pilote
# --------------------------------------------------------------------------
def tester() -> int:
    """Puissance de la porte : (1) contre une simulation directe sur des profils tirés au hasard ; (2) égale à la loi
    binomiale quand toutes les tâches ont la même taille."""
    rng = np.random.default_rng(20261106)
    cfg = H.config()
    barres = sorted({float(b) for b in cfg.barres.values() if float(b) > 1e-3})
    pires_z, nb = 0.0, 0
    for _ in range(40):
        T = int(rng.integers(3, 230))
        tailles = tuple(sorted(int(v) for v in rng.integers(1, 12, size=T)))
        b = float(rng.choice(barres))
        P = puissance_porte(tailles, b)
        p = min(PLAFOND_TAUX, PORTE_MULTIPLE * b)
        N = 100_000
        X = (rng.random((N, T)) < p).astype(np.int32) @ np.asarray(tailles, dtype=np.int32)
        n = sum(tailles)
        ne1 = CL.taille_effective(list(tailles), 1.0)[2]
        ok = {int(x): CL.bornes_cp(x * ne1 / n, ne1)[0] > b for x in np.unique(X)}
        pmc = float(np.mean([ok[int(x)] for x in X]))
        se = math.sqrt(max(P * (1 - P), 1e-6) / N)
        pires_z = max(pires_z, abs(pmc - P) / se)
        nb += 1
    ecart_bin = 0.0
    for T, m, b in ((196, 1, 1 / 132), (185, 5, 1 / 132), (19, 10, 10 / 861), (9, 50, 5 / 189), (160, 10, 1 / 132),
                    (59, 5, 1 / 132)):
        P = puissance_porte(tuple([m] * T), b)
        k = next(k for k in range(1, T + 1) if CL.bornes_cp(k, T)[0] > b) if CL.bornes_cp(T, T)[0] > b else None
        Pb = 0.0 if k is None else float(binom.sf(k - 1, T, min(PLAFOND_TAUX, PORTE_MULTIPLE * b)))
        ecart_bin = max(ecart_bin, abs(P - Pb))
        print(f"tailles égales T={T} m={m} barre=1/{1 / b:.1f} : exact {P:.6f}, binomiale {Pb:.6f}")
    ok = pires_z < 4.5 and ecart_bin < 1e-9
    print(f"{nb} profils au hasard : plus grand écart à la simulation directe {pires_z:.2f} écarts-types ; "
          f"tailles égales : plus grand écart à la binomiale {ecart_bin:.2e} -> {'réussi' if ok else 'ÉCHEC'}")
    return 0 if ok else 1


def pilote() -> int:
    """Quelques tirages par type de case : validation et durée seulement (aucune issue de règle n'est affichée)."""
    verifier_sha_v4()
    v4g, v4c = charger_v4()
    val = nouvelle_validation()
    choix = [i for i, c in enumerate(CAS) if c["groupe"] != "grille"] + \
        [i for i, c in enumerate(CAS) if c["groupe"] == "grille" and (c["ref"] == "moteur" or c["multiple"] == 1.0)]
    taches = [(i, rep) for i in choix for rep in range(2)]
    t0 = time.time()
    with get_context("spawn").Pool(PROCESSUS) as pool:
        rs = pool.map(tirage, taches, chunksize=1)
    duree = time.time() - t0
    for r in rs:
        valider(r, val, v4g, v4c)
    print(json.dumps(val, ensure_ascii=False))
    print(f"{len(rs)} tirages en {duree:.1f} s sur {PROCESSUS} processus ({duree * PROCESSUS / len(rs):.3f} s par tirage"
          f" et par processus) ; écarts : {nb_ecarts(val)}")
    return 0 if not nb_ecarts(val) else 1


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
