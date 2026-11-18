# Options de R4 : méthode du cinquième passage (écrite avant le lancement)

Claude, 06/11/2026, à la demande d'Otsoa. Moteur au commit 49bbc3d ; `controle3.lancer --verifier` : empreintes conformes, vérifié avant l'écriture de ce fichier. Données synthétiques seulement, aucun appel payant (`env -u ANTHROPIC_API_KEY`). Ce fichier est figé avant le lancement : `options_r4.py --lancer` refuse de partir sans lui et inscrit son empreinte sha256 dans `meta.json`. Aucun calcul de règle n'a été fait avant son écriture.

## 1. Question

Cinq règles pour l'étiquette R4, comparées sur l'étude de délégabilité seule (point 4, comme `controle3.harnais.delegabilite`) : pour chaque case, part des tirages qui donnent « délégable », R4 et « preuves insuffisantes ».

## 2. Ce que fournit le moteur (aucune réimplémentation)

Un tirage : `controle3.mondes.generer`, `rejeu.preuves.preparer(…, "confirmes")`, jeux de calibration `rejeu.suites.jeu_configuration`, classes `rejeu.classes.classes_tous_environnements` (ρ̂ selon N3). Par type : n, x, n_eff à ρ̂, n_eff_preuve à ρ = 1, `lo` (borne basse unilatérale de Clopper-Pearson à 95 % sur n_eff_preuve), `lo_hyp` (même borne sur n_eff à ρ̂), `estime_sous`, `jugeable`. Une configuration est délégable si un de ses types est `estime_sous`, jugeable si un de ses types est `jugeable` (comme `rejeu.pipeline`). L'étiquette de A sort de `rejeu.decision.point4` puis `decision.etiquette`, points 0 à 2 tenus.

## 3. Règles

« Établi au-dessus » (un type) : borne basse unilatérale de Clopper-Pearson à 95 % (`classes.bornes_cp`, sur x_eff = x·n_eff/n et n_eff) strictement au-dessus de la barre. Un type sans erreur n'est jamais établi.

- **A** : étiquette du moteur. Issues : délégable, R4, « volume insuffisant » (aucun type jugeable), compté dans la colonne « preuves insuffisantes ».
- **C-ρ1** : R4 si A donne R4 et si chaque configuration qui a un type jugeable a au moins un type établi au-dessus à ρ = 1 (champ `lo` du moteur, n_eff = (Σm)²/Σm²). Sinon, rien n'étant délégable : preuves insuffisantes.
- **C-ρ̂** : idem avec `lo_hyp`, n_eff au ρ̂ que le moteur attribue au type (valeur propre ou commune, plancher 0,3).
- **C-hybride** : idem ; une configuration d'au moins 10 erreurs dans au moins 5 tâches (`classes.erreurs_et_taches`) dont le ρ̂ propre est calculable (`classes.rho_fc_strates(classes.strates_par_type([jeu]))`) prend ρ = max(0,3 ; ρ̂ propre) ; toutes les autres, ρ = 1. n_eff = `classes.taille_effective(m, ρ)`. Lecture retenue : l'éligibilité seule compte, pas la condition du moteur « plus grand que la valeur commune ».
- **C-porte** : C-ρ1 limité aux configurations détectables. Puissance d'un type : probabilité, sous groupement total (chaque tâche porteuse ratée en entier, indépendamment, avec la probabilité p = min(0,5 ; 5 × barre), 0,5 étant le plafond du générateur), que sa borne basse à ρ = 1 dépasse la barre. Elle est calculée exactement sur les tailles des tâches porteuses du type (loi de Σ m_i B_i), donc sur les seuls comptes de tâches, avant les erreurs. Une configuration est détectable si la probabilité qu'au moins un de ses types soit établi, 1 − Π(1 − P_type), est au moins 0,80 (types indépendants, comme dans le générateur). R4 si A donne R4, si au moins une configuration est détectable et jugeable, et si chacune de ces configurations a un type établi au-dessus à ρ = 1. Sinon : preuves insuffisantes.

