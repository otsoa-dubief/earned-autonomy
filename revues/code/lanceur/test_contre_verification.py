"""Contre-vérification des corrections du lanceur (commit 13bdc94), revue du 06/11.

Chaque test PASSE tant que le défaut décrit est présent. Aucun appel réel : exécuteur factice ou enfant simulé, fausse
clé dans un fichier temporaire, bancs redirigés vers des dossiers temporaires (aides de banc/tests/test_lanceur.py).

    cd ROOT
    env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u OPENROUTER_API_KEY \
        simulation/.venv/bin/python -m pytest -q -s -p no:cacheprovider revues/code/lanceur/test_contre_verification.py
"""
import json
import re
import time
from datetime import datetime
from pathlib import Path

import pytest

import lanceur as L
import pilote_etape1 as pe
import test_lanceur as T


def reels(racine):
    v = racine / "vague1"
    return sorted(d for d in v.iterdir() if d.is_dir() and not d.name.endswith("-blanc")) if v.is_dir() else []


def partie_tau(env="aviation", modele="claude-opus-5-5", tache="1"):
    return {"id": L.id_partie(env, modele, 1, tache), "env": env, "modele": modele, "tache": tache, "passage": 1,
            "rang": 1, "n_config": 1}


# ======================================================================== CV1 : --sortie-racine contourne le refus
def test_CV1_sortie_racine_contourne_le_refus_d_un_second_dossier_reel(tmp_path, monkeypatch, capsys):
    """Choix 24 : « un lancement est refusé si la vague a déjà un dossier réel sous la racine des sorties ». La racine
    est une option (--sortie-racine), libre en réel : la même commande avec une autre racine ouvre un second dossier
    réel, une autre graine et un second plafond."""
    T.neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L, "RESERVE", T.ecrire_reserve(tmp_path))
    cle = T.fichier_cle(tmp_path)
    cher = T.executeur_factice(p=200_000, s=0, modele="claude-sonnet-5-5")  # 0,40 $ par partie, arrêt à 2,40 $
    a1 = T.argv(tmp_path, "--reel", "--concurrence", "1", reserve=L.RESERVE, graine=None)
    a2 = list(a1)
    a2[a2.index("--sortie-racine") + 1] = str(tmp_path / "ailleurs")
    rc1 = L.main(list(a1), executeur=cher, base_env={}, chemin_cle=cle, extracteur=T.extracteur_ok)
    rc_meme = L.main(list(a1), executeur=cher, base_env={}, chemin_cle=cle, extracteur=T.extracteur_ok)
    rc2 = L.main(list(a2), executeur=cher, base_env={}, chemin_cle=cle, extracteur=T.extracteur_ok)
    dossiers = reels(tmp_path / "s") + reels(tmp_path / "ailleurs")
    total = sum(json.loads((d / "cout.json").read_text())["cumul_usd"] for d in dossiers)
    print(f"\nCV1 codes : même racine {rc1} puis {rc_meme} ; autre racine {rc2} ; dossiers réels : "
          f"{[str(d.relative_to(tmp_path)) for d in dossiers]} ; dépense totale {total:.2f} USD pour plafond = accord = 3")
    assert (rc1, rc_meme, rc2) == (4, 2, 4) and len(dossiers) == 2 and total == pytest.approx(4.8)


# ======================================================================== CV2 : deux lancements réels simultanés
def test_CV2_deux_lancements_reels_qui_se_chevauchent_ouvrent_deux_dossiers(tmp_path, monkeypatch):
    """Le refus se décide dans preparer, le dossier se crée dans mettre_en_place, après la clé et l'extraction des
    outils (quelques secondes en réel) : un second lancement parti dans cet intervalle passe le même contrôle."""
    T.neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L, "RESERVE", T.ecrire_reserve(tmp_path))
    cle = T.fichier_cle(tmp_path)
    args = T.argv(tmp_path, "--reel", "--concurrence", "1", reserve=L.RESERVE, graine=None)
    cher = T.executeur_factice(p=200_000, s=0, modele="claude-sonnet-5-5")
    codes = []

    def extraction_du_premier(dossier, env):
        T.extracteur_ok(dossier, env)
        if not codes:  # pendant l'extraction du premier lancement, la même commande est relancée
            codes.append(L.main(list(args), executeur=cher, base_env={}, chemin_cle=cle, extracteur=T.extracteur_ok))
            time.sleep(1.1)  # dossiers nommés à la seconde

    rc1 = L.main(list(args), executeur=cher, base_env={}, chemin_cle=cle, extracteur=extraction_du_premier)
    dossiers = reels(tmp_path / "s")
    total = sum(json.loads((d / "cout.json").read_text())["cumul_usd"] for d in dossiers)
    print(f"\nCV2 codes : second {codes}, premier {rc1} ; dossiers réels de la vague 1 : {[d.name for d in dossiers]} ; "
          f"dépense {total:.2f} USD pour plafond = accord = 3")
    assert codes == [4] and rc1 == 4 and len(dossiers) == 2 and total == pytest.approx(4.8)


