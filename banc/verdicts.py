"""Verdicts action par action pour l'experience « autonomie meritee ».

On enregistre des parties jouees par des agents sur tau-bench 2.0 (airline,
retail, banking_knowledge) et sur WorkBench, puis on rejoue des regles hors
ligne. Chaque tache liste les actions attendues. Ce module donne un verdict
pour chaque ECRITURE de l'agent, par comparaison exacte avec ces actions,
sans aucun juge IA. Le banc verifie seulement que les actions attendues ont
eu lieu ; ici on fait le controle inverse, action par action.

SPECIFICATION (a implementer exactement)
----------------------------------------
- Lectures (outils READ) : kind = « lecture », aucun verdict.
- Demandes d'aide (transfer_to_human_agents, request_human_agent_transfer,
  etc.) : kind = « doute », neutre, aucun verdict.
- Actions de l'utilisateur simule (requestor « user ») : ignorees.
- Ecritures de l'agent : outils WRITE. Pour la banque, c'est l'outil
  sous-jacent de `call_discoverable_agent_tool`, dont le nom est dans
  `agent_tool_name` et les arguments dans une chaine JSON a parser. Chaque
  ecriture recoit un verdict parmi quatre :
  * « juste » : elle correspond a une action attendue de l'agent qui n'est
    pas encore consommee.
      - meme nom, et memes arguments compares : ceux de `compare_args` s'il
        est present, sinon tous ;
      - nombres normalises entre int et float, y compris 14.00 contre 14.0
        dans le JSON imbrique ;
      - arguments imbriques parses, l'ordre des cles et celui des actions
        n'importe pas ;
      - appariement un pour un : la premiere ecriture correspondante
        consomme l'action attendue.
  * « doublon » : elle correspond a une action attendue deja consommee.
  * « refusée » : l'outil a renvoye une erreur, donc aucun changement
    d'etat. Categorie a part, son traitement sera decide plus tard.
  * « fausse » : toute autre ecriture.
  Cinquieme valeur, posee APRES juger() par marquer_doublons_sans_effet (verdicts_csv.py) : « doublon sans effet »,
  neutre, pour un « doublon » sur un outil dont la table des outils dit `idempotent` = « oui ».
- Champs de sortie pour chaque action : identifiant de partie, tache, rang
  dans la partie, banc, domaine, outil, arguments, kind, verdict, et modele
  de l'agent quand l'information existe (voir CHAMPS).
- Ce que le module ne fait pas : decider quelles categories comptent comme
  erreur. C'est un parametre, regle ailleurs.

CHOIX D'IMPLEMENTATION (la specification ne les tranche pas)
------------------------------------------------------------
- Ordre de verification d'une ecriture : refus d'abord (une ecriture refusee
  ne consomme jamais d'action attendue), puis juste, doublon, fausse.
- Refus tau-bench : ToolMessage.error vrai, ou execution_status « rejected »
  (rejet par l'orchestrateur), ou contenu commencant par « Error » ou
  « Failed to », ou (banque) contenu qui correspond a une chaine renvoyee par
  un chemin de sortie SANS modification de la base (banc/refus_banque.json,
  extrait par lecture AST de tools.py, voir extraire_refus_banque). La banque
  renvoie ses refus en texte avec error=False.
- Arguments effectifs (tau-bench) : l'appel de l'agent et l'action attendue
  sont tous deux completes par les valeurs par defaut de la signature de
  l'outil (lues par AST dans tools.py, sans import). Un argument omis dont le
  defaut egale la valeur attendue donne « juste » ; un defaut different donne
  « fausse ». compare_args, quand il est present, filtre apres completion.
- Champ `motif` (WorkBench, ecritures « fausse » seulement) :
  « texte libre seulement » si l'appel ne differe d'une action attendue du
  meme outil que par des champs de texte libre (CHAMPS_LIBRES_WORKBENCH, voir
  la justification la-bas), « autre » sinon. Vide pour tout le reste, et
  pour tau-bench sauf le cas suivant. La comparaison reste exacte : le motif ne change pas le verdict.
- payment_id sans paiement (aviation, PAIEMENT_CONDITIONNEL) : pour
  update_reservation_baggages et update_reservation_flights, payment_id n'est
  compare que si l'appel a enregistre un paiement, c'est-a-dire si
  l'historique de paiement de la reservation s'est allonge. L'etat d'avant est
  le dernier etat de la reservation renvoye dans la partie (lecture ou
  ecriture), sinon l'etat initial de db.json. Etat d'avant inconnu : payment_id
  est compare (cas strict). Quand cette exception change le verdict, le motif
  vaut MOTIF_PAIEMENT_SANS_EFFET, pour que le verdict strict reste calculable.
- Fichiers du pilote WorkBench (workbench_pilote.py / src/evals/inference.py) :
  `<modele>_all_<horodatage>.csv` (task, function_calls, full_response, error),
  `_meta.json`, `_traces.json` ; convertis par parties_depuis_pilote_workbench.
- Refus WorkBench : aucun drapeau, l'outil renvoie une chaine. Une ecriture
  est reussie si la chaine contient « successfully » (update/delete/send/...),
  est un identifiant a 8 chiffres (create_event, create_task, add_customer)
  ou un chemin « plots/... » (create_plot). Tout autre retour = refusee.
  Sans resultat enregistre, on ne peut pas conclure a un refus.
- Comparaison : les listes gardent leur ordre ; les chaines sont comparees
  telles quelles ; un booleen n'est pas un nombre ; une chaine qui contient
  un objet ou une liste JSON est parsee (recursivement). Une chaine
  numerique reste une chaine.
- Banque : attendue et appel sont « deballes » : le nom compare est
  `agent_tool_name`, les arguments compares sont le JSON de `arguments`.
  Un `compare_args` de l'enveloppe qui ne cite pas « arguments » (cas
  courant : ['agent_tool_name']) ne compare donc que le nom.
- Ecriture sans etat : un outil decore WRITE avec mutates_state=False
  (rewrite_context) ne change pas l'etat : kind « autre », pas de verdict.
  Un outil GENERIC meme avec mutates_state=True (unlock_discoverable_agent_tool,
  give_discoverable_user_tool) n'est pas WRITE : kind « autre ».
- Outil absent des tables (nom invente) : kind « inconnu », pas de verdict.
- Rang : position (a partir de 0) de l'action parmi toutes les actions de
  l'agent de la partie (lectures et doutes compris), dans l'ordre des messages
  (turn_idx si present).
- Le module ne lit les sources des bancs que comme des donnees (regex, ast,
  csv, json) : il n'importe ni n'execute aucun code des bancs.
"""
from __future__ import annotations

import ast
import csv
import json
import math
import re
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Iterable, Iterator, Optional

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
LECTURE = "lecture"
DOUTE = "doute"
ECRITURE = "écriture"
AUTRE = "autre"
INCONNU = "inconnu"

