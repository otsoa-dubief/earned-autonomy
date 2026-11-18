"""Une répétition d'un monde fictif, de la génération des entrées à l'étiquette (PLAN_EXPERIENCE.md, 5.14).

La chaîne est celle du rejeu final (`rejeu.bout_en_bout.executer`, analyse principale et point 5) : preuves (5.4),
suites et rejeu (5.5 à 5.11) des configurations et des 48 scénarios, classes calibrées et configurations délégables
(5.12, point 4 ; 5.13), max-T de B-tout (5.14, point 1, Q13), réussite face aux témoins (point 2), hasard (point 3,
sans effet), point 4, étiquette (point 5) ; désaccord persistant (B2) : la même analyse avec les verdicts bruts des
vagues concernées, et l'étiquette la moins favorable. Les analyses secondaires (point 6) n'entrent pas dans
l'étiquette : elles ne sont pas refaites.

Seule différence de réglage, déclarée (RAPPORT.md) : R0 et B réduits, et seule B-tout est rejouée parmi les quatre
règles (les trois autres n'entrent pas dans l'étiquette ; un test du moteur vérifie déjà que le résultat d'une règle
ne dépend pas des autres, 5.16, point 7). Les autres réglages sont ceux du plan : K = 10, e = 5 %, méthode des
intervalles lue dans `rejeu/resultats_couverture_charge/` (jackknife-t).
"""
from __future__ import annotations

import functools
import math
import time
from dataclasses import dataclass

import numpy as np

from rejeu import analyse as AN
from rejeu import bout_en_bout as BE
from rejeu import classes as CL
from rejeu import config_rejeu as CR
from rejeu import decision as DE
from rejeu import pipeline as PL
from rejeu import preuves as PR
from rejeu import regles as RG
from rejeu import types_regle as TY

from . import mondes as MD


@dataclass(frozen=True)
class Parametres:
    R0: int
    B: int
    K: int
    tranche: int
    graine: int


@functools.lru_cache(maxsize=None)
def config():
    return CR.charger_config()


@functools.lru_cache(maxsize=None)
def choix_methode() -> dict:
    return BE.choix_methode()


N_INERTE = 10 ** 9   # jamais atteint : aucune suite n'a autant d'écritures d'un type


def regles_monde(monde: MD.Monde, cfg) -> dict:
    """B-tout rejouée avec N × facteur (au moins 1 pour les types mérités) ; règle inerte : N immense et aucun palier 2
    (décision 4 : le palier 2 est une délégation ; 5.14, point 2, lecture du 06/11) ; None : la règle figée."""
    if monde.facteur_N is None and not monde.inerte:
        return None
    out = {}
    for env in MD.ENVS:
        r = RG.regle("B-tout", env, cfg)
        if monde.inerte:
            p = r.params
            params = RG._params("B-tout", p.pb2, p.pm2, p.pb3, p.pm3, np.zeros(TY.NT, dtype=bool), alpha=p.alpha)
            out[env] = [RG.variante(r, "B-tout", N=np.where(TY.MERITE, N_INERTE, 0), params=params)]
        else:
            N = np.where(TY.MERITE, np.maximum(1, np.floor(r.N * monde.facteur_N)), 0).astype(np.int64)
            out[env] = [RG.variante(r, "B-tout", N=N)]
    return out


def graine_repetition(params: Parametres, monde: MD.Monde, rep: int) -> np.random.SeedSequence:
    return np.random.SeedSequence([int(params.graine), MD.MONDES.index(monde), int(rep)])


def _f(x) -> float:
    x = float(x)
    return x if math.isfinite(x) else None


def resume_classes(an) -> dict:
    out = {}
    for (env, mod), cl in sorted(an.classes_cal.items()):
        if not cl:
            continue
        out[f"{env}/{mod}"] = {TY.SIGLES[k]: dict(classe=c["classe"], classe_hyp=c.get("classe_sous_hypothese"),
                                                  n=c["n"], x=c["x"], n_eff=_f(c["n_eff"]),
                                                  p_sur_barre=_f(c["p"] / c["barre"]) if c["n"] else None,
                                                  hi_sur_barre=_f(c["hi"] / c["barre"]), rho=_f(c["rho"]),
                                                  source_rho=c["source_rho"])
                               for k, c in cl.items() if c["n"] > 0}
    return out


