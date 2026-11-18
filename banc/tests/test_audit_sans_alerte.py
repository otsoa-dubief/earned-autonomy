"""Tests de l'audit des tâches sans alerte (banc/relecture/audit_sans_alerte.py ; PLAN_EXPERIENCE.md, 4.5).

Dossiers de vague synthétiques au format du lanceur (cout.json, parties/, actions_typees.csv, taches/)."""
import csv
import json
import random
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "banc" / "relecture"))

import audit_sans_alerte as audit  # noqa: E402

CHAMPS = ["partie", "tache", "rang", "banc", "domaine", "outil", "arguments", "kind", "verdict", "modele", "motif",
          "resultat", "type", "enjeu", "plafonnee", "montant", "raison", "etiquettes"]
JETONS = ("claude", "haiku", "sonnet", "opus", "anthropic", "openai", "gpt", "gemini")
DOMAINE = {"aviation": "airline", "commerce": "retail"}
POLICY = ("# Airline Policy\n\n## Bags\n\nUse update_reservation_baggages only with the payment the user chose.\n\n"
          "## Other\n\nParagraphe sans rapport, présent seulement dans le règlement entier.\n")


def ligne(**kw):
    base = {c: "" for c in CHAMPS}
    base.update(banc="tau2", domaine="airline", kind="écriture", enjeu="faible", type="écriture durable")
    base.update(kw)
    return base


def partie_tau2(d, cid, tache, env="aviation", modele="claude-haiku-5-5", ecritures=("juste",), ok=True):
    """Une partie τ-bench : une lecture (rang 0), puis une écriture par verdict (rangs 1…)."""
    sim, dom = f"sim-{cid}", DOMAINE[env]
    msgs = [{"role": "assistant", "content": f"Bonjour, je suis {modele} d'anthropic.", "turn_idx": 0, "tool_calls": None},
            {"role": "user", "content": "Je veux changer mes bagages.", "turn_idx": 1, "tool_calls": None},
            {"role": "assistant", "content": "", "turn_idx": 2, "tool_calls": [
                {"id": "c0", "name": "get_user_details", "arguments": {"user_id": "u1"}, "requestor": "assistant"}]},
            {"role": "tool", "id": "c0", "content": "{\"user_id\": \"u1\"}", "turn_idx": 3, "tool_calls": None}]
    lignes = [ligne(partie=sim, tache=tache, rang="0", outil="get_user_details", kind="lecture", domaine=dom,
                    modele=f"anthropic/{modele}", arguments="{\"user_id\": \"u1\"}")]
    t = 4
    for k, v in enumerate(ecritures, 1):
        args = {"reservation_id": f"R{k}", "payment_id": "gift_card_A"}
        msgs.append({"role": "assistant", "content": f"écriture {k}", "turn_idx": t, "tool_calls": [
            {"id": f"c{k}", "name": "update_reservation_baggages", "arguments": args, "requestor": "assistant"}]})
        msgs.append({"role": "tool", "id": f"c{k}", "content": "{\"ok\": true}", "turn_idx": t + 1, "tool_calls": None})
        t += 2
        lignes.append(ligne(partie=sim, tache=tache, rang=str(k), outil="update_reservation_baggages", verdict=v,
                            domaine=dom, modele=f"anthropic/{modele}", arguments=json.dumps(args)))
    tache_json = {"id": tache, "user_scenario": {"instructions": {"reason_for_call": f"RAISON-{tache}",
                                                                   "task_instructions": "Use gift_card_A."}},
                  "evaluation_criteria": {"actions": [{"action_id": f"{tache}_1", "requestor": "assistant",
                                                       "name": "update_reservation_baggages",
                                                       "arguments": {"reservation_id": "R1", "payment_id": "gift_card_A"},
                                                       "info": None, "compare_args": ["payment_id"]}]}}
    run = {"id": sim, "task_id": tache, "messages": msgs, "policy": POLICY, "start_time": f"2026-11-20T10:00:{cid[-2:]}"}
    info = {"environment_info": {"domain_name": dom}, "agent_info": {"llm": f"anthropic/{modele}"}}
    dossier = f"tau2-{cid}"
    (d / "parties" / dossier).mkdir(parents=True)
    (d / "parties" / dossier / "results.json").write_text(json.dumps({"info": info, "tasks": [tache_json],
                                                                       "simulations": [run]}))
    cout = {"id": cid, "env": env, "modele": modele, "tache": tache, "ok": ok, "statut": "terminée" if ok else "échec",
            "passage": 1, "vague": 1}
    return cout, lignes


