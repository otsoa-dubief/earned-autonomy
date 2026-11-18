"""Fait tourner toute la simulation et écrit les tableaux CSV de resultats/.

Usage : .venv/bin/python executer.py
Les tests (pytest tests/) doivent passer avant (le script le vérifie s'il est lancé
avec --verifier-tests).
"""
import csv
import json
import os
import subprocess
import sys
import time

import numpy as np

import config as C
import flux as F
import mesures as M
import regle as RG
import temoins as TM

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER = os.environ.get("AM_DOSSIER", os.path.join(ICI, "resultats"))
if "--v1" in sys.argv:  # reproduire la première passe (écrire ailleurs que resultats_v1/ : AM_DOSSIER)
    C.VERSION = "v1"
    if "AM_DOSSIER" not in os.environ:
        raise SystemExit("--v1 : donner AM_DOSSIER (jamais resultats_v1/)")
if "AM_R_CLES" in os.environ:  # essais rapides seulement
    C.R_CLES = int(os.environ["AM_R_CLES"])
    C.R_CAS = int(os.environ["AM_R_CAS"])

METRIQUES = ["charge", "charge_hors_lec", "charge_validation", "charge_correction", "charge_doute",
             "charge_epreuve", "degats_faible", "degats_moyen", "degats_fort", "degats_total", "degats_epreuve",
             "degats_bareme_illustratif"]
METRIQUES_TYPE = [f"degats_{t}" for t in C.TYPES]
CMP = ["charge", "charge_hors_lec", "degats_faible", "degats_moyen", "degats_fort"]
TEMOINS_CMP = ["tout_valider", "liste_fixe", "tri_risque", "hasard"]
FENETRE = 100


class Tables:
    def __init__(self):
        self.t = {}

    def ajouter(self, nom, ligne):
        self.t.setdefault(nom, []).append(ligne)

    def ecrire(self):
        os.makedirs(DOSSIER, exist_ok=True)
        for nom, lignes in self.t.items():
            cles = list(lignes[0].keys())
            for l in lignes:
                for k in l:
                    if k not in cles:
                        cles.append(k)
            with open(os.path.join(DOSSIER, f"{nom}.csv"), "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=cles)
                w.writeheader()
                for l in lignes:
                    w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in l.items()})


def nreg(reglage, alpha):
    return C.nom_reglage(reglage, alpha)


def graine(*parts):
    return np.random.SeedSequence([C.GRAINE, *parts])


def ligne_mesures(tab, mix, agent, regle, reglage, e, out):
    l = dict(melange=mix, agent=agent, regle=regle, reglage=reglage, e=e, n_rep=len(out["charge"]),
             n_actions=C.HORIZON)
    for m in METRIQUES:
        moy, lo, hi, _ = M.ic_moyenne(out[m])
        l[m] = moy
        l[m + "_lo"] = lo
        l[m + "_hi"] = hi
    for m in METRIQUES_TYPE:
        l[m] = float(np.mean(out[m]))
    tab.ajouter("mesures", l)


def lignes_comparaison(tab, mix, agent, reglage, e, regle, out_r, contre, out_t):
    n = len(out_r["charge"])
    for m in CMP:
        d, lo, hi, _ = M.ic_diff(out_r[m], out_t[m][:n])
        tab.ajouter("comparaisons", dict(melange=mix, agent=agent, reglage=reglage, e=e, regle=regle,
                                         contre=contre, mesure=m, diff=d, lo=lo, hi=hi, n_rep=n,
                                         regle_moy=float(np.mean(out_r[m])),
                                         contre_moy=float(np.mean(out_t[m][:n]))))


def autonomie_temps(tab, mix, agent, regle, reglage, P):
    R, T = P.shape
    w = T // FENETRE
    l2 = (P >= 2).reshape(R, w, FENETRE).mean(axis=2)
    l3 = (P == 3).reshape(R, w, FENETRE).mean(axis=2)
    p2, p3 = l2.mean(axis=0), l3.mean(axis=0)
    se2 = l2.std(axis=0, ddof=1) / np.sqrt(R)
    for i in range(w):
        tab.ajouter("autonomie_temps", dict(melange=mix, agent=agent, regle=regle, reglage=reglage,
                                            debut=i * FENETRE, part_palier2plus=float(p2[i]),
                                            part_palier2plus_lo=float(p2[i] - M.Z95 * se2[i]),
                                            part_palier2plus_hi=float(p2[i] + M.Z95 * se2[i]),
                                            part_palier3=float(p3[i]), n_rep=R))


