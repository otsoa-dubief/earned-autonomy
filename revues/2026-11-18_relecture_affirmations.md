# Relecture « affirmations contre preuves » (18/11/2026)

Relecteur : Claude (Fable 5.2), instance séparée. Angle : écart entre ce que l'article affirme et ce qu'il prouve.

Lu : `article/latex/main.pdf` (texte extrait, 51 pages, en entier), `article/atelier.md`, `article/brouillon.md` (résumé, discussion, conclusion, déclarations), `PLAN_EXPERIENCE.md` (1.1 à 1.5, 2.4, 5.13, 5.14, section 6), `article/FORMULATION_VERDICT.md`, les deux rapports de recherche sur le verdict et le titre. Non ouvert : `experience/`, `donnees/`, `pilote/`, `data/`, `notes/`. Contrôle des chiffres non relancé. Tous les chiffres cités ci-dessous viennent du PDF lui-même.

## Verdict

L'article est honnête sur l'essentiel : R4 n'est ni gonflé ni minimisé, « not refuted, but hardly put to the test » est répété partout, le dénominateur 12 ne quitte jamais la phrase. Il reste un passage contredit par le tableau X2 de l'article (à corriger avant diffusion) et sept points où un chiffre de tête (20 sur 40, 8,6 %, « main lesson ») est cité sans la réserve que l'article donne ailleurs.

## Ce qui tient (vérifié, rien à changer)

- Résumé, « Results in brief », 6.2, conclusion : même phrase de verdict, conforme à `FORMULATION_VERDICT.md`. « Only one of twelve » y figure à chaque fois.
- H1 : « held in the sense of "not refuted", with almost no power » (6.3), c* = 7,0 donné dans le corps, « H1 can hardly fail through the data » dit en section 5.
- H2 : « not judged », « "validate everything" is not beaten », les dépassements des témoins présentés comme « an illustration of the gap, not a success of B-all ».
- Fragilité de R4 dans le corps (6.2) : 0,740 contre 0,6905, bascule à ρ̂ = 0,885, « post hoc » dit.
- Exploratoire marqué en 6.2, 6.4 (« descriptive »), 6.7, discussion (deux fois), légendes des figures 1 et 3.
- Titre : il décrit ce qui a été fait et n'annonce aucun résultat. Le résumé dit lui-même (« hardly put to the test ») que le test a peu tranché. Pas de constat.
- Aucun classement des trois modèles. La discussion le dit (« or which model is better »).

## Bloquant

### B1. « within what the author's blind sample allows » : contredit par le tableau X2

- Endroit : section 7 (Discussion), PDF p. 6. Même formule dans `brouillon.md`, section 7, pour l'aviation seule.
- Citation : « On airline and retail, high-stakes rates stay established with 31 % to 79 % false confirmations (exploratory, Appendix D), within what the author's blind sample allows (3 of 10 confirmed alerts lifted; 95 % interval 7 % to 65 %). »
- Problème. La phrase rassure. Les chiffres disent l'inverse. L'intervalle monte à 65 %. Les trois types d'aviation tolèrent 31 %, 48 % et 55 % (tableau X2) : tous sous 65 %. Le type qui porte R4 tolère 63 % : sous 65 % aussi. En tout, 9 des 20 dépassements établis ne tiennent pas au haut de l'intervalle (seuils 0, 30, 31, 41, 45, 47, 48, 55, 63 %). À la valeur centrale (30 %), aviation/Opus tient à un point près (31 %). L'échantillon compte 10 alertes, tous environnements confondus : il ne dit rien par type.
- Même défaut, plus discret : limite 23 et C.6.4 donnent « up to 63 % » sans le rapprocher de 65 %.
- Réécriture : « Table X2 (exploratory) gives, for each established excess, the share of confirmed errors that could be false alerts before the excess is lost: 70 % to 79 % on retail money-moving writes, 31 % to 55 % on airline, 63 % for the type that carries R4. The author's blind sample (3 of 10 confirmed alerts lifted; 95 % interval 7 % to 65 %, all environments pooled) is too small to rule such shares out: at its upper end, 9 of the 20 established excesses, including the one that carries R4, would no longer be established. »

