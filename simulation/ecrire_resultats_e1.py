"""Écrit resultats_e1/RESULTATS_E1.md (et choix.csv, figures) à partir des CSV d'executer_e1.py.

La règle de choix de la section 4 du plan est appliquée mécaniquement (fonction `choisir`), ainsi que
l'alerte 4.5 ; la prédiction datée de la section 0 est confrontée aux résultats.
Usage : .venv/bin/python ecrire_resultats_e1.py   (AM_DOSSIER_E1 comme pour executer_e1.py)
"""
import csv
import json
import math
import os
import time
from collections import defaultdict

import numpy as np

import config as C
import config_e1 as E
import rapport as RP  # format français et palette des figures (aucun accès à resultats/)

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.environ.get("AM_DOSSIER_E1", os.path.join(ICI, "resultats_e1"))
if os.path.realpath(DOSSIER) in {os.path.realpath(os.path.join(ICI, d)) for d in ("resultats", "resultats_v1")}:
    raise SystemExit("AM_DOSSIER_E1 ne peut pas être resultats/ ni resultats_v1/")
REGLES = E.NOMS_REGLES
FAM_B = [r for r in REGLES if E.FAMILLE[r] == "B"]
A_BARRE = ["A½", "A¼"]
SEUIL_EGALITE = 1.0       # section 4.3 : moins d'un point de charge hors lectures pour 100 actions
NIV = E.NIVEAUX
MERITES = [C.TYPES[k] for k in range(C.N_MERITES) if k != C.LEC]
HAUTS = ["DUR", "EXE", "SOR", "ARG"]
FORTS = ["SOR", "ARG"]
nb, pc = RP.nb, RP.pc


def lire(nom):
    p = os.path.join(DOSSIER, nom + ".csv")
    if not os.path.exists(p):
        return []
    return RP.lire(nom, DOSSIER)


def hi_final(l):
    return l["exces_hi_relance"] if l.get("exces_hi_relance") is not None else l["exces_hi"]


def vfinal(l):
    return l.get("verdict_final") or l["verdict"]


LECTURES = {
    "amendee": "amendement E1-a : budget sur tout l'horizon, fenêtre après le changement jugée à l'horizon long "
               "seulement, au plus une erreur constatée avant le retrait (décision 5)",
    "ancienne": "lecture d'avant l'amendement E1-a : fenêtre après le changement éliminatoire aux deux horizons, "
                "sans le critère de la décision 5",
}


def eliminatoire(l, lecture):
    """Une cellule du budget compte-t-elle dans le critère éliminatoire ?"""
    if lecture == "ancienne":
        return True
    return l["fenetre"] == "tout" or l["horizon"] == "long"


# --------------------------------------------------------------------------
# Section 4 : règle de choix
# --------------------------------------------------------------------------
def cellules_choix(budget, regle, lecture="amendee", mode="base"):
    return [l for l in budget if l["regle"] == regle and l["mode"] == mode and l["epreuves"] == "à blanc"
            and eliminatoire(l, lecture)]


def echecs_derive(derive, regle, mode="base"):
    """Amendement E1-a, point 1 : épisodes de dérive (enjeu moyen ou fort) où plus d'une erreur constatée passe."""
    return [l for l in derive if l["regle"] == regle and l["mode"] == mode and l["critere"]
            and l["verdict"] == "échoue"]


def charge_classement(charges, regle, horizon="court"):
    xs = [l["charge_hors_lec"] for l in charges if l["regle"] == regle and l["horizon"] == horizon and l["delegable"]]
    return (float(np.mean(xs)), len(xs)) if xs else (float("nan"), 0)


def choisir(budget, charges, derive, lecture="amendee", horizon_classement="court"):
    etat = {}
    for r in REGLES:
        cel = cellules_choix(budget, r, lecture)
        echecs = [l for l in cel if vfinal(l) != "passe"]
        ech_d = echecs_derive(derive, r) if lecture == "amendee" else []
        pire = max(cel, key=lambda l: hi_final(l) / l["budget"]) if cel else None
        ch, n = charge_classement(charges, r, horizon_classement)
        etat[r] = dict(n_cellules=len(cel), echecs=echecs, echecs_derive=ech_d, tient=bool(cel) and not echecs and not ech_d,
                       pire=pire, marge=(1 - hi_final(pire) / pire["budget"]) if pire else float("nan"), charge=ch,
                       n_couples=n, relancees=sum(1 for l in cel if l.get("relance")),
                       n_episodes=sum(1 for l in derive if l["regle"] == r and l["mode"] == "base" and l["critere"]))
    survivantes = [r for r in REGLES if etat[r]["tient"]]
    out = dict(etat=etat, survivantes=survivantes, retenue=None, egalite=[], motif="", lecture=lecture)
    if not survivantes:
        out["motif"] = "aucune règle ne tient le budget dans tous les cas simulés (section 4.4) : Otsoa décide"
        return out
    meilleure = min(survivantes, key=lambda r: etat[r]["charge"])
    groupe = [r for r in survivantes if etat[r]["charge"] - etat[meilleure]["charge"] < SEUIL_EGALITE]
    out["egalite"] = groupe
    if len(groupe) == 1:
        out["retenue"] = meilleure
        out["motif"] = "charge hors lectures la plus basse parmi les règles qui tiennent le budget"
        return out
    marges = {r: round(etat[r]["marge"], 3) for r in groupe}
    mmax = max(marges.values())
    prudentes = [r for r in groupe if marges[r] == mmax]
    if len(prudentes) == 1:
        out["retenue"] = prudentes[0]
        out["motif"] = (f"égalité de charge (moins de {nb(SEUIL_EGALITE, 0)} point) entre {', '.join(groupe)} ; "
                        "départage par la prudence (plus grande marge au budget dans la pire cellule)")
    else:
        out["retenue"] = min(prudentes, key=E.ORDRE_SIMPLICITE.index)
        out["motif"] = "égalité de charge et de prudence ; départage par la simplicité (ordre fixé avant le lancement)"
    return out


def alerte_resistance(budget, derive, choix):
    """Section 4.5 : la règle retenue tient-elle nettement moins bien les tests de résistance qu'une autre
    règle restée en lice ? Critère fixé avant le lancement, appliqué aux cellules éliminatoires de
    l'amendement E1-a : dans un mode de résistance, plus d'échecs qu'une autre survivante (cellules hors
    budget et épisodes de dérive à plus d'une erreur constatée), ou une pire cellule au moins 1,25 fois plus
    haute (et au moins à la moitié du budget)."""
    r0 = choix["retenue"]
    if r0 is None:
        return []
    alertes = []
    for mode in E.MODES[1:]:
        st = {}
        for r in choix["survivantes"]:
            cel = cellules_choix(budget, r, "amendee", mode)
            if not cel:
                continue
            n = sum(1 for l in cel if l["verdict"] != "passe") + len(echecs_derive(derive, r, mode))
            st[r] = (n, max(l["exces_hi"] / l["budget"] for l in cel))
        if r0 not in st:
            continue
        for r, (n, w) in st.items():
            if r == r0:
                continue
            n0, w0 = st[r0]
            if n0 > n or (w0 >= 0.5 and w0 >= 1.25 * w):
                alertes.append(dict(mode=mode, autre=r, hors_budget_retenue=n0, hors_budget_autre=n,
                                    pire_retenue=w0, pire_autre=w))
    return alertes