def q_phase(agent, phase):
    return F.q_regle_par_type(agent, phase == "apres")


def lignes_garantie(tab, mix, agent, regle, reglage, params, d, R, phases=None):
    """Part des répétitions où le type atteint le palier 3 (et 2) avant l'horizon."""
    tc = agent.t_change
    if phases is None:
        phases = ["tout"]
        if agent.evenement == "modele" or agent.nom == "A6b":
            phases = ["avant", "apres"]
    for phase in phases:
        q = q_phase(agent, phase)
        for k in range(C.N_MERITES):
            if phase == "tout":
                prom3 = d["premier3"][:, k] >= 0
                prom2 = d["premier2"][:, k] >= 0 if "premier2" in d else None
            elif phase == "avant":
                prom3 = (d["premier3"][:, k] >= 0) & (d["premier3"][:, k] < tc)
                prom2 = (d["premier2"][:, k] >= 0) & (d["premier2"][:, k] < tc)
            else:
                prom3 = d["premier3_apres"][:, k] >= 0
                prom2 = None
            p, lo, hi, n = M.ic_proportion(int(prom3.sum()), R)
            l = dict(melange=mix, regle=regle, reglage=reglage, agent=agent.nom, phase=phase,
                     type=C.TYPES[k], enjeu=C.NIVEAUX[C.ENJEU[k]], q=float(q[k]),
                     pb3=float(params.pb3[k]), pm3=float(params.pm3[k]),
                     mauvais=bool(q[k] >= params.pm3[k] - C.TOL), bon=bool(q[k] <= params.pb3[k] + C.TOL),
                     n=n, k3=int(prom3.sum()), p3=p, p3_lo=lo, p3_hi=hi)
            if prom2 is not None:
                l["p2plus"] = float(prom2.mean())
            if "n_prom3" in d:
                l["promotions_p3_moy"] = float(d["n_prom3"][:, k].mean())
            tab.ajouter("garantie", l)


def lignes_promotion(tab, mix, agent, regle, reglage, params, d, R):
    q = q_phase(agent, "avant")
    for k in range(C.N_MERITES):
        for palier, cle in ((3, "premier3"), (2, "premier2")):
            t = d[cle][:, k]
            prom = t >= 0
            p, lo, hi, n = M.ic_proportion(int((~prom).sum()), R)
            l = dict(melange=mix, regle=regle, reglage=reglage, agent=agent.nom, type=C.TYPES[k],
                     enjeu=C.NIVEAUX[C.ENJEU[k]], palier=palier if palier == 3 else "2 ou plus",
                     q=float(q[k]), pb3=float(params.pb3[k]), bon=bool(q[k] <= params.pb3[k] + C.TOL),
                     n=n, jamais=p, jamais_lo=lo, jamais_hi=hi)
            l["n_promues"] = int(prom.sum())
            if prom.sum() >= 2:
                tp = t[prom].astype(float)
                m, mlo, mhi, _ = M.ic_moyenne(tp)
                l.update(delai_moy=m, delai_moy_lo=mlo, delai_moy_hi=mhi)
                if palier == 3:
                    med = M.ic_quantile(tp, 0.5)
                    p90 = M.ic_quantile(tp, 0.9)
                    l.update(delai_med=med[0], delai_med_lo=med[1], delai_med_hi=med[2],
                             delai_p90=p90[0], delai_p90_lo=p90[1], delai_p90_hi=p90[2])
                else:
                    l.update(delai_med=float(np.median(tp)), delai_p90=float(np.quantile(tp, 0.9)))
            tab.ajouter("promotion", l)


