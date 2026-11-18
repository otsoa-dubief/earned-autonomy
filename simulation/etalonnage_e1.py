"""Étalonnage de pm3 pour la règle A-dégâts (PLAN_EXPLORATION_E1.md, section 2).

A-dégâts est la règle v2 (amendement A1, α = 5 %) avec pb3 = pm3 ÷ 2, où pm3 est choisi pour que
l'excès du pire agent régulier égale le budget. Méthode (fixée avant E1) :

1. Agent régulier : sur les types d'un niveau, des erreurs indépendantes de taux q constant ;
   5 % d'actions invérifiables ; variantes d'épreuve au taux des cas difficiles, min(0,9 ; 6q).
2. Pour un type, la règle ne dépend que de ses propres preuves (pièce 2). Le palier 3 ne dépend que
   du score L3 (et des épreuves) : réversible ou non, la part du temps au palier 3, π3(q), est la même.
   Les épreuves sont jouées à blanc (décision 6) : l'excès par action du type vaut 0,95 · q · π3(q),
   et par 100 actions du flux, 0,95 · q · π3(q) · 100 · part du niveau. Il égale le budget si et
   seulement si q · π3(q) = barre.
3. On mesure π3(q) en régime stationnaire (la plus prudente des lectures : un départ à froid ne fait
   que retarder l'autonomie), par simulation d'un type isolé, fidèle au moteur action par action
   (même ordre : épreuve due, exécution, preuve ; mêmes opérations sur L ; test de cohérence avec
   regle.RegleUnTypeV2 dans tests/test_e1.py).
4. E(pm3) = max_q q · π3(q ; pm3) : grille de q autour du maximum, puis parabole sur les trois
   meilleurs points. On résout E(pm3) = barre par itérations pm3 ← pm3 · barre ÷ E(pm3), avec les
   mêmes tirages à chaque itération (nombres aléatoires communs), jusqu'à |E/barre − 1| < 0,3 %.

Usage : .venv/bin/python etalonnage_e1.py   (écrit etalonnage_e1.json ; les valeurs sont ensuite
recopiées dans config_e1.PM3_A_DEGATS, couvertes par le gel).
"""
import json
import math
import os
import sys
import time

import numpy as np

import config as C
import config_e1 as E

ICI = os.path.dirname(os.path.abspath(__file__))
LNB = math.log(C.BETA / (1 - E.ALPHA_A))
GRAINE_ETALONNAGE = [C.GRAINE, 20, 1]
# q exprimé en fraction de pm3 : la forme de q · π3(q) est presque invariante d'échelle pour
# les petits taux (b ≈ pm3 / 2) ; la grille couvre largement le maximum (repéré à l'essai).
GRILLE_HAUT = np.array([0.05, 0.07, 0.09, 0.11, 0.13, 0.15, 0.17, 0.20, 0.24, 0.30])
GRILLE_FAIBLE = np.array([0.25, 0.30, 0.35, 0.40, 0.44, 0.48, 0.52, 0.58, 0.66])


def constantes(pm3: float):
    pb3 = pm3 / 2
    a = math.log(pm3 / pb3)
    b = -math.log((1 - pm3) / (1 - pb3))
    return a, b, LNB - a


def simuler_un_type(q, pm3, haut, T, T_chauffe, rng=None, tirages=None, journal=None):
    """Un type isolé sous la règle A (v2), pour des agents réguliers de taux q (une voie par q).

    Rend le nombre d'actions exécutées au palier 3 sur [T_chauffe, T), par voie.
    `tirages` (tests) : liste de triplets (u_verif, u_err, u_epreuve) de tableaux par voie.
    `journal` (tests) : liste où ajouter, à chaque pas, le booléen « au palier 3 » par voie.
    """
    q = np.asarray(q, dtype=float)
    n = q.size
    a, b, f = constantes(pm3)
    qd = np.minimum(C.PLAFOND_DIFFICILE, C.FACTEUR_DIFFICILE * q)
    p_ep = (1 - qd) ** C.EPREUVE_VARIANTES
    L = np.zeros(n)
    Eo = np.zeros(n, dtype=np.int32)
    att = np.zeros(n, dtype=np.int32)
    n3 = np.zeros(n, dtype=np.int64)
    seuil = LNB + C.TOL
    for t in range(T):
        if tirages is not None:
            uv, ue, up = tirages[t]
        else:
            uv = rng.random(n)
            ue = rng.random(n)
            up = rng.random(n) if haut else None
        if haut:
            ouvert = Eo > 0
            if ouvert.any():
                attend = ouvert & (att > 0)
                att[attend] -= 1
                due = ouvert & ~attend
                passe = due & (up < p_ep)
                Eo[passe] -= 1
                att[due & ~passe] = C.EPREUVE_ATTENTE
        pal3 = (L <= seuil) & (Eo == 0)
        if journal is not None:
            journal.append(pal3.copy())
        if t >= T_chauffe:
            n3 += pal3
        ver = uv >= C.PART_INVERIFIABLE
        err = ue < q
        ok = ver & ~err & (Eo == 0)
        L[ok] = np.maximum(L[ok] - b, f)
        ko = ver & err
        if haut:
            L[ko] = np.maximum(L[ko], 0.0) + a
            Eo[ko] += 1
        else:
            L[ko] += a
    return n3


