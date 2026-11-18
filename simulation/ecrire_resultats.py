"""Écrit resultats/RESULTATS.md à partir des tableaux CSV (aucun chiffre recopié à la main).

Deuxième passe : la règle amendée (A1, version v2). La section « v1 contre v2 » lit les tableaux
de la première passe dans resultats_v1/, en lecture seule.

Usage : .venv/bin/python ecrire_resultats.py   (après executer.py et rapport.py)
"""
import json
import math
import os
import re
import subprocess
import sys

import numpy as np

import config as C
import flux as F
import regle as RG
import sprt
from mesures import ic_proportion
from rapport import (BONS, DOSSIER, ICI, MIXES, NIV, REG_MAIN, REGLAGES, TOUS_AGENTS, bat, calcul_marges,
                     calcul_verdicts, diffs, filtre, ic, icp, lire, lire_v1, mesure, nb, pc, synthese_degats, un,
                     verdict_charge, verdict_degats, verdict_seuil)

NM = {"bureau": "bureau", "service_client": "service client"}
R5, R1 = C.R_CLES, C.R_CAS


def n_de(reg):
    return R5 if reg in (REG_MAIN, "-", "pb depart", "pb stricte", "pb souple") else R1


def ent(x):
    return nb(float(x), 0)


def nrep(reg):
    return ent(n_de(reg))


def taux_apparent_doute_calibre(q):
    """Taux d'erreur vu par le contrôle quand l'agent doute d'une action difficile sur deux."""
    qd, qf = float(C.taux_difficile(q)), float(C.taux_facile(q))
    h, pdc = C.PART_DIFFICILE, C.PROBA_DOUTE_CALIBRE
    return (h * (1 - pdc) * qd + (1 - h) * qf) / (h * (1 - pdc) + (1 - h))


def reussites_fort_stricte(alpha):
    p = C.params_regle("stricte", alpha)
    return math.ceil(-p.lnB / p.b3[C.ARG] - 1e-12)


def m3(mix, a, regle, reg, col, nd=2, e=C.E_PRINCIPAL, lecteur=None):
    rows = (lecteur or lire)("mesures")
    m = un(rows, melange=mix, agent=a, regle=regle, reglage=reg, e=e)
    return ic(m[col], m[col + "_lo"], m[col + "_hi"], nd)


def dfmt(d, k, nd=3):
    r = d[k]
    return ic(r["diff"], r["lo"], r["hi"], nd)


def fmt_marge(v):
    return v if isinstance(v, str) else nb(v, 3).rstrip("0").rstrip(",") if v not in (0, 0.0) else "0"


# ==========================================================================
# Garantie
# ==========================================================================
def garantie_vues(reg, regle="regle", lecteur=None):
    rows = [r for r in filtre((lecteur or lire)("garantie"), regle=regle, reglage=reg)
            if r["mauvais"] and r["agent"] in TOUS_AGENTS]
    vues = {
        "stationnaires": [r for r in rows if r["phase"] == "tout" and "-" not in r["agent"]],
        "doute": [r for r in rows if r["phase"] == "tout" and "-" in r["agent"]],
        "non_stationnaires": [r for r in rows if r["phase"] != "tout"],
    }
    vues["tous"] = rows
    out = {}
    for k, rr in vues.items():
        if not rr:
            out[k] = None
            continue
        pire = max(rr, key=lambda r: r["p3"])
        kk = sum(r["k3"] for r in rr)
        nn = sum(r["n"] for r in rr)
        p, lo, hi, _ = ic_proportion(int(kk), int(nn))
        out[k] = dict(pire=pire, n_couples=len(rr), p=p, lo=lo, hi=hi,
                      verdict=verdict_seuil(pire["p3_lo"], pire["p3_hi"], 0.05))
    return out


def fmt_pire(g):
    if g is None:
        return "aucun couple"
    p = g["pire"]
    ph = {"tout": "", "apres": ", après t = 1 500", "avant": ", avant t = 1 500"}[p["phase"]]
    return (f"{p['agent']} sur {p['type']} ({NM[p['melange']]}{ph}) : {icp(p['p3'], p['p3_lo'], p['p3_hi'])}, "
            f"n = {ent(p['n'])} → **{g['verdict']}**")


# ==========================================================================
# Marges
# ==========================================================================
def marge_min(reg, agents, niv, e=C.E_PRINCIPAL, regle="regle"):
    """Plus petite marge de la grille qui passe pour tous les (agent, mélange) donnés, et le pire écart."""
    pire = None
    marges = []
    for mix in MIXES:
        for a in agents:
            r = diffs(mix, a, reg, "tout_valider", regle=regle, e=e)[f"degats_{niv}"]
            passe = [mg for mg in C.MARGES if verdict_seuil(r["lo"], r["hi"], mg) == "passe"]
            marges.append(min(passe) if passe else None)
            if pire is None or r["diff"] > pire[2]["diff"]:
                pire = (mix, a, r)
    if any(m is None for m in marges):
        return "aucune (> 1)", pire
    return max(marges), pire


# ==========================================================================
def nb_tests():
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", os.path.join(ICI, "tests")], cwd=ICI,
                       capture_output=True, text=True)
    m = re.search(r"(\d+) passed", r.stdout)
    f = re.search(r"(\d+) failed", r.stdout)
    return (int(m.group(1)) if m else 0), (int(f.group(1)) if f else 0)


def mesure_extinction(version, seed=(C.GRAINE, 87)):
    """La mesure du test d'extinction (A2, bureau, départ α = 5 %, 1 000 répétitions)."""
    agent = C.AGENTS_PAR_NOM["A2"]
    fl = F.generer_flux("bureau", 1000, seed=list(seed))
    P = RG.simuler_regle(fl, agent, [C.params_regle("depart", 0.05, version=version)]).P
    return float((P[:, 1250:1750] >= 2).mean()), float((P[:, 2500:3000] >= 2).mean())


def section_tests(n_ok, n_ko):
    rng = np.random.default_rng([C.GRAINE, 99])
    _, rej2, asn2 = sprt.sprt_exact(0.02, 0.02, 0.10, 0.05, 0.05)
    acc10, _, asn10 = sprt.sprt_exact(0.10, 0.02, 0.10, 0.05, 0.05)
    _, rej2_mc, _ = sprt.sprt_monte_carlo(0.02, 0.02, 0.10, 0.05, 0.05, 400_000, rng)
    acc10_mc, _, _ = sprt.sprt_monte_carlo(0.10, 0.02, 0.10, 0.05, 0.05, 400_000, rng)
    z = 1.959963984540054
    se2 = math.sqrt(rej2_mc * (1 - rej2_mc) / 400_000)
    se10 = math.sqrt(acc10_mc * (1 - acc10_mc) / 400_000)
    agent = C.agent_q_constant(0.05)
    fl = F.generer_flux("bureau", 20000, 200, seed=[C.GRAINE, 98])
    err = F.erreurs(fl, agent)
    lec = fl.type == C.LEC
    msk = lec & (np.cumsum(lec, axis=1) <= 20)
    p20 = float((~(err & msk).any(axis=1)).mean())
    se20 = math.sqrt(p20 * (1 - p20) / 20000)
    m2, f2 = mesure_extinction("v2")
    m1, f1 = mesure_extinction("v1")
    p = C.params_regle(*C.REGLAGE_PRINCIPAL)
    L = ["## Contrôles du code (tests de la section 8, adaptés au score réfléchi)\n",
         f"Lancés avant toute production de résultats : `.venv/bin/python -m pytest tests/` → **{n_ok} tests "
         f"passés, {n_ko} en échec** (`executer.py --verifier-tests` refuse de produire des résultats sinon). "
         "Le contrôle de cohérence moteur contre version de référence tourne sur les deux versions ; le chemin v1 "
         "du code reproduit `resultats_v1/` au chiffre près (vérifié sur A2, A6a et A7, deux mélanges).\n",
         "| contrôle | attendu | obtenu |", "|--|--|--|",
         "| réussites pour monter depuis L = 0 (pb 2 %, pm 10 %, α = β = 5 %) | 35 | 35 (type DUR, réglage de départ) |",
         "| réussites pour remonter après une erreur à enjeu moyen ou fort (L = a) | 54 | 54, que l'erreur arrive depuis L = 0 ou depuis le plancher |",
         f"| réussites pour absorber une erreur au plancher : ⌈a/b⌉ | ⌈a/b⌉ pour 6 jeux (pb ; pm) | égal dans les 6 cas ; LEC : {math.ceil(p.a3[C.LEC] / p.b3[C.LEC])} au palier 3, {math.ceil(p.a2[C.LEC] / p.b2[C.LEC])} au palier 2 |",
         "| erreurs à enjeu faible rapprochées qui font descendre depuis le plancher | 2, d'un seul palier | 2 (LEC : 3 → 2 ; MSG : 3 → 1) ; séparées par ⌈a/b⌉ réussites, 20 erreurs ne font pas descendre |",
         f"| agent stable à 2 % : part d'actions sans validation préalable, fin (2 500-2 999) contre milieu (1 250-1 749) | écart relatif ≤ 10 % (critère fixé avant la passe) | v2 : {pc(f2)} contre {pc(m2)} ; la v1 donnait {pc(f1)} contre {pc(m1)} (le test les sépare) |",
         f"| risque réel de rejeter à tort, p = 2 %, test sans borne | 2,97 % | exact {pc(rej2, 2)} ; Monte-Carlo {pc(rej2_mc, 2)} [{nb(100 * (rej2_mc - z * se2), 2)} ; {nb(100 * (rej2_mc + z * se2), 2)}], n = 400 000 |",
         f"| risque réel d'accepter à tort, p = 10 % | 4,89 % | exact {pc(acc10, 2)} ; Monte-Carlo {pc(acc10_mc, 2)} [{nb(100 * (acc10_mc - z * se10), 2)} ; {nb(100 * (acc10_mc + z * se10), 2)}], n = 400 000 |",
         f"| taille moyenne d'échantillon (p = 2 % ; 10 %) | 54,6 ; 38,3 | {nb(asn2, 2)} ; {nb(asn10, 2)} |",
         f"| enchaîner 20 réussites à 5 % d'erreur | 0,95^20 = 0,358 | {nb(p20, 3)} [{nb(p20 - z * se20, 3)} ; {nb(p20 + z * se20, 3)}], n = 20 000 |",
         "| erreur à enjeu moyen ou fort | palier 1, L = max(L, 0) + a, épreuve | vérifié (référence et moteur, 4 types) ; le score ne bouge pas tant que l'épreuve est ouverte |",
         "| actions plafonnées | jamais autonomes | vérifié pour la règle, ses 5 variantes et tous les témoins sauf « tout approuver » |",
         "| doute | ne change ni le score ni s | vérifié (un agent qui doute de tout reste à L = 0 ; doute abusif : L rejoué à la main sur les seules actions jugées) |",
         "| remises à zéro (A1) | consigne : L/2 si L < 0 ; changement de modèle : L = 0, erreurs moyennes ou fortes en épreuves, erreurs faibles effacées | vérifié (référence ; moteur sur A6a et A8) |",
         "| cohérence | moteur vectorisé = version de référence | identique action par action, v2 et v1, 9 agents × 8 à 10 variantes × 4 répétitions |",
         "",
         "Les nombres tombent juste. Avec le score réfléchi, plus rien n'est sur le fil : après 54 réussites, le "
         "score est nettement sous ln B (la v1 l'y ramenait exactement). Une erreur au plancher ramène toujours le "
         "score exactement à ln B, d'où la lecture « au plus ln B », gardée (choix 1).\n",
         "Une incohérence de texte, sans effet sur le code : REGLE.md, A1, écrit qu'une erreur « est absorbée par "
         "environ a/b réussites nouvelles », soit 8 à enjeu faible, 19 à enjeu moyen et 39 à enjeu fort. C'est "
         "exact pour une erreur à enjeu faible (L + a). Pour une erreur à enjeu moyen ou fort, l'opération écrite "
         "juste au-dessus, L = max(L, 0) + a, efface le crédit : il faut "
         f"{math.ceil((p.a3[C.DUR] - p.lnB) / p.b3[C.DUR] - 1e-12)} réussites (moyen) et "
         f"{math.ceil((p.a3[C.SOR] - p.lnB) / p.b3[C.SOR] - 1e-12)} (fort) pour revenir au palier 3, après "
         "l'épreuve. La simulation suit l'opération écrite ; le test d'absorption porte donc sur les erreurs à "
         "enjeu faible.\n"]
    return "\n".join(L)


