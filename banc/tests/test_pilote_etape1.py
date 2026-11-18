"""Tests de banc/pilote_etape1.py. Aucun appel réel : fausse clé dans un fichier temporaire, exécuteur factice,
aucun enfant lancé (sauf un petit python local qui affiche sa variable d'environnement, pour tester la purge du journal)."""
import json
import os
import stat
import sys

import pytest

import pilote_etape1 as pe
import usage_wrap

CLE = "sk-ant-FAUSSE-CLE-DE-TEST-123456"


def fichier_cle(tmp_path, contenu=f"ANTHROPIC_API_KEY={CLE}\n", mode=0o600):
    p = tmp_path / "anthropic.env"
    p.write_text(contenu, encoding="utf-8")
    os.chmod(p, mode)
    return p


# ---------------------------------------------------------------- clé
def test_lire_cle_ok(tmp_path):
    assert pe.lire_cle(fichier_cle(tmp_path)) == CLE


@pytest.mark.parametrize("contenu", [f"export ANTHROPIC_API_KEY={CLE}\n", f'ANTHROPIC_API_KEY="{CLE}"\n',
                                     f"# note\nAUTRE=1\nANTHROPIC_API_KEY={CLE}\n"])
def test_lire_cle_formes(tmp_path, contenu):
    assert pe.lire_cle(fichier_cle(tmp_path, contenu)) == CLE


@pytest.mark.parametrize("mode", [0o644, 0o640, 0o660, 0o400, 0o700, 0o666])
def test_cle_refusee_si_permissions_pas_600(tmp_path, mode):
    p = fichier_cle(tmp_path, mode=mode)
    with pytest.raises(pe.ErreurPilote) as e:
        pe.lire_cle(p)
    assert CLE not in str(e.value)


@pytest.mark.parametrize("contenu", ["ANTHROPIC_API_KEY=\n", "ANTHROPIC_API_KEY=   \n", 'ANTHROPIC_API_KEY=""\n', ""])
def test_cle_vide_ou_absente_refusee(tmp_path, contenu):
    with pytest.raises(pe.ErreurPilote):
        pe.lire_cle(fichier_cle(tmp_path, contenu))


def test_cle_ligne_absente_et_fichier_absent(tmp_path):
    with pytest.raises(pe.ErreurPilote) as e:
        pe.lire_cle(fichier_cle(tmp_path, f"OPENAI_API_KEY={CLE}\n"))
    assert CLE not in str(e.value)
    with pytest.raises(pe.ErreurPilote):
        pe.lire_cle(tmp_path / "absent.env")


