# Décision « au moins une strate sous son seuil » (any-of-K) : multiplicité, seuils d'information minimale, mise en commun partielle, calibrage par simulation, cadres d'autonomie graduée

Conventions de ces notes : **c = n × seuil**, le nombre d'erreurs attendu dans une strate (type d'action) si l'agent était exactement au seuil. **m = taux réel / seuil** : m = 2 veut dire deux fois au-dessus de la barre. Les sections « Inferences » contiennent des calculs que j'ai faits moi-même : Python, approximation de Poisson du binomial (exacte à mieux que 1 % pour p ≤ 1/200), intervalles exacts. Ce sont des résultats reproductibles, pas des faits sourcés. Les scripts sont dans le scratchpad de session, pas dans le dépôt.

## Q1. Probabilité qu'au moins une des K strates passe par hasard, et corrections possibles (IUT, part minimale, Bonferroni)

### Takeaway
« Délégable si au moins un type passe » est un test d'union. Sous l'hypothèse globale « tous les types sont au-dessus de leur barre », le risque de faux « délégable » croît à peu près comme 1 − (1 − α_type)^K. La FDA exige un ajustement de multiplicité quand le succès sur l'un quelconque de plusieurs critères suffit. Elle n'en exige aucun quand tous doivent réussir : c'est la logique intersection-union de Berger (1982), qui se paie en puissance. Avec des données rares, c'est bien pire qu'une simple inflation de α. La règle « estimation ponctuelle ≤ barre » n'a aucun α contrôlé, et un type où c < 1 affiche 0 erreur avec une forte probabilité même quand m = 5 à 10.

