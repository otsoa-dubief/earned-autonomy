"""Les règles témoins (pièce 1 de REGLE.md, section 6 du plan).

Chaque témoin rend, pour chaque répétition et chaque action, le palier auquel l'action
est exécutée (1 demander avant, 2 agir puis prévenir, 3 agir seul). La comptabilité
(charge, dégâts) est commune à toutes les règles (module `mesures`).

Les témoins 6 à 10 (la règle sans remise à zéro, sans pondération, sans doute gratuit,
sans palier du milieu, sans épreuve) sont des variantes de la règle : voir
`config.ABLATIONS` et le moteur `regle.simuler_regle`.
"""
import numpy as np

import config as C
import flux as F


def paliers_tout_approuver(types: np.ndarray) -> np.ndarray:
    """Témoin 1 : tout est exécuté sans validation, plafonnés compris."""
    return np.full(types.shape, 3, dtype=np.int8)


def paliers_tout_valider(types: np.ndarray) -> np.ndarray:
    """Témoin 2 : tout demande une validation."""
    return np.ones(types.shape, dtype=np.int8)


def paliers_liste_fixe(types: np.ndarray) -> np.ndarray:
    """Témoin 3 : LEC et ECR agissent seuls, tout le reste demande une validation."""
    return np.where((types == C.LEC) | (types == C.ECR), 3, 1).astype(np.int8)


def paliers_tri_risque(types: np.ndarray) -> np.ndarray:
    """Témoin 4 : toute action à enjeu faible agit seule, le reste demande une validation."""
    faible = (C.ENJEU == C.FAIBLE)
    faible[C.PLA] = False
    return np.where(faible[types], 3, 1).astype(np.int8)


def paliers_oracle(types: np.ndarray, agent: C.Agent, params: C.ParamsRegle) -> np.ndarray:
    """Témoin 11 : un type agit seul si et seulement si son vrai q est au plus pb du palier 3."""
    T = types.shape[1]
    out = np.empty(types.shape, dtype=np.int8)
    tc = agent.t_change if (agent.t_change is not None and agent.q_apres is not None) else T
    for apres, sl in ((False, slice(0, tc)), (True, slice(tc, T))):
        if sl.start >= sl.stop:
            continue
        q = F.q_regle_par_type(agent, apres)
        autonome = q[:8] <= params.pb3 + C.TOL
        autonome[C.PLA] = False
        out[:, sl] = np.where(autonome[types[:, sl]], 3, 1)
    return out


def paliers_hasard(types: np.ndarray, comptes: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Témoin 12 : chaque type est promu à des moments tirés au hasard, pendant la même part
    du temps que sous la règle (mêmes parts de palier 2 et 3, type par type).

    La part est la moyenne sur toutes les répétitions de la règle, pas celle de la même
    répétition : la part d'une répétition dépend de ses propres erreurs (une erreur fait
    descendre la règle), et la reprendre donnerait au hasard une information sur l'avenir.
    """
    tot = comptes.sum(axis=(0, 2)).astype(np.float64)
    tot[tot == 0] = 1.0
    f3 = (comptes[:, :, 2].sum(axis=0) / tot).astype(np.float32)
    f23 = ((comptes[:, :, 2] + comptes[:, :, 1]).sum(axis=0) / tot).astype(np.float32)
    f3[C.PLA] = 0.0
    f23[C.PLA] = 0.0
    u = rng.random(types.shape, dtype=np.float32)
    out = np.where(u < f3[types], 3, np.where(u < f23[types], 2, 1)).astype(np.int8)
    return out


def simuler_trois_reussites(fl: F.Flux, err: np.ndarray, dou: np.ndarray, t_change=None) -> dict:
    """Témoin 5 : autonomie (palier 3) après 3 réussites vérifiées d'affilée sur le type,
    quel que soit l'enjeu ; retirée à la première erreur vérifiée. Doute et invérifiable
    neutres. Les plafonnés restent au palier 1."""
    R, T = fl.R, fl.T
    typesT = np.ascontiguousarray(fl.type.T)
    verT = np.ascontiguousarray(fl.verifiable.T)
    douT = np.ascontiguousarray(dou.T)
    errT = np.ascontiguousarray(err.T)
    serie = np.zeros(R * 8, dtype=np.int32)
    pal = np.ones(R * 8, dtype=np.int8)
    premier3 = np.full(R * 8, -1, dtype=np.int32)
    snap = np.zeros(R * 8, dtype=np.int8)
    retour1 = np.full(R * 8, -1, dtype=np.int32)
    PT = np.empty((T, R), dtype=np.int8)
    base = np.arange(R, dtype=np.int64) * 8
    tc = -1 if t_change is None else t_change
    for t in range(T):
        if t == tc:
            snap[:] = pal
        k = typesT[t].astype(np.int64)
        idx = base + k
        PT[t] = pal[idx]
        juge = (k != C.PLA) & verT[t] & ~douT[t]
        ok = juge & ~errT[t]
        ko = juge & errT[t]
        io = idx[ok]
        serie[io] += 1
        prom = io[serie[io] >= 3]
        pal[prom] = 3
        m = premier3[prom] < 0
        premier3[prom[m]] = t
        ik = idx[ko]
        serie[ik] = 0
        pal[ik] = 1
        if tc >= 0 and t >= tc:
            m1 = (retour1[ik] < 0) & (snap[ik] >= 2)
            retour1[ik[m1]] = t
    return dict(P=np.ascontiguousarray(PT.T), premier3=premier3.reshape(R, 8),
                snap=snap.reshape(R, 8), retour1=retour1.reshape(R, 8))
