"""Lancement unique du contrôle 3 (PLAN_EXPERIENCE.md, section 7, étape 6) : mondes fictifs passés par toute la chaîne de
décision, et étude de délégabilité (point 4 seul).

Second passage (06/11), après les décisions d'Otsoa sur Q14 et Q15 et la règle G1 de ρ̂ (moteur, phase 4, commit
07ae30d) : sorties dans `resultats_v2/` ; `resultats/` reste l'historique du premier passage (code du commit bbbaa72).
Troisième passage (06/11), après N1 (délégabilité sur le taux médian, tranché par la recherche à la demande d'Otsoa),
le correctif de ρ̂ (tâches d'au moins deux écritures) et le garde-fou « volume insuffisant » : sorties dans
`resultats_v3/` ; `resultats_v2/` reste l'historique du second passage (code du commit 7a43671).
Quatrième passage (06/11), après N3 (ρ̂ par type, Fleiss–Cuzick stratifié ; preuves à 95 % à ρ = 1 ; tranché par la
recherche à la demande d'Otsoa) et les corrections de la revue de code « ultra » : sorties dans `resultats_v4/`.
Ajouts, jugés sur la pire case (recherche N3) : ρ = 0,9 et 1 dans l'étude de délégabilité ; deux mécanismes de plus
(logit-normal à variance latente commune ; ρ différent d'un type à l'autre) ; cases critiques de la certification à
tort, 10 000 répétitions chacune (`critiques.jsonl`) ; trois mondes ajoutés en dernier (A-rho9, A-logit, A-het).
Mêmes réglages figés (R0 = B = 200, K = 10, e = 5 %, même graine : les mondes du premier passage gardent les mêmes
données et les mêmes graines du moteur, d'où une comparaison appariée). Ajouts : le monde D-inerte (en dernier, pour ne
pas décaler les graines), les multiples 2, 5 et 10 de l'étude de délégabilité.
Cinquième passage (07/11), après l'amendement de R4 (décision d'Otsoa du 07/11 ; « preuves insuffisantes » remplace
« volume insuffisant ») : sorties dans `resultats_v5/` ; `resultats_v4/` reste l'historique du quatrième passage (code
du commit 49bbc3d). Mêmes réglages et même graine, d'où une comparaison appariée avec le quatrième passage. Changements :
étiquette attendue du monde C (« R4 ou preuves insuffisantes ») ; deux mondes ajoutés en dernier, B-seuil (dépassement
vrai d'une fois le budget, dérive étalonnée dans `b_seuil/`) et V (un dixième des tâches de la réserve) ; l'étude de
délégabilité et les cases critiques ne sont pas refaites ici (`ETUDES_POINT4`) : la partie R4 du passage les a refaites
avec la règle amendée, sur de nouvelles graines (`passage5_r4/`).
Sixième passage (07/11, soir), après l'amendement des cellules non testables (décision d'Otsoa du 07/11 ; plan, 5.14,
point 2 : moins de deux tâches porteuses, écart type bootstrap nul ou non défini) : sorties dans `resultats_v6/` ;
`resultats_v5/` reste l'historique du cinquième passage (code du commit e300b0e). Mêmes mondes, mêmes réglages et même
graine, d'où une comparaison appariée avec le cinquième passage ; seul le moteur change.
Septième passage (08/11), après la correction du max-T (relecture C13, C1 : T* recentré sur la moyenne des répétitions,
c* au moins 0 ; formule F1 de la mesure préenregistrée `maxt_niveau/`), le motif « estimation non définie » (C5) et la
tolérance d'un écart type nul portée à quatre epsilon du float32 (C6) : sorties dans `resultats_v7/` ; `resultats_v6/`
reste l'historique du sixième passage (code du commit 0a908cf).
Huitième passage (08/11) : la même correction avec le 97,5e centile (formule F3, décidée par Otsoa le 08/11 ; plan,
5.14, point 2) et l'échelle de la tolérance étendue aux répétitions : sorties dans `resultats_v8/` ; `resultats_v7/`
reste l'historique du septième passage (code du commit 5e87ae0). Mêmes mondes, mêmes réglages et même graine que les
passages précédents, d'où des comparaisons appariées ; seul le moteur change.

Usage (depuis simulation/) :
    .venv/bin/python -m controle3.lancer --lancer      une seule fois ; écrit controle3/resultats_v8/
    .venv/bin/python -m controle3.lancer --resumer     refait les tableaux à partir des résultats bruts (aucun calcul)
    .venv/bin/python -m controle3.lancer --verifier    empreintes du code, comparées à celles du lancement

Paramètres écrits et figés AVANT le lancement (raisons : RAPPORT.md, « Méthode ») :
- R0 = 200 et B = 200 au lieu de 2 000 (plan, 5.5, point 5) : une répétition complète aux volumes de l'expérience
  (12 configurations, 48 scénarios, jackknife et bootstrap) prend environ deux minutes et demie sur un cœur avec ces
  valeurs ; K = 10 et e = 5 % restent ceux du plan ; méthode des intervalles : celle que lit le rejeu final
  (`rejeu/resultats_couverture_charge/choix.json`, jackknife-t) ;
- seule B-tout est rejouée (les trois autres règles n'entrent pas dans l'étiquette) ;
- répétitions par monde : `REPETITIONS` ; graine maîtresse `GRAINE` ;
- exécution : 12 processus, bootstrap rejoué par tranches de 50 répétitions. Un premier lancement (14 processus,
  tranches de 200) a été arrêté au bout de 14 répétitions : la mémoire de la machine (48 Go) était saturée. Ni le
  nombre de processus ni la taille des tranches ne changent les sorties (graine propre à chaque monde et répétition ;
  invariance aux tranches vérifiée à l'identique, RAPPORT.md, 2.3) ; les répétitions sont donc les mêmes ;
- étude de délégabilité : multiples de la barre `DELEG_MULTIPLES`, ρ dans `DELEG_RHOS`, avec ou sans témoins en
  défaut (monde A), `DELEG_REPETITIONS` répétitions par case.
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import csv  # noqa: E402
import glob  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import platform  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor, as_completed  # noqa: E402

import numpy as np  # noqa: E402

from . import ICI, SIMULATION  # noqa: E402
from . import harnais as H  # noqa: E402
from . import mondes as MD  # noqa: E402
from rejeu import decision as DE  # noqa: E402

DOSSIER = os.path.join(ICI, "resultats_v8")   # huitième passage (max-T recentré, F3) ; v7 (F1) : commit 5e87ae0

# ---- paramètres figés
GRAINE = 2026110503
R0, B, K, TRANCHE = 200, 200, 10, 50
PROCESSUS = 8   # 12 jusqu'au septième passage ; 8 depuis le 08/11, pour laisser la machine utilisable
REPETITIONS = {"A": 80, "A-tf": 40, "A4": 40, "A-rho0": 30, "A-rho7": 30, "B": 60, "B100": 20, "C": 25, "D": 50,
               "D-piege": 40, "E": 50, "E-fort": 30, "F1": 8, "F2": 8, "K": 8, "D-inerte": 40,
               "A-rho9": 30, "A-logit": 30, "A-het": 30,
               "B-seuil": 120, "V": 30}
# cinquième passage : étude de délégabilité et cases critiques refaites par `passage5_r4/` (règle amendée, graines
# neuves) ; B-seuil : 120 répétitions pour lire une part de R1 près de 5 % (intervalle de Wilson d'environ ± 4 points)
ETUDES_POINT4 = False
DELEG_MULTIPLES = (0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 2.0, 5.0, 10.0)
DELEG_RHOS = (0.0, 0.3, 0.7, 0.9, 1.0)
DELEG_TEMOINS = (False, True)
DELEG_REPETITIONS = 300
# quatrième passage : autres mécanismes (mécanisme, ρ, multiples), avec et sans témoins en défaut
DELEG_AUTRES = (("logit_normal", (0.3, 0.7, 0.9), (0.0, 0.5, 1.0, 2.0, 5.0)),
                ("heterogene", (0.0,), (0.0, 0.5, 1.0, 2.0)))
# cases critiques de la certification à tort (type exactement à la barre) : (multiple, ρ, témoins, mécanisme)
CRITIQUES = tuple((1.0, r, t, "beta") for r in (0.7, 0.9, 1.0) for t in (False, True)) + \
    ((1.0, 0.9, False, "logit_normal"),)
CRITIQUE_REPETITIONS = 10_000
ETIQUETTES = DE.ORDRE_ETIQUETTES   # amendement R4 (07/11) : « preuves insuffisantes » remplace « volume insuffisant »
SEUIL_ALERTE = 0.80          # consigne : signaler une étiquette attendue sous 80 % pour A, B, C et F
FICHIERS_CODE = (("controle3", ("mondes.py", "harnais.py", "lancer.py")),
                 ("rejeu", tuple(sorted(os.path.basename(p) for p in glob.glob(os.path.join(SIMULATION, "rejeu",
                                                                                        "*.py"))))))
AUTRES_EMPREINTES = ("rejeu/config_rejeu.json", "rejeu/resultats_couverture_charge/choix.json")


def parametres() -> H.Parametres:
    return H.Parametres(R0=R0, B=B, K=K, tranche=TRANCHE, graine=GRAINE)


def empreintes() -> dict:
    out = {}
    for dossier, noms in FICHIERS_CODE:
        for n in noms:
            with open(os.path.join(SIMULATION, dossier, n), "rb") as f:
                out[f"{dossier}/{n}"] = hashlib.sha256(f.read()).hexdigest()
    for rel in AUTRES_EMPREINTES:
        with open(os.path.join(SIMULATION, rel), "rb") as f:
            out[rel] = hashlib.sha256(f.read()).hexdigest()
    return out


def _json(o):
    if hasattr(o, "item"):
        return o.item()
    return str(o)


def _ecrire_meta(meta: dict) -> None:
    with open(os.path.join(DOSSIER, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1, default=_json)
        f.write("\n")


def cases_deleg() -> list:
    """(multiple, ρ, témoins, mécanisme) de l'étude de délégabilité, dans un ordre fixe (l'indice fait la graine)."""
    cases = [(m, r, t, "beta") for t in DELEG_TEMOINS for r in DELEG_RHOS for m in DELEG_MULTIPLES]
    cases += [(m, r, t, mec) for mec, rhos, mults in DELEG_AUTRES for t in DELEG_TEMOINS for r in rhos for m in mults]
    return cases


def taches_deleg() -> list:
    return [(m, r, t, rep, GRAINE, i, mec) for rep in range(DELEG_REPETITIONS)
            for i, (m, r, t, mec) in enumerate(cases_deleg())]


def taches_critiques() -> list:
    """Cases critiques : graines distinctes de l'étude (indice 50 000 + rang de la case)."""
    return [(m, r, t, rep, GRAINE, 50_000 + i, mec) for rep in range(CRITIQUE_REPETITIONS)
            for i, (m, r, t, mec) in enumerate(CRITIQUES)]


