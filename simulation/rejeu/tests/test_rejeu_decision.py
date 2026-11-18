"""Rejeu, phase 2 : règle de décision (PLAN_EXPERIENCE.md, 5.14), désaccord persistant (B2), règle de choix
réappliquée (1.3, point 4), hasard (Q7), alerte des tests de résistance (5.11).
"""
import json
import os

import pytest

from rejeu import analyse as AN
from rejeu import bout_en_bout as BE
from rejeu import decision as DE
from rejeu import entrees as EN
from rejeu import essais as ES
from rejeu import preuves as PR


def test_ordre_des_etiquettes():
    assert DE.ORDRE_ETIQUETTES == ("R5", "R1", "preuves insuffisantes", "R4", "R2", "confirmée")
    assert DE.moins_favorable("confirmée", "R2") == "R2"
    assert DE.moins_favorable("R4", "R1") == "R1"
    assert DE.moins_favorable("R2", "R5", "confirmée") == "R5"
    oui, non = dict(tenu=True), dict(tenu=False)
    r4 = dict(tenu=False, jugeable=True, etablie=True)   # amendement du 07/11 : dépassement établi partout où l'on juge
    assert DE.etiquette(non, non, non, non) == "R5"
    assert DE.etiquette(oui, non, non, non) == "R1"
    assert DE.etiquette(oui, oui, non, r4) == "R4"       # R4 avant R2, même si les témoins sont battus
    assert DE.etiquette(oui, oui, oui, r4) == "R4"
    assert DE.etiquette(oui, oui, non, oui) == "R2"
    assert DE.etiquette(oui, oui, oui, oui) == "confirmée"
    # garde-fou de R4 (N1, 06/11 ; amendement du 07/11) : sans dépassement établi dans chaque configuration jugeable,
    # l'absence de configuration délégable ne prouve rien contre les agents : « preuves insuffisantes »
    sans_volume = dict(tenu=False, jugeable=False, etablie=False)
    assert DE.etiquette(oui, oui, oui, sans_volume) == DE.PREUVES_INSUFFISANTES == "preuves insuffisantes"
    assert DE.etiquette(oui, non, oui, sans_volume) == "R1"          # un dépassement établi l'emporte
    assert DE.etiquette(oui, oui, oui, dict(tenu=False, jugeable=True, etablie=False)) == "preuves insuffisantes"
    assert DE.etiquette(oui, oui, oui, non) == "preuves insuffisantes"   # sans établissement connu, pas de R4
    assert DE.moins_favorable("preuves insuffisantes", "R4") == "preuves insuffisantes"
    assert DE.moins_favorable("preuves insuffisantes", "R1") == "R1"


def test_regle_de_choix():
    noms = ("B-tout", "B-régulier", "A½", "A¼")
    e = lambda tient, charge, marge: dict(tient=tient, charge=charge, marge=marge)  # noqa: E731
    etat = {"B-tout": e(True, 70.0, 0.9), "B-régulier": e(True, 60.0, 0.5), "A½": e(False, 50.0, 0.1),
            "A¼": e(True, 65.0, 0.95)}
    r = DE.choisir_regle(etat, noms)
    assert r["retenue"] == "B-régulier" and r["survivantes"] == ["B-tout", "B-régulier", "A¼"]
    etat["B-tout"]["charge"] = 60.5                       # moins d'un point d'écart : la plus prudente
    assert DE.choisir_regle(etat, noms)["retenue"] == "B-tout"
    etat["B-régulier"]["marge"] = 0.9                     # égalité de prudence : la plus simple
    assert DE.choisir_regle(etat, noms)["retenue"] == "B-tout"
    for v in etat.values():
        v["tient"] = False
    assert DE.choisir_regle(etat, noms)["retenue"] is None


def test_hasard_et_alerte_de_resistance():
    n = lambda lo, hi: dict(diff=0, lo=lo, hi=hi)  # noqa: E731
    assert DE.conclusion_hasard({"faible": n(-2, -1), "moyen": n(-1, 1)}, False) == "méritée"
    assert DE.conclusion_hasard({"faible": n(-2, -1), "moyen": n(0.1, 1)}, False) == "répartie"
    assert DE.conclusion_hasard({"faible": n(-2, 1)}, False) == "répartie"
    assert DE.conclusion_hasard({}, True) == "sans objet"
    b = {"rate10": {"B-tout": (3, 0.8), "A½": (1, 0.9)}, "retard10": {"B-tout": (0, 0.9), "A½": (0, 0.6)},
         "groupees": {"B-tout": (0, 0.4), "A½": (0, 0.1)}}
    al = DE.alerte_resistance(b)
    assert {(a["mode"], a["autre"]) for a in al} == {("rate10", "A½"), ("retard10", "A½")}


