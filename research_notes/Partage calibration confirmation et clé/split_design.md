# Partage de la réserve entre calibration et confirmation scellée (Q1)

Réserve : airline 40 tâches, retail 91, banking 77, WorkBench 552. La règle B-tout est gelée et n'a aucun paramètre ajusté. La calibration ne sert donc pas à entraîner un modèle. Elle sert à estimer des « vérités » (taux d'erreur réels) qui alimentent l'oracle, les configurations « déléguables » et l'écart de délégation.

Limite de méthode : les PDF (Anderson-Magruder, Fafchamps-Labonne, Joseph) n'ont pas pu être lus en texte brut par l'outil de lecture. Les chiffres d'Anderson-Magruder viennent d'un billet de blog de la Banque mondiale (secondaire). Les résumés d'abstracts sont cités tels quels. Les calculs numériques de ce fichier sont les miens (marqués « Inférences »).

## Q-A. Que dit la littérature sur la part à allouer à l'exploration/calibration versus la confirmation ?

### Takeaway
Aucune source ne donne de formule applicable telle quelle à notre cas. Les règles existantes (√p:1 de Joseph, 40-80 % d'entraînement de Dobbin-Simon, 50/50 de Fafchamps-Labonne, 30/70 d'Anderson-Magruder) optimisent un arbitrage « ajuster un modèle puis le tester ». Chez nous la règle est gelée, donc la logique d'« entraînement » disparaît. Ce qui reste est un arbitrage entre deux précisions : celle des taux estimés et celle du verdict primaire.

