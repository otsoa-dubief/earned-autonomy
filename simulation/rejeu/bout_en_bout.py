"""Rejeu de bout en bout (PLAN_EXPERIENCE.md, 5.14 à 5.16) : toutes les analyses, la règle de décision et les sorties.

Usage (depuis simulation/) :
    .venv/bin/python -m rejeu.bout_en_bout --pilote [--sortie DOSSIER] [--R0 N] [--B N] [--K N]

Sur le pilote (5.16, point 6) : les 120 parties de développement de `pilote/etape2/2026-11-05_07-50-58/`, avec un
partage fictif calculé par `banc/tirage/tirage_public.py` (`graine` puis `partager`) à partir d'une valeur de balise de
TEST, écrite ci-dessous : aucune balise réelle n'est interrogée, aucun réseau. Ces chiffres n'ont aucune valeur de
preuve ; chaque sortie le dit en tête.

Déroulé (5.14) :
1. analyse principale : verdicts confirmés, calibration → confirmation, configurations et scénarios ;
2. points 0 à 4 et étiquette ; désaccord persistant (B2) : la même analyse avec les verdicts bruts pour les vagues
   concernées, et l'étiquette la moins favorable des deux ;
3. analyses secondaires (point 6) : verdicts bruts (Q11), toute la réserve (verdict éliminatoire), échange des rôles
   (Q1), tests de résistance (rate10, retard10, ratées groupées ; e = 0, 2 et 10 %), sensibilités à l'ordre (Q5) ;
   « fragile » en cas de désaccord ;
4. écart de délégation, taux de tâches réussies, règle de choix réappliquée ; sorties (5.15).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

from . import RACINE
from . import analyse as AN
from . import classes as CL
from . import config_rejeu as CR
from . import couverture as CO
from . import couverture_charge as CC
from . import decision as DE
from . import entrees as EN
from . import intervalles as IC
from . import pipeline as PL
from . import preuves as PR
from . import sorties as SO
from . import suites as SU
from . import types_regle as TY

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PILOTE = os.path.join(RACINE, "pilote", "etape2", "2026-11-05_07-50-58")
SORTIE_PILOTE = os.path.join(ICI, "sorties_pilote")
MANIFESTE_TEST = hashlib.sha256(b"autonomie-meritee/pilote/manifeste-de-test").hexdigest()
BALISE_TEST = hashlib.sha512(b"autonomie-meritee/pilote/balise-de-test : pas une vraie balise").hexdigest()
AVERTISSEMENT_PILOTE = (
    "bout en bout sur les 120 parties de développement du pilote (pilote/etape2/2026-11-05_07-50-58/), avec un partage "
    "fictif calculé par banc/tirage/tirage_public.py à partir d'une valeur de balise de test (aucune balise réelle "
    "interrogée). Ces chiffres n'ont AUCUNE valeur de preuve et ne sont pas des résultats de l'expérience "
    "(PLAN_EXPERIENCE.md, 3.1 et 5.16, point 6).")


def partage_par_env(partage: dict) -> tuple:
    """{env: tâches} de calibration et de confirmation, à partir d'un partage par strates."""
    cal, conf = {}, {}
    for jeu, sortie in (("calibration", cal), ("confirmation", conf)):
        for s, ids in partage[jeu].items():
            env = s.split(":")[0]
            sortie.setdefault(env, []).extend(str(t) for t in ids)
    return {e: sorted(v) for e, v in cal.items()}, {e: sorted(v) for e, v in conf.items()}


def partage_pilote(entrees) -> dict:
    import tirage_public as TP
    reserve = {}
    for p in entrees.parties:
        reserve.setdefault(p.environnement, set()).add(p.tache)
    reserve = {e: sorted(v) for e, v in reserve.items()}
    return TP.partager(reserve, TP.graine(MANIFESTE_TEST, BALISE_TEST))