« R4 à tort » : R4 alors qu'une configuration jugeable est fiable (tous ses types au plus à la barre). Dans les cases au plus à la barre et dans M1 et M1-bis, tout R4 est à tort.

## 4. Mondes et cases (mécanisme bêta partout)

1. **Grille** : ρ ∈ {0 ; 0,3 ; 0,7 ; 0,9 ; 1} × multiples {0,2 ; 0,5 ; 1 ; 2 ; 3 ; 5 ; 10} × témoins tenus ou en défaut (`harnais.monde_delegabilite`), 300 tirages par case, 70 cases.
2. **Cases critiques, 10 000 tirages chacune** : à la barre, ρ = 0,9 et 1, témoins tenus et en défaut (4 cases) ; à 0,5 × la barre, ρ = 1, témoins tenus et en défaut (2 cases ; la demande ne précise pas les témoins, les deux sont tirés) ; M1 ; M1-bis.
3. **Mondes mixtes** (surcharges propres au script, `mondes.py` intact) :
   - **M1** (demandé, 10 000 tirages) : écriture réversible de Haiku dans WorkBench à 1 × la barre et ρ = 1 ; tous les autres couples (configuration, type) à 0,2 × la barre et ρ = 0.
   - **M1-bis** (ajouté par Claude, 10 000 tirages) : Haiku dans WorkBench à 1 × la barre sur tous ses types (écriture réversible à ρ = 1, autres types à ρ = 0) ; toutes les autres configurations à 10 × la barre et ρ = 0. Raison, par déduction avant tout calcul : dans M1, Sonnet et Opus dans WorkBench sont jugeables et à 0,2 × la barre ; toutes les variantes de C exigent un dépassement établi dans chaque configuration jugeable, que ces configurations fiables n'atteignent presque jamais. M1 peut donc ne pas montrer l'échec de C-ρ̂ qu'il vise. M1-bis réalise le pire cas du rapport : une configuration pile à la barre, les autres très au-dessus, avec des erreurs dispersées qui tirent la valeur commune de ρ̂ vers le plancher et diluent le ρ̂ propre de Haiku quand il en a un.
   - **M2** (demandé, 2 000 tirages) : les trois configurations du commerce à 0,2 × la barre, toutes les autres à 5 ×, ρ = 0,3 partout. « Petite configuration » lue comme l'environnement commerce, qui a peu de tâches porteuses. Tout R4 avec une configuration du commerce jugeable est à tort : c'est le trou attendu de la porte.
   - **M3** (demandé, 2 000 tirages) : tous les types à 5 × la barre, ρ = 0, témoins tenus. C'est aussi la case (5 ; 0 ; tenus) de la grille, tirée ici avec d'autres graines : contrôle croisé.
   - Surcharge de ρ : sous-classe de `mondes.Monde` dont le taux porte son ρ ; pendant la seule génération de M1 et M1-bis, `mondes.taux_par_tache` est remplacé par une enveloppe qui lit ce ρ et appelle la fonction d'origine. Les autres mondes passent par le générateur tel quel.

## 5. Graines

Graine d'un tirage : `SeedSequence([2026110503, 1000 + indice de case, répétition])`, comme `harnais.delegabilite` ; 2026110503 est la graine maîtresse du quatrième passage.
- Grille aux multiples 0,2 ; 0,5 ; 1 ; 2 ; 5 ; 10 : indice de la case dans `lancer.cases_deleg()`, répétitions 0 à 299. Ce sont les tirages de `resultats_v4/delegabilite.jsonl`, donc ceux du chiffrage exploratoire : la grille refait ce chiffrage avec les bornes exactes du moteur, elle n'en est pas une réplication indépendante.
- Cases critiques à la barre : indices 50 002 à 50 005, répétitions 0 à 9 999 : les tirages de `resultats_v4/critiques.jsonl`, qui n'ont servi qu'à la certification à tort, jamais à R4.
- Cases nouvelles : indice 60 000 + j. j = 0 à 9 : grille au multiple 3 (témoins tenus puis en défaut, ρ croissant) ; 10 et 11 : 0,5 × la barre, ρ = 1, tenus puis en défaut ; 12 : M1 ; 13 : M1-bis ; 14 : M2 ; 15 : M3.

