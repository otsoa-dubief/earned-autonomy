"""Diagnostic après coup du cinquième passage (NON préenregistré dans METHODE.md) : quels types établissent le
dépassement dans les R4 des règles C, et ce que donnerait l'exigence d'un type établi parmi les types jugeables.

Pourquoi : sur les mêmes tirages, les bornes exactes du moteur donnent plus de R4 à la barre que le chiffrage
exploratoire (qui ne voyait que les types faibles). Hypothèse à vérifier : « au moins un type établi » est une union
sur les types d'une configuration (écriture réversible, écriture durable, messages internes…), chacun testé à 5 %.

Méthode : on refait, avec leurs graines, les seuls tirages où une règle C donne R4 (`tirages.csv`), et l'on vérifie
d'abord que les cinq issues refaites sont identiques à celles du lancement. Les variantes sont plus strictes que leur
règle mère (leur R4 implique celui de la règle mère) : leurs parts, rapportées au nombre de tirages de la case, sont
donc exactes sans refaire les autres tirages.
- « -J » : chaque configuration jugeable (ou, pour la porte, détectable et jugeable) doit avoir un type JUGEABLE établi
  au-dessus (même borne que la règle mère).
- « C-rho1-Bonf » : C-ρ1 avec, dans chaque configuration, une borne basse à 1 − 0,05 ÷ k (k : types qui ont des
  écritures dans la configuration), correction de Bonferroni de l'union.

Usage (depuis simulation/, après le lancement ; au plus 12 processus) :
    env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/options_r4/diagnostic_types.py
Écrit `diagnostic_types.csv` dans ce dossier.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import csv  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import get_context  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

import numpy as np  # noqa: E402

import options_r4 as O  # noqa: E402  (même dossier ; ajoute simulation/ au chemin)
from rejeu import classes as CL  # noqa: E402
from rejeu import config_rejeu as CR  # noqa: E402
from rejeu import preuves as PR  # noqa: E402
from rejeu import suites as SU  # noqa: E402
from rejeu import types_regle as TY  # noqa: E402
from controle3 import harnais as H  # noqa: E402
from controle3 import mondes as MD  # noqa: E402

REGLES_C = ("C-rho1", "C-rhohat", "C-hybride", "C-porte")
VARIANTES = ("C-rho1-J", "C-rhohat-J", "C-hybride-J", "C-porte-J", "C-rho1-Bonf")
SORTIE = os.path.join(ICI, "diagnostic_types.csv")


def refaire(args) -> dict:
    i_cas, rep = args
    c = O.CAS[i_cas]
    cfg = H.config()
    monde = O.monde_du_cas(c)
    rng = np.random.default_rng(np.random.SeedSequence([int(O.GRAINE), 1000 + int(c["indice"]), int(rep)]))
    g = O.generer(monde, rng, cfg)
    e = g["entrees"]
    prep = PR.preparer(e, "confirmes")
    jks = {env: {m: SU.jeu_configuration(prep, e, env, m, g["cal"][env], "calibration") for m in CR.MODELES}
           for env in MD.ENVS}
    cls = CL.classes_tous_environnements(jks, cfg)
    issues = O.evaluer(jks, cls, monde)
    # détail par configuration : types jugeables et types établis (ρ = 1, ρ̂, hybride, Bonferroni à ρ = 1)
    jug, det, e1, eh, ehy, eb, e1j, ehj, ehyj = {}, {}, {}, {}, {}, {}, {}, {}, {}
    porteurs = {}   # configuration -> types établis à ρ = 1 (sigles)
    for env in MD.ENVS:
        for m in CR.MODELES:
            cle = (env, m)
            cl, j = cls[env][m], jks[env][m]
            jug[cle] = any(CL.jugeable(v) for v in cl.values())
            x_c, t_c = CL.erreurs_et_taches(j)
            r_prop = (CL.rho_fc_strates(CL.strates_par_type([j]))
                      if (x_c >= CL.SEUIL_ERREURS_CONF and t_c >= CL.SEUIL_TACHES_CONF) else None)
            rho_h = max(CL.PLANCHER_RHO, r_prop) if r_prop is not None else 1.0
            k_types = sum(1 for v in cl.values() if v["n"] > 0)
            pas = 1.0
            a1 = ah = ahy = ab = a1j = ahj = ahyj = False
            por = []
            for k, v in cl.items():
                if v["n"] <= 0:
                    continue
                par_t = CL.comptes_par_tache(j, (k,))
                ms = [mm for mm, _x in par_t.values()]
                x, n = sum(xx for _m, xx in par_t.values()), sum(ms)
                b = float(v["barre"])
                ju = CL.jugeable(v)
                t1, th = v["lo"] > b, v["lo_hyp"] > b
                _n, _mb, ne_h = CL.taille_effective(ms, rho_h)
                thy = CL.bornes_cp(x * ne_h / n, ne_h)[0] > b
                ne1 = float(v["n_eff_preuve"])
                tb = CL.bornes_cp(x * ne1 / n, ne1, 0.05 / k_types)[0] > b
                a1, ah, ahy, ab = a1 or t1, ah or th, ahy or thy, ab or tb
                a1j, ahj, ahyj = a1j or (t1 and ju), ahj or (th and ju), ahyj or (thy and ju)
                if t1:
                    por.append(TY.SIGLES[k] + ("*" if ju else ""))
                pas *= 1.0 - O.puissance_porte(tuple(sorted(ms)), b)
            det[cle] = 1.0 - pas >= O.PORTE_PROBA
            e1[cle], eh[cle], ehy[cle], eb[cle] = a1, ah, ahy, ab
            e1j[cle], ehj[cle], ehyj[cle] = a1j, ahj, ahyj
            porteurs[cle] = por
    r4a = issues["A"] == "R4"
    jugs = [cc for cc in O.CONFIGS if jug[cc]]
    dj = [cc for cc in O.CONFIGS if det[cc] and jug[cc]]
    var = {"C-rho1-J": r4a and all(e1j[cc] for cc in jugs),
           "C-rhohat-J": r4a and all(ehj[cc] for cc in jugs),
           "C-hybride-J": r4a and all(ehyj[cc] for cc in jugs),
           "C-porte-J": r4a and bool(dj) and all(e1j[cc] for cc in dj),
           "C-rho1-Bonf": r4a and all(eb[cc] for cc in jugs)}
    # mécanisme (pour les R4 de C-ρ1) : une configuration jugeable établie seulement par des types non jugeables
    seul_non_jugeable = any(e1[cc] and not e1j[cc] for cc in jugs)
    return dict(cas=i_cas, rep=rep, issues={g: issues[g] for g in O.REGLES}, var=var,
                seul_non_jugeable=seul_non_jugeable,
                porteurs=";".join(f"{cc[0]}/{cc[1].split('-')[1]}:{'+'.join(porteurs[cc]) or '-'}" for cc in jugs))


def main() -> int:
    if not os.path.exists(O.META):
        raise SystemExit("meta.json absent : lancer d'abord options_r4.py --lancer")
    attendu, n_cas, fiable_jug = {}, {}, {}
    with open(O.TIRAGES, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            i = int(r["cas"])
            n_cas[i] = n_cas.get(i, 0) + 1
            if any(r[g] == "R4" for g in REGLES_C):
                attendu[(i, int(r["rep"]))] = {g: r[g] for g in O.REGLES}
                fiable_jug[(i, int(r["rep"]))] = r["fiable_jug"] == "1"
    taches = sorted(attendu)
    print(f"{len(taches)} tirages à refaire (R4 sous au moins une règle C)", flush=True)
    t0 = time.time()
    with get_context("spawn").Pool(O.PROCESSUS) as pool:
        res = pool.map(refaire, taches, chunksize=8)
    ecarts = sum(r["issues"] != attendu[(r["cas"], r["rep"])] for r in res)
    print(f"refaits en {time.time() - t0:.0f} s ; issues identiques au lancement : {len(res) - ecarts}/{len(res)} "
          f"(écarts : {ecarts})", flush=True)
    if ecarts:
        print("ÉCARTS : les tirages refaits ne donnent pas les mêmes issues ; diagnostic non écrit")
        return 1
    lignes = []
    for i in sorted(n_cas):
        rs = [r for r in res if r["cas"] == i]
        n = n_cas[i]
        d = dict(cas=i, nom=O.NOMS[i], n=n)
        for g in REGLES_C:
            d[g] = sum(r["issues"][g] == "R4" for r in rs)
        for v in VARIANTES:
            k = sum(r["var"][v] for r in rs)
            lo, hi = O.wilson(k, n)
            kt = sum(r["var"][v] and fiable_jug[(r["cas"], r["rep"])] for r in rs)
            d.update({v: k, f"{v}_part": round(k / n, 5), f"{v}_bas": round(lo, 5), f"{v}_haut": round(hi, 5),
                      f"{v}_a_tort": kt})
        r4 = [r for r in rs if r["issues"]["C-rho1"] == "R4"]
        d["C-rho1_R4_etablis_seulement_par_non_jugeables"] = sum(r["seul_non_jugeable"] for r in r4)
        lignes.append(d)
    with open(SORTIE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)
    print("\n| case | n | C-ρ1 R4 | dont établis seulement par des types non jugeables | " + " | ".join(VARIANTES)
          + " |")
    print("|---|---|---|---|" + "---|" * len(VARIANTES))
    for d in lignes:
        if d["C-rho1"] == 0 and all(d[v] == 0 for v in VARIANTES) and not d["nom"].startswith(("critique", "M")):
            continue
        cel = [f"{O.pc(d[v + '_part'], 2)} [{O.pc(d[v + '_bas'], 2)}–{O.pc(d[v + '_haut'], 2)}]"
               if d["nom"].startswith(("critique", "M")) else f"{d[v]}" for v in VARIANTES]
        print(f"| {d['nom']} | {d['n']} | {d['C-rho1']} | {d['C-rho1_R4_etablis_seulement_par_non_jugeables']} | "
              + " | ".join(cel) + " |")
    print("\nR4 à tort (R4 avec une configuration jugeable fiable), mondes où des configurations fiables côtoient des "
          "mauvaises :")
    for d in lignes:
        if d["nom"] in ("M1", "M1-bis", "M2"):
            print(f"- {d['nom']} : " + " ; ".join(
                f"{v} {d[v + '_a_tort']}/{d['n']} = {O.pc(d[v + '_a_tort'] / d['n'], 2)} % "
                f"[{O.pc(O.wilson(d[v + '_a_tort'], d['n'])[0], 2)}–{O.pc(O.wilson(d[v + '_a_tort'], d['n'])[1], 2)}]"
                for v in VARIANTES))
    print("\nExemples de porteurs (critique 1x rho=1 tenus, R4 de C-ρ1 ; * = type jugeable) :")
    i0 = O.NOMS.index("critique 1x rho=1 tenus")
    for r in [r for r in res if r["cas"] == i0 and r["issues"]["C-rho1"] == "R4"][:8]:
        print(f"- rép. {r['rep']} : {r['porteurs']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
