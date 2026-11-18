"""Doublons sans effet (REGLE.md, 5 novembre, point 6, precision du matin).

Un doublon n'est une erreur que si refaire l'ecriture change l'etat persistant. L'idempotence de chaque outil est
lue dans banc/table_outils.json (champ `idempotent`), verifiee dans le code des bancs. Etape juste apres juger() :
verdicts.marquer_doublons_sans_effet. Aucun clone de banc n'est necessaire ici.
"""
import copy
import csv
import json
import sys
from pathlib import Path

import pytest

BANC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BANC))
sys.path.insert(0, str(BANC / "relecture"))

import verdicts as v  # noqa: E402

TABLE = json.loads((BANC / "table_outils.json").read_text(encoding="utf-8"))
VALEURS = {"oui", "non", "refus", "incertain", "sans objet"}


def ligne(outil, verdict, banc="tau2", domaine="banking_knowledge", kind="écriture", **kw):
    base = {c: "" for c in v.CHAMPS}
    base.update(partie="p", tache="1", rang="0", banc=banc, domaine=domaine, outil=outil, arguments="{}", kind=kind,
                verdict=verdict)
    base.update(kw)
    return base


# --- idempotence lue dans la table -------------------------------------------------------------------------
def test_chaque_outil_de_la_table_a_une_idempotence():
    for o in TABLE["outils"]:
        assert o.get("idempotent") in VALEURS, o["outil"]
        assert o.get("idempotent_preuve"), o["outil"]


def test_les_ecritures_ont_un_vrai_diagnostic_les_autres_sans_objet():
    for o in TABLE["outils"]:
        if o["type"] in ("lecture", "doute", "préparation"):
            assert o["idempotent"] == "sans objet", o["outil"]
        elif o["outil"] != "call_discoverable_agent_tool":
            assert o["idempotent"] in {"oui", "non", "refus", "incertain"}, o["outil"]


@pytest.mark.parametrize("banc,domaine,outil,attendu", [
    ("tau2", "banking_knowledge", "give_discoverable_user_tool", "oui"),
    ("tau2", "banking_knowledge", "change_user_email", "oui"),
    ("tau2", "airline", "update_reservation_passengers", "oui"),
    ("tau2", "airline", "cancel_reservation", "non"),
    ("tau2", "airline", "send_certificate", "non"),
    ("tau2", "banking_knowledge", "transfer_funds_between_bank_accounts_7291", "non"),
    ("tau2", "retail", "cancel_pending_order", "refus"),
    ("tau2", "banking_knowledge", "apply_statement_credit_8472", "refus"),
    ("workbench", "email", "email.send_email", "non"),
    ("workbench", "email", "email.delete_email", "refus"),
    ("workbench", "project_management", "project_management.update_task", "oui"),
    ("workbench", "analytics", "analytics.create_plot", "incertain"),
])
def test_idempotence_lue_dans_la_table(banc, domaine, outil, attendu):
    assert v.idempotence(banc, domaine, outil) == attendu


def test_outil_inconnu_est_traite_comme_incertain():
    assert v.idempotence("tau2", "retail", "outil_invente") == "incertain"


def test_idempotence_workbench_ne_depend_pas_du_domaine_de_la_ligne():
    assert v.idempotence("workbench", "multi_domain", "email.send_email") == "non"
    assert v.idempotence("workbench", "multi_domain", "calendar.update_event") == "oui"


# --- doublon sur outil idempotent ----------------------------------------------------------------------------
def test_doublon_sur_outil_idempotent_devient_sans_effet():
    lignes = [ligne("give_discoverable_user_tool", "juste"), ligne("give_discoverable_user_tool", "doublon")]
    sortie = v.marquer_doublons_sans_effet(lignes)
    assert [l["verdict"] for l in sortie] == ["juste", "doublon sans effet"]
    assert v.DOUBLON_SANS_EFFET == "doublon sans effet"


def test_doublon_workbench_update_idempotent():
    lignes = [ligne("calendar.update_event", "doublon", banc="workbench", domaine="calendar")]
    assert v.marquer_doublons_sans_effet(lignes)[0]["verdict"] == "doublon sans effet"


# --- doublon sur outil non idempotent ------------------------------------------------------------------------
@pytest.mark.parametrize("banc,domaine,outil", [
    ("tau2", "airline", "cancel_reservation"),
    ("tau2", "banking_knowledge", "pay_credit_card_from_checking_9182"),
    ("workbench", "email", "email.send_email"),
])
def test_doublon_sur_outil_non_idempotent_reste_une_erreur(banc, domaine, outil):
    sortie = v.marquer_doublons_sans_effet([ligne(outil, "doublon", banc=banc, domaine=domaine)])
    assert sortie[0]["verdict"] == "doublon"


