"""Rejeu d'une configuration (PLAN_EXPERIENCE.md, 5.5 à 5.9 et 5.12), couche R0 ; préparation de la couche bootstrap.

`rejouer_suite` fait tourner, sur une suite déjà construite, les quatre règles (B-tout en principal ; B-régulier, A½,
A¼) et tous les témoins de 5.7, sur les mêmes tirages, puis calcule les mesures de base. `rejouer_configuration`
construit G(c, S) et la couche R0 ; `rejouer_bootstrap` une répétition bootstrap (tirage des tâches par strate, K
ordres), sans intervalle (phase 2).

Quantités calibrées fixes (5.5, point 7) : les classes de l'oracle viennent du jeu de calibration entier, celles de
l'oracle rétrospectif du jeu rejoué entier ; elles ne changent pas d'une répétition à l'autre. Le hasard apparié
copie la part de la règle sur la même suite (moyenne de ses colonnes : les R0 répétitions, ou les K ordres d'une
répétition bootstrap).

Points d'accroche de la phase 2 : scénarios (`moteur.simuler(jonction=…)`, 5.10), tests de résistance (transformations
des tableaux de la suite, et constat différé dans le moteur, 5.11), intervalles et max-T (5.13), règle de décision et
étiquettes (5.14), sorties (5.15).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from . import classes as CL
from . import epreuves as EP
from . import mesures as ME
from . import moteur as MO
from . import regles as RG
from . import suites as SU
from . import temoins as TM


@dataclass
class ResultatSuite:
    suite: SU.Suite
    moteur: MO.ResultatMoteur
    temoins: MO.Compteur
    noms_temoins: list
    valeurs_e: tuple
    classes_calibration: Optional[dict]
    classes_retro: Optional[dict]
    P_temoins: Optional[dict] = None
    mesures: dict = field(default_factory=dict)

    def agregats(self, nom: str) -> dict:
        """Agrégats par ligne d'une règle ou d'un témoin."""
        noms_regles = [r.nom for r in self.moteur.regles]
        if nom in noms_regles:
            return self.moteur.cpt.lignes(self.moteur.lignes(noms_regles.index(nom)))
        i = self.noms_temoins.index(nom)
        R = self.suite.R
        return self.temoins.lignes(slice(i * R, (i + 1) * R))

    @property
    def noms(self) -> list:
        return [r.nom for r in self.moteur.regles] + list(self.noms_temoins)


def rejouer_suite(suite: SU.Suite, pool: EP.PoolEpreuves, regles: list, valeurs_e, classes_calibration=None,
                  classes_retro=None, journal: bool = False, garder_P: bool = False, fournisseur=None) -> ResultatSuite:
    """Règles et témoins sur une suite (mêmes tirages), puis mesures de base."""
    fournisseur = fournisseur or EP.FournisseurParties(pool, suite.cles_epreuves)
    res = MO.simuler(suite, regles, fournisseur, valeurs_e, journal=journal, garder_P=garder_P)
    Ps = {nom: TM.paliers_fixes(nom, suite) for nom in TM.NOMS_FIXES}
    Ps["trois_reussites"] = TM.paliers_trois_reussites(suite)
    u = TM.tirages_hasard(suite)
    for i, r in enumerate(regles):
        f3, f23 = TM.parts_regle(res.cpt.comptes[res.lignes(i)])
        Ps[f"hasard_{r.nom}"] = TM.paliers_hasard(suite, f3, f23, u)
    if classes_calibration is not None:
        Ps["oracle_p2"] = TM.paliers_oracle(suite, classes_calibration)
    if classes_retro is not None:
        Ps["oracle_retro"] = TM.paliers_oracle(suite, classes_retro)
    noms_t = list(Ps)
    cpt_t = MO.compter_paliers(np.concatenate([Ps[n] for n in noms_t], axis=1), suite, valeurs_e) if noms_t else \
        MO.Compteur(0, valeurs_e)
    out = ResultatSuite(suite, res, cpt_t, noms_t, tuple(valeurs_e), classes_calibration, classes_retro,
                        Ps if garder_P else None)
    out.mesures = mesurer(out)
    return out


def mesurer(rs: ResultatSuite) -> dict:
    """Mesures de base de toutes les règles et de tous les témoins (5.12, phase 1)."""
    env = rs.suite.meta.get("environnement", "")
    tables = dict(degats=[], charges=[], autonomie=[])
    par_rep = {}
    m = rs.moteur
    for i, r in enumerate(m.regles):
        sl = m.lignes(i)
        ep = {k: getattr(m, k)[sl] for k in ("ep_ouvertes", "ep_tentatives", "ep_reussies", "ep_ratees",
                                             "ep_impossibles", "ep_validations")}
        prom = {k: getattr(m, k)[sl] for k in ("n_prom3", "n_retraits3", "volume3")}
        lg = ME.lignes_groupe(r.nom, "règle", m.cpt.lignes(sl), rs.suite, rs.valeurs_e, env, ep, prom)
        par_rep[r.nom] = lg.pop("par_repetition")
        for k in tables:
            tables[k] += lg[k]
    for nom in rs.noms_temoins:
        lg = ME.lignes_groupe(nom, "témoin", rs.agregats(nom), rs.suite, rs.valeurs_e, env)
        par_rep[nom] = lg.pop("par_repetition")
        for k in tables:
            tables[k] += lg[k]
    tables["par_repetition"] = par_rep
    return tables


@dataclass
class Configuration:
    """Ce qui ne dépend pas de la répétition : G(c, S), vivier des épreuves, règles, classes calibrées."""
    jeu: SU.JeuConfiguration
    pool: EP.PoolEpreuves
    regles: list
    classes_calibration: Optional[dict]
    classes_retro: dict
    G0: int
    valeurs_e: tuple


def preparer_configuration(preparees: dict, entrees, config, environnement: str, modele: str, taches,
                           jeu: str = "confirmation", taches_calibration=None, noms_regles=RG.NOMS_REGLES,
                           G0: Optional[int] = None, valeurs_e=None, regles=None) -> Configuration:
    jc = SU.jeu_configuration(preparees, entrees, environnement, modele, taches, jeu)
    cl_cal = None
    if taches_calibration is not None:
        jcal = SU.jeu_configuration(preparees, entrees, environnement, modele, taches_calibration, "calibration")
        cl_cal = CL.classes_jeu(jcal, config)
    return Configuration(jeu=jc, pool=EP.PoolEpreuves(jc),
                         regles=regles if regles is not None else RG.regles(environnement, config, noms_regles),
                         classes_calibration=cl_cal, classes_retro=CL.classes_jeu(jc, config),
                         G0=config.graine_maitresse(G0),
                         valeurs_e=tuple(valeurs_e) if valeurs_e is not None else config.valeurs_e)


def rejouer_configuration(preparees: dict, entrees, config, environnement: str, modele: str, taches, R: int = None,
                          journal: bool = False, garder_P: bool = False, **kw) -> ResultatSuite:
    """Couche R0 (valeur centrale) d'une configuration sur un jeu de tâches."""
    cf = preparer_configuration(preparees, entrees, config, environnement, modele, taches, **kw)
    suite = SU.suite_r0(cf.jeu, cf.G0, config.R0 if R is None else R)
    return rejouer_suite(suite, cf.pool, cf.regles, cf.valeurs_e, cf.classes_calibration, cf.classes_retro,
                         journal=journal, garder_P=garder_P)


