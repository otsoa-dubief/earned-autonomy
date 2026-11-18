# Cellule non testable : choix de mise en œuvre (07/11/2026)

Décision d'Otsoa du 07/11, après la recherche approfondie (`reports/Cellules portées par une seule tâche.md`) : plan,
5.14, point 2 ; `REGLE.md`, décision 3 (lecture datée) ; `JOURNAL_CHANGEMENTS.md` (les deux versions côte à côte). La règle
est introduite avant toute donnée d'évaluation.

## 1. Ce qui change dans le moteur

- **`maxt.depassement_etabli`**. La fonction reçoit le nombre de tâches porteuses de chaque cellule (`porteuses`).
  - Une cellule est testable dans trois conditions réunies : au moins `PORTEUSES_MIN` = 2 tâches porteuses, un écart type
    bootstrap défini (aucune répétition NaN), et un écart type non nul à la tolérance près.
    *Complété le 08/11 (relecture C13, C5)* : quatre conditions, avec une estimation définie (`CHOIX_MAXT_RECENTRE.md`).
  - Seules les cellules testables entrent dans le maximum, et seules elles peuvent établir un dépassement.
  - Une cellule non testable reçoit une borne NaN et un motif.
  - La branche « hors maximum, établi si l'estimation dépasse le budget » disparaît.
  - Sans `porteuses` (cellules synthétiques du point 8 de 5.16), seules les conditions sur l'écart type s'appliquent.
- **`decision.cellules`** (point 1, B-tout) passe `porteuses` et publie `non_testable` (le motif, vide si la cellule est
  testable). Le verdict reste « non réfutée ».
- **`decision.cellules_temoin` et `depassement_temoin`** (point 2, témoins) suivent la même règle : chaque ligne porte
  `porteuses` et `non_testable`. Une cellule non testable ne peut pas faire battre un témoin.
- **`sorties`** :
  - colonne `non_testable` dans `budget.csv`, pour les règles et pour les témoins ;
  - nombre de cellules non testables dans la ligne du point 1 et dans celles des témoins de `decision.csv`.
- **Harnais du contrôle 3** :
  - `non_testables` par répétition, au point 1 et pour chaque témoin ;
  - plus haute borne calculée sur les seules bornes définies.

## 2. Choix (Tranché par Claude)

1. **Tolérance d'un écart type nul** : racine de l'epsilon machine, soit environ 1,5 × 10⁻⁸ (celle de libcoin, notes de la
   recherche). Elle est relative à la plus grande de l'estimation et du budget. Une tolérance absolue n'aurait pas le même
   sens aux trois niveaux, dont les budgets vont de 0,5 à 0,005.
   - *Remplacé le 08/11 (relecture C13, C6)* : quatre epsilon du float32, puisque le moteur range les répétitions en
     float32 (`CHOIX_MAXT_RECENTRE.md`, choix 3).
2. **Nombre de tâches porteuses** : celui que calculait déjà `decision.cellules`, soit les tâches qui ont au moins une
   écriture du niveau au dénominateur, sommées sur les jeux de la famille (jeu principal, plus la seconde famille quand
   elle existe). Les deux jeux portent des tâches différentes : la somme compte des tâches distinctes. Les témoins
   comptent de la même façon. Ce nombre ne dépend que de la composition des parties, pas des erreurs : un filtre sur lui
   ne touche pas au risque du test (Bourgon, Gentleman et Huber, notes de la recherche).
3. **Motifs**, dans cet ordre de priorité :
   - « moins de 2 tâches porteuses » ;
   - « écart type bootstrap non défini » ;
   - « aucune variation bootstrap ».
   - *Complété le 08/11 (relecture C13, C5)* : « estimation non définie », juste après le premier
     (`CHOIX_MAXT_RECENTRE.md`, choix 4).
4. **Intervalles inchangés.** L'intervalle descriptif d'une cellule non testable est publié tel quel, avec la mention.
   - Il sert aussi à la règle de choix et à l'alerte de résistance (`decision.regle_de_choix`, `bilan_mode`), qu'il ne
     fallait pas changer.
   - La mention suffit à empêcher qu'on le lise comme un test.
   - La synthèse de la recherche proposait de le marquer « non défini ». Écart retenu : la mention porte la même
     information sans toucher à ces deux usages.
5. **Une seule répétition bootstrap** (B ≤ 1) : écart type non défini, donc cellule non testable. Avant, l'écart type
   était mis à 0, donc la cellule était jugée sur son estimation. Ce cas n'arrive pas avec les réglages du plan.
6. **Seuil de deux tâches** : confirmé par la mesure sur des cellules de 2 à 5 tâches porteuses au budget exact
   (`controle3/porteuses/`, méthode commitée avant le calcul). Au plus 0,15 % de dépassement établi à tort, borne haute
   0,25 %.

## 3. Tests

- `rejeu/tests/test_rejeu_maxt.py` :
  - mécanique revue : l'écart type nul n'établit plus rien ;
  - cellule à une seule tâche porteuse avec un écart type minuscule ;
  - répétitions 0/0 ;
  - variation d'arrondi seule ;
  - priorité des motifs ;
  - c* calculé sur les seules cellules testables.
- `controle3/tests/test_controle3_non_testable.py` (répétition 24 du monde V, réglages du contrôle 3) :
  - plus de faux R1 : « preuves insuffisantes, aucun type jugeable » ;
  - 11 cellules non testables avec leur motif, chacune avec une borne NaN ;
  - témoins : nombre de tâches porteuses et motif ;
  - résumé du harnais.
- `controle3/tests/test_controle3_porteuses.py` : cases et graine de la mesure, valeur vraie au budget, cellule à une
  tâche jamais établie.
- Total : 323 tests de la simulation réussis, 1 échec attendu.

## 4. Empreintes

Le moteur change.
- `controle3.lancer --verifier` compare désormais le code au sixième passage (`controle3/resultats_v6/`, même graine que
  le cinquième, appariée).
- Le cinquième passage (`resultats_v5/`) reste lié au moteur du commit e300b0e.
- La partie R4 du cinquième passage (`passage5_r4/`) n'est pas refaite : elle n'appelle que le point 4 et l'étiquette
  (`classes.statut_configuration`, `decision.point4`, `decision.etiquette`), que cet amendement ne touche pas.
