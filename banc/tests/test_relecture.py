"""Tests de l'outil de relecture des alertes (banc/relecture/). Données synthétiques, puis vraies sorties du pilote."""
import csv
import json
import random
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "banc" / "relecture"))

import accord  # noqa: E402
import decisions  # noqa: E402
import fiches  # noqa: E402
import tirage_aveugle as tirage  # noqa: E402

MODELE = "anthropic/claude-haiku-5-5"
CHAMPS = ["partie", "tache", "rang", "banc", "domaine", "outil", "arguments", "kind", "verdict", "modele", "motif",
          "resultat", "type", "enjeu", "plafonnee", "montant", "raison", "etiquettes"]
JETONS = ("claude", "haiku", "sonnet", "opus", "anthropic", "openai", "gpt", "gemini")


def ligne(**kw):
    base = {c: "" for c in CHAMPS}
    base.update(banc="tau2", domaine="airline", kind="écriture", modele=MODELE, enjeu="faible", type="écriture durable")
    base.update(kw)
    return base


def ecrire_csv(chemin, lignes):
    with open(chemin, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CHAMPS)
        w.writeheader()
        w.writerows(lignes)


def pilote_tau2(tmp_path, n_filler=20):
    """Une partie aviation : 20 messages de remplissage, une lecture (rang 0), une écriture fausse (rang 1)."""
    msgs, t = [], 0
    for k in range(n_filler):
        role = "user" if k % 2 else "assistant"
        texte = f"message {k:02d}" + (" je suis claude-haiku-5-5 d'anthropic" if k == n_filler - 1 else "")
        msgs.append({"role": role, "content": texte, "tool_calls": None, "turn_idx": t})
        t += 1
    msgs.append({"role": "assistant", "content": "", "turn_idx": t, "tool_calls": [
        {"id": "c1", "name": "get_user_details", "arguments": {"user_id": "u1"}, "requestor": "assistant"}]})
    msgs.append({"role": "tool", "id": "c1", "content": "{\"user_id\": \"u1\"}", "turn_idx": t + 1, "tool_calls": None})
    msgs.append({"role": "assistant", "content": "Je modifie vos bagages.", "turn_idx": t + 2, "tool_calls": [
        {"id": "c2", "name": "update_reservation_baggages",
         "arguments": {"reservation_id": "R1", "total_baggages": 2, "nonfree_baggages": 0, "payment_id": "gift_card_B"},
         "requestor": "assistant"}]})
    msgs.append({"role": "tool", "id": "c2", "content": "{\"reservation_id\": \"R1\", \"ok\": true}", "turn_idx": t + 3, "tool_calls": None})
    tache = {"id": "21", "description": {"purpose": "p"},
             "user_scenario": {"instructions": {"reason_for_call": "SCENARIO_COMPLET_ICI", "task_instructions": "Use gift_card_A."}},
             "evaluation_criteria": {"actions": [{"action_id": "21_1", "requestor": "assistant", "name": "update_reservation_baggages",
                                                  "arguments": {"reservation_id": "R1", "payment_id": "gift_card_A"},
                                                  "info": None, "compare_args": ["payment_id"]}]}}
    policy = ("# Airline Policy\n\n## Bags\n\nUse update_reservation_baggages only with the payment the user chose.\n\n"
              "## Other\n\nParagraphe sans rapport.\n")
    run = {"id": "sim-1", "task_id": "21", "messages": msgs, "policy": policy}
    info = {"environment_info": {"domain_name": "airline"}, "agent_info": {"llm": MODELE}}
    d = tmp_path / "pilote"
    (d / "parties" / "tau2-aviation-1").mkdir(parents=True)
    (d / "parties" / "tau2-aviation-1" / "results.json").write_text(json.dumps({"info": info, "tasks": [tache], "simulations": [run]}))
    ecrire_csv(d / "actions_typees.csv", [
        ligne(partie="sim-1", tache="21", rang="0", outil="get_user_details", kind="lecture", arguments="{\"user_id\": \"u1\"}"),
        ligne(partie="sim-1", tache="21", rang="1", outil="update_reservation_baggages", verdict="fausse", enjeu="moyen",
              arguments=json.dumps({"reservation_id": "R1", "total_baggages": 2, "nonfree_baggages": 0, "payment_id": "gift_card_B"}),
              resultat="{\"reservation_id\": \"R1\", \"ok\": true}"),
        ligne(partie="sim-1", tache="21", rang="2", outil="update_reservation_baggages", verdict="juste"),
    ])
    return d


