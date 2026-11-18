"""Rejeu, phase 1 : entrées (PLAN_EXPERIENCE.md, 5.2) et passage des verdicts aux preuves (5.4, 5.8).

Sur les sorties du pilote (tâches de développement seulement) et sur des actions construites à la main.
"""
import csv
import dataclasses
import json
import os

import pytest

from rejeu import entrees as EN
from rejeu import essais as ES
from rejeu import preuves as PR
from rejeu import suites as SU
from rejeu import types_regle as TY

D = ES.DOSSIER_PILOTE
REL = os.path.join(D, "relecture")


# --------------------------------------------------------------------------
# 5.2, entrées 1 et 2 : parties et actions
# --------------------------------------------------------------------------
def test_parties_et_actions_du_pilote():
    e = ES.entrees_pilote()
    assert len(e.parties) == 120
    assert sum(len(v) for v in e.actions.values()) == 956
    configs = {}
    for p in e.parties:
        configs[(p.environnement, p.modele)] = configs.get((p.environnement, p.modele), 0) + 1
    assert len(configs) == 12 and set(configs.values()) == {10}
    p = next(x for x in e.parties if x.dossier == "tau2-aviation-haiku-1")
    assert (p.id, p.tache, p.strate, p.passage, p.vague, p.statut_ok, p.reussie) == \
        ("9e4a3280-47fa-4dbf-99ef-cb8ec4be2e67", "11", "aviation", 1, "pilote-2", True, True)
    wb = next(x for x in e.parties if x.dossier == "workbench-WorkBench-haiku-1")
    assert (wb.id, wb.tache, wb.strate, wb.debut) == ("claude-haiku-5-5_all_2026-11-05_07-54-15:0", "email:0",
                                                      "WorkBench:email", "2026-11-05T07:54:15")
    # une partie sans aucune action (tau2-aviation-sonnet-9) reste une partie
    assert [x.dossier for x in e.parties if not e.actions[x.id]] == ["tau2-aviation-sonnet-9"]
    assert sum(x.reussie for x in e.parties) == 98  # reussite.txt : 98/120
    for pid, acts in e.actions.items():
        assert [a.rang for a in acts] == sorted(a.rang for a in acts)
    assert all(e.jeu_de(x) == "developpement" for x in e.parties)


def test_action_d_une_partie_inconnue_refusee():
    e = ES.entrees_pilote()
    a = next(iter(next(v for v in e.actions.values() if v)))
    with pytest.raises(EN.EntreeInvalide):
        EN.grouper_actions([dataclasses.replace(a, partie="inconnue")], e.parties)


# --------------------------------------------------------------------------
# 5.2, entrées 3 et 4 : décisions et tâches retirées
# --------------------------------------------------------------------------
def test_alertes_du_pilote_jointes_par_alertes_json():
    j = ES.entrees_pilote().jointure
    assert len(j.alertes) == 7  # 5 fausses et 2 refusées
    assert all(d.decision == EN.CONFIRMEE for d in j.decisions.values())
    # l'alerte levée (motif d) n'en est plus une depuis le correctif payment_id : décision obsolète, listée
    assert j.obsoletes == ["aviation-21-r12-d5376b"]
    assert ES.entrees_pilote().taches_retirees == {}


def _registre(tmp_path, lignes, nom="decisions.csv"):
    chemin = tmp_path / nom
    with open(chemin, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["alerte_id", "decision", "motif", "justification", "preuve"])
        w.writeheader()
        for l in lignes:
            w.writerow({"justification": "essai", "preuve": "essai", **l})
    return str(chemin)


def test_alerte_sans_decision(tmp_path):
    e = ES.entrees_pilote()
    ids = sorted(e.jointure.alertes.values())
    reg = _registre(tmp_path, [dict(alerte_id=i, decision="confirmée", motif="", preuve="") for i in ids[1:]])
    v = EN.VagueRelecture("essai", reg, os.path.join(REL, "alertes.json"))
    with pytest.raises(EN.EntreeInvalide):
        EN.joindre_decisions(e.actions, [v])
    j = EN.joindre_decisions(e.actions, [v], manquante="confirmee")
    assert j.sans_decision == [ids[0]] and j.decisions[ids[0]].decision == EN.CONFIRMEE


