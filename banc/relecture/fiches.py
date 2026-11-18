"""Fiches de relecture des alertes (REGLE.md, 5 novembre, points 6 et 7).

A partir d'un dossier de sortie du pilote (actions_typees.csv + parties enregistrees), produit une fiche par
alerte (donc une fiche par conversation une fois le tirage fait : le tirage garde au plus une alerte par
conversation), en deux versions, aveugles toutes les deux (contrôle 1 du 05/11, constat C11) : SANS nom de modèle,
SANS numéro de partie ni de rang, SANS identifiant de tâche.
- version Claude, pour les instances de Claude qui relisent toutes les alertes : elle montre en plus l'identifiant
  opaque de l'alerte, à reporter dans decisions.csv ;
- version aveugle, pour la page d'Otsoa (tirage_aveugle.py) : sans cet identifiant.
La correspondance entre l'identifiant et la partie, le rang, le modèle et la tâche est dans alertes.json, que les
relecteurs ne voient pas.

Ordre d'une fiche (Markdown et page HTML) : encadré factuel en français ; différence champ par champ entre l'appel
de l'agent et l'action attendue la plus proche (calculée ici, pas par une personne) ; énoncé de la tâche ; règles du
domaine utiles à l'outil ; actions attendues ; conversation entière. Aucun avis : ni décision, ni motif, ni preuve de
Claude, ni nombre d'alertes, ni effet d'une levée sur un verdict.

Alerte = écriture dont le verdict automatique est « fausse », « doublon » ou « refusée ».
« doublon sans effet » (REGLE.md, 5 novembre, point 6) est neutre : ce n'est PAS une alerte.
Ne lit que la sortie du pilote (et le règlement du clone tau-bench) : jamais de résultat publié par les bancs.

Usage : python banc/relecture/fiches.py --pilote DOSSIER [--sortie DOSSIER/relecture] [--tau2 CLONE]
Sortie : alertes.json (correspondance, jamais montrée aux relecteurs), decisions_modele.csv (vide),
fiches/{claude,aveugle}/<id>.{json,md}
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Optional

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "banc"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import decisions  # noqa: E402
import verdicts  # noqa: E402

# Liste fermee : verdicts.DOUBLON_SANS_EFFET en est volontairement absent (neutre).
VERDICTS_ALERTE = (verdicts.FAUSSE, verdicts.DOUBLON, verdicts.REFUSEE)
TAU2_PAR_DEFAUT = RACINE / "externe" / "tau2-bench"
ENV_TAU2 = {"airline": "aviation", "retail": "commerce", "banking_knowledge": "banque"}
POLICY_FICHIER = {
    "airline": "data/tau2/domains/airline/policy.md",
    "retail": "data/tau2/domains/retail/policy.md",
    # la banque assemble son règlement à partir de composants : le fichier est le gabarit du mode bm25/grep
    "banking_knowledge": "data/tau2/domains/banking_knowledge/prompts/grep_only.md",
}
MARQUE_SIGNALE = "◄ ACTION SIGNALÉE"
ROLES = {"assistant": "agent", "user": "client", "tool": "outil", "system": "système"}
MOT_GENERIQUES = {"update", "reservation", "details", "create", "delete", "search", "number", "current", "agent",
                  "user", "discoverable", "send", "list", "return", "items", "item", "order", "cancel"}

# ---------------------------------------------------------------------------
# Masquage des noms de modèle (version aveugle)
# ---------------------------------------------------------------------------
JETONS_MODELE = ("claude", "haiku", "sonnet", "opus", "anthropic", "openai", "gpt", "gemini")
_RE_JETON = re.compile(r"[\w.\-]*(?:%s)[\w.\-]*(?:/[\w.\-:]+)?" % "|".join(JETONS_MODELE), re.I)
MASQUE = "[modèle masqué]"


def masquer(texte, noms=()):
    """Remplace tout nom de modèle (noms connus + jetons usuels) par MASQUE. Récursif sur listes et dicts."""
    if isinstance(texte, dict):
        return {masquer(k, noms): masquer(v, noms) for k, v in texte.items()}
    if isinstance(texte, (list, tuple)):
        return [masquer(v, noms) for v in texte]
    if not isinstance(texte, str):
        return texte
    for n in sorted({x for x in noms if x}, key=len, reverse=True):
        texte = re.sub(re.escape(n), MASQUE, texte, flags=re.I)
    return _RE_JETON.sub(MASQUE, texte)


def contient_modele(texte: str, noms=()) -> bool:
    bas = (texte or "").lower()
    return any(j in bas for j in JETONS_MODELE) or any(n and n.lower() in bas for n in noms)


# ---------------------------------------------------------------------------
# Alertes
# ---------------------------------------------------------------------------
def environnement(ligne: dict) -> str:
    if ligne["banc"] == "workbench":
        return "WorkBench"
    return ENV_TAU2.get(ligne["domaine"], ligne["domaine"])


def alerte_id(ligne: dict) -> str:
    """Identifiant stable et opaque : l'environnement, puis 12 caractères du SHA-256 de (tâche, partie, rang).

    Les relecteurs le voient (Claude le reporte dans decisions.csv) : il ne montre donc ni le modèle, ni la partie, ni
    le rang, ni la tâche (contrôle 1 du 05/11, constat C11). La correspondance est dans alertes.json, que les
    relecteurs ne voient pas. Une collision est refusée par lire_alertes."""
    env = environnement(ligne).lower()
    cle = "\x1f".join((str(ligne["tache"]), str(ligne["partie"]), str(int(ligne["rang"]))))
    return f"{env}-{hashlib.sha256(cle.encode('utf-8')).hexdigest()[:12]}"


def lire_alertes(dossier) -> list:
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    chemin = Path(dossier) / "actions_typees.csv"
    with open(chemin, newline="", encoding="utf-8") as fh:
        lignes = list(csv.DictReader(fh))
    alertes = [l for l in lignes if l.get("verdict") in VERDICTS_ALERTE and l.get("kind") == verdicts.ECRITURE]
    for l in alertes:
        l["id"] = alerte_id(l)
    ids = [l["id"] for l in alertes]
    if len(ids) != len(set(ids)):
        raise ValueError("identifiants d'alerte en double")
    return alertes


# ---------------------------------------------------------------------------
# Règlement
# ---------------------------------------------------------------------------
def _blocs(texte: str) -> list:
    """[(section, paragraphe)] ; un bloc de plus de 1200 caractères est coupé par lignes."""
    section, blocs = "", []
    for bloc in re.split(r"\n\s*\n", texte):
        bloc = bloc.strip("\n")
        if not bloc.strip():
            continue
        premiere = bloc.lstrip().splitlines()[0]
        if premiere.startswith("#"):
            section = premiere.lstrip("# ").strip()
        if len(bloc) > 1200:
            blocs += [(section, l) for l in bloc.splitlines() if l.strip()]
        else:
            blocs.append((section, bloc))
    return blocs


def paragraphes_outil(texte: str, outil: str) -> tuple:
    """(paragraphes, mode). Recherche exacte du nom de l'outil ; à défaut, mots de ce nom (recherche élargie)."""
    blocs = _blocs(texte)
    exact = [{"section": s, "texte": b} for s, b in blocs if outil in b]
    if exact:
        return exact, "nom de l'outil"
    mots = [m for m in re.split(r"[_\W]+", outil.lower()) if len(m) >= 5 and m not in MOT_GENERIQUES]
    racines = [m[:-1] if m.endswith("s") else m for m in mots]
    if racines:
        motif = re.compile("|".join(re.escape(r) for r in racines), re.I)
        large = [{"section": s, "texte": b} for s, b in blocs if motif.search(b)]
        if large:
            return large, "mots du nom de l'outil (le nom exact n'apparaît pas dans le règlement) : " + ", ".join(racines)
    return [], "aucun paragraphe ne cite l'outil"


