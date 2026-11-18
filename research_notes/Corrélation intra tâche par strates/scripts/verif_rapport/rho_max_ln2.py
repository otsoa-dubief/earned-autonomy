import sys, math
sys.path.insert(0, "ROOT/simulation")
import numpy as np
from controle3 import harnais as H, mondes as MD, lancer as L
from rejeu import classes as CL, config_rejeu as CR, preuves as PR, suites as SU, types_regle as TY
B = {"WorkBench": 1/132, "commerce": 1/38, "banque": 1/86}
for nom, rep in (("A", 0), ("A", 1), ("E", 25), ("A-rho7", 18)):
    params = L.parametres(); monde = MD.MONDES_PAR_NOM[nom]; cfg = H.config()
    g_gen, _ = H.graine_repetition(params, monde, rep).spawn(2)
    g = MD.generer(monde, np.random.default_rng(g_gen), cfg); e = g["entrees"]; prep = PR.preparer(e, "confirmes")
    for env in ("WorkBench", "commerce", "banque"):
        j = SU.jeu_configuration(prep, e, env, "claude-haiku-5-5", g["cal"][env], "calibration")
        for k in TY.TYPES_SUITE:
            if TY.SIGLES[k] not in ("ECR", "MSG"): continue
            c = CL.comptes_par_tache(j, (k,))
            m = np.array([v[0] for v in c.values() if v[0] > 0], dtype=float) if c else np.array([])
            if m.size == 0: continue
            n = m.sum(); ms = (m**2).sum()/n
            out = []
            for niv, a in (("95%", 0.05), ("50%", 0.5)):
                s = (math.log(2)/B[env]) if a == 0.5 else math.log(a)/math.log(1-B[env])
                rmax = (n/s - 1)/(ms - 1) if ms > 1 else float('inf')
                out.append(f"{niv}: seuil {s:.0f}, rho_max {rmax:.3f}")
            print(f"{nom} n°{rep} {env} Haiku {TY.SIGLES[k]} taches={m.size} n={int(n)} m*={ms:.3f} n_eff(1)={n/ms:.0f} | " + " ; ".join(out))