def test_identifiant_calcule_par_fiches_sans_alertes_json(tmp_path):
    e = ES.entrees_pilote()
    nouveaux = [EN.fiches.alerte_id(a.ligne()) for acts in e.actions.values() for a in acts if EN.est_alerte(a)]
    assert len(nouveaux) == 7 and all("-" in i and len(i.split("-")[-1]) == 12 for i in nouveaux)
    reg = _registre(tmp_path, [dict(alerte_id=i, decision="confirmée", motif="", preuve="") for i in nouveaux])
    j = EN.joindre_decisions(e.actions, [EN.VagueRelecture("essai", reg)])
    assert sorted(j.alertes.values()) == sorted(nouveaux) and not j.obsoletes


def test_decisions_d_otsoa_et_motif_a(tmp_path):
    """Claude lève X (motif a) et Y (motif b) ; Otsoa confirme Y et lève Z, que Claude avait confirmée."""
    e = ES.entrees_pilote()
    al = json.load(open(os.path.join(REL, "alertes.json"), encoding="utf-8"))
    actuelles = set(e.jointure.alertes.values())
    X = next(a for a in al if a["id"] == "commerce-0-r4-c14d23")   # Sonnet, commerce, tâche 0
    Y, Z = "aviation-23-r14-bdc47b", "aviation-23-r11-2fd01a"
    lignes = []
    for i in sorted(actuelles):
        if i == X["id"]:
            lignes.append(dict(alerte_id=i, decision="levée", motif="a", preuve="a2 : essai"))
        elif i == Y:
            lignes.append(dict(alerte_id=i, decision="levée", motif="b"))
        else:
            lignes.append(dict(alerte_id=i, decision="confirmée", motif="", preuve=""))
    reg = _registre(tmp_path, lignes)
    bilan = tmp_path / "accord.json"
    bilan.write_text(json.dumps({"decisions_otsoa": {Y: "confirmée", Z: "levée"}, "desaccord_persistant": True}),
                     encoding="utf-8")
    v = EN.VagueRelecture("v1", reg, os.path.join(REL, "alertes.json"), str(bilan))
    ent = EN.charger_entrees(D, vagues=[v])
    j = ent.jointure
    assert (j.decisions[Y].decision, j.decisions[Y].par_otsoa) == (EN.CONFIRMEE, True)
    assert (j.decisions[Z].decision, j.decisions[Z].motif) == (EN.LEVEE, "")   # levée par Otsoa : neutre, pas a
    assert j.desaccord_persistant == {"v1": True}
    assert ent.taches_retirees == {("commerce", "0"): f"alerte {X['id']} levée pour le motif a (tâche défectueuse)"}
    # la tâche retirée l'est pour tous les modèles (4.5)
    prep = PR.preparer(ent)
    for m in ("claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"):
        jc = SU.jeu_configuration(prep, ent, "commerce", m, ES.taches_pilote("commerce"), "developpement")
        assert "0" not in {x.partie.tache for x in jc.parties} and "0" not in jc.taches
        assert jc.n_parties == 9
    # liste explicite de tâches retirées (audit), ajoutée aux motifs a
    ent2 = EN.charger_entrees(D, taches_retirees=[("banque", "task_003")])
    assert ent2.taches_retirees == {("banque", "task_003"): "liste des tâches retirées"}


# --------------------------------------------------------------------------
# 5.2, entrée 5 : appartenance
# --------------------------------------------------------------------------
def test_appartenance_depuis_un_partage():
    e = ES.entrees_pilote()
    reserve = {env: ES.taches_pilote(env) for env in ("aviation", "commerce", "banque", "WorkBench")}
    partage = EN.partage_factice(reserve, "ab" * 32)
    app = EN.appartenance_depuis_partage(partage)
    assert len(app) == sum(len(v) for v in reserve.values())
    ent = EN.Entrees(e.parties, e.actions, e.jointure, {}, app, set())
    jeux = {ent.jeu_de(p) for p in e.parties}
    assert jeux == {"calibration", "confirmation"}
    for p in e.parties:
        assert ent.jeu_de(p) == app[(p.strate, p.tache)]
    with pytest.raises(EN.EntreeInvalide):
        EN.appartenance_depuis_partage({"calibration": {"aviation": ["1"]}, "confirmation": {"aviation": ["1"]}})


