"""Classes des types : « sous la barre », « au-dessus », « indéterminé » (PLAN_EXPERIENCE.md, 5.12, point 4 ; 5.13,
« Taux par type » ; contrôle 1, B1 et B4).

Phase 2 : Clopper-Pearson sur la taille effective, à la place de la fonction provisoire de la phase 1.
- n = écritures vérifiables et non neutres du type, x = erreurs confirmées, refusées comprises ; en principal, toutes
  les écritures du type, plafonnées comprises (5.12, point 4).
- n_eff = n ÷ (1 + (m̄ − 1) ρ̂), m̄ = Σ m² ÷ Σ m sur les tâches porteuses du type (m : écritures du type, comptées
  comme n, dans une tâche) ; x_eff = x × n_eff ÷ n (le taux estimé ne change pas) ; bornes lues sur la loi bêta, qui
  accepte des effectifs non entiers.
- ρ̂ (N3, tranché par la recherche à la demande d'Otsoa, 06/11 ; `reports/Corrélation intra tâche par strates.md`) :
  corrélation des erreurs d'un même type à l'intérieur d'une tâche. Grappe = (tâche, type) dans une configuration ;
  strate = (configuration, type), avec son propre taux ; estimateur de Fleiss–Cuzick stratifié, corrigé du biais de
  petit échantillon, mis en commun sur toutes les configurations puis borné entre 0 et 1 (`rho_fc_strates`). Une
  strate sans erreur et une grappe d'une écriture n'y pèsent rien. ρ̂ des décisions au taux médian : le plus grand du
  plancher (0,3) et de la valeur commune ; une configuration d'au moins 10 erreurs dans au moins 5 tâches prend la
  sienne si elle est plus grande ; sans aucune strate informative, le plancher.
- Preuves à 95 % (classement prouvé, « démontrée ») : ρ = 1, soit la taille effective (Σ m)² ÷ Σ m², le nombre
  effectif de tâches. C'est la seule valeur valable sans hypothèse sur la corrélation ; la classe calculée avec ρ̂
  est publiée à côté, « sous hypothèse » (`classe_sous_hypothese`).
- Risque : 5 % unilatéral de chaque côté ; à zéro erreur, la borne haute vaut 1 − 0,05^(1/n_eff).
- « sous la barre » : borne haute au plus la barre ; « au-dessus » : borne basse au-dessus ; « indéterminé » sinon.
- Délégabilité (N1, tranché par la recherche à la demande d'Otsoa, 06/11 ; remplace la lecture de Q14 sur le taux
  observé) : un type compte si son taux médian, la borne haute de Clopper-Pearson à 50 % sur la taille effective
  (médiane de la même loi Bêta(x + 1, n − x) que la borne à 95 %), est au plus la barre. Sans erreur, il faut
  n_eff × barre ≥ ln 2 environ. Un type est « jugeable » si zéro erreur suffirait à le faire compter (garde-fou de R4).
- R4 (amendement d'Otsoa du 07/11, avant toute donnée d'évaluation) : sans configuration délégable, R4 exige, dans
  chaque configuration qui a un type jugeable, un type jugeable dont le dépassement est établi à ρ = 1
  (`depassement_etabli` : la classe prouvée « au-dessus ») ; sinon « preuves insuffisantes ». Publiés à côté, jamais
  comme preuve : la lecture au ρ̂ propre de la configuration (`statut_configuration`) et le point de bascule ρ*
  (`rho_bascule`).
- ρ̂ ne se lit que sur les tâches d'au moins deux écritures (résidu de G1, 06/11) : une tâche d'une seule écriture n'a
  pas de variance interne et ne dit rien de la corrélation à l'intérieur d'une tâche.
  Un type sans donnée (n = 0) est « sans donnée » : l'oracle le traite comme au-dessus (5.7, pièce 4) ; il ne compte
  pas comme « au-dessus » pour la garantie ni comme « devenu mauvais ».

`classer(x, n, barre)` sans taille effective garde la lecture provisoire de la phase 1 (effectifs bruts) : elle sert
aux tests de la phase 1 et vaut le cas ρ̂ = 0.

Modèle bêta-binomial (5.13, descriptif seulement) : `beta_binomiale`, maximum de vraisemblance de (μ, ρ) sur les tâches.
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np
from scipy.optimize import brentq, minimize
from scipy.special import betaln, gammaln
from scipy.stats import beta

from . import types_regle as TY

SOUS, AU_DESSUS, INDETERMINE, SANS_DONNEE = "sous la barre", "au-dessus", "indéterminé", "sans donnée"
RISQUE = 0.05
NIVEAU_MEDIANE = 0.5   # délégabilité (N1, 06/11) : borne haute à 50 %, médiane de Bêta(x + 1, n − x)
SOURCES_RHO = ("configuration", "environnement", "défaut (ρ = 1)")
# Règle de ρ̂ (N3, 06/11, PLAN_EXPERIENCE.md, 5.13 ; remplace G1) : valeur commune à toutes les configurations
# (Fleiss–Cuzick stratifié par configuration et type), plancher 0,3 ; une configuration d'au moins 10 erreurs dans au
# moins 5 tâches prend la sienne si elle est plus grande ; sans strate informative, le plancher.
PLANCHER_RHO = 0.3
SEUIL_ERREURS_CONF, SEUIL_TACHES_CONF = 10, 5
RHO_PREUVE = 1.0   # preuves à 95 % : valable sans hypothèse sur la corrélation (N3)
SOURCES_G1 = ("configuration (au moins 10 erreurs dans au moins 5 tâches)", "toutes les configurations réunies",
              "plancher")


def bornes_cp(x: float, n: float, risque: float = RISQUE) -> tuple:
    """Bornes unilatérales de Clopper-Pearson (risque de chaque côté) ; acceptent des effectifs non entiers."""
    if n <= 0:
        return 0.0, 1.0
    lo = 0.0 if x <= 0 else float(beta.ppf(risque, x, n - x + 1))
    hi = 1.0 if x >= n else float(beta.ppf(1 - risque, x + 1, n - x))
    return lo, hi


def _classe(lo: float, hi: float, barre: float) -> str:
    if hi <= barre:
        return SOUS
    if lo > barre:
        return AU_DESSUS
    return INDETERMINE


def mediane_haute(x_eff: float, n_eff: float) -> float:
    """Taux médian d'un type : borne haute unilatérale de Clopper-Pearson à 50 % (N1, 06/11)."""
    return bornes_cp(x_eff, n_eff, NIVEAU_MEDIANE)[1]


