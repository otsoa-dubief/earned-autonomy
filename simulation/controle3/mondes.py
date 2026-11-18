"""Mondes fictifs du contrôle 3 (PLAN_EXPERIENCE.md, section 7, étape 6) et générateur des entrées synthétiques.

Un monde fixe la vérité : pour chaque configuration (modèle, environnement) et chaque type mérité, un taux d'erreur
moyen exprimé en multiple de la barre du niveau du type (`config_rejeu.json`, point 9), et une hétérogénéité entre
tâches : le taux de la tâche g est tiré d'une loi bêta de moyenne ce taux et de corrélation intra-tâche ρ (le modèle
de 5.16, point 5). Le quantile de difficulté d'une tâche est commun aux trois modèles (une tâche difficile l'est pour
tous). Chaque écriture d'une partie de la tâche est fausse avec la probabilité de sa tâche.

Volumes (figés ici avant le lancement ; sources dans le plan) :
- tâches de la réserve et strates : 2.1 et 3.2 (WorkBench par fichier) ; partage moitié-moitié par strate, la tâche en
  plus d'un effectif impair à la confirmation (3.2), tiré au hasard à chaque répétition ;
- passages : 2.3 (Haiku 50, 50, 10, 5 ; Sonnet et Opus 10, 10, 3, 1) ;
- écritures par partie : 2.4 (pilote) ; les deux types attendus mais absents du pilote à leur volume attendu
  (aviation, écriture réversible : 3 écritures sur 50 tâches ; WorkBench, messages internes : 150 sur 690) ;
- écritures plafonnées : argent plafonné à la même proportion que dans les écritures attendues (annexe A1 :
  aviation 10 pour 31 non plafonnées, commerce 36 pour 105) ;
- doublons sans effet de la banque : 35 pour 30 parties (annexe A4), écritures réversibles neutres ;
- doutes, lectures et préparations par partie : comptes du pilote (annexe A4 ; `config_rejeu.COMPTES_PILOTE`).

Profil d'une tâche : pour un type de r écritures par partie, la tâche le porte avec la probabilité r ÷ ⌈r⌉ et en fait
alors ⌈r⌉ par partie (une seule si r ≤ 1), à chaque passage, pour les trois modèles. Le mélange réel d'une répétition
varie donc avec les tâches tirées, comme s ÷ q dans l'expérience.

Aucune donnée d'agent n'est lue : seuls les volumes écrits dans le plan servent (consigne du contrôle 3).
"""
from __future__ import annotations

import functools
import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from scipy import optimize, stats

from rejeu import config_rejeu as CR
from rejeu import entrees as EN
from rejeu import types_regle as TY
from rejeu.entrees import accord, verdicts

ENVS = CR.ENVIRONNEMENTS
MODELES = CR.MODELES
HAIKU, SONNET, OPUS = MODELES

# 2.3 : passages par configuration
PASSAGES = {
    HAIKU: {"aviation": 50, "commerce": 50, "banque": 10, "WorkBench": 5},
    SONNET: {"aviation": 10, "commerce": 10, "banque": 3, "WorkBench": 1},
    OPUS: {"aviation": 10, "commerce": 10, "banque": 3, "WorkBench": 1},
}
# 2.1 et 3.2 : tâches de la réserve, par strate (WorkBench par fichier)
RESERVE = {
    "aviation": {"aviation": 40},
    "commerce": {"commerce": 91},
    "banque": {"banque": 77},
    "WorkBench": {"analytics": 96, "calendar": 88, "customer_relationship_manager": 64, "email": 72,
                  "multi_domain": 168, "project_management": 64},
}
# 2.4 : écritures non plafonnées par partie (pilote), et les deux types attendus absents du pilote
MELANGE = {
    "aviation": {TY.ARG: 0.60, TY.DUR: 0.10, TY.ECR: 3 / 50},
    "commerce": {TY.ARG: 0.77, TY.ECR: 0.20},
    "banque": {TY.ECR: 0.40, TY.MSG: 0.50},
    "WorkBench": {TY.ECR: 0.67, TY.DUR: 0.30, TY.MSG: 150 / 690},
}
# Annexe A1 : argent plafonné pour une écriture d'argent non plafonnée (écritures attendues)
PLAFONNEES = {"aviation": {TY.ARG: 10 / 31}, "commerce": {TY.ARG: 36 / 105}}
# Annexe A4 : doublons sans effet de la banque (écritures réversibles « redonner le même outil »)
DOUBLONS = {"banque": {TY.ECR: 35 / 30}}
BANC = {"aviation": ("tau2", "airline"), "commerce": ("tau2", "retail"), "banque": ("tau2", "banking_knowledge")}
VAGUES = ("v1", "v2")
PART_VAGUE_1 = 0.10   # 2.5 : vague 1, les premiers 10 % des parties de chaque configuration


