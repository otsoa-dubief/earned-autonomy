"""Contrôle 3 avant le gel (PLAN_EXPERIENCE.md, 5.16 et section 7, étape 6 ; REGLE.md, « Contrôles obligatoires avant
le gel », n° 3) : tests du moteur qui manquaient, et mondes fictifs où la vérité est connue, passés par toute la chaîne
de décision jusqu'à l'étiquette (R5, R1, R4, R2 ou « confirmée »).

Ce dossier n'écrit rien dans `simulation/rejeu/` : le moteur y est appelé tel quel. Données synthétiques seulement ;
aucune donnée d'agent, aucun appel payant.

Modules :
- `mondes`  : les mondes fictifs (paramètres figés) et le générateur des entrées synthétiques ;
- `harnais` : une répétition d'un monde, de la génération à l'étiquette, avec les diagnostics ;
- `lancer`  : le lancement unique, parallélisé, et ses résultats bruts (`resultats/`).
"""
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
SIMULATION = os.path.dirname(ICI)
RACINE = os.path.dirname(SIMULATION)
if SIMULATION not in sys.path:   # `rejeu` et les modules d'E1 s'importent par leur nom
    sys.path.insert(0, SIMULATION)
