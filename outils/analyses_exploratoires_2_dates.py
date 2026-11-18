"""Exploratory (18/11/2026), after the verdict, no effect on the label: the reviewers' decisions on WorkBench plots.

analytics.create_plot alerts often differ from the expected action only by the end date (the agent plots up to
2023-11-30, "today", where the benchmark expects 2023-11-29). This script counts how the alert review decided those
cases, and recomputes the judged type (WorkBench/Haiku, reversible writes, calibration half) under consistent
decisions, with the same rho = 1 lower bound as the first exploratory pass. Aggregates only, written to
experience/exploratoire_2/M_plots_review.csv and M_plots_sensitivity.csv.

    cd ROOT/simulation; .venv/bin/python ../outils/analyses_exploratoires_2_dates.py ROOT/experience
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "simulation"))
sys.path.insert(0, str(ROOT / "outils"))
from rejeu import entrees as EN  # noqa: E402
from rejeu import types_regle as TR  # noqa: E402
from analyses_exploratoires import lo_rho1, lire_csv  # noqa: E402
from analyses_exploratoires_2 import write  # noqa: E402

SIGLE = {x.nom: x.sigle for x in TR.TABLE}
V1, V2 = "vague1/2026-11-10_06-19-06", "vague2/2026-11-10_19-53-13"
PLOT = "analytics.create_plot"


def end_on_30(j: str) -> bool:
    return "11-30" in j or "jour courant" in j or "aujourd" in j


def end_only(j: str) -> bool:
    return bool(re.search(r"time_max 2023-11-30 au lieu de 2023-11-29", j)) and "time_min" not in j


def main(exp: Path):
    out = exp / "exploratoire_2"
    out.mkdir(exist_ok=True)
    opp = {tuple(x) for x in json.load(open(exp / "retraits_motif_a/oppositions_motif_a.json"))}
    just, alerts = {}, {}
    for v in (V1, V2):
        for d in csv.DictReader(open(exp / v / "relecture/decisions.csv", encoding="utf-8")):
            just[d["alerte_id"]] = (d["decision"], d["justification"])
        for a in json.load(open(exp / v / "relecture/alertes.json", encoding="utf-8")):
            alerts[a["id"]] = a

    # Review decisions on all plot alerts (both waves, all models)
    dec = Counter()
    by_task = defaultdict(set)
    for aid, a in alerts.items():
        if a["outil"] != PLOT or aid not in just:
            continue
        d, j = just[aid]
        dec[(d, "end on 30 Nov" if end_on_30(j) else "other")] += 1
        by_task[a["tache"]].add(d)
    both = sum(1 for s in by_task.values() if {"levée", "confirmée"} <= s)
    rows = [dict(decision={"levée": "lifted", "confirmée": "confirmed"}.get(d, d), case=c, alerts=n)
            for (d, c), n in sorted(dec.items())]
    rows.append(dict(decision="tasks decided both ways", case=f"of {len(by_task)} plot tasks", alerts=both))
    write(out, "M_plots_review", rows)

    # Judged type under consistent decisions: the engine's confirmed errors (retained decisions), classified by hand-
    # checked patterns of the reviewers' justifications (18/11: every confirmed plot error of the judged type was read).
    waves = [EN.relecture_du_dossier(str(exp / V1), "1"), EN.relecture_du_dossier(str(exp / V2), "2")]
    ent = EN.charger_entrees_vagues([str(exp / V1), str(exp / V2)], waves, oppositions=opp)
    appart = EN.appartenance_depuis_partage(json.load(open(exp / "tirage/partage.json")))
    removed = {(t["environnement"], str(t["tache"])) for t in
               json.load(open(exp / "retraits_motif_a/retraits_motif_a.json"))} - opp
    e = [r for r in lire_csv(exp / "rejeu_final/ecart.csv") if r["version"] == "principal"
         and r["environnement"] == "WorkBench" and "haiku" in r["modele"] and r["type"] == "ECR"][0]
    n, x, bar = int(e["n"]), int(e["x"]), float(e["barre"])
    mbar = float(e["m_bar"]) if e.get("m_bar") else n / float(e["n_eff_preuve"])

    def confirmed(a, p):
        aid = ent.jointure.alertes.get((a.partie, a.rang))
        if aid is None:
            return False
        d = ent.jointure.decisions.get(aid)
        return d is None or d.decision == "confirmée" or (d.motif == "a" and (p.environnement, p.tache) in opp)

    def kind(j):
        if re.search(r"condition|aucune action n.était attendue|Aucune action n.était attendue", j):
            return "condition false, no plot expected"
        if "time_min" in j or "2023-11-03" in j:
            return "window shifted by one day"
        if end_on_30(j) or "29 novembre" in j or "2023-11-29" in j:
            return "end date only (30 instead of 29 November)"
        return "other"
    c = Counter()
    total = 0
    for p in ent.parties:
        if not p.statut_ok or p.environnement != "WorkBench" or "haiku" not in p.modele or (p.environnement, p.tache) in removed:
            continue
        if appart.get((EN.strate(p.environnement, p.tache), p.tache)) != "calibration":
            continue
        for a in ent.actions.get(p.id, []):
            if a.kind != "écriture" or SIGLE.get(a.type, a.type) != "ECR":
                continue
            if a.verdict in ("fausse", "doublon", "refusée") and confirmed(a, p):
                total += 1
                if a.outil == PLOT:
                    c[kind(just.get(ent.jointure.alertes.get((a.partie, a.rang)), ("", ""))[1])] += 1
    assert total == x, (total, x)
    plots = sum(c.values())
    end_only_n = c["end date only (30 instead of 29 November)"]
    window_n = c["window shifted by one day"]
    scen = [("engine decisions", x),
            ("end-date-only cases lifted", x - end_only_n),
            ("end-date and window-shift cases lifted", x - end_only_n - window_n),
            ("no plot error counted", x - plots)]
    rows = [dict(scenario=s, errors=xx, writes=n, rate=round(xx / n, 4), lower_bound_rho1=round(lo_rho1(xx, n, mbar), 5),
                 bar=round(bar, 6), established=lo_rho1(xx, n, mbar) > bar, plot_errors=plots,
                 end_date_only=end_only_n, window_shift=window_n,
                 condition_false=c["condition false, no plot expected"], other=c["other"]) for s, xx in scen]
    k = 0
    while lo_rho1(k, n, mbar) <= bar:
        k += 1
    for r in rows:
        r["min_errors_established"] = k
    write(out, "M_plots_sensitivity", rows)
    for r in rows:
        print(r)
    print(dict(dec), "tasks both ways:", both, "of", len(by_task))


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
