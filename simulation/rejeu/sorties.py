"""Les sorties du rejeu (PLAN_EXPERIENCE.md, 5.15) : les CSV, `meta.json` et `RESULTATS.md` (écrit à partir des CSV).

CSV du plan : budget, charges, ecart, garantie, retrait, derive, resistance, volume, epreuves, reussite_taches, choix ;
en plus (CHOIX_PHASE2.md) : decision.csv, les points 0 à 6 de la règle de décision et l'étiquette.

Avec un avertissement (bout en bout sur le pilote), chaque sortie commence par une ligne « # AVERTISSEMENT … » (CSV),
un champ « avertissement » (meta.json) ou un encadré (RESULTATS.md).
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import sys
import time

import numpy as np
import scipy

from . import classes as CL
from . import config_rejeu as CR
from . import decision as DE
from . import entrees as EN
from . import intervalles as IC
from . import pipeline as PL
from . import suites as SU
from . import types_regle as TY

FICHIERS = ("budget", "charges", "ecart", "garantie", "retrait", "derive", "resistance", "volume", "epreuves",
            "reussite_taches", "choix", "decision", "symetrie")
Z95 = IC.Z95


# --------------------------------------------------------------------------
# Écriture
# --------------------------------------------------------------------------
def _propre(v):
    if isinstance(v, (np.floating, float)):
        v = float(v)
        return "" if math.isnan(v) else ("inf" if math.isinf(v) and v > 0 else ("-inf" if math.isinf(v) else v))
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if isinstance(v, (tuple, list)):
        return " ; ".join(str(x) for x in v)
    return v


def ecrire_csv(dossier: str, nom: str, lignes: list, avertissement: str = None) -> str:
    chemin = os.path.join(dossier, nom + ".csv")
    champs = []
    for l in lignes:
        for k in l:
            if k not in champs:
                champs.append(k)
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        if avertissement:
            f.write(f"# AVERTISSEMENT : {avertissement}\n")
        w = csv.DictWriter(f, fieldnames=champs or ["vide"])
        w.writeheader()
        for l in lignes:
            w.writerow({k: _propre(v) for k, v in l.items()})
    return chemin


def lire_csv(dossier: str, nom: str) -> list:
    chemin = os.path.join(dossier, nom + ".csv")
    if not os.path.exists(chemin):
        return []
    with open(chemin, encoding="utf-8") as f:
        return list(csv.DictReader(l for l in f if not l.startswith("#")))


def _fam(cm) -> dict:
    if cm[0] == "config":
        return dict(type_suite="configuration", environnement=cm[1], modele=cm[2], modele_Y="", mode="")
    if cm[0] == "scenario":
        return dict(type_suite="scénario", environnement=cm[1], modele=cm[2], modele_Y=cm[3],
                    mode=cm[4] if len(cm) > 4 else "")
    return dict(type_suite=str(cm[0]), environnement="", modele="", modele_Y="", mode="")


def _iv(prefixe: str, iv: dict) -> dict:
    out = {}
    for m in ("i", "ii", "iii", "percentile"):
        out[f"{prefixe}lo_{m}"], out[f"{prefixe}hi_{m}"] = iv[m]
    return out


# --------------------------------------------------------------------------
# Tables
# --------------------------------------------------------------------------
def lignes_budget(analyses: dict, decision_principale: dict) -> list:
    """Cellules du budget : règles (toutes les valeurs de e) et témoins (e principal) pour l'analyse principale ;
    règles à e principal pour les analyses secondaires ; dégâts pour 100 actions (Q8) et fenêtre après la jonction."""
    lignes = []
    dep, non_t = {}, {}
    for t, d in decision_principale["point2"]["temoins"].items():
        for c in d["depassement"]["cellules"]:
            dep[(t, c["famille"], c["niveau"])] = c["etabli"]
            non_t[(t, c["famille"], c["niveau"])] = c.get("non_testable", "")
    for nom_an, an in analyses.items():
        principale = nom_an == "principale"
        noms = list(an.reglages.noms_regles)
        e_vals = an.reglages.valeurs_e if principale else (an.reglages.e_principal,)
        for regle in noms:
            for e in e_vals:
                for c in DE.cellules(an, regle, e):
                    q_act = an.magasin.get(("budget_actions",) + c["famille"] + (regle, e, c["niveau"]))
                    q_fen = an.magasin.get(("budget_fenetre",) + c["famille"] + (regle, e, c["niveau"]))
                    l = dict(analyse=nom_an, **_fam(c["famille"]), regle=regle, type_regle="règle", e=e,
                             niveau=c["niveau"], statut=c["verdict"], exces_100_ecritures=c["centre"],
                             budget=c["budget"], rapport=c["centre"] / c["budget"], methode=c["methode"],
                             lo=c["lo"], hi=c["hi"], etabli=c.get("etabli", ""), borne_maxt=c.get("borne_maxt", ""),
                             non_testable=c.get("non_testable", ""),
                             c_etoile=c.get("c_etoile", ""), borne_construction=c.get("borne_construction", ""),
                             s_sur_q=c.get("s_sur_q", ""), s_sur_q_lo=c.get("s_sur_q_lo", ""),
                             s_sur_q_hi=c.get("s_sur_q_hi", ""), demontree=c.get("demontree", ""),
                             borne_cp_haute=c.get("borne_cp_haute", ""), n_eff=c.get("n_eff", ""),
                             demontree_sous_hypothese=c.get("demontree_hyp", ""),
                             borne_cp_haute_sous_hypothese=c.get("borne_cp_haute_hyp", ""),
                             rho_hypothese=c.get("rho_hyp", ""),
                             rho=c.get("rho", ""), garantie_hors_hypothese=c.get("garantie_hors_hypothese", ""),
                             fragile=c["fragile"], part_rep_palier3=c["part_rep_p3"],
                             ecritures_niveau=c["ecritures_niveau"], taches_porteuses=c["porteuses"], G=c["G"],
                             eliminatoire=bool(principale and regle == "B-tout" and e == an.reglages.e_principal),
                             exces_100_actions=q_act.centre if q_act is not None and e == an.reglages.e_principal
                             else float("nan"),
                             exces_fenetre_apres_jonction=q_fen.centre if q_fen is not None else float("nan"),
                             degats_absolus=an.resume_r0.get(c["famille"], {}).get("degats", {}).get(
                                 (regle, e, c["niveau"]), float("nan")))
                    l.update(_iv("", c["intervalles"]))
                    lignes.append(l)
        if principale:
            e = an.reglages.e_principal
            temoins = sorted({k[0] for r in an.resume_r0.values() for k in r.get("delegue", {})})
            for t in temoins:
                for cle in an.familles:
                    for cm in an.modes(cle):
                        for niv in TY.NIVEAUX:
                            q = an.magasin.get(("budget",) + cm + (t, e, niv))
                            if q is None:
                                continue
                            iv = PL.intervalles_quantite(q, an.reglages.choix, an.reglages.B)
                            b = float(CR.BUDGET[niv])
                            l = dict(analyse=nom_an, **_fam(cm), regle=t, type_regle="témoin", e=e, niveau=niv,
                                     statut="", exces_100_ecritures=q.centre, budget=b, rapport=q.centre / b,
                                     methode=iv["methode_effective"], lo=iv["retenue"][0], hi=iv["retenue"][1],
                                     verdict_intervalle_descriptif=IC.verdict(*iv["retenue"], b) if len(q.boot)
                                     else "",   # ne décide plus rien depuis Q13 (C13, M7)
                                     delegue=an.resume_r0.get(cm, {}).get("delegue", {}).get((t, niv), ""),
                                     depassement_etabli=dep.get((t, cm, niv), ""),
                                     non_testable=non_t.get((t, cm, niv), ""))
                            l.update(_iv("", iv))
                            lignes.append(l)
    return lignes


def lignes_lettre(an) -> list:
    """Lettre d'origine (Q8, lecture A) : B-tout avec les barres et les N du point 8, dégâts en plus pour 100 actions
    (lectures comprises), même mesure (dépassement établi par max-T) ; analyse secondaire."""
    out = []
    for c in DE.cellules(an, "B-tout-lettre", cle_q="budget_actions"):
        env = c["famille"][1]
        l = dict(analyse=an.nom, **_fam(c["famille"]), regle="B-tout-lettre", type_regle="règle (lettre d'origine)",
                 e=c["e"], niveau=c["niveau"], statut=c["verdict"], exces_100_actions=c["centre"], budget=c["budget"],
                 rapport=c["centre"] / c["budget"], methode=c["methode"], lo=c["lo"], hi=c["hi"],
                 etabli=c.get("etabli", ""), borne_maxt=c.get("borne_maxt", ""), c_etoile=c.get("c_etoile", ""),
                 non_testable=c.get("non_testable", ""),
                 N_point_8=an.config.n_tout_lettre[(env, c["niveau"])] if an.config is not None else "",
                 part_rep_palier3=c["part_rep_p3"], taches_porteuses=c["porteuses"], G=c["G"],
                 eliminatoire=False)
        l.update(_iv("", c["intervalles"]))
        out.append(l)
    return out


def part_du_gain(q, oracle, choix, B) -> tuple:
    """Part du gain de l'oracle (5.12, point 6 ; descriptive, Q15) : (100 − charge de la règle) ÷ (100 − charge de
    l'oracle), si l'oracle gagne au moins un point ; intervalle par la méthode retenue, sur les mêmes répétitions."""
    from . import analyse as AN
    if not (100 - oracle.centre >= 1):
        return float("nan"), float("nan"), float("nan")
    with np.errstate(divide="ignore", invalid="ignore"):
        f = lambda a, b: (100 - np.asarray(a, float)) / (100 - np.asarray(b, float))  # noqa: E731
        nb = min(len(q.boot), len(oracle.boot))
        d = AN.Quantite(centre=float(f(q.centre, oracle.centre)), boot=f(q.boot.tableau()[:nb], oracle.boot.tableau()[:nb]),
                        jack=f(q.jack, oracle.jack) if q.jack is not None and oracle.jack is not None else None,
                        strates_jack=q.strates_jack, G=q.G)
    iv = PL.intervalles_quantite(d, choix, B)
    return d.centre, iv["retenue"][0], iv["retenue"][1]


def lignes_charges(an) -> list:
    choix, e = an.reglages.choix, an.reglages.e_principal
    lignes = []
    for cle in an.configs():
        env, mod = cle[1], cle[2]
        dele = an.delegables.get((env, mod))
        ch = {}
        for k, q in an.magasin.items():
            if k[0] == "charge" and k[1:4] == cle and k[5] == e:
                ch[k[4]] = q
        tv = ch.get("tout_valider")
        oracle = ch.get("oracle_p2")
        for nom, q in ch.items():
            iv = PL.intervalles_quantite(q, choix, an.reglages.B)
            l = dict(**_fam(cle), ligne=nom, mesure="charge_hors_lec", delegable=dele, valeur=q.centre,
                     lo=iv["retenue"][0], hi=iv["retenue"][1], methode=iv["methode_effective"],
                     lo_seconde=iv["seconde"][0], hi_seconde=iv["seconde"][1])
            if tv is not None and tv.centre:
                l["baisse_des_validations"] = 1 - q.centre / tv.centre
            if oracle is not None and nom in an.reglages.noms_regles:
                pg = part_du_gain(q, oracle, choix, an.reglages.B)
                l.update(part_du_gain_de_l_oracle=pg[0], part_du_gain_lo=pg[1], part_du_gain_hi=pg[2])
            qe = an.magasin.get(("charge_avec_ep",) + cle + (nom, e))
            if qe is not None:
                l["charge_hors_lec_avec_epreuves"] = qe.centre
            r0 = an.resume_r0.get(cle, {}).get("charges", {}).get(nom, {})
            for k in ("charge_100_ecritures", "charge_totale", "charge_epreuves", "exces_a_part",
                      "inverifiables_seules", "ouvertes", "tentatives", "reussies", "ratees", "impossibles"):
                if k in r0:
                    l[k] = r0[k]
            lignes.append(l)
        for k, q in an.magasin.items():
            if k[0] == "diff_charge" and k[1:4] == cle:
                iv = PL.intervalles_quantite(q, choix, an.reglages.B)
                lignes.append(dict(**_fam(cle), ligne=f"{k[4]} − {k[5]}", mesure="différence de charge (appariée)",
                                   delegable=dele, valeur=q.centre, lo=iv["retenue"][0], hi=iv["retenue"][1],
                                   methode=iv["methode_effective"], lo_seconde=iv["seconde"][0],
                                   hi_seconde=iv["seconde"][1]))
            if k[0] == "diff_exces" and k[1:4] == cle:
                iv = PL.intervalles_quantite(q, choix, an.reglages.B)
                lignes.append(dict(**_fam(cle), ligne=f"{k[4]} − hasard_{k[4]} ({k[5]})",
                                   mesure="différence de dégâts en plus (appariée)", delegable=dele, valeur=q.centre,
                                   lo=iv["retenue"][0], hi=iv["retenue"][1], methode=iv["methode_effective"]))
    for k, q in an.magasin.items():
        if k[0] in PL.MOYENNES:
            iv = PL.intervalles_quantite(q, choix, an.reglages.B)
            lignes.append(dict(type_suite="moyenne des configurations délégables", ligne=" ".join(map(str, k[1:])),
                               mesure=k[0], valeur=q.centre, lo=iv["retenue"][0], hi=iv["retenue"][1],
                               methode=iv["methode_effective"], lo_seconde=iv["seconde"][0],
                               hi_seconde=iv["seconde"][1], G=q.G))
    return lignes


def lignes_ecart(versions: dict, config) -> list:
    """Écart de délégation (5.12, point 4) : versions = {nom: {(env, modèle): classes}} ; principal, non plafonnées,
    verdicts bruts, calibration réunie à la confirmation."""
    lignes = []
    for version, par_conf in versions.items():
        for (env, mod), cl in sorted(par_conf.items()):
            for k, c in (cl or {}).items():
                niv = TY.niveau(k)
                b = float(config.barres[(env, niv)])
                cert = CR.certification(config.barres[(env, niv)])
                bb = c.get("beta_binomiale", {})
                lignes.append(dict(version=version, environnement=env, modele=mod, type=TY.SIGLES[k], niveau=niv,
                                   n=c["n"], x=c["x"], reussites=c.get("reussites", ""), taux=c["p"],
                                   n_eff=c["n_eff"], x_eff=c["x_eff"], borne_basse=c["lo"], borne_haute=c["hi"],
                                   barre=b, taux_sur_barre=c["p"] / b if c["n"] else float("nan"),
                                   borne_haute_sur_barre=c["hi"] / b, classe=c["classe"],
                                   n_eff_preuve=c.get("n_eff_preuve", ""),
                                   classe_sous_hypothese=c.get("classe_sous_hypothese", ""),
                                   borne_haute_sous_hypothese=c.get("hi_hyp", ""),
                                   taux_median=c.get("hi50", float("nan")),
                                   erreurs_attendues_a_la_barre=c["n_eff"] * b,
                                   jugeable=CL.jugeable(c), compte_pour_la_delegabilite=CL.estime_sous(c),
                                   borne_basse_sous_hypothese=c.get("lo_hyp", ""),
                                   depassement_etabli=CL.depassement_etabli(c), rho_bascule=CL.rho_bascule(c),
                                   statut=("délégable" if CL.estime_sous(c) else "dépassement établi"
                                           if CL.jugeable(c) and CL.depassement_etabli(c) else "ni l'un ni l'autre"),
                                   taches_pour_etablir_5_fois=CL.taches_pour_etablir(b, 5.0),
                                   taches_porteuses=c.get("n_taches", ""), m_bar=c.get("m_bar", ""),
                                   rho=c.get("rho", ""), source_rho=c.get("source_rho", ""),
                                   volume_certification=cert, n_eff_atteint_certification=c["n_eff"] >= cert,
                                   bb_mu=bb.get("mu", float("nan")), bb_rho=bb.get("rho", float("nan")),
                                   limite="lectures sans verdict : pas d'écart (Q12)"))
    return lignes


def lignes_garantie(an) -> list:
    choix = an.reglages.choix
    lignes = []
    for k, q in an.magasin.items():
        if k[0] != "garantie":
            continue
        cm, regle, typ = k[1:-2], k[-2], k[-1]
        iv = PL.intervalles_quantite(q, choix, an.reglages.B)
        lignes.append(dict(**_fam(cm), regle=regle, type=typ, phase="après la jonction" if cm[0] == "scenario"
                           else "configuration constante", part_rep_palier3=q.centre, lo=iv["retenue"][0],
                           hi=iv["retenue"][1], methode=iv["methode_effective"], lo_seconde=iv["seconde"][0],
                           hi_seconde=iv["seconde"][1], seuil=0.05,
                           note="mesurée sans seuil (décision 5) ; classe « au-dessus » au jeu de calibration"))
    return lignes


def lignes_r0(an, cle_r0: str, extra: dict = None) -> list:
    out = []
    for cm, r in an.resume_r0.items():
        for d in r.get(cle_r0, []):
            l = dict(analyse=an.nom, **_fam(cm))
            l.update({k: v for k, v in d.items() if k not in l})
            if extra:
                l.update(extra)
            out.append(l)
    return out


def lignes_resistance(modes: dict, alertes: list) -> list:
    """modes = {nom du mode: (analyse, e)} : cellules des quatre règles, et bilan de l'alerte 4.5."""
    lignes = []
    for mode, (an, e) in modes.items():
        for regle in an.reglages.noms_regles:
            for c in DE.cellules(an, regle, e):
                if c["statut"] != DE.JUGEE:
                    continue
                lignes.append(dict(mode=mode, **_fam(c["famille"]), regle=regle, e=e, niveau=c["niveau"],
                                   exces_100_ecritures=c["centre"], budget=c["budget"], lo=c["lo"], hi=c["hi"],
                                   verdict=c["verdict"], etabli=c.get("etabli", ""), rapport_hi=c["hi"] / c["budget"] if c["hi"] == c["hi"]
                                   else float("nan")))
        for regle, (n, w) in DE.bilan_mode(an, e).items():
            lignes.append(dict(mode=mode, type_suite="bilan du mode", regle=regle, echecs=n, pire_rapport_hi=w,
                               alerte=any(a["mode"] == mode for a in alertes) if regle == "B-tout" else ""))
    return lignes


