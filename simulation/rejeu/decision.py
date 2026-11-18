"""Règle de décision appliquée aux résultats (PLAN_EXPERIENCE.md, 5.14), points 0 à 6, mentions « fragile », règle
de choix réappliquée (1.3, point 4), comparaison au hasard (Q7) et alerte des tests de résistance (5.11).

Ordre des étiquettes (C6) : R5, R1, « preuves insuffisantes », R4, R2, puis « confirmée » ; « la moins favorable » de
deux étiquettes est celle qui vient d'abord dans cet ordre (désaccord persistant, décision B2). « Preuves
insuffisantes » remplace « volume insuffisant » (amendement R4, Otsoa, 07/11) et garde son rang : un constat négatif
doit tenir dans les deux calculs.
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np

from . import classes as CL
from . import config_rejeu as CR
from . import intervalles as IC
from . import maxt as MX
from . import pipeline as PL
from . import preuves as PR
from . import regles as RG
from . import types_regle as TY
from .entrees import accord

# Amendement R4 (Otsoa, 07/11, avant toute donnée d'évaluation) : « preuves insuffisantes » remplace « volume
# insuffisant » (N1, 06/11) ; son motif est publié avec l'étiquette
PREUVES_INSUFFISANTES = "preuves insuffisantes"
MOTIF_AUCUN_JUGEABLE = "aucun type jugeable"
MOTIF_NON_ETABLI = "dépassement non établi"
MOTIF_RHO_PROPRE = "dépassement établi sous ρ̂ propre, pas à ρ = 1"
ORDRE_ETIQUETTES = ("R5", "R1", PREUVES_INSUFFISANTES, "R4", "R2", "confirmée")
CONCLUSIONS_GARDEES = (accord.GARDEE, accord.GARDEE_SECOND_TOUR, accord.PERSISTANT)
SANS_OBJET, NON_EPROUVEE, JUGEE = "sans objet", "tenue, non mise à l'épreuve", "jugée"
NON_CALCULE = "non calculé (sans bootstrap)"   # le max-T n'a pas tourné : point 1 non calculé (C13, M3)
SEUIL_PORTEUSES = 30
SEUIL_EGALITE = 1.0          # « à moins d'un point d'écart » (1.3, point 4)
NIVEAUX = TY.NIVEAUX


def moins_favorable(*etiquettes) -> str:
    return min(etiquettes, key=ORDRE_ETIQUETTES.index)


# ==========================================================================
# Point 0 : validité de l'instrument
# ==========================================================================
def point0(entrees, preparees: dict, seuil: float = 0.95) -> dict:
    """Chaque vague a fini en « relecture gardée » (premier ou second tour) ou suit la règle du désaccord persistant,
    et la couverture de l'instrument (part d'écritures vérifiables ; ce n'est pas d) est au moins 0,95."""
    res = PR.resume(preparees)
    vagues = sorted({p.vague for p in entrees.parties if not entrees.retiree(p)})
    etat = {}
    for v in vagues:
        c = entrees.jointure.conclusions.get(v)
        etat[v] = c if c is not None else "non relue à l'aveugle (aucun bilan d'accord)"
    relecture_ok = all(etat[v] in CONCLUSIONS_GARDEES for v in vagues)
    couverture = res["couverture"]
    return dict(tenu=bool(relecture_ok and couverture == couverture and couverture >= seuil), vagues=etat,
                relecture_ok=relecture_ok, couverture=couverture, seuil=seuil, ecritures=res["ecritures"],
                verifiables=res["verifiables"],
                persistantes=sorted(v for v, p in entrees.jointure.desaccord_persistant.items() if p))


def instrument(entrees, preparees: dict) -> dict:
    """Instrument (5.12, point 11) : alertes, confirmées, levées par motif ; couverture de l'instrument (sur toutes
    les écritures des suites, et hors effet illisible) ; tâches retirées."""
    from .entrees import CONFIRMEE, LEVEE
    j = entrees.jointure
    decs = [j.decisions[a] for a in j.alertes.values() if a in j.decisions]
    par_motif: dict = {}
    for d in decs:
        if d.decision == LEVEE:
            par_motif[d.motif or "(sans motif : levée d'Otsoa)"] = par_motif.get(d.motif or "(sans motif : levée d'Otsoa)",
                                                                                 0) + 1
    res = PR.resume(preparees)
    n_ill = sum(int((e.typ == TY.ILL).sum()) for e in preparees.values())
    v_ill = sum(int(((e.typ == TY.ILL) & e.ver).sum()) for e in preparees.values())
    hors = res["ecritures"] - n_ill
    return dict(alertes=len(j.alertes), confirmees=sum(1 for d in decs if d.decision == CONFIRMEE),
                levees=sum(1 for d in decs if d.decision == LEVEE), levees_par_motif=par_motif,
                obsoletes=len(j.obsoletes), sans_decision=len(j.sans_decision), couverture=res["couverture"],
                couverture_hors_illisible=(res["verifiables"] - v_ill) / hors if hors else float("nan"),
                taches_retirees={f"{e}/{t}": r for (e, t), r in sorted(entrees.taches_retirees.items())})


