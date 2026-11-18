"""Pilote, étapes 2a et 2 de l'expérience « autonomie méritée ».

- Étape 2a : mini-essai du cache. 2 parties claude-haiku-5-5 AVEC cache (aviation, première tâche de la liste ; banque,
  première tâche de la liste : les mêmes qu'à l'étape 1). Plafond 0,10 $. Rapport : jetons de cache lus et écrits, coût v2,
  comparaison au coût de l'étape 1 (rapport_2a.txt / .json).
- Étape 2 : 3 modèles d'agent (claude-haiku-5-5, claude-sonnet-5-5, claude-opus-5-5) x 4 environnements x 10 tâches.
  Le client simulé tau2 est toujours claude-haiku-5-5. Plafond obligatoire en réel, 40 $ au plus.

MODE PAR DÉFAUT : À BLANC (aucune clé, aucun réseau : bancs sur leurs réponses factices, proxys cassés).

    python banc/pilote_etape2.py --etape 2a                                       # à blanc
    python banc/pilote_etape2.py --etape 2a --reel --plafond-usd 0.10             # réel (voir INSTALLATION.md, section 8)
    python banc/pilote_etape2.py --etape 2 --cache --reel --plafond-usd 25        # réel

Réutilise les garde-fous de l'étape 1 (banc/pilote_etape1.py, inchangé) : clé lue seulement dans
~/.config/autonomie-meritee/anthropic.env (600), jamais affichée ; environnement des enfants nettoyé de toute autre clé ;
pas de `.env` dans les bancs ; arrêt avant toute nouvelle partie à 80 % du plafond, ou dès qu'un usage est illisible,
incomplet, d'un modèle inconnu, ou si un enfant échoue.

Coût : calculé APRÈS chaque partie depuis le JSONL du callback LiteLLM (tau2, banc/usage_tau2.py) ou de l'enveloppe
WorkBench (banc/usage_wrap.py), par appel et par modèle (banc/cout_v2.py). En réel, JSONL absent, illisible ou
incomplet (croisement avec results.json) : arrêt.

Cache : drapeau --cache (forcé en 2a) = `cache_control_injection_points` dans --agent-llm-args et --user-llm-args de tau2.
WorkBench n'a pas de cache (client OpenAI-compatible d'Anthropic : aucun point d'injection n'y est possible).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
import threading
from datetime import datetime
from pathlib import Path

BANC = Path(__file__).resolve().parent
if str(BANC) not in sys.path:
    sys.path.insert(0, str(BANC))

import cout_v2 as cv  # noqa: E402
import pilote_etape1 as pe  # noqa: E402
from pilote_etape1 import ErreurPilote  # noqa: E402

RACINE = pe.RACINE
TAU2 = pe.TAU2
WORKBENCH = pe.WORKBENCH
WB_RUN = pe.WB_RUN
DEVELOPPEMENT = pe.DEVELOPPEMENT
CHEMIN_CLE = pe.CHEMIN_CLE
ENVS = pe.ENVS
DOMAINE_TAU = pe.DOMAINE_TAU

MODELES = ("claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5")
COURT = {"claude-haiku-5-5": "haiku", "claude-sonnet-5-5": "sonnet", "claude-opus-5-5": "opus"}
MODELE_USER = "anthropic/claude-haiku-5-5"  # client simulé tau2 : toujours Haiku
PARTIES_PAR_ENV = 10
# Ordre des fichiers WorkBench pour le tourniquet (décision du coordinateur, 05/11).
ORDRE_WB = ("email", "calendar", "customer_relationship_manager", "project_management", "analytics", "multi_domain")
MAX_POINTS_CACHE = 4  # limite de points d'arrêt de cache par requête chez Anthropic
PLAFOND_MAX = {"2a": 0.10, "2": 40.0}
CONCURRENCE_DEFAUT = {"2a": 1, "2": 2}
CONCURRENCE_MAX = 3
SORTIES = {"2a": RACINE / "pilote" / "etape2a", "2": RACINE / "pilote" / "etape2"}
MAX_PAS_REEL = pe.MAX_PAS_REEL
DELAI_PARTIE_S = pe.DELAI_PARTIE_S
# Coûts de l'étape 1 (sans cache, haiku) pour la comparaison 2a : pilote/etape1/2026-11-05_07-25-06/cout.json,
# parties aviation-1 (tâche 11) et banque-1 (task_003).
REF_ETAPE1 = {"aviation": 0.0153169, "banque": 0.0158345}
TACHES_2A_ENVS = ("aviation", "banque")

LISTE_FACTICE = {
    "aviation": [str(i) for i in range(10)],
    "commerce": [str(i) for i in range(10)],
    "banque": [f"task_{i:03d}" for i in range(1, 11)],
    "WorkBench": [f"{p}:{i}" for i in range(2) for p in ORDRE_WB][:PARTIES_PAR_ENV],
}


# --- tâches -------------------------------------------------------------------------------------------------
def tourniquet_workbench(ids: list, n: int = PARTIES_PAR_ENV, ordre=ORDRE_WB) -> list:
    """n tâches WorkBench en tourniquet sur les fichiers (dans `ordre`), chaque fichier dans l'ordre de la liste.
    Un fichier épuisé est sauté. ErreurPilote si moins de n tâches au total."""
    par_fichier = {p: [i for i in ids if isinstance(i, str) and i.split(":", 1)[0] == p] for p in ordre}
    sortie, rang = [], 0
    while len(sortie) < n and any(rang < len(v) for v in par_fichier.values()):
        for p in ordre:
            if len(sortie) < n and rang < len(par_fichier[p]):
                sortie.append(par_fichier[p][rang])
        rang += 1
    if len(sortie) < n:
        raise ErreurPilote(f"WorkBench : {len(sortie)} tâches disponibles dans les fichiers {', '.join(ordre)}, {n} attendues")
    return sortie


def charger_taches(chemin, reel: bool, etape: str = "2", n: int = PARTIES_PAR_ENV) -> tuple:
    """({env: [ids]}, factice ?). Étape 2 : les n premières de chaque liste (tau2) et le tourniquet (WorkBench).
    Étape 2a : la première de aviation et de banque. Fichier absent : réel = refus, blanc = liste factice."""
    chemin = Path(chemin)
    if not chemin.is_file():
        if reel:
            raise ErreurPilote(f"liste des tâches introuvable : {chemin}")
        data, factice = {e: list(v) for e, v in LISTE_FACTICE.items()}, True
    else:
        try:
            data = json.loads(chemin.read_text(encoding="utf-8"))
        except ValueError:
            raise ErreurPilote(f"liste des tâches illisible : {chemin}")
        factice = False
    if etape == "2a":
        sortie = {}
        for e in TACHES_2A_ENVS:
            ids = data.get(e) if isinstance(data, dict) else None
            if not isinstance(ids, list) or not ids or not isinstance(ids[0], str) or not ids[0]:
                raise ErreurPilote(f"liste des tâches : identifiant attendu pour {e}")
            sortie[e] = [ids[0]]
        return sortie, factice
    sortie = {}
    for e in ("aviation", "commerce", "banque"):
        ids = data.get(e) if isinstance(data, dict) else None
        if not isinstance(ids, list) or len(ids) < n or not all(isinstance(i, str) and i for i in ids[:n]):
            raise ErreurPilote(f"liste des tâches : au moins {n} identifiants (chaînes) attendus pour {e}")
        sortie[e] = list(ids[:n])
    wb = data.get("WorkBench") if isinstance(data, dict) else None
    if not isinstance(wb, list):
        raise ErreurPilote("liste des tâches : WorkBench absent")
    sortie["WorkBench"] = tourniquet_workbench(wb, n)
    return {e: sortie[e] for e in ENVS}, factice


def verifier_taches_existent(taches: dict, tau2=None, workbench=None) -> None:
    """Contrôle avant tout appel : chaque identifiant existe dans le banc correspondant (seulement les environnements présents)."""
    tau2 = Path(tau2 or TAU2)
    for env, dom in DOMAINE_TAU.items():
        if env not in taches:
            continue
        chemin = tau2 / "data" / "tau2" / "domains" / dom / "tasks.json"
        connus = {str(t["id"]) for t in json.loads(chemin.read_text(encoding="utf-8"))}
        for i in taches[env]:
            if i not in connus:
                raise ErreurPilote(f"{env} : tâche {i!r} absente de {chemin.name}")
    if "WorkBench" in taches:
        from verdicts import charger_taches_workbench
        connus = set(charger_taches_workbench(workbench or WORKBENCH))
        for i in taches["WorkBench"]:
            if i not in connus:
                raise ErreurPilote(f"WorkBench : tâche {i!r} inconnue")


def construire_parties(taches: dict, modeles=MODELES) -> list:
    """Intercalées par rang, puis par environnement, puis par modèle : un arrêt laisse une couverture équilibrée."""
    parties = []
    n = max(len(v) for v in taches.values())
    for rang in range(n):
        for env in ENVS:
            if env in taches and rang < len(taches[env]):
                for m in modeles:
                    parties.append({"id": f"{env}-{COURT[m]}-{rang + 1}", "env": env, "tache": taches[env][rang],
                                    "rang": rang + 1, "modele": m})
    return parties


# --- cache et commandes -------------------------------------------------------------------------------------
def verifier_points(points: list) -> list:
    if len(points) > MAX_POINTS_CACHE:
        raise ErreurPilote(f"cache : {len(points)} points d'injection, au plus {MAX_POINTS_CACHE}")
    return points


def points_injection() -> list:
    """Message système + dernier message. Syntaxe lue dans litellm/integrations/anthropic_cache_control_hook.py (1.81.11) :
    `role` cible tous les messages de ce rôle, `index` accepte les négatifs (-1 = dernier). Le point sur le système couvre
    aussi les outils (ordre du préfixe : outils, système, messages) ; le point sur le dernier message fait cacher le préfixe
    de la conversation, tour après tour. Vérifié hors réseau : le corps de requête Anthropic reçoit bien cache_control
    sur le bloc système et sur le dernier message (y compris un résultat d'outil)."""
    return verifier_points([{"location": "message", "role": "system"}, {"location": "message", "index": -1}])


def commande_tau2(partie: dict, nom_sauvegarde: str, reel: bool, cache: bool) -> list:
    """Ligne de commande (sans aucune clé) d'une partie tau2. Évaluation ENV seule (tau2_sans_juge.py) : aucun juge OpenAI.
    Réglages vides en réel (les modèles 5.5 refusent `temperature`) ; avec cache, seuls les points d'injection."""
    env = partie["env"]
    cmd = [str(TAU2 / ".venv" / "bin" / "python"), str(BANC / "tau2_sans_juge.py"), "run", "--domain", DOMAINE_TAU[env]]
    if reel:
        args_agent, args_user = {}, {}
        pas = MAX_PAS_REEL
    else:
        args_agent, args_user, pas = pe._mock_tau(env)
    if cache:
        pts = points_injection()
        args_agent = dict(args_agent, cache_control_injection_points=pts)
        args_user = dict(args_user, cache_control_injection_points=pts)
    cmd += ["--agent-llm", f"anthropic/{partie['modele']}", "--user-llm", MODELE_USER,
            "--agent-llm-args", json.dumps(args_agent), "--user-llm-args", json.dumps(args_user)]
    if env == "aviation":
        cmd += ["--communicate-scorer", "substring"]
    if env == "banque":
        cmd += ["--retrieval-config", "bm25_grep"]
    cmd += ["--task-ids", partie["tache"], "--num-trials", "1", "--max-concurrency", "1", "--save-to", nom_sauvegarde,
            "--max-steps", str(pas)]
    return cmd


def commande_workbench(chemin_taches, modele: str) -> list:
    return [str(WORKBENCH / ".venv" / "bin" / "python"), str(BANC / "workbench_pilote.py"), "--model_name", modele,
            "--tasks_path", str(chemin_taches), "--tool_selection", "all", "--workers", "1", "--log_traces",
            "--structured_outputs"]


def env_partie(env: dict, chemin_usage) -> dict:
    """Copie de l'environnement des enfants + PILOTE_USAGE_FILE (posée APRÈS env_enfant, qui retire les PILOTE_*)."""
    e = dict(env)
    e["PILOTE_USAGE_FILE"] = str(chemin_usage)
    return e


# --- usage et exécution -------------------------------------------------------------------------------------
def usage_partie_tau2(results, usage, modele: str, reel: bool) -> tuple:
    """(appels, estime). Réel : le JSONL du callback fait foi et doit couvrir results.json (ValueError sinon).
    À blanc : si le JSONL manque, usage estimé depuis results.json (caractères / 4) et marqué estimé."""
    de_results = pe.appels_tau2(results, estimer=not reel)
    try:
        appels = cv.lire_usage_jsonl(usage)
    except ValueError:
        if reel:
            raise
        return [{"modele": modele, "prompt_tokens": p, "completion_tokens": c, "cache_creation_input_tokens": 0,
                 "cache_read_input_tokens": 0} for p, c, _ in de_results], True
    if reel:
        cv.croiser(appels, de_results)
    return appels, False


def _concat(a, b):
    return (a + " ; " if a else "") + b


def executer_partie(partie: dict, ctx: dict) -> dict:
    """Lance une partie et rend {ok, appels (dicts), estime, copies, erreur}. Ne lève pas : l'échec est une donnée."""
    sortie: Path = ctx["sortie"]
    reel = ctx["reel"]
    pid = partie["id"]
    log = sortie / "logs" / f"{pid}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    usage = sortie / "usage" / f"{pid}.jsonl"
    usage.parent.mkdir(parents=True, exist_ok=True)
    env = env_partie(ctx["env_enfant"], usage)
    res = {"ok": False, "appels": None, "estime": False, "erreur": None, "copies": []}
    if partie["env"] != "WorkBench":
        nom = f"{'pilote' if reel else 'essai-blanc'}-etape{ctx['etape']}-{ctx['horodatage']}-{pid}"
        code = pe.executer_enfant(commande_tau2(partie, nom, reel, ctx["cache"]), env, TAU2, log, ctx.get("cle"))
        source = TAU2 / "data" / "simulations" / nom / "results.json"
        if code != 0:
            res["erreur"] = f"tau2 : code de retour {code}"
        if source.is_file():
            cible = sortie / "parties" / f"tau2-{pid}" / "results.json"
            cible.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, cible)
            res["copies"].append(str(cible))
            try:
                res["appels"], res["estime"] = usage_partie_tau2(cible, usage, partie["modele"], reel)
            except ValueError as e:
                res["erreur"] = _concat(res["erreur"], f"usage illisible : {e}")
        else:
            res["erreur"] = _concat(res["erreur"], "results.json absent")
        res["ok"] = res["erreur"] is None
        return res
    # WorkBench : parties sérialisées (fichiers de sortie nommés à la seconde près, dossier commun). Pas de cache.
    with ctx["verrou_wb"]:
        csv_taches = pe.ecrire_taches_workbench(partie, sortie / "taches" / pid, WORKBENCH)
        avant = pe._fichiers(WB_RUN / "data" / "results")
        code = pe.executer_enfant(commande_workbench(csv_taches, partie["modele"]), env, WB_RUN, log, ctx.get("cle"))
        nouveaux = sorted(pe._fichiers(WB_RUN / "data" / "results") - avant)
        cible = sortie / "parties" / f"workbench-{pid}"
        cible.mkdir(parents=True, exist_ok=True)
        for p in nouveaux:
            shutil.move(str(p), str(cible / p.name))
            res["copies"].append(str(cible / p.name))
    if code != 0:
        res["erreur"] = f"WorkBench : code de retour {code}"
    if not any(c.endswith(".csv") for c in res["copies"]):
        res["erreur"] = _concat(res["erreur"], "csv de prédictions absent")
    try:
        res["appels"] = cv.lire_usage_jsonl(usage)
    except ValueError as ex:
        res["erreur"] = _concat(res["erreur"], f"usage illisible : {ex}")
    res["ok"] = res["erreur"] is None
    return res