def lignes_reussite(entrees, jeux: dict, B: int = 2000, graine: int = 0) -> list:
    """Taux de tâches réussies (point 10 ; 5.13) : réunion de Wilson (sur les parties) et du bootstrap par tâches."""
    lignes = []
    for nom_jeu, taches_par_env in jeux.items():
        for env, taches in taches_par_env.items():
            for mod in CR.MODELES:
                # graine du schéma SeedSequence, usage « reussite » (audit du moteur, 09/11 ; plan 5.5, point 4)
                rng = np.random.default_rng(SU.graine(graine, "reussite", env, mod, couche="bootstrap", jeu=nom_jeu))
                ps = [p for p in entrees.parties if p.environnement == env and p.modele == mod
                      and p.tache in set(taches) and p.statut_ok and not entrees.retiree(p) and p.reussie is not None]
                n = len(ps)
                k = sum(1 for p in ps if p.reussie)
                if n == 0:
                    continue
                p_, z2 = k / n, Z95 ** 2
                den = 1 + z2 / n
                ctr = (p_ + z2 / (2 * n)) / den
                demi = Z95 * math.sqrt(p_ * (1 - p_) / n + z2 / (4 * n * n)) / den
                par_t = {}
                for p in ps:
                    par_t.setdefault(p.tache, []).append(1.0 if p.reussie else 0.0)
                ts = list(par_t)
                # bootstrap stratifié comme le reste (environnement, fichier pour WorkBench ; 5.5, point 2.i)
                strates = {}
                for t in sorted(ts):
                    strates.setdefault(EN.strate(env, t), []).append(t)
                s_tot, n_tot = np.zeros(B), np.zeros(B)
                for _s, tt in sorted(strates.items()):
                    sommes = np.array([sum(par_t[t]) for t in tt])
                    nombres = np.array([len(par_t[t]) for t in tt])
                    tirs = rng.integers(0, len(tt), size=(B, len(tt)))
                    s_tot += sommes[tirs].sum(axis=1)
                    n_tot += nombres[tirs].sum(axis=1)
                boot = s_tot / n_tot
                lb, hb = np.quantile(boot, 0.025), np.quantile(boot, 0.975)
                lignes.append(dict(jeu=nom_jeu, environnement=env, modele=mod, parties=n, reussies=k, taux=p_,
                                   lo_wilson=max(0.0, ctr - demi), hi_wilson=min(1.0, ctr + demi), lo_bootstrap=lb,
                                   hi_bootstrap=hb, lo=min(max(0.0, ctr - demi), lb), hi=max(min(1.0, ctr + demi), hb),
                                   taches=len(ts)))
    return lignes


