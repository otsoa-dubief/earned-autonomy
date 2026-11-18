"""Non-régression des 13 constats de la revue du lanceur (revues/code/2026-11-06_revue_lanceur.md), des 9 constats de
sa contre-vérification (A à I) et des décisions qui ont suivi : chaque test affirme le comportement corrigé. Aucun appel
réel : exécuteur factice ou enfant simulé (pe.executer_enfant remplacé), fausse clé dans un fichier temporaire, bancs
redirigés vers des dossiers temporaires."""
import fcntl
import json
import math
import os
import socket
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path

import pytest

import cout_v2 as cv
import lanceur as L
import pilote_etape1 as pe
import test_lanceur as T


# ------------------------------------------------------------------------------------------------ aides
def parties_wb(n, modele="claude-opus-5-5"):
    out = []
    for i in range(n):
        tache, passage = f"email:{i % 2}", 1 + i // 2
        out.append({"id": L.id_partie("WorkBench", modele, passage, tache), "env": "WorkBench", "modele": modele,
                    "tache": tache, "passage": passage, "rang": i + 1, "n_config": n})
    return [(x, 1) for x in out]


def partie_tau(env="aviation", modele="claude-opus-5-5", tache="1"):
    return {"id": L.id_partie(env, modele, 1, tache), "env": env, "modele": modele, "tache": tache, "passage": 1,
            "rang": 1, "n_config": 1}


def predictions(tmp_path, erreur="", modele="claude-opus-5-5", traces=None):
    """Fichiers de prédictions WorkBench nommés à la seconde ; `traces` : liste d'étapes (llm_input, llm_output)."""
    d = tmp_path / "wbrun" / "data" / "results" / "email"
    d.mkdir(parents=True, exist_ok=True)
    n = f"{modele}_all_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    (d / f"{n}.csv").write_text(f'"task","function_calls","full_response","error"\n"q","[]","x","{erreur}"\n')
    if traces is not None:
        (d / f"{n}_traces.json").write_text(json.dumps([{"task": "q", "steps": [
            {"llm_input": i, "llm_output": o, "action": "a", "action_input": {}, "observation": ""} for i, o in traces]}]))
        (d / f"{n}_meta.json").write_text(json.dumps({"sample_system_prompt": "système " * 50}))
    return n


def enfant_wb(tmp_path, erreur="", usage=True, traces=None, jetons=1000, notes=None, compta=None):
    def faux(cmd, env, cwd, log, cle=None, delai=0):
        if notes is not None:
            notes.append(compta.doit_arreter() if compta is not None else None)
        predictions(tmp_path, erreur, traces=traces)
        if usage:
            T.ecrire_usage(env["PILOTE_USAGE_FILE"], [("claude-opus-5-5", "claude-opus-5-5", jetons, 0)])
        time.sleep(0.05)
        return 0
    return faux


def lancer_reel_v1(tmp_path, monkeypatch, ex, *extra):
    monkeypatch.setattr(L, "RESERVE", T.ecrire_reserve(tmp_path))
    return L.main(T.argv(tmp_path, "--reel", "--concurrence", "1", *extra, reserve=L.RESERVE, graine=None), executeur=ex,
                  base_env={}, chemin_cle=T.fichier_cle(tmp_path), extracteur=T.extracteur_ok)


# ======================================================================== constat 1 : un seul lancement par vague
def test_c1_relancer_une_vague_reelle_sans_reprendre_est_refuse(tmp_path, monkeypatch, capsys):
    T.neutraliser(monkeypatch, tmp_path)
    cher = T.executeur_factice(p=200_000, s=0, modele="claude-sonnet-5-5")  # 0,40 $ par partie
    assert lancer_reel_v1(tmp_path, monkeypatch, cher) == 4
    capsys.readouterr()
    trace, extractions = [], []

    def extracteur(dossier, env):
        extractions.append(dossier)
        T.extracteur_ok(dossier, env)

    assert L.main(T.argv(tmp_path, "--reel", "--concurrence", "1", reserve=L.RESERVE, graine=None),
                  executeur=T.executeur_factice(trace), base_env={}, chemin_cle=T.fichier_cle(tmp_path),
                  extracteur=extracteur) == 2
    err = capsys.readouterr().err
    assert "REFUS" in err and "--reprendre" in err and not trace
    assert not extractions  # refusé dès preparer, avant la clé et l'extraction des outils (le flock de B confirme)
    (d,) = list((tmp_path / "s" / "vague1").iterdir())  # un seul dossier, un seul plafond
    assert json.loads((d / "cout.json").read_text())["cumul_usd"] == pytest.approx(2.4)
    assert not (d / L.NOM_VERROU).exists()  # verrou rendu à la fin


def test_c1_verrou_vivant_seconde_reprise_refusee_rien_joue_deux_fois(tmp_path, monkeypatch):
    T.neutraliser(monkeypatch, tmp_path)
    assert L.main(T.argv(tmp_path, "--limite", "2"), executeur=T.executeur_factice(), base_env={},
                  extracteur=T.extracteur_ok) == 0
    d = T.dossier_unique(tmp_path)
    args = T.argv(tmp_path, "--reprendre", str(d), "--limite", "10", "--concurrence", "1")
    joue_par, codes = {"premiere": [], "seconde": []}, []

    def seconde(t, ctx):
        joue_par["seconde"].append(t["id"])
        return T.executeur_factice()(t, ctx)

    def premiere(t, ctx):
        joue_par["premiere"].append(t["id"])
        if len(joue_par["premiere"]) == 1:  # seconde reprise lancée pendant la première tentative de la première
            assert json.loads((d / L.NOM_VERROU).read_text())["pid"] > 0
            codes.append(L.main(list(args), executeur=seconde, base_env={}, extracteur=T.extracteur_ok))
        return T.executeur_factice()(t, ctx)

    assert L.main(list(args), executeur=premiere, base_env={}, extracteur=T.extracteur_ok) == 0
    fins, orphelines = L.lire_tentatives(d / "tentatives.jsonl")
    assert codes == [2] and joue_par["seconde"] == [] and len(joue_par["premiere"]) == 10 and not orphelines
    assert len(json.loads((d / "cout.json").read_text())["parties"]) == len(fins) == 12


def test_c1_verrou_orphelin_signale_et_repris(tmp_path, monkeypatch):
    T.neutraliser(monkeypatch, tmp_path)
    assert L.main(T.argv(tmp_path, "--limite", "2"), executeur=T.executeur_factice(), base_env={},
                  extracteur=T.extracteur_ok) == 0
    d = T.dossier_unique(tmp_path)
    mort = subprocess.Popen(["true"])
    mort.wait()  # PID d'un processus fini : verrou laissé par un lanceur tué
    (d / L.NOM_VERROU).write_text(json.dumps({"pid": mort.pid, "machine": L.socket.gethostname(),
                                              "debut": "2026-11-06T01:00:00"}))
    assert L.main(T.argv(tmp_path, "--reprendre", str(d), "--limite", "1"), executeur=T.executeur_factice(),
                  base_env={}, extracteur=T.extracteur_ok) == 0
    assert "VERROU ORPHELIN" in (d / "journal.log").read_text() and str(mort.pid) in (d / "journal.log").read_text()
    assert list(d.glob("verrou.orphelin-*")) and not (d / L.NOM_VERROU).exists()
    reprise = json.loads((d / "cout.json").read_text())["reprises"][-1]
    assert reprise["verrou_orphelin"]["pid"] == mort.pid


