#!/usr/bin/env python3
# Verification locale (pas une source publiee) : comportement d'estimateurs d'un rho COMMUN
# quand la prevalence differe entre strates. Grappes de taille >= 2 seulement (singletons exclus).
# Generation beta-binomiale : p_i ~ Beta(p(1-rho)/rho, (1-p)(1-rho)/rho), y ~ Bin(m, p_i).
import numpy as np
from scipy.special import betaln
from scipy.optimize import minimize

rng = np.random.default_rng(20261106)


def gen_stratum(p, rho, sizes):
    sizes = np.asarray(sizes, dtype=float)
    if p == 0:
        return sizes, np.zeros_like(sizes)
    if rho <= 0:
        pi = np.full(len(sizes), p)
    else:
        a = p * (1 - rho) / rho
        b = (1 - p) * (1 - rho) / rho
        pi = rng.beta(a, b, size=len(sizes))
    return sizes, rng.binomial(sizes.astype(int), pi).astype(float)


def anova_core(strata):
    """ANOVA a moyennes propres a chaque strate, carres moyens mis en commun.
    Avec une seule 'strate' (tout concatene) = ANOVA poolee classique."""
    N = sum(m.sum() for m, y in strata)
    K = sum(len(m) for m, y in strata)
    S = len(strata)
    if K - S <= 0 or N - K <= 0:
        return np.nan
    SSB = sum((y ** 2 / m).sum() - y.sum() ** 2 / m.sum() for m, y in strata)
    SSW = sum((y - y ** 2 / m).sum() for m, y in strata)
    MSB, MSW = SSB / (K - S), SSW / (N - K)
    m0 = (N - sum((m ** 2).sum() / m.sum() for m, y in strata)) / (K - S)
    den = MSB + (m0 - 1) * MSW
    return np.nan if den <= 0 else (MSB - MSW) / den


def concat(strata):
    return [(np.concatenate([m for m, y in strata]), np.concatenate([y for m, y in strata]))]


def fc(strata):
    """Fleiss-Cuzick a p_s propre a chaque strate :
    1 - sum_s SSW_s / sum_s (N_s - K_s) p_s (1 - p_s). Strates sans evenement : neutres."""
    num = den = 0.0
    for m, y in strata:
        N, K = m.sum(), len(m)
        p = y.sum() / N
        if p <= 0 or p >= 1:
            continue
        num += (y * (m - y) / m).sum()
        den += (N - K) * p * (1 - p)
    return np.nan if den == 0 else 1 - num / den


def fc_corr(strata, iters=200):
    """FC a p_s par strate + correction du biais de p_s(1-p_s) (point fixe) :
    E[p(1-p)] ~ p(1-p)(1 - deff_s/N_s), deff_s = 1 + (m*_s - 1) rho, m*_s = sum m^2 / N_s."""
    parts = []
    for m, y in strata:
        N, K = m.sum(), len(m)
        p = y.sum() / N
        if p <= 0 or p >= 1:
            continue
        parts.append(((y * (m - y) / m).sum(), (N - K) * p * (1 - p), N, (m ** 2).sum() / N))
    if not parts:
        return np.nan
    rho = fc(strata)
    S = sum(a for a, d, N, ms in parts)
    for _ in range(iters):
        den = sum(d / max(1 - (1 + (ms - 1) * rho) / N, 0.05) for a, d, N, ms in parts)
        new = min(max(1 - S / den, -0.5), 0.99)
        if abs(new - rho) < 1e-10:
            break
        rho = new
    return rho


def gee(strata):
    """Moment GEE echangeable (residus de Pearson standardises par p_s, chaque paire a poids egal)."""
    num = npairs = ssr = nres = 0.0
    npar = 0
    for m, y in strata:
        N = m.sum()
        p = y.sum() / N
        if p <= 0 or p >= 1:
            continue
        npar += 1
        sd = np.sqrt(p * (1 - p))
        r1, r0 = (1 - p) / sd, -p / sd
        sr = y * r1 + (m - y) * r0
        sq = y * r1 ** 2 + (m - y) * r0 ** 2
        num += ((sr ** 2 - sq) / 2).sum()
        npairs += (m * (m - 1) / 2).sum()
        ssr += sq.sum()
        nres += N
    if npar == 0:
        return np.nan
    phi = ssr / (nres - npar)
    return num / (npairs - npar) / phi


def bb_negll(params, ev):
    rho = 1 / (1 + np.exp(-params[-1]))
    ll = 0.0
    for k, (m, y) in enumerate(ev):
        p = 1 / (1 + np.exp(-params[k]))
        a = p * (1 - rho) / rho
        b = (1 - p) * (1 - rho) / rho
        ll += (betaln(y + a, m - y + b) - betaln(a, b)).sum()
    return -ll


