"""Grille de l'exploration E1 (PLAN_EXPLORATION_E1.md) : écrit les CSV de resultats_e1/.

Usage : .venv/bin/python executer_e1.py [--verifier-tests] [--verifier-gel]
  AM_DOSSIER_E1   dossier de sortie (défaut : resultats_e1/ ; jamais resultats/ ni resultats_v1/)
  AM_TRAVAILLEURS nombre de processus (défaut 8)
  Essais seulement : AM_E1_R_COURT, AM_E1_BLOC_COURT, AM_E1_R_LONG, AM_E1_BLOC_LONG, AM_E1_T_LONG,
                     AM_E1_AGENTS (liste de noms séparés par des virgules).

Déroulé : une tâche par (horizon, mélange, agent) ; les cinq règles et les quatre modes (base et
tests de résistance) tournent dans le même moteur, sur les mêmes tirages ; puis les témoins.
Les cellules « indécises » des règles (mode base) sont relancées avec 4 fois plus de répétitions
(répétitions emboîtées : les premières sont les mêmes) ; si elles restent indécises, elles comptent
comme un échec (plan, mesure 1).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")  # un fil par processus : les processus de travail se partagent les cœurs

import csv  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402

import numpy as np  # noqa: E402

import config as C  # noqa: E402
import config_e1 as E  # noqa: E402
import flux as F  # noqa: E402
import mesures as M  # noqa: E402
import regle_e1 as RE  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.environ.get("AM_DOSSIER_E1", os.path.join(ICI, "resultats_e1"))
if os.path.realpath(DOSSIER) in {os.path.realpath(os.path.join(ICI, d)) for d in ("resultats", "resultats_v1")}:
    raise SystemExit("AM_DOSSIER_E1 ne peut pas être resultats/ ni resultats_v1/")

HORIZONS = {h: dict(v) for h, v in E.HORIZONS.items()}
for h, cle in (("court", "COURT"), ("long", "LONG")):
    if f"AM_E1_R_{cle}" in os.environ:
        HORIZONS[h]["R"] = int(os.environ[f"AM_E1_R_{cle}"])
        HORIZONS[h]["bloc"] = int(os.environ.get(f"AM_E1_BLOC_{cle}", HORIZONS[h]["R"]))
if "AM_E1_T_LONG" in os.environ:
    HORIZONS["long"]["T"] = int(os.environ["AM_E1_T_LONG"])
FILTRE_AGENTS = set(os.environ["AM_E1_AGENTS"].split(",")) if os.environ.get("AM_E1_AGENTS") else None
TRAVAILLEURS = int(os.environ.get("AM_TRAVAILLEURS", "8"))
N_BOOT = 2000
NOMS_TEMOINS_FIXES = ["tout_valider", "liste_fixe", "tri_risque", "tout_approuver"]
TYPES_MERITES = [k for k in range(C.N_MERITES) if k != C.LEC]  # LEC agit seule en E1
SILENCIEUX = lambda a: a.t_change is not None and a.evenement is None and a.q_apres is not None  # noqa: E731


# --------------------------------------------------------------------------
# Intervalles
# --------------------------------------------------------------------------
def poids_bootstrap(R: int, graine) -> np.ndarray:
    rng = np.random.default_rng(graine)
    return rng.multinomial(R, np.full(R, 1.0 / R), size=N_BOOT).astype(np.float32)


def intervalles(X: np.ndarray, W: np.ndarray) -> dict:
    """X : (R, cellules). Moyenne, intervalle normal à 95 %, intervalle bootstrap (percentile),
    et leur union (intervalle retenu pour le verdict : la plus prudente des deux lectures)."""
    X = np.asarray(X, dtype=np.float64)
    R = X.shape[0]
    m = X.mean(axis=0)
    se = X.std(axis=0, ddof=1) / math.sqrt(R) if R > 1 else np.zeros_like(m)
    lo_n, hi_n = m - M.Z95 * se, m + M.Z95 * se
    B = (W @ X.astype(np.float32)) / R
    lo_b, hi_b = np.quantile(B, 0.025, axis=0), np.quantile(B, 0.975, axis=0)
    return dict(m=m, lo_n=lo_n, hi_n=hi_n, lo_b=lo_b, hi_b=hi_b, lo=np.minimum(lo_n, lo_b),
                hi=np.maximum(hi_n, hi_b), non_nulles=(X != 0).mean(axis=0))


def verdict(lo, hi, seuil):
    if hi <= seuil + 1e-15:
        return "passe"
    if lo > seuil + 1e-15:
        return "échoue"
    return "indécis"


def quantile_censure(x, censure, q):
    """Quantile d'une durée avec censure à droite (valeurs censurées comptées comme +∞)."""
    if x.size == 0:
        return float("nan")
    v = np.where(censure, np.inf, x.astype(float))
    r = float(np.quantile(v, q, method="inverted_cdf"))
    return r


