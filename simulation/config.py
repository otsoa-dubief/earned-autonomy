"""Paramètres de la simulation de niveau 1.

Toutes les valeurs viennent de PLAN_SIMULATION.md (sections 1 à 5) : ce sont des
hypothèses déclarées du plan, pas des mesures. Les changer, c'est changer le plan.
"""
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

# --------------------------------------------------------------------------
# Graine maîtresse (notée dans RESULTATS.md)
# --------------------------------------------------------------------------
GRAINE = 20261104

# --------------------------------------------------------------------------
# 1. Types d'action (pièce 2), plan section 1
# --------------------------------------------------------------------------
TYPES = ["LEC", "ECR", "DUR", "EXE", "MSG", "SOR", "ARG", "PLA"]
LEC, ECR, DUR, EXE, MSG, SOR, ARG, PLA = range(8)
N_TYPES = 8
N_MERITES = 7  # types où l'autonomie se mérite (tous sauf PLA)

NOMS_TYPES = {
    "LEC": "Lecture", "ECR": "Écriture réversible", "DUR": "Écriture durable",
    "EXE": "Exécution et délégation", "MSG": "Message interne",
    "SOR": "Sortie vers l'extérieur", "ARG": "Argent sous le montant", "PLA": "Plafonné",
}

NIVEAUX = ["faible", "moyen", "fort"]
FAIBLE, MOYEN, FORT = 0, 1, 2
# Niveau d'enjeu de chaque type. PLA : plafonds absolus, argent au-delà du montant,
# premier message à un inconnu -> enjeu fort pour le compte des dégâts (pièce 2 :
# « modifier un garde-fou ou des droits (fort) »).
ENJEU = np.array([FAIBLE, FAIBLE, MOYEN, MOYEN, FAIBLE, FORT, FORT, FORT], dtype=np.int8)
# Enjeu moyen ou fort : déclenche la descente immédiate et l'épreuve (pièce 7).
ENJEU_HAUT = ENJEU >= MOYEN
ENJEU_HAUT[PLA] = False  # PLA n'est jamais autonome : sans objet
# Types réversibles qui ont le palier 2 (plan, tableau de la section 1).
A_PALIER2 = np.array([True, True, False, True, False, False, False, False])

# --------------------------------------------------------------------------
# 2. Flux d'actions, plan section 2
# --------------------------------------------------------------------------
# Catégories internes du flux : les plafonnés sont tirés depuis trois sources,
# pour que leur taux d'erreur soit celui du type d'origine.
CATS = ["LEC", "ECR", "DUR", "EXE", "MSG", "SOR", "ARG", "PLA_abs", "PLA_SOR", "PLA_ARG"]
CAT_TYPE = np.array([LEC, ECR, DUR, EXE, MSG, SOR, ARG, PLA, PLA, PLA], dtype=np.int8)
# Indice du taux d'erreur à utiliser (dans le vecteur q d'un agent, longueur 8 ;
# l'indice 7 porte le taux « partout » de l'agent, utilisé pour les plafonds absolus).
CAT_TAUX = np.array([LEC, ECR, DUR, EXE, MSG, SOR, ARG, 7, SOR, ARG])

PART_PLAFONNEE_SOR = 0.20  # premier message à une personne inconnue
PART_PLAFONNEE_ARG = 0.20  # argent au-delà du montant

MELANGES_BRUTS = {
    # parts de SOR et ARG incluant leur fraction plafonnée ; PLA = plafonds absolus
    "bureau": dict(LEC=.45, ECR=.15, DUR=.08, EXE=.08, MSG=.06, SOR=.12, ARG=.05, PLA=.01),
    "service_client": dict(LEC=.40, ECR=.05, DUR=.20, EXE=.02, MSG=.03, SOR=.15, ARG=.14, PLA=.01),
}
NOMS_MELANGES = {"bureau": "« bureau »", "service_client": "« service client »"}


