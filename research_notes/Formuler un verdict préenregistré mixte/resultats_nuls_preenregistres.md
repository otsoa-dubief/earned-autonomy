# Rapporter un résultat principal nul, négatif ou non concluant dans une étude préenregistrée / un Registered Report

Cadre de lecture pour la suite (vocabulaire retenu dans ces notes) :
- **Effet établi** : la règle de décision préenregistrée se déclenche (test significatif au seuil prévu, IC excluant la valeur nulle).
- **Absence de preuve** (*absence of evidence*) : test non significatif, IC compatible à la fois avec zéro et avec un effet important. Statut : **non concluant / indéterminé**.
- **Preuve d'absence** (*evidence of absence*) : seule une procédure dédiée le permet (test d'équivalence contre une plus petite taille d'effet d'intérêt, SESOI, ou facteur de Bayes en faveur de H0). Sans elle, on ne peut pas écrire « pas d'effet ».

---

## 1. Ce que disent COS/OSF, les critères de Stage 2 et les revues à filière RR

### Takeaway
Les guides RR imposent de rapporter **toutes** les analyses enregistrées, quel que soit le résultat, de séparer confirmatoire et exploratoire, et font juger en Stage 2 si « les conclusions sont justifiées par les données ». Ils disent explicitement qu'un résultat non concluant est publiable et qu'une non-significativité ne vaut jamais soutien à H0. Ils ne donnent **pas** de formule type pour l'abstract.