# --------------------------------------------------------------------------
# Une tâche
# --------------------------------------------------------------------------
def agent_par_nom(horizon, melange, nom):
    for a in E.agents_horizon(horizon, melange):
        if a.nom == nom:
            return a
    raise KeyError(nom)


def q_phase(agent, apres):
    return F.q_regle_par_type(agent, apres)


def tache(horizon, melange, nom_agent, blocs, regles=None, modes=None, temoins=True, etiquette=0):
    t_debut = time.time()
    hz = HORIZONS[horizon]
    T, Rb = hz["T"], hz["bloc"]
    tc = T // 2
    agent = E.agent_horizon(agent_par_nom(horizon, melange, nom_agent), T)
    ih, im, ida = list(E.HORIZONS).index(horizon), E.MELANGES.index(melange), E.ID_AGENT_E1[agent.nom]
    regles = E.NOMS_REGLES if regles is None else regles
    modes = E.MODES if modes is None else modes
    fx = RE.flux_e1(horizon, melange, agent, blocs, T=T, taille_bloc=Rb)
    R = fx.R
    t_flux = time.time() - t_debut
    objets = [E.regle_e1(n, melange) for n in regles]
    var = [(r, m) for m in modes for r in objets]
    graines = {m: [C.GRAINE, 30, ih, ida, im, E.MODES.index(m), etiquette] for m in modes}
    res = RE.simuler_e1(fx, agent, var, graines, tc=tc)
    t_moteur = time.time() - t_debut - t_flux
    rng_ep = np.random.default_rng([C.GRAINE, 32, ih, ida, im, etiquette])
    n_nonlec = (fx.typ != C.LEC).sum(axis=0).astype(np.int64)
    n_nonlec_w = (fx.typ[tc:] != C.LEC).sum(axis=0).astype(np.int64)
    out = dict(horizon=horizon, melange=melange, agent=agent.nom, R=R, T=T, tc=tc, blocs=list(blocs),
               change=E.change(agent), silencieux=bool(SILENCIEUX(agent)), evenement=agent.evenement,
               donnees={}, par_type={}, derive={}, n_nonlec=n_nonlec, n_nonlec_w=n_nonlec_w)
    cpt = res.cpt
    for i, (r, m) in enumerate(var):
        sl = res.lignes(i)
        d = dict(exc=cpt.exc[sl].astype(np.int32), exc_w=cpt.exc_w[sl].astype(np.int32))
        if m == "base":
            d["exc_ep"] = rng_ep.binomial(res.ep_err[sl], E.E_VALIDATEUR).astype(np.int32)
            d["exc_ep_w"] = rng_ep.binomial(res.ep_err_w[sl], E.E_VALIDATEUR).astype(np.int32)
            d.update(val_nl=cpt.val_nl[sl], dou_nl=cpt.dou_nl[sl], cor_nl=cpt.cor_nl[sl], n_ep=res.n_ep[sl],
                     val_tot=cpt.val_tot[sl], dou_tot=cpt.dou_tot[sl], cor_tot=cpt.cor_tot[sl],
                     dmg=cpt.dmg[sl], ep_tent=res.ep_tentatives[sl], ep_reu=res.ep_reussites[sl])
            out["par_type"][r.nom] = dict(
                premier3=res.premier3[sl], premier2=res.premier2[sl], premier3_apres=res.premier3_apres[sl],
                snap=res.snap[sl], perte3=res.perte3[sl], dtype_perte3=res.dtype_perte3[sl],
                err_delai=res.err_delai[sl], pertes3_avant=res.pertes3_avant[sl], retour1=res.retour1[sl],
                comptes=cpt.comptes[sl].sum(axis=0), comptes_w=cpt.comptes_w[sl].sum(axis=0),
                temps3_w=cpt.comptes_w[sl][:, :, 2], temps_w=cpt.comptes_w[sl].sum(axis=2),
                expo3_avant=(cpt.comptes[sl] - cpt.comptes_w[sl])[:, :, 2],
                ever3=(res.premier3[sl] >= 0))
        out["donnees"][(r.nom, m)] = d
        out["derive"][(r.nom, m)] = dict(n_stints=res.n_stints[sl], max_cst=res.max_cst[sl], tot_cst=res.tot_cst[sl],
                                         tot_inv=res.tot_inv[sl], tot_rat=res.tot_rat[sl])
    if temoins:
        def ajouter(nom, fabrique):
            c = RE.Compteur(R, tc, True)
            pas = 2000
            for t0 in range(0, T, pas):
                c.accumuler(fabrique(t0, min(T, t0 + pas)), t0, fx)
            out["donnees"][(nom, "base")] = dict(
                exc=c.exc.astype(np.int32), exc_w=c.exc_w.astype(np.int32), val_nl=c.val_nl, dou_nl=c.dou_nl,
                cor_nl=c.cor_nl, n_ep=np.zeros(R, np.int64), val_tot=c.val_tot, dou_tot=c.dou_tot,
                cor_tot=c.cor_tot, dmg=c.dmg)
        for nom in NOMS_TEMOINS_FIXES:
            ajouter(nom, lambda a, b, nom=nom: RE.paliers_fixes(nom, fx.typ[a:b]))
        ajouter("oracle_p2", lambda a, b: RE.paliers_oracle_p2(fx.typ[a:b], agent, melange, max(0, tc - a)))
        P3r = RE.paliers_trois_reussites(fx)
        ajouter("trois_reussites", lambda a, b: P3r[a:b])
        del P3r
        for j, nom in enumerate(regles):
            if "base" not in modes:
                break
            sl = res.lignes(modes.index("base") * len(objets) + j)
            comptes = cpt.comptes[sl]
            rng_h = np.random.default_rng([C.GRAINE, 31, ih, ida, im, E.NOMS_REGLES.index(nom), etiquette])
            ajouter(f"hasard_{nom}", lambda a, b, comptes=comptes, rng_h=rng_h:
                    RE.paliers_hasard(fx.typ[a:b], comptes, rng_h))
    out["durees"] = dict(flux=t_flux, moteur=t_moteur, total=time.time() - t_debut)
    return out