def lignes_choix(rc: dict) -> list:
    out = [dict(regle=r, **e, retenue=(r == rc["retenue"])) for r, e in rc["etat"].items()]
    out.append(dict(regle="(résultat)", retenue=rc["retenue"], motif=rc["motif"],
                    note="résultat secondaire : ne change pas la règle principale (1.3, point 4)"))
    return out


def _r(x):
    return "—" if x is None else round(float(x), 3)


def lignes_point4(p4: dict) -> list:
    """Point 4 (5.14 ; amendement R4, Otsoa, 07/11) : configurations délégables, puis dépassement établi à ρ = 1 dans
    chaque configuration jugeable (R4) ou motif de « preuves insuffisantes », avec ρ* et le ρ̂ propre des configurations
    non établies (publiés, jamais comme preuve)."""
    out = [dict(element="point 4 : configurations délégables", valeur="au moins une" if p4["tenu"] else "aucune",
                detail=" ; ".join(f"{e}/{m}" for e, m in p4["delegables"]))]
    if p4["tenu"]:
        valeur = "sans objet (au moins une configuration délégable)"
    else:
        valeur = "oui" if p4.get("etablie") else "non : " + p4.get("motif", "")
    detail = []
    for (e, m), d in p4.get("details", {}).items():
        bascule = d.get("rho_bascule")
        quand = f"établi si ρ < {_r(bascule)}" if bascule is not None else "non établi, même à ρ = 0"
        propre = f"ρ̂ propre {_r(d.get('rho_propre'))}" if d.get("rho_propre") is not None else "pas de ρ̂ propre"
        detail.append(f"{e}/{m} : {quand} ({propre}, lecture à ρ = {_r(d.get('rho_lecture'))})")
    if p4.get("jugeable") and p4.get("sans_type_jugeable"):   # R4 ne dit rien d'elles (plan, 1.5)
        detail.append("hors du constat, aucun type jugeable : "
                      + ", ".join(f"{e}/{m}" for e, m in p4["sans_type_jugeable"]))
    out.append(dict(element="point 4 : dépassement établi dans chaque configuration jugeable (R4)", valeur=valeur,
                    detail=" ; ".join(detail)))
    return out