def resume_oracle(an) -> dict:
    """Oracle avec palier 2 (5.7 ; Q14 : palier 3 si le taux estimé est au plus la barre), descriptif : cellules de
    configuration où il délègue à enjeu moyen ou fort, et sa plus haute valeur centrale de dégâts en plus ÷ budget."""
    e = an.reglages.e_principal
    deleg_haut, rapports = 0, []
    for cm in an.configs():
        r0 = an.resume_r0.get(cm, {})
        for niv in ("moyen", "fort"):
            deleg_haut += bool(r0.get("delegue", {}).get(("oracle_p2", niv), False))
        for niv in DE.NIVEAUX:
            q = an.magasin.get(("budget",) + cm + ("oracle_p2", e, niv))
            if q is not None and q.centre == q.centre:
                rapports.append(q.centre / float(CR.BUDGET[niv]))
    return dict(cellules_moyen_fort_deleguees=deleg_haut, max_centre_sur_budget=_f(max(rapports, default=0.0)))


def resume_decision(dec: dict, an) -> dict:
    p1 = dec["point1"]
    cel = p1["cellules"]
    jug = [c for c in cel if c["statut"] == DE.JUGEE]
    est = [c for c in jug if c["verdict"] == DE.ETABLI]
    hh = [c for c in cel if c.get("garantie_hors_hypothese")]
    out = dict(
        etiquette=dec["etiquette"], mention=dec.get("mention", ""), oracle=resume_oracle(an),
        p0=dict(tenu=dec["point0"]["tenu"], couverture=_f(dec["point0"]["couverture"]),
                relecture_ok=dec["point0"]["relecture_ok"]),
        p1=dict(tenu=p1["tenu"], m=len(jug), non_eprouvees=sum(c["statut"] == DE.NON_EPROUVEE for c in cel),
                sans_objet=sum(c["statut"] == DE.SANS_OBJET for c in cel),
                c_etoile=_f(jug[0].get("c_etoile", float("nan"))) if jug else None,
                etablies=[dict(famille="/".join(map(str, c["famille"])), niveau=c["niveau"], centre=_f(c["centre"]),
                               borne=_f(c.get("borne_maxt", float("nan"))), budget=c["budget"]) for c in est],
                max_centre_sur_budget=_f(max((c["centre"] / c["budget"] for c in jug), default=0.0)),
                max_borne_sur_budget=_f(max((c["borne_maxt"] / c["budget"] for c in jug
                                             if math.isfinite(c.get("borne_maxt", math.nan))), default=-math.inf)),
                # sixième passage : cellules non testables (plan, 5.14, point 2, amendé le 07/11)
                non_testables=sum(bool(c.get("non_testable")) for c in jug),
                demontrees=sum(bool(c.get("demontree")) for c in jug),
                hors_hypothese=[dict(famille="/".join(map(str, c["famille"])), niveau=c["niveau"],
                                     statut=c["statut"], s_sur_q=_f(c["s_sur_q"]), lo=_f(c["s_sur_q_lo"]))
                                for c in hh],
                configs_p3={"/".join(c["famille"][1:]) + "/" + c["niveau"]: _f(c["part_rep_p3"])
                            for c in cel if c["famille"][0] == "config" and c["statut"] == DE.JUGEE},
                # cinquième passage : lecture de B-seuil (dépassement réalisé, cellule par cellule)
                centres_config={"/".join(c["famille"][1:]) + "/" + c["niveau"]: _f(c["centre"] / c["budget"])
                                for c in cel if c["famille"][0] == "config" and c["statut"] == DE.JUGEE}),
        p2={}, p3=dec["point3"]["conclusion"],
        p4=dict(delegables=["/".join(c) for c in dec["point4"]["delegables"]],
                sans_type_jugeable=["/".join(c) for c in dec["point4"].get("sans_type_jugeable", [])]),
        classes=resume_classes(an))
    for t, v in dec["point2"]["temoins"].items():
        dep = v["depassement"]
        cel_t = dep["cellules"]
        out["p2"][t] = dict(battu=v["battu"], battu_partout=v["battu_partout"], battu_charge=v["battu_charge"],
                            m=dep["m"], c_etoile=_f(dep["c_etoile"]), n_etablies=len(dep["etablies"]),
                            max_centre_sur_budget=_f(max((c["centre"] / c["budget"] for c in cel_t), default=0.0)),
                            max_borne_sur_budget=_f(max((c["borne"] / c["budget"] for c in cel_t
                                                         if math.isfinite(c["borne"])), default=-math.inf)),
                            non_testables=sum(bool(c.get("non_testable")) for c in cel_t),
                            diff_moyenne=_f(v["diff_moyenne"]), intervalle=[_f(x) for x in v["intervalle"]])
    return out


