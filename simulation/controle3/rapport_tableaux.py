"""Tableaux du rapport du contrôle 3, lus dans les résultats bruts ; aucun calcul du moteur.

Usage (depuis simulation/) :
    .venv/bin/python -m controle3.rapport_tableaux                 huitième passage (resultats_v8/), apparié au septième
    .venv/bin/python -m controle3.rapport_tableaux resultats_v7 resultats_v6   septième passage, apparié au sixième
    .venv/bin/python -m controle3.rapport_tableaux resultats_v6 resultats_v5   sixième passage, apparié au cinquième
    .venv/bin/python -m controle3.rapport_tableaux resultats_v5 resultats_v4   cinquième passage, apparié au quatrième
    .venv/bin/python -m controle3.rapport_tableaux resultats_v4 resultats_v3   quatrième passage, apparié au troisième
    .venv/bin/python -m controle3.rapport_tableaux resultats_v3 resultats_v2   troisième passage, apparié au second
    .venv/bin/python -m controle3.rapport_tableaux resultats_v2 resultats
                                                                    un passage, apparié à un autre (second contre premier)
    .venv/bin/python -m controle3.rapport_tableaux resultats        premier passage (historique ; sa délégabilité, au
                                                                    format du premier passage, n'est pas relue ici)
"""
from __future__ import annotations

import collections
import json
import os
import sys

import numpy as np

from . import ICI
from . import mondes as MD
from rejeu import decision as DE

ETIQ = DE.ORDRE_ETIQUETTES
# amendement R4 (07/11) : les résultats des passages précédents nomment « volume insuffisant » ce qui est désormais
# « preuves insuffisantes » (même rang, motif « aucun type jugeable »)
ANCIENNES = {"volume insuffisant": DE.PREUVES_INSUFFISANTES}
SEUIL = 0.80
SURVEILLES = ("A", "B", "C", "F1", "F2", "V")
WB_HAIKU = "WorkBench/haiku/ECR"


def etiquette_lue(e: str) -> str:
    return ANCIENNES.get(e, e)