def ecart_versions(an_p, an_bruts, entrees, prep, config, cal, conf) -> dict:
    """Écart de délégation (5.12, point 4) : principal (toutes les écritures, plafonnées comprises), non plafonnées,
    verdicts bruts, calibration réunie à la confirmation ; modèle bêta-binomial descriptif sur la version principale."""
    versions = {"principal": dict(an_p.classes_cal)}
    for (env, mod), cl in versions["principal"].items():
        jk = an_p.jeux_cal.get((env, mod))
        for k, c in (cl or {}).items():
            pt = CL.comptes_par_tache(jk, (k,)) if jk is not None else {}
            if pt:
                m, x = zip(*pt.values())
                c["beta_binomiale"] = CL.beta_binomiale(m, x)
    jks = {}
    for (env, m), j in an_p.jeux_cal.items():
        jks.setdefault(env, {})[m] = j
    versions["non plafonnées"] = {(env, m): cl for env, d in CL.classes_tous_environnements(jks, config, False).items()
                                  for m, cl in d.items()}
    if an_bruts is not None:
        versions["verdicts bruts"] = dict(an_bruts.classes_cal)
    ju = {env: {m: SU.jeu_configuration(prep, entrees, env, m, sorted(set(cal[env]) | set(conf.get(env, []))),
                                        "reserve") for m in CR.MODELES} for env in sorted(cal)}
    versions["calibration et confirmation"] = {(env, m): cl for env, d in
                                               CL.classes_tous_environnements(ju, config).items()
                                               for m, cl in d.items()}
    return versions