# ======================================================================== CV3 : vague 2 pendant une reprise de la vague 1
def test_CV3_vague_2_lancee_pendant_la_mise_en_route_d_une_reprise_de_la_vague_1(tmp_path, monkeypatch):
    """Le marqueur vague2.json est lu par la reprise de la vague 1 dans preparer, et écrit par la vague 2 sans prendre
    le verrou de la vague 1 ; la vague 2 n'exige que `fin` dans le cout.json de la vague 1, qui reste celui du lancement
    précédent tant que la reprise n'a pas fini sa mise en route. Une vague 2 lancée dans cet intervalle et la reprise
    jouent toutes deux les parties restantes de la vague 1."""
    T.neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L, "RESERVE", T.ecrire_reserve(tmp_path))
    cle = T.fichier_cle(tmp_path)
    derniere = L.parties_vague1(L.construire_parties(T.RESERVE_TEST, 5))[-1]["id"]
    base = T.executeur_factice(p=20_000, s=0, modele="claude-sonnet-5-5", fichiers=True)

    def ex1(t, ctx):
        r = base(t, ctx)
        if t["id"] == derniere:
            r.update(ok=False, code=-2, erreur="tau2 : code de retour -2")  # interrompue : reste à jouer
        return r

    assert L.main(T.argv(tmp_path, "--reel", "--concurrence", "1", reserve=L.RESERVE), executeur=ex1, base_env={},
                  chemin_cle=cle, extracteur=T.extracteur_ok) == 4
    v1 = T.dossier_unique(tmp_path)
    p = T.plafond_permis_v2(tmp_path, v1, "1000", reel=True)
    codes_v2, joue_v1 = [], []

    def extraction_de_la_reprise(dossier, env):
        T.extracteur_ok(dossier, env)
        if not codes_v2:
            codes_v2.append(T.main_v2_reelle(tmp_path, v1, "1000", p, T.executeur_factice(
                p=5_000, s=0, modele="claude-sonnet-5-5", fichiers=True)))

    def ex_reprise(t, ctx):
        joue_v1.append(t["id"])
        return base(t, ctx)

    rc_reprise = L.main(T.argv(tmp_path, "--reel", "--reprendre", str(v1), "--concurrence", "1", reserve=L.RESERVE),
                        executeur=ex_reprise, base_env={}, chemin_cle=cle, extracteur=extraction_de_la_reprise)
    v2 = T.dossier_unique(tmp_path, 2)
    banc = "workbench" if derniere.startswith("WorkBench") else "tau2"
    g1 = [l["id"] for l in T.lignes_cout(v1) if l["partie"] == derniere and l["ok"]]
    g2 = [l["id"] for l in T.lignes_cout(v2) if l["partie"] == derniere and l["ok"]]
    print(f"\nCV3 codes : vague 2 {codes_v2}, reprise de la vague 1 {rc_reprise} ; marqueur posé : "
          f"{(v1 / L.NOM_MARQUEUR_VAGUE2).is_file()} ; la reprise a joué {joue_v1} ; gardée en vague 1 {g1}, en vague 2 {g2}")
    assert codes_v2 == [0] and rc_reprise == 0 and joue_v1 == [derniere] and len(g1) == len(g2) == 1
    assert (v1 / "parties" / f"{banc}-{derniere}").is_dir() and (v2 / "parties" / f"{banc}-{derniere}").is_dir()