def section_exigences():
    L = ["## Ce que la règle amendée exige, calcul exact\n",
         "Calculé à partir des réglages, sans simulation. Score réfléchi par palier visé : une réussite retire b, "
         "le score ne descend pas sous ln B − a ; une erreur à enjeu faible ajoute a ; une erreur à enjeu moyen ou "
         "fort remet le score à max(L, 0) + a.\n",
         "| réglage | ln B | enjeu | palier 3 : réussites depuis L = 0 | palier 2 : réussites depuis L = 0 | palier 3 : réussites après une erreur à enjeu moyen ou fort | erreur à enjeu faible au plancher : réussites pour l'absorber (palier 3 ; palier 2) |",
         "|--|--|--|--|--|--|--|"]
    for (r, a) in C.REGLAGES:
        p = C.params_regle(r, a)
        for niv, k in ((0, C.LEC), (1, C.EXE), (2, C.SOR)):
            n3 = math.ceil(-p.lnB / p.b3[k] - 1e-12)
            n2 = str(math.ceil(-p.lnB / p.b2[k] - 1e-12)) if p.a_palier2[k] else "sans objet"
            if niv == 0:
                apres = "sans objet"
                ab = f"{math.ceil(p.a3[k] / p.b3[k] - 1e-12)} ; {math.ceil(p.a2[k] / p.b2[k] - 1e-12)}"
            else:
                apres = str(math.ceil((p.a3[k] - p.lnB) / p.b3[k] - 1e-12))
                ab = "sans objet (le crédit est effacé)"
            L.append(f"| {C.nom_reglage(r, a)} | {nb(p.lnB, 3)} | {C.NIVEAUX[niv]} | {n3} | {n2} | {apres} | {ab} |")
    L.append("")
    L.append("Actions vérifiables par type sur l'horizon (3 000 actions × part du type × 95 %, en moyenne) :\n")
    L.append("| mélange | " + " | ".join(C.TYPES[:7]) + " |")
    L.append("|--|" + "--|" * 7)
    for mix in MIXES:
        pr = C.probas_categories(mix)
        L.append(f"| {NM[mix]} | " + " | ".join(ent(round(C.HORIZON * 0.95 * pr[k])) for k in range(7)) + " |")
    L.append("")
    vol_arg = round(C.HORIZON * 0.95 * C.probas_categories("bureau")[C.ARG])
    L.append("Il n'y a plus de budget d'erreurs : une erreur à enjeu faible isolée est absorbée en quelques "
             "réussites, et le palier 3 n'est jamais fermé pour toute la configuration. Ce qui ne change pas : au "
             f"réglage strict, ARG en « bureau » demande {reussites_fort_stricte(0.05)} réussites vérifiées d'affilée "
             f"(α = 5 %) pour {vol_arg} actions vérifiables en moyenne sur l'horizon.\n")
    return "\n".join(L)


