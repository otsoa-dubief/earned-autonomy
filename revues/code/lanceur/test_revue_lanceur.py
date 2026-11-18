"""Reproductions des constats de la revue du lanceur (revues/code/2026-11-06_revue_lanceur.md).

Chaque test PASSE tant que le défaut est présent : il affirme le comportement constaté, et sa docstring dit le
comportement attendu. Aucun appel réel : exécuteur factice ou enfant simulé (pe.executer_enfant remplacé), fausse clé
dans un fichier temporaire, bancs redirigés vers des dossiers temporaires (aides de banc/tests/test_lanceur.py).

    cd ROOT
    env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u OPENROUTER_API_KEY \
        simulation/.venv/bin/python -m pytest -q -s -p no:cacheprovider revues/code/lanceur/test_revue_lanceur.py
"""
import json
import threading
import time
from datetime import datetime

import pytest

import lanceur as L
import pilote_etape1 as pe
import test_lanceur as T


# ------------------------------------------------------------------------------------------------ aides
def parties_wb(n, modele="claude-opus-5-5"):
    """n parties WorkBench (tâches email:0 et email:1 de preparer_workbench, passages 1, 1, 2, 2...)."""
    out = []
    for i in range(n):
        tache, passage = f"email:{i % 2}", 1 + i // 2
        out.append({"id": L.id_partie("WorkBench", modele, passage, tache), "env": "WorkBench", "modele": modele,
                    "tache": tache, "passage": passage, "rang": i + 1, "n_config": n})
    return [(x, 1) for x in out]


def partie_tau(env="aviation", modele="claude-opus-5-5", tache="1"):
    return {"id": L.id_partie(env, modele, 1, tache), "env": env, "modele": modele, "tache": tache, "passage": 1,
            "rang": 1, "n_config": 1}


def ecrire_predictions(tmp_path, erreur="", modele="claude-opus-5-5"):
    d = tmp_path / "wbrun" / "data" / "results" / "email"
    d.mkdir(parents=True, exist_ok=True)
    n = f"{modele}_all_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    (d / f"{n}.csv").write_text(f'"task","function_calls","full_response","error"\n"q","[]","x","{erreur}"\n')


# ======================================================================== R1 : WorkBench lancé après l'arrêt
def enfant_wb_qui_note(tmp_path, compta, departs, jetons, pendant=None):
    """Faux WorkBench : note, au moment où l'enfant démarre, si l'arrêt était déjà décidé."""
    def faux(cmd, env, cwd, log, cle=None, delai=0):
        departs.append({"heure": time.time(), "arret_deja_decide": compta.doit_arreter(), "cumul": compta.cumul})
        if pendant:
            pendant(len(departs))
        ecrire_predictions(tmp_path)
        T.ecrire_usage(env["PILOTE_USAGE_FILE"], [("claude-opus-5-5", "claude-opus-5-5", jetons, 0)])
        time.sleep(0.2)
        return 0
    return faux


def test_R1_parties_workbench_lancees_apres_le_seuil_d_arret(tmp_path, monkeypatch):
    """Attendu : aucune partie lancée une fois le seuil atteint (choix 9 ; docstring de lancer_vague).
    Constaté : les parties WorkBench qui attendaient verrou_wb démarrent quand même, après l'arrêt."""
    T.preparer_workbench(tmp_path, monkeypatch)
    ctx, compta, reg, journal = T.contexte(tmp_path, 5.0)  # vague 1 : seuil 4 $ ; une partie = 1 M jetons Opus = 4 $
    departs = []
    monkeypatch.setattr(pe, "executer_enfant", enfant_wb_qui_note(tmp_path, compta, departs, 1_000_000))
    L.lancer_vague(parties_wb(3), 3, compta, ctx, journal, L.executer_partie)
    print("\nR1 départs des enfants WorkBench :", [(d["arret_deja_decide"], round(d["cumul"], 2)) for d in departs])
    print("R1 arrêt :", compta.arret, "; cumul final :", compta.cumul, "USD ; plafond :", compta.plafond, "USD")
    assert [d["arret_deja_decide"] for d in departs] == [False, True, True]
    assert compta.cumul == pytest.approx(12.0) and len(reg.lignes) == 3