def estime_sous(c: dict) -> bool:
    """Le type compte pour la délégabilité (Q14, Otsoa, 06/11 : meilleure estimation ; N1, tranché par la recherche à
    sa demande, 06/11) : son taux médian au jeu de calibration est au plus la barre. Un type sans donnée ne compte
    jamais ; faute de comptes, seul un type prouvé « sous la barre » compte."""
    if "estime_sous" in c:
        return bool(c["estime_sous"])
    if c.get("n", 0) > 0 and "barre" in c and "x_eff" in c and "n_eff" in c:
        return bool(mediane_haute(c["x_eff"], c["n_eff"]) <= c["barre"])
    return c.get("classe") == SOUS


def jugeable(c: dict) -> bool:
    """Le volume du type permet de le juger : zéro erreur suffirait à le faire compter (garde-fou de R4, N1)."""
    if "jugeable" in c:
        return bool(c["jugeable"])
    ne = float(c.get("n_eff") or 0.0)
    return bool(c.get("n", 0) > 0 and ne > 0 and mediane_haute(0.0, ne) <= float(c.get("barre", 0.0)))


def depassement_etabli(c: dict) -> bool:
    """Dépassement établi (R4, amendement du 07/11) : la borne basse unilatérale de Clopper-Pearson à 95 %, sur la
    taille effective à ρ = 1, est au-dessus de la barre. C'est la classe prouvée « au-dessus » (5.12, point 4), valable
    sans hypothèse sur le groupement des erreurs. Un type sans erreur n'est jamais établi."""
    if "lo" in c and "barre" in c:
        return bool(c.get("n", 0) > 0 and c["lo"] > c["barre"])
    return c.get("classe") == AU_DESSUS


