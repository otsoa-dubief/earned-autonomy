"""Tables and figures for the paper, built from the output folder of the final replay (simulation/rejeu).

Outside the frozen perimeter. Reads only the CSV files written by the frozen engine and reformats them (English labels,
rounding, counts); it adds only simple derived quantities (counts, ratios, n_eff x bar), never a new test. Run it on the final replay folder once the verdict exists:

    simulation/.venv/bin/python outils/tables_article.py <replay output folder> <destination folder>

Writes <destination>/tables.md and <destination>/fig_gap.png, fig_budget.png. A warning line from the source files
(e.g. a pilot dry run) is copied at the top of tables.md.
"""
import csv
import io
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

LEVELS = {"faible": "low", "moyen": "medium", "fort": "high"}
HALVES = {"calibration": "calibration", "confirmation": "confirmation", "tout": "whole reserve"}
STATUS = {"sans objet": "without object", "tenue, non mise à l'épreuve": "held, not put to the test",
          "jugée": "judged", "non réfutée": "judged, not refuted", "réfutée": "judged, excess established",
          "non testable": "non-testable"}
MAIN_E = "0.05"  # main analysis: validator misses 5 % (plan); other e values are complements
ENVS = {"aviation": "airline", "commerce": "retail", "banque": "banking", "WorkBench": "WorkBench"}
COLOURS = ["#1f77b4", "#d62728", "#2ca02c"]
RULES_ORDER =["B-tout", "tout_valider", "liste_fixe", "tri_risque", "hasard", "oracle", "B-regulier", "A½", "A¼"]
RULE_NAMES = {"B-tout": "B-all (main)", "tout_valider": "validate everything", "liste_fixe": "fixed list",
              "tri_risque": "risk triage", "hasard": "random, same pace", "oracle": "oracle", "B-regulier": "B-regular"}


def read(folder: Path, name: str):
    p = folder / f"{name}.csv"
    if not p.exists():
        return [], ""
    lines = p.read_text(encoding="utf-8").splitlines()
    warning = " ".join(l.lstrip("# ") for l in lines if l.startswith("#"))
    return list(csv.DictReader(io.StringIO("\n".join(l for l in lines if not l.startswith("#"))))), warning


def num(x, d=2):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return "–"
    if math.isnan(v):
        return "–"
    if math.isinf(v):
        return "∞"
    return f"{v:.{d}f}"


def pct(x):
    try:
        return f"{100 * float(x):.1f} %"
    except (TypeError, ValueError):
        return "–"