def test_R1b_parties_workbench_lancees_apres_une_interruption(tmp_path, monkeypatch):
    """Même mécanisme pour tout arrêt (Ctrl-C, nom de modèle changé, coût non compté, échecs en série) : ici l'arrêt
    est posé comme le fait le gestionnaire de KeyboardInterrupt (compta.arreter), pendant la première partie."""
    T.preparer_workbench(tmp_path, monkeypatch)
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    departs = []

    def pendant(k):
        if k == 1:
            compta.arreter("interruption par l'opérateur")

    monkeypatch.setattr(pe, "executer_enfant", enfant_wb_qui_note(tmp_path, compta, departs, 1000, pendant))
    L.lancer_vague(parties_wb(3), 3, compta, ctx, journal, L.executer_partie)
    print("\nR1b départs :", [d["arret_deja_decide"] for d in departs], "; statuts :", [l["statut"] for l in reg.lignes])
    assert [d["arret_deja_decide"] for d in departs] == [False, True, True]
    assert [l["statut"] for l in reg.lignes] == [L.TERMINEE] * 3


# ======================================================================== R2 : relancer une vague = nouveau plafond
def test_R2_relancer_la_vague_au_lieu_de_la_reprendre_ouvre_un_second_plafond(tmp_path, monkeypatch):
    """Attendu : le plafond (et l'accord d'Otsoa) bornent la dépense de la vague. Constaté : la même commande relancée
    (sans --reprendre) crée un second dossier, avec une nouvelle graine et un plafond neuf : 2 x 2,40 $ pour 3 $."""
    T.neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L, "RESERVE", T.ecrire_reserve(tmp_path))
    cle = T.fichier_cle(tmp_path)
    ex = T.executeur_factice(p=200_000, s=0, modele="claude-sonnet-5-5")  # 0,40 $ par partie
    rcs = []
    for _ in range(2):
        rcs.append(L.main(T.argv(tmp_path, "--reel", "--concurrence", "1", reserve=L.RESERVE, graine=None),
                          executeur=ex, base_env={}, chemin_cle=cle, extracteur=T.extracteur_ok))
        time.sleep(1.1)  # le dossier de sortie est nommé à la seconde
    dossiers = sorted((tmp_path / "s" / "vague1").iterdir())
    couts = [json.loads((d / "cout.json").read_text()) for d in dossiers]
    plans = [json.loads((d / "plan_de_jeu.json").read_text()) for d in dossiers]
    total = sum(c["cumul_usd"] for c in couts)
    print("\nR2 codes :", rcs, "; dossiers :", [d.name for d in dossiers], "; graines :", [p["graine"] for p in plans])
    print("R2 dépense par dossier :", [c["cumul_usd"] for c in couts], "; total :", round(total, 2),
          "USD pour plafond = accord = 3 USD")
    assert rcs == [4, 4] and len(dossiers) == 2 and total == pytest.approx(4.8) and total > 3.0


def test_R2b_seconde_reprise_pendant_la_premiere_rejoue_les_memes_parties(tmp_path, monkeypatch):
    """Aucun verrou sur le dossier de vague : un second --reprendre lancé pendant que le premier tourne (deux
    terminaux, session SSH coupée mais processus encore vivant) prend la tentative en cours pour une interruption,
    puis joue la même file que le premier, sous son propre plafond. Simulé sans fils d'exécution : la seconde reprise
    est lancée depuis la première tentative de la première, ce qui revient à deux processus entrelacés."""
    T.neutraliser(monkeypatch, tmp_path)
    assert L.main(T.argv(tmp_path, "--limite", "2"), executeur=T.executeur_factice(), base_env={},
                  extracteur=T.extracteur_ok) == 0
    d = T.dossier_unique(tmp_path)
    args = T.argv(tmp_path, "--reprendre", str(d), "--limite", "10", "--concurrence", "1")
    joue_par = {"premiere": [], "seconde": []}
    rcs = []

    def seconde(t, ctx):
        joue_par["seconde"].append(t["id"])
        return T.executeur_factice()(t, ctx)

    def premiere(t, ctx):
        joue_par["premiere"].append(t["id"])
        if len(joue_par["premiere"]) == 1:
            rcs.append(("seconde", L.main(list(args), executeur=seconde, base_env={}, extracteur=T.extracteur_ok)))
        return T.executeur_factice()(t, ctx)

    rcs.append(("premiere", L.main(list(args), executeur=premiere, base_env={}, extracteur=T.extracteur_ok)))
    doubles = sorted(set(joue_par["premiere"]) & set(joue_par["seconde"]))
    fins, _ = L.lire_tentatives(d / "tentatives.jsonl")
    gardees = {}
    for l in fins:
        gardees[l["partie"]] = gardees.get(l["partie"], 0) + int(bool(l["ok"]))
    cout = json.loads((d / "cout.json").read_text())
    print("\nR2b codes :", rcs, "; jouées par la 1re :", len(joue_par["premiere"]), "; par la 2de :",
          len(joue_par["seconde"]), "; jouées deux fois :", len(doubles))
    print("R2b tentatives.jsonl : parties gardées deux fois :", sum(1 for v in gardees.values() if v > 1),
          "; cout.json final :", len(cout["parties"]), "lignes pour", len(fins), "fins dans tentatives.jsonl")
    assert len(doubles) == 10 and sum(1 for v in gardees.values() if v > 1) == 10
    assert len(cout["parties"]) < len(fins)  # le cout.json de la 1re ignore les lignes (et le coût) de la 2de


