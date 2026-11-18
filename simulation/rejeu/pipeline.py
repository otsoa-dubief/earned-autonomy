"""Orchestration d'une analyse du rejeu (PLAN_EXPERIENCE.md, 5.5 à 5.14) : configurations et scénarios, couches R0,
jackknife et bootstrap, moyennes sur les configurations délégables, intervalles et relance des cellules indécises.

`analyser` rend un objet `Analyse` : le magasin des quantités (valeur centrale, répétitions bootstrap et leurs écarts
types, valeurs jackknife), les classes calibrées, les configurations délégables, et les résumés descriptifs de la
couche R0 (autonomie, épreuves, volumes, retrait et périodes d'autonomie après la jonction).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from . import analyse as AN
from . import classes as CL
from . import config_rejeu as CR
from . import epreuves as EP
from . import intervalles as IC
from . import lots as LO
from . import mesures as ME
from . import regles as RG
from . import suites as SU
from . import types_regle as TY

NIVEAUX = TY.NIVEAUX
MOYENNES = ("moy_diff_charge", "moy_diff_exces", "moy_charge")


@dataclass
class Analyse:
    nom: str
    reglages: AN.Reglages
    magasin: AN.Magasin
    familles: dict = field(default_factory=dict)        # clé -> Famille
    classes_cal: dict = field(default_factory=dict)     # (env, modèle) -> classes du jeu de calibration
    classes_retro: dict = field(default_factory=dict)   # (env, modèle) -> classes du jeu rejoué
    delegables: dict = field(default_factory=dict)      # (env, modèle) -> bool
    jugeables: dict = field(default_factory=dict)       # (env, modèle) -> bool : au moins un type jugeable (N1)
    statuts: dict = field(default_factory=dict)         # (env, modèle) -> classes.statut_configuration (R4, 07/11)
    jeux: dict = field(default_factory=dict)            # (env, modèle) -> JeuConfiguration rejouée
    jeux_cal: dict = field(default_factory=dict)
    taches: dict = field(default_factory=dict)          # env -> tâches rejouées
    resume_r0: dict = field(default_factory=dict)       # clé de famille et mode -> résumé descriptif de R0
    options: dict = field(default_factory=dict)
    config: object = None

    def configs(self) -> list:
        return [c for c in self.familles if c[0] == "config"]

    def scenarios(self) -> list:
        return [c for c in self.familles if c[0] == "scenario"]

    def modes(self, cle) -> list:
        return [AN.suffixe_mode(self.familles[cle], a) for a in self.familles[cle].modes]


# ==========================================================================
# Résumés descriptifs de la couche R0
# ==========================================================================
def taches_porteuses(jeu, niveau: int) -> int:
    """Tâches qui portent au moins une écriture au dénominateur du niveau (« fragile » sous 30, section 8)."""
    if not jeu.n_parties:
        return 0
    t = CL.taches_ecritures(jeu)
    m = jeu.attrs["den"] & (TY.ENJEU[np.where(jeu.typ >= 0, jeu.typ, 0)] == niveau) & (jeu.typ >= 0)
    return len(set(t[m].tolist()))


def ecritures_niveau(jeu, niveau: int) -> int:
    m = jeu.attrs["den"] & (TY.ENJEU[np.where(jeu.typ >= 0, jeu.typ, 0)] == niveau) & (jeu.typ >= 0)
    return int(m.sum())


def _censure(v: np.ndarray, cens: np.ndarray, q: float) -> float:
    if v.size == 0:
        return float("nan")
    x = np.where(cens, np.inf, v.astype(float))
    return float(np.quantile(x, q, method="inverted_cdf"))


def devenus_mauvais(cl_X: Optional[dict], cl_Y: Optional[dict]) -> dict:
    """{type: lecture} des types devenus mauvais (5.10 ; M7, B1) : « principal » si l'intervalle de Y est entièrement
    au-dessus de la barre et pas celui de X ; « secondaire » si l'estimation seule de Y est au-dessus et pas celle de X."""
    out = {}
    for k in TY.TYPES_SUITE:
        y = (cl_Y or {}).get(k)
        x = (cl_X or {}).get(k, {})
        if not y or y.get("classe") == CL.SANS_DONNEE:
            continue
        if y["classe"] == CL.AU_DESSUS and x.get("classe") != CL.AU_DESSUS:
            out[k] = "principal"
        elif y["p"] > y["barre"] and not (x.get("p", 0.0) == x.get("p", 0.0) and x.get("p", 0.0) > x.get("barre", 1.0)):
            out[k] = "secondaire"
    return out


