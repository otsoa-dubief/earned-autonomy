"""Moteur de tirage : le flux d'actions et les issues des agents fictifs.

Tous les tirages sont faits une fois pour toutes, par mélange, sous une graine fixe.
Toutes les règles (la règle et ses témoins) tournent ensuite sur les mêmes tirages :
mêmes actions, mêmes cas difficiles, mêmes erreurs, mêmes doutes, même validateur.
Les agents partagent aussi les mêmes nombres aléatoires (seul le seuil d'erreur change).
"""
from dataclasses import dataclass

import numpy as np

import config as C


@dataclass
class Flux:
    melange: str
    R: int
    T: int
    cat: np.ndarray      # (R, T) int8, catégorie interne (10 catégories)
    type: np.ndarray     # (R, T) int8, type d'action de la règle (8 types)
    difficile: np.ndarray  # (R, T) bool
    verifiable: np.ndarray  # (R, T) bool
    u_err: np.ndarray    # (R, T) float32
    u_doute: np.ndarray  # (R, T) float32
    u_val: np.ndarray    # (R, T) float32 : le validateur rate l'erreur si u_val < e

    def sous_ensemble(self, R: int) -> "Flux":
        """Les R premières répétitions (les cas à 1 000 sont emboîtés dans les cas à 5 000)."""
        return Flux(self.melange, R, self.T, self.cat[:R], self.type[:R], self.difficile[:R],
                    self.verifiable[:R], self.u_err[:R], self.u_doute[:R], self.u_val[:R])


def graine_melange(melange: str) -> np.random.SeedSequence:
    i = list(C.MELANGES_BRUTS).index(melange)
    return np.random.SeedSequence([C.GRAINE, 1, i])


def generer_flux(melange: str, R: int, T: int = C.HORIZON, seed=None) -> Flux:
    ss = graine_melange(melange) if seed is None else np.random.SeedSequence(seed)
    rng = np.random.default_rng(ss)
    p = C.probas_categories(melange)
    cum = np.cumsum(p)
    cum[-1] = 1.0 + 1e-9
    u = rng.random((R, T), dtype=np.float32)
    cat = np.searchsorted(cum, u, side="right").astype(np.int8)
    del u
    typ = C.CAT_TYPE[cat]
    difficile = rng.random((R, T), dtype=np.float32) < C.PART_DIFFICILE
    verifiable = rng.random((R, T), dtype=np.float32) >= C.PART_INVERIFIABLE
    u_err = rng.random((R, T), dtype=np.float32)
    u_doute = rng.random((R, T), dtype=np.float32)
    u_val = rng.random((R, T), dtype=np.float32)
    return Flux(melange, R, T, cat, typ, difficile, verifiable, u_err, u_doute, u_val)


def seuils_erreur(agent: C.Agent, apres: bool):
    """Taux d'erreur (difficile, facile) par catégorie interne."""
    q = agent.q(apres)[C.CAT_TAUX]
    return C.taux_difficile(q), C.taux_facile(q)


def erreurs(flux: Flux, agent: C.Agent) -> np.ndarray:
    """Issue vraie de chaque action : True si l'action est fausse."""
    T = flux.T
    tc = agent.t_change if (agent.t_change is not None and agent.q_apres is not None) else T
    out = np.empty((flux.R, T), dtype=bool)
    for apres, sl in ((False, slice(0, tc)), (True, slice(tc, T))):
        if sl.start >= sl.stop:
            continue
        qd, qf = seuils_erreur(agent, apres)
        c = flux.cat[:, sl]
        seuil = np.where(flux.difficile[:, sl], qd[c], qf[c]).astype(np.float32)
        out[:, sl] = flux.u_err[:, sl] < seuil
    return out


def doutes(flux: Flux, agent: C.Agent) -> np.ndarray:
    """L'agent doute-t-il de l'action (et demande une validation) ?"""
    if agent.doute == "jamais":
        return np.zeros((flux.R, flux.T), dtype=bool)
    if agent.doute == "calibre":
        return flux.difficile & (flux.u_doute < C.PROBA_DOUTE_CALIBRE)
    if agent.doute == "abusif":
        return flux.u_doute < C.PROBA_DOUTE_ABUSIF
    raise ValueError(agent.doute)


def q_regle_par_type(agent: C.Agent, apres: bool) -> np.ndarray:
    """Taux vrai par type de la règle (8 types ; PLA : taux « partout », sans usage)."""
    return agent.q(apres)[:8]
