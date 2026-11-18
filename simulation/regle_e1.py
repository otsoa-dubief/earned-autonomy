"""Moteur de l'exploration E1 (PLAN_EXPLORATION_E1.md) : règles A (Wald, amendement A1) et B
(séries), témoins, comptabilité. Le chemin v2 (regle.py, mesures.py, temoins.py) n'est pas touché.

- `RegleUnTypeB` : implémentation de référence de la règle B pour un type (section 2, points 1 à 8).
  La règle A garde sa référence v2, `regle.RegleUnTypeV2`.
- `simuler_e1` : moteur vectorisé (variantes × répétitions), les deux familles dans la même boucle,
  sur les mêmes tirages ; modes de résistance (mesure 9) ; comptabilité par paquets de pas.
- Interrupteurs d'E1 : `RegleE1.lec_autonome` (LEC agit seule dès le départ) et
  `Compteur(lec_sans_effet=True)` (une erreur de lecture n'est pas un dégât). Épreuves à blanc :
  leurs erreurs ne sont jamais des dégâts ; elles sont comptées à part (colonne « avec épreuves »).

Disposition des tableaux du flux : temps d'abord, (T, R), pour lire le flux pas à pas.
"""
from collections import deque
from dataclasses import dataclass
from typing import Optional

import numpy as np

import config as C
import config_e1 as E
import flux as F
import regle as RG

GRAND = 1 << 40  # « N » d'une ligne de la famille A : jamais atteint


# ==========================================================================
# Référence : la règle B pour un type
# ==========================================================================
class RegleUnTypeB:
    """Règle B, les séries (plan E1, section 2), pour un seul type d'action.

    1. palier 3 après N réussites vérifiées d'affilée sur le type (compteur c) ;
    2. toute erreur, à n'importe quel palier, remet c à 0 ;
    3. erreur au palier 3 : à enjeu moyen ou fort, palier 1 et épreuve ; à enjeu faible, palier 2 si le
       type est réversible, palier 1 sinon. Le palier 2 garde le score de Wald v2 (réglages de départ),
       qui décide seul du palier 2 sous le palier 3 ;
    4. pièce 7.3 : après une erreur à enjeu moyen ou fort (à tout palier), la montée suivante exige
       ⌈1,25 × N⌉ ; les suivantes, sans nouvelle erreur, N ;
    5. c ne bouge pas tant qu'une épreuve est ouverte ;
    6. c est plafonné à la longueur exigée (N, ou ⌈1,25 N⌉ pendant une montée allongée) ; une consigne
       modifiée divise c par deux (⌊c/2⌋, soit ⌊N/2⌋ au palier 3) et fait perdre le palier 3 ;
    7. changement de modèle ou droits élargis : c = 0, plus d'allongement ; les erreurs moyennes ou
       fortes gardées en mémoire (s) deviennent des épreuves, les faibles disparaissent ;
    8. invérifiable et doute : neutres.
    Les épreuves suivent exactement la v2 (3 variantes difficiles, nouvel essai après 50 actions).
    """

    def __init__(self, N, a2, b2, lnB, a_palier2, enjeu_haut, epreuves=True):
        self.N = int(N)
        self.N_allonge = E.n_allonge(self.N)
        self.a2, self.b2, self.lnB = float(a2), float(b2), float(lnB)
        self.a_palier2, self.enjeu_haut, self.epreuves = bool(a_palier2), bool(enjeu_haut), bool(epreuves)
        self.c = 0
        self.allonge = False
        self.L2 = 0.0
        self.s = 0
        self.palier = 1
        self.E_desc = 0
        self.E_conv = 0
        self.attente = 0

    @classmethod
    def depuis_regle(cls, regle: E.RegleE1, k: int) -> "RegleUnTypeB":
        p = regle.params
        return cls(regle.N[k], p.a2[k], p.b2[k], p.lnB, p.a_palier2[k], C.ENJEU_HAUT[k])

    @property
    def longueur(self) -> int:
        return self.N_allonge if self.allonge else self.N

    @property
    def plancher2(self):
        return self.lnB - self.a2

    def cible(self) -> int:
        if self.c >= self.longueur:
            return 3
        if self.a_palier2 and self.L2 <= self.lnB + C.TOL:
            return 2
        return 1

    def _monter(self):
        nouveau = max(self.palier, self.cible())
        if nouveau == 3 and self.palier < 3 and self.allonge:
            self.allonge = False          # la montée allongée est faite : les suivantes exigent N
            self.c = min(self.c, self.N)
        self.palier = nouveau

    def epreuves_ouvertes(self) -> int:
        return self.E_desc + self.E_conv

    def epreuve_due(self) -> bool:
        if self.epreuves_ouvertes() == 0:
            return False
        if self.attente > 0:
            self.attente -= 1
            return False
        return True

    def resultat_epreuve(self, reussie: bool):
        if reussie:
            if self.E_desc > 0:
                self.E_desc -= 1
            else:
                self.E_conv -= 1
                self.s -= 1
            self._monter()
        else:
            self.attente = C.EPREUVE_ATTENTE

    def succes(self):
        if self.epreuves_ouvertes() > 0:
            return
        self.c = min(self.c + 1, self.longueur)
        if self.a_palier2:
            self.L2 = max(self.L2 - self.b2, self.plancher2)
        self._monter()

    def erreur(self):
        self.s += 1
        self.c = 0
        if self.enjeu_haut:
            self.allonge = True
            if self.a_palier2:
                self.L2 = max(self.L2, 0.0) + self.a2
            self.palier = 1
            if self.epreuves:
                self.E_desc += 1
        else:
            if self.a_palier2:
                self.L2 += self.a2
            c = self.cible()
            if c < self.palier:
                inferieur = self.palier - 1 if self.a_palier2 else 1
                self.palier = max(c, inferieur)

    def neutre(self):
        """Doute ou résultat invérifiable : rien ne change."""

    def changement_configuration(self):
        self.c = 0
        self.allonge = False
        self.L2 = 0.0
        if self.enjeu_haut:
            if self.epreuves:
                self.E_conv = self.s
                self.E_desc = 0
                self.attente = 0
        else:
            self.s = 0
        self.palier = self.cible()

    def consigne_modifiee(self):
        self.c //= 2
        if self.a_palier2 and self.L2 < 0:
            self.L2 /= 2.0
        self.palier = self.cible()


