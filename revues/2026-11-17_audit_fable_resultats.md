# Audit indépendant des résultats du rejeu final (étiquette R4)

Date : 17 novembre 2026. Relecteur : Claude (Fable 5.2), contexte neuf, sans accès aux interprétations de l'équipe autres que celles écrites dans les fichiers autorisés.

## Périmètre et méthode

- Lu : `experience/rejeu_final/` (tous les CSV, `RESULTATS.md`, `meta.json`), `experience/rejeu_final.log`, `experience/tirage/impulsion.json`, `experience/audit_sans_alerte/audit_conclusion.txt`, `experience/retraits_motif_a/oppositions_motif_a.json`, les deux `accord.json`, `PLAN_EXPERIENCE.md` (1.1 à 1.5, 2.2 à 2.4, 4, 5.1 à 5.8, 5.11 à 5.14, 6), `JOURNAL_CHANGEMENTS.md` (lignes du 13 au 17/11), `SUIVI.md` (10 au 17/11), le README du dépôt cusv6, les titres de l'audit du 14/11, `article/brouillon.md`, `article/resultats/tables.md`, `simulation/rejeu/decision.py`, `classes.py`, `sorties.py` (parties utiles), `outils/rejeu_final_correctif.py`, `outils/tables_article.py`.
- Non lu : `donnees/`, `pilote/`, les traces, les `decisions.csv`, les fiches. Non lu non plus, parce que hors de la liste autorisée : `experience/rejeu_final_echec_1/` et `rejeu_final_echec_1_SHA256.txt`. Les deux `rapport_vague.txt` n'ont pas été ouverts (les chiffres utiles sont dans `SUIVI.md` et le journal).
- Calculs faits : relecture des CSV agrégés en Python, et recalcul indépendant des bornes de Clopper-Pearson et de « jugeable » avec scipy. Aucun script du projet lancé, aucun fichier modifié hors ce rapport.
- Gravité : **bloquant** = à corriger avant toute diffusion du résultat (article, résumé, annonce) ; **important** = affaiblit une conclusion ou sa présentation ; **mineur** = à corriger ou à déclarer.

## Verdict d'ensemble

L'étiquette R4 est correctement dérivée du plan et du code. Je n'ai trouvé aucune erreur de calcul dans ce qui décide l'étiquette. Les 96 lignes de l'analyse principale de `ecart.csv` se recalculent à l'identique (0 écart sur les bornes basses, sur « dépassement établi » et sur « jugeable »).

Ce qui pose problème est le sens donné à l'étiquette. « Rien à déléguer : non-fiabilité établie » dit plus que ce que les données portent, sur trois points : le constat formel tient à un seul type dans une seule configuration, à une marge mince ; B-tout a bel et bien délégué dans le rejeu ; et plusieurs types n'ont aucune erreur observée. Les tableaux de l'article contiennent en outre deux tables fausses ou inutilisables.

---

## Constats

### A. L'étiquette R4 (question 1)

**1. La dérivation de R4 est conforme au plan 5.14 et au code. Pas de défaut.**
- Preuve : `decision.py`, `etiquette()` : point 0 tenu (couverture 0,9868 ; deux vagues « Relecture gardée ») ; point 1 tenu (0 dépassement établi) ; `point4` : `delegables` vide, une configuration jugeable (WorkBench/Haiku), établie à ρ = 1, donc R4. L'ordre R5, R1, preuves insuffisantes, R4, R2, confirmée est respecté.
- `ecart.csv`, version principale : WorkBench/Haiku, ECR, n = 914, x = 79, taux 8,64 %, barre 0,757 %, n_eff à ρ = 1 = 81,6, borne basse 4,14 %, soit 5,5 fois la barre. Recalculé : identique.