### Cited Findings
- COS : « Editorial decisions for RRs are made independently of whether the results support the pre-registered hypotheses » ; « Stage 2 manuscripts cannot be rejected because editors or reviewers find the outcomes of hypothesis testing to be surprising, counterintuitive, or unappealing » — [COS, Registered Reports](https://www.cos.io/initiatives/registered-reports)
- COS : acceptation de principe « that will not be revoked based on the outcomes, but only on failings of quality assurance, following through on the registered protocol, or unresolvable problems in reporting clarity or style » — [COS](https://www.cos.io/initiatives/registered-reports)
- COS (FAQ) : « Ensuring high statistical power increases the credibility of all findings, regardless of whether they are clearly positive, clearly negative or inconclusive. » — [COS](https://www.cos.io/initiatives/registered-reports)
- COS (FAQ) : « statistical non-significance, regardless of power, can never be taken as direct support for the null hypothesis. » — [COS](https://www.cos.io/initiatives/registered-reports)
- COS : « the RR model does not prevent or hinder exploration – it simply enables readers to distinguish confirmatory hypothesis testing from exploratory analysis. » — [COS](https://www.cos.io/initiatives/registered-reports)
- Critères de Stage 2 (formulation type, Journal of Cognition, dérivée du modèle Cortex/Chambers) : reviewers décident
  1. « Whether the data are able to test the authors' proposed hypotheses by satisfying the approved outcome-neutral conditions »
  2. « Whether the Introduction, rationale and stated hypotheses are the same as the approved Stage 1 submission (required) »
  3. « Whether the authors adhered precisely to the registered experimental procedures »
  4. « Whether any unregistered post hoc analyses added by the authors are justified, methodologically sound, and informative »
  5. « Whether the authors' conclusions are justified given the data »
  — [Journal of Cognition, RR guidelines](https://journalofcognition.org/about/registered-reports)
- Même guide : « editorial decisions will not be based on the perceived importance, novelty or conclusiveness of the results » ; « The outcome of all registered analyses must be reported in the manuscript » (sauf analyse ensuite reconnue logiquement viciée, d'accord entre auteurs, reviewers et éditeur) ; « the stated hypotheses cannot be amended or appended » — [Journal of Cognition](https://journalofcognition.org/about/registered-reports)
- Analyses exploratoires : « admissible but must be clearly justified in the text, appropriately caveated », dans une section séparée « Exploratory analyses » ; « Authors should be careful not to base their conclusions entirely on the outcome of statistically significant post hoc analyses » — [Journal of Cognition](https://journalofcognition.org/about/registered-reports)
- Plans bayésiens avec taille maximale : celle-ci doit être « sufficiently large that inconclusive results at this sample size would nevertheless be an important message for the field » — [Journal of Cognition](https://journalofcognition.org/about/registered-reports) ; même clause dans [Springer Discover RR guidelines](https://media.springer.com/full/springer-instructions-for-authors-assets/pdf/Registered-report-guidelines-Discover.pdf)
- RSOS (cité par COS) : critère Stage 2 « Whether the data are able to test the authors' proposed hypotheses by passing the approved outcome-neutral criteria » — [COS](https://www.cos.io/initiatives/registered-reports)
- Le critère « conclusions justified given the data » se retrouve chez BMC Biology et ASHA ; JEPS (Cambridge) limite la Stage 2 à l'exécution — [BMC Biology](https://bmcbiol.biomedcentral.com/about/registered-reports) ; [ASHA](https://academy.pubs.asha.org/qa-entry/what-are-the-criteria-for-evaluating-registered-reports/) ; [JEPS FAQ](https://www.cambridge.org/core/journals/journal-of-experimental-political-science/information/faqs-for-registered-reports)
- Méta-recherche : 96 % de résultats positifs dans la littérature standard contre 44 % dans les RR (première hypothèse de chaque article ; 71 RR à nov. 2018 vs 152 études standard) — [Scheel, Schijen & Lakens, préprint PsyArXiv](https://doi.org/10.31234/osf.io/p6e9c), publié dans AMPPS 2021 ([plaudit](https://plaudit.pub/endorsements/doi:10.1177/25152459211007467))

### Inferences
- Pour un verdict mixte, le critère 5 (« conclusions justified given the data ») est le garde-fou : l'abstract ne doit pas affirmer plus que ce que la règle a établi, ni moins (la règle a bien tiré).
- La règle « rapporter toutes les analyses enregistrées » implique de rapporter les 11 unités non concluantes au même rang que l'unité où l'excès est établi, pas en note.
- La réserve « outcome-neutral conditions » est utile : si un volume minimal par unité était prévu comme condition de testabilité, les unités sous le seuil sont « non testées », distinctes des unités « testées, non concluantes ».

### Gaps
- Pages RR de RSOS et Nature Human Behaviour non lisibles (403 / redirection d'authentification) : pas de citation exacte de leurs consignes de Stage 2.
- Aucun guide RR trouvé ne prescrit une formule d'abstract pour un résultat partiellement soutenu.
- Guide reviewers de PCI RR non accessible (erreur 444).

---

## 2. CONSORT 2010/2025, CONSORT pour les résumés, SPIRIT

### Takeaway
CONSORT exige pour chaque critère principal l'estimation de l'effet **et sa précision** (IC 95 %), interdit d'interpréter un résultat non significatif comme une équivalence, dénonce le « spin » dans les résumés, interdit la puissance post hoc comme excuse, et pose explicitement qu'**on ne peut pas inférer un effet de sous-groupe d'un P significatif dans un sous-groupe et non significatif dans un autre**. C'est la règle la plus directement applicable au cas « 1 unité sur 12 ».

### Cited Findings
- CONSORT 2025, item 26 : « For each primary and secondary outcome, by group: • the number of participants included in the analysis • the number of participants with available data at the outcome time point • result for each group, and the estimated effect size and its precision (such as 95% confidence interval) • for binary outcomes, presentation of both absolute and relative effect size » — [CONSORT 2025 E&E, BMJ 2025;389:e081124](https://discovery.ucl.ac.uk/id/eprint/10207694/1/bmj-2024-081124.full.pdf)
- CONSORT 2025, item 28 : « Any other analyses performed, including subgroup and sensitivity analyses, distinguishing prespecified from post hoc » ; item 29 : « Interpretation consistent with results, balancing benefits and harms, and considering other relevant evidence » ; item 30 : « Trial limitations, addressing sources of potential bias, imprecision, generalisability, and, if relevant, multiplicity of analyses » — [CONSORT 2025 E&E](https://discovery.ucl.ac.uk/id/eprint/10207694/1/bmj-2024-081124.full.pdf)
- E&E item 30 : « The difference between statistical significance and clinical importance should always be borne in mind. Authors should particularly avoid the common error of interpreting a non-significant result as indicating equivalence of interventions. The CI (item 26) provides valuable insight into whether the trial result is compatible with a clinically important effect, regardless of the P value. » (réf. 500 = Altman & Bland 1995) — [CONSORT 2025 E&E](https://discovery.ucl.ac.uk/id/eprint/10207694/1/bmj-2024-081124.full.pdf)
- E&E item 30 : « Authors should exercise special care when evaluating the results of trials with multiple comparisons. Such multiplicity arises from several interventions, outcome measures, time points, subgroup analyses, and other factors. In such circumstances, some statistically significant findings are likely to result from chance alone. » — [CONSORT 2025 E&E](https://discovery.ucl.ac.uk/id/eprint/10207694/1/bmj-2024-081124.full.pdf)
- E&E sous-groupes : « It is incorrect to infer a subgroup effect (interaction) from one significant (in one subgroup) and one non-significant P value (in another subgroup). » ; « Post hoc subgroup comparisons (analyses done after looking at the data) are especially likely not to be confirmed by further studies. » — [CONSORT 2025 E&E](https://discovery.ucl.ac.uk/id/eprint/10207694/1/bmj-2024-081124.full.pdf)
- E&E item 29 : « some discussion sections can be overly optimistic when discussing the trial findings (interpretation bias; spin). Authors need to guard against such behaviours, as they diminish the rigour of the scientific effort and may result in a loss of trust by readers. » — [CONSORT 2025 E&E](https://discovery.ucl.ac.uk/id/eprint/10207694/1/bmj-2024-081124.full.pdf)
- E&E item résumé : « abstracts should not be a distorted representation of the trial results » ; « Abstracts are also frequently reported with spin defined as a distorted representation of the study results. Authors should avoid selectively reporting only statistically significant secondary outcomes or subgroup analyses. » — [CONSORT 2025 E&E](https://discovery.ucl.ac.uk/id/eprint/10207694/1/bmj-2024-081124.full.pdf)
- E&E taille d'échantillon : « There is no value in conducting and reporting a post hoc calculation of statistical power using the results of a trial, for example, as a pretext to explain non-significant findings; this may even mislead and confuse readers. » — [CONSORT 2025 E&E](https://discovery.ucl.ac.uk/id/eprint/10207694/1/bmj-2024-081124.full.pdf)
- E&E cite la Déclaration d'Helsinki : « Negative and inconclusive as well as positive results must be published or otherwise made publicly available. » — [CONSORT 2025 E&E](https://discovery.ucl.ac.uk/id/eprint/10207694/1/bmj-2024-081124.full.pdf)
- E&E cite l'étude de référence sur le spin : Boutron et al., « Reporting and interpretation of randomized controlled trials with statistically nonsignificant results for primary outcomes », JAMA 2010;303:2058-64 — [bibliographie CONSORT 2025 E&E](https://discovery.ucl.ac.uk/id/eprint/10207694/1/bmj-2024-081124.full.pdf)
- CONSORT for Abstracts (2008), item résultat : « For the primary outcome, a result for each group and the estimated effect size and its precision. » — [Hopewell et al., PLoS Med 2008](https://doi.org/10.1371/journal.pmed.0050020)
- CONSORT for Abstracts, item conclusions : « General interpretation of the results. » Explication : « The conclusions of the trial, consistent with the results reported in the abstract, should be clearly stated along with their clinical application (avoiding over-generalisation). Authors should balance the benefits and harms in their conclusions. Where applicable, authors should also note whether additional studies are required… » Exemple donné : « Multivitamin supplementation reduced the incidence of low birth weight and small-for-gestational-age births but had no significant effects on prematurity or fetal death » — [Hopewell et al., PLoS Med 2008](https://doi.org/10.1371/journal.pmed.0050020)
- CONSORT 2025 = 30 items + diagramme de flux ; l'item généralisabilité a été fondu dans l'item limites — [ECRIN](https://icss.ecrin.org/en/node/380)

### Inferences
- Appliqué au cas mixte : il est **incorrect** de lire « excès dans l'unité A, rien dans les 11 autres » comme « l'excès est propre à A ». Les 11 autres ne montrent pas l'absence d'excès ; elles ne permettent pas de conclure.
- Le résumé doit mentionner les 12 unités jugées (pas seulement l'unité positive), sinon c'est la forme de spin visée par CONSORT (« selectively reporting only statistically significant … subgroup analyses »).
- L'exemple CONSORT-Abstracts (« no significant effects on … ») montre une formulation encore tolérée en 2008, mais CONSORT 2025 et Altman & Bland poussent plutôt vers « IC compatible avec … » que vers « no significant effect ».
- Multiplicité (12 unités) : signaler si la règle de décision corrige ou non pour 12 tests ; sinon, une détection isolée sur 12 est attendue en partie par hasard.

### Gaps
- Texte de SPIRIT 2025 non consulté : pas de citation sur la manière de prévoir le rapport d'un résultat non concluant au protocole.
- Le texte de l'article principal CONSORT 2025 (vs E&E) non consulté directement ; les citations viennent de l'E&E, qui reprend le checklist.

---

## 3. Lakens et coll. (équivalence, SESOI), Altman & Bland 1995 : formulations

### Takeaway
Sans test d'équivalence ou facteur de Bayes, la seule conclusion correcte après p > α est que « les données ne sont pas surprenantes sous H0 ». Lakens définit quatre issues possibles, dont « undetermined » (ni différent de zéro, ni équivalent) : c'est le statut exact des 11 unités sans volume. Altman & Bland : un essai « négatif » est le plus souvent un essai qui n'a pas pu montrer, pas un essai qui a montré l'absence.

### Cited Findings
- Lakens 2017, résumé : « Scientists should be able to provide support for the absence of a meaningful effect. Currently, researchers often incorrectly conclude an effect is absent based a nonsignificant result. » — [Lakens, SPPS 2017, doi:10.1177/1948550617697177](https://doi.org/10.1177/1948550617697177) (texte : [copie PDF](https://psy505.netlify.app/reading/tost.pdf))
- Lakens 2017 : « When you perform a statistical test, and the outcome is a p value larger than the α level (e.g., p > .05), the only formally correct conclusion is that the data are not surprising, assuming the null hypothesis is true. It is not possible to conclude there is no effect when p > α—our test might simply have lacked the statistical power to detect a true effect. » — [Lakens 2017](https://psy505.netlify.app/reading/tost.pdf)
- Lakens 2017 : « the absence of an effect can be rejected, but not statistically supported » (avec le test classique) ; TOST : bornes fixées sur la « smallest effect size of interest (SESOI; e.g., a positive or negative difference of d = .3) » ; si les deux tests unilatéraux rejettent, « the observed effect falls within the equivalence bounds and is close enough to zero to be practically equivalent » — [Lakens 2017](https://psy505.netlify.app/reading/tost.pdf)
- Lakens 2017, exemple de formulation fautive : « researchers often incorrectly use nonsignificance to claim the absence of an effect (e.g., "there were no gender effects, p > .10") » ; les mots « no effect » relevés dans 108 articles de SPPS — [Lakens 2017](https://psy505.netlify.app/reading/tost.pdf)
- Lakens 2017, quatre issues (NHST + équivalence) : « The effect can be statistically equivalent (larger than ΔL, smaller than ΔU) and not statistically different from zero, statistically different from zero but not statistically equivalent, statistically different from zero and statistically equivalent, or undetermined (neither statistically different from zero nor statistically equivalent). » Scénario D : « an effect can be undetermined, or not statistically different from zero, and not statistically equivalent … when the 90% CI includes one of the equivalence bounds and the 95% CI includes zero. » — [Lakens 2017](https://psy505.netlify.app/reading/tost.pdf)
- Lakens 2017 : à défaut de bornes théoriques, « set the bounds to the smallest effect size they have sufficient power to detect » (approche pragmatique, critiquée comme circulaire) — [Lakens 2017](https://psy505.netlify.app/reading/tost.pdf) ; [synthèse](https://www.citedrive.com/en/discovery/equivalence-tests)
- Lakens, McLatchie, Isager, Scheel & Dienes 2020 : « it is neither logically nor statistically correct to conclude an effect is absent when a hypothesis test is not significant » ; équivalence et facteurs de Bayes servent à « reject the presence of a meaningful or predicted effect » — [J Gerontol B 2020, doi:10.1093/geronb/gby065](https://doi.org/10.1093/geronb/gby065)
- Altman & Bland 1995 : le qualificatif « négatif » « wrongly implies that the study has shown that there is no difference » ; à propos de « there is no evidence that A causes B » ; « While we can never prove the absence of a relation… » ; « confidence intervals are likely to be wide, indicating considerable uncertainty » ; exemple : un essai qui « had only a 5% chance of getting a statistically significant result » ; parmi 71 essais « négatifs » (Freiman), seuls 30 % étaient assez grands pour détecter une différence de 50 % ; méta-analyse fibrinolyse : réduction de mortalité de 22 % très significative mais « only five of the 24 trials had shown a statistically significant effect » — [Altman & Bland, BMJ 1995;311:485 (copie)](https://www.acsu.buffalo.edu/~wdmccall/os512d/EvidAbs.html)
- Altman & Bland (lettre BMJ 2004) : là où l'IC inclut encore des effets cliniquement importants, la conclusion « pas d'effet » n'est pas soutenue ; le titre lui-même vient d'un article de 1983 (Hartung, Cottrell & Giffin, Anesthesiology) — [résumé de résultats de recherche ; lettre non lue en entier](https://pmc.ncbi.nlm.nih.gov/articles/PMC404543)

### Inferences
- Grille de formulations conformes (dérivée des sources ci-dessus) :
  - Effet établi : « La règle préenregistrée est remplie : un excès est établi pour [unité], [estimation, IC]. »
  - Non concluant : « Les données ne permettent pas de conclure » / « nous n'avons pas pu établir … » / « non déterminé (ni excès établi, ni absence établie) », avec IC.
  - À proscrire sans test dédié : « pas d'excès », « aucun effet », « l'effet est limité à [unité] », « négatif ».
  - Preuve d'absence : seulement si une SESOI a été fixée et le test d'équivalence (ou BF) est passé.
- Pour les 11 unités : rapporter le volume et, si possible, la taille d'effet minimale détectable avec ce volume (approche « sensitivity » de Lakens), plutôt qu'une puissance post hoc (que CONSORT déconseille).
- Le verdict global le plus fidèle est donc à trois volets : (1) règle déclenchée, (2) dans 1 unité sur 12 jugeables, (3) 11 non concluantes faute de volume — ni « excès général », ni « excès isolé ».

### Gaps
- Texte intégral BMJ 1995 non accessible sur bmj.com / PMC (403 / captcha) ; citations tirées d'une copie universitaire.
- Le tutoriel Lakens, Scheel & Isager 2018 (AMPPS) n'a pas été consulté pour ses exemples de phrases de résultats.
- Pas de source trouvée prescrivant une phrase canonique « we could not reject / we could not establish » ; la formule « the only formally correct conclusion is that the data are not surprising » est l'équivalent le plus proche.

---

## 4. Exemples publiés (RR / préenregistrés) avec résultat non concluant ou partiellement soutenu

### Takeaway
Les exemples publiés combinent une phrase de cadrage (« contrary to our expectations », « inconsistent with ») et l'estimation chiffrée avec IC ou facteur de Bayes, sans dire « pas d'effet » quand rien n'établit l'absence. Aucun exemple trouvé ne porte exactement sur « 1 unité sur 12 ».

### Cited Findings
- Field et al. 2020, RR (RSOS) — non concluant : « Contrary to our expectations, we report ambiguous Bayes factors and conclude that we do not have strong evidence towards answering our research questions. Our findings are presented along with evidence that our manipulations were ineffective for many participants, leading to the exclusion of 68% of complete datasets, and an underpowered design as a consequence. » Titre : « The effect of preregistration on trust in empirical research findings: results of a registered report » — [RSOS 2020, doi:10.1098/rsos.181351](https://doi.org/10.1098/rsos.181351)
- Wagenmakers et al. 2016, Registered Replication Report (17 labos) — estimation sans verdict verbal dans l'abstract : « The original Strack et al. (1988) study reported a rating difference of 0.82 units on a 10-point Likert scale. Our meta-analysis revealed a rating difference of 0.03 units with a 95% confidence interval ranging from -0.11 to 0.16. » — [Perspect Psychol Sci 2016, doi:10.1177/1745691616674458](https://doi.org/10.1177/1745691616674458)
- Hagger et al. 2016, RRR ego depletion (23 labos, N = 2 141) : « Meta-analysis of the studies revealed that the size of the ego-depletion effect was small with 95% confidence intervals (CIs) that encompassed zero (d = 0.04, 95% CI [-0.07, 0.15]. » — [Perspect Psychol Sci 2016, doi:10.1177/1745691616652873](https://doi.org/10.1177/1745691616652873)
- Exemple CONSORT-Abstracts de résultat mixte (essai, non RR) : « Multivitamin supplementation reduced the incidence of low birth weight and small-for-gestational-age births but had no significant effects on prematurity or fetal death » — [Hopewell et al. 2008](https://doi.org/10.1371/journal.pmed.0050020)
- Exemple CONSORT 2025 (item 29) d'interprétation mixte : réduction du paludisme avec DHA-piperaquine, mais « the risk of adverse pregnancy outcomes (composite primary endpoint) was significantly lower in the sulfadoxine–pyrimethamine group » — [CONSORT 2025 E&E](https://discovery.ucl.ac.uk/id/eprint/10207694/1/bmj-2024-081124.full.pdf)

### Inferences
- Modèle utilisable (structure, pas une citation) : « Conformément à la règle préenregistrée, un excès est établi pour [1] des 12 unités disposant d'assez de données ([estimation, IC]). Pour les 11 autres, les données sont insuffisantes pour conclure dans un sens ou dans l'autre ([fourchette des IC / volumes]). Ce résultat n'établit ni un excès général, ni l'absence d'excès ailleurs. »
- Le modèle Field et al. montre qu'un RR peut afficher dans l'abstract même « we do not have strong evidence towards answering our research questions » tout en expliquant la cause (exclusions, puissance) : précédent direct pour « non concluant faute de volume ».
- Les abstracts RRR mettent l'estimation et l'IC au premier plan, laissant le lecteur juger : cohérent avec CONSORT item 26.

### Gaps
- Pas trouvé d'abstract RR dont le résultat principal est « confirmé dans une sous-unité, indéterminé ailleurs ». Recherche plus poussée (catalogues RR de Cortex, RSOS, PCI RR) nécessaire pour un précédent exact.
- Titres de RR à hypothèse partiellement soutenue : non recensés systématiquement.
