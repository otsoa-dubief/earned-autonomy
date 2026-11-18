"""Tests de banc/cout_v2.py (prix, palier, cache) et banc/usage_tau2.py (callback LiteLLM). Aucun appel réel."""
import json
import threading
from types import SimpleNamespace as NS

import pytest

import cout_v2 as c
import usage_tau2 as u


def approx(x):
    return pytest.approx(x, rel=1e-9, abs=1e-12)


# ---------------------------------------------------------------- prix
def test_prix_haiku_sans_cache():
    r = c.cout_appel("claude-haiku-5-5", 10_000, 1_000)
    assert r["cout"] == approx((10_000 * 0.10 + 1_000 * 0.50) / 1e6) and r["palier_haut"] is False


def test_prix_sonnet_et_opus():
    assert c.cout_appel("claude-sonnet-5-5", 1_000_000, 1_000_000)["cout"] == approx(2 + 10)
    assert c.cout_appel("claude-opus-5-5", 1_000_000, 1_000_000)["cout"] == approx(4 + 20)


def test_prefixe_anthropic_accepte():
    assert c.cout_appel("anthropic/claude-sonnet-5-5", 1000, 0)["cout"] == c.cout_appel("claude-sonnet-5-5", 1000, 0)["cout"]


@pytest.mark.parametrize("modele", ["gpt-5", "claude-haiku-4.5", "", None, "claude-haiku-5-5-x"])
def test_modele_inconnu_erreur(modele):
    with pytest.raises(c.ModeleInconnu):
        c.cout_appel(modele, 10, 10)
    assert issubclass(c.ModeleInconnu, ValueError)


def test_palier_haiku_exactement_100000_reste_bas_puis_haut():
    bas = c.cout_appel("claude-haiku-5-5", 100_000, 1000)
    haut = c.cout_appel("claude-haiku-5-5", 100_001, 1000)
    assert bas["palier_haut"] is False and bas["cout"] == approx((100_000 * 0.10 + 1000 * 0.50) / 1e6)
    assert haut["palier_haut"] is True and haut["cout"] == approx((100_001 * 0.50 + 1000 * 2.50) / 1e6)


def test_palier_sur_invite_totale_cache_compris():
    # 30 000 non cachés + 20 000 écrits + 60 000 lus = 110 000 > 100 000 : palier haut, multiplicateurs sur le prix du palier.
    r = c.cout_appel("claude-haiku-5-5", 110_000, 500, cache_ecriture=20_000, cache_lecture=60_000)
    attendu = (30_000 * 0.50 + 20_000 * 0.50 * 1.25 + 60_000 * 0.50 * 0.1 + 500 * 2.50) / 1e6
    assert r["palier_haut"] and r["cout"] == approx(attendu)


def test_multiplicateurs_cache_haiku_sonnet():
    r = c.cout_appel("claude-haiku-5-5", 1_000_000, 0, cache_ecriture=400_000, cache_lecture=500_000)
    assert r["palier_haut"]  # 1 M jetons
    r = c.cout_appel("claude-haiku-5-5", 90_000, 0, cache_ecriture=30_000, cache_lecture=50_000)
    assert r["cout"] == approx((10_000 * 0.10 + 30_000 * 0.10 * 1.25 + 50_000 * 0.10 * 0.1) / 1e6)
    r = c.cout_appel("claude-sonnet-5-5", 90_000, 0, cache_ecriture=30_000, cache_lecture=50_000)
    assert r["cout"] == approx((10_000 * 2 + 30_000 * 2 * 1.25 + 50_000 * 2 * 0.1) / 1e6)


def test_lecture_cache_opus_est_5_pour_cent():
    r = c.cout_appel("claude-opus-5-5", 1_000_000, 0, cache_ecriture=0, cache_lecture=1_000_000)
    assert r["cout"] == approx(0.20)
    r = c.cout_appel("claude-opus-5-5", 1_000_000, 0, cache_ecriture=1_000_000, cache_lecture=0)
    assert r["cout"] == approx(5.0)


def test_pas_de_double_compte_non_caches_est_le_reste():
    r = c.cout_appel("claude-sonnet-5-5", 1000, 0, cache_ecriture=300, cache_lecture=600)
    assert r["non_caches"] == 100