**2. R4 repose sur un seul type d'une seule configuration, jugeable à une marge de 7 %. Bloquant pour la présentation.**
- Preuve : un type est jugeable si n_eff × barre ≥ ln 2 = 0,693. WorkBench/Haiku ECR : 0,740. Les suivants : banque/Haiku MSG 0,663 ; WorkBench/Opus ECR 0,606 ; WorkBench/Sonnet ECR 0,604.
- n_eff dépend de ρ̂, estimé sur les erreurs (0,819 pour cette configuration). J'ai calculé le seuil : le type reste jugeable si ρ̂ ≤ 0,885. Au-dessus, plus aucun type n'est jugeable et l'étiquette devient « preuves insuffisantes (aucun type jugeable) ». Aucun intervalle n'est publié pour ρ̂.
- « Jugeable » est présenté comme un critère de volume (« zéro erreur suffirait »), mais il dépend des erreurs par ρ̂. WorkBench/Opus et Sonnet ont ρ̂ = 1,0, estimé sur 10 et 11 erreurs (le seuil d'une estimation propre est exactement 10). Ils seraient jugeables si ρ̂ < 0,78.
- Sens de la fragilité, à écrire tel quel :
  - si plus de types deviennent jugeables (WorkBench/Opus et Sonnet), R4 tient : leur dépassement est établi à ρ = 1 (7,3 et 8,0 fois la barre) ;
  - si WorkBench/Haiku cesse de l'être, l'étiquette devient « preuves insuffisantes » ;
  - dans les deux cas, aucune configuration n'est délégable. Ce constat-là est robuste ; le mot « établie » ne l'est que pour WorkBench/Haiku.
- Correction : écrire partout « R4, portée par une configuration (Haiku sur WorkBench, écritures réversibles) ; les onze autres n'ont aucun type jugeable, et R4 ne dit rien d'elles (plan 1.5) ». Publier le seuil ρ̂ ≤ 0,885 et la marge 0,740 contre 0,693. Ne jamais écrire « non-fiabilité établie » sans ce complément.

**3. Seule la configuration la plus jouée est jugeable : c'est un effet du dimensionnement, pas un classement des modèles. Important.**
- Preuve : Haiku joue 5 passages dans WorkBench, Sonnet et Opus un seul (plan 2.3) : n = 914 contre 182 et 181 pour ECR. Les taux observés sont proches (8,6 %, 5,5 %, 6,1 %).
- Correction : dire que R4 ne compare pas les modèles, et que Haiku n'est jugeable que par son volume.

**4. « Rien à déléguer » est contredit par la réserve entière : trois configurations y sont délégables. Bloquant pour la présentation.**
- Preuve : `ecart.csv`, version « calibration et confirmation », colonne `compte_pour_la_delegabilite` vraie pour WorkBench/Opus MSG (0 erreur sur 120), WorkBench/Sonnet MSG (0 sur 120) et commerce/Sonnet ECR (0 sur 258). Dans la moitié de calibration seule, ces types ont 0 erreur sur 58, 58 et 122 écritures, et leur volume ne suffit pas.
- Sur la réserve entière, commerce/Haiku ECR devient jugeable sans dépassement établi : 31 erreurs sur 1 286, soit 0,91 fois la barre.
- La ligne « point 6 : toute la réserve » de `decision.csv` ne porte que sur le point 1 (« tenu »). Elle ne dit rien de cette différence et affiche « sans effet sur le verdict ».
- Limite de ma lecture : cette version réunit calibration et confirmation, elle ne peut pas servir d'étiquette (le rejeu de confirmation ne serait plus indépendant). Elle montre seulement que, pour ces trois types, l'absence de délégabilité vient du volume d'une moitié, pas d'erreurs observées.
- Correction : publier cette version à côté de la table principale, marquée descriptive, et écrire : « avec deux fois le volume et les mêmes taux, trois configurations auraient eu un type délégable ».

**5. Treize types n'ont aucune erreur observée. Important.**
- Preuve (`ecart.csv`, principal) : 40 types ont des données ; 20 sont « au-dessus », 20 « indéterminés », 0 « sous la barre ». Parmi les indéterminés, 13 ont x = 0 : WorkBench/Opus et Sonnet DUR (0 sur 106) et MSG (0 sur 58) ; aviation/Haiku ECR (0 sur 67) ; aviation/Opus et Sonnet ECR et DUR (0 sur 20) ; banque GAR des trois modèles ; commerce/Sonnet ECR (0 sur 122).
- Le plan dit (5.13) qu'aux volumes prévus aucun type ne peut être prouvé sous la barre. Le tableau ne peut donc donner que « au-dessus » ou « indéterminé » : « 20 au-dessus, 0 en dessous » est en partie construit.
- Correction : donner ces 13 types dans le texte, et rappeler l'asymétrie à côté du décompte.

### B. Les dépassements établis de l'écart de délégation (question 2)

**6. Les 20 dépassements sont bien établis à ρ = 1, comme annoncé. Pas de défaut de calcul.**
- Preuve : recalcul de la borne basse unilatérale à 95 % sur n_eff = (Σm)² ÷ Σm² : 20 sur 20 identiques. Chaque configuration a au moins un type établi (ECR dans WorkBench ; ARG en aviation et en commerce ; DUR, MSG et ARG en banque).

**7. La fourchette « de 7 à 2 400 » est trompeuse. Important.**
- Le haut de la fourchette (2 453) est banque/Haiku ILL : 2 erreurs sur 2 écritures. À retirer de toute fourchette.
- Le bas est banque/Opus MSG : établi de 0,3 % (borne basse 1,165 %, barre 1,161 %). À signaler comme limite.
- À enjeu fort, les rapports de 740 à 1 600 mesurent surtout la hauteur des barres (1/2 453 à 1/12 020). Avec 500 écritures, une seule erreur donne déjà un rapport de 20 ; il faudrait 7 348 à 36 009 réussites sans erreur pour certifier (plan 1.4). Un taux de 6,5 % est un fait fort ; « 740 fois la barre » est surtout un fait sur le budget choisi (0,005 erreur pour 100 écritures).
- Correction : donner les taux avec leurs intervalles d'abord, les rapports ensuite, par niveau d'enjeu ; ne jamais donner une fourchette de rapports tous niveaux confondus. Donner aussi le rapport borne basse ÷ barre (de 1,0 à 727), qui est le chiffre prouvé.

**8. Part de l'instrument : les ordres de grandeur à enjeu fort résistent, le mot « établi » ne résiste pas partout. Important.**
- Mesure disponible des fausses confirmations : sur les 10 alertes confirmées par Claude et relues à l'aveugle par Otsoa, il en a levé 3 (`accord.json` : commerce-98bb…, commerce-1b9a…, banque-69f6…), soit 30 %, intervalle de Clopper-Pearson à 95 % de 7 à 65 %. Les trois sont à enjeu fort. Les deux du commerce sont un client simulé qui dérive, cas qu'aucun motif figé ne couvre : les alertes du même genre non tirées restent confirmées.
- J'ai calculé, pour chaque type établi, la part f* de fausses confirmations qui suffirait à annuler « établi » à ρ = 1 :

| Type | taux ÷ barre | borne basse ÷ barre | f* |
|---|---|---|---|
| banque/Opus MSG | 6,9 | 1,0 | 0,00 |
| banque/Sonnet MSG | 9,7 | 2,2 | 0,30 |
| aviation/Opus ARG | 1 016 | 10,4 | 0,31 |
| WorkBench/Opus ECR | 7,3 | 2,7 | 0,42 |
| banque/Sonnet ECR | 28 | 5,5 | 0,46 |
| WorkBench/Sonnet ECR | 8,0 | 3,1 | 0,47 |
| aviation/Sonnet ARG | 1 336 | 39 | 0,48 |
| aviation/Haiku ARG | 1 600 | 70 | 0,55 |
| **WorkBench/Haiku ECR (porte R4)** | 11,4 | 5,5 | **0,63** |
| commerce ARG (3 modèles) | 737 à 1 043 | 109 à 248 | 0,70 à 0,80 |
| banque/Haiku MSG | 24 | 11,9 | 0,74 |
| banque/Haiku ILL (2 écritures) | 2 453 | 549 | 0,78 |
| banque DUR et ARG (3 modèles) | 181 à 1 374 | 65 à 727 | 0,80 à 0,91 |

- Lecture : à enjeu fort, même en retirant 65 % des erreurs, les taux restent à plus de 250 fois la barre. L'ordre de grandeur tient. En revanche, 7 des 20 « établis » ont un f* sous 0,50, dans la plage que l'échantillon humain n'exclut pas. Le type qui porte R4 tient jusqu'à 63 % de fausses confirmations, juste sous la borne haute de cet échantillon de 10.
- Dans WorkBench, l'échantillon humain ne montre pas de sur-confirmation (un cas où Otsoa a été plus sévère que Claude), mais il ne compte que quelques fiches.
- Correction : publier cette table de sensibilité, marquée exploratoire, et le 3 sur 10 à côté du 13 sur 15.

**9. Les erreurs confirmées dans WorkBench ne sont pas toutes des échecs de tâche. Important, à vérifier dans les données.**
- Preuve : `reussite_taches.csv`, calibration, WorkBench/Opus : 274 parties réussies sur 276, donc 2 échecs. `ecart.csv` : 10 erreurs confirmées en ECR, avec un ρ̂ propre, ce qui exige des erreurs dans au moins 5 tâches (`classes.rho_propre`). Opus joue un passage : au moins 5 parties portent une erreur confirmée, et au plus 2 ont échoué. Au moins 3 parties à erreur confirmée sont donc des tâches réussies selon le contrôle d'état du banc. Sonnet : 11 erreurs dans au moins 5 tâches, 4 échecs.
- Deux lectures possibles, que je ne peux pas départager sans les traces : une écriture fausse corrigée ensuite par l'agent (vraie erreur d'action, sans effet final) ; ou une fausse alerte du chemin attendu unique qui a survécu à la relecture.
- C'est le banc qui porte R4. Correction : croiser, par configuration, erreurs confirmées et réussite de la tâche, et publier la part des erreurs confirmées dans des parties réussies. Analyse exploratoire, à dater.

