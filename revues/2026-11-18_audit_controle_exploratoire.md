# Audit de contrôle — seconde passe exploratoire (commit 7d73e42)

Date : 18/11/2026. Auditeur indépendant. Périmètre lu : diff du commit (atelier.md, brouillon.md, sources_chiffres.csv, les trois scripts), `article/resultats/tables_exploratoires.md`, `article/latex/main.pdf` (pdftotext), `outils/analyses_exploratoires.py` (lo_rho1, confirmee), `simulation/rejeu/classes.py` (bornes_cp) et `entrees.py` (jointure), code seulement. Aucune donnée ouverte (experience/, donnees/, pilote/, data/, notes/ non lus). Aucun script relancé sur les données.

**Verdict : publiable après corrections — aucun chiffre faux par rapport aux tableaux, mais la phrase du résumé (« Most of its errors come from one plot-date discrepancy ») n'est pas soutenue par X8 (36 sur 79, soit 46 %), et la robustesse « 4,7 %, still established » repose sur un filtre de texte strict dont la marge (14 erreurs sur 19) n'est pas dite.**

## Ce qui est vérifié

- Chiffres du texte contre X7 / X8 (atelier.md, brouillon.md, PDF) : 55 sur 79 (79 − 24) ; 177 et 144 ; 40 sur 46 ; 43 erreurs ; 4,7 % (43/914 = 4,70 %) ; 1,6 % (1,58 %) ; 24 erreurs ; 0,51 % ; 64–82 % (63,9 ; 78,9 ; 81,8, WorkBench) ; 47–77 % (min 47,1 banking/haiku ; max 76,5 airline/haiku ; vrai dans les 12 configurations). Tous concordent.
- X7 : colonnes « failed » = épisodes − réussis pour les lignes contrôlées (WorkBench/haiku 112, airline/haiku 294, banking/haiku 527). Colonne « of which successful » identique à X3.
- Borne basse : `analyses_exploratoires_2_dates.py` importe `lo_rho1` de la première passe (même fonction, même m̄ lu dans la même ligne d'`ecart.csv`). Recalcul indépendant (Clopper-Pearson, risque 0,05, m̄ ≈ 11,2 déduit de 4,14 %) : 79 → 4,14 % ; 43 → 1,575 % ; 143 → 9,457 % ; 24 → 0,509 %. Les quatre bornes de X8 sont cohérentes entre elles.
- Seuil de bascule recalculé : dépassement établi à partir de x = 30 (x = 29 donne 0,757 % contre une barre de 0,7575 %, à la limite). Cohérent avec le « 63 % » de X2 (79 × 0,37 = 29,2).
- PDF : résumé, résultats en bref, 6.7, discussion, limites, tableaux X7 et X8, limite 32 présents et identiques au markdown. « 32 limitations » dans atelier.md, body.tex, PDF, controle_fr.md ; la liste du brouillon a bien 32 entrées.
- Marquage exploratoire : présent en 6.7, dans le paragraphe du brouillon, dans X7/X8 et dans la limite 32.

## Ce qui n'est PAS vérifié

- Les valeurs des CSV sources (55, 36, 64, 177, 144, 40/46) : données interdites, non relues. Je n'ai vérifié que texte = tableau, et la logique du code.
- La qualité de classement des deux filtres de texte sur les justifications réelles.

## Constats

### À corriger

**C1. Résumé : « Most of its errors come from one plot-date discrepancy » n'est pas soutenu.**
- Endroit : brouillon.md l. 19 (Abstract), `arxiv/abstract.txt`, `latex/abstract.tex`, PDF p. 1.
- Preuve : X8. Le scénario « end on 30 Nov only lifted » passe de 79 à 43 : 36 erreurs de date seule, soit 46 % des 79. Ce qui est majoritaire, c'est « plots » (55 sur 79, 70 %), pas « l'écart de date ». Le nombre d'erreurs confirmées « fin au 30 » au sens large dans le type jugé n'est dans aucun tableau.
- Correction : « Most of its errors are plots (55 of 79); 36 differ from the expected plot only by a one-day end date, a case reviewers decided both ways; lifting it throughout leaves 4.7%, still established. » Même défaut, plus léger, dans la limite du § 8 de l'atelier (« a recurring plot discrepancy that carries most errors of the judged type ») : écrire « plots, which carry most errors of the judged type, were reviewed inconsistently ».

**C2. La robustesse « 43 erreurs, still established » dépend d'un filtre strict ; la marge n'est pas dite.**
- Endroit : `analyses_exploratoires_2_dates.py`, `end_only` ; phrases « Deciding it consistently leaves the excess established » (6.7, brouillon l. 300, limite 32, résumé).
- Preuve : `end_only` exige la chaîne exacte « time_max 2023-11-30 au lieu de 2023-11-29 » dans un texte libre de relecteur, sans « time_min ». Toute autre tournure (« jour courant », « aujourd'hui », « 30/11 ») n'est pas levée. Il reste 19 erreurs de graphiques confirmées (55 − 36). Le dépassement tombe dès x ≤ 29 : il suffit que 14 de ces 19 soient en réalité le même écart de date, formulé autrement. Le biais va dans le sens de la conclusion (« still established »).
- Correction : (a) dire la marge dans le texte : « still established; it would not be if 14 of the 19 other confirmed plot errors were the same case ». (b) Ajouter à X8 le scénario « toutes les confirmées "end on 30" au sens large levées » (filtre `end_on_30`, celui des 144). (c) Idéalement, classer sur les arguments de l'action (time_max attendu contre obtenu), pas sur le texte de la justification.

**C3. Deux définitions et deux périmètres mêlés dans une même phrase.**
- Endroit : 6.7 atelier, brouillon l. 300, limite 32 : « plots carry 55 of the 79 errors of the judged type […] decided that case both ways (177 such alerts lifted, 144 confirmed; 40 of 46 plot tasks) ».
- Preuve (code) : 177 / 144 / 40 sur 46 portent sur toutes les alertes `create_plot`, deux vagues, trois modèles, deux moitiés, sans filtre type ni tâches retirées, avec le filtre large `end_on_30` (« 11-30 », « jour courant », « aujourd »). 55 / 79 / 43 portent sur Haiku, calibration, ECR, avec le filtre strict. Dans le type jugé, les chiffres comparables sont 36 confirmées (strict) et 64 levées (large) (143 − 79). Le lecteur lit « 144 confirmées » à côté de « 79 erreurs » : incohérent en apparence. « that case » pour 144 est trop fort : le filtre large retient toute justification qui mentionne « 11-30 », y compris un écart de date accompagné d'un autre défaut (144 large contre 36 strict dans un sous-ensemble).
- Correction : « across all models and both halves, 177 alerts mentioning the 30 November end date were lifted and 144 confirmed (text match on the reviewers' justifications); in the judged type, 36 confirmed errors differ by the end date only and 64 such alerts were lifted ». Préciser le périmètre dans la légende de X8.

**C4. « 40 of 46 plot tasks decided both ways » ne prouve pas que le même cas a été tranché dans les deux sens.**
- Endroit : mêmes phrases ; `by_task[a["tache"]].add(d)`.
- Preuve : le décompte par tâche prend toutes les alertes de graphiques, tous motifs, tous modèles et les deux vagues. Une tâche avec une alerte de date levée et une autre erreur confirmée compte « both ways ». « 46 » = tâches ayant au moins une alerte de graphique décidée, pas toutes les tâches à graphique.
- Correction : restreindre le décompte aux alertes `end_on_30` (ou `end_only`) et recalculer ; sinon écrire « 40 of the 46 tasks with a reviewed plot alert had plot alerts both lifted and confirmed (any reason) ».

**C5. Le script des dates ne lit pas les décisions comme le moteur.**
- Endroit : `analyses_exploratoires_2_dates.py`, boucle « Judged type ».
- Preuve : (1) il lit `decisions.csv` brut (`just[...]`, dernière ligne gagnante par identifiant) et non `ent.jointure.decisions` (décisions retenues : arbitrages d'Otsoa, alerte sans décision = confirmée, motif a avec opposition = confirmée) ; (2) il n'exclut pas les tâches retirées (la première passe le fait : `retirees_a`, ligne 207 ; la seconde aussi dans `analyses_exploratoires_2.py`) ; (3) il ne teste pas `a.verdict`. Si un de ces cas existe parmi les graphiques Haiku/calibration, « 55 » et donc « 24 » ne sont pas « les erreurs de graphiques comptées par le moteur », et le scénario « all confirmed » peut compter deux fois une alerte levée motif a déjà comptée. Aucun contrôle interne ne le détecte (le script ne recalcule pas x = 79 par outil).
- Correction : utiliser la fonction `confirmed` de la seconde passe et l'exclusion des tâches retirées ; ajouter une assertion : somme des erreurs confirmées par outil du type jugé = 79. Si l'assertion passe sans changer 55, le constat se ferme.

**C6. Discussion : « An agent can pass a task after a wrong state-changing action » est trop fort au vu de X8.**
- Endroit : atelier § 7, brouillon l. 300, PDF.
- Preuve : sur WorkBench, les erreurs confirmées sont en majorité des graphiques (55 sur 79 dans le type jugé), dont l'écart de date a été jugé tantôt erreur, tantôt non. Le 64–82 % est donc en partie fait d'actions dont le caractère « faux » est justement contesté quelques lignes plus loin ; et le banc qui les note « réussies » peut avoir raison. La même passe affirme les deux choses sans les relier.
- Correction : « An agent can pass a task after an action the review confirmed as an error; on WorkBench many of these are the plot-date case above, so the share is an upper reading. » Garder « which outcome-only scoring does not see » seulement avec cette réserve.

### Remarques

**R1. « 47 % to 77 % of failed episodes have no confirmed action error »** : juste, mais ambigu. Ces échecs comprennent les omissions (écriture attendue non faite), les erreurs de lecture ou de réponse, et les alertes levées. Une demi-phrase suffit : « (omissions and non-write failures are not action errors here) ». Sinon le lecteur conclut que la règle « manque » la moitié des échecs.

**R2. « mostly because the agent ended the plot on 30 November »** : 36 sur 55 (65 %) au filtre strict. Juste, mais donner le chiffre (« 36 of them ») évite C1.

**R3. « the 8.6 % rate is less solid than its interval suggests »** : force correcte. Cohérent avec X2 (63 %), R4 et la limite 9. Pas de contradiction avec 8,6 % / 4,1 % : ces valeurs restent celles du moteur, et le texte le dit.

**R4. Étiquette R4** : non contredite. Dans le scénario « no plot error », le type n'est plus établi au-dessus mais n'est pas délégable non plus ; « no configuration reached the level of evidence » tient. En revanche « is established above the 0.76% threshold » (résumé) devient conditionnel à la relecture des graphiques ; la phrase suivante le dit, une fois C1 corrigé.

**R5. Compte des limites** : `article/correspondance_atelier.md` l. 17 dit encore « 31 » (deux fois). À passer à 32.

**R6. En-tête de `tables_exploratoires.md`** : « All analyses below were run […] by `outils/analyses_exploratoires.py` » est faux pour X7 et X8 (scripts `_2` et `_2_dates`). Corriger dans `tables_exploratoires.py`.

**R7. X7 répète X3** (colonne « of which successful »). Sans conséquence ; le dire dans la légende ou renvoyer à X3.

**R8. Ordre dans le brouillon** : le paragraphe du 18/11 précède celui du 17/11. Inverser.

**R9. `article/FORMULATION_VERDICT.md`** : la formulation de référence du résumé n'a pas la phrase sur les graphiques. À décider : soit elle reste la formulation du seul verdict, soit l'aligner.

**R10. `sources_chiffres.csv`** : les 7 lignes ajoutées correspondent aux tableaux. Manquent le « 36 » et le « 64 » si C3 est suivi.
