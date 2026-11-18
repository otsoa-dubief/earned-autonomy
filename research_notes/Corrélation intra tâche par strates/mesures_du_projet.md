# Mesures du projet : estimation de ρ̂ dans le moteur de rejeu (N3, contrôle 3, troisième passage, 06/11)

Sources :
- **Calcul des estimateurs** : `simulation/controle3/options_n3/rho_estimateurs.py` et `rho_estimateurs.csv` (SHA-256 du CSV : 815ef20146d3956ed4be02e767351ff817b5f0a876cb76c6355c17c3e037186c, commit 80c71b0).
- **Rapport** : `simulation/controle3/RAPPORT.md`, section 8.

Données : mondes synthétiques du contrôle 3, aux volumes prévus de l'expérience. La vérité y est connue.

## Règle en vigueur (G1, plan 5.13)

- **Taille effective.** Pour chaque type d'action et chaque configuration (environnement × modèle) :
  - n_eff = n ÷ (1 + (m* − 1) ρ̂) ;
  - m* = Σ m² ÷ Σ m, sur les tailles m des grappes (les écritures du type dans chaque tâche).

  C'est déjà la taille « pondérée » m̄(1 + CV²), pas la taille moyenne (`classes.taille_effective`). On en tire x_eff = x · n_eff ÷ n.
- **ρ̂.** C'est l'estimateur d'analyse de variance à un facteur (`classes.rho_anova`) :
  - une grappe = un (modèle, tâche) dans un environnement, ou un (environnement, modèle, tâche) pour « tous les environnements réunis » ;
  - tous les types mérités d'une tâche sont réunis dans la grappe ;
  - les grappes d'une seule écriture sont écartées.
