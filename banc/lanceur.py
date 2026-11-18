"""Lanceur de l'expérience « autonomie méritée » : toute la réserve, en deux vagues.

Sources : PLAN_EXPERIENCE.md, 2.2 (modèles, 100 tours, 30 minutes, cache, nom de modèle renvoyé), 2.3 (passages par
configuration, 14 266 parties, coût estimé), 2.5 (vagues, ordre de jeu, plafonds, réduction des passages, vérifications
entre deux vagues), 4.7 points 2 et 5, 5.5 point 1 ; décision d'Otsoa du 05/11 sur Q10. Choix et imprécisions
tranchées : banc/CHOIX_LANCEUR.md.

MODE PAR DÉFAUT : ESSAI À BLANC. Aucune clé n'est lue, aucun appel réseau n'est fait : les bancs tournent sur leurs
réponses factices (τ-bench `mock_response`, WorkBench `PILOTE_HORS_LIGNE=2`), proxys cassés, comme au pilote
(banc/pilote_etape2.py), dont ce lanceur reprend l'exécution, les garde-fous et le format de sortie.

    cd "$RACINE"   # racine du dépôt : RACINE=$(git rev-parse --show-toplevel)
    # aperçu : parties, estimation, plafond permis ; rien n'est lancé ni écrit
    env -u ANTHROPIC_API_KEY simulation/.venv/bin/python banc/lanceur.py --vague 1 --apercu
    # essai à blanc de la vague 1 (toute la vague ; --limite N n'en joue que les N premières parties)
    env -u ANTHROPIC_API_KEY simulation/.venv/bin/python banc/lanceur.py --vague 1 --plafond-usd 90 --accord-otsoa-usd 90
    # vague 1 réelle, après le second accord d'Otsoa
    simulation/.venv/bin/python banc/lanceur.py --vague 1 --reel --plafond-usd X --accord-otsoa-usd Y
    # vague 2 : estimation refaite sur les coûts mesurés à la vague 1 (à blanc : sur les coûts du pilote, ceux d'une
    # vague 1 à blanc étant factices), passages réduits si 1,25 fois l'estimation dépasse le budget restant (règle C9)
    simulation/.venv/bin/python banc/lanceur.py --vague 2 --vague1 experience/vague1/<horodatage> \
        --budget-restant-usd B --plafond-usd X --accord-otsoa-usd Y [--reel]
    # reprise d'une vague interrompue : même dossier, le coût déjà dépensé compte dans le plafond ; chaque coût inconnu
    # (arrêt « coût non compté ») doit d'abord être chiffré dans la console et donné par --cout-retenu
    simulation/.venv/bin/python banc/lanceur.py --vague N --reprendre experience/vagueN/<horodatage> \
        --plafond-usd X --accord-otsoa-usd Y [--vague1 ...] [--cout-retenu ID=USD ...] [--reel]

Garde-fous :
- plafond (--plafond-usd) et montant accordé par Otsoa pour la vague (--accord-otsoa-usd) obligatoires ; plafond refusé
  au-delà de ce montant, de 1,5 fois l'estimation de la vague 1, ou, à la vague 2, de 1,25 fois l'estimation refaite et
  du budget restant (--budget-restant-usd, donné par l'opérateur : aucun montant dépensé n'est écrit dans le code) ;
  arrêt avant toute nouvelle partie à 80 % du plafond à la vague 1 (FRACTION_ARRET du pilote), et à la vague 2 au plus
  petit de 95 % du plafond et du plafond moins 15 $ (Otsoa, QCM, 06/11) ; la réduction des passages (C9) fait tenir
  1,25 fois le total réduit dans le budget restant. Aucune limite dans la console (Q10) : ce plafond est le seul mur ;
- un seul lancement par vague : en réel, les sorties vont dans experience/ (--sortie-racine refusé), et un nouveau
  lancement est refusé si la vague a déjà un dossier réel (la poursuivre avec --reprendre), contrôle refait sous un
  flock de experience/vague<N>/ au moment de créer le dossier ; verrou exclusif dans le dossier de vague (fichier
  `verrou`, PID) : un second lanceur sur le même dossier est refusé, un verrou orphelin (processus mort) est signalé et
  repris ; la vague 2 tient le verrou de la vague 1 pendant sa mise en route, puis la ferme (`vague2.json` dans son
  dossier : elle ne se reprend plus) ; elle refuse une vague 1 qui a une tentative commencée sans fin ;
- parties WorkBench une à la fois entre tous les lanceurs, réels et à blanc (flock de
  externe/workbench-run/data/results.verrou) ; une partie WorkBench qui attendait son tour quand l'arrêt est décidé
  n'est pas lancée et reste en file ;
- coût d'une tentative majoré (usage incomplet ; WorkBench : depuis ses traces, sortie bornée par le maximum du modèle)
  ou inconnu (usage absent ou illisible alors que des appels sont sûrs, sans majorant) : arrêt ; la reprise exige un
  montant retenu pour chaque coût inconnu (--cout-retenu), et la vague 2 une vague 1 sans coût inconnu ;
- clé lue seulement en réel (~/.config/autonomie-meritee/anthropic.env, 600), jamais affichée ; environnement des
  enfants nettoyé de toute autre clé ; aucun `.env` dans les bancs (garde-fous du pilote), et aucun chargé au-dessus
  d'eux (PYTHON_DOTENV_DISABLED=1) ;
- définitions d'outils réextraites avant de jouer (banc/outils_agent.py) : une empreinte différente de
  banc/outils_agent/ arrête tout ;
- nom de modèle renvoyé par l'API noté pour chaque appel, comparé à la référence de son banc (τ-bench et WorkBench
  passent par deux points d'accès) ; s'il change, arrêt, et la partie est exclue (2.5, point 6),
  puis rejouée une fois à la reprise sous un nouveau numéro de tentative (les deux tentatives sont déclarées) ;
- une partie en échec technique (panne : erreur d'API, processus ou fichiers en défaut) est relancée une fois, puis
  exclue et déclarée ; τ-bench ne se relance plus lui-même (--max-retries 0) ; une partie arrêtée par les 100 tours ou
  les 30 minutes est « arrêtée » et gardée (5.5, point 1) ; une partie arrêtée sans trace exploitable (fenêtre de
  contexte, exception d'outil WorkBench, filet de 35 minutes) est exclue, déclarée, jamais relancée ;
- le rapport de vague ne couvre que les points 1, 2, 3 et 6 de 2.5 : aucun décompte d'erreurs, de verdicts ni
  d'alertes (« on ne regarde rien d'autre ») ; les exceptions d'outil WorkBench (le plus souvent des erreurs de
  l'agent) n'y sont comptées que par environnement ; le journal visible (journal.log, console) ne nomme ni la partie
  ni le modèle d'une tentative WorkBench, le détail va dans journal_complet.log, à ne pas lire avant le rejeu final.

Sorties : experience/vague<N>/<horodatage>[-blanc]/, hors du périmètre du gel (gel/manifeste.py), au format du pilote lu
par simulation/rejeu/entrees.py (cout.json, parties/, actions.csv, actions_typees.csv, logs/, usage/, taches/), plus
plan_de_jeu.json, ordre_de_jeu.csv, tentatives.jsonl, modeles_renvoyes.json, outils_agent.json, ecartees/ (fichiers des
tentatives non gardées), rapport_vague.json, rapport_vague.txt, journal_complet.log, et `verrou` pendant le jeu (retiré
à la fin). Seules les parties gardées sont dans parties/.

Codes de sortie : 0 vague jouée ; 2 refus avant tout lancement (dont : vague déjà lancée, autre racine en réel,
dossier verrouillé, coût inconnu non chiffré, vague 1 avec une tentative sans fin) ; 3 post-traitement échoué ; 4 vague arrêtée avant la fin (seuil d'arrêt, nom de modèle changé,
coût majoré ou non compté, échecs techniques ou exceptions d'outil en série, interruption) : voir journal.log.
"""
from __future__ import annotations

import argparse
import csv
import fcntl
import hashlib
import json
import math
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from fractions import Fraction
from pathlib import Path

BANC = Path(__file__).resolve().parent
if str(BANC) not in sys.path:
    sys.path.insert(0, str(BANC))

import cout_v2 as cv  # noqa: E402
import outils_agent as oa  # noqa: E402
import pilote_etape1 as pe  # noqa: E402
import pilote_etape2 as p2  # noqa: E402
from pilote_etape1 import ErreurPilote  # noqa: E402

RACINE = pe.RACINE
TAU2 = pe.TAU2
WORKBENCH = pe.WORKBENCH
WB_RUN = pe.WB_RUN
CHEMIN_CLE = pe.CHEMIN_CLE
ENVS = pe.ENVS
MODELES = p2.MODELES
COURT = p2.COURT
MODELE_USER = p2.MODELE_USER
RESERVE = BANC / "tirage" / "reserve.json"
DOSSIER_OUTILS = oa.DOSSIER
TABLE_OUTILS = BANC / "table_outils.json"
SORTIE_RACINE = RACINE / "experience"  # hors du périmètre du gel (gel/manifeste.py)
FICHIER_OUTILS = {"aviation": "aviation", "commerce": "commerce", "banque": "banque", "WorkBench": "workbench"}
verifier_taches_existent = p2.verifier_taches_existent  # remplaçable dans les tests

# 2.3 (Décidé, SUIVI.md, « Dimensionnement de l'expérience », point 1) : passages des tâches réservées.
PASSAGES = {
    "claude-haiku-5-5": {"aviation": 50, "commerce": 50, "banque": 10, "WorkBench": 5},
    "claude-sonnet-5-5": {"aviation": 10, "commerce": 10, "banque": 3, "WorkBench": 1},
    "claude-opus-5-5": {"aviation": 10, "commerce": 10, "banque": 3, "WorkBench": 1},
}
# 2.3 et annexe A3 : coût moyen par partie au pilote, agent et client simulé compris = somme des `cout_usd` des
# 10 parties de la case dans pilote/etape2/2026-11-05_07-50-58/cout.json, divisée par 10 (recoupé par les tests ;
# total de 2.3 : 595,73 $).
COUT_PILOTE = {
    "claude-haiku-5-5": {"aviation": 0.04885504 / 10, "commerce": 0.03904043 / 10, "banque": 0.15469865 / 10,
                         "WorkBench": 0.0472029 / 10},
    "claude-sonnet-5-5": {"aviation": 0.72600731 / 10, "commerce": 0.53349661 / 10, "banque": 3.54033096 / 10,
                          "WorkBench": 0.858226 / 10},
    "claude-opus-5-5": {"aviation": 1.28926671 / 10, "commerce": 0.86694902 / 10, "banque": 4.71071248 / 10,
                        "WorkBench": 1.761476 / 10},
}
SOURCE_COUT_PILOTE = "pilote/etape2/2026-11-05_07-50-58/cout.json (moyenne des 10 parties de chaque case, 2.3)"
# Vague 2 à blanc (coordinateur, 06/11) : les coûts d'une vague 1 à blanc sont factices (réponses simulées) ; l'estimation
# reprend ceux du pilote, pour un plafond et un seuil réalistes. En réel, rien ne change : coûts mesurés à la vague 1.
SOURCE_COUTS_BLANC = "coûts du pilote, essai à blanc"

PART_VAGUE1 = Fraction(1, 10)  # 2.5 : les premiers 10 % des parties de chaque configuration, arrondi au supérieur
FACTEUR_PLAFOND = {1: 1.5, 2: 1.25}  # Q10 (Décidé, Otsoa, 05/11)
FRACTION_ARRET = pe.FRACTION_ARRET  # vague 1 : arrêt avant toute nouvelle partie à 80 % du plafond (2.5)
# Vague 2 (Décidé, Otsoa, QCM, 06/11) : arrêt au plus petit de 95 % du plafond et du plafond moins 15 $ (réserve pour les
# parties en cours) ; la réduction C9 fait tenir le plafond entier (1,25 x le total réduit) dans le budget restant.
FRACTION_ARRET_VAGUE2 = 0.95
RESERVE_EN_COURS_USD = 15.0
CONCURRENCE_DEFAUT = 2
CONCURRENCE_MAX = 3  # comme au pilote
TENTATIVES_MAX = 2  # échec technique : relancée une fois, puis exclue (Q10, tranché par Claude)
EXCLUSIONS_NOM_MAX = 2  # nom de modèle changé : rejouée une fois à la reprise (tranché par Claude, 06/11)
MOTIF_NOM_REJOUEE = "nom de modèle renvoyé changé (2.5, point 6) : rejouée une fois à la reprise"
MOTIF_NOM_DEUX_FOIS = "nom de modèle renvoyé changé, et encore au rejeu (2.5, point 6)"
SERIE_ECHECS_MAX = 3  # échecs techniques consécutifs : panne probable, arrêt (CHOIX_LANCEUR.md)
SERIE_EXCEPTIONS_OUTIL_MAX = 3  # exceptions d'outil WorkBench consécutives : erreur de configuration probable, arrêt
DELAI_PARTIE_S = pe.DELAI_PARTIE_S  # 30 minutes (2.2)
MARGE_DELAI_S = 300  # τ-bench s'arrête lui-même à 30 minutes (--timeout) ; filet : processus tué 5 minutes plus tard
SEUIL_COUVERTURE = 0.95  # 2.5, point 3 ; 5.8 ; 5.14, point 0
PERIODE_COUT_S = 30.0  # cout.json réécrit au plus toutes les 30 s et à la fin ; tentatives.jsonl après chaque tentative
EPS = 1e-9

TERMINEE = "terminée"
ARRETEE = "arrêtée"
ECHEC = "échec technique"
EXCLUE_NOM = "exclue : nom de modèle changé"
INTERROMPUE = "interrompue"
COUT_RETENU = "coût retenu"  # ligne sans partie jouée : montant retenu par l'opérateur pour un coût inconnu (--cout-retenu)
STATUTS = (TERMINEE, ARRETEE, ECHEC, EXCLUE_NOM, INTERROMPUE, COUT_RETENU)
ARRET_30_MIN = "30 minutes"
ARRET_CONTEXTE = "fenêtre de contexte"
ARRET_WORKBENCH = "limite du banc WorkBench (20 itérations ou 10 minutes)"
ARRET_EXCEPTION_OUTIL = "exception d'outil"
MOTIF_SANS_TRACE = "arrêtée sans trace exploitable"
MOTIF_EXCEPTION_OUTIL = "exception d'outil : WorkBench a perdu les actions de la partie"
# τ-bench classe ces deux terminaisons comme des essais en erreur (src/tau2/metrics/benchmark.py, TrialStatus.ERROR).
TERMINAISONS_ECHEC = frozenset({"infrastructure_error", "unexpected_error"})
# τ-bench (033bf08) n'attribue jamais « context_window_exceeded » : un dépassement lève ContextWindowExceededError
# (LiteLLM), et la simulation finit vide en « infrastructure_error » avec ce type d'erreur (runner/progress.py).
TYPE_ERREUR_CONTEXTE = "ContextWindowExceededError"
# WorkBench, commit 49c7dfd : src/evals/agent.py (AGENT_STOPPED_MESSAGE) et src/evals/inference.py (fenêtre de contexte).
WB_MESSAGE_ARRET = "Agent stopped due to iteration limit or time limit."
WB_MESSAGE_CONTEXTE = "Context window exceeded"
# Erreurs d'API de WorkBench, seules tenues pour des échecs techniques (revue du 06/11, constat 5) : textes des
# exceptions du SDK OpenAI 1.x (APIStatusError, APIConnectionError, APITimeoutError, et APIResponseValidationError :
# message par défaut de openai/_exceptions.py, contre-vérification, constat I) et de l'enveloppe de délai de WorkBench
# (src/evals/agent.py, _create_with_deadline). Toute autre exception est une exception d'outil, y compris « list index
# out of range » : texte générique de Python, qu'une réponse sans choix (agent.py:233, 252) donne mais qu'un outil
# pourrait donner aussi (limite déclarée, CHOIX_LANCEUR.md, choix 28).
WB_ERREURS_API = ("Error code:", "Connection error.", "Request timed out.", "LLM call exceeded",
                  "Data returned by API invalid for expected schema.")
# Majorant d'une partie WorkBench sans usage (CHOIX_LANCEUR.md, choix 27) : jetons d'invite bornés par les octets des
# textes de ses traces, plus une marge pour la mise en forme des messages et des outils par l'API ; jetons de sortie
# bornés, à chaque étape, par le maximum de sortie du modèle, raisonnement compris (contre-vérification, constat G).
MARGE_FORMAT_JETONS = 2000
# Maximum de jetons de sortie par appel, raisonnement compris : « Max Output 128K » pour les trois modèles 5.5
# (documentation de l'API, compétence claude-api, shared/models.md, cache du 2026-10-06 ; champ `max_tokens` de
# GET /v1/models/{id}, à relever avant le gel). WorkBench n'envoie pas de max_tokens (src/evals/agent.py,
# _call_llm_structured) : le plafond du modèle est la seule borne.
MAX_SORTIE_JETONS = {"claude-haiku-5-5": 128_000, "claude-sonnet-5-5": 128_000, "claude-opus-5-5": 128_000}
# Code de retour d'un banc coupé par Ctrl-C (Python se termine par le signal SIGINT : -2 ; 130 pour un shell).
CODES_INTERRUPTION = frozenset({-2, 130})
NOM_VERROU = "verrou"  # verrou exclusif du dossier de vague (O_EXCL, PID)
NOM_MARQUEUR_VAGUE2 = "vague2.json"  # posé dans le dossier de la vague 1 quand la vague 2 commence
DOSSIER_ENFANTS = "enfants"  # PID de chaque enfant pendant qu'il tourne (revue « ultra » du 06/11, constat 3)
# Verrou commun à tous les lanceurs (réels et à blanc), tenu pendant toute partie WorkBench : WorkBench écrit dans un
# dossier commun, externe/workbench-run/data/results/ (contre-vérification, constat C). Fichier à côté de ce dossier.
NOM_VERROU_WB = "results.verrou"
# Journal complet (parties WorkBench nommées) : jamais affiché ; le journal visible ne les nomme pas (constat E).
NOM_JOURNAL_COMPLET = "journal_complet.log"
ENTETE_JOURNAL_COMPLET = "à ne pas lire avant le rejeu final (2.5, on ne regarde rien d'autre)"
CHAMPS_TENTATIVE = ("id", "partie", "tentative", "env", "modele", "tache", "passage", "rang", "vague")
CHAMPS_ORDRE = ["ordre", "id", "env", "modele", "tache", "passage", "rang", "n_config"]


def maintenant() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _joindre(a, b):
    return b if not a else (a if not b else f"{a} ; {b}")


