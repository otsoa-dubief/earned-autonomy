# Critère de succès « sûre ET utile » : leçons des essais cliniques et de la statistique confirmatoire

_Notes de recherche du 2026-11-06. Entre guillemets : citations verbatim, laissées en anglais. Les textes FDA, EMA et ICH ont été lus en entier (PDF officiels extraits en local) : leurs citations sont vérifiées mot à mot. Les articles académiques ont été lus au niveau du résumé PubMed, sauf mention contraire. Quelques citations courtes (Lakens, DELTA2, audit CONSORT) viennent d'un outil d'extraction qui rend des fragments : elles sont plus fragiles. Les sections « Inferences » contiennent mes déductions, pas ce que disent les sources._

---

## 1. Guidances réglementaires (FDA 2022, FDA 2016, EMA/ICH E9 et E9(R1), CONSORT NI) : exiger l'efficacité en plus de la sécurité, ordre des tests, contrôle du FWER

### Takeaway
Les textes convergent sur quatre points.
1. Quand le succès exige de gagner sur **tous** les critères, l'erreur de type I ne gonfle pas (il n'y a qu'un chemin vers le succès), mais la puissance baisse.
2. Une NI suivie d'une supériorité sur le **même** critère se teste sans ajustement, dans cet ordre. Dès qu'un second critère entre en jeu, il faut préspécifier l'ordre des tests ou le partage d'α.
3. Pour l'EMA, une différence statistiquement significative n'est pas forcément pertinente cliniquement, et la pertinence se juge à part.
4. Selon ICH E9, on ne conclut jamais à la non-infériorité à partir d'un test non significatif.

### Cited Findings