JUSTE = "juste"
DOUBLON = "doublon"
DOUBLON_SANS_EFFET = "doublon sans effet"  # neutre : ni reussite ni erreur (REGLE.md, 5 novembre, point 6)
REFUSEE = "refusée"
FAUSSE = "fausse"

CHAMPS = [
    "partie",
    "tache",
    "rang",
    "banc",
    "domaine",
    "outil",
    "arguments",
    "kind",
    "verdict",
    "modele",
    "motif",
    "resultat",  # ajoute le 05/11 : contenu renvoye par l'outil, sert a lire les montants (typage.py)
]

MOTIF_TEXTE_LIBRE = "texte libre seulement"
MOTIF_AUTRE = "autre"
MOTIF_PAIEMENT_SANS_EFFET = "payment_id sans effet (aucun paiement enregistré)"

# Outils aviation dont le moyen de paiement n'a d'effet enregistré que si un paiement est créé
# (airline/tools.py, commit 033bf08, _payment_for_update) : le moyen est vérifié (il doit exister et ne pas être
# un certificat, sinon l'appel est refusé), mais un Payment n'est ajouté à payment_history que si total_price != 0,
# et une carte cadeau perd total_price, donc rien si le total est nul. Constat du pilote, étape 2 (05/11), tâche 21 :
# ajout de bagages gratuits avec un autre moyen de paiement, alerte levée en relecture (motif d).
PAIEMENT_CONDITIONNEL = {"update_reservation_baggages": "payment_id", "update_reservation_flights": "payment_id"}

COMMIT_TAU2 = "033bf08"
FICHIER_BANQUE = "src/tau2/domains/banking_knowledge/tools.py"
CHEMIN_REFUS_BANQUE = Path(__file__).with_name("refus_banque.json")
CHEMIN_TABLE_OUTILS = Path(__file__).with_name("table_outils.json")

ENVELOPPE_BANQUE = "call_discoverable_agent_tool"
DOMAINES_TAU2 = ("airline", "retail", "banking_knowledge")

# Demandes d'aide : transfer_to_human_agents, request_human_agent_transfer,
# initial_transfer_to_human_agent_NNNN, emergency_credit_bureau_incident_transfer_1114.
_DOUTE_RE = re.compile(r"human_agent|transfer_to_human|_incident_transfer_")
_PREFIXES_ERREUR = ("Error", "Failed to")


# ---------------------------------------------------------------------------
# Types de donnees
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Attendue:
    nom: str
    arguments: dict
    compare_args: Optional[tuple] = None


@dataclass
class Appel:
    nom: str
    arguments: dict
    kind: str
    refuse: bool = False
    resultat: Optional[str] = None  # contenu renvoye par l'outil, tel quel (None : rien d'enregistre)
    ignorer: tuple = ()  # arguments sans effet enregistre pour cet appel, exclus de la comparaison


@dataclass
class TypesOutils:
    """Types d'outils de l'agent : 'read', 'write', 'generic', 'think',
    'write_sans_etat'. `decouvrables` ne sert qu'a la banque."""

    directs: dict = field(default_factory=dict)
    decouvrables: dict = field(default_factory=dict)
    # {nom d'outil: {parametre: valeur par defaut litterale}}, lus par AST
    defauts_directs: dict = field(default_factory=dict)
    defauts_decouvrables: dict = field(default_factory=dict)
    # aviation seulement : {reservation_id: nombre d'entrees de payment_history} dans db.json (etat initial ; exact
    # parce qu'aucune tache aviation n'a d'initial_state, verifie par un test)
    paiements_initiaux: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Comparaison
# ---------------------------------------------------------------------------
def normaliser(x: Any) -> Any:
    """Forme canonique comparable avec == : nombres int/float unifies,
    chaines JSON (objet ou liste) parsees, booleens distincts des nombres."""
    if isinstance(x, bool):
        return ("__bool__", x)
    if isinstance(x, (int, float)):
        f = float(x)
        if math.isfinite(f) and f.is_integer():
            return int(f)
        return f
    if isinstance(x, dict):
        return {str(k): normaliser(val) for k, val in x.items()}
    if isinstance(x, (list, tuple)):
        return [normaliser(val) for val in x]
    if isinstance(x, str):
        s = x.strip()
        if s[:1] in ("{", "["):
            try:
                parse = json.loads(s)
            except ValueError:
                return x
            if isinstance(parse, (dict, list)):
                return normaliser(parse)
        return x
    return x


def correspond(attendue: Attendue, nom: str, arguments: dict, ignorer: tuple = ()) -> bool:
    """`ignorer` : arguments exclus des deux cotes (sans effet enregistre pour cet appel)."""
    if attendue.nom != nom:
        return False
    ca = attendue.compare_args
    if ca is None:
        if not ignorer:
            return normaliser(attendue.arguments) == normaliser(arguments)

        def sans(d: dict) -> dict:
            return {k: val for k, val in d.items() if k not in ignorer}

        return normaliser(sans(attendue.arguments)) == normaliser(sans(arguments))
    if len(ca) == 0:
        return True

    def filtre(d: dict) -> dict:
        return {k: val for k, val in d.items() if k in ca and k not in ignorer}

    return normaliser(filtre(attendue.arguments)) == normaliser(filtre(arguments))


def juger(appels: list, attendues: list) -> list:
    """Retourne, pour chaque appel, (verdict, index de l'attendue) ; (None, None)
    pour ce qui n'est pas une ecriture. L'index n'est donne que pour « juste »
    (attendue consommee) et « doublon » (attendue deja consommee)."""
    consommees: set = set()
    sortie = []
    for ap in appels:
        if ap.kind != ECRITURE:
            sortie.append((None, None))
            continue
        if ap.refuse:
            sortie.append((REFUSEE, None))
            continue
        libre = next(
            (i for i, a in enumerate(attendues) if i not in consommees and correspond(a, ap.nom, ap.arguments, ap.ignorer)),
            None,
        )
        if libre is not None:
            consommees.add(libre)
            sortie.append((JUSTE, libre))
            continue
        deja = next(
            (i for i, a in enumerate(attendues) if i in consommees and correspond(a, ap.nom, ap.arguments, ap.ignorer)),
            None,
        )
        if deja is not None:
            sortie.append((DOUBLON, deja))
        else:
            sortie.append((FAUSSE, None))
    return sortie


# ---------------------------------------------------------------------------
# Doublons sans effet (REGLE.md, 5 novembre, point 6, precision du matin)
# ---------------------------------------------------------------------------
_TABLE_CACHE: dict = {}


def _table_outils() -> dict:
    if "t" not in _TABLE_CACHE:
        _TABLE_CACHE["t"] = json.loads(CHEMIN_TABLE_OUTILS.read_text(encoding="utf-8"))
    return _TABLE_CACHE["t"]


def idempotence(banc: str, domaine: str, outil: str, table: Optional[dict] = None) -> str:
    """Idempotence d'un outil lue dans la table des outils : « oui », « non », « refus », « incertain » ou
    « sans objet ». WorkBench : cle (banc, outil), le domaine de la ligne ne compte pas. Outil absent de la table,
    ou champ absent : « incertain » (traite comme « non »)."""
    for o in (table or _table_outils()).get("outils", []):
        if o.get("banc") == banc and o.get("outil") == outil and (banc == "workbench" or o.get("domaine") == domaine):
            return o.get("idempotent") or "incertain"
    return "incertain"