def test_c1_verrou_vivant_d_un_autre_processus(tmp_path):
    (tmp_path / L.NOM_VERROU).write_text(json.dumps({"pid": 1, "machine": L.socket.gethostname(), "debut": "x"}))
    with pytest.raises(pe.ErreurPilote, match="toujours vivant"):  # PID 1 : toujours vivant
        L.prendre_verrou(tmp_path)
    (tmp_path / L.NOM_VERROU).write_text(json.dumps({"pid": 1, "machine": "autre-machine", "debut": "x"}))
    with pytest.raises(pe.ErreurPilote, match="autre machine"):
        L.prendre_verrou(tmp_path)


# ======================================================================== constat 2 : rien ne part après l'arrêt
def test_c2_partie_workbench_non_lancee_apres_l_arret_et_laissee_en_file(tmp_path, monkeypatch):
    T.preparer_workbench(tmp_path, monkeypatch)
    ctx, compta, reg, journal = T.contexte(tmp_path, 5.0)  # seuil 4 $ ; une partie = 1 M jetons Opus = 4 $
    notes = []
    monkeypatch.setattr(pe, "executer_enfant", enfant_wb(tmp_path, jetons=1_000_000, notes=notes, compta=compta))
    file = parties_wb(3)
    L.lancer_vague(file, 3, compta, ctx, journal, L.executer_partie)
    assert notes == [False] and len(reg.lignes) == 1 and compta.cumul == pytest.approx(4.0)
    fins, orphelines = L.lire_tentatives(ctx["sortie"] / "tentatives.jsonl")
    assert not orphelines and len(fins) == 1
    jouee = reg.lignes[0]["partie"]  # la première à prendre le verrou WorkBench, quel que soit son rang
    assert [(x["id"], k) for x, k in L.file_d_attente([x for x, _ in file], fins)] == [
        (x["id"], 1) for x, _ in file if x["id"] != jouee]
    assert (ctx["sortie"] / "journal.log").read_text().count("non lancée : une tentative WorkBench") == 2


# ======================================================================== constat 3 : vague 1 close par la vague 2
def test_c3_reprise_de_la_vague_1_refusee_une_fois_la_vague_2_commencee(tmp_path, monkeypatch, capsys):
    T.neutraliser(monkeypatch, tmp_path)
    assert L.main(T.argv(tmp_path, "--limite", "3"), executeur=T.executeur_factice(), base_env={},
                  extracteur=T.extracteur_ok) == 0
    v1 = T.dossier_unique(tmp_path)
    p = T.plafond_permis_v2(tmp_path, v1, "1000")
    assert L.main(T.argv(tmp_path, "--vague1", str(v1), "--budget-restant-usd", "1000", "--limite", "2", vague=2,
                         plafond=str(p), accord=str(p), graine=None), executeur=T.executeur_factice(), base_env={},
                  extracteur=T.extracteur_ok) == 0
    marqueur = json.loads((v1 / L.NOM_MARQUEUR_VAGUE2).read_text())
    assert marqueur["vagues2"][0]["dossier"] == str(T.dossier_unique(tmp_path, 2).resolve())
    capsys.readouterr()
    trace = []
    assert L.main(T.argv(tmp_path, "--reprendre", str(v1)), executeur=T.executeur_factice(trace), base_env={},
                  extracteur=T.extracteur_ok) == 2
    assert not trace and "vague 2 a commencé" in capsys.readouterr().err


def test_c3_vague_2_a_blanc_sur_une_vague_1_reelle_ne_touche_pas_au_dossier_reel(tmp_path, monkeypatch):
    rc, v1 = T.vague1_reelle(tmp_path, monkeypatch)
    assert rc == 0
    avant = sorted(x.name for x in v1.iterdir())
    p = T.plafond_permis_v2(tmp_path, v1, "1000")
    verrou_v1 = []

    def extracteur(dossier, env):  # pendant la mise en route : aucun verrou posé dans le dossier réel (constat D)
        verrou_v1.append((v1 / L.NOM_VERROU).exists())
        T.extracteur_ok(dossier, env)

    assert L.main(T.argv(tmp_path, "--vague1", str(v1), "--budget-restant-usd", "1000", "--limite", "2", vague=2,
                         plafond=str(p), accord=str(p), graine=None, reserve=L.RESERVE),
                  executeur=T.executeur_factice(), base_env={}, extracteur=extracteur) == 0
    assert T.dossier_unique(tmp_path, 2).name.endswith("-blanc") and verrou_v1 == [False]
    assert not (v1 / L.NOM_MARQUEUR_VAGUE2).exists() and sorted(x.name for x in v1.iterdir()) == avant


# ======================================================================== constat 4 : WorkBench, usage absent
def test_c4_workbench_usage_absent_apres_des_appels_cout_majore_depuis_les_traces_et_arret(tmp_path, monkeypatch):
    T.preparer_workbench(tmp_path, monkeypatch)
    etapes = [("a" * 4000, "b" * 300), ("c" * 6000, "d" * 200)]
    monkeypatch.setattr(pe, "executer_enfant", enfant_wb(tmp_path, erreur=L.WB_MESSAGE_ARRET, usage=False,
                                                         traces=etapes))
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)  # réel
    L.lancer_vague(parties_wb(2), 1, compta, ctx, journal, L.executer_partie)
    (x,) = reg.lignes
    assert x["cout_majore"] and x["usage"] == "majoré" and x["cout_usd"] > 0 and "majoré" in compta.arret
    outils = json.loads((L.DOSSIER_OUTILS / "workbench.json").read_text())["outils"]
    systeme = len(("système " * 50).encode("utf-8"))
    # Sortie : le maximum du modèle à chaque étape, raisonnement compris (contre-vérification, constat G).
    attendu = sum((len(i) + systeme + L._octets(outils) + L.MARGE_FORMAT_JETONS) * 4.0 * 1.25
                  + 128_000 * 20.0 for i, _ in etapes) / 1e6
    assert x["cout_usd"] == pytest.approx(attendu) and compta.cumul == pytest.approx(attendu)


@pytest.mark.parametrize("erreur", [L.WB_MESSAGE_CONTEXTE, "Unknown datetime string format, unable to parse: x", ""])
def test_c4_workbench_usage_absent_sans_traces_cout_inconnu_et_arret(tmp_path, monkeypatch, erreur):
    T.preparer_workbench(tmp_path, monkeypatch)
    monkeypatch.setattr(pe, "executer_enfant", enfant_wb(tmp_path, erreur=erreur, usage=False))
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague(parties_wb(2), 1, compta, ctx, journal, L.executer_partie)
    assert len(reg.lignes) == 1 and reg.lignes[0]["cout_inconnu"] and "non compté" in compta.arret