## Important

### I1. Le nom préenregistré de R4 n'apparaît pas dans le corps, et le renvoi qui devait l'expliquer est vide

- Endroit : résumé, sections 1, 5, 6.2 (« label R4 », sans nom) ; annexe C.5.2, PDF p. 19.
- Citation (C.5.2) : « the label is R4 (preregistered name: "nothing to delegate, unreliability established"; Section C.6.2 states what it means here) ».
- Problème. Le plan figé nomme l'étiquette « R4, rien à déléguer : non-fiabilité établie » (1.5). Le corps ne donne jamais ce nom. C.6.2 ne le reprend pas non plus : le renvoi ne mène à rien. Un lecteur qui ouvre le dépôt OSF trouvera une étiquette plus forte que celle de l'article, sans explication dans les huit pages. L'adoucissement va dans le bon sens, mais il doit être déclaré. Le rapport « Formuler un verdict » demandait l'étiquette « mot pour mot, entre guillemets ».
- Réécriture (section 5, après « the label is R4 ») : « R4's registered name is "nothing to delegate: unreliability established". We keep the label and not the name as a description: what is established concerns one action type in one configuration (Section 6.2). »
- Et corriger le renvoi de C.5.2 vers la section 7 et la limite 21, qui font ce travail.

### I2. « 20 of 40 » cité sans sa composition : 11 des 20 sont en banque

- Endroit : résumé ; « Results in brief » ; section 7 ; section 9.
- Citations : « Descriptively, 20 of 40 action types have an error rate established above their threshold » (résumé) ; « Across 40 observed action types, 20 have an error rate established above their bar » (Results in brief, sans « descriptively ») ; « 20 had established excesses » (section 7).
- Problème. Compté dans le tableau 6 : 11 des 20 sont en banque, où l'article écrit lui-même « these rates therefore do not separate agent error from setup error ». 6 sont des écritures d'argent en aviation et en commerce, à des barres voisines de 0,008 %, où « the high-stakes ratios mostly measure the budget chosen ». 3 seulement sont à enjeu faible hors banque (WorkBench). Deux sont marginaux (banque/Opus MSG à 0,3 % près ; banque/Haiku ILL sur 2 écritures). Aucune correction pour 40 types. Et « 20 above, 0 below » est « partly built in » (C.6.4). Rien de cela n'accompagne le chiffre là où il est repris.
- Réécriture (résumé) : « Descriptively, and without multiplicity correction, 20 of 40 action types have an error rate established above their threshold (11 of them on banking, where agent and setup errors cannot be separated; 6 on money-moving writes whose thresholds are near 0.008 %); 13 show no observed error but too little volume; at these volumes none could have been shown below. »
- Réécriture (Results in brief) : ajouter « Descriptively, » en tête de la phrase et « (11 on banking, Section 6.4) » après « bar ».

### I3. « where it can be measured it is wide » : effet de sélection

- Endroit : section 9, PDF p. 7. Aussi `brouillon.md`, section 9.
- Citation : « The main lesson is the delegation gap: where it can be measured it is wide ».
- Problème. « Mesuré » veut dire ici « établi ». Or à ces volumes, seuls les grands écarts peuvent être établis (limite 11 : « Established excesses are detectable only when large »). Là où un taux est estimé sans être établi, l'écart est faible : commerce, écritures réversibles, 3,2 % et 3,8 % pour une barre à 2,6 % (ratio 1,2 à 1,4) ; WorkBench/Haiku, messages internes, ratio 0,90 (tableau 6). La phrase prend la conséquence du filtre pour un fait sur les agents.
- Réécriture : « The main descriptive result is the delegation gap: the excesses these volumes could establish are large (lower bound 2.7 to 5.5 times the bar on WorkBench reversible writes), smaller gaps could not be resolved either way, and no type could be shown below its bar. »