@pytest.mark.parametrize("args", [(100, 10, 60, 60), (-1, 0, 0, 0), (10, -1, 0, 0), (10, 0, -1, 0), (10, 0, 0, -5), (True, 0, 0, 0), (1.5, 0, 0, 0)])
def test_valeurs_invalides_refusees(args):
    with pytest.raises(ValueError):
        c.cout_appel("claude-haiku-5-5", args[0], args[1], cache_ecriture=args[2], cache_lecture=args[3])


# ---------------------------------------------------------------- JSONL
def jsonl(tmp_path, lignes, nom="u.jsonl"):
    p = tmp_path / nom
    p.write_text("".join((x if isinstance(x, str) else json.dumps(x)) + "\n" for x in lignes), encoding="utf-8")
    return p


def ligne(modele="claude-haiku-5-5", p=1000, s=100, cc=0, cr=0):
    return {"modele": modele, "prompt_tokens": p, "completion_tokens": s, "cache_creation_input_tokens": cc,
            "cache_read_input_tokens": cr, "horodatage": "2026-11-05T08:00:00"}


def test_lire_usage_ok_et_bilan(tmp_path):
    p = jsonl(tmp_path, [ligne(p=10_000, s=100, cc=2000, cr=5000), ligne("anthropic/claude-opus-5-5", p=1000, s=50)])
    appels = c.lire_usage_jsonl(p)
    b = c.bilan(appels)
    assert b["appels"] == 2 and b["jetons_entree"] == 11_000 and b["jetons_sortie"] == 150
    assert b["cache_ecriture"] == 2000 and b["cache_lecture"] == 5000 and b["jetons_non_caches"] == 4000
    attendu = (3000 * 0.10 + 2000 * 0.125 + 5000 * 0.01 + 100 * 0.5) / 1e6 + (1000 * 4 + 50 * 20) / 1e6
    assert b["cout_usd"] == approx(attendu) and b["appels_hauts"] == 0 and b["estime"] is False


def test_lire_usage_format_workbench_sans_champs_cache(tmp_path):
    p = jsonl(tmp_path, [{"modele": "claude-sonnet-5-5", "prompt_tokens": 500, "completion_tokens": 5}])
    (a,) = c.lire_usage_jsonl(p)
    assert a["cache_creation_input_tokens"] == 0 and a["cache_read_input_tokens"] == 0


@pytest.mark.parametrize("contenu", [
    [],  # vide
    ["pas du json"],
    [{"modele": "claude-haiku-5-5", "prompt_tokens": None, "completion_tokens": 3}],
    [{"modele": "claude-haiku-5-5", "prompt_tokens": 5, "completion_tokens": "3"}],
    [{"modele": "claude-haiku-5-5", "prompt_tokens": 5, "completion_tokens": 3, "cache_read_input_tokens": None}],
    [{"prompt_tokens": 5, "completion_tokens": 3}],  # sans modèle
    [[1, 2]],
])
def test_lire_usage_illisible(tmp_path, contenu):
    with pytest.raises(ValueError):
        c.lire_usage_jsonl(jsonl(tmp_path, contenu))


def test_lire_usage_absent_et_modele_inconnu(tmp_path):
    with pytest.raises(ValueError):
        c.lire_usage_jsonl(tmp_path / "absent.jsonl")
    with pytest.raises(c.ModeleInconnu):
        c.bilan(c.lire_usage_jsonl(jsonl(tmp_path, [ligne("gpt-9")])))


def test_ligne_partielle_en_fin_de_fichier_est_illisible(tmp_path):
    p = tmp_path / "u.jsonl"
    p.write_text(json.dumps(ligne()) + "\n" + '{"modele": "claude-haiku', encoding="utf-8")
    with pytest.raises(ValueError):
        c.lire_usage_jsonl(p)


def test_croiser_avec_tau2():
    usage = [ligne(p=100), ligne(p=200)]
    c.croiser(c.normaliser_appels(usage), [(100, 5, False), (200, 5, False)])  # égal : ok
    c.croiser(c.normaliser_appels(usage + [ligne(p=50)]), [(100, 5, False), (200, 5, False)])  # plus de lignes (tentatives) : ok
    with pytest.raises(ValueError):
        c.croiser(c.normaliser_appels(usage[:1]), [(100, 5, False), (200, 5, False)])  # une ligne manque
    with pytest.raises(ValueError):
        c.croiser(c.normaliser_appels([ligne(p=100), ligne(p=10)]), [(100, 5, False), (200, 5, False)])  # jetons manquants