# ======================================================================== R3 : reprise de la vague 1 après la vague 2
def test_R3_reprendre_la_vague_1_apres_la_vague_2_rejoue_les_memes_parties(tmp_path, monkeypatch):
    """Attendu : une partie jouée une fois. Constaté : une partie de la vague 1 restée sans fin (ici interrompue) est
    jouée par la vague 2, puis encore par une reprise de la vague 1, que rien n'interdit : deux tentatives gardées
    (deux dossiers parties/), payées deux fois."""
    T.neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L, "RESERVE", T.ecrire_reserve(tmp_path))
    cle = T.fichier_cle(tmp_path)
    derniere = L.parties_vague1(L.construire_parties(T.RESERVE_TEST, 5))[-1]["id"]
    base = T.executeur_factice(p=20_000, s=0, modele="claude-sonnet-5-5", fichiers=True)

    def ex1(t, ctx):
        r = base(t, ctx)
        if t["id"] == derniere:  # coupée (code -2) : statut « interrompue », rejouée plus tard
            r.update(ok=False, code=-2, erreur="tau2 : code de retour -2")
        return r

    rc1 = L.main(T.argv(tmp_path, "--reel", "--concurrence", "1", reserve=L.RESERVE), executeur=ex1, base_env={},
                 chemin_cle=cle, extracteur=T.extracteur_ok)
    v1 = T.dossier_unique(tmp_path)
    p = T.plafond_permis_v2(tmp_path, v1, "1000", reel=True)
    rc2 = T.main_v2_reelle(tmp_path, v1, "1000", p, T.executeur_factice(p=5_000, s=0, modele="claude-sonnet-5-5",
                                                                        fichiers=True))
    v2 = T.dossier_unique(tmp_path, 2)
    trace3 = []
    rc3 = L.main(T.argv(tmp_path, "--reel", "--reprendre", str(v1), "--concurrence", "1", reserve=L.RESERVE),
                 executeur=T.executeur_factice(trace3, p=20_000, s=0, modele="claude-sonnet-5-5", fichiers=True),
                 base_env={}, chemin_cle=cle, extracteur=T.extracteur_ok)
    banc = "workbench" if derniere.startswith("WorkBench") else "tau2"
    g1 = [l for l in T.lignes_cout(v1) if l["partie"] == derniere and l["ok"]]
    g2 = [l for l in T.lignes_cout(v2) if l["partie"] == derniere and l["ok"]]
    print("\nR3 codes :", rc1, rc2, rc3, "; reprise de la vague 1 a joué :", [x[0] for x in trace3])
    print("R3 tentatives gardées de", derniere, ": vague 1", [(l["id"], l["vague"], l["cout_usd"]) for l in g1],
          "; vague 2", [(l["id"], l["vague"], l["cout_usd"]) for l in g2])
    assert rc3 == 0 and [x[0] for x in trace3] == [derniere] and len(g1) == 1 and len(g2) == 1
    assert (v1 / "parties" / f"{banc}-{derniere}").is_dir() and (v2 / "parties" / f"{banc}-{derniere}").is_dir()