def borne_basse(c: dict, rho: float, risque: float = RISQUE) -> float:
    """Borne basse unilatérale de Clopper-Pearson d'un type, sur la taille effective à `rho` :
    n_eff = n ÷ (1 + (m̄ − 1) ρ), x_eff = x × n_eff ÷ n. À ρ = 1, c'est `lo` ; au ρ̂ du type, `lo_hyp`. m̄ est lu dans
    `m_bar`, sinon sur n ÷ n_eff à ρ = 1."""
    n, x = float(c.get("n", 0)), float(c.get("x", 0))
    if n <= 0 or x <= 0:
        return 0.0
    mbar = float(c["m_bar"]) if c.get("m_bar") else n / float(c["n_eff_preuve"])
    ne = n / (1.0 + (mbar - 1.0) * float(rho))
    return bornes_cp(x * ne / n, ne, risque)[0]


def rho_bascule(c: dict, risque: float = RISQUE) -> Optional[float]:
    """Point de bascule ρ* d'un dépassement (amendement R4, 07/11) : le dépassement est établi (borne basse à 95 %
    au-dessus de la barre) pour tout ρ < ρ*. 1 s'il l'est même à ρ = 1 ; None s'il ne l'est pas même à ρ = 0, ou sans
    erreur. Publié par type, jamais comme preuve : le lecteur le compare au ρ̂ estimé."""
    if c.get("n", 0) <= 0 or c.get("x", 0) <= 0:
        return None
    b = float(c["barre"])

    def f(r):
        return borne_basse(c, r, risque) - b

    if f(1.0) > 0:
        return 1.0
    if f(0.0) <= 0:
        return None
    return float(brentq(f, 0.0, 1.0, xtol=1e-12))


def taches_pour_etablir(barre: float, multiple: float = 5.0, risque: float = RISQUE) -> int:
    """Plus petit nombre de tâches distinctes (taille effective à ρ = 1, tâches de même taille) pour lequel un taux
    observé de `multiple` fois la barre établit le dépassement : borne basse à 95 % au-dessus de la barre (publication,
    amendement R4 du 07/11)."""
    p = float(multiple) * float(barre)
    if not 0.0 < float(barre) < p < 1.0:
        raise ValueError("il faut 0 < barre < multiple × barre < 1")

    def etabli(n: int) -> bool:
        return bornes_cp(p * n, n, risque)[0] > barre

    haut = 1
    while not etabli(haut):
        haut *= 2
    bas = haut // 2 + 1 if haut > 1 else 1
    while bas < haut:
        milieu = (bas + haut) // 2
        if etabli(milieu):
            haut = milieu
        else:
            bas = milieu + 1
    return haut


def classer(x: float, n: float, barre: float, risque: float = RISQUE, n_eff: Optional[float] = None,
            n_eff_preuve: Optional[float] = None) -> dict:
    """Classe d'un type. Sans n_eff : effectifs bruts (lecture provisoire de la phase 1) ; avec n_eff : x ramené à
    x_eff = x × n_eff ÷ n (5.13). n_eff (ρ̂) sert au taux médian et à « jugeable » ; n_eff_preuve (ρ = 1, N3) aux bornes à
    95 % de la classe (lo, hi). La classe calculée sur n_eff est `classe_sous_hypothese` (bornes lo_hyp, hi_hyp)."""
    if n <= 0:
        return dict(n=0, x=0, p=float("nan"), n_eff=0.0, x_eff=0.0, n_eff_preuve=0.0, lo=0.0, hi=1.0, lo_hyp=0.0,
                    hi_hyp=1.0, hi50=1.0, barre=float(barre), classe=SANS_DONNEE, classe_sous_hypothese=SANS_DONNEE,
                    estime_sous=False, jugeable=False)
    ne = float(n) if n_eff is None else float(n_eff)
    xe = float(x) * ne / float(n)
    lo_h, hi_h = bornes_cp(xe, ne, risque)
    np_ = ne if n_eff_preuve is None else float(n_eff_preuve)
    lo, hi = (lo_h, hi_h) if n_eff_preuve is None else bornes_cp(float(x) * np_ / float(n), np_, risque)
    hi50 = mediane_haute(xe, ne)
    p = float(x) / float(n)
    b = float(barre)
    return dict(n=int(n), x=int(x), p=p, n_eff=ne, x_eff=xe, n_eff_preuve=np_, lo=lo, hi=hi, lo_hyp=lo_h, hi_hyp=hi_h,
                hi50=hi50, barre=b, classe=_classe(lo, hi, b), classe_sous_hypothese=_classe(lo_h, hi_h, b),
                estime_sous=bool(hi50 <= b), jugeable=bool(mediane_haute(0.0, ne) <= b))


