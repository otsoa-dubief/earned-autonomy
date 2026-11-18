"""Audit des tâches sans alerte (PLAN_EXPERIENCE.md, 4.5 ; Q2 ; consigne : CONSIGNE_RELECTURE.md, « Audit »).

Une seule fois, après la relecture de la dernière vague et avant le gel des verdicts. Deux étapes.

1. `tirer` : tire les tâches et prépare les fiches.
   - Population : les tâches de la réserve jouées au moins une fois (au moins une partie gardée au bon statut
     technique) et sans aucune alerte, toutes parties et toutes vagues confondues. Alerte : écriture fausse, doublon
     ou refusée, exactement comme `fiches.lire_alertes` (le doublon sans effet n'en est pas une). Les parties sont
     lues comme le moteur les lit (`simulation/rejeu/entrees.py`, `charger_parties`).
   - Tirage : cinq tâches par environnement (toutes s'il y en a moins), puis une partie par tâche.
   - La graine vient de `secrets` ; elle est inscrite dans audit_tirage.json APRÈS le tirage. Un tirage ne se refait
     pas : le programme refuse d'écrire là où un tirage existe.
   Sortie : audit_tirage.json (correspondance fiche -> tâche, partie : jamais montrée aux relecteurs) ;
   fiches/<id>.md et .json (aveugles : ni modèle, ni partie, ni rang, ni identifiant de tâche) ; audit_modele.csv.

2. `conclure` : lit les réponses des relecteurs (instances de Claude au contexte vierge ; une ligne CSV par fiche).
   - Tâches défectueuses (motif a, cas a1 à a4, preuve) : retraits proposés. `--apercu` affiche la conclusion sans
     rien écrire, pour montrer la liste à Otsoa ; `--oppositions ID…` garde les tâches auxquelles il s'oppose
     (4.5, « Contrôle »).
   - Erreurs invisibles : écritures jugées justes que le règlement ou la demande du client contredit. Leur nombre,
     rapporté au nombre d'écritures jugées justes des parties lues, par environnement, puis taux global pondéré par le
     nombre de tâches sans alerte de chaque environnement. Ne change aucun verdict : publié comme mesure de ce que la
     comparaison ne voit pas (5.8 ; limite sur d, 1.4).
   Sortie : audit_conclusion.json, audit_conclusion.txt, taches_retirees_audit.json ([[environnement, tâche], …], le
   format de `simulation/rejeu/bout_en_bout.py --retirees`). Une conclusion ne se refait pas.

Choix d'implémentation (tranchés par Claude le 06/11 ; PLAN_EXPERIENCE.md, 4.5, lecture datée) :
1. La partie lue est tirée parmi les parties de la tâche qui comptent au moins une écriture jugée juste (à défaut,
   parmi toutes ses parties au bon statut). Le taux visé ne change pas : une partie sans écriture n'ajoute rien, ni
   au numérateur ni au dénominateur ; aucune des 20 fiches n'est perdue pour la mesure.
2. Les écritures jugées justes sont marquées « ◄ ÉCRITURE n° k » dans la conversation et listées en tête de fiche ;
   le relecteur cite une erreur par ce numéro (un message peut porter deux appels). Une écriture répétée sans effet,
   neutre (REGLE.md, 5 novembre, point 6), est marquée à part et n'entre pas dans la mesure.
3. Le dénominateur est le nombre d'écritures marquées, compté par le programme ; un écart avec le compte du
   relecteur est signalé dans la conclusion, sans changer la mesure.
4. Une erreur invisible compte une fois par écriture, même si plusieurs champs sont en cause.
5. Les fiches des tâches retirées sortent de la mesure, puisque leurs écritures quittent l'expérience ; leurs nombres
   sont donnés à part.

Usage :
    python banc/relecture/audit_sans_alerte.py tirer --dossier VAGUE1 --dossier VAGUE2 --sortie AUDIT
    python banc/relecture/audit_sans_alerte.py conclure --sortie AUDIT --reponses reponses.csv --apercu
    python banc/relecture/audit_sans_alerte.py conclure --sortie AUDIT --reponses reponses.csv [--oppositions ID …]
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import random
import re
import secrets
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

ICI = Path(__file__).resolve().parent
RACINE = ICI.parents[1]
for _d in (RACINE, RACINE / "banc", ICI):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

import journal  # noqa: E402  (banc/relecture/journal.py)
import decisions  # noqa: E402
import fiches  # noqa: E402
import verdicts  # noqa: E402
from simulation.rejeu import entrees  # noqa: E402  (les parties comme le moteur les lit)

PAR_ENVIRONNEMENT = 5
NATURE = "audit des tâches sans alerte"
COLONNES = ["tache", "defectueuse", "cas", "preuve", "erreurs_invisibles", "ecritures_lues"]
CAS = ("a1", "a2", "a3", "a4")
MARQUE = "◄ ÉCRITURE n° {k}"
MARQUE_SANS_EFFET = "◄ écriture répétée sans effet (hors mesure)"
DOMAINE_TAU2 = {env: dom for dom, env in fiches.ENV_TAU2.items()}  # aviation -> airline…
F_TIRAGE = "audit_tirage.json"
F_MODELE = "audit_modele.csv"
F_CONCLUSION = "audit_conclusion.json"
F_TEXTE = "audit_conclusion.txt"
F_RETRAITS = "taches_retirees_audit.json"


class AuditInvalide(ValueError):
    pass


def _sha256(chemin) -> str:
    return hashlib.sha256(Path(chemin).read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Lecture des dossiers de vague
# ---------------------------------------------------------------------------
def _lire_actions(dossier: Path) -> list:
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    with open(dossier / "actions_typees.csv", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _tache_de(l: dict, parties: dict, dossier: Path) -> tuple:
    """(environnement, tâche) de la partie d'une ligne d'action, contrôlée contre cout.json."""
    pid = str(l["partie"])
    if pid not in parties or parties[pid][0] != dossier:
        raise AuditInvalide(f"{dossier.name} : action d'une partie absente de ce dossier ({pid})")
    p = parties[pid][1]
    env = entrees.environnement_action(l["banc"], l["domaine"])
    if (env, str(l["tache"])) != (p.environnement, str(p.tache)):
        raise AuditInvalide(f"{dossier.name} : la partie {pid} est ({p.environnement}, {p.tache}) dans cout.json, "
                            f"({env}, {l['tache']}) dans actions_typees.csv")
    return env, str(p.tache)


def charger(dossiers) -> dict:
    """Parties, alertes et écritures (hors alertes) de tous les dossiers de vague.

    {"parties": {id: (dossier, Partie)}, "alertes": {(env, tâche): nombre}, "ecritures": {id de partie: [ligne]},
    "sources": [{dossier, empreintes}]}."""
    dossiers = [Path(d) for d in dossiers]
    if not dossiers:
        raise AuditInvalide("aucun dossier de vague")
    parties: dict = {}
    for d in dossiers:
        for p in entrees.charger_parties(str(d)):
            if p.id in parties:
                raise AuditInvalide(f"partie {p.id} présente dans deux dossiers")
            parties[p.id] = (d, p)
    alertes: dict = defaultdict(int)
    ecritures: dict = defaultdict(list)
    sources = []
    for d in dossiers:
        for a in fiches.lire_alertes(d):
            alertes[_tache_de(a, parties, d)] += 1
        for l in _lire_actions(d):
            if l.get("kind") != verdicts.ECRITURE or l.get("verdict") in fiches.VERDICTS_ALERTE:
                continue
            _tache_de(l, parties, d)
            if l.get("verdict") not in (verdicts.JUSTE, verdicts.DOUBLON_SANS_EFFET):
                raise AuditInvalide(f"{d.name} : écriture au verdict inattendu « {l.get('verdict')} » "
                                    f"(partie {l['partie']}, rang {l['rang']})")
            ecritures[str(l["partie"])].append(l)
        sources.append({"dossier": str(d), "cout_sha256": _sha256(d / "cout.json"),
                        "actions_typees_sha256": _sha256(d / "actions_typees.csv")})
    return {"parties": parties, "alertes": dict(alertes), "ecritures": dict(ecritures), "sources": sources}


def population(donnees: dict) -> tuple:
    """({environnement: {tâche: [parties au bon statut]}} des tâches jouées sans aucune alerte,
    {environnement: nombre de tâches jouées})."""
    jouees: dict = defaultdict(lambda: defaultdict(list))
    for pid, (_, p) in donnees["parties"].items():
        if p.statut_ok:
            jouees[p.environnement][str(p.tache)].append(pid)
    pop = {env: {t: sorted(ps) for t, ps in taches.items() if (env, t) not in donnees["alertes"]}
           for env, taches in jouees.items()}
    return pop, {env: len(taches) for env, taches in jouees.items()}


def _justes(lignes) -> list:
    return sorted((l for l in lignes if l.get("verdict") == verdicts.JUSTE), key=lambda l: int(l["rang"]))


def tirer(pop: dict, ecritures: dict, rng: random.Random, par_env: int = PAR_ENVIRONNEMENT) -> list:
    """Cinq tâches par environnement (toutes s'il y en a moins), puis une partie par tâche (choix 1)."""
    choix = []
    for env in sorted(pop):
        taches = sorted(pop[env])
        for t in rng.sample(taches, min(par_env, len(taches))):
            au_bon_statut = pop[env][t]
            avec = [pid for pid in au_bon_statut if _justes(ecritures.get(pid, ()))]
            candidates = sorted(avec or au_bon_statut)
            choix.append({"environnement": env, "tache": t, "partie": rng.choice(candidates),
                          "avec_ecriture": bool(avec), "candidates": len(candidates)})
    return choix


def identifiant(graine: int, env: str, tache: str) -> str:
    """Opaque pour le relecteur : sans la graine (jamais montrée), il ne dit rien de la tâche."""
    h = hashlib.sha256(f"{graine}\x1f{env}\x1f{tache}".encode("utf-8")).hexdigest()[:12]
    return f"audit-{decisions.sans_accent(env).lower()}-{h}"


# ---------------------------------------------------------------------------
# Fiches
# ---------------------------------------------------------------------------
def _marques(lignes: list) -> tuple:
    """({rang: libellé}, [écritures comptées, dans l'ordre des rangs]) (choix 2)."""
    comptees = _justes(lignes)
    libelles = {int(l["rang"]): MARQUE.format(k=k) for k, l in enumerate(comptees, 1)}
    for l in lignes:
        if l.get("verdict") == verdicts.DOUBLON_SANS_EFFET:
            libelles[int(l["rang"])] = MARQUE_SANS_EFFET
    return libelles, comptees


def _texte_tau2(m: dict, marque_de: dict) -> str:
    """Comme `fiches._texte_message`, avec une marque par appel (identité de l'objet) au lieu d'une seule."""
    parts = []
    if m.get("content"):
        parts.append(str(m["content"]))
    for tc in m.get("tool_calls") or []:
        who = " (utilisateur)" if tc.get("requestor") == "user" else ""
        ligne = f"[appel d'outil{who}] {tc.get('name')}({json.dumps(tc.get('arguments'), ensure_ascii=False)})"
        if id(tc) in marque_de:
            ligne += f"   {marque_de[id(tc)]}"
        parts.append(ligne)
    return "\n".join(parts)


def _messages_step(s: dict, libelle: Optional[str]) -> list:
    """Comme `fiches._messages_step`, avec un libellé de marque au lieu de « action signalée »."""
    if s.get("action") in verdicts._OBSERVATION_SANS_OUTIL:
        return fiches._messages_step(s)
    appel = f"[appel d'outil] {s.get('action')}({json.dumps(s.get('action_input'), ensure_ascii=False)})"
    if libelle:
        appel += f"   {libelle}"
    contenu = fiches._contenu_step(s)
    return [{"role": "agent", "texte": (contenu + "\n" if contenu else "") + appel, "signale": False},
            {"role": "outil", "texte": str(s.get("observation", "")), "signale": False}]


def _reglement_entier(domaine: Optional[str], texte: Optional[str], tau2) -> dict:
    """Le règlement entier reçu par l'agent (pas d'outil signalé, donc pas d'extrait)."""
    if not domaine or domaine not in fiches.POLICY_FICHIER:
        return {"chemin": None, "texte": "", "note": "WorkBench n'a pas de règlement de domaine (pas de policy.md)."}
    chemin = Path(tau2) / fiches.POLICY_FICHIER[domaine]
    try:
        affiche = str(chemin.relative_to(RACINE))
    except ValueError:
        affiche = str(chemin)
    if not texte and chemin.is_file():
        texte = chemin.read_text(encoding="utf-8")
    note = ""
    if domaine == "banking_knowledge":
        note = ("Le règlement de la banque est assemblé à partir de composants du gabarit ; le texte ci-dessous est celui "
                "reçu par l'agent. Les règles d'outils détaillées sont dans la base de connaissances.")
    return {"chemin": affiche, "texte": texte or "", "note": note}


def _base(env: str, domaine: str) -> dict:
    return {"id": "", "version": "audit", "environnement": env, "domaine": domaine, "consigne": "",
            "etat_initial": None, "reglement": {}, "attendues_lisibles": [], "ecritures": [], "sans_effet": 0,
            "conversation": [], "encadre": [], "avertissements": []}


def _verifier_outil(f: dict, rang: int, nom: str, ligne: dict, lib: str = "") -> None:
    """Sans le rang dans l'avertissement (C11 ; revue « ultra » du 06/11, constat 7) : l'écriture est désignée par sa
    marque de la fiche (« ÉCRITURE n° k »), le rang reste dans audit_tirage.json."""
    if nom != ligne["outil"]:
        qui = f"l'appel marqué « {lib.lstrip('◄ ')} »" if lib else "l'appel marqué"
        f["avertissements"].append(fiches.avertissement_incoherence(nom, ligne["outil"], qui))


def _fiche_tau2(dossier_partie: Path, p, lignes: list, tau2, types) -> dict:
    data = json.loads((dossier_partie / "results.json").read_text(encoding="utf-8"))
    run = data["simulations"][0]
    info = data.get("info") or {}
    domaine = (info.get("environment_info") or {}).get("domain_name") or DOMAINE_TAU2.get(p.environnement, "")
    f = _base(p.environnement, domaine)
    tache = {str(t["id"]): t for t in data.get("tasks", [])}.get(str(run.get("task_id")))
    if tache is None:
        f["avertissements"].append("tâche introuvable dans results.json")
    else:
        f["consigne"] = fiches.enonce_lisible(tache.get("user_scenario"))
        f["etat_initial"] = tache.get("initial_state") or None
    ordre, appels = fiches._appels_tau2(run.get("messages") or [])
    libelles, comptees = _marques(lignes)
    par_rang = {int(l["rang"]): l for l in lignes}
    marque_de, message_de = {}, {}
    for rang, lib in sorted(libelles.items()):
        if rang >= len(appels):
            f["avertissements"].append(fiches.avertissement_hors(len(appels), "appels de la partie",
                                                                 lib.lstrip("◄ ")) + " : écriture non retrouvée")
            continue
        i, appel = appels[rang]
        nom, _, _ = verdicts._deballer(appel["name"], appel.get("arguments") or {})
        _verifier_outil(f, rang, nom, par_rang[rang], lib)
        marque_de[id(appel)] = lib
        message_de[rang] = i + 1
    f["conversation"] = [{"role": fiches.ROLES.get(m.get("role"), str(m.get("role"))), "texte": _texte_tau2(m, marque_de)}
                         for m in ordre]
    f["reglement"] = _reglement_entier(domaine, run.get("policy"), tau2)
    f["attendues_lisibles"] = [f"{k}. {fiches.ligne_attendue(a)}"
                               for k, a in enumerate(fiches.attendues_tau2(tache, types), 1)]
    f["ecritures"] = [{"numero": k, "message": message_de.get(int(l["rang"])), "outil": l["outil"]}
                      for k, l in enumerate(comptees, 1)]
    f["sans_effet"] = sum(1 for l in lignes if l.get("verdict") == verdicts.DOUBLON_SANS_EFFET)
    return f


def _fiche_workbench(dossier_vague: Path, dossier_partie: Path, p, lignes: list) -> dict:
    stem, _, i = str(p.id).rpartition(":")
    domaine = str(p.tache).split(":")[0]
    f = _base(p.environnement, domaine)
    chemin = dossier_partie / f"{stem}.csv"
    if not chemin.is_file() or not i.isdigit():
        raise AuditInvalide(f"partie WorkBench {p.id} introuvable dans {dossier_partie}")
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    with open(chemin, newline="", encoding="utf-8") as fh:
        rangee = list(csv.DictReader(fh))[int(i)]
    texte = rangee["task"]
    f["consigne"] = texte
    brut = fiches._attendues_workbench(dossier_vague, texte)
    if brut is None:
        f["avertissements"].append("actions attendues introuvables dans taches/")
    f["attendues_lisibles"] = [f"{k}. {fiches.ligne_attendue(a)}"
                               for k, a in enumerate(fiches.attendues_workbench(brut or ""), 1)]
    libelles, comptees = _marques(lignes)
    par_rang = {int(l["rang"]): l for l in lignes}
    messages = [{"role": "client", "texte": texte}]
    message_de = {}
    traces = dossier_partie / f"{stem}_traces.json"
    entree = None
    if traces.is_file():
        liste = json.loads(traces.read_text(encoding="utf-8"))
        k = int(i)
        entree = liste[k] if k < len(liste) and liste[k].get("task") == texte else None
    if entree is None:
        f["avertissements"].append("traces absentes pour cette tâche : conversation limitée à la consigne")
    else:
        steps = entree.get("steps", [])
        outils = [k for k, s in enumerate(steps) if s.get("action") not in verdicts._OBSERVATION_SANS_OUTIL]
        try:
            n_appels = len(ast.literal_eval(rangee["function_calls"])) if rangee["function_calls"].strip() else 0
        except (ValueError, SyntaxError):
            n_appels = -1
        if n_appels != len(outils):
            f["avertissements"].append("le nombre d'étapes d'outil ne coïncide pas avec function_calls : rangs approximatifs")
        etape_de = {}
        for rang, lib in sorted(libelles.items()):
            if rang >= len(outils):
                f["avertissements"].append(fiches.avertissement_hors(len(outils), "étapes d'outil",
                                                                     lib.lstrip("◄ ")) + " : écriture non retrouvée")
                continue
            etape_de[outils[rang]] = (rang, lib)
            _verifier_outil(f, rang, str(steps[outils[rang]].get("action")), par_rang[rang], lib)
        for k, s in enumerate(steps):
            rang, lib = etape_de.get(k, (None, None))
            if rang is not None:
                message_de[rang] = len(messages) + 1
            messages += [{"role": m["role"], "texte": m["texte"]} for m in _messages_step(s, lib)]
    f["conversation"] = messages
    f["reglement"] = _reglement_entier(None, None, None)
    f["ecritures"] = [{"numero": k, "message": message_de.get(int(l["rang"])), "outil": l["outil"]}
                      for k, l in enumerate(comptees, 1)]
    f["sans_effet"] = sum(1 for l in lignes if l.get("verdict") == verdicts.DOUBLON_SANS_EFFET)
    return f


def encadre(f: dict) -> list:
    """Résumé factuel en tête de fiche, sans avis."""
    env = f"WorkBench, domaine {f['domaine']}" if f["environnement"] == "WorkBench" else f["environnement"]
    L = [f"Environnement : {env}.",
         "Aucune écriture de cette tâche n'a été signalée par le contrôle automatique, dans aucune partie."]
    n = len(f["ecritures"])
    if n:
        L.append(f"La partie montrée compte {n} écriture{'s' if n > 1 else ''} jugée{'s' if n > 1 else ''} juste"
                 f"{'s' if n > 1 else ''}, marquée{'s' if n > 1 else ''} « ◄ ÉCRITURE n° k » dans la conversation.")
    else:
        L.append("La partie montrée ne compte aucune écriture jugée juste : seule la question 1 (tâche défectueuse) se pose.")
    if f["sans_effet"]:
        L.append(f"Elle compte aussi {f['sans_effet']} écriture(s) répétée(s) sans effet, marquée(s) à part : neutres, "
                 "elles n'entrent pas dans la mesure.")
    return L


def rendre_markdown(f: dict) -> str:
    L = [f"# Fiche d'audit {f['id']} (aveugle)", "",
         f"- Identifiant de la tâche, à reporter dans la colonne « tache » : {f['id']}", "",
         "## Résumé", ""] + [f"> {x}" for x in f["encadre"]]
    for a in f["avertissements"]:
        L += ["", f"ATTENTION : {a}"]
    L += ["", "## Écritures jugées justes de la partie", ""]
    if f["ecritures"]:
        L += ["| Écriture | Message | Outil |", "|---|---|---|"]
        L += [f"| n° {e['numero']} | {e['message'] or '(non retrouvé)'} | `{e['outil']}` |" for e in f["ecritures"]]
    else:
        L.append("Aucune.")
    L += ["", "## Énoncé de la tâche", "", fiches._bloc(f["consigne"])]
    if f.get("etat_initial"):
        L += ["", "## Données initiales propres à la tâche", "", fiches._bloc(fiches._json(f["etat_initial"]))]
    r = f["reglement"]
    L += ["", "## Règlement du domaine (texte entier)", ""]
    if r.get("chemin"):
        L.append(f"Fichier : `{r['chemin']}`")
    if r.get("note"):
        L.append(r["note"])
    if r.get("texte"):
        L += ["", fiches._bloc(r["texte"])]
    L += ["", "## Actions attendues de la tâche", "", fiches._bloc("\n".join(f["attendues_lisibles"]))]
    L += ["", "## Conversation entière", ""]
    if not f["conversation"]:
        L.append("(aucun message retrouvé)")
    for k, m in enumerate(f["conversation"], 1):
        L += [f"### {k}. {m['role']}", "", fiches._bloc(m["texte"]), ""]
    return "\n".join(L).rstrip() + "\n"


def construire_fiche(donnees: dict, choix: dict, ident: str, tau2, types_du_domaine) -> tuple:
    """(fiche aveugle, Markdown). Refuse une fiche qui laisse voir un modèle ou la partie."""
    dossier_vague, p = donnees["parties"][choix["partie"]]
    lignes = donnees["ecritures"].get(choix["partie"], [])
    dossier_partie = dossier_vague / "parties" / p.dossier
    if p.environnement == "WorkBench":
        f = _fiche_workbench(dossier_vague, dossier_partie, p, lignes)
    else:
        f = _fiche_tau2(dossier_partie, p, lignes, tau2, types_du_domaine(DOMAINE_TAU2.get(p.environnement, "")))
    f["id"] = ident
    f["encadre"] = encadre(f)
    noms = {p.modele, p.id, p.dossier} | {str(l.get("modele", "")) for l in lignes}
    noms = {n for n in noms if n} | {n.split("/")[-1] for n in noms if n}
    f = fiches.masquer(f, noms)
    md = rendre_markdown(f)
    if fiches.contient_modele(md + json.dumps(f, ensure_ascii=False), noms):
        raise AssertionError(f"nom de modèle ou partie présent dans la fiche {ident}")
    return f, md


def _types_cache(tau2):
    cache: dict = {}

    def types_du_domaine(domaine):
        if domaine not in cache:
            try:
                cache[domaine] = verdicts.types_tau2(tau2, domaine)
            except (FileNotFoundError, OSError, ValueError):
                cache[domaine] = None
        return cache[domaine]
    return types_du_domaine


def produire_tirage(dossiers, sortie, tau2=fiches.TAU2_PAR_DEFAUT, rng=None, graine=None) -> dict:
    """rng/graine : seulement pour les tests. En usage normal, la graine vient de `secrets`."""
    sortie = Path(sortie)
    deja = [str(sortie / n) for n in (F_TIRAGE, F_MODELE, "fiches") if (sortie / n).exists()]
    if deja:
        raise AuditInvalide(f"déjà tiré : {', '.join(deja)} ; un tirage ne se refait pas")
    # relecture C13, P11 : le journal de chaque vague fait foi, quel que soit le dossier de sortie
    if any(l.get("type") == "audit" for d in dossiers for l in journal.lire(Path(d) / "relecture")):
        raise AuditInvalide("audit déjà tiré selon le journal d'une vague ; un tirage ne se refait pas")
    donnees = charger(dossiers)
    pop, jouees = population(donnees)
    if rng is None:
        graine = secrets.randbits(64)
        rng = random.Random(graine)
    choix = tirer(pop, donnees["ecritures"], rng)
    types_du_domaine = _types_cache(tau2)
    construites = []
    for c in choix:
        ident = identifiant(graine, c["environnement"], c["tache"])
        construites.append((c, ident, *construire_fiche(donnees, c, ident, tau2, types_du_domaine)))
    ids = [i for _, i, _, _ in construites]
    if len(ids) != len(set(ids)):
        raise AuditInvalide("identifiants de fiche en double")
    (sortie / "fiches").mkdir(parents=True)
    fiches_tirage = []
    for c, ident, f, md in construites:
        base = sortie / "fiches" / ident
        base.with_suffix(".json").write_text(json.dumps(f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        base.with_suffix(".md").write_text(md, encoding="utf-8")
        _, p = donnees["parties"][c["partie"]]
        fiches_tirage.append({
            "id": ident, "environnement": c["environnement"], "tache": c["tache"], "partie": c["partie"],
            "dossier_partie": str(donnees["parties"][c["partie"]][0] / "parties" / p.dossier),
            "avec_ecriture": c["avec_ecriture"], "parties_candidates": c["candidates"],
            "ecritures_comptees": len(f["ecritures"]), "ecritures": f["ecritures"], "sans_effet": f["sans_effet"],
            "avertissements": f["avertissements"], "fiche_sha256": _sha256(base.with_suffix(".md")),
        })
    with open(sortie / F_MODELE, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(COLONNES)
        for ident in sorted(ids):
            w.writerow([ident, "", "", "", "", ""])
    resultat = {
        "nature": NATURE,
        "sources": donnees["sources"],
        "taches_jouees": dict(sorted(jouees.items())),
        "population": {env: len(pop[env]) for env in sorted(pop)},
        "tirees": {env: sum(1 for c in choix if c["environnement"] == env) for env in sorted(pop)},
        "fiches": fiches_tirage,
        "graine": graine,  # inscrite après le tirage
    }
    (sortie / F_TIRAGE).write_text(json.dumps(resultat, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for d in dossiers:   # relecture C13, P11 : une ligne au journal de chaque vague
        journal.noter(Path(d) / "relecture", dict(type="audit", graine=graine, sortie=str(sortie),
                                                  tirage_sha256=journal.sha256(sortie / F_TIRAGE)))
    return resultat


# ---------------------------------------------------------------------------
# Réponses des relecteurs
# ---------------------------------------------------------------------------
def _outil_concorde(cite: str, vrai: str) -> bool:
    a, b = cite.strip().lower(), vrai.strip().lower()
    return bool(a) and (a in b or b in a)


def lire_reponses(chemin, tirage: dict) -> dict:
    """{id: {defectueuse, cas, preuve, erreurs: [{ecriture, outil, champ, preuve}], ecritures_lues}}.
    Refuse le fichier entier à la première série d'erreurs, toutes listées."""
    par_id = {f["id"]: f for f in tirage["fiches"]}
    with open(chemin, newline="", encoding="utf-8-sig") as fh:
        lecteur = csv.DictReader(fh)
        if lecteur.fieldnames != COLONNES:
            raise AuditInvalide(f"en-tête attendu : {','.join(COLONNES)} ; lu : {','.join(lecteur.fieldnames or [])}")
        lignes = list(lecteur)
    fautes, sortie = [], {}
    for n, l in enumerate(lignes, 2):
        ident = (l.get("tache") or "").strip()
        if ident not in par_id:
            fautes.append(f"ligne {n} : fiche inconnue « {ident} »")
            continue
        if ident in sortie:
            fautes.append(f"ligne {n} : fiche {ident} en double")
            continue
        f = par_id[ident]
        rep = decisions.sans_accent((l.get("defectueuse") or "").strip()).lower()
        cas = (l.get("cas") or "").strip().lower()
        preuve = (l.get("preuve") or "").strip()
        if rep not in ("oui", "non"):
            fautes.append(f"ligne {n} : defectueuse vaut « oui » ou « non », pas « {l.get('defectueuse')} »")
        elif rep == "oui":
            m = re.fullmatch(r"a?([1-4])", cas)
            if not m:
                fautes.append(f"ligne {n} : tâche défectueuse sans cas valide (a1 à a4) : « {l.get('cas')} »")
            else:
                cas = "a" + m.group(1)
            if not preuve:
                fautes.append(f"ligne {n} : tâche défectueuse sans preuve")
        elif cas:
            fautes.append(f"ligne {n} : un cas est donné pour une tâche non défectueuse")
        erreurs = []
        for element in (x.strip() for x in (l.get("erreurs_invisibles") or "").split("|")):
            if not element:
                continue
            morceaux = [x.strip() for x in element.split(";", 3)]
            if len(morceaux) != 4 or not all(morceaux):
                fautes.append(f"ligne {n} : erreur invisible mal formée (« écriture ; outil ; champ ; preuve ») : "
                              f"« {element[:80]} »")
                continue
            nums = re.findall(r"\d+", morceaux[0])
            k = int(nums[0]) if len(nums) == 1 else None
            if k is None or not 1 <= k <= len(f["ecritures"]):
                fautes.append(f"ligne {n} : « {morceaux[0]} » n'est pas le numéro d'une écriture marquée de la fiche "
                              f"(1 à {len(f['ecritures'])})")
                continue
            if not _outil_concorde(morceaux[1], f["ecritures"][k - 1]["outil"]):
                fautes.append(f"ligne {n} : l'écriture n° {k} est {f['ecritures'][k - 1]['outil']}, pas « {morceaux[1]} »")
                continue
            erreurs.append({"ecriture": k, "outil": f["ecritures"][k - 1]["outil"], "champ": morceaux[2],
                            "preuve": morceaux[3]})
        lues = (l.get("ecritures_lues") or "").strip()
        if not lues.isdigit():
            fautes.append(f"ligne {n} : ecritures_lues doit être un entier positif ou nul, pas « {lues} »")
        sortie[ident] = {"defectueuse": rep == "oui", "cas": cas if rep == "oui" else "", "preuve": preuve,
                         "erreurs": erreurs, "ecritures_lues": int(lues) if lues.isdigit() else None}
    manquantes = sorted(set(par_id) - set(sortie))
    if manquantes:
        fautes.append(f"fiches sans réponse : {', '.join(manquantes)}")
    if fautes:
        raise AuditInvalide("réponses refusées :\n- " + "\n- ".join(fautes))
    return sortie


# ---------------------------------------------------------------------------
# Conclusion
# ---------------------------------------------------------------------------
def conclure(tirage: dict, reponses: dict, oppositions=()) -> dict:
    par_id = {f["id"]: f for f in tirage["fiches"]}
    proposes = sorted(i for i, r in reponses.items() if r["defectueuse"])
    oppositions = sorted(set(oppositions))
    hors = sorted(set(oppositions) - set(proposes))
    if hors:
        raise AuditInvalide(f"opposition à une tâche qui n'est pas proposée au retrait : {', '.join(hors)}")
    retirees = [i for i in proposes if i not in oppositions]

    def decrire(i):
        f, r = par_id[i], reponses[i]
        return {"id": i, "environnement": f["environnement"], "tache": f["tache"], "cas": r["cas"], "preuve": r["preuve"]}

    par_env: dict = {}
    hors_mesure = {"fiches": 0, "ecritures": 0, "erreurs_invisibles": 0}
    detail, ecarts = [], []
    for f in tirage["fiches"]:
        r = reponses[f["id"]]
        n_err = len({e["ecriture"] for e in r["erreurs"]})  # choix 4
        if r["ecritures_lues"] != f["ecritures_comptees"]:
            ecarts.append({"id": f["id"], "programme": f["ecritures_comptees"], "relecteur": r["ecritures_lues"]})
        if f["id"] in retirees:  # choix 5
            hors_mesure["fiches"] += 1
            hors_mesure["ecritures"] += f["ecritures_comptees"]
            hors_mesure["erreurs_invisibles"] += n_err
            continue
        e = par_env.setdefault(f["environnement"], {"fiches": 0, "ecritures": 0, "erreurs_invisibles": 0})
        e["fiches"] += 1
        e["ecritures"] += f["ecritures_comptees"]
        e["erreurs_invisibles"] += n_err
        detail += [{"id": f["id"], "environnement": f["environnement"], **x} for x in r["erreurs"]]
    poids = {}
    for env, e in par_env.items():
        e["taches_sans_alerte"] = tirage["population"].get(env, 0)
        e["taux"] = e["erreurs_invisibles"] / e["ecritures"] if e["ecritures"] else None
        if e["taux"] is not None and e["taches_sans_alerte"]:
            poids[env] = e["taches_sans_alerte"]
    total = sum(poids.values())
    taux = sum(poids[env] * par_env[env]["taux"] for env in poids) / total if total else None
    return {
        "nature": NATURE,
        "retraits": [decrire(i) for i in retirees],
        "oppositions": [decrire(i) for i in oppositions],
        "mesure": {
            "par_environnement": dict(sorted(par_env.items())),
            "poids": {env: poids[env] / total for env in sorted(poids)} if total else {},
            "taux_pondere": taux,
            "hors_mesure": hors_mesure,
        },
        "erreurs_invisibles": detail,
        "ecarts_de_compte": ecarts,
    }


def _pct(x) -> str:
    return "non défini (aucune écriture lue)" if x is None else f"{100 * x:.2f} %"


def texte_conclusion(c: dict) -> str:
    L = ["Audit des tâches sans alerte (PLAN_EXPERIENCE.md, 4.5)", ""]
    L.append(f"Retraits ({len(c['retraits'])}) : tâches défectueuses, retirées avec toutes leurs actions.")
    for r in c["retraits"]:
        L.append(f"- {r['environnement']}, tâche {r['tache']} ({r['id']}) : cas {r['cas']}. Preuve : {r['preuve']}")
    if c["oppositions"]:
        L.append(f"Gardées sur opposition d'Otsoa ({len(c['oppositions'])}) :")
        L += [f"- {r['environnement']}, tâche {r['tache']} ({r['id']}) : cas {r['cas']}. Preuve : {r['preuve']}"
              for r in c["oppositions"]]
    m = c["mesure"]
    L += ["", "Erreurs invisibles (écritures jugées justes que le règlement ou la demande du client contredit) :"]
    for env, e in m["par_environnement"].items():
        L.append(f"- {env} : {e['erreurs_invisibles']} sur {e['ecritures']} écritures lues, dans {e['fiches']} fiches "
                 f"({_pct(e['taux'])}) ; {e['taches_sans_alerte']} tâches sans alerte.")
    L.append(f"Taux global, pondéré par le nombre de tâches sans alerte de chaque environnement : {_pct(m['taux_pondere'])}.")
    h = m["hors_mesure"]
    if h["fiches"]:
        L.append(f"Hors mesure (tâches retirées) : {h['fiches']} fiches, {h['erreurs_invisibles']} erreurs invisibles "
                 f"sur {h['ecritures']} écritures.")
    if c["ecarts_de_compte"]:
        L += ["", "Écarts entre le compte d'écritures du programme et celui du relecteur (la mesure garde celui du programme) :"]
        L += [f"- {x['id']} : programme {x['programme']}, relecteur {x['relecteur']}" for x in c["ecarts_de_compte"]]
    L += ["", "Cette mesure ne change aucun verdict."]
    return "\n".join(L) + "\n"


def verifier_fiches(sortie: Path, tirage: dict) -> None:
    """Les fiches lues sont celles du tirage (empreinte du Markdown)."""
    for f in tirage["fiches"]:
        chemin = sortie / "fiches" / f"{f['id']}.md"
        if not chemin.is_file() or _sha256(chemin) != f["fiche_sha256"]:
            raise AuditInvalide(f"la fiche {f['id']} manque ou a changé depuis le tirage")


def produire_conclusion(sortie, reponses_csv, oppositions=(), apercu: bool = False) -> dict:
    sortie = Path(sortie)
    tirage_brut = (sortie / F_TIRAGE).read_bytes()
    tirage = json.loads(tirage_brut)
    verifier_fiches(sortie, tirage)
    c = conclure(tirage, lire_reponses(reponses_csv, tirage), oppositions)
    c["tirage_sha256"] = hashlib.sha256(tirage_brut).hexdigest()
    c["reponses_sha256"] = _sha256(reponses_csv)
    if apercu:
        return c
    deja = [str(sortie / n) for n in (F_CONCLUSION, F_TEXTE, F_RETRAITS) if (sortie / n).exists()]
    if deja:
        raise AuditInvalide(f"déjà conclu : {', '.join(deja)} ; une conclusion ne se refait pas")
    retirees = sorted([r["environnement"], r["tache"]] for r in c["retraits"])
    (sortie / F_RETRAITS).write_text(json.dumps(retirees, ensure_ascii=False) + "\n", encoding="utf-8")
    (sortie / F_TEXTE).write_text(texte_conclusion(c), encoding="utf-8")
    (sortie / F_CONCLUSION).write_text(json.dumps(c, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return c


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sous = p.add_subparsers(dest="etape", required=True)
    t = sous.add_parser("tirer", help="tirer les tâches et écrire les fiches")
    t.add_argument("--dossier", action="append", required=True, help="dossier de vague (répété : toutes les vagues)")
    t.add_argument("--sortie", required=True)
    t.add_argument("--tau2", default=str(fiches.TAU2_PAR_DEFAUT), help="clone tau-bench (règlement, types)")
    c = sous.add_parser("conclure", help="lire les réponses et conclure")
    c.add_argument("--sortie", required=True, help="dossier du tirage")
    c.add_argument("--reponses", required=True)
    c.add_argument("--oppositions", nargs="*", default=[], help="fiches dont Otsoa refuse le retrait")
    c.add_argument("--apercu", action="store_true", help="afficher sans rien écrire")
    a = p.parse_args(argv)
    try:
        if a.etape == "tirer":
            r = produire_tirage(a.dossier, a.sortie, a.tau2)
            for env, n in r["population"].items():
                print(f"{env} : {r['tirees'][env]} tirées sur {n} tâches sans alerte ({r['taches_jouees'][env]} jouées)")
            print(f"{len(r['fiches'])} fiches dans {Path(a.sortie) / 'fiches'}")
        else:
            r = produire_conclusion(a.sortie, a.reponses, a.oppositions, a.apercu)
            print(texte_conclusion(r), end="")
            if a.apercu:
                print("(aperçu : rien n'est écrit)")
    except (AuditInvalide, entrees.EntreeInvalide, ValueError, FileNotFoundError) as e:
        print(f"erreur: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