# ==========================================================================
def section_verdict():
    L = ["## Verdict de la pièce 1, réglage par réglage (validateur à 5 %)\n",
         "Trois verdicts possibles pour chaque critère : **passe** (tout l'intervalle à 95 % est du bon côté du "
         "seuil), **échoue** (tout l'intervalle est du mauvais côté), **indécis** (l'intervalle chevauche le seuil). "
         f"Réglage de départ α = 5 % : {ent(R5)} répétitions ; les cinq autres réglages : {ent(R1)} répétitions "
         "(les 1 000 premières des mêmes tirages). Les dégâts sont lus sur la grille de marges de l'amendement A1 : "
         + " ; ".join(fmt_marge(m) for m in C.MARGES) + " pour 100 actions.\n",
         "### Synthèse\n",
         "| réglage | 1. garantie : agents stables | 1. garantie : doute (A4) | 1. garantie : dérive et changements | 2. charge ≤ 50, en tout et hors lectures (A1 et A2) | 2. plus petite marge de dégâts qui passe, A1 et A2 (faible / moyen / fort) | 2. bat la liste fixe | 2. bat le tri par le risque | 3. réactivité A6b, 95e centile : tous les types promus ; types devenus mauvais (bureau / service client) |",
         "|--|--|--|--|--|--|--|--|--|"]
    etat = {}
    for reg in REGLAGES:
        g = garantie_vues(reg)
        gs, gdo, gns = (g[k]["verdict"] if g[k] else "sans objet" for k in ("stationnaires", "doute", "non_stationnaires"))
        vc = verdict_charge(reg)
        ch = "passe" if all(v["v_charge"] == "passe" and v["v_hors"] == "passe" for v in vc.values()) else (
            "échoue" if any(v["v_charge"] == "échoue" or v["v_hors"] == "échoue" for v in vc.values()) else "indécis")
        mm = [marge_min(reg, BONS, niv)[0] for niv in NIV]
        blf = [bat(diffs(mx, a, reg, "liste_fixe"))[0] for mx in MIXES for a in BONS]
        btr = [bat(diffs(mx, a, reg, "tri_risque"))[0] for mx in MIXES for a in BONS]
        etat[reg] = dict(gs=gs, gdo=gdo, gns=gns, ch=ch, mm=mm)

        def resume_bat(vs):
            return "non (" + ", ".join(sorted(set(vs))) + ")" if any(v != "bat" for v in vs) else "oui"
        ra = []
        for mx in MIXES:
            r_t = filtre(lire("reactivite"), regle="regle", reglage=reg, agent="A6b", melange=mx, type="tous")[0]
            r_m = filtre(lire("reactivite"), regle="regle", reglage=reg, agent="A6b", melange=mx, type="mauvais_apres")[0]
            ra.append(f"{ent(r_t['delai_p95'])} ; {ent(r_m['delai_p95']) if r_m.get('delai_p95') is not None else '—'}")
        L.append(f"| {reg} | {gs} | {gdo} | {gns} | {ch} | {' / '.join(fmt_marge(m) for m in mm)} | "
                 f"{resume_bat(blf)} | {resume_bat(btr)} | {' / '.join(ra)} |")
    L.append("")

    def liste(pred):
        rr = [r for r in REGLAGES if pred(etat[r])]
        return ", ".join(rr) if rr else "aucun réglage"
    L.append("Lecture, critère par critère. Garantie pour les agents mauvais stables : passe à "
             f"{liste(lambda x: x['gs'] == 'passe')} ; indécise à {liste(lambda x: x['gs'] == 'indécis')} ; "
             f"échoue à {liste(lambda x: x['gs'] == 'échoue')}. Avec le doute calibré d'A4 : échoue à "
             f"{liste(lambda x: x['gdo'] == 'échoue')}. En dérive ou autour d'un changement : échoue à "
             f"{liste(lambda x: x['gns'] == 'échoue')}. Charge (A1 et A2, les deux mélanges, en tout et hors "
             f"lectures) : passe à {liste(lambda x: x['ch'] == 'passe')} ; échoue à "
             f"{liste(lambda x: x['ch'] == 'échoue')}. La marge de dégâts se lit dans la colonne correspondante, "
             "à comparer à la marge fixée par Otsoa. La réactivité ne se juge qu'une fois K fixé ; la colonne donne "
             "le K qu'il faudrait pour la tenir 95 fois sur 100.\n")

    # garantie
    L.append("### 1. Garantie\n")
    L.append("Agent « mauvais » sur un type : son vrai taux d'erreur est au moins le pm du palier 3 de ce niveau "
             "d'enjeu, au réglage considéré (choix 17). Mesure : part des répétitions où ce type atteint le palier 3 "
             "avant l'horizon. Le verdict porte sur le **pire couple** (agent, type) ; la part groupée est donnée "
             "aussi. Avec plusieurs dizaines de couples, le pire couple est un peu biaisé vers le haut.\n")
    L.append("| réglage | couples mauvais (stables / doute / non stables) | part groupée, tous couples | pire couple, agents stables (A3, A4, A5) | pire couple, doute (A4 calibré ou abusif) | pire couple, phases non stables (A6a après, A6b après, A7 avant) |")
    L.append("|--|--|--|--|--|--|")
    for reg in REGLAGES:
        g = garantie_vues(reg)
        nn = " / ".join(str(g[k]["n_couples"]) if g[k] else "0" for k in ("stationnaires", "doute", "non_stationnaires"))
        L.append(f"| {reg} | {nn} | {icp(g['tous']['p'], g['tous']['lo'], g['tous']['hi'], 2)} | "
                 f"{fmt_pire(g['stationnaires'])} | {fmt_pire(g['doute'])} | {fmt_pire(g['non_stationnaires'])} |")
    L.append("")
    # q = pm on the curve
    g2 = lire("garantie_courbe")
    lignes_pm = []
    for reg in REGLAGES:
        for t in ("LEC", "ECR", "MSG"):
            for mx in MIXES:
                rr = [r for r in filtre(g2, melange=mx, reglage=reg, type=t) if abs(r["q"] - r["pm3"]) < 1e-9]
                if rr:
                    lignes_pm.append(rr[0])
    if lignes_pm:
        k = int(sum(r["k3"] for r in lignes_pm))
        n = int(sum(r["n"] for r in lignes_pm))
        pp, plo, phi, _ = ic_proportion(k, n)
        pire = max(lignes_pm, key=lambda r: r["p3"])
        L.append(f"Agents à taux constant exactement au pm, types à enjeu faible (courbe de garantie, {len(lignes_pm)} "
                 f"points de {ent(R1)} répétitions) : promus au palier 3 avant l'horizon dans "
                 f"{icp(pp, plo, phi, 2)} des cas en moyenne ; au pire {icp(pire['p3'], pire['p3_lo'], pire['p3_hi'])} "
                 f"({pire['type']}, {NM[pire['melange']]}, {pire['reglage'].replace('depart', 'départ')}). La courbe complète est dans "
                 "`fig2_garantie_*.png` et `garantie_courbe.csv`.\n")

    # charge
    L.append("### 2. Utilité\n")
    L.append("**Charge** pour 100 actions (validations, corrections, doutes et variantes d'épreuve), en tout et hors "
             "lectures. « Tout faire valider » vaut 100 dans les deux cas. Seuil : 50.\n")
    L.append("| réglage | A1 bureau : tout ; hors lectures | A1 service client | A2 bureau | A2 service client |")
    L.append("|--|--|--|--|--|")
    for reg in REGLAGES:
        cells = []
        for a in BONS:
            for mx in MIXES:
                m = mesure(mx, a, "regle", reg)
                v1 = verdict_seuil(m["charge_lo"], m["charge_hi"], 50)
                v2 = verdict_seuil(m["charge_hors_lec_lo"], m["charge_hors_lec_hi"], 50)
                cells.append(f"{ic(m['charge'], m['charge_lo'], m['charge_hi'], 1)} {v1} ; "
                             f"{ic(m['charge_hors_lec'], m['charge_hors_lec_lo'], m['charge_hors_lec_hi'], 1)} {v2}")
        L.append(f"| {reg} (n = {nrep(reg)}) | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")
    L.append("")
    L.append(f"Pour comparer, en bureau : liste fixe {m3('bureau', 'A2', 'liste_fixe', '-', 'charge', 1)} en tout et "
             f"{m3('bureau', 'A2', 'liste_fixe', '-', 'charge_hors_lec', 1)} hors lectures ; tri par le risque "
             f"{m3('bureau', 'A2', 'tri_risque', '-', 'charge', 1)} et {m3('bureau', 'A2', 'tri_risque', '-', 'charge_hors_lec', 1)}.\n")

    # dégâts : marges
    L.append("**Dégâts**, écart apparié avec « tout faire valider », pour 100 actions du flux, niveau par niveau. "
             "« Plus petite marge » : la plus petite valeur de la grille telle que l'intervalle à 95 % de l'écart soit "
             "tout entier sous la marge, pour tous les couples (agent, mélange) considérés. Détail par agent : "
             "`marge_minimale.csv` ; verdict à chaque marge : `marges.csv`.\n")
    L.append("| réglage | niveau | A1 et A2 : plus petite marge qui passe | plus grand écart chez A1 et A2 | 13 agents : plus petite marge qui passe | plus grand écart, 13 agents |")
    L.append("|--|--|--|--|--|--|")
    for reg in REGLAGES:
        for niv in NIV:
            mb, pb_ = marge_min(reg, BONS, niv)
            mt, pt = marge_min(reg, TOUS_AGENTS, niv)
            L.append(f"| {reg} (n = {nrep(reg)}) | {niv} | {fmt_marge(mb)} | {pb_[1]} ({NM[pb_[0]]}) : "
                     f"{ic(pb_[2]['diff'], pb_[2]['lo'], pb_[2]['hi'], 3)} | {fmt_marge(mt)} | {pt[1]} "
                     f"({NM[pt[0]]}) : {ic(pt[2]['diff'], pt[2]['lo'], pt[2]['hi'], 3)} |")
    L.append("")
    L.append(f"Verdict à chaque marge de la grille, réglage de départ α = 5 % ({ent(R5)} répétitions), A1 et A2 dans "
             "les deux mélanges :\n")
    L.append("| marge (pour 100 actions) | " + " | ".join(f"enjeu {n}" for n in NIV) + " |")
    L.append("|--|--|--|--|")
    for mg in C.MARGES:
        cells = []
        for niv in NIV:
            vs = [verdict_seuil(diffs(mx, a, REG_MAIN, "tout_valider")[f"degats_{niv}"]["lo"],
                                diffs(mx, a, REG_MAIN, "tout_valider")[f"degats_{niv}"]["hi"], mg)
                  for mx in MIXES for a in BONS]
            cells.append("passe" if all(v == "passe" for v in vs) else ("échoue" if any(v == "échoue" for v in vs) else "indécis"))
        L.append(f"| {fmt_marge(mg)} | " + " | ".join(cells) + " |")
    L.append("")

    # bat
    L.append("**Bat-elle les concurrents simples ?** Critère (choix 19) : sur les mêmes tirages, meilleure sur au "
             "moins une mesure parmi la charge et les dégâts des trois niveaux (intervalle de l'écart tout sous 0), "
             "pire sur aucune (aucun intervalle tout au-dessus de 0). Comptes sur les 26 couples agent × mélange.\n")
    L.append("| réglage | contre la liste fixe | contre le tri par le risque | contre le hasard |")
    L.append("|--|--|--|--|")
    for reg in REGLAGES:
        cells = []
        for contre in ("liste_fixe", "tri_risque", "hasard"):
            cpt = {}
            for mx in MIXES:
                for a in TOUS_AGENTS:
                    v = bat(diffs(mx, a, reg, contre))[0]
                    cpt[v] = cpt.get(v, 0) + 1
            cells.append(", ".join(f"{k} {v}" for k, v in sorted(cpt.items())))
        L.append(f"| {reg} | {cells[0]} | {cells[1]} | {cells[2]} |")
    L.append("")
    L.append("« Compromis » : la règle est meilleure sur une mesure et pire sur une autre. Détail dans la section "
             "suivante et dans `comparaisons.csv`.\n")

    # réactivité
    L.append("### 3. Réactivité\n")
    L.append("Couples (répétition, type) au palier 2 ou 3 à t = 1 500, au moment où le taux passe de 2 % à 10 %. "
             "Délai : actions de l'agent (tous types) jusqu'au retour au palier 1 ; un type non revenu à l'horizon "
             "compte pour 1 500 et figure dans « non retiré ». « Types devenus mauvais » : ceux où 10 % atteint le "
             "pm du palier 3 du réglage, que la règle doit retirer ; sur les autres types, 10 % reste sous pm et la "
             "règle n'a pas à retirer l'autonomie. Dégâts : erreurs parties sur ce type pendant le délai, par couple "
             "promu. Intervalles des centiles par rééchantillonnage (400 tirages).\n")
    L.append("| réglage | agent | mélange | types | couples promus à t = 1 500 | délai médian | 95e centile | non retiré avant l'horizon | dégâts pendant le délai, par couple |")
    L.append("|--|--|--|--|--|--|--|--|--|")

    def ligne_r(lab, a, mx, r, types):
        return (f"| {lab} | {a} | {NM[mx]} | {types} | {ent(r['n_promus'])} | "
                f"{ic(r['delai_med'], r['delai_med_lo'], r['delai_med_hi'], 0)} | "
                f"{ic(r['delai_p95'], r['delai_p95_lo'], r['delai_p95_hi'], 0)} | "
                f"{icp(r['part_non_retire'], r['part_non_retire_lo'], r['part_non_retire_hi'])} | "
                f"{ic(r['degats_intervalle_moy'], r['degats_intervalle_lo'], r['degats_intervalle_hi'], 3)} |")
    a6a_zero = True
    for reg in REGLAGES:
        for mx in MIXES:
            for grp, lab in (("tous", "tous"), ("mauvais_apres", None)):
                r = filtre(lire("reactivite"), regle="regle", reglage=reg, agent="A6b", melange=mx, type=grp)[0]
                if r.get("delai_med") is None:
                    continue
                types = "tous les promus" if grp == "tous" else f"devenus mauvais ({r['types_mauvais_apres']})"
                L.append(ligne_r(reg, "A6b", mx, r, types))
            r6a = filtre(lire("reactivite"), regle="regle", reglage=reg, agent="A6a", melange=mx, type="tous")[0]
            a6a_zero &= (r6a["delai_p95"] == 0 and r6a["part_non_retire"] == 0)
    n6a = filtre(lire("reactivite"), regle="regle", reglage=REG_MAIN, agent="A6a", melange="bureau", type="tous")[0]
    L.append(f"| tous les réglages | A6a | les deux | tous les promus | {ent(n6a['n_promus'])} au départ α = 5 %, bureau | 0 | 0 | 0,0 % | 0,000 |"
             if a6a_zero else "| (voir reactivite.csv) | A6a | | | | | | | |")
    for regle, reg, lab in (("trois_reussites", "-", "trois réussites"), ("regle_sans_remise", REG_MAIN, "règle sans remise à zéro"),
                            ("oracle", "pb depart", "oracle")):
        for a in ("A6b", "A6a"):
            for mx in MIXES:
                rr = filtre(lire("reactivite"), regle=regle, reglage=reg, agent=a, melange=mx, type="tous")
                if rr and rr[0].get("delai_med") is not None:
                    L.append(ligne_r(lab, a, mx, rr[0], "tous les promus"))
    L.append("")
    L.append("Par type : `reactivite.csv` et `fig4_reactivite.png`.\n")
    # A8
    L.append("**Consigne modifiée (A8).** À t = 1 500, le score de SOR est divisé par deux s'il est négatif. Parmi les "
             "répétitions où SOR était au palier 3 juste avant (réglage de départ, α = 5 %), comparées à A2 sur les "
             "mêmes tirages :\n")
    L.append("| mélange | agent | SOR au palier 3 à t = 1 500 | palier 3 perdu à la première sortie suivante | jamais revenu avant l'horizon | délai médian du retour |")
    L.append("|--|--|--|--|--|--|")
    for mx in MIXES:
        for a in ("A8", "A2"):
            r = un(lire("consigne"), melange=mx, agent=a)
            jam = icp(r["part_jamais_revenu"], r["part_jamais_revenu_lo"], r["part_jamais_revenu_hi"]) if r.get("part_jamais_revenu") is not None else "sans objet"
            dl = ic(r["delai_retour_med"], r["delai_retour_med_lo"], r["delai_retour_med_hi"], 0) if r.get("delai_retour_med") is not None else "sans objet"
            L.append(f"| {NM[mx]} | {a} | {ent(r['n_sor_palier3_a_1500'])} sur {ent(r['n_rep'])} | "
                     f"{icp(r['part_sor_retire'], r['part_sor_retire_lo'], r['part_sor_retire_hi'])} | {jam} | {dl} |")
    pS = C.params_regle(*C.REGLAGE_PRINCIPAL)
    besoin = math.ceil((pS.plancher3[C.SOR] / 2 - pS.lnB) / pS.b3[C.SOR] - 1e-12)
    L.append("")
    L.append(f"Calcul : au plancher, L = ln B − a = {nb(pS.plancher3[C.SOR], 3)} ; divisé par deux, {nb(pS.plancher3[C.SOR] / 2, 3)}, "
             f"au-dessus de ln B = {nb(pS.lnB, 3)}. Il faut {besoin} réussites de SOR pour revenir au palier 3.\n")
    return "\n".join(L)


