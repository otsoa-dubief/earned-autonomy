"""Les trois méthodes d'intervalle candidates, la règle de choix et la mention « fragile » (PLAN_EXPERIENCE.md, 5.13 ;
5.16, point 5 ; contrôle 1, B4).

Une quantité q (dégâts en plus d'une cellule, différence appariée, moyenne sur les configurations…) est connue par :
- sa valeur centrale : la moyenne sur les R0 répétitions sans rééchantillonnage (5.13) ;
- ses répétitions bootstrap q*_b, b = 1…B : bootstrap par grappes de tâches, stratifié, chaque répétition moyenne
  sur K ordres et tirages du validateur (5.5, point 2.i) ;
- pour le bootstrap-t, l'écart type de q estimé sur l'échantillon d'origine (se) et sur chaque répétition (se*_b) ;
- ses valeurs jackknife q_(−g) : chaque tâche retirée à son tour, chaque valeur moyenne sur K ordres.

Méthodes (écrites avant la simulation de couverture, 5.13) :
- (i)   bootstrap par grappes : intervalle percentile réuni avec l'intervalle normal (centre ± 1,96 × écart type des
        répétitions bootstrap) ;
- (ii)  bootstrap-t par grappes, sur les mêmes répétitions : t*_b = (q*_b − q) ÷ se*_b ; intervalle à queues égales
        [q − t*_(97,5 %) × se ; q − t*_(2,5 %) × se] ;
- (iii) jackknife-t par tâche : q ± t(G − 1 ; 97,5 %) × se_J, où G est le nombre de tâches et se_J l'écart type
        jackknife (stratifié : somme sur les strates de (G_h − 1) ÷ G_h × Σ (q_(−g) − moyenne de la strate)²).

Écart type d'un rapport de sommes par grappes (`se_rapport`) : linéarisation, celle du bootstrap-t ; pour
q = Σ a_g ÷ Σ d_g, se² = Σ_h G_h ÷ (G_h − 1) × Σ_(g ∈ h) (z_g − z̄_h)² ÷ (Σ d_g)², avec z_g = a_g − q d_g.

Règle de choix (5.13) : la première méthode qui couvre au moins 93 % partout, dans l'ordre (i), (ii), (iii) ; sinon,
la méthode dont la pire couverture est la meilleure, et les cellules dont le nombre de grappes tombe dans la zone qui
échoue sont marquées « fragile ». « Fragile » aussi (B4) : la décision diffère entre la méthode retenue et une
seconde méthode (le jackknife-t ; le percentile du bootstrap par grappes si la méthode retenue est le jackknife-t).
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np
from scipy.stats import t as student

Z95 = 1.959963984540054
METHODES = ("i", "ii", "iii")
NOMS_METHODES = {"i": "bootstrap par grappes, percentile réuni avec normal", "ii": "bootstrap-t par grappes",
                 "iii": "jackknife-t par tâche", "percentile": "bootstrap par grappes, percentile seul"}
SEUIL_COUVERTURE = 0.93
PASSE, ECHOUE, INDECISE = "passe", "échoue", "indécise"
_GRAND = 1e300  # remplace ±∞ avant l'interpolation des quantiles (bootstrap-t)


# --------------------------------------------------------------------------
# Les méthodes (dernier axe : répétitions bootstrap, ou tâches pour le jackknife)
# --------------------------------------------------------------------------
def ic_percentile(boot, alpha: float = 0.05) -> tuple:
    b = np.asarray(boot, dtype=float)
    return np.quantile(b, alpha / 2, axis=-1), np.quantile(b, 1 - alpha / 2, axis=-1)


def ic_normal(centre, boot) -> tuple:
    b = np.asarray(boot, dtype=float)
    sd = b.std(axis=-1, ddof=1) if b.shape[-1] > 1 else np.zeros(b.shape[:-1])
    c = np.asarray(centre, dtype=float)
    return c - Z95 * sd, c + Z95 * sd


def ic_bootstrap_reuni(centre, boot) -> tuple:
    """Méthode (i) : percentile réuni avec normal."""
    lp, hp = ic_percentile(boot)
    ln, hn = ic_normal(centre, boot)
    return np.minimum(lp, ln), np.maximum(hp, hn)


def studentiser(boot, centre, se_boot) -> np.ndarray:
    """t*_b = (q*_b − q) ÷ se*_b ; se*_b nul : 0 si q*_b = q, ±∞ sinon."""
    b = np.asarray(boot, dtype=float)
    c = np.asarray(centre, dtype=float)[..., None]
    s = np.asarray(se_boot, dtype=float)
    d = b - c
    with np.errstate(divide="ignore", invalid="ignore"):
        t = np.where(s > 0, d / np.where(s > 0, s, 1.0), np.where(d == 0, 0.0, np.sign(d) * np.inf))
    return t


def _quantile_inf(t, q) -> np.ndarray:
    x = np.clip(np.asarray(t, dtype=float), -_GRAND, _GRAND)
    v = np.quantile(x, q, axis=-1)
    return np.where(v >= _GRAND / 2, np.inf, np.where(v <= -_GRAND / 2, -np.inf, v))


def ic_bootstrap_t(centre, se, boot, se_boot, alpha: float = 0.05) -> tuple:
    """Méthode (ii) : bootstrap-t à queues égales ; se nul : intervalle réduit au centre."""
    t = studentiser(boot, centre, se_boot)
    q_lo, q_hi = _quantile_inf(t, alpha / 2), _quantile_inf(t, 1 - alpha / 2)
    c = np.asarray(centre, dtype=float)
    s = np.asarray(se, dtype=float)
    with np.errstate(invalid="ignore"):
        lo = np.where(s > 0, c - q_hi * s, c)
        hi = np.where(s > 0, c - q_lo * s, c)
    return lo, hi


def variance_jackknife(jack, strates=None) -> np.ndarray:
    """Σ_h (G_h − 1) ÷ G_h × Σ_(g ∈ h) (q_(−g) − moyenne_h)² ; une strate d'une seule tâche n'apporte rien (comme le
    bootstrap stratifié, qui la retire toujours)."""
    j = np.asarray(jack, dtype=float)
    G = j.shape[-1]
    if strates is None:
        strates = np.zeros(G, dtype=np.int64)
    strates = np.asarray(strates)
    var = np.zeros(j.shape[:-1])
    for h in np.unique(strates):
        m = strates == h
        gh = int(m.sum())
        if gh < 2:
            continue
        jh = j[..., m]
        var = var + (gh - 1) / gh * ((jh - jh.mean(axis=-1, keepdims=True)) ** 2).sum(axis=-1)
    return var


def ic_jackknife_t(centre, jack, strates=None, alpha: float = 0.05) -> tuple:
    """Méthode (iii) : centre ± t(G − 1) × se_J ; G = nombre de tâches (5.13)."""
    j = np.asarray(jack, dtype=float)
    G = j.shape[-1]
    se = np.sqrt(variance_jackknife(j, strates))
    tq = float(student.ppf(1 - alpha / 2, G - 1)) if G > 1 else float("inf")
    c = np.asarray(centre, dtype=float)
    with np.errstate(invalid="ignore"):
        return c - tq * se, c + tq * se


def influences_jackknife(jack) -> dict:
    """Descriptif (5.13) : influence de chaque tâche, (G − 1)(moyenne − q_(−g)), et nombre effectif de grappes,
    (Σ infl²)² ÷ Σ infl⁴ (inverse de la concentration des influences au carré)."""
    j = np.asarray(jack, dtype=float)
    G = j.shape[-1]
    infl = (G - 1) * (j.mean(axis=-1, keepdims=True) - j)
    i2 = infl ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        geff = np.where(i2.sum(axis=-1) > 0, i2.sum(axis=-1) ** 2 / np.maximum((i2 ** 2).sum(axis=-1), 1e-300), 0.0)
    return dict(influence=infl, grappes_effectives=geff)


def se_rapport(a, d, strates=None) -> np.ndarray:
    """Écart type linéarisé d'un rapport de sommes par grappes, q = Σ a_g ÷ Σ d_g (dernier axe : grappes)."""
    a = np.asarray(a, dtype=float)
    d = np.asarray(d, dtype=float)
    D = d.sum(axis=-1)
    with np.errstate(divide="ignore", invalid="ignore"):
        q = np.where(D > 0, a.sum(axis=-1) / np.where(D > 0, D, 1.0), 0.0)
    z = a - q[..., None] * d
    G = z.shape[-1]
    if strates is None:
        strates = np.zeros(G, dtype=np.int64)
    strates = np.asarray(strates)
    s2 = np.zeros(z.shape[:-1])
    for h in np.unique(strates):
        m = strates == h
        gh = int(m.sum())
        if gh < 2:
            continue
        zh = z[..., m]
        s2 = s2 + gh / (gh - 1) * ((zh - zh.mean(axis=-1, keepdims=True)) ** 2).sum(axis=-1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(D > 0, np.sqrt(s2) / np.where(D > 0, D, 1.0), 0.0)


# --------------------------------------------------------------------------
# Une quantité et ses intervalles
# --------------------------------------------------------------------------
def verdict(lo, hi, seuil) -> str:
    """« passe » si la borne haute est au plus le seuil ; « échoue » si la borne basse est au-dessus ; « indécise »
    sinon (5.13)."""
    if not (lo == lo and hi == hi):
        return INDECISE
    if hi <= seuil:
        return PASSE
    if lo > seuil:
        return ECHOUE
    return INDECISE


def intervalle(methode: str, centre: float, boot=None, se: Optional[float] = None, se_boot=None, jack=None,
               strates_jack=None) -> tuple:
    """(lo, hi) d'une quantité par la méthode donnée (« i », « ii », « iii » ou « percentile »)."""
    if methode == "i":
        lo, hi = ic_bootstrap_reuni(centre, boot)
    elif methode == "percentile":
        lo, hi = ic_percentile(boot)
    elif methode == "ii":
        if se is None or se_boot is None:
            raise ValueError("bootstrap-t : écarts types requis")
        lo, hi = ic_bootstrap_t(centre, se, boot, se_boot)
    elif methode == "iii":
        lo, hi = ic_jackknife_t(centre, jack, strates_jack)
    else:
        raise ValueError(methode)
    return float(lo), float(hi)


def methode_seconde(retenue: str) -> str:
    """Seconde méthode de « fragile » (B4) : le jackknife-t, ou le percentile si la méthode retenue est le jackknife-t."""
    return "percentile" if retenue == "iii" else "iii"


# --------------------------------------------------------------------------
# Règle de choix (5.13) et zone « fragile »
# --------------------------------------------------------------------------
def choisir_methode(couverture: dict, rhos, gs, seuil: float = SEUIL_COUVERTURE, ordre=METHODES) -> dict:
    """couverture : {(méthode, ρ, G): couverture}. La première méthode qui couvre au moins `seuil` partout ; sinon le
    repli (la meilleure pire couverture, l'ordre départageant les égalités) et sa zone qui échoue."""
    pire = {m: min(couverture[(m, r, g)] for r in rhos for g in gs) for m in ordre}
    for m in ordre:
        if pire[m] >= seuil:
            return dict(methode=m, repli=False, pire=pire, G_sur=min(gs), zone_echec=[], seuil=seuil)
    m = max(ordre, key=lambda x: (pire[x], -ordre.index(x)))
    passe = {g: all(couverture[(m, r, g)] >= seuil for r in rhos) for g in gs}
    g_sur = math.inf
    for g in sorted(gs, reverse=True):
        if not passe[g]:
            break
        g_sur = g
    zone = [g for g in sorted(gs) if g < g_sur]
    return dict(methode=m, repli=True, pire=pire, G_sur=g_sur, zone_echec=zone, seuil=seuil)


def fragile_par_grappes(G: int, choix: dict) -> bool:
    """Repli : une cellule dont le nombre de grappes est sous le plus petit G simulé à partir duquel la méthode passe
    partout (et à tous les G simulés plus grands) est « fragile » ; si la méthode échoue au plus grand G simulé, toutes
    les cellules le sont."""
    return bool(choix.get("repli")) and G < choix.get("G_sur", math.inf)