# ==========================================================================
# Cellules du budget (point 1) et mentions « fragile »
# ==========================================================================
def jeu_famille(an, cm) -> object:
    cle = cm[:4] if cm[0] == "scenario" else cm
    return an.familles[cle].jeu


ETABLI, NON_REFUTEE = "dépassement établi", "non réfutée"


def rho_cellule(an, cm) -> tuple:
    """ρ̂ d'une cellule : celui de la calibration de la configuration (avec son repli) ; dans un scénario, le plus grand
    de X et de Y ; sans calibration (toute la réserve), celui du jeu rejoué."""
    def rho_conf(env, mod):
        cl = an.classes_cal.get((env, mod)) or an.classes_retro.get((env, mod)) or {}
        v = next(iter(cl.values()), None)
        return (float(v["rho"]), v["source_rho"]) if v else (1.0, CL.SOURCES_RHO[2])
    if cm[0] == "config":
        return rho_conf(cm[1], cm[2])
    return max(rho_conf(cm[1], cm[2]), rho_conf(cm[1], cm[3]), key=lambda r: r[0])


def _den_par_tache(an, cm, cache: dict) -> list:
    cle = cm[:4] if cm[0] == "scenario" else cm
    if cle not in cache:
        jeu = an.familles[cle].jeu
        t = CL.taches_ecritures(jeu)
        m = jeu.attrs["den"] & (jeu.typ >= 0)
        par: dict = {}
        for x in t[m].tolist():
            par[x] = par.get(x, 0) + 1
        autres = getattr(an, "familles_b", None) or {}
        if cle in autres:   # échange des rôles : les tâches du second pli s'ajoutent
            jb = autres[cle].jeu
            tb = CL.taches_ecritures(jb)
            for x in tb[jb.attrs["den"] & (jb.typ >= 0)].tolist():
                par[("b", x)] = par.get(("b", x), 0) + 1
        cache[cle] = list(par.values())
    return cache[cle]


def demontree(an, cm, centre: float, budget: float, cache: dict) -> dict:
    """« Démontrée » (5.13, Q13) : borne haute de Clopper-Pearson sur la taille effective, 5 % unilatéral, au plus le
    budget ; x = dégâts en plus attendus (valeur centrale × écritures au dénominateur ÷ 100), n = écritures au
    dénominateur, m = écritures au dénominateur par tâche, x_eff = x × n_eff ÷ n. Preuve à 95 % : taille effective à
    ρ = 1, valable sans hypothèse sur la corrélation (N3, 06/11) ; la même lecture avec le ρ̂ de la calibration est
    publiée à côté, « sous hypothèse » (demontree_hyp, borne_cp_haute_hyp, rho_hyp)."""
    m = _den_par_tache(an, cm, cache)
    rho, src = rho_cellule(an, cm)
    n, _mbar, ne = CL.taille_effective(m, CL.RHO_PREUVE)
    _n, _m, ne_h = CL.taille_effective(m, rho)
    vide = dict(demontree=False, borne_cp_haute=float("nan"), n_eff=0.0, rho=CL.RHO_PREUVE,
                source_rho="preuve sans hypothèse (ρ = 1)", demontree_hyp=False, borne_cp_haute_hyp=float("nan"),
                rho_hyp=rho, source_rho_hyp=src)
    if n <= 0 or not centre == centre:
        return vide
    x = centre * n / 100.0
    hi = 100.0 * CL.bornes_cp(x * ne / n, ne)[1]
    hi_h = 100.0 * CL.bornes_cp(x * ne_h / n, ne_h)[1]
    return dict(vide, demontree=bool(hi <= budget), borne_cp_haute=hi, n_eff=ne, demontree_hyp=bool(hi_h <= budget),
                borne_cp_haute_hyp=hi_h)


def choix_decisifs(an) -> dict:
    """Méthode des intervalles qui décident (point 2, hasard) et des intervalles descriptifs : celle de la simulation
    refaite sur les différences de charge (phase 3) ; à défaut, celle des réglages."""
    return an.reglages.choix


