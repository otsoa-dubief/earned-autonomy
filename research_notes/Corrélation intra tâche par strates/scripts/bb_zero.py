# Exact check: zero-error stratum, Clopper-Pearson one-sided on n_eff = k*m/(1+(m-1)*rho_assumed)
# True model: beta-binomial clusters (mean theta, ICC rho_true), k tasks of m runs.
from math import lgamma, log, exp
def p0_cluster(theta, rho, m):
    if rho <= 0: return (1-theta)**m
    if rho >= 1: return 1-theta
    a = theta*(1-rho)/rho; b = (1-theta)*(1-rho)/rho
    # P(Y=0) = B(a, b+m)/B(a,b) = prod_{i<m} (b+i)/(a+b+i)
    return exp(sum(log((b+i)/(a+b+i)) for i in range(m)))
alpha = 0.05
print("1) P(cluster has zero errors) vs rho  (theta=0.02, m=10)")
print("   ", [(r, round(p0_cluster(0.02, r, 10), 4)) for r in (0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0)])
print("2) Minimal k certifying at x=0, and TRUE false-certification prob P(all zero | p=theta) under rho_true")
for m in (5, 10, 20):
    for theta in (0.01, 0.05):
        need = log(alpha)/log(1-theta)   # n_eff must exceed this
        for ra in (0.3, 0.5, 1.0):
            de = 1+(m-1)*ra
            k = 1
            while k*m/de <= need: k += 1
            row = []
            for rt in (0.0, 0.3, 0.5, 0.7, 0.9, 1.0):
                row.append(f"{rt}:{p0_cluster(theta, rt, m)**k:.3f}")
            print(f"   m={m:2d} theta={theta} rho_assumed={ra}: k_min={k:4d} | " + "  ".join(row))