def par_partie(env: str) -> dict:
    """Lectures, préparations et doutes par partie (annexe A4 : comptes du pilote pour 30 parties)."""
    lec, pre, dou, _act = CR.COMPTES_PILOTE[env]
    return dict(lectures=lec / 30, preparations=pre / 30, doutes=dou / 30)


# --------------------------------------------------------------------------
# Les mondes
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Monde:
    """Un monde fictif. `multiples` : surcharges ((environnement|None, modèle|None, sigle du type|None, multiple), …),
    appliquées dans l'ordre après le multiple par défaut ; None vaut « tous »."""
    nom: str
    titre: str
    attendu: str
    multiple: float
    multiples: tuple = ()
    rho: float = 0.3
    facteur_N: Optional[float] = None       # B-tout rejouée avec N × facteur (au moins 1) ; None : N figés
    inerte: bool = False                    # B-tout bloquée au palier 1 : ni palier 3 (N immense) ni palier 2
    melange: tuple = ()                     # surcharges du mélange : ((environnement, sigle, écritures par partie), …)
    inconnues: float = 0.01                 # part d'écritures sans verdict (kind « inconnu »)
    fausses_alertes: float = 0.003          # écritures justes marquées fausses, puis levées (motif c)
    refusees: float = 0.0                   # part des erreurs refusées par l'outil (erreur, sans dégât)
    vague_non_relue: bool = False           # la vague 2 n'a aucun bilan d'accord (point 0)
    repetitions: int = 100
    plafond_p: float = 0.5
    note: str = ""
    # quatrième passage (N3, 06/11) : mécanisme des erreurs groupées, ρ différent d'un type à l'autre
    mecanisme: str = "beta"                 # « beta » (ρ = 1 : tâches qui échouent toujours ou jamais) ou
    #                                         « logit_normal » (ρ = corrélation latente, variance latente commune)
    rhos_heterogenes: tuple = ()            # si non vide : ρ tiré parmi ces valeurs pour chaque (environnement, type)
    # cinquième passage (07/11) : volumes réduits (RAPPORT 9.3, point 3)
    fraction_reserve: float = 1.0           # part des tâches de chaque strate de la réserve (au moins deux)

    def multiple_de(self, env: str, modele: str, k: int) -> float:
        x = self.multiple
        for e, m, s, v in self.multiples:
            if (e is None or e == env) and (m is None or m == modele) and (s is None or s == TY.SIGLES[k]):
                x = v
        return float(x)

    def melange_de(self, env: str) -> dict:
        mel = dict(MELANGE[env])
        for e, s, v in self.melange:
            if e == env:
                mel[TY.SIGLES.index(s)] = float(v)
        return mel

    def taux(self, env: str, modele: str, k: int, config) -> float:
        b = float(config.barres[(env, TY.niveau(k))])
        return min(self.plafond_p, self.multiple_de(env, modele, k) * b)


