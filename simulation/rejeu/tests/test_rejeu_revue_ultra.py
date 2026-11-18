"""Revue de code « ultra » du 06/11, lot moteur (copie `autonomie-meritee-revue-moteur`) : un test par constat retenu.

2. `--experience` et `--essai-a-blanc` sans `--sortie` écrivaient dans `sorties_pilote/`, suivi par git et figé ;
3. `--R0`, `--B` et `--K` remplaçaient les valeurs figées sans contrôle (avec `--B 0`, le point 1 ne testait rien) ;
4. un essai à blanc (ou le bout en bout du pilote) lancé après `--tirer-g0` prenait le vrai G0 ;
5. `ecrire_config` remettait G0 à null : G0 pouvait être tirée deux fois ;
6. RESULTATS.md citait `resultats_couverture/` au lieu de la simulation d'où vient la méthode ;
7. `facteur_relance` et `relances` restaient, alors que la relance ne s'applique plus (Q13).
Le constat 1 (gel) est testé dans `gel/tests/test_manifeste.py` ; le 9 (fusion des tâches retirées en double) est
couvert par les tests des entrées ; le 8 n'est pas retenu (voir `simulation/controle3/RAPPORT.md`, section 8).
"""
import dataclasses
import json
import os
import types

import pytest

from rejeu import analyse as AN
from rejeu import bout_en_bout as BE
from rejeu import config_rejeu as CR
from rejeu import pipeline as PL
from rejeu import sorties as SO


def _g0_tiree(monkeypatch, g0=123456789):
    """Configuration du dépôt, comme après `gel/manifeste.py --tirer-g0`."""
    cfg = dataclasses.replace(CR.charger_config(), G0=g0)
    monkeypatch.setattr(BE.CR, "charger_config", lambda *a, **k: cfg)
    return cfg


# 2. --sortie obligatoire hors du bout en bout du pilote ----------------------------------------------------------
@pytest.mark.parametrize("mode", [["--experience", "--dossier", "v1", "--partage", "p.json", "--vague", "1=d.csv,,"],
                                  ["--essai-a-blanc"]])
def test_sortie_obligatoire_pour_experience_et_essai(mode, monkeypatch):
    monkeypatch.setattr(BE, "executer_experience", lambda *a, **k: pytest.fail("ne doit pas être appelé"))
    with pytest.raises(SystemExit) as e:
        BE.main(mode)
    assert e.value.code == 2


def test_experience_refuse_une_sortie_dans_le_perimetre_fige(monkeypatch):
    monkeypatch.setattr(BE, "executer_experience", lambda *a, **k: pytest.fail("ne doit pas être appelé"))
    for sortie in (BE.SORTIE_PILOTE, os.path.join(BE.ICI, "sorties_experience")):
        with pytest.raises(SystemExit) as e:
            BE.main(["--experience", "--dossier", "v1", "--partage", "p.json", "--vague", "1=d.csv,,",
                     "--sortie", sortie])
        assert e.value.code == 2


def test_experience_hors_perimetre_passe_la_sortie(monkeypatch, tmp_path):
    vu = {}

    def faux(dossier, partage, vagues, sortie, *a, **k):
        vu["sortie"] = sortie
        return dict(etiquette="test")
    monkeypatch.setattr(BE, "executer_experience", faux)
    assert BE.main(["--experience", "--dossier", "v1", "--partage", "p.json", "--vague", "1=d.csv,,",
                    "--manifeste-verdicts", "m.txt", "--sortie", str(tmp_path / "sortie")]) == 0
    assert vu["sortie"] == str(tmp_path / "sortie")


# 3. R0, B et K : entiers positifs ; figés pour l'expérience réelle ---------------------------------------------------
@pytest.mark.parametrize("option", ["--R0", "--B", "--K"])
def test_r0_b_k_nuls_refuses(option, monkeypatch, tmp_path):
    monkeypatch.setattr(BE, "executer_experience", lambda *a, **k: pytest.fail("ne doit pas être appelé"))
    with pytest.raises(SystemExit) as e:
        BE.main(["--essai-a-blanc", "--sortie", str(tmp_path), option, "0"])
    assert e.value.code == 2


def test_experience_reelle_refuse_de_changer_les_valeurs_figees(monkeypatch, tmp_path):
    cfg = _g0_tiree(monkeypatch)
    for k in (dict(R0=cfg.R0 + 1), dict(B=4), dict(K=cfg.K + 1)):
        with pytest.raises(SystemExit, match="figé"):
            BE.executer_experience("v1", "p.json", [], str(tmp_path), essai=False, **k)