def tache_relance(horizon, melange, nom_agent, regles, R_orig):
    """Relance : 3 × R_orig répétitions nouvelles (blocs suivants), mode base, sans témoins ; en trois
    passes de R_orig répétitions, pour garder la mémoire d'une tâche ordinaire."""
    Rb = HORIZONS[horizon]["bloc"]
    n0 = R_orig // Rb
    par_passe = R_orig // Rb
    sorties = []
    for p in range(E.FACTEUR_RELANCE - 1):
        blocs = list(range(n0 + p * par_passe, n0 + (p + 1) * par_passe))
        sorties.append(tache(horizon, melange, nom_agent, blocs, regles=regles, modes=["base"], temoins=False,
                             etiquette=1 + p))
    o = sorties[0]
    for o2 in sorties[1:]:
        for cle, d in o2["donnees"].items():
            for ch in ("exc", "exc_w"):
                o["donnees"][cle][ch] = np.concatenate([o["donnees"][cle][ch], d[ch]])
        o["R"] += o2["R"]
        o["durees"] = {k: o["durees"][k] + o2["durees"][k] for k in o["durees"]}
    return o


# --------------------------------------------------------------------------
# Résumés d'une tâche
# --------------------------------------------------------------------------
def lignes_budget(o, W, cles=None, sources=None):
    """Lignes de budget.csv pour une tâche (ou une relance fusionnée)."""
    T, tc = o["T"], o["tc"]
    lignes = []
    cles = list(o["donnees"]) if cles is None else cles
    fenetres = [("tout", "exc", T)] + ([("apres", "exc_w", T - tc)] if o["change"] else [])
    cols, meta = [], []
    for cle in cles:
        d = o["donnees"][cle]
        for fen, ch, n_act in fenetres:
            for j, niv in enumerate(E.NIVEAUX):
                cols.append(d[ch][:, j] * (100.0 / n_act))
                meta.append((cle, fen, niv, n_act, False))
                if "exc_ep" in d:
                    che = "exc_ep" if fen == "tout" else "exc_ep_w"
                    cols.append((d[ch][:, j] + d[che][:, j]) * (100.0 / n_act))
                    meta.append((cle, fen, niv, n_act, True))
    if not cols:
        return lignes
    I = intervalles(np.stack(cols, axis=1), W)
    regles_set = set(E.NOMS_REGLES)
    for c, (cle, fen, niv, n_act, avec_ep) in enumerate(meta):
        regle, mode = cle
        b = float(E.BUDGET[niv])
        lignes.append(dict(
            horizon=o["horizon"], melange=o["melange"], agent=o["agent"], regle=regle,
            type_regle="règle" if regle in regles_set else "témoin", mode=mode, epreuves="avec" if avec_ep else "à blanc",
            niveau=niv, fenetre=fen, n_rep=o["R"], n_actions=n_act, exces=I["m"][c], exces_lo_n=I["lo_n"][c],
            exces_hi_n=I["hi_n"][c], exces_lo_b=I["lo_b"][c], exces_hi_b=I["hi_b"][c], exces_lo=I["lo"][c],
            exces_hi=I["hi"][c], part_rep_non_nulles=I["non_nulles"][c], budget=b, rapport=I["m"][c] / b,
            rapport_hi=I["hi"][c] / b, verdict=verdict(I["lo"][c], I["hi"][c], b),
            # amendement E1-a : la fenêtre après le changement n'est jugée qu'à l'horizon long
            eliminatoire=bool(fen == "tout" or o["horizon"] == "long")))
    return lignes