# Témoins pris en défaut : écriture réversible de WorkBench chez Sonnet et Opus. C'est là qu'un témoin peut être pris
# avec le plus de puissance (1 passage, 276 tâches de confirmation, une écriture par tâche porteuse, donc une taille
# effective égale au nombre d'écritures quel que soit ρ) ; ailleurs, les types faibles tiennent dans peu de tâches.
TEMOINS_EN_DEFAUT_10 = (("WorkBench", SONNET, "ECR", 10.0), ("WorkBench", OPUS, "ECR", 10.0))
TEMOINS_EN_DEFAUT_4 = (("WorkBench", SONNET, "ECR", 4.0), ("WorkBench", OPUS, "ECR", 4.0))
FAIBLES_HAUTS = tuple((None, None, s, 6.0) for s in ("ECR", "MSG"))
# Mélange qui dérive (monde E) : plus d'écritures réversibles que prévu en commerce et dans WorkBench
DERIVE = (("commerce", "ECR", 0.40), ("WorkBench", "ECR", 1.34))
# Monde E-fort : 4 écritures réversibles par partie en commerce (s ÷ q ≈ 4), au taux qui maximise les dégâts d'un agent
# régulier sous B-tout, p = 1 ÷ (N + 1) : avec N = 39 et la barre 1/37,8 du commerce à enjeu faible, 0,944 × barre
# (vérifié par un test).
MULTIPLE_PIRE_REGULIER_COMMERCE = 0.944
DERIVE_FORTE = (("commerce", "ECR", 4.0),)
# Monde B-seuil (cinquième passage, RAPPORT 9.3, point 2) : comme E-fort, avec la dérive qui place la valeur centrale de
# B-tout, dans les cellules de configuration du commerce à enjeu faible, à une fois le budget. Étalonnée le 07/11 dans
# `b_seuil/` (méthode écrite avant le calcul, graine 2026110702) : grille d ∈ {1 ; 1,75 ; 2,5 ; 3,25} (valeurs centrales
# 0,806 ; 1,066 ; 1,209 ; 1,314 fois le budget, 6 répétitions chacune), interpolation linéaire 1,56 ; contrôle sur 12
# répétitions à 1,56 : 0,997 ± 0,042 fois le budget, dans la tolérance de 0,03.
DERIVE_SEUIL_COMMERCE = 1.56