# --------------------------------------------------------------------------
# Corrélation intra-tâche et taille effective
# --------------------------------------------------------------------------
def rho_anova(m, x) -> Optional[float]:
    """Estimateur d'analyse de variance de la corrélation intra-grappe pour des données binaires groupées (tailles m,
    erreurs x), borné entre 0 et 1 ; None s'il n'est pas calculable (moins de deux grappes, aucune variance). Les
    grappes d'une seule écriture sont écartées (résidu de G1, 06/11) : sans variance interne, elles ne disent rien de
    la corrélation, et une seule erreur en grappe d'une écriture donnait ρ̂ = 1 à tout un environnement."""
    m = np.asarray(m, dtype=float)
    x = np.asarray(x, dtype=float)
    garde = m > 1
    m, x = m[garde], x[garde]
    k = m.size
    N = m.sum()
    if k < 2 or N <= k:
        return None
    msb = (np.sum(x ** 2 / m) - x.sum() ** 2 / N) / (k - 1)
    msw = (x.sum() - np.sum(x ** 2 / m)) / (N - k)
    m0 = (N - np.sum(m ** 2) / N) / (k - 1)
    den = msb + (m0 - 1) * msw
    if not den > 0:
        return None
    return float(min(1.0, max(0.0, (msb - msw) / den)))


def taille_effective(m, rho: float) -> tuple:
    """(n, m̄, n_eff) : n = Σ m ; m̄ = Σ m² ÷ Σ m ; n_eff = n ÷ (1 + (m̄ − 1) ρ) (au plus n ; avec ρ = 1, le nombre
    effectif de tâches (Σ m)² ÷ Σ m²)."""
    m = np.asarray([v for v in m if v > 0], dtype=float)
    n = float(m.sum())
    if n <= 0:
        return 0.0, 0.0, 0.0
    mbar = float(np.sum(m ** 2) / n)
    return n, mbar, n / (1.0 + (mbar - 1.0) * float(rho))


# --------------------------------------------------------------------------
# Comptes sur un jeu (suites.JeuConfiguration)
# --------------------------------------------------------------------------
def masque_non_neutre(jeu, plafonnees: bool = True) -> np.ndarray:
    m = jeu.attrs["reu"] | jeu.attrs["errp"]
    if not plafonnees:
        m = m & ~jeu.attrs["plaf"]
    return m


def taches_ecritures(jeu) -> np.ndarray:
    """La tâche de chaque écriture du jeu (à plat)."""
    if not jeu.n_parties:
        return np.zeros(0, dtype=object)
    return np.repeat(np.array([e.partie.tache for e in jeu.parties], dtype=object), jeu.longueurs)


def comptes_par_tache(jeu, types=None, plafonnees: bool = True) -> dict:
    """{tâche: (m, x)} : écritures vérifiables non neutres (des types donnés ; tous les types mérités sinon) et erreurs
    confirmées, par tâche (toutes les parties de la tâche dans la configuration forment une grappe)."""
    nn = masque_non_neutre(jeu, plafonnees)
    if types is not None:
        nn = nn & np.isin(jeu.typ, np.asarray(list(types), dtype=np.int8))
    taches = taches_ecritures(jeu)[nn]
    err = jeu.attrs["errp"][nn]
    out: dict = {}
    for t, e in zip(taches.tolist(), err.tolist()):
        m, x = out.get(t, (0, 0))
        out[t] = (m + 1, x + int(e))
    return out


def rho_jeu(jeu) -> Optional[float]:
    """ρ̂ d'une configuration, tous types mérités réunis (None si non calculable)."""
    c = comptes_par_tache(jeu)
    if not c:
        return None
    m, x = zip(*c.values())
    return rho_anova(m, x)