def lignes_charges(o):
    R = o["R"]
    nl = np.maximum(o["n_nonlec"], 1)
    lignes, par_cle = [], {}
    agent = agent_par_nom(o["horizon"], o["melange"], o["agent"])
    delegable = any(float(q_phase(agent, ph)[k]) <= float(E.BARRES[(o["melange"], E.niveau_type(k))]) + C.TOL
                    for k in TYPES_MERITES for ph in (False, True))
    for (regle, mode), d in o["donnees"].items():
        if mode != "base":
            continue
        hors = 100.0 * (d["val_nl"] + d["dou_nl"] + d["cor_nl"]) / nl
        hors_ep = 100.0 * (d["val_nl"] + d["dou_nl"] + d["cor_nl"] + d["n_ep"]) / nl
        tot = 100.0 * (d["val_tot"] + d["dou_tot"] + d["cor_tot"]) / o["T"]
        tot_ep = 100.0 * (d["val_tot"] + d["dou_tot"] + d["cor_tot"] + d["n_ep"]) / o["T"]
        par_cle[regle] = dict(hors=hors, hors_ep=hors_ep)
        l = dict(horizon=o["horizon"], melange=o["melange"], agent=o["agent"], regle=regle,
                 type_regle="règle" if regle in E.NOMS_REGLES else "témoin", n_rep=R, delegable=delegable,
                 agent_change=o["change"])
        for nom, x in (("charge_hors_lec", hors), ("charge_hors_lec_avec_ep", hors_ep), ("charge_totale", tot),
                       ("charge_totale_avec_ep", tot_ep)):
            m, lo, hi, _ = M.ic_moyenne(x)
            l.update({nom: m, nom + "_lo": lo, nom + "_hi": hi})
        l["charge_epreuves_hors_lec"] = float(np.mean(100.0 * d["n_ep"] / nl))
        if "ep_tent" in d:
            l["epreuves_par_rep"] = float(d["ep_tent"].mean())
            l["epreuves_reussies"] = float(d["ep_reu"].sum() / max(1, d["ep_tent"].sum()))
        lignes.append(l)
    comp = []
    for regle in E.NOMS_REGLES:
        if regle not in par_cle:
            continue
        for contre in ["liste_fixe", "tri_risque", "oracle_p2", "tout_valider", f"hasard_{regle}"]:
            if contre not in par_cle:
                continue
            for mesure in ("hors", "hors_ep"):
                dd, lo, hi, n = M.ic_diff(par_cle[regle][mesure], par_cle[contre][mesure])
                comp.append(dict(horizon=o["horizon"], melange=o["melange"], agent=o["agent"], regle=regle,
                                 contre="hasard" if contre.startswith("hasard") else contre,
                                 mesure="charge_hors_lec" + ("_avec_ep" if mesure == "hors_ep" else ""),
                                 diff=dd, lo=lo, hi=hi, n_rep=n, regle_moy=float(par_cle[regle][mesure].mean()),
                                 contre_moy=float(par_cle[contre][mesure].mean())))
    return lignes, comp, delegable