def lire(dossier, nom):
    with open(os.path.join(dossier, nom), encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def pct(x, n):
    return f"{100 * x / n:.0f} %" if n else "—"


def ic_wilson(k, n, z=1.96):
    if not n:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def compte_attendu(rs, attendu: str) -> int:
    """Répétitions où sort l'étiquette attendue, avec la mention si elle est écrite (R2, « preuves insuffisantes ») ;
    plusieurs étiquettes possibles, séparées par « ou » (cinquième passage, monde C ; `mondes.conforme`)."""
    return sum(1 for r in rs if MD.conforme(etiquette_lue(r["etiquette"]), r.get("mention", ""), attendu))


def frequences(reps, meta):
    print("| Monde | Attendu | n | R5 | R1 | preuves insuffisantes | R4 | R2 (aucune / inférieure) | confirmée | "
          "Attendue la plus fréquente ? | Part de l'attendue (IC 95 %) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for nom, m in meta["mondes"].items():
        rs = [r for r in reps if r["monde"] == nom]
        n = len(rs)
        if not n:
            continue
        c = collections.Counter(etiquette_lue(r["etiquette"]) for r in rs)
        aucune = sum(1 for r in rs if r["etiquette"] == "R2" and r.get("mention") == "aucune délégation établie")
        inf = c.get("R2", 0) - aucune
        k = compte_attendu(rs, m["attendu"])
        atts = MD.etiquettes_attendues(m["attendu"])   # cinquième passage : plusieurs étiquettes possibles (C)
        k_etiq = sum(c.get(a, 0) for a in atts)
        autres = max((v for e, v in c.items() if e not in atts), default=0)
        plus = "oui" if k_etiq > autres else ("égalité" if k_etiq == autres else "non")
        lo, hi = ic_wilson(k, n)
        alerte = " **⚠**" if (plus != "oui" or k < k_etiq or (nom in SURVEILLES and k / n < SEUIL)) else ""
        print(f"| {nom} | {m['attendu']} | {n} | {c.get('R5', 0)} | {c.get('R1', 0)} | "
              f"{c.get(DE.PREUVES_INSUFFISANTES, 0)} | {c.get('R4', 0)} | "
              f"{c.get('R2', 0)} ({aucune} / {inf}) | {c.get('confirmée', 0)} | {plus}{alerte} | "
              f"{pct(k, n)} ({100 * lo:.0f}–{100 * hi:.0f}) |")
    seuil = [r for r in reps if r["monde"] == "B-seuil"]
    if seuil:   # cinquième passage : niveau du max-T au seuil exact (RAPPORT 9.3, point 2)
        k1 = sum(not r["p1"]["tenu"] for r in seuil)
        lo, hi = ic_wilson(k1, len(seuil))
        print(f"\nB-seuil (dépassement vrai d'une fois le budget) : R1 dans {k1} répétitions sur {len(seuil)} "
              f"({pct(k1, len(seuil))}, IC 95 % {100 * lo:.1f}–{100 * hi:.1f} %) ; attendu au plus 5 %"
              + (" **⚠**" if k1 / len(seuil) > 0.05 else ""))
        rap = []   # contrôle de l'étalonnage sur les répétitions mêmes (b_seuil/)
        for r in seuil:
            xs = [x for cle, x in r["p1"].get("centres_config", {}).items()
                  if cle.startswith("commerce/") and cle.endswith("/faible") and x is not None]
            if xs:
                rap.append(float(np.mean(xs)))
        if len(rap) > 1:
            print(f"Valeur centrale ÷ budget, commerce à enjeu faible (moyenne des configurations jugées, "
                  f"{len(rap)} répétitions) : {np.mean(rap):.3f} ± {1.96 * np.std(rap, ddof=1) / np.sqrt(len(rap)):.3f}")


def apparies(reps, precedentes, meta):
    """Comparaison appariée avec un passage précédent (mêmes données, même graine du moteur) : changements
    d'étiquette, configurations délégables (moyenne sur 12), oracle (délégation à enjeu moyen ou fort, dépassement du
    budget par la plus haute valeur centrale)."""
    prec = {(r["monde"], r["rep"]): r for r in precedentes}
    print("\n| Monde | appariées | changements d'étiquette (avant → après : répétitions) | délégables, avant → après "
          "| oracle à enjeu moyen ou fort, avant → après | oracle au-delà du budget, avant → après |")
    print("|---|---|---|---|---|---|")
    for nom in meta["mondes"]:
        paires = [(prec[(r["monde"], r["rep"])], r) for r in reps if r["monde"] == nom and (r["monde"], r["rep"]) in prec]
        if not paires:
            continue
        ch = collections.Counter((a["etiquette"], b["etiquette"]) for a, b in paires if a["etiquette"] != b["etiquette"])
        txt = ", ".join(f"{x} → {y} : {v}" for (x, y), v in ch.most_common()) or "aucun"
        nd = lambda r: len(r["p4"]["delegables"])  # noqa: E731
        mf = lambda r: r.get("oracle", {}).get("cellules_moyen_fort_deleguees", 0) > 0  # noqa: E731
        dep = lambda r: (r.get("oracle", {}).get("max_centre_sur_budget") or 0) > 1  # noqa: E731
        print(f"| {nom} | {len(paires)} | {txt} | {np.mean([nd(a) for a, _ in paires]):.1f} → "
              f"{np.mean([nd(b) for _, b in paires]):.1f} | {sum(mf(a) for a, _ in paires)} → "
              f"{sum(mf(b) for _, b in paires)} | {sum(dep(a) for a, _ in paires)} → {sum(dep(b) for _, b in paires)} |")


def rho_par_source(reps, meta):
    """ρ̂ des configurations par source (règle G1 jusqu'au troisième passage, N3 ensuite), par monde, face au ρ vrai :
    pour chaque source, nombre de configurations × répétitions, médiane et maximum de ρ̂."""
    sources = sorted({t0["source_rho"] for r in reps for types in r.get("classes", {}).values()
                      for t0 in list(types.values())[:1]})
    print("\n| Monde | ρ vrai | " + " | ".join(f"ρ̂ « {s} » : n, médiane, max" for s in sources) + " |")
    print("|---|---|" + "---|" * len(sources))
    for nom, m in meta["mondes"].items():
        par = collections.defaultdict(list)
        for r in reps:
            if r["monde"] != nom:
                continue
            for types in r["classes"].values():
                t0 = next(iter(types.values()), None)
                if t0:
                    par[t0["source_rho"]].append(t0["rho"])
        if not par:
            continue
        vrai = (f"{m['rho']:g}" + (" (latent)" if m.get("mecanisme") == "logit_normal" else "")
                if not m.get("rhos_heterogenes") else "/".join(f"{x:g}" for x in m["rhos_heterogenes"]))
        cel = lambda v: f"{len(v)}, {np.median(v):.2f}, {max(v):.2f}" if v else "—"  # noqa: E731
        print(f"| {nom} | {vrai} | " + " | ".join(cel(par.get(s, [])) for s in sources) + " |")


def diagnostics(reps, meta):
    print("\n| Monde | point 1 non tenu | ≥ 1 délégable | délégables (moyenne sur 12) | « tout faire valider » battu | "
          "liste fixe battue | tri battu | les deux témoins battus par le budget | m moyen (B-tout) | mention hors "
          "hypothèse, cellule jugée hors banque | oracle délègue à enjeu moyen ou fort | durée moyenne |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for nom in meta["mondes"]:
        rs = [r for r in reps if r["monde"] == nom]
        n = len(rs)
        if not n:
            continue
        f = lambda cond: pct(sum(1 for r in rs if cond(r)), n)  # noqa: E731
        hb = lambda r: any(c["statut"] == "jugée" and "/banque/" not in "/" + c["famille"] + "/"  # noqa: E731
                           for c in r["p1"]["hors_hypothese"])
        print(f"| {nom} | {f(lambda r: not r['p1']['tenu'])} | {f(lambda r: r['p4']['delegables'])} | "
              f"{np.mean([len(r['p4']['delegables']) for r in rs]):.1f} | "
              f"{f(lambda r: r['p2'].get('tout_valider', {}).get('battu'))} | "
              f"{f(lambda r: r['p2']['liste_fixe']['battu'])} | {f(lambda r: r['p2']['tri_risque']['battu'])} | "
              f"{f(lambda r: r['p2']['liste_fixe']['battu_partout'] and r['p2']['tri_risque']['battu_partout'])} | "
              f"{np.mean([r['p1']['m'] for r in rs]):.0f} | {f(hb)} | "
              f"{f(lambda r: r.get('oracle', {}).get('cellules_moyen_fort_deleguees', 0) > 0)} | "
              f"{np.mean([r['duree'] for r in rs]):.0f} s |")


def details(reps):
    par = collections.defaultdict(list)
    for r in reps:
        par[r["monde"]].append(r)
    print("\n### Détails")
    for nom, rs in par.items():
        n = len(rs)
        print(f"\n**{nom}** (n = {n})")
        etab = collections.Counter()
        for r in rs:
            for c in r["p1"]["etablies"]:
                etab[(c["famille"].split("/")[0], c["famille"].split("/")[1], c["niveau"])] += 1
        if etab:
            print("- cellules de B-tout établies (genre, environnement, niveau : répétitions) : "
                  + ", ".join(f"{k[0]} {k[1]} {k[2]} : {v}" for k, v in etab.most_common(8)))
        dl = collections.Counter(len(r["p4"]["delegables"]) for r in rs)
        print("- nombre de configurations délégables (sur 12) : " + ", ".join(f"{k} : {v}" for k, v in sorted(dl.items())))
        for t in ("tout_valider", "liste_fixe", "tri_risque"):
            v = [r["p2"].get(t) for r in rs if r["p2"].get(t)]
            if not v:
                continue
            d = [x["diff_moyenne"] for x in v if x["diff_moyenne"] is not None]
            hi = [x["intervalle"][1] for x in v if x["intervalle"][1] is not None]
            txt = (f"- {t} : battu {pct(sum(x['battu'] for x in v), n)} (par le budget "
                   f"{pct(sum(x['battu_partout'] for x in v), n)}, par la charge {pct(sum(x['battu_charge'] for x in v), n)})")
            if d:
                txt += f" ; différence de charge médiane {np.median(d):+.2f} (borne haute médiane {np.median(hi):+.2f})"
            print(txt)
        ment = collections.Counter(r.get("mention") for r in rs if r["etiquette"] == "R2")
        if ment:
            print("- mentions de R2 : " + "; ".join(f"{k} : {v}" for k, v in ment.items()))
        mb = [r["p1"]["max_centre_sur_budget"] for r in rs if r["p1"]["m"]]
        if mb:
            print(f"- B-tout, plus haute valeur centrale ÷ budget sur les cellules jugées : médiane {np.median(mb):.2f}, "
                  f"max {max(mb):.2f}")
        ob = [r.get("oracle", {}).get("max_centre_sur_budget") for r in rs if r.get("oracle")]
        if ob:
            print(f"- oracle, plus haute valeur centrale ÷ budget (configurations) : médiane {np.median(ob):.2f}, "
                  f"max {max(ob):.2f}")


def mec(r) -> str:
    return r.get("mecanisme", "beta")


def delegabilite(dl):
    autres = sorted({mec(r) for r in dl} - {"beta"})
    if autres:   # quatrième passage : les autres mécanismes, tableau compact
        for mc in autres:
            sous = [r for r in dl if mec(r) == mc]
            mults_m = sorted({r["multiple"] for r in sous})
            for t in (False, True):
                print(f"\nMécanisme {mc}, témoins en défaut : {'oui' if t else 'non'}. Au moins une délégable / "
                      "prouvée (ρ = 1) / prouvée sous hypothèse (ρ̂) ; configurations délégables en moyenne :")
                print("| ρ | " + " | ".join(f"{m:g} ×" for m in mults_m) + " |")
                print("|---|" + "---|" * len(mults_m))
                for rho in sorted({r["rho"] for r in sous}):
                    cells = []
                    for m in mults_m:
                        rs = [r for r in sous if r["temoins"] == t and r["rho"] == rho and r["multiple"] == m]
                        n = len(rs)
                        cells.append(f"{pct(sum(bool(r['delegables']) for r in rs), n)} / "
                                     f"{pct(sum(bool(r['delegables_prouvees']) for r in rs), n)} / "
                                     f"{pct(sum(bool(r.get('delegables_prouvees_hypothese')) for r in rs), n)} ; "
                                     f"{np.mean([len(r['delegables']) for r in rs]):.2f}" if rs else "—")
                    print(f"| {rho:g} | " + " | ".join(cells) + " |")
    dl = [r for r in dl if mec(r) == "beta"]
    mults = sorted({r["multiple"] for r in dl})
    for t in (False, True):
        print(f"\nTémoins en défaut : {'oui' if t else 'non'}. Au moins une configuration délégable (Q14, lue sur le "
              "taux médian depuis N1) / par un type faible seulement / prouvée (borne haute au plus la barre ; à ρ = 1 "
              "depuis N3) / prouvée sous hypothèse (à ρ̂, quatrième passage) :")
        print("| ρ | " + " | ".join(f"{m:g} ×" for m in mults) + " |")
        print("|---|" + "---|" * len(mults))
        for rho in sorted({r["rho"] for r in dl}):
            cells = []
            for m in mults:
                rs = [r for r in dl if r["temoins"] == t and r["rho"] == rho and r["multiple"] == m]
                n = len(rs)
                hyp = (f" / {pct(sum(bool(r['delegables_prouvees_hypothese']) for r in rs), n)}"
                       if rs and "delegables_prouvees_hypothese" in rs[0] else "")
                cells.append(f"{pct(sum(bool(r['delegables']) for r in rs), n)} / "
                             f"{pct(sum(bool(r['delegables_faibles']) for r in rs), n)} / "
                             f"{pct(sum(bool(r['delegables_prouvees']) for r in rs), n)}{hyp}")
            print(f"| {rho:g} | " + " | ".join(cells) + " |")
        print("\nConfigurations délégables, moyenne sur 12 :")
        print("| ρ | " + " | ".join(f"{m:g} ×" for m in mults) + " |")
        print("|---|" + "---|" * len(mults))
        for rho in sorted({r["rho"] for r in dl}):
            cells = []
            for m in mults:
                rs = [r for r in dl if r["temoins"] == t and r["rho"] == rho and r["multiple"] == m]
                cells.append(f"{np.mean([len(r['delegables']) for r in rs]):.2f}" if rs else "—")
            print(f"| {rho:g} | " + " | ".join(cells) + " |")
    for mult in (1.0, 5.0, 10.0):
        rs = [r for r in dl if not r["temoins"] and r["rho"] == 0.3 and r["multiple"] == mult]
        c = collections.Counter(x.split("/")[0] + "/" + x.split("/")[2] for r in rs for x in r["estimes_sous"])
        print(f"\nTypes estimés sous la barre à {mult:g} × barre, ρ = 0,3, sans témoin en défaut (configurations × "
              f"répétitions, sur {len(rs)} répétitions × 3 modèles) : " + "; ".join(f"{k} : {v}" for k, v in c.most_common(9)))


def certification_a_tort(dl):
    """Classement prouvé (borne haute de Clopper-Pearson sur la taille effective ; ρ̂ selon G1 jusqu'au troisième
    passage, ρ = 1 depuis N3) d'un type exactement à la barre (1 × barre) : part des répétitions où il est dit « sous la
    barre » (nominal : 5 % au plus). Les cases critiques à 10 000 répétitions : `critiques`."""
    dl = [r for r in dl if mec(r) == "beta"]
    print("\n| ρ | type (configuration) | n | « sous la barre » à tort | IC 95 % | ρ̂ médian | sources de ρ̂ |")
    print("|---|---|---|---|---|---|---|")
    for rho in sorted({r["rho"] for r in dl}):
        rs = [r for r in dl if r["rho"] == rho and r["multiple"] == 1.0 and not r["temoins"]]
        cles = sorted({k for r in rs for k in r["faibles"]})
        tot_k = tot_n = 0
        for k in cles:
            v = [r["faibles"][k] for r in rs if k in r["faibles"]]
            s = sum(1 for w in v if w[0] == "S")
            tot_k += s
            tot_n += len(v)
            if s or k in (WB_HAIKU, "commerce/haiku/ECR", "aviation/haiku/ECR"):
                lo, hi = ic_wilson(s, len(v))
                noms = ("config", "commun", "plancher") if len(v[0]) > 6 else ("config", "env", "tous", "plancher")
                src = collections.Counter(noms[w[5]] if 0 <= w[5] < len(noms) else "?" for w in v)
                print(f"| {rho:g} | {k} | {len(v)} | {pct(s, len(v))} | {100 * lo:.1f}–{100 * hi:.1f} % | "
                      f"{np.median([w[4] for w in v]):.2f} | {dict(src)} |")
        print(f"| {rho:g} | tous les types faibles réunis | {tot_n} | {pct(tot_k, tot_n)} | | | |")


def critiques(cl):
    """Cases critiques (quatrième passage) : type exactement à la barre, 10 000 répétitions par case ; part dite « sous
    la barre » par la classe prouvée (ρ = 1) et par la classe sous hypothèse (ρ̂), intervalle de Wilson à 95 %."""
    print("\nCases critiques (type exactement à la barre ; nominal : 5 % au plus) :")
    print("| mécanisme | ρ vrai | témoins en défaut | n | Haiku WorkBench réversible, prouvé (ρ = 1) | prouvé sous "
          "hypothèse (ρ̂) | tous les types faibles, prouvé | tous, sous hypothèse |")
    print("|---|---|---|---|---|---|---|---|")
    cle = lambda r: (mec(r), r["rho"], r["temoins"])  # noqa: E731
    for mc, rho, t in sorted({cle(r) for r in cl}):
        rs = [r for r in cl if cle(r) == (mc, rho, t)]
        wb = [r["faibles"][WB_HAIKU] for r in rs if WB_HAIKU in r["faibles"]]
        tous = [w for r in rs for w in r["faibles"].values()]
        cel = lambda ws, i: (lambda k, n: f"{100 * k / n:.2f} % ({100 * ic_wilson(k, n)[0]:.2f}–"  # noqa: E731
                             f"{100 * ic_wilson(k, n)[1]:.2f})" if n else "—")(
            sum(1 for w in ws if len(w) > i and w[i] == "S"), len(ws))
        print(f"| {mc} | {rho:g} | {'oui' if t else 'non'} | {len(rs)} | {cel(wb, 0)} | {cel(wb, 6)} | "
              f"{cel(tous, 0)} | {cel(tous, 6)} |")


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    dossier = os.path.join(ICI, argv[0] if argv else "resultats_v8")
    precedent = argv[1] if len(argv) > 1 else ("resultats_v7" if not argv else None)
    with open(os.path.join(dossier, "meta.json"), encoding="utf-8") as f:
        meta = json.load(f)
    reps = lire(dossier, "repetitions.jsonl")
    print(f"Répétitions : {len(reps)} ; statut : {meta.get('statut')} ; durée : {meta.get('duree_s')} s\n")
    frequences(reps, meta)
    if precedent and os.path.exists(os.path.join(ICI, precedent, "repetitions.jsonl")):
        print(f"\nApparié à {precedent}/ :")
        apparies(reps, lire(os.path.join(ICI, precedent), "repetitions.jsonl"), meta)
    if any("source_rho" in t for r in reps[:1] for types in r.get("classes", {}).values() for t in types.values()):
        rho_par_source(reps, meta)
    diagnostics(reps, meta)
    details(reps)
    chemin = os.path.join(dossier, "delegabilite.jsonl")
    if os.path.exists(chemin):
        dl = lire(dossier, "delegabilite.jsonl")
        if dl and "delegables_faibles" in dl[0]:
            delegabilite(dl)
            certification_a_tort(dl)
    if os.path.exists(os.path.join(dossier, "critiques.jsonl")):
        critiques(lire(dossier, "critiques.jsonl"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