def marquer_doublons_sans_effet(lignes: Iterable[dict], table: Optional[dict] = None) -> list:
    """Etape qui suit juger() : une ligne de verdict « doublon » sur un outil idempotent (« oui » dans la table)
    devient « doublon sans effet », categorie neutre. Tout autre doublon (outil « non », « refus », « incertain »,
    ou absent de la table) reste « doublon », donc une erreur. Les autres verdicts et tous les champs sont inchanges ;
    les lignes recues ne sont pas modifiees. Le verdict brut de juger() reste « doublon » : cette etape est separee
    pour que le pire cas (verdicts bruts, REGLE.md point 7) reste calculable."""
    sortie = []
    for l in lignes:
        if l.get("verdict") == DOUBLON and idempotence(l.get("banc", ""), l.get("domaine", ""), l.get("outil", ""), table) == "oui":
            l = {**l, "verdict": DOUBLON_SANS_EFFET}
        sortie.append(l)
    return sortie


# ---------------------------------------------------------------------------
# tau-bench : types d'outils (regex sur les decorateurs, sans import du banc)
# ---------------------------------------------------------------------------
_DECO_RE = re.compile(r"^\s*@(is_tool|is_discoverable_tool)\((.*)\)\s*$")
_DEF_RE = re.compile(r"^\s*def\s+(\w+)\s*\(")
_CLASSE_RE = re.compile(r"^class\s+(\w+)")
_TYPE_RE = re.compile(r"ToolType\.(\w+)")
_MUT_RE = re.compile(r"mutates_state\s*=\s*(True|False)")


def _types_depuis_source(texte: str, types: TypesOutils) -> None:
    classe = None
    en_attente: list = []
    for ligne in texte.splitlines():
        m = _CLASSE_RE.match(ligne)
        if m:
            classe = m.group(1)
            en_attente = []
            continue
        m = _DECO_RE.match(ligne)
        if m:
            en_attente.append((m.group(1), m.group(2)))
            continue
        m = _DEF_RE.match(ligne)
        if m:
            nom = m.group(1)
            # classes cote utilisateur (KnowledgeUserTools...) : pas des outils de l'agent
            if en_attente and not (classe and "User" in classe):
                for deco, params in en_attente:
                    t = _TYPE_RE.search(params)
                    typ = t.group(1).lower() if t else "read"
                    mut = _MUT_RE.search(params)
                    if typ == "write" and mut and mut.group(1) == "False":
                        typ = "write_sans_etat"
                    cible = types.directs if deco == "is_tool" else types.decouvrables
                    cible.setdefault(nom, typ)
            en_attente = []
            continue
        if ligne.strip() and not ligne.strip().startswith(("#", "@")) and en_attente:
            # ligne de code entre decorateur et def (ne devrait pas arriver)
            en_attente = []


def _defauts_depuis_source(texte: str, types: TypesOutils) -> None:
    """Valeurs par defaut litterales des parametres d'outils (AST, sans import)."""
    for classe in ast.parse(texte).body:
        if not isinstance(classe, ast.ClassDef) or "User" in classe.name:
            continue
        for fn in classe.body:
            if not isinstance(fn, ast.FunctionDef):
                continue
            for deco in fn.decorator_list:
                nom_deco = deco.func.id if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Name) else None
                if nom_deco not in ("is_tool", "is_discoverable_tool"):
                    continue
                a = fn.args
                pos = a.posonlyargs + a.args
                defauts = {}
                for param, d in zip(pos[len(pos) - len(a.defaults):], a.defaults):
                    defauts[param.arg] = d
                for param, d in zip(a.kwonlyargs, a.kw_defaults):
                    if d is not None:
                        defauts[param.arg] = d
                lits = {}
                for k, d in defauts.items():
                    try:
                        lits[k] = ast.literal_eval(d)
                    except (ValueError, SyntaxError):
                        pass  # defaut non litteral : non complete
                if lits:
                    cible = types.defauts_directs if nom_deco == "is_tool" else types.defauts_decouvrables
                    cible.setdefault(fn.name, lits)


def types_tau2(racine, domaine: str) -> TypesOutils:
    racine = Path(racine)
    dossier = racine / "src" / "tau2" / "domains" / domaine
    types = TypesOutils()
    fichiers = [dossier / "tools.py"]
    if domaine == "banking_knowledge":
        fichiers.append(dossier / "retrieval_mixins.py")
    for f in fichiers:
        if f.is_file():
            texte = f.read_text(encoding="utf-8")
            _types_depuis_source(texte, types)
            _defauts_depuis_source(texte, types)
    if not types.directs:
        raise FileNotFoundError(f"aucun outil trouve pour le domaine {domaine} sous {dossier}")
    if domaine == "airline":
        base = racine / "data" / "tau2" / "domains" / "airline" / "db.json"
        if base.is_file():
            resas = json.loads(base.read_text(encoding="utf-8")).get("reservations") or {}
            types.paiements_initiaux = {rid: len(r.get("payment_history") or []) for rid, r in resas.items()}
    return types


# ---------------------------------------------------------------------------
# Banque : chaines renvoyees par les chemins qui sortent SANS modifier la base
# ---------------------------------------------------------------------------
_APPELS_ECRITURE_BASE = {"add_to_db", "update_record_in_db"}
_METHODES_MUTANTES = {"pop", "update", "append", "extend", "remove", "clear", "setdefault", "insert", "popitem"}


def _echapper(texte: str) -> str:
    return texte.replace("{", "{{").replace("}", "}}")


def _modele_statique(n) -> Optional[str]:
    """Modele textuel d'une valeur retournee, '{}' pour chaque trou ; None si
    la valeur n'est pas une chaine constante ou un f-string."""
    if isinstance(n, ast.Constant) and isinstance(n.value, str):
        return _echapper(n.value)
    if isinstance(n, ast.JoinedStr):
        morceaux = []
        for part in n.values:
            if isinstance(part, ast.Constant):
                morceaux.append(_echapper(str(part.value)))
            else:
                morceaux.append("{}")
        return "".join(morceaux)
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        g, d = _modele_statique(n.left), _modele_statique(n.right)
        return g + d if g is not None and d is not None else None
    return None


def _valeur_retournee(ret: ast.Return) -> Optional[str]:
    val = ret.value
    if isinstance(val, ast.Tuple) and val.elts:
        val = val.elts[0]  # helpers qui renvoient (message_erreur, objet)
    return _modele_statique(val) if val is not None else None


