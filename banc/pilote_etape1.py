"""Pilote, étape 1 de l'expérience « autonomie méritée » : 3 parties par environnement, claude-haiku-5-5
(agent et client simulé), 1 essai par tâche.

Environnements : aviation (tau2 airline), commerce (tau2 retail), banque (tau2 banking_knowledge, bm25_grep),
WorkBench. Tâches : les 3 premières de chaque liste de banc/tirage/developpement.json (lu à l'exécution).

MODE PAR DÉFAUT : À BLANC. Aucune clé n'est lue, aucun appel réseau n'est fait : les bancs tournent sur leurs
réponses factices (tau2 : mock_response ; WorkBench : PILOTE_HORS_LIGNE=2), proxys cassés, et l'usage manquant est
ESTIMÉ (caractères / 4) et marqué `estime`. Le mode réel exige `--reel` ET `--plafond-usd X` (X <= 1.00).

    python banc/pilote_etape1.py                                  # à blanc
    python banc/pilote_etape1.py --reel --plafond-usd 1.00        # réel (voir INSTALLATION.md, section 7)

Garde-fous (réel) : clé lue seulement dans ~/.config/autonomie-meritee/anthropic.env (permissions 600, non vide),
jamais affichée ni journalisée ni passée en argument : elle n'existe que dans l'environnement des enfants, nettoyé de
toute autre clé de fournisseur ; coût calculé après chaque partie depuis l'usage enregistré ; arrêt avant toute
nouvelle partie à 80 % du plafond, ou dès qu'un usage est illisible, ou si un enfant échoue.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import socket
import stat
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

BANC = Path(__file__).resolve().parent
if str(BANC) not in sys.path:
    sys.path.insert(0, str(BANC))

RACINE = BANC.parent
TAU2 = RACINE / "externe" / "tau2-bench"
WORKBENCH = RACINE / "externe" / "WorkBench"
WB_RUN = RACINE / "externe" / "workbench-run"
DEVELOPPEMENT = BANC / "tirage" / "developpement.json"
SORTIE_RACINE = RACINE / "pilote" / "etape1"
CHEMIN_CLE = Path.home() / ".config" / "autonomie-meritee" / "anthropic.env"

MODELE_TAU = "anthropic/claude-haiku-5-5"
MODELE_WB = "claude-haiku-5-5"

# Prix de claude-haiku-5-5 (décision d'Otsoa), en USD par million de jetons.
PRIX_ENTREE_M = 0.10
PRIX_SORTIE_M = 0.50
SEUIL_DOUBLE = 100_000  # jetons d'entrée par appel au-delà desquels l'appel est compté au double (prudence)
PLAFOND_MAX = 1.00
FRACTION_ARRET = 0.80
PARTIES_PAR_ENV = 3
DELAI_PARTIE_S = 1800
MAX_PAS_REEL = 100  # tours au plus par partie tau2 en réel (défaut du banc : 200)
PREFERENCE_WB = ("email", "calendar", "customer_relationship_manager")

ENVS = ("aviation", "commerce", "banque", "WorkBench")
DOMAINE_TAU = {"aviation": "airline", "commerce": "retail", "banque": "banking_knowledge"}
ENV_DE_DOMAINE = {v: k for k, v in DOMAINE_TAU.items()}

# Tâches factices (blanc seulement, si developpement.json n'existe pas) : identifiants valides des bancs.
LISTE_FACTICE = {
    "aviation": ["0", "1", "2"],
    "commerce": ["0", "1", "2"],
    "banque": ["task_001", "task_002", "task_003"],
    "WorkBench": ["email:0", "email:1", "email:2"],
}

# --- environnement des enfants -------------------------------------------------------------------------------
AUTRES_FOURNISSEURS = (
    "OPENAI_API_KEY", "OPENROUTER_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY", "XAI_API_KEY", "AZURE_API_KEY",
    "MISTRAL_API_KEY", "ANTHROPIC_AUTH_TOKEN",
)
# Tout nom commençant par l'un de ces préfixes est retiré (autres fournisseurs, passerelles, redirections d'URL).
PREFIXES_RETIRES = (
    "ANTHROPIC_", "OPENAI_", "OPENROUTER_", "AZURE_", "GEMINI_", "GOOGLE_", "VERTEX", "AWS_", "MISTRAL_", "XAI_",
    "GROQ_", "COHERE_", "DEEPSEEK_", "TOGETHER", "FIREWORKS", "PERPLEXITY_", "HF_", "HUGGINGFACE", "REPLICATE_",
    "LITELLM_", "PILOTE_", "OLLAMA_", "NVIDIA_", "CEREBRAS_", "VOYAGE_", "JINA_",
)
MOTIF_SECRET = re.compile(r"(API_KEY|AUTH_TOKEN|ACCESS_TOKEN|SECRET|CREDENTIALS)", re.I)
PROXY_CASSE = "http://127.0.0.1:9"


class ErreurPilote(Exception):
    """Refus ou arrêt du pilote. Le message ne contient jamais la clé."""


def lire_cle(chemin) -> str:
    """Clé Anthropic depuis une ligne `ANTHROPIC_API_KEY=...` du fichier. Refus : fichier absent, non régulier,
    permissions autres que 600, ligne absente, clé vide. La clé n'apparaît dans aucun message d'erreur."""
    chemin = Path(chemin)
    try:
        st = os.stat(chemin)
    except OSError:
        raise ErreurPilote(f"fichier de clé introuvable : {chemin}")
    if not stat.S_ISREG(st.st_mode):
        raise ErreurPilote(f"fichier de clé : pas un fichier régulier : {chemin}")
    mode = stat.S_IMODE(st.st_mode)
    if mode != 0o600:
        raise ErreurPilote(f"fichier de clé : permissions {oct(mode)} au lieu de 0o600 : {chemin}")
    cle = None
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if ligne.startswith("export "):
            ligne = ligne[len("export "):].lstrip()
        if ligne.startswith("ANTHROPIC_API_KEY="):
            cle = ligne.split("=", 1)[1].strip()
            if len(cle) >= 2 and cle[0] == cle[-1] and cle[0] in "\"'":
                cle = cle[1:-1].strip()
    if cle is None:
        raise ErreurPilote(f"fichier de clé : ligne ANTHROPIC_API_KEY=... absente : {chemin}")
    if not cle:
        raise ErreurPilote(f"fichier de clé : clé vide : {chemin}")
    return cle


def _a_retirer(nom: str) -> bool:
    n = nom.upper()
    return n in AUTRES_FOURNISSEURS or n.startswith(PREFIXES_RETIRES) or bool(MOTIF_SECRET.search(n))


def env_enfant(base, cle=None) -> dict:
    """Environnement des processus enfants. Retire toute clé ou jeton de fournisseur (AUTRES_FOURNISSEURS, préfixes,
    noms contenant API_KEY / TOKEN / SECRET...). Réel (`cle` donnée) : ne laisse que ANTHROPIC_API_KEY. À blanc : aucune
    clé, proxys cassés, WorkBench hors ligne."""
    env = {k: v for k, v in base.items() if not _a_retirer(k)}
    env["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    if cle:
        env["ANTHROPIC_API_KEY"] = cle
    else:
        env["PILOTE_HORS_LIGNE"] = "2"
        for k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
            env[k] = PROXY_CASSE
        env["NO_PROXY"] = ""
        env["no_proxy"] = ""
    return env


def verifier_env_enfant(env, reel: bool) -> None:
    """Contrôle d'impossibilité de facturer un autre fournisseur. Réel : clé Anthropic présente, clé OpenRouter (et
    toute autre) absente, donc WorkBench ne peut pas basculer sur OpenRouter. À blanc : aucune clé."""
    mauvais = sorted(k for k in env if k != "ANTHROPIC_API_KEY" and _a_retirer(k) and k != "LITELLM_LOCAL_MODEL_COST_MAP"
                     and k != "PILOTE_HORS_LIGNE")
    if mauvais:
        raise ErreurPilote(f"environnement des enfants : variables de fournisseur présentes : {', '.join(mauvais)}")
    if reel:
        if not env.get("ANTHROPIC_API_KEY"):
            raise ErreurPilote("environnement des enfants : clé Anthropic absente (WorkBench basculerait sur OpenRouter)")
        if "PILOTE_HORS_LIGNE" in env:
            raise ErreurPilote("environnement des enfants : PILOTE_HORS_LIGNE présent en mode réel")
    else:
        if "ANTHROPIC_API_KEY" in env:
            raise ErreurPilote("mode à blanc : une clé Anthropic est présente dans l'environnement des enfants")


def verifier_pas_de_dotenv(*dossiers) -> None:
    """tau2 et WorkBench chargent un `.env` du dossier courant : il pourrait réintroduire une clé d'un autre fournisseur."""
    for d in dossiers:
        if (Path(d) / ".env").exists():
            raise ErreurPilote(f"un fichier .env existe dans {d} : refus (il pourrait ajouter une clé de fournisseur)")