# --------------------------------------------------------------------------
# Tableaux
# --------------------------------------------------------------------------
def table(entete, lignes):
    s = "| " + " | ".join(entete) + " |\n|" + "--|" * len(entete) + "\n"
    for l in lignes:
        s += "| " + " | ".join(str(x) for x in l) + " |\n"
    return s


def nom_cellule(l):
    m = "bureau" if l["melange"] == "bureau" else "service client"
    f = "" if l["fenetre"] == "tout" else ", après le changement"
    return f"{l['agent']}, {m}, {l['horizon']}, {l['niveau']}{f}"


def ratio_txt(l):
    return f"{nb(hi_final(l) / l['budget'], 2)} × budget (borne haute ; moyenne {nb(l['exces'] / l['budget'], 2)})"


def section_choix(budget, charges, choix, choix_ancien, alertes, choix_long):
    s = "## En tête : la règle retenue (section 4, appliquée mécaniquement)\n\n"
    s += f"Lecture : {LECTURES['amendee']}.\n\n"
    r0 = choix["retenue"]
    s += f"**Règle retenue : {r0 if r0 else 'aucune'}.** {choix['motif'].capitalize()}.\n\n"
    rows = []
    for r in REGLES:
        st = choix["etat"][r]
        p = st["pire"]
        tient = "oui" if st["tient"] else "non (" + ", ".join(
            x for x in (f"{len(st['echecs'])} cellule(s) de budget" if st["echecs"] else "",
                        f"{len(st['echecs_derive'])} épisode(s) de dérive" if st["echecs_derive"] else "") if x) + ")"
        rows.append([r, tient, nb(st["charge"], 1), st["n_couples"], nb(st["marge"], 3) if p else "—",
                     nom_cellule(p) if p else "—", st["relancees"]])
    s += table(["règle", "tient le budget et la décision 5", "charge hors lectures (court, couples délégables)",
                "couples", "marge de la pire cellule", "pire cellule", "cellules relancées"], rows) + "\n"
    for r in REGLES:
        st = choix["etat"][r]
        if st["echecs"]:
            ex = sorted(st["echecs"], key=lambda l: -hi_final(l) / l["budget"])[:4]
            s += f"- {r} échoue au budget, par exemple : " + " ; ".join(
                f"{nom_cellule(l)} ({ratio_txt(l)}, {vfinal(l)})" for l in ex) + ".\n"
        if st["echecs_derive"]:
            ex = sorted(st["echecs_derive"], key=lambda l: -l["max_constatees"])[:4]
            s += f"- {r} échoue à la décision 5, par exemple : " + " ; ".join(
                f"{l['agent']}, {l['melange']}, {l['horizon']}, {l['type']} ({int(l['max_constatees'])} erreurs constatées "
                f"dans un même épisode)" for l in ex) + ".\n"
    if choix["egalite"] and len(choix["egalite"]) > 1:
        s += f"- Égalité de charge (moins de {nb(SEUIL_EGALITE, 0)} point) : {', '.join(choix['egalite'])}.\n"
    s += ("- Alerte 4.5 (tests de résistance) : " + ("aucune.\n" if not alertes else
          "**oui**. " + " ; ".join(f"mode {a['mode']} : {a['hors_budget_retenue']} échec(s) contre "
                                   f"{a['hors_budget_autre']} pour {a['autre']}, pire cellule {nb(a['pire_retenue'], 2)} "
                                   f"contre {nb(a['pire_autre'], 2)} × budget" for a in alertes)
          + ". À signaler à Otsoa avant de valider le choix.\n"))
    r1 = choix_ancien["retenue"]
    s += (f"- Rapporté à part ({LECTURES['ancienne']}) : règle retenue {r1 if r1 else 'aucune'}"
          f"{' (même choix)' if r1 == r0 else ' (choix différent)'}. L'amendement E1-a a été décidé par Otsoa après "
          "l'essai de vérification à petite taille (`explorations/essai_e1_phase1/`, chiffres sans valeur), sur le "
          "principe de la décision 5 : à l'horizon court, la fenêtre après la dérive fait 1 500 actions, et le budget "
          "moyen n'y permet que 0,75 erreur, si bien que l'erreur unique acceptée par la décision 5 suffisait à "
          "éliminer une règle.\n")
    s += "  " + table(["règle", "tient (ancienne lecture)", "cellules hors budget"],
                      [[r, "oui" if choix_ancien["etat"][r]["tient"] else "non", len(choix_ancien["etat"][r]["echecs"])]
                       for r in REGLES]).replace("\n", "\n  ").rstrip() + "\n"
    r2 = choix_long["retenue"]
    s += (f"- Classement lu à l'horizon long (couples délégables de l'horizon long) : {r2 if r2 else 'aucune'}"
          f"{' (même choix)' if r2 == r0 else ''}.\n")
    s += ("- Volume de l'expérience réelle (section 4.6) : quelques milliers d'actions par agent, à confirmer avec "
          "le banc d'essai. L'horizon court (3 000 actions) est cette lecture : c'est lui qui sert au classement.\n\n")
    return s


