"""Moteur vectorisé du rejeu et comptabilité (PLAN_EXPERIENCE.md, 5.6 et 5.8 ; phase 2 : 5.10, 5.11 et 5.13).

Adapté de `regle_e1.simuler_e1` et de `regle_e1.Compteur` (E1, inchangés) :
- types paramétrés (`types_regle`, 9 codes ; LEC n'entre jamais dans une suite) ;
- preuve et dégât séparés (`erreur_preuve`, `erreur_degat`, 5.4) ; réussite lue sur le verdict (`reussite`), puisque
  des écritures vérifiables peuvent être neutres (doublon sans effet, alerte levée) ;
- écritures plafonnées : drapeau d'une écriture typée (Q4 b) — exécutées au palier 1, leurs erreurs comptent (remise à
  zéro, palier 1, épreuve), leurs réussites non ; elles ne déclenchent pas d'épreuve et n'en font pas avancer
  l'attente ;
- épreuves lues dans des parties enregistrées (`epreuves`, 5.9), par un fournisseur d'issues ; file des cas fautifs ;
- longueurs variables : code VIDE (5.5, point 6).

Phase 2 :
- jonction d'un scénario de changement de modèle (5.10 ; branche « modele » de `simuler_e1`) : `jonction` donne, par
  colonne, le premier pas du second segment. Mode annoncé : avant cette écriture, c = 0, L = 0, plus d'allongement ;
  les erreurs moyennes et fortes gardées en mémoire deviennent des épreuves converties (Ec), leurs cas étant leurs
  écritures fautives (donc leurs tâches) ; les faibles sont effacées. Mode silencieux : aucun événement. Dans les deux
  modes, suivi après la jonction : palier à la jonction, premier palier 3 après, perte du palier 3 (délai en écritures
  du type, erreurs passées pendant ce délai), périodes d'autonomie et erreurs constatées par période (amendement E1-a,
  décision 5), comptes après la jonction ;
- constat différé (`retard`, test retard10, 5.11 ; logique d'E1) : la preuve d'une écriture arrive `retard` écritures
  du type plus tard ;
- comptes par grappe (`grappes`) : dégâts en plus, validations et corrections par occurrence de tâche et par groupe de
  colonnes (une répétition bootstrap), pour l'écart type linéarisé du bootstrap-t (5.13).

Pour toutes les règles, à chaque écriture w de type k, dans l'ordre de la suite (5.6) :
1. si une épreuve est due, on la passe d'abord (5.9) ;
2. le palier d'exécution est le palier courant du type, forcé à 1 si w est plafonnée ;
3. on fait la comptabilité (5.8) ;
4. on met à jour la règle : réussite si w est vérifiable et juste ; erreur si `erreur_preuve` ; neutre sinon.

Disposition des tableaux : temps d'abord, (T, lignes) ; lignes rangées règle par règle : [i R, (i + 1) R) = règle i.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Optional

import numpy as np

import config as C

from . import epreuves as EP
from . import types_regle as TY
from .regles import GRAND

NT = TY.NT


# ==========================================================================
# Comptabilité (5.8), commune aux règles et aux témoins
# ==========================================================================
class Compteur:
    """Agrégats par ligne, pour chaque valeur de e (adapté de regle_e1.Compteur).

    - Palier 1 : validation (charge) ; une erreur passe si u_val < e (dégât, comme sous « tout faire valider »).
    - Palier 2 : une erreur est exécutée, puis corrigée si u_val ≥ e (charge) ; sinon c'est un dégât.
    - Palier 3 : une erreur est un dégât.
    - Dégât en plus (`exc`) : erreurs `erreur_degat` exécutées au palier 3 avec u_val ≥ e, celles que « tout faire
      valider » aurait arrêtées : c'est la différence appariée des dégâts.
    - À part (5.4, 5.8) : erreurs des écritures ILL avec verdict (`exc_part`), et invérifiables exécutées au palier 3
      (`inv3`, dégâts possibles, comptés en nombre).
    - Les doutes (une validation chacun, hors suite) et les épreuves (charge à part) sont ajoutés par `mesures`.
    - Phase 2 : `fenetre` (suite avec jonction) : mêmes comptes sur les écritures du second segment (`*_w`) ;
      `grappes` = dict(groupe=(R,) groupe de chaque colonne, n_groupes, G) : dégâts en plus, validations et corrections
      par (groupe, grappe), sommés sur les colonnes du groupe (`exc_g`, `val_g`, `cor_g`).
    """

    def __init__(self, N: int, valeurs_e=(0.05,), grappes: Optional[dict] = None, fenetre: bool = False):
        self.N = N
        self.valeurs_e = tuple(float(e) for e in valeurs_e)
        E_ = len(self.valeurs_e)
        z = lambda *s: np.zeros(s, dtype=np.int64)  # noqa: E731
        self.exc, self.dmg = z(E_, N, 3), z(E_, N, 3)
        self.cor, self.exc_part = z(E_, N), z(E_, N)
        self.val, self.inv3 = z(N), z(N)
        self.comptes = z(N, NT, 3)   # écritures non plafonnées, par type et palier d'exécution
        self.fenetre = bool(fenetre)
        if self.fenetre:
            self.exc_w, self.dmg_w = z(E_, N, 3), z(E_, N, 3)
            self.cor_w, self.val_w = z(E_, N), z(N)
            self.comptes_w = z(N, NT, 3)
        self.grappes = grappes
        if grappes is not None:
            R = len(grappes["groupe"])
            V = N // R if R else 0
            ng, G = int(grappes["n_groupes"]), int(grappes["G"])
            self.exc_g = z(E_, V, ng, 3, G)
            self.cor_g = z(E_, V, ng, G)
            self.val_g = z(V, ng, G)

    def accumuler(self, P: np.ndarray, t0: int, suite):
        """P : paliers (Tc, N) des pas t0.. (0 : VIDE) ; N = V × R lignes, rangées règle par règle."""
        Tc, N = P.shape
        R = suite.R
        V = N // R
        sl = slice(t0, t0 + Tc)
        typ = suite.typ[sl]
        actif = typ >= 0
        errd, apart, ver, plaf, u = (suite.errd[sl], suite.apart[sl], suite.ver[sl], suite.plaf[sl],
                                     suite.u_val[sl])
        niv = TY.ENJEU[np.where(actif, typ, 0)]
        principal = errd & ~apart
        niv_m = [principal & (niv == j) for j in range(3)]
        rates = [u < e for e in self.valeurs_e]
        cle_base = (np.arange(R, dtype=np.int64)[None, :] * NT + np.where(actif, typ, 0)) * 3
        nonplaf = actif & ~plaf
        apres = None
        if self.fenetre and getattr(suite, "jonction", None) is not None:
            apres = np.arange(t0, t0 + Tc)[:, None] >= np.asarray(suite.jonction)[None, :]
        cle_g = None
        if self.grappes is not None:
            ng, G = int(self.grappes["n_groupes"]), int(self.grappes["G"])
            gr = suite.grappe[sl]
            okg = gr >= 0
            cle_g = np.asarray(self.grappes["groupe"], dtype=np.int64)[None, :] * G + np.where(okg, gr, 0)
            taille_g = ng * G

            def par_grappe(masque):
                return np.bincount(cle_g[masque & okg], minlength=taille_g).reshape(ng, G)
        for v in range(V):
            cs = slice(v * R, (v + 1) * R)
            p = P[:, cs]
            p1, p2, p3 = p == 1, p == 2, p == 3
            self.val[cs] += p1.sum(axis=0)
            self.inv3[cs] += (p3 & ~ver & actif).sum(axis=0)
            for ie, rate in enumerate(rates):
                x = p3 & ~rate
                passe = p3 | ((p1 | p2) & rate)
                corr = p2 & errd & ~rate
                for j in range(3):
                    self.exc[ie, cs, j] += (x & niv_m[j]).sum(axis=0)
                    self.dmg[ie, cs, j] += (passe & niv_m[j]).sum(axis=0)
                self.cor[ie, cs] += corr.sum(axis=0)
                self.exc_part[ie, cs] += (x & errd & apart).sum(axis=0)
                if apres is not None:
                    for j in range(3):
                        self.exc_w[ie, cs, j] += (x & niv_m[j] & apres).sum(axis=0)
                        self.dmg_w[ie, cs, j] += (passe & niv_m[j] & apres).sum(axis=0)
                    self.cor_w[ie, cs] += (corr & apres).sum(axis=0)
                if cle_g is not None:
                    for j in range(3):
                        self.exc_g[ie, v, :, j, :] += par_grappe(x & niv_m[j])
                    self.cor_g[ie, v] += par_grappe(corr)
            if cle_g is not None:
                self.val_g[v] += par_grappe(p1)
            m = nonplaf & (p > 0)
            cle = cle_base + (p.astype(np.int64) - 1)
            self.comptes[cs] += np.bincount(cle[m], minlength=R * NT * 3).reshape(R, NT, 3)
            if apres is not None:
                self.val_w[cs] += (p1 & apres).sum(axis=0)
                mw = m & apres
                self.comptes_w[cs] += np.bincount(cle[mw], minlength=R * NT * 3).reshape(R, NT, 3)

    def lignes(self, sl: slice) -> dict:
        """Les agrégats des lignes `sl` (une règle ou un témoin)."""
        out = dict(exc=self.exc[:, sl], dmg=self.dmg[:, sl], cor=self.cor[:, sl], exc_part=self.exc_part[:, sl],
                   val=self.val[sl], inv3=self.inv3[sl], comptes=self.comptes[sl])
        if self.fenetre:
            out.update(exc_w=self.exc_w[:, sl], dmg_w=self.dmg_w[:, sl], cor_w=self.cor_w[:, sl],
                       val_w=self.val_w[sl], comptes_w=self.comptes_w[sl])
        return out


def compter_paliers(P: np.ndarray, suite, valeurs_e=(0.05,), paquet: int = 2000, grappes: Optional[dict] = None
                    ) -> Compteur:
    """Comptabilité de paliers déjà calculés (témoins) : P (T, V × R)."""
    cpt = Compteur(P.shape[1], valeurs_e, grappes, fenetre=getattr(suite, "jonction", None) is not None)
    for t0 in range(0, suite.T, paquet):
        cpt.accumuler(P[t0:t0 + paquet], t0, suite)
    return cpt


# ==========================================================================
# Moteur vectorisé
# ==========================================================================
@dataclass
class ResultatMoteur:
    regles: list
    R: int
    T: int
    cpt: Compteur
    ep_ouvertes: np.ndarray     # (N,) épreuves ouvertes par une erreur à enjeu moyen ou fort
    ep_tentatives: np.ndarray   # (N,) essais (épreuves dues), impossibles compris
    ep_reussies: np.ndarray
    ep_ratees: np.ndarray
    ep_impossibles: np.ndarray
    ep_validations: np.ndarray  # (N,) charge des épreuves : 3 validations par essai joué
    n_prom3: np.ndarray         # (N, NT) promotions au palier 3
    n_retraits3: np.ndarray     # (N, NT) pertes du palier 3
    premier3: np.ndarray        # (N, NT) pas de la première promotion au palier 3 (−1 : jamais)
    volume3: np.ndarray         # (N, NT) écritures du type vues jusqu'à la première promotion (−1 : jamais)
    pal_final: np.ndarray       # (N, NT)
    P: Optional[np.ndarray] = None
    journal: Optional[list] = None   # (ligne, t, type, statut, variantes, cas) de chaque essai d'épreuve
    # Phase 2, après la jonction d'un scénario (None sans jonction) : (N, NT), sauf `suivi` (N,)
    suivi: Optional[np.ndarray] = None          # la jonction a eu lieu sur la ligne
    snap: Optional[np.ndarray] = None           # palier juste avant la jonction
    premier3_apres: Optional[np.ndarray] = None  # premier pas au palier 3 à partir de la jonction (−1 : jamais)
    prom3_apres: Optional[np.ndarray] = None    # promotions au palier 3 après la jonction
    perte3: Optional[np.ndarray] = None         # pas de la perte du palier 3 (types au palier 3 à la jonction)
    delai3: Optional[np.ndarray] = None         # écritures du type de la jonction à cette perte (−1 : jamais)
    err_delai: Optional[np.ndarray] = None      # erreurs avec dégât exécutées au palier 3 pendant ce délai
    n_periodes: Optional[np.ndarray] = None     # périodes d'autonomie (palier 3) après la jonction (E1-a)
    max_constatees: Optional[np.ndarray] = None  # erreurs constatées exécutées dans une même période, au plus
    tot_constatees: Optional[np.ndarray] = None
    tot_ratees: Optional[np.ndarray] = None     # erreurs non vues exécutées au palier 3 après la jonction (5.11)
    tot_inverifiables: Optional[np.ndarray] = None

    def lignes(self, i: int) -> slice:
        return slice(i * self.R, (i + 1) * self.R)

    def issues_ligne(self, ligne: int) -> dict:
        """{(t, type): statut} des épreuves d'une ligne (pour `regles.rejouer_reference`)."""
        return {(t, k): st for (li, t, k, st, _v, _c) in (self.journal or []) if li == ligne}


