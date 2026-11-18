# Plans d'acceptation et démonstration de fiabilité : « rejet / clairement mauvais » vs « preuve insuffisante », sous défauts groupés

Légende : **[ouvert]** = document ouvert et lu (texte ou OCR). **[moteur]** = résumé du moteur de recherche, page non ouverte : à revérifier avant toute citation publique. Les « Inferences » sont mes déductions, pas des faits sourcés.

## Q1 — AQL, LTPD/RQL, risques fournisseur et client, courbes OC : où est la zone de rejet par rapport à la zone d'indifférence ? Quels rapports LTPD/AQL ?

### Takeaway
Un plan classique se fixe par deux points de sa courbe OC : le risque fournisseur α au niveau « bon » (AQL, p1, θ0) et le risque client β au niveau « mauvais » (LTPD, p2, θ1). Entre les deux s'étend une zone grise sans garantie. Le « rejet » classique est calibré pour rester rare au niveau *bon*. Il ne veut pas dire « clairement mauvais » : un lot pile au LTPD est rejeté avec une probabilité 1 − β, soit environ 90 %. En fiabilité, le rapport de discrimination usuel va de 1,5 à 3, et 2 est la valeur courante. Pour les plans par attributs, je n'ai trouvé aucune source primaire donnant un rapport LTPD/AQL « usuel ».