def cellules(an, regle: str = "B-tout", e: Optional[float] = None, cle_q: str = "budget") -> list:
    """Les cellules d'une règle (configurations et scénarios × 3 niveaux) : statut (sans objet, tenue non mise à
    l'épreuve, dépassement établi, non réfutée), valeur centrale, intervalle descriptif, borne de construction
    0,95 × budget × s ÷ q, s ÷ q et son intervalle, « démontrée », « garantie hors hypothèse », mentions « fragile »
    (moins de 30 tâches porteuses, zone qui échoue). Le dépassement est établi par le max-T de Westfall et Young sur
    les cellules jugées de la règle (Q13 : la même mesure pour toutes les règles)."""
    e = an.reglages.e_principal if e is None else e
    choix = choix_decisifs(an)
    B = an.reglages.B
    out, cache = [], {}
    autres = getattr(an, "familles_b", None) or {}
    for cle in an.familles:
        jeux = [an.familles[cle].jeu] + ([autres[cle].jeu] if cle in autres else [])
        for cm in an.modes(cle):
            r0 = an.resume_r0.get(cm, {})
            for j, niv in enumerate(NIVEAUX):
                q = an.magasin.get((cle_q,) + cm + (regle, e, niv))
                if q is None:
                    continue
                n_niv = sum(PL.ecritures_niveau(jj, j) for jj in jeux)
                porteuses = sum(PL.taches_porteuses(jj, j) for jj in jeux)
                p3 = r0.get("p3", {}).get((regle, niv))
                if p3 is None and n_niv > 0:   # C13, M5 : un résumé R0 incomplet ne doit pas rendre la cellule « jugée »
                    raise ValueError(f"part des répétitions R0 au palier 3 absente : {cm} {niv} ({regle})")
                p3 = float("nan") if p3 is None else p3
                statut = SANS_OBJET if n_niv == 0 else (NON_EPROUVEE if p3 == 0 else JUGEE)
                b = float(CR.BUDGET[niv])
                iv = PL.intervalles_quantite(q, choix, B)
                ligne = dict(famille=cm, niveau=niv, regle=regle, e=e, statut=statut, centre=q.centre, budget=b,
                             lo=iv["retenue"][0], hi=iv["retenue"][1], methode=iv["methode_effective"],
                             lo_seconde=iv["seconde"][0], hi_seconde=iv["seconde"][1], intervalles=iv,
                             part_rep_p3=p3, ecritures_niveau=n_niv, porteuses=porteuses, G=q.G or
                             len(an.taches.get(cm[1], ())), fragile=[], _q=q)
                qs = an.magasin.get(("s_sur_q",) + cm + (niv,))
                if qs is not None and statut != SANS_OBJET:
                    ivs = PL.intervalles_quantite(qs, choix, B)
                    ligne.update(s_sur_q=qs.centre, s_sur_q_lo=ivs["retenue"][0], s_sur_q_hi=ivs["retenue"][1],
                                 borne_construction=0.95 * b * qs.centre,
                                 garantie_hors_hypothese=bool(statut == JUGEE and ivs["retenue"][0] > 1 / 0.95))
                if statut == JUGEE:
                    ligne.update(demontree(an, cm, q.centre, b, cache))
                    if porteuses < SEUIL_PORTEUSES:
                        ligne["fragile"].append(f"moins de {SEUIL_PORTEUSES} tâches porteuses")
                    if IC.fragile_par_grappes(ligne["G"], choix):
                        ligne["fragile"].append("zone des grappes qui échoue (simulation de couverture du point 2)")
                out.append(ligne)
    # max-T sur les cellules jugées (m : la règle atteint le palier 3 dans au moins une répétition R0, hors « sans
    # objet ») ; sans répétitions bootstrap, le dépassement n'est pas calculé
    jug = [c for c in out if c["statut"] == JUGEE]
    calc = bool(jug) and all(len(c["_q"].boot) >= B > 0 for c in jug)
    if calc:
        r = MX.depassement_etabli(np.array([c["centre"] for c in jug]),
                                  np.stack([c["_q"].boot.tableau()[:B] for c in jug], axis=1),
                                  np.array([c["budget"] for c in jug]),
                                  porteuses=np.array([c["porteuses"] for c in jug]))
        for i, c in enumerate(jug):   # cellule non testable : motif publié, rien d'établi (5.14, point 2, 07/11)
            c.update(etabli=bool(r["etabli"][i]), borne_maxt=float(r["borne"][i]), c_etoile=r["c_etoile"],
                     non_testable=r["motif"][i])
    for c in out:
        del c["_q"]
        if c["statut"] == JUGEE:
            c["verdict"] = (ETABLI if c.get("etabli") else NON_REFUTEE) if calc else NON_CALCULE
        else:
            c["verdict"] = c["statut"]
    return out