def detail_point1(p1: dict) -> str:
    """Détail de la ligne du point 1 (la mention O4 b y figure d'office quand la famille du max-T est petite)."""
    cel1 = p1["cellules"]
    return (f"{len(cel1)} cellules : {sum(c['statut'] == DE.JUGEE for c in cel1)} jugées, dont "
               f"{sum(bool(c.get('non_testable')) for c in cel1)} non testables (hors du max-T, 5.14), "
               f"{sum(c['statut'] == DE.NON_EPROUVEE for c in cel1)} tenues non mises à l'épreuve, "
               f"{sum(c['statut'] == DE.SANS_OBJET for c in cel1)} sans objet ; dépassements établis : "
               f"{len(p1['echecs'])} ; démontrées : {sum(bool(c.get('demontree')) for c in cel1)} ; "
               f"garantie hors hypothèse : {sum(bool(c.get('garantie_hors_hypothese')) for c in cel1)}"
               + (f" ; famille du max-T : {p1['testables']} cellule(s) testable(s), {p1['mention_famille']}"
                  if p1.get("mention_famille") else ""))


def lignes_decision(dec: dict) -> list:
    out = [dict(element="étiquette finale", valeur=dec["etiquette"] + (f" ({dec['mention']})" if dec.get("mention")
                                                                          else ""),
                detail=dec.get("motif_etiquette", ""))]
    p0 = dec["principale"]["point0"]
    out.append(dict(element="point 0 : validité de l'instrument", valeur="tenu" if p0["tenu"] else "non tenu",
                    detail=f"couverture {p0['couverture']:.4f} (seuil {p0['seuil']}) ; vagues : "
                           + " ; ".join(f"{v} : {c}" for v, c in p0["vagues"].items())))
    p1 = dec["principale"]["point1"]
    cel1 = p1["cellules"]
    out.append(dict(element="point 1 : éliminatoire (B-tout, dépassement établi par max-T, Q13)",
                    valeur="tenu" if p1["tenu"] else "non tenu (R1)", detail=detail_point1(p1)))
    out.append(dict(element="contrôle du code : critère de retrait de la décision 5 (scénarios)",
                    valeur="tenu" if not p1["defauts_retrait"] else "DÉFAUT DU CODE",
                    detail=f"{len(p1['defauts_retrait'])} période(s) à plus d'une erreur constatée"))
    p2 = dec["principale"]["point2"]
    for t, d in p2["temoins"].items():
        cel_t = d["depassement"]["cellules"]
        distinctes = len({(tuple(c["famille"][:-1]) if c["famille"][0] == "scenario" else tuple(c["famille"]),
                           c["niveau"]) for c in cel_t})   # un scénario figure dans ses deux modes (C13, M7)
        sec = d.get("intervalle_seconde", (float("nan"), float("nan")))
        out.append(dict(element=f"point 2 : témoin {t}", valeur="battu" if d["battu"] else "non battu",
                        detail=f"dépassement établi (max-T) : {len(d['depassement']['etablies'])} sur "
                               f"{d['depassement']['m']} cellules ({distinctes} suites distinctes), dont "
                               f"{sum(bool(c.get('non_testable')) for c in d['depassement']['cellules'])} non "
                               f"testable(s), c* = {d['depassement']['c_etoile']} ; "
                               f"différence de charge moyenne {d['diff_moyenne']} [{d['intervalle'][0]} ; "
                               f"{d['intervalle'][1]}] ; seconde méthode [{sec[0]} ; {sec[1]}]"
                               + (" ; méthodes divergentes : fragile" if d.get("methodes_divergent") else "")))
    jugee = dec["principale"]["point4"]["tenu"]
    out.append(dict(element="point 2 : réussite (Q15 : « tout faire valider », puis les deux autres témoins)",
                    valeur=("tenu" if p2["tenu"] else f"non tenu ({p2.get('mention_r2', '')})") if jugee else
                    "non jugé (aucune configuration délégable, point 4)",
                    detail="les trois témoins battus (dépassement établi, ou charge moyenne inférieure)"))
    p3 = dec["principale"]["point3"]
    out.append(dict(element="point 3 : hasard au même rythme (sans effet sur l'étiquette)", valeur=p3["conclusion"],
                    detail=" ; ".join(f"{n} : {v['diff']} [{v['lo']} ; {v['hi']}]" for n, v in p3["niveaux"].items())
                    + (f" ; seconde méthode : {p3['conclusion_seconde']}" if p3.get("conclusion_seconde") else "")
                    + (" ; méthodes divergentes : fragile" if p3.get("methodes_divergent") else "")))
    out.extend(lignes_point4(dec["principale"]["point4"]))
    for nom, v in dec.get("etiquettes_secondaires", {}).items():
        out.append(dict(element=f"point 6 : étiquette, {nom}", valeur=v, detail="sans effet sur le verdict"))
    for nom, liste in dec.get("desaccords", {}).items():
        out.append(dict(element=f"point 6 : désaccords de cellules, {nom}", valeur=len(liste),
                        detail=" ; ".join(f"{c[0]} {c[1]}" for c in liste[:20]) + (" …" if len(liste) > 20 else "")))
    for f in dec.get("fragiles", []):
        out.append(dict(element="mention « fragile »", valeur="fragile", detail=f))
    out.append(dict(element="alerte des tests de résistance (5.11)", valeur="oui" if dec.get("alertes") else "non",
                    detail=" ; ".join(f"{a['mode']} : {a['echecs_regle']} échec(s) contre {a['echecs_autre']} pour "
                                      f"{a['autre']}, pire {a['pire_regle']:.2f} contre {a['pire_autre']:.2f}"
                                      for a in dec.get("alertes", []))))
    if dec.get("b2"):
        b2 = dec["b2"]
        out.append(dict(element="désaccord persistant (B2)", valeur=b2["etiquette_bruts_vague"],
                        detail=f"vagues {b2['vagues']} ; étiquette retenue : la moins favorable ; mention des verdicts "
                               f"bruts : {b2.get('mention_bruts_vague', '') or '—'} ; leurs points : "
                               f"{b2.get('points_bruts_vague', {})}"))
    ins = dec.get("instrument")
    if ins:
        out.append(dict(element="instrument : alertes (5.12, point 11)", valeur=ins["alertes"],
                        detail=f"confirmées {ins['confirmees']} ; levées {ins['levees']} ("
                               + ", ".join(f"motif {k} : {v}" for k, v in sorted(ins["levees_par_motif"].items()))
                               + f") ; décisions obsolètes {ins['obsoletes']} ; sans décision {ins['sans_decision']}"))
        out.append(dict(element="instrument : couverture (part d'écritures vérifiables ; ce n'est pas d)",
                        valeur=ins["couverture"], detail=f"hors effet illisible : {ins['couverture_hors_illisible']}"))
        out.append(dict(element="instrument : tâches retirées (motif a et liste)", valeur=len(ins["taches_retirees"]),
                        detail=" ; ".join(f"{k} : {v}" for k, v in ins["taches_retirees"].items())))
    return out


