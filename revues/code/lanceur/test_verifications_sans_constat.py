"""Vérifications indépendantes de la revue du lanceur qui n'ont RIEN trouvé (section « vérifié sans constat » du
rapport). Calculs refaits à la main ou par force brute, sans reprendre le code du lanceur. Tous ces tests passent.

    cd ROOT
    env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u OPENROUTER_API_KEY \
        simulation/.venv/bin/python -m pytest -q -p no:cacheprovider revues/code/lanceur/test_verifications_sans_constat.py
"""
import math
import random
from fractions import Fraction

import pytest

import cout_v2 as cv
import lanceur as L
import pilote_etape1 as pe
import test_lanceur as T


# ------------------------------------------------------------------------------------- prix (2.2), cache, palier
def appel(m, p, s, ce=0, cl=0):
    return {"modele": m, "prompt_tokens": p, "completion_tokens": s, "cache_creation_input_tokens": ce,
            "cache_read_input_tokens": cl}


@pytest.mark.parametrize("a,attendu", [
    (appel("claude-haiku-5-5", 100_000, 1000), (100_000 * 0.10 + 1000 * 0.50) / 1e6),  # pile au seuil : palier bas
    (appel("claude-haiku-5-5", 100_001, 1000), (100_001 * 0.50 + 1000 * 2.50) / 1e6),  # au-delà : tout au palier haut
    (appel("anthropic/claude-haiku-5-5", 150_000, 1000, cl=140_000),
     (10_000 * 0.50 + 140_000 * 0.50 * 0.1 + 1000 * 2.50) / 1e6),  # palier jugé cache compris, lecture à 0,1
    (appel("claude-sonnet-5-5", 10_000, 500, ce=2_000, cl=7_000),
     (1_000 * 2 + 2_000 * 2 * 1.25 + 7_000 * 2 * 0.1 + 500 * 10) / 1e6),
    (appel("claude-opus-5-5", 10_000, 500, ce=1_000, cl=8_000),
     (1_000 * 4 + 1_000 * 4 * 1.25 + 8_000 * 4 * 0.05 + 500 * 20) / 1e6),  # lecture Opus à 0,05
])
def test_prix_de_2_2(a, attendu):
    assert cv.bilan([a])["cout_usd"] == pytest.approx(attendu, abs=1e-8)


def test_client_simule_compte_dans_la_tentative():
    """Une tentative Opus avec son client simulé Haiku : les deux modèles sont comptés, chacun à son prix."""
    r = {"ok": True, "appels": [appel("claude-opus-5-5", 2000, 100), appel("anthropic/claude-haiku-5-5", 3000, 50)],
         "renvoyes": [], "trace": True, "terminaison": "user_stop"}
    t = L.tentative(T.premieres(1)[0][0], 1, 1)
    _, cout, coupure = L.traiter_tentative(t, r, "d")
    assert cout == pytest.approx((2000 * 4 + 100 * 20 + 3000 * 0.10 + 50 * 0.50) / 1e6) and coupure is None


# ------------------------------------------------------------------------------------- seuils et plafonds
@pytest.mark.parametrize("p", [15.01, 50.0, 100.0, 299.99, 300.0, 300.01, 741.43])
def test_seuils(p):
    assert L.seuil_arret(1, p)[0] == pytest.approx(0.8 * p)
    assert L.seuil_arret(2, p)[0] == pytest.approx(min(0.95 * p, p - 15))


def test_refus_du_plafond():
    est = 60.53
    assert L.verifier_plafond(1, 1.5 * est, 1.5 * est, est) == pytest.approx(1.5 * est)
    for plafond, accord in ((1.5 * est + 0.01, 1000), (50, 49.99), (-0.0, 10), (float("nan"), 10), (10, float("inf"))):
        with pytest.raises(pe.ErreurPilote):
            L.verifier_plafond(1, plafond, accord, est)
    with pytest.raises(pe.ErreurPilote):  # vague 2 : au-delà du budget restant
        L.verifier_plafond(2, 100.01, 1000, 1000, budget_restant=100.0)
    with pytest.raises(pe.ErreurPilote):  # vague 2 : seuil nul
        L.verifier_plafond(2, 15.0, 1000, 1000, budget_restant=1000)