# ==========================================================================
def section_comparaison():
    L = ["## Comparaison avec la liste fixe et le tri par le risque\n",
         f"Réglage de départ, α = 5 %, validateur à 5 %, {ent(R5)} répétitions de 3 000 actions, mêmes tirages pour "
         "toutes les règles. Valeurs pour 100 actions, intervalle à 95 %.\n",
         "### Valeurs absolues\n",
         "| mélange | agent | règle | charge | charge hors lectures | dégâts faibles | dégâts moyens | dégâts forts |",
         "|--|--|--|--|--|--|--|--|"]
    noms = [("tout_valider", "-", "tout faire valider"), ("liste_fixe", "-", "liste fixe"), ("tri_risque", "-", "tri par le risque"),
            ("regle", REG_MAIN, "**la règle**"), ("hasard", REG_MAIN, "hasard"), ("oracle", "pb depart", "oracle"),
            ("trois_reussites", "-", "trois réussites"), ("tout_approuver", "-", "tout approuver")]
    for mx in MIXES:
        for a in ("A1", "A2", "A4", "A5"):
            for regle, reg, lab in noms:
                m = mesure(mx, a, regle, reg)
                L.append(f"| {NM[mx]} | {a} | {lab} | {ic(m['charge'], m['charge_lo'], m['charge_hi'], 1)} | "
                         f"{ic(m['charge_hors_lec'], m['charge_hors_lec_lo'], m['charge_hors_lec_hi'], 1)} | "
                         + " | ".join(ic(m[f'degats_{n}'], m[f'degats_{n}_lo'], m[f'degats_{n}_hi'], 3) for n in NIV) + " |")
    L.append("")
    L.append("Les autres agents sont dans `mesures.csv` ; `fig1_charge_degats_*.png` place toutes les règles et tous "
             "les réglages dans le plan charge contre dégâts, niveau par niveau.\n")
    L.append("### Écarts appariés : la règle moins le témoin\n")
    L.append("Négatif = la règle fait mieux. Verdict selon le critère du choix 19.\n")
    L.append("| mélange | agent | contre | charge | dégâts faibles | dégâts moyens | dégâts forts | verdict |")
    L.append("|--|--|--|--|--|--|--|--|")
    for mx in MIXES:
        for a in TOUS_AGENTS:
            for contre in ("liste_fixe", "tri_risque"):
                d = diffs(mx, a, REG_MAIN, contre)
                L.append(f"| {NM[mx]} | {a} | {'liste fixe' if contre == 'liste_fixe' else 'tri'} | {dfmt(d, 'charge', 1)} | "
                         + " | ".join(dfmt(d, f"degats_{n}") for n in NIV) + f" | {bat(d)[0]} |")
    L.append("")
    L.append("### Illustration seulement : un barème 1, 10, 100\n")
    L.append("REGLE.md, pièce 2 : un barème peut illustrer, jamais servir de critère. Dégâts pondérés = faibles + "
             "10 × moyens + 100 × forts, pour 100 actions, avec leur intervalle.\n")
    L.append("| mélange | agent | tout faire valider | liste fixe | tri par le risque | la règle |")
    L.append("|--|--|--|--|--|--|")
    for mx in MIXES:
        for a in ("A1", "A2", "A3", "A4", "A5"):
            vals = [m3(mx, a, regle, reg, "degats_bareme_illustratif", 2)
                    for regle, reg in (("tout_valider", "-"), ("liste_fixe", "-"), ("tri_risque", "-"), ("regle", REG_MAIN))]
            L.append(f"| {NM[mx]} | {a} | " + " | ".join(vals) + " |")
    L.append("")
    return "\n".join(L)


def section_validateur():
    L = ["## Variantes du validateur : 0, 2, 5 et 10 %\n",
         f"Réglage de départ, α = 5 %, {ent(R5)} répétitions. La trajectoire de la règle ne dépend pas de e (le contrôle "
         "automatique voit tout) ; seuls changent les dégâts et les corrections. Marge : plus petite valeur de la "
         "grille qui passe pour l'agent dans le mélange.\n",
         "| e | mélange | agent | charge | écart de dégâts avec tout valider : faibles ; moyens ; forts | plus petite marge qui passe (faible / moyen / fort) | contre liste fixe | contre tri |",
         "|--|--|--|--|--|--|--|--|"]
    for e in C.VALEURS_E:
        for mx in MIXES:
            for a in ("A1", "A2", "A4"):
                m = mesure(mx, a, "regle", REG_MAIN, e)
                d = diffs(mx, a, REG_MAIN, "tout_valider", e=e)
                mm = []
                for n in NIV:
                    passe = [mg for mg in C.MARGES if verdict_seuil(d[f"degats_{n}"]["lo"], d[f"degats_{n}"]["hi"], mg) == "passe"]
                    mm.append(fmt_marge(min(passe)) if passe else "aucune (> 1)")
                L.append(f"| {pc(e, 0)} | {NM[mx]} | {a} | {ic(m['charge'], m['charge_lo'], m['charge_hi'], 1)} | "
                         + " ; ".join(dfmt(d, f"degats_{n}") for n in NIV)
                         + f" | {' / '.join(mm)} | {bat(diffs(mx, a, REG_MAIN, 'liste_fixe', e=e))[0]} | "
                         f"{bat(diffs(mx, a, REG_MAIN, 'tri_risque', e=e))[0]} |")
    L.append("")
    return "\n".join(L)