def executer(entrees, cal: dict, conf: dict, reglages: AN.Reglages, dossier: str, avertissement: str = None,
             secondaires: bool = True, meta_entrees: dict = None, journal=print, processus: int = 1) -> dict:
    """Toutes les analyses, la décision et les sorties ; rend la décision."""
    os.makedirs(dossier, exist_ok=True)
    debut = time.time()
    config = CR.charger_config()
    prep = PR.preparer(entrees, "confirmes")
    log = lambda m: journal(f"[{time.time() - debut:7.1f} s] {m}") if journal else None  # noqa: E731

    log("analyse principale")
    an = PL.analyser(entrees, prep, config, reglages, conf, cal, processus=processus, nom="principale")
    p0 = DE.point0(entrees, prep)
    dec_p = DE.decider(an, p0)
    etiquette = dec_p["etiquette"]
    dec = dict(principale=dec_p, etiquette=etiquette, mention=dec_p["mention"], etiquettes_secondaires={},
               desaccords={}, fragiles=[], motif_etiquette="étiquette de l'analyse principale",
               instrument=DE.instrument(entrees, prep))
    analyses = {"principale": an}
    # « fragile » quand la seconde méthode conclut autrement (5.13, B4 ; relecture C13, M2)
    for t, v in dec_p["point2"]["temoins"].items():
        if v.get("methodes_divergent"):
            dec["fragiles"].append(f"point 2, témoin {t} : la méthode retenue et la seconde méthode ne concluent pas "
                                   "de même sur la charge")
    if dec_p["point3"].get("methodes_divergent"):
        dec["fragiles"].append("point 3 : la méthode retenue et la seconde méthode ne concluent pas de même")
    # désaccord persistant (B2)
    if p0["persistantes"]:
        log("désaccord persistant : verdicts bruts pour les vagues " + ", ".join(p0["persistantes"]))
        prep_bv = PR.preparer(entrees, "bruts_vague", p0["persistantes"])
        an_bv = PL.analyser(entrees, prep_bv, config, reglages, conf, cal, processus=processus, nom="bruts_vague")
        d_bv = DE.decider(an_bv, DE.point0(entrees, prep_bv))
        comb = DE.combiner_b2(dec_p, d_bv)
        dec["b2"] = dict(vagues=p0["persistantes"], **{k: comb[k] for k in ("etiquette_bruts_vague",
                                                                            "mention_bruts_vague",
                                                                            "points_bruts_vague")})
        etiquette = comb["etiquette"]
        dec["mention"] = comb["mention"]
        dec["etiquette"] = etiquette
        dec["motif_etiquette"] = "désaccord persistant (B2) : la moins favorable des deux étiquettes"
        analyses["bruts_vague"] = an_bv
    cel_p = dec_p["point1"]["cellules"]
    for c in cel_p:
        if c["fragile"]:
            dec["fragiles"].append(f"cellule {c['famille']} {c['niveau']} : " + ", ".join(c["fragile"]))
    an_b = None
    resistance_modes = {f"e = {e:g}": (an, e) for e in reglages.valeurs_e[1:]}
    if secondaires:
        prep_b = PR.preparer(entrees, "bruts")
        log("verdicts bruts (Q11)")
        an_b = PL.analyser(entrees, prep_b, config, reglages, conf, cal, processus=processus, nom="verdicts bruts")
        dec_b = DE.decider(an_b, DE.point0(entrees, prep_b))
        dec["etiquettes_secondaires"]["verdicts bruts"] = dec_b["etiquette"]
        dec["desaccords"]["verdicts bruts"] = DE.desaccords(cel_p, dec_b["point1"]["cellules"])
        analyses["verdicts bruts"] = an_b
        resistance_modes["verdicts bruts"] = (an_b, reglages.e_principal)
        if dec_b["etiquette"] != dec_p["etiquette"]:
            dec["fragiles"].append(f"étiquette : {dec_p['etiquette']} (confirmés) contre {dec_b['etiquette']} (bruts), "
                                   "Q11")
        log("toute la réserve (verdict éliminatoire)")
        reserve = {e: sorted(set(cal.get(e, [])) | set(conf.get(e, []))) for e in set(cal) | set(conf)}
        an_r = PL.analyser(entrees, prep, config, reglages, reserve, None, processus=processus, nom="toute la réserve", nom_jeu="reserve")
        p1_r = DE.point1(an_r)
        dec["etiquettes_secondaires"]["toute la réserve (point 1)"] = ("non calculé" if p1_r["tenu"] is None else
                                                                        "tenu" if p1_r["tenu"] else "non tenu (R1)")
        dec["desaccords"]["toute la réserve"] = DE.desaccords(cel_p, p1_r["cellules"])
        analyses["toute la réserve"] = an_r
        log("échange des rôles (Q1)")
        an_e = PL.analyser(entrees, prep, config, reglages, cal, conf, processus=processus, nom="échange (pli inverse)",
                           nom_jeu="calibration")
        an_c = DE.combiner_echange(an, an_e)
        dec_c = DE.decider(an_c, p0)
        dec["etiquettes_secondaires"]["échange des rôles"] = dec_c["etiquette"]
        dec["desaccords"]["échange des rôles"] = DE.desaccords(cel_p, dec_c["point1"]["cellules"])
        analyses["échange des rôles"] = an_c
        for nom, liste in dec["desaccords"].items():
            for k in liste:
                dec["fragiles"].append(f"cellule {k[0]} {k[1]} : désaccord avec « {nom} »")
        for mode in ("rate10", "retard10", "groupees"):
            log(f"test de résistance {mode}")
            an_m = PL.analyser(entrees, prep, config, reglages, conf, cal, processus=processus, nom=f"résistance {mode}",
                               resistance=mode)
            resistance_modes[mode] = (an_m, reglages.e_principal)
        for ordre in ("par_passage", "reel"):
            log(f"sensibilité à l'ordre ({ordre})")
            analyses[f"ordre {ordre}"] = PL.analyser(entrees, prep, config, reglages, conf, cal, processus=processus,
                                                     nom=f"ordre {ordre}", scenarios=False, ordre=ordre,
                                                     bootstrap=False, jackknife=False)
    an_l = None
    if secondaires:
        log("lettre d'origine (Q8, lecture A : barres et N du point 8, dégâts pour 100 actions)")
        reg_l = AN.Reglages(**{**reglages.__dict__, "noms_regles": ("B-tout-lettre",)})
        an_l = PL.analyser(entrees, prep, config, reg_l, conf, cal, processus=processus,
                           nom="lettre d'origine (Q8 A)")
        cel_l = DE.cellules(an_l, "B-tout-lettre", cle_q="budget_actions")
        dec["etiquettes_secondaires"]["lettre d'origine (Q8 A), point 1"] = \
            "tenu" if not any(c["verdict"] == DE.ETABLI for c in cel_l) else "non tenu (dépassement établi)"
    bilans = {m: DE.bilan_mode(a, e) for m, (a, e) in resistance_modes.items()}
    dec["alertes"] = DE.alerte_resistance(bilans)
    rc = DE.regle_de_choix(an)
    log("sorties")
    av = avertissement
    SO.ecrire_csv(dossier, "budget", SO.lignes_budget(analyses, dec_p) + (SO.lignes_lettre(an_l) if an_l else []),
                  av)
    SO.ecrire_csv(dossier, "charges", SO.lignes_charges(an), av)
    SO.ecrire_csv(dossier, "ecart", SO.lignes_ecart(ecart_versions(an, an_b, entrees, prep, config, cal, conf),
                                                    config), av)
    SO.ecrire_csv(dossier, "garantie", SO.lignes_garantie(an), av)
    SO.ecrire_csv(dossier, "retrait", SO.lignes_r0(an, "retrait"), av)
    derive = SO.lignes_r0(an, "derive", dict(mode_resistance="aucun (constat immédiat)"))
    if "retard10" in resistance_modes:
        derive += SO.lignes_r0(resistance_modes["retard10"][0], "derive", dict(mode_resistance="retard10"))
    SO.ecrire_csv(dossier, "derive", derive, av)
    SO.ecrire_csv(dossier, "resistance", SO.lignes_resistance(resistance_modes, dec["alertes"]), av)
    SO.ecrire_csv(dossier, "volume", SO.lignes_r0(an, "autonomie"), av)
    SO.ecrire_csv(dossier, "epreuves", SO.lignes_r0(an, "epreuves"), av)
    SO.ecrire_csv(dossier, "reussite_taches", SO.lignes_reussite(entrees, {"calibration": cal, "confirmation": conf},
                                                                 B=reglages.B, graine=reglages.G0), av)
    SO.ecrire_csv(dossier, "choix", SO.lignes_choix(rc), av)
    SO.ecrire_csv(dossier, "decision", SO.lignes_decision(dec), av)
    SO.ecrire_csv(dossier, "symetrie", SO.lignes_symetrie(entrees, cal, conf), av)   # relecture C13, P16
    choix = reglages.choix
    meta = dict(G0=reglages.G0, R0=reglages.R0, B=reglages.B, K=reglages.K, valeurs_e=reglages.valeurs_e,
                methode_intervalle=dict(retenue=choix["methode"], nom=IC.NOMS_METHODES[choix["methode"]],
                                        seconde=choix.get("methode_seconde"), repli=choix.get("repli"),
                                        G_sur=str(choix.get("G_sur")), zone_echec=choix.get("zone_echec"),
                                        source=choix.get("source", ""),
                                        historique="resultats_couverture/ (première simulation, dégâts rares)"),
                etiquette=dec["etiquette"], processus=processus,
                config_rejeu_sha256=SO.sha256_fichier(CR.CHEMIN_CONFIG),
                table_outils_sha256=SO.sha256_fichier(CR.CHEMIN_TABLE_OUTILS),
                partage=dict(calibration=cal, confirmation=conf), duree_s=round(time.time() - debut, 1))
    meta.update(meta_entrees or {})
    SO.ecrire_meta(dossier, meta, av)
    SO.ecrire_rapport(dossier, av)
    log(f"étiquette : {dec['etiquette']}")
    return dec