def _contient_mutation(noeud) -> bool:
    for n in ast.walk(noeud):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id in _APPELS_ECRITURE_BASE:
                return True
            if isinstance(f, ast.Attribute) and (f.attr in _METHODES_MUTANTES or f.attr in _APPELS_ECRITURE_BASE):
                return True
        if isinstance(n, (ast.Assign, ast.AugAssign)):
            cibles = n.targets if isinstance(n, ast.Assign) else [n.target]
            if any(isinstance(c, ast.Subscript) for c in cibles):
                return True
        if isinstance(n, ast.Delete):
            return True
    return False


def _noms_succes_base(fn: ast.FunctionDef) -> set:
    """Variables recevant le succes d'add_to_db / update_record_in_db."""
    noms = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
            f = n.value.func
            if isinstance(f, ast.Name) and f.id in _APPELS_ECRITURE_BASE:
                cible = n.targets[0]
                if isinstance(cible, ast.Tuple) and cible.elts:
                    cible = cible.elts[0]
                if isinstance(cible, ast.Name):
                    noms.add(cible.id)
    return noms


def _retours_helpers(arbre: ast.Module) -> dict:
    """{helper: [(ligne, modele)]} pour les fonctions de module _validate* (et
    celles qu'elles appellent) : messages d'erreur partages entre outils."""
    fonctions = {n.name: n for n in arbre.body if isinstance(n, ast.FunctionDef) and n.name.startswith("_validate")}
    propres = {}
    for nom, fn in fonctions.items():
        propres[nom] = [
            (n.lineno, m)
            for n in ast.walk(fn)
            if isinstance(n, ast.Return) and (m := _valeur_retournee(n)) is not None
        ]
    sortie = {}
    for nom, fn in fonctions.items():
        total = list(propres[nom])
        for n in ast.walk(fn):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in propres and n.func.id != nom:
                total += propres[n.func.id]
        sortie[nom] = sorted(set(total))
    return sortie


def _analyser_outil(fn: ast.FunctionDef, helpers: dict) -> list:
    """[(ligne, modele, regle)] des retours de chaines sur un chemin sans modification."""
    if not _contient_mutation(fn):
        return []  # l'outil ne modifie jamais rien : aucun de ses retours n'est un « refus »
    succes_base = _noms_succes_base(fn)
    sorties: list = []

    def appels_helpers(stmt) -> set:
        return {
            n.func.id
            for n in ast.walk(stmt)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in helpers
        }

    def suite(stmts, mute: bool, echec: bool):
        """Retourne (mute apres, la suite s'execute apres)."""
        for st in stmts:
            if isinstance(st, ast.Return):
                m = _valeur_retournee(st)
                if m is not None and (not mute or echec):
                    sorties.append((st.lineno, m, "echec-ecriture" if mute else "avant-modification"))
                return mute, False
            if isinstance(st, ast.Raise):
                return mute, False
            if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue  # fonctions imbriquees : leurs retours ne sont pas ceux de l'outil
            if isinstance(st, ast.If):
                t = st.test
                echec_corps = isinstance(t, ast.UnaryOp) and isinstance(t.op, ast.Not) and isinstance(t.operand, ast.Name) and t.operand.id in succes_base
                echec_sinon = isinstance(t, ast.Name) and t.id in succes_base
                if not mute:
                    for h in appels_helpers(t):
                        for ligne, m in helpers[h]:
                            sorties.append((ligne, m, "validation-partagee"))
                m1, t1 = suite(st.body, mute, echec or echec_corps)
                m2, t2 = suite(st.orelse, mute, echec or echec_sinon)
                suivants = [m for m, tombe in ((m1, t1), (m2, t2)) if tombe]
                if not suivants:
                    return mute, False
                mute = any(suivants)
                continue
            if isinstance(st, (ast.For, ast.AsyncFor, ast.While)):
                m1, _ = suite(st.body, mute, echec)
                m2, _ = suite(st.orelse, mute, echec)
                mute = mute or m1 or m2
                continue
            if isinstance(st, ast.Try):
                m1, _ = suite(st.body, mute, echec)
                mh = [suite(h.body, mute, echec)[0] for h in st.handlers]
                m3, _ = suite(st.finalbody, mute or m1, echec)
                mute = mute or m1 or any(mh) or m3
                continue
            if isinstance(st, (ast.With, ast.AsyncWith)):
                mute, tombe = suite(st.body, mute, echec)
                if not tombe:
                    return mute, False
                continue
            if not mute:
                for h in appels_helpers(st):
                    for ligne, m in helpers[h]:
                        sorties.append((ligne, m, "validation-partagee"))
            if _contient_mutation(st):
                mute = True
        return mute, True

    suite(fn.body, False, False)
    return sorties


def extraire_refus_banque(racine) -> dict:
    """Chaines renvoyees par les outils d'ECRITURE de l'agent (KnowledgeTools)
    sur des chemins qui sortent sans modifier la base, par lecture AST de
    banking_knowledge/tools.py (sans import ni execution).

    Regles : « avant-modification » = return d'une chaine constante avant toute
    modification sur le chemin ; « echec-ecriture » = return dans la branche
    d'echec de add_to_db / update_record_in_db (`if not success`) ; « validation-partagee » =
    chaine d'une fonction _validate* appelee avant toute modification (ligne = celle du helper).
    Les chaines de helper qui ne commencent pas par « Error » sont aussi donnees
    avec le prefixe « Error: » (les outils les enveloppent ainsi)."""
    chemin = Path(racine) / FICHIER_BANQUE
    arbre = ast.parse(chemin.read_text(encoding="utf-8"))
    helpers = _retours_helpers(arbre)
    types = TypesOutils()
    _types_depuis_source(chemin.read_text(encoding="utf-8"), types)
    outils: dict = {}
    for classe in arbre.body:
        if not isinstance(classe, ast.ClassDef) or classe.name != "KnowledgeTools":
            continue
        for fn in classe.body:
            if not isinstance(fn, ast.FunctionDef):
                continue
            decos = [d for d in fn.decorator_list if isinstance(d, ast.Call) and getattr(d.func, "id", "") in ("is_tool", "is_discoverable_tool")]
            if not decos:
                continue
            portee = "direct" if decos[0].func.id == "is_tool" else "decouvrable"
            table = types.directs if portee == "direct" else types.decouvrables
            if table.get(fn.name) != "write":
                continue
            entrees, vus = [], set()

            def ajouter(ligne, modele, regle):
                if (modele, ligne) in vus:
                    return
                vus.add((modele, ligne))
                entrees.append({"modele": modele, "fichier": FICHIER_BANQUE, "ligne": ligne, "regle": regle, "portee": portee})

            for ligne, modele, regle in _analyser_outil(fn, helpers):
                ajouter(ligne, modele, regle)
                if regle == "validation-partagee" and not modele.startswith("Error"):
                    ajouter(ligne, "Error: " + modele, regle)
            if entrees:
                outils[fn.name] = sorted(entrees, key=lambda e: (e["ligne"], e["modele"]))
    return {
        "source": {
            "fichier": FICHIER_BANQUE,
            "commit": COMMIT_TAU2,
            "genere_par": "banc/verdicts.py extraire_refus_banque (lecture AST, aucun import du banc)",
        },
        "outils": dict(sorted(outils.items())),
    }


