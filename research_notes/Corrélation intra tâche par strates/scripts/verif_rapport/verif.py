from math import log, exp, sqrt
def p0(theta, rho, m):
    if rho >= 1: return 1 - theta
    if rho <= 0: return (1 - theta) ** m
    a, b = theta * (1 - rho) / rho, (1 - theta) * (1 - rho) / rho
    return exp(sum(log((b + i) / (a + b + i)) for i in range(m)))
alpha = 0.05
print("P(tache sans erreur) theta=0.02 m=10:", [round(p0(0.02, r, 10), 3) for r in (0, .1, .3, .5, .7, .9, 1)])
# table : k minimal certifiant a zero erreur sous rho suppose, risque reel sous rho vrai
import math
res = {}
for rs in (0.3, 0.5, 0.7, 0.8, 0.9, 1.0):
    row = {}
    for m in (5, 10, 20):
        for th in (0.01, 0.05):
            seuil = log(alpha) / log(1 - th)
            k = 1
            while k * m / (1 + (m - 1) * rs) <= seuil: k += 1
            for rv in (0.3, 0.5, 0.7, 0.9, 1.0):
                row.setdefault(rv, []).append(p0(th, rv, m) ** k)
            if m == 10: row.setdefault("k", []).append((th, k))
    res[rs] = row
for rs, row in res.items():
    print(f"rho suppose {rs}: k(m=10)={row['k']}", {rv: (round(min(v), 3), round(max(v), 3)) for rv, v in row.items() if rv != 'k'})
# seuils de n_eff a zero erreur pour les barres a enjeu faible
for nom, th in (("WorkBench", 1/132), ("commerce", 1/38), ("banque", 1/86), ("aviation", 1/12), ("faible", 1/200), ("moyen", 1/2000), ("fort", 1/20000)):
    print(nom, "n_eff 95%:", round(log(0.05)/log(1-th), 1), " n_eff 50% (jugeable):", round(log(0.5)/log(1-th), 1))
# Frechet
plo, phi = 1e-4, 1e-2
print("phi_max(1%,0.01%)", round(sqrt(plo*(1-phi)/(phi*(1-plo))), 4))
# CP zero erreur n=300 m*=50 rho=0.3
ne = 300/(1+49*0.3); print("n_eff", round(ne,1), "borne95", round(1-0.05**(1/ne),4), "vs n", round(1-0.05**(1/300),4))
# precision Monte-Carlo
print("reps pour 4% < 5% unilateral 95%:", round(1.645**2*0.04*0.96/0.01**2))
for n in (300, 1000, 10000):
    print(n, "demi-largeur unilaterale a 4%:", round(1.645*sqrt(0.04*0.96/n), 4))
# Deff illustratifs
for ms in (1, 2, 8, 70):
    print("m*", ms, {r: round(1+(ms-1)*r, 2) for r in (0.3, 0.5, 0.7, 1.0)}, "ratio n_eff rho1/rho0.3:", round((1+(ms-1)*0.3)/(1+(ms-1)*1.0), 2))