MENTION_FAMILLE = "niveau non mesuré pour cette taille de famille"


def testables(cel: list) -> int:
    """Taille de la famille du max-T du point 1 : cellules jugées et testables (5.14, point 2)."""
    return sum(c["statut"] == JUGEE and not c.get("non_testable") for c in cel)


def mention_famille(cel: list) -> str:
    """O4 (b), décision d'Otsoa du 09/11 (plan, section 6) : le niveau du max-T n'a été mesuré que sur les familles des
    mondes du contrôle 3 ; avec une ou deux cellules testables, la mention sort d'office. Sans effet sur l'étiquette."""
    return MENTION_FAMILLE if 1 <= testables(cel) <= 2 else ""


def point1(an, regle: str = "B-tout") -> dict:
    """Éliminatoire (Q13) : R1 si un dépassement est établi dans au moins une cellule de B-tout ; le critère de retrait
    de la décision 5 est recalculé comme contrôle du code (un échec signalerait un défaut du code, pas une
    réfutation)."""
    cel = cellules(an, regle)
    echecs = [c for c in cel if c["verdict"] == ETABLI]
    non_calcule = any(c["statut"] == JUGEE and c["verdict"] == NON_CALCULE for c in cel)
    controle = [dict(famille=cm, **d) for cm, r in an.resume_r0.items() for d in r.get("derive", [])
                if d["regle"] == regle and d["verdict"] != "passe"]
    # C13, M3 : sans max-T (bootstrap absent ou incomplet), le point 1 n'est pas « tenu » : il n'est pas calculé
    return dict(tenu=None if non_calcule else not echecs, calcule=not non_calcule, cellules=cel, echecs=echecs,
                defauts_retrait=controle, testables=testables(cel), mention_famille=mention_famille(cel))


# ==========================================================================
# Point 2 : réussite face aux témoins (max-T, puis charge moyenne)
# ==========================================================================
def cellules_temoin(an, temoin: str) -> list:
    """m (5.14, point 2) : cellules où le témoin délègue des écritures du niveau, et qui ne sont pas « sans objet » ;
    avec le nombre de tâches porteuses de chacune (cellule non testable, compté comme pour B-tout)."""
    e = an.reglages.e_principal
    out = []
    autres = getattr(an, "familles_b", None) or {}
    for cle in an.familles:
        jeu = an.familles[cle].jeu
        jeux = [jeu] + ([autres[cle].jeu] if cle in autres else [])
        for cm in an.modes(cle):
            for j, niv in enumerate(NIVEAUX):
                q = an.magasin.get(("budget",) + cm + (temoin, e, niv))
                if q is None or sum(PL.ecritures_niveau(jj, j) for jj in jeux) == 0:   # comme cellules (C13, M5)
                    continue
                if not an.resume_r0.get(cm, {}).get("delegue", {}).get((temoin, niv), False):
                    continue
                out.append((cm, niv, q, sum(PL.taches_porteuses(jj, j) for jj in jeux)))
    return out


def depassement_temoin(an, temoin: str) -> dict:
    B = an.reglages.B
    cel = cellules_temoin(an, temoin)
    cel = [c for c in cel if len(c[2].boot) >= B and B > 0]
    if not cel:
        return dict(m=0, c_etoile=float("nan"), etablies=[], cellules=[])
    est = np.array([c[2].centre for c in cel])
    boot = np.stack([c[2].boot.tableau()[:B] for c in cel], axis=1)
    bud = np.array([float(CR.BUDGET[c[1]]) for c in cel])
    r = MX.depassement_etabli(est, boot, bud, porteuses=np.array([c[3] for c in cel]))
    lignes = [dict(famille=c[0], niveau=c[1], centre=float(est[i]), ecart_type=float(r["ecart_type"][i]),
                   borne=float(r["borne"][i]), budget=float(bud[i]), etabli=bool(r["etabli"][i]),
                   porteuses=int(c[3]), non_testable=r["motif"][i])
              for i, c in enumerate(cel)]
    return dict(m=len(cel), c_etoile=r["c_etoile"], etablies=[l for l in lignes if l["etabli"]], cellules=lignes)


TEMOINS_POINT2 = ("tout_valider", "liste_fixe", "tri_risque")   # Q15 : « tout faire valider » d'abord
R2_AUCUNE, R2_INFERIEURE = "aucune délégation établie", "délégation inférieure à un témoin"