## 6. Validation, avant tout résultat

1. Grille, 60 cases du quatrième passage (18 000 tirages) : liste des types estimés sous la barre, liste des configurations délégables et détail des types faibles (`faibles`) identiques à `resultats_v4/delegabilite.jsonl` (empreinte sha256 vérifiée).
2. Grille au multiple 3 (3 000 tirages) : mêmes comparaisons avec `harnais.delegabilite` appelé sur la même graine (le moteur refait le tirage).
3. Cases critiques à la barre (40 000 tirages) : `faibles` identique à `resultats_v4/critiques.jsonl`.
4. Cohérence interne, à chaque tirage : (n, x) recomptés égaux à ceux du moteur ; borne de C-hybride égale à `lo` quand ρ = 1 et à `lo_hyp` quand ρ égale le ρ̂ du moteur ; R4 de A égal à « rien de délégable et un type jugeable ».
5. Mondes mixtes : là où ρ vrai vaut 1, aucune tâche porteuse de l'écriture réversible de Haiku dans WorkBench n'a d'erreurs partielles ; taux observés ÷ barre proches des multiples voulus (écriture réversible de Haiku et de Sonnet dans WorkBench, de Haiku dans le commerce).
6. Auto-tests de la porte (`--tester`) : puissance exacte comparée à une simulation directe sur des profils de tâches tirés au hasard, et égale à la loi binomiale quand les tâches ont la même taille.

Un écart aux points 1 à 4 arrête le script avant tout tableau ; il est rapporté et expliqué.

## 7. Cibles, fixées avant le lancement, et jugement

Cibles d'Otsoa : R4 à tort au plus 5 % à la barre et au plus 1 % à 0,5 × la barre, dans la pire case. Jugement, règle par règle :
1. Cases critiques (10 000 tirages) : la borne haute de Wilson à 95 % de la part de R4 est au plus 5 % dans chacune des cases demandées à la barre (4 cases de grille et M1), au plus 1 % dans chacune des deux cases à 0,5 ×.
2. Grille (300 tirages) : la part mesurée de R4 est au plus 5 % dans chacune des dix cases au multiple 1, au plus 1 % (3 tirages sur 300) dans chacune des dix cases à 0,5 ×. Avec 300 tirages, la borne haute ne descend pas sous 1,26 % : la grille sert seulement à vérifier que la pire case n'est pas ailleurs.
3. Une règle tient une cible si 1 et 2 passent. M1-bis est jugé avec le critère 1 « à la barre » et rapporté à part : une règle qui tient les cibles sur les cases demandées mais pas sur M1-bis est signalée comme telle, sans changer le verdict sur les cases demandées.

Puissance : part de R4 à 3 et 5 × la barre, par ρ et témoins (grille) et dans M3, sans seuil. Intervalles de Wilson à 95 % sur chaque part.

## 8. Exécution et sorties

12 processus (spawn), `PYTHONDONTWRITEBYTECODE=1`. Ordre : grille (validations 1 et 2, arrêt en cas d'écart), puis cases critiques et mondes mixtes (validations 3 à 5). Sorties dans ce dossier : `options_r4.py`, `meta.json` (paramètres, graines, empreintes, durées, validation), `tirages.csv` (un tirage par ligne), `options_r4.csv` (par case et par règle : parts et intervalles de Wilson), `options_r4.md` (résumé).