# ======================================================================== CV4 : le journal désigne quand même la partie
def test_CV4_journal_partie_et_modele_de_l_exception_d_outil_retrouves_par_elimination(tmp_path, monkeypatch):
    """Choix 28 : la ligne de fin d'une exception d'outil ne nomme ni la partie ni le modèle. Mais la ligne « début »
    de chaque tentative les nomme, toutes les autres fins aussi, et les parties WorkBench passent une à une : la
    tentative restée sans fin nommée est celle de l'exception. Deux parties à la fois, τ-bench intercalé."""
    T.preparer_workbench(tmp_path, monkeypatch)
    erreur = {"WorkBench-sonnet-p01-email_1": "Unknown datetime string format, unable to parse: next week"}

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        pid = Path(env["PILOTE_USAGE_FILE"]).stem  # la partie que lance cet enfant
        d = tmp_path / "wbrun" / "data" / "results" / "email"
        d.mkdir(parents=True, exist_ok=True)
        n = f"claude-x_all_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        (d / f"{n}.csv").write_text(f'"task","function_calls","full_response","error"\n"q","[]","x","{erreur.get(pid, "")}"\n')
        T.ecrire_usage(env["PILOTE_USAGE_FILE"], [("claude-sonnet-5-5", "claude-sonnet-5-5", 1000, 10)])
        time.sleep(0.05)
        return 0

    def executeur(t, ctx):
        return L.executer_partie(t, ctx) if t["env"] == "WorkBench" else T.executeur_factice()(t, ctx)

    monkeypatch.setattr(pe, "executer_enfant", faux)
    wb = [{"id": L.id_partie("WorkBench", m, 1, tache), "env": "WorkBench", "modele": m, "tache": tache, "passage": 1,
           "rang": 1, "n_config": 1} for m, tache in (("claude-opus-5-5", "email:0"), ("claude-sonnet-5-5", "email:1"),
                                                     ("claude-haiku-5-5", "email:0"))]
    file = [(partie_tau(), 1), (wb[0], 1), (partie_tau(tache="2"), 1), (wb[1], 1), (partie_tau(tache="3"), 1),
            (wb[2], 1)]
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague(file, 2, compta, ctx, journal, executeur)
    lignes = (ctx["sortie"] / "journal.log").read_text().splitlines()
    debuts = {m.group(1): m.group(2) for m in (re.search(r" début (\S+) \(([^,]+),", l) for l in lignes) if m}
    fins_nommees = {m.group(1) for m in (re.search(r" fin (\S+) statut=", l) for l in lignes) if m}
    anonymes = [l for l in lignes if "fin d'une tentative" in l]
    retrouvees = {pid: debuts[pid] for pid in debuts if pid not in fins_nommees}
    vraies = {l["partie"] for l in reg.lignes if l["arret"] == L.ARRET_EXCEPTION_OUTIL}
    print(f"\nCV4 fins anonymes au journal : {len(anonymes)} ; tentatives sans fin nommée, avec leur modèle : {retrouvees} ; "
          f"exceptions d'outil réelles : {sorted(vraies)}")
    assert len(anonymes) == 1 and set(retrouvees) == vraies == {"WorkBench-sonnet-p01-email_1"}
    assert retrouvees["WorkBench-sonnet-p01-email_1"] == "claude-sonnet-5-5"


# ======================================================================== CV5 : panne d'API au premier appel τ-bench
def test_CV5_panne_d_api_au_premier_appel_tau2_arret_et_cout_retenu_exige(tmp_path, monkeypatch):
    """Avec --max-retries 0 (choix 29) et results.json « preuve de départ » (choix 33) : si le premier appel d'une
    partie τ-bench échoue (529 après les relances de LiteLLM), il n'y a ni simulation ni JSONL (l'échec n'est pas
    facturé) : coût « inconnu », arrêt du lanceur, et la reprise exige --cout-retenu, à chaque panne de ce genre."""
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        nom = cmd[cmd.index("--save-to") + 1]
        f = tmp_path / "tau2" / "data" / "simulations" / nom / "results.json"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({"simulations": [{"id": "s", "task_id": "1", "messages": [],
                                                  "termination_reason": "infrastructure_error",
                                                  "info": {"error_type": "InternalServerError",
                                                           "error": "AnthropicException - Overloaded",
                                                           "failed_after_attempts": 1}}]}))
        return 0  # aucune ligne d'usage : le seul appel a échoué

    monkeypatch.setattr(pe, "executer_enfant", faux)
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague([(partie_tau(), 1), (partie_tau(tache="2"), 1)], 1, compta, ctx, journal, L.executer_partie)
    (x,) = reg.lignes
    print(f"\nCV5 statut={x['statut']} cout_inconnu={x['cout_inconnu']} terminaison={x['terminaison']!r} ; "
          f"arret : {compta.arret}")
    assert x["cout_inconnu"] and x["statut"] == L.ECHEC and "--cout-retenu" in compta.arret
    assert L.couts_inconnus_en_suspens(reg.lignes) == [x["id"]]