def _reglement(domaine: Optional[str], texte: Optional[str], outil: str, tau2) -> dict:
    if not domaine or domaine not in POLICY_FICHIER:
        return {"chemin": None, "paragraphes": [], "recherche": "",
                "note": "WorkBench n'a pas de règlement de domaine (pas de policy.md)."}
    chemin = Path(tau2) / POLICY_FICHIER[domaine]
    try:
        affiche = str(chemin.relative_to(RACINE))
    except ValueError:
        affiche = str(chemin)
    if texte is None and chemin.is_file():
        texte = chemin.read_text(encoding="utf-8")
    paras, mode = paragraphes_outil(texte or "", outil)
    note = ""
    entier = texte or ""   # relecture C13, P10 : le règlement entier, comme dans la fiche de l'audit
    if domaine == "banking_knowledge":
        note = ("Le règlement de la banque est assemblé à partir de composants du gabarit ; le texte ci-dessous est celui "
                "reçu par l'agent. Les règles d'outils détaillées sont dans la base de connaissances.")
    return {"chemin": affiche, "paragraphes": paras, "recherche": mode, "note": note, "texte_entier": entier}


# ---------------------------------------------------------------------------
# Conversation
# ---------------------------------------------------------------------------
def _json(x) -> str:
    return json.dumps(x, ensure_ascii=False, indent=2, sort_keys=False)


