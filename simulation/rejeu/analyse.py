"""Analyse du rejeu, phase 2 : valeur centrale, bootstrap par grappes, jackknife et intervalles de chaque quantité
(PLAN_EXPERIENCE.md, 5.5 à 5.13).

Une analyse rejoue un jeu de tâches (la confirmation, ou une autre moitié pour l'échange des rôles, ou toute la
réserve) avec les quantités calibrées d'un autre jeu (5.5, point 7 : fixes dans toutes les répétitions) :
1. pour chaque configuration (modèle, environnement) : couche R0 (valeur centrale, tables descriptives, écart type
   d'origine du bootstrap-t), jackknife (une tâche retirée des K premiers ordres), bootstrap par tranches de
   répétitions (valeurs et écarts types par répétition) ;
2. pour chaque scénario (environnement, X, Y), dans les deux modes : les mêmes couches (5.10) ;
3. les moyennes à poids égaux sur les configurations délégables (5.13), répétition par répétition, avec leur écart
   type linéarisé (les configurations d'un environnement partagent le tirage des tâches) ;
4. les intervalles : la méthode retenue par la simulation de couverture, la seconde méthode de « fragile », et la
   relance des cellules indécises de B-tout (4 fois plus de répétitions et d'ordres, 5.13).

Une quantité sans écart type linéarisé (proportions de la garantie, fenêtre après la jonction, charge avec épreuves)
prend l'intervalle (i) quand la méthode retenue est le bootstrap-t (CHOIX_PHASE2.md).
"""
from __future__ import annotations

import math
import warnings
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from . import classes as CL
from . import config_rejeu as CR
from . import epreuves as EP
from . import intervalles as IC
from . import lots as LO
from . import mesures as ME
from . import moteur as MO
from . import preuves as PR
from . import regles as RG
from . import suites as SU
from . import temoins as TM
from . import types_regle as TY

TEMOINS_DIFF = ("liste_fixe", "tri_risque", "tout_valider", "oracle_p2", "oracle_retro", "trois_reussites",
                "tout_approuver")
TEMOINS_REUSSITE = ("liste_fixe", "tri_risque")   # critère 2 (décision 3, Q6)
NIVEAUX = TY.NIVEAUX


# ==========================================================================
# Réglages et contexte
# ==========================================================================
@dataclass
class Reglages:
    G0: int
    R0: int = CR.R0
    B: int = CR.B
    K: int = CR.K
    tranche: int = 200                 # répétitions bootstrap rejouées ensemble
    valeurs_e: tuple = (CR.E_PRINCIPAL,) + CR.E_COMPLEMENTS
    choix: dict = field(default_factory=lambda: dict(methode="ii", repli=False, G_sur=0, methode_seconde="iii"))
    noms_regles: tuple = RG.NOMS_REGLES

    @property
    def e_principal(self) -> float:
        return float(self.valeurs_e[0])


def palier_par_type(classes: Optional[dict]) -> np.ndarray:
    """Oracle avec palier 2 (5.7) : palier 3 si le taux estimé est au plus la barre (Q14, Otsoa, 06/11 ; le classement
    prouvé reste publié) ; sinon palier 2 si réversible, palier 1 sinon."""
    pal = np.ones(TY.NT, dtype=np.int8)
    for k in TY.TYPES_SUITE:
        c = (classes or {}).get(k)
        pal[k] = 3 if (c and CL.estime_sous(c)) else (2 if TY.A_PALIER2[k] else 1)
    return pal


def paliers_oracle_segments(suite, classes_av, classes_ap=None) -> np.ndarray:
    """Oracle d'une suite ; dans un scénario, il passe des classes de X à celles de Y à la jonction (5.10)."""
    k = np.where(suite.typ >= 0, suite.typ, 0)
    pav = palier_par_type(classes_av)
    if suite.jonction is None or classes_ap is None:
        return TM._finir(pav[k], suite)
    apres = np.arange(suite.T)[:, None] >= np.asarray(suite.jonction)[None, :]
    return TM._finir(np.where(apres, palier_par_type(classes_ap)[k], pav[k]), suite)