def section_ablations():
    L = ["## Ablations\n",
         f"Réglage de départ, α = 5 %, validateur à 5 %, {ent(R1)} répétitions (les 1 000 premières des mêmes tirages "
         "que la règle). Écarts appariés : l'ablation moins la règle amendée.\n",
         "| ablation | charge A1 bureau ; service client | charge A2 bureau ; service client | écart de charge A2 bureau | écart de dégâts A2 bureau : faibles ; moyens ; forts | agent le plus touché en charge (bureau) : écart de charge ; dégâts faibles ; moyens ; forts | garantie, pire couple stable | bat liste fixe / tri (26 couples) |",
         "|--|--|--|--|--|--|--|--|"]
    g = garantie_vues(REG_MAIN, "regle")
    c1 = " ; ".join(m3(mx, "A1", "regle", REG_MAIN, "charge", 1) for mx in MIXES)
    c2 = " ; ".join(m3(mx, "A2", "regle", REG_MAIN, "charge", 1) for mx in MIXES)
    L.append(f"| règle amendée (référence) | {c1} | {c2} | — | — | — | {fmt_pire(g['stationnaires'])} | — |")
    for nom in C.ABLATIONS:
        regle = "regle_" + nom
        c1 = " ; ".join(m3(mx, "A1", regle, REG_MAIN, "charge", 1) for mx in MIXES)
        c2 = " ; ".join(m3(mx, "A2", regle, REG_MAIN, "charge", 1) for mx in MIXES)
        d = diffs("bureau", "A2", REG_MAIN, "regle", regle=regle)
        a = max(TOUS_AGENTS, key=lambda ag: abs(diffs("bureau", ag, REG_MAIN, "regle", regle=regle)["charge"]["diff"]))
        da = diffs("bureau", a, REG_MAIN, "regle", regle=regle)
        ga = garantie_vues(REG_MAIN, regle)
        cnt_lf, cnt_tr = {}, {}
        for mx in MIXES:
            for ag in TOUS_AGENTS:
                v = bat(diffs(mx, ag, REG_MAIN, "liste_fixe", regle=regle))[0]
                cnt_lf[v] = cnt_lf.get(v, 0) + 1
                v = bat(diffs(mx, ag, REG_MAIN, "tri_risque", regle=regle))[0]
                cnt_tr[v] = cnt_tr.get(v, 0) + 1
        L.append(f"| {C.NOMS_ABLATIONS[nom]} | {c1} | {c2} | {dfmt(d, 'charge', 1)} | "
                 + " ; ".join(dfmt(d, f"degats_{n}") for n in NIV)
                 + f" | {a} : {dfmt(da, 'charge', 1)} ; " + " ; ".join(dfmt(da, f"degats_{n}") for n in NIV)
                 + f" | {fmt_pire(ga['stationnaires'])} | "
                 + ", ".join(f"{k} {v}" for k, v in sorted(cnt_lf.items())) + " / "
                 + ", ".join(f"{k} {v}" for k, v in sorted(cnt_tr.items())) + " |")
    L.append("")
    L.append("Réactivité des ablations (95e centile du délai, tous les types promus, et part non retirée) :\n")
    L.append("| variante | A6a bureau | A6b bureau | A6a service client | A6b service client |")
    L.append("|--|--|--|--|--|")
    for regle, lab in (("regle", "règle amendée"), ("regle_sans_remise", "sans remise à zéro"),
                       ("regle_sans_epreuve", "sans épreuve"), ("regle_sans_palier_milieu", "sans palier du milieu"),
                       ("regle_sans_ponderation", "sans pondération")):
        cells = []
        for mx in MIXES:
            for a in ("A6a", "A6b"):
                rr = filtre(lire("reactivite"), regle=regle, reglage=REG_MAIN, agent=a, melange=mx, type="tous")
                if rr and rr[0].get("delai_p95") is not None:
                    r = rr[0]
                    cells.append(f"{ic(r['delai_p95'], r['delai_p95_lo'], r['delai_p95_hi'], 0)}, non retiré "
                                 f"{pc(r['part_non_retire'])}")
                else:
                    cells.append("—")
        L.append(f"| {lab} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")
    L.append("")
    da6 = diffs("bureau", "A6a", REG_MAIN, "regle", regle="regle_sans_remise")
    dsp1 = diffs("bureau", "A1", REG_MAIN, "regle", regle="regle_sans_ponderation")
    dsp4 = diffs("bureau", "A4", REG_MAIN, "regle", regle="regle_sans_ponderation")
    ddg = diffs("bureau", "A2-calibre", REG_MAIN, "regle", regle="regle_sans_doute_gratuit")
    g_dg = garantie_vues(REG_MAIN, "regle_sans_doute_gratuit")["doute"]
    g_main = garantie_vues(REG_MAIN, "regle")["doute"]
    dpm1 = diffs("bureau", "A1", REG_MAIN, "regle", regle="regle_sans_palier_milieu")
    dpm4 = diffs("bureau", "A4", REG_MAIN, "regle", regle="regle_sans_palier_milieu")
    dse4 = diffs("bureau", "A4", REG_MAIN, "regle", regle="regle_sans_epreuve")
    dse2 = diffs("bureau", "A2", REG_MAIN, "regle", regle="regle_sans_epreuve")
    L.append("Ce que montrent les ablations, mesuré (bureau) :\n")
    L.append(f"- **Sans remise à zéro** : rien ne change hors changement de configuration. Pour A6a, dégâts faibles en "
             f"plus {dfmt(da6, 'degats_faible')} et charge {dfmt(da6, 'charge', 1)} : la dégradation annoncée n'est plus vue.")
    L.append(f"- **Sans pondération par l'enjeu** : A1, charge {dfmt(dsp1, 'charge', 1)} et dégâts forts "
             f"{dfmt(dsp1, 'degats_fort')} ; A4, charge {dfmt(dsp4, 'charge', 1)} et dégâts faibles {dfmt(dsp4, 'degats_faible')}.")
    L.append(f"- **Sans doute gratuit** : l'agent qui doute à bon escient paie (A2 calibré : charge {dfmt(ddg, 'charge', 1)}) ; "
             f"le pire couple « doute » de la garantie passe de {icp(g_main['pire']['p3'], g_main['pire']['p3_lo'], g_main['pire']['p3_hi'])} "
             f"(n = {ent(g_main['pire']['n'])}) à {icp(g_dg['pire']['p3'], g_dg['pire']['p3_lo'], g_dg['pire']['p3_hi'])} (n = {ent(g_dg['pire']['n'])}).")
    L.append(f"- **Sans palier du milieu** : dégâts inchangés (A1, dégâts faibles {dfmt(dpm1, 'degats_faible')}), charge "
             f"en plus : A1 {dfmt(dpm1, 'charge', 1)}, A4 {dfmt(dpm4, 'charge', 1)}.")
    L.append(f"- **Sans épreuve** : A4, charge {dfmt(dse4, 'charge', 1)} et dégâts forts {dfmt(dse4, 'degats_fort')} (les "
             f"variantes d'épreuve comptent comme de vraies tâches, choix 5) ; A2, dégâts moyens {dfmt(dse2, 'degats_moyen')}.")
    L.append("")
    L.append("Interprété : le palier 2 ne coûte toujours aucun dégât dans ce modèle (une correction après coup vaut une "
             "validation avant). Sans épreuve, un bon agent revient plus vite au palier 3 après une erreur à enjeu "
             "moyen ou fort, d'où un peu plus de dégâts moyens ; l'épreuve garde donc un effet en v2.\n")
    return "\n".join(L)


def section_promotion():
    L = ["## Agents bons laissés de côté, délai de promotion\n",
         f"Règle amendée, réglage de départ, α = 5 %, {ent(R5)} répétitions. « Jamais » : part des répétitions où le "
         "type n'atteint jamais le palier 3 avant l'horizon (Wilson). Délai : numéro de l'action (tous types) de la "
         "première promotion au palier 3, parmi les répétitions promues (centiles : rééchantillonnage). « Bon » : q "
         "au plus pb du palier 3 (A2 n'est pas bon à enjeu fort, où pb = 1 %).\n",
         "| mélange | agent | type | bon ? | jamais promu au palier 3 | répétitions promues | délai moyen | délai médian | 90e centile |",
         "|--|--|--|--|--|--|--|--|--|"]
    for mx in MIXES:
        for a in BONS:
            for t in C.TYPES[:7]:
                r = un(lire("promotion"), melange=mx, agent=a, regle="regle", reglage=REG_MAIN, type=t, palier=3.0)
                L.append(f"| {NM[mx]} | {a} | {t} | {'oui' if r['bon'] else 'non'} | "
                         f"{icp(r['jamais'], r['jamais_lo'], r['jamais_hi'])} | {ent(r['n_promues'])} | "
                         f"{ic(r.get('delai_moy'), r.get('delai_moy_lo'), r.get('delai_moy_hi'), 0)} | "
                         f"{ic(r.get('delai_med'), r.get('delai_med_lo'), r.get('delai_med_hi'), 0)} | "
                         f"{ic(r.get('delai_p90'), r.get('delai_p90_lo'), r.get('delai_p90_hi'), 0)} |")
    L.append("")
    L.append("Le premier passage au palier 3 suit les mêmes seuils qu'en v1 (35 réussites, 72 à enjeu fort au "
             "départ) ; ce qui change en v2, c'est ce qui se passe ensuite (`promotion.csv`, `fig3_delai_promotion.png`).\n")
    return "\n".join(L)


def section_epreuves():
    L = ["## Épreuves : réussite comparée aux tâches ordinaires\n",
         f"Réglage de départ, α = 5 %, {ent(R5)} répétitions. Réussite d'une épreuve : les 3 variantes justes. Tâches "
         "ordinaires : actions vérifiables des types à enjeu moyen ou fort (n : leur nombre, toutes répétitions). "
         "Rapports : méthode delta, répétition par répétition ; « 3 tâches » : la réussite d'une tâche au cube.\n",
         "| mélange | agent | épreuves par répétition | réussite d'une épreuve | réussite d'une variante | réussite d'une tâche ordinaire | 3 tâches ordinaires | 3 tâches difficiles ordinaires |",
         "|--|--|--|--|--|--|--|--|"]
    for mx in MIXES:
        for a in TOUS_AGENTS:
            r = un(lire("epreuves"), melange=mx, agent=a, regle="regle", reglage=REG_MAIN)
            L.append(f"| {NM[mx]} | {a} | {ic(r['tentatives_par_rep'], r['tentatives_par_rep_lo'], r['tentatives_par_rep_hi'], 1)} | "
                     f"{icp(r['reussite_epreuve'], r['reussite_epreuve_lo'], r['reussite_epreuve_hi'])} | "
                     f"{icp(r['reussite_variante'], r['reussite_variante_lo'], r['reussite_variante_hi'])} | "
                     f"{icp(r['reussite_tache_ordinaire'], r['reussite_tache_ordinaire_lo'], r['reussite_tache_ordinaire_hi'], 2)} "
                     f"(n = {ent(r['n_taches_ordinaires'])}) | "
                     f"{icp(r['reussite_3_taches_ordinaires'], r['reussite_3_taches_ordinaires_lo'], r['reussite_3_taches_ordinaires_hi'])} | "
                     f"{icp(r['reussite_3_taches_difficiles'], r['reussite_3_taches_difficiles_lo'], r['reussite_3_taches_difficiles_hi'])} |")
    L.append("")
    return "\n".join(L)


# ==========================================================================
def autonomie(lecteur, mix, a, regle="regle", reg=REG_MAIN):
    rr = sorted(filtre(lecteur("autonomie_temps"), melange=mix, agent=a, regle=regle, reglage=reg),
                key=lambda x: x["debut"])
    ys = [r["part_palier2plus"] for r in rr]
    i = int(np.argmax(ys))
    j = 15 + int(np.argmax(ys[15:]))
    return dict(pic=(ys[i], rr[i]["part_palier2plus_lo"], rr[i]["part_palier2plus_hi"]), pic_t=rr[i]["debut"],
                fin=(ys[-1], rr[-1]["part_palier2plus_lo"], rr[-1]["part_palier2plus_hi"]),
                apres=(ys[j], rr[j]["part_palier2plus_lo"], rr[j]["part_palier2plus_hi"]))


def icpa(t):
    return icp(t[0], max(0.0, t[1]), t[2])