# ---------------------------------------------------------------------------
# tau-bench : taches et actions attendues
# ---------------------------------------------------------------------------
def _json_dict(brut: Any) -> dict:
    if isinstance(brut, dict):
        return brut
    if brut is None or (isinstance(brut, str) and not brut.strip()):
        return {}
    try:
        parse = json.loads(brut) if isinstance(brut, str) else None
    except ValueError:
        parse = None
    if isinstance(parse, dict):
        return parse
    return {"__arguments_illisibles__": brut}


def _deballer(nom: str, arguments: dict) -> tuple:
    """(nom, arguments, enveloppe) : ouvre call_discoverable_agent_tool."""
    if nom == ENVELOPPE_BANQUE and isinstance(arguments, dict):
        interne = arguments.get("agent_tool_name") or nom
        return interne, _json_dict(arguments.get("arguments")), True
    return nom, arguments if isinstance(arguments, dict) else {}, False


def _completer(arguments: dict, defauts: Optional[dict]) -> dict:
    """Arguments effectifs : valeurs par defaut de la signature, puis ceux donnes."""
    if not defauts:
        return arguments
    return {**defauts, **arguments}


def _defauts(types: Optional[TypesOutils], nom: str, enveloppe: bool) -> Optional[dict]:
    if types is None:
        return None
    return (types.defauts_decouvrables if enveloppe else types.defauts_directs).get(nom)


# Arguments comparés par outil quand l'action attendue ne fixe pas compare_args, parce que les autres arguments
# n'ont aucun effet enregistré. give_discoverable_user_tool (banking_knowledge/tools.py, commit 033bf08) : seuls
# « tool_name » et « status: GIVEN » vont en base ; « arguments » n'est qu'une indication affichée au client
# (état en mémoire). Les actions attendues ne le fixent jamais. Constat du pilote, étape 2 (05/11) : 47 fausses
# alertes, toutes dues à ce seul argument (motif d, défaut de notre comparaison).
COMPARAISON_PAR_OUTIL = {"give_discoverable_user_tool": ("discoverable_tool_name",)}


def attendue_depuis_action(action: dict, types: Optional[TypesOutils] = None) -> Attendue:
    nom, args, enveloppe = _deballer(action["name"], action.get("arguments") or {})
    args = _completer(args, _defauts(types, nom, enveloppe))
    ca = action.get("compare_args")
    if ca is None and not enveloppe and nom in COMPARAISON_PAR_OUTIL:
        compare = COMPARAISON_PAR_OUTIL[nom]
    elif ca is None:
        compare = None
    elif enveloppe:
        # compare_args porte sur l'enveloppe (agent_tool_name / arguments)
        compare = None if "arguments" in ca else tuple(k for k in ca if k != "agent_tool_name")
    else:
        compare = tuple(ca)
    return Attendue(nom=nom, arguments=args, compare_args=compare)


def charger_taches_tau2(racine, domaine: str, types: Optional[TypesOutils] = None) -> dict:
    """{id de tache (str): [Attendue de l'agent]}. Actions « user » ecartees."""
    chemin = Path(racine) / "data" / "tau2" / "domains" / domaine / "tasks.json"
    brut = json.loads(chemin.read_text(encoding="utf-8"))
    taches = {}
    for t in brut:
        ec = t.get("evaluation_criteria") or {}
        actions = ec.get("actions") or []
        taches[str(t["id"])] = [
            attendue_depuis_action(a, types) for a in actions if a.get("requestor", "assistant") != "user"
        ]
    return taches


# ---------------------------------------------------------------------------
# tau-bench : parties enregistrees
# ---------------------------------------------------------------------------
def _messages_ranges(messages: list) -> list:
    if messages and all(m.get("turn_idx") is not None for m in messages):
        return sorted(messages, key=lambda m: m["turn_idx"])  # tri stable
    return list(messages)


_REFUS_CACHE: dict = {}


def _modele_vers_regex(modele: str):
    """'Error: Account {} not found.' -> regex (accolades doublees = litteral)."""
    morceaux, i, lit = [], 0, ""
    while i < len(modele):
        c = modele[i]
        if c == "{" and modele[i + 1 : i + 2] == "{":
            lit += "{"
            i += 2
        elif c == "}" and modele[i + 1 : i + 2] == "}":
            lit += "}"
            i += 2
        elif c == "{" and modele[i + 1 : i + 2] == "}":
            morceaux.append(re.escape(lit))
            morceaux.append(".*?")
            lit = ""
            i += 2
        else:
            lit += c
            i += 1
    morceaux.append(re.escape(lit))
    return re.compile("".join(morceaux), re.S)


def charger_refus_banque(chemin=None) -> dict:
    """{outil: [regex]} depuis banc/refus_banque.json (cache)."""
    chemin = Path(chemin) if chemin else CHEMIN_REFUS_BANQUE
    cle = str(chemin)
    if cle not in _REFUS_CACHE:
        data = json.loads(chemin.read_text(encoding="utf-8"))
        _REFUS_CACHE[cle] = {
            outil: [_modele_vers_regex(e["modele"]) for e in entrees] for outil, entrees in data["outils"].items()
        }
    return _REFUS_CACHE[cle]


def _refuse_tau2(rep: Optional[dict], nom: str = "", enveloppe: bool = False) -> bool:
    if not rep:
        return False
    if rep.get("error") or rep.get("execution_status") == "rejected":
        return True
    contenu = (rep.get("content") or "").strip().lstrip("\"'")
    if contenu.startswith(_PREFIXES_ERREUR):
        return True
    if CHEMIN_REFUS_BANQUE.is_file():
        table = charger_refus_banque()
        patrons = list(table.get(nom, ()))
        if enveloppe:
            patrons += table.get(ENVELOPPE_BANQUE, ())
        brut = (rep.get("content") or "").strip()
        return any(p.fullmatch(brut) for p in patrons)
    return False


# Outils GENERIC à effet, classés comme écritures par décision d'Otsoa (REGLE.md, section du 5 novembre, point 5 :
# D7, « donner un outil au client » = écriture réversible) : ils doivent être jugés contre les actions attendues.
# Constat du pilote, étape 2 (05/11) : 47 actions de ce type passaient en « autre », sans verdict.
ECRITURES_DECIDEES = frozenset({"give_discoverable_user_tool"})


def _kind_tau2(nom: str, types: TypesOutils, enveloppe: bool) -> str:
    if _DOUTE_RE.search(nom):
        return DOUTE
    if not enveloppe and nom in ECRITURES_DECIDEES:
        return ECRITURE
    table = types.decouvrables if enveloppe else types.directs
    typ = table.get(nom)
    if typ is None:
        # l'enveloppe est un outil WRITE : un outil sous-jacent inconnu reste une ecriture
        return ECRITURE if enveloppe else INCONNU
    if typ == "read":
        return LECTURE
    if typ == "write":
        return ECRITURE
    return AUTRE