def clean(s):
    """Rounds long floats to 3 decimals and writes "–" for nan (engine wording otherwise kept)."""
    s = re.sub(r"(?<![\w.])(-?\d+\.\d{4,})", lambda mm: f"{float(mm.group(1)):.3f}", str(s))
    return re.sub(r"\bnan\b", "–", s)


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def build(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    parts, warn = [], ""

    dec, w = read(src, "decision")
    warn = warn or w
    if dec:
        parts.append("## Decision table (plan 5.14), as written by the engine\n\n"
                     + table(["element", "value", "detail"], [[r["element"], clean(r["valeur"]), clean(r["detail"])] for r in dec])
                     + "\n\n*Engine wording, in French, kept for traceability and not reproduced in the paper (the "
                     "English decision table is Table 2, Section 6.2). In the rows « témoin liste_fixe : battu », "
                     "« témoin tri_risque : battu » and « point 2 : réussite », « battu » and « les trois témoins battus » "
                     "are the wording of the criterion, not a result: point 2 is not judged under R4.*")

    sym, w = read(src, "symetrie")
    warn = warn or w
    if sym:
        parts.append("## Table 4. Symmetry between halves\n\n" + table(
            ["environment", "half", "tasks", "removed", "played (removed tasks included)", "writes low", "writes medium",
             "writes high"],
            [[r["environnement"], HALVES.get(r["moitie"], r["moitie"]), r["taches"], r["taches_retirees"],
              r["taches_jouees"], r["ecritures_faible"], r["ecritures_moyen"], r["ecritures_fort"]] for r in sym])
            + "\n\n*Note: the airline halves are unbalanced at high stakes (542 writes in calibration against 1,166 in "
              "confirmation, with 20 tasks per half).*")

    rt, w = read(src, "reussite_taches")
    warn = warn or w
    if rt:
        parts.append("## Task success rate per model and environment\n\n" + table(
            ["set", "environment", "model", "episodes", "successes", "rate", "95 % interval"],
            [[HALVES.get(r["jeu"], r["jeu"]), r["environnement"], r["modele"].replace("claude-", ""), r["parties"],
              r["reussies"], pct(r["taux"]), f"[{pct(r['lo'])} ; {pct(r['hi'])}]"] for r in rt]))

    bud, w = read(src, "budget")
    warn = warn or w
    if bud:
        agg = defaultdict(lambda: defaultdict(int))
        worst = {}
        for r in bud:
            if r["analyse"] != "principale" or r["regle"] != "B-tout" or r["e"] != MAIN_E:
                continue
            kind = "configuration" if r["type_suite"] == "configuration" else "model-change scenario"
            k = (kind, r["environnement"], LEVELS.get(r["niveau"], r["niveau"]))
            agg[k][STATUS.get(r["statut"], r["statut"])] += 1
            if r["etabli"] in ("True", "true", "1"):
                agg[k]["established excess"] += 1
            if r.get("non_testable"):
                agg[k]["of which non-testable"] += 1
            try:
                v = float(r["rapport"])
                if v == v and r["statut"] not in ("sans objet",):
                    worst[k] = max(worst.get(k, 0.0), v)
            except ValueError:
                pass
        cols = ["without object", "held, not put to the test", "judged, not refuted", "judged, excess established",
                "of which non-testable", "established excess"]
        total = sum(sum(v for kk, v in d.items() if kk not in ("established excess", "of which non-testable"))
                    for d in agg.values())
        parts.append(f"## Table 5 (summary). B-all budget cells, main analysis (e = 5 %): {total} cells, "
                     "12 configurations and 48 model-change scenarios × 3 stakes levels\n\n"
                     + table(["sequence", "environment", "level"] + cols + ["worst ratio to budget (point estimate)"],
                             [[k[0], k[1], k[2]] + [agg[k].get(c, 0) for c in cols]
                              + [num(worst[k]) if k in worst else "–"] for k in sorted(agg)]))

    ec, w = read(src, "ecart")
    warn = warn or w
    ec = [r for r in ec if r.get("version") == "principal" and r.get("n") and int(r["n"]) > 0]
    if ec:
        def judge(r):
            try:
                return num(float(r["n_eff"]) * float(r["barre"]), 3)
            except ValueError:
                return "–"
        def mark(r):
            m = []
            if r["x"] == "0":
                m.append("no error observed")
            if int(r["n"]) < 10:
                m.append("tiny n")
            return "; ".join(m)
        parts.append("## Table 6. Delegation gap per configuration and action type (main version, calibration half)\n\n"
                     "*n_eff × bar ≥ 0.6905 (about ln 2; exact criterion 1 − 2^(−1/n_eff) ≤ bar) makes a type judgeable; that product uses n_eff under ρ̂ (column ρ̂), not the ρ = 1 column (for WorkBench/Haiku ECR: 97.7 × bar = 0.740, against 81.6 × bar = 0.618 at ρ = 1); an excess is established when the one-sided 95 % "
                     "Clopper-Pearson lower bound on the effective size at ρ = 1 exceeds the bar (no multiplicity correction).*\n\n"
                     + table(["environment", "model", "type", "level", "writes", "confirmed errors", "rate", "bar",
                              "rate / bar", "n_eff (ρ=1)", "lower bound (ρ=1)", "ρ̂", "n_eff × bar", "class", "judgeable",
                              "note"],
                             [[r["environnement"], r["modele"].replace("claude-", ""), r["type"],
                               LEVELS.get(r["niveau"], r["niveau"]), r["n"], r["x"], num(r["taux"], 4),
                               num(r["barre"], 5), num(r["taux_sur_barre"]), num(r["n_eff_preuve"], 1),
                               num(r["borne_basse"], 4), num(r.get("rho", ""), 3), judge(r), r["classe"], r["jugeable"],
                               mark(r)] for r in ec]))

    ecw = [r for r in read(src, "ecart")[0] if r.get("version") == "calibration et confirmation" and r.get("n")
           and int(r["n"]) > 0]
    if ecw:
        parts.append("## Table 6 bis. Delegation gap on the whole reserve (calibration and confirmation halves pooled), "
                     "DESCRIPTIVE ONLY: it cannot serve as the label\n\n" + table(
            ["environment", "model", "type", "level", "writes", "confirmed errors", "rate", "bar", "rate / bar", "class",
             "counts for delegability"],
            [[r["environnement"], r["modele"].replace("claude-", ""), r["type"], LEVELS.get(r["niveau"], r["niveau"]),
              r["n"], r["x"], num(r["taux"], 4), num(r["barre"], 5), num(r["taux_sur_barre"]), r["classe"],
              r["compte_pour_la_delegabilite"]] for r in ecw]))

    vol, w = read(src, "volume")
    vol = [r for r in vol if r["analyse"] == "principale" and r["type_suite"] == "configuration"
           and r["regle"] == "B-tout"]
    if vol:
        parts.append("## Table 7 bis. Where B-all reduced validations: share of non-capped writes at tier 2 "
                     "(executed then flagged) and tier 3 (autonomous), per configuration and type (confirmation half)\n\n"
                     + table(["environment", "model", "type", "level", "writes", "share at tier 2", "share at tier 3"],
                             [[r["environnement"], r["modele"].replace("claude-", ""), r["type"],
                               LEVELS.get(r["niveau"], r["niveau"]), num(r["ecritures_non_plafonnees"], 0),
                               pct(r["part_p2"]), pct(r["part_p3"])] for r in vol]))

    ch, w = read(src, "charges")
    warn = warn or w
    ch = [r for r in ch if r["type_suite"] == "configuration" and r["mesure"] == "charge_hors_lec" and not r["mode"]]
    if ch:
        rules = [x for x in RULES_ORDER if any(r["ligne"] == x for r in ch)]
        by = defaultdict(dict)
        for r in ch:
            by[(r["environnement"], r["modele"].replace("claude-", ""))][r["ligne"]] = (
                f"{num(r['valeur'], 1)} [{num(r['lo'], 1)} ; {num(r['hi'], 1)}]")
        parts.append("## Table 7. Validation load per 100 non-read actions, per configuration and rule\n\n" + table(
            ["environment", "model"] + [RULE_NAMES.get(x, x) for x in rules],
            [[e, m] + [by[(e, m)].get(x, "–") for x in rules] for (e, m) in sorted(by)]))

    gar, w = read(src, "garantie")
    gar = [r for r in gar if r.get("regle") == "B-tout"]
    if gar:
        def lo0(x):
            return "0.000*" if x not in ("", "nan") and float(x) < 0 else num(x, 3)

        def hi1(x):
            return "1.000*" if x not in ("", "nan") and float(x) > 1 else num(x, 3)
        parts.append("## Table G. B-all: share of replays reaching tier 3 per phase (guarantee measure, plan 5.12; no threshold)\n\n" + table(
            ["sequence", "environment", "model", "model Y", "mode", "type", "phase", "share at tier 3", "95 % interval"],
            [[r["type_suite"], r["environnement"], r["modele"].replace("claude-", ""), r["modele_Y"].replace("claude-", ""),
              r["mode"], r["type"], r["phase"], num(r["part_rep_palier3"], 3), f"[{lo0(r['lo'])} ; {hi1(r['hi'])}]"]
             for r in gar])
            + "\n\n*Rule B-all only (`garantie.csv` also holds the secondary rules). An asterisk marks an interval bound "
              "outside [0, 1] given by the interval method for a proportion; it is shown clipped.*")

    excl_p = src.parent / "exploratoire" / "A_parties_exclues.csv"
    if excl_p.exists():
        ex = list(csv.DictReader(io.StringIO("".join(l for l in open(excl_p, encoding="utf-8") if not l.startswith("#")))))
        cnt = defaultdict(int)
        for r in ex:
            cnt[(r["environnement"], r["modele"].replace("claude-", ""), r["causes"])] += 1
        parts.append(f"## Table 3. Episodes excluded after two failed attempts, per configuration and cause ({len(ex)} in total; "
                     "`experience/exploratoire/A_parties_exclues.csv`, causes read from the error lines of the episode logs)\n\n"
                     + table(["environment", "model", "cause", "excluded episodes"],
                             [[e, m, "empty agent message" if c == "agent" else c, n] for (e, m, c), n in sorted(cnt.items())]))

    der, w = read(src, "derive")
    der = [r for r in der if r["analyse"] == "principale" and r["regle"] == "B-tout" and r["type_suite"] == "scénario"
           and "aucun" in r.get("mode_resistance", "aucun")]
    if der:
        agg = defaultdict(lambda: [0, 0, 0.0, 0])
        for r in der:
            k = (r["environnement"], r["mode"], LEVELS.get(r["niveau"], r["niveau"]))
            a = agg[k]
            a[0] += 1
            a[1] += r["verdict"] == "passe"
            a[2] = max(a[2], float(r["part_rep_plus_d_une"] or 0))
            a[3] = max(a[3], int(float(r["max_constatees"] or 0)))
        parts.append("## Table 8. Model-change scenarios (announced and silent): withdrawal criterion of decision 5, B-all "
                     "(`derive.csv`, main analysis, immediate detection)\n\n" + table(
                         ["environment", "change", "level", "scenario × type rows", "passing", "worst share of replays with >1 "
                          "detected error per autonomy period", "max detected errors in a period"],
                         [[k[0], {"annoncé": "announced", "silencieux": "silent"}.get(k[1], k[1]), k[2], a[0], a[1], pct(a[2]), a[3]]
                          for k, a in sorted(agg.items())]))

    epr, w = read(src, "epreuves")
    epr = [r for r in epr if r["analyse"] == "principale" and r["type_suite"] == "configuration" and r["regle"] == "B-tout"]
    if epr:
        parts.append("## Trials (B-all, configurations; `epreuves.csv`, means over replays)\n\n" + table(
            ["environment", "model", "trials opened", "attempted", "passed", "failed", "impossible", "validations"],
            [[r["environnement"], r["modele"].replace("claude-", ""), num(r["ep_ouvertes"], 1), num(r["ep_tentatives"], 1),
              num(r["ep_reussies"], 1), num(r["ep_ratees"], 1), num(r["ep_impossibles"], 1), num(r["ep_validations"], 1)]
             for r in epr]))

    cho, w = read(src, "choix")
    if cho:
        parts.append("## Secondary rules and choice rule (`choix.csv`; the choice is reapplied descriptively, no effect on the label)\n\n"
                     + table(["rule", "judged cells", "failures (established excess)", "no established excess", "worst upper bound / budget", "margin",
                              "load", "retained", "reason"],
                             [[RULE_NAMES.get(r["regle"], r["regle"]), r["n_cellules"], r["echecs"], r["tient"], num(r["pire"]),
                               num(r["marge"]), num(r["charge"]), r["retenue"], r["motif"] or "–"] for r in cho]))

    res, w = read(src, "resistance")
    warn = warn or w
    res = [r for r in res if r.get("type_suite") == "bilan du mode"]
    if res:
        parts.append("## Table 9. Stress tests: summary per mode (plan 5.11; no effect on the label)\n\n" + table(
            ["mode", "rule", "failures (established excess)", "worst upper bound / budget", "alert (B-all)"],
            [[r["mode"], RULE_NAMES.get(r["regle"], r["regle"]), r["echecs"], num(r["pire_rapport_hi"]),
              r["alerte"] or "–"] for r in res]))

    head = "# Results tables (generated by outils/tables_article.py)\n\n"
    if warn:
        head += f"> **Source warning, copied as is:** {warn[:600]}\n\n"
    (dst / "tables.md").write_text(head + "\n\n".join(parts) + "\n", encoding="utf-8")
    figures(ec, bud, dst)
    print(f"{len(parts)} tables -> {dst / 'tables.md'}")


def figures(ec, bud, dst: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    envs = sorted({r["environnement"] for r in ec})
    if envs:
        fig, axes = plt.subplots(1, len(envs), figsize=(4 * len(envs), 4), squeeze=False)
        models = sorted({r["modele"] for r in ec})
        for ax, env in zip(axes[0], envs):
            rows = [r for r in ec if r["environnement"] == env]
            types = sorted({(r["niveau"], r["type"]) for r in rows})
            for j, m in enumerate(models):
                for i, t in enumerate(types):
                    for r in rows:
                        if r["modele"] == m and (r["niveau"], r["type"]) == t:
                            try:
                                y, hi = float(r["taux_sur_barre"]), float(r["borne_haute_sur_barre"])
                            except ValueError:
                                continue
                            y = max(y, 1e-3)  # a zero rate is drawn at the floor 1e-3 (say so in the caption)
                            ax.errorbar(i + (j - 1) * 0.2, y, yerr=[[0], [max(hi - y, 0)]], fmt="o", capsize=2,
                                        color=COLOURS[j % len(COLOURS)])
            ax.axhline(1, color="grey", lw=0.8, ls="--")
            ax.set_yscale("log")
            ax.set_xticks(range(len(types)))
            ax.set_xticklabels([f"{t}\n{LEVELS.get(n, n)}" for n, t in types], fontsize=7)
            ax.set_title(ENVS.get(env, env))
            ax.set_ylabel("error rate / bar (log)")
        from matplotlib.lines import Line2D
        axes[0][0].legend([Line2D([], [], marker="o", ls="", color=COLOURS[j % len(COLOURS)]) for j in range(len(models))],
                          [m.replace("claude-", "") for m in models], fontsize=7)
        fig.tight_layout()
        fig.savefig(dst / "fig_gap.png", dpi=150)
        plt.close(fig)

    judged = [r for r in bud if r["analyse"] == "principale" and r["regle"] == "B-tout" and r["e"] == MAIN_E
              and r["statut"] in ("jugée", "non réfutée", "réfutée") and r["type_suite"] == "configuration"]
    if judged:
        fig, ax = plt.subplots(figsize=(6, 4))
        for i, r in enumerate(judged):
            try:
                v, lo, hi = float(r["exces_100_ecritures"]), float(r["lo"]), float(r["hi"])
            except ValueError:
                continue
            ax.errorbar(i, v, yerr=[[v - lo], [hi - v]], fmt="o", capsize=2)
        for b in sorted({float(r["budget"]) for r in judged}):
            ax.axhline(b, color="red", lw=0.8, ls="--")
        ax.text(0, float(judged[0]["budget"]), " budget", color="red", va="bottom", fontsize=7)
        ax.set_ylabel("extra errors per 100 writes")
        ax.set_xlabel("judged cell")
        fig.tight_layout()
        fig.savefig(dst / "fig_budget.png", dpi=150)
        plt.close(fig)


if __name__ == "__main__":
    build(Path(sys.argv[1]), Path(sys.argv[2]))
