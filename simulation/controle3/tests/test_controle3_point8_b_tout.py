"""Contrôle 3, test manquant de 5.16, point 8, depuis Q13 : le max-T décide aussi le budget de B-tout (5.14, point 1).

Le test du moteur porte sur des cellules synthétiques du module `maxt` (`test_rejeu_maxt.py`). Depuis Q13, le même
max-T s'applique aux cellules de B-tout produites par le rejeu : ici, par toute la chaîne (preuves, suites, rejeu,
bootstrap par grappes, `decision.point1`), sur des entrées faites à la main :
(i) un dépassement planté (B-tout avec N = 1, agent fautif) est établi : point 1 non tenu ;
(ii) sans dépassement (B-tout figée, agent sans erreur dans la confirmation), rien n'est établi ;
(iii) une cellule où B-tout n'atteint jamais le palier 3 est « tenue, non mise à l'épreuve » et reste hors de m.
La fréquence des dépassements établis à tort, aux volumes de l'expérience, est mesurée par les mondes A et D
(RAPPORT.md).
"""
import numpy as np
import pytest

from aide_controle3 import entrees_main, erreurs_aleatoires, taches_wb
from rejeu import analyse as AN
from rejeu import config_rejeu as CR
from rejeu import decision as DE
from rejeu import pipeline as PL
from rejeu import preuves as PR
from rejeu import regles as RG
from rejeu import types_regle as TY

H, S, O = CR.MODELES
ENV = "WorkBench"


def analyse(erreurs_conf_haiku: float, N: int, graine: int = 3):
    rng = np.random.default_rng(graine)
    taches = taches_wb(120)
    cal, conf = taches[:60], taches[60:]
    specs = {H: dict(passages=5, taches=taches, erreurs=erreurs_aleatoires(rng, conf, 5, erreurs_conf_haiku)),
             S: dict(passages=1, taches=taches, erreurs=set()), O: dict(passages=1, taches=taches, erreurs=set())}
    e = entrees_main(ENV, specs)
    prep = PR.preparer(e)
    cfg = CR.charger_config()
    r = RG.regle("B-tout", ENV, cfg)
    regles = {ENV: [RG.variante(r, "B-tout", N=np.where(TY.MERITE, N, 0))]}
    reg = AN.Reglages(G0=11, R0=20, B=80, K=2, tranche=40, valeurs_e=(0.05,), noms_regles=("B-tout",),
                      choix=dict(methode="iii", repli=False, G_sur=20, methode_seconde="percentile"))
    an = PL.analyser(e, prep, cfg, reg, {ENV: conf}, {ENV: cal}, scenarios=False, regles_imposees=regles)
    return an, DE.point1(an)


def test_depassement_plante_dans_une_cellule_de_b_tout_est_etabli():
    an, p1 = analyse(0.10, N=1)
    assert not p1["tenu"]
    etab = {(c["famille"], c["niveau"]) for c in p1["echecs"]}
    assert (("config", ENV, H), "faible") in etab
    c = next(c for c in p1["cellules"] if c["famille"] == ("config", ENV, H) and c["niveau"] == "faible")
    assert c["centre"] > 5 * c["budget"] and c["borne_maxt"] > c["budget"]


def test_sans_depassement_rien_n_est_etabli():
    an, p1 = analyse(0.0, N=int(CR.charger_config().n_tout[(ENV, "faible")]))
    assert p1["tenu"] and not p1["echecs"]
    jug = [c for c in p1["cellules"] if c["statut"] == DE.JUGEE]
    assert all(c["centre"] == 0 for c in jug)


def test_cellule_jamais_au_palier_3_hors_de_m():
    an, p1 = analyse(0.10, N=10_000)
    assert p1["tenu"]
    assert all(c["statut"] in (DE.SANS_OBJET, DE.NON_EPROUVEE) for c in p1["cellules"])
    assert not any("etabli" in c for c in p1["cellules"])
