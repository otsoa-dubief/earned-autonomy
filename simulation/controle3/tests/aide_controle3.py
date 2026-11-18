"""Entrées faites à la main pour les tests du contrôle 3 : une écriture par partie, erreurs placées exactement."""
from __future__ import annotations

import numpy as np

from rejeu import entrees as EN
from rejeu import types_regle as TY
from rejeu.entrees import accord, verdicts

BANC = {"aviation": ("tau2", "airline"), "commerce": ("tau2", "retail"), "banque": ("tau2", "banking_knowledge")}


def entrees_main(env: str, specs: dict, k: int = TY.ECR) -> EN.Entrees:
    """specs : {modèle: dict(passages=n, taches=[…], erreurs={(tâche, passage), …})} ; chaque partie fait une écriture
    du type k, fausse (alerte confirmée) si (tâche, passage) est dans `erreurs`, juste sinon. Une seule vague, gardée."""
    parties, actions, alertes, decisions = [], {}, {}, {}
    banc, domaine = BANC.get(env, ("workbench", None))
    nom = TY.TABLE[k].nom
    for modele, sp in specs.items():
        for t in sp["taches"]:
            for ps in range(1, sp["passages"] + 1):
                pid = f"{env}-{modele}-{t}-{ps}"
                parties.append(EN.Partie(id=pid, dossier=pid, environnement=env, modele=modele, tache=t,
                                         strate=EN.strate(env, t), passage=ps, vague="v1", debut="", statut_ok=True,
                                         terminaison="", reussie=None))
                err = (t, ps) in sp.get("erreurs", ())
                actions[pid] = [EN.Action(partie=pid, tache=t, rang=0, banc=banc,
                                          domaine=domaine or t.split(":")[0], outil="o", kind=verdicts.ECRITURE,
                                          verdict=verdicts.FAUSSE if err else verdicts.JUSTE, motif="", type=nom,
                                          enjeu=TY.niveau(k), plafonnee=False, montant=None)]
                if err:
                    aid = f"{pid}#0"
                    alertes[(pid, 0)] = aid
                    decisions[aid] = EN.DecisionRetenue(aid, EN.CONFIRMEE, "", "v1", False)
    j = EN.Jointure(alertes=alertes, decisions=decisions, desaccord_persistant={"v1": False},
                    conclusions={"v1": accord.GARDEE})
    return EN.Entrees(parties, actions, j, {}, {}, set())


def taches_wb(n: int, fichier: str = "multi_domain") -> list:
    return [f"{fichier}:{i}" for i in range(n)]


def erreurs_aleatoires(rng, taches, passages: int, p: float) -> set:
    return {(t, ps) for t in taches for ps in range(1, passages + 1) if rng.random() < p}