def regle_un_type_e1(regle: E.RegleE1, k: int):
    if regle.famille == "B":
        return RegleUnTypeB.depuis_regle(regle, k)
    return RG.RegleUnTypeV2.depuis_params(regle.params, k)


# ==========================================================================
# Le flux d'une tâche (temps d'abord)
# ==========================================================================
@dataclass
class FluxE1:
    melange: str
    R: int
    T: int
    typ: np.ndarray    # (T, R) int8
    ver: np.ndarray    # (T, R) bool
    dif: np.ndarray    # (T, R) bool
    err: np.ndarray    # (T, R) bool, propre à l'agent
    dou: np.ndarray    # (T, R) bool, propre à l'agent
    rate: np.ndarray   # (T, R) bool : le validateur laisse passer l'erreur (u_val < e)
    rat10: np.ndarray  # (T, R) bool : le contrôle automatique rate l'erreur (graine à part)

    def sous_ensemble(self, R: int) -> "FluxE1":
        return FluxE1(self.melange, R, self.T, *(np.ascontiguousarray(getattr(self, a)[:, :R])
                                                 for a in ("typ", "ver", "dif", "err", "dou", "rate", "rat10")))


def graine_bloc(horizon: str, melange: str, j: int):
    """Graine du flux d'un bloc. Au court, le bloc 0 est le flux de la deuxième passe (mêmes tirages)."""
    im = E.MELANGES.index(melange)
    if horizon == "court":
        return None if j == 0 else [C.GRAINE, 12, im, j]
    return [C.GRAINE, 10, im, j]


def graine_ratees(horizon: str, melange: str, j: int):
    """Graine à part du contrôle imparfait (mesure 9) : distincte de celle du flux."""
    return [C.GRAINE, 11, E.MELANGES.index(melange), list(E.HORIZONS).index(horizon), j]


def flux_e1(horizon: str, melange: str, agent: C.Agent, blocs, T: Optional[int] = None,
            taille_bloc: Optional[int] = None) -> FluxE1:
    """Concatène les blocs `blocs` du flux (répétitions emboîtées : les blocs 0.. sont communs)."""
    T = E.HORIZONS[horizon]["T"] if T is None else T
    Rb = E.HORIZONS[horizon]["bloc"] if taille_bloc is None else taille_bloc
    R = Rb * len(blocs)
    arr = {a: np.empty((T, R), dtype=np.int8 if a == "typ" else bool)
           for a in ("typ", "ver", "dif", "err", "dou", "rate", "rat10")}
    for i, j in enumerate(blocs):  # rempli bloc par bloc : la mémoire reste celle du flux final
        cs = slice(i * Rb, (i + 1) * Rb)
        g = graine_bloc(horizon, melange, j)
        fl = F.generer_flux(melange, Rb, T) if g is None else F.generer_flux(melange, Rb, T, seed=g)
        arr["err"][:, cs] = F.erreurs(fl, agent).T
        arr["dou"][:, cs] = F.doutes(fl, agent).T
        arr["rate"][:, cs] = (fl.u_val < E.E_VALIDATEUR).T
        arr["typ"][:, cs] = fl.type.T
        arr["ver"][:, cs] = fl.verifiable.T
        arr["dif"][:, cs] = fl.difficile.T
        del fl
        rng = np.random.default_rng(graine_ratees(horizon, melange, j))
        arr["rat10"][:, cs] = (rng.random((Rb, T), dtype=np.float32) < E.PART_RATEE).T
    return FluxE1(melange, R, T, **arr)


