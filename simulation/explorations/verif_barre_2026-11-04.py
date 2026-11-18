# Vérification rapide (hors plan, aucune donnée réelle) : barres déduites du budget,
# volume de Wald, et règle « N réussites d'affilée, retrait à la première erreur ».
import math, numpy as np
eps = 0.05                      # le validateur laisse passer 5 % des erreurs
budget = {"faible": 0.5, "moyen": 0.05, "fort": 0.005}   # pour 100 actions du flux
parts = {"bureau": {"faible": .66, "faible_sans_lect": .21, "moyen": .16, "fort": .136},
         "service_client": {"faible": .48, "faible_sans_lect": .08, "moyen": .22, "fort": .232}}
for m, d in parts.items():
    for niv, part in d.items():
        b = budget["faible" if niv.startswith("faible") else niv]
        ps = b / ((1 - eps) * 100 * part)
        print(f"{m:15s} {niv:17s} barre p* = {ps:.5f}  (1 sur {1/ps:,.0f})")
# Wald, pm = barre fort bureau, pb = pm/k : réussites d'affilée pour monter depuis L = 0
ps = 0.005 / ((1 - eps) * 100 * .136); lnB = math.log(0.05 / 0.95)
for k in (2, 4, 1e9):
    pm, pb = ps, ps / k
    bb = -math.log((1 - pm) / (1 - pb))
    print(f"Wald k={k:g}: {abs(lnB)/bb:,.0f} réussites d'affilée")
print("N d'affilée, agent régulier :", math.ceil(1 / (math.e * ps)) - 1, "; tout comportement :", math.ceil(1 / ps) - 1)
# Simulation de la règle N d'affilée (agent régulier), N = 950
rng = np.random.default_rng(20261104)
N = 950
for p in (1/951, 1/10000, 0.005, 0.02):
    err = rng.random(3_000_000) < p
    run = 0; auto = False; n_auto = 0; exc = 0.0
    for x in err:
        if auto:
            n_auto += 1
            if x: exc += 1 - eps; auto = False; run = 0
        else:
            run = 0 if x else run + 1
            if run >= N: auto = True
    n = len(err)
    print(f"p=1/{1/p:,.0f}: autonomie {n_auto/n:.3f} (théorie {(1-p)**N:.3f}) ; excès/action {exc/n:.2e} (théorie {(1-eps)*p*(1-p)**N:.2e}, plafond {(1-eps)*ps:.2e})")