def appels_tau2(messages: list, types: TypesOutils) -> list:
    reponses = {}
    for m in messages:
        if m.get("role") == "tool" and m.get("id") is not None:
            reponses.setdefault(m["id"], m)
    appels = []
    for m in _messages_ranges(messages):
        if m.get("role") != "assistant":
            continue
        for c in m.get("tool_calls") or []:
            if c.get("requestor", "assistant") == "user":
                continue
            nom, args, enveloppe = _deballer(c["name"], c.get("arguments") or {})
            kind = _kind_tau2(nom, types, enveloppe)
            args = _completer(args, _defauts(types, nom, enveloppe))
            rep = reponses.get(c.get("id"))
            contenu = rep.get("content") if rep else None
            appels.append(
                Appel(nom, args, kind, _refuse_tau2(rep, nom, enveloppe), None if contenu is None else str(contenu))
            )
    _marquer_paiements_sans_effet(appels, types.paiements_initiaux)
    return appels


def _reservation(resultat: Optional[str]) -> Optional[dict]:
    """La reservation renvoyee par un outil aviation (dict avec reservation_id et payment_history), sinon None."""
    if not resultat:
        return None
    try:
        d = json.loads(resultat)
    except ValueError:
        return None
    if isinstance(d, dict) and d.get("reservation_id") and isinstance(d.get("payment_history"), list):
        return d
    return None


def _marquer_paiements_sans_effet(appels: list, paiements_initiaux: dict) -> None:
    """Pose `ignorer` sur chaque ecriture reussie de PAIEMENT_CONDITIONNEL qui n'a enregistre aucun paiement : meme
    nombre d'entrees dans payment_history avant et apres. Avant = dernier etat de la reservation renvoye dans la partie,
    sinon l'etat initial ; inconnu = rien d'ignore (comparaison stricte)."""
    connus = dict(paiements_initiaux or {})
    for ap in appels:
        resa = None if ap.refuse else _reservation(ap.resultat)
        if resa is None:
            continue
        rid, apres = resa["reservation_id"], len(resa["payment_history"])
        avant = connus.get(rid)
        if ap.kind == ECRITURE and ap.nom in PAIEMENT_CONDITIONNEL and avant is not None and apres == avant:
            ap.ignorer = (PAIEMENT_CONDITIONNEL[ap.nom],)
        connus[rid] = apres


def _ligne(partie, tache, rang, banc, domaine, ap: Appel, verdict, modele, motif="") -> dict:
    return {
        "partie": partie,
        "tache": tache,
        "rang": rang,
        "banc": banc,
        "domaine": domaine,
        "outil": ap.nom,
        "arguments": json.dumps(ap.arguments, ensure_ascii=False, sort_keys=True),
        "kind": ap.kind,
        "verdict": verdict or "",
        "modele": modele or "",
        "motif": motif or "",
        "resultat": ap.resultat if ap.resultat is not None else "",
    }


def actions_partie_tau2(run: dict, taches: dict, types: TypesOutils, domaine: str, modele: Optional[str] = None) -> list:
    if run.get("messages") is None:
        raise ValueError(f"partie {run.get('id')}: pas de messages (mode full-duplex non gere)")
    tache = str(run["task_id"])
    attendues = taches.get(tache, [])
    appels = appels_tau2(run["messages"], types)
    verdicts = juger(appels, attendues)
    if any(ap.ignorer for ap in appels):
        stricts = juger([replace(ap, ignorer=()) for ap in appels], attendues)
    else:
        stricts = verdicts
    return [
        _ligne(str(run.get("id", "")), tache, i, "tau2", domaine, ap, verd, modele,
               MOTIF_PAIEMENT_SANS_EFFET if ap.ignorer and verd != strict else "")
        for i, (ap, (verd, _), (strict, _s)) in enumerate(zip(appels, verdicts, stricts))
    ]


# ---------------------------------------------------------------------------
# WorkBench
# ---------------------------------------------------------------------------
def parser_appel_workbench(chaine: str) -> tuple:
    """'email.delete_email.func(email_id="1")' -> ('email.delete_email', {'email_id': '1'}).
    Parse avec ast, jamais eval. Les valeurs sont passees par str(), comme le banc."""
    try:
        arbre = ast.parse(chaine.strip(), mode="eval")
    except SyntaxError as e:
        raise ValueError(f"appel illisible: {chaine!r}") from e
    appel = arbre.body
    if not isinstance(appel, ast.Call):
        raise ValueError(f"ce n'est pas un appel: {chaine!r}")
    if appel.args:
        raise ValueError(f"arguments positionnels non pris en charge: {chaine!r}")
    parties = []
    noeud = appel.func
    while isinstance(noeud, ast.Attribute):
        parties.append(noeud.attr)
        noeud = noeud.value
    if not isinstance(noeud, ast.Name):
        raise ValueError(f"appel non reconnu: {chaine!r}")
    parties.append(noeud.id)
    parties.reverse()
    if len(parties) >= 3 and parties[-1] == "func":
        parties = parties[:-1]
    args = {}
    for kw in appel.keywords:
        if kw.arg is None:
            raise ValueError(f"**kwargs non pris en charge: {chaine!r}")
        try:
            valeur = ast.literal_eval(kw.value)
        except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError) as e:
            raise ValueError(f"valeur non litterale pour {kw.arg}: {chaine!r}") from e
        args[kw.arg] = str(valeur)
    return ".".join(parties), args


def types_workbench(racine) -> dict:
    """{nom d'outil: 'write'|'read'} lu dans src/tools/toolkits.py (liste
    tools_with_side_effects = ecritures) et les decorateurs @tool des modules."""
    src = Path(racine) / "src" / "tools"
    noms = {}  # (module, fonction) -> nom d'outil
    for f in src.glob("*.py"):
        texte = f.read_text(encoding="utf-8")
        for nom_outil, fonction in re.findall(r'@tool\("([^"]+)"\)\s*\ndef (\w+)', texte):
            noms[(f.stem, fonction)] = nom_outil
    texte = (src / "toolkits.py").read_text(encoding="utf-8")
    ecr = re.search(r"tools_with_side_effects[^=]*=\s*\[(.*?)\]", texte, re.S)
    tous = re.search(r"all_tools[^=]*=\s*tools_with_side_effects\s*\+\s*\[(.*?)\]", texte, re.S)
    if not ecr or not tous:
        raise ValueError("toolkits.py : listes d'outils introuvables")

    def lire(bloc: str) -> list:
        return re.findall(r"^\s*(\w+)\.(\w+),", bloc, re.M)

    types = {}
    for mod, fonction in lire(tous.group(1)):
        types[noms[(mod, fonction)]] = "read"
    for mod, fonction in lire(ecr.group(1)):
        types[noms[(mod, fonction)]] = "write"
    return types