def prix_json() -> dict:
    return {m: {"entree": v["entree"], "sortie": v["sortie"], "palier": v["palier"], "lecture_cache_x": v["lecture"],
                "ecriture_cache_x": cv.ECRITURE_CACHE} for m, v in cv.PRIX.items()}


def lancer_parties(parties: list, concurrence: int, compta: pe.Comptable, ctx: dict, journal: pe.Journal,
                   executeur=executer_partie, etape: str = "2") -> list:
    """Exécute les parties (1 à 3 à la fois). Avant CHAQUE nouvelle partie : arrêt si le coût cumulé a atteint 80 % du
    plafond. Après chaque partie : usage lu, coût (par appel et par modèle) ajouté, cout.json réécrit.
    Usage illisible, incomplet, modèle inconnu, ou échec : arrêt."""
    file_attente = list(parties)
    verrou = threading.Lock()
    resultats = []
    cout_json = ctx["sortie"] / "cout.json"

    def ecrire_cout():
        pe.ecrire_json_atomique(cout_json, {
            "etape": etape,
            "mode": "réel" if ctx["reel"] else "à blanc",
            "cache": bool(ctx.get("cache")),
            "client_simule": MODELE_USER,
            "prix_usd_par_million": prix_json(),
            "plafond_usd": compta.plafond,
            "seuil_arret_usd": compta.seuil,
            "cumul_usd": round(compta.cumul, 8),
            "arret": compta.arret,
            "usage_estime": any(r.get("estime") for r in resultats),
            "parties": resultats,
        })

    def travailleur():
        while True:
            with verrou:
                if compta.doit_arreter() or not file_attente:
                    return
                partie = file_attente.pop(0)
            journal.ecrire(f"début {partie['id']} ({partie['modele']}, tâche {partie['tache']})")
            try:
                r = executeur(partie, ctx)
            except Exception as e:  # échec inattendu = arrêt, jamais de reprise silencieuse
                r = {"ok": False, "appels": None, "erreur": f"exception {type(e).__name__}", "copies": []}
            ligne = {"id": partie["id"], "env": partie["env"], "modele": partie["modele"], "tache": partie["tache"],
                     "ok": r["ok"], "erreur": r["erreur"]}
            b = None
            if r.get("appels"):
                try:
                    b = cv.bilan(r["appels"], bool(r.get("estime")))
                except ValueError as e:  # modèle inconnu, valeurs incohérentes
                    r = dict(r, ok=False, erreur=_concat(r.get("erreur"), f"usage invalide : {e}"))
                    ligne.update({"ok": False, "erreur": r["erreur"]})
            if b:
                ligne.update(b)
                compta.ajouter(b["cout_usd"])
                if b["appels_hauts"]:
                    journal.ecrire(f"ATTENTION {partie['id']} : {b['appels_hauts']} appel(s) Haiku de plus de "
                                   f"{cv.PRIX['claude-haiku-5-5']['palier'][0]} jetons d'invite, palier haut")
            else:
                ligne.update({"appels": 0, "jetons_entree": None, "jetons_non_caches": None, "cache_ecriture": None,
                              "cache_lecture": None, "jetons_sortie": None, "cout_usd": None})
            if not r["ok"]:
                compta.arreter(f"partie {partie['id']} : {r['erreur']}")
            with verrou:
                resultats.append(ligne)
                ecrire_cout()
            journal.ecrire(f"fin {partie['id']} ok={r['ok']} cumul={compta.cumul:.6f} USD"
                           + (f" erreur={r['erreur']}" if r["erreur"] else ""))

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=concurrence) as ex:
        for f in [ex.submit(travailleur) for _ in range(concurrence)]:
            f.result()
    ecrire_cout()
    if compta.arret:
        journal.ecrire(f"ARRÊT : {compta.arret} ; parties non lancées : {len(file_attente)}")
    return resultats


