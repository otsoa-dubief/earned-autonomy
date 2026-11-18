"""La règle d'autonomie méritée (pièces 4 à 8 de REGLE.md, section 5 du plan).

Deux implémentations de la même logique :
- `RegleUnType` : version de référence, lisible, pour un seul type d'action. Elle sert
  aux tests et à contrôler le moteur vectorisé, pas à produire les résultats.
- `simuler_regle` : le moteur vectorisé sur les répétitions (et sur plusieurs variantes
  de réglage à la fois), qui produit les résultats.

Deux versions (paramètre `version` de config.ParamsRegle) :
- "v2", par défaut : amendement A1 de REGLE.md. Un score réfléchi L par type et par palier visé
  (plancher ln B − a sur le score lui-même) ; au changement de modèle, L = 0 et les erreurs à enjeu
  faible disparaissent.
- "v1" : première passe (compteurs r et s, r plafonné), gardée pour reproduire resultats_v1/.

Résumé de la logique de la v1, par type d'action :
- compteurs r (réussites vérifiées) et s (erreurs vérifiées) ; doute et invérifiable neutres ;
- score de Wald pour chaque palier visé : LLR = s·a − r·b ; l'agent est au plus haut palier
  dont le score est au plus ln B = ln(β/(1−α)) ;
- plancher : r plafonné à r_max = (a − ln B)/b du test du palier 3 ;
- erreur à enjeu faible : descente d'un seul palier par erreur, si le score dépasse ln B ;
- erreur à enjeu moyen ou fort : palier 1, r = 0, s + 1, épreuve de 3 variantes difficiles
  à réussir en entier avant que r recommence à compter ; nouvel essai après 50 actions du type ;
- changement de modèle annoncé : r = 0 partout ; les erreurs à enjeu moyen ou fort deviennent
  des épreuves, chaque épreuve réussie efface une erreur (s − 1) ;
- droits élargis : même chose sur le seul type concerné ;
- consigne modifiée : r divisé par deux sur le type concerné.
"""
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

import config as C
import flux as F


# ==========================================================================
# Version de référence (un type)
# ==========================================================================
class RegleUnType:
    def __init__(self, a2, b2, a3, b3, lnB, rmax, a_palier2, enjeu_haut, epreuves=True,
                 plancher_glissant=False):
        self.a2, self.b2, self.a3, self.b3 = float(a2), float(b2), float(a3), float(b3)
        self.lnB, self.rmax = float(lnB), float(rmax)
        self.a_palier2, self.enjeu_haut = bool(a_palier2), bool(enjeu_haut)
        self.epreuves, self.plancher_glissant = bool(epreuves), bool(plancher_glissant)
        self.r = 0.0
        self.s = 0
        self.palier = 1
        self.E_desc = 0   # épreuves ouvertes par une erreur (même configuration) : n'effacent rien
        self.E_conv = 0   # épreuves issues d'un changement de configuration : effacent une erreur
        self.attente = 0  # actions du type à laisser passer avant le prochain essai

    @classmethod
    def depuis_params(cls, p: C.ParamsRegle, k: int) -> "RegleUnType":
        return cls(p.a2[k], p.b2[k], p.a3[k], p.b3[k], p.lnB, p.rmax[k], p.a_palier2[k],
                   C.ENJEU_HAUT[k], epreuves=p.epreuves, plancher_glissant=p.plancher_glissant)

    # --- score et palier visé
    def llr3(self):
        return self.s * self.a3 - self.r * self.b3

    def llr2(self):
        return self.s * self.a2 - self.r * self.b2

    def cible(self) -> int:
        if self.llr3() <= self.lnB + C.TOL:
            return 3
        if self.a_palier2 and self.llr2() <= self.lnB + C.TOL:
            return 2
        return 1

    def plafond_r(self) -> float:
        if self.plancher_glissant:
            return self.rmax + self.s * self.a3 / self.b3
        return self.rmax

    def epreuves_ouvertes(self) -> int:
        return self.E_desc + self.E_conv

    # --- épreuves
    def epreuve_due(self) -> bool:
        """À l'arrivée d'une action du type : faut-il passer une épreuve maintenant ?"""
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
                self.s -= 1  # après un changement de configuration, l'épreuve efface l'erreur
            self.palier = max(self.palier, self.cible())
        else:
            self.attente = C.EPREUVE_ATTENTE

    # --- preuves
    def succes(self):
        if self.epreuves_ouvertes() > 0:
            return  # r ne compte pas tant qu'une épreuve est ouverte
        self.r = min(self.r + 1.0, self.plafond_r())
        self.palier = max(self.palier, self.cible())

    def erreur(self):
        self.s += 1
        if self.enjeu_haut:
            self.palier = 1
            self.r = 0.0
            if self.epreuves:
                self.E_desc += 1  # le délai après un échec d'épreuve n'est pas remis à zéro
        else:
            c = self.cible()
            if c < self.palier:
                inferieur = self.palier - 1 if self.a_palier2 else 1
                self.palier = max(c, inferieur)

    def neutre(self):
        """Doute ou résultat invérifiable : rien ne change."""

    # --- remises à zéro (pièce 8)
    def changement_configuration(self, oubli_faibles: bool = False):
        """Nouveau modèle (appliqué à tous les types) ou droits élargis (à ce type)."""
        self.r = 0.0
        if self.enjeu_haut:
            if self.epreuves:
                self.E_conv = self.s
                self.E_desc = 0
                self.attente = 0
        elif oubli_faibles:
            self.s = 0
        self.palier = self.cible()

    def consigne_modifiee(self):
        self.r = self.r / 2.0
        self.palier = self.cible()


