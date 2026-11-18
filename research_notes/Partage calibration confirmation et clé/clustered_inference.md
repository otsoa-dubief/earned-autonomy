# Inférence statistique avec essais répétés groupés par tâche, et partage calibration / confirmation

Note de méthode : sources lues en texte intégral = Miller 2024 (arXiv 2411.00640, PDF), Bowyer et al. 2025 (arXiv 2503.01747v3, PDF), MacKinnon-Nielsen-Webb summclust (arXiv 2205.03288v3, PDF). Les autres (Cameron-Gelbach-Miller 2008, guide MNW 2023, Madaan 2024, Korn-Graubard 1998, τ-bench) = résumés ou abstracts seulement ; texte intégral non lu. Les chiffres tirés de formules sont marqués « calcul ». Date de référence : novembre 2026 ; aucune source trouvée postérieure à 2025 sur ce sujet précis.

## 1. Comment la littérature récente sur les évaluations de LLM traite les échantillons répétés par question/tâche ; taille effective

### Takeaway
Miller (2024) donne le cadre : l'unité d'indépendance est la question/tâche, la variance se décompose en variance entre tâches (incompressible) + variance intra-tâche réduite par les répétitions (diviseur K). Au-delà de K modeste, répéter ne sert plus : le plancher est la variance entre tâches. Bowyer et al. (2025) montrent que même l'erreur-type groupée au CLT sous-couvre avec peu de clusters. Aucune des sources ne donne un « effective sample size » chiffré pour 50 essais/tâche ; il se déduit de la formule.