# ==========================================================================
# Comptabilité (commune aux règles et aux témoins)
# ==========================================================================
class Compteur:
    """Agrégats par ligne. Excès = erreurs exécutées au palier 3 que « tout faire valider » aurait
    arrêtées (même tirage du validateur) : c'est la différence appariée des dégâts, ligne par ligne.
    Palier 1 ou doute : validation ; palier 2 : une erreur est exécutée puis corrigée (charge) sauf si
    le validateur la rate (dégât, comme sous « tout faire valider ») ; palier 3 : l'erreur est un dégât.
    Avec lec_sans_effet (E1, décision 4), une erreur de lecture n'est jamais un dégât."""

    def __init__(self, N: int, tc: int, lec_sans_effet: bool = True):
        self.N, self.tc, self.lec_sans_effet = N, tc, lec_sans_effet
        z = lambda *s: np.zeros(s, dtype=np.int64)  # noqa: E731
        self.exc, self.exc_w = z(N, 3), z(N, 3)
        self.dmg, self.dmg_w = z(N, 3), z(N, 3)          # dégâts absolus (hors épreuves)
        self.val_nl, self.dou_nl, self.cor_nl = z(N), z(N), z(N)
        self.val_tot, self.dou_tot, self.cor_tot = z(N), z(N), z(N)
        self.comptes, self.comptes_w = z(N, 8, 3), z(N, 8, 3)

    def accumuler(self, P: np.ndarray, t0: int, fx: FluxE1):
        """P : paliers (Tc, N) des pas t0.. ; N = V × R lignes, rangées variante par variante."""
        Tc, N = P.shape
        R = fx.R
        V = N // R
        sl = slice(t0, t0 + Tc)
        ty, d, e, rt = fx.typ[sl], fx.dou[sl], fx.err[sl], fx.rate[sl]
        nonlec = ty != C.LEC
        eff = nonlec if self.lec_sans_effet else np.ones_like(nonlec)
        niv = C.ENJEU[ty]
        x_base = e & ~rt & ~d & eff          # excès si exécutée au palier 3
        dmg_base = e & eff                   # dégât si au palier 3 (et pas de doute)
        dmg_val = e & rt & eff               # dégât si validée ou corrigée (le validateur rate)
        cor_base = e & ~rt & ~d              # correction au palier 2
        w0 = min(max(0, self.tc - t0), Tc)   # premier pas de la fenêtre dans ce paquet
        niv_m = [niv == j for j in range(3)]
        x_niv = [x_base & m for m in niv_m]
        cle_base = (np.arange(R, dtype=np.int64)[None, :] * 8 + ty) * 3
        for v in range(V):
            cs = slice(v * R, (v + 1) * R)
            p = P[:, cs]
            p1, p2, p3 = p == 1, p == 2, p == 3
            for j in range(3):
                xj = p3 & x_niv[j]
                self.exc[cs, j] += xj.sum(axis=0)
                dj = ((p3 & ~d & dmg_base) | ((~p3 | d) & dmg_val)) & niv_m[j]
                self.dmg[cs, j] += dj.sum(axis=0)
                if w0 < Tc:
                    self.exc_w[cs, j] += xj[w0:].sum(axis=0)
                    self.dmg_w[cs, j] += dj[w0:].sum(axis=0)
            dsup = d & ~p1
            cor = p2 & cor_base
            self.val_tot[cs] += p1.sum(axis=0)
            self.dou_tot[cs] += dsup.sum(axis=0)
            self.cor_tot[cs] += cor.sum(axis=0)
            self.val_nl[cs] += (p1 & nonlec).sum(axis=0)
            self.dou_nl[cs] += (dsup & nonlec).sum(axis=0)
            self.cor_nl[cs] += (cor & nonlec).sum(axis=0)
            cle = cle_base + (p.astype(np.int64) - 1)
            self.comptes[cs] += np.bincount(cle.ravel(), minlength=R * 24).reshape(R, 8, 3)
            if w0 < Tc:
                self.comptes_w[cs] += np.bincount(cle[w0:].ravel(), minlength=R * 24).reshape(R, 8, 3)


# ==========================================================================
# Moteur vectorisé
# ==========================================================================
@dataclass
class ResultatE1:
    variantes: list
    R: int
    T: int
    tc: int
    cpt: Compteur
    n_ep: np.ndarray
    n_ep_w: np.ndarray
    ep_err: np.ndarray       # (N, 3) erreurs (vraies) des variantes d'épreuve, par niveau
    ep_err_w: np.ndarray
    ep_tentatives: np.ndarray
    ep_reussites: np.ndarray
    premier3: np.ndarray     # (N, 8) premier pas au palier 3 (−1 : jamais)
    premier2: np.ndarray
    premier3_apres: np.ndarray
    n_prom3: np.ndarray
    snap: np.ndarray         # palier à tc
    retour1: np.ndarray      # premier retour au palier 1 après tc (types au palier 2 ou 3 à tc)
    perte3: np.ndarray       # première perte du palier 3 après tc (types au palier 3 à tc)
    dtype_perte3: np.ndarray  # actions du type entre tc et la perte du palier 3
    err_delai: np.ndarray    # erreurs exécutées au palier 3 sur le type entre tc et la perte du palier 3
    n_stints: np.ndarray     # périodes au palier 3 après tc (amendement E1-a)
    max_cst: np.ndarray      # erreurs constatées qui passent dans une même période, au plus (après tc)
    tot_cst: np.ndarray      # erreurs constatées passées au palier 3 après tc
    tot_inv: np.ndarray      # erreurs sur des actions invérifiables passées au palier 3 après tc
    tot_rat: np.ndarray      # erreurs vérifiables ratées par le contrôle imparfait (modes de résistance)
    pertes3_avant: np.ndarray  # pertes du palier 3 avant tc
    pal_final: np.ndarray
    P: Optional[np.ndarray] = None   # (T, N) si demandé
    journal_epreuves: Optional[list] = None

    def lignes(self, i: int) -> slice:
        return slice(i * self.R, (i + 1) * self.R)


