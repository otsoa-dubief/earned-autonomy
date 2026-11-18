# Audit de l'article, version atelier (main.pdf du 17/11/2026)

Relecteur : Claude (Opus 5.5), contexte neuf, 17/11/2026. Lecture seule. Aucun fichier modifié hors ce rapport. Aucun appel payant, aucun commit.

Gravité : **bloquant** = à corriger avant arXiv ; **important** = affaiblit une conclusion, sa traçabilité ou sa présentation ; **mineur** = à corriger au passage.

Les renvois « PDF l. N » désignent la ligne N de `pdftotext -layout article/latex/main.pdf -`. Les pages sont celles du PDF (64 pages).

---

## 0. Ce que j'ai lu, ce que je n'ai pas lu

Lu :
- `article/latex/main.pdf`, en entier (texte extrait, plus le rendu des pages 4, 5, 29 et 33).
- `article/atelier.md` : comparaison des nombres avec le corps du PDF (aucun écart), début du fichier.
- `article/brouillon.md` : titres, et comparaison des nombres avec les annexes B à E (aucun écart hors références).
- `article/latex/main.tex` (préambule), `main.log` (avertissements), liste de `article/latex/tables/`.
- `article/sources_chiffres.csv` : quelques lignes, par recherche.
- `experience/rejeu_final/` : tous les CSV, `meta.json` (clés), `RESULTATS.md` (recherche seulement).
- `experience/exploratoire/` : tous les CSV et `RESUME.md`.
- `experience/audit_sans_alerte/audit_conclusion.txt`, `experience/tirage/impulsion.json`, `experience/tirage/partage.json` (champs simples).
- `JOURNAL_CHANGEMENTS.md` : lignes du 09/11 au 17/11 (l. 53 à 71).
- `PLAN_SUITE.md` : section 0 (R1 à R8).
- `PLAN_EXPERIENCE.md` : titres et recherches ciblées (5.12, comparateurs). Pas lu en entier.
- `revues/2026-11-14_audit_fable.md` et `revues/2026-11-17_audit_fable_resultats.md`, en entier.

Pas lu :
- `article/latex/body.tex`, `abstract.tex` (taille seulement), `appendix_*.tex` : le PDF en sort ; je juge le PDF.
- `lectures/` : non nécessaire à cette grille ; je n'ai pas vérifié les citations.
- `donnees/`, `pilote/`, `data/`, `experience/vague1/`, `experience/vague2/`, `banc/`, `simulation/`, `gel/`, `externe/`, `~/.config/` : non ouverts.
- Les autres fichiers de `revues/` : non ouverts (seul leur nom est apparu dans une liste du dossier).

Ce que je n'ai pas pu vérifier depuis les fichiers autorisés : 14 265 parties jouées, 837,19 $, couverture de la banque (92,5 % et 93,0 %), 3 sur 10 confirmées levées par l'auteur (`accord.json` hors périmètre), heure du dépôt OSF du plan (05:00 UTC).

---

## Liste des constats