# ======================================================================== R4 : WorkBench, usage absent après des appels
@pytest.mark.parametrize("erreur_wb", [L.WB_MESSAGE_ARRET, L.WB_MESSAGE_CONTEXTE, "Error code: 529 overloaded"])
def test_R4_workbench_usage_absent_apres_des_appels_cout_nul_sans_arret(tmp_path, monkeypatch, erreur_wb):
    """Attendu (choix 16 b) : en réel, JSONL absent alors que des appels ont eu lieu = coût non compté, arrêt. Constaté :
    une partie WorkBench arrêtée par sa limite de 20 itérations (ou par la fenêtre de contexte), donc après des appels,
    sans aucune ligne d'usage, est gardée avec un coût nul, et le lanceur continue. Même chose pour une erreur d'API
    survenue après des appels réussis."""
    T.preparer_workbench(tmp_path, monkeypatch)

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        ecrire_predictions(tmp_path, erreur=erreur_wb)
        return 0  # capture d'usage en panne : aucune ligne écrite

    monkeypatch.setattr(pe, "executer_enfant", faux)
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)  # réel
    L.lancer_vague(parties_wb(1), 1, compta, ctx, journal, L.executer_partie)
    x = reg.lignes[0]
    print(f"\nR4 [{erreur_wb[:30]}] statut={x['statut']} ok={x['ok']} usage={x['usage']} cout_usd={x['cout_usd']} "
          f"cumul={compta.cumul} arret={compta.arret}")
    assert x["usage"] == "absent" and x["cout_usd"] is None and compta.cumul == 0
    assert compta.arret is None or "de suite" in compta.arret  # jamais « coût non compté »
    if erreur_wb in (L.WB_MESSAGE_ARRET, L.WB_MESSAGE_CONTEXTE):
        assert x["statut"] == L.ARRETEE and x["ok"] and compta.arret is None


def test_R4_temoin_sans_erreur_le_garde_fou_joue(tmp_path, monkeypatch):
    """Témoin : sans texte d'erreur, le même usage absent arrête bien le lanceur (coût non compté)."""
    T.preparer_workbench(tmp_path, monkeypatch)
    monkeypatch.setattr(pe, "executer_enfant", lambda *a, **k: (ecrire_predictions(tmp_path), 0)[1])
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague(parties_wb(2), 1, compta, ctx, journal, L.executer_partie)
    assert len(reg.lignes) == 1 and "non compté" in compta.arret


# ======================================================================== R5 : τ-bench, plantage sans simulation ni usage
def test_R5_tau2_plante_sans_simulation_ni_usage_cout_nul_sans_arret(tmp_path, monkeypatch):
    """En réel, τ-bench sorti en erreur avec un results.json sans simulation et sans JSONL d'usage : coût 0, sans arrêt
    (le croisement avec results.json est impossible). Si la capture était en panne, rien ne le signale."""
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        nom = cmd[cmd.index("--save-to") + 1]
        T.resultats_tau2(tmp_path / "tau2" / "data" / "simulations" / nom / "results.json", sims=0)
        return 1

    monkeypatch.setattr(pe, "executer_enfant", faux)
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague([(partie_tau(), 1)], 1, compta, ctx, journal, L.executer_partie)
    print("\nR5 lignes :", [(l["id"], l["statut"], l["usage"], l["cout_usd"]) for l in reg.lignes], "; arret :", compta.arret)
    assert [l["usage"] for l in reg.lignes] == ["absent", "absent"] and compta.cumul == 0 and compta.arret is None


# ======================================================================== R6 : coût inconnu oublié à la reprise
def test_R6_cout_inconnu_puis_reprise_le_cout_n_est_jamais_compte(tmp_path, monkeypatch):
    """Le lanceur s'arrête sur un coût non compté (bien), mais la reprise repart comme si cette tentative avait coûté
    0 : rien n'est majoré, rien n'oblige à l'examiner."""
    T.neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L, "RESERVE", T.ecrire_reserve(tmp_path))
    cle = T.fichier_cle(tmp_path)
    base, premier = T.executeur_factice(p=20_000, s=0, modele="claude-sonnet-5-5"), []

    def ex(t, ctx):
        r = base(t, ctx)
        if not premier:
            premier.append(t["id"])
            r.update(appels=None, renvoyes=[], cout_inconnu=True, ok=False, erreur="usage absent", usage="absent")
        return r

    rc1 = L.main(T.argv(tmp_path, "--reel", "--concurrence", "1", reserve=L.RESERVE), executeur=ex, base_env={},
                 chemin_cle=cle, extracteur=T.extracteur_ok)
    d = T.dossier_unique(tmp_path)
    c1 = json.loads((d / "cout.json").read_text())
    rc2 = L.main(T.argv(tmp_path, "--reel", "--reprendre", str(d), "--concurrence", "1", reserve=L.RESERVE),
                 executeur=ex, base_env={}, chemin_cle=cle, extracteur=T.extracteur_ok)
    c2 = json.loads((d / "cout.json").read_text())
    x = [l for l in c2["parties"] if l["id"] == premier[0]][0]
    print("\nR6 1er lancement :", rc1, c1["arret"], c1["cumul_usd"], "; reprise :", rc2, "cumul", c2["cumul_usd"],
          "; ligne :", x["usage"], x["cout_usd"])
    assert rc1 == 4 and "non compté" in c1["arret"] and rc2 == 0 and x["cout_usd"] is None
    assert c2["cumul_usd"] == pytest.approx(sum(l["cout_usd"] or 0 for l in c2["parties"]))


