# Étiquettes préenregistrées : distinguer « preuve d'absence » et « absence de preuve »

Notes de recherche du 2026-11-06, pour le choix A/B sur « R4 · rien à déléguer ». Rappel de la commande : en simulation, R4 sort pour des agents fiables dans environ 20 % des cas quand leurs erreurs sont fortement groupées par tâche. Ce chiffre vient de la commande, pas d'une source externe. Convention : « extrait de recherche » = texte vu dans le résumé du moteur de recherche, page non ouverte ; « paraphrase de l'outil » = page ouverte, mais rendue reformulée par l'outil de lecture.

## 1. Essais cliniques : futilité ou « non concluant », cadres bayésiens go / no-go, ICH E9 et E9(R1)

### Takeaway
ICH E9 interdit de conclure à l'équivalence ou à la non-infériorité à partir d'un test non significatif. Il exige une marge fixée dans le protocole et un intervalle de confiance entièrement contenu dans cette marge. La futilité y est définie comme une prédiction sur l'essai (« la démonstration [...] est devenue improbable »), pas comme une preuve d'absence d'effet. Les cadres bayésiens de décision « quantitative » prévoient explicitement une zone intermédiaire (« Gray », « consider »). Dans l'un d'eux, le NoGo exige une probabilité a posteriori élevée que l'effet soit sous une valeur minimale : c'est une preuve d'insuffisance, pas un simple échec du Go. Un autre cadre définit au contraire le no-go comme un « échec à montrer » l'efficacité. Les deux conventions coexistent. E9(R1) ne dit rien sur les résultats non significatifs. Il ajoute l'exigence de documenter les hypothèses de l'estimateur, de préspécifier des analyses de sensibilité et de dire si chaque analyse a été préspécifiée, introduite à l'aveugle ou faite après coup.

### Cited Findings
**ICH E9 (Statistical Principles for Clinical Trials)**, texte extrait du PDF officiel :
- §3.3.2 : « Concluding equivalence or non-inferiority based on observing a non-significant test result of the null hypothesis that there is no difference between the investigational product and the active comparator is inappropriate. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- §3.3.2 : « An equivalence margin should be specified in the protocol; this margin is the largest difference that can be judged as being clinically acceptable » ; « Equivalence is inferred when the entire confidence interval falls within the equivalence margins. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- §3.3.2 : « It is vital that the protocol of a trial designed to demonstrate equivalence or non-inferiority contain a clear statement that this is its explicit intention. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- §3.3.2, sur le sens du biais : « The equivalence (or non-inferiority) trial is not conservative in nature, so that many flaws in the design or conduct of the trial will tend to bias the results towards a conclusion of equivalence. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- §4.5, sur la futilité : « The goal of such an interim analysis is to stop the trial early if the superiority of the treatment under study is clearly established, if the demonstration of a relevant treatment difference has become unlikely or if unacceptable adverse effects are apparent. » La futilité y est donc formulée comme l'improbabilité de *démontrer*. Le texte ne parle pas de preuve d'absence d'effet. — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- §4.5, seuils asymétriques selon l'enjeu : « Generally, boundaries for monitoring efficacy require more evidence to terminate a trial early (i.e. they are more conservative) than boundaries for monitoring safety. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- §4.5 : « The stopping guidelines and their properties should be clearly described in the protocol or amendments. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)

**ICH E9(R1)** (addendum sur les estimands, adopté le 20 novembre 2019) :
- Une recherche dans le texte intégral ne trouve aucune occurrence de « non-significant » ou de « not significant ». Je n'ai trouvé aucun passage sur l'interprétation d'un résultat non significatif. L'addendum renvoie à E9 §3.3.2 pour la non-infériorité et l'équivalence. — [ICH E9(R1)](https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf)
- A.5.2.1 : « Inferences based on a particular estimand should be robust to limitations in the data and deviations from the assumptions used in the statistical model for the main estimator. This robustness is evaluated through a sensitivity analysis. » — [ICH E9(R1)](https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf)
- A.5.2.1 : « The statistical assumptions that underpin the main estimator should be documented. One or more analyses, focused on the same estimand, should then be pre-specified to investigate these assumptions [...]. This might be characterised as the extent of departures from assumptions that change the interpretation of the results in terms of their statistical or clinical significance (e.g. tipping point analysis). » — [ICH E9(R1)](https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf)
- Fin de la section A.3, sur la non-infériorité et l'équivalence : « Responses in both treatment groups can appear more similar following discontinuation of randomised treatment or use of another medication for reasons that are unrelated to the similarity of the initially randomised treatments. » — [ICH E9(R1)](https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf)