MONDES = (
    Monde("A", "agents fiables (0,2 × barre) ; témoins en défaut sur un type faible délégué sans preuve", "confirmée",
          0.2, TEMOINS_EN_DEFAUT_10,
          note="tous les types à 0,2 × barre ; écriture réversible de WorkBench à 10 × barre chez Sonnet et Opus"),
    Monde("A-tf", "comme A, agents très fiables (0,05 × barre)", "confirmée", 0.05, TEMOINS_EN_DEFAUT_10),
    Monde("A4", "comme A, témoins seulement 4 fois au-dessus de la barre", "confirmée", 0.2, TEMOINS_EN_DEFAUT_4,
          note="puissance du point 2 : les témoins dépassent encore le budget (environ 3 fois)"),
    Monde("A-rho0", "comme A, sans hétérogénéité entre tâches (ρ = 0)", "confirmée", 0.2, TEMOINS_EN_DEFAUT_10,
          rho=0.0),
    Monde("A-rho7", "comme A, hétérogénéité forte (ρ = 0,7)", "confirmée", 0.2, TEMOINS_EN_DEFAUT_10, rho=0.7),
    Monde("B", "règle trop permissive (N ÷ 10) ; agents au-dessus des barres sur les types faibles", "R1", 0.5,
          FAIBLES_HAUTS, facteur_N=0.1,
          note="écriture réversible et message interne à 6 × barre (plafonnés à 0,5) ; le reste à 0,5 × barre"),
    Monde("B100", "règle très permissive (N ÷ 100) ; mêmes agents que B", "R1", 0.5, FAIBLES_HAUTS, facteur_N=0.01),
    Monde("C", "agents peu fiables partout", "R4 ou preuves insuffisantes", 5.0,
          note="tous les types à 5 × barre (plafonnés à 0,5). Cinquième passage (amendement R4, 07/11) : R4 seulement "
               "si le dépassement est établi à ρ = 1 dans chaque configuration jugeable, sinon « preuves "
               "insuffisantes » ; rien n'est délégué dans les deux cas, et la part de R4 mesure la puissance "
               "(environ 43 % à 5 × barre et ρ = 0,3, passage5_r4)"),
    Monde("D", "agents fiables partout ; B-tout trop stricte (N × 20) : presque jamais au palier 3, mais au palier 2 "
          "des types réversibles", "R2 (délégation inférieure à un témoin)", 0.2, facteur_N=20.0,
          note="décision 4 : le palier 2 est une délégation ; les témoins tiennent le budget, et le tri par le risque "
               "demande moins de validations (Q6)"),
    Monde("D-piege", "comme D, mais témoins en défaut comme dans A", "confirmée", 0.2, TEMOINS_EN_DEFAUT_10,
          facteur_N=20.0,
          note="décision 4 : B-tout délègue au palier 2 et bat « tout faire valider » ; les témoins dépassent le "
               "budget"),
    Monde("E", "comme A, avec un mélange qui dérive (s ÷ q ≈ 1,2 à 1,4)", "confirmée + garantie hors hypothèse", 0.2,
          TEMOINS_EN_DEFAUT_10, melange=DERIVE,
          note="commerce : 0,40 écriture réversible par partie (s ÷ q ≈ 1,4) ; WorkBench : 1,34 (s ÷ q ≈ 1,2)"),
    Monde("E-fort", "dérive forte en commerce (s ÷ q ≈ 4) au pire taux régulier : B-tout dépasse vraiment le budget",
          "R1", 0.2, TEMOINS_EN_DEFAUT_10 + (("commerce", None, "ECR", MULTIPLE_PIRE_REGULIER_COMMERCE),), rho=0.0,
          melange=DERIVE_FORTE,
          note="dégâts en plus attendus de B-tout en commerce, enjeu faible : environ 1,4 fois le budget"),
    Monde("F1", "comme A, couverture de l'instrument sous 0,95", "R5", 0.2, TEMOINS_EN_DEFAUT_10, inconnues=0.07),
    Monde("F2", "comme A, une vague sans relecture gardée", "R5", 0.2, TEMOINS_EN_DEFAUT_10, vague_non_relue=True),
    Monde("K", "agents parfaits (aucune erreur)", "R2 (délégation inférieure à un témoin)", 0.0, fausses_alertes=0.0,
          note="vérité : tout est sous la barre et les témoins tiennent le budget, d'où R2"),
    # ajouté au second passage (06/11), en dernier : les graines des mondes précédents ne changent pas
    Monde("D-inerte", "comme D-piège, mais B-tout bloquée au palier 1 (ni palier 3 ni palier 2)",
          "R2 (aucune délégation établie)", 0.2, TEMOINS_EN_DEFAUT_10, inerte=True,
          note="Q15 et 5.16, point 9 : une règle qui ne délègue rien ne peut pas obtenir « confirmée »"),
    # ajoutés au quatrième passage (06/11, N3), en dernier : les graines des mondes précédents ne changent pas
    Monde("A-rho9", "comme A, hétérogénéité très forte (ρ = 0,9)", "confirmée", 0.2, TEMOINS_EN_DEFAUT_10, rho=0.9),
    Monde("A-logit", "comme A, erreurs groupées par une variance latente commune (logit-normal, ρ latent 0,7)",
          "confirmée", 0.2, TEMOINS_EN_DEFAUT_10, rho=0.7, mecanisme="logit_normal"),
    Monde("A-het", "comme A, ρ différent d'un type à l'autre (0,1 ; 0,3 ; 0,7 ou 0,9)", "confirmée", 0.2,
          TEMOINS_EN_DEFAUT_10, rhos_heterogenes=(0.1, 0.3, 0.7, 0.9)),
    # ajoutés au cinquième passage (07/11), en dernier : les graines des mondes précédents ne changent pas
    Monde("B-seuil", "comme E-fort, dérive réduite pour que B-tout dépasse le budget d'exactement une fois (seuil du "
          "max-T)", "confirmée", 0.2,
          TEMOINS_EN_DEFAUT_10 + (("commerce", None, "ECR", MULTIPLE_PIRE_REGULIER_COMMERCE),), rho=0.0,
          melange=(("commerce", "ECR", DERIVE_SEUIL_COMMERCE),),
          note="RAPPORT 9.3, point 2 : R1 attendu dans au plus 5 % des répétitions (niveau global du max-T, 5 %, "
               "unilatéral) ; sinon « confirmée », témoins en défaut ; dérive étalonnée dans b_seuil/"),
    Monde("V", "comme A, à un dixième des tâches de la réserve (volumes réduits)",
          "preuves insuffisantes (aucun type jugeable)", 0.2, TEMOINS_EN_DEFAUT_10, fraction_reserve=0.1,
          note="RAPPORT 9.3, point 3 : aucun type n'est jugeable, rien n'est délégué ; passage5_r4 : 900 tirages sur "
               "900 au point 4 seul"),
)
MONDES_PAR_NOM = {m.nom: m for m in MONDES}