def section_prediction(budget, autonomie, charges, choix, garantie, retrait):
    s = "## La prédiction de la section 0, confrontée aux résultats\n\n"

    def p3(regles, horizon, types):
        xs = [l["part_temps_p3"] for l in autonomie if l["regle"] in regles and l["horizon"] == horizon
              and l["type"] in types]
        return max(xs) if xs else float("nan")

    et = choix["etat"]
    bB = min(FAM_B, key=lambda r: et[r]["charge"])
    bA = min(A_BARRE, key=lambda r: et[r]["charge"])
    ok1 = et[bB]["charge"] < et[bA]["charge"]
    s += (f"1. « B gagnera sur la charge, par construction » : **{'confirmée' if ok1 else 'infirmée'}**. "
          f"Meilleure B ({bB}) : {nb(et[bB]['charge'], 1)} ; meilleure A réglée sur la barre ({bA}) : "
          f"{nb(et[bA]['charge'], 1)} validations hors lectures pour 100 actions (horizon court, couples délégables). "
          f"A-dégâts : {nb(et['A-dégâts']['charge'], 1)}.\n")
    v2 = p3(A_BARRE, "court", HAUTS)
    s += (f"2. « À 3 000 actions, A n'atteint le palier 3 ni à enjeu moyen ni à enjeu fort » (A½ et A¼) : "
          f"**{'confirmée' if v2 == 0 else 'infirmée'}** (part maximale du temps au palier 3 sur DUR, EXE, SOR, ARG : "
          f"{pc(v2, 3)}). A-dégâts, réglé autrement, atteint l'enjeu moyen : {pc(p3(['A-dégâts'], 'court', ['DUR', 'EXE']), 1)} "
          "au plus.\n")
    v3 = p3(["A½"], "long", FORTS)
    s += (f"3. « À 150 000 actions, A½ n'atteint toujours pas le palier 3 à enjeu fort » : "
          f"**{'confirmée' if v3 == 0 else ('infirmée' if v3 == v3 else 'non mesurée')}** (part maximale : {pc(v3, 3)}).\n")
    v4 = p3(REGLES, "court", FORTS)
    qui = sorted({l["regle"] for l in autonomie if l["horizon"] == "court" and l["type"] in FORTS
                  and l["part_temps_p3"] > 0 and l["regle"] in REGLES})
    s += (f"4. « Avec quelques milliers d'actions par agent, aucune règle n'atteindra le palier 3 à enjeu fort » : "
          f"**{'confirmée' if v4 == 0 else 'infirmée'}** (part maximale au court : {pc(v4, 3)}"
          f"{'' if not qui else ' ; ' + ', '.join(qui)}).\n")
    moy = sorted({l["regle"] for l in autonomie if l["horizon"] == "court" and l["type"] in ("DUR", "EXE")
                  and l["part_temps_p3"] > 0 and l["regle"] in REGLES})
    s += (f"5. « La comparaison s'y jouera à enjeu faible, et à enjeu moyen pour B-régulier » : règles qui atteignent "
          f"le palier 3 à enjeu moyen au court : {', '.join(moy) if moy else 'aucune'}.\n")
    s += "\nCe qu'E1 peut vraiment apprendre (section 0) :\n\n"
    for r in FAM_B:
        cel = [l for l in cellules_choix(budget, r) if str(l["agent"]).startswith(("bord_", "bordD_"))]
        if cel:
            pire = max(cel, key=lambda l: hi_final(l) / l["budget"])
            ko = sum(1 for l in cel if vfinal(l) != "passe")
            s += (f"- {r} et les agents bord (à son pire cas et au-delà) : {len(cel) - ko} cellules sur {len(cel)} "
                  f"tiennent le budget ; pire cellule {nom_cellule(pire)}, {ratio_txt(pire)}.\n")
    for r in FAM_B + ["A-dégâts"]:
        g = [l for l in garantie if l["regle"] == r and l["au_dessus"]]
        if g:
            w = max(g, key=lambda l: l["p3"])
            s += (f"- Coût en garantie de {r} : un type au-dessus de la barre atteint le palier 3 jusqu'à "
                  f"{pc(w['p3'], 1)} des répétitions ({w['agent']}, {w['type']}, {w['melange']}, {w['horizon']}, "
                  f"phase {w['phase']}).\n")
    ret = []
    for r in REGLES:
        x = [l for l in retrait if l["regle"] == r and l["evenement"] == "silencieux" and l["n_promus"]]
        npro = sum(l["n_promus"] for l in x)
        if npro:
            ret.append(f"{r} {nb(sum(l['erreurs_passees_moy'] * l['n_promus'] for l in x) / npro, 2)}")
    if ret:
        s += ("- Coût au retrait (dérives silencieuses, types au palier 3 au changement) : erreurs passées avant le "
              "retrait, en moyenne : " + " ; ".join(ret) + ".\n")
    ad = et["A-dégâts"]
    s += (f"- Wald réglé sur les dégâts (A-dégâts) : {'tient' if ad['tient'] else 'ne tient pas'} le budget partout "
          f"({len(ad['echecs'])} cellule(s) hors budget) ; charge {nb(ad['charge'], 1)} contre {nb(et[bB]['charge'], 1)} "
          f"pour {bB}.\n")
    return s + "\n"


def section_budget(budget):
    s = "## 1. Budget (mesure 1, éliminatoire)\n\n"
    s += ("Excès de dégâts pour 100 actions du flux, niveau par niveau, apparié avec « tout faire valider » ; "
          "intervalle retenu : l'union de l'intervalle normal à 95 % et de l'intervalle bootstrap (2 000 tirages), "
          "pour les événements rares. Amendement E1-a : le budget se lit sur tout l'horizon ; la fenêtre qui va du "
          "changement à la fin n'est éliminatoire qu'à l'horizon long ; à l'horizon court, elle est mesurée et "
          "rapportée (deuxième tableau), sans éliminer. Épreuves jouées à blanc (décision d'Otsoa) ; la colonne "
          "« avec épreuves » les compte comme en deuxième passe, pour information.\n\n")

    def lignes(filtre):
        rows = []
        for r in REGLES + ["liste_fixe", "tri_risque", "trois_reussites", "oracle_p2", "tout_approuver"] + \
                [f"hasard_{x}" for x in REGLES]:
            cel = [l for l in budget if l["regle"] == r and l["mode"] == "base" and l["epreuves"] == "à blanc"
                   and filtre(l)]
            if not cel:
                continue
            av = [l for l in budget if l["regle"] == r and l["mode"] == "base" and l["epreuves"] == "avec" and filtre(l)]
            n_ini = defaultdict(int)
            for l in cel:
                n_ini[l["verdict"]] += 1
            n_fin = sum(1 for l in cel if vfinal(l) != "passe")
            pire = max(cel, key=lambda l: hi_final(l) / l["budget"])
            rows.append([r, len(cel), n_ini["passe"], n_ini["échoue"], n_ini["indécis"], n_fin,
                         nb(hi_final(pire) / pire["budget"], 2), nom_cellule(pire),
                         (str(sum(1 for l in av if l["verdict"] != "passe")) if av else "—")])
        return rows
    ent = ["règle ou témoin", "cellules", "passe", "échoue", "indécis", "hors budget au final",
           "pire cellule (borne haute ÷ budget)", "où", "hors budget avec épreuves"]
    s += "Cellules éliminatoires (tout l'horizon, aux deux horizons ; fenêtre après le changement à l'horizon long) :\n\n"
    s += table(ent, lignes(lambda l: eliminatoire(l, "amendee"))) + "\n"
    s += "Fenêtre après le changement, horizon court (mesurée, non éliminatoire depuis l'amendement E1-a) :\n\n"
    s += table(ent, lignes(lambda l: not eliminatoire(l, "amendee"))) + "\n"
    return s


def section_derive(derive):
    s = "## 1 bis. Dérive : au plus une erreur constatée avant le retrait (amendement E1-a, décision 5)\n\n"
    s += ("Agents dont le taux monte au changement (A6a, annoncé ; A6b, A0d et agents bord qui dérivent, en silence). "
          "Épisode : chaque période au palier 3 après le changement, sur un type dont le taux monte. On compte les "
          "erreurs constatées qui passent pendant l'épisode (exécutées au palier 3, sur une action vérifiable). À enjeu "
          "moyen et fort, le critère est éliminatoire : au plus une, dans chaque épisode de chaque répétition (mode "
          "base). Les erreurs sur des actions invérifiables, qui ne déclenchent pas le retrait, sont exclues du critère "
          "et rapportées à part ; à enjeu faible, les chiffres sont donnés pour information.\n\n")
    rows = []
    for r in REGLES:
        for niv_haut, lib in ((True, "moyen et fort"), (False, "faible (information)")):
            x = [l for l in derive if l["regle"] == r and l["mode"] == "base" and l["critere"] == niv_haut]
            if not x:
                continue
            ep = [l for l in x if l["n_rep_episode"]]
            n_rep_ep = sum(l["n_rep_episode"] for l in ep)
            inv = sum(l["inverifiables_moy"] * l["n_rep_episode"] for l in ep) / n_rep_ep if n_rep_ep else 0.0
            cst = sum(l["constatees_moy"] * l["n_rep_episode"] for l in ep) / n_rep_ep if n_rep_ep else 0.0
            rows.append([r, lib, len(x), int(n_rep_ep), max((int(l["max_constatees"]) for l in x), default=0),
                         sum(1 for l in x if l["verdict"] == "échoue") if niv_haut else "—",
                         nb(cst, 3), nb(inv, 3), max((int(l["inverifiables_max"]) for l in x), default=0)])
    s += table(["règle", "enjeu", "cellules (agent, mélange, horizon, type)", "répétitions avec épisode",
                "erreurs constatées dans un épisode, au plus", "cellules hors critère",
                "erreurs constatées passées (moyenne)", "erreurs invérifiables passées (moyenne, à part)",
                "invérifiables, au plus"], rows) + "\n"
    return s