# ---------------------------------------------------------------- callback LiteLLM (faux objet de réponse)
def fausse_reponse(prompt=310, completion=5, cc=100, cr=200, details=False):
    usage = NS(prompt_tokens=prompt, completion_tokens=completion, cache_creation_input_tokens=cc, cache_read_input_tokens=cr)
    if details:
        usage = NS(prompt_tokens=prompt, completion_tokens=completion,
                   prompt_tokens_details=NS(cached_tokens=cr, cache_creation_tokens=cc))
    return NS(usage=usage, choices=[NS(message=NS(content="TEXTE SECRET DE MESSAGE"))])


def test_callback_ecrit_une_ligne_sans_contenu(tmp_path, monkeypatch):
    f = tmp_path / "usage.jsonl"
    monkeypatch.setenv("PILOTE_USAGE_FILE", str(f))
    kw = {"model": "claude-haiku-5-5", "messages": [{"role": "user", "content": "CONTENU PRIVE"}], "api_key": "sk-ant-XYZ"}
    u.callback_succes(kw, fausse_reponse(), None, None)
    (l,) = [json.loads(x) for x in f.read_text().splitlines()]
    assert set(l) == {"modele", "modele_renvoye", "prompt_tokens", "completion_tokens", "cache_creation_input_tokens",
                      "cache_read_input_tokens", "horodatage"}
    assert l["modele_renvoye"] is None  # la fausse réponse n'a pas d'attribut `model`
    assert (l["modele"], l["prompt_tokens"], l["completion_tokens"], l["cache_creation_input_tokens"], l["cache_read_input_tokens"]) \
        == ("claude-haiku-5-5", 310, 5, 100, 200)
    brut = f.read_text()
    assert "CONTENU PRIVE" not in brut and "TEXTE SECRET" not in brut and "sk-ant" not in brut


def test_callback_sans_variable_ne_fait_rien(tmp_path, monkeypatch):
    monkeypatch.delenv("PILOTE_USAGE_FILE", raising=False)
    monkeypatch.chdir(tmp_path)
    u.callback_succes({"model": "m"}, fausse_reponse(), None, None)
    assert list(tmp_path.iterdir()) == []


def test_callback_champs_cache_via_details(tmp_path, monkeypatch):
    f = tmp_path / "usage.jsonl"
    monkeypatch.setenv("PILOTE_USAGE_FILE", str(f))
    u.callback_succes({"model": "claude-opus-5-5"}, fausse_reponse(details=True), None, None)
    l = json.loads(f.read_text())
    assert l["cache_creation_input_tokens"] == 100 and l["cache_read_input_tokens"] == 200


def test_callback_usage_absent_donne_null_et_ne_leve_pas(tmp_path, monkeypatch):
    f = tmp_path / "usage.jsonl"
    monkeypatch.setenv("PILOTE_USAGE_FILE", str(f))
    u.callback_succes({"model": "claude-haiku-5-5"}, NS(usage=None), None, None)
    l = json.loads(f.read_text())
    assert l["prompt_tokens"] is None and l["completion_tokens"] is None
    with pytest.raises(ValueError):  # lu ensuite comme « illisible » : arrêt
        c.lire_usage_jsonl(f)


def test_callback_fichier_non_inscriptible_ne_leve_pas(tmp_path, monkeypatch):
    monkeypatch.setenv("PILOTE_USAGE_FILE", str(tmp_path / "dossier" / "inexistant" / "u.jsonl"))
    u.callback_succes({"model": "m"}, fausse_reponse(), None, None)  # ne doit pas casser l'appel


def test_callback_ecritures_concurrentes(tmp_path, monkeypatch):
    f = tmp_path / "usage.jsonl"
    monkeypatch.setenv("PILOTE_USAGE_FILE", str(f))
    ts = [threading.Thread(target=lambda: [u.callback_succes({"model": "claude-haiku-5-5"}, fausse_reponse(), None, None) for _ in range(25)]) for _ in range(4)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    assert len(c.lire_usage_jsonl(f)) == 100


def test_prompt_tokens_litellm_inclut_le_cache():
    """Contrat vérifié dans litellm/llms/anthropic/chat/transformation.py (calculate_usage) :
    prompt_tokens = input_tokens + cache_creation_input_tokens + cache_read_input_tokens.
    La fonction de coût en dépend : le reste non caché est prompt - écriture - lecture."""
    assert c.cout_appel("claude-sonnet-5-5", 310, 0, cache_ecriture=100, cache_lecture=200)["non_caches"] == 10