def test_vague_1_du_plan_60_53_dollars_plafond_90_78():
    parties = L.construire_parties(T.vraie_reserve(), 77)
    v1 = L.parties_vague1(parties)
    est = L.estimation(v1, L.COUT_PILOTE)
    assert round(est, 2) == 60.53 and math.floor(1.5 * est * 100) / 100 == 90.78 and len(v1) == 1430


# ------------------------------------------------------------------------------------- réduction C9 (force brute)
def c9_force_brute(passages, couts, taches, joues, budget):
    meilleur = None
    for c in range(1, 101):
        red = {m: {e: max(1, math.floor(Fraction(c, 100) * n)) for e, n in d.items()} for m, d in passages.items()}
        total = 0.0
        for m, d in red.items():
            for e, n in d.items():
                deja = sum(k for p, k in joues.get((m, e), {}).items() if p <= n)
                total += max(0, n * taches[e] - deja) * couts[m][e]
        if 1.25 * total <= budget + 1e-9:
            meilleur = (c, red, total)
    return meilleur


def test_c9_egale_la_force_brute_sur_des_tirages():
    rng = random.Random(20261106)
    taches = {"aviation": 40, "commerce": 91, "banque": 77, "WorkBench": 552}
    for _ in range(300):
        couts = {m: {e: L.COUT_PILOTE[m][e] * rng.uniform(0.3, 3.0) for e in L.ENVS} for m in L.MODELES}
        joues = {(m, e): {p: taches[e] if p < 2 else rng.randint(0, taches[e]) for p in range(1, rng.randint(1, 3))}
                 for m in L.MODELES for e in L.ENVS if rng.random() < 0.7}
        budget = rng.uniform(5, 1500)
        attendu = c9_force_brute(L.PASSAGES, couts, taches, joues, budget)
        if attendu is None:
            with pytest.raises(pe.ErreurPilote):
                L.facteur_reduction(L.PASSAGES, couts, taches, joues, budget)
            continue
        c, red, total = L.facteur_reduction(L.PASSAGES, couts, taches, joues, budget)
        assert (c, red) == attendu[:2] and total == pytest.approx(attendu[2])


# ------------------------------------------------------------------------------------- ordre de jeu et vague 1
def test_vague_1_est_le_debut_de_chaque_configuration_dans_l_ordre_tire():
    reserve = T.vraie_reserve()
    parties = L.construire_parties(reserve, 31337)
    v1 = {x["id"] for x in L.parties_vague1(parties)}
    for m in L.MODELES:
        for e in L.ENVS:
            seq = [x for x in parties if x["modele"] == m and x["env"] == e]
            k = math.ceil(len(seq) / 10)
            assert [x["id"] in v1 for x in seq] == [True] * k + [False] * (len(seq) - k)
            assert [x["rang"] for x in seq] == list(range(1, len(seq) + 1))
            for p in range(1, L.PASSAGES[m][e] + 1):  # chaque passage : toutes les tâches, ordre SHA-256 de la graine
                taches = [x["tache"] for x in seq if x["passage"] == p]
                assert taches == sorted(reserve[e], key=lambda t: L.cle_ordre(31337, e, p, t))


# ------------------------------------------------------------------------------------- essai à blanc : aucune clé
def test_environnement_a_blanc_sans_aucune_cle_ni_redirection():
    base = {"PATH": "/usr/bin", "ANTHROPIC_API_KEY": "sk-ant-x", "ANTHROPIC_BASE_URL": "http://ailleurs",
            "OPENAI_API_KEY": "o", "LITELLM_PROXY": "p", "HTTPS_PROXY": "http://vrai", "MON_SECRET": "s"}
    env = pe.env_enfant(base, None)
    pe.verifier_env_enfant(env, False)
    assert not any(k.startswith(("ANTHROPIC_", "OPENAI_", "LITELLM_PROXY")) for k in env) and "MON_SECRET" not in env
    assert env["HTTPS_PROXY"] == pe.PROXY_CASSE and env["PILOTE_HORS_LIGNE"] == "2"
    with pytest.raises(pe.ErreurPilote):
        pe.verifier_env_enfant(dict(env, ANTHROPIC_API_KEY="sk-ant-x"), False)
