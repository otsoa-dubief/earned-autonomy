# Définir le « succès » d'une politique d'abstention ou de délégation : classification sélective, learning to defer, conformal risk control, Learn then Test

## Q1. Classification sélective à risque garanti : comment le succès est-il énoncé, une couverture minimale est-elle exigée, comment la couverture est-elle rapportée avec son incertitude ?

### Takeaway
Chez Geifman et El-Yaniv (2017), le succès combine deux éléments. La contrainte est une garantie PAC : risque sélectif ≤ r* avec probabilité ≥ 1 − δ. L'objectif est de maximiser la couverture. Aucune couverture minimale n'est exigée, et la couverture est rapportée comme une simple valeur observée. El-Yaniv et Wiener (2010) vont plus loin. Pour eux, un « résultat positif » est une paire de bornes conjointes, risque ≤ B_R **et** couverture ≥ B_Φ, valables avec probabilité ≥ 1 − δ. Ils nomment explicitement le rejet total comme la solution triviale à risque nul.

### Cited Findings
**Geifman et El-Yaniv 2017, « Selective Classification for Deep Neural Networks » (arXiv 1705.08500)**
- Définitions (§2). La couverture `φ(f,g) = E_P[g(x)]` « is the probability mass of the non-rejected region in 𝒳 ». Le risque sélectif s'écrit `R(f,g) = E_P[ℓ(f(x),y)·g(x)] / φ(f,g)` (Éq. 1) — [Geifman & El-Yaniv 2017](https://arxiv.org/abs/1705.08500)
- Énoncé du problème (§2, Éq. 2) : `Pr_{S_m}{R(f,g) > r*} < δ`, puis « Among all classifiers satisfying (2), the best ones are those that maximize the coverage. » Au §1, l'objectif est un classifieur « whose test error will be no larger than r∗ with probability of at least 1−δ » — [Geifman & El-Yaniv 2017](https://arxiv.org/abs/1705.08500)
- Algorithme SGR. Il fait une recherche dichotomique sur le seuil de confiance θ, en ⌈log₂ m⌉ itérations. À chaque pas, il calcule `b*_i = B*(r̂_i, δ/⌈log₂m⌉, g_i(S_m))`. Si `b*_i < r*`, il élargit l'acceptation (`z_max = z`), sinon il la resserre. La sortie est « (f,g_k) and the bound b*_k ».
  - Lemme 3.1 (Gascuel & Caraux 1992) : B* est la solution b de `Σ_{j=0}^{m·r̂} C(m,j) b^j (1−b)^{m−j} = δ`, c'est-à-dire une inversion de la queue binomiale.
  - Théorème 3.2 : `Pr_{S_m}{∃i : R(f|P_{g_i}) > B*(r̂_i, δ/k, g_i(S_m))} < δ`, avec `k = ⌈log₂m⌉`. Le passage à toutes les itérations se fait par borne de l'union.
  — [Geifman & El-Yaniv 2017](https://arxiv.org/abs/1705.08500)
- Absences constatées dans le texte lu : aucun cas d'échec décrit si aucun seuil n'atteint r* ; aucune mention du rejet total comme solution triviale ; aucune couverture minimale — [Geifman & El-Yaniv 2017](https://arxiv.org/abs/1705.08500)
- Formulation du résultat dans le résumé : « an unprecedented 2% error in top-5 ImageNet classification can be guaranteed with probability 99.9% » … « and almost 60% test coverage. » Le risque est garanti ; la couverture est un résultat empirique placé à côté — [Geifman & El-Yaniv 2017](https://arxiv.org/abs/1705.08500)
- Rapport des résultats. Les colonnes des tables sont « Desired risk (r*) », « Train risk », « Train coverage », « Test risk », « Test coverage » et « Risk bound (b*) ». Le §5.1 indique : « computed, for each selective classifier, test risk and test coverage ». La couverture est une valeur ponctuelle sur le jeu de test, sans intervalle de confiance — [Geifman & El-Yaniv 2017](https://arxiv.org/abs/1705.08500)
- Courbe risque-couverture (§2) : « The entire performance profile of such a classifier can be specified by its risk-coverage curve, defined to be risk as a function of coverage. » — [Geifman & El-Yaniv 2017](https://arxiv.org/abs/1705.08500)

**El-Yaniv et Wiener 2010, « On the Foundations of Noise-free Selective Classification », JMLR 11:1605–1641 (PDF lu page par page)**
- Résumé : « The essence in selective classification is to trade-off classifier coverage for higher accuracy. We term this trade-off the risk-coverage (RC) trade-off. » — [El-Yaniv & Wiener 2010](https://www.jmlr.org/papers/volume11/el-yaniv10a/el-yaniv10a.pdf)
- Définitions 1 et 2 (p. 1606–1607) : `Φ(f,g) ≜ E[g(X)]`. Le risque est « the average loss on the accepted samples », soit `R(f,g) ≜ E[ℓ(f(X),Y)·g(X)] / Φ(f,g)` — [El-Yaniv & Wiener 2010](https://www.jmlr.org/papers/volume11/el-yaniv10a/el-yaniv10a.pdf)
- **Critère de succès (p. 1607).** « A positive result in this model is a pair of bounds, B_R = B_R(𝓕,δ,m) and B_Φ = B_Φ(𝓕,δ,m), for risk and coverage, respectively, that for any δ and m, hold with high probability, of at least 1 − δ for any distribution P; namely, `Pr{R(f,g) ≤ B_R ∧ Φ(f,g) ≥ B_Φ} ≥ 1 − δ`. » Un résultat négatif est l'énoncé symétrique `Pr{R(f,g) ≥ B_R ∨ Φ(f,g) ≤ B_Φ} ≥ δ`, pour une certaine distribution P — [El-Yaniv & Wiener 2010](https://www.jmlr.org/papers/volume11/el-yaniv10a/el-yaniv10a.pdf)
- But et faisabilité (p. 1608).
  - « the goal in selective classification is to output a selective classifier (f,g) that has sufficiently low risk with sufficiently high coverage ».
  - « We say that (r,c) is (efficiently) achievable if there is an (efficient) learning algorithm that will output a selective classifier (f,g) such that with probability of at least 1 − δ, its coverage is at least c and its risk is at most r. »
  — [El-Yaniv & Wiener 2010](https://www.jmlr.org/papers/volume11/el-yaniv10a/el-yaniv10a.pdf)
- Exemple de cahier des charges (p. 1608) : « an error constraint (say, 2% error) … a classifier whose ensured test error (w.h.p.) is not larger than 2%, while having the maximum possible coverage of the domain. » — [El-Yaniv & Wiener 2010](https://www.jmlr.org/papers/volume11/el-yaniv10a/el-yaniv10a.pdf)
- **La solution triviale est nommée.** p. 1610 : « Obviously, zero risk is trivially achieved by taking g that rejects the entire input space 𝒳. But is it possible to achieve perfect learning on a guaranteed fraction of the effective volume of 𝒳? » p. 1608 : « it is not at all clear if non-trivial perfect learning (with guaranteed positive coverage) can be accomplished. » — [El-Yaniv & Wiener 2010](https://www.jmlr.org/papers/volume11/el-yaniv10a/el-yaniv10a.pdf)
- Théorème 8 (résumé p. 1610) : pour une classe 𝓕 finie, avec probabilité ≥ 1 − δ, la couverture de la stratégie CSS vaut au moins `1 − (1/m)·O(|𝓕| + ln(1/δ))` (Éq. 2). Le Théorème 7 établit qu'aucune stratégie à risque nul n'a une couverture supérieure à celle de CSS — [El-Yaniv & Wiener 2010](https://www.jmlr.org/papers/volume11/el-yaniv10a/el-yaniv10a.pdf)
- Théorème 14 (résumé p. 1610).
  - « it is impossible to provide any coverage guarantees for perfect learning, in the general case ».
  - Pour les classifieurs linéaires, une distribution défavorable force tout apprenant à risque nul « to reject the entire volume of 𝒳, thus failing to guarantee more than zero coverage ».
  - « point c* is simply the coordinate (0,0) on the RC plane ».
  - « when aiming at very small risks, the rejection rate might in general be very high (very small coverage), which may be unacceptable in many applications. »
  — [El-Yaniv & Wiener 2010](https://www.jmlr.org/papers/volume11/el-yaniv10a/el-yaniv10a.pdf)
- Note 1 (p. 1610) : « The requirement that in perfect learning the risk is zero with certainty is dual to the requirement that the coverage is 100% with certainty in standard learning. » — [El-Yaniv & Wiener 2010](https://www.jmlr.org/papers/volume11/el-yaniv10a/el-yaniv10a.pdf)

**SelectiveNet (Geifman et El-Yaniv 2019, arXiv 1901.09192) : la formulation duale, à couverture imposée**
- Formulation (Éq. 2) : `θ* = argmin_θ R(f_θ,g_θ) s.t. φ(g_θ) ≥ c`, décrite comme « optimizing the selective risk, given a constraint on the coverage or vice versa ». L'introduction précise : « Within an abstention-constrained framework, whereby the user specifies the desired target coverage… » — [SelectiveNet](https://arxiv.org/abs/1901.09192)
- Calibration de la couverture (§5) : « τ is set to be the 100(1−c) percentile of the distribution of g(x_i), x_i∈V_n ». Une borne de Hoeffding place la couverture dans `[c − ε, c + ε]` avec probabilité ≥ 1 − δ, où `ε = √(ln(2/δ)/(2n))`. Les tables donnent la couverture test en moyenne ± écart-type sur plusieurs entraînements, avec une ligne « Average violation » — [SelectiveNet](https://arxiv.org/abs/1901.09192)
- Le §2 indique qu'on peut convertir un modèle « à couverture contrôlée, risque optimisé » en modèle à risque contrôlé « using the technique of Geifman & El-Yaniv 2017b » — [SelectiveNet](https://arxiv.org/abs/1901.09192)

**Franc, Prusa et Voracek, « Optimal strategies for reject option classifiers » (arXiv 2101.12523)**
- Trois modèles de rejet :
  - modèle à coût (Problème 1, Éq. 1) : `min_{h,c} R_B(h,c)`, avec une perte de rejet ε ;
  - bounded-improvement (Problème 2, Éq. 7) : « Given a target risk λ>0 … », `max φ(c) s.t. R_S(h,c) ≤ λ` ;
  - bounded-coverage (Problème 4, Éq. 18) : « Given a target coverage ω>0 … », `min R_S(h,c) s.t. φ(c) ≥ ω`.
  — [Franc et al.](https://arxiv.org/abs/2101.12523)
- Le résumé affirme : « the three rejection models lead to the same prediction strategy », à savoir un classifieur de Bayes et un seuil de sélection éventuellement randomisé. Le §1 note : « The cost-based model requires the reject cost to be defined explicitly which is difficult in some applications. » Le cas d'une cible infaisable n'est pas traité ; les auteurs supposent que les optima existent — [Franc et al.](https://arxiv.org/abs/2101.12523)

**AURC et métriques intégrées sur la courbe**
- Geifman, Uziel et El-Yaniv 2019 (arXiv 1805.08206).
  - La courbe RC est « the selective risk as a function of coverage ».
  - `AURC(κ,f|V_n) = (1/n) Σ_{θ∈Θ} r̂(f,g_θ|V_n)`.
  - `E-AURC = AURC(κ,f|V_n) − AURC(κ*,f|V_n)` ; « E-AURC is a unitless measure in [0,1], and the optimal κ will have E-AURC = 0 ».
  - `AURC(κ*) = (1/n) Σ_{i=1}^{r̂n} i/(n(1−r̂)+i)`.
  - Les erreurs-types ne sont données que pour une partie des méthodes ; aucun intervalle de confiance.
  - Incohérence interne : un paragraphe parle de « normaliser par » AURC(κ*), alors que la formule soustrait.
  — [Geifman, Uziel & El-Yaniv 2019](https://arxiv.org/abs/1805.08206)
- Traub et al. 2024 (arXiv 2407.01032).
  - Risque généralisé (Éq. 3) : « This metric reflects the joint probability of misclassification and acceptance by the confidence score threshold. »
  - AUGRC (Éq. 6) : borné dans [0, 1/2].
  - Critiques : « excessive over-weighting of high-confidence failures in AURC » ; « the Selective Risk is not suitable for aggregation over rejection thresholds to holistically assess a SC system » ; le risk@coverage « implies a pre-determined cutoff on the risk or coverage ».
  - Ils posent cinq exigences, R1 à R5, dont R2 : « The metric should be monotonic w.r.t both evaluated factors stated in R1 ».
  - Incertitude : bootstrap, puis « one-sided Wilcoxon signed-rank tests » avec correction de Holm, pour la stabilité des classements entre méthodes ; pas d'intervalle de confiance sur les métriques. Rien sur le rejet total.
  — [Traub et al. 2024](https://arxiv.org/abs/2407.01032)
- La survey de Hendrickx et al. emploie « AURC » pour « the Area Under the ARC Curve », c'est-à-dire la courbe précision-rejet. Le sigle entre en collision avec l'AURC risque-couverture — [Hendrickx et al.](https://arxiv.org/abs/2107.11277)

### Inferences
- **SGR n'interdit pas la solution triviale, il la domine.** Le succès y vaut « risque certifié + couverture maximale », sans plancher. La politique triviale perd dès qu'un seuil à couverture positive passe la borne. Si aucun seuil ne passe, SGR renvoie quand même un seuil, avec b* ≥ r*. C'est ma lecture de l'algorithme : les auteurs ne discutent pas ce cas.
- **La borne B* pénalise la timidité extrême.** B* est une inversion binomiale calculée sur les seuls exemples acceptés (`g_i(S_m)`). Moins on accepte d'exemples, plus la borne est lâche. Une couverture quasi nulle ne peut donc pas certifier un risque bas : avec le risque **sélectif**, le cadre à risque garanti pénalise mécaniquement la timidité extrême. Inférence tirée de la forme du Lemme 3.1.
- **El-Yaniv et Wiener donnent le critère formel le plus net.** Un succès est un énoncé PAC conjoint sur le risque **et** la couverture ; « non-trivial » signifie une couverture garantie strictement positive. Leur Théorème 14 avertit aussi qu'une cible de risque trop stricte peut, à elle seule, ramener la couverture garantie à zéro. Une politique triviale peut donc refléter un budget trop dur, et non la qualité d'une règle.
- **AURC, E-AURC et AUGRC ne sont pas des critères confirmatoires pour une règle unique.** Ils évaluent un score de confiance, donc un classement, sur toutes les couvertures, et non une règle à un point de fonctionnement.

### Gaps
- Méthode, valable pour toutes les questions. Les textes ont été lus dans leur version arXiv, rendue par ar5iv ; la numérotation peut différer des actes. Les citations ont été extraites par un modèle (WebFetch), sauf El-Yaniv et Wiener 2010, lu directement dans le PDF. La notation mathématique est retranscrite.
- Chez El-Yaniv et Wiener, seule la synthèse du §3 a été lue ; les énoncés complets des Théorèmes 7, 11, 14 et 21 et leurs preuves ne l'ont pas été.
- Aucune source trouvée ne rapporte la couverture obtenue par SGR avec un intervalle de confiance.

## Q2. Learning to defer : comment mesure-t-on la valeur d'un système de délégation face à « toujours déléguer » et « ne jamais déléguer », et utilise-t-on des contraintes de charge humaine ?

### Takeaway
La valeur se mesure de deux façons. Soit on balaie, ou on fixe, le taux de délégation entre les deux extrêmes (« complete automation and none »). Soit on compare aux performances seules : expert seul, modèle seul. « Toujours déléguer » est écarté par un coût de délégation (c, c(x), γ_defer) ou par un budget de charge humaine (`E[π(x)] ≤ b`, budget B, couverture de c % imposée). Aucune des sources lues ne teste statistiquement la supériorité sur « toujours déléguer ».

### Cited Findings
**Madras, Pitassi et Zemel 2018, « Predict Responsibly » (arXiv 1711.06664)**
- Perte de délégation (Éq. 3) : un mélange `(1−s_i)·ℓ(Y_i, Ŷ_M,i) + s_i·ℓ(Y_i, Ŷ_D,i)` (modèle contre décideur), sans pénalité. La pénalité n'apparaît que dans la preuve du théorème (Éq. 7), introduite par « If we include a similar γ_defer penalty, the deferring loss function is ». Dans les expériences : « We show results across various hyperparameter settings (α_fair, γ_defer/γ_reject). » — [Madras et al. 2018](https://arxiv.org/abs/1711.06664)
- Points de référence dans les figures : « Square is a baseline binary classifier, trained only to optimize accuracy » (jamais déléguer) et « Yellow circle is DM alone. » (décideur seul). Conclusion : « the most accurate result is not to replace the DM, but to use a DM-model mixture » — [Madras et al. 2018](https://arxiv.org/abs/1711.06664)
- Le taux de délégation est un résultat observé (axe x de la Fig. 3c), pas une contrainte. La justification de γ_defer n'a pas été trouvée — [Madras et al. 2018](https://arxiv.org/abs/1711.06664)

**Mozannar et Sontag 2020, « Consistent Estimators for Learning to Defer to an Expert » (arXiv 2006.01862)**
- Le coût de l'expert `l_exp(x,y,m)` peut inclure « a constant additive cost function c(x) for querying the expert depending on the instance x ». Les auteurs écrivent : « The above formulation is a generalization of the learning with rejection framework studied by [CDM16b] … as by setting lexp(x,y,m)=c for a constant c>0 the two objectives coincide ». Ils rappellent : « The framework of rejection learning assumes a constant cost c of deferring » — [Mozannar & Sontag 2020](https://arxiv.org/abs/2006.01862)
- Métriques (légende de la Table 2) : « recording system accuracy, coverage and classifier accuracy on non-deferred examples » — [Mozannar & Sontag 2020](https://arxiv.org/abs/2006.01862)
- **Balayage contraint de la couverture** : « We constrain our method and the baselines to achieve c% coverage for c∈[100] to simulate the spectrum between complete automation and none. » La motivation est clinique : « In a clinical setting there might be a cost associated to querying a radiologist, this then imposes a constraint on how often we can query the radiologist » — [Mozannar & Sontag 2020](https://arxiv.org/abs/2006.01862)
- Les baselines nommées sont Confidence (Raghu et al.), MixOfExp (Madras et al.), des variantes Oracle et ModelConfidence. « Expert seul » et « modèle seul » ne figurent pas comme bras de comparaison explicites dans la partie lue — [Mozannar & Sontag 2020](https://arxiv.org/abs/2006.01862)

**Okati, De et Gomez-Rodriguez 2021, « Differentiable Learning Under Triage » (arXiv 2103.08902)**
- Le problème (Éq. 1) est de minimiser `L(π,m)` sous la contrainte `E_x[π(x)] ≤ b`, où b « is a given parameter that limits the level of triage ». La perte (Éq. 2) s'écrit `L(π,m) = E[(1−π(x))ℓ(m(x),y) + π(x)ℓ(h,y)]`. Les contributions évoquent un algorithme « subject to a constraint on the maximum level of triage » — [Okati et al. 2021](https://arxiv.org/abs/2103.08902)
- **Proposition 2 (condition de non-trivialité).** S'il existe un sous-ensemble de mesure positive où la perte du modèle en automatisation complète dépasse celle de l'humain, « then there exists a nontrivial triage policy » qui fait mieux que l'automatisation complète π₀. Théorème 3 : « the optimal triage policy is a deterministic threshold rule » — [Okati et al. 2021](https://arxiv.org/abs/2103.08902)
- Évaluation : « Misclassification test error P(ŷ ≠ y) against the triage level b » (Fig. 4). Les baselines sont un triage par confiance, par score, par surrogate, et l'automatisation complète ; il n'y a pas de bras « humain seul ». En travaux liés, les méthodes de learning to defer qui « just pay a constant cost every time they defer predictions » sont opposées à cette approche — [Okati et al. 2021](https://arxiv.org/abs/2103.08902)

**Raghu et al. 2019, « The Algorithmic Automation Problem » (arXiv 1903.12220)**
- Formulation (§2.1) : « We would like to select a subset S of instances on which no human effort will be used » ; « Suppose that we have a budget B on the total number of units of human effort that we can allocate ». Au §2.2, α est « the fraction of instances that we wish to assign to the algorithm » — [Raghu et al. 2019](https://arxiv.org/abs/1903.12220)
- Références (§4.2) : « full automation » d'un côté ; de l'autre, α = 0, qui « corresponds to equal coverage of all instances by human effort ». L'erreur moyenne et le F1 sont tracés en fonction de la fraction automatisée. Au §1 : « when the algorithm automates a fraction of the cases, that frees up human effort » — [Raghu et al. 2019](https://arxiv.org/abs/1903.12220)
- La valeur n'est pas formulée comme « effort humain économisé à erreur égale » : l'erreur est mesurée à budget fixé — [Raghu et al. 2019](https://arxiv.org/abs/1903.12220)

**Bansal et al. 2021 (CHI 2021) : la « complementary performance »**
- Définition : « complementary performance, where team accuracy is higher than either the human or the AI working solo ». Sur les études antérieures : « prior studies observed improvements from explanations only when the AI, alone, outperformed both the human and the best team. » — [Bansal et al. 2021](https://arxiv.org/abs/2006.14779)

**Hendrickx et al., survey sur le rejet (arXiv 2107.11277)**
- Motivations liées à la charge humaine. Le rejet « can still result in time savings by only requiring human interventions to make decisions in a small number of cases » (§1). Dans une application au cancer du sein : « The rejection thresholds are chosen to limit the rejection rate and reduce manual effort » (§8). Le §9.5 distingue la délégation : « learning with rejection usually assumes that the user will inspect any rejected examples » — [Hendrickx et al.](https://arxiv.org/abs/2107.11277)

### Inferences
- **Chez Okati, la contrainte de charge est une couverture minimale vue côté humain.** `E_x[π(x)] ≤ b` équivaut à un taux d'automatisation ≥ 1 − b. Avec b < 1, « toujours déléguer » est infaisable par construction. Il en va de même du budget B de Raghu et des c % de couverture imposés par Mozannar et Sontag.
- **« Toujours déléguer » pourrait être optimal sans coût ni budget.** La Proposition 2 d'Okati dit quand une politique non triviale bat l'automatisation complète. Inversement, si la délégation est gratuite et l'humain meilleur partout, « toujours déléguer » minimise la perte. Aucun texte lu ne l'écrit ; c'est ce qui rend nécessaire le coût (c, c(x), γ_defer) ou le budget.
- **La comparaison aux extrêmes reste descriptive.** Elle passe par des courbes et des tables (points « DM alone », « α = 0 », couverture de 0 à 100 %). Je n'ai trouvé aucun test d'hypothèse confirmatoire contre « toujours déléguer ».
- **La règle de Bansal se transpose à l'expérience.** Un système délégant doit battre **chacun** des solos. Ici, cela voudrait dire battre « tout valider » sur la charge humaine, et les règles de base sur le risque.

### Gaps
- Non vérifiés : la littérature récente de learning to defer avec contraintes explicites de charge ou de capacité, comme Narasimhan et al. 2022, Mozannar et al. 2023 ou Alves et al. 2024.
- Chez Mozannar et Sontag, la fin de l'annexe (au-delà de 100 000 caractères) n'a pas été lue.
- Chez Madras et al., aucune phrase ne justifie γ_defer.
- Ni Okati ni Raghu n'emploient « trivial » pour la politique « tout envoyer aux humains ».

## Q3. Conformal risk control, Learn then Test, RCPS : que garantissent-ils quand aucun paramètre ne passe, et comment formulent-ils l'utilité à côté de la garantie de risque ?

### Takeaway
Les trois méthodes réagissent différemment quand aucun paramètre ne passe :
- CRC retombe sur λ_max, qu'une hypothèse suppose sûr (`L_i(λ_max) ≤ α`) ;
- RCPS suppose qu'il existe un λ_max de risque nul ;
- LTT renvoie Λ̂ = ∅ et écrit « we abstain from returning an RCP ».

L'utilité n'est jamais garantie. Elle est optimisée parmi les paramètres valides, puis rapportée empiriquement (taille d'ensemble, taux d'abstention). Le seul garde-fou formel est la borne inférieure de risque de CRC (« not too conservative »).

### Cited Findings
**Conformal Risk Control (Angelopoulos, Bates, Fisch, Lei, Schuster ; arXiv 2208.02814)**
- Théorème 1. Les hypothèses : `L_i(λ)` est « non-increasing in λ, right-continuous », avec `L_i(λ_max) ≤ α` et `sup_λ L_i(λ) ≤ B < ∞` presque sûrement (Éq. 6). La conclusion : `E[L_{n+1}(λ̂)] ≤ α` (Éq. 7) — [CRC](https://arxiv.org/abs/2208.02814)
- Choix du paramètre (Éq. 4) : `λ̂ = inf{λ : (n/(n+1))·R̂_n(λ) + B/(n+1) ≤ α}`. **Si aucun λ ne passe :** « When the set is empty, we define λ̂ = λ_max. » — [CRC](https://arxiv.org/abs/2208.02814)
- **Borne inférieure.** Théorème 2 : `E[L_{n+1}(λ̂)] ≥ α − 2B/(n+1)`, sous des hypothèses i.i.d., `L_i ≥ 0` et absence de sauts (`P(J(L_i,λ) > 0) = 0`). Les auteurs commentent : « the algorithm satisfies a tight lower bound saying it is not too conservative » ; elle est « tight up to a factor 2B/(n+1) that cannot be improved in general » — [CRC](https://arxiv.org/abs/2208.02814)
- Utilité. Le résumé annonce des exemples qui « bound the false negative rate, graph distance, and token-level F1-score ». Le §3 affirme que la procédure « bounds the risk as desired and gives useful outputs to the end-user ». La taille des ensembles est montrée dans les figures (« report FNR and set size »), sans être un objectif formel. Ni la trivialité ni la classification sélective ne sont discutées — [CRC](https://arxiv.org/abs/2208.02814)

**Learn then Test (Angelopoulos, Bates, Candès, Jordan, Lei ; arXiv 2110.01052)**
- Définition 1 : un prédicteur est un (α,δ)-RCP si `P(R(T_λ̂) ≤ α) ≥ 1−δ`. « The risk tolerance α and error level δ are chosen in advance by the user. » — [LTT](https://arxiv.org/abs/2110.01052)
- Le contrôle du risque devient un test multiple. À chaque λ_j on associe « the null hypothesis ℋ_j : R(λ_j) > α », avec la remarque : « Notice that rejecting ℋ_j corresponds to selecting λ_j as a point where the risk is controlled. » On pose ensuite `Λ̂ = 𝒜(p_1,…,p_N)`, où 𝒜 « controls the family-wise error rate (FWER) ». Théorème 1 : `P(sup_{λ∈Λ̂} R(λ) ≤ α) ≥ 1−δ` — [LTT](https://arxiv.org/abs/2110.01052)
- **Si rien ne passe.** Au Théorème 1 : « the supremum over an empty set is defined as −∞ ». Au §1.1 : « Note that some risks cannot be controlled at every level α for every data-generating distribution; in such cases, we abstain from returning an RCP. » Légende de la Fig. 10 : « An entry of ∅ means that the procedure failed to reject anywhere: Λ̂=∅. » — [LTT](https://arxiv.org/abs/2110.01052)
- **Utilité.** Parmi les λ valides, « we can choose the one that maximizes another performance metric estimated using the same data ». Par exemple : « we would want to choose λ̂=min Λ̂, which yields the most discoveries and hence the lowest false negative rate (FNR) ». Le §4.1 ajoute : « Because we use FWER control to pick Λ̂, we can optimize over the parameters however we wish. » — [LTT](https://arxiv.org/abs/2110.01052)
- **Classification sélective (§3.2).** Le risque contrôlé est « the error conditionally on predicting », `P[T(X)≠Y | T(X)≠∅]`. L'utilité apparaît dans la légende de la Fig. 4 : « The line plot shows the empirical risk and fraction of abstentions when sweeping across values of λ. » Un garde-fou ad hoc : « To avoid degeneracy, we clip all λ with n(T_λ)<25. » — [LTT](https://arxiv.org/abs/2110.01052)
- Risques multiples (§2.4) : « we seek to control m risks R_1,…,R_m at levels α_1,…,α_m simultaneously ». Aucune garantie séparée de puissance ni de couverture minimale n'a été trouvée — [LTT](https://arxiv.org/abs/2110.01052)

**RCPS (Bates, Angelopoulos, Lei, Malik, Jordan ; arXiv 2101.02703)**
- Définition 1 : « We say that 𝒯 is a (α,δ)-risk-controlling prediction set if, with probability at least 1−δ, we have R(𝒯)≤α. » Théorème 1 : `P(R(𝒯_λ̂) ≤ α) ≥ 1−δ` — [RCPS](https://arxiv.org/abs/2101.02703)
- Choix du paramètre (Éq. 4) : `λ̂ = inf{λ∈Λ : R̂⁺(λ′) < α, ∀λ′ ≥ λ}`, où R̂⁺ est une borne de confiance supérieure (UCB). Les auteurs supposent « there exists an element λ_max∈Λ such that R(λ_max)=0 » (§2.1). Aucun repli explicite n'est décrit si l'ensemble est vide — [RCPS](https://arxiv.org/abs/2101.02703)
- Utilité :
  - « Any collection of the sets can be used to control the risk by Theorem 1, but some may produce larger sets than others » (§4) ;
  - optimalité oracle : des ensembles qui « have the smallest average size among all procedure [sic] that control the risk » (§4.2) ;
  - « The RCPS procedure controls the risk at the correct level and the sets have reasonable sizes » (§5.1) ;
  - dans l'exemple de classement : « The UCB calibration tunes λ so that we abstain from as few pairs as possible » (§6.1).
  — [RCPS](https://arxiv.org/abs/2101.02703)

**CRC appliqué à l'abstention : Yadkori et al. 2024, « Mitigating LLM Hallucinations via Conformal Abstention » (arXiv 2405.01563)**
- La perte (Éq. 1), `ℓ(X,Y;λ) = (1 − a_λ(X))(1 − m(X; f(X), Y))`, pénalise le fait de répondre faux. C'est un risque **joint** : erreur et réponse. Le problème (Éq. 2) consiste à **minimiser le taux d'abstention T(λ) sous la contrainte R(λ) ≤ α**. La garantie (Éq. 4) est `E[R(λ̂_n)] ≤ α` — [Yadkori et al. 2024](https://arxiv.org/abs/2405.01563)
- **La solution triviale est reconnue explicitement** (§2) : « A trivial policy that always abstains would result in a zero loss » ; « an interesting policy would also have a small abstention rate ». — [Yadkori et al. 2024](https://arxiv.org/abs/2405.01563)
- Formulation conjointe dans le résumé : la méthode « reliably bounds the hallucination rate » tout en « maintaining a significantly less conservative abstention rate on a dataset with long responses ». — [Yadkori et al. 2024](https://arxiv.org/abs/2405.01563)
- Rapport des résultats. Le calibrage est rééchantillonné 10 fois, avec des tables « AVERAGE TEST ABSTENTION RATES » en moyenne ± écart-type. La Fig. 1 trace la perte en fonction du taux d'abstention : « Box widths and heights represent 90% confidence intervals ». Le §3.1 précise que la garantie CRC « holds only in expectation over the calibration data » et propose une variante en haute probabilité (Prop. 3.1) — [Yadkori et al. 2024](https://arxiv.org/abs/2405.01563)

### Inferences
- **Deux philosophies quand rien ne passe.**
  - Le repli sur la configuration triviale sûre (λ_max de CRC, λ_max de risque nul de RCPS) laisse la garantie « satisfaite », mais sans aucune utilité.
  - La déclaration d'échec de LTT (Λ̂ = ∅, « abstain from returning an RCP ») évite ce piège.
  - Pour un label confirmatoire, seule la seconde se traduit proprement en « non confirmé ».
- **Le sort du λ trivial dans LTT dépend de la définition du risque.**
  - Supposons que la configuration « tout abstenir » figure dans la grille et que le risque soit **joint**. Ce λ n'a aucune perte, donc son H_j est rejeté sans peine, et il entre dans Λ̂.
  - Seule l'étape « maximiser une autre métrique parmi Λ̂ » l'écarte, et seulement s'il existe un concurrent valide.
  - Avec un risque **conditionnel**, `P[erreur | prédire]`, le λ trivial n'a pas de données et n'est pas certifiable. LTT écarte d'ailleurs les λ ayant moins de 25 prédictions.
- **La borne inférieure de CRC a une portée limitée.** C'est la seule garantie formelle contre le sur-conservatisme que j'aie trouvée. Mais elle porte sur le risque, en espérance, et suppose l'absence de sauts. Cette hypothèse sera probablement violée par une règle discrète à paliers, comme « N succès consécutifs ».
- **Garantie formelle, utilité empirique.** Les quatre papiers énoncent la garantie de risque formellement, avec α et δ fixés à l'avance, et l'utilité à côté, empiriquement : « reasonable sizes », « useful outputs », « less conservative abstention rate », couverture test ponctuelle. L'utilité n'est jamais l'objet d'une garantie.

### Gaps
- La fin de LTT (environ 75 000 caractères d'annexes) et celle de RCPS (environ 51 000) n'ont pas été lues ; d'autres mentions pertinentes peuvent s'y trouver.
- Je n'ai pas trouvé, dans CRC ou RCPS, de phrase reconnaissant explicitement que l'ensemble complet satisfait trivialement la garantie. La reconnaissance explicite vient de Yadkori et al.
- La formule exacte de la Proposition 3.1 de Yadkori et al. n'a pas été vérifiée.

## Q4. Existe-t-il une notion formelle de solution « non triviale », de couverture utile minimale ou d'amélioration sur « tout abstenir », et est-elle testée statistiquement ?

### Takeaway
La notion formelle la plus nette vient d'El-Yaniv et Wiener : un succès est une borne PAC conjointe, risque ≤ B_R **et** couverture ≥ B_Φ, et « non trivial » signifie une couverture garantie strictement positive. Ailleurs, la non-trivialité passe par trois voies :
- une contrainte : couverture ω, budget b ;
- un objectif : minimiser l'abstention sous contrainte de risque ;
- un garde-fou ad hoc : n(T_λ) ≥ 25 dans LTT.

Je n'ai trouvé aucun article qui teste, par un test unilatéral confirmatoire, que la couverture dépasse un minimum ou bat « tout abstenir ».

### Cited Findings
- **El-Yaniv et Wiener 2010.** Un résultat positif est `Pr{R(f,g) ≤ B_R ∧ Φ(f,g) ≥ B_Φ} ≥ 1 − δ`. Ils écrivent « non-trivial perfect learning (with guaranteed positive coverage) » et « zero risk is trivially achieved by taking g that rejects the entire input space ». La couverture de CSS est bornée inférieurement avec probabilité ≥ 1 − δ (Théorème 8). Le Théorème 14 établit l'impossibilité d'une garantie de couverture en général : « point c* is simply the coordinate (0,0) » — [El-Yaniv & Wiener 2010](https://www.jmlr.org/papers/volume11/el-yaniv10a/el-yaniv10a.pdf)
- **Yadkori et al. 2024.** « A trivial policy that always abstains would result in a zero loss », d'où l'objectif « minimize T(λ) subject to R(λ) ≤ α » (Éq. 2) — [Yadkori et al. 2024](https://arxiv.org/abs/2405.01563)
- **Hendrickx et al. (survey).**
  - « looking only at the prediction quality will tend to favor the model with the highest rejection rate » (§3.1) ;
  - « metrics specifically tailored to learning to reject must capture this trade-off » (§3) ;
  - variante contrainte : « the user may provide an upper bound ℜ for the rejection rate and aim to limit the number of rejections » (§5) ;
  - modèle à coût : le coût de rejet « must be lower than a random predictor's average cost » (§3.3).
  - Métriques globales : la qualité combinée vaut `CQ = (TA + TR)/(TA + FA + FR + TR)` et la couverture `φ = (TA + FA)/(TA + FA + FR + TR)`.
  - Dans la partie lue (environ les 100 000 premiers caractères), aucun test statistique ni intervalle de confiance sur le taux de rejet.
  — [Hendrickx et al.](https://arxiv.org/abs/2107.11277)
- **Okati et al. 2021.** La Proposition 2 conclut « there exists a nontrivial triage policy » dès que l'humain fait mieux que le modèle sur un sous-ensemble de mesure positive — [Okati et al. 2021](https://arxiv.org/abs/2103.08902)
- **LTT.** « To avoid degeneracy, we clip all λ with n(T_λ)<25 » ; si rien ne passe, « we abstain from returning an RCP » — [LTT](https://arxiv.org/abs/2110.01052)
- **Franc et al.** Le modèle bounded-coverage, « Given a target coverage ω>0 », s'écrit `min R_S s.t. φ ≥ ω` — [Franc et al.](https://arxiv.org/abs/2101.12523). SelectiveNet le formule ainsi : « whereby the user specifies the desired target coverage » — [SelectiveNet](https://arxiv.org/abs/1901.09192)
- **Incertitude sur la couverture.** SelectiveNet donne un intervalle de Hoeffding, couverture ∈ `[c − ε, c + ε]` avec probabilité ≥ 1 − δ et `ε = √(ln(2/δ)/(2n))` — [SelectiveNet](https://arxiv.org/abs/1901.09192). Traub et al. utilisent des tests de Wilcoxon unilatéraux avec correction de Holm, mais pour départager des méthodes, pas pour les comparer à la politique triviale — [Traub et al. 2024](https://arxiv.org/abs/2407.01032)
- **Sélection conforme (Jin et Candès, arXiv 2210.01408), proche de « déléguer = sélectionner ».**
  - Garantie : `FDR ≤ q` (Théorème 2.3).
  - Utilité : la puissance, « the proportion of correct selections among all positive test samples ».
  - « sometimes one needs to output ℛ=∅ in order to keep the FDR below q, leading to smaller selection sets ».
  - Objectif : trouver « as many test units … as possible, while ensuring the false discovery rate (FDR) is controlled ».
  - La puissance est rapportée en moyenne sur des réplications (« averaging … over all replicates »), sans intervalle de confiance.
  - Cas d'usage cités : « filter out low-risk cases, leaving other cases for careful human evaluation ».
  — [Jin & Candès 2023](https://arxiv.org/abs/2210.01408)

### Inferences
- **Quatre verrous contre la solution triviale**, chacun observé dans au moins une littérature :
  - **(a) Coût de l'abstention ou de la délégation** : Chow, c et c(x) chez Mozannar et Sontag, γ_defer chez Madras. Il exige de chiffrer le rapport entre le coût d'une validation et celui d'une erreur ; Franc et al. jugent cela « difficult ».
  - **(b) Couverture minimale imposée** : ω, le c de SelectiveNet, `E[π] ≤ b`, le budget B, les c % de Mozannar et Sontag. Il exige un seuil fixé à l'avance.
  - **(c) Maximiser la couverture sous contrainte de risque** : bounded-improvement, SGR, Éq. 2 de Yadkori. La couverture devient l'objectif ; les règles se comparent sur la couverture, à risque certifié égal.
  - **(d) Énoncé PAC conjoint** : El-Yaniv et Wiener. Il demande une borne de couverture B_Φ > 0, valable avec la même probabilité 1 − δ que la borne de risque.
- **Le défaut observé est l'analogue exact du rejet total.** La règle « tout valider » obtient « confirmée » : elle a un risque nul et passe la jambe risque. Aucune des littératures lues ne laisse la jambe risque décider seule ; toutes ajoutent une jambe utilité. Le critère actuel n'en a qu'une forme conditionnelle : « plus de validations que B-tout » n'est exigé que face aux baselines qui ne dépassent pas le budget.
- **Traduction statistique la plus fidèle à (d) : une condition d'utilité testée.** La borne inférieure de confiance unilatérale du taux de délégation de B-tout doit dépasser 0, ou un c_min fixé à l'avance. Ce test doit être contrôlé **conjointement** avec la jambe risque : même δ, intégration dans la famille max-T ou partage de δ. L'outillage existe dans LTT : le §2.4 contrôle m risques simultanément, et l'on pourrait déclarer le taux d'abstention comme un « risque » de niveau 1 − c_min. LTT ne présente pas cet usage ; c'est une transposition de ma part.
- **Un « plus de zéro » dans l'échantillon est la forme la plus faible.** Si le rejeu hors ligne compte les validations de manière déterministe, battre « tout valider » sur ce seul compte revient à déléguer au moins une action dans l'échantillon. La littérature exige davantage : une couverture garantie avec probabilité ≥ 1 − δ (El-Yaniv et Wiener) ou un niveau ω fixé à l'avance (bounded-coverage).

### Gaps
- Je n'ai trouvé aucun test confirmatoire publié de « couverture > c_min » ou de « mieux que tout abstenir ». La recherche s'est limitée à une vingtaine de lectures ciblées : cela ne prouve pas qu'il n'en existe pas.
- Aucune de ces littératures ne donne de règle pour choisir c_min. Il est laissé à l'utilisateur : « the user specifies the desired target coverage ».
- Non couverts directement : Chow 1970 et Cortes, DeSalvo et Mohri 2016 (learning with rejection), évoqués seulement à travers d'autres textes.

## Q5. Comment rapporter conjointement une garantie de risque et une revendication d'utilité sans que la politique triviale se qualifie ?

### Takeaway
L'usage dominant énonce la garantie de risque formellement, avec α et δ fixés à l'avance, et l'utilité à côté, empiriquement. Trois exceptions comptent :
- seuls El-Yaniv et Wiener exigent les deux dans **un même** énoncé probabiliste ;
- LTT fournit la règle d'échec explicite (« abstain from returning an RCP ») ;
- Yadkori et al. écrivent noir sur blanc que l'abstention totale a une perte nulle, et qu'une politique « intéressante » doit avoir un faible taux d'abstention.

### Cited Findings
- Modèle de phrase chez Geifman et El-Yaniv : une erreur « can be guaranteed with probability 99.9% », puis « and almost 60% test coverage ». La garantie vient d'abord, la couverture observée ensuite — [Geifman & El-Yaniv 2017](https://arxiv.org/abs/1705.08500)
- El-Yaniv et Wiener : « (r,c) is (efficiently) achievable if … with probability of at least 1 − δ, its coverage is at least c and its risk is at most r » — [El-Yaniv & Wiener 2010](https://www.jmlr.org/papers/volume11/el-yaniv10a/el-yaniv10a.pdf)
- LTT : « The risk tolerance α and error level δ are chosen in advance by the user » ; on choisit parmi les λ valides « the one that maximizes another performance metric » ; si aucun ne passe, « we abstain from returning an RCP » — [LTT](https://arxiv.org/abs/2110.01052)
- RCPS : « Any collection of the sets can be used to control the risk by Theorem 1, but some may produce larger sets than others » ; « controls the risk at the correct level and the sets have reasonable sizes » — [RCPS](https://arxiv.org/abs/2101.02703)
- CRC : la procédure « bounds the risk as desired and gives useful outputs to the end-user » ; la borne inférieure est « not too conservative » — [CRC](https://arxiv.org/abs/2208.02814)
- Yadkori et al. : « A trivial policy that always abstains would result in a zero loss » ; « an interesting policy would also have a small abstention rate » ; résumé : « reliably bounds the hallucination rate » … « maintaining a significantly less conservative abstention rate » — [Yadkori et al. 2024](https://arxiv.org/abs/2405.01563)
- Jin et Candès : « as many test units … as possible, while ensuring the false discovery rate (FDR) is controlled » — [Jin & Candès 2023](https://arxiv.org/abs/2210.01408)
- Traub et al. : le risk@coverage « implies a pre-determined cutoff on the risk or coverage » ; un seuil unique « does not provide a comprehensive evaluation of the system's overall performance » — [Traub et al. 2024](https://arxiv.org/abs/2407.01032)
- Pratiques de rapport de l'utilité :
  - couverture test ponctuelle (Geifman et El-Yaniv 2017) — [source](https://arxiv.org/abs/1705.08500) ;
  - moyenne ± écart-type sur plusieurs entraînements, et borne de Hoeffding de calibration (SelectiveNet) — [source](https://arxiv.org/abs/1901.09192) ;
  - moyenne ± écart-type sur 10 rééchantillonnages, boîtes à 90 % (Yadkori et al.) — [source](https://arxiv.org/abs/2405.01563) ;
  - puissance moyenne sur réplications (Jin et Candès) — [source](https://arxiv.org/abs/2210.01408).

### Inferences
- **Gabarit de rapport qui exclut la politique triviale**, construit à partir des sources ci-dessus :
  - (1) **la garantie de risque** : α et δ fixés à l'avance ; succès = « risque ≤ α » certifié, ou absence de dépassement établi selon le choix de conception ;
  - (2) **l'utilité** : taux de délégation ponctuel, accompagné d'une borne inférieure de confiance unilatérale, testée dans la même famille que (1) ;
  - (3) **un verdict d'échec explicite** (« non confirmé ») si (1) ou (2) manque. C'est le pendant de « abstain from returning an RCP ».
- **Options pour la condition supplémentaire de « confirmée »**, dans l'ordre de ma préférence :
  1. **Condition d'utilité testée.** La borne inférieure unilatérale du taux de délégation de B-tout doit dépasser 0, ou un c_min fixé à l'avance, dans la même famille max-T que la jambe risque. Elle calque le « positive result » d'El-Yaniv et Wiener et le contrôle multi-risque de LTT. **Variante équivalente, plus proche de la structure actuelle :** ajouter « tout valider » comme baseline obligatoire. Comme cette règle ne dépasse jamais le budget, elle ne peut être battue que par « moins de validations humaines que B-tout ». C'est la logique des points de référence du learning to defer (« DM alone » chez Madras, α = 0 chez Raghu, couverture 0 % chez Mozannar et Sontag) et de la « complementary performance » de Bansal. Pour ne pas retomber dans la forme faible décrite en Q4, cet avantage doit être établi statistiquement ou dépasser un seuil fixé à l'avance.
  2. **Restreindre la victoire « par dépassement ».** Dans le modèle bounded-improvement, une règle qui dépasse le budget est *infaisable* : elle est éliminée, pas « battue ». Gagner contre elle devrait exiger que B-tout soit lui-même faisable **et** délègue une part établie. Sinon le gain sur une baseline infaisable est vide.
  3. **Renverser la charge de la preuve sur la jambe risque.**
     - Il s'agirait de certifier « risque ≤ budget » en rejetant H0 : R > budget, comme le font SGR, RCPS et LTT, au lieu de se contenter de l'absence de dépassement établi.
     - Avec un risque **conditionnel aux actions déléguées**, la règle nulle n'est alors pas certifiable, puisqu'elle n'a aucune action déléguée. Une règle timide ne profite plus non plus de la faible puissance du test.
     - Avec un risque **joint** (erreurs déléguées / toutes les actions, le « generalized risk » de Traub), la règle nulle reste à risque 0 et passe. Ce renversement ne suffit donc pas seul.
     - Il change la nature du critère, qui devient plus exigeant : c'est à arbitrer.
  4. **Coût par validation (Chow, γ_defer).** C'est l'option la plus fidèle économiquement. Mais elle impose de chiffrer le rapport entre le coût d'une validation et celui d'une erreur ; Franc et al. jugent cela « difficult ». Elle convient donc mal à un critère confirmatoire fixé à l'avance.
- **Définir explicitement le risque du budget dans le protocole.** Il peut être sélectif, `P(erreur | délégué)`, ou joint, `P(erreur ∧ délégué)`. Ce choix décide à lui seul si la règle nulle passe la jambe risque : elle passe toujours avec le risque joint (« zero loss » chez Yadkori), et n'est jamais certifiable avec le risque sélectif.

### Gaps
- Je n'ai trouvé aucune source qui traite la multiplicité entre une jambe risque et une jambe utilité dans un **plan confirmatoire fixé à l'avance**. Les seules réponses formelles proches sont le contrôle multi-risque simultané de LTT (§2.4) et l'énoncé PAC conjoint d'El-Yaniv et Wiener.
- Aucune pratique de préenregistrement n'a été trouvée dans ces littératures, ni de recommandation sur le choix de c_min.