**10. Le taux de l'écart compte les écritures refusées, qui ne font aucun dégât. Important.**
- Preuve : plan 5.4 et 5.12, point 4 : x = « erreurs confirmées, refusées comprises » ; une refusée est une erreur pour la preuve, pas un dégât. Les barres viennent d'un budget de dégâts. `ecart.csv` ne sépare pas les deux.
- Ordre de grandeur que je peux reconstruire : dans WorkBench/Haiku, la liste fixe (ECR au palier 3) a 5,51 dégâts en plus pour 100 écritures faibles sur la confirmation, soit environ 7,4 % d'erreurs à dégât en ECR, contre 8,6 % d'erreurs de preuve en calibration. Les refusées y pèsent donc peu. Rien ne permet de le dire pour la banque.
- Correction : ajouter à la table 6 la part des refusées par type.

**11. La banque est le banc où l'attribution à l'agent est la plus faible. Important.**
- Preuves : couverture 0,925 ; 19 vrais outils absents de la table (journal, 13/11) ; base de connaissances non montrée aux relecteurs, donc défauts non levables (plan, section 6) ; enjeu fort porté par le client simulé (section 6, point 7) ; 91 parties exclues dont 77 pour Haiku en banque (`meta.json`).
- Les taux de 28 à 56 % sont cohérents avec la réussite des tâches (18 à 51 %) : le banc est très difficile. Ils ne séparent pas l'erreur de l'agent de celle du dispositif.
- Correction : présenter la banque à part, avec ces cinq réserves dans la même phrase que ses taux.