def lignes_par_type(o):
    """Garantie (mesure 6), autonomie, retrait (5), volume (7), données du CUSUM (10), consigne."""
    agent = agent_par_nom(o["horizon"], o["melange"], o["agent"])
    R, T, tc = o["R"], o["T"], o["tc"]
    q_av, q_ap = q_phase(agent, False), q_phase(agent, True)
    gar, aut, ret, vol, cus, cons = [], [], [], [], [], []
    base = dict(horizon=o["horizon"], melange=o["melange"], agent=o["agent"])
    for regle, pt in o["par_type"].items():
        for k in TYPES_MERITES:
            niv = E.niveau_type(k)
            b = float(E.BARRES[(o["melange"], niv)])
            tk = dict(base, regle=regle, type=C.TYPES[k], niveau=niv, barre=b)
            phases = [("avant", q_av[k], (pt["premier3"][:, k] >= 0) & (pt["premier3"][:, k] < tc)),
                      ("apres", q_ap[k], pt["premier3_apres"][:, k] >= 0)] if o["change"] else \
                     [("tout", q_av[k], pt["premier3"][:, k] >= 0)]
            for ph, q, prom in phases:
                kk = int(prom.sum())
                p, lo, hi, n = M.ic_proportion(kk, R)
                gar.append(dict(tk, phase=ph, q=float(q), au_dessus=bool(q > b + C.TOL), n=n, k3=kk, p3=p,
                                p3_lo=lo, p3_hi=hi, verdict=verdict(lo, hi, 0.05) if q > b + C.TOL else ""))
            cpt = pt["comptes"][k]
            tot = max(1, int(cpt.sum()))
            aut.append(dict(tk, q_avant=float(q_av[k]), q_apres=float(q_ap[k]), part_temps_p3=cpt[2] / tot,
                            part_temps_p2plus=(cpt[1] + cpt[2]) / tot, part_rep_jamais_p3=float((~pt["ever3"][:, k]).mean()),
                            part_temps_p3_apres=pt["comptes_w"][k][2] / max(1, int(pt["comptes_w"][k].sum()))))
            # retrait (mesure 5) : types devenus mauvais, au palier 3 au moment du changement
            if o["change"] and agent.q_apres is not None and q_ap[k] > b + C.TOL and q_ap[k] > q_av[k]:
                promu = pt["snap"][:, k] == 3
                cens = pt["perte3"][promu, k] < 0
                dflux = np.where(cens, T - tc, pt["perte3"][promu, k] - tc).astype(float)
                dty = pt["dtype_perte3"][promu, k].astype(float)
                errs = pt["err_delai"][promu, k].astype(float)
                temps3 = pt["temps3_w"][:, k] / np.maximum(1, pt["temps_w"][:, k])
                l = dict(tk, q_avant=float(q_av[k]), q_apres=float(q_ap[k]), evenement=agent.evenement or "silencieux",
                         n_rep=R, n_promus=int(promu.sum()), part_temps_p3_apres=float(temps3.mean()))
                if promu.any():
                    pc, pclo, pchi, _ = M.ic_proportion(int(cens.sum()), int(promu.sum()))
                    em = M.ic_moyenne(errs)
                    l.update(part_non_retire=pc, part_non_retire_lo=pclo, part_non_retire_hi=pchi,
                             delai_med=quantile_censure(dflux, cens, 0.5), delai_p95=quantile_censure(dflux, cens, 0.95),
                             delai_type_med=quantile_censure(dty, cens, 0.5),
                             delai_type_p95=quantile_censure(dty, cens, 0.95),
                             delai_type_moy_retires=float(dty[~cens].mean()) if (~cens).any() else float("nan"),
                             erreurs_passees_moy=em[0], erreurs_passees_lo=em[1], erreurs_passees_hi=em[2])
                ret.append(l)
                if SILENCIEUX(agent):
                    expo = int(pt["expo3_avant"][:, k].sum())
                    fa = int(pt["pertes3_avant"][:, k].sum())
                    cus.append(dict(tk, p0=float(q_av[k]), p1=float(q_ap[k]), expo3_avant=expo, fausses_alertes=fa,
                                    arl0_type=(expo / fa) if fa else float("inf"), n_promus=int(promu.sum()),
                                    n_retires=int((~cens).sum()),
                                    delai_type_moy=float(dty[~cens].mean()) if (~cens).any() else float("nan"),
                                    part_censure=float(cens.mean()) if promu.any() else float("nan")))
            # volume (mesure 7) : horizon long, agents constants
            if o["horizon"] == "long" and not o["change"]:
                t3 = pt["premier3"][:, k]
                jam = t3 < 0
                vol.append(dict(tk, q=float(q_av[k]), n_rep=R, part_jamais=float(jam.mean()),
                                volume_med=quantile_censure(t3, jam, 0.5), volume_p95=quantile_censure(t3, jam, 0.95)))
        if agent.evenement == "consigne_SOR":  # paramétré par l'horizon (relecture, M4)
            au3 = pt["snap"][:, C.SOR] == 3
            perdu = (pt["perte3"][au3, C.SOR] >= 0)
            cons.append(dict(base, regle=regle, n_rep=R, n_sor_palier3_au_changement=int(au3.sum()),
                             part_sor_retire=float(perdu.mean()) if au3.any() else float("nan")))
    return gar, aut, ret, vol, cus, cons


