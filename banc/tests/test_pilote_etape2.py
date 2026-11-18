"""Tests de banc/pilote_etape2.py. Aucun appel réel : fausse clé, exécuteur factice, bancs redirigés vers des dossiers vides."""
import json
import os

import pytest

import pilote_etape1 as pe
import pilote_etape2 as p2

CLE = "sk-ant-FAUSSE-CLE-DE-TEST-123456"


def fichier_cle(tmp_path):
    p = tmp_path / "anthropic.env"
    p.write_text(f"ANTHROPIC_API_KEY={CLE}\n", encoding="utf-8")
    os.chmod(p, 0o600)
    return p


def dev_json(tmp_path, n_wb=8):
    d = {
        "aviation": [str(i) for i in (11, 13, 21, 23, 31, 32, 39, 41, 46, 5)],
        "commerce": [str(i) for i in range(100, 123)],
        "banque": [f"task_{i:03d}" for i in range(3, 23)],
        "WorkBench": [f"{p}:{i}" for p in ("analytics", "calendar", "customer_relationship_manager", "email", "multi_domain", "project_management")
                      for i in range(n_wb)],
    }
    f = tmp_path / "dev.json"
    f.write_text(json.dumps(d))
    return f, d


# ---------------------------------------------------------------- choix des tâches
def test_dix_premieres_dans_l_ordre_de_la_liste(tmp_path):
    f, d = dev_json(tmp_path)
    t, factice = p2.charger_taches(f, reel=True)
    assert factice is False
    for env in ("aviation", "commerce", "banque"):
        assert t[env] == d[env][:10]


def test_workbench_tourniquet_sur_les_fichiers_dans_l_ordre_demande(tmp_path):
    f, d = dev_json(tmp_path)
    t, _ = p2.charger_taches(f, reel=True)
    wb = t["WorkBench"]
    assert len(wb) == 10
    ordre = ["email", "calendar", "customer_relationship_manager", "project_management", "analytics", "multi_domain"]
    assert [x.split(":")[0] for x in wb] == ordre + ordre[:4]
    # dans chaque fichier : ordre de la liste (pas l'ordre numérique)
    assert wb[0] == "email:0" and wb[6] == "email:1" and wb[7] == "calendar:1"


def test_workbench_ordre_de_liste_respecte(tmp_path):
    f, d = dev_json(tmp_path)
    d["WorkBench"] = ["email:9", "email:2"] + [x for x in d["WorkBench"] if not x.startswith("email")]
    f.write_text(json.dumps(d))
    t, _ = p2.charger_taches(f, reel=True)
    assert t["WorkBench"][0] == "email:9" and t["WorkBench"][6] == "email:2"


def test_workbench_fichier_epuise_est_saute(tmp_path):
    f, d = dev_json(tmp_path)
    d["WorkBench"] = [x for x in d["WorkBench"] if not x.startswith("analytics")] + ["analytics:0"]
    f.write_text(json.dumps(d))
    t, _ = p2.charger_taches(f, reel=True)
    assert len(t["WorkBench"]) == 10 and t["WorkBench"].count("analytics:0") == 1


def test_liste_trop_courte_refusee(tmp_path):
    f, d = dev_json(tmp_path)
    d["aviation"] = d["aviation"][:9]
    f.write_text(json.dumps(d))
    with pytest.raises(pe.ErreurPilote):
        p2.charger_taches(f, reel=True)
    f, d = dev_json(tmp_path, n_wb=1)  # 6 tâches WorkBench seulement
    with pytest.raises(pe.ErreurPilote):
        p2.charger_taches(f, reel=True)


def test_fichier_absent_refus_en_reel_liste_factice_a_blanc(tmp_path):
    with pytest.raises(pe.ErreurPilote):
        p2.charger_taches(tmp_path / "absent.json", reel=True)
    t, factice = p2.charger_taches(tmp_path / "absent.json", reel=False)
    assert factice and all(len(v) == 10 for v in t.values())