def resumer_r0(fam: AN.Famille, annonce: bool, rl: AN.ResultatLot, reglages: AN.Reglages) -> dict:
    """Résumé descriptif de la couche R0 : autonomie, épreuves, volumes ; parts des répétitions où chaque règle atteint
    le palier 3 par niveau ; délégation des témoins ; après la jonction : retrait et périodes d'autonomie."""
    s = rl.lot.suite
    m = rl.moteur
    env = fam.cle[1]
    out = dict(autonomie=[], epreuves=[], p3=dict(), delegue=dict(), retrait=[], derive=[], n_rep=s.R, charges={},
               degats={})
    for nom in rl.noms_temoins:   # charges, dégâts absolus et dégâts à part des témoins (5.12, points 1 et 2)
        lg = ME.lignes_groupe(nom, "témoin", rl.agregats(nom), s, reglages.valeurs_e, env)
        out["charges"][nom] = lg["charges"][0]
        out["degats"].update({(nom, d["e"], d["niveau"]): d["degats_absolus"] for d in lg["degats"]})
    for i, r in enumerate(rl.regles):
        sl = m.lignes(i)
        ep = rl.epreuves(r.nom)
        prom = {k: getattr(m, k)[sl] for k in ("n_prom3", "n_retraits3", "volume3")}
        lg = ME.lignes_groupe(r.nom, "règle", rl.agregats(r.nom), s, reglages.valeurs_e, env, ep, prom)
        out["charges"][r.nom] = lg["charges"][0]
        out["degats"].update({(r.nom, d["e"], d["niveau"]): d["degats_absolus"] for d in lg["degats"]})
        out["autonomie"] += lg["autonomie"]
        out["epreuves"].append(dict(regle=r.nom, **{k: float(np.mean(v)) for k, v in ep.items()}))
        for j, niv in enumerate(NIVEAUX):
            types = [k for k in TY.TYPES_SUITE if TY.ENJEU[k] == j]
            atteint = (m.premier3[sl][:, types] >= 0).any(axis=1)
            out["p3"][(r.nom, niv)] = float(atteint.mean())
    for nom in rl.noms_temoins:
        cmp = rl.agregats(nom)["comptes"].sum(axis=0)    # (NT, 3)
        for j, niv in enumerate(NIVEAUX):
            types = [k for k in TY.TYPES_SUITE if TY.ENJEU[k] == j]
            out["delegue"][(nom, niv)] = bool(cmp[types, 2].sum() > 0)
    if s.jonction is not None and m.suivi is not None:
        cl_X, cl_Y = fam.classes
        dm = devenus_mauvais(cl_X, cl_Y)
        apres = np.arange(s.T)[:, None] >= s.jonction[None, :]
        for i, r in enumerate(rl.regles):
            sl = m.lignes(i)
            for k in TY.TYPES_SUITE:
                n_apres = ((s.typ == k) & apres).sum(axis=0)
                if TY.ENJEU_HAUT[k] and n_apres.sum() > 0:
                    per = m.n_periodes[sl][:, k]
                    mx = m.max_constatees[sl][:, k]
                    out["derive"].append(dict(regle=r.nom, type=TY.SIGLES[k], niveau=TY.niveau(k), n_rep=s.R,
                                              n_rep_periodes=int((per > 0).sum()),
                                              periodes_moy=float(per.mean()), max_constatees=int(mx.max()),
                                              part_rep_plus_d_une=float((mx >= 2).mean()),
                                              constatees_moy=float(m.tot_constatees[sl][:, k].mean()),
                                              ratees_moy=float(m.tot_ratees[sl][:, k].mean()),
                                              verdict="passe" if int(mx.max()) <= 1 else "échoue"))
                if k in dm and n_apres.sum() > 0:
                    promu = m.snap[sl][:, k] == 3
                    cens = m.delai3[sl][:, k] < 0
                    dl = np.where(cens, n_apres, m.delai3[sl][:, k])
                    cw = rl.agregats(r.nom)["comptes_w"][:, k]
                    tot = cw.sum(axis=1)
                    out["retrait"].append(dict(
                        regle=r.nom, type=TY.SIGLES[k], niveau=TY.niveau(k), lecture=dm[k], n_rep=s.R,
                        n_promus=int(promu.sum()),
                        part_non_retire=float(cens[promu].mean()) if promu.any() else float("nan"),
                        delai_med=_censure(dl[promu], cens[promu], 0.5) if promu.any() else float("nan"),
                        delai_p95=_censure(dl[promu], cens[promu], 0.95) if promu.any() else float("nan"),
                        erreurs_passees_moy=float(m.err_delai[sl][promu, k].mean()) if promu.any() else float("nan"),
                        part_autonomies_nouvelles=float((m.premier3_apres[sl][:, k] >= 0).mean()),
                        part_temps_p3_apres=float((cw[:, 2].sum() / tot.sum()) if tot.sum() else float("nan"))))
    return out