def sans_action_id(actions):
    """Actions attendues de τ-bench sans leur action_id, de la forme « <tâche>_<n> » : il nommerait la tâche dans les
    deux versions de la fiche (C11 ; revue « ultra » du 06/11, constat 6). Le reste de chaque action est gardé."""
    if not isinstance(actions, list):
        return actions
    return [{k: v for k, v in a.items() if k != "action_id"} if isinstance(a, dict) else a for a in actions]


def avertissement_hors(n: int, quoi: str, qui: str = "écriture signalée") -> str:
    """Avertissement d'une écriture introuvable dans la partie, sans son rang (C11 ; revue « ultra » du 06/11, constat 7) :
    le rang reste dans alertes.json (ou audit_tirage.json), que les relecteurs ne voient pas."""
    return f"{qui} hors des {n} {quoi}"


def avertissement_incoherence(nom: str, outil: str, qui: str = "l'appel signalé") -> str:
    """L'appel trouvé à la place de l'écriture n'est pas l'outil du CSV ; sans rang (C11, constat 7)."""
    return f"incohérence : {qui} est {nom}, le CSV dit {outil}"


def _texte_message(m: dict, marque=None) -> str:
    """Texte d'un message ; la ligne de l'appel `marque` (identité de l'objet) porte MARQUE_SIGNALE."""
    parts = []
    c = m.get("content")
    if c:
        parts.append(str(c))
    for tc in m.get("tool_calls") or []:
        who = " (utilisateur)" if tc.get("requestor") == "user" else ""
        ligne = f"[appel d'outil{who}] {tc.get('name')}({json.dumps(tc.get('arguments'), ensure_ascii=False)})"
        if marque is not None and tc is marque:
            ligne += f"   {MARQUE_SIGNALE}"
        parts.append(ligne)
    return "\n".join(parts)


def _message(m: dict, marque=None) -> dict:
    texte = _texte_message(m, marque)
    return {"role": ROLES.get(m.get("role"), str(m.get("role"))), "texte": texte, "signale": MARQUE_SIGNALE in texte}


def _appels_tau2(messages: list) -> tuple:
    """(messages rangés, [(indice du message, appel)]) dans le même ordre que verdicts.appels_tau2."""
    ordre = verdicts._messages_ranges(messages)
    appels = []
    for i, m in enumerate(ordre):
        if m.get("role") != "assistant":
            continue
        for c in m.get("tool_calls") or []:
            if c.get("requestor", "assistant") == "user":
                continue
            appels.append((i, c))
    return ordre, appels


# ---------------------------------------------------------------------------
# Lisibilité : énoncé, actions attendues
# ---------------------------------------------------------------------------
def _valeur_courte(v) -> str:
    return json.dumps(v, ensure_ascii=False, sort_keys=True)


def _appel_lisible(nom: str, arguments: dict) -> str:
    args = ", ".join(f"{k}={_valeur_courte(v)}" for k, v in (arguments or {}).items())
    return f"{nom}({args})"


def enonce_lisible(scenario) -> str:
    """Énoncé du client en « clé : valeur » (les valeurs vides sont omises, les textes gardés tels quels)."""
    if scenario is None or scenario == "":
        return ""
    if not isinstance(scenario, (dict, list)):
        return str(scenario)

    def rendre(x, niveau=0):
        pre = "  " * niveau
        if isinstance(x, dict):
            L = []
            for k, v in x.items():
                if v in (None, "", [], {}):
                    continue
                if isinstance(v, (dict, list)):
                    L.append(f"{pre}{k} :")
                    L += rendre(v, niveau + 1)
                else:
                    corps = str(v).strip().replace("\n", "\n" + pre + "    ")
                    L.append(f"{pre}{k} : {corps}")
            return L
        if isinstance(x, list):
            return [f"{pre}- {_valeur_courte(v) if isinstance(v, (dict, list)) else v}" for v in x]
        return [f"{pre}{x}"]

    return "\n".join(rendre(scenario))


