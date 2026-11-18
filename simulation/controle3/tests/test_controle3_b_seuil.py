"""Monde B-seuil, seconde mesure (`b_seuil/seconde_mesure.py`, méthode : `b_seuil/METHODE.md`, section 4) : même monde
que B-seuil à la dérive près, et même chemin de calcul que `harnais.repetition`."""
import dataclasses
import importlib.util
import os

from controle3 import harnais as HA
from controle3 import mondes as MD


def _seconde_mesure():
    chemin = os.path.join(os.path.dirname(__file__), "..", "b_seuil", "seconde_mesure.py")
    spec = importlib.util.spec_from_file_location("seconde_mesure", chemin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_monde_de_la_seconde_mesure():
    SM = _seconde_mesure()
    m, base = SM.monde(), MD.MONDES_PAR_NOM["B-seuil"]
    assert m.nom == "B-seuil-bis" and m.melange == (("commerce", "ECR", 1.40),)
    assert dataclasses.replace(m, nom=base.nom, melange=base.melange) == base
    assert SM.GRAINE not in (2026110503, 2026110701, 2026110702) and SM.REPETITIONS == 120


def test_seconde_mesure_suit_le_chemin_du_harnais():
    """En petit (R0 = 4, B = 6, K = 2), sur le monde B-seuil et la graine du contrôle 3 : mêmes sorties que
    `harnais.repetition`, plus toutes les cellules du commerce à enjeu faible (configurations et scénarios)."""
    SM = _seconde_mesure()
    p = HA.Parametres(R0=4, B=6, K=2, tranche=6, graine=7)
    m = MD.MONDES_PAR_NOM["B-seuil"]
    a = HA.repetition("B-seuil", 0, p)
    b = SM.une_repetition(m, HA.graine_repetition(p, m, 0), p)
    for k in ("etiquette", "etiquette_principale", "mention", "p0", "p1", "p3", "p4", "G0", "volumes"):
        assert a[k] == b[k], k
    cel = b["cellules_commerce_faible"]
    assert cel and all(c["famille"].split("/")[1] == "commerce" for c in cel)
    assert {c["famille"].split("/")[0] for c in cel} == {"config", "scenario"}
    conf = {"/".join(c["famille"].split("/")[1:]) + "/faible": c["centre"] / c["budget"]
            for c in cel if c["statut"] == "jugée" and c["famille"].startswith("config/")}
    attendu = {k: v for k, v in a["p1"]["centres_config"].items() if k.startswith("commerce/") and k.endswith("/faible")}
    assert conf.keys() == attendu.keys()
    assert all(abs(conf[k] - attendu[k]) < 1e-9 for k in conf)