def paliers_hasard_groupes(suite, comptes_regle, groupe, n_groupes, u) -> np.ndarray:
    """Hasard apparié : chaque type passe au hasard la même part de ses écritures non plafonnées aux paliers 2 et 3
    que la règle sur le même groupe de colonnes (R0 : toutes ; bootstrap : les K ordres d'une répétition ; jackknife :
    les K ordres sans la tâche) (5.5, point 7 ; 5.7)."""
    cg = np.zeros((n_groupes, TY.NT, 3))
    np.add.at(cg, np.asarray(groupe), comptes_regle)
    tot = cg.sum(axis=2)
    tot[tot == 0] = 1.0
    f3, f23 = cg[:, :, 2] / tot, (cg[:, :, 2] + cg[:, :, 1]) / tot
    k = np.where(suite.typ >= 0, suite.typ, 0)
    g = np.asarray(groupe)[None, :]
    P = np.where(u < f3[g, k], 3, np.where(u < f23[g, k], 2, 1))
    return TM._finir(P, suite)


# ==========================================================================
# Rejeu d'un lot : règles et témoins
# ==========================================================================
@dataclass
class ResultatLot:
    lot: LO.Lot
    moteur: MO.ResultatMoteur
    temoins: MO.Compteur
    noms_temoins: list
    regles: list

    @property
    def noms(self) -> list:
        return [r.nom for r in self.regles] + list(self.noms_temoins)

    def cpt_et_v(self, nom: str):
        noms_r = [r.nom for r in self.regles]
        if nom in noms_r:
            return self.moteur.cpt, noms_r.index(nom), True
        return self.temoins, self.noms_temoins.index(nom), False

    def agregats(self, nom: str) -> dict:
        cpt, v, _ = self.cpt_et_v(nom)
        R = self.lot.suite.R
        return cpt.lignes(slice(v * R, (v + 1) * R))

    def epreuves(self, nom: str) -> Optional[dict]:
        cpt, v, regle = self.cpt_et_v(nom)
        if not regle:
            return None
        sl = self.moteur.lignes(v)
        return {k: getattr(self.moteur, k)[sl] for k in ("ep_ouvertes", "ep_tentatives", "ep_reussies", "ep_ratees",
                                                          "ep_impossibles", "ep_validations")}


def rejouer_lot(lot: LO.Lot, regles: list, valeurs_e, fournisseur, classes=(None, None), retro=(None, None),
                annonce: bool = False, retard: int = 0, grappes: bool = True, journal: bool = False,
                garder_P: bool = False) -> ResultatLot:
    """Règles et témoins sur les colonnes d'un lot (mêmes tirages pour tous)."""
    s = lot.suite
    gr = lot.grappes_moteur() if grappes else None
    res = MO.simuler(s, regles, fournisseur, valeurs_e, journal=journal, garder_P=garder_P, jonction=s.jonction,
                     annonce=annonce, retard=retard, grappes=gr)
    Ps = {nom: TM.paliers_fixes(nom, s) for nom in TM.NOMS_FIXES}
    Ps["trois_reussites"] = TM.paliers_trois_reussites(s)
    u = TM.tirages_hasard(s)
    for i, r in enumerate(regles):
        Ps[f"hasard_{r.nom}"] = paliers_hasard_groupes(s, res.cpt.comptes[res.lignes(i)], lot.groupe, lot.n_groupes, u)
    Ps["oracle_p2"] = paliers_oracle_segments(s, classes[0], classes[1])
    Ps["oracle_retro"] = paliers_oracle_segments(s, retro[0], retro[1])
    noms = list(Ps)
    cpt = MO.compter_paliers(np.concatenate([Ps[n] for n in noms], axis=1), s, valeurs_e, grappes=gr)
    out = ResultatLot(lot, res, cpt, noms, list(regles))
    if garder_P:
        out.P_temoins = Ps
    return out