def point2(an, regle: str = "B-tout") -> dict:
    """Réussite (Q6, Q15) : trois témoins obligatoires, « tout faire valider » testé d'abord. Un témoin est battu
    partout si son dépassement est établi dans au moins une cellule (« tout faire valider » ne délègue rien : il ne peut
    pas l'être) ; sinon, il faut que la charge hors lectures de la règle soit inférieure à la sienne en moyenne sur les
    configurations délégables, l'intervalle de la différence appariée étant entièrement et strictement sous 0 (une
    différence nulle partout, ou [0, 0], n'établit rien). Mention de R2 : « aucune délégation établie » si « tout faire
    valider » n'est pas battu, « délégation inférieure à un témoin » sinon."""
    choix = choix_decisifs(an)
    out = {}
    for t in TEMOINS_POINT2:
        dep = depassement_temoin(an, t) if t != "tout_valider" else dict(m=0, c_etoile=float("nan"), etablies=[],
                                                                         cellules=[])
        q = an.magasin.get(("moy_diff_charge", regle, t))
        iv = PL.intervalles_quantite(q, choix, an.reglages.B) if q is not None and q.centre == q.centre else None
        battu_charge = bool(iv and iv["retenue"][1] < 0)
        diverge = bool(iv and (iv["seconde"][1] < 0) != battu_charge)
        out[t] = dict(depassement=dep, battu_partout=bool(dep["etablies"]), diff_moyenne=q.centre if q else float("nan"),
                      intervalle=iv["retenue"] if iv else (float("nan"), float("nan")),
                      intervalle_seconde=iv["seconde"] if iv else (float("nan"), float("nan")),
                      battu_charge=battu_charge, battu=bool(dep["etablies"]) or battu_charge,
                      methodes_divergent=diverge)
    tenu = all(v["battu"] for v in out.values())
    mention = "" if tenu else (R2_AUCUNE if not out["tout_valider"]["battu"] else R2_INFERIEURE)
    return dict(tenu=tenu, temoins=out, mention_r2=mention)


# ==========================================================================
# Points 3 et 4
# ==========================================================================
def point3(an, regle: str = "B-tout") -> dict:
    """Comparaison au hasard au même rythme (Q7) : « méritée », « répartie » ou « sans objet » ; sans effet sur
    l'étiquette."""
    choix = an.reglages.choix
    e = an.reglages.e_principal
    dele = [c for c in an.configs() if an.delegables.get((c[1], c[2]))]
    if not dele:
        return dict(conclusion="non calculable (aucune configuration délégable)", niveaux={})
    nul = all(an.magasin[("budget",) + c + (n, e, niv)].centre == 0 for c in dele for niv in NIVEAUX
              for n in (regle, f"hasard_{regle}"))
    niveaux = {}
    for niv in NIVEAUX:
        q = an.magasin.get(("moy_diff_exces", regle, niv))
        if q is None:
            continue
        iv = PL.intervalles_quantite(q, choix, an.reglages.B)
        lo, hi = iv["retenue"]
        lo2, hi2 = iv["seconde"]
        niveaux[niv] = dict(diff=q.centre, lo=lo, hi=hi, lo_seconde=lo2, hi_seconde=hi2)
    conc = conclusion_hasard(niveaux, nul)
    conc2 = conclusion_hasard({n: dict(lo=v["lo_seconde"], hi=v["hi_seconde"]) for n, v in niveaux.items()}, nul)
    # C13, M2 : « fragile » si la seconde méthode conclut autrement (5.13, B4)
    return dict(conclusion=conc, conclusion_seconde=conc2, methodes_divergent=conc != conc2, niveaux=niveaux)


def conclusion_hasard(niveaux: dict, nul: bool) -> str:
    """Q7 : « méritée » si l'intervalle de la différence appariée est tout sous 0 à au moins un niveau et tout au-dessus
    de 0 à aucun ; « sans objet » si aucun dégât en plus, ni pour la règle ni pour le hasard ; « répartie » sinon."""
    if nul:
        return "sans objet"
    moins = any(v["hi"] < 0 for v in niveaux.values())
    plus = any(v["lo"] > 0 for v in niveaux.values())
    return "méritée" if moins and not plus else "répartie"