def lignes_reactivite(tab, mix, agent, regle, reglage, snap, retour1, dmg, types, R, params=None):
    """Délai entre la dégradation (t = 1500) et le retour au palier 1, pour les types promus
    (palier 2 ou 3) à t = 1500 ; dégâts sur ce type pendant l'intervalle. Lignes groupées :
    « tous » (tous les types promus) et « mauvais_apres » (types où le nouveau taux atteint le pm
    du palier 3 du réglage : ceux que la règle doit retirer)."""
    params = params if params is not None else C.params_regle(*C.REGLAGE_PRINCIPAL)
    q_ap = F.q_regle_par_type(agent, True)
    mauvais_apres = [k for k in range(C.N_MERITES) if q_ap[k] >= params.pm3[k] - C.TOL]
    tc, T = agent.t_change, C.HORIZON
    promu = snap[:, :C.N_MERITES] >= 2
    fin = np.where(retour1[:, :C.N_MERITES] >= 0, retour1[:, :C.N_MERITES], T)
    # dégâts pendant l'intervalle, par type
    lim = np.where(promu, fin, tc)
    lim8 = np.concatenate([lim, np.full((R, 1), tc)], axis=1)
    tt = np.arange(T)[None, :]
    masque = (tt >= tc) & (tt < lim8[np.arange(R)[:, None], types])
    dm = dmg & masque
    tous_d, tous_c, tous_dmg = [], [], []
    for k in list(range(C.N_MERITES)) + ["tous", "mauvais_apres"]:
        if k in ("tous", "mauvais_apres"):
            garde = list(range(C.N_MERITES)) if k == "tous" else mauvais_apres
            dd = np.concatenate([tous_d[j] for j in garde]) if garde else np.array([])
            cc = np.concatenate([tous_c[j] for j in garde]) if garde else np.array([], dtype=bool)
            gg = np.concatenate([tous_dmg[j] for j in garde]) if garde else np.array([])
            nomk = k
        else:
            m = promu[:, k]
            dd = (fin[m, k] - tc).astype(float)
            cc = retour1[m, k] < 0  # censuré : pas revenu au palier 1 avant l'horizon
            gg = (dm & (types == k)).sum(axis=1)[m].astype(float)
            tous_d.append(dd)
            tous_c.append(cc)
            tous_dmg.append(gg)
            nomk = C.TYPES[k]
        l = dict(melange=mix, regle=regle, reglage=reglage, agent=agent.nom, type=nomk,
                 n_rep=R, n_promus=int(dd.size),
                 types_mauvais_apres=" ".join(C.TYPES[j] for j in mauvais_apres))
        if dd.size:
            pc, pclo, pchi, _ = M.ic_proportion(int(cc.sum()), int(cc.size))
            med = M.ic_quantile(dd, 0.5)
            p95 = M.ic_quantile(dd, 0.95)
            dmo = M.ic_moyenne(gg)
            l.update(part_non_retire=pc, part_non_retire_lo=pclo, part_non_retire_hi=pchi,
                     delai_med=med[0], delai_med_lo=med[1], delai_med_hi=med[2],
                     delai_p95=p95[0], delai_p95_lo=p95[1], delai_p95_hi=p95[2],
                     delai_moy=float(dd.mean()),
                     degats_intervalle_moy=dmo[0], degats_intervalle_lo=dmo[1], degats_intervalle_hi=dmo[2])
        tab.ajouter("reactivite", l)


def lignes_consigne(tab, mix, agent, d, typ, R):
    """A8 (et A2, témoin sans consigne) : que devient SOR, au palier 3 juste avant t = 1 500 ?"""
    tc = C.T_CHANGEMENT
    P = d["P"]
    sor = typ == C.SOR
    au3 = d["snap"][:, C.SOR] == 3
    lignes = np.nonzero(au3)[0]
    tt = np.arange(P.shape[1])
    apres = sor & (tt[None, :] >= tc)
    perdu, retour = [], []
    for i in lignes:
        idx = np.nonzero(apres[i])[0]
        if idx.size == 0:
            continue
        perdu.append(P[i, idx[0]] < 3)
        if P[i, idx[0]] < 3:
            ok = idx[P[i, idx] == 3]
            retour.append(float(ok[0] - tc) if ok.size else float("nan"))
    perdu = np.array(perdu, dtype=bool)
    retour = np.array(retour)
    p, lo, hi, n = M.ic_proportion(int(perdu.sum()), int(perdu.size))
    l = dict(melange=mix, agent=agent.nom, n_rep=R, n_sor_palier3_a_1500=int(perdu.size),
             part_sor_retire=p, part_sor_retire_lo=lo, part_sor_retire_hi=hi)
    if retour.size:
        jamais = np.isnan(retour)
        pj, pjlo, pjhi, _ = M.ic_proportion(int(jamais.sum()), int(retour.size))
        l.update(part_jamais_revenu=pj, part_jamais_revenu_lo=pjlo, part_jamais_revenu_hi=pjhi)
        if (~jamais).sum() >= 2:
            med = M.ic_quantile(retour[~jamais], 0.5)
            l.update(delai_retour_med=med[0], delai_retour_med_lo=med[1], delai_retour_med_hi=med[2])
    tab.ajouter("consigne", l)


