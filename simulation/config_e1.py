"""Paramètres de l'exploration E1 (PLAN_EXPLORATION_E1.md, révision 1).

Le chemin v2 (config.py, regle.py, executer.py…) n'est pas touché : tout ce qui est propre à E1
vit dans les modules *_e1.py. Les interrupteurs d'E1 (lectures sans effet, épreuves à blanc) sont
des paramètres du moteur E1, pas des réglages globaux.

Barres et longueurs N : calculées en fractions exactes (plan, section 2 ; REGLE.md, note datée de
la décision 2), et épinglées dans tests/test_e1.py.
"""
import dataclasses
import math
from fractions import Fraction

import numpy as np

import config as C

# --------------------------------------------------------------------------
# Section 1.2 et 1.3 : budget d'erreurs et barres
# --------------------------------------------------------------------------
# Budget d'Otsoa (fixé à l'aveugle le 04/11 à 15 h 42), en erreurs en plus pour 100 actions du flux.
BUDGET = {"faible": Fraction("0.5"), "moyen": Fraction("0.05"), "fort": Fraction("0.005")}
UN_MOINS_E = Fraction(95, 100)  # le validateur arrête 95 % des erreurs (e = 5 %)
D_CONSTAT = Fraction(95, 100)   # d : part des erreurs constatées (5 % d'actions invérifiables)
E_VALIDATEUR = 0.05             # plan, section 1.7

# Types de chaque niveau qui peuvent agir seuls (LEC et parts plafonnées exclues).
TYPES_NIVEAU = {"faible": (C.ECR, C.MSG), "moyen": (C.DUR, C.EXE), "fort": (C.SOR, C.ARG)}
PART_PLAFONNEE = {C.SOR: Fraction(str(C.PART_PLAFONNEE_SOR)), C.ARG: Fraction(str(C.PART_PLAFONNEE_ARG))}


def part_type(melange: str, k: int) -> Fraction:
    """Part du flux occupée par le type k quand il peut agir seul (fraction plafonnée exclue)."""
    p = Fraction(str(C.MELANGES_BRUTS[melange][C.TYPES[k]]))
    return p * (1 - PART_PLAFONNEE.get(k, Fraction(0)))


def part_niveau(melange: str, niveau: str) -> Fraction:
    return sum((part_type(melange, k) for k in TYPES_NIVEAU[niveau]), Fraction(0))


def barre(melange: str, niveau: str) -> Fraction:
    """barre = budget ÷ (0,95 × 100 × part)."""
    return BUDGET[niveau] / (UN_MOINS_E * 100 * part_niveau(melange, niveau))


def n_b_tout(melange: str, niveau: str) -> int:
    """B-tout : N = 1 ÷ (d × barre) − 1, en fractions exactes (arrondi par excès si non entier)."""
    x = 1 / (D_CONSTAT * barre(melange, niveau))
    return math.ceil(x) - 1