def lignes_derive(o):
    """Amendement E1-a (décision 5) : à enjeu moyen et fort, au plus une erreur constatée passe avant le
    retrait, par type et par épisode de dérive (éliminatoire, mode base). Épisode : chaque période au
    palier 3 après le changement, sur un type dont le taux monte. Les erreurs sur des actions
    invérifiables sont exclues du critère (elles ne déclenchent pas le retrait) et rapportées à part ;
    dans les modes de résistance, les erreurs ratées par le contrôle aussi."""
    if not o["change"]:
        return []
    agent = agent_par_nom(o["horizon"], o["melange"], o["agent"])
    if agent.q_apres is None:
        return []
    q_av, q_ap = q_phase(agent, False), q_phase(agent, True)
    out = []
    for (regle, mode), dv in o["derive"].items():
        for k in TYPES_MERITES:
            if not q_ap[k] > q_av[k]:
                continue
            ep = dv["n_stints"][:, k] > 0
            haut = bool(C.ENJEU_HAUT[k])
            mx = int(dv["max_cst"][:, k].max()) if ep.any() else 0
            out.append(dict(horizon=o["horizon"], melange=o["melange"], agent=o["agent"], regle=regle, mode=mode,
                            type=C.TYPES[k], niveau=E.niveau_type(k), q_avant=float(q_av[k]), q_apres=float(q_ap[k]),
                            evenement=agent.evenement or "silencieux", n_rep=o["R"], n_rep_episode=int(ep.sum()),
                            periodes_moy=float(dv["n_stints"][ep, k].mean()) if ep.any() else 0.0,
                            max_constatees=mx,
                            part_rep_plus_d_une=float((dv["max_cst"][:, k] >= 2).mean()),
                            constatees_moy=float(dv["tot_cst"][ep, k].mean()) if ep.any() else 0.0,
                            inverifiables_moy=float(dv["tot_inv"][ep, k].mean()) if ep.any() else 0.0,
                            inverifiables_max=int(dv["tot_inv"][:, k].max()),
                            ratees_moy=float(dv["tot_rat"][ep, k].mean()) if ep.any() else 0.0,
                            critere=haut, verdict=("passe" if mx <= 1 else "échoue") if haut else ""))
    return out


# --------------------------------------------------------------------------
# Mesure 8 : bornes de B sur deux suites piège (référence RegleUnTypeB)
# --------------------------------------------------------------------------
def suite_piege(regle_un_type, n_cycles, rafale=False, d=0.95, rng=None):
    """« N réussites puis une erreur » (toutes vérifiées) ou « rafale » : réussites vérifiées jusqu'à
    l'autonomie, puis des erreurs, constatées chacune avec la probabilité d, jusqu'au retrait.
    Épreuves toujours réussies. Rend l'excès (erreurs au palier 3 × 0,95) par action du type."""
    rg = regle_un_type
    n_act = 0
    n_err3 = 0
    for _ in range(n_cycles):
        while rg.palier < 3:
            if rg.epreuve_due():
                rg.resultat_epreuve(True)
            rg.succes()
            n_act += 1
        while rg.palier == 3:
            if rg.epreuve_due():
                rg.resultat_epreuve(True)
            n_act += 1
            n_err3 += 1
            if not rafale or rng.random() < d:
                rg.erreur()
            else:
                rg.neutre()
    return (1 - E.E_VALIDATEUR) * n_err3 / n_act


def lignes_bornes_b():
    out = []
    rng = np.random.default_rng([C.GRAINE, 40])
    d = float(E.D_CONSTAT)
    for m in E.MELANGES:
        for nom in ("B-régulier", "B-tout"):
            r = E.regle_e1(nom, m)
            for niv in E.NIVEAUX:
                k = E.TYPES_NIVEAU[niv][0]
                N = int(r.N[k])
                Ne = E.n_allonge(N) if C.ENJEU_HAUT[k] else N
                p1 = suite_piege(RE.RegleUnTypeB.depuis_regle(r, k), 50)
                p2 = suite_piege(RE.RegleUnTypeB.depuis_regle(r, k), 200, rafale=True, rng=rng)
                b = float(E.BARRES[(m, niv)])
                out.append(dict(melange=m, regle=nom, niveau=niv, type=C.TYPES[k], N=N, N_effectif=Ne,
                                piege1_borne=0.95 / (N + 1), piege1_attendu=0.95 / (Ne + 1), piege1_mesure=p1,
                                rafale_borne=0.95 / (d * N + 1), rafale_attendu=0.95 / (d * Ne + 1), rafale_mesure=p2,
                                exces_max_par_action=0.95 * b, piege1_sur_budget=p1 / (0.95 * b),
                                rafale_sur_budget=p2 / (0.95 * b)))
    return out


