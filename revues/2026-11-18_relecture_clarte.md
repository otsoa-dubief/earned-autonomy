# Relecture clarté et présentation — 18 novembre 2026

Objet : `article/latex/main.pdf` (51 pages ; corps p. 1-7, déclarations p. 7-8, références p. 8-10, annexes A à F p. 11-51).
Point de vue : chercheur en agents IA, pas statisticien, qui découvre le sujet.
Méthode : lecture intégrale du texte extrait du PDF, rendu en image des pages 1, 5, 6, 15, 22, 29, 30, 34, 40, contrôle des renvois dans les sources LaTeX. Aucun fichier modifié hors ce rapport. Rien ouvert dans `experience/`, `donnees/`, `pilote/`, `data/`, `notes/`.

## Verdict

Le fond est honnête et l'introduction donne la question, la règle et le résultat ; mais le corps ne se lit pas seul : une dizaine de termes porteurs du verdict (ρ, n_eff, R5, R2, « point 1 », « judgeable », « without object »…) ne sont jamais définis dans les 7 pages, et le vocabulaire change entre corps et annexes.
Les annexes sont un versement brut de la version longue : numérotation héritée (B.3, C.5), deux « Table 2 », tableaux en police illisible, résidus de français, mathématiques non composées. À reprendre avant dépôt.

---

## Constats bloquants

### B1. Sigles et symboles du verdict jamais définis dans le corps
Un lecteur ne peut pas reconstituer pourquoi le label est R4.

| Terme | Où (PDF) | Citation exacte | Problème | Correction |
|---|---|---|---|---|
| ρ, ρ = 1 | p. 4, § 5 | « one-sided 95 % Clopper–Pearson lower bound at ρ = 1 lies above its bar » | ρ n'est défini nulle part dans le corps. Première définition p. 24 (« estimated within-task correlation ρ̂ »). | Ajouter en § 5 : « ρ is the within-task correlation of errors; ρ = 1 is the most conservative case (one independent observation per task) ». |
| n_eff | p. 3, § 5 | « (n_eff × bar ≥ 0.6905, about ln 2) » | Jamais défini, ni dans le corps ni en annexe (aucune formule de la taille effective dans les 51 pages). | Donner la formule une fois (annexe C.5.2) et une phrase dans le corps : « n_eff is the number of writes discounted for within-task correlation ». |
| R5, R2 | p. 4, § 5 | « Order: R5, R1, insufficient evidence, R4, R2, confirmed. » | R5 et R2 ne sont jamais expliqués dans le corps. R1 l'est à moitié. | Remplacer la phrase par un tableau de 6 lignes : label, nom en clair, condition. |
| R4 | p. 1, résumé | « (pre-registered verdict R4) » | Un code interne dans le résumé, sans sens. | Résumé : supprimer « R4 » ou écrire « (label "no delegable configuration, excess established") ». |
| Point 1, Point 2 | p. 4, § 6.3 et 6.5 | « Point 1 is held in the sense of “not refuted” » ; « Point 2 is not judged under R4 » | Le § 5 parle de H1 et H2, pas de points 1 et 2. Seul « Point 0 » y figure. | Choisir un seul nom. Garder H1 (safety) et H2 (utility) partout. |
| judged / held / without object | p. 4, § 6.3 | « 51 were judged (all at low stakes), 108 held without being put to the test and 21 were without object » | Trois catégories non définies dans le corps. « Without object » est un calque de « sans objet ». | Définir en une phrase : judged = la règle a atteint le palier 3 ; not exercised = jamais atteint ; not applicable = aucune écriture de ce niveau. |
| AOQL, UAOQL | p. 1 résumé ; p. 2, § 2 | « adapting the unrestricted AOQL of continuous sampling plans » | Sigle jamais développé dans tout le document. | « average outgoing quality limit (AOQL) » à la première occurrence ; hors résumé de préférence. |
| max-T, c* | p. 3-4 | « B-all has no established budget excess (max-T) » ; « (c* = 7.0) » | max-T cité sans dire ce que c'est ; c* sans définition. | Une phrase : « a resampling-based correction for testing many cells at once (Westfall–Young max-T); c* is its critical value ». |
| trial, secondary reading, stress-test alert, delay10, role swap, raw verdicts, oracle, construction bound, mix gap | p. 3, 4, 6 | « (to tier 1 with a trial at medium and high stakes) » ; « in the secondary reading (point estimate above the bar) » ; « 2.34 under delay10, 0 failures » ; « Raw verdicts and the role swap also give R4 » | Noms d'analyses internes, sans définition dans le corps. | Soit une demi-phrase de définition, soit couper (voir I9). |

