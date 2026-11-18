"""Mesure des cellules de 2 à 5 tâches porteuses (`porteuses/porteuses.py`, méthode : `porteuses/METHODE.md`) :
valeur vraie au budget, cellule à une tâche jamais établie, graines et cases de la méthode."""
import importlib.util
import os

import numpy as np


def _module():
    chemin = os.path.join(os.path.dirname(__file__), "..", "porteuses", "porteuses.py")
    spec = importlib.util.spec_from_file_location("porteuses", chemin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_cases_et_graine_de_la_methode():
    P = _module()
    cs = P.cases()
    niveau = [c for c in cs if c["multiple"] == 1.0]
    assert len(niveau) == 40 and all(c["tirages"] == 10_000 for c in niveau)
    assert {(c["k"], c["rho"], c["tailles"]) for c in niveau} == {(k, r, t) for k in (1, 2, 3, 4, 5)
                                                                   for r in (0.0, 0.3, 0.7, 1.0)
                                                                   for t in ("égales", "inégales")}
    assert len([c for c in cs if c["multiple"] != 1.0]) == 8
    assert P.GRAINE == 2026110704 and P.B == 2000 and P.G == 20 and P.N_CELLULES == 11


def test_valeur_vraie_au_budget():
    """L'espérance de la grandeur vaut le budget fois le multiple (moyenne sur 4 000 tirages, à 5 % près)."""
    P = _module()
    rng = np.random.default_rng(1)
    for k, rho, mult in ((3, 0.3, 1.0), (2, 0.0, 5.0)):
        v = [P.estimation(rng, k, rho, "inégales", mult).mean() for _ in range(4000)]
        assert abs(np.mean(v) / (mult * P.BUDGET) - 1) < 0.05


def test_une_seule_tache_jamais_etablie_et_bootstrap_sans_nan():
    P = _module()
    rng = np.random.default_rng(2)
    for _ in range(30):
        etabli, testables = P.un_tirage(rng, 1, 1.0, "égales", 5.0)
        assert not etabli and testables == 0
    etabli, testables = P.un_tirage(np.random.default_rng(3), 4, 0.3, "égales", 1.0)
    assert 0 <= testables <= P.N_CELLULES     # une cellule sans erreur ne varie pas : non testable


def test_mesure_refaite_avec_un_suffixe():
    """Mesure refaite avec le moteur du septième passage du contrôle 3 (max-T recentré, 08/11) : mêmes graines et mêmes
    cases, autres fichiers ; la première mesure reste en place."""
    P = _module()
    P.chemins("v7")
    assert [os.path.basename(c) for c in (P.SORTIE, P.META, P.RESUME)] == ["porteuses_v7.csv", "meta_v7.json",
                                                                           "porteuses_v7.md"]
    P.chemins("")
    assert [os.path.basename(c) for c in (P.SORTIE, P.META, P.RESUME)] == ["porteuses.csv", "meta.json",
                                                                           "porteuses.md"]