def ligne_attendue(a: "verdicts.Attendue") -> str:
    texte = _appel_lisible(a.nom, a.arguments)
    if a.compare_args is not None:
        texte += (" ; arguments comparés : " + ", ".join(a.compare_args)) if a.compare_args else " ; aucun argument comparé"
    return texte


def attendues_tau2(tache, types=None) -> list:
    """[Attendue] de l'agent (actions « utilisateur » écartées, comme le comparateur)."""
    actions = ((tache or {}).get("evaluation_criteria") or {}).get("actions") or []
    return [verdicts.attendue_depuis_action(a, types) for a in actions if a.get("requestor", "assistant") != "user"]


def attendues_workbench(brut) -> list:
    try:
        chaines = ast.literal_eval(brut) if brut else []
        sortie = []
        for c in chaines:
            nom, args = verdicts.parser_appel_workbench(c)
            sortie.append(verdicts.Attendue(nom=nom, arguments=args))
        return sortie
    except (ValueError, SyntaxError, TypeError):
        return []


# ---------------------------------------------------------------------------
# Différence champ par champ (calculée par le programme)
# ---------------------------------------------------------------------------
ABSENT = object()


def _feuilles(x, chemin="") -> dict:
    """{chemin: valeur} pour les feuilles d'une valeur normalisée ; dict -> « a.b », liste -> « a[0] »."""
    if isinstance(x, dict) and x:
        out = {}
        for k, v in x.items():
            out.update(_feuilles(v, f"{chemin}.{k}" if chemin else str(k)))
        return out
    if isinstance(x, list) and x:
        out = {}
        for i, v in enumerate(x):
            out.update(_feuilles(v, f"{chemin}[{i}]"))
        return out
    return {chemin: x}


def _champ_racine(chemin: str) -> str:
    return re.split(r"[.\[]", chemin, maxsplit=1)[0]


def _score(a: "verdicts.Attendue", arguments: dict) -> tuple:
    na, nb = _feuilles(verdicts.normaliser(arguments)), _feuilles(verdicts.normaliser(a.arguments))
    communs = sum(1 for k, v in nb.items() if k in na and na[k] == v)
    return (communs, -(len(na) + len(nb) - 2 * communs))


def difference(nom: str, arguments: dict, attendues: list) -> dict:
    """Compare l'appel à l'action attendue la plus proche : même outil, le plus de valeurs identiques (à égalité, la
    première de la liste). Retourne {attendue, indice, lignes, champs_differents, note}.
    Une ligne : champ (chemin), agent, attendu, etat, compare (False si le comparateur ignore ce champ), libre (champ
    de texte libre de WorkBench)."""
    memes = [(i, a) for i, a in enumerate(attendues) if a.nom == nom]
    if not memes:
        outils = sorted({a.nom for a in attendues})
        note = "Aucune action attendue n'utilise cet outil."
        if outils:
            note += " Outils des actions attendues : " + ", ".join(outils) + "."
        return {"attendue": None, "indice": None, "lignes": [], "champs_differents": [], "note": note}
    indice, a = max(memes, key=lambda ia: (_score(ia[1], arguments), -ia[0]))
    ag = _feuilles(verdicts.normaliser(arguments or {}))
    at = _feuilles(verdicts.normaliser(a.arguments or {}))
    libres = set(verdicts._champs_libres(nom, arguments or {}))
    lignes, diffs = [], []
    for chemin in list(ag) + [k for k in at if k not in ag]:
        va, vt = ag.get(chemin, ABSENT), at.get(chemin, ABSENT)
        etat = ("absent de l'appel de l'agent" if va is ABSENT else "absent de l'action attendue" if vt is ABSENT
                else "identique" if va == vt else "différent")
        racine = _champ_racine(chemin)
        compare = a.compare_args is None or racine in a.compare_args
        lignes.append({"champ": chemin or "(valeur)", "agent": "" if va is ABSENT else _valeur_courte(va),
                       "attendu": "" if vt is ABSENT else _valeur_courte(vt), "etat": etat, "compare": compare,
                       "libre": racine in libres})
        if etat != "identique" and compare and racine not in diffs:
            diffs.append(racine)
    return {"attendue": ligne_attendue(a), "indice": indice + 1, "lignes": lignes, "champs_differents": diffs, "note": ""}


