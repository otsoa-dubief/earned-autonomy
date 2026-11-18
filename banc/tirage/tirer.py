"""Tirage des taches de developpement (20 %, arrondi au superieur). Usage : tirer.py <graine> [sortie]"""
import json, math, random, sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "banc"))
from verdicts import charger_taches_workbench  # noqa: E402

TAU = {"aviation": "airline", "commerce": "retail", "banque": "banking_knowledge"}


def univers():
    """{environnement: [ids tries]} ; WorkBench : {fichier: [ids]} a part."""
    ext = RACINE / "externe"
    env = {}
    for nom, dom in TAU.items():
        chemin = ext / "tau2-bench/data/tau2/domains" / dom / "tasks.json"
        env[nom] = sorted(str(t["id"]) for t in json.loads(chemin.read_text()))
    wb = {}
    for ident in charger_taches_workbench(ext / "WorkBench"):
        wb.setdefault(ident.split(":")[0], []).append(ident)
    return env, {k: sorted(v) for k, v in sorted(wb.items())}


def effectif(n):
    return math.ceil(n * 20 / 100)


def tirer(graine):
    env, wb = univers()
    rng = random.Random(graine)
    dev, res = {}, {}
    for nom, ids in env.items():
        d = sorted(rng.sample(ids, effectif(len(ids))))
        dev[nom], res[nom] = d, [i for i in ids if i not in set(d)]
    dw, rw = [], []
    for f, ids in wb.items():
        d = sorted(rng.sample(ids, effectif(len(ids))))
        dw += d
        rw += [i for i in ids if i not in set(d)]
    dev["WorkBench"], res["WorkBench"] = sorted(dw), sorted(rw)
    return dev, res


if __name__ == "__main__":
    graine = int(sys.argv[1])
    sortie = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent
    dev, res = tirer(graine)
    (sortie / "developpement.json").write_text(json.dumps(dev, indent=1, ensure_ascii=False))
    (sortie / "reserve.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