def section_charge(charges, comparaisons):
    s = "## 2. Charge (mesure 2)\n\n"
    s += ("Validations, corrections et doutes pour 100 actions hors lectures (sans la charge des épreuves, comptée à "
          "part), en moyenne sur les couples (agent, mélange) où au moins un type est sous la barre. Le détail couple "
          "par couple est dans `charges.csv`.\n\n")
    rows = []
    for r in REGLES + ["oracle_p2", "liste_fixe", "tri_risque", "trois_reussites", "tout_valider"]:
        vals = {}
        for h in ("court", "long"):
            ls = [l for l in charges if l["regle"] == r and l["horizon"] == h and l["delegable"]]
            vals[h] = (np.mean([l["charge_hors_lec"] for l in ls]), np.mean([l["charge_hors_lec_avec_ep"] for l in ls]),
                       np.mean([l["charge_totale"] for l in ls]), len(ls)) if ls else (float("nan"),) * 3 + (0,)
        rows.append([r, nb(vals["court"][0], 1), nb(vals["court"][1], 1), nb(vals["court"][2], 1), vals["court"][3],
                     nb(vals["long"][0], 1), nb(vals["long"][1], 1), vals["long"][3]])
    s += table(["règle", "court : hors lectures", "avec épreuves", "totale", "couples", "long : hors lectures",
                "avec épreuves", "couples"], rows) + "\n"
    ags = ["A1", "A2", "A3", "A5"]
    rows = []
    for a in ags:
        for m in E.MELANGES:
            ls = {l["regle"]: l for l in charges if l["agent"] == a and l["melange"] == m and l["horizon"] == "court"}
            if not ls:
                continue
            rows.append([a, m] + [nb(ls[r]["charge_hors_lec"], 1) if r in ls else "—"
                                  for r in REGLES + ["oracle_p2", "liste_fixe", "tri_risque"]])
    if rows:
        s += "Quelques couples de l'horizon court (hors lectures, sans épreuves) :\n\n"
        s += table(["agent", "mélange"] + REGLES + ["oracle", "liste fixe", "tri"], rows) + "\n"
    return s


def tenue_budget(budget, lecture="amendee"):
    """(horizon, mélange, agent, règle ou témoin) → le budget est-il tenu dans ce couple ? Correctif E1-b :
    seules les cellules éliminatoires de la lecture comptent (amendement E1-a : la fenêtre courte, mesurée,
    ne compte plus) ; lecture « ancienne » : toutes les cellules, comme dans le rapport d'origine."""
    tient = defaultdict(lambda: True)
    for l in budget:
        if l["mode"] == "base" and l["epreuves"] == "à blanc" and eliminatoire(l, lecture):
            tient[(l["horizon"], l["melange"], l["agent"], l["regle"])] &= vfinal(l) == "passe"
    return tient


def reussites(budget, charges, comparaisons, lecture="amendee"):
    """Mesure 3 (décision 3) et mesure 4, par règle et par horizon : couples, réussites sans et avec la charge
    des épreuves, parts du gain de l'oracle."""
    tient = tenue_budget(budget, lecture)
    cmp_ = {(l["horizon"], l["melange"], l["agent"], l["regle"], l["contre"], l["mesure"]): l for l in comparaisons}
    ch = {(l["horizon"], l["melange"], l["agent"], l["regle"]): l for l in charges}
    out = {}
    for r in REGLES:
        for h in ("court", "long"):
            couples = sorted({(l["melange"], l["agent"]) for l in charges if l["regle"] == r and l["horizon"] == h})
            if not couples:
                continue
            n_ok = n_ok_ep = 0
            parts = []
            for m, a in couples:
                if not tient[(h, m, a, r)]:
                    continue
                for mes, cpt in (("charge_hors_lec", 0), ("charge_hors_lec_avec_ep", 1)):
                    bat = True
                    for t in ("liste_fixe", "tri_risque"):
                        if not tient[(h, m, a, t)]:
                            continue
                        c = cmp_.get((h, m, a, r, t, mes))
                        bat &= c is not None and c["hi"] < 0
                    if bat:
                        if cpt == 0:
                            n_ok += 1
                        else:
                            n_ok_ep += 1
                o, x = ch.get((h, m, a, "oracle_p2")), ch.get((h, m, a, r))
                if o and x and 100 - o["charge_hors_lec"] >= 1:
                    parts.append((100 - x["charge_hors_lec"]) / (100 - o["charge_hors_lec"]))
            out[(r, h)] = dict(couples=len(couples), ok=n_ok, ok_ep=n_ok_ep, parts=parts)
    return out


def section_reussite_oracle(budget, charges, comparaisons):
    s = "## 3. Réussite au sens de la décision 3, et part du gain de l'oracle (mesures 3 et 4)\n\n"
    s += ("Pour chaque couple (horizon, mélange, agent) : la règle tient-elle le budget dans ce couple (cellules "
          "éliminatoires de l'amendement E1-a ; correctif E1-b), et demande-t-elle moins de validations hors lectures "
          "que la liste fixe et que le tri par le risque (différence appariée, intervalle à 95 % tout sous 0) ? Un "
          "témoin qui dépasse le budget dans le couple compte comme battu. Part du gain de l'oracle : (100 − charge) "
          "÷ (100 − charge de l'oracle avec palier 2), seulement si l'oracle gagne au moins un point. Dernière "
          "colonne : réussites sans épreuves dans le rapport d'origine, qui comptait aussi la fenêtre courte.\n\n")
    apres = reussites(budget, charges, comparaisons, "amendee")
    avant = reussites(budget, charges, comparaisons, "ancienne")
    rows = []
    for (r, h), x in apres.items():
        p = x["parts"]
        rows.append([r, h, x["couples"], x["ok"], x["ok_ep"], nb(float(np.median(p)), 2) if p else "—",
                     f"{nb(min(p), 2)} à {nb(max(p), 2)}" if p else "—", avant[(r, h)]["ok"]])
    s += table(["règle", "horizon", "couples", "réussite (sans épreuves)", "réussite (avec épreuves)",
                "part du gain de l'oracle (médiane)", "étendue", "origine (sans épreuves)"], rows) + "\n"
    return s


def famille_agent(a):
    a = str(a)
    if a.startswith("bordD_"):
        return "bord qui dérive, " + a.split("_")[1]
    return a