# --------------------------------------------------------------------------
# 5.4 et 5.8 : des verdicts aux preuves
# --------------------------------------------------------------------------
def action(**kw):
    base = dict(partie="p", tache="t", rang=0, banc="tau2", domaine="retail", outil="o", kind="écriture",
                verdict="juste", motif="", type="argent", enjeu="fort", plafonnee=False, montant=None)
    base.update(kw)
    return EN.Action(**base)


CONF = EN.DecisionRetenue("x", EN.CONFIRMEE, "", "v", False)
LEV = EN.DecisionRetenue("x", EN.LEVEE, "c", "v", False)


def cles(p):
    return (p.categorie, p.type, p.verifiable, p.reussite, p.erreur_preuve, p.erreur_degat, p.au_denominateur,
            p.a_part)


def test_table_de_5_4():
    E_ = PR.ECRITURE
    assert cles(PR.preuve(action())) == (E_, TY.ARG, True, True, False, False, True, False)
    assert cles(PR.preuve(action(verdict="fausse"), CONF)) == (E_, TY.ARG, True, False, True, True, True, False)
    assert cles(PR.preuve(action(verdict="fausse"), LEV)) == (E_, TY.ARG, True, False, False, False, True, False)
    assert cles(PR.preuve(action(verdict="doublon"), CONF)) == (E_, TY.ARG, True, False, True, True, True, False)
    assert cles(PR.preuve(action(verdict="doublon sans effet"))) == (E_, TY.ARG, True, False, False, False, False,
                                                                     False)
    # refusée : erreur pour la règle, pas un dégât, hors dénominateur (point 6 ; Q4 a)
    assert cles(PR.preuve(action(verdict="refusée"), CONF)) == (E_, TY.ARG, True, False, True, False, False, False)
    assert cles(PR.preuve(action(verdict="refusée"), LEV)) == (E_, TY.ARG, True, False, False, False, False, False)
    # inconnu : invérifiable, ILL, dégât à part, hors dénominateur
    assert cles(PR.preuve(action(kind="inconnu", verdict="", type="effet illisible"))) == \
        (E_, TY.ILL, False, False, False, False, False, True)
    # ILL avec un verdict : la preuve suit le verdict, le dégât est à part, hors dénominateur (M5)
    assert cles(PR.preuve(action(type="effet illisible", verdict="fausse", plafonnee=True), CONF)) == \
        (E_, TY.ILL, True, False, True, True, False, True)
    assert PR.preuve(action(type="effet illisible", verdict="fausse", plafonnee=True), CONF).plafonnee
    # plafonnée : garde son type et sa preuve ; elle compte au dénominateur (Q4 a)
    p = PR.preuve(action(plafonnee=True))
    assert (p.type, p.plafonnee, p.reussite, p.au_denominateur) == (TY.ARG, True, True, True)
    # hors suite : lectures (kind « autre » typé lecture compris), préparations, doutes
    assert PR.preuve(action(kind="lecture", verdict="", type="lecture")).categorie == PR.LECTURE
    assert PR.preuve(action(kind="autre", verdict="", type="lecture")).categorie == PR.LECTURE
    assert PR.preuve(action(kind="autre", verdict="", type="préparation")).categorie == PR.PREPARATION
    assert PR.preuve(action(kind="doute", verdict="", type="doute")).categorie == PR.DOUTE
    # kind « autre » typé comme une écriture : invérifiable de son type
    assert cles(PR.preuve(action(kind="autre", verdict="", type="écriture réversible"))) == \
        (E_, TY.ECR, False, False, False, False, False, True)