# --------------------------------------------------------------------------
# meta.json et RESULTATS.md
# --------------------------------------------------------------------------
def sha256_fichier(chemin: str):
    if not chemin or not os.path.exists(chemin):
        return None
    with open(chemin, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def empreintes_code() -> dict:
    return {n: sha256_fichier(os.path.join(_ICI, n)) for n in sorted(os.listdir(_ICI)) if n.endswith(".py")}


_ICI = os.path.dirname(os.path.abspath(__file__))


def ecrire_meta(dossier: str, meta: dict, avertissement: str = None) -> str:
    m = dict(meta)
    if avertissement:
        m = dict(avertissement=avertissement, **m)
    m.update(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__,
             machine=platform.platform(), ecrit_le=time.strftime("%Y-%m-%d %H:%M:%S %z"),
             empreintes_code=empreintes_code())
    chemin = os.path.join(dossier, "meta.json")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1, default=str)
        f.write("\n")
    return chemin


def _f(x, nd=3):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    if math.isnan(v):
        return "—"
    if math.isinf(v):
        return "∞" if v > 0 else "−∞"
    return f"{v:.{nd}f}".replace(".", ",")


def _table(entete, lignes) -> str:
    s = "| " + " | ".join(entete) + " |\n|" + "---|" * len(entete) + "\n"
    for l in lignes:
        s += "| " + " | ".join(str(x) for x in l) + " |\n"
    return s + "\n"