# ==========================================================================
# L'analyse
# ==========================================================================
def familles_analyse(prep, entrees, config, reglages: AN.Reglages, taches_jeu: dict, taches_cal: Optional[dict],
                     nom_jeu: str, scenarios: bool, resistance: Optional[str], ordre: Optional[str], envs, modeles,
                     an: Analyse, regles_imposees: Optional[dict] = None) -> None:
    retard = LO.RETARD if resistance == "retard10" else 0
    res_lot = resistance if resistance in ("rate10", "groupees") else None
    # jeux de toutes les configurations d'abord : la règle G1 de ρ̂ replie un environnement sans erreur sur tous les
    # environnements réunis (5.13, 06/11)
    jcs = {env: {m: SU.jeu_configuration(prep, entrees, env, m, taches_jeu[env], nom_jeu) for m in modeles}
           for env in envs}
    jks = {env: {m: SU.jeu_configuration(prep, entrees, env, m, taches_cal[env], "calibration") for m in modeles}
           for env in envs} if taches_cal is not None else None
    cls_cal = CL.classes_tous_environnements(jks, config) if jks is not None else {e: {m: None for m in modeles}
                                                                                     for e in envs}
    cls_ret = CL.classes_tous_environnements(jcs, config)
    for env in envs:
        jc = jcs[env]
        an.taches[env] = list(taches_jeu[env])
        if jks is not None:
            an.jeux_cal.update({(env, m): jks[env][m] for m in modeles})
        cl_cal, cl_ret = cls_cal[env], cls_ret[env]
        pools = {}
        for m in modeles:
            pools[m] = EP.PoolEpreuves(jc[m])
            pools[m].ident = CR.MODELES.index(m) + 1
            an.jeux[(env, m)] = jc[m]
            an.classes_cal[(env, m)] = cl_cal[m]
            an.classes_retro[(env, m)] = cl_ret[m]
            # Q14 (Otsoa, 06/11) et N1 (tranché par la recherche à sa demande, 06/11) : délégable = au moins un type
            # mérité dont le taux médian (borne haute à 50 %) est au plus la barre ; jugeable : au moins un type dont le
            # volume suffirait, sans erreur, à le faire compter (garde-fou de R4). Amendement R4 (Otsoa, 07/11) :
            # dépassement établi à ρ = 1 par un type jugeable, et sa lecture au ρ̂ propre (motif publié)
            st = CL.statut_configuration(cl_cal[m], CL.rho_propre(jks[env][m]) if jks is not None else None)
            an.statuts[(env, m)] = st
            an.delegables[(env, m)] = st["delegable"]
            an.jugeables[(env, m)] = st["jugeable"]
        regles_env = (regles_imposees or {}).get(env) or RG.regles(env, config, reglages.noms_regles)
        for m in modeles:
            cle = ("config", env, m)
            an.familles[cle] = AN.Famille(cle, jc[m], AN.fabrique_config(pools[m]), (cl_cal[m], None),
                                          (cl_ret[m], None), regles_env, (False,), resistance=res_lot, retard=retard,
                                          ordre=ordre)
        if scenarios:
            for X, Y in LO.couples(modeles):
                jcomb, _ = LO.jeu_combine(jc[X], jc[Y])
                cle = ("scenario", env, X, Y)
                an.familles[cle] = AN.Famille(cle, jcomb, AN.fabrique_scenario(pools[X], pools[Y]),
                                              (cl_cal[X], cl_cal[Y]), (cl_ret[X], cl_ret[Y]), regles_env,
                                              (True, False), jX=jc[X], jY=jc[Y], resistance=res_lot, retard=retard)