def test_cas_refuses_par_les_preuves():
    with pytest.raises(EN.EntreeInvalide):
        PR.preuve(action(verdict="fausse"))  # alerte sans décision (verdicts confirmés)
    with pytest.raises(EN.EntreeInvalide):
        PR.preuve(action(verdict="fausse"), EN.DecisionRetenue("x", EN.LEVEE, "a", "v", False))  # tâche non retirée
    with pytest.raises(EN.EntreeInvalide):
        PR.preuve(action(type="lecture"))  # écriture typée lecture : table incohérente
    with pytest.raises(EN.EntreeInvalide):
        PR.preuve(action(verdict="bizarre"))


def test_verdicts_bruts():
    """4.6 : avant marquer_doublons_sans_effet et avec la comparaison stricte de payment_id ; toute alerte est une
    erreur, les dégâts suivent la même table."""
    E_ = PR.ECRITURE
    assert cles(PR.preuve(action(verdict="doublon sans effet"), brut=True)) == \
        (E_, TY.ARG, True, False, True, True, True, False)
    pid = action(verdict="juste", motif="payment_id sans effet (aucun paiement enregistré)")
    assert PR.preuve(pid).reussite and PR.preuve(pid, brut=True).erreur_preuve
    assert cles(PR.preuve(action(verdict="fausse"), brut=True)) == (E_, TY.ARG, True, False, True, True, True, False)
    assert cles(PR.preuve(action(verdict="refusée"), brut=True)) == (E_, TY.ARG, True, False, True, False, False,
                                                                     False)
    assert PR.preuve(action(verdict="fausse"), LEV, brut=True).erreur_preuve is False  # décision d'Otsoa appliquée


def test_preuves_du_pilote_confirmees_et_brutes():
    c = PR.resume(ES.preparees_pilote("confirmes"))
    assert (c["actions"], c["lectures"], c["preparations"], c["doutes"], c["ecritures"]) == (956, 761, 3, 44, 148)
    # 106 justes ; 5 fausses et 2 refusées confirmées ; 35 doublons sans effet neutres et hors dénominateur
    assert (c["reussites"], c["erreurs_preuve"], c["erreurs_degat"], c["au_denominateur"]) == (106, 7, 5, 111)
    assert (c["plafonnees"], c["a_part"], c["couverture"]) == (7, 0, 1.0)
    b = PR.resume(ES.preparees_pilote("bruts"))
    # + 35 doublons et 1 juste par l'exception payment_id, comptés comme erreurs
    assert (b["reussites"], b["erreurs_preuve"], b["erreurs_degat"], b["au_denominateur"]) == (105, 43, 41, 146)
    e = ES.entrees_pilote()
    v = PR.resume(PR.preparer(e, "bruts_vague", {"pilote-2"}))
    assert v == b   # aucune décision d'Otsoa au pilote : verdicts bruts pour la vague
    assert PR.resume(PR.preparer(e, "bruts_vague", {"autre"})) == c


def test_opposition_d_otsoa_garde_la_tache(tmp_path):
    """Relecture C13, P9 : une tâche visée par une opposition d'Otsoa n'est pas retirée ; ses alertes levées pour le
    motif a deviennent des erreurs confirmées (décision d'Otsoa)."""
    e = ES.entrees_pilote()
    X = "commerce-0-r4-c14d23"
    lignes = [dict(alerte_id=i, decision="levée", motif="a", preuve="a2 : essai") if i == X
              else dict(alerte_id=i, decision="confirmée", motif="", preuve="") for i in sorted(set(e.jointure.alertes.values()))]
    v = EN.VagueRelecture("v1", _registre(tmp_path, lignes), os.path.join(REL, "alertes.json"))
    sans = EN.charger_entrees(D, vagues=[v])
    assert ("commerce", "0") in sans.taches_retirees
    avec = EN.charger_entrees(D, vagues=[v], oppositions=[("commerce", "0")])
    assert ("commerce", "0") not in avec.taches_retirees
    d = avec.jointure.decisions[X]
    assert (d.decision, d.motif, d.par_otsoa) == (EN.CONFIRMEE, "", True)
