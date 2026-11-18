# Inférence quand une cellule ne contient qu'une grappe ou très peu de grappes (G = 1 à 10), avec des événements binaires rares

Conventions. « Cited Findings » : sourcé ; les citations entre guillemets anglais sont recopiées du texte lu (PDF converti en texte ou page web), sauf mention « d'après le résumé de recherche » (texte original non lu). « Inferences » : déduit par moi, y compris tous les calculs (refaits avec scipy, `env -u ANTHROPIC_API_KEY`). « Gaps » : cherché, pas trouvé, ou non lu. Correspondance utilisée partout : une tâche porteuse du projet joue le rôle d'une grappe « traitée » (celle qui porte l'information sur le paramètre) en économétrie, ou d'une UPE (unité primaire de sondage) qui contient des membres du domaine en sondage. Les tâches sans écriture du niveau jouent le rôle des grappes témoins, qui ne contribuent que des zéros.

## 1. Une inférence fréquentiste valide sur la variation entre grappes est-elle possible avec G = 1 ? Avec G = 2 à 5 ?

### Takeaway
Avec G = 1, la variance entre grappes n'est pas estimable : il reste 0 degré de liberté. Aucune méthode de la littérature lue n'établit un écart à une valeur de référence sans une hypothèse forte sur la structure intra-grappe, invérifiable avec une seule grappe. Avec G = 2 à 5, une inférence valide existe, mais seulement sous hypothèses (estimations par grappe indépendantes et à peu près normales). Le t de Ibragimov et Müller vaut dès 2 groupes. Les tests par changements de signe n'ont aucune puissance à 5 % sous 6 grappes, et les variantes de bootstrap et de variance robuste sont mal calibrées.

### Cited Findings
- **Ibragimov et Müller (2010), rapporté par Cameron et Miller (2015).** On estime le paramètre dans chaque groupe, puis on fait un t sur les G estimations : « Ibragimov and Müller (2010) show that tests based on the T(G − 1) distribution will be conservative tests (i.e., under-reject) for level α ≤ 0.083. This approach permits correct inference even with extremely few clusters, assuming N_g is large. However, the requirement that cluster estimates are asymptotically independent must be met. » — [Cameron & Miller 2015, PDF](http://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
- **Conditions de validité.** Ibragimov et Müller (2010, JBES 28(4)) : l'inférence est valide « as long as the groups are chosen in a way that ensures the parameter estimators to be asymptotically independent, unbiased and Gaussian of possibly different variances ». L'ingrédient clé (Bakirov et Székely) : « for a significance level of 5% or lower, the t-test remains conservative for underlying observations that are independent and Gaussian with heterogenous variances » (d'après le résumé de recherche) — [notice Imperial SPIRAL](https://spiral.imperial.ac.uk/entities/publication/651db680-95fd-4163-b596-ae55ddef49aa)
- **Tests de randomisation approchés par changements de signe** (Canay, Romano et Shaikh 2017 ; mode d'emploi de Cai, Canay, Kim et Shaikh 2023). Le groupe des changements de signe a « |G| = 2^q » éléments, q étant le nombre de grappes. « the test may have trivial power for very low values of q. For example, when α = 10%, this problem arises if q ≤ 4. For q = 5 the test already has non-trivial power and is only slightly conservative under the null. Similarly, when α = 5% the test has non-trivial power for any q ≥ 6. » Le résumé dit que la méthode s'applique quand « the number of clusters is small – even as small as five » — [Cai, Canay, Kim & Shaikh, arXiv 2102.09058](https://arxiv.org/abs/2102.09058)
- **Cadre de Canay, Romano et Shaikh (2017, Econometrica 85).** Nombre fixe de grappes, chacune avec beaucoup d'observations. Les résultats admettent des grappes hétérogènes et une dépendance à l'intérieur des grappes comme entre elles (d'après le résumé de recherche) — [RePEc](https://ideas.repec.org/a/wly/emetrp/v85y2017ip1013-1030.html)
- **Une seule grappe traitée (G1 = 1) : la variance robuste estime une variance nulle.** « from equation (7) it is evident that the variance of that term is incorrectly estimated to be zero. » « tests based on the cluster-robust t statistic (4) using conventional critical values almost always overreject very severely when G1 = 1 or G0 = 1. The denominator of (4) grossly underestimates the variance of the numerator. » Avec les résidus non contraints, les résidus « sum to zero for the single treated cluster » — [MacKinnon & Webb 2018, QED WP 1364](https://www.econ.queensu.ca/sites/econ.queensu.ca/files/qed_wp_1364.pdf)
- **Seule voie valide avec G1 = 1 : supposer peu de corrélation intra-grappe.** Le wild bootstrap ordinaire (au niveau de l'observation) « yields (approximately) valid inferences for the pure treatment model (1) whenever all clusters are the same size and the amount of intra-cluster correlation is not too large, even when G1 = 1 ». Mais « the failure of Assumption 3 can cause serious errors of inference when G1 = 1, but not when G1 ≥ 2, unless the amount of intra-cluster correlation is very large » — [MacKinnon & Webb 2018](https://www.econ.queensu.ca/sites/econ.queensu.ca/files/qed_wp_1364.pdf)
- **Ferman et Pinto (2019).** Leurs procédures « can work well even with just one treated cluster. However, this is possible only because, unlike methods based on a CRVE, they do not allow for unrestricted heteroskedasticity » — [MacKinnon, Nielsen & Webb 2023, arXiv 2205.03285](https://arxiv.org/abs/2205.03285)
- **Conley et Taber (2011) : peu de groupes traités, inférence empruntée aux groupes témoins.** « If there are group-time random effects, then the DiD model is inconsistent because the treated groups random effects are not averaged away. If the random effects are normally distributed, then the model of Donald and Lang (2007) applies and inference can use a T distribution based on the number of treated groups. [...] Conley and Taber (2011) then propose a novel method that uses the distribution of the untreated groups to perform inference on the treatment parameter. » — [Cameron & Miller 2015](http://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
- **Borne générale (Bahadur et Savage 1956, Ann. Math. Statist. 27).** Sur la famille des lois de moyenne finie, tout test de niveau α uniforme d'une hypothèse unilatérale sur la moyenne a une puissance au plus α contre chaque alternative (d'après le résumé de recherche) — [arXiv 2609.05360](https://arxiv.org/pdf/2609.05360) ; [notice IAS](https://repository.ias.ac.in/27021). Romano (2004) en tire que, pour la plupart des modèles non paramétriques, la taille du test t vaut 1 à toute taille d'échantillon (d'après le résumé de recherche) — [RePEc, Scand. J. Stat. 31](https://econpapers.repec.org/RePEc:bla:scjsta:v:31:y:2004:i:4:p:567-584)
- **Intervalle à une seule observation (loi normale, variance inconnue).** La forme ±c|X| remonte à Stein. Avec Machol, « the confidence is 90% for x±5|x| » (d'après le résumé de recherche) — [Rodriguez, arXiv bayes-an/9504001](https://arxiv.org/pdf/bayes-an/9504001). Wall, Boen et Tweedie (2001, Am. Stat. 55) proposent c = 4,84 à 90 %, selon le commentaire de Wittkowski (d'après le résumé de recherche) — [commentaire, PDF](https://www.ma.imperial.ac.uk/~dvandyk/Research/02-tas-cment.pdf). Portnoy (2019) en donne une version minimax — [RePEc](https://ideas.repec.org/a/taf/amstat/v73y2019i1p10-15.html)

### Inferences
- **G = 1.** La variance empirique de G estimations par grappe a G − 1 = 0 degré de liberté : elle n'existe pas. Le t de Ibragimov et Müller est indéfini ; il faut au moins 2 groupes.
- **Changements de signe avec q = 1.** Il n'y a que 2 configurations de signes, donc la plus petite valeur p atteignable est 1/2 : aucun rejet n'est possible à 5 %. Avec q = 2 à 5, le minimum vaut 1/4 à 1/32. Cai et al. situent la puissance non triviale à q ≥ 6 pour α = 5 %.
- **Les intervalles à une observation ne servent à rien ici.** Ils ont la forme x ± c|x| avec c > 1 (5 ; 4,84), donc ils contiennent toujours 0. Appliqués à (estimation − budget), ils contiennent toujours le budget et ne peuvent jamais établir un dépassement. L'existence d'une inférence « valide » à G = 1 est donc réelle sous normalité, mais sans aucun usage pour R1.
- **Ce qui rend l'inférence possible, c'est une restriction du modèle** (Bahadur et Savage), pas le nombre de grappes. À G = 1, la restriction doit porter tout entière sur la corrélation intra-tâche, que les données d'une seule tâche ne permettent pas de vérifier. MacKinnon et Webb le disent pour G1 = 1 : la validité exige des grappes de même taille et peu de corrélation intra-grappe.
- **Même mécanisme que dans le projet.** Avec une seule grappe traitée, le résidu de la grappe traitée somme à zéro, d'où une variance estimée nulle (MacKinnon et Webb). Avec une seule tâche porteuse, le ratio erreurs ÷ écritures reproduit exactement la tâche, et son résidu y − R̂x est nul. C'est la même dégénérescence que le bootstrap plat : elle tient à l'estimateur, pas au bootstrap.

### Gaps
- Je n'ai lu ni le texte original d'Ibragimov et Müller (2010), ni Bakirov et Székely (2006), ni Conley et Taber (2011) : leurs énoncés viennent de Cameron et Miller (2015), de MacKinnon, Nielsen et Webb (2023) et de résumés.
- Je n'ai trouvé aucun texte qui traite de G = 1 comme cas propre (au-delà de G1 = 1 en économétrie et de la strate à une UPE en sondage). Aucun ne propose une inférence sur la variation entre grappes à G = 1 sans hypothèse externe.

## 2. Bootstrap par paires de grappes, wild cluster bootstrap (WCR/WCU ; Rademacher, Webb) et tests de randomisation avec peu de grappes et des événements rares

### Takeaway
Avec peu de grappes porteuses, le bootstrap par paires de grappes dégénère : des tirages ne contiennent aucune grappe porteuse, des statistiques sont constantes ou « perfect fit ». Les rejets mesurés partent dans les deux sens : 0,001 pour l'écart type bootstrap par paires à G = 6, et sur-rejet sévère quand G1 est petit. Le wild cluster restreint (WCR) ne rejette presque jamais avec une seule grappe traitée, le non restreint (WCU) sur-rejette très fortement. Rademacher plafonne à 2^G tirages distincts (valeur p d'au moins 1/16 à G = 5), d'où les poids de Webb sous G = 10. La randomisation tient avec G1 = 1 seulement si les grappes sont homogènes et G assez grand. Je n'ai trouvé aucun taux mesuré pour peu de grappes avec des issues binaires rares.

### Cited Findings
- **Variance robuste (CRVE) avec la valeur critique 1,96.** Cameron, Gelbach et Miller (2008, table 3) : rejets de « .068, .081, .118, and .208 for G equal to, respectively, 30, 20, 10 and 5 ». Bertrand, Duflo et Mullainathan (2004) : « .063, .058, .080, and .115 for number of states (G) equal to, respectively, 50, 20, 10 and 6 ». Avec la correction de biais : « .062, .070, .092, and .138 for G equal to, respectively, 30, 20, 10 and 5 ». Avec des grappes déséquilibrées à G = 10 : « .183, appreciably worse than rejection rates of .126 and .115 for balanced clusters » — [Cameron & Miller 2015](http://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
- **Bootstraps de Cameron, Gelbach et Miller (2008).**
  - Le bootstrap-t par paires de grappes a des taux de rejet « of 0.08 ».
  - Les bootstrap-t par résidus et wild cluster ne diffèrent pas statistiquement de 0,05 « (with the exception of the residual bootstrap with G = 5) ».
  - Le wild cluster bootstrap-se « under-rejects for G ≤ 10 ».
  - Dans le cadre en différence de différences : « the cluster-pairs standard error bootstrap (row 4) produces severe under-rejection (0.001) with G = 6. Informal experimentation suggests to us that this is because many bootstrap replications (with only a couple of states sampled) sample only one "treatment" or "control" state. »
  - Avec un régresseur binaire constant dans chaque grappe : « some bootstrap resamples may have all clusters with the regressor taking only value 0 (or value 1), so that β̂ is inestimable ».
  - — [CGM, NBER t0344](https://www.nber.org/system/files/working_papers/t0344/t0344.pdf)
- **Écart type bootstrap nul ou quasi nul** (« Bootstrap with Caution ») : « if you are using a pairs cluster bootstrap with dummy right-hand side variables, then in some samples you can get no or very limited variation in treatment. This can lead to zero or near-zero standard errors. [...] if the bootstrapped standard errors are zero plus machine precision noise, rather than exactly zero, very large t-values may result. [...] No variation or very limited variation in treatment can also result in many of your β̂*'s being "perfect fit" β̂*'s with limited variability. Then the bootstrap standard deviation of the β̂*'s will be too small, and if you use it as your estimated standard error you will over-reject. » — [Cameron & Miller 2015](http://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
- **Wild cluster avec peu de grappes traitées (G = 14, 400 000 réplications).**
  - Le WCR « almost never rejects for G1 = 1 and G1 = 13, underrejects severely for G1 = 2 and G1 = 12, performs almost perfectly for G1 = 3 and G1 = 11 (a coincidence that would not have occurred if G had been larger or smaller), and overrejects modestly for other values of G1 ».
  - Le WCU « overrejects very severely for G1 = 1 and G1 = 13, but it improves rapidly as G1 becomes less extreme and performs extremely well for 6 ≤ G1 ≤ 8 ».
  - Le CV1 avec la loi t(13) « leads to severe overrejection when G1 = 1 ».
  - Ailleurs : « When G1 = 1, it [le WCR] typically never rejects at any conventional level. »
  - — [MacKinnon & Webb 2018](https://www.econ.queensu.ca/sites/econ.queensu.ca/files/qed_wp_1364.pdf)
- **Bootstrap par paires de grappes avec peu de grappes traitées** : « G1 varies across the bootstrap samples and may well equal 0 for many of them. Because this procedure tends to overreject very severely when G1 is small, we do not study it further » — [MacKinnon & Webb 2018](https://www.econ.queensu.ca/sites/econ.queensu.ca/files/qed_wp_1364.pdf)
- **Synthèse de MacKinnon, Nielsen et Webb (2023).** « In the most extreme case of just one treated cluster, rejection frequencies may be essentially zero. In this case, the bootstrap distribution is often bimodal. » Ils conseillent alors d'essayer le WR (wild restreint ordinaire) ou l'inférence par randomisation. Sur le bootstrap par paires de grappes : « it can either over-reject or underreject severely » — [MNW 2023](https://arxiv.org/abs/2205.03285)
- **Rademacher contre Webb.**
  - Avec Rademacher, « there are at most 2^G unique values ». Webb montre qu'il n'y a que 2^(G−1) valeurs absolues possibles du t : « Thus with G = 5 there are at most 2^4 = 16 possible values [...] all we know is that the p-value is smaller than 1/16 = 0.0625. »
  - « As G gets to be as large as 11 this concern is less of an issue since 2^10 = 1024. »
  - La loi de Webb à six points « outperforms the two-point wild bootstrap for G < 10 and is the preferred method to use if G < 10 ».
  - — [Cameron & Miller 2015](http://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
  - MNW : la loi à six points « largely solves this problem » ; si 2^G ou 6^G est plus petit que B, on énumère — [MNW 2023](https://arxiv.org/abs/2205.03285)
- **Randomisation (RI).** Les tests RI-β et RI-t « work very well when the clusters are homogeneous and G is reasonably large, even when G1 = 1. However, when the treated clusters are systematically larger or smaller than average, neither RI-β nor RI-t tests perform well ». Et : « It seems to be widely believed that tests based on RI are always exact. This is not true. » — [MNW 2023](https://arxiv.org/abs/2205.03285)
- **Permutation dans les essais en grappes.** Avec 5 grappes, « the permutation tests generally control type I errors better than does MM » ; le test « remains valid in small samples and in the presence of correlation across different clusters » — [PMC5507602](https://pmc.ncbi.nlm.nih.gov/articles/PMC5507602)

### Inferences
- **Le bootstrap du projet est un bootstrap par paires de grappes** (tâches tirées avec remise, stratifié), studentisé par l'écart type bootstrap dans le max-T. Avec une tâche porteuse, c'est exactement le cas « pairs cluster, G1 = 1 » de MacKinnon et Webb. Une réplique sans la tâche donne 0/0 ; une réplique qui la tire donne un ratio constant. C'est le cas « perfect fit, standard deviation too small, you will over-reject » de Cameron et Miller, observé dans le monde V (un faux R1 sur 30).
- **Si l'écart type n'est pas exactement nul** (variation par les seuls ordres et le validateur), l'avertissement « zero plus machine precision noise » s'applique. D'après `maxt.py`, T* = (estimation* − estimation) ÷ écart type peut devenir énorme et gonfler c* pour toutes les cellules : le max-T perd de la puissance ailleurs. La borne de la cellule elle-même vaut alors à peu près l'estimation moins le bruit des ordres et du validateur. Dans les deux cas, aucune variance entre tâches n'entre dans la décision.
- **Point de code à vérifier, non vérifié.** Dans `maxt.depassement_etabli`, l'écart type vient de `np.std(ddof=1)`. Si les répliques 0/0 sont stockées en NaN, l'écart type vaut NaN, et `var = sd > 0` est faux pour NaN. La cellule part alors en silence dans la branche « estimation > budget ». Je n'ai pas lu le module qui construit `q.boot` (hors du périmètre autorisé) : je ne sais pas si des NaN y apparaissent.
- **Événements rares.** Quand la plupart des tâches ont zéro écriture du niveau ou zéro erreur, l'information est portée par le nombre de tâches porteuses (l'analogue de G1), pas par le nombre total de tâches. Selon MNW, augmenter G à G1 fixe n'aide pas et peut aggraver le sur-rejet.
- **Wild bootstrap au niveau des tâches avec une seule porteuse.** Seuls 2 signes sont possibles, donc la plus petite valeur p est 1/2. Le wild au niveau des écritures suppose une corrélation intra-tâche faible, ce que la section 8 du plan refuse de supposer.

### Gaps
- Aucun taux de rejet mesuré trouvé pour la combinaison exacte du projet : peu de grappes porteuses et issue binaire rare, avec beaucoup de zéros, par bootstrap par paires, wild ou randomisation. Les travaux lus portent sur des régresseurs binaires (traitement), pas sur des issues rares.
- Les valeurs numériques des figures de MacKinnon et Webb (2018) ne sont pas données dans le texte ; je n'ai que la description qualitative.
- Leyrat et al. (2018) sur les essais en grappes avec peu de grappes et issue binaire : non consulté.

## 3. Nombres minimaux de grappes recommandés : par qui, pour quelle méthode

### Takeaway
Aucun seuil universel. Les seuils publiés dépendent de la méthode :
- « peu » de grappes = moins de 20 à moins de 50 (Cameron et Miller) ;
- poids de Webb sous G = 10 ;
- au moins 6 grappes pour un test par changements de signe à 5 % (Cai et al.) ;
- au moins 2 groupes pour le t de Ibragimov et Müller, sous hypothèses ;
- en statistique publique (NCHS) : revue obligatoire sous 8 degrés de liberté, suppression sous une taille effective de 30.

La littérature économétrique insiste sur un point : ce qui compte est le nombre de grappes qui portent l'information (traitées, porteuses), pas le total.

### Cited Findings
- **Cameron et Miller (2015).** « there is no clear-cut definition of "few". Depending on the situation "few" may range from less than 20 clusters to less than 50 clusters in the balanced case, and even more clusters in the unbalanced case. » Et : « there is no specific point at which we need to worry about few clusters. Instead, "more is better". Current consensus appears to be that G = 50 is enough for state-year panel data. » Enfin : « with less than ten clusters the wild cluster bootstrap should use the six-point version of Webb (2013) » — [Cameron & Miller 2015](http://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
- **Cameron, Gelbach et Miller (2008).** « the residual and wild cluster bootstrap methods perform well in cases with as few as 6 clusters » ; leurs simulations vont jusqu'à « as few as five clusters » — [CGM, NBER t0344](https://www.nber.org/system/files/working_papers/t0344/t0344.pdf)
- **MacKinnon, Nielsen et Webb (2023).** « As the number of treated clusters, say G1, increases, the problem often goes away fairly rapidly. But increasing G when G1 is small and fixed does not help and may cause over-rejection to increase. » — [MNW 2023](https://arxiv.org/abs/2205.03285)
- **MacKinnon et Webb (2018).** « Even when G is quite small (say, between 15 and 20), simulation results [...] suggest that rejection frequencies tend to be very close to nominal levels, provided that cluster sizes do not vary extremely and the number of treated clusters is not too small. » — [MacKinnon & Webb 2018](https://www.econ.queensu.ca/sites/econ.queensu.ca/files/qed_wp_1364.pdf)
- **Changements de signe.** Puissance non triviale à 5 % pour « any q ≥ 6 », à 10 % dès q = 5 — [Cai, Canay, Kim & Shaikh 2023](https://arxiv.org/abs/2102.09058)
- **Sondage.** « For the design with two PSUs per stratum, an unbiased variance estimator for the linear estimators exist without any implicit assumptions. » — [Mosaferi 2019, arXiv 1910.05840](https://arxiv.org/abs/1910.05840)
- **NCHS Data Presentation Standards for Proportions** (Vital Health Stat 2(175), 2017).
  - « When applicable for complex surveys, if the sample size and CI criteria are met for presentation and the degrees of freedom are fewer than 8, then the proportion should be flagged for statistical review by the clearance official. This review may result in either the presentation or the suppression of the proportion. »
  - Note de tableau : « Effective sample size is less than 30. Estimate would be suppressed. »
  - Les normes reposent sur « a minimum denominator sample size » et sur des intervalles de Clopper-Pearson, ou de Korn-Graubard pour les sondages complexes.
  - « estimated proportions based on fewer than 8 degrees of freedom have an RSE(Var) of 50% or higher ».
  - Elles avertissent que « default calculations from survey software may not be appropriate or feasible for all situations, including [...] estimates for subgroups represented in only a subset of primary sampling units (PSUs) ».
  - « When an estimate is flagged or suppressed, a footnote indicating the reason the estimate has been flagged or suppressed should be provided in the publication. »
  - — [NCHS, Series 2 n° 175](https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf)

### Inferences
- **Lecture en strate unique.** Les degrés de liberté valent (nombre de porteuses − 1). Le seuil NCHS de 8 degrés de liberté correspond donc à au moins 9 tâches porteuses, et une seule porteuse donne 0 degré de liberté. Le « fragile sous 30 tâches porteuses » du plan rappelle le seuil NCHS de 30, mais le seuil NCHS porte sur une taille effective en individus, pas en UPE : les deux ne sont pas équivalents.
- **Plancher cohérent avec la littérature et les mesures du projet : 5 à 6 tâches porteuses** pour une décision fondée sur un rééchantillonnage. Le projet a mesuré le max-T bien calibré entre 5 et 11 porteuses (0 R1 sur 120 au seuil). La littérature montre des échecs nets à G1 = 2 (WCR) et à G = 5 (variance robuste à 20,8 %).
- **Entre 2 et 4 porteuses**, ni la littérature ni le projet ne fournissent de calibration pour le max-T bootstrap ; c'est la zone non mesurée.

### Gaps
- La règle « au moins 4 grappes par bras » attribuée à Hayes et Moulton (2009) : non vérifiée ; je n'ai trouvé qu'une mention indirecte, et pour des essais pilotes. La phrase de CONSORT déconseillant une grappe par bras n'est pas vérifiée non plus.
- Je n'ai trouvé aucun guide réglementaire propre au cas « événements rares et peu de grappes », hormis les normes du NCHS.

## 4. Sondages : les strates à une seule UPE (« lonely PSU »)

### Takeaway
Les deux logiciels de référence refusent par défaut de produire une variance : R `survey` (`fail`, une erreur) et Stata (`singleunit(missing)`, des écarts types manquants). Le remède recommandé par Lumley comme par le manuel Stata est de fusionner la strate avec une strate voisine bien choisie (strates regroupées, biais positif, donc prudent). Les traitements automatiques diffèrent :
- `certainty` et `remove` (contribution nulle) sont non prudents, sauf pour une vraie unité tirée avec certitude ;
- `adjust` et `centered` sont qualifiés de prudents ;
- `average` et `scaled` supposent des UPE isolées « manquantes au hasard ».

Pour SAS, la contribution serait nulle par défaut, avec une note dans le journal ; ce n'est pas vérifié dans sa documentation officielle. Point décisif pour le projet : la cellule n'est pas une strate à une UPE, c'est un domaine porté par une seule UPE. Dans ce cas, la variance linéarisée d'un ratio vaut exactement 0, et aucun des correctifs automatiques ne la rétablit (déduit).

### Cited Findings
- **Page de Lumley (paquet R `survey`).**
  - « If only one PSU is sampled from a particular stratum the variance can't be computed. »
  - Le défaut rend « an error to have a stratum with a single, non-certainty PSU ».
  - Pour une UPE certaine, « there is no contribution to the variance from the first stage of sampling in this stratum ».
  - `remove` et `certainty` : « an alternative to specifying fpc », « might be useful for compatibility with other software ».
  - `adjust` : « conservative ».
  - `average` : « might be appropriate if the lonely PSUs were due to data missing at random ».
  - « The best adjustment is probably to combine the single-PSU stratum with another well-chosen stratum. »
  - Domaines : le cas où « only one PSU in a stratum has observations in a particular domain or subpopulation » donne un avertissement, pas une erreur.
  - Les poids répliqués ont les mêmes problèmes ; l'option est lue par `as.svrepdesign`.
  - — [Lumley, « Lonely PSUs »](https://r-survey.r-forge.r-project.org/survey/exmample-lonely.html)
- **Options de `survey.lonely.psu`.**
  - Défaut `"fail"`, « which gives an error ».
  - `"remove"` : « to ignore that PSU for variance computation ».
  - `"adjust"` : « to center the stratum at the population mean rather than the stratum mean ».
  - `"average"` : « to replace the variance contribution of the stratum by the average variance contribution across strata ».
  - Domaines : les formules « give well-defined, positive results » mais « are not unbiased ». Avec `survey.adjust.domain.lonely = TRUE` et `adjust` ou `average`, le même ajustement s'applique dans le domaine, mais « this adjustment is not available for replicate-weight designs ».
  - — [R survey, surveyoptions](https://r-survey.r-forge.r-project.org/survey/html/surveyoptions.html)
- **Stata, `svyset`.** « singleunit(missing) results in missing values for the standard errors and is the default. singleunit(certainty) causes strata with single sampling units to be treated as certainty units. Certainty units contribute nothing to the standard error. singleunit(scaled) results in a scaled version of singleunit(certainty). The scaling factor comes from using the average of the variances from the strata with multiple sampling units for each stratum with one sampling unit. singleunit(centered) specifies that strata with one sampling unit are centered at the grand mean instead of the stratum mean. » — [Stata, svyset](https://www.stata.com/manuals/svysvyset.pdf)
- **Stata, estimation de variance.**
  - « By default, Stata's svy commands report missing standard errors when they encounter a stratum with one sampling unit. Although the best way to solve this problem is to reassign the sampling unit to another appropriately chosen stratum, there are three automatic alternatives [...] »
  - Le facteur d'échelle de `scaled` vaut (L − Lc)/(L − Lc − Ls).
  - Pour `centered`, « The quotient n_h/(n_h − 1) in the variance formula is also taken to be 1 if n_h = 1. »
  - Le ratio R̂ = Ŷ/X̂ a pour variable de score z_j = (y_j − R̂ x_j)/X̂.
  - Bootstrap de sondage (Rao-Wu-Yue) : « if n_h is the number of observed PSUs in stratum h, then n_h − 1 PSUs are sampled with replacement from within stratum h », avec le poids w* = n_h/(n_h − 1) × m* × w.
  - — [Stata, variance estimation](https://www.stata.com/manuals/svyvarianceestimation.pdf)
- **SAS.** Une réponse du forum SAS dit que le défaut retire les UPE isolées du calcul de variance : la strate ne contribue rien (d'après le résumé de recherche) — [communauté SAS](https://communities.sas.com/t5/Statistical-Procedures/Can-SAS-deal-with-the-singleton-lonely-PSU-in-Survey-procedures/m-p/952010). Une sortie d'exemple porte une note : une seule grappe dans une strate, variance estimée à zéro (d'après le résumé de recherche) — [exemple PEAS](https://www.restore.ac.uk/PEAS/ex2datafiles/results/ex2sas_ncres.pdf)
- **Strates regroupées.** « The collapsed stratum method for variance estimation was first introduced by [Hansen, Hurwitz & Madow]. This method usually causes an overestimation in the variance of estimator » — [Mosaferi 2019](https://arxiv.org/abs/1910.05840). Ailleurs, l'estimateur « is not design-unbiased » et « the bias increases as the population means of the pseudo-strata become more variant » — [arXiv 2110.10296 (v2 retirée, version finale 2603.03569)](https://arxiv.org/abs/2110.10296)

### Inferences
- **Le défaut des deux logiciels est le refus**, et la justification de Lumley est littérale : la variance « can't be computed ». Tout correctif automatique ajoute une hypothèse.
- **Classement par prudence :**
  - `certainty` et `remove` : contribution nulle, non prudents dès que l'UPE n'est pas une vraie unité certaine ;
  - `adjust` et `centered` : qualifiés de prudents par Lumley ;
  - `average` et `scaled` : prudents seulement si la variance empruntée est au moins la vraie ; Lumley les réserve aux UPE isolées manquantes au hasard ;
  - regroupement de strates : biais positif, donc prudent ; c'est la voie recommandée.
- **Correspondance avec les options du projet :**
  - la règle actuelle du plan (5.14, point 1) est le traitement `certainty` (aucune contribution entre tâches) ;
  - l'option (b) est le comportement par défaut de R et Stata (`fail`, `missing`), complété par la pratique du NCHS (estimation signalée avec une note qui en dit la raison).
- **Une unité « certaine » contribue légitimement zéro si elle est toute la population de son niveau.** La règle actuelle se défend donc seulement si la cible d'inférence est l'ensemble fixe des tâches du banc. Or le plan rééchantillonne les tâches, ce qui suppose une population de tâches. Pour cette cible, la tâche unique n'est pas une unité certaine, et le traitement `certainty` contredit la cible du plan comme sa section 8.
- **Le cas du projet est un domaine porté par une seule UPE.** La strate aviation a beaucoup de tâches ; c'est le domaine « écritures de ce niveau » qui n'en a qu'une. Avec le score du ratio de Stata, z_j = (y_j − R̂x_j)/X̂ :
  - les tâches non porteuses ont y = x = 0, donc z = 0 ;
  - la tâche porteuse a R̂ = y₁/x₁, donc z = 0 ;
  - la variance linéarisée vaut donc exactement 0, comme le bootstrap plat.
- **Aucun correctif automatique ne s'applique.** `adjust` centre sur la moyenne des scores, qui vaut 0, donc la contribution reste nulle. `average` emprunte aux autres strates des contributions nulles pour cette cellule. Regrouper avec une autre strate n'ajoute que des tâches sans écriture du niveau. Les « well-defined, positive results » de Lumley pour les domaines valent quand d'autres strates portent le domaine, pas ici.
- **Le seul vrai remède est d'emprunter une variance à d'autres cellules**, par exemple d'autres niveaux, configurations ou environnements. C'est un modèle, analogue à `average` ou à Conley et Taber.

### Gaps
- Wolter (2007), section 2.5 sur les strates regroupées : non lu. Les sources secondaires le citent comme traitement de référence ; je ne peux pas citer sa recommandation.
- Le livre de Lumley (2010) : non lu (seulement sa documentation et sa page).
- La documentation officielle de SAS sur les strates à une UPE : texte non trouvé (le manuel SURVEYMEANS 13.1 téléchargé ne contient pas ces mots). SUDAAN (MISSUNIT) : non vérifié.
- Le traitement d'une sous-population portée par une seule UPE dans Stata (`subpop`) : non vérifié dans le manuel ; ma déduction (variance nulle pour un ratio) n'est pas confirmée par une source.

## 5. Bootstrap dégénéré : statistique constante, ou 0/0 quand la seule grappe n'est pas tirée

### Takeaway
Le bootstrap ne peut pas créer une variation absente de l'échantillon. Avec une seule grappe porteuse, le ratio rééchantillonné est constant quand la grappe est tirée et vaut 0/0 sinon ; la linéarisation et le jackknife donnent aussi zéro ou un résultat indéfini. Le paquet `boot`, compagnon de Davison et Hinkley, refuse de calculer un intervalle quand toutes les répliques sont égales, et écarte en silence les répliques non finies. Cameron et Miller recommandent de ne jamais prendre un bootstrap dégénéré pour argent comptant. Je n'ai pas pu lire les recommandations de Davison et Hinkley (1997) ni de Canty et al. (2006).

### Cited Findings
- **Le paquet `boot`** « Functions and datasets for bootstrapping from the book "Bootstrap Methods and Their Application" by A. C. Davison and D. V. Hinkley (1997, CUP), originally written by Angelo Canty for S » — [boot, DESCRIPTION](https://github.com/cran/boot/blob/master/DESCRIPTION).
  - Dans `boot.ci` : `print(paste("All values of t are equal to ", mean(t, na.rm=TRUE), "\n Cannot calculate confidence intervals")); return(NULL)`.
  - Les répliques non finies sont retirées avant le calcul : `fins <- seq_along(t)[is.finite(t)]`.
  - Le tracé avertit « All values of t* are equal to », et l'affichage « WARNING: All values of t... * are NA ».
  - — [boot, R/bootfuns.q](https://github.com/cran/boot/blob/master/R/bootfuns.q)
- **Cameron et Miller (2015), « Bootstrap with Caution ».**
  - « if you are using a pairs cluster bootstrap and one cluster is an outlier in some sense, then the resulting histogram may have a big "mass" that sits separately from the rest of the bootstrap distribution – that is, there may be two distinct distributions, one for cases where that cluster is sampled and one for cases where it is not. »
  - « For a percentile-t pairs cluster bootstrap, a zero or missing standard error will lead to missing values for w*, since the standard error is zero or missing. If you naively use the remaining distribution, then there is no reason to expect that you will have valid inference. »
  - « Fifth, in general if you see missing values in your bootstrapped t-statistics, then you need to figure out why. Don't take your bootstrap results at face value until you know what's going on. »
  - — [Cameron & Miller 2015](http://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
- **Statistiques inestimables (Cameron, Gelbach et Miller 2008).** « some pseudo-samples β̂1 or s_β̂1 may be inestimable » avec un régresseur binaire constant dans les grappes, et peu de grappes — [CGM, NBER t0344](https://www.nber.org/system/files/working_papers/t0344/t0344.pdf)
- **Diagnostic par le tracé (MacKinnon, Nielsen et Webb 2023).** Si la distribution bootstrap « has more than one mode, then it probably does not provide a good approximation to the actual distribution » — [MNW 2023](https://arxiv.org/abs/2205.03285)
- **Bootstrap de sondage (Rao-Wu-Yue)** : on tire n_h − 1 UPE avec le facteur n_h/(n_h − 1) — [Stata, variance estimation](https://www.stata.com/manuals/svyvarianceestimation.pdf)
- **Canty, Davison, Hinkley et Ventura (2006, Can. J. Stat. 34, 5–27).** Les diagnostics évaluent la fiabilité des calculs bootstrap et peuvent orienter vers des calculs modifiés. Ils portent sur la sensibilité aux particularités des données, un mauvais modèle de rééchantillonnage, le mauvais usage des sorties et l'imprécision propre au bootstrap ; mots clés : jackknife-after-bootstrap, sous-échantillonnage (d'après le résumé de recherche et la notice) — [DOI 10.1002/cjs.5550340103](https://doi.org/10.1002/cjs.5550340103) ; [notice BibBase](https://bibbase.org/network/publication/canty-davison-hinkley-venture-bootstrapdiagnosticsandremedies-2006)
- **Davison et Hinkley (1997)** proposent plusieurs variantes du bootstrap par grappes : grappes tirées avec remise, puis éventuellement permutation ou rééchantillonnage dans les grappes (d'après le résumé de recherche) — [arXiv 2510.07770](https://www.arxiv.org/pdf/2510.07770)

### Inferences
- **Mécanique du ratio avec une seule porteuse.** La réplique vaut k·x₁/(k·m₁) = estimation dès que la tâche porteuse est tirée k ≥ 1 fois, et 0/0 sinon. Dans une strate de n tâches, la tâche n'est pas tirée avec la probabilité (1 − 1/n)^n : 0,25 pour n = 2, 0,33 pour n = 5, 0,36 pour n = 50.
- **Écarter les 0/0, comme `boot.ci`, conditionne sur « porteuse tirée »** : l'écart type devient nul. C'est exactement le « flat » du monde V.
- **Les remplacer par 0 serait un faux remède.** On fabriquerait une loi à deux masses, celle que décrivent Cameron et Miller, avec un écart type d'environ estimation × √(p(1 − p)), soit à peu près 0,48 × estimation pour p ≈ 0,36. Cette variance dépendrait du tirage de la tâche, pas de la variation entre tâches.
- **Jackknife par tâche.** Retirer la porteuse donne 0/0 ; retirer une autre tâche ne change rien. La variance jackknife est donc nulle ou indéfinie. La dégénérescence est la même pour la linéarisation, le bootstrap et le jackknife : elle vient des données (G = 1), pas de la méthode.
- **Le bootstrap plat n'est pas un défaut du code.** Il reproduit fidèlement la loi empirique d'une seule grappe (principe de substitution). La règle actuelle (écart type nul, donc comparaison directe de l'estimation au budget) prend ce bootstrap dégénéré « at face value », ce que Cameron et Miller déconseillent. `boot.ci` réagirait au contraire par un refus.

### Gaps
- Je n'ai lu ni Davison et Hinkley (1997) ni Canty et al. (2006) : je ne peux pas citer leur recommandation précise pour des répliques indéfinies ou constantes.
- Je n'ai trouvé aucune source qui tranche entre écarter et imputer les répliques 0/0 dans un bootstrap par grappes d'un ratio.

## 6. Conséquence directe pour le projet : dans une cellule portée par une seule tâche, un excès observé a-t-il un poids de preuve sur le taux de la population ? Sous quelles hypothèses ?

### Takeaway
Sans hypothèse sur le groupement des erreurs dans la tâche, un excès observé dans une cellule à une seule tâche porteuse n'a aucun poids de preuve fréquentiste sur le taux de la population de tâches : à ρ = 1, la taille effective vaut 1. Sous l'hypothèse la plus favorable (écritures indépendantes, ρ = 0), une erreur en 20 à 60 écritures à enjeu faible donne encore p = 0,095 à 0,26 contre le budget de 0,5 pour 100, donc aucun dépassement établi. Le poids de preuve dépend entièrement d'une corrélation intra-tâche invérifiable avec une seule tâche. L'option (b) reproduit le défaut de R et de Stata, la pratique du NCHS et le choix déjà fait par le projet pour R4.

### Cited Findings
- **Seule voie valide à une grappe traitée : grappes de même taille et corrélation intra-grappe limitée** ; sinon « serious errors of inference when G1 = 1 » — [MacKinnon & Webb 2018](https://www.econ.queensu.ca/sites/econ.queensu.ca/files/qed_wp_1364.pdf)
- **Les méthodes qui marchent avec une seule grappe traitée** le font « only because [...] they do not allow for unrestricted heteroskedasticity » — [MNW 2023](https://arxiv.org/abs/2205.03285)
- **Facteur de Moulton.** Le facteur d'inflation de l'écart type, quand on ignore les grappes, est √(1 + ρ_x ρ_u (N_g − 1)), illustré par « √(1 + (1 × 0.018 × (0.20 × 65685/51 − 1))) = 2.38 » — [Cameron & Miller 2015](http://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015_February.pdf)
- **Unité certaine.** Une UPE certaine ne contribue pas à la variance du premier degré — [Lumley](https://r-survey.r-forge.r-project.org/survey/exmample-lonely.html) ; « Certainty units contribute nothing to the standard error » — [Stata, svyset](https://www.stata.com/manuals/svysvyset.pdf)
- **Pratique de publication.** Une estimation signalée ou supprimée porte une note qui en dit la raison — [NCHS 2017](https://www.cdc.gov/nchs/data/series/sr_02/sr02_175.pdf)
- **Contexte interne** (non externe, pour mémoire) : `PLAN_EXPERIENCE.md`, 5.13 et 5.14. La taille effective à ρ = 1, (Σm)² ÷ Σm², y est « la seule valeur valable sans hypothèse sur la corrélation ». ρ̂ n'est « pas calculable » avec une seule tâche. R4 renvoie « preuves insuffisantes » quand la preuve manque. Le rapport du contrôle 3 (section 9.3, point 5 ; section 10.7) mesure un faux R1 sur 30 dans le monde V et une exposition de 6 répétitions sur 12 dans A, 3 sur 12 dans E.

### Inferences
- **À ρ = 1 (aucune hypothèse), une seule tâche donne n_eff = 1.** La borne basse unilatérale de Clopper-Pearson à 95 %, quantile 5 % de Bêta(f, 2 − f), ne dépasse le budget que si la part f des écritures de cette tâche qui sont des erreurs déléguées dépasse :
  - 60,9 % à enjeu faible ;
  - 42,5 % à enjeu moyen ;
  - 32,4 % à enjeu fort.

  En pratique, une cellule à une seule tâche n'établit donc jamais de dépassement sans hypothèse.
- **À ρ = 0 (écritures indépendantes, hypothèse la plus favorable),** le test binomial exact de « au moins une erreur » contre le budget donne :

  | Écritures n | Faible (0,005/écriture) : 1 erreur | Faible : 2 erreurs | Moyen (0,0005) : 1 erreur | Fort (0,00005) : 1 erreur |
  |---|---|---|---|---|
  | 20 | 0,095 | 0,0045 | 0,010 | 0,0010 |
  | 40 | 0,18 | 0,017 | 0,020 | 0,0020 |
  | 60 | 0,26 | 0,037 | 0,030 | 0,0030 |

  Le cas observé (aviation, enjeu faible, 20 à 60 écritures) ne serait donc pas significatif même en ignorant tout groupement. À enjeu moyen ou fort, une seule erreur serait significative, mais seulement sous ρ = 0.
- **Entre les deux, la taille effective vaut n_eff = m ÷ (1 + (m − 1)ρ).** Pour m = 40 : 13,6 à ρ = 0,05 ; 8,2 à 0,1 ; 3,1 à 0,3 ; 2,0 à 0,5.

  Le verdict bascule donc selon ρ, qui n'est pas estimable avec une tâche. Une estimation issue d'une tâche tirée au hasard reste sans biais pour le taux moyen : elle garde une valeur descriptive, mais son incertitude est inconnue.
- **Lecture des options :**
  - **(a) garder la règle.** C'est le traitement `certainty` : non prudent ; contraire à la cible « population de tâches » du bootstrap et à la section 8 ; aucun logiciel de référence ne l'applique par défaut.
  - **(b) amender.** C'est le défaut de R (`fail`) et de Stata (`missing`), plus le signalement avec note du NCHS ; c'est aussi la logique de R4 (« preuves insuffisantes »). Elle ne coûte presque rien en puissance face à toute méthode sans hypothèse, puisqu'à ρ = 1 rien n'est établissable. Elle ne coûte de la puissance que sous ρ = 0 aux enjeux moyen et fort ; or les cellules à une porteuse observées sont toutes en aviation à enjeu faible.
  - **(c) un minimum de k tâches porteuses.** La littérature soutient k ≈ 5 à 6 pour les tests par rééchantillonnage (Cai et al. ; échecs à G1 = 2). Le projet a mesuré le max-T entre 5 et 11 porteuses. La zone de 2 à 4 n'est pas mesurée : une simulation y serait nécessaire avant de fixer k > 2.
  - **(d) une borne de Clopper-Pearson à ρ = 1 sur n_eff pour les cellules à peu de porteuses.** Elle prolonge 5.13 et R4 et varie continûment avec G ; à G = 1 elle équivaut à (b) en pratique. Deux limites : sa validité est prouvée à zéro erreur, approchée au-delà ; et la combiner au max-T sur plusieurs cellules exige un partage du risque de type Bonferroni.
  - **(e) emprunter la variance entre tâches à d'autres cellules** (analogue de `average`, `scaled` ou Conley et Taber). C'est une inférence sous modèle. Lumley réserve `average` aux UPE isolées manquantes au hasard ; ici, la porteuse unique vient de la rareté de l'action en aviation, une cause structurelle.
  - **(f) wild bootstrap, changements de signe ou randomisation.** Impossibles ou trompeurs à G = 1 : la plus petite valeur p est 1/2, le WCR ne rejette jamais, le WCU sur-rejette.
- **Multiplicité.** Retirer du max-T, par une règle écrite d'avance, les cellules qui ne peuvent rien établir ne gonfle pas le risque global des autres, à condition que la règle n'utilise que le nombre de tâches porteuses et pas les erreurs. Tarone (1990, Biometrics 46) écarte de même les hypothèses dont la plus petite valeur p atteignable ne peut franchir le seuil, avant la correction et éventuellement avant la collecte, ce qui rend la procédure plus puissante que Bonferroni (d'après le résumé de recherche) — [Zhu & Guo, arXiv 1711.08147](https://arxiv.org/pdf/1711.08147) ; [MHTdiscrete, Tarone.p.adjust](https://rdrr.io/cran/MHTdiscrete/man/Tarone.p.adjust.html). Je déduis l'analogie ; ni Tarone ni Zhu et Guo ne traitent des tâches porteuses. Dans `maxt.py`, une cellule à écart type quasi nul peut en outre gonfler c* : l'écarter aiderait les autres cellules.

### Gaps
- Je n'ai trouvé aucune source sur le « poids de preuve » d'un excès venu d'une seule grappe en termes de vraisemblance (Royall) ou en bayésien.
- Je n'ai trouvé aucune source sur le max-T de Westfall et Young avec des cellules d'écart type nul. La règle « hors du maximum, jugée sur l'estimation » n'a pas de précédent dans la littérature lue.
- Je n'ai pas vérifié si une erreur dans l'unique tâche serait un événement réellement aléatoire entre les K ordres et tirages du validateur ou quasi déterministe. Cela change la lecture de ρ, mais demande le code du moteur, hors périmètre.