# ======================================================================== constat 5 : exception d'outil WorkBench
def test_c5_exception_d_outil_arretee_exclue_jamais_relancee_comptee_par_environnement(tmp_path, monkeypatch):
    T.preparer_workbench(tmp_path, monkeypatch)
    texte = "Unknown datetime string format, unable to parse: next week"
    monkeypatch.setattr(pe, "executer_enfant", enfant_wb(tmp_path, erreur=texte))
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    file = parties_wb(1)
    L.lancer_vague(file, 1, compta, ctx, journal, L.executer_partie)
    (x,) = reg.lignes  # une seule tentative : jamais relancée
    assert (x["statut"], x["arret"], x["ok"], x["finale"], x["exclue"]) == (L.ARRETEE, L.ARRET_EXCEPTION_OUTIL, False,
                                                                            True, True)
    assert x["motif_exclusion"] == L.MOTIF_EXCEPTION_OUTIL and x["dossier"].startswith("ecartees/")
    assert x["cout_usd"] > 0 and compta.arret is None
    visible = (ctx["sortie"] / "journal.log").read_text()  # constat E : ni partie, ni modèle, ni façon de finir
    assert x["id"] not in visible and "opus" not in visible and texte not in visible
    assert "exception d'outil" not in visible and "fin d'une tentative WorkBench ; cumul=" in visible
    d = L.section_deroulement([p for p, _ in file], reg.lignes, [])
    assert d["exceptions_outil_par_environnement"] == {"WorkBench": 1}
    (c,) = d["par_configuration"]
    assert "gardees" not in c and "terminees" not in c and not c["arretees"] and not c["exclues"]
    assert L.ARRET_EXCEPTION_OUTIL not in json.dumps(d["par_configuration"], ensure_ascii=False)


@pytest.mark.parametrize("texte", ["Connection error.", "Request timed out.",
                                   "LLM call exceeded 75.0s wall-clock deadline; client closed",
                                   "Error code: 401 - invalid x-api-key"])
def test_c5_erreurs_d_api_workbench_restent_des_echecs_techniques(texte):
    assert L.classer({"env": "WorkBench"}, {"ok": True, "terminaison": texte, "trace": True})[0] == L.ECHEC


def test_c5_exceptions_d_outil_en_serie_arretent(tmp_path, monkeypatch):
    T.preparer_workbench(tmp_path, monkeypatch)
    monkeypatch.setattr(pe, "executer_enfant", enfant_wb(tmp_path, erreur="KeyError: 'xyz'"))
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague(parties_wb(6), 1, compta, ctx, journal, L.executer_partie)
    assert len(reg.lignes) == L.SERIE_EXCEPTIONS_OUTIL_MAX and "exceptions d'outil WorkBench de suite" in compta.arret


# ======================================================================== constat 6 : relances de τ-bench, contexte
def test_c6_tau2_sans_relance_interne_et_depassement_de_contexte_arrete_sans_trace(tmp_path, monkeypatch):
    cmd = L.commande_tau2({"id": "x", "env": "banque", "modele": "claude-opus-5-5", "tache": "task_001"}, "n", True)
    assert cmd[cmd.index("--max-retries") + 1] == "0"
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        nom = cmd[cmd.index("--save-to") + 1]
        f = tmp_path / "tau2" / "data" / "simulations" / nom / "results.json"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({"simulations": [{"id": "s", "task_id": "task_001", "messages": [],
                                                  "termination_reason": "infrastructure_error",
                                                  "info": {"error_type": "ContextWindowExceededError"}}]}))
        T.ecrire_usage(env["PILOTE_USAGE_FILE"], [("claude-opus-5-5", "claude-opus-5-5", 150_000, 500)] * 10)
        return 0

    monkeypatch.setattr(pe, "executer_enfant", faux)
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague([(partie_tau("banque", "claude-opus-5-5", "task_001"), 1)], 1, compta, ctx, journal,
                   L.executer_partie)
    (x,) = reg.lignes  # pas de relance
    assert (x["statut"], x["arret"], x["ok"], x["finale"], x["exclue"]) == (L.ARRETEE, L.ARRET_CONTEXTE, False, True,
                                                                            True)
    assert x["motif_exclusion"] == L.MOTIF_SANS_TRACE and "ContextWindowExceededError" in x["terminaison"]
    assert compta.cumul == pytest.approx(10 * (150_000 * 4.0 + 500 * 20.0) / 1e6) and compta.arret is None


def test_c6_autre_erreur_d_infrastructure_reste_un_echec_technique():
    r = {"ok": True, "terminaison": "infrastructure_error", "type_erreur": "APIConnectionError", "trace": True}
    assert L.classer({"env": "aviation"}, r)[0] == L.ECHEC


# ======================================================================== constat 7 : référence par banc et modèle
def test_c7_reference_du_nom_par_banc_et_modele(tmp_path):
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    tau, wb = partie_tau(modele="claude-haiku-5-5"), parties_wb(1, "claude-haiku-5-5")[0][0]

    def renvoye(t):
        return "claude-haiku-5-5" if t["env"] == "WorkBench" else "claude-haiku-5-5-20261001"

    L.lancer_vague([(tau, 1), (wb, 1)], 1, compta, ctx, journal, T.executeur_factice(renvoye=renvoye))
    assert [l["statut"] for l in reg.lignes] == [L.TERMINEE, L.TERMINEE] and compta.arret is None
    assert ctx["noms"].reference == {"tau2:claude-haiku-5-5": "claude-haiku-5-5-20261001",
                                     "workbench:claude-haiku-5-5": "claude-haiku-5-5"}


# ======================================================================== constat 8 : filet sur simulation finie
@pytest.mark.parametrize("terminaison,statut,gardee", [("infrastructure_error", L.ECHEC, False),
                                                       ("user_stop", L.TERMINEE, True)])
def test_c8_filet_de_35_minutes_classe_une_simulation_finie_sur_sa_terminaison(tmp_path, monkeypatch, terminaison,
                                                                               statut, gardee):
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        nom = cmd[cmd.index("--save-to") + 1]
        T.resultats_tau2(tmp_path / "tau2" / "data" / "simulations" / nom / "results.json", terminaison)
        T.ecrire_usage(env["PILOTE_USAGE_FILE"], [("claude-haiku-5-5", "claude-haiku-5-5", 100, 5),
                                                  ("claude-opus-5-5", "claude-opus-5-5", 200, 6)])
        return -1  # processus tué par le filet après l'enregistrement

    monkeypatch.setattr(pe, "executer_enfant", faux)
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague([(partie_tau(), 1)], 1, compta, ctx, journal, L.executer_partie)
    x = reg.lignes[0]
    assert (x["statut"], x["ok"], x["arret"]) == (statut, gardee, None)