def entrees_et_partage_pilote() -> tuple:
    entrees = EN.charger_entrees(DOSSIER_PILOTE)
    part = partage_pilote(entrees)
    cal, conf = partage_par_env(part)
    meta = dict(entrees=dict(
        dossier=os.path.relpath(DOSSIER_PILOTE, RACINE),
        actions_typees_sha256=SO.sha256_fichier(os.path.join(DOSSIER_PILOTE, "actions_typees.csv")),
        cout_sha256=SO.sha256_fichier(os.path.join(DOSSIER_PILOTE, "cout.json")),
        reussite_sha256=SO.sha256_fichier(os.path.join(DOSSIER_PILOTE, "reussite.csv")),
        decisions_sha256=SO.sha256_fichier(os.path.join(DOSSIER_PILOTE, "relecture", "decisions.csv")),
        alertes_sha256=SO.sha256_fichier(os.path.join(DOSSIER_PILOTE, "relecture", "alertes.json")),
        partage_fictif=dict(manifeste_test=MANIFESTE_TEST, balise_test=BALISE_TEST,
                            script="banc/tirage/tirage_public.py (graine, partager)"),
        taches_retirees=sorted(map(list, entrees.taches_retirees))))
    return entrees, cal, conf, meta


def choix_methode() -> dict:
    """Méthode des intervalles : celle de la simulation refaite sur la différence appariée de charge (Q13, phase 3)."""
    c = CO.lire_choix(CC.DOSSIER)
    c["source"] = os.path.relpath(CC.DOSSIER, RACINE)
    return c


