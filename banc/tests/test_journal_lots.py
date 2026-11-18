"""Lots de la relecture des alertes (relecture/journal_lots.py ; plan 4.4 ; relecture C13, P11)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "relecture"))
import journal_lots as JL  # noqa: E402


def _fichiers(tmp_path):
    invite = tmp_path / "invite.md"
    invite.write_text("Relis ces fiches selon la consigne.", encoding="utf-8")
    sortie = tmp_path / "lot1.csv"
    sortie.write_text("alerte_id,decision\nA,confirmée\nB,confirmée\n", encoding="utf-8")
    return invite, sortie


def test_un_lot_relu_une_fois(tmp_path):
    rel = tmp_path / "relecture"
    invite, sortie = _fichiers(tmp_path)
    JL.ouvrir(rel, 1, ["A", "B"], invite)
    with pytest.raises(JL.LotInvalide, match="déjà ouvert"):
        JL.ouvrir(rel, 1, ["A", "B"], invite)
    JL.fermer(rel, 1, sortie)
    with pytest.raises(JL.LotInvalide, match="déjà fermé"):
        JL.fermer(rel, 1, sortie)
    JL.fermer(rel, 1, sortie, relance="sortie mal formée : colonne manquante")
    lignes = [json.loads(l) for l in (rel / "journal_relecture.jsonl").read_text().splitlines()]
    assert [l["etape"] for l in lignes] == ["ouverture", "fermeture", "relance"]
    assert len(lignes[0]["invite_sha256"]) == 64 and lignes[2]["raison"].startswith("sortie mal formée")


def test_une_alerte_dans_un_seul_lot_et_verification(tmp_path):
    rel = tmp_path / "relecture"
    invite, sortie = _fichiers(tmp_path)
    JL.ouvrir(rel, 1, ["A", "B"], invite)
    with pytest.raises(JL.LotInvalide, match="déjà dans le lot 1"):
        JL.ouvrir(rel, 2, ["B", "C"], invite)
    assert any("non fermé" in e for e in JL.verifier(rel, ["A", "B"]))
    JL.fermer(rel, 1, sortie)
    assert JL.verifier(rel, ["A", "B"]) == []
    assert any("C" in e for e in JL.verifier(rel, ["A", "B", "C"]))