def rho_jeux(jeux) -> Optional[float]:
    """ρ̂ de plusieurs configurations réunies (l'environnement, tous modèles) : chaque (modèle, tâche) est une grappe."""
    m, x = [], []
    for j in jeux:
        for mm, xx in comptes_par_tache(j).values():
            m.append(mm)
            x.append(xx)
    return rho_anova(m, x) if m else None


def rho_avec_repli(rho_conf: Optional[float], rho_env: Optional[float]) -> tuple:
    """(ρ̂, source) : configuration, sinon environnement, sinon 1 (5.13)."""
    if rho_conf is not None:
        return rho_conf, SOURCES_RHO[0]
    if rho_env is not None:
        return rho_env, SOURCES_RHO[1]
    return 1.0, SOURCES_RHO[2]


def compter(jeu, plafonnees: bool = True) -> dict:
    """{type: (n, x)} sur un jeu : écritures vérifiables non neutres du type (plafonnées comprises par défaut)."""
    nn = masque_non_neutre(jeu, plafonnees)
    errp = jeu.attrs["errp"]
    return {k: (int((nn & (jeu.typ == k)).sum()), int((nn & errp & (jeu.typ == k)).sum())) for k in TY.TYPES_SUITE}


def classes_jeu(jeu, config, rho: Optional[float] = None, source_rho: Optional[str] = None,
                plafonnees: bool = True) -> dict:
    """{type: dict(n, x, p, n_eff, x_eff, n_eff_preuve, lo, hi, lo_hyp, hi_hyp, barre, classe, classe_sous_hypothese,
    n_taches, m_bar, rho, source_rho, reussites)}.

    rho : ρ̂ déjà choisi (règle N3, `rho_par_configuration`) ; par défaut, celui du jeu seul (`rho_fc_strates`), sinon le
    plancher. La classe (bornes à 95 %) se lit sur la taille effective à ρ = 1 ; la classe sous hypothèse, sur ρ̂."""
    if rho is None:
        r = rho_fc_strates(strates_par_type([jeu]))
        rho, source_rho = (max(PLANCHER_RHO, r), SOURCES_G1[1]) if r is not None else (PLANCHER_RHO, SOURCES_G1[2])
    out = {}
    for k in TY.TYPES_SUITE:
        par_t = comptes_par_tache(jeu, (k,), plafonnees)
        ms = [v[0] for v in par_t.values()]
        n, mbar, ne = taille_effective(ms, rho)
        _n, _m, ne1 = taille_effective(ms, RHO_PREUVE)
        x = sum(v[1] for v in par_t.values())
        c = classer(x, int(n), float(config.barres[(jeu.environnement, TY.niveau(k))]), n_eff=ne if n > 0 else None,
                    n_eff_preuve=ne1 if n > 0 else None)
        c.update(n_taches=len(ms), m_bar=mbar, rho=float(rho), source_rho=source_rho, reussites=int(n) - int(x))
        out[k] = c
    return out


def erreurs_et_taches(jeu) -> tuple:
    """(erreurs confirmées, tâches qui en portent) sur les types mérités d'une configuration."""
    c = comptes_par_tache(jeu)
    return sum(x for _m, x in c.values()), sum(1 for _m, x in c.values() if x > 0)


# --------------------------------------------------------------------------
# Règle de ρ̂ (N3, 06/11) : Fleiss–Cuzick stratifié par (configuration, type)
# --------------------------------------------------------------------------
def strates_par_type(jeux) -> list:
    """[(m, y)] par strate (configuration, type mérité) : une grappe par tâche où le type est écrit, m écritures
    vérifiables non neutres (plafonnées comprises), y erreurs confirmées."""
    out = []
    for j in jeux:
        for k in TY.TYPES_SUITE:
            c = comptes_par_tache(j, (k,))
            if c:
                out.append((np.array([v[0] for v in c.values()], dtype=float),
                            np.array([v[1] for v in c.values()], dtype=float)))
    return out


