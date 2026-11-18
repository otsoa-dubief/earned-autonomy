"""Moteur de rejeu de l'expérience « autonomie méritée », phases 1 et 2 (PLAN_EXPERIENCE.md, section 5).

La règle figée (B-tout) et les règles rejouées à côté sont appliquées hors ligne, écriture par écriture, aux
parties enregistrées (5.1). Phase 1 : le cœur du rejeu. Phase 2 : intervalles, scénarios, résistance, décision,
sorties (modules plus bas).

Modules, dans l'ordre du plan :
- `types_regle`  : types de la règle (5.3) ;
- `config_rejeu` : configuration figée, barres et N en fractions exactes (5.2, point 6 ; annexe A1) ;
- `entrees`      : parties, actions typées, décisions sur les alertes, tâches retirées, appartenance (5.2) ;
- `preuves`      : des verdicts aux preuves et aux dégâts, cas particuliers (5.4 et 5.8) ;
- `suites`       : construction des suites, graines, ordre figé, couche bootstrap (5.5) ;
- `epreuves`     : épreuves jouées à blanc, variantes tirées dans des parties enregistrées (5.9) ;
- `regles`       : règles comparées et références par type (5.6) ;
- `moteur`       : moteur vectorisé et comptabilité (5.6, 5.8), adaptés de `regle_e1.simuler_e1` et `Compteur` ;
- `classes`      : classes « sous la barre », « au-dessus », « indéterminé » (5.12, point 4) ; phase 2 :
                   Clopper-Pearson sur la taille effective, ρ̂ et son repli, bêta-binomial descriptif (5.13) ;
- `temoins`      : règles témoins (5.7) ;
- `mesures`      : mesures de base par cellule, sans intervalles (5.12) ;
- `rejeu`        : rejeu d'une configuration (couche R0), empreinte de déterminisme (5.16, point 7).

Phase 2 :
- `intervalles`  : les trois méthodes candidates, la règle de choix, « fragile » par seconde méthode (5.13) ;
- `couverture`   : simulation de couverture sur données synthétiques, script à part (5.16, point 5) ;
- `lots`         : colonnes groupées (R0, bootstrap à tirage commun, jackknife), scénarios, résistance (5.5, 5.10,
                   5.11) ;
- `analyse`      : rejeu d'un lot, valeurs par répétition, écarts types par grappe, magasin des quantités ;
- `pipeline`     : configurations et scénarios, moyennes sur les configurations délégables, relance (5.13) ;
- `maxt`         : dépassement établi par max-T de Westfall et Young (5.14, point 2 ; 5.16, point 8) ;
- `decision`     : règle de décision, étiquettes, « fragile », règle de choix, hasard, alerte (5.14) ;
- `sorties`      : CSV, meta.json, RESULTATS.md (5.15) ;
- `bout_en_bout` : toutes les analyses et les sorties ; bout en bout sur le pilote (5.16, point 6) ; phase 3 : entrée
                   de l'expérience réelle, essai à blanc, parallélisation par familles.

Phase 3 :
- `couverture_charge` : simulation de couverture refaite sur la différence appariée de charge (Q13).

Choix d'implémentation : `CHOIX_PHASE1.md`, `CHOIX_PHASE2.md`, `CHOIX_PHASE3.md`. Le code d'E1 n'est pas modifié : il est importé tel quel, ou copié et
adapté ici en citant sa source (5.17).
"""
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
SIMULATION = os.path.dirname(ICI)
RACINE = os.path.dirname(SIMULATION)
if SIMULATION not in sys.path:  # les modules d'E1 s'importent par leur nom (import config, regle_e1...)
    sys.path.insert(0, SIMULATION)