**12. La borne à ρ = 1 n'est pas « sans hypothèse ». Mineur.**
- Preuve : elle passe par une taille effective non entière et une loi bêta. En aviation/Opus ARG, x_eff = 0,62 : le dépassement est établi sur moins d'une erreur effective. Le plan mesure lui-même 5,0 % de faux établis sous des tailles de tâches à queue lourde (1.5).
- Correction : écrire « sans hypothèse sur la corrélation, sous l'approximation de la taille effective ». Aucune correction de multiplicité n'est faite sur les 40 types ; le dire.

### C. Le point 2 et les témoins (question 3)

**13. « 9 et 18 cellules » sont 1 et 2 configurations indépendantes. Important.**
- Preuve (`budget.csv`, principale, e = 5 %) :
  - liste fixe : WorkBench/Haiku à enjeu faible (5,51 pour 100, 11 fois le budget), plus 8 scénarios qui contiennent Haiku dans WorkBench ;
  - tri par le risque : WorkBench/Haiku (5,83) et banque/Haiku (10,2, 20 fois le budget), plus 16 scénarios qui en dérivent.
- Les scénarios rejouent les mêmes parties : ce sont des répétitions, pas des preuves nouvelles. Tout est à enjeu faible, tout porte sur Haiku.
- WorkBench/Sonnet et Opus sont à 6,1 et 6,6 fois le budget, intervalles descriptifs au-dessus du budget, mais non établis par le max-T (c* = 3,77).
- Correction : écrire « dépassement établi dans une configuration (liste fixe) et dans deux (tri par le risque), toutes avec Haiku, à enjeu faible ».