def repetition(nom_monde: str, rep: int, params: Parametres) -> dict:
    """Une répétition : génération, analyse principale, décision ; rend l'étiquette et les diagnostics."""
    t0 = time.time()
    monde = MD.MONDES_PAR_NOM[nom_monde]
    cfg = config()
    ss = graine_repetition(params, monde, rep)
    g_gen, g_moteur = ss.spawn(2)
    rng = np.random.default_rng(g_gen)
    g = MD.generer(monde, rng, cfg)
    e = g["entrees"]
    t1 = time.time()
    prep = PR.preparer(e, "confirmes")
    G0 = int(g_moteur.generate_state(1, np.uint64)[0] >> np.uint64(1))
    reg = AN.Reglages(G0=G0, R0=params.R0, B=params.B, K=params.K, tranche=params.tranche, valeurs_e=(CR.E_PRINCIPAL,),
                      noms_regles=("B-tout",), choix=choix_methode())
    regles = regles_monde(monde, cfg)
    an = PL.analyser(e, prep, cfg, reg, g["conf"], g["cal"], processus=1, regles_imposees=regles)
    p0 = DE.point0(e, prep)
    dec = DE.decider(an, p0)
    out = resume_decision(dec, an)
    out["etiquette_principale"] = out["etiquette"]
    if p0["persistantes"]:   # désaccord persistant (B2) : verdicts bruts pour ces vagues, la moins favorable
        prep_bv = PR.preparer(e, "bruts_vague", p0["persistantes"])
        an_bv = PL.analyser(e, prep_bv, cfg, reg, g["conf"], g["cal"], processus=1, regles_imposees=regles)
        e_bv = DE.decider(an_bv, DE.point0(e, prep_bv))["etiquette"]
        out["etiquette"] = DE.moins_favorable(out["etiquette"], e_bv)
        out["b2"] = dict(vagues=p0["persistantes"], etiquette_bruts_vague=e_bv)
    res = PR.resume(prep)
    out.update(monde=nom_monde, rep=int(rep), G0=G0, attendu=monde.attendu,
               volumes=dict(parties=res["parties"], ecritures=res["ecritures"], erreurs=res["erreurs_preuve"],
                            plafonnees=res["plafonnees"], doutes=res["doutes"], lectures=res["lectures"]),
               duree_generation=round(t1 - t0, 2), duree=round(time.time() - t0, 2))
    return out


# --------------------------------------------------------------------------
# Étude de délégabilité : le point 4 seul (5.12, point 4 ; 5.13), sans rejeu
# --------------------------------------------------------------------------
RHOS_HETEROGENES = (0.1, 0.3, 0.7, 0.9)   # quatrième passage : ρ tiré par (environnement, type)