def test_point0_relecture_et_couverture(tmp_path):
    e = ES.entrees_pilote()
    p0 = DE.point0(e, ES.preparees_pilote())
    assert not p0["tenu"] and p0["couverture"] == 1.0 and not p0["relecture_ok"]   # pilote : rodage sans accord
    bilan = tmp_path / "accord.json"
    bilan.write_text(json.dumps(dict(conclusion=EN.accord.PERSISTANT, desaccord_persistant=True,
                                     decisions_otsoa={})), encoding="utf-8")
    rel = os.path.join(BE.DOSSIER_PILOTE, "relecture")
    v = EN.VagueRelecture("pilote-2", os.path.join(rel, "decisions.csv"), os.path.join(rel, "alertes.json"),
                          str(bilan))
    e2 = EN.charger_entrees(BE.DOSSIER_PILOTE, vagues=[v])
    p0b = DE.point0(e2, PR.preparer(e2))
    assert p0b["tenu"] and p0b["persistantes"] == ["pilote-2"]


def test_desaccord_persistant_etiquette_la_moins_favorable(tmp_path):
    bilan = tmp_path / "accord.json"
    bilan.write_text(json.dumps(dict(conclusion=EN.accord.PERSISTANT, desaccord_persistant=True,
                                     decisions_otsoa={})), encoding="utf-8")
    rel = os.path.join(BE.DOSSIER_PILOTE, "relecture")
    v = EN.VagueRelecture("pilote-2", os.path.join(rel, "decisions.csv"), os.path.join(rel, "alertes.json"),
                          str(bilan))
    e = EN.charger_entrees(BE.DOSSIER_PILOTE, vagues=[v])
    cal, conf = BE.partage_par_env(BE.partage_pilote(e))
    cal, conf = {"commerce": cal["commerce"]}, {"commerce": conf["commerce"]}
    reg = AN.Reglages(G0=3, R0=4, B=4, K=2, tranche=4)
    dec = BE.executer(e, cal, conf, reg, str(tmp_path / "sortie"), "essai", secondaires=False, journal=None)
    assert dec["b2"]["vagues"] == ["pilote-2"]
    attendu = DE.moins_favorable(dec["principale"]["etiquette"], dec["b2"]["etiquette_bruts_vague"])
    assert dec["etiquette"] == attendu and dec["principale"]["point0"]["tenu"]


def test_point4_garde_fou_aucun_type_jugeable():
    """N1 (06/11) : R4 suppose au moins un type jugeable quelque part ; sinon « preuves insuffisantes » (amendement du
    07/11, qui remplace « volume insuffisant »), motif « aucun type jugeable »."""
    from types import SimpleNamespace
    cfgs = [("WorkBench", "claude-haiku-5-5"), ("aviation", "claude-opus-5-5")]
    rien = SimpleNamespace(delegables={c: False for c in cfgs}, jugeables={c: False for c in cfgs})
    un = SimpleNamespace(delegables={c: False for c in cfgs}, jugeables={cfgs[0]: True, cfgs[1]: False})
    p4 = DE.point4(rien)
    assert (p4["tenu"], p4["delegables"], p4["jugeable"], p4["etablie"]) == (False, [], False, False)
    assert p4["motif"] == DE.MOTIF_AUCUN_JUGEABLE
    assert DE.point4(un)["jugeable"] and not DE.point4(un)["tenu"]
    oui = dict(tenu=True)
    assert DE.etiquette(oui, oui, oui, DE.point4(rien)) == "preuves insuffisantes"
    # jugeable, mais aucun dépassement établi connu (analyse sans statuts) : pas de R4
    assert DE.etiquette(oui, oui, oui, DE.point4(un)) == "preuves insuffisantes"
    assert DE.point4(un)["motif"] == DE.MOTIF_NON_ETABLI and DE.point4(un)["non_etablies"] == [cfgs[0]]
    ancien = SimpleNamespace(delegables={c: False for c in cfgs})          # analyse sans « jugeables » : pas de R4
    assert DE.etiquette(oui, oui, oui, DE.point4(ancien)) == "preuves insuffisantes"