def section_retrait(retrait):
    s = "## 5. Retrait (mesure 5)\n\n"
    s += ("Agents qui se dégradent (A6a, changement annoncé ; A6b, A0d et agents bord qui dérivent, en silence), types "
          "dont le nouveau taux dépasse la barre et qui sont au palier 3 au moment du changement. Pour chaque règle : "
          "délai médian jusqu'à la perte du palier 3, en actions du type (pire type), part jamais retirée avant la fin "
          "(pire type), erreurs passées pendant le délai (moyenne) ; « — » : aucun type au palier 3 au changement. "
          "Détail, 95e centile et part du temps au palier 3 après le changement : `retrait.csv`.\n\n")
    groupes = sorted({(famille_agent(l["agent"]), l["horizon"]) for l in retrait},
                     key=lambda x: (x[1] != "court", x[0]))
    rows = []
    for fam, h in groupes:
        row = [fam, h]
        for r in REGLES:
            x = [l for l in retrait if famille_agent(l["agent"]) == fam and l["horizon"] == h and l["regle"] == r]
            pro = [l for l in x if l["n_promus"]]
            if not pro:
                row.append("—")
                continue
            npro = sum(l["n_promus"] for l in pro)
            em = sum(l["erreurs_passees_moy"] * l["n_promus"] for l in pro) / npro
            dm = max(l["delai_type_med"] for l in pro)
            nr = max(l["part_non_retire"] for l in pro)
            row.append(f"{nb(dm, 0) if math.isfinite(dm) else '> fin'} ; {pc(nr, 0)} ; {nb(em, 2)}")
        rows.append(row)
    s += table(["agent", "horizon"] + [f"{r} : délai ; jamais ; erreurs" for r in REGLES], rows) + "\n"
    return s


def section_garantie(garantie):
    s = "## 6. Garantie « au plus 5 fois sur 100 » (mesure 6)\n\n"
    s += ("Part des répétitions où un type dont le vrai taux dépasse la barre atteint le palier 3 (agents constants : "
          "tout l'horizon ; agents qui changent : avant, et après le changement pour une nouvelle promotion). "
          "Intervalle de Wilson ; « échoue » si l'intervalle est tout au-dessus de 5 %.\n\n")
    rows = []
    for r in REGLES:
        for h in ("court", "long"):
            g = [l for l in garantie if l["regle"] == r and l["horizon"] == h and l["au_dessus"]]
            if not g:
                continue
            w = max(g, key=lambda l: l["p3"])
            n_ko = sum(1 for l in g if l["verdict"] == "échoue")
            n_ind = sum(1 for l in g if l["verdict"] == "indécis")
            rows.append([r, h, len(g), n_ko, n_ind, RP.icp(w["p3"], w["p3_lo"], w["p3_hi"]),
                         f"{w['agent']}, {w['type']}, {w['melange']}, {w['phase']}"])
    s += table(["règle", "horizon", "couples (type au-dessus de la barre)", "au-dessus de 5 %", "indécis",
                "pire part", "où"], rows) + "\n"
    return s


def section_volume(volume, volume_a):
    s = "## 7. Volume pour mériter (mesure 7)\n\n"
    s += ("Horizon long, agent A0 (1 sur 10 000 partout) : actions du flux avant le premier palier 3, médiane et "
          "95e centile, et part des répétitions qui ne l'atteignent jamais ; entre parenthèses, le volume analytique "
          "d'un agent sans erreur (relecture, I10). Les autres agents constants de l'horizon long sont dans `volume.csv`.\n\n")
    ana = {(l["melange"], l["regle"], l["type"]): l for l in volume_a}
    rows = []
    for m in E.MELANGES:
        for t in MERITES:
            row = [m, t]
            for r in REGLES:
                l = next((x for x in volume if x["agent"] == "A0" and x["melange"] == m and x["type"] == t
                          and x["regle"] == r), None)
                a = ana.get((m, r, t))
                f = lambda v: nb(v, 0) if v is not None and math.isfinite(v) else "jamais"  # noqa: E731
                cell = "—" if l is None else f"{f(l['volume_med'])} / {f(l['volume_p95'])} ; {pc(l['part_jamais'], 0)}"
                row.append(f"{cell} ({nb(a['volume_flux'], 0) if a else '—'})")
            rows.append(row)
    s += table(["mélange", "type"] + [f"{r} : médiane / 95e centile ; jamais (analytique)" for r in REGLES], rows) + "\n"
    return s


def section_bornes(bornes):
    s = "## 8. Bornes de la règle B sur deux suites piège (mesure 8)\n\n"
    s += ("Référence `RegleUnTypeB`, épreuves toujours réussies. « N réussites puis une erreur » : borne 0,95 ÷ (N + 1) ; "
          "à enjeu moyen ou fort, l'allongement de la pièce 7.3 donne 0,95 ÷ (⌈1,25 N⌉ + 1). « Rafale » : N réussites "
          "puis des erreurs, constatées chacune avec la probabilité d = 0,95, jusqu'au retrait : environ "
          "0,95 ÷ (d × N + 1). Dernière colonne : rapport à l'excès par action qu'autorise le budget (0,95 × barre).\n\n")
    g3 = lambda x: f"{x:.3g}".replace(".", ",")  # noqa: E731
    rows = [[l["melange"], l["regle"], l["niveau"], int(l["N"]), f"{g3(l['piege1_mesure'])} ({g3(l['piege1_attendu'])})",
             f"{g3(l['rafale_mesure'])} ({g3(l['rafale_attendu'])})", nb(l["piege1_sur_budget"], 2),
             nb(l["rafale_sur_budget"], 2)] for l in bornes]
    s += table(["mélange", "règle", "niveau", "N", "piège 1 : mesuré (attendu)", "rafale : mesurée (attendue)",
                "piège 1 ÷ budget", "rafale ÷ budget"], rows) + "\n"
    return s


def section_resistance(budget, derive, choix):
    s = "## 9. Tests de résistance (mesure 9, hors du choix)\n\n"
    s += ("Le contrôle automatique rate 10 % des erreurs au hasard (graine à part), ou toutes les erreurs des cas "
          "difficiles (pire cas), ou constate 10 actions du type après l'action. Une erreur ratée compte comme une "
          "réussite. Avec un constat 100 actions plus tard, la borne (1 + k) ÷ (N + 1) dépasse 1 à enjeu faible "
          "(N = 15 ou 41) : elle est vide, ce qui est signalé sans être simulé.\n\n")
    rows = []
    for r in REGLES:
        row = [r]
        for mode in E.MODES:
            cel = cellules_choix(budget, r, "amendee", mode)
            if not cel:
                row.append("—")
                continue
            n = sum(1 for l in cel if (vfinal(l) if mode == "base" else l["verdict"]) != "passe")
            hi = (lambda l: hi_final(l)) if mode == "base" else (lambda l: l["exces_hi"])  # base : après relance
            w = max(cel, key=lambda l: hi(l) / l["budget"])
            nd = len(echecs_derive(derive, r, mode))
            mx = max((int(l["max_constatees"]) for l in derive if l["regle"] == r and l["mode"] == mode and l["critere"]),
                     default=0)
            row.append(f"{n} / {len(cel)} ; pire {nb(hi(w) / w['budget'], 2)} ; décision 5 : {nd} ({mx} au plus)")
        rows.append(row)
    s += table(["règle"] + [f"{m} : hors budget ; pire cellule (× budget) ; épisodes hors décision 5" for m in E.MODES],
               rows) + "\n"
    s += ("Cellules éliminatoires de l'amendement E1-a. Avec le constat différé, les erreurs exécutées pendant le délai "
          "passent : la décision 5 suppose un constat immédiat. Avec un contrôle qui rate des erreurs, celles-ci ne sont "
          "pas constatées : elles passent sans compter dans le critère (colonne « ratées » de `derive.csv`).\n\n")
    return s


