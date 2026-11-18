"""Tests du module de verdicts action par action (TDD : ecrits avant verdicts.py).

Les tests synthetiques n'ont besoin d'aucun clone de banc. Les tests sur les
parties enregistrees et sur les fichiers de taches sont ignores si les clones
sont absents (chemins par defaut ci-dessous, surchargeables par variables
d'environnement TAU2_RACINE et WORKBENCH_RACINE).
"""
import csv
import json
import os
import re
from pathlib import Path

import pytest

import verdicts as v

_EXTERNE = Path(__file__).resolve().parents[2] / "externe"  # clones épinglés (banc/INSTALLATION.md)
TAU2 = Path(os.environ.get("TAU2_RACINE", _EXTERNE / "tau2-bench"))
WORKBENCH = Path(os.environ.get("WORKBENCH_RACINE", _EXTERNE / "WorkBench"))
besoin_tau2 = pytest.mark.skipif(not TAU2.is_dir(), reason="clone tau-bench absent")
besoin_workbench = pytest.mark.skipif(not WORKBENCH.is_dir(), reason="clone WorkBench absent")


# --------------------------------------------------------------------------
# Outils de construction de parties synthetiques (format simulation tau-bench)
# --------------------------------------------------------------------------
TYPES = v.TypesOutils(
    directs={
        "get_order_details": "read",
        "cancel_pending_order": "write",
        "modify_pending_order_items": "write",
        "transfer_to_human_agents": "generic",
        "calculate": "generic",
        "call_discoverable_agent_tool": "write",
        "unlock_discoverable_agent_tool": "generic",
        "rewrite_context": "write_sans_etat",
    },
    decouvrables={
        "apply_checking_account_credit_5829": "write",
        "get_payment_history_6183": "read",
        "initial_transfer_to_human_agent_0218": "generic",
    },
)


def appel(i, nom, args, requestor=None):
    c = {"id": f"c{i}", "name": nom, "arguments": args}
    if requestor:
        c["requestor"] = requestor
    return c


def msg_agent(*calls):
    return {"role": "assistant", "content": None, "tool_calls": list(calls)}


def rep(i, contenu="ok", erreur=False, requestor=None, statut=None):
    m = {"id": f"c{i}", "role": "tool", "content": contenu}
    if erreur:
        m["error"] = True
    if requestor:
        m["requestor"] = requestor
    if statut:
        m["execution_status"] = statut
    return m


def partie(*msgs, task_id="1"):
    return {"id": "p1", "task_id": task_id, "messages": list(msgs)}


def att(nom, args, compare_args=None):
    return v.Attendue(nom=nom, arguments=args, compare_args=compare_args)


def verdicts_de(run, attendues, types=TYPES, domaine="retail", modele="m"):
    acts = v.actions_partie_tau2(
        run, {"1": attendues}, types, domaine=domaine, modele=modele
    )
    return acts


def seuls_verdicts(acts):
    return [a["verdict"] for a in acts if a["kind"] == "écriture"]


# --------------------------------------------------------------------------
# Cas synthetiques
# --------------------------------------------------------------------------
def test_correspondance_exacte():
    run = partie(
        msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W1", "reason": "no longer needed"})),
        rep(1),
    )
    acts = verdicts_de(run, [att("cancel_pending_order", {"order_id": "#W1", "reason": "no longer needed"})])
    assert seuls_verdicts(acts) == ["juste"]


def test_argument_faux():
    run = partie(
        msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W2", "reason": "no longer needed"})),
        rep(1),
    )
    acts = verdicts_de(run, [att("cancel_pending_order", {"order_id": "#W1", "reason": "no longer needed"})])
    assert seuls_verdicts(acts) == ["fausse"]


