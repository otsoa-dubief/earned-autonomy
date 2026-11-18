# Plan de l'article (PLAN_SUITE T13 ; accord d'Otsoa le 17/11/2026 sur Q2 et Q3)

**Titre (Q2, titre principal recommandé par la recherche « Titre pour un article préenregistré »)** : *Earned Autonomy for AI Agents: A Pre-registered Error-Budget Test of Per-Action-Type Delegation*. Graphie unique « Pre-registered » partout. Même titre sur arXiv et à l'atelier.

**Format (Q3)** : un seul document, 8 pages hors références et annexes, annexes complètes ; l'atelier ne demandera qu'un changement de gabarit.

## Le message en trois phrases (repris de `FORMULATION_VERDICT.md`)

1. No configuration reached the pre-registered level of evidence required for delegation (pre-registered verdict R4); only one of twelve had enough volume to be judged, and its error rate, 8.6% (lower bound 4.1%), is established above its 0.76% threshold, while the other eleven had too little volume to conclude either way.
2. The delegation gap is wide where it can be measured: 20 of 40 action types have an error rate established above their threshold, 13 show no observed error but too little volume, and none can be shown below.
3. The rule was not refuted but was hardly put to the test; earning autonomy under such budgets takes far more verified actions than current benchmarks provide.

## Budget de pages (corps : 8 pages)

| Section | Pages | Contenu |
|---|---|---|
| Abstract | 0,3 | phrase officielle du verdict, puis l'écart de délégation, puis ce que veut dire une « erreur » |
| 1 Introduction | 0,8 | le problème (que laisser faire seul à un agent ?), les trois contributions : la règle avec N déduit d'un budget, la mesure de l'écart, le protocole préenregistré avec relecture à l'aveugle |
| 2 Related work | 0,7 | contrôle qualité (Dodge, Lieberman), niveaux d'autonomie, budgets d'erreurs (CASE), autorité méritée (Zhang & Zhang), bancs d'agents, préenregistrement d'expériences avec agents (arXiv 2606.11217), statistique des évaluations |
| 3 The rule | 1,2 | types d'action et enjeux, paliers, N et la garantie conditionnelle (borne 1/(1 + N·d), deux facteurs 0,95 distincts), hypothèses |
| 4 Setup | 1,2 | bancs, modèles, contrôle par action, confirmation des alertes et relecture à l'aveugle, vagues et coût, jeux calibration et confirmation, tirage public, rejeu hors ligne |
| 5 Pre-registered analysis | 0,8 | critères, étiquettes R1 à R5, jugeabilité (n_eff × barre ≥ ln 2), dépassement établi à ρ = 1 sans correction de multiplicité, témoins |
| 6 Results | 1,6 | verdict et table de décision résumée ; écart de délégation (table 6 courte, figure de l'écart) ; ce que la règle a fait (paliers 2 et 3, charges) ; témoins (1 et 2 configurations Haiku, enjeu faible) ; alerte de résistance ; validité de l'instrument |
| 7 Discussion | 0,7 | ce que R4 veut dire et ne veut pas dire ; fragilité de la jugeabilité (ρ̂ 0,800 [0,660 ; 0,924]) ; le volume nécessaire ; les erreurs d'action ne sont pas des échecs de tâche (WorkBench) ; comparaison avec Zhang & Zhang et CASE |
| 8 Limitations | 0,7 | un seul chemin attendu ; client simulé qui dérive ; instrument de la banque ; exclusions pour message vide ; relecture de la vague 2 par Opus ; page de relecture simplifiée ; incidents (u26kr remplacé par cusv6, correctif en mémoire du rejeu final) |
| **Total** | **8,0** | |

## Ce qui part en annexe

- A. Écarts au préenregistrement, datés (tirés de `JOURNAL_CHANGEMENTS.md`), dont le correctif en mémoire (`article/morceaux/deviation_correctif_en.md`).
- B. Table des outils et des types d'action ; barres et N par environnement (table 1 du brouillon).
- C. Tables complètes : 5 (180 cases du budget), 6 (40 types), 6 bis (réserve entière, descriptive), 7 et 7 bis (charges, paliers), 9 (tests de résistance), G (garantie), 4 (symétrie), réussite des tâches.
- D. Analyses exploratoires, datées : tables X1 à X6 (`article/resultats/tables_exploratoires.md`).
- E. Instrument : alertes par motif, relectures à l'aveugle (13 sur 15 deux fois), retraits de tâches et opposition de l'auteur, audit des tâches sans alerte.
- F. Reproductibilité : empreintes, dépôts OSF (7ju3c, vycge, cusv6), tirage public, commandes exactes.

## Version française de contrôle du message

1. Aucune configuration n'a atteint le niveau de preuve fixé à l'avance pour qu'on lui délègue des actions (verdict R4) ; une seule sur douze avait assez de volume pour être jugée, et son taux d'erreurs, 8,6 % (borne basse 4,1 %), est établi au-dessus du seuil de 0,76 % ; les onze autres n'avaient pas assez de volume pour conclure.
2. L'écart de délégation est grand là où on peut le mesurer : 20 types d'actions sur 40 ont un taux établi au-dessus de leur seuil, 13 n'ont aucune erreur observée mais trop peu de volume, et aucun ne peut être prouvé en dessous.
3. La règle n'est pas réfutée, mais elle a peu été mise à l'épreuve ; mériter l'autonomie sous de tels budgets demande beaucoup plus d'actions vérifiées que les bancs actuels n'en offrent.