def test_taches_2a_sont_celles_de_l_etape_1(tmp_path):
    f, d = dev_json(tmp_path)
    t, _ = p2.charger_taches(f, reel=True, etape="2a")
    assert t == {"aviation": [d["aviation"][0]], "banque": [d["banque"][0]]}


def test_memes_taches_pour_les_trois_modeles(tmp_path):
    f, _ = dev_json(tmp_path)
    t, _ = p2.charger_taches(f, reel=True)
    parties = p2.construire_parties(t, p2.MODELES)
    for env in p2.ENVS:
        for rang in range(1, 11):
            ids = {p["tache"] for p in parties if p["env"] == env and p["rang"] == rang}
            assert len(ids) == 1


# ---------------------------------------------------------------- ordre et combinaisons
def test_nombre_de_parties_et_ordre_intercale(tmp_path):
    f, _ = dev_json(tmp_path)
    t, _ = p2.charger_taches(f, reel=True)
    parties = p2.construire_parties(t, p2.MODELES)
    assert len(parties) == 120 and len({p["id"] for p in parties}) == 120
    assert [p["modele"] for p in parties[:3]] == ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"]
    assert [p["env"] for p in parties[:12:3]] == ["aviation", "commerce", "banque", "WorkBench"]
    assert all(p["rang"] == 1 for p in parties[:12]) and all(p["rang"] == 2 for p in parties[12:24])
    assert parties[0]["id"] == "aviation-haiku-1" and parties[2]["id"] == "aviation-opus-1"
    # ordre strict : rang, puis environnement, puis modèle
    cles = [(p["rang"], p2.ENVS.index(p["env"]), p2.MODELES.index(p["modele"])) for p in parties]
    assert cles == sorted(cles)


def test_modeles_et_client_simule():
    assert p2.MODELES == ("claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5")
    assert p2.MODELE_USER == "anthropic/claude-haiku-5-5"


# ---------------------------------------------------------------- cache : points d'injection et commande
def test_points_injection():
    pts = p2.points_injection()
    assert pts == [{"location": "message", "role": "system"}, {"location": "message", "index": -1}]
    assert len(pts) <= 4 == p2.MAX_POINTS_CACHE


def test_points_injection_plus_de_quatre_refuse():
    with pytest.raises(pe.ErreurPilote):
        p2.verifier_points([{"location": "message", "index": i} for i in range(5)])


def arg(cmd, nom):
    return json.loads(cmd[cmd.index(nom) + 1])


def partie(env="aviation", modele="claude-sonnet-5-5", tache="11"):
    return {"id": f"{env}-x-1", "env": env, "tache": tache, "rang": 1, "modele": modele}


def test_commande_reel_sans_cache_args_vides_et_modeles():
    cmd = p2.commande_tau2(partie(), "nom", reel=True, cache=False)
    assert arg(cmd, "--agent-llm-args") == {} and arg(cmd, "--user-llm-args") == {}
    assert cmd[cmd.index("--agent-llm") + 1] == "anthropic/claude-sonnet-5-5"
    assert cmd[cmd.index("--user-llm") + 1] == "anthropic/claude-haiku-5-5"
    assert cmd[cmd.index("--max-steps") + 1] == "100" and cmd[cmd.index("--max-concurrency") + 1] == "1"
    assert "--communicate-scorer" in cmd and cmd[cmd.index("--communicate-scorer") + 1] == "substring"
    assert cmd[cmd.index("--task-ids") + 1] == "11" and "temperature" not in " ".join(cmd)


def test_commande_reel_avec_cache():
    cmd = p2.commande_tau2(partie("banque", "claude-opus-5-5", "task_003"), "nom", reel=True, cache=True)
    for nom in ("--agent-llm-args", "--user-llm-args"):
        assert arg(cmd, nom) == {"cache_control_injection_points": p2.points_injection()}
    assert cmd[cmd.index("--retrieval-config") + 1] == "bm25_grep" and cmd[cmd.index("--agent-llm") + 1].endswith("opus-5-5")


