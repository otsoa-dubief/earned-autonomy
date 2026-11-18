"""Les entrées du rejeu (PLAN_EXPERIENCE.md, 5.2), lues dans un dossier de sortie au format du pilote
(`pilote/etape2/<horodatage>/`).

1. Les parties : identifiant, environnement, modèle, tâche, numéro de passage, vague, heure de début, statut technique,
   réussite de la tâche (`cout.json`, `parties/`, `reussite.csv`).
2. Les actions : `actions_typees.csv` (partie, rang, kind, outil, verdict après `marquer_doublons_sans_effet`, type,
   enjeu, plafonnée, montant).
3. Les décisions sur les alertes : `decisions.csv` de chaque vague (`banc/relecture/decisions.py`), et les décisions
   d'Otsoa, qui l'emportent sur les cas qu'il a relus (`banc/relecture/accord.py`, `decisions_retenues`), jointes par
   l'identifiant d'alerte (`banc/relecture/fiches.py`, `alerte_id`, ou la correspondance d'`alertes.json`).
4. Les tâches retirées : alertes levées pour le motif a, et liste explicite (audit des tâches sans alerte, 4.5).
5. L'appartenance de chaque tâche (calibration ou confirmation), lue dans le `partage.json` du tirage public
   (`banc/tirage/tirage_public.py`, 3.4).
6. La configuration figée : `config_rejeu`.

Jointure des parties et des actions (format du pilote, voir CHOIX_PHASE1.md) : la colonne `partie` des actions porte
l'identifiant de simulation de τ-bench (`parties/tau2-<id>/results.json`) ou `<fichier>:<ligne>` pour WorkBench
(`parties/workbench-<id>/<fichier>.csv`, comme `verdicts.parties_depuis_pilote_workbench`).
"""
from __future__ import annotations

import csv
import glob
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Iterable, Optional

from . import RACINE

for _d in (os.path.join(RACINE, "banc"), os.path.join(RACINE, "banc", "relecture"),
           os.path.join(RACINE, "banc", "tirage")):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import accord  # noqa: E402  (banc/relecture/accord.py)
import decisions as registre_decisions  # noqa: E402  (banc/relecture/decisions.py)
import fiches  # noqa: E402  (banc/relecture/fiches.py)
import tirage_public  # noqa: E402  (banc/tirage/tirage_public.py)
import verdicts  # noqa: E402  (banc/verdicts.py)

ENV_DE_DOMAINE = {"airline": "aviation", "retail": "commerce", "banking_knowledge": "banque"}
CHEMIN_DEVELOPPEMENT = os.path.join(RACINE, "banc", "tirage", "developpement.json")
CONFIRMEE, LEVEE = registre_decisions.CONFIRMEE, registre_decisions.LEVEE
VERDICTS_ALERTE = fiches.VERDICTS_ALERTE  # fausse, doublon, refusée (pas le doublon sans effet)
MOTIF_TACHE_DEFECTUEUSE = "a"


class EntreeInvalide(ValueError):
    pass


# --------------------------------------------------------------------------
# Petits outils
# --------------------------------------------------------------------------
def environnement_action(banc: str, domaine: str) -> str:
    return "WorkBench" if banc == "workbench" else ENV_DE_DOMAINE.get(domaine, domaine)


def strate(environnement: str, tache: str) -> str:
    """Strate du tirage public et du rééchantillonnage : l'environnement, et le fichier pour WorkBench
    (tirage_public.strates ; 5.5, point 2.i)."""
    if environnement == "WorkBench":
        return f"WorkBench:{str(tache).split(':')[0]}"
    return environnement


def modele_court(m: str) -> str:
    return (m or "").split("/")[-1]


def _vrai(x) -> bool:
    return str(x).strip().lower() in ("true", "1", "oui", "vrai")