# --------------------------------------------------------------------------
# Tables analytiques (mesures 7 et 11) et étalonnage
# --------------------------------------------------------------------------
def lignes_analytiques():
    vol, cert, bar = [], [], []
    for m in E.MELANGES:
        for niv in E.NIVEAUX:
            b = E.BARRES[(m, niv)]
            bar.append(dict(melange=m, niveau=niv, part=float(E.part_niveau(m, niv)), barre=float(b),
                            un_sur=float(1 / b), budget=float(E.BUDGET[niv]), N_B_regulier=E.N_B_REGULIER[(m, niv)],
                            N_B_tout=E.N_B_TOUT[(m, niv)], N_B_regulier_allonge=E.n_allonge(E.N_B_REGULIER[(m, niv)]),
                            N_B_tout_allonge=E.n_allonge(E.N_B_TOUT[(m, niv)]),
                            pm3_A_degats=E.PM3_A_DEGATS[(m, niv)], pm3_A_degats_sur_barre=E.PM3_A_DEGATS[(m, niv)] / float(b)))
            cert.append(dict(melange=m, niveau=niv, barre=float(b), certification=E.certification(m, niv),
                             regle_de_trois=3 / float(b)))
        for nom in E.NOMS_REGLES:
            r = E.regle_e1(nom, m)
            for k in TYPES_MERITES:
                if r.famille == "B":
                    n = int(r.N[k])
                else:
                    n = math.ceil(-r.params.lnB / r.params.b3[k] - 1e-12)
                part = float(E.part_type(m, k))
                vol.append(dict(melange=m, regle=nom, type=C.TYPES[k], niveau=E.niveau_type(k), reussites=n,
                                volume_flux=n / (part * (1 - C.PART_INVERIFIABLE))))
    return vol, cert, bar


# --------------------------------------------------------------------------
# Écriture
# --------------------------------------------------------------------------
def ecrire_csv(nom, lignes):
    if not lignes:
        return
    os.makedirs(DOSSIER, exist_ok=True)
    cles = []
    for l in lignes:
        for k in l:
            if k not in cles:
                cles.append(k)
    with open(os.path.join(DOSSIER, f"{nom}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cles)
        w.writeheader()
        for l in lignes:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in l.items()})


def liste_taches():
    taches = []
    for horizon, hz in HORIZONS.items():
        nb = hz["R"] // hz["bloc"]
        for m in E.MELANGES:
            for a in E.agents_horizon(horizon, m):
                if FILTRE_AGENTS and a.nom not in FILTRE_AGENTS:
                    continue
                taches.append((horizon, m, a.nom, list(range(nb))))
    # les plus longues d'abord
    taches.sort(key=lambda x: -HORIZONS[x[0]]["T"] * HORIZONS[x[0]]["R"])
    return taches


def resumer(o):
    """Dans le processus de travail : tout ce qui ne dépend que de la tâche."""
    W = poids_bootstrap(o["R"], [C.GRAINE, 33, list(E.HORIZONS).index(o["horizon"]),
                                 E.MELANGES.index(o["melange"]), E.ID_AGENT_E1[o["agent"]]])
    bud = lignes_budget(o, W)
    ch, comp, deleg = lignes_charges(o)
    gar, aut, ret, vol, cus, cons = lignes_par_type(o)
    brut = {cle: dict(exc=d["exc"], exc_w=d["exc_w"]) for cle, d in o["donnees"].items()
            if cle[1] == "base" and cle[0] in E.NOMS_REGLES}
    return dict(cle=(o["horizon"], o["melange"], o["agent"]), R=o["R"], T=o["T"], tc=o["tc"], change=o["change"],
                budget=bud, charges=ch, comparaisons=comp, garantie=gar, autonomie=aut, retrait=ret, volume=vol,
                cusum=cus, consigne=cons, derive=lignes_derive(o), brut=brut, durees=o["durees"])


def travail(args):
    return resumer(tache(*args))


def travail_relance(args):
    horizon, melange, agent, regles, R_orig = args
    o = tache_relance(horizon, melange, agent, regles, R_orig)
    brut = {cle: dict(exc=d["exc"], exc_w=d["exc_w"]) for cle, d in o["donnees"].items()}
    return dict(cle=(horizon, melange, agent), brut=brut, R=o["R"], durees=o["durees"])


def fusionner_relances(resumes, relances):
    """Recalcule les cellules indécises avec les répétitions emboîtées (originales + nouvelles)."""
    par_cle = {r["cle"]: r for r in resumes}
    for rel in relances:
        r0 = par_cle[rel["cle"]]
        h, m, a = rel["cle"]
        R4 = r0["R"] + rel["R"]
        W = poids_bootstrap(R4, [C.GRAINE, 34, list(E.HORIZONS).index(h), E.MELANGES.index(m), E.ID_AGENT_E1[a]])
        o = dict(horizon=h, melange=m, agent=a, R=R4, T=r0["T"], tc=r0["tc"], change=r0["change"], donnees={})
        for cle, d in rel["brut"].items():
            d0 = r0["brut"][cle]
            o["donnees"][cle] = dict(exc=np.concatenate([d0["exc"], d["exc"]]),
                                     exc_w=np.concatenate([d0["exc_w"], d["exc_w"]]))
        nouvelles = {(l["regle"], l["niveau"], l["fenetre"]): l for l in lignes_budget(o, W)}
        for l in r0["budget"]:
            cle = (l["regle"], l["niveau"], l["fenetre"])
            if l["mode"] == "base" and l["epreuves"] == "à blanc" and l.get("relance") and cle in nouvelles:
                n = nouvelles[cle]
                l.update(n_rep_relance=R4, exces_relance=n["exces"], exces_lo_relance=n["exces_lo"],
                         exces_hi_relance=n["exces_hi"], verdict_relance=n["verdict"])
                l["verdict_final"] = n["verdict"] if n["verdict"] != "indécis" else "échoue (indécis après relance)"


