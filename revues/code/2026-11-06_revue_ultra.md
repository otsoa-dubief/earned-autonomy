# Revue de code « ultra » (dans le cloud), lots moteur et banc

6 novembre 2026. Revue `/code-review ultra` de Claude Code, lancée par Otsoa sur deux copies propres et facturée sur
son compte. Les constats ont ensuite été vérifiés et corrigés dans le dépôt de recherche par Claude : le lot moteur
directement, le lot banc par une copie de Claude dont le diff a été relu.

**Objet.** La revue « ultra » relit au plus 8 000 lignes modifiées (doc de Claude Code lue le 06/11). Le code a donc
été découpé en deux lots par `revues/code/preparer_copie_revue.py --lot …`, à partir du commit 31e49d3. Dans chaque
copie, `main` porte tout le reste comme contexte, et la branche `revue` ajoute seulement le lot :
- moteur de rejeu (`simulation/rejeu/*.py`, hors tests) et gel (`gel/`) : 26 fichiers, 7 138 lignes ;
- cœur du banc (lanceur, relecture, tirage, verdicts, typage et leurs petits modules) : 20 fichiers, 7 436 lignes.

Les scripts du pilote et le harnais du contrôle 3 (environ 3 100 lignes) n'ont pas été relus : ils ne calculent pas
le verdict.

**Méthode.** La revue « ultra » fait reproduire chacun de ses constats par ses propres agents. Chaque constat a été
revérifié dans le code du dépôt. Chaque correction retenue a un test, écrit d'abord et en échec avant la
correction. À la relecture du lot banc, deux corrections ont été resserrées :
- un PID noté puis réutilisé par un autre processus n'est plus pris pour une partie ;
- une ligne d'usage mal formée ne fait plus lever une seconde exception dans le chemin d'erreur.

**Respect des interdits.**
- Aucun appel réel, et la clé n'a jamais été lue.
- Rien n'a été lu sous `donnees/`, ni dans les résultats publiés des bancs, ni dans les sorties brutes du pilote.
- Les copies ne contenaient ni `donnees/`, ni notes, ni historique.

## Lot moteur : 9 constats (1 normal, 8 mineurs)

| # | Constat | Verdict | Correction | Test |
|---|---|---|---|---|
| 1 | `gel/manifeste.py` : `verifier` ne voit pas un fichier ajouté dans `externe/workbench-run/` | confirmé | `verifier` lit aussi les fichiers externes. Même défaut, étendu : il signale aussi un fichier non suivi par git dans le périmètre (un module importable) | `gel/tests/test_manifeste.py::test_verifier_trouve_les_fichiers_ajoutes_hors_git` |
| 2 | `bout_en_bout.py` : sans `--sortie`, `--experience` et `--essai-a-blanc` écrivent dans `sorties_pilote/`, suivi par git et figé | confirmé | `--sortie` est obligatoire pour ces deux modes. Pour l'expérience, une sortie dans `banc/`, `simulation/` ou `gel/` est refusée | `test_rejeu_revue_ultra.py`, 3 tests |
| 3 | `--R0`, `--B` et `--K` remplacent les valeurs figées sans contrôle (`--B 0`) | confirmé | Entiers positifs exigés. L'expérience réelle refuse toute valeur différente de `config_rejeu.json` ; les essais peuvent réduire | 2 tests |
| 4 | Un essai à blanc lancé après `--tirer-g0` prend le vrai G0 | confirmé, et même défaut pour `--pilote` | Graine de développement pour tout ce qui n'est pas l'expérience réelle | 3 tests |
| 5 | `ecrire_config()` remet G0 à null : G0 peut être tirée deux fois | confirmé | Une G0 déjà tirée est gardée | 1 test |
| 6 | RESULTATS.md cite `resultats_couverture/`, alors que la méthode vient de `resultats_couverture_charge/` | confirmé | Le texte cite la source de la méthode, lue dans `meta.json` | 1 test |
| 7 | `facteur_relance` et `relances` restent, alors que la relance ne s'applique plus (Q13 ; CHOIX_PHASE3, contradiction 2) | confirmé | Retirés de la configuration, des réglages, de l'analyse et de `meta.json`. `config_rejeu.json` est réécrit, avec une ligne en moins | 1 test et une assertion sur `meta.json` |
| 8 | `empreinte_code()` et `verifier()` copiés trois fois | **non retenu** | Chaque script de couverture vérifie l'empreinte de son propre code contre celle de son lancement unique. Les factoriser changerait cette empreinte et casserait la preuve d'origine de `choix.json`, qui fixe la méthode d'intervalle du moteur | — |
| 9 | La fusion des tâches retirées est copiée à deux endroits | retenu : les deux copies sont identiques | `entrees.fusionner_retirees` | tests existants des entrées |