def test_commande_blanc_garde_les_reponses_factices():
    cmd = p2.commande_tau2(partie(), "nom", reel=False, cache=True)
    a = arg(cmd, "--agent-llm-args")
    assert a["mock_response"] == "ok" and "cache_control_injection_points" in a
    assert cmd[cmd.index("--max-steps") + 1] == "8"


def test_commande_ne_contient_aucune_cle():
    cmd = " ".join(p2.commande_tau2(partie(), "nom", reel=True, cache=True))
    assert "sk-ant" not in cmd and "API_KEY" not in cmd


def test_commande_workbench_modele():
    cmd = p2.commande_workbench("/x/email.csv", "claude-opus-5-5")
    assert cmd[cmd.index("--model_name") + 1] == "claude-opus-5-5" and "--structured_outputs" in cmd
    assert "cache" not in " ".join(cmd)  # pas de cache pour WorkBench (voir INSTALLATION.md)


# ---------------------------------------------------------------- plafond
@pytest.mark.parametrize("etape,plafond,ok", [("2", "40", True), ("2", "40.01", False), ("2", "100", False), ("2", "0", False), ("2", "nan", False),
                                              ("2a", "0.10", True), ("2a", "0.11", False), ("2a", "1", False)])
def test_plafond_par_etape(etape, plafond, ok):
    a = p2.analyser(["--etape", etape, "--reel", "--plafond-usd", plafond])
    if ok:
        assert p2.verifier_plafond(a) == float(plafond)
    else:
        with pytest.raises(pe.ErreurPilote):
            p2.verifier_plafond(a)


def test_reel_exige_plafond_et_etape(capsys):
    assert p2.main(["--etape", "2", "--reel"]) == 2 and "plafond" in capsys.readouterr().err
    with pytest.raises(SystemExit):
        p2.analyser(["--reel", "--plafond-usd", "1"])


def test_concurrence_defaut_2_max_3():
    assert p2.analyser(["--etape", "2"]).concurrence == 2
    assert p2.analyser(["--etape", "2a"]).concurrence == 1
    assert p2.analyser(["--etape", "2", "--concurrence", "3"]).concurrence == 3
    with pytest.raises(SystemExit):
        p2.analyser(["--etape", "2", "--concurrence", "4"])


def test_refus_de_plafond_ne_cree_aucun_dossier(tmp_path):
    rc = p2.main(["--etape", "2", "--reel", "--plafond-usd", "41", "--sortie-racine", str(tmp_path / "s")], chemin_cle=fichier_cle(tmp_path))
    assert rc == 2 and not (tmp_path / "s").exists()


# ---------------------------------------------------------------- exécution (exécuteur factice)
def faux_appels(modele="claude-haiku-5-5", p=1000, s=100, cc=0, cr=0, n=1):
    return [{"modele": modele, "prompt_tokens": p, "completion_tokens": s, "cache_creation_input_tokens": cc,
             "cache_read_input_tokens": cr}] * n


def executeur_factice(p=1000, s=100, ok=True, trace=None, modele_de_partie=True, cc=0, cr=0):
    def f(partie, ctx):
        if trace is not None:
            trace.append((partie["id"], ctx["reel"], dict(ctx["env_enfant"]), ctx["cache"]))
        m = partie["modele"] if modele_de_partie else "claude-haiku-5-5"
        return {"ok": ok, "appels": faux_appels(m, p, s, cc, cr) if p is not None else None,
                "erreur": None if ok else "échec", "copies": [], "estime": False}
    return f


