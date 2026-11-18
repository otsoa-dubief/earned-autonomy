"""Rejeu, phase 1 : configuration figée et types de la règle (PLAN_EXPERIENCE.md, 5.2 point 6, 5.3 ; annexes A1, A2).

- q et barres en fractions exactes, recalculées depuis les volumes de banc/TABLE_OUTILS.md ;
- les 24 valeurs du tableau du point 9 (REGLE.md) et les 12 volumes de certification de l'annexe A2 ;
- les formules recopiées de config_e1 redonnent les valeurs d'E1 sur les mélanges d'E1 ;
- le fichier figé se recalcule à l'identique et porte l'empreinte de la table des outils.
"""
import os
import json
from fractions import Fraction

import pytest

import config as C
import config_e1 as E
from rejeu import config_rejeu as CR
from rejeu import types_regle as TY


def test_q_et_barres_exactes_de_l_annexe_A1():
    c = CR.charger_config()
    assert c.q[("aviation", "faible")] == Fraction(3, 49)
    assert c.q[("aviation", "fort")] == Fraction(31, 49)  # 41 écritures d'argent − 10 plafonnées
    assert c.q[("banque", "fort")] == Fraction(47, 364)   # 71 − 30 + 6 garde-fou
    assert c.q[("commerce", "moyen")] == Fraction(22, 60)  # secours : profil service client, rapporté aux écritures
    assert c.q[("WorkBench", "fort")] == Fraction(136, 1000) / Fraction(55, 100)
    assert c.barres[("aviation", "faible")] == Fraction(49, 570)  # « 1/12 » vaut 1/11,63 (M4)
    assert float(1 / c.barres[("aviation", "faible")]) == pytest.approx(11.63, abs=0.01)
    for (env, niv), b in c.barres.items():
        assert b == CR.BUDGET[niv] / (Fraction(95, 100) * 100 * c.q[(env, niv)])
    # avec les plafonnées au numérateur, l'aviation à enjeu fort donnerait 1/15 898 (annexe A1)
    assert round(1 / CR.barre_de_q("fort", Fraction(41, 49))) == 15898


def test_tableau_du_point_9_et_annexe_A2():
    c = CR.charger_config()
    for (env, niv), (un_sur, nt, nr) in CR.TABLE_POINT_9.items():
        b = c.barres[(env, niv)]
        assert round(float(1 / b)) == un_sur, (env, niv)
        assert (c.n_tout[(env, niv)], c.n_regulier[(env, niv)]) == (nt, nr), (env, niv)
        assert CR.n_b_tout(b) + 1 >= 1 / (CR.D_CONSTAT * b)  # N + 1 ≥ 1 ÷ (d × barre)
    for env, valeurs in CR.TABLE_A2.items():
        assert tuple(CR.certification(c.barres[(env, n)]) for n in CR.NIVEAUX) == valeurs


def test_formules_recopiees_egales_a_celles_d_E1():
    for m in E.MELANGES:
        for n in E.NIVEAUX:
            b = E.BARRES[(m, n)]
            assert CR.n_b_tout(b) == E.N_B_TOUT[(m, n)] == E.n_b_tout(m, n)
            assert CR.n_b_regulier(b) == E.N_B_REGULIER[(m, n)] == E.n_b_regulier(m, n)
            assert CR.certification(b) == E.certification(m, n)
    assert CR.n_allonge is E.n_allonge


def test_fichier_fige_recalcule_et_empreinte_de_la_table(tmp_path):
    c = CR.charger_config()
    assert c.brut["table_outils_sha256"] == CR.sha256_fichier(CR.CHEMIN_TABLE_OUTILS)
    if c.G0 is None:   # avant le gel
        assert c.graine_maitresse() == CR.G0_DEVELOPPEMENT
    else:              # après le gel : G0 tirée une fois, entier 64 bits égal à la valeur écrite au plan (5.5, point 4)
        import re
        plan = open(os.path.join(os.path.dirname(CR.CHEMIN_CONFIG), "..", "..", "PLAN_EXPERIENCE.md"),
                    encoding="utf-8").read()
        ecrites = re.findall(r"^\s*- valeur tirée au gel : G0 = (\d+)\s*$", plan, flags=re.M)
        assert isinstance(c.G0, int) and 0 <= c.G0 < 2 ** 64 and ecrites == [str(c.G0)]
        assert c.graine_maitresse() == c.G0
    assert c.graine_maitresse(7) == 7
    assert (c.R0, c.B, c.K) == (2000, 2000, 10)
    assert c.valeurs_e == (0.05, 0.0, 0.02, 0.10)
    # une configuration retouchée à la main est refusée
    brut = json.loads(open(CR.CHEMIN_CONFIG, encoding="utf-8").read())
    brut["barres"]["aviation"]["faible"] = "1/12"
    faux = tmp_path / "config.json"
    faux.write_text(json.dumps(brut), encoding="utf-8")
    with pytest.raises(CR.ConfigInvalide):
        CR.charger_config(str(faux))
    # une table des outils différente est refusée (q et barres à recalculer, 5.2 point 6)
    autre = tmp_path / "table.json"
    autre.write_text("{}", encoding="utf-8")
    with pytest.raises(CR.ConfigInvalide):
        CR.charger_config(chemin_table=str(autre))


def test_types_parametres_de_5_3():
    assert TY.SIGLES[:7] == tuple(C.TYPES[:7])  # codes communs avec E1 (LEC … ARG)
    for k in range(7):
        assert TY.ENJEU[k] == C.ENJEU[k]
    assert TY.SIGLES[7:] == ("GAR", "ILL")
    assert TY.ENJEU[TY.GAR] == TY.ENJEU[TY.ILL] == TY.FORT
    assert not TY.A_PALIER2[TY.GAR] and not TY.A_PALIER2[TY.ILL]
    assert list(np_where(TY.A_PALIER2)) == [TY.ECR, TY.EXE]   # palier 2 : types réversibles
    assert TY.TYPES_SUITE == (1, 2, 3, 4, 5, 6, 7, 8)          # LEC n'entre jamais dans une suite
    assert TY.ENJEU_HAUT.tolist() == [False, False, True, True, False, True, True, True, True]
    assert TY.code_type("garde-fou ou droits") == TY.GAR and TY.code_type("effet illisible") == TY.ILL
    with pytest.raises(KeyError):
        TY.code_type("doute")


def np_where(m):
    return [i for i, x in enumerate(m) if x]