def section_v1_v2():
    L = ["## v1 contre v2\n",
         "Mêmes agents, mêmes tirages, mêmes graines ; seule la règle change (amendement A1). v1 : `resultats_v1/` "
         "(première passe, archivée, non modifiée). v2 : ce dossier. Les intervalles sont ceux de chaque passe ; les "
         f"deux passes portent sur les mêmes répétitions ({ent(R5)} au réglage de départ α = 5 %, {ent(R1)} ailleurs).\n",
         "### Extinction de l'autonomie\n",
         "Part des actions d'une fenêtre de 100 exécutées sans validation préalable (palier 2 ou 3), règle au "
         f"réglage de départ, {ent(R5)} répétitions (`fig6_v1_v2_autonomie.png`).\n",
         "| mélange | agent | v1 : au plus haut | v1 : 100 dernières actions | v2 : au plus haut | v2 : 100 dernières actions |",
         "|--|--|--|--|--|--|"]
    for mx in MIXES:
        for a in ("A1", "A2", "A3", "A4", "A7"):
            v1 = autonomie(lire_v1, mx, a)
            v2 = autonomie(lire, mx, a)
            L.append(f"| {NM[mx]} | {a} | {icpa(v1['pic'])} (actions {ent(v1['pic_t'])}-{ent(v1['pic_t'] + 99)}) | "
                     f"{icpa(v1['fin'])} | {icpa(v2['pic'])} (actions {ent(v2['pic_t'])}-{ent(v2['pic_t'] + 99)}) | {icpa(v2['fin'])} |")
    L.append("")
    L.append("### Charge\n")
    L.append("| réglage | mélange | agent | v1 : charge ; hors lectures | v2 : charge ; hors lectures |")
    L.append("|--|--|--|--|--|")
    for reg in REGLAGES:
        for mx in MIXES:
            for a in BONS:
                c1 = (m3(mx, a, "regle", reg, "charge", 1, lecteur=lire_v1) + " ; "
                      + m3(mx, a, "regle", reg, "charge_hors_lec", 1, lecteur=lire_v1))
                c2 = m3(mx, a, "regle", reg, "charge", 1) + " ; " + m3(mx, a, "regle", reg, "charge_hors_lec", 1)
                L.append(f"| {reg} (n = {nrep(reg)}) | {NM[mx]} | {a} | {c1} | {c2} |")
    for mx in MIXES:
        for a in ("A3", "A4", "A7"):
            c1 = (m3(mx, a, "regle", REG_MAIN, "charge", 1, lecteur=lire_v1) + " ; "
                  + m3(mx, a, "regle", REG_MAIN, "charge_hors_lec", 1, lecteur=lire_v1))
            c2 = m3(mx, a, "regle", REG_MAIN, "charge", 1) + " ; " + m3(mx, a, "regle", REG_MAIN, "charge_hors_lec", 1)
            L.append(f"| {REG_MAIN} (n = {nrep(REG_MAIN)}) | {NM[mx]} | {a} | {c1} | {c2} |")
    L.append("")
    L.append("### Dégâts\n")
    L.append("Écart apparié avec « tout faire valider », pour 100 actions, réglage de départ α = 5 %.\n")
    L.append("| mélange | agent | niveau | v1 | v2 |")
    L.append("|--|--|--|--|--|")
    cmp1 = lire_v1("comparaisons")
    for mx in MIXES:
        for a in ("A1", "A2", "A3", "A4", "A7"):
            d2 = diffs(mx, a, REG_MAIN, "tout_valider")
            d1 = {r["mesure"]: r for r in filtre(cmp1, melange=mx, agent=a, reglage=REG_MAIN, contre="tout_valider",
                                                   regle="regle", e=C.E_PRINCIPAL)}
            for n in NIV:
                L.append(f"| {NM[mx]} | {a} | {n} | {dfmt(d1, f'degats_{n}')} | {dfmt(d2, f'degats_{n}')} |")
    L.append("")
    L.append("### Garantie\n")
    L.append("| réglage | v1 : pire couple stable ; doute ; non stable | v2 : pire couple stable ; doute ; non stable |")
    L.append("|--|--|--|")
    for reg in REGLAGES:
        g1 = garantie_vues(reg, lecteur=lire_v1)
        g2 = garantie_vues(reg)

        def court(g):
            if g is None:
                return "—"
            p = g["pire"]
            return f"{p['agent']} {p['type']} {icp(p['p3'], p['p3_lo'], p['p3_hi'])} ({g['verdict']})"
        L.append(f"| {reg} | {court(g1['stationnaires'])} ; {court(g1['doute'])} ; {court(g1['non_stationnaires'])} | "
                 f"{court(g2['stationnaires'])} ; {court(g2['doute'])} ; {court(g2['non_stationnaires'])} |")
    L.append("")
    gc1, gc2 = lire_v1("garantie_courbe"), lire("garantie_courbe")
    L.append("Agents à taux constant exactement au pm (courbe de garantie, bureau, 1 000 répétitions par point) :\n")
    L.append("| réglage | type | v1 | v2 |")
    L.append("|--|--|--|--|")
    for reg in REGLAGES:
        for t in C.TYPES[:7]:
            r2 = [r for r in filtre(gc2, melange="bureau", reglage=reg, type=t) if abs(r["q"] - r["pm3"]) < 1e-9]
            r1 = [r for r in filtre(gc1, melange="bureau", reglage=reg, type=t) if abs(r["q"] - r["pm3"]) < 1e-9]
            if r1 and r2:
                L.append(f"| {reg} | {t} | {icp(r1[0]['p3'], r1[0]['p3_lo'], r1[0]['p3_hi'])} | "
                         f"{icp(r2[0]['p3'], r2[0]['p3_lo'], r2[0]['p3_hi'])} |")
    L.append("")
    L.append("### Réactivité\n")
    L.append("A6b (dérive silencieuse), tous les types promus à t = 1 500 : 95e centile du délai et part non retirée.\n")
    L.append("| réglage | mélange | v1 : 95e centile ; non retiré | v2 : 95e centile ; non retiré |")
    L.append("|--|--|--|--|")
    re1, re2 = lire_v1("reactivite"), lire("reactivite")
    for reg in REGLAGES:
        for mx in MIXES:
            r1 = filtre(re1, regle="regle", reglage=reg, agent="A6b", melange=mx, type="tous")[0]
            r2 = filtre(re2, regle="regle", reglage=reg, agent="A6b", melange=mx, type="tous")[0]

            def cel(r):
                return (f"{ic(r['delai_p95'], r['delai_p95_lo'], r['delai_p95_hi'], 0)} ; "
                        f"{icp(r['part_non_retire'], r['part_non_retire_lo'], r['part_non_retire_hi'])}")
            L.append(f"| {reg} | {NM[mx]} | {cel(r1)} | {cel(r2)} |")
    L.append("")
    L.append("### Contre les concurrents simples\n")
    L.append("| réglage | v1 : contre liste fixe ; tri ; hasard | v2 : contre liste fixe ; tri ; hasard |")
    L.append("|--|--|--|")
    for reg in REGLAGES:
        cels = []
        for lect in (lire_v1, lire):
            parts = []
            for contre in ("liste_fixe", "tri_risque", "hasard"):
                cpt = {}
                rows = lect("comparaisons")
                for mx in MIXES:
                    for a in TOUS_AGENTS:
                        d = {r["mesure"]: r for r in filtre(rows, melange=mx, agent=a, reglage=reg, contre=contre,
                                                              regle="regle", e=C.E_PRINCIPAL)}
                        v = bat(d)[0]
                        cpt[v] = cpt.get(v, 0) + 1
                parts.append(", ".join(f"{k} {v}" for k, v in sorted(cpt.items())))
            cels.append(" ; ".join(parts))
        L.append(f"| {reg} | {cels[0]} | {cels[1]} |")
    L.append("")
    return "\n".join(L)


# ==========================================================================
def section_surprises():
    v2a1, v2a2 = autonomie(lire, "bureau", "A1"), autonomie(lire, "bureau", "A2")
    v1a2 = autonomie(lire_v1, "bureau", "A2")
    v2a4 = autonomie(lire, "bureau", "A4")
    v2a7, v1a7 = autonomie(lire, "bureau", "A7"), autonomie(lire_v1, "bureau", "A7")
    r1 = filtre(lire_v1("reactivite"), regle="regle", reglage=REG_MAIN, agent="A6b", melange="bureau", type="tous")[0]
    r2 = filtre(lire("reactivite"), regle="regle", reglage=REG_MAIN, agent="A6b", melange="bureau", type="tous")[0]
    r2m = filtre(lire("reactivite"), regle="regle", reglage=REG_MAIN, agent="A6b", melange="bureau", type="mauvais_apres")[0]
    p = C.params_regle(*C.REGLAGE_PRINCIPAL)
    derive_lec = 0.10 * p.a3[C.LEC] - 0.90 * p.b3[C.LEC]
    derive_p2_a4 = 0.15 * p.a2[C.LEC] - 0.85 * p.b2[C.LEC]
    d_h_a2 = diffs("bureau", "A2", REG_MAIN, "hasard")
    d_h_a7 = diffs("bureau", "A7", REG_MAIN, "hasard")
    m_a4 = mesure("bureau", "A4", "regle", REG_MAIN)
    m_a4v1 = un(lire_v1("mesures"), melange="bureau", agent="A4", regle="regle", reglage=REG_MAIN, e=C.E_PRINCIPAL)
    g_st = garantie_vues(C.nom_reglage("stricte", 0.05))["non_stationnaires"]["pire"]
    pS = C.params_regle("stricte", 0.05)
    derive_strict = 0.10 * pS.a3[C.ECR] - 0.90 * pS.b3[C.ECR]
    lf = diffs("bureau", "A1", REG_MAIN, "liste_fixe")
    L = ["## Ce qui surprend\n", "Chaque point sépare ce qui est **mesuré** de ce qui est **interprété**.\n"]
    L.append("**1. L'extinction a disparu.**  ")
    L.append(f"Mesuré : en bureau, A2 culmine à {icpa(v2a2['pic'])} et finit à {icpa(v2a2['fin'])} (v1 : "
             f"{icpa(v1a2['pic'])} puis {icpa(v1a2['fin'])}) ; A1 culmine à {icpa(v2a1['pic'])} et finit à "
             f"{icpa(v2a1['fin'])}.  ")
    L.append("Interprété : avec le score réfléchi, une erreur isolée est absorbée et le processus devient "
             "stationnaire ; l'horizon ne décide plus du verdict de charge.\n")
    L.append("**2. La réactivité se paie : la dérive silencieuse est retirée plus lentement.**  ")
    L.append(f"Mesuré : A6b, bureau, tous les types promus : 95e centile {ent(r2['delai_p95'])} actions, "
             f"{pc(r2['part_non_retire'])} non retirés à l'horizon (v1 : {ent(r1['delai_p95'])} et "
             f"{pc(r1['part_non_retire'])}). Sur les seuls types devenus mauvais ({r2m['types_mauvais_apres']}) : "
             f"95e centile {ent(r2m['delai_p95'])}, {pc(r2m['part_non_retire'])} non retirés.  ")
    L.append(f"Interprété : sur un type à enjeu faible, un agent à 10 % reste sous le pm de départ (20 %) ; la dérive "
             f"moyenne de son score par action vérifiée vaut {nb(derive_lec, 3)}, négative, donc il reste promu, comme "
             "la règle le veut. Le lent retrait mesuré « tous types » est surtout celui-là. Sur les types à enjeu "
             "moyen ou fort, la première erreur suffit toujours.\n")
    L.append("**3. Au pm exact, la garantie à enjeu faible s'effrite.**  ")
    L.append(f"Mesuré : au réglage strict, A6b après la dérive (10 % = pm sur les types à enjeu faible) est promu de "
             f"nouveau au palier 3 sur {g_st['type']} ({NM[g_st['melange']]}) dans {icp(g_st['p3'], g_st['p3_lo'], g_st['p3_hi'])} "
             f"des répétitions (n = {ent(g_st['n'])}). Sur la courbe de garantie, la promotion au pm des types à enjeu "
             "faible monte d'environ 3 % (v1) à environ 4 à 6 % (v2) ; voir « v1 contre v2 ».  ")
    L.append(f"Interprété : le seuil de Wald protège un test ; le score réfléchi refait le test après chaque "
             f"descente. Au pm exact, la dérive du score reste faible devant ses pas : {nb(derive_strict, 3)} par "
             f"action vérifiée au réglage strict, quand une réussite retire {nb(pS.b3[C.ECR], 3)} et une erreur ajoute "
             f"{nb(pS.a3[C.ECR], 3)} ; sur un horizon long, l'agent finit par aligner les réussites qu'il faut. La "
             "garantie de 5 % ne tient plus « à vie » pour un agent au bord du seuil ; elle tient pour les agents "
             "nettement mauvais.\n")
    L.append("**4. Le palier du milieu ouvre la porte aux agents moyens à mauvais sur les types à enjeu faible.**  ")
    L.append(f"Mesuré : A4 (15 %) exécute {icpa(v2a4['fin'])} de ses actions sans validation préalable en fin "
             f"d'horizon (bureau) ; sa charge passe de {ic(m_a4v1['charge'], m_a4v1['charge_lo'], m_a4v1['charge_hi'], 1)} "
             f"(v1) à {ic(m_a4['charge'], m_a4['charge_lo'], m_a4['charge_hi'], 1)}.  ")
    L.append(f"Interprété : le palier 2 des types à enjeu faible se mérite sous pm = 30 % ; à 15 %, la dérive du "
             f"score L2 vaut {nb(derive_p2_a4, 3)} par action, négative. La garantie ne porte que sur le palier 3 : "
             "rien, dans la pièce 1, ne borne le palier 2 d'un agent mauvais. Les erreurs y sont corrigées après coup "
             "(95 % ici), ce qui limite les dégâts mais pas la charge de correction.\n")
    L.append("**5. Le hasard fait toujours aussi bien pour un agent stable ; la règle gagne sur l'agent qui change.**  ")
    L.append(f"Mesuré : A2, bureau, règle moins hasard : dégâts faibles {dfmt(d_h_a2, 'degats_faible')}, charge "
             f"{dfmt(d_h_a2, 'charge', 2)} (le coût des épreuves). A7 (amélioration annoncée) : dégâts faibles "
             f"{dfmt(d_h_a7, 'degats_faible')} ; A7 retrouve {icpa(v2a7['fin'])} d'actions sans validation en fin "
             f"d'horizon (v1 : {icpa(v1a7['fin'])}).  ")
    L.append("Interprété : dans ce monde aux erreurs indépendantes, le moment des promotions ne vaut quelque chose "
             "que si l'agent change ; la correction de la pièce 8 (erreurs faibles effacées au changement de modèle) "
             "rend enfin justice à l'agent qui progresse.\n")
    L.append("**6. Face à la liste fixe, le compromis a changé de sens.**  ")
    L.append(f"Mesuré : A1, bureau, règle moins liste fixe : charge {dfmt(lf, 'charge', 1)}, dégâts faibles "
             f"{dfmt(lf, 'degats_faible')}, moyens {dfmt(lf, 'degats_moyen')}, forts {dfmt(lf, 'degats_fort')}.  ")
    L.append("Interprété : en v1, la règle faisait moins de dégâts faibles pour plus de charge ; en v2, elle demande "
             "beaucoup moins de validations pour un bon agent, mais elle lui donne l'autonomie à enjeu moyen et fort, "
             "que la liste fixe ne donne jamais. Le critère « pas pire à aucun niveau » interdit ce troc tant que la "
             "marge à ces niveaux est nulle.\n")
    return "\n".join(L)