def partie_workbench(d, cid, tache, seconde, modele="claude-haiku-5-5", verdict="juste"):
    """Une partie WorkBench : une lecture, une écriture (rang 1), une réponse finale."""
    stem = f"{modele}_all_2026-11-20_10-00-{seconde:02d}"
    dossier = f"workbench-{cid}"
    (d / "parties" / dossier).mkdir(parents=True)
    (d / "taches" / cid).mkdir(parents=True)
    texte = f"Delete my last email from nadia ({tache})"
    calls = ["email.search_emails.func(query=\"nadia\")", "email.delete_email.func(email_id=\"00000479\")"]
    with open(d / "parties" / dossier / f"{stem}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["task", "function_calls", "full_response", "error"])
        w.writeheader()
        w.writerow({"task": texte, "function_calls": repr(calls), "full_response": "x", "error": ""})
    steps = [
        {"llm_output": json.dumps({"content": f"Je cherche ({modele})"}), "action": "email.search_emails",
         "action_input": {"query": "nadia"}, "observation": "[{\"email_id\": \"00000479\"}]"},
        {"llm_output": json.dumps({"content": ""}), "action": "email.delete_email",
         "action_input": {"email_id": "00000479"}, "observation": "Email deleted successfully."},
        {"llm_output": "{}", "action": "Final Answer", "action_input": "ok", "observation": ""},
    ]
    (d / "parties" / dossier / f"{stem}_traces.json").write_text(json.dumps([{"task": texte, "steps": steps}]))
    with open(d / "taches" / cid / "email_tasks_and_outcomes.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["task", "outcome"])
        w.writerow([texte, "['email.delete_email.func(email_id=\"00000479\")']"])
    lignes = [ligne(banc="workbench", domaine="email", partie=f"{stem}:0", tache=tache, rang="0",
                    outil="email.search_emails", kind="lecture", modele=modele),
              ligne(banc="workbench", domaine="email", partie=f"{stem}:0", tache=tache, rang="1",
                    outil="email.delete_email", verdict=verdict, modele=modele,
                    arguments=json.dumps({"email_id": "00000479"}))]
    cout = {"id": cid, "env": "WorkBench", "modele": modele, "tache": tache, "ok": True, "statut": "terminée",
            "passage": 1, "vague": 1}
    return cout, lignes


def ecrire_vague(d, elements):
    d.mkdir(parents=True, exist_ok=True)
    couts, lignes = zip(*elements) if elements else ((), ())
    (d / "cout.json").write_text(json.dumps({"etape": "experience", "vague": 1, "parties": list(couts)}))
    with open(d / "actions_typees.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CHAMPS)
        w.writeheader()
        for ls in lignes:
            w.writerows(ls)
    return d


def vague_type(tmp_path):
    """Aviation : 7 tâches sans alerte (t1 à t7, t1 jouée trois fois), t8 avec une alerte dans une seule de ses deux
    parties, t9 jouée seulement en échec technique ; WorkBench : 2 tâches sans alerte, 1 avec alerte."""
    d = tmp_path / "vague1"
    el = [partie_tau2(d, "a01", "t1", ecritures=()), partie_tau2(d, "a02", "t1", ecritures=(),
                                                                   modele="claude-sonnet-5-5"),
          partie_tau2(d, "a03", "t1", ecritures=("juste", "doublon sans effet", "juste"), modele="claude-opus-5-5")]
    el += [partie_tau2(d, f"a1{k}", f"t{k}") for k in range(2, 8)]
    el += [partie_tau2(d, "a20", "t8"), partie_tau2(d, "a21", "t8", ecritures=("fausse",), modele="claude-sonnet-5-5")]
    el += [partie_tau2(d, "a30", "t9", ok=False)]
    el += [partie_workbench(d, "w1", "email:1", 1), partie_workbench(d, "w2", "email:2", 2),
           partie_workbench(d, "w3", "email:3", 3, verdict="refusée")]
    return ecrire_vague(d, el)


# ---------------------------------------------------------------------------
# Population et tirage
# ---------------------------------------------------------------------------
def test_population_sans_aucune_alerte_toutes_parties_et_vagues(tmp_path):
    v1 = vague_type(tmp_path)
    v2 = ecrire_vague(tmp_path / "vague2", [partie_tau2(tmp_path / "vague2", "b01", "t7", ecritures=("doublon",))])
    pop, jouees = audit.population(audit.charger([v1, v2]))
    assert sorted(pop["aviation"]) == ["t1", "t2", "t3", "t4", "t5", "t6"]  # t7 : alerte en vague 2 ; t8 ; t9
    assert sorted(pop["WorkBench"]) == ["email:1", "email:2"]
    assert jouees == {"aviation": 8, "WorkBench": 3}  # t9 n'a aucune partie au bon statut : pas jouée
    assert pop["aviation"]["t1"] == ["sim-a01", "sim-a02", "sim-a03"]


def test_cinq_par_environnement_toutes_s_il_y_en_a_moins_et_partie_avec_ecriture(tmp_path):
    donnees = audit.charger([vague_type(tmp_path)])
    pop, _ = audit.population(donnees)
    for graine in range(40):
        choix = audit.tirer(pop, donnees["ecritures"], random.Random(graine))
        envs = [c["environnement"] for c in choix]
        assert envs.count("aviation") == 5 and envs.count("WorkBench") == 2
        assert len({(c["environnement"], c["tache"]) for c in choix}) == 7
        for c in choix:
            if c["tache"] == "t1":  # seule la partie a03 compte des écritures jugées justes
                assert c["partie"] == "sim-a03" and c["avec_ecriture"] and c["candidates"] == 1


def test_sans_ecriture_on_tire_parmi_toutes_les_parties(tmp_path):
    d = tmp_path / "v"
    donnees = audit.charger([ecrire_vague(d, [partie_tau2(d, "a01", "t1", ecritures=()),
                                              partie_tau2(d, "a02", "t1", ecritures=("doublon sans effet",))])])
    pop, _ = audit.population(donnees)
    vues = {audit.tirer(pop, donnees["ecritures"], random.Random(g))[0]["partie"] for g in range(30)}
    assert vues == {"sim-a01", "sim-a02"}


def test_tirage_reproductible_graine_secrets_inscrite_apres(tmp_path, monkeypatch):
    v = vague_type(tmp_path)
    monkeypatch.setattr(audit.secrets, "randbits", lambda n: 123456789)
    r1 = audit.produire_tirage([v], tmp_path / "audit1")
    (v / "relecture" / "journal_relecture.jsonl").unlink()   # comme sur une copie de la vague (C13, P11)
    r2 = audit.produire_tirage([v], tmp_path / "audit2", rng=random.Random(123456789), graine=123456789)
    assert [f["id"] for f in r1["fiches"]] == [f["id"] for f in r2["fiches"]]
    assert [f["partie"] for f in r1["fiches"]] == [f["partie"] for f in r2["fiches"]]
    texte = (tmp_path / "audit1" / audit.F_TIRAGE).read_text()
    assert list(json.loads(texte))[-1] == "graine" and json.loads(texte)["graine"] == 123456789
    assert r1["population"] == {"WorkBench": 2, "aviation": 7} and r1["tirees"] == {"WorkBench": 2, "aviation": 5}


def test_un_tirage_ne_se_refait_pas(tmp_path):
    v = vague_type(tmp_path)
    audit.produire_tirage([v], tmp_path / "audit", rng=random.Random(1), graine=1)
    with pytest.raises(audit.AuditInvalide, match="un tirage ne se refait pas"):
        audit.produire_tirage([v], tmp_path / "audit", rng=random.Random(2), graine=2)


def test_partie_inconnue_ou_tache_incoherente_refusee(tmp_path):
    d = tmp_path / "v"
    c, ls = partie_tau2(d, "a01", "t1")
    ls[1]["tache"] = "t2"
    ecrire_vague(d, [(c, ls)])
    with pytest.raises(audit.AuditInvalide, match="cout.json"):
        audit.charger([d])


def test_ecriture_au_verdict_inattendu_refusee(tmp_path):
    d = tmp_path / "v"
    ecrire_vague(d, [partie_tau2(d, "a01", "t1", ecritures=("",))])
    with pytest.raises(audit.AuditInvalide, match="verdict inattendu"):
        audit.charger([d])


# ---------------------------------------------------------------------------
# Fiches
# ---------------------------------------------------------------------------
def _fiche(tmp_path, graine=7):
    v = vague_type(tmp_path)
    r = audit.produire_tirage([v], tmp_path / "audit", rng=random.Random(graine), graine=graine)
    return r, tmp_path / "audit"


def test_fiche_tau2_aveugle_reglement_entier_et_ecritures_numerotees(tmp_path):
    r, sortie = _fiche(tmp_path)
    t1 = [f for f in r["fiches"] if f["tache"] == "t1"]
    if not t1:  # t1 n'est pas toujours tirée : on la force avec une autre graine
        graines = [g for g in range(50)
                   if any(c["tache"] == "t1" for c in audit.tirer(*_pop(tmp_path), random.Random(g)))]
        r, sortie = _fiche(tmp_path / "bis", graines[0])
        t1 = [f for f in r["fiches"] if f["tache"] == "t1"]
    f = t1[0]
    md = (sortie / "fiches" / f"{f['id']}.md").read_text()
    js = (sortie / "fiches" / f"{f['id']}.json").read_text()
    assert f["ecritures_comptees"] == 2 and f["sans_effet"] == 1
    assert "◄ ÉCRITURE n° 1" in md and "◄ ÉCRITURE n° 2" in md and audit.MARQUE_SANS_EFFET in md
    assert "Paragraphe sans rapport" in md  # règlement entier, pas un extrait
    assert "RAISON-t1" in md and "update_reservation_baggages" in md
    bas = (md + js).lower()
    assert not any(j in bas for j in JETONS)
    assert "sim-a03" not in md + js and "tau2-a03" not in md + js
    fj = json.loads(js)
    assert not {"modele", "partie", "rang", "tache"} & set(fj)
    # le numéro de message du tableau pointe bien sur l'écriture marquée
    for e in fj["ecritures"]:
        assert f"◄ ÉCRITURE n° {e['numero']}" in fj["conversation"][e["message"] - 1]["texte"]


def _pop(tmp_path):
    donnees = audit.charger([tmp_path / "vague1"])
    pop, _ = audit.population(donnees)
    return pop, donnees["ecritures"]


def test_fiche_workbench_marque_la_bonne_etape(tmp_path):
    r, sortie = _fiche(tmp_path)
    f = [f for f in r["fiches"] if f["environnement"] == "WorkBench"][0]
    fj = json.loads((sortie / "fiches" / f"{f['id']}.json").read_text())
    assert fj["ecritures"] == [{"numero": 1, "message": 4, "outil": "email.delete_email"}]
    assert "email.delete_email" in fj["conversation"][3]["texte"] and "◄ ÉCRITURE n° 1" in fj["conversation"][3]["texte"]
    assert fj["conversation"][0]["role"] == "client" and "WorkBench n'a pas de règlement" in fj["reglement"]["note"]
    assert fj["attendues_lisibles"] == ['1. email.delete_email(email_id="00000479")']
    assert not any(j in json.dumps(fj).lower() for j in JETONS)


def test_modele_csv_prerempli(tmp_path):
    r, sortie = _fiche(tmp_path)
    lignes = list(csv.reader(open(sortie / audit.F_MODELE, encoding="utf-8")))
    assert lignes[0] == audit.COLONNES
    assert sorted(l[0] for l in lignes[1:]) == sorted(f["id"] for f in r["fiches"])


# ---------------------------------------------------------------------------
# Réponses et conclusion
# ---------------------------------------------------------------------------
def ecrire_reponses(chemin, lignes, entete=None):
    with open(chemin, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(entete or audit.COLONNES)
        w.writerows(lignes)
    return chemin


def reponses_neutres(r):
    return {f["id"]: [f["id"], "non", "", "", "", str(f["ecritures_comptees"])] for f in r["fiches"]}


def test_reponses_valides(tmp_path):
    r, sortie = _fiche(tmp_path)
    rep = reponses_neutres(r)
    av = [f for f in r["fiches"] if f["environnement"] == "aviation"][0]
    rep[av["id"]] = [av["id"], "Oui", "A2", "l'enregistrement R1 n'existe pas", "1 ; update_reservation_baggages ; "
                     "payment_id ; le client a demandé gift_card_B | écriture n° 1 ; baggages ; total ; autre", "1"]
    lu = audit.lire_reponses(ecrire_reponses(tmp_path / "r.csv", rep.values()), r)
    assert lu[av["id"]]["defectueuse"] and lu[av["id"]]["cas"] == "a2"
    assert [e["ecriture"] for e in lu[av["id"]]["erreurs"]] == [1, 1]


@pytest.mark.parametrize("modif, attendu", [
    (lambda l: l.__setitem__(0, "audit-inconnue"), "fiche inconnue"),
    (lambda l: l.__setitem__(1, "peut-être"), "« oui » ou « non »"),
    (lambda l: (l.__setitem__(1, "oui"), l.__setitem__(3, "preuve")), "sans cas valide"),
    (lambda l: (l.__setitem__(1, "oui"), l.__setitem__(2, "a3")), "sans preuve"),
    (lambda l: l.__setitem__(2, "a1"), "non défectueuse"),
    (lambda l: l.__setitem__(4, "1 ; outil ; champ"), "mal formée"),
    (lambda l: l.__setitem__(4, "9 ; update_reservation_baggages ; champ ; preuve"), "n'est pas le numéro"),
    (lambda l: l.__setitem__(4, "1 ; cancel_reservation ; champ ; preuve"), "pas « cancel_reservation »"),
    (lambda l: l.__setitem__(5, "deux"), "entier"),
])
def test_reponses_refusees(tmp_path, modif, attendu):
    r, sortie = _fiche(tmp_path)
    rep = reponses_neutres(r)
    av = [f for f in r["fiches"] if f["environnement"] == "aviation" and f["ecritures_comptees"]][0]
    modif(rep[av["id"]])
    with pytest.raises(audit.AuditInvalide, match=attendu):
        audit.lire_reponses(ecrire_reponses(tmp_path / "r.csv", rep.values()), r)


def test_reponses_manquante_double_et_entete(tmp_path):
    r, sortie = _fiche(tmp_path)
    rep = list(reponses_neutres(r).values())
    with pytest.raises(audit.AuditInvalide, match="sans réponse"):
        audit.lire_reponses(ecrire_reponses(tmp_path / "a.csv", rep[1:]), r)
    with pytest.raises(audit.AuditInvalide, match="en double"):
        audit.lire_reponses(ecrire_reponses(tmp_path / "b.csv", rep + rep[:1]), r)
    with pytest.raises(audit.AuditInvalide, match="en-tête"):
        audit.lire_reponses(ecrire_reponses(tmp_path / "c.csv", rep, entete=audit.COLONNES[:-1]), r)


def _tirage_synthetique():
    """20 tâches sans alerte en aviation (5 fiches de 2 écritures), 2 en WorkBench (2 fiches d'une écriture) : les
    poids par tâches (20, 2) diffèrent des poids par écritures (10, 2)."""
    fiches_ = [{"id": f"av{k}", "environnement": "aviation", "tache": f"t{k}", "ecritures_comptees": 2,
                "ecritures": [{"numero": 1, "outil": "o"}, {"numero": 2, "outil": "o"}]} for k in range(5)]
    fiches_ += [{"id": f"wb{k}", "environnement": "WorkBench", "tache": f"email:{k}", "ecritures_comptees": 1,
                 "ecritures": [{"numero": 1, "outil": "o"}]} for k in range(2)]
    return {"population": {"aviation": 20, "WorkBench": 2}, "fiches": fiches_}


def _rep(defectueuse=False, cas="", erreurs=(), lues=None):
    return {"defectueuse": defectueuse, "cas": cas, "preuve": "p" if defectueuse else "",
            "erreurs": [{"ecriture": k, "outil": "o", "champ": c, "preuve": "p"} for k, c in erreurs],
            "ecritures_lues": lues}


def test_taux_pondere_par_les_taches_sans_alerte_et_une_erreur_par_ecriture():
    t = _tirage_synthetique()
    rep = {f["id"]: _rep(lues=f["ecritures_comptees"]) for f in t["fiches"]}
    rep["av0"] = _rep(erreurs=[(1, "payment_id"), (1, "total")], lues=2)  # deux champs, une seule écriture
    rep["wb1"] = _rep(erreurs=[(1, "email_id")], lues=1)
    c = audit.conclure(t, rep)
    m = c["mesure"]
    assert m["par_environnement"]["aviation"]["erreurs_invisibles"] == 1
    assert m["par_environnement"]["aviation"]["taux"] == pytest.approx(0.1)
    assert m["par_environnement"]["WorkBench"]["taux"] == pytest.approx(0.5)
    assert m["taux_pondere"] == pytest.approx((20 * 0.1 + 2 * 0.5) / 22)  # ni (1 + 1) / 12, ni pondéré par écritures
    assert m["poids"] == pytest.approx({"WorkBench": 2 / 22, "aviation": 20 / 22})
    assert len(c["erreurs_invisibles"]) == 3 and c["retraits"] == [] and c["ecarts_de_compte"] == []


def test_tache_retiree_hors_mesure_opposition_et_ecart_de_compte():
    t = _tirage_synthetique()
    rep = {f["id"]: _rep(lues=f["ecritures_comptees"]) for f in t["fiches"]}
    rep["av1"] = _rep(defectueuse=True, cas="a1", erreurs=[(2, "x")], lues=2)
    rep["av2"] = _rep(defectueuse=True, cas="a4", lues=3)
    c = audit.conclure(t, rep, oppositions=["av2"])
    assert [r["tache"] for r in c["retraits"]] == ["t1"] and [r["tache"] for r in c["oppositions"]] == ["t2"]
    m = c["mesure"]
    assert m["hors_mesure"] == {"fiches": 1, "ecritures": 2, "erreurs_invisibles": 1}
    assert m["par_environnement"]["aviation"]["fiches"] == 4 and m["par_environnement"]["aviation"]["ecritures"] == 8
    assert c["ecarts_de_compte"] == [{"id": "av2", "programme": 2, "relecteur": 3}]
    with pytest.raises(audit.AuditInvalide, match="pas proposée au retrait"):
        audit.conclure(t, rep, oppositions=["av3"])


def test_chaine_complete_cli(tmp_path, capsys):
    v = vague_type(tmp_path)
    sortie = tmp_path / "audit"
    assert audit.main(["tirer", "--dossier", str(v), "--sortie", str(sortie)]) == 0
    r = json.loads((sortie / audit.F_TIRAGE).read_text())
    rep = reponses_neutres(r)
    av = [f for f in r["fiches"] if f["environnement"] == "aviation"][0]
    rep[av["id"]] = [av["id"], "oui", "a3", "la consigne demande l'inverse", "", str(av["ecritures_comptees"])]
    chemin = ecrire_reponses(tmp_path / "reponses.csv", rep.values())
    args = ["conclure", "--sortie", str(sortie), "--reponses", str(chemin)]
    assert audit.main(args + ["--apercu"]) == 0
    assert "aperçu" in capsys.readouterr().out and not (sortie / audit.F_CONCLUSION).exists()
    assert audit.main(args) == 0
    with open(sortie / audit.F_RETRAITS, encoding="utf-8") as f:
        retirees = [tuple(x) for x in json.load(f)]  # comme bout_en_bout.py --retirees
    assert retirees == [("aviation", av["tache"])]
    c = json.loads((sortie / audit.F_CONCLUSION).read_text())
    assert c["retraits"][0]["cas"] == "a3" and len(c["tirage_sha256"]) == 64
    assert "Retraits (1)" in (sortie / audit.F_TEXTE).read_text()
    assert audit.main(args) == 2  # une conclusion ne se refait pas
    assert "ne se refait pas" in capsys.readouterr().err


def test_fiche_modifiee_apres_le_tirage_refusee(tmp_path):
    r, sortie = _fiche(tmp_path)
    chemin = sortie / "fiches" / f"{r['fiches'][0]['id']}.md"
    chemin.write_text(chemin.read_text() + "\najout\n")
    rep = ecrire_reponses(tmp_path / "r.csv", reponses_neutres(r).values())
    with pytest.raises(audit.AuditInvalide, match="a changé depuis le tirage"):
        audit.produire_conclusion(sortie, rep)


def test_audit_refait_ailleurs_refuse_par_le_journal(tmp_path):
    """Relecture C13, P11 : l'audit inscrit au journal d'une vague ne se refait pas dans un autre dossier."""
    v = vague_type(tmp_path)
    audit.produire_tirage([v], tmp_path / "audit", rng=random.Random(1), graine=1)
    with pytest.raises(audit.AuditInvalide, match="journal"):
        audit.produire_tirage([v], tmp_path / "audit_bis", rng=random.Random(2), graine=2)
