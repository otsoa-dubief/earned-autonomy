# Zéro numérateur et information minimale : quand peut-on dire qu'un taux d'erreur est « sous le seuil » ?

Notes de recherche (web, novembre 2026). Notations : x erreurs observées sur n écritures d'un type d'action ; seuil (« barre ») b ; λ_b = n·b (ou n_eff·b) = nombre d'erreurs **attendu si le vrai taux était exactement b**. Les calculs marqués « (calcul) » ont été faits par moi (scipy, binomiale exacte ou approximation de Poisson, sans grappes). Ce ne sont pas des faits sourcés.

---

## 1. Le problème du zéro numérateur : ce que montre un compte nul, et ce qu'il ne montre pas (règle de trois et résultats associés)

### Takeaway
Zéro événement sur n essais indépendants borne le taux à environ 3/n (borne supérieure unilatérale à 95 %), et pas à 0. Un zéro n'est donc informatif face à une barre b que si n·b ≳ 3 pour une « preuve » à 95 %. En pratique, « combien d'essais avant qu'un zéro veuille dire quelque chose » se calcule par inversion : n ≥ 3/b, ou n = ln(1−C)/ln(R) en fiabilité. Les versions bayésiennes dépendent fortement de l'a priori quand le compte est nul. Et le réflexe « conservateur » de la borne à 95 % peut se retourner contre la décision en aval.