# ======================================================================== constat 9 : WorkBench, fenêtre de contexte
def test_c9_workbench_fenetre_de_contexte_arretee_sans_trace_exclue(tmp_path, monkeypatch):
    T.preparer_workbench(tmp_path, monkeypatch)
    monkeypatch.setattr(pe, "executer_enfant", enfant_wb(tmp_path, erreur=L.WB_MESSAGE_CONTEXTE))
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague(parties_wb(1), 1, compta, ctx, journal, L.executer_partie)
    (x,) = reg.lignes
    assert (x["statut"], x["arret"], x["ok"], x["finale"], x["exclue"], x["motif_exclusion"]) == (
        L.ARRETEE, L.ARRET_CONTEXTE, False, True, True, L.MOTIF_SANS_TRACE)
    assert x["dossier"].startswith("ecartees/")


# ======================================================================== constat 10 : τ-bench planté sans usage
def enfant_tau2(tmp_path, sim=None, code=0):
    """Enfant τ-bench simulé : results.json avec la simulation `sim` (sans simulation si None), aucun JSONL d'usage."""
    def faux(cmd, env, cwd, log, cle=None, delai=0):
        f = tmp_path / "tau2" / "data" / "simulations" / cmd[cmd.index("--save-to") + 1] / "results.json"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps({"simulations": [sim] if sim else []}))
        return code
    return faux


def test_c10_tau2_simulation_avec_messages_sans_usage_lisible_cout_inconnu_et_arret(tmp_path, monkeypatch):
    """Constat 10, restreint par la contre-vérification (constat F) : des appels ont certainement eu lieu (la simulation
    a des messages), le JSONL manque, et results.json ne donne pas les jetons : coût inconnu, arrêt."""
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")
    sim = {"id": "s", "task_id": "1", "termination_reason": "user_stop", "messages": [{"role": "assistant"}]}
    monkeypatch.setattr(pe, "executer_enfant", enfant_tau2(tmp_path, sim))

    def illisible(*a, **k):
        raise ValueError("jetons absents")

    monkeypatch.setattr(pe, "appels_tau2", illisible)
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague([(partie_tau(), 1), (partie_tau(tache="2"), 1)], 1, compta, ctx, journal, L.executer_partie)
    (x,) = reg.lignes
    assert x["cout_inconnu"] and "non compté" in compta.arret and "--cout-retenu" in compta.arret


# ======================================================================== constat 11 : coût inconnu à la reprise
def test_c11_cout_inconnu_reprise_exige_un_montant_retenu(tmp_path, monkeypatch, capsys):
    T.neutraliser(monkeypatch, tmp_path)
    base, premier = T.executeur_factice(p=20_000, s=0, modele="claude-sonnet-5-5"), []

    def ex(t, ctx):
        r = base(t, ctx)
        if not premier:
            premier.append(t["id"])
            r.update(appels=None, renvoyes=[], cout_inconnu=True, ok=False, erreur="usage absent", usage="absent")
        return r

    assert lancer_reel_v1(tmp_path, monkeypatch, ex) == 4
    d = T.dossier_unique(tmp_path)
    reprise = T.argv(tmp_path, "--reel", "--reprendre", str(d), "--concurrence", "1", reserve=L.RESERVE, graine=None)
    capsys.readouterr()
    assert L.main(list(reprise), executeur=ex, base_env={}, chemin_cle=T.fichier_cle(tmp_path),
                  extracteur=T.extracteur_ok) == 2
    assert premier[0] in capsys.readouterr().err
    assert L.main(list(reprise) + ["--cout-retenu", "inconnue=1"], executeur=ex, base_env={},
                  chemin_cle=T.fichier_cle(tmp_path), extracteur=T.extracteur_ok) == 2  # identifiant étranger
    assert L.main(list(reprise) + ["--cout-retenu", f"{premier[0]}=0.05"], executeur=ex, base_env={},
                  chemin_cle=T.fichier_cle(tmp_path), extracteur=T.extracteur_ok) == 0
    cout = json.loads((d / "cout.json").read_text())
    (retenu,) = [l for l in cout["parties"] if l["statut"] == L.COUT_RETENU]
    assert retenu["cout_retenu_pour"] == premier[0] and retenu["cout_usd"] == 0.05
    assert cout["cumul_usd"] == pytest.approx(sum(l["cout_usd"] or 0 for l in cout["parties"]))
    assert cout["reprises"][-1]["couts_retenus"] == {premier[0]: 0.05}
    assert L.couts_inconnus_en_suspens(cout["parties"]) == []


def test_c11_vague_2_refusee_tant_que_la_vague_1_a_un_cout_inconnu(tmp_path, monkeypatch, capsys):
    T.neutraliser(monkeypatch, tmp_path)
    base = T.executeur_factice(p=20_000, s=0, modele="claude-sonnet-5-5")

    def ex(t, ctx):
        r = base(t, ctx)
        if t["id"].startswith("WorkBench"):
            r.update(appels=None, renvoyes=[], cout_inconnu=True, ok=False, erreur="usage absent")
        return r

    assert lancer_reel_v1(tmp_path, monkeypatch, ex) == 4
    v1 = T.dossier_unique(tmp_path)
    capsys.readouterr()
    assert T.main_v2_reelle(tmp_path, v1, "1000", 20, T.executeur_factice()) == 2
    assert "coûts inconnus" in capsys.readouterr().err


# ======================================================================== constat 12 : aucun .env chargé
def test_c12_enfants_et_extraction_sans_dotenv(tmp_path, monkeypatch):
    T.neutraliser(monkeypatch, tmp_path)
    trace, vus = [], []

    def extracteur(dossier, env):
        vus.append(env.get("PYTHON_DOTENV_DISABLED"))
        T.extracteur_ok(dossier, env)

    assert L.main(T.argv(tmp_path, "--limite", "2"), executeur=T.executeur_factice(trace), base_env={"PATH": "/b"},
                  extracteur=extracteur) == 0
    assert vus == ["1"] and all(env["PYTHON_DOTENV_DISABLED"] == "1" for _, _, env in trace)
    env = L.environnement_enfants({"PATH": "/b"}, "sk-ant-x")
    pe.verifier_env_enfant(env, True)
    assert env["PYTHON_DOTENV_DISABLED"] == "1"


# ======================================================================== constat 13 : refus propres
def orpheline(d, rang=2, lisible=False):
    """Ajoute à tentatives.jsonl une tentative commencée sans fin (la partie de ce rang de la vague 1), avec son
    fichier d'usage, lisible ou coupé en plein milieu."""
    x = L.parties_vague1(L.construire_parties(T.RESERVE_TEST, 5))[rang]
    t = L.tentative(x, 1, 1)
    with open(d / "tentatives.jsonl", "a") as fh:
        fh.write(json.dumps({"evenement": "début", "id": t["id"],
                             "tentative": {c: t[c] for c in L.CHAMPS_TENTATIVE}}) + "\n")
    (d / "usage").mkdir(exist_ok=True)
    if lisible:
        T.ecrire_usage(d / "usage" / f"{t['id']}.jsonl", [("claude-sonnet-5-5", "claude-sonnet-5-5", 10_000, 0)])
    else:
        (d / "usage" / f"{t['id']}.jsonl").write_text('{"modele": "claude-sonnet-5-5", "prompt_tok')  # coupée
    return t["id"]