def taches_mondes() -> list:
    """(monde, répétition), entrelacées : un arrêt laisse une couverture équilibrée des mondes."""
    n = max(REPETITIONS.values())
    return [(m.nom, rep) for rep in range(n) for m in MD.MONDES if rep < REPETITIONS[m.nom]]


def _deleg(args):
    return H.delegabilite(*args)


def _monde(args):
    nom, rep = args
    return H.repetition(nom, rep, parametres())


def lancer() -> None:
    if os.path.exists(os.path.join(DOSSIER, "meta.json")):
        raise SystemExit(f"{os.path.relpath(DOSSIER, SIMULATION)}/meta.json existe déjà : ce passage se lance une "
                         "seule fois")
    os.makedirs(DOSSIER, exist_ok=True)
    debut = time.time()
    meta = dict(statut="en cours", debut=time.strftime("%Y-%m-%d %H:%M:%S"), graine=GRAINE, R0=R0, B=B, K=K,
                tranche=TRANCHE, processus=PROCESSUS, repetitions=REPETITIONS, etudes_point4=ETUDES_POINT4,
                mondes={m.nom: dict(titre=m.titre, attendu=m.attendu, multiple=m.multiple, multiples=m.multiples,
                                    rho=m.rho, facteur_N=m.facteur_N, inerte=m.inerte, melange=m.melange,
                                    inconnues=m.inconnues,
                                    fausses_alertes=m.fausses_alertes, refusees=m.refusees,
                                    vague_non_relue=m.vague_non_relue, mecanisme=m.mecanisme,
                                    rhos_heterogenes=m.rhos_heterogenes, fraction_reserve=m.fraction_reserve,
                                    note=m.note) for m in MD.MONDES},
                empreintes=empreintes(), python=sys.version.split()[0], numpy=np.__version__,
                machine=platform.platform())
    if ETUDES_POINT4:
        meta.update(delegabilite=dict(multiples=DELEG_MULTIPLES, rhos=DELEG_RHOS, temoins=DELEG_TEMOINS,
                                      repetitions=DELEG_REPETITIONS, autres=DELEG_AUTRES),
                    critiques=dict(cases=CRITIQUES, repetitions=CRITIQUE_REPETITIONS))
    else:
        meta["etudes_point4_note"] = ("étude de délégabilité et cases critiques refaites par la partie R4 du "
                                      "cinquième passage (controle3/passage5_r4/), règle amendée, graines neuves")
    _ecrire_meta(meta)
    with ProcessPoolExecutor(max_workers=PROCESSUS) as ex:
        if ETUDES_POINT4:
            t0 = time.time()
            with open(os.path.join(DOSSIER, "delegabilite.jsonl"), "w", encoding="utf-8") as f:
                for r in ex.map(_deleg, taches_deleg(), chunksize=20):
                    f.write(json.dumps(r, ensure_ascii=False, default=_json) + "\n")
            meta["duree_delegabilite_s"] = round(time.time() - t0, 1)
            print(f"délégabilité : {meta['duree_delegabilite_s']} s", flush=True)
            t0 = time.time()
            with open(os.path.join(DOSSIER, "critiques.jsonl"), "w", encoding="utf-8") as f:
                for r in ex.map(_deleg, taches_critiques(), chunksize=50):
                    f.write(json.dumps(dict(multiple=r["multiple"], rho=r["rho"], temoins=r["temoins"],
                                            mecanisme=r["mecanisme"], rep=r["rep"], faibles=r["faibles"]),
                                       ensure_ascii=False, default=_json) + "\n")
            meta["duree_critiques_s"] = round(time.time() - t0, 1)
            print(f"cases critiques : {meta['duree_critiques_s']} s", flush=True)
        t1 = time.time()
        taches = taches_mondes()
        futurs = {ex.submit(_monde, a): a for a in taches}
        fait = 0
        with open(os.path.join(DOSSIER, "repetitions.jsonl"), "w", encoding="utf-8") as f:
            for fu in as_completed(futurs):
                r = fu.result()
                f.write(json.dumps(r, ensure_ascii=False, default=_json) + "\n")
                f.flush()
                fait += 1
                if fait % 12 == 0 or fait == len(taches):
                    print(f"[{time.time() - t1:7.0f} s] {fait}/{len(taches)} répétitions", flush=True)
        meta["duree_mondes_s"] = round(time.time() - t1, 1)
    meta.update(statut="terminé", fin=time.strftime("%Y-%m-%d %H:%M:%S"), duree_s=round(time.time() - debut, 1))
    _ecrire_meta(meta)
    resumer()