# --- résumés ------------------------------------------------------------------------------------------------
def _modele_ligne(l: dict) -> str:
    m = l.get("modele") or ""
    return m[len("anthropic/"):] if m.startswith("anthropic/") else (m or "?")


def _somme(d: dict, ps: list, nom: str) -> int:
    return sum(p.get(nom) or 0 for p in ps)


def resume_par_env_modele(lignes: list, parties: list) -> dict:
    """{env: {modèle: parties, actions, lectures, écritures par verdict et par type, jetons dont cache, coût}}."""
    r = {}
    for e in ENVS:
        r[e] = {}
        for m in MODELES:
            ps = [p for p in parties if p["env"] == e and p.get("modele") == m]
            ls = [l for l in lignes if pe.env_de_ligne(l) == e and _modele_ligne(l) == m]
            ecr = [l for l in ls if l["kind"] == "écriture"]
            lect = sum(1 for l in ls if l["kind"] == "lecture")
            r[e][m] = {
                "parties_lancees": len(ps), "parties_ok": sum(1 for p in ps if p["ok"]),
                "actions": len(ls), "lectures": lect, "ecritures": len(ecr), "autres_actions": len(ls) - len(ecr) - lect,
                "ecritures_par_verdict": dict(sorted(pe._compter(l["verdict"] or "sans verdict" for l in ecr).items())),
                "ecritures_par_type": dict(sorted(pe._compter(l["type"] for l in ecr).items())),
                "jetons_entree": _somme(r, ps, "jetons_entree"), "jetons_non_caches": _somme(r, ps, "jetons_non_caches"),
                "cache_ecriture": _somme(r, ps, "cache_ecriture"), "cache_lecture": _somme(r, ps, "cache_lecture"),
                "jetons_sortie": _somme(r, ps, "jetons_sortie"),
                "cout_usd": round(sum(p.get("cout_usd") or 0 for p in ps), 8),
            }
    return r


