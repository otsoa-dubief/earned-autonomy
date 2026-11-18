import math, warnings
warnings.filterwarnings("ignore")
import numpy as np
from scipy import stats
import helpers2 as H

# (a) Gulliford-type check: observed ICC at p=0.01 and p=0.40 for small latent ICCs (logit)
for r in [0.03, 0.05, 0.1, 0.15]:
    print(f"logit rhoL={r}: obs ICC p=0.01 -> {H.obs_icc('logit', r, 0.01):.4f} ; p=0.40 -> {H.obs_icc('logit', r, 0.40):.4f}")

# (b) plim of pooled one-way ANOVA ICC with heterogeneous item types, fixed composition, equal cluster size
#     derived: plim = (C - D) / ((m-1)(S + D)),  S=sum p_i q_i, C=sum_{i!=j} Cov(Y_i,Y_j), D=sum (p_i-pbar)^2
def plim_pooled(types, m_per, rhoL, link="probit"):
    items = [p for p, k in zip(types, m_per) for _ in range(k)]
    m = len(items); pbar = sum(items)/m
    S = sum(p*(1-p) for p in items); D = sum((p-pbar)**2 for p in items)
    C = 0.0
    for i, pi in enumerate(items):
        for j, pj in enumerate(items):
            if i == j: continue
            if pi == pj:
                C += H.obs_icc(link, rhoL, pi) * pi*(1-pi)
            else:
                C += H.cross(link, rhoL, pi, pj) * math.sqrt(pi*(1-pi)*pj*(1-pj))
    return (C - D)/((m-1)*(S + D))

def anova_icc(Y):
    k, m = Y.shape
    gm = Y.mean(); cm = Y.mean(axis=1)
    msb = m*((cm-gm)**2).sum()/(k-1)
    msw = ((Y-cm[:, None])**2).sum()/(k*(m-1))
    return (msb-msw)/(msb+(m-1)*msw)

rng = np.random.default_rng(1)
types = [0.02, 0.005]; m_per = [3, 3]; rhoL = 0.8
# Monte Carlo check of the plim formula under a shared probit latent intercept
k = 400000
u = rng.standard_normal(k)
cols = []
for p, n in zip(types, m_per):
    thr = stats.norm.ppf(1-p)   # Y=1 if sqrt(rhoL)*u + sqrt(1-rhoL)*e > thr
    for _ in range(n):
        e = rng.standard_normal(k)
        cols.append((math.sqrt(rhoL)*u + math.sqrt(1-rhoL)*e > thr).astype(float))
Y = np.column_stack(cols)
print("\nMC pooled ANOVA ICC:", round(anova_icc(Y), 4), " formula plim:", round(plim_pooled(types, m_per, rhoL), 4))
print("per-type observed ICC (exact):", [round(H.obs_icc('probit', rhoL, p), 4) for p in types],
      " MC per-type ANOVA:", [round(anova_icc(Y[:, 0:3]), 4), round(anova_icc(Y[:, 3:6]), 4)])

# (c) illustration: 4 types, shared latent ICC, pooled plim vs per-type observed ICC
types = [0.01, 0.003, 0.001, 0.0001]; m_per = [4, 3, 2, 1]
for rL in [0.7, 0.95]:
    pl = plim_pooled(types, m_per, rL)
    per = [H.obs_icc('probit', rL, p) for p in types]
    print(f"\nprobit shared rhoL={rL}: pooled ANOVA plim={pl:.4f}; per-type observed ICC=" + ", ".join(f"{p:g}:{v:.4f}" for p, v in zip(types, per)))