def main():
    debut = time.time()
    if "--verifier-gel" in sys.argv:
        import gel_e1
        ecarts = gel_e1.verifier()
        if ecarts:
            print("Le code a changé depuis le gel (GEL_E1.txt) : aucun résultat produit.\n" + "\n".join(ecarts))
            sys.exit(1)
    if "--verifier-tests" in sys.argv:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", os.path.join(ICI, "tests")], cwd=ICI)
        if r.returncode != 0:
            print("Les tests ne passent pas : aucun résultat produit.")
            sys.exit(1)
    taches = liste_taches()
    print(f"{len(taches)} tâches, {TRAVAILLEURS} processus, sortie {DOSSIER}", flush=True)
    resumes = []
    with ProcessPoolExecutor(max_workers=TRAVAILLEURS) as ex:
        for i, r in enumerate(ex.map(travail, taches)):
            resumes.append(r)
            h, m, a = r["cle"]
            print(f"[{i + 1}/{len(taches)}] {h:5s} {m:15s} {a:22s} moteur {r['durees']['moteur']:6.1f} s, "
                  f"tâche {r['durees']['total']:6.1f} s (écoulé {time.time() - debut:6.0f} s)", flush=True)
    # cellules indécises des règles (mode base, épreuves à blanc) : relance à 4 fois plus de répétitions
    a_relancer = {}
    for r in resumes:
        for l in r["budget"]:
            if l["type_regle"] == "règle" and l["mode"] == "base" and l["epreuves"] == "à blanc":
                l["relance"] = l["verdict"] == "indécis"
                l["verdict_final"] = l["verdict"]
                if l["relance"]:
                    a_relancer.setdefault(r["cle"], set()).add(l["regle"])
    for r in resumes:
        for l in r["budget"]:
            l.setdefault("relance", False)
            l.setdefault("verdict_final", l["verdict"])
    relances = []
    if a_relancer:
        args = [(h, m, a, sorted(regs, key=E.NOMS_REGLES.index), next(x["R"] for x in resumes if x["cle"] == (h, m, a)))
                for (h, m, a), regs in a_relancer.items()]
        print(f"relance de {len(args)} tâches (cellules indécises)", flush=True)
        with ProcessPoolExecutor(max_workers=TRAVAILLEURS) as ex:
            for rel in ex.map(travail_relance, args):
                relances.append(rel)
                print(f"  relance {rel['cle']} {rel['durees']['total']:.1f} s", flush=True)
        fusionner_relances(resumes, relances)
    tables = {n: [] for n in ("budget", "charges", "comparaisons", "garantie", "autonomie", "retrait", "volume",
                              "cusum", "consigne", "derive")}
    for r in resumes:
        for n in tables:
            tables[n].extend(r[n])
    for n, lignes in tables.items():
        ecrire_csv(n, lignes)
    vol_a, cert, bar = lignes_analytiques()
    ecrire_csv("volume_analytique", vol_a)
    ecrire_csv("certification", cert)
    ecrire_csv("barres", bar)
    ecrire_csv("bornes_b", lignes_bornes_b())
    with open(os.path.join(ICI, "etalonnage_e1.json")) as f:
        et = json.load(f)
    ecrire_csv("etalonnage_a_degats", [dict(melange=c["melange"], niveau=c["niveau"], barre=c["barre"], pm3=c["pm3"],
                                            pb3=c["pb3"], pm3_sur_barre=c["pm3_sur_barre"], q_pire=c["q_pire"],
                                            q_pire_sur_barre=c["q_pire_sur_barre"], E_sur_barre=c["E_sur_barre"],
                                            iterations=len(c["iterations"]), T=c["T"], R=c["R"])
                                       for c in et["cellules"]])
    meta = dict(graine=C.GRAINE, horizons=HORIZONS, n_boot=N_BOOT, travailleurs=TRAVAILLEURS, numpy=np.__version__,
                duree_s=round(time.time() - debut, 1), n_taches=len(taches), n_relances=len(relances),
                filtre_agents=sorted(FILTRE_AGENTS) if FILTRE_AGENTS else None,
                durees_taches={f"{h}|{m}|{a}": r["durees"] for r in resumes for (h, m, a) in [r["cle"]]})
    with open(os.path.join(DOSSIER, "meta.json"), "w") as f:
        json.dump(meta, f, indent=1, ensure_ascii=False)
    print(f"terminé en {time.time() - debut:.0f} s")


if __name__ == "__main__":
    main()