def charger_taches_workbench(racine) -> dict:
    """{'email:12': [Attendue]} : colonne `outcome`, chaines parsees avec ast.
    Identifiant = prefixe du fichier + ':' + numero de ligne (0 = premiere tache)."""
    dossier = Path(racine) / "data" / "processed" / "tasks_and_outcomes"
    taches = {}
    for chemin in sorted(dossier.glob("*_tasks_and_outcomes.csv")):
        prefixe = chemin.name[: -len("_tasks_and_outcomes.csv")]
        with open(chemin, newline="", encoding="utf-8") as fh:
            for i, ligne in enumerate(csv.DictReader(fh)):
                sorties = ast.literal_eval(ligne["outcome"])
                attendues = []
                for chaine in sorties:
                    nom, args = parser_appel_workbench(chaine)
                    attendues.append(Attendue(nom=nom, arguments=args))
                taches[f"{prefixe}:{i}"] = attendues
    return taches


_ID8 = re.compile(r"^\d{8}$")


def refuse_workbench(nom: str, resultat: Optional[str]) -> bool:
    if resultat is None:
        return False
    r = str(resultat).strip()
    if "successfully" in r:
        return False
    if nom in ("calendar.create_event", "project_management.create_task", "customer_relationship_manager.add_customer"):
        return not _ID8.match(r)
    if nom == "analytics.create_plot":
        return not r.startswith("plots/")
    return True


# Champs de texte libre, par outil WorkBench. Justification (lue dans src/tools/*.py du
# commit 49c7dfd) : ces valeurs sont stockees telles quelles, sans liste de valeurs valides
# ni normalisation ; une reformulation y est une difference de texte, pas de decision.
#   email.send_email    : subject, body (seul `recipient` est valide : adresse)
#   email.reply_email   : body
#   calendar.create_event : event_name (participant_email normalise, start/duree structures)
#   project_management.create_task : task_name (assignee, list, board valides par liste)
#   customer_relationship_manager.add_customer : customer_name, notes
# Exclus volontairement : identifiants, adresses, dates, durees, statuts, boards, listes.
CHAMPS_LIBRES_WORKBENCH = {
    "email.send_email": ("subject", "body"),
    "email.reply_email": ("body",),
    "calendar.create_event": ("event_name",),
    "project_management.create_task": ("task_name",),
    "customer_relationship_manager.add_customer": ("customer_name", "notes"),
}
# update_* : `new_value` est du texte libre seulement quand `field` designe un champ libre.
CHAMPS_LIBRES_MAJ_WORKBENCH = {
    "calendar.update_event": ("event_name",),
    "project_management.update_task": ("task_name",),
    "customer_relationship_manager.update_customer": ("customer_name", "notes"),
}


def _champs_libres(nom: str, arguments: dict) -> tuple:
    libres = tuple(CHAMPS_LIBRES_WORKBENCH.get(nom, ()))
    if arguments.get("field") in CHAMPS_LIBRES_MAJ_WORKBENCH.get(nom, ()):
        libres += ("new_value",)
    return libres


def motif_fausse_workbench(nom: str, arguments: dict, attendues: list) -> str:
    """« texte libre seulement » si une attendue du meme outil ne differe que par des
    champs libres presents des deux cotes ; « autre » sinon."""
    libres = _champs_libres(nom, arguments)
    if not libres:
        return MOTIF_AUTRE
    for a in attendues:
        if a.nom != nom:
            continue
        if any((k in arguments) != (k in a.arguments) for k in libres):
            continue
        reste_agent = {k: val for k, val in arguments.items() if k not in libres}
        reste_att = {k: val for k, val in a.arguments.items() if k not in libres}
        if normaliser(reste_agent) == normaliser(reste_att):
            return MOTIF_TEXTE_LIBRE
    return MOTIF_AUTRE


def actions_partie_workbench(game: dict, taches: dict, types: dict, domaine: Optional[str] = None) -> list:
    tache = game["tache"]
    attendues = taches.get(tache, [])
    domaine = domaine or tache.split(":")[0]
    appels, resultats = [], []
    for entree in game.get("appels", []):
        chaine, resultat = (entree, None) if isinstance(entree, str) else (entree["appel"], entree.get("resultat"))
        try:
            nom, args = parser_appel_workbench(chaine)
            typ = types.get(nom)
            kind = ECRITURE if typ == "write" else LECTURE if typ == "read" else INCONNU
            appels.append(
                Appel(nom, args, kind, kind == ECRITURE and refuse_workbench(nom, resultat),
                      None if resultat is None else str(resultat))
            )
        except ValueError:
            appels.append(Appel(chaine, {}, INCONNU, False))
    verdicts = juger(appels, attendues)
    return [
        _ligne(
            str(game.get("id", "")), tache, i, "workbench", domaine, ap, verd, game.get("modele"),
            motif_fausse_workbench(ap.nom, ap.arguments, attendues) if verd == FAUSSE else "",
        )
        for i, (ap, (verd, _)) in enumerate(zip(appels, verdicts))
    ]


# ---------------------------------------------------------------------------
# WorkBench : fichiers ecrits par le pilote (src/evals/inference.py)
# ---------------------------------------------------------------------------
_OBSERVATION_SANS_OUTIL = ("Final Answer", "__parse_error__")  # FINAL_ANSWER et PARSE_ERROR du banc


def charger_textes_workbench(racine) -> dict:
    """{'email:12': texte de la consigne}, memes identifiants que charger_taches_workbench."""
    dossier = Path(racine) / "data" / "processed" / "tasks_and_outcomes"
    textes = {}
    for chemin in sorted(dossier.glob("*_tasks_and_outcomes.csv")):
        prefixe = chemin.name[: -len("_tasks_and_outcomes.csv")]
        with open(chemin, newline="", encoding="utf-8") as fh:
            for i, ligne in enumerate(csv.DictReader(fh)):
                textes[f"{prefixe}:{i}"] = ligne["task"]
    return textes


def _modele_depuis_nom(stem: str) -> str:
    m = re.match(r"^(.*)_(?:all|domains)_\d{4}-\d\d-\d\d_\d\d-\d\d-\d\d$", stem)
    return m.group(1) if m else stem


def _resoudre_tache(texte: str, i: int, textes: dict, prefixe: Optional[str], n_lignes: Optional[int] = None) -> str:
    """Identifiant de la tache d'apres sa consigne. Si plusieurs taches ont ce texte : la ligne i ne la designe que
    dans un fichier de domaine complet (le lanceur et le pilote ecrivent une seule tache par fichier : i vaut 0) ;
    sinon le domaine du fichier ; s'il reste plusieurs candidats, refus plutot qu'un identifiant devine, qui serait
    faux dans actions.csv (revue « ultra » du 06/11, constat 5 ; aucun texte partage parmi les 690 taches au 06/11)."""
    candidats = sorted(k for k, t in textes.items() if t == texte)
    if not candidats:
        raise ValueError(f"consigne inconnue du jeu de taches WorkBench: {texte[:80]!r}")
    if len(candidats) == 1:
        return candidats[0]
    if prefixe:
        direct = f"{prefixe}:{i}"
        if direct in candidats and (n_lignes is None or n_lignes > 1):
            return direct
        du_domaine = [k for k in candidats if k.split(":")[0] == prefixe or prefixe.endswith("_" + k.split(":")[0])]
        if len(du_domaine) == 1:
            return du_domaine[0]
        candidats = du_domaine or candidats
    domaines = sorted({k.split(":")[0] for k in candidats})
    raise ValueError(f"consigne partagee par {len(candidats)} taches WorkBench ({', '.join(domaines)}) : identifiant "
                     f"ambigu, refus plutot qu'un identifiant devine")


