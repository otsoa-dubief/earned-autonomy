import warnings; warnings.filterwarnings("ignore")
from scipy import optimize
import helpers2 as H
# Link sensitivity of the extrapolation: calibrate the latent ICC so that the observed ICC at the
# common type (p=1%) is fixed, then extrapolate to rarer types under each link.
for target in [0.02, 0.05, 0.3]:
    out = []
    for link in ["logit", "probit"]:
        rL = optimize.brentq(lambda r: H.obs_icc(link, r, 0.01) - target, 1e-5, 0.9999, xtol=1e-9)
        ext = [H.obs_icc(link, rL, p) for p in [0.001, 0.0001]]
        out.append(f"{link}: rhoL={rL:.4f} -> obs ICC p=0.001: {ext[0]:.5f}, p=0.0001: {ext[1]:.5f}")
    print(f"obs ICC fixed at {target} for p=1%  |  " + "  |  ".join(out))
