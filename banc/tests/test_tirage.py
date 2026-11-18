import json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tirage"))
import tirer as T  # noqa: E402

DOSSIER = Path(T.__file__).parent
GRAINE = int(os.environ.get("GRAINE_TIRAGE") or (DOSSIER / "graine.txt").read_text().strip())


def test_reproductible():
    dev, res = T.tirer(GRAINE)
    assert dev == json.loads((DOSSIER / "developpement.json").read_text())
    assert res == json.loads((DOSSIER / "reserve.json").read_text())


def test_disjoints_et_complets():
    env, wb = T.univers()
    tout = dict(env, WorkBench=sorted(i for v in wb.values() for i in v))
    dev, res = T.tirer(GRAINE)
    for nom, ids in tout.items():
        assert not set(dev[nom]) & set(res[nom])
        assert sorted(dev[nom] + res[nom]) == ids


def test_effectifs():
    env, wb = T.univers()
    dev, _ = T.tirer(GRAINE)
    for nom, ids in env.items():
        assert len(dev[nom]) == -(-len(ids) // 5)
    for f, ids in wb.items():
        assert len([i for i in dev["WorkBench"] if i.split(":")[0] == f]) == -(-len(ids) // 5)