def point4(an) -> dict:
    """Point 4 (5.14 ; amendement R4, Otsoa, 07/11). Configurations délégables : taux médian d'au moins un type au plus
    la barre (Q14, N1). Sans configuration délégable, R4 (« non-fiabilité établie ») exige au moins un type jugeable et,
    dans chaque configuration qui a un type jugeable, un type jugeable dont le dépassement est établi à ρ = 1
    (`classes.statut_configuration`). Sinon « preuves insuffisantes », avec son motif : aucun type jugeable ;
    dépassement non établi (même au ρ̂ propre) dans au moins une configuration jugeable ; dépassement établi au ρ̂ propre
    mais pas à ρ = 1 dans chacune. Une analyse sans statuts n'établit rien. Sans configuration délégable, les
    configurations sans type jugeable sont nommées (`sans_type_jugeable`) : R4 ne dit rien d'elles (plan, 1.5 ; tranché
    par Claude, 07/11, cinquième passage du contrôle 3)."""
    dele = sorted(c for c, v in an.delegables.items() if v)
    jug = getattr(an, "jugeables", None) or {}
    st = getattr(an, "statuts", None) or {}
    jugeables = sorted(c for c, v in jug.items() if v)
    non_etablies = [c for c in jugeables if not st.get(c, {}).get("etablie")]
    etablie = bool(jugeables) and not non_etablies
    if dele or etablie:
        motif = ""
    elif not jugeables:
        motif = MOTIF_AUCUN_JUGEABLE
    elif all(st.get(c, {}).get("etablie_rho_propre") for c in non_etablies):
        motif = MOTIF_RHO_PROPRE
    else:
        motif = MOTIF_NON_ETABLI
    details = {c: {k: st.get(c, {}).get(k) for k in ("rho_propre", "rho_lecture", "rho_bascule")}
               for c in non_etablies} if not dele else {}
    sans_type_jugeable = sorted(c for c, v in jug.items() if not v) if not dele else []
    return dict(tenu=bool(dele), delegables=dele, jugeable=bool(jugeables), etablie=etablie,
                non_etablies=non_etablies, motif=motif, details=details, sans_type_jugeable=sans_type_jugeable)


def etiquette(p0: dict, p1: dict, p2: dict, p4: dict) -> str:
    if p1["tenu"] is None:   # C13, M3 : une valeur non calculée ne tombe jamais dans la branche favorable
        raise ValueError("point 1 non calculé : le max-T n'a pas tourné (bootstrap absent ou incomplet)")
    if not p0["tenu"]:
        return "R5"
    if not p1["tenu"]:
        return "R1"
    if not p4["tenu"]:
        return "R4" if p4.get("etablie", False) else PREUVES_INSUFFISANTES
    if not p2["tenu"]:
        return "R2"
    return "confirmée"


def mention(et: str, p2: dict, p4: dict) -> str:
    """Mention publiée avec l'étiquette : celle de R2 (aucune délégation établie, ou charge inférieure), ou le motif de
    « preuves insuffisantes » (amendement R4, 07/11)."""
    if et == "R2":
        return p2.get("mention_r2", "")
    if et == PREUVES_INSUFFISANTES:
        return p4.get("motif", "")
    return ""


def combiner_b2(dec_p: dict, d_bv: dict) -> dict:
    """Désaccord persistant (B2) : l'étiquette retenue est la moins favorable des deux (analyse principale, verdicts
    bruts des vagues en désaccord) ; la mention suit l'étiquette retenue ; à étiquettes égales, la mention de l'analyse
    principale reste, et celle des verdicts bruts est publiée à côté, avec leurs points 1, 2 et 4 (relecture C13, M4)."""
    et = moins_favorable(dec_p["etiquette"], d_bv["etiquette"])
    p1, p4 = d_bv["point1"], d_bv["point4"]
    return dict(etiquette=et, mention=d_bv["mention"] if et != dec_p["etiquette"] else dec_p["mention"],
                etiquette_bruts_vague=d_bv["etiquette"], mention_bruts_vague=d_bv["mention"],
                points_bruts_vague=dict(point1=dict(tenu=p1["tenu"], etablies=len(p1["echecs"])),
                                        point2={t: v["battu"] for t, v in d_bv["point2"]["temoins"].items()},
                                        point4=dict(tenu=p4["tenu"], motif=p4.get("motif", ""))))


def decider(an, p0: dict, regle: str = "B-tout") -> dict:
    p1, p2, p3, p4 = point1(an, regle), point2(an, regle), point3(an, regle), point4(an)
    et = etiquette(p0, p1, p2, p4)
    return dict(etiquette=et, mention=mention(et, p2, p4), point0=p0, point1=p1, point2=p2, point3=p3, point4=p4)