class RegleUnTypeV2:
    """Version de référence de la v2 (amendement A1), pour un seul type d'action.

    Un score réfléchi par palier visé (L3, et L2 pour les types réversibles) :
    - réussite vérifiée : L = max(L − b, ln B − a) ;
    - erreur à enjeu faible : L + a, puis descente d'un seul palier si le score dépasse ln B ;
    - erreur à enjeu moyen ou fort : L = max(L, 0) + a, palier 1, épreuve ;
    - changement de modèle ou droits élargis : L = 0 ; erreurs à enjeu moyen ou fort → épreuves,
      erreurs à enjeu faible effacées ;
    - consigne modifiée : L divisé par deux si L < 0.
    s ne sert plus qu'à compter les erreurs à enjeu moyen ou fort qui deviendraient des épreuves.
    """

    def __init__(self, a2, b2, a3, b3, lnB, a_palier2, enjeu_haut, epreuves=True):
        self.a2, self.b2, self.a3, self.b3 = float(a2), float(b2), float(a3), float(b3)
        self.lnB = float(lnB)
        self.a_palier2, self.enjeu_haut, self.epreuves = bool(a_palier2), bool(enjeu_haut), bool(epreuves)
        self.L3 = 0.0
        self.L2 = 0.0
        self.s = 0
        self.palier = 1
        self.E_desc = 0
        self.E_conv = 0
        self.attente = 0

    @classmethod
    def depuis_params(cls, p: C.ParamsRegle, k: int) -> "RegleUnTypeV2":
        return cls(p.a2[k], p.b2[k], p.a3[k], p.b3[k], p.lnB, p.a_palier2[k], C.ENJEU_HAUT[k],
                   epreuves=p.epreuves)

    @property
    def plancher3(self):
        return self.lnB - self.a3

    @property
    def plancher2(self):
        return self.lnB - self.a2

    def cible(self) -> int:
        if self.L3 <= self.lnB + C.TOL:
            return 3
        if self.a_palier2 and self.L2 <= self.lnB + C.TOL:
            return 2
        return 1

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
            self.palier = max(self.palier, self.cible())
        else:
            self.attente = C.EPREUVE_ATTENTE

    def succes(self):
        if self.epreuves_ouvertes() > 0:
            return  # le score ne bouge pas tant qu'une épreuve est ouverte
        self.L3 = max(self.L3 - self.b3, self.plancher3)
        if self.a_palier2:
            self.L2 = max(self.L2 - self.b2, self.plancher2)
        self.palier = max(self.palier, self.cible())

    def erreur(self):
        self.s += 1
        if self.enjeu_haut:
            self.L3 = max(self.L3, 0.0) + self.a3
            if self.a_palier2:
                self.L2 = max(self.L2, 0.0) + self.a2
            self.palier = 1
            if self.epreuves:
                self.E_desc += 1
        else:
            self.L3 += self.a3
            if self.a_palier2:
                self.L2 += self.a2
            c = self.cible()
            if c < self.palier:
                inferieur = self.palier - 1 if self.a_palier2 else 1
                self.palier = max(c, inferieur)

    def neutre(self):
        """Doute ou résultat invérifiable : rien ne change."""

    def changement_configuration(self, oubli_faibles: bool = True):
        self.L3 = 0.0
        self.L2 = 0.0
        if self.enjeu_haut:
            if self.epreuves:
                self.E_conv = self.s
                self.E_desc = 0
                self.attente = 0
        else:
            self.s = 0  # A1 : les erreurs à enjeu faible disparaissent
        self.palier = self.cible()

    def consigne_modifiee(self):
        if self.L3 < 0:
            self.L3 /= 2.0
        if self.a_palier2 and self.L2 < 0:
            self.L2 /= 2.0
        self.palier = self.cible()


