"""Types de la règle dans le rejeu (PLAN_EXPERIENCE.md, 5.3).

`simulation/config.py` code les 8 types d'E1 en dur ; ici, la liste est paramétrée (enjeu, palier 2, mérité ou non).
Les codes reprennent ceux d'E1 pour les types communs (LEC = 0 … ARG = 6), ce qui permet de rejouer un flux d'E1
dans le moteur du rejeu (test de non-régression, 5.16, point 1). E1 avait un type à part PLA (7) : dans le rejeu,
« plafonnée » est un drapeau posé sur une écriture qui garde son type (5.3, dernière ligne du tableau) ; les codes 7
et 8 vont aux deux types nouveaux, GAR et ILL.

- LEC n'entre jamais dans une suite : les lectures sont retirées et comptées par partie (5.5, point 2.iv), ce qui
  revient à l'interrupteur `lec_autonome` d'E1 (autonome dès le départ, sans preuve, sans charge, sans dégât).
- GAR et ILL sont des types à part, à enjeu fort, sans palier 2 (5.3, « GAR et ILL », Découle).
"""
from dataclasses import dataclass

import numpy as np

import config as C

FAIBLE, MOYEN, FORT = C.FAIBLE, C.MOYEN, C.FORT
NIVEAUX = tuple(C.NIVEAUX)  # ("faible", "moyen", "fort")


@dataclass(frozen=True)
class TypeRegle:
    code: int
    sigle: str
    nom: str        # nom du type dans banc/typage.py et banc/table_outils.json
    enjeu: int      # FAIBLE, MOYEN ou FORT
    palier2: bool   # type réversible : palier 2 permis (pièce 5)
    merite: bool    # l'autonomie se mérite (False : LEC, autonome dès le départ, décision 4)


TABLE = (
    TypeRegle(0, "LEC", "lecture", FAIBLE, False, False),
    TypeRegle(1, "ECR", "écriture réversible", FAIBLE, True, True),
    TypeRegle(2, "DUR", "écriture durable", MOYEN, False, True),
    TypeRegle(3, "EXE", "exécution et délégation", MOYEN, True, True),
    TypeRegle(4, "MSG", "message interne", FAIBLE, False, True),
    TypeRegle(5, "SOR", "sortie vers l'extérieur", FORT, False, True),
    TypeRegle(6, "ARG", "argent", FORT, False, True),
    TypeRegle(7, "GAR", "garde-fou ou droits", FORT, False, True),
    TypeRegle(8, "ILL", "effet illisible", FORT, False, True),
)
LEC, ECR, DUR, EXE, MSG, SOR, ARG, GAR, ILL = range(9)
NT = len(TABLE)
SIGLES = tuple(t.sigle for t in TABLE)
# Code de remplissage des suites de longueur variable (5.5, point 6) : ne change aucun état, n'est compté nulle part.
VIDE = -1

ENJEU = np.array([t.enjeu for t in TABLE], dtype=np.int8)
A_PALIER2 = np.array([t.palier2 for t in TABLE], dtype=bool)
MERITE = np.array([t.merite for t in TABLE], dtype=bool)
# Enjeu moyen ou fort : descente immédiate au palier 1 et épreuve (pièce 7) ; LEC est sans objet.
ENJEU_HAUT = (ENJEU >= MOYEN) & MERITE
TYPES_SUITE = tuple(t.code for t in TABLE if t.merite)  # types qui peuvent figurer dans une suite

# Noms du typage (banc/typage.py) hors des types de la règle : ils ne vont jamais dans une suite.
NOM_DOUTE = "doute"
NOM_PREPARATION = "préparation"
CODE_PAR_NOM = {t.nom: t.code for t in TABLE}


def niveau(code: int) -> str:
    return NIVEAUX[int(ENJEU[code])]


def code_type(nom: str) -> int:
    """Code d'un type nommé comme dans banc/typage.py ; KeyError pour doute, préparation ou un nom inconnu."""
    return CODE_PAR_NOM[nom]
