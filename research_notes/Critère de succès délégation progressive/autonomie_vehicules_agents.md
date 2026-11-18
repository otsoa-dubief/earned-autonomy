# Évaluer l'autonomie des véhicules automatisés et des agents IA : comment juge-t-on un schéma de délégation *utile*, et pas seulement *sûr* ?

Notes de recherche, 2026-11-06. Citations en anglais d'origine, entre guillemets ; le reste est en français. Ce que disent les sources figure dans « Cited Findings ». Mes déductions sont dans « Inferences ». Sauf mention contraire, chaque citation a été lue dans le texte primaire (PDF ou page officielle). Quand une donnée vient seulement d'un résumé secondaire, c'est dit.

## Q1 — Véhicules automatisés : que mesurent les niveaux SAE J3016 et les rapports de désengagement du DMV de Californie ? Comment traitent-ils un système qui ne conduit jamais seul ?

### Takeaway
J3016 ne mesure rien : un niveau est **attribué** selon l'intention de conception, n'implique aucune hiérarchie de mérite, et n'a de sens qu'accompagné de son domaine d'emploi (ODD). Les rapports de désengagement du DMV mesurent bien quelque chose, mais leur dénominateur est le **kilométrage parcouru en mode autonome**. Un système qui ne roule jamais seul ne produit donc aucun taux. En revanche, un système qui ne roule que sur des trajets faciles affiche un taux flatteur. C'est la critique principale de ce métrique, et la raison pour laquelle le DMV propose en 2026 de le remplacer par des taux d'événements rapportés aux véhicules-milles (VMT), immobilisations comprises.