**Cadres bayésiens go / no-go**
- BayesianQDM, paquet R sur le CRAN qui renvoie à Kang, Yamaguchi et Han (2026). Critère Go : Pr(θ > θ_TV | D) ≥ γ_go. Critère NoGo : Pr(θ ≤ θ_MAV | D) ≥ γ_nogo, avec θ_MAV (valeur minimale acceptable) < θ_TV (valeur cible). Texte : « The decision is Go if only the Go criterion is met, NoGo if only the NoGo criterion is met, and Gray if neither is met. » Si les deux critères sont remplis, « the decision is called Miss ». Le cas Miss n'est possible que si γ_go + γ_nogo ≤ 1. — [BayesianQDM, vignette](https://gosukehommaex.r-universe.dev/BayesianQDM/doc/overview.html)
- Même source : la calibration calcule γ_go et γ_nogo pour contrôler « the probabilities of a false Go and a false NoGo decision ». La fonction de caractéristiques opératoires rapporte « the probabilities of Go, NoGo, Gray and Miss decisions under scenarios for the true parameters ». — [BayesianQDM, vignette](https://gosukehommaex.r-universe.dev/BayesianQDM/doc/overview.html)
- BOP2-DC (Zhao, Li, Liu, Yuan, arXiv 2112.10880, 2021). Go si P(θ > θ_LRV | data) > λ_LRV **et** P(θ > θ_CMV | data) > λ_CMV. Définitions : « go decision means that the drug is effective both statistically and clinically » ; « consider decision means that the drug shows efficacy either statistically or clinically, but not both », et dans ce cas « the final decision whether the drug warrants further development should be made based on other considerations » ; « no-go decision means that the drug fails to show efficacy either statistically or clinically ». Ici, le no-go correspond à un **échec à montrer**, pas à une preuve d'inefficacité. Plages de recherche des seuils, selon la paraphrase de l'outil : λ_LRV dans environ [0,5 ; 0,99], λ_CMV dans environ [0,01 ; 0,5]. — [BOP2-DC (ar5iv)](https://ar5iv.labs.arxiv.org/html/2112.10880)
- Même article : « Sargent et al. (2001) introduced the additional uncertainty region in decision-making in phase II trials » (Sargent, Chan, Goldberg, *Controlled Clinical Trials* 22(2):117-125, « A three-outcome design for phase II clinical trials »). — [BOP2-DC (ar5iv)](https://ar5iv.labs.arxiv.org/html/2112.10880)
- Références citées par BOP2-DC, non lues directement :
  - Frewer et al., 2016, *Pharmaceutical Statistics* 15(3):255-63. BOP2-DC le décrit comme un cadre fréquentiste qui compare les bornes d'intervalle de confiance à un profil cible à deux niveaux.
  - Pulkstenis, Patra, Zhang, 2017, « A Bayesian paradigm for decision-making in proof-of-concept trials », *J Biopharm Stat*, doi 10.1080/10543406.2017.1289947.
  - Roychoudhury, Scheuer, Neuenschwander, 2018, « Beyond p-values: a phase II dual-criterion design with statistical significance and clinical relevance », *Clinical Trials* 15(5):452-461.
  - Lalonde et al., 2007, « Model-based drug development », *Clin Pharmacol Ther* 82(1):21-32.

  — [BOP2-DC, bibliographie](https://ar5iv.labs.arxiv.org/html/2112.10880)
- Source commerciale, faible poids, extrait de recherche : décision à trois issues GO / NO-GO / CONSIDER avec une « lower reference value » (LRV) et une valeur cible. — [MetricGate](https://metricgate.com/docs/clinical-go-no-go-bayesian-decision/)

### Inferences
- Deux conventions existent pour l'issue négative :
  - (i) « No-Go = échec à démontrer » (BOP2-DC). Elle se défend quand l'étiquette est une **décision** (investir ou non) et pas un constat sur le produit.
  - (ii) « NoGo = preuve d'insuffisance », avec une zone grise à part (BayesianQDM, Sargent).

  L'intention de l'auteur pour R4 (« clairement non fiable ») est un **constat**, donc de type (ii). Sous la règle actuelle, R4 se comporte en pratique comme (i). C'est exactement l'écart entre A et B.
- Le taux de 20 % où R4 sort pour un agent fiable aux erreurs groupées est, dans le vocabulaire de BayesianQDM, une probabilité de « faux NoGo » sous un scénario donné. Ce cadre calibre le seuil γ_nogo pour borner cette probabilité, et rapporte les caractéristiques opératoires scénario par scénario. Transposé : le jeu de scénarios devrait contenir explicitement le cas « fiable, erreurs groupées ».
- E9 §4.5 : lire « rien à déléguer » comme « démontrer la fiabilité est devenu improbable avec ce protocole » rapproche R4 de la **futilité**, pas d'une preuve de non-fiabilité.
- E9(R1) A.5.2.1 : l'indépendance des erreurs entre essais d'une même tâche est une hypothèse de l'estimateur. Elle devrait être documentée et accompagnée d'une analyse de sensibilité préspécifiée, du type « point de bascule » : à partir de quel degré de regroupement l'étiquette change-t-elle ? Cela vaut pour A comme pour B.
- E9 §3.3.2 et E9(R1) A.3 mettent en garde contre des défauts qui poussent le résultat vers une conclusion donnée pour des raisons étrangères à la question. Ici, le regroupement pousse vers l'étiquette négative. Le sens du biais d'une règle est donc à documenter.
- E9 §4.5 admet des seuils asymétriques selon l'enjeu, plus exigeants pour arrêter sur l'efficacité que sur la sécurité. On peut agir prudemment, en ne déléguant pas, sur moins de preuves qu'il n'en faut pour affirmer « non fiable ». Ce sont deux seuils distincts.

### Gaps
- Frewer 2016, Pulkstenis 2017, Roychoudhury 2018, Lalonde 2007 et Sargent 2001 n'ont pas été lus directement : seulement via la bibliographie et l'introduction de BOP2-DC. Les seuils exacts de Pulkstenis (go / no-go / zone intermédiaire) ne sont pas vérifiés. L'attribution du couple « target value / lower reference value » à Lalonde n'est pas vérifiée : BOP2-DC ne la fait pas.
- Kang, Yamaguchi, Han (2026), référence méthodologique de BayesianQDM, n'a pas été lu.
- Je n'ai trouvé aucune source qui dise explicitement, au-delà de la formulation d'E9, qu'un arrêt pour futilité ne prouve pas l'absence d'effet. La littérature des comités de surveillance n'a pas été consultée.
- La doctrine FDA sur les méthodes bayésiennes ou adaptatives n'a pas été consultée.

## 2. « L'absence de preuve n'est pas la preuve de l'absence » et le cadrage par équivalence ou non-infériorité

### Takeaway
Altman et Bland (BMJ, 1995) : un essai non significatif est à tort appelé « négatif ». En général, il n'a montré qu'une « absence of evidence of a difference ». Le mot « négatif » ne devrait pas être employé dans ce cas. Il faut rapporter une estimation chiffrée avec son intervalle de confiance. Pour affirmer une absence, il faut un dispositif fait pour : marge fixée à l'avance et intervalle entièrement dans la marge (E9 §3.3.2), facteur de Bayes sous 1/3 (Dienes), ou formulation graduée par niveau de certitude (Cochrane). Chacun de ces cadres distingue trois états : preuve de l'effet, preuve de l'absence, données insuffisantes.

### Cited Findings
- Référence : Altman DG, Bland JM. « Absence of evidence is not evidence of absence ». *BMJ* 1995;311(7003):485, 19 août 1995, doi 10.1136/bmj.311.7003.485. — [PMC2550545](https://pmc.ncbi.nlm.nih.gov/articles/PMC2550545/)
- Extrait de recherche de la page BMJ (la page renvoie une erreur 403 à l'outil) : les essais sans différence significative « are often called "negative." » Ce terme « implies that the study has shown that there is no difference, whereas usually all that has been shown is an absence of evidence of a difference. These are quite different statements. » Et : « The term "negative" should not be used in this context. » — [BMJ 1995;311:485](https://www.bmj.com/content/311/7003/485)
- Copie du texte sur une page de cours universitaire (paraphrase de l'outil) :
  - Freiman et al. : seuls 30 % d'un échantillon de 71 essais avec P > 0,1 étaient assez grands pour détecter de façon fiable même une différence de 50 %.
  - Essai octréotide contre sclérothérapie : 100 patients, alors qu'un calcul en demandait environ 1 800 ; environ 5 % de chances de détecter une différence cliniquement utile. Les auteurs ont conclu à une efficacité égale, alors que l'IC à 95 % allait jusqu'à 20 points de pourcentage.
  - Fibrinolytiques : une méta-analyse montre une réduction de mortalité de 22 %, très significative, alors que seuls 5 essais sur 24 étaient significatifs.

  — [Copie, université de Buffalo](https://www.acsu.buffalo.edu/~wdmccall/os512d/EvidAbs.html)
- Même copie (paraphrase de l'outil), recommandations : devant « no evidence that A causes B », se demander d'abord s'il existe des données. Chercher une estimation chiffrée avec son intervalle, pas seulement une valeur de P. Ne jamais tenir l'absence de relation pour prouvée. — [Copie, université de Buffalo](https://www.acsu.buffalo.edu/~wdmccall/os512d/EvidAbs.html)
- Extrait de recherche, à confirmer : un éditorial du BMJ d'Alderson (2004) revient sur la note et rappelle que la vérité de ces situations ne s'établit qu'en recueillant davantage de preuves. L'identité de la page n'a pas été vérifiée. — [PMC351831 (supposé Alderson 2004)](https://pmc.ncbi.nlm.nih.gov/articles/PMC351831)
- E9 §3.3.2 : un essai d'équivalence exige une marge préspécifiée et un intervalle entièrement contenu dans la marge. Conclure à l'équivalence sur un test non significatif est « inappropriate ». — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- Dienes (2014), *Frontiers in Psychology* 5:781 :
  - « A non-significant p-value does not distinguish evidence for the null from no evidence at all. »
  - « A high p-value may simply reflect data insensitivity. »
  - Les facteurs de Bayes « allow three different types of conclusions » : preuve pour H1, preuve pour H0, « the evidence is insensitive ». Seuil : « A Bayes factor greater than 3 or else less than 1/3 represents substantial evidence ».

  — [Dienes 2014](https://www.frontiersin.org/articles/10.3389/fpsyg.2014.00781/full)
- Cochrane Handbook, chapitre 15 : « A common mistake is to confuse 'no evidence of an effect' with 'evidence of no effect'. » (§15.6.4). Encadré MECIR 15.3.a : « Authors commonly mistake a lack of evidence of effect as evidence of a lack of effect. » — [Cochrane Handbook, ch. 15](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-15)

### Inferences
- Pour que R4 veuille dire « clairement non fiable », il lui faut l'équivalent d'une marge : un seuil minimal de fiabilité fixé à l'avance, et une règle qui exige que l'incertitude se situe entièrement sous ce seuil. Au sens d'E9, c'est un test d'infériorité démontrée face au minimum acceptable. C'est aussi la forme du NoGo de BayesianQDM : Pr(fiabilité ≤ minimum) ≥ γ.
- Raisonnement statistique général, non sourcé dans ces notes : des erreurs groupées par tâche réduisent l'information indépendante. La taille d'échantillon effective se rapproche du nombre de tâches plutôt que du nombre d'essais. Avec une règle qui tient compte de ce regroupement, ces cas tombent mécaniquement dans « données insuffisantes ».
- La simulation décrite place R4 dans la situation de l'essai octréotide cité par Altman et Bland : un verdict négatif tiré d'un dispositif trop peu sensible pour le cas considéré.

### Gaps
- Le texte intégral du BMJ n'a pas pu être lu à la source (erreur 403 sur bmj.com, page PDF de PMC et de Europe PMC inaccessibles). Le contenu vient d'un extrait de recherche de la page BMJ et d'une copie sur une page de cours, rendue en paraphrase. Les chiffres de Freiman sont à revérifier sur l'original avant toute citation publique.
- Les tutoriels de Lakens sur les tests d'équivalence (TOST, plus petit effet d'intérêt) n'ont pas été consultés.

## 3. Registered reports et préenregistrement : catégories d'issues, modification avant le gel, documentation

### Takeaway
La pratique des registered reports demande de préenregistrer, pour chaque hypothèse, toutes les issues possibles et leur interprétation. Chez PCI RR, c'est une ligne par issue dans la table de conception. Changer le plan avant l'analyse est admis. Le Center for Open Science (COS) le dit en toutes lettres : si la collecte n'a pas commencé, on crée un nouveau préenregistrement et on retire l'ancien, et le retrait reste public. ICH E9 admet la mise à jour du plan d'analyse jusqu'à la levée de l'aveugle, à condition de tracer formellement les dates et de passer par un amendement pour tout changement principal. E9(R1) demande d'étiqueter chaque analyse : préspécifiée, introduite à l'aveugle, ou après coup.

### Cited Findings
- COS : « Updates or amendments to a preregistration are permissible (in most cases) prior to analyzing the data ». À l'inverse, le COS juge problématique « updating the registration after results of the initial analyses are known ». — [COS, Preregistration](https://www.cos.io/initiatives/prereg)
- COS : une fois le préenregistrement finalisé, deux voies. Option 1 : créer un nouveau préenregistrement et retirer l'original, « if you have not yet started data collection ». Option 2 : un document de « Transparent Changes », « if you have already begun the study ». Le retrait laisse une trace : « a notification of the withdrawal will be public. » — [COS, Preregistration](https://www.cos.io/initiatives/prereg)
- COS : « it is important to transparently disclose any changes from the proposed plan ». Le document de changements est déposé dans le projet OSF et cité lors du compte rendu des résultats. — [COS, Preregistration](https://www.cos.io/initiatives/prereg)
- COS : « The central aims of preregistration are to distinguish confirmatory and exploratory analyses ». Et : « Once a researcher begins to slightly change the way to test the hypothesis, the work should be considered exploratory. » Le contexte de cette phrase n'a pas été relu : elle vise vraisemblablement les changements après la collecte. — [COS, Preregistration](https://www.cos.io/initiatives/prereg)
- Extrait de recherche, correspondance de relecture d'un registered report chez PCI RR. La table de conception contient les colonnes « Interpretation given different outcomes » et « Theory that could be shown wrong by the outcomes ». Le relecteur demande : « The first column should list all different outcomes and interpretations ». Les auteurs répondent avoir ajouté une ligne par issue. — [PCI RR, réponse aux relecteurs](https://rr.peercommunityin.org/download/t_recommendations.reply_pdf.8ca8c368f0dc5b3c.506572736f6e616c6974792c207269736b20616e6420636f6d706c69616e6365202d20526573706f6e736520746f20326e6420504349205252207265766965772e706466.pdf)
- Extrait de recherche, autre dossier PCI RR : un éditeur demande une ligne par hypothèse, « so it is clear exactly which test addresses which hypothesis and what follows from possible outcomes in each case ». — [PCI RR, réponse aux relecteurs](https://rr.peercommunityin.org/PCIRegisteredReports/download/t_recommendations.reply_pdf.9b5528bbb1f10711.5265766973696f6e2031205043495f526573706f6e736520746f207265766965776572732e706466.pdf)
- Extrait de recherche, consignes de registered report d'une revue de Cambridge : demander « description and interpretation of potential outcomes (to author's best ability), specifying the theoretical implications of the different outcomes ». — [Cambridge, consignes RR](https://www.cambridge.org/core/services/aop-file-manager/file/5c5c5b034060634b0e30ee1a/BIL-rra.pdf)
- ICH E9 §5.1 : « The plan should be reviewed and possibly updated as a result of the blind review of the data [...] and should be finalised before breaking the blind. Formal records should be kept of when the statistical analysis plan was finalised as well as when the blind was subsequently broken. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- ICH E9 §5.1 : « If the blind review suggests changes to the principal features stated in the protocol, these should be documented in a protocol amendment. [...] Only results from analyses envisaged in the protocol (including amendments) can be regarded as confirmatory. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- ICH E9, glossaire, « Blind Review » : « The checking and assessment of data during the period of time between trial completion [...] and the breaking of the blind, for the purpose of finalising the planned analysis. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- ICH E9 §4.2 : les changements « should be made without breaking the blind and should always be described by a protocol amendment which should cover any statistical consequences ». §4.4 : une taille d'échantillon révisée « should be justified and documented in a protocol amendment and in the clinical study report ». — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- ICH E9 §4.5 : « Deviations from the planned procedure always bear the potential of invalidating the trial results. If it becomes necessary to make changes to the trial, any consequent changes to the statistical procedures should be specified in an amendment to the protocol at the earliest opportunity, especially discussing the impact on any analysis and inferences that such changes may cause. » — [ICH E9](https://database.ich.org/sites/default/files/E9_Guideline.pdf)
- ICH E9(R1) A.6 : « Results from the main, sensitivity and supplementary analyses should be reported systematically in the clinical trial report, specifying whether each analysis was pre-specified, introduced while the trial was still blinded, or performed post hoc. » Et : « Changes to the estimand during the trial can be problematic and can reduce the credibility of the trial. » — [ICH E9(R1)](https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf)

### Inferences
- Une modification avant le gel, déclenchée par une simulation et non par des données réelles, est le cas le plus défendable dans tous les cadres consultés. C'est « prior to analyzing the data » pour le COS. Pour E9, l'équivalent est un changement fait sans lever l'aveugle, ou issu de la revue à l'aveugle. Rien ne suggère qu'elle soit inacceptable. Ce que les sources exigent, c'est la trace.
- Forme de documentation compatible avec les trois sources :
  - un amendement versionné et daté ;
  - l'ancienne et la nouvelle définition, côte à côte ;
  - le motif, c'est-à-dire la simulation, rendue reproductible ;
  - la déclaration qu'aucune donnée d'évaluation réelle n'a été vue ;
  - l'ancienne version laissée visible (le retrait public du COS) ;
  - l'étiquetage de la nouvelle règle comme « introduite avant les données », selon la trichotomie d'E9(R1).
- Avec l'option A, l'issue R4 porterait deux interprétations dans la même ligne : non-fiabilité établie, ou données insuffisantes sous erreurs groupées. La pratique PCI RR relevée, une ligne par issue et par interprétation, va dans le sens d'une séparation. Avec l'option B, la table de conception gagne une ligne : « preuves insuffisantes ».
- L'option A ne dispense pas de documentation. La limite déclarée devrait figurer dans la colonne « interprétation selon l'issue », chiffrée, au moins avec le taux de 20 % de la simulation et le scénario qui le produit.

### Gaps
- Le guide des auteurs de PCI RR (`rr.peercommunityin.org/help/guide_for_authors`) a renvoyé une erreur HTTP 444. Les consignes de registered reports de *Nature Human Behaviour* demandent une authentification. Les règles précises sur les changements après acceptation de principe, et qui les approuve (recommandeur ou éditeur), ne sont donc pas vérifiées. Les colonnes de la table de conception ne sont connues que par des extraits de correspondance.
- Je n'ai trouvé aucune source qui traite précisément du changement de **définition d'une étiquette d'issue**. Les conclusions ci-dessus transposent les règles générales d'amendement.
- SPIRIT et CONSORT, sur les amendements de protocole, n'ont pas été consultés.

## 4. Évaluation IA / ML : NSF seldonien, repli sur la politique de référence, abstention conforme, METR, UK AISI, Anthropic

### Takeaway
Les méthodes d'apprentissage à garanties traitent la confiance insuffisante comme une issue à part, au nom neutre, avec une action par défaut prudente. Un algorithme seldonien rend « No Solution Found » quand la borne supérieure à 1−δ ne passe pas : cela veut dire « impossible de certifier », pas « dangereux ». SPIBB se replie sur la politique de référence là où l'incertitude est forte. L'abstention conforme fait répondre « je ne sais pas » avec un taux d'erreur borné. Côté évaluateurs de modèles frontière :
- METR gradue ses conclusions négatives (« unlikely »), s'appuie sur le haut de l'intervalle de confiance et liste ce qui changerait sa conclusion. Ses lignes directrices disent qu'un échec peut être un artefact, à corriger avant d'en tirer quoi que ce soit.
- UK AISI présente ses résultats comme « preliminary ».
- Anthropic a séparé « pas encore déterminé » de « seuil franchi », et a agi par précaution.

Aucun texte de METR ou de l'AISI trouvé n'emploie le mot « inconclusive ».

### Cited Findings
**Algorithmes seldoniens**
- Tutoriel de l'université du Massachusetts (UMass) : sortie de l'algorithme, « Either a solution in Θ or No Solution Found (NSF) ». Le test de sécurité calcule « a high-confidence upper bound » sur chaque contrainte g_i(θ), par un intervalle de Student, qui tient avec une probabilité d'au moins 1 − δ_i. Le candidat n'est rendu que si la borne est ≤ 0 pour toutes les contraintes ; « otherwise, the algorithm returns NSF. » — [UMass, A Simple Seldonian Algorithm](https://aisafety.cs.umass.edu/seldonian/tutorial3.html)
- Extrait de recherche, tutoriel UMass sur le test de sécurité : « If the 1-δ confidence upper bound is greater than zero, the algorithm cannot conclude with sufficient confidence that θc is safe, and so it returns No Solution Found (NSF) instead. » — [UMass, Safety Test](https://aisafety.cs.umass.edu/seldonian/tutorial5py.html)
- Extrait de recherche, article de 2025 sur le RLHF sous contraintes de sécurité à haute confiance : « Seldonian algorithms can return 'No Solution Found' (NSF) when they cannot confidently satisfy the safety constraint g (e.g., when there is not sufficient data to confidently estimate g). This outcome is assumed to be safe, i.e., g(NSF) = 0. » — [arXiv 2506.08266](https://arxiv.org/pdf/2506.08266)

**Amélioration sûre de politique et abstention**
- SPIBB (Laroche, Trichelair, Tachet des Combes, ICML 2019) : la méthode « bootstraps the trained policy with the baseline when the uncertainty is high », dans l'esprit « knows-what-it-knows ». Objectif : une politique « guaranteed to perform at least as well as the baseline policy used to collect the data ». — [arXiv 1712.06924](https://arxiv.org/abs/1712.06924)
- Abstention conforme (Yadkori et al., 2024) : « a principled procedure for determining when a large language model (LLM) should abstain from responding », avec « rigorous theoretical guarantees on the hallucination rate (error rate) ». Le modèle répond « je ne sais pas » au lieu de risquer une réponse fausse. — [arXiv 2405.01563](https://arxiv.org/abs/2405.01563)

**METR**
- Rapport GPT-5 (7 août 2025) : « we conclude that GPT-5 (and incremental development beyond GPT-5) is unlikely to pose a catastrophic risk ». La conclusion négative repose sur la borne haute : « Even assuming that the true time horizon is at the upper end of our confidence intervals (4.5 hours) ». — [METR, rapport GPT-5](https://metr.org/evaluations/gpt-5-report/)
- Même rapport, ce qui changerait la conclusion : « An 80% time horizon for high-context SWE tasks greater than 8 hours » ; « A 50% time horizon on SWE and ML tasks greater than 40 hours. » ; « Evidence that time horizon is no longer a predictive metric of autonomous capability. » — [METR, rapport GPT-5](https://metr.org/evaluations/gpt-5-report/)
- Même rapport, réserves explicites :
  - « Our monitors for reward hacking and sandbagging miss many examples of misbehavior ».
  - « we could not establish confidence in them during our evaluation » (pour certaines tâches).
  - « this evaluation shouldn't be interpreted as robust formal oversight or accountability ».
  - Une phrase au conditionnel : « we think these limitations would have prevented us from making a confident risk assessment ». Le contexte exact de ce conditionnel n'a pas été relu.
  - Selon l'outil, le rapport n'emploie ni « inconclusive », ni « cannot rule out », ni « insufficient ».

  — [METR, rapport GPT-5](https://metr.org/evaluations/gpt-5-report/)
- Lignes directrices de METR sur l'élicitation des capacités (15 mars 2024) :
  - « it is hard to upper-bound what might be possible with clever prompting and tooling ».
  - Les échecs « spurious » « can create very large differences in eval performance » mais « are not related to underlying capability levels ».
  - Exigences : « Identify all test set failures », puis « Fix the failure and rerun the task » ; « Bugs are always spurious failures ».
  - Attestations demandées aux évaluateurs : « They do not know of any easy ways the model performance could be dramatically improved » ; « They believe that any calculated safety margin used is sufficient ».

  — [METR, Guidelines for capability elicitation](https://metr.org/blog/2024-03-15-guidelines-for-capability-elicitation/)
- Extrait de recherche, à confirmer : l'article de METR sur les tâches longues dit que ses résultats « do not rule out the possibility that trends are meaningfully slower on the distribution of tasks required to automate software engineer jobs ». — [arXiv 2503.14499](https://arxiv.org/pdf/2503.14499v1)

**UK AISI**
- Évaluation de pré-déploiement d'o1 (18 décembre 2024) :
  - « the findings should be considered preliminary ».
  - « These tests were conducted in a limited time period with finite resources ».
  - « This report makes no claims about the performance of other versions of o1. »
  - « smaller differences in model performance presented below may fall within the margins of error for these tests. »
  - Selon l'outil, la page n'emploie ni « lower bound », ni « not conclusive », ni « cannot rule out ».

  — [UK AISI, évaluation d'o1](https://aisi.gov.uk/work/pre-deployment-evaluation-of-openais-o1-model)

**Anthropic**
- Activation des protections ASL-3 pour Claude Opus 4 (22 mai 2025) :
  - « we have not yet determined whether Claude Opus 4 has definitively passed the Capabilities Threshold ».
  - « clearly ruling out ASL-3 risks is not possible for Claude Opus 4 in the way it was for every previous model ».
  - « more detailed study is required to conclusively assess the model's level of risk ».
  - La mesure est décrite comme « a precautionary and provisional action ». La politique (RSP) « allows us to err on the side of caution and deploy a model under a higher standard than we are sure is needed ».

  — [Anthropic, Activating ASL-3 protections](https://www.anthropic.com/news/activating-asl3-protections)

**Statistique des évaluations**
- Miller (2024), résumé seulement : « Fundamentally, evaluations are experiments; but the literature on evaluations has largely ignored [...] ». L'article propose de concevoir les questions d'évaluation « as having been drawn from an unseen super-population ». — [arXiv 2411.00640](https://arxiv.org/abs/2411.00640)

### Inferences
- Motif commun aux méthodes à garanties (Seldonian, SPIBB, abstention) et à la décision d'Anthropic : on sépare l'**issue épistémique** (certifiable ou non) de l'**action** (défaut prudent). L'option B n'oblige donc pas à changer la conséquence pratique, ne pas déléguer. Elle change la raison affichée : « non établie » au lieu de « non fiable ».
- Le Seldonian ne distingue pas « prouvé dangereux » et « données insuffisantes » : les deux donnent NSF. Mais l'issue fusionnée porte le nom de l'affirmation la plus faible (« aucune solution trouvée »), jamais celui de la plus forte. Leçon pour A : si l'on garde la fusion, il faut nommer et définir R4 par l'affirmation faible, du type « délégation non établie ». R4 perd alors le sens « clairement non fiable » que l'auteur voulait lui donner.
- METR fonde sa conclusion négative sur la borne haute de l'intervalle. C'est une preuve d'absence établie par une borne, la logique de B. Sa liste « ce qui changerait la conclusion » est un modèle réutilisable dans la définition de chaque étiquette.
- Lignes directrices de METR transposées aux agents, à titre d'hypothèse : des erreurs concentrées sur quelques tâches peuvent signaler des défauts propres à ces tâches (énoncé ambigu, environnement cassé). METR les traite comme des échecs « spurious » à corriger avant toute inférence. C'est une raison de plus de ne pas lire ce motif comme une non-fiabilité établie.
- Le cas Anthropic est le précédent le plus proche de la situation : l'impossibilité d'écarter un risque est dite comme telle (« not yet determined », « ruling out [...] is not possible »). Elle déclenche une action prudente, sans être présentée comme un constat positif.

### Gaps
- L'article de Thomas et al. (2019, *Science*) n'a pas été lu : derrière un paywall, et le PDF récupéré sur le site de l'UMass était un autre article (inégalités de concentration pour la CVaR). La sémantique de NSF dans l'article lui-même, et l'évolution de la fréquence de NSF avec la quantité de données, ne sont pas vérifiées. La sémantique décrite ici vient des tutoriels UMass et d'un article de 2025, vus en partie par extraits de recherche.
- SPIBB : seul le résumé a été lu. Le mécanisme exact de repli (seuil de comptage par paire état-action) n'est pas vérifié.
- Abstention conforme : la façon dont les abstentions sont comptées à part des erreurs n'est pas vérifiée (résumé seulement). Learn-then-Test, où un ensemble vide de paramètres valides mène à ne pas déployer, n'a pas été consulté.
- Je n'ai trouvé aucun texte de METR ou de l'UK AISI qui emploie « inconclusive » ou « cannot rule out ». Une critique publiée sur GreaterWrong, « AI companies' eval reports mostly don't support their claims », est apparue dans les résultats mais n'a pas été lue : [lien](https://www.greaterwrong.com/posts/AK6AihHGjirdoiJg6/ai-companies-eval-reports-mostly-don-t-support-their-claims/comment/mAcm2tdfRLRcHhnJ7).
- Miller (2024) : le détail sur les erreurs types groupées (« clustered standard errors ») quand les questions sont regroupées n'est pas vérifié, faute d'avoir lu le texte intégral. C'est pourtant la référence la plus directe pour le mécanisme du regroupement.
- Des articles de presse sur la mesure de « Claude Mythos » par METR (IC à 95 % de 8,5 h à 55 h, seulement 5 tâches de 16 h ou plus sur 228) n'ont pas été vérifiés à la source primaire. À ne pas citer en l'état.

## 5. Formulations recommandées pour les étiquettes et les résumés

### Takeaway
Les conventions trouvées convergent sur six règles :
- ne jamais appeler « négatif » un résultat non significatif (Altman et Bland) ;
- distinguer « pas de preuve d'effet » et « preuve d'absence d'effet » (Cochrane) ;
- graduer la formulation selon le niveau de certitude (Cochrane, tableau 15.6.b) ;
- dire que des données insensibles « ne comptent pas contre » l'hypothèse (Dienes) ;
- donner un nom neutre à l'issue non certifiée (« No Solution Found », « Gray », « consider ») ;
- énoncer ce qui changerait la conclusion (METR), ou « pas encore déterminé, impossible d'écarter, mesure provisoire » (Anthropic).

### Cited Findings
- Cochrane, tableau 15.6.b, formulations par niveau de certitude :
  - certitude élevée : « X results in little to no difference in outcome » ;
  - modérée : « X probably results in little to no difference in outcome » ;
  - faible : « X may result in little to no difference in outcome » ou « The evidence suggests that X results in little to no difference in outcome » ;
  - très faible : « The evidence is very uncertain about the effect of X on outcome ».

  Selon l'outil, la formule « may make little or no difference » n'apparaît pas telle quelle. — [Cochrane Handbook, ch. 15](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-15)
- Cochrane §15.6.4 : un intervalle large est « compatible with both a true beneficial effect and a true harmful effect ». Si l'une des deux possibilités figure dans la conclusion, l'autre doit y figurer aussi. — [Cochrane Handbook, ch. 15](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-15)
- Cochrane §15.3.1 : « Intervals that are very wide (e.g. 0.50 to 1.10) indicate that we have little knowledge about the effect », et « further information would be needed before we could draw a more certain conclusion ». — [Cochrane Handbook, ch. 15](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-15)
- Cochrane §15.6.4, test du renversement : se demander « how the results would be presented and framed in the conclusions if the direction of the results was reversed ». — [Cochrane Handbook, ch. 15](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-15)
- Altman et Bland, extrait de recherche de la page BMJ : « The term "negative" should not be used in this context » ; dire ce qui a été montré, « an absence of evidence of a difference ». — [BMJ 1995;311:485](https://www.bmj.com/content/311/7003/485)
- Dienes : « the data are insensitive and do not count against the theory ». Et, après une analyse bayésienne, « conclude that the data were simply insensitive and more participants should be run ». — [Dienes 2014](https://www.frontiersin.org/articles/10.3389/fpsyg.2014.00781/full)
- Noms d'issue neutres :
  - « No Solution Found » — [UMass](https://aisafety.cs.umass.edu/seldonian/tutorial3.html) ;
  - « Gray », quand ni Go ni NoGo n'est atteint — [BayesianQDM](https://gosukehommaex.r-universe.dev/BayesianQDM/doc/overview.html) ;
  - « consider », avec renvoi à d'autres éléments — [BOP2-DC](https://ar5iv.labs.arxiv.org/html/2112.10880).
- Formules d'incertitude chez les évaluateurs :
  - « not yet determined », « clearly ruling out [...] is not possible », « precautionary and provisional » — [Anthropic](https://www.anthropic.com/news/activating-asl3-protections) ;
  - « preliminary », « makes no claims about the performance of other versions », « may fall within the margins of error » — [UK AISI](https://aisi.gov.uk/work/pre-deployment-evaluation-of-openais-o1-model) ;
  - « unlikely », adossé à la borne haute de l'intervalle, plus la liste de ce qui changerait la conclusion — [METR](https://metr.org/evaluations/gpt-5-report/).

### Inferences
Formulations dérivées des sources ci-dessus, non sourcées en tant que telles. Ce sont des gabarits, pas un avis sur A ou B.
- **Règle de nommage.** Une étiquette ne porte que l'affirmation que sa règle établit. Si la règle peut sortir faute de données, son nom et sa définition doivent dire « non établi » (modèle NSF), pas « non fiable ».
- **Gabarit B, deux étiquettes séparées :**
  - R4, constat négatif : « R4 · rien à déléguer — non-fiabilité établie ». Définition : la fiabilité est sous le minimum fixé avec une confiance ≥ γ (préspécifié), intervalle calculé en tenant compte du regroupement par tâche. Calqué sur le NoGo de BayesianQDM et la marge d'E9.
  - Nouvelle étiquette : « preuves insuffisantes » ou « non concluant ». Phrase de résumé sur le modèle Cochrane et Dienes : « Les données ne permettent pas de conclure. Elles sont compatibles avec un agent fiable comme avec un agent non fiable, et ne comptent pas contre lui. »
  - Pour chacune : l'action par défaut (« ne pas déléguer pour l'instant », comme NSF, le repli de SPIBB ou la précaution d'Anthropic) et ce qui manque (« davantage de tâches distinctes », comme chez Dienes).
- **Gabarit A, une étiquette avec limite déclarée.** Pour respecter la règle Cochrane (« mentionner l'autre possibilité »), chaque occurrence de R4, y compris dans les résumés, devrait porter les deux lectures, par exemple : « R4 peut aussi sortir pour un agent fiable dont les erreurs sont concentrées sur quelques tâches (environ 20 % des cas simulés) ; R4 seul ne prouve pas la non-fiabilité. » Un lecteur qui ne voit que le nom de l'étiquette n'a pas accès à cette réserve. C'est le mécanisme qu'Altman et Bland reprochent au mot « négatif ».
- **Test du renversement appliqué aux étiquettes (Cochrane §15.6.4).** Accepterait-on qu'une étiquette positive (« délégable ») sorte dans 20 % des cas pour un agent non fiable, avec une simple note dans la définition ? La réponse donne la symétrie attendue entre les deux sens.
- **Liste de contrôle pour chaque étiquette :**
  - l'affirmation établie ;
  - la règle et son seuil, préspécifiés ;
  - les caractéristiques opératoires simulées par scénario, dont « fiable, erreurs groupées » ;
  - l'action par défaut ;
  - ce qui changerait la conclusion (modèle METR) ;
  - le statut de la règle (préspécifiée, ou introduite avant les données selon E9(R1)).

### Gaps
- Je n'ai trouvé aucune source sur le nommage d'étiquettes dans un protocole d'évaluation d'agents IA. Les gabarits ci-dessus sont transposés de la clinique, de la psychologie et de l'apprentissage à garanties.
- L'article GRADE sur les « informative statements » (Santesso et al., 2020) n'a pas été consulté directement. Les formulations viennent du tableau 15.6.b de Cochrane, qui s'appuie sur GRADE.
- La littérature sur le « spin » dans les essais non significatifs (par exemple Boutron et al., 2010) n'a pas été consultée. Elle documenterait empiriquement la sur-interprétation des résultats non concluants.
