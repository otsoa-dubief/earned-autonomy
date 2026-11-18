# Contrôle 1 · suites appliquées

5 novembre 2026, fin de journée. Rapport d'origine : `revues/2026-11-05_controle1_regle.md` (28 constats). Fait par un agent Claude, sur les consignes du coordinateur. Aucun commit : le diff est à relire.

**Fichiers modifiés**
- `REGLE.md` : ajouts seulement (0 ligne retirée au diff), en lectures datées et renvois en italique ;
- `PLAN_EXPERIENCE.md` : texte corrigé, chaque ajout étiqueté (section 0) ;
- `banc/relecture/fiches.py` et `banc/tests/test_relecture.py` (C11) ;
- ce compte rendu.

Rien d'ouvert sous `donnees/` ni dans les résultats publiés des bancs. `SUIVI.md`, `JOURNAL_CHANGEMENTS.md` et `banc/tirage/` : lus, pas modifiés. Aucun réseau, aucune clé.

**Tests** : 578 verts avant ; **596 verts après**, aucun échec. L'écart : 1 test ajouté ici, et 17 venus de deux commits faits en parallèle (ci-dessous).

**Commits arrivés pendant le travail.** Aucun ne touche les fichiers ci-dessus.
- 7013f70 (17 h 29) : second tour de relecture dans `banc/relecture/accord.py`, « décision B2 », avec 9 tests.
- 56bdb95 (17 h 31) : `banc/tirage/paires.py` et `banc/tirage/paires.json`, avec 8 tests. En conséquence, C8 décrit les paires comme écrites et à figer au gel, et non comme « code à écrire ».

**Étiquettes** : celles de la section 0 du plan. « Déduit » sert aux raisonnements qui ne tranchent rien (RF1, RF3, M3).

## Table des suites

Lignes au moment de la remise. PLAN = `PLAN_EXPERIENCE.md`.