# ======================================================================== R7 : référence de nom commune aux deux bancs
def test_R7_reference_du_nom_partagee_entre_tau2_et_workbench(tmp_path):
    """La référence est indexée par le seul modèle demandé : τ-bench (API Anthropic via LiteLLM) et WorkBench (API
    compatible OpenAI) partagent la même. Si les deux points d'accès ne renvoient pas la même chaîne pour le même
    modèle (non prouvé : rien n'a été mesuré), la première partie WorkBench est exclue et le lanceur s'arrête, puis
    chaque reprise exclut définitivement une partie."""
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    tau, wb = partie_tau(modele="claude-haiku-5-5"), parties_wb(1, "claude-haiku-5-5")[0][0]

    def renvoye(t):
        return "claude-haiku-5-5" if t["env"] == "WorkBench" else "claude-haiku-5-5-20261001"

    L.lancer_vague([(tau, 1), (wb, 1)], 1, compta, ctx, journal, T.executeur_factice(renvoye=renvoye))
    print("\nR7 statuts :", [(l["env"], l["statut"]) for l in reg.lignes], "; arret :", compta.arret)
    assert [l["statut"] for l in reg.lignes] == [L.TERMINEE, L.EXCLUE_NOM] and "nom de modèle" in compta.arret


# ======================================================================== R8 : filet de 35 minutes, simulation finie
@pytest.mark.parametrize("terminaison", ["infrastructure_error", "user_stop"])
def test_R8_filet_de_35_minutes_sur_une_simulation_finie(tmp_path, monkeypatch, terminaison):
    """Processus τ-bench tué par le filet (code -1) alors que results.json contient une simulation finie : la partie
    est classée « arrêtée (30 minutes) » et gardée, quelle que soit sa terminaison (un infrastructure_error devrait être
    un échec technique ; un user_stop, une partie terminée)."""
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        nom = cmd[cmd.index("--save-to") + 1]
        T.resultats_tau2(tmp_path / "tau2" / "data" / "simulations" / nom / "results.json", terminaison)
        T.ecrire_usage(env["PILOTE_USAGE_FILE"], [("claude-haiku-5-5", "claude-haiku-5-5", 100, 5),
                                                  ("claude-opus-5-5", "claude-opus-5-5", 200, 6)])
        return -1

    monkeypatch.setattr(pe, "executer_enfant", faux)
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague([(partie_tau(), 1)], 1, compta, ctx, journal, L.executer_partie)
    (x,) = reg.lignes
    print(f"\nR8 [{terminaison}] statut={x['statut']} arret={x['arret']} ok={x['ok']} terminaison={x['terminaison']} "
          f"dossier={x['dossier']}")
    assert (x["statut"], x["arret"], x["ok"], x["terminaison"]) == (L.ARRETEE, L.ARRET_30_MIN, True, terminaison)
    assert x["dossier"].startswith("parties/")