def simuler_e1(fx: FluxE1, agent: C.Agent, variantes: list, graines_modes: dict, tc: Optional[int] = None,
               journal: bool = False, garder_P: bool = False, paquet: int = 200,
               lec_sans_effet: bool = True) -> ResultatE1:
    """Fait tourner les variantes (RegleE1, mode) sur les mêmes tirages ; lignes variante par variante.

    graines_modes : {mode: graine} des tirages d'épreuve, un flux aléatoire par mode, pour que les
    lignes « base » ne dépendent pas des modes de résistance lancés avec elles.
    tc : instant du changement (et de l'instantané) ; par défaut, celui de l'agent, sinon T // 2.
    """
    R, T = fx.R, fx.T
    V = len(variantes)
    N = V * R
    if tc is None:
        tc = agent.t_change if agent.t_change is not None else T // 2
    regles = [v[0] for v in variantes]
    modes = [v[1] for v in variantes]
    for m in modes:
        if m not in E.MODES:
            raise ValueError(m)

    def par_type(vals, dtype):
        return np.repeat(np.stack([np.asarray(x, dtype=dtype) for x in vals]), R, axis=0).ravel()

    def par_ligne(vals, dtype):
        return np.repeat(np.asarray(vals, dtype=dtype), R)

    est_B = [r.famille == "B" for r in regles]
    zeros8 = np.zeros(8)
    a2 = par_type([r.params.a2 for r in regles], float)
    b2 = par_type([r.params.b2 for r in regles], float)
    f2 = par_type([r.params.plancher2 for r in regles], float)
    ap2 = par_type([r.params.a_palier2 for r in regles], bool)
    a3 = par_type([zeros8 if b else r.params.a3 for r, b in zip(regles, est_B)], float)
    b3 = par_type([zeros8 if b else r.params.b3 for r, b in zip(regles, est_B)], float)
    f3 = par_type([zeros8 if b else np.broadcast_to(r.params.plancher3, (8,)) for r, b in zip(regles, est_B)],
                  float)
    lnB = par_type([np.full(8, r.params.lnB) for r in regles], float)
    famB = par_type([np.full(8, b) for b in est_B], bool)
    Nn = par_type([r.N if b else np.full(8, GRAND) for r, b in zip(regles, est_B)], np.int64)
    Nl = par_type([r.N_allonge if b else np.full(8, GRAND) for r, b in zip(regles, est_B)], np.int64)
    epreuves8 = par_type([np.full(8, r.params.epreuves) for r in regles], bool)
    remises_l = par_ligne([r.params.remises for r in regles], bool)
    lec_auto = par_ligne([r.lec_autonome for r in regles], bool)
    lec_auto_l = np.nonzero(lec_auto)[0]
    m_rate10 = par_ligne([m == "rate10" for m in modes], bool)
    m_diff = par_ligne([m == "difficiles" for m in modes], bool)
    lignes_retard = np.nonzero(par_ligne([m == "retard10" for m in modes], bool))[0]
    mode_l = par_ligne([E.MODES.index(m) for m in modes], np.int8)
    tous_A = not any(est_B)
    tous_B = all(est_B)
    eh = np.tile(C.ENJEU_HAUT, N)
    rngs = {m: np.random.default_rng(graines_modes[m]) for m in set(modes)}
    modes_presents = [m for m in E.MODES if m in set(modes)]

    # état, à plat : indice = ligne * 8 + type
    pal = np.ones(N * 8, dtype=np.int8)
    if lec_auto_l.size:
        pal[lec_auto_l * 8 + C.LEC] = 3
    L2 = np.zeros(N * 8)
    L3 = np.zeros(N * 8)
    cc = np.zeros(N * 8, dtype=np.int64)
    allonge = np.zeros(N * 8, dtype=bool)
    s = np.zeros(N * 8, dtype=np.int32)
    Ed = np.zeros(N * 8, dtype=np.int32)
    Ec = np.zeros(N * 8, dtype=np.int32)
    att = np.zeros(N * 8, dtype=np.int32)
    cnt = np.zeros(N * 8, dtype=np.int64)
    K = E.RETARD_K
    buf = np.zeros((N * 8, K), dtype=np.int8) if lignes_retard.size else None

    premier3 = np.full(N * 8, -1, dtype=np.int32)
    premier2 = np.full(N * 8, -1, dtype=np.int32)
    premier3_apres = np.full(N * 8, -1, dtype=np.int32)
    n_prom3 = np.zeros(N * 8, dtype=np.int32)
    snap = np.zeros(N * 8, dtype=np.int8)
    retour1 = np.full(N * 8, -1, dtype=np.int32)
    perte3 = np.full(N * 8, -1, dtype=np.int32)
    dtype_perte3 = np.full(N * 8, -1, dtype=np.int64)
    cnt_tc = np.zeros(N * 8, dtype=np.int64)
    err_delai = np.zeros(N * 8, dtype=np.int32)
    pertes3_avant = np.zeros(N * 8, dtype=np.int32)
    en_stint = np.zeros(N * 8, dtype=bool)     # amendement E1-a : périodes au palier 3 après tc
    n_stints = np.zeros(N * 8, dtype=np.int32)
    stint_cst = np.zeros(N * 8, dtype=np.int32)
    max_cst = np.zeros(N * 8, dtype=np.int32)
    tot_cst = np.zeros(N * 8, dtype=np.int32)
    tot_inv = np.zeros(N * 8, dtype=np.int32)
    tot_rat = np.zeros(N * 8, dtype=np.int32)
    n_ep = np.zeros(N, dtype=np.int64)
    n_ep_w = np.zeros(N, dtype=np.int64)
    ep_err = np.zeros((N, 3), dtype=np.int64)
    ep_err_w = np.zeros((N, 3), dtype=np.int64)
    ep_tent = np.zeros(N, dtype=np.int64)
    ep_reu = np.zeros(N, dtype=np.int64)
    log = [] if journal else None

    cpt = Compteur(N, tc, lec_sans_effet)
    Pbuf = np.empty((paquet, N), dtype=np.int8)
    Pall = np.empty((T, N), dtype=np.int8) if garder_P else None
    t0 = 0

    base = np.arange(N, dtype=np.int64) * 8
    qh_avant = C.taux_difficile(F.q_regle_par_type(agent, False))
    qh_apres = C.taux_difficile(F.q_regle_par_type(agent, True))
    pd = agent.proba_doute_epreuve
    suivi = False
    tous_types = np.arange(C.N_MERITES)

    def cible(ii):
        lb = lnB[ii] + C.TOL
        ok2 = ap2[ii] & (L2[ii] <= lb)
        if tous_A:
            ok3 = L3[ii] <= lb
        elif tous_B:
            ok3 = cc[ii] >= np.where(allonge[ii], Nl[ii], Nn[ii])
        else:
            ok3 = np.where(famB[ii], cc[ii] >= np.where(allonge[ii], Nl[ii], Nn[ii]), L3[ii] <= lb)
        return np.where(ok3, 3, np.where(ok2, 2, 1)).astype(np.int8)

    def descentes(ii, ancien, t):
        """Suivi des retraits (après tc) et des fausses alertes (pertes du palier 3 avant tc)."""
        if ii.size == 0:
            return
        pv = pal[ii]
        if not suivi:
            m = (ancien == 3) & (pv < 3)
            pertes3_avant[ii[m]] += 1
            return
        m1 = (pv == 1) & (retour1[ii] < 0) & (snap[ii] >= 2)
        retour1[ii[m1]] = t
        m3 = (pv < 3) & (perte3[ii] < 0) & (snap[ii] == 3)
        i3 = ii[m3]
        perte3[i3] = t
        dtype_perte3[i3] = cnt[i3] - cnt_tc[i3]

    for t in range(T):
        # ---- 1. instantané et événement de configuration (avant l'action t)
        if t == tc:
            snap[:] = pal
            cnt_tc[:] = cnt
            suivi = True
            lignes_ev = np.nonzero(remises_l)[0]
            if agent.evenement == "modele" and lignes_ev.size:
                ii = (lignes_ev[:, None] * 8 + tous_types[None, :]).ravel()
                ii = ii[~((ii % 8 == C.LEC) & lec_auto[ii // 8])]
                ancien = pal[ii].copy()
                cc[ii] = 0
                allonge[ii] = False
                L3[ii] = 0.0
                L2[ii] = 0.0
                hi = ii[eh[ii] & epreuves8[ii]]
                Ec[hi] = s[hi]
                Ed[hi] = 0
                att[hi] = 0
                lo = ii[~eh[ii]]
                s[lo] = 0
                pal[ii] = cible(ii)
                descentes(ii, ancien, t)
            elif agent.evenement == "consigne_SOR" and lignes_ev.size:
                ii = lignes_ev * 8 + C.SOR
                ancien = pal[ii].copy()
                L3[ii] = np.where(L3[ii] < 0, L3[ii] / 2.0, L3[ii])
                L2[ii] = np.where(L2[ii] < 0, L2[ii] / 2.0, L2[ii])
                cc[ii] //= 2
                pal[ii] = cible(ii)
                descentes(ii, ancien, t)

        k = np.tile(fx.typ[t], V).astype(np.int64)
        idx = base + k

        # ---- 2. épreuves dues à l'arrivée d'une action du type
        pend = (Ed[idx] + Ec[idx]) > 0
        if pend.any():
            lp = np.nonzero(pend)[0]
            ip = idx[lp]
            w = att[ip]
            dec = w > 0
            att[ip[dec]] = w[dec] - 1
            la_tous = lp[~dec]
            if la_tous.size:
                ph_t = qh_apres if t >= tc else qh_avant
                for m in modes_presents:
                    la = la_tous[mode_l[la_tous] == E.MODES.index(m)] if len(modes_presents) > 1 else la_tous
                    if la.size == 0:
                        continue
                    rng = rngs[m]
                    ia = idx[la]
                    ka = k[la]
                    ph = ph_t[ka]
                    n = la.size
                    if pd > 0:  # même suite de tirages que la v2 (regle.simuler_regle)
                        D_neutre = rng.negative_binomial(C.EPREUVE_VARIANTES, 1 - pd, size=n)
                        rng.binomial(C.EPREUVE_VARIANTES, pd, size=n)  # Dd : sans usage sans « doute erreur »
                    else:
                        D_neutre = np.zeros(n, dtype=np.int64)
                    J = rng.binomial(C.EPREUVE_VARIANTES, ph)
                    Jd = rng.binomial(D_neutre, ph)
                    nvar = C.EPREUVE_VARIANTES + D_neutre
                    if m == "rate10":
                        Jvu = rng.binomial(J, 1 - E.PART_RATEE)
                    elif m == "difficiles":
                        Jvu = np.zeros_like(J)  # les variantes sont des cas difficiles : erreurs ratées
                    else:
                        Jvu = J
                    reussie = Jvu == 0
                    n_ep[la] += nvar
                    nivk = C.ENJEU[ka]
                    ep_err[la, nivk] += J + Jd
                    if t >= tc:
                        n_ep_w[la] += nvar
                        ep_err_w[la, nivk] += J + Jd
                    ep_tent[la] += 1
                    ep_reu[la] += reussie
                    if log is not None:
                        for li, ki, ok in zip(la.tolist(), ka.tolist(), reussie.tolist()):
                            log.append((li, t, ki, bool(ok)))
                    ok_i = ia[reussie]
                    if ok_i.size:
                        desc = Ed[ok_i] > 0
                        Ed[ok_i[desc]] -= 1
                        conv = ok_i[~desc]
                        Ec[conv] -= 1
                        s[conv] -= 1
                        anc = pal[ok_i]
                        nouv = np.maximum(anc, cible(ok_i))
                        pal[ok_i] = nouv
                        if not tous_A:
                            fin = ok_i[(nouv == 3) & (anc < 3) & allonge[ok_i]]
                            allonge[fin] = False
                            cc[fin] = np.minimum(cc[fin], Nn[fin])
                    att[ia[~reussie]] = C.EPREUVE_ATTENTE

        # ---- 3. l'action est exécutée au palier courant
        palk = pal[idx]
        Pbuf[t - t0] = palk
        if Pall is not None:
            Pall[t] = palk
        if t - t0 + 1 == paquet or t == T - 1:
            cpt.accumuler(Pbuf[:t - t0 + 1], t0, fx)
            t0 = t + 1
        e_vrai = np.tile(fx.err[t], V)
        d = np.tile(fx.dou[t], V)
        v = np.tile(fx.ver[t], V)
        e_vu = e_vrai      # erreurs que le contrôle automatique voit (modes de résistance)
        if m_rate10.any():
            e_vu = e_vu & ~(m_rate10 & np.tile(fx.rat10[t], V))
        if m_diff.any():
            e_vu = e_vu & ~(m_diff & np.tile(fx.dif[t], V))
        if suivi:
            # épisodes d'autonomie après le changement (amendement E1-a, décision 5) : une période au
            # palier 3 commence à la première action du type exécutée au palier 3, finit à la suivante
            # exécutée plus bas ; on y compte les erreurs qui passent
            pk3 = palk == 3
            en = en_stint[idx]
            deb = idx[pk3 & ~en]
            n_stints[deb] += 1
            stint_cst[deb] = 0
            en_stint[deb] = True
            en_stint[idx[~pk3 & en]] = False
            m = pk3 & e_vrai & ~d
            if m.any():
                im_ = idx[m]
                cst = (v & e_vu)[m]            # constatée (aussitôt ou plus tard, en mode retard)
                ic = im_[cst]
                stint_cst[ic] += 1
                max_cst[ic] = np.maximum(max_cst[ic], stint_cst[ic])
                tot_cst[ic] += 1
                tot_inv[im_[~v[m]]] += 1      # invérifiables : ne déclenchent pas le retrait
                tot_rat[im_[v[m] & ~cst]] += 1  # ratées par le contrôle imparfait (résistance)
                im_ = im_[(snap[im_] == 3) & (perte3[im_] < 0)]
                err_delai[im_] += 1

        # ---- 4. preuves (contrôle automatique)
        juge = (k != C.PLA) & v & ~d
        if lec_auto_l.size:
            juge &= ~((k == C.LEC) & lec_auto)
        ok = juge & ~e_vu   # une erreur ratée compte comme une réussite
        ko = juge & e_vu
        if lignes_retard.size:  # constat K actions du type plus tard
            rd = lignes_retard
            ii = idx[rd]
            pos = cnt[ii] % K
            code = np.where(ok[rd], 1, np.where(ko[rd], 2, 0)).astype(np.int8)
            vieux = buf[ii, pos]
            buf[ii, pos] = code
            ok[rd] = vieux == 1
            ko[rd] = vieux == 2
        cnt[idx] += 1

        # réussites
        li = np.nonzero(ok)[0]
        if li.size:
            ii = idx[li]
            ii = ii[(Ed[ii] + Ec[ii]) == 0]
            if ii.size:
                L2[ii] = np.maximum(L2[ii] - b2[ii], f2[ii])
                if tous_A:
                    L3[ii] = np.maximum(L3[ii] - b3[ii], f3[ii])
                else:
                    isB = famB[ii]
                    iA = ii[~isB]
                    if iA.size:
                        L3[iA] = np.maximum(L3[iA] - b3[iA], f3[iA])
                    iB = ii[isB]
                    if iB.size:
                        cc[iB] = np.minimum(cc[iB] + 1, np.where(allonge[iB], Nl[iB], Nn[iB]))
                ancien = pal[ii]
                nouveau = np.maximum(ancien, cible(ii))
                pal[ii] = nouveau
                prom3 = (nouveau == 3) & (ancien < 3)
                if prom3.any():
                    ip3 = ii[prom3]
                    if not tous_A:
                        fin = ip3[allonge[ip3]]
                        allonge[fin] = False
                        cc[fin] = np.minimum(cc[fin], Nn[fin])
                    n_prom3[ip3] += 1
                    m3 = premier3[ip3] < 0
                    premier3[ip3[m3]] = t
                    if suivi:
                        m3a = premier3_apres[ip3] < 0
                        premier3_apres[ip3[m3a]] = t
                m2 = (nouveau >= 2) & (premier2[ii] < 0)
                premier2[ii[m2]] = t

        # erreurs (constatées)
        li = np.nonzero(ko)[0]
        if li.size:
            ii = idx[li]
            ancien = pal[ii].copy()
            s[ii] += 1
            cc[ii] = 0
            haut = eh[ii]
            ih = ii[haut]
            if ih.size:
                pal[ih] = 1
                L3[ih] = np.maximum(L3[ih], 0.0) + a3[ih]
                L2[ih] = np.maximum(L2[ih], 0.0) + a2[ih]
                allonge[ih] = True
                Ed[ih] += epreuves8[ih].astype(np.int32)
            ib = ii[~haut]
            if ib.size:
                L3[ib] += a3[ib]
                L2[ib] += a2[ib]
                c_ = cible(ib)
                cur = pal[ib]
                inferieur = np.maximum(np.where(ap2[ib], cur - 1, 1), 1).astype(np.int8)
                pal[ib] = np.where(c_ < cur, np.maximum(c_, inferieur), cur)
            descentes(ii, ancien, t)

    rs = lambda x: x.reshape(N, 8)  # noqa: E731
    return ResultatE1(
        variantes=variantes, R=R, T=T, tc=tc, cpt=cpt, n_ep=n_ep, n_ep_w=n_ep_w, ep_err=ep_err,
        ep_err_w=ep_err_w, ep_tentatives=ep_tent, ep_reussites=ep_reu, premier3=rs(premier3),
        premier2=rs(premier2), premier3_apres=rs(premier3_apres), n_prom3=rs(n_prom3), snap=rs(snap),
        retour1=rs(retour1), perte3=rs(perte3), dtype_perte3=rs(dtype_perte3), err_delai=rs(err_delai),
        n_stints=rs(n_stints), max_cst=rs(max_cst), tot_cst=rs(tot_cst), tot_inv=rs(tot_inv), tot_rat=rs(tot_rat),
        pertes3_avant=rs(pertes3_avant), pal_final=rs(pal), P=Pall, journal_epreuves=log)


# ==========================================================================
# Référence rejouée (tests de cohérence, action par action)
# ==========================================================================
def rejouer_reference_e1(fx: FluxE1, agent: C.Agent, regle: E.RegleE1, mode: str, rep: int,
                         journal: list, ligne: int, tc: int) -> np.ndarray:
    """Rejoue une répétition avec les références (RegleUnTypeV2 pour A, RegleUnTypeB pour B), avec les
    issues d'épreuve du journal du moteur ; même lecture des preuves (modes de résistance compris)."""
    T = fx.T
    issues = {(t, k): ok for (li, t, k, ok) in journal if li == ligne}
    regles = [regle_un_type_e1(regle, k) for k in range(C.N_MERITES)]
    files = [deque() for _ in range(C.N_MERITES)]
    out = np.empty(T, dtype=np.int8)
    for t in range(T):
        if t == tc and regle.params.remises:
            if agent.evenement == "modele":
                for k, rg in enumerate(regles):
                    if not (k == C.LEC and regle.lec_autonome):
                        rg.changement_configuration()
            elif agent.evenement == "consigne_SOR":
                regles[C.SOR].consigne_modifiee()
        k = int(fx.typ[t, rep])
        if k == C.PLA:
            out[t] = 1
            continue
        if k == C.LEC and regle.lec_autonome:
            out[t] = 3
            continue
        rg = regles[k]
        if rg.epreuve_due():
            rg.resultat_epreuve(issues[(t, k)])
        out[t] = rg.palier
        d = bool(fx.dou[t, rep])
        juge = bool(fx.ver[t, rep]) and not d
        e = bool(fx.err[t, rep])
        if mode == "rate10" and fx.rat10[t, rep]:
            e = False
        if mode == "difficiles" and fx.dif[t, rep]:
            e = False
        code = (2 if e else 1) if juge else 0
        if mode == "retard10":
            files[k].append(code)
            code = files[k].popleft() if len(files[k]) > E.RETARD_K else 0
        if code == 1:
            rg.succes()
        elif code == 2:
            rg.erreur()
        else:
            rg.neutre()
    return out


# ==========================================================================
# Témoins (section 2) : paliers, temps d'abord
# ==========================================================================
def paliers_fixes(nom: str, typ: np.ndarray, lec_autonome: bool = True) -> np.ndarray:
    if nom == "tout_approuver":
        return np.full(typ.shape, 3, dtype=np.int8)
    if nom == "tout_valider":
        P = np.ones(typ.shape, dtype=np.int8)
    elif nom == "liste_fixe":
        P = np.where((typ == C.LEC) | (typ == C.ECR), 3, 1).astype(np.int8)
    elif nom == "tri_risque":
        faible = (C.ENJEU == C.FAIBLE)
        faible[C.PLA] = False
        P = np.where(faible[typ], 3, 1).astype(np.int8)
    else:
        raise ValueError(nom)
    if lec_autonome:
        P[typ == C.LEC] = 3
    return P


def paliers_oracle_p2(typ: np.ndarray, agent: C.Agent, melange: str, tc: int) -> np.ndarray:
    """Oracle avec palier 2 : palier 3 si le vrai taux du moment est au plus la barre ; sinon palier 2
    si le type est réversible ; sinon palier 1. LEC agit toujours seule ; PLA demande toujours."""
    T = typ.shape[0]
    out = np.empty(typ.shape, dtype=np.int8)
    for apres, sl in ((False, slice(0, tc)), (True, slice(tc, T))):
        if sl.start >= sl.stop:
            continue
        q = F.q_regle_par_type(agent, apres)
        pal = np.ones(8, dtype=np.int8)
        for k in range(C.N_MERITES):
            if k == C.LEC:
                pal[k] = 3
                continue
            b = float(E.BARRES[(melange, E.niveau_type(k))])
            pal[k] = 3 if q[k] <= b + C.TOL else (2 if C.A_PALIER2[k] else 1)
        out[sl] = pal[typ[sl]]
    return out


def paliers_hasard(typ: np.ndarray, comptes: np.ndarray, rng) -> np.ndarray:
    """Hasard apparié : chaque type passe, au hasard, la même part du temps aux paliers 2 et 3 que
    sous la règle (moyenne sur les répétitions, comme en v2)."""
    tot = comptes.sum(axis=(0, 2)).astype(np.float64)
    tot[tot == 0] = 1.0
    f3 = (comptes[:, :, 2].sum(axis=0) / tot).astype(np.float32)
    f23 = ((comptes[:, :, 2] + comptes[:, :, 1]).sum(axis=0) / tot).astype(np.float32)
    f3[C.PLA] = 0.0
    f23[C.PLA] = 0.0
    u = rng.random(typ.shape, dtype=np.float32)
    return np.where(u < f3[typ], 3, np.where(u < f23[typ], 2, 1)).astype(np.int8)


def paliers_trois_reussites(fx: FluxE1, lec_autonome: bool = True) -> np.ndarray:
    """Témoin « trois réussites » (palier 3 après 3 réussites d'affilée, retrait à la première erreur),
    temps d'abord ; avec LEC autonome en E1."""
    R, T = fx.R, fx.T
    serie = np.zeros(R * 8, dtype=np.int32)
    pal = np.ones(R * 8, dtype=np.int8)
    base = np.arange(R, dtype=np.int64) * 8
    P = np.empty((T, R), dtype=np.int8)
    for t in range(T):
        k = fx.typ[t].astype(np.int64)
        idx = base + k
        P[t] = pal[idx]
        juge = (k != C.PLA) & fx.ver[t] & ~fx.dou[t]
        ok = juge & ~fx.err[t]
        ko = juge & fx.err[t]
        io = idx[ok]
        serie[io] += 1
        pal[io[serie[io] >= 3]] = 3
        ik = idx[ko]
        serie[ik] = 0
        pal[ik] = 1
    if lec_autonome:
        P[fx.typ == C.LEC] = 3
    return P


def compter_temoin(P: np.ndarray, fx: FluxE1, tc: int, lec_sans_effet: bool = True, paquet: int = 2000) -> Compteur:
    cpt = Compteur(fx.R, tc, lec_sans_effet)
    for t0 in range(0, fx.T, paquet):
        cpt.accumuler(P[t0:t0 + paquet], t0, fx)
    return cpt
