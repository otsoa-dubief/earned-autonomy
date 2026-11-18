"""Analyses exploratoires après le verdict (17/11/2026), toutes marquées EXPLORATOIRES, sans effet sur l'étiquette.

Hors du périmètre figé. Réutilise en lecture les fonctions du moteur figé (chargement des entrées, bornes de
Clopper-Pearson à ρ = 1) sans les modifier. Quatre analyses :

A. Exclusions pour message vide de l'agent (fixée d'avance dans le dépôt cusv6) : chaque partie exclue dont les
   tentatives ont échoué par un message vide de l'agent compte comme une erreur confirmée, au type d'écriture de plus
   fort enjeu attendu par sa tâche ; l'écart de délégation (version principale, moitié de calibration) est recalculé.
   Approximation déclarée : le type attendu est pris parmi les écritures jugées « juste » des parties gardées de la
   même tâche (une écriture juste correspond exactement à une action attendue).
B. Réserve entière : types qui comptent pour la délégabilité, par version de `ecart.csv`, tels que le moteur les a
   écrits (aucun calcul nouveau).
C. Sensibilité aux fausses confirmations : pour chaque dépassement établi, la plus grande part f des erreurs
   confirmées qui pourraient être de fausses alertes sans que le dépassement cesse d'être établi (même borne que le
   moteur : `classes.bornes_cp` sur la taille effective à ρ = 1).
D. Erreurs et réussite des tâches : par configuration, parties gardées avec au moins une écriture fausse confirmée,
   et part de ces parties où la tâche est quand même réussie.

    cd ROOT/simulation; .venv/bin/python ../outils/analyses_exploratoires.py ROOT/experience
"""
import csv
import io
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "simulation"))
from rejeu import classes as CL  # noqa: E402
from rejeu import entrees as EN  # noqa: E402
from rejeu import types_regle as TR  # noqa: E402
SIGLE = {x.nom: x.sigle for x in TR.TABLE}

V1, V2 = "vague1/2026-11-10_06-19-06", "vague2/2026-11-10_19-53-13"
ORDRE = {"faible": 0, "moyen": 1, "fort": 2}
EN_TETE = ("EXPLORATOIRE : analyse après le verdict, sans effet sur l'étiquette préenregistrée (R4). "
           "Écrite par outils/analyses_exploratoires.py le 17/11/2026.")


def lire_csv(p):
    lignes = [l for l in open(p, encoding="utf-8") if not l.startswith("#")]
    return list(csv.DictReader(io.StringIO("".join(lignes))))


def ecrire(dossier, nom, lignes):
    p = dossier / f"{nom}.csv"
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(f"# {EN_TETE}\n")
        if lignes:
            w = csv.DictWriter(fh, fieldnames=list(lignes[0].keys()))
            w.writeheader()
            w.writerows(lignes)
    return p


def lo_rho1(x, n, mbar):
    """Borne basse à ρ = 1, comme classes.borne_basse : n_eff = n / m̄, x_eff = x × n_eff / n."""
    if n <= 0 or x <= 0:
        return 0.0
    ne = n / mbar
    return CL.bornes_cp(x * ne / n, ne)[0]