def _charger(nom: str, chemin: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _module_gel():
    """gel/manifeste.py (manifeste du gel du plan), chargé par son chemin."""
    return _charger("gel_manifeste", os.path.join(RACINE, "gel", "manifeste.py"))


def _module_manifeste_verdicts():
    """gel/manifeste_verdicts.py (manifeste du gel des verdicts), chargé par son chemin."""
    return _charger("gel_manifeste_verdicts", os.path.join(RACINE, "gel", "manifeste_verdicts.py"))


def controles_experience(dossiers, partage: str, vagues: list, retirees, sortie: str, manifeste_verdicts: str,
                         oppositions: str = None) -> list:
    """Refus du rejeu final réel, avant tout calcul (relecture C13, P1 et P3 ; plan 3.4, 5.2 et 5.14) : dépôt conforme
    au manifeste du gel du plan ; manifeste des verdicts égal à celui du tirage ; toute entrée lue inscrite au
    manifeste avec la même empreinte ; réussite des tâches déjà calculée ; dossier de sortie vide."""
    from pathlib import Path
    refus = [f"le dépôt diffère du manifeste du gel du plan : {e}" for e in _module_gel().verifier(Path(RACINE))]
    mv = _module_manifeste_verdicts()
    with open(partage, encoding="utf-8") as f:
        attendue = json.load(f).get("empreinte_manifeste")
    if mv.sha256(manifeste_verdicts) != attendue:
        refus.append("le manifeste des verdicts donné n'est pas celui du tirage (empreinte_manifeste de partage.json)")
    lus = list(dossiers)
    for v in vagues:
        lus += [c for c in (v.decisions, v.alertes, v.bilan_otsoa) if c]
    lus += [f for f in (retirees, oppositions) if f]
    refus += [f"entrée non conforme au manifeste des verdicts : {e}" for e in mv.ecarts(manifeste_verdicts, lus)]
    refus += [f"{os.path.join(d, 'reussite.csv')} manque : la réussite des tâches se calcule au gel des verdicts "
              f"(gel/manifeste_verdicts.py), avant le tirage" for d in dossiers
              if not os.path.exists(os.path.join(d, "reussite.csv"))]
    if os.path.isdir(sortie) and os.listdir(sortie):
        refus.append(f"{sortie} n'est pas vide : le rejeu final tourne une seule fois, dans un dossier neuf")
    return refus


def noter_lancement(sortie: str, ligne: dict) -> None:
    """Journal des lancements du rejeu final, à côté du dossier de sortie (relecture C13, P3) : une ligne JSON par
    étape (début, fin), déposée avec les résultats."""
    chemin = os.path.join(os.path.dirname(os.path.abspath(sortie)), "journal_rejeu_final.jsonl")
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(heure=time.strftime("%Y-%m-%d %H:%M:%S %z"), sortie=os.path.abspath(sortie), **ligne),
                           ensure_ascii=False) + "\n")


def vague_depuis_texte(texte: str) -> EN.VagueRelecture:
    """« NOM=decisions.csv,alertes.json,accord.json » (alertes et bilan facultatifs : chaîne vide)."""
    nom, reste = texte.split("=", 1)
    parts = (reste.split(",") + ["", ""])[:3]
    return EN.VagueRelecture(nom, parts[0], parts[1] or None, parts[2] or None)


def meta_bilans(vagues: list) -> dict:
    """Ce que disent les bilans d'accord de chaque vague (lus sans être modifiés) : conclusion, désaccord persistant,
    décisions d'Otsoa (fortes levées comprises, déjà réunies par accord.py), relecture des fortes."""
    out = {}
    for v in vagues:
        d = dict(decisions=v.decisions, decisions_sha256=SO.sha256_fichier(v.decisions),
                 alertes=v.alertes, bilan=v.bilan_otsoa, bilan_sha256=SO.sha256_fichier(v.bilan_otsoa))
        if v.bilan_otsoa:
            with open(v.bilan_otsoa, encoding="utf-8") as f:
                b = json.load(f)
            d.update(conclusion=b.get("conclusion"), desaccord_persistant=b.get("desaccord_persistant"),
                     decisions_otsoa=len(b.get("decisions_otsoa", {})), fortes=b.get("fortes"))
        out[v.nom] = d
    return out