### I4. La « leçon principale » sur les volumes était écrite dans le plan ; elle n'est pas un résultat des données

- Endroit : résumé (dernière phrase) ; contribution 3 ; section 7 ; section 9.
- Citations : « Earning autonomy under such budgets takes far more verified actions than these benchmarks provide at our volumes. » ; « our rule is one instance, and our data show what it costs » ; « A pre-registered protocol whose outcome was open, and which shows the volumes earned autonomy requires ».
- Problème. Les longueurs N (12 à 12 653) découlent des budgets choisis par l'auteur, avant toute donnée (plan 1.2, 2.4 : « Personne n'atteint l'enjeu fort »). La contribution 3 l'admet à moitié (« the plan stated in advance… »). Deux formules restent trop fortes. (a) « our data show what it costs » : c'est le budget qui fixe le coût, pas les données. (b) « whose outcome was open » : onze configurations n'ont aucun type jugeable (tableau 6, n_eff × bar sous 0,6905), donc aucune ne pouvait être délégable, même sans une seule erreur. L'issue n'était ouverte que pour une configuration.
- Réécriture (résumé) : « As the plan stated in advance, earning autonomy under such budgets takes far more verified actions than our volumes on these benchmarks provide. »
- Réécriture (section 7) : « our rule is one instance; the budgets fix what it costs (Table 1), and our data show that agents erring several percent of the time rarely pay it. »
- Réécriture (contribution 3) : « A pre-registered protocol. Its label was open for the one configuration with enough volume; for the eleven others, volume excluded delegation whatever the error rate (Section 6.2). The plan stated in advance that… »
- `brouillon.md` va plus loin que l'atelier : « than current benchmarks offer » et « than current benchmarks give per configuration ». Le volume venait du budget de 1 100 USD (un passage pour Sonnet et Opus sur WorkBench), pas des bancs. Aligner sur « these benchmarks provide at our volumes ».

### I5. « err 8.6 % of the time » : la réserve la plus forte n'est pas à côté du chiffre

- Endroit : « Results in brief », PDF p. 2 ; section 6.2.
- Citation : « Only Haiku on WorkBench had enough volume to be judged, and its reversible writes err 8.6 % of the time against a 0.76 % bar. »
- Problème. Phrase la plus facile à reprendre hors contexte (« Claude Haiku se trompe 8,6 % du temps »). Sur ce même banc, le taux de tâches réussies de Haiku est de 97,0 % (calibration), et 63,9 % des parties avec une erreur confirmée sont des tâches réussies (tableau X3). Les verdicts par action de WorkBench sont « derived by us, not provided by the benchmark » (limite 20). Le corps ne garde que quatre mots : « confirmed errors inside successful tasks » (section 8), sans chiffre.
- Réécriture (Results in brief) : « …its reversible writes have a confirmed action-error rate of 8.6 % against a 0.76 % bar (errors against a single expected path; Haiku's task success on WorkBench is 95 % to 97 %, and 64 % of its episodes with a confirmed error are successful tasks). »
- Réécriture (section 8) : remplacer « confirmed errors inside successful tasks » par « confirmed errors inside successful tasks (64 % to 82 % of the WorkBench episodes with a confirmed error) ».

### I6. « the rates are the strong fact » pour des taux aux intervalles de 0,1 % à 51 %

- Endroit : section 6.4, PDF p. 4 ; C.6.4, p. 24.
- Citation : « money-moving writes on airline and retail err 6.5 % to 13.3 % against bars near 0.008 % […] the high-stakes ratios mostly measure the budget chosen, while the rates are the strong fact. »
- Problème. Les intervalles à ρ = 1 sont dans l'annexe seulement : aviation [0,6 ; 50,7], [0,3 ; 47,3], [0,1 ; 44,6] ; commerce [2,2 ; 23,6], [1,0 ; 20,5], [1,0 ; 20,5]. Aviation/Opus repose sur 6 erreurs dans 9 tâches. 12 à 17 % des erreurs de Haiku sur ce type sont des écritures refusées, sans dégât (tableau X4). « Strong fact » ne décrit pas cela.
- Réécriture : « …the high-stakes ratios mostly measure the budget chosen; the rates are the informative quantity, with wide intervals (lower bounds 0.1 % to 2.2 %, upper bounds 20 % to 51 %; Appendix C). »

### I7. La jugeabilité se lit sous ρ̂, pas à ρ = 1 ; le tableau 6 laisse croire le contraire

- Endroit : section 5 ; section 6.2 ; tableau 6, PDF p. 30.
- Citation : « a type is judgeable if zero errors would bring it under its bar (n_eff × bar ≥ 0.6905, about ln 2) » ; tableau 6, première ligne : « n_eff (ρ=1) 81.6 […] n_eff × bar 0.740 ».
- Problème. 81,6 × 0,00757 = 0,618, sous 0,6905. Le 0,740 vient d'un autre n_eff (97,72, sous ρ̂ = 0,819, d'après `FORMULATION_VERDICT.md`). Le lecteur qui refait le produit conclut que le type n'est pas jugeable. Et le fond compte : à ρ = 1, l'étiquette serait « insufficient evidence ». R4 est donc « établi sans hypothèse sur le groupement » pour le dépassement, mais pas pour la jugeabilité. Le corps le dit par la bascule à 0,885, sans le dire en clair.
- Réécriture (6.2) : « Judgeability is read under the estimated correlation (n_eff = 97.7 at ρ̂ = 0.819, hence 0.740), not at ρ = 1 (n_eff = 81.6, 0.618), where the type would not be judgeable. The excess is established at ρ = 1; the judgeability that makes it count is not. »
- Tableau 6 : ajouter la colonne « n_eff (ρ̂) » ou une note sous le tableau.

