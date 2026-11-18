"""Tests de banc/lanceur.py. Aucun appel réel : fausse clé dans un fichier temporaire, exécuteur factice, extraction des
outils simulée, bancs redirigés vers des dossiers temporaires."""
import hashlib
import json
import math
import os
import random
import shutil
import threading
import time
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

import cout_v2 as cv
import lanceur as L
import pilote_etape1 as pe
import pilote_etape2 as p2
import usage_tau2
import usage_wrap

CLE = "sk-ant-FAUSSE-CLE-DE-TEST-123456"
RESERVE_TEST = {"aviation": ["1", "2", "3", "4"], "commerce": ["10", "11", "12"], "banque": ["task_001", "task_002"],
                "WorkBench": ["email:1", "calendar:2", "analytics:3"]}
MOTS_INTERDITS = ("fausse", "juste", "doublon", "refusée", "refusee", "alerte")


def fichier_cle(tmp_path):
    p = tmp_path / "anthropic.env"
    p.write_text(f"ANTHROPIC_API_KEY={CLE}\n", encoding="utf-8")
    os.chmod(p, 0o600)
    return p


def ecrire_reserve(tmp_path, reserve=None):
    f = tmp_path / "reserve.json"
    f.write_text(json.dumps(reserve or RESERVE_TEST))
    return f


def vraie_reserve():
    return L.charger_reserve(L.RESERVE)


def faux_appels(modele, p=1000, s=100, n=1, renvoye="nom"):
    r = modele if renvoye == "nom" else renvoye
    appels = [{"modele": modele, "prompt_tokens": p, "completion_tokens": s, "cache_creation_input_tokens": 0,
               "cache_read_input_tokens": 0}] * n
    return appels, [(modele, r)] * n


def executeur_factice(trace=None, p=1000, s=100, ok=True, renvoye="nom", modele=None, plus=None, fichiers=False):
    """Résultat au format de l'exécuteur ; `plus(t)` complète le résultat ; `fichiers` crée la trace dans parties/."""
    def f(t, ctx):
        if trace is not None:
            trace.append((t["id"], ctx["reel"], dict(ctx["env_enfant"])))
        m = modele or t["modele"]
        ren = renvoye(t) if callable(renvoye) else renvoye
        appels, noms = faux_appels(m, p, s, renvoye=ren)
        r = {"ok": ok, "appels": appels, "estime": False, "erreur": None if ok else "échec", "copies": [],
             "renvoyes": noms}
        if fichiers:
            d = ctx["sortie"] / "parties" / f"{L.banc_de(t['env'])}-{t['id']}"
            d.mkdir(parents=True, exist_ok=True)
            (d / "results.json").write_text("{}")
        if plus:
            r.update(plus(t) or {})
        return r
    return f


def extracteur_ok(dossier, env):
    assert "ANTHROPIC_API_KEY" not in env  # l'extraction tourne toujours sans clé
    for p in L.DOSSIER_OUTILS.glob("*.json"):
        shutil.copy(p, Path(dossier) / p.name)


def extracteur_modifie(dossier, env):
    extracteur_ok(dossier, env)
    f = Path(dossier) / "aviation.json"
    d = json.loads(f.read_text())
    d["outils"][0]["function"]["description"] = "modifiée"
    f.write_text(json.dumps(d))


def neutraliser(monkeypatch, tmp_path, actions=None):
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")
    monkeypatch.setattr(L, "WB_RUN", tmp_path / "wbrun")
    monkeypatch.setattr(L, "WORKBENCH", tmp_path / "wb")
    # La racine des sorties du test tient lieu d'experience/ (seule racine permise en réel : contre-vérification, A).
    monkeypatch.setattr(L, "SORTIE_RACINE", tmp_path / "s")
    monkeypatch.setattr(L, "verifier_taches_existent", lambda *a, **k: None)
    monkeypatch.setattr(L, "post_traitement", lambda sortie, *a, **k: list(actions or []))
    # vague réelle : conformité au gel du plan (relecture C13, P3), testée à part (test_lanceur_gel.py)
    monkeypatch.setattr(L, "verifier_gel", lambda: dict(commit="essai", etiquette=None, manifeste_gel=None))


def argv(tmp_path, *extra, vague=1, plafond="3", accord="3", graine="5", reserve=None):
    a = ["--vague", str(vague), "--reserve", str(reserve or ecrire_reserve(tmp_path)), "--sortie-racine",
         str(tmp_path / "s"), "--plafond-usd", plafond, "--accord-otsoa-usd", accord]
    if graine is not None:
        a += ["--graine", graine]
    return a + list(extra)


def dossier_unique(tmp_path, vague=1):
    (d,) = list((tmp_path / "s" / f"vague{vague}").iterdir())
    return d


def lignes_cout(d):
    return json.loads((d / "cout.json").read_text())["parties"]


def contexte(tmp_path, plafond, noms=None, reel=True, vague=1):
    sortie = tmp_path / "sortie"
    sortie.mkdir(exist_ok=True)
    compta = L.Comptable(plafond, vague)
    reg = L.Registre(sortie, {"etape": "experience"}, [], compta)
    ctx = {"sortie": sortie, "reel": reel, "env_enfant": {}, "cle": None, "horodatage": "t", "cache": True,
           "vague": vague, "verrou_wb": threading.Lock(), "registre": reg, "noms": noms or L.Noms()}
    return ctx, compta, reg, pe.Journal(sortie / "journal.log")


def premieres(n, reserve=None):
    return [(x, 1) for x in L.construire_parties(reserve or RESERVE_TEST, 1)[:n]]


# ================================================================== 1. les parties
def test_toute_la_reserve_14266_parties_avec_les_passages_de_2_3():
    reserve = vraie_reserve()
    assert {e: len(v) for e, v in reserve.items()} == {"aviation": 40, "commerce": 91, "banque": 77, "WorkBench": 552}
    parties = L.construire_parties(reserve, 123)
    assert len(parties) == 14266 and len({x["id"] for x in parties}) == 14266
    n = L.compter(parties)
    for m, d in L.PASSAGES.items():
        for e, k in d.items():
            assert n[(m, e)] == k * len(reserve[e])
    assert sum(v for (m, _), v in n.items() if m == "claude-haiku-5-5") == 10080
    assert sum(v for (m, _), v in n.items() if m == "claude-sonnet-5-5") == 2093
    par_passage = {}
    for x in parties:  # chaque passage joue toute la réserve, une fois
        assert 1 <= x["passage"] <= L.PASSAGES[x["modele"]][x["env"]]
        par_passage.setdefault((x["modele"], x["env"], x["passage"]), []).append(x["tache"])
    assert len(par_passage) == sum(k for d in L.PASSAGES.values() for k in d.values())
    for (m, e, p), taches in par_passage.items():
        assert sorted(taches) == sorted(reserve[e])


def test_passages_decides():
    assert L.PASSAGES == {"claude-haiku-5-5": {"aviation": 50, "commerce": 50, "banque": 10, "WorkBench": 5},
                          "claude-sonnet-5-5": {"aviation": 10, "commerce": 10, "banque": 3, "WorkBench": 1},
                          "claude-opus-5-5": {"aviation": 10, "commerce": 10, "banque": 3, "WorkBench": 1}}


def test_identifiant_porte_passage_et_tache():
    assert L.id_partie("WorkBench", "claude-opus-5-5", 1, "customer_relationship_manager:15") == \
        "WorkBench-opus-p01-customer_relationship_manager_15"
    assert L.id_partie("aviation", "claude-haiku-5-5", 50, "12") == "aviation-haiku-p50-12"


# ================================================================== 2. l'ordre de jeu
def test_cle_d_ordre_est_un_sha256():
    assert L.cle_ordre(7, "aviation", 1, "12") == hashlib.sha256(b"7|aviation|1|12").hexdigest()


def test_ordre_fige_par_valeurs_de_reference():
    """Valeurs calculées le 05/11 : tout changement de la clé d'ordre change l'ordre de jeu et fait échouer ce test."""
    assert L.ordre_des_taches(["a", "b", "c", "d", "e"], 42, "aviation", 1) == ["b", "c", "e", "d", "a"]
    assert L.ordre_des_taches(["a", "b", "c", "d", "e"], 42, "aviation", 2) == ["d", "e", "b", "c", "a"]


def test_ordre_reproductible_sans_le_module_random(monkeypatch):
    def interdit(*a, **k):
        raise AssertionError("random ne doit pas servir à l'ordre de jeu")

    for nom in ("sample", "shuffle", "random", "randrange", "choice"):
        monkeypatch.setattr(random, nom, interdit)
    monkeypatch.setattr(random, "Random", interdit)
    a = [x["id"] for x in L.construire_parties(RESERVE_TEST, 99)]
    b = [x["id"] for x in L.construire_parties(RESERVE_TEST, 99)]
    c = [x["id"] for x in L.construire_parties(RESERVE_TEST, 100)]
    assert a == b and a != c and sorted(a) == sorted(c)


def test_intercale_par_rang_relatif_couverture_equilibree():
    parties = L.construire_parties(RESERVE_TEST, 3)
    fr = [x["rang"] / x["n_config"] for x in parties]
    assert fr == sorted(fr)
    n = L.compter(parties)
    vus = {}
    for x in parties:  # à tout instant, chaque configuration a joué la même part de ses parties, à une partie près
        vus[(x["modele"], x["env"])] = vus.get((x["modele"], x["env"]), 0) + 1
        f = x["rang"] / x["n_config"]
        for k, total in n.items():
            assert abs(vus.get(k, 0) - f * total) <= 1 + 1e-9


def test_a_tailles_egales_c_est_l_ordre_du_pilote():
    reserve = {e: [f"{e}{i}" for i in range(3)] for e in L.ENVS}
    passages = {m: {e: 1 for e in L.ENVS} for m in L.MODELES}
    parties = L.construire_parties(reserve, 1, passages)
    cles = [(x["rang"], L.ENVS.index(x["env"]), L.MODELES.index(x["modele"])) for x in parties]
    assert cles == sorted(cles) and len(parties) == 36
    for e in L.ENVS:
        for r in range(1, 4):
            assert len({x["tache"] for x in parties if x["env"] == e and x["rang"] == r}) == 1  # mêmes tâches, 3 modèles