def ic_ratio(y, x):
    y = np.asarray(y, float)
    x = np.asarray(x, float)
    n = y.size
    if x.sum() == 0:
        return float("nan"), float("nan"), float("nan")
    r = y.sum() / x.sum()
    d = y - r * x
    se = d.std(ddof=1) / np.sqrt(n) / x.mean() if n > 1 else 0.0
    return r, r - M.Z95 * se, r + M.Z95 * se


def lignes_epreuves(tab, mix, agent, regle, reglage, d, fl, err):
    tent, reu = d["ep_tentatives"], d["ep_reussites"]
    jug, jok = d["ep_jugees"], d["ep_jugees_ok"]
    hi = C.ENJEU_HAUT[fl.type] & fl.verifiable
    ord_ok = 1.0 - err[hi].mean() if hi.any() else float("nan")
    hid = hi & fl.difficile
    dif_ok = 1.0 - err[hid].mean() if hid.any() else float("nan")
    tm, tlo, thi, _ = M.ic_moyenne(tent)
    l = dict(melange=mix, regle=regle, reglage=reglage, agent=agent.nom, n_rep=len(tent),
             tentatives_par_rep=tm, tentatives_par_rep_lo=tlo, tentatives_par_rep_hi=thi,
             tentatives_total=int(tent.sum()))
    r, lo, hh = ic_ratio(reu, tent)
    l.update(reussite_epreuve=r, reussite_epreuve_lo=lo, reussite_epreuve_hi=hh)
    r, lo, hh = ic_ratio(jok, jug)
    l.update(reussite_variante=r, reussite_variante_lo=lo, reussite_variante_hi=hh)
    n_o, k_o = int(hi.sum()), int((hi & ~err).sum())
    n_d, k_d = int(hid.sum()), int((hid & ~err).sum())
    po, polo, pohi, _ = M.ic_proportion(k_o, n_o)
    pd_, pdlo, pdhi, _ = M.ic_proportion(k_d, n_d)
    l.update(reussite_tache_ordinaire=po, reussite_tache_ordinaire_lo=polo, reussite_tache_ordinaire_hi=pohi,
             n_taches_ordinaires=n_o,
             reussite_3_taches_ordinaires=po ** 3, reussite_3_taches_ordinaires_lo=polo ** 3,
             reussite_3_taches_ordinaires_hi=pohi ** 3,
             reussite_tache_difficile_ordinaire=pd_, n_taches_difficiles=n_d,
             reussite_3_taches_difficiles=pd_ ** 3, reussite_3_taches_difficiles_lo=pdlo ** 3,
             reussite_3_taches_difficiles_hi=pdhi ** 3)
    tab.ajouter("epreuves", l)


def comptable(P, fl, err, dou, honore=True, ep_var=None, ep_err=None, gr=0):
    return M.Comptable(P, fl.type, err, dou, fl.u_val, honore, ep_var, ep_err, gr)