def lignes_symetrie(entrees, cal: dict, conf: dict) -> list:
    """Comparaison descriptive des deux moitiés du partage, sans test ni seuil (plan, 4.5 ; relecture C13, P16) : par
    environnement et par moitié, tâches, tâches retirées, tâches jouées (au moins une partie gardée) et écritures par
    niveau d'enjeu."""
    jouees = {(p.environnement, str(p.tache)) for p in entrees.parties if p.statut_ok}
    ecritures = {}
    for actions in entrees.actions.values():
        for a in actions:
            if a.kind == "écriture" and a.enjeu:
                cle = (a.environnement, str(a.tache), a.enjeu)
                ecritures[cle] = ecritures.get(cle, 0) + 1
    retirees = {(e, str(t)) for e, t in entrees.taches_retirees}
    out = []
    for env in sorted(set(cal) | set(conf)):
        for moitie, jeu in (("calibration", cal), ("confirmation", conf)):
            taches = [str(t) for t in jeu.get(env, [])]
            l = dict(environnement=env, moitie=moitie, taches=len(taches),
                     taches_retirees=sum((env, t) in retirees for t in taches),
                     taches_jouees=sum((env, t) in jouees for t in taches))
            for niv in TY.NIVEAUX:
                l[f"ecritures_{niv}"] = sum(ecritures.get((env, t, niv), 0) for t in taches)
            out.append(l)
    return out


