# Cinquième passage, partie R4 : méthode (écrite avant le lancement)

Claude, 07/11/2026, après la décision d'Otsoa du 07/11 (règle recommandée retenue, `PLAN_EXPERIENCE.md`, 1.5 et 5.16,
point 10). Moteur au commit 6c02d69. Données synthétiques seulement, aucun appel payant (`env -u ANTHROPIC_API_KEY`).
Ce fichier est figé avant le lancement : `passage5_r4.py --lancer` refuse de partir sans lui et inscrit son empreinte
sha256 dans `meta.json`. Aucun tirage de ce passage n'a été fait avant son écriture.

## 1. Question

La règle retenue a été choisie après avoir vu les tirages du quatrième passage (correction « type jugeable », options_r4,
section 7). Ce passage la confirme sur de nouveaux tirages :
1. R4 à tort au plus 5 % à la barre et au plus 1 % à 0,5 fois la barre, dans la pire case (cibles d'Otsoa) ;
2. puissance à 2, 3, 5 et 10 fois la barre, et répartition des motifs de « preuves insuffisantes » ;
3. le motif « aucun type jugeable » sort quand les volumes manquent (monde à volumes réduits) ;
4. la borne basse à ρ = 1 garde son risque quand les tâches ont des tailles inégales et des erreurs ;
5. monotonie : quand les agents empirent, la part de R4 ne baisse pas et la part délégable ne monte pas.

## 2. Ce que fournit le moteur (aucune réimplémentation de la règle)

Un tirage : `mondes.generer` (mondes mixtes : `options_r4.generer`, déjà validé), `preuves.preparer(…, "confirmes")`,
jeux de calibration `suites.jeu_configuration`, classes `classes.classes_tous_environnements`, statut de chaque
configuration `classes.statut_configuration(classes, classes.rho_propre(jeu))`, point 4 `decision.point4`, étiquette
`decision.etiquette` avec les points 0 à 2 tenus. Issues : délégable (point 4 tenu), R4, « preuves insuffisantes » et
son motif. C'est le calcul de `pipeline.familles_analyse` (test `test_pipeline_erreurs_dispersees_et_nettes_r4`).

## 3. Cases

Mécanismes et mondes comme au quatrième passage (`controle3.harnais.monde_delegabilite`) : tous les types au même
multiple de la barre ; témoins tenus, ou en défaut (écriture réversible de Sonnet et Opus dans WorkBench à 10 fois la
barre).
1. **Grille A (R4 à tort), 1 000 tirages par case** : bêta, ρ ∈ {0 ; 0,3 ; 0,7 ; 0,9 ; 1} × multiples {0 ; 0,2 ; 0,5 ; 1}
   × témoins (40 cases) ; logit-normal, ρ ∈ {0,3 ; 0,7 ; 0,9} × {0 ; 0,5 ; 1} × témoins (18) ; ρ hétérogène × {0 ; 0,5 ;
   1} × témoins (6). 64 cases.
2. **Grille B (puissance), 300 tirages par case** : bêta × {2 ; 3 ; 5 ; 10} (40 cases) ; logit-normal × {2 ; 3 ; 5}
   (18) ; ρ hétérogène × {2 ; 3} (4). 62 cases.
3. **Cases critiques, 10 000 tirages chacune** : à la barre, bêta, ρ ∈ {0,7 ; 0,9 ; 1} × témoins (6) ; à la barre,
   logit-normal, ρ = 0,9, témoins tenus (1) ; à 0,5 fois la barre, bêta, ρ = 1 × témoins (2) ; M1-bis (Haiku dans
   WorkBench à la barre, écriture réversible à ρ = 1, le reste à 10 fois et ρ = 0) ; M2 (les trois configurations du
   commerce à 0,2 fois la barre, le reste à 5 fois, ρ = 0,3). 11 cases.
4. **Cases critiques ajoutées (deuxième étape)** : toute case de la grille A au multiple 1 dont la part mesurée de R4
   dépasse 3 %, et toute case aux multiples 0 à 0,5 dont la part dépasse 0,5 %, devient une case critique de 10 000
   tirages, avec ses propres graines, si elle ne l'est pas déjà. Raison (tranché par Claude le 07/11) : avec 300
   tirages, une case dont le vrai taux est 4 % dépasse 5 % dans 15 à 22 % des cas ; le jugement se fait sur les cases
   critiques.
5. **Monde à volumes réduits, 300 tirages par case** : comme la grille bêta, ρ = 0,3, témoins tenus, multiples {0,2 ;
   1 ; 5}, en ne gardant qu'une fraction f ∈ {1/10 ; 1/3} des tâches de calibration de chaque environnement, tirées au
   hasard sans remise (graine propre au tirage). 6 cases. Attendu à f = 1/10 : aucun type jugeable, donc « preuves
   insuffisantes », motif « aucun type jugeable », dans toutes les répétitions.

R4 à tort : R4 dans une case au plus à la barre (grilles, cases critiques, M1-bis) ; dans M2, R4 alors qu'une
configuration du commerce est jugeable.

## 4. Tâches de tailles inégales (question 4)

Hors générateur, qui donne à un type des tâches presque toutes de même taille. Pour un profil de tailles (m_1 … m_T),
erreurs groupées au maximum (ρ = 1 : chaque tâche échoue en entier, indépendamment, avec la probabilité p), x = Σ m_i
B_i ; classe du type par `classes.classer(x, n, barre, n_eff=…, n_eff_preuve=(Σm)² ÷ Σm²)` ; dépassement établi par
`classes.depassement_etabli`. Part des 200 000 répétitions où le dépassement est établi, à p = barre et à p = 0,5 ×
barre, pour les barres faibles de WorkBench (947/125020) et du commerce (88/3325) et la barre moyenne de WorkBench
(947/549100). Profils (graine propre) : 300 tâches de 7 écritures ; 300 tâches de taille géométrique de moyenne 3 ;
300 tâches de taille de Pareto (indice 1,5, minimum 1, tronquée à 200) ; 100 tâches d'une écriture et une de 100 ;
100 tâches d'une écriture et trois de 100. Le dépassement établi à p = barre doit rester au plus 5 % (borne haute de
Wilson) ; un profil qui dépasse est rapporté comme une limite, avec la part à p = 0,5 × barre.

