"""Paquets OSF : le dépôt d'antériorité se refait à l'identique ; le dépôt du gel dit qu'il est le préenregistrement."""
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("construire_depot", RACINE / "depots" / "construire_depot.py")
cd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cd)

ANTERIORITE = "e82fb54ff24ddedba990c8d94d2ef23dbbe722f4"
VERSIONNE = RACINE / "depots" / "2026-11-05_anteriorite" / "contenu"


def test_anteriorite_se_refait_a_l_identique(tmp_path):
    dossier = tmp_path / "2026-11-05_anteriorite"
    cd.construire(ANTERIORITE, dossier, "5 November 2026")
    for nom in ("README_DEPOT.md", "MANIFEST_SHA256.txt"):
        assert (dossier / "contenu" / nom).read_text(encoding="utf-8") == (VERSIONNE / nom).read_text(encoding="utf-8")


def test_gel_exige_les_fichiers_du_gel(tmp_path):
    # le commit d'antériorité n'a ni gel/GEL.json ni gel/MANIFESTE_SHA256.txt : pas de paquet de gel possible
    with pytest.raises(SystemExit, match="gel"):
        cd.construire(ANTERIORITE, tmp_path / "2026-11-18_gel", "18 November 2026", type_depot="gel", etiquette="x")


def test_readme_du_gel_est_le_preenregistrement():
    obj = {n: ("tree", "0" * 40) for n in cd.EXCLUS}
    obj["depots"] = ("tree", "1" * 40)
    texte = cd.readme("a" * 40, "b" * 40, obj, "18 November 2026", type_depot="gel", etiquette="gel-2026-11-18",
                      manifeste_sha="c" * 64, g0=123)
    assert "This is the preregistration" in texte
    assert "not the preregistration" not in texte.lower()
    assert "not frozen" not in texte.lower()
    assert "gel-2026-11-18" in texte and "c" * 64 in texte and "123" in texte
    assert "`depots/`" in texte                 # toute entrée du commit hors du paquet est citée par son empreinte


def test_entree_inconnue_refusee():
    with pytest.raises(SystemExit, match="inconnue"):
        cd.verifier_entrees({**{n: ("tree", "0") for n in cd.EXCLUS}, "nouveau": ("tree", "0")}, cd.INCLUS_GEL)


def test_zip_identique_sur_deux_constructions(tmp_path):
    _, _, _, z1, h1 = cd.construire(ANTERIORITE, tmp_path / "a" / "2026-11-05_anteriorite", "5 November 2026")
    _, _, _, z2, h2 = cd.construire(ANTERIORITE, tmp_path / "b" / "2026-11-05_anteriorite", "5 November 2026")
    assert h1 == h2 and cd.sha256(z1) == cd.sha256(z2)


def test_tous_les_fichiers_portent_la_date_du_commit(tmp_path):
    dossier = tmp_path / "2026-11-05_anteriorite"
    cd.construire(ANTERIORITE, dossier, "5 November 2026")
    t = int(subprocess.run(["git", "-C", str(RACINE), "show", "-s", "--format=%ct", ANTERIORITE],
                           capture_output=True, text=True, check=True).stdout)
    dates = {p.relative_to(dossier).as_posix(): int(p.stat().st_mtime) for p in (dossier / "contenu").rglob("*")}
    assert {n: d for n, d in dates.items() if d != t} == {}


def test_zip_independant_du_fuseau(tmp_path, monkeypatch):
    import time
    hs = []
    for i, tz in enumerate(("Asia/Tokyo", "America/New_York")):
        monkeypatch.setenv("TZ", tz)
        time.tzset()
        hs.append(cd.construire(ANTERIORITE, tmp_path / str(i) / "2026-11-05_anteriorite", "5 November 2026")[4])
    monkeypatch.delenv("TZ")
    time.tzset()
    assert hs[0] == hs[1]