| N° | Gravité | Constat | Où |
|---|---|---|---|
| B1 | bloquant | Crochet « [VERIFY: names of independent human or model reviewers…] » laissé dans les déclarations | p. 7, PDF l. 347 |
| B2 | bloquant | Table X2 : colonne « bar » fausse pour l'argent en aviation et en commerce (8.31918 et 8.82205 au lieu de 0.0000832 et 0.0000882 ; exposant perdu) | p. 52, PDF l. 2795-2807 ; `C_sensibilite_fausses_confirmations.csv`, colonne `barre` |
| B3 | bloquant | Table de décision laissée en français, avec la consigne interne « to be translated by hand for the paper », et deux lignes « témoin liste_fixe : battu », « témoin tri_risque : battu » sans note (formule R8) | p. 27-29, PDF l. 1297-1534 |
| I1 | important | Table G : 9 pages, colonne « règle » absente, donc 4 lignes indiscernables par type ; 34 bornes basses négatives pour une proportion, sans note | p. 37-45, PDF l. 1798-2658 ; `garantie.csv` (100 lignes par règle) |
| I2 | important | Tables d'annexe en français : aviation, banque, commerce (le texte dit airline, banking, retail), au-dessus, indéterminé, scénario, annoncé, silencieux, B-régulier, retard10, groupees ; table des règles secondaires avec la colonne « keeps budget True » (formule R8) | p. 30-50 ; PDF l. 2722 |
| I3 | important | Séparation préenregistré / exploratoire : dans le corps, trois chiffres post hoc sans étiquette | §7 PDF l. 268-270 ; §6.2 l. 188 ; §6.5-6.6 l. 254 |
| I4 | important | Statut public des dépôts OSF non dit (embargo, levée) : « anyone can redo the draw » n'est vrai qu'après levée | p. 1, 18, 64 |
| I5 | important | Sorties secondaires annoncées, non rapportées : « approve everything », « autonomy after three successes », oracle rétrospectif, charge avec épreuves, sensibilité à l'ordre des parties | C.5.1, C.5.4, PDF l. 899-902, 997-998 |
| I6 | important | Relecture des alertes : harnais de la vague 1 inconnu, non dit ; analyses annoncées par l'audit du 14/11 (levées par modèle de l'agent, relecture par un autre fournisseur, vague 1 relue avec le harnais de la vague 2) ni faites ni déclarées abandonnées | Annexe A, D7 ; limite 9 |
| I7 | important | D1 garde l'étiquette « (presentation) », alors que la page simplifiée change la tâche : verdict calculé, ordre b, c, a, d, question (a) amputée de trois règles, question (d) mal formulée ; l'instrument humain figé n'a jamais servi | D1, D8, PDF l. 511-520, 573-577 |
| I8 | important | Retraits de la banque fondés sur la base de connaissances : déclarés comme interprétation, sans analyse de sensibilité ; task_082 (a3 « moins net ») non discutée | D11, PDF l. 599-602 |
| I9 | important | Version « atelier » non anonymisée (nom, courriel, ORCID, liens OSF nominatifs) et pas au gabarit d'une conférence (`article` 11 pt) | p. 1 ; `main.tex` l. 3 |
| I10 | important | Le cadrage « a pre-registered protocol that could fail » survend : aux volumes prévus, le plan savait qu'aucun type ne pouvait être prouvé sous sa barre et que N à enjeu fort dépasse les données ; le résultat est surtout un résultat de faisabilité | §1 PDF l. 48-52 ; C.5.3 l. 983-987 ; limite 11 |
| M1 | mineur | §6.7 donne la pire borne de l'alerte de résistance à 1,65-1,68 ; omet 2,34 en retard10 | PDF l. 258 ; `resistance.csv`, bilan retard10 B-tout 2,336 |
| M2 | mineur | D4 parle de deux fiches levées hors motif ; le moteur en compte 3 ; la troisième (vague 2) n'est pas décrite | PDF l. 544-551 ; `decision.csv` |
| M3 | mineur | Coût de la vague 1 : 72,10 $ puis 72,13 $ ; arrêt à 72,00 $ alors que 0,8 × 1,5 × 60,53 = 72,64 $ | C.6.1, PDF l. 1006, 1018 ; B.4.4 l. 846 |
| M4 | mineur | Mentions « fragile » : le compte 27 est juste (`decision.csv`), mais la description « the airline, retail and banking/Sonnet configurations and their model-change scenarios » est fausse en détail (seule aviation/Haiku est fragile parmi les configurations aviation ; 2 scénarios aviation n'y sont pas) | PDF l. 1100-1102 |
| M5 | mineur | X3 porte sur toute la réserve (13 623 parties), la légende ne le dit pas ; X5 mêle taux de la réserve entière et part au palier 2 de la confirmation, sans le dire | p. 53, 55 |
| M6 | mineur | Table 5 : deux colonnes redondantes (« judged, excess established » et « established excess ») | p. 32 |
| M7 | mineur | Table 7 : intervalles au-delà de 100 pour une charge bornée (102,3 ; 110,5), sans note | p. 36 |
| M8 | mineur | Renvois ambigus vers la version longue : « Section 4.3 » (déclarations) et « Appendix B, Section 3.4 » (corps) visent B.4.3 et B.3.4 ; « Table 2 » désigne deux tables (épisodes prévus en B.4.2, table de décision en C.6.2 et E.7) ; plusieurs tables sans numéro | p. 3, 7, 16, 22, 60 |
| M9 | mineur | D12 ne dit pas qu'aucune sortie du premier passage n'a été lue avant le second (le journal l. 68 le dit) ; « checked independently » sans dire par qui | PDF l. 603-616 |
| M10 | mineur | Spécification octet par octet du tirage absente (audit 14/11, n° 4) ; renvoyer au script et à son empreinte en annexe F | Annexe F |
| M11 | mineur | Haiku 5.5 présent dans `execution.jsonl` (audit 14/11, n° 12) : non mentionné | D7 |
| M12 | mineur | Kappa et intervalle de 13/15 absents (audit 14/11, n° 16) | C.6.1, limite 9 |
| M13 | mineur | Par tâche retirée, nombre d'alertes du motif (a) sur le total : absent (audit 14/11, n° 19) | C.6.1, table de décision |
| M14 | mineur | Taux d'exclusion par configuration absent (77 parties de Haiku en banque, environ 10 %), seulement des comptes | Table 3, p. 46 |
| M15 | mineur | Analyse de sensibilité avec les levées hors motif reconfirmées : non faite (3 alertes, poids négligeable ; le dire) | D4 |
| M16 | mineur | E.2 : deux paragraphes successifs sur Zhang et Zhang qui se répètent | PDF l. 2993-3021 |
| M17 | mineur | « registered on OSF on 10 November 2026 at 05:00 UTC » : donner l'horodatage serveur exact (l'audit du 14/11 cite un commit à 06 h 03 heure locale) | §1, PDF l. 49-50 |
| M18 | mineur | La valeur probante du commit du manifeste dépend d'un historique publié intact (audit 14/11, n° 3) : non dit | Annexe A, F |
| M19 | mineur | Table 6 en corps minuscule, illisible à l'impression ; figure 2 : étiquettes de la banque superposées (« lowmediumhigh ») ; figure 3 : titre d'axe coupé | p. 33, 5, 6 |
| M20 | mineur | 5 « Overfull hbox » (URL Hryniewicz, chemins `outils/…` en D7 et D13, une figure à 76 pt) | `main.log` l. 557-646 |
| M21 | mineur | `journal_rejeu_final.jsonl` non cité dans l'annexe F (audit 17/11, n° 27) | Annexe F |
| M22 | mineur | §6.6 « withdrawal … took 40 to 61 writes » : le corps omet « lecture secondaire » (l'annexe le dit) | PDF l. 254 ; `retrait.csv`, `lecture = secondaire` |

Total : **3 bloquants, 10 importants, 22 mineurs.**

Corrections proposées, une ligne par constat :
- B1 : retirer la phrase « Reviewers » ou la remplir.
- B2 : écrire la barre en notation scientifique ou en pourcentage dans `outils/tables_exploratoires.py`.
- B3 : traduire la table de décision, supprimer la consigne interne, annoter les deux lignes « battu » comme pour « réussite » (« libellé du critère, point 2 non jugé sous R4 »), ou remplacer la table par la version anglaise de la table 2.
- I1 : ne garder que B-tout, ajouter la colonne règle, borner à [0 ; 1] ou prendre la seconde méthode (percentile) ; ou sortir la table de l'article et renvoyer au CSV.
- I2 : traduire les libellés dans `outils/tables_latex.py` ; renommer « keeps budget » en « no established excess ».
- I3 : ajouter « (exploratory, Appendix D) » aux trois endroits.
- I4 : dire si vycge et cusv6 sont publics ; lever l'embargo avant arXiv.
- I5 : une table courte de ces sorties, ou une phrase par sortie qui dit pourquoi elle n'est pas donnée.
- I6 : écrire en D7 que le harnais de la vague 1 est inconnu, et que les analyses annoncées ne sont pas faites.
- I7 : réécrire D1 avec les quatre différences et dire que l'instrument figé n'a pas servi.
- I8 : produire l'analyse de sensibilité (trois tâches gardées) ou écrire qu'elle n'est pas faite ; dire un mot de task_082.
- I9 : pour un atelier en double aveugle, gabarit de la conférence et version anonyme ; arXiv peut garder la version signée.
- I10 : présenter la contribution 3 comme « un protocole préenregistré dont on montre les volumes qu'il exige » ; dire dès l'introduction que le plan prévoyait l'absence de certification sous la barre.
- M1 à M22 : voir la colonne « Constat ».

---

## 1. Les 53 constats des deux audits

### Audit du 14/11 (26 constats)

| N° | Sujet | Statut | Où, ou pourquoi |
|---|---|---|---|
| 1 | Commande du rejeu final non fixée | Traité | D11 (fixée dans cusv6), D12, annexe F |
| 2 | Horodatage OSF ambigu | Traité | D11 ; C.6.1 et F (`date_registered` à la seconde, impulsion 2031457 ; conforme à `impulsion.json`) |
| 3 | `gel_plan.json` sans étiquette, commit invisible | En partie | Étiquette et commit a8eb1aae donnés ; dépendance à un historique publié non dite (M18) |
| 4 | Tirage non refaisable dans un autre langage | Non traité | M10 |
| 5 | Manifeste complet | Sans objet | Aucun défaut |
| 6 | Dépôt soumis par Claude, embargo | En partie | D11 dit que l'embargo a été approuvé sur consigne de l'assistant ; ni qui a soumis, ni la durée, ni le statut public (I4) |
| 7 | Raison des relances perdue | Traité | D7 : les 1 428 lots fermés au premier essai |
| 8 | Vagues 1 et 2 non comparables | Insuffisant | Modèle et découpage déclarés ; harnais de la vague 1 non dit ; analyse annoncée absente (I6) |
| 9 | Opus relit Opus | Insuffisant | Limite 9 renforcée ; analyses annoncées absentes (I6) |
| 10 | Aveugle sur la seule obéissance | Traité | B.4.3, D7, limite 9 |
| 11 | 32 s par lot | Traité comme limite | Limite 9, §8 ; non expliqué (attaque probable, point 6) |
| 12 | Haiku dans `execution.jsonl` | Non traité | M11 |
| 13 | Extension de la règle de relance | Sans objet | Aucune relance (D7) |
| 14 | Page simplifiée change la tâche | Insuffisant | D1, D8 ; I7 |
| 15 | Levées hors motif | Traité | D4 ; compte 2 contre 3 (M2) ; sensibilité absente (M15) |
| 16 | Ce que 13/15 établit | En partie | Limite 9 (4 désaccords, 28 % levées), 3/10 et [7 ; 65 %] ; kappa et intervalle de 13/15 absents (M12) |
| 17 | Retraits de la banque par la base de connaissances | Insuffisant | D11 déclare une interprétation ; pas de sensibilité ; task_082 absente (I8) |
| 18 | Commerce 98 | Traité | D11 : opposition, 23 alertes confirmées |
| 19 | Portée des retraits et de l'audit | En partie | Limite 28 et C.6.1 (borne 13 %) ; compte du motif (a) par tâche absent (M13) ; la limite 4 ne dit pas que l'audit ne peut pas appuyer d = 0,95 |
| 20 | Journal arrêté au 13/11 | Traité | Annexe A complète (point 5) ; 13 081 contre 13 080 expliqué en C.6.1 |
| 21 | Exclusions de Haiku en banque | En partie | Table X1 (définition et résultat) ; taux par configuration absent (M14) |
| 22 | H1 ne peut presque pas échouer | Traité | §5 « What the labels can mean », C.5.2 |
| 23 | Formulations de 3.4, titre | Traité | §3 « long-run bound when d < 1 » ; résumé « conditional bound » ; titre sans « guarantee » |
| 24 | « every write action is judged » | Traité | Résumé : « writes checked by exact comparison (98.7% coverage) » |
| 25 | Mises à jour 4.3, limites, écarts | Traité | B.4.3, D5, D7, limite 9, §1 (05:00 et 05:19 UTC) |
| 26 | Défauts de `tables_article.py` | Traité | Table 5 avec les scénarios, « – » pour les vides, figure 1 au budget faible |

### Audit du 17/11 (27 constats)

| N° | Sujet | Statut | Où, ou pourquoi |
|---|---|---|---|
| 1 | Dérivation de R4 | Sans objet | Vérifié à nouveau : seul type jugeable WorkBench/Haiku ECR, borne basse 4,14 % > 0,757 % |
| 2 | R4 sur un type, marge mince | Traité | §6.2, limite 21, table X6 |
| 3 | Dimensionnement, pas classement | Traité | §7, limite 31 |
| 4 | Trois délégables sur la réserve entière | Traité | §6.4, C.6.4, table 6 bis, limite 21 |
| 5 | 13 types sans erreur | Traité | C.6.4 les nomme ; asymétrie « partly built in » dite |
| 6 | 20 dépassements établis | Sans objet | Recalculé : 20 |
| 7 | « de 7 à 2 400 » | Traité | Absent ; taux d'abord, puis borne basse ÷ barre, par niveau |
| 8 | Sensibilité aux fausses confirmations | Traité | Table X2 ; mais colonne barre fausse (B2) |
| 9 | Erreurs dans des tâches réussies | Traité | Table X3, limite 24 |
| 10 | Refusées comptées | Traité | Table X4, limite 25 |
| 11 | Banque à part | Traité | §6.4, C.6.4, limite 27 |
| 12 | Borne à ρ = 1 et approximation | Traité | §5, C.6.4 |
| 13 | 9 et 18 cellules | Traité | §6.5, C.6.5 |
| 14 | Témoins vrais par construction | Traité dans le texte | Mais lignes « battu » de la table de décision sans note (B3) |
| 15 | Palier 2 | Traité | Limite 26, table X5, table 7 bis |
| 16 | Point 1 sans puissance | Traité | §6.3, C.6.3, limite 22 |
| 17 | Baisse de charge contre « rien de délégable » | Traité | Résumé, §6.5, table 7 bis |
| 18 | Correctif du rejeu | Traité | D12 ; phrase « rien lu du premier passage » absente (M9) |
| 19 | Verdicts bruts, échange des rôles | Traité | §6.2, limite 30 |
| 20 | Alerte de résistance | Traité | §6.7, C.6.7, table 9 ; le corps omet 2,34 (M1) |
| 21 | Mentions « fragile » | Traité | 27 dans l'article, 27 dans `decision.csv` (l'audit disait 29 : c'est l'audit qui se trompait) ; description inexacte (M4) |
| 22 | Analyse des exclusions | Traité | Table X1 |
| 23 | Audit 0 sur 21 | Traité | Limite 28 |
| 24 | Table 5 fausse | Traité | Recalculée : 51 jugées, 108, 21, 6 non testables, conforme à `budget.csv` |
| 25 | Table 9 inutilisable | Traité | 28 lignes « bilan du mode » ; le même défaut est passé à la table G (I1) |
| 26 | Table 6 sans n_eff, borne, ρ̂ | Traité | Colonnes présentes |
| 27 | Défauts mineurs de sortie | En partie | Symétrie et asymétrie de l'aviation traitées ; bornes > 1 annotées mais bornes < 0 non (I1) ; libellés français restés (B3, I2) ; `journal_rejeu_final.jsonl` non cité (M21) |

