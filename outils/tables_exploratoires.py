"""Exploratory tables for the paper (English), from experience/exploratoire/*.csv (PLAN_SUITE T11).

Outside the frozen perimeter; reformats only. Every table is titled "Exploratory, dated 17 November 2026" and cites
its CSV. No effect on the preregistered label.

    python3 outils/tables_exploratoires.py ROOT/experience/exploratoire ROOT/article/resultats/tables_exploratoires.md
"""
import csv
import io
import sys
from pathlib import Path

ENVS = {"aviation": "airline", "commerce": "retail", "banque": "banking", "WorkBench": "WorkBench"}
LEVELS = {"faible": "low", "moyen": "medium", "fort": "high"}
DATE = "Exploratory, dated 17 November 2026"


def lire(p):
    return list(csv.DictReader(io.StringIO("".join(l for l in open(p, encoding="utf-8") if not l.startswith("#")))))


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    return "\n".join(out + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def m(x):
    return x.replace("claude-", "")


def pct(x, d=1):
    try:
        return f"{100 * float(x):.{d}f} %"
    except ValueError:
        return "–"


def main(src: Path, dst: Path):
    parts = ["# Exploratory analyses (not preregistered; no effect on the label R4)\n\n"
             "All analyses below were run after the verdict, by `outils/analyses_exploratoires.py` (X1 to X6, 17 November 2026) and `outils/analyses_exploratoires_2.py` with `outils/analyses_exploratoires_2_dates.py` (X7 and X8, 18 November 2026), reading the frozen "
             "engine's outputs and functions without modifying them. The ρ = 1 lower bound recomputed by the script "
             "reproduces the engine's bound for all 20 established excesses."]

    a = [r for r in lire(src / "A_ecart_avec_exclusions.csv") if int(r["ajout"]) > 0]
    parts.append(f"## Table X1. Episodes excluded for an empty agent message, counted as errors ({DATE}; "
                 "`A_ecart_avec_exclusions.csv`)\n\n91 episodes were excluded after two failed attempts, all caused by an "
                 "empty agent message (9 in wave 1, 82 in wave 2). On the calibration half, counting each as one confirmed "
                 "error at the highest-stakes write type expected by its task adds 24 errors (2 episodes without an "
                 "identifiable expected type), all in banking. Established excesses go from 20 to 21; the new one rests on "
                 "5 writes.\n\n" + table(
                     ["environment", "model", "type", "level", "added", "rate before", "rate after", "established before",
                      "established after"],
                     [[ENVS.get(r["environnement"], r["environnement"]), m(r["modele"]), r["type"],
                       LEVELS.get(r["niveau"], r["niveau"]), r["ajout"], pct(r["taux"]), pct(r["taux_avec_exclusions"]),
                       r["etabli"], r["etabli_avec_exclusions"]] for r in a]))

    c = sorted(lire(src / "C_sensibilite_fausses_confirmations.csv"), key=lambda r: float(r["part_max_fausses_confirmations"]))
    parts.append(f"## Table X2. Sensitivity of established excesses to false confirmations ({DATE}; "
                 "`C_sensibilite_fausses_confirmations.csv`)\n\nLargest share of confirmed errors that could be false alerts "
                 "while the excess stays established (same ρ = 1 bound as the engine). For reference, in the author's "
                 "blind review, agreement with the first reviewer was 13 of 15 in each wave, and 3 of the 10 confirmed "
                 "alerts he reviewed were lifted.\n\n" + table(
                     ["environment", "model", "type", "level", "writes", "confirmed errors", "bar", "max share of false confirmations"],
                     [[ENVS.get(r["environnement"], r["environnement"]), m(r["modele"]), r["type"],
                       LEVELS.get(r["niveau"], r["niveau"]), r["n"], r["x"], f"{100 * float(r['barre']):.4g} %",
                       pct(r["part_max_fausses_confirmations"], 0)] for r in c]))

    d = lire(src / "D_erreurs_et_reussite.csv")
    parts.append(f"## Table X3. Confirmed action errors and task success ({DATE}; `D_erreurs_et_reussite.csv`)\n\n"
                 "Whole reserve (calibration and confirmation halves), kept episodes, removed tasks excluded. An action error does not always mean a failed task, especially "
                 "on WorkBench, which scores the final state only.\n\n" + table(
                     ["environment", "model", "episodes", "successful", "with ≥1 confirmed error",
                      "of which successful", "share successful among those"],
                     [[ENVS.get(r["environnement"], r["environnement"]), m(r["modele"]), r["parties"], r["reussies"],
                       r["avec_erreur_confirmee"], r["avec_erreur_mais_reussies"],
                       pct(r["part_reussies_parmi_avec_erreur"]) if r["part_reussies_parmi_avec_erreur"] else "–"]
                      for r in d]))

    e = lire(src / "E_refusees_parmi_erreurs.csv")
    tot, ref = sum(int(r["erreurs_confirmees"]) for r in e), sum(int(r["dont_refusees"]) for r in e)
    parts.append(f"## Table X4. Refused writes among confirmed errors ({DATE}; `E_refusees_parmi_erreurs.csv`)\n\n"
                 f"{ref} of {tot} confirmed errors ({100 * ref / tot:.1f} %) are writes refused by the tool, which the frozen "
                 "rule counts as errors without damage.\n\n" + table(
                     ["environment", "model", "type", "level", "confirmed errors", "of which refused", "share"],
                     [[ENVS.get(r["environnement"], r["environnement"]), m(r["modele"]), r["type"],
                       LEVELS.get(r["niveau"], r["niveau"]), r["erreurs_confirmees"], r["dont_refusees"],
                       pct(r["part_refusees"])] for r in e]))

    f = lire(src / "F_erreurs_palier2_approx.csv")
    parts.append(f"## Table X5. Errors executed then flagged at tier 2 under B-all, approximation ({DATE}; "
                 "`F_erreurs_palier2_approx.csv`)\n\nWhole-reserve error rate × share of writes at tier 2 on the confirmation half, per 100 writes "
                 "of the type. At tier 2 these errors are executed before being flagged.\n\n" + table(
                     ["environment", "model", "type", "share at tier 2", "error rate (whole reserve)", "errors per 100 writes"],
                     [[ENVS.get(r["environnement"], r["environnement"]), m(r["modele"]), r["type"], pct(r["part_palier2"]),
                       pct(r["taux_reserve_entiere"], 2), r["erreurs_executees_puis_signalees_pour_100"]] for r in f]))

    g = lire(src / "G_intervalle_rho.csv")
    parts.append(f"## Table X6. Uncertainty on ρ̂ ({DATE}; `G_intervalle_rho.csv`)\n\nTask-level bootstrap, 2,000 draws, "
                 "seed 20261117, estimator `classes.rho_anova` pooled over types, not the engine's stratified Fleiss–Cuzick estimator, so the share of draws above 0.885 likely understates the risk. The reconstruction of clusters is approximate "
                 "(0.800 here against 0.819 in the engine); the engine's value is the one of record. The single type that "
                 "carries R4 stays judgeable while ρ̂ ≤ 0.885.\n\n" + table(
                     ["environment", "model", "tasks", "ρ̂ (reconstructed)", "95 % interval", "share of draws above 0.885"],
                     [[ENVS.get(r["environnement"], r["environnement"]), m(r["modele"]), r["taches"], r["rho_chapeau"],
                       f"[{r['ic95_bas']} ; {r['ic95_haut']}]", pct(r["part_bootstrap_au_dessus_0_885"])] for r in g]))

    src2 = src.parent / "exploratoire_2"  # second exploratory pass, 18 November 2026
    if src2.exists():
        i = lire(src2 / "I_success_and_action_errors.csv")
        parts.append("## Table X7. Task success and confirmed action errors, both directions (Exploratory, dated 18 November "
                     "2026; `exploratoire_2/I_success_and_action_errors.csv`)\n\nWhole reserve, kept episodes, removed tasks "
                     "excluded. Task-level and action-level scores disagree in both directions.\n\n" + table(
                         ["environment", "model", "episodes", "with ≥1 confirmed error", "of which successful tasks",
                          "failed episodes", "of which without confirmed error"],
                         [[ENVS.get(r["environment"], r["environment"]), m(r["model"]), r["episodes"],
                           r["with_confirmed_error"], pct(r["share_successful_among_with_error"]), r["failed"],
                           pct(r["share_without_error_among_failed"])] for r in i]))
        rv = lire(src2 / "M_plots_review.csv")
        se = lire(src2 / "M_plots_sensitivity.csv")
        both = [r for r in rv if r["decision"] == "tasks decided both ways"][0]
        parts.append("## Table X8. WorkBench plots: inconsistent alert review and sensitivity of the judged type (Exploratory, "
                     "dated 18 November 2026; `exploratoire_2/M_plots_review.csv`, `M_plots_sensitivity.csv`)\n\n"
                     "`analytics.create_plot` alerts often differ from the expected action only by the end date (the agent "
                     "plots up to 30 November, \"today\", where the benchmark expects 29 November). The reviewing instances "
                     "decided that case both ways: " + "; ".join(f"{r['decision']}, {r['case']}: {r['alerts']}" for r in rv
                                                                  if r["decision"] != "tasks decided both ways")
                     + f"; {both['alerts']} {both['case']} had alerts decided both ways. Below, the judged type (WorkBench/Haiku, "
                     "reversible writes, calibration half; every confirmed plot error read and classified) under consistent decisions; lower bound at ρ = 1 as in Table X2.\n\n"
                     + table(["scenario", "confirmed errors", "writes", "rate", "lower bound (ρ = 1)", "bar", "established"],
                             [[r["scenario"], r["errors"], r["writes"], pct(r["rate"]), pct(r["lower_bound_rho1"], 2),
                               pct(r["bar"], 2), "yes" if r["established"] == "True" else "no"] for r in se]))

    dst.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    print(f"{len(parts) - 1} tables -> {dst}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