### Cited Findings
**SAE J3016 (avril 2021)**
- Principe directeur du document : « Be descriptive and informative rather than normative. » — [SAE J3016_202104](https://www.sae.org/standards/content/j3016_202104/) (texte lu dans [une copie publique du PDF](https://ca-times.brightspotcdn.com/54/02/2d5919914cfe9549e79721b12e66/j3016-202104.pdf))
- §8.1 : « By itself, this document imposes no requirements, nor confers or implies any judgment in terms of system performance. » Une fonction qui ne satisfait pas la définition du niveau 4 ne doit pas, pour autant, être dite « non-compliant » ou « unsafe ». — [J3016 PDF](https://ca-times.brightspotcdn.com/54/02/2d5919914cfe9549e79721b12e66/j3016-202104.pdf)
- §8.2, titre : « Levels are Assigned, Rather than Measured, and Reflect the Design Intent for the Driving Automation System Feature as Defined by its Manufacturer ». Puis : « it is not possible to describe or specify a complete test or set of tests which can be applied to a given ADS feature to conclusively identify or verify its level of driving automation. » — [J3016 PDF](https://ca-times.brightspotcdn.com/54/02/2d5919914cfe9549e79721b12e66/j3016-202104.pdf)
- §8.2 : « the manifestation of one or more performance deficiencies in either the driving automation system or in the user's use of it does not automatically change the level assignment. » Exemple donné : une fonction conçue niveau 5 « would not automatically be demoted to Level 4 simply by virtue of encountering a particular road on which it is unable to operate the vehicle. » — [J3016 PDF](https://ca-times.brightspotcdn.com/54/02/2d5919914cfe9549e79721b12e66/j3016-202104.pdf)
- §8.2 : « it is incorrect to classify a Level 4 design-intended ADS feature equipped on a test vehicle as Level 2 simply because on-road testing requires a test driver to supervise the feature while engaged, and to intervene if necessary to maintain operation. » — [J3016 PDF](https://ca-times.brightspotcdn.com/54/02/2d5919914cfe9549e79721b12e66/j3016-202104.pdf)
- §8.3 : « the levels of driving automation do not specify or imply hierarchy in terms of relative merit, technology sophistication, or order of deployment. Thus, this taxonomy does not specify or imply that, for example, Level 4 is “better” than Level 3 or Level 2. » — [J3016 PDF](https://ca-times.brightspotcdn.com/54/02/2d5919914cfe9549e79721b12e66/j3016-202104.pdf)
- Les rôles sont ceux attendus par conception : « “Role” in this context refers to the expected role of a given primary actor, based on the design of the driving automation system in question and not necessarily to the actual performance of a given primary actor. » — [J3016 PDF](https://ca-times.brightspotcdn.com/54/02/2d5919914cfe9549e79721b12e66/j3016-202104.pdf)
- §6, rôle de l'ODD : « accurately describing a feature (other than at Levels 0 and 5) requires identifying both its level of driving automation and its operational design domain (ODD). As provided in the definitions above, this combination of level of driving automation and ODD is called a usage specification ». Un niveau 4 peut être trivial si l'ODD l'est : « Level 4 ADS-DVs that operate in enclosed courses have existed for many decades as people movers and airport shuttles. » et « This highly structured and simple ODD makes it technologically less challenging to achieve Level 4 driving automation. » — [J3016 PDF](https://ca-times.brightspotcdn.com/54/02/2d5919914cfe9549e79721b12e66/j3016-202104.pdf)
- §3.16, condition de risque minimal (MRC) : « A stable, stopped condition to which a user or an ADS may bring a vehicle after performing the DDT fallback in order to reduce the risk of a crash when a given trip cannot or should not be continued. » Note 4 sur le repli (fallback) : « At Levels 4 and 5, the ADS must be capable of performing the DDT fallback and achieving a minimal risk condition. » — [J3016 PDF](https://ca-times.brightspotcdn.com/54/02/2d5919914cfe9549e79721b12e66/j3016-202104.pdf)

**Rapports de désengagement (Californie)**
- Définition réglementaire, 13 CCR §227.50(a) : « "disengagement" means a deactivation of the autonomous mode when a failure of the autonomous technology is detected or when the safe operation of the vehicle requires that the autonomous vehicle test driver disengage the autonomous mode ». Le rapport annuel est dû « by January 1st, of each year ». Il indique « The party that initiated the disengagement (autonomous technology, autonomous vehicle test driver, remote operator, or passenger) » et « the total number of miles each autonomous vehicle tested in autonomous mode on public roads each month ». — [Cornell LII, 13 CCR §227.50](https://www.law.cornell.edu/regulations/california/13-CCR-227.50)
- Limites rapportées par la presse (2020), non vérifiées dans les rapports eux-mêmes :
  - Waymo jugeait que le métrique « does not provide relevant insights into the capabilities of the Waymo Driver ».
  - Le DMV précisait que les rapports « are not intended to compare one company with another or reach broad conclusions on technological capabilities ».
  - Les pratiques divergeaient : Nissan ne comptait pas les désengagements de début et de fin de trajet, Nvidia si ; des libellés comme « perception discrepancy » restaient vagues.

  — [VentureBeat, 26/02/2020](https://venturebeat.com/2020/02/26/california-dmv-releases-latest-batch-of-autonomous-vehicle-disengagement-reports/)
- Effet pervers d'incitation, selon TechCrunch (2020) : le métrique « incentivizes testing in less difficult circumstances ». Des acteurs ont aussi accusé des concurrents de manipuler le métrique « by easing the difficulty of miles driven over time to look like real progress ». — [TechCrunch, 04/08/2020](https://techcrunch.com/2020/08/04/autonomous-vehicle-reporting-data-is-driving-av-innovation-right-off-the-road/)
- Réforme en cours. Communiqué du DMV du 20/02/2026 : « The new regulations propose to replace disengagement reporting requirements » (13 CCR §227.56 selon le DMV) « with updated metrics offering a more precise picture of safety-relevant events ». Les nouveaux éléments à déclarer comprennent :
  - « Dynamic driving task performance relevant system failures that occur during drivered testing and deployment » ;
  - « Vehicle immobilizations that occur during driverless testing and deployment. » ;
  - « Vehicle Miles Traveled during testing and deployment. » ;
  - les avis de non-conformité dressés par les forces de l'ordre, des événements de freinage et les accidents (alignés sur la NHTSA).

  Le communiqué précise aussi : « Disengagement reporting is not required for AV operations conducted under deployment permits. » Le DMV « expects to finalize » ces règles en 2026. — [DMV Californie, 20/02/2026](https://www.dmv.ca.gov/portal/news-and-media/autonomous-vehicle-permit-holders-in-california-logged-more-than-9-million-test-miles-between-december-1-2024-and-november-30-2025)
- Dans l'autre sens, un AEB (freinage d'urgence automatique) qui freinerait tout le temps serait « sûr » vis-à-vis des collisions. La règle fédérale américaine prévoit donc des **essais de fausse activation**. Le NPRM de 2023 en proposait deux : une plaque d'acier de tranchée sur la voie, et un passage entre deux véhicules arrêtés. NHTSA y écrit que ces essais « establish only a baseline for system functionality » (formulation rapportée par un résumé de recherche ; le NPRM n'a pas été relu en entier). — [Federal Register, NPRM FMVSS 127, 13/06/2023](https://www.govinfo.gov/content/pkg/FR-2023-06-13/pdf/2023-11863.pdf). Le texte codifié du 49 CFR 571.127 contient une section « False activation » (S5.3). — [Cornell LII, 49 CFR 571.127](https://www.law.cornell.edu/cfr/text/49/571.127)

### Inferences
- J3016 ne propose aucun garde-fou contre le système qui ne fait rien, parce qu'il n'évalue rien : un niveau est une déclaration d'intention, pas une autonomie méritée. Pour B-tout, la bonne analogie n'est donc pas J3016. Ce sont plutôt les métriques normalisées par l'exposition (désengagements par mille autonome, VMT) et les essais de fausse activation.
- Pour le désengagement, le garde-fou contre l'inaction est implicite : sans kilomètre autonome, pas de taux. Mais il n'existe **aucun plancher d'exposition**. Un système qui roule peu, ou seulement en conditions faciles, sort gagnant. Transposé au protocole : le taux d'erreur de B-tout sur les actions déléguées doit toujours être accompagné du **volume et de la composition** de ces actions (par type et par niveau de risque). Sinon, une règle qui ne délègue que des lectures triviales ressemble à une règle utile.
- La réforme californienne de 2026 (VMT, immobilisations, défaillances pertinentes) déplace la mesure du « combien de fois l'humain reprend la main » vers « quels événements de sécurité par unité d'exposition, et quel coût du repli ». Les immobilisations sont l'équivalent d'un agent qui s'arrête pour demander. Pour B-tout, une validation humaine est le coût du repli : elle doit être **comptée**, et non traitée comme une sécurité gratuite.
- L'essai de fausse activation de l'AEB est le parallèle le plus net de notre défaut. Il existe pour qu'un système trop prudent ne passe pas l'homologation en freinant sans cesse. Le critère « confirmée » n'a pas d'équivalent : aucune condition ne pénalise une règle qui ne délègue jamais.

### Gaps
- Numérotation : le DMV parle de « 13CCR § 227.56 », LII héberge le texte sous §227.50 « Reporting Disengagement of Autonomous Mode ». Je n'ai pas vérifié s'il s'agit de deux articles distincts (essais avec ou sans conducteur) ou d'une renumérotation.
- Adoption finale des nouvelles règles du DMV non confirmée à ce jour (seulement « expects to finalize » en 2026).
- Texte final (2024) des essais de fausse activation FMVSS 127 non relu. Seuls le NPRM de 2023 et un sommaire du CFR ont été vus.
- Je n'ai pas trouvé d'étude académique de 2023-2026 qui chiffre le biais de sélection des trajets dans les rapports de désengagement. Les critiques citées sont journalistiques (2020).

## Q2 — Véhicules : « positive risk balance », safety case (UL 4600, ISO 21448, ISO/TS 5083, commission d'éthique allemande) et argument de puissance (RAND). Comment combine-t-on une revendication de sécurité et une revendication d'utilité ?

### Takeaway
Le cadre d'acceptation des véhicules autonomes est **comparatif** : faire au moins aussi bien que la référence humaine (positive risk balance, GAMAB). Il exige aussi de prouver cette comparaison sur une exposition réelle, ce que RAND montre statistiquement très coûteux. Le texte fondateur, la commission d'éthique allemande, pose explicitement l'utilité comme finalité : sécurité *et* mobilité. Il ajoute que le déploiement peut devenir « ethically mandated » s'il réduit les dommages. RAND et Kalra & Groves chiffrent le coût de ne pas déployer : l'erreur de type II est « a serious error ». Ne pas automatiser n'est donc pas considéré comme neutre. Les normes, en revanche, n'imposent pas de plancher d'utilité ou de disponibilité. Celle-ci passe par la définition de l'ODD, le repli vers la condition de risque minimal et, en Californie, la future déclaration des immobilisations.

### Cited Findings
**Commission d'éthique allemande (BMVI, juin 2017)**
- Règle 1 : « The primary purpose of partly and fully automated transport systems is to improve safety for all road users. Another purpose is to increase mobility opportunities and to make further benefits possible. » — [Ethics Commission, Automated and Connected Driving (2017)](https://www.bmvi.de/SharedDocs/EN/Documents/G/ethic-commission-report.pdf?__blob=publicationFile) (lu via [copie archivée](https://web.archive.org/web/2020/https://www.bmvi.de/SharedDocs/EN/Documents/G/ethic-commission-report.pdf?__blob=publicationFile))
- Règle 2 : « The protection of individuals takes precedence over all other utilitarian considerations. The objective is to reduce the level of harm until it is completely prevented. The licensing of automated systems is not justifiable unless it promises to produce at least a diminution in harm compared with human driving, in other words a positive balance of risks. » — [Ethics Commission 2017](https://www.bmvi.de/SharedDocs/EN/Documents/G/ethic-commission-report.pdf?__blob=publicationFile)
- Règle 3 : « technologically unavoidable residual risks do not militate against the introduction of automated driving if the balance of risks is fundamentally positive. » — [Ethics Commission 2017](https://www.bmvi.de/SharedDocs/EN/Documents/G/ethic-commission-report.pdf?__blob=publicationFile)
- Règle 6 : « The introduction of more highly automated driving systems, especially with the option of automated collision prevention, may be socially and ethically mandated if it can unlock existing potential for damage limitation. » — [Ethics Commission 2017](https://www.bmvi.de/SharedDocs/EN/Documents/G/ethic-commission-report.pdf?__blob=publicationFile)
- Règle 5 : parmi les moyens d'éviter les situations critiques, le texte cite « limiting the scope of application to controllable traffic environments ». Restreindre le domaine d'emploi est donc un levier de sécurité légitime. — [Ethics Commission 2017](https://www.bmvi.de/SharedDocs/EN/Documents/G/ethic-commission-report.pdf?__blob=publicationFile)

**Positive risk balance (PRB) dans l'industrie et les normes**
- Livre blanc « Safety First for Automated Driving » (2019, 11 industriels), présentation de synthèse : « Based on recommendation of the German Ethics Commission in 06/2017 (BMVI): Maximizing the evidence of a positive risk balance of automated driving solutions compared to THE AVERAGE HUMAN DRIVING PERFORMANCE. » — [vbw, présentation SaFAD 04/12/2019](https://www.vbw-bayern.de/Redaktion/Frei-zugaengliche-Medien/Abteilungen-GS/Wirtschaftspolitik/2019/Downloads/20191204-Safety-for-Automated-Driving.pdf)
- ISO/TS 5083:2025 (1re éd., avril 2025). Son sommaire comprend :
  - §6.1 « Defining the ADS feature », avec « 6.1.3 Example solution: ADS feature description with capabilities » ;
  - §6.2 « Defining the risk acceptance criteria », avec « 6.2.3 Example solution: Absence of unreasonable risk and risk acceptance criteria » et « 6.2.6 Example solution: Quantitative risk balance ».

  La balance de risque y figure donc comme **exemple de solution**, pas comme exigence. — [ISO/TS 5083:2025, extrait iTeh (sommaire)](https://cdn.standards.iteh.ai/samples/81920/972e362f5d59439389bf949f5b8a96ce/ISO-TS-5083-2025.pdf)
- ISO 21448 (SOTIF), lu via Putze et al. (DLR, 2023) :
  - la norme « permits qualitative and quantitative acceptance criteria, but at the same time heavily promotes quantitative acceptance criteria (GAMAB, PRB, ALARP, MEM) as examples thereof » ;
  - « Once quantitative acceptance criteria for residual risk have been defined, it is possible to derive validation targets from them. » ;
  - la SOTIF est atteinte si « the residual risk of the system causing a hazardous event is shown as being lower than the acceptance criteria [...] and there is no known scenario that could lead to an unreasonable risk for specific road users » (citation d'ISO 21448, p. 37). Le critère combine donc un seuil agrégé et l'absence de risque déraisonnable pour un sous-groupe.

  — [Putze et al. 2023, arXiv 2304.10170](https://arxiv.org/abs/2304.10170)
- Favaro (2021) : « two possible interpretations exist for PRB, and that failure to distinguish them can lead to misunderstanding different parties' positions ». — [Favaro 2021, arXiv 2110.10566](https://arxiv.org/abs/2110.10566)
- Koopman & Widen (2024) :
  - définition : « Positive Risk Balance (PRB): the proposition that a computer driver should be no less safe (and ideally safer than) a human driver. » ;
  - verdict : « Positive Risk Balance is a necessary but insufficient condition for safety outcomes that are likely to be broadly acceptable to a wide range of stakeholders. » ;
  - exemple contre l'agrégat : « Total fatalities are reduced by 50%, but every single person harmed is a child boarding or debarking a school bus » ;
  - puissance : avec environ « one fatality per 74 million miles », il faudrait peut-être « two more orders of magnitude mileage accumulation to get a meaningful understanding of fatality outcomes ».

  — [Koopman & Widen, « Breaking the Tyranny of Net Risk Metrics for Automated Vehicle Safety », Safety-Critical Systems eJournal, 2024](https://users.ece.cmu.edu/~koopman/pubs/Koopman2024_TyrannyNetRiskMetrics.pdf)
- Koopman & Wagner (2020) jugent qu'au moment du déploiement l'incertitude sur le risque restera forte. Ils proposent une « positive trust balance » qui combine tests, rigueur d'ingénierie, retour d'exploitation et culture de sécurité (d'après le résumé ; texte complet non relu). — [arXiv 2009.05801](https://arxiv.org/abs/2009.05801)
- UL 4600 (3e éd., mars 2023 selon [ULSE](https://ulse.org/ul-standards-engagement/presenting-standard-safety-evaluation-autonomous-vehicles-and-other-2)) impose des indicateurs de performance de sécurité (SPI). Définition citée par l'article ci-dessous : « An SPI is a metric supported by evidence that uses a threshold comparison to condition a claim in a safety case. » La note 16.2.2.6.2 « explicitly states that relying solely on lagging indicators is not acceptable ». La clause 16.1.1 « mandates the incorporation of SPIs in the safety case ». — [Towards an Argument Pattern for the Use of SPIs, arXiv 2410.00578](https://arxiv.org/abs/2410.00578)

**RAND : l'argument de puissance et le coût d'attendre**
- Kalra & Paddock (2016), constats clés :
  - « Autonomous vehicles would have to be driven hundreds of millions of miles and sometimes hundreds of billions of miles to demonstrate their reliability in terms of fatalities and injuries. » ;
  - « at least for fatalities and injuries, test-driving alone cannot provide sufficient evidence for demonstrating autonomous vehicle safety » ;
  - il est « imperative to develop adaptive regulations ».

  — [RAND RR-1478, Driving to Safety](https://www.rand.org/pubs/research_reports/RR1478.html) ([PDF](https://www.rand.org/content/dam/rand/pubs/research_reports/RR1400/RR1478/RAND_RR1478.pdf))
- Chiffres du tableau final (flotte de 100 véhicules, 24 h/24, 25 mph), pour le taux de mortalité humain de 1,09 pour 100 millions de miles :
  - 275 millions de miles **sans aucun échec** pour démontrer, à 95 % de confiance, un taux au plus égal à ce niveau (12,5 ans) ;
  - 8,8 milliards de miles pour l'estimer à ±20 % (400 ans) ;
  - 11 milliards de miles pour démontrer, à 95 % de confiance et 80 % de puissance, un taux **20 % meilleur** (500 ans).

  — [RAND RR-1478 PDF](https://www.rand.org/content/dam/rand/pubs/research_reports/RR1400/RR1478/RAND_RR1478.pdf)
- Le type II est traité comme une vraie erreur : conclure à tort que les véhicules autonomes ne font pas mieux « would be a serious error as it could delay the introduction of potentially beneficial technology and needlessly perpetuate the risks posed by human drivers ». Pour une amélioration de 5 %, le kilométrage nécessaire est « almost ludicrous: 215 billion miles ». RAND évoque un test de **non-infériorité** si le consensus admettait une performance « no more than some (small) amount worse than human-driven cars ». — [RAND RR-1478 PDF](https://www.rand.org/content/dam/rand/pubs/research_reports/RR1400/RR1478/RAND_RR1478.pdf)
- Kalra & Groves (2017) :
  - « waiting for HAVs that are many times safer than human drivers misses opportunities to save lives. It is the very definition of allowing perfect to be the enemy of good. » ;
  - à 15 ans, « more lives are cumulatively saved under the less stringent Improve10 policy than the more stringent Improve75 or Improve90 policies in nearly all conditions, and those savings can be significant—tens of thousands to hundreds of thousands of lives » ;
  - à 30 ans, sous toutes les conditions explorées, parfois « more than half a million lives ».

  — [RAND RR-2150, The Enemy of Good](https://www.rand.org/pubs/research_reports/RR2150.html) ([PDF](https://www.rand.org/content/dam/rand/pubs/research_reports/RR2100/RR2150/RAND_RR2150.pdf))

### Inferences
- **Sécurité et utilité, dans ce domaine** :
  - la revendication de sécurité est comparative : PRB ou GAMAB, faire mieux que la référence humaine sur la même exposition ;
  - l'utilité est posée comme finalité (règle 1) et parfois comme obligation (règle 6, Kalra & Groves) ;
  - mais aucune norme ne fixe de seuil d'utilité. Le pendant opérationnel est l'ODD : on délimite où le système agit seul, puis on prouve la sécurité dans ce périmètre.

  Pour B-tout, l'analogue est direct : l'ensemble des types d'actions délégués joue le rôle d'un ODD appris. La revendication doit porter sur la sécurité dans ce périmètre *et* sur sa taille, comme une couverture.
- **Puissance.** Le chiffre de 275 millions de miles correspond à la « règle de trois » : avec zéro échec, la borne supérieure à 95 % vaut environ 3/n (3 / 1,09×10⁻⁸ ≈ 275 M ; c'est mon calcul). Transposé : avec un budget d'erreur b, il faut au moins 3/b actions déléguées sans erreur pour **démontrer** b. Or le critère actuel (« pas de dépassement établi ») fonctionne à l'envers. Moins une règle délègue, moins on a de données, et moins on peut établir un dépassement. Le critère de sécurité lui-même favorise donc la délégation minimale. Koopman et RAND insistent sur ce piège : l'absence d'échec observé sur une petite exposition ne prouve rien.
- **Le coût de l'inaction est reconnu dans ce domaine.** RAND (type II), Kalra & Groves (vies perdues à attendre) et la règle 6 vont tous dans ce sens. C'est une base normative pour exiger que B-tout délègue effectivement. Un « succès » sans délégation reviendrait à la politique « attendre la perfection ».
- **Agrégat et sous-groupes.** Le double critère SOTIF (risque résiduel agrégé sous le seuil *et* aucun scénario à risque déraisonnable pour un usager particulier) et la critique de Koopman (transfert de risque) suggèrent un contrôle par type d'action : pas de type délégué au taux d'erreur déraisonnable, même si l'agrégat respecte le budget. Le max-T par type du protocole va déjà dans ce sens.

### Gaps
- Texte exact de la définition de PRB dans ISO/TS 5083:2025 non accessible (payant ; seul le sommaire a été vu).
- Texte d'UL 4600 non consulté directement. Les clauses SPI sont citées via arXiv 2410.00578. Je n'ai trouvé aucune exigence d'UL 4600 sur la disponibilité ou l'utilité.
- ISO 21448 lu seulement via Putze et al. (citation de la p. 37 de la norme). Les annexes sur les cibles de validation n'ont pas été vues.
- Les deux interprétations de PRB chez Favaro (2021) ne sont pas détaillées dans le résumé. Le PDF complet n'a pas été lu.

## Q3 — Agents IA : cadres de niveaux d'autonomie (Feng et al. 2025, Morris et al. 2023-2024, Anthropic 2026). L'autonomie est-elle déclarée ou mesurée ?

### Takeaway
Comme J3016, les cadres de niveaux pour agents (Feng et al., Morris et al.) traitent l'autonomie comme un **choix de conception séparé de la capacité**. Morris et al. ajoutent que le bon niveau « need not be the maximum achievable ». Feng et al. vont plus loin et proposent une évaluation qui mesure l'autonomie : l'**assisted evaluation**. Elle cherche le *niveau minimal d'implication humaine* qui permet à l'agent de dépasser un seuil de réussite. C'est la formulation la plus proche d'une autonomie méritée. Anthropic (2026) mesure l'autonomie en production (auto-approbation, interruptions, durée des tours). Elle constate un « deployment overhang » : on délègue moins que ce que le modèle sait faire.

### Cited Findings
**Feng, McDonald, Zhang (2025)**
- « We use autonomy to refer to the extent to which an AI agent is designed to operate without user involvement. » et « our framework views autonomy as a property that can also be designed independently of capability. » — [Feng et al., Levels of Autonomy for AI Agents, arXiv 2506.12469](https://arxiv.org/abs/2506.12469)
- Les cinq niveaux, définis par le rôle de l'utilisateur :
  - L1, opérateur : « the user is in charge at all times » ;
  - L2, collaborateur ;
  - L3, consultant : « The agent takes initiative in task planning and execution over extended time horizons » ;
  - L4, approbateur : « the user is only required to interact with the agent when the agent encounters a blocker » ;
  - L5, observateur.

  — [arXiv 2506.12469](https://arxiv.org/abs/2506.12469)
- Certificats d'autonomie : « a digital document that prescribes the maximum level of autonomy » qu'un agent peut exercer, « issued by a third-party governing body ». — [arXiv 2506.12469](https://arxiv.org/abs/2506.12469)
- Assisted evaluation (§5) :
  - principe : « autonomy evaluations should measure the extent of user involvement requested by an agent to successfully complete a task » ;
  - but : « assisted evaluations are designed to surface the minimum level of user involvement needed for the agent to exceed a certain accuracy or pass rate threshold, and then assign an autonomy level based on that information » ;
  - procédure : partir sans implication (« The agent is considered L5 if it achieves at least T on all main tasks »), puis « Iteratively increase user involvement in subsequent rounds until the agent achieves T », en commençant par des interactions de type L4 : « providing approvals and rejections » ;
  - coût : désigner un agent L1 demande cinq tours.

  — [arXiv 2506.12469](https://arxiv.org/abs/2506.12469)
- Risques d'une autonomie trop faible ou mal supervisée :
  - L4 : « User disengagement can lower the care with which they approve actions » ;
  - question ouverte : « How can users be engaged in agent activities to avoid meaningless rubber stamping? » ;
  - systèmes multi-agents : « a system comprised of entirely L1 agents is not ideal ».

  — [arXiv 2506.12469](https://arxiv.org/abs/2506.12469)

**Morris et al. (Google DeepMind, « Levels of AGI », ICML 2024)**
- Le niveau 0 « No AI » correspond à « human does everything ». Le niveau 5 est « AI as an Agent ». — [arXiv 2311.02462](https://arxiv.org/abs/2311.02462)
- « Higher levels of autonomy are “unlocked” by AGI capability progression. » ; « Increasing capabilities unlock new interaction paradigms, but do not determine them. » ; « The choice of appropriate autonomy level need not be the maximum achievable given the capabilities of the underlying model. » ; « We may develop an AGI, but choose not to deploy it autonomously ». — [arXiv 2311.02462](https://arxiv.org/abs/2311.02462)

**Anthropic, « Measuring AI agent autonomy in practice » (18/02/2026)**
- Définitions :
  - « Autonomy is not a fixed property of a model or system but an emergent characteristic of a deployment » ;
  - « An agent with minimal autonomy executes exactly what a human explicitly requests » ;
  - autonomie limitée par l'agent : « Claude chooses to seek guidance from the human when it could have continued operating independently ».

  — [Anthropic 2026](https://www.anthropic.com/research/measuring-agent-autonomy)
- Mesures (Claude Code) :
  - « Among new users, roughly 20% of sessions use full auto-approve, which increases to over 40% as users gain experience » (vers 750 sessions) ;
  - les nouveaux utilisateurs interrompent Claude « in 5% of turns, while more experienced users interrupt in around 9% of turns » ;
  - « the 99.9th percentile turn duration nearly doubled, from under 25 minutes to over 45 minutes » ;
  - usage interne : « the average number of human interventions per session decreased from 5.4 to 3.3 » ;
  - « On the most complex tasks, Claude Code stops to ask for clarification more than twice as often as humans interrupt it. »

  — [Anthropic 2026](https://www.anthropic.com/research/measuring-agent-autonomy)
- Mesures (API publique) :
  - « 87% of tool calls on minimal-complexity tasks (like editing a line of code) have some form of human involvement », contre « only 67% of tool calls for high-complexity tasks » ;
  - « 73% appear to have a human in the loop in some way » ;
  - « only 0.8% of actions appear to be irreversible » ;
  - réserve des auteurs : ce sont « an upper bound on human involvement ».

  — [Anthropic 2026](https://www.anthropic.com/research/measuring-agent-autonomy)
- Conclusions :
  - « a significant deployment overhang, where the autonomy models are capable of handling exceeds what they exercise in practice » ;
  - « effective oversight doesn't require approving every action but being in a position to intervene when it matters » ;
  - « Effective oversight of agents requires more than putting a human in the approval chain. » ;
  - réserve sur leur propre indicateur : « Turn duration is an imperfect proxy for autonomy » ; et Claude « may ask unnecessary questions ».

  — [Anthropic 2026](https://www.anthropic.com/research/measuring-agent-autonomy)

### Inferences
- Deux traditions coexistent :
  - **l'autonomie déclarée** : J3016, Morris, le certificat de Feng ;
  - **l'autonomie mesurée** : l'assisted evaluation de Feng, la télémétrie d'Anthropic.

  B-tout relève de la seconde : l'autonomie y est conférée par un historique de succès. L'assisted evaluation de Feng en est le cousin le plus proche. Elle fixe un seuil de réussite T puis cherche l'implication **minimale** qui l'atteint. Transposé, le critère de succès devient : atteindre le budget d'erreur avec **moins** d'implication humaine que les références. C'est exactement ce que le critère actuel n'impose pas quand une référence dépasse son budget.
- Feng (rubber stamping), Anthropic (« more than putting a human in the approval chain ») et l'idée d'overhang convergent : la référence « tout valider » n'est pas l'état idéal. C'est un état coûteux, et pas parfaitement sûr si les approbations deviennent mécaniques (voir Q4).
- La télémétrie d'Anthropic montre que la confiance se construit avec l'expérience : l'auto-approbation monte de 20 % à plus de 40 % des sessions. Cela ressemble à une autonomie méritée *informelle*, côté utilisateur. Mais ces données ne disent rien du taux d'erreur à ce niveau de délégation. Ce n'est pas une évaluation « utile ET sûre ».

### Gaps
- Version « Knight Institute » du travail de Feng et al. non vérifiée. J'ai consulté la version arXiv v2, juillet 2025.
- Autres cadres non consultés : Cihon et al. (2025, mesure de l'autonomie par inspection du code, cité comme [7] par Feng), Kasirzadeh & Gabriel (2025), Mitchell et al. (2025).
- Feng et al. ne donnent aucun seuil numérique (nombre d'approbations, taux d'aide) pour attribuer un niveau.

## Q4 — Agents IA : systèmes de permission et supervision humaine. Comment mesure-t-on les demandes d'approbation face à l'accomplissement des tâches ? Quels benchmarks pénalisent l'inaction ?

### Takeaway
Les développeurs mesurent maintenant les deux côtés :
- **la charge**, en demandes évitées ou en fausses alertes ;
- **la sécurité**, en actions dangereuses laissées passer.

Anthropic fait cette évaluation à deux faces pour l'auto mode de Claude Code (FPR 0,4 %, FNR 17 %). Elle chiffre aussi l'allègement apporté par le bac à sable : −84 % de demandes, « safely ». OpenAI ne publie que le côté rappel (taux de confirmation 92 % puis 94 %), sans taux de sur-confirmation. Côté benchmarks, l'inaction est explicitement neutralisée : ToolEmu publie un agent « NoAct » (sécurité parfaite, utilité quasi nulle) ; AgentDojo publie l'utilité avec et sans attaque ; ST-WebAgentBench ne crédite qu'une tâche accomplie *et* conforme (CuP), et pénalise ainsi « over-cautiousness as well as recklessness ». Plusieurs sources signalent la fatigue d'approbation : la référence « tout valider » n'est pas sûre en pratique.

### Cited Findings
**Anthropic (Claude Code)**
- Bac à sable : « In our internal usage, we've found that sandboxing safely reduces permission prompts by 84%. » (20/10/2025 ; donnée interne, non indépendante). — [Anthropic Engineering, Claude Code sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
- Auto mode (25/03/2026) :
  - constat : les utilisateurs acceptent les demandes de permission, « in practice users accept 93% of them anyway. Over time that leads to approval fatigue, where people stop paying close attention to what they're approving. » ;
  - définitions : « False-negative rate (FNR) is the fraction of dangerous actions the classifier lets through » ; « false positive rate (FPR) is the fraction of benign actions it blocks. » ;
  - jeux d'évaluation : trafic réel interne (n = 10 000), actions « overeager » réelles (n = 52, refusées par un employé ou signalées après coup), exfiltration synthétique (n = 1 000) ;
  - résultats, pipeline complet : 0,4 % de FPR sur le trafic réel, 17 % de FNR sur les actions overeager réelles, 5,7 % sur l'exfiltration synthétique. Étape 1 seule : 8,5 % de FPR, 6,6 % de FNR.

  — [Anthropic Engineering, Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)
- Positionnement :
  - par rapport au contournement : « Bypassing permissions is zero-maintenance but offers no protection. » ; si l'on utilise `--dangerously-skip-permissions`, « this is a substantial improvement » ;
  - par rapport à la validation manuelle : « If you are manually approving every action carefully, it's arguably a regression » ;
  - « Whether 17% is acceptable depends on what you're comparing against. » ;
  - repli : « If a session accumulates 3 consecutive denials or 20 total, we stop the model and escalate to the human. »

  — [Anthropic Engineering, auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)
- Billet produit (24/03/2026, mis à jour 10/07/2026) : « Auto mode is a middle path that lets you run longer tasks with fewer interruptions ». Il « reduces risk compared to --dangerously-skip-permissions but doesn't eliminate it entirely ». — [Claude blog, Auto mode](https://claude.com/blog/auto-mode)

**OpenAI**
- Addendum Operator o3 (mai 2025) :
  - objectif : « We aim to have the model ask the user for confirmations before finalizing actions that affect the state of the world (e.g. before submitting a purchase or sending an email) » ;
  - mesure : « obtained an improved confirmation rate of 94%, compared to 92% with the previous model. Of note, Operator now confirms in 100% of the financial transactions in our eval set. »

  Aucun taux de sur-confirmation n'est publié dans cet addendum. — [OpenAI, Operator o3 system card addendum](https://cdn.openai.com/pdf/4375e605-f9a6-438d-bcc8-190599c183a6/o3_cua_system_card.pdf)
- Shavit et al. (OpenAI, déc. 2023) :
  - l'approbation humaine est « a standard way to limit egregious failures », mais devient plus difficile « when the user must approve many decisions and thus must make each approval quickly, reducing their ability to meaningfully consider each one » ;
  - « the risk-mitigation benefits of these measures must be carefully balanced with the reduction in agentic AI systems’ capabilities and utility » ;
  - questions ouvertes : « How should a user or system deployer determine and enforce which interactions need human approval, as a function of a model’s empirical reliability on that task and other factors? », et comment éviter que l'approbation ne tourne au « “rubber stamp” ».

  — [Shavit et al., Practices for Governing Agentic AI Systems](https://cdn.openai.com/papers/practices-for-governing-agentic-ai-systems.pdf)

**Agents avec humain dans la boucle (recherche)**
- Magentic-UI (Microsoft, 2025) : « With a simulated user possessing side information, Magentic-UI's task completion rate increases by 71% (from 30.3% to 51.9%), with minimal user intervention (help requested in only 10% of tasks) » (GAIA, 162 tâches ; utilisateurs simulés par un LLM). — [Mozannar et al., arXiv 2507.22358](https://arxiv.org/abs/2507.22358). Le système « seeks user approval before executing potentially irreversible actions, and the user can specify how often Magentic-UI needs approvals ». — [Microsoft Research blog](https://www.microsoft.com/en-us/research/blog/magentic-ui-an-experimental-human-centered-web-agent)
- Collaborative Gym (Shao et al., ICLR 2026) mesure le processus. Le « controlled autonomy » compte « the agent's confirmation questions that effectively elicit a human response » et « instances where the human verbally intervenes to halt the agent's actions » ([README co-gym](https://pypi.org/project/co-gym/)). Résultat : agents collaboratifs à « win rates of 86% in Travel Planning and 74% in Tabular Analysis compared to fully autonomous agents when evaluated by real users ». — [arXiv 2412.15701](https://arxiv.org/abs/2412.15701)

**Benchmarks qui neutralisent l'inaction**
- ToolEmu (ICLR 2024) :
  - référence : « ‘NoAct’ denotes an agent that refrains from taking any actions, which could achieve a perfect safety score but a nearly 0 helpfulness score » (tableau 5 : sécurité 3,000/3, échecs 0,00 %, utilité 0,063/3) ;
  - un évaluateur d'utilité dédié sert « to capture the potential tradeoff between safety and helpfulness » ;
  - définition de l'utilité : « deleting all files without confirmation to “clean disk space” is not “helpful” » ;
  - effet du prompt : demander de « seek user confirmation before executing risky actions » améliore la sécurité *et* l'utilité ; ajouter « operate autonomously and seek user assistance only when necessary » dégrade les deux.

  — [Ruan et al., ToolEmu, arXiv 2309.15817](https://arxiv.org/abs/2309.15817)
- AgentDojo (NeurIPS 2024 D&B) publie trois métriques :
  - « Benign Utility: the fraction of user tasks that the model solves in the absence of any attacks » ;
  - « Utility Under Attack » ;
  - « Targeted Attack Success Rate ».

  Les défenses sont comparées sur une frontière de Pareto utilité/robustesse. Le détecteur d'injection « has too many false positives, however, and significantly degrades utility ». — [Debenedetti et al., arXiv 2406.13352](https://arxiv.org/abs/2406.13352)
- ST-WebAgentBench (IBM, ICLR 2026) :
  - définition : « Completion-under-Policy (CuP), which awards credit only when both the task is fully completed and every policy constraint is satisfied » ;
  - effet : « CuP penalizes over-cautiousness as well as recklessness » ;
  - politique de consentement : « The agent must solicit confirmation before irreversible operations » ;
  - résultats : taux d'accomplissement brut moyen de 24,3 %, mais CuP de 15,0 %.

  — [Levy et al., arXiv 2410.06703](https://arxiv.org/abs/2410.06703)
- Hors agents, XSTest mesure la « sécurité exagérée » : 250 invites sûres qui ressemblent à des invites dangereuses. Llama2 refusait à tort 38 % de ces invites (d'après le résumé ; chiffres non relus dans le PDF). — [Röttger et al., XSTest, arXiv 2308.01263](https://arxiv.org/abs/2308.01263)

**Encadrement réglementaire de la supervision**
- AI Act, art. 14(4)(b) : la personne chargée de la supervision doit pouvoir « remain aware of the possible tendency of automatically relying or over-relying on the output produced by a high-risk AI system (automation bias) ». Art. 14(4)(e) : elle doit pouvoir arrêter le système « through a ‘stop’ button or a similar procedure that allows the system to come to a halt in a safe state ». — [AI Act, article 14](https://artificialintelligenceact.eu/article/14/)

### Inferences
- **Le schéma d'évaluation est à deux faces partout où l'on veut éviter la solution triviale.** Côté charge : FPR, demandes évitées, utilité, couverture. Côté sécurité : FNR, taux d'attaque réussie, violations. Seul le rappel de confirmation d'OpenAI est à une face, et il récompenserait un agent qui confirme tout. Le critère « confirmée » actuel est aussi à une face, dès qu'une référence dépasse son budget.
- **Le « NoAct » de ToolEmu est l'outil le plus simple à reprendre.** On fait tourner la règle « ne délègue rien », c'est-à-dire H, la validation intégrale, comme référence explicite, et l'on exige que B-tout s'en distingue sur la charge. Pour l'instant, H est la ligne de base dont on mesure l'économie, mais aucune condition n'exige de la battre. Une condition « battre NoAct en utilité à sécurité égale » ferait échouer par construction une règle qui ne délègue rien.
- **CuP et ROHE (voir Q5) montrent deux façons de fusionner sécurité et utilité en un score.** Mais un score composite cache l'arbitrage. Les essais cliniques (Q6-Q7) gardent deux critères hiérarchisés : la sécurité comme porte, puis l'utilité. C'est probablement plus lisible pour un label confirmatoire.
- **La référence « tout valider » n'est pas une sécurité parfaite.** Anthropic constate 93 % d'acceptation et une « approval fatigue ». OpenAI parle de « rubber stamp », l'AI Act de « automation bias ». Un rejeu hors ligne qui traite la validation humaine comme un oracle favorise donc H et les règles qui délèguent peu. Comparer B-tout à H « à sécurité égale » sous cette hypothèse est *conservateur* pour B-tout. Une analyse de sensibilité avec un validateur imparfait serait informative, mais n'a pas sa place dans le critère confirmatoire.

### Gaps
- Pas de taux de sur-confirmation (demandes inutiles) publié par OpenAI pour Operator ou ChatGPT agent. La system card originale d'Operator (janv. 2025) et celle de ChatGPT agent (juil. 2025) n'ont pas pu être lues (HTTP 403).
- Agents de navigateur (Claude for Chrome, Gemini, Comet…) : pas de métrique publiée « demandes d'approbation contre accomplissement » trouvée.
- Des sources secondaires ([The Register](https://www.theregister.com/a/5285326), hyrax.dev) attribuent à Anthropic un chiffre de 97 % d'acceptation et un taux de détection des commandes dangereuses de 89 % (classifieur) contre 14 % (validation manuelle). Je n'en ai trouvé **aucune source primaire**. Le billet Claude de juillet 2026 ne contient pas ces chiffres. Ils ne sont pas utilisés ici.
- Les 84 % de demandes en moins (bac à sable) sont une mesure interne, sans protocole publié.

## Q5 — Autonomie graduée et calibration de la confiance : facteurs humains, robotique interactive, agents

### Takeaway
La littérature sur l'automatisation choisit le niveau d'automatisation **par type de fonction**. Ses critères sont la performance humaine, la fiabilité de l'automate et le coût des conséquences (Parasuraman et al. 2000). C'est la logique « par type d'action » de B-tout. Elle nomme aussi l'échec par excès de prudence : le « disuse », c'est-à-dire la sous-utilisation de l'automatisation (Parasuraman & Riley 1997). Les travaux de robotique interactive mesurent l'efficacité de l'autonomie graduée par des métriques qui **rapportent la performance à l'effort humain** (ROHE de Fleet-DAgger, pourcentage d'autonomie de Bojarski). Ils comparent les méthodes **à niveau de réussite garanti égal, par le taux d'aide** (KnowNo). Une méthode trop prudente y est explicitement pénalisée.

### Cited Findings
- Parasuraman, Sheridan & Wickens (2000) proposent quatre types de fonctions : acquisition d'information, analyse, décision, exécution. Chacune peut être automatisée sur un continuum de niveaux. Le critère d'évaluation primaire est l'effet sur la performance humaine ; les critères secondaires sont notamment la fiabilité de l'automate et le coût des conséquences des décisions et actions (d'après le résumé ; texte intégral non relu). — [IEEE Trans. SMC-A 30(3), 2000](https://ieeexplore.ieee.org/document/844354)
- Parasuraman & Riley (1997) définissent le « disuse » comme « the neglect or underutilization of automation ». Selon le résumé, il est souvent causé par des alarmes qui se déclenchent à tort. — [Human Factors 39(2), 1997](https://journals.sagepub.com/doi/10.1518/001872097778543886)
- Fleet-DAgger (CoRL 2022) définit le « return on human effort » : « the expected ratio of the cumulative reward across all timesteps and all robots to the total amount of human time spent helping robots ». La formule ajoute 1 au dénominateur « for the degenerate case of zero human time ». « Intuitively, the ROHE measures the performance of the robot fleet normalized by the total human effort required to achieve this performance. » La méthode atteint « up to 8.8× higher ROHE than baselines ». — [Hoque et al., arXiv 2206.14349](https://arxiv.org/abs/2206.14349)
- KnowNo (CoRL 2023) :
  - garantie : la prédiction conforme fournit des « statistical guarantees on task completion while minimizing human help » ; le planificateur réussit « with a user-specified probability 1−ϵ » ;
  - comparaison au même niveau de réussite : KnowNo « reduces the human help rate by 14% step-wise and 8% trial-wise » ;
  - méthode trop prudente : avec ϵ = 0,25, la méthode de référence est « grossly over-conservative and requires a step-wise help rate of 87% ».

  — [Ren et al., arXiv 2307.01928](https://arxiv.org/abs/2307.01928)
- NVIDIA (2016), métrique d'autonomie : « autonomy = (1 − (number of interventions) · 6 seconds / elapsed time [seconds]) · 100 ». Chaque intervention est comptée comme 6 s de perte. Sur route, la voiture était « autonomous approximately 98% of the time ». — [Bojarski et al., arXiv 1604.07316](https://arxiv.org/abs/1604.07316)
- Collaboration humain-IA en production : la part de sessions en auto-approbation complète passe d'environ 20 % (nouveaux utilisateurs) à plus de 40 % (environ 750 sessions). Anthropic y voit une confiance qui se construit progressivement (voir Q3). — [Anthropic 2026](https://www.anthropic.com/research/measuring-agent-autonomy)
- Analogie hors IA, la formation médicale par activités confiables (EPA) : l'autonomie est accordée activité par activité, sur des échelles ordinales « entrustment-supervision ». Les décisions sommatives « reflect a generalised and continuing permission to act at the expected supervision level » (attribution d'après un résumé de recherche ; chapitre non relu en entier). — [Burch et al., chapitre Ubiquity Press, 2024](https://ubiquitypress.com/site/chapters/10.5334/bdc.s)

### Inferences
- B-tout applique au niveau d'un agent l'idée « types et niveaux » de Parasuraman (2000), la fiabilité étant estimée par un historique de succès. Le coût des conséquences n'est pas explicite dans B-tout. Il l'est dans les deux références (liste par catégorie de risque, tri par risque). Une comparaison équitable doit donc tenir compte du fait que les références intègrent une information que B-tout n'a pas.
- Le « disuse » donne un nom à l'échec que le critère « confirmée » ne voit pas : une règle sûre parce qu'inutilisée. Les facteurs humains le traitent comme une défaillance, au même titre que la sur-confiance.
- Les métriques de robotique interactive offrent des formes prêtes à l'emploi pour un indicateur secondaire :
  - ROHE : succès par unité d'effort humain, avec un +1 contre la division par zéro ;
  - taux d'aide à réussite garantie (KnowNo) ;
  - pourcentage d'autonomie avec coût d'intervention (Bojarski).

  Le schéma de KnowNo est le plus proche d'un critère confirmatoire : fixer la garantie de sécurité, puis classer les règles par **taux d'aide humaine**. Une règle « sur-conservatrice » est alors visiblement mauvaise (87 % d'aide).

### Gaps
- Je n'ai pas trouvé d'étude 2024-2026 qui évalue une règle « autonomie après N succès consécutifs » pour agents LLM avec mesure conjointe de la charge et des erreurs. L'analogue le plus proche reste la télémétrie d'Anthropic, qui ne mesure pas les erreurs à niveau de délégation donné.
- EPA : pas de source sur le nombre d'observations réussies exigé avant de confier une activité.
- Les études de calibration de la confiance avec des agents LLM (expériences utilisateur 2024-2026) n'ont pas été couvertes au-delà de Magentic-UI, Co-Gym et Anthropic.

## Q6 — Décision humain-IA : exigence de complémentarité, et obligation de battre « l'humain fait tout » sur la charge à précision égale

### Takeaway
La complémentarité (Bansal et al.) exige que l'équipe humain-IA fasse **mieux que chacun seul en précision**. La méta-analyse de Vaccaro et al. montre qu'en moyenne ce n'est pas le cas pour les tâches de décision (g = −0,23). Une seconde exigence est plus pertinente pour la délégation : **réduire la charge humaine sans perdre en précision ou en sécurité** par rapport à « l'humain fait tout ». Elle est formalisée par Raghu et al. (l'automatisation est une méta-décision de triage). Elle est appliquée dans des essais cliniques d'IA autonome ou de triage : MASAI (plancher de sécurité, non-infériorité, −44,3 % de lectures), Plesner (28 % des radios normales rapportées seules, sensibilité ≥ 99 %), IDx-DR (critères préspécifiés sur la sensibilité et la spécificité, plus l'« imageabilité », c'est-à-dire la part de patients où l'IA rend un résultat).

### Cited Findings
- Complémentarité : performance d'équipe « higher than either the human or the AI working solo ». Les explications « increased the chance that humans will accept the AI's recommendation, regardless of its correctness ». Étude menée avec une IA « with accuracy comparable to humans ». — [Bansal et al., CHI 2021, arXiv 2006.14779](https://arxiv.org/abs/2006.14779)
- Méta-analyse préenregistrée (106 études, 370 effets, 2020-2023) :
  - « on average, human-AI combinations performed significantly worse than the best of humans or AI alone (Hedges' g = −0.23; 95% confidence interval, −0.39 to −0.07) » ;
  - « performance losses in tasks that involved making decisions » ;
  - « when humans outperformed AI alone, we found performance gains in the combination, but when AI outperformed humans alone, we found losses ».

  Un effet positif (g = 0,64) par rapport à l'humain seul est rapporté par des résumés secondaires, mais je ne l'ai pas vérifié dans le texte. — [Vaccaro, Almaatouq & Malone, Nature Human Behaviour 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11659167/)
- Raghu et al. (2019) :
  - « automation is more than just the replacement of human effort on a task; it is also the meta-decision of which instances of the task to automate » ;
  - résultat : même quand l'algorithme bat les humains en moyenne, « the optimal solution is to automate only a fraction of the instances and to optimally divide up the available human effort on the remaining ones » ;
  - chiffres (exemple médical) : l'automatisation complète fait passer l'erreur « from roughly 5.5% by human doctors to 4% », et le triage optimal « to roughly 3.5% ».

  — [Raghu et al., The Algorithmic Automation Problem, arXiv 1903.12220](https://arxiv.org/abs/1903.12220)
- MASAI (Lancet Oncology 2023) :
  - titre : « a clinical safety analysis of a randomised, controlled, non-inferiority, single-blinded, screening accuracy study » ;
  - plancher de sécurité : « The lowest acceptable limit for safety in the intervention group was a cancer detection rate of more than 3 per 1000 participants screened » ;
  - résultats : détection de 6,1 contre 5,1 pour 1 000 (ratio 1,2 ; IC 95 % 1,0-1,5), faux positifs 1,5 % dans les deux bras, 46 345 lectures contre 83 231 ; « The screen-reading workload was reduced by 44·3% using AI. » ;
  - conclusion : « similar cancer detection rate compared with standard double reading, with a substantially lower screen-reading workload, indicating that the use of AI in mammography screening is safe ».

  La charge de lecture était un critère **secondaire** préspécifié, sans seuil chiffré dans le résumé. Le critère primaire est le taux de cancers d'intervalle, en cours de suivi. — [Lång et al., Lancet Oncol 2023, PubMed 37541274](https://pubmed.ncbi.nlm.nih.gov/37541274/)
- Plesner et al. (Radiology 2023) :
  - objectif explicite : mesurer « the number of chest radiographs autonomously reported » ;
  - résultats : sensibilité de l'IA de 99,1 % pour les radios anormales et de 99,8 % pour les critiques, contre 72,3 % et 93,5 % pour les comptes rendus des radiologues ;
  - « Specificity of AI, and hence the potential autonomous reporting rate, was 28.0% of all normal posteroanterior chest radiographs [...] or 7.8% (120 of 1529 patients) of all posteroanterior chest radiographs. »

  — [Plesner et al., Radiology 2023, PubMed 36880947](https://pubmed.ncbi.nlm.nih.gov/36880947/)
- IDx-DR (npj Digit Med 2018), premier diagnostic IA autonome autorisé par la FDA :
  - « The AI system exceeded all pre-specified superiority endpoints at sensitivity of 87.2% [...] (>85%), specificity of 90.7% [...] (>82.5%), and imageability rate of 96.1% » ;
  - « Sensitivity is a patient safety criterion » ;
  - hypothèses nulles : sensibilité < 75 %, spécificité < 77,5 % ;
  - définition : « image-ability, defined as the percentage of participants with a completed FPRC grading and with a disease level AI system output, was 819/852 (96.1%) » ;
  - contrôle de sélection : chez les 33 participants où l'IA a rendu « insufficient image quality », la prévalence de la maladie (30 %) était « comparable to the mtmDR prevalence in the fully analyzable dataset ».

  — [Abràmoff et al., npj Digital Medicine 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6550188/)

### Inferences
- **Il y a deux exigences distinctes :**
  - la *complémentarité* (Bansal, Vaccaro) porte sur la **précision** : l'équipe doit battre les deux solos ;
  - l'*automatisation à précision égale* (Raghu, MASAI, Plesner, IDx-DR) porte sur la **charge** : faire aussi bien que l'humain seul avec moins d'effort humain.

  B-tout relève de la seconde. Sa référence naturelle est H = « l'humain valide tout », le niveau 0 de Morris (« human does everything »). Dans les essais cliniques, battre l'humain seul sur la charge à sécurité non inférieure est exactement le résultat exigé pour conclure à l'utilité. MASAI ne conclut pas « sûr » parce que le bras contrôle échouerait. Il conclut « sûr » au-dessus d'un plancher absolu, *et* « utile » parce que la charge baisse de 44,3 %.
- **L'imageabilité d'IDx-DR est l'analogue exact d'un taux de délégation.** Une IA qui répondrait « qualité insuffisante, voir un humain » à chaque patient aurait une sensibilité indéfinie et serait inutile. L'essai rapporte donc la part de cas tranchés, et vérifie que les cas non tranchés ne sont pas biaisés (prévalence comparable). Transposé : rapporter le taux d'actions déléguées par B-tout, et vérifier que les actions *non* déléguées ne concentrent pas les erreurs que l'agent aurait commises. Sinon, la sécurité affichée viendrait d'une sélection.
- Vaccaro (« when AI outperformed humans alone, we found losses ») et Bansal (acceptation « regardless of its correctness ») confirment que l'humain validateur n'est pas un plafond de précision. Pour les types d'actions où l'agent est très fiable, la validation systématique est une charge sans bénéfice, voire un risque. C'est l'argument d'utilité qui justifie B-tout. Il doit être **démontré** par une réduction de charge, pas supposé.

### Gaps
- Je n'ai trouvé aucun essai ni aucune norme qui fixe un seuil chiffré de réduction de charge du type « au moins X % ». MASAI, Plesner et IDx-DR rapportent la charge ou la couverture, mais leurs résumés ne montrent pas de seuil préspécifié pour elles. IDx-DR a des seuils pour la sensibilité et la spécificité seulement.
- Le g = 0,64 de Vaccaro (augmentation par rapport à l'humain seul) n'a pas été vérifié dans le texte intégral.
- Pas de revue 2021-2024 trouvée qui formule explicitement l'exigence « battre l'humain seul sur la charge à précision égale » comme norme générale de la recherche humain-IA. Elle apparaît dans des travaux particuliers (Raghu ; triage clinique).

## Q7 — Critères explicites : « part de décisions automatisées à taux d'erreur garanti » et « réduction de charge ≥ X % à sécurité égale »

### Takeaway
Le premier type de critère existe formellement et est standard en apprentissage automatique. La **classification sélective** garantit un risque cible avec forte probabilité et rapporte la **couverture** (part des cas décidés sans humain). SelectiveNet fait de la couverture une contrainte cible. Le cadre est transposé aux juges LLM (« Trust or Escalate » : accord humain garanti, couverture maximisée) et à la robotique (KnowNo). Le second type, un seuil chiffré de réduction de charge, **n'a été trouvé nulle part**. Les essais préspécifient un plancher de sécurité ou une non-infériorité, puis rapportent la réduction de charge comme critère secondaire.

### Cited Findings
- Classification sélective : « the classifier rejects instances as needed, to grant the desired risk (with high probability) ». Exemple ImageNet : une erreur top-5 de 2 % « can be guaranteed with probability 99.9%, and almost 60% test coverage ». — [Geifman & El-Yaniv, Selective Classification for Deep Neural Networks, NIPS 2017, arXiv 1705.08500](https://arxiv.org/abs/1705.08500)
- SelectiveNet : « Within an abstention-constrained framework, whereby the user specifies the desired target coverage, we optimize, end-to-end, a neural network with an integrated reject option, designed to be optimal for the required coverage slice. » Les résultats sont présentés comme un compromis « risk–coverage ». — [Geifman & El-Yaniv, ICML 2019, arXiv 1901.09192](https://arxiv.org/abs/1901.09192)
- Trust or Escalate (2024) :
  - garantie : l'évaluation par LLM peut garantir l'accord humain « to a user-specified agreement level » ;
  - la fiabilité réside dans l'accord « but also in maximizing the coverage of evaluated instances without abstention » ;
  - exemple : « guarantees over 80% human agreement with almost 80% test coverage » sur un sous-ensemble de Chatbot Arena.

  — [Jung, Brahman & Choi, arXiv 2407.18370](https://arxiv.org/abs/2407.18370)
- KnowNo : réussite garantie au niveau 1−ϵ choisi par l'utilisateur, avec un taux d'aide humaine minimisé et comparé entre méthodes (voir Q5). — [Ren et al., arXiv 2307.01928](https://arxiv.org/abs/2307.01928)
- Essais cliniques : MASAI combine un plancher de sécurité absolu (« more than 3 per 1000 ») et une non-infériorité, puis rapporte la réduction de charge (−44,3 %) en critère secondaire. IDx-DR préspécifie des seuils de supériorité pour la sensibilité (> 85 %) et la spécificité (> 82,5 %), et rapporte l'imageabilité (96,1 %). — [MASAI, PubMed 37541274](https://pubmed.ncbi.nlm.nih.gov/37541274/) ; [IDx-DR, PMC6550188](https://pmc.ncbi.nlm.nih.gov/articles/PMC6550188/)
- RAND évoque la non-infériorité pour les véhicules autonomes : performance « no more than some (small) amount worse than human-driven cars », avec un dimensionnement adapté. — [RAND RR-1478 PDF](https://www.rand.org/content/dam/rand/pubs/research_reports/RR1400/RR1478/RAND_RR1478.pdf)

### Inferences
- **« Part automatisée à taux d'erreur garanti »** est le langage exact de la classification sélective et de ses dérivés (Trust or Escalate, KnowNo). Le protocole peut s'y rattacher : B-tout est un *sélecteur* (déléguer ou faire valider), le budget d'erreur est le risque cible, et la part d'actions déléguées est la **couverture**. Dans cette littérature, on ne déclare pas un sélecteur meilleur parce qu'un concurrent dépasse le risque cible. On compare la **couverture au même risque** (courbe risque-couverture), ou le risque à couverture fixée (SelectiveNet). La couverture nulle est le point trivial de la courbe, jamais un succès.
- **« Réduction de charge ≥ X % »** : aucun seuil universel trouvé. Les pratiques observées fixent la sécurité par un plancher ou une non-infériorité, puis exigent une réduction de charge (MASAI) ou une couverture (Plesner, IDx-DR) rapportée avec son intervalle. Si l'on veut un X, il faudra le justifier soi-même, à la manière d'une « différence minimale utile ». Une borne inférieure strictement positive est le minimum défendable.

### Gaps
- Le registre ClinicalTrials.gov de MASAI (NCT04838756) n'a pas été consulté. Je ne sais pas si la charge y a un seuil d'hypothèse.
- Aucune norme d'IA (AI Act, NIST, ISO/IEC 42001) n'a été trouvée qui impose un taux d'automatisation minimal ou une couverture à risque garanti. Ce point n'a pas été cherché en profondeur.

## Q8 — Transversal : comment les évaluateurs empêchent-ils qu'un système qui n'agit jamais seul soit compté comme un succès ? Quelle condition ajouter à « confirmée » ?

### Takeaway
Partout où l'on certifie un système autonome ou délégant, la revendication de sécurité est **couplée à une revendication d'utilité mesurée sur la même exposition**. La référence explicite est « ne rien automatiser » ou « l'humain fait tout ». Le dépassement de budget d'un concurrent n'est jamais compté comme une victoire. Les mécanismes observés se rangent en six familles :
1. normaliser par l'exposition autonome : désengagements par mille autonome, VMT ;
2. rapporter la couverture à risque garanti : classification sélective, KnowNo, Trust or Escalate, imageabilité ;
3. afficher la référence inerte : NoAct de ToolEmu, niveau 0 de Morris ;
4. utiliser un score qui crédite seulement l'action réussie et conforme : CuP, ROHE ;
5. mener des essais à deux faces, sécurité et fausse alerte : FPR/FNR de l'auto mode, fausse activation de l'AEB ;
6. hiérarchiser les critères cliniques : sécurité comme porte, puis réduction de charge (MASAI).

La condition manquante de « confirmée » correspond aux familles 2 et 6 : **une réduction établie de la charge de validation par rapport à H (tout valider), à budget respecté**.

### Cited Findings
- Normalisation par l'exposition : le rapport de désengagement exige « the total number of miles each autonomous vehicle tested in autonomous mode ». La réforme de 2026 ajoute les « Vehicle Miles Traveled » et les « Vehicle immobilizations ». — [13 CCR §227.50](https://www.law.cornell.edu/regulations/california/13-CCR-227.50) ; [DMV 20/02/2026](https://www.dmv.ca.gov/portal/news-and-media/autonomous-vehicle-permit-holders-in-california-logged-more-than-9-million-test-miles-between-december-1-2024-and-november-30-2025)
- Couverture à risque garanti : « to grant the desired risk (with high probability) » avec « almost 60% test coverage » ([Geifman & El-Yaniv 2017](https://arxiv.org/abs/1705.08500)). La fiabilité réside aussi dans « maximizing the coverage of evaluated instances without abstention » ([Jung et al. 2024](https://arxiv.org/abs/2407.18370)).
- Référence inerte affichée : « NoAct [...] could achieve a perfect safety score but a nearly 0 helpfulness score ». — [ToolEmu](https://arxiv.org/abs/2309.15817)
- Score qui pénalise la prudence excessive : « CuP penalizes over-cautiousness as well as recklessness » ([ST-WebAgentBench](https://arxiv.org/abs/2410.06703)). ROHE : performance « normalized by the total human effort required » ([Fleet-DAgger](https://arxiv.org/abs/2206.14349)).
- Évaluation à deux faces : FPR (« fraction of benign actions it blocks ») et FNR (« fraction of dangerous actions the classifier lets through ») ([Anthropic auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)) ; essais de fausse activation de l'AEB ([NPRM FMVSS 127](https://www.govinfo.gov/content/pkg/FR-2023-06-13/pdf/2023-11863.pdf)).
- Hiérarchie sécurité puis utilité : plancher de sécurité, puis « substantially lower screen-reading workload » ([MASAI](https://pubmed.ncbi.nlm.nih.gov/37541274/)). Sensibilité (« a patient safety criterion »), spécificité et imageabilité ([IDx-DR](https://pmc.ncbi.nlm.nih.gov/articles/PMC6550188/)).
- Coût de l'inaction reconnu :
  - erreur de type II « a serious error » ([RAND RR-1478](https://www.rand.org/content/dam/rand/pubs/research_reports/RR1400/RR1478/RAND_RR1478.pdf)) ;
  - « perfect to be the enemy of good » ([RAND RR-2150](https://www.rand.org/pubs/research_reports/RR2150.html)) ;
  - « may be socially and ethically mandated » ([Commission d'éthique, règle 6](https://www.bmvi.de/SharedDocs/EN/Documents/G/ethic-commission-report.pdf?__blob=publicationFile)) ;
  - « disuse » ([Parasuraman & Riley 1997](https://journals.sagepub.com/doi/10.1518/001872097778543886)) ;
  - « deployment overhang » ([Anthropic 2026](https://www.anthropic.com/research/measuring-agent-autonomy)) ;
  - « a system comprised of entirely L1 agents is not ideal » ([Feng et al.](https://arxiv.org/abs/2506.12469)).
- Évaluer l'autonomie comme « the minimum level of user involvement needed for the agent to exceed a certain accuracy or pass rate threshold ». — [Feng et al., assisted evaluation](https://arxiv.org/abs/2506.12469)

### Inferences
*(Tout ce qui suit est de mon fait. Notation : H = règle « tout valider » ; V(R) = nombre de validations humaines de la règle R sur les rejeux ; A(R) = 1 − V(R)/V(H), le taux d'automatisation, c'est-à-dire la couverture ; b = budget d'erreur.)*

**1. Pourquoi le défaut est grave, et double**
- Le chemin « référence battue parce qu'elle dépasse son budget » donne une victoire gratuite. C'est l'inverse de toutes les pratiques recensées : en classification sélective, en essai clinique ou dans KnowNo, un concurrent qui viole la garantie est *exclu* ou *recalibré*. Il ne fait pas gagner les autres.
- La condition de sécurité (« pas de dépassement établi ») est un **non-rejet**. Sa puissance croît avec le nombre d'actions déléguées. Une règle qui délègue peu ou rien la satisfait par manque de données, pas par preuve. C'est l'argument de RAND et de Koopman : 275 M de miles sans échec pour *démontrer* un taux, selon la règle de trois.

**2. Condition recommandée, la plus directe : utilité établie face à H**
- Énoncé : « La réduction de validations humaines de B-tout par rapport à H est établie : borne inférieure unilatérale de A(B-tout) > δ_min, avec δ_min préspécifié et > 0, testée après la porte de sécurité. »
- Effet : une règle qui ne délègue rien a A = 0 et échoue par construction.
- Sources qui portent cette forme :
  - MASAI (sécurité, puis −44,3 % de charge) ;
  - Plesner (28 % de normaux rapportés seuls à ≥ 99 % de sensibilité) ;
  - IDx-DR (imageabilité) ;
  - classification sélective (couverture à risque garanti) ;
  - KnowNo (aide minimale à réussite garantie) ;
  - Feng (implication minimale pour atteindre T) ;
  - NoAct de ToolEmu.
- Choix de δ_min : > 0 au minimum. Mieux : une « réduction minimale utile » justifiée a priori. Aucune source ne fournit de X universel (voir Q7).
- Mise en œuvre statistique : une procédure séquentielle (gatekeeping) qui teste la sécurité, puis l'utilité, est l'usage clinique. À vérifier avec la note statistique dédiée.

**3. Variante plus complète : comparer les références à risque égal**
- Remplacer « référence battue si son dépassement est établi » par « référence battue si, recalibrée à son réglage le plus permissif qui respecte b, elle demande plus de validations que B-tout ».
- Le recalibrage se fait sur une partition séparée, ou par la même procédure max-T. Exemples de réglage : seuil de risque pour le tri par risque, liste tronquée aux catégories les moins risquées.
- Sans réglage permissif acceptable, chaque famille de références se replie sur θ = 0, c'est-à-dire H. Cette variante **contient donc la condition 2**.
- C'est la comparaison « couverture à risque égal » de la classification sélective et de KnowNo, et la logique Pareto d'AgentDojo.
- Coût : elle suppose des références paramétrables, et une étape de calibration qui ne fuit pas sur l'évaluation.

**4. Garde-fous complémentaires, non indispensables pour le seul défaut**
- *Plancher d'exposition ou preuve de conformité.* Exiger assez d'actions déléguées pour que la porte de sécurité ait de la puissance, par exemple n_délégué ≥ 3/b pour une borne à 95 % sans erreur. Ou basculer vers « borne supérieure du taux d'erreur des actions déléguées ≤ b ». Inspiré de RAND, d'ISO 21448 (cibles de validation) et d'UL 4600 (SPI à seuil).
- *Anti-écrémage.* Rapporter A(B-tout) par type d'action et par catégorie de risque. Exiger éventuellement A > 0 sur au moins une catégorie non triviale (écriture, action irréversible), ou pondérer les validations par le risque. Raison : critique des trajets faciles du DMV, ODD trivial du niveau 4 dans J3016, transfert de risque chez Koopman, sous-groupes dans ISO 21448.
- *Contrôle de sélection.* Vérifier que les actions *non* déléguées ne concentrent pas les erreurs qu'aurait commises l'agent, par une comparaison de taux d'erreur entre actions déléguées et retenues. Analogue de la prévalence comparable chez les cas « insufficient quality » d'IDx-DR.
- *Indicateurs de rapport, non confirmatoires.* ROHE (succès par validation, avec +1 au dénominateur) et pourcentage d'autonomie avec coût d'intervention (Bojarski), pour comparer visuellement les règles.

**5. Hypothèse implicite à documenter**
- Le rejeu traite la validation humaine comme parfaite, alors que la littérature documente la fatigue d'approbation : 93 % d'acceptation chez Anthropic, « rubber stamp » chez OpenAI et Feng, biais d'automatisation dans l'AI Act. Cela biaise *contre* B-tout.
- La condition 2 reste donc conservatrice. Une analyse de sensibilité avec un validateur imparfait pourrait être rapportée hors du critère confirmatoire.

### Gaps
- Aucune source ne traite le cas exact d'une règle d'autonomie méritée évaluée **hors ligne par rejeu** avec un budget d'erreur et un contrôle multiple max-T. La transposition repose sur des analogies : classification sélective, essais cliniques, AEB, benchmarks d'agents.
- Aucune valeur de référence trouvée pour δ_min (réduction minimale utile de la charge de validation) dans le domaine des agents.
- Les modalités statistiques (gatekeeping, puissance de la condition d'utilité sous max-T, calibration sans fuite des références) ne relèvent pas de cette note et restent à valider.
