from math import log, exp
def p0(theta, rho, m):
    if rho >= 1: return 1 - theta
    if rho <= 0: return (1 - theta) ** m
    a, b = theta * (1 - rho) / rho, (1 - theta) * (1 - rho) / rho
    return exp(sum(log((b + i) / (a + b + i)) for i in range(m)))
for K in (20, 50, 100):
    v = {r: p0(0.02, r, 10) ** K for r in (0, 0.3, 0.7, 1.0)}
    print("K", K, {r: round(x, 4) for r, x in v.items()}, "ratio 0.7/0.3:", round(v[0.7]/v[0.3], 1))
# Deff pour rho 0.8 et ratios
for ms in (2, 8, 70):
    d = {r: 1+(ms-1)*r for r in (0.3, 0.8, 1.0)}
    print("m*", ms, "gain n_eff 0.8 vs 1:", round(d[1.0]/d[0.8], 2), " 0.3 vs 1:", round(d[1.0]/d[0.3], 2))