def ecrire_rapport(dossier: str, avertissement: str = None) -> str:
    """RESULTATS.md, écrit à partir des CSV du dossier (5.15)."""
    dec = lire_csv(dossier, "decision")
    bud = [l for l in lire_csv(dossier, "budget") if l.get("eliminatoire") == "True"]
    with open(os.path.join(dossier, "meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    s = "# Rejeu de l'expérience « autonomie méritée » : résultats\n\n"
    if avertissement:
        s += f"> **AVERTISSEMENT.** {avertissement}\n\n"
    s += (f"Écrit le {meta.get('ecrit_le')} par `simulation/rejeu/sorties.py`, à partir des CSV de ce dossier. "
          f"R0 = {meta.get('R0')}, B = {meta.get('B')}, K = {meta.get('K')} ; méthode d'intervalle : "
          f"{meta.get('methode_intervalle', {}).get('nom', '')} (simulation de couverture : "
          f"`{meta.get('methode_intervalle', {}).get('source') or 'simulation/rejeu/resultats_couverture_charge'}/`)."
          "\n\n")
    s += "## Règle de décision (PLAN_EXPERIENCE.md, 5.14)\n\n"
    s += _table(["élément", "valeur", "détail"], [(l["element"], l["valeur"], l["detail"]) for l in dec])
    s += "## Cellules éliminatoires de B-tout (e = 5 %, budget par écriture)\n\n"
    rows = []
    for l in bud:
        fam = l["environnement"] + " / " + l["modele"] + ((" → " + l["modele_Y"] + " (" + l["mode"] + ")")
                                                            if l["type_suite"] == "scénario" else "")
        rows.append((fam, l["niveau"], l["statut"], _f(l["exces_100_ecritures"], 4), _f(l["budget"], 3),
                     f"[{_f(l['lo'], 4)} ; {_f(l['hi'], 4)}]", _f(l.get("borne_construction"), 4),
                     f"{_f(l.get('s_sur_q'), 2)} [{_f(l.get('s_sur_q_lo'), 2)} ; {_f(l.get('s_sur_q_hi'), 2)}]",
                     l.get("demontree", ""), l.get("garantie_hors_hypothese", ""), l.get("fragile", ""),
                     l.get("taches_porteuses", ""), l.get("non_testable", "")))
    s += _table(["suite", "niveau", "statut", "dégâts en plus / 100 écritures", "budget", "intervalle descriptif",
                 "borne de construction", "s ÷ q", "démontrée", "garantie hors hypothèse", "fragile",
                 "tâches porteuses", "non testable (motif)"], rows)
    s += "## Fichiers\n\n"
    for n in FICHIERS:
        s += f"- `{n}.csv` : {len(lire_csv(dossier, n))} lignes\n"
    s += "- `meta.json` : graines, versions, empreintes des entrées et du code\n"
    chemin = os.path.join(dossier, "RESULTATS.md")
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(s)
    return chemin