def neutraliser(monkeypatch, tmp_path):
    monkeypatch.setattr(pe, "TAU2", tmp_path / "tau2")
    monkeypatch.setattr(p2, "TAU2", tmp_path / "tau2")
    monkeypatch.setattr(p2, "WB_RUN", tmp_path / "wbrun")
    monkeypatch.setattr(p2, "WORKBENCH", tmp_path / "wb")
    monkeypatch.setattr(p2, "verifier_taches_existent", lambda *a, **k: None)

    def faux_post(sortie, *a, **k):
        (sortie / "resume.txt").write_text("résumé factice")
        return {}

    monkeypatch.setattr(p2, "post_traitement", faux_post)


def lancer(tmp_path, executeur, plafond, concurrence=1, n=24, cache=True, reel=True):
    sortie = tmp_path / "sortie"
    sortie.mkdir(exist_ok=True)
    ctx = {"sortie": sortie, "reel": reel, "env_enfant": {}, "cle": None, "horodatage": "t", "cache": cache}
    f, _ = dev_json(tmp_path)
    t, _ = p2.charger_taches(f, reel=True)
    parties = p2.construire_parties(t, p2.MODELES)[:n]
    journal = pe.Journal(sortie / "journal.log")
    compta = pe.Comptable(plafond)
    res = p2.lancer_parties(parties, concurrence, compta, ctx, journal, executeur, etape="2")
    return res, compta, json.loads((sortie / "cout.json").read_text()), (sortie / "journal.log").read_text()


def test_cout_par_modele_de_la_partie(tmp_path):
    res, compta, cout, _ = lancer(tmp_path, executeur_factice(p=100_000, s=0), plafond=40.0, n=3)
    assert [round(r["cout_usd"], 6) for r in res] == [0.01, 0.2, 0.4]
    assert cout["cumul_usd"] == pytest.approx(0.61)


def test_arret_a_80_pour_cent_avant_toute_nouvelle_partie(tmp_path):
    # 1 M jetons Opus = 4 $ par partie ; plafond 10 -> seuil 8 : 2 parties
    ex = executeur_factice(p=1_000_000, s=0, modele_de_partie=False)
    res, compta, cout, journal = lancer(tmp_path, lambda p, c: dict(ex(p, c), appels=faux_appels("claude-opus-5-5", 1_000_000, 0)), plafond=10.0, n=12)
    assert len(res) == 2 and compta.cumul == pytest.approx(8.0) and cout["arret"] and "ARRÊT" in journal


def test_arret_usage_illisible_et_echec_et_exception(tmp_path):
    res, compta, cout, _ = lancer(tmp_path, executeur_factice(p=None, ok=False), plafond=40.0)
    assert len(res) == 1 and compta.arret and cout["parties"][0]["cout_usd"] is None

    def boum(partie, ctx):
        raise RuntimeError("secret " + CLE)

    res, compta, cout, journal = lancer(tmp_path / "b" if (tmp_path / "b").mkdir() is None else tmp_path, boum, plafond=40.0)
    assert len(res) == 1 and compta.arret and CLE not in json.dumps(cout) and CLE not in journal


def test_modele_inconnu_dans_l_usage_arrete(tmp_path):
    ex = executeur_factice()
    res, compta, cout, _ = lancer(tmp_path, lambda p, c: dict(ex(p, c), appels=faux_appels("gpt-9")), plafond=40.0)
    assert len(res) == 1 and compta.arret and "modèle inconnu" in compta.arret.lower()


def test_cout_json_contient_cache_et_prix(tmp_path):
    _, _, cout, _ = lancer(tmp_path, executeur_factice(p=10_000, s=10, cc=2000, cr=3000), plafond=40.0, n=3)
    p = cout["parties"][0]
    assert p["cache_ecriture"] == 2000 and p["cache_lecture"] == 3000 and p["jetons_entree"] == 10_000 and p["jetons_non_caches"] == 5000
    assert cout["cache"] is True and "claude-opus-5-5" in cout["prix_usd_par_million"]
    assert cout["seuil_arret_usd"] == pytest.approx(32.0)