def test_c13_orpheline_illisible_refus_propre_puis_reprise_avec_cout_retenu(tmp_path, monkeypatch, capsys):
    """Une orpheline lisible devant l'illisible (comme R13) : le refus ne laisse rien à moitié fait, la lisible n'est
    pas mise à l'écart avant que l'illisible fasse refuser (contre-vérification, nuance du constat 13)."""
    T.neutraliser(monkeypatch, tmp_path)
    assert L.main(T.argv(tmp_path, "--limite", "2"), executeur=T.executeur_factice(), base_env={},
                  extracteur=T.extracteur_ok) == 0
    d = T.dossier_unique(tmp_path)
    lisible, tid = orpheline(d, 3, lisible=True), orpheline(d, 2)
    capsys.readouterr()
    assert L.main(T.argv(tmp_path, "--reprendre", str(d)), executeur=T.executeur_factice(), base_env={},
                  extracteur=T.extracteur_ok) == 2
    assert "REFUS" in capsys.readouterr().err
    fins, orphelines = L.lire_tentatives(d / "tentatives.jsonl")
    assert [o["id"] for o in orphelines] == [lisible, tid] and len(fins) == 2  # rien de déplacé ni d'écrit
    assert all((d / "usage" / f"{i}.jsonl").exists() for i in (lisible, tid)) and not list(d.rglob("*interrompue*"))
    assert not (d / L.NOM_VERROU).exists()
    assert L.main(T.argv(tmp_path, "--reprendre", str(d), "--limite", "1", "--cout-retenu", f"{tid}=0.25"),
                  executeur=T.executeur_factice(), base_env={}, extracteur=T.extracteur_ok) == 0
    inter = {l["id"].split("-interrompue-")[0]: l for l in T.lignes_cout(d) if l["statut"] == L.INTERROMPUE}
    assert set(inter) == {lisible, tid} and inter[tid]["cout_usd"] == 0.25 and inter[tid]["cout_retenu_pour"] == tid
    assert inter[lisible]["cout_usd"] == pytest.approx(10_000 * 2.0 / 1e6) and not inter[lisible]["cout_majore"]


def test_c13_second_lancement_dans_la_meme_seconde_refus_propre(tmp_path, monkeypatch, capsys):
    T.neutraliser(monkeypatch, tmp_path)

    class Fige(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 11, 6, 12, 0, 0)

    monkeypatch.setattr(L, "datetime", Fige)
    args = T.argv(tmp_path, "--limite", "1")
    assert L.main(list(args), executeur=T.executeur_factice(), base_env={}, extracteur=T.extracteur_ok) == 0
    capsys.readouterr()
    assert L.main(list(args), executeur=T.executeur_factice(), base_env={}, extracteur=T.extracteur_ok) == 2
    assert "REFUS" in capsys.readouterr().err


# =================================================================================================================
# Contre-vérification du 06/11 (revues/code/2026-11-06_revue_lanceur.md, section « Contre-vérification ») : constats
# A à I, chacun affirmé corrigé.
# =================================================================================================================
def args_vague2(tmp_path, v1, plafond):
    return T.argv(tmp_path, "--vague1", str(v1), "--budget-restant-usd", "1000", "--limite", "2", vague=2,
                  plafond=str(plafond), accord=str(plafond), graine=None)


# ======================================================================== A : une seule racine en réel
def test_cA_reel_refuse_toute_autre_racine_de_sortie(tmp_path, monkeypatch, capsys):
    T.neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L, "RESERVE", T.ecrire_reserve(tmp_path))
    a = T.argv(tmp_path, "--reel", "--concurrence", "1", reserve=L.RESERVE, graine=None)
    a[a.index("--sortie-racine") + 1] = str(tmp_path / "ailleurs")
    trace = []
    assert L.main(a, executeur=T.executeur_factice(trace), base_env={}, chemin_cle=T.fichier_cle(tmp_path),
                  extracteur=T.extracteur_ok) == 2
    assert not trace and not (tmp_path / "ailleurs").exists() and "--sortie-racine refusé" in capsys.readouterr().err
    b = T.argv(tmp_path, "--limite", "1")  # à blanc, la racine reste libre
    b[b.index("--sortie-racine") + 1] = str(tmp_path / "ailleurs")
    assert L.main(b, executeur=T.executeur_factice(), base_env={}, extracteur=T.extracteur_ok) == 0


# ======================================================================== B : contrôle et création ensemble
def test_cB_deux_lancements_reels_qui_se_chevauchent_un_seul_dossier(tmp_path, monkeypatch, capsys):
    """CV2 : la même commande relancée pendant l'extraction des outils du premier lancement. Le second ouvre son
    dossier ; le premier, revérifiant sous le flock de vague1/ au moment de créer le sien, est refusé."""
    T.neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L, "RESERVE", T.ecrire_reserve(tmp_path))
    cle = T.fichier_cle(tmp_path)
    args = T.argv(tmp_path, "--reel", "--concurrence", "1", reserve=L.RESERVE, graine=None)
    codes, trace = [], []

    def extraction_du_premier(dossier, env):
        T.extracteur_ok(dossier, env)
        if not codes:
            codes.append(L.main(list(args), executeur=T.executeur_factice(), base_env={}, chemin_cle=cle,
                                extracteur=T.extracteur_ok))
            time.sleep(1.1)  # dossiers nommés à la seconde

    rc1 = L.main(list(args), executeur=T.executeur_factice(trace), base_env={}, chemin_cle=cle,
                 extracteur=extraction_du_premier)
    reels = [d for d in (tmp_path / "s" / "vague1").iterdir() if d.is_dir() and not d.name.endswith("-blanc")]
    assert codes == [0] and rc1 == 2 and len(reels) == 1 and not trace
    assert "déjà un dossier réel" in capsys.readouterr().err