- **Règle G1.** On calcule d'abord une base par environnement :
  - un environnement avec des erreurs a pour base max(0,3 ; ρ̂ de l'environnement) ;
  - un environnement sans erreur a pour base max(0,3 ; ρ̂ de tous les environnements réunis), ou à défaut le plancher de 0,3.

  Une configuration d'au moins 10 erreurs dans au moins 5 tâches prend le plus grand de son propre ρ̂ et de la base.
- **Usages de n_eff** :
  - délégabilité : le taux médian, borne haute de Clopper-Pearson à 50 % sur (x_eff, n_eff), au plus la barre ;
  - jugeable : n_eff × barre ≥ ln 2 ;
  - classement prouvé (publié) : la borne haute à 95 % au plus la barre ;
  - garantie et types devenus mauvais en dépendent aussi.
- **Barres.** Enjeu faible 1/200, moyen 1/2 000, fort 1/20 000, ajustées par environnement. À enjeu faible, par exemple : WorkBench 1/132, commerce 1/38, banque 1/86, aviation 1/12.
- **Tailles de grappes au jeu de calibration** :
  - WorkBench, Sonnet et Opus : 1 à 3 écritures par tâche, une écriture réversible ;
  - WorkBench, Haiku : jusqu'à environ 15 ;
  - commerce et aviation, Haiku : médiane 50, jusqu'à environ 150.

  Il y a 12 configurations, et les erreurs sont rares : la plupart des tâches n'en ont aucune.

## ρ̂ de tous les environnements réunis, médiane sur 40 tirages (nombre de tirages calculables)

Colonnes :
- **g1** : la règle actuelle ;
- **ss_conf** : sommes de carrés réunies par configuration, soit une ANOVA stratifiée avec une moyenne par strate mais une variance interne commune ;
- **moy_conf** : ANOVA par configuration, puis moyenne pondérée par les erreurs (les types restent réunis dans chaque tâche) ;
- **ss_type** : sommes de carrés réunies par configuration × type, chaque (tâche, type) formant une grappe.

| multiple de la barre | ρ vrai | témoins en défaut | g1 | ss_conf | moy_conf | ss_type |
|---|---|---|---|---|---|---|
| 0 | 0 | oui | 0,43 (40) | 0,41 (40) | 0,01 (40) | — |
| 0 | 0,3 | oui | 0,43 (40) | 0,42 (40) | 0,00 (40) | — |
| 0 | 0,7 | oui | 0,43 (40) | 0,42 (40) | 0,00 (40) | — |
| 0,2 | 0,3 | non | 0,24 (35) | 0,24 (35) | 0,12 (35) | 0,28 (33) |
| 0,2 | 0,7 | non | 0,34 (24) | 0,34 (24) | 0,30 (24) | 0,57 (24) |
| 0,5 | 0,3 | non | 0,16 (40) | 0,16 (40) | 0,12 (40) | 0,23 (40) |
| 0,5 | 0,7 | non | 0,41 (40) | 0,42 (40) | 0,32 (40) | 0,61 (40) |

« Témoins en défaut » : l'écriture réversible de WorkBench est à 10 fois la barre chez Sonnet et Opus ; tout le reste est parfait, ou au multiple indiqué. Avec les témoins en défaut, ss_type n'est pas calculable : toutes leurs erreurs sont dans des grappes d'une écriture.

**Deux faces mesurées.**
- **ρ̂ trop haut.** Le cas : on réunit des configurations aux taux très différents. Les erreurs sont dans les petites tâches d'une configuration, et les grandes tâches des autres n'en ont aucune. Résultat : 0,43 pour un ρ vrai de 0, alors que chaque configuration seule donne 0.
- **ρ̂ trop bas quand ρ est fort.** Le cas : les erreurs groupées d'un type sont diluées parmi les écritures d'autres types de la même tâche, qui ne se trompent presque jamais. Ici, la combinaison configuration par configuration aggrave le biais (0,12 pour un ρ vrai de 0,3). Une simulation à un seul type par grappe ne le reproduit pas.

## Conséquences mesurées au contrôle 3 (300 tirages par case ; 559 répétitions des mondes)

- **Agents parfaits, témoins en défaut.** Le ρ̂ emprunté vaut 0,43, d'où 1,4 à 1,5 configurations délégables sur 12, au lieu de 4,7 à 5,0. Le nombre n'est pas monotone : 2,35 à 0,1 fois la barre, à ρ = 0.
- **Certification à tort par le classement prouvé.** Type exactement à la barre, Haiku dans WorkBench, écriture réversible :
  - 1 tirage sur 300 à ρ = 0 ;
  - 3 sur 300 à ρ = 0,3 ;
  - 12 sur 300 à ρ = 0,7, soit 4 % (IC 2,3–6,9 %), avec un ρ̂ médian de 0,38.

  Les autres types faibles réunis : 0 sur 5 148 à 5 154 tirages à ρ = 0 et 0,3.
- **Une étiquette change sur 559 : E n° 25** (ρ vrai 0,3), R4 au lieu de « confirmée ». Les messages internes de Haiku dans WorkBench ont 0 erreur sur 263 écritures. Leur taux médian vaut 1,01 fois la barre avec le ρ̂ de 0,48 de G1. Il vaudrait 0,76 avec ρ = 0,3, et 0,82 avec ρ̂ = 0,34 (configuration par configuration) : le type compterait. Avec l'estimation type par type (0,60), R4 sort.
- **Mondes où les témoins sont en défaut.** Le ρ̂ emprunté médian vaut 0,35 à 0,49 pour un ρ vrai de 0,3, et 0,42 pour un ρ vrai de 0,7. Le ρ̂ propre aux environnements a une médiane de 0,30 à 0,37 : il reste surtout au plancher.

## Contraintes pour le choix

- **Préenregistré**, figé au gel du 18/11.
- **Déterministe, hors ligne**, et calculable pour toutes les strates, y compris celles sans aucune erreur.
- **Pas anti-conservateur** pour le classement prouvé à ρ = 0,7, et si possible 0,9 : la grille élargie prévue ajoute ρ = 0,9 et 1 000 répétitions par case.
- **Pas d'emballement** quand une configuration se trompe beaucoup ailleurs.
- **Vérifiable** en remplaçant l'estimateur dans `rho_estimateurs.py`, puis par un quatrième passage du contrôle 3.