### B2. Le rôle des deux moitiés et des trois « vérificateurs » n'est pas compréhensible à la première lecture
- p. 3, § 4 : « a calibration half, which measures each configuration's error rate by type and decides delegability, and a confirmation half, where the frozen rule is replayed once ».
- Le lecteur croit que la règle (N succès consécutifs) décide de la délégation. Or le label dépend d'un autre critère, statistique, sur la moitié calibration (« delegable », « judgeable »). Ce double mécanisme n'est jamais dit en clair.
- Quatre acteurs de contrôle se mélangent : « automated check » (comparaison exacte), « fresh Claude instances » (relecture des alertes), « the author » (relecture à l'aveugle), « simulated validator » (humain simulé du rejeu, rate 5 %). Le mot « verdict » désigne tantôt le jugement d'une écriture (« confirmed verdicts »), tantôt le label (« pre-registered verdict R4 »).
- Correction : un schéma d'une demi-colonne (épisodes → contrôle automatique → relecture des alertes → gel → tirage → moitié calibration : taux par type et label ; moitié confirmation : rejeu de la règle, H1/H2). Réserver « verdict » aux écritures et « label » au résultat. Ce schéma vaut plus que la figure 1.

### B3. Trois facteurs 0,95 dans le corps, un seul nommé
- p. 3, § 3 : « bar = B/(0.95 × 100 × q) […] N = ⌈1/(d × bar)⌉ − 1 with d = 0.95 the assumed detection share » puis « the extra errors stay below 0.95 × budget × s/q ».
- Le premier 0,95 n'est pas expliqué dans le corps. L'annexe (p. 16) dit elle-même : « Two 0.95 factors must be kept apart: the validator's stop rate (1 − e, inside the bar) and the detection share d (inside N) ». Le symbole e n'apparaît jamais dans le corps.
- Correction : écrire bar = B / ((1 − e) × 100 × q) avec « e = 5 %: share of errors the simulated human validator misses », et donner un exemple chiffré (WorkBench, niveau bas : budget 0,5 → barre 0,76 % → N = 138). Sans exemple, le lecteur ne relie pas « 0.5 per 100 writes » à « 0.76 % bar ».

### B4. Deux tableaux portent le numéro 2 ; tableaux sans numéro ; ordre cassé
- p. 17 : « Table 2. Planned episodes (frozen). »
- p. 22 : « Decision table (Table 2, from decision.csv). »
- p. 25 : « The 9 and 18 cells counted in Table 2 » (ambigu : lequel ?).
- Ordre d'apparition p. 27-41 : 4, sans numéro (task success), 5, 6, 6 bis, 7 bis, 7, G, 3, 8, sans numéro (Trials), sans numéro (Secondary rules), 9. Puis X1 à X6.
- Trois tableaux sans numéro : p. 28 « Task success rate per model and environment », p. 39 « Trials (B-all, configurations; epreuves.csv…) », p. 40 « Secondary rules and choice rule ».
- Correction : numérotation unique et continue (A1…An) dans l'ordre d'appel ; « 6 bis » → 6b ; « G » et « X1-X6 » fondus dans la série.

### B5. Tableaux illisibles (taille de police)
- p. 30, Table 6 : 16 colonnes, corps d'environ 4 points. Illisible à l'impression et à l'écran sans zoom à 300 %. C'est le tableau principal du résultat.
- p. 29, Table 5 : même taille, 24 lignes presque toutes à 0, puis trois quarts de page blanche.
- p. 40, « Secondary rules » : même taille, 5 lignes.
- p. 27, Table 4 et p. 38, Table 8 : idem.
- Correction : Table 6 en paysage, ou retirer 5 colonnes (rate/bar, n_eff, ρ̂, judgeable, note → une seule colonne « class »). Tables 5, 8, G : ne garder que les lignes non nulles et dire le reste en une phrase.

### B6. Mathématiques non composées
- p. 3 : « N = ⌈1/(d × bar)⌉ − 1 », « 1/(1 + N d) », variables en romain.
- p. 15 : « bar(ℓ, e) = B_ℓ / (0.95 × 100 × q(ℓ, e)) », « NˆN / (N + 1)ˆ(N+1) ≤ d × bar » (accents circonflexes visibles), « (p_good, p_bad) ».
- p. 4, 22, 30 : « n_eff × bar » avec tiret bas apparent ; p. 20 : « T*_c », « estimate_c − c* × SD_c ».
- Pour un atelier ML, c'est le défaut le plus visible. Correction : passer toutes les formules en mode mathématique (`$N$`, `$n_{\mathrm{eff}}$`, `$N^N/(N+1)^{N+1}$`), formules principales en équations numérotées.

### B7. Résidus de français dans le PDF
- p. 40 : « (résultat) » et « charge moyenne non calculable (aucune configuration délégable) ».
- p. 27 : « (resistance.csv, “bilan du mode” rows) ».
- Sigles de types français utilisés jusque dans la figure 2 : ECR, DUR, ARG, GAR, ILL (p. 2 : « reversible write ECR […] money ARG, guardrail or rights GAR, illegible effect ILL »). Un lecteur anglophone ne peut pas deviner ARG = money.
- Correction : traduire les deux cellules ; renommer les codes (REV, DUR, MSG, MON, GRD, OPQ) ou écrire les noms en clair sur l'axe de la figure 2.

---

## Constats importants

### I1. « 40 action types » est trompeur
- p. 1 : « Descriptively, 20 of 40 action types have an error rate established above their threshold » ; p. 2 : « Across 40 observed action types » ; p. 4 : « 20 of 40 types ».
- Il y a une dizaine de types. 40 est le nombre de couples (modèle, environnement, type).
- Correction : « 20 of the 40 model–environment–type combinations ».
- Même glissement p. 1 : « Only one of twelve configurations had enough volume to be judged; its error rate, 8.6% » : c'est le taux d'un type (écritures réversibles), pas de la configuration. Écrire « its reversible writes err 8.6% », comme p. 2.

### I2. Vocabulaire qui change entre corps et annexes
| Corps | Annexes | Endroit |
|---|---|---|
| comparators | witnesses (calque de « témoins ») | p. 23 « 2. Witnesses », p. 25 « The witnesses' excesses » |
| risk triage | risk-based triage ; « the risk-sorted list » | p. 19, p. 23 |
| random delegation | « Chance at the same pace » | p. 23, p. 26 |
| simulated user | simulated client | p. 4 (corps, une fois), p. 12, 24, 50 |
| bar | threshold | p. 1 résumé : « above the 0.76% threshold » |
| label | verdict | p. 1 : « pre-registered verdict R4 » |
| H1 / safety | point 1 / eliminatory criterion | p. 22-23 |
| pre-registered | preregistered | corps : 8 fois avec trait d'union ; annexes : 12 sans, 3 avec |
Correction : un glossaire d'une demi-page en tête d'annexe, et un seul terme par notion.

### I3. Calques du français qui gênent la lecture
- « without object » (p. 4, 22, 23, 29) → « not applicable ».
- « lifted » pour une alerte (partout ; p. 1 : « 3 of 10 confirmed alerts were lifted ») → « dismissed » ou « overturned ». Dans le résumé, « confirmed alerts were lifted » se lit comme une contradiction ; écrire « 3 of the 10 alerts the first reviewers had confirmed were overturned by the author ».
- « the reserve » (p. 3 : « The reserve is split by task ») : jamais défini dans le corps → « the held-out tasks (the 80 % not used in the pilot) ».
- « carrying tasks » (p. 20, 22, 23) : jamais défini → « tasks that contribute at least one write to the cell ».
- « The author opposed the removal » (p. 13) → « objected to ».
- « Dimensioning decides who can be judged » (p. 50) → « Sample sizing ».
- « played “dry” » (p. 14), « “the error stays” » (p. 14), « original letter (Q8 A) » (p. 23), « H1 can hardly fail through the data » (p. 4) → « the data can hardly falsify H1 ».
- « What bound the study was volume, not the bound. » (p. 6) : jeu sur deux sens de « bound », incompréhensible → « The limiting factor was volume, not the guarantee. »

### I4. Renvois cassés ou ambigus
- p. 2 : « (Section 6.4) ». Le corps n'a pas de sous-sections numérotées ; seulement des titres en gras « Delegation gap (6.4). ». Acceptable mais bancal ; « Utility and model changes (6.5–6.6) » et « Secondary analyses (6.7) » renvoient à la numérotation de la version longue.
- p. 3 : « (Section B.3.4) » ; p. 7 : « (Section B.4.3) ». L'annexe B commence à B.3 (pas de B.1 ni B.2) ; l'annexe C commence à C.5. Numérotation héritée des sections 3 à 6 de `brouillon.md`. Un lecteur cherche B.1.
- p. 23 : « on WorkBench and banking (Section 7) ». Dans ce PDF, la section 7 est la Discussion, qui ne parle pas de s/q. Le bon renvoi est l'annexe E, limite 12.
- p. 22, 23, 24 (à l'intérieur de l'annexe C) : « full table in Appendix C » ; « Table 5 (summary; full table in Appendix C) » ; « Full table: Table 6 (Appendix C) ». L'annexe se renvoie à elle-même. Donner le numéro de table et la page.
- p. 2 et p. 6 : « The extended version of this paper (article/brouillon.md in the code archive, Appendix F) » ; « The extended version of this paper (Appendix F) gives the full discussion ». Se lit comme si l'annexe F contenait la discussion ; elle ne contient qu'un chemin de fichier. Écrire « the extended version (in the code archive; see Appendix F for its location) ». Un fichier nommé « brouillon » comme version longue de référence fait mauvais effet : le renommer.
- p. 19-27 : renvois à un document que le lecteur n'a pas : « plan 1.4 » (4 fois), « (5.13) », « (5.14, Q15) », « plan 5.8 », « plan 5.11 », « plan 5.12 », « Q2 », « Q8 A », « decision 5 » (4 fois), « formula F3 », « F1 », « E1 », « G0 », « R0 », « case a3 ». Les retirer ou les regrouper dans une table de correspondance.
- p. 22-23, table de décision : les points vont 0, 1, 2, 3, 4, 6. Le point 5 manque sans explication.

### I5. Introduction : bonne, mais la contribution (3) est illisible
- p. 2 : « (3) A pre-registered protocol whose outcome was open, and which shows the volumes earned autonomy requires; the plan stated in advance that at these volumes no type could be certified below its bar and that the high-stakes run lengths exceed the data: plan, rule, code, seeds and labels were registered on OSF on 10 November 2026 at 05:00 UTC, before wave 1 started at 05:19 UTC; alerts are reviewed blind; the calibration/confirmation split is drawn from a public randomness beacon after the confirmed verdicts are frozen. »
- Environ 85 mots, deux points-virgules, deux deux-points. « wave 1 », « bar », « confirmed verdicts », « calibration/confirmation split » y sont employés avant d'être définis.
- Correction : « (3) A pre-registered protocol with an open outcome. Plan, rule, code and seeds were registered before data collection; alerts were reviewed blind; the data split was drawn from a public randomness beacon. The plan stated in advance that these volumes could not certify any type as safe. » Les heures UTC vont en annexe F.
- « Results in brief » (p. 2) : clair, sauf « (label R4) », « bar » (non défini à ce stade : ajouter « the maximum error rate the budget allows, the bar ») et « The safety criterion was not refuted, but with almost no power; utility could not be judged » (dire ce que sont ces deux critères en une demi-phrase).
- Bilan : à la fin de l'introduction, le lecteur a la question (oui), la règle (oui, très bien amenée par Dodge), le résultat (oui en gros). Il lui manque le sens de « bar » et de « judged ».

### I6. Résumé trop dense
- p. 1 : environ 230 mots, un seul bloc. « by adapting the unrestricted AOQL of continuous sampling plans, with a conditional bound on the extra errors delegation lets through » : incompréhensible hors du champ.
- Ordre des chiffres : « 14,265 episodes played (13,623 analysed), writes checked by exact comparison (98.7% coverage) » avant le résultat.
- Correction : retirer AOQL, R4 et la couverture ; garder règle, dispositif, résultat principal (1 sur 12 jugeable, 8,6 % contre 0,76 %), leçon (volumes). Viser 150 mots.

### I7. Figures
- Mise en page p. 5 : les figures 1 et 2 occupent une page entière avec environ 40 % de blanc. La phrase du § 6.5 est coupée entre p. 4 (« since they lack error ») et p. 6 (« feedback and tier 2 »). La figure 3 arrive p. 6.
- Figure 1 (p. 5) : presque tous les points sont à 0. Axe des abscisses sans étiquettes : on ne sait pas quelle cellule est laquelle. Les marqueurs creux ont trois formes, non expliquées (quel modèle pour un scénario à deux modèles ?). Information utile : une phrase. À couper en premier ou à remplacer par le schéma du protocole (B2).
- Figure 2 (p. 5) : la plus utile, à garder et agrandir. Défauts : étiquettes qui se chevauchent dans le panneau banking (« lowmediumhigh ») ; la note sous la légende chevauche la légende ; « n=2 » rogné au bord droit ; gris et noir indiscernables à cette taille ; codes ECR/ARG/GAR/ILL non parlants ; les intervalles qui descendent à 10⁻³ écrasent l'échelle ; la légende emploie « ρ = 1 interval » que le corps ne définit pas.
- Figure 3 (p. 6) : 12 configurations, 4 règles, mais les modèles ne sont pas distingués et la plupart des points s'empilent à (85-100 ; 0). Les deux marqueurs gris (fixed list, risk triage) se confondent. Lisible seulement pour WorkBench et banking. À réduire à ces deux panneaux ou à déplacer en annexe.
- Les trois figures sont citées dans le corps (p. 4). Aucune table dans le corps : une petite table « 12 configurations : volume, jugeable ?, résultat » manque.
- Annexe : p. 23-25, « Figure 1 (article/figures/fig1_budget.pdf) plots… » : chemins de fichiers dans le texte, à retirer.

### I8. Annexes : structure et répétitions
- Ordre : l'annexe A (écarts) vient avant B (règle, dispositif). Elle parle de G0, `banc/`, « reason (d) », « wave 2 » avant que le lecteur ne sache ce que c'est. Mettre B et C d'abord, ou ouvrir A par une table (identifiant, date, objet, effet sur le label).
- Annexe A, ton de journal de bord : D0 (gel avorté), D3 (p. 11 : « Wave 2 was first launched outside a terminal multiplexer and interrupted within a minute (exit code 130) »), D11 (p. 13 : « its embargo had already been approved by the author on the assistant's instruction »). Honnête, mais sans effet sur le label. Une ligne chacun suffit ; le récit va dans le dépôt.
- Tableaux un par page, p. 27-47 : 21 pages. Table 3 (p. 37) : 4 lignes sur une page entière. Table G (p. 34-36) : trois pages, presque toutes les lignes à « 0.000 [0.000 ; 0.000] ». Gain possible : environ 12 pages.
- Répétitions quasi mot pour mot :
  - paragraphe « No configuration reached the pre-registered level of evidence required for delegation… » : p. 1, 2, 4, 7, 22 (cinq fois) ;
  - « 3 of 10 confirmed alerts » : p. 1, 6, 7, 43, 50 ;
  - « 0.740 against 0.6905 … 0.885 » : p. 4, 22, 49 ;
  - liste « banking is where attribution to the agent is weakest: coverage 0.925, … » : p. 4, 24, 50 ;
  - exclusions (91 épisodes, 77 Haiku banking) : p. 4, 11 (D2), 12 (D10), 21, 37, 42, 48 ;
  - « 0.6930 against 0.6905 » : p. 26 et 50.
  - Les annexes A, C.6.1 et E se recoupent : renvoyer de E vers A et C au lieu de redire.
- p. 25 : « (The detail of the “point 2: success” line in decision.csv, “the three witnesses beaten”, is the wording of the criterion written into the engine's output, not a result.) » : incompréhensible pour un lecteur ; à couper.
- p. 20 : le paragraphe sur « formula F3 » et « F1 » (« The pre-set formula-choice rule, applied to the measurement draws only, designated F1, which over-rejected… ») ne se comprend pas sans le plan. À réécrire en trois phrases ou à couper.

### I9. Corps : ce qu'il faut couper en premier
Par ordre, pour un lecteur pressé :
1. § 6.7 « Secondary analyses » (p. 6) : « the stress-test alert fired in all seven modes, driven by one airline cell carried by 2 tasks (worst upper bound 1.65 to 1.68 times the budget, 2.34 under delay10, 0 failures) ». Jargon pur. Une phrase : « Secondary and stress analyses do not change the label (Appendix C). »
2. § 6.5-6.6, deuxième moitié (p. 6) : retrait après changement de modèle, « secondary reading », « 4.3 %, up to 11.8 % ». Renvoyer à l'annexe.
3. Figure 1 (voir I7).
4. § 6.2 (p. 4) : « Raw verdicts and the role swap also give R4, but they sit at the edge of the same threshold. »
5. § 5 « What the labels can mean » (p. 4) : utile mais abstrait avant les résultats ; le fusionner avec § 6.3.
6. Identifiants internes dans le corps : « (OSF cusv6) » p. 3, « (OSF u26kr by cusv6) » p. 7, « (D0 to D13) » p. 7, « named B-tout in the frozen plan » p. 3.
La place gagnée sert aux définitions de B1 et à l'exemple chiffré de B3.

### I10. Sections 7 et 8 : blocs sans respiration
- § 7 Discussion (p. 6) : un seul paragraphe d’environ 300 mots, six idées (portée de R4, volume, fausses confirmations, Zhang et Zhang, CASE, palier 2). Découper en trois paragraphes à titre en gras : « What R4 does and does not say », « Relation to prior work », « What it costs ».
- § 8 Limitations (p. 7) : première « phrase » d’environ 75 mots sans verbe, à points-virgules. « same-provider reviewers, whose wave-2 batches closed in about 32 s each » est cryptique. Mettre en liste de 5 limites principales, une ligne chacune.
- § 2 Related work (p. 2) : un seul paragraphe ; les titres en italique aident. Correct pour un atelier.

### I11. Références
- Liste numérotée [1] à [42], mais appels auteur-année dans le texte : les numéros ne servent à rien. Choisir un style.
- Environ 13 entrées ne sont citées nulle part dans le PDF : [1] Anthropic, [2] Arora, [10] El-Yaniv et Wiener, [13] Geifman, [14] Greenblatt, [17] Kapoor, [20] Liu, [23] Ou, [24] et [25] Pan, [26] Panossian, [28] Rodriguez et Jeske, [30] Shi (Progent), [34] Thomas. Elles viennent de la version longue. Les retirer ou les citer.
- [42] « Project materials » : pas une référence ; à mettre en note ou en annexe F.
- [9] : « [not read; volume and pages as given by Hryniewicz (2011)…] » : honnête, mais à dire dans le texte (c'est déjà fait p. 2 : « as reported by Hryniewicz, 2011 »), pas dans la bibliographie.

---

## Constats mineurs

- M1. Espace avant % (typographie française) dans le corps (« 8.6 % », « 95 % ») mais pas dans le résumé (« 8.6% », « 98.7% », p. 1). En anglais : jamais d'espace. Coupures disgracieuses : p. 20 « 4.7 / % cumulated », p. 22 « 99.3 / % on WorkBench », p. 25 « 2.4 / % ».
- M2. Intervalles « [4.1 ; 15.6] » avec point-virgule espacé (p. 24, tables) : usage français. → « [4.1, 15.6] ».
- M3. « ÷ » (p. 4 : « lower bound ÷ bar 2.7 to 5.5 ») → « lower bound / bar ».
- M4. Monnaie : « USD » dans le corps et l'annexe A, « $ » après le nombre en C.6.1 (p. 21 : « 72.10 $ spent against a 72.00 $ stop »).
- M5. Casse et ordre : « Airline, Retail, Banking » (Table 1, p. 15) contre « airline, retail, banking » ailleurs ; ordre des modèles haiku-opus-sonnet (Tables 6, 7) contre haiku-sonnet-opus (Tables 7 bis, G, trials) ; ordre des environnements variable.
- M6. Tables : booléens Python « True / False » (p. 30, 31, 40-42), identifiants « haiku-5-5 » au lieu de « Haiku 5.5 », « tiny n », « e=0 » contre « e = 0.02 » (p. 41).
- M7. Table 1 (p. 15) : barres en fractions (« 1/132 ») alors que tout le texte parle en pour cent (« 0.76 % bar »). Cellules repliées (« 1/12,020 (12,653; / 4,655) »). Donner fraction et pour cent, une colonne par règle.
- M8. Légendes contenant des chemins : p. 37 « experience/exploratoire/A_parties_exclues.csv », p. 38 « (derive.csv, main analysis…) », p. 39 « epreuves.csv », p. 42-47 noms de fichiers français. À sortir des légendes.
- M9. Légendes X1 à X6 : « (Exploratory, dated 17 November 2026; …) » répété six fois alors que l'en-tête de l'annexe D le dit déjà.
- M10. p. 16 et 19 : « A ½, A ¼ » composés en fractions empilées minuscules ; définis seulement p. 16. Écrire A(1/2), A(1/4).
- M11. p. 3 : « B-all (named B-tout in the frozen plan) » dans le corps : détail d'archive, à mettre en annexe F. Le nom « B-all » lui-même n'évoque rien ; « the strict rule » contre « the regular rule » serait plus parlant.
- M12. p. 1 : « Draft, 17 November 2026 » sous le titre ; à retirer au dépôt. Ligne « (frozen at git tag gel-2026-11-09) » : détail pour l'annexe F.
- M13. p. 7 : la déclaration d'usage d'IA cite la politique arXiv avec URL et date de lecture (4 lignes). Une phrase suffit.
- M14. p. 3 : « 14,266 episodes were planned » puis p. 4 « 14,265 episodes were played » : l'écart d'un épisode n'est expliqué qu'en p. 21. Ajouter « (one was missing from the plan file) » ou n'en donner qu'un.
- M15. p. 3 : « the τ-bench simulated user is Haiku 5.5 » et p. 3 « reviewed by fresh Claude instances on blind sheets » : « sheets » (fiches) → « anonymised records ».
- M16. p. 2 : la citation « (Dodge, 1943, p. 265) » avec pages dans l'introduction, « (Eq. 7, p. 10) », « (p. 11) » en § 2 : précision utile à l'audit, lourde à la lecture. Garder les pages en annexe.
- M17. p. 19 : « earned type » (« at least one earned type has a median calibration rate ») : terme non défini.
- M18. p. 22 : la table de décision se coupe entre p. 22 et p. 23 avec répétition de l'en-tête ; tenir sur une page.
- M19. Sections numérotées à la main (`\subsection{1 Introduction}`) : pas de renvois cliquables, pas de table des matières pour 40 pages d'annexes. Ajouter un sommaire des annexes p. 11.
- M20. Aucun débordement de marge signalé par LaTeX (0 « Overfull » dans `main.log`). Le seul rognage visible est « n=2 » dans la figure 2.

---

## Les 5 changements qui amélioreraient le plus l'article

1. **Définir une fois, dans le corps, les termes qui portent le verdict**, sous forme d'un encadré ou d'une table de dix lignes : bar, extra errors, cell, judgeable, delegable, established, ρ, n_eff, labels R1/R2/R4/R5 en clair. Retirer « R4 » et « AOQL » du résumé. Unifier H1/H2 contre « point 1/2 », « comparators » contre « witnesses », « label » contre « verdict ».
2. **Remplacer la figure 1 par un schéma du protocole** (contrôle automatique → relecture des alertes → gel → tirage → moitié calibration = label ; moitié confirmation = rejeu), avec les quatre vérificateurs nommés. Agrandir et nettoyer la figure 2. Ajouter une petite table des 12 configurations.
3. **Donner un exemple chiffré de bout en bout** (WorkBench, écritures réversibles : budget 0,5 pour 100 → barre 0,76 % → N = 138 → 8,6 % observé) et nommer le facteur e à côté de d. Composer toutes les formules en mode mathématique.
4. **Refaire les annexes comme des annexes, pas comme la version longue collée** : numérotation propre (B.1…, C.1…), tables numérotées en continu et dans l'ordre (plus de double « Table 2 », plus de tables sans numéro), Table 6 lisible, tables à zéros réduites aux lignes non nulles, renvois « plan 1.4 / Q15 / decision 5 / Section 7 » retirés ou corrigés, résidus de français traduits. Gain : une douzaine de pages.
5. **Alléger le corps de ce qu'un lecteur ne peut pas suivre** : § 6.7, la seconde moitié de § 6.5-6.6, les identifiants OSF et D0-D13 ; scinder la Discussion en trois paragraphes, les Limitations en liste, la contribution (3) en trois phrases ; remplacer « 40 action types » par « 40 model–environment–type combinations » et les calques (« without object », « lifted », « reserve », « carrying tasks »).
