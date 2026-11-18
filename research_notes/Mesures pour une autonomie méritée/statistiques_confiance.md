# Statistiques de la confiance : promouvoir / révoquer un agent sur preuves rares

Légende : [V] = vérifié dans une source consultée (fetch/search) ; [C] = calculé par moi (scipy, 2026-11-04) ; [M] = connaissance de mémoire, source non rouverte, à vérifier ; [I] = inférence. Aucune référence inventée ; ce qui n'a pas pu être vérifié est dit.

## 1. Zéro échec, règle de trois, démonstration de fiabilité, intervalles binomiaux

### Takeaway
Avec 0 échec sur n essais indépendants, borne sup. à 95 % unilatérale = 1-0,05^(1/n) ≈ 3/n. Prouver « taux d'échec < 1 % à 95 % » exige 299 succès d'affilée ; « < 5 % » 59 ; « < 0,1 % » 2 995. Chaque échec toléré coûte cher (1 échec : 473 essais pour p<1 %). Le 1 refus sur 83 approbations donne une borne sup. de 5,6 % seulement : trop peu de données pour des seuils exigeants.

### Cited Findings
- Règle de trois : n sujets, 0 événement => borne sup. IC 95 % ≈ 3/n ; bonne approximation dès n>30 ; à n=20, 15 % vs 14 % exact. Réf. originale : Hanley & Lippman-Hand, « If nothing goes wrong, is everything all right? Interpreting zero numerators », JAMA 1983;249(13):1743-1745, PMID 6827763 — [Wikipedia, rule of three](https://en.wikipedia.org/wiki/Rule_of_three_(statistics)) [V, via recherche ; article original non ouvert]
- Success-run (démonstration de fiabilité attribut) : après n succès sans échec, borne inf. de fiabilité R_L=(1-C)^(1/n) ; n = ceil(ln(1-C)/ln(R)). Exemples : R=95 %/C=90 % => 45 ; R=99 %/C=95 % => 299 ; avec 1 échec toléré 77, 2 échecs 105 (pour R=95 %, C=90 %) — [Khuston, reliability & confidence for pass/fail](https://khuston.github.io/statistics/2021/01/25/reliability-and-confidence-for-pass-fail-data.html) ; [MetricGate, reliability demonstration test](https://metricgate.com/docs/reliability-demonstration-test/) ; chiffres 45/299/77/105 recalculés [C].
- Hypothèses du success-run : unités indépendantes, identiques, défaillance aléatoire ; les défaillances logicielles sont systématiques (bugs), la formule est « généralement réservée au matériel » — [MetricGate](https://metricgate.com/docs/reliability-demonstration-test/) [V]
- Dérivation bayésienne : le success-run = postérieur Beta(1, n+1) pour le taux d'échec avec prior uniforme ; thèse sur démonstration bayésienne zéro-échec et effet du prior sur la taille d'essai — [Rahrouh, Durham 2005](https://etheses.durham.ac.uk/id/eprint/2389/) [V sur existence/sujet].
- Intervalles : Wald (normal) a une couverture chaotique, à proscrire en petit n ; recommandés Wilson ou Jeffreys (équi-queues) en petit n, Agresti-Coull en grand n — Brown, Cai & DasGupta, « Interval Estimation for a Binomial Proportion », Statistical Science 16(2):101-133, 2001, doi:10.1214/ss/1009213286 — [Project Euclid](https://projecteuclid.org/euclid.ss/1009213286) [V]
- Clopper-Pearson (1934, Biometrika 26:404-413) = exact, conservateur ; borne sup. unilatérale = quantile Beta(k+1, n-k) [M, formule standard ; non rouvert]. Jeffreys = Beta(k+0,5 ; n-k+0,5) [V pour le prior : [MetricGate Bayesian](https://metricgate.com/docs/bayesian-binomial-reliability/) ; calcul [C]].
- Prior Jeffreys non informatif => intervalles larges en très petit n ; prior informatif issu d'historique possible — [MetricGate](https://metricgate.com/docs/bayesian-binomial-reliability/) [V]

### Chiffres concrets [C] (borne sup. 95 % unilatérale du taux d'échec, 0 échec sur n)
| n | Clopper-Pearson | 3/n | Jeffreys | Unif. Beta(1,1) | Wilson |
|---|---|---|---|---|---|
| 10 | 25,9 % | 30 % | 17,1 % | 23,8 % | 21,3 % |
| 20 | 13,9 % | 15 % | 9,1 % | 13,3 % | 11,9 % |
| 30 | 9,5 % | 10 % | 6,2 % | 9,2 % | 8,3 % |
| 50 | 5,8 % | 6 % | 3,8 % | 5,7 % | 5,1 % |
| 83 | 3,54 % | 3,61 % | 2,28 % | 3,50 % | 3,16 % |
| 100 | 2,95 % | 3 % | 1,9 % | 2,9 % | 2,6 % |
| 216 | 1,38 % | 1,39 % | 0,88 % | 1,37 % | 1,24 % |
| 300 | 0,99 % | 1 % | 0,64 % | 0,99 % | 0,89 % |
| 702 | 0,43 % | 0,43 % | 0,27 % | 0,43 % | 0,38 % |
| 1000 | 0,30 % | 0,30 % | 0,19 % | 0,30 % | 0,27 % |
Note : Jeffreys « zéro échec » est moins conservateur que CP ; pour une barrière de sécurité, utiliser CP (garantie de couverture ≥ nominale).

Essais sans échec nécessaires, n = ceil(ln(1-C)/ln(1-p)) [C] :
| p (taux d'échec toléré) | C=90 % | C=95 % | C=99 % |
|---|---|---|---|
| 10 % | 22 | 29 | 44 |
| 5 % | 45 | 59 | 90 |
| 2 % | 114 | 149 | 228 |
| 1 % | 230 | 299 | 459 |
| 0,5 % | 460 | 598 | 919 |
| 0,1 % | 2 302 | 2 995 | 4 603 |
Avec k échecs tolérés (p=1 %, C=95 %) : k=0 -> 299 ; 1 -> 473 ; 2 -> 628 ; 3 -> 773 [C]. (p=5 %, C=90 % : 45 / 77 / 105 / 132.)

Application aux données du pilote [C] :
- 83 approbations, 1 refus : taux de refus 1,2 % ; IC CP 95 % bilatéral [0,03 % ; 6,5 %] ; borne sup. unilatérale 5,6 % ; Jeffreys bilatéral [0,13 % ; 5,5 %]. Distinguer : refus humain != échec de l'agent (le refus peut être un désaccord légitime) [I].
- 17 incidents / 216 tâches : 7,9 % ; CP bilatéral [4,65 % ; 12,3 %]. Pas de promotion « < 1 % » possible sur ce palier tant que les incidents ne sont pas ramenés à ~0 sur ≥299 tâches consécutives d'une même configuration.
- Si 0 incident sur 216 tâches : borne sup. 1,38 % (95 %). Il faudrait 299 pour 1 %.
- 702 blocages / 216 tâches : ce n'est pas un taux binomial (3,25 blocages/tâche, plusieurs par tâche) ; voir §5.

### Inferences
- [I] Un seuil de promotion honnête pour un palier à faible enjeu (p<5 %, C=90-95 %) demande 45-59 tâches propres ; un palier à enjeu moyen (p<1 %) ≈ 300 ; un palier à enjeu élevé (p<0,1 %) ≈ 3 000, hors de portée d'une PME sauf à agréger plusieurs déploiements (= argument pour un protocole ouvert qui mutualise des preuves, sous réserve d'exchangeabilité).
- [I] La règle de trois suppose indépendance et stationnarité ; sur des agents, les tâches d'un même client/jour sont corrélées (effet de grappe) => n effectif < n nominal. Correction possible : facteur d'effet de plan 1+(m-1)ρ [M, notion standard Kish ; non sourcée ici].
- [I] Le test doit porter sur la population de tâches du palier visé (couverture), pas seulement sur le volume : 299 tâches triviales ne prouvent rien sur les cas rares.

### Gaps
- Texte original de Hanley & Lippman-Hand non ouvert (PMID cité via recherche). Newman 1995 (JAMA, lettre) mentionné par la recherche, non vérifié.
- Page NIST e-Handbook consultée (apr43) ne traite pas la démonstration zéro-échec ; pas de source NIST pour success-run. Source primaire du success-run (SAE 972753 « Attribute Reliability and the Success Run: A Review ») vue en titre seulement.
- Clopper-Pearson 1934 non ouvert.

## 2. Décisions séquentielles : SPRT, CUSUM, cartes de contrôle

### Takeaway
SPRT de Wald (1945) compare H0 « taux d'échec acceptable p0 » à H1 « taux inacceptable p1 » et s'arrête dès que le log-rapport de vraisemblance franchit un seuil : en moyenne ~2x moins d'essais qu'un test à taille fixe, et utilisable dans les deux sens (promouvoir / révoquer). CUSUM détecte une dégradation après changement de configuration plus vite qu'un seuil fixe pour les petits décalages.

### Cited Findings
- SPRT : Wald, « Sequential Tests of Statistical Hypotheses », Ann. Math. Statist. 16(2):117-186, 1945, doi:10.1214/aoms/1177731118 — [Project Euclid](https://projecteuclid.org/euclid.aoms/1177731118) [V]
- Règle : S_i = S_{i-1} + log Λ_i ; continuer si a<S_i<b ; accepter H1 si S_i ≥ b, H0 si S_i ≤ a ; seuils a ≈ ln(β/(1-α)), b ≈ ln((1-β)/α) ; approximations pour données discrètes (franchissement entre deux observations) — [Wikipedia SPRT](https://en.wikipedia.org/wiki/Sequential_probability_ratio_test) [V]
- CUSUM tabulaire : S_hi(i)=max(0, S_hi(i-1)+x_i-μ0-k) ; S_lo(i)=max(0, S_lo(i-1)+μ0-k-x_i) ; alarme si > h ; k=δσ/2 ; règle pratique k = moitié du décalage à détecter, h ≈ 4 à 5 ; plus efficace que Shewhart pour décalages ≤ 2σ — [NIST/SEMATECH e-Handbook, 6.3.2.3 CUSUM](https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm) [V]
- CUSUM original : E. S. Page, « Continuous Inspection Schemes », Biometrika 41(1-2):100-115, 1954, doi:10.1093/biomet/41.1-2.100 [M, DOI non ouvert].

### Chiffres concrets (SPRT binomial, α=β=5 %) [C]
Pour chaque tâche : échec ajoute ln(p1/p0), succès ajoute ln((1-p1)/(1-p0)) ; seuils ±ln(19)=±2,944.
| H0 (acceptable) vs H1 (inacceptable) | pas échec | pas succès | succès consécutifs pour accepter H0 | n moyen sous H0 | n moyen sous H1 |
|---|---|---|---|---|---|
| p0=2 % vs p1=10 % | +1,609 | -0,085 | 35 | 52 | 31 |
| p0=1 % vs p1=5 % | +1,609 | -0,041 | 72 | 107 | 64 |
| p0=5 % vs p1=15 % | +1,099 | -0,111 | 27 | 52 | 38 |
(n moyen = approximation de Wald [M].) Lecture : un échec annule ~19 succès (cas 2 %/10 %) ; 2 échecs rapprochés suffisent à franchir b si peu de crédit accumulé. Le « temps de preuve » est bien inférieur aux 299 du test fixe parce qu'on compare deux hypothèses (p0 vs p1) au lieu de borner p vers zéro ; on ne prouve pas p<1 %, on prouve « p plutôt p0 que p1 ».
- Promotion = SPRT « p ≤ p0 vs p ≥ p1 » ; Révocation = SPRT miroir (H0 : p=p0 ok, H1 : p=p1 dégradé) tournant en continu avec remise à zéro de S après chaque décision (SPRT répété) ou, mieux, CUSUM de Page qui borne S inférieurement à 0 (c'est un SPRT redémarré) [I].
- CUSUM Bernoulli : référence k_Bern = ln((1-p0)/(1-p1)) / ln(p1(1-p0)/(p0(1-p1))) [M, forme standard Page/Moustakides ; non vérifiée] ; alarme h≈4-5 (règle NIST pour moyennes).

### Inferences
- [I] Hypothèses cassées pour agents : (a) i.i.d. : tâches non homogènes, dérive de la population de tâches ; (b) p0/p1 doivent être pondérés par la sévérité (§4) ; (c) regarder les données en continu sans correction gonfle α pour un test fixe, mais le SPRT contrôle α,β par construction ; en revanche le SPRT suppose p fixe : après changement de config, redémarrer S.
- [I] Pour des preuves « toujours valides » (anytime-valid) on peut citer les e-processes/martingales de test (Ramdas et al.) : non recherché ici.

### Gaps
- Pas de source primaire consultée pour l'ASN de Wald ni pour le CUSUM Bernoulli ; pas d'article appliquant SPRT/CUSUM à l'autonomie d'agents LLM trouvé.
- Recherche arXiv « sequential testing agent autonomy » : rien de pertinent (résultats adjacents seulement : bornes bootstrap, escalade sélective) ; tous les ID arXiv 26xx retournés sont à vérifier avant citation.

## 3. Modèles bayésiens de confiance/réputation, oubli, transfert après changement de configuration

### Takeaway
Beta reputation (Jøsang & Ismail 2002) : espérance (r+1)/(r+s+2), mise à jour par comptage, oubli exponentiel par facteur λ. C'est exactement un posterior Beta avec compteurs décayés. Le transfert d'évidence après changement de configuration se traite par prior réduit (power prior / commensurate prior) plutôt que remise à zéro totale ou conservation totale.

### Cited Findings
- Jøsang & Ismail, « The Beta Reputation System », 15th Bled eCommerce Conference, 17-19 juin 2002 — [PDF uio.no](https://mn.uio.no/ifi/english/people/aca/josang/publications/ji2002-bled.pdf) [V]. Contenu vérifié dans le PDF (texte partiellement illisible, formules lues par recoupement) : exemple 7 observations positives + 1 négative => espérance 0,8 = (7+1)/(7+1+2) ; prior sans observation Beta(1,1) ; §2.6 « Forgetting » : facteur λ ∈ [0,1], λ=1 = rien oublié, λ=0 = seule la dernière observation compte ; version récursive r_n = λ·r_{n-1} + r_new, s_n = λ·s_{n-1} + s_new (éq. 13) ; l'ordre compte ; un schéma attribué à Jøsang [4] (Jøsang 2001). Opérateurs : combinaison (somme de r,s), escompte (discounting) pour chaînes de recommandation, associatif non commutatif.
- Poids effectif sous oubli : somme géométrique => taille d'échantillon effective max ≈ 1/(1-λ) par flux de rythme 1 [C: arithmétique ; calcul de moi]. λ=0,98 par tâche => ≈50 tâches de mémoire ; λ=0,99 => 100.
- Lien oubli exponentiel et modèles probabilistes de confiance : analyse du principe de décroissance exponentielle — [data.zhenzhi.com, référencé en recherche](https://data.zhenzhi.com/details/1/894694543) [V partiel, source secondaire, non lue].
- Dérive de concept bayésienne : Bach & Maloof, « A Bayesian Approach to Concept Drift », NeurIPS 2010 — distribution de probabilité sur la position du dernier point de dérive — [NeurIPS](https://papers.NeurIPS.cc/paper_files/paper/2010/file/8edd72158ccd2a879f79cb2538568fdc-Paper.pdf) [V sur le résumé]
- Power priors hiérarchiques pour flux de données : taux d'apprentissage (poids de l'ancien) avec son propre prior, dérive abrupte ou graduelle — [arXiv 1707.02293](https://arxiv.org/pdf/1707.02293) [V sur le résumé]
- Priors commensurables / power priors (Hobbs, Carlin, Mandrekar, Sargent 2011) : l'emprunt d'historique dépend de l'accord entre données historiques et courantes ; emprunt homogène total peut ruiner puissance et erreur de type I si l'historique est biaisé — [PMC4007051 (2014, s'appuie sur Hobbs 2011)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4007051) [V]
- Logique subjective (opinions b,d,u,a, escompte, fusion) : travaux de Jøsang ; livre « Subjective Logic » Springer 2016 [M, non vérifié, pas de DOI exact en main].

### Inferences
- [I] Règle de transfert par type de changement : prior Beta(a,b) = (a0,b0) + w·(r_old, s_old), avec w ∈ [0,1] selon la distance du changement (w=1 changement cosmétique ; w≈0,2-0,5 prompt/outil ajouté ; w=0 changement de modèle de base ou élargissement de permissions). Le calibrer sur des données de rejouage (même tâches avant/après) : si les résultats concordent (commensurabilité), augmenter w.
- [I] Asymétrie recommandée : l'évidence négative (échecs) se transfère à w=1 (prudence), l'évidence positive est escomptée (w<1). L'oubli devrait s'appliquer aux succès, pas aux incidents graves (incidents de classe majeure jamais oubliés dans la fenêtre de revue).
- [I] « Remise à zéro » = prior plat Beta(1,1) : coûte à nouveau 299 tâches pour p<1 %. Garder une période de probation avec périmètre réduit (canari, §6) pendant que l'évidence se reconstitue.

### Gaps
- Équations de Jøsang & Ismail non extraites proprement (PDF à polices encodées) ; (r+1)/(r+s+2) et la récurrence λ vérifiés par recoupement avec l'exemple 0,8 et le texte du §2.6, pas lisibles verbatim.
- Aucun article trouvé qui traite spécifiquement du transfert d'évidence entre versions de modèles LLM/agents.

## 4. Risque pondéré par la sévérité, coûts asymétriques, comptage des quasi-accidents (blocages de garde-fous)

### Takeaway
Aucune source vérifiée ne donne une formule canonique ; la littérature statistique fournit des briques (décision bayésienne à pertes asymétriques, taux d'événements pondérés). Les 702 blocages ne sont pas des « échecs évités » homogènes : ils mesurent à la fois la tentative de l'agent ET l'efficacité de la barrière ; à traiter comme évidence séparée sur un taux de tentatives dangereuses.

### Cited Findings
- Couverture des garde-fous / approbations : chez Claude Code, les nouveaux utilisateurs auto-approuvent ~20 % des sessions, >40 % après 750 sessions ; interventions humaines par session de 5,4 à 3,3 ; les utilisateurs expérimentés interrompent aussi plus (supervision qui change de nature) — [Anthropic, Measuring AI agent autonomy in practice, 2026-02-18](https://www.anthropic.com/research/measuring-agent-autonomy) [V via extraits de recherche, page originale non ouverte ; chiffres API 80 %/0,8 % non confirmés]
- Un cas d'étude industriel conclut que l'autonomie non contrainte donne des résultats instables : contraintes explicites et supervision humaine — [arXiv 2605.01471](https://arxiv.org/html/2605.01471) [V sur extrait, source non évaluée]
- Une étude d'escalade sélective rapporte « decision risk » (part de décisions autonomes invalides) et note que zéro décision dangereuse est un résultat empirique, pas une garantie — [arXiv 2609.26532](https://arxiv.org/pdf/2609.26532) [V sur extrait seulement ; ID douteux, à vérifier]

### Inferences (aucune source ; propositions de conception)
- [I] Risque = Σ_c p_c · S_c (fréquence par classe de sévérité c x coût). Faire une borne sup. CP par classe, puis majorer : R_sup = Σ S_c · ub_c. Les classes graves (irréversible, argent, tiers) ont n faible => borne énorme => ce sont elles qui bloquent la promotion : correct, c'est voulu.
- [I] Coûts asymétriques : fausse promotion (coût C_FP, incident) >> fausse rétrogradation (C_FD, perte de productivité). Décision de Bayes : promouvoir si P(p>p_max | données)·C_FP < P(p≤p_max | données)·C_FD, soit seuil de probabilité postérieure C_FD/(C_FP+C_FD). Exemple : C_FP=20·C_FD => exiger P(p≤p_max) ≥ 95,2 % (cohérent avec C=95 %). Révocation : seuil bas (P(dégradé) ≥ ~5-10 % suffit).
- [I] Quasi-accidents : modéliser une tentative dangereuse comme événement Poisson (taux λ_t = 702/216 ≈ 3,25 blocages par tâche sur 5 semaines [C, simple division]) et la barrière comme Bernoulli avec efficacité inconnue e. Échec de la barrière (blocage contourné ou faux négatif) = incident. Un blocage seul prouve la barrière mais PAS la sûreté de l'agent : si l'agent tente 3 fois par tâche, la barrière porte toute la sûreté. Règle : ne pas promouvoir l'agent sur la base de blocages ; promouvoir sur (a) incidents sur actions autorisées et (b) tendance du taux de tentatives bloquées (en baisse = l'agent apprend la limite ; stable ou en hausse après changement de config = alerte). Pyramide « 1 accident ↔ N quasi-accidents » (Heinrich) : ratio contesté [M, non vérifié] ; ne pas l'utiliser comme coefficient.
- [I] Les incidents de la période (17) à étiqueter par sévérité et par classe d'action avant tout calcul ; mêmes 17 incidents ne valent pas 17 échecs homogènes.

### Gaps
- Pas de source trouvée sur les statistiques de quasi-accidents pour agents IA, ni sur la conversion barrière/agent. Heinrich non vérifié. Politiques d'augmentation de limite de crédit : voir §6 (non sourcées).

## 5. Fiabilité répétée : pass^k (τ-bench)

### Takeaway
Pour une tâche répétée k fois, pass^k = probabilité que les k essais réussissent ; avec taux de succès p par essai indépendant, pass^k = p^k : il s'effondre vite. Il mesure la cohérence, pas la moyenne ; un agent à 95 % par essai n'a que 66 % de pass^8.

### Cited Findings
- Définition : « chance que les k essais i.i.d. d'une tâche réussissent tous », moyennée sur les tâches ; estimateur non biaisé : pass^k = E_tâches[ C(c,k) / C(n,k) ] où c réussites sur n essais ; pass@k = 1 - E[C(n-c,k)/C(n,k)] ; pass^1 = E[c/n] — Yao, Shinn, Razavi, Narasimhan, « τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains », 2024, arXiv:2406.12045 — [arXiv](https://arxiv.org/abs/2406.12045), formule lue dans le PDF [V]
- Résultats : gpt-4o function-calling < 50 % de succès; pass^8 < 25 % sur τ-retail, même pour le meilleur agent à >60 % de succès moyen — [arXiv 2406.12045](https://arxiv.org/abs/2406.12045) [V]
- Hypothèse du papier : la stochasticité vient de l'échantillonnage du LM (utilisateur et agent) à base de données et prompt identiques [V, PDF].

### Chiffres concrets [C] (cas homogène p^k)
| p par essai | k=1 | 2 | 4 | 8 | 16 |
|---|---|---|---|---|---|
| 0,99 | 0,990 | 0,980 | 0,961 | 0,923 | 0,851 |
| 0,98 | 0,980 | 0,960 | 0,922 | 0,851 | 0,724 |
| 0,95 | 0,950 | 0,902 | 0,815 | 0,663 | 0,440 |
| 0,90 | 0,900 | 0,810 | 0,656 | 0,430 | 0,185 |
| 0,80 | 0,800 | 0,640 | 0,410 | 0,168 | 0,028 |
Pour pass^k ≥ 0,95 avec k=8 : p ≥ 0,95^(1/8)=0,9936.

### Inferences
- [I] Lecture protocole : définir une « tâche récurrente » (même type d'action chez un client, répété chaque semaine) ; pass^k mesure « sur k exécutions de la même classe, aucune n'échoue » ; ça se relie directement à un seuil p_max : pass^k ≥ 1-α_k si p ≤ 1-(…) . Un palier d'autonomie portant sur 50 exécutions/mois exige p_échec ≪ 2 %.
- [I] En production, les tâches ne sont pas des répliques i.i.d. d'une même tâche : estimer c/n par classe de tâches, et regrouper avec précaution (hétérogénéité => variance supplémentaire, modèle Beta-binomial hiérarchique).

### Gaps
- τ-bench est un benchmark de simulation, pas des logs de production ; l'extrapolation p^k suppose indépendance entre essais, démentie dès que l'échec dépend de la tâche (dans ce cas, pass^k >= p^k est possible quand p varie fortement entre tâches, inégalité de Jensen [I]).

## 6. Analogues pratiques : budgets d'erreur SRE, canaris, croissance de fiabilité logicielle, crédit

### Takeaway
SRE : budget d'erreur = 100 % - SLO, consommation mesurée par taux de combustion (burn rate), alertes multi-fenêtres ; les déploiements progressifs (Argo Rollouts, Flagger) font du rollback automatique sur dépassement d'un nombre d'échecs de vérification : ce sont des règles de révocation prêtes à l'emploi. Les politiques de crédit et les modèles de croissance de fiabilité n'ont pas pu être sourcés ici.

### Cited Findings
- Budget d'erreur : « 100 % moins le SLO » ; ex. SLO 99,9 % sur 3 millions de requêtes => 3 000 erreurs ; une panne de 1 500 erreurs coûte 50 % du budget — [Google SRE Workbook, Implementing SLOs](https://sre.google/workbook/implementing-slos/) [V]
- Burn rate : vitesse à laquelle le service consomme le budget relativement au SLO. Alertes recommandées pour SLO 99,9 % : page à 14,4x sur 1 h (fenêtre courte 5 min, 2 % du budget) ; page à 6x sur 6 h (30 min, 5 %) ; ticket à 1x sur 3 jours (6 h, 10 %) ; fenêtre courte ≈ 1/12 de la longue — [Google SRE Workbook, Alerting on SLOs, tableau 5-8](https://sre.google/workbook/alerting-on-slos/) [V]
- Argo Rollouts : failureLimit (défaut 0) = nombre max de mesures en échec avant échec de l'analyse ; count/interval ; une analyse en échec abort le canari, remet le poids à zéro, statut Degraded ; analyse « inconclusive » met le déploiement en pause jusqu'à décision humaine — [Argo Rollouts, Analysis](https://argo-rollouts.readthedocs.io/en/stable/features/analysis/) [V]
- Flagger : stepWeight/maxWeight ; threshold = nombre d'échecs de vérification avant rollback ; durée de promotion ≈ interval·(maxWeight/stepWeight), de rollback ≈ interval·threshold ; avancement suspendu tant qu'une vérification personnalisée échoue — [Flagger, How it works](https://fluxcd.io/flagger/usage/how-it-works/) [V via extraits de recherche]
- Croissance de fiabilité logicielle : Goel & Okumoto, « Time-dependent error-detection rate model for software reliability and other performance measures », IEEE Trans. Reliability R-28(3):206-211, 1979, doi:10.1109/TR.1979.5220566 (NHPP) — [Scilit](https://scilit.com/publications/a0ef8d84616bdb7c34ba257dbd33ef3a) [V sur citation ; contenu non lu]. Un index donne des pages 465-484 (conflit, non retenu).

### Inferences
- [I] Traduction SRE : définir un SLO d'autonomie (ex. 99 % de tâches sans incident par mois) ; budget d'erreur mensuel = 1 % des tâches ; budget épuisé => rétrogradation automatique d'un palier ; burn rate 14,4x sur courte fenêtre => suspension immédiate (révocation rapide), 1x sur 3 jours => revue. Avec 216 tâches/5 semaines (~43/semaine), un SLO à 99 % donne un budget < 2 incidents sur 216 : les fenêtres SRE doivent s'exprimer en nombre de tâches, pas en heures (trafic trop faible pour les seuils de minutes).
- [I] Canari = palier d'autonomie : périmètre réduit (X % de tâches ou clients, ou classe de tâches), failureLimit=0 sur la classe grave, failureLimit>0 sur la classe mineure, état « inconclusif => pause humaine » = notre « incertain => n'étend pas ».
- [I] SRGM (Goel-Okumoto) : hypothèse de correction des défauts (le taux d'échec décroît dans le temps parce qu'on corrige) : inapplicable tel quel quand la config change souvent (chaque changement ré-injecte des défauts) ; utile pour décider « a-t-on cessé de trouver des défauts ? » (courbe cumulée qui s'aplatit) [I].
- [I] Crédit : les banques augmentent les limites sur un historique de paiement, un profil de risque et des paliers, révocables ; analogie de palier + probation + révision périodique — AUCUNE source vérifiée.

### Gaps
- Politiques d'augmentation de limite de crédit : aucune source fiable trouvée ou consultée (aucune réf. citée).
- Documentation officielle Flagger lue seulement via extraits de recherche ; Argo `inconclusiveLimit`/`consecutiveErrorLimit` non couverts par la page lue.
- Pas de papier trouvé appliquant SPRT/CUSUM/budget d'erreur à l'autonomie d'agents IA ; l'analogie SRE est une inférence.

## Synthèse opérationnelle (inférences, à valider par le rédacteur)
1. Promotion palier bas : ≥45-59 tâches propres de la classe, même config (CP unilatéral 90-95 %, p<5 %) ; palier moyen ≈ 300 ; palier haut : mutualisation ou périmètre borné.
2. Séquentiel : SPRT (p0 vs p1, α=β=5 %) pour décider tôt ; ex. 2 % vs 10 % => 35 succès d'affilée acceptent ; un échec = +1,609, soit environ 19 succès annulés.
3. Révocation : CUSUM ou budget d'erreur avec burn rate ; condition « incident grave unique => rétrogradation immédiate + revue », pas de test statistique (la borne CP après 1 échec/83 est de toute façon 5,6 %).
4. Changement de config : preuve escomptée par w (0 à 1) selon le type ; échecs transférés à w=1 ; phase de probation en canari.
5. Quasi-accidents : preuve de la barrière, pas de l'agent.
6. Hypothèses à surveiller : indépendance (grappes par client), stationnarité (dérive de modèle, de population), mesure (qui détecte les incidents ? incidents non détectés => bornes optimistes).
