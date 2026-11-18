"""Retraits du motif a montrés à Otsoa (relecture/retraits_motif_a.py ; plan 4.5 ; relecture C13, P9)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "relecture"))
import decisions  # noqa: E402
import retraits_motif_a as RM  # noqa: E402


def _vague(tmp_path):
    alertes = [dict(id="commerce-aaa", environnement="commerce", tache="7", partie="p1", rang=3, modele="claude-opus-5-5"),
               dict(id="commerce-bbb", environnement="commerce", tache="7", partie="p2", rang=1, modele="claude-haiku-5-5"),
               dict(id="aviation-ccc", environnement="aviation", tache="12", partie="p3", rang=2, modele="claude-opus-5-5")]
    (tmp_path / "alertes.json").write_text(json.dumps(alertes), encoding="utf-8")
    decisions.ecrire_modele(tmp_path / "decisions.csv")
    with open(tmp_path / "decisions.csv", "a", encoding="utf-8") as f:
        f.write('commerce-aaa,levée,a,vol introuvable,"a2 : le vol XY12 n\'existe pas dans la base"\n')
        f.write("commerce-bbb,confirmée,,mauvais montant,\n")
        f.write("aviation-ccc,levée,b,reformulation,champ libre reformulé\n")
    return f"{tmp_path / 'decisions.csv'},{tmp_path / 'alertes.json'}"


def test_liste_des_retraits_sans_modele(tmp_path):
    sortie = tmp_path / "sortie"
    assert RM.main(["--vague", _vague(tmp_path), "--sortie", str(sortie)]) == 0
    liste = json.loads((sortie / "retraits_motif_a.json").read_text(encoding="utf-8"))
    assert [(t["environnement"], t["tache"]) for t in liste] == [("commerce", "7")]
    assert liste[0]["alertes"][0]["cas"] == "a2" and "XY12" in liste[0]["alertes"][0]["preuve"]
    texte = (sortie / "retraits_motif_a.md").read_text(encoding="utf-8") + json.dumps(liste)
    assert "claude" not in texte.lower() and "modele" not in texte
    assert json.loads((sortie / "oppositions_motif_a.json").read_text(encoding="utf-8")) == []


def test_oppositions_existantes_jamais_ecrasees(tmp_path):
    sortie = tmp_path / "sortie"
    sortie.mkdir()
    (sortie / "oppositions_motif_a.json").write_text('[["commerce", "7"]]', encoding="utf-8")
    RM.main(["--vague", _vague(tmp_path), "--sortie", str(sortie)])
    assert json.loads((sortie / "oppositions_motif_a.json").read_text(encoding="utf-8")) == [["commerce", "7"]]