def traiter(tab, fl5, agent, mix, im):
    R5, R1 = C.R_CLES, C.R_CAS
    fl1 = fl5.sous_ensemble(R1)
    err5 = F.erreurs(fl5, agent)
    dou5 = F.doutes(fl5, agent)
    err1, dou1 = err5[:R1], dou5[:R1]
    ida = C.ID_AGENT[agent.nom]

    # ---------------- la règle
    p_main = C.params_regle(*C.REGLAGE_PRINCIPAL)
    res5 = RG.simuler_regle(fl5, agent, [p_main], graine=graine(2, ida, im, 0), err=err5, dou=dou5)
    var1 = [("regle", nreg(r, a), C.params_regle(r, a)) for (r, a) in C.REGLAGES if (r, a) != C.REGLAGE_PRINCIPAL]
    var1 += [("regle_" + nom, nreg(*C.REGLAGE_PRINCIPAL), C.params_regle(*C.REGLAGE_PRINCIPAL, **kw))
             for nom, kw in C.ABLATIONS.items()]
    if C.VERSION == "v1":  # sensibilités de la première passe (sans objet en v2)
        var1 += [("regle_oubli_faibles", nreg(*C.REGLAGE_PRINCIPAL),
                  C.params_regle(*C.REGLAGE_PRINCIPAL, oubli_faibles_au_changement=True)),
                 ("regle_plancher_glissant", nreg(*C.REGLAGE_PRINCIPAL),
                  C.params_regle(*C.REGLAGE_PRINCIPAL, plancher_glissant=True))]
    res1 = RG.simuler_regle(fl1, agent, [v[2] for v in var1], graine=graine(2, ida, im, 1), err=err1, dou=dou1)

    sorties = {}  # (regle, reglage) -> {e: out}

    def evaluer(cle, P, fl, err, dou, honore=True, ep_var=None, ep_err=None):
        cpt = comptable(P, fl, err, dou, honore, ep_var, ep_err, gr=ida * 100 + im)
        sorties[cle] = {e: cpt.evaluer(e) for e in C.VALEURS_E}
        for e in C.VALEURS_E:
            ligne_mesures(tab, mix, agent.nom, cle[0], cle[1], e, sorties[cle][e])
        return cpt

    reg_main = nreg(*C.REGLAGE_PRINCIPAL)
    d5 = res5.extraire(0)
    cpt_main = evaluer(("regle", reg_main), d5["P"], fl5, err5, dou5, True, d5["ep_var"], d5["ep_err"])
    lignes_garantie(tab, mix, agent, "regle", reg_main, p_main, d5, R5)
    lignes_promotion(tab, mix, agent, "regle", reg_main, p_main, d5, R5)
    lignes_epreuves(tab, mix, agent, "regle", reg_main, d5, fl5, err5)
    autonomie_temps(tab, mix, agent.nom, "regle", reg_main, d5["P"])
    if agent.nom in ("A8", "A2"):
        lignes_consigne(tab, mix, agent, d5, fl5.type, R5)
    comptes_par_reglage = {reg_main: (d5["comptes"], R5)}
    d1_par = {}
    for i, (regle, reg, p) in enumerate(var1):
        d1 = res1.extraire(i)
        d1_par[(regle, reg)] = (d1, p)
        evaluer((regle, reg), d1["P"], fl1, err1, dou1, True, d1["ep_var"], d1["ep_err"])
        lignes_garantie(tab, mix, agent, regle, reg, p, d1, R1)
        if regle == "regle":
            comptes_par_reglage[reg] = (d1["comptes"], R1)
            lignes_promotion(tab, mix, agent, regle, reg, p, d1, R1)
            lignes_epreuves(tab, mix, agent, regle, reg, d1, fl1, err1)
        if regle.startswith("regle_"):
            autonomie_temps(tab, mix, agent.nom, regle, reg, d1["P"])
            lignes_promotion(tab, mix, agent, regle, reg, p, d1, R1)

    # ---------------- les témoins (5 000 répétitions)
    typ5 = fl5.type
    evaluer(("tout_approuver", "-"), TM.paliers_tout_approuver(typ5), fl5, err5, dou5, honore=False)
    evaluer(("tout_valider", "-"), TM.paliers_tout_valider(typ5), fl5, err5, dou5)
    evaluer(("liste_fixe", "-"), TM.paliers_liste_fixe(typ5), fl5, err5, dou5)
    evaluer(("tri_risque", "-"), TM.paliers_tri_risque(typ5), fl5, err5, dou5)
    tr = TM.simuler_trois_reussites(fl5, err5, dou5, agent.t_change)
    cpt_tr = evaluer(("trois_reussites", "-"), tr["P"], fl5, err5, dou5)
    lignes_garantie(tab, mix, agent, "trois_reussites", "-", p_main, tr, R5, phases=["tout"])
    autonomie_temps(tab, mix, agent.nom, "trois_reussites", "-", tr["P"])
    oracles = {}
    for (r, a) in C.REGLAGES:
        reg = nreg(r, a)
        p = C.params_regle(r, a)
        if r not in oracles:
            Po = TM.paliers_oracle(typ5, agent, p)
            oracles[r] = (Po, evaluer(("oracle", "pb " + r), Po, fl5, err5, dou5))
    for j, (r, a) in enumerate(C.REGLAGES):
        reg = nreg(r, a)
        cpt_c, Rr = comptes_par_reglage[reg]
        rng = np.random.default_rng(graine(5, ida, im, j))
        Ph = TM.paliers_hasard(typ5[:Rr], cpt_c, rng)
        flr = fl5 if Rr == R5 else fl1
        evaluer(("hasard", reg), Ph, flr, err5[:Rr], dou5[:Rr])

    # ---------------- comparaisons appariées (mêmes tirages)
    for (r, a) in C.REGLAGES:
        reg = nreg(r, a)
        for e in C.VALEURS_E:
            out_r = sorties[("regle", reg)][e]
            for t in TEMOINS_CMP:
                cle_t = ("hasard", reg) if t == "hasard" else (t, "-")
                lignes_comparaison(tab, mix, agent.nom, reg, e, "regle", out_r, t, sorties[cle_t][e])
            lignes_comparaison(tab, mix, agent.nom, reg, e, "regle", out_r, "oracle",
                               sorties[("oracle", "pb " + r)][e])
    sens = ["oubli_faibles", "plancher_glissant"] if C.VERSION == "v1" else []
    for nom in list(C.ABLATIONS) + sens:
        for e in C.VALEURS_E:
            out_a = sorties[("regle_" + nom, reg_main)][e]
            lignes_comparaison(tab, mix, agent.nom, reg_main, e, "regle_" + nom, out_a, "regle",
                               {k: v[:R1] for k, v in sorties[("regle", reg_main)][e].items()})
            for t in ["tout_valider", "liste_fixe", "tri_risque"]:
                lignes_comparaison(tab, mix, agent.nom, reg_main, e, "regle_" + nom, out_a, t,
                                   sorties[(t, "-")][e])
    for e in C.VALEURS_E:
        for t in ["tout_valider", "liste_fixe", "tri_risque"]:
            lignes_comparaison(tab, mix, agent.nom, "-", e, "trois_reussites",
                               sorties[("trois_reussites", "-")][e], t, sorties[(t, "-")][e])
            lignes_comparaison(tab, mix, agent.nom, "-", e, "tout_approuver",
                               sorties[("tout_approuver", "-")][e], t, sorties[(t, "-")][e])

    # ---------------- réactivité (A6a, A6b), e = 5 %
    if agent.nom in ("A6a", "A6b"):
        e = C.E_PRINCIPAL
        rate5 = fl5.u_val < e
        dmg_main = cpt_main.err_p3 | (cpt_main.err_pre_p2 & rate5)
        lignes_reactivite(tab, mix, agent, "regle", reg_main, d5["snap"], d5["retour1"], dmg_main, typ5, R5, p_main)
        rate1 = rate5[:R1]
        for (regle, reg), (d1, p) in d1_par.items():
            if regle in ("regle", "regle_sans_remise", "regle_sans_epreuve", "regle_sans_palier_milieu",
                         "regle_plancher_glissant", "regle_oubli_faibles", "regle_sans_ponderation"):
                c1 = comptable(d1["P"], fl1, err1, dou1, True, d1["ep_var"], d1["ep_err"])
                dm = c1.err_p3 | (c1.err_pre_p2 & rate1)
                lignes_reactivite(tab, mix, agent, regle, reg, d1["snap"], d1["retour1"], dm, fl1.type, R1, p)
        dm_tr = cpt_tr.err_p3 | (cpt_tr.err_pre_p2 & rate5)
        lignes_reactivite(tab, mix, agent, "trois_reussites", "-", tr["snap"], tr["retour1"], dm_tr, typ5, R5)
        # oracle : connaît le vrai taux, retire l'autonomie au moment même de la dégradation
        Po = oracles["depart"][0]
        snap_o = np.zeros((R5, 8), dtype=np.int8)
        ret_o = np.full((R5, 8), -1, dtype=np.int32)
        q_av, q_ap = F.q_regle_par_type(agent, False), F.q_regle_par_type(agent, True)
        auto_av = q_av <= p_main.pb3 + C.TOL
        auto_ap = q_ap <= p_main.pb3 + C.TOL
        for k in range(C.N_MERITES):
            if auto_av[k]:
                snap_o[:, k] = 3
                if not auto_ap[k]:
                    ret_o[:, k] = agent.t_change
        cpt_o = oracles["depart"][1]
        dm_o = cpt_o.err_p3 | (cpt_o.err_pre_p2 & rate5)
        lignes_reactivite(tab, mix, agent, "oracle", "pb depart", snap_o, ret_o, dm_o, typ5, R5)