# ======================================================================== C : WorkBench, verrou commun aux lanceurs
def test_cC_parties_workbench_de_deux_lanceurs_serialisees_chacune_sa_prediction(tmp_path, monkeypatch):
    """CV8 : un lanceur réel et un lanceur à blanc (deux contextes, deux verrou_wb), même modèle, même domaine, même
    seconde. Le verrou commun les sérialise : jamais deux enfants WorkBench à la fois, chacun garde sa prédiction."""
    T.preparer_workbench(tmp_path, monkeypatch)
    nom = "claude-haiku-5-5_all_2026-11-06_12-00-00"
    en_cours, pics = [0], []

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        en_cours[0] += 1
        pics.append(en_cours[0])
        reel = "/reel/" in env["PILOTE_USAGE_FILE"]
        d = tmp_path / "wbrun" / "data" / "results" / "email"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{nom}.csv").write_text('"task","function_calls","full_response","error"\n'
                                      f'"q","[\'{"REEL" if reel else "FACTICE"}\']","x",""\n')
        T.ecrire_usage(env["PILOTE_USAGE_FILE"], [("claude-haiku-5-5", "claude-haiku-5-5", 10, 2)])
        time.sleep(0.3)
        en_cours[0] -= 1
        return 0

    monkeypatch.setattr(pe, "executer_enfant", faux)
    t = {"id": "WorkBench-haiku-p01-email_1", "env": "WorkBench", "modele": "claude-haiku-5-5", "tache": "email:1",
         "passage": 1, "rang": 1, "n_config": 1}
    res = {}

    def jouer(nom_ctx, reel):
        sortie = tmp_path / nom_ctx
        sortie.mkdir()
        ctx = {"sortie": sortie, "reel": reel, "env_enfant": {}, "cle": None, "horodatage": "h", "vague": 1,
               "verrou_wb": threading.Lock()}  # un verrou par processus, comme en vrai
        res[nom_ctx] = L.executer_partie(dict(t), ctx)

    fils = [threading.Thread(target=jouer, args=a) for a in (("reel", True), ("blanc", False))]
    for f in fils:
        f.start()
    for f in fils:
        f.join()
    assert max(pics) == 1 and len(pics) == 2
    for n, attendu in (("reel", "REEL"), ("blanc", "FACTICE")):
        (c,) = [x for x in res[n]["copies"] if x.endswith(".csv")]
        assert res[n]["ok"] and attendu in Path(c).read_text()
    assert (tmp_path / "wbrun" / "data" / L.NOM_VERROU_WB).is_file()


def test_cC_partie_workbench_qui_attend_le_verrou_commun_non_lancee_si_l_arret_tombe(tmp_path, monkeypatch):
    T.preparer_workbench(tmp_path, monkeypatch)
    lances = []
    monkeypatch.setattr(pe, "executer_enfant", lambda *a, **k: lances.append(1) or 0)
    chemin = tmp_path / "wbrun" / "data" / L.NOM_VERROU_WB
    chemin.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(chemin, os.O_CREAT | os.O_RDWR)
    fcntl.flock(fd, fcntl.LOCK_EX)  # un autre lanceur joue sa partie WorkBench
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    ctx["compta"] = compta
    minuterie = threading.Timer(0.3, compta.arreter, args=("seuil d'arrêt atteint",))
    minuterie.start()
    try:
        r = L.executer_partie(parties_wb(1)[0][0], ctx)
    finally:
        minuterie.cancel()
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    assert r["non_lancee"] and not lances


# ======================================================================== D : la vague 2 et le verrou de la vague 1
def test_cD_vague_2_prend_le_verrou_de_la_vague_1_pendant_sa_mise_en_route(tmp_path, monkeypatch, capsys):
    T.neutraliser(monkeypatch, tmp_path)
    assert L.main(T.argv(tmp_path, "--limite", "3"), executeur=T.executeur_factice(), base_env={},
                  extracteur=T.extracteur_ok) == 0
    v1 = T.dossier_unique(tmp_path)
    p = T.plafond_permis_v2(tmp_path, v1, "1000")
    # Une reprise de la vague 1 tient son verrou (processus vivant) : la vague 2 est refusée, rien n'est marqué.
    (v1 / L.NOM_VERROU).write_text(json.dumps({"pid": os.getpid(), "machine": socket.gethostname(), "debut": "t"}))
    capsys.readouterr()
    trace = []
    assert L.main(args_vague2(tmp_path, v1, p), executeur=T.executeur_factice(trace), base_env={},
                  extracteur=T.extracteur_ok) == 2
    assert not trace and not (v1 / L.NOM_MARQUEUR_VAGUE2).exists() and "verrouillé" in capsys.readouterr().err
    (v1 / L.NOM_VERROU).unlink()
    # Sinon : verrou de la vague 1 tenu pendant la mise en route (le marqueur s'écrit dessous), rendu ensuite.
    pendant = []

    def extracteur(dossier, env):
        pendant.append((v1 / L.NOM_VERROU).exists())
        T.extracteur_ok(dossier, env)

    assert L.main(args_vague2(tmp_path, v1, p), executeur=T.executeur_factice(), base_env={}, extracteur=extracteur) == 0
    assert pendant == [True] and (v1 / L.NOM_MARQUEUR_VAGUE2).is_file() and not (v1 / L.NOM_VERROU).exists()


# ======================================================================== E : journal visible sans partie WorkBench
def test_cE_journal_visible_ne_designe_aucune_partie_workbench_journal_complet_a_part(tmp_path, monkeypatch):
    """CV4 : deux parties à la fois, τ-bench intercalé, une exception d'outil. Au journal visible, aucune ligne ne
    nomme une partie ou un modèle WorkBench, et toutes les fins WorkBench se ressemblent ; journal_complet.log a tout,
    sous son avertissement."""
    T.preparer_workbench(tmp_path, monkeypatch)
    erreur = {"WorkBench-sonnet-p01-email_1": "Unknown datetime string format, unable to parse: next week"}

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        pid = Path(env["PILOTE_USAGE_FILE"]).stem
        d = tmp_path / "wbrun" / "data" / "results" / "email"
        d.mkdir(parents=True, exist_ok=True)
        n = f"claude-x_all_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        (d / f"{n}.csv").write_text('"task","function_calls","full_response","error"\n'
                                    f'"q","[]","x","{erreur.get(pid, "")}"\n')
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
    ctx, compta, reg, _ = T.contexte(tmp_path, 100.0)
    journal = L.JournalVague(ctx["sortie"])
    L.lancer_vague(file, 2, compta, ctx, journal, executeur)
    assert [l["arret"] for l in reg.lignes if l["partie"] == wb[1]["id"]] == [L.ARRET_EXCEPTION_OUTIL]
    visible = (ctx["sortie"] / "journal.log").read_text().splitlines()
    lignes_wb = [l for l in visible if "WorkBench" in l]
    assert len(lignes_wb) == 6  # trois débuts, trois fins
    assert not any(mot in l for l in lignes_wb for mot in ("haiku", "sonnet", "opus", "email"))
    assert not any(x["id"] in l for l in visible for x in wb)
    fins = {l.split(" ", 1)[1].split(" ; cumul=")[0] for l in lignes_wb if "fin d'une tentative WorkBench" in l}
    assert fins == {"fin d'une tentative WorkBench"}  # rien ne distingue l'exception d'outil
    complet = (ctx["sortie"] / L.NOM_JOURNAL_COMPLET).read_text().splitlines()
    assert complet[0] == L.ENTETE_JOURNAL_COMPLET
    assert all(any(f"début {x['id']} ({x['modele']}" in l for l in complet) for x in wb)
    assert any(f"fin {wb[1]['id']} statut={L.ARRETEE} ({L.ARRET_EXCEPTION_OUTIL})" in l for l in complet)
    assert len(complet) == len(visible) + 1