def _module_reussite():
    """banc/reussite.py, chargé par son chemin (aucun module homonyme ne peut le masquer)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("banc_reussite", os.path.join(RACINE, "banc", "reussite.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def preparer_reussite(dossiers) -> list:
    """`reussite.csv` de chaque dossier de vague, calculé ici s'il manque, par `banc/reussite.py` (état final, sans juge
    IA ; il écrit reussite.csv, .json et .txt dans le dossier, rien d'autre). Le lanceur ne le calcule pas : les taux de
    réussite sont interdits entre deux vagues (banc/CHOIX_LANCEUR.md) ; au rejeu final, toutes les vagues sont jouées.
    Calculé avant toute lecture des entrées et sans rien afficher (les taux se lisent dans les sorties) ; un échec
    arrête le rejeu avant tout calcul. Renvoie les dossiers où il a été calculé."""
    import contextlib
    import io
    faits = []
    for d in dossiers:
        if not os.path.exists(os.path.join(d, "reussite.csv")):
            module = _module_reussite()
            with contextlib.redirect_stdout(io.StringIO()):
                module.main(["--dossier", d])
            faits.append(d)
    return faits


def executer_experience(dossier, partage: str, vagues: list, sortie: str, retirees=None, processus: int = 1,
                        essai: bool = False, R0=None, B=None, K=None, tranche: int = 200,
                        manifeste_verdicts: str = None, retirees_fichier: str = None,
                        oppositions_fichier: str = None) -> dict:
    """Le rejeu final (5.14) : entrées du lanceur, partage du tirage public, bilans de relecture de chaque vague ; G0
    lue dans config_rejeu.json, refusée si elle vaut null ; R0, B et K figés dans config_rejeu.json (revue « ultra »,
    06/11). L'essai à blanc prend toujours la graine de développement, même après le tirage de G0, et peut réduire
    R0, B et K. La réussite des tâches est calculée d'abord si elle manque (`preparer_reussite`)."""
    cfg = CR.charger_config()
    if cfg.G0 is None and not essai:
        raise SystemExit("G0 vaut null dans config_rejeu.json : elle se tire au gel (gel/manifeste.py --tirer-g0)")
    for nom, v in (("R0", R0), ("B", B), ("K", K)):
        if v is not None and int(v) < 1:
            raise SystemExit(f"{nom} doit être un entier positif (reçu {v})")
    figees = dict(R0=cfg.R0, B=cfg.B, K=cfg.K)
    autres = {k: v for k, v in dict(R0=R0, B=B, K=K).items() if v is not None and v != figees[k]}
    if autres and not essai:   # revue « ultra » du 06/11, constat 3
        raise SystemExit(f"rejeu final : R0, B et K sont figés dans config_rejeu.json ({figees}) ; demandé : {autres}")
    G0 = cfg.G0 if not essai else cfg.G0_developpement   # constat 4 : jamais le vrai G0 hors de l'expérience réelle
    with open(partage, encoding="utf-8") as f:
        part = json.load(f)
    cal, conf = partage_par_env(part)
    dossiers = [dossier] if isinstance(dossier, str) else list(dossier)
    gel = None
    if not essai:   # relecture C13, P1 et P3 : rien ne tourne hors du code figé et des entrées gelées
        if not manifeste_verdicts:
            raise SystemExit("rejeu final : --manifeste-verdicts est obligatoire (gel/manifeste_verdicts.py)")
        refus = controles_experience(dossiers, partage, vagues, retirees_fichier, sortie, manifeste_verdicts,
                                     oppositions_fichier)
        if refus:
            raise SystemExit("rejeu final refusé :\n- " + "\n- ".join(refus))
        gel = _module_manifeste_verdicts().gel_plan_courant()
        noter_lancement(sortie, dict(etape="début", gel=gel, manifeste_verdicts=os.path.abspath(manifeste_verdicts),
                                     manifeste_verdicts_sha256=SO.sha256_fichier(manifeste_verdicts),
                                     partage_sha256=SO.sha256_fichier(partage)))
    else:
        preparer_reussite(dossiers)
    oppositions = []
    if oppositions_fichier:   # oppositions d'Otsoa aux retraits du motif a (plan 4.5 ; relecture C13, P9)
        with open(oppositions_fichier, encoding="utf-8") as f:
            oppositions = [tuple(x) for x in json.load(f)]
    if len(dossiers) == 1:
        entrees = EN.charger_entrees(dossiers[0], vagues=vagues, taches_retirees=retirees or (),
                                     oppositions=oppositions)
    else:   # les deux vagues du lanceur, réunies en une seule entrée (phase 4)
        entrees = EN.charger_entrees_vagues(dossiers, vagues, retirees or (), oppositions=oppositions)
    reg = AN.Reglages(G0=G0, R0=R0 if R0 is not None else cfg.R0, B=B if B is not None else cfg.B,
                      K=K if K is not None else cfg.K, tranche=tranche, choix=choix_methode())
    meta = dict(entrees=dict(dossiers=[os.path.abspath(d) for d in dossiers],
                             actions_typees_sha256=[SO.sha256_fichier(os.path.join(d, "actions_typees.csv"))
                                                    for d in dossiers],
                             cout_sha256=[SO.sha256_fichier(os.path.join(d, "cout.json")) for d in dossiers],
                             reussite_sha256=[SO.sha256_fichier(os.path.join(d, "reussite.csv")) for d in dossiers],
                             lanceur=EN.bilan_lanceur(dossiers),
                             partage=os.path.abspath(partage), partage_sha256=SO.sha256_fichier(partage),
                             vagues=meta_bilans(vagues), taches_retirees=sorted(map(list, entrees.taches_retirees)),
                             essai_a_blanc=essai, gel_plan=gel, oppositions_motif_a=sorted(map(list, oppositions)),
                             manifeste_verdicts_sha256=SO.sha256_fichier(manifeste_verdicts) if manifeste_verdicts
                             else None))
    av = AVERTISSEMENT_ESSAI if essai else None
    dec = executer(entrees, cal, conf, reg, sortie, av, meta_entrees=meta, processus=processus)
    if not essai:
        noter_lancement(sortie, dict(etape="fin", etiquette=dec.get("etiquette")))
    return dec