def rho_fc_strates(strates, correction: bool = True, iterations: int = 50) -> Optional[float]:
    """ρ̂ commun aux strates : Fleiss–Cuzick stratifié, ρ̂ = 1 − Σ SSW_s ÷ Σ (N_s − K_s) p̂_s (1 − p̂_s), avec
    SSW_s = Σ y (m − y) ÷ m sur les grappes de la strate, N_s écritures, K_s grappes, p̂_s = Σ y ÷ N_s. Sans biais si les
    taux sont connus. Seules les grappes d'au moins deux écritures entrent, taux p̂_s compris : une erreur dans une
    grappe d'une écriture ne dit rien de ρ, et gonflerait p̂_s (résidu de G1) ; une strate sans erreur dans ces grappes
    ne pèse rien. Correction du biais de petit
    échantillon (E[p̂(1 − p̂)] = p(1 − p)(1 − deff ÷ N), deff = 1 + (m* − 1) ρ, point fixe ; facteur borné à 0,1).
    Borné entre 0 et 1 après la mise en commun. None si aucune strate n'est informative (N3, recherche du 06/11)."""
    ssw, d0, info = 0.0, [], []
    for m, y in strates:
        m = np.asarray(m, dtype=float)
        y = np.asarray(y, dtype=float)
        garde = m > 1
        m, y = m[garde], y[garde]
        N, K, Y = float(m.sum()), int(m.size), float(y.sum())
        if N <= K or Y <= 0.0 or Y >= N:
            continue
        p = Y / N
        ssw += float(np.sum(y * (m - y) / m))
        d0.append((N - K) * p * (1.0 - p))
        info.append((N, float(np.sum(m ** 2) / N)))
    if not d0:
        return None
    rho = 1.0 - ssw / sum(d0)
    if correction:
        for _ in range(iterations):
            r = min(max(rho, 0.0), 1.0)
            d = sum(di / max(1.0 - (1.0 + (ms - 1.0) * r) / N, 0.1) for di, (N, ms) in zip(d0, info))
            nouveau = 1.0 - ssw / d
            if abs(nouveau - rho) < 1e-12:
                rho = nouveau
                break
            rho = nouveau
    return float(min(max(rho, 0.0), 1.0))


def rho_commun(jeux_par_env: dict) -> Optional[float]:
    """ρ̂ commun à toutes les configurations (tous environnements et modèles), sur les strates (configuration, type)."""
    return rho_fc_strates(strates_par_type([j for jeux in jeux_par_env.values() for j in jeux.values()]))


def rho_par_configuration(jeux: dict, rho_c: Optional[float]) -> dict:
    """{modèle: (ρ̂, source)} selon la règle N3 : le plus grand du plancher (0,3) et de la valeur commune `rho_c` (le
    plancher seul s'il n'y en a pas) ; une configuration d'au moins 10 erreurs dans au moins 5 tâches prend sa propre
    valeur si elle est plus grande."""
    if rho_c is not None:
        base, src = max(PLANCHER_RHO, rho_c), SOURCES_G1[1]
    else:
        base, src = PLANCHER_RHO, SOURCES_G1[2]
    out = {}
    for mod, j in jeux.items():
        r_conf = rho_propre(j)
        out[mod] = (r_conf, SOURCES_G1[0]) if (r_conf is not None and r_conf > base) else (base, src)
    return out


def rho_propre(jeu) -> Optional[float]:
    """ρ̂ propre d'une configuration (N3) : Fleiss–Cuzick sur ses seules strates, si elle a au moins 10 erreurs dans au
    moins 5 tâches ; None sinon (ou s'il n'est pas calculable)."""
    x, t = erreurs_et_taches(jeu)
    if x >= SEUIL_ERREURS_CONF and t >= SEUIL_TACHES_CONF:
        return rho_fc_strates(strates_par_type([jeu]))
    return None


def classes_environnement(jeux: dict, config, plafonnees: bool = True, rho_c: Optional[float] = None) -> dict:
    """{modèle: classes} des configurations d'un environnement (jeux : {modèle: JeuConfiguration}), ρ̂ selon la règle
    N3 avec la valeur commune `rho_c` (calculée sur ces seules configurations si elle n'est pas donnée). ρ̂ est toujours
    estimé sur toutes les écritures (plafonnées comprises)."""
    if rho_c is None:
        rho_c = rho_commun({"": jeux})
    rhos = rho_par_configuration(jeux, rho_c)
    return {mod: classes_jeu(j, config, rhos[mod][0], rhos[mod][1], plafonnees) for mod, j in jeux.items()}