def resume_par_modele(r: dict) -> dict:
    tot = {}
    for m in MODELES:
        t = {"parties_lancees": 0, "parties_ok": 0, "actions": 0, "lectures": 0, "ecritures": 0, "autres_actions": 0,
             "ecritures_par_verdict": {}, "ecritures_par_type": {}, "jetons_entree": 0, "jetons_non_caches": 0,
             "cache_ecriture": 0, "cache_lecture": 0, "jetons_sortie": 0, "cout_usd": 0.0}
        for e in ENVS:
            v = r[e][m]
            for k in ("parties_lancees", "parties_ok", "actions", "lectures", "ecritures", "autres_actions", "jetons_entree",
                      "jetons_non_caches", "cache_ecriture", "cache_lecture", "jetons_sortie"):
                t[k] += v[k]
            t["cout_usd"] += v["cout_usd"]
            for k in ("ecritures_par_verdict", "ecritures_par_type"):
                for cle, n in v[k].items():
                    t[k][cle] = t[k].get(cle, 0) + n
        t["cout_usd"] = round(t["cout_usd"], 8)
        for k in ("ecritures_par_verdict", "ecritures_par_type"):
            t[k] = dict(sorted(t[k].items()))
        tot[m] = t
    return tot


def _bloc(v: dict) -> str:
    return (f"parties {v['parties_lancees']} (ok {v['parties_ok']}) ; actions {v['actions']} ; lectures {v['lectures']} ; "
            f"écritures {v['ecritures']} ; autres {v['autres_actions']}\n"
            f"  écritures par verdict : {v['ecritures_par_verdict']}\n  écritures par type : {v['ecritures_par_type']}\n"
            f"  jetons d'invite {v['jetons_entree']} (dont cache lu {v['cache_lecture']}, cache écrit {v['cache_ecriture']}, "
            f"non caché {v['jetons_non_caches']}) ; sortie {v['jetons_sortie']} ; coût {v['cout_usd']:.6f} USD")