def excès_max(pm3, haut, R, mult_chauffe, mult_mesure, graine, grille=None):
    """E(pm3) = max_q q · π3(q) (stationnaire), avec la courbe mesurée."""
    grille = (GRILLE_HAUT if haut else GRILLE_FAIBLE) if grille is None else grille
    qs = np.minimum(grille * pm3, 0.95)
    q_voies = np.repeat(qs, R)
    tau = 1.0 / pm3
    T_chauffe = int(mult_chauffe * tau)
    T = T_chauffe + int(mult_mesure * tau)
    rng = np.random.default_rng(graine)
    n3 = simuler_un_type(q_voies, pm3, haut, T, T_chauffe, rng=rng)
    pi = (n3 / (T - T_chauffe)).reshape(len(qs), R)
    pi3 = pi.mean(axis=1)
    se = pi.std(axis=1, ddof=1) / math.sqrt(R)
    y = qs * pi3
    i = int(np.argmax(y))
    if 0 < i < len(qs) - 1:  # parabole sur les trois meilleurs points
        x3, y3 = qs[i - 1:i + 2], y[i - 1:i + 2]
        c2, c1, c0 = np.polyfit(x3, y3, 2)
        if c2 < 0:
            qstar = -c1 / (2 * c2)
            emax = float(np.polyval([c2, c1, c0], qstar))
        else:
            qstar, emax = float(qs[i]), float(y[i])
    else:
        qstar, emax = float(qs[i]), float(y[i])
    return dict(E=emax, q_pire=float(qstar), qs=qs.tolist(), pi3=pi3.tolist(), se_pi3=se.tolist(),
                q_pi3=y.tolist(), bord_de_grille=bool(i in (0, len(qs) - 1)), T=T, T_chauffe=T_chauffe)


def etalonner(melange, niveau, R=1000, mult_chauffe=60, mult_mesure=600, tol=0.003, it_max=8, log=print):
    barre = float(E.BARRES[(melange, niveau)])
    haut = niveau != "faible"
    pm3 = barre * (20.0 if haut else 3.1)  # point de départ (ordre de grandeur repéré à l'essai)
    graine = GRAINE_ETALONNAGE + [E.MELANGES.index(melange), E.NIVEAUX.index(niveau)]
    hist = []
    for it in range(it_max):
        r = excès_max(pm3, haut, R, mult_chauffe, mult_mesure, graine)
        rapport = r["E"] / barre
        hist.append(dict(pm3=pm3, E=r["E"], rapport=rapport, q_pire=r["q_pire"]))
        log(f"  {melange:15s} {niveau:6s} it {it}: pm3 = 1/{1 / pm3:,.1f}  E/barre = {rapport:.4f}  "
            f"q pire = {r['q_pire'] / barre:.2f} barre{'  (bord de grille !)' if r['bord_de_grille'] else ''}")
        if abs(rapport - 1) < tol:
            break
        pm3 = pm3 / rapport
    return dict(melange=melange, niveau=niveau, barre=barre, pm3=pm3, pb3=pm3 / 2, pm3_sur_barre=pm3 / barre,
                q_pire=r["q_pire"], q_pire_sur_barre=r["q_pire"] / barre, E_sur_barre=rapport,
                iterations=hist, courbe=dict(qs=r["qs"], pi3=r["pi3"], se_pi3=r["se_pi3"], q_pi3=r["q_pi3"]),
                bord_de_grille=r["bord_de_grille"], T=r["T"], T_chauffe=r["T_chauffe"], R=R,
                graine=graine)


def main():
    debut = time.time()
    out = dict(methode=__doc__, graine=GRAINE_ETALONNAGE, alpha=E.ALPHA_A, beta=C.BETA,
               date=time.strftime("%Y-%m-%d %H:%M:%S"), cellules=[])
    for m in E.MELANGES:
        for n in E.NIVEAUX:
            t0 = time.time()
            res = etalonner(m, n)
            res["duree_s"] = round(time.time() - t0, 1)
            out["cellules"].append(res)
            print(f"{m} {n}: pm3 = {res['pm3']:.6g} (1/{1 / res['pm3']:,.1f}, {res['pm3_sur_barre']:.2f} barre), "
                  f"pb3 = pm3/2, pire q = {res['q_pire_sur_barre']:.2f} barre, E/barre = {res['E_sur_barre']:.4f}"
                  f"  [{res['duree_s']} s]", flush=True)
    out["duree_s"] = round(time.time() - debut, 1)
    chemin = os.path.join(ICI, "etalonnage_e1.json")
    with open(chemin, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print("PM3_A_DEGATS = {")
    for c in out["cellules"]:
        print(f"    ({c['melange']!r}, {c['niveau']!r}): {c['pm3']!r},")
    print("}")
    print(f"écrit {chemin} ({out['duree_s']} s)")


if __name__ == "__main__":
    if "--essai" in sys.argv:
        for haut in (True, False):
            r = excès_max(0.004 if haut else 0.1, haut, 400, 60, 300, GRAINE_ETALONNAGE)
            print("haut" if haut else "faible", {k: (np.round(v, 4) if isinstance(v, list) else v)
                                                for k, v in r.items()})
    else:
        main()