def courbe_cusum(p0, p1, d=0.95, cible=200):
    """CUSUM optimal (Page) pour p0 → p1 sur les actions vérifiées, par chaîne de Markov discrétisée
    (pas δ = b ÷ r ; une erreur monte de round(a ÷ δ) pas ; seuil h = H δ, H entier ; H = 1 : alerte à la
    première erreur). Rend une fonction ARL0 (en actions du type) → délai (en actions du type, départ à
    S = 0), interpolée entre seuils voisins (CUSUM randomisé : enveloppe atteignable) ; le détecteur
    trivial (alerte immédiate : ARL0 = délai = 1) borne le bas de la courbe."""
    import scipy.sparse as sp
    import scipy.sparse.linalg as spl
    a = math.log(p1 / p0)
    b = -math.log((1 - p1) / (1 - p0))
    r = max(1, math.ceil(cible * b / a))
    up = max(1, round(a / (b / r)))
    memo = {}

    def arl(H, p):
        if (H, p) in memo:
            return memo[(H, p)]
        if H == 0:
            return 1.0
        i = np.arange(H)
        j_up, j_dn = i + up, np.maximum(i - r, 0)
        m = j_up < H
        rows = np.concatenate([i, i[m], i])
        cols = np.concatenate([i, j_up[m], j_dn])
        vals = np.concatenate([np.ones(H), np.full(m.sum(), -p), np.full(H, -(1 - p))])
        A = sp.csc_matrix((vals, (rows, cols)), shape=(H, H))
        memo[(H, p)] = float(spl.spsolve(A, np.ones(H))[0]) if H > 1 else 1.0 / p
        return memo[(H, p)]

    def delai(arl0_type):
        A = arl0_type * d
        hi = 1
        while arl(hi, p0) < A:
            hi *= 2
            if hi > 2_000_000:
                return float("nan")
        lo = 0  # arl(lo) < A <= arl(hi)
        if arl(hi, p0) >= A and hi == 1:
            lo = 0
        else:
            lo = hi // 2
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if arl(mid, p0) < A:
                lo = mid
            else:
                hi = mid
        a_lo, a_hi = arl(lo, p0), arl(hi, p0)
        d_lo, d_hi = (1.0 if lo == 0 else arl(lo, p1)), arl(hi, p1)
        lam = 0.0 if a_hi == a_lo else (A - a_lo) / (a_hi - a_lo)
        return (d_lo + lam * (d_hi - d_lo)) / d
    return delai


