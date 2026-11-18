"""Mesure du niveau du max-T (`maxt_niveau/maxt_niveau.py`, méthode : `maxt_niveau/METHODE.md`) : les cinq formules sur
des cas construits, avant tout calcul sur le moteur."""
import importlib.util
import os

import numpy as np
import pytest


def _module():
    chemin = os.path.join(os.path.dirname(__file__), "..", "maxt_niveau", "maxt_niveau.py")
    spec = importlib.util.spec_from_file_location("maxt_niveau", chemin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cas(decalage, rng, B=4000):
    """Une cellule : estimation 1, budget 0,9 (un écart type sous l'estimation) ; répétitions décalées."""
    boot = rng.normal(1.0 + decalage, 0.1, size=(B, 1))
    return np.array([1.0]), boot, np.array([0.9]), np.array([5])


def test_f0_et_f1_concordent_quand_le_bootstrap_est_centre():
    MN = _module()
    rng = np.random.default_rng(1)
    est, boot, bud, por = _cas(0.0, rng)
    boot = boot - boot.mean() + 1.0
    assert MN.formule("F0", est, boot, bud, por).tolist() == MN.formule("F1", est, boot, bud, por).tolist()


def test_f1_corrige_un_bootstrap_decentre_vers_le_bas():
    """Répétitions décalées de deux écarts types vers le bas : F0 établit à tort (c* négatif), F1 non."""
    MN = _module()
    est, boot, bud, por = _cas(-0.2, np.random.default_rng(2))
    assert MN.formule("F0", est, boot, bud, por)[0]
    assert not MN.formule("F1", est, boot, bud, por)[0]
    assert not MN.formule("F3", est, boot, bud, por)[0]


def test_f3_plus_prudente_que_f1():
    """Estimation 1,9 écart type au-dessus du budget : établie à 95 % (1,645), pas à 97,5 % (1,96)."""
    MN = _module()
    rng = np.random.default_rng(3)
    boot = rng.normal(1.0, 0.1, size=(20000, 1))
    est, bud, por = np.array([1.0]), np.array([1.0 - 0.19]), np.array([5])
    assert MN.formule("F1", est, boot, bud, por)[0] and not MN.formule("F3", est, boot, bud, por)[0]


def test_f2_bootstrap_t_et_f4_jackknife():
    MN = _module()
    rng = np.random.default_rng(4)
    boot = rng.normal(1.0, 0.1, size=(4000, 1))
    se_boot = np.full((4000, 1), 0.1)
    est, por = np.array([1.0]), np.array([5])
    assert MN.formule("F2", est, boot, np.array([0.7]), por, se=np.array([0.1]), se_boot=se_boot)[0]
    assert not MN.formule("F2", est, boot, np.array([0.9]), por, se=np.array([0.1]), se_boot=se_boot)[0]
    jack = [1.0 + rng.normal(0, 0.1 / np.sqrt(49), size=50)]         # écart type jackknife d'environ 0,1
    g = [[0]]
    assert MN.formule("F4", est, boot, np.array([0.7]), por, jack=jack, groupes=g, rng=np.random.default_rng(5))[0]
    assert not MN.formule("F4", est, boot, np.array([0.95]), por, jack=jack, groupes=g,
                          rng=np.random.default_rng(5))[0]


@pytest.mark.parametrize("nom", ["F0", "F1", "F2", "F3", "F4"])
def test_cellule_a_une_tache_jamais_etablie(nom):
    MN = _module()
    rng = np.random.default_rng(6)
    boot = rng.normal(5.0, 0.01, size=(1000, 1))
    r = MN.formule(nom, np.array([5.0]), boot, np.array([1.0]), np.array([1]), se=np.array([0.01]),
                   se_boot=np.full((1000, 1), 0.01), jack=[5.0 + rng.normal(0, 0.001, 30)], groupes=[[0]],
                   rng=np.random.default_rng(7))
    assert not r[0]


def test_regimes_et_graine_de_la_methode():
    MN = _module()
    assert MN.GRAINE == 2026110705 and MN.FORMULES == ("F0", "F1", "F2", "F3", "F4")
    assert [(r[0], r[2], r[3]) for r in MN.REGIMES] == [("N1", 200, True), ("N2", 100, True), ("P2", 120, False),
                                                        ("P1", 60, False), ("P4", 30, False)]


# --------------------------------------------------------------------------
# Mesure de confirmation dans N1 (`maxt_niveau/CONFIRMATION.md`, écrite avant le calcul)
# --------------------------------------------------------------------------
def _confirmation():
    import sys
    dossier = os.path.join(os.path.dirname(__file__), "..", "maxt_niveau")
    sys.path.insert(0, os.path.abspath(dossier))
    chemin = os.path.join(dossier, "confirmation.py")
    spec = importlib.util.spec_from_file_location("confirmation", chemin)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_confirmation_tirages_neufs_et_independants():
    C = _confirmation()
    assert (C.RANG, C.REPETITIONS, C.MONDE) == (10, 400, "A")
    assert C.RANG not in range(len(C.MN.REGIMES))           # rangs 0 à 4 : régimes de la mesure
    t = C.taches()
    assert len(t) == 400 and t[0] == ("N1c", 10, "A", 0) and t[-1][3] == 399


def test_confirmation_cumul_des_tirages():
    """F1 : mesure (10/200), deux tirages antérieurs (15/200 chacun) et tirage neuf ; F3 : mesure et tirage neuf."""
    C = _confirmation()
    mesure = {"F0": (31, 200), "F1": (10, 200), "F2": (30, 200), "F3": (6, 200), "F4": (18, 200)}
    nouveaux = {fo: (20, 400) for fo in C.MN.FORMULES}
    l = {x["formule"]: x for x in C.cumuls(nouveaux, mesure)}
    assert (l["F1"]["rejets_cumul"], l["F1"]["n_cumul"]) == (60, 1000)
    assert (l["F0"]["rejets_cumul"], l["F0"]["n_cumul"]) == (130, 1000)
    assert (l["F3"]["rejets_cumul"], l["F3"]["n_cumul"]) == (26, 600)
    assert l["F1"]["part"] == pytest.approx(0.05) and l["F3"]["part_cumul"] == pytest.approx(26 / 600)
    assert l["F1"]["cumul_wilson_bas"] < 0.06 < l["F1"]["cumul_wilson_haut"]


def test_confirmation_refuse_un_nom_egal_a_la_casse_pres(tmp_path, monkeypatch):
    """La sortie ne doit jamais écraser `CONFIRMATION.md` (disque insensible à la casse)."""
    C = _confirmation()
    monkeypatch.setattr(C, "ICI", str(tmp_path))
    (tmp_path / "CONFIRMATION.md").write_text("méthode", encoding="utf-8")
    with pytest.raises(RuntimeError):
        C.ecrire_sortie("confirmation.md", "x")
    assert (tmp_path / "CONFIRMATION.md").read_text(encoding="utf-8") == "méthode"
    C.ecrire_sortie("confirmation_resultats.md", "ok")
    assert (tmp_path / "confirmation_resultats.md").read_text(encoding="utf-8") == "ok"