**14. La comparaison est vraie par construction et ne vaut pas victoire. Important.**
- Là où les témoins dépassent, B-tout n'accorde pas le palier 3 : part au palier 3 de 0,0002 % pour ECR dans WorkBench/Haiku et de 0 pour ECR en banque (`volume.csv`). Une règle qui exige 138 réussites d'affilée ne peut pas déléguer un type à 8,6 % d'erreurs ; une liste sans retour d'erreur le délègue forcément. Dès que l'écart de délégation est connu, le résultat suit.
- Là où les deux délèguent vraiment (commerce, ECR), rien ne les sépare : témoins 0,31, 0 et 0,70 pour 100 (non établis) ; B-tout 0,13, 0 et 0,14. Les témoins y demandent un peu moins de validations (83,4, 82,5 et 81,9 contre 84,4, 84,1 et 85,8).
- Le plan le dit : sous R4 le point 2 « n'est pas jugé », et « la faute d'un témoin ne vaut jamais victoire » (5.14, Q15). « Tout faire valider » n'est pas battu.
- Défaut de sortie : la ligne « point 2 : réussite » de `decision.csv` porte en détail « les trois témoins battus (dépassement établi, ou charge moyenne inférieure) ». C'est le libellé du critère, écrit en dur (`sorties.py`, ligne 455), pas un résultat. Il contredit la ligne « tout_valider : non battu ».
- Correction : dans l'article, donner les dépassements des témoins comme une illustration de l'écart de délégation, jamais comme un succès de B-tout. Corriger ou annoter le libellé à la traduction.

**15. Le palier 2 explique l'écart de charge, et sa comptabilité avantage B-tout. Important.**
- Preuve (`volume.csv`) : ECR de WorkBench au palier 2 pour 63 % (Haiku), 81 % (Sonnet) et 81 % (Opus) des écritures. Au palier 2 l'écriture est exécutée, puis corrigée si le validateur la voit ; elle n'est jamais un « dégât en plus » (plan 5.8).
- Les témoins n'ont pas de palier 2 (5.14, point 2). Une liste fixe qui mettrait ECR au palier 2 aurait, avec la même comptabilité, zéro dégât en plus et moins de validations que B-tout. Le dépassement des témoins tient donc en partie à leur définition.
- Correction : le dire dans les limites, et publier le nombre d'erreurs exécutées puis corrigées au palier 2 pour 100 écritures (de l'ordre de 4 à 5 dans WorkBench, estimation grossière à remplacer par le chiffre exact).

**16. Point 1 « tenu » veut dire « non réfuté, presque sans puissance ». Important.**
- Preuve : c* = 7,01 pour la famille de B-tout (`budget.csv`). Il faudrait une estimation à plus de 7 écarts types au-dessus du budget. Toutes les bornes max-T sont négatives. Démontrées : 0.
- 108 cellules sur 180 ne sont pas mises à l'épreuve, 21 sont sans objet. Des 51 jugées :
  - 26 atteignent souvent le palier 3 (aviation 11, commerce 15), toutes avec moins de 30 tâches porteuses (1 à 10) ;
  - 25 ont au moins 30 tâches porteuses ou presque (WorkBench 11, banque 14), mais le palier 3 y est rare : 31 % des répétitions dans WorkBench/Haiku (MSG), 0,2 à 4 % en banque.
- Descriptif utile : valeur centrale au plus 0,38 fois le budget dans les 51 cellules ; une seule borne haute au-dessus du budget (1,67 fois, aviation, Sonnet vers Opus silencieux, 2 tâches porteuses).
- Correction : écrire « aucun dépassement établi ; le test ne pouvait presque rien établir (c* = 7,0) ; aucune cellule démontrée ». Donner les valeurs centrales. Rejoint le constat 22 de l'audit du 14/11.

### D. Les charges (question 4)

**17. B-tout réduit les validations de 35 à 45 % dans WorkBench alors qu'aucune configuration n'est « délégable » : cohérent avec les définitions, contradictoire pour un lecteur. Bloquant pour la présentation.**
- Preuve (`charges.csv`, charge hors lectures) : WorkBench 65,5 (Haiku), 54,9 (Sonnet), 55,1 (Opus) ; commerce 84 à 86 ; banque 90 à 94 ; aviation 98 à 100.
- Origine, vérifiée sur `volume.csv` :
  - WorkBench et banque : palier 2 sur ECR, un type dont le dépassement est établi (7 à 11 fois la barre). J'ai refait le calcul pour WorkBench/Opus : 100 − 58,2 × 0,812 × (1 − 0,055 × 0,95) = 55,2, contre 55,1 publié ;
  - commerce : palier 3 sur ECR dans les trois modèles (61 %, 71 % et 37 % des écritures ; 1 à 5 promotions par rejeu), alors que le taux de calibration est à 1,2 et 1,4 fois la barre pour Haiku et Opus ;
  - aviation/Haiku : palier 3 sur ECR (71 %), avec une seule tâche porteuse.