def _strates_env(an: Analyse, env: str) -> np.ndarray:
    """Strate de chaque tâche canonique d'un environnement (les mêmes tâches pour tous les modèles)."""
    jeu = next(j for (e, _m), j in an.jeux.items() if e == env)
    return LO.taches_canoniques(jeu)[2]


def _couches_famille(an: Analyse, cle, reglages: AN.Reglages, reps, K_jack: int, R0: bool, jack: bool) -> dict:
    """R0 et jackknife d'une famille ; rend les influences par grappe de la couche R0 (moyennes)."""
    fam = an.familles[cle]
    mag = an.magasin
    zr0 = {}
    if R0:
        lot0 = fam.lot("R0", reglages)
        for annonce in fam.modes:
            rl = fam.rejouer(lot0, reglages, annonce)
            zr0 = AN.enregistrer_groupes(mag, fam, annonce, rl, reglages, "R0") or zr0
            cm = AN.suffixe_mode(fam, annonce)
            an.resume_r0[cm] = resumer_r0(fam, annonce, rl, reglages)
            cl = fam.classes[1] if fam.scenario else fam.classes[0]
            for (r, k), v in AN.garantie_groupes(rl, cl, apres=fam.scenario).items():
                mag.q(("garantie",) + cm + (r, TY.SIGLES[k])).centre = float(v[0])
    if jack:
        base = fam.lot("R0", reglages, K=K_jack)
        lj = LO.lot_jackknife(base)
        st = base.strate_grappe
        for annonce in fam.modes:
            rl = fam.rejouer(lj, reglages, annonce, grappes=False)
            AN.enregistrer_groupes(mag, fam, annonce, rl, reglages, "jackknife")
            cm = AN.suffixe_mode(fam, annonce)
            cl = fam.classes[1] if fam.scenario else fam.classes[0]
            for (r, k), v in AN.garantie_groupes(rl, cl, apres=fam.scenario).items():
                mag.q(("garantie",) + cm + (r, TY.SIGLES[k])).jack = v
            for c, q in mag.items():
                if tuple(c[1:1 + len(cm)]) == cm:
                    q.strates_jack = st
                    q.G = int(lj.G)
    return zr0


def _bootstrap_famille(an: Analyse, cle, reglages: AN.Reglages, reps) -> dict:
    fam = an.familles[cle]
    lotb = fam.lot("bootstrap", reglages, reps=reps)
    z = {}
    for annonce in fam.modes:
        rl = fam.rejouer(lotb, reglages, annonce)
        z = AN.enregistrer_groupes(an.magasin, fam, annonce, rl, reglages, "bootstrap") or z
        cm = AN.suffixe_mode(fam, annonce)
        cl = fam.classes[1] if fam.scenario else fam.classes[0]
        for (r, k), v in AN.garantie_groupes(rl, cl, apres=fam.scenario).items():
            an.magasin.q(("garantie",) + cm + (r, TY.SIGLES[k])).boot += v
    return z


def _cle_config(type_moy: str, cle_conf: tuple, reste: tuple, e: float) -> tuple:
    if type_moy == "moy_diff_charge":
        return ("diff_charge",) + cle_conf + reste
    if type_moy == "moy_diff_exces":
        return ("diff_exces",) + cle_conf + reste
    return ("charge",) + cle_conf + reste + (e,)


