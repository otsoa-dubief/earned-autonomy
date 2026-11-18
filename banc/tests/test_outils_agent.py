"""Les définitions d'outils figées (banc/outils_agent/) : empreinte cohérente, commits épinglés, couverture du pilote."""
import csv
import json
import sys
from pathlib import Path

import pytest

import outils_agent as oa
import verdicts as v

ENVS = ("aviation", "commerce", "banque", "workbench")
PILOTE = Path(__file__).resolve().parents[2] / "pilote" / "etape2" / "2026-11-05_07-50-58" / "actions.csv"


def charger(env):
    return json.loads((oa.DOSSIER / f"{env}.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("env", ENVS)
def test_empreinte_correspond_au_contenu(env):
    d = charger(env)
    assert d["empreinte_sha256"] == oa.empreinte(d["outils"])
    assert d["nombre_outils"] == len(d["outils"]) > 0


@pytest.mark.parametrize("env", ENVS)
def test_commit_epingle(env):
    attendu = "49c7dfd" if env == "workbench" else v.COMMIT_TAU2
    assert charger(env)["commit"] == attendu


def test_empreinte_ne_depend_pas_de_l_ordre_des_cles():
    assert oa.empreinte([{"a": 1, "b": 2}]) == oa.empreinte([{"b": 2, "a": 1}])
    assert oa.empreinte([{"a": 1}]) != oa.empreinte([{"a": 2}])


@pytest.mark.skipif(not PILOTE.is_file(), reason="pilote absent")
def test_les_outils_appeles_au_pilote_sont_dans_les_definitions_figees():
    """Sauf les outils bancaires « découvrables », révélés pendant la partie par unlock_discoverable_agent_tool."""
    csv.field_size_limit(sys.maxsize)
    noms = {env: {o["function"]["name"] for o in charger(env)["outils"]} for env in ENVS}
    env_de = {"airline": "aviation", "retail": "commerce", "banking_knowledge": "banque"}
    absents = set()
    with open(PILOTE, newline="", encoding="utf-8") as fh:
        for l in csv.DictReader(fh):
            env = "workbench" if l["banc"] == "workbench" else env_de[l["domaine"]]
            nom = l["outil"].replace(".", "_") if env == "workbench" else l["outil"]
            if nom not in noms[env]:
                absents.add((env, l["outil"]))
    decouvrables = {(e, n) for e, n in absents if e == "banque" and n.rsplit("_", 1)[-1].isdigit()}
    assert absents == decouvrables
