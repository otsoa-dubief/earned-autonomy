"""Rejeu final, mode réel : contrôles avant tout calcul (relecture C13, P1 et P3 ; plan 3.4, 5.2 et 5.14).

- le dépôt est conforme au manifeste du gel du plan (`gel/manifeste.py`) ;
- le manifeste des verdicts est celui du tirage (son SHA-256 est `empreinte_manifeste` de `partage.json`) ;
- toute entrée lue (dossiers de vague, bilans de relecture, tâches retirées) y figure avec la même empreinte ;
- la réussite des tâches est déjà calculée (elle est inscrite au manifeste avant le tirage) ;
- le dossier de sortie est vide ; chaque lancement est noté au journal du rejeu final.
"""
import hashlib
import json
import os

import pytest

from rejeu import bout_en_bout as BE
from rejeu import entrees as EN


def _experience(tmp_path, reussite=True):
    racine = tmp_path / "experience"
    v = racine / "vague1"
    v.mkdir(parents=True)
    for nom in ("actions_typees.csv", "cout.json") + (("reussite.csv",) if reussite else ()):
        (v / nom).write_text("x\n", encoding="utf-8")
    rel = racine / "relecture1"
    rel.mkdir()
    (rel / "decisions.csv").write_text("alerte,decision\n", encoding="utf-8")
    mv = BE._module_manifeste_verdicts()
    manifeste = racine / "manifeste_verdicts.txt"
    mv.ecrire(racine, [v, rel], manifeste)
    partage = tmp_path / "partage.json"
    partage.write_text(json.dumps({"empreinte_manifeste": mv.sha256(manifeste)}), encoding="utf-8")
    vague = EN.VagueRelecture("1", str(rel / "decisions.csv"))
    return racine, str(v), str(partage), vague, str(manifeste)


@pytest.fixture
def gel_conforme(monkeypatch):
    class Gel:
        @staticmethod
        def verifier(racine):
            return []
    monkeypatch.setattr(BE, "_module_gel", lambda: Gel)


def test_entrees_conformes(tmp_path, gel_conforme):
    racine, d, partage, vague, manifeste = _experience(tmp_path)
    assert BE.controles_experience([d], partage, [vague], None, str(tmp_path / "sortie"), manifeste) == []


def test_depot_different_du_gel_du_plan(tmp_path, monkeypatch):
    racine, d, partage, vague, manifeste = _experience(tmp_path)

    class Gel:
        @staticmethod
        def verifier(r):
            return ["simulation/rejeu/decision.py : empreinte différente"]
    monkeypatch.setattr(BE, "_module_gel", lambda: Gel)
    refus = BE.controles_experience([d], partage, [vague], None, str(tmp_path / "s"), manifeste)
    assert any("gel du plan" in r for r in refus)


def test_manifeste_qui_n_est_pas_celui_du_tirage(tmp_path, gel_conforme):
    racine, d, partage, vague, manifeste = _experience(tmp_path)
    with open(partage, "w", encoding="utf-8") as f:
        json.dump({"empreinte_manifeste": hashlib.sha256(b"autre").hexdigest()}, f)
    refus = BE.controles_experience([d], partage, [vague], None, str(tmp_path / "s"), manifeste)
    assert any("n'est pas celui du tirage" in r for r in refus)


def test_entree_modifiee_ou_hors_du_manifeste(tmp_path, gel_conforme):
    racine, d, partage, vague, manifeste = _experience(tmp_path)
    with open(os.path.join(d, "actions_typees.csv"), "w", encoding="utf-8") as f:
        f.write("retouche\n")
    retirees = tmp_path / "experience" / "retirees.json"
    retirees.write_text("[]", encoding="utf-8")
    refus = " | ".join(BE.controles_experience([d], partage, [vague], str(retirees), str(tmp_path / "s"), manifeste))
    assert "vague1/actions_typees.csv diffère" in refus and "retirees.json absent du manifeste" in refus


def test_reussite_manquante_et_sortie_non_vide(tmp_path, gel_conforme):
    racine, d, partage, vague, manifeste = _experience(tmp_path, reussite=False)
    sortie = tmp_path / "sortie"
    sortie.mkdir()
    (sortie / "ancien.csv").write_text("x", encoding="utf-8")
    refus = " | ".join(BE.controles_experience([d], partage, [vague], None, str(sortie), manifeste))
    assert "reussite.csv" in refus and "n'est pas vide" in refus


def test_journal_du_rejeu_final(tmp_path):
    sortie = tmp_path / "rejeu" / "sortie"
    BE.noter_lancement(str(sortie), dict(etape="début", entrees={"a": "b"}))
    BE.noter_lancement(str(sortie), dict(etape="fin", code=0))
    lignes = (tmp_path / "rejeu" / "journal_rejeu_final.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(l)["etape"] for l in lignes] == ["début", "fin"] and all("heure" in json.loads(l)
                                                                                 for l in lignes)


def test_ligne_de_commande_exige_le_manifeste_des_verdicts(tmp_path, capsys):
    with pytest.raises(SystemExit) as e:
        BE.main(["--experience", "--dossier", str(tmp_path), "--partage", str(tmp_path / "p.json"),
                 "--vague", "1=d.csv,,", "--sortie", str(tmp_path / "hors")])
    assert e.value.code == 2 and "--manifeste-verdicts" in capsys.readouterr().err


def test_oppositions_inscrites_au_manifeste(tmp_path, gel_conforme):
    """Relecture C13, P9 : le fichier des oppositions d'Otsoa est une entrée gelée comme les autres."""
    racine, d, partage, vague, manifeste = _experience(tmp_path)
    opp = tmp_path / "experience" / "oppositions_motif_a.json"
    opp.write_text("[]", encoding="utf-8")
    refus = BE.controles_experience([d], partage, [vague], None, str(tmp_path / "s"), manifeste, str(opp))
    assert any("oppositions_motif_a.json absent du manifeste" in r for r in refus)