# ======================================================================== R9 : relances internes de τ-bench
def test_R9_relances_internes_de_tau2_et_depassement_de_contexte(tmp_path, monkeypatch):
    """τ-bench relance lui-même une simulation en exception (3 fois par défaut ; la commande ne passe pas
    --max-retries) ; un dépassement de contexte n'y devient jamais « context_window_exceeded » mais une simulation vide
    « infrastructure_error » après 4 essais. Le lanceur la classe en échec technique, la relance (4 essais de plus),
    puis l'exclut : jamais « arrêtée (fenêtre de contexte) »."""
    cmd = L.commande_tau2({"id": "x", "env": "banque", "modele": "claude-opus-5-5", "tache": "task_001"}, "n", True)
    config = (L.TAU2 / "src" / "tau2" / "config.py").read_text()
    orchestrateur = (L.TAU2 / "src" / "tau2" / "orchestrator" / "orchestrator.py").read_text()
    assert "--max-retries" not in cmd and "DEFAULT_RETRY_ATTEMPTS = 3" in config
    assert "CONTEXT_WINDOW_EXCEEDED" not in orchestrateur
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        nom = cmd[cmd.index("--save-to") + 1]
        f = tmp_path / "tau2" / "data" / "simulations" / nom / "results.json"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({"simulations": [{"id": "s", "task_id": "task_001", "messages": [],
                                                  "termination_reason": "infrastructure_error",
                                                  "info": {"error_type": "ContextWindowExceededError",
                                                           "failed_after_attempts": 4}}]}))
        T.ecrire_usage(env["PILOTE_USAGE_FILE"], [("claude-opus-5-5", "claude-opus-5-5", 150_000, 500)] * 40)
        return 0

    monkeypatch.setattr(pe, "executer_enfant", faux)
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague([(partie_tau("banque", "claude-opus-5-5", "task_001"), 1)], 1, compta, ctx, journal,
                   L.executer_partie)
    print("\nR9 lignes :", [(l["id"], l["statut"], l["arret"], l["motif_exclusion"], l["cout_usd"]) for l in reg.lignes])
    assert [l["statut"] for l in reg.lignes] == [L.ECHEC, L.ECHEC] and reg.lignes[1]["exclue"]
    assert not any(l["arret"] == L.ARRET_CONTEXTE for l in reg.lignes)
    assert compta.cumul == pytest.approx(2 * 40 * (150_000 * 4.0 + 500 * 20.0) / 1e6)


# ======================================================================== R13 : usage d'une tentative orpheline illisible
def test_R13_orpheline_a_usage_illisible_exception_hors_du_refus(tmp_path, monkeypatch):
    """recuperer_interrompues lève ErreurPilote (« à examiner avant de reprendre ») hors du try de main : traceback et
    code 1 au lieu de « REFUS : » et du code 2, après avoir déjà mis à l'écart les orphelines précédentes et écrit
    outils_agent.json et le journal."""
    T.neutraliser(monkeypatch, tmp_path)
    assert L.main(T.argv(tmp_path, "--limite", "2"), executeur=T.executeur_factice(), base_env={},
                  extracteur=T.extracteur_ok) == 0
    d = T.dossier_unique(tmp_path)
    suivantes = L.parties_vague1(L.construire_parties(T.RESERVE_TEST, 5))[2:4]
    (d / "usage").mkdir(exist_ok=True)
    for k, x in enumerate(suivantes):  # arrêt brutal pendant deux parties
        t = L.tentative(x, 1, 1)
        with open(d / "tentatives.jsonl", "a") as fh:
            fh.write(json.dumps({"evenement": "début", "id": t["id"],
                                 "tentative": {c: t[c] for c in L.CHAMPS_TENTATIVE}}) + "\n")
        if k == 0:
            T.ecrire_usage(d / "usage" / f"{t['id']}.jsonl", [("claude-sonnet-5-5", "claude-sonnet-5-5", 1000, 10)])
        else:
            (d / "usage" / f"{t['id']}.jsonl").write_text('{"modele": "claude-sonnet-5-5", "prompt_tok')  # coupée
    with pytest.raises(pe.ErreurPilote) as e:
        L.main(T.argv(tmp_path, "--reprendre", str(d)), executeur=T.executeur_factice(), base_env={},
               extracteur=T.extracteur_ok)
    fins, orphelines = L.lire_tentatives(d / "tentatives.jsonl")
    print("\nR13 exception non rattrapée :", type(e.value).__name__, str(e.value)[:90])
    print("R13 après coup : orphelines restantes", [o["id"] for o in orphelines], "; interruptions écrites",
          [l["id"] for l in fins if l["statut"] == L.INTERROMPUE])
    assert [o["id"] for o in orphelines] == [suivantes[1]["id"]]


def test_R2c_deux_lancements_dans_la_meme_seconde_plantent_sans_refus(tmp_path, monkeypatch):
    """Le dossier est nommé à la seconde (mkdir exist_ok=False, hors du try de main) : un second lancement dans la même
    seconde lève FileExistsError (traceback) au lieu d'un refus ; une seconde plus tard, il passe (R2)."""
    T.neutraliser(monkeypatch, tmp_path)
    args = T.argv(tmp_path, "--limite", "1")
    while time.time() % 1 > 0.5:  # se placer en début de seconde
        time.sleep(0.01)
    assert L.main(list(args), executeur=T.executeur_factice(), base_env={}, extracteur=T.extracteur_ok) == 0
    with pytest.raises(FileExistsError):
        L.main(list(args), executeur=T.executeur_factice(), base_env={}, extracteur=T.extracteur_ok)
