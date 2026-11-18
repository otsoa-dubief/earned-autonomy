# Max-T recentré : choix de mise en œuvre (08/11/2026)

Sources :
- relecture indépendante C13 du code du verdict, constats C1 (M1 au suivi), C5, point 1 (M5) et C6 (M6) :
  `revues/2026-11-07_C13_moteur_verdict.md` ; suites : `revues/2026-11-07_C13_suites.md` ;
- mesure préenregistrée des corrections : `simulation/controle3/maxt_niveau/` (méthode commitée avant le calcul ;
  résultats : commit 9d7f9d9).

Décision : **F3, 97,5e centile (Otsoa, 08/11)**, sur recommandation de Claude après la relecture indépendante. La règle
est introduite avant toute donnée d'évaluation.
- La règle de choix de la mesure (METHODE.md, section 4), appliquée à ses seuls tirages, désigne F1 (5,0 % en N1).
- Deux tirages antérieurs de la même quantité donnaient 15 sur 200 chacun : en cumul, F1 est à 6,7 % (Wilson 4,9 à
  9,0 %). Appliquée à tous les tirages, la règle retient F3 (3,0 % sur 200 tirages).
- Recommandation de Claude, après la relecture indépendante du 08/11 : F3 ; retenue par Otsoa le même jour.
- Le commit 5e87ae0 applique F1 ; le septième passage du contrôle 3 a tourné avec elle et sert de comparaison. Le
  commit 228c522 applique F3 (constante `CENTILE` = 0,975) ; huitième passage du contrôle 3 avec elle.

## 1. Ce qui change dans le moteur

- **`maxt.depassement_etabli`** :
  - T*_bc = (estimation*_bc − moyenne des répétitions_c) ÷ écart type_c. Avant : estimation*_bc − estimation_c.
  - c* = 97,5e centile (`CENTILE`), sur les répétitions, du maximum des T*_bc sur les cellules testables, ramené à 0
    s'il est négatif. Avant : 95e centile, sans plancher.
  - La borne et la décision ne changent pas : dépassement établi si estimation_c − c* × écart type_c dépasse le budget.
  - Motif « estimation non définie » (estimation NaN ou infinie). Priorité des motifs : moins de deux tâches
    porteuses, estimation non définie, écart type non défini, écart type nul.
  - Tolérance d'un écart type nul : quatre epsilon du float32, soit environ 4,8 × 10⁻⁷, relative à la plus grande
    valeur absolue de l'estimation, du budget et des répétitions. Avant : racine de l'epsilon du float64, environ
    1,5 × 10⁻⁸, relative à l'estimation et au budget.
- **Appelants inchangés.** `decision.cellules` (point 1, B-tout) et `decision.depassement_temoin` (point 2, témoins)
  appellent la même fonction. La correction vaut donc aussi pour les témoins, comme la mesure le prévoyait (METHODE.md,
  section 4).

## 2. Choix (Tranché par Claude)

1. **Plancher de c\* à 0.** Il fait partie de F1 et de F3 telles que mesurées. Sans lui, une loi bootstrap très
   asymétrique donne un c* négatif, et la borne passe au-dessus de l'estimation (relecture C13, C1, preuve 5).
   - Limite (relecture indépendante du 08/11) : quand le plancher joue, la borne vaut l'estimation, et la cellule est
     jugée sur son estimation seule, comme avec la règle remplacée le 07/11 pour l'écart type nul.
   - Mesuré (`controle3/maxt_niveau/descriptif_apres_mesure.txt`, section 5) : le plancher n'a joué dans aucune famille
     des 510 répétitions ; pour une cellule testée seule, dans 0 à 3,3 % des cas selon le régime. Limite déclarée au plan (5.14,
     point 2).
2. **Moyenne des répétitions de la cellule.** Une cellule testable n'a aucune répétition NaN (sinon son écart type
   n'est pas défini) : la moyenne porte sur les B répétitions.
3. **Tolérance plutôt que répétitions en float64.** La relecture proposait l'un ou l'autre.
   - Ranger les répétitions en float64 doublerait la mémoire du magasin.
   - Ce rangement toucherait aussi tous les intervalles du moteur.
   - La tolérance ne change que le cas visé : des répétitions égales à l'arrondi près.
   - Son échelle inclut les répétitions (relecture du 08/11, constat 9) : l'arrondi du float32 suit leur grandeur.
   - Le test passe par `analyse.Quantite`, comme le moteur.
4. **Estimation non définie.** NaN et infini sont traités ensemble. Le motif vient après celui des tâches porteuses,
   comme la relecture le proposait. Une telle cellule n'entre pas dans le maximum : avec T* recentré, elle aurait
   sinon pesé sur c* sans pouvoir rien établir.

## 3. Recoupement

Script : `controle3/maxt_niveau/recoupement_moteur.py` ; sortie : `recoupement_moteur.txt`.
- Il porte sur les 510 répétitions de la mesure : régimes N1, N2, P2, P1 et P4, plus P3, évalué sur les répétitions de
  N2 (610 évaluations).
- Le moteur et la formule mesurée qu'il applique prennent les mêmes décisions, cellule par cellule : F1 au commit
  5e87ae0, F3 au commit 228c522.
- La nouvelle tolérance ne change la testabilité d'aucune cellule.

## 4. Tests

`rejeu/tests/test_rejeu_maxt.py` :
- T* recentré : des répétitions décalées de deux écarts types sous l'estimation n'établissent plus rien ;
- c* jamais négatif ;
- estimation non définie : motif propre, hors du maximum ;
- priorité des quatre motifs ;
- arrondi float32 à travers `analyse.Quantite` : des répétitions égales à l'arrondi float64 près, à cheval sur deux
  float32, restent « aucune variation bootstrap » ;
- c* attendu recalculé avec la formule recentrée dans les tests existants.

Ajoutés au commit 228c522 (relecture du 08/11, constat 10) : c* contre une valeur exacte à deux cellules ; estimation
infinie ; zéro ou une répétition ; borne égale au budget ; valeur de la tolérance épinglée ; arrondi float32 à
l'échelle des répétitions.

Suite de la simulation : 354 réussis, 1 échec attendu (commit 5e87ae0) ; 363 réussis, 1 échec attendu (commit 228c522).

## 5. Empreintes et mesures refaites

Le moteur change. Comme la méthode de la mesure le prévoyait (METHODE.md, section 4, « Ensuite »), on refait avec F1 :
- **le contrôle 3** : septième passage (`controle3/resultats_v7/`), même graine que le sixième, donc apparié ;
  `controle3.lancer --verifier` compare désormais le code au septième passage ;
- **la seconde mesure de B-seuil** : `controle3/b_seuil/seconde_mesure_v7.*` ;
- **les cellules de 2 à 5 tâches porteuses** : `controle3/porteuses/porteuses_v7.*`. Le seuil de deux tâches tient.
  - Au budget exact, au plus 0,11 % de dépassement établi à tort (borne haute de Wilson 0,20 %). Avant : 0,15 %.
  - À cinq fois le budget, la puissance descriptive va de 0,1 à 5,5 %. Avant : 0,9 à 7,2 %.
  - Une part de l'ancienne puissance venait du décentrage, qui faisait aussi les faux dépassements.
- **les sorties agrégées du pilote**, où l'empreinte de `maxt.py` est inscrite.

La mesure du niveau (`maxt_niveau.py`) garde ses propres formules et ses constantes. Ses résultats restent ceux de la
mesure.