def test_doublon_sur_outil_refus_reste_doublon():
    assert v.marquer_doublons_sans_effet([ligne("cancel_pending_order", "doublon", domaine="retail")])[0]["verdict"] == "doublon"


# --- outil incertain -----------------------------------------------------------------------------------------
def test_outil_incertain_reste_doublon_par_prudence():
    sortie = v.marquer_doublons_sans_effet([ligne("analytics.create_plot", "doublon", banc="workbench", domaine="analytics")])
    assert sortie[0]["verdict"] == "doublon"


def test_outil_absent_de_la_table_reste_doublon():
    assert v.marquer_doublons_sans_effet([ligne("outil_invente", "doublon")])[0]["verdict"] == "doublon"


def test_table_passee_en_parametre():
    table = {"outils": [{"banc": "tau2", "domaine": "retail", "outil": "x", "idempotent": "oui"}]}
    assert v.marquer_doublons_sans_effet([ligne("x", "doublon", domaine="retail")], table)[0]["verdict"] == "doublon sans effet"
    table["outils"][0]["idempotent"] = "incertain"
    assert v.marquer_doublons_sans_effet([ligne("x", "doublon", domaine="retail")], table)[0]["verdict"] == "doublon"


# --- le reste ne bouge pas -------------------------------------------------------------------------------------
def test_autres_verdicts_et_champs_inchanges_entree_non_modifiee():
    lignes = [ligne("change_user_email", "juste"), ligne("change_user_email", "fausse"), ligne("change_user_email", "refusée"),
              ligne("get_x", "", kind="lecture"), ligne("change_user_email", "doublon", motif="m", resultat="r")]
    avant = copy.deepcopy(lignes)
    sortie = v.marquer_doublons_sans_effet(lignes)
    assert lignes == avant
    assert [l["verdict"] for l in sortie] == ["juste", "fausse", "refusée", "", "doublon sans effet"]
    assert [list(l) for l in sortie] == [list(l) for l in avant]
    assert sortie[4]["motif"] == "m" and sortie[4]["resultat"] == "r"


def test_doublon_sans_effet_nest_pas_une_alerte():
    import fiches
    assert v.DOUBLON_SANS_EFFET not in fiches.VERDICTS_ALERTE
    assert set(fiches.VERDICTS_ALERTE) == {"fausse", "doublon", "refusée"}


def test_fiches_exclut_les_doublons_sans_effet(tmp_path):
    import fiches
    champs = ["partie", "tache", "rang", "banc", "domaine", "outil", "arguments", "kind", "verdict", "modele", "motif",
              "resultat", "type", "enjeu", "plafonnee", "montant", "raison", "etiquettes"]
    rows = []
    for i, verdict in enumerate(["juste", "fausse", "doublon", "doublon sans effet", "refusée"]):
        r = {c: "" for c in champs}
        r.update(partie="p", tache="1", rang=str(i), banc="tau2", domaine="airline", outil="o", kind="écriture", verdict=verdict)
        rows.append(r)
    with open(tmp_path / "actions_typees.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=champs)
        w.writeheader()
        w.writerows(rows)
    assert [a["verdict"] for a in fiches.lire_alertes(tmp_path)] == ["fausse", "doublon", "refusée"]


# --- cablage dans le CSV -------------------------------------------------------------------------------------
def test_verdicts_csv_applique_l_etape(tmp_path, monkeypatch):
    import verdicts_csv
    brutes = [ligne("give_discoverable_user_tool", "juste"), ligne("give_discoverable_user_tool", "doublon"),
              ligne("cancel_reservation", "doublon", domaine="airline")]
    monkeypatch.setattr(v, "actions_dossier", lambda *a, **k: iter(brutes))
    sortie = tmp_path / "a.csv"
    assert verdicts_csv.main(["--dossier", str(tmp_path), "--sortie", str(sortie)]) == 0
    lignes = list(csv.DictReader(open(sortie, newline="", encoding="utf-8")))
    assert [l["verdict"] for l in lignes] == ["juste", "doublon sans effet", "doublon"]
    assert list(lignes[0].keys()) == v.CHAMPS


# --- table generee --------------------------------------------------------------------------------------------
def test_table_md_porte_la_colonne_et_le_paragraphe_date():
    md = (BANC / "TABLE_OUTILS.md").read_text(encoding="utf-8")
    assert "| Idempotent |" in md
    assert "point 6" in md and "précision" in md and "doublon sans effet" in md