### Cited Findings
- Anderson & Magruder (NBER w23544, 2017) comparent le plan d'analyse préenregistré (PAP) à un partage exploration/confirmation. Pour des hypothèses homogènes, leur méthode de partage améliorée obtient « 90% of the rejections of the optimal PAP » sans préenregistrement. Pour des hypothèses hétérogènes (priorités différentes), un hybride préspécifie les hypothèses à fort poids et teste les autres par partage. — [NBER w23544](https://www.nber.org/papers/w23544)
- Version hybride décrite dans le billet de la Banque mondiale : l'hypothèse principale est testée sur l'échantillon entier. Un échantillon exploratoire d'environ 30 % sert à cribler les hypothèses secondaires avec un seuil laxiste (|t| ≈ 1,2). Le test secondaire porte sur les 70 % restants, en ne testant que le signe vu dans la première part. Chiffres du billet : puissance de l'hypothèse principale 0,80 en échantillon entier, 0,71 avec Bonferroni, 77,6 % avec l'hybride. Puissance du test secondaire 0,65. Le billet ne donne pas de règle générale pour choisir le ratio. — [Banque mondiale, Development Impact](https://blogs.worldbank.org/en/impactevaluations/trouble-pre-analysis-plans-try-these-three-weird-tricks) (secondaire, à recouper avec le [PDF de l'auteur](https://anderson.are.berkeley.edu/pdf/split-sample.pdf))
- Fafchamps & Labonne (Political Analysis 25(4), 2017) : un tiers indépendant tire au hasard un échantillon d'entraînement et un échantillon de test. L'analyse exploratoire se fait sur le premier, puis la méthode est appliquée une seule fois au second. Le billet de la Banque mondiale rapporte un partage en deux moitiés, avec une puissance de 0,86 par moitié et 0,74 au total contre 0,495 sans partage (cas de recherche d'hypothèses multiples). Les auteurs reconnaissent que le coût principal est la perte de puissance et ne recommandent pas la méthode quand l'échantillon est petit et cher. — [Cambridge Core](https://www.cambridge.org/core/journals/political-analysis/article/using-split-samples-to-improve-inference-on-causal-effects/6727EF63175DF517BF56EC64EFF3E807), [NBER w21842](https://www.nber.org/papers/w21842), [Banque mondiale](https://blogs.worldbank.org/en/impactevaluations/trouble-pre-analysis-plans-try-these-three-weird-tricks)
- Joseph (2022, Statistical Analysis and Data Mining 15(4)) : ratio entraînement:test optimal = √p : 1, où p est le nombre de paramètres d'une régression linéaire qui décrit bien les données. La part de test vaut 1/(√p+1). Critère : minimiser l'espérance de l'erreur quadratique d'estimation sur tous les partages possibles. L'auteur le oppose à la règle 80:20, qui reste une heuristique. — [arXiv 2202.03326](https://arxiv.org/abs/2202.03326), [résumé détaillé (DeepAI)](https://deepai.org/publication/optimal-ratio-for-data-splitting)
- Dobbin & Simon (BMC Medical Genomics 4:31, 2011) : le partage optimal minimise l'erreur quadratique de l'estimation de précision par rapport au classifieur construit sur toutes les données. Cette erreur se décompose en variance de la précision, variance binomiale du test et biais carré dû à l'entraînement sur moins de cas. Sur les conditions simulées, la part d'entraînement optimale se situe entre 40 % et 80 %. Plus n est petit, plus on met en entraînement. Quand la précision atteignable est proche de 50 %, la majorité va au test. 2/3 d'entraînement est quasi optimal pour n ≥ 100 et précision ≥ 85 %. En dessous de 60 % de précision, 1/2 vaut mieux. À n = 50, ils recommandent le rééchantillonnage car un test de 10 cas est trop petit. — [PMC3090739](https://pmc.ncbi.nlm.nih.gov/articles/PMC3090739)
- Guyon (1997, rapport AT&T Bell Labs, « A Scaling Law for the Validation-Set Training-Set Size Ratio ») : cité seulement de seconde main. Un article le résume ainsi : Guyon 1997 et 1998 cherchent à minimiser l'erreur de test pour des étiquettes discrètes et obtiennent une solution en O(m) pour la taille du test. Je n'ai pas pu lire le rapport. — [arXiv 2112.05977, bibliographie](https://arxiv.org/pdf/2112.05977) et [arXiv 2102.06701](https://arxiv.org/pdf/2102.06701v2) (références secondaires)
- Conformal fractionné (Angelopoulos & Bates, « A Gentle Introduction to Conformal Prediction ») : la garantie de couverture marginale vaut pour tout n de calibration. Sur un jeu de calibration fixé, la couverture réelle varie. Les auteurs concluent qu'environ n = 1000 points de calibration suffisent « pour la plupart des usages ». — [arXiv 2107.07511](https://arxiv.org/pdf/2107.07511)
- Loi de la couverture (Vovk 2012), rapportée par un article secondaire : 1−α̂ ~ Beta(n_cal+1−l, l) avec l = ⌊(n_cal+1)α⌋. L'écart-type de couverture décroît donc en 1/√n_cal. — [arXiv 2601.16636](https://arxiv.org/pdf/2601.16636) (secondaire, à vérifier contre Vovk 2012)

### Inferences
- Aucune de ces règles ne s'applique directement : Joseph et Dobbin-Simon supposent un modèle ajusté sur la part « entraînement », alors que B-tout n'a aucun paramètre. Le terme de biais d'entraînement (moins de données = modèle moins bon) est nul chez nous. Le seul coût d'une part calibration petite est le bruit sur l'oracle. Le seul coût d'une part confirmation petite est la précision du verdict. Il n'y a donc pas d'optimum « à la Joseph » à chercher.
- Le cadre d'Anderson-Magruder est le plus proche conceptuellement : une partie sert à décider ce qui sera testé, l'autre à tester. Leur logique « hybride » (garder l'hypothèse principale sur l'échantillon entier) suggère une piste : le verdict primaire de B-tout, qui ne dépend d'aucun paramètre, pourrait être calculé sur toutes les tâches si la calibration n'influençait pas le verdict. Mais ici la calibration définit les « configurations déléguables » qui agrègent le critère d'utilité, donc l'indépendance est nécessaire pour ce critère (voir Q-D).
- Le conformal fournit une échelle utile : le bruit d'une estimation de quantile ou de taux décroît en 1/√n_cal. Les ~1000 points d'Angelopoulos-Bates sont hors de portée en unités indépendantes (tâches) pour airline, banking et retail. WorkBench seul s'en approche.

### Gaps
- Je n'ai pas pu lire les PDF d'Anderson-Magruder, Fafchamps-Labonne, Joseph (échec de l'extraction PDF). Les chiffres d'Anderson-Magruder passent par un billet de blog.
- Guyon 1997 : rapport introuvable en ligne, forme exacte de la loi non vérifiée.
- Aucune source trouvée donnant une règle de partage quand le prédicteur n'a aucun paramètre ajusté et que la calibration définit seulement une vérité de référence.

## Q-B. Unité du partage quand les observations sont groupées (rejeux répétés d'une même tâche) et stratification

### Takeaway
Partager en dessous du niveau de la grappe (par rejeu) place les mêmes tâches des deux côtés et gonfle l'optimisme. Le partage par tâche est la pratique recommandée. La littérature sur la stratification de petites strates est maigre dans ce que j'ai trouvé.

### Cited Findings
- Roberts et al. (Ecography 40(8):913-929, 2017) : quand la dépendance est ignorée, l'erreur prédictive est « sérieusement sous-estimée ». La dépendance des données persiste dans les résidus. Les auteurs recommandent la validation croisée par blocs partout où il y a une structure de dépendance, même si aucune corrélation n'est visible dans les résidus du modèle. Mise en garde : le blocage restreint les plages de prédicteurs disponibles à l'entraînement, ce qui peut gonfler l'erreur d'interpolation. — [Roberts et al. 2017 (PDF)](https://www.biometrie.uni-freiburg.de/mitarbeiter/dormann/roberts-et-al-2017-ecography.pdf), [notice](https://pred.uni-regensburg.de/id/eprint/1455/)
- Kapoor & Narayanan (Patterns, 2023, « Leakage and the reproducibility crisis in ML-based science ») : une fuite d'information (leakage) touche au moins 294 articles dans 17 disciplines selon un résumé, 329 articles selon une autre source (les deux chiffres divergent, à vérifier dans l'article). Dans l'étude de cas sur la guerre civile, une fois les fuites corrigées, les modèles ML ne font pas substantiellement mieux que des régressions logistiques anciennes. — [PMC10499856](https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856), [arXiv 2207.07048](https://arxiv.org/abs/2207.07048v1)
- Exemple chiffré, hors domaine et non revu par les pairs : sur des données post-reconstruction du LCA, la CV stratifiée à 10 plis donne une précision de 0,91 contre 0,66 en laissant un participant de côté. Les auteurs l'attribuent à une fuite au niveau du sujet. — [JMIR Preprints 87728](https://preprints.jmir.org/preprint/87728)
- Le partage groupé (group k-fold) garde toutes les lignes d'un sujet dans un seul pli, donc l'estimation reflète des groupes inédits et non des lignes inédites. Ne corrige pas le biais de sélection d'hyperparamètres. — [MetricGate (doc commerciale, secondaire)](https://metricgate.com/docs/group-k-fold-cv/)
- Validation croisée de Chernozhukov et al. : pour des données i.i.d., un partage aléatoire simple suffit. Le partage par blocs ou grappes s'applique aux séries temporelles et aux données groupées. — [résumé secondaire (EmergentMind)](https://www.emergentmind.com/topics/cross-fitting-sample-splitting)

### Inferences
- Nos 50 rejeux d'une même tâche (airline, retail) sont des mesures répétées d'une grappe. Les verdicts de deux rejeux d'une même tâche sont corrélés (même instance, mêmes pièges). Partager par rejeu mettrait la même tâche dans les deux parts : le taux « vrai » estimé en calibration contiendrait l'information propre aux tâches de la confirmation. L'oracle serait alors artificiellement proche de la réalité de la confirmation, ce qui rend la mesure de l'« écart de délégation » trop petite. Partager par tâche est cohérent avec la recommandation de Roberts et al.
- Le bootstrap par grappes (tâche) du verdict primaire est cohérent avec le partage par tâche : l'unité de rééchantillonnage et l'unité de partage sont identiques.
- La stratification par environnement est quasi forcée (les trois environnements ont des niveaux d'erreur très différents). Stratifier par fichier WorkBench paraît raisonnable (6 fichiers, tailles à vérifier). Aucune source ne fixe un seuil de taille de strate. Avec 40 tâches (20 par part) une strate très petite aurait un partage presque arbitraire : tirage aléatoire exact et fixé à l'avance avec graine publiée, pas d'ajustement après coup.

### Gaps
- Pas de source trouvée sur la stratification de strates très petites (≤ 10 unités) dans un partage calibration/confirmation.
- Pas de source quantifiant l'optimisme dû à des rejeux répétés d'agents LLM sur la même tâche. Les sources lues portent sur sujets, sites ou espèces.

## Q-C. Alternatives à un partage unique : cross-fitting, estimation honnête, partages répétés

### Takeaway
Le cross-fitting avec permutation des rôles est standard pour récupérer l'efficacité perdue par le partage. Il demande que chaque part soit tour à tour « calibration » et « confirmation », ce qui entre en tension avec une confirmation scellée à usage unique. Les partages répétés (Meinshausen et al.) ajoutent une agrégation conservatrice et diluent la notion de « verdict unique ».

### Cited Findings
- Chernozhukov et al. (Econometrics Journal 2018, DML) : le partage en K plis (cross-fitting) ajuste les nuisances sur K−1 plis et évalue le moment sur le pli retenu. En pratique on fait tourner les partages et on moyenne sur plusieurs partitions aléatoires pour réduire la perte d'efficacité. Pas de règle formelle sur K trouvée (5 ou 10 évoqués, un logiciel prend 2 par défaut). — [alphaxiv 1608.00060](https://alphaxiv.org/abs/1608.00060), [résumé secondaire](https://www.emergentmind.com/topics/cross-fitting-sample-splitting)
- Athey & Imbens (PNAS 2016) : estimation « honnête » = un échantillon construit la partition, un autre estime l'effet par sous-groupe. Dans leurs simulations, l'estimation honnête donne une couverture nominale (IC à 90 %), contre 74-84 % pour les approches non honnêtes. Coût : modèle estimé sur un échantillon plus petit, MSE accrue d'environ 7-22 % pour la méthode préférée. Une critique de 2025 (Cattaneo et coauteurs) juge ces estimateurs possiblement imprécis et invalides pour des IC par sous-groupe. — [arXiv 1504.01132](https://www.arxiv.org/pdf/1504.01132), [PMC4941430](https://pmc.ncbi.nlm.nih.gov/articles/PMC4941430), [critique 2025](https://arxiv.org/html/2509.11381v1)
- Meinshausen, Meier & Bühlmann (JASA 104, 2009) : le jeu est divisé en deux moitiés plusieurs fois. Sélection sur une moitié, p-values classiques sur l'autre. Agrégation par quantiles empiriques des p-values ajustées divisées par γ. La règle médiane (2 × p médiane) est jugée conservatrice. — [arXiv 0811.2177](https://arxiv.org/pdf/0811.2177), [diapositives Bühlmann](https://stat.ethz.ch/education/semesters/ss2015/CompStat/PB-highdim-Pval-etc.pdf)
- Data fission (Leiner, Duan, Wasserman, Ramdas, JASA 2023) et data thinning (Neufeld et al.) : alternatives qui scindent une observation en deux parties indépendantes. Garanties exactes pour des familles paramétriques précises (gaussien pour la fission). Critiquées pour leurs hypothèses paramétriques fortes. — [arXiv 2112.11079](https://arxiv.org/pdf/2112.11079), [arXiv 2405.13591](https://arxiv.org/html/2405.13591v3)
- Holdout réutilisable (Dwork et al., 2015) : un holdout fixe perd sa validité quand l'analyste le réinterroge de façon adaptative. Une lecture via un mécanisme différentiellement privé permet un usage plus large, de l'ordre du carré de la taille du holdout selon la théorie. — [arXiv 1506.02629](https://arxiv.org/pdf/1506.02629)

### Inferences
- Compatibilité avec un holdout chiffré et préenregistré : je n'ai trouvé aucune source sur cross-fitting et confirmation scellée ensemble. Raisonnement propre : comme B-tout est gelée et sans paramètre, rejouer la règle sur la moitié « calibration » ne l'adapte à rien. L'unique couplage est l'oracle (taux estimés ailleurs). Un cross-fitting à deux plis serait donc faisable : taux de la moitié A estimés sur la B et inversement, règle rejouée une fois sur chaque moitié, résultats poolés. Cela double le volume de tâches du verdict primaire. Mais c'est un schéma différent d'une confirmation scellée : les deux moitiés sont vues pour calibrer, il faut figer à l'avance la procédure complète (définition des déléguables, seuil, graine), et le verdict n'est plus « une seule lecture d'un jeu inconnu ». Tout le poids de la rigueur passe sur la préenregistrement de la procédure.
- Le doublement est réel mais pas complet : la variance du verdict poolé dépend aussi de la corrélation entre les deux estimations d'oracle. Aucune source n'a quantifié cela dans un cas comme le nôtre.
- Partages répétés à la Meinshausen : utiles pour réduire le « hasard du tirage » (loterie de p-values), mais l'agrégation est conservatrice et le résultat n'est plus un verdict unique sur un jeu scellé. À réserver à une analyse de robustesse, pas au verdict primaire.
- L'estimation honnête d'Athey-Imbens correspond exactement à notre séparation : une moitié choisit/définit, l'autre estime. Leur coût de 7-22 % de MSE donne un ordre de grandeur de la perte de précision d'un partage honnête.

### Gaps
- Aucune source trouvée sur la compatibilité cross-fitting et holdout préenregistré/chiffré.
- Aucun chiffre trouvé sur le gain exact d'efficacité d'un cross-fitting à 2 plis avec une cible de type « taux vs seuil ».

## Q-D. Biais de l'estimation de la « vérité » sur les mêmes données que l'évaluation (malédiction du vainqueur, sélection, régression vers la moyenne)

### Takeaway
Classer les types d'actions selon leur taux estimé (au-dessus ou en dessous du seuil) puis évaluer sur les mêmes données gonfle le résultat : on retient les cas où le bruit est favorable. Une calibration indépendante élimine ce biais pour des observations indépendantes, au prix de données écartées.

### Cited Findings
- Le problème : choisir l'option qui semble la meilleure sur les données puis rapporter l'estimation sur les mêmes données la gonfle. Le remède usuel est de choisir la cible sur une partie et d'estimer sur une autre. Cela garantit l'absence de biais de sélection pour des observations indépendantes, mais jette des données. Des estimateurs sans biais médian conditionnels à la sélection peuvent dominer le partage. — [IFS CWP731818](https://www.ifs.org.uk/sites/default/files/output_url_files/CWP731818.pdf), [NBER w25456](https://www.nber.org/system/files/working_papers/w25456/revisions/w25456.rev1.pdf), [arXiv 1910.03788](https://web3.arxiv.org/pdf/1910.03788) (résumés via recherche, articles non lus en entier)
- Un article de 2026 distingue le biais par rapport à la vraie moyenne de l'option choisie et par rapport à la vraie meilleure option. La meilleure correction dépend de l'objectif du décideur. — [arXiv 2605.18887](https://arxiv.org/pdf/2605.18887)
- Athey-Imbens : couverture nominale en estimation honnête contre 74-84 % sinon (voir Q-C). — [PMC4941430](https://pmc.ncbi.nlm.nih.gov/articles/PMC4941430)
- Même avec un partage groupé, un biais de sélection subsiste si l'on règle ou choisit sur le jeu d'évaluation ; il faut une CV imbriquée. — [MetricGate](https://metricgate.com/blogs/cross-validation-pitfalls) (secondaire)

### Inferences
- Pour nous, deux usages diffèrent. (1) Oracle et classement des types selon le seuil : l'erreur d'estimation d'un taux proche du seuil fait mal classer un type. Si l'oracle est estimé sur les tâches de la confirmation, les types « au-dessus du seuil » par chance de tirage seront ceux où la règle paraît bonne : biais optimiste. L'indépendance de la calibration le supprime. (2) Définition des configurations déléguables qui agrègent le critère d'utilité : même logique.
- Régression vers la moyenne : je n'ai pas de source qui la traite sous cet angle. Raisonnement : les types classés « délégables » sur un petit échantillon ont, en moyenne, un vrai taux plus mauvais que celui observé. Une calibration trop petite classe donc trop de types comme déléguables, et l'écart de délégation (mesure descriptive) est biaisé vers le bas ou vers le haut selon le sens de l'erreur de classement. L'amplitude dépend de la masse de configurations proches du seuil. Je n'ai aucun ordre de grandeur sourcé.
- Les seuils d'erreur du plan (0,5 / 0,05 / 0,005 dommages par 100 actions) sont très bas. Avec peu de tâches, un taux vrai de 0,005 n'est pas distinguable de 0 : la calibration ne peut guère classer au niveau « haut enjeu ». Un calcul de ma part : pour estimer un taux autour de 0,5 % avec une précision relative de ±50 %, il faut de l'ordre de 1 500-2 000 actions indépendantes (loi binomiale). Les actions d'une même tâche sont corrélées, donc davantage de tâches. Ordre de grandeur non sourcé, à confirmer par calcul de puissance.

### Gaps
- Pas de source chiffrant l'ampleur du biais de classement au voisinage d'un seuil.
- Aucune source trouvée traitant spécifiquement de « régression vers la moyenne » pour des classements au-dessus/en dessous d'un seuil.

## Q-E. Avec nos effectifs, quel partage la littérature appuie-t-elle ? 50/50, 30/70 ou 70/30

### Takeaway
La littérature n'impose pas un ratio. Elle appuie : partage par tâche, calibration et confirmation toutes deux petites en airline (40) et banking (77), donc pas de ratio qui sauve les deux rôles dans ces environnements. 50/50 est le défaut raisonnable (Fafchamps-Labonne, Dobbin-Simon sous 60 % de précision). 30/70 favorise le verdict, 70/30 favorise l'oracle.

### Cited Findings
- Fafchamps-Labonne : partage en deux moitiés. Perte de puissance reconnue comme coût principal, méthode déconseillée si l'échantillon est petit. — [Cambridge Core](https://www.cambridge.org/core/journals/political-analysis/article/using-split-samples-to-improve-inference-on-causal-effects/6727EF63175DF517BF56EC64EFF3E807)
- Anderson-Magruder : exploration de l'ordre de 30 % dans la variante hybride, confirmation de 70 %. — [Banque mondiale](https://blogs.worldbank.org/en/impactevaluations/trouble-pre-analysis-plans-try-these-three-weird-tricks)
- Dobbin-Simon : 1/2 préférable quand le signal est faible, 2/3 d'entraînement quand le signal est fort et n ≥ 100. À n = 50, éviter un partage simple. — [PMC3090739](https://pmc.ncbi.nlm.nih.gov/articles/PMC3090739)
- Angelopoulos-Bates : ~1000 points de calibration suffisent pour la plupart des usages ; la couverture varie sur un petit jeu de calibration. — [arXiv 2107.07511](https://arxiv.org/pdf/2107.07511)

### Inferences
Calculs de ma part (écart-type binomial par tâche, au pire p = 0,5, en supposant des tâches indépendantes et un seul verdict par tâche ; l'écart-type réel dépend de la variance entre tâches et du nombre d'actions par tâche) :

| Environnement | Réserve | 50/50 | 30/70 | 70/30 |
|---|---|---|---|---|
| airline | 40 | 20 / 20 (ET ≈ 0,11) | 12 / 28 (ET 0,14 / 0,09) | 28 / 12 (ET 0,09 / 0,14) |
| banking | 77 | 38-39 / 38-39 (ET ≈ 0,08) | 23 / 54 (0,10 / 0,07) | 54 / 23 (0,07 / 0,10) |
| retail | 91 | 45-46 / 45-46 (ET ≈ 0,07) | 27 / 64 (0,10 / 0,06) | 64 / 27 (0,06 / 0,10) |
| WorkBench | 552 | 276 / 276 (ET ≈ 0,03) | 166 / 386 (0,04 / 0,03) | 386 / 166 (0,03 / 0,04) |

- Dans les trois environnements τ-bench, aucun ratio ne donne plus de ~30 tâches aux deux rôles. Passer de 50/50 à 30/70 gagne environ 20 % d'écart-type sur le verdict mais en perd environ 30 % sur l'oracle. L'asymétrie réelle dépend de ce qui compte le plus pour la question de recherche (verdict primaire = confirmatoire et scellé ; écart de délégation = descriptif). Le verdict primaire est la question confirmatoire : l'argument d'Anderson-Magruder (le confirmatoire garde la plus grande part) va vers 30/70 ou 40/60. L'argument inverse : l'oracle sert de baseline et d'étalon pour l'ensemble, et son bruit contamine l'écart de délégation.
- WorkBench (552 tâches) tolère n'importe quel ratio : même un 30/70 laisse 166 tâches en calibration. Le goulot est τ-bench, en particulier airline (40).
- Le partage pourrait être différent par environnement (ex. 50/50 airline et banking, plus de calibration sur WorkBench). Il faut le justifier par une règle écrite d'avance, sinon c'est un degré de liberté.
- Le cross-fitting à deux plis (Q-C) serait la seule option qui ne force pas à choisir : il utilise toutes les tâches pour le verdict et pour l'oracle, au prix du schéma « scellé ». C'est à mon avis l'alternative à présenter au rédacteur, avec la condition d'un préenregistrement complet de la procédure.
- Les rejeux répétés (50 pour Haiku en airline) réduisent le bruit intra-tâche mais pas la variance entre tâches : ils n'augmentent pas le nombre d'unités indépendantes. Ils justifient surtout d'estimer le taux par tâche avec plus de précision, ce qui aide l'oracle plus que le verdict.

### Gaps
- Pas de calcul de puissance fait ici avec les vraies variances (je n'ai pas le droit d'ouvrir les données). Les écarts-types du tableau sont un plafond théorique à p = 0,5 : à reprendre avec les vrais taux et la corrélation intra-tâche.
- Aucune source ne traite du cas exact (règle gelée, calibration = définition d'une vérité de référence, confirmation scellée).