def empreinte_json(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def empreinte_ordre(parties: list) -> str:
    return hashlib.sha256("\n".join(x["id"] for x in parties).encode("utf-8")).hexdigest()


def banc_de(env: str) -> str:
    return "workbench" if env == "WorkBench" else "tau2"


def court(modele) -> str:
    m = modele if isinstance(modele, str) else ""
    return m[len("anthropic/"):] if m.startswith("anthropic/") else m


# =================================================================================================================
# 1-3. La réserve, les parties, l'ordre de jeu et les vagues
# =================================================================================================================
def charger_reserve(chemin=RESERVE) -> dict:
    """{environnement: [identifiants]} de banc/tirage/reserve.json : les quatre environnements, sans doublon."""
    chemin = Path(chemin)
    try:
        data = json.loads(chemin.read_text(encoding="utf-8"))
    except OSError:
        raise ErreurPilote(f"réserve introuvable : {chemin}")
    except ValueError:
        raise ErreurPilote(f"réserve illisible : {chemin}")
    if not isinstance(data, dict) or set(data) != set(ENVS):
        raise ErreurPilote(f"réserve : les environnements {', '.join(ENVS)} sont attendus, et eux seuls")
    sortie = {}
    for e in ENVS:
        ids = data[e]
        if not isinstance(ids, list) or not ids or not all(isinstance(i, str) and i for i in ids):
            raise ErreurPilote(f"réserve : liste d'identifiants (chaînes) attendue pour {e}")
        if len(set(ids)) != len(ids):
            raise ErreurPilote(f"réserve : identifiant en double dans {e}")
        sortie[e] = list(ids)
    return sortie


def cle_ordre(graine: int, env: str, passage: int, tache: str) -> str:
    """Clé de tri : SHA-256 de « graine|environnement|passage|tâche ». Aucun générateur pseudo-aléatoire : l'ordre ne
    dépend ni de la version de Python ni du module random (random.sample peut changer d'une version à l'autre)."""
    return hashlib.sha256(f"{graine}|{env}|{passage}|{tache}".encode("utf-8")).hexdigest()


def ordre_des_taches(taches: list, graine: int, env: str, passage: int) -> list:
    """Les tâches d'un environnement dans l'ordre tiré pour un passage (le même pour les trois modèles)."""
    return sorted(taches, key=lambda t: (cle_ordre(graine, env, passage, t), t))


def id_partie(env: str, modele: str, passage: int, tache: str) -> str:
    return f"{env}-{COURT[modele]}-p{passage:02d}-{str(tache).replace(':', '_')}"


def parties_configuration(reserve: dict, modele: str, env: str, n_passages: int, graine: int) -> list:
    """Les parties d'une configuration, passage après passage : chaque passage joue toutes les tâches réservées de
    l'environnement, dans l'ordre tiré pour ce passage. `rang` est la place dans la configuration (1 à n_config)."""
    sortie = []
    for p in range(1, n_passages + 1):
        for t in ordre_des_taches(reserve[env], graine, env, p):
            sortie.append({"id": id_partie(env, modele, p, t), "env": env, "modele": modele, "tache": t, "passage": p})
    for r, x in enumerate(sortie, 1):
        x["rang"], x["n_config"] = r, len(sortie)
    return sortie


def construire_parties(reserve: dict, graine: int, passages=None, modeles=MODELES) -> list:
    """Toutes les parties du plan, intercalées par rang, environnement et modèle comme au pilote
    (pilote_etape2.construire_parties). Les configurations n'ayant pas la même taille, le rang est pris relatif à la
    configuration (rang / n_config, en fractions exactes) : à tout moment, chaque configuration a joué la même part de
    ses parties, et un arrêt laisse une couverture équilibrée (2.5). À tailles égales, c'est l'ordre du pilote."""
    passages = PASSAGES if passages is None else passages
    tout = []
    for m in modeles:
        for e in ENVS:
            n = passages.get(m, {}).get(e) or 0
            if n and e in reserve:
                tout += parties_configuration(reserve, m, e, n, graine)
    tout.sort(key=lambda x: (Fraction(x["rang"], x["n_config"]), ENVS.index(x["env"]), modeles.index(x["modele"])))
    ids = [x["id"] for x in tout]
    if len(set(ids)) != len(ids):
        raise ErreurPilote("plan de jeu : identifiant de partie en double")
    return tout


def n_vague1(n_config: int) -> int:
    return math.ceil(n_config * PART_VAGUE1)


def parties_vague1(parties: list) -> list:
    """Les premiers 10 % des parties de chaque configuration (arrondi au supérieur), dans l'ordre de jeu."""
    return [x for x in parties if x["rang"] <= n_vague1(x["n_config"])]


def compter(parties: list) -> dict:
    d: dict = {}
    for x in parties:
        k = (x["modele"], x["env"])
        d[k] = d.get(k, 0) + 1
    return d


# =================================================================================================================
# 4. L'estimation et les plafonds
# =================================================================================================================
def cout_moyen(couts: dict, modele: str, env: str) -> float:
    try:
        v = float(couts[modele][env])
    except (KeyError, TypeError, ValueError):
        raise ErreurPilote(f"coût moyen par partie inconnu pour {modele} / {env}")
    if not math.isfinite(v) or v < 0:
        raise ErreurPilote(f"coût moyen par partie invalide pour {modele} / {env}")
    return v


def detail_estimation(parties: list, couts: dict) -> list:
    n = compter(parties)
    return [{"modele": m, "env": e, "parties": n[(m, e)], "cout_moyen_usd": cout_moyen(couts, m, e),
             "estimation_usd": round(n[(m, e)] * cout_moyen(couts, m, e), 6)}
            for m in MODELES for e in ENVS if (m, e) in n]


def estimation(parties: list, couts: dict) -> float:
    return sum(d["parties"] * d["cout_moyen_usd"] for d in detail_estimation(parties, couts))


def plafond_permis(vague: int, estim: float, budget_restant=None) -> float:
    """Vague 1 : 1,5 x l'estimation. Vague 2 : 1,25 x l'estimation refaite, et jamais au-delà du budget restant."""
    p = FACTEUR_PLAFOND[vague] * estim
    if vague == 2 and budget_restant is not None:
        p = min(p, budget_restant)
    return p


def _cents_bas(x: float) -> float:
    return math.floor(x * 100 + EPS) / 100


def seuil_arret(vague: int, plafond: float) -> tuple:
    """(seuil, règle) : coût cumulé à partir duquel aucune nouvelle partie n'est lancée. Vague 1 : 80 % du plafond (2.5).
    Vague 2 : le plus petit de 95 % du plafond et du plafond moins 15 $ (décision d'Otsoa, QCM, 06/11) ; la réserve de
    15 $ l'emporte sous 300 $ de plafond."""
    if vague == 1:
        return plafond * FRACTION_ARRET, f"{int(FRACTION_ARRET * 100)} % du plafond"
    return (min(FRACTION_ARRET_VAGUE2 * plafond, plafond - RESERVE_EN_COURS_USD),
            f"le plus petit de {int(FRACTION_ARRET_VAGUE2 * 100)} % du plafond et du plafond moins "
            f"{RESERVE_EN_COURS_USD:.0f} USD")


class Comptable(pe.Comptable):
    """Le comptable du pilote (coût cumulé, jamais diminué ; sûr entre fils d'exécution), avec le seuil d'arrêt de la
    vague (seuil_arret) au lieu des 80 % fixes du pilote."""

    def __init__(self, plafond: float, vague: int):
        super().__init__(plafond)
        self.seuil, self.regle = seuil_arret(vague, plafond)

    def ajouter(self, cout: float) -> None:
        with self._verrou:
            self.cumul += cout
            if self.arret is None and self.cumul >= self.seuil - 1e-12:
                self.arret = (f"coût cumulé {self.cumul:.6f} USD >= seuil d'arrêt {self.seuil:.6f} USD "
                              f"({self.regle})")


def verifier_plafond(vague: int, plafond, accord, estim: float, budget_restant=None) -> float:
    """Contrôle du plafond demandé ; rend le plafond permis. ErreurPilote si refusé."""
    for nom, v in (("--plafond-usd", plafond), ("--accord-otsoa-usd", accord)):
        if v is None:
            raise ErreurPilote(f"{nom} est obligatoire")
        if not math.isfinite(v) or v <= 0:
            raise ErreurPilote(f"{nom} invalide : un nombre positif est attendu")
    if vague == 2:
        if budget_restant is None:
            raise ErreurPilote("vague 2 : --budget-restant-usd est obligatoire")
        if not math.isfinite(budget_restant) or budget_restant <= 0:
            raise ErreurPilote("--budget-restant-usd invalide : un nombre positif est attendu")
    if plafond > accord + EPS:
        raise ErreurPilote(f"plafond {plafond:.2f} USD refusé : supérieur au montant accordé par Otsoa pour la vague "
                           f"({accord:.2f} USD)")
    pmax = plafond_permis(vague, estim, budget_restant)
    if plafond > pmax + EPS:
        regle = ("1,5 fois l'estimation de la vague" if vague == 1 else
                 "1,25 fois l'estimation refaite sur la vague 1, dans la limite du budget restant")
        raise ErreurPilote(f"plafond {plafond:.2f} USD refusé : au plus {_cents_bas(pmax):.2f} USD à la vague {vague} "
                           f"({regle} ; estimation {estim:.2f} USD)")
    seuil, regle_arret = seuil_arret(vague, plafond)
    if seuil <= 0:
        raise ErreurPilote(f"plafond {plafond:.2f} USD refusé : seuil d'arrêt {seuil:.2f} USD ({regle_arret}), aucune "
                           f"partie ne pourrait être lancée")
    return pmax


# =================================================================================================================
# 5. La réduction des passages (2.5, règle C9)
# =================================================================================================================
def passages_reduits(passages: dict, centiemes: int) -> dict:
    """Chaque nombre de passages multiplié par centiemes/100, arrondi à l'inférieur, au moins 1 (calcul entier exact)."""
    if not isinstance(centiemes, int) or isinstance(centiemes, bool) or not 1 <= centiemes <= 100:
        raise ValueError(f"facteur en centièmes attendu entre 1 et 100 : {centiemes!r}")
    return {m: {e: max(1, (centiemes * int(n)) // 100) for e, n in d.items()} for m, d in passages.items()}


def parties_restantes(passages: dict, taches: dict, joues=None) -> dict:
    """{(modèle, env): parties du plan (passages donnés) qui restent à jouer}. joues : {(modèle, env): {passage: n}},
    parties déjà jouées ; seules comptent celles d'un passage encore dans le plan."""
    joues = joues or {}
    out = {}
    for m, d in passages.items():
        for e, n in d.items():
            deja = sum(k for p, k in joues.get((m, e), {}).items() if p <= n)
            out[(m, e)] = max(0, n * taches[e] - deja)
    return out


def facteur_reduction(passages: dict, couts: dict, taches: dict, joues: dict, budget: float,
                      marge: float = FACTEUR_PLAFOND[2]) -> tuple:
    """Règle C9 (2.5 ; Q10), avec la cible décidée par Otsoa (QCM, 06/11) : le plafond entier doit tenir dans le budget
    restant, c'est-à-dire marge (1,25) x total refait <= budget restant. Sinon, tous les nombres de passages sont
    multipliés par le même facteur, puis arrondis à l'inférieur, avec au moins un passage par tâche et par modèle ; le
    facteur est le plus grand, au centième, qui satisfait cette condition. Aucune tâche n'est retirée : chaque
    configuration garde au moins un passage complet. Fonction pure, sans aucun résultat de partie : seulement des coûts.

    Rend (centièmes, passages réduits, total refait des parties restantes). 100 : pas de réduction.
    ErreurPilote si même le plus petit facteur (un centième) ne tient pas."""
    for c in range(100, 0, -1):
        red = passages_reduits(passages, c)
        reste = parties_restantes(red, taches, joues)
        total = sum(k * cout_moyen(couts, m, e) for (m, e), k in reste.items() if k)
        if marge * total <= budget + EPS:
            return c, red, total
    raise ErreurPilote(f"réduction des passages impossible : même avec un passage partout, {marge} x le total refait "
                       f"dépasse le budget restant ({budget:.2f} USD)")


# =================================================================================================================
# 7. Les définitions d'outils (4.7, point 2)
# =================================================================================================================
def extraire_outils(dossier: Path, env: dict) -> None:
    """Relance banc/outils_agent.py dans l'environnement Python de chaque banc, sans clé ni réseau, vers `dossier`."""
    for banc, racine in (("tau2", TAU2), ("workbench", WORKBENCH)):
        cmd = [str(racine / ".venv" / "bin" / "python"), str(BANC / "outils_agent.py"), "--banc", banc,
               "--dossier", str(dossier)]
        try:
            r = subprocess.run(cmd, cwd=str(racine), env=env, capture_output=True, text=True, timeout=900,
                               stdin=subprocess.DEVNULL)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise ErreurPilote(f"extraction des définitions d'outils ({banc}) impossible : {type(e).__name__}")
        if r.returncode != 0:
            fin = " ".join((r.stderr or "").strip().splitlines()[-1:])[:300]
            raise ErreurPilote(f"extraction des définitions d'outils ({banc}) : code de retour {r.returncode} {fin}")


def comparer_outils(reference, nouveau) -> list:
    """Écarts entre les définitions figées (banc/outils_agent/) et une nouvelle extraction : empreinte, commit du banc,
    fichier manquant ou en plus. Liste vide : identiques."""
    reference, nouveau = Path(reference), Path(nouveau)
    refs = {p.name for p in reference.glob("*.json")}
    neufs = {p.name for p in nouveau.glob("*.json")}
    if not refs:
        return [f"aucune définition figée dans {reference}"]
    ecarts = []
    for nom in sorted(refs | neufs):
        if nom not in neufs:
            ecarts.append(f"{nom} : absent de la nouvelle extraction")
            continue
        if nom not in refs:
            ecarts.append(f"{nom} : absent des définitions figées")
            continue
        try:
            a = json.loads((reference / nom).read_text(encoding="utf-8"))
            b = json.loads((nouveau / nom).read_text(encoding="utf-8"))
            ha, hb = oa.empreinte(a["outils"]), oa.empreinte(b["outils"])
        except (OSError, ValueError, KeyError, TypeError):
            ecarts.append(f"{nom} : illisible")
            continue
        if ha != a.get("empreinte_sha256"):
            ecarts.append(f"{nom} : empreinte figée incohérente avec son contenu")
        if ha != hb:
            ecarts.append(f"{nom} : empreinte {hb[:16]} au lieu de {ha[:16]}")
        if a.get("commit") != b.get("commit"):
            ecarts.append(f"{nom} : commit du banc {b.get('commit')} au lieu de {a.get('commit')}")
    return ecarts


def verifier_outils_agent(env: dict, extracteur=None, reference=None) -> dict:
    """Relance l'extraction dans un dossier temporaire et compare à banc/outils_agent/. ErreurPilote au moindre écart.
    Rend {fichier: empreinte}."""
    reference = Path(reference or DOSSIER_OUTILS)
    with tempfile.TemporaryDirectory(prefix="outils-agent-") as d:
        (extracteur or extraire_outils)(Path(d), env)
        ecarts = comparer_outils(reference, d)
        if not ecarts:
            resume = {p.stem: json.loads(p.read_text(encoding="utf-8"))["empreinte_sha256"]
                      for p in sorted(Path(d).glob("*.json"))}
    if ecarts:
        raise ErreurPilote("définitions d'outils différentes de banc/outils_agent/ : " + " ; ".join(ecarts))
    return resume


# =================================================================================================================
# 6, 8. L'usage, le coût et l'exécution d'une tentative
# =================================================================================================================
def lire_usage(chemin) -> tuple:
    """(appels au format de cout_v2, [(modèle demandé, modèle renvoyé)] dans le même ordre), depuis le JSONL du callback
    tau2 (usage_tau2.py) ou de l'enveloppe WorkBench (usage_wrap.py). ValueError si absent, vide ou illisible."""
    try:
        lignes = [json.loads(x) for x in Path(chemin).read_text(encoding="utf-8").splitlines() if x.strip()]
    except (OSError, ValueError):
        raise ValueError("fichier d'usage illisible ou absent")
    if not lignes:
        raise ValueError("fichier d'usage vide")
    appels = cv.normaliser_appels(lignes)
    return appels, [(l.get("modele"), l.get("modele_renvoye")) for l in lignes]


def cout_majorant(appels_results: list, modele: str) -> float:
    """Majorant du coût d'appels lus dans results.json (jetons sans le détail du cache), si l'usage du callback manque
    ou est incomplet : chaque jeton d'invite au prix d'une écriture en cache (1,25 x l'entrée), au prix du modèle de
    l'agent (le client simulé, Haiku, ne coûte jamais plus), palier haut de Haiku au-delà de son seuil."""
    m = cv.PRIX[cv.normaliser_modele(modele)]
    total = 0.0
    for p, c, _ in appels_results:
        entree, sortie = m["entree"], m["sortie"]
        if m["palier"] and p > m["palier"][0]:
            entree, sortie = m["palier"][1], m["palier"][2]
        total += (p * entree * cv.ECRITURE_CACHE + c * sortie) / 1e6
    return total


def _usage_vide() -> dict:
    return {"appels": None, "estime": False, "renvoyes": [], "etat": "absent", "erreur": None, "cout_majore": None,
            "cout_inconnu": False}


def usage_tau2(results, usage, modele: str, reel: bool, appels_certains: bool = False) -> dict:
    """Usage d'une tentative τ-bench. En réel, le JSONL du callback fait foi et doit couvrir results.json (croisement du
    pilote) ; s'il manque ou ne couvre pas tout, le coût est majoré depuis results.json, ou déclaré inconnu. Sans JSONL,
    le coût n'est inconnu que si des appels ont certainement eu lieu (`appels_certains` : simulation avec au moins un
    message, ou dépassement de contexte) : un results.json sans simulation ou une simulation vide (premier appel en
    échec, Ctrl-C au démarrage) ne coûte rien (contre-vérification, constat F ; une capture en panne se voit à la partie
    normale suivante, par le croisement). À blanc, usage estimé depuis results.json s'il manque, comme au pilote.
    etat : complet, estimé, incomplet, majoré, illisible, absent."""
    out = _usage_vide()
    de_results, erreur_results = None, None
    if results is not None:
        try:
            de_results = pe.appels_tau2(results, estimer=not reel)
        except ValueError as e:
            erreur_results = f"results.json : {e}"
    present = Path(usage).is_file()
    try:
        appels, renvoyes = lire_usage(usage)
    except ValueError as e:
        if de_results and not reel:
            out.update(appels=[{"modele": modele, "prompt_tokens": p, "completion_tokens": c,
                                "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
                               for p, c, _ in de_results], estime=True, etat="estimé")
            return out
        out["etat"] = "illisible" if present else "absent"
        if reel and (present or de_results or appels_certains):
            out["erreur"] = f"usage {'illisible' if present else 'absent'} ({e})"
            if de_results:
                out.update(cout_majore=cout_majorant(de_results, modele), etat="majoré")
            else:
                out["cout_inconnu"] = True
        return out
    out.update(appels=appels, renvoyes=renvoyes, etat="complet")
    if erreur_results and reel:
        out["erreur"] = erreur_results
    elif reel and de_results is not None:
        try:
            cv.croiser(appels, de_results)
        except ValueError as e:
            out.update(etat="incomplet", erreur=str(e), cout_majore=cout_majorant(de_results, modele))
    return out


def _octets(x) -> int:
    return len((x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)).encode("utf-8"))


def cout_majorant_workbench(copies: list, modele: str, outils=None) -> float | None:
    """Majorant du coût d'une partie WorkBench sans usage lisible, depuis ses traces (`--log_traces`). Chaque appel au
    modèle donne au moins une étape (une par outil appelé, ou la réponse finale) : on compte un appel par étape. Jetons
    d'invite au plus les octets de l'entrée de l'étape (toute la conversation), de l'invite système (`_meta.json`) et des
    définitions d'outils figées, plus MARGE_FORMAT_JETONS (un jeton couvre au moins un octet) ; jetons de sortie au plus
    le maximum de sortie du modèle (MAX_SORTIE_JETONS), raisonnement compris : le raisonnement est facturé mais absent
    des traces (contre-vérification, constat G) ; prix de cout_majorant. None si les traces manquent ou sont illisibles,
    ou si le modèle est inconnu : le coût est alors inconnu."""
    traces = [c for c in copies if c.endswith("_traces.json")]
    metas = [c for c in copies if c.endswith("_meta.json")]
    if len(traces) != 1:
        return None
    try:
        etapes = [e for tache in json.loads(Path(traces[0]).read_text(encoding="utf-8")) for e in tache["steps"]]
        systeme = _octets(json.loads(Path(metas[0]).read_text(encoding="utf-8")).get("sample_system_prompt") or "") \
            if metas else 0
        if outils is None:
            outils = json.loads((DOSSIER_OUTILS / "workbench.json").read_text(encoding="utf-8"))["outils"]
        sortie_max = MAX_SORTIE_JETONS[cv.normaliser_modele(modele)]
        appels = [(_octets(e.get("llm_input") or "") + systeme + _octets(outils) + MARGE_FORMAT_JETONS, sortie_max, False)
                  for e in etapes]
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None
    return cout_majorant(appels, modele) if appels else None


def usage_workbench(usage, reel: bool, appels_faits: bool, majorant=None) -> dict:
    """Usage d'une tentative WorkBench (enveloppe usage_wrap.py). En réel, sans usage lisible alors que des appels ont
    certainement eu lieu (`appels_faits` : prédiction écrite sans erreur d'API, quel que soit son champ `error`, ou délai
    dépassé ; revue du 06/11, constat 4, et contre-vérification, constat F) : coût majoré depuis les traces
    (`majorant`, appelé sans argument), sinon inconnu ; dans les deux cas le lanceur s'arrête."""
    out = _usage_vide()
    present = Path(usage).is_file()
    try:
        appels, renvoyes = lire_usage(usage)
    except ValueError as e:
        out["etat"] = "illisible" if present else "absent"
        if reel and (present or appels_faits):
            out["erreur"] = f"usage {'illisible' if present else 'absent'} ({e})"
            m = majorant() if majorant else None
            if m is not None:
                out.update(cout_majore=m, etat="majoré")
            else:
                out["cout_inconnu"] = True
        return out
    out.update(appels=appels, renvoyes=renvoyes, etat="complet")
    return out


def commande_tau2(partie: dict, nom: str, reel: bool) -> list:
    """Commande du pilote (pilote_etape2.commande_tau2, cache des invites : 2.2), plus :
    - le délai de 30 minutes tenu par τ-bench lui-même (--timeout : la simulation finit avec la terminaison « timeout »
      et garde sa trace, 5.5 point 1) ;
    - --max-retries 0 : τ-bench ne rejoue plus lui-même une simulation en exception (3 fois par défaut) ; seule reste la
      relance du lanceur, comptée et déclarée (Q10 ; revue du 06/11, constat 6)."""
    return p2.commande_tau2(partie, nom, reel, True) + ["--timeout", str(DELAI_PARTIE_S), "--max-retries", "0"]


def _simulation_unique(chemin) -> dict | None:
    try:
        sims = json.loads(Path(chemin).read_text(encoding="utf-8")).get("simulations")
    except (OSError, ValueError, AttributeError):
        return None
    return sims[0] if isinstance(sims, list) and len(sims) == 1 and isinstance(sims[0], dict) else None


def erreur_workbench(chemin_csv) -> tuple:
    """(champ `error`, champ `full_response`) de l'unique ligne d'un fichier de prédictions WorkBench ("" : vide). Sur
    une exception, WorkBench écrit `str(e)` dans `error` et une réponse vide (src/evals/inference.py, _run_single_task) ;
    une fin normale a toujours une réponse (le texte de AgentResult)."""
    csv.field_size_limit(min(sys.maxsize, 2 ** 31 - 1))
    with open(chemin_csv, newline="", encoding="utf-8") as fh:
        lignes = list(csv.DictReader(fh))
    if len(lignes) != 1:
        raise ValueError(f"{Path(chemin_csv).name} : {len(lignes)} tâches (une attendue)")
    return (lignes[0].get("error") or "").strip(), (lignes[0].get("full_response") or "").strip()


def resultat_vide() -> dict:
    """Contrat de l'exécuteur (les clés absentes valent ces défauts ; l'exécuteur factice des tests n'en donne qu'une
    partie, comme au pilote) : ok, appels, estime, erreur, copies (pilote) ; code (code de retour du banc),
    delai_depasse, terminaison (raison d'arrêt de τ-bench ou champ `error` de WorkBench), type_erreur (τ-bench :
    `info.error_type` d'une simulation en erreur), renvoyes [(demandé, renvoyé)], trace (trace exploitable dans
    parties/), usage (état), cout_majore, cout_inconnu, pas (tours permis), non_lancee (WorkBench : arrêt décidé pendant
    l'attente de son tour, aucun enfant lancé), exception_muette (WorkBench : exception sans message, champ `error`
    vide et réponse vide)."""
    return {"ok": False, "appels": None, "estime": False, "erreur": None, "copies": [], "code": None,
            "delai_depasse": False, "terminaison": "", "type_erreur": "", "renvoyes": [], "trace": False,
            "usage": "absent", "cout_majore": None, "cout_inconnu": False, "pas": None, "non_lancee": False,
            "exception_muette": False}


def _fusionner_usage(res: dict, u: dict) -> None:
    res.update(appels=u["appels"], estime=u["estime"], renvoyes=u["renvoyes"], usage=u["etat"],
               cout_majore=u["cout_majore"], cout_inconnu=u["cout_inconnu"])


def resultat_exception(t: dict, ctx: dict, e: Exception) -> dict:
    """Résultat d'une tentative dont l'exécuteur a levé (disque plein, fichier illisible…), peut-être après que l'enfant
    a joué et dépensé (revue « ultra » du 06/11, constat 2). Le coût est lu dans l'usage de la tentative ; s'il ne se lit
    pas, il est inconnu (la reprise exigera --cout-retenu). Dans les deux cas, `traiter_tentative` arrête le lanceur."""
    r = dict(resultat_vide(), erreur=f"exception {type(e).__name__}", exception_executeur=True)
    usage = Path(ctx["sortie"]) / "usage" / f"{t['id']}.jsonl"
    try:
        appels, renvoyes = lire_usage(usage)
    except Exception:  # absent, vide, illisible ou mal formé : jamais une seconde exception dans ce chemin d'erreur
        appels, renvoyes = None, []
    if appels:
        r.update(appels=appels, renvoyes=renvoyes, usage="complet")
    else:
        r["cout_inconnu"] = True
    return r


def executer_partie(partie: dict, ctx: dict) -> dict:
    """Joue une tentative (une partie, une fois) et rend son résultat brut (voir resultat_vide). Ne lève pas : l'échec
    est une donnée, classée ensuite par classer()."""
    sortie, pid = ctx["sortie"], partie["id"]
    log = sortie / "logs" / f"{pid}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    usage = sortie / "usage" / f"{pid}.jsonl"
    usage.parent.mkdir(parents=True, exist_ok=True)
    env = p2.env_partie(ctx["env_enfant"], usage)
    env[pe.VAR_FICHIER_PID] = str(fichier_enfant(sortie, pid))  # revue « ultra » du 06/11, constat 3
    if partie["env"] == "WorkBench":
        return _executer_workbench(partie, ctx, env, log, usage)
    return _executer_tau2(partie, ctx, env, log, usage)


def fichier_enfant(sortie: Path, tid: str) -> Path:
    """Fichier où `pe.executer_enfant` note le PID de l'enfant d'une tentative tant qu'il tourne."""
    return Path(sortie) / DOSSIER_ENFANTS / f"{tid}.json"


def enfants_vivants(sortie: Path) -> list:
    """PID des enfants notés dans le dossier de vague et toujours vivants (ou notés sur une autre machine, où le PID ne
    se vérifie pas). Un lanceur tué (kill) laisse tourner ses enfants, qui dépensent encore et dont l'usage grandit :
    tant qu'il en reste, une reprise compterait trop peu et rejouerait des parties en cours (revue « ultra », constat 3)."""
    out = []
    for f in sorted((Path(sortie) / DOSSIER_ENFANTS).glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue  # fichier en cours d'écriture ou coupé : son enfant n'a jamais été noté en entier
        if not isinstance(d, dict):
            continue
        if d.get("machine") not in (None, socket.gethostname()):
            out.append(d.get("pid"))  # autre machine : le PID ne se vérifie pas ici
        elif pid_vivant(d.get("pid")) and processus_de_la_partie(d.get("pid"), d.get("commande")):
            out.append(d.get("pid"))
    return out


def processus_de_la_partie(pid, commande) -> bool:
    """Le processus vivant `pid` est bien l'enfant noté : sa ligne de commande contient l'interpréteur et le script
    notés. Après un redémarrage, un PID réutilisé par un autre processus n'est donc pas pris pour une partie qui
    dépense, et l'opérateur n'est pas invité à le tuer. Sans commande notée, ou si `ps` ne répond pas : oui (prudence)."""
    if not commande:
        return True
    try:
        r = subprocess.run(["ps", "-o", "command=", "-p", str(int(pid))], capture_output=True, text=True, timeout=10,
                           env=dict(os.environ, LC_ALL="C"))
    except (OSError, subprocess.SubprocessError, ValueError):
        return True
    if r.returncode != 0:  # le processus a fini entre-temps
        return False
    return all(str(c) in r.stdout for c in commande)


def _executer_tau2(partie: dict, ctx: dict, env: dict, log: Path, usage: Path) -> dict:
    sortie, reel, pid = ctx["sortie"], ctx["reel"], partie["id"]
    res = resultat_vide()
    nom = f"{'experience' if reel else 'essai-blanc'}-vague{ctx['vague']}-{ctx['horodatage']}-{pid}"
    cmd = commande_tau2(partie, nom, reel)
    res["pas"] = int(cmd[cmd.index("--max-steps") + 1])
    code = pe.executer_enfant(cmd, env, TAU2, log, ctx.get("cle"), delai=DELAI_PARTIE_S + MARGE_DELAI_S)
    res["code"], res["delai_depasse"] = code, code == -1
    erreurs = [] if code in (0, -1) else [f"tau2 : code de retour {code}"]
    source = TAU2 / "data" / "simulations" / nom / "results.json"
    results = None
    if source.is_file():
        cible = sortie / "parties" / f"tau2-{pid}" / "results.json"
        cible.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, cible)
        res["copies"].append(str(cible))
        sim = _simulation_unique(cible)
        if sim is not None:
            res["trace"], results = True, cible
            res["terminaison"] = str(sim.get("termination_reason") or "")
            res["type_erreur"] = str((sim.get("info") or {}).get("error_type") or "") \
                if isinstance(sim.get("info"), dict) else ""
            if res["terminaison"] == "infrastructure_error" and res["type_erreur"] == TYPE_ERREUR_CONTEXTE:
                res["trace"] = False  # simulation vide : rien à rejouer (revue du 06/11, constat 6)
        elif not res["delai_depasse"]:
            erreurs.append("results.json : une simulation attendue")
    elif not res["delai_depasse"]:
        erreurs.append("results.json absent")
    # Une simulation vide (erreur d'infrastructure de τ-bench) ne se croise pas avec l'usage : seul le JSONL compte.
    avec_messages = results is not None and bool((_simulation_unique(results) or {}).get("messages"))
    # Appels certains (constat F) : une simulation avec messages, ou un dépassement de contexte (la conversation a
    # grandi, appel après appel, jusqu'à la limite ; τ-bench n'en garde qu'une simulation vide). Pas un results.json seul :
    # τ-bench l'écrit dès la préparation du lot, avant tout appel (runner/checkpoint.py, try_resume).
    certains = avec_messages or res["type_erreur"] == TYPE_ERREUR_CONTEXTE
    u = usage_tau2(results if avec_messages else None, usage, partie["modele"], reel, appels_certains=certains)
    if reel and res["delai_depasse"] and u["etat"] == "absent":
        u["cout_inconnu"] = True  # 35 minutes de jeu sans aucune ligne d'usage : le coût n'est pas compté
    _fusionner_usage(res, u)
    if u["erreur"]:
        erreurs.append(u["erreur"])
    res["erreur"] = " ; ".join(erreurs) or None
    # Filet de 35 minutes : une simulation déjà finie et enregistrée se classe sur sa terminaison (constat 8).
    res["ok"] = not erreurs and (not res["delai_depasse"] or results is not None)
    return res


def seconde_du_nom_workbench(nom: str) -> float | None:
    """Heure (secondes depuis l'époque, heure locale) écrite par WorkBench dans le nom de ses prédictions :
    <modèle>_all_<AAAA-MM-JJ_HH-MM-SS>.csv (src/evals/inference.py). None si le nom ne suit pas ce format."""
    try:
        return datetime.strptime(Path(nom).stem.rsplit("_all_", 1)[1], "%Y-%m-%d_%H-%M-%S").timestamp()
    except (IndexError, ValueError):
        return None


def noms_workbench_existants(sortie: Path) -> set:
    """Noms des fichiers de prédictions WorkBench déjà présents dans le dossier de la vague (reprise)."""
    return {p.stem for d in ("parties", "ecartees") for p in (Path(sortie) / d).rglob("*_all_*.csv")}


def prendre_verrou_workbench(compta=None):
    """Verrou commun à tous les lanceurs, réels et à blanc (contre-vérification, constat C) : flock exclusif sur
    `externe/workbench-run/data/results.verrou`, tenu pendant toute la partie WorkBench, car WorkBench écrit dans un
    dossier commun où chaque lanceur ramasse « les fichiers nouveaux ». Attente par essais successifs, pour s'arrêter si
    l'arrêt est décidé entre-temps (rend None) ; libéré par le système si le processus meurt. Rend le descripteur."""
    chemin = WB_RUN / "data" / NOM_VERROU_WB
    chemin.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(chemin, os.O_CREAT | os.O_RDWR, 0o644)
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fd
        except BlockingIOError:
            if compta is not None and compta.doit_arreter():
                os.close(fd)
                return None
            time.sleep(0.25)


def liberer_verrou_workbench(fd) -> None:
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def _executer_workbench(partie: dict, ctx: dict, env: dict, log: Path, usage: Path) -> dict:
    """Comme au pilote : parties WorkBench sérialisées (fichiers de sortie nommés à la seconde, dossier commun), dans le
    processus (`verrou_wb`) et entre lanceurs (prendre_verrou_workbench, constat C).
    WorkBench nomme ses prédictions à la seconde près, et le moteur de rejeu, verdicts.py et fiches.py identifient une
    partie WorkBench par ce nom : deux parties lancées dans la même seconde (constaté à l'essai à blanc complet de la
    vague 1, 3 paires sur 388 parties) se confondraient. Une partie ne démarre donc qu'après la seconde inscrite dans
    le nom de la précédente, et un nom déjà vu dans la vague est un échec technique (la relance aura un autre nom)."""
    reel = ctx["reel"]
    res = resultat_vide()
    with ctx["verrou_wb"]:
        fd_commun = prendre_verrou_workbench(ctx.get("compta"))
        if fd_commun is None:  # arrêt décidé pendant qu'un autre lanceur jouait sa partie WorkBench
            res["non_lancee"] = True
            return res
        try:
            lance = _lancer_workbench(partie, ctx, env, log, res)
        finally:
            liberer_verrou_workbench(fd_commun)
    if lance is None:
        return res
    code, doublons = lance
    res["code"], res["delai_depasse"] = code, code == -1
    erreurs = [] if code in (0, -1) else [f"WorkBench : code de retour {code}"]
    if doublons:
        erreurs.append(f"nom de fichier WorkBench déjà utilisé dans la vague : {', '.join(doublons)}")
    csvs = [c for c in res["copies"] if c.endswith(".csv")]
    ecrite, reponse = False, ""  # une prédiction écrite prouve que l'agent a tourné (constat 4)
    if len(csvs) == 1:
        try:
            res["terminaison"], reponse = erreur_workbench(csvs[0])
            res["trace"] = ecrite = True
        except (OSError, ValueError, csv.Error) as e:
            erreurs.append(f"prédictions illisibles : {e}")
    elif not res["delai_depasse"]:
        erreurs.append("csv de prédictions absent" if not csvs else f"{len(csvs)} csv de prédictions (un attendu)")
    term = res["terminaison"]
    api = term.startswith(WB_ERREURS_API)
    # Exception sans message (constat I) : champ `error` vide, comme une fin normale, mais réponse vide.
    res["exception_muette"] = ecrite and not term and not reponse
    if (term and term != WB_MESSAGE_ARRET and not api) or res["exception_muette"]:
        # Fenêtre de contexte ou exception : WorkBench ne recopie pas les actions déjà faites (src/evals/inference.py,
        # _run_single_task) : aucune trace exploitable (revue du 06/11, constats 5 et 9 ; contre-vérification, I).
        res["trace"] = False
    # Appels certains (constats 4 et F) : prédiction écrite sans erreur d'API, ou délai dépassé. Après une erreur d'API
    # sans usage, aucun appel n'a abouti (l'enveloppe note chaque réponse) : coût nul, comme un premier appel τ-bench en
    # échec ; une capture en panne se verrait à la partie suivante.
    u = usage_workbench(usage, reel, appels_faits=res["delai_depasse"] or (ecrite and not api),
                        majorant=lambda: cout_majorant_workbench(res["copies"], partie["modele"]))
    _fusionner_usage(res, u)
    if u["erreur"]:
        erreurs.append(u["erreur"])
    res["erreur"] = " ; ".join(erreurs) or None
    res["ok"] = not erreurs and (not res["delai_depasse"] or ecrite)  # filet : prédiction écrite, classée (constat 8)
    return res


def _lancer_workbench(partie: dict, ctx: dict, env: dict, log: Path, res: dict):
    """Sous les deux verrous : attend la seconde qui suit le nom de la partie WorkBench précédente, revérifie l'arrêt,
    lance WorkBench et range ses fichiers dans parties/. (code de retour, noms en double), ou None si la partie n'est
    pas lancée (arrêt décidé pendant l'attente de son tour : elle reste en file, revue du 06/11, constat 2)."""
    sortie, pid = ctx["sortie"], partie["id"]
    etat = ctx.setdefault("wb_etat", {"prochain": 0.0, "noms": noms_workbench_existants(sortie)})
    while time.time() < etat["prochain"]:
        time.sleep(min(0.25, max(0.01, etat["prochain"] - time.time())))
    compta = ctx.get("compta")
    if compta is not None and compta.doit_arreter():
        res["non_lancee"] = True
        return None
    csv_taches = pe.ecrire_taches_workbench(partie, sortie / "taches" / pid, WORKBENCH)
    avant = pe._fichiers(WB_RUN / "data" / "results")
    code = pe.executer_enfant(p2.commande_workbench(csv_taches, partie["modele"]), env, WB_RUN, log, ctx.get("cle"),
                              delai=DELAI_PARTIE_S)
    nouveaux = sorted(pe._fichiers(WB_RUN / "data" / "results") - avant)
    noms = [p.stem for p in nouveaux if p.suffix == ".csv"]
    secondes = [seconde_du_nom_workbench(n) for n in noms]
    if noms and None not in secondes:
        etat["prochain"] = max(etat["prochain"], max(secondes) + 1)
    else:  # nom absent ou inattendu : la seconde inscrite est au plus celle-ci
        etat["prochain"] = max(etat["prochain"], math.floor(time.time()) + 1)
    doublons = [n for n in noms if n in etat["noms"]]
    etat["noms"].update(noms)
    if nouveaux:
        cible = sortie / "parties" / f"workbench-{pid}"
        cible.mkdir(parents=True, exist_ok=True)
        for p in nouveaux:  # un doublon est renommé : fiches.py cherche les prédictions par leur nom dans tout le dossier
            nom = ("nom-deja-utilise-" + p.name) if doublons else p.name
            shutil.move(str(p), str(cible / nom))
            res["copies"].append(str(cible / nom))
    return code, doublons


# =================================================================================================================
# 8. Le classement des fins de partie
# =================================================================================================================
def classer(tentative: dict, r: dict) -> tuple:
    """(statut, arrêt, motif d'échec) d'une tentative.
    - processus tué par le filet sans trace, ou terminaison « timeout » : arrêtée (30 minutes), pas un échec technique
      (5.5, point 1) ; une simulation déjà finie quand le filet tue le processus se classe sur sa terminaison (constat 8) ;
    - « max_steps » : arrêtée par les tours (100 en réel) ; fenêtre de contexte (y compris l'erreur d'infrastructure de
      τ-bench dont le type est ContextWindowExceededError, constat 6), limite propre de WorkBench : arrêtée ;
    - WorkBench : seules les erreurs d'API (WB_ERREURS_API) sont des échecs techniques ; toute autre exception est une
      exception d'outil, arrêtée sans trace (constat 5), y compris une exception sans message (contre-vérification,
      constat I) ;
    - « infrastructure_error », « unexpected_error » (τ-bench), processus en erreur, fichiers ou usage manquants : échec
      technique ;
    - sinon : terminée."""
    if r.get("delai_depasse") and not r.get("trace"):
        return ARRETEE, ARRET_30_MIN, None
    if not r.get("ok"):
        return ECHEC, None, r.get("erreur") or "échec sans message"
    term = (r.get("terminaison") or "").strip()
    if tentative["env"] == "WorkBench":
        if not term:
            return (ARRETEE, ARRET_EXCEPTION_OUTIL, None) if r.get("exception_muette") else (TERMINEE, None, None)
        if term == WB_MESSAGE_ARRET:
            return ARRETEE, ARRET_WORKBENCH, None
        if term == WB_MESSAGE_CONTEXTE:
            return ARRETEE, ARRET_CONTEXTE, None
        if term.startswith(WB_ERREURS_API):
            return ECHEC, None, f"WorkBench : {term[:300]}"
        return ARRETEE, ARRET_EXCEPTION_OUTIL, None
    if term == "infrastructure_error" and r.get("type_erreur") == TYPE_ERREUR_CONTEXTE:
        return ARRETEE, ARRET_CONTEXTE, None
    if term in TERMINAISONS_ECHEC:
        return ECHEC, None, f"τ-bench : terminaison {term}"
    if term == "max_steps":
        return ARRETEE, f"{r.get('pas') or pe.MAX_PAS_REEL} tours", None
    if term == "timeout":
        return ARRETEE, ARRET_30_MIN, None
    if term == "context_window_exceeded":
        return ARRETEE, ARRET_CONTEXTE, None
    return TERMINEE, None, None


class Noms:
    """Noms de modèle renvoyés par l'API (2.2 ; 2.5, point 6). Référence par banc et modèle demandé (« tau2:… »,
    « workbench:… » : τ-bench passe par l'API Anthropic, WorkBench par l'API compatible OpenAI, qui peuvent ne pas
    renvoyer la même chaîne ; revue du 06/11, constat 7) : celle de la vague 1, ou la première observation. Tout autre
    nom est un changement : la partie est exclue et le lanceur s'arrête."""

    def __init__(self, reference=None, source="première observation", observes=None, changements=None, absents=0):
        self.reference = dict(reference or {})
        self.source = source
        self.observes = {k: dict(v) for k, v in (observes or {}).items()}
        self.changements = list(changements or [])
        self.absents = int(absents or 0)

    @classmethod
    def depuis_json(cls, d: dict, source=None):
        d = d or {}
        return cls(d.get("reference"), source or d.get("source") or "première observation", d.get("observes"),
                   d.get("changements"), d.get("appels_sans_nom"))

    def examiner(self, tentative_id: str, renvoyes: list, banc: str) -> tuple:
        """(changements, appels sans nom) d'une tentative jouée sur `banc` (« tau2 » ou « workbench ») ; met à jour la
        référence et les compteurs. Sous verrou."""
        changes, absents = [], 0
        for dem, ren in renvoyes or []:
            d = f"{banc}:{court(dem) or '?'}"
            if not isinstance(ren, str) or not ren:
                absents += 1
                continue
            self.observes.setdefault(d, {})
            self.observes[d][ren] = self.observes[d].get(ren, 0) + 1
            ref = self.reference.get(d)
            if ref is None:
                self.reference[d] = ren
            elif ren != ref and not any(c["modele"] == d and c["recu"] == ren for c in changes):
                changes.append({"tentative": tentative_id, "modele": d, "attendu": ref, "recu": ren})
        self.changements += changes
        self.absents += absents
        return changes, absents

    def json(self) -> dict:
        return {"reference": self.reference, "source": self.source, "observes": self.observes,
                "changements": self.changements, "appels_sans_nom": self.absents}


def ligne_tentative(t: dict, statut: str, arret, motif, r: dict, b, cout: float, majore: bool, debut: str) -> dict:
    """Ligne de cout.json : champs du pilote (id, env, modele, tache, ok, erreur, jetons, cout_usd, estime), plus les
    nouveaux (partie, tentative, passage, rang, vague, statut, arret, terminaison, finale, exclue, motif_exclusion,
    dossier, modeles_renvoyes, usage, cout_majore, debut, fin). `ok` vaut vrai si et seulement si la tentative est
    gardée (fichiers dans parties/) : c'est le statut technique que lit simulation/rejeu/entrees.py."""
    l = {"id": t["id"], "env": t["env"], "modele": t["modele"], "tache": t["tache"], "ok": False, "erreur": motif}
    if b:
        l.update(b)
    else:
        l.update({"appels": 0, "appels_hauts": 0, "jetons_entree": None, "jetons_non_caches": None,
                  "cache_ecriture": None, "cache_lecture": None, "jetons_sortie": None, "cout_usd": None,
                  "estime": bool(r.get("estime"))})
    if majore:
        l["cout_usd"] = round(cout, 8)
    usage = r.get("usage") or ("estimé" if r.get("estime") else ("complet" if b else "absent"))
    terminaison = (r.get("terminaison") or "") + (f" ({r['type_erreur']})" if r.get("type_erreur") else "")
    l.update({"partie": t["partie"], "tentative": t["tentative"], "passage": t["passage"], "rang": t["rang"],
              "vague": t["vague"], "statut": statut, "arret": arret, "terminaison": terminaison[:300],
              "finale": False, "exclue": False, "motif_exclusion": None, "dossier": None,
              "modeles_renvoyes": sorted({ren for _, ren in (r.get("renvoyes") or []) if isinstance(ren, str) and ren}),
              "usage": usage, "cout_majore": majore, "cout_inconnu": False, "debut": debut, "fin": maintenant()})
    return l


def traiter_tentative(t: dict, r: dict, debut: str) -> tuple:
    """(ligne, coût à compter, raison d'arrêter le lanceur ou None) d'une tentative, avant l'examen des noms de modèle.
    Le coût de chaque tentative est compté, échecs compris : c'est de l'argent dépensé. Un coût qui ne peut pas être
    compté (usage illisible sans majorant, modèle inconnu) est noté `cout_inconnu` dans la ligne et arrête le lanceur ;
    la reprise exige alors un montant retenu (--cout-retenu ; revue du 06/11, constats 10 et 11)."""
    statut, arret, motif = classer(t, r)
    coupure, b = None, None
    inconnu = bool(r.get("cout_inconnu"))
    if r.get("appels"):
        try:
            b = cv.bilan(r["appels"], bool(r.get("estime")))
        except ValueError as e:  # modèle inconnu, valeurs incohérentes : le coût ne peut plus être compté
            statut, arret, motif = ECHEC, None, _joindre(motif, f"usage invalide : {e}")
            coupure = (f"tentative {t['id']} : usage invalide ({e}), coût non compté : à chiffrer, puis reprendre avec "
                       f"--cout-retenu {t['id']}=<USD>")
            inconnu = True
    cout = b["cout_usd"] if b else 0.0
    majore = r.get("cout_majore") is not None
    if majore:
        cout, inconnu = max(cout, float(r["cout_majore"])), False
        coupure = coupure or f"tentative {t['id']} : usage incomplet ou illisible, coût majoré à {cout:.6f} USD"
    if inconnu:
        coupure = coupure or (f"tentative {t['id']} : usage illisible, coût non compté : à chiffrer, puis reprendre "
                              f"avec --cout-retenu {t['id']}=<USD>")
    if r.get("exception_executeur"):  # revue « ultra » du 06/11, constat 2 : jamais de relance silencieuse
        coupure = coupure or (f"tentative {t['id']} : {r.get('erreur')} dans l'exécuteur, coût lu dans son usage : "
                              f"arrêt avant toute nouvelle partie ; reprendre avec --reprendre")
    ligne = ligne_tentative(t, statut, arret, motif, r, b, cout, majore, debut)
    ligne["cout_inconnu"] = inconnu
    return ligne, cout, coupure


def ranger(sortie: Path, t: dict, garder: bool) -> str | None:
    """parties/ ne garde que les tentatives gardées (le moteur de rejeu et verdicts_csv les lisent toutes) ; les autres
    vont dans ecartees/. Rend le chemin relatif des fichiers de la tentative, ou None."""
    nom = f"{banc_de(t['env'])}-{t['id']}"
    src = sortie / "parties" / nom
    if not src.exists():
        return None
    if garder:
        return f"parties/{nom}"
    dst = sortie / "ecartees" / nom
    if dst.exists():
        dst = sortie / "ecartees" / f"{nom}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return str(dst.relative_to(sortie))


def mettre_de_cote(sortie: Path, t: dict, suffixe: str) -> str | None:
    """Met à l'écart tous les fichiers d'une tentative interrompue (partie, usage, journal, tâches) : la partie sera
    rejouée sous le même identifiant, sans que l'usage déjà compté s'ajoute à celui de la nouvelle tentative."""
    tid, banc = t["id"], banc_de(t.get("env") or "")
    dst = sortie / "ecartees" / f"{banc}-{tid}-{suffixe}"
    for src, nom in ((sortie / "parties" / f"{banc}-{tid}", "partie"), (sortie / "usage" / f"{tid}.jsonl", "usage.jsonl"),
                     (sortie / "logs" / f"{tid}.log", "log.txt"), (sortie / "taches" / tid, "taches")):
        if src.exists():
            dst.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst / nom))
    return str(dst.relative_to(sortie)) if dst.exists() else None


def tentative(partie: dict, k: int, vague: int) -> dict:
    t = dict(partie)
    t.update(partie=partie["id"], tentative=k, vague=vague, id=partie["id"] if k == 1 else f"{partie['id']}-t{k}")
    return t


# =================================================================================================================
# 9. Les sorties : tentatives.jsonl, cout.json, modeles_renvoyes.json
# =================================================================================================================
class Registre:
    """tentatives.jsonl (un événement par ligne, écrit à chaque début et fin de tentative : fait foi pour la reprise) et
    cout.json (format du pilote, réécrit au plus toutes les PERIODE_COUT_S secondes, et à la fin)."""

    def __init__(self, sortie: Path, entete: dict, lignes: list, compta):
        self.sortie, self.entete, self.compta = sortie, entete, compta
        self.lignes = list(lignes)
        self.chemin = sortie / "tentatives.jsonl"
        self._verrou = threading.Lock()
        self._dernier = 0.0

    def evenement(self, ev: dict) -> None:
        with self._verrou:
            with open(self.chemin, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(ev, ensure_ascii=False) + "\n")

    def debut(self, t: dict) -> None:
        self.evenement({"evenement": "début", "id": t["id"], "horodatage": maintenant(),
                        "tentative": {k: t[k] for k in CHAMPS_TENTATIVE}})

    def fin(self, ligne: dict, evenement: str = "fin", id_evenement=None) -> None:
        self.evenement({"evenement": evenement, "id": id_evenement or ligne["id"], "ligne": ligne})
        with self._verrou:
            self.lignes.append(ligne)
            ecrire = time.monotonic() - self._dernier >= PERIODE_COUT_S
        if ecrire:
            self.ecrire_cout()

    def ecrire_cout(self, **maj) -> None:
        with self._verrou:
            self.entete.update(maj)
            obj = dict(self.entete)
            obj.update(plafond_usd=self.compta.plafond, seuil_arret_usd=self.compta.seuil,
                       cumul_usd=round(self.compta.cumul, 8), arret=self.compta.arret,
                       usage_estime=any(l.get("estime") for l in self.lignes), parties=list(self.lignes))
            pe.ecrire_json_atomique(self.sortie / "cout.json", obj)
            self._dernier = time.monotonic()


EVENEMENTS_AVEC_LIGNE = ("fin", "interruption", "cout_retenu")
EVENEMENTS_FIN = ("fin", "interruption", "non_lancee")  # referment un « début »


def lire_tentatives(chemin) -> tuple:
    """(lignes des tentatives finies, interrompues ou chiffrées après coup, tentatives commencées sans fin) de
    tentatives.jsonl. Une tentative « non lancée » (arrêt décidé pendant qu'elle attendait son tour) referme son début
    sans ligne : elle reste en file. ErreurPilote si une ligne est illisible : la reprise est refusée, le coût ne serait
    plus compté exactement."""
    chemin = Path(chemin)
    if not chemin.is_file():
        return [], []
    lignes, debuts, fins = [], {}, {}
    for k, brut in enumerate(chemin.read_text(encoding="utf-8").splitlines(), 1):
        if not brut.strip():
            continue
        try:
            ev = json.loads(brut)
            sorte, ident = ev["evenement"], ev["id"]
            ligne = ev["ligne"] if sorte in EVENEMENTS_AVEC_LIGNE else None
            if sorte in EVENEMENTS_AVEC_LIGNE and not isinstance(ligne, dict):
                raise TypeError
        except (ValueError, KeyError, TypeError):
            raise ErreurPilote(f"{chemin.name}, ligne {k} illisible : reprise refusée (le coût ne serait plus compté "
                               f"exactement)")
        if sorte == "début":
            debuts.setdefault(ident, []).append(ev.get("tentative") or {"id": ident})
        if sorte in EVENEMENTS_FIN:
            fins[ident] = fins.get(ident, 0) + 1
        if ligne is not None:
            lignes.append(ligne)
    orphelines = []
    for ident, evs in debuts.items():
        orphelines += evs[fins.get(ident, 0):]
    return lignes, orphelines


def couts_inconnus_en_suspens(lignes: list) -> list:
    """Identifiants des tentatives au coût inconnu (`cout_inconnu`) qui n'ont pas encore reçu de montant retenu."""
    retenus = {l.get("cout_retenu_pour") for l in lignes if l.get("statut") == COUT_RETENU}
    return sorted(l["id"] for l in lignes if l.get("cout_inconnu") and l["id"] not in retenus)


def orphelines_illisibles(sortie: Path, orphelines: list) -> list:
    """Identifiants des tentatives interrompues dont l'usage existe mais ne peut pas être compté (coût inconnu)."""
    out = []
    for t in orphelines:
        usage = Path(sortie) / "usage" / f"{t['id']}.jsonl"
        if usage.is_file():
            try:
                cv.bilan(lire_usage(usage)[0])
            except ValueError:
                out.append(t["id"])
    return out


def ligne_cout_retenu(origine: dict, montant: float, horodatage: str) -> dict:
    """Ligne « coût retenu » : montant chiffré par l'opérateur (console) pour une tentative au coût inconnu, ajouté au
    cumul de la vague (revue du 06/11, constat 11). Aucune partie jouée, aucune tentative comptée."""
    t = {k: origine.get(k) for k in CHAMPS_TENTATIVE}
    t.update(id=f"{origine['id']}-cout-retenu-{horodatage}", tentative=0)
    l = ligne_tentative(t, COUT_RETENU, None, f"coût retenu par l'opérateur pour {origine['id']} (--cout-retenu)",
                        dict(resultat_vide(), usage="retenu"), None, montant, True, "")
    l.update(cout_usd=round(float(montant), 8), cout_retenu_pour=origine["id"])
    return l


def recuperer_interrompues(sortie: Path, orphelines: list, registre: Registre, horodatage: str,
                           couts_retenus=None) -> list:
    """Tentatives commencées et jamais finies (arrêt brutal du lanceur) : leur coût est lu dans leur usage et compté,
    leurs fichiers sont mis à l'écart ; la partie sera rejouée (une interruption ne compte pas comme une tentative). Si
    l'usage existe mais est illisible, le coût est celui retenu par l'opérateur (--cout-retenu), exigé avant (preparer) ;
    ErreurPilote sinon."""
    couts_retenus = couts_retenus or {}
    lignes = []
    for t in orphelines:
        tid, env = t["id"], t.get("env", "")
        usage = sortie / "usage" / f"{tid}.jsonl"
        b, renvoyes, retenu = None, [], None
        if usage.is_file():
            try:
                appels, renvoyes = lire_usage(usage)
                b = cv.bilan(appels)
            except ValueError as e:
                if tid not in couts_retenus:
                    raise ErreurPilote(f"reprise : usage illisible de la tentative interrompue {tid} ({e}) : coût "
                                       f"inconnu ; le chiffrer, puis reprendre avec --cout-retenu {tid}=<USD>")
                b, renvoyes, retenu = None, [], float(couts_retenus[tid])
        dossier = mettre_de_cote(sortie, {"id": tid, "env": env}, f"interrompue-{horodatage}")
        fichier_enfant(sortie, tid).unlink(missing_ok=True)  # son enfant est mort (preparer : enfants_vivants)
        tt = {k: t.get(k) for k in CHAMPS_TENTATIVE}
        tt["id"] = f"{tid}-interrompue-{horodatage}"
        r = dict(resultat_vide(), renvoyes=renvoyes,
                 usage="retenu" if retenu is not None else ("complet" if b else "absent"))
        ligne = ligne_tentative(tt, INTERROMPUE, None, "tentative interrompue (arrêt brutal du lanceur)", r, b,
                                retenu if retenu is not None else (b["cout_usd"] if b else 0.0), retenu is not None, "")
        if retenu is not None:
            ligne["cout_retenu_pour"] = tid
        ligne["dossier"] = dossier
        registre.fin(ligne, evenement="interruption", id_evenement=tid)
        lignes.append(ligne)
    return lignes


def historique_parties(lignes: list) -> dict:
    """{partie: {"echecs": n, "noms": n}} : tentatives en échec technique et tentatives exclues pour nom de modèle
    changé. Une interruption ou un coût retenu ne comptent pas comme une tentative."""
    h: dict = {}
    for l in lignes:
        if l.get("statut") == COUT_RETENU:
            continue
        d = h.setdefault(l["partie"], {"echecs": 0, "noms": 0})
        if l.get("statut") == ECHEC:
            d["echecs"] += 1
        elif l.get("statut") == EXCLUE_NOM:
            d["noms"] += 1
    return h


def file_d_attente(parties: list, lignes: list) -> list:
    """[(partie, numéro de tentative)] des parties sans fin définitive, dans l'ordre de jeu. Le numéro suit les
    tentatives déjà comptées : échec technique (relancée une fois) et exclusion pour nom de modèle changé (rejouée une
    fois, à la reprise) ; une interruption ne compte pas."""
    h = historique_parties(lignes)
    finales = {l["partie"] for l in lignes if l.get("finale")}
    return [(x, 1 + h.get(x["id"], {}).get("echecs", 0) + h.get(x["id"], {}).get("noms", 0))
            for x in parties if x["id"] not in finales]


# =================================================================================================================
# 9. La boucle de jeu
# =================================================================================================================
class JournalVague(pe.Journal):
    """Deux journaux (contre-vérification, constat E) : journal.log, visible (console et fichier), où aucune ligne ne
    nomme la partie ni le modèle d'une tentative WorkBench ; journal_complet.log, jamais affiché, qui a toutes les lignes
    en entier et dont la première dit ENTETE_JOURNAL_COMPLET. Les parties WorkBench se jouant une à une, une fin
    distinguée au journal visible suffirait à retrouver la partie par élimination."""

    def __init__(self, dossier: Path, cle=None):
        super().__init__(Path(dossier) / "journal.log", cle)
        self.complet = Path(dossier) / NOM_JOURNAL_COMPLET
        if not self.complet.exists():
            self.complet.write_text(ENTETE_JOURNAL_COMPLET + "\n", encoding="utf-8")

    def ecrire(self, texte: str, complet: str | None = None) -> None:
        horodatage = datetime.now().isoformat(timespec="seconds")
        visible = f"{horodatage} {self.purger(texte)}"
        with self._verrou:
            with open(self.chemin, "a", encoding="utf-8") as fh:
                fh.write(visible + "\n")
            with open(self.complet, "a", encoding="utf-8") as fh:
                fh.write(f"{horodatage} {self.purger(texte if complet is None else complet)}\n")
        print(visible, flush=True)


def noter(journal, visible: str, complet: str | None = None) -> None:
    """Écrit `visible` au journal ; `complet` (la ligne détaillée) au journal complet, si le journal en a un."""
    if isinstance(journal, JournalVague):
        journal.ecrire(visible, complet)
    else:
        journal.ecrire(visible)


_PARTIE_WB = re.compile(r"WorkBench-(?:haiku|sonnet|opus)-p\d+-\S+")


def masquer_workbench(texte: str) -> str:
    """Texte sans nom de modèle ni identifiant de partie WorkBench, pour le journal visible."""
    for m in MODELES:
        texte = texte.replace(m, "<modèle>")
    return _PARTIE_WB.sub("<partie WorkBench>", texte)


def arret_visible(arret):
    """Motif d'arrêt tel qu'il s'affiche (journal visible, console, rapport de vague) : sans partie ni modèle
    WorkBench (constat E ; revue « ultra » du 06/11, constat 1). Le motif complet va au journal complet."""
    return masquer_workbench(arret) if arret else arret


def lignes_de_fin(t: dict, ligne: dict, cumul: float) -> tuple:
    """(ligne visible, ligne complète) de la fin d'une tentative. τ-bench : la même ligne. WorkBench (constat E) : la
    ligne visible ne nomme ni la partie ni le modèle, et ne dit comment la partie a fini que pour un échec technique,
    une interruption ou un nom de modèle changé : sinon l'ordre de jeu suffirait à retrouver une exception d'outil."""
    complet = (f"fin {ligne['id']} statut={ligne['statut']}" + (f" ({ligne['arret']})" if ligne["arret"] else "")
               + f" cumul={cumul:.6f} USD" + (f" ; {ligne['erreur']}" if ligne["erreur"] else ""))
    if t["env"] != "WorkBench":
        return complet, complet
    if ligne.get("terminaison"):
        complet += f" ; terminaison : {ligne['terminaison']}"
    visible = "fin d'une tentative WorkBench"
    if ligne["statut"] in (ECHEC, INTERROMPUE, EXCLUE_NOM):
        visible += f" : {ligne['statut']}" + (f" ; {masquer_workbench(ligne['erreur'])}" if ligne["erreur"] else "")
    return f"{visible} ; cumul={cumul:.6f} USD", complet


def lancer_vague(file: list, concurrence: int, compta, ctx: dict, journal, executeur=executer_partie) -> None:
    """Joue la file [(partie, tentative)] (1 à 3 parties à la fois). Avant CHAQUE nouvelle tentative : arrêt si le coût
    cumulé a atteint le seuil d'arrêt de la vague (Comptable : 80 % du plafond à la vague 1 ; à la vague 2, le plus
    petit de 95 % du plafond et du plafond moins 15 $) ou si un arrêt a été demandé. Après chaque tentative : coût
    compté (échecs compris), noms de modèle examinés, fichiers rangés, ligne écrite ; un premier échec technique est
    relancé aussitôt ; un nom de modèle changé (la partie sera rejouée une fois, à la reprise), un coût non compté,
    SERIE_ECHECS_MAX échecs techniques ou SERIE_EXCEPTIONS_OUTIL_MAX exceptions d'outil WorkBench de suite arrêtent le
    lanceur (les parties en cours se terminent ; une partie WorkBench qui attendait son tour n'est pas lancée)."""
    attente = deque(file)
    verrou = threading.Lock()
    interruption = threading.Event()
    serie, serie_outil = [0], [0]
    reg, noms, sortie = ctx["registre"], ctx["noms"], ctx["sortie"]
    ctx["compta"] = compta  # lu par _executer_workbench avant de lancer une partie (constat 2)
    historique = ctx.setdefault("historique", {})
    exceptions_outil = ctx.setdefault("exceptions_outil", {})  # {environnement: n}, jamais par modèle (constat 5)

    def conclure(t: dict, partie: dict, k: int, r: dict, debut: str) -> dict:
        ligne, cout, coupure = traiter_tentative(t, r, debut)
        evenement = "fin"
        with verrou:
            changes, absents = noms.examiner(t["id"], r.get("renvoyes") or [], banc_de(t["env"]))
            statut = ligne["statut"]
            if changes:
                statut = EXCLUE_NOM
                detail = ", ".join(f"{c['modele']} : {c['recu']} au lieu de {c['attendu']}" for c in changes)
                ligne["erreur"] = _joindre(ligne["erreur"], f"nom de modèle renvoyé changé ({detail})")
                coupure = (f"nom de modèle renvoyé changé ({detail}) : arrêt ; on ne reprend que si l'ancien nom "
                           f"revient (2.5, point 6)")
            elif absents and statut in (TERMINEE, ARRETEE):
                statut = ECHEC
                ligne["erreur"] = _joindre(ligne["erreur"], f"nom de modèle renvoyé absent ({absents} appel(s))")
            if statut == ECHEC and (interruption.is_set() or r.get("code") in CODES_INTERRUPTION):
                # Partie coupée par l'interruption de l'opérateur (Ctrl-C atteint aussi les bancs) : ce n'est pas un échec
                # technique ; coût compté, fichiers mis à l'écart, partie rejouée à la reprise sous le même numéro.
                statut, evenement = INTERROMPUE, "interruption"
            if statut != ARRETEE:
                ligne["arret"] = None
            outil = ligne["arret"] == ARRET_EXCEPTION_OUTIL  # WorkBench a perdu les actions : jamais gardée
            gardee = statut in (TERMINEE, ARRETEE) and bool(r.get("trace", r.get("ok"))) and not outil
            h = historique.setdefault(t["partie"], {"echecs": 0, "noms": 0})
            if statut == ECHEC:
                h["echecs"] += 1
                finale = h["echecs"] >= TENTATIVES_MAX
                motif = "échec technique (deux tentatives)" if finale else None
            elif statut == INTERROMPUE:
                finale, motif = False, None
            elif statut == EXCLUE_NOM:  # rejouée une fois, à la reprise ; la tentative exclue reste déclarée
                h["noms"] += 1
                finale = h["noms"] >= EXCLUSIONS_NOM_MAX
                motif = MOTIF_NOM_DEUX_FOIS if finale else MOTIF_NOM_REJOUEE
            elif not gardee:
                finale, motif = True, (MOTIF_EXCEPTION_OUTIL if outil else MOTIF_SANS_TRACE)
            else:
                finale, motif = True, None
            if t["env"] == "WorkBench" and statut != INTERROMPUE:
                if outil:
                    exceptions_outil[t["env"]] = exceptions_outil.get(t["env"], 0) + 1
                    serie_outil[0] += 1
                    if serie_outil[0] >= SERIE_EXCEPTIONS_OUTIL_MAX:
                        compta.arreter(f"{serie_outil[0]} exceptions d'outil WorkBench de suite : erreur de "
                                       f"configuration probable, arrêt avant toute nouvelle partie")
                else:
                    serie_outil[0] = 0
            if statut == INTERROMPUE:
                suffixe = f"interrompue-{ctx['horodatage']}"
                ligne.update(id=f"{t['id']}-{suffixe}", dossier=mettre_de_cote(sortie, t, suffixe))
            else:
                ligne["dossier"] = ranger(sortie, t, gardee)
            ligne.update(statut=statut, ok=gardee, finale=finale, exclue=motif is not None, motif_exclusion=motif)
            compta.ajouter(cout)
            if coupure:
                compta.arreter(coupure)
            if statut == ECHEC:
                serie[0] += 1
                if not finale:
                    attente.appendleft((partie, k + 1))
                if serie[0] >= SERIE_ECHECS_MAX:
                    compta.arreter(f"{serie[0]} échecs techniques de suite : panne probable, arrêt avant toute "
                                   f"nouvelle partie")
            elif statut != INTERROMPUE:
                serie[0] = 0
            pe.ecrire_json_atomique(sortie / "modeles_renvoyes.json", noms.json())
        reg.fin(ligne, evenement=evenement, id_evenement=t["id"])
        return ligne

    def travailleur():
        while True:
            with verrou:
                if compta.doit_arreter() or not attente:
                    return
                partie, k = attente.popleft()
            t = tentative(partie, k, ctx["vague"])
            reg.debut(t)
            wb = t["env"] == "WorkBench"  # constat E : au journal visible, ni partie ni modèle WorkBench
            qui = "une tentative WorkBench" if wb else t["id"]
            detail = f"début {t['id']} ({t['modele']}, tâche {t['tache']}, passage {t['passage']}, tentative {k})"
            noter(journal, f"début d'une tentative WorkBench (tentative {k})" if wb else detail, detail)
            debut = maintenant()
            try:
                r = executeur(t, ctx)
            except Exception as e:  # échec inattendu de l'exécuteur, peut-être après le jeu : jamais de reprise silencieuse
                r = resultat_exception(t, ctx, e)
            if r.get("non_lancee"):  # arrêt décidé pendant qu'elle attendait son tour : rien joué, rien compté
                reg.evenement({"evenement": "non_lancee", "id": t["id"], "horodatage": maintenant()})
                with verrou:
                    attente.appendleft((partie, k))
                noter(journal, f"non lancée : {qui} (arrêt décidé avant son départ ; elle reste en file)",
                      f"non lancée : {t['id']} (arrêt décidé avant son départ ; elle reste en file)")
                continue
            try:
                ligne = conclure(t, partie, k, r, debut)
            except Exception as e:  # erreur du lanceur lui-même : arrêt ; la tentative sera retrouvée à la reprise
                compta.arreter(f"erreur interne du lanceur après {qui} ({type(e).__name__}) : arrêt ; reprendre "
                               f"avec --reprendre")
                noter(journal, f"ERREUR INTERNE après {qui} : {type(e).__name__}",
                      f"ERREUR INTERNE après {t['id']} : {type(e).__name__}")
                return
            noter(journal, *lignes_de_fin(t, ligne, compta.cumul))

    with ThreadPoolExecutor(max_workers=concurrence) as ex:
        futs = [ex.submit(travailleur) for _ in range(concurrence)]
        try:
            for f in futs:
                f.result()
        except KeyboardInterrupt:
            interruption.set()
            compta.arreter("interruption par l'opérateur")
            journal.ecrire("interruption : aucune nouvelle partie n'est lancée ; les parties coupées seront rejouées")
            for f in futs:
                f.result()
    if compta.arret:  # revue « ultra » du 06/11, constat 1 : motif complet au journal complet seulement
        reste = f" ; tentatives non lancées : {len(attente)}"
        noter(journal, f"ARRÊT : {arret_visible(compta.arret)}{reste}", f"ARRÊT : {compta.arret}{reste}")


# =================================================================================================================
# 10. Le rapport de vague (2.5, points 1, 2, 3 et 6 seulement)
# =================================================================================================================
def post_traitement(sortie: Path, tau2=None, workbench=None) -> list:
    """Verdicts (banc/verdicts_csv.py) et typage (banc/typage.py) des parties gardées, comme au pilote : actions.csv et
    actions_typees.csv, lus par le moteur de rejeu et la relecture. Aucun résumé par verdict ni taux de réussite n'est
    calculé ici (2.5, « on ne regarde rien d'autre ») : le resume.* du pilote n'est pas écrit."""
    import verdicts_csv
    tau2, workbench = tau2 or TAU2, workbench or WORKBENCH
    dossier = sortie / "parties"
    dossier.mkdir(exist_ok=True)
    actions = sortie / "actions.csv"
    rc = verdicts_csv.main(["--dossier", str(dossier), "--tau2", str(tau2), "--workbench", str(workbench),
                            "--sortie", str(actions)])
    if rc != 0:
        raise ErreurPilote("verdicts_csv.py a échoué")
    return pe.typer_csv(actions, sortie / "actions_typees.csv", workbench)


def index_table_outils(chemin=TABLE_OUTILS) -> set:
    t = json.loads(Path(chemin).read_text(encoding="utf-8"))
    return {(o["banc"], o["outil"]) if o["banc"] == "workbench" else (o["banc"], o.get("domaine"), o["outil"])
            for o in t["outils"]}


def outils_figes(dossier=DOSSIER_OUTILS) -> dict:
    out = {}
    for env, nom in FICHIER_OUTILS.items():
        d = json.loads((Path(dossier) / f"{nom}.json").read_text(encoding="utf-8"))
        out[env] = {o["function"]["name"] for o in d["outils"]}
    return out


def instrument(actions: list, table=None, figes=None) -> dict:
    """Point 3 de 2.5, par environnement : écritures (au sens des suites du rejeu, 5.5 : kind « écriture », « inconnu »,
    ou « autre » typé comme une écriture), vérifiables (un verdict existe), sans verdict, actions « inconnu », typages
    « effet illisible », couverture de l'instrument (vérifiables / écritures, face au seuil de 0,95 ; ce n'est pas d),
    nouveaux noms d'outils. Seule l'existence d'un verdict est lue, jamais sa valeur."""
    import typage
    import verdicts
    table = index_table_outils() if table is None else table
    figes = outils_figes() if figes is None else figes
    neutres = {typage.LECTURE, typage.PREPARATION, typage.DOUTE}
    vide = {"actions": 0, "ecritures": 0, "verifiables": 0, "sans_verdict": 0, "inconnu": 0, "effet_illisible": 0}
    par = {e: dict(vide) for e in ENVS}
    hors_table = {e: set() for e in ENVS}
    hors_definitions = {e: set() for e in ENVS}
    for l in actions:
        e = pe.env_de_ligne(l)
        if e not in par:
            par[e], hors_table[e], hors_definitions[e] = dict(vide), set(), set()
        c = par[e]
        kind, typ, outil = l.get("kind"), l.get("type"), l.get("outil") or ""
        c["actions"] += 1
        if kind == verdicts.INCONNU:
            suite, verifiable = True, False
            c["inconnu"] += 1
        elif typ in neutres or kind in (verdicts.LECTURE, verdicts.DOUTE):
            suite, verifiable = False, False
        elif kind != verdicts.ECRITURE:
            suite, verifiable = True, False
        else:
            suite, verifiable = True, bool((l.get("verdict") or "").strip())
        if suite:
            c["ecritures"] += 1
            c["verifiables" if verifiable else "sans_verdict"] += 1
        if typ == typage.ILLISIBLE:
            c["effet_illisible"] += 1
        cle = (l.get("banc"), outil) if l.get("banc") == "workbench" else (l.get("banc"), l.get("domaine"), outil)
        if kind == verdicts.INCONNU or (kind in (verdicts.ECRITURE, verdicts.AUTRE) and cle not in table):
            hors_table[e].add(outil)
        nom = outil.replace(".", "_") if e == "WorkBench" else outil
        decouvrable = e == "banque" and nom.rsplit("_", 1)[-1].isdigit()  # outils bancaires révélés en cours de partie
        if e in figes and nom and nom not in figes[e] and not decouvrable:
            hors_definitions[e].add(outil)
    total = dict(vide)
    for c in par.values():
        for k in total:
            total[k] += c[k]
    for c in list(par.values()) + [total]:
        c["couverture"] = round(c["verifiables"] / c["ecritures"], 6) if c["ecritures"] else None
        c["sous_le_seuil"] = c["couverture"] is not None and c["couverture"] < SEUIL_COUVERTURE
    return {"par_environnement": par, "total": total, "seuil_couverture": SEUIL_COUVERTURE,
            "outils_hors_table": {e: sorted(v) for e, v in hors_table.items() if v},
            "outils_hors_definitions_figees": {e: sorted(v) for e, v in hors_definitions.items() if v}}


def _par_config(lignes: list) -> dict:
    d: dict = {}
    for l in lignes:
        d.setdefault((l["modele"], l["env"]), []).append(l)
    return d


def section_cout(plan: dict, lignes: list, restantes: dict, budget, depense_avant: float, joues=None,
                 taches=None) -> dict:
    """Point 1 : coût par partie de chaque configuration face à l'estimation, total, et total extrapolé (parties qui
    restent à jouer, au coût moyen mesuré dans cette vague), comparé au budget restant s'il est donné."""
    groupes = _par_config(lignes)
    par = []
    mesures = couts_mesures(lignes)  # même coût moyen que l'estimation de la vague 2 : sans les coûts majorés
    for d in plan["par_configuration"]:
        m, e = d["modele"], d["env"]
        ls = groupes.get((m, e), [])
        essais = [l for l in ls if l["statut"] != COUT_RETENU]  # un coût retenu compte en dollars, pas en tentatives
        jouees = len({l["partie"] for l in essais})
        cout = sum(l.get("cout_usd") or 0.0 for l in ls)  # dépense : coûts majorés compris
        moyen = mesures.get(m, {}).get(e)
        base = d["cout_moyen_usd"]
        par.append({"modele": m, "env": e, "parties_prevues": d["parties"], "parties_jouees": jouees,
                    "tentatives": len(essais), "cout_usd": round(cout, 6), "estimation_usd": d["estimation_usd"],
                    "cout_moyen_usd": None if moyen is None else round(moyen, 6), "cout_moyen_estime_usd": round(base, 6),
                    "ecart_pct": None if moyen is None or not base else round((moyen / base - 1) * 100, 1)})
    depense = sum(l.get("cout_usd") or 0.0 for l in lignes)
    reste, sans_mesure = 0.0, []
    for (m, e), n in sorted(restantes.items()):
        if not n:
            continue
        moyen = mesures.get(m, {}).get(e)
        if moyen is None:
            moyen = plan["couts_moyens"].get(m, {}).get(e)
            sans_mesure.append(f"{m} / {e}")
        reste += n * (moyen or 0.0)
    extrap = {"parties_restantes": sum(restantes.values()), "estimation_restante_usd": round(reste, 4),
              "depense_vagues_precedentes_usd": round(depense_avant, 4),
              "total_extrapole_usd": round(depense_avant + depense + reste, 4),
              "base": "coût moyen par partie mesuré dans cette vague",
              "configurations_sans_mesure": sans_mesure, "budget_restant_usd": budget}
    if budget is not None:
        extrap["estimation_restante_tient_dans_le_budget"] = reste <= budget + EPS
        # Cible de C9 (Otsoa, QCM, 06/11) : le plafond entier, 1,25 x l'estimation restante, tient dans le budget restant.
        extrap["plafond_refait_tient_dans_le_budget"] = FACTEUR_PLAFOND[2] * reste <= budget + EPS
        if plan["vague"] == 1 and joues is not None and taches is not None:
            couts = {m: dict(plan["couts_moyens"].get(m, {}), **mesures.get(m, {})) for m in MODELES}
            try:
                c, red, total = facteur_reduction(PASSAGES, couts, taches, joues, budget)
                extrap["reduction_previsible"] = {"centiemes": c, "passages": red, "total_refait_usd": round(total, 4)}
            except ErreurPilote as ex:
                extrap["reduction_previsible"] = {"impossible": str(ex)}
    return {"par_configuration": par, "depense_usd": round(depense, 6), "estimation_usd": round(plan["estimation_usd"], 6),
            "plafond_usd": plan.get("plafond_usd"), "seuil_arret_usd": plan.get("seuil_arret_usd"),
            "extrapolation": extrap}


def section_deroulement(plan_parties: list, lignes: list, en_attente: list) -> dict:
    """Point 2 : tentatives arrêtées (par cause), en échec technique, relancées, exclues (par motif), interrompues ;
    parties non jouées ; état des usages. Les exceptions d'outil WorkBench sont des erreurs de l'agent : elles ne sont
    comptées que par environnement, jamais par configuration (revue du 06/11, constat 5). Pour qu'on ne les retrouve pas
    par différence, les comptes par configuration ne donnent ni les parties gardées ni les terminées (au total
    seulement)."""
    essais = [l for l in lignes if l["statut"] != COUT_RETENU]
    groupes = _par_config(essais)
    prevues = compter(plan_parties)
    attente = compter([x for x, _ in en_attente])
    par, total = [], {}
    for (m, e), n in sorted(prevues.items(), key=lambda kv: (MODELES.index(kv[0][0]), ENVS.index(kv[0][1]))):
        ls = groupes.get((m, e), [])
        arretees, exclues, usages = {}, {}, {}
        for l in ls:
            outil = l.get("arret") == ARRET_EXCEPTION_OUTIL
            if l["statut"] == ARRETEE and not outil:
                arretees[l.get("arret") or "?"] = arretees.get(l.get("arret") or "?", 0) + 1
            if l.get("exclue") and not outil:
                exclues[l["motif_exclusion"]] = exclues.get(l["motif_exclusion"], 0) + 1
            usages[l.get("usage") or "?"] = usages.get(l.get("usage") or "?", 0) + 1
        d = {"modele": m, "env": e, "parties_prevues": n, "parties_jouees": len({l["partie"] for l in ls}),
             "tentatives": len(ls), "arretees": arretees,
             "echecs_techniques": sum(1 for l in ls if l["statut"] == ECHEC),
             "relancees": sum(1 for l in ls if l["statut"] == ECHEC and not l.get("finale")),
             "interrompues": sum(1 for l in ls if l["statut"] == INTERROMPUE), "exclues": exclues,
             "non_jouees": attente.get((m, e), 0), "usages": usages}
        par.append(d)
        for k, v in d.items():
            if isinstance(v, int) and k not in ("modele", "env"):
                total[k] = total.get(k, 0) + v
            elif isinstance(v, dict):
                for kk, vv in v.items():
                    total.setdefault(k, {})[kk] = total.setdefault(k, {}).get(kk, 0) + vv
    total["gardees"] = sum(1 for l in essais if l.get("ok"))
    total["terminees"] = sum(1 for l in essais if l["statut"] == TERMINEE)
    outils: dict = {}
    for l in essais:
        if l.get("arret") == ARRET_EXCEPTION_OUTIL:
            outils[l["env"]] = outils.get(l["env"], 0) + 1
    retenus = [l for l in lignes if l["statut"] == COUT_RETENU]
    return {"par_configuration": par, "total": total, "exceptions_outil_par_environnement": outils,
            "couts_retenus": {"lignes": len(retenus), "usd": round(sum(l.get("cout_usd") or 0.0 for l in retenus), 6)},
            "couts_inconnus_en_suspens": couts_inconnus_en_suspens(lignes)}


def section_noms(noms: Noms, lignes: list) -> dict:
    """Point 6 : nom de modèle renvoyé par l'API, qui doit rester le même. Les tentatives exclues pour ce motif sont
    toutes déclarées, avec leur rejeu éventuel."""
    exclues = [l for l in lignes if l["statut"] == EXCLUE_NOM]
    finies = {l["partie"] for l in lignes if l.get("finale")}
    return dict(noms.json(), parties_exclues=sorted(l["id"] for l in exclues),
                parties_a_rejouer=sorted({l["partie"] for l in exclues if l["partie"] not in finies}),
                change=bool(noms.changements))


def rapport_vague(plan: dict, plan_parties: list, lignes: list, actions, noms: Noms, en_attente: list,
                  restantes: dict, budget=None, depense_avant: float = 0.0, joues=None, taches=None,
                  erreur_post=None) -> dict:
    return {"vague": plan["vague"], "mode": plan["mode"], "horodatage": maintenant(), "limite": plan.get("limite"),
            "arret": plan.get("arret"),
            "reduction_des_passages": plan.get("reduction"),
            "1_cout": section_cout(plan, lignes, restantes, budget, depense_avant, joues, taches),
            "2_deroulement": section_deroulement(plan_parties, lignes, en_attente),
            "3_instrument": instrument(actions) if actions is not None else {"indisponible": erreur_post},
            "6_nom_de_modele": section_noms(noms, lignes),
            "non_couvert": "points 4 et 5 de 2.5 (relecture à l'aveugle, tâches défectueuses) : hors du lanceur ; "
                           "rien d'autre n'est regardé (2.5)"}


def _usd(x) -> str:
    return "—" if x is None else f"{x:.4f}"


def texte_rapport(r: dict) -> str:
    c, d, i, n = r["1_cout"], r["2_deroulement"], r["3_instrument"], r["6_nom_de_modele"]
    out = [f"Rapport de la vague {r['vague']} ({r['mode']})" + (f", essai limité à {r['limite']} parties"
                                                               if r.get("limite") else ""),
           "Points 1, 2, 3 et 6 de PLAN_EXPERIENCE.md, 2.5. Rien d'autre n'est regardé.", ""]
    if r.get("arret"):
        out += [f"ARRÊT : {r['arret']}", ""]
    if r.get("reduction_des_passages"):
        red = r["reduction_des_passages"]
        out += [f"Réduction des passages (règle C9) : facteur {red['centiemes'] / 100:.2f}, passages {red['passages']}",
                ""]
    out += ["1. Coût par configuration, face à l'estimation",
            f"{'modèle':<18} {'env':<10} {'prévues':>7} {'jouées':>6} {'tent.':>5} {'coût $':>10} {'estim. $':>9} "
            f"{'moyen $':>9} {'estimé $':>9} {'écart':>7}"]
    for x in c["par_configuration"]:
        ecart = "—" if x["ecart_pct"] is None else f"{x['ecart_pct']:+.1f} %"
        out.append(f"{x['modele']:<18} {x['env']:<10} {x['parties_prevues']:>7} {x['parties_jouees']:>6} "
                   f"{x['tentatives']:>5} {x['cout_usd']:>10.4f} {x['estimation_usd']:>9.4f} {_usd(x['cout_moyen_usd']):>9} "
                   f"{_usd(x['cout_moyen_estime_usd']):>9} {ecart:>7}")
    e = c["extrapolation"]
    out += [f"Dépensé dans la vague : {c['depense_usd']:.4f} USD ; estimation de la vague : {c['estimation_usd']:.4f} USD ; "
            f"plafond : {_usd(c['plafond_usd'])} USD, arrêt à {_usd(c['seuil_arret_usd'])} USD",
            f"Reste à jouer : {e['parties_restantes']} parties, estimées à {e['estimation_restante_usd']:.4f} USD "
            f"({e['base']}) ; total extrapolé de l'expérience : {e['total_extrapole_usd']:.4f} USD "
            f"(dont vagues précédentes : {e['depense_vagues_precedentes_usd']:.4f} USD)"]
    if e["configurations_sans_mesure"]:
        out.append("  sans mesure dans cette vague (coût de l'estimation repris) : " + ", ".join(e["configurations_sans_mesure"]))
    if e.get("budget_restant_usd") is not None:
        out.append(f"Budget restant donné : {e['budget_restant_usd']:.2f} USD ; l'estimation restante "
                   f"{'y tient' if e['estimation_restante_tient_dans_le_budget'] else 'le DÉPASSE'} ; 1,25 fois "
                   f"l'estimation restante (cible de C9) "
                   f"{'y tient' if e['plafond_refait_tient_dans_le_budget'] else 'le DÉPASSE : passages réduits'}")
        rp = e.get("reduction_previsible")
        if rp:
            out.append("  réduction prévisible (C9) : " + (rp["impossible"] if "impossible" in rp else
                       f"facteur {rp['centiemes'] / 100:.2f}, total refait {rp['total_refait_usd']:.4f} USD"))
    out += ["", "2. Déroulement",
            f"{'modèle':<18} {'env':<10} {'prévues':>7} {'jouées':>6} {'tent.':>5} {'échecs':>6} "
            f"{'relancées':>9} {'non jouées':>10}  arrêtées / exclues / usages"]
    for x in d["par_configuration"]:
        out.append(f"{x['modele']:<18} {x['env']:<10} {x['parties_prevues']:>7} {x['parties_jouees']:>6} "
                   f"{x['tentatives']:>5} {x['echecs_techniques']:>6} {x['relancees']:>9} {x['non_jouees']:>10}  "
                   f"{x['arretees'] or '-'} / {x['exclues'] or '-'} / {x['usages']}")
    t = d["total"]
    out.append(f"Total : {t.get('tentatives', 0)} tentatives, {t.get('gardees', 0)} gardées, {t.get('terminees', 0)} "
               f"terminées, {t.get('echecs_techniques', 0)} échecs techniques, {t.get('interrompues', 0)} interrompues, "
               f"{t.get('non_jouees', 0)} parties non jouées ; arrêtées : {t.get('arretees') or '-'} ; "
               f"exclues : {t.get('exclues') or '-'} ; usages : {t.get('usages') or '-'}")
    out.append(f"Exceptions d'outil (erreurs de l'agent, par environnement seulement) : "
               f"{d['exceptions_outil_par_environnement'] or 'aucune'}")
    if d["couts_retenus"]["lignes"]:
        out.append(f"Coûts retenus par l'opérateur : {d['couts_retenus']['lignes']} ligne(s), "
                   f"{d['couts_retenus']['usd']:.4f} USD")
    if d["couts_inconnus_en_suspens"]:
        out.append(f"COÛTS INCONNUS À CHIFFRER avant de reprendre (--cout-retenu) : {d['couts_inconnus_en_suspens']}")
    out += ["", "3. Instrument (seule l'existence d'un verdict est lue)"]
    if "indisponible" in i:
        out.append(f"indisponible : {i['indisponible']}")
    else:
        for env, x in list(i["par_environnement"].items()) + [("total", i["total"])]:
            cv_ = "—" if x["couverture"] is None else f"{x['couverture']:.4f}"
            out.append(f"{env:<10} actions {x['actions']} ; écritures {x['ecritures']} ; vérifiables {x['verifiables']} ; "
                       f"sans verdict {x['sans_verdict']} ; « inconnu » {x['inconnu']} ; « effet illisible » "
                       f"{x['effet_illisible']} ; couverture {cv_}" + (" SOUS LE SEUIL DE 0,95" if x["sous_le_seuil"] else ""))
        out.append(f"Noms d'outils absents de la table des outils : {i['outils_hors_table'] or 'aucun'}")
        out.append(f"Noms d'outils absents des définitions figées : {i['outils_hors_definitions_figees'] or 'aucun'}")
    out += ["", "6. Nom de modèle renvoyé par l'API",
            f"Référence ({n['source']}) : {n['reference'] or 'aucune'}", f"Observés (appels) : {n['observes'] or 'aucun'}",
            f"Appels sans nom : {n['appels_sans_nom']}",
            ("CHANGEMENT : " + "; ".join(f"{x['modele']} : {x['recu']} au lieu de {x['attendu']} ({x['tentative']})"
                                         for x in n["changements"])) if n["change"] else "Aucun changement.",
            f"Parties exclues pour ce motif : {n['parties_exclues'] or 'aucune'}", ""]
    return "\n".join(out)


# =================================================================================================================
# Vague 1 vue de la vague 2 ; reprise
# =================================================================================================================
def _lire_json(chemin: Path, quoi: str):
    try:
        return json.loads(Path(chemin).read_text(encoding="utf-8"))
    except OSError:
        raise ErreurPilote(f"{quoi} introuvable : {chemin}")
    except ValueError:
        raise ErreurPilote(f"{quoi} illisible : {chemin}")


def charger_vague(dossier) -> dict:
    """plan_de_jeu.json, cout.json et modeles_renvoyes.json d'un dossier de vague terminé."""
    d = Path(dossier)
    plan = _lire_json(d / "plan_de_jeu.json", "plan de jeu")
    cout = _lire_json(d / "cout.json", "cout.json")
    noms = _lire_json(d / "modeles_renvoyes.json", "noms de modèle") if (d / "modeles_renvoyes.json").is_file() else {}
    return {"dossier": d, "plan": plan, "cout": cout, "lignes": list(cout.get("parties") or []), "noms": noms}


def couts_mesures(lignes: list) -> dict:
    """{modèle: {env: coût moyen par partie}} : coût de toutes les tentatives de la configuration (échecs,
    interruptions et montants retenus compris), divisé par le nombre de parties jouées. Base de l'estimation de la
    vague 2, de C9 et du point 1 du rapport. Une tentative au coût majoré (majorant τ-bench ou WorkBench, quand l'usage
    manque) compte dans la dépense mais pas ici : le majorant vaut des dizaines de fois le coût réel (décision du
    06/11, question 3 de CHOIX_LANCEUR.md). Une partie dont toutes les tentatives sont majorées n'est pas comptée ; une
    configuration sans autre mesure reste sans mesure, et la vague 2 est alors refusée (detail_estimation)."""
    tot, parties = {}, {}
    for l in lignes:
        if l.get("cout_majore") and not l.get("cout_retenu_pour"):
            continue  # majorant ; un montant retenu par l'opérateur (--cout-retenu) est une estimation, gardée
        k = (l["modele"], l["env"])
        tot[k] = tot.get(k, 0.0) + (l.get("cout_usd") or 0.0)
        parties.setdefault(k, set()).add(l["partie"])
    out: dict = {}
    for (m, e), s in parties.items():
        out.setdefault(m, {})[e] = tot[(m, e)] / len(s)
    return out


def joues_par_passage(lignes: list) -> dict:
    """{(modèle, env): {passage: parties finies}}."""
    vus, out = set(), {}
    for l in lignes:
        if l.get("finale") and l["partie"] not in vus:
            vus.add(l["partie"])
            d = out.setdefault((l["modele"], l["env"]), {})
            d[int(l["passage"])] = d.get(int(l["passage"]), 0) + 1
    return out


def charger_reprise(dossier) -> dict:
    d = Path(dossier)
    if not d.is_dir():
        raise ErreurPilote(f"reprise : dossier introuvable : {d}")
    plan = _lire_json(d / "plan_de_jeu.json", "plan de jeu")
    lignes, orphelines = lire_tentatives(d / "tentatives.jsonl")
    cout = _lire_json(d / "cout.json", "cout.json") if (d / "cout.json").is_file() else {}
    noms = _lire_json(d / "modeles_renvoyes.json", "noms de modèle") if (d / "modeles_renvoyes.json").is_file() else None
    return {"dossier": d, "plan": plan, "lignes": lignes, "orphelines": orphelines, "cout": cout, "noms": noms}


# =================================================================================================================
# Un seul lancement par vague (revue du 06/11, constats 1 et 3)
# =================================================================================================================
def pid_vivant(pid) -> bool:
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:  # processus d'un autre utilisateur : vivant
        return True
    except OSError:
        return False
    return True


def prendre_verrou(dossier) -> dict:
    """Verrou exclusif du dossier de vague : fichier `verrou` créé avec O_CREAT | O_EXCL, qui porte le PID, la machine
    et l'heure. Refus tant qu'il appartient à un processus vivant (ou à une autre machine, où le PID ne se vérifie
    pas) : un second lancement ou une seconde reprise du même dossier ne joue rien. Un verrou orphelin (processus mort)
    est signalé (clé « orphelin » du résultat), mis de côté, puis repris. Vérification et reprise se font sous un flock
    du dossier, libéré par le système si le processus meurt : deux lanceurs ne reprennent pas le même orphelin."""
    dossier = Path(dossier)
    if not dossier.is_dir():
        raise ErreurPilote(f"dossier de vague introuvable : {dossier}")
    chemin = dossier / NOM_VERROU
    moi = {"pid": os.getpid(), "machine": socket.gethostname(), "debut": maintenant()}
    orphelin = None
    fd_dossier = os.open(dossier, os.O_RDONLY)
    try:
        fcntl.flock(fd_dossier, fcntl.LOCK_EX)
        if chemin.exists():
            try:
                ancien = json.loads(chemin.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                ancien = {}
            ancien = ancien if isinstance(ancien, dict) else {}
            pid = ancien.get("pid")
            if ancien.get("machine") not in (None, moi["machine"]):
                raise ErreurPilote(f"dossier de vague verrouillé depuis une autre machine ({ancien.get('machine')}, "
                                   f"processus {pid}) : refus")
            if pid_vivant(pid):
                raise ErreurPilote(f"dossier de vague verrouillé par le processus {pid}, toujours vivant (depuis "
                                   f"{ancien.get('debut')}) : un seul lancement à la fois sur un dossier de vague")
            orphelin = dict(ancien, mis_de_cote=f"{NOM_VERROU}.orphelin-{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
            chemin.rename(dossier / orphelin["mis_de_cote"])
        fd = os.open(chemin, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(moi, ensure_ascii=False) + "\n")
    finally:
        fcntl.flock(fd_dossier, fcntl.LOCK_UN)
        os.close(fd_dossier)
    return {"chemin": chemin, "pid": moi["pid"], "orphelin": orphelin}


def liberer_verrou(verrou) -> None:
    """Retire le verrou du dossier de vague s'il est toujours le nôtre."""
    if not verrou:
        return
    try:
        if json.loads(verrou["chemin"].read_text(encoding="utf-8")).get("pid") == verrou["pid"]:
            verrou["chemin"].unlink()
    except (OSError, ValueError, AttributeError):
        pass


def dossiers_reels(racine_vague) -> list:
    """Dossiers réels (sans -blanc) d'une vague sous la racine des sorties."""
    racine_vague = Path(racine_vague)
    if not racine_vague.is_dir():
        return []
    return sorted(d.name for d in racine_vague.iterdir() if d.is_dir() and not d.name.endswith("-blanc"))


def marquer_vague1(dossier_v1, sortie_v2: Path, mode: str) -> None:
    """Marqueur vague2.json dans le dossier de la vague 1 : la vague 2 a commencé, la vague 1 ne se reprend plus (ses
    parties restantes sont celles de la vague 2)."""
    chemin = Path(dossier_v1) / NOM_MARQUEUR_VAGUE2
    try:
        d = json.loads(chemin.read_text(encoding="utf-8")) if chemin.is_file() else {}
    except (OSError, ValueError):
        d = {}
    d = d if isinstance(d, dict) else {}
    d.setdefault("vagues2", []).append({"dossier": str(Path(sortie_v2).resolve()), "horodatage": maintenant(),
                                        "mode": mode})
    pe.ecrire_json_atomique(chemin, d)


def mode_de(a) -> str:
    return "réel" if a.reel else "à blanc"


def mode_de_la_vague(dossier) -> str | None:
    """Mode noté au plan de jeu d'un dossier de vague (ErreurPilote s'il est illisible)."""
    return _lire_json(Path(dossier) / "plan_de_jeu.json", "plan de jeu").get("mode")


def lire_couts_retenus(valeurs) -> dict:
    """{identifiant de tentative: USD} des options --cout-retenu ID=USD."""
    out = {}
    for v in valeurs or []:
        ident, sep, montant = str(v).rpartition("=")
        try:
            usd = float(montant)
        except ValueError:
            usd = float("nan")
        if not sep or not ident or not math.isfinite(usd) or usd < 0:
            raise ErreurPilote(f"--cout-retenu {v!r} : forme ID=USD attendue, montant positif ou nul")
        out[ident] = usd
    return out


def environnement_enfants(base, cle=None) -> dict:
    """Environnement des bancs (pilote_etape1.env_enfant), plus PYTHON_DOTENV_DISABLED=1 : python-dotenv (τ-bench et
    WorkBench) ne charge alors aucun `.env`, où qu'il soit au-dessus du banc (revue du 06/11, constat 12)."""
    env = pe.env_enfant(base, cle)
    env["PYTHON_DOTENV_DISABLED"] = "1"
    return env


# =================================================================================================================
# Ligne de commande
# =================================================================================================================
def analyser(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--vague", type=int, choices=(1, 2), required=True, help="vague à jouer")
    p.add_argument("--reel", action="store_true", help="appels réels (sinon : essai à blanc, sans clé)")
    p.add_argument("--plafond-usd", type=float, default=None, help="plafond de dépense de la vague (obligatoire)")
    p.add_argument("--accord-otsoa-usd", type=float, default=None,
                   help="montant accordé par Otsoa pour la vague (obligatoire) : tout plafond supérieur est refusé")
    p.add_argument("--budget-restant-usd", type=float, default=None,
                   help="budget restant (vague 2 : obligatoire, borne le plafond et décide de la réduction des passages ; "
                        "vague 1 : facultatif, sert seulement au rapport)")
    p.add_argument("--vague1", default=None, help="dossier de sortie de la vague 1 (obligatoire pour la vague 2)")
    p.add_argument("--graine", type=int, default=None,
                   help="vague 1 : graine de l'ordre de jeu (sinon tirée par secrets.randbits(64) et notée)")
    p.add_argument("--concurrence", type=int, choices=tuple(range(1, CONCURRENCE_MAX + 1)), default=CONCURRENCE_DEFAUT,
                   help=f"parties simultanées (défaut {CONCURRENCE_DEFAUT}, au plus {CONCURRENCE_MAX})")
    p.add_argument("--limite", type=int, default=None, help="essai à blanc seulement : ne jouer que les N premières parties")
    p.add_argument("--reprendre", default=None, help="dossier d'une vague interrompue, à poursuivre")
    p.add_argument("--cout-retenu", action="append", default=[], metavar="ID=USD",
                   help="avec --reprendre : montant retenu (lu dans la console) pour une tentative au coût inconnu ; "
                        "obligatoire pour chacune avant de reprendre")
    p.add_argument("--apercu", action="store_true", help="montrer le plan, l'estimation et le plafond permis, sans rien "
                                                          "lancer ni écrire")
    p.add_argument("--reserve", default=str(RESERVE), help="réserve des tâches (réel : banc/tirage/reserve.json seulement)")
    p.add_argument("--sortie-racine", default=None,
                   help="racine des sorties (défaut : experience/ ; en réel, experience/ seulement)")
    return p.parse_args(argv)


def _positif(x, nom):
    if x is not None and (not math.isfinite(x) or x <= 0):
        raise ErreurPilote(f"{nom} invalide : un nombre positif est attendu")


def preparer(a) -> dict:
    """Tout ce qui précède le jeu, sans rien écrire ni lire de clé : réserve, plan, vague, estimation, plafond, file."""
    vague, reel, mode = a.vague, a.reel, "réel" if a.reel else "à blanc"
    if not a.apercu:
        if a.plafond_usd is None:
            raise ErreurPilote("--plafond-usd est obligatoire (plafond de la vague)")
        if a.accord_otsoa_usd is None:
            raise ErreurPilote("--accord-otsoa-usd est obligatoire (montant accordé par Otsoa pour la vague)")
    _positif(a.budget_restant_usd, "--budget-restant-usd")
    if a.limite is not None:
        if reel:
            raise ErreurPilote("--limite est réservé à l'essai à blanc : une vague réelle joue toutes ses parties")
        if a.limite < 1:
            raise ErreurPilote("--limite : un entier positif est attendu")
    if a.graine is not None and a.graine < 0:
        raise ErreurPilote("--graine : un entier positif ou nul est attendu")
    if reel and Path(a.reserve).resolve() != RESERVE.resolve():
        raise ErreurPilote(f"mode réel : la réserve est {RESERVE} (toute la réserve, 2.3)")
    couts_retenus = lire_couts_retenus(a.cout_retenu)
    if couts_retenus and not a.reprendre:
        raise ErreurPilote("--cout-retenu ne sert qu'avec --reprendre")
    racine = Path(a.sortie_racine) if a.sortie_racine else SORTIE_RACINE
    if reel and racine.resolve() != SORTIE_RACINE.resolve():
        # Contre-vérification, constat A : une autre racine ouvrirait un second dossier réel, donc un second plafond.
        raise ErreurPilote(f"mode réel : les sorties vont dans {SORTIE_RACINE} (--sortie-racine refusé : {racine})")
    if reel and not a.reprendre and not a.apercu:
        existants = dossiers_reels(racine / f"vague{vague}")
        if existants:  # constat 1 : relancer ouvrirait un second plafond (et une autre graine) pour la même vague
            raise ErreurPilote(f"la vague {vague} a déjà un dossier réel ({racine / f'vague{vague}' / existants[-1]}) : "
                               f"la poursuivre avec --reprendre <dossier>, jamais par un nouveau lancement")
    reserve = charger_reserve(a.reserve)
    verifier_taches_existent(reserve)
    taches = {e: len(v) for e, v in reserve.items()}
    sha_reserve = empreinte_json(reserve)
    rep = charger_reprise(a.reprendre) if a.reprendre else None
    if rep:
        if rep["plan"].get("vague") != vague:
            raise ErreurPilote(f"reprise : le dossier est celui de la vague {rep['plan'].get('vague')}, pas de la vague {vague}")
        if rep["plan"].get("mode") != mode:
            raise ErreurPilote(f"reprise : le dossier a été joué en mode {rep['plan'].get('mode')}, pas {mode}")
        if rep["plan"].get("reserve", {}).get("sha256") != sha_reserve:
            raise ErreurPilote("reprise : la réserve a changé depuis le début de la vague")
        if vague == 1 and (rep["dossier"] / NOM_MARQUEUR_VAGUE2).is_file():  # constat 3
            raise ErreurPilote(f"reprise de la vague 1 refusée : la vague 2 a commencé ({NOM_MARQUEUR_VAGUE2} dans "
                               f"{rep['dossier']}) ; les parties restantes de la vague 1 sont jouées par la vague 2")
        vivants = enfants_vivants(rep["dossier"])
        if vivants:  # revue « ultra » du 06/11, constat 3 (PID seulement : un identifiant WorkBench casserait l'aveugle)
            raise ErreurPilote(f"reprise refusée : {len(vivants)} partie(s) lancée(s) avant l'arrêt tourne(nt) encore et "
                               f"dépense(nt) toujours (processus {', '.join(map(str, vivants))}) ; attendre leur fin ou "
                               f"les arrêter (kill PID, après avoir vérifié avec ps -p PID que c'est bien une partie du "
                               f"banc), puis reprendre")
        en_suspens = couts_inconnus_en_suspens(rep["lignes"]) + orphelines_illisibles(rep["dossier"], rep["orphelines"])
        etrangers = sorted(set(couts_retenus) - set(en_suspens))
        if etrangers:
            raise ErreurPilote(f"--cout-retenu : aucun coût inconnu à chiffrer pour {etrangers} dans cette vague")
        manquants = [i for i in en_suspens if i not in couts_retenus]
        if manquants:  # constats 10, 11 et 13 : un coût inconnu n'est jamais oublié à la reprise
            raise ErreurPilote(f"reprise refusée : coût inconnu pour {manquants} ; le chiffrer (console), puis reprendre "
                               f"avec --cout-retenu ID=USD pour chacune")
    budget = a.budget_restant_usd
    reduction, depense_avant, lignes_avant, v1 = None, 0.0, [], None
    if vague == 1:
        if a.vague1:
            raise ErreurPilote("--vague1 ne sert qu'à la vague 2")
        if rep:
            graine, source_graine = int(rep["plan"]["graine"]), "plan de jeu de la vague (reprise)"
            if a.graine is not None and a.graine != graine:
                raise ErreurPilote("reprise : --graine diffère de la graine de la vague")
        elif a.graine is not None:
            graine, source_graine = a.graine, "option --graine"
        elif a.apercu:
            graine, source_graine = 0, "non tirée (aperçu)"
        else:
            graine, source_graine = secrets.randbits(64), "tirée par secrets.randbits(64)"
        passages = PASSAGES
        parties_plan = construire_parties(reserve, graine, passages)
        parties = parties_vague1(parties_plan)
        couts, source_couts = COUT_PILOTE, SOURCE_COUT_PILOTE
        noms = Noms(source="première observation de la vague 1")
    else:
        if not a.vague1:
            raise ErreurPilote("vague 2 : --vague1 (dossier de sortie de la vague 1) est obligatoire")
        if a.graine is not None:
            raise ErreurPilote("vague 2 : la graine est celle de la vague 1 (pas de --graine)")
        v1 = charger_vague(a.vague1)
        if v1["plan"].get("vague") != 1:
            raise ErreurPilote(f"--vague1 : {v1['dossier']} n'est pas un dossier de vague 1")
        if not v1["cout"].get("fin"):
            raise ErreurPilote(f"--vague1 : la vague 1 n'est pas finie ({v1['dossier']}) : la reprendre d'abord")
        if reel and v1["plan"].get("mode") != "réel":
            raise ErreurPilote("vague 2 réelle : la vague 1 donnée a été jouée à blanc")
        if v1["plan"].get("reserve", {}).get("sha256") != sha_reserve:
            raise ErreurPilote("vague 2 : la réserve diffère de celle de la vague 1")
        inconnus_v1 = couts_inconnus_en_suspens(v1["lignes"])
        if inconnus_v1:
            raise ErreurPilote(f"vague 2 refusée : la vague 1 a des coûts inconnus non chiffrés ({inconnus_v1}) ; "
                               f"reprendre d'abord la vague 1 avec --cout-retenu ID=USD")
        if not rep:
            # Contre-vérification, constat H : une tentative commencée sans fin (arrêt brutal, erreur interne) n'a pas son
            # coût dans cout.json ; la reprise de la vague 1 la retrouve, la compte et la rejoue.
            _, orphelines_v1 = lire_tentatives(v1["dossier"] / "tentatives.jsonl")
            if orphelines_v1:
                raise ErreurPilote(f"vague 2 refusée : la vague 1 a des tentatives commencées sans fin "
                                   f"({[o.get('id') for o in orphelines_v1]}) ; reprendre d'abord la vague 1 "
                                   f"(avec --cout-retenu ID=USD si leur usage est illisible)")
        dossier_v1 = str(Path(a.vague1).resolve())
        if rep and rep["plan"].get("vague1") != dossier_v1:
            raise ErreurPilote("reprise : --vague1 diffère du dossier de vague 1 noté au début de la vague 2")
        graine, source_graine = int(v1["plan"]["graine"]), f"vague 1 ({dossier_v1})"
        if reel:
            couts, source_couts = couts_mesures(v1["lignes"]), f"coûts mesurés à la vague 1 ({dossier_v1})"
        else:  # les coûts de la vague 1 à blanc sont factices : plafond et seuil seraient sans rapport avec le réel
            couts = COUT_PILOTE
            source_couts = (f"{SOURCE_COUTS_BLANC} : {SOURCE_COUT_PILOTE}, au lieu des coûts factices de la vague 1 "
                            f"à blanc ({dossier_v1})")
        joues = joues_par_passage(v1["lignes"])
        if rep:
            budget_note = rep["plan"].get("budget_restant_usd")
            if budget_note is None:
                raise ErreurPilote("reprise : budget restant absent du plan de jeu de la vague 2")
            if budget is not None and abs(budget - budget_note) > EPS:
                raise ErreurPilote(f"reprise : le budget restant de la vague 2 est celui noté au début "
                                   f"({budget_note:.2f} USD)")
            budget = budget_note
            passages = {m: {e: int(n) for e, n in d.items()} for m, d in rep["plan"]["passages"].items()}
            reduction = rep["plan"].get("reduction")
        elif budget is not None:
            c, passages, total = facteur_reduction(PASSAGES, couts, taches, joues, budget)
            reduction = None if c == 100 else {"centiemes": c, "passages": passages, "total_refait_usd": round(total, 6),
                                               "plafond_refait_usd": round(FACTEUR_PLAFOND[2] * total, 6),
                                               "budget_restant_usd": budget,
                                               "regle": "1,25 x le total réduit tient dans le budget restant "
                                                        "(Otsoa, QCM, 06/11)"}
        elif a.apercu:
            passages = PASSAGES
        else:
            raise ErreurPilote("vague 2 : --budget-restant-usd est obligatoire")
        parties_plan = construire_parties(reserve, graine, passages)
        finales_v1 = {l["partie"] for l in v1["lignes"] if l.get("finale")}
        parties = [x for x in parties_plan if x["id"] not in finales_v1]
        lignes_avant = list(v1["lignes"])
        depense_avant = sum(l.get("cout_usd") or 0.0 for l in v1["lignes"])
        noms = Noms.depuis_json(v1["noms"], source=f"vague 1 ({dossier_v1})")
        noms.observes, noms.changements, noms.absents = {}, [], 0
    detail = detail_estimation(parties, couts)
    estim = sum(d["parties"] * d["cout_moyen_usd"] for d in detail)
    pmax = plafond_permis(vague, estim, budget if vague == 2 else None)
    if not a.apercu:
        verifier_plafond(vague, a.plafond_usd, a.accord_otsoa_usd, estim, budget if vague == 2 else None)
    ordre_sha = empreinte_ordre(parties)
    lignes_vague = []
    if rep:
        if rep["plan"].get("ordre_sha256") != ordre_sha:
            raise ErreurPilote("reprise : le plan de jeu recalculé ne correspond plus à celui de la vague")
        lignes_vague = rep["lignes"]
        if rep["noms"] is not None:
            noms = Noms.depuis_json(rep["noms"])
    file = file_d_attente(parties, lignes_avant + lignes_vague)
    if a.limite:
        file = file[:a.limite]
    plan = {"vague": vague, "mode": mode, "graine": graine, "graine_source": source_graine,
            "reserve": {"chemin": str(Path(a.reserve).resolve()), "sha256": sha_reserve, "taches": taches},
            "passages_decides": PASSAGES, "passages": passages, "reduction": reduction,
            "part_vague1": "10 % des parties de chaque configuration, arrondi au supérieur",
            "couts_moyens": couts, "source_couts": source_couts, "parties_vague": len(parties),
            "par_configuration": detail, "estimation_usd": round(estim, 6), "facteur_plafond": FACTEUR_PLAFOND[vague],
            "plafond_permis_usd": round(pmax, 6), "plafond_usd": a.plafond_usd, "accord_otsoa_usd": a.accord_otsoa_usd,
            "budget_restant_usd": budget,
            "seuil_arret_usd": None if a.plafond_usd is None else seuil_arret(vague, a.plafond_usd)[0],
            "regle_arret": seuil_arret(vague, 1.0)[1], "vague1": str(Path(a.vague1).resolve()) if a.vague1 else None,
            "ordre_sha256": ordre_sha, "limite": a.limite, "concurrence": a.concurrence,
            "delai_partie_s": DELAI_PARTIE_S, "max_tours": pe.MAX_PAS_REEL, "cache": True, "client_simule": MODELE_USER,
            "modeles": list(MODELES), "tentatives_max": TENTATIVES_MAX, "exclusions_nom_max": EXCLUSIONS_NOM_MAX,
            "serie_echecs_max": SERIE_ECHECS_MAX, "serie_exceptions_outil_max": SERIE_EXCEPTIONS_OUTIL_MAX,
            "couts_du_pilote_essai_a_blanc": vague == 2 and not reel}
    return {"plan": plan, "parties": parties, "parties_plan_complet": parties_plan, "file": file, "noms": noms,
            "reprise": rep, "lignes_avant": lignes_avant, "lignes_vague": lignes_vague, "depense_avant": depense_avant,
            "taches": taches, "v1": v1, "racine": racine, "couts_retenus": couts_retenus}


def texte_apercu(prep: dict) -> str:
    plan = prep["plan"]
    out = [f"Vague {plan['vague']} ({plan['mode']}) : {plan['parties_vague']} parties ; graine : {plan['graine_source']}",
           f"Coûts moyens : {plan['source_couts']}"]
    if plan["reduction"]:
        out.append(f"Réduction des passages (C9) : facteur {plan['reduction']['centiemes'] / 100:.2f}, "
                   f"passages {plan['reduction']['passages']}")
    out.append(f"{'modèle':<18} {'env':<10} {'parties':>7} {'moyen $':>9} {'estimation $':>12}")
    for d in plan["par_configuration"]:
        out.append(f"{d['modele']:<18} {d['env']:<10} {d['parties']:>7} {d['cout_moyen_usd']:>9.4f} {d['estimation_usd']:>12.4f}")
    pmax = _cents_bas(plan["plafond_permis_usd"])
    seuil = seuil_arret(plan["vague"], pmax)[0]
    out += [f"Estimation de la vague : {plan['estimation_usd']:.2f} USD",
            f"Plafond permis : {pmax:.2f} USD ({plan['facteur_plafond']} x l'estimation"
            + (", dans la limite du budget restant" if plan["vague"] == 2 and plan["budget_restant_usd"] is not None else "")
            + f") ; arrêt automatique au seuil : {plan['regle_arret']} (au plafond permis : {seuil:.2f} USD"
            + (", aucune partie ne pourrait être lancée" if seuil <= 0 else "") + ")",
            f"Tentatives à jouer : {len(prep['file'])}"]
    return "\n".join(out) + "\n"


def creer_dossier_de_vague(racine_vague: Path, nom: str, reel: bool, verrous: list) -> Path:
    """Crée le dossier d'une nouvelle vague et y prend le verrou, sous un flock exclusif de `<racine>/vague<N>/`
    (contre-vérification, constat B) : en réel, l'absence de tout autre dossier réel de la vague est revérifiée sous ce
    flock, donc deux lancements qui se chevauchent n'ouvrent jamais deux dossiers (le contrôle de preparer, fait plus
    tôt pour refuser vite, ne suffit pas : la clé et l'extraction des outils passent entre les deux)."""
    racine_vague.mkdir(parents=True, exist_ok=True)
    fd = os.open(racine_vague, os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        existants = dossiers_reels(racine_vague) if reel else []
        if existants:
            raise ErreurPilote(f"la vague a déjà un dossier réel ({racine_vague / existants[-1]}) : la poursuivre avec "
                               f"--reprendre <dossier>, jamais par un nouveau lancement")
        sortie = racine_vague / nom
        try:
            sortie.mkdir(exist_ok=False)
        except FileExistsError:
            raise ErreurPilote(f"le dossier {sortie} existe déjà (lancement dans la même seconde) : relancer")
        verrous.append(prendre_verrou(sortie))
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    return sortie


def _module_gel():
    """gel/manifeste.py (manifeste du gel du plan), chargé par son chemin."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("gel_manifeste", RACINE / "gel" / "manifeste.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verifier_gel() -> dict:
    """Vague réelle, au lancement comme à la reprise : le dépôt doit être conforme au manifeste du gel du plan
    (relecture C13, P3) ; rend le commit, l'étiquette et l'empreinte du manifeste, notés dans le plan de jeu."""
    import subprocess
    ecarts = _module_gel().verifier(RACINE)
    if ecarts:
        raise ErreurPilote("le dépôt diffère du manifeste du gel du plan (gel/manifeste.py --verifier) : "
                           + " ; ".join(ecarts[:5]) + (" …" if len(ecarts) > 5 else ""))

    def git(*args):
        return subprocess.run(["git", "-C", str(RACINE), *args], capture_output=True, text=True).stdout.strip()
    m = RACINE / "gel" / "MANIFESTE_SHA256.txt"
    import hashlib
    return dict(commit=git("rev-parse", "HEAD"), etiquette=git("describe", "--tags", "--exact-match") or None,
                manifeste_gel=hashlib.sha256(m.read_bytes()).hexdigest() if m.is_file() else None)


def mettre_en_place(a, prep: dict, argv, cle, empreintes: dict, verrous: list) -> dict:
    """Dossier de vague, verrou, plan de jeu, journal, comptable et registre ; tentatives interrompues récupérées,
    coûts retenus notés, marqueur de la vague 1. Toute erreur ici est un refus propre (revue du 06/11, constat 13)."""
    plan, rep, noms = prep["plan"], prep["reprise"], prep["noms"]
    horodatage = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    entete = {"etape": "experience", "vague": a.vague, "mode": plan["mode"], "cache": True,
              "client_simule": MODELE_USER, "prix_usd_par_million": p2.prix_json(), "graine": plan["graine"],
              "accord_otsoa_usd": a.accord_otsoa_usd, "estimation_usd": plan["estimation_usd"],
              "plafond_permis_usd": plan["plafond_permis_usd"], "budget_restant_usd": plan["budget_restant_usd"],
              "debut": maintenant(), "fin": None, "arrets": [], "reprises": [], "gel_plan": prep.get("gel_plan")}
    orphelin = verrous[0]["orphelin"] if verrous else None
    if rep:
        sortie = rep["dossier"]
        entete.update({k: v for k, v in rep["cout"].items() if k not in ("parties", "plafond_usd", "seuil_arret_usd",
                                                                        "cumul_usd", "arret", "usage_estime")})
        entete["arrets"] = list(entete.get("arrets") or []) + ([rep["cout"]["arret"]] if rep["cout"].get("arret") else [])
        entete["reprises"] = list(entete.get("reprises") or []) + [{
            "horodatage": horodatage, "plafond_usd": a.plafond_usd, "accord_otsoa_usd": a.accord_otsoa_usd,
            "couts_retenus": prep["couts_retenus"], "verrou_orphelin": orphelin, "gel_plan": prep.get("gel_plan")}]
        entete.update(fin=None, accord_otsoa_usd=a.accord_otsoa_usd)
    else:
        sortie = creer_dossier_de_vague(prep["racine"] / f"vague{a.vague}",
                                        horodatage if a.reel else horodatage + "-blanc", a.reel, verrous)
        plan["horodatage"] = horodatage
        plan["commande"] = list(argv) if argv is not None else sys.argv[1:]
        plan["gel_plan"] = prep.get("gel_plan")
        pe.ecrire_json_atomique(sortie / "plan_de_jeu.json", plan)
        with open(sortie / "ordre_de_jeu.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=CHAMPS_ORDRE, extrasaction="ignore")
            w.writeheader()
            for k, x in enumerate(prep["parties"], 1):
                w.writerow(dict(x, ordre=k))
        if a.vague == 2 and prep["v1"]["plan"].get("mode") == plan["mode"]:
            # Constat 3. Seulement une vague 2 du même mode : une vague 2 à blanc sur une vague 1 réelle ne joue rien
            # pour de vrai et ne touche pas au dossier réel (CHOIX_LANCEUR.md, choix 26).
            marquer_vague1(prep["v1"]["dossier"], sortie, plan["mode"])
    pe.ecrire_json_atomique(sortie / "outils_agent.json", {"horodatage": maintenant(), "empreintes": empreintes,
                                                           "reference": str(DOSSIER_OUTILS), "identiques": True})
    journal = JournalVague(sortie, cle)
    compta = Comptable(a.plafond_usd, a.vague)
    reg = Registre(sortie, entete, prep["lignes_vague"], compta)
    deja = sum(l.get("cout_usd") or 0.0 for l in prep["lignes_vague"])
    journal.ecrire(f"{'reprise de la' if rep else 'début de la'} vague {a.vague}, mode {plan['mode']}, plafond "
                   f"{a.plafond_usd:.2f} USD (arrêt à {compta.seuil:.2f} : {compta.regle}), "
                   f"accord d'Otsoa {a.accord_otsoa_usd:.2f} USD, "
                   f"estimation {plan['estimation_usd']:.2f} USD, plafond permis {_cents_bas(plan['plafond_permis_usd']):.2f} USD, "
                   f"graine {plan['graine']} ({plan['graine_source']}), concurrence {a.concurrence}, "
                   f"tentatives à jouer {len(prep['file'])}" + (f", limite {a.limite}" if a.limite else ""))
    if orphelin is not None:
        journal.ecrire(f"VERROU ORPHELIN repris : processus {orphelin.get('pid')} mort (verrou posé le "
                       f"{orphelin.get('debut')}, mis de côté sous {orphelin.get('mis_de_cote')})")
    journal.ecrire(f"coûts moyens de l'estimation : {plan['source_couts']}")
    if plan["reduction"]:
        journal.ecrire(f"RÉDUCTION DES PASSAGES (C9) : facteur {plan['reduction']['centiemes'] / 100:.2f}, "
                       f"passages {plan['reduction']['passages']}")
    journal.ecrire(f"définitions d'outils identiques à banc/outils_agent/ : {empreintes}")
    retenus = dict(prep["couts_retenus"])
    if rep and rep["orphelines"]:
        rec = recuperer_interrompues(sortie, rep["orphelines"], reg, horodatage, retenus)
        deja += sum(l.get("cout_usd") or 0.0 for l in rec)
        journal.ecrire(f"tentatives interrompues récupérées : {[l['id'] for l in rec]}")
        for l in rec:
            retenus.pop(l.get("cout_retenu_pour"), None)
    if rep and retenus:
        par_id = {l["id"]: l for l in rep["lignes"]}
        for ident, usd in sorted(retenus.items()):
            ligne = ligne_cout_retenu(par_id[ident], usd, horodatage)
            reg.fin(ligne, evenement="cout_retenu", id_evenement=ligne["id"])
            deja += usd
        journal.ecrire(f"coûts retenus par l'opérateur : {retenus}")
    if rep:
        prep["file"] = file_d_attente(prep["parties"], prep["lignes_avant"] + reg.lignes)
        if a.limite:
            prep["file"] = prep["file"][:a.limite]
    compta.ajouter(deja)
    if deja:
        journal.ecrire(f"déjà dépensé dans cette vague : {deja:.6f} USD")
    if a.reel:
        journal.ecrire(f"parties factices supprimées : {pe.nettoyer_parties_factices(TAU2 / 'data' / 'simulations')}")
    reg.ecrire_cout()
    pe.ecrire_json_atomique(sortie / "modeles_renvoyes.json", noms.json())
    exceptions = {}
    for l in reg.lignes:
        if l.get("arret") == ARRET_EXCEPTION_OUTIL:
            exceptions[l["env"]] = exceptions.get(l["env"], 0) + 1
    return {"sortie": sortie, "horodatage": horodatage, "journal": journal, "compta": compta, "reg": reg,
            "exceptions_outil": exceptions}


def jouer(a, prep: dict, mise: dict, env: dict, cle, executeur) -> int:
    """Joue la file, écrit cout.json, le post-traitement et le rapport de vague ; rend le code de sortie."""
    plan, noms = prep["plan"], prep["noms"]
    sortie, journal, compta, reg = mise["sortie"], mise["journal"], mise["compta"], mise["reg"]
    ctx = {"sortie": sortie, "reel": a.reel, "env_enfant": env, "cle": cle, "horodatage": mise["horodatage"],
           "cache": True, "vague": a.vague, "etape": f"vague{a.vague}", "verrou_wb": threading.Lock(), "registre": reg,
           "noms": noms, "historique": historique_parties(prep["lignes_avant"] + reg.lignes),
           "exceptions_outil": mise["exceptions_outil"]}
    lancer_vague(prep["file"], a.concurrence, compta, ctx, journal, executeur)
    reg.ecrire_cout(fin=maintenant())
    pe.ecrire_json_atomique(sortie / "modeles_renvoyes.json", noms.json())
    lignes_toutes = prep["lignes_avant"] + reg.lignes
    finales = {l["partie"] for l in lignes_toutes if l.get("finale")}
    en_attente = file_d_attente(prep["parties"], lignes_toutes)
    restantes = compter([x for x in prep["parties_plan_complet"] if x["id"] not in finales])
    actions, erreur_post, rc = None, None, 0
    try:
        actions = post_traitement(sortie)
    except Exception as e:  # le rapport s'écrit quand même, sans le point 3
        erreur_post = f"post-traitement échoué : {type(e).__name__} {e}"
        journal.ecrire(erreur_post)
        rc = 3
    plan_r = dict(plan, arret=arret_visible(compta.arret), plafond_usd=a.plafond_usd, seuil_arret_usd=compta.seuil)
    joues = joues_par_passage(lignes_toutes) if a.vague == 1 else None
    rapport = rapport_vague(plan_r, prep["parties"], reg.lignes, actions, noms, en_attente, restantes,
                            a.budget_restant_usd if a.vague == 1 else plan["budget_restant_usd"], prep["depense_avant"],
                            joues, prep["taches"], erreur_post)
    pe.ecrire_json_atomique(sortie / "rapport_vague.json", rapport)
    texte = texte_rapport(rapport)
    (sortie / "rapport_vague.txt").write_text(texte, encoding="utf-8")
    jouees_limite = {x["id"] for x, _ in prep["file"]}
    reste = [x for x, _ in en_attente if x["id"] in jouees_limite or not a.limite]
    journal.ecrire(f"fin du lanceur : {len(reg.lignes)} tentatives notées, cumul {compta.cumul:.6f} USD, parties "
                   f"restantes {len(reste)} -> {sortie}")
    print(texte)
    if rc:
        return rc
    return 4 if reste else 0


def main(argv=None, executeur=None, base_env=None, chemin_cle=None, extracteur=None) -> int:
    a = analyser(argv)
    executeur = executeur or executer_partie
    base = os.environ if base_env is None else base_env
    verrous: list = []  # tenus jusqu'à la fin : le verrou du dossier de la vague jouée
    mise_en_route: list = []  # tenus pendant la mise en route seulement : le verrou de la vague 1, pour la vague 2
    try:
        try:
            if a.reprendre and not a.apercu:
                # Avant de lire tentatives.jsonl : un second lanceur sur le même dossier ne doit rien prendre pour une
                # interruption ni rien jouer (revue du 06/11, constat 1).
                verrous.append(prendre_verrou(Path(a.reprendre)))
            elif a.vague == 2 and a.vague1 and not a.apercu and mode_de_la_vague(a.vague1) == mode_de(a):
                # Contre-vérification, constat D : la vague 1 est lue, puis marquée (vague2.json), sous son verrou ; une
                # reprise de la vague 1 en cours fait refuser la vague 2, et une reprise lancée ensuite voit le marqueur.
                mise_en_route.append(prendre_verrou(Path(a.vague1)))
            prep = preparer(a)
            if a.apercu:
                print(texte_apercu(prep))
                return 0
            if a.reel:   # relecture C13, P3 : rien de réel ne tourne hors du code figé (lancement et reprise)
                prep["gel_plan"] = verifier_gel()
            cle = pe.lire_cle(chemin_cle or CHEMIN_CLE) if a.reel else None
            env = environnement_enfants(base, cle)
            pe.verifier_env_enfant(env, a.reel)
            pe.verifier_pas_de_dotenv(TAU2, WB_RUN)
            empreintes = verifier_outils_agent(environnement_enfants(base, None), extracteur)
            mise = mettre_en_place(a, prep, argv, cle, empreintes, verrous)
        except (ErreurPilote, FileExistsError) as e:
            print(f"REFUS : {e}", file=sys.stderr)
            return 2
        finally:
            while mise_en_route:
                liberer_verrou(mise_en_route.pop())
        return jouer(a, prep, mise, env, cle, executeur)
    finally:
        for v in verrous:
            liberer_verrou(v)


if __name__ == "__main__":
    sys.exit(main())