def section_cusum(cusum):
    s = "## 10. Retrait comparé au meilleur détecteur possible (mesure 10)\n\n"
    s += ("Pour chaque règle et chaque type devenu mauvais en silence (A6b, A0d, agents bord qui dérivent) : fréquence "
          "mesurée des fausses alertes avant le changement (actions au palier 3 par perte du palier 3), délai moyen "
          "mesuré du retrait, et délai du CUSUM optimal (Page, mêmes taux avant et après) réglé sur la même fréquence "
          "de fausses alertes. Rapport > 1 : la règle est plus lente que le meilleur détecteur.\n\n")
    rows = []
    cache = {}
    for l in cusum:
        if not (l["fausses_alertes"] and l["n_retires"] and l["delai_type_moy"] == l["delai_type_moy"]):
            continue
        cle = (l["p0"], l["p1"])
        if cle not in cache:
            cache[cle] = courbe_cusum(l["p0"], l["p1"])
        try:
            dc = cache[cle](l["arl0_type"])
        except Exception:  # noqa: BLE001
            dc = float("nan")
        l["delai_cusum"] = dc
        rows.append([l["regle"], l["agent"], l["melange"], l["horizon"], l["type"], nb(l["arl0_type"], 0),
                     nb(l["delai_type_moy"], 0), nb(dc, 0), nb(l["delai_type_moy"] / dc, 2) if dc == dc else "—"])
    rows.sort(key=lambda x: (x[0], x[1]))
    if rows:
        with open(os.path.join(DOSSIER, "cusum_comparaison.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["regle", "agent", "melange", "horizon", "type", "arl0_type", "delai_regle", "delai_cusum", "rapport"])
            for l in cusum:
                if "delai_cusum" in l:
                    w.writerow([l["regle"], l["agent"], l["melange"], l["horizon"], l["type"], f"{l['arl0_type']:.6g}",
                                f"{l['delai_type_moy']:.6g}", f"{l['delai_cusum']:.6g}",
                                f"{l['delai_type_moy'] / l['delai_cusum']:.6g}"])
    s += table(["règle", "agent", "mélange", "horizon", "type", "actions entre fausses alertes", "délai mesuré",
                "délai du CUSUM", "rapport"], rows[:60]) + "\n"
    if len(rows) > 60:
        s += f"({len(rows) - 60} lignes de plus dans `cusum.csv`.)\n\n"
    if not rows:
        s += "Aucun couple avec à la fois des fausses alertes avant et un retrait après le changement.\n\n"
    return s


def section_tables_fixes(barres, cert, etal):
    s = "## 11. Certification (mesure 11), barres, N, étalonnage d'A-dégâts\n\n"
    rows = [[l["melange"], l["niveau"], f"1 sur {nb(l['un_sur'], 1)}", int(l["N_B_regulier"]), int(l["N_B_tout"]),
             int(l["N_B_regulier_allonge"]), int(l["N_B_tout_allonge"]),
             f"1 sur {nb(1 / l['pm3_A_degats'], 1)} ({nb(l['pm3_A_degats_sur_barre'], 2)} barre)"] for l in barres]
    s += table(["mélange", "niveau", "barre", "N B-régulier", "N B-tout", "⌈1,25 N⌉ B-rég.", "⌈1,25 N⌉ B-tout",
                "pm3 d'A-dégâts"], rows) + "\n"
    rows = [[l["melange"], l["niveau"], nb(l["certification"], 0), nb(l["regle_de_trois"], 0)] for l in cert]
    s += "Réussites sans erreur pour établir que le taux est sous la barre (risque 5 %) :\n\n"
    s += table(["mélange", "niveau", "exact : (1 − barre)^n ≤ 0,05", "règle de trois, 3 ÷ barre"], rows) + "\n"
    rows = [[l["melange"], l["niveau"], f"{l['pm3']:.5g}", nb(l["pm3_sur_barre"], 2), nb(l["q_pire_sur_barre"], 2),
             nb(l["E_sur_barre"], 4), int(l["iterations"])] for l in etal]
    s += ("Étalonnage d'A-dégâts (`etalonnage_e1.py`) : pm3 tel que l'excès stationnaire du pire agent régulier égale "
          "le budget, pb3 = pm3 ÷ 2 ; simulation d'un type isolé, fidèle au moteur ; contrôle hors échantillon à ±0,5 %.\n\n")
    s += table(["mélange", "niveau", "pm3", "pm3 ÷ barre", "pire q ÷ barre", "excès max ÷ budget", "itérations"], rows)
    return s + "\n"


NOTES = [
    "Chemin v2 intact : aucun fichier de la deuxième passe n'est modifié ; E1 vit dans config_e1.py, regle_e1.py, "
    "etalonnage_e1.py, executer_e1.py, ecrire_resultats_e1.py. Le moteur E1, réglé comme la v2, refait exactement le "
    "moteur v2 (test). Interrupteurs d'E1 : `lec_autonome` (règles et témoins) et `lec_sans_effet` (comptabilité).",
    E.NOTE_AGENTS_BORD_DERIVE,
    "Amendement E1-a (décision d'Otsoa, après l'essai de vérification) : critère de la décision 5 compté par période "
    "au palier 3 après le changement (la période en cours au changement, puis chaque nouvelle promotion), sur les types "
    "dont le taux monte ; « constatée » : erreur sur une action vérifiable, que le contrôle voit (aussitôt, ou 10 "
    "actions plus tard en mode retard) ; erreurs invérifiables et erreurs ratées par un contrôle imparfait exclues du "
    "critère, rapportées à part. Les cellules indécises de la fenêtre courte sont encore relancées, pour que "
    "l'ancienne lecture soit calculée comme avant.",
    "Classement (4.2) : les couples sont ceux de l'horizon court (agent × mélange), qui est aussi le volume de "
    "l'expérience réelle (4.6) ; le classement à l'horizon long est donné à part. La charge de classement est hors "
    "lectures et sans la charge des épreuves (« comptée à part », décision 6) ; la version avec épreuves est donnée.",
    "Prudence (4.3) : marge = 1 − (borne haute de l'excès ÷ budget) dans la pire cellule de la règle (toutes cellules, "
    "après relance) ; égalité de prudence à 0,001 près, puis simplicité : B-tout, B-régulier, A½, A¼, A-dégâts.",
    "Intervalles : l'union de l'intervalle normal et de l'intervalle bootstrap (percentile, 2 000 tirages), pour toutes "
    "les cellules : c'est plus prudent que l'un ou l'autre (une cellule indécise est relancée, puis compte comme un échec).",
    "Règle B, points laissés ouverts par le plan : la consigne modifiée divise le compteur par deux (⌊c/2⌋, soit ⌊N/2⌋ "
    "au palier 3, comme écrit dans le plan) ; le compteur est plafonné à la longueur exigée (⌈1,25 N⌉ pendant une "
    "montée allongée, N sinon) ; l'allongement ne se cumule pas ; après un changement de modèle, plus d'allongement "
    "(nouvel agent ; les erreurs deviennent des épreuves) ; sous le palier 3, le palier 2 suit le score de Wald v2.",
    "Tests de résistance : une variante d'épreuve est jugée par le même contrôle (10 % de ses erreurs ratées ; toutes, "
    "dans le pire cas, puisque les variantes sont des cas difficiles) ; avec le constat différé, l'épreuve est jugée "
    "aussitôt, seules les preuves des actions ordinaires arrivent 10 actions du type plus tard.",
    "Garantie après un changement : seules les nouvelles promotions au palier 3 comptent (comme en v2) ; un type déjà "
    "au palier 3 au changement relève du retrait (mesure 5).",
    "Alerte 4.5 : critère fixé avant le lancement (plus d'échecs qu'une autre survivante dans un mode, ou une pire "
    "cellule au moins 1,25 fois plus haute et au moins à la moitié du budget), appliqué aux cellules éliminatoires de "
    "l'amendement E1-a ; les échecs comptent les cellules hors budget et les épisodes hors décision 5.",
    "Pannes injectées : non simulées (décision 3). A8 est vide à l'horizon court (aucune règle n'atteint SOR au "
    "palier 3 avant t = 1 500) ; il n'y a pas d'A8 à l'horizon long dans le plan.",
]


# --------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------
def pire_rapport(budget, regle, lecture="amendee"):
    """Borne haute de l'excès ÷ budget dans la pire cellule éliminatoire de la règle ou du témoin (mode
    base, épreuves à blanc) ; correctif E1-b : cellules de la lecture E1-a, fenêtre courte exclue."""
    cel = [l for l in budget if l["regle"] == regle and l["mode"] == "base" and l["epreuves"] == "à blanc"
           and eliminatoire(l, lecture)]
    return max(hi_final(l) / l["budget"] for l in cel) if cel else None


def figures(budget, charges, garantie, volume):
    import matplotlib.pyplot as plt
    couleurs = dict(zip(REGLES, [RP.BLEU, RP.AQUA, RP.VIOLET, RP.ORANGE, RP.MAGENTA]))
    faits = []
    # 1. charge contre pire cellule
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    for r in REGLES + ["liste_fixe", "tri_risque", "oracle_p2", "trois_reussites"]:
        x = pire_rapport(budget, r)
        ch = [l["charge_hors_lec"] for l in charges if l["regle"] == r and l["horizon"] == "court" and l["delegable"]]
        if x is None or not ch:
            continue
        y = float(np.mean(ch))
        ax.scatter([max(x, 1e-3)], [y], s=46, color=couleurs.get(r, RP.ENCRE2), marker="o" if r in REGLES else "s",
                   zorder=3)
        ax.annotate(r.replace("_", " "), (max(x, 1e-3), y), textcoords="offset points", xytext=(6, 4), fontsize=8)
    ax.axvline(1.0, color=RP.ROUGE, lw=1, ls="--")
    ax.set_xscale("log")
    ax.set_xlabel("pire cellule éliminatoire (amendement E1-a) : borne haute de l'excès ÷ budget")
    ax.set_ylabel("charge hors lectures (court, couples délégables)")
    ax.set_title("Charge et budget, par règle")
    fig.tight_layout()
    fig.savefig(os.path.join(DOSSIER, "fig1_charge_budget.png"), dpi=160)
    plt.close(fig)
    faits.append("fig1_charge_budget.png")
    # 2. garantie
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    xs = np.arange(len(REGLES))
    for j, h in enumerate(("court", "long")):
        vals = []
        for r in REGLES:
            g = [l["p3"] for l in garantie if l["regle"] == r and l["horizon"] == h and l["au_dessus"]]
            vals.append(max(g) if g else 0)
        ax.bar(xs + (j - 0.5) * 0.38, vals, width=0.36, color=[RP.BLEU, RP.ORANGE][j], label=f"horizon {h}")
    ax.axhline(0.05, color=RP.ROUGE, lw=1, ls="--")
    ax.set_xticks(xs, REGLES)
    ax.set_ylabel("pire part promue au palier 3\n(types au-dessus de la barre)")
    ax.set_title("Garantie « au plus 5 fois sur 100 »")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(DOSSIER, "fig2_garantie.png"), dpi=160)
    plt.close(fig)
    faits.append("fig2_garantie.png")
    # 3. volume pour mériter (A0, long)
    if volume:
        fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.8), sharey=True)
        for ax, m in zip(axs, E.MELANGES):
            for i, r in enumerate(REGLES):
                ys, xs_ = [], []
                for j, t in enumerate(MERITES):
                    l = next((x for x in volume if x["agent"] == "A0" and x["melange"] == m and x["type"] == t
                              and x["regle"] == r), None)
                    if l is not None and l["part_jamais"] < 0.5:
                        ys.append(l["volume_med"])
                        xs_.append(j + (i - 2) * 0.12)
                ax.scatter(xs_, ys, color=couleurs[r], s=24, label=r)
            ax.set_yscale("log")
            ax.set_xticks(range(len(MERITES)), MERITES)
            ax.set_title(m.replace("_", " "))
            ax.axhline(3000, color=RP.ENCRE2, lw=0.8, ls=":")
        axs[0].set_ylabel("actions du flux avant le palier 3 (médiane)")
        axs[1].legend(fontsize=7)
        fig.suptitle("Volume pour mériter, agent A0, horizon long (pointillé : 3 000)")
        fig.tight_layout()
        fig.savefig(os.path.join(DOSSIER, "fig3_volume.png"), dpi=160)
        plt.close(fig)
        faits.append("fig3_volume.png")
    return faits