def _poser_moyennes(an: Analyse, zsum: dict, couche: str, n_rep: int) -> None:
    """Moyennes sur les configurations délégables, répétition par répétition (5.13) ; écart type linéarisé par les
    influences des grappes, sommées sur les configurations d'un environnement (tirage commun des tâches)."""
    dele = [c for c in an.configs() if an.delegables.get((c[1], c[2]))]
    if not dele:
        return
    C = len(dele)
    e = an.reglages.e_principal
    cles_moy = {k[:-1] for k in zsum} if zsum else set()
    if not cles_moy:
        # sans influences (jackknife) : les clés viennent des quantités de configuration
        cles_moy = {("moy_diff_charge", r, t) for r in an.reglages.noms_regles
                    for t in list(AN.TEMOINS_DIFF) + [f"hasard_{r}"]}
        cles_moy |= {("moy_diff_exces", r, n) for r in an.reglages.noms_regles for n in NIVEAUX}
        cles_moy |= {("moy_charge", r) for r in an.reglages.noms_regles}
    for km in cles_moy:
        vals = []
        for c in dele:
            q = an.magasin.get(_cle_config(km[0], c, km[1:], e))
            if q is None:
                break
            vals.append(q)
        if len(vals) != C:
            continue
        qm = an.magasin.q(km)
        if couche == "R0":
            qm.centre = float(np.mean([q.centre for q in vals]))
            se2 = 0.0
            for env in sorted({c[1] for c in dele}):
                z = zsum.get(km + (env,))
                if z is not None:
                    se2 += float(AN.se_depuis_z(z[0] / C, _strates_env(an, env)) ** 2)
            qm.se = 100.0 * math.sqrt(se2)
        elif couche == "bootstrap":
            b = np.mean([np.asarray(q.boot[-n_rep:], dtype=float) for q in vals], axis=0)
            qm.boot += b
            se2 = np.zeros(n_rep)
            for env in sorted({c[1] for c in dele}):
                z = zsum.get(km + (env,))
                if z is not None:
                    se2 += AN.se_depuis_z(z / C, _strates_env(an, env)) ** 2
            qm.se_boot += 100.0 * np.sqrt(se2)
        elif couche == "jackknife":
            centres = np.array([q.centre for q in vals])
            jacks, strates, G = [], [], 0
            for env in sorted({c[1] for c in an.configs()}):
                idx = [i for i, c in enumerate(dele) if c[1] == env]
                if not idx:
                    continue
                st = _strates_env(an, env)
                for g in range(len(st)):
                    v = centres.copy()
                    for i in idx:
                        jv = vals[i].jack
                        v[i] = jv[g] if jv is not None and g < len(jv) else centres[i]
                    jacks.append(float(v.mean()))
                    strates.append(f"{env}:{st[g]}")
                G += len(st)
            qm.jack = np.array(jacks)
            _, codes = np.unique(np.array(strates), return_inverse=True)
            qm.strates_jack = codes
            qm.G = G


def taches_familles(an: Analyse) -> list:
    """Les tâches de calcul, dans un ordre fixe : par environnement, ses trois configurations ensemble (leurs influences
    s'additionnent pour les moyennes : tirage commun), puis chaque scénario."""
    taches = []
    for env in dict.fromkeys(c[1] for c in an.familles):
        conf = [c for c in an.familles if c[0] == "config" and c[1] == env]
        if conf:
            taches.append((env, conf))
        taches += [(env, [c]) for c in an.familles if c[0] == "scenario" and c[1] == env]
    return taches