## 5. Graines

Graine maîtresse 2026110701, distincte de celle du quatrième passage (2026110503) : aucun tirage n'est repris. Graine
d'un tirage : `SeedSequence([2026110701, indice de case, répétition])` ; indices : grille A 1 000 + rang, grille B
2 000 + rang, cases critiques 3 000 + rang, cases critiques ajoutées 4 000 + rang de la case de grille A, volumes réduits
5 000 + rang, tailles inégales 6 000 + rang du profil. Sous-échantillon des volumes réduits : `SeedSequence([2026110701,
indice, répétition, 1])`.

## 6. Validation, avant tout résultat

1. **Recoupement avec l'étude du 06/11** : 6 cases de `options_r4` refaites avec leurs graines (grille, 5 fois ρ = 0
   tenus et en défaut, 1 fois ρ = 1 tenus, 3 fois ρ = 0,3 tenus, 2 fois ρ = 0,7 tenus, 1 fois ρ = 0,9 en défaut ;
   1 800 tirages). Le nombre de R4 doit égaler C-ρ1-J et le nombre de R4 plus motif « établi sous ρ̂ propre » doit
   égaler C-hybride-J (`options_r4/diagnostic_types.csv`). Un écart arrête le script avant tout tirage du passage.
2. **Cohérence interne, à chaque tirage** : R4 seulement si aucune configuration n'est délégable et si chaque
   configuration jugeable est établie ; « établie » implique « établie sous ρ̂ propre » et ρ* = 1 ; le motif suit
   l'ordre écrit (`decision.point4`). Un écart arrête le script.
3. **Auto-tests** (`--tester`) : sous-échantillon des volumes réduits (taille, sans remise, reproductible) ; part
   établie des tailles inégales comparée au calcul exact sur de petits profils ; déclenchement de la deuxième étape.

## 7. Cibles et jugement (fixés avant le lancement)

Cibles d'Otsoa : R4 à tort au plus 5 % à la barre et au plus 1 % à 0,5 fois la barre, dans la pire case.
1. Cases critiques, ajoutées comprises : borne haute de Wilson à 95 % de la part de R4 à tort au plus 5 % dans chaque
   case à la barre (et dans M1-bis et M2), au plus 1 % dans chaque case aux multiples 0 à 0,5.
2. Grille A : sert à trouver les cases à mesurer (deuxième étape) ; une case de grille n'est pas jugée sur ses 1 000
   tirages si elle est devenue critique.
3. La règle tient les cibles si 1 passe. Sinon, le résultat est rapporté tel quel à Otsoa, avec la case fautive ;
   aucune règle n'est changée dans ce passage.
4. Monotonie (rapportée) : dans chaque série (mécanisme, ρ, témoins), une baisse de la part de R4, ou une hausse de la
   part délégable, de plus de deux erreurs types quand le multiple augmente.
5. Puissance, motifs, volumes réduits et tailles inégales : rapportés avec leurs intervalles de Wilson, sans seuil (sauf
   4).

## 8. Exécution et sorties

12 processus (spawn), `PYTHONDONTWRITEBYTECODE=1`. Ordre : validation 1, grille A, deuxième étape, cases critiques,
grille B, volumes réduits, tailles inégales. Sorties dans ce dossier : `passage5_r4.py`, `meta.json` (paramètres,
graines, empreintes du moteur, durées, validations, cases ajoutées), `tirages.csv` (un tirage par ligne, non versionné,
empreinte dans `tirages.csv.sha256`), `passage5_r4.csv` (par case : parts, intervalles de Wilson, motifs),
`tailles_inegales.csv`, `passage5_r4.md` (résumé).