def simuler(suite, regles: list, fournisseur, valeurs_e=(0.05,), journal: bool = False, garder_P: bool = False,
            paquet: int = 256, jonction=None, annonce: bool = False, retard: int = 0,
            grappes: Optional[dict] = None) -> ResultatMoteur:
    """Fait tourner les règles sur la suite (mêmes tirages pour toutes) ; lignes règle par règle.

    jonction : (R,) premier pas du second segment (défaut : `suite.jonction`) ; annonce : remise à zéro à la jonction
    (mode annoncé) ou non (silencieux) ; retard : constat différé de `retard` écritures du type (0 : immédiat) ;
    grappes : comptes par grappe (bootstrap-t)."""
    T, R = suite.T, suite.R
    V = len(regles)
    N = V * R
    if jonction is None:
        jonction = getattr(suite, "jonction", None)
    suivre = jonction is not None

    def par_type(vals, dtype):
        return np.repeat(np.stack([np.asarray(x, dtype=dtype) for x in vals]), R, axis=0).ravel()

    est_B = [r.famille == "B" for r in regles]
    zeros = np.zeros(NT)
    a2 = par_type([r.params.a2 for r in regles], float)
    b2 = par_type([r.params.b2 for r in regles], float)
    f2 = par_type([r.params.plancher2 for r in regles], float)
    ap2 = par_type([r.params.a_palier2 for r in regles], bool)
    a3 = par_type([zeros if b else r.params.a3 for r, b in zip(regles, est_B)], float)
    b3 = par_type([zeros if b else r.params.b3 for r, b in zip(regles, est_B)], float)
    f3 = par_type([zeros if b else np.broadcast_to(r.params.plancher3, (NT,)) for r, b in zip(regles, est_B)], float)
    lnB = par_type([np.full(NT, r.params.lnB) for r in regles], float)
    famB = par_type([np.full(NT, b) for b in est_B], bool)
    Nn = par_type([r.N if b else np.full(NT, GRAND) for r, b in zip(regles, est_B)], np.int64)
    Nl = par_type([r.N_allonge if b else np.full(NT, GRAND) for r, b in zip(regles, est_B)], np.int64)
    eh = par_type([r.enjeu_haut for r in regles], bool)
    epr = par_type([np.full(NT, r.epreuves) for r in regles], bool)
    attente = C.EPREUVE_ATTENTE

    # état, à plat : indice = ligne × NT + type
    pal = np.ones(N * NT, dtype=np.int8)
    L2 = np.zeros(N * NT)
    L3 = np.zeros(N * NT)
    cc = np.zeros(N * NT, dtype=np.int64)
    allonge = np.zeros(N * NT, dtype=bool)
    s = np.zeros(N * NT, dtype=np.int32)
    Ed = np.zeros(N * NT, dtype=np.int32)
    Ec = np.zeros(N * NT, dtype=np.int32)
    att = np.zeros(N * NT, dtype=np.int32)
    cnt = np.zeros(N * NT, dtype=np.int64)
    files_Ed: dict = {}      # indice -> deque des cas des épreuves ouvertes par une erreur (le plus ancien d'abord)
    files_Ec: dict = {}      # indice -> deque des cas des épreuves converties à la jonction
    cas_memoire: dict = {}   # indice -> cas des erreurs moyennes ou fortes gardées en mémoire (s)
    tentatives: dict = {}    # (indice, cas) -> essais déjà passés sur l'épreuve ouverte de ce cas

    n_prom3 = np.zeros(N * NT, dtype=np.int32)
    n_ret3 = np.zeros(N * NT, dtype=np.int32)
    premier3 = np.full(N * NT, -1, dtype=np.int32)
    volume3 = np.full(N * NT, -1, dtype=np.int64)
    ep_ouv = np.zeros(N, dtype=np.int64)
    ep_tent = np.zeros(N, dtype=np.int64)
    ep_reu = np.zeros(N, dtype=np.int64)
    ep_rat = np.zeros(N, dtype=np.int64)
    ep_imp = np.zeros(N, dtype=np.int64)
    ep_val = np.zeros(N, dtype=np.int64)
    log = [] if journal else None

    if suivre:
        jl = np.tile(np.asarray(jonction, dtype=np.int64), V)
        suivi = np.zeros(N, dtype=bool)
        snap = np.zeros(N * NT, dtype=np.int8)
        cnt_tc = np.zeros(N * NT, dtype=np.int64)
        premier3_ap = np.full(N * NT, -1, dtype=np.int32)
        prom3_ap = np.zeros(N * NT, dtype=np.int32)
        perte3 = np.full(N * NT, -1, dtype=np.int32)
        delai3 = np.full(N * NT, -1, dtype=np.int64)
        err_delai = np.zeros(N * NT, dtype=np.int32)
        n_per = np.zeros(N * NT, dtype=np.int32)
        en_per = np.zeros(N * NT, dtype=bool)
        cst_per = np.zeros(N * NT, dtype=np.int32)
        max_cst = np.zeros(N * NT, dtype=np.int32)
        tot_cst = np.zeros(N * NT, dtype=np.int32)
        tot_rat = np.zeros(N * NT, dtype=np.int32)
        tot_inv = np.zeros(N * NT, dtype=np.int32)
        types_tous = np.arange(NT, dtype=np.int64)
    rate_s = getattr(suite, "rate", None)
    if retard:
        buf_code = np.zeros((N * NT, retard), dtype=np.int8)
        buf_cas = np.zeros((N * NT, retard, 3), dtype=np.int32)

    cpt = Compteur(N, valeurs_e, grappes, fenetre=suivre)
    Pbuf = np.empty((max(1, paquet), N), dtype=np.int8)
    Pall = np.empty((T, N), dtype=np.int8) if garder_P else None
    t0 = 0
    base = np.arange(N, dtype=np.int64) * NT
    colonne_de = np.tile(np.arange(R, dtype=np.int64), V)

    def cible(ii):
        lb = lnB[ii] + C.TOL
        ok2 = ap2[ii] & (L2[ii] <= lb)
        ok3 = np.where(famB[ii], cc[ii] >= np.where(allonge[ii], Nl[ii], Nn[ii]), L3[ii] <= lb)
        return np.where(ok3, 3, np.where(ok2, 2, 1)).astype(np.int8)

    def promus(ii, ancien, nouveau, t):
        """Suivi des promotions au palier 3 ; fin d'une montée allongée (B : les suivantes exigent N)."""
        p3 = (nouveau == 3) & (ancien < 3)
        if not p3.any():
            return
        ip = ii[p3]
        fin = ip[famB[ip] & allonge[ip]]
        allonge[fin] = False
        cc[fin] = np.minimum(cc[fin], Nn[fin])
        n_prom3[ip] += 1
        m = premier3[ip] < 0
        premier3[ip[m]] = t
        volume3[ip[m]] = cnt[ip[m]]
        if suivre:
            ia = ip[suivi[ip // NT]]
            prom3_ap[ia] += 1
            m = premier3_ap[ia] < 0
            premier3_ap[ia[m]] = t

    def pertes(ii, t):
        """Perte du palier 3 après la jonction, pour les types au palier 3 à la jonction (retrait, 5.10)."""
        if not suivre or ii.size == 0:
            return
        m = suivi[ii // NT] & (snap[ii] == 3) & (pal[ii] < 3) & (perte3[ii] < 0)
        i3 = ii[m]
        perte3[i3] = t
        delai3[i3] = cnt[i3] - cnt_tc[i3]

    for t in range(T):
        # ---- 0. jonction d'un scénario, avant l'écriture t (5.10)
        if suivre:
            lj = np.nonzero(jl == t)[0]
            if lj.size:
                ii = (lj[:, None] * NT + types_tous[None, :]).ravel()
                snap[ii] = pal[ii]
                cnt_tc[ii] = cnt[ii]
                suivi[lj] = True
                if annonce:
                    ancien = pal[ii].copy()
                    cc[ii] = 0
                    allonge[ii] = False
                    L2[ii] = 0.0
                    L3[ii] = 0.0
                    hi = ii[eh[ii] & epr[ii]]
                    for i in hi.tolist():
                        for cas in list(files_Ed.get(i, ())) + list(files_Ec.get(i, ())) + list(cas_memoire.get(i, ())):
                            tentatives.pop((i, cas), None)
                        files_Ed[i] = deque()
                        files_Ec[i] = deque(cas_memoire.get(i, []))
                    Ec[hi] = s[hi]
                    Ed[hi] = 0
                    att[hi] = 0
                    lo = ii[~eh[ii]]
                    s[lo] = 0
                    pal[ii] = cible(ii)
                    n_ret3[ii[(ancien == 3) & (pal[ii] < 3)]] += 1
                    pertes(ii, t)
                    if retard:   # retard10 : les preuves en attente de l'ancien modèle ne passent pas la jonction
                        buf_code[ii] = 0   # annoncée (audit du moteur, 09/11)

        k = np.tile(suite.typ[t], V).astype(np.int64)
        actif = k >= 0
        idx = base + np.where(actif, k, 0)
        plaf = np.tile(suite.plaf[t], V)

        # ---- 1. épreuve due à l'arrivée d'une écriture non plafonnée du type (5.9)
        pend = actif & ~plaf & ((Ed[idx] + Ec[idx]) > 0)
        if pend.any():
            lp = np.nonzero(pend)[0]
            ip = idx[lp]
            w = att[ip]
            dec = w > 0
            att[ip[dec]] = w[dec] - 1
            ok_i = []
            for li in lp[~dec].tolist():
                i = int(idx[li])
                kk_ = int(k[li])
                file = files_Ed[i] if Ed[i] > 0 else files_Ec[i]
                cas = file[0]
                n_ess = tentatives.get((i, cas), 0)
                tentatives[(i, cas)] = n_ess + 1
                iss = fournisseur.issue(li, t, int(colonne_de[li]), kk_, cas, n_ess)
                ep_tent[li] += 1
                ep_val[li] += iss.validations
                if log is not None:
                    log.append((li, t, kk_, iss.statut, iss.variantes, cas))
                if iss.statut == EP.REUSSIE:
                    ep_reu[li] += 1
                    ok_i.append(i)
                    file.popleft()
                    tentatives.pop((i, cas), None)   # épreuve fermée : la mémoire reste bornée aux cas ouverts
                    if Ed[i] > 0:
                        Ed[i] -= 1
                    else:
                        Ec[i] -= 1
                        s[i] -= 1
                        if cas_memoire.get(i) and cas in cas_memoire[i]:
                            cas_memoire[i].remove(cas)
                elif iss.statut == EP.RATEE:
                    ep_rat[li] += 1
                    att[i] = attente
                else:
                    ep_imp[li] += 1   # l'épreuve reste ouverte ; le type reste au palier 1 (M7)
            if ok_i:
                ii = np.array(ok_i, dtype=np.int64)
                anc = pal[ii].copy()
                nouv = np.maximum(anc, cible(ii))
                pal[ii] = nouv
                promus(ii, anc, nouv, t)

        # ---- 2. palier d'exécution (forcé à 1 si l'écriture est plafonnée), 3. comptabilité
        palk = np.where(actif, np.where(plaf, 1, pal[idx]), 0).astype(np.int8)
        Pbuf[t - t0] = palk
        if Pall is not None:
            Pall[t] = palk
        if t - t0 + 1 == paquet or t == T - 1:
            cpt.accumuler(Pbuf[:t - t0 + 1], t0, suite)
            t0 = t + 1

        ver, reu, errp = np.tile(suite.ver[t], V), np.tile(suite.reu[t], V), np.tile(suite.errp[t], V)
        if suivre:
            # périodes d'autonomie après la jonction (amendement E1-a) : une période commence à la première écriture du
            # type exécutée au palier 3 et finit à la suivante exécutée plus bas ; on y compte les erreurs constatées
            act_s = actif & suivi
            pk3 = act_s & (palk == 3)
            en = en_per[idx]
            deb = idx[pk3 & ~en]
            n_per[deb] += 1
            cst_per[deb] = 0
            en_per[deb] = True
            en_per[idx[act_s & ~plaf & ~pk3 & en]] = False   # une plafonnée, forcée au palier 1, ne coupe pas (audit 09/11)
            im = idx[pk3 & errp]
            cst_per[im] += 1
            max_cst[im] = np.maximum(max_cst[im], cst_per[im])
            tot_cst[im] += 1
            tot_inv[idx[pk3 & ~ver]] += 1
            if rate_s is not None:
                tot_rat[idx[pk3 & np.tile(rate_s[t], V)]] += 1
            imd = idx[pk3 & np.tile(suite.errd[t], V)]
            imd = imd[(snap[imd] == 3) & (perte3[imd] < 0)]
            err_delai[imd] += 1

        # ---- 4. preuves (Q4 b : réussites plafonnées ignorées, erreurs plafonnées comptées)
        ok = actif & ~plaf & ver & reu
        ko = actif & errp
        cas_p = np.tile(suite.partie[t], V).astype(np.int64)
        cas_r = np.tile(suite.rang[t], V).astype(np.int64)
        cas_o = np.tile(suite.outil[t], V).astype(np.int64)
        ia_l = np.nonzero(actif)[0]
        ia = idx[ia_l]
        if retard:   # constat différé : la preuve arrive `retard` écritures du type plus tard (5.11, logique d'E1)
            pos = cnt[ia] % retard
            code = np.where(ok[ia_l], 1, np.where(ko[ia_l], 2, 0)).astype(np.int8)
            vieux = buf_code[ia, pos].copy()
            vcas = buf_cas[ia, pos].copy()
            buf_code[ia, pos] = code
            buf_cas[ia, pos] = np.stack([cas_p[ia_l], cas_r[ia_l], cas_o[ia_l]], axis=1)
            ok = np.zeros(N, dtype=bool)
            ko = np.zeros(N, dtype=bool)
            ok[ia_l] = vieux == 1
            ko[ia_l] = vieux == 2
            cas_p[ia_l], cas_r[ia_l], cas_o[ia_l] = vcas[:, 0], vcas[:, 1], vcas[:, 2]
        cnt[ia] += 1

        li = np.nonzero(ok)[0]
        if li.size:
            ii = idx[li]
            ii = ii[(Ed[ii] + Ec[ii]) == 0]   # le compteur ne bouge pas tant qu'une épreuve est ouverte
            if ii.size:
                L2[ii] = np.maximum(L2[ii] - b2[ii], f2[ii])
                isB = famB[ii]
                iA, iB = ii[~isB], ii[isB]
                if iA.size:
                    L3[iA] = np.maximum(L3[iA] - b3[iA], f3[iA])
                if iB.size:
                    cc[iB] = np.minimum(cc[iB] + 1, np.where(allonge[iB], Nl[iB], Nn[iB]))
                anc = pal[ii].copy()
                nouv = np.maximum(anc, cible(ii))
                pal[ii] = nouv
                promus(ii, anc, nouv, t)

        li = np.nonzero(ko)[0]
        if li.size:
            ii = idx[li]
            anc = pal[ii].copy()
            s[ii] += 1
            cc[ii] = 0
            haut = eh[ii]
            ih = ii[haut]
            if ih.size:
                pal[ih] = 1
                L3[ih] = np.maximum(L3[ih], 0.0) + a3[ih]
                L2[ih] = np.maximum(L2[ih], 0.0) + a2[ih]
                allonge[ih] = True
                ouvre = ih[epr[ih]]
                Ed[ouvre] += 1
                lh = li[haut]
                for j, i in zip(lh[epr[ih]].tolist(), ouvre.tolist()):
                    cas = EP.Cas(int(cas_p[j]), int(cas_r[j]), int(cas_o[j]))
                    files_Ed.setdefault(i, deque()).append(cas)
                    cas_memoire.setdefault(i, []).append(cas)
                np.add.at(ep_ouv, lh[epr[ih]], 1)
            ib = ii[~haut]
            if ib.size:
                L3[ib] += a3[ib]
                L2[ib] += a2[ib]
                c_ = cible(ib)
                cur = pal[ib]
                inferieur = np.maximum(np.where(ap2[ib], cur - 1, 1), 1).astype(np.int8)
                pal[ib] = np.where(c_ < cur, np.maximum(c_, inferieur), cur)
            n_ret3[ii[(anc == 3) & (pal[ii] < 3)]] += 1
            pertes(ii, t)

    rs = lambda x: x.reshape(N, NT)  # noqa: E731
    res = ResultatMoteur(regles=list(regles), R=R, T=T, cpt=cpt, ep_ouvertes=ep_ouv, ep_tentatives=ep_tent,
                         ep_reussies=ep_reu, ep_ratees=ep_rat, ep_impossibles=ep_imp, ep_validations=ep_val,
                         n_prom3=rs(n_prom3), n_retraits3=rs(n_ret3), premier3=rs(premier3), volume3=rs(volume3),
                         pal_final=rs(pal), P=Pall, journal=log)
    if suivre:
        res.suivi = suivi
        res.snap, res.premier3_apres, res.prom3_apres = rs(snap), rs(premier3_ap), rs(prom3_ap)
        res.perte3, res.delai3, res.err_delai = rs(perte3), rs(delai3), rs(err_delai)
        res.n_periodes, res.max_constatees, res.tot_constatees = rs(n_per), rs(max_cst), rs(tot_cst)
        res.tot_ratees, res.tot_inverifiables = rs(tot_rat), rs(tot_inv)
    return res