# --------------------------------------------------------------------------
# 1. Les parties
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Partie:
    id: str              # identifiant porté par les actions
    dossier: str         # nom du dossier de la partie (tau2-aviation-haiku-1…)
    environnement: str
    modele: str          # claude-haiku-5-5…
    tache: str
    strate: str
    passage: int
    vague: str
    debut: str
    statut_ok: bool      # statut technique ; False : partie en échec technique, retirée (5.5, point 1)
    terminaison: str     # raison d'arrêt de τ-bench (max_steps : arrêt par les 100 tours, gardée)
    reussie: Optional[bool]
    statut_lanceur: str = ""   # lanceur de l'expérience (banc/CHOIX_LANCEUR.md, choix 14) : terminée, arrêtée…
    tentative: int = 1         # numéro de la tentative gardée (2 : relance « -t2 », choix 15)


def _parties_tau2(chemin: str) -> list:
    with open(os.path.join(chemin, "results.json"), encoding="utf-8") as f:
        sims = json.load(f)["simulations"]
    if len(sims) != 1:
        raise EntreeInvalide(f"{chemin} : {len(sims)} simulations (une attendue par dossier, format du pilote)")
    s = sims[0]
    return [(str(s["id"]), str(s.get("task_id", "")), str(s.get("start_time") or ""),
             str(s.get("termination_reason") or ""))]


def _parties_workbench(chemin: str) -> list:
    fichiers = [c for c in glob.glob(os.path.join(chemin, "*.csv"))]
    if len(fichiers) != 1:
        raise EntreeInvalide(f"{chemin} : {len(fichiers)} fichiers de prédictions (un attendu)")
    stem = os.path.basename(fichiers[0])[: -len(".csv")]
    csv.field_size_limit(min(sys.maxsize, 2 ** 31 - 1))
    with open(fichiers[0], newline="", encoding="utf-8") as fh:
        n = sum(1 for _ in csv.DictReader(fh))
    if n != 1:
        raise EntreeInvalide(f"{chemin} : {n} tâches dans le fichier (une attendue par dossier, format du pilote)")
    horo = stem.rsplit("_all_", 1)[-1]  # 2026-11-05_07-54-15
    debut = horo[:10] + "T" + horo[11:].replace("-", ":") if len(horo) == 19 else ""
    return [(f"{stem}:0", "", debut, "")]


def charger_parties(dossier: str, vague: Optional[str] = None) -> list:
    """Les parties d'un dossier de sortie au format du pilote, triées par identifiant."""
    with open(os.path.join(dossier, "cout.json"), encoding="utf-8") as f:
        cout = json.load(f)
    meta = {p["id"]: p for p in cout["parties"]}
    reussite = {}
    chemin_reussite = os.path.join(dossier, "reussite.csv")
    if os.path.exists(chemin_reussite):
        with open(chemin_reussite, newline="", encoding="utf-8") as fh:
            reussite = {l["partie"]: l["reussie"] == "oui" for l in csv.DictReader(fh)}
    vague = vague or f"pilote-{cout.get('etape', '?')}"
    brutes = []
    for chemin in sorted(glob.glob(os.path.join(dossier, "parties", "*"))):
        nom = os.path.basename(chemin)
        banc, pid = nom.split("-", 1)
        if pid not in meta:
            raise EntreeInvalide(f"partie {nom} absente de cout.json")
        m = meta[pid]
        if banc == "tau2":
            elements = _parties_tau2(chemin)
        elif banc == "workbench":
            elements = _parties_workbench(chemin)
        else:
            raise EntreeInvalide(f"dossier de partie inconnu : {nom}")
        for ident, tache_sim, debut, term in elements:
            tache = str(m["tache"])
            if tache_sim and tache_sim != tache:
                raise EntreeInvalide(f"{nom} : tâche {tache_sim} dans la partie, {tache} dans cout.json")
            env = m["env"]
            brutes.append(dict(id=ident, dossier=nom, environnement=env, modele=modele_court(m.get("modele", "")),
                               tache=tache, strate=strate(env, tache), passage=m.get("passage"),
                               vague=str(m.get("vague") or vague), debut=debut, statut_ok=bool(m.get("ok")),
                               terminaison=term or str(m.get("terminaison") or ""), reussie=reussite.get(nom),
                               statut_lanceur=str(m.get("statut") or ""), tentative=int(m.get("tentative") or 1)))
    # Numéro de passage absent du format du pilote : rang par heure de début parmi les parties de même
    # (environnement, modèle, tâche) (CHOIX_PHASE1.md).
    groupes: dict = {}
    for b in brutes:
        groupes.setdefault((b["environnement"], b["modele"], b["tache"]), []).append(b)
    for g in groupes.values():
        for i, b in enumerate(sorted(g, key=lambda x: (x["debut"], x["id"]))):
            if b["passage"] is None:
                b["passage"] = i + 1
    ids = [b["id"] for b in brutes]
    if len(ids) != len(set(ids)):
        raise EntreeInvalide("identifiant de partie en double")
    return sorted((Partie(**b) for b in brutes), key=lambda p: p.id)