# ==========================================================================
# Valeurs par groupe et écarts types linéarisés
# ==========================================================================
def _moy_groupes(x, ng: int) -> np.ndarray:
    """Moyenne par groupe sur le dernier axe (colonnes rangées groupe par groupe, autant par groupe)."""
    x = np.asarray(x, dtype=float)
    sh = x.shape[:-1] + (ng, x.shape[-1] // ng)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmean(x.reshape(sh), axis=-1)


def den_fenetre(suite) -> np.ndarray:
    """Écritures au dénominateur du second segment, par colonne."""
    apres = np.arange(suite.T)[:, None] >= np.asarray(suite.jonction)[None, :]
    return (suite.den & apres).sum(axis=0)


def valeurs_groupes(rl: ResultatLot, nom: str) -> dict:
    """Valeurs d'une règle ou d'un témoin, par groupe : budget (E, 3, ng), charge (E, ng), etc."""
    s, ng = rl.lot.suite, rl.lot.n_groupes
    agr = rl.agregats(nom)
    ep = rl.epreuves(nom)
    pr = ME.par_repetition(agr, s, ep)
    out = dict(budget=_moy_groupes(np.moveaxis(pr["exces_100_ecritures"], 1, -1), ng),
               budget_actions=_moy_groupes(np.moveaxis(pr["exces_100_actions"], 1, -1), ng),
               degats=_moy_groupes(np.moveaxis(pr["degats"], 1, -1), ng),
               charge=_moy_groupes(pr["charge_hors_lec"], ng),
               charge_avec_ep=_moy_groupes(pr["charge_hors_lec_avec_ep"], ng),
               charge_100_ecritures=_moy_groupes(pr["charge_100_ecritures"], ng),
               charge_totale=_moy_groupes(pr["charge_totale"], ng),
               charge_epreuves=_moy_groupes(pr["charge_epreuves"], ng),
               exces_a_part=_moy_groupes(pr["exces_a_part"], ng),
               inverifiables_seules=_moy_groupes(pr["inverifiables_seules"], ng))
    if s.jonction is not None:
        dw = den_fenetre(s)
        with np.errstate(divide="ignore", invalid="ignore"):
            fen = np.where(dw[None, :, None] > 0, agr["exc_w"] * 100.0 / np.maximum(dw, 1)[None, :, None], np.nan)
        out["budget_fenetre"] = _moy_groupes(np.moveaxis(fen, 1, -1), ng)
    return out


def numerateurs_grappes(rl: ResultatLot, nom: str) -> dict:
    """Numérateurs par (groupe, grappe), moyennés sur les colonnes du groupe : dégâts en plus (E, ng, 3, G) et
    validations + corrections + doutes (E, ng, G) ; dénominateurs par grappe."""
    cpt, v, _ = rl.cpt_et_v(nom)
    lot = rl.lot
    Kg = lot.K_groupe.astype(float)
    pg = lot.par_grappe
    exc = cpt.exc_g[:, v] / Kg[None, :, None, None]
    ch = (cpt.val_g[v][None] + cpt.cor_g[:, v]) / Kg[None, :, None] + pg["dou"][None]
    return dict(budget=exc, charge=ch, den=pg["den"].astype(float), hors_lec=(pg["ecr"] + pg["dou"]).astype(float))


def se_budget(a: np.ndarray, den: np.ndarray, strates) -> np.ndarray:
    """(E, 3, ng) écarts types linéarisés des dégâts en plus pour 100 écritures."""
    a2 = np.moveaxis(a, 2, 1)                                    # (E, 3, ng, G)
    return 100.0 * IC.se_rapport(a2, den[None, None, :, :], strates)


def se_charge(a: np.ndarray, d: np.ndarray, strates) -> np.ndarray:
    """(E, ng) écarts types linéarisés d'une charge (ou d'une différence de charges) pour 100 actions hors lectures."""
    return 100.0 * IC.se_rapport(a, d[None, :, :], strates)


def z_rapport(a: np.ndarray, d: np.ndarray) -> np.ndarray:
    """Influence linéarisée de chaque grappe sur un rapport Σa ÷ Σd : (a − q d) ÷ Σd (dernier axe : grappes)."""
    D = d.sum(axis=-1, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        q = np.where(D > 0, a.sum(axis=-1, keepdims=True) / np.where(D > 0, D, 1.0), 0.0)
        return np.where(D > 0, (a - q * d) / np.where(D > 0, D, 1.0), 0.0)


def se_depuis_z(z: np.ndarray, strates) -> np.ndarray:
    """√(Σ_h G_h ÷ (G_h − 1) Σ (z − z̄_h)²) (dernier axe : grappes)."""
    strates = np.asarray(strates)
    s2 = np.zeros(z.shape[:-1])
    for h in np.unique(strates):
        m = strates == h
        gh = int(m.sum())
        if gh < 2:
            continue
        zh = z[..., m]
        s2 = s2 + gh / (gh - 1) * ((zh - zh.mean(axis=-1, keepdims=True)) ** 2).sum(axis=-1)
    return np.sqrt(s2)


# ==========================================================================
# Le magasin des quantités
# ==========================================================================
class _Morceaux:
    """Répétitions bootstrap rangées par tranches (tableaux float32), lues comme un seul tableau."""

    def __init__(self, valeurs=None):
        self._m = []
        self._cache = None
        if valeurs is not None and len(valeurs):
            self += valeurs

    def __iadd__(self, v):
        self._m.append(np.asarray(v, dtype=np.float32).ravel())
        self._cache = None
        return self

    def __len__(self):
        return int(sum(m.size for m in self._m))

    def __getitem__(self, i):
        return self.tableau()[i]

    def tableau(self) -> np.ndarray:
        if self._cache is None:
            self._cache = np.concatenate(self._m).astype(float) if self._m else np.zeros(0)
        return self._cache

    def tolist(self):
        return self.tableau().tolist()


@dataclass
class Quantite:
    centre: float = float("nan")
    se: float = float("nan")              # écart type d'origine (bootstrap-t) ; nan : pas d'écart type linéarisé
    boot: _Morceaux = field(default_factory=_Morceaux)
    se_boot: _Morceaux = field(default_factory=_Morceaux)
    jack: Optional[np.ndarray] = None
    strates_jack: Optional[np.ndarray] = None
    G: int = 0
    info: dict = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.boot, _Morceaux):
            self.boot = _Morceaux(self.boot)
        if not isinstance(self.se_boot, _Morceaux):
            self.se_boot = _Morceaux(self.se_boot)

    @property
    def a_se(self) -> bool:
        return self.se == self.se and len(self.se_boot) == len(self.boot) and len(self.boot) > 0

    def intervalle(self, methode: str) -> tuple:
        b = self.boot.tableau()
        if methode in ("i", "percentile", "ii") and b.size == 0:
            return float("nan"), float("nan")
        if methode == "ii":
            if not self.a_se:
                return IC.intervalle("i", self.centre, b)
            return IC.intervalle("ii", self.centre, b, self.se, self.se_boot.tableau())
        if methode == "iii":
            if self.jack is None or len(self.jack) < 2:
                return float("nan"), float("nan")
            return IC.intervalle("iii", self.centre, jack=self.jack, strates_jack=self.strates_jack)
        return IC.intervalle(methode, self.centre, b)


class Magasin(dict):
    """{clé: Quantite}."""

    def q(self, cle) -> Quantite:
        if cle not in self:
            self[cle] = Quantite()
        return self[cle]


# ==========================================================================
# Une famille de suites (configuration ou scénario) : couches R0, jackknife, bootstrap
# ==========================================================================
@dataclass
class Famille:
    """Ce qui ne dépend pas de la répétition, pour une configuration ou un scénario."""
    cle: tuple                    # ("config", env, modèle) ou ("scenario", env, X, Y)
    jeu: object                   # JeuConfiguration (combiné pour un scénario)
    fabrique_fournisseur: object  # lot -> fournisseur d'épreuves
    classes: tuple                # (avant, après la jonction)
    retro: tuple
    regles: list
    modes: tuple                  # scénarios : (True, False) = annoncé, silencieux ; configuration : (False,)
    jX: object = None
    jY: object = None
    resistance: Optional[str] = None
    retard: int = 0
    ordre: Optional[str] = None   # sensibilité à l'ordre (Q5)

    @property
    def scenario(self) -> bool:
        return self.cle[0] == "scenario"

    def lot(self, couche: str, reglages: Reglages, reps=None, K=None):
        G0 = reglages.G0
        if self.scenario:
            if couche == "R0":
                lot = LO.lot_scenario_r0(self.jX, self.jY, G0, reglages.R0 if K is None else K)
            else:
                lot = LO.lot_scenario_bootstrap(self.jX, self.jY, G0, reps, reglages.K)
        elif self.ordre is not None:
            sc = LO.SCENARIO_PAR_PASSAGE if self.ordre == "par_passage" else LO.SCENARIO_ORDRE_REEL
            lot = LO.lot_ordre_impose(self.jeu, G0, reglages.R0 if K is None else K, self.ordre, sc)
        elif couche == "R0":
            lot = LO.lot_r0(self.jeu, G0, reglages.R0 if K is None else K)
        else:
            lot = LO.lot_bootstrap(self.jeu, G0, reps, reglages.K)
        return lot

    def preparer(self, lot: LO.Lot) -> tuple:
        """(lot transformé, fournisseur) selon le test de résistance."""
        ratees = LO.taches_ratees(lot) if self.resistance == "groupees" else None
        if self.resistance in ("rate10", "groupees"):
            nv = LO.non_vues_epreuves(lot, self.resistance, ratees)
            lot = LO.transformer_resistance(lot, self.resistance, ratees)
        else:
            nv = None
        return lot, self.fabrique_fournisseur(lot, nv)

    def rejouer(self, lot: LO.Lot, reglages: Reglages, annonce: bool, grappes: bool = True, **kw) -> ResultatLot:
        lot, f = self.preparer(lot)
        return rejouer_lot(lot, self.regles, reglages.valeurs_e, f, self.classes, self.retro, annonce=annonce,
                           retard=self.retard, grappes=grappes, **kw)


def exclues_jackknife(lot):
    """Jackknife : la tâche retirée de chaque colonne sort aussi du vivier des variantes (audit du moteur, 09/11)."""
    if getattr(lot, "couche", None) != "jackknife":
        return None
    return [frozenset({lot.taches[int(g)]}) for g in lot.groupe]


class FabriqueConfig:
    """Fournisseur d'épreuves d'une configuration (objet et non fonction anonyme : une famille doit pouvoir passer à
    un autre processus)."""

    def __init__(self, pool: EP.PoolEpreuves):
        self.pool = pool

    def __call__(self, lot, nv):
        return EP.FournisseurParties(self.pool, lot.suite.cles_epreuves, nv, exclues_jackknife(lot))


class FabriqueScenario:
    def __init__(self, pool_X: EP.PoolEpreuves, pool_Y: EP.PoolEpreuves):
        self.pool_X, self.pool_Y = pool_X, pool_Y

    def __call__(self, lot, nv):
        return EP.FournisseurScenario(self.pool_X, self.pool_Y, lot.nX, lot.suite.cles_epreuves, lot.suite.jonction,
                                      lot.outils, nv, exclues_jackknife(lot))


def fabrique_config(pool: EP.PoolEpreuves):
    return FabriqueConfig(pool)


def fabrique_scenario(pool_X: EP.PoolEpreuves, pool_Y: EP.PoolEpreuves):
    return FabriqueScenario(pool_X, pool_Y)


def suffixe_mode(famille: Famille, annonce: bool) -> tuple:
    if not famille.scenario:
        return famille.cle
    return famille.cle + ("annoncé" if annonce else "silencieux",)


def noms_lignes(regles: list) -> list:
    return [r.nom for r in regles] + list(TM.NOMS_FIXES) + ["trois_reussites"] + \
        [f"hasard_{r.nom}" for r in regles] + ["oracle_p2", "oracle_retro"]


def _quantites_budget(fam: Famille, reglages: Reglages, nom: str) -> list:
    """(indice de e, e) des quantités de budget gardées : toutes les valeurs de e pour les règles, e principal pour
    les témoins."""
    regle = nom in [r.nom for r in fam.regles]
    return list(enumerate(reglages.valeurs_e)) if regle else [(0, reglages.e_principal)]


def enregistrer_groupes(mag: Magasin, fam: Famille, annonce: bool, rl: ResultatLot, reglages: Reglages,
                        couche: str, strates=None) -> dict:
    """Valeurs (et écarts types, pour R0 et le bootstrap) de toutes les quantités d'une famille ; rend les numérateurs
    par grappe des quantités qui entrent dans les moyennes sur les configurations (configurations seulement)."""
    cle_f = suffixe_mode(fam, annonce)
    ng = rl.lot.n_groupes
    vals = {nom: valeurs_groupes(rl, nom) for nom in rl.noms}
    num = {nom: numerateurs_grappes(rl, nom) for nom in rl.noms} if couche in ("R0", "bootstrap") else None
    st = rl.lot.strate_grappe if strates is None else strates
    se_b = {nom: se_budget(num[nom]["budget"], num[nom]["den"], st) for nom in rl.noms} if num else None
    se_c = {nom: se_charge(num[nom]["charge"], num[nom]["hors_lec"], st) for nom in rl.noms} if num else None
    sorties = []

    def poser(cle, v, se=None, centre_seul=False):
        sorties.append((cle, np.asarray(v, dtype=float), None if se is None else np.asarray(se, dtype=float),
                        centre_seul))

    regles_n = [r.nom for r in fam.regles]
    for nom in rl.noms:
        V = vals[nom]
        regle = nom in regles_n
        # scénarios : seuls les deux témoins de la réussite (max-T, 5.14, point 2) gardent leurs répétitions
        seul = fam.scenario and not regle and nom not in TEMOINS_REUSSITE
        for ie, e in _quantites_budget(fam, reglages, nom):
            for j, niv in enumerate(NIVEAUX):
                poser(("budget",) + cle_f + (nom, e, niv), V["budget"][ie, j], se_b[nom][ie, j] if se_b else None,
                      seul)
                if regle and ie == 0:
                    poser(("budget_actions",) + cle_f + (nom, e, niv), V["budget_actions"][ie, j])
                    if "budget_fenetre" in V:
                        poser(("budget_fenetre",) + cle_f + (nom, e, niv), V["budget_fenetre"][ie, j])
        if not fam.scenario:
            for ie, e in _quantites_budget(fam, reglages, nom):
                poser(("charge",) + cle_f + (nom, e), V["charge"][ie], se_c[nom][ie] if se_c else None)
            if nom in regles_n:
                poser(("charge_avec_ep",) + cle_f + (nom, reglages.e_principal), V["charge_avec_ep"][0])
    if not fam.scenario:
        for r in regles_n:
            for t in list(TEMOINS_DIFF) + [f"hasard_{r}"]:
                d = vals[r]["charge"][0] - vals[t]["charge"][0]
                se = None
                if num:
                    se = se_charge(num[r]["charge"][:1] - num[t]["charge"][:1], num[r]["hors_lec"], st)[0]
                poser(("diff_charge",) + cle_f + (r, t), d, se)
            h = f"hasard_{r}"
            for j, niv in enumerate(NIVEAUX):
                d = vals[r]["budget"][0, j] - vals[h]["budget"][0, j]
                se = None
                if num:
                    se = se_budget(num[r]["budget"][:1] - num[h]["budget"][:1], num[r]["den"], st)[0, j]
                poser(("diff_exces",) + cle_f + (r, niv), d, se)
    for cle, v, se, centre_seul in sorties:
        if centre_seul and couche != "R0":
            continue
        q = mag.q(cle)
        if couche == "R0":
            q.centre = float(v[0])
            q.se = float(se[0]) if se is not None else float("nan")
        elif couche == "bootstrap":
            q.boot += v
            if se is not None:
                q.se_boot += se
        elif couche == "jackknife":
            q.jack = v.copy()
    if num is None or fam.scenario:
        return {}
    # numérateurs des moyennes sur les configurations (e principal) : influences par grappe
    z = {}
    for r in regles_n:
        for t in list(TEMOINS_DIFF) + [f"hasard_{r}"]:
            z[("moy_diff_charge", r, t)] = z_rapport(num[r]["charge"][0] - num[t]["charge"][0], num[r]["hors_lec"])
        h = f"hasard_{r}"
        a = np.moveaxis(num[r]["budget"][0] - num[h]["budget"][0], 1, 0)   # (3, ng, G)
        for j, niv in enumerate(NIVEAUX):
            z[("moy_diff_exces", r, niv)] = z_rapport(a[j], num[r]["den"])
        z[("moy_charge", r)] = z_rapport(num[r]["charge"][0], num[r]["hors_lec"])
    return z


def garantie_groupes(rl: ResultatLot, classes: dict, apres: bool = False) -> dict:
    """{(règle, type): (ng,)} part des colonnes du groupe où un type « au-dessus » atteint le palier 3 (5.12, point 8 ;
    après la jonction dans les scénarios)."""
    out = {}
    m = rl.moteur
    ng = rl.lot.n_groupes
    for i, r in enumerate(rl.regles):
        sl = m.lignes(i)
        p3 = (m.premier3_apres if apres else m.premier3)[sl] >= 0
        if apres and m.snap is not None:
            # recommandation de l'audit du moteur (09/11 ; plan 5.12, point 8, Otsoa peut l'infirmer) : en mode
            # silencieux, un type déjà au palier 3 à la jonction et qui ne le perd pas compte aussi
            p3 = p3 | ((m.snap[sl] == 3) & (m.perte3[sl] < 0))
        for k in TY.TYPES_SUITE:
            if (classes or {}).get(k, {}).get("classe") == CL.AU_DESSUS:
                out[(r.nom, k)] = _moy_groupes(p3[:, k].astype(float), ng)
    return out