def classes_tous_environnements(jeux_par_env: dict, config, plafonnees: bool = True) -> dict:
    """{env: {modèle: classes}} avec la valeur commune de ρ̂ calculée sur toutes les configurations (règle N3)."""
    rc = rho_commun(jeux_par_env)
    return {env: classes_environnement(jeux, config, plafonnees, rc) for env, jeux in jeux_par_env.items()}


def statut_configuration(cl: Optional[dict], rho_propre: Optional[float] = None) -> dict:
    """Statut d'une configuration au jeu de calibration (5.14, point 4 ; amendement R4 du 07/11) :
    - délégable : un type au taux médian au plus la barre (Q14, N1) ;
    - jugeable : un type jugeable (N1) ;
    - établie : un type jugeable dont le dépassement est établi à ρ = 1 (`depassement_etabli`) ; un type non jugeable
      ne compte pas, même établi (correction du 06/11 au soir, `controle3/options_r4/options_r4.md`, section 7) ;
    - établie sous le ρ̂ propre : même exigence, la borne basse étant lue à ρ = max(0,3 ; ρ̂ propre) si la configuration
      a un ρ̂ propre (au moins 10 erreurs dans au moins 5 tâches), à ρ = 1 sinon. Lecture publiée avec « preuves
      insuffisantes », jamais une preuve ;
    - rho_bascule : le plus grand point de bascule ρ* de ses types jugeables (None si aucun n'est établi à ρ = 0)."""
    cl = cl or {}
    jug = [c for c in cl.values() if jugeable(c)]
    rho_l = max(PLANCHER_RHO, float(rho_propre)) if rho_propre is not None else RHO_PREUVE
    etablie = any(depassement_etabli(c) for c in jug)
    bascules = [r for r in map(rho_bascule, jug) if r is not None]
    return dict(delegable=any(estime_sous(c) for c in cl.values()), jugeable=bool(jug), etablie=etablie,
                etablie_rho_propre=etablie or (rho_l < RHO_PREUVE and
                                               any(borne_basse(c, rho_l) > float(c["barre"]) for c in jug)),
                rho_propre=rho_propre, rho_lecture=rho_l, rho_bascule=max(bascules) if bascules else None)


# --------------------------------------------------------------------------
# Modèle bêta-binomial (descriptif)
# --------------------------------------------------------------------------
def beta_binomiale(m, x) -> dict:
    """Maximum de vraisemblance du modèle bêta-binomial sur les tâches : taux moyen μ et corrélation ρ = 1 ÷ (a + b + 1).
    Descriptif seulement (5.13). Sans erreur ou sans succès, le maximum est au bord : μ = 0 ou 1, ρ indéterminée."""
    m = np.asarray(m, dtype=float)
    x = np.asarray(x, dtype=float)
    garde = m > 0
    m, x = m[garde], x[garde]
    if m.size == 0:
        return dict(mu=float("nan"), rho=float("nan"), n_taches=0)
    if x.sum() == 0 or x.sum() == m.sum():
        return dict(mu=float(x.sum() / m.sum()), rho=float("nan"), n_taches=int(m.size))

    def nll(th):
        mu = 1 / (1 + math.exp(-th[0]))
        rho = 1 / (1 + math.exp(-th[1]))
        s = (1 - rho) / rho
        a, b = mu * s, (1 - mu) * s
        return -float(np.sum(gammaln(m + 1) - gammaln(x + 1) - gammaln(m - x + 1) + betaln(x + a, m - x + b)
                             - betaln(a, b)))

    mu0 = x.sum() / m.sum()
    th0 = np.array([math.log(mu0 / (1 - mu0)), math.log(0.1 / 0.9)])
    r = minimize(nll, th0, method="Nelder-Mead", options=dict(xatol=1e-6, fatol=1e-8, maxiter=2000))
    return dict(mu=float(1 / (1 + math.exp(-r.x[0]))), rho=float(1 / (1 + math.exp(-r.x[1]))), n_taches=int(m.size))