def encadre(ligne: dict, f: dict, diff: dict, arguments: dict) -> list:
    """Encadré factuel en tête de fiche : une phrase par ligne, sans avis."""
    env = f["environnement"]
    if ligne["banc"] == "workbench":
        env = f"WorkBench, domaine {ligne['domaine']}"
    L = [f"Environnement : {env}.",
         f"Outil appelé : {ligne['outil']} (écriture).",
         "Ce que l'agent a fait : il a appelé " + _appel_lisible(ligne["outil"], arguments) + "."]
    if diff["attendue"]:
        L.append(f"Ce qui était attendu : l'action attendue la plus proche est la n°{diff['indice']} de la liste : "
                 f"{diff['attendue']}.")
    else:
        L.append("Ce qui était attendu : rien de comparable. " + diff["note"])
    v = ligne["verdict"]
    if v == verdicts.FAUSSE:
        ecart = "le comparateur n'a trouvé aucune action attendue encore à faire qui corresponde à cet appel."
        if diff["attendue"]:
            ecart += (" Champs qui diffèrent de l'action la plus proche : " + ", ".join(diff["champs_differents"]) + "."
                      if diff["champs_differents"] else " Aucune différence n'apparaît champ par champ avec l'action la plus proche.")
    elif v == verdicts.DOUBLON:
        ecart = ("le comparateur a trouvé une action attendue identique, mais l'agent l'avait déjà réalisée plus tôt "
                 "dans la conversation : cet appel la répète.")
    else:
        res = (ligne.get("resultat") or f.get("resultat") or "").strip().replace("\n", " ")
        ecart = "l'outil a refusé l'écriture." + (f" Réponse de l'outil : {res[:300]}" if res else "")
    L.append("Écart signalé par le comparateur : " + ecart)
    return L


def _habiller(f: dict, ligne: dict, attendues: list) -> None:
    """Calcule encadré, différence et liste lisible des attendues (champs communs aux deux bancs)."""
    try:
        arguments = json.loads(ligne["arguments"])
        if not isinstance(arguments, dict):
            arguments = {"valeur": arguments}
    except (ValueError, TypeError):
        arguments = {"arguments (illisibles)": ligne["arguments"]}
    f["difference"] = difference(ligne["outil"], arguments, attendues)
    f["encadre"] = encadre(ligne, f, f["difference"], arguments)
    f["attendues_lisibles"] = [f"{k}. {ligne_attendue(a)}" for k, a in enumerate(attendues, 1)]