def resume_texte(r: dict, tot: dict, compta: pe.Comptable, mode: str, etape: str, cache: bool, factice: bool) -> str:
    out = [f"Pilote étape {etape}, mode {mode}, cache {'oui' if cache else 'non'}" + (" (liste de tâches FACTICE)" if factice else ""),
           f"Coût cumulé : {compta.cumul:.6f} USD sur un plafond de {compta.plafond:.2f} USD"
           + (f" ; ARRÊT : {compta.arret}" if compta.arret else ""), ""]
    for e in ENVS:
        for m in MODELES:
            if r[e][m]["parties_lancees"]:
                out += [f"## {e} / {m}", _bloc(r[e][m]), ""]
    out += ["# Par modèle (tous environnements)"]
    for m in MODELES:
        if tot[m]["parties_lancees"]:
            out += [f"## {m}", _bloc(tot[m]), ""]
    return "\n".join(out)


def rapport_2a(parties: list) -> dict:
    """Par partie : cache écrit et lu, part de l'invite lue en cache, coût v2, coût de l'étape 1 pour la même tâche."""
    sortie = []
    for p in parties:
        ref = REF_ETAPE1.get(p["env"])
        cout, ent = p.get("cout_usd"), p.get("jetons_entree")
        lec = p.get("cache_lecture")
        sortie.append({
            "id": p["id"], "env": p["env"], "ok": p["ok"],
            "cache_ecriture": p.get("cache_ecriture"), "cache_lecture": lec, "jetons_entree": ent,
            "jetons_non_caches": p.get("jetons_non_caches"), "jetons_sortie": p.get("jetons_sortie"),
            "part_cache_lu_pct": round(lec / ent * 100, 2) if ent and lec is not None else None,
            "cout_v2_usd": cout, "ref_etape1_usd": ref,
            "variation_pct": round((cout / ref - 1) * 100, 2) if cout is not None and ref else None,
        })
    return {"parties": sortie,
            "cout_v2_total_usd": round(sum(x["cout_v2_usd"] or 0 for x in sortie), 8),
            "ref_etape1_total_usd": round(sum(x["ref_etape1_usd"] or 0 for x in sortie), 8)}


