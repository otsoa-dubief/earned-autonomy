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