def balayage_garantie(tab, flux_par_mix):
    """Courbe de garantie : agents à taux constant, part des répétitions promues au palier 3."""
    qs = [0.0025, 0.005, 0.01, 0.015, 0.02, 0.03, 0.04, 0.05, 0.075, 0.10, 0.15, 0.20, 0.30]
    variantes = [C.params_regle(r, a) for (r, a) in C.REGLAGES]
    for im, (mix, fl5) in enumerate(flux_par_mix.items()):
        fl1 = fl5.sous_ensemble(C.R_CAS)
        for iq, q in enumerate(qs):
            agent = C.agent_q_constant(q)
            res = RG.simuler_regle(fl1, agent, variantes, graine=graine(6, im, iq))
            for i, (r, a) in enumerate(C.REGLAGES):
                d = res.extraire(i)
                for k in range(C.N_MERITES):
                    k3 = int((d["premier3"][:, k] >= 0).sum())
                    p, lo, hi, n = M.ic_proportion(k3, C.R_CAS)
                    tab.ajouter("garantie_courbe", dict(
                        melange=mix, reglage=nreg(r, a), q=q, type=C.TYPES[k], enjeu=C.NIVEAUX[C.ENJEU[k]],
                        pb3=float(variantes[i].pb3[k]), pm3=float(variantes[i].pm3[k]), n=n, k3=k3,
                        p3=p, p3_lo=lo, p3_hi=hi, p2plus=float((d["premier2"][:, k] >= 0).mean()),
                        part_temps_palier3=float((d["comptes"][:, k, 2].sum() / max(1, d["comptes"][:, k, :].sum())))))