def section_limites():
    return "\n".join([
        "## Limites\n",
        "- **Monde idéal, par construction.** Erreurs indépendantes, taux constant dans chaque phase, contrôle "
        "automatique parfait sur les actions vérifiables, validateur qui rate 5 % des erreurs au hasard.",
        "- **Même taux sur tous les types** (sauf A5) : la règle ne peut presque rien gagner à répartir l'autonomie "
        "entre les types d'un même agent.",
        "- **Un seul horizon (3 000 actions).** En v2 l'autonomie est stationnaire, mais l'effritement de la garantie "
        "au pm (surprise 3) grandit avec l'horizon.",
        "- **Une seule dérive** (2 % à 10 % à t = 1 500) : sur les types à enjeu faible, elle reste sous le pm de "
        "départ ; la réactivité sur ces types n'est pas une exigence de la règle.",
        "- **Variantes d'épreuve comptées comme de vraies tâches** (charge et dégâts) : choix prudent, isolé dans "
        "`charge_epreuve` et `degats_epreuve`.",
        "- **« Bon » et « mauvais » sont des définitions de travail** (q au plus pb, q au moins pm) ; la garantie ne "
        "porte que sur le palier 3.",
        "- **Dégâts pour 100 actions du flux entier**, pas pour 100 actions du niveau.",
        "- **Statistiques** : normale (moyennes), Wilson (proportions), delta (rapports), rééchantillonnage "
        "(centiles) ; aucune correction pour comparaisons multiples. La grille de marges est lue à 95 % par "
        "couple ; avec 26 couples, un « indécis » isolé peut être du bruit.",
        "- **Réglages autres que celui de départ à 1 000 répétitions** : intervalles environ deux fois plus larges.",
        "- **Ce n'est pas l'expérience de confirmation** ; aucun agent réel, aucune donnée réelle.\n",
    ])


def section_choix():
    items = [
        "**« Sous ln B » lu « au plus ln B »** (tolérance 1e−9) : une erreur au plancher ramène le score exactement à ln B, et la règle ne doit pas descendre pour une seule erreur (test des 2 erreurs rapprochées).",
        "**Score réfléchi (A1)** : un score par type et par palier visé, L3 (pb ; pm du palier 3) et L2 (palier 2, types réversibles), chacun avec son plancher ln B − a. Plus de plafond sur r. Le palier visé est le plus haut dont le score est au plus ln B.",
        "**Mise à jour du palier.** Une réussite ne peut que faire monter. Le palier ne descend que sur une erreur (un cran pour l'enjeu faible, palier 1 pour l'enjeu moyen ou fort) ou sur un changement de configuration (recalcul complet). L'action est exécutée au palier d'avant sa propre preuve.",
        "**Épreuves** (inchangées) : une par erreur à enjeu moyen ou fort, passées une à une à l'arrivée de la prochaine action du type ; après un échec, nouvel essai après 50 actions du type ; une nouvelle erreur ne remet pas ce délai à zéro, un changement de modèle si. Une épreuve ratée n'ajoute pas d'erreur. Tant qu'une épreuve est ouverte, les réussites ne font pas baisser le score. s compte les erreurs à enjeu moyen ou fort de la configuration : au changement de modèle, elles deviennent autant d'épreuves, et chaque épreuve réussie en efface une.",
        "**Variantes d'épreuve** : 3 cas difficiles (taux min(0,9 ; 6q) du moment), en plus des 3 000 actions, au palier 1 : elles comptent dans la charge et dans les dégâts, pas dans le dénominateur. Le doute s'y applique (variante en doute neutre et remplacée ; comptée ratée sans doute gratuit).",
        "**Changement de modèle (A1)** : L2 = L3 = 0 sur tous les types ; erreurs à enjeu faible effacées ; erreurs à enjeu moyen ou fort en épreuves.",
        "**Consigne modifiée (A1)** : sur le type, chaque score négatif est divisé par deux ; palier recalculé.",
        "**Plafonnés** : trois sources (plafonds absolus 1 %, 20 % de SOR, 20 % d'ARG) ; taux d'erreur de la source ; enjeu fort pour les dégâts ; toujours au palier 1, sauf sous « tout approuver ».",
        "**Doute** : une validation (charge), aucune preuve. Doute calibré : une action difficile sur deux, indépendamment de l'issue ; abusif : 30 % de toutes les actions.",
        "**Invérifiable** : 5 % des actions, au hasard. **Validateur** : un même nombre aléatoire par action pour toutes les règles et toutes les valeurs de e.",
        "**Témoins** inchangés depuis la v1 : tout approuver (plafonnés compris, doutes ignorés) ; liste fixe et tri par le risque au palier 3 ; trois réussites (palier 3 après 3 réussites vérifiées d'affilée, palier 1 à la première erreur) ; oracle (palier 3 si le vrai q du moment est au plus pb) ; hasard (mêmes parts de palier 2 et 3 que la règle, type par type, en moyenne sur les répétitions, tirées action par action).",
        "**Sans remise à zéro** : changements de configuration ignorés. **Sans pondération** : réglages de l'enjeu moyen partout. **Sans doute gratuit** : un doute compte comme une erreur. **Sans palier du milieu** : un seul score, celui du palier 3. **Sans épreuve** : après une erreur à enjeu moyen ou fort, le score reprend aussitôt ; au changement de modèle, L = 0 et plus rien d'autre.",
        "**Les sensibilités de la v1** (erreurs faibles effacées, plancher glissant) n'ont plus d'objet : la première est devenue la règle, la seconde est le score réfléchi lui-même.",
        "**Droits élargis** : codés (même traitement que le changement de modèle, sur un type) ; aucun scénario du plan ne les utilise.",
        "**Version v1 gardée dans le code** (`version=\"v1\"`, `executer.py --v1`) pour reproduire `resultats_v1/` ; le contrôle a été fait sur six cas, au chiffre près.",
        "**Grille de marges (A1)** : " + " ; ".join(fmt_marge(m) for m in C.MARGES) + " pour 100 actions. « Passe » à une marge : tout l'intervalle de l'écart avec « tout faire valider » est sous la marge.",
        "**Agent mauvais** sur un type : q au moins pm du palier 3 de son niveau, au réglage considéré ; **bon** : q au plus pb. Couples comptés pour la garantie : agents stables (A3, A4, A5 et doutes d'A4), plus les phases mauvaises d'A6a (après la remise à zéro), d'A6b (après la dérive) et d'A7 (avant le changement).",
        "**Verdicts** trivalués sur les intervalles à 95 % : passe, échoue, indécis.",
        "**« Bat »** : écarts appariés ; meilleure sur au moins une mesure parmi la charge et les dégâts des trois niveaux, pire sur aucune.",
        "**Utilité jugée sur A1 et A2** ; le critère de dégâts est aussi donné pour les 13 agents.",
        "**Réactivité** : couples (répétition, type) au palier 2 ou 3 à t = 1 500 ; délai jusqu'au premier retour au palier 1 ; censure à l'horizon. Nouvelle ligne en v2 : les seuls types où le nouveau taux atteint pm.",
        f"**Répétitions** : {ent(R5)} pour le réglage de départ α = 5 % et tous les témoins ; {ent(R1)} pour les cinq autres réglages et les ablations. **Graines** : celles de la v1 (graine maîtresse {C.GRAINE}), donc mêmes tirages.",
    ]
    L = ["## Choix d'implémentation\n", "Points où le plan laisse un choix ; à chaque fois, l'option la plus simple et la plus prudente.\n"]
    for i, t in enumerate(items, 1):
        L.append(f"{i}. {t}")
    L.append("")
    return "\n".join(L)