def rejouer_bootstrap(cf: Configuration, b: int, K: int, journal: bool = False) -> ResultatSuite:
    """Répétition bootstrap b : tâches tirées avec remise par strate, K ordres ; variantes d'épreuve tirées dans G(c, S)
    d'origine (5.9, M7) ; quantités calibrées fixes (5.5, point 7). Sans intervalle (phase 2)."""
    suite = SU.suite_bootstrap(cf.jeu, cf.G0, b, K)
    return rejouer_suite(suite, cf.pool, cf.regles, cf.valeurs_e, cf.classes_calibration, cf.classes_retro,
                         journal=journal)


# --------------------------------------------------------------------------
# Déterminisme (5.16, point 7)
# --------------------------------------------------------------------------
def _maj(h, nom: str, x) -> None:
    a = np.ascontiguousarray(np.asarray(x))
    h.update(f"{nom}|{a.dtype.str}|{a.shape}|".encode())
    h.update(a.tobytes())


def empreinte(rs: ResultatSuite) -> str:
    """SHA-256 des sorties d'un rejeu : agrégats, épreuves, promotions, et mesures."""
    h = hashlib.sha256()
    m = rs.moteur
    for cpt, nom in ((m.cpt, "regles"), (rs.temoins, "temoins")):
        for a in ("exc", "dmg", "cor", "exc_part", "val", "inv3", "comptes"):
            _maj(h, f"{nom}.{a}", getattr(cpt, a))
    for a in ("ep_ouvertes", "ep_tentatives", "ep_reussies", "ep_ratees", "ep_impossibles", "ep_validations",
              "n_prom3", "n_retraits3", "premier3", "volume3", "pal_final"):
        _maj(h, a, getattr(m, a))
    _maj(h, "suite.typ", rs.suite.typ)
    _maj(h, "suite.u_val", rs.suite.u_val)
    mes = {k: v for k, v in rs.mesures.items() if k != "par_repetition"}
    h.update(json.dumps(mes, sort_keys=True, ensure_ascii=False, default=repr).encode())
    return h.hexdigest()