### I8. Déclarations : le rôle de l'IA dans les décisions de méthode et dans les audits n'est pas dit

- Endroit : « Use of AI tools », PDF p. 7 ; annexe A, D11 ; résumé.
- Citations : « Claude models (Anthropic), through Claude Code, were used, under the author's direction, to write the code […], to draft and revise the text of the plan […], and to audit the results and the paper. » ; D11 : « An independent audit then found… » ; résumé : « alerts reviewed blind ».
- Problème, en trois points.
  1. Le plan figé porte 83 mentions « Tranché par Claude » (compte fait dans `PLAN_EXPERIENCE.md`) : ordre des étiquettes, max-T à la place de Holm, lecture de « jamais », etc. La déclaration parle de code et de rédaction, pas de choix de méthode.
  2. « Independent audit » (D11) : l'audit est celui d'une instance Claude séparée (`revues/2026-11-14_audit_fable.md`). Le mot « independent » laisse attendre un tiers.
  3. Résumé : « alerts reviewed blind » laisse croire à une relecture humaine. Les relecteurs sont des instances Claude, du même fournisseur que les agents ; en vague 2, Opus 5.5 relit des parties jouées par Opus 5.5 ; l'aveugle tient à une consigne (D7). C'est dit en sections 4 et 8, pas dans le résumé.