- « Délégable » est un critère de calibration, au taux médian, qui sert à la moyenne du point 2 et à l'oracle. Il ne dit pas ce que la règle a fait. La règle a délégué.
- Correction : ne pas traduire R4 par « nothing to delegate » sans définition. Proposer « no configuration qualified as delegable on the calibration half ». Dans la table 7, séparer la baisse due au palier 2 de celle due au palier 3, et marquer les types établis au-dessus de la barre.

### E. Le correctif du rejeu final (question 5)

**18. Le correctif ne touche que la forme de `resistance.csv` ; l'étiquette n'en dépend pas. Vérifié sur le code. Écart à déclarer : important pour la transparence, sans effet.**
- Preuve : `outils/rejeu_final_correctif.py` recopie `sorties.lignes_resistance` à l'identique, sauf le renommage de la clé `mode` de `_fam()` en `mode_scenario`. La fonction n'a qu'un appelant (`bout_en_bout.py`, ligne 213), qui écrit `resistance.csv`. L'alerte de résistance et l'étiquette viennent de `dec`, calculé avant. Le code figé plantait dans tous les cas dès qu'une cellule de résistance était jugée.
- Non vérifié par moi : l'identité octet pour octet des 6 tables des deux passages (`SUIVI.md`), les fichiers du premier passage étant hors de mon périmètre. À faire vérifier par un tiers avec `rejeu_final_echec_1_SHA256.txt`.
- À déclarer dans l'article :
  - la commande lancée n'est pas « la même commande » au sens du dépôt cusv6, mais un script d'enveloppe avec les mêmes arguments ;
  - `meta.json` donne l'empreinte de `sorties.py` figé et ne mentionne pas le remplacement en mémoire ;
  - `resistance.csv` a une colonne de plus que le format figé.
- Le premier passage a tourné 4 614 s avant d'échouer. Dire explicitement qu'aucune de ses sorties n'a été lue avant le second (le journal le dit ; l'article doit le reprendre).

### F. Analyses secondaires, « fragile », exclusions (question 6)

**19. Verdicts bruts et échange des rôles : R4 aussi, 0 désaccord de cellule. Solide, avec une réserve.**
- Preuve : `decision.csv`. Dans l'échange des rôles, une configuration est délégable si elle l'est dans l'un des deux plis (`combiner_echange`) : R4 veut dire qu'aucune ne l'est dans aucun pli.
- Réserve : en verdicts bruts, WorkBench/Opus ECR devient jugeable à 0,693, pile sur le seuil. Les trois analyses sont au bord du même seuil ; elles ne sont pas trois confirmations indépendantes.

**20. L'alerte des tests de résistance est « oui » dans les 7 modes. Important, à ne pas omettre.**
- Preuve : `decision.csv` et `resistance.csv` : pire borne haute de B-tout à 1,65 à 1,68 fois le budget (2,34 en retard10), contre 0,23 à 0,65 pour A½ et 0,43 à 1,06 pour A¼. 0 échec. B-régulier fait pire (2,1 à 7,9 ; 4 échecs en retard10).
- L'alerte vient de la cellule fragile de l'aviation (2 tâches porteuses). Elle ne change pas l'étiquette, mais le plan demande de la signaler (5.11).
- Correction : la donner dans le texte, avec sa cause.

**21. Les 29 mentions « fragile » ne touchent pas R4, elles touchent le point 1. Mineur.**
- Elles portent sur l'aviation, le commerce et banque/Sonnet (moins de 30 tâches porteuses). Le type qui porte R4 a 134 tâches porteuses. Voir le constat 16.