def parties_depuis_pilote_workbench(chemin_csv, textes: dict) -> Iterator[dict]:
    """Convertit `<modele>_all_<horodatage>.csv` (+ `_meta.json`, `_traces.json`) en parties
    internes {id, tache, modele, appels:[{appel, resultat}], erreur}.

    - `function_calls` : liste Python ecrite par pandas ; une chaine par outil appele.
    - `_traces.json` : pour chaque tache, `steps` ; les etapes d'outil (action ni « Final Answer »
      ni « __parse_error__ ») sont dans le meme ordre que function_calls, et leur
      `observation` est le resultat de l'outil. Si le nombre d'etapes ne coincide pas, ou si
      les traces manquent, `resultat` vaut None (aucun refus ne peut etre conclu)."""
    chemin = Path(chemin_csv)
    base = str(chemin)[: -len(".csv")]
    meta = None
    if Path(base + "_meta.json").is_file():
        meta = json.loads(Path(base + "_meta.json").read_text(encoding="utf-8"))
    modele = (meta or {}).get("model_name") or _modele_depuis_nom(chemin.stem)
    prefixe = None
    tp = (meta or {}).get("tasks_path")
    if tp:
        nom = Path(tp).name
        if nom.endswith("_tasks_and_outcomes.csv"):
            prefixe = nom[: -len("_tasks_and_outcomes.csv")]
    traces = None
    if Path(base + "_traces.json").is_file():
        traces = json.loads(Path(base + "_traces.json").read_text(encoding="utf-8"))
    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    with open(chemin, newline="", encoding="utf-8") as fh:
        lignes = list(csv.DictReader(fh))
    for i, ligne in enumerate(lignes):
        try:
            appels = ast.literal_eval(ligne["function_calls"]) if ligne["function_calls"].strip() else []
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"{chemin.name} ligne {i}: function_calls illisible") from e
        if not isinstance(appels, list) or not all(isinstance(a, str) for a in appels):
            raise ValueError(f"{chemin.name} ligne {i}: function_calls n'est pas une liste de chaines")
        observations: Optional[list] = None
        if traces is not None and i < len(traces) and traces[i].get("task") == ligne["task"]:
            outils = [st for st in traces[i].get("steps", []) if st.get("action") not in _OBSERVATION_SANS_OUTIL]
            if len(outils) == len(appels):
                observations = [st.get("observation") for st in outils]
        yield {
            "id": f"{chemin.stem}:{i}",
            "tache": _resoudre_tache(ligne["task"], i, textes, prefixe, len(lignes)),
            "modele": modele,
            "appels": [
                {"appel": a, "resultat": observations[k] if observations is not None else None}
                for k, a in enumerate(appels)
            ],
            "erreur": ligne.get("error", ""),
        }


# ---------------------------------------------------------------------------
# Dossier de parties
# ---------------------------------------------------------------------------
def _domaine_depuis_chemin(chemin: Path) -> Optional[str]:
    for p in reversed(chemin.parts):
        if p in DOMAINES_TAU2:
            return p
    return None


def actions_dossier(dossier, tau2=None, workbench=None, domaine=None) -> Iterator[dict]:
    """Parcourt les .json d'un dossier (recursivement). Reconnait :
    - un fichier de resultats tau-bench ({"info", "tasks", "simulations"}) ;
    - une simulation seule ({"messages", "task_id"}), domaine donne ou deduit
      du chemin ;
    - une partie WorkBench ({"tache", "appels"}) ou une liste de telles parties."""
    cache_types: dict = {}
    cache_taches: dict = {}

    def tau(dom: str):
        if tau2 is None:
            raise ValueError("racine du clone tau-bench requise (--tau2)")
        if dom not in cache_types:
            cache_types[dom] = types_tau2(tau2, dom)
            cache_taches[dom] = charger_taches_tau2(tau2, dom, cache_types[dom])
        return cache_types[dom], cache_taches[dom]

    wb_cache: dict = {}

    def wb():
        if workbench is None:
            raise ValueError("racine du clone WorkBench requise (--workbench)")
        if not wb_cache:
            wb_cache["types"] = types_workbench(workbench)
            wb_cache["taches"] = charger_taches_workbench(workbench)
            wb_cache["textes"] = charger_textes_workbench(workbench)
        return wb_cache

    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))
    chemins = sorted(p for p in Path(dossier).rglob("*") if p.suffix in (".json", ".csv") and p.is_file())
    for chemin in chemins:
        if chemin.name.endswith(("_meta.json", "_traces.json")):
            continue  # annexes du pilote WorkBench, lues avec leur csv
        if chemin.suffix == ".csv":
            with open(chemin, newline="", encoding="utf-8") as fh:
                entete = next(csv.reader(fh), [])
            if "function_calls" not in entete:
                continue
            w = wb()
            for game in parties_depuis_pilote_workbench(chemin, w["textes"]):
                yield from actions_partie_workbench(game, w["taches"], w["types"])
            continue
        data = json.loads(chemin.read_text(encoding="utf-8"))
        elements = data if isinstance(data, list) else [data]
        for el in elements:
            if "appels" in el and "tache" in el:
                w = wb()
                yield from actions_partie_workbench(el, w["taches"], w["types"])
            elif "simulations" in el:
                info = el.get("info") or {}
                dom = (info.get("environment_info") or {}).get("domain_name") or domaine
                modele = (info.get("agent_info") or {}).get("llm")
                if dom is None:
                    raise ValueError(f"{chemin}: domaine introuvable")
                types, taches = tau(dom)
                for run in el["simulations"]:
                    yield from actions_partie_tau2(run, taches, types, dom, modele)
            elif "messages" in el and "task_id" in el:
                dom = domaine or _domaine_depuis_chemin(chemin)
                if dom is None:
                    raise ValueError(f"{chemin}: domaine inconnu (option --domaine)")
                types, taches = tau(dom)
                yield from actions_partie_tau2(el, taches, types, dom, el.get("modele"))
            else:
                raise ValueError(f"{chemin}: format de partie non reconnu")


def _ecrire_refus(racine, sortie=None) -> Path:
    sortie = Path(sortie) if sortie else CHEMIN_REFUS_BANQUE
    sortie.write_text(json.dumps(extraire_refus_banque(racine), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return sortie


if __name__ == "__main__":
    # python banc/verdicts.py CLONE_TAU2 : regenere banc/refus_banque.json
    if len(sys.argv) != 2:
        sys.exit("usage: python banc/verdicts.py RACINE_CLONE_TAU2  (regenere refus_banque.json)")
    print(_ecrire_refus(sys.argv[1]))