# ==========================================================================
# Règle de choix réappliquée (1.3, point 4) et alerte de résistance (5.11)
# ==========================================================================
def regle_de_choix(an) -> dict:
    """Budget tenu partout ; puis charge hors lectures la plus basse en moyenne sur les configurations délégables ; à
    moins d'un point d'écart, la plus prudente (plus grande marge au budget dans sa pire cellule), puis la plus simple
    (B-tout, B-régulier, A½, A¼)."""
    etat = {}
    for r in an.reglages.noms_regles:
        cel = [c for c in cellules(an, r) if c["statut"] == JUGEE]
        echecs = [c for c in cel if c["verdict"] == ETABLI]
        pire = max((c["hi"] / c["budget"] for c in cel if c["hi"] == c["hi"]), default=0.0)
        q = an.magasin.get(("moy_charge", r))
        etat[r] = dict(n_cellules=len(cel), echecs=len(echecs), tient=not echecs, pire=pire, marge=1 - pire,
                       charge=q.centre if q is not None else float("nan"))
    return choisir_regle(etat, an.reglages.noms_regles)


def choisir_regle(etat: dict, noms) -> dict:
    """La règle de choix sur des états {règle: dict(tient, charge, marge)} (1.3, point 4)."""
    surv = [r for r in noms if etat[r]["tient"]]
    out = dict(etat=etat, survivantes=surv, retenue=None, motif="")
    if not surv:
        out["motif"] = "aucune règle ne tient le budget partout"
        return out
    ch = {r: etat[r]["charge"] for r in surv}
    if not all(v == v for v in ch.values()):
        out["motif"] = "charge moyenne non calculable (aucune configuration délégable)"
        return out
    meilleure = min(surv, key=lambda r: ch[r])
    groupe = [r for r in surv if ch[r] - ch[meilleure] < SEUIL_EGALITE]
    if len(groupe) == 1:
        out.update(retenue=meilleure, motif="charge hors lectures la plus basse parmi les règles qui tiennent le budget")
        return out
    marges = {r: round(etat[r]["marge"], 3) for r in groupe}
    mmax = max(marges.values())
    prud = [r for r in groupe if marges[r] == mmax]
    if len(prud) == 1:
        out.update(retenue=prud[0], motif="égalité de charge ; départage par la prudence")
    else:
        out.update(retenue=min(prud, key=RG.ORDRE_SIMPLICITE.index),
                   motif="égalité de charge et de prudence ; départage par la simplicité")
    return out


def bilan_mode(an, e: Optional[float] = None) -> dict:
    """{règle: (échecs, pire cellule ÷ budget)} : cellules jugées hors budget et périodes d'autonomie à plus d'une
    erreur constatée (scénarios), comme l'alerte 4.5 d'E1."""
    out = {}
    for r in an.reglages.noms_regles:
        cel = [c for c in cellules(an, r, e) if c["statut"] == JUGEE]
        n = sum(1 for c in cel if c["verdict"] == ETABLI)
        n += sum(1 for cm, x in an.resume_r0.items() for d in x.get("derive", [])
                 if d["regle"] == r and d["verdict"] != "passe")
        w = max((c["hi"] / c["budget"] for c in cel if c["hi"] == c["hi"]), default=0.0)
        out[r] = (n, w)
    return out


def alerte_resistance(bilans: dict, regle: str = "B-tout") -> list:
    """Signalée si, dans un mode, la règle a plus d'échecs qu'une autre, ou une pire cellule au moins 1,25 fois plus
    haute et au moins à la moitié du budget (critère de l'alerte 4.5 d'E1, 5.11)."""
    alertes = []
    for mode, st in bilans.items():
        if regle not in st:
            continue
        n0, w0 = st[regle]
        for r, (n, w) in st.items():
            if r == regle:
                continue
            if n0 > n or (w0 >= 0.5 and w0 >= 1.25 * w):
                alertes.append(dict(mode=mode, autre=r, echecs_regle=n0, echecs_autre=n, pire_regle=w0, pire_autre=w))
    return alertes


# ==========================================================================
# Comparaisons entre analyses (« fragile ») et échange des rôles
# ==========================================================================
def verdicts_cellules(cel: list) -> dict:
    """{(famille, niveau): dépassement établi ?} des cellules comparables (« sans objet » ne se compare pas)."""
    return {(c["famille"], c["niveau"]): c["verdict"] == ETABLI for c in cel if c["statut"] != SANS_OBJET}


def desaccords(cel_a: list, cel_b: list) -> list:
    a, b = verdicts_cellules(cel_a), verdicts_cellules(cel_b)
    return sorted(k for k in a if k in b and a[k] != b[k])


