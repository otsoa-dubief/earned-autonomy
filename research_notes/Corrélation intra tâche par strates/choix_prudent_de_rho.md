# Choix prudent et pré-enregistrable de ρ pour n_eff — erreurs rares groupées par tâche

Cadre. Règle étudiée : certifier « taux d'erreur < seuil θ » par une borne Clopper–Pearson (CP) unilatérale sur n_eff = n / (1 + (m̄ − 1) ρ), erreurs groupées par tâche. Règle actuelle : ANOVA par environnement, plancher 0,3 ; environnement sans erreur → estimation poolée de tous les environnements ; configuration avec ≥ 10 erreurs dans ≥ 5 tâches → max(propre, base). Mesuré par l'équipe : le plancher couvre ρ = 0,3 mais pas 0,7 (≈ 4 % de fausses certifications pour 5 % nominal, IC Monte-Carlo jusqu'à 6,9 %) ; l'estimation empruntée peut être gonflée (0,43 pour 0 vrai) quand une configuration erre beaucoup.

Fiabilité des sources : **[lu]** texte ouvert dans cette session ; **[abstract]** résumé officiel lu via Europe PMC (paraphrasé) ; **[résumé]** vu seulement via un résumé de moteur de recherche ou une notice ; **[mémoire]** référence complète donnée de mémoire, non rouverte ici ; **[calcul]** calcul exact fait ici (formule et code en section 3).

## 1. Pratique des essais en grappes face à un ICC incertain ; cas des événements rares

### Takeaway
En essai randomisé en grappes (ERG), l'incertitude sur l'ICC est traitée **au dimensionnement** (puissance), par trois voies : borne haute d'IC (courante, jugée inefficace), moyenne sur une plage plausible ou un a priori (Turner 2004 ; Lewis & Julious 2021), a priori bâti sur plusieurs ICC publiés pondérés par pertinence (Turner, Thompson & Spiegelhalter 2005). Ces méthodes visent une puissance *moyenne*, pas une garantie au pire cas. Aucune recommandation « événements rares » pour choisir ρ n'a été trouvée ; le fait robuste est que l'ICC sur l'échelle des proportions baisse avec la prévalence (Gulliford 2005).

### Cited Findings
- Turner, Prevost & Thompson (2004) : simulation bayésienne ; l'imprécision d'un ICC estimé antérieurement peut réduire la puissance attendue, d'où des effectifs plus grands pour s'en prémunir. Stat Med 23(8):1195–1214 [abstract] — [PubMed 15083478](https://pubmed.ncbi.nlm.nih.gov/15083478/)
- Turner, Thompson & Spiegelhalter (2005) : a priori informatifs sur l'ICC construits à partir de multiples estimations antérieures, en sous-pondérant les moins pertinentes ou moins précises ; la sous-pondération peut augmenter la précision de l'ICC anticipé ; l'a priori sert à choisir un design de puissance adéquate « across the range of likely ICC values » et peut entrer dans l'analyse bayésienne. Clin Trials 2(2):108–118 [abstract/résumé] — [PubMed 16279132](https://pubmed.ncbi.nlm.nih.gov/16279132/) ; [notice QxMD](https://read.qxmd.com/read/16279132/prior-distributions-for-the-intracluster-correlation-coefficient-based-on-multiple-previous-estimates-and-their-application-in-cluster-randomized-trials)
- Turner, Omar & Thompson (2006) : intervalles pour l'ICC par modélisation bayésienne ; extensions : ajustement sur covariables, estimation simultanée de plusieurs ICC. Stat Med 25(9):1443–1456 [abstract] — [PubMed 16220510](https://pubmed.ncbi.nlm.nih.gov/16220510/)
- Lewis & Julious (2021) [lu] : prendre la borne haute de l'IC à 95 % de l'ICC est courant mais « a largely inefficient method which can result in overpowered main trials » ; supposer simplement des ICC élevés est « not recommended » ; méthode proposée : intégrer la taille d'échantillon sur toutes les valeurs plausibles de l'ICC (bornes d'intégration = IC à 99,8 %) ; elle « will still result in a loss of power if the ICC estimate is very imprecise » ; IC de l'ICC par trois méthodes reprises d'Ukoumunne 2002 : Searle la plus prudente, Swiger la moins. Stat Methods Med Res 30(11):2459–2470 — [PMC8649444](https://pmc.ncbi.nlm.nih.gov/articles/PMC8649444)
- Prolongement « hybride » par assurance (Williamson, Tishkovskaya & Wilson 2023, préprint) : selon le résumé de recherche, intégrer l'incertitude sur les trois paramètres de nuisance plutôt que sur le seul ICC n'augmente pas notablement la taille requise [résumé] — [arXiv 2308.11278](https://arxiv.org/abs/2308.11278)
- Ukoumunne (2002) : simulation comparant les IC de l'estimateur ANOVA de l'ICC ; méthodes « variance-ratio » de meilleure couverture ; la non-normalité des effets de grappe dégrade toutes les méthodes ; une précision raisonnable demande beaucoup plus de grappes que les essais habituels. **D'après les notices, il porte sur des issues continues (essai asthme), pas binaires** — le brief l'attribue aux binaires. Stat Med 21(24):3757–3774 [abstract/résumé] — [PubMed 12483765](https://pubmed.ncbi.nlm.nih.gov/12483765/)
- Pour les binaires : Zou & Donner (2004) étudient les IC de l'ICC fondés sur l'ANOVA, l'estimateur de Pearson par paires, la vraisemblance profilée bêta-binomiale et une approche hybride. Biometrics 60(3):807–811 [résumé] — [IDEAS](https://ideas.repec.org/a/bla/biomet/v60y2004i3p807-811.html). Une revue ultérieure (Shan) rapporte que l'IC de Fleiss–Cuzick y garde une couverture proche du nominal sur une large plage, comparé aux IC ANOVA et Zou–Donner [résumé, page non ouverte] — [PMC9225324](https://pmc.ncbi.nlm.nih.gov/articles/PMC9225324)
- Ridout, Demétrio & Firth (1999) : revue et simulation de nombreux estimateurs de l'ICC binaire ; performance relative dépendant de plusieurs facteurs « in complex ways ». Biometrics 55(1):137–148 [résumé] — [notice](https://www.bohrium.com/paper-details/estimating-intraclass-correlation-for-binary-data/812349946677166081-922)
- Gulliford et al. (2005) : log ICC linéairement associé au log prévalence (données GPRD et 136 ICC d'une revue HTA) ; prévalence médiane 6,5 %, ICC médian 0,006 (IQR 0,0003–0,036) ; ICC prédit ≈ 0,002–0,008 à 1 % de prévalence contre ≈ 0,046–0,075 à 40 % ; la prévalence peut guider l'hypothèse d'ICC. J Clin Epidemiol 58:246–251 [résumé] — [UKHSA](https://researchportal.ukhsa.gov.uk/en/publications/intraclass-correlation-coefficient-and-outcome-prevalence-are-ass/)
- Campbell, Fayers & Grimshaw (2005) : 220 ICC de recherche d'implémentation ; l'ICC varie selon le contexte et le type d'issue (plus élevé pour les issues de processus et en soins secondaires). Clin Trials 2(2):99–107 [abstract] — [PubMed 16279131](https://pubmed.ncbi.nlm.nih.gov/16279131/)
- Campbell, Grimshaw & Elbourne (2004) : rapporter un ICC selon trois dimensions — description du jeu de données, méthode de calcul, précision. BMC Med Res Methodol 4:9 [résumé] — [PDF](https://bmcmedresmethodol.biomedcentral.com/track/pdf/10.1186/1471-2288-4-9)
- CONSORT, extension grappes (2012), item 7a : la justification d'effectif donne l'ICC supposé « and an indication of its uncertainty » [mémoire] — [BMJ 2012;345:e5661](https://www.bmj.com/content/345/bmj.e5661)
- Eldridge, Ashby & Kerry (2006) : effet de plan avec tailles de grappes variables, DE = 1 + ((CV² + 1) m̄ − 1) ρ (CV = coefficient de variation des tailles). Int J Epidemiol 35(5):1292–1300 [abstract ; formule via sources secondaires] — [PubMed 16943232](https://pubmed.ncbi.nlm.nih.gov/16943232/) ; formule : [annexe UCL](https://discovery-pp.ucl.ac.uk/397503/5/1748-5908-5-86-s4.pdf) ; effet négligeable si CV < ≈ 0,23 [résumé secondaire] — [notice](https://synapsesocial.com/papers/W2153247789)
- Repère « évaluations d'IA » : dans les exemples de Miller (2024), les erreurs-types groupées peuvent dépasser 3 fois les erreurs-types naïves [résumé] — [arXiv 2411.00640](https://arxiv.org/abs/2411.00640)

### Inferences
- **Le transfert ERG → certification est asymétrique.** En ERG, ρ sert à dimensionner ; la validité (type I) est protégée par l'analyse, qui ré-estime la grappe sur les données. Ici ρ entre **dans la borne de certification** : le sous-estimer produit directement des fausses certifications. Le verdict « borne haute = inefficace » (Lewis & Julious) porte sur un coût de puissance ; dans une règle de sûreté, ce coût est le prix de la validité. Ne pas importer ce verdict tel quel.
- Les méthodes « moyenne sur l'a priori » (Turner 2004 ; Lewis & Julious) contrôlent une propriété moyenne. L'équivalent pour une garantie de sûreté est un **quantile haut** de l'a priori ou du postérieur, pas sa moyenne.
- Les bases d'ICC publiées (santé, médiane 0,006 chez Gulliford) ne se transposent pas aux tâches d'agents (ρ mesurés 0,3 à 0,7 ; ratio d'erreurs-types > 3 chez Miller, soit DE > 9 puisque DE = ratio²). Aucune base de référence d'ICC « agents » n'existe pour un quantile publié.
- Si les tâches n'ont pas toutes le même nombre d'essais, n_eff = n / (1 + (m̄ − 1) ρ) **sous-estime** l'effet de plan (Eldridge 2006) : autre source d'anti-conservatisme, indépendante du choix de ρ.
- Prévalence : sous un mécanisme logit-normal, l'ICC en proportions tend vers 0 quand p → 0 (cohérent avec Gulliford) ; sous un mécanisme « tâche qui échoue toujours », il reste proche de 1 quel que soit p. Une strate sans erreur ne permet pas de distinguer les deux.

### Gaps
- Pas trouvé de recommandation ERG propre au choix de ρ pour issues **rares**.
- Pas trouvé de règle standard « prendre le Xe centile des ICC publiés ».
- Texte intégral de Turner 2005 (formes de lois, schéma de sous-pondération) non lu.
- Couverture des IC binaires de Zou & Donner à faible prévalence non vérifiée en source primaire.

## 2. Rétrécissement empirique-bayésien ou hiérarchique des ICC par strate

### Takeaway
Mise en œuvre standard : une loi commune sur les paramètres de dispersion par unité (ICC, dispersion bêta-binomiale ou binomiale négative), centre et largeur estimés sur toutes les unités, chaque estimation tirée vers le centre selon son manque d'information. Avec zéro événement, la vraisemblance de la strate est plate en ρ : le postérieur égale la loi commune. Le rétrécissement devient un pur emprunt, mais avec sa dispersion, qu'il faut propager. La génomique ajoute un garde-fou asymétrique : ne pas rétrécir une estimation nettement au-dessus de la tendance (DESeq2 : plus de 2 écarts-types résiduels), car cela crée des faux positifs. C'est un précédent publié de la règle max(propre, base).

### Cited Findings
- Turner, Thompson & Spiegelhalter (2005) : modèle hiérarchique sur plusieurs estimations d'ICC, sous-pondération selon pertinence et précision [abstract] — [PubMed 16279132](https://pubmed.ncbi.nlm.nih.gov/16279132/)
- Turner, Omar & Thompson (2006) : estimation bayésienne simultanée de plusieurs ICC, avec ajustement sur covariables [abstract] — [PubMed 16220510](https://pubmed.ncbi.nlm.nih.gov/16220510/)
- DESeq2 (Love, Huber & Anders 2014) [lu] : dispersions par gène rétrécies « toward the values predicted by the curve » ; largeur de l'a priori estimée sur les données ; « as the sample size increases, the shrinkage decreases in strength » ; estimation propre conservée quand elle est « more than 2 residual standard deviations above the curve », parce que certains gènes sont plus variables et que « inference based on the shrunken dispersion estimates could lead to undesirable false positive calls » ; gènes à faible comptage moyen écartés par filtrage indépendant ; gènes à somme nulle exclus de l'analyse des faux positifs du banc d'essai. Genome Biol 15:550 — [article](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-014-0550-8), lu via [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4302049/fullTextXML)
- DSS (méthylation) : bêta-binomiale par site CpG ; dispersion estimée par un estimateur de rétrécissement issu d'un modèle bayésien hiérarchique (a priori log-normal) ; emprunt d'information entre sites quand les réplicats sont peu nombreux [résumé] — [Bioconductor DSS](https://bioconductor.org/packages/release/bioc/html/DSS.html) ; article 2014 [PMC4005660](https://rcastoragev2.blob.core.windows.net/282a111b24219fd349fd48ba6814b934/PMC4005660.pdf) (Feng, Conneely & Wu, Nucleic Acids Res 2014 [mémoire pour les auteurs])
- Analogue méta-analytique (variance entre unités, peu d'unités informatives) : avec peu d'études, l'incertitude sur l'hétérogénéité reste « consistent with small to large heterogeneity » ; recommandation d'a priori faiblement informatifs (demi-normale d'échelle 0,5 ou 1,0 sur le log-OR) ; avec très peu d'études, les intervalles dépendent du choix de l'a priori. Friede et al., Res Synth Methods 2017 [résumé] — [PMC5347842](https://pmc.ncbi.nlm.nih.gov/articles/PMC5347842)

### Inferences
- **[calcul] Strate sans erreur = aucune information sur ρ.** Sous bêta-binomiale, la vraisemblance d'une strate sans erreur vaut 1 en p → 0 quel que soit ρ ; le profil de ρ est plat ; le postérieur de ρ est la loi commune.
- **[calcul] Une strate sans erreur est plus probable quand ρ est élevé.** À p fixé, P(tâche sans erreur) croît avec ρ. θ = 0,02, m = 10 : 0,817 (ρ = 0), 0,869 (0,1), 0,917 (0,3), 0,943 (0,5), 0,961 (0,7), 0,974 (0,9), 0,980 (1). Cohérent avec la convexité de (1 − x)^m et l'ordre convexe des lois bêta de même moyenne. Les strates où ρ est inestimable sont donc celles où un ρ élevé est le plus dangereux.
- **Gonflement de l'emprunt (0,43 pour 0 vrai).** Un ANOVA poolé sans terme « configuration » compte la variance de p entre configurations comme variance entre tâches. Remède hiérarchique : p propre à chaque configuration (effets fixes), loi commune sur ρ seul (ou sur la variance inter-tâches). Cohérent avec l'ajustement sur covariables de Turner 2006. Ce gonflement est conservateur : perte de puissance, pas de fausse certification.
- Le garde-fou de DESeq2 justifie la règle max(propre, base) : ne jamais tirer vers le bas une estimation nettement au-dessus de la base. La règle actuelle le fait déjà pour les configurations « ≥ 10 erreurs dans ≥ 5 tâches ».
- Échelle : une loi commune portée sur l'échelle latente (variance inter-tâches en logit) est plus transportable entre strates de taux différents qu'une loi sur ρ en proportions (cf. Gulliford). Elle ne règle pas le cas « tâches déterministes ». Pour la décision, utiliser un quantile haut du postérieur de ρ (p. ex. 95e), pas sa moyenne.

### Gaps
- Aucune source trouvée sur le rétrécissement d'ICC entre strates **avec beaucoup de strates sans événement**, ni en ERG ni en évaluation d'IA.
- Traitement exact des gènes tout à zéro dans l'ajustement de dispersion de DESeq2 non vérifié (seulement filtrage et exclusion du banc d'essai).
- Pas de simulation publiée trouvée sur le biais de l'ANOVA poolé sous hétérogénéité de p entre configurations.

## 3. Fixer ρ d'avance, borne haute de confiance ou estimation avec plancher ? Pratique des domaines critiques

### Takeaway
Trois options sont valides par construction : (a) ρ fixé à la plus grande valeur plausible ; à la limite ρ = 1, n_eff = nombre de tâches, valide pour tout ρ vrai ; (b) Berger–Boos : prendre le pire ρ d'un ensemble de confiance à 1 − γ et retrancher γ de α ; (c) inférence bayésienne prudente (pire a priori compatible avec ce qu'on sait). L'estimation avec plancher n'est valide que si ρ vrai ≤ plancher ou si l'estimation est fiable : c'est justement ce qui manque dans les strates sans erreur. Les domaines critiques n'estiment pas la dépendance sur les données qu'ils certifient : IEC 61508 fixe β par liste de contrôle ; la fiabilité logicielle prudente traite le doute sur l'indépendance au pire ; le LQAS en grappes fixe l'ICC par hypothèse et valide par simulation. Les enquêtes (Korn–Graubard, NCHS) estiment l'effet de plan mais plafonnent n_eff à n, corrigent les degrés de liberté et imposent un n_eff minimal.

### Cited Findings
- Berger & Boos (1994) : p-valeur valide p_C = sup sur θ ∈ C_β de p(θ), plus β, où C_β est un ensemble de confiance à 1 − β pour la nuisance ; maximiser sur tout l'espace peut coûter beaucoup de puissance ; le comportement aux bords dépend de la statistique et de la valeur de la nuisance. JASA 89(427):1012–1016 [résumé] — [notice](https://scilit.com/publications/ca7db59ac28da80d53233761e14b623b) ; [DOI](https://doi.org/10.1080/01621459.1994.10476836) ; validité rappelée dans [arXiv 2001.05126](https://arxiv.org/pdf/2001.05126)
- Salako & Zhao (2023) : l'hypothèse i.i.d. peut rendre les évaluations bayésiennes de fiabilité « extremely optimistic » ; l'inférence bayésienne prudente (CBI) rend l'hypothèse d'indépendance inutile en intégrant le doute sur elle dans l'évaluation ; bornes prudentes sur la probabilité de défaillance à la demande après des tests sans défaillance ; exemple d'un système de protection nucléaire. IEEE TSE 49(4):2829–2838 [résumé] — [arXiv 2208.00462](https://arxiv.org/abs/2208.00462). Suite : « Demonstrating software reliability using possibly correlated tests », Qual Reliab Eng Int 2024 [résumé, non ouvert].
- IEC 61508-6:2010 : β (part des défaillances de cause commune) déterminé par une liste de 37 questions couvrant 8 mesures de défense, scores cumulés convertis en β ; méthode qualitative, opposée aux modèles quantitatifs estimés sur données historiques [lu] — Govardhan Rao, Castellanos-Ardila & Punnekkat, « A Proposal for Enhancing IEC 61508 Methodology for the β-Factor Estimation », Springer 2024, DOI 10.1007/978-3-031-71139-8_20 — [PDF](https://www.es.mdu.se/pdf_publications/7020.pdf)
- Korn & Graubard (1998) : CP modifié pour enquêtes complexes à faible nombre attendu de positifs, n remplacé par n_eff ; meilleure couverture que les IC normaux, logit ou Poisson dans des simulations limitées. Survey Methodology, p. 193–201 [résumé] — [Statistique Canada](https://www150.statcan.gc.ca/n1/en/catalogue/12-001-X19980024356) ; implémenté par `svyciprop(method = "beta")` du paquet R survey [résumé] — [doc](https://r-survey.r-forge.r-project.org/survey/html/svyciprop.html)
- NCHS (Parker et al. 2017) [lu] : n_e* = min(n, (n / DEFF) · (t_{n−1, α/2} / t_{df, α/2})²), n_eff corrigé des degrés de liberté et plafonné à n (contrainte active si DEFF < 1) ; suppression si n < 30 ou n_eff < 30 ; revue si df < 8, car « the precision of the estimated variance is approximately related to the square root of the degrees of freedom » ; le cas p̂ = 0 n'est pas traité sur la page — [tutoriel NHANES](https://wwwn.cdc.gov/nchs/nhanes/tutorials/reliabilityofestimates.aspx)
- Dean & Pagano (2015) : simulation sur plan d'enquête 30 × 7 ; quand l'ICC est élevé et la prévalence < 0,10, Agresti–Coull et CP sur n_eff sont les meilleurs ; Wald mauvais. JSSAM 3(4):484–503 [résumé] — [notice](https://www.technet-21.org/en/resources/journal-article/survey-publication-dean-j-survey-stats-methods-2015)
- Échantillonnage d'acceptation en grappes (LQAS) : Olives et al. (2009) valident des plans par simulation ; un ICC modéré laisse les plans approximativement valides, une corrélation forte gonfle fortement l'erreur de classification. JRSS-A 172(2):495–510 [résumé] — [EconPapers](https://econpapers.repec.org/RePEc:bla:jorssa:v:172:y:2009:i:2:p:495-510). Hedt-Gauthier et al. (2013) : cadre bêta-binomial pour le LQAS en grappes [résumé] — [notice](https://test.chwcentral.org/resources/the-effect-of-clustering-on-lot-quality-assurance-sampling-a-probabilistic-model-to-calculate-sample-sizes-for-quality-assessments/). Hund, Bedrick & Pagano (2015) : les tailles d'échantillon diffèrent beaucoup selon la paramétrisation de la grappe ; aucune paramétrisation existante ne colle clairement aux données observées [résumé] — [PMC4488393](https://pmc.ncbi.nlm.nih.gov/articles/PMC4488393)
- ERG à peu de grappes : sans correction petits échantillons, erreurs de type I gonflées ; analyses au niveau grappe et modèles avec correction des degrés de liberté ≤ 5 % (issues continues). Leyrat et al., Int J Epidemiol 2018;47(1):321–331 [résumé] — [LSHTM](https://researchonline.lshtm.ac.uk/id/eprint/4539073). Inflation signalée jusqu'à 70 grappes pour modèles mixtes ou GEE sans correction : Kahan et al., Trials 2016;17:438 [mémoire].
- FDA (2019) : on peut argumenter que certains scénarios ont nécessairement une erreur de type I plus faible que d'autres « based on monotonicity » [lu] — [FDA, Adaptive Designs for Clinical Trials of Drugs and Biologics](https://www.fda.gov/media/78495/download)

### Inferences
- **[calcul] Coût d'un ρ sous-estimé dans la plus petite strate certifiable à zéro erreur.** Avec zéro erreur, CP certifie si 1 − α^(1/n_eff) < θ, soit n_eff > ln α / ln(1 − θ). On prend le plus petit nombre de tâches k qui certifie avec ρ supposé, puis on calcule le vrai risque P(0 erreur | p = θ, ρ vrai) = P(tâche sans erreur)^k sous bêta-binomiale. α = 0,05 ; m ∈ {5, 10, 20} ; θ ∈ {0,01 ; 0,05}. Plages sur ces six cas :

  | ρ supposé | k minimal (m = 10, θ = 0,05 / 0,01) | ρ vrai = 0,3 | 0,5 | 0,7 | 0,9 | 1 |
  |---|---|---|---|---|---|---|
  | 0,3 | 22 / 111 | 0,003–0,018 | 0,026–0,049 | **0,098–0,108** | **0,20–0,25** | **0,26–0,37** |
  | 0,5 | 33 / 164 | ≤ 0,004 | 0,003–0,017 | 0,027–0,047 | **0,107–0,118** | **0,16–0,21** |
  | 1 | 59 / 299 | ≈ 0 | ≤ 0,001 | 0,001–0,006 | 0,016–0,026 | 0,048–0,050 |

  Code (reproductible) :
  ```python
  from math import log, exp
  def p0(theta, rho, m):  # P(tâche de m essais sans erreur), bêta-binomiale de moyenne theta, ICC rho
      if rho >= 1: return 1 - theta
      if rho <= 0: return (1 - theta) ** m
      a, b = theta * (1 - rho) / rho, (1 - theta) * (1 - rho) / rho
      return exp(sum(log((b + i) / (a + b + i)) for i in range(m)))
  # k minimal : k*m/(1+(m-1)*rho_suppose) > log(alpha)/log(1-theta) ; risque réel = p0(theta, rho_vrai, m)**k
  ```
- Lecture du tableau : quand ρ supposé = ρ vrai, le risque à zéro erreur reste ≤ α (l'approximation n_eff tient ici). Le plancher 0,3 échoue nettement à ρ ≥ 0,7 **dans les petites strates sans erreur** : le 4 % mesuré est une moyenne de scénarios ; la pire cellule peut être bien plus haute. ρ = 1 reste ≤ 0,050 partout. Son coût : k minimal multiplié par ≈ 2,7 face à ρ = 0,3 (22 → 59 tâches pour θ = 0,05, m = 10).
- **Monotonie** : à zéro erreur, le risque croît avec ρ vrai (cf. section 2). ρ = 1 est donc le point le moins favorable. L'argument de monotonie admis par la FDA permet de simuler ρ = 1 pour couvrir ]0,9 ; 1]. Pour x ≥ 1 erreur, la monotonie n'est pas démontrée ici : à simuler.
- **Options comparées** (synthèse de ce qui précède) :

  | Option | Si ρ vrai > valeur utilisée | Coût en puissance | Hypothèse clé | Précédent |
  |---|---|---|---|---|
  | ρ = 1 (n_eff = nombre de tâches) | valide pour tout ρ (montré à x = 0) | maximal | aucune | analyse au niveau grappe (Leyrat) ; démonstration par unités indépendantes |
  | ρ fixé à 0,5 | risque 0,11–0,21 à ρ ≥ 0,9 | intermédiaire | ρ vrai ≤ 0,5 | IEC 61508 (β fixé a priori) |
  | Borne haute Berger–Boos (γ pris sur α) | valide si l'ensemble de confiance l'est pour la strate | γ + largeur de l'ensemble | ρ commun aux strates si emprunt | Berger & Boos 1994 |
  | Estimation + plancher 0,3 (actuel) | si la valeur retenue est 0,3 : risque 0,10–0,37 à ρ vrai ≥ 0,7 dans les petites strates sans erreur (moins si la base empruntée est plus haute) | faible | ρ vrai ≤ max(plancher, ρ̂) | plafond DEFF ≥ 1 du NCHS (plus faible) |
  | Postérieur hiérarchique, quantile haut | valide si l'a priori commun est pertinent ou prudent | modéré | échangeabilité des strates | Turner 2005 ; DESeq2, DSS ; CBI |
  | max(propre, base) pour strates informatives | protège contre une base trop basse | faible | seuil d'information fiable | DESeq2 (> 2 écarts-types résiduels) |

- Strate sans erreur : seules deux positions sont cohérentes. Soit ρ = 1 (aucune hypothèse), soit l'ensemble de confiance ou le postérieur de ρ issu des autres strates, sous une hypothèse d'échangeabilité **pré-enregistrée**. Emprunter une estimation ponctuelle sans son incertitude n'est ni l'un ni l'autre.
- La correction de degrés de liberté de Korn–Graubard propage l'incertitude d'un effet de plan estimé. Exemple : avec 5 tâches (df = 4), le facteur (1,96 / 2,776)² ≈ 0,50 divise n_eff par deux. Elle n'est pas définie quand p̂ = 0.
- Comme en LQAS, la paramétrisation de la grappe compte (Hund 2015) : la valeur prudente de ρ dépend du modèle générateur supposé (bêta-binomial, logit-normal, mélange « tâches déterministes »).

### Gaps
- Valeurs de la table D.4 d'IEC 61508-6 (score → β) non vérifiées.
- Aucune norme de démonstration de fiabilité trouvée qui corrige les tailles « zéro défaillance » (success-run) pour des défaillances corrélées, hors littérature CBI.
- ISO 2859 / ANSI Z1.4 non examinées pour des dispositions « grappes ».
- Aucun guide FDA ou EMA propre au choix de l'ICC trouvé ; seul le guide FDA général sur les plans adaptatifs est cité.
- Aucune application publiée de Berger–Boos à un ICC avec CP discret trouvée.

## 4. Combien de grappes avec au moins un événement avant qu'une estimation de ρ soit utilisable ?

### Takeaway
Aucune règle publiée propre au « nombre de grappes avec ≥ 1 événement » pour estimer un ICC binaire rare n'a été trouvée. Les repères les plus proches demandent tous bien plus que « ≥ 10 erreurs dans ≥ 5 tâches » : régression logistique multiniveau (≥ 50 à 100 groupes, plus d'un événement attendu par groupe), règles de fiabilité d'enquête (n_eff ≥ 30, df ≥ 8), littérature des études pilotes (estimation imprécise et biaisée vers le bas sauf grand nombre de grappes).

### Cited Findings
- Moineddin, Matheson & Glazier (2007) : composantes de variance légèrement biaisées même avec 100 groupes de 50 ; erreurs-types des composantes sous-estimées ; biais sévères avec des groupes de 5 ; recommandation : ≥ 50 groupes de ≥ 50 ; pour des événements peu fréquents, ≥ 100 groupes de 50 et taille de groupe telle que le nombre attendu d'événements par groupe dépasse 1. BMC Med Res Methodol 7:34 [résumé] — [PMC1955447](https://pmc.ncbi.nlm.nih.gov/articles/PMC1955447)
- Eldridge, Costelloe, Kahan, Lancaster & Kerry : les pilotes sont en général trop petits pour estimer l'ICC ; les tailles d'essai qui en découlent sont probablement biaisées vers le bas et très imprécises sauf grand nombre de grappes et d'individus (ICC simulés 0,01, 0,05, 0,2). Stat Methods Med Res, DOI 10.1177/0962280215588242 [résumé] — [Lancaster](https://eprints.lancs.ac.uk/id/eprint/73984)
- Ukoumunne (2002) : une précision raisonnable sur l'ICC exige beaucoup plus de grappes que les essais habituels (issues continues) [résumé] — [PubMed 12483765](https://pubmed.ncbi.nlm.nih.gov/12483765/)
- Lewis & Julious (2021) [lu] : « 4–8 clusters of 15–20 individuals per arm will approach the asymptote » dans de nombreux cas, présenté comme repère grossier, issues continues ; la taille « adéquate » d'un pilote dépend du nombre de grappes, de l'ICC, de l'effet et de la taille des grappes — [PMC8649444](https://pmc.ncbi.nlm.nih.gov/articles/PMC8649444)
- NCHS [lu] : n_eff ≥ 30 et revue si df < 8 (df = unités primaires − strates) — [tutoriel NHANES](https://wwwn.cdc.gov/nchs/nhanes/tutorials/reliabilityofestimates.aspx)
- Méta-analyse : avec peu d'unités, l'hétérogénéité reste compatible avec des valeurs faibles comme fortes (Friede et al. 2017) [résumé] — [PMC5347842](https://pmc.ncbi.nlm.nih.gov/articles/PMC5347842)

### Inferences
- Avec des erreurs rares, le nombre attendu d'erreurs par tâche est ≪ 1 : on est hors du domaine où Moineddin trouve des composantes de variance fiables. L'information sur ρ vient presque seulement des tâches avec ≥ 1 erreur. Transposer « df ≥ 8 » aux tâches avec erreur donnerait ≥ 9 tâches avec erreur dans une strate : c'est une analogie, pas une règle publiée. Le seuil actuel (≥ 5 tâches) est en dessous.
- Alternative auto-calibrée, pré-enregistrable : n'utiliser l'estimation propre que si sa borne haute à 1 − γ est inférieure à la valeur de repli (ρ = 1 ou base prudente). Sinon, garder le repli. Le seuil n'est plus un comptage arbitraire mais une condition d'information.
- Ou bien calibrer un seuil de comptage par simulation : plus petit nombre de tâches avec erreur pour lequel la borne haute de ρ couvre ρ vrai au niveau nominal sur toute la grille (section 5).

### Gaps
- Aucune règle d'information minimale publiée pour l'ICC binaire rare.
- Aucune simulation publiée trouvée sur la loi d'échantillonnage de l'ANOVA ρ̂ en fonction du nombre de grappes avec événement.
- Conclusions de Ridout 1999 sur le biais de l'ANOVA à faible prévalence non récupérées.

## 5. Valider le choix avant de voir les données : simulation des caractéristiques opératoires

### Takeaway
La pratique admise (FDA 2019) : simulations pré-spécifiées sur une grille de paramètres de nuisance plausibles, conclusion portant sur l'erreur de type I **maximale** sur la grille, nombre de réplicats justifié (100 000 par scénario donne ≈ ± 0,1 %), arguments de monotonie pour couvrir l'entre-deux, et contrôle après coup que les nuisances observées tombent dans la grille. Pour ρ : inclure 0,7, 0,9 et 1, plusieurs modèles générateurs, l'hétérogénéité entre configurations et les strates sans erreur.

### Cited Findings
- FDA (2019) [lu] : pour l'erreur de type I, simuler « under a series of assumptions compatible with the null hypothesis » ; les scénarios « may include varying assumptions about nuisance parameters » ; « It is common to perform simulations on a grid of plausible values and argue [...] that maximal Type I error probability likely does not exceed a desired level across the range covered by the grid » ; monotonie admise ; si une nuisance observée sort de la plage simulée, « additional simulations would be required » ; « Using 100,000 iterations per scenario [...] ensures a 95% confidence interval for estimated Type I error probability with a width of approximately ± 0.1% » ; graines différentes par scénario ; le rapport de simulation donne les configurations de paramètres avec justification, le nombre de réplicats avec justification, les résultats par scénario et le code — [Adaptive Designs for Clinical Trials of Drugs and Biologics, novembre 2019](https://www.fda.gov/media/78495/download)
- Olives et al. (2009) : précédent de validation par simulation d'un plan d'acceptation en grappes selon l'ICC [résumé] — [EconPapers](https://econpapers.repec.org/RePEc:bla:jorssa:v:172:y:2009:i:2:p:495-510)
- Hund, Bedrick & Pagano (2015) : les résultats dépendent de la paramétrisation de la grappe [résumé] — [PMC4488393](https://pmc.ncbi.nlm.nih.gov/articles/PMC4488393)
- Grilles d'ICC usuelles en ERG : 0,01, 0,05, 0,2 chez Eldridge et al. [résumé] — [Lancaster](https://eprints.lancs.ac.uk/id/eprint/73984)
- Cadre ADEMP pour planifier et rapporter une étude de simulation, avec erreur Monte-Carlo de chaque estimation : Morris, White & Crowther, Stat Med 2019;38:2074–2102 [mémoire] — [DOI](https://doi.org/10.1002/sim.8086)
- Supposer l'indépendance rend les conclusions de fiabilité trop optimistes (Salako & Zhao 2023) [résumé] — [arXiv 2208.00462](https://arxiv.org/abs/2208.00462)

### Inferences
- **[calcul] Précision Monte-Carlo.** Si cet IC est un IC binomial à 95 %, « 4 %, IC jusqu'à 6,9 % » correspond à environ 175–200 réplicats (demi-largeur 1,96·√(0,04·0,96/n) ≈ 0,029). Pour montrer qu'un taux vrai de 4 % est < 5 % avec une borne unilatérale à 95 %, il faut ≈ 1 040 réplicats par cellule (1,645²·0,04·0,96 / 0,01²). Le repère FDA (100 000) donne ≈ ± 0,1 %.
- Grille proposée : ρ ∈ {0 ; 0,1 ; 0,3 ; 0,5 ; 0,7 ; 0,9 ; 1} ; p au seuil θ (point le moins favorable) et juste au-dessus ; k et m̄ du plan réel, avec variabilité des tailles (CV) ; strates sans erreur et à 1–3 erreurs ; une configuration qui erre beaucoup (gonflement de l'emprunt) ; trois modèles générateurs : bêta-binomial, logit-normal, mélange « tâches qui échouent toujours / jamais ».
- Critère pré-enregistré : la **cellule maximale**, pas la moyenne, avec sa borne Monte-Carlo, ≤ α (ou ≤ α + tolérance fixée d'avance).
- Couvrir ]0,9 ; 1] par la monotonie (démontrée à x = 0, section 3) ; la vérifier par simulation pour x ≥ 1.
- Après les données : si ρ̂ ou l'hétérogénéité entre configurations sort de la grille, simulations complémentaires (FDA).

### Gaps
- Aucune source ne prescrit une grille d'ICC précise ; les grilles d'ERG trouvées s'arrêtent vers 0,2, loin de 0,7–0,9.
- Le guide FDA vise les essais adaptatifs de médicaments : l'appliquer à une certification d'agents est un transfert par analogie.