def regle_un_type(p: C.ParamsRegle, k: int):
    return RegleUnTypeV2.depuis_params(p, k) if p.version == "v2" else RegleUnType.depuis_params(p, k)


# ==========================================================================
# Moteur vectorisé
# ==========================================================================
@dataclass
class ResultatRegle:
    variantes: list
    R: int
    T: int
    P: np.ndarray
    ep_var: np.ndarray
    ep_err: np.ndarray
    premier3: np.ndarray
    premier2: np.ndarray
    premier3_apres: np.ndarray
    n_prom3: np.ndarray
    snap: np.ndarray
    retour1: np.ndarray
    perte3: np.ndarray
    comptes: np.ndarray
    ep_tentatives: np.ndarray
    ep_reussites: np.ndarray
    ep_jugees: np.ndarray
    ep_jugees_ok: np.ndarray
    r_final: Optional[np.ndarray]
    s_final: np.ndarray
    pal_final: np.ndarray
    L3_final: Optional[np.ndarray] = None
    L2_final: Optional[np.ndarray] = None
    journal_epreuves: Optional[list] = None

    def lignes(self, i: int) -> slice:
        return slice(i * self.R, (i + 1) * self.R)

    def extraire(self, i: int) -> dict:
        sl = self.lignes(i)
        return dict(
            P=self.P[sl], ep_var=self.ep_var[sl], ep_err=self.ep_err[sl],
            premier3=self.premier3[sl], premier2=self.premier2[sl], premier3_apres=self.premier3_apres[sl],
            n_prom3=self.n_prom3[sl], snap=self.snap[sl],
            retour1=self.retour1[sl], perte3=self.perte3[sl], comptes=self.comptes[sl],
            ep_tentatives=self.ep_tentatives[sl], ep_reussites=self.ep_reussites[sl],
            ep_jugees=self.ep_jugees[sl], ep_jugees_ok=self.ep_jugees_ok[sl],
            r_final=None if self.r_final is None else self.r_final[sl], s_final=self.s_final[sl],
            pal_final=self.pal_final[sl],
            L3_final=None if self.L3_final is None else self.L3_final[sl],
            L2_final=None if self.L2_final is None else self.L2_final[sl],
        )


def graine_regle(agent_nom: str, melange: str, etiquette: int) -> np.random.SeedSequence:
    ida = C.ID_AGENT.get(agent_nom, 1000 + abs(hash(agent_nom)) % 1000)
    im = list(C.MELANGES_BRUTS).index(melange)
    return np.random.SeedSequence([C.GRAINE, 2, ida, im, etiquette])