def probas_categories(melange: str) -> np.ndarray:
    m = MELANGES_BRUTS[melange]
    p = np.array([
        m["LEC"], m["ECR"], m["DUR"], m["EXE"], m["MSG"],
        m["SOR"] * (1 - PART_PLAFONNEE_SOR), m["ARG"] * (1 - PART_PLAFONNEE_ARG),
        m["PLA"], m["SOR"] * PART_PLAFONNEE_SOR, m["ARG"] * PART_PLAFONNEE_ARG,
    ])
    assert abs(p.sum() - 1.0) < 1e-12, (melange, p.sum())
    return p


PART_INVERIFIABLE = 0.05
HORIZON = 3000
R_CAS = 1000      # répétitions par cas
R_CLES = 5000     # répétitions pour les cas clés
T_CHANGEMENT = 1500

# --------------------------------------------------------------------------
# 3. Agents fictifs, plan section 3
# --------------------------------------------------------------------------
PART_DIFFICILE = 0.10   # h
FACTEUR_DIFFICILE = 6.0  # taux des cas difficiles = min(0,9 ; 6 q)
PLAFOND_DIFFICILE = 0.9

PROBA_DOUTE_CALIBRE = 0.5  # sur une action difficile
PROBA_DOUTE_ABUSIF = 0.30  # sur toutes les actions


def taux_difficile(q):
    return np.minimum(PLAFOND_DIFFICILE, FACTEUR_DIFFICILE * np.asarray(q, dtype=float))


def taux_facile(q):
    q = np.asarray(q, dtype=float)
    return (q - PART_DIFFICILE * taux_difficile(q)) / (1 - PART_DIFFICILE)


def vecteur_q(partout: float, **exceptions) -> np.ndarray:
    """Vecteur de taux d'erreur de longueur 8 : 7 types mérités + le taux « partout »."""
    q = np.full(8, partout, dtype=float)
    for nom, val in exceptions.items():
        q[TYPES.index(nom)] = val
    q[7] = partout
    return q


@dataclass(frozen=True)
class Agent:
    nom: str
    description: str
    q_avant: tuple
    q_apres: Optional[tuple] = None
    t_change: Optional[int] = None
    evenement: Optional[str] = None  # None, "modele", "consigne_SOR"
    doute: str = "jamais"            # "jamais", "calibre", "abusif"

    def q(self, apres: bool) -> np.ndarray:
        if apres and self.q_apres is not None:
            return np.array(self.q_apres)
        return np.array(self.q_avant)

    @property
    def proba_doute_epreuve(self) -> float:
        # les variantes d'épreuve sont des cas difficiles
        return {"jamais": 0.0, "calibre": PROBA_DOUTE_CALIBRE, "abusif": PROBA_DOUTE_ABUSIF}[self.doute]


def _t(v):
    return tuple(float(x) for x in v)


AGENTS = [
    Agent("A1", "excellent (0,5 %)", _t(vecteur_q(0.005))),
    Agent("A2", "bon (2 %)", _t(vecteur_q(0.02))),
    Agent("A3", "moyen (5 %)", _t(vecteur_q(0.05))),
    Agent("A4", "mauvais (15 %)", _t(vecteur_q(0.15))),
    Agent("A5", "mauvais sur la sortie (2 %, SOR 15 %)", _t(vecteur_q(0.02, SOR=0.15))),
    Agent("A6a", "dégradation annoncée (2 % puis 10 %, changement de modèle)",
          _t(vecteur_q(0.02)), _t(vecteur_q(0.10)), T_CHANGEMENT, "modele"),
    Agent("A6b", "dérive silencieuse (2 % puis 10 %, rien d'annoncé)",
          _t(vecteur_q(0.02)), _t(vecteur_q(0.10)), T_CHANGEMENT, None),
    Agent("A7", "amélioration annoncée (10 % puis 2 %, changement de modèle)",
          _t(vecteur_q(0.10)), _t(vecteur_q(0.02)), T_CHANGEMENT, "modele"),
    Agent("A8", "consigne modifiée sur SOR (A2, r de SOR divisé par deux)",
          _t(vecteur_q(0.02)), None, T_CHANGEMENT, "consigne_SOR"),
    Agent("A2-calibre", "A2, doute calibré", _t(vecteur_q(0.02)), doute="calibre"),
    Agent("A2-abusif", "A2, doute abusif", _t(vecteur_q(0.02)), doute="abusif"),
    Agent("A4-calibre", "A4, doute calibré", _t(vecteur_q(0.15)), doute="calibre"),
    Agent("A4-abusif", "A4, doute abusif", _t(vecteur_q(0.15)), doute="abusif"),
]
AGENTS_PAR_NOM = {a.nom: a for a in AGENTS}
# identifiant stable pour les graines (pas le hash() de Python, qui est salé)
ID_AGENT = {a.nom: i for i, a in enumerate(AGENTS)}