def pilote_workbench(tmp_path):
    stem = "claude-haiku-5-5_all_2026-11-05_07-26-50"
    d = tmp_path / "pilote_wb"
    (d / "parties" / "workbench-WorkBench-1").mkdir(parents=True)
    (d / "taches" / "WorkBench-1").mkdir(parents=True)
    tache = "Delete my last email from nadia"
    calls = ["email.search_emails.func(query=\"nadia\")", "email.delete_email.func(email_id=\"00000001\")"]
    with open(d / "parties" / "workbench-WorkBench-1" / f"{stem}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["task", "function_calls", "full_response", "error"])
        w.writeheader()
        w.writerow({"task": tache, "function_calls": repr(calls), "full_response": "x", "error": ""})
    steps = [
        {"llm_output": json.dumps({"content": "Je cherche (claude)"}), "action": "email.search_emails",
         "action_input": {"query": "nadia"}, "observation": "[{\"email_id\": \"00000479\"}]"},
        {"llm_output": json.dumps({"content": ""}), "action": "email.delete_email",
         "action_input": {"email_id": "00000001"}, "observation": "Email deleted successfully."},
        {"llm_output": "{}", "action": "Final Answer", "action_input": "ok", "observation": ""},
    ]
    (d / "parties" / "workbench-WorkBench-1" / f"{stem}_traces.json").write_text(json.dumps([{"task": tache, "steps": steps}]))
    with open(d / "taches" / "WorkBench-1" / "email_tasks_and_outcomes.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["task", "outcome"])
        w.writerow([tache, "['email.delete_email.func(email_id=\"00000479\")']"])
    ecrire_csv(d / "actions_typees.csv", [
        ligne(banc="workbench", domaine="email", partie=f"{stem}:0", tache="email:3", rang="1", outil="email.delete_email",
              verdict="refusée", modele="claude-haiku-5-5", arguments=json.dumps({"email_id": "00000001"}),
              resultat="Email deleted successfully."),
    ])
    return d


# ---------------------------------------------------------------------------
# fiches.py
# ---------------------------------------------------------------------------
def test_alertes_seulement_ecritures_fausse_doublon_refusee(tmp_path):
    d = pilote_tau2(tmp_path)
    rows = [ligne(partie="p", tache="1", rang=str(i), outil="o", verdict=v, kind=k)
            for i, (v, k) in enumerate([("juste", "écriture"), ("fausse", "écriture"), ("doublon", "écriture"),
                                        ("refusée", "écriture"), ("", "lecture"), ("fausse", "lecture")])]
    ecrire_csv(d / "actions_typees.csv", rows)
    assert [a["verdict"] for a in fiches.lire_alertes(d)] == ["fausse", "doublon", "refusée"]


def test_identifiant_stable_sans_modele():
    """Contrôle 1, C11 : l'identifiant est vu par les relecteurs ; il ne montre ni modèle, ni partie, ni rang, ni tâche."""
    l = ligne(partie="claude-haiku-5-5_all_2026-11-05_07-26-50:0", tache="email:3", rang="1", banc="workbench", domaine="email")
    a = fiches.alerte_id(l)
    assert a == fiches.alerte_id(dict(l))
    assert not fiches.contient_modele(a, {l["partie"]})
    assert a.startswith("workbench-") and len(a) == len("workbench-") + 12
    assert "email" not in a and "r1" not in a and "2026" not in a
    # opaque mais distinct : un autre rang, une autre partie ou une autre tâche donnent un autre identifiant
    assert fiches.alerte_id(dict(l, rang="2")) != a
    assert fiches.alerte_id(dict(l, partie="claude-haiku-5-5_all_2026-11-05_07-26-50:1")) != a
    assert fiches.alerte_id(dict(l, tache="email:4")) != a


def test_fiche_claude_complete(tmp_path):
    d = pilote_tau2(tmp_path)
    res = fiches.produire(d, tau2=tmp_path / "absent")
    assert len(res) == 1
    f = json.loads((d / "relecture" / "fiches" / "claude" / f"{res[0]['id']}.json").read_text())
    # contrôle 1, C11 : modèle et tâche ne sont plus dans la fiche de Claude, seulement dans la correspondance
    assert res[0]["modele"] == MODELE and res[0]["tache"] == "21"
    assert "modele" not in f and "tache" not in f and f["id"] == res[0]["id"]
    assert f["verdict_automatique"] == "fausse" and f["environnement"] == "aviation"
    assert "SCENARIO_COMPLET_ICI" in f["consigne"] and "Use gift_card_A." in f["consigne"]
    assert "\"compare_args\"" in f["attendues"] and "gift_card_A" in f["attendues"]
    assert f["ecriture"]["outil"] == "update_reservation_baggages" and "gift_card_B" in f["ecriture"]["arguments"]
    assert f["ecriture"]["message_agent"] == "Je modifie vos bagages."
    assert "\"ok\": true" in f["resultat"]
    assert f["avertissements"] == []


def test_conversation_entiere_avec_locuteur_et_action_signalee(tmp_path):
    """Décidé le 05/11 : la fiche montre la conversation entière (avant : les 12 derniers messages avant l'écriture)."""
    d = pilote_tau2(tmp_path)
    res = fiches.produire(d, tau2=tmp_path / "absent")
    f = json.loads((d / "relecture" / "fiches" / "claude" / f"{res[0]['id']}.json").read_text())
    conv = f["conversation"]
    assert len(conv) == 24  # 20 de remplissage + lecture + résultat + écriture + résultat
    assert conv[0]["texte"].startswith("message 00")
    assert conv[-1]["role"] == "outil" and "ok" in conv[-1]["texte"]
    assert conv[-2]["role"] == "agent" and "update_reservation_baggages" in conv[-2]["texte"]
    assert conv[19]["role"] == "client" and conv[19]["texte"].startswith("message 19")
    assert fiches.MASQUE in conv[19]["texte"]  # masqué dans la fiche de Claude aussi (contrôle 1, C11)
    assert {m["role"] for m in conv} <= {"agent", "client", "outil"}
    # une seule ligne porte la marque de l'action signalée : celle de l'écriture, pas la lecture
    marques = [k for k, m in enumerate(conv) if fiches.MARQUE_SIGNALE in m["texte"]]
    assert marques == [22] and [k for k, m in enumerate(conv) if m["signale"]] == [22]


def test_reglement_chemin_et_paragraphes_de_l_outil(tmp_path):
    d = pilote_tau2(tmp_path)
    res = fiches.produire(d, tau2=RACINE / "externe" / "tau2-bench")
    f = json.loads((d / "relecture" / "fiches" / "claude" / f"{res[0]['id']}.json").read_text())
    r = f["reglement"]
    assert r["chemin"].endswith("domains/airline/policy.md")
    assert r["recherche"] == "nom de l'outil"
    textes = [p["texte"] for p in r["paragraphes"]]
    assert any("update_reservation_baggages" in t for t in textes)
    assert not any("sans rapport" in t for t in textes)


def test_reglement_recherche_elargie_et_aucune():
    texte = "# P\n\nChange baggage and insurance.\n\nAutre chose."
    paras, mode = fiches.paragraphes_outil(texte, "update_reservation_baggages")
    assert [p["texte"] for p in paras] == ["Change baggage and insurance."] and "mots" in mode
    paras, mode = fiches.paragraphes_outil(texte, "zzz_outil_inconnu")
    assert paras == [] and "aucun" in mode


def test_version_aveugle_sans_modele_nulle_part(tmp_path):
    d = pilote_tau2(tmp_path)
    res = fiches.produire(d, tau2=tmp_path / "absent")
    i = res[0]["id"]
    aveugle = d / "relecture" / "fiches" / "aveugle"
    for fichier in aveugle.iterdir():
        assert not fiches.contient_modele(fichier.name, {MODELE, "claude-haiku-5-5"})
        contenu = fichier.read_text(encoding="utf-8").lower()
        assert not any(j in contenu for j in JETONS), fichier.name
    for parent in aveugle.resolve().parents[:3]:
        assert not any(j in str(parent.name).lower() for j in JETONS if parent != tmp_path.parent)
    md = (aveugle / f"{i}.md").read_text(encoding="utf-8")
    assert fiches.MASQUE in md  # le message qui nommait le modèle est masqué, pas supprimé
    # contrôle 1, C11 : la version Claude est aveugle elle aussi ; le modèle n'est que dans la correspondance
    for fichier in (d / "relecture" / "fiches" / "claude").iterdir():
        assert not any(j in fichier.read_text(encoding="utf-8").lower() for j in JETONS), fichier.name
    assert MODELE in (d / "relecture" / "alertes.json").read_text(encoding="utf-8")


def test_masquage_noms():
    t = fiches.masquer({"a": ["gpt-4o et openai/gpt-5 puis Anthropic/Claude-Opus-4", "RAS"]}, {"mon-modele-x"})
    s = json.dumps(t)
    assert not fiches.contient_modele(s)
    assert fiches.masquer("utilise mon-modele-x ici", {"mon-modele-x"}) == f"utilise {fiches.MASQUE} ici"
    assert fiches.masquer("texte neutre") == "texte neutre"


def test_fiche_workbench(tmp_path):
    d = pilote_workbench(tmp_path)
    res = fiches.produire(d, tau2=tmp_path / "absent")
    assert res[0]["environnement"] == "WorkBench" and res[0]["verdict"] == "refusée"
    f = json.loads((d / "relecture" / "fiches" / "claude" / f"{res[0]['id']}.json").read_text())
    assert f["consigne"] == "Delete my last email from nadia"
    assert "00000479" in f["attendues"]
    assert f["ecriture"]["outil"] == "email.delete_email"
    # conversation entière : consigne, lecture + résultat, écriture signalée + résultat, réponse finale
    assert [m["role"] for m in f["conversation"]] == ["client", "agent", "outil", "agent", "outil", "agent"]
    assert [m["signale"] for m in f["conversation"]] == [False, False, False, True, False, False]
    assert fiches.MARQUE_SIGNALE in f["conversation"][3]["texte"]
    assert "WorkBench n'a pas de règlement" in f["reglement"]["note"]
    b = (d / "relecture" / "fiches" / "aveugle" / f"{res[0]['id']}.json").read_text(encoding="utf-8").lower()
    assert not any(j in b for j in JETONS)
    assert "_all_2026" not in b  # identifiant de partie (qui contient le modèle) absent


def test_fiches_ne_remplit_aucune_decision(tmp_path):
    d = pilote_tau2(tmp_path)
    fiches.produire(d, tau2=tmp_path / "absent")
    modele = (d / "relecture" / "decisions_modele.csv").read_text(encoding="utf-8").strip()
    assert modele == ",".join(decisions.COLONNES)


# ---------------------------------------------------------------------------
# decisions.py
# ---------------------------------------------------------------------------
def ecrire_decisions(chemin, lignes):
    with open(chemin, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=decisions.COLONNES)
        w.writeheader()
        for l in lignes:
            w.writerow({**{c: "" for c in decisions.COLONNES}, **l})


def test_modele_vide_lisible(tmp_path):
    decisions.ecrire_modele(tmp_path / "m.csv")
    assert decisions.lire(tmp_path / "m.csv") == {}


def test_decision_valide(tmp_path):
    ecrire_decisions(tmp_path / "d.csv", [
        {"alerte_id": "A", "decision": "levée", "motif": "c", "justification": "autre carte permise", "preuve": "policy L95"},
        {"alerte_id": "B", "decision": "Confirmee", "justification": "mauvaise carte"},
    ])
    reg = decisions.lire(tmp_path / "d.csv", ids_attendus=["A", "B"])
    assert reg["A"]["decision"] == "levée" and reg["B"]["decision"] == "confirmée" and reg["B"]["motif"] == ""


@pytest.mark.parametrize("ligne_, attendu", [
    ({"alerte_id": "A", "decision": "levée", "justification": "j", "preuve": "p"}, "motif obligatoire"),
    ({"alerte_id": "A", "decision": "confirmée", "motif": "a", "justification": "j"}, "motif interdit"),
    ({"alerte_id": "A", "decision": "levée", "motif": "e", "justification": "j", "preuve": "p"}, "motif inconnu"),
    ({"alerte_id": "A", "decision": "peut-être", "justification": "j"}, "décision inconnue"),
    ({"alerte_id": "A", "decision": "levée", "motif": "a", "justification": "j"}, "preuve obligatoire"),
    ({"alerte_id": "A", "decision": "confirmée"}, "justification vide"),
    # relecture C13, P9 : le cas du motif a ouvre la preuve (CONSIGNE_RELECTURE.md)
    ({"alerte_id": "A", "decision": "levée", "motif": "a", "justification": "j", "preuve": "policy L12"}, "a1 à a4"),
    ({"alerte_id": "A", "decision": "levée", "motif": "a", "justification": "j", "preuve": "a5 : x"}, "a1 à a4"),
])
def test_decision_invalide(tmp_path, ligne_, attendu):
    ecrire_decisions(tmp_path / "d.csv", [ligne_])
    with pytest.raises(decisions.DecisionInvalide, match=attendu):
        decisions.lire(tmp_path / "d.csv")


def test_decisions_doublon_manquante_et_inconnue(tmp_path):
    l = {"decision": "confirmée", "justification": "j"}
    ecrire_decisions(tmp_path / "d.csv", [{"alerte_id": "A", **l}, {"alerte_id": "A", **l}, {"alerte_id": "Z", **l}])
    with pytest.raises(decisions.DecisionInvalide) as e:
        decisions.lire(tmp_path / "d.csv", ids_attendus=["A", "B"])
    m = str(e.value)
    assert "en double" in m and "B sans décision" in m and "inconnue : Z" in m


def test_decisions_mauvais_entete(tmp_path):
    (tmp_path / "d.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    with pytest.raises(decisions.DecisionInvalide, match="en-tête"):
        decisions.lire(tmp_path / "d.csv")


# ---------------------------------------------------------------------------
# tirage_aveugle.py
# ---------------------------------------------------------------------------
def faux_dossier_relecture(tmp_path, n_levees, n_confirmees, forte_levee=None):
    """Dossier relecture/ synthétique + decisions.csv."""
    rel = tmp_path / "relecture"
    (rel / "fiches" / "aveugle").mkdir(parents=True)
    alertes, lignes = [], []
    for k in range(n_levees + n_confirmees):
        i = f"aviation-{k}-r1-abc{k:03d}"
        levee = k < n_levees
        alertes.append({"id": i, "environnement": "aviation", "verdict": "fausse", "enjeu": "fort" if i == forte_levee else "faible",
                        "modele": MODELE, "partie": f"p{k}"})
        fiche = {"id": i, "environnement": "aviation", "tache": str(k), "verdict_automatique": "fausse", "consigne": f"consigne <{k}> & co",
                 "attendues": "[]", "ecriture": {"outil": "o", "arguments": "{}", "message_agent": ""}, "resultat": "ok",
                 "conversation": [{"role": "agent", "texte": f"salut {k}"}], "avertissements": [],
                 "reglement": {"chemin": "externe/x/policy.md", "paragraphes": [], "recherche": "aucun", "note": ""}}
        (rel / "fiches" / "aveugle" / f"{i}.json").write_text(json.dumps(fiche))
        lignes.append({"alerte_id": i, "decision": "levée" if levee else "confirmée", "motif": "c" if levee else "",
                       "justification": "j", "preuve": "p" if levee else ""})
    (rel / "alertes.json").write_text(json.dumps(alertes))
    ecrire_decisions(tmp_path / "decisions.csv", lignes)
    return rel, tmp_path / "decisions.csv"


def test_tirage_10_levees_5_confirmees(tmp_path):
    rel, dec = faux_dossier_relecture(tmp_path, 14, 9)
    r = tirage.produire(rel, dec, rng=random.Random(7), graine=7)
    assert r["tirage"] == {"levees": 10, "confirmees": 5} and r["signalements"] == []
    assert sorted(f["numero"] for f in r["fiches"]) == list(range(1, 16))
    assert len({f["alerte_id"] for f in r["fiches"]}) == 15


def test_tirage_prend_tout_et_signale(tmp_path):
    rel, dec = faux_dossier_relecture(tmp_path, 4, 2)
    r = tirage.produire(rel, dec, rng=random.Random(1), graine=1)
    assert r["tirage"] == {"levees": 4, "confirmees": 2}
    assert len(r["signalements"]) == 2 and "levées" in r["signalements"][0] and "confirmées" in r["signalements"][1]
    assert r["signalements"][0].startswith("seulement 4")



def _oublier_journal(rel, garder=0):
    """Pour les tests qui tirent plusieurs fois sur le même dossier : le journal de la vague (relecture C13, P11) ne
    garde que ses `garder` premières lignes, comme si chaque tirage se faisait sur une copie du dossier."""
    j = Path(rel) / "journal_relecture.jsonl"
    if j.exists():
        lignes = j.read_text(encoding="utf-8").splitlines()[:garder]
        j.write_text("".join(l + "\n" for l in lignes), encoding="utf-8")

def test_tirage_reproductible_avec_graine_et_ordre_melange(tmp_path):
    rel, dec = faux_dossier_relecture(tmp_path, 14, 9)
    a = tirage.produire(rel, dec, tmp_path / "a", rng=random.Random(42), graine=42)
    _oublier_journal(rel)
    b = tirage.produire(rel, dec, tmp_path / "b", rng=random.Random(42), graine=42)
    _oublier_journal(rel)
    c = tirage.produire(rel, dec, tmp_path / "c", rng=random.Random(43), graine=43)
    assert [f["alerte_id"] for f in a["fiches"]] == [f["alerte_id"] for f in b["fiches"]]
    assert [f["alerte_id"] for f in a["fiches"]] != [f["alerte_id"] for f in c["fiches"]]
    decs = [f["decision_claude"] for f in a["fiches"]]
    assert decs != sorted(decs) and decs != sorted(decs, reverse=True)  # levées et confirmées mélangées


def test_graine_secrets_ecrite_apres_tirage(tmp_path):
    rel, dec = faux_dossier_relecture(tmp_path, 12, 6)
    r = tirage.produire(rel, dec)
    ecrit = json.loads((rel / "tirage_aveugle.json").read_text())
    assert isinstance(ecrit["graine"], int) and ecrit["graine"] == r["graine"]
    # la graine inscrite permet de refaire exactement le même tirage
    reg = decisions.lire(dec)
    levees = [i for i, d in reg.items() if d["decision"] == "levée"]
    confirmees = [i for i, d in reg.items() if d["decision"] == "confirmée"]
    choix, _ = tirage.tirer(levees, confirmees, random.Random(ecrit["graine"]))
    assert choix == [f["alerte_id"] for f in ecrit["fiches"]]
    # la graine n'est pas dans la page
    assert str(ecrit["graine"]) not in (rel / "relecture_otsoa.html").read_text(encoding="utf-8")


def test_tirage_refuse_decisions_incompletes(tmp_path):
    rel, dec = faux_dossier_relecture(tmp_path, 3, 3)
    lignes = list(csv.DictReader(open(dec, encoding="utf-8")))[:-1]
    ecrire_decisions(dec, lignes)
    with pytest.raises(decisions.DecisionInvalide, match="sans décision"):
        tirage.produire(rel, dec)


def test_page_html_autonome_responsive_sans_fuite(tmp_path):
    rel, dec = faux_dossier_relecture(tmp_path, 12, 6)
    r = tirage.produire(rel, dec)
    page = (rel / "relecture_otsoa.html").read_text(encoding="utf-8")
    assert page.startswith("<!doctype html>") and '<html lang="fr">' in page
    assert 'name="viewport"' in page
    assert page.count('<article class="fiche"') == 15
    assert page.count('value="vraie erreur"') == 15 and page.count('value="fausse alerte"') == 15
    assert page.count('type="text"') == 15
    assert "consigne &lt;" in page and "consigne <" not in page  # échappement
    assert "http://" not in page and "https://" not in page and "src=" not in page and "<link" not in page  # autonome
    assert not any(j in page.lower() for j in JETONS)
    for f in r["fiches"]:
        assert f["alerte_id"] not in page
    # lisible sans JavaScript : tout le contenu et les champs sont dans le HTML ; le script n'est qu'un confort
    assert "<noscript>" in page and "hidden" in page
    for mot in ("levée", "confirmée"):
        assert mot not in page  # l'avis de Claude n'apparaît pas


# ---------------------------------------------------------------------------
# accord.py
# ---------------------------------------------------------------------------
def faux_tirage(n_accord_cible=15, forte_levee_a=None):
    fiches_ = []
    for k in range(1, 16):
        levee = k <= 10
        fiches_.append({"numero": k, "alerte_id": f"id{k}", "decision_claude": "levée" if levee else "confirmée",
                        "motif_claude": "c" if levee else "", "enjeu": "fort" if k == forte_levee_a else "faible"})
    return {"fiches": fiches_}


def reponses_depuis(tirage_, desaccords=()):
    rep = {}
    for f in tirage_["fiches"]:
        claude = f["decision_claude"]
        autre = "confirmée" if claude == "levée" else "levée"
        rep[f["numero"]] = (autre if f["numero"] in desaccords else claude, "")
    return rep


@pytest.mark.parametrize("n_desaccords, conclusion", [(0, accord.GARDEE), (2, accord.GARDEE), (3, accord.PLUS), (6, accord.PLUS)])
def test_accord_seuil_13_sur_15(n_desaccords, conclusion):
    t = faux_tirage()
    r = accord.comparer(t, reponses_depuis(t, desaccords=range(1, n_desaccords + 1)))
    assert r["accords"] == 15 - n_desaccords and r["seuil"] == 13 and r["total"] == 15
    assert r["conclusion"] == conclusion
    assert len(r["desaccords"]) == n_desaccords


def test_drapeau_levee_forte_jugee_vraie_erreur():
    t = faux_tirage(forte_levee_a=4)
    r = accord.comparer(t, reponses_depuis(t, desaccords=[4]))
    assert r["conclusion"] == accord.GARDEE  # 14 sur 15 : accord suffisant, mais drapeau quand même
    assert r["drapeau_enjeu_fort"] and r["alertes_a_relire"] == ["id4"] and "alertes fortes levées" in r["drapeau"]
    # désaccord sur une alerte faible, ou levée forte sur laquelle on est d'accord : pas de drapeau
    t2 = faux_tirage(forte_levee_a=4)
    assert not accord.comparer(t2, reponses_depuis(t2, desaccords=[5]))["drapeau_enjeu_fort"]
    assert not accord.comparer(t2, reponses_depuis(t2))["drapeau_enjeu_fort"]
    # confirmée par Claude et jugée fausse alerte par Otsoa : pas ce drapeau
    t3 = faux_tirage()
    t3["fiches"][12]["enjeu"] = "fort"
    assert not accord.comparer(t3, reponses_depuis(t3, desaccords=[13]))["drapeau_enjeu_fort"]


def test_accord_echantillon_reduit_seuil_prorata():
    t = {"fiches": faux_tirage()["fiches"][:6]}
    r = accord.comparer(t, reponses_depuis(t))
    assert r["seuil"] == 6 and r["note"]


def test_accord_lecture_reponses_csv(tmp_path):
    (tmp_path / "r.csv").write_text("fiche,reponse,motif\n1,Vraie erreur,mauvaise carte\n2,fausse alerte,\n3,FAUSSE ALERTE,\"a, b\"\n", encoding="utf-8")
    rep = accord.lire_reponses(tmp_path / "r.csv")
    assert rep == {1: ("confirmée", "mauvaise carte"), 2: ("levée", ""), 3: ("levée", "a, b")}
    (tmp_path / "x.csv").write_text("fiche,reponse,motif\n1,peut-être,\n", encoding="utf-8")
    with pytest.raises(accord.ReponsesInvalides, match="réponse inconnue"):
        accord.lire_reponses(tmp_path / "x.csv")


def test_accord_fiche_sans_reponse_refusee():
    t = faux_tirage()
    rep = reponses_depuis(t)
    del rep[3]
    with pytest.raises(accord.ReponsesInvalides, match="sans réponse"):
        accord.comparer(t, rep)


def test_accord_decisions_a_jour_prioritaires():
    t = faux_tirage()
    registre = {"id1": {"decision": "confirmée"}}
    r = accord.comparer(t, reponses_depuis(t), registre)
    assert r["accords"] == 14


def test_chaine_complete_cli(tmp_path):
    rel, dec = faux_dossier_relecture(tmp_path, 12, 6, forte_levee="aviation-0-r1-abc000")
    assert tirage.main(["--relecture", str(rel), "--decisions", str(dec)]) == 0
    t = json.loads((rel / "tirage_aveugle.json").read_text())
    with open(tmp_path / "rep.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["fiche", "reponse", "motif"])
        for f in t["fiches"]:
            w.writerow([f["numero"], "fausse alerte" if f["decision_claude"] == "levée" else "vraie erreur", ""])
    assert accord.main(["--tirage", str(rel / "tirage_aveugle.json"), "--reponses", str(tmp_path / "rep.csv")]) == 0


# ---------------------------------------------------------------------------
# Vraies sorties du pilote (lecture seule ; écriture dans tmp_path)
# ---------------------------------------------------------------------------
ETAPE1 = RACINE / "pilote" / "etape1" / "2026-11-05_07-25-06"
ETAPE2A = RACINE / "pilote" / "etape2a" / "2026-11-05_07-46-58"


@pytest.mark.skipif(not ETAPE1.is_dir(), reason="sortie du pilote absente")
def test_reel_etape1_alertes(tmp_path):
    """Depuis le correctif payment_id (05/11, JOURNAL_CHANGEMENTS.md), l'ajout de bagages gratuits de la tâche 21, payé par
    un autre moyen, n'est plus une alerte : il reste l'alerte bancaire."""
    res = fiches.produire(ETAPE1, tmp_path / "rel")
    assert sorted((r["environnement"], r["tache"], r["outil"]) for r in res) == [("banque", "task_016", "log_verification")]
    for r in res:
        for sous in ("claude", "aveugle"):
            assert (tmp_path / "rel" / "fiches" / sous / f"{r['id']}.md").is_file()
        f = json.loads((tmp_path / "rel" / "fiches" / "claude" / f"{r['id']}.json").read_text())
        assert f["avertissements"] == [], f["avertissements"]
        assert len(f["conversation"]) > 0 and f["consigne"] and f["attendues"] and f["resultat"]
        assert f["reglement"]["chemin"].endswith("policy.md") or f["reglement"]["chemin"].endswith("grep_only.md")
        assert r["modele"] == "anthropic/claude-haiku-5-5" and "modele" not in f  # correspondance seulement (C11)
        brut = "".join(p.read_text(encoding="utf-8") for p in (tmp_path / "rel" / "fiches" / "aveugle").iterdir()).lower()
        assert not any(j in brut for j in JETONS)
    csv.field_size_limit(sys.maxsize)
    with open(ETAPE1 / "actions_typees.csv", newline="", encoding="utf-8") as fh:
        bag = [l for l in csv.DictReader(fh) if l["tache"] == "21" and l["outil"] == "update_reservation_baggages"]
    assert [(l["verdict"], l["motif"]) for l in bag] == [("juste", "payment_id sans effet (aucun paiement enregistré)")]
    assert "gift_card_7091239" in bag[0]["arguments"]


@pytest.mark.skipif(not ETAPE2A.is_dir(), reason="sortie du pilote absente")
def test_reel_etape2a_fiches_sans_erreur(tmp_path):
    res = fiches.produire(ETAPE2A, tmp_path / "rel")
    for r in res:
        f = json.loads((tmp_path / "rel" / "fiches" / "claude" / f"{r['id']}.json").read_text())
        assert f["avertissements"] == [], (r["id"], f["avertissements"])
        brut = "".join(p.read_text(encoding="utf-8") for p in (tmp_path / "rel" / "fiches" / "aveugle").iterdir()).lower()
        assert not any(j in brut for j in JETONS)


# ===========================================================================
# Fiches refaites (05/11) : encadré, différence champ par champ, aveugle, tirage par conversation et par motif
# ===========================================================================
MOTS_AVIS = ("levée", "confirmée", "justification", "preuve", "décision", "decision_claude", "motif_claude", "décision de claude")


def _fiche_json(d, i, version="claude"):
    return json.loads((d / "relecture" / "fiches" / version / f"{i}.json").read_text())


def test_aveugle_ni_modele_ni_partie_ni_rang_ni_tache(tmp_path):
    for d, partie in ((pilote_tau2(tmp_path / "a"), "sim-1"), (pilote_workbench(tmp_path / "b"), "claude-haiku-5-5_all_2026-11-05_07-26-50:0")):
        res = fiches.produire(d, tau2=tmp_path / "absent")
        i = res[0]["id"]
        brut = _fiche_json(d, i, "aveugle")
        assert not {"modele", "partie", "rang", "tache"} & set(brut)
        md = (d / "relecture" / "fiches" / "aveugle" / f"{i}.md").read_text(encoding="utf-8")
        assert partie not in md and partie not in json.dumps(brut)
        for interdit in ("Partie :", "Rang de l'action", "Tâche :", "Modèle de l'agent"):
            assert interdit not in md
        assert not any(j in (md + json.dumps(brut)).lower() for j in JETONS)
        # contrôle 1, C11 : la version Claude ne les montre pas non plus ; la correspondance est dans alertes.json
        assert next(a for a in res if a["id"] == i)["partie"] == partie


def test_fiche_de_claude_aveugle_et_correspondance_a_part(tmp_path):
    """Contrôle 1 (05/11), C11 : les instances de Claude qui relisent toutes les alertes reçoivent la version aveugle,
    avec le seul identifiant opaque de l'alerte ; la correspondance (partie, rang, modèle, tâche) reste dans
    alertes.json, que les relecteurs ne voient pas."""
    for d, partie, tache in ((pilote_tau2(tmp_path / "a"), "sim-1", "21"),
                             (pilote_workbench(tmp_path / "b"), "claude-haiku-5-5_all_2026-11-05_07-26-50:0", "email:3")):
        res = fiches.produire(d, tau2=tmp_path / "absent")
        i = res[0]["id"]
        f = _fiche_json(d, i)  # version Claude
        assert not {"modele", "partie", "rang", "tache"} & set(f) and f["version"] == "relecture"
        assert f["id"] == i and f["conversation"] and f["encadre"] and f["difference"]  # le contenu utile est là
        md = (d / "relecture" / "fiches" / "claude" / f"{i}.md").read_text(encoding="utf-8")
        for interdit in ("Partie :", "Rang de l'action", "Tâche :", "Modèle de l'agent", partie):
            assert interdit not in md and interdit not in json.dumps(f, ensure_ascii=False)
        assert not any(j in (md + json.dumps(f)).lower() for j in JETONS)
        assert f"à reporter dans decisions.csv : {i}" in md  # Claude peut remplir son registre
        # même contenu que la page d'Otsoa, à l'identifiant et à l'étiquette près
        b = _fiche_json(d, i, "aveugle")
        assert {k: v for k, v in f.items() if k != "version"} == {k: v for k, v in b.items() if k != "version"}
        assert i not in (d / "relecture" / "fiches" / "aveugle" / f"{i}.md").read_text(encoding="utf-8")
        # la correspondance, elle, garde tout
        corr = json.loads((d / "relecture" / "alertes.json").read_text(encoding="utf-8"))
        assert [(a["id"], a["partie"], a["rang"], a["tache"]) for a in corr] == [(i, partie, 1, tache)]
        assert corr[0]["modele"] in (MODELE, "claude-haiku-5-5")


def test_aucun_avis_ni_decompte_dans_fiche_et_page(tmp_path):
    rel, dec = faux_dossier_relecture(tmp_path, 12, 6)
    lignes = list(csv.DictReader(open(dec, encoding="utf-8")))
    for k, l in enumerate(lignes):
        l["justification"] = f"JUSTIF_SECRETE_{k}"
        l["preuve"] = f"PREUVE_SECRETE_{k}" if l["decision"] == "levée" else ""
    ecrire_decisions(dec, lignes)
    tirage.produire(rel, dec)
    page = (rel / "relecture_otsoa.html").read_text(encoding="utf-8")
    assert "SECRETE" not in page
    assert not any(m in page.lower() for m in MOTS_AVIS)
    # aucun nombre d'alertes ni effet sur un verdict : aucun de ces mots dans les fiches aveugles du pipeline réel
    d = pilote_tau2(tmp_path / "p")
    res = fiches.produire(d, tau2=tmp_path / "absent")
    md = (d / "relecture" / "fiches" / "aveugle" / f"{res[0]['id']}.md").read_text(encoding="utf-8").lower()
    for mot in ("alertes", "verdict", "décision", "levée", "confirmée", "fragile", "motif"):
        assert mot not in md


def test_encadre_tau2_contenu_et_difference_champ_par_champ(tmp_path):
    d = pilote_tau2(tmp_path)
    res = fiches.produire(d, tau2=tmp_path / "absent")
    f = _fiche_json(d, res[0]["id"])
    enc = " ".join(f["encadre"])
    assert f["encadre"][0].startswith("Environnement : aviation")
    assert "Outil appelé : update_reservation_baggages" in f["encadre"][1]
    assert 'payment_id="gift_card_B"' in f["encadre"][2]                       # ce que l'agent a fait
    assert "n°1" in f["encadre"][3] and 'payment_id="gift_card_A"' in f["encadre"][3]  # ce qui était attendu
    assert "Écart signalé par le comparateur" in f["encadre"][4] and "payment_id" in f["encadre"][4]
    assert "alertes" not in enc
    d_ = f["difference"]
    par_champ = {l["champ"]: l for l in d_["lignes"]}
    assert par_champ["payment_id"]["etat"] == "différent"
    assert par_champ["payment_id"]["agent"] == '"gift_card_B"' and par_champ["payment_id"]["attendu"] == '"gift_card_A"'
    assert par_champ["reservation_id"]["etat"] == "identique" and par_champ["reservation_id"]["compare"] is False  # compare_args = payment_id
    assert par_champ["total_baggages"]["etat"] == "absent de l'action attendue"
    assert d_["champs_differents"] == ["payment_id"]
    md = (d / "relecture" / "fiches" / "aveugle" / f"{res[0]['id']}.md").read_text(encoding="utf-8")
    assert "| `payment_id` |" in md and "champ non comparé" in md
    # ordre des sections
    ordre = [md.index(t) for t in ("## Résumé", "## Différence champ par champ", "## Énoncé de la tâche",
                                   "## Règles du domaine", "## Actions attendues", "## Conversation entière")]
    assert ordre == sorted(ordre)


def test_encadre_workbench_et_champs_libres():
    attendues = fiches.attendues_workbench("['email.send_email.func(recipient=\"a@x.fr\", subject=\"Bonjour\", body=\"Salut\")']")
    d = fiches.difference("email.send_email", {"recipient": "a@x.fr", "subject": "Hello", "body": "Salut"}, attendues)
    par = {l["champ"]: l for l in d["lignes"]}
    assert par["subject"]["etat"] == "différent" and par["subject"]["libre"] is True
    assert par["recipient"]["etat"] == "identique" and par["recipient"]["libre"] is False
    assert d["champs_differents"] == ["subject"]
    # outil absent des attendues
    d2 = fiches.difference("email.delete_email", {"email_id": "1"}, attendues)
    assert d2["attendue"] is None and d2["lignes"] == [] and "email.send_email" in d2["note"]


def test_encadre_selon_le_verdict():
    att = [fiches.verdicts.Attendue(nom="t", arguments={"a": 1})]
    diff = fiches.difference("t", {"a": 1}, att)
    f = {"environnement": "aviation", "resultat": "Error: refusé par l'outil"}
    doublon = fiches.encadre(ligne(outil="t", verdict="doublon"), f, diff, {"a": 1})
    assert "déjà réalisée plus tôt" in doublon[-1] and "identique" in doublon[-1]
    refus = fiches.encadre(ligne(outil="t", verdict="refusée"), f, diff, {"a": 1})
    assert "refusé l'écriture" in refus[-1] and "Error: refusé par l'outil" in refus[-1]
    fausse = fiches.encadre(ligne(outil="t", verdict="fausse"), f, fiches.difference("t", {"a": 2}, att), {"a": 2})
    assert "aucune action attendue" in fausse[-1] and "Champs qui diffèrent" in fausse[-1] and "a" in fausse[-1]


def test_difference_imbriquee_et_action_la_plus_proche():
    att = [fiches.verdicts.Attendue(nom="t", arguments={"flights": [{"n": "A", "d": "1"}], "x": 1}),
           fiches.verdicts.Attendue(nom="t", arguments={"flights": [{"n": "B", "d": "2"}], "x": 1})]
    d = fiches.difference("t", {"flights": [{"n": "B", "d": "3"}], "x": 1}, att)
    assert d["indice"] == 2  # la plus proche : 2 valeurs communes contre 1
    par = {l["champ"]: l["etat"] for l in d["lignes"]}
    assert par == {"flights[0].n": "identique", "flights[0].d": "différent", "x": "identique"}
    assert d["champs_differents"] == ["flights"]


# --- tirage ---------------------------------------------------------------
def _levees_par_motif(effectifs, conv_par_alerte=1):
    """ids, motif_de, conversation_de pour des levées : effectifs {motif: n} ; `conv_par_alerte` alertes par conversation."""
    ids, motif_de, conversation_de, k = [], {}, {}, 0
    for m, n in effectifs.items():
        for _ in range(n):
            i = f"L{k:03d}"
            ids.append(i)
            motif_de[i] = m
            conversation_de[i] = f"conv-{k // conv_par_alerte}"
            k += 1
    return ids, motif_de, conversation_de


def test_tirage_une_alerte_par_conversation_toutes_graines():
    # jeu large : 24 conversations de 3 alertes levées chacune, et des confirmées qui partagent des conversations avec les levées
    ids, motif_de, conv = _levees_par_motif({"a": 15, "b": 30, "c": 27}, conv_par_alerte=3)
    confirmees = [f"C{k}" for k in range(20)]
    for k, c in enumerate(confirmees):
        conv[c] = f"conv-{k}" if k < 10 else f"autre-{k // 2}"  # 10 partagent une conversation avec une levée, 10 non
    for graine in range(60):
        choix, signal = tirage.tirer(ids, confirmees, random.Random(graine), motif_de, conv)
        assert len(choix) == 15 and len(set(choix)) == 15 and signal == []
        assert len({conv[i] for i in choix}) == 15  # au plus une alerte par conversation
        assert sum(i in ids for i in choix) == 10 and sum(i in confirmees for i in choix) == 5


def test_tirage_conversation_limite_et_signale():
    ids, motif_de, conv = _levees_par_motif({"a": 9}, conv_par_alerte=3)  # 3 conversations seulement
    choix, signal = tirage.tirer(ids, [], random.Random(1), motif_de, conv)
    assert len(choix) == 3 and len({conv[i] for i in choix}) == 3
    assert signal[0].startswith("seulement 3 alertes levées sur 10") and "au plus une alerte par conversation" in signal[0]


def test_repartition_des_levees_par_motif():
    ids, motif_de, conv = _levees_par_motif({"a": 2, "b": 3, "c": 12, "d": 1})
    quotas = tirage._repartir({"a": 2, "b": 3, "c": 12, "d": 1}, {"a": 2, "b": 3, "c": 12, "d": 1}, 10)
    assert sum(quotas.values()) == 10 and min(quotas.values()) >= 1
    assert quotas["c"] == max(quotas.values()) and quotas["c"] >= 5 and quotas["d"] == 1
    for graine in range(30):
        choix, _ = tirage.tirer(ids, [], random.Random(graine), motif_de, conv)
        par = {m: sum(1 for i in choix if motif_de[i] == m) for m in "abcd"}
        assert par == quotas
    # un motif absent n'a pas de place ; un motif minuscule garde la sienne
    q2 = tirage._repartir({"b": 40, "d": 1}, {"b": 40, "d": 1}, 10)
    assert q2 == {"b": 9, "d": 1}
    # un motif qui ne peut fournir que 2 : sa place va aux autres
    q3 = tirage._repartir({"a": 2, "c": 40}, {"a": 2, "c": 40}, 10)
    assert q3["a"] <= 2 and sum(q3.values()) == 10
    # moins de levées que de motifs : tout est pris
    q4 = tirage._repartir({"a": 1, "b": 1, "c": 1}, {"a": 1, "b": 1, "c": 1}, 10)
    assert q4 == {"a": 1, "b": 1, "c": 1}


def test_repartition_levees_complete_si_un_motif_est_court():
    ids, motif_de, conv = _levees_par_motif({"a": 1, "c": 30})
    choix, signal = tirage.tirer(ids, [], random.Random(5), motif_de, conv)
    assert len(choix) == 10 and not any("levées" in x for x in signal) and any(motif_de[i] == "a" for i in choix)


def test_repartition_dans_produire_et_json(tmp_path):
    rel, dec = faux_dossier_relecture(tmp_path, 20, 8)
    lignes = list(csv.DictReader(open(dec, encoding="utf-8")))
    motifs = ["a"] * 3 + ["b"] * 5 + ["c"] * 10 + ["d"] * 2
    for l, m in zip([l for l in lignes if l["decision"] == "levée"], motifs):
        l["motif"] = m
        if m == "a":   # relecture C13, P9 : le cas ouvre la preuve
            l["preuve"] = "a1 : " + (l.get("preuve") or "essai")
    ecrire_decisions(dec, lignes)
    r = tirage.produire(rel, dec, rng=random.Random(11), graine=11)
    assert r["tirage"] == {"levees": 10, "confirmees": 5}
    rep = r["repartition_motifs"]
    assert set(rep) == {"a", "b", "c", "d"} and all(v >= 1 for v in rep.values()) and sum(rep.values()) == 10
    assert rep["c"] == max(rep.values())


def test_tirage_ordre_reproductible_avec_la_graine_page_identique(tmp_path):
    rel, dec = faux_dossier_relecture(tmp_path, 14, 9)
    for nom, g in (("s1", 42), ("s2", 42), ("s3", 43)):  # un tirage ne se refait pas dans le même dossier
        tirage.produire(rel, dec, tmp_path / nom, rng=random.Random(g), graine=g)
        _oublier_journal(rel)
    page = lambda nom: (tmp_path / nom / "relecture_otsoa.html").read_text(encoding="utf-8")  # noqa: E731
    assert page("s1") == page("s2") and page("s1") != page("s3")
    t = json.loads((tmp_path / "s3" / "tirage_aveugle.json").read_text())
    assert t["graine"] == 43


def test_tirage_conversations_dans_produire(tmp_path):
    """Alertes d'une même partie dans alertes.json : une seule peut être tirée."""
    rel, dec = faux_dossier_relecture(tmp_path, 14, 9)
    alertes = json.loads((rel / "alertes.json").read_text())
    for a in alertes:
        k = int(a["id"].split("-")[1])
        a["partie"] = f"partie-{k // 2 if k < 6 else k}"  # les 6 premières alertes vont par deux dans une même partie
    (rel / "alertes.json").write_text(json.dumps(alertes))
    for graine in range(20):
        r = tirage.produire(rel, dec, tmp_path / f"s{graine}", rng=random.Random(graine), graine=graine)
        _oublier_journal(rel)
        parties = [next(a["partie"] for a in alertes if a["id"] == f["alerte_id"]) for f in r["fiches"]]
        assert len(parties) == len(set(parties)) == 15


def test_fichier_reponses_inchange_et_lu_par_accord(tmp_path):
    """Le fichier d'Otsoa garde le format fiche,reponse,motif ; accord.py le lit tel quel (sortie du bouton comprise)."""
    rel, dec = faux_dossier_relecture(tmp_path, 12, 6)
    r = tirage.produire(rel, dec, rng=random.Random(3), graine=3)
    page = (rel / "relecture_otsoa.html").read_text(encoding="utf-8")
    assert "var lignes=['fiche,reponse,motif'];" in page  # script du bouton inchangé
    assert 'data-numero="1"' in page and 'name="r1"' in page and 'name="m1"' in page
    # reproduit ce que fait le script : n,valeur,"motif" ; un motif vide ; un motif avec virgule et guillemets
    lignes = ["fiche,reponse,motif"]
    for f in r["fiches"]:
        valeur = "fausse alerte" if f["decision_claude"] == "levée" else "vraie erreur"
        motif = 'dit "oui", puis non' if f["numero"] == 2 else ""
        lignes.append(f'{f["numero"]},{valeur},"{motif.replace(chr(34), chr(34) * 2)}"')
    chemin = tmp_path / "reponses.csv"
    chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    rep = accord.lire_reponses(chemin)
    assert len(rep) == 15 and rep[2][1] == 'dit "oui", puis non'
    res = accord.comparer(json.loads((rel / "tirage_aveugle.json").read_text()), rep)
    assert res["accords"] == 15 and res["conclusion"] == accord.GARDEE
    # le format des entrées du tirage lu par accord n'a pas changé
    assert set(r["fiches"][0]) == {"numero", "alerte_id", "decision_claude", "motif_claude", "enjeu", "verdict"}


def test_page_html_ordre_des_sections_et_encadre(tmp_path):
    d = pilote_tau2(tmp_path / "p")
    res = fiches.produire(d, tau2=tmp_path / "absent")
    f = _fiche_json(d, res[0]["id"], "aveugle")
    html_ = tirage.rendre_fiche_html(f, 1, 1)
    ordre = [html_.index(t) for t in ('class="encadre"', "Différence champ par champ", "Énoncé de la tâche",
                                      "Règles du domaine", "Actions attendues", "Conversation entière", "Ton avis")]
    assert ordre == sorted(ordre)
    assert "update_reservation_baggages" in html_ and "ACTION SIGNALÉE" in html_ and "<table>" in html_
    assert not any(j in html_.lower() for j in JETONS)


# ---------------------------------------------------------------------------
# Second tour, fortes levées après le drapeau, tirage unique (décision B2 d'Otsoa, 5 novembre)
# ---------------------------------------------------------------------------
def dossier_conversations_partagees(tmp_path, n_levees, n_confirmees, fortes=()):
    """Deux alertes par partie (conversation) ; `fortes` : indices des alertes à enjeu fort."""
    rel, dec = faux_dossier_relecture(tmp_path, n_levees, n_confirmees)
    alertes = json.loads((rel / "alertes.json").read_text())
    for a in alertes:
        k = int(a["id"].split("-")[1])
        a["partie"] = f"partie-{k // 2}"
        a["enjeu"] = "fort" if k in fortes else "faible"
    (rel / "alertes.json").write_text(json.dumps(alertes))
    return rel, dec, {a["id"]: a["partie"] for a in alertes}


def ecrire_reponses(chemin, t, desaccords=()):
    """CSV d'Otsoa : d'accord avec Claude, sauf sur les fiches `desaccords`."""
    with open(chemin, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["fiche", "reponse", "motif"])
        for f in t["fiches"]:
            levee = (f["decision_claude"] == "levée") != (f["numero"] in desaccords)
            w.writerow([f["numero"], "fausse alerte" if levee else "vraie erreur", ""])


def test_second_tour_ecarte_alertes_et_conversations_du_premier(tmp_path):
    rel, dec, partie = dossier_conversations_partagees(tmp_path, 41, 21)
    t1 = tirage.produire(rel, dec, rng=random.Random(3), graine=3)
    ids1 = {f["alerte_id"] for f in t1["fiches"]}
    for g in range(15):
        sortie = tmp_path / f"t2-{g}"
        t2 = tirage.produire(rel, dec, sortie, rng=random.Random(g), graine=g, exclure=[rel / "tirage_aveugle.json"])
        _oublier_journal(rel, garder=1)
        assert (t2["nature"], t2["tour"], t2["premier_numero"]) == (tirage.TIRAGE, 2, 16)
        assert [f["numero"] for f in t2["fiches"]] == list(range(16, 31))
        assert t2["tirage"] == {"levees": 10, "confirmees": 5} and t2["signalements"] == []
        ids2 = {f["alerte_id"] for f in t2["fiches"]}
        assert not ids1 & ids2
        assert not {partie[i] for i in ids1} & {partie[i] for i in ids2}
        assert t2["exclues"] == {"alertes": 15, "conversations": 15}
        assert t2["precedents"][0]["fichier"] == "tirage_aveugle.json" and len(t2["precedents"][0]["sha256"]) == 64
        page = (sortie / "relecture_otsoa_tour2.html").read_text(encoding="utf-8")
        assert "second tour" in page and "Fiche 16 sur 30" in page and 'data-numero="30"' in page
        assert (sortie / "tirage_aveugle_tour2.json").exists() and not (sortie / "tirage_aveugle.json").exists()
        assert "levée" not in page and "confirmée" not in page


def test_tirer_n_utilise_aucune_conversation_exclue():
    ids, motif_de, conv = _levees_par_motif({"a": 12, "b": 30}, conv_par_alerte=2)
    confirmees = [f"C{k}" for k in range(16)]
    for k, c in enumerate(confirmees):
        conv[c] = f"conv-{k}"  # les confirmées partagent les conversations des premières levées
    exclues = {f"conv-{k}" for k in range(0, 21, 2)}
    for graine in range(40):
        choix, _ = tirage.tirer(ids, confirmees, random.Random(graine), motif_de, conv, exclues)
        assert choix and not {conv[i] for i in choix} & exclues
        assert len({conv[i] for i in choix}) == len(choix)


def test_second_tour_signale_les_conversations_ecartees(tmp_path):
    rel, dec, _ = dossier_conversations_partagees(tmp_path, 24, 12)  # 12 conversations de levées, 6 de confirmées
    tirage.produire(rel, dec, rng=random.Random(5), graine=5)
    t2 = tirage.produire(rel, dec, tmp_path / "t2", rng=random.Random(6), graine=6, exclure=[rel / "tirage_aveugle.json"])
    assert t2["tirage"] == {"levees": 2, "confirmees": 1}
    assert len(t2["signalements"]) == 2 and all("écartées" in s for s in t2["signalements"])


def test_tirage_ne_se_refait_pas_et_deux_tours_au_plus(tmp_path):
    rel, dec, _ = dossier_conversations_partagees(tmp_path, 41, 21)
    tirage.produire(rel, dec, rng=random.Random(1), graine=1)
    avant = (rel / "tirage_aveugle.json").read_text()
    with pytest.raises(tirage.TirageInvalide, match="ne se refait pas"):
        tirage.produire(rel, dec, rng=random.Random(2), graine=2)
    assert tirage.main(["--relecture", str(rel), "--decisions", str(dec)]) == 2
    assert (rel / "tirage_aveugle.json").read_text() == avant
    tirage.produire(rel, dec, rng=random.Random(2), graine=2, exclure=[rel / "tirage_aveugle.json"])
    with pytest.raises(tirage.TirageInvalide, match="2 tours"):
        tirage.produire(rel, dec, tmp_path / "x", rng=random.Random(3), graine=3,
                        exclure=[rel / "tirage_aveugle.json", rel / "tirage_aveugle_tour2.json"])
    with pytest.raises(tirage.TirageInvalide, match="incohérents"):  # le second tour sans le premier
        tirage.produire(rel, dec, tmp_path / "y", rng=random.Random(4), graine=4,
                        exclure=[rel / "tirage_aveugle_tour2.json"])


def test_exclure_un_fichier_d_une_autre_vague_refuse(tmp_path):
    rel, dec, _ = dossier_conversations_partagees(tmp_path, 41, 21)
    autre = tmp_path / "autre.json"
    autre.write_text(json.dumps({"nature": "tirage", "tour": 1, "fiches": [{"numero": 1, "alerte_id": "commerce-9-r1-x"}]}))
    with pytest.raises(tirage.TirageInvalide, match="absentes de cette vague"):
        tirage.produire(rel, dec, exclure=[autre])
    (tmp_path / "pas_un_tirage.json").write_text("[1, 2]")
    with pytest.raises(tirage.TirageInvalide, match="pas un fichier de tirage"):
        tirage.produire(rel, dec, exclure=[tmp_path / "pas_un_tirage.json"])


def test_second_tour_bout_en_bout_en_ligne_de_commande(tmp_path):
    rel, dec, _ = dossier_conversations_partagees(tmp_path, 41, 21)
    assert tirage.main(["--relecture", str(rel), "--decisions", str(dec)]) == 0
    assert tirage.main(["--relecture", str(rel), "--decisions", str(dec), "--exclure", str(rel / "tirage_aveugle.json")]) == 0
    t1 = json.loads((rel / "tirage_aveugle.json").read_text())
    t2 = json.loads((rel / "tirage_aveugle_tour2.json").read_text())
    ecrire_reponses(tmp_path / "r1.csv", t1, desaccords={1, 2, 3})  # 12 sur 15 : second tour
    ecrire_reponses(tmp_path / "r2.csv", t2, desaccords={16})       # 26 sur 30 : gardée au second tour
    args = ["--tirage", str(rel / "tirage_aveugle.json"), "--reponses", str(tmp_path / "r1.csv"),
            "--tirage", str(rel / "tirage_aveugle_tour2.json"), "--reponses", str(tmp_path / "r2.csv")]
    assert accord.main(args + ["--sortie", str(tmp_path / "accord.json")]) == 0
    b = json.loads((tmp_path / "accord.json").read_text())
    assert (b["accords"], b["total"], b["conclusion"]) == (26, 30, accord.GARDEE_SECOND_TOUR)
    assert len(b["decisions_otsoa"]) == 30
    inverse = args[4:] + args[:4]  # tours donnés dans le mauvais ordre
    assert accord.main(inverse) == 2


def test_relecture_des_fortes_levees_puis_second_tour(tmp_path):
    fortes = {0, 2, 4, 6, 8, 10, 12, 14}  # levées à enjeu fort, une par conversation
    rel, dec, partie = dossier_conversations_partagees(tmp_path, 41, 21, fortes=fortes)
    t1 = tirage.produire(rel, dec, rng=random.Random(8), graine=8)
    f = tirage.produire(rel, dec, rng=random.Random(9), graine=9, fortes=True, exclure=[rel / "tirage_aveugle.json"])
    vus = {x["alerte_id"] for x in t1["fiches"]}
    ids_fortes = {a for a in partie if int(a.split("-")[1]) in fortes}
    assert (f["nature"], f["tour"], f["premier_numero"]) == (tirage.FORTES, None, 1)
    assert {x["alerte_id"] for x in f["fiches"]} == ids_fortes - vus
    assert all(x["decision_claude"] == "levée" and x["enjeu"] == "fort" for x in f["fiches"])
    page = (rel / "relecture_fortes_levees.html").read_text(encoding="utf-8")
    assert "enjeu fort" in page and "ta décision l'emporte" in page and "second tour" not in page
    # le second tour écarte le premier tour et les fortes relues, avec leurs conversations
    t2 = tirage.produire(rel, dec, rng=random.Random(10), graine=10,
                         exclure=[rel / "tirage_aveugle.json", rel / "fortes_levees.json"])
    assert t2["tour"] == 2 and t2["premier_numero"] == 16
    montres = vus | {x["alerte_id"] for x in f["fiches"]}
    assert not {x["alerte_id"] for x in t2["fiches"]} & montres
    assert not {partie[x["alerte_id"]] for x in t2["fiches"]} & {partie[i] for i in montres}
    with pytest.raises(tirage.TirageInvalide, match="déjà faite"):
        tirage.produire(rel, dec, tmp_path / "z", rng=random.Random(11), graine=11, fortes=True,
                        exclure=[rel / "tirage_aveugle.json", rel / "fortes_levees.json"])


def test_accord_fortes_levees_l_emportent_hors_accord():
    t = faux_tirage(forte_levee_a=4)
    rep = reponses_depuis(t, desaccords=[4])  # levée forte jugée vraie erreur : drapeau
    tf = {"nature": tirage.FORTES, "tour": None, "fiches": [
        {"numero": 1, "alerte_id": "f1", "decision_claude": "levée", "enjeu": "fort"},
        {"numero": 2, "alerte_id": "f2", "decision_claude": "levée", "enjeu": "fort"}]}
    rf = {1: ("confirmée", "vraie"), 2: ("levée", "")}
    b = accord.conclure([(t, rep)], fortes=(tf, rf))
    assert (b["accords"], b["total"]) == (14, 15)  # les fortes relues ne comptent pas dans l'accord
    assert b["fortes"] == {"relues": 2, "jugees_vraies_erreurs": 1}
    registre = {x["alerte_id"]: {"decision": x["decision_claude"]} for x in t["fiches"]}
    registre.update({"f1": {"decision": "levée"}, "f2": {"decision": "levée"}, "z": {"decision": "levée"}})
    retenues = accord.decisions_retenues(registre, b["decisions_otsoa"])
    assert (retenues["id4"], retenues["f1"], retenues["f2"], retenues["z"]) == ("confirmée", "confirmée", "levée", "levée")
    with pytest.raises(accord.ReponsesInvalides, match="sans drapeau"):
        accord.conclure([(t, reponses_depuis(t))], fortes=(tf, rf))
    with pytest.raises(accord.ReponsesInvalides, match="déjà jugées"):
        accord.conclure([(t, rep)], fortes=({"nature": tirage.FORTES, "fiches": [{"numero": 1, "alerte_id": "id4"}]},
                                            {1: ("confirmée", "")}))
    with pytest.raises(accord.ReponsesInvalides, match="fortes_levees.json"):
        accord.conclure([(t, rep)], fortes=(t, rep))
    with pytest.raises(accord.ReponsesInvalides, match="pas un tirage à l'aveugle"):
        accord.conclure([(tf, rf)])


def test_drapeau_puis_fortes_en_ligne_de_commande(tmp_path, capsys):
    rel, dec, _ = dossier_conversations_partagees(tmp_path, 41, 21, fortes=set(range(41)))  # toutes les levées sont fortes
    assert tirage.main(["--relecture", str(rel), "--decisions", str(dec)]) == 0
    t1 = json.loads((rel / "tirage_aveugle.json").read_text())
    forte = next(f["numero"] for f in t1["fiches"] if f["decision_claude"] == "levée")
    ecrire_reponses(tmp_path / "r1.csv", t1, desaccords={forte})
    base = ["--tirage", str(rel / "tirage_aveugle.json"), "--reponses", str(tmp_path / "r1.csv")]
    assert accord.main(base) == 0 and "DRAPEAU" in capsys.readouterr().out
    assert tirage.main(["--relecture", str(rel), "--decisions", str(dec), "--fortes",
                        "--exclure", str(rel / "tirage_aveugle.json")]) == 0
    tf = json.loads((rel / "fortes_levees.json").read_text())
    assert len(tf["fiches"]) == 41 - 10
    ecrire_reponses(tmp_path / "rf.csv", tf, desaccords={1})  # Otsoa juge la fiche 1 vraie erreur
    fortes = ["--fortes", str(rel / "fortes_levees.json"), "--reponses-fortes", str(tmp_path / "rf.csv")]
    assert accord.main(base + fortes + ["--sortie", str(tmp_path / "accord.json")]) == 0
    b = json.loads((tmp_path / "accord.json").read_text())
    assert b["drapeau_enjeu_fort"] and b["fortes"] == {"relues": 31, "jugees_vraies_erreurs": 1}
    assert len(b["decisions_otsoa"]) == 15 + 31
    assert accord.main(base + fortes[:2]) == 2  # --fortes sans --reponses-fortes


def test_motif_a_avec_son_cas(tmp_path):
    ecrire_decisions(tmp_path / "d.csv", [
        {"alerte_id": "A", "decision": "levée", "motif": "a", "justification": "j", "preuve": "a2 : vol absent de la base"},
        {"alerte_id": "B", "decision": "levée", "motif": "(a)", "justification": "j", "preuve": " A4: introuvable"},
    ])
    reg = decisions.lire(tmp_path / "d.csv")
    assert reg["A"]["motif"] == "a" and reg["B"]["motif"] == "a"


def test_fiche_montre_le_reglement_entier_et_l_etat_initial(tmp_path):
    """Relecture C13, P10 : la fiche d'alerte montre les pièces que le critère du motif a cite, comme celle de l'audit :
    le règlement entier reçu par l'agent et l'état initial propre à la tâche."""
    d = pilote_tau2(tmp_path)
    res = fiches.produire(d, tau2=RACINE / "externe" / "tau2-bench")
    f = json.loads((d / "relecture" / "fiches" / "claude" / f"{res[0]['id']}.json").read_text())
    # le règlement reçu par l'agent, en entier : avec le paragraphe qui ne cite pas l'outil
    assert "Paragraphe sans rapport" in f["reglement"]["texte_entier"] and "etat_initial" in f
    assert not any("Paragraphe sans rapport" in p["texte"] for p in f["reglement"]["paragraphes"])
    md = (d / "relecture" / "fiches" / "claude" / f"{res[0]['id']}.md").read_text()
    assert "## Règlement entier" in md and "## État initial propre à la tâche" in md


def test_journal_de_la_vague_refuse_un_tirage_refait_ailleurs(tmp_path):
    """Relecture C13, P11 : un tirage inscrit au journal de la vague ne se refait pas dans un autre dossier."""
    rel, dec = faux_dossier_relecture(tmp_path, 14, 9)
    tirage.produire(rel, dec, tmp_path / "s1", rng=random.Random(1), graine=1)
    lignes = [json.loads(l) for l in (rel / "journal_relecture.jsonl").read_text().splitlines()]
    assert lignes[0]["type"] == "tirage" and lignes[0]["tour"] == 1 and len(lignes[0]["page_sha256"]) == 64
    with pytest.raises(tirage.TirageInvalide, match="journal"):
        tirage.produire(rel, dec, tmp_path / "s2", rng=random.Random(2), graine=2)