def test_passages_joues_l_un_apres_l_autre_dans_chaque_configuration():
    parties = L.construire_parties(RESERVE_TEST, 8)
    for m in L.MODELES:
        for e in L.ENVS:
            ps = [x["passage"] for x in parties if x["modele"] == m and x["env"] == e]
            assert ps == sorted(ps)


def test_sonnet_et_opus_jouent_les_memes_taches_au_meme_rang():
    parties = L.construire_parties(vraie_reserve(), 11)
    son = {(x["env"], x["rang"]): x["tache"] for x in parties if x["modele"] == "claude-sonnet-5-5"}
    opu = {(x["env"], x["rang"]): x["tache"] for x in parties if x["modele"] == "claude-opus-5-5"}
    assert son == opu


# ================================================================== 3. les vagues
def test_vague1_premiers_10_pour_cent_de_chaque_configuration():
    parties = L.construire_parties(vraie_reserve(), 4)
    v1 = L.parties_vague1(parties)
    n, n1 = L.compter(parties), L.compter(v1)
    for k, total in n.items():
        assert n1[k] == math.ceil(total / 10)
    assert len(v1) == 1430 and len(parties) - len(v1) == 12836
    pos = {x["id"]: i for i, x in enumerate(parties)}
    assert [pos[x["id"]] for x in v1] == sorted(pos[x["id"]] for x in v1)  # dans l'ordre de jeu


def test_estimation_de_2_3_et_de_la_vague_1():
    parties = L.construire_parties(vraie_reserve(), 4)
    assert round(L.estimation(parties, L.COUT_PILOTE), 2) == 595.73
    d = {(x["modele"], x["env"]): x["estimation_usd"] for x in L.detail_estimation(parties, L.COUT_PILOTE)}
    assert round(d[("claude-haiku-5-5", "aviation")], 2) == 9.77 and round(d[("claude-opus-5-5", "banque")], 2) == 108.82
    e1 = L.estimation(L.parties_vague1(parties), L.COUT_PILOTE)
    assert 59 < e1 < 62  # « environ 60 $ » (Q10)


def test_couts_du_pilote_recoupes_avec_son_cout_json():
    chemin = L.RACINE / "pilote" / "etape2" / "2026-11-05_07-50-58" / "cout.json"
    if not chemin.is_file():
        pytest.skip("sortie du pilote absente")
    somme, nb = {}, {}
    for x in json.loads(chemin.read_text())["parties"]:
        k = (x["modele"], x["env"])
        somme[k] = somme.get(k, 0) + x["cout_usd"]
        nb[k] = nb.get(k, 0) + 1
    for (m, e), s in somme.items():
        assert nb[(m, e)] == 10 and L.COUT_PILOTE[m][e] == pytest.approx(s / 10, abs=1e-12)


# ================================================================== 4. les plafonds
def test_plafond_vague_1_au_plus_1_5_fois_l_estimation():
    assert L.verifier_plafond(1, 90.0, 95.0, 60.0) == pytest.approx(90.0)
    with pytest.raises(pe.ErreurPilote, match="au plus 90.00"):
        L.verifier_plafond(1, 90.01, 95.0, 60.0)
    with pytest.raises(pe.ErreurPilote, match="accordé par Otsoa"):
        L.verifier_plafond(1, 60.0, 50.0, 60.0)
    for mauvais in (0.0, -1.0, float("nan"), float("inf")):
        with pytest.raises(pe.ErreurPilote):
            L.verifier_plafond(1, mauvais, 95.0, 60.0)
    with pytest.raises(pe.ErreurPilote, match="accord-otsoa"):
        L.verifier_plafond(1, 60.0, None, 60.0)


def test_plafond_vague_2_au_plus_1_25_fois_l_estimation_et_le_budget_restant():
    assert L.verifier_plafond(2, 125.0, 200.0, 100.0, budget_restant=500.0) == pytest.approx(125.0)
    with pytest.raises(pe.ErreurPilote):
        L.verifier_plafond(2, 125.01, 200.0, 100.0, budget_restant=500.0)
    assert L.verifier_plafond(2, 110.0, 200.0, 100.0, budget_restant=110.0) == pytest.approx(110.0)
    with pytest.raises(pe.ErreurPilote, match="budget restant"):
        L.verifier_plafond(2, 111.0, 200.0, 100.0, budget_restant=110.0)
    with pytest.raises(pe.ErreurPilote, match="budget-restant"):
        L.verifier_plafond(2, 100.0, 200.0, 100.0)


def test_accord_d_otsoa_obligatoire_rien_n_est_cree(tmp_path, monkeypatch, capsys):
    neutraliser(monkeypatch, tmp_path)
    a = argv(tmp_path)
    i = a.index("--accord-otsoa-usd")
    del a[i:i + 2]
    trace = []
    rc = L.main(a, executeur=executeur_factice(trace), base_env={}, extracteur=extracteur_ok)
    assert rc == 2 and not trace and not (tmp_path / "s").exists() and "accord-otsoa" in capsys.readouterr().err