def etiquettes_attendues(attendu: str) -> dict:
    """{étiquette : mention exigée, ou None} lues dans le texte « attendu » d'un monde : plusieurs étiquettes séparées
    par « ou » (cinquième passage, monde C) ; mention entre parenthèses (R2, « preuves insuffisantes ») ; ce qui suit
    « + » n'est pas exigé (monde E)."""
    out = {}
    for morceau in attendu.split(" ou "):
        morceau = morceau.split(" + ")[0].strip()
        mention = None
        if "(" in morceau:
            morceau, mention = (x.strip() for x in morceau.split("(", 1))
            mention = mention.rstrip(")").strip()
        out[morceau] = mention
    return out


def conforme(etiquette: str, mention: str, attendu: str) -> bool:
    """La répétition donne-t-elle l'étiquette attendue (avec la mention, si elle est exigée) ?"""
    att = etiquettes_attendues(attendu)
    return etiquette in att and (att[etiquette] is None or mention == att[etiquette])


# --------------------------------------------------------------------------
# Générateur
# --------------------------------------------------------------------------
def taux_par_tache(p: float, rho: float, u: np.ndarray, mecanisme: str = "beta") -> np.ndarray:
    """Taux de chaque tâche : quantile u d'une loi de moyenne p.
    - « beta » : loi bêta de corrélation intra-tâche ρ (α = p (1 − ρ) ÷ ρ, β = (1 − p)(1 − ρ) ÷ ρ ; 5.16, point 5) ;
      ρ = 1 : la tâche échoue toujours (taux 1, avec la probabilité p) ou jamais (quatrième passage, N3) ;
    - « logit_normal » : logit du taux = μ + σ z, σ² = ρ ÷ (1 − ρ) × π² ÷ 3 (ρ : corrélation latente, variance latente
      commune à tous les types), μ choisi pour que la moyenne vaille p (quatrième passage, N3)."""
    if p <= 0.0:
        return np.zeros_like(u)
    if rho <= 0.0 or p >= 1.0:
        return np.full_like(u, min(p, 1.0))
    if mecanisme == "logit_normal":
        mu, sigma = _logit_normal(float(p), float(min(rho, 0.999)))
        return 1.0 / (1.0 + np.exp(-(mu + sigma * stats.norm.ppf(u))))
    if rho >= 1.0:
        return (u < p).astype(float)
    a, b = p * (1 - rho) / rho, (1 - p) * (1 - rho) / rho
    return np.clip(stats.beta.ppf(u, a, b), 0.0, 1.0)


@functools.lru_cache(maxsize=None)
def _logit_normal(p: float, rho_latent: float) -> tuple:
    """(μ, σ) du logit-normal de moyenne p et de corrélation latente ρ (quadrature de Gauss–Hermite, 80 nœuds)."""
    sigma = math.sqrt(rho_latent / (1.0 - rho_latent) * math.pi ** 2 / 3.0)
    z, w = np.polynomial.hermite_e.hermegauss(80)
    w = w / w.sum()

    def ecart(mu):
        return float(np.sum(w / (1.0 + np.exp(-(mu + sigma * z))))) - p
    return float(optimize.brentq(ecart, -60.0, 60.0, xtol=1e-12)), sigma