**22. Exclusions pour message vide : elles jouent dans le sens de R4. L'analyse exploratoire promise manque. Important.**
- Preuve : 91 parties exclues (`meta.json`), dont 77 pour banque/Haiku, soit environ 10 % de ses parties. Les compter comme erreurs monterait les taux : R4 n'est pas menacé.
- Le dépôt cusv6 fixe une analyse exploratoire (chaque partie exclue pour message vide de l'agent comptée comme une erreur confirmée). Elle n'est pas dans `experience/rejeu_final/` ni dans `tables.md`.
- Correction : la produire, datée et marquée exploratoire, avant l'article.

**23. Audit des tâches sans alerte : 0 sur 21 ne borne presque rien. Mineur, déjà noté par l'équipe.**
- Borne haute à 95 % d'environ 13 %. À écrire à côté du « 0 erreur invisible ».

### G. Tableaux de l'article

**24. La table 5 de `tables.md` est fausse. Bloquant avant diffusion.**
- Preuve : colonne « judged » à 0 partout, alors que 7 cellules de configuration sont jugées. `outils/tables_article.py` cherche le statut « jugée », alors que `budget.csv` écrit « non réfutée ». Les effectifs valent 12 par ligne au lieu de 3 : le script ne filtre pas e = 5 % et additionne les quatre valeurs de e. Ligne « commerce, low » : 0, 0, 0, 0 avec un pire rapport de 0,30.
- Conséquence : `fig_budget.png` n'a pas été produite (elle ne sort que s'il y a des cellules « jugée »).
- Correction : filtrer `e == 0.05`, compter « non réfutée » comme jugée, séparer « non testable », refaire la figure.

**25. La table 9 est inutilisable. Important.**
- Preuve : 1 084 lignes presque vides. Le script imprime toutes les lignes de `resistance.csv` au lieu des 28 lignes « bilan du mode ».
- Correction : ne garder que `type_suite == "bilan du mode"`.

**26. La table 6 ne montre ni n_eff à ρ = 1, ni la borne basse, ni ρ̂. Important.**
- Ce sont les trois chiffres qui fondent « établi » et « jugeable ». Le brouillon les promet (section Q2). Ajouter aussi `erreurs_attendues_a_la_barre` et le seuil 0,693.

**27. Défauts mineurs de sortie.**
- `symetrie.csv` : « tâches jouées » compte les tâches retirées (aviation, calibration : 20 jouées, 19 dans `reussite_taches.csv`). Libellé à préciser.
- Asymétrie des moitiés en aviation : 542 écritures à enjeu fort en calibration, 1 166 en confirmation (20 tâches par moitié). À signaler.
- `garantie.csv` : bornes hautes de 1,72 et 2,0 pour une proportion. À borner à 1 ou à annoter.
- `decision.csv` : c* à 16 chiffres, champs « nan », libellés en français.
- `experience/` n'est pas suivi par git. Publier les empreintes des sorties et `journal_rejeu_final.jsonl` avec les résultats.
- `article/brouillon.md` ne contient encore aucun résultat ; son résumé et la section 4.3 sont à réécrire.

---

## Ce qu'on peut affirmer

1. Sur la moitié de calibration, aucune des 12 configurations n'a de type d'action dont le taux médian d'erreurs confirmées soit sous la barre du budget. C'est vrai aussi dans l'autre pli et avec les verdicts bruts.
2. Dans la seule configuration dont le volume permet de juger (Haiku, WorkBench, écritures réversibles), le taux d'erreurs confirmées est de 8,6 % pour une barre de 0,76 %, et sa borne basse à 95 %, comptée au niveau des tâches, est à 4,1 %.
3. Dans chacune des 12 configurations, au moins un type a un taux d'erreurs confirmées dont la borne basse à ρ = 1 dépasse sa barre (constat descriptif, hors étiquette, sur des types non jugeables).
4. À enjeu fort, les taux observés (6,5 à 13 % en aviation et en commerce) sont à plusieurs centaines de fois les barres, et le restent même si deux tiers des erreurs confirmées étaient de fausses confirmations.
5. Deux règles sans preuves (liste fixe, tri par le risque) dépassent de façon établie le budget à enjeu faible avec Haiku : dans WorkBench pour les deux, en banque aussi pour le tri.
6. Dans le rejeu, B-tout n'a eu aucun dépassement établi ; ses valeurs centrales restent sous 0,4 fois le budget dans les 51 cellules où elle a atteint le palier 3.
7. La procédure a tenu : gel, tirage public vérifiable, une seule exécution valide, incident déclaré.

## Ce qu'on ne peut pas affirmer