def test_cE_echec_technique_workbench_visible_sans_modele():
    t = {"id": "WorkBench-opus-p01-email_1", "env": "WorkBench"}
    ligne = {"id": t["id"], "statut": L.ECHEC, "arret": None, "terminaison": "",
             "erreur": "nom de fichier WorkBench déjà utilisé dans la vague : claude-opus-5-5_all_2026-11-06_12-00-00"}
    visible, complet = L.lignes_de_fin(t, ligne, 1.0)
    assert visible.startswith("fin d'une tentative WorkBench : échec technique ; ") and "opus" not in visible
    assert t["id"] in complet and "claude-opus-5-5_all_" in complet


# ======================================================================== F : coût inconnu seulement si des appels sont sûrs
def test_cF_tau2_premier_appel_en_echec_sans_usage_ni_cout_inconnu_ni_arret(tmp_path, monkeypatch):
    """CV5 : simulation vide (infrastructure_error, premier appel en échec), aucun JSONL : coût nul, aucun montant à
    saisir ; échec technique, relancé une fois puis exclu, comme toute panne."""
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")
    sim = {"id": "s", "task_id": "1", "messages": [], "termination_reason": "infrastructure_error",
           "info": {"error_type": "InternalServerError", "error": "AnthropicException - Overloaded",
                    "failed_after_attempts": 1}}
    monkeypatch.setattr(pe, "executer_enfant", enfant_tau2(tmp_path, sim))
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague([(partie_tau(), 1)], 1, compta, ctx, journal, L.executer_partie)
    assert [l["statut"] for l in reg.lignes] == [L.ECHEC, L.ECHEC]
    assert not any(l["cout_inconnu"] for l in reg.lignes) and compta.cumul == 0 and compta.arret is None
    assert L.couts_inconnus_en_suspens(reg.lignes) == []


def test_cF_tau2_ctrl_c_au_demarrage_interrompue_sans_montant_a_saisir(tmp_path, monkeypatch):
    """CV5b : results.json sans simulation (écrit avant tout appel), code 130, aucun JSONL."""
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")
    monkeypatch.setattr(pe, "executer_enfant", enfant_tau2(tmp_path, None, code=130))
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague([(partie_tau("banque", "claude-opus-5-5", "task_001"), 1)], 1, compta, ctx, journal,
                   L.executer_partie)
    (x,) = reg.lignes
    assert x["statut"] == L.INTERROMPUE and not x["cout_inconnu"] and L.couts_inconnus_en_suspens(reg.lignes) == []


@pytest.mark.parametrize("cas", ["contexte", "filet"])
def test_cF_contexte_ou_filet_sans_usage_restent_des_couts_inconnus(tmp_path, monkeypatch, cas):
    """Des appels sont sûrs : dépassement de contexte (simulation vide, mais la conversation a grandi jusqu'à la
    limite), ou filet de 35 minutes."""
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")
    sim = {"id": "s", "task_id": "1", "messages": [], "termination_reason": "infrastructure_error",
           "info": {"error_type": L.TYPE_ERREUR_CONTEXTE}} if cas == "contexte" else None
    monkeypatch.setattr(pe, "executer_enfant", enfant_tau2(tmp_path, sim, code=0 if cas == "contexte" else -1))
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague([(partie_tau(), 1), (partie_tau(tache="2"), 1)], 1, compta, ctx, journal, L.executer_partie)
    (x,) = reg.lignes
    assert x["cout_inconnu"] and "non compté" in compta.arret


def test_cF_workbench_erreur_d_api_sans_usage_ni_cout_inconnu_ni_arret(tmp_path, monkeypatch):
    """Même règle pour WorkBench : après une erreur d'API sans usage, aucun appel n'a abouti."""
    T.preparer_workbench(tmp_path, monkeypatch)
    monkeypatch.setattr(pe, "executer_enfant", enfant_wb(tmp_path, erreur="Error code: 529 overloaded", usage=False))
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague(parties_wb(1), 1, compta, ctx, journal, L.executer_partie)
    assert [l["statut"] for l in reg.lignes] == [L.ECHEC, L.ECHEC]
    assert not any(l["cout_inconnu"] for l in reg.lignes) and compta.cumul == 0 and compta.arret is None


# ======================================================================== G : majorant WorkBench, sortie bornée
def test_cG_majorant_workbench_couvre_le_raisonnement_absent_des_traces(tmp_path):
    """Pilote, WorkBench-haiku-6 : un appel a facturé 6 409 jetons de sortie pour 460 octets tracés. La sortie de
    chaque étape est bornée par le maximum du modèle (128 000 jetons), raisonnement compris."""
    (tmp_path / "x_traces.json").write_text(json.dumps([{"task": "q", "steps": [
        {"llm_input": "a" * 3000, "llm_output": "b" * 460}]}]))
    (tmp_path / "x_meta.json").write_text(json.dumps({"sample_system_prompt": ""}))
    copies = [str(tmp_path / "x_traces.json"), str(tmp_path / "x_meta.json")]
    m = L.cout_majorant_workbench(copies, "claude-haiku-5-5", outils=[])
    reel = cv.bilan([{"modele": "claude-haiku-5-5", "prompt_tokens": 3000, "completion_tokens": 6409,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}])["cout_usd"]
    assert m >= reel and m == pytest.approx(((3000 + 2 + L.MARGE_FORMAT_JETONS) * 0.10 * 1.25 + 128_000 * 0.50) / 1e6)
    assert set(L.MAX_SORTIE_JETONS) == set(L.MODELES) and L.cout_majorant_workbench(copies, "claude-x", []) is None


# ======================================================================== H : vague 1 avec une orpheline
def test_cH_vague_2_refuse_une_vague_1_qui_a_une_tentative_commencee_sans_fin(tmp_path, monkeypatch, capsys):
    T.neutraliser(monkeypatch, tmp_path)
    assert L.main(T.argv(tmp_path, "--limite", "3"), executeur=T.executeur_factice(), base_env={},
                  extracteur=T.extracteur_ok) == 0
    v1 = T.dossier_unique(tmp_path)
    p = T.plafond_permis_v2(tmp_path, v1, "1000")
    tid = orpheline(v1, 3, lisible=True)  # erreur interne ou arrêt brutal : commencée, jamais finie
    capsys.readouterr()
    trace = []
    assert L.main(args_vague2(tmp_path, v1, p), executeur=T.executeur_factice(trace), base_env={},
                  extracteur=T.extracteur_ok) == 2
    assert not trace and tid in capsys.readouterr().err and not (v1 / L.NOM_MARQUEUR_VAGUE2).exists()
    # La reprise de la vague 1 retrouve l'orpheline (son coût est compté) ; la vague 2 peut partir.
    assert L.main(T.argv(tmp_path, "--reprendre", str(v1), "--limite", "1"), executeur=T.executeur_factice(),
                  base_env={}, extracteur=T.extracteur_ok) in (0, 4)
    assert L.lire_tentatives(v1 / "tentatives.jsonl")[1] == []
    p = T.plafond_permis_v2(tmp_path, v1, "1000")
    assert L.main(args_vague2(tmp_path, v1, p), executeur=T.executeur_factice(), base_env={},
                  extracteur=T.extracteur_ok) == 0