# ======================================================================== CV6 : erreur interne, vague 1 « finie » orpheline
RESERVE_CV6 = {"aviation": [str(i) for i in range(10)], "commerce": [str(i) for i in range(10, 20)],
               "banque": [f"task_{i:03d}" for i in range(1, 11)], "WorkBench": [f"email:{i}" for i in range(100)]}


def test_CV6_erreur_interne_laisse_une_orpheline_que_la_vague_2_ne_voit_pas(tmp_path, monkeypatch):
    """Après une erreur interne (choix 16 e), la tentative reste commencée sans fin dans tentatives.jsonl, mais le
    lanceur finit normalement et écrit `fin` dans cout.json. La vague 2 n'exige que `fin` et l'absence de coût
    inconnu dans les lignes : elle part, et le coût de l'orpheline (son JSONL existe) n'est compté nulle part. Réserve
    choisie pour que toutes les configurations soient mesurées avant l'erreur, comme dans la vraie vague 1."""
    T.neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L, "RESERVE", T.ecrire_reserve(tmp_path, RESERVE_CV6))
    cle = T.fichier_cle(tmp_path)
    paye = {}

    def ex(t, ctx):  # comme un vrai banc : le JSONL d'usage est écrit sur disque
        (ctx["sortie"] / "usage").mkdir(exist_ok=True)
        T.ecrire_usage(ctx["sortie"] / "usage" / f"{t['id']}.jsonl", [("claude-sonnet-5-5", "claude-sonnet-5-5", 20_000, 0)])
        paye[t["id"]] = paye.get(t["id"], 0.0) + 0.04
        return T.executeur_factice(p=20_000, s=0, modele="claude-sonnet-5-5")(t, ctx)

    vrai_ranger, n = L.ranger, [0]

    def ranger(sortie, t, garder):
        n[0] += 1
        if n[0] == 200:
            raise OSError("disque plein")
        return vrai_ranger(sortie, t, garder)

    pmax = L.preparer(L.analyser(["--vague", "1", "--apercu", "--reel", "--reserve", str(L.RESERVE)]))["plan"]
    plafond = str(int(pmax["plafond_permis_usd"]))
    monkeypatch.setattr(L, "ranger", ranger)
    rc1 = L.main(T.argv(tmp_path, "--reel", "--concurrence", "1", plafond=plafond, accord=plafond, reserve=L.RESERVE),
                 executeur=ex, base_env={}, chemin_cle=cle, extracteur=T.extracteur_ok)
    monkeypatch.setattr(L, "ranger", vrai_ranger)
    v1 = T.dossier_unique(tmp_path)
    paye_v1 = sum(paye.values())
    _, orphelines = L.lire_tentatives(v1 / "tentatives.jsonl")
    p = T.plafond_permis_v2(tmp_path, v1, "1000", reel=True)
    rc2 = T.main_v2_reelle(tmp_path, v1, "1000", p, T.executeur_factice(p=5_000, s=0, modele="claude-sonnet-5-5"))
    compte_v1 = sum(l["cout_usd"] or 0 for l in T.lignes_cout(v1))
    print(f"\nCV6 vague 1 : code {rc1}, fin={json.loads((v1 / 'cout.json').read_text())['fin'] is not None}, orphelines "
          f"{[o['id'] for o in orphelines]} ; vague 2 : code {rc2} ; vague 1 payée {paye_v1:.2f} USD, comptée "
          f"{compte_v1:.2f} USD")
    assert rc1 == 4 and len(orphelines) == 1 and rc2 == 0
    assert paye_v1 - compte_v1 == pytest.approx(0.04)


# ======================================================================== CV7 : erreurs d'API hors de la liste
@pytest.mark.parametrize("texte", ["Data returned by API invalid for expected schema.", "list index out of range"])
def test_CV7_anomalie_d_api_hors_liste_rangee_en_exception_d_outil(texte):
    """WB_ERREURS_API ne couvre pas toutes les exceptions côté API : APIResponseValidationError du SDK OpenAI, ou une
    réponse sans choix (IndexError dans _call_llm_structured) deviennent des « exceptions d'outil » : erreurs de
    l'agent, jamais relancées, comptées comme telles."""
    assert L.classer({"env": "WorkBench"}, {"ok": True, "terminaison": texte, "trace": False})[1] == L.ARRET_EXCEPTION_OUTIL


