"""Final figures of the paper, vector PDF (PLAN_SUITE T29). Outside the frozen perimeter; reads only the CSV
outputs of the final replay and draws them, without any new statistic.

    simulation/.venv/bin/python outils/figures_article.py experience/rejeu_final article/figures

Fig. 1: extra errors per 100 writes against the budget, B-all, judged cells (main analysis, e = 5 %).
Fig. 2: delegation gap, error rate / bar with the rho = 1 interval, log scale, one panel per environment.
Fig. 3: validation load against extra errors at low stakes, per rule and configuration.
Readable in black and white: models differ by marker shape, rules by marker shape and fill.
"""
import csv
import io
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams.update({"font.size": 8, "pdf.fonttype": 42, "svg.hashsalt": "autonomie",
                            "path.simplify": False})
import matplotlib.pyplot as plt  # noqa: E402

ENVS = {"WorkBench": "WorkBench", "aviation": "airline", "banque": "banking", "commerce": "retail"}
ORDER = ["WorkBench", "aviation", "banque", "commerce"]
LEVELS = {"faible": "low", "moyen": "medium", "fort": "high"}
MODELS = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"]
MARK = {"claude-haiku-5-5": "o", "claude-sonnet-5-5": "s", "claude-opus-5-5": "^"}
SHORT = {m: m.replace("claude-", "").replace("-5-5", " 5.5").capitalize() for m in MODELS}
FLOOR = 1e-3  # a zero rate is drawn at this floor, hollow


def read(src: Path, name: str):
    text = "".join(l for l in open(src / f"{name}.csv", encoding="utf-8") if not l.startswith("#"))
    return list(csv.DictReader(io.StringIO(text)))


def save(fig, path: Path):
    fig.savefig(path, metadata={"CreationDate": None, "ModDate": None, "Producer": None, "Creator": None})
    plt.close(fig)


def fig_budget(bud, dst):
    judged = [r for r in bud if r["analyse"] == "principale" and r["regle"] == "B-tout" and r["e"] == "0.05"
              and r["statut"] == "non réfutée"]
    fig, axes = plt.subplots(1, 4, figsize=(7, 2.4), sharey=True)
    for ax, env in zip(axes, ORDER):
        rows = sorted((r for r in judged if r["environnement"] == env),
                      key=lambda r: (r["type_suite"], r["modele"], r["modele_Y"], r["mode"]))
        for i, r in enumerate(rows):
            v, lo, hi = float(r["exces_100_ecritures"]), float(r["lo"]), float(r["hi"])
            filled = r["type_suite"] == "configuration"
            ax.errorbar(i, v, yerr=[[max(v - lo, 0)], [max(hi - v, 0)]], fmt=MARK[r["modele"]], ms=3.5, capsize=1.5,
                        color="black", mfc="black" if filled else "white", lw=0.6)
        for b in sorted({float(r["budget"]) for r in rows}):
            ax.axhline(b, color="black", lw=0.8, ls="--")
        ax.axhline(0, color="grey", lw=0.4)
        ax.set_title(f"{ENVS[env]} ({len(rows)} cells)")
        ax.set_xticks([])
    axes[0].set_ylabel("extra errors per 100 writes")
    axes[0].text(0, 0.52, "budget (low stakes)", fontsize=6, va="bottom")
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker=MARK[m], ls="", color="black", ms=4) for m in MODELS]
    handles += [Line2D([], [], marker="o", ls="", color="black", mfc="white", ms=4)]
    fig.legend(handles, [SHORT[m] + " (configuration)" for m in MODELS] + ["model-change scenario (hollow)"],
               loc="lower center", ncol=4, fontsize=6, frameon=False)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    save(fig, dst / "fig1_budget.pdf")
    return len(judged)