---

## 2. Formules interdites (R8)

| Formule | Présente ? | Où |
|---|---|---|
| « unreliability established » sans dire où | Non dans le texte. Une seule fois, comme nom préenregistré, suivi de « Section 6.2 states what it means here » | PDF l. 918 |
| « nothing to delegate » sans définition | Non. Deux fois comme nom préenregistré défini (l. 918, 930), une fois niée (limite 21, l. 3231) | — |
| « B-tout keeps the budget » | Non comme affirmation. Présente comme énoncé du critère H1 (l. 908) et niée (limite 22). **Présente en colonne** « keeps budget : True » de la table des règles secondaires (l. 2722) | I2 |
| « beats the fixed list and the risk triage » | Non dans le texte. **Présente en substance** dans la table de décision : « témoin liste_fixe : battu », « témoin tri_risque : battu », sans note | B3 |
| « 7 to 2,400 times the bar » | Non | — |
| Classement des trois modèles | Non. Nié explicitement (§7, limite 31) | — |

---

## 3. Chiffres recalculés depuis les CSV

Méthode : Python, lignes « # » écartées. Tous les chiffres ci-dessous concordent, sauf mention.

| Chiffre de l'article | Source | Recalcul | Verdict |
|---|---|---|---|
| R4 ; un seul type jugeable (WorkBench/Haiku ECR) | `ecart.csv` principal | 1 jugeable | OK |
| 8,6 % ; 914 écritures ; 79 erreurs ; borne basse 4,1 % ; barre 0,76 % | `ecart.csv` | 8,64 % ; 4,141 % ; 0,757 % | OK |
| n_eff × barre = 0,740 ; ρ̂ = 0,819 | `ecart.csv` | 0,7402 ; 0,819 | OK |
| 20 sur 40 au-dessus ; 20 indéterminés ; 0 en dessous | `ecart.csv` | 20 / 20 / 0 sur 40 types avec données | OK |
| 13 sans erreur, de 3 à 122 écritures | `ecart.csv` | 13 ; n de 3 à 122 | OK |
| 7 avec erreurs sans dépassement établi | `ecart.csv` | 7 | OK |
| WorkBench ECR 5,5 à 8,6 % ; borne basse ÷ barre 2,7 à 5,5 | `ecart.csv` | 5,49-8,64 % ; 2,7-5,5 | OK |
| Argent aviation et commerce 6,5 à 13,3 % ; ratios 70, 39, 10 ; 248, 118, 109 | `ecart.csv` | 6,50-13,31 % ; 70,2 ; 39,4 ; 10,4 ; 247,8 ; 118,4 ; 108,8 | OK |
| Banque 28 à 56 % (argent et enjeu moyen) | `ecart.csv` | 28,5-56,0 % | OK |
| 21 types au-dessus sous ρ̂ | `ecart.csv` | 21 | OK |
| Réserve entière : 22 sur 41 ; 3 délégables (WB Opus MSG, WB Sonnet MSG, commerce Sonnet ECR) | `ecart.csv` version « calibration et confirmation » | 22 sur 41 ; mêmes 3 | OK |
| 180 cellules : 51 jugées, 108, 21 ; 6 non testables | `budget.csv` B-tout, e = 0,05 | 51 / 108 / 21 ; 5 + 1 | OK |
| Toutes à enjeu faible ; c* = 7,0 | `budget.csv` | 51 faibles ; 7,01 | OK |
| Valeur centrale ≤ 0,38 fois le budget | `budget.csv` | 0,381 | OK |
| Pire borne haute 1,67 | `budget.csv`, `choix.csv` | 1,668 | OK |
| 24 cellules avec s/q > 1/0,95 (11 WB, 13 banque) ; s/q 0,72 à 1,14 ; borne jusqu'à 1,08 fois | `budget.csv` | 24 (11 + 13) ; 0,718-1,141 ; 1,084 | OK |
| Témoins : liste fixe 1 configuration (WB/Haiku, 5,5, 11 fois) ; tri 2 (WB/Haiku 5,8 ; banque/Haiku 10,2) ; 9 et 18 cellules | `budget.csv`, `depassement_etabli` | Identique ; 9 et 18 | OK |
| WB Sonnet et Opus à 6,6 et 6,1 fois | `budget.csv` | 3,29 et 3,03 pour 100, soit 6,6 et 6,1 | OK |
| Charge B-tout 65,5 / 54,9 / 55,1 ; commerce 84-86 ; banque 90-94 ; aviation 98-100 | `charges.csv` | Identique | OK |
| Commerce : témoins 83,4 / 82,5 / 81,9 contre 84,4 / 84,1 / 85,8 | `charges.csv` | Identique | OK |
| Palier 2 sur ECR WB : 63 %, 81 %, 81 % | `volume.csv` | 63,0 ; 81,3 ; 81,2 | OK |
| Retrait commerce : médianes 61 et 40, p95 226 et 108, une erreur passée, 85 à 100 % | `retrait.csv` | Identique (lecture secondaire) | OK (M22) |
| Banque/Opus MSG au palier 3 : 4,3 %, jusqu'à 11,8 % ; banque/Sonnet MSG 8,3 % | `garantie.csv`, B-tout | 4,25 % ; 11,8 % ; 8,25 % | OK |
| Alerte de résistance : 7 modes ; 1,65 à 1,68 ; 2,34 en retard10 ; A½ 0,23-0,65 ; A¼ 0,43-1,06 | `resistance.csv`, bilans | Identique | OK (corps : M1) |
| Règles secondaires : 78, 10, 13 cellules ; 2,21 ; 0,39 ; 0,43 | `choix.csv` | Identique | OK |
| Mentions « fragile » : 27 | `decision.csv` | 27 | OK |
| 2 761 alertes ; 1 991 / 770 ; a 75, b 78, c 331, d 283, hors motif 3 | `decision.csv` | Identique | OK |
| Couverture 98,7 % | `decision.csv` | 0,9868 | OK |
| 13 623 parties analysées | `reussite_taches.csv` ; `D_erreurs_et_reussite.csv` | 13 623 | OK |
| Réussite des tâches : WB 94,9-99,3 ; aviation 81,7-92,5 ; commerce 84,0-92,8 ; banque 18,3-50,9 | `reussite_taches.csv` | Identique | OK |
| 91 exclusions : 77 / 10 / 2 banque, 2 aviation ; 9 et 82 par vague | `A_parties_exclues.csv` | Identique | OK |
| Exclusions comptées : +24 erreurs ; 20 → 21 | `A_ecart_avec_exclusions.csv` | 24 ; 20 → 21 | OK |
| 63 % (type qui porte R4) ; 31 à 79 % (argent aviation et commerce) | `C_…csv` | 0,63 ; 0,31-0,79 | OK |
| **Table X2, colonne « bar »** | `C_…csv`, `barre` | 8,32e-05 et 8,82e-05 | **Écart (B2)** |
| 64 à 82 % de parties réussies parmi celles à erreur (WB) | `D_…csv` | 0,639-0,818 | OK |
| 104 sur 1 067 refusées (9,7 %) | `E_…csv` | 104 / 1 067 | OK |
| 4,6 à 6,2 erreurs pour 100 au palier 2 (WB) | `F_…csv` | 4,637-6,223 | OK |
| ρ̂ 0,800 [0,660 ; 0,924] ; 9,6 % au-dessus de 0,885 | `G_…csv` | Identique | OK |
| Manifeste 904aa8d3…f88d ; impulsion 2031457 à 08:18:00 UTC ; dépôt 08:17:47 UTC | `partage.json`, `impulsion.json` | Identique | OK |
| Audit sans alerte : 0 sur 21 (8, 3, 4, 6) | `audit_conclusion.txt` | Identique | OK |
| 14 266 parties prévues | Calcul : 50 × 40 + 50 × 91 + 10 × 77 + 5 × 552 + 2 × (10 × 40 + 10 × 91 + 3 × 77 + 552) | 14 266 | OK |
| Barres et N de la table 1 | Formule N = ⌈1/(0,95 × barre)⌉ − 1 sur les barres de `ecart.csv` | Concordant (ex. WB faible : 138) | OK |