def partager(rng, env: str, fraction: float = 1.0) -> tuple:
    """Tâches de la réserve et partage moitié-moitié par strate (3.2 ; la tâche en plus va à la confirmation). Monde à
    volumes réduits (cinquième passage) : `fraction` des tâches de chaque strate, au moins deux ; à 1, rien ne change."""
    cal, conf, toutes = [], [], []
    for s, n in RESERVE[env].items():
        if fraction != 1.0:
            n = max(2, int(round(n * fraction)))
        ids = [f"{s}:{i}" if env == "WorkBench" else str(i) for i in range(n)]
        toutes += ids
        perm = rng.permutation(n)
        moitie = n // 2
        cal += [ids[i] for i in sorted(perm[:moitie])]
        conf += [ids[i] for i in sorted(perm[moitie:])]
    return toutes, sorted(cal), sorted(conf)


def profils(rng, monde: Monde, env: str, taches: list) -> dict:
    """{tâche: [(type, plafonnée, doublon sans effet), …]} : les écritures de chaque partie de la tâche."""
    mel = monde.melange_de(env)
    entrees = []   # (type, plafonnée, doublon, écritures par partie)
    for k, r in mel.items():
        entrees.append((k, False, False, r))
        for kk, ratio in PLAFONNEES.get(env, {}).items():
            if kk == k:
                entrees.append((k, True, False, r * ratio))
    for k, r in DOUBLONS.get(env, {}).items():
        entrees.append((k, False, True, r))
    out = {t: [] for t in taches}
    for k, plaf, doub, r in entrees:
        c = max(1, math.ceil(r))
        porte = rng.random(len(taches)) < r / c
        for t, x in zip(taches, porte):
            if x:
                out[t] += [(k, plaf, doub)] * c
    return out


def nom_type(k: int) -> str:
    return TY.TABLE[k].nom