def travail_familles(args) -> dict:
    """Couches R0, jackknife et bootstrap d'un groupe de familles (exécutable dans un autre processus). Rend le
    magasin de ces familles, leurs résumés R0, et les influences par grappe, sommées sur les configurations délégables
    du groupe (couche R0 ; et bootstrap, toutes tranches mises bout à bout)."""
    cles, familles, delegables, reglages, jackknife, bootstrap = args
    mini = Analyse("travail", reglages, AN.Magasin(), familles=familles, delegables=delegables)
    dele = lambda c: c[0] == "config" and delegables.get((c[1], c[2]))  # noqa: E731
    zr0, zb = {}, {}
    for cle in cles:
        z = _couches_famille(mini, cle, reglages, None, reglages.K, True, jackknife)
        if dele(cle):
            for k, v in z.items():
                zr0[k] = zr0.get(k, 0) + v
    if bootstrap:
        morceaux = {}
        for b0 in range(0, reglages.B, reglages.tranche):
            reps = list(range(b0, min(reglages.B, b0 + reglages.tranche)))
            zt = {}
            for cle in cles:
                z = _bootstrap_famille(mini, cle, reglages, reps)
                if dele(cle):
                    for k, v in z.items():
                        zt[k] = zt.get(k, 0) + v
            for k, v in zt.items():
                morceaux.setdefault(k, []).append(v)
        zb = {k: np.concatenate(v, axis=0) for k, v in morceaux.items()}
    return dict(magasin=dict(mini.magasin), resume_r0=mini.resume_r0, zr0=zr0, zb=zb)


def analyser(entrees, prep, config, reglages: AN.Reglages, taches_jeu: dict, taches_cal: Optional[dict],
             nom: str = "principale", nom_jeu: str = "confirmation", scenarios: bool = True,
             resistance: Optional[str] = None, ordre: Optional[str] = None, bootstrap: bool = True,
             jackknife: bool = True, envs=None, modeles=CR.MODELES, processus: int = 1,
             regles_imposees: Optional[dict] = None) -> Analyse:
    """Une analyse complète d'un jeu de tâches (configurations et, si demandé, scénarios). Les familles sont calculées
    par groupes, dans `processus` processus ; le résultat ne dépend pas de ce nombre (graines par famille, assemblage
    dans un ordre fixe)."""
    envs = list(envs or [e for e in CR.ENVIRONNEMENTS if e in taches_jeu])
    an = Analyse(nom, reglages, AN.Magasin(), options=dict(nom_jeu=nom_jeu, resistance=resistance, ordre=ordre,
                                                           scenarios=scenarios))
    an.config = config
    familles_analyse(prep, entrees, config, reglages, taches_jeu, taches_cal, nom_jeu, scenarios, resistance, ordre,
                     envs, modeles, an, regles_imposees)
    taches = taches_familles(an)
    args = [(cles, {c: an.familles[c] for c in cles}, {k: v for k, v in an.delegables.items() if k[0] == env},
             reglages, jackknife, bootstrap) for env, cles in taches]
    if processus > 1 and len(args) > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=processus) as ex:
            resultats = list(ex.map(travail_familles, args))
    else:
        resultats = [travail_familles(a) for a in args]
    zr0, zb = {}, {}
    for (env, _cles), res in zip(taches, resultats):
        an.magasin.update(res["magasin"])
        an.resume_r0.update(res["resume_r0"])
        for k, v in res["zr0"].items():
            zr0[k + (env,)] = v
        for k, v in res["zb"].items():
            zb[k + (env,)] = v
    _poser_moyennes(an, zr0, "R0", 1)
    if jackknife:
        _poser_moyennes(an, {}, "jackknife", 0)
    if bootstrap:
        _poser_moyennes(an, zb, "bootstrap", reglages.B)
    poser_s_sur_q(an, reglages if bootstrap else AN.Reglages(**{**reglages.__dict__, "B": 0}))
    return an


# ==========================================================================
# Intervalles, verdicts et relance
# ==========================================================================
def intervalles_quantite(q: AN.Quantite, choix: dict, B: Optional[int] = None) -> dict:
    """Intervalles d'une quantité : méthode retenue, seconde méthode, et les quatre lectures (rapportées)."""
    if B is not None and len(q.boot) > B and not q.info.get("relance"):
        q = AN.Quantite(q.centre, q.se, q.boot[:B], q.se_boot[:B], q.jack, q.strates_jack, q.G, q.info)
    out = {}
    for m in ("i", "ii", "iii", "percentile"):
        out[m] = q.intervalle(m)
    ret = choix["methode"]
    sec = choix.get("methode_seconde") or IC.methode_seconde(ret)
    out["retenue"] = out[ret]
    out["seconde"] = out[sec]
    out["methode_effective"] = ret if (ret != "ii" or q.a_se) else "i"
    return out