def main(exp: Path):
    sortie = exp / "exploratoire"
    sortie.mkdir(exist_ok=True)
    ecart = lire_csv(exp / "rejeu_final/ecart.csv")
    princ = [r for r in ecart if r["version"] == "principal" and r["n"] and int(r["n"]) > 0]
    partage = json.load(open(exp / "tirage/partage.json", encoding="utf-8"))
    appart = EN.appartenance_depuis_partage(partage)
    oppositions = {tuple(x) for x in json.load(open(exp / "retraits_motif_a/oppositions_motif_a.json"))}
    retirees_a = {(t["environnement"], str(t["tache"])) for t in
                  json.load(open(exp / "retraits_motif_a/retraits_motif_a.json"))} - oppositions

    # Entrées comme le moteur les lit (parties gardées, actions, décisions)
    vagues = [EN.relecture_du_dossier(str(exp / V1), "1"), EN.relecture_du_dossier(str(exp / V2), "2")]
    ent = EN.charger_entrees_vagues([str(exp / V1), str(exp / V2)], vagues, oppositions=oppositions)
    parties = {p.id: p for p in ent.parties}

    def confirmee(a, p):
        aid = ent.jointure.alertes.get((a.partie, a.rang))
        if aid is None:
            return False
        d = ent.jointure.decisions.get(aid)
        if d is None:
            return True
        if d.decision == "confirmée":
            return True
        return d.motif == "a" and (p.environnement, p.tache) in oppositions

    # --- A : exclusions pour message vide de l'agent
    attendu = defaultdict(Counter)   # (env, tache) -> Counter((enjeu, type)) des écritures justes
    for pid, acts in ent.actions.items():
        p = parties.get(pid)
        if p is None:
            continue
        for a in acts:
            if a.kind == "écriture" and a.verdict == "juste" and a.enjeu in ORDRE:
                attendu[(p.environnement, p.tache)][(a.enjeu, a.type)] += 1
    exclues = []
    for v in (V1, V2):
        tent = defaultdict(list)
        for l in open(exp / v / "tentatives.jsonl", encoding="utf-8"):
            r = json.loads(l)
            if r["evenement"] != "fin":
                continue
            L = r.get("ligne", {})
            base = L.get("partie", r["id"])
            tent[base].append((L.get("statut"), r["id"], L.get("env"), L.get("modele"), str(L.get("tache"))))
        for base, ts in tent.items():
            st = {t[0] for t in ts}
            if st & {"terminée", "arrêtée"} or "échec technique" not in st:
                continue
            causes = set()
            for _, tid, *_ in ts:
                for cand in (exp / v / "logs" / f"{tid}.log",):
                    if cand.exists():
                        txt = cand.read_text(encoding="utf-8", errors="replace")
                        if "AssistantMessage must have either content" in txt:
                            causes.add("agent")
                        if "UserMessage must have either content" in txt:
                            causes.add("client")
            env, mod, tache = ts[0][2], ts[0][3], ts[0][4]
            exclues.append(dict(vague=v[:6], partie=base, environnement=env, modele=mod, tache=tache,
                                causes="+".join(sorted(causes)) or "inconnue"))
    ecrire(sortie, "A_parties_exclues", exclues)
    ajout = Counter()
    sans_type = 0
    for e in exclues:
        if e["causes"] != "agent":
            continue
        strate = EN.strate(e["environnement"], e["tache"])
        if appart.get((strate, e["tache"])) != "calibration" or (e["environnement"], e["tache"]) in retirees_a:
            continue
        c = attendu.get((e["environnement"], e["tache"]))
        if not c:
            sans_type += 1
            continue
        haut = max(ORDRE[k[0]] for k in c)
        enjeu, typ = max((k for k in c if ORDRE[k[0]] == haut), key=lambda k: c[k])
        ajout[(e["environnement"], e["modele"], SIGLE.get(typ, typ), enjeu)] += 1
    lignes_a = []
    for r in princ:
        k = (r["environnement"], r["modele"], r["type"], r["niveau"])
        n, x, barre = int(r["n"]), int(r["x"]), float(r["barre"])
        mbar = float(r["m_bar"]) if r.get("m_bar") else n / float(r["n_eff_preuve"])
        a = ajout.get(k, 0)
        lo0, lo1 = lo_rho1(x, n, mbar), lo_rho1(x + a, n + a, mbar)
        lignes_a.append(dict(environnement=k[0], modele=k[1], type=k[2], niveau=k[3], n=n, x=x, ajout=a,
                             taux=round(x / n, 5), taux_avec_exclusions=round((x + a) / (n + a), 5), barre=barre,
                             rapport=round(x / n / barre, 3), rapport_avec_exclusions=round((x + a) / (n + a) / barre, 3),
                             etabli=lo0 > barre, etabli_avec_exclusions=lo1 > barre))
    ecrire(sortie, "A_ecart_avec_exclusions", lignes_a)

    # --- B : délégabilité par version (lecture des sorties du moteur)
    lignes_b = [dict(version=r["version"], environnement=r["environnement"], modele=r["modele"], type=r["type"],
                     niveau=r["niveau"], n=r["n"], x=r["x"], compte_pour_la_delegabilite=r["compte_pour_la_delegabilite"],
                     jugeable=r["jugeable"]) for r in ecart if r["n"] and r["compte_pour_la_delegabilite"] == "True"]
    ecrire(sortie, "B_types_delegables_par_version", lignes_b)

    # --- C : sensibilité aux fausses confirmations
    lignes_c = []
    for r in princ:
        if r["depassement_etabli"] != "True":
            continue
        n, x, barre = int(r["n"]), int(r["x"]), float(r["barre"])
        mbar = float(r["m_bar"]) if r.get("m_bar") else n / float(r["n_eff_preuve"])
        f = 0.0
        while f < 1.0 and lo_rho1(x * (1 - f), n, mbar) > barre:
            f = round(f + 0.01, 2)
        lignes_c.append(dict(environnement=r["environnement"], modele=r["modele"], type=r["type"], niveau=r["niveau"],
                             n=n, x=x, barre=barre, borne_basse_rho1=round(lo_rho1(x, n, mbar), 5),
                             borne_moteur=r["borne_basse"], part_max_fausses_confirmations=round(max(f - 0.01, 0.0), 2)))
    ecrire(sortie, "C_sensibilite_fausses_confirmations", lignes_c)

    # --- D : erreurs confirmées et réussite des tâches
    agg = defaultdict(lambda: Counter())
    for pid, p in parties.items():
        if not p.statut_ok or (p.environnement, p.tache) in retirees_a:
            continue
        acts = ent.actions.get(pid, [])
        err = any(a.kind == "écriture" and a.verdict in ("fausse", "doublon", "refusée") and confirmee(a, p)
                  for a in acts)
        k = (p.environnement, p.modele)
        agg[k]["parties"] += 1
        agg[k]["reussies"] += bool(p.reussie)
        if err:
            agg[k]["avec_erreur"] += 1
            agg[k]["avec_erreur_reussies"] += bool(p.reussie)
    lignes_d = [dict(environnement=e, modele=m, parties=c["parties"], reussies=c["reussies"],
                     avec_erreur_confirmee=c["avec_erreur"], avec_erreur_mais_reussies=c["avec_erreur_reussies"],
                     part_reussies_parmi_avec_erreur=round(c["avec_erreur_reussies"] / c["avec_erreur"], 3)
                     if c["avec_erreur"] else "")
                for (e, m), c in sorted(agg.items())]
    ecrire(sortie, "D_erreurs_et_reussite", lignes_d)


    # --- E, F, G (17/11, PLAN_SUITE T10)
    import numpy as np
    TYPES_MERITE = {x.sigle for x in TR.TABLE if x.merite}
    def cal(p):
        return appart.get((EN.strate(p.environnement, p.tache), p.tache)) == "calibration"
    compte = defaultdict(Counter)          # (env, modèle, type, niveau) -> refusées / erreurs
    grappes = defaultdict(lambda: defaultdict(lambda: [0, 0]))   # (env, modèle) -> tâche -> [m, x]
    for pid, p in parties.items():
        if not p.statut_ok or (p.environnement, p.tache) in retirees_a or not cal(p):
            continue
        for a in ent.actions.get(pid, []):
            if a.kind != "écriture":
                continue
            sig = SIGLE.get(a.type, a.type)
            err = a.verdict in ("fausse", "doublon", "refusée") and confirmee(a, p)
            if err:
                compte[(p.environnement, p.modele, sig, a.enjeu)]["erreurs"] += 1
                compte[(p.environnement, p.modele, sig, a.enjeu)]["refusees"] += a.verdict == "refusée"
            if sig in TYPES_MERITE and (a.verdict == "juste" or err):
                g = grappes[(p.environnement, p.modele)][p.tache]
                g[0] += 1
                g[1] += int(err)
    lignes_e = [dict(environnement=k[0], modele=k[1], type=k[2], niveau=k[3], erreurs_confirmees=c["erreurs"],
                     dont_refusees=c["refusees"], part_refusees=round(c["refusees"] / c["erreurs"], 3))
                for k, c in sorted(compte.items()) if c["erreurs"]]
    ecrire(sortie, "E_refusees_parmi_erreurs", lignes_e)
    tot_e = sum(l["erreurs_confirmees"] for l in lignes_e)
    tot_ecart = sum(int(r["x"]) for r in princ)

    vol = lire_csv(exp / "rejeu_final/volume.csv")
    ecw = {(r["environnement"], r["modele"], r["type"], r["niveau"]): r for r in ecart
           if r["version"] == "calibration et confirmation" and r["n"] and int(r["n"]) > 0}
    lignes_f = []
    for r in vol:
        if r["analyse"] != "principale" or r["type_suite"] != "configuration" or r["regle"] != "B-tout":
            continue
        k = (r["environnement"], r["modele"], r["type"], r["niveau"])
        e = ecw.get(k)
        if e is None or not float(r["part_p2"] or 0):
            continue
        taux = int(e["x"]) / int(e["n"])
        lignes_f.append(dict(environnement=k[0], modele=k[1], type=k[2], niveau=k[3], part_palier2=round(float(r["part_p2"]), 3),
                             taux_reserve_entiere=round(taux, 4),
                             erreurs_executees_puis_signalees_pour_100=round(100 * taux * float(r["part_p2"]), 3)))
    ecrire(sortie, "F_erreurs_palier2_approx", lignes_f)

    rng = np.random.default_rng(20261117)
    lignes_g = []
    for (env, mod), g in sorted(grappes.items()):
        m = np.array([v[0] for v in g.values()], dtype=float)
        x = np.array([v[1] for v in g.values()], dtype=float)
        r0 = CL.rho_anova(m, x)
        if r0 is None:
            continue
        boot = []
        for _ in range(2000):
            i = rng.integers(0, len(m), len(m))
            v = CL.rho_anova(m[i], x[i])
            if v is not None:
                boot.append(v)
        lo, hi = (np.percentile(boot, [2.5, 97.5]) if boot else (float("nan"), float("nan")))
        lignes_g.append(dict(environnement=env, modele=mod, taches=len(m), rho_chapeau=round(r0, 3),
                             ic95_bas=round(float(lo), 3), ic95_haut=round(float(hi), 3),
                             part_bootstrap_au_dessus_0_885=round(float(np.mean(np.array(boot) > 0.885)), 3) if boot else ""))
    ecrire(sortie, "G_intervalle_rho", lignes_g)
    print(f"E : {tot_e} erreurs confirmées (ecart.csv principal : {tot_ecart}) ; F : {len(lignes_f)} lignes ; "
          f"G : {[(l['environnement'], l['modele'][7:], l['rho_chapeau'], l['ic95_bas'], l['ic95_haut']) for l in lignes_g if l['environnement']=='WorkBench']}")
    print(f"A : {len(exclues)} parties exclues ({Counter(e['causes'] for e in exclues)}), "
          f"ajouts {sum(ajout.values())} erreurs, sans type attendu {sans_type}")
    print(f"A : établis avant {sum(l['etabli'] for l in lignes_a)}, après {sum(l['etabli_avec_exclusions'] for l in lignes_a)}")
    print(f"B : {len(lignes_b)} lignes ; C : {len(lignes_c)} dépassements ; D : {len(lignes_d)} configurations")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
