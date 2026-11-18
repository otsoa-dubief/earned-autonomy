"""Les mesures (plan section 7) : charge, dégâts, et leurs intervalles.

Comptabilité commune à toutes les règles, à partir du palier de chaque action :
- palier 1 (demander avant), ou doute de l'agent : une validation (charge) ; une action
  fausse est arrêtée avec une probabilité 1 − e, sinon elle part et compte dans les dégâts ;
- palier 2 (agir puis prévenir) : une action fausse est exécutée, puis corrigée avec une
  probabilité 1 − e (la correction compte dans la charge), sinon elle compte dans les dégâts ;
- palier 3 (agir seul) : une action fausse compte dans les dégâts.
Les variantes d'épreuve (règle seulement) sont des actions au palier 1 en plus du flux :
elles comptent dans la charge et dans les dégâts, pas dans le dénominateur.
Dénominateur : les 3 000 actions du flux (« pour 100 actions »).
"""
import math

import numpy as np

import config as C

Z95 = 1.959963984540054


class Comptable:
    """Prépare une fois ce qui ne dépend pas de e, puis évalue pour chaque e."""

    def __init__(self, P, types, err, dou, u_val, honore_doute=True, ep_var=None, ep_err=None,
                 graine=0):
        self.T = P.shape[1]
        self.R = P.shape[0]
        self.types = types
        self.err = err
        self.u_val = u_val
        dv = dou if honore_doute else np.zeros_like(dou)
        self.pre = (P == 1) | dv
        self.p2 = (P == 2) & ~self.pre
        self.p3 = (P == 3) & ~self.pre
        self.err_pre_p2 = err & (self.pre | self.p2)
        self.err_p3 = err & self.p3
        self.err_p2 = err & self.p2
        self.niveau = C.ENJEU[types]
        self.nonlec = types != C.LEC
        self.n_nonlec = self.nonlec.sum(axis=1)
        valid = (P == 1)
        doute_sup = dv & (P > 1)
        self.n_valid = valid.sum(axis=1)
        self.n_valid_nonlec = (valid & self.nonlec).sum(axis=1)
        self.n_doute = doute_sup.sum(axis=1)
        self.n_doute_nonlec = (doute_sup & self.nonlec).sum(axis=1)
        self.ep_var = ep_var
        self.ep_err = ep_err
        self.graine = graine
        if ep_var is not None:
            self.n_ep = ep_var.sum(axis=1, dtype=np.int64)
            m = ep_err > 0
            self.ep_lignes, self.ep_t = np.nonzero(m)
            self.ep_nerr = ep_err[m].astype(np.int64)
            self.ep_niv = C.ENJEU[types[self.ep_lignes, self.ep_t]]
        else:
            self.n_ep = np.zeros(self.R, dtype=np.int64)

    def evaluer(self, e: float) -> dict:
        rate = self.u_val < e  # le validateur laisse passer l'erreur
        dmg = (self.err_pre_p2 & rate) | self.err_p3
        corr = self.err_p2 & ~rate
        n_corr = corr.sum(axis=1)
        n_corr_nonlec = (corr & self.nonlec).sum(axis=1)
        out = {}
        k = 100.0 / self.T
        charge = self.n_valid + self.n_doute + n_corr + self.n_ep
        out["charge"] = charge * k
        out["charge_hors_lec"] = 100.0 * (self.n_valid_nonlec + self.n_doute_nonlec + n_corr_nonlec
                                          + self.n_ep) / np.maximum(self.n_nonlec, 1)
        out["charge_validation"] = self.n_valid * k
        out["charge_correction"] = n_corr * k
        out["charge_doute"] = self.n_doute * k
        out["charge_epreuve"] = self.n_ep * k
        ep_dmg = np.zeros((self.R, 3))
        if self.ep_var is not None and self.ep_nerr.size and e > 0:
            rng = np.random.default_rng([C.GRAINE, 3, self.graine, int(round(e * 1000))])
            rates = rng.binomial(self.ep_nerr, e)
            np.add.at(ep_dmg, (self.ep_lignes, self.ep_niv), rates)
        for niv, nom in enumerate(C.NIVEAUX):
            out[f"degats_{nom}"] = ((dmg & (self.niveau == niv)).sum(axis=1) + ep_dmg[:, niv]) * k
        out["degats_total"] = out["degats_faible"] + out["degats_moyen"] + out["degats_fort"]
        out["degats_epreuve"] = ep_dmg.sum(axis=1) * k  # part due aux variantes d'épreuve (incluse ci-dessus)
        # illustration seulement (REGLE.md, pièce 2 : un barème illustre, il ne juge pas)
        out["degats_bareme_illustratif"] = out["degats_faible"] + 10 * out["degats_moyen"] + 100 * out["degats_fort"]
        for j, nom in enumerate(C.TYPES):
            out[f"degats_{nom}"] = (dmg & (self.types == j)).sum(axis=1) * k
        return out


def comptabiliser(P, flux_sub, err, dou, e, honore_doute=True, ep_var=None, ep_err=None, graine=0):
    cpt = Comptable(P, flux_sub.type, err, dou, flux_sub.u_val, honore_doute, ep_var, ep_err, graine)
    return cpt.evaluer(e)


# --------------------------------------------------------------------------
# Intervalles à 95 %
# --------------------------------------------------------------------------
def ic_moyenne(x):
    x = np.asarray(x, dtype=float)
    n = x.size
    m = float(x.mean())
    if n < 2:
        return m, m, m, n
    se = float(x.std(ddof=1)) / math.sqrt(n)
    return m, m - Z95 * se, m + Z95 * se, n


def ic_diff(x, y):
    return ic_moyenne(np.asarray(x, dtype=float) - np.asarray(y, dtype=float))


def ic_proportion(k, n):
    """Intervalle de Wilson à 95 %."""
    if n == 0:
        return float("nan"), float("nan"), float("nan"), 0
    p = k / n
    z2 = Z95 ** 2
    den = 1 + z2 / n
    centre = (p + z2 / (2 * n)) / den
    demi = Z95 * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / den
    return p, max(0.0, centre - demi), min(1.0, centre + demi), n


def ic_quantile(x, q, rng=None, n_boot=400):
    """Quantile empirique et intervalle bootstrap (percentile) à 95 %."""
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return float("nan"), float("nan"), float("nan"), 0
    est = float(np.quantile(x, q))
    rng = rng or np.random.default_rng([C.GRAINE, 4])
    idx = rng.integers(0, x.size, size=(n_boot, x.size))
    b = np.quantile(x[idx], q, axis=1)
    return est, float(np.quantile(b, 0.025)), float(np.quantile(b, 0.975)), x.size


def verdict_seuil(lo, hi, seuil):
    """« passe » si tout l'intervalle est sous le seuil, « échoue » s'il est tout au-dessus."""
    if hi <= seuil:
        return "passe"
    if lo > seuil:
        return "échoue"
    return "indécis"


def fmt(m, lo, hi, nd=2, pct=False):
    if pct:
        return f"{100 * m:.{nd}f} % [{100 * lo:.{nd}f} ; {100 * hi:.{nd}f}]"
    return f"{m:.{nd}f} [{lo:.{nd}f} ; {hi:.{nd}f}]"