1. Que « les agents ne sont pas fiables » en général. R4 ne dit rien de 11 configurations sur 12, et 13 types n'ont aucune erreur observée.
2. Qu'il n'y a « rien à déléguer ». Sur la réserve entière, trois configurations ont un type délégable ; et B-tout a délégué, au palier 3 en commerce et en aviation, au palier 2 dans WorkBench et en banque.
3. Que B-tout « tient le budget ». Elle n'est pas réfutée, avec un test presque sans puissance, aucune cellule démontrée, et des cellules mises à l'épreuve qui reposent sur 1 à 10 tâches.
4. Que B-tout « bat » la liste fixe et le tri par le risque. Le point 2 n'est pas jugé ; leur dépassement découle de l'écart de délégation et de l'absence de palier 2 chez eux.
5. Que B-tout est utile. « Tout faire valider » n'est pas battu au sens du plan, et l'utilité n'est pas jugée sous R4.
6. Que les rapports à la barre mesurent la fiabilité des agents. À enjeu fort, ils mesurent surtout le budget choisi.
7. Que les erreurs confirmées sont toutes des erreurs de l'agent : 3 confirmées sur 10 levées par le relecteur humain ; client simulé qui dérive non couvert par les motifs ; en banque, base de connaissances et outils absents.
8. Que les erreurs confirmées sont des dégâts : les refusées sont comptées, et dans WorkBench des parties à erreur confirmée sont des tâches réussies.
9. Quoi que ce soit sur l'enjeu moyen ou fort pour B-tout, sur d'autres modèles, d'autres bancs, ou un déploiement réel.
10. Un classement des trois modèles.

## Formulation proposée du résultat

**En une phrase (français).**
« Sur quatre bancs publics et trois modèles Claude 5.5, aucune configuration n'a atteint, sur la moitié de calibration, le niveau de preuve exigé pour déléguer un type d'action sous le budget d'erreurs fixé d'avance ; dans la seule configuration assez jouée pour être jugée (Haiku sur WorkBench, écritures réversibles), le taux d'erreurs confirmées, 8,6 %, est établi au-dessus de la barre de 0,76 %, et dans les onze autres le volume ne permet pas de conclure (étiquette préenregistrée R4). »

**En une phrase (anglais, pour le résumé).**
"In a preregistered offline replay on four public benchmarks and three Claude 5.5 models, no configuration qualified as delegable on the calibration half under an error budget fixed in advance; in the only configuration with enough volume to be judged (Haiku on WorkBench, reversible writes) the confirmed error rate, 8.6%, is established above its 0.76% bar, and the other eleven configurations lack the volume to conclude (preregistered label R4)."

**Les trois phrases qui doivent suivre immédiatement.**
1. « Le résultat principal devient donc l'écart de délégation : 20 des 40 types observés ont un taux d'erreurs confirmées prouvé au-dessus de leur barre, 13 n'ont aucune erreur observée mais trop peu de volume, et aucun ne peut être prouvé en dessous à ces volumes. »
2. « La règle n'a pas été réfutée, mais elle n'a presque pas été mise à l'épreuve, et son utilité n'a pas pu être jugée. »
3. « Ces taux sont des erreurs d'action confirmées par relecture, sur un seul chemin attendu par tâche ; un échantillon relu à l'aveugle par l'auteur en lève 3 sur 10. »

**À éviter.** « Non-fiabilité établie » sans préciser où ; « rien à déléguer » sans définition ; « B-tout tient le budget partout » ; « bat la liste fixe et le tri par le risque » ; « de 7 à 2 400 fois la barre ».

## À faire avant l'article, par ordre

1. Corriger `outils/tables_article.py` (tables 5 et 9, figure du budget) et régénérer.
2. Réécrire la phrase de résultat et le sens de R4 (constats 2, 4, 17).
3. Ajouter à la table 6 : n_eff à ρ = 1, borne basse, ρ̂, erreurs attendues à la barre ; publier la version « réserve entière » à côté.
4. Produire l'analyse exploratoire des exclusions promise au dépôt.
5. Analyses exploratoires datées : erreurs confirmées croisées avec la réussite des tâches ; part des refusées ; erreurs exécutées puis corrigées au palier 2 ; sensibilité aux fausses confirmations (table du constat 8).
6. Déclarer l'écart du correctif (constat 18) et faire vérifier l'identité des 6 tables par un tiers.
7. Donner l'alerte des tests de résistance et sa cause.