def main():
    debut = time.time()
    if "--verifier-tests" in sys.argv:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", os.path.join(ICI, "tests")], cwd=ICI)
        if r.returncode != 0:
            print("Les tests ne passent pas : aucun résultat produit.")
            sys.exit(1)
    tab = Tables()
    flux_par_mix = {m: F.generer_flux(m, C.R_CLES) for m in C.MELANGES_BRUTS}
    print(f"flux tirés ({time.time() - debut:.0f} s)", flush=True)
    for im, (mix, fl5) in enumerate(flux_par_mix.items()):
        for agent in C.AGENTS:
            t0 = time.time()
            traiter(tab, fl5, agent, mix, im)
            print(f"{mix:15s} {agent.nom:11s} {time.time() - t0:5.1f} s (total {time.time() - debut:.0f} s)",
                  flush=True)
    balayage_garantie(tab, flux_par_mix)
    print(f"balayage de garantie fait (total {time.time() - debut:.0f} s)", flush=True)
    tab.ecrire()
    meta = dict(version_regle=C.VERSION, graine=C.GRAINE, horizon=C.HORIZON, r_cas=C.R_CAS, r_cles=C.R_CLES,
                duree_s=round(time.time() - debut, 1), numpy=np.__version__,
                reglage_principal=nreg(*C.REGLAGE_PRINCIPAL), valeurs_e=C.VALEURS_E)
    with open(os.path.join(DOSSIER, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"terminé en {time.time() - debut:.0f} s")


if __name__ == "__main__":
    main()