### Cited Findings
- AQL : « a percent defective that is the base line requirement for the quality of the producer's product ». LTPD : « a designated high defect level that would be unacceptable to the consumer » [ouvert] — [NIST e-Handbook 6.2.2](https://www.itl.nist.gov/div898/handbook/pmc/section2/pmc22.htm)
- Risque fournisseur (erreur de type I) : « the probability, for a given (n,c) sampling plan, of rejecting a lot that has a defect level equal to the AQL ». Risque client (type II) : probabilité « of accepting a lot with a defect level equal to the LTPD ». La courbe OC trace P(acceptation) en fonction de la fraction défectueuse. Valeurs typiques données pour α et β : de 0,2 à 0,01 [ouvert] — [NIST 6.2.2](https://www.itl.nist.gov/div898/handbook/pmc/section2/pmc22.htm)
- Plan simple (n,c) : « the lot is rejected if there are more than c defectives in the sample ». On le choisit de deux façons : des tables centrées sur l'AQL *ou* sur le LTPD (MIL-STD-105D), ou bien deux points imposés sur la courbe OC [ouvert] — [NIST 6.2.3](https://www.itl.nist.gov/div898/handbook/pmc/section2/pmc23.htm)
- Méthode des deux points : p1 = AQL avec α, p2 = LTPD avec β. Les deux équations binomiales sont non linéaires, donc on résout par itération [ouvert] — [NIST 6.2.3.2](https://www.itl.nist.gov/div898/handbook/pmc/section2/pmc232.htm)
- LQAS (santé publique), mêmes concepts sous d'autres noms :
  - seuil haut p_u : proportion « at or above which a lot … should be classified as suboptimal » ;
  - seuil bas p_l : proportion « at or below which a lot should be classified to have sufficient quality » ;
  - contraintes : P(X < d | n, p_u) ≤ α_max et P(X ≥ d | n, p_l) ≤ β_max ;
  - zone grise : « The area between the two thresholds, often referred to as the grey area, has less discernible classification properties ».
  - Attention : dans cette littérature, α désigne le risque au seuil *mauvais*, à l'inverse du NIST. [ouvert] — [Hedt-Gauthier et al. 2013, Emerg Themes Epidemiol 10:11](https://pmc.ncbi.nlm.nih.gov/articles/PMC3819670)
- Fiabilité (démonstration MTBF, d'après MIL-HDBK-781) :
  - α = probabilité de rejeter un équipement dont le MTBF vrai dépasse θ0 (point haut) ; β = probabilité d'accepter un équipement dont le MTBF est sous θ1 (point bas) ;
  - « The upper test point (θ0) is the value on which the reject criteria are based » ; θ1 est la valeur sur laquelle reposent les critères d'acceptation ;
  - d = θ0/θ1 ; « The values of d in practicable plans normally range between 1.5 and 3. A commonly used value is 2 » ;
  - plus d est grand, plus le test est court, mais le θ0 élevé qui sert de base au risque fournisseur peut devenir inacceptable. [ouvert] — [Applied R&M Manual for Defence Systems GR-77, Part D, ch. 10, §2.2–2.3](https://sars.org.uk/BOK/Applied%20R&M%20Manual%20for%20Defence%20Systems%20(GR-77)/p4c10.pdf)
- Le risque fournisseur « is commonly chosen to be the same as that for the consumer but there is no mathematical requirement for this » [ouvert] — [GR-77 ch. 10, Leaflet 1 §2.5](https://sars.org.uk/BOK/Applied%20R&M%20Manual%20for%20Defence%20Systems%20(GR-77)/p4c10.pdf)
- Hald (1978) décrit trois systèmes : LTPD, AOQL et IQL. Points relevés :
  - les contraintes sont posées « to get protection against the effects of outliers » ;
  - LTPD avec β = 0,10 : on retrouve le système Dodge-Romig ;
  - « The choice of [LTPD] is based on technological considerations whereas the choice of β to a large extent is arbitrary » (le symbole du LTPD est illisible à l'OCR) ;
  - IQL : on impose P(acceptation) = ½ à l'« Indifference Quality Level », égal à la qualité d'équilibre des coûts (proposition attribuée à Weibull). [ouvert, OCR] — [Hald, *On the Statistical Theory of Sampling Inspection by Attributes*, preprint IMS Copenhague 1978 n° 10](https://www.math.ku.dk/bibliotek/arkivet/preprints-fra-ims/1978/preprint_1978_-_no_10_hald__anders_-_on_the_statistical_theory_of_sampling_inspection_by_attributes.pdf)
- Exemple chiffré NIST (plan séquentiel) : p1 = 0,01, p2 = 0,10 (rapport 10), α = 0,05, β = 0,10 [ouvert] — [NIST 6.2.6](https://www.itl.nist.gov/div898/handbook/pmc/section2/pmc26.htm)
- Cibles « typiques » α ≈ 0,05 à l'AQL et β ≈ 0,10 au LTPD. Un rapport p2/p1 proche de 1 exige un très grand échantillon. Source : un éditeur de calculateurs, donc secondaire [moteur] — [MetricGate, producer and consumer risk](https://metricgate.com/docs/producer-and-consumer-risk/)

### Inferences
- **Le « rejet » classique protège le client, il ne qualifie pas un produit de mauvais.** En démonstration MTBF, le rejet est calibré à θ0, qui vaut d × le minimum acceptable. Dans le plan III-D (d = 2, β réel 12,79 %), un équipement pile au minimum θ1 est rejeté environ 87 % du temps. Un R4 qui doit signifier « clairement mauvais » demande donc le calibrage inverse :
  - faux R4 rare à la barre : P(R4 | p = barre) ≤ α_R4, la barre jouant le rôle d'un « AQL du R4 » ;
  - puissance à k × barre : P(R4 | p = k·barre) ≥ 1 − β_R4, k × barre jouant le rôle d'un « RQL du R4 ».
- **La délégation suit le calibrage habituel, protecteur du client :** P(déléguer | p ≥ barre) petit. Il faut donc deux contraintes OC distinctes, et la zone barre < p < k·barre revient de droit à « preuve insuffisante ». C'est la logique de la zone grise LQAS.
- **La règle actuelle de R4 est un plan IQL, pas un plan RQL.** Une règle « estimation ponctuelle (médiane) vs barre » place la frontière sur la barre elle-même : par construction, P(R4) avoisine ½ pour un type situé pile à la barre. Elle ne peut pas porter le sens « clairement mauvais ».
- Le choix de k joue le rôle du rapport de discrimination. La fiabilité utilise 1,5 à 3 (2 courant) avec des risques de 10 à 20 %. Un k plus grand raccourcit l'évaluation pour un même α et une même puissance, mais n'atteste que d'une mauvaise qualité plus grossière.

### Gaps
- Aucun rapport LTPD/AQL « usuel » trouvé dans une source primaire pour les attributs (Schilling & Neubauer, Montgomery, tables de Cameron et ISO 2859 non consultés, accès payant). Seuls trouvés : l'analogue fiabilité (d de 1,5 à 3) et des exemples isolés (rapport 10 au NIST).
- Courbes OC de type A et de type B (lot isolé vs processus) : pas de source obtenue.

## Q2 — SPRT de Wald avec p0 = barre et p1 = k × barre : accepter / rejeter / continuer. Comment rendre compte de « continuer » quand le test doit s'arrêter (SPRT tronqué) ?

### Takeaway
Le SPRT binomial donne deux droites parallèles : au-dessus on rejette, en dessous on accepte, entre les deux on continue. Dans les normes de fiabilité (MIL-HDBK-781, IEC 61123), la troncature *force* une décision binaire : acceptation à la limite de durée, rejet à la limite de défaillances. Les risques réels s'écartent alors des risques nominaux. Le seul cadre trouvé qui garde « non concluant » comme verdict à part entière est celui des essais de phase II à trois issues (Storer 1992, Sargent et al. 2001), plus la zone grise du LQAS.

### Cited Findings
- SPRT par attributs (NIST) :
  - on porte le cumul des défectueux contre le nombre d'unités inspectées ; « As soon as a point falls on or above the upper line, the lot is rejected » ; sur la droite basse on accepte ; entre les deux on continue ;
  - droite d'acceptation x_a = −h1 + s·n, droite de rejet x_r = h2 + s·n ;
  - k = log[p2(1−p1)/(p1(1−p2))] ; h1 = log((1−α)/β)/k ; h2 = log((1−β)/α)/k ; s = log((1−p1)/(1−p2))/k. [ouvert] — [NIST 6.2.6](https://www.itl.nist.gov/div898/handbook/pmc/section2/pmc26.htm)
- Exemple NIST (p1 = 0,01, p2 = 0,10, α = 0,05, β = 0,10) :
  - x_a = −0,939 + 0,04n et x_r = 1,205 + 0,04n ;
  - le rejet est possible dès **2 défectueux** pour n = 2 à 19, puis à 3 à partir de n = 20 ;
  - l'acceptation (0 défectueux) n'est possible qu'à partir de n = 24 ;
  - les cases « pas de décision possible » sont notées « x » ;
  - plan simple équivalent : (52, 2). [ouvert] — [NIST 6.2.6](https://www.itl.nist.gov/div898/handbook/pmc/section2/pmc26.htm)
- Troncature selon le NIST : « The process can theoretically last until the lot is 100% inspected ». Règle empirique : tronquer à trois fois la taille du plan simple correspondant. Rien n'est dit de la décision prise à la troncature. L'efficacité se mesure par l'ASN (taille moyenne d'échantillon) [ouvert] — [NIST 6.2.6](https://www.itl.nist.gov/div898/handbook/pmc/section2/pmc26.htm)
- SPRT de fiabilité (d'après MIL-HDBK-781) :
  - rejet si f ≥ s·t + h1, acceptation si f ≤ s·t − h0, poursuite si s·t − h0 < f < s·t + h1 ;
  - des limites de troncature en défaillances et en durée sont ajoutées « to prevent the test extending indefinitely possible when an MTBF between the upper and lower test points is exhibited » ;
  - h1 contient un facteur correctif (1+d)/2d « to reduce the differences between the consumer's and producer's risks arising from test truncation ». [ouvert] — [GR-77 ch. 10, §4.2–4.8](https://sars.org.uk/BOK/Applied%20R&M%20Manual%20for%20Defence%20Systems%20(GR-77)/p4c10.pdf)
- Plan MIL-HDBK-781 III-D (α = β = 10 %, d = 2), table d'acceptation et de rejet :
  - rejet à 16 défaillances ;
  - acceptation à la durée de troncature 20,60 (en unités de θ1) avec 15 défaillances ou moins ;
  - aucune case « non concluant » ;
  - risques réels α = 12,82 % et β = 12,79 % pour 10 % visés, à cause de l'arrondi à des nombres entiers de défaillances. [ouvert] — [GR-77 ch. 10, §2.4.3 et Table 1](https://sars.org.uk/BOK/Applied%20R&M%20Manual%20for%20Defence%20Systems%20(GR-77)/p4c10.pdf)
- Le séquentiel a une durée maximale plus longue même tronqué, mais une durée espérée plus courte quand le vrai MTBF atteint au moins θ0. Il peut être plus long que le test fixe quand le MTBF est « midway » entre les deux points [ouvert] — [GR-77 ch. 10, §2.1.4 et §2.5.3](https://sars.org.uk/BOK/Applied%20R&M%20Manual%20for%20Defence%20Systems%20(GR-77)/p4c10.pdf)
- IEC 61123:2019 (taux de succès, essais succès/échec) :
  - plans « for fixed trial/failure terminated tests as well as truncated sequential probability ratio tests (SPRTs) » ;
  - SPRT « significantly truncated (the maximum trial numbers are low) » sans hausse substantielle du nombre espéré d'essais avant décision (ENT) ;
  - large plage de taux d'échec, de risques et de rapports de discrimination, risques inégaux admis ;
  - hypothèse : probabilité de succès constante d'un essai à l'autre, événements indépendants. [ouvert] — [IEC webstore, IEC 61123:2019](https://webstore.iec.ch/en/publication/61933)
- Un SPRT tronqué avec plafond N doit trancher au plafond « even though the sample still spans the neutral region » [moteur] — [arXiv quant-ph/0402181](https://arxiv.org/pdf/quant-ph/0402181)
- Tronquer garantit une décision après au plus ℓ étapes, mais pour un ℓ petit les deux taux d'erreur augmentent [moteur] — [arXiv 1502.03722](https://arxiv.org/pdf/1502.03722)
- Thèses NPS :
  - Petersen (1980) : tout SPRT de Bernoulli possède un « natural truncation point » qui ne dépasse pas les risques visés ;
  - Lewis (1992) : modifier ce point ou la règle d'acceptation peut écarter la courbe OC de façon inacceptable.
  - [moteur] — [Calhoun NPS 1](https://calhoun.nps.edu/entities/publication/7af6f38e-7bf7-4593-b12d-3a12630af641) ; [Calhoun NPS 2](https://calhoun.nps.edu/entities/publication/59bc655d-c02d-4b32-b92c-362c3101782b)
- Selon une thèse de l'université d'Arizona, les plans séquentiels de MIL-STD-781 ne tiennent pas leurs risques nominaux, et leur troncature suit la théorie des échantillons fixes [moteur] — [repository.arizona.edu 10150/185264](https://repository.arizona.edu/handle/10150/185264)
- Plans à trois issues :
  - Storer (1992), « A class of phase II designs with three possible outcomes », Biometrics 48(1):55–60 : on peut ne rejeter ni H0 : p ≤ p1 ni Ha : p ≥ p2 quand le taux observé tombe entre les deux ;
  - Sargent, Chan et Goldberg (2001), « A three-outcome design for phase II clinical trials », Controlled Clinical Trials 22(2):117–125 : une région « inconclusive » bornée par deux seuils.
  - [moteur] — [Mayo Clinic, notice Sargent et al.](https://mayoclinic.elsevierpure.com/en/publications/a-three-outcome-design-for-phase-ii-clinical-trials/) ; [NEJSDS art. 94](https://nejsds.nestat.org/journal/NEJSDS/article/94)

### Inferences
- **Un SPRT par action (p0 = barre, p1 = k·barre) n'est valide que sous indépendance.** C'est l'hypothèse explicite d'IEC 61123. L'exemple NIST le montre : avec un rapport 10, **deux** erreurs suffisent à rejeter tôt. Si ces deux erreurs viennent de la même tâche (ρ élevé), le α nominal ne tient plus. C'est précisément le mécanisme des faux R4 observés.
- **Suivre les normes à la troncature casserait la sémantique de R4.** Elles forcent un verdict binaire. Pour que R4 garde le sens « clairement mauvais », il faut :
  - que R4 ne tombe qu'au franchissement de la frontière de rejet ;
  - que la troncature sans franchissement donne « preuve insuffisante » (logique Storer et Sargent, zone grise LQAS) ;
  - que la courbe OC soit calculée troncature comprise, puisque les risques réels diffèrent des nominaux (12,82 % pour 10 % dans le plan III-D).
- Le protocole a deux frontières pour deux décisions :
  - délégation : calibrée contre p ≥ barre ;
  - R4 : calibrée contre p ≤ barre, avec puissance à k·barre.
  
  Cela ressemble à deux SPRT juxtaposés, ou à une procédure séquentielle à trois décisions (voir Gaps).

### Gaps
- La règle de troncature de Wald lui-même (*Sequential Analysis*, 1947, §3.8 selon une source) n'a pas été vérifiée. Ne pas la citer sans lecture.
- Le moteur prête à IEC 61123 une décision « accepter / rejeter / continuer » après chaque essai, et un ENT 1,4 à 1,8 fois plus petit que l'essai fixe pour p ≤ p0. Non confirmé sur la page IEC.
- La procédure séquentielle à trois hypothèses de Sobel et Wald (1949) n'a pas été vérifiée dans cette recherche.

## Q3 — Démonstration de fiabilité : comment se définit un verdict d'échec ? Les normes (MIL-HDBK-781, IEC 61124, ISO 2859, ISO 3951) distinguent-elles « non démontré » et « échec démontré » ?

### Takeaway
Aucune des normes consultées ne pose « non démontré » et « défaillance démontrée » comme deux verdicts formels distincts. Le rejet d'un essai de conformité est calibré par α au point haut θ0 : il signifie « ne satisfait pas l'objectif, au risque α », pas « nettement sous le minimum ». Dans la filiation Dodge, le CSP-1 n'a même aucun état de rejet. L'équivalent le plus proche d'un « arrêt pour mauvaise qualité » est l'interruption du contrôle prévue par les règles de passage d'ISO 2859-1, ainsi que les règles d'arrêt ajoutées au CSP-1 (Murphy 1958–1959).

### Cited Findings
- « there is a risk that a pass result may be obtained with equipment that is actually outside the specification. Similarly a fail result may occur with equipment that is actually inside the specification ». Ramener ces risques à zéro « would require an infinitely long test » [ouvert] — [GR-77 ch. 10, §2.2.1](https://sars.org.uk/BOK/Applied%20R&M%20Manual%20for%20Defence%20Systems%20(GR-77)/p4c10.pdf)
- Le risque fournisseur α porte sur le rejet d'un équipement dont le MTBF vrai dépasse θ0. Les critères de rejet reposent sur θ0, objectif minimal de conception du fournisseur. Les critères d'acceptation reposent sur θ1, minimum acceptable pour le client [ouvert] — [GR-77 ch. 10, §2.2.2–2.3.3](https://sars.org.uk/BOK/Applied%20R&M%20Manual%20for%20Defence%20Systems%20(GR-77)/p4c10.pdf)
- Règle de 3 : avec N essais i.i.d. sans erreur, p ≤ 3/N à 95 % (2/N à 90 %). « a test of 300 independent samples returning no errors can be said with 95% confidence to have an error rate of 1% or less » [ouvert] — [Mansfield & Wayman 2002, NPL CMSC 14/02, §85](https://www.face-rec.org/databases/Mansfield02.pdf)
- Calculateur PRST de MIL-HDBK-781A :
  - d = MTBF haut / MTBF bas ; un d proche de 1 élargit la zone d'indécision et allonge le test ;
  - exemple : MTBF bas 100 h, d = 1,5, risques de 5 %, soit au moins 883 h pour accepter sans défaillance et 6 800 h au plus avec troncature. [moteur] — [Reliability Analytics, Sequential Reliability Test Calculator](https://reliabilityanalytics.com/blog/2013/05/16/sequential-reliability-test-calculator/)
- Un rapport DTIC sur MIL-STD-781C préconise les plans PRST quand on veut un test séquentiel aux risques de décision de 10 à 20 % [moteur] — [DTIC ADA063875](https://apps.dtic.mil/sti/pdfs/ADA063875.pdf)
- Le NIST a repris le PRST tronqué de MIL-HDBK-781A comme référence pour la qualification des taux d'erreur (systèmes de vote) : « theoretical formulas lead to somewhat different numbers, but we use numbers from MIL-HDBK-781A tables as the reference ». C'est un usage direct du PRST pour un *taux d'erreur*, pas pour un MTBF [moteur] — [NIST, Error rate qualification testing](https://nist.gov/document/9-errorratequalificationtestingpdf)
- IEC 61123 couvre les taux de succès ; pour un taux de défaillance constant, c'est IEC 61124 qui s'applique [moteur pour IEC 61124] — [IEC 61123:2019](https://webstore.iec.ch/en/publication/61933)
- ISO 2859-1, règles de passage : les libellés du schéma comprennent « 5 batches not accepted while on tightened inspection », condition d'interruption du contrôle, et « 2 of 5 or fewer consecutive batches not accepted ». La page ne dit rien de la reprise [ouvert, libellés du schéma seulement] — [SQC Online, Switching rules ISO 2859-1](https://www.sqconline.com/switching-rules-iso-2859-1)
- Selon le résumé d'ISO 2859-1, les règles de passage protègent le client (« by means of a switch to tightened inspection or discontinuation of sampling inspection ») si la qualité se détériore. Pour les lots isolés, ce résumé renvoie à ISO 2859-2, indexée par la qualité limite (LQ) [moteur] — [ANSI webstore ISO 2859-1](https://webstore.ansi.org/standards/iso/iso28591999) ; [Quality Magazine, troisième révision d'ISO 2859-1](https://www.qualitymag.com/articles/99511-third-revision-of-iso-2859-1)
- Selon Quality Magazine (mai 2026), le projet final de la 3e édition d'ISO 2859-1 a été approuvé en décembre 2025 mais reste à corriger avant publication [moteur] — [Quality Magazine, mai 2026](https://digitaledition.qualitymag.com/may-2026/quality-edge/)
- CSP-1 (Dodge 1943) : contrôle à 100 % jusqu'à i unités conformes consécutives, puis échantillonnage à la fraction f ; tout défaut trouvé renvoie au 100 % [moteur] — [Hryniewicz, WITZ](https://www.wit.edu.pl/dokumenty/wydawnictwa_naukowe/zeszyty_naukowe_WITZ_04/002_Hryniewicz-WITZ-jwo.pdf)
- MIL-STD-1235B (CSP-1 et dérivés) n'est plus soutenue par le DoD depuis le milieu des années 1990 ; ASTM E2819-11 l'a reprise. Cette pratique précise quand commencer le 100 %, quand passer à l'échantillonnage et quand revenir au 100 % [moteur] — [ASTM E2819](https://store.astm.org/e2819-11r15.html) ; [Nimonik ASTM E2819](https://standards.nimonik.com/products/astm/e2819/)
- Règles d'arrêt ajoutées au CSP-1, dont le contenu n'a pas été lu (existence confirmée par des listes de références) :
  - Murphy, « A Criterion to Limit Inspection Effort in Continuous Sampling Plans », Bell System Technical Journal, 1958 ;
  - Murphy, « Stopping Rules With CSP-1 Sampling Inspection Plans in Continuous Production », Industrial Quality Control 16(5), nov. 1959, p. 10–16.
  - [moteur] — [Nokia Bell Labs, notice](https://nokia.com/bell-labs/publications-and-media/publications/a-criterion-to-limit-inspection-effort-in-continuous-sampling-plans) ; [liste de références, JQT 1970](https://informahealthcare.com/doi/ref/10.1080/00224065.1970.11980401)
- Selon le résumé d'un article plus récent, ajouter une règle d'arrêt au CSP préserve ses caractéristiques statistiques de base, à condition que l'arrêt ne survienne que si la dernière unité inspectée en phase 100 % est défectueuse [moteur] — [CSP-1 with stopping inspection rule (n*−1)](https://applmath.cjoe.ac.cn/jweb_yysxxb/EN/10.12387/C1996018)

### Inferences
- **Échouer à démontrer ne prouve pas la mauvaise qualité.** Ne pas atteindre la règle de 3 ni une série de N succès, c'est seulement « non démontré ». Le vocabulaire des normes n'offre pas de verdict « échec démontré » distinct ; il faut le construire avec sa propre courbe OC, comme en Q1 : α à la barre, puissance à k·barre.
- **Le CSP-1 ne dit jamais « mauvais ».** Il reste en 100 %, comme la règle de délégation du protocole. L'analogue historique de R4 est une règle d'arrêt greffée sur le CSP (Murphy) ou l'interruption d'ISO 2859-1. Dans les deux cas, le déclencheur est une *accumulation* de non-acceptations sur plusieurs lots, pas une seule mauvaise estimation ponctuelle.

### Gaps
- Textes intégraux de MIL-HDBK-781A, IEC 61124, ISO 2859-1/-2/-5 et ISO 3951 non consultés (payants ou scannés). ISO 3951 (contrôle par mesures) n'a pas été étudiée du tout.
- Libellé exact du verdict négatif dans IEC 61123/61124 (« non-conformité » ? « rejet » ?) : non trouvé.
- Contenu des règles d'arrêt de Murphy (1958–1959) : non lu.

## Q4 — Défauts groupés ou surdispersés : plans composés ou bêta-binomiaux, variation d'un lot à l'autre. Comment changent la courbe OC et la règle de rejet ?

### Takeaway
La surdispersion est la norme empirique : selon Hald, la plupart des distributions réelles de qualité des lots suivent une bêta-binomiale. Ignorer le regroupement fait dépasser les risques nominaux. Exemple LQAS : α passe de 0,098 à 0,173 et β de 0,080 à 0,127 quand le ρ vrai vaut 0,2 au lieu de 0,01 (4 grappes de 5). Les parades sourcées sont trois :
- calibrer la règle sur une loi bêta-binomiale avec un ρ prudent ;
- échantillonner plus de grappes, ce qui compte plus que d'échantillonner plus d'unités ;
- raisonner en taille d'échantillon effective.

### Cited Findings
- « Suppose that the process average varies at random from lot to lot. The lot quality distribution then becomes a mixed binomial ». « According to my experience most empirical lot quality distributions may be described rather well by a beta-binomial distribution ». Réserve : les « outliers », c'est-à-dire les lots d'une période hors contrôle [ouvert, OCR] — [Hald 1978](https://www.math.ku.dk/bibliotek/arkivet/preprints-fra-ims/1978/preprint_1978_-_no_10_hald__anders_-_on_the_statistical_theory_of_sampling_inspection_by_attributes.pdf)
- Avec une loi a priori continue de p, l'inspection a un double objet : « (1) to reject outliers, and (2) to sort out lots of unsatisfactory quality from normal production ». « The properties of the solution for a continuous prior are thus fundamentally different from the properties for a degenerate prior ». Hald juge ce modèle « usually … more realistic than the classical assumption » [ouvert, OCR] — [Hald 1978](https://www.math.ku.dk/bibliotek/arkivet/preprints-fra-ims/1978/preprint_1978_-_no_10_hald__anders_-_on_the_statistical_theory_of_sampling_inspection_by_attributes.pdf)
- LQAS en grappes (C-LQAS), avec m = nombre de grappes et k = taille par grappe :
  - loi bêta-binomiale paramétrée par l'ICC ρ, à fixer en plus des deux seuils et des deux risques ;
  - sans regroupement : n = 20, d = 3, α = 0,091, β = 0,075 ;
  - avec ρ = 0,1 : n va de 20 (20 grappes de 1) à 136 (2 grappes de 68) ;
  - plan conçu pour ρ = 0,01 (4 grappes de 5, d = 3) : α = 0,173 et β = 0,127 si le ρ vrai vaut 0,2, contre 0,098 et 0,080 à ρ = 0,01 ;
  - si l'on ignore le regroupement, « the true misclassification risks are likely greater than the specified limits ». [ouvert] — [Hedt-Gauthier et al. 2013](https://pmc.ncbi.nlm.nih.gov/articles/PMC3819670)
- Même article :
  - « the total sample size increases as the number of clusters sampled decreases » ;
  - « The more clusters in the sample, the smaller the impact of the ICC » ;
  - « a conservative value of the ICC is ideal to protect against high misclassification errors » ;
  - il existe un nombre minimal de grappes, fonction de ρ, qu'aucune taille par grappe ne compense (formule illisible dans l'extraction). [ouvert] — [Hedt-Gauthier et al. 2013](https://pmc.ncbi.nlm.nih.gov/articles/PMC3819670)
- « Traditional lot quality assurance sampling (LQAS) methods require simple random sampling to guarantee valid results ». Les plans 67×3 et 33×6 restent à peu près valides sous une corrélation intra-grappe modérée. « The presence of intercluster correlation can impact dramatically the classification error » [ouvert, résumé] — [Olives et al. 2009, JRSS A 172(2):495–510](https://ideas.repec.org/a/bla/jorssa/v172y2009i2p495-510.html)
- Les méthodes en grappes « are not sensitive to the distributional assumptions » mais « can result in substantially different designs (sample sizes) depending on the clustering parameterization ». Et « none of the clustering parameterizations used in the existing methods appears to be consistent with the observed data » [ouvert, résumé] — [Hund, Bedrick & Pagano 2015, PLoS ONE 10(6)](https://econpapers.repec.org/RePEc:plo:pone00:0129564)
- Décomposition de la variance quand n personnes font chacune m tentatives : V(FNMR_obs) = σ²/n + (ρ(1−ρ) − σ²)/(mn). Ici ρ désigne le taux moyen et σ² la variance entre personnes. Une composante décroît en 1/(nombre de personnes), l'autre en 1/(nombre de tentatives) [ouvert] — [Mansfield & Wayman 2002, annexe B §202–204](https://www.face-rec.org/databases/Mansfield02.pdf)
- Les erreurs se concentrent sur certaines personnes (« goats », « lambs », « wolves »), d'où une composante de variance entre personnes non nulle. La formule binomiale « has sometimes been misapplied to cases where subjects make several attempts. The replacement of the number of subjects n, by the number of attempts nm, is generally not valid » [ouvert] — [Mansfield & Wayman 2002, §165 d, §168, §207](https://www.face-rec.org/databases/Mansfield02.pdf)
- La taille d'échantillon effective doit servir au calcul de puissance. Accroître le nombre de grappes améliore la puissance plus efficacement qu'accroître la taille des grappes. Les analyses qui ignorent le regroupement « may report significance where none exists » [moteur] — [Killip, Mahfoud & Pearce 2004, Ann Fam Med 2(3):204–208](https://www.annfammed.org/content/2/3/204.full.pdf)
- Effet de plan de Kish pour des grappes égales : DEFF = 1 + (m − 1)ρ, avec m la taille de grappe, et n_eff = n/DEFF. Source : un éditeur de calculateurs, donc secondaire [moteur] — [MetricGate, design effect (cluster)](https://metricgate.com/docs/design-effect-cluster/)
- Comptes de défauts par unité : courbes OC de plans par attributs sous un modèle gamma-Poisson, la loi gamma représentant la variation d'un lot à l'autre [moteur] — [Am. J. Math. Manag. Sci. 2007](https://informahealthcare.com/doi/full/10.1080/01966324.2007.10737695) ; [EQC 2011, plan en chaîne bayésien](https://www.degruyterbrill.com/document/doi/10.1515/EQC.2011.017/html)
- IEC 61123 suppose explicitement des essais indépendants à probabilité constante [ouvert] — [IEC 61123:2019](https://webstore.iec.ch/en/publication/61933)

### Inferences
- **La surdispersion aplatit la courbe OC.** P(R4) se calcule alors comme une moyenne sur la loi des taux par tâche (OC composée à la Hald), pas comme une binomiale. À n égal, la probabilité de franchir une frontière de rejet fixée en binomiale augmente aux p faibles : d'où des faux R4 à 0,2 × barre.
- **Pour un R4 robuste, calibrer la frontière à ρ_max.** On choisit ρ_max prudent, à préenregistrer, et on vérifie sur une bêta-binomiale que P(R4 | p = barre, ρ) ≤ α pour tout ρ ≤ ρ_max. La puissance à k·barre se rapporte alors au nombre de *tâches*, la vraie unité d'information.
- **Hald voit dans le rejet un détecteur d'« outliers ».** Transposé : une tâche qui concentre des erreurs ressemble à un lot hors contrôle. Mieux vaut la traiter comme un *événement* à diagnostiquer que comme une série de défauts indépendants qui suffiraient à conclure « mauvais ».
- Hund et al. montrent que la paramétrisation du regroupement change fortement la taille requise. Il faut donc préenregistrer le modèle de corrélation, ou un borne pire cas qui n'en dépend pas (voir Q5).

### Gaps
- Pas d'accès aux traitements bêta-binomiaux de Schilling & Neubauer, ni aux plans composés de Hald (1960, Technometrics).
- Effet des défauts corrélés sur la garantie d'AOQL du CSP-1 de Dodge : aucune source trouvée.
- Estimation de l'ICC pour une variable 0/1 (échelle latente ou échelle des probabilités) : pas de source primaire obtenue.

## Q5 — Exemples de « compter les grappes, pas les unités » (corrélation pire cas) pour une décision de rejet ?

### Takeaway
Aucune norme d'échantillonnage ISO ou MIL trouvée n'impose de compter les grappes. L'exemple le plus net vient des essais biométriques (NPL, Mansfield & Wayman 2002). Dans le cas « most pessimistic », la variance du taux d'erreur vaut p(1−p)/n où n est le nombre de *personnes*, non de tentatives. C'est exactement la borne obtenue avec ρ = 1. Le C-LQAS va dans le même sens : nombre minimal de grappes, et plus de grappes = plan plus prudent.

### Cited Findings
- Bornes de variance : dans le cas le plus optimiste, V(FNMR_obs) = ρ(1−ρ)/(mn) ; dans le plus pessimiste, V(FNMR_obs) = ρ(1−ρ)/n, avec n personnes et m tentatives chacune. « In real cases, the truth is somewhere between these extremes » [ouvert] — [Mansfield & Wayman 2002, annexe B §206](https://www.face-rec.org/databases/Mansfield02.pdf)
- « Ten enrolment-test sample pairs from each of a hundred people is not statistically equivalent to a single enrolment-test sample pair from each of a thousand people ». Les règles de 3 et de 30 « are over-optimistic, as they assume that error rates are due to a "single source of variability" » [ouvert] — [Mansfield & Wayman 2002, §84](https://www.face-rec.org/databases/Mansfield02.pdf)
- « The number of people tested is more significant than the total number of attempts in determining test accuracy ». Recommandation : d'abord un groupe de personnes le plus large possible, ensuite assez de tentatives par personne [ouvert] — [Mansfield & Wayman 2002, §90](https://www.face-rec.org/databases/Mansfield02.pdf)
- Le caractère i.i.d. « may be achieved if each genuine attempt uses a different volunteer ». Pour la règle de 30, « Strictly speaking this would require 3,000 enrolees », sinon il faut « compromise on independence … and … be prepared for a loss of statistical significance » [ouvert] — [Mansfield & Wayman 2002, §87 et note 5](https://www.face-rec.org/databases/Mansfield02.pdf)
- Exemple d'effort comparable : 200 personnes × 6 donnent 1 200 tentatives « (though not fully independent) », contre 240 personnes × 1, soit 240 tentatives indépendantes [ouvert] — [Mansfield & Wayman 2002, §88](https://www.face-rec.org/databases/Mansfield02.pdf)
- C-LQAS : il faut un nombre minimal de grappes même avec des grappes infiniment grandes. Plus de grappes est « a more conservative design ». Les systèmes à 4 grappes dépassent plus souvent les limites de risque quand le vrai ICC excède l'hypothèse [ouvert] — [Hedt-Gauthier et al. 2013](https://pmc.ncbi.nlm.nih.gov/articles/PMC3819670)

### Inferences
- **Une borne pire cas indépendante du modèle.** On garde le taux d'erreur par action comme paramètre, mais on borne sa variance par p(1−p)/n_tâches, ce qui revient à DEFF à ρ = 1, donc n_eff = nombre de tâches. Le contrôle du faux R4 tient alors quel que soit ρ (à indépendance entre tâches près), et la puissance à k·barre est une fonction connue du nombre de tâches.
- **Piège si l'on compte des tâches en échec (au moins une erreur).** Le paramètre change : le taux d'échec par tâche dépend de ρ et de m. Pour une tâche de m actions avec m > k, il vaut à peu près m·barre pour un agent à la barre avec ρ = 0, mais seulement k·barre pour un agent à k·barre avec ρ = 1. Les deux peuvent se confondre, et la puissance s'effondre. Mieux vaut un taux par action avec une variance robuste aux grappes, ou une bêta-binomiale à ρ_max, qu'un indicateur binaire par tâche.
- **Ce que le protocole peut préenregistrer pour R4 :**
  - frontière de rejet calibrée pour que P(R4 | p = barre) ≤ α sous le pire cas (ou sous bêta-binomiale à ρ_max) ;
  - puissance annoncée à k·barre en fonction du nombre de tâches indépendantes ;
  - troncature qui donne « preuve insuffisante », jamais R4.

### Gaps
- Aucune règle « compter les grappes » trouvée dans ISO 2859, ISO 3951 ou MIL-STD/HDBK.
- La distinction d'ISO 2859-1 entre « nonconforming items » et « nonconformities per 100 items » (une unité porteuse de plusieurs défauts compte une fois) pourrait être un analogue, mais aucune source ouverte ne l'a confirmé ici.
- Analyse par résumé de grappe des essais randomisés en grappes (Donner & Klar ; Hayes & Moulton) : non recherchée, hors périmètre de rejet.