# --- coût --------------------------------------------------------------------------------------------------
def cout_appel(prompt_tokens: int, completion_tokens: int) -> tuple:
    """(coût USD, doublé ?). Un appel de plus de SEUIL_DOUBLE jetons d'entrée est compté au double."""
    c = (prompt_tokens * PRIX_ENTREE_M + completion_tokens * PRIX_SORTIE_M) / 1e6
    double = prompt_tokens > SEUIL_DOUBLE
    return (c * 2 if double else c), double


def _entier_ok(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool) and x >= 0


def _estimer(messages: list, i: int) -> dict:
    """Usage estimé (blanc seulement) : entrée = caractères de l'historique / 4, sortie = caractères du message / 4."""
    avant = sum(len(json.dumps(m, ensure_ascii=False)) for m in messages[:i])
    return {"prompt_tokens": avant // 4 + 1, "completion_tokens": len(json.dumps(messages[i], ensure_ascii=False)) // 4 + 1}


def appels_tau2(chemin_results, estimer: bool = False) -> list:
    """[(prompt, completion, estime)] pour chaque appel de modèle (messages assistant et user) d'un results.json tau2.
    ValueError si l'usage est illisible : fichier absent ou invalide, pas une seule simulation, message sans usage entier
    (hors salutation initiale de l'agent, qui n'appelle aucun modèle), ou total nul. `estimer` (blanc) comble les manques."""
    try:
        data = json.loads(Path(chemin_results).read_text(encoding="utf-8"))
        sims = data["simulations"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise ValueError(f"results.json illisible : {type(e).__name__}")
    if not isinstance(sims, list) or len(sims) != 1:
        raise ValueError("results.json : une simulation attendue")
    messages = sims[0].get("messages")
    if not isinstance(messages, list) or not messages:
        raise ValueError("results.json : aucun message")
    appels = []
    for i, m in enumerate(messages):
        if not isinstance(m, dict) or m.get("role") not in ("assistant", "user"):
            continue
        if i == 0 and m.get("role") == "assistant" and m.get("usage") is None:
            continue
        u = m.get("usage")
        if isinstance(u, dict) and _entier_ok(u.get("prompt_tokens")) and _entier_ok(u.get("completion_tokens")):
            appels.append((u["prompt_tokens"], u["completion_tokens"], False))
        elif estimer:
            e = _estimer(messages, i)
            appels.append((e["prompt_tokens"], e["completion_tokens"], True))
        else:
            raise ValueError(f"message {i} sans usage lisible")
    if not appels or sum(a + b for a, b, _ in appels) == 0:
        raise ValueError("usage nul ou absent")
    return appels


def appels_workbench(chemin_usage) -> list:
    """[(prompt, completion, False)] depuis le JSONL écrit par banc/usage_wrap.py. ValueError si illisible."""
    try:
        lignes = [json.loads(x) for x in Path(chemin_usage).read_text(encoding="utf-8").splitlines() if x.strip()]
    except (OSError, ValueError):
        raise ValueError("fichier d'usage WorkBench illisible")
    if not lignes:
        raise ValueError("fichier d'usage WorkBench vide")
    appels = []
    for k, l in enumerate(lignes):
        if not (isinstance(l, dict) and _entier_ok(l.get("prompt_tokens")) and _entier_ok(l.get("completion_tokens"))):
            raise ValueError(f"appel {k} sans usage lisible")
        appels.append((l["prompt_tokens"], l["completion_tokens"], False))
    return appels


def bilan_appels(appels: list) -> dict:
    cout, doubles, estime, ent, sor = 0.0, 0, False, 0, 0
    for p, c, est in appels:
        x, d = cout_appel(p, c)
        cout += x
        doubles += int(d)
        estime = estime or est
        ent += p
        sor += c
    return {"appels": len(appels), "appels_doubles": doubles, "jetons_entree": ent, "jetons_sortie": sor,
            "cout_usd": round(cout, 8), "estime": estime}


class Comptable:
    """Coût cumulé et règle d'arrêt. `cout_usd` n'est jamais diminué. Sûr entre fils d'exécution."""

    def __init__(self, plafond: float):
        self.plafond = plafond
        self.seuil = plafond * FRACTION_ARRET
        self.cumul = 0.0
        self.arret = None
        self._verrou = threading.Lock()

    def ajouter(self, cout: float) -> None:
        with self._verrou:
            self.cumul += cout
            if self.arret is None and self.cumul >= self.seuil - 1e-12:
                self.arret = f"coût cumulé {self.cumul:.6f} USD >= {int(FRACTION_ARRET * 100)} % du plafond ({self.seuil:.6f} USD)"

    def arreter(self, raison: str) -> None:
        with self._verrou:
            if self.arret is None:
                self.arret = raison

    def doit_arreter(self) -> bool:
        with self._verrou:
            return self.arret is not None


# --- tâches ---------------------------------------------------------------------------------------------------
def charger_taches(chemin, reel: bool, n: int = PARTIES_PAR_ENV) -> tuple:
    """({env: [n premiers ids dans l'ordre de la liste]}, factice ?). Fichier absent : réel = refus, blanc = liste factice."""
    chemin = Path(chemin)
    if not chemin.is_file():
        if reel:
            raise ErreurPilote(f"liste des tâches introuvable : {chemin}")
        return {e: list(v[:n]) for e, v in LISTE_FACTICE.items()}, True
    try:
        data = json.loads(chemin.read_text(encoding="utf-8"))
    except ValueError:
        raise ErreurPilote(f"liste des tâches illisible : {chemin}")
    sortie = {}
    for e in ENVS:
        ids = data.get(e) if isinstance(data, dict) else None
        if not isinstance(ids, list) or len(ids) < n or not all(isinstance(i, str) and i for i in ids[:n]):
            raise ErreurPilote(f"liste des tâches : au moins {n} identifiants (chaînes) attendus pour {e}")
        sortie[e] = list(ids[:n])
    # WorkBench : une tâche par fichier (mail, agenda, fichier clients), pour faire passer de vraies écritures dans la
    # chaîne de contrôle (retouche du coordinateur, 05/11). Repli sur l'ordre de la liste si un fichier manque.
    choix = []
    for prefixe in PREFERENCE_WB[:n]:
        trouve = next((i for i in data["WorkBench"] if isinstance(i, str) and i.split(":", 1)[0] == prefixe), None)
        if trouve:
            choix.append(trouve)
    if len(choix) == n:
        sortie["WorkBench"] = choix
    return sortie, False


def verifier_taches_existent(taches: dict, tau2=TAU2, workbench=WORKBENCH) -> None:
    """Contrôle avant tout appel : chaque identifiant existe dans le banc correspondant."""
    for env, dom in DOMAINE_TAU.items():
        chemin = Path(tau2) / "data" / "tau2" / "domains" / dom / "tasks.json"
        connus = {str(t["id"]) for t in json.loads(chemin.read_text(encoding="utf-8"))}
        for i in taches[env]:
            if i not in connus:
                raise ErreurPilote(f"{env} : tâche {i!r} absente de {chemin.name}")
    from verdicts import charger_taches_workbench
    connus = set(charger_taches_workbench(workbench))
    for i in taches["WorkBench"]:
        if i not in connus:
            raise ErreurPilote(f"WorkBench : tâche {i!r} inconnue")


def construire_parties(taches: dict) -> list:
    """Parties intercalées par rang (tâche 1 de chaque environnement, puis tâche 2...) : un arrêt anticipé laisse
    une couverture équilibrée."""
    parties = []
    n = max(len(v) for v in taches.values())
    for rang in range(n):
        for env in ENVS:
            if rang < len(taches[env]):
                parties.append({"id": f"{env}-{rang + 1}", "env": env, "tache": taches[env][rang], "rang": rang + 1})
    return parties


# --- commandes ----------------------------------------------------------------------------------------------
def _mock_tau(env: str) -> tuple:
    """(args agent, args client, max-steps) factices pour l'essai à blanc : réponses LiteLLM `mock_response`."""
    outil = {"aviation": "list_all_airports", "commerce": "list_all_product_types", "banque": None}[env]
    agent = {"temperature": 0.0, "mock_response": "ok"}
    if outil:
        agent["mock_tool_calls"] = [{"id": "call_1", "type": "function", "function": {"name": outil, "arguments": "{}"}}]
        return agent, {"temperature": 0.0, "mock_response": "Hello, I want to check my reservation."}, 8
    return agent, {"temperature": 0.0, "mock_response": "Thanks. ###STOP###"}, 8


def commande_tau2(partie: dict, nom_sauvegarde: str, reel: bool) -> list:
    """Ligne de commande (sans aucune clé) d'une partie tau2. Évaluation ENV seule (tau2_sans_juge.py) : aucun juge OpenAI."""
    env = partie["env"]
    cmd = [str(TAU2 / ".venv" / "bin" / "python"), str(BANC / "tau2_sans_juge.py"), "run", "--domain", DOMAINE_TAU[env]]
    if reel:
        # Réglages vides et explicites : sinon tau2 ajoute `temperature`, que les modèles 5.5 refusent
        # (« `temperature` is deprecated for this model », essai réel du 05/11 à 7 h 23, aucune dépense).
        args_agent = args_user = {}
        extra = ["--max-steps", str(MAX_PAS_REEL)]  # borne une partie qui tournerait en boucle (le plafond est vérifié entre parties)
    else:
        args_agent, args_user, pas = _mock_tau(env)
        extra = ["--max-steps", str(pas)]
    cmd += ["--agent-llm", MODELE_TAU, "--user-llm", MODELE_TAU,
            "--agent-llm-args", json.dumps(args_agent), "--user-llm-args", json.dumps(args_user)]
    if env == "aviation":
        cmd += ["--communicate-scorer", "substring"]
    if env == "banque":
        cmd += ["--retrieval-config", "bm25_grep"]
    cmd += ["--task-ids", partie["tache"], "--num-trials", "1", "--max-concurrency", "1", "--save-to", nom_sauvegarde] + extra
    return cmd


def commande_workbench(chemin_taches: Path) -> list:
    cmd = [str(WORKBENCH / ".venv" / "bin" / "python"), str(BANC / "workbench_pilote.py"), "--model_name", MODELE_WB,
           "--tasks_path", str(chemin_taches), "--tool_selection", "all", "--workers", "1", "--log_traces",
           "--structured_outputs"]
    return cmd


def ecrire_taches_workbench(partie: dict, dossier: Path, workbench=WORKBENCH) -> Path:
    """CSV d'une seule tâche (mêmes colonnes que l'original) sous `dossier`/<préfixe>_tasks_and_outcomes.csv.
    Le préfixe du nom de fichier sert de domaine à WorkBench et à verdicts.py."""
    prefixe, num = partie["tache"].split(":")
    source = Path(workbench) / "data" / "processed" / "tasks_and_outcomes" / f"{prefixe}_tasks_and_outcomes.csv"
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    with open(source, newline="", encoding="utf-8") as fh:
        lecteur = csv.DictReader(fh)
        lignes = list(lecteur)
        champs = lecteur.fieldnames
    dossier.mkdir(parents=True, exist_ok=True)
    sortie = dossier / f"{prefixe}_tasks_and_outcomes.csv"
    with open(sortie, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=champs, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerow(lignes[int(num)])
    return sortie


# --- exécution ---------------------------------------------------------------------------------------------
class Journal:
    def __init__(self, chemin: Path, cle=None):
        self.chemin = chemin
        self.cle = cle
        self._verrou = threading.Lock()

    def purger(self, texte: str) -> str:
        return texte.replace(self.cle, "***") if self.cle else texte

    def ecrire(self, texte: str) -> None:
        ligne = f"{datetime.now().isoformat(timespec='seconds')} {self.purger(texte)}"
        with self._verrou:
            with open(self.chemin, "a", encoding="utf-8") as fh:
                fh.write(ligne + "\n")
        print(ligne, flush=True)


def nettoyer_parties_factices(dossier_simulations: Path) -> list:
    """Supprime les dossiers `essai-blanc-*` (parties factices, INSTALLATION.md point 6). Rend les noms supprimés."""
    supprimes = []
    d = Path(dossier_simulations)
    if d.is_dir():
        for p in sorted(d.glob("essai-blanc-*")):
            if p.is_dir() and not p.is_symlink():
                shutil.rmtree(p)
                supprimes.append(p.name)
    return supprimes


def _fichiers(dossier: Path) -> set:
    return {p for p in Path(dossier).rglob("*") if p.is_file()} if Path(dossier).is_dir() else set()


VAR_FICHIER_PID = "PILOTE_FICHIER_PID"


def executer_enfant(cmd: list, env: dict, cwd: Path, journal_enfant: Path, cle=None, delai: int = DELAI_PARTIE_S) -> int:
    """Lance l'enfant, écrit sa sortie (clé purgée) dans `journal_enfant`. Rend le code de retour (-1 : délai dépassé).
    Si `env` porte VAR_FICHIER_PID (lanceur), le PID de l'enfant est noté dans ce fichier tant qu'il tourne, puis
    effacé ; la variable n'est pas transmise à l'enfant. Un lanceur tué laisse le fichier : la reprise refuse tant que
    l'enfant vit encore, car il dépense toujours (revue « ultra » du 06/11, constat 3)."""
    fichier_pid = env.get(VAR_FICHIER_PID)
    env = {k: v for k, v in env.items() if k != VAR_FICHIER_PID}
    with subprocess.Popen(cmd, env=env, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                          stdin=subprocess.DEVNULL) as p:
        try:
            if fichier_pid:
                Path(fichier_pid).parent.mkdir(parents=True, exist_ok=True)
                ecrire_json_atomique(Path(fichier_pid), {"pid": p.pid, "machine": socket.gethostname(),
                                                         "debut": datetime.now().isoformat(timespec="seconds"),
                                                         "commande": [str(c) for c in cmd[:2]]})
            try:
                out, err = p.communicate(timeout=delai)
                sortie, code = (out or "") + "\n--- stderr ---\n" + (err or ""), p.returncode
            except subprocess.TimeoutExpired:
                p.kill()
                p.communicate()
                sortie, code = "délai dépassé", -1
        except BaseException:  # comme subprocess.run : l'enfant ne survit pas à une erreur du parent
            p.kill()
            raise
        finally:
            if fichier_pid:
                Path(fichier_pid).unlink(missing_ok=True)
    if cle:
        sortie = sortie.replace(cle, "***")
    journal_enfant.write_text(sortie, encoding="utf-8")
    return code


def executer_partie(partie: dict, ctx: dict) -> dict:
    """Lance une partie et rend {ok, appels (usage), copies, erreur}. Ne lève pas : l'échec est une donnée."""
    sortie: Path = ctx["sortie"]
    reel = ctx["reel"]
    env = ctx["env_enfant"]
    pid = partie["id"]
    log = sortie / "logs" / f"{pid}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    res = {"ok": False, "appels": None, "erreur": None, "copies": []}
    if partie["env"] != "WorkBench":
        nom = f"{'pilote' if reel else 'essai-blanc'}-etape1-{ctx['horodatage']}-{pid}"
        code = executer_enfant(commande_tau2(partie, nom, reel), env, TAU2, log, ctx.get("cle"))
        source = TAU2 / "data" / "simulations" / nom / "results.json"
        if code != 0:
            res["erreur"] = f"tau2 : code de retour {code}"
        if source.is_file():
            cible = sortie / "parties" / f"tau2-{pid}" / "results.json"
            cible.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, cible)
            res["copies"].append(str(cible))
            try:
                res["appels"] = appels_tau2(cible, estimer=not reel)
            except ValueError as e:
                res["erreur"] = (res["erreur"] + " ; " if res["erreur"] else "") + f"usage illisible : {e}"
        else:
            res["erreur"] = (res["erreur"] + " ; " if res["erreur"] else "") + "results.json absent"
        res["ok"] = res["erreur"] is None
        return res
    # WorkBench : parties sérialisées (les fichiers de sortie sont nommés à la seconde près, dans un dossier commun)
    with ctx["verrou_wb"]:
        csv_taches = ecrire_taches_workbench(partie, sortie / "taches" / pid)
        usage = sortie / "usage" / f"{pid}.jsonl"
        usage.parent.mkdir(parents=True, exist_ok=True)
        e = dict(env)
        e["PILOTE_USAGE_FILE"] = str(usage)
        avant = _fichiers(WB_RUN / "data" / "results")
        code = executer_enfant(commande_workbench(csv_taches), e, WB_RUN, log, ctx.get("cle"))
        nouveaux = sorted(_fichiers(WB_RUN / "data" / "results") - avant)
        cible = sortie / "parties" / f"workbench-{pid}"
        cible.mkdir(parents=True, exist_ok=True)
        for p in nouveaux:
            shutil.move(str(p), str(cible / p.name))
            res["copies"].append(str(cible / p.name))
    if code != 0:
        res["erreur"] = f"WorkBench : code de retour {code}"
    if not any(c.endswith(".csv") for c in res["copies"]):
        res["erreur"] = (res["erreur"] + " ; " if res["erreur"] else "") + "csv de prédictions absent"
    try:
        res["appels"] = appels_workbench(usage)
    except ValueError as ex:
        res["erreur"] = (res["erreur"] + " ; " if res["erreur"] else "") + f"usage illisible : {ex}"
    res["ok"] = res["erreur"] is None
    return res


def ecrire_json_atomique(chemin: Path, obj) -> None:
    tmp = chemin.with_suffix(chemin.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, chemin)


def lancer_parties(parties: list, concurrence: int, compta: Comptable, ctx: dict, journal: Journal, executeur=executer_partie) -> list:
    """Exécute les parties (1 ou 2 à la fois). Avant CHAQUE nouvelle partie : arrêt si le coût cumulé a atteint 80 %
    du plafond. Après chaque partie : usage lu, coût ajouté, cout.json réécrit. Usage illisible ou échec : arrêt."""
    file_attente = list(parties)
    verrou = threading.Lock()
    resultats = []
    cout_json = ctx["sortie"] / "cout.json"

    def ecrire_cout():
        ecrire_json_atomique(cout_json, {
            "mode": "réel" if ctx["reel"] else "à blanc",
            "modele": MODELE_TAU,
            "prix_usd_par_million": {"entree": PRIX_ENTREE_M, "sortie": PRIX_SORTIE_M},
            "regle_double": f"appel de plus de {SEUIL_DOUBLE} jetons d'entrée compté au double",
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
            journal.ecrire(f"début {partie['id']} ({partie['tache']})")
            try:
                r = executeur(partie, ctx)
            except Exception as e:  # échec inattendu = arrêt, jamais de reprise silencieuse
                r = {"ok": False, "appels": None, "erreur": f"exception {type(e).__name__}", "copies": []}
            ligne = {"id": partie["id"], "env": partie["env"], "tache": partie["tache"], "ok": r["ok"], "erreur": r["erreur"]}
            if r.get("appels"):
                b = bilan_appels(r["appels"])
                ligne.update(b)
                compta.ajouter(b["cout_usd"])
                if b["appels_doubles"]:
                    journal.ecrire(f"ATTENTION {partie['id']} : {b['appels_doubles']} appel(s) de plus de {SEUIL_DOUBLE} jetons d'entrée, comptés au double")
            else:
                ligne.update({"appels": 0, "jetons_entree": None, "jetons_sortie": None, "cout_usd": None})
            if not r["ok"]:
                compta.arreter(f"partie {partie['id']} : {r['erreur']}")
            with verrou:
                resultats.append(ligne)
                ecrire_cout()
            journal.ecrire(f"fin {partie['id']} ok={r['ok']} cumul={compta.cumul:.6f} USD"
                           + (f" erreur={r['erreur']}" if r["erreur"] else ""))

    with ThreadPoolExecutor(max_workers=concurrence) as ex:
        for f in [ex.submit(travailleur) for _ in range(concurrence)]:
            f.result()
    ecrire_cout()
    if compta.arret:
        journal.ecrire(f"ARRÊT : {compta.arret} ; parties non lancées : {len(file_attente)}")
    return resultats


# --- après les parties ---------------------------------------------------------------------------------------
CHAMPS_TYPAGE = ["type", "enjeu", "plafonnee", "montant", "raison", "etiquettes"]


def typer_csv(entree: Path, sortie: Path, workbench=WORKBENCH) -> list:
    """Ajoute à chaque action les colonnes du typage (banc/typage.py). L'historique donné à typer() = actions
    précédentes de la même partie. Une erreur de typage rend « effet illisible » (enjeu fort), jamais une ligne perdue."""
    import typage
    with open(entree, newline="", encoding="utf-8") as fh:
        lecteur = csv.DictReader(fh)
        lignes = list(lecteur)
        champs = list(lecteur.fieldnames or [])
    ctx = typage.charger_contexte_workbench(workbench) if any(l["banc"] == "workbench" for l in lignes) else None
    vus: dict = {}
    for l in lignes:
        hist = vus.setdefault(l["partie"], [])
        try:
            t = typage.typer(l, ctx, list(hist))
        except Exception as e:
            t = {"type": typage.ILLISIBLE, "enjeu": typage.ENJEUX[typage.ILLISIBLE], "plafonnee": True, "montant": None,
                 "raison": f"erreur de typage : {type(e).__name__}", "etiquettes": []}
        l.update({"type": t["type"], "enjeu": t["enjeu"], "plafonnee": t["plafonnee"],
                  "montant": "" if t["montant"] is None else t["montant"], "raison": t["raison"],
                  "etiquettes": ";".join(t["etiquettes"])})
        hist.append(dict(l))
    with open(sortie, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=champs + CHAMPS_TYPAGE)
        w.writeheader()
        w.writerows(lignes)
    return lignes


def env_de_ligne(l: dict) -> str:
    return "WorkBench" if l["banc"] == "workbench" else ENV_DE_DOMAINE.get(l["domaine"], l["domaine"])


def resume_par_env(lignes: list, parties: list) -> dict:
    """Par environnement : parties, actions, lectures, écritures par verdict et par type, jetons et coût."""
    r = {}
    for e in ENVS:
        ps = [p for p in parties if p["env"] == e]
        ls = [l for l in lignes if env_de_ligne(l) == e]
        ecr = [l for l in ls if l["kind"] == "écriture"]
        r[e] = {
            "parties_lancees": len(ps),
            "parties_ok": sum(1 for p in ps if p["ok"]),
            "actions": len(ls),
            "lectures": sum(1 for l in ls if l["kind"] == "lecture"),
            "ecritures": len(ecr),
            "autres_actions": len(ls) - len(ecr) - sum(1 for l in ls if l["kind"] == "lecture"),
            "ecritures_par_verdict": dict(sorted(_compter(l["verdict"] or "sans verdict" for l in ecr).items())),
            "ecritures_par_type": dict(sorted(_compter(l["type"] for l in ecr).items())),
            "jetons_entree": sum(p.get("jetons_entree") or 0 for p in ps),
            "jetons_sortie": sum(p.get("jetons_sortie") or 0 for p in ps),
            "cout_usd": round(sum(p.get("cout_usd") or 0 for p in ps), 8),
        }
    return r


def _compter(it) -> dict:
    d: dict = {}
    for x in it:
        d[x] = d.get(x, 0) + 1
    return d


def resume_texte(resume: dict, compta: Comptable, mode: str, factice: bool) -> str:
    out = [f"Pilote étape 1, mode {mode}" + (" (liste de tâches FACTICE)" if factice else ""),
           f"Coût cumulé : {compta.cumul:.6f} USD sur un plafond de {compta.plafond:.2f} USD"
           + (f" ; ARRÊT : {compta.arret}" if compta.arret else ""), ""]
    for e, v in resume.items():
        out += [f"## {e}",
                f"parties lancées {v['parties_lancees']} (ok {v['parties_ok']}) ; actions {v['actions']} ; lectures {v['lectures']} ; "
                f"écritures {v['ecritures']} ; autres {v['autres_actions']}",
                f"écritures par verdict : {v['ecritures_par_verdict']}", f"écritures par type : {v['ecritures_par_type']}",
                f"jetons : {v['jetons_entree']} en entrée, {v['jetons_sortie']} en sortie ; coût {v['cout_usd']:.6f} USD", ""]
    return "\n".join(out)


def post_traitement(sortie: Path, resultats: list, compta: Comptable, mode: str, factice: bool,
                    tau2=TAU2, workbench=WORKBENCH) -> dict:
    import verdicts_csv
    actions = sortie / "actions.csv"
    rc = verdicts_csv.main(["--dossier", str(sortie / "parties"), "--tau2", str(tau2), "--workbench", str(workbench),
                            "--sortie", str(actions)])
    if rc != 0:
        raise ErreurPilote("verdicts_csv.py a échoué")
    lignes = typer_csv(actions, sortie / "actions_typees.csv", workbench)
    resume = resume_par_env(lignes, resultats)
    ecrire_json_atomique(sortie / "resume.json", {"mode": mode, "liste_taches_factice": factice,
                                                   "cumul_usd": round(compta.cumul, 8), "arret": compta.arret, "environnements": resume})
    (sortie / "resume.txt").write_text(resume_texte(resume, compta, mode, factice), encoding="utf-8")
    return resume


# --- principal ---------------------------------------------------------------------------------------------
def analyser(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--reel", action="store_true", help="appels réels (exige --plafond-usd)")
    p.add_argument("--plafond-usd", type=float, default=None, help=f"plafond de dépense en USD, au plus {PLAFOND_MAX:.2f}")
    p.add_argument("--concurrence", type=int, choices=(1, 2), default=1)
    p.add_argument("--developpement", default=str(DEVELOPPEMENT), help="liste des tâches de développement (JSON)")
    p.add_argument("--sortie-racine", default=str(SORTIE_RACINE))
    return p.parse_args(argv)


def verifier_plafond(a) -> float:
    if a.reel and a.plafond_usd is None:
        raise ErreurPilote("mode réel : --plafond-usd obligatoire")
    plafond = a.plafond_usd if a.plafond_usd is not None else PLAFOND_MAX
    if not math.isfinite(plafond) or plafond <= 0:
        raise ErreurPilote("plafond invalide : un nombre positif est attendu")
    if plafond > PLAFOND_MAX:
        raise ErreurPilote(f"plafond {plafond} USD refusé : au plus {PLAFOND_MAX:.2f} USD")
    return plafond


def main(argv=None, executeur=executer_partie, base_env=None, chemin_cle=None) -> int:
    a = analyser(argv)
    try:
        plafond = verifier_plafond(a)
        reel = a.reel
        taches, factice = charger_taches(a.developpement, reel)
        cle = lire_cle(chemin_cle or CHEMIN_CLE) if reel else None
        env = env_enfant(os.environ if base_env is None else base_env, cle)
        verifier_env_enfant(env, reel)
        verifier_pas_de_dotenv(TAU2, WB_RUN)
        if not factice:
            verifier_taches_existent(taches)
    except ErreurPilote as e:
        print(f"REFUS : {e}", file=sys.stderr)
        return 2
    mode = "réel" if reel else "à blanc"
    horodatage = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    sortie = Path(a.sortie_racine) / (horodatage if reel else horodatage + "-blanc")
    sortie.mkdir(parents=True, exist_ok=False)
    journal = Journal(sortie / "journal.log", cle)
    journal.ecrire(f"pilote étape 1, mode {mode}, plafond {plafond:.2f} USD, concurrence {a.concurrence}, "
                   f"tâches {'FACTICES' if factice else a.developpement}")
    journal.ecrire("tâches : " + json.dumps(taches, ensure_ascii=False))
    if reel:
        sup = nettoyer_parties_factices(TAU2 / "data" / "simulations")
        journal.ecrire(f"parties factices supprimées : {sup}")
    compta = Comptable(plafond)
    ctx = {"sortie": sortie, "reel": reel, "env_enfant": env, "cle": cle, "horodatage": horodatage,
           "verrou_wb": threading.Lock()}
    resultats = lancer_parties(construire_parties(taches), a.concurrence, compta, ctx, journal, executeur)
    try:
        resume = post_traitement(sortie, resultats, compta, mode, factice)
    except (ErreurPilote, ValueError, OSError) as e:
        journal.ecrire(f"post-traitement échoué : {type(e).__name__} {e}")
        return 3
    journal.ecrire(f"terminé : {len(resultats)} parties, cumul {compta.cumul:.6f} USD -> {sortie}")
    print((sortie / "resume.txt").read_text(encoding="utf-8"))
    return 4 if compta.arret else 0


if __name__ == "__main__":
    sys.exit(main())