## Lot banc : 10 constats (6 normaux, 4 mineurs)

| # | Constat | Verdict | Correction | Test (`banc/tests/test_revue_ultra_banc.py`) |
|---|---|---|---|---|
| 1 | Lanceur : le motif d'arrêt nomme la partie et le modèle WorkBench (constat E) | confirmé | `arret_visible` le masque au journal visible, à la console et dans le rapport de vague. Le motif complet reste au journal complet | `test_u1`, 2 tests |
| 2 | Une exception de l'exécuteur après le jeu compte 0 $ et la partie est rejouée en `-t2` | confirmé | Le coût est lu dans l'usage, ou déclaré inconnu s'il ne se lit pas. Le lanceur s'arrête (choix 45 a) | `test_u2`, 3 tests |
| 3 | `--reprendre` ne vérifie pas les enfants encore vivants | confirmé | Le PID de chaque enfant est noté, avec sa commande. La reprise est refusée tant qu'un enfant noté vit ; un PID réutilisé est reconnu (choix 45 b) | `test_u3`, 4 tests |
| 4 | Tirage public : `verifier` ne lie pas l'impulsion brute à l'impulsion désignée | confirmé | `ecarts_impulsion` contrôle, pour le NIST, l'heure, l'adresse, la fenêtre et la première minute ; pour drand, le tour et le lien signature → hasard. `--en-ligne` refait la sélection dans l'archive publique | `test_u4`, 5 tests |
| 5 | Verdicts : la tâche est retrouvée par son texte, et l'identifiant est deviné en cas de doublon | partiel : aucun texte partagé parmi les 690 tâches au 06/11 | L'ambiguïté est refusée au lieu d'un identifiant deviné | `test_u5`, 2 tests |
| 6 | Fiches : l'`action_id` (`<tâche>_<n>`) des actions attendues nomme la tâche (C11) | confirmé | Retiré des deux versions de la fiche | `test_u6` |
| 7 | Fiches et audit : les avertissements affichent le rang (C11) | confirmé | Les avertissements sont sans rang. L'audit désigne l'écriture par sa marque (« ÉCRITURE n° k ») | `test_u7`, 2 tests |
| 8 | Décisions : un en-tête avec espaces passe, puis chaque ligne est lue vide | confirmé | Les lignes sont lues sous les noms bruts des colonnes | `test_u8` |
| 9 | Audit et fiches : logique de trace et de rang dupliquée | doublon sans divergence | rien | — |
| 10 | `lire_usage` duplique `cout_v2.lire_usage_jsonl` | doublon sans divergence (mêmes lectures, mêmes erreurs) | rien | — |

## Ce qui reste visible ou ouvert

- **Identifiants WorkBench à l'opérateur.** Ils restent affichés dans trois cas, comme décidé à la revue du lanceur : la liste des coûts inconnus à chiffrer, certains refus de reprise, et les parties exclues pour nom de modèle changé. L'opérateur en a besoin pour taper `--cout-retenu`.
- **Enfants non notés.** Une fenêtre de quelques millisecondes reste entre le lancement d'un enfant et l'écriture de son PID.
- **Tirage hors ligne.** La signature des balises n'est pas vérifiée. Le protocole des lecteurs passe par `verifier --en-ligne` (PLAN 3.4, point 6, aligné).
- **Sorties agrégées du pilote.** Celles que suit git (`simulation/rejeu/sorties_pilote/`, `essai_a_blanc_pilote/`) datent d'avant ces corrections : `meta.json` y porte encore `facteur_relance`, et RESULTATS.md l'ancien chemin. Elles sont à refaire avec le moteur final, avant le gel.

**Tests après corrections** : simulation 282 réussis et 1 échec attendu ; banc 697 ; gel 7.
