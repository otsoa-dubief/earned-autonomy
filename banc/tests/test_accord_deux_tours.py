"""Second tour de la relecture à l'aveugle et décisions retenues (banc/relecture/accord.py ; décision B2 du 05/11)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "relecture"))
import accord  # noqa: E402


def tirage(prefixe, n=15, levees=10):
    return {"fiches": [{"numero": k, "alerte_id": f"{prefixe}{k}",
                        "decision_claude": "levée" if k <= levees else "confirmée",
                        "motif_claude": "c" if k <= levees else "", "enjeu": "faible"}
                       for k in range(1, n + 1)]}


def reponses(t, desaccords=()):
    rep = {}
    for f in t["fiches"]:
        claude = f["decision_claude"]
        autre = "confirmée" if claude == "levée" else "levée"
        rep[f["numero"]] = (autre if f["numero"] in desaccords else claude, "")
    return rep


def test_un_tour_garde():
    t = tirage("a")
    b = accord.conclure([(t, reponses(t, [1, 2]))])
    assert b["conclusion"] == accord.GARDEE and not b["desaccord_persistant"]
    assert len(b["decisions_otsoa"]) == 15


def test_second_tour_garde_a_26_sur_30():
    t1, t2 = tirage("a"), tirage("b")
    b = accord.conclure([(t1, reponses(t1, [1, 2, 3])), (t2, reponses(t2, [4]))])
    assert (b["accords"], b["total"], b["seuil"]) == (26, 30, 26)
    assert b["conclusion"] == accord.GARDEE_SECOND_TOUR and not b["desaccord_persistant"]


def test_desaccord_persistant_a_25_sur_30():
    t1, t2 = tirage("a"), tirage("b")
    b = accord.conclure([(t1, reponses(t1, [1, 2, 3])), (t2, reponses(t2, [4, 5]))])
    assert b["accords"] == 25
    assert b["conclusion"] == accord.PERSISTANT and b["desaccord_persistant"]


def test_second_tour_inutile_refuse():
    t1, t2 = tirage("a"), tirage("b")
    with pytest.raises(accord.ReponsesInvalides, match="second tour inutile"):
        accord.conclure([(t1, reponses(t1)), (t2, reponses(t2))])


def test_meme_alerte_dans_les_deux_tours_refusee():
    t1 = tirage("a")
    with pytest.raises(accord.ReponsesInvalides, match="deux tours"):
        accord.conclure([(t1, reponses(t1, [1, 2, 3])), (t1, reponses(t1))])


def test_seuil_cumule_au_prorata():
    t1, t2 = tirage("a", n=10, levees=7), tirage("b", n=10, levees=7)
    b = accord.conclure([(t1, reponses(t1, [1, 2, 3])), (t2, reponses(t2))])
    assert b["seuil"] == 18 and b["accords"] == 17 and b["desaccord_persistant"]


def test_decisions_d_otsoa_l_emportent():
    registre = {"a1": {"decision": "levée"}, "a2": {"decision": "confirmée"}, "x9": {"decision": "levée"}}
    retenues = accord.decisions_retenues(registre, {"a1": "confirmée"})
    assert retenues == {"a1": "confirmée", "a2": "confirmée", "x9": "levée"}
    with pytest.raises(accord.ReponsesInvalides):
        accord.decisions_retenues(registre, {"inconnue": "levée"})


def _ecrire(tmp_path, nom, t, rep):
    (tmp_path / f"{nom}.json").write_text(json.dumps(t), encoding="utf-8")
    lignes = ["fiche,reponse,motif"] + [f"{k},{'fausse alerte' if d == 'levée' else 'vraie erreur'}," for k, (d, _) in rep.items()]
    (tmp_path / f"{nom}.csv").write_text("\n".join(lignes) + "\n", encoding="utf-8")


def test_ligne_de_commande_deux_tours(tmp_path, capsys):
    t1, t2 = tirage("a"), tirage("b")
    _ecrire(tmp_path, "t1", t1, reponses(t1, [1, 2, 3]))
    _ecrire(tmp_path, "t2", t2, reponses(t2, [4, 5]))
    code = accord.main(["--tirage", str(tmp_path / "t1.json"), "--reponses", str(tmp_path / "t1.csv"),
                        "--tirage", str(tmp_path / "t2.json"), "--reponses", str(tmp_path / "t2.csv"),
                        "--sortie", str(tmp_path / "accord.json")])
    assert code == 0
    assert "Désaccord persistant" in capsys.readouterr().out
    bilan = json.loads((tmp_path / "accord.json").read_text(encoding="utf-8"))
    assert bilan["desaccord_persistant"] and len(bilan["decisions_otsoa"]) == 30


def test_ligne_de_commande_refuse_un_nombre_inegal(tmp_path):
    t1 = tirage("a")
    _ecrire(tmp_path, "t1", t1, reponses(t1))
    assert accord.main(["--tirage", str(tmp_path / "t1.json"), "--tirage", str(tmp_path / "t1.json"),
                        "--reponses", str(tmp_path / "t1.csv")]) == 2