def rapport_2a_texte(r: dict) -> str:
    out = ["Étape 2a : mini-essai du cache (claude-haiku-5-5, cache actif)",
           "Comparaison à l'étape 1 (sans cache, mêmes tâches, autre exécution : le dialogue n'est pas identique).", ""]
    for x in r["parties"]:
        out.append(f"{x['id']} ({x['env']}) ok={x['ok']} : cache écrit {x['cache_ecriture']}, cache lu {x['cache_lecture']} "
                   f"(part de l'invite : {x['part_cache_lu_pct']} %), invite {x['jetons_entree']}, sortie {x['jetons_sortie']} ; "
                   f"coût v2 {x['cout_v2_usd']} USD contre {x['ref_etape1_usd']:.4f} USD à l'étape 1 (variation {x['variation_pct']} %)")
    out.append(f"Total : {r['cout_v2_total_usd']} USD contre {r['ref_etape1_total_usd']:.4f} USD.")
    return "\n".join(out) + "\n"


def post_traitement(sortie: Path, resultats: list, compta: pe.Comptable, mode: str, etape: str, cache: bool, factice: bool,
                    tau2=None, workbench=None) -> dict:
    import verdicts_csv
    tau2, workbench = tau2 or TAU2, workbench or WORKBENCH
    actions = sortie / "actions.csv"
    rc = verdicts_csv.main(["--dossier", str(sortie / "parties"), "--tau2", str(tau2), "--workbench", str(workbench),
                            "--sortie", str(actions)])
    if rc != 0:
        raise ErreurPilote("verdicts_csv.py a échoué")
    lignes = pe.typer_csv(actions, sortie / "actions_typees.csv", workbench)
    r = resume_par_env_modele(lignes, resultats)
    tot = resume_par_modele(r)
    pe.ecrire_json_atomique(sortie / "resume.json", {"etape": etape, "mode": mode, "cache": cache, "liste_taches_factice": factice,
                                                      "cumul_usd": round(compta.cumul, 8), "arret": compta.arret,
                                                      "environnements": r, "modeles": tot})
    (sortie / "resume.txt").write_text(resume_texte(r, tot, compta, mode, etape, cache, factice), encoding="utf-8")
    return r