# --------------------------------------------------------------------------
# 2. Les actions
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Action:
    partie: str
    tache: str
    rang: int
    banc: str
    domaine: str
    outil: str
    kind: str
    verdict: str
    motif: str
    type: str
    enjeu: str
    plafonnee: bool
    montant: Optional[float]

    @property
    def environnement(self) -> str:
        return environnement_action(self.banc, self.domaine)

    def ligne(self) -> dict:
        """Les champs qu'attend fiches.alerte_id."""
        return {"banc": self.banc, "domaine": self.domaine, "tache": self.tache, "partie": self.partie,
                "rang": self.rang}


def lire_actions(chemin: str) -> list:
    """Les lignes de actions_typees.csv, sans les champs volumineux (arguments, résultat)."""
    csv.field_size_limit(min(sys.maxsize, 2 ** 31 - 1))
    sortie = []
    with open(chemin, newline="", encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            m = (l.get("montant") or "").strip()
            sortie.append(Action(partie=l["partie"], tache=str(l["tache"]), rang=int(l["rang"]), banc=l["banc"],
                                 domaine=l["domaine"], outil=l["outil"], kind=l["kind"], verdict=l.get("verdict") or "",
                                 motif=l.get("motif") or "", type=l.get("type") or "", enjeu=l.get("enjeu") or "",
                                 plafonnee=_vrai(l.get("plafonnee")), montant=float(m) if m else None))
    return sortie


def grouper_actions(actions: Iterable[Action], parties: list) -> dict:
    """{partie: [actions triées par rang]} ; toute action doit appartenir à une partie connue, de même tâche."""
    par_id = {p.id: p for p in parties}
    out: dict = {p.id: [] for p in parties}
    for a in actions:
        p = par_id.get(a.partie)
        if p is None:
            raise EntreeInvalide(f"action d'une partie inconnue : {a.partie}")
        if a.tache != p.tache or a.environnement != p.environnement:
            raise EntreeInvalide(f"action {a.partie}/{a.rang} : tâche ou environnement différents de la partie")
        out[a.partie].append(a)
    for pid, l in out.items():
        l.sort(key=lambda a: a.rang)
        rangs = [a.rang for a in l]
        if len(rangs) != len(set(rangs)):
            raise EntreeInvalide(f"partie {pid} : rang en double")
    return out


# --------------------------------------------------------------------------
# 3. Les décisions sur les alertes
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class VagueRelecture:
    nom: str
    decisions: str                        # decisions.csv (registre de Claude)
    alertes: Optional[str] = None         # alertes.json : correspondance identifiant -> (partie, rang)
    bilan_otsoa: Optional[str] = None     # sortie JSON d'accord.py (decisions_otsoa, desaccord_persistant)


def relecture_du_dossier(dossier: str, nom: str) -> Optional[VagueRelecture]:
    rel = os.path.join(dossier, "relecture")
    dec = os.path.join(rel, "decisions.csv")
    if not os.path.exists(dec):
        return None
    al = os.path.join(rel, "alertes.json")
    bilan = os.path.join(rel, "accord.json")
    return VagueRelecture(nom, dec, al if os.path.exists(al) else None, bilan if os.path.exists(bilan) else None)


@dataclass(frozen=True)
class DecisionRetenue:
    alerte_id: str
    decision: str        # confirmée ou levée
    motif: str           # a, b, c, d, ou "" (confirmée, ou levée par Otsoa sans motif de Claude)
    vague: str
    par_otsoa: bool


@dataclass
class Jointure:
    alertes: dict = field(default_factory=dict)        # (partie, rang) -> alerte_id
    decisions: dict = field(default_factory=dict)      # alerte_id -> DecisionRetenue
    vague_alerte: dict = field(default_factory=dict)   # alerte_id -> vague
    obsoletes: list = field(default_factory=list)      # décisions sur des actions qui ne sont plus des alertes
    sans_decision: list = field(default_factory=list)  # alertes sans décision (option manquante="confirmee")
    desaccord_persistant: dict = field(default_factory=dict)  # vague -> bool
    decisions_otsoa: dict = field(default_factory=dict)       # alerte_id -> décision d'Otsoa
    conclusions: dict = field(default_factory=dict)           # vague -> conclusion d'accord.py (None : pas de bilan)


def est_alerte(a: Action) -> bool:
    return a.kind == verdicts.ECRITURE and a.verdict in VERDICTS_ALERTE


def joindre_decisions(actions_par_partie: dict, vagues: Iterable[VagueRelecture],
                      manquante: str = "erreur") -> Jointure:
    """Joint chaque alerte à sa décision retenue (celle de Claude, ou celle d'Otsoa sur les cas qu'il a relus).

    manquante : « erreur » (défaut : le registre doit être complet, Claude relit toutes les alertes) ou « confirmee »
    (pire cas : une alerte sans décision reste une erreur, essais seulement)."""
    if manquante not in ("erreur", "confirmee"):
        raise ValueError(manquante)
    j = Jointure()
    retenues, registres, inverse = {}, {}, {}
    for v in vagues:
        reg = registre_decisions.lire(v.decisions)
        otsoa, persistant, conclusion = {}, False, None
        if v.bilan_otsoa:
            with open(v.bilan_otsoa, encoding="utf-8") as f:
                bilan = json.load(f)
            otsoa = {k: registre_decisions.normaliser_decision(x) or x
                     for k, x in bilan.get("decisions_otsoa", {}).items()}
            persistant = bool(bilan.get("desaccord_persistant", False))
            conclusion = bilan.get("conclusion")
        j.desaccord_persistant[v.nom] = persistant
        j.conclusions[v.nom] = conclusion
        for aid, dec in accord.decisions_retenues(reg, otsoa).items():
            if aid in retenues:
                raise EntreeInvalide(f"alerte {aid} décidée dans deux vagues")
            retenues[aid] = (dec, v.nom, aid in otsoa)
            registres[aid] = reg.get(aid)
        j.decisions_otsoa.update(otsoa)
        if v.alertes:
            with open(v.alertes, encoding="utf-8") as f:
                for a in json.load(f):
                    inverse[(a["partie"], int(a["rang"]))] = a["id"]
    utilisees = set()
    for pid, actions in actions_par_partie.items():
        for a in actions:
            if not est_alerte(a):
                continue
            aid = inverse.get((a.partie, a.rang)) or fiches.alerte_id(a.ligne())
            j.alertes[(a.partie, a.rang)] = aid
            if aid not in retenues:
                if manquante == "erreur":
                    raise EntreeInvalide(f"alerte {aid} ({a.partie}, rang {a.rang}) sans décision")
                j.sans_decision.append(aid)
                j.decisions[aid] = DecisionRetenue(aid, CONFIRMEE, "", "", False)
                continue
            dec, vague, par_otsoa = retenues[aid]
            reg = registres[aid] or {}
            motif = reg.get("motif", "") if (dec == LEVEE and reg.get("decision") == LEVEE) else ""
            j.decisions[aid] = DecisionRetenue(aid, dec, motif, vague, par_otsoa)
            j.vague_alerte[aid] = vague
            utilisees.add(aid)
    j.obsoletes = sorted(set(retenues) - utilisees)
    return j


def appliquer_oppositions(actions_par_partie: dict, jointure: Jointure, oppositions: Iterable = ()) -> list:
    """Oppositions d'Otsoa aux retraits du motif a (plan, 4.5 ; relecture C13, P9) : une tâche visée n'est pas
    retirée ; ses alertes levées pour le motif a deviennent des erreurs confirmées, par décision d'Otsoa. Rend les
    alertes concernées."""
    gardees = {(str(e), str(t)) for e, t in oppositions}
    touchees = []
    for actions in actions_par_partie.values():
        for a in actions:
            if (a.environnement, str(a.tache)) not in gardees:
                continue
            aid = jointure.alertes.get((a.partie, a.rang))
            d = jointure.decisions.get(aid) if aid else None
            if d and d.decision == LEVEE and d.motif == MOTIF_TACHE_DEFECTUEUSE:
                jointure.decisions[aid] = DecisionRetenue(aid, CONFIRMEE, "", d.vague, True)
                touchees.append(aid)
    return sorted(set(touchees))


def taches_retirees_par_motif_a(actions_par_partie: dict, jointure: Jointure) -> dict:
    """{(environnement, tâche): raison} pour chaque alerte levée pour le motif a (4.5 ; 5.4)."""
    out = {}
    for actions in actions_par_partie.values():
        for a in actions:
            aid = jointure.alertes.get((a.partie, a.rang))
            d = jointure.decisions.get(aid) if aid else None
            if d and d.decision == LEVEE and d.motif == MOTIF_TACHE_DEFECTUEUSE:
                out[(a.environnement, a.tache)] = f"alerte {aid} levée pour le motif a (tâche défectueuse)"
    return out


# --------------------------------------------------------------------------
# 5. L'appartenance des tâches
# --------------------------------------------------------------------------
def appartenance_depuis_partage(partage: dict) -> dict:
    """{(strate, tâche): « calibration » | « confirmation »} ; chaque tâche dans un seul jeu."""
    out = {}
    for jeu in ("calibration", "confirmation"):
        for s, ids in partage[jeu].items():
            for t in ids:
                if (s, t) in out:
                    raise EntreeInvalide(f"tâche {t} ({s}) dans les deux jeux")
                out[(s, str(t))] = jeu
    return out


def charger_partage(chemin: str) -> dict:
    with open(chemin, encoding="utf-8") as f:
        return appartenance_depuis_partage(json.load(f))


def partage_factice(taches_par_env: dict, graine_hex: str) -> dict:
    """Partage calculé par tirage_public.partager, avec une graine donnée : pour les essais sur des tâches de
    développement seulement (le vrai partage n'existe qu'après le gel, 3.4)."""
    return tirage_public.partager(taches_par_env, bytes.fromhex(graine_hex))


def charger_developpement(chemin: str = CHEMIN_DEVELOPPEMENT) -> set:
    with open(chemin, encoding="utf-8") as f:
        d = json.load(f)
    return {(env, str(t)) for env, ids in d.items() for t in ids}


# --------------------------------------------------------------------------
# Tout ensemble
# --------------------------------------------------------------------------
@dataclass
class Entrees:
    parties: list
    actions: dict
    jointure: Jointure
    taches_retirees: dict
    appartenance: dict
    developpement: set

    def partie(self, pid: str) -> Partie:
        return self._index[pid]

    def __post_init__(self):
        self._index = {p.id: p for p in self.parties}

    def jeu_de(self, p: Partie) -> str:
        """« developpement », « calibration », « confirmation » ou « non attribuée »."""
        if (p.environnement, p.tache) in self.developpement:
            return "developpement"
        return self.appartenance.get((p.strate, p.tache), "non attribuée")

    def retiree(self, p: Partie) -> bool:
        return (p.environnement, p.tache) in self.taches_retirees


def charger_entrees_vagues(dossiers: list, vagues: list, taches_retirees: Iterable = (),
                           developpement: Optional[set] = None, manquante: str = "erreur",
                           oppositions: Iterable = ()) -> Entrees:
    """Les dossiers des vagues du lanceur (`experience/vague1/…`, `experience/vague2/…`), réunis en une seule entrée
    (phase 4) : parties gardées de chaque dossier (`parties/` ; les tentatives exclues, interrompues ou relancées sont
    dans `ecartees/` et ne sont pas lues), actions, et relectures de chaque vague (une `VagueRelecture` par vague, nommée
    comme le champ `vague` des parties : « 1 », « 2 »). Une partie gardée dans deux vagues est refusée."""
    parties, actions = [], []
    for d in dossiers:
        parties += charger_parties(d)
        actions += lire_actions(os.path.join(d, "actions_typees.csv"))
    ids = [p.id for p in parties]
    if len(ids) != len(set(ids)):
        doubles = sorted({i for i in ids if ids.count(i) > 1})
        raise EntreeInvalide(f"partie gardée dans deux vagues : {doubles[:5]}")
    parties = sorted(parties, key=lambda p: p.id)
    groupees = grouper_actions(actions, parties)
    jointure = joindre_decisions(groupees, vagues, manquante)
    retirees = fusionner_retirees(groupees, jointure, taches_retirees, oppositions)
    dev = charger_developpement() if developpement is None else set(developpement)
    return Entrees(parties, groupees, jointure, retirees, {}, dev)


def fusionner_retirees(actions, jointure, taches_retirees, oppositions: Iterable = ()) -> dict:
    """{(environnement, tâche): raison} : motifs a (hors oppositions d'Otsoa), puis la liste explicite (liste ou dict),
    sans écraser un motif a."""
    appliquer_oppositions(actions, jointure, oppositions)
    retirees = dict(taches_retirees_par_motif_a(actions, jointure))
    explicites = taches_retirees.items() if isinstance(taches_retirees, dict) else \
        ((t, "liste des tâches retirées") for t in taches_retirees)
    for cle, raison in explicites:
        retirees.setdefault((cle[0], str(cle[1])), raison)
    return retirees


def bilan_lanceur(dossiers: list) -> dict:
    """Ce que disent les `cout.json` du lanceur (banc/CHOIX_LANCEUR.md, choix 14, 15 et 18) : tentatives par statut,
    exclusions et leurs motifs, relances (tentative 2 ou plus), parties gardées par vague."""
    out = dict(tentatives={}, exclues={}, exclues_par_configuration={}, relances=0, gardees_par_vague={})
    for d in dossiers:
        with open(os.path.join(d, "cout.json"), encoding="utf-8") as f:
            cout = json.load(f)
        for l in cout.get("parties", []):
            st = str(l.get("statut") or ("gardée" if l.get("ok") else "non gardée"))
            out["tentatives"][st] = out["tentatives"].get(st, 0) + 1
            if l.get("exclue"):
                m = str(l.get("motif_exclusion") or "?")
                out["exclues"][m] = out["exclues"].get(m, 0) + 1
                cfg = out["exclues_par_configuration"].setdefault(f"{l.get('env')}/{l.get('modele')}", {})
                cfg[m] = cfg.get(m, 0) + 1   # publié par configuration (plan, 5.5, point 1 ; relecture C13, P7)
            if int(l.get("tentative") or 1) >= 2:
                out["relances"] += 1
            if l.get("ok"):
                v = str(l.get("vague") or "?")
                out["gardees_par_vague"][v] = out["gardees_par_vague"].get(v, 0) + 1
    return out


def charger_entrees(dossier: str, vagues: Optional[list] = None, partage: Optional[str] = None,
                    appartenance: Optional[dict] = None, taches_retirees: Iterable = (),
                    developpement: Optional[set] = None, manquante: str = "erreur",
                    oppositions: Iterable = ()) -> Entrees:
    """Les entrées 1 à 5 d'un dossier de sortie au format du pilote.

    vagues : relectures (défaut : relecture/ du dossier, si elle existe) ; partage : chemin d'un partage.json, ou
    appartenance déjà calculée ; taches_retirees : liste explicite [(environnement, tâche)] ou {(env, tâche): raison},
    qui s'ajoute aux motifs a ; developpement : tâches de développement (défaut : banc/tirage/developpement.json)."""
    parties = charger_parties(dossier)
    actions = grouper_actions(lire_actions(os.path.join(dossier, "actions_typees.csv")), parties)
    if vagues is None:
        v = relecture_du_dossier(dossier, parties[0].vague if parties else "pilote")
        vagues = [v] if v else []
    jointure = joindre_decisions(actions, vagues, manquante)
    retirees = fusionner_retirees(actions, jointure, taches_retirees, oppositions)
    if appartenance is None:
        appartenance = charger_partage(partage) if partage else {}
    dev = charger_developpement() if developpement is None else set(developpement)
    return Entrees(parties, actions, jointure, retirees, appartenance, dev)
