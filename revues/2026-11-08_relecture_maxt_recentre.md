# Relecture indépendante du max-T recentré (08/11/2026)

Agent neuf, qui n'a pas suivi les échanges. Lecture seule, sans accès à `donnees/`, ni au pilote, ni aux résultats des
bancs. Périmètre : diff 9d7f9d9..6fa6ce9 (moteur, tests, scripts de la mesure, plan, règle, journal, rapport,
suites C13). Douze constats. Chacun a été relu par le coordinateur, et ses chiffres ont été vérifiés dans les sources
(relecture C13, C1, preuve 4 ; `METHODE.md`, en tête ; sorties de la mesure).

Statuts :
- **fait** : corrigé, avec le commit ;
- **à faire** : retenu, pas encore fait ;
- **non retenu** : écarté, avec sa raison.

| N° | Gravité | Constat | Suite retenue | Statut |
|---|---|---|---|---|
| 1 | à corriger | Le niveau de F1 repose sur le seul tirage de la mesure (10 sur 200). Deux tirages antérieurs de la même quantité donnaient 15 sur 200 chacun : en cumul, 40 sur 600, soit 6,7 % (Wilson 4,9 à 9,0 %). | Cumul cité dans le plan (5.14, point 2 ; section 6), `REGLE.md`, le journal, le rapport (12.1) et `CHOIX_MAXT_RECENTRE.md`. **Recommandation de Claude changée de F1 à F3 ; F3 décidée par Otsoa le 08/11.** Mesure de confirmation écrite avant le calcul (`maxt_niveau/CONFIRMATION.md`, 54d923c), lancée après le contrôle 3 en cours. | fait pour les textes ; confirmation faite (bb45168 ; rapport du contrôle 3, 12.5) : F3 à 4,7 % en cumul (28 sur 600, Wilson 3,2 à 6,7 %) |
| 2 | à corriger | « Les rejets à tort viennent surtout de WorkBench » n'était établi par aucune sortie ; « 16 % » = 32 sur 200, soit 32 sur 154 répétitions testables. | `descriptif_apres_mesure.py`, section 3 : 6 des 10 rejets de F1 portent sur WorkBench à enjeu faible. « 32 sur 154 » donné. | fait (54d923c) |
| 3 | à corriger | La cause suggérée, un écart type bootstrap trop petit, est contredite : la configuration de Haiku dans WorkBench a un rapport de 0,99 et reste la pire cellule seule de F3. Piste : la testabilité dépend des erreurs. | « Cause non établie ». Section 4 du descriptif : la valeur centrale des répétitions testables vaut 1,30 à 1,48 fois θ_G (WorkBench, N1) et 1,54 à 1,96 fois (banque, N2). | fait |
| 4 | à corriger | « De même garantie » que Holm, « garde le risque à 5 % au plus » et la borne de 7,5 % restent écrits comme en vigueur. | Lectures datées : niveau nominal, renvoi au niveau mesuré (plan, l. 62 et 751, Q15, section 8 ; `REGLE.md`). | fait |
| 5 | mineur | « Puissance entière » sans bornes, alors que les cinq formules y font 100 % ; « baisse un peu » à deux tâches porteuses, de 18 à 3 sur 2 000. | Bornes basses de Wilson, « ne les départage pas » ; « six fois moins ». | fait |
| 6 | mineur | « Se dilue », « un peu », « le cas le moins favorable » : vrai pour la configuration d'hypothèses dans le monde A, pas pour le monde ni pour la composition de la famille ; 0 sur 16 sans borne. | « Configuration d'hypothèses la moins favorable dans un monde donné » ; niveaux par monde ; 0 sur 16, borne haute 19 %. | fait |
| 7 | mineur | Mécanisme écrit comme établi (la relecture C13 le classe « déduit ») ; plage de décalage du seul monde B ; réglages R0 = B = 200 absents du plan. | « Déduit » ; plages par monde ; réglages cités. La docstring de `maxt.py` suivra au prochain changement du moteur. | fait (plan ; moteur : 228c522) |
| 8 | mineur | Quand le plancher de c* joue, la borne vaut l'estimation : la cellule est jugée sur son estimation seule. | Limite déclarée (plan, 5.14, point 2 ; `CHOIX_MAXT_RECENTRE.md`). Compté : aucune famille sur 510 répétitions ; 0 à 3,3 % des cellules testées seules. | fait |
| 9 | mineur | La tolérance d'un écart type nul est relative à l'estimation et au budget, alors que l'arrondi float32 suit la grandeur des répétitions. | Échelle portée à la plus grande valeur absolue de l'estimation, du budget et des répétitions ; test du cas relevé. | fait (228c522) |
| 10 | mineur | Tests : c* vérifié par un calcul qui recopie le code ; manquent un c* indépendant à deux cellules, l'estimation infinie, la valeur de la tolérance, B = 1, la borne égale au budget, un test du moteur sur des cellules de B-tout. | Ajoutés avec le prochain changement du moteur. Le test du moteur sur des cellules de B-tout n'est pas retenu : la mesure (510 répétitions du moteur) et le recoupement cellule par cellule font ce contrôle, trop lourd pour la suite de tests. | fait (228c522) |
| 11 | mineur | Cohérence : « trois conditions » ; ordre des motifs non écrit au plan ; 5.16, point 11, sans les nouveaux tests ; étiquettes manquantes ; « 610 répétitions » pour 510 distinctes. | Corrigés dans les textes. La docstring de `maxt.py` suivra. | fait (textes ; moteur : 228c522) |
| 12 | mineur | F1 présentée sans « à confirmer » dans `maxt.py`, `lancer.py`, la section 6 du plan et `REGLE.md`. | Section 6 et `REGLE.md` réécrites avec F1 et F3. `maxt.py` et `lancer.py` suivront au prochain changement du moteur. | fait (textes ; moteur : 228c522) |

Vérifié sans défaut par la relecture : `maxt.py` applique la F1 de `METHODE.md` ; cas limites conformes (m = 0, aucune
cellule testable, B = 0 ou 1, estimation ou répétition NaN ou infinie, borne égale au budget, tolérance à 3,9 et
4,1 ε du float32) ; `decision.py` passe à `maxt` les mêmes répétitions que la mesure ; chiffres recopiés exacts ;
`porteuses_v7` produit avec le `maxt.py` actuel ; `METHODE.md` commitée avant le lancement de la mesure.

Le moteur a été modifié après le septième passage du contrôle 3 et sa mesure au seuil (commit 228c522), qui lisent
`maxt.py` au démarrage de chaque étape.