def test_concurrence_trois_respecte_l_arret(tmp_path):
    ex = executeur_factice(p=1_000_000, s=0, modele_de_partie=False)
    res, compta, _, _ = lancer(tmp_path, lambda p, c: dict(ex(p, c), appels=faux_appels("claude-opus-5-5", 1_000_000, 0)), plafond=10.0, concurrence=3, n=12)
    assert 2 <= len(res) <= 4 and compta.doit_arreter()


# ---------------------------------------------------------------- main : blanc, réel, garde-fous
def test_blanc_ne_lit_pas_la_cle_et_nettoie_l_environnement(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    trace = []
    base = {"PATH": "/usr/bin", "OPENAI_API_KEY": "o", "OPENROUTER_API_KEY": "r", "ANTHROPIC_API_KEY": "parent"}
    f, _ = dev_json(tmp_path)
    rc = p2.main(["--etape", "2", "--developpement", str(f), "--sortie-racine", str(tmp_path / "s")],
                 executeur=executeur_factice(trace=trace), base_env=base, chemin_cle=tmp_path / "ne-pas-lire")
    assert rc == 0 and len(trace) == 120
    for _id, reel, env, cache in trace:
        assert reel is False and "ANTHROPIC_API_KEY" not in env and env["PILOTE_HORS_LIGNE"] == "2" and cache is False
    (d,) = list((tmp_path / "s").iterdir())
    assert d.name.endswith("-blanc")


def test_2a_blanc_deux_parties_cache_force(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    trace = []
    f, d = dev_json(tmp_path)
    rc = p2.main(["--etape", "2a", "--developpement", str(f), "--sortie-racine", str(tmp_path / "s")],
                 executeur=executeur_factice(trace=trace), base_env={})
    assert rc == 0 and [t[0] for t in trace] == ["aviation-haiku-1", "banque-haiku-1"] and all(t[3] is True for t in trace)


def test_reel_cle_fausse_environnement_et_pas_de_fuite(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    sim = tmp_path / "tau2" / "data" / "simulations"
    (sim / "essai-blanc-vieux").mkdir(parents=True)
    f, _ = dev_json(tmp_path)
    trace = []
    base = {"PATH": "/usr/bin", "OPENAI_API_KEY": "o", "OPENROUTER_API_KEY": "r", "PILOTE_USAGE_FILE": "/ailleurs"}
    rc = p2.main(["--etape", "2", "--cache", "--reel", "--plafond-usd", "40", "--developpement", str(f), "--sortie-racine", str(tmp_path / "s")],
                 executeur=executeur_factice(trace=trace), base_env=base, chemin_cle=fichier_cle(tmp_path))
    assert rc == 0 and len(trace) == 120
    for _id, reel, env, cache in trace:
        assert reel and env["ANTHROPIC_API_KEY"] == CLE and "OPENROUTER_API_KEY" not in env and "PILOTE_USAGE_FILE" not in env and cache is True
    assert not (sim / "essai-blanc-vieux").exists()
    (d,) = list((tmp_path / "s").iterdir())
    for fic in d.rglob("*"):
        if fic.is_file():
            assert CLE not in fic.read_text(errors="ignore"), fic


def test_reel_refuse_cle_mal_protegee_sans_rien_lancer(tmp_path, monkeypatch, capsys):
    neutraliser(monkeypatch, tmp_path)
    c = fichier_cle(tmp_path)
    os.chmod(c, 0o644)
    trace = []
    f, _ = dev_json(tmp_path)
    rc = p2.main(["--etape", "2", "--reel", "--plafond-usd", "5", "--developpement", str(f), "--sortie-racine", str(tmp_path / "s")],
                 executeur=executeur_factice(trace=trace), base_env={}, chemin_cle=c)
    assert rc == 2 and not trace and CLE not in capsys.readouterr().err


def test_reel_refuse_dotenv(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    (tmp_path / "tau2").mkdir()
    (tmp_path / "tau2" / ".env").write_text("OPENAI_API_KEY=x")
    trace = []
    f, _ = dev_json(tmp_path)
    rc = p2.main(["--etape", "2", "--reel", "--plafond-usd", "5", "--developpement", str(f), "--sortie-racine", str(tmp_path / "s")],
                 executeur=executeur_factice(trace=trace), base_env={}, chemin_cle=fichier_cle(tmp_path))
    assert rc == 2 and not trace


def test_env_usage_pose_apres_env_enfant():
    env = pe.env_enfant({"PILOTE_USAGE_FILE": "/x", "PATH": "/b"}, CLE)
    assert "PILOTE_USAGE_FILE" not in env  # retiré par env_enfant
    e = p2.env_partie(env, "/tmp/u.jsonl")
    assert e["PILOTE_USAGE_FILE"] == "/tmp/u.jsonl" and "PILOTE_USAGE_FILE" not in env
    pe.verifier_env_enfant(env, True)  # l'original reste valide


# ---------------------------------------------------------------- lecture de l'usage d'une partie tau2
def results_json(tmp_path, usages):
    msgs = [{"role": "assistant", "content": "salut", "usage": None}]
    for i, (p, s) in enumerate(usages):
        msgs.append({"role": "user" if i % 2 == 0 else "assistant", "content": "x", "usage": {"prompt_tokens": p, "completion_tokens": s}})
    f = tmp_path / "results.json"
    f.write_text(json.dumps({"simulations": [{"messages": msgs}]}))
    return f


def test_usage_partie_tau2_reel_depuis_jsonl_et_croisement(tmp_path):
    r = results_json(tmp_path, [(100, 5), (200, 6)])
    u = tmp_path / "u.jsonl"
    u.write_text("".join(json.dumps(x) + "\n" for x in faux_appels("claude-haiku-5-5", 100, 5, 20, 30) + faux_appels("claude-opus-5-5", 200, 6)))
    appels, estime = p2.usage_partie_tau2(r, u, "claude-opus-5-5", reel=True)
    assert len(appels) == 2 and estime is False and appels[0]["cache_read_input_tokens"] == 30


def test_usage_partie_tau2_reel_jsonl_absent_ou_incoherent_leve(tmp_path):
    r = results_json(tmp_path, [(100, 5), (200, 6)])
    with pytest.raises(ValueError):
        p2.usage_partie_tau2(r, tmp_path / "absent.jsonl", "claude-opus-5-5", reel=True)
    u = tmp_path / "u.jsonl"
    u.write_text(json.dumps(faux_appels("claude-opus-5-5", 100, 5)[0]) + "\n")  # une ligne sur deux
    with pytest.raises(ValueError):
        p2.usage_partie_tau2(r, u, "claude-opus-5-5", reel=True)


def test_usage_partie_tau2_blanc_estime_si_jsonl_absent(tmp_path):
    r = results_json(tmp_path, [(100, 5)])
    appels, estime = p2.usage_partie_tau2(r, tmp_path / "absent.jsonl", "claude-opus-5-5", reel=False)
    assert estime is True and appels and all(a["modele"] == "claude-opus-5-5" for a in appels)


# ---------------------------------------------------------------- résumé et rapport 2a
def test_resume_par_env_et_modele():
    lignes = [
        {"banc": "tau2", "domaine": "airline", "kind": "lecture", "verdict": "", "type": "lecture", "modele": "anthropic/claude-haiku-5-5"},
        {"banc": "tau2", "domaine": "airline", "kind": "écriture", "verdict": "juste", "type": "argent", "modele": "anthropic/claude-opus-5-5"},
        {"banc": "tau2", "domaine": "airline", "kind": "écriture", "verdict": "fausse", "type": "argent", "modele": "anthropic/claude-opus-5-5"},
        {"banc": "workbench", "domaine": "email", "kind": "écriture", "verdict": "juste", "type": "message interne", "modele": "claude-opus-5-5"},
    ]
    parties = [
        {"id": "aviation-haiku-1", "env": "aviation", "modele": "claude-haiku-5-5", "ok": True, "jetons_entree": 10, "jetons_sortie": 5,
         "cache_ecriture": 1, "cache_lecture": 2, "cout_usd": 0.5},
        {"id": "aviation-opus-1", "env": "aviation", "modele": "claude-opus-5-5", "ok": True, "jetons_entree": 20, "jetons_sortie": 6,
         "cache_ecriture": 3, "cache_lecture": 4, "cout_usd": 1.5},
        {"id": "WorkBench-opus-1", "env": "WorkBench", "modele": "claude-opus-5-5", "ok": False, "jetons_entree": None, "jetons_sortie": None, "cout_usd": None},
    ]
    r = p2.resume_par_env_modele(lignes, parties)
    op = r["aviation"]["claude-opus-5-5"]
    assert (op["parties_lancees"], op["actions"], op["ecritures"]) == (1, 2, 2)
    assert op["ecritures_par_verdict"] == {"fausse": 1, "juste": 1} and op["ecritures_par_type"] == {"argent": 2}
    assert (op["jetons_entree"], op["cache_ecriture"], op["cache_lecture"], op["cout_usd"]) == (20, 3, 4, 1.5)
    assert r["aviation"]["claude-haiku-5-5"]["lectures"] == 1
    assert r["WorkBench"]["claude-opus-5-5"]["ecritures_par_type"] == {"message interne": 1} and r["banque"]["claude-opus-5-5"]["parties_lancees"] == 0
    tot = p2.resume_par_modele(r)
    assert tot["claude-opus-5-5"]["cout_usd"] == 1.5 and tot["claude-opus-5-5"]["ecritures"] == 3


def test_rapport_2a():
    parties = [
        {"id": "aviation-haiku-1", "env": "aviation", "ok": True, "jetons_entree": 100_000, "jetons_non_caches": 20_000, "cache_ecriture": 10_000,
         "cache_lecture": 70_000, "jetons_sortie": 5000, "cout_usd": 0.0100},
        {"id": "banque-haiku-1", "env": "banque", "ok": True, "jetons_entree": 100_000, "jetons_non_caches": 100_000, "cache_ecriture": 0,
         "cache_lecture": 0, "jetons_sortie": 3000, "cout_usd": 0.0158345},
    ]
    r = p2.rapport_2a(parties)
    av, bq = r["parties"]
    assert av["ref_etape1_usd"] == 0.0153169 and bq["ref_etape1_usd"] == 0.0158345
    assert av["cache_lecture"] == 70_000 and av["cache_ecriture"] == 10_000 and av["cout_v2_usd"] == 0.01
    assert av["variation_pct"] == pytest.approx((0.0100 / 0.0153169 - 1) * 100, abs=0.01) and bq["variation_pct"] == pytest.approx(0.0)
    assert av["part_cache_lu_pct"] == pytest.approx(70.0)
    assert "aviation-haiku-1" in p2.rapport_2a_texte(r) and "0.0153" in p2.rapport_2a_texte(r)


def test_prix_etape1_de_reference_coherents_avec_cout_v2():
    # Les 2 coûts de l'étape 1 retenus pour la comparaison doivent exister dans le dossier de sortie de l'étape 1 s'il est là.
    chemin = p2.RACINE / "pilote" / "etape1" / "2026-11-05_07-25-06" / "cout.json"
    if not chemin.is_file():
        pytest.skip("sortie de l'étape 1 absente")
    d = {x["id"]: x["cout_usd"] for x in json.loads(chemin.read_text())["parties"]}
    assert d["aviation-1"] == pytest.approx(p2.REF_ETAPE1["aviation"], abs=1e-7) and d["banque-1"] == pytest.approx(p2.REF_ETAPE1["banque"], abs=1e-7)