def test_plafond_au_dela_de_l_accord_ou_de_la_regle_refuse(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    trace = []
    assert L.main(argv(tmp_path, plafond="3", accord="2"), executeur=executeur_factice(trace), base_env={},
                  extracteur=extracteur_ok) == 2
    assert L.main(argv(tmp_path, plafond="3.8", accord="10"), executeur=executeur_factice(trace), base_env={},
                  extracteur=extracteur_ok) == 2  # 1,5 x 2,51 = 3,765
    assert not trace and not (tmp_path / "s").exists()


def test_apercu_ne_lance_ni_n_ecrit_rien(tmp_path, monkeypatch, capsys):
    neutraliser(monkeypatch, tmp_path)
    rc = L.main(["--vague", "1", "--apercu", "--reserve", str(ecrire_reserve(tmp_path)), "--sortie-racine",
                 str(tmp_path / "s")], executeur=executeur_factice([]), extracteur=extracteur_ok)
    out = capsys.readouterr().out
    assert rc == 0 and not (tmp_path / "s").exists() and "Plafond permis : 3.76" in out and "57" in out


# ================================================================== arrêt à 80 % sur des coûts simulés
def opus_cher(t, ctx):
    appels, noms = faux_appels("claude-opus-5-5", 1_000_000, 0)  # 4 $ par partie
    return {"ok": True, "appels": appels, "estime": False, "erreur": None, "copies": [], "renvoyes": noms}


def test_arret_a_80_pour_cent_avant_toute_nouvelle_partie(tmp_path):
    ctx, compta, reg, journal = contexte(tmp_path, 10.0)  # seuil 8 $ : deux parties
    L.lancer_vague(premieres(12), 1, compta, ctx, journal, opus_cher)
    assert len(reg.lignes) == 2 and compta.cumul == pytest.approx(8.0) and "80 %" in compta.arret
    assert "ARRÊT" in (ctx["sortie"] / "journal.log").read_text()


def test_arret_a_80_pour_cent_avec_trois_parties_a_la_fois(tmp_path):
    ctx, compta, reg, journal = contexte(tmp_path, 10.0)
    L.lancer_vague(premieres(12), 3, compta, ctx, journal, opus_cher)
    assert 2 <= len(reg.lignes) <= 4 and compta.doit_arreter()


def test_arret_a_80_pour_cent_en_bout_de_chaine(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    rc = L.main(argv(tmp_path, "--concurrence", "1", plafond="3", accord="3"),
                executeur=executeur_factice(p=200_000, s=0, modele="claude-sonnet-5-5"),
                base_env={}, extracteur=extracteur_ok)  # 0,40 $ par partie, arrêt à 2,40 $ ; une partie à la fois
    d = dossier_unique(tmp_path)
    cout = json.loads((d / "cout.json").read_text())
    assert rc == 4 and len(cout["parties"]) == 6 and "80 %" in cout["arret"] and cout["cumul_usd"] == pytest.approx(2.4)
    rapport = json.loads((d / "rapport_vague.json").read_text())
    assert rapport["2_deroulement"]["total"]["non_jouees"] == 57 - 6


# ================================================================== vague 2 : 95 % et réserve de 15 $ (Otsoa, 06/11)
def test_seuil_d_arret_de_la_vague_2_avec_la_reserve_de_15_dollars():
    assert L.seuil_arret(1, 100.0)[0] == pytest.approx(80.0)  # la vague 1 reste à 80 %
    assert L.seuil_arret(2, 100.0)[0] == pytest.approx(85.0)  # petit plafond : la réserve de 15 $ l'emporte
    assert L.seuil_arret(2, 600.0)[0] == pytest.approx(570.0)  # grand plafond : 95 % l'emporte
    assert L.seuil_arret(2, 300.0)[0] == pytest.approx(285.0)  # les deux règles se rejoignent à 300 $
    assert L.verifier_plafond(2, 100.0, 100.0, 80.0, budget_restant=500.0) == pytest.approx(100.0)
    with pytest.raises(pe.ErreurPilote, match="seuil d'arrêt"):  # plafond de 15 $ ou moins : rien ne serait joué
        L.verifier_plafond(2, 15.0, 20.0, 100.0, budget_restant=500.0)


def cout_fixe(p_opus):
    def f(t, ctx):
        appels, noms = faux_appels("claude-opus-5-5", p_opus, 0)
        return {"ok": True, "appels": appels, "estime": False, "erreur": None, "copies": [], "renvoyes": noms}
    return f


@pytest.mark.parametrize("plafond,jetons,parties,seuil", [
    (100.0, 2_500_000, 9, 85.0),  # 10 $ par partie : 80 $ < 85 $, la 9e atteint le seuil
    (600.0, 25_000_000, 6, 570.0),  # 100 $ par partie : 500 $ < 570 $, la 6e atteint le seuil
])
def test_arret_de_la_vague_2_au_seuil_sur_des_couts_simules(tmp_path, plafond, jetons, parties, seuil):
    ctx, compta, reg, journal = contexte(tmp_path, plafond, vague=2)
    assert compta.seuil == pytest.approx(seuil)
    L.lancer_vague(premieres(20), 1, compta, ctx, journal, cout_fixe(jetons))
    assert len(reg.lignes) == parties and "seuil d'arrêt" in compta.arret and compta.cumul <= plafond + 1e-9


# ================================================================== 5. réduction des passages (règle C9)
TACHES = {"aviation": 40, "commerce": 91, "banque": 77, "WorkBench": 552}


def test_reduction_inutile_si_le_total_tient():
    c, red, total = L.facteur_reduction(L.PASSAGES, L.COUT_PILOTE, TACHES, {}, 1000.0)
    assert c == 100 and red == L.PASSAGES and round(total, 2) == 595.73


def test_reduction_plus_grand_facteur_au_centieme():
    budget = 500.0
    c, red, total = L.facteur_reduction(L.PASSAGES, L.COUT_PILOTE, TACHES, {}, budget)
    assert 1.25 * total <= budget and c < 100
    suivant = L.passages_reduits(L.PASSAGES, c + 1)
    total_suivant = sum(k * L.COUT_PILOTE[m][e] for (m, e), k in L.parties_restantes(suivant, TACHES).items())
    assert 1.25 * total_suivant > budget
    assert red == L.passages_reduits(L.PASSAGES, c)


def test_reduction_fait_tenir_le_plafond_entier_dans_le_budget():
    """Cible décidée par Otsoa (QCM, 06/11) : 1,25 x total réduit <= budget restant. À 700 $, le total entier (595,73 $)
    tiendrait dans le budget, mais pas 1,25 fois ce total (744,67 $) : les passages sont réduits."""
    c, red, total = L.facteur_reduction(L.PASSAGES, L.COUT_PILOTE, TACHES, {}, 700.0)
    assert c < 100 and 1.25 * total <= 700.0 and total < 595.73
    assert L.facteur_reduction(L.PASSAGES, L.COUT_PILOTE, TACHES, {}, 700.0, marge=1.0)[0] == 100  # l'ancienne lecture
    c, red, total = L.facteur_reduction(L.PASSAGES, L.COUT_PILOTE, TACHES, {}, 745.0)
    assert c == 100 and 1.25 * total <= 745.0
    plafond = L.plafond_permis(2, total, 745.0)
    assert plafond == pytest.approx(1.25 * total)  # le budget ne borne plus le plafond
    assert L.seuil_arret(2, plafond)[0] >= 1.18 * total  # environ 19 % de marge au-dessus de l'estimation


def test_reduction_arrondit_a_l_inferieur_sans_erreur_de_virgule():
    assert L.passages_reduits({"m": {"e": 10}}, 70) == {"m": {"e": 7}}  # 0,7 x 10 = 6,999… en flottant
    assert L.passages_reduits({"m": {"e": 50}}, 83) == {"m": {"e": 41}}
    assert L.passages_reduits({"m": {"e": 3}}, 50) == {"m": {"e": 1}}
    assert L.passages_reduits({"m": {"e": 10}}, 29) == {"m": {"e": 2}}


def test_reduction_garde_au_moins_un_passage_et_toutes_les_taches():
    red = L.passages_reduits(L.PASSAGES, 1)
    assert all(n == 1 for d in red.values() for n in d.values())
    red = L.passages_reduits(L.PASSAGES, 50)
    assert red["claude-sonnet-5-5"]["WorkBench"] == 1 and red["claude-opus-5-5"]["WorkBench"] == 1
    assert red["claude-sonnet-5-5"]["banque"] == 1 and red["claude-haiku-5-5"]["aviation"] == 25
    parties = L.construire_parties(vraie_reserve(), 2, red)
    for m in L.MODELES:  # aucune tâche retirée
        for e in L.ENVS:
            assert {x["tache"] for x in parties if x["modele"] == m and x["env"] == e} == set(vraie_reserve()[e])


def test_reduction_meme_facteur_partout():
    for c in (99, 77, 50, 33, 10, 3):
        red = L.passages_reduits(L.PASSAGES, c)
        for m, d in L.PASSAGES.items():
            for e, n in d.items():
                assert red[m][e] == max(1, (c * n) // 100)


def test_reduction_impossible_refusee():
    with pytest.raises(pe.ErreurPilote, match="impossible"):
        L.facteur_reduction(L.PASSAGES, L.COUT_PILOTE, TACHES, {}, 1.0)


def test_reduction_compte_les_parties_deja_jouees():
    passages = {"m": {"e": 10}}
    couts, taches = {"m": {"e": 1.0}}, {"e": 10}
    assert L.parties_restantes(passages, taches, {("m", "e"): {1: 10, 2: 10}}) == {("m", "e"): 80}
    assert L.parties_restantes({"m": {"e": 1}}, taches, {("m", "e"): {1: 10, 2: 10}}) == {("m", "e"): 0}
    c, red, total = L.facteur_reduction(passages, couts, taches, {("m", "e"): {1: 10, 2: 10}}, 30.0)
    assert (c, red, total) == (49, {"m": {"e": 4}}, 20.0)  # 1,25 x 20 <= 30 ; à 50 centièmes, 1,25 x 30 > 30


def test_reduction_entrees_invalides():
    for c in (0, 101, 1.5, True):
        with pytest.raises(ValueError):
            L.passages_reduits(L.PASSAGES, c)


# ================================================================== 6. nom de modèle renvoyé par l'API
def test_capture_du_nom_renvoye_par_les_deux_enveloppes(tmp_path, monkeypatch):
    rep = NS(model="claude-haiku-5-5-20261001", usage=NS(prompt_tokens=10, completion_tokens=2))
    assert usage_tau2.ligne_usage("claude-haiku-5-5", rep)["modele_renvoye"] == "claude-haiku-5-5-20261001"
    assert usage_wrap.ligne_usage("claude-haiku-5-5", rep)["modele_renvoye"] == "claude-haiku-5-5-20261001"
    assert usage_tau2.ligne_usage("m", NS(usage=None))["modele_renvoye"] is None
    assert usage_wrap.ligne_usage("m", NS(model="", usage=None))["modele_renvoye"] is None
    f = tmp_path / "u.jsonl"
    monkeypatch.setenv("PILOTE_USAGE_FILE", str(f))
    usage_tau2.callback_succes({"model": "claude-opus-5-5"}, rep)
    appels, noms = L.lire_usage(f)
    assert noms == [("claude-opus-5-5", "claude-haiku-5-5-20261001")] and appels[0]["prompt_tokens"] == 10
    assert cv.lire_usage_jsonl(f)[0]["modele"] == "claude-opus-5-5"  # le format reste lisible par cout_v2


def test_noms_reference_premiere_observation_puis_changement():
    n = L.Noms()
    assert n.examiner("a", [("anthropic/claude-haiku-5-5", "H1"), ("claude-opus-5-5", "O1")], "tau2") == ([], 0)
    assert n.reference == {"tau2:claude-haiku-5-5": "H1", "tau2:claude-opus-5-5": "O1"}
    ch, absents = n.examiner("b", [("claude-haiku-5-5", "H1"), ("claude-haiku-5-5", "H2"), ("claude-opus-5-5", None)],
                             "tau2")
    assert ch == [{"tentative": "b", "modele": "tau2:claude-haiku-5-5", "attendu": "H1", "recu": "H2"}] and absents == 1
    assert n.reference["tau2:claude-haiku-5-5"] == "H1" and n.observes["tau2:claude-haiku-5-5"] == {"H1": 2, "H2": 1}


def test_nom_change_arret_et_partie_marquee_et_exclue(tmp_path):
    ctx, compta, reg, journal = contexte(tmp_path, 100.0)
    vus = []

    def renvoye(t):
        vus.append(t["id"])
        return "NOUVEAU" if len(vus) == 3 else "ANCIEN"

    L.lancer_vague(premieres(10), 1, compta, ctx, journal,
                   executeur_factice(renvoye=renvoye, modele="claude-haiku-5-5", fichiers=True))
    assert len(reg.lignes) == 3 and "nom de modèle" in compta.arret
    x = reg.lignes[2]
    assert x["statut"] == L.EXCLUE_NOM and x["ok"] is False and x["exclue"] and not x["finale"]  # rejouée à la reprise
    assert x["motif_exclusion"] == L.MOTIF_NOM_REJOUEE
    assert x["modeles_renvoyes"] == ["NOUVEAU"] and x["dossier"].startswith("ecartees/")
    assert not (ctx["sortie"] / "parties" / f"tau2-{x['id']}").exists()
    assert all(l["ok"] and l["dossier"].startswith("parties/") for l in reg.lignes[:2])
    noms = json.loads((ctx["sortie"] / "modeles_renvoyes.json").read_text())
    assert noms["reference"] == {"tau2:claude-haiku-5-5": "ANCIEN"} and noms["changements"][0]["recu"] == "NOUVEAU"


def test_nom_de_la_vague_1_fait_reference(tmp_path):
    ctx, compta, reg, journal = contexte(tmp_path, 100.0, noms=L.Noms({"tau2:claude-haiku-5-5": "V1"}, "vague 1"))
    L.lancer_vague(premieres(5), 1, compta, ctx, journal, executeur_factice(renvoye="V2", modele="claude-haiku-5-5"))
    assert len(reg.lignes) == 1 and reg.lignes[0]["statut"] == L.EXCLUE_NOM and compta.arret


def test_nom_absent_est_un_echec_technique(tmp_path):
    ctx, compta, reg, journal = contexte(tmp_path, 100.0)
    L.lancer_vague(premieres(1), 1, compta, ctx, journal, executeur_factice(renvoye=None))
    assert [l["statut"] for l in reg.lignes] == [L.ECHEC, L.ECHEC] and reg.lignes[1]["exclue"]


# ================================================================== 7. définitions d'outils
def test_outils_identiques_acceptes():
    e = L.verifier_outils_agent({}, extracteur_ok)
    assert set(e) == {"aviation", "commerce", "banque", "workbench"}


def test_outils_modifies_refuses():
    with pytest.raises(pe.ErreurPilote, match="aviation.json : empreinte"):
        L.verifier_outils_agent({}, extracteur_modifie)


def test_comparer_outils_commit_et_fichier_manquant(tmp_path):
    extracteur_ok(tmp_path, {})
    (tmp_path / "banque.json").unlink()
    d = json.loads((tmp_path / "commerce.json").read_text())
    d["commit"] = "0000000"
    (tmp_path / "commerce.json").write_text(json.dumps(d))
    ecarts = L.comparer_outils(L.DOSSIER_OUTILS, tmp_path)
    assert any("banque.json : absent" in x for x in ecarts) and any("commerce.json : commit" in x for x in ecarts)


def test_outils_modifies_rien_n_est_lance(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    trace = []
    assert L.main(argv(tmp_path), executeur=executeur_factice(trace), base_env={}, extracteur=extracteur_modifie) == 2
    assert not trace and not (tmp_path / "s").exists()


def test_extraction_relancee_dans_chaque_banc_sans_cle(tmp_path, monkeypatch):
    vus = []

    def faux_run(cmd, cwd, env, **k):
        vus.append((cmd, cwd, env))
        return NS(returncode=0, stderr="", stdout="")

    monkeypatch.setattr(L.subprocess, "run", faux_run)
    L.extraire_outils(tmp_path, pe.env_enfant({"ANTHROPIC_API_KEY": "x", "PATH": "/b"}, None))
    assert [cmd[cmd.index("--banc") + 1] for cmd, _, _ in vus] == ["tau2", "workbench"]
    assert all(cmd[cmd.index("--dossier") + 1] == str(tmp_path) and "ANTHROPIC_API_KEY" not in env
               for cmd, _, env in vus)
    assert [Path(cwd) for _, cwd, _ in vus] == [L.TAU2, L.WORKBENCH]


# ================================================================== 8. fins anormales
@pytest.mark.parametrize("env,r,attendu", [
    ("aviation", {"ok": False, "delai_depasse": True}, (L.ARRETEE, L.ARRET_30_MIN)),
    ("aviation", {"ok": True, "terminaison": "max_steps", "pas": 100}, (L.ARRETEE, "100 tours")),
    ("aviation", {"ok": True, "terminaison": "timeout"}, (L.ARRETEE, L.ARRET_30_MIN)),
    ("commerce", {"ok": True, "terminaison": "context_window_exceeded"}, (L.ARRETEE, L.ARRET_CONTEXTE)),
    ("banque", {"ok": True, "terminaison": "infrastructure_error"}, (L.ECHEC, None)),
    ("banque", {"ok": True, "terminaison": "unexpected_error"}, (L.ECHEC, None)),
    ("banque", {"ok": True, "terminaison": "too_many_errors"}, (L.TERMINEE, None)),
    ("aviation", {"ok": True, "terminaison": "user_stop"}, (L.TERMINEE, None)),
    ("aviation", {"ok": False, "erreur": "tau2 : code de retour 1"}, (L.ECHEC, None)),
    ("WorkBench", {"ok": True, "terminaison": ""}, (L.TERMINEE, None)),
    ("WorkBench", {"ok": True, "terminaison": L.WB_MESSAGE_ARRET}, (L.ARRETEE, L.ARRET_WORKBENCH)),
    ("WorkBench", {"ok": True, "terminaison": L.WB_MESSAGE_CONTEXTE}, (L.ARRETEE, L.ARRET_CONTEXTE)),
    ("WorkBench", {"ok": True, "terminaison": "Error code: 529 overloaded"}, (L.ECHEC, None)),
])
def test_classement_des_fins(env, r, attendu):
    statut, arret, _ = L.classer({"env": env}, r)
    assert (statut, arret) == attendu


def test_partie_arretee_par_les_30_minutes_n_est_pas_relancee(tmp_path):
    ctx, compta, reg, journal = contexte(tmp_path, 100.0)
    sans_trace = executeur_factice(ok=False, plus=lambda t: {"delai_depasse": True, "trace": False})
    L.lancer_vague(premieres(1), 1, compta, ctx, journal, sans_trace)
    (x,) = reg.lignes
    assert x["statut"] == L.ARRETEE and x["arret"] == "30 minutes" and x["finale"] and x["tentative"] == 1
    assert x["motif_exclusion"] == "arrêtée sans trace exploitable" and x["cout_usd"] > 0
    (tmp_path / "b").mkdir()
    ctx, compta, reg, journal = contexte(tmp_path / "b", 100.0)
    avec_trace = executeur_factice(fichiers=True, plus=lambda t: {"terminaison": "timeout", "trace": True})
    L.lancer_vague(premieres(1), 1, compta, ctx, journal, avec_trace)
    (x,) = reg.lignes
    assert x["statut"] == L.ARRETEE and x["ok"] and not x["exclue"] and x["dossier"].startswith("parties/")


def test_partie_arretee_par_les_100_tours_gardee(tmp_path):
    ctx, compta, reg, journal = contexte(tmp_path, 100.0)
    L.lancer_vague(premieres(1), 1, compta, ctx, journal,
                   executeur_factice(fichiers=True, plus=lambda t: {"terminaison": "max_steps", "pas": 100}))
    (x,) = reg.lignes
    assert (x["statut"], x["arret"], x["ok"], x["exclue"]) == (L.ARRETEE, "100 tours", True, False)


def test_echec_technique_relance_une_fois_puis_exclu_et_declare(tmp_path):
    ctx, compta, reg, journal = contexte(tmp_path, 100.0)
    L.lancer_vague(premieres(1), 1, compta, ctx, journal, executeur_factice(ok=False, fichiers=True))
    a, b = reg.lignes
    assert (a["id"], a["tentative"], a["finale"], a["exclue"]) == (a["partie"], 1, False, False)
    assert (b["id"], b["tentative"], b["finale"], b["exclue"]) == (a["partie"] + "-t2", 2, True, True)
    assert b["motif_exclusion"] == "échec technique (deux tentatives)"
    assert a["dossier"].startswith("ecartees/") and b["dossier"].startswith("ecartees/")
    assert not any((ctx["sortie"] / "parties").iterdir())  # parties/ ne garde que les tentatives gardées
    assert compta.cumul == pytest.approx(2 * 0.00015)  # le coût des échecs est compté


def test_echec_puis_reussite_a_la_seconde_tentative(tmp_path):
    ctx, compta, reg, journal = contexte(tmp_path, 100.0)
    ex = executeur_factice(fichiers=True, plus=lambda t: {"ok": t["tentative"] == 2,
                                                           "erreur": None if t["tentative"] == 2 else "échec"})
    L.lancer_vague(premieres(2), 1, compta, ctx, journal, ex)
    assert [(l["id"].endswith("-t2"), l["statut"], l["ok"]) for l in reg.lignes] == [
        (False, L.ECHEC, False), (True, L.TERMINEE, True), (False, L.ECHEC, False), (True, L.TERMINEE, True)]
    assert compta.arret is None  # la série est remise à zéro par chaque réussite


def test_echecs_en_serie_arretent_le_lanceur(tmp_path):
    ctx, compta, reg, journal = contexte(tmp_path, 100.0)
    L.lancer_vague(premieres(10), 1, compta, ctx, journal, executeur_factice(ok=False))
    assert len(reg.lignes) == L.SERIE_ECHECS_MAX and "de suite" in compta.arret


def test_cout_majore_ou_inconnu_arrete(tmp_path):
    ctx, compta, reg, journal = contexte(tmp_path, 100.0)
    L.lancer_vague(premieres(3), 1, compta, ctx, journal,
                   executeur_factice(ok=False, plus=lambda t: {"cout_majore": 0.5}))
    assert len(reg.lignes) == 1 and compta.cumul == pytest.approx(0.5) and "majoré" in compta.arret
    assert reg.lignes[0]["cout_majore"] is True and reg.lignes[0]["cout_usd"] == pytest.approx(0.5)
    (tmp_path / "b").mkdir()
    ctx, compta, reg, journal = contexte(tmp_path / "b", 100.0)
    L.lancer_vague(premieres(3), 1, compta, ctx, journal,
                   executeur_factice(ok=False, plus=lambda t: {"appels": None, "cout_inconnu": True}))
    assert len(reg.lignes) == 1 and "non compté" in compta.arret


def test_modele_inconnu_dans_l_usage_arrete(tmp_path):
    ctx, compta, reg, journal = contexte(tmp_path, 100.0)
    L.lancer_vague(premieres(3), 1, compta, ctx, journal, executeur_factice(modele="gpt-9"))
    assert len(reg.lignes) == 1 and reg.lignes[0]["statut"] == L.ECHEC and "non compté" in compta.arret


def test_partie_coupee_par_ctrl_c_ne_consomme_pas_sa_relance(tmp_path):
    ctx, compta, reg, journal = contexte(tmp_path, 100.0)

    def coupee(t, c):
        (c["sortie"] / "parties" / f"tau2-{t['id']}").mkdir(parents=True)
        (c["sortie"] / "usage").mkdir(exist_ok=True)
        ecrire_usage(c["sortie"] / "usage" / f"{t['id']}.jsonl", [("claude-haiku-5-5", "claude-haiku-5-5", 1000, 100)])
        appels, noms = faux_appels("claude-haiku-5-5")
        return {"ok": False, "appels": appels, "erreur": "tau2 : code de retour -2", "copies": [], "renvoyes": noms,
                "code": -2}

    parties = premieres(2)
    L.lancer_vague(parties, 1, compta, ctx, journal, coupee)
    assert [l["statut"] for l in reg.lignes] == [L.INTERROMPUE, L.INTERROMPUE] and compta.arret is None
    x = reg.lignes[0]
    assert x["id"] == f"{x['partie']}-interrompue-t" and not x["finale"] and not x["exclue"] and x["tentative"] == 1
    assert not (ctx["sortie"] / "usage" / f"{x['partie']}.jsonl").exists()  # l'usage compté ne s'ajoutera pas au suivant
    assert (ctx["sortie"] / x["dossier"] / "usage.jsonl").is_file() and (ctx["sortie"] / x["dossier"] / "partie").is_dir()
    assert compta.cumul == pytest.approx(2 * 0.00015)
    assert [(p["id"], k) for p, k in L.file_d_attente([p for p, _ in parties], reg.lignes)] == \
        [(p["id"], 1) for p, _ in parties]
    lignes, orphelines = L.lire_tentatives(ctx["sortie"] / "tentatives.jsonl")
    assert len(lignes) == 2 and not orphelines


def test_erreur_interne_du_lanceur_arrete_et_laisse_la_tentative_a_reprendre(tmp_path, monkeypatch):
    ctx, compta, reg, journal = contexte(tmp_path, 100.0)

    def panne(*a, **k):
        raise OSError("disque plein")

    monkeypatch.setattr(L, "ranger", panne)
    L.lancer_vague(premieres(3), 1, compta, ctx, journal, executeur_factice())
    assert "erreur interne" in compta.arret and not reg.lignes
    lignes, orphelines = L.lire_tentatives(ctx["sortie"] / "tentatives.jsonl")
    assert not lignes and [o["id"] for o in orphelines] == [premieres(1)[0][0]["id"]]


def test_exception_de_l_executeur_sans_fuite_de_cle(tmp_path):
    ctx, compta, reg, journal = contexte(tmp_path, 100.0)

    def boum(t, c):
        raise RuntimeError("secret " + CLE)

    L.lancer_vague(premieres(1), 1, compta, ctx, journal, boum)
    # revue « ultra » du 06/11, constat 2 : une exception de l'exécuteur arrête le lanceur (plus de relance silencieuse)
    assert [l["statut"] for l in reg.lignes] == [L.ECHEC] and compta.arret and CLE not in compta.arret
    assert CLE not in (ctx["sortie"] / "tentatives.jsonl").read_text() and CLE not in json.dumps(reg.lignes)


# ================================================================== commandes et exécution d'une tentative (sans appel)
def test_commande_tau2_du_pilote_avec_le_delai_tenu_par_tau2():
    t = {"id": "x", "env": "banque", "modele": "claude-opus-5-5", "tache": "task_001"}
    cmd = L.commande_tau2(t, "nom", reel=True)
    assert cmd[cmd.index("--timeout") + 1] == "1800" and cmd[cmd.index("--max-steps") + 1] == "100"
    assert json.loads(cmd[cmd.index("--agent-llm-args") + 1]) == {"cache_control_injection_points": p2.points_injection()}
    assert cmd[cmd.index("--retrieval-config") + 1] == "bm25_grep" and cmd[cmd.index("--agent-llm") + 1].endswith("opus-5-5")
    assert cmd[:-4] == p2.commande_tau2(t, "nom", True, True) and "sk-ant" not in " ".join(cmd)
    assert cmd[-2:] == ["--max-retries", "0"]  # τ-bench ne se relance plus lui-même (revue du 06/11, constat 6)


def resultats_tau2(chemin, termination="user_stop", sims=1):
    msgs = [{"role": "assistant", "content": "bonjour", "usage": None},
            {"role": "user", "content": "x", "usage": {"prompt_tokens": 100, "completion_tokens": 5}},
            {"role": "assistant", "content": "y", "usage": {"prompt_tokens": 200, "completion_tokens": 6}}]
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps({"simulations": [{"id": "s1", "task_id": "1", "termination_reason": termination,
                                                   "messages": msgs}] * sims}))


def ecrire_usage(chemin, lignes):
    with open(chemin, "a") as fh:
        for m, r, p, s in lignes:
            fh.write(json.dumps({"modele": m, "modele_renvoye": r, "prompt_tokens": p, "completion_tokens": s,
                                 "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}) + "\n")


def ctx_execution(tmp_path, reel=True):
    sortie = tmp_path / "sortie"
    sortie.mkdir(exist_ok=True)
    return {"sortie": sortie, "reel": reel, "env_enfant": {"PATH": "/b"}, "cle": None, "horodatage": "h", "vague": 1,
            "verrou_wb": threading.Lock()}


def test_executer_tau2_trace_terminaison_noms_et_croisement(tmp_path, monkeypatch):
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        nom = cmd[cmd.index("--save-to") + 1]
        assert nom.startswith("experience-vague1-h-") and delai == L.DELAI_PARTIE_S + L.MARGE_DELAI_S
        resultats_tau2(tmp_path / "tau2" / "data" / "simulations" / nom / "results.json", "max_steps")
        ecrire_usage(env["PILOTE_USAGE_FILE"], [("claude-haiku-5-5", "H", 100, 5), ("claude-opus-5-5", "O", 200, 6)])
        Path(log).write_text("ok")
        return 0

    monkeypatch.setattr(pe, "executer_enfant", faux)
    t = {"id": "aviation-opus-p01-1", "env": "aviation", "modele": "claude-opus-5-5", "tache": "1"}
    r = L.executer_partie(t, ctx_execution(tmp_path))
    assert r["ok"] and r["trace"] and r["terminaison"] == "max_steps" and r["usage"] == "complet" and r["pas"] == 100
    assert r["renvoyes"] == [("claude-haiku-5-5", "H"), ("claude-opus-5-5", "O")]
    assert L.classer(t, r) == (L.ARRETEE, "100 tours", None)


def test_executer_tau2_delai_depasse_cout_compte_sans_trace(tmp_path, monkeypatch):
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        nom = cmd[cmd.index("--save-to") + 1]
        resultats_tau2(tmp_path / "tau2" / "data" / "simulations" / nom / "results.json", sims=0)
        ecrire_usage(env["PILOTE_USAGE_FILE"], [("claude-opus-5-5", "O", 5000, 50)])
        return -1

    monkeypatch.setattr(pe, "executer_enfant", faux)
    t = {"id": "aviation-opus-p01-2", "env": "aviation", "modele": "claude-opus-5-5", "tache": "2"}
    r = L.executer_partie(t, ctx_execution(tmp_path))
    assert r["delai_depasse"] and not r["trace"] and r["appels"] and r["usage"] == "complet" and not r["ok"]
    assert L.classer(t, r)[:2] == (L.ARRETEE, L.ARRET_30_MIN)


def test_executer_tau2_usage_incomplet_majore(tmp_path, monkeypatch):
    monkeypatch.setattr(L, "TAU2", tmp_path / "tau2")

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        nom = cmd[cmd.index("--save-to") + 1]
        resultats_tau2(tmp_path / "tau2" / "data" / "simulations" / nom / "results.json")
        ecrire_usage(env["PILOTE_USAGE_FILE"], [("claude-haiku-5-5", "H", 100, 5)])  # une ligne sur deux
        return 0

    monkeypatch.setattr(pe, "executer_enfant", faux)
    t = {"id": "aviation-opus-p01-3", "env": "aviation", "modele": "claude-opus-5-5", "tache": "3"}
    r = L.executer_partie(t, ctx_execution(tmp_path))
    assert not r["ok"] and r["usage"] == "incomplet" and r["cout_majore"] == pytest.approx(
        (300 * 4.0 * 1.25 + 11 * 20.0) / 1e6)


def preparer_workbench(tmp_path, monkeypatch):
    monkeypatch.setattr(L, "WB_RUN", tmp_path / "wbrun")
    monkeypatch.setattr(L, "WORKBENCH", tmp_path / "wb")
    src = tmp_path / "wb" / "data" / "processed" / "tasks_and_outcomes"
    src.mkdir(parents=True)
    (src / "email_tasks_and_outcomes.csv").write_text('"query","answer"\n"q0","[]"\n"q1","[]"\n')


def faux_workbench(tmp_path, nom=None, erreur=""):
    """Comme WorkBench : prédictions nommées à la seconde du lancement (ou `nom`), plus une ligne d'usage."""
    debuts = []

    def faux(cmd, env, cwd, log, cle=None, delai=0):
        debuts.append(time.time())
        d = tmp_path / "wbrun" / "data" / "results" / "email"
        d.mkdir(parents=True, exist_ok=True)
        n = nom or f"claude-haiku-5-5_all_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        (d / f"{n}.csv").write_text(f'"task","function_calls","full_response","error"\n"q1","[]","fait","{erreur}"\n')
        (d / f"{n}_meta.json").write_text("{}")
        ecrire_usage(env["PILOTE_USAGE_FILE"], [("claude-haiku-5-5", "claude-haiku-5-5", 10, 2)])
        return 0

    return faux, debuts


T_WB = {"id": "WorkBench-haiku-p01-email_1", "env": "WorkBench", "modele": "claude-haiku-5-5", "tache": "email:1"}


def test_executer_workbench_trace_et_erreur_du_banc(tmp_path, monkeypatch):
    preparer_workbench(tmp_path, monkeypatch)
    faux, _ = faux_workbench(tmp_path, nom="claude-haiku-5-5_all_2026-11-05_10-00-00")
    monkeypatch.setattr(pe, "executer_enfant", faux)
    ctx = ctx_execution(tmp_path)
    r = L.executer_partie(T_WB, ctx)
    assert r["ok"] and r["trace"] and r["terminaison"] == "" and r["renvoyes"] == [("claude-haiku-5-5", "claude-haiku-5-5")]
    assert (ctx["sortie"] / "taches" / T_WB["id"] / "email_tasks_and_outcomes.csv").is_file()
    assert L.classer(T_WB, r)[0] == L.TERMINEE
    faux, _ = faux_workbench(tmp_path, nom="claude-haiku-5-5_all_2026-11-05_10-00-07", erreur="Error code: 529 overloaded")
    monkeypatch.setattr(pe, "executer_enfant", faux)
    t2 = dict(T_WB, id=T_WB["id"] + "-t2")
    r = L.executer_partie(t2, ctx)
    assert r["ok"] and L.classer(t2, r)[0] == L.ECHEC


def test_workbench_deux_parties_n_ont_jamais_le_meme_nom(tmp_path, monkeypatch):
    """Constaté à l'essai à blanc complet : deux parties lancées dans la même seconde avaient le même nom de fichier."""
    preparer_workbench(tmp_path, monkeypatch)
    faux, debuts = faux_workbench(tmp_path)
    monkeypatch.setattr(pe, "executer_enfant", faux)
    ctx = ctx_execution(tmp_path)
    r1 = L.executer_partie(T_WB, ctx)
    r2 = L.executer_partie(dict(T_WB, id="WorkBench-haiku-p02-email_1"), ctx)
    n1, n2 = (Path(next(c for c in r["copies"] if c.endswith(".csv"))).stem for r in (r1, r2))
    assert r1["ok"] and r2["ok"] and n1 != n2 and int(debuts[1]) > int(debuts[0])


def test_workbench_nom_deja_utilise_est_un_echec_et_renomme(tmp_path, monkeypatch):
    preparer_workbench(tmp_path, monkeypatch)
    nom = "claude-haiku-5-5_all_2026-11-05_10-00-00"
    faux, _ = faux_workbench(tmp_path, nom=nom)
    monkeypatch.setattr(pe, "executer_enfant", faux)
    ctx = dict(ctx_execution(tmp_path), wb_etat={"prochain": 0.0, "noms": {nom}})
    r = L.executer_partie(T_WB, ctx)
    assert not r["ok"] and "déjà utilisé" in r["erreur"] and L.classer(T_WB, r)[0] == L.ECHEC
    assert all(Path(c).name.startswith("nom-deja-utilise-") for c in r["copies"])
    assert L.noms_workbench_existants(ctx["sortie"]) == {"nom-deja-utilise-" + nom}
    assert L.seconde_du_nom_workbench(nom + ".csv") == datetime(2026, 11, 5, 10, 0, 0).timestamp()
    assert L.seconde_du_nom_workbench("autre.csv") is None


# ================================================================== 9. les sorties
CHAMPS_PILOTE = {"id", "env", "modele", "tache", "ok", "erreur", "appels", "appels_hauts", "jetons_entree",
                 "jetons_non_caches", "cache_ecriture", "cache_lecture", "jetons_sortie", "cout_usd", "estime"}
CHAMPS_NOUVEAUX = {"partie", "tentative", "passage", "rang", "vague", "statut", "arret", "terminaison", "finale", "exclue",
                   "motif_exclusion", "dossier", "modeles_renvoyes", "usage", "cout_majore", "debut", "fin"}


def test_sorties_au_format_du_pilote_avec_les_nouveaux_champs(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    ex = executeur_factice(fichiers=True, plus=lambda t: {"ok": not t["id"].startswith("commerce"),
                                                           "erreur": "échec" if t["id"].startswith("commerce") else None})
    rc = L.main(argv(tmp_path), executeur=ex, base_env={}, extracteur=extracteur_ok)
    d = dossier_unique(tmp_path)
    cout = json.loads((d / "cout.json").read_text())
    assert rc == 4 or rc == 0
    for k in ("etape", "mode", "cache", "client_simule", "prix_usd_par_million", "plafond_usd", "seuil_arret_usd",
              "cumul_usd", "arret", "usage_estime", "parties", "vague", "graine", "accord_otsoa_usd", "fin"):
        assert k in cout
    assert cout["vague"] == 1 and cout["graine"] == 5 and cout["fin"] and cout["mode"] == "à blanc"
    for l in cout["parties"]:
        assert CHAMPS_PILOTE | CHAMPS_NOUVEAUX <= set(l)
        assert l["ok"] == (l["dossier"] or "").startswith("parties/")
    gardees = {l["id"] for l in cout["parties"] if l["ok"]}
    dossiers = {p.name.split("-", 1)[1] for p in (d / "parties").iterdir()}
    assert dossiers == gardees and all(p.name.split("-", 1)[0] in ("tau2", "workbench") for p in (d / "parties").iterdir())
    assert {p.name.split("-", 1)[1] for p in (d / "ecartees").iterdir()} == {l["id"] for l in cout["parties"] if not l["ok"]}
    plan = json.loads((d / "plan_de_jeu.json").read_text())
    assert plan["graine"] == 5 and plan["parties_vague"] == 57 and plan["estimation_usd"] == pytest.approx(2.51, abs=0.01)
    ordre = (d / "ordre_de_jeu.csv").read_text().splitlines()
    assert len(ordre) == 58 and ordre[0].startswith("ordre,id,env,modele,tache,passage")
    assert hashlib.sha256("\n".join(x.split(",")[1] for x in ordre[1:]).encode()).hexdigest() == plan["ordre_sha256"]
    for nom in ("journal.log", "tentatives.jsonl", "modeles_renvoyes.json", "outils_agent.json", "rapport_vague.json",
                "rapport_vague.txt"):
        assert (d / nom).is_file()


def test_essai_a_blanc_ne_lit_pas_la_cle_et_nettoie_l_environnement(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    trace = []
    base = {"PATH": "/usr/bin", "OPENAI_API_KEY": "o", "OPENROUTER_API_KEY": "r", "ANTHROPIC_API_KEY": "parent"}
    rc = L.main(argv(tmp_path), executeur=executeur_factice(trace), base_env=base, chemin_cle=tmp_path / "ne-pas-lire",
                extracteur=extracteur_ok)
    assert rc == 0 and len(trace) == 57
    for _id, reel, env in trace:
        assert reel is False and "ANTHROPIC_API_KEY" not in env and env["PILOTE_HORS_LIGNE"] == "2"
        assert "OPENAI_API_KEY" not in env and env["HTTPS_PROXY"] == pe.PROXY_CASSE
    assert dossier_unique(tmp_path).name.endswith("-blanc")


def test_graine_tiree_et_notee_si_absente(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L.secrets, "randbits", lambda n: 424242)
    assert L.main(argv(tmp_path, graine=None), executeur=executeur_factice(), base_env={}, extracteur=extracteur_ok) == 0
    plan = json.loads((dossier_unique(tmp_path) / "plan_de_jeu.json").read_text())
    assert plan["graine"] == 424242 and "secrets" in plan["graine_source"]


def test_reel_cle_dans_les_enfants_seulement_et_aucune_fuite(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L, "RESERVE", ecrire_reserve(tmp_path))
    sim = tmp_path / "tau2" / "data" / "simulations"
    (sim / "essai-blanc-vieux").mkdir(parents=True)
    trace = []
    base = {"PATH": "/usr/bin", "OPENAI_API_KEY": "o", "PILOTE_USAGE_FILE": "/ailleurs"}
    a = argv(tmp_path, "--reel", reserve=L.RESERVE)
    rc = L.main(a, executeur=executeur_factice(trace), base_env=base, chemin_cle=fichier_cle(tmp_path),
                extracteur=extracteur_ok)
    assert rc == 0 and len(trace) == 57 and not (sim / "essai-blanc-vieux").exists()
    for _id, reel, env in trace:
        assert reel and env["ANTHROPIC_API_KEY"] == CLE and "OPENAI_API_KEY" not in env and "PILOTE_USAGE_FILE" not in env
    d = dossier_unique(tmp_path)
    assert not d.name.endswith("-blanc")
    for f in d.rglob("*"):
        if f.is_file():
            assert CLE not in f.read_text(errors="ignore"), f


def test_reel_refuse_cle_mal_protegee_et_reserve_non_standard(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L, "RESERVE", ecrire_reserve(tmp_path))
    c = fichier_cle(tmp_path)
    os.chmod(c, 0o644)
    trace = []
    assert L.main(argv(tmp_path, "--reel", reserve=L.RESERVE), executeur=executeur_factice(trace), base_env={},
                  chemin_cle=c, extracteur=extracteur_ok) == 2
    autre = tmp_path / "autre"
    autre.mkdir()
    assert L.main(argv(tmp_path, "--reel", reserve=ecrire_reserve(autre)), executeur=executeur_factice(trace),
                  base_env={}, chemin_cle=fichier_cle(tmp_path), extracteur=extracteur_ok) == 2
    assert not trace


def test_limite_a_blanc_seulement(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    trace = []
    assert L.main(argv(tmp_path, "--limite", "7"), executeur=executeur_factice(trace), base_env={},
                  extracteur=extracteur_ok) == 0
    assert len(trace) == 7
    monkeypatch.setattr(L, "RESERVE", ecrire_reserve(tmp_path))
    assert L.main(argv(tmp_path, "--reel", "--limite", "7", reserve=L.RESERVE), executeur=executeur_factice(trace),
                  base_env={}, chemin_cle=fichier_cle(tmp_path), extracteur=extracteur_ok) == 2
    assert len(trace) == 7


# ================================================================== 10. le rapport de vague
def actions_type(verdict="juste"):
    return [
        {"banc": "tau2", "domaine": "airline", "outil": "get_user_details", "kind": "lecture", "verdict": "", "type": "lecture"},
        {"banc": "tau2", "domaine": "airline", "outil": "book_reservation", "kind": "écriture", "verdict": verdict,
         "type": "argent"},
        {"banc": "tau2", "domaine": "airline", "outil": "cancel_reservation", "kind": "écriture", "verdict": "",
         "type": "argent"},
        {"banc": "tau2", "domaine": "airline", "outil": "outil_nouveau", "kind": "inconnu", "verdict": "",
         "type": "effet illisible"},
        {"banc": "tau2", "domaine": "retail", "outil": "calculate", "kind": "autre", "verdict": "", "type": "lecture"},
        {"banc": "tau2", "domaine": "retail", "outil": "transfer_to_human_agents", "kind": "doute", "verdict": "",
         "type": "doute"},
        {"banc": "tau2", "domaine": "banking_knowledge", "outil": "submit_dispute_4821", "kind": "écriture",
         "verdict": verdict, "type": "écriture réversible"},
        {"banc": "workbench", "domaine": "email", "outil": "email.send_email", "kind": "écriture", "verdict": verdict,
         "type": "message interne"},
    ]


def test_instrument_couverture_et_nouveaux_noms_d_outils():
    i = L.instrument(actions_type())
    av = i["par_environnement"]["aviation"]
    assert (av["actions"], av["ecritures"], av["verifiables"], av["sans_verdict"], av["inconnu"], av["effet_illisible"]) \
        == (4, 3, 1, 2, 1, 1)
    assert av["couverture"] == pytest.approx(1 / 3) and av["sous_le_seuil"]
    assert i["par_environnement"]["commerce"]["ecritures"] == 0 and i["par_environnement"]["commerce"]["couverture"] is None
    assert i["par_environnement"]["WorkBench"]["couverture"] == 1.0 and not i["par_environnement"]["WorkBench"]["sous_le_seuil"]
    assert i["total"]["ecritures"] == 5 and i["total"]["verifiables"] == 3
    assert i["outils_hors_table"]["aviation"] == ["outil_nouveau"]
    assert i["outils_hors_definitions_figees"] == {"aviation": ["outil_nouveau"]}  # outil bancaire découvrable écarté


def rapport_de(actions, lignes=None):
    plan = {"vague": 1, "mode": "à blanc", "estimation_usd": 1.0, "couts_moyens": L.COUT_PILOTE, "plafond_usd": 2.0,
            "seuil_arret_usd": 1.6, "par_configuration": [{"modele": "claude-haiku-5-5", "env": "aviation", "parties": 2,
                                                          "cout_moyen_usd": 0.005, "estimation_usd": 0.01}]}
    parties = [{"id": f"p{i}", "modele": "claude-haiku-5-5", "env": "aviation"} for i in range(2)]
    r = L.rapport_vague(plan, parties, lignes or [], actions, L.Noms(), [], {("claude-haiku-5-5", "aviation"): 3},
                        budget=500.0, joues={}, taches={"aviation": 40, "commerce": 91, "banque": 77, "WorkBench": 552})
    r.pop("horodatage")
    return r


def test_rapport_ne_depend_pas_de_la_valeur_des_verdicts():
    base = rapport_de(actions_type("juste"))
    for v in ("fausse", "doublon", "refusée", "doublon sans effet"):
        assert rapport_de(actions_type(v)) == base
        assert L.texte_rapport(dict(rapport_de(actions_type(v)), horodatage="h")) == \
            L.texte_rapport(dict(base, horodatage="h"))


def test_rapport_sans_decompte_d_erreurs_ni_d_alertes():
    r = rapport_de(actions_type("fausse"))
    brut = (json.dumps(r, ensure_ascii=False) + L.texte_rapport(dict(r, horodatage="h"))).lower()
    for mot in MOTS_INTERDITS:
        assert mot not in brut, mot
    assert set(r) == {"vague", "mode", "limite", "arret", "reduction_des_passages", "1_cout", "2_deroulement",
                      "3_instrument", "6_nom_de_modele", "non_couvert"}


def test_rapport_extrapolation_et_reduction_previsible():
    lignes = [{"modele": "claude-haiku-5-5", "env": "aviation", "partie": "p0", "cout_usd": 0.02, "statut": L.TERMINEE,
               "ok": True}]
    c = rapport_de([], lignes)["1_cout"]
    x = c["par_configuration"][0]
    assert x["cout_moyen_usd"] == pytest.approx(0.02) and x["ecart_pct"] == pytest.approx(300.0)
    e = c["extrapolation"]
    assert e["estimation_restante_usd"] == pytest.approx(0.06) and e["total_extrapole_usd"] == pytest.approx(0.08)
    assert e["estimation_restante_tient_dans_le_budget"] and "centiemes" in e["reduction_previsible"]
    assert e["plafond_refait_tient_dans_le_budget"]


def test_le_lanceur_n_ecrit_pas_le_resume_par_verdict_du_pilote(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path, actions=actions_type("fausse"))
    assert L.main(argv(tmp_path), executeur=executeur_factice(), base_env={}, extracteur=extracteur_ok) == 0
    d = dossier_unique(tmp_path)
    assert not (d / "resume.txt").exists() and not (d / "resume.json").exists() and not (d / "reussite.csv").exists()
    texte = (d / "rapport_vague.txt").read_text().lower()
    for mot in MOTS_INTERDITS:
        assert mot not in texte, mot


# ================================================================== la vague 2
def vague1_a_blanc(tmp_path, monkeypatch):
    """Vague 1 à blanc, chaque partie à 0,04 $ (20 000 jetons Sonnet, 2,28 $ pour 57 parties, sous l'arrêt à 2,40 $).
    Nom renvoyé : le modèle demandé."""
    neutraliser(monkeypatch, tmp_path)
    assert L.main(argv(tmp_path), executeur=executeur_factice(p=20_000, s=0, modele="claude-sonnet-5-5"), base_env={},
                  extracteur=extracteur_ok) == 0
    return dossier_unique(tmp_path)


def vague1_reelle(tmp_path, monkeypatch, p=20_000):
    """Vague 1 en réel (fausse clé, exécuteur factice, la réserve de test tient lieu de réserve officielle), une partie
    à la fois, chaque partie au prix de p jetons Sonnet. À 20 000 jetons : 0,04 $ par partie, 2,28 $ pour 57 parties,
    sous l'arrêt à 2,40 $ ; l'estimation refaite de la vague 2 (486 x 0,04 $ = 19,44 $) donne un plafond au-dessus de
    la réserve de 15 $."""
    neutraliser(monkeypatch, tmp_path)
    monkeypatch.setattr(L, "RESERVE", ecrire_reserve(tmp_path))
    rc = L.main(argv(tmp_path, "--reel", "--concurrence", "1", reserve=L.RESERVE),
                executeur=executeur_factice(p=p, s=0, modele="claude-sonnet-5-5"), base_env={},
                chemin_cle=fichier_cle(tmp_path), extracteur=extracteur_ok)
    return rc, dossier_unique(tmp_path)


def plafond_permis_v2(tmp_path, v1, budget, reel=False):
    a = L.analyser(["--vague", "2", "--apercu", "--vague1", str(v1), "--budget-restant-usd", budget, "--reserve",
                    str(tmp_path / "reserve.json")] + (["--reel"] if reel else []))
    return math.floor(L.preparer(a)["plan"]["plafond_permis_usd"] * 100) / 100


def main_v2_reelle(tmp_path, v1, budget, plafond, executeur):
    return L.main(argv(tmp_path, "--reel", "--vague1", str(v1), "--budget-restant-usd", budget, vague=2,
                       plafond=str(plafond), accord=str(plafond), graine=None, reserve=L.RESERVE),
                  executeur=executeur, base_env={}, chemin_cle=fichier_cle(tmp_path), extracteur=extracteur_ok)


def test_vague_2_reelle_joue_le_reste_avec_les_couts_mesures(tmp_path, monkeypatch):
    rc, v1 = vague1_reelle(tmp_path, monkeypatch)
    assert rc == 0
    p = plafond_permis_v2(tmp_path, v1, "1000", reel=True)
    assert p == pytest.approx(1.25 * 486 * 0.04, abs=0.011)
    trace = []
    rc = main_v2_reelle(tmp_path, v1, "1000", p, executeur_factice(trace, p=5_000, s=0, modele="claude-sonnet-5-5"))
    assert rc == 0 and len(trace) == 543 - 57  # 0,01 $ par partie : 4,86 $, sous le seuil
    d = dossier_unique(tmp_path, 2)
    plan = json.loads((d / "plan_de_jeu.json").read_text())
    assert plan["graine"] == 5 and plan["reduction"] is None and plan["source_couts"].startswith("coûts mesurés")
    assert plan["couts_moyens"]["claude-haiku-5-5"]["aviation"] == pytest.approx(0.04)
    assert not plan["couts_du_pilote_essai_a_blanc"]
    cout = json.loads((d / "cout.json").read_text())
    assert cout["seuil_arret_usd"] == pytest.approx(min(0.95 * p, p - 15))  # ici, la réserve de 15 $ l'emporte
    ids1 = {l["partie"] for l in lignes_cout(v1)}
    assert not ids1 & {l["partie"] for l in lignes_cout(d)}
    noms = json.loads((d / "modeles_renvoyes.json").read_text())
    assert noms["reference"] == {"tau2:claude-sonnet-5-5": "claude-sonnet-5-5",
                                 "workbench:claude-sonnet-5-5": "claude-sonnet-5-5"} and not noms["changements"]


def test_vague_2_reelle_refusee_si_une_configuration_n_a_pas_de_mesure(tmp_path, monkeypatch, capsys):
    rc, v1 = vague1_reelle(tmp_path, monkeypatch, p=200_000)  # 0,40 $ par partie : arrêt après 6 parties Haiku
    assert rc == 4
    capsys.readouterr()
    trace = []
    assert main_v2_reelle(tmp_path, v1, "1000", 20, executeur_factice(trace)) == 2
    assert not trace and "coût moyen par partie inconnu" in capsys.readouterr().err


def test_vague_2_a_blanc_estimee_sur_les_couts_du_pilote_et_jouable(tmp_path, monkeypatch):
    """Même cas qu'au-dessus, à blanc : une vague 1 à blanc écourtée (configurations sans mesure, coûts factices)."""
    neutraliser(monkeypatch, tmp_path)
    assert L.main(argv(tmp_path, "--limite", "3"), executeur=executeur_factice(), base_env={},
                  extracteur=extracteur_ok) == 0
    v1 = dossier_unique(tmp_path)
    p = plafond_permis_v2(tmp_path, v1, "1000")
    assert L.seuil_arret(2, p)[0] > 0  # plafond réaliste : au-dessus de la réserve de 15 $
    trace = []
    rc = L.main(argv(tmp_path, "--vague1", str(v1), "--budget-restant-usd", "1000", "--limite", "4", vague=2,
                     plafond=str(p), accord=str(p), graine=None),
                executeur=executeur_factice(trace), base_env={}, extracteur=extracteur_ok)
    assert rc == 0 and len(trace) == 4
    d = dossier_unique(tmp_path, 2)
    plan = json.loads((d / "plan_de_jeu.json").read_text())
    assert plan["couts_moyens"] == L.COUT_PILOTE and plan["couts_du_pilote_essai_a_blanc"]
    assert plan["source_couts"].startswith("coûts du pilote, essai à blanc")
    assert "coûts du pilote, essai à blanc" in (d / "journal.log").read_text()
    assert plan["estimation_usd"] == pytest.approx(L.estimation(L.construire_parties(RESERVE_TEST, 5), L.COUT_PILOTE)
                                                   - sum(L.COUT_PILOTE[l["modele"]][l["env"]] for l in lignes_cout(v1)))


def test_vague_2_reduction_appliquee_et_declaree(tmp_path, monkeypatch):
    rc, v1 = vague1_reelle(tmp_path, monkeypatch)
    assert rc == 0
    p = plafond_permis_v2(tmp_path, v1, "20", reel=True)  # 1,25 x 19,44 $ = 24,30 $ > 20 $ : passages réduits
    trace = []
    rc = main_v2_reelle(tmp_path, v1, "20", p, executeur_factice(trace, p=2_000, s=0, modele="claude-sonnet-5-5"))
    d = dossier_unique(tmp_path, 2)
    plan = json.loads((d / "plan_de_jeu.json").read_text())
    red = plan["reduction"]
    assert rc == 0 and red and red["centiemes"] < 100 and 1.25 * red["total_refait_usd"] <= 20 + 1e-9
    assert red["plafond_refait_usd"] == pytest.approx(1.25 * red["total_refait_usd"]) and p <= 20
    assert plan["passages"] == L.passages_reduits(L.PASSAGES, red["centiemes"])
    assert len(trace) == plan["parties_vague"] < 543 - 57
    assert "RÉDUCTION DES PASSAGES" in (d / "journal.log").read_text()
    assert "Réduction des passages" in (d / "rapport_vague.txt").read_text()


def test_vague_2_refus(tmp_path, monkeypatch):
    v1 = vague1_a_blanc(tmp_path, monkeypatch)
    trace = []
    ex = executeur_factice(trace)
    assert L.main(argv(tmp_path, "--budget-restant-usd", "10", vague=2, graine=None), executeur=ex, base_env={},
                  extracteur=extracteur_ok) == 2  # --vague1 manque
    assert L.main(argv(tmp_path, "--vague1", str(v1), vague=2, graine=None), executeur=ex, base_env={},
                  extracteur=extracteur_ok) == 2  # budget restant manque
    assert L.main(argv(tmp_path, "--vague1", str(v1), "--budget-restant-usd", "10", vague=2), executeur=ex,
                  base_env={}, extracteur=extracteur_ok) == 2  # --graine interdite
    monkeypatch.setattr(L, "RESERVE", tmp_path / "reserve.json")
    assert L.main(argv(tmp_path, "--reel", "--vague1", str(v1), "--budget-restant-usd", "10", vague=2, graine=None,
                       reserve=L.RESERVE), executeur=ex, base_env={}, chemin_cle=fichier_cle(tmp_path),
                  extracteur=extracteur_ok) == 2  # vague 1 jouée à blanc
    assert not trace and not (tmp_path / "s" / "vague2").exists()


# ================================================================== reprise
def test_reprise_apres_arret_compte_le_deja_depense(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    cher = executeur_factice(p=200_000, s=0, modele="claude-sonnet-5-5")  # 0,40 $ par partie
    assert L.main(argv(tmp_path, plafond="2", accord="2"), executeur=cher, base_env={}, extracteur=extracteur_ok) == 4
    d = dossier_unique(tmp_path)
    n1 = len(lignes_cout(d))
    trace = []
    rc = L.main(argv(tmp_path, "--reprendre", str(d), plafond="2", accord="2"), executeur=executeur_factice(trace),
                base_env={}, extracteur=extracteur_ok)
    assert rc == 4 and not trace  # déjà au-delà de 80 % du plafond : aucune nouvelle partie
    rc = L.main(argv(tmp_path, "--reprendre", str(d), plafond="3.7", accord="3.7"), executeur=executeur_factice(trace),
                base_env={}, extracteur=extracteur_ok)
    cout = json.loads((d / "cout.json").read_text())
    assert rc == 0 and len(trace) == 57 - n1 and len(cout["parties"]) == 57
    assert len(cout["reprises"]) == 2 and cout["arrets"] and len({l["partie"] for l in cout["parties"]}) == 57
    assert cout["cumul_usd"] == pytest.approx(sum(l["cout_usd"] for l in cout["parties"]))


def test_reprise_recupere_une_tentative_interrompue(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    assert L.main(argv(tmp_path, "--limite", "3"), executeur=executeur_factice(), base_env={},
                  extracteur=extracteur_ok) == 0
    d = dossier_unique(tmp_path)
    suivante = L.construire_parties(RESERVE_TEST, 5)
    t = L.tentative(L.parties_vague1(suivante)[3], 1, 1)
    with open(d / "tentatives.jsonl", "a") as fh:  # arrêt brutal pendant la 4e partie
        fh.write(json.dumps({"evenement": "début", "id": t["id"], "tentative": {k: t[k] for k in L.CHAMPS_TENTATIVE}}) + "\n")
    (d / "usage").mkdir(exist_ok=True)
    ecrire_usage(d / "usage" / f"{t['id']}.jsonl", [("claude-sonnet-5-5", "claude-sonnet-5-5", 50_000, 0)])  # 0,10 $
    (d / "parties" / f"tau2-{t['id']}").mkdir(parents=True)
    trace = []
    rc = L.main(argv(tmp_path, "--reprendre", str(d), "--limite", "1"), executeur=executeur_factice(trace), base_env={},
                extracteur=extracteur_ok)
    lignes = lignes_cout(d)
    inter = [l for l in lignes if l["statut"] == L.INTERROMPUE]
    assert rc == 0 and len(inter) == 1 and inter[0]["cout_usd"] == pytest.approx(0.1) and inter[0]["partie"] == t["id"]
    assert trace[0][0] == t["id"]  # rejouée, avec le même identifiant (l'interruption ne compte pas)
    assert not (d / "usage" / f"{t['id']}.jsonl").exists() and inter[0]["dossier"].startswith("ecartees/")
    assert not (d / "parties" / f"tau2-{t['id']}").exists()
    assert json.loads((d / "cout.json").read_text())["cumul_usd"] == pytest.approx(
        sum(l["cout_usd"] or 0 for l in lignes))


def test_reprise_refusee_si_autre_vague_ou_tentatives_illisibles(tmp_path, monkeypatch):
    neutraliser(monkeypatch, tmp_path)
    assert L.main(argv(tmp_path, "--limite", "2"), executeur=executeur_factice(), base_env={},
                  extracteur=extracteur_ok) == 0
    d = dossier_unique(tmp_path)
    trace = []
    assert L.main(argv(tmp_path, "--reprendre", str(d), "--graine", "6"), executeur=executeur_factice(trace),
                  base_env={}, extracteur=extracteur_ok) == 2
    with open(d / "tentatives.jsonl", "a") as fh:
        fh.write('{"evenement": "fin", "id": "x", "ligne": {"cout_\n')
    assert L.main(argv(tmp_path, "--reprendre", str(d)), executeur=executeur_factice(trace), base_env={},
                  extracteur=extracteur_ok) == 2
    assert not trace


def test_file_d_attente_tentative_suivante():
    ps = [{"id": "a"}, {"id": "b"}, {"id": "c"}, {"id": "d"}, {"id": "e"}]
    lignes = [{"partie": "a", "statut": L.ECHEC, "finale": False}, {"partie": "b", "statut": L.TERMINEE, "finale": True},
              {"partie": "c", "statut": L.INTERROMPUE, "finale": False},
              {"partie": "d", "statut": L.EXCLUE_NOM, "finale": False}, {"partie": "d", "statut": L.ECHEC, "finale": False},
              {"partie": "e", "statut": L.EXCLUE_NOM, "finale": True}]
    assert [(x["id"], k) for x, k in L.file_d_attente(ps, lignes)] == [("a", 2), ("c", 1), ("d", 3)]


# ================================================================== rejeu d'une exclusion pour nom changé (06/11)
def vague_coupee_par_un_nom(tmp_path, monkeypatch):
    """Vague 1 à blanc, une partie à la fois ; la 3e partie reçoit un autre nom de modèle : exclue, arrêt."""
    neutraliser(monkeypatch, tmp_path)
    vus = []

    def nouveau_au_troisieme(t):
        vus.append(t["id"])
        return "NOUVEAU" if len(vus) == 3 else t["modele"]

    assert L.main(argv(tmp_path, "--concurrence", "1"), executeur=executeur_factice(renvoye=nouveau_au_troisieme),
                  base_env={}, extracteur=extracteur_ok) == 4
    d = dossier_unique(tmp_path)
    (x,) = [l for l in lignes_cout(d) if l["statut"] == L.EXCLUE_NOM]
    assert len(lignes_cout(d)) == 3 and x["tentative"] == 1 and x["exclue"] and not x["finale"]
    return d, x


def test_exclusion_pour_nom_change_rejouee_une_fois_a_la_reprise(tmp_path, monkeypatch):
    d, x = vague_coupee_par_un_nom(tmp_path, monkeypatch)
    trace = []  # reprise, l'ancien nom est revenu
    rc = L.main(argv(tmp_path, "--reprendre", str(d), "--concurrence", "1"), executeur=executeur_factice(trace),
                base_env={}, extracteur=extracteur_ok)
    assert rc == 0 and trace[0][0] == x["partie"] + "-t2"  # rejouée en premier, sous un nouveau numéro
    deux = [l for l in lignes_cout(d) if l["partie"] == x["partie"]]
    assert [(l["id"], l["tentative"], l["statut"], l["exclue"], l["ok"]) for l in deux] == [
        (x["partie"], 1, L.EXCLUE_NOM, True, False), (x["partie"] + "-t2", 2, L.TERMINEE, False, True)]
    noms = json.loads((d / "rapport_vague.json").read_text())["6_nom_de_modele"]
    assert noms["parties_exclues"] == [x["partie"]] and noms["parties_a_rejouer"] == []  # les deux sont déclarées


def test_rejeu_sous_le_nouveau_nom_exclut_definitivement(tmp_path, monkeypatch):
    d, x = vague_coupee_par_un_nom(tmp_path, monkeypatch)
    rc = L.main(argv(tmp_path, "--reprendre", str(d), "--concurrence", "1"),
                executeur=executeur_factice(renvoye="NOUVEAU"), base_env={}, extracteur=extracteur_ok)
    deux = [l for l in lignes_cout(d) if l["partie"] == x["partie"]]
    assert rc == 4 and [(l["tentative"], l["statut"], l["exclue"], l["finale"]) for l in deux] == [
        (1, L.EXCLUE_NOM, True, False), (2, L.EXCLUE_NOM, True, True)]
    assert deux[1]["motif_exclusion"] == L.MOTIF_NOM_DEUX_FOIS
    trace = []  # nouvelle reprise, ancien nom revenu : la partie n'est plus rejouée
    rc = L.main(argv(tmp_path, "--reprendre", str(d), "--concurrence", "1"), executeur=executeur_factice(trace),
                base_env={}, extracteur=extracteur_ok)
    rejeux = {x["partie"], x["partie"] + "-t2", x["partie"] + "-t3"}
    assert rc == 0 and trace and not rejeux & {tid for tid, _, _ in trace}