def bb_ml(strata):
    """MV beta-binomial : p_s propre a chaque strate, rho commun (borne a >= ~0)."""
    ev = [(m, y) for m, y in strata if 0 < y.sum() < m.sum()]
    if not ev:
        return np.nan
    x0 = [np.log(y.sum() / (m.sum() - y.sum())) for m, y in ev] + [np.log(0.1 / 0.9)]
    res = minimize(bb_negll, x0, args=(ev,), method="L-BFGS-B",
                   bounds=[(-15, 15)] * len(ev) + [(-12, 6)])
    return 1 / (1 + np.exp(-res.x[-1]))


def per_stratum_avg(strata, est, weight="events"):
    vals, w = [], []
    for m, y in strata:
        if y.sum() == 0 or len(m) < 2:
            continue
        v = est([(m, y)])
        if np.isnan(v):
            continue
        vals.append(v)
        w.append(y.sum())
    if not vals:
        return np.nan
    return float(np.average(vals, weights=w))


ESTIMATORS = {
    "ANOVA poolee (1 moyenne)": lambda s: anova_core(concat(s)),
    "ANOVA stratifiee (toutes strates)": anova_core,
    "ANOVA stratifiee (strates a 0 evt exclues)": lambda s: anova_core([x for x in s if x[1].sum() > 0]),
    "Moy. ANOVA par strate, poids = nb erreurs": lambda s: per_stratum_avg(s, anova_core),
    "FC pooled (1 moyenne)": lambda s: fc(concat(s)),
    "FC a p_s par strate": fc,
    "Moy. FC par strate, poids = nb erreurs": lambda s: per_stratum_avg(s, fc),
    "FC a p_s par strate, corrige (point fixe)": fc_corr,
    "GEE moment, p_s par strate": gee,
    "MV beta-binomiale, p_s par strate": bb_ml,
}


def logu(lo, hi, k):
    return np.unique(np.round(np.exp(rng.uniform(np.log(lo), np.log(hi), k))).astype(int)) if False else \
        np.round(np.exp(rng.uniform(np.log(lo), np.log(hi), k))).astype(int)


def scen_D1(rho=0.0):
    return [gen_stratum(0.10, rho, rng.integers(2, 7, 25)),
            gen_stratum(0.0, rho, rng.integers(60, 151, 8)),
            gen_stratum(0.0, rho, rng.integers(60, 151, 8))]


def scen_D2(rho=0.0):
    return [gen_stratum(0.10, rho, rng.integers(2, 7, 25)),
            gen_stratum(0.003, rho, rng.integers(60, 151, 8)),
            gen_stratum(0.003, rho, rng.integers(60, 151, 8))]


def scen_O(rho):
    return [gen_stratum(p, rho, logu(2, 150, 12)) for p in (0.02, 0.05, 0.08, 0.10)]


def scen_O3(rho=0.3):
    return [gen_stratum(0.10, rho, rng.integers(2, 7, 25)),
            gen_stratum(0.02, rho, rng.integers(60, 151, 8)),
            gen_stratum(0.02, rho, rng.integers(60, 151, 8))]


SCENARIOS = [
    ("D1 rho=0 : erreurs en petites grappes (p=.10) ; 2 strates grandes grappes sans erreur", lambda: scen_D1(0.0), 0.0),
    ("D2 rho=0 : idem mais strates grandes grappes p=.003 (rares, non nulles)", lambda: scen_D2(0.0), 0.0),
    ("D1bis rho=0.3 : configuration D1, vraie correlation 0.3", lambda: scen_D1(0.3), 0.3),
    ("O1 rho=0.3 : 4 strates p=.02/.05/.08/.10, 12 grappes chacune, tailles 2-150", lambda: scen_O(0.3), 0.3),
    ("O2 rho=0.1 : idem O1", lambda: scen_O(0.1), 0.1),
    ("O4 rho=0.05 : idem O1", lambda: scen_O(0.05), 0.05),
    ("O3 rho=0.3 : petites grappes p=.10 + grandes grappes p=.02", lambda: scen_O3(0.3), 0.3),
]

R = 400
for name, gen, truth in SCENARIOS:
    res = {k: [] for k in ESTIMATORS}
    for _ in range(R):
        s = gen()
        for k, f in ESTIMATORS.items():
            res[k].append(f(s))
    print(f"\n### {name}  (vrai rho = {truth}, R = {R})")
    print(f"{'estimateur':48s} {'moyenne':>8s} {'mediane':>8s} {'%indef':>7s} {'P(>0.1)':>8s}")
    for k, v in res.items():
        v = np.array(v, dtype=float)
        ok = v[~np.isnan(v)]
        if len(ok) == 0:
            print(f"{k:48s} {'-':>8s} {'-':>8s} {100:7.0f}")
            continue
        print(f"{k:48s} {ok.mean():8.3f} {np.median(ok):8.3f} {100*np.isnan(v).mean():7.0f} {100*(ok>0.1).mean():7.0f}%")