# --- principal ----------------------------------------------------------------------------------------------
def analyser(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--etape", required=True, choices=("2a", "2"), help="2a : mini-essai du cache ; 2 : 3 modèles x 4 environnements x 10 tâches")
    p.add_argument("--reel", action="store_true", help="appels réels (exige --plafond-usd)")
    p.add_argument("--plafond-usd", type=float, default=None, help="plafond de dépense en USD (2a : au plus 0,10 ; 2 : au plus 40)")
    p.add_argument("--cache", action="store_true", help="active le cache tau2 (forcé en 2a)")
    p.add_argument("--concurrence", type=int, choices=(1, 2, 3), default=None, help="parties simultanées (défaut : 2 ; 1 en 2a)")
    p.add_argument("--developpement", default=str(DEVELOPPEMENT), help="liste des tâches de développement (JSON)")
    p.add_argument("--sortie-racine", default=None)
    a = p.parse_args(argv)
    if a.concurrence is None:
        a.concurrence = CONCURRENCE_DEFAUT[a.etape]
    return a


def verifier_plafond(a) -> float:
    pmax = PLAFOND_MAX[a.etape]
    if a.reel and a.plafond_usd is None:
        raise ErreurPilote("mode réel : --plafond-usd obligatoire")
    plafond = a.plafond_usd if a.plafond_usd is not None else pmax
    if not math.isfinite(plafond) or plafond <= 0:
        raise ErreurPilote("plafond invalide : un nombre positif est attendu")
    if plafond > pmax:
        raise ErreurPilote(f"plafond {plafond} USD refusé : au plus {pmax} USD à l'étape {a.etape}")
    return plafond


def main(argv=None, executeur=executer_partie, base_env=None, chemin_cle=None) -> int:
    a = analyser(argv)
    try:
        plafond = verifier_plafond(a)
        reel = a.reel
        cache = a.cache or a.etape == "2a"
        taches, factice = charger_taches(a.developpement, reel, a.etape)
        cle = pe.lire_cle(chemin_cle or CHEMIN_CLE) if reel else None
        env = pe.env_enfant(os.environ if base_env is None else base_env, cle)
        pe.verifier_env_enfant(env, reel)
        pe.verifier_pas_de_dotenv(TAU2, WB_RUN)
        if not factice:
            verifier_taches_existent(taches)
    except ErreurPilote as e:
        print(f"REFUS : {e}", file=sys.stderr)
        return 2
    mode = "réel" if reel else "à blanc"
    modeles = (MODELES[0],) if a.etape == "2a" else MODELES
    horodatage = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    racine = Path(a.sortie_racine) if a.sortie_racine else SORTIES[a.etape]
    sortie = racine / (horodatage if reel else horodatage + "-blanc")
    sortie.mkdir(parents=True, exist_ok=False)
    journal = pe.Journal(sortie / "journal.log", cle)
    journal.ecrire(f"pilote étape {a.etape}, mode {mode}, plafond {plafond:.2f} USD, concurrence {a.concurrence}, cache {cache}, "
                   f"modèles {', '.join(modeles)}, tâches {'FACTICES' if factice else a.developpement}")
    journal.ecrire("tâches : " + json.dumps(taches, ensure_ascii=False))
    if reel:
        sup = pe.nettoyer_parties_factices(TAU2 / "data" / "simulations")
        journal.ecrire(f"parties factices supprimées : {sup}")
    compta = pe.Comptable(plafond)
    ctx = {"sortie": sortie, "reel": reel, "env_enfant": env, "cle": cle, "horodatage": horodatage, "cache": cache,
           "etape": a.etape, "verrou_wb": threading.Lock()}
    resultats = lancer_parties(construire_parties(taches, modeles), a.concurrence, compta, ctx, journal, executeur, a.etape)
    if a.etape == "2a":
        rap = rapport_2a(resultats)
        pe.ecrire_json_atomique(sortie / "rapport_2a.json", rap)
        (sortie / "rapport_2a.txt").write_text(rapport_2a_texte(rap), encoding="utf-8")
        print(rapport_2a_texte(rap))
    try:
        post_traitement(sortie, resultats, compta, mode, a.etape, cache, factice)
    except (ErreurPilote, ValueError, OSError) as e:
        journal.ecrire(f"post-traitement échoué : {type(e).__name__} {e}")
        return 3
    journal.ecrire(f"terminé : {len(resultats)} parties, cumul {compta.cumul:.6f} USD -> {sortie}")
    print((sortie / "resume.txt").read_text(encoding="utf-8"))
    return 4 if compta.arret else 0


if __name__ == "__main__":
    sys.exit(main())
