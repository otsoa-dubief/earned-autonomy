import sys, math
SIM = "ROOT/simulation"
sys.path.insert(0, SIM)
import numpy as np
from controle3 import harnais as H, mondes as MD, lancer as L
from rejeu import classes as CL, config_rejeu as CR, preuves as PR, suites as SU, types_regle as TY
BARRES = {"WorkBench": 1/132, "commerce": 1/38, "banque": 1/86, "aviation": 1/12}
nom, rep = "A", 0
params = L.parametres(); monde = MD.MONDES_PAR_NOM[nom]; cfg = H.config()
g_gen, _ = H.graine_repetition(params, monde, rep).spawn(2)
g = MD.generer(monde, np.random.default_rng(g_gen), cfg); e = g["entrees"]; prep = PR.preparer(e, "confirmes")
print("monde", nom, "rep", rep, "| types:", [TY.SIGLES[k] for k in TY.TYPES_SUITE])
for env in g["cal"]:
    for mod in CR.MODELES:
        j = SU.jeu_configuration(prep, e, env, mod, g["cal"][env], "calibration")
        for k in TY.TYPES_SUITE:
            c = CL.comptes_par_tache(j, (k,))
            if not c: continue
            m = np.array([v[0] for v in c.values() if v[0] > 0], dtype=float)
            if m.size == 0: continue
            n = m.sum(); ms = (m**2).sum()/n
            ne = {r: n/(1+(ms-1)*r) for r in (0.0, 0.3, 1.0)}
            b = BARRES.get(env)
            seuil = math.log(0.05)/math.log(1-b) if b else float('nan')
            print(f"{env:9s} {mod[:18]:18s} {TY.SIGLES[k]:4s} taches={m.size:4d} n={int(n):5d} m*={ms:6.1f} "
                  f"n_eff(0)={ne[0.0]:7.0f} n_eff(.3)={ne[0.3]:6.0f} n_eff(1)={ne[1.0]:6.0f} | seuil95%(0 err, barre faible)={seuil:5.0f}")