# ======================================================================== I : frontière erreur d'API / exception
def test_cI_workbench_exception_sans_message_arretee_sans_trace_exclue(tmp_path, monkeypatch):
    """Une exception sans message laisse `error` vide, comme une fin normale, mais aussi la réponse vide (WorkBench perd
    les actions) : arrêtée sans trace exploitable, exclue, déclarée, jamais relancée."""
    T.preparer_workbench(tmp_path, monkeypatch)

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        d = tmp_path / "wbrun" / "data" / "results" / "email"
        d.mkdir(parents=True, exist_ok=True)
        n = f"claude-opus-5-5_all_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        (d / f"{n}.csv").write_text('"task","function_calls","full_response","error"\n"q","[]","",""\n')
        T.ecrire_usage(env["PILOTE_USAGE_FILE"], [("claude-opus-5-5", "claude-opus-5-5", 1000, 10)])
        return 0

    monkeypatch.setattr(pe, "executer_enfant", faux)
    ctx, compta, reg, journal = T.contexte(tmp_path, 100.0)
    L.lancer_vague(parties_wb(1), 1, compta, ctx, journal, L.executer_partie)
    (x,) = reg.lignes
    assert (x["statut"], x["arret"], x["ok"], x["finale"], x["exclue"]) == (L.ARRETEE, L.ARRET_EXCEPTION_OUTIL, False,
                                                                            True, True)
    assert x["dossier"].startswith("ecartees/") and x["cout_usd"] > 0
    assert L.classer({"env": "WorkBench"}, {"ok": True, "terminaison": "", "trace": True}) == (L.TERMINEE, None, None)


@pytest.mark.parametrize("texte,statut", [("Data returned by API invalid for expected schema.", L.ECHEC),
                                          ("list index out of range", L.ARRETEE)])
def test_cI_frontiere_entre_erreur_d_api_et_exception_d_outil(texte, statut):
    """CV7 : l'erreur de validation du SDK OpenAI est une erreur d'API ; « list index out of range », texte générique
    qu'un outil pourrait aussi lever, reste une exception d'outil (limite déclarée, choix 28)."""
    assert L.classer({"env": "WorkBench"}, {"ok": True, "terminaison": texte, "trace": False})[0] == statut


# ======================================================================== question 3 (06/11) : coût majoré et estimation
RESERVE_Q3 = {"aviation": ["0", "1"], "commerce": ["10", "11"], "banque": ["task_001"],
              "WorkBench": [f"email:{i}" for i in range(11)]}  # Opus WorkBench : 11 parties, 2 à la vague 1


def test_q3_cout_majore_dans_la_depense_pas_dans_le_cout_moyen_estimation_de_la_vague_2_inchangee(tmp_path, monkeypatch):
    """Une partie Opus WorkBench au coût majoré (majorant : des dizaines de fois le coût réel) compte dans la dépense,
    mais ne change pas l'estimation de la vague 2 ; si toutes les tentatives d'une configuration sont majorées, elle
    reste sans mesure et la vague 2 est refusée."""
    T.neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L, "RESERVE", T.ecrire_reserve(tmp_path, RESERVE_Q3))
    pmax = L.preparer(L.analyser(["--vague", "1", "--apercu", "--reel", "--reserve", str(L.RESERVE)]))["plan"]
    plafond = str(math.floor(pmax["plafond_permis_usd"] * 100) / 100)
    assert L.main(T.argv(tmp_path, "--reel", "--concurrence", "1", plafond=plafond, accord=plafond, reserve=L.RESERVE),
                  executeur=T.executeur_factice(p=20_000, s=0, modele="claude-sonnet-5-5"), base_env={},
                  chemin_cle=T.fichier_cle(tmp_path), extracteur=T.extracteur_ok) == 0  # 0,04 $ par partie
    v1 = T.dossier_unique(tmp_path)

    def estimation_vague2():
        a = L.analyser(["--vague", "2", "--apercu", "--reel", "--vague1", str(v1), "--budget-restant-usd", "1000",
                        "--reserve", str(L.RESERVE)])
        return L.preparer(a)["plan"]["estimation_usd"]

    avant = estimation_vague2()
    cout = json.loads((v1 / "cout.json").read_text())
    wb_opus = [l for l in cout["parties"] if (l["modele"], l["env"]) == ("claude-opus-5-5", "WorkBench")]
    assert len(wb_opus) == 2
    wb_opus[0].update(cout_usd=9.74, cout_majore=True, usage="majoré")  # majorant moyen d'une partie Opus au pilote
    (v1 / "cout.json").write_text(json.dumps(cout))
    assert estimation_vague2() == pytest.approx(avant)
    assert L.couts_mesures(cout["parties"])["claude-opus-5-5"]["WorkBench"] == pytest.approx(0.04)
    plan = json.loads((v1 / "plan_de_jeu.json").read_text())
    s = L.section_cout(plan, cout["parties"], {}, None, 0.0)  # point 1 du rapport : même règle
    (c,) = [d for d in s["par_configuration"] if (d["modele"], d["env"]) == ("claude-opus-5-5", "WorkBench")]
    assert c["cout_usd"] == pytest.approx(9.74 + 0.04) and c["cout_moyen_usd"] == pytest.approx(0.04)
    assert s["depense_usd"] == pytest.approx(sum(l["cout_usd"] or 0.0 for l in cout["parties"]))
    wb_opus[1].update(cout_usd=9.74, cout_majore=True, usage="majoré")
    (v1 / "cout.json").write_text(json.dumps(cout))
    with pytest.raises(L.ErreurPilote, match="claude-opus-5-5 / WorkBench"):
        estimation_vague2()


def test_q3_montant_retenu_reste_dans_le_cout_moyen():
    """Un montant retenu par l'opérateur (--cout-retenu) porte aussi `cout_majore`, mais c'est une estimation : il
    reste dans le coût moyen."""
    lignes = [{"modele": "claude-opus-5-5", "env": "WorkBench", "partie": "p1", "cout_usd": None, "cout_majore": False},
              {"modele": "claude-opus-5-5", "env": "WorkBench", "partie": "p1", "cout_usd": 0.3, "cout_majore": True,
               "cout_retenu_pour": "p1"},
              {"modele": "claude-opus-5-5", "env": "WorkBench", "partie": "p2", "cout_usd": 0.1, "cout_majore": False}]
    assert L.couts_mesures(lignes)["claude-opus-5-5"]["WorkBench"] == pytest.approx(0.2)