| Constat | Ce qui a été fait | fichier:ligne | Étiquette |
|---|---|---|---|
| B1 | Trois classes par intervalle, au jeu de calibration. Oracle au palier 3 pour les seuls types « sous la barre » ; un type indéterminé ou au-dessus va au palier 2 s'il est réversible, au palier 1 sinon. Délégable : au moins un type mérité sous la barre ; R4 suit la même définition. « Ni au-dessous pour le retrait » est remplacé : un type indéterminé n'est pas délégué par l'oracle et ne compte pas comme devenu mauvais. | PLAN:479, 608, 94, 579, 247, 552, 646, 891, 690 | Découle |
| B2 | **Non touché**, comme demandé. Aucun passage modifié sur le second tour, la révision des motifs ou la moitié « relecture » de R5. | — | — |
| B3 | Holm remplacé par le max-T de Westfall et Young sur le même bootstrap : α = 5 %, unilatéral ; m = cellules où le témoin délègue (palier 3) et pas « sans objet » ; T*, c* au 95e centile du maximum, règle de dépassement. Précision datée sous la lecture de Q6. Test ajouté en 5.16. | PLAN:637-644, 57, 835, 680, 705 ; REGLE:267 | Tranché par Claude |
| B4 | 5.13 réécrit : une seule règle par quantité ; candidates (i), (ii), (iii) ; critère 93 % sur ρ et G donnés ; repli ; « fragile » défini par une seconde méthode ; jackknife et bêta-binomial descriptifs ; Clopper-Pearson sur n_eff (remplace « écritures supposées indépendantes ») ; 5.16, point 5, avec seuil. Notes dans la section 8. | PLAN:597-604, 612, 613-614, 615-619, 677, 703-704, 886-890 | Tranché par Claude |
| RF1 | Critère de retrait présenté comme une propriété vérifiée par construction et par 5.16, pas comme une voie de réfutation ; R1 ne porte plus que sur le budget ; version avec constat différé (retard10) rapportée. Renvoi sous la décision 5. | PLAN:56, 91, 80, 634, 561, 717 ; REGLE:288 | Déduit |
| RF2 | Le seuil de 0,95 devient la « couverture de l'instrument », sans justification par d ; d est déclaré non observable (5.8 réécrit). Lecture datée sous la définition de d. | PLAN:95 (seconde moitié de R5 seulement), 194, 496-500, 591, 629 ; REGLE:244 | Tranché par Claude |
| RF3 | En 1.4 : la borne de B-tout (budget × s ÷ q), ce que R1 et « confirmée » peuvent signifier et ce qu'ils ne peuvent pas signifier. Renvois en 1.5. | PLAN:74-80, 91, 96 | Déduit |
| C1 | q écrit exactement au point 9 : numérateur sans les plafonnées ; dénominateur avec, hors doutes et préparations ; secours d'E1 rapporté aux écritures (exemple 0,22 ÷ 0,60). Renvoi au point 8. Recalculé : 1/12 020 et 1/15 898 (aviation, fort), 1/697 (commerce, moyen). | REGLE:386, 364 ; PLAN:899 | Précision sans changement de valeurs |
| C2 | Lecture datée sous les trois épreuves : utilité remplacée par la décision 3 ; garantie mesurée sans seuil ; K abandonné, retrait à la première erreur constatée. Chaque élément a été vérifié dans le texte des décisions 3 et 5, et de la décision 7 pour l'enjeu faible. | REGLE:27-31 | Lecture datée |
| C3 | Spécification de B-tout (points 1 à 8), attente de 50 écritures et réglages du palier 2, sous la décision 7, avec le sha256 du plan d'E1. Valeurs vérifiées dans `config.py`, `config_e1.py` et `RegleUnTypeB`. Renvois sous les pièces 6 et 7. | REGLE:305-315, 129, 144 | Lecture datée |
| C4 | (a) Témoins « sans pondération » et « sans doute gratuit » non rejoués, écart déclaré ; (b) renvoi à Q12 ; (c) renvoi à Q3, avec un renvoi depuis la pièce 7. | REGLE:48, 276, 165, 145 ; PLAN:714, 715, 722 | (a) Découle du plan d'E1 |
| C5 | Les 9 renvois du tableau du rapport (lignes d'avant les ajouts : 10, 18, 41-44, 113-116, 118 et 124-127, 129, 198, 213, 255). | REGLE:11, 20, 55, 129, 132, 144, 149, 222, 238, 285 | Renvoi |
| C6 | Étiquette finale écrite dans l'ordre R5, R1, R4, R2, puis « confirmée » ; avec un ensemble délégable vide, le point 2 n'est pas jugé (R4). | PLAN:647-654, 646, 96 | Tranché par Claude |
| C7 | En 5.5, point 7 : quantités calibrées fixes ; le hasard apparié copie la règle sur la même répétition ; les deux plis de l'échange des rôles refont toute la procédure et sont moyennés à poids égaux. Renvoi en 5.13. | PLAN:427-430, 605 | Tranché par Claude |
| C8 | Paires retenues. 3.4 aligné sur `tirage_public.py` : champs précédés de leur longueur, strate dans le rang, règle des paires, lancement au plus tôt une heure après l'heure désignée, panne de réseau sans secours, signature du NIST vérifiable mais pas vérifiée, drand contrôlé par SHA-256(signature). Algorithme et fichier : écrits (56bdb95), à figer au gel. | PLAN:261-263, 267, 268, 348, 884 | Tranché par Claude |
| C9 | Arrondi à l'inférieur, au moins un passage par tâche et par modèle, facteur le plus grand au centième ; la règle fait partie du plan de jeu figé. | PLAN:189, 868, 346 ; REGLE:186 | Tranché par Claude |
| C10 | Nom de modèle changé : le lanceur s'arrête, les parties sous le nouveau nom sont exclues et déclarées, et l'on ne reprend que si l'ancien nom revient. | PLAN:197, 126, 343, 346, 736 | Tranché par Claude |
| C11 | `fiches.py` : la version de Claude est la version aveugle (ni modèle, ni partie, ni rang, ni tâche), avec un identifiant opaque ; la correspondance est dans `alertes.json`. Tests adaptés, plus un test ajouté. Plan : 4.3, 4.7, l. 184 reformulée, Q2. | fiches.py:95, 578, 629, 661, 677 ; test_relecture.py:119, 133, 188, 526, 541 ; PLAN:305, 347, 199, 793 | Tranché par Claude |
| C12 | « Avant le gel » au lieu de « avant la première vague » ; une tâche défectueuse trouvée par l'audit est retirée selon le même critère, déclarée et comptée dans les tests de symétrie. | PLAN:331, 349, 793 ; REGLE:361 | Découle |
| C13 | Section 7 dans l'ordre réel, chaque contrôle à sa place ; seconde relecture indépendante courte du plan figé et du manifeste, juste avant la relecture finale d'Otsoa et le gel. | PLAN:752-762, 4 | Tranché par Claude |
| M1 | « Données sensibles » lu comme les secrets du plafond 3. | REGLE:279 | Précision |
| M2 | Lecture datée en pièce 9 (énoncés et actions attendues permis, résultats d'agents jamais) ; l. 326 nuancée. | REGLE:183, 371 | Précision |
| M3 | Deux lignes « attendu, absent du pilote » (aviation réversible, messages internes de WorkBench ; absence vérifiée par comptage) et lecture nuancée. | PLAN:164, 171, 175 | Déduit |
| M4 | q et les barres figés en fractions exactes, avec l'empreinte de `table_outils.json`. | PLAN:364 ; REGLE:396 | Tranché par Claude |
| M5 | Ligne « ILL avec verdict » dans le tableau de 5.4, et note. | PLAN:402, 405 | Tranché par Claude |
| M6 | Règle « au gel, chaque statut passe à Décidé ou disparaît », avec la liste des statuts ouverts dans les deux fichiers. | PLAN:19 ; REGLE:413 | Découle |
| M7 | (a) « devenu mauvais » exige aussi « pas au-dessus chez X » ; (b) « jamais » = dans aucune des R0 répétitions ; (c) « plus » = intervalle tout au-dessus de 0 ; (d) variantes tirées dans le jeu d'origine, et épreuve impossible sans 3 variantes : le type reste au palier 1. | PLAN:551, 633, 645, 520 | Tranché par Claude |
| M8 | Un seul risque, 5 % unilatéral, pour le volume de certification et les classes ; garantie avec intervalle par grappes de tâches (Wilson retiré). | PLAN:580, 619, 620, 929 | Tranché par Claude |

## Détails ajoutés pour rendre les décisions calculables

Ces détails ne figuraient pas dans les consignes. Tous sont étiquetés « Tranché par Claude » et contestables jusqu'au gel.
- **B4.**
  - m̄ est pondéré par la taille (Σ m² ÷ Σ m), et x_eff = x × n_eff ÷ n.
  - ρ̂ est estimé par analyse de variance, par configuration. À défaut, on prend celui de l'environnement ; sinon, ρ̂ = 1.
  - Pour le jackknife-t, la relance multiplie par 4 le nombre d'ordres.
  - La simulation de couverture utilise des grappes bêta-binomiales, avec au moins 1 000 jeux par case.
- **B3.** Une cellule dont l'écart type bootstrap est nul sort du maximum.
- **M8.** Les classes passent à des bornes unilatérales à 95 % : à zéro erreur, environ 3 ÷ n_eff au lieu de 3,7 ÷ n. L'autre choix, garder le bilatéral et refaire l'annexe A2 à 2,5 %, aurait changé les chiffres de 1.4.
- **C10.** J'ai lu « exclues de l'analyse de confirmation » comme « de l'analyse confirmatoire, calibration comme confirmation ». Une partie est exclue dès qu'un de ses appels a reçu le nouveau nom.
- **C11.**
  - L'identifiant d'alerte devient opaque : l'environnement, puis 12 caractères du SHA-256 de (tâche, partie, rang).
  - L'étiquette de la version de Claude est « relecture » : le mot « claude » déclencherait le garde-fou des noms de modèle.
  - Les identifiants du `decisions.csv` du rodage, à l'ancien format, ne correspondent plus. Ce rodage n'avait aucune mesure, et les fiches sont refaites.
  - Limite : un mot comme « Claude » ou « opus » dans les données d'une tâche est masqué des deux côtés. La différence champ par champ reste calculée avant le masquage.
- **M7 (d).** L'épreuve est impossible dès que les replis donnent moins de 3 variantes, et pas seulement aucune.
- Le code du moteur (max-T, méthodes d'intervalle, n_eff, couche bootstrap) n'est pas écrit : seules les spécifications le sont.

## Ce qui reste pour Otsoa

1. **B2, à écrire à part.**
   - Le commit 7013f70 l'a codé dans `accord.py` : 26 accords sur 30 au second tour ; la décision d'Otsoa l'emporte sur les cas relus ; un désaccord persistant fait garder l'étiquette la moins favorable de deux calculs.
   - Les textes n'ont pas suivi : `REGLE.md` (point 7, « Si le désaccord persiste, les motifs sont revus »), le plan (R5, première moitié ; 4.4 ; 5.14, point 0).
   - Avec B2 tel que codé, un désaccord persistant ne semble plus mener à R5. Le point 0 et R5 sont donc à réécrire avec B2 ; l'ordre de C6 (R5 d'abord) renvoie au point 0 et suivra.
2. **RF1 change le rôle d'un critère.** Le critère de retrait de la décision 5 n'est plus une voie de réfutation : R1 ne porte que sur le budget. L'amendement E1-a, une décision d'Otsoa, l'avait rendu éliminatoire dans E1. C'est fait comme demandé, mais à porter à sa connaissance.
3. **R5 modifié en partie**, malgré la consigne de ne pas le toucher : seule la moitié « 0,95 » a changé, pour RF2. La moitié « relecture » est mot pour mot.
4. **M1** : la lecture « données sensibles = secrets du plafond 3 » était douteuse pour le relecteur lui-même. Otsoa peut la contester ; elle est sans effet sur le rejeu.
5. **M6, statuts à clore au gel**, par décision d'Otsoa.
   - `REGLE.md` : pièce 7 « nombre à confirmer par la simulation » ; pièce 8 « hypothèse, à tester » ; section du 5 novembre, point 5 « révisables par Otsoa » et point 7 « appliqué sauf objection d'Otsoa ».
   - Plan : les huit « Proposé » listés en section 0.
6. **Choix « Tranché par Claude » contestables jusqu'au gel** (section 0) : B3, B4, C6 à C11, C13, M4, M5, M7, M8, et les détails ci-dessus.


## B2, traité ensuite (05/11, fin d'après-midi)

Décision d'Otsoa (QCM, après explication et une correction de Claude : les verdicts bruts seuls aidaient B-tout à battre les règles simples) : second tour sur les deux tours cumulés, au moins 26 accords sur 30 ; décision d'Otsoa prioritaire sur les cas relus ; désaccord persistant : aucun motif réécrit après le gel, verdict calculé deux fois (décisions retenues, verdicts bruts), étiquette la moins favorable. Écrit dans `REGLE.md` (point 7), `PLAN_EXPERIENCE.md` (1.5, R5 ; 4.4 ; 5.14, points 0 et 5) ; code dans `banc/relecture/accord.py` (commit 7013f70). Reste : exclusion des cas déjà tirés au second tour (`tirage_aveugle.py`).