Conclusion : hors B2, aucun écart dans le résumé, les sections 6 et 7 du corps et la conclusion.

---

## 4. Préenregistré et exploratoire

Bien fait :
- Annexe D entière marquée « Not pre-registered; run after the verdict, dated 17 November 2026 ». Chaque table X porte « (Exploratory, dated 17 November 2026) ».
- Les CSV exploratoires portent la même mention en tête.
- Table 6 bis : « DESCRIPTIVE ONLY: it cannot serve as the label ». Figure 3 : « descriptive: the pre-registered comparison is not judged ».
- §6.4 « On the whole reserve (descriptive) » ; §6.7 « Exploratory analyses, dated after the verdict » ; §7 « (exploratory) » pour le palier 2.
- Limites marquées « preregistered », « added after the freeze » ou « added after the results ».

Glissements :
- I3. §7 (PDF l. 268-270) : « high-stakes rates stay established with 31 % to 79 % false confirmations » vient de la table X2, sans « exploratory ». §6.2 (l. 188) : le seuil ρ̂ = 0,885 est un calcul post hoc, sans étiquette dans le corps (l'annexe C renvoie à X6). §6.6 (l. 254) : chiffres de lecture secondaire sans le dire (M22).
- M5. X3 et X5 ne disent pas sur quelle moitié ils portent.
- La table de décision (p. 27-29) mêle sortie du moteur et note de l'auteur dans la même légende. Acceptable une fois traduite (B3).

---

## 5. Écarts au préenregistrement : journal contre annexe A

Lignes du journal datées du 10/11 ou après :

| Ligne du journal | Contenu | Annexe A |
|---|---|---|
| l. 56 (10/11, soir) | Page de relecture simplifiée, vague 1 | D1 (insuffisant, I7) |
| l. 57 (10/11, soir) | Lecture des erreurs de la banque, biais d'exclusion | D2 |
| l. 58 (10/11, soir) | Incident de lancement de la vague 2 | D3 |
| l. 59 (13/11) | Procédure de relecture de la vague 2 | D7 |
| l. 60 (13/11) | Page simplifiée en vague 2 | D8 |
| l. 61 (10/11 et 14/11) | Levées d'Otsoa hors motif | D4 (compte : M2) |
| l. 62 (13/11) | Outils absents de la table | D6 |
| l. 63 (14/11) | Audit des tâches sans alerte | D9 |
| l. 64 (14/11) | Précisions sur la relecture (relance, Read, Opus sur Opus, lots, 32 s) | D7 et limite 9 |
| l. 65 (14/11) | u26kr, commerce 98, commande, horodatage, base de connaissances | D11 |
| l. 66 (14/11) | Diagnostic des échecs de la vague 2 (207 et 19) | D10 |
| l. 67 (14/11, 8 h UTC) | u26kr non annulable, dépôt cusv6 | D11 |
| l. 68 (17/11) | Échec du rejeu final et correctif en mémoire | D12 (M9) |
| l. 69 (17/11) | `tables_article.py` corrigé | D13 |
| l. 70 (17/11) | Analyses exploratoires E, F, G | D13 |
| l. 71 (17/11) | `tables_exploratoires.py` et registre des chiffres | D13 |

Toutes les lignes sont déclarées. D5 (coût) est déclaré sans ligne au journal : sans gravité. D0 (09/11, nuit) correspond à la l. 55.

---

## 6. Ce qu'un relecteur d'atelier attaquerait, par ordre de gravité

1. **L'expérience ne pouvait presque rien confirmer.** Le plan savait qu'aucun type ne serait prouvé sous sa barre (C.5.3, l. 983-987) et que N à enjeu fort (2 582 à 12 653) dépasse les données. Réponse du texte : honnête (limite 11, §5, §7), mais le cadrage de l'introduction (« a protocol that could fail ») survend. → I10. Ajouter une phrase dès l'introduction ; présenter le résultat comme une mesure des volumes exigés.
2. **Validité de la vérité terrain.** Erreurs confirmées par des instances Claude, Opus relisant Opus, 32 s par lot sans explication, un seul chemin attendu, 3 sur 10 confirmées levées par l'auteur, client simulé qui dérive. Réponse : tout est déclaré (limites 6 à 9, 23), et la table X2 est une bonne parade. Manque : aucun contrôle par un autre fournisseur, aucune explication des 32 s. → I6. Au minimum, écrire que ces contrôles n'ont pas été faits et pourquoi.
3. **Nouveauté.** La borne adapte l'UAOQL et « n'est pas revendiquée comme nouvelle » ; la règle est simple. Réponse : positionnement net (Zhang et Zhang, CASE, Weber et Taneja). Suffisant pour un atelier, faible pour une conférence principale.
4. **H1 vide par construction.** Réponse : dite franchement (§5, limite 22). Rien à ajouter.
5. **Budget arbitraire.** À enjeu fort, les rapports mesurent le budget. Réponse : dite (§6.4, limite 11). Manque une lecture utile : quel budget rendrait chaque type jugeable ou délégable aux volumes observés (exploratoire, une table). Non traité ; non bloquant.
6. **Rejeu hors ligne, validateur simulé, pas de contrefactuel.** Réponse : limites 1 à 3. Suffisant.
7. **Plan déséquilibré** (Haiku joue 5 fois plus). Réponse : limite 31. Suffisant.
8. **Sorties préenregistrées manquantes.** « approve everything », « three successes », oracle rétrospectif, charge avec épreuves, ordre des parties : annoncés, non rapportés. Un relecteur y verra un rapport sélectif. → I5.
9. **Vérifiabilité.** Si les dépôts OSF sont sous embargo, rien n'est vérifiable à la soumission. → I4.
10. **Indépendance.** Code, texte, audits et relectures par des instances Claude ; agents évalués aussi Claude. Réponse : déclaration d'usage d'IA complète. Le crochet « [VERIFY: … reviewers] » (B1) aggrave l'impression. Une relecture humaine extérieure, prévue au plan, répondrait.
11. **Présentation.** 64 pages pour un corps de 6 ; tables en français ; table G de 9 pages illisible ; table de décision non traduite ; version non anonyme. → B3, I1, I2, I9.

---

## 7. Cohérence, renvois, mise en forme

Cohérence corps / annexes / figures / tables :
- Corps et `atelier.md` : mêmes nombres. Annexes B à E et `brouillon.md` : mêmes nombres. Les annexes reprennent bien la version longue.
- Figure 1 : 11 + 11 + 14 + 15 = 51 cellules, conforme à la table 5. Figure 2 : 40 types, conforme à la table 6. Figure 3 : conforme à la table 7.
- Écarts de détail : M1 (2,34 omis dans le corps), M3 (72,10 contre 72,13 $), M4 (description des « fragile »), M22.
- Le corps parle de « delay10 », la table 9 de « retard10 » ; le texte de « B-regular », les tables de « B-régulier » (I2).

Renvois :
- Aucun « ?? » dans le PDF ; pas de référence indéfinie au journal LaTeX.
- Renvois ambigus vers la version longue et double « Table 2 » (M8).

Mise en forme :
- B1 (crochet), B3 (table française et consigne interne), I1 (table G), I2 (libellés français).
- M19 (table 6 minuscule, figure 2 superposée, figure 3 coupée), M20 (5 débordements de marge).
- Résumé : 1 531 caractères de source, sous la limite d'arXiv (1 920).

---

## Verdict

**Prêt après corrections.**

L'étiquette R4 est bien dérivée. Les chiffres du résumé, des sections 6 et 7 et de la conclusion se recalculent sans écart. Les écarts au préenregistrement sont tous déclarés. Les formules R8 sont absentes du texte.

Avant arXiv, il faut au minimum : B1, B2, B3 (une heure de travail), puis I1, I2, I4. I3, I5 à I8 et I10 renforcent l'article face à un relecteur. I9 ne compte que pour une soumission en double aveugle.