### Cited Findings
- La FDA chiffre l'inflation pour des critères indépendants testés chacun à 0,025 unilatéral : 1 − 0,975³ ≈ 7 % pour trois critères, ≈ 22 % pour dix. Des critères corrélés gonflent aussi l'erreur, mais moins. — [FDA, *Multiple Endpoints in Clinical Trials*, guidance finale, oct. 2022](https://www.fda.gov/media/162416/download)
- Même guidance : il y a aussi multiplicité quand on analyse plusieurs « facettes » d'un même critère (doses, temps, **sous-groupes de sujets**) et que l'une quelconque suffit à conclure à un bénéfice. — [FDA 2022](https://www.fda.gov/media/162416/download)
- Cas « au moins un critère parmi plusieurs suffit » : la FDA y voit une « famille » de critères primaires, donc un problème de multiplicité. Elle cite comme méthodes appropriées Bonferroni, Holm, Hochberg, et les méthodes graphiques ou à gardien (Bretz 2009, Dmitrienko 2008). — [FDA 2022, §III.C.2 et §IV](https://www.fda.gov/media/162416/download)
- Cas « tous doivent réussir » (critères co-primaires), selon la FDA :
  - pas de problème de multiplicité, mais l'erreur de type II augmente ;
  - deux critères indépendants à 80 % de puissance chacun donnent 64 % de puissance conjointe, soit 36 % de type II ; il faut viser environ 90 % par critère pour retrouver 80 % ;
  - au-delà de deux co-primaires, il faut « bien réfléchir » à cause de la perte de puissance ;
  - relever α par critère (0,06 ou 0,07) n'est **pas acceptable**.

  — [FDA 2022, §II.B et §III.C.1](https://www.fda.gov/media/162416/download)
- Avec 10 tests d'interaction indépendants au seuil 0,05, la probabilité d'au moins un faux positif dépasse 40 %. — [Wang, Lagakos et al., NEJM 2007](https://www.biostat.jhsph.edu/courses/bio622/misc/SubgroupAnalyses_NEJM2007.pdf) (cohérent avec 1 − 0,95¹⁰ ≈ 0,40)
- Lagakos (NEJM 2006;354:1667-9) donne une figure de la probabilité d'au moins 1, 2 ou 3 faux positifs selon le nombre de sous-groupes testés. Un article secondaire rapporte qu'avec 33 tests d'interaction (essai PLATO), P(≥ 3 faux positifs) dépasse 20 %. — [PubMed 16625007](https://www.pubmed.gov/16625007/) ; [reprise secondaire](https://emergency.doctorsonly.co.il/?p=79324)
- Simulations de Brookes et al. :
  - le test d'interaction formel garde 5 % de faux positifs en l'absence d'effet différentiel ;
  - des tests séparés par sous-groupe montrent un effet « significatif dans un seul sous-groupe » dans 7 % à 64 % des simulations, selon le scénario ;
  - les essais dimensionnés pour l'effet global ont peu de puissance pour détecter des interactions.

  — [Brookes et al., J Clin Epidemiol 2004;57:229-236](https://research-information.bris.ac.uk/en/publications/subgroup-analyses-in-randomized-trials-risks-of-subgroup-specific/)
- Berger (1982, *Technometrics* 24(4):295-300, « Multiparameter hypothesis testing and acceptance sampling ») : un test intersection-union (IUT), qui rejette seulement si chaque test individuel rejette, est de niveau α quand chaque test individuel est de niveau α. Berger et Hsu (1996) l'étendent à la bioéquivalence. En pratique, la taille réelle est souvent très inférieure à α (test conservateur). — [doc. R jocre::iutsize](https://search.r-project.org/CRAN/refmans/jocre/html/iutsize.html) ; [Berger & Hsu, Statistical Science 1996](https://projecteuclid.org/euclid.ss/1032280304)
- Quand on observe beaucoup d'estimations, les plus extrêmes surestiment leur vraie valeur : c'est le biais de sélection, ou régression vers la moyenne. La formule de Tweedie en donne une correction empirique bayésienne. — [Efron, « Tweedie's Formula and Selection Bias », JASA 2011;106:1602-1614](https://pubmed.ncbi.nlm.nih.gov/22505788/)
- Règle de trois : avec 0 événement sur n, la borne supérieure de l'IC à 95 % vaut environ 3/n (Eypasch et al. 1995 la valident pour n > 30). — [Hanley & Lippman-Hand, JAMA 1983;249(13):1743-5](https://scilit.com/publications/ddfc523d905fccaecb8488227831d6ec) ; [Eypasch et al., BMJ 1995](https://scilit.com/publications/92d44b11beab0d6218d84a3f54a6e7fb)
- Filtrage indépendant : on écarte d'abord des hypothèses sur un critère indépendant de la statistique de test sous H0 (par exemple la taille d'échantillon), puis on corrige la multiplicité sur les seules survivantes. On gagne en puissance tout en gardant le contrôle du type I. Certains couples filtre/test, en revanche, font perdre ce contrôle. — [Bourgon, Gentleman & Huber, PNAS 2010;107:9546-51](https://pmc.ncbi.nlm.nih.gov/articles/PMC2906865)

### Inferences
- **Règle A (estimation ponctuelle ≤ barre)** ⇔ X ≤ ⌊c⌋, avec X ~ Poisson(m·c). Probabilité qu'au moins un type sur K = 9 passe (calculé) :

| c \ m | 10 | 5 | 2 | 1 | 0,5 |
|---|---|---|---|---|---|
| 0,1 | 0,984 | 1,000 | 1,000 | 1,000 | 1,000 |
| 0,5 | 0,059 | 0,537 | 0,984 | 1,000 | 1,000 |
| 1 | 0,004 | 0,310 | 0,991 | 1,000 | 1,000 |
| 3 | 0,000 | 0,002 | 0,771 | 1,000 | 1,000 |
| 10 | 0,000 | 0,000 | 0,093 | 1,000 | 1,000 |

  - Probabilités par type à c = 1 : 0,0005 pour m = 10, 0,040 pour m = 5, 0,406 pour m = 2, 0,736 pour m = 1.
  - Ces chiffres sont du même ordre que la simulation du projet : 99 % à 2× pour des types où c ≈ 1, entre 31 et 54 % à 5× pour c entre 1 et 0,5, contre 38 à 78 % annoncés. Les types à fort enjeu affichent presque toujours 0 erreur : à c = 0,01, P(0 erreur | m = 10) = 0,90 ; à c = 0,1, c'est 0,37 par type et 0,98 sur l'union de 9.
  - À m = 1, un type passe de 56 % à 74 % du temps **quel que soit c ≥ 0,5** (et 90 % à c = 0,1). La règle A est une pièce de monnaie au niveau de la barre. Augmenter c ne fait que raidir la transition, et la règle A ne protège contre m = 2 qu'à partir de c ≈ 10 (union = 9 %).
- **Règle B (borne supérieure exacte à 95 % ≤ barre)** :
  - **impossible tant que c < 3,00** (−ln 0,05) ;
  - **c ≥ 5,19** avec Bonferroni sur 9 types (−ln(0,05/9)) ;
  - **c ≥ 7,68** sur 108 cellules type × configuration ;
  - c ≥ 1,61 avec une borne à 80 %.

  Une fois la règle possible, la multiplicité joue aussi. À c = 3, P(passe | m = 1) = 0,05 par type mais 0,37 sur l'union des 9. À c = 10 et 20, l'union à m = 1 vaut 0,23 et 0,30, contre 0,025 et 0,044 avec Bonferroni (α/9). Bonferroni coûte en puissance : à c = 10 et m = 0,5, l'union passe de 0,995 à 0,698.
- **Règle « au moins r types sur K »** (règle A, K = 9, c = 1), en P(délégable) :
  - à m = 2 : 0,991 pour r = 1 ; 0,934 pour r = 2 ; 0,779 pour r = 3 ; 0,279 pour r = 5 ;
  - à m = 5 : 0,049 pour r = 2.

  Exiger une part minimale réduit les faux positifs, mais change l'estimand. On ne demande plus « un type délégable », on demande « une configuration globalement fiable ».
- **R4 comme IUT** (« tous les types prouvés au-dessus de la barre », borne inférieure exacte à 95 % > barre) :
  - c = 0,1 : P(R4) = 0,000 même pour m = 10 ;
  - c = 1 : 0,91 pour m = 10, 0,06 pour m = 5 ;
  - c = 3 : 1,00 pour m = 10, 0,93 pour m = 5.

  Sans information suffisante, on ne peut donc **prouver** l'absence de fiabilité ni d'une strate ni d'une configuration. Définir R4 comme « aucun type ne passe » mélange « clairement non fiable » et « pas assez de données », sauf à ne compter que les types qui franchissent la porte d'information.
- Quel outil pour quel usage :
  - **Bonferroni ou Holm sur la famille des affirmations sur lesquelles on agira.** Chaque type déclaré délégable est une décision. Holm est uniformément plus puissant que Bonferroni.
  - **IUT pour les affirmations conjonctives** (R4, « configuration entièrement délégable »). Pas d'ajustement nécessaire.
  - **Part minimale r-sur-K** si l'estimand est la fiabilité de la configuration.
  - **Correction du biais de sélection** (Efron) si l'on met en avant « le meilleur type » ou « la meilleure configuration ».
- Une porte fondée sur n (ou sur c), fixée avant de voir les résultats, est un filtre indépendant au sens de Bourgon et al. Elle réduit la taille de la famille à corriger, donc **augmente** la puissance, sans biaiser l'erreur. Une porte fondée sur les erreurs observées serait illégitime.

### Gaps
- Je n'ai pas consulté la source primaire du principe union-intersection de Roy (1953).
- Les valeurs exactes de la figure de Lagakos (2006) ne sont pas vérifiées.
- Le cadre « partial conjunction » (Benjamini & Heller 2008, tester « au moins u hypothèses fausses sur n ») formalise les règles r-sur-K. C'est une piste non vérifiée dans cette session.
- Je n'ai trouvé aucune source traitant spécifiquement des règles any-of-K dans l'évaluation d'agents IA.

## Q2. Seuils d'information minimale avant une affirmation par strate (essais, sous-groupes, épidémiologie, réglementaire)

### Takeaway
Les institutions fixent des minimums en **nombre d'événements**, en **taille d'échantillon** ou en **largeur d'intervalle**, et les assument comme des conventions (« convenient, if somewhat arbitrary »). Les valeurs usuelles :
- NCHS, mortalité : moins de 20 décès, soit une erreur standard relative (RSE) ≥ 23 %, jusqu'aux données 2022 ; **depuis les données 2023, moins de 10 décès, plus une largeur relative d'IC ≤ 160 %** ;
- NCHS, proportions : n ≥ 30 et des critères de largeur d'IC ;
- CMS : n < 25 ;
- essais : pilotage par le nombre d'événements ; un arrêt précoce avec moins de 500 événements surestime l'effet ;
- Japon : effectif national suffisant pour une probabilité ≥ 80 % de cohérence.

Ce qui se transpose au projet :
1. fixer la porte sur une quantité indépendante du résultat (n, ou c) ;
2. la dériver d'une caractéristique opératoire ;
3. traiter « 0 événement » comme une information, qui reste soumise à une revue.

### Cited Findings
- **Standards NCHS pour les proportions** (Parker et al. 2017, Vital Health Stat 2(175)) :
  - n et n effectif ≥ 30, sinon suppression ;
  - intervalle de Clopper-Pearson (Korn-Graubard pour les enquêtes complexes) ;
  - largeur absolue ≤ 0,05 : présentable si le nombre d'événements n'est pas 0 et si les degrés de liberté suffisent, sinon revue ;
  - largeur ≥ 0,30 : suppression ;
  - largeur entre 0,05 et 0,30 avec largeur relative > 130 % : suppression ;
  - moins de 8 degrés de liberté : revue.

  — [NCHS Series 2 No. 175](https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf)
- Même document :
  - avec 0 événement, on calcule l'IC sur le n réel et l'estimation passe en revue statistique, parce que « observer aucun événement » peut être informatif (événements rares) ;
  - les deux largeurs, absolue et relative, sont combinées parce que la RSE est trop conservatrice pour les très petites proportions et trop libérale pour les très grandes.

  — [NCHS Series 2 No. 175](https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf)
- **Mortalité NCHS / CDC WONDER** :
  - jusqu'aux données 2022 : astérisque à la place d'un taux fondé sur moins de 20 décès, « l'équivalent d'une RSE ≥ 23 % ». Le seuil de 20 est un repère « commode, quoique quelque peu arbitraire » ;
  - pour les taux standardisés sur l'âge, la porte porte sur la **somme** des décès de toutes les tranches d'âge, pas sur chaque tranche ;
  - depuis les données 2023 : moins de 10 décès donne un astérisque, et à partir de 10 décès il faut en plus une largeur relative de l'IC à 95 % ≤ 160 % ;
  - le seuil de 10 rejoint aussi le minimum de protection contre la divulgation.

  — [Kochanek et al., *Implementation of New Data Presentation Standards for Rates and Counts for Mortality*, CDC WONDER, révisé le 10/02/2026](https://wonder.cdc.gov/controller/pdf/presentation-standards-mortality-2024.pdf) ; standard de référence : Parker et al. 2023, [Vital Health Stat 2(200)](https://www.cdc.gov/nchs/data/series/sr_02/sr02-200.pdf)
- **CMS Hospital Compare** :
  - mention « nombre de cas trop faible (n < 25) pour prédire de façon fiable la performance » ;
  - les hôpitaux sous 25 cas sont exclus des graphiques et de la distinction « top » ;
  - le ratio standardisé de Medicare (RSMR) rapproche les petits hôpitaux de la moyenne nationale, d'autant plus fort qu'ils ont peu de cas.

  — [footnotes Hospital Compare](https://lha.ahd.com/def_qual_footnotes.html) ; [PMC2976775](https://pmc.ncbi.nlm.nih.gov/articles/PMC2976775) ; [PMC3401406](https://pmc.ncbi.nlm.nih.gov/articles/PMC3401406) (résumés, textes intégraux non lus)
- **Essais à critère temporel** : la puissance dépend du nombre d'événements et non du nombre de sujets. Il est donc courant de viser un nombre fixe d'événements. — [FDA, *Adaptive Designs for Clinical Trials of Drugs and Biologics*, nov. 2019, §VI.C](https://www.fda.gov/media/78495/download)
- **Arrêt précoce pour bénéfice** (91 essais tronqués comparés à 424 essais non tronqués) :
  - ratio des risques relatifs de 0,71 (IC 0,65 à 0,77) ;
  - les grands écarts (ratio < 0,75) apparaissent dans les essais tronqués à **moins de 500 événements** ;
  - l'écart est le même avec ou sans règle d'arrêt statistique, et il est maximal dans les petits essais.

  — [Bassler et al., JAMA 2010;303(12):1180-7](https://si.biostat.washington.edu/sites/default/files/modules/Bassler.pdf)
- **Sous-groupes** : le rapport HTA 2001 recommande de restreindre les analyses à celles proposées avant la collecte des données et, idéalement, de dimensionner l'essai pour elles, ce qui est souvent infaisable pour des interactions modestes. — [Health Technol Assess 2001;5(33)](https://doaj.org/article/05d3ea43db274da6ac797332f1a68656)
- **ICEMAN** (Schandelmaier et al., CMAJ 2020;192(32):E901-6) :
  - 5 questions centrales pour un essai randomisé, 8 pour une méta-analyse, une échelle de crédibilité ;
  - l'outil évalue les affirmations **qu'une modification d'effet existe** ;
  - ces analyses sont « typiquement surestimées ».

  — [CMAJ](https://www.cmaj.ca/content/192/32/E901) ; [PubMed 32778601](https://pubmed.ncbi.nlm.nih.gov/32778601/)
- **Japon, MHLW 2007 (« Method 1 »)** :
  - assez de patients japonais pour que D_Japon / D_global > 0,5 avec une probabilité ≥ 80 % si les effets sont identiques ;
  - c'est une porte d'information par strate définie par une caractéristique opératoire.

  — [diaporama MHLW](https://www.mhlw.go.jp/file/04-Houdouhappyou-11123000-Iyakushokuhinkyoku-Shinsakanrika/GCPclinicaltrials.pdf) ; [DIJ 2011](https://journals.sagepub.com/doi/abs/10.1177/009286151104500616) (texte original non lu)
- **Démonstration sans défaillance (« success run »)** : n = ln(1 − C)/ln(R), soit 59 essais sans défaillance pour 95 % de fiabilité à 95 % de confiance. — [Quality Digest](https://qualitydigest.com/node/35963) ; [Pharmaceutical Online](https://www.pharmaceuticalonline.com/doc/how-to-establish-sample-sizes-for-process-validation-using-the-success-run-theorem-0001)
- **Échantillonnage d'acceptation** :
  - AQL : niveau de qualité de base attendu du producteur ; LTPD : niveau de défauts jugé inacceptable par le client ;
  - risque producteur α (rejeter un lot au niveau AQL) et risque client β (accepter un lot au niveau LTPD), avec des valeurs typiques de 0,2 à 0,01 ;
  - la courbe OC (caractéristique opératoire) est « l'outil principal ».

  — [NIST/SEMATECH e-Handbook §6.2.2](https://www.itl.nist.gov/div898/handbook/pmc/section2/pmc22.htm)
- **Waymo** : n'affiche que les villes avec « assez de miles Waymo pour des comparaisons statistiques », sans seuil chiffré publié. — [Waymo Safety Impact](https://waymo.com/safety/impact/)

### Inferences
- Trois traditions aboutissent à **c ≈ 3** comme plancher absolu d'une preuve sans défaillance :
  - la règle de trois : 3/n ;
  - le « success run » : 59 × 5 % = 2,95 ;
  - RAND : 275 millions de miles × 1,09 décès par 10⁸ miles ≈ 3,0 (voir Q5).

  Le seuil NCHS de 20 décès correspond, lui, à la **précision d'estimation** : RSE de Poisson = 1/√20 ≈ 22 %. C'est une autre cible, plus exigeante, qui sert à publier un taux et non à trancher par rapport à une barre.
- **Choisir c à partir d'une zone d'indifférence (m_bon, m_mauvais) et de (α, β)**. Valeurs minimales calculées pour une règle « délégable si X ≤ t » par type :

| mauvais | bon | α = 0,05 ; β = 0,2 | α = 0,05/9 ; β = 0,2 | α = β = 0,05 |
|---|---|---|---|---|
| 2× | 0,5× | c ≈ 3,9 (t = 3) | c ≈ 7,0 (t = 5) | c ≈ 6,0 (t = 6) |
| 2× | 0,25× | c ≈ 2,4 (t = 1) | c ≈ 4,6 (t = 2) | c ≈ 3,2 (t = 2) |
| 1× (barre = H0) | 0,25× | c ≈ 7,8 (t = 3) | c ≈ 14 (t = 5) | c ≈ 11,9 (t = 6) |
| 1× | 0,1× | c ≈ 4,8 (t = 1) | c ≈ 7,4 (t = 1) | c ≈ 6,3 (t = 2) |
| 5× | 0,5× | c ≈ 1,0 (t = 1) | c ≈ 1,5 (t = 1) | c ≈ 1,3 (t = 2) |
| 10× | 0,5× | c ≈ 0,3 (t = 0) | c ≈ 0,75 (t = 1) | c ≈ 0,5 (t = 1) |

  Conséquence : **c est fixé par la largeur de la zone d'indifférence et par l'erreur visée, pas par une convention**. Si R4 doit seulement repérer des agents « clairement non fiables » (5 à 10× la barre), c ≈ 1 à 1,5 suffit pour cette décision. Prouver la délégabilité à la barre demande c ≈ 5 à 14.
- n impliqué par type (n = c / barre) :

| barre | c = 3 | c = 5,2 | c = 7 |
|---|---|---|---|
| 1/200 | 600 | ≈ 1 040 | 1 400 |
| 1/2 000 | 6 000 | ≈ 10 400 | 14 000 |
| 1/20 000 | 60 000 | ≈ 104 000 | 140 000 |

  Dans un plan hors ligne, les types à fort enjeu seront presque toujours sous la porte. Il faut le dire dans le préenregistrement.
- La règle CDC sur les taux standardisés (porte sur la **somme** des tranches) montre une pratique acceptée : franchir la porte au niveau d'un agrégat pré-défini quand chaque cellule est trop petite. Pour le projet, on pourrait l'appliquer en agrégeant un type sur plusieurs configurations, ou en regroupant des types de même barre.

### Gaps
- Les questions centrales d'ICEMAN n'ont pas été récupérées mot pour mot (CMAJ en 403).
- La guideline EMA sur les sous-groupes (2019) n'a pas été consultée.
- Je n'ai trouvé aucun minimum d'événements universel pour une affirmation par sous-groupe.
- Method 1 n'est connue que par un diaporama et un article secondaire.
- Les règles d'information minimale des comités de surveillance (bornes Haybittle-Peto ou O'Brien-Fleming) n'ont pas été récupérées dans cette session.

## Q3. Mise en commun partielle (bayésien empirique ou hiérarchique bêta-binomial) à la place des seuils par strate

### Takeaway
La mise en commun règle le « problème du zéro ». Un type à 0 erreur n'est plus estimé à 0 : il hérite de la moyenne du groupe (pseudo-comptes a₀ + b₀). Cela empêche la délégation « par chance », et cela rend une preuve possible même quand c < 3 si les strates sont réellement homogènes. En contrepartie, on échange le risque de multiplicité contre un **risque d'échangeabilité** :
- une strate mauvaise entourée de bonnes est tirée vers le bas (Freidlin & Korn, Berry 2013) ;
- le degré d'emprunt est mal estimé quand il y a peu de strates (environ 10 ou moins).

C'est préenregistrable si le modèle, les priors, les règles de décision et les scénarios de simulation, dont celui de « l'intrus », sont fixés à l'avance. C'est ce que demande le projet de guidance FDA 2026.

### Cited Findings
- Selon Gelman et al. :
  - les modèles multiniveaux font de la mise en commun partielle en rapprochant les estimations les unes des autres, alors que les procédures classiques laissent les centres en place et élargissent les intervalles ;
  - les comparaisons multiniveaux sont plus conservatrices ;
  - Bonferroni contrôle le type I au prix du type II ;
  - le problème des comparaisons multiples « peut disparaître entièrement » dans une perspective bayésienne hiérarchique.

  — [Gelman, Hill & Yajima, J Res Educ Eff 2012;5(2):189-211](https://arxiv.org/abs/0907.2478)
- Pharmacovigilance FDA :
  - le Gamma-Poisson Shrinker (DuMouchel 1999, Am Stat 53(3):177-190), puis le MGPS, servent à la FDA sur la base de déclarations spontanées ;
  - les ratios observé/attendu fondés sur de petits comptes sont ramenés vers 1 ;
  - le signal se lit sur EB05, la borne à 5 % de la loi a posteriori ;
  - le seuil « EB05 ≥ 2 » est décrit comme une règle courante, pas comme une règle FDA confirmée.

  — [openEBGM, R Journal 2017](https://journal.r-project.org/archive/2017/RJ-2017-063) ; [Drug Safety 2002](https://link.springer.com/content/pdf/10.2165/00002018-200225060-00001.pdf) ; [MetricGate (secondaire)](https://metricgate.com/docs/mgps-ebgm-gamma-poisson/)
- Berry & Berry (Biometrics 2004;60(2):418-26) : modèle hiérarchique à trois niveaux (type d'effet indésirable < système d'organe < ensemble) pour la multiplicité en sécurité. On emprunte entre systèmes, et davantage à l'intérieur d'un même système. — [RePEc](https://ideas.repec.org/a/bla/biomet/v60y2004i2p418-426.html)
- Berry et al. 2013 :
  - un plan hiérarchique conclut plus souvent correctement (efficace ou futile) que les plans indépendant et poolé dans de nombreux scénarios ;
  - quand le traitement marche dans certains groupes et pas dans d'autres, l'emprunt peut **gonfler le type I**.

  — [Berry et al., Clinical Trials 2013, PubMed 23983156](https://www.pubmed.gov/23983156/)
- Freidlin & Korn :
  - selon des résumés du texte, la mise en commun simple n'est utile que si l'on a de fortes raisons d'attendre une activité uniforme ;
  - les travaux qui citent l'article lui attribuent ceci : le modèle hiérarchique sur-rétrécit vers la moyenne commune et gonfle fortement le type I pour les strates insensibles, surtout avec 10 sous-groupes ou moins, parce que les données ne déterminent pas bien l'emprunt.

  — [Freidlin & Korn, Clin Cancer Res 2013;19:1326-34 (résumé INCa)](https://www.cancer.fr/professionnels-de-sante/veille/nota-bene-cancer/bulletin-n-167/borrowing-information-across-subgroups-in-phase-ii-trials-is-it-useful) ; [arXiv 2002.03007](https://ar5iv.labs.arxiv.org/html/2002.03007) ; [PMC6546564](https://pmc.ncbi.nlm.nih.gov/articles/PMC6546564)
- Neuenschwander et al. (EXNEX) :
  - chaque strate est un mélange : soit échangeable avec les autres, soit non échangeable ;
  - l'objectif est d'éviter le rétrécissement excessif des strates extrêmes ;
  - la spécification et les priors sont plus exigeants.

  — [Neuenschwander et al., Pharm Stat 2016;15(2):123-34](https://zendy.io/title/10.1002/pst.1730) ; [vignette bhmbasket](https://cran.case.edu/web/packages/bhmbasket/vignettes/reproduceExNex.html)
- **FDA, projet de guidance du 12/01/2026, « Use of Bayesian Methodology in Clinical Trials of Drug and Biological Products » (CDER/CBER)** :
  - un modèle hiérarchique suppose l'échangeabilité et fait de la mise en commun partielle ;
  - risques identifiés : conflit entre prior et données, prior mal spécifié, non-échangeabilité ;
  - exigences : emprunt et décote pré-spécifiés, analyses de sensibilité ;
  - la taille d'échantillon effective du prior est a₀ + b₀ en bêta-binomial ;
  - le texte de la guidance n'a pas été lu directement.

  — [Ji, arXiv 2601.14701](https://arxiv.org/html/2601.14701v1) ; [Applied Clinical Trials, 14/01/2026](https://appliedclinicaltrialsonline.com/view/fda-issues-draft-guidance-advance-bayesian-methods-clinical-trials)
- **CMS** : le rétrécissement du RSMR est critiqué parce qu'il peut affaiblir le signal de qualité en ramenant trop les scores vers la moyenne (Silber et al. 2010, d'après des sources qui le citent). Les petits hôpitaux sont plus exposés au mauvais classement. — [PMC3401406](https://pmc.ncbi.nlm.nih.gov/articles/PMC3401406) ; [Health Affairs (PDF)](https://medstaff.chsbuffalo.org/wp-content/uploads/2020/06/Improving-The-Accuracy-Of-Hospital-Quality-Ratings-By-Focusing-On-The-Association-Between-Volume-And-Outcome.pdf)

### Inferences
- **Simulation (calculée)** :
  - montage : 12 configurations, un type de barre 1/2 000, hyperparamètres bêta-binomiaux estimés par maximum de vraisemblance (bayésien empirique « plug-in ») sur une grille, 300 répétitions ;
  - règle « délégable » : P(taux ≤ barre | données) ≥ 0,95 ;
  - rappel : sans mise en commun, à c = 0,5 la borne supérieure exacte ne passe **jamais**.

| Scénario | c | Mauvaise strate (5×) délégable | Bonnes strates (0,2×) délégables | Pooling complet |
|---|---|---|---|---|
| B : 12 bonnes (0,2×) | 0,5 | — | 0,97 | 65 % |
| C : 12 mauvaises (5×) | 0,5 | 0,00 | — | 62 % |
| A : 6 bonnes + 6 mauvaises | 0,5 | 0,00 | 0,00 | 5 % |
| **D : 11 bonnes + 1 mauvaise (« intrus »)** | 0,5 | **0,30** | 0,58 | 27 % |
| E : 6 + 6 | 5 | 0,00 | 0,73 | 0 % |
| F : 11 + 1 | 5 | 0,00 | 0,92 | 0 % |

  Lecture :
  - la mise en commun donne de la puissance quand les strates sont homogènes (B) ;
  - elle ne donne rien si elles sont hétérogènes (A) ;
  - elle **délègue l'intrus 30 % du temps** quand c est faible (D) ;
  - avec c = 5, elle redevient sûre (F).

  **La mise en commun ne dispense donc pas d'une porte d'information par strate. Elle la complète.**
- Mettre en commun **entre types dont les barres diffèrent d'un facteur 100** est inadapté. Un prior tiré des types à faible enjeu (échelle 1/200) empêcherait mécaniquement un type à fort enjeu d'atteindre 1/20 000. À défaut, il faudrait modéliser log(taux/barre) avec des effets de type, ce qui suppose une échangeabilité forte et difficile à défendre. Le niveau le plus défendable est **un même type à travers les configurations** (même barre), avec une structure EXNEX ou un emprunt plafonné.
- Pour un projet préenregistré :

| Pour | Contre |
|---|---|
| Plus de « zéro chanceux » | Hypothèse d'échangeabilité invérifiable avec peu de strates |
| Multiplicité traitée par la structure | L'intrus est masqué (30 % dans D) |
| Gain de puissance si les strates sont homogènes | Sensibilité au prior et à l'hyperprior |
| Pré-spécifiable (modèle, prior, seuil de probabilité a posteriori) | Calcul et documentation plus lourds |
| | Le bayésien empirique « plug-in » ignore l'incertitude des hyperparamètres (mon raisonnement), d'où le choix d'un bayésien complet ou d'une calibration par simulation |
| | Difficile à expliquer à un lecteur non statisticien |

### Gaps
- Je n'ai pas lu le texte intégral de Freidlin & Korn 2013 ni celui du projet FDA 2026. Le statut final du projet en novembre 2026 n'est pas vérifié.
- Je n'ai trouvé aucune source chiffrant le nombre minimal de strates pour estimer l'emprunt de façon stable.
- La référence classique sur la sous-estimation des intervalles en bayésien empirique (Morris 1983 ; Kass & Steffey 1989) n'a pas été vérifiée dans cette session.

## Q4. Fixer les paramètres par simulation des caractéristiques opératoires (FDA et pratique)

### Takeaway
La FDA (2019) attend :
- des simulations pour choisir les valeurs critiques ;
- un type I estimé sur une **grille de scénarios nuls**, avec les paramètres de nuisance, et un maximum sur la grille ≤ la cible ;
- environ 100 000 itérations par scénario, soit ±0,1 % ;
- un rapport de simulation complet : scénarios justifiés, nombre d'itérations, code, essais exemples.

Côté bayésien, la guidance dispositifs de 2010 a des sections sur les caractéristiques opératoires et leur simulation. Le projet de 2026 permet de calibrer sur le type I ou sur des métriques bayésiennes, à condition d'une évaluation exhaustive des scénarios. Le modèle historique est l'échantillonnage d'acceptation : on choisit (n, c) pour passer par deux points de la courbe OC.

### Cited Findings
- FDA 2019, §VI.A (p. 18-20) :
  - les simulations servent à choisir le nombre et le moment des analyses intermédiaires, à fixer la valeur critique de la statistique, à comparer des plans et surtout à montrer que les caractéristiques opératoires atteignent les niveaux visés ;
  - pour le type I, on simule sous une série d'hypothèses compatibles avec H0, et la proportion de faux positifs estime le type I de chaque scénario ;
  - il existe une infinité de scénarios nuls : on choisit un ensemble limité qui représente la plage plausible, avec les paramètres de nuisance, en combinant considérations médicales et mathématiques, dont la **monotonie**.

  — [FDA 2019](https://www.fda.gov/media/78495/download)
- Même section :
  - pratique courante : simuler sur une **grille** de valeurs plausibles (par exemple une mortalité de 75, 80, 85, 90, 95 et 99 %) et argumenter que le type I maximal ne dépasse pas la cible ;
  - si le paramètre de nuisance observé sort de la grille (par exemple 50 %), il faut des simulations supplémentaires ;
  - pour plusieurs critères, supposer l'indépendance peut donner une borne supérieure du type I avec Bonferroni ou Holm.

  — [FDA 2019](https://www.fda.gov/media/78495/download)
- Précision demandée :
  - 100 000 itérations par scénario donnent un IC à 95 % d'environ ±0,1 % sur le type I, « suffisant dans la plupart des cas » ;
  - 10 000 peuvent suffire avec une grille fine si tous les scénarios restent sous la cible, ou si la borne supérieure de l'IC est sous la cible ;
  - des graines aléatoires différentes par scénario sont préférables ;
  - la puissance et les autres caractéristiques demandent moins de précision et une grille plus clairsemée.

  — [FDA 2019](https://www.fda.gov/media/78495/download)
- Documentation (p. 28) :
  - caractéristiques à rapporter : type I, puissance, taille d'échantillon attendue, minimale et maximale, biais, couverture des IC ;
  - rapport de simulation : description du plan, **essais exemples** aux conclusions différentes, configurations de paramètres simulées avec justification, nombre d'itérations et sa justification, résultats par scénario, **code lisible**.

  — [FDA 2019](https://www.fda.gov/media/78495/download)
- Avec des priors informatifs, les propriétés bayésiennes sont « plus informatives que le type I ». Les simulations sont particulièrement coûteuses pour les plans bayésiens. — [FDA 2019, §VI.B](https://www.fda.gov/media/78495/download)
- **FDA 2010, guidance bayésienne pour les dispositifs médicaux** (CDRH, finale, février 2010) :
  - la table des matières contient des sections sur les caractéristiques opératoires d'un plan bayésien et sur les « Simulations to Obtain Operating Characteristics » ;
  - selon un diaporama secondaire, contrôler le type I moins strictement qu'en fréquentiste peut être approprié selon la confiance accordée au prior.

  — [page FDA](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/guidance-use-bayesian-statistics-medical-device-clinical-trials) ; [PDF HHS](https://www.hhs.gov/guidance/sites/default/files/hhs-guidance-documents/FDA/Guidance-for-the-Use-of-Bayesian-Statistics-in-Medical-Device-Clinical-Trials-%28PDF-Version%29.pdf)
- **Projet FDA 2026** :
  - critère de succès Pr(d > a) ≥ c ;
  - calibration soit sur des erreurs fréquentistes (type I, FWER), soit, avec l'accord de la FDA, sur des métriques bayésiennes (puissance bayésienne, assurance, probabilité de décision correcte) ;
  - caractéristiques opératoires évaluées **prospectivement** sur des scénarios pertinents, souvent par simulation, avec documentation du plan de simulation, des hypothèses et du code ;
  - Frank Harrell critique la calibration d'une règle bayésienne sur le type I.

  — [Ji, arXiv 2601.14701](https://arxiv.org/html/2601.14701v1)
- Échantillonnage d'acceptation : risque producteur à l'AQL, risque client au LTPD, la courbe OC comme outil principal. — [NIST e-Handbook](https://www.itl.nist.gov/div898/handbook/pmc/section2/pmc22.htm) ; Berger (1982) relie explicitement les tests IUT à l'acceptation multiparamétrique ([jocre](https://search.r-project.org/CRAN/refmans/jocre/html/iutsize.html))

### Inferences
Protocole transposable au projet, à figer avant la collecte :
1. **Définir l'état vrai** : vecteur des m par type et par configuration, et n par type.
2. **Grille de scénarios** :
   - homogènes : tous les types à m ∈ {0,1 ; 0,25 ; 0,5 ; 1 ; 2 ; 5 ; 10} ;
   - mixtes : un seul bon type au milieu de mauvais ; une mauvaise configuration au milieu de bonnes ;
   - n réalistes, y compris des types rares.

   La monotonie (plus m est grand, moins on délègue) permet, comme le note la FDA, de réduire la grille aux frontières.
3. **Sorties par scénario** : P(au moins un type délégable), P(R4), P(indéterminé), et P(délégable) par type.
4. **Calibrer** la valeur critique t par type, c_min et le seuil de R4 pour que :
   - P(délégable | tous les types ≥ m_mauvais) ≤ α (famille définie à l'avance) ;
   - P(R4 | au moins un type ≤ m_bon) ≤ α′ ;
   - la puissance soit ≥ 1 − β aux scénarios « bons ».
5. **Précision** : 100 000 itérations pour les erreurs (±0,1 %), ou 10 000 si toutes les estimations restent sous la cible avec de la marge. Des graines distinctes par scénario. Code et graines publiés avec le préenregistrement.
6. **Prévoir la vérification a posteriori** : si les n réalisés ou les taux observés sortent de la grille, relancer les simulations (cf. l'exemple des 50 % de la FDA).

### Gaps
- Je n'ai lu ni le texte intégral de la guidance 2010 (sections 4.8 et 7.2 selon des sources secondaires) ni celui du projet 2026.
- ICH E20 (plans adaptatifs) n'a pas été consulté.
- Je n'ai trouvé aucun exemple publié de calibration par simulation pour une règle any-of-K appliquée à des agents IA.

## Q5. Cadres d'autonomie graduée (véhicules autonomes, aviation, agents IA) et capacités sans preuve suffisante

### Takeaway
Aucun de ces cadres n'accorde d'autonomie à une capacité ou à un domaine sur la seule absence de défaillance observée dans des données rares :
- **véhicules autonomes** : l'autonomie est bornée à un domaine de conception opérationnelle (ODD) ; hors ODD, repli vers une condition de risque minimal (MRC) ;
- **Waymo** n'affiche que les villes avec assez de miles ;
- **RAND** montre que l'essai routier seul ne peut pas prouver la sécurité face aux événements rares ;
- **aviation** : un taux de 10⁻⁹ ne se démontre pas par l'essai, il s'argumente par l'analyse de conception ;
- **agents IA** : approbation par défaut, autonomie accordée progressivement, niveaux et « certificats » d'autonomie proposés, fiabilité mesurée par pass^k.

Le défaut universel pour « pas assez de preuves » est **« pas d'autonomie »**, ce qui ne veut pas dire « non fiable ».

### Cited Findings
- **RAND, Kalra & Paddock 2016** (RAND RR-1478 ; Transp Res A 94:182-193) :
  - référence humaine : 1,09 décès par 100 millions de miles, soit 32 719 décès en 2013 ;
  - il faut 275 millions de miles **sans défaillance** pour démontrer ce taux à 95 % de confiance, soit environ 12,5 ans pour 100 véhicules roulant 24 h/24 à 25 mph ;
  - démontrer une amélioration de 20 % avec 80 % de puissance demanderait environ 11 milliards de miles (sources secondaires) ;
  - conclusion : des centaines de millions, voire des centaines de milliards de miles seraient nécessaires.

  — [TRID](https://trid.trb.org/View/1435302) ; [RAND RR-1478](https://www.rand.org/pubs/research_reports/RR1478.html) ; [citation des 275 M (liste systemsafety)](https://lists.techfak.uni-bielefeld.de/pipermail/systemsafety/2018-March/003798.html) ; [IEEE T&S Mag. 2018 (11 Md)](https://nxtbook.com/nxtbooks/ieee/technologysociety_march2018/index.php?startid=64)
- **Butler & Finelli 1993** (IEEE TSE 19(1):3-12) :
  - exigence historique de 10⁻⁷ à 10⁻⁹ par mission de 1 à 10 h ; « ultrafiabilité » = taux < 10⁻⁷/h ;
  - pour 10⁻⁹ par mission de 10 h, le temps moyen avant défaillance est d'environ 10¹⁰ h ;
  - durée d'essai attendue avec une seule défaillance observée : 1 141 550 ans pour 1 exemplaire en test, 114 155 ans pour 10, 11 415 ans pour 100, 114 ans pour 10 000, et cela « au prix d'erreurs α et β extrêmement grandes » ;
  - ni les modèles de croissance de fiabilité ni la diversité logicielle (N-version) ne lèvent l'obstacle.

  — [NASA NTRS](https://ntrs.nasa.gov/citations/20040139817)
- **FAA AC 25.1309-1B** (30/08/2024) :
  - « extrêmement improbable » ≤ 10⁻⁹ par heure de vol pour les conditions catastrophiques ; 10⁻⁷ pour « extrêmement lointain », 10⁻⁵ pour « lointain » ;
  - qualitativement, une condition « extrêmement improbable » n'est pas censée survenir pendant toute la vie opérationnelle de tous les avions d'un type.

  — [FAA (PDF, 403 lors de la session)](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_25.1309-1B.pdf) ; [Wikipedia (secondaire)](https://en.wikipedia.org/wiki/AC_25.1309-1) ; [extrait reproduit](https://lists.techfak.uni-bielefeld.de/pipermail/systemsafety/attachments/20240823/55c0cb54/attachment-0001.html)
- **SAE J3016 (avril 2021)** :
  - l'ODD est l'ensemble des conditions de fonctionnement pour lesquelles un système ou une fonction est spécifiquement conçu ;
  - un système de niveau 4 ou 5 exécute un repli vers une MRC à la sortie de son ODD ou en cas de défaillance.

  — [Stanford CIS (MRC)](https://cyberlaw.stanford.edu/blog/2022/01/deep-weeds-levels-driving-automation-lurks-ambiguous-minimal-risk-condition) ; [arXiv 2304.02705](https://arxiv.org/pdf/2304.02705) (définitions reprises de sources secondaires)
- **Waymo, Safety Impact hub** (271,3 M miles sans conducteur à fin juin 2026) :
  - « seules les villes avec assez de miles Waymo pour des comparaisons statistiques sont montrées » ;
  - IC de Poisson exacts, Clopper-Pearson pour les écarts en pourcentage ; écart significatif si l'IC ne croise pas 0 % ;
  - Atlanta (8,6 M miles) affiche « N/A » pour une des comparaisons.

  — [Waymo](https://waymo.com/safety/impact/)
- **Kusano et al. 2025** (56,7 M miles) : 11 groupes de types d'accidents ; taux significativement plus bas pour les accidents avec blessure déclarée et avec déclenchement d'airbag. — [Traffic Inj Prev 2025;26(sup1):S8-S20](https://pubmed.ncbi.nlm.nih.gov/40378124/)
- **Feng, McDonald & Zhang 2025** :
  - cinq niveaux d'autonomie définis par le rôle de l'utilisateur : opérateur, collaborateur, consultant, approbateur, observateur ;
  - l'autonomie est une décision de conception, pas une conséquence de la capacité ;
  - les auteurs proposent des **certificats d'autonomie** délivrés par un tiers, sur la base d'« autonomy cases » analogues aux safety cases.

  — [arXiv 2506.12469](https://arxiv.org/abs/2506.12469)
- **Anthropic, « Measuring AI agent autonomy in practice » (18/02/2026)** :
  - l'approbation automatique complète concerne environ 20 % des sessions chez les nouveaux utilisateurs (moins de 50 sessions) et plus de 40 % après 750 sessions ;
  - la progression est graduelle, et les utilisateurs expérimentés interrompent **plus** souvent ;
  - le réglage par défaut exige d'approuver chaque action ;
  - la base d'utilisateurs a doublé entre janvier et mi-février.

  — [Anthropic](https://www.anthropic.com/research/measuring-agent-autonomy)
- **Claude Code** :
  - règles allow, ask et deny par outil et par motif de commande, évaluées dans l'ordre deny, puis ask, puis allow ;
  - le mode fixe le comportement **par défaut quand aucune règle ne s'applique**, et le mode par défaut demande avant les opérations potentiellement dangereuses ;
  - l'application est faite par le harnais, pas par le modèle.

  — [docs Claude Code](https://code.claude.com/docs/en/permissions)
- **τ-bench** :
  - pass^k = probabilité de réussir les k essais d'une même tâche ;
  - gpt-4o réussit moins de 50 % des tâches et a un pass^8 inférieur à 25 % en commerce de détail, soit environ 60 % de baisse par rapport à pass^1.

  — [Yao et al., arXiv 2406.12045](https://arxiv.org/pdf/2406.12045) ; [Sierra](https://sierra.ai/uk/blog/benchmarking-ai-agents)

### Inferences
- Le chiffre RAND est encore la règle de trois : 275 M × 1,09·10⁻⁸ ≈ 3,0 événements attendus au seuil. **c = 3 est le plancher universel d'une preuve sans défaillance.** Avec des barres de 1/20 000, prouver par l'expérience demande au moins 60 000 exécutions du type concerné.
- Correspondances avec le projet :
  - ODD ↔ ensemble des types ayant franchi la porte ;
  - hors ODD ↔ « indéterminé, donc non délégué par défaut » ;
  - « ask par défaut » de Claude Code ↔ un type sans preuve reste en approbation humaine.

  Aucun de ces cadres n'utilise l'absence de preuve pour conclure à la non-fiabilité. Cela va dans le sens de séparer R4 (« clairement non fiable ») d'un label « preuves insuffisantes ».
- L'aviation montre l'issue pour les taux ultra-faibles : quand l'essai est infaisable (Butler & Finelli), on ne prétend pas démontrer statistiquement. On s'appuie sur d'autres arguments (analyse de conception, barrières). Pour les types à fort enjeu, le projet peut préenregistrer « non démontrable dans ce plan » plutôt que de laisser un zéro valoir preuve.

### Gaps
- Je n'ai pas lu le texte de l'AC 25.1309-1B (403) ; les définitions viennent de sources secondaires.
- Le cadre NHTSA (ODD, MRC) n'a pas été récupéré.
- Waymo ne publie pas de seuil chiffré d'inclusion d'une ville.
- Je n'ai trouvé aucun cadre d'agents IA exigeant explicitement un minimum de preuves **par type d'action** avant d'accorder l'autonomie. Les cadres trouvés sont qualitatifs (niveaux, certificats) ou laissés à l'utilisateur.

## Q6 (synthèse). Meilleur design de la condition « au moins un parmi K », et comment fixer c avant la collecte

### Takeaway
Remplacer la règle binaire actuelle par une décision à trois issues par type :
- **délégable** : preuve de taux ≤ barre, avec contrôle d'erreur sur la famille ;
- **non délégable prouvé** : preuve de taux > barre, ou règle calibrée « mauvais » ;
- **indéterminé** : porte d'information non franchie.

La configuration est délégable si au moins un type est **délégable** (union contrôlée par Holm ou Bonferroni sur les seuls types qui ont franchi la porte). **R4** ne s'affirme que si **tous** les types ayant franchi la porte sont non délégables prouvés (IUT), et à condition que ces types soient en nombre suffisant. Sinon, le label est « preuves insuffisantes ». On fixe c, t et α en simulant les caractéristiques opératoires sur une grille préenregistrée, à la manière de la FDA 2019.

### Cited Findings
- Union = multiplicité à ajuster ; conjonction = pas d'ajustement mais perte de puissance. — [FDA 2022](https://www.fda.gov/media/162416/download) ; [Berger 1982 via jocre](https://search.r-project.org/CRAN/refmans/jocre/html/iutsize.html)
- Un filtrage préalable indépendant du résultat (ici n ou c) puis une correction sur les survivants garde le contrôle d'erreur et gagne en puissance. — [Bourgon et al. 2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC2906865)
- Les seuils d'information sont des conventions assumées (20 puis 10 décès, n ≥ 30, n < 25) et se combinent à des critères de largeur d'IC. — [CDC WONDER 2024](https://wonder.cdc.gov/controller/pdf/presentation-standards-mortality-2024.pdf) ; [NCHS 2(175)](https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf)
- Les paramètres se calibrent par simulation sur une grille, avec code et justification documentés. — [FDA 2019](https://www.fda.gov/media/78495/download) ; [projet FDA 2026 via Ji](https://arxiv.org/html/2601.14701v1)
- La mise en commun partielle exige l'échangeabilité ; EXNEX limite l'emprunt pour les strates extrêmes. — [Neuenschwander 2016](https://zendy.io/title/10.1002/pst.1730) ; [Berry 2013](https://www.pubmed.gov/23983156/)

### Inferences
Design recommandé, en étapes préenregistrables :
1. **Porte d'information par type, sur c = n_prévu × barre.** Le seuil c_min se déduit de la zone d'indifférence et de l'erreur visée (tableau Q2). Par exemple, c_min ≈ 4 à 7 pour séparer 0,5× de 2× avec α par famille de 0,05 ; c_min = 3,0 au strict minimum pour qu'une preuve sans erreur soit seulement possible ; 5,2 avec Bonferroni sur 9 types. Les types sous la porte sont **indéterminés** : ni délégables, ni comptés pour R4.
2. **Règle « délégable » par type** : nombre d'erreurs ≤ t_type, avec t calibré par simulation, ou de façon équivalente une borne supérieure à 1 − α/K_franchis ≤ barre. **Jamais** l'estimation ponctuelle (règle A) : elle n'a aucun contrôle d'erreur au niveau de la barre.
3. **Définir la famille à l'avance** : les types d'une configuration si chaque configuration reçoit son propre label ; toutes les cellules (jusqu'à 108, soit c ≥ 7,7 pour une preuve sans erreur) si le résultat principal est « au moins une configuration délégable ». Si l'on met en avant la meilleure configuration, prévoir une correction de sélection ou une réplication.
4. **R4 = intersection-union sur les types franchis** : chaque type prouvé au-dessus de sa barre, ou classé « mauvais » par une règle calibrée, avec un nombre minimal de types franchis fixé à l'avance. Sinon, label distinct « preuves insuffisantes ». Calcul : avec c = 3, R4 est atteint 93 % du temps pour un agent à 5× sur 9 types ; avec c = 1, seulement 6 %.
5. **Option de mise en commun** : hiérarchique **par type à travers les configurations** (même barre), robuste (EXNEX), seuil de probabilité a posteriori calibré par simulation, scénario « intrus » obligatoire. Elle ne remplace pas la porte : dans la simulation, l'intrus est délégué 30 % du temps à c = 0,5, et 0 % à c = 5.
6. **Simulation des caractéristiques opératoires** (protocole Q4) sur la grille homogène plus les scénarios mixtes. Publier P(délégable), P(R4) et P(indéterminé) par scénario. 100 000 itérations pour les erreurs. Code et graines figés.
7. **Types à fort enjeu** : avec n réaliste, c reste bien en dessous de 1 (60 000 exécutions pour c = 3 à 1/20 000). Les préenregistrer comme **non démontrables par ce plan**, comme en aviation, plutôt que de laisser un zéro valoir preuve.

### Gaps
- Je n'ai trouvé aucune étude préenregistrée d'agents IA appliquant ce type de règle à trois issues, donc pas de précédent direct.
- Les règles de décision « go / no-go / indéterminé » à double critère (Roychoudhury et al. 2018 ; Frewer et al. 2016) seraient la référence méthodologique naturelle. Elles n'ont pas été vérifiées dans cette session.