- Réécriture (déclaration) : ajouter « Claude also proposed, and in places settled, analysis choices recorded in the frozen plan (marked "Tranché par Claude" there; for example the order of labels and the max-T procedure); the author approved the plan as frozen. The audits cited in this paper were run by separate Claude instances, not by a third party. »
- Réécriture (D11) : « An audit by a separate Claude instance then found… »
- Réécriture (résumé) : « alerts reviewed on blind sheets by Claude instances, with a blind sample re-reviewed by the author ».
- Financement : déclaration complète et exacte (crédits Anthropic, abonnement payé par l'auteur, micro-entreprise). Placement en fin d'article acceptable. Conseil : une note de première page d'une ligne (« Agents, alert reviewers and writing assistant are Claude models; API costs covered by Anthropic startup credits; see Declarations »), car c'est la page que lit le lecteur pressé.

## Mineur

### M1. Introduction : la borne est annoncée sans ses conditions

- Endroit : section 1, PDF p. 1.
- Citation : « Without any assumption of statistical control, such a plan bounds outgoing quality […], and a cycle argument gives a bound on the extra errors that delegation lets through. »
- Problème : le résumé dit « conditional bound » ; l'introduction perd le mot. La borne suppose un constat immédiat, des erreurs détectées, des ratés non ciblés et s ≤ q/0,95 (non tenu dans 24 des 51 cellules jugées, 6.3).
- Réécriture : « …and a cycle argument gives a conditional bound (detected errors, immediate detection, a write mix close to the expected one; Section 3) on the extra errors that delegation lets through. »

### M2. « we instantiate that relation and test it »

- Endroit : section 2, PDF p. 2.
- Problème : « test it » sans réserve, alors que le test a peu tranché.
- Réécriture : « we instantiate that relation and put it to a pre-registered test, which had little power (Section 6.3). »

### M3. Contribution 2 : « the real error rate », « for each »

- Endroit : section 1, PDF p. 2 ; aussi B.4.5 (« real reliability »).
- Citation : « for each model, environment and action type, the distance between the real error rate and the bar ».
- Problème : c'est un taux d'erreurs confirmées par relecture, contre un chemin attendu unique ; 20 types sur 40 restent indéterminés.
- Réécriture : « for each model, environment and action type observed, the confirmed error rate against the bar the budget requires, with its interval; half of the types remain undetermined (Section 6.4). »

### M4. Accord de la relecture : « 13 of 15 » sans dire que c'est le seuil

- Endroit : section 6.1, PDF p. 4.
- Citation : « The author's blind review agreed 13 of 15 times in each wave. »
- Problème : 13 est le seuil exact, les deux fois (dit en C.6.1 seulement). Et 3 des 4 désaccords lèvent une alerte confirmée.
- Réécriture : « …agreed 13 of 15 times in each wave, exactly the threshold; three of the four disagreements lifted a confirmed alert. »

### M5. Section 8 : trois limites de la relecture restent en annexe

- Endroit : section 8, PDF p. 7.
- Manquent dans le corps : aveugle tenu par consigne, sans barrière technique ni transcription (D7) ; modèle relecteur de la vague 1 non enregistré (D7) ; Haiku rejoue 50 fois les mêmes tâches en aviation et en commerce (limite 13).
- Réécriture : après « same-provider reviewers », ajouter « blind by instruction only, with the wave-1 reviewing model not recorded » ; après « one expected path per task », ajouter « tasks replayed up to 50 times ».

### M6. Section 6.5 : « 55 to 66 validations per 100 » peut se lire comme une économie

- Endroit : section 6.5, PDF p. 4.
- Problème : la réserve suit (« mostly through tier 2 on a type established above its bar »), mais le chiffre des erreurs exécutées (4,6 à 6,2 pour 100) n'arrive qu'en discussion.
- Réécriture : accoler « (about 4.6 to 6.2 errors per 100 such writes executed then flagged, exploratory) » à la phrase de 6.5.

### M7. Version longue : phrase reprenable hors contexte

- Endroit : `brouillon.md`, section 7.
- Citation : « Descriptively, every one of the twelve configurations has at least one type whose lower bound at ρ = 1 lies above its bar ».
- Problème : exact (vérifié sur le tableau 6), mais 6 de ces 12 types sont à enjeu fort, à des barres voisines de 0,008 %, et 3 en banque. Sortie de son paragraphe, la phrase dit « les douze configurations sont en dépassement ».
- Réécriture : « …(for nine of the twelve, only on banking or on high-stakes types whose bars are near 0.008 %; not a label claim) ».

### M8. Hors article : `FORMULATION_VERDICT.md` définit « délégable » autrement que le plan

- Citation : « une configuration l'est si chacun de ses types jugeables a un taux médian […] au plus égal à sa barre ».
- Le plan (5.13, Q14) et l'article (section 5) disent « au moins un type ». À corriger dans la page de référence, pour que la mauvaise définition ne passe pas dans un message de diffusion.