def simuler_regle(flux: F.Flux, agent: C.Agent, variantes: list, R: Optional[int] = None,
                  graine=None, journal: bool = False, err=None, dou=None) -> ResultatRegle:
    """Fait tourner une ou plusieurs variantes de la règle sur les mêmes tirages.

    Les lignes sont rangées variante par variante : lignes [i*R, (i+1)*R) = variante i.
    """
    R = flux.R if R is None else R
    fl = flux.sous_ensemble(R)
    V = len(variantes)
    N = V * R
    T = fl.T
    if err is None:
        err = F.erreurs(fl, agent)
    if dou is None:
        dou = F.doutes(fl, agent)
    # colonnes contiguës : on lit le flux pas à pas
    typesT = np.ascontiguousarray(fl.type.T)
    verT = np.ascontiguousarray(fl.verifiable.T)
    douT = np.ascontiguousarray(dou.T)
    errT = np.ascontiguousarray(err.T)
    rng = np.random.default_rng(graine if graine is not None else graine_regle(agent.nom, fl.melange, 0))

    def plat(attr, dtype=float):
        return np.repeat(np.stack([np.asarray(getattr(v, attr), dtype=dtype) for v in variantes]), R, axis=0).ravel()

    versions = {v.version for v in variantes}
    if len(versions) != 1:
        raise ValueError("une seule version de la règle par appel")
    v2 = versions.pop() == "v2"
    a2, b2, a3, b3, rmax = plat("a2"), plat("b2"), plat("a3"), plat("b3"), plat("rmax")
    f2, f3 = plat("plancher2"), np.repeat(np.array([v.plancher3 for v in variantes]), R, axis=0).ravel()
    ap2 = plat("a_palier2", bool)
    lnB = np.repeat(np.array([v.lnB for v in variantes]), R * 8)
    glis = np.repeat(np.array([v.plancher_glissant for v in variantes]), R * 8)
    ratio = a3 / b3
    eh = np.tile(C.ENJEU_HAUT, N)
    remises_l = np.repeat(np.array([v.remises for v in variantes]), R)
    epreuves_l = np.repeat(np.array([v.epreuves for v in variantes]), R)
    doute_err_l = np.repeat(np.array([v.doute_erreur for v in variantes]), R)
    oubli_l = np.repeat(np.array([v.oubli_faibles_au_changement for v in variantes]), R)
    epreuves_p = np.repeat(epreuves_l, 8)
    any_doute_err = bool(doute_err_l.any())

    # état, à plat : indice = ligne*8 + type
    r = np.zeros(N * 8)          # v1
    L3 = np.zeros(N * 8)         # v2
    L2 = np.zeros(N * 8)         # v2
    s = np.zeros(N * 8, dtype=np.int32)
    pal = np.ones(N * 8, dtype=np.int8)
    Ed = np.zeros(N * 8, dtype=np.int32)
    Ec = np.zeros(N * 8, dtype=np.int32)
    att = np.zeros(N * 8, dtype=np.int32)

    PT = np.empty((T, N), dtype=np.int8)
    ep_var = np.zeros((N, T), dtype=np.int8)
    ep_err = np.zeros((N, T), dtype=np.int8)
    premier3 = np.full(N * 8, -1, dtype=np.int32)
    premier2 = np.full(N * 8, -1, dtype=np.int32)
    premier3_apres = np.full(N * 8, -1, dtype=np.int32)
    n_prom3 = np.zeros(N * 8, dtype=np.int32)
    snap = np.zeros(N * 8, dtype=np.int8)
    retour1 = np.full(N * 8, -1, dtype=np.int32)
    perte3 = np.full(N * 8, -1, dtype=np.int32)
    comptes = np.zeros(N * 8 * 3, dtype=np.int32)
    ep_tent = np.zeros(N, dtype=np.int32)
    ep_reu = np.zeros(N, dtype=np.int32)
    ep_jug = np.zeros(N, dtype=np.int32)
    ep_jok = np.zeros(N, dtype=np.int32)
    log = [] if journal else None

    base = np.arange(N, dtype=np.int64) * 8
    # instantané à t = 1 500 pour tous les agents (événement seulement s'il y en a un)
    tc = agent.t_change if agent.t_change is not None else C.T_CHANGEMENT
    qh_avant = np.minimum(C.PLAFOND_DIFFICILE, C.FACTEUR_DIFFICILE * F.q_regle_par_type(agent, False))
    qh_apres = np.minimum(C.PLAFOND_DIFFICILE, C.FACTEUR_DIFFICILE * F.q_regle_par_type(agent, True))
    pd = agent.proba_doute_epreuve
    suivi_actif = False

    def cible(ii):
        lb = lnB[ii] + C.TOL
        if v2:
            ok3 = L3[ii] <= lb
            ok2 = ap2[ii] & (L2[ii] <= lb)
        else:
            sv = s[ii]
            rv = r[ii]
            ok3 = sv * a3[ii] - rv * b3[ii] <= lb
            ok2 = ap2[ii] & (sv * a2[ii] - rv * b2[ii] <= lb)
        return np.where(ok3, 3, np.where(ok2, 2, 1)).astype(np.int8)

    def suivre_descentes(ii, t):
        if not suivi_actif or ii.size == 0:
            return
        pv = pal[ii]
        m1 = (pv == 1) & (retour1[ii] < 0) & (snap[ii] >= 2)
        retour1[ii[m1]] = t
        m3 = (pv < 3) & (perte3[ii] < 0) & (snap[ii] == 3)
        perte3[ii[m3]] = t

    tous_types = np.arange(C.N_MERITES)

    for t in range(T):
        # ---- 1. événement de configuration (avant l'action t)
        if t == tc:
            snap[:] = pal
            suivi_actif = True
            lignes_ev = np.nonzero(remises_l)[0]
            if agent.evenement == "modele" and lignes_ev.size:
                ii = (lignes_ev[:, None] * 8 + tous_types[None, :]).ravel()
                r[ii] = 0.0
                L3[ii] = 0.0
                L2[ii] = 0.0
                hi = ii[eh[ii] & epreuves_p[ii]]
                Ec[hi] = s[hi]
                Ed[hi] = 0
                att[hi] = 0
                if v2:
                    lo = ii[~eh[ii]]  # A1 : les erreurs à enjeu faible disparaissent
                else:
                    lo = ii[~eh[ii] & np.repeat(oubli_l[lignes_ev], C.N_MERITES)]
                s[lo] = 0
                pal[ii] = cible(ii)
                suivre_descentes(ii, t)
            elif agent.evenement == "consigne_SOR" and lignes_ev.size:
                ii = lignes_ev * 8 + C.SOR
                if v2:
                    L3[ii] = np.where(L3[ii] < 0, L3[ii] / 2.0, L3[ii])
                    L2[ii] = np.where(L2[ii] < 0, L2[ii] / 2.0, L2[ii])
                else:
                    r[ii] = r[ii] / 2.0
                pal[ii] = cible(ii)
                suivre_descentes(ii, t)

        k = np.tile(typesT[t], V).astype(np.int64)
        idx = base + k

        # ---- 2. épreuves dues à l'arrivée d'une action du type
        Etot = Ed[idx] + Ec[idx]
        pend = Etot > 0
        if pend.any():
            lp = np.nonzero(pend)[0]
            ip = idx[lp]
            w = att[ip]
            dec = w > 0
            att[ip[dec]] = w[dec] - 1
            la = lp[~dec]
            if la.size:
                ia = idx[la]
                ka = k[la]
                ph = (qh_apres if (tc >= 0 and t >= tc) else qh_avant)[ka]
                de = doute_err_l[la]
                n = la.size
                if pd > 0:
                    D_neutre = rng.negative_binomial(C.EPREUVE_VARIANTES, 1 - pd, size=n)
                    Dd = rng.binomial(C.EPREUVE_VARIANTES, pd, size=n)
                else:
                    D_neutre = np.zeros(n, dtype=np.int64)
                    Dd = np.zeros(n, dtype=np.int64)
                juges = np.where(de, C.EPREUVE_VARIANTES - Dd, C.EPREUVE_VARIANTES)
                J = rng.binomial(juges, ph)
                Dv = np.where(de, Dd, D_neutre)
                Jd = rng.binomial(Dv, ph)
                nvar = np.where(de, C.EPREUVE_VARIANTES, C.EPREUVE_VARIANTES + D_neutre)
                reussie = (J == 0) & np.where(de, Dd == 0, True)
                ep_var[la, t] = np.minimum(nvar, 127)
                ep_err[la, t] = np.minimum(J + Jd, 127)
                ep_tent[la] += 1
                ep_reu[la] += reussie
                ep_jug[la] += juges
                ep_jok[la] += juges - J
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
                    pal[ok_i] = np.maximum(pal[ok_i], cible(ok_i))
                ko_i = ia[~reussie]
                att[ko_i] = C.EPREUVE_ATTENTE

        # ---- 3. l'action est exécutée au palier courant
        palk = pal[idx]
        PT[t] = palk
        comptes[idx * 3 + (palk - 1)] += 1

        # ---- 4. preuves (contrôle automatique)
        v = np.tile(verT[t], V)
        d = np.tile(douT[t], V)
        e = np.tile(errT[t], V)
        nonpla = k != C.PLA
        juge = nonpla & v & ~d
        ok = juge & ~e
        ko = juge & e
        if any_doute_err:
            ko |= nonpla & d & doute_err_l

        # réussites
        li = np.nonzero(ok)[0]
        if li.size:
            ii = idx[li]
            libre = (Ed[ii] + Ec[ii]) == 0
            ii = ii[libre]
            if ii.size:
                if v2:
                    L3[ii] = np.maximum(L3[ii] - b3[ii], f3[ii])
                    L2[ii] = np.maximum(L2[ii] - b2[ii], f2[ii])
                else:
                    plafond = np.where(glis[ii], rmax[ii] + s[ii] * ratio[ii], rmax[ii])
                    r[ii] = np.minimum(r[ii] + 1.0, plafond)
                ancien = pal[ii]
                nouveau = np.maximum(ancien, cible(ii))
                pal[ii] = nouveau
                prom3 = (nouveau == 3) & (ancien < 3)
                if prom3.any():
                    ip3 = ii[prom3]
                    n_prom3[ip3] += 1
                    m3 = premier3[ip3] < 0
                    premier3[ip3[m3]] = t
                    if suivi_actif:
                        m3a = premier3_apres[ip3] < 0
                        premier3_apres[ip3[m3a]] = t
                m2 = (nouveau >= 2) & (premier2[ii] < 0)
                premier2[ii[m2]] = t

        # erreurs
        li = np.nonzero(ko)[0]
        if li.size:
            ii = idx[li]
            s[ii] += 1
            haut = eh[ii]
            ih = ii[haut]
            if ih.size:
                pal[ih] = 1
                if v2:
                    L3[ih] = np.maximum(L3[ih], 0.0) + a3[ih]
                    L2[ih] = np.maximum(L2[ih], 0.0) + a2[ih]
                else:
                    r[ih] = 0.0
                Ed[ih] += epreuves_p[ih].astype(np.int32)
            ib = ii[~haut]
            if ib.size:
                if v2:
                    L3[ib] += a3[ib]
                    L2[ib] += a2[ib]
                c = cible(ib)
                cur = pal[ib]
                inferieur = np.where(ap2[ib], cur - 1, 1).astype(np.int8)
                inferieur = np.maximum(inferieur, 1)
                pal[ib] = np.where(c < cur, np.maximum(c, inferieur), cur)
            suivre_descentes(ii, t)

    return ResultatRegle(
        variantes=variantes, R=R, T=T, P=np.ascontiguousarray(PT.T), ep_var=ep_var, ep_err=ep_err,
        premier3=premier3.reshape(N, 8), premier2=premier2.reshape(N, 8),
        premier3_apres=premier3_apres.reshape(N, 8), n_prom3=n_prom3.reshape(N, 8), snap=snap.reshape(N, 8),
        retour1=retour1.reshape(N, 8), perte3=perte3.reshape(N, 8), comptes=comptes.reshape(N, 8, 3),
        ep_tentatives=ep_tent, ep_reussites=ep_reu, ep_jugees=ep_jug, ep_jugees_ok=ep_jok,
        r_final=None if v2 else r.reshape(N, 8), s_final=s.reshape(N, 8), pal_final=pal.reshape(N, 8),
        L3_final=L3.reshape(N, 8) if v2 else None, L2_final=L2.reshape(N, 8) if v2 else None,
        journal_epreuves=log,
    )