# ======================================================================== CV5b : Ctrl-C pendant le démarrage de τ-bench
def test_CV5b_ctrl_c_pendant_le_demarrage_de_tau2_cout_inconnu_et_montant_a_saisir(tmp_path, monkeypatch):
    """τ-bench écrit results.json (sans simulation) dès la préparation du lot, avant tout appel (runner/checkpoint.py,
    try_resume). Une partie coupée par Ctrl-C pendant son démarrage (chargement, index bm25 de la banque) sort en 130
    sans JSONL : « interrompue » au coût inconnu, et la reprise exige un --cout-retenu pour une tentative qui n'a fait
    aucun appel."""
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        nom = cmd[cmd.index("--save-to") + 1]
        T.resultats_tau2(tmp_path / "tau2" / "data" / "simulations" / nom / "results.json", sims=0)
        return 130  # os._exit(130) de τ-bench sur Ctrl-C

    monkeypatch.setattr(pe, "executer_enfant", faux)
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague([(partie_tau("banque", "claude-opus-5-5", "task_001"), 1)], 1, compta, ctx, journal,
                   L.executer_partie)
    (x,) = reg.lignes
    print(f"\nCV5b statut={x['statut']} cout_inconnu={x['cout_inconnu']} ; en suspens : "
          f"{L.couts_inconnus_en_suspens(reg.lignes)}")
    assert x["statut"] == L.INTERROMPUE and x["cout_inconnu"]
    assert L.couts_inconnus_en_suspens(reg.lignes) == [x["id"]]


# ======================================================================== CV8 : WorkBench, répertoire commun à tous les lanceurs
def test_CV8_essai_a_blanc_en_parallele_mele_ses_predictions_a_une_partie_reelle(tmp_path, monkeypatch):
    """verrou_wb n'agit que dans un processus, et le verrou du choix 24 que sur un dossier de vague : deux lanceurs
    (un réel et un à blanc, « plusieurs essais restent permis ») font écrire WorkBench dans le même
    externe/workbench-run/data/results/. Même modèle, même domaine, même seconde : même nom de fichier ; la prédiction
    factice écrase la vraie, et la partie réelle la garde. Deux processus simulés par deux fils, chacun son contexte."""
    T.preparer_workbench(tmp_path, monkeypatch)
    import threading
    a_ecrit, b_ecrit = threading.Event(), threading.Event()
    nom = "claude-haiku-5-5_all_2026-11-06_12-00-00"  # nom pris au lancement : même seconde pour les deux

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        reel = "/reel/" in env["PILOTE_USAGE_FILE"]
        d = tmp_path / "wbrun" / "data" / "results" / "email"
        d.mkdir(parents=True, exist_ok=True)
        if not reel:
            a_ecrit.wait(5)
        (d / f"{nom}.csv").write_text('"task","function_calls","full_response","error"\n'
                                      f'"q","[\'{"REEL" if reel else "FACTICE"}\']","x",""\n')
        T.ecrire_usage(env["PILOTE_USAGE_FILE"], [("claude-haiku-5-5", "claude-haiku-5-5", 10, 2)])
        if reel:
            a_ecrit.set()
            b_ecrit.wait(5)  # le processus réel finit après l'écriture du processus à blanc
        else:
            b_ecrit.set()
            time.sleep(0.3)
        return 0

    monkeypatch.setattr(pe, "executer_enfant", faux)
    t = {"id": "WorkBench-haiku-p01-email_1", "env": "WorkBench", "modele": "claude-haiku-5-5", "tache": "email:1",
         "passage": 1, "rang": 1, "n_config": 1}
    res = {}

    def jouer(cle_ctx, reel):
        sortie = tmp_path / cle_ctx
        sortie.mkdir()
        ctx = {"sortie": sortie, "reel": reel, "env_enfant": {}, "cle": None, "horodatage": "h", "vague": 1,
               "verrou_wb": threading.Lock()}  # un verrou par processus, comme en vrai
        res[cle_ctx] = L.executer_partie(dict(t), ctx)

    fils = [threading.Thread(target=jouer, args=("reel", True)), threading.Thread(target=jouer, args=("blanc", False))]
    for f in fils:
        f.start()
    for f in fils:
        f.join()
    csv_reel = [c for c in res["reel"]["copies"] if c.endswith(".csv")]
    contenu = open(csv_reel[0]).read() if csv_reel else ""
    print(f"\nCV8 partie réelle : ok={res['reel']['ok']} classée {L.classer(t, res['reel'])[0]} ; sa prédiction contient "
          f"{'FACTICE' if 'FACTICE' in contenu else 'REEL'} ; partie à blanc : {res['blanc']['erreur']}")
    assert res["reel"]["ok"] and "FACTICE" in contenu and L.classer(t, res["reel"])[0] == L.TERMINEE
    assert "csv de prédictions absent" in (res["blanc"]["erreur"] or "")