# 4. la graine de développement pour tout ce qui n'est pas l'expérience réelle ------------------------------------
def _capturer_reglages(monkeypatch):
    vu = {}
    monkeypatch.setattr(BE, "partage_par_env", lambda p: ({}, {}))
    monkeypatch.setattr(BE, "preparer_reussite", lambda ds: [])
    monkeypatch.setattr(BE.EN, "charger_entrees", lambda *a, **k: types.SimpleNamespace(taches_retirees={}))
    monkeypatch.setattr(BE.EN, "bilan_lanceur", lambda ds: {})
    monkeypatch.setattr(BE, "meta_bilans", lambda v: [])
    monkeypatch.setattr(BE.SO, "sha256_fichier", lambda c: "0")

    def executer(entrees, cal, conf, reg, sortie, *a, **k):
        vu["reg"] = reg
        return dict(etiquette="test")
    monkeypatch.setattr(BE, "executer", executer)
    return vu


def test_essai_a_blanc_garde_la_graine_de_developpement_apres_le_tirage(monkeypatch, tmp_path):
    cfg = _g0_tiree(monkeypatch)
    vu = _capturer_reglages(monkeypatch)
    part = tmp_path / "p.json"
    part.write_text("{}", encoding="utf-8")
    BE.executer_experience(str(tmp_path), str(part), [], str(tmp_path / "s"), essai=True, R0=2, B=2, K=2)
    assert vu["reg"].G0 == cfg.G0_developpement != cfg.G0


def test_experience_reelle_prend_g0(monkeypatch, tmp_path):
    cfg = _g0_tiree(monkeypatch)
    vu = _capturer_reglages(monkeypatch)
    part = tmp_path / "p.json"
    part.write_text("{}", encoding="utf-8")
    manifeste = tmp_path / "manifeste_verdicts.txt"
    manifeste.write_text("", encoding="utf-8")
    # contrôles du mode réel (relecture C13, P1 et P3) : testés à part (test_rejeu_gel_verdicts.py)
    monkeypatch.setattr(BE, "controles_experience", lambda *a, **k: [])
    monkeypatch.setattr(BE, "noter_lancement", lambda *a, **k: None)

    class MV:
        @staticmethod
        def gel_plan_courant():
            return {}
    monkeypatch.setattr(BE, "_module_manifeste_verdicts", lambda: MV)
    BE.executer_experience(str(tmp_path), str(part), [], str(tmp_path / "s"), essai=False,
                           manifeste_verdicts=str(manifeste))
    assert vu["reg"].G0 == cfg.G0 and (vu["reg"].R0, vu["reg"].B, vu["reg"].K) == (cfg.R0, cfg.B, cfg.K)
    with pytest.raises(SystemExit):        # sans manifeste des verdicts, le rejeu réel ne part pas
        BE.executer_experience(str(tmp_path), str(part), [], str(tmp_path / "s"), essai=False)


def test_bout_en_bout_du_pilote_garde_la_graine_de_developpement(monkeypatch, tmp_path):
    cfg = _g0_tiree(monkeypatch)
    vu = _capturer_reglages(monkeypatch)
    monkeypatch.setattr(BE, "entrees_et_partage_pilote", lambda: (None, {}, {}, {}))
    BE.main(["--pilote", "--sortie", str(tmp_path), "--R0", "2", "--B", "2", "--K", "2"])
    assert vu["reg"].G0 == cfg.G0_developpement != cfg.G0


# 5. réécrire la configuration garde une G0 déjà tirée -------------------------------------------------------------
def test_ecrire_config_garde_g0_tiree(tmp_path):
    chemin = tmp_path / "config_rejeu.json"
    CR.ecrire_config(str(chemin))
    assert json.loads(chemin.read_text(encoding="utf-8"))["graines"]["G0"] is None
    brut = json.loads(chemin.read_text(encoding="utf-8"))
    brut["graines"]["G0"] = 987654321
    chemin.write_text(json.dumps(brut), encoding="utf-8")
    CR.ecrire_config(str(chemin))
    assert json.loads(chemin.read_text(encoding="utf-8"))["graines"]["G0"] == 987654321


# 6. RESULTATS.md cite la simulation d'où vient la méthode -----------------------------------------------------------
def test_resultats_cite_la_source_de_la_methode(tmp_path):
    meta = dict(ecrit_le="2026-11-06", R0=2, B=2, K=2,
                methode_intervalle=dict(nom="jackknife-t", source="simulation/rejeu/resultats_couverture_charge"))
    (tmp_path / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    texte = open(SO.ecrire_rapport(str(tmp_path)), encoding="utf-8").read()
    assert "`simulation/rejeu/resultats_couverture_charge/`" in texte
    assert "`simulation/rejeu/resultats_couverture/`" not in texte


# 7. plus de trace de la relance -----------------------------------------------------------------------------------
def test_plus_de_relance():
    assert "facteur_relance" not in {f.name for f in dataclasses.fields(AN.Reglages)}
    assert "relances" not in {f.name for f in dataclasses.fields(PL.Analyse)}
    assert "facteur_relance" not in CR.calculer()
    assert "facteur_relance" not in json.loads(open(CR.CHEMIN_CONFIG, encoding="utf-8").read())