def test_argument_en_trop_ou_manquant_est_faux():
    attendue = att("cancel_pending_order", {"order_id": "#W1", "reason": "x"})
    en_trop = partie(
        msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W1", "reason": "x", "extra": 1})), rep(1)
    )
    manquant = partie(msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W1"})), rep(1))
    assert seuls_verdicts(verdicts_de(en_trop, [attendue])) == ["fausse"]
    assert seuls_verdicts(verdicts_de(manquant, [attendue])) == ["fausse"]


def test_nom_different_est_faux():
    run = partie(msg_agent(appel(1, "modify_pending_order_items", {"order_id": "#W1"})), rep(1))
    acts = verdicts_de(run, [att("cancel_pending_order", {"order_id": "#W1"})])
    assert seuls_verdicts(acts) == ["fausse"]


def test_ecriture_dans_une_tache_sans_attendue():
    run = partie(msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W1", "reason": "x"})), rep(1))
    assert seuls_verdicts(verdicts_de(run, [])) == ["fausse"]
    # tache absente de la table : meme traitement, pas d'exception
    acts = v.actions_partie_tau2(run, {}, TYPES, domaine="retail", modele=None)
    assert seuls_verdicts(acts) == ["fausse"]


def test_doublon():
    a = {"order_id": "#W1", "reason": "x"}
    run = partie(
        msg_agent(appel(1, "cancel_pending_order", a)),
        rep(1),
        msg_agent(appel(2, "cancel_pending_order", a)),
        rep(2),
    )
    assert seuls_verdicts(verdicts_de(run, [att("cancel_pending_order", a)])) == ["juste", "doublon"]


def test_appariement_un_pour_un_deux_attendues_identiques():
    a = {"order_id": "#W1", "reason": "x"}
    run = partie(
        msg_agent(appel(1, "cancel_pending_order", a)), rep(1),
        msg_agent(appel(2, "cancel_pending_order", a)), rep(2),
        msg_agent(appel(3, "cancel_pending_order", a)), rep(3),
    )
    att2 = [att("cancel_pending_order", a), att("cancel_pending_order", a)]
    assert seuls_verdicts(verdicts_de(run, att2)) == ["juste", "juste", "doublon"]


def test_ecriture_refusee_par_erreur_outil():
    a = {"order_id": "#W1", "reason": "x"}
    run = partie(
        msg_agent(appel(1, "cancel_pending_order", a)),
        rep(1, "Error: order is not pending", erreur=True),
    )
    assert seuls_verdicts(verdicts_de(run, [att("cancel_pending_order", a)])) == ["refusée"]


def test_refusee_ne_consomme_pas_l_attendue():
    a = {"order_id": "#W1", "reason": "x"}
    run = partie(
        msg_agent(appel(1, "cancel_pending_order", a)), rep(1, "Error: boom", erreur=True),
        msg_agent(appel(2, "cancel_pending_order", a)), rep(2),
    )
    assert seuls_verdicts(verdicts_de(run, [att("cancel_pending_order", a)])) == ["refusée", "juste"]


def test_refusee_meme_si_aucune_attendue_et_si_rejetee_par_orchestrateur():
    run = partie(
        msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W9"})),
        rep(1, "rejected", erreur=True, statut="rejected"),
    )
    assert seuls_verdicts(verdicts_de(run, [])) == ["refusée"]


def test_14_00_contre_14_0_et_int_float():
    attendue = v.attendue_depuis_action(
        {
            "name": "call_discoverable_agent_tool",
            "arguments": {
                "agent_tool_name": "apply_checking_account_credit_5829",
                "arguments": '{"account_id": "chk_1", "amount": 14.00, "credit_type": "fee_refund"}',
            },
        }
    )
    run = partie(
        msg_agent(
            appel(
                1,
                "call_discoverable_agent_tool",
                {
                    "agent_tool_name": "apply_checking_account_credit_5829",
                    "arguments": '{"credit_type": "fee_refund", "amount": 14.0, "account_id": "chk_1"}',
                },
            )
        ),
        rep(1, "credit applied"),
    )
    acts = verdicts_de(run, [attendue], domaine="banking_knowledge")
    assert seuls_verdicts(acts) == ["juste"]
    assert acts[0]["outil"] == "apply_checking_account_credit_5829"
    # entier contre flottant au premier niveau
    assert v.normaliser({"x": 14}) == v.normaliser({"x": 14.0}) == v.normaliser({"x": 14.00})
    assert v.normaliser(14.5) != v.normaliser(14)
    # un booleen n'est pas un nombre
    assert v.normaliser(True) != v.normaliser(1)


def test_json_imbrique_cles_dans_un_autre_ordre():
    attendue = v.attendue_depuis_action(
        {
            "name": "call_discoverable_agent_tool",
            "arguments": {
                "agent_tool_name": "apply_checking_account_credit_5829",
                "arguments": '{"a": 1, "b": {"x": 1, "y": [1, 2]}}',
            },
        }
    )
    run = partie(
        msg_agent(
            appel(
                1,
                "call_discoverable_agent_tool",
                {
                    "agent_tool_name": "apply_checking_account_credit_5829",
                    "arguments": '{"b": {"y": [1, 2], "x": 1.0}, "a": 1}',
                },
            )
        ),
        rep(1),
    )
    assert seuls_verdicts(verdicts_de(run, [attendue], domaine="banking_knowledge")) == ["juste"]


def test_ordre_des_listes_compte():
    a1 = {"order_id": "#W1", "item_ids": ["1", "2"]}
    a2 = {"order_id": "#W1", "item_ids": ["2", "1"]}
    run = partie(msg_agent(appel(1, "modify_pending_order_items", a2)), rep(1))
    assert seuls_verdicts(verdicts_de(run, [att("modify_pending_order_items", a1)])) == ["fausse"]


def test_json_imbrique_dans_un_argument_ordinaire():
    a_att = {"order_id": "#W1", "payload": '{"k": 1, "j": 2}'}
    a_ag = {"order_id": "#W1", "payload": '{"j": 2.0, "k": 1}'}
    run = partie(msg_agent(appel(1, "modify_pending_order_items", a_ag)), rep(1))
    assert seuls_verdicts(verdicts_de(run, [att("modify_pending_order_items", a_att)])) == ["juste"]


def test_chaine_numerique_n_est_pas_un_nombre():
    run = partie(msg_agent(appel(1, "modify_pending_order_items", {"order_id": "0123"})), rep(1))
    acts = verdicts_de(run, [att("modify_pending_order_items", {"order_id": "123"})])
    assert seuls_verdicts(acts) == ["fausse"]


def test_actions_dans_un_autre_ordre():
    a, b = {"order_id": "#W1", "reason": "x"}, {"order_id": "#W2", "reason": "x"}
    run = partie(
        msg_agent(appel(1, "cancel_pending_order", b)), rep(1),
        msg_agent(appel(2, "cancel_pending_order", a)), rep(2),
    )
    att2 = [att("cancel_pending_order", a), att("cancel_pending_order", b)]
    assert seuls_verdicts(verdicts_de(run, att2)) == ["juste", "juste"]


def test_compare_args_partiel():
    attendue = att("modify_pending_order_items", {"order_id": "#W1", "reason": "x", "note": "a"}, ("order_id",))
    run = partie(
        msg_agent(appel(1, "modify_pending_order_items", {"order_id": "#W1", "reason": "AUTRE", "note": "b"})),
        rep(1),
        msg_agent(appel(2, "modify_pending_order_items", {"order_id": "#W2", "reason": "x"})),
        rep(2),
    )
    assert seuls_verdicts(verdicts_de(run, [attendue])) == ["juste", "fausse"]


def test_compare_args_vide_ne_compare_que_le_nom():
    attendue = att("modify_pending_order_items", {"order_id": "#W1"}, ())
    run = partie(msg_agent(appel(1, "modify_pending_order_items", {"order_id": "#ZZ"})), rep(1))
    assert seuls_verdicts(verdicts_de(run, [attendue])) == ["juste"]


def test_compare_args_banque_agent_tool_name_seul():
    # compare_args=['agent_tool_name'] : seul le nom de l'outil sous-jacent compte
    attendue = v.attendue_depuis_action(
        {
            "name": "call_discoverable_agent_tool",
            "arguments": {"agent_tool_name": "apply_checking_account_credit_5829"},
            "compare_args": ["agent_tool_name"],
            "requestor": "assistant",
        },
        TYPES,
    )
    run = partie(
        msg_agent(
            appel(
                1,
                "call_discoverable_agent_tool",
                {"agent_tool_name": "apply_checking_account_credit_5829", "arguments": '{"amount": 3}'},
            )
        ),
        rep(1),
    )
    assert seuls_verdicts(verdicts_de(run, [attendue], domaine="banking_knowledge")) == ["juste"]


def test_actions_de_l_utilisateur_ignorees():
    run = partie(
        {
            "role": "user",
            "content": None,
            "tool_calls": [appel(1, "cancel_pending_order", {"order_id": "#W1"}, requestor="user")],
        },
        rep(1, requestor="user"),
        msg_agent(appel(2, "get_order_details", {"order_id": "#W1"})),
        rep(2),
    )
    acts = verdicts_de(run, [])
    assert [a["outil"] for a in acts] == ["get_order_details"]
    # un appel marque requestor=user porte par un message assistant est ignore aussi
    run2 = partie(msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W1"}, requestor="user")), rep(1))
    assert verdicts_de(run2, []) == []


def test_lectures_et_doutes_sans_verdict():
    run = partie(
        msg_agent(appel(1, "get_order_details", {"order_id": "#W1"})), rep(1),
        msg_agent(appel(2, "transfer_to_human_agents", {"summary": "s"})), rep(2),
        msg_agent(appel(3, "calculate", {"expression": "1+1"})), rep(3),
    )
    acts = verdicts_de(run, [])
    assert [(a["kind"], a["verdict"]) for a in acts] == [("lecture", ""), ("doute", ""), ("autre", "")]


def test_outils_decouvrables_banque():
    run = partie(
        msg_agent(
            appel(1, "call_discoverable_agent_tool", {"agent_tool_name": "get_payment_history_6183", "arguments": "{}"}),
        ),
        rep(1),
        msg_agent(
            appel(2, "call_discoverable_agent_tool", {"agent_tool_name": "initial_transfer_to_human_agent_0218"}),
        ),
        rep(2),
        msg_agent(
            appel(
                3,
                "call_discoverable_agent_tool",
                {"agent_tool_name": "apply_checking_account_credit_5829", "arguments": "{\"amount\": 5}"},
            ),
        ),
        rep(3, "Error: Account 'x' not found."),  # erreur renvoyee en texte, error=False
        msg_agent(appel(4, "unlock_discoverable_agent_tool", {"agent_tool_name": "apply_checking_account_credit_5829"})),
        rep(4),
    )
    acts = verdicts_de(run, [], domaine="banking_knowledge")
    assert [(a["outil"], a["kind"], a["verdict"]) for a in acts] == [
        ("get_payment_history_6183", "lecture", ""),
        ("initial_transfer_to_human_agent_0218", "doute", ""),
        ("apply_checking_account_credit_5829", "écriture", "refusée"),
        ("unlock_discoverable_agent_tool", "autre", ""),
    ]


def test_arguments_decouvrable_json_invalide_ne_plante_pas():
    run = partie(
        msg_agent(appel(1, "call_discoverable_agent_tool", {"agent_tool_name": "apply_checking_account_credit_5829", "arguments": "{pas du json"})),
        rep(1, "Error: Invalid JSON in arguments: x"),
    )
    acts = verdicts_de(run, [], domaine="banking_knowledge")
    assert seuls_verdicts(acts) == ["refusée"]


def test_ecriture_sans_etat_n_est_pas_une_ecriture():
    # rewrite_context : decore WRITE mais mutates_state=False
    run = partie(msg_agent(appel(1, "rewrite_context", {"new_context": "x"})), rep(1))
    acts = verdicts_de(run, [])
    assert acts[0]["kind"] == "autre" and acts[0]["verdict"] == ""


def test_outil_inconnu():
    run = partie(msg_agent(appel(1, "outil_invente", {})), rep(1, "Error: Tool not found", erreur=True))
    acts = verdicts_de(run, [])
    assert acts[0]["kind"] == "inconnu" and acts[0]["verdict"] == ""


def test_champs_de_sortie_et_rang():
    run = partie(
        msg_agent(appel(1, "get_order_details", {"order_id": "#W1"})), rep(1),
        msg_agent(appel(2, "cancel_pending_order", {"order_id": "#W1", "reason": "x"})), rep(2),
    )
    run["id"] = "sim-42"
    acts = v.actions_partie_tau2(
        run, {"1": [att("cancel_pending_order", {"order_id": "#W1", "reason": "x"})]},
        TYPES, domaine="retail", modele="claude-x",
    )
    assert set(acts[0]) == set(v.CHAMPS)
    assert [a["rang"] for a in acts] == [0, 1]
    a = acts[1]
    assert (a["partie"], a["tache"], a["banc"], a["domaine"], a["outil"], a["kind"], a["verdict"], a["modele"]) == (
        "sim-42", "1", "tau2", "retail", "cancel_pending_order", "écriture", "juste", "claude-x",
    )
    assert json.loads(a["arguments"]) == {"order_id": "#W1", "reason": "x"}


def test_reponse_manquante_n_est_pas_un_refus():
    run = partie(msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W1", "reason": "x"})))
    assert seuls_verdicts(verdicts_de(run, [att("cancel_pending_order", {"order_id": "#W1", "reason": "x"})])) == ["juste"]


def test_messages_dans_le_desordre_sont_ranges_par_turn_idx():
    m_rep = {**rep(1), "turn_idx": 5}
    m_call = {**msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W1", "reason": "x"})), "turn_idx": 6}
    m_call2 = {**msg_agent(appel(2, "get_order_details", {"order_id": "#W1"})), "turn_idx": 2}
    acts = verdicts_de(partie(m_rep, m_call, m_call2), [])
    assert [a["outil"] for a in acts] == ["get_order_details", "cancel_pending_order"]


# --------------------------------------------------------------------------
# Types d'outils extraits par regex
# --------------------------------------------------------------------------
@besoin_tau2
def test_types_retail_airline():
    t = v.types_tau2(TAU2, "retail")
    assert t.directs["modify_pending_order_items"] == "write"
    assert t.directs["get_order_details"] == "read"
    assert t.directs["calculate"] == "generic"
    assert t.directs["transfer_to_human_agents"] == "generic"
    assert "think" not in t.directs  # decorateur commente : pas un outil
    ta = v.types_tau2(TAU2, "airline")
    assert ta.directs["book_reservation"] == "write"
    assert ta.directs["get_flight_status"] == "read"


@besoin_tau2
def test_types_banque_directs_et_decouvrables():
    t = v.types_tau2(TAU2, "banking_knowledge")
    assert t.directs["call_discoverable_agent_tool"] == "write"
    assert t.directs["unlock_discoverable_agent_tool"] == "generic"
    assert t.directs["change_user_email"] == "write"
    assert t.directs["rewrite_context"] == "write_sans_etat"
    assert t.directs["grep"] == "read"
    assert t.decouvrables["apply_checking_account_credit_5829"] == "write"
    assert t.decouvrables["get_payment_history_6183"] == "read"
    assert t.decouvrables["initial_transfer_to_human_agent_0218"] == "generic"
    # les outils decouvrables de l'utilisateur ne sont pas ceux de l'agent
    assert "submit_cash_back_dispute_0589" not in t.decouvrables
    assert "apply_checking_account_credit_5829" not in t.directs


@besoin_tau2
def test_taches_tau2_banque_deballe_les_decouvrables_et_ecarte_l_utilisateur():
    t = v.types_tau2(TAU2, "banking_knowledge")
    taches = v.charger_taches_tau2(TAU2, "banking_knowledge", t)
    assert len(taches) == 97
    toutes = [a for lst in taches.values() for a in lst]
    assert not any(a.nom == "call_discoverable_agent_tool" for a in toutes)
    assert not any(a.nom in ("apply_for_credit_card", "submit_referral", "request_human_agent_transfer") for a in toutes)
    montants = [a for a in toutes if a.nom == "apply_checking_account_credit_5829"]
    assert montants and all(isinstance(a.arguments, dict) for a in montants)


# --------------------------------------------------------------------------
# Les 3 parties livrees avec tau-bench : coherence avec les action_checks
# --------------------------------------------------------------------------
PARTIES_ISSUES = sorted((TAU2 / "data/tau2/domains/retail/task_issues").glob("*.json")) if TAU2.is_dir() else []


@besoin_tau2
def test_trois_parties_livrees_existent():
    assert len(PARTIES_ISSUES) == 3


@besoin_tau2
@pytest.mark.parametrize("chemin", PARTIES_ISSUES, ids=lambda p: p.name)
def test_coherence_avec_action_checks_du_banc(chemin):
    run = json.loads(chemin.read_text())
    types = v.types_tau2(TAU2, "retail")
    taches = v.charger_taches_tau2(TAU2, "retail", types)
    attendues = taches[str(run["task_id"])]
    acts = v.actions_partie_tau2(run, taches, types, domaine="retail", modele=None)
    appels = v.appels_tau2(run["messages"], types)
    jug = v.juger(appels, attendues)  # liste de (verdict, index de l'attendue consommee)
    juste = [(ap, ix) for ap, (verd, ix) in zip(appels, jug) if verd == "juste"]

    checks = run["reward_info"]["action_checks"]
    ecr_attendues = [(i, c) for i, c in enumerate(checks) if types.directs[c["action"]["name"]] == "write"]
    trouvees_par_banc = [i for i, c in ecr_attendues if c["action_match"]]
    assert trouvees_par_banc, "la partie doit comporter une ecriture attendue trouvee"
    # chaque ecriture attendue que le banc marque trouvee est appariee chez nous
    assert len(juste) >= len(trouvees_par_banc)
    idx_consommes = {ix for _, ix in juste}
    # action_checks suit l'ordre de evaluation_criteria.actions
    assert [c["action"]["name"] for c in checks] == [a.nom for a in attendues]
    for i in trouvees_par_banc:
        assert i in idx_consommes, f"attendue {i} trouvee par le banc mais non appariee"
    # on ne marque pas juste plus d'ecritures qu'il n'y en a d'attendues
    assert len(juste) <= len([a for a in attendues if types.directs[a.nom] == "write"])
    assert len([a for a in acts if a["verdict"] == "juste"]) == len(juste)
    # les lectures et les doutes n'ont aucun verdict
    assert all(a["verdict"] == "" for a in acts if a["kind"] != "écriture")


# --------------------------------------------------------------------------
# WorkBench
# --------------------------------------------------------------------------
def test_parser_appel_workbench_ast():
    nom, args = v.parser_appel_workbench('email.delete_email.func(email_id="00000479")')
    assert (nom, args) == ("email.delete_email", {"email_id": "00000479"})
    nom, args = v.parser_appel_workbench(
        'email.send_email.func(recipient="a@b.c", subject="Hi \\"x\\"", body="l1\\nl2")'
    )
    assert nom == "email.send_email"
    assert args == {"recipient": "a@b.c", "subject": 'Hi "x"', "body": "l1\nl2"}


def test_parser_appel_workbench_refuse_le_code_arbitraire():
    for mauvais in [
        "__import__('os').system('echo x')",
        'email.delete_email.func(email_id=__import__("os").getcwd())',
        'email.delete_email.func(email_id=open("/etc/passwd").read())',
        "1 + 1",
        "email.delete_email.func(",
    ]:
        with pytest.raises(ValueError):
            v.parser_appel_workbench(mauvais)


@besoin_workbench
def test_types_workbench():
    t = v.types_workbench(WORKBENCH)
    ecr = {n for n, k in t.items() if k == "write"}
    assert ecr == {
        "calendar.create_event", "calendar.delete_event", "calendar.update_event",
        "email.send_email", "email.delete_email", "email.forward_email", "email.reply_email",
        "analytics.create_plot",
        "project_management.create_task", "project_management.delete_task", "project_management.update_task",
        "customer_relationship_manager.update_customer", "customer_relationship_manager.add_customer",
        "customer_relationship_manager.delete_customer",
    }
    assert t["email.search_emails"] == "read"
    assert t["company_directory.find_email_address"] == "read"


@besoin_workbench
def test_taches_workbench_chargees_sans_eval():
    taches = v.charger_taches_workbench(WORKBENCH)
    assert len(taches) == 690
    att_ = taches["email:0"]
    assert att_[0].nom == "email.delete_email"
    assert att_[0].arguments == {"email_id": "00000479"}


def wb(tache, appels, modele="m"):
    return {"id": "w1", "tache": tache, "modele": modele, "appels": appels}


WB_TYPES = {
    "email.delete_email": "write",
    "email.send_email": "write",
    "calendar.create_event": "write",
    "email.search_emails": "read",
}
WB_ATT = {
    "email:0": [
        v.Attendue("email.delete_email", {"email_id": "00000479"}),
        v.Attendue("email.send_email", {"recipient": "a@b.c", "subject": "s", "body": "b"}),
    ]
}


def wb_verdicts(appels):
    acts = v.actions_partie_workbench(wb("email:0", appels), WB_ATT, WB_TYPES, domaine="email")
    return acts


def test_workbench_copie_exacte_est_juste():
    acts = wb_verdicts([
        {"appel": 'email.delete_email.func(email_id="00000479")', "resultat": "Email deleted successfully."},
        'email.send_email.func(recipient="a@b.c", subject="s", body="b")',
    ])
    assert [a["verdict"] for a in acts] == ["juste", "juste"]
    assert acts[0]["banc"] == "workbench" and acts[0]["domaine"] == "email" and acts[0]["tache"] == "email:0"


def test_workbench_argument_modifie_est_faux():
    acts = wb_verdicts(['email.delete_email.func(email_id="00000480")'])
    assert acts[0]["verdict"] == "fausse"


def test_workbench_ordre_libre_et_doublon():
    acts = wb_verdicts([
        'email.send_email.func(body="b", subject="s", recipient="a@b.c")',
        'email.delete_email.func(email_id="00000479")',
        'email.delete_email.func(email_id="00000479")',
    ])
    assert [a["verdict"] for a in acts] == ["juste", "juste", "doublon"]


def test_workbench_lecture_et_ecriture_hors_tache():
    acts = wb_verdicts([
        'email.search_emails.func(query="x")',
        'calendar.create_event.func(event_name="e", participant_email="a@b.c", event_start="2023-01-01 10:00:00", duration="60")',
    ])
    assert [(a["kind"], a["verdict"]) for a in acts] == [("lecture", ""), ("écriture", "fausse")]


def test_workbench_refus_par_message_d_erreur():
    acts = wb_verdicts([
        {"appel": 'email.delete_email.func(email_id="00000479")', "resultat": "Email not found."},
        {"appel": 'email.delete_email.func(email_id="00000479")', "resultat": "Email deleted successfully."},
        {"appel": 'calendar.create_event.func(event_name="e", participant_email="a@b.c", event_start="s", duration="60")', "resultat": "00000012"},
        {"appel": 'calendar.create_event.func(event_name="e", participant_email="a@b.c", event_start="s", duration="60")', "resultat": "Event duration not provided."},
    ])
    assert [a["verdict"] for a in acts] == ["refusée", "juste", "fausse", "refusée"]


def test_workbench_nombres_nombre_et_chaine():
    # les valeurs WorkBench sont des chaines ; un nombre JSON est ramene a la meme forme
    att2 = {"w:0": [v.Attendue("calendar.create_event", {"duration": "60", "event_name": "e"})]}
    types = {"calendar.create_event": "write"}
    ok = v.actions_partie_workbench(
        wb("w:0", ['calendar.create_event.func(event_name="e", duration="60")']), att2, types, domaine="calendar"
    )
    assert ok[0]["verdict"] == "juste"


@besoin_workbench
def test_workbench_copie_exacte_de_vraies_taches():
    taches = v.charger_taches_workbench(WORKBENCH)
    types = v.types_workbench(WORKBENCH)
    chaines = {}
    # relit les chaines brutes pour simuler une prediction identique au format de la colonne outcome
    import ast as _ast
    for chemin in sorted((WORKBENCH / "data/processed/tasks_and_outcomes").glob("*.csv")):
        pref = chemin.name.replace("_tasks_and_outcomes.csv", "")
        for i, ligne in enumerate(csv.DictReader(open(chemin, newline=""))):
            chaines[f"{pref}:{i}"] = _ast.literal_eval(ligne["outcome"])
    cles = ["email:0", "calendar:3", "customer_relationship_manager:7", "analytics:5", "multi_domain:11", "project_management:2"]
    for cle in cles:
        # copie exacte : tout juste
        acts = v.actions_partie_workbench(wb(cle, list(chaines[cle])), taches, types, domaine=cle.split(":")[0])
        assert [a["verdict"] for a in acts] == ["juste"] * len(chaines[cle]), cle
        # argument modifie sur la premiere : fausse
        premiere = chaines[cle][0]
        modifiee = re.sub(r'="([^"]*)"', lambda m: '="' + m.group(1) + 'Z"', premiere, count=1)
        assert modifiee != premiere
        acts = v.actions_partie_workbench(wb(cle, [modifiee] + list(chaines[cle][1:])), taches, types, domaine="x")
        assert acts[0]["verdict"] == "fausse"
        # tout en double : les doublons sont detectes
        acts = v.actions_partie_workbench(wb(cle, list(chaines[cle]) * 2), taches, types, domaine="x")
        n = len(chaines[cle])
        assert [a["verdict"] for a in acts] == ["juste"] * n + ["doublon"] * n


# --------------------------------------------------------------------------
# Dossier de parties -> CSV
# --------------------------------------------------------------------------
@besoin_tau2
def test_dossier_vers_csv(tmp_path):
    import shutil
    from verdicts_csv import main

    dossier = tmp_path / "retail"
    dossier.mkdir()
    for p in PARTIES_ISSUES:
        shutil.copy(p, dossier / p.name)
    sortie = tmp_path / "actions.csv"
    code = main(["--dossier", str(dossier), "--tau2", str(TAU2), "--sortie", str(sortie)])
    assert code == 0
    lignes = list(csv.DictReader(open(sortie, newline="", encoding="utf-8")))
    assert lignes and list(lignes[0].keys()) == v.CHAMPS
    assert {l["banc"] for l in lignes} == {"tau2"}
    assert {l["domaine"] for l in lignes} == {"retail"}
    assert any(l["verdict"] == "juste" for l in lignes)


# --------------------------------------------------------------------------
# Agent parfait : rejouer la reference elle-meme doit tout rendre « juste »
# --------------------------------------------------------------------------
@besoin_tau2
@pytest.mark.parametrize("domaine", ["airline", "retail", "banking_knowledge"])
def test_agent_parfait_toutes_taches_tau2(domaine):
    types = v.types_tau2(TAU2, domaine)
    taches = v.charger_taches_tau2(TAU2, domaine, types)
    brut = json.loads((TAU2 / f"data/tau2/domains/{domaine}/tasks.json").read_text())
    nb_ecr = 0
    for t in brut:
        msgs = []
        for i, a in enumerate(a for a in (t["evaluation_criteria"].get("actions") or []) if a.get("requestor", "assistant") != "user"):
            msgs.append({"role": "assistant", "tool_calls": [{"id": f"c{i}", "name": a["name"], "arguments": a["arguments"]}]})
            msgs.append(rep(i))
        run = {"id": "x", "task_id": t["id"], "messages": msgs}
        acts = v.actions_partie_tau2(run, taches, types, domaine=domaine)
        assert not [a for a in acts if a["kind"] == "inconnu"], t["id"]
        ecr = [a for a in acts if a["kind"] == "écriture"]
        nb_ecr += len(ecr)
        assert all(a["verdict"] == "juste" for a in ecr), (t["id"], [(a["outil"], a["verdict"]) for a in ecr])
    assert nb_ecr > 0


@besoin_workbench
def test_agent_parfait_toutes_taches_workbench_et_taches_sans_attendue():
    import ast as _ast
    taches = v.charger_taches_workbench(WORKBENCH)
    types = v.types_workbench(WORKBENCH)
    vides = 0
    for chemin in sorted((WORKBENCH / "data/processed/tasks_and_outcomes").glob("*.csv")):
        pref = chemin.name.replace("_tasks_and_outcomes.csv", "")
        for i, ligne in enumerate(csv.DictReader(open(chemin, newline=""))):
            sorties = _ast.literal_eval(ligne["outcome"])
            acts = v.actions_partie_workbench(wb(f"{pref}:{i}", sorties), taches, types)
            assert all(a["verdict"] == "juste" for a in acts), (pref, i)
            if not sorties:
                vides += 1
                # une ecriture quelconque dans une tache sans attendue est fausse
                acts = v.actions_partie_workbench(
                    wb(f"{pref}:{i}", ['email.delete_email.func(email_id="00000001")']), taches, types
                )
                assert acts[0]["verdict"] == "fausse"
    assert vides > 0


# ==========================================================================
# Correction 1 : arguments effectifs (valeurs par defaut de la signature)
# ==========================================================================
TYPES_DEF = v.TypesOutils(
    directs={
        "cancel_pending_order": "write",
        "call_discoverable_agent_tool": "write",
        "get_order_details": "read",
    },
    decouvrables={"close_bank_account_7392": "write"},
    defauts_directs={"cancel_pending_order": {"reason": "no longer needed"}},
    defauts_decouvrables={
        "close_bank_account_7392": {"reason": "Customer requested closure", "waive_early_closure_fee": False}
    },
)


def verdicts_def(run, actions_attendues, domaine="retail"):
    attendues = [v.attendue_depuis_action(a, TYPES_DEF) for a in actions_attendues]
    acts = v.actions_partie_tau2(run, {"1": attendues}, TYPES_DEF, domaine=domaine)
    return seuls_verdicts(acts)


def act(nom, args, **kw):
    return {"name": nom, "arguments": args, **kw}


def test_defaut_omis_par_l_agent_egal_a_l_attendue_donne_juste():
    run = partie(msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W1"})), rep(1))
    att_ = act("cancel_pending_order", {"order_id": "#W1", "reason": "no longer needed"})
    assert verdicts_def(run, [att_]) == ["juste"]


def test_defaut_omis_par_l_attendue_et_donne_explicitement_par_l_agent():
    run = partie(msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W1", "reason": "no longer needed"})), rep(1))
    assert verdicts_def(run, [act("cancel_pending_order", {"order_id": "#W1"})]) == ["juste"]


def test_defaut_omis_par_les_deux_est_juste():
    run = partie(msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W1"})), rep(1))
    assert verdicts_def(run, [act("cancel_pending_order", {"order_id": "#W1"})]) == ["juste"]


def test_defaut_different_de_l_attendue_donne_fausse():
    run = partie(msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W1"})), rep(1))
    att_ = act("cancel_pending_order", {"order_id": "#W1", "reason": "ordered by mistake"})
    assert verdicts_def(run, [att_]) == ["fausse"]
    # et dans l'autre sens : l'agent donne une valeur non par defaut, l'attendue omet
    run2 = partie(msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W1", "reason": "ordered by mistake"})), rep(1))
    assert verdicts_def(run2, [act("cancel_pending_order", {"order_id": "#W1"})]) == ["fausse"]


def test_defaut_ne_comble_pas_un_argument_sans_defaut():
    run = partie(msg_agent(appel(1, "cancel_pending_order", {"reason": "no longer needed"})), rep(1))
    assert verdicts_def(run, [act("cancel_pending_order", {"order_id": "#W1", "reason": "no longer needed"})]) == ["fausse"]


def test_defaut_et_compare_args_conserve():
    run = partie(msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W1", "reason": "autre"})), rep(1))
    att_ = act("cancel_pending_order", {"order_id": "#W1"}, compare_args=["order_id"])
    assert verdicts_def(run, [att_]) == ["juste"]


def test_defaut_decouvrable_banque_dans_le_json_interne():
    brut = {"agent_tool_name": "close_bank_account_7392", "arguments": '{"account_id": "a1"}'}
    explicite = {
        "agent_tool_name": "close_bank_account_7392",
        "arguments": '{"account_id": "a1", "waive_early_closure_fee": false, "reason": "Customer requested closure"}',
    }
    diff = {"agent_tool_name": "close_bank_account_7392", "arguments": '{"account_id": "a1", "waive_early_closure_fee": true}'}
    attendue = act("call_discoverable_agent_tool", brut)
    for cas, verdict in ((explicite, "juste"), (brut, "juste"), (diff, "fausse")):
        run = partie(msg_agent(appel(1, "call_discoverable_agent_tool", cas)), rep(1))
        assert verdicts_def(run, [attendue], domaine="banking_knowledge") == [verdict]


@besoin_tau2
def test_defauts_lus_par_ast_dans_le_code_du_banc():
    t = v.types_tau2(TAU2, "banking_knowledge")
    assert t.defauts_decouvrables["close_bank_account_7392"] == {
        "reason": "Customer requested closure",
        "waive_early_closure_fee": False,
    }
    assert t.defauts_decouvrables["order_replacement_credit_card_7291"] == {"expedited_shipping": False}
    assert t.defauts_decouvrables["file_credit_card_transaction_dispute_4829"] == {"partial_refund_amount": None}
    # les outils de l'utilisateur ne sont pas melanges
    assert "submit_cash_back_dispute_0589" not in t.defauts_decouvrables
    assert t.defauts_directs["call_discoverable_agent_tool"] == {"arguments": "{}"}
    # aucun outil d'ecriture de retail / airline n'a de valeur par defaut
    for dom in ("retail", "airline"):
        td = v.types_tau2(TAU2, dom)
        assert not [n for n in td.defauts_directs if td.directs[n] == "write"]


# ==========================================================================
# Correction 2 : refus de la banque ecrits en texte libre (lus par AST)
# ==========================================================================
REFUS_JSON = Path(__file__).resolve().parent.parent / "refus_banque.json"


def test_refus_banque_json_versionne_avec_origine():
    data = json.loads(REFUS_JSON.read_text(encoding="utf-8"))
    assert data["source"]["commit"].startswith("033bf08")
    assert len(data["outils"]) >= 30
    n = 0
    for outil, entrees in data["outils"].items():
        for e in entrees:
            n += 1
            assert e["fichier"].endswith("banking_knowledge/tools.py")
            assert isinstance(e["ligne"], int) and e["ligne"] > 0
            assert e["modele"]
            assert e["regle"] in {"avant-modification", "echec-ecriture", "validation-partagee"}
    assert n > 200


@besoin_tau2
def test_refus_banque_json_reproductible_depuis_le_clone():
    assert v.extraire_refus_banque(TAU2) == json.loads(REFUS_JSON.read_text(encoding="utf-8"))


@besoin_tau2
def test_refus_banque_chaque_ligne_est_un_return():
    data = json.loads(REFUS_JSON.read_text(encoding="utf-8"))
    lignes = (TAU2 / "src/tau2/domains/banking_knowledge/tools.py").read_text().splitlines()
    for outil, entrees in data["outils"].items():
        for e in entrees:
            if e["regle"] == "validation-partagee":
                continue
            assert "return" in lignes[e["ligne"] - 1], (outil, e)


def run_banque(nom_interne, args, contenu, erreur=False):
    return partie(
        msg_agent(appel(1, "call_discoverable_agent_tool", {"agent_tool_name": nom_interne, "arguments": json.dumps(args)})),
        rep(1, contenu, erreur=erreur),
    )


def verdict_banque(run):
    types = v.TypesOutils(
        directs={"call_discoverable_agent_tool": "write", "log_verification": "write", "change_user_email": "write"},
        decouvrables={
            "change_debit_card_pin_6285": "write",
            "apply_checking_account_credit_5829": "write",
            "activate_debit_card_8291": "write",
            "close_bank_account_7392": "write",
        },
    )
    return seuls_verdicts(v.actions_partie_tau2(run, {"1": []}, types, domaine="banking_knowledge"))


def test_refus_banque_pin_sequentiel_est_refusee():
    msg = "Error: PIN cannot be sequential (e.g., 1234). Please choose a more secure PIN."
    assert verdict_banque(run_banque("change_debit_card_pin_6285", {"card_id": "c"}, msg)) == ["refusée"]
    # meme texte nu (sans prefixe Error) : liste des helpers
    nu = "PIN cannot be sequential (e.g., 1234). Please choose a more secure PIN."
    assert verdict_banque(run_banque("change_debit_card_pin_6285", {"card_id": "c"}, nu)) == ["refusée"]


def test_refus_banque_activation_via_helper_partage():
    msg = "Error: Card verification failed. The last 4 digits do not match our records."
    assert verdict_banque(run_banque("activate_debit_card_8291", {"card_id": "c"}, msg)) == ["refusée"]
    msg2 = "Error: Debit card 'dc_9' is already active."
    assert verdict_banque(run_banque("activate_debit_card_8291", {"card_id": "c"}, msg2)) == ["refusée"]


def test_refus_banque_echec_apres_tentative_d_ecriture():
    run = partie(msg_agent(appel(1, "log_verification", {"user_id": "u"})), rep(1, "Failed to log verification: Record may already exist."))
    assert verdict_banque(run) == ["refusée"]


def test_refus_banque_placeholders_et_succes():
    ok = "Bank account closed successfully!\n  - Account ID: a1\n  - Account Type: checking"
    assert verdict_banque(run_banque("close_bank_account_7392", {"account_id": "a1"}, ok)) == ["fausse"]
    ref = "Error: Account balance must be $0.00 before closing. Current balance: $12.50"
    assert verdict_banque(run_banque("close_bank_account_7392", {"account_id": "a1"}, ref)) == ["refusée"]
    ref2 = "Error: Account unable to be closed."
    assert verdict_banque(run_banque("close_bank_account_7392", {"account_id": "a1"}, ref2)) == ["refusée"]


def test_refus_banque_ne_retient_pas_un_retour_apres_modification():
    data = json.loads(REFUS_JSON.read_text(encoding="utf-8"))
    # un message de succes n'est jamais dans la liste
    for entrees in data["outils"].values():
        for e in entrees:
            assert "successfully" not in e["modele"].lower() or e["modele"].startswith(("Error", "Failed"))


def test_refus_banque_texte_inconnu_n_est_pas_un_refus():
    assert verdict_banque(run_banque("apply_checking_account_credit_5829", {"amount": 3}, "Credit applied successfully!")) == ["fausse"]


# ==========================================================================
# Correction 3 : motif des « fausse » WorkBench
# ==========================================================================
WB_TYPES2 = {
    "email.send_email": "write",
    "email.reply_email": "write",
    "email.delete_email": "write",
    "calendar.create_event": "write",
    "calendar.update_event": "write",
    "project_management.update_task": "write",
    "customer_relationship_manager.update_customer": "write",
}
SEND = {"recipient": "a@b.c", "subject": "Hello", "body": "Bonjour tout le monde"}


def wb_motifs(attendues, appels):
    taches = {"x:0": attendues}
    acts = v.actions_partie_workbench(wb("x:0", appels), taches, WB_TYPES2, domaine="x")
    return [(a["verdict"], a["motif"]) for a in acts]


def test_motif_texte_libre_seulement():
    att_ = [v.Attendue("email.send_email", SEND)]
    assert wb_motifs(att_, ['email.send_email.func(recipient="a@b.c", subject="Hi", body="Salut")']) == [("fausse", "texte libre seulement")]
    assert wb_motifs(att_, ['email.send_email.func(recipient="a@b.c", subject="Hello", body="Autre")']) == [("fausse", "texte libre seulement")]


def test_motif_autre_si_un_champ_non_libre_differe():
    att_ = [v.Attendue("email.send_email", SEND)]
    assert wb_motifs(att_, ['email.send_email.func(recipient="z@b.c", subject="Hi", body="Salut")']) == [("fausse", "autre")]
    # outil different, tache sans attendue
    assert wb_motifs([], ['email.delete_email.func(email_id="1")']) == [("fausse", "autre")]
    assert wb_motifs(att_, ['email.delete_email.func(email_id="1")']) == [("fausse", "autre")]


def test_motif_champ_manquant_n_est_pas_du_texte_libre():
    att_ = [v.Attendue("email.send_email", SEND)]
    assert wb_motifs(att_, ['email.send_email.func(recipient="a@b.c", subject="Hello")']) == [("fausse", "autre")]


def test_motif_vide_pour_les_autres_verdicts():
    att_ = [v.Attendue("email.delete_email", {"email_id": "1"})]
    res = wb_motifs(att_, ['email.delete_email.func(email_id="1")', 'email.delete_email.func(email_id="1")'])
    assert res == [("juste", ""), ("doublon", "")]


def test_motif_update_depend_du_champ_modifie():
    att_ = [v.Attendue("calendar.update_event", {"event_id": "1", "field": "event_name", "new_value": "Point equipe"})]
    assert wb_motifs(att_, ['calendar.update_event.func(event_id="1", field="event_name", new_value="Reunion")']) == [("fausse", "texte libre seulement")]
    att2 = [v.Attendue("calendar.update_event", {"event_id": "1", "field": "event_start", "new_value": "2023-01-01 10:00:00"})]
    assert wb_motifs(att2, ['calendar.update_event.func(event_id="1", field="event_start", new_value="2023-01-02 10:00:00")']) == [("fausse", "autre")]
    # le champ lui-meme differe : autre
    assert wb_motifs(att_, ['calendar.update_event.func(event_id="1", field="event_start", new_value="x")']) == [("fausse", "autre")]


def test_motif_crm_notes_et_noms():
    att_ = [v.Attendue("customer_relationship_manager.update_customer", {"customer_id": "1", "field": "notes", "new_value": "a"})]
    assert wb_motifs(att_, ['customer_relationship_manager.update_customer.func(customer_id="1", field="notes", new_value="b")']) == [("fausse", "texte libre seulement")]
    att2 = [v.Attendue("customer_relationship_manager.update_customer", {"customer_id": "1", "field": "status", "new_value": "Lost"})]
    assert wb_motifs(att2, ['customer_relationship_manager.update_customer.func(customer_id="1", field="status", new_value="Won")']) == [("fausse", "autre")]


def test_motif_champs_libres_par_outil_table_justifiee():
    assert v.CHAMPS_LIBRES_WORKBENCH["email.send_email"] == ("subject", "body")
    assert v.CHAMPS_LIBRES_WORKBENCH["email.reply_email"] == ("body",)
    assert "email.forward_email" not in v.CHAMPS_LIBRES_WORKBENCH
    assert "email.delete_email" not in v.CHAMPS_LIBRES_WORKBENCH


def test_motif_vide_cote_tau2():
    run = partie(msg_agent(appel(1, "cancel_pending_order", {"order_id": "#W9", "reason": "x"})), rep(1))
    acts = verdicts_de(run, [])
    assert acts[0]["verdict"] == "fausse" and acts[0]["motif"] == ""


@besoin_workbench
def test_motif_champs_libres_ne_sont_pas_des_champs_a_valeurs_controlees():
    """Justification lue dans le code WorkBench : chaque champ libre est stocke tel quel, sans validation
    contre une liste ; les champs non libres (status, board, list, email...) sont valides ou structurés."""
    src = WORKBENCH / "src" / "tools"
    pm = (src / "project_management.py").read_text()
    crm = (src / "customer_relationship_manager.py").read_text()
    cal = (src / "calendar.py").read_text()
    em = (src / "email.py").read_text()
    # les listes de valeurs valides existent pour les champs que l'on exclut des champs libres
    assert "VALID_STATUSES" in crm and "VALID_PRODUCT_INTERESTS" in crm
    assert "VALID_BOARDS" in pm and "VALID_LISTS" in pm
    assert "event_name" in cal and "subject" in em and "body" in em


# ==========================================================================
# Correction 4 : adaptateur des fichiers du pilote WorkBench
# ==========================================================================
FIXT = Path(__file__).resolve().parent / "fixtures" / "pilote_workbench" / "mini_email"
TEXTES = {
    "email:0": "Delete my last email from nadia",
    "email:1": "Delete my last email from sofia",
    "email:2": "Delete my last email from anaya",
}
WB_ATT_P = {
    "email:0": [v.Attendue("email.delete_email", {"email_id": "00000479"})],
    "email:1": [v.Attendue("email.delete_email", {"email_id": "00000438"})],
    "email:2": [v.Attendue("email.delete_email", {"email_id": "00000166"})],
}
TYPES_P = {"email.delete_email": "write", "company_directory.find_email_address": "read"}


def ecrire_csv_pandas(chemin, lignes):
    """Meme ecriture que DataFrame.to_csv(index=False, quoting=QUOTE_ALL) : une liste est ecrite par str()."""
    with open(chemin, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL, lineterminator="\n")
        w.writerow(["task", "function_calls", "full_response", "error"])
        for l in lignes:
            w.writerow([l["task"], str(l["function_calls"]), l["full_response"], l["error"]])


def ecrire_pilote(dossier, nom, taches, modele="claude-sonnet-5-5", meta=True, traces=True):
    """Ecrit trois fichiers au format exact de WorkBench src/evals/inference.py.
    taches : liste de (texte, [(action, input, observation)], erreur)."""
    dossier.mkdir(parents=True, exist_ok=True)
    base = dossier / f"{modele}_all_2026-11-05_10-00-00"
    lignes, trs = [], []
    for texte, etapes, erreur in taches:
        fc = [f"{a}.func(" + ", ".join(f'{k}="{val}"' for k, val in i.items()) + ")" for a, i, _ in etapes]
        lignes.append({"task": texte, "function_calls": fc, "full_response": "AgentResult(...)", "error": erreur})
        steps = [
            {"llm_input": "x", "llm_output": "y", "action": a, "action_input": i, "observation": o} for a, i, o in etapes
        ]
        steps.append({"llm_input": "x", "llm_output": "z", "action": "Final Answer", "action_input": "fini", "observation": ""})
        trs.append({"task": texte, "steps": steps})
    ecrire_csv_pandas(str(base) + ".csv", lignes)
    if traces:
        (Path(str(base) + "_traces.json")).write_text(json.dumps(trs, indent=2))
    if meta:
        (Path(str(base) + "_meta.json")).write_text(json.dumps({"model_name": modele, "tasks_path": "mini_email_tasks_and_outcomes.csv"}))
    return Path(str(base) + ".csv")


@besoin_workbench
def test_pilote_fixture_hors_ligne_convertie():
    parties = list(v.parties_depuis_pilote_workbench(FIXT / "claude-haiku-5-5_all_2026-11-05_06-36-02.csv", v.charger_textes_workbench(WORKBENCH)))
    assert [p["tache"] for p in parties] == ["email:0", "email:1", "email:2"]
    assert {p["modele"] for p in parties} == {"claude-haiku-5-5"}
    p = parties[0]
    assert p["appels"] == [
        {"appel": 'company_directory.find_email_address.func(name="nadia")', "resultat": '["nadia.moreau@atlas.com"]'}
    ]
    assert p["id"].startswith("claude-haiku-5-5_all_2026-11-05_06-36-02")


@besoin_workbench
def test_pilote_fixture_react_et_structure_donnent_le_meme_format():
    textes = v.charger_textes_workbench(WORKBENCH)
    react = list(v.parties_depuis_pilote_workbench(FIXT / "claude-haiku-5-5_all_2026-11-05_06-36-00.csv", textes))
    struct = list(v.parties_depuis_pilote_workbench(FIXT / "claude-haiku-5-5_all_2026-11-05_06-36-02.csv", textes))
    assert [p["appels"] for p in react] == [p["appels"] for p in struct]


def test_pilote_synthetique_ecritures_resultats_et_verdicts(tmp_path):
    csv_ = ecrire_pilote(
        tmp_path / "email",
        "x",
        [
            ("Delete my last email from nadia", [("email.delete_email", {"email_id": "00000479"}, "Email deleted successfully.")], ""),
            (
                "Delete my last email from sofia",
                [
                    ("company_directory.find_email_address", {"name": "sofia"}, '["sofia@atlas.com"]'),
                    ("email.delete_email", {"email_id": "00000438"}, "Email not found."),
                    ("email.delete_email", {"email_id": "00000438"}, "Email deleted successfully."),
                    ("email.delete_email", {"email_id": "00000438"}, "Email deleted successfully."),
                    ("email.delete_email", {"email_id": "00000999"}, "Email deleted successfully."),
                ],
                "",
            ),
            ("Delete my last email from anaya", [], "Context window exceeded"),
        ],
    )
    parties = list(v.parties_depuis_pilote_workbench(csv_, TEXTES))
    assert [p["tache"] for p in parties] == ["email:0", "email:1", "email:2"]
    assert parties[0]["modele"] == "claude-sonnet-5-5"
    assert parties[2]["appels"] == []
    acts = []
    for p in parties:
        acts += v.actions_partie_workbench(p, WB_ATT_P, TYPES_P)
    assert [(a["tache"], a["outil"], a["kind"], a["verdict"]) for a in acts] == [
        ("email:0", "email.delete_email", "écriture", "juste"),
        ("email:1", "company_directory.find_email_address", "lecture", ""),
        ("email:1", "email.delete_email", "écriture", "refusée"),
        ("email:1", "email.delete_email", "écriture", "juste"),
        ("email:1", "email.delete_email", "écriture", "doublon"),
        ("email:1", "email.delete_email", "écriture", "fausse"),
    ]
    assert {a["modele"] for a in acts} == {"claude-sonnet-5-5"}


def test_pilote_arguments_avec_guillemets_et_retours_a_la_ligne(tmp_path):
    appel_ = 'email.send_email.func(recipient="a@b.c", subject="Il dit \\"oui\\"", body="l1\\nl2")'
    base = tmp_path / "m_all_2026-01-01_00-00-00"
    ecrire_csv_pandas(str(base) + ".csv", [{"task": "T", "function_calls": [appel_], "full_response": "", "error": ""}])
    p = list(v.parties_depuis_pilote_workbench(Path(str(base) + ".csv"), {"email:7": "T"}))[0]
    assert p["tache"] == "email:7" and p["modele"] == "m"
    assert p["appels"] == [{"appel": appel_, "resultat": None}]  # sans traces : pas de resultat
    nom, args = v.parser_appel_workbench(appel_)
    assert args == {"recipient": "a@b.c", "subject": 'Il dit "oui"', "body": "l1\nl2"}


def test_pilote_texte_de_tache_inconnu_leve_une_erreur(tmp_path):
    csv_ = ecrire_pilote(tmp_path, "x", [("Une tache qui n'existe pas", [], "")])
    with pytest.raises(ValueError):
        list(v.parties_depuis_pilote_workbench(csv_, TEXTES))


def test_pilote_texte_duplique_choisit_selon_le_prefixe_du_fichier_de_taches(tmp_path):
    textes = {"email:0": "Doublon", "calendar:5": "Doublon"}
    csv_ = ecrire_pilote(tmp_path, "x", [("Doublon", [], "")])  # meta : tasks_path=mini_email_...
    p = list(v.parties_depuis_pilote_workbench(csv_, textes))[0]
    assert p["tache"] == "email:0"


def test_pilote_traces_desalignees_ne_donnent_pas_de_resultat(tmp_path):
    csv_ = ecrire_pilote(tmp_path, "x", [("Delete my last email from nadia", [("email.delete_email", {"email_id": "1"}, "Email deleted successfully.")], "")])
    tr = Path(str(csv_)[:-4] + "_traces.json")
    data = json.loads(tr.read_text())
    data[0]["steps"] = data[0]["steps"][1:]  # plus aucune etape d'outil
    tr.write_text(json.dumps(data))
    p = list(v.parties_depuis_pilote_workbench(csv_, TEXTES))[0]
    assert p["appels"][0]["resultat"] is None


def test_pilote_sans_meta_modele_deduit_du_nom_de_fichier(tmp_path):
    csv_ = ecrire_pilote(tmp_path, "x", [("Delete my last email from nadia", [], "")], modele="claude-opus-5-5", meta=False)
    p = list(v.parties_depuis_pilote_workbench(csv_, TEXTES))[0]
    assert p["modele"] == "claude-opus-5-5"


@besoin_workbench
def test_dossier_pilote_workbench_vers_csv(tmp_path):
    import shutil
    from verdicts_csv import main

    dossier = tmp_path / "wb" / "mini_email"
    dossier.mkdir(parents=True)
    for f in FIXT.iterdir():
        shutil.copy(f, dossier / f.name)  # csv + _meta.json + _traces.json : les json annexes sont ignores
    sortie = tmp_path / "actions.csv"
    code = main(["--dossier", str(tmp_path / "wb"), "--workbench", str(WORKBENCH), "--sortie", str(sortie)])
    assert code == 0
    lignes = list(csv.DictReader(open(sortie, newline="", encoding="utf-8")))
    assert len(lignes) == 6  # 2 fichiers x 3 taches, une lecture chacune
    assert {l["banc"] for l in lignes} == {"workbench"} and {l["kind"] for l in lignes} == {"lecture"}
    assert {l["modele"] for l in lignes} == {"claude-haiku-5-5"}
    assert list(lignes[0].keys()) == v.CHAMPS


def test_donner_outil_au_client_est_une_ecriture_jugee():
    """D7 (REGLE.md, 5 novembre) : give_discoverable_user_tool est une écriture réversible, jugée contre l'attendu."""
    import verdicts as v
    types = v.TypesOutils(directs={"give_discoverable_user_tool": "generic"}, decouvrables={})
    assert v._kind_tau2("give_discoverable_user_tool", types, enveloppe=False) == v.ECRITURE
    assert v._kind_tau2("unlock_discoverable_agent_tool", v.TypesOutils(directs={"unlock_discoverable_agent_tool": "generic"},
                                                                          decouvrables={}), enveloppe=False) == v.AUTRE


def test_donner_outil_compare_seulement_le_nom_de_l_outil():
    """L'argument « arguments » de give_discoverable_user_tool n'est pas enregistré en base : seul le nom compte."""
    import verdicts as v
    att = v.attendue_depuis_action({"name": "give_discoverable_user_tool",
                                    "arguments": {"discoverable_tool_name": "submit_cash_back_dispute_0589"}})
    assert att.compare_args == ("discoverable_tool_name",)
    att2 = v.attendue_depuis_action({"name": "give_discoverable_user_tool",
                                     "arguments": {"discoverable_tool_name": "x"}, "compare_args": ["discoverable_tool_name", "arguments"]})
    assert att2.compare_args == ("discoverable_tool_name", "arguments")


# --------------------------------------------------------------------------
# payment_id sans paiement enregistré (aviation ; constat du pilote, tâche 21)
# --------------------------------------------------------------------------
TYPES_AVIATION = v.TypesOutils(
    directs={"get_reservation_details": "read", "update_reservation_baggages": "write",
             "update_reservation_flights": "write"},
    decouvrables={},
)
BAG_ATT = {"reservation_id": "ABC123", "total_baggages": 2, "nonfree_baggages": 0, "payment_id": "gift_card_X"}
BAG_AGENT = {**BAG_ATT, "payment_id": "gift_card_Y"}
VOLS_ATT = {"reservation_id": "ABC123", "cabin": "economy",
            "flights": [{"flight_number": "HAT1", "date": "2024-05-20"}], "payment_id": "gift_card_X"}


def resa(nb_paiements, rid="ABC123"):
    hist = [{"payment_id": f"gift_card_{i}", "amount": 100 + i} for i in range(nb_paiements)]
    return json.dumps({"reservation_id": rid, "payment_history": hist})


def verdicts_aviation(run, attendues, types=TYPES_AVIATION):
    acts = verdicts_de(run, attendues, types=types, domaine="airline")
    return [(a["verdict"], a["motif"]) for a in acts if a["kind"] == "écriture"]


def test_payment_id_ignore_si_aucun_paiement_enregistre():
    run = partie(
        msg_agent(appel(1, "get_reservation_details", {"reservation_id": "ABC123"})), rep(1, resa(2)),
        msg_agent(appel(2, "update_reservation_baggages", BAG_AGENT)), rep(2, resa(2)),
    )
    assert verdicts_aviation(run, [att("update_reservation_baggages", BAG_ATT)]) == [("juste", v.MOTIF_PAIEMENT_SANS_EFFET)]


def test_payment_id_compare_si_un_paiement_est_enregistre():
    run = partie(
        msg_agent(appel(1, "get_reservation_details", {"reservation_id": "ABC123"})), rep(1, resa(2)),
        msg_agent(appel(2, "update_reservation_baggages", BAG_AGENT)), rep(2, resa(3)),
    )
    assert verdicts_aviation(run, [att("update_reservation_baggages", BAG_ATT)]) == [("fausse", "")]


def test_payment_id_compare_si_l_etat_d_avant_est_inconnu():
    run = partie(msg_agent(appel(1, "update_reservation_baggages", BAG_AGENT)), rep(1, resa(2)))
    assert verdicts_aviation(run, [att("update_reservation_baggages", BAG_ATT)]) == [("fausse", "")]


def test_payment_id_etat_initial_de_la_base():
    types = v.TypesOutils(directs=TYPES_AVIATION.directs, decouvrables={}, paiements_initiaux={"ABC123": 2})
    run = partie(msg_agent(appel(1, "update_reservation_baggages", BAG_AGENT)), rep(1, resa(2)))
    assert verdicts_aviation(run, [att("update_reservation_baggages", BAG_ATT)], types) == [("juste", v.MOTIF_PAIEMENT_SANS_EFFET)]


def test_payment_id_suit_les_ecritures_precedentes():
    """Cas du pilote (tâche 21) : le changement de vols crée un paiement, l'ajout de bagages gratuits n'en crée pas."""
    run = partie(
        msg_agent(appel(1, "get_reservation_details", {"reservation_id": "ABC123"})), rep(1, resa(1)),
        msg_agent(appel(2, "update_reservation_flights", VOLS_ATT)), rep(2, resa(2)),
        msg_agent(appel(3, "update_reservation_baggages", BAG_AGENT)), rep(3, resa(2)),
    )
    attendues = [att("update_reservation_flights", VOLS_ATT), att("update_reservation_baggages", BAG_ATT)]
    assert verdicts_aviation(run, attendues) == [("juste", ""), ("juste", v.MOTIF_PAIEMENT_SANS_EFFET)]


def test_payment_id_changement_de_vols_avec_paiement_reste_compare():
    run = partie(
        msg_agent(appel(1, "get_reservation_details", {"reservation_id": "ABC123"})), rep(1, resa(1)),
        msg_agent(appel(2, "update_reservation_flights", {**VOLS_ATT, "payment_id": "gift_card_Y"})), rep(2, resa(2)),
    )
    assert verdicts_aviation(run, [att("update_reservation_flights", VOLS_ATT)]) == [("fausse", "")]


def test_payment_id_ignore_ne_couvre_pas_les_autres_arguments():
    run = partie(
        msg_agent(appel(1, "get_reservation_details", {"reservation_id": "ABC123"})), rep(1, resa(2)),
        msg_agent(appel(2, "update_reservation_baggages", {**BAG_AGENT, "total_baggages": 3})), rep(2, resa(2)),
    )
    assert verdicts_aviation(run, [att("update_reservation_baggages", BAG_ATT)]) == [("fausse", "")]


def test_payment_id_motif_vide_si_le_moyen_de_paiement_est_le_meme():
    run = partie(
        msg_agent(appel(1, "get_reservation_details", {"reservation_id": "ABC123"})), rep(1, resa(2)),
        msg_agent(appel(2, "update_reservation_baggages", BAG_ATT)), rep(2, resa(2)),
    )
    assert verdicts_aviation(run, [att("update_reservation_baggages", BAG_ATT)]) == [("juste", "")]


def test_payment_id_ecriture_refusee_reste_refusee():
    run = partie(
        msg_agent(appel(1, "get_reservation_details", {"reservation_id": "ABC123"})), rep(1, resa(2)),
        msg_agent(appel(2, "update_reservation_baggages", BAG_AGENT)), rep(2, "Error: Payment method not found", erreur=True),
    )
    assert verdicts_aviation(run, [att("update_reservation_baggages", BAG_ATT)]) == [("refusée", "")]


def test_payment_id_autre_reservation_n_utilise_pas_le_meme_etat():
    run = partie(
        msg_agent(appel(1, "get_reservation_details", {"reservation_id": "ZZZ999"})), rep(1, resa(2, rid="ZZZ999")),
        msg_agent(appel(2, "update_reservation_baggages", BAG_AGENT)), rep(2, resa(2)),
    )
    assert verdicts_aviation(run, [att("update_reservation_baggages", BAG_ATT)]) == [("fausse", "")]


AVIATION_REELLE = Path(__file__).resolve().parents[2] / "externe" / "tau2-bench"


@pytest.mark.skipif(not AVIATION_REELLE.is_dir(), reason="clone tau-bench absent")
def test_paiements_initiaux_lus_dans_la_base_aviation():
    types = v.types_tau2(AVIATION_REELLE, "airline")
    assert types.paiements_initiaux["OBUT9V"] == 1
    assert v.types_tau2(AVIATION_REELLE, "retail").paiements_initiaux == {}


@pytest.mark.skipif(not AVIATION_REELLE.is_dir(), reason="clone tau-bench absent")
def test_aucune_tache_aviation_ne_modifie_l_etat_initial():
    """L'état initial lu dans db.json n'est exact que si aucune tâche n'a d'initial_state."""
    taches = json.loads((AVIATION_REELLE / "data/tau2/domains/airline/tasks.json").read_text(encoding="utf-8"))
    assert not [t["id"] for t in taches if t.get("initial_state")]