# ---------------------------------------------------------------------------
# Index des parties du pilote
# ---------------------------------------------------------------------------
def indexer_tau2(dossier) -> dict:
    """{id de partie: (run, tâche, info)} pour tous les results.json sous parties/."""
    index = {}
    for chemin in sorted(Path(dossier).rglob("results.json")):
        data = json.loads(chemin.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "simulations" not in data:
            continue
        taches = {str(t["id"]): t for t in data.get("tasks", [])}
        for run in data["simulations"]:
            index[str(run.get("id"))] = (run, taches.get(str(run.get("task_id"))), data.get("info") or {})
    return index


def _csv_workbench(dossier, stem: str) -> Optional[Path]:
    trouves = sorted(Path(dossier).rglob(stem + ".csv"))
    return trouves[0] if trouves else None


def _attendues_workbench(dossier, texte_tache: str) -> Optional[str]:
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    for chemin in sorted(Path(dossier).rglob("*_tasks_and_outcomes.csv")):
        with open(chemin, newline="", encoding="utf-8") as fh:
            for l in csv.DictReader(fh):
                if l.get("task") == texte_tache:
                    return l.get("outcome")
    return None


# ---------------------------------------------------------------------------
# Construction d'une fiche (structure commune aux deux versions)
# ---------------------------------------------------------------------------
def _base(ligne: dict) -> dict:
    return {
        "id": ligne["id"],
        "environnement": environnement(ligne),
        "banc": ligne["banc"],
        "domaine": ligne["domaine"],
        "tache": ligne["tache"],
        "partie": ligne["partie"],
        "rang": int(ligne["rang"]),
        "verdict_automatique": ligne["verdict"],
        "consigne": "",
        "attendues": "",
        "ecriture": {"outil": ligne["outil"], "arguments": _arguments_lisibles(ligne["arguments"]), "message_agent": ""},
        "resultat": ligne.get("resultat", ""),
        "conversation": [],
        "encadre": [],
        "difference": {},
        "attendues_lisibles": [],
        "reglement": {},
        "etat_initial": None,   # relecture C13, P10 : comme la fiche de l'audit
        "avertissements": [],
    }


def _arguments_lisibles(brut: str) -> str:
    try:
        return _json(json.loads(brut))
    except (ValueError, TypeError):
        return brut


def _fiche_tau2(ligne, index, tau2, types=None) -> dict:
    f = _base(ligne)
    if ligne["partie"] not in index:
        raise ValueError(f"partie {ligne['partie']} introuvable dans les results.json du dossier")
    run, tache, info = index[ligne["partie"]]
    if tache is None:
        f["avertissements"].append("tâche introuvable dans results.json")
    else:
        f["consigne"] = enonce_lisible(tache.get("user_scenario"))
        f["attendues"] = _json(sans_action_id((tache.get("evaluation_criteria") or {}).get("actions")))
        f["etat_initial"] = tache.get("initial_state") or None
    ordre, appels = _appels_tau2(run.get("messages") or [])
    rang = int(ligne["rang"])
    if rang >= len(appels):
        f["avertissements"].append(avertissement_hors(len(appels), "appels de la partie") + " : conversation non retrouvée")
    else:
        i, appel = appels[rang]
        nom, _, _ = verdicts._deballer(appel["name"], appel.get("arguments") or {})
        if nom != ligne["outil"]:
            f["avertissements"].append(avertissement_incoherence(nom, ligne["outil"]))
        f["ecriture"]["message_agent"] = str(ordre[i].get("content") or "")
        f["conversation"] = [_message(m, appel if k == i else None) for k, m in enumerate(ordre)]
    domaine = (info.get("environment_info") or {}).get("domain_name") or ligne["domaine"]
    f["reglement"] = _reglement(domaine, run.get("policy"), ligne["outil"], tau2)
    f["modele"] = ligne.get("modele") or (info.get("agent_info") or {}).get("llm") or ""
    _habiller(f, ligne, attendues_tau2(tache, types))
    return f


def _fiche_workbench(ligne, dossier, tau2) -> dict:
    f = _base(ligne)
    stem, _, i = str(ligne["partie"]).rpartition(":")
    chemin = _csv_workbench(dossier, stem)
    if chemin is None or not i.isdigit():
        raise ValueError(f"partie WorkBench {ligne['partie']} introuvable dans le dossier")
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    with open(chemin, newline="", encoding="utf-8") as fh:
        lignes = list(csv.DictReader(fh))
    i = int(i)
    rangee = lignes[i]
    texte = rangee["task"]
    f["consigne"] = texte
    attendues = _attendues_workbench(dossier, texte)
    if attendues is None:
        f["avertissements"].append("actions attendues introuvables dans taches/")
        attendues = ""
    f["attendues"] = attendues
    messages = [{"role": "client", "texte": texte, "signale": False}]
    traces_chemin = chemin.with_name(stem + "_traces.json")
    rang = int(ligne["rang"])
    if traces_chemin.is_file():
        traces = json.loads(traces_chemin.read_text(encoding="utf-8"))
        entree = traces[i] if i < len(traces) and traces[i].get("task") == texte else None
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
                f["avertissements"].append("le nombre d'étapes d'outil ne coïncide pas avec function_calls : rang approximatif")
            if rang >= len(outils):
                f["avertissements"].append(avertissement_hors(len(outils), "étapes d'outil"))
            else:
                debut = outils[rang]
                for k, s in enumerate(steps):
                    messages += _messages_step(s, signale=(k == debut))
                s = steps[debut]
                f["ecriture"]["message_agent"] = _contenu_step(s)
                f["resultat"] = f["resultat"] or str(s.get("observation", ""))
    else:
        f["avertissements"].append("traces absentes : conversation limitée à la consigne")
    f["conversation"] = messages
    f["reglement"] = _reglement(None, None, ligne["outil"], tau2)
    f["modele"] = ligne.get("modele") or ""
    _habiller(f, ligne, attendues_workbench(attendues))
    return f


def _contenu_step(s: dict) -> str:
    try:
        return str(json.loads(s.get("llm_output") or "{}").get("content") or "")
    except (ValueError, AttributeError):
        return ""


def _messages_step(s: dict, signale: bool = False) -> list:
    if s.get("action") in verdicts._OBSERVATION_SANS_OUTIL:
        corps = s.get("action_input") if s.get("action") == "Final Answer" else s.get("observation")
        contenu = _contenu_step(s)
        texte = (contenu + "\n" if contenu else "") + f"[réponse finale] {corps}"
        return [{"role": "agent", "texte": texte, "signale": False}]
    appel = f"[appel d'outil] {s.get('action')}({json.dumps(s.get('action_input'), ensure_ascii=False)})"
    if signale:
        appel += f"   {MARQUE_SIGNALE}"
    contenu = _contenu_step(s)
    return [
        {"role": "agent", "texte": (contenu + "\n" if contenu else "") + appel, "signale": signale},
        {"role": "outil", "texte": str(s.get("observation", "")), "signale": False},
    ]


# ---------------------------------------------------------------------------
# Rendu Markdown
# ---------------------------------------------------------------------------
def _bloc(texte: str) -> str:
    texte = texte if texte else "(vide)"
    plus_long = max((len(m) for m in re.findall(r"`+", texte)), default=0)
    barre = "`" * max(3, plus_long + 1)
    return f"{barre}\n{texte}\n{barre}"


def _cellule(t: str) -> str:
    return (t or "").replace("|", "\\|").replace("\n", " ")


def tableau_difference_md(d: dict) -> list:
    if not d.get("lignes"):
        return [d.get("note") or "(rien à comparer)"]
    L = [f"Action attendue la plus proche (n°{d['indice']}) : `{d['attendue']}`", "",
         "| Champ | Appel de l'agent | Action attendue | Écart |", "|---|---|---|---|"]
    for l in d["lignes"]:
        etat = l["etat"] + ("" if l["compare"] else " (champ non comparé)") + (" (texte libre)" if l["libre"] else "")
        L.append(f"| `{_cellule(l['champ'])}` | {_cellule(l['agent'])} | {_cellule(l['attendu'])} | {etat} |")
    return L


def rendre_markdown(f: dict, aveugle: bool) -> str:
    """Ordre : encadré, différence champ par champ, énoncé, règles du domaine, actions attendues, conversation.

    Les deux versions n'ont ni modèle, ni partie, ni rang, ni tâche (contrôle 1, C11). La version Claude montre en plus
    l'identifiant opaque de l'alerte, à reporter dans decisions.csv ; la version aveugle (page d'Otsoa) ne le montre pas."""
    if aveugle:
        L = ["# Fiche (version aveugle)", ""]
    else:  # le mot du nom de modèle n'apparaît pas non plus dans l'en-tête : la fiche passe le même contrôle
        L = [f"# Fiche {f['id']} (version de relecture, aveugle)", "",
             f"- Identifiant de l'alerte, à reporter dans decisions.csv : {f['id']}", ""]
    L += ["## Résumé", ""] + [f"> {x}" for x in f["encadre"]]
    for a in f["avertissements"]:
        L += ["", f"ATTENTION : {a}"]
    L += ["", "## Différence champ par champ", ""] + tableau_difference_md(f["difference"])
    L += ["", "## Énoncé de la tâche", "", _bloc(f["consigne"])]
    r = f["reglement"]
    L += ["", "## Règles du domaine utiles à l'outil", ""]
    if r.get("chemin"):
        L += [f"Fichier : `{r['chemin']}`", f"Recherche : {r['recherche']}"]
    if r.get("note"):
        L.append(r["note"])
    for p in r.get("paragraphes", []):
        L += ["", f"Section : {p['section'] or '(sans titre)'}", "", _bloc(p["texte"])]
    if r.get("chemin") and not r.get("paragraphes"):
        L += ["", "Aucun paragraphe du règlement ne cite cet outil."]
    if r.get("texte_entier"):
        L += ["", "## Règlement entier (tel que reçu par l'agent)", "", _bloc(r["texte_entier"])]
    if f.get("banc") != "workbench":
        L += ["", "## État initial propre à la tâche", "",
              _bloc(_json(f["etat_initial"])) if f.get("etat_initial") else "(aucun : la tâche part de la base commune)"]
    L += ["", "## Actions attendues de la tâche", "", _bloc("\n".join(f["attendues_lisibles"]))]
    L += ["", "## Conversation entière", ""]
    if not f["conversation"]:
        L.append("(aucun message retrouvé)")
    for k, m in enumerate(f["conversation"], 1):
        L += [f"### {k}. {m['role']}", "", _bloc(m["texte"]), ""]
    return "\n".join(L).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Production
# ---------------------------------------------------------------------------
# Absents des deux versions (aveugle et Claude, contrôle 1, C11) : le modèle ; la partie (son identifiant peut contenir
# le nom du modèle, et son numéro ou celui du passage trahit le modèle) ; le rang ; l'identifiant de tâche (WorkBench le
# construit avec un numéro de ligne). Ils restent dans alertes.json, que les relecteurs ne voient pas.
CHAMPS_CACHES = ("modele", "partie", "rang", "tache")


def version_aveugle(f: dict, noms) -> dict:
    """Copie de la fiche sans modèle, partie, rang ni tâche ; noms de modèle masqués partout."""
    b = {k: v for k, v in f.items() if k not in CHAMPS_CACHES}
    b = masquer(b, noms)
    b["version"] = "aveugle"
    return b


def version_claude(aveugle: dict) -> dict:
    """Fiche des instances de Claude qui relisent toutes les alertes (contrôle 1, C11) : la version aveugle, avec
    l'identifiant opaque de l'alerte (déjà présent dans « id ») ; ni modèle, ni partie, ni rang, ni tâche.
    Son étiquette est « relecture » : le mot du nom de modèle ne doit apparaître nulle part dans la fiche."""
    return {**aveugle, "version": "relecture"}


def produire(dossier, sortie=None, tau2=TAU2_PAR_DEFAUT) -> list:
    dossier = Path(dossier)
    sortie = Path(sortie) if sortie else dossier / "relecture"
    alertes = lire_alertes(dossier)
    index = indexer_tau2(dossier) if any(a["banc"] != "workbench" for a in alertes) else {}
    for sous in ("claude", "aveugle"):
        (sortie / "fiches" / sous).mkdir(parents=True, exist_ok=True)
    resume = []
    types_cache: dict = {}

    def types_du_domaine(domaine):
        """Types et valeurs par défaut des outils tau2 (pour compléter les deux côtés de la différence)."""
        if domaine not in types_cache:
            try:
                types_cache[domaine] = verdicts.types_tau2(tau2, domaine)
            except (FileNotFoundError, OSError, ValueError):
                types_cache[domaine] = None
        return types_cache[domaine]

    for l in alertes:
        f = (_fiche_workbench(l, dossier, tau2) if l["banc"] == "workbench"
             else _fiche_tau2(l, index, tau2, types_du_domaine(l["domaine"])))
        noms = {l.get("modele", ""), f.get("modele", ""), str(l["partie"])} - {""}
        noms |= {n.split("/")[-1] for n in noms}
        aveugle = version_aveugle(f, noms)
        claude = version_claude(aveugle)
        md_aveugle, md_claude = rendre_markdown(aveugle, True), rendre_markdown(claude, False)
        for nom_version, fiche, md in (("Claude", claude, md_claude), ("aveugle", aveugle, md_aveugle)):
            # noms contient aussi l'identifiant de la partie : ni modèle ni partie dans aucune des deux versions
            if contient_modele(md + json.dumps(fiche, ensure_ascii=False), noms):
                raise AssertionError(f"nom de modèle ou partie présent dans la fiche {nom_version} {l['id']}")
        for sous, fiche, md in (("claude", claude, md_claude), ("aveugle", aveugle, md_aveugle)):
            base = sortie / "fiches" / sous / l["id"]
            base.with_suffix(".json").write_text(json.dumps(fiche, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            base.with_suffix(".md").write_text(md, encoding="utf-8")
        resume.append({
            "id": l["id"], "environnement": f["environnement"], "banc": l["banc"], "domaine": l["domaine"],
            "tache": l["tache"], "partie": l["partie"], "rang": int(l["rang"]), "outil": l["outil"],
            "verdict": l["verdict"], "enjeu": l.get("enjeu", ""), "modele": f.get("modele", ""),
            "avertissements": f["avertissements"],
        })
    # alertes.json est la correspondance identifiant -> partie, rang, modèle, tâche : jamais montrée aux relecteurs (C11)
    (sortie / "alertes.json").write_text(json.dumps(resume, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    decisions.ecrire_modele(sortie / "decisions_modele.csv")
    return resume


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pilote", required=True, help="dossier de sortie du pilote (avec actions_typees.csv)")
    p.add_argument("--sortie", help="défaut : <pilote>/relecture")
    p.add_argument("--tau2", default=str(TAU2_PAR_DEFAUT), help="clone tau-bench (chemin du règlement)")
    a = p.parse_args(argv)
    try:
        resume = produire(a.pilote, a.sortie, a.tau2)
    except (ValueError, FileNotFoundError) as e:
        print(f"erreur: {e}", file=sys.stderr)
        return 2
    for r in resume:
        print(f"{r['id']}  {r['verdict']}  {r['outil']}")
    print(f"{len(resume)} alertes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