# --------------------------------------------------------------------------
# Tableaux
# --------------------------------------------------------------------------
def lire_jsonl(nom: str) -> list:
    with open(os.path.join(DOSSIER, nom), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def hors_banque(r: dict) -> bool:
    """Mention « garantie hors hypothèse » sur une cellule jugée hors de la banque (la banque y est dès le mélange du
    pilote : s ÷ q ≈ 2,2 à enjeu faible)."""
    return any(c["statut"] == "jugée" and "/banque/" not in "/" + c["famille"] + "/" for c in r["p1"]["hors_hypothese"])


def lignes_frequences(reps: list) -> list:
    out = []
    for m in MD.MONDES:
        rs = sorted((r for r in reps if r["monde"] == m.nom), key=lambda r: r["rep"])
        n = len(rs)
        if not n:
            continue
        cnt = {e: sum(r["etiquette"] == e for r in rs) for e in ETIQUETTES}
        lig = dict(monde=m.nom, attendu=m.attendu, n=n, **{e: cnt[e] for e in ETIQUETTES})
        lig.update({f"part {e}": round(cnt[e] / n, 3) for e in ETIQUETTES})
        k = sum(MD.conforme(r["etiquette"], r.get("mention", ""), m.attendu) for r in rs)   # cinquième passage
        lig.update({"attendue": k, "part attendue": round(k / n, 3)})
        lig.update({f"pi {nom}": sum(r["etiquette"] == DE.PREUVES_INSUFFISANTES and r.get("mention") == motif
                                     for r in rs)
                    for nom, motif in (("aucun type jugeable", DE.MOTIF_AUCUN_JUGEABLE),
                                       ("dépassement non établi", DE.MOTIF_NON_ETABLI),
                                       ("établi sous rho propre", DE.MOTIF_RHO_PROPRE))})
        lig.update(
            plus_frequente=max(ETIQUETTES, key=lambda e: cnt[e]),
            p1_etabli=round(sum(not r["p1"]["tenu"] for r in rs) / n, 3),
            delegable=round(sum(bool(r["p4"]["delegables"]) for r in rs) / n, 3),
            r2_aucune_delegation=sum(r["etiquette"] == "R2" and r.get("mention") == "aucune délégation établie"
                                     for r in rs),
            r2_delegation_inferieure=sum(r["etiquette"] == "R2" and r.get("mention") == "délégation inférieure à un "
                                         "témoin" for r in rs),
            tout_valider_battu=round(sum(r["p2"].get("tout_valider", {}).get("battu", False) for r in rs) / n, 3),
            liste_fixe_battue=round(sum(r["p2"]["liste_fixe"]["battu"] for r in rs) / n, 3),
            tri_battu=round(sum(r["p2"]["tri_risque"]["battu"] for r in rs) / n, 3),
            temoins_battus_par_le_budget=round(sum(r["p2"]["liste_fixe"]["battu_partout"]
                                                   and r["p2"]["tri_risque"]["battu_partout"] for r in rs) / n, 3),
            hors_hypothese_jugee=round(sum(any(c["statut"] == "jugée" for c in r["p1"]["hors_hypothese"])
                                           for r in rs) / n, 3),
            hors_hypothese_hors_banque=round(sum(hors_banque(r) for r in rs) / n, 3),
            m_moyen=round(float(np.mean([r["p1"]["m"] for r in rs])), 1),
            oracle_delegue_moyen_fort=round(sum(r.get("oracle", {}).get("cellules_moyen_fort_deleguees", 0) > 0
                                                for r in rs) / n, 3),
            oracle_max_sur_budget_median=round(float(np.median([r.get("oracle", {}).get("max_centre_sur_budget") or 0
                                                                for r in rs])), 3),
            couverture_moyenne=round(float(np.mean([r["p0"]["couverture"] for r in rs])), 4),
            duree_moyenne_s=round(float(np.mean([r["duree"] for r in rs])), 1))
        out.append(lig)
    return out


CLE_WB_HAIKU = "WorkBench/haiku/ECR"


def lignes_delegabilite(dl: list) -> list:
    """Par case (témoins, ρ, multiple) : délégable selon Q14 (taux estimé au plus la barre, n'importe quel type mérité),
    délégable par un type faible seulement, délégable selon le classement prouvé (borne haute au plus la barre) ; pour
    l'écriture réversible de Haiku dans WorkBench : classée « sous la barre » (prouvé à ρ = 1, et sous hypothèse à ρ̂),
    selon le nombre d'erreurs, et source de ρ̂ (règle N3). Quatrième passage : le mécanisme entre dans la clé."""
    out = []
    cle = lambda r: (r.get("mecanisme", "beta"), r["temoins"], r["rho"], r["multiple"])  # noqa: E731
    for mec, t, rho, mult in sorted({cle(r) for r in dl}):
        rs = [r for r in dl if cle(r) == (mec, t, rho, mult)]
        n = len(rs)
        wb = [r["faibles"].get(CLE_WB_HAIKU) for r in rs]
        wb = [w for w in wb if w]
        z = [w for w in wb if w[1] == 0]
        u = [w for w in wb if w[1] in (1, 2)]
        part = lambda ws, f: round(sum(1 for w in ws if f(w)) / max(1, len(ws)), 3)  # noqa: E731
        out.append(dict(
            mecanisme=mec, temoins=int(t), rho=rho, multiple=mult, n=n,
            au_moins_une_delegable=round(sum(bool(r["delegables"]) for r in rs) / n, 3),
            toutes_delegables=round(sum(len(r["delegables"]) == 12 for r in rs) / n, 3),
            au_moins_une_delegable_par_un_type_faible=round(sum(bool(r["delegables_faibles"]) for r in rs) / n, 3),
            au_moins_une_prouvee=round(sum(bool(r["delegables_prouvees"]) for r in rs) / n, 3),
            au_moins_une_prouvee_sous_hypothese=round(sum(bool(r.get("delegables_prouvees_hypothese"))
                                                          for r in rs) / n, 3),
            delegables_moyenne=round(float(np.mean([len(r["delegables"]) for r in rs])), 2),
            wb_haiku_delegable=round(sum("WorkBench/haiku" in r["delegables"] for r in rs) / n, 3),
            wb_haiku_ecr_prouve=part(wb, lambda w: w[0] == "S"),
            wb_haiku_ecr_prouve_sous_hypothese=part(wb, lambda w: len(w) > 6 and w[6] == "S"),
            wb_haiku_ecr_zero_erreur=part(wb, lambda w: w[1] == 0),
            wb_haiku_ecr_prouve_si_zero=part(z, lambda w: w[0] == "S"),
            wb_haiku_ecr_prouve_si_une_ou_deux=part(u, lambda w: w[0] == "S"),
            wb_haiku_rho_source_commun=part(wb, lambda w: w[5] == 1),
            wb_haiku_rho_source_plancher=part(wb, lambda w: w[5] == 2),
            wb_haiku_rho_source_configuration=part(wb, lambda w: w[5] == 0),
            wb_haiku_rho_median=round(float(np.median([w[4] for w in wb])), 3) if wb else None))
    return out


def lignes_critiques(cl: list) -> list:
    """Par case critique : part des répétitions où un type exactement à la barre est dit « sous la barre », par la
    classe prouvée (ρ = 1) et par la classe sous hypothèse (ρ̂) ; l'écriture réversible de Haiku dans WorkBench, puis
    tous les types faibles réunis ; intervalle de Wilson à 95 %."""
    def wilson(k, n):
        if not n:
            return (float("nan"), float("nan"))
        z, p = 1.959964, k / n
        c = (p + z * z / (2 * n)) / (1 + z * z / n)
        h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        return (round(c - h, 4), round(c + h, 4))
    out = []
    cle = lambda r: (r["mecanisme"], r["temoins"], r["rho"], r["multiple"])  # noqa: E731
    for mec, t, rho, mult in sorted({cle(r) for r in cl}):
        rs = [r for r in cl if cle(r) == (mec, t, rho, mult)]
        wb = [r["faibles"][CLE_WB_HAIKU] for r in rs if CLE_WB_HAIKU in r["faibles"]]
        tous = [w for r in rs for w in r["faibles"].values()]
        k1, kh = sum(w[0] == "S" for w in wb), sum(len(w) > 6 and w[6] == "S" for w in wb)
        t1, th = sum(w[0] == "S" for w in tous), sum(len(w) > 6 and w[6] == "S" for w in tous)
        out.append(dict(mecanisme=mec, temoins=int(t), rho=rho, multiple=mult, n=len(rs), n_wb=len(wb),
                        wb_prouve=round(k1 / max(1, len(wb)), 4), wb_prouve_ic=wilson(k1, len(wb)),
                        wb_prouve_sous_hypothese=round(kh / max(1, len(wb)), 4),
                        wb_prouve_sous_hypothese_ic=wilson(kh, len(wb)),
                        n_types_faibles=len(tous), tous_prouve=round(t1 / max(1, len(tous)), 5),
                        tous_prouve_sous_hypothese=round(th / max(1, len(tous)), 5)))
    return out


def _ecrire_csv(nom: str, lignes: list) -> None:
    if not lignes:
        return
    with open(os.path.join(DOSSIER, nom), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)


def resumer() -> None:
    reps = lire_jsonl("repetitions.jsonl")
    _ecrire_csv("frequences.csv", lignes_frequences(reps))
    if os.path.exists(os.path.join(DOSSIER, "delegabilite.jsonl")):
        _ecrire_csv("delegabilite.csv", lignes_delegabilite(lire_jsonl("delegabilite.jsonl")))
    if os.path.exists(os.path.join(DOSSIER, "critiques.jsonl")):
        _ecrire_csv("critiques.csv", lignes_critiques(lire_jsonl("critiques.jsonl")))
    print(f"tableaux écrits dans {os.path.relpath(DOSSIER, SIMULATION)}/ ({len(reps)} répétitions)")


def verifier() -> list:
    with open(os.path.join(DOSSIER, "meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    actuelles = empreintes()
    return sorted(k for k, v in meta["empreintes"].items() if actuelles.get(k) != v)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--lancer", action="store_true")
    g.add_argument("--resumer", action="store_true")
    g.add_argument("--verifier", action="store_true")
    a = p.parse_args(argv)
    if a.lancer:
        lancer()
    elif a.resumer:
        resumer()
    else:
        ecarts = verifier()
        print("empreintes conformes" if not ecarts else "empreintes changées : " + ", ".join(ecarts))
        return 1 if ecarts else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