def fig_gap(ec, dst):
    rows = [r for r in ec if r["version"] == "principal" and r["n"] not in ("", "0")]
    fig, axes = plt.subplots(1, 4, figsize=(7, 2.8), sharey=True)
    drawn = {}
    for ax, env in zip(axes, ORDER):
        sub = [r for r in rows if r["environnement"] == env]
        types = sorted({(r["niveau"], r["type"]) for r in sub}, key=lambda t: (list(LEVELS).index(t[0]), t[1]))
        for i, t in enumerate(types):
            for j, m in enumerate(MODELS):
                for r in sub:
                    if r["modele"] != m or (r["niveau"], r["type"]) != t:
                        continue
                    bar = float(r["barre"])
                    y = float(r["taux"]) / bar
                    lo, hi = float(r["borne_basse"]) / bar, float(r["borne_haute"]) / bar
                    x = i + (j - 1) * 0.22
                    zero = float(r["taux"]) == 0
                    small = int(r["n"]) < 5
                    yy = max(y, FLOOR)
                    ax.errorbar(x, yy, yerr=[[max(yy - max(lo, FLOOR), 0)], [max(hi - yy, 0)]], fmt=MARK[m], ms=3.5,
                                capsize=1.5, lw=0.6, color="grey" if small else "black",
                                mfc="white" if (zero or small) else ("black" if r["classe"] == "au-dessus" else "grey"))
                    if small:
                        ax.annotate(f"n={r['n']}", (x, yy), fontsize=5, xytext=(2, 2), textcoords="offset points")
                    drawn[(env, m, r["type"])] = (y, lo, hi)
        ax.axhline(1, color="black", lw=0.8, ls="--")
        ax.set_yscale("log")
        ax.set_xticks(range(len(types)))
        ax.set_xticklabels([f"{t}\n{LEVELS[n]}" for n, t in types], fontsize=6)
        ax.set_title(ENVS[env])
    axes[0].set_ylabel("error rate / bar (log; ρ = 1 interval)")
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker=MARK[m], ls="", color="black", ms=4) for m in MODELS]
    fig.legend(handles, [SHORT[m] for m in MODELS] + [], loc="lower center", ncol=3, fontsize=6, frameon=False)
    fig.text(0.99, 0.01, "filled: established above the bar; grey: undetermined; hollow: no observed error "
             f"(drawn at {FLOOR:g}) or fewer than 5 writes (n given)", fontsize=5, ha="right")
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    save(fig, dst / "fig2_gap.pdf")
    return drawn


def fig_load(ch, bud, dst):
    rules = {"B-tout": ("B-all", "o", "black"), "tout_valider": ("validate everything", "s", "white"),
             "liste_fixe": ("fixed list", "^", "white"), "tri_risque": ("risk triage", "D", "grey")}
    load = {(r["environnement"], r["modele"], r["ligne"]): float(r["valeur"]) for r in ch
            if r["type_suite"] == "configuration" and r["mesure"] == "charge_hors_lec" and r["ligne"] in rules}
    exc = {(r["environnement"], r["modele"], r["regle"]): float(r["exces_100_ecritures"] or 0) for r in bud
           if r["analyse"] == "principale" and r["e"] == "0.05" and r["type_suite"] == "configuration"
           and r["niveau"] == "faible" and r["regle"] in rules}
    fig, axes = plt.subplots(1, 4, figsize=(7, 2.4), sharey=True)
    for ax, env in zip(axes, ORDER):
        for rule, (label, mk, fc) in rules.items():
            pts = [(load[(env, m, rule)], exc.get((env, m, rule), 0.0)) for m in MODELS if (env, m, rule) in load]
            ax.scatter([p[0] for p in pts], [p[1] for p in pts], marker=mk, s=14, facecolors=fc, edgecolors="black",
                       linewidths=0.6, label=label)
        ax.axhline(0.5, color="black", lw=0.8, ls="--")
        ax.set_title(ENVS[env])
        ax.set_xlabel("validations per 100\nnon-read actions", fontsize=6)
        ax.set_xlim(0, 105)
    axes[0].set_ylabel("extra errors per 100 writes\n(low stakes)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=6, frameon=False)
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    save(fig, dst / "fig3_load.pdf")


def main(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    n1 = fig_budget(read(src, "budget"), dst)
    drawn = fig_gap(read(src, "ecart"), dst)
    fig_load(read(src, "charges"), read(src, "budget"), dst)
    print(f"fig1: {n1} judged cells; fig2: {len(drawn)} types; fig3 written -> {dst}")
    return drawn


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
