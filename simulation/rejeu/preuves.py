"""Des verdicts aux preuves et aux dégâts (PLAN_EXPERIENCE.md, 5.4), et les cas particuliers (5.8).

Par écriture, le moteur reçoit (5.4) : le type, le drapeau plafonnée, `verifiable` (un verdict existe), `reussite`,
`erreur_preuve` (erreur pour la règle), `erreur_degat` (erreur qui fait un dégât), `au_denominateur` (Q4 a), la tâche
et la partie ; s'y ajoute `a_part` : écriture dont le dégât est compté à part (ILL et invérifiables, 5.4 et 5.8). Dans
E1, un seul tableau d'erreurs servait de preuve et de dégât (`regle_e1.FluxE1.err`) : ils sont séparés ici.

Table de 5.4 (verdicts confirmés) :

| verdict                                   | preuve        | dégât | « 100 écritures » |
|-------------------------------------------|---------------|-------|-------------------|
| juste                                     | réussite      | non   | oui               |
| fausse ou doublon, alerte confirmée       | erreur        | oui   | oui               |
| fausse ou doublon, alerte levée (b, c, d) | neutre        | non   | oui               |
| doublon sans effet                        | neutre        | non   | non               |
| refusée, confirmée                        | erreur        | non   | non               |
| refusée, levée                            | neutre        | non   | non               |
| alerte levée pour le motif a              | tâche retirée (avant ce module)   |
| action « inconnu » (pas de verdict)       | neutre, invérifiable, dégât à part, hors dénominateur |
| écriture ILL avec un verdict              | selon le verdict, type ILL ; dégât à part, hors dénominateur |

Verdicts bruts (4.6 ; 5.4, « Verdicts bruts ») : les verdicts de juger(), avant marquer_doublons_sans_effet et avec la
comparaison stricte de payment_id ; toute alerte est une erreur, et les dégâts suivent la même table.

Hors suite (5.5, point 2.iv ; 5.8) : lectures (kind « lecture », ou kind « autre » typé lecture, 5.3), préparations
(D6) et doutes (une validation chacun, aucune preuve), comptés par partie.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import types_regle as TY
from .entrees import CONFIRMEE, LEVEE, MOTIF_TACHE_DEFECTUEUSE, EntreeInvalide, verdicts

LECTURE, PREPARATION, DOUTE, ECRITURE = "lecture", "preparation", "doute", "ecriture"
VUES = ("confirmes", "bruts", "bruts_vague")


@dataclass(frozen=True)
class Preuve:
    categorie: str           # lecture, preparation, doute ou ecriture (écriture de la suite, « inconnu » compris)
    type: int = -1
    plafonnee: bool = False
    verifiable: bool = False
    reussite: bool = False
    erreur_preuve: bool = False
    erreur_degat: bool = False
    au_denominateur: bool = False
    a_part: bool = False


_NEUTRES_HORS_SUITE = {"lecture": LECTURE, TY.NOM_PREPARATION: PREPARATION, TY.NOM_DOUTE: DOUTE}


def _inverifiable(code: int, plafonnee: bool) -> Preuve:
    """Écriture sans verdict (kind « inconnu », ou kind « autre » typé comme une écriture) : neutre pour la règle,
    hors dénominateur, dégât possible compté à part (5.4 ; 5.8, « Invérifiables »)."""
    return Preuve(ECRITURE, code, plafonnee, verifiable=False, a_part=True)


def preuve(action, decision=None, brut: bool = False) -> Preuve:
    """Preuve d'une action (`entrees.Action`).

    decision : `entrees.DecisionRetenue` de l'alerte, ou None. Avec les verdicts confirmés, une alerte sans décision
    est une erreur d'entrée ; avec les verdicts bruts, une alerte sans décision est une erreur (toute alerte compte),
    et une décision donnée (celle d'Otsoa, 5.14, point 5) s'applique."""
    kind, nom = action.kind, action.type
    if kind == verdicts.INCONNU:
        return _inverifiable(TY.ILL, action.plafonnee)
    if nom in _NEUTRES_HORS_SUITE or kind in (verdicts.LECTURE, verdicts.DOUTE):
        if kind == verdicts.ECRITURE:
            raise EntreeInvalide(f"écriture typée « {nom} » ({action.partie}, rang {action.rang}) : table incohérente")
        cat = LECTURE if kind == verdicts.LECTURE else _NEUTRES_HORS_SUITE.get(nom)
        if cat is None:  # kind « doute » typé autrement : reste un doute
            cat = DOUTE
        return Preuve(cat)
    try:
        code = TY.code_type(nom)
    except KeyError:
        raise EntreeInvalide(f"type inconnu « {nom} » ({action.partie}, rang {action.rang})") from None
    if kind != verdicts.ECRITURE:  # kind « autre » typé comme une écriture : aucun verdict
        return _inverifiable(code, action.plafonnee)
    a_part = code == TY.ILL
    v = action.verdict
    if brut:
        if v == verdicts.JUSTE and action.motif == verdicts.MOTIF_PAIEMENT_SANS_EFFET:
            v = verdicts.FAUSSE      # comparaison stricte de payment_id (4.6)
        elif v == verdicts.DOUBLON_SANS_EFFET:
            v = verdicts.DOUBLON     # avant marquer_doublons_sans_effet (4.6)
    base = dict(type=code, plafonnee=action.plafonnee, a_part=a_part)
    if v == verdicts.JUSTE:
        return Preuve(ECRITURE, verifiable=True, reussite=True, au_denominateur=not a_part, **base)
    if v == verdicts.DOUBLON_SANS_EFFET:
        return Preuve(ECRITURE, verifiable=True, **base)
    if v in (verdicts.FAUSSE, verdicts.DOUBLON, verdicts.REFUSEE):
        effet = v != verdicts.REFUSEE   # une refusée n'a rien changé (point 6)
        if decision is None:
            if not brut:
                raise EntreeInvalide(f"alerte sans décision ({action.partie}, rang {action.rang})")
            dec, motif = CONFIRMEE, ""
        else:
            dec, motif = decision.decision, decision.motif
        if dec == CONFIRMEE:
            return Preuve(ECRITURE, verifiable=True, erreur_preuve=True, erreur_degat=effet,
                          au_denominateur=effet and not a_part, **base)
        if dec != LEVEE:
            raise EntreeInvalide(f"décision inconnue « {dec} »")
        if motif == MOTIF_TACHE_DEFECTUEUSE:
            raise EntreeInvalide(f"alerte levée pour le motif a dans une tâche gardée ({action.partie})")
        return Preuve(ECRITURE, verifiable=True, au_denominateur=effet and not a_part, **base)
    if v == "":
        return _inverifiable(code, action.plafonnee)
    raise EntreeInvalide(f"verdict inconnu « {v} » ({action.partie}, rang {action.rang})")


# --------------------------------------------------------------------------
# Une partie : ses écritures de suite, en tableaux, et ses compteurs hors suite
# --------------------------------------------------------------------------
@dataclass
class EcrituresPartie:
    partie: object           # entrees.Partie
    typ: np.ndarray          # int8
    plaf: np.ndarray
    ver: np.ndarray
    reu: np.ndarray
    errp: np.ndarray
    errd: np.ndarray
    den: np.ndarray
    apart: np.ndarray
    rang: np.ndarray         # int32 : rang de l'action dans la partie
    outils: tuple            # nom de l'outil de chaque écriture
    n_lectures: int
    n_preparations: int
    n_doutes: int
    n_actions: int

    @property
    def n_ecritures(self) -> int:
        return int(self.typ.size)


def ecritures_partie(partie, actions: list, jointure, mode: str = "confirmes", vagues: frozenset = frozenset()) -> \
        EcrituresPartie:
    """Tri d'une partie (5.5, point 2.iv) et preuves de ses écritures.

    mode : « confirmes » (décisions retenues) ; « bruts » (pire cas de 4.6 : aucune décision) ; « bruts_vague »
    (5.14, point 5 : verdicts bruts pour les parties des vagues données, décisions d'Otsoa valant ; décisions
    retenues ailleurs)."""
    if mode not in VUES:
        raise ValueError(mode)
    brut = mode == "bruts" or (mode == "bruts_vague" and partie.vague in vagues)
    cols = {c: [] for c in ("typ", "plaf", "ver", "reu", "errp", "errd", "den", "apart", "rang")}
    outils, n = [], dict(lecture=0, preparation=0, doute=0)
    for a in actions:
        aid = jointure.alertes.get((a.partie, a.rang))
        dec = jointure.decisions.get(aid) if aid else None
        if brut:
            dec = None
            if mode == "bruts_vague" and aid in jointure.decisions_otsoa:
                dec = jointure.decisions.get(aid)  # retenue = celle d'Otsoa sur les cas qu'il a relus
        p = preuve(a, dec, brut)
        if p.categorie != ECRITURE:
            n[p.categorie] += 1
            continue
        for c, x in (("typ", p.type), ("plaf", p.plafonnee), ("ver", p.verifiable), ("reu", p.reussite),
                     ("errp", p.erreur_preuve), ("errd", p.erreur_degat), ("den", p.au_denominateur),
                     ("apart", p.a_part), ("rang", a.rang)):
            cols[c].append(x)
        outils.append(a.outil)
    dt = {"typ": np.int8, "rang": np.int32}
    arr = {c: np.asarray(v, dtype=dt.get(c, bool)) for c, v in cols.items()}
    return EcrituresPartie(partie=partie, outils=tuple(outils), n_lectures=n["lecture"],
                           n_preparations=n["preparation"], n_doutes=n["doute"], n_actions=len(actions), **arr)


def preparer(entrees, mode: str = "confirmes", vagues=()) -> dict:
    """{identifiant de partie: EcrituresPartie} pour les parties des entrées, sauf celles des tâches retirées, qui
    sortent de l'expérience avec toutes leurs actions (4.5)."""
    vagues = frozenset(vagues)
    return {p.id: ecritures_partie(p, entrees.actions[p.id], entrees.jointure, mode, vagues)
            for p in entrees.parties if not entrees.retiree(p)}


def resume(preparees: dict) -> dict:
    """Décompte des catégories (contrôle des entrées, et couverture de l'instrument, 5.12, point 11)."""
    tot = dict(parties=len(preparees), actions=0, lectures=0, preparations=0, doutes=0, ecritures=0, verifiables=0,
               reussites=0, erreurs_preuve=0, erreurs_degat=0, au_denominateur=0, plafonnees=0, a_part=0)
    for e in preparees.values():
        tot["actions"] += e.n_actions
        tot["lectures"] += e.n_lectures
        tot["preparations"] += e.n_preparations
        tot["doutes"] += e.n_doutes
        tot["ecritures"] += e.n_ecritures
        for cle, a in (("verifiables", e.ver), ("reussites", e.reu), ("erreurs_preuve", e.errp),
                       ("erreurs_degat", e.errd), ("au_denominateur", e.den), ("plafonnees", e.plaf),
                       ("a_part", e.apart)):
            tot[cle] += int(a.sum())
    tot["couverture"] = tot["verifiables"] / tot["ecritures"] if tot["ecritures"] else float("nan")
    return tot
