import sys, math
sys.path.insert(0, "ROOT/simulation")
import numpy as np
from controle3 import harnais as H, mondes as MD, lancer as L
from rejeu import classes as CL, config_rejeu as CR, preuves as PR, suites as SU, types_regle as TY
def p0(theta, rho, m):
    if rho >= 1: return 1 - theta
    if rho <= 0: return (1 - theta) ** m
    a, b = theta * (1 - rho) / rho, (1 - theta) * (1 - rho) / rho
    return math.exp(sum(math.log((b + i) / (a + b + i)) for i in range(int(m))))
for nom, rep in (("A", 0), ("E", 25)):
    params = L.parametres(); monde = MD.MONDES_PAR_NOM[nom]; cfg = H.config()
    g_gen, _ = H.graine_repetition(params, monde, rep).spawn(2)
    g = MD.generer(monde, np.random.default_rng(g_gen), cfg); e = g["entrees"]; prep = PR.preparer(e, "confirmes")
    j = SU.jeu_configuration(prep, e, "WorkBench", "claude-haiku-5-5", g["cal"]["WorkBench"], "calibration")
    k = [k for k in TY.TYPES_SUITE if TY.SIGLES[k] == "ECR"][0]
    m = [v[0] for v in CL.comptes_par_tache(j, (k,)).values() if v[0] > 0]
    th = 1/132
    print(nom, rep, "taches", len(m), "P(0 erreur au taux de la barre):", {r: round(math.prod(p0(th, r, mm) for mm in m), 4) for r in (0.0, 0.3, 0.5, 0.7, 0.9, 1.0)})