# --------------------------------------------------------------------------
def note_correctif_e1b(budget, charges, comparaisons):
    """Note de tête du correctif E1-b (après la grille, sans nouvelle simulation)."""
    av = reussites(budget, charges, comparaisons, "ancienne")
    ap = reussites(budget, charges, comparaisons, "amendee")
    chg = " ; ".join(f"{r} {av[(r, h)]['ok']} → {ap[(r, h)]['ok']}" for r in REGLES for h in ("court",) if (r, h) in ap)
    chg_l = " ; ".join(f"{r} {av[(r, h)]['ok']} → {ap[(r, h)]['ok']}" for r in REGLES for h in ("long",) if (r, h) in ap)
    fig = " ; ".join(f"{r} {nb(pire_rapport(budget, r, 'ancienne'), 2)} → {nb(pire_rapport(budget, r), 2)}"
                     for r in REGLES if pire_rapport(budget, r) is not None)
    s = ("> **Correctif E1-b** (4 novembre 2026, après la grille ; aucune simulation relancée : ce rapport et ses "
         "figures sont régénérés à partir des CSV de la grille, commit e0b076f ; rapport d'origine : "
         "`RESULTATS_E1_origine.md`). Deux défauts de `ecrire_resultats_e1.py` :\n")
    s += ("> - figure 1 : chaque règle y était placée selon sa pire cellule, fenêtre courte comprise (ancienne lecture). "
          f"Elle suit maintenant les cellules éliminatoires de l'amendement E1-a. Pire cellule ÷ budget, avant → après : "
          f"{fig} ;\n")
    s += ("> - mesure 3 (réussite) : la tenue du budget dans un couple comptait aussi la fenêtre courte. Elle ne compte "
          f"plus que les cellules éliminatoires. Réussites sans épreuves, avant → après, horizon court : {chg} ; "
          f"horizon long : {chg_l}. Les baisses viennent des témoins : une liste fixe ou un tri hors budget dans la "
          "seule fenêtre courte comptait comme battu d'office ; il faut maintenant le battre en charge.\n")
    s += ("> - Ne changent pas : les CSV, les cellules et les verdicts du budget, la décision 5, la règle de choix et son "
          "résultat (B-régulier), l'alerte 4.5, l'ancienne lecture (B-tout).\n")
    s += (">\n> **Décision d'Otsoa après l'alerte 4.5** (`REGLE.md`, « Décisions prises après la deuxième passe », point 7) : "
          "B-tout en principal pour l'expérience réelle ; B-régulier mesurée à côté, sur les mêmes actions, si le banc "
          "d'essai le permet sans surcoût.\n")
    return s


def main():
    budget, charges, comparaisons = lire("budget"), lire("charges"), lire("comparaisons")
    garantie, autonomie, retrait = lire("garantie"), lire("autonomie"), lire("retrait")
    volume, volume_a, cusum = lire("volume"), lire("volume_analytique"), lire("cusum")
    bornes, cert, barres, etal = lire("bornes_b"), lire("certification"), lire("barres"), lire("etalonnage_a_degats")
    with open(os.path.join(DOSSIER, "meta.json")) as f:
        meta = json.load(f)
    derive = lire("derive")
    choix = choisir(budget, charges, derive)
    choix_ancien = choisir(budget, charges, derive, lecture="ancienne")
    choix_long = choisir(budget, charges, derive, horizon_classement="long")
    alertes = alerte_resistance(budget, derive, choix)
    with open(os.path.join(DOSSIER, "choix.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["lecture", "regle", "tient", "charge_classement", "n_couples", "marge_pire_cellule",
                    "cellules_hors_budget", "episodes_hors_decision5", "retenue"])
        for nom, ch in (("amendement_E1a", choix), ("ancienne_fenetre_courte", choix_ancien),
                        ("amendement_E1a_classement_long", choix_long)):
            for r in REGLES:
                st = ch["etat"][r]
                w.writerow([nom, r, st["tient"], f"{st['charge']:.6g}", st["n_couples"], f"{st['marge']:.6g}",
                            len(st["echecs"]), len(st["echecs_derive"]), r == ch["retenue"]])
    gel = os.path.join(ICI, "GEL_E1.txt")
    essai = bool(meta.get("filtre_agents")) or meta["horizons"]["court"]["R"] != E.HORIZONS["court"]["R"] or \
        meta["horizons"]["long"]["R"] != E.HORIZONS["long"]["R"] or meta["horizons"]["long"]["T"] != E.HORIZONS["long"]["T"]
    s = "# Exploration E1 · résultats\n\n"
    s += (f"> Exploration annoncée comme telle (`PLAN_EXPLORATION_E1.md`, révision 1). Elle ne change pas le verdict de la "
          f"deuxième passe (`resultats/`). Écrit le {time.strftime('%d/%m/%Y à %H:%M')} par `ecrire_resultats_e1.py`, à partir "
          f"des CSV de ce dossier.\n")
    s += (f"> Horizons : court {meta['horizons']['court']['T']} actions × {meta['horizons']['court']['R']} répétitions ; "
          f"long {meta['horizons']['long']['T']} actions × {meta['horizons']['long']['R']} répétitions (blocs de "
          f"{meta['horizons']['long']['bloc']}). Graine maîtresse {meta['graine']}. {meta['n_taches']} tâches, "
          f"{meta['n_relances']} relances, {nb(meta['duree_s'] / 60, 1)} min. Gel : `GEL_E1.txt`"
          f"{'' if os.path.exists(gel) else ' (absent)'}.\n")
    if essai:
        s += "> **ESSAI À PEU DE RÉPÉTITIONS : ces chiffres ne valent rien comme résultat.**\n"
    s += ">\n" + note_correctif_e1b(budget, charges, comparaisons)
    s += "\n"
    s += section_choix(budget, charges, choix, choix_ancien, alertes, choix_long)
    s += section_prediction(budget, autonomie, charges, choix, garantie, retrait)
    s += section_budget(budget)
    s += section_derive(derive)
    s += section_charge(charges, comparaisons)
    s += section_reussite_oracle(budget, charges, comparaisons)
    s += section_retrait(retrait)
    s += section_garantie(garantie)
    s += section_volume(volume, volume_a)
    s += section_bornes(bornes)
    s += section_resistance(budget, derive, choix)
    s += section_cusum(cusum)
    s += section_tables_fixes(barres, cert, etal)
    s += "## Choix d'implémentation et points du plan tranchés\n\n" + "".join(f"- {n}\n" for n in NOTES) + "\n"
    figs = figures(budget, charges, garantie, volume)
    s += "## Figures\n\n" + "".join(f"- `{f}`\n" for f in figs)
    with open(os.path.join(DOSSIER, "RESULTATS_E1.md"), "w") as f:
        f.write(s)
    print(f"écrit {os.path.join(DOSSIER, 'RESULTATS_E1.md')} ; règle retenue : {choix['retenue']}")


if __name__ == "__main__":
    main()