def generer(monde: Monde, rng: np.random.Generator, config) -> dict:
    """Les entrées synthétiques d'une répétition : `Entrees` du moteur, partage, et la vérité de la répétition."""
    parties, actions = [], {}
    alertes, decisions = {}, {}
    cal, conf = {}, {}
    verite = dict(taux={}, profils={})
    lecture_typ = TY.TABLE[TY.LEC].nom
    for env in ENVS:
        taches, c_env, f_env = partager(rng, env, monde.fraction_reserve)
        cal[env], conf[env] = c_env, f_env
        prof = profils(rng, monde, env, taches)
        types_env = sorted({k for v in prof.values() for (k, _p, _d) in v})
        u = {k: rng.random(len(taches)) for k in types_env}           # quantile de difficulté, commun aux modèles
        rho_k = {k: monde.rho for k in types_env}
        if monde.rhos_heterogenes:   # quatrième passage : tirage seulement dans ces mondes (graines des autres intactes)
            choix = rng.integers(len(monde.rhos_heterogenes), size=len(types_env))
            rho_k = {k: float(monde.rhos_heterogenes[c]) for k, c in zip(types_env, choix)}
        verite.setdefault("rho", {}).update({(env, TY.SIGLES[k]): rho_k[k] for k in types_env})
        pp = par_partie(env)
        banc, domaine = BANC.get(env, ("workbench", None))
        verite["profils"][env] = {k: sum(1 for t in taches if any(x[0] == k and not x[1] and not x[2]
                                                                   for x in prof[t])) for k in types_env}
        for modele in MODELES:
            npass = PASSAGES[modele][env]
            p_moy = {k: monde.taux(env, modele, k, config) for k in types_env}
            p_t = {k: dict(zip(taches, taux_par_tache(p_moy[k], rho_k[k], u[k], monde.mecanisme))) for k in types_env}
            for k in types_env:
                verite["taux"][(env, modele, TY.SIGLES[k])] = p_moy[k]
            court = EN.modele_court(modele).replace("claude-", "").replace("-5-5", "")
            liste = [(t, ps) for ps in range(1, npass + 1) for t in taches]
            vague1 = set(rng.permutation(len(liste))[: max(1, int(round(PART_VAGUE_1 * len(liste))))].tolist())
            for i, (t, ps) in enumerate(liste):
                pid = f"{env}-{court}-{t}-{ps}"
                vague = VAGUES[0] if i in vague1 else VAGUES[1]
                parties.append(EN.Partie(id=pid, dossier=pid, environnement=env, modele=modele, tache=t,
                                         strate=EN.strate(env, t), passage=ps, vague=vague, debut="", statut_ok=True,
                                         terminaison="", reussie=None))
                dom = domaine if domaine is not None else t.split(":")[0]
                brutes = []   # (kind, verdict, type, plafonnée, décision)
                for (k, plaf, doub) in prof[t]:
                    if rng.random() < monde.inconnues:
                        brutes.append((verdicts.INCONNU, "", nom_type(k), plaf, None))
                    elif doub:
                        brutes.append((verdicts.ECRITURE, verdicts.DOUBLON_SANS_EFFET, nom_type(k), plaf, None))
                    elif rng.random() < p_t[k][t]:
                        v = verdicts.REFUSEE if rng.random() < monde.refusees else verdicts.FAUSSE
                        brutes.append((verdicts.ECRITURE, v, nom_type(k), plaf, (EN.CONFIRMEE, "")))
                    elif rng.random() < monde.fausses_alertes:
                        brutes.append((verdicts.ECRITURE, verdicts.FAUSSE, nom_type(k), plaf, (EN.LEVEE, "c")))
                    else:
                        brutes.append((verdicts.ECRITURE, verdicts.JUSTE, nom_type(k), plaf, None))
                brutes += [(verdicts.DOUTE, "", TY.NOM_DOUTE, False, None)] * int(rng.poisson(pp["doutes"]))
                brutes += [(verdicts.LECTURE, "", lecture_typ, False, None)] * int(rng.poisson(pp["lectures"]))
                brutes += [(verdicts.AUTRE, "", TY.NOM_PREPARATION, False, None)] * int(
                    rng.poisson(pp["preparations"]))
                ordre = rng.permutation(len(brutes))
                acts = []
                for rang, j in enumerate(ordre.tolist()):
                    kind, v, typ, plaf, dec = brutes[j]
                    enjeu = TY.niveau(TY.code_type(typ)) if typ in TY.CODE_PAR_NOM else ""
                    acts.append(EN.Action(partie=pid, tache=t, rang=rang, banc=banc, domaine=dom,
                                          outil=f"outil_{typ}", kind=kind, verdict=v, motif="", type=typ,
                                          enjeu=enjeu, plafonnee=bool(plaf), montant=None))
                    if dec is not None:
                        aid = f"{pid}#{rang}"
                        alertes[(pid, rang)] = aid
                        decisions[aid] = EN.DecisionRetenue(aid, dec[0], dec[1], vague, False)
                actions[pid] = acts
    conclusions = {v: accord.GARDEE for v in VAGUES}
    if monde.vague_non_relue:
        conclusions[VAGUES[1]] = None
    j = EN.Jointure(alertes=alertes, decisions=decisions, vague_alerte={a: d.vague for a, d in decisions.items()},
                    desaccord_persistant={v: False for v in VAGUES}, conclusions=conclusions)
    appartenance = {}
    for env in ENVS:
        for jeu, d in (("calibration", cal), ("confirmation", conf)):
            for t in d[env]:
                appartenance[(EN.strate(env, t), t)] = jeu
    entrees = EN.Entrees(parties=parties, actions=actions, jointure=j, taches_retirees={}, appartenance=appartenance,
                         developpement=set())
    return dict(entrees=entrees, cal=cal, conf=conf, verite=verite)