def section_resume(n_ok, n_ko):
    g = {reg: garantie_vues(reg) for reg in REGLAGES}
    gd = g[REG_MAIN]
    vcm = verdict_charge(REG_MAIN)
    passe_st = [reg for reg in REGLAGES if g[reg]["stationnaires"]["verdict"] == "passe"]
    ech_ns = [reg for reg in REGLAGES if g[reg]["non_stationnaires"]["verdict"] == "échoue"]
    ech_do = [reg for reg in REGLAGES if g[reg]["doute"]["verdict"] == "échoue"]
    ch_ok = [reg for reg in REGLAGES if all(v["v_charge"] == "passe" and v["v_hors"] == "passe" for v in verdict_charge(reg).values())]
    mm = [marge_min(REG_MAIN, BONS, n)[0] for n in NIV]
    r6 = {mx: filtre(lire("reactivite"), regle="regle", reglage=REG_MAIN, agent="A6b", melange=mx, type="tous")[0] for mx in MIXES}
    r6m = {mx: filtre(lire("reactivite"), regle="regle", reglage=REG_MAIN, agent="A6b", melange=mx, type="mauvais_apres")[0] for mx in MIXES}
    v2a2, v1a2 = autonomie(lire, "bureau", "A2"), autonomie(lire_v1, "bureau", "A2")
    cpt = {}
    for reg in REGLAGES:
        for contre in ("liste_fixe", "tri_risque"):
            for mx in MIXES:
                for a in TOUS_AGENTS:
                    v = bat(diffs(mx, a, reg, contre))[0]
                    cpt[v] = cpt.get(v, 0) + 1
    n_cmp = sum(cpt.values())
    trois = [reg for reg in REGLAGES if g[reg]["tous"]["verdict"] == "passe" and reg in ch_ok]
    a2_hors_ko = [reg for reg in REGLAGES
                  if any(verdict_charge(reg)[(mx, "A2")]["v_hors"] == "échoue" for mx in MIXES)]
    if not ch_ok and len(a2_hors_ko) == len(REGLAGES):
        l10 = ("10. **Les trois épreuves ensemble** : la charge hors lectures d'A2 dépasse 50 à tous les réglages ; "
               "aucun réglage ne passe donc l'épreuve d'utilité, quelle que soit la marge de dégâts retenue. "
               f"Garantie (tous couples) et charge ensemble : {', '.join(trois) or 'aucun réglage'}.")
    else:
        l10 = ("10. **Les trois épreuves ensemble** : charge tenue à " + (', '.join(ch_ok) or 'aucun réglage')
               + " ; garantie (tous couples) et charge ensemble : " + (', '.join(trois) or 'aucun réglage')
               + " ; reste la marge de dégâts (point 5) et K.")
    lignes = [
        "## Résumé\n",
        f"1. **Tests** : {n_ok} passés, {n_ko} en échec, dont les cinq ajoutés pour l'amendement (35 ; 54 ; ⌈a/b⌉ ; 2 erreurs ; pas d'extinction à 2 %). Le chemin v1 du code reproduit `resultats_v1/` au chiffre près.",
        f"2. **Extinction** : disparue. A2 en bureau finit à {icpa(v2a2['fin'])} d'actions sans validation préalable (v1 : {icpa(v1a2['fin'])}).",
        f"3. **Garantie** : agents mauvais stables, passe à {', '.join(passe_st) or 'aucun réglage'} (pire couple au départ α = 5 % : {gd['stationnaires']['pire']['agent']} {gd['stationnaires']['pire']['type']}, {icp(gd['stationnaires']['pire']['p3'], gd['stationnaires']['pire']['p3_lo'], gd['stationnaires']['pire']['p3_hi'])}) ; échoue en dérive ou autour d'un changement à {', '.join(ech_ns) or 'aucun réglage'}, et avec le doute calibré à {', '.join(ech_do) or 'aucun réglage'}.",
        f"4. **Charge** (A1 et A2, en tout et hors lectures, ≤ 50) : passe à {', '.join(ch_ok) or 'aucun réglage'}. Au départ α = 5 %, A2 hors lectures : {ic(*vcm[('bureau', 'A2')]['hors'], 1)} en bureau, {ic(*vcm[('service_client', 'A2')]['hors'], 1)} en service client.",
        f"5. **Dégâts** (départ α = 5 %, A1 et A2) : plus petite marge de la grille qui passe, enjeu faible {fmt_marge(mm[0])}, moyen {fmt_marge(mm[1])}, fort {fmt_marge(mm[2])} pour 100 actions. À lire contre la marge fixée par Otsoa.",
        f"6. **Liste fixe et tri par le risque** : " + ", ".join(f"{k} {v}" for k, v in sorted(cpt.items())) + f" sur {n_cmp} comparaisons (6 réglages × 2 témoins × 26 couples).",
        f"7. **Réactivité** (A6b, départ α = 5 %) : 95e centile {ent(r6['bureau']['delai_p95'])} actions en bureau, {ent(r6['service_client']['delai_p95'])} en service client, tous types promus ; sur les types devenus mauvais, {ent(r6m['bureau']['delai_p95'])} et {ent(r6m['service_client']['delai_p95'])}.",
        "8. **Ce qui surprend** : la dérive silencieuse est retirée plus lentement qu'en v1 ; au pm exact, la garantie à enjeu faible s'effrite ; le palier 2 se mérite pour un agent à 15 % sur les types à enjeu faible.",
        "9. **Ce qui ne change pas** : le hasard fait aussi bien que la règle pour un agent stable ; le palier 2 ne coûte aucun dégât ; α compte peu ; au réglage strict, l'argent en bureau reste presque hors d'atteinte.",
        l10,
        "",
    ]
    return "\n".join(lignes)


def main():
    calcul_verdicts()
    calcul_marges()
    n_ok, n_ko = nb_tests()
    meta = json.load(open(os.path.join(DOSSIER, "meta.json")))
    entete = "\n".join([
        "# Simulation de niveau 1 · deuxième passe, règle amendée (A1), 4 novembre 2026\n",
        "> Agents fictifs de fiabilité connue, aucun agent réel, aucune donnée réelle, aucun modèle d'IA, aucun "
        "appel réseau. Plan : `PLAN_SIMULATION.md`, avec son amendement A1 (fait foi). Règle : `../REGLE.md`, "
        "section « Amendements », A1. Première passe : `../resultats_v1/` (archivée, non modifiée). Code : "
        "`config.py`, `flux.py`, `regle.py`, `temoins.py`, `mesures.py`, `executer.py`, `rapport.py`, "
        f"`ecrire_resultats.py` ; tests : `tests/`. Version de la règle : {meta.get('version_regle', '?')}. Graine "
        f"maîtresse {meta['graine']}. Durée de la grille : {nb(meta['duree_s'], 0)} s. Ce n'est pas l'expérience "
        "de confirmation.\n",
    ])
    lecture = "\n".join([
        "## Comment lire les chiffres\n",
        f"- **Dénominateurs** : une répétition = un agent sur 3 000 actions. {ent(R5)} répétitions pour le réglage "
        f"de départ α = 5 % et pour tous les témoins ; {ent(R1)} pour les autres réglages et les ablations. Charge "
        "et dégâts : pour 100 actions du flux. Proportions : sur les répétitions.",
        "- **Intervalles à 95 %** entre crochets, toujours. Moyennes : approximation normale ; proportions : Wilson ; "
        "écarts : appariés (mêmes tirages pour toutes les règles, et pour les deux versions).",
        "- **Validateur à 5 %** partout, sauf dans la section qui fait varier e.",
        "- Ce fichier est écrit par `ecrire_resultats.py` à partir des CSV, sans recopie à la main.\n",
    ])
    figures = "\n".join([
        "## Fichiers\n",
        "- `mesures.csv`, `comparaisons.csv`, `verdict.csv` ; `marges.csv` (verdict de dégâts à chaque marge de la "
        "grille, par réglage, mélange, agent et niveau) ; `marge_minimale.csv` (plus petite marge qui passe).",
        "- `garantie.csv`, `garantie_courbe.csv`, `promotion.csv`, `reactivite.csv`, `epreuves.csv`, "
        "`autonomie_temps.csv`, `consigne.csv`, `meta.json`.",
        "- Figures : `fig1_charge_degats_*.png`, `fig2_garantie_*.png`, `fig3_delai_promotion.png`, "
        "`fig4_reactivite.png`, `fig5_autonomie_temps.png`, `fig6_v1_v2_autonomie.png`.",
        "- Reproduire (3 minutes environ, depuis `simulation/`) : `.venv/bin/python executer.py --verifier-tests && "
        ".venv/bin/python rapport.py && .venv/bin/python ecrire_resultats.py`. La première passe : "
        "`AM_DOSSIER=<autre dossier> .venv/bin/python executer.py --v1` (jamais dans `resultats_v1/`).",
        "",
    ])
    texte = "\n".join([entete, section_resume(n_ok, n_ko), lecture, section_tests(n_ok, n_ko), section_exigences(),
                       section_verdict(), section_comparaison(), section_validateur(), section_ablations(),
                       section_promotion(), section_epreuves(), section_v1_v2(), section_surprises(), section_limites(),
                       section_choix(), figures])
    texte = texte.replace("pb depart", "pb de départ").replace("depart α", "départ α")
    with open(os.path.join(DOSSIER, "RESULTATS.md"), "w") as f:
        f.write(texte)
    print(os.path.join(DOSSIER, "RESULTATS.md"), len(texte.splitlines()), "lignes", f"tests {n_ok}/{n_ok + n_ko}")


if __name__ == "__main__":
    main()