### Cited Findings
- Miller recommande d'« additionner » le groupage : quand les questions viennent en groupes, calculer des erreurs-types groupées ; réduire la variance par rééchantillonnage des réponses ; puissance statistique pour dimensionner. — [Miller 2024, arXiv](https://arxiv.org/abs/2411.00640) (PDF lu : https://arxiv.org/pdf/2411.00640)
- Miller : les questions sont tirées d'une super-population ; Var(µ̂) = Var(s)/n = (Var(x) + E[σ²ᵢ])/n, où Var(x) = variance de la moyenne conditionnelle par question (propriété de la super-population, « immutable »), E[σ²ᵢ] = variance conditionnelle moyenne (réductible). — [Miller 2024, PDF](https://arxiv.org/pdf/2411.00640)
- Miller : avec K réponses par question, Var(sᵢ) = σᵢ²/K ; « once E[σᵢ²]/K ≪ Var(x), increasing K further will have little effect on the standard error of µ̂ ». Exemple binaire avec difficulté U[0,1] : Var(x)=1/12, E[σ²]=1/6, d'où Var(µ̂|K) = Var(µ̂|K=1) × (1+2/K)/3 ; réduction 1/3 à K=2, 1/2 à K=4, 5/9 à K=6, plafond 2/3. — [Miller 2024, PDF](https://arxiv.org/pdf/2411.00640)
- Miller : calculer une erreur-type poolée sur les K·N réponses est « inconsistent » (réponses multiples à la même question non indépendantes). — [Miller 2024, PDF](https://arxiv.org/pdf/2411.00640)
- Miller (éq. 4) : l'erreur-type groupée est une « sliding scale » entre corrélation intra-cluster parfaite (chaque cluster = une seule observation indépendante) et nulle (= non groupée) ; l'ajustement atteint « up to 3X » sur des données réelles de modèles Anthropic (Table 4). Il conseille de rapporter le nombre de clusters avec le nombre de questions. — [Miller 2024, PDF](https://arxiv.org/pdf/2411.00640)
- Bowyer, Aitchison, Ivanova (ICML 2025) : les IC fondés sur le CLT « usually dramatically underestimating uncertainty » sur petits benchmarks ; IC par bootstrap non groupé aussi mal calibrés ; en N=100, un IC CLT nominal 95 % ne couvre que 92,5 %. — [Bowyer et al. 2025](https://arxiv.org/abs/2503.01747) (PDF lu : https://arxiv.org/pdf/2503.01747)
- Bowyer et al., cadre groupé (Fig. 3) : « in a small-data regime, neither simple CLT nor clustered CLT intervals produce correct coverage » ; le bootstrap groupé sous-couvre aussi en petit échantillon ; « To our knowledge there are no readily available frequentist methods, tailored to such clustered data » ; seule la méthode bayésienne à modèle groupé (Beta-binomiale hiérarchique, concentration par cluster) atteint la bonne couverture à toutes tailles testées. Bibliothèque : github.com/sambowyer/bayes_evals. — [Bowyer et al. 2025, PDF](https://arxiv.org/pdf/2503.01747)
- Bowyer et al., cadre i.i.d. : seuls Wilson et l'intervalle crédible bayésien atteignent la couverture nominale en petit N ; Clopper-Pearson est valide mais conservateur (sur-couverture) ; le CLT donne SE=0 quand θ̂ = 0 ou 1. — [Bowyer et al. 2025, PDF](https://arxiv.org/pdf/2503.01747)
- Bowyer et al. : leurs simulations groupées utilisent notamment Nt=5 questions par tâche avec T = 2, 6, 20, 60 clusters (Fig. 11 légende), donc 20 clusters et plus est dans la plage testée ; je n'ai pas extrait le chiffre de couverture pour T=20 précisément. — [Bowyer et al. 2025, PDF](https://arxiv.org/pdf/2503.01747)
- τ-bench : pass^k = probabilité que les k essais indépendants d'une tâche réussissent, moyennée sur les tâches ; estimateur non biaisé moyenne sur tâches de C(c,k)/C(n,k) (n essais, c succès). Le papier rapporte la fiabilité par tâche mais, d'après le résumé lu, pas d'IC groupé. — [τ-bench, arXiv 2406.12045](https://arxiv.org/pdf/2406.12045) (via résumé de recherche ; texte non relu)
- Madaan et al. 2024 : mesurent la variance de graine (écart-type d'un score sur modèles ne différant que par la graine) sur 13 benchmarks et plus de 280 modèles ; item analysis / IRT ne réduisent pas bien la variance. Ne traite pas les essais répétés groupés par tâche d'agents. — [Madaan et al. 2024](https://arxiv.org/abs/2406.10229) (abstract + résumés seulement)

### Inferences
- Design effect/taille effective (calcul, formule standard DEFF = 1+(m−1)ρ ; voir section 3) : pour m=50 essais/tâche, ρ=0,5 → DEFF=25,5 ; n_eff ≈ 2 % du nombre brut d'essais, soit ≈ 1,96 tâches-équivalentes par tâche. Pour ρ=0,9 → DEFF=45,1. Même pour ρ=0,1 → DEFF=5,9. Dès que ρ>~0,05, 50 essais/tâche sont dominés par la variance entre tâches.
- Lecture de Miller dans notre cas : la variance de la moyenne ≈ [Var(x) + E[σ²]/K]/G. Pour des taux d'erreur par type d'action, si les erreurs sont surtout « difficulté de tâche » (Var(x) grand), K=50 ne gagne presque rien sur K=10 ; seul G (nombre de tâches) compte. Haiku à 50 essais n'apporte donc que le plancher de bruit intra-tâche, pas de tâches de plus.
- Le fait que Bowyer et al. ne trouvent aucune méthode fréquentiste groupée correcte en petit échantillon est un avertissement direct pour notre bootstrap groupé B=2000 à 20 tâches (airline) : à confirmer par simulation sur nos propres paramètres (sans toucher aux données de résultats).

### Gaps
- Aucune source trouvée donnant ρ (ICC) typique des erreurs d'agents par tâche ; τ-bench ne le publie pas dans ce que j'ai lu. Il faudra l'estimer sur nos propres épisodes (hors périmètre de cette recherche).
- Texte intégral de Madaan 2024 et de τ-bench non relu ; je ne sais pas si τ-bench ou une variante 2.0 propose un IC groupé.
- Chiffre exact de couverture du bootstrap groupé de Bowyer à T=20 non extrait (graphiques).

## 2. Bootstrap par cluster et inférence robuste aux clusters avec peu de clusters (20, 40, 90)

### Takeaway
La théorie économétrique dit que les tests robustes aux clusters sur-rejettent avec peu de clusters (5-30) et que le bootstrap wild cluster est le remède standard, avec CV3/jackknife comme variantes. Tout ceci est établi pour des régressions linéaires (moyennes, effets) ; je n'ai trouvé aucune validation pour des proportions d'événements rares. Les cas dangereux sont les clusters très inégaux et les « few treated clusters », analogues à nos erreurs concentrées dans quelques tâches.

### Cited Findings
- Cameron, Gelbach, Miller (2008, Review of Economics and Statistics 90(3):414-427) : les tests asymptotiques « can over-reject, however, with few (5-30) clusters » ; les procédures de bootstrap-t groupé donnent un raffinement asymptotique ; le wild cluster bootstrap fonctionne mieux en pratique que le pairs cluster bootstrap ; un taux de rejet de 10 % pour un test nominal 5 % peut être ramené à 5 %. — [NBER t0344](https://www.nber.org/papers/t0344), [RePEc](https://econpapers.repec.org/RePEc:tpr:restat:v:90:y:2008:i:3:p:414-427) (via abstract et extraits de recherche ; texte intégral non lu)
- MacKinnon, Nielsen, Webb (2023, Journal of Econometrics 232(2):272-299), « Cluster-robust inference: A guide to empirical practice » : le CRVE peut mal fonctionner avec peu de clusters ; le wild cluster bootstrap fait souvent, pas toujours, mieux. — [RePEc](https://econpapers.repec.org/RePEc:eee:econom:v:232:y:2023:i:2:p:272-299) (notice ; texte intégral non lu, accès payant)
- MNW, texte de leur papier compagnon summclust (lu) : deux situations où les tests robustes aux clusters sur-rejettent « to an extreme extent, even when G is not small » : (1) un ou quelques clusters bien plus gros que les autres, (2) les observations « traitées » appartiennent à quelques clusters seulement. — [MacKinnon, Nielsen, Webb, summclust, arXiv 2205.03288](https://arxiv.org/abs/2205.03288) (PDF lu : https://arxiv.org/pdf/2205.03288)
- Même source : « inferences based on either the t(G−1) distribution or the WCR bootstrap are likely to be completely unreliable » dans le cas de peu de clusters traités ; quand G est assez grand et les clusters homogènes, WCR et CV1+t(G−1) sont proches ; « When they differ noticeably, neither should be relied upon without further investigation ». — [arXiv 2205.03288](https://arxiv.org/pdf/2205.03288)
- Même source : recommandation de calculer CV3 ou CV3J (jackknife par cluster) « essentially all the time » car plus fiables que CV1 avec des clusters hétérogènes ; recommandation forte de calculer à la fois WCR-C (classique) et WCR-S (variante « score », MNW 2023b) quand CV1 et CV3 divergent, et en cas de désaccord, privilégier WCR-S. — [arXiv 2205.03288](https://arxiv.org/pdf/2205.03288)
- Même source : propose le « nombre effectif de clusters » G* (Carter, Schnepel, Steigerwald) comme diagnostic ; exemple où G*(0)=5,5 et G*(1)=1,4 pour un G=72 nominal. — [arXiv 2205.03288](https://arxiv.org/pdf/2205.03288)
- Simulation (blog R, non évaluée par les pairs) : IC wild cluster bootstrap proches de 95 % pour 5-10 clusters ; pour G=50 et G=100, wild bootstrap et Satterthwaite équivalents pour tous les ICC ; pour 3≤G≤10, Satterthwaite légèrement meilleur. Résultats pour variable continue. — [r-bloggers 2022](https://www.r-bloggers.com/2022/01/a-%f0%9f%90%b4-race-the-wild-cluster-bootstrap-vs-satterthwaite-corrected-sandwich-estimators-when-the-number-of-clusters-is-small/) (source secondaire)
- MacKinnon-Webb (few treated clusters) : le WCR restreint sous-rejette fortement, le non restreint sur-rejette fortement ; le sous-cluster wild bootstrap marche bien sous conditions de tailles similaires. — [résumé de recherche, résultats non primaires](https://carleton.ca/economics/wp-content/uploads/Webb_Abstract.pdf) (abstract)

### Inferences
- Le wild cluster bootstrap est conçu pour un modèle de régression avec résidus ; appliqué à une moyenne de variable binaire (ou taux par type d'action) il revient à un bootstrap des signes des résidus par cluster (Rademacher/Webb). Avec 20 clusters, Rademacher a 2^20 ≈ 10^6 poids distincts : correct ; avec <12 clusters on préfère le poids de Webb à six points (point connu dans la littérature, non vérifié ici sur source lue).
- Notre plan (bootstrap de type « pairs » stratifié par tâche, percentile + normal, union) n'est pas le wild bootstrap-t recommandé : le percentile pairs bootstrap sous-couvre en petit G (cohérent avec Bowyer sur le bootstrap groupé). L'union percentile+normal élargit, ce qui compense en partie ; mais cela n'est pas validé par une source. À simuler.
- Fiabilité par nombre de clusters (jugement, non sourcé comme seuil) : la littérature place le problème à 5-30 clusters ; 20 tâches (airline en 50/50) est dans cette zone ; 40-45 est en lisière ; ≈90 (banking_knowledge 77 → 38-39 par moitié, retail 91 → 45-46 par moitié, WorkBench 552 → 276) est confortable pour les moyennes, mais pas démontré pour des taux rares.
- Risque spécifique « few treated clusters » transposé : si les erreurs de chaque type d'action se concentrent dans 1-3 tâches, c'est l'analogue d'une poignée de clusters « traités » ; les intervalles bootstrap deviennent alors peu fiables. Un diagnostic de type G* ou d'influence par tâche (leave-one-task-out) est recommandé par analogie avec summclust.

### Gaps
- Aucune source primaire lue ne teste le bootstrap groupé ou wild sur proportions d'événements rares (taux ≪ 1 %) avec 20-90 clusters. Le résumé de recherche n'a rien trouvé sur ce point.
- Texte intégral du guide MNW 2023 (JoE) et de CGM 2008 non lu : pas de tableau de taux de rejet par G.

## 3. Arbitrage nombre de tâches vs répétitions ; design effect ; ICC ; rendements décroissants

### Takeaway
Le design effect 1+(m−1)ρ, formule standard d'essais en grappes, montre que la précision est bornée par le nombre de clusters : n_eff → G/ρ quand m→∞. Avec 50 essais par tâche, quasi tout le gain vient des 10 premiers essais si ρ n'est pas minuscule ; mieux vaut des tâches de plus que des essais de plus.

### Cited Findings
- DEFF = 1 + (m − 1)ρ (m taille moyenne de cluster, ρ ICC) ; taille effective = n/DEFF ; ρ estimé par (DE−1)/(m−1). — [MetricGate, cluster sampling design](https://metricgate.com/docs/cluster-sampling-design/) et [plan d'analyse GSK, ClinicalTrials.gov](https://cdn.clinicaltrials.gov/large-docs/20/NCT03688620/SAP_001.pdf) (sources secondaires ; la formule elle-même est standard, Kish)
- Clusters de tailles inégales : 1 + ((CV²+1)m − 1)ρ (Eldridge et al. 2006). — [MetricGate, cluster RCT](https://metricgate.com/calculator/sample-size-cluster-rct-icc) (source secondaire)
- Même plan GSK : ICC et DE « not estimated when the proportion is 0% or 100% » (cas à zéro événement). — [SAP GSK](https://cdn.clinicaltrials.gov/large-docs/20/NCT03688620/SAP_001.pdf)
- Miller : la variance entre questions Var(x) est une propriété de la super-population, non réductible par rééchantillonnage ; augmenter n (questions) est « the simplest way » de réduire la variance. — [Miller 2024, PDF](https://arxiv.org/pdf/2411.00640)

### Inferences
- Calcul : Var(moyenne) ∝ [ρ + (1−ρ)/m]/G, d'où le rendement décroissant. Pour ρ=0,3 : m=1 → 1,00 ; m=5 → 0,44 ; m=10 → 0,37 ; m=50 → 0,314 ; plafond (m→∞) 0,30. Passer de 10 à 50 essais gagne ~15 % de variance ; ajouter 25 % de tâches en gagne 20 %. (ρ=0,3 hypothétique, à estimer.)
- Pour les rôles Haiku (50 essais airline/retail) : excès d'effort sur les répétitions ; pour Sonnet/Opus (10 essais) : déjà presque au plafond si ρ ≥ 0,2. Dans notre cas, le nombre de tâches (40, 91, 77, 552) fixe la précision, pas le nombre de parties.
- ρ est probablement très différent selon le type d'action : une action « rare » concentrée dans quelques tâches a ρ élevé, une action fréquente et diffuse a ρ faible. À estimer par type d'action sur les épisodes de calibration.

### Gaps
- Pas de source primaire (biostatistique) lue directement (Donner & Klar, Kish, Eldridge) ; formules citées via sources secondaires mais standard.
- Aucune valeur publiée d'ICC pour des erreurs d'agents LLM par tâche.

## 4. Intervalles pour taux d'erreur rares (zéro ou peu d'erreurs) sous groupage

### Takeaway
Pour un taux rare, Clopper-Pearson (exact, conservateur) ou Wilson (bonne couverture selon Bowyer) s'appliquent à des essais i.i.d. ; sous groupage, la méthode publiée est Korn-Graubard : Clopper-Pearson avec taille effective (n/DEFF). La règle de trois (≈3/n à 95 %) se transpose avec n_eff.

### Cited Findings
- Korn & Graubard (1998, Survey Methodology 23:193-201) : modification simple de l'intervalle binomial exact pour données d'enquête complexes avec peu de positifs ; ajustement par taille effective ; meilleure couverture que normal, logit et Poisson dans leurs simulations limitées. Implémenté dans R `survey::svyciprop(method="beta")` et Stata `kg_nchs`. — [Statistics Canada](https://www150.statcan.gc.ca/n1/en/catalogue/12-001-X19980024356) (abstract ; formules non lues)
- Protocole clinique : borne exacte binomiale × design effect (ICC par ANOVA, formule d'Eldridge) pour limite supérieure à zéro événement ; autre protocole : Clopper-Pearson modifié pour clusters citant Korn-Graubard. — [SAP NCT03278067](https://cdn.clinicaltrials.gov/large-docs/67/NCT03278067/SAP_001.pdf), [SAP NCT03961009](https://cdn.clinicaltrials.gov/large-docs/09/NCT03961009/SAP_001.pdf) (via extraits de recherche)
- Règle de trois : 0 événement sur n essais indépendants → borne haute ≈ 3/n à 95 % (2,996/n exact) ; approximation moins fiable avec peu d'événements. — [Statology](https://www.statology.org/a-concise-guide-to-the-statistical-rule-of-three/) (secondaire)
- Bowyer et al. : Clopper-Pearson sur-couvre ; Wilson et bayésien OK en i.i.d. ; le bootstrap non paramétrique est mal calibré en petit N et, avec zéro erreur, un bootstrap simple dégénère (θ̂=0 → toutes les ré-échantillons à 0 ; le CLT donne SE=0). — [Bowyer et al. 2025, PDF](https://arxiv.org/pdf/2503.01747)
- Jeffreys : non trouvé comme source distincte ; Bowyer et al. discutent des priors Beta(1,1) pour leur méthode bayésienne, pas de Jeffreys en particulier d'après l'extraction faite.

### Inferences
- Avec zéro erreur observée, l'intervalle bootstrap est [0,0] : il ne dit rien. Seul Clopper-Pearson (ou équivalent) donne une borne non nulle. C'est précisément le cas qui fait passer ou non un budget très serré. Notre « union bootstrap ∪ CP » retombe donc sur CP en zéro erreur ; or CP calculé sur le nombre brut d'écritures ignore le groupage et est trop optimiste (trop étroit) ; il faut le calculer sur n_eff = n/DEFF (méthode Korn-Graubard) ou, plus simplement, au niveau tâche.
- Ordre de grandeur des budgets (calcul) : budget 0,005 excès d'erreurs pour 100 écritures = 5×10⁻⁵ par écriture. Zéro erreur et règle de trois → il faut n_eff ≈ 3/(5×10⁻⁵) = 60 000 écritures indépendantes. Budget 0,05/100 → 6 000 ; budget 0,5/100 → 600. Avec DEFF de 5 à 25, cela monte de 5× à 25× en écritures brutes. Il est probable que le budget 0,005 ne puisse être certifié par aucun partage, à vérifier avec le nombre réel d'écritures par type d'action (non consulté).
- Alternative au niveau tâche : la proportion de tâches avec au moins une erreur d'un type donné a pour borne zéro-événement 3/G. À G=20 → 15 % ; G=40 → 7,5 % ; G=90 → 3,3 % ; G=276 → ≈ 1,1 % (calcul). Cela donne un plancher de résolution, indépendant du nombre d'essais par tâche.

### Gaps
- Pas de source lue sur Wilson/Jeffreys sous groupage ; seule piste : Korn-Graubard (formule non lue).
- Pas de source sur le bootstrap groupé stratifié avec zéro événement.
- Pas de source sur « erreurs en excès » (différence à un taux de base) avec clusters.

## 5. Partage des réserves 40 / 91 / 77 / 552 tâches en deux ensembles

### Takeaway
Airline est de loin le plus affamé en clusters : 20 tâches par moitié est dans la zone 5-30 clusters où l'inférence groupée standard échoue et où Bowyer et al. constatent un sous-couvrage même groupé. Aucun seuil universel n'existe dans les sources ; la littérature économétrique situe le problème autour de 30 clusters et moins. Le partage 50/50 est probablement sous-optimal pour l'ensemble de confirmation.

### Cited Findings
- Seuil 5-30 clusters comme zone de sur-rejet des tests asymptotiques. — [Cameron, Gelbach, Miller 2008](https://www.nber.org/papers/t0344) (via extraits)
- Le wild cluster bootstrap est jugé fiable pour 5-10 clusters en simulation continue (blog) mais mal en dessous de 11 selon une autre source ; désaccord entre sources secondaires. — [r-bloggers](https://www.r-bloggers.com/2022/01/a-%f0%9f%90%b4-race-the-wild-cluster-bootstrap-vs-satterthwaite-corrected-sandwich-estimators-when-the-number-of-clusters-is-small/)
- Bowyer et al. : en petit-N groupé, aucune méthode fréquentiste testée n'est valide ; le bayésien hiérarchique l'est. — [Bowyer et al. 2025](https://arxiv.org/pdf/2503.01747)
- Pas de source trouvée sur l'allocation optimale d'un petit lot de tâches entre ensemble de calibration et ensemble de confirmation avec cluster bootstrap, ni sur l'effet de la stratification sur la couverture du bootstrap groupé.

### Inferences
- Plus affamé : airline (40 tâches). 50/50 → 20 + 20 ; retail 91 → ≈ 45 + 46 ; banking_knowledge 77 → ≈ 38 + 39 ; WorkBench 552 → 276 + 276 (6 fichiers : attention, si le groupage est aussi par fichier, c'est un niveau supérieur à 6 clusters, à traiter à part ; non étudié).
- Seuil défendable (jugement fondé sur : zone 5-30 de CGM, et nos budgets rares) : viser au moins 30-40 tâches par ensemble pour que le bootstrap soit crédible, et valider par simulation ; en dessous de ~25, ne pas annoncer de verdict primaire fondé sur le bootstrap seul. Pour airline, cela veut dire qu'un partage ne peut pas satisfaire les deux ensembles : option : tâches airline en un seul ensemble (confirmation), sans calibration propre, ou calibration par pooling avec retail si les types d'action sont communs ; à décider par Otsoa.
- Asymétrie : l'ensemble de calibration n'a besoin que d'estimer des taux (erreur de précision acceptable, tolère plus d'incertitude) tandis que l'ensemble de confirmation porte le verdict avec bornes supérieures contre un budget : la confirmation devrait recevoir la plus grosse part des clusters (ex. 30/70 ou 40/60) quand G est petit. Argument de jugement, non sourcé.
- Stratification : stratifier le partage par difficulté/type d'action (par ex. répartir les tâches à erreurs connues dans les deux moitiés) réduit la variance entre moitiés ; sur le bootstrap, stratifier par domaine évite qu'un domaine disparaisse d'un rééchantillon. Aucune source lue n'en quantifie le gain ; avertissement : stratifier le bootstrap « par tâche » (tâche = strate) n'a pas de sens, car chaque tâche est le cluster ; la stratification est au niveau des groupes de tâches.
- Diagnostic à ajouter au plan (inspiré de summclust) : influence par tâche (leave-one-task-out) et nombre effectif de clusters G*, pour détecter qu'une tâche domine un taux d'erreur.
- Option plus robuste à G petit : IC bayésien hiérarchique de Bowyer (seule méthode validée en petit N groupé dans les sources) ou wild cluster bootstrap-t / CV3 jackknife en complément de l'union percentile+normal ; à comparer par simulation sur des données synthétiques, jamais sur les résultats réels des réserves.

### Gaps
- Aucune règle publiée de « nombre minimal de tâches par ensemble » pour un bootstrap groupé de taux rares.
- Pas de littérature trouvée sur le partage calibration/confirmation spécifique aux évaluations d'agents LLM.
- Non vérifié : si Bowyer et al. couvrent des taux ≪ 1 % ; leurs simulations tirent θ ~ Beta(1,1), donc principalement des taux moyens.
