# Charge de la preuve, coûts d'erreur asymétriques et amendement avant le gel : comment étiqueter un dépassement tiré d'une seule tâche

> Notes de recherche documentaire, 07/11/2026, avant le gel du 18/11. Aucune donnée réelle vue ; seuls des documents publics et, pour le contexte, `PLAN_EXPERIENCE.md` (1.5, 5.14, 8), `REGLE.md` et `simulation/controle3/RAPPORT.md` (9.3, 10.7, 10.8). Convention : **Cited Findings** = sourcé (citation en langue d'origine, lien) ; **Inferences** = déduit par moi ; **Gaps** = non trouvé ou non vérifié. Les calculs marqués « calcul » sont les miens (Python, sans appel payant), sur des décomptes bruts, pas sur l'estimateur du moteur.

## 1. Surveillance de la sécurité en essais cliniques : que vaut un signal de nuisance porté par un ou deux événements ?

### Takeaway
Pour la FDA et l'EMA, un ou deux événements font un **signal**, qui appelle une suite : validation, enquête, données en plus. Ce n'est pas un risque établi. Exception : un événement très spécifique, presque absent sans le produit (cas de Hy, angio-œdème). Là, un seul cas déclenche une action réglementaire, sans valoir pour autant « risque identifié ». Les comités de surveillance (DMC) arrêtent un essai avec moins de preuves pour une nuisance que pour un bénéfice. Mais c'est une décision de protection des participants, et la FDA rappelle qu'elle peut conclure à tort à un effet indésirable.

### Cited Findings
- **Définition du signal, un seul cas possible, et suite attendue (FDA, 2005).** « safety signal refers to a concern about an excess of adverse events compared to what would be expected to be associated with a product's use […] It is possible that even a single well-documented case report can be viewed as a signal, particularly if the report describes a positive rechallenge or if the event is extremely rare in the absence of drug use. Signals generally indicate the need for further investigation, which may or may not lead to the conclusion that the product caused the event. After a signal is identified, it should be further assessed to determine whether it represents a potential safety risk » — [FDA, Guidance for Industry: Good Pharmacovigilance Practices and Pharmacoepidemiologic Assessment, mars 2005, section III](https://www.fda.gov/media/71546/download)
- Même guide, sur ce qu'un signal ne dit pas : « The actual risk to patients cannot be known from these data » ; liste des signaux qui « may warrant further investigation », dont « Occurrence of serious events thought to be extremely rare in the general population » — [FDA GPV 2005, section IV.F](https://www.fda.gov/media/71546/download)
- **Quand un seul événement suffit à suggérer la causalité (règlement américain sur les rapports de sécurité).** « (A) A single occurrence of an event that is uncommon and known to be strongly associated with drug exposure (e.g., angioedema, hepatic injury, Stevens-Johnson Syndrome); (B) One or more occurrences of an event that is not commonly associated with drug exposure, but is otherwise uncommon in the population exposed to the drug (e.g., tendon rupture); (C) An aggregate analysis of specific events observed in a clinical trial (such as […] other events that commonly occur in the study population independent of drug therapy) that indicates those events occur more frequently in the drug treatment group than in a concurrent or historical control group. » — [21 CFR 312.32(c)(1)(i)](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-D/part-312/subpart-B/section-312.32). Pour un événement fréquent sans le produit, un cas isolé ne suffit donc pas : il faut une analyse agrégée face à un témoin.
- **Cas de Hy (FDA, 2009) : un cas inquiète, deux prédisent.** « Finding one Hy's Law case in the clinical trial database is worrisome; finding two is considered highly predictive that the drug has the potential to cause severe DILI […] Clinical trials of tasosartan […] showed a single Hy's Law case. This led to a request for a much larger premarketing database and the drug was abandoned. » Et : « Failure to find a case, however, does not imply that a drug with AT elevations is free of a risk of severe DILI. » — [FDA, Drug-Induced Liver Injury: Premarketing Clinical Evaluation, juillet 2009](https://www.fda.gov/media/116737/download). Le cas de Hy est défini par trois critères, causes alternatives exclues : c'est un événement très spécifique.
- **Asymétrie des arrêts pour nuisance (FDA, guide DMC, 2006).** « a DMC may recommend termination of a study with a trend toward showing harm on the basis of data that, were they in the other direction, would not be considered strong enough to terminate early with a conclusion of benefit. » Et : « Such assessments have potential implications for falsely concluding that there is an adverse effect, just as regular assessments of efficacy have the potential to lead to false positive conclusions about benefit. […] It is usually appropriate to demand less rigorous proof of harm to justify early termination than would be appropriate for a finding of benefit. In some cases, however, it may be appropriate to establish a harmful effect more definitively » — [FDA, Establishment and Operation of Clinical Trial Data Monitoring Committees, mars 2006](https://www.fda.gov/media/75398/download)
- **Exemple de borne de nuisance dans un plan séquentiel.** Dans la vignette « harm bound » du paquet R gsDesign, la borne de nuisance « lies below the futility bound ». L'exemple lui alloue un α nominal de 0,1 sous H0 (si l'on ignore la futilité) ; « the actual cumulative probability of stopping for harm is approximately 0.0417 when all active stopping rules are followed ». La vignette renvoie au projet de guide de la FDA d'août 2025 sur la survie globale comme critère de sécurité. Elle ne formule pas le principe « moins de preuves pour la nuisance » — [gsDesign, Futility and harm bounds for overall survival monitoring](https://keaven.github.io/gsDesign/articles/HarmBound.html)
- **ICH E9 sur l'évaluation statistique de la sécurité (section 6.4).** « conclusive information from confirmatory clinical trials is the exception rather than the rule » ; les p-valeurs servent souvent de « 'flagging' device […] to highlight differences worth further attention » ; « If hypothesis tests are used, statistical adjustments for multiplicity to quantify the type I error are appropriate, but the type II error is usually of more concern. Care should be taken when interpreting putative statistically significant findings when there is no multiplicity adjustment. » — [ICH E9, 1998, 6.4](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- **Validation d'un signal à l'EMA : la force de la preuve se juge sur le nombre de cas.** « the total number of cases (after exclusion of duplicates), and amongst those, the number of supportive cases […] number of cases in the context of patient exposure » — [EMA, GVP Module IX Rev 1, Signal management](https://www.ema.europa.eu/en/documents/scientific-guideline/guideline-good-pharmacovigilance-practices-gvp-module-ix-signal-management-rev-1_en.pdf)

### Inferences
- **R1 n'est pas une décision d'arrêt.** C'est une conclusion publiée et éliminatoire (« règle réfutée »). Son équivalent est la classe « nuisance établie / risque identifié », pas l'arrêt précoce d'un DMC. Le seuil plus bas du DMC sert à protéger des participants exposés pendant l'essai. Le rejeu hors ligne n'expose personne. L'action protectrice correspondante, dans le projet, est le déploiement (garder la validation humaine), pas l'étiquette.
- **L'exception « un seul cas » ne s'applique pas ici.** Elle suppose un événement spécifique, presque inexistant sans le produit (critère A du 21 CFR 312.32, cas de Hy, « extremely rare in the absence of drug use »). Une erreur déléguée en plus n'est pas rare au regard du budget. Calcul, écritures indépendantes : avec un taux égal au budget faible (0,5 pour 100), la probabilité d'au moins une erreur vaut 9,5 % sur 20 écritures, 18 % sur 40 et 26 % sur 60. On est dans le cas C : il faut une comparaison agrégée, donc plusieurs unités indépendantes.
- **La mise en garde d'E9 vise exactement la règle actuelle.** Les cellules à écart type nul sortent du max-T, donc de la correction de multiplicité. Leur « dépassement établi » est un résultat « significatif » sans ajustement : c'est la situation pour laquelle E9 demande de la prudence (« Care should be taken… »).
- **« L'erreur de type II préoccupe davantage » ne veut pas dire « abaisser le seuil de R1 ».** E9 répond à cette préoccupation par l'intervalle de confiance qui montre l'absence de différence inacceptable (paragraphe suivant de 6.4, cité en question 5). Dans le projet, c'est la mention « démontrée ». Ce n'est pas un test de nuisance plus laxiste.

### Gaps
- Je n'ai consulté directement ni Ellenberg, Fleming et DeMets (*Data Monitoring Committees in Clinical Trials*) ni Jennison et Turnbull (*Group Sequential Methods*) : pas d'accès ouvert. Le principe d'asymétrie est sourcé par le guide DMC de la FDA (2006). Je n'ai pas vérifié s'il existe une révision plus récente de ce guide.
- Aucune source trouvée sur un signal de nuisance porté par une seule grappe (un seul centre, un seul site) en surveillance d'essai.
- Aucune donnée trouvée sur la part des arrêts pour nuisance fondés sur un ou deux événements qui ont ensuite été démentis.

## 2. La règle de trois, ses limites, et la frontière entre signal et risque établi (FDA, EMA)

### Takeaway
La règle de trois donne une borne haute quand on n'a observé **aucun** événement, sur des unités indépendantes, bien observées et assez nombreuses (n > 30). Elle ne sert pas à établir un dépassement. Comptée en tâches, une cellule à une seule tâche ne donne d'information dans aucun sens. L'EMA tient un vocabulaire à plusieurs états, qui correspond à la situation : signal (validé ou non), risque potentiel, risque identifié, signal réfuté, information manquante.

### Cited Findings
- **Règle de trois et condition n > 30.** « upper limit of 95% confidence interval = maximum risk = 3/n (for n > 30) » ; elle sert « when complication rates of zero are reported » — [Eypasch et al., BMJ 1995, résumé](https://pmc.ncbi.nlm.nih.gov/articles/PMC2550668/) (formule attribuée à Hanley)
- **Hypothèses de la règle (FDA, 2009).** « The Rule of 3 is derived from simple binomial calculation. There will be at least a 95 percent chance of seeing one or more cases of DILI in 3n trial subjects if its true incidence is 1 in n subjects, and the group is well observed. » — [FDA DILI 2009, note 4](https://www.fda.gov/media/116737/download)
- Article d'origine : Hanley et Lippman-Hand, « If nothing goes wrong, is everything all right? Interpreting zero numerators », JAMA 1983;249:1743-1745 — [DOI](https://doi.org/10.1001/jama.1983.03330370053031). Texte non lu (accès payant).
- **Vocabulaire de l'EMA (GVP, annexe I, révision 4).**
  - *Signal* : « Information […] which suggests a new potentially causal association […] that is judged to be of sufficient likelihood to justify verificatory action ».
  - *Validated signal* : la documentation « contains sufficient evidence demonstrating the existence of a new potentially causal association […] and therefore justifies further analysis ».
  - *Non-validated signal* : la documentation « at that point in time does not contain sufficient evidence ».
  - *Refuted signal* : « following further assessment has been determined to be "false", i.e. a causal association cannot be established at that point in time ».
  - *Potential risk* : « some basis for suspicion of an association […] but where this association has not been confirmed ». Exemple donné : des événements d'essais où l'écart « raises a suspicion of, but is not large enough to suggest, a causal relationship ».
  - *Identified risk* : « adequate evidence of an association ».
  - *Missing information* : « Gaps in knowledge […] which could be clinically significant ».
  - *Closed signal* : « closed either because it is refuted or because it is determined to be a potential or identified risk ».
  - Source : [EMA, GVP Annex I – Definitions (Rev 4)](https://www.ema.europa.eu/en/documents/scientific-guideline/guideline-good-pharmacovigilance-practices-annex-i-definitions-rev-4_en.pdf). La copie consultée porte la mention « Superseded version (not valid anymore) ». Ces définitions viennent d'ICH E2F, mais la révision en vigueur n'a pas été relue.
- **Inférence groupée avec très peu de grappes.** « Inference based on cluster-robust standard errors […] using either the Student's t-distribution or the wild cluster bootstrap, is known to fail when the number of treated clusters is very small. » — [MacKinnon & Webb, Econometrics Journal 2018, résumé](https://econpapers.repec.org/RePEc:wly:emjrnl:v:21:y:2018:i:2:p:114-135). Pour les essais en grappes : « the need to use small sample corrections when the number of clusters is small » — [Hemming et al., Trials 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC11866560/)
- **Interne.**
  - « bornes "zéro erreur" calculées sur la taille effective ou au niveau des tâches, jamais sur les écritures brutes ».
  - « fragile » sous 30 tâches porteuses, car « de 5 à 30 grappes, l'inférence groupée devient peu fiable ».
  - « Le bootstrap-t donne une borne haute infinie dès que les dégâts tiennent à trois tâches ou moins ».
  - Source : [PLAN_EXPERIENCE.md, section 8](ROOT/PLAN_EXPERIENCE.md). Le rapport utilise lui-même la règle de trois, sur des répétitions indépendantes et nombreuses : « au plus 0,6 %, règle de trois », pour 0 faux R1 sur 539 répétitions — [RAPPORT.md, 10.7](ROOT/simulation/controle3/RAPPORT.md)

### Inferences
- **Une cellule à une seule tâche ne dit rien, dans aucun sens.** Calcul, Clopper-Pearson unilatéral à 95 % avec n_eff = 1 (ρ = 1, la lecture du plan pour R4) :
  - sans erreur, la borne haute vaut 0,95 : rien n'est démontré ;
  - avec une erreur, la borne basse vaut environ 10⁻²⁶ à 10⁻⁷⁸ (m = 20 à 60 écritures) : rien n'est établi.
  - La règle de trois elle-même ne s'applique pas (n = 1, loin de n > 30).
- **Même la lecture la plus indulgente n'établit rien sur une erreur.** Calcul, en ignorant le groupement (écritures brutes, lecture que la section 8 interdit) : une erreur sur 20, 40 ou 60 écritures donne une borne basse de 0,26, 0,13 ou 0,09 pour 100, sous le budget faible de 0,5. C'est avant toute correction de multiplicité. Deux erreurs donneraient 1,81, 0,90 ou 0,60 pour 100 : établi, mais seulement en écritures brutes.
- **La règle actuelle est donc plus indulgente que n'importe quel intervalle.** Elle établit le dépassement sur l'estimation ponctuelle (« son dépassement n'est établi que si son estimation dépasse le budget »). C'est contraire à la section 8 du plan. Réserve : mes calculs portent sur un décompte brut, pas sur l'estimateur du moteur, qui donne 1,9 à 3,8 fois le budget pour une erreur (RAPPORT 10.7).
- **Correspondance avec le vocabulaire réglementaire.**
  - Une cellule à une tâche dont l'estimation dépasse le budget est au mieux un *signal*, ou un *potential risk* : « some basis for suspicion […] not confirmed ». Ce n'est pas un *identified risk*, qui demande une « adequate evidence ».
  - Les cellules à une tâche en général relèvent de la *missing information*.
- **Piège de vocabulaire, à signaler au rédacteur.** À l'EMA, *refuted signal* veut dire « causalité non établie à ce stade ». C'est le sens inverse du R1 du projet, où « réfutée » veut dire « dépassement établi ». Le mot « réfuté » ne doit pas être transposé tel quel.

### Gaps
- Aucune source trouvée qui adapte explicitement la règle de trois aux données groupées (effet de plan, taille effective). L'adaptation par n_eff est celle du plan, et elle est déduite.
- Le guide de la FDA « Premarketing Risk Assessment » (2005) n'a pas été consulté : le téléchargement depuis fda.gov a échoué dans mes outils. Jovanovic et Levy (1997, « A look at the rule of three ») est introuvable dans Europe PMC.
- La version en vigueur des annexes GVP (I et IX) n'a pas été vérifiée.

## 3. Plans à trois issues et zones « non concluant »

### Takeaway
Storer (1992), puis Sargent, Chan et Goldberg (2001), ajoutent une troisième issue : ne rejeter ni H0 ni H1. Elle vaut quand l'intervalle de confiance couvre une bonne part de l'écart entre les deux hypothèses, et la décision passe alors par d'autres éléments. C'est la situation d'une cellule à une seule tâche, et le projet a déjà cette structure : dépassement établi (R1) / « démontrée » / entre les deux.

### Cited Findings
- **Sargent et al. 2001, résumé complet.** « Phase II clinical trials are typically designed in the hypothesis testing framework with two possible outcomes, either reject the null hypothesis H(0) or reject the alternative hypothesis H(a), based on the observed activity level. However, in cases where the observed activity is "borderline," the decision regarding the future of the agent is not as clear as the prespecified hypothesis test would indicate. In this paper we propose an alternative design that allows for three outcomes: reject H(0), reject H(a), or reject neither. […] We focus on the clinical implications of the three-outcome design. » — [Sargent, Chan & Goldberg, Controlled Clinical Trials 2001;22:117-125, PMID 11306150](https://pubmed.ncbi.nlm.nih.gov/11306150/)
- **Storer 1992, résumé.** Le plan à deux issues de Fleming « can lead to some ambiguity as to the appropriate practical decision at the end of the trial, as the confidence region for p may include a substantial part of the interval between p1 and p2. We propose a class of designs wherein an allowable outcome is not to reject either H1 or H2. An additional constraint is placed on the design by specifying Pr(reject Hj | pm) less than or equal to gamma (j = 1, 2), where p1 less than pm less than p2. […] This type of design can provide a more realistic basis for decision making following the trial, although traditional values of alpha and/or beta need to be viewed from a somewhat different perspective » — [Storer, Biometrics 1992;48:55-60, PMID 1581493](https://pubmed.ncbi.nlm.nih.gov/1581493/)
- Principe général, cité pour mémoire : [Altman & Bland, « Absence of evidence is not evidence of absence », BMJ 1995](https://pmc.ncbi.nlm.nih.gov/articles/PMC2550545/) (titre seulement, texte non relu).
- Troisième issue en apprentissage automatique, « No Solution Found » : voir la question 4. Troisième issue en pharmacovigilance (signal clos comme réfuté, risque potentiel ou risque identifié) : voir la question 2.
- **Interne.**
  - Le point 1 ne dit « tenu » que faute de dépassement établi ; la mention « démontrée » est à part — [PLAN_EXPERIENCE.md, 5.14, point 1](ROOT/PLAN_EXPERIENCE.md).
  - Pour R4, le projet a déjà choisi le 07/11 une troisième issue avec son motif : « preuves insuffisantes ». Elle est définie ainsi : « les données sont compatibles avec des agents fiables […] comme avec des agents peu fiables : elles ne comptent pas contre eux » — [PLAN_EXPERIENCE.md, 1.5](ROOT/PLAN_EXPERIENCE.md).

### Inferences
- **Le critère d'ambiguïté de Storer est rempli au maximum.** Sur une cellule à une tâche, l'intervalle compté en tâches va de presque 0 à presque 1 (question 2). La cellule tombe donc dans la zone « ne rejeter ni l'un ni l'autre ».
- **La règle actuelle ramène cette zone à deux issues, et sans intervalle.** Elle la tranche par l'estimation ponctuelle. C'est l'inverse de ce que proposent les plans à trois issues.
- **Correspondance avec les options en présence.**
  - (b), et la mention « signal sur une seule tâche » sans effet : troisième issue au niveau de la cellule.
  - « R1 remplacé par preuves insuffisantes pour ce motif » : troisième issue au niveau de toute l'étude.
  - (a), et « garder R1 par précaution » : deux issues, la zone ambiguë étant comptée comme un rejet.
- **Le prix de la troisième issue, comme le dit Storer : α et β se lisent autrement.** Dans le projet, une cellule à une seule tâche perd toute puissance de détection d'un vrai dépassement par R1. Cette perte doit être déclarée. Ce prix n'est pas nouveau : la règle actuelle n'a pas de vraie puissance sur ces cellules, elle tranche au hasard de l'erreur présente ou absente.

### Gaps
- Les textes complets de Sargent et de Storer n'ont pas été lus (accès payant). Les règles de décision précises dans la zone non concluante ne sont vérifiées qu'au niveau des résumés.
- Aucune source trouvée qui applique un plan à trois issues à un critère de sécurité éliminatoire. Ces plans servent au tri d'efficacité en phase II.

## 4. Amélioration sûre de politique et algorithmes seldoniens : bloquer, se replier ou signaler ?

### Takeaway
Avec trop peu de données, ces cadres **ne concluent jamais que le candidat est dangereux**. Ils s'abstiennent (« No Solution Found ») et reviennent à la solution de référence : globalement (Seldonian, HCPI) ou localement, pour chaque paire état-action trop peu vue (SPIBB, seuil N∧ fixé d'avance). La charge de la preuve porte sur la démonstration de sûreté. Dire qu'une politique est sûre est une affirmation sur la croyance, pas sur la politique.

### Cited Findings
- **Seldonian, test de sûreté.** « The Safety Test mechanism checks whether the algorithm has sufficient confidence that gi(θc) ≤ 0 for each constraint […] If so, it returns the candidate solution θc, otherwise it returns NSF. » — [Thomas et al., Science 2019, fig. 1](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf) (DOI 10.1126/science.aag3311)
- **NSF faute de données, et retour à la référence.** « Even using approximate confidence bounds, there may not be sufficient data for any algorithm to ensure that the behavioral constraints are met. Rather than require an algorithm to produce a solution even in such cases, we propose allowing the algorithm to return No Solution Found (NSF). The algorithm should return NSF when it is unable to find a satisfactory solution given the available data. […] if a Seldonian algorithm returns NSF, we can revert to using the baseline solution. » — [Thomas et al. 2019, matériel supplémentaire, même PDF, p. 20](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf)
- **Le coût de l'abstention.** « if NSF is included in the SOP, then the algorithm that always returns NSF is trivially Seldonian. If the SOP is properly designed, the objective function f should assign low utility to this trivial algorithm […] a Seldonian algorithm that returns NSF less frequently. » — [même source](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf)
- **Bornes approchées (t, bootstrap).** Les bornes des algorithmes « quasi-Seldonian » (Student, bootstrap) « only approximately hold » ; « researchers should clearly state the assumptions upon which quasi-Seldonian algorithms rely » — [même source](https://people.cs.umass.edu/~brun/pubs/pubs/Thomas19science.pdf)
- **HCPI, définitions.** « we call an RL algorithm safe if it ensures that the probability that a policy with performance less than ρ− will be proposed is at most δ » ; « "a policy is safe" is a statement about our belief concerning that policy given the observed data, and not a statement about the policy itself » ; l'algorithme « outputs either a new policy or NO SOLUTION FOUND (NSF) » ; « We call an RL algorithm semi-safe if it would be safe, except that it makes a false but reasonable assumption » (cas des variantes t et BCa) — [Thomas, Theocharous & Ghavamzadeh, ICML 2015](https://proceedings.mlr.press/v37/thomas15.pdf)
- **SPIBB, repli local.**
  - « it bootstraps the trained policy with the baseline when the uncertainty is high ».
  - « B is the set of state-action pairs with counts smaller than N∧ » ; « when a state-action pair (x, a) is rarely seen in the dataset, we propose to rely on the baseline by copying its probability ».
  - « SPIBB looks for a solution that improves the baseline when it can guarantee improvement and falls back on the baseline when the uncertainty is too high. One can see it as a knows-what-it-knows algorithm, asking for help from the baseline when it does not know whether it knows ».
  - « N∧ is not a property of the dataset, but a hyper-parameter of the algorithm ».
  - Source : [Laroche, Trichelair & Tachet des Combes, ICML 2019 (arXiv 1712.06924)](https://arxiv.org/abs/1712.06924)

### Inferences
- **Correspondance avec le projet.**
  - La référence, c'est la validation humaine (paliers 1 et 2, ou « tout faire valider »).
  - NSF correspond à « non démontrée » ou « preuves insuffisantes », jamais à « réfutée ».
  - Une cellule à une tâche ne peut donc ni être certifiée sûre (« démontrée » impossible), ni servir de preuve de danger. En déploiement, le type d'action concerné reste sous validation.
- **Local ou global : deux réponses possibles.**
  - Le repli local de SPIBB correspond à l'option (b) : la cellule seule devient non concluante, l'étiquette n'en dépend pas.
  - Le NSF global des algorithmes seldoniens correspond à « preuves insuffisantes » comme étiquette d'ensemble.
  - Mais « confirmée » n'est pas une certification seldonienne : elle ne demande « démontrée » pour aucune cellule. Bloquer « confirmée » à cause d'une cellule à une tâche avec une erreur, alors qu'une cellule à une tâche sans erreur, tout aussi muette, ne bloque rien, serait une asymétrie à justifier.
- **N∧, ou le nombre minimal de tâches porteuses.** L'équivalent de N∧ serait un minimum de tâches porteuses fixé d'avance pour qu'une cellule compte dans R1. L'option (b) revient à N∧ = 2 tâches.
  - La simulation couvre des cellules de 5 à 11 tâches porteuses (0 R1 sur 120 au seuil exact ; RAPPORT 10.8).
  - Rien n'est rapporté pour 2 à 4 tâches. Le plan note pourtant une borne haute infinie du bootstrap-t à trois tâches ou moins, et MacKinnon et Webb un rejet trop ou trop peu fréquent quand les grappes sont très peu nombreuses.
  - Le seuil de 2 n'est donc pas couvert par les preuves. C'est le point le plus important à simuler si (b) est retenue.
- **Le bootstrap par tâches est une méthode « semi-safe » au sens de HCPI.** Son hypothèse raisonnable, assez de grappes, est franchement fausse avec une seule tâche. La règle de Thomas (« clearly state the assumptions ») plaide au minimum pour déclarer cette limite, même sous l'option (a).
- **L'avertissement sur le NSF trivial vaut pour « preuves insuffisantes ».** Une règle qui sort trop souvent « preuves insuffisantes » est sûre mais inutile. Si l'option « R1 remplacé par preuves insuffisantes » est retenue, sa fréquence dans les mondes où B-tout tient son budget près de la barre doit être mesurée.
  - Données disponibles : une cellule jugée portée par une seule tâche apparaît dans 6 répétitions sur 12 du monde A (RAPPORT 9.3, point 5).
  - Au budget, une erreur y apparaît dans 10 à 26 % des cas, d'après le calcul de la question 1 (indépendance supposée).
  - Ordre de grandeur non simulé.

### Gaps
- HCOPE (Thomas, Theocharous & Ghavamzadeh, AAAI 2015) n'a pas été consulté directement : seule sa présentation dans HCPI, section 2.2, l'a été.
- Aucune source trouvée qui applique l'amélioration sûre de politique à une délégation par paliers et par type d'action. La correspondance est la mienne.
- Le passage sur le NSF vient du matériel supplémentaire joint au PDF de l'article (UMass), pas du texte principal de *Science*.

## 5. Coûts d'erreur asymétriques et charge de la preuve : test de précaution ou test de preuve ?

### Takeaway
Les sources séparent deux charges.
- **Démontrer la sûreté** revient à qui veut déployer ou autoriser. L'échec donne « non démontré », et toute mesure de précaution reste provisoire et révisable.
- **Établir une nuisance** demande une preuve adéquate.

Pour une conclusion publiée « règle réfutée », ces cadres et la décision Q13 du projet (05/11) plaident pour un **test de preuve**. Le test éliminatoire protège d'abord contre la fausse élimination. Le risque de laisser passer un dépassement est couvert par la mention « démontrée », qu'une cellule à une tâche n'obtient jamais, et par le déploiement, pas par l'étiquette éliminatoire.

### Cited Findings
- **Précaution et prudence scientifique : deux choses distinctes (Commission européenne, 2000).** « The precautionary principle, which is essentially used by decision-makers in the management of risk, should not be confused with the element of caution that scientists apply in their assessment of scientific data. Recourse to the precautionary principle presupposes that potentially dangerous effects […] have been identified, and that scientific evaluation does not allow the risk to be determined with sufficient certainty. » — [COM(2000) 1, Communication on the precautionary principle](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52000DC0001)
- **Mesures provisoires et révisables.** Les mesures doivent être, entre autres, « subject to review, in the light of new scientific data, and capable of assigning responsibility for producing the scientific evidence necessary for a more comprehensive risk assessment » ; « Measures should be periodically reviewed in the light of scientific progress, and amended as necessary » ; et, selon l'accord SPS, elles « are provisional and imply that efforts be undertaken to elicit or generate the necessary scientific data » — [même source](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52000DC0001)
- **Charge de la preuve sous autorisation préalable.** Le législateur a « reversed the burden of proof by requiring that the substances be deemed hazardous until proven otherwise. Hence it is up to the business community to carry out the scientific work needed to evaluate the risk. As long as the human health risk cannot be evaluated with sufficient certainty, the legislator is not legally entitled to authorise use of the substance ». Sans autorisation préalable, « it may be for the user […] or the public authorities to demonstrate the nature of a danger and the level of risk ». Et : « Judging what is an "acceptable" level of risk for society is an eminently political responsibility » ; « The decision to do nothing may be a response in its own right. » — [même source, 6.4 et 5](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:52000DC0001)
- **Droit européen du médicament.** Selon l'article 12 du règlement (CE) 726/2004, rappelé par l'EMA, « a marketing authorisation shall be refused if the quality, safety or efficacy are not properly or sufficiently demonstrated » — [GVP Annex I Rev 4, entrée « Missing information »](https://www.ema.europa.eu/en/documents/scientific-guideline/guideline-good-pharmacovigilance-practices-annex-i-definitions-rev-4_en.pdf)
- **ICH E9, 6.4.** « In the majority of trials investigators are seeking to establish that there are no clinically unacceptable differences in safety and tolerability […] the use of confidence intervals is preferred to hypothesis testing in this situation. In this way, the considerable imprecision often arising from low frequencies of occurrence is clearly demonstrated. » Avec « the type II error is usually of more concern » (question 1) — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- **Exclure un risque inacceptable : la FDA en 2008, antidiabétiques.** D'après une source secondaire : « New ADDs need to prove that the CV risk is within an acceptable range of increase by demonstrating the upper bound of the two-sided 95% confidence interval (CI) of the risk ratio of MACEs < 1.8 » ; si la borne est « between 1.3 and 1.8 », « a postmarketing clinical trial will be needed » pour passer sous 1,3 — [Goyat et al., Clinical Drug Investigation 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC5953843/). Il y a donc trois états : risque exclu, risque non exclu (il faut plus de données), nuisance.
- **Définition probabiliste de la sûreté : HCPI et Seldonian** (question 4). L'algorithme sûr borne par δ la probabilité de *proposer* une mauvaise politique. Faute de preuve, il rend NSF.
- **Interne.**
  - *Décidé (Otsoa, 05/11 au soir, Q13)* : « le dépassement doit être établi […] une cellule indécise n'est plus un échec » — [PLAN_EXPERIENCE.md, 1.5](ROOT/PLAN_EXPERIENCE.md).
  - Avec l'ancienne règle « indécise = échec », une cellule où B-tout délègue finissait en R1 « dans 89 % des cas si B-tout est cinq fois sous le budget ». L'option étudiée alors : « Démontrer, et le dire […] R1 scindé en "réfutée" et "non démontrée" » — [PLAN_EXPERIENCE.md, 8](ROOT/PLAN_EXPERIENCE.md).
  - Précédent R4 (07/11) : « Un type non jugeable ne compte pas, même établi ». Les types trop rares « établissaient un dépassement avec deux ou trois tâches ratées et faisaient sortir R4 à tort dans 4,0 à 4,3 % des répétitions » — [PLAN_EXPERIENCE.md, 1.5](ROOT/PLAN_EXPERIENCE.md).

### Inferences
- **Deux affirmations, deux erreurs, deux tests.**
  - E1, le faux R1 : publier la réfutation d'une règle qui tient son budget.
  - E2, le dépassement manqué : une règle au-dessus du budget ne sort pas R1.
  - La logique de Neyman-Pearson veut qu'on mette en H0 l'hypothèse dont le rejet à tort coûte le plus. Ce point est déduit ; je n'ai pas retrouvé la citation de Neyman.
  - Pour R1, l'affirmation est « dépasse » : H0 = « tient », ce qui protège contre E1.
  - Pour « démontrée », l'affirmation est « sûre » : H0 = « dépasse », ce qui protège contre E2.
  - Le projet a déjà les deux tests. La cellule à une tâche échoue aux deux : c'est la troisième issue. C'est la structure réglementaire : démontrer pour autoriser, établir pour déclarer une nuisance.
- **Le R1 de précaution (éliminer sur un excès non mesurable) va contre les sources et contre le plan.**
  - Il confond gestion du risque et évaluation scientifique, ce que la Commission demande d'éviter.
  - Il n'est ni provisoire ni révisable, alors que la Commission l'exige d'une mesure de précaution : un R1 publié est définitif.
  - Il rouvre, dans un coin, la règle « indécise = échec » abandonnée le 05/11.
  - Il donne au seuil un taux de faux R1 par cellule d'environ 10 à 26 % (calcul, question 1), sans correction de multiplicité.
- **Le test de preuve, avec la mention « non démontrée », met la précaution à sa place.** Elle va dans la mention, dans la recommandation de déploiement (garder la validation, comme SPIBB) et dans le texte publié. Elle ne va pas dans l'étiquette éliminatoire.
- **Ce qui sert le mieux l'étude.** Sa thèse est : « la délégation tient son budget, et l'on dit ce qui est démontré ». Une élimination qui peut naître d'une seule erreur sur une seule tâche affaiblirait autant un R1 juste qu'un R1 faux, car le lecteur ne pourrait plus les distinguer. Le précédent R4 du 07/11 suit la même logique : non jugeable, donc ne compte pas, et motif publié.
- **Tableau des options**, chacune avec son équivalent dans les cadres (déduit).

| Option | Effet sur la cellule | Effet sur l'étiquette | Cadre équivalent | Cohérence interne | Prix |
|---|---|---|---|---|---|
| (a) garder et déclarer la limite | établie sur l'estimation ponctuelle | R1 possible (« fragile », sous 30 tâches) | aucun cadre consulté n'établit sans mesure d'incertitude | contraire à la section 8 et à l'esprit de Q13 | faux R1 au seuil d'environ 10 à 26 % par cellule (calcul approché, question 1) ; 1 sur 30 observé dans V |
| (b) aucune cellule à une tâche n'établit ; estimation et mention publiées | non concluante | inchangée par cette cellule | SPIBB (repli local) ; signal ou risque potentiel GVP ; « flagging » d'E9 | conforme à la section 8, à Q13 et au précédent R4 | aucune puissance R1 sur ces cellules (à déclarer) ; 2 à 4 tâches non simulées |
| R1 remplacé par « preuves insuffisantes », motif « une seule tâche porteuse » | non concluante | l'étude entière passe en PI si aucun R1 ailleurs | NSF global seldonien ; « reject neither » au niveau de l'étude | vocabulaire de R4, mais asymétrique face aux cellules à une tâche sans erreur | fréquence de PI près de la barre à mesurer ; le traitement du point 2 est à préciser |
| mention « signal sur une seule tâche », sans effet | comme (b) | inchangée | signal FDA ou EMA | comme (b) | comme (b) |
| garder R1 par précaution, avec mention | établie | R1 | arrêt précoce d'un DMC (décision protectrice, pas conclusion) | contraire à Q13 et à la section 8 | comme (a) ; R1 publié non révisable |

- **Variante (déduite, non simulée).** Pour les cellules sous K tâches porteuses, juger le dépassement par la borne basse de Clopper-Pearson sur n_eff à ρ = 1, la méthode de R4.
  - Une seule tâche n'établirait jamais rien, et les cellules de 2 à 4 tâches auraient un test conservateur valide.
  - Il faudrait l'articuler avec le niveau global du max-T, par exemple par Bonferroni sur ces cellules, et la simuler.

### Gaps
- Aucune source décisionnelle trouvée sur le cas précis d'une étiquette éliminatoire, dans une évaluation préenregistrée, fondée sur une seule grappe.
- La formalisation bayésienne (décider « nuisance » si P > c_FA ÷ (c_FA + c_M)) relève de la théorie standard. Je n'ai trouvé aucune source qui l'applique à ce type d'étiquette.
- Le texte primaire du guide FDA 2008 sur les antidiabétiques n'a pas été lu : il a été retiré, et le téléchargement a échoué. La citation vient d'une méta-analyse secondaire.
- Les cadres de sécurité de l'IA (seuils de capacité, « preuves insuffisantes ») n'ont pas été cherchés : hors du périmètre confié.

## 6. Amender le plan avant toute donnée réelle : légitimité et documentation

### Takeaway
Toutes les sources consultées tiennent pour légitime un changement fait avant l'accès aux données, s'il est daté, justifié et visible.
- ICH E9 veut un plan d'analyse revu, puis finalisé avant la levée de l'aveugle, avec des traces formelles.
- Nosek (2018) et Lakens (2024) jugent qu'un changement indépendant des données ne coûte rien à la sévérité du test.
- Willroth et Atherton (2024) donnent la grille de déclaration.

Ici, le gel n'a pas eu lieu. C'est donc une **révision du plan** plutôt qu'une déviation, et `REGLE.md` prévoit lui-même de corriger la règle avant le gel si la simulation le demande.

### Cited Findings
- **ICH E9, 5.1.** « The plan should be reviewed and possibly updated as a result of the blind review of the data […] and should be finalised before breaking the blind. Formal records should be kept of when the statistical analysis plan was finalised as well as when the blind was subsequently broken. If the blind review suggests changes to the principal features stated in the protocol, these should be documented in a protocol amendment. […] Only results from analyses envisaged in the protocol (including amendments) can be regarded as confirmatory. » Définition de la *blind review* : « The checking and assessment of data during the period of time between trial completion […] and the breaking of the blind, for the purpose of finalising the planned analysis. » — [ICH E9, 5.1 et glossaire](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- **ICH E9, 4.4 (révision de l'effectif) et 7.1.** Un changement doit être « justified and documented in a protocol amendment and in the clinical study report », avec ses conséquences « for the type I error and the width of confidence intervals ». Et : « Particular attention should be paid to any differences between the planned analysis and the actual analysis […] A careful explanation should be provided for deviations from the planned analysis. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- **ICH E9(R1), 2019.** Rapporter chaque analyse « specifying whether each analysis was pre-specified, introduced while the trial was still blinded, or performed post hoc » ; « Changes to the estimand during the trial can be problematic and can reduce the credibility of the trial […] A change to the estimand should usually be reflected through amendment to the protocol. » — [ICH E9(R1)](https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf)
- **Nosek et al. 2018.** « Deviations from data collection and analysis plans are common, even in the most predictable investigations. » Si les résultats n'ont pas encore été observés, on peut « document the changes to her preregistration without undermining diagnosticity ». Après observation, il faut « transparently report changes that were made and why », avec un « increased risk of bias » — [Nosek et al., PNAS 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/)
- **Lakens 2024, sur les changements faits avant les données.** « Sometimes deviations to the preregistration can be made before the data is available. Updating a preregistration can transparently communicate that these decisions were unlikely to suffer from biasing selection effects, as the data was not available when these decisions were made. Updating the preregistration has no consequences for the severity of a test, as long as the updates are independent of the data that is used to test the hypothesis. » Et : « Researchers can preregister analysis code based on simulated data » — [Lakens, Collabra: Psychology 2024](https://doi.org/10.1525/collabra.117094) ([PDF ouvert](https://pure.tue.nl/ws/files/342190925/collabra_2024_10_1_117094.pdf))
- **Lakens 2024, sur les erreurs du plan.** Cinq motifs de déviation, dont « errors in the preregistration » et « violations of untested assumptions ». Pour une erreur, il faut « 1) specify which mistake was made, and correct the mistake, and 2) evaluate the possibility that the deviation from the preregistered analysis plan reduces the severity of the test. This requires evaluating how much flexibility researchers would have when correcting the mistake. » Et : « A principled approach to the use of preregistration should not treat all deviations as problematic. » Pour la forme : « typically as tables where each deviation is a row », avec des numéros de ligne renvoyant au plan et au code — [même source](https://pure.tue.nl/ws/files/342190925/collabra_2024_10_1_117094.pdf)
- **Willroth et Atherton 2024, le modèle de tableau.**
  - Une ligne par déviation, avec des menus pour le type, le motif et le moment.
  - Des colonnes pour « the original text of the preregistration, a description of the deviation, and a reader-impact statement », plus une place pour les « unregistered steps ».
  - Les moments : « before data were collected, during data collection, after data collection but before data were accessed, after data were accessed but before results of preregistered approach were known, and after results of preregistered approach were known ».
  - « It is important to transparently report the timing […] because data-dependent deviations increase risk of bias ».
  - Source : [Willroth & Atherton, AMPPS 2024](https://doi.org/10.1177/25152459231213802) ([copie PDF](https://uopsych.github.io/psy611/readings/willroth_atherton_2024.pdf))
- **OSF.** « Updating a registration is a process of transparently reflecting necessary changes to a study design. » ; « The changes should be implemented only to reflect events outside your control or include unexpected anomalies. » ; une justification est obligatoire pour soumettre une mise à jour — [OSF Help, Entering Updates](https://help.osf.io/article/113-entering-updates)
- **Interne.**
  - Contrôles obligatoires avant le gel, point 3 : « La règle doit montrer les propriétés annoncées ; sinon, on la corrige avant le gel. »
  - Pièce 9 : les énoncés et les actions attendues peuvent servir aux réglages, « les résultats d'agents, jamais. Le danger visé est l'ajustement après avoir regardé des résultats » ; « Après le gel, tout changement est daté et marqué "exploratoire" ».
  - Source : [REGLE.md](ROOT/REGLE.md).
  - L'amendement de R4 du 07/11 est déjà « introduit avant toute donnée d'évaluation », avec l'ancienne définition conservée à côté — [PLAN_EXPERIENCE.md, 1.5](ROOT/PLAN_EXPERIENCE.md).
  - Effet de l'option (b) sur le contrôle complet : seule la répétition 24 de V change. Coût : moteur, tests et plan amendés, puis contrôle 3 refait (environ 3 h) — [RAPPORT.md, 9.3, point 5](ROOT/simulation/controle3/RAPPORT.md)

### Inferences
- **Pourquoi le changement est légitime.**
  - *Le moment.* Avant le gel, avant tout résultat d'agent : c'est la catégorie « before data were collected » de Willroth et Atherton. Pour Lakens, un changement indépendant des données de test ne coûte rien à la sévérité. Pour E9, c'est l'équivalent d'une mise à jour du plan d'analyse avant la levée de l'aveugle.
  - *Le déclencheur.* Un défaut des propriétés de la règle trouvé par simulation : la taille par cellule n'est pas contrôlée. Chez Lakens, c'est à la fois une « error in the preregistration » et une « violation of untested assumptions », puisque le bootstrap suppose plusieurs grappes.
  - *L'information utilisée.* La structure des tâches (l'écriture réversible dans 3 tâches sur 50) est une information de conception, permise par la pièce 9. Ce n'est pas un résultat d'agent.
- **Le risque à maîtriser est la flexibilité** : plusieurs corrections sont possibles (Lakens). Trois parades :
  - écrire le critère de choix avant de relancer le contrôle 3, comme pour R4 et la « règle de choix » de `REGLE.md` ;
  - publier toutes les options examinées avec leurs effets simulés ;
  - préférer la correction qui rétablit la cohérence avec la section 8 sans ajouter de degré de liberté.
- **Ce qu'il faut documenter, d'après E9, E9(R1), Lakens, Willroth et Atherton et OSF.**
  - la date et qui décide ;
  - l'ancien et le nouveau texte côte à côte (déjà la pratique du journal des changements) ;
  - le type : critère d'inférence ;
  - le motif : erreur ou hypothèse violée, trouvée par simulation (RAPPORT 10.7 ; 9.3, point 5) ;
  - le moment : avant le gel, sur données simulées seulement ;
  - l'impact attendu : répétition 24 de V ; exposition dans 6 répétitions sur 12 de A et 3 sur 12 de E ; aviation, enjeu faible ;
  - le prix déclaré : aucune puissance R1 sur les cellules à une tâche, « démontrée » impossible ;
  - les empreintes (commit, tests) et le contrôle 3 refait avec le moteur final.
- **Pas besoin de la mise à jour OSF.** Elle vise des changements postérieurs au dépôt, causés par des « events outside your control ». Le dépôt se fera au gel du 18/11 : l'amendement entre dans la version gelée et dans le journal des changements. Décidé après le 18/11, le même changement serait « exploratoire » (pièce 9). La date de décision compte donc.

### Gaps
- Gamble et al. 2017 (JAMA, lignes directrices sur le contenu des plans d'analyse) : seul le résumé a été lu, et ses items sur l'historique des versions et la justification des révisions ne sont pas vérifiés — [PMID 29260229](https://pubmed.ncbi.nlm.nih.gov/29260229/)
- Pas de page COS trouvée dans cette session sur un modèle « Transparent Changes » : la page d'aide d'OSF la remplace.
- Aucune source trouvée sur les changements de plan dictés par la simulation, avant les données, dans des évaluations préenregistrées d'agents d'IA. La légitimité est établie par extension de Lakens, Nosek et E9.
- Le guide de la FDA sur les plans adaptatifs (simulation des propriétés) n'a pas été consulté.
