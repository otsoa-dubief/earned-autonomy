"""Sorties (relecture C13, M7) : RESULTATS.md publie le nombre de tâches porteuses et le motif d'une cellule non
testable (plan, 5.14, point 2) ; la colonne d'intervalle des témoins ne s'appelle plus « verdict »."""
import csv
import json

from rejeu import sorties as SO


def test_resultats_publient_le_motif_non_testable(tmp_path):
    with open(tmp_path / "decision.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["element", "valeur", "detail"])
        w.writeheader()
        w.writerow(dict(element="étiquette finale", valeur="confirmée", detail=""))
    champs = ["eliminatoire", "environnement", "modele", "modele_Y", "mode", "type_suite", "niveau", "statut",
              "exces_100_ecritures", "budget", "lo", "hi", "taches_porteuses", "non_testable"]
    with open(tmp_path / "budget.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=champs)
        w.writeheader()
        w.writerow(dict(eliminatoire="True", environnement="aviation", modele="claude-haiku-5-5", modele_Y="", mode="",
                        type_suite="configuration", niveau="faible", statut="non réfutée", exces_100_ecritures="1.2",
                        budget="0.5", lo="0", hi="3", taches_porteuses="1",
                        non_testable="moins de 2 tâches porteuses"))
    (tmp_path / "meta.json").write_text(json.dumps({"R0": 2, "B": 2, "K": 2}), encoding="utf-8")
    texte = open(SO.ecrire_rapport(str(tmp_path)), encoding="utf-8").read()
    assert "non testable (motif)" in texte and "moins de 2 tâches porteuses" in texte and "tâches porteuses" in texte


def test_parties_exclues_par_configuration(tmp_path):
    """P7 : le bilan du lanceur, repris dans meta.json, compte les parties exclues par configuration et par motif."""
    from rejeu import entrees as EN
    cout = {"parties": [dict(env="WorkBench", modele="claude-haiku-5-5", exclue=True,
                             motif_exclusion="arrêtée sans trace exploitable", ok=False, vague=1),
                        dict(env="WorkBench", modele="claude-haiku-5-5", exclue=True,
                             motif_exclusion="arrêtée sans trace exploitable", ok=False, vague=1),
                        dict(env="aviation", modele="claude-opus-5-5", exclue=False, ok=True, vague=1)]}
    (tmp_path / "cout.json").write_text(json.dumps(cout), encoding="utf-8")
    b = EN.bilan_lanceur([str(tmp_path)])
    assert b["exclues_par_configuration"] == {"WorkBench/claude-haiku-5-5": {"arrêtée sans trace exploitable": 2}}


def test_symetrie_des_deux_moities():
    """P16 : par environnement et par moitié, tâches, retraits, tâches jouées et écritures par niveau ; les deux
    moitiés réunies redonnent les totaux."""
    from rejeu import bout_en_bout as BE
    entrees, cal, conf, _meta = BE.entrees_et_partage_pilote()
    lignes = SO.lignes_symetrie(entrees, cal, conf)
    envs = sorted(set(cal) | set(conf))
    assert [(l["environnement"], l["moitie"]) for l in lignes] == [(e, m) for e in envs
                                                                    for m in ("calibration", "confirmation")]
    for e in envs:
        ls = [l for l in lignes if l["environnement"] == e]
        assert sum(l["taches"] for l in ls) == len(cal.get(e, [])) + len(conf.get(e, []))
        assert all(l["taches_jouees"] <= l["taches"] and l["taches_retirees"] <= l["taches"] for l in ls)
    total = sum(l["ecritures_faible"] + l["ecritures_moyen"] + l["ecritures_fort"] for l in lignes)
    assert 0 < total
