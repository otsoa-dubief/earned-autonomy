import math, warnings
warnings.filterwarnings("ignore")
import numpy as np
from scipy import integrate, optimize, stats
import icc_scales as M

def F(link):
    return M.expit if link == "logit" else stats.norm.cdf

def E(link, b0, s, b0b=None, power=1):
    f = F(link)
    pts = sorted({-b0 / s} | ({-b0b / s} if b0b is not None else set()))
    pts = [x for x in pts if -40 < x < 40]
    lo, hi = -40.0, 40.0
    if b0b is None:
        g = (lambda u: f(b0 + s*u)*stats.norm.pdf(u)) if power == 1 else (lambda u: f(b0 + s*u)**2*stats.norm.pdf(u))
    else:
        g = lambda u: f(b0 + s*u)*f(b0b + s*u)*stats.norm.pdf(u)
    return integrate.quad(g, lo, hi, points=pts or None, limit=1000, epsabs=0, epsrel=1e-11)[0]

def solve_b0(link, p, s):
    h = lambda b0: E(link, b0, s) - p
    lo, hi = -10.0, 5.0
    while h(lo) > 0: lo *= 2
    while h(hi) < 0: hi *= 2
    return optimize.brentq(h, lo, hi, xtol=1e-12)

def obs_icc(link, rhoL, p):
    s = math.sqrt(M.sigma2_from_rhoL(link, rhoL)); b0 = solve_b0(link, p, s)
    m1 = E(link, b0, s); m2 = E(link, b0, s, power=2)
    return (m2 - m1*m1)/(m1*(1-m1))

def cross(link, rhoL, pa, pb):
    s = math.sqrt(M.sigma2_from_rhoL(link, rhoL)); ba, bb = solve_b0(link, pa, s), solve_b0(link, pb, s)
    mab = E(link, ba, s, b0b=bb)
    return (mab - pa*pb)/math.sqrt(pa*(1-pa)*pb*(1-pb))

# 1) consistency check against the first script and against the bivariate normal CDF (probit)
for (r, p) in [(0.7, 0.01), (0.3, 0.001), (0.7, 0.0001)]:
    z = stats.norm.ppf(p)
    p11 = stats.multivariate_normal.cdf([z, z], mean=[0, 0], cov=[[1, r], [r, 1]], abseps=1e-15, releps=1e-12, maxpts=10**7)
    print(f"check probit rhoL={r} p={p}: quad={obs_icc('probit', r, p):.5f}  BVN={(p11 - p*p)/(p*(1-p)):.5f}  logit quad={obs_icc('logit', r, p):.5f}")

# 2) latent ICC implied by a fixed OBSERVED ICC
print("\n=== Latent ICC implied by an OBSERVED ICC held fixed across prevalences ===")
for target in [0.05, 0.3, 0.7]:
    for link in ["logit", "probit"]:
        out = []
        for p in [0.01, 0.001, 0.0001]:
            g = lambda r: obs_icc(link, r, p) - target
            out.append(optimize.brentq(g, 1e-4, 0.99999, xtol=1e-8))
        print(f"rho_obs={target:<5} {link:<6} -> rhoL at p=0.01,0.001,0.0001: " + ", ".join(f"{v:.4f}" for v in out))

# 3) cross-type observed correlation under a shared latent intercept
print("\n=== Cross-type observed correlation (shared latent intercept) ===")
pairs = [(0.01, 0.001), (0.01, 0.0001), (0.001, 0.0001)]
for r in [0.3, 0.7, 0.9, 0.99]:
    for link in ["logit", "probit"]:
        vals = [cross(link, r, a, b) for a, b in pairs]
        print(f"rhoL={r:<5} {link:<6} " + "  ".join(f"({a:g},{b:g})={v:.4f}" for (a, b), v in zip(pairs, vals)))
print("phi_max: " + "  ".join(f"({a:g},{b:g})={M.phi_max(a, b):.4f}" for a, b in pairs))