def test_cle_dossier_refuse(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    os.chmod(d, 0o600)
    with pytest.raises(pe.ErreurPilote):
        pe.lire_cle(d)


def test_chemin_cle_par_defaut():
    assert str(pe.CHEMIN_CLE).endswith(".config/autonomie-meritee/anthropic.env")


# ---------------------------------------------------------------- environnement des enfants
PARENT = {
    "PATH": "/usr/bin", "HOME": "/h", "LANG": "fr_FR.UTF-8",
    "OPENAI_API_KEY": "o", "OPENROUTER_API_KEY": "r", "GOOGLE_API_KEY": "g", "GEMINI_API_KEY": "g2", "XAI_API_KEY": "x",
    "AZURE_API_KEY": "a", "MISTRAL_API_KEY": "m", "ANTHROPIC_AUTH_TOKEN": "t", "ANTHROPIC_API_KEY": "autre-cle",
    "ANTHROPIC_BASE_URL": "https://proxy.exemple", "OPENAI_BASE_URL": "https://x", "AWS_SECRET_ACCESS_KEY": "s",
    "GROQ_API_KEY": "q", "GOOGLE_APPLICATION_CREDENTIALS": "/c.json", "MA_VARIABLE_SECRET": "z", "PILOTE_HORS_LIGNE": "1",
    "LITELLM_API_KEY": "l", "HF_TOKEN": "h",
}


def test_env_reel_ne_garde_que_la_cle_anthropic_du_fichier():
    env = pe.env_enfant(PARENT, CLE)
    assert env["ANTHROPIC_API_KEY"] == CLE
    for k in PARENT:
        if k not in ("PATH", "HOME", "LANG", "ANTHROPIC_API_KEY"):
            assert k not in env, k
    assert env["PATH"] == "/usr/bin" and env["LITELLM_LOCAL_MODEL_COST_MAP"] == "True"
    pe.verifier_env_enfant(env, reel=True)


def test_env_reel_cas_openrouter_impossible():
    env = pe.env_enfant(PARENT, CLE)
    assert "OPENROUTER_API_KEY" not in env and env["ANTHROPIC_API_KEY"]
    env["OPENROUTER_API_KEY"] = "r"
    with pytest.raises(pe.ErreurPilote):
        pe.verifier_env_enfant(env, reel=True)


def test_verifier_env_refuse_sans_cle_anthropic_en_reel():
    env = pe.env_enfant(PARENT, CLE)
    del env["ANTHROPIC_API_KEY"]
    with pytest.raises(pe.ErreurPilote):
        pe.verifier_env_enfant(env, reel=True)


def test_verifier_env_refuse_hors_ligne_en_reel():
    env = pe.env_enfant(PARENT, CLE)
    env["PILOTE_HORS_LIGNE"] = "2"
    with pytest.raises(pe.ErreurPilote):
        pe.verifier_env_enfant(env, reel=True)


def test_env_a_blanc_sans_aucune_cle_et_hors_ligne():
    env = pe.env_enfant(PARENT, None)
    assert not [k for k in env if "KEY" in k or "TOKEN" in k or "SECRET" in k]
    assert env["PILOTE_HORS_LIGNE"] == "2"
    assert env["HTTPS_PROXY"] == pe.PROXY_CASSE
    pe.verifier_env_enfant(env, reel=False)
    env["ANTHROPIC_API_KEY"] = "x"
    with pytest.raises(pe.ErreurPilote):
        pe.verifier_env_enfant(env, reel=False)


def test_dotenv_refuse(tmp_path):
    pe.verifier_pas_de_dotenv(tmp_path)
    (tmp_path / ".env").write_text("OPENROUTER_API_KEY=x")
    with pytest.raises(pe.ErreurPilote):
        pe.verifier_pas_de_dotenv(tmp_path)


def test_cle_jamais_en_argument(tmp_path):
    parties = pe.construire_parties(pe.LISTE_FACTICE)
    for reel in (True, False):
        for p in parties:
            if p["env"] == "WorkBench":
                cmd = pe.commande_workbench(tmp_path / "x.csv")
            else:
                cmd = pe.commande_tau2(p, "nom", reel)
            assert CLE not in " ".join(cmd) and "sk-ant" not in " ".join(cmd)


def test_enfant_sortie_purgee_de_la_cle(tmp_path):
    env = pe.env_enfant({"PATH": os.environ["PATH"]}, CLE)
    log = tmp_path / "enfant.log"
    code = pe.executer_enfant([sys.executable, "-c", "import os;print(os.environ['ANTHROPIC_API_KEY']);"
                               "print('autre', os.environ.get('OPENAI_API_KEY'))"], env, tmp_path, log, CLE)
    assert code == 0
    texte = log.read_text()
    assert CLE not in texte and "***" in texte and "autre None" in texte


def test_journal_purge_la_cle(tmp_path):
    j = pe.Journal(tmp_path / "j.log", CLE)
    j.ecrire(f"incident avec {CLE}")
    assert CLE not in (tmp_path / "j.log").read_text()


# ---------------------------------------------------------------- coût
def test_cout_appel_prix():
    c, d = pe.cout_appel(100_000, 1_000_000)
    assert c == pytest.approx(0.51) and not d
    c, d = pe.cout_appel(100_000, 0)
    assert c == pytest.approx(0.01) and not d  # 100 000 exactement : pas doublé


def test_cout_appel_double_au_dessus_de_100k():
    c, d = pe.cout_appel(100_001, 1000)
    assert d and c == pytest.approx(2 * (100_001 * 0.10 + 1000 * 0.50) / 1e6)


def test_bilan_appels():
    b = pe.bilan_appels([(1000, 100, False), (200_000, 10, False)])
    assert b["appels"] == 2 and b["appels_doubles"] == 1 and b["jetons_entree"] == 201_000 and b["jetons_sortie"] == 110
    assert b["cout_usd"] == pytest.approx((1000 * 0.1 + 100 * 0.5) / 1e6 + 2 * (200_000 * 0.1 + 10 * 0.5) / 1e6)


def test_comptable_arret_a_80_pour_cent():
    c = pe.Comptable(1.00)
    c.ajouter(0.79)
    assert not c.doit_arreter()
    c.ajouter(0.01)
    assert c.doit_arreter() and "80 %" in c.arret


def test_comptable_arreter_garde_la_premiere_raison():
    c = pe.Comptable(1.0)
    c.arreter("a")
    c.arreter("b")
    assert c.arret == "a"


def msg(role, p=None, c=None, i=0):
    m = {"role": role, "content": "x", "turn_idx": i}
    m["usage"] = None if p is None else {"prompt_tokens": p, "completion_tokens": c}
    return m


def ecrire_results(tmp_path, messages, n_sims=1):
    p = tmp_path / "results.json"
    p.write_text(json.dumps({"simulations": [{"messages": messages}] * n_sims}))
    return p


def test_appels_tau2_lit_l_usage_et_ignore_la_salutation(tmp_path):
    p = ecrire_results(tmp_path, [msg("assistant"), msg("user", 10, 5, 1), msg("assistant", 20, 6, 2),
                                  {"role": "tool", "content": "r"}, msg("assistant", 30, 7, 3)])
    assert pe.appels_tau2(p) == [(10, 5, False), (20, 6, False), (30, 7, False)]


@pytest.mark.parametrize("messages", [
    [msg("assistant"), msg("user", 10, 5), msg("assistant")],      # appel sans usage
    [msg("assistant"), msg("user", 10, None)],                      # usage incomplet
    [msg("assistant"), msg("user", 0, 0)],                          # usage nul
    [msg("assistant", 1, 1)][:0],                                   # aucun message
    [msg("assistant"), {"role": "tool", "content": "x"}],           # aucun appel
])
def test_appels_tau2_usage_illisible(tmp_path, messages):
    with pytest.raises(ValueError):
        pe.appels_tau2(ecrire_results(tmp_path, messages))


def test_appels_tau2_fichier_absent_corrompu_ou_deux_simulations(tmp_path):
    with pytest.raises(ValueError):
        pe.appels_tau2(tmp_path / "absent.json")
    (tmp_path / "c.json").write_text("{pas du json")
    with pytest.raises(ValueError):
        pe.appels_tau2(tmp_path / "c.json")
    with pytest.raises(ValueError):
        pe.appels_tau2(ecrire_results(tmp_path, [msg("assistant"), msg("user", 1, 1)], n_sims=2))


def test_appels_tau2_estimation_seulement_a_blanc(tmp_path):
    p = ecrire_results(tmp_path, [msg("assistant"), msg("user"), msg("assistant")])
    with pytest.raises(ValueError):
        pe.appels_tau2(p)
    a = pe.appels_tau2(p, estimer=True)
    assert len(a) == 2 and all(x[2] and x[0] > 0 and x[1] > 0 for x in a)


def test_appels_workbench(tmp_path):
    p = tmp_path / "u.jsonl"
    p.write_text('{"modele":"m","prompt_tokens":100,"completion_tokens":5}\n{"modele":"m","prompt_tokens":7,"completion_tokens":1}\n')
    assert pe.appels_workbench(p) == [(100, 5, False), (7, 1, False)]
    p.write_text('{"modele":"m","prompt_tokens":null,"completion_tokens":5}\n')
    with pytest.raises(ValueError):
        pe.appels_workbench(p)
    p.write_text("")
    with pytest.raises(ValueError):
        pe.appels_workbench(p)
    with pytest.raises(ValueError):
        pe.appels_workbench(tmp_path / "absent.jsonl")


# ---------------------------------------------------------------- capture d'usage WorkBench (usage_wrap)
class Rep:
    def __init__(self, usage):
        self.usage = usage


class Usage:
    def __init__(self, p, c):
        self.prompt_tokens, self.completion_tokens = p, c


def test_enveloppe_transparente_et_ecrit_l_usage(tmp_path):
    vu = {}
    rep = Rep(Usage(12, 3))

    def original(client, **kw):
        vu["args"] = (client, kw)
        return rep

    f = usage_wrap.envelopper(original, tmp_path / "u.jsonl")
    assert f("C", model="claude-haiku-5-5", messages=[1]) is rep
    assert vu["args"] == ("C", {"model": "claude-haiku-5-5", "messages": [1]})
    assert pe.appels_workbench(tmp_path / "u.jsonl") == [(12, 3, False)]
    assert "messages" not in (tmp_path / "u.jsonl").read_text()


def test_enveloppe_usage_absent_donne_null_donc_illisible(tmp_path):
    f = usage_wrap.envelopper(lambda client, **kw: Rep(None), tmp_path / "u.jsonl")
    f(None, model="m")
    with pytest.raises(ValueError):
        pe.appels_workbench(tmp_path / "u.jsonl")


def test_enveloppe_laisse_passer_les_exceptions(tmp_path):
    def original(client, **kw):
        raise TimeoutError("x")

    with pytest.raises(TimeoutError):
        usage_wrap.envelopper(original, tmp_path / "u.jsonl")(None, model="m")
    assert not (tmp_path / "u.jsonl").exists()


def test_enveloppe_ne_casse_pas_si_ecriture_impossible(tmp_path):
    rep = Rep(Usage(1, 1))
    f = usage_wrap.envelopper(lambda client, **kw: rep, tmp_path / "dossier-absent" / "u.jsonl")
    assert f(None, model="m") is rep


# ---------------------------------------------------------------- tâches
def test_taches_trois_premieres_dans_l_ordre_de_la_liste(tmp_path):
    dev = {e: [f"{e}-{i}" for i in (9, 1, 5, 2)] for e in pe.ENVS}
    p = tmp_path / "dev.json"
    p.write_text(json.dumps(dev))
    t, factice = pe.charger_taches(p, reel=True)
    assert not factice and t["aviation"] == ["aviation-9", "aviation-1", "aviation-5"]
    assert all(len(v) == 3 for v in t.values())


def test_taches_workbench_trois_fichiers_differents(tmp_path):
    dev = {e: [f"{e}-{i}" for i in (9, 1, 5, 2)] for e in pe.ENVS}
    dev["WorkBench"] = ["analytics:10", "analytics:103", "calendar:7", "customer_relationship_manager:3",
                        "email:12", "email:2", "calendar:1"]
    p = tmp_path / "dev.json"
    p.write_text(json.dumps(dev))
    t, _ = pe.charger_taches(p, reel=True)
    assert t["WorkBench"] == ["email:12", "calendar:7", "customer_relationship_manager:3"]
    dev["WorkBench"] = ["analytics:10", "analytics:103", "analytics:110"]
    p.write_text(json.dumps(dev))
    t, _ = pe.charger_taches(p, reel=True)
    assert t["WorkBench"] == ["analytics:10", "analytics:103", "analytics:110"]


def test_taches_fichier_absent_factice_a_blanc_refus_en_reel(tmp_path):
    t, factice = pe.charger_taches(tmp_path / "absent.json", reel=False)
    assert factice and set(t) == set(pe.ENVS)
    with pytest.raises(pe.ErreurPilote):
        pe.charger_taches(tmp_path / "absent.json", reel=True)


def test_taches_liste_trop_courte_ou_environnement_manquant(tmp_path):
    p = tmp_path / "dev.json"
    p.write_text(json.dumps({"aviation": ["1", "2"], "commerce": ["1", "2", "3"], "banque": ["a", "b", "c"], "WorkBench": ["x:1"] * 3}))
    with pytest.raises(pe.ErreurPilote):
        pe.charger_taches(p, reel=True)
    p.write_text("[]")
    with pytest.raises(pe.ErreurPilote):
        pe.charger_taches(p, reel=False)


def test_parties_intercalees_par_rang():
    ps = pe.construire_parties(pe.LISTE_FACTICE)
    assert len(ps) == 12
    assert [p["id"] for p in ps[:4]] == ["aviation-1", "commerce-1", "banque-1", "WorkBench-1"]


# ---------------------------------------------------------------- commandes
def test_commande_tau2_reglages():
    av = pe.commande_tau2({"env": "aviation", "tache": "11"}, "n", True)
    assert av[1].endswith("banc/tau2_sans_juge.py") and av[:1][0].endswith("tau2-bench/.venv/bin/python")
    assert "substring" in av and av[av.index("--communicate-scorer") + 1] == "substring"
    assert av[av.index("--agent-llm") + 1] == av[av.index("--user-llm") + 1] == "anthropic/claude-haiku-5-5"
    assert av[av.index("--task-ids") + 1] == "11" and av[av.index("--num-trials") + 1] == "1"
    assert "mock_response" not in " ".join(av)
    assert av[av.index("--max-steps") + 1] == "100"
    # Les modèles 5.5 refusent `temperature` (« deprecated for this model », essai réel du 05/11 à 7 h 23)
    assert "temperature" not in " ".join(av)
    assert av[av.index("--agent-llm-args") + 1] == "{}" and av[av.index("--user-llm-args") + 1] == "{}"
    ba = pe.commande_tau2({"env": "banque", "tache": "task_003"}, "n", True)
    assert ba[ba.index("--retrieval-config") + 1] == "bm25_grep" and "--communicate-scorer" not in ba
    co = pe.commande_tau2({"env": "commerce", "tache": "0"}, "n", True)
    assert "--retrieval-config" not in co and "--communicate-scorer" not in co
    blanc = pe.commande_tau2({"env": "commerce", "tache": "0"}, "n", False)
    assert "mock_response" in " ".join(blanc) and "--max-steps" in blanc


def test_commande_workbench():
    c = pe.commande_workbench(pe.Path("/x/analytics_tasks_and_outcomes.csv"))
    assert c[1].endswith("banc/workbench_pilote.py") and c[c.index("--model_name") + 1] == "claude-haiku-5-5"
    assert c[c.index("--workers") + 1] == "1"


def test_nettoyer_parties_factices(tmp_path):
    for n in ("essai-blanc-a", "essai-blanc-b", "pilote-x"):
        (tmp_path / n).mkdir()
        (tmp_path / n / "results.json").write_text("{}")
    assert pe.nettoyer_parties_factices(tmp_path) == ["essai-blanc-a", "essai-blanc-b"]
    assert [p.name for p in tmp_path.iterdir()] == ["pilote-x"]
    assert pe.nettoyer_parties_factices(tmp_path / "absent") == []


# ---------------------------------------------------------------- plafond et mode à blanc par défaut
def test_mode_par_defaut_est_a_blanc():
    a = pe.analyser([])
    assert a.reel is False and a.plafond_usd is None and a.concurrence == 1


def test_reel_exige_plafond(capsys):
    assert pe.main(["--reel"]) == 2
    assert "plafond" in capsys.readouterr().err


@pytest.mark.parametrize("plafond", ["1.01", "5", "0", "-1", "nan", "inf"])
def test_plafond_refuse(plafond, tmp_path):
    assert pe.main(["--reel", "--plafond-usd", plafond, "--sortie-racine", str(tmp_path)], chemin_cle=fichier_cle(tmp_path)) == 2
    assert pe.main(["--plafond-usd", plafond, "--sortie-racine", str(tmp_path)]) == 2  # même refus à blanc
    assert not list(tmp_path.glob("20*"))


def executeur_factice(prompt=1000, completion=100, ok=True, appels=1, trace=None):
    def f(partie, ctx):
        if trace is not None:
            trace.append((partie["id"], ctx["reel"], dict(ctx["env_enfant"])))
        return {"ok": ok, "appels": [(prompt, completion, False)] * appels if prompt is not None else None,
                "erreur": None if ok else "échec", "copies": []}
    return f


def neutraliser_externe(monkeypatch, tmp_path):
    """Aucun test ne touche à externe/ : dossiers de bancs redirigés vers des dossiers temporaires vides."""
    monkeypatch.setattr(pe, "TAU2", tmp_path / "tau2")
    monkeypatch.setattr(pe, "WB_RUN", tmp_path / "wbrun")
    monkeypatch.setattr(pe, "WORKBENCH", tmp_path / "wb")

    def faux_post(sortie, *a, **k):
        (sortie / "resume.txt").write_text("résumé factice")
        return {}

    monkeypatch.setattr(pe, "post_traitement", faux_post)


def test_blanc_par_defaut_ne_lit_pas_la_cle_et_nettoie_l_environnement(tmp_path, monkeypatch):
    neutraliser_externe(monkeypatch, tmp_path)
    trace = []
    base = {"PATH": "/usr/bin", "OPENAI_API_KEY": "o", "OPENROUTER_API_KEY": "r", "ANTHROPIC_API_KEY": "parent"}
    rc = pe.main(["--developpement", str(tmp_path / "absent.json"), "--sortie-racine", str(tmp_path / "s")],
                 executeur=executeur_factice(trace=trace), base_env=base, chemin_cle=tmp_path / "ne-doit-pas-etre-lu")
    assert rc == 0 and len(trace) == 12
    for _id, reel, env in trace:
        assert reel is False and "ANTHROPIC_API_KEY" not in env and "OPENAI_API_KEY" not in env
        assert env["PILOTE_HORS_LIGNE"] == "2"
    (dossier,) = list((tmp_path / "s").iterdir())
    assert dossier.name.endswith("-blanc")
    assert json.loads((dossier / "cout.json").read_text())["mode"] == "à blanc"


def test_blanc_ne_supprime_rien_dans_les_simulations(tmp_path, monkeypatch):
    neutraliser_externe(monkeypatch, tmp_path)
    sim = tmp_path / "tau2" / "data" / "simulations" / "essai-blanc-vieux"
    sim.mkdir(parents=True)
    pe.main(["--developpement", str(tmp_path / "absent.json"), "--sortie-racine", str(tmp_path / "s")], executeur=executeur_factice(), base_env={})
    assert sim.is_dir()


def test_reel_avec_fausse_cle_environnement_et_nettoyage(tmp_path, monkeypatch):
    neutraliser_externe(monkeypatch, tmp_path)
    monkeypatch.setattr(pe, "verifier_taches_existent", lambda t, *a, **k: None)
    sim = tmp_path / "tau2" / "data" / "simulations"
    (sim / "essai-blanc-vieux").mkdir(parents=True)
    dev = tmp_path / "dev.json"
    dev.write_text(json.dumps({e: ["1", "2", "3", "4"] for e in pe.ENVS}))
    trace = []
    base = {"PATH": "/usr/bin", "OPENAI_API_KEY": "o", "OPENROUTER_API_KEY": "r"}
    rc = pe.main(["--reel", "--plafond-usd", "1.00", "--developpement", str(dev), "--sortie-racine", str(tmp_path / "s")],
                 executeur=executeur_factice(trace=trace), base_env=base, chemin_cle=fichier_cle(tmp_path))
    assert rc == 0 and len(trace) == 12
    for _id, reel, env in trace:
        assert reel and env["ANTHROPIC_API_KEY"] == CLE and "OPENROUTER_API_KEY" not in env and "OPENAI_API_KEY" not in env
    assert not (sim / "essai-blanc-vieux").exists()
    (dossier,) = list((tmp_path / "s").iterdir())
    assert not dossier.name.endswith("-blanc")
    for f in dossier.rglob("*"):
        if f.is_file():
            assert CLE not in f.read_text(errors="ignore"), f


def test_reel_refuse_cle_mal_protegee_sans_rien_lancer(tmp_path, monkeypatch, capsys):
    neutraliser_externe(monkeypatch, tmp_path)
    trace = []
    rc = pe.main(["--reel", "--plafond-usd", "0.5", "--developpement", str(tmp_path / "x.json"), "--sortie-racine", str(tmp_path / "s")],
                 executeur=executeur_factice(trace=trace), base_env={}, chemin_cle=fichier_cle(tmp_path, mode=0o644))
    assert rc == 2 and not trace and CLE not in capsys.readouterr().err


def test_reel_refuse_sans_liste_de_taches(tmp_path, monkeypatch):
    neutraliser_externe(monkeypatch, tmp_path)
    trace = []
    rc = pe.main(["--reel", "--plafond-usd", "0.5", "--developpement", str(tmp_path / "absent.json"), "--sortie-racine", str(tmp_path / "s")],
                 executeur=executeur_factice(trace=trace), base_env={}, chemin_cle=fichier_cle(tmp_path))
    assert rc == 2 and not trace


def lancer(tmp_path, executeur, plafond, concurrence=1, n=12):
    sortie = tmp_path / "sortie"
    sortie.mkdir(exist_ok=True)
    ctx = {"sortie": sortie, "reel": True, "env_enfant": {}, "cle": None, "horodatage": "t"}
    journal = pe.Journal(sortie / "journal.log")
    compta = pe.Comptable(plafond)
    res = pe.lancer_parties(pe.construire_parties(pe.LISTE_FACTICE)[:n], concurrence, compta, ctx, journal, executeur)
    return res, compta, json.loads((sortie / "cout.json").read_text()), (sortie / "journal.log").read_text()


def test_arret_avant_toute_nouvelle_partie_a_80_pour_cent(tmp_path):
    # chaque partie : 1 appel de 200 000 jetons d'entrée, doublé = 0.04 USD. Plafond 0.10 -> seuil 0.08.
    res, compta, cout, journal = lancer(tmp_path, executeur_factice(prompt=200_000, completion=0), plafond=0.10)
    assert len(res) == 2 and compta.cumul == pytest.approx(0.08)
    assert cout["arret"] and cout["cumul_usd"] == pytest.approx(0.08) and len(cout["parties"]) == 2
    assert "ARRÊT" in journal and "compté(s) au double" not in journal and "comptés au double" in journal
    assert cout["parties"][0]["appels_doubles"] == 1


def test_pas_d_arret_sous_le_seuil(tmp_path):
    res, compta, cout, _ = lancer(tmp_path, executeur_factice(prompt=1000, completion=100), plafond=1.0)
    assert len(res) == 12 and cout["arret"] is None


def test_arret_si_usage_illisible(tmp_path):
    res, compta, cout, journal = lancer(tmp_path, executeur_factice(prompt=None, ok=False), plafond=1.0)
    assert len(res) == 1 and "ARRÊT" in journal and cout["parties"][0]["cout_usd"] is None


def test_arret_si_echec_meme_avec_usage_lisible(tmp_path):
    res, compta, cout, _ = lancer(tmp_path, executeur_factice(ok=False), plafond=1.0)
    assert len(res) == 1 and compta.arret and cout["cumul_usd"] > 0


def test_arret_si_exception_de_l_executeur(tmp_path):
    def boum(partie, ctx):
        raise RuntimeError("secret " + CLE)

    res, compta, cout, journal = lancer(tmp_path, boum, plafond=1.0)
    assert len(res) == 1 and compta.arret and CLE not in json.dumps(cout) and CLE not in journal


def test_concurrence_deux_respecte_l_arret(tmp_path):
    res, compta, cout, _ = lancer(tmp_path, executeur_factice(prompt=200_000, completion=0), plafond=0.10, concurrence=2)
    assert 2 <= len(res) <= 3 and compta.doit_arreter()  # au plus une partie déjà en cours lors du franchissement


def test_cout_json_complet(tmp_path):
    _, _, cout, _ = lancer(tmp_path, executeur_factice(), plafond=1.0, n=4)
    assert {"mode", "plafond_usd", "seuil_arret_usd", "cumul_usd", "arret", "parties", "prix_usd_par_million"} <= set(cout)
    assert cout["seuil_arret_usd"] == pytest.approx(0.8) and cout["prix_usd_par_million"] == {"entree": 0.1, "sortie": 0.5}
    assert cout["cumul_usd"] == pytest.approx(4 * (1000 * 0.1 + 100 * 0.5) / 1e6)


# ---------------------------------------------------------------- résumé
def test_resume_par_env():
    lignes = [
        {"banc": "tau2", "domaine": "airline", "kind": "lecture", "verdict": "", "type": "lecture"},
        {"banc": "tau2", "domaine": "airline", "kind": "écriture", "verdict": "juste", "type": "argent"},
        {"banc": "tau2", "domaine": "airline", "kind": "écriture", "verdict": "fausse", "type": "argent"},
        {"banc": "tau2", "domaine": "airline", "kind": "doute", "verdict": "", "type": "doute"},
        {"banc": "workbench", "domaine": "email", "kind": "écriture", "verdict": "juste", "type": "message interne"},
    ]
    parties = [{"id": "aviation-1", "env": "aviation", "ok": True, "jetons_entree": 10, "jetons_sortie": 5, "cout_usd": 0.5},
               {"id": "WorkBench-1", "env": "WorkBench", "ok": False, "jetons_entree": None, "jetons_sortie": None, "cout_usd": None}]
    r = pe.resume_par_env(lignes, parties)
    av = r["aviation"]
    assert (av["parties_lancees"], av["parties_ok"], av["actions"], av["lectures"], av["ecritures"], av["autres_actions"]) == (1, 1, 4, 1, 2, 1)
    assert av["ecritures_par_verdict"] == {"fausse": 1, "juste": 1} and av["ecritures_par_type"] == {"argent": 2}
    assert av["cout_usd"] == 0.5 and r["WorkBench"]["ecritures_par_type"] == {"message interne": 1}
    assert r["banque"]["parties_lancees"] == 0