def combiner_statuts(sa: dict, sb: dict) -> dict:
    """Statut d'une configuration dans l'échange des rôles (secondaire, 3.2 ; amendement R4, 07/11) : délégable ou
    jugeable si elle l'est dans l'un des deux plis ; dépassement établi (à ρ = 1, ou au ρ̂ propre) s'il l'est dans
    chaque pli où elle est jugeable ; ρ* : le plus petit de ces plis (None si l'un n'en a pas) ; ρ̂ propre : le plus
    grand des deux (affichage)."""
    plis = [s for s in (sa, sb) if s.get("jugeable")]
    bascules = [s.get("rho_bascule") for s in plis]
    propres = [s.get("rho_propre") for s in (sa, sb) if s.get("rho_propre") is not None]
    return dict(delegable=bool(sa.get("delegable")) or bool(sb.get("delegable")), jugeable=bool(plis),
                etablie=bool(plis) and all(s.get("etablie") for s in plis),
                etablie_rho_propre=bool(plis) and all(s.get("etablie_rho_propre") for s in plis),
                rho_propre=max(propres) if propres else None,
                rho_lecture=max([s.get("rho_lecture", CL.RHO_PREUVE) for s in plis], default=CL.RHO_PREUVE),
                rho_bascule=min(bascules) if plis and None not in bascules else None)


def combiner_echange(anA, anB):
    """Échange des rôles (3.2 ; 5.5, point 7) : quantité combinée = moyenne à poids égaux des deux plis, répétition par
    répétition ; valeur centrale = moyenne des deux ; jackknife sur les tâches des deux moitiés (strates séparées) ;
    écart type du bootstrap-t = √((se_A² + se_B²) ÷ 4), les deux moitiés étant tirées indépendamment. Rend une analyse
    dont le magasin porte les quantités combinées (familles, jeux et résumés du pli A, statuts réunis)."""
    from copy import copy
    from . import analyse as AN
    B = anA.reglages.B
    mag = AN.Magasin()
    for k, qa in anA.magasin.items():
        qb = anB.magasin.get(k)
        if qb is None or not (qa.centre == qa.centre and qb.centre == qb.centre):
            continue
        q = mag.q(k)
        q.centre = (qa.centre + qb.centre) / 2
        q.se = math.sqrt((qa.se ** 2 + qb.se ** 2) / 4) if qa.se == qa.se and qb.se == qb.se else float("nan")
        nb = min(len(qa.boot), len(qb.boot), B)
        if nb:
            q.boot += (qa.boot.tableau()[:nb] + qb.boot.tableau()[:nb]) / 2
            if len(qa.se_boot) >= nb and len(qb.se_boot) >= nb:
                q.se_boot += np.sqrt((qa.se_boot.tableau()[:nb] ** 2 + qb.se_boot.tableau()[:nb] ** 2) / 4)
        if qa.jack is not None and qb.jack is not None:
            q.jack = np.concatenate([(qa.jack + qb.centre) / 2, (qa.centre + qb.jack) / 2])
            sa = np.asarray(qa.strates_jack if qa.strates_jack is not None else np.zeros(len(qa.jack), int))
            sb = np.asarray(qb.strates_jack if qb.strates_jack is not None else np.zeros(len(qb.jack), int))
            q.strates_jack = np.concatenate([sa, sb + (sa.max() + 1 if sa.size else 0)])
            q.G = int(len(q.jack))
    for k, qa in anA.magasin.items():   # moyennes présentes dans un seul pli : ce pli seul
        if k not in mag and k[0] in PL.MOYENNES and k not in anB.magasin:
            mag[k] = qa
    for k, qb in anB.magasin.items():
        if k not in mag and k[0] in PL.MOYENNES:
            mag[k] = qb
    an = copy(anA)
    an.nom = "échange des rôles (combinée)"
    an.magasin = mag
    an.familles_b = anB.familles
    an.delegables = {c: bool(anA.delegables.get(c)) or bool(anB.delegables.get(c)) for c in anA.delegables}
    an.jugeables = {c: bool(getattr(anA, "jugeables", {}).get(c)) or bool(getattr(anB, "jugeables", {}).get(c))
                    for c in anA.delegables}
    an.statuts = {c: combiner_statuts(getattr(anA, "statuts", {}).get(c, {}), getattr(anB, "statuts", {}).get(c, {}))
                  for c in anA.delegables}
    r0 = {}
    for cm, x in anA.resume_r0.items():
        y = anB.resume_r0.get(cm, {})
        z = dict(x)
        z["p3"] = {k: max(v, y.get("p3", {}).get(k, 0.0)) for k, v in x.get("p3", {}).items()}
        z["delegue"] = {k: v or y.get("delegue", {}).get(k, False) for k, v in x.get("delegue", {}).items()}
        z["derive"] = list(x.get("derive", [])) + list(y.get("derive", []))
        r0[cm] = z
    an.resume_r0 = r0
    return an
