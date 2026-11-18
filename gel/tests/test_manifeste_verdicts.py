"""Manifeste du gel des verdicts (gel/manifeste_verdicts.py ; plan 3.4, point 3, et 5.2 ; relecture C13, P1)."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

RACINE_DEPOT = Path(__file__).resolve().parents[2]


def _module():
    spec = importlib.util.spec_from_file_location("manifeste_verdicts", RACINE_DEPOT / "gel" / "manifeste_verdicts.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _experience(tmp_path):
    """Une expérience fictive : deux vagues, un bilan de relecture hors des vagues, l'audit et les retraits."""
    racine = tmp_path / "experience"
    for v in ("vague1", "vague2"):
        (racine / v / "parties" / "p1").mkdir(parents=True)
        (racine / v / "actions_typees.csv").write_text(f"partie,rang\n{v},1\n", encoding="utf-8")
        (racine / v / "parties" / "p1" / "trace.json").write_text("{}", encoding="utf-8")
    (racine / "relecture1").mkdir()
    (racine / "relecture1" / "decisions.csv").write_text("alerte,decision\n", encoding="utf-8")
    (racine / "audit").mkdir()
    (racine / "audit" / "taches_retirees_audit.json").write_text("[]", encoding="utf-8")
    return racine


def test_ecrire_lire_et_verifier(tmp_path):
    MV = _module()
    racine = _experience(tmp_path)
    sortie = racine / "manifeste_verdicts.txt"
    empreinte = MV.ecrire(racine, [racine / "vague1", racine / "vague2", racine / "relecture1", racine / "audit"],
                          sortie, gel_plan={"commit": "abc", "etiquette": "gel-2026-11-18", "manifeste_gel": "0" * 64})
    assert empreinte == hashlib.sha256(sortie.read_bytes()).hexdigest()
    lu = MV.lire(sortie)
    assert "vague1/parties/p1/trace.json" in lu and "relecture1/decisions.csv" in lu and "gel_plan.json" in lu
    lignes = sortie.read_text(encoding="utf-8").splitlines()
    assert lignes == sorted(lignes) and all(len(l.split("  ")[0]) == 64 for l in lignes)
    assert json.loads((racine / "gel_plan.json").read_text(encoding="utf-8"))["etiquette"] == "gel-2026-11-18"
    lus = [racine / "vague1", racine / "vague2", racine / "relecture1" / "decisions.csv"]
    assert MV.ecarts(sortie, lus) == []


def test_ecarts_fichier_modifie_ajoute_ou_retire(tmp_path):
    MV = _module()
    racine = _experience(tmp_path)
    sortie = racine / "manifeste_verdicts.txt"
    MV.ecrire(racine, [racine / "vague1", racine / "relecture1"], sortie)
    (racine / "vague1" / "actions_typees.csv").write_text("partie,rang\nautre,1\n", encoding="utf-8")
    (racine / "vague1" / "ajout.csv").write_text("x\n", encoding="utf-8")
    (racine / "vague1" / "parties" / "p1" / "trace.json").unlink()
    ec = " | ".join(MV.ecarts(sortie, [racine / "vague1"]))
    assert "vague1/actions_typees.csv diffère" in ec
    assert "vague1/ajout.csv absent du manifeste" in ec
    assert "vague1/parties/p1/trace.json manque" in ec


def test_entree_hors_du_manifeste_ou_hors_de_la_racine(tmp_path):
    MV = _module()
    racine = _experience(tmp_path)
    sortie = racine / "manifeste_verdicts.txt"
    MV.ecrire(racine, [racine / "vague1"], sortie)
    autre = tmp_path / "ailleurs.json"
    autre.write_text("[]", encoding="utf-8")
    ec = " | ".join(MV.ecarts(sortie, [racine / "audit" / "taches_retirees_audit.json", autre]))
    assert "audit/taches_retirees_audit.json absent du manifeste" in ec and "hors de la racine" in ec
    with pytest.raises(ValueError):
        MV.ecrire(racine, [autre], racine / "m2.txt")


def test_refuse_donnees_et_ecrasement(tmp_path):
    MV = _module()
    racine = _experience(tmp_path)
    (racine / "donnees").mkdir()
    (racine / "donnees" / "scelle.md").write_text("x", encoding="utf-8")
    with pytest.raises(ValueError):
        MV.ecrire(racine, [racine / "donnees"], racine / "m.txt")
    sortie = racine / "manifeste_verdicts.txt"
    MV.ecrire(racine, [racine / "vague1"], sortie)
    with pytest.raises(FileExistsError):
        MV.ecrire(racine, [racine / "vague1"], sortie)
