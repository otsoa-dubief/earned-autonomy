# Audit indépendant de l'article (brouillon du 17/11) et de sa version française de contrôle

Date : 17 novembre 2026. Relecteur : Claude (Fable 5.2), contexte neuf.
Objet : `article/brouillon.md` (464 lignes) et `article/controle_fr.md`.

## Périmètre et méthode

- Lu : `article/` (brouillon, contrôle, `FORMULATION_VERDICT.md`, `PLAN_ARTICLE.md`, `sources_chiffres.csv`, `resultats/tables.md`, `resultats/tables_exploratoires.md`, `morceaux/deviation_correctif_en.md`, `verif_originaux.md`), `experience/rejeu_final/` (les 13 CSV, `meta.json`, extraits de `RESULTATS.md`), `experience/exploratoire/` (A à G, `RESUME.md`), `experience/audit_sans_alerte/audit_conclusion.txt`, `experience/tirage/`, `revues/2026-11-17_audit_fable_resultats.md`, les titres et six constats de `revues/2026-11-14_audit_fable.md`, `lectures/zhang_zhang_autorite_meritee.md`, `lectures/case_budget_erreurs.md`, `JOURNAL_CHANGEMENTS.md`, `SUIVI.md` (lignes 289 à 418, par recherche), `PLAN_EXPERIENCE.md` (1.3 à 1.5, 5.3, 5.10, 5.12, 5.13 en partie, 5.14), `PLAN_SUITE.md` (sections 0 et 1).
- Non ouvert : `donnees/`, `pilote/`, `data/`, `experience/vague1/`, `experience/vague2/`, `banc/`, `simulation/`, `gel/`, `externe/`, `~/.config/`. Aucun appel payant, aucun fichier modifié, aucun commit.
- Calculs : relecture des CSV en Python (lignes « # » écartées). Recalcul avec scipy de la borne de Clopper-Pearson du type qui porte R4 et du seuil de jugeabilité.
- Limite de l'audit : les chiffres dont la seule source est un `rapport_vague.txt` ou un `accord.json` (dossiers interdits) n'ont pas pu être recalculés. Je les ai recoupés avec `SUIVI.md` et le journal quand ils y figurent.
- Gravité : **bloquant** = à corriger avant qu'Otsoa valide le fond ; **important** = affirmation fausse, trop forte, ou omission qui change la lecture ; **mineur** = arrondi, renvoi, vocabulaire, déclaration à compléter.
- Les numéros de ligne renvoient à `article/brouillon.md`, sauf mention contraire.

## Vue d'ensemble

Les chiffres qui portent le résultat sont exacts. L'étiquette R4, la jugeabilité, le point 1, le point 2 « non jugé » et les témoins sont décrits conformément au plan. Aucune formulation interdite par R8 n'est employée comme affirmation. Les fiches Zhang et Zhang, CASE et les originaux du contrôle qualité sont respectés.

Les défauts sont ailleurs. Trois phrases de la section 6.6 et de la discussion sont contredites par les CSV. Deux mesures prévues au plan manquent et l'une affaiblit une phrase de 6.5. Le résumé garde une formule déjà relevée comme fausse le 14/11. Les annexes et sept tables citées n'existent pas dans le brouillon.

Décompte : 2 bloquants, 13 importants, 23 mineurs.

---

## Constats

### A. Bloquants

**1. Une phrase périmée ouvre la section 6 et contredit tout ce qui suit. Bloquant (correction d'une ligne).**
- Preuve : l. 230, « *No results yet. Data collection is in progress (wave 2 started on 10 November 2026). This section lists the planned contents only.* ». L'en-tête (l. 3) dit « No result placeholders left ».
- Correction : supprimer la ligne 230.

**2. Section 6.6, limite 29 et contrôle français : « aucune autonomie après un changement de modèle » est faux à enjeu faible. Bloquant.**
- Texte : l. 316, « `derive.csv` records no tier-3 autonomy period after any junction […] so no type that became bad had autonomy to withdraw, and no withdrawal delay can be measured » ; l. 380 (limite 29), « No autonomy period at tier 3 followed any model change in the replay » ; `controle_fr.md` l. 26, « aucune autonomie n'avait été accordée après un changement de modèle ».
- Preuve : `derive.csv` ne porte que sur l'enjeu moyen et fort (critère de la décision 5). `retrait.csv`, B-tout, analyse principale, commerce, ECR, enjeu faible, lecture « secondaire » :

| scénario | promus à la jonction | délai de retrait médian | 95e centile | erreurs passées | autonomies nouvelles après | part du temps au palier 3 après |
|---|---|---|---|---|---|---|
| Sonnet → Haiku, annoncé | 2 000 sur 2 000 | 0 | 0 | 0 | 100 % | 61 % |
| Sonnet → Haiku, silencieux | 2 000 sur 2 000 | 61 écritures | 226 | 1,0 | 100 % | 66 % |
| Sonnet → Opus, annoncé | 2 000 sur 2 000 | 0 | 0 | 0 | 100 % | 37 % |
| Sonnet → Opus, silencieux | 2 000 sur 2 000 | 40 écritures | 108 | 1,0 | 85 % | 57 % |

- `garantie.csv` confirme : des types « au-dessus » atteignent le palier 3 après la jonction (banque MSG, jusqu'à 11,8 % des répétitions). `budget.csv` : 44 cellules de scénario sont jugées, donc B-tout y atteint le palier 3.
- Portée exacte : en lecture principale (intervalle entièrement au-dessus de la barre), aucun type devenu mauvais n'avait d'autonomie (aucune ligne « principal » de B-tout n'a de promu ; 16 lignes sur 20 sont à 0). En lecture secondaire (estimation seule au-dessus : Haiku 3,2 % et Opus 3,8 % pour une barre de 2,6 %), le délai est mesuré. Le plan demande de le publier (1.3, point 5 ; 5.10).
- Correction (anglais) : « Across the 48 scenarios, the withdrawal criterion of decision 5 (medium and high stakes) passed in every scenario × type row, in the main analysis and under delay10. At these levels the pass is empty: no tier-3 period followed any junction. At low stakes, autonomy did cross junctions. On retail, Sonnet's reversible writes were at tier 3 at the junction in all 2,000 replays. When Sonnet was silently replaced by Haiku or Opus (3.2 % and 3.8 % against a 2.6 % bar; "became bad" in the secondary reading only, point estimate above the bar), withdrawal took a median of 61 and 40 writes of the type (95th percentile 226 and 108), with one error let through on average, and autonomy was granted again afterwards in 85 % to 100 % of replays (`retrait.csv`). With an announced change, the reset withdrew autonomy at once. In the primary reading (interval entirely above the bar), no type that became bad held autonomy. »
- Limite 29 : remplacer par « At medium and high stakes, no autonomy period followed any model change, so the decision-5 criterion passed without being tested. At low stakes withdrawal after a silent change was observed on one type only (retail reversible writes, secondary reading). »
- `controle_fr.md` l. 26 : « Le critère de retrait (enjeu moyen et fort) passe partout, mais à vide. À enjeu faible, un retrait après changement silencieux est observé en commerce : 40 à 61 écritures de délai médian, une erreur passée en moyenne. »

### B. Importants

**3. Section 6.6 : « judged ones only […] on airline and retail, all "fragile" » est faux.**
- Texte : l. 316.
- Preuve : `budget.csv`, B-tout, principale, e = 0,05, scénarios jugés : WorkBench 10, banque 12, aviation 10, commerce 12 (44 en tout). 22 sont « fragile », 22 ne le sont pas (WorkBench et banque, 29 à 188 tâches porteuses). `tables.md`, table 5, donne les mêmes effectifs.
- Correction : « judged ones only at low stakes: 10 on WorkBench, 12 on banking, 10 on airline and 12 on retail; the 22 on airline and retail are "fragile" (fewer than 30 carrying tasks); none has an established excess. »

**4. Discussion : « banking's low-stakes cells were mostly not put to the test » est faux.**
- Texte : l. 340.
- Preuve : `budget.csv`, banque, enjeu faible : 14 cellules jugées sur 15 (2 configurations sur 3, 12 scénarios sur 12). Seule banque/Haiku est « tenue, non mise à l'épreuve ». Le palier 3 y est rare (0,2 à 12 % des répétitions), ce qui est autre chose.
- Correction : « The pilot's banking ratio of 2.2 did not recur: s/q is 1.04 to 1.14 in banking's low-stakes cells, 14 of 15 of which were judged, with tier 3 reached in 0.2 % to 12 % of replays only. »

**5. La borne de construction dépasse le budget dans 24 des 51 cellules jugées, et le texte dit le contraire.**
- Texte : l. 276, « the budget can only be exceeded if the actual share s […] exceeds the expected share q by about 5 % » ; l. 340, « Which constraint bound. Neither. […] the construction bound, at most about 1.14 × 0.95 × budget, was never the limiting quantity ».
- Preuve : 1,14 × 0,95 = 1,08 fois le budget. `budget.csv` : s ÷ q dépasse 1 ÷ 0,95 dans 24 cellules jugées (WorkBench 11, banque 13), et la colonne `borne_construction` y dépasse le budget (0,51 à 0,54 pour 0,5). La mention « garantie hors hypothèse » ne sort pas parce qu'elle exige la borne basse de s ÷ q au-dessus de 1,05, pas l'estimation.
- Conséquence : dans ces 24 cellules, la tenue du budget ne repose pas sur la borne mais sur la seule absence de dépassement établi (section 5.3, l. 220). Avec la limite 22 (test presque sans puissance), c'est un point faible à dire.
- Correction (l. 340) : « The mix ratio s/q stayed between 0.72 and 1.14 in the 51 judged cells. In 24 of them (11 on WorkBench, 13 on banking) the point estimate exceeds 1/0.95, so the construction bound there is up to 1.08 times the budget: the bound alone does not guarantee the budget in these cells, although no cell carried the "guarantee outside the assumption" mention, which requires the lower bound of s/q to exceed 1/0.95. »
- Mettre aussi à jour la limite 12 (l. 363), qui garde le seul chiffre du pilote (2,2).

**6. La mesure de la garantie (plan 1.3, point 5 ; 5.12, point 8) n'est pas rapportée, et elle nuance la section 6.5.**
- Texte : l. 312, « B-tout does not grant tier 3 to a type at 8.6 % errors […] whereas a list without error feedback delegates it ».
- Preuve : `garantie.csv`, B-tout. Type « au-dessus » au jeu de calibration qui atteint le palier 3 : banque/Opus MSG (8,1 % d'erreurs, dépassement établi) dans 4,25 % des répétitions en configuration constante, et jusqu'à 11,8 % après la jonction (Sonnet → Opus, silencieux) ; banque/Sonnet MSG 0,2 % ; WorkBench ECR 0,05 à 0,2 %.
- La phrase est vraie pour WorkBench ECR. Elle ne l'est pas pour tout type établi au-dessus de sa barre. La section 5 ne décrit pas cette mesure, la section 6 ne la donne pas.
- Correction : ajouter en 6.5 ou 6.6 : « Guarantee measure (no threshold; plan 5.12). Types classed above their bar on the calibration half still reached tier 3 in some replays: banking/Opus internal messages (8.1 % errors) in 4.3 % of replays as a constant configuration and in up to 11.8 % after a silent change from Sonnet; WorkBench reversible writes in at most 0.2 %. »
- Défaut de la table G (`tables.md`, l. 290) : lignes répétées quatre fois (la colonne de la règle manque) et bornes hautes au-dessus de 1.

**7. Résumé : « every write checked » est faux, et « 14,265 episodes » est le nombre joué, pas analysé.**
- Texte : l. 21.
- Preuve : couverture 98,68 % (`decision.csv`), 92,5 à 93 % en banque (l. 240). L'audit du 14/11 l'avait relevé (constat 24). 14 265 parties jouées ; 91 exclues ; 12 tâches retirées. `reussite_taches.csv` : 13 623 parties dans les deux moitiés.
- Correction : « 14,265 episodes played (13,623 analysed after exclusions and removed tasks), with every write made with a mapped tool checked by exact comparison (98.7 % of writes) and every alert reviewed on blind sheets ».

**8. Le résumé omet la troisième phrase obligatoire de `FORMULATION_VERDICT.md` et « l'utilité non jugée ».**
- Preuve : `FORMULATION_VERDICT.md` l. 24-25 (« its usefulness could not be judged » ; « What an error is here […] 3 of 10 confirmed alerts were lifted ») ; `PLAN_ARTICLE.md` l. 17 (le résumé finit par « ce que veut dire une erreur »). Le résumé (l. 21) et la conclusion (l. 388) ne disent ni l'un ni l'autre. « Results in brief » (l. 37) dit l'utilité, pas le sens d'une erreur, et omet les 13 types sans erreur.
- Correction, à ajouter au résumé : « Its usefulness could not be judged. These rates count action errors confirmed by review against a single expected path per task; in a blind sample reviewed by the author, 3 of 10 confirmed alerts were lifted. » Même ajout, en court, dans la conclusion.

**9. Discussion, « Implications for practice » : une alternative fausse.**
- Texte : l. 344, « the types without observed errors had too few writes, and the types with enough writes had established excesses ».
- Preuve : `ecart.csv`, principal. 7 types indéterminés ont des erreurs sans dépassement établi : WorkBench/Haiku DUR (2 sur 523) et MSG (2 sur 292, soit 0,68 % sous la barre de 0,76 %) ; aviation/Haiku DUR (1 sur 49) ; banque/Haiku ECR (3 sur 152) ; banque/Opus ECR (12 sur 74) ; commerce/Haiku ECR (20 sur 632) et Opus ECR (5 sur 132). Un seul type a « assez de volume » au sens du plan.
- Correction : « no action type could have been delegated with evidence: 13 types had no observed error but too few writes, 7 had errors without an established excess, and 20 had established excesses, only one of them on a type with enough volume to be judged. »

**10. CASE : la discussion contredit la section 2 et prête à CASE un résultat que rien ne teste.**
- Texte : l. 342, « Our N is one way to make such a function explicit per action type » ; « a budget-driven rule of either kind would keep most write types under human validation ». `controle_fr.md` l. 31, « notre N est une façon de le dire ».
- Preuve : l. 49 dit « the mechanism differs » : CASE module l'autonomie par le budget **restant** (Éq. 7), notre N est fixé d'avance et le retrait suit la première erreur. Notre règle n'est donc pas une fonction g du budget restant. Fiche CASE, section 3 : ni g ni le SLO ne sont spécifiés ; section 5 : le mécanisme n'est pas testé. Rien ne permet de dire ce qu'une règle CASE ferait.
- Correction : « Our N is a different way to tie autonomy to a budget: sized in advance, per action type, with a stated bound, rather than a function of the budget remaining. Our data say nothing about CASE's mechanism, whose function g and service-level objective are unspecified. » Français : « notre N est une autre façon de lier l'autonomie à un budget ».

**11. Les annexes A à F et sept tables citées n'existent pas dans le brouillon ; « Table 2 » désigne deux tables.**
- Preuve : le fichier finit aux références (l. 464). Sont cités sans exister dans le brouillon : annexes B (l. 312), C (l. 250, 278, 286), D (l. 236, 258, 304, 310), E (l. 242), F (l. 252, 388) ; tables 3, 4, 5, 6, 6 bis, 7, 8, 9, X1 à X6. « Table 2 » est la table des parties prévues (l. 147) et la table de décision (l. 260, renvois l. 312 et 336).
- Les tables existent dans `article/resultats/tables.md` et `tables_exploratoires.md`, sauf deux contenus introuvables : la ventilation des alertes par environnement (« Appendix E gives the breakdown per environment », l. 242) et la couverture par environnement (« Coverage is published per environment », l. 162).
- Correction : renuméroter la table de décision ; assembler les annexes ou écrire « (supplementary tables, `article/resultats/`) » ; produire la ventilation des alertes et la couverture par environnement, ou retirer les deux renvois.

**12. Fiabilité de la relecture : trois faits connus ne sont pas dits comme limites.**
- Rythme : 2 529 alertes en 1 428 lots et 2 h 05 à six instances, soit environ 32 s par lot (journal, ligne du 14/11, point 5). L'audit du 14/11 (constat 11) le juge « pas plausible » sans explication ; rien n'indique qu'il ait été levé. D7 (l. 403) donne les chiffres sans la réserve.
- Sens des désaccords : la section 6.1 (l. 244) ne dit pas que, sur les 4 désaccords, 3 sont des confirmées levées par l'auteur et 1 une levée jugée vraie erreur (`SUIVI.md` l. 378, fiche 1 de la vague 2). Une levée à tort joue vers la délégation ; 770 alertes sur 2 761 sont levées (28 %), dont 283 pour un défaut de notre comparaison.
- Correction (limite 9 ou 23) : « Wave-2 batches closed in about 32 s each on average, which we could not explain; whether every sheet was read in full is not established. Of the author's four disagreements, three lifted a confirmed alert and one confirmed a lifted alert; 28 % of all alerts were lifted, so wrongly lifted alerts, which favour delegation, cannot be excluded either. »

**13. Registre des sources (règle R6) : beaucoup de chiffres des sections 6 à 8 n'y sont pas.**
- Preuve : `sources_chiffres.csv` compte 67 lignes. Absents, bien que je les aie retrouvés dans les CSV : effectifs des 13 types sans erreur (l. 288) ; taux, bornes et écritures par type (l. 292-296) ; ρ̂ par environnement (l. 298) ; s ÷ q 0,72 à 1,14 ; 6,6 et 6,1 fois ; c* = 3,77 ; charges 84 à 86, 90 à 94, 98 à 100 ; charges et dégâts du commerce (l. 312) ; épreuves (l. 318) ; 78, 10 et 13 cellules ; 0,23 à 0,65 et 0,43 à 1,06 ; 0,19 ; symétrie (l. 248) ; 64 à 82 % ; 31 à 79 % ; 24 erreurs ajoutées ; volumes 34 à 394 ; 1 380 contre 276.
- Absents et non vérifiables par moi : 4 parties arrêtées aux 100 tours en vague 1 et « none without a name in wave 1 » (l. 234, 236) ; 232 alertes et 9 exclusions en vague 1 (déduits).
- Présents seulement dans `SUIVI.md` : 883,50 $, 209 000 appels, 14,77 $, 15 parties arrêtées dont 10 Opus, 13 081, 1 428 lots.
- Correction : compléter le registre avant la mise en page.

**14. Des analyses annoncées en section 5 ne sont pas rapportées en section 6.**
- Texte : l. 190 (« Reported without effect on the label: approve everything; autonomy after three successes; […] a retrospective oracle ») ; l. 224 (« sensitivity to episode order »).
- Preuve : aucun de ces résultats en section 6. Les données existent dans `budget.csv` (par exemple « trois réussites », WorkBench/Haiku : 3,30 dégâts en plus pour 100, 6,6 fois le budget). Aucune analyse de l'ordre des parties n'apparaît dans les sorties lues (`budget.csv` : principale, verdicts bruts, toute la réserve, échange des rôles, lettre d'origine).
- Autre omission : B-régulier a 4 dépassements établis sous retard10 (pire borne 7,87 fois ; `resistance.csv`) et 4 lignes « échoue » dans `derive.csv`. La section 6.7 (l. 324) ne donne que son résultat principal. C'est pourtant ce qui justifie le choix de B-tout avant le gel (l. 133).
- Correction : une phrase par analyse, ou un renvoi explicite à une table d'annexe ; dire si la sensibilité à l'ordre a été calculée.

**15. Discussion : la robustesse à enjeu fort est dite trop vite.**
- Texte : l. 338, « The high-stakes rates are robust in order of magnitude: on airline and retail they stay established above their bars if 31 % to 79 % of confirmed errors were false […], and in the author's blind review 3 of 10 confirmed alerts were lifted ».
- Preuve : 3 sur 10 fait 30 %, intervalle exact à 95 % de 7 à 65 % (audit des résultats, constat 8). En aviation les seuils sont 31 %, 48 % et 55 % (`C_sensibilite_fausses_confirmations.csv`) : l'échantillon ne les exclut pas. L'audit des résultats écrit que les trois levées sont à enjeu fort ; `SUIVI.md` l. 378 décrit celle de la vague 2 comme une fiche de banque levée en (c). À vérifier dans `accord.json`, hors de mon périmètre.
- Correction : « The high-stakes rates keep their order of magnitude: on retail they stay established with up to 70 % to 79 % false confirmations. On airline the margin is thinner (31 % to 55 %), within what the author's blind sample allows (3 of 10 confirmed alerts lifted; exact 95 % interval 7 % to 65 %). »

### C. Mineurs

**16. Le critère de jugeabilité est écrit de façon approchée, et un chiffre le contredit.**
- Texte : l. 258, « n_eff × bar = 0.740 against ln 2 = 0.693 » ; l. 326 et 381, WorkBench/Opus en verdicts bruts « judgeable at 0.693, exactly at the threshold ».
- Preuve : le critère exact est 1 − 2^(−1/n_eff) ≤ barre, soit ici n_eff × barre ≥ 0,6905. `ecart.csv`, verdicts bruts, WorkBench/Opus ECR : 0,69301, sous ln 2 = 0,69315, et pourtant jugeable. Le seuil ρ̂ ≤ 0,885 correspond au critère exact (0,881 avec ln 2).
- Correction : « n_eff × bar = 0.740 against a threshold of 0.6905 (about ln 2) » ; « judgeable at 0.6930 against 0.6905, a margin of 0.4 % ». Même retouche dans `FORMULATION_VERDICT.md` l. 30.

**17. Coûts : trois petits écarts.**
- 72,13 + 765,07 = 837,20, pas 837,19 (l. 238 ; registre, ligne `cout_total_usd`). Écrire « 837.19 $ (sum of unrounded amounts) » ou 837,20.
- l. 234 « 72.10 $ spent » contre l. 238 « wave 1: 72.13 $ ». Dire lequel est le montant à l'arrêt.
- L'arrêt à 72,00 $ correspond à un plafond de 90 $ (`SUIVI.md` l. 294), pas à 1,5 fois 60,53 $ = 90,80 $ comme le dit la section 4.4 (l. 170). Ajouter « (cap set at 90 $) ».

**18. Une partie prévue n'a jamais été jouée, sans écart déclaré.**
- Preuve : 14 266 prévues, 14 265 jouées (l. 234, « was not in its plan file »). Dire quelle configuration, et l'inscrire aux écarts.

**19. « 3 lifted by the author outside any written reason » : D4 n'en décrit que deux.**
- Preuve : l. 242 et l. 400. Journal (ligne « 10/11 et 14/11 ») : fiches 2 et 4 de la vague 1. La troisième est la fiche 14 de la vague 2, levée en (c) selon `SUIVI.md` l. 378 ; le moteur la range « sans motif ».
- Correction : « two lifted outside any written reason (wave 1) and one lifted by the author under reason (c) (wave 2); the engine labels all three "author's lift" ».

**20. Échecs techniques de la vague 2 : 226 (D10, l. 406 ; journal) contre 228 (`SUIVI.md` l. 369).** À trancher sur `rapport_vague.txt`.

**21. GAR mal glosé.** l. 288, « irreversible high-stakes writes (GAR) ». GAR est « garde-fou ou droits » (plan 5.3 ; l. 75). Écrire « guardrail or rights (GAR) ».

**22. Arrondis.** l. 278 « at most 0.38 » : le maximum est 0,381. `controle_fr.md` l. 23 « sous 0,38 » est donc faux au sens strict ; écrire « au plus 0,38 ». l. 312 : c* = 3,77 vaut pour la liste fixe ; 3,73 pour le tri (`decision.csv`).

**23. Renvoi sans objet et formule de R8.** l. 200 et 204 : « Section 6.2 states what it means here ». La section 6.2 ne parle pas du nom préenregistré ; l'explication est en section 7 (l. 336) et dans la limite 21. Renvoyer à la section 7. l. 35 : « nothing to delegate » figure dans une liste sans définition ; écrire « no delegable configuration (label R4) ».

**24. Conclusion.** l. 388 : « no configuration earned delegation » perd le dénominateur (`FORMULATION_VERDICT.md` l. 13 : « le 12 reste toujours ») ; « the one configuration […] is established above its bar » : c'est le taux d'un type. Écrire « none of the twelve configurations earned delegation: in the one that could be judged, the error rate of reversible writes is established above its bar ». Même remarque, plus légère, pour « its error rate » du résumé.

**25. Limite 31 : « because of its volume, not because of its errors ».** La jugeabilité dépend de ρ̂, donc des erreurs. WorkBench/Opus et Sonnet (ρ̂ = 1,0 sur 10 et 11 erreurs) seraient jugeables si ρ̂ < 0,78 (audit des résultats, constat 2). Écrire « mainly because of its volume; judgeability also depends on the estimated correlation ».

**26. Intervalle de ρ̂.** l. 258 et 372 : l'intervalle 0,660 à 0,924 et les 9,6 % viennent d'une reconstruction centrée sur 0,800, pas sur le 0,819 du moteur (`RESUME.md`, point G). Le dire dans le texte ; la part au-dessus de 0,885 est sans doute sous-estimée.

**27. Commerce : la baisse ne vient pas du seul palier 3.** l. 310. `volume.csv` : palier 2 pour 34 %, 20 % et 43 % des écritures ECR. Écrire « from tier 3 and tier 2 ».

**28. Couverture.** l. 240, « every unverifiable write is an `unknown` write on banking », contre D6 (l. 402) : deux noms inventés en commerce restent aussi sans verdict.

**29. D12 incomplet.** Le journal (17/11) dit que les sorties partielles du premier passage sont gardées « sans être lues ». L'audit des résultats (constat 18) demandait de le reprendre. Ajouter : « The partial outputs of the failed run were kept unread; only their fingerprints were compared. »

**30. Dépôts OSF.** Non déclaré : les enregistrements du gel ont été soumis par l'assistant dans le navigateur, et cusv6 est sous embargo jusqu'au 04/11/2030 (`PLAN_SUITE.md` l. 50 ; audit du 14/11, constat 6). « Anyone can redo the draw » (l. 176) n'est vrai qu'à la levée de l'embargo.

**31. Règle de ρ̂.** l. 298 omet le plancher de 0,3 et « le plus grand des deux » (plan 5.13).

**32. Point 2 non jugé.** La section 5.2 ne dit pas que le point 2 n'est pas jugé sans configuration délégable. La section 6.5 (l. 308) cite « 5.14, Q15 » ; la source est 5.14, point 4.

**33. « 27 cells […] the airline, retail and banking/Sonnet configurations and their model-change scenarios »** (l. 272). Le compte est exact. Mais seule aviation/Haiku est concernée en aviation, et les scénarios de banque ne sont pas « fragile ». Écrire « airline/Haiku, the three retail configurations, banking/Sonnet, and the airline and retail scenarios ».

**34. Vocabulaire.** « witnesses » (sections 6 à 8) contre « comparators » (section 5) ; « risk-sorted list » (l. 267) contre « risk triage » ; « chance at the same pace » contre « random delegation at the same rate » ; « $ » contre « USD ». Choisir un terme.

**35. Résumé et discussion : « than current benchmarks provide ».** l. 21, 344, 388. Le volume dépend aussi du nombre de passages choisi. Écrire « than these benchmarks provide at our volumes ».

**36. `controle_fr.md`.**
- l. 35 : dit deux marques pour les limites ; il y en a trois (la limite 20 est « ajoutée après le gel »).
- l. 39 : D0 (gel avorté) et D8 (page simplifiée en vague 2) ne sont pas décrits.
- Il ne couvre pas « Results in brief » ni les sections 2 à 5 (R10) : la garantie de 3.4 et les paragraphes sur Zhang et Zhang et CASE ne sont pas validables en français.
- Il reprend les défauts des constats 2, 10 et 22.

**37. `FORMULATION_VERDICT.md` l. 29.** « délégable […] si chacun de ses types jugeables a un taux médian […] » contredit le plan 5.13 (« au moins un type mérité ») et le brouillon (l. 198), qui sont justes. Fichier de référence à corriger.

**38. Citations : fidèles, trois réserves légères.**
- Zhang et Zhang : toutes les affirmations (l. 51, 53, 83, 342) suivent la fiche et ses nuances. Omission possible : ils critiquent explicitement les échelles d'« earned autonomy » sans plafond terminal (VII.a, p. 5 ; tableau II, p. 6). Une phrase éviterait le reproche : « Their objection to earned-autonomy ladders targets ladders with no terminal ceiling; ours terminates beneath caps that no evidence lifts. »
- CASE, section 2 (l. 49) : conforme à la fiche, pages comprises. Voir le constat 10 pour la discussion.
- Contrôle qualité (l. 29, 45, 129) : conforme à `verif_originaux.md`. Hillier « pp. 161-163 » : la fiche ne donne que la p. 161 et la section 3. Les phrases sur Hryniewicz (2011) et Rodriguez et Jeske (2018) n'ont pas de ligne dans `verif_originaux.md` : non vérifiées ici.
- `PLAN_ARTICLE.md` l. 19 prévoit « préenregistrement d'expériences avec agents (arXiv 2606.11217) » ; absent de la section 2 et des références.

---

## Ce qui est vérifié et conforme

**Chiffres recalculés, sans écart.**
- R4 : 914 écritures, 79 erreurs, 8,64 %, barre 0,757 %, borne basse 4,14 % (recalculée avec scipy : 0,041415), borne haute 15,6 %, n_eff × barre 0,740, ρ̂ 0,819, seuil 0,885, 134 tâches porteuses.
- Écart : 40 types, 20 au-dessus, 20 indéterminés, 13 sans erreur (les 13 effectifs de la l. 288 sont exacts), 1 067 erreurs, 21 sous ρ̂, bascule à 0,924, 7 faible, 3 moyen, 10 fort.
- Tous les taux, bornes, effectifs et rapports des l. 292 à 298 ; volumes de certification 34 à 394 et 7 348 à 36 009.
- Réserve entière : 22 sur 41, trois types délégables (0 sur 120, 0 sur 120, 0 sur 258), commerce/Haiku 31 sur 1 286.
- Point 1 : 180 cellules, 51, 108, 21 ; 6 non testables (5 et 1) ; c* = 7,01 ; bornes max-T toutes négatives ; 1,67 fois (2 tâches) ; s ÷ q 0,72 à 1,14 ; 27 « fragile » (l'audit des résultats disait 29 : c'est lui qui se trompait).
- Témoins : 9 et 18 cellules, soit 1 et 2 configurations plus 8 et 16 scénarios ; 5,5, 5,8 et 10,2 ; 6,6 et 6,1 fois ; commerce 0,31, 0, 0,70 contre 0,13, 0, 0,14 ; charges 83,4, 82,5, 81,9 contre 84,4, 84,1, 85,8.
- Charges 65,5, 54,9, 55,1 ; palier 2 à 63, 81 et 81 % ; promotions 1 à 5 ; épreuves (168, 106, toutes les fourchettes) ; 100 lignes de `derive.csv`, toutes « passe ».
- Règles secondaires, tests de résistance (sept modes, toutes les fourchettes), symétrie, réussite des tâches, audit 0 sur 21 (borne 13,3 %), tirage (cusv6, impulsion 2031457, empreinte).
- Exploratoire : 91 exclusions (77, 10, 2, 2 ; 9 et 82), 24 erreurs ajoutées, 20 → 21, 63 %, 0 %, 104 sur 1 067, 4,6 à 6,2, 64 à 82 %, 9,6 %.
- Alertes : 2 761 = 1 991 + 770 ; 75 + 78 + 331 + 283 + 3 = 770 ; 12 tâches retirées (6, 5, 1).

**Fidélité au plan.** Délégable, jugeable, conditions (i) et (ii) de R4, ordre des étiquettes, point 0, point 1 (cellules « tenues, non mises à l'épreuve », non testables, F3), critère de retrait comme contrôle du code, point 2 non jugé, hasard « non calculable », définition des témoins : conformes à 1.4, 1.5 et 5.14. La table de décision (l. 262-270) traduit `decision.csv` sans reprendre « battu ».

**Sur-affirmation (R8).** Aucune occurrence fautive de « keeps the budget », « beats », « times the bar » en fourchette, ni de classement des modèles. « Nothing to delegate » n'apparaît que comme nom préenregistré ou pour être nié (sauf l. 35, constat 23). Les limites 21 à 31 couvrent les dix points de « Ce qu'on ne peut pas affirmer ».

**Écarts.** Chaque ligne du journal datée du 10/11 ou après a son écart : 10/11 soir (D1, D2, D3), 13/11 (D7, D8, D6), 10 et 14/11 (D4), 14/11 (D9, D7, D11, D10, D11), 17/11 (D12, D13). D5 (coût) est déclaré sans ligne au journal. Numérotation D0 à D13 continue ; limites 1 à 31 continues ; les renvois « limitation n » et « Dn » du texte tombent juste.

---

## Verdict

**Validable après corrections mineures**, au sens suivant : aucune analyse n'est à refaire, aucun chiffre porteur n'est faux, et le sens donné à R4 est juste. Les corrections sont des retouches de phrases. Mais deux d'entre elles sont bloquantes et treize importantes : le fond ne doit pas être validé sur le texte actuel, ni sur `controle_fr.md` tel quel.

### À corriger avant la validation d'Otsoa

1. Supprimer la ligne 230 (constat 1).
2. Réécrire la section 6.6, la limite 29 et la ligne 26 du contrôle français d'après `retrait.csv` (constat 2).
3. Corriger les deux phrases fausses sur les cellules jugées : l. 316 et l. 340 (constats 3 et 4).
4. Dire que la borne de construction dépasse le budget dans 24 cellules jugées ; mettre à jour la limite 12 (constat 5).
5. Rapporter la mesure de la garantie et nuancer la l. 312 (constat 6).
6. Résumé : « every write checked », 14 265 joué contre 13 623 analysé, phrase sur le sens d'une erreur, utilité non jugée (constats 7 et 8).
7. Discussion : alternative fausse de la l. 344, phrases sur CASE, robustesse à enjeu fort (constats 9, 10 et 15).
8. Limite sur la relecture : 32 s par lot, sens des quatre désaccords (constat 12).
9. Critère de jugeabilité exact : 0,6905 (constat 16).
10. Reporter dans `controle_fr.md` les corrections 2, 4, 5, 6 et 7, puis le remontrer à Otsoa.

### À faire avant la mise en page, sans bloquer la validation du fond

11. Annexes, numéros de tables, ventilation des alertes et couverture par environnement (constat 11).
12. Compléter `sources_chiffres.csv` (constat 13).
13. Analyses annoncées et non rapportées ; B-régulier sous retard10 (constat 14).
14. Mineurs 17 à 38.
