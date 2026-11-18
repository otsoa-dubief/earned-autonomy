# Passe exploratoire du 18/11/2026 (après le verdict, sans effet sur l'étiquette R4)

Demandée par Otsoa (« y a-t-il autre chose à tirer de l'étude ? »). Scripts : `outils/analyses_exploratoires_2.py` (sorties agrégées dans `experience/exploratoire_2/`, H à L) et `outils/analyses_exploratoires_2_dates.py`. Mêmes règles de comptage que le moteur et que la première passe (13 623 parties gardées, tâches retirées exclues, alertes confirmées). Toutes ces questions ont été posées après avoir vu les résultats : description, pas tests.

## 1. Réussir la tâche ne veut pas dire agir juste (tableau I)
- WorkBench : 64 à 82 % des parties avec une erreur d'action confirmée sont des tâches réussies ; 56 à 79 % des erreurs confirmées tombent dans des tâches réussies (le banc ne note que l'état final).
- τ-bench (aviation, commerce) : 0 à 14 % seulement (le banc compare aussi les actions).
- Dans l'autre sens, partout : 47 à 77 % des parties échouées n'ont aucune erreur d'action confirmée.
- Les deux mesures (tâche, action) se recouvrent mal dans les deux sens.

## 2. Sur WorkBench, un seul outil porte la plupart des erreurs (tableau H)
- `analytics.create_plot` : 156 des 247 erreurs confirmées de WorkBench (taux 27 % par écriture).
- Type jugé (WorkBench/Haiku, écritures réversibles, moitié de calibration) : 55 à 56 des 79 erreurs viennent de cet outil ; sans lui, 24 erreurs (2,6 %).

## 3. Relecture incohérente sur les graphiques
- Même écart (graphique tracé jusqu'au 30/11, « aujourd'hui », au lieu du 29/11 attendu par le banc) : levé 168 fois (« la consigne "since X" ne fixe pas de fin »), confirmé 137 fois (« date différente, équivalence non prouvable »).
- 40 des 46 tâches de graphiques ont des alertes tranchées dans les deux sens.
- Sensibilité du type jugé (borne basse à ρ = 1 contre une barre de 0,7575 %) :
  - décisions du moteur : 79 erreurs, borne basse 4,14 %, établi ;
  - toutes les « fin au 30 seule » levées : 43 erreurs, 1,58 %, établi ;
  - en levant aussi les décalages de dates (approximation) : 33 erreurs, 0,98 %, établi ;
  - toutes les « fin au 30 » confirmées : 143 erreurs, 9,46 %, établi ;
  - sans aucune erreur de graphique : 24 erreurs, 0,51 %, **non établi**.
- Le dépassement qui porte R4 survit à une décision cohérente sur l'écart de date, mais pas au retrait de toutes les erreurs de graphiques (dont certaines sont de vraies fautes : graphique créé alors que la condition de la consigne était fausse).

## 4. Erreurs systématiques sur WorkBench, aléatoires sur τ-bench (tableau L)
- WorkBench : les 10 % de tâches les plus touchées portent 94 à 100 % des erreurs ; pour Haiku, une tâche fautive l'est dans 46 % de ses passages en moyenne, et 5 tâches dans tous.
- Aviation et commerce : 57 à 83 % ; une tâche fautive l'est dans 10 à 25 % de ses passages.
- Cohérent avec le ρ̂ élevé de WorkBench (0,819 et 1,0) et faible ailleurs (0,40 à 0,47).

## 5. Autres
- Position (hors banque) : en commerce, la première écriture d'une partie se trompe plus souvent (6,1 % contre 3,4 % pour les suivantes) ; WorkBench et aviation : écart faible ; banque : l'inverse (15,0 % contre 29,5 %).
- Profil par modèle (tableau J) : les erreurs d'Opus et de Sonnet sont presque toutes des écritures fausses ; Haiku a aussi 5 à 19 % d'écritures refusées. Taux par écriture : Haiku au-dessus d'Opus et de Sonnet sur WorkBench (5,6 contre 3,0 à 3,3) et en commerce (5,6 contre 3,2 à 3,7), proche en aviation (5,1 à 6,6).

## Ce que cela change pour l'article
- Le point 3 touche directement le type qui porte R4 : il devrait être déclaré (analyse exploratoire, limite).
- Le point 1 est l'enseignement le plus utile pour ceux qui évaluent des agents.
- Les points 2 et 4 éclairent la corrélation intra-tâche et la portée du verdict.