### Cited Findings
- **Hanley & Lippman-Hand (1983)**, « If nothing goes wrong, is everything all right? Interpreting zero numerators », *JAMA* 249(13):1743-1745, DOI 10.1001/jama.1983.03330370053031. Notice bibliographique : [JAMA](https://jamanetwork.com/journals/jama/article-abstract/389714) ; [DOI](https://doi.org/10.1001/jama.1983.03330370053031).
- Énoncé de la règle de trois : « 3/n is a good approximation for an upper 95% confidence bound for p when we have seen n independent trials with no occurrences of the event of interest (Louis 1981; Hanley and Lippman-Hand 1983) ». Elle est « quite simple and very accurate for large n ». Source : [Winkler, Smith & Fryback 2002, *Am Stat* 56(1):1-4](https://jimsmith.host.dartmouth.edu/wp-content/uploads/2022/04/The_Role_of_Informative_Priors_in_Zero_Numerator_Problems.pdf).
- Les exemples de Hanley & Lippman-Hand, cités par Winkler et al. : « a still-perfect surgical record, a field trial of a vaccine that uncovered no major side effects, … an airline that has never had a fatality ». Winkler et al. ajoutent qu'une fréquence observée de zéro « is an indication of a low probability, but it clearly does not imply a probability of zero ». — [Winkler et al. 2002](https://jimsmith.host.dartmouth.edu/wp-content/uploads/2022/04/The_Role_of_Informative_Priors_in_Zero_Numerator_Problems.pdf)
- Le résumé de Hanley & Lippman-Hand pose le constat de départ : l'absence d'événement « seems to be viewed as very different both quantitatively and qualitatively from the occurrence of one or more events ». Je n'ai que le début du résumé, lu dans un extrait de recherche. — [JAMA](https://jamanetwork.com/journals/jama/article-abstract/389714)
- L'exemple canonique de Hanley & Lippman-Hand, repris par Winkler et al. Un ancien produit de contraste provoque une réaction grave chez environ 15 patients sur 10 000, soit 1,5 ‰. Le nouveau produit est testé sur 167 patients, sans aucune réaction. La règle de trois dit qu'on peut être sûr à 95 % que le risque vaut au plus 3/167 = 0,018 (1,8 %), alors que l'estimateur du maximum de vraisemblance vaut 0. — [Winkler et al. 2002](https://jimsmith.host.dartmouth.edu/wp-content/uploads/2022/04/The_Role_of_Informative_Priors_in_Zero_Numerator_Problems.pdf)
- La borne exacte unilatérale à 95 % est 1 − 0,05^(1/n), et non 1 − 0,95^(1/n). C'est la correction faite par Winkler dans sa réponse à Browne. — [Comments & Reply, *Am Stat* 56(3):252-253, 2002](https://jimsmith.host.dartmouth.edu/wp-content/uploads/2022/04/The_Role_of_Informative_Priors_in_Zero_Numerator_Problems_Comments_and_Replies.pdf)
- **Browne (2002)**. 3/n surestime la borne exacte p95 de 20 % ou plus pour n < 9, de 7,8 % pour n = 20, et encore de plus de 2 % pour n = 80. Il propose une « Modified Rule of Three » 3/(n+1,7), qui sous-estime p95 de moins de 1 % pour tout n > 3. — [Comments & Reply 2002](https://jimsmith.host.dartmouth.edu/wp-content/uploads/2022/04/The_Role_of_Informative_Priors_in_Zero_Numerator_Problems_Comments_and_Replies.pdf)
- **Eddings (2002)** propose les intervalles de vraisemblance (« support intervals », Royall 1997). Avec 0 succès sur n essais, l'intervalle 1/k est (0, 1 − k^(−1/n)) ; les valeurs typiques de k sont 8 et 32. L'IC exact (0, 1 − α^(1/n)) correspond à k = 1/α, soit k = 20 à 95 %. La règle de trois correspond asymptotiquement à k = e³ ≈ 20,1, mais pour n < 10 elle peut inclure des valeurs de très faible vraisemblance relative. — [Comments & Reply 2002](https://jimsmith.host.dartmouth.edu/wp-content/uploads/2022/04/The_Role_of_Informative_Priors_in_Zero_Numerator_Problems_Comments_and_Replies.pdf)
- **Jovanovic & Levy (1997)**, « A Look at the Rule of Three », *The American Statistician* 51(2):137-139, DOI 10.1080/00031305.1997.10473947. Le résumé dit que 3/n donne une borne supérieure à 95 % d'une probabilité binomiale quand aucun événement ne survient en n essais indépendants, discute la validité en petit échantillon et propose des alternatives. — [Scilit](https://scilit.com/publications/9556769c9079eff2c67f7e5569fb27ce)
- Selon Winkler et al., Jovanovic & Levy ont dérivé des « Bayesian Rules of Three » qui approchent le fractile 0,95 de l'a posteriori. Sous a priori uniforme, l'a posteriori est Beta(1, n+1) et la règle devient 3/(n+1) ; J&L qualifient cet a priori de « a limiting and most conservative prior in this context ». Sous a priori Beta(1, b) avec b ≥ 1, la règle devient 3/(n+b). — [Winkler et al. 2002](https://jimsmith.host.dartmouth.edu/wp-content/uploads/2022/04/The_Role_of_Informative_Priors_in_Zero_Numerator_Problems.pdf)
- **Eypasch, Lefering, Kum & Troidl (1995)**, « Probability of adverse events that have not yet occurred: a statistical reminder », *BMJ* 311:619-620. Formule : « upper limit of 95% confidence interval = maximum risk = 3/n (for n > 30) ». Conseil : « Doctors and surgeons should keep this simple rule in mind when complication rates of zero are reported in the literature. » — [PMC2550668](https://pmc.ncbi.nlm.nih.gov/articles/PMC2550668)
- **Tuyl, Gerlach & Mengersen (2009)**, « The Rule of Three, its Variants and Extensions », *Int Stat Rev* 77(2):266-275. La règle découle de la borne exacte unilatérale de Clopper-Pearson ; les autres méthodes fréquentistes courantes ne la reproduisent pas. Parmi les a priori non informatifs usuels, seuls Bayes-Laplace (uniforme) et Zellner s'y conforment. Appliquer la règle au nombre d'événements d'une future expérience de même taille est un contresens : c'est une autre quantité, qui correspond à environ 87,5-93,75 % de confiance. Les auteurs proposent une « Rule of Four » et défendent l'a priori de Bayes-Laplace. — [IDEAS/RePEc](https://ideas.repec.org/a/bla/istatr/v77y2009i2p266-275.html)
- **Tuyl, Gerlach & Mengersen (2008)**, « A Comparison of Bayes-Laplace, Jeffreys, and Other Priors: The Case of Zero Events », *Am Stat* 62:40-44. Je n'ai que la notice ; le texte n'a pas été lu. — [IDEAS/RePEc](https://ideas.repec.org/a/bes/amstat/v62y2008mfebruaryp40-44.html)
- **Winkler, Smith & Fryback (2002)** : les a priori « non informatifs » se contredisent à zéro. Avec des a priori Beta(a, a), 0 < a ≤ 1, et n = 167, le fractile 0,95 a posteriori va de « arbitrarily close to zero » à 0,018 (a = 1). La borne haute monte à 0,133 pour n = 20 et à 0,238 pour n = 10. Leur conclusion : « When different schools of thought on what is an appropriate noninformative prior lead to very different results, it is clear that the analysis cannot be viewed as objective. » — [Winkler et al. 2002](https://jimsmith.host.dartmouth.edu/wp-content/uploads/2022/04/The_Role_of_Informative_Priors_in_Zero_Numerator_Problems.pdf)
- Winkler et al., a priori informatif. On prend une moyenne a priori de 0,0015 (le risque de l'ancien produit) et une probabilité de 95 % que p < 0,75 %. Cela donne Beta(0,042 ; 27,96), soit l'équivalent de 0,042 réaction pour 28 patients. Avec 0/167, l'a posteriori est Beta(0,042 ; 194,96) : moyenne 0,022 %, fractile 0,95 de 0,11 %. Avec la même moyenne a priori et une force a priori (a+b) entre 1 et 5 000, le fractile 0,95 ne dépasse jamais 0,4 %, contre 1,8 % pour la règle de trois. — [Winkler et al. 2002](https://jimsmith.host.dartmouth.edu/wp-content/uploads/2022/04/The_Role_of_Informative_Priors_in_Zero_Numerator_Problems.pdf)
- Winkler et al., la prudence qui se retourne (« conservatism backfires »). Il s'agit d'un dépistage néonatal : premier test positif après environ 13 000 vrais négatifs. La règle de trois fixe le taux de faux positifs à 3/13 000 = 0,000231, ce qui donne P(maladie | +) = 0,018. Avec un a priori Beta(1, 999), l'a posteriori Beta(1, 13 999) a une moyenne de 1/14 000 et P(maladie | +) = 0,053, presque trois fois plus. Le maximum de vraisemblance (0) donne une probabilité de 1. Leur message : « It is better to be candid than conservative, using all of the information available in forming the prior and considering the uncertainty represented by the full posterior distribution. » — [Winkler et al. 2002](https://jimsmith.host.dartmouth.edu/wp-content/uploads/2022/04/The_Role_of_Informative_Priors_in_Zero_Numerator_Problems.pdf)
- **Littlewood & Strigini (1993)**, *CACM* 36(11):69-80. Avec un a priori d'« ignorance complète », la fiabilité a posteriori après t₀ heures sans défaillance est R(t) = t₀/(t+t₀). Autrement dit, « there is a 50:50 chance that we shall wait a further period exceeding t₀ until the first failure ». Pour une médiane a posteriori de 10⁹ heures avant défaillance sans croyance a priori, « we would need to see 10⁹ hours of failure-free working ». Bayésiens et classiques concordent « within an order of magnitude » sauf a priori très forts. Ils rappellent aussi que E(p | n succès sur n) = (n+1)/(n+2). — [City Research Online](https://openaccess.city.ac.uk/id/eprint/1251/)
- Usage en qualité : 300 échantillons sans défaut permettent d'affirmer à 95 % qu'un procédé est fiable à au moins 99 % — [Quality Digest, « Rules of three and five »](https://www.qualitydigest.com/inside/statistics-column/rules-three-and-five-082317.html). Le théorème « success-run » donne exactement 299 (ln 0,05 / ln 0,99 = 298,07, arrondi au-dessus) — [Durivage, Pharmaceutical Online 2016](https://www.pharmaceuticalonline.com/doc/how-to-establish-sample-sizes-for-process-validation-using-the-success-run-theorem-0001).

### Inferences
- **Inversion pratique.** Pour qu'un zéro démontre « taux ≤ b » à la confiance C, il faut n ≥ −ln(1−C)/b, c'est-à-dire λ_b = n·b ≥ 3,0 à 95 %, 2,3 à 90 % et 4,6 à 99 %. Nombre minimal d'écritures sans erreur pour un Clopper-Pearson unilatéral à 95 % (calcul) : n = 598 pour b = 1/200, n = 5 990 pour b = 1/2 000, n = 59 914 pour b = 1/20 000, soit λ_b ≈ 2,99-3,00 dans les trois cas. Dans l'exemple de Hanley & Lippman-Hand, 0/167 laisse plausible un risque 12 fois supérieur à celui de l'ancien produit. Il faudrait environ 2 000 patients sans réaction pour montrer « ≤ 1,5 ‰ » à 95 %.
- **Ce qu'un zéro montre** : une borne supérieure d'environ 3/n à 95 %. Elle ne devient pertinente que comparée à la barre, via λ_b.
- **Ce qu'un zéro ne montre pas** :
  - que le taux est nul (l'estimation 0 est en bord d'espace) ;
  - que le taux est sous b quand λ_b est petit. C'est exactement la pathologie « 0 ≤ barre faute de données » : la règle « estimation MV ≤ b » revient à n'exiger aucune information minimale ;
  - combien d'erreurs surviendront dans une prochaine série (autre quantité, Tuyl 2009) ;
  - rien d'indépendant de l'a priori quand on passe au bayésien (Winkler 2002).
- La leçon de Winkler et al. s'applique au projet. Une borne « prudente » n'est pas prudente si la décision dépend du taux à travers une autre fonction. La règle de décision doit être définie sur la distribution entière, et le niveau d'exigence doit être choisi explicitement, pas hérité d'un estimateur.

### Gaps
- Je n'ai pas eu accès au texte intégral de Hanley & Lippman-Hand (1983, payant) ni à celui de Jovanovic & Levy (1997). Le contenu bayésien de J&L vient de Winkler et al. Je n'ai pas vérifié si Hanley & Lippman-Hand donnent aussi une table ou une version à 99 % (4,6/n).
- Le contenu de Tuyl et al. (2008) n'a pas été lu. Leur position (préférer Bayes-Laplace à Jeffreys quand le compte est nul) se déduit seulement du résumé de 2009.
- Je n'ai pas lu les tables ni les exemples chiffrés d'Eypasch et al., seulement le résumé.

---

## 2. Estimateurs pour taux rares à x = 0 ou x petit, et la règle « médiane a posteriori ≤ seuil »

### Takeaway
À x = 0, tous les estimateurs « rétrécis » usuels donnent une valeur non nulle qui décroît en k/n. Le coefficient k vaut environ :

| Estimateur | k |
|---|---|
| médiane de Jeffreys | 0,23 |
| moyenne de Jeffreys (= correction « +½ ») | 0,5 |
| médiane sous a priori uniforme | 0,69 |
| moyenne de Laplace | ≈ 1 |
| centre de Wilson | 1,92 |
| centre d'Agresti-Coull | 2 |

« Estimation ≤ b » avec zéro erreur équivaut donc à « n·b ≥ k ». C'est une règle d'information minimale implicite, dont le seuil dépend du choix d'estimateur et non d'un choix de risque. La règle « médiane a posteriori ≤ b » revient à exiger P(p ≤ b | données) ≥ ½. C'est un standard de preuve à pile ou face. Avec l'a priori de Jeffreys, elle accepte une strate sans erreur dès que n·b ≥ 0,23 : elle reproduit presque la pathologie observée, car elle ne rejette de façon fiable que des agents à environ 10 fois la barre.

### Cited Findings
- **Brown, Cai & DasGupta (2001)**, « Interval Estimation for a Binomial Proportion », *Statistical Science* 16(2):101-133, DOI 10.1214/ss/1009213286. Pour n ≤ 40 : « we recommend that either the Wilson or the Jeffreys prior interval should be used. They are very similar, and either may be used depending on taste ». Pour n plus grand, ils favorisent Agresti-Coull (n > 40 : Wilson, Jeffreys et Agresti-Coull « are all very similar »). L'intervalle de Wald a une couverture « erratic » et les règles des manuels sont « defective ». Ces passages viennent du texte de l'article, lu via des extraits de recherche. — [Project Euclid](https://projecteuclid.org/euclid.ss/1009213286) ; résumé par le [NIST Dataplot](https://itl.nist.gov/div898/software/dataplot/refman1/auxillar/propconf.htm)
- Formules NIST (Dataplot) :
  - Jeffreys : LCL = quantile α/2 et UCL = quantile 1−α/2 d'une Beta(x+0,5 ; n−x+0,5) ;
  - Wald ajusté (Agresti-Coull) : X̃ = X + z²/2, ñ = n + z², p̃ = X̃/ñ ;
  - Wilson : forme score ;
  - exact (Clopper-Pearson) : par inversion de la fonction de répartition binomiale.
  Selon NIST, BCD recommandent Wilson et Jeffreys pour n ≤ 40. — [NIST Dataplot](https://itl.nist.gov/div898/software/dataplot/refman1/auxillar/propconf.htm)
- **Mid-p** (documentation DescTools::BinomCI). La méthode « accumulate[s] tail areas » pour réduire le conservatisme de Clopper-Pearson. La borne haute p_u résout ½·f(x; n, p_u) + F(x−1; n, p_u) = α/2 ; à x = 0, la borne basse vaut 0. Le « modified Jeffreys » de BCD (2001) modifie les bornes pour x = 0, 1, n−1, n. Wilson, Wilson modifié et Agresti-Coull peuvent rendre une estimation ponctuelle « slightly closer to 0.5 » (p̃) au lieu de x/n. Clopper-Pearson y est qualifié de « very conservative », Wald d'inadéquat pour petit n ou p proche de 0 ou de 1. — [DescTools BinomCI](https://rdrr.io/cran/DescTools/man/BinomCI.html)
- Position NCHS : « The Clopper-Pearson CI is known to perform well for estimated proportions with few events in the numerator ». Sa couverture est « generally conservative ». Le Wald donne des bornes basses négatives et une sous-couverture aux petites proportions. — [NCHS, Parker et al. 2017, Vital Health Stat 2(175)](https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf)
- Conjugaison bêta-binomiale. Avec un a priori Beta(a, b) et r événements sur n, l'a posteriori est Beta(a+r, b+n−r) ; a priori valent « a » événements sur « a+b » essais. Beta(0,5 ; 0,5) est « a Jeffreys prior and a reference prior ». Beta(0, 0) (improper, Haldane) et Beta(1, 1) sont aussi d'usage courant. Ces a priori non informatifs « lead to very different results in zero-numerator problems ». — [Winkler et al. 2002](https://jimsmith.host.dartmouth.edu/wp-content/uploads/2022/04/The_Role_of_Informative_Priors_in_Zero_Numerator_Problems.pdf)
- La médiane a posteriori sert déjà de cible de sûreté de fonctionnement. Littlewood & Strigini raisonnent sur la « posterior median time to failure » et montrent que, sous ignorance, une médiane de T exige T heures sans défaillance. — [Littlewood & Strigini 1993](https://openaccess.city.ac.uk/id/eprint/1251/)
- Parmi les a priori non informatifs, seuls Bayes-Laplace et Zellner reproduisent la règle de trois (Tuyl et al. 2009). — [IDEAS/RePEc](https://ideas.repec.org/a/bla/istatr/v77y2009i2p266-275.html)
- **Cadre réglementaire bayésien.** Le projet de guide FDA de janvier 2026 (« Use of Bayesian Methodology in Clinical Trials of Drug and Biological Products », non contraignant) admet des critères de succès de forme Pr(effet > seuil) ≥ c. Calibrer sur une erreur de type I unilatérale de 0,025 donne, dans les cas simples avec a priori non informatif, un seuil Pr > 0,975. Avec emprunt de données externes, la calibration sur le type I « may not be applicable or appropriate ». Je n'ai pas lu le texte FDA, seulement des commentaires secondaires. — [Berry Consultants](https://www.berryconsultants.com/resource/guide-to-the-draft-fda-bayesian-guidance-2026) ; [arXiv 2601.14701](https://arxiv.org/html/2601.14701)

### Inferences
- **Estimations ponctuelles à x = 0** (formules ; les valeurs numériques sont des calculs) :
  - maximum de vraisemblance : 0 ;
  - Jeffreys, moyenne = correction de Haldane-Anscombe : 0,5/(n+1) ;
  - Laplace, moyenne sous uniforme : 1/(n+2) ;
  - médiane sous uniforme : 1 − 0,5^(1/(n+1)) ≈ 0,693/(n+1) ;
  - Wilson, centre (z = 1,96) : 1,92/(n+3,84) ;
  - Agresti-Coull, centre : 2/(n+4) ;
  - **Jeffreys, médiane : ≈ 0,2275/n.** La limite est la médiane d'une Gamma(½, 1), soit 0,22747. Valeurs exactes : n·médiane = 0,2194 (n = 10), 0,2266 (n = 100), 0,2274 (n = 1 000), 0,2275 (n = 10⁴).
  La médiane de Jeffreys est environ 2,2 fois plus basse que sa moyenne et 3 fois plus basse que la médiane sous uniforme.
- **Seuil implicite λ_b à x = 0 : nombre minimal d'erreurs attendues à la barre pour qu'un zéro suffise** (calcul, identique pour b = 1/200, 1/2 000 et 1/20 000) :

  | Règle | λ_b minimal |
  |---|---|
  | médiane de Jeffreys | 0,228 |
  | moyenne de Jeffreys / +½ | 0,50 |
  | médiane uniforme | 0,693 |
  | Jeffreys, P(p ≤ b) ≥ 0,8 | 0,821 |
  | Jeffreys, P ≥ 0,9 | 1,353 |
  | centre de Wilson | 1,92 |
  | Jeffreys, borne haute à 95 % | 1,92 |
  | centre d'Agresti-Coull | 2,0 |
  | mid-p unilatéral 95 % | 2,303 |
  | Clopper-Pearson unilatéral 95 % = règle de trois | 2,996 |
  | Clopper-Pearson bilatéral 95 % (quantile 97,5 %) | 3,689 |
  | Wilson, borne haute bilatérale 95 % | 3,84 |

  Pour b = 1/20 000, cela fait n ≥ 4 550 écritures sans erreur avec la médiane de Jeffreys, contre n ≥ 59 914 avec Clopper-Pearson.
- **Courbes OC** (calcul, b = 1/2 000, binomiale exacte, sans grappes). On calcule P(strate déclarée ≤ b) selon λ_b et f = vrai taux / b.

  | λ_b | Règle | f = 0 | 0,1 | 0,5 | 1 | 2 | 10 |
  |---|---|---|---|---|---|---|---|
  | 0,5 | Clopper-Pearson 95 % | 0 | 0 | 0 | 0 | 0 | 0 |
  | 0,5 | médiane de Jeffreys | 1,00 | 0,95 | 0,78 | 0,61 | 0,37 | 0,01 |
  | 1 | Clopper-Pearson 95 % | 0 | 0 | 0 | 0 | 0 | 0 |
  | 1 | médiane de Jeffreys | 1,00 | 0,90 | 0,61 | 0,37 | 0,14 | 0,00 |
  | 1 | Jeffreys 80 % | 1,00 | 0,90 | 0,61 | 0,37 | 0,14 | 0,00 |
  | 3 | Clopper-Pearson 95 % | 1,00 | 0,74 | 0,22 | 0,05 | 0,00 | 0,00 |
  | 3 | médiane de Jeffreys | 1,00 | 1,00 | 0,81 | 0,42 | 0,06 | 0,00 |
  | 3 | Jeffreys 80 % | 1,00 | 0,96 | 0,56 | 0,20 | 0,02 | 0,00 |
  | 10 | Clopper-Pearson 95 % | 1,00 | 1,00 | 0,44 | 0,03 | 0,00 | 0,00 |
  | 10 | médiane de Jeffreys | 1,00 | 1,00 | 0,97 | 0,46 | 0,00 | 0,00 |
  | 10 | Jeffreys 80 % | 1,00 | 1,00 | 0,87 | 0,22 | 0,00 | 0,00 |

  Lecture. La règle de la médiane est une règle d'**indifférence à la barre** : environ 40-50 % d'acceptation à f = 1 dès que λ_b ≥ 2. Clopper-Pearson est une règle de **protection du « client »** : au plus 5 % d'acceptation à f = 1, au prix d'un rejet fréquent des bons agents tant que λ_b est petit. La règle à 80 % est un compromis réel.
- La médiane comme règle de décision est un résultat standard de théorie de la décision (Berger 1985 ; non revérifié ici). « Médiane a posteriori ≤ b » équivaut à P(p ≤ b | données) ≥ ½. C'est la règle de Bayes pour une perte 0-1 symétrique entre « p ≤ b » et « p > b ». Avec des pertes asymétriques (L pour déléguer à tort, K pour refuser à tort), le seuil devient P ≥ L/(L+K). La règle est donc reconnue, mais elle suppose qu'une délégation à tort coûte autant qu'un refus à tort. C'est peu défendable pour les actions à fort enjeu, où les régulateurs exigent plutôt P ≥ 0,975 (cadre FDA ci-dessus).
- Choix de l'a priori pour une règle bayésienne à zéro. Jeffreys rend un zéro environ 3 fois « plus convaincant » qu'avec Bayes-Laplace pour la médiane (0,23 contre 0,69) et environ 1,56 fois pour le 95 % (1,92 contre 3,0). Winkler et Tuyl montrent que ce choix n'est pas neutre. Il faut le préenregistrer, avec une analyse de sensibilité entre Jeffreys et l'uniforme.

### Gaps
- Je n'ai pas lu le texte intégral de BCD 2001 (PDF inaccessible). Les bornes exactes du « modified Jeffreys » et du « modified Wilson » aux points x = 0, 1 ne sont pas vérifiées.
- Je n'ai pas lu Berry & Armitage (1995) sur le mid-p, ni Agresti & Coull (1998).
- Je n'ai trouvé aucune source qui prescrive explicitement « médiane a posteriori ≤ seuil » comme règle d'acceptation réglementaire ou industrielle. L'usage le plus proche est la médiane du temps avant défaillance chez Littlewood & Strigini.
- Je n'ai pas vérifié l'a priori « neutre » Beta(⅓, ⅓) de Kerman (2011), qui vise une médiane a posteriori ≈ x/n.

---

## 3. Conditions d'« information minimale » ou d'observabilité avant qu'une strate compte

### Takeaway
Les institutions appliquent bien des conditions explicites d'information minimale, de deux familles :
- **un minimum d'événements observés ou de précision à l'estimation** : statistiques de décès, ≥ 20 décès (soit une erreur-type relative < 23 %) jusqu'en 2022, puis ≥ 10 décès et une largeur relative de l'IC 95 % ≤ 160 % depuis 2023 ; GRADE, taille d'information optimale d'environ 300 événements ;
- **un dénominateur effectif minimal et des critères d'intervalle exact** : NCHS proportions, n_eff ≥ 30, largeurs Clopper-Pearson / Korn-Graubard, estimations à 0 événement signalées pour revue.

Pour une décision par rapport à un seuil avec des comptes possiblement nuls, la bonne quantité est **l'espérance du nombre d'erreurs à la barre, λ_b = n_eff·b**. C'est exactement ce que tabulent les plans de démonstration de fiabilité : à zéro défaillance, 0,69 à 50 %, 1,61 à 80 %, 2,30 à 90 %, 3,00 à 95 %.

### Cited Findings
- **NCHS Data Presentation Standards for Proportions** (Parker et al. 2017, Vital Health Stat 2(175)) :
  - « Estimated proportions should be based on a minimum denominator sample size and effective denominator sample size (when applicable) of 30 » ; en dessous, l'estimation est supprimée ;
  - n_e = n / effet de plan ;
  - IC 95 % bilatéral de Clopper-Pearson (Korn-Graubard pour les enquêtes complexes). Largeur absolue ≤ 0,05 : présenter si le nombre d'événements est > 0 et si df ≥ 8. Largeur ≥ 0,30 : supprimer. Entre 0,05 et 0,30 : supprimer si la largeur relative dépasse 130 % ;
  - « If the number of numerator events is 0 … the estimate should be flagged for statistical review » ;
  - à 0 événement, la variance estimée vaut 0 et « the effective sample size will be undefined » ; on utilise alors n pour le critère de taille et pour l'IC. Si n_eff > n, on utilise n ;
  - « there is no minimum number of events (i.e., numerator size). For the calculation of the Clopper-Pearson CI, a minimum numerator is not needed » ;
  - un zéro « can provide important information (e.g., in the context of rare health outcomes) » ;
  - l'erreur-type relative est rejetée car « when dividing the SE by very small proportions, the RSE can be too conservative » ;
  - « Rates calculated from vital statistics will continue to use the criterion of requiring 20 or more events » ;
  - regrouper des sous-groupes ou agréger des années est recommandé.

  — [NCHS sr02_175](https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf)
- **Taux de mortalité NCHS** (Kochanek et al., « Implementation of New Data Presentation Standards for Rates and Counts for Mortality », révisé le 10/02/2026) :
  - de 1989 à 2022, astérisque à la place d'un taux fondé sur moins de 20 décès, « the equivalent of an RSE of 23% or more ». La limite de 20 est « a convenient, if somewhat arbitrary, benchmark » ;
  - depuis les données 2023, astérisque sous 10 décès (aligné sur le seuil de confidentialité), et à partir de 10 décès il faut une largeur relative de l'IC 95 % ≤ 160 % ;
  - pour moins de 100 décès, IC gamma : L = GAMMAINV(0,025 ; D ; 1), U = GAMMAINV(0,975 ; D+1 ; 1).

  — [CDC WONDER, presentation standards mortality](https://wonder.cdc.gov/controller/pdf/presentation-standards-mortality-2024.pdf)
- **GRADE 6, imprécision** (Guyatt et al., *J Clin Epidemiol* 2011;64:1283-1293) :
  - la taille d'information optimale (OIS) est le nombre de patients qu'exigerait « a conventional sample size calculation for a single adequately powered trial » ;
  - « Power is, however, more closely related to number of events than to sample size » ;
  - avec un taux d'événements témoin de 0,2 et une réduction relative du risque de 25 %, l'OIS vaut environ 2 000 patients, soit environ 325 événements ;
  - Table 1 : « 100 or less » événements « Will almost never meet threshold whatever control event rate » ; 400 événements ou plus avec une réduction relative de 30 % : « Will meet threshold for any control group risks » ;
  - exemple de fragilité : un essai arrêté tôt avec 20 événements au total. Déplacer 5 événements fait perdre la significativité, et conclure à partir de 20 événements « violates common sense ».

  — [Guyatt et al. 2011 (copie SIPTA)](https://school16.sipta.org/slides/04-thursday/01-ullrika/papers/Guyattetal_grade_imprecision.pdf)
- Précurseur GRADE : un critère simplifié de précision adéquate est « the total number of events is greater than 300 ». — [Guyatt, Kunz, Oxman, Cochrane Colloquium 2007](https://abstracts.cochrane.org/2007-sao-paulo/arriving-bottom-line-evidence-quality-precision-estimate)
- **Démonstration de fiabilité (NIST e-Handbook 8.3.1.1).** Facteur = 0,5·χ²(α ; 2(r+1)), et la durée du test vaut objectif de MTBF × facteur.

  | r | 50 % | 60 % | 75 % | 80 % | 90 % | 95 % |
  |---|---|---|---|---|---|---|
  | 0 | 0,693 | 0,916 | 1,39 | 1,61 | 2,30 | 3,00 |
  | 1 | 1,68 | 2,02 | 2,69 | 2,99 | 3,89 | 4,74 |
  | 2 | 2,67 | 3,11 | 3,92 | 4,28 | 5,32 | 6,30 |

  Les tests à zéro défaillance « have a large chance of failing a marginally acceptable piece of equipment ». Plus on autorise de défaillances, plus le test est long, mais moins un bon équipement risque d'être rejeté. On peut cumuler les unités : « count all the fails from all the tools and the sum of the test hours ». — [NIST 8.3.1.1](https://www.itl.nist.gov/div898/handbook/apr/section3/apr311.htm)

### Inferences
- **Deux familles à ne pas confondre.**
  - Les règles « minimum d'événements observés » (≥ 10, ≥ 20, ≈ 300) visent la **précision d'un taux rapporté**. Appliquées à une décision de délégabilité, elles pénalisent systématiquement les bons agents, qui produisent peu d'erreurs : une strate parfaite n'atteindrait jamais 20 erreurs.
  - La condition pertinente porte sur l'information **évaluée à la barre** : λ_b = n_eff·b. Elle est connue avant de voir le résultat et ne dépend pas de x.
- **Justification statistique.** Pour un compte de Poisson d'espérance λ, l'information de Fisher sur log λ vaut λ et l'erreur-type de log λ̂ vaut environ 1/√λ. C'est la logique NCHS « 20 décès ↔ RSE ≈ 23 % » : 1/√20 = 22,4 %. Exiger λ_b ≥ c, c'est donc exiger une précision relative minimale de l'ordre de 1/√c **au voisinage de la barre**. Cela évite la circularité des critères d'erreur-type relative, indéfinis à x = 0, défaut que NCHS lui-même relève.
- **Valeurs de c justifiées par la table de démonstration.** À zéro erreur, c = −ln(1−C) :

  | C | c |
  |---|---|
  | 50 % | 0,69 |
  | 63 % | 1 |
  | 80 % | 1,61 |
  | 90 % | 2,30 |
  | 95 % | 3,00 |

  c est donc un niveau de confiance déguisé. Un c de 0,23 (ce qu'implique la médiane de Jeffreys) correspond à une confiance d'environ 20 % (1 − e^−0,23 = 0,21) à zéro erreur.
- **Choisir c par conception à deux points**, comme en échantillonnage d'acceptation (calcul, Poisson). On fixe un « bon » niveau f₁·b, à accepter avec une probabilité ≥ 1−α, et un « mauvais » niveau f₂·b, à accepter avec une probabilité ≤ β. On en tire le nombre d'erreurs tolérées c et le λ_b requis. Avec α = 5 % et β = 10 % :

  | Bon | Mauvais | Erreurs tolérées | λ_b requis | P(accepter le bon) | P(accepter le mauvais) |
  |---|---|---|---|---|---|
  | 0,1 × b | 1 × b | ≤ 2 | ≈ 5,3 | 0,983 | 0,10 |
  | 0,1 × b | 2 × b | ≤ 1 | ≈ 1,95 | 0,983 | 0,10 |
  | 0,1 × b | 10 × b | 0 | ≈ 0,23 | 0,977 | 0,10 |

  La dernière ligne est, à peu près, ce que fait la médiane de Jeffreys. Elle ne protège que contre les agents environ 10 fois au-dessus de la barre, ce qui est cohérent avec la pathologie « délégable de 0 à 10 fois la barre ».
- **Traitement préenregistrable d'une strate sous le seuil d'information** (pas de source qui l'énonce tel quel ; c'est une synthèse) :
  - la déclarer « non informative » ;
  - elle ne peut pas rendre une configuration délégable, mais elle ne compte pas non plus contre elle ;
  - on rapporte le nombre de telles strates ;
  - option NCHS : agréger des strates voisines (même type et même modèle sur plusieurs environnements) avant de juger.
- **Transposition de la structure NCHS** : un plancher sur n_eff, un intervalle exact, une revue des zéros, un plafond n_eff ≤ n. Les seuils numériques NCHS (30, 0,05, 130 %) sont conçus pour des prévalences de l'ordre du pourcent et ne se transposent pas à des barres de 1/20 000.

### Gaps
- Je n'ai trouvé aucune source qui formule littéralement « espérance du nombre d'événements au seuil ≥ c » comme condition préalable à une comparaison. L'équivalent exact existe dans les tables de démonstration (NIST) et en échantillonnage d'acceptation (n·LTPD), mais il est présenté comme une taille d'essai, pas comme une condition d'admissibilité.
- Je n'ai pas vérifié l'origine des règles « np ≥ 5 / n(1−p) ≥ 5 » pour l'approximation normale (Cochran) ; BCD les jugent défectueuses.
- GRADE 2011 ne contient pas, dans le passage lu, la formule « 300 événements », qui figure dans le résumé de 2007. Les mises à jour GRADE 2021-2022 (guidances 33 et 34) n'ont pas été lues, seulement des extraits de recherche.

---

## 4. Échantillonnage d'acceptation et démonstration de fiabilité : courbes OC, plans c = 0, choix de n et c

### Takeaway
Un plan simple (n, c) se dimensionne à partir de deux points de la courbe OC :
- le niveau de qualité acceptable (AQL), avec le risque fournisseur α ;
- le niveau de défectuosité inacceptable pour le client (LTPD), avec le risque client β.

Les plans à zéro acceptation (c = 0) maximisent la protection du client par unité inspectée. Leur rapport de discrimination est en revanche énorme (LTPD/AQL ≈ 45 pour α = 5 % et β = 10 %) : ils refusent beaucoup de lots « bons mais pas parfaits ». Tolérer c ≥ 1 raidit la courbe au prix d'un n plus grand. La démonstration de fiabilité (théorème success-run, tests à zéro défaillance) est exactement la même mathématique.

### Cited Findings
- **Définitions NIST (e-Handbook 6.2.2).**
  - AQL : « a percent defective that is the base line requirement for the quality of the producer's product ».
  - LTPD : « a designated high defect level that would be unacceptable to the consumer ».
  - Erreur de type I (risque fournisseur) : « the probability, for a given (n,c) sampling plan, of rejecting a lot that has a defect level equal to the AQL ».
  - Erreur de type II (risque client) : « the probability … of accepting a lot with a defect level equal to the LTPD ».
  - Courbe OC : probabilité d'acceptation en fonction de la fraction défectueuse.
  - AOQ et AOQL : niveau de défaut à long terme, avec inspection à 100 % des lots rejetés.
  - Fourchette de risques donnée : 0,2 à 0,01.
  - Types de plans : simple, double, multiple, **séquentiel** (décision après chaque unité : accepter, rejeter ou continuer) et skip-lot.

  — [NIST 6.2.2](https://www.itl.nist.gov/div898/handbook/pmc/section2/pmc22.htm)
- Un plan simple est « specified by the pair of numbers (n,c) » : on rejette s'il y a plus de c défectueux. Deux façons de choisir le plan : des tables (MIL-STD-105D) centrées sur l'AQL ou la LTPD, ou deux points imposés sur la courbe OC, qui déterminent (n, c). — [NIST 6.2.3](https://www.itl.nist.gov/div898/handbook/pmc/section2/pmc23.htm)
- **Zéro défaillance en fiabilité** (NIST 8.3.1.1). La table des facteurs figure à la section 3. Exemple : pour un objectif de MTBF de 200 h à 90 %, il faut 460 h avec r = 0, 1 336 h avec r = 3 et 1 598 h avec r = 4. « The more fails allowed, the longer the test required », mais un bon équipement est moins souvent rejeté. Les tests à zéro défaillance ont « a large chance of failing a marginally acceptable piece of equipment ». — [NIST 8.3.1.1](https://www.itl.nist.gov/div898/handbook/apr/section3/apr311.htm)
- **Théorème success-run** : n = ln(1−C)/ln(R). Pour C = 95 % et R = 99 %, n = 299 (298,07 arrondi au-dessus), et « 298 parts would not substantiate » l'affirmation. Une seule défaillance invalide un plan à zéro défaillance ; l'hypothèse est celle d'essais indépendants et identiques. — [Durivage, Pharmaceutical Online 2016](https://www.pharmaceuticalonline.com/doc/how-to-establish-sample-sizes-for-process-validation-using-the-success-run-theorem-0001)
- **Plans c = 0 de Squeglia** (*Zero Acceptance Number Sampling Plans*, ASQ Quality Press, 6e éd. 2023). Ils ont été conçus pour offrir une protection du client égale ou supérieure à celle de MIL-STD-105E, avec moins d'inspection ; la 6e édition reprend la table c = 0 d'origine. — [ASQ Quality Press](https://asq.org/quality-press/display-item?item=H1607)
- Critique praticienne (Levinson) : « we can not design a set of consistent c=0 sampling plans with the producer's risk in mind ». Les plans indexés sur l'AQL existent pour « plier » la courbe OC au point AQL. Le c = 0 se justifie quand le fournisseur est « extremely confident » de sa qualité. C'est un avis de praticien. — [Quality Digest](https://www.qualitydigest.com/node/31374/)
- **Historique des normes.**
  - Le DoD a annulé MIL-STD-105E en 1995 au profit d'ANSI/ASQ Z1.4 (et MIL-STD-414 en 1999 au profit de Z1.9) — [ASTM](https://www.astm.org/news/preservation-of-the-military-standards-for-acceptance-sampling).
  - MIL-STD-1916 privilégie l'amélioration des procédés, avec des plans attributs « zero accept, one reject » utilisables à la place de MIL-STD-105 / Z1.4. Ce point vient d'un extrait de recherche du manuel MIL-HDBK-1916 : [copie Scribd](https://www.scribd.com/doc/94367045/hdbk1916). Il existe une analyse des AQL et RQL des plans de MIL-STD-1916 : [EconBiz](https://www.econbiz.de/Record/the-aql-and-rql-of-the-attributes-sampling-plans-in-mil-std-1916/10010993048).

### Inferences
- **Courbe OC d'un plan c = 0** : P(accepter) = (1−p)^n ≈ e^(−np).
- **Rapports de discrimination p₂/p₁ pour α = 5 % et β = 10 %** (calcul, Poisson ; ce sont les valeurs classiques de la table de Cameron, non consultée ici) :

  | c | n·p₁ | n·p₂ | p₂/p₁ |
  |---|---|---|---|
  | 0 | 0,051 | 2,303 | 44,9 |
  | 1 | 0,355 | 3,890 | 10,95 |
  | 2 | 0,818 | 5,322 | 6,51 |
  | 3 | 1,366 | 6,681 | 4,89 |
  | 4 | 1,970 | 7,994 | 4,06 |
  | 5 | 2,613 | 9,275 | 3,55 |

  Distinguer un agent à 0,1 × b d'un agent à 1 × b (rapport 10) avec α = 5 % et β = 10 % est impossible à c = 0 ou c = 1. Il faut c = 2 et λ_b ≈ 5,3.
- **Correspondance avec le problème des agents.**
  - La barre joue le rôle de la LTPD : le risque client est la probabilité de déclarer délégable un agent exactement à la barre.
  - Un « bon agent » (par exemple 0,1 × b) joue le rôle de l'AQL : le risque fournisseur est la probabilité de refuser un bon agent.
  - La règle « borne Clopper-Pearson 95 % ≤ b » est un plan à c variable dont le risque client est ≤ 5 % à la LTPD = b. À x = 0, elle équivaut à un plan c = 0 avec n·b ≥ 3.
  - Un agent parfait n'échoue que si aucune strate n'atteint λ_b ≥ 3. Un agent à f·b passe un plan c = 0 avec λ_b = 3 avec une probabilité d'environ e^(−3f) : 0,74 pour f = 0,1 et 0,22 pour f = 0,5. Au-delà, Clopper-Pearson tolère des erreurs (x ≤ 1 à λ_b = 5, x ≤ 4 à λ_b = 10).
  - Les taux observés en simulation (92-93 % pour les parfaits, 39-65 % pour 0,1 × b) sont donc la signature attendue d'une protection client stricte avec λ_b proche du minimum. Ils ne trahissent pas un défaut d'implémentation.
- **Leviers classiques quand l'information manque** :
  - davantage de données, c'est-à-dire un λ_b plus grand ;
  - un risque client moins strict à la barre, assumé explicitement ;
  - un « mauvais » niveau défini plus haut (2 × b plutôt que 1 × b) ;
  - un plan séquentiel ou double, qui crée un troisième verdict, « indéterminé / continuer », au lieu de forcer oui ou non ;
  - de l'information a priori (section 5).
- Le cumul des unités (NIST) justifie qu'on additionne les écritures de plusieurs tâches, mais seulement sous indépendance. Sinon, il faut passer par n_eff (section 6).

### Gaps
- Je n'ai pas vérifié en session les tables de Dodge-Romig (LTPD avec β = 0,10, AOQL), ni les règles de basculement normal / renforcé / réduit d'ISO 2859-1 et d'ANSI/ASQ Z1.4.
- Je n'ai pas consulté la table de Cameron (1952) ; les rapports ont été recalculés.
- Le contenu exact des tables et des courbes OC de Squeglia n'a pas été lu.
- Statut actuel de MIL-STD-1916 : je n'ai qu'un extrait secondaire.

---

## 5. RAND « Driving to Safety » (et Littlewood & Strigini) : démontrer des taux faibles avec peu de données

### Takeaway
RAND applique la règle de trois à la barre. Il faudrait 275 millions de miles sans accident mortel pour démontrer, à 95 %, un taux de 1,09 décès pour 100 millions de miles, soit environ 12,5 ans pour 100 véhicules roulant 24 h/24 à 25 mph. Plus généralement, il faudrait de centaines de millions à centaines de milliards de miles : on « cannot drive their way to safety ». La démonstration par le seul usage doit être complétée par d'autres preuves, et la réglementation doit évoluer avec la technologie. Littlewood & Strigini font le même constat pour le logiciel : un écart de plusieurs ordres de grandeur, comblable seulement par des a priori forts et justifiés.

### Cited Findings
- Kalra & Paddock (2016), *Driving to Safety: How Many Miles of Driving Would It Take to Demonstrate Autonomous Vehicle Reliability?*, RAND RR-1478 — [RAND](https://www.rand.org/pubs/research_reports/RR1478.html). Version revue : *Transportation Research Part A* 94:182-193, DOI 10.1016/j.tra.2016.09.010 — [EconPapers](https://econpapers.repec.org/RePEc:eee:transa:v:94:y:2016:i:c:p:182-193).
- Citation de la p. 3 : « To demonstrate that fully autonomous vehicles have a fatality rate of 1.09 fatalities per 100 million miles (R=99.9999989%) with a C=95% confidence level, the vehicles would have to be driven 275 million failure-free miles. With a fleet of 100 autonomous vehicles being test-driven 24 hours a day, 365 days a year at an average speed of 25 miles per hour, this would take about 12.5 years. » Source secondaire qui cite le rapport : [liste SystemSafety, 22/03/2018](https://lists.techfak.uni-bielefeld.de/pipermail/systemsafety/2018-March/003798.html).
- Communiqué RAND :
  - « hundreds of millions of miles and, under some scenarios, hundreds of billions of miles » ;
  - avec les flottes existantes, « tens and even hundreds of years » ;
  - au moment de l'étude, le maximum parcouru en mode autonome par un développeur était d'environ 1,3 million de miles ;
  - même à 10 millions de miles, « one still would not be able to draw statistical conclusions » ;
  - références humaines : 77 blessés et environ 1 décès pour 100 millions de miles (2013) ;
  - les développeurs « cannot drive their way to safety » ;
  - alternatives : tests accélérés, tests virtuels et simulateurs, modélisation mathématique, tests de scénarios, études pilotes ;
  - la réglementation doit « evolve with the technology ».

  — [EurekAlert, communiqué RAND](https://www.eurekalert.org/news-releases/817435)
- Littlewood & Strigini (1993) :
  - sous ignorance, une médiane de T heures avant défaillance exige T heures sans défaillance ;
  - pour obtenir une médiane de 10⁶ avec seulement 10³ heures de test, « we essentially need to start with the belief in the 10⁶ median » ;
  - l'écart entre exigences et ce qu'on peut apprendre par l'observation est de « several orders of magnitude » et ne disparaît pas avec les variantes d'a priori ;
  - les a priori forts « must, of course, have a scientific foundation ».

  — [City Research Online](https://openaccess.city.ac.uk/id/eprint/1251/)

### Inferences
- Le chiffre RAND est la règle de trois (calcul). 2,996 / 1,09·10⁻⁸ = 274,9 millions de miles. La flotte parcourt 100 × 24 × 365 × 25 = 21,9 millions de miles par an, d'où environ 12,6 ans. La leçon tient en une ligne : la donnée nécessaire est proportionnelle à 1/barre.
- **Transposition au projet** (calcul) :
  - pour une barre de 1/20 000, une « preuve » à 95 % exige environ 60 000 écritures **effectivement indépendantes** du type à fort enjeu, sans aucune erreur, et davantage si les erreurs sont groupées (section 6) ;
  - avec une condition d'information plus légère (λ_b ≥ 1), il en faut encore environ 20 000.
  - Un banc hors-ligne n'atteindra souvent pas ces volumes. Le verdict honnête pour ces strates est alors « non démontrable », pas « délégable ».
- **La seule autre voie rigoureuse** (Littlewood & Strigini, Winkler et al.) est une information a priori explicite et justifiée. On peut emprunter de la force entre types, environnements ou modèles par un modèle hiérarchique, avec une analyse de sensibilité préenregistrée.
- Démontrer « mieux que la barre avec une marge et une puissance donnée » coûte beaucoup plus qu'une simple borne. RAND cite des milliards de miles, mais je n'ai pas pu vérifier ces chiffres.

### Gaps
- Les chiffres RAND pour « X % mieux que l'humain avec 80 % de puissance » et pour la précision d'estimation (souvent cités, de l'ordre de 5 à 11 milliards de miles) n'ont pas été vérifiés : PDF RAND en 403, article de revue payant. Ne pas les citer sans vérification.
- La citation de 275 millions et 12,5 ans vient d'une source secondaire qui reproduit la p. 3. Je n'ai pas pu la vérifier dans le PDF.

---

## 6. Grappes : effet de plan, taille effective, ICC binaire, grappes de taille 1

### Takeaway
On calcule n_eff = n/DE avec DE = 1 + (m̄−1)ρ (Kish). Si la taille des grappes varie, m̄ doit être remplacé par (CV²+1)·m̄ = Σmᵢ²/N, sinon l'effet de plan est sous-estimé. Les estimateurs de l'ICC binaire (ANOVA, etc.) sont bruités, peuvent être négatifs et sont **indéfinis quand une strate n'a aucune erreur**. Les grappes de taille 1 n'apportent aucune information intra-grappe. Les conventions NCHS (n_eff indéfini à 0 événement, on prend alors n ; plafond n_eff ≤ n) servent au rapport statistique ; pour décider, elles sont **anti-conservatrices** si les erreurs se groupent. Korn-Graubard est la façon standard d'injecter n_eff dans un intervalle de Clopper-Pearson.

### Cited Findings
- NCHS : n_e = n / effet de plan. À 0 événement, la variance est nulle, « the effective sample size will be undefined », et l'on utilise n pour le critère de taille comme pour l'IC. Si n_eff > n, on utilise n. — [NCHS sr02_175](https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf)
- **Korn & Graubard (1998)**, « Confidence Intervals for Proportions with Small Expected Number of Positive Counts Estimated from Survey Data », *Survey Methodology* (Statistique Canada 12-001-X, décembre 1998), pp. 193-201. L'intervalle binomial exact est adapté aux données d'enquête via une taille effective. Dans des simulations limitées, sa couverture est meilleure que celle des intervalles normaux, logit ou Poisson. — [Statistique Canada](https://www150.statcan.gc.ca/n1/en/catalogue/12-001-X19980024356)
- Mise en œuvre dans le paquet R `survey` (`svyciprop`, méthode « beta ») : taille effective fondée sur la variance estimée de la proportion. Les méthodes « beta », « likelihood » et « logit » sont « noticeably better » près de 0 et de 1. — [R survey, svyciprop](https://r-survey.r-forge.r-project.org/survey/html/svyciprop.html)
- **Wu, Crespi & Wong (2012)**, *Contemp Clin Trials* 33(5):869-880 :
  - estimateur ANOVA : ρ̂ = (MSB − MSW)/(MSB + (n_A−1)·MSW), avec n_A = [N − Σnᵢ²/N]/(k−1), MSB = [Σ(Zᵢ²/nᵢ) − (ΣZᵢ)²/N]/(k−1) et MSW = [ΣZᵢ − Σ(Zᵢ²/nᵢ)]/(N−k) ;
  - facteur d'inflation de variance « 1+(m − 1)ρ » ;
  - les estimateurs ANOVA, Fleiss-Cuzick, Pearson et GEE peuvent être négatifs ; dans un calcul d'effectif, on utilise alors 0 ou une petite valeur positive ;
  - les intervalles linéaires « do not perform well with extreme values of π and ρ or when cluster size is small » ;
  - leurs données réelles contiennent beaucoup de grappes de taille 1 ;
  - leurs simulations ne couvrent que π de 0,1 à 0,5, pas les événements rares.

  — [PMC3426610](https://pmc.ncbi.nlm.nih.gov/articles/PMC3426610)
- **Ridout, Demétrio & Firth (1999)**, « Estimating Intraclass Correlation for Binary Data », *Biometrics* 55(1):137-148. Comparaison par simulation de nombreux estimateurs ; l'efficacité relative dépend de multiples facteurs de façon complexe. Je n'ai lu que des résumés. — [IDEAS/RePEc](https://ideas.repec.org/a/bla/biomet/v55y1999i1p137-148.html)
- **Rutterford, Copas & Eldridge (2015)**, *Int J Epidemiol* 44(3):1051-1067 :
  - tailles égales : DE = 1+(n−1)ρ ;
  - tailles variables : DE = 1+{(CV²+1)·n̄−1}ρ ;
  - utiliser la taille moyenne « will underestimate the required sample size », d'autant plus que la variabilité est forte ;
  - sous CV < 0,23, l'ajustement est négligeable ;
  - prendre la taille maximale « may be overly conservative ».

  — [PMC4521133](https://pmc.ncbi.nlm.nih.gov/articles/PMC4521133)

### Inferences
- Les points suivants se déduisent algébriquement des formules de Wu et al.
- **Strate sans erreur.** Tous les Zᵢ valent 0, donc MSB = MSW = 0 et ρ̂ = 0/0 : l'ICC est indéfini. C'est le pendant de « n_eff indéfini » chez NCHS. La correction n/(1+(m̄−1)ρ̂) n'est **pas calculable** justement dans les strates qui posent problème.
- **Grappes de taille 1.** Pour nᵢ = 1 et Zᵢ ∈ {0, 1}, Zᵢ − Zᵢ²/1 = 0 : elles ne contribuent pas à la somme des carrés intra-grappe et n'informent que la variation inter-grappes. Elles tirent aussi n_A vers 1. Si toutes les grappes sont de taille 1, MSW = 0/0 mais DE = 1 quel que soit ρ : aucune correction n'est nécessaire.
- **Bornes utiles quand ρ̂ est inestimable.** Pour ρ ∈ [0, 1], DE ∈ [1, Σmᵢ²/N], car (CV²+1)·m̄ = Σmᵢ²/N. D'où n_eff ∈ [N²/Σmᵢ², N]. La borne basse N²/Σmᵢ² = k/(1+CV²), où k est le nombre de tâches, a la forme de la taille effective de Kish pour pondérations. **Le nombre de tâches, corrigé du CV, est un plancher défendable pour n_eff** quand ρ̂ n'est pas estimable. Exemple : 2 000 écritures réparties en 20 tâches. Si les erreurs sont fortement groupées, l'information réelle est plus proche de 20 que de 2 000.
- **Options préenregistrables pour les strates à x = 0**, par ordre de prudence décroissante :
  1. n_eff = plancher par tâches ;
  2. ρ fixé à un quantile haut des ρ̂ observés dans les strates avec événements (ou dans un pilote) ;
  3. ρ emprunté à un regroupement : même modèle × environnement, tous types confondus, avec un rétrécissement hiérarchique ;
  4. la convention NCHS (n), à réserver au rapport descriptif.
- **Le m̄ de la formule doit être Σmᵢ²/N**, la moyenne pondérée par la taille, et non la moyenne simple, dès que le nombre d'écritures par tâche varie (CV ≥ 0,23). Sinon, n_eff est surestimé.
- **La condition d'information se calcule sur n_eff** : λ_b = n_eff·b ≥ c. Exemple (calcul) : avec m̄ = 5 et ρ = 0,2, DE = 1,8 ; il faut 1,8 fois plus d'écritures pour le même λ_b.
- **Pour x > 0**, l'analogue Korn-Graubard consiste à utiliser des comptes effectifs (x_eff = p̂·n_eff, n_eff) dans Clopper-Pearson ou dans une Beta a posteriori. Pour la version bayésienne, c'est une approximation usuelle, mais je n'ai pas de source pour cet usage précis.

### Gaps
- Je n'ai trouvé aucune source sur le comportement des estimateurs d'ICC binaire pour des événements très rares (prévalence < 1 %) : Wu et al. simulent π ≥ 0,1. Je n'ai pas non plus étudié la dépendance de l'ICC binaire à la prévalence.
- Je n'ai pas consulté Kish (1965) directement ; la formule de l'effet de plan est citée via Wu et al., Rutterford et al. et NCHS.
- Le texte intégral de Ridout et al. (1999) n'a pas été lu.
- Je n'ai pas de source sur l'usage de « comptes effectifs » dans un a posteriori bêta. C'est une heuristique, à préenregistrer comme telle.