def verdict_cellule(q: AN.Quantite, budget: float, choix: dict, B: Optional[int] = None) -> dict:
    iv = intervalles_quantite(q, choix, B)
    v = IC.verdict(*iv["retenue"], budget)
    v2 = IC.verdict(*iv["seconde"], budget)
    return dict(intervalles=iv, verdict=v, verdict_seconde=v2, diverge=v != v2)


def _comptes_taches_niveaux(jeu, index: dict) -> tuple:
    """Par tâche canonique : écritures au dénominateur non plafonnées de chaque niveau (3, G) et écritures au
    dénominateur (G,)."""
    G = len(index)
    t = CL.taches_ecritures(jeu)
    gi = np.array([index.get(x, -1) for x in t.tolist()], dtype=np.int64)
    ok = gi >= 0
    den = jeu.attrs["den"] & ok & (jeu.typ >= 0)
    niv = TY.ENJEU[np.where(jeu.typ >= 0, jeu.typ, 0)]
    d = np.bincount(gi[den], minlength=G).astype(float)
    a = np.stack([np.bincount(gi[den & ~jeu.attrs["plaf"] & (niv == j)], minlength=G) for j in range(3)])
    return a.astype(float), d


def poser_s_sur_q(an: Analyse, reglages: AN.Reglages) -> None:
    """s ÷ q de chaque cellule (1.4, RF3 ; 5.14, point 1, Q13) : s = écritures au dénominateur non plafonnées du niveau
    ÷ écritures au dénominateur, dans la suite rejouée ; q = la part attendue du point 9 (`config_rejeu.json`). Valeur
    centrale, écart type linéarisé, répétitions bootstrap (le même tirage commun des tâches que le rejeu) et jackknife :
    s ne dépend que des tâches tirées, pas de la règle."""
    cache = {}
    B = reglages.B
    for cle, fam in an.familles.items():
        env = cle[1]
        base = fam.jX if fam.scenario else fam.jeu
        taches, index, strates, _ = LO.taches_canoniques(base)
        a, d = _comptes_taches_niveaux(fam.jeu, index)
        G = len(taches)
        idx = None
        if B > 0 and G:
            kc = (env, base.jeu, B)
            if kc not in cache:
                lignes = []
                for b in range(B):
                    tir = LO.tirage_commun(reglages.G0, env, b, base.jeu, base.strates)
                    dec, cols = 0, []
                    for s_, ts in base.strates.items():
                        cols.append(dec + tir[s_])
                        dec += len(ts)
                    lignes.append(np.concatenate(cols))
                cache[kc] = np.array(lignes, dtype=np.int64)
            idx = cache[kc]
        D = d.sum()
        for j, niv in enumerate(NIVEAUX):
            qv = float(an.config.q[(env, niv)])
            A = a[j].sum()
            vals = dict(centre=A / D / qv if D else float("nan"),
                        se=float(IC.se_rapport(a[j], d, strates)) / qv if D else float("nan"))
            with np.errstate(divide="ignore", invalid="ignore"):
                jack = np.where(D - d > 0, (A - a[j]) / np.where(D - d > 0, D - d, 1.0), np.nan) / qv
            boot = se_boot = None
            if idx is not None:
                ao, do = a[j][idx], d[idx]
                with np.errstate(divide="ignore", invalid="ignore"):
                    boot = np.where(do.sum(axis=1) > 0, ao.sum(axis=1) / np.maximum(do.sum(axis=1), 1), np.nan) / qv
                se_boot = IC.se_rapport(ao, do, strates) / qv
            for cm in an.modes(cle):
                q = an.magasin.q(("s_sur_q",) + cm + (niv,))
                q.centre, q.se = vals["centre"], vals["se"]
                q.jack, q.strates_jack, q.G = jack, strates, G
                if boot is not None:
                    q.boot, q.se_boot = AN._Morceaux(boot), AN._Morceaux(se_boot)