def n_b_regulier(melange: str, niveau: str) -> int:
    """B-régulier : plus petit N tel que N^N ÷ (N + 1)^(N + 1) ≤ d × barre (entiers exacts)."""
    cible = D_CONSTAT * barre(melange, niveau)
    num, den = cible.numerator, cible.denominator

    def ok(n):  # n^n / (n+1)^(n+1) <= num/den
        return n ** n * den <= (n + 1) ** (n + 1) * num

    lo, hi = 1, 1
    while not ok(hi):
        hi *= 2
    while lo < hi:  # la suite n^n/(n+1)^(n+1) décroît
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def n_allonge(n: int) -> int:
    """Pièce 7.3 transposée : ⌈1,25 × N⌉ (entiers exacts)."""
    return -((-5 * n) // 4)


MELANGES = list(C.MELANGES_BRUTS)
NIVEAUX = C.NIVEAUX
BARRES = {(m, n): barre(m, n) for m in MELANGES for n in NIVEAUX}
N_B_REGULIER = {(m, n): n_b_regulier(m, n) for m in MELANGES for n in NIVEAUX}
N_B_TOUT = {(m, n): n_b_tout(m, n) for m in MELANGES for n in NIVEAUX}

# Mesure 11 : réussites sans erreur pour certifier q < barre (règle de trois, risque 5 %) :
# plus petit n tel que (1 − barre)^n ≤ 0,05.
def certification(melange: str, niveau: str, risque: float = 0.05) -> int:
    b = float(barre(melange, niveau))
    return math.ceil(math.log(risque) / math.log1p(-b))


# --------------------------------------------------------------------------
# Section 1.6 : horizons et répétitions
# --------------------------------------------------------------------------
HORIZONS = {
    "court": dict(T=3000, R=5000, bloc=5000),
    "long": dict(T=150_000, R=1000, bloc=200),
}
FACTEUR_RELANCE = 4  # « indécis » : on relance la cellule avec 4 fois plus de répétitions

# --------------------------------------------------------------------------
# Section 1.5 : agents
# --------------------------------------------------------------------------
TAUX_A0 = 1e-4
TAUX_A0D_APRES = 1 / 200
VALEURS_BORD = ("pireBreg", "1.5barre", "3barre")


def q_bord(melange: str, niveau: str, valeur: str) -> float:
    if valeur == "pireBreg":
        return 1.0 / (N_B_REGULIER[(melange, niveau)] + 1)
    f = {"1.5barre": Fraction(3, 2), "3barre": Fraction(3)}[valeur]
    return float(f * BARRES[(melange, niveau)])


def _q_niveau(niveau: str, val: float) -> tuple:
    q = C.vecteur_q(TAUX_A0)
    for k in TYPES_NIVEAU[niveau]:
        q[k] = val
    return C._t(q)


def agents_bord(melange: str) -> list:
    """Agents « bord » (constants) puis leurs variantes qui dérivent en silence au milieu de
    l'horizon (« agents bord qui changent », mesure 5 ; amendement E1-a : ils comptent dans le choix)."""
    out = []
    for niveau in NIVEAUX:
        for val in VALEURS_BORD:
            q = q_bord(melange, niveau, val)
            out.append(C.Agent(f"bord_{niveau}_{val}", f"bord {niveau}, q = {q:.3g} sur ce niveau, "
                               f"A0 ailleurs", _q_niveau(niveau, q)))
    for niveau in NIVEAUX:
        for val in VALEURS_BORD:
            q = q_bord(melange, niveau, val)
            out.append(C.Agent(f"bordD_{niveau}_{val}", f"A0 puis dérive silencieuse au milieu de "
                               f"l'horizon vers q = {q:.3g} sur le niveau {niveau}",
                               C._t(C.vecteur_q(TAUX_A0)), _q_niveau(niveau, q), C.T_CHANGEMENT, None))
    return out


NOTE_AGENTS_BORD_DERIVE = (
    "Agents bord qui changent (mesure 5) : chaque agent bord a une variante qui part du taux d'A0 et dérive en "
    "silence vers la valeur bord au milieu de l'horizon (bordD_*). Ajoutés en phase 1 ; leur place est tranchée par "
    "l'amendement E1-a (décision d'Otsoa) : ils comptent dans le choix, et leur dérive se juge selon la décision 5.")

A0 = C.Agent("A0", "excellent (1 sur 10 000 partout)", C._t(C.vecteur_q(TAUX_A0)))
A0D = C.Agent("A0d", "A0 puis dérive silencieuse vers 1 sur 200 au milieu de l'horizon",
              C._t(C.vecteur_q(TAUX_A0)), C._t(C.vecteur_q(TAUX_A0D_APRES)), C.T_CHANGEMENT, None)

# Identifiants des graines : les 13 agents de la deuxième passe gardent les leurs (0 à 12) ;
# les nouveaux sont ajoutés en fin de liste.
NOMS_BORD = [f"bord_{n}_{v}" for n in NIVEAUX for v in VALEURS_BORD]
NOMS_BORD_D = [f"bordD_{n}_{v}" for n in NIVEAUX for v in VALEURS_BORD]
ID_AGENT_E1 = dict(C.ID_AGENT)
for _nom in ["A0", "A0d"] + NOMS_BORD + NOMS_BORD_D:
    ID_AGENT_E1[_nom] = len(ID_AGENT_E1)

AGENTS_LONG_BASE = ["A0", "A0d", "A1", "A2", "A6b"]


def agent_horizon(agent: C.Agent, T: int) -> C.Agent:
    """Les changements sont placés au milieu de l'horizon (1 500 au court, 75 000 au long)."""
    if agent.t_change is None:
        return agent
    return dataclasses.replace(agent, t_change=T // 2)


def agents_horizon(horizon: str, melange: str) -> list:
    T = HORIZONS[horizon]["T"]
    if horizon == "court":
        base = list(C.AGENTS)
    else:
        par_nom = {**C.AGENTS_PAR_NOM, "A0": A0, "A0d": A0D}
        base = [par_nom[n] for n in AGENTS_LONG_BASE]
    return [agent_horizon(a, T) for a in base + agents_bord(melange)]


def change(agent: C.Agent) -> bool:
    """L'agent change-t-il (taux, modèle ou consigne) pendant l'horizon ?"""
    return agent.t_change is not None


# --------------------------------------------------------------------------
# Section 2 : règles comparées
# --------------------------------------------------------------------------
ALPHA_A = 0.05
NOMS_REGLES = ["A½", "A¼", "A-dégâts", "B-régulier", "B-tout"]
FAMILLE = {"A½": "A", "A¼": "A", "A-dégâts": "A", "B-régulier": "B", "B-tout": "B"}
# Départage final (section 4.3, « puis la plus simple »), fixé avant le lancement :
# B (un compteur pour le palier 3, N en forme close pour B-tout) avant A (deux scores de Wald) ;
# A-dégâts en dernier (pm3 étalonné par simulation).
ORDRE_SIMPLICITE = ["B-tout", "B-régulier", "A½", "A¼", "A-dégâts"]

# pm3 d'A-dégâts (pb3 = pm3 ÷ 2), étalonné par etalonnage_e1.py le 04/11/2026 au soir (méthode
# dans ce module ; détail des itérations et des courbes dans etalonnage_e1.json, graine
# [GRAINE, 20, 1, mélange, niveau]) : l'excès stationnaire du pire agent régulier égale le budget,
# à ±0,5 % près (contrôle hors échantillon). En barres : 3,1 à enjeu faible, 20 à 21 à enjeu moyen
# et fort ; le pire agent régulier est vers 1,4 barre (faible) et 2,5 à 2,7 barres (moyen, fort).
PM3_A_DEGATS = {
    ("bureau", "faible"): 0.07873438500869696,
    ("bureau", "moyen"): 0.06983485739570537,
    ("bureau", "fort"): 0.007803912725743209,
    ("service_client", "faible"): 0.2047594168718612,
    ("service_client", "moyen"): 0.048890481001284666,
    ("service_client", "fort"): 0.004570958066311724,
}


@dataclasses.dataclass
class RegleE1:
    nom: str
    famille: str            # "A" (Wald, amendement A1) ou "B" (séries)
    params: C.ParamsRegle   # palier 2 (réglages de départ), et palier 3 pour A
    N: np.ndarray           # B : longueur par type (0 pour LEC et PLA) ; A : zéros
    lec_autonome: bool = True

    @property
    def N_allonge(self) -> np.ndarray:
        return np.array([n_allonge(int(n)) for n in self.N], dtype=np.int64)


def _params(pb3, pm3, nom) -> C.ParamsRegle:
    dep = C.params_regle("depart", ALPHA_A)
    return C.ParamsRegle(nom=nom, reglage="e1", alpha=ALPHA_A, pb2=dep.pb2.copy(), pm2=dep.pm2.copy(),
                         pb3=np.asarray(pb3, float), pm3=np.asarray(pm3, float),
                         a_palier2=dep.a_palier2.copy(), version="v2")


def niveau_type(k: int) -> str:
    return NIVEAUX[int(C.ENJEU[k])]


def regle_e1(nom: str, melange: str, lec_autonome: bool = True) -> RegleE1:
    dep = C.params_regle("depart", ALPHA_A)
    pb3, pm3 = dep.pb3.copy(), dep.pm3.copy()  # LEC et PLA : sans usage en E1
    N = np.zeros(8, dtype=np.int64)
    for k in range(C.N_MERITES):
        if k == C.LEC:
            continue
        niv = niveau_type(k)
        b = float(BARRES[(melange, niv)])
        if nom == "A½":
            pm3[k], pb3[k] = b, b / 2
        elif nom == "A¼":
            pm3[k], pb3[k] = b, b / 4
        elif nom == "A-dégâts":
            pm = PM3_A_DEGATS[(melange, niv)]
            pm3[k], pb3[k] = pm, pm / 2
        elif nom == "B-régulier":
            N[k] = N_B_REGULIER[(melange, niv)]
        elif nom == "B-tout":
            N[k] = N_B_TOUT[(melange, niv)]
        else:
            raise ValueError(nom)
    return RegleE1(nom, FAMILLE[nom], _params(pb3, pm3, nom), N, lec_autonome)


def regles_e1(melange: str) -> list:
    return [regle_e1(n, melange) for n in NOMS_REGLES]


# --------------------------------------------------------------------------
# Mesure 9 : tests de résistance (hors du choix)
# --------------------------------------------------------------------------
MODES = ["base", "rate10", "difficiles", "retard10"]
PART_RATEE = 0.10   # le contrôle automatique rate 10 % des erreurs, au hasard, sur une graine à part
RETARD_K = 10       # le constat arrive 10 actions du type après l'action