def agent_q_constant(q: float) -> Agent:
    """Agent de balayage pour la courbe de garantie (même q sur tous les types)."""
    return Agent(f"q={q:g}", f"taux constant {q:.2%}", _t(vecteur_q(q)))


# --------------------------------------------------------------------------
# 4. Validateur humain simulé, plan section 4
# --------------------------------------------------------------------------
VALEURS_E = [0.0, 0.02, 0.05, 0.10]
E_PRINCIPAL = 0.05
# Amendement A1 : grille fine de marges (points pour 100 actions), lue à l'aveugle par Otsoa
MARGES = [0.0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
MARGES_V1 = [0.0, 0.1, 0.5]  # grille de la première passe

# --------------------------------------------------------------------------
# 5. La règle, plan section 5
# --------------------------------------------------------------------------
BETA = 0.05
ALPHAS = [0.05, 0.20]
FACTEURS_REGLAGE = {"stricte": 0.5, "depart": 1.0, "souple": 1.5}
# (pb ; pm) au départ, par niveau d'enjeu et par palier visé
REGLAGES_DEPART = {
    (FAIBLE, 3): (0.05, 0.20), (FAIBLE, 2): (0.10, 0.30),
    (MOYEN, 3): (0.02, 0.10), (MOYEN, 2): (0.05, 0.20),
    (FORT, 3): (0.01, 0.05),
}
EPREUVE_VARIANTES = 3
EPREUVE_ATTENTE = 50
TOL = 1e-9  # « sous ln B » lu comme « au plus ln B » (voir RESULTATS.md, choix d'implémentation)

# Version de la règle.
# "v2" (défaut) : amendement A1 de REGLE.md (score réfléchi L par type et par palier visé ; au
#                 changement de modèle, les erreurs à enjeu faible disparaissent).
# "v1"          : première passe (compteurs r et s, r plafonné) ; gardée pour reproduire resultats_v1/.
VERSION = "v2"


@dataclass
class ParamsRegle:
    """Réglages d'une variante de la règle, type par type (tableaux de longueur 8)."""
    nom: str
    reglage: str
    alpha: float
    pb2: np.ndarray
    pm2: np.ndarray
    pb3: np.ndarray
    pm3: np.ndarray
    a_palier2: np.ndarray
    remises: bool = True          # pièce 8 (changement de modèle, droits, consigne)
    epreuves: bool = True         # pièce 7 et 8
    doute_erreur: bool = False    # témoin « sans doute gratuit »
    oubli_faibles_au_changement: bool = False  # v1 seulement : lecture de REGLE.md pièce 8 (sensibilité)
    plancher_glissant: bool = False            # v1 seulement : hors plan, exploratoire
    version: str = VERSION
    a2: np.ndarray = field(init=False)
    b2: np.ndarray = field(init=False)
    a3: np.ndarray = field(init=False)
    b3: np.ndarray = field(init=False)
    lnB: float = field(init=False)
    rmax: np.ndarray = field(init=False)
    plancher2: np.ndarray = field(init=False)
    plancher3: np.ndarray = field(init=False)

    def __post_init__(self):
        self.lnB = float(np.log(BETA / (1 - self.alpha)))
        self.a3 = np.log(self.pm3 / self.pb3)
        self.b3 = -np.log((1 - self.pm3) / (1 - self.pb3))
        with np.errstate(divide="ignore", invalid="ignore"):
            a2 = np.log(self.pm2 / self.pb2)
            b2 = -np.log((1 - self.pm2) / (1 - self.pb2))
        self.a2 = np.where(self.a_palier2, a2, 0.0)
        self.b2 = np.where(self.a_palier2, b2, 0.0)
        # v1 : plancher par r plafonné à r_max = (a - ln B)/b sur le test le plus strict (palier 3)
        self.rmax = (self.a3 - self.lnB) / self.b3
        # v2 (A1) : plancher du score réfléchi, ln B − a, pour chaque palier visé
        self.plancher3 = self.lnB - self.a3
        self.plancher2 = np.where(self.a_palier2, self.lnB - self.a2, 0.0)
        assert self.version in ("v1", "v2"), self.version


def params_regle(reglage: str = "depart", alpha: float = 0.05, *, sans_ponderation=False,
                 sans_palier_milieu=False, remises=True, epreuves=True, doute_erreur=False,
                 oubli_faibles_au_changement=False, plancher_glissant=False, nom=None,
                 version=None) -> ParamsRegle:
    f = FACTEURS_REGLAGE[reglage]
    a_p2 = A_PALIER2.copy()
    if sans_palier_milieu:
        a_p2[:] = False
    pb2 = np.ones(8); pm2 = np.ones(8); pb3 = np.ones(8); pm3 = np.ones(8)
    for k in range(N_MERITES):
        niv = MOYEN if sans_ponderation else int(ENJEU[k])
        pb3[k], pm3[k] = (x * f for x in REGLAGES_DEPART[(niv, 3)])
        if a_p2[k]:
            pb2[k], pm2[k] = (x * f for x in REGLAGES_DEPART[(niv, 2)])
    # PLA : valeurs neutres, jamais utilisées (PLA reste au palier 1)
    pb3[PLA], pm3[PLA] = 0.01, 0.05
    if nom is None:
        nom = "regle"
    version = VERSION if version is None else version
    if version == "v2" and (oubli_faibles_au_changement or plancher_glissant):
        raise ValueError("options de la v1 seulement")
    return ParamsRegle(nom=nom, reglage=reglage, alpha=alpha, pb2=pb2, pm2=pm2, pb3=pb3, pm3=pm3,
                       a_palier2=a_p2, remises=remises, epreuves=epreuves, doute_erreur=doute_erreur,
                       oubli_faibles_au_changement=oubli_faibles_au_changement,
                       plancher_glissant=plancher_glissant, version=version)


REGLAGES = [(r, a) for r in ["stricte", "depart", "souple"] for a in ALPHAS]
REGLAGE_PRINCIPAL = ("depart", 0.05)


def nom_reglage(reglage: str, alpha: float) -> str:
    return f"{reglage} α={int(round(alpha * 100))} %"


ABLATIONS = {
    "sans_remise": dict(remises=False),
    "sans_ponderation": dict(sans_ponderation=True),
    "sans_doute_gratuit": dict(doute_erreur=True),
    "sans_palier_milieu": dict(sans_palier_milieu=True),
    "sans_epreuve": dict(epreuves=False),
}
NOMS_ABLATIONS = {
    "sans_remise": "sans remise à zéro",
    "sans_ponderation": "sans pondération par l'enjeu",
    "sans_doute_gratuit": "sans doute gratuit",
    "sans_palier_milieu": "sans palier du milieu",
    "sans_epreuve": "sans épreuve",
}