PERIMETRE_FIGE = ("banc", "simulation", "gel")   # dossiers figés par gel/manifeste.py (PERIMETRE)


def dans_perimetre_fige(chemin: str) -> bool:
    """Le chemin est dans un dossier que le gel fige (les sorties de l'expérience vont hors de ce périmètre)."""
    c = os.path.realpath(chemin)
    for d in PERIMETRE_FIGE:
        racine = os.path.realpath(os.path.join(RACINE, d))
        if os.path.commonpath([c, racine]) == racine:
            return True
    return False


def entier_positif(texte: str) -> int:
    v = int(texte)
    if v < 1:
        raise argparse.ArgumentTypeError(f"entier positif attendu, reçu {texte}")
    return v


AVERTISSEMENT_ESSAI = ("essai à blanc du rejeu final sur les parties de développement du pilote, partage fictif tiré "
                       "d'une valeur de balise de test, graine de développement. Ces chiffres n'ont AUCUNE valeur de "
                       "preuve (PLAN_EXPERIENCE.md, 5.16, point 6).")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--pilote", action="store_true", help="bout en bout sur le pilote (partage fictif)")
    p.add_argument("--experience", action="store_true", help="rejeu final de l'expérience réelle")
    p.add_argument("--essai-a-blanc", action="store_true",
                   help="le chemin du rejeu final sur le pilote (partage fictif écrit dans la sortie)")
    p.add_argument("--dossier", action="append", default=[],
                   help="dossier d'une vague du lanceur (un par vague : experience/vague1/…, experience/vague2/…)")
    p.add_argument("--partage", help="partage.json du tirage public (banc/tirage/tirage_public.py)")
    p.add_argument("--vague", action="append", default=[],
                   help="NOM=decisions.csv,alertes.json,accord.json (une par vague ; NOM = le champ vague des parties, "
                        "« 1 » ou « 2 » pour le lanceur)")
    p.add_argument("--retirees", help="JSON [[environnement, tâche], …] : tâches retirées hors motif a (inscrit au "
                                      "manifeste des verdicts)")
    p.add_argument("--oppositions", help="JSON [[environnement, tâche], …] : oppositions d'Otsoa aux retraits du "
                                         "motif a (inscrit au manifeste des verdicts)")
    p.add_argument("--manifeste-verdicts",
                   help="manifeste du gel des verdicts (gel/manifeste_verdicts.py) : obligatoire pour --experience")
    p.add_argument("--sortie", default=None,
                   help="dossier de sortie : obligatoire pour --experience (hors de banc/, simulation/ et gel/) et "
                        "--essai-a-blanc ; sorties_pilote/ par défaut pour --pilote")
    p.add_argument("--processus", type=int, default=1)
    p.add_argument("--R0", type=entier_positif, default=None,
                   help="essais seulement : l'expérience prend la valeur figée")
    p.add_argument("--B", type=entier_positif, default=None, help="essais seulement")
    p.add_argument("--K", type=entier_positif, default=None, help="essais seulement")
    p.add_argument("--tranche", type=entier_positif, default=200)
    a = p.parse_args(argv)
    if a.sortie is None:   # revue « ultra » du 06/11, constat 2 : sorties_pilote/ est suivi par git et figé
        if a.experience or a.essai_a_blanc:
            p.error("--experience et --essai-a-blanc demandent --sortie (pour l'expérience : un dossier hors de banc/, "
                    "simulation/ et gel/, que le gel fige)")
        a.sortie = SORTIE_PILOTE
    if a.experience and dans_perimetre_fige(a.sortie):
        p.error(f"--sortie {a.sortie} : les sorties de l'expérience vont hors de banc/, simulation/ et gel/ "
                "(gel/manifeste.py les fige)")
    if a.experience:
        if not (a.dossier and a.partage and a.vague):
            p.error("--experience demande --dossier, --partage et au moins une --vague")
        if not a.manifeste_verdicts:
            p.error("--experience demande --manifeste-verdicts (gel/manifeste_verdicts.py ; relecture C13, P1)")
        retirees = None
        if a.retirees:
            with open(a.retirees, encoding="utf-8") as f:
                retirees = [tuple(x) for x in json.load(f)]
        dec = executer_experience(a.dossier, a.partage, [vague_depuis_texte(v) for v in a.vague], a.sortie, retirees,
                                  a.processus, False, a.R0, a.B, a.K, a.tranche, a.manifeste_verdicts, a.retirees,
                                  a.oppositions)
    elif a.essai_a_blanc:
        os.makedirs(a.sortie, exist_ok=True)
        entrees = EN.charger_entrees(DOSSIER_PILOTE)
        chemin = os.path.join(a.sortie, "partage_essai.json")
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(partage_pilote(entrees), f, ensure_ascii=False, indent=1)
        rel = os.path.join(DOSSIER_PILOTE, "relecture")
        v = EN.VagueRelecture(entrees.parties[0].vague, os.path.join(rel, "decisions.csv"),
                              os.path.join(rel, "alertes.json"), None)
        dec = executer_experience(DOSSIER_PILOTE, chemin, [v], a.sortie, None, a.processus, True, a.R0, a.B, a.K,
                                  a.tranche)
    elif a.pilote:
        entrees, cal, conf, meta = entrees_et_partage_pilote()
        cfg = CR.charger_config()
        reg = AN.Reglages(G0=cfg.G0_developpement, R0=a.R0 or CR.R0, B=a.B or CR.B, K=a.K or CR.K,
                          tranche=a.tranche, choix=choix_methode())   # constat 4 : jamais le vrai G0 ici
        dec = executer(entrees, cal, conf, reg, a.sortie, AVERTISSEMENT_PILOTE, meta_entrees=meta,
                       processus=a.processus)
    else:
        p.error("--pilote, --essai-a-blanc ou --experience")
    print(json.dumps(dict(etiquette=dec["etiquette"], sortie=a.sortie), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