**Versions et dates**
- FDA, *Multiple Endpoints in Clinical Trials — Guidance for Industry* (CDER/CBER, Biostatistics), version finale datée « October 2022 » — [FDA PDF](https://www.fda.gov/media/162416/download)
- FDA, *Non-Inferiority Clinical Trials to Establish Effectiveness — Guidance for Industry*, version finale datée « November 2016 » — [FDA PDF](https://www.fda.gov/media/78504/download)
- CPMP/EWP/482/99, *Points to consider on switching between superiority and non-inferiority* : « RELEASE FOR CONSULTATION September 1999 », « APPROVAL BY THE CPMP July 2000 » — [EMA PDF](https://www.ema.europa.eu/en/documents/scientific-guideline/points-consider-switching-between-superiority-and-non-inferiority_en.pdf)
- ICH E9, *Statistical Principles for Clinical Trials* : « Current Step 4 version dated 5 February 1998 » — [ICH PDF](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- ICH E9(R1), addendum sur les estimands : adopté au Step 4 le 20 novembre 2019 (« document dated 17 November 2019 ») ; Step 2 le 30 août 2017 — [ICH PDF](https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf). La FDA cite sa propre version de E9(R1) « (May 2021) » — [FDA PDF, note 3](https://www.fda.gov/media/162416/download)
- Extension CONSORT pour les essais NI et d'équivalence : Piaggio et al., JAMA 2012;308(24):2594-604. Elle met à jour la version de 2006 : « recommendations for noninferiority and equivalence trials were made in 2006. In this article, we present an updated extension of the CONSORT checklist ... based on the 2010 version of the CONSORT Statement » — [PubMed 23268518](https://pubmed.ncbi.nlm.nih.gov/23268518/)

**Sécurité, puis efficacité**
- FDA 2022, §II : les critères de sécurité testés entrent dans la multiplicité. « if safety outcomes are to be assessed via hypothesis testing, they would be subject to the multiplicity considerations described in this guidance. Multiplicity problems for safety analyses that are not part of a prespecified set of hypotheses for formal statistical testing are outside the scope of this guidance. » — [FDA 2022](https://www.fda.gov/media/162416/download)
- FDA 2022, §III.A.1, succès conditionné à tous les critères : « The second is when the determination of effectiveness depends on success on all primary endpoints ... In this setting, there are no multiplicity issues related to primary endpoints, as there is only one path that leads to a successful outcome for the trial and therefore, no concern with Type I error rate inflation. » — [FDA 2022](https://www.fda.gov/media/162416/download)
- FDA 2022, §III.A.1, succès sur l'un ou l'autre : « These multiple endpoints thus correspond to multiple chances of success, and in this case, failure to adjust for multiplicity can lead to Type I error rate inflation and a false conclusion that the drug is effective. » — [FDA 2022](https://www.fda.gov/media/162416/download)
- FDA 2016 NI, §I : « This guidance does not provide recommendations for the use of NI study designs to evaluate the safety of a drug. » — [FDA 2016](https://www.fda.gov/media/78504/download)
- FDA 2016 NI : la marge clinique M2 peut être élargie « if the test drug were shown to have some important advantage (e.g., on safety or on a secondary endpoint). » — [FDA 2016](https://www.fda.gov/media/78504/download)
- EMA PtC, §IV.1 : la supériorité suffit si la sécurité est comparable. « Usually this demonstration of a benefit is sufficient on its own, provided the safety profiles of the new agent and the comparator are similar. When there is an increase in adverse events, however, it is important to estimate the size of the effect to evaluate whether it is sufficient in clinical terms to outweigh the adverse effects. » — [EMA PtC](https://www.ema.europa.eu/en/documents/scientific-guideline/points-consider-switching-between-superiority-and-non-inferiority_en.pdf)
- EMA PtC, fin du document : la logique NI s'applique aussi à la sécurité. « The concepts covered in these Points to Consider can also be applied to specific safety variables when these have been pre-identified as major endpoints of a trial to compare active agents. » — [EMA PtC](https://www.ema.europa.eu/en/documents/scientific-guideline/points-consider-switching-between-superiority-and-non-inferiority_en.pdf)
- EMA PtC, §II.1 : la pertinence se juge à part. « in a superiority trial clinical relevance requires separate consideration: a statistically significant difference may not be clinically relevant. The difference taken as the basis of the power calculation in a superiority trial cannot be assumed to provide a suitable value. » — [EMA PtC](https://www.ema.europa.eu/en/documents/scientific-guideline/points-consider-switching-between-superiority-and-non-inferiority_en.pdf)
- ICH E9, §2.2.2 : « There should generally be only one primary variable. This will usually be an efficacy variable ... Safety/tolerability may sometimes be the primary variable, and will always be an important consideration. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- ICH E9, §3.3.2 : « Concluding equivalence or non-inferiority based on observing a non-significant test result of the null hypothesis that there is no difference between the investigational product and the active comparator is inappropriate. » La marge est « the largest difference that can be judged as being clinically acceptable » ; « The choice of equivalence margins should be justified clinically » ; « For non-inferiority trials a one-sided interval should be used. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)

**Ordre des tests (NI → supériorité)**
- FDA 2016 NI, section « G. Testing Non-Inferiority and Superiority in a Single Trial » : « In general, when there is only one primary endpoint and one dose of the test treatment, a trial that is planned to demonstrate non-inferiority may also be used to test for superiority without concern about inflating the Type I error rate. This sequential testing procedure has the Type I error rates for tests of both non-inferiority and superiority controlled at the 2.5% level. » — [FDA 2016](https://www.fda.gov/media/78504/download)
- Même section : « An unplanned determination of non-inferiority following failure to show superiority, when the margin was not determined until results of the trial were known, would not be sufficient for demonstrating non-inferiority ». Avec plusieurs critères : « careful planning of the order in which hypothesis tests are to be carried out is needed ... it would not be appropriate to apply 95% confidence intervals for multiple tests of non-inferiority and superiority across multiple endpoints or multiple doses ... use of larger intervals that reflect adjustment for multiple tests (e.g., 97.5% confidence intervals or higher) may be needed. » — [FDA 2016](https://www.fda.gov/media/78504/download)
- FDA 2016 NI : supériorité trouvée dans un essai NI : « this superiority finding arising in an NI study can be interpreted without adjustment for multiplicity. » — [FDA 2016](https://www.fda.gov/media/78504/download)
- FDA 2022, §IV : « If this endpoint is the only endpoint being tested, then non-inferiority and superiority can be tested without multiplicity adjustment because the null hypotheses of non-inferiority and superiority are naturally ordered ... However, if at least one more endpoint is included for testing, then multiplicity issues arise ... (e.g., test the secondary endpoint only if the primary endpoint superiority is shown or split alpha between the two tests). » — [FDA 2022](https://www.fda.gov/media/162416/download)
- EMA PtC, §IV.1 : « There is no multiplicity argument that affects this interpretation because, in statistical terms, it corresponds to a simple closed test procedure. » Fin du document : « The problem of switching objectives post hoc can be avoided by designing a trial prospectively in the knowledge that both non-inferiority and superiority are outcomes of potential value ... the statistical analysis should be conducted using an appropriate stepwise procedure, progressing from non-inferiority to superiority. » — [EMA PtC](https://www.ema.europa.eu/en/documents/scientific-guideline/points-consider-switching-between-superiority-and-non-inferiority_en.pdf)
- EMA PtC, §IV.2 : une marge non préspécifiée est rarement défendable. « In trials where there is no prospectively defined non-inferiority margin, such a quantity has to be justified after the event and in many situations this will not be possible. » — [EMA PtC](https://www.ema.europa.eu/en/documents/scientific-guideline/points-consider-switching-between-superiority-and-non-inferiority_en.pdf)

**FWER et préspécification**
- FDA 2022, §II.B : « FDA’s concern for controlling the Type I error probability is to minimize the chances of a false favorable conclusion for any primary or secondary endpoints ..., regardless of which and how many of these endpoints in the study have no effect. » Il faut préspécifier « all endpoints in the primary and secondary families » et « all data analyses that will be performed to test hypotheses ». Conventions : « 0.05 for two-sided tests and 0.025 for one-sided tests ». — [FDA 2022](https://www.fda.gov/media/162416/download)
- FDA 2022, §II.C : « The statistical analysis plan should not be changed after unmasking of treatment assignments and performing statistical analyses. » §III.A.3 : « The overall Type I error rate should control for the primary and secondary endpoint families all together. » — [FDA 2022](https://www.fda.gov/media/162416/download)
- ICH E9, §5.6 : « In confirmatory analyses, any aspects of multiplicity which remain after steps of this kind have been taken should be identified in the protocol; adjustment should always be considered and the details of any adjustment procedure or an explanation of why adjustment is not thought to be necessary should be set out in the analysis plan. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- ICH E9, §2.2.5 : « It should be clear whether an impact on any of the variables, some minimum number of them, or all of them, would be considered necessary to achieve the trial objectives. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)

**Estimands (E9(R1))**
- §A.3 : « An estimand is a precise description of the treatment effect reflecting the clinical question posed by a given clinical trial objective ... The targets of estimation are to be defined in advance of a clinical trial. » Attributs : traitement (et comparateur), population, variable, stratégies pour les événements intercurrents, et « a population-level summary for the variable ». — [ICH E9(R1)](https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf)
- §A.1 : l'objectif est une analyse « both aligned to the estimand and pre-specified to a level of detail that it can be replicated precisely by a third party ». Plus loin : « A precise description of the treatment effects of interest should inform sample size calculations. » — [ICH E9(R1)](https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf)

**CONSORT NI (reporting)**
- Audit de 209 essais publiés (Trials, 2012). « The non-inferiority or equivalence margin was defined in most reports (94%) », mais « justified only for a quarter of the trials » (24 %). Pour la taille d'échantillon, « the margin was taken into account in only 78% of the trials reported ». Items audités : « Justification for margin stated », « Sample size calculation using a non-inferiority or equivalence criterion and specifying the margin », « Interpretation correct (non-inferiority/equivalence/superiority/inferiority/inconclusive result ». — [PMC3554513](https://pmc.ncbi.nlm.nih.gov/articles/PMC3554513/)

### Inferences
- **Le défaut, dit en vocabulaire d'essai clinique.**
  - Correspondances :
    - « valider tout » = placebo (aucune délégation) ;
    - liste fixe et tri par risque = comparateurs actifs ;
    - budget d'erreur = marge de NI sur la sécurité ;
    - validations humaines économisées = critère d'efficacité.
  - « Baseline battue par dépassement établi » revient à déclarer un médicament efficace parce que le comparateur actif s'est révélé dangereux. Aucun texte lu ne prévoit ce chemin. Chez la FDA, c'est l'exclusion de M1 (effet > 0 contre placebo) qui fonde l'efficacité.
  - Ici le « placebo » est observé directement dans le rejeu. Un test de supériorité direct contre « valider tout » est donc possible, sans l'hypothèse de constance (« constancy assumption ») de l'essai NI classique.
- **La condition ajoutée ne coûte pas d'α.** « Confirmée » est une conjonction. D'après FDA §III.A.1 et ICH E9 §2.2.5, exiger toutes les conditions ne gonfle pas l'erreur de type I (logique intersection-union). Le prix se paie en puissance (voir §4).
- **Deux sous-conditions actuelles sont des unions, donc des « chances multiples ».**
  - « Baseline battue » = dépassement établi OU davantage de validations établi : deux chemins de succès par baseline. Sans ajustement interne (Holm, ou max-T sur les deux voies), le risque de déclarer à tort une baseline battue peut monter jusqu'à environ 2α (borne de Bonferroni).
  - « Au moins une configuration délégable » est un énoncé existentiel. Si c'est un test, il faut contrôler le FWER sur l'ensemble des configurations.
- **Orientation du test de sécurité : point d'attention.**
  - Si « pas de dépassement établi » signifie « H0 (B-tout respecte le budget) n'a pas été rejetée », c'est un critère d'absence de preuve de nuisance. ICH E9 §3.3.2 juge inapproprié de conclure à la NI sur un test non significatif.
  - Dans ce sens-là, le max-T à 5 % contrôle le risque d'accuser B-tout à tort. Il ne contrôle pas le risque de le déclarer sûr à tort.
  - Avec des erreurs rares et peu de clusters, le test de dépassement est peu puissant, et l'ajustement max-T le rend encore moins sensible.
  - L'orientation NI serait : H0 = taux d'erreur ≥ budget, rejetée si la borne supérieure simultanée est sous le budget. Si le protocole utilise déjà des bornes supérieures, ce point tombe.
- **Ordre des tests suggéré par les textes, transposé.** La sécurité d'abord : « superiority only after NI » (FDA, annexe 7) et « stepwise ... from non-inferiority to superiority » (EMA). L'utilité ensuite. Pour un label conjonctif, l'ordre ne change ni l'α ni la puissance. Il ne compte que pour des labels intermédiaires (voir §2).
- **Préspécification.** Dans un rejeu hors ligne, l'équivalent du « unmasking » de la FDA est le premier calcul des règles sur les runs confirmatoires. Il faut figer avant ce calcul : les seuils (Δ, ρ), l'ordre des tests et le traitement des unions.
- **Peu de clusters.** La sécurité orientée NI, sur des erreurs rares, sera la contrainte de puissance dominante. Une condition d'économie (événement fréquent) coûte peu en comparaison, sauf si le seuil Δ est ambitieux.
- **Niveau α.** Si le 5 % du max-T est unilatéral, c'est le double de la convention réglementaire (0,025 unilatéral, FDA §II.B). C'est défendable pour une recherche, mais il faut l'écrire.

### Gaps
- Libellé exact des items CONSORT NI 2012 (2b, 6a, 7a, 12a, 22) non obtenu : JAMA a bloqué la lecture. Je n'ai que les libellés de l'audit de 2012 et un résumé secondaire (moteur de recherche) donnant « specifying the noninferiority margin with the rationale for its choice », non vérifié mot à mot. Mise à jour de l'extension NI après CONSORT 2025 : non vérifiée.
- Non consultés : la guideline EMA sur la multiplicité (projet EMA/CHMP/44762/2017) et les Points to consider CPMP sur la multiplicité de 2002.
- Piste non vérifiée : la guidance FDA de 2008 sur la sécurité cardiovasculaire des antidiabétiques, exemple classique de porte de sécurité par borne supérieure avant tout claim d'efficacité.
- Dates des projets (drafts) des deux guidances FDA : non vérifiées.

---

## 2. Séquence fixe et gatekeeping (Dmitrienko, Tamhane ; approche graphique de Bretz) : tester plusieurs claims dans l'ordre sans inflation, et sort des claims suivants quand un claim échoue

### Takeaway
Ces procédures sont des tests fermés : elles contrôlent le FWER au sens fort. En séquence fixe, chaque hypothèse est testée à α plein. Dans un graphe, α ne passe à l'hypothèse suivante que si la précédente est rejetée. Quand un test échoue tôt, la suite s'arrête (séquence fixe, gatekeeping série) ou se restreint (gatekeeping parallèle, graphe) : un claim plus loin dans la chaîne ne peut plus être déclaré significatif, même avec une p-valeur minuscule. La littérature « NI sur tous les critères, puis supériorité sur au moins un » (Bloch 2001, Röhmel 2006, Logan & Tamhane 2008) est la forme publiée de « sûre puis utile ».

### Cited Findings
- FDA 2022, annexe 5 (séquence fixe). La procédure exige « (1) prospective specification of the testing sequence and (2) no further testing once the sequence breaks ». Ensuite : « The appeal of the fixed-sequence testing method is that it does not require any alpha adjustment of the individual tests. Its main drawback is that if a hypothesis in the sequence is not rejected, statistical significance cannot be achieved for the endpoints planned for the subsequent hypotheses, even if they have extremely small p-values. » Exemple p = 0,59 puis p = 0,001 : « not considered statistically significant. Ignoring the first endpoint’s result recreates the multiplicity problem ». — [FDA 2022](https://www.fda.gov/media/162416/download)
- FDA 2022, annexe 5 : avec Bonferroni, le second critère « would have shown an effect » ; « It is often not possible to determine a priori the best order for testing (Hung and Wang 2010) ». §III.A.2 : « if a hierarchy is used, the important hypotheses further down the hierarchy might never get tested. » — [FDA 2022](https://www.fda.gov/media/162416/download)
- FDA 2022, annexe 7 (gatekeeping) : « Inferences in each family depend on the acceptance or rejection of null hypotheses in the earlier families ». — [FDA 2022](https://www.fda.gov/media/162416/download)
  - Série : « If, however, at least one of the null hypotheses of the primary family fails to be rejected, the primary family criterion has not been met and the secondary endpoint family is not tested. »
  - Parallèle : « the second endpoint family is examined when at least one of the endpoints in the first family has shown statistical significance. »
- FDA 2022, annexe 7, cas NI + supériorité : « if the goal of a study is to demonstrate non-inferiority as well as superiority, a single path of sequential tests is preferred ». Restriction logique : « Test for superiority on an endpoint only after non-inferiority for that endpoint is first concluded. » Et : « if multiple branches split off from a single node, the alpha should be split across the multiple branches. » — [FDA 2022](https://www.fda.gov/media/162416/download)
- FDA 2022, annexe 8 (graphe). Le poids d'une arête « indicates the fraction of the preserved alpha to be shifted along that path to the receiving hypothesis, when the hypothesis at the tail end of the path is successful (i.e., is rejected) » ; « A key requirement is that the sum of all of the endpoint-specific alpha levels is equal to the total alpha level ». Séquence fixe vue comme un graphe : « if the test of H1 is unsuccessful, there is no pre-assigned non-zero alpha for H2 to allow testing of H2 ». — [FDA 2022](https://www.fda.gov/media/162416/download)
- FDA 2022, §IV : pour des relations logiques complexes, il existe des « graphical approaches (e.g., Bretz et al. 2009) and mixture gatekeeping procedures (Dmitrienko et al. 2008). The graphical method has a sequential testing algorithm and makes it possible to visualize the testing process via a graph. » — [FDA 2022](https://www.fda.gov/media/162416/download)
- Bretz, Maurer, Brannath, Posch, Stat Med 2009;28(4):586-604 : « gatekeeping procedures, fixed sequence tests, and fallback procedures ... allow to map the difference in importance as well as the relationship between the various research questions onto an adequate multiple test procedure. Since these procedures rely on the closed test principle, they usually require the explicit specification of a large number of intersection hypotheses tests ... » Les procédures sont représentées par des « directed, weighted graphs, where each node corresponds to an elementary hypothesis ». — [PubMed 19051220](https://pubmed.ncbi.nlm.nih.gov/19051220/)
- Bretz, Maurer, Hommel, Stat Med 2011 : discute « suitable power measures for clinical trials with multiple primary and/or secondary objectives ». — [PubMed 21290405](https://pubmed.ncbi.nlm.nih.gov/21290405/)
- Maurer, Bretz, Posch, Pharm Stat 2022 : l'approche graphique contrôle « the familywise error rate » ; « A critical step is to update the transition weights following a pre-specified algorithm ». — [PubMed 35819117](https://pubmed.ncbi.nlm.nih.gov/35819117/)
- Dmitrienko & Tamhane, Pharm Stat 2007;6(3):171-80 : « analysis of hierarchically ordered multiple objectives. Testing procedures for this problem are known as gatekeeping procedures ... serial and parallel gatekeeping procedures, and tree gatekeeping procedures that account for logical restrictions among multiple objectives. » — [PubMed 17583553](https://pubmed.ncbi.nlm.nih.gov/17583553/)
- Brechenmacher, Xu, Dmitrienko, Tamhane, J Biopharm Stat 2011 : « When conducting clinical trials with hierarchically ordered objectives, it is essential to use multiplicity adjustment methods that control the familywise error rate in the strong sense while taking into account the logical relations among the null hypotheses. » — [PubMed 21516567](https://pubmed.ncbi.nlm.nih.gov/21516567/)
- Röhmel, Gerlinger, Benda, Läuter, Biom J 2006 : cas de deux critères primaires « in which superiority in one of them would suffice given that non-inferiority is observed in the other ». — [PubMed 17240652](https://pubmed.ncbi.nlm.nih.gov/17240652/)
  - Procédure : « We propose a hierarchical three step procedure, where non-inferiority in both variables must be proven in the first step, superiority has to be shown by a bivariate test ... in the second step, and then superiority in at least one variable has to be verified in the third step ... All statistical tests are performed at the same one-sided significance level alpha. »
  - Puissance : « depends to a considerable degree on the correlation and on the magnitude of the expected effects ».
- Bloch, Lai, Tubert-Bitter, Biometrics 2001 : montrer qu'un traitement est « superior to the current standard for some components ... and is not inferior, modulo biologically unimportant difference to the standard treatment for all other components ». — [PubMed 11764242](https://pubmed.ncbi.nlm.nih.gov/11764242/)
- Logan & Tamhane, Biom J 2008 : proposent « a closed testing formulation which generalizes the three-step procedure proposed by Röhmel et al. ». Pour l'étape de supériorité globale, ils recommandent « the one-sided likelihood ratio test used by Perlman and Wu (2004) or the union-intersection t(max) test used by Tamhane and Logan (2004) ». — [PubMed 18932132](https://pubmed.ncbi.nlm.nih.gov/18932132/)
- FDA 2022, annexe 6 (méthodes par rééchantillonnage, comme un max-T bootstrap). Elles peuvent « provide more power ... while maintaining control of the overall Type I error rate, and the power increases as the correlation increases ». Mais : « These methods, consequently, usually require large study sample sizes (particularly bootstrap methods) and often require simulations to ensure ... adequate Type I error rate control. » — [FDA 2022](https://www.fda.gov/media/162416/download)

### Inferences
- **Hiérarchie candidate (avis, non sourcé).** On teste dans cet ordre, chaque test à α plein, et on s'arrête au premier échec :
  1. H1 : sécurité de B-tout ;
  2. H2 : économie > 0 contre « valider tout » ;
  3. H3 : économie ≥ Δ, ou ≥ ρ × gain de l'oracle ;
  4. H4 : baselines battues, avec un Holm interne aux deux voies.

  Cela permet des labels intermédiaires sous FWER contrôlé : « sûre » (H1), « sûre et utile » (H1 à H3), « confirmée » (tout).
- **Si H1 échoue, rien d'autre n'est revendiquable**, même avec une économie spectaculaire (exemple FDA : p = 0,59 puis p = 0,001). C'est la sémantique voulue : pas de claim d'utilité pour une règle qui n'est pas sûre.
- **H3 avant H4 est un vrai choix.** Si H3 échoue, les comparaisons aux baselines ne sont plus testables. Pour garder ces claims malgré tout, un graphe de Bretz peut partager α entre H3 et H4 après H2 (FDA annexe 7 : « the alpha should be split across the multiple branches »). Pour un label purement conjonctif, ce partage est inutile et coûte de la puissance.
- **Analogue publié.** Röhmel 2006 et Logan & Tamhane 2008 sont la forme établie de « sûre puis utile » : NI sur tout en étape 1, supériorité ensuite, au même α unilatéral, dans un cadre de tests fermés.
- **Le max-T bootstrap relève de l'annexe 6 de la FDA.** Avec 20 clusters, il faut calibrer son erreur de type I par simulation, sous des scénarios nuls construits : B-tout exactement au budget, économie exactement à Δ.
- **Peu de clusters.** La séquence fixe ne « dépense » pas d'α sur les premiers tests. Mais la probabilité d'atteindre l'étape k est plafonnée par la puissance des étapes précédentes. Ici la logique impose la sécurité en premier, alors que c'est probablement le test le moins puissant (erreurs rares) : il plafonne tout le reste.

### Gaps
- Bretz 2009 et Dmitrienko & Tamhane 2007 lus au niveau du résumé seulement : la formule de mise à jour des poids et les conditions de cohérence (consonance, α-exhaustivité) ne sont pas extraites.
- Dmitrienko, Tamhane & Wiens 2008 (mixture gatekeeping, cité par la FDA) : non consulté.

---

## 3. MCID et « smallest effect size of interest » (SESOI) : choix et justification avant les données ; un claim de supériorité peut-il exiger que la borne dépasse le MCID plutôt que zéro ?

### Takeaway
Oui. C'est un « minimum effect test » (Lakens), ou le troisième rôle possible du MCID chez Chuang-Stein et al. (2011) : tester H0 : effet ≤ MCID. Le rejet établit un effet à la fois statistiquement et pratiquement significatif, mais demande plus de données qu'un test contre zéro. Le seuil se justifie par :
- un ancrage (jugement du patient ou du soignant) ;
- la distribution des données ;
- un calcul économique ou coût-bénéfice ;
- l'avis des parties prenantes ;
- une étude pilote ;
- la revue des preuves existantes ;
- en dernier recours, une taille d'effet standardisée.

Dans tous les cas, il est fixé avant les données. Les essais NI offrent un analogue direct de la « part minimale du gain d'un oracle » : préserver une fraction préspécifiée de l'effet du comparateur (M2 exprimé en % de M1).

### Cited Findings
- Chuang-Stein, Kirby, Hirsch, Atkinson, Pharm Stat 2011 : trois rôles possibles du MCID. — [PubMed 20936625](https://pubmed.ncbi.nlm.nih.gov/20936625/)
  - « (1) using the MCID to determine the required sample size so that the trial has a pre-specified statistical power to conclude a significant treatment effect when the treatment effect is equal to the MCID; (2) requiring with high probability, the observed treatment effect in a trial, in addition to being statistically significant, to be at least as large as the MCID; (3) demonstrating via hypothesis testing that the effect of the new treatment is at least as large as the MCID. »
  - Ils examinent les conséquences « on sample size, expectations of a new treatment, and the chance for a successful trial ».
- Lakens, chapitre 9 de *Improving Your Statistical Inferences* (fragments). — [Lakens, ch. 9](https://lakens.github.io/statistical_inferences/09-equivalencetest.html)
  - Test d'effet minimum : « it is called a minimum effect test » ; « whenever it is rejected, the effect is both statistically and practically significant ».
  - Coût : il « requires more observations than if the goal had been to reject an effect of zero » ; « it takes a very large sample size to have high power to reliably reject very small effects ».
- Lakens, ch. 9, préspécification : « The equivalence range should be specified in advance » ; « if you only think about the possibility of observing a null effect when the data has been collected, it is often too late ». — [Lakens, ch. 9](https://lakens.github.io/statistical_inferences/09-equivalencetest.html)
- Lakens, ch. 9, justifications du SESOI. — [Lakens, ch. 9](https://lakens.github.io/statistical_inferences/09-equivalencetest.html)
  - MCID : « a minimal important difference, or clinically significant difference » ; ancrage : « Often, the patient is directly asked to answer the anchor question ».
  - Coût-bénéfice : « Another principled approach to justify a smallest effect size of interest is to perform a cost-benefit analysis. »
  - Ressources : « Setting the smallest effect size of interest based on this approach does not answer any theoretical question ».
  - « Small telescopes » : l'effet « that would give 33% power to the original study ».
- Lakens, ch. 9, quatre issues possibles quand on combine un test d'égalité et un test d'équivalence. — [Lakens, ch. 9](https://lakens.github.io/statistical_inferences/09-equivalencetest.html)
  - Les deux significatifs : « you can claim there is an effect, but at the same time claim the effect is too small to be of interest ».
  - Les deux non significatifs : « inconclusive ».
- Lakens, SPPS 2017 : bornes fixées « based on the smallest effect size of interest » ; « In randomized controlled trials, it is expected that equivalence bounds are prespecified » ; « the maximum sample size you are willing to collect implicitly determines your SESOI » ; « both one-sided tests need to be significant to declare equivalence » ; « A 90% confidence interval (CI; 1 − 2α) is used instead of a 95% CI (1 − α) » ; « Error rates in equivalence tests are controlled at the α level when the true effect equals the equivalence bound. » — [PMC5502906](https://pmc.ncbi.nlm.nih.gov/articles/PMC5502906/)
- DELTA2, BMJ 2018;363:k3750 : choisir la différence cible. — [PMC6216070](https://pmc.ncbi.nlm.nih.gov/articles/PMC6216070/)
  - Principe : « a key principle is that the target difference should be viewed as important by at least one (and preferably more) key stakeholder groups ». Les groupes cités sont patients, professionnels de santé, agences réglementaires, financeurs.
  - Deux approches : « Important to one or more stakeholder groups » / « Realistic (plausible), based on either existing evidence, or expert opinion. » ; « It has been argued that a target difference should always be both important and realistic ».
- DELTA2, Box 2, méthodes de choix (étiquettes) : « Anchor », « Distribution », « Health economic », « Opinion seeking », « Pilot study », « Review of evidence base », « Standardised effect size ». — [PMC6216070](https://pmc.ncbi.nlm.nih.gov/articles/PMC6216070/)
- DELTA2, autres recommandations. — [PMC6216070](https://pmc.ncbi.nlm.nih.gov/articles/PMC6216070/)
  - « Specifying the target difference based solely on a standardised effect size approach should be considered a last resort » ; « The choice should not be based solely on which outcome yields the minimum sample size. »
  - La différence cible « does not necessarily have to be the minimum value that would be considered important » ; « A key question of interest is what magnitude of difference can be ruled out. »
  - « Failure to clarify sufficiently what is important and realistic at the design stage can lead to subsequent sample size revisions ».
- Jaeschke, Singer, Guyatt, Control Clin Trials 1989 (origine du MCID par ancrage) : on compare les changements de score à des « global ratings of change » ; « the MCID was represented by mean change in score of approximately 0.5 per item, when responses were presented on a seven point Likert scale ». — [PubMed 2691207](https://pubmed.ncbi.nlm.nih.gov/2691207/)
- Man-Son-Hing et al., J Gen Intern Med 2002 : juger l'importance clinique d'un résultat par « the relationship between the point estimate of the treatment effect (with its associated confidence interval) and the estimate of the smallest treatment effect that would lead to a change in a patient's management ». — [PubMed 12133163](https://pubmed.ncbi.nlm.nih.gov/12133163/)
- EMA PtC, §II.1 : « Whether the observed difference is indeed clinically relevant is a matter of judgement » ; « The difference taken as the basis of the power calculation in a superiority trial cannot be assumed to provide a suitable value. » — [EMA PtC](https://www.ema.europa.eu/en/documents/scientific-guideline/points-consider-switching-between-superiority-and-non-inferiority_en.pdf)
- FDA 2016 NI, fraction préservée de l'effet du comparateur. — [FDA 2016](https://www.fda.gov/media/78504/download)
  - Définition : « M2 = the largest clinically acceptable difference (degree of inferiority) of the test drug compared to the active control » ; « The choice of M2 is a matter of clinical judgment, but M2 can never be greater than M1 ».
  - Forme : M2 peut être exprimée « as an absolute difference in effect (typical of antibiotic trials) or as a fraction of the risk reduction provided by the control (typical in cardiovascular outcome trials) ».
- FDA 2016 NI, exemples de fraction. — [FDA 2016](https://www.fda.gov/media/78504/download)
  - « M2 might be chosen to be 40% of M1. By meeting this M2 criterion, ruling out a loss of 40% of the effect of the control, a single NI study provides reasonable assurance that the test drug preserves a clinically sufficient fraction (at least 60%) of the effect of the control treatment. »
  - Streptokinase : « A clinical decision was made that any new thrombolytic should rule out a loss of more than half of the benefit of streptokinase ».
  - « If M2 is ruled out, then the effect of the test drug has been shown to preserve a clinically important fraction of the effect of the control drug. »
- FDA 2016 NI, conditions de validité. M1, même préspécifié, peut devoir être « “discounted” ». Une étude conçue pour la supériorité ne prouve la NI que si « the NI margin must be prespecified, and assay sensitivity and HESDE must be established ». — [FDA 2016](https://www.fda.gov/media/78504/download)
- ICH E9, §2.2.3 : pour un critère combiné, « an interpretation of the resulting scale should be provided in terms of the size of a clinically relevant benefit. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)

### Inferences
- **On peut exiger une borne au-dessus de Δ plutôt qu'au-dessus de zéro.** C'est le rôle (3) de Chuang-Stein, c'est-à-dire le test d'effet minimum de Lakens. L'EMA appuie l'idée qu'une significativité contre zéro ne prouve pas la pertinence. En pratique réglementaire, l'efficacité se teste plutôt contre zéro et la pertinence se juge ensuite (« matter of judgement »). Je n'ai trouvé aucune guidance qui impose H0 : effet ≤ MCID pour une autorisation : ce serait un standard plus strict que l'usage.
- **Arithmétique de puissance** (mon calcul, approximation normale, α unilatéral 2,5 %, puissance 80 %) :
  - Rôle (1) : si on dimensionne pour 80 % à δ = Δ, l'erreur type vaut Δ/2,80 et le seuil de significativité sur l'estimation vaut 1,96/2,80 × Δ ≈ 0,70 Δ. Un résultat « significatif » peut donc afficher une économie observée inférieure d'environ 30 % à Δ.
  - Rôle (2) : si la vraie valeur vaut exactement Δ, P(estimation ≥ Δ) = 50 %. La puissance plafonne à 50 %.
  - Rôle (3) : à δ = Δ, la puissance vaut α. Pour 80 %, il faut un vrai δ ≈ Δ + 2,80 erreurs types.
- **Lecture des trois conditions candidates.**
  - **(a) Économie établie > 0 contre « valider tout ».** C'est le test contre zéro. Il ferme le trou « ne délègue rien », pas le trou « délègue presque rien ». L'économie est ≥ 0 par construction et l'événement est fréquent, donc ce test passera souvent pour des gains minimes (le « significant but not relevant » de l'EMA).
  - **(b) Économie ≥ Δ préspécifié.** C'est le rôle (3). Pour justifier Δ selon DELTA2 et Lakens :
    - ancrage : quelle économie l'opérateur perçoit-il ?
    - coût-bénéfice : coût d'une validation humaine × volume, face au coût d'exploitation et de surveillance de la règle ; le seuil de rentabilité donne Δ ;
    - avis des utilisateurs ;
    - économies publiées pour des dispositifs humain-dans-la-boucle ;
    - les ressources seulement en dernier recours.

    Variante plus douce, le rôle (2) : borne inférieure > 0 ET estimation ≥ Δ.
  - **(c) Part ≥ ρ du gain de l'oracle.** C'est l'analogue de M2 exprimé en fraction de M1 (« preserves ... at least 60% of the effect »).
    - Avantages : le critère ne dépend pas de l'échelle, donc il se compare d'un environnement à l'autre. Et l'oracle est calculé sur les mêmes runs (comparaison concurrente, appariée) : pas d'hypothèse de constance ni de M1 à rabattre comme avec un témoin historique.
    - Forme de test conseillée : linéarisée, H0 : S_B − ρ·S_O ≤ 0 sur la différence par cluster d_g = S_B,g − ρ·S_O,g. Cela évite un ratio de moyennes instable quand le gain de l'oracle est proche de zéro.
    - Piège : si l'oracle ne gagne presque rien dans un environnement, le critère n'apprend rien. La condition actuelle « au moins une configuration délégable » joue alors le rôle de l'« assay sensitivity » des essais NI.
- **L'asymétrie M1/M2 de la FDA donne deux niveaux de claim.** Exclure « aucune économie » (équivalent de M1 : un effet existe) ou exclure « économie insuffisante » (équivalent de M2 : une fraction suffisante est préservée). C'est exactement (a) contre (b)/(c), et cela peut fonder deux labels.
- **Avis.** La condition qui corrige le mieux le défaut tout en restant confirmatoire est (b) ou (c), testée en forme de test d'effet minimum (linéarisée pour (c)). Comme Δ > 0 ou ρ > 0 impliquent (a), on peut garder (a) comme porte dans la séquence. Choisir (b) si on sait justifier a priori une économie absolue qui compte pour quelqu'un. Choisir (c) si la priorité est de comparer des environnements hétérogènes. Garder l'autre en critère secondaire ou descriptif, pour ne pas multiplier les co-primaires (§4).
- **Peu de clusters.** (b) et (c) sont des tests d'effet minimum : ils demandent plus de données qu'un test contre zéro. Avec G = 20, il faut s'attendre à une puissance faible, sauf si la vraie économie dépasse largement Δ. Il faut fixer Δ ou ρ en connaissant la différence minimale détectable de chaque environnement (§5), sans pour autant laisser ce seul critère de ressources fixer le seuil (Lakens : il « does not answer any theoretical question »).

### Gaps
- Chuang-Stein 2011 : texte intégral non lu, donc ni leur recommandation finale ni leurs tables. Seul le résumé a été lu.
- Lakens, Scheel & Isager 2018 (tutoriel AMPPS sur l'équivalence) : inaccessible (erreur 403). Remplacé par Lakens 2017 et le chapitre 9 du livre.
- Recherche non exhaustive : aucun texte réglementaire trouvé qui exige une borne de supériorité au-dessus du MCID. Ne pas l'avoir trouvé ne prouve pas qu'il n'en existe pas.
- Définition canonique du MCID (« the smallest difference in score ... which patients perceive as beneficial ... ») : elle n'est pas dans le résumé de Jaeschke 1989, donc non citée verbatim ici.

---

## 4. Critères co-primaires (« gagner sur les deux ») contre critères composites : coût en puissance

### Takeaway
Des critères co-primaires relèvent d'un test intersection-union : pas d'ajustement d'α, mais une puissance qui chute à peu près multiplicativement. Exemple FDA : deux critères indépendants à 80 % chacun donnent 64 % ensemble, d'où la recommandation de viser environ 90 % par critère. La FDA refuse de relever l'α de chaque critère pour compenser. Un critère composite (ou multi-composantes) se teste en un seul test, sans multiplicité, et peut gagner en puissance. Mais il peut masquer une nuisance sur la composante la plus importante : les composantes doivent toujours être examinées, et l'algorithme de combinaison doit être préspécifié avec une échelle interprétable.

### Cited Findings
- FDA 2022, §III.B : « Using two or more endpoints for which demonstration of an effect on each is recommended to support regulatory approval (called co-primary endpoints ...) will increase the Type II error rate and decrease study power. ... If the endpoints are independent, the power to show success on both will be approximately 64% (0.8 x 0.8); i.e., ... the Type II error rate ... would be 36%. To maintain desired study power, a larger sample size is recommended, and the individual endpoints could be powered at approximately 90% to ensure the probability of success is at least 80%. The calculation would be different if the endpoints were highly positively correlated or the power was not equal for each endpoint. » — [FDA 2022](https://www.fda.gov/media/162416/download)
- FDA 2022, §III.C.1 : « Multiple primary endpoints become co-primary endpoints when demonstrating an effect on each of the endpoints is critical to concluding that a drug is effective. » — [FDA 2022](https://www.fda.gov/media/162416/download)
  - Multiplicité et puissance : « there is no multiplicity problem when the study is designed to demonstrate efficacy on all of the separate endpoints. However, co-primary endpoint testing increases the Type II error rate. In general, unless clinically very important, the use of more than two co-primary endpoints should be carefully considered because of the loss of power. »
  - Compensation refusée : « Increasing α for each co-primary endpoint is not acceptable because doing so may undermine the ability to interpret a treatment effect on each disease aspect considered critical to show that the drug is effective ».
- ICH E9, §2.2.5 : « If the purpose of the trial is to demonstrate effects on all of the designated primary variables, then there is no need for adjustment of the type I error, but the impact on type II error and sample size should be carefully considered. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- Chuang-Stein, Stryszak, Dmitrienko, Offen, Stat Med 2007 : l'exigence co-primaire est « rooted in the intersection-union (IU) test, has led many researchers to increase the study sample size ... the increase in sample size could be substantial when the endpoints are minimally correlated and the treatment effects on the multiple endpoints are comparable ». Ils proposent de contrôler une erreur de type I moyenne, idée que la FDA écarte en 2022 (citation précédente). — [PubMed 16927251](https://pubmed.ncbi.nlm.nih.gov/16927251/)
- FDA 2022, §III.C.3 (composite). — [FDA 2022](https://www.fda.gov/media/162416/download)
  - Multiplicité : « If a single statistical test is performed on the composite endpoint, no multiplicity problem will occur for this endpoint. »
  - Puissance : le composite « can provide a substantially higher overall event rate that allows a study with a reasonable sample size and study duration to have adequate power ».
- FDA 2022, §III.C.3, mises en garde. — [FDA 2022](https://www.fda.gov/media/162416/download)
  - Le composite « will not be a reasonable indicator of the effect on all of the components ... if the clinical importance of different components is substantially different and the treatment effect is chiefly on the least important event. Furthermore, it is possible that a component with greater importance would be adversely affected by the treatment, even if one or more event types of lesser importance are favorably affected ».
  - « The examination of the components is always necessary, but whether multiplicity adjustment should be made depends on the purpose. »
- FDA 2022, §III.C.4 (multi-composantes intra-sujet) : il « may be efficient if the treatment effects on the different components are generally trending in the same direction within a subject. Study power can be adversely affected, however, if there is limited concordance among the endpoints » ; le choix est « generally determined by clinical, rather than statistical, considerations. » — [FDA 2022](https://www.fda.gov/media/162416/download)
- FDA 2022, §III.A.3 et §III.C.5 : un critère crucial mais trop rare (mortalité) se met en secondaire, ou dans un composite plus en secondaire, pendant que le critère fréquent est primaire. — [FDA 2022](https://www.fda.gov/media/162416/download)
- ICH E9, §2.2.3 : le composite « addresses the multiplicity problem without requiring adjustment to the type I error. The method of combining the multiple measurements should be specified in the protocol ». — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- ICH E9(R1), §A.3.2, stratégie de variable composite : « An intercurrent event is considered in itself to be informative about the patient’s outcome and is therefore incorporated into the definition of the variable. For example, a patient who discontinues treatment because of toxicity may be considered not to have been successfully treated. » — [ICH E9(R1)](https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf)

### Inferences
- **Composite « bénéfice net » pour B-tout : à déconseiller comme critère principal.** Un indice du type économie − λ × erreurs en excès éviterait la perte de puissance de la conjonction. Mais il exige un λ préspécifié : un taux de change entre une validation économisée et une erreur laissée passer, à justifier comme les poids d'un composite. Surtout, il peut masquer un échec de sécurité, ce que la FDA signale explicitement. Quand la sécurité est une contrainte dure, il vaut mieux garder la structure co-primaire « sûre ET utile ». C'est cohérent avec la FDA, qui réserve le co-primaire aux aspects « critically important ».
- **Corrélation défavorable.** Plus B-tout délègue, plus il s'expose aux erreurs. Passer la sécurité et passer l'économie sont donc probablement corrélés négativement. La puissance jointe peut alors tomber sous le produit des puissances, alors que la FDA ne commente que le cas d'une corrélation positive. Il faut estimer la puissance jointe par simulation, pas par la formule du produit.
- **Trop de co-primaires.** Aujourd'hui, « confirmée » cumule déjà la sécurité et une condition par baseline. Ajouter l'économie fait au moins quatre conditions conjointes, quand la FDA demande de bien réfléchir au-delà de deux. Option : famille primaire = {sécurité, économie ≥ Δ (ou ≥ ρ × oracle) contre « valider tout »}, et famille secondaire en gatekeeping série = {bat la liste fixe, bat le tri par risque}.
- **Événements intercurrents.** La stratégie composite de E9(R1) peut servir à définir ce qui arrive dans un run : interruption, reprise en main humaine, run avorté. On peut les compter comme échec ou comme erreur dans la variable.
- **Peu de clusters.** En co-primaire, la puissance jointe est le produit de puissances déjà limitées par G : à G = 20, elle peut être très basse. C'est un argument de plus pour deux co-primaires au maximum.

### Gaps
- Non consultés : Offen et al. 2007 (DIJ, « Multiple co-primary endpoints: medical and statistical solutions ») et le livre de Sozu, Sugimoto et Hamasaki sur les co-primaires. Aucune table d'inflation de taille d'échantillon selon la corrélation n'a été extraite.
- Aucune source trouvée sur des co-primaires corrélés négativement par construction (compromis sécurité/efficacité). L'effet sur la puissance est déduit, pas sourcé.

---

## 5. Puissance avec peu de clusters : ce que disent les guides des essais en clusters (corrections petits échantillons, problème des « few clusters ») sur la préspécification des tailles d'effet

### Takeaway
Avec peu de clusters, l'inférence non corrigée (variance robuste, modèles mixtes, GEE) rejette trop souvent, même jusqu'à 70 clusters. Les corrections petits échantillons et les analyses au niveau du cluster rétablissent l'erreur de type I, mais la puissance reste faible : sous 50 % dans certains scénarios à moins de 20 clusters. Quand le nombre de clusters est fixé, la puissance a un plafond. Il existe une différence minimale détectable, quelle que soit la taille des clusters. D'où trois consignes : préspécifier cette différence minimale (ou la puissance maximale atteignable), intégrer les corrections dans le calcul de taille, et se méfier quand la variation se concentre dans quelques clusters.

### Cited Findings
- Kahan et al., Trials 2016 : « using mixed-effects models or GEEs without an appropriate correction led to inflated type I error rates, even for as many as 70 clusters. Conversely, using small-sample corrections provided correct type I error rates across all scenarios. » — [PubMed 27600609](https://pubmed.ncbi.nlm.nih.gov/27600609/)
  - Réanalyse d'un essai à 6 clusters : « inappropriate methods of analysis gave much smaller P values (P ≤ 0.01) than appropriate methods (P = 0.04-0.15) ».
  - Revue de 99 essais : 65 % « at risk of an increased type I error rate ». Le seuil de « fewer than 40 clusters » sans correction est leur critère de classement, pas une règle.
- Leyrat et al., Int J Epidemiol 2018 : simulation de 12 analyses pour des essais à 40 clusters ou moins. — [PubMed 29025158](https://pubmed.ncbi.nlm.nih.gov/29025158/)
  - Les approches corrigées « all maintained the type I error rate at or below 5% across most scenarios, whereas uncorrected approaches lead to inflated type I error rates. However, these analyses had low power (below 50% in some scenarios) when fewer than 20 clusters were randomized, with none reaching the expected 80% power. »
  - Conclusion : « The use of these corrections should be incorporated into the sample size calculation to prevent studies from being underpowered. »
- Hemming et al., BMC Med Res Methodol 2011, nombre de clusters fixé : l'essai est faisable si le nombre de clusters dépasse le produit nI × ρ (effectif requis en randomisation individuelle × corrélation intra-cluster). — [PubMed 21718530](https://pubmed.ncbi.nlm.nih.gov/21718530/)
  - Sinon, « investigators can determine the maximum available power to detect the pre-specified difference, or the minimum detectable difference under the pre-specified value for power. »
  - Conclusion : « leading to the notion of a minimum detectable difference (or a maximum achievable power), irrespective of how many individuals are included within each cluster. »
- Taljaard et al., Clin Trials 2016 : « substantial risks associated with few clusters, including increased probability of chance imbalances and type I and type II error, limited perceived or actual generalizability, and fewer options for statistical analysis ». Les designs avec mesures avant intervention « can substantially reduce the required numbers of clusters by decreasing between-cluster sources of variation ». — [PubMed 26940696](https://pubmed.ncbi.nlm.nih.gov/26940696/)
- Cameron & Miller, *A Practitioner’s Guide to Cluster-Robust Inference* (version auteurs, février 2015), définition de « few » : « There is no clear-cut definition of “few”; depending on the situation “few” may range from less than 20 to less than 50 clusters in the balanced case » ; « and even more clusters in the unbalanced case » ; « Current consensus appears to be that G = 50 is enough for state-year panel data. » — [Cameron & Miller PDF](http://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
- Cameron & Miller, les deux problèmes : l'« overfitting » rend l'estimation de variance biaisée vers le bas, et il y a sur-rejet « if the critical values are from the standard normal or even the T(G − 1) distribution ». — [Cameron & Miller PDF](http://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
- Cameron & Miller, ordres de grandeur (simulations de Cameron, Gelbach et Miller 2008, valeur critique 1,96). — [Cameron & Miller PDF](http://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
  - Variance robuste standard : taux de rejet de .068, .081, .118 et .208 pour G = 30, 20, 10 et 5.
  - Avec la correction jackknife CR3 (« equal the delete-one-cluster jackknife estimate ») : .062, .070, .092 et .138, soit « still considerable over-rejection for very small G ».
  - « The literature has gravitated to using the CR2VE adjustment ... This reduces but does not eliminate over-rejection ».
- Cameron & Miller, clusters déséquilibrés : à G = 10, avec moitié de clusters de taille 10 et moitié de taille 50, le taux de rejet est de .183 contre .126 et .115 en clusters équilibrés. Le nombre effectif de clusters baisse quand les tailles varient (Carter, Schnepel & Steigerwald ; Imbens & Kolesár). MacKinnon & Webb 2013 : « even with G = 50, tests based on the standard CRVE with T(G − 1) critical values can over-reject considerably if the clusters are unbalanced. By contrast, the two-point wild bootstrap with Rademacher weights is generally reliable. » — [Cameron & Miller PDF](http://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
- Cameron & Miller, bootstrap : « in Monte Carlos with few clusters the pairs cluster bootstrap did not eliminate test over-rejection ». Les auteurs ont donc proposé « the wild cluster bootstrap, that holds the regressors fixed ». Avec la pondération à six points de Webb, c'est « the preferred method to use if G < 10 ». Section « Bootstrap with Caution » : il faut « examine the distribution of bootstrapped values ». — [Cameron & Miller PDF](http://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
- Cameron & Miller, « Few Treated Groups » : « Problems arise if most of the variation in the regressor is concentrated in just a few clusters, even when G is sufficiently large. » — [Cameron & Miller PDF](http://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
- DELTA2, Table 1, essais en clusters : « Variability in cluster size should be considered and, if necessary, the coefficient of variation ». — [PMC6216070](https://pmc.ncbi.nlm.nih.gov/articles/PMC6216070/)
- FDA 2022, annexe 6, bootstrap et multiplicité : ces méthodes demandent de grands échantillons et « often require simulations to ensure ... adequate Type I error rate control ». — [FDA 2022](https://www.fda.gov/media/162416/download)

### Inferences
- **Dans un rejeu hors ligne, l'échantillon est fixé** (les runs enregistrés) : la logique de Hemming s'applique telle quelle. La préregistration honnête se fait en trois temps.
  1. Pour chaque environnement, calculer la différence minimale détectable au G disponible, pour l'économie et, si la sécurité est orientée NI, pour le taux d'erreur. Le calcul se fait à l'α et à la puissance visés, avec l'estimateur prévu et son comportement en petit échantillon.
  2. Fixer Δ ou ρ en croisant l'importance (DELTA2) et ce seuil détectable.
  3. Déclarer à l'avance quels environnements sont sous-puissants (par exemple G = 20) et les traiter comme des appuis plutôt que comme des preuves confirmatoires, ou les regrouper selon une règle préspécifiée.
- **G = 20 est « few », G = 276 ne l'est pas**, sauf fort déséquilibre de taille des clusters ou erreurs concentrées dans quelques clusters (seuils de Cameron & Miller). À G = 20, le quantile t(19) à 97,5 % vaut 2,09 au lieu de 1,96 : coût supplémentaire en puissance (mon calcul).
- **Erreurs rares = variation concentrée dans peu de clusters.** C'est l'analogue des « few treated groups ». Le nombre effectif de clusters pour estimer un taux d'erreur peut être très inférieur à G. Les intervalles bootstrap ou jackknife sur ces taux deviennent alors peu fiables, avec des distributions bootstrap dégénérées pleines de zéros. Il faut inspecter la distribution bootstrap (« Bootstrap with Caution »). En analyse de sensibilité, ajouter des bornes exactes ou par vraisemblance pour événements rares (déduction non sourcée).
- **Appariement.** Toutes les règles sont rejouées sur les mêmes runs, donc les comparaisons se font à l'intérieur de chaque cluster. Les différences par cluster retirent la variation entre clusters, dans l'esprit de Taljaard sur les designs à mesure préalable. La puissance pour comparer les économies devrait être nettement meilleure que celle d'un essai en clusters parallèle de même G (déduction).
- **Le bootstrap par tâche-cluster est probablement un « pairs cluster bootstrap ».** D'après Cameron, Gelbach et Miller, il n'élimine pas le sur-rejet à petit G. Le jackknife CR3 l'atténue, mais le taux reste à 7,0 % pour 5 % nominal à G = 20 dans leur simulation. Le protocole utilise les deux : il faut préregistrer lequel décide (par exemple le plus conservateur) et valider la taille réelle par simulation.
- **Le sens du sur-rejet compte.** En sécurité orientée NI, sur-rejeter revient à certifier la sécurité à tort. En supériorité sur l'économie, à certifier l'utilité à tort. Dans les deux cas, il faut une taille de test calibrée par simulation à G = 20.

**Synthèse par design (déduction)**

| Design | Multiplicité | Puissance | Avec peu de clusters (G ≈ 20, erreurs rares) |
|---|---|---|---|
| NI sécurité → supériorité efficacité | Aucune pour un seul critère testé NI puis supériorité. Dès deux critères : ordre ou partage d'α préspécifié | La conjonction donne à peu près le produit des puissances | La NI sur erreurs rares domine : borne supérieure large, sécurité difficile à établir |
| Séquence fixe, gatekeeping, graphe | FWER fort sans ajuster les tests individuels (séquence fixe). α partagé entre les branches | Les tests tardifs sont plafonnés par les précédents | L'ordre logique (sécurité d'abord) s'impose même si ce test est le moins puissant |
| Co-primaires contre composite | Co-primaires : aucune. Composite : un seul test | Co-primaires : environ 0,8 × 0,8 = 0,64. Le composite peut gagner | Sécurité et économie corrélées négativement : pire que le produit. Un composite pourrait masquer la nuisance |
| MCID / SESOI (test d'effet minimum) | Aucune en soi : s'ajoute à la conjonction | Il faut un vrai effet supérieur à Δ d'environ 2,8 erreurs types (unilatéral 2,5 %, 80 %) | Calculer la différence minimale détectable par environnement avant de fixer Δ |

### Gaps
- Non consulté : MacKinnon, Nielsen & Webb 2023 (*Cluster-robust inference: A guide to empirical practice*, J Econometrics), source la plus récente sur le jackknife CV3, le wild bootstrap et le nombre effectif de clusters (erreur de certificat TLS à la lecture).
- Aucune source trouvée sur la combinaison événements binaires rares + peu de clusters + bootstrap (par exemple GEE petits échantillons pour issues binaires).
- Aucun guide d'essais en clusters trouvé qui traite explicitement la préspécification d'un seuil d'importance (type MCID) sous nombre de clusters fixé. Hemming 2011 ne couvre que la logique de différence minimale détectable.
- Leyrat 2018 et Kahan 2016 portent sur des essais en clusters parallèles avec issue continue. Leur transposition à un rejeu apparié est une déduction.