def rejouer_reference(flux: F.Flux, agent: C.Agent, p: C.ParamsRegle, rep: int,
                      journal_epreuves: list, ligne: int) -> np.ndarray:
    """Rejoue une répétition avec la version de référence (mêmes issues d'épreuve).

    Sert au test de cohérence entre la version lisible et le moteur vectorisé.
    """
    T = flux.T
    fl1 = flux.sous_ensemble(flux.R)
    err = F.erreurs(fl1, agent)[rep]
    dou = F.doutes(fl1, agent)[rep]
    ver = flux.verifiable[rep]
    typ = flux.type[rep]
    issues = {(t, k): ok for (li, t, k, ok) in journal_epreuves if li == ligne}
    regles = [regle_un_type(p, k) for k in range(C.N_MERITES)]
    out = np.empty(T, dtype=np.int8)
    # instantané à t = 1 500 pour tous les agents (événement seulement s'il y en a un)
    tc = agent.t_change if agent.t_change is not None else C.T_CHANGEMENT
    for t in range(T):
        if t == tc and p.remises:
            if agent.evenement == "modele":
                for rg in regles:
                    if p.version == "v2":
                        rg.changement_configuration()
                    else:
                        rg.changement_configuration(p.oubli_faibles_au_changement)
            elif agent.evenement == "consigne_SOR":
                regles[C.SOR].consigne_modifiee()
        k = int(typ[t])
        if k == C.PLA:
            out[t] = 1
            continue
        rg = regles[k]
        if rg.epreuve_due():
            rg.resultat_epreuve(issues[(t, k)])
        out[t] = rg.palier
        if p.doute_erreur and dou[t]:
            rg.erreur()
        elif ver[t] and not dou[t]:
            if err[t]:
                rg.erreur()
            else:
                rg.succes()
        else:
            rg.neutre()
    return out