def monde_delegabilite(multiple: float, rho: float, temoins: bool, mecanisme: str = "beta") -> MD.Monde:
    """Tous les types au même multiple de la barre ; avec `temoins`, l'écriture réversible de WorkBench à 10 × barre
    chez Sonnet et Opus, comme dans le monde A. mecanisme : « beta », « logit_normal » (ρ latent) ou « heterogene » (ρ
    tiré parmi RHOS_HETEROGENES pour chaque environnement et type ; `rho` est alors ignoré)."""
    het = mecanisme == "heterogene"
    return MD.Monde(f"delegabilite-{multiple:g}-{rho:g}-{int(temoins)}-{mecanisme}", "étude de délégabilité", "",
                    multiple, MD.TEMOINS_EN_DEFAUT_10 if temoins else (), rho=rho,
                    mecanisme="beta" if het else mecanisme, rhos_heterogenes=RHOS_HETEROGENES if het else ())


def delegabilite(multiple: float, rho: float, temoins: bool, rep: int, graine: int, case: int,
                 mecanisme: str = "beta") -> dict:
    """Classes calibrées et configurations délégables d'une répétition (aucune règle n'est rejouée), avec la règle du
    rejeu : ρ̂ selon la règle N3 (`classes.classes_tous_environnements`, comme `pipeline.familles_analyse`) ; délégable
    = au moins un type mérité dont le taux médian est au plus la barre (Q14 et N1, `classes.estime_sous`). Le classement
    prouvé (« sous la barre » : borne haute à 95 % au plus la barre, sur la taille effective à ρ = 1, N3) est relevé à
    part, ainsi que le classement sous hypothèse (même borne sur la taille effective à ρ̂)."""
    from rejeu import suites as SU
    cfg = config()
    monde = monde_delegabilite(multiple, rho, temoins, mecanisme)
    rng = np.random.default_rng(np.random.SeedSequence([int(graine), 1000 + int(case), int(rep)]))
    g = MD.generer(monde, rng, cfg)
    e = g["entrees"]
    prep = PR.preparer(e, "confirmes")
    jks = {env: {m: SU.jeu_configuration(prep, e, env, m, g["cal"][env], "calibration") for m in CR.MODELES}
           for env in MD.ENVS}
    cls = CL.classes_tous_environnements(jks, cfg)
    dele, dele_faible, dele_prouve, dele_hyp, estimes, faibles = [], [], [], [], [], {}
    for env in MD.ENVS:
        for m, c in cls[env].items():
            cm = f"{env}/{m.split('-')[1]}"     # claude-haiku-5-5 -> haiku (sorties compactes)
            if any(CL.estime_sous(v) for v in c.values()):
                dele.append(cm)
            if any(CL.estime_sous(v) for k, v in c.items() if TY.ENJEU[k] == TY.FAIBLE):
                dele_faible.append(cm)
            if any(v["classe"] == CL.SOUS for v in c.values()):
                dele_prouve.append(cm)
            if any(v.get("classe_sous_hypothese") == CL.SOUS for v in c.values()):
                dele_hyp.append(cm)
            for k, v in c.items():
                if v["n"] <= 0:
                    continue
                if CL.estime_sous(v):
                    estimes.append(f"{cm}/{TY.SIGLES[k]}")
                if TY.ENJEU[k] == TY.FAIBLE:   # [classe, x, n, borne haute ÷ barre, ρ̂, source de ρ̂, classe sous
                    # hypothèse] ; la classe et sa borne sur la taille effective à ρ = 1 (N3)
                    faibles[f"{cm}/{TY.SIGLES[k]}"] = [CODES_CLASSE.get(v["classe"], "?"), int(v["x"]), int(v["n"]),
                                                       round(float(v["hi"] / v["barre"]), 4), round(float(v["rho"]), 4),
                                                       CL.SOURCES_G1.index(v["source_rho"])
                                                       if v["source_rho"] in CL.SOURCES_G1 else -1,
                                                       CODES_CLASSE.get(v.get("classe_sous_hypothese"), "?")]
    return dict(multiple=multiple, rho=rho, temoins=temoins, mecanisme=mecanisme, rep=int(rep), delegables=dele,
                delegables_faibles=dele_faible, delegables_prouvees=dele_prouve,
                delegables_prouvees_hypothese=dele_hyp, estimes_sous=estimes, faibles=faibles)


CODES_CLASSE = {CL.SOUS: "S", CL.AU_DESSUS: "A", CL.INDETERMINE: "I", CL.SANS_DONNEE: "0"}
