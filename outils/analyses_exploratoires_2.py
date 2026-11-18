"""Second exploratory pass after the verdict (18/11/2026), all EXPLORATORY, no effect on the pre-registered label (R4).

Outside the frozen perimeter. Reads the replay inputs exactly as outils/analyses_exploratoires.py does (frozen engine
loaders, kept episodes, confirmed alerts, removed tasks), on the whole reserve (both halves), and writes aggregates
only, to experience/exploratoire_2/. The first exploratory pass (experience/exploratoire/, deposited on Zenodo) is not
touched. Questions asked after seeing the results; read as description, not as tests.

H. Confirmed errors by tool: writes, confirmed errors and their kind (wrong, duplicate, refused), per environment.
I. Task success and action errors: per configuration, episodes with a confirmed error that still succeed, and failed
   episodes with no confirmed error.
J. Error profile per configuration: error rate per write, episodes with at least one error, share of each kind.
K. Where errors fall in an episode: rank of each confirmed error among the episode's writes (first, second, later).
L. Concentration by task: how many tasks carry the errors, and how consistently a task fails across passes.

    cd ROOT/simulation; .venv/bin/python ../outils/analyses_exploratoires_2.py ROOT/experience
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "simulation"))
from rejeu import entrees as EN  # noqa: E402
from rejeu import types_regle as TR  # noqa: E402

SIGLE = {x.nom: x.sigle for x in TR.TABLE}
V1, V2 = "vague1/2026-11-10_06-19-06", "vague2/2026-11-10_19-53-13"
FAUX = ("fausse", "doublon", "refusée")
HEAD = ("EXPLORATORY: analysis after the verdict, no effect on the pre-registered label (R4). "
        "Written by outils/analyses_exploratoires_2.py on 18/11/2026.")


def write(folder, name, rows):
    p = folder / f"{name}.csv"
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(f"# {HEAD}\n")
        if rows:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    return p


def main(exp: Path):
    out = exp / "exploratoire_2"
    out.mkdir(exist_ok=True)
    oppositions = {tuple(x) for x in json.load(open(exp / "retraits_motif_a/oppositions_motif_a.json"))}
    removed = {(t["environnement"], str(t["tache"])) for t in
               json.load(open(exp / "retraits_motif_a/retraits_motif_a.json"))} - oppositions
    removed |= {(t["environnement"], str(t["tache"])) for t in
                json.load(open(exp / "audit_sans_alerte/taches_retirees_audit.json"))}
    waves = [EN.relecture_du_dossier(str(exp / V1), "1"), EN.relecture_du_dossier(str(exp / V2), "2")]
    ent = EN.charger_entrees_vagues([str(exp / V1), str(exp / V2)], waves, oppositions=oppositions)
    parties = {p.id: p for p in ent.parties if p.statut_ok and (p.environnement, p.tache) not in removed}

    def confirmed(a, p):
        aid = ent.jointure.alertes.get((a.partie, a.rang))
        if aid is None:
            return False
        d = ent.jointure.decisions.get(aid)
        if d is None or d.decision == "confirmée":
            return True
        return d.motif == "a" and (p.environnement, p.tache) in oppositions

    tool = defaultdict(Counter)        # (env, tool, type, level) -> counts
    conf = defaultdict(Counter)        # (env, model) -> counts
    rank = defaultdict(Counter)        # (env, model) -> position of each error
    task = defaultdict(lambda: defaultdict(Counter))  # (env, model) -> task -> counts
    for pid, p in parties.items():
        writes = sorted((a for a in ent.actions.get(pid, []) if a.kind == "écriture"), key=lambda a: a.rang)
        k = (p.environnement, p.modele)
        errs = 0
        for i, a in enumerate(writes):
            tk = (p.environnement, a.outil, SIGLE.get(a.type, a.type), a.enjeu)
            tool[tk]["writes"] += 1
            tool[tk][f"writes_{p.modele}"] += 1
            conf[k]["writes"] += 1
            if a.verdict in FAUX and confirmed(a, p):
                errs += 1
                tool[tk]["errors"] += 1
                tool[tk][a.verdict] += 1
                tool[tk][f"errors_{p.modele}"] += 1
                conf[k]["errors"] += 1
                conf[k][a.verdict] += 1
                rank[k]["first" if i == 0 else "second" if i == 1 else "later"] += 1
                if p.reussie:
                    conf[k]["errors_in_successful"] += 1
        conf[k]["episodes"] += 1
        conf[k]["successful"] += bool(p.reussie)
        conf[k]["with_error"] += errs > 0
        conf[k]["with_error_successful"] += errs > 0 and bool(p.reussie)
        conf[k]["failed_without_error"] += (p.reussie is False) and errs == 0
        conf[k]["failed"] += p.reussie is False
        task[k][p.tache]["episodes"] += 1
        task[k][p.tache]["with_error"] += errs > 0
        task[k][p.tache]["errors"] += errs

    models = sorted({p.modele for p in parties.values()})
    rows_h = []
    for (env, outil, typ, lvl), c in sorted(tool.items(), key=lambda kv: (-kv[1]["errors"], kv[0])):
        r = dict(environment=env, tool=outil, type=typ, level=lvl, writes=c["writes"], confirmed_errors=c["errors"],
                 rate=round(c["errors"] / c["writes"], 4) if c["writes"] else "", wrong=c["fausse"],
                 duplicate=c["doublon"], refused=c["refusée"])
        for m in models:
            r[f"errors_{m}"] = c[f"errors_{m}"]
            r[f"writes_{m}"] = c[f"writes_{m}"]
        rows_h.append(r)
    write(out, "H_errors_by_tool", rows_h)

    rows_i, rows_j, rows_k = [], [], []
    for (env, mod), c in sorted(conf.items()):
        rows_i.append(dict(environment=env, model=mod, episodes=c["episodes"], successful=c["successful"],
                           with_confirmed_error=c["with_error"], with_error_but_successful=c["with_error_successful"],
                           share_successful_among_with_error=round(c["with_error_successful"] / c["with_error"], 3)
                           if c["with_error"] else "",
                           failed=c["failed"], failed_without_confirmed_error=c["failed_without_error"],
                           share_without_error_among_failed=round(c["failed_without_error"] / c["failed"], 3)
                           if c["failed"] else "",
                           share_errors_in_successful_tasks=round(c["errors_in_successful"] / c["errors"], 3)
                           if c["errors"] else ""))
        rows_j.append(dict(environment=env, model=mod, writes=c["writes"], confirmed_errors=c["errors"],
                           errors_per_100_writes=round(100 * c["errors"] / c["writes"], 2) if c["writes"] else "",
                           share_episodes_with_error=round(c["with_error"] / c["episodes"], 3),
                           share_wrong=round(c["fausse"] / c["errors"], 3) if c["errors"] else "",
                           share_duplicate=round(c["doublon"] / c["errors"], 3) if c["errors"] else "",
                           share_refused=round(c["refusée"] / c["errors"], 3) if c["errors"] else ""))
        rk = rank[(env, mod)]
        tot = sum(rk.values())
        rows_k.append(dict(environment=env, model=mod, confirmed_errors=tot,
                           on_first_write=rk["first"], on_second_write=rk["second"], later=rk["later"],
                           share_first=round(rk["first"] / tot, 3) if tot else ""))
    write(out, "I_success_and_action_errors", rows_i)
    write(out, "J_error_profile", rows_j)
    write(out, "K_error_position", rows_k)

    rows_l = []
    for (env, mod), tasks in sorted(task.items()):
        n_tasks = len(tasks)
        with_err = {t: c for t, c in tasks.items() if c["with_error"]}
        errs = sorted((c["errors"] for c in tasks.values()), reverse=True)
        total = sum(errs)
        top = max(1, round(0.1 * n_tasks))
        passes = [c["with_error"] / c["episodes"] for c in with_err.values() if c["episodes"] >= 5]
        rows_l.append(dict(environment=env, model=mod, tasks=n_tasks, tasks_with_error=len(with_err),
                           share_errors_top10pct_tasks=round(sum(errs[:top]) / total, 3) if total else "",
                           tasks_with_5plus_passes_and_error=len(passes),
                           mean_share_of_passes_with_error=round(sum(passes) / len(passes), 3) if passes else "",
                           tasks_failing_every_pass=sum(1 for c in with_err.values()
                                                        if c["episodes"] >= 5 and c["with_error"] == c["episodes"])))
    write(out, "L_concentration_by_task", rows_l)
    print(f"{len(parties)} kept episodes on kept tasks; files in {out}")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve())
