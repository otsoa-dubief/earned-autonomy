# Cellules portées par une seule tâche : bornes exactes, surdispersion, mise en commun bayésienne, regroupement et seuils d'information minimale

Notes de recherche, 07/11/2026. Exemple de référence : une seule tâche porteuse, 1 erreur déléguée sur 60 écritures (1,67 pour 100), budget faible 0,5 pour 100 (0,005 par écriture). Budgets moyen et fort : 0,05 et 0,005 pour 100.
Trois marques séparent la provenance : **[Source]** (lien), **Calcul personnel** (script `scipy` lancé dans le `.venv` du dépôt, en lecture seule ; hypothèses dites à chaque fois), **Déduit** (raisonnement à partir des sources ou du code). Ce qui n'a pas été trouvé est dans « Gaps ».

## 1. Bornes exactes ou prudentes au niveau des grappes : avec n_eff = 1, 2, 3 ou 5 tâches, une borne basse unilatérale à 95 % peut-elle dépasser 0,5 pour 100 ?

### Takeaway
Avec 1 erreur sur 60 écritures dans une seule tâche, aucune borne valide ne dépasse le budget faible, pas même la borne exacte qui suppose des écritures indépendantes (0,086 pour 100). La règle de repli actuelle (« estimation > budget ») est plus libérale que toutes les méthodes examinées. Mais aux niveaux moyen et fort, une borne sans aucune hypothèse sur le groupement des erreurs (inégalité de Markov) peut établir un dépassement à partir d'une seule tâche, cellule par cellule, avant correction de multiplicité. Il faut donc distinguer le budget faible, où rien de valide ne peut conclure, des niveaux moyen et fort, où une borne exacte garde un peu de puissance.

### Cited Findings
- **Règle actuelle.** Le plan écrit : « Une cellule dont l'écart type bootstrap est nul (aucune variation entre répétitions) n'entre pas dans le maximum ; son dépassement n'est établi que si son estimation dépasse le budget. » — [PLAN_EXPERIENCE.md, 5.14, point 2](ROOT/PLAN_EXPERIENCE.md). Le code fait exactement cela : `var = sd > 0`, `borne = est − c*·sd` pour les cellules qui varient, `etabli = est > bud` sinon — [simulation/rejeu/maxt.py](ROOT/simulation/rejeu/maxt.py).
- **Le bootstrap ne mesure rien avec une tâche.** Le rapport du contrôle 3 dit que le bootstrap « est plat, ou ne varie que par les ordres et le validateur ». Dans la répétition 24 du monde V, les 11 cellules jugées n'ont qu'une tâche porteuse, l'écart type est nul partout, c* n'est pas calculable, et 10 cellules valent 1,9 à 3,8 fois le budget : d'où un faux R1 — [RAPPORT.md, 9.3 point 5 et 10.7](ROOT/simulation/controle3/RAPPORT.md).
- **Ce que le plan admet déjà comme preuve.** Pour les preuves à 95 %, la taille effective à ρ = 1, (Σm)² ÷ Σm², « c'est la seule valeur valable sans hypothèse sur la corrélation » ; les erreurs sont ramenées à x_eff = x × n_eff ÷ n et les bornes se lisent sur une loi bêta à effectifs non entiers — [PLAN_EXPERIENCE.md, 5.13](ROOT/PLAN_EXPERIENCE.md). La section 8 tranche : bornes « calculées sur la taille effective ou au niveau des tâches, jamais sur les écritures brutes » — [PLAN_EXPERIENCE.md, section 8](ROOT/PLAN_EXPERIENCE.md).
- **Korn et Graubard (1998)** adaptent l'intervalle exact binomial (Clopper-Pearson) aux données d'enquête en remplaçant n par la taille effective n ÷ effet de plan (Kish, 1965) — [Statistique Canada, Survey Methodology 12-001-X19980024356](https://www150.statcan.gc.ca/n1/en/catalogue/12-001-X19980024356). La version utilisée par le NCHS corrige aussi par les degrés de liberté : n*_df = [p(1 − p) ÷ var(p)] × (t_{n−1}(1 − α/2) ÷ t_df(1 − α/2))², où df est la différence entre le nombre d'unités primaires et le nombre de strates ; puis x = n*_df × p et bornes par la loi F — [Ward 2019, Stata Journal, manuscrit HHS](https://stacks.cdc.gov/view/cdc/83564/cdc_83564_DS1.pdf).
- Ward rappelle que « the Korn-Graubard CI is known to be conservative (Brown, Cai, and DasGupta, 2001; Gray et al., 2004) » — [Ward 2019](https://stacks.cdc.gov/view/cdc/83564/cdc_83564_DS1.pdf). Brown, Cai et DasGupta recommandent l'intervalle de Wilson ou celui de Jeffreys à queues égales pour les petits n, et celui d'Agresti-Coull pour les n plus grands — [Statistical Science 16(2), 2001](https://projecteuclid.org/euclid.ss/1009213286).
- **Une strate à une seule unité n'a pas de variance.** Stata : « there is insufficient information to compute an estimate of that stratum's variance » ; le réglage par défaut `singleunit(missing)` « results in missing values for the standard errors » — [FAQ Stata](https://stata.com/support/faqs/statistics/standard-error-because-of-stratum).
- **Peu de grappes « traitées » : l'inférence par grappes échoue.** Selon le résumé de MacKinnon et Webb (2018), tel que rapporté par la recherche, l'inférence par la loi de Student comme par le bootstrap sauvage par grappes est connue pour échouer quand les grappes traitées sont très peu nombreuses — [Econometrics Journal 21(2), 114-135](https://econpapers.repec.org/RePEc:wly:emjrnl:v:21:y:2018:i:2:p:114-135). Dans un autre article des mêmes auteurs, le bootstrap sauvage marche bien en général, mais toutes les méthodes échouent gravement quand les grappes traitées sont peu nombreuses — [QED WP 1314](https://ageconsearch.umn.edu/record/274639/files/qed_wp_1314.pdf) (résumé lu par la recherche, texte non lu).
- Cameron, Gelbach et Miller (2008) : les tests asymptotiques usuels peuvent rejeter trop souvent avec peu de grappes (5 à 30) ; leurs procédures bootstrap-t par grappes ramènent le taux de rejet de 10 % au niveau nominal de 5 %, sur des exemples descendant jusqu'à cinq grappes — [NBER t0344](https://www.nber.org/papers/t0344).

### Inferences

**Ce que fait vraiment la règle actuelle (Déduit, du code de `maxt.py`).**
- Le défaut ne passe pas seulement par un écart type nul. Une cellule à une tâche dont le bootstrap ne varie que par les K ordres et le validateur a un écart type petit mais non nul : elle entre dans le maximum, et sa borne est l'estimation moins c* fois cet écart type minuscule. Elle est donc « établie » dès que l'estimation dépasse un peu le budget. Un amendement doit porter sur le **nombre de tâches porteuses**, pas sur « écart type nul ».
- À l'inverse, un écart type nul peut survenir avec plusieurs tâches : l'estimateur Σx ÷ Σm ne varie pas si toutes les tâches porteuses ont exactement le même taux (par exemple deux tâches à 1 erreur sur 30). C'est rare, mais le repli actuel y établirait aussi le dépassement sans mesure d'incertitude.
- Point de mise en œuvre : `decision.cellules` compte les porteuses sur le jeu principal et sur la seconde famille quand elle existe (`jeux = [jeu] + [autres[cle].jeu]`). Le seuil devrait compter les tâches distinctes du cadre de rééchantillonnage qui produit `q.boot`, pour que la règle et le bootstrap parlent des mêmes tâches.

**Décision pour 1 erreur sur 60 écritures, une seule tâche (Calcul personnel).**
Les seuils de Markov supposent une tâche tirée au hasard, un taux par tâche positif ou nul et une grandeur égale à la moyenne des taux par tâche. La bêta-binomiale « à ρ connu » teste « au moins une erreur » dans une grappe de 60 écritures.

| Méthode | Borne basse ou p-valeur (faible) | Établi au faible ? | Au moyen ? | Au fort ? |
|---|---|---|---|---|
| Règle actuelle (repli ponctuel) | estimation 1,67/100 | oui | oui | oui |
| Clopper-Pearson, écritures indépendantes (ρ = 0) | 0,086/100 ; p = 0,26 | non | oui (0,086 > 0,05) | oui |
| Clopper-Pearson sur n_eff à ρ̂ = 0,05 ; 0,1 ; 0,2 (Kish) | n_eff = 15,2 ; 8,7 ; 4,7 ; borne ≈ 0 ; p = 0,57 ; 0,68 ; 0,78 | non | non | non |
| Clopper-Pearson sur n_eff à ρ = 1 (formule du plan) | n_eff = 1, x_eff = 0,017 ; borne ≈ 0 ; p = 0,93 | non | non | non |
| Bêta-binomiale exacte, ρ supposé connu | p = 0,26 (ρ = 0) ; 0,13 (0,05) ; 0,09 (0,1) ; 0,056 (0,2) ; 0,040 (0,3) ; 0,023 (0,5) | oui si ρ ≥ 0,25 environ | oui (p ≤ 0,030 pour tout ρ) | oui (p ≤ 0,003) |
| Bêta-binomiale robuste (pire ρ) | p = 0,26 (atteint à ρ = 0) | non | oui (0,030) | oui (0,003) |
| Markov, sans hypothèse | borne α × y = 0,083/100 ; p = budget ÷ y = 0,30 | non | oui (p = 0,03) | oui (p = 0,003) |
| Markov après Bonferroni sur les 11 cellules de la même tâche | il faudrait y ≥ 110 % | non | non (il faudrait y ≥ 11 %) | oui (il faudrait y ≥ 1,1 %) |
| Markov après Bonferroni sur 180 cellules | — | non | non (y ≥ 180 %) | non (y ≥ 18 %) |
| Quasi-vraisemblance | dispersion φ̂ = χ² ÷ (G − p) à 0 degré de liberté | non calculable | non calculable | non calculable |

- La borne exacte qui suppose les écritures indépendantes est la plus libérale des méthodes valides au faible. Elle ne conclut pas avec 1 erreur, mais conclut avec 2 erreurs sur 60 (0,595/100). Le repli actuel conclut avec 1 : il est plus libéral que l'hypothèse la plus optimiste.
- Coïncidence utile : pour 1 erreur, la borne sans hypothèse d'une seule tâche (Markov, α × y = 0,083/100) est presque égale à la borne exacte sous indépendance (0,086/100).
- La borne du plan (Clopper-Pearson sur n_eff à ρ = 1) rejette moins que Markov à une tâche. Elle exige un taux d'au moins 61 % dans la tâche, contre 10 % pour Markov. Sa région de rejet est donc incluse dans celle de Markov, et son risque reste sous 5 % quel que soit le mécanisme de groupement (Déduit). C'est la formule déjà codée pour R4 (`classes.borne_basse`).

**Combien de tâches pour qu'une borne exacte puisse conclure ? (Calcul personnel ; ρ = 1, tâches de même taille, taux mis en commun minimal pour que la borne de Clopper-Pearson à 95 % unilatéral dépasse le budget.)**

| Tâches porteuses k | faible (0,5/100) | moyen (0,05/100) | fort (0,005/100) | Même calcul avec la correction de degrés de liberté de Korn-Graubard (df = k − 1, 60 écritures) : faible / moyen / fort |
|---|---|---|---|---|
| 1 | 60,9 % | 42,5 % | 32,4 % | non défini (df = 0) |
| 2 | 34,2 % | 23,0 % | 17,2 % | impossible même à 100 % (facteur 0,070) |
| 3 | 24,7 % | 16,2 % | 11,9 % | 61,8 / 43,2 / 32,9 % |
| 5 | 16,6 % | 10,5 % | 7,6 % | 24,2 / 15,9 / 11,7 % |
| 10 | 9,9 % | 5,9 % | 4,1 % | 11,4 / 6,9 / 4,8 % |
| 30 | 4,7 % | 2,5 % | 1,6 % | 4,8 / 2,5 / 1,65 % |

- Lecture : à ρ = 1, il faut au faible des taux de 9 fois le budget (30 tâches) à 120 fois (une tâche). Cela confirme ce que le plan déclare déjà : la borne à ρ = 1 ne sert pas à établir un dépassement de B-tout. Le max-T est bien plus puissant : sur 5 à 11 tâches porteuses, 10 R1 sur 120 à 1,05 fois le budget ([RAPPORT.md, 10.7 et 10.8](ROOT/simulation/controle3/RAPPORT.md)).

**Saut du bootstrap entre une et deux tâches (Calcul personnel ; k tâches de même taille, dont une seule porte des erreurs, k fixe, bruit des ordres ignoré).**
- Le nombre de copies de la tâche fautive dans une répétition suit une loi binomiale (k, 1/k). La borne de cette cellule seule vaut estimation × (1 − (q − 1)), où q est le 95e centile de cette loi.
- k = 2 ou 3 : q = 2, borne = 0. Pour k ≥ 5, q = 3, borne = −1 × l'estimation. Le maximum sur les cellules ne fait qu'augmenter c*.
- Donc, dès deux tâches, le max-T ne peut **jamais** établir un dépassement qui ne repose que sur une tâche fautive. À une tâche, la règle actuelle l'établit toujours si l'estimation dépasse le budget.
- L'option (b) rend le cas k = 1 cohérent avec k ≥ 2. Il n'existe que 3 répétitions distinctes à k = 2, 10 à k = 3 et 126 à k = 5. Une tâche absente d'une répétition l'est avec probabilité 0,25 (k = 2) à 0,36 (k = 30).

**La surdispersion pousse dans deux sens opposés selon la méthode (Calcul personnel et Déduit).**
- Avec l'effet de plan de Kish, la borne baisse quand ρ monte (n_eff s'effondre).
- Avec la loi bêta-binomiale exacte d'une seule grappe, la probabilité d'observer au moins une erreur sous l'hypothèse nulle baisse quand ρ monte : de 0,26 à ρ = 0 à 0,005 quand ρ tend vers 1. Le groupement concentre les erreurs dans peu de tâches, si bien qu'une tâche « touchée » devient rare.
- L'effet de plan est une approximation de variance, au second ordre, qui ne vaut pas pour les queues d'une seule grappe à événements rares.
- Conséquence : brancher un ρ̂ emprunté (environnement, autres modèles) dans un test exact bêta-binomial pourrait établir un dépassement au faible à partir d'une seule erreur (si ρ̂ ≥ 0,25 environ). Si le vrai ρ de la cellule est plus bas, c'est un faux R1.
- La version robuste (pire ρ) est valide dans la famille bêta-binomiale. Au faible, elle exige au moins 3 erreurs sur 60 (pire p : 0,26 pour 1 erreur, 0,068 pour 2, 0,038 pour 3, 0,017 pour 6).

**Ordre de grandeur du faux R1 avec la règle actuelle, au budget exact (Calcul personnel ; enveloppe haute : erreur déléguée dans assez d'ordres pour que l'estimation dépasse le budget).**
- Une tâche de m écritures au taux exact du budget faible porte au moins une erreur avec probabilité 1 − 0,995^m : 9,5 % pour m = 20, 26 % pour m = 60 (écritures indépendantes ; 9 % pour m = 60 à ρ = 0,1).
- Si une cellule à une tâche apparaît dans la moitié des répétitions, comme dans le monde A, un monde au seuil pourrait sortir un faux R1 dans 5 à 13 % des répétitions, au-dessus de la cible de 5 %. Déduit, non simulé.
- Coût de (b) en puissance, au faible, dans un monde à 5 fois le budget (2,5/100, 60 écritures, indépendance) :
  - règle actuelle : environ 78 % (mais avec le faux R1 ci-dessus) ;
  - bêta-binomiale robuste (au moins 3 erreurs) : environ 19 % ;
  - Markov (au moins 6 erreurs) : environ 0,5 % ;
  - Clopper-Pearson à ρ = 1 et (b) : environ 0 %.

**Insertion dans le max-T préenregistré (Déduit).**
- Les cellules à une tâche (ou à écart type nul) restent hors du maximum. Leur repli ponctuel est remplacé par un test exact écrit d'avance :
  - soit la borne de Clopper-Pearson sur n_eff à ρ = 1 (déjà codée, cohérente avec 5.13 et la section 8) ;
  - soit la borne de Markov (plus puissante au moyen et au fort, mais il faut écrire ses hypothèses : tirage, positivité, grandeur).
- Le risque global se garde par une répartition de type Bonferroni : par exemple le max-T à 4 % et les cellules exclues à 1 % partagé entre elles. Ou bien un total déclaré au plus 5 % + α', comme le plan le fait déjà pour la liste fixe (7,5 %).
- Au faible, la borne du plan ne conclut presque jamais à une tâche. En pratique, ce « repli exact » revient à (b), avec en plus la possibilité de conclure au fort sur une forte concentration d'erreurs.

**Synthèse par famille (Déduit et Calcul personnel).**

| Famille | 1/60, une tâche, faible | Insertion dans le max-T | À écrire avant les données | Risques principaux |
|---|---|---|---|---|
| Règle actuelle | établi | hors maximum, repli ponctuel | déjà écrite | faux R1 sans mesure d'incertitude ; enveloppe de 10 à 26 % par cellule au budget exact |
| (b) une seule tâche porteuse : rien d'établi, publiée avec mention | non établi | hors maximum | une phrase et la définition de « porteuse » ; à exprimer sur k, pas sur l'écart type nul | dépassement manqué, mais aucune méthode valide n'a de puissance utile au faible |
| (c) repli exact : Clopper-Pearson sur n_eff à ρ = 1 | non (taux ≥ 61 % requis) | branche exacte hors maximum, α' déclaré | faible : formule et code existants | ≈ (b) au faible ; couvre aussi l'écart type nul à plusieurs tâches |
| (c') repli exact : Markov | non (p = 0,30) | idem | faible, mais hypothèses à écrire | peut conclure au moyen ou au fort sur une seule tâche ; dépend de la grandeur (ratio ou moyenne par tâche) |
| Surdispersion avec ρ̂ emprunté | Kish : non ; bêta-binomiale exacte : oui si ρ̂ ≥ 0,25 environ | idem | moyen : source de ρ̂, cascade de repli | sens opposés selon la méthode ; faux R1 si ρ̂ trop haut pour la cellule |
| Bêta-binomiale robuste (pire ρ) | non ; au moins 3 erreurs sur 60 | idem | moyen | validité limitée à la famille bêta-binomiale |
| Bayes « vague » | « établi » par l'a priori seul (section 2) | hors cadre fréquentiste | — | décision dictée par l'a priori |
| Bayes empirique entre cellules | non, sauf si les autres cellules dépassent | hors cadre ; caractéristiques opératoires à simuler | élevé | masque un dommage local ; la décision dépend des autres cellules |
| Regroupement pour la variance seule, « centré » | non | estimation locale, variance empruntée | moyen à élevé (règles d'appariement) | ≈ (b) (section 3) |
| Regroupement de l'estimation | selon le voisin | nouvelle cellule dans le maximum | élevé | dilution, changement d'hypothèse et de budget |
| Seuil k ≥ 2 tâches porteuses | non établi | critère d'entrée dans le maximum | très faible | identique à (b) |
| Seuil n_eff × budget ≥ c | non établi | idem | faible, mais c arbitraire | exclut presque toutes les cellules au faible (section 4) |

### Gaps
- Je n'ai trouvé aucune source sur le max-T de Westfall et Young appliqué à des cellules dont la loi bootstrap est dégénérée (écart type nul ou quasi nul), ni de règle standard pour ce cas.
- Pas de source consultée sur la quasi-vraisemblance avec une seule grappe. L'impossibilité d'estimer φ à 0 degré de liberté est déduite de la formule usuelle, pas lue.
- La borne de Markov pour une seule grappe est un résultat élémentaire, que j'ai appliqué moi-même. Je n'ai pas trouvé de texte de référence qui l'utilise pour ce cas ; ses conditions (estimande ratio ou moyenne par tâche, taille des tâches variable) restent à écrire si elle est retenue.
- Le texte de Korn et Graubard (1998) n'a pas été lu en entier : leur comportement à df = 1 ou 2 n'est connu que par la formule rapportée par Ward (2019).
- Les mots exacts de Brown, Cai et DasGupta sur le caractère prudent de Clopper-Pearson n'ont pas été vérifiés dans l'article ; seul Ward (2019) les cite à ce sujet.

## 2. Mise en commun bayésienne ou bayésienne empirique entre cellules : quelle probabilité a posteriori de dépassement dans une cellule à une tâche ?

### Takeaway
Dans une cellule à une tâche, la probabilité a posteriori de dépassement est surtout celle de l'a priori. Un a priori « vague » donne déjà 0,955 (Jeffreys) à 0,995 (uniforme) avant toute donnée, donc une règle « probabilité > 0,95 » établirait un dépassement sans donnée. Un a priori empirique tiré des autres cellules dit au contraire « non établi », sauf si les autres cellules dépassent aussi. La pharmacovigilance assume ce rétrécissement, qui rabat volontairement les signaux isolés et rares. Mais c'est l'opposé de l'intention d'un critère éliminatoire, qui doit attraper un dommage local.

### Cited Findings
- **Berry et Berry (2004)** : modèle hiérarchique à trois niveaux (type d'événement indésirable, appareil, ensemble) qui emprunte de l'information entre types ; un médicament est plus probablement en cause quand le taux est élevé pour plusieurs types du même appareil que pour des types épars — [IDEAS/RePEc, Biometrics 60(2), 418-426](https://ideas.repec.org/a/bla/biomet/v60y2004i2p418-426.html) ; [MD Anderson, notice](https://mdanderson.elsevierpure.com/en/publications/accounting-for-multiplicities-in-assessing-drug-safety-a-three-le).
- **DuMouchel (1999), Gamma-Poisson Shrinker** : a priori mélange de deux lois gamma ; l'EBGM est une version rétrécie du rapport observé ÷ attendu ; les 5e et 95e centiles a posteriori (EB05, EB95) donnent des bornes de crédibilité unilatérales à 95 % ; la FDA a utilisé ce modèle (Szarfman et al., 2002) — [R Journal 2017, openEBGM](https://journal.r-project.org/archive/2017/RJ-2017-063). Le seuil « EB05 ≥ 2 » n'apparaît que sur un site de calculatrices, comme convention courante — [MetricGate](https://metricgate.com/docs/mgps-ebgm-gamma-poisson/) (source faible, non vérifiée).
- **Norén, Hopstadius et Bate (2011, Statistical Methods in Medical Research)** : les rapports observé ÷ attendu bruts sont sensibles aux fluctuations aléatoires pour les événements rares à faible effectif attendu ; le rétrécissement protège des associations factices — [notice Scilit](https://scilit.com/publications/99eca2586d9346be24e8f52bc885b843). Une transcription de cours décrit l'ajout d'un demi-rapport imaginaire à l'observé et à l'attendu, IC = log2((O + 0,5) ÷ (E + 0,5)) — [transcription, source secondaire](https://www.scribd.com/document/904350718/Transcript-Lesson-5).
- **Gelman et al., exemple des tumeurs du rat (BDA, chapitre 5)** : 70 expériences historiques, vraisemblance binomiale par expérience, a priori bêta commun, mise en commun partielle qui rétrécit chaque expérience vers la moyenne de population — [laboratoire AM207](https://am207.github.io/2018fall/wiki/hierlab.html) ; [exemple PyMC](https://molab.marimo.io/github/pymc-devs/pymc-examples/blob/main/examples/generalized_linear_models/GLM-hierarchical-binomial-model.ipynb). Hyper-a priori proposé dans le livre : proportionnel à (α + β)^(−5/2) — [vignette bang, section 5.3](https://vps.fmvz.usp.br/CRAN/web/packages/bang/vignettes/bang-b-hef-vignette.html). Le livre lui-même n'a pas été consulté.
- **Bayes empirique avec une unité par strate** : Mosaferi propose un estimateur bayésien empirique de variance pour un plan à une unité primaire par strate ; il « over-shrinks » vers la moyenne a priori, d'où une version contrainte ; en simulation, les deux battent l'estimateur à strates regroupées en erreur quadratique relative — [arXiv 1910.05840](https://arxiv.org/abs/1910.05840).
- **Emprunter la loi aux unités non traitées.** Conley et Taber (2011) : avec peu de groupes qui changent de politique, on ne peut pas estimer l'effet de façon convergente, mais on peut estimer la loi de l'estimateur à partir des nombreux groupes qui ne changent pas, et construire des intervalles par inversion de test — [NBER t0312](https://nber.org/papers/t0312) ; [Review of Economics and Statistics 93(1)](https://econpapers.repec.org/RePEc:tpr:restat:v:93:y:2011:i:1:p:113-125).
- **Règles de sécurité bayésiennes préenregistrées** (essais à un bras, taux d'événements élevés) : a priori Bêta(1, 4) et arrêt si la probabilité a posteriori que le taux dépasse 20 % atteint 85 %, avec des probabilités d'arrêt simulées d'environ 4 % à un taux de 10 % et 24 % à 20 % — [protocole NCT03692052](https://cdn.clinicaltrials.gov/large-docs/52/NCT03692052/Prot_000.pdf) ; a priori de Jeffreys et arrêt si P(taux > 0,30) ≥ 0,948 — [protocole NCT07489976](https://cdn.clinicaltrials.gov/large-docs/76/NCT07489976/Prot_000.pdf).
- Dans le plan, le modèle bêta-binomial hiérarchique est « descriptif seulement » — [PLAN_EXPERIENCE.md, section 8](ROOT/PLAN_EXPERIENCE.md).

### Inferences
**Probabilité de dépassement, cellule à une tâche, 1 erreur sur 60 (Calcul personnel).**

| A priori | Avant données | Après 1/60, écritures indépendantes | Après 1/60 ramené à ρ = 1 (n_eff = 1, x_eff = 1/60) |
|---|---|---|---|
| Uniforme Bêta(1, 1), budget faible | 0,995 | 0,962 | 0,991 |
| Jeffreys Bêta(½, ½), budget faible | 0,955 | 0,897 | 0,918 |
| Uniforme, budget moyen / fort | 0,9995 / 1,000 | 0,9996 / 1,000 | 0,999 / 0,9999 |
| Jeffreys, budget moyen / fort | 0,986 / 0,9955 | 0,996 / 0,9999 | 0,975 / 0,992 |

- Un a priori « non informatif » sur [0, 1] met presque toute sa masse au-dessus de 0,005. La règle « probabilité a posteriori > 0,95 » est franchie sans donnée sous Jeffreys au faible, et sous l'uniforme partout. Sous Jeffreys, observer 1 erreur sur 60 fait même *baisser* la probabilité (0,955 → 0,897).

**A priori bayésien empirique Bêta(μM, (1 − μ)M) tiré des autres cellules, budget faible (Calcul personnel).**

| Moyenne des autres cellules μ | Poids M (en écritures) | Avant données | Après 1/60, indépendance (moyenne a posteriori) | Après 1/60 à ρ = 1 |
|---|---|---|---|---|
| 0,1/100 (0,2 fois le budget) | 100 | 0,059 | 0,497 (0,69/100) | 0,068 |
| 0,1/100 | 1 000 | 0,007 | 0,031 (0,19/100) | 0,007 |
| 0,1/100 | 10 000 | 0,000 | 0,000 (0,11/100) | 0,000 |
| 0,25/100 (0,5 fois) | 100 | 0,154 | 0,563 | 0,164 |
| 0,25/100 | 1 000 | 0,075 | 0,157 | 0,076 |
| 0,5/100 (au budget) | 100 à 10 000 | 0,32 à 0,48 | 0,52 à 0,66 | 0,33 à 0,48 |

- À ρ = 1, la cellule n'apporte presque aucune information, et la probabilité a posteriori égale celle de l'a priori. La décision est alors celle des **autres** cellules.
- Risque de dépassement manqué : si l'aviation à enjeu faible est vraiment à 2 fois le budget alors que le reste est à 0,2 fois, une mise en commun forte (M = 1 000) laisse la probabilité à 0,03 après 1/60. Le dommage local est masqué. C'est exactement ce que fait Berry et Berry pour un événement isolé, mais c'est contraire à un critère éliminatoire « dans au moins une cellule ».
- **Sensibilité à l'a priori** : la probabilité passe de 0,03 à 0,50 selon M (100 ou 1 000), un paramètre que les données d'une seule tâche ne peuvent pas trancher.

**Insertion dans le max-T et pré-enregistrement (Déduit).**
- Une probabilité a posteriori n'a pas la garantie du max-T (risque global de 5 %). Pour la mêler aux autres cellules, il faudrait simuler ses caractéristiques opératoires, comme les protocoles cités le font. Cela fait une seconde machinerie, pour quelques cellules.
- On peut écrire d'avance une procédure bayésienne empirique : quelles cellules nourrissent l'a priori, quel estimateur (moments, maximum de vraisemblance bêta-binomiale), quel seuil. Les hyperparamètres viennent alors des données des autres cellules, et la décision dans la cellule à une tâche dépend de résultats obtenus ailleurs. Un dépassement réel dans une autre configuration « contamine » la cellule, et l'inverse.
- Un a priori fixé après avoir vu les données serait indéfendable ici : avec une seule tâche, le choix de l'a priori **est** la décision.
- Variante fréquentiste plus sobre, inspirée de Conley et Taber : emprunter aux autres environnements la dispersion des taux entre tâches pour construire la loi nulle de la cellule. Il faut alors supposer les environnements échangeables, et pour des événements rares la dispersion dépend du taux moyen. C'est une hypothèse forte, contestable pour l'aviation.
- Usage cohérent avec le plan : publier une estimation rétrécie de façon descriptive, sans effet sur l'étiquette.

### Gaps
- Efron (Bayes empirique, *Large-Scale Inference*) n'a pas été consulté ; aucune citation de lui ici.
- Pas de guide réglementaire consulté (FDA ou EMA) sur la fixation préalable des a priori.
- Aucune source trouvée qui chiffre la probabilité a posteriori de dépassement dans une cellule à une seule grappe, ni qui recommande un seuil a posteriori pour des taux de l'ordre de 10⁻³ à 10⁻⁵.
- Les textes complets de Berry et Berry (2004) et de DuMouchel (1999) n'ont pas été lus ; le seuil EB05 ≥ 2 n'est pas vérifié à la source.

## 3. Fusion ou regroupement de cellules creuses : quand est-ce prudent, quand cela dilue-t-il un dommage local ?

### Takeaway
En sondage, une strate à une seule unité primaire n'a pas de variance estimable. Les logiciels refusent par défaut : erreur dans R, écart type manquant dans Stata. Traiter cette unité comme sans variance est réservé aux unités tirées avec certitude, ce que n'est pas une tâche d'un jeu rééchantillonné. L'option prudente, centrer sur la moyenne générale, rendrait ici tout dépassement impossible à établir : elle revient à (b). Regrouper n'aide que si l'on ajoute des tâches distinctes. Regrouper les scénarios avec leur configuration n'ajoute rien (même tâche). Regrouper deux niveaux ou deux environnements change l'hypothèse et dilue le dommage local.

### Cited Findings
- **R, paquet `survey`** : par défaut `options(survey.lonely.psu="fail")`, il est « an error to have a stratum with a single, non-certainty PSU » ; avec `remove` ou `certainty`, la strate « makes no contribution to the variance » ; `adjust` centre la strate sur la moyenne générale : « This is conservative » ; `average` prend la moyenne des strates à plusieurs unités et « might be appropriate if the lonely PSUs were due to data missing at random » ; « The best adjustment is probably to combine the single-PSU stratum with another well-chosen stratum » — [T. Lumley, Lonely PSUs](https://faculty.washington.edu/tlumley/old-survey/exmample-lonely.html). L'aide de `svyCprod` ajoute, selon la recherche, qu'il vaudrait souvent mieux regrouper les strates « de façon intelligente » et que les propriétés de `average` n'ont pas été étudiées à fond — [svyCprod](https://search.r-project.org/CRAN/refmans/survey/html/svyCprod.html).
- **Stata** : `certainty` fait que ces strates « contribute nothing to the standard error » ; `scaled` utilise « the average of the variances from the strata with multiple sampling units » ; `centered` centre « at the grand mean instead of the stratum mean » ; première solution conseillée : réaffecter la strate isolée à une autre strate bien choisie ; « You can decide how to specify singleunit() based on your analysis assumption » — [FAQ Stata](https://stata.com/support/faqs/statistics/standard-error-because-of-stratum). Des utilisateurs de Statalist décrivent `centered` comme l'option la plus prudente (plus grands écarts types) — [Statalist, 2011](https://stata.com/statalist/archive/2011-12/msg00397.html) (avis de forum).
- **Estimateur à strates regroupées** : il « is not design-unbiased » et « the bias increases as the population means of the pseudo-strata become more variant » ; il « may suffer from a large mean squared error » — [Mosaferi, arXiv 2110.10296](https://arxiv.org/abs/2110.10296) (version 2 retirée ; version finale annoncée : arXiv 2603.03569) ; même constat dans [arXiv 1910.05840](https://arxiv.org/abs/1910.05840).
- **Contexte du plan** : la même tâche porte la cellule de configuration et une dizaine de cellules de scénario de changement de modèle — [RAPPORT.md, 10.7](ROOT/simulation/controle3/RAPPORT.md).

### Inferences
- **Correspondance (Déduit).**
  - La règle actuelle équivaut à `certainty`/`remove` : variance nulle et décision sur la seule estimation.
  - (b) équivaut au défaut de Stata (`missing` : pas d'écart type, donc pas d'inférence) ou de R (`fail`).
  - Les deux logiciels réservent la variance nulle aux unités tirées avec certitude. Or la tâche porteuse est un tirage de la réserve, pas une unité certaine.
- **« Centré » (`adjust`/`centered`) transposé (Déduit).**
  - L'écart de la tâche est mesuré par rapport au taux de l'ensemble : écart type ≈ |y − ȳ|. La borne y − c* × |y − ȳ| tombe sous ȳ dès que c* ≥ 1.
  - Si l'ensemble est sous le budget, aucun dépassement n'est établi. En pratique, c'est (b).
- **« Moyenne » ou « mis à l'échelle » transposé (Déduit).**
  - Emprunter la variance moyenne des autres cellules n'est pas garanti prudent pour des événements rares : la variance entre tâches croît avec le taux.
  - Emprunter à des cellules plus propres sous-estime l'incertitude, d'où des faux R1 ; emprunter à des cellules plus sales la surestime.
  - Il faudrait un modèle d'échelle (coefficient de variation commun), écrit d'avance et contestable.
- **Regrouper les scénarios avec leur configuration (Déduit).** C'est la même tâche porteuse : on n'ajoute aucune grappe, donc aucune information sur la variation entre tâches. Ce n'est pas un remède.
- **Regrouper le niveau faible de l'aviation avec le niveau moyen (Déduit).**
  - Les budgets diffèrent d'un facteur 10. Un test commun en « fois le budget » pèse chaque erreur à enjeu moyen 10 fois plus.
  - Il peut donc noyer un vrai dépassement local à enjeu faible, ou faire porter au niveau faible un dépassement venu du moyen.
  - La conclusion change de nature : « B-tout dépasse sur faible ∪ moyen ». Et le niveau moyen de l'aviation est peut-être creux lui aussi.
- **Regrouper les environnements à même niveau (Déduit).** Cela redéfinit la cellule (l'environnement fait partie de la configuration) et dilue par construction un dommage propre à l'aviation. C'est contraire au but d'un critère éliminatoire « dans au moins une cellule ».
- **Quand le regroupement est prudent (Déduit).** Seulement s'il sert à la *variance* et que l'estimation reste locale, dans la variante centrée. Il dilue dès que l'*estimation* est mise en commun.
- **Coût de spécification (Déduit).** Il faut écrire d'avance quelle cellule s'apparie à quelle autre, dans quel ordre de repli, et sur quelle échelle. Cela fait beaucoup de choix pour un cas qui touche une poignée de cellules d'un seul environnement.

### Gaps
- Le texte original de Rust et Kalton (1987, Journal of Official Statistics) n'a pas été trouvé. Selon des articles qui le citent, un regroupement plus fort serait préférable quand peu d'unités primaires sont tirées, mais je n'ai pas pu rattacher ce résumé à une source précise : non retenu comme fait.
- Wolter (2007) n'a pas été consulté. Le sens du biais de l'estimateur à strates regroupées (classiquement vers le haut, donc prudent) n'est pas vérifié ici. Les sources lues disent seulement « non sans biais », avec un biais qui croît avec l'écart des moyennes.

## 4. Seuils d'information minimale : nombre minimal de tâches porteuses, ou compte attendu au budget ?

### Takeaway
Les praticiens écrivent d'avance des seuils simples :
- au moins 3 cas (PRR de l'agence britannique ; EudraVigilance pour les substances sous surveillance renforcée), ou 5 cas (autres substances) ;
- au moins 2 unités primaires par strate pour qu'une variance existe ;
- au moins 30 en taille réelle et en taille effective pour publier une proportion (NCHS), avec un examen au cas par cas sous 8 degrés de liberté.

Pour un test de dépassement, un critère qui ne regarde pas les erreurs, la p-valeur minimale atteignable (Tarone, 1990), classe d'avance une cellule à une tâche au budget faible comme « non testable » dès que la famille compte 11 tests ou plus. Le seuil le plus simple et le mieux fondé ici est k ≥ 2 tâches porteuses distinctes pour entrer dans le max-T. Un seuil de compte attendu (n_eff × budget ≥ c) exclurait presque toutes les cellules au faible.

### Cited Findings
- **Evans, Waller et Davis (2001)** : critères minimaux d'un signal dans la base britannique Yellow Card : au moins 3 cas, PRR ≥ 2, χ² ≥ 4 — [LSHTM Research Online](https://researchonline.lshtm.ac.uk/id/eprint/18379) ; [doi 10.1002/pds.677](https://doi.org/10.1002/pds.677) (résumé et sources secondaires ; texte complet non lu).
- **EudraVigilance (EMA)** : un signal de disproportion est levé si, « in at least one macro region », la borne basse de l'intervalle à 95 % du ROR « is greater than one » et le nombre de cas est au moins 3 pour les substances sous surveillance renforcée, au moins 5 pour les autres — [Candore et al., Drug Safety 2021-2022, PMC8763735](https://pmc.ncbi.nlm.nih.gov/articles/PMC8763735).
- Selon une source secondaire, un seuil de 5 cas au lieu de 3 réduit de 25 % les faux signaux et fait perdre 12 % des vrais signaux détectés tôt — étude citée sous le titre « Choosing thresholds for statistical signal detection with the proportional reporting ratio » (Slattery et al., 2013) — [notice QxMD](https://read.qxmd.com/read/23754759/choosing-thresholds-for-statistical-signal-detection-with-the-proportional-reporting-ratio) (résumé non lu : accès bloqué ; chiffre non vérifié).
- **NCHS (normes de présentation des proportions, 2017)** : une proportion est jugée non fiable et n'est pas présentée si « (a) n<30 or n*<30, (b) the absolute width of its Korn-Graubard CI is ≥0.30, or (c) its absolute CI width is >0.05 and <0.30, and its relative CI width is >130% » ; un examen statistique est requis quand la largeur absolue est ≤ 0,05 et « df<8 » — [Ward 2019](https://stacks.cdc.gov/view/cdc/83564/cdc_83564_DS1.pdf).
- **Tarone (1990)** : pour des statistiques discrètes, une hypothèse dont la p-valeur minimale atteignable dépasse le seuil de Bonferroni ne peut jamais être rejetée ; on la retire du compte des tests, ce qui rend la procédure plus puissante que Bonferroni — [diapositives K. Borgwardt](https://www.biochem.mpg.de/8406871/KBorgwardt_UniBasel_20160421.pdf) ; [Zhu et Guo, arXiv 1711.08147](https://arxiv.org/pdf/1711.08147). Hommel et Krummenauer (1998) ont noté que la procédure n'est pas monotone en α ; Roth en a donné une version monotone — même source.
- **Peu de grappes** : rejets excessifs entre 5 et 30 grappes avec les méthodes usuelles ; procédures bootstrap-t par grappes au niveau nominal dans des exemples à partir de 5 grappes — [Cameron, Gelbach et Miller, NBER t0344](https://www.nber.org/papers/t0344).
- **Dans le plan** : « fragile » sous 30 tâches porteuses (seuil tiré de la recherche du 05/11 : « de 5 à 30 grappes, l'inférence groupée devient peu fiable ») ; un type est « jugeable » si n_eff × barre ≥ ln 2 ≈ 0,69 — [PLAN_EXPERIENCE.md, 5.13, 5.14 et section 8](ROOT/PLAN_EXPERIENCE.md). Mesure du projet : sur des cellules de 5 à 11 tâches porteuses, 0 R1 sur 120 au seuil exact et 10 sur 120 à 1,05 fois le budget — [RAPPORT.md, 10.7 et 10.8](ROOT/simulation/controle3/RAPPORT.md).

### Inferences
- **Rétrécissement et compte minimal implicite (Calcul personnel ; formule IC de la source secondaire, intervalle de crédibilité par les quantiles de Gamma(O + 0,5, E + 0,5)).**
  - IC025 vaut −2,21 pour 1 rapport et −0,27 pour 2 rapports, même avec un attendu nul : jamais de signal.
  - Avec 3 rapports, IC025 vaut +0,76 si l'attendu est nul, et +0,08 si l'attendu est 0,3.
  - Le +0,5 impose donc de lui-même au moins 3 rapports, comme la règle des 3 cas.
- **Tarone appliqué aux cellules (Calcul personnel).**
  - À une tâche, la p-valeur minimale atteignable de la borne du plan (toutes les écritures fautives) vaut le budget : 0,005 au faible, 0,0005 au moyen, 0,00005 au fort.
  - Avec α ÷ K, la cellule faible est non testable dès K ≥ 11 (0,05 ÷ 11 = 0,0045), la cellule moyenne dès K > 100, la cellule forte dès K > 1 000.
  - À deux tâches, le minimum tombe à 0,000025 au faible : la cellule redevient testable.
  - Ce critère ne dépend que du plan des données (tâches et écritures), pas des erreurs. On peut donc l'écrire avant les données sans gonfler le risque.
- **Candidats pour un seuil sur k, le nombre de tâches porteuses distinctes (Déduit).**
  - **k ≥ 2** est le minimum pour qu'une variance entre tâches existe (règle des deux unités par strate). C'est aussi le point où le bootstrap se protège seul : dès k ≥ 2, une preuve qui ne repose que sur une tâche fautive ne peut pas être établie (section 1). Il corrige exactement le défaut, sans toucher aux autres cellules.
  - **k ≥ 5** s'appuie sur la plage mesurée par le projet (5 à 11 tâches tiennent le niveau) et sur la borne basse de Cameron, Gelbach et Miller. Il retirerait des cellules où le max-T semble fonctionner, donc de la puissance, sans preuve d'un défaut entre 2 et 4.
  - **k ≥ 30** est le seuil « fragile » actuel. L'appliquer à l'établissement retirerait presque toute l'aviation, la banque et le commerce du critère éliminatoire. Trop large.
- **Compte attendu au budget (Calcul personnel).**
  - À ρ = 1 et au faible, c = ln 2 demande n_eff ≥ 139 tâches effectives, et c = 3 en demande 600. Presque aucune cellule ne passerait.
  - Sur les écritures brutes (n × budget ≥ c), il faut 139 écritures (c = 0,69) ou 600 (c = 3). Cela exclut les cellules à une tâche (20 à 60 écritures), mais aussi beaucoup de cellules à plusieurs tâches.
  - Le choix de c est arbitraire. Ce critère convient pour « jugeable » (preuve sous la barre), pas pour l'entrée dans le test de dépassement.
- **Règle « au moins 3 erreurs déléguées » façon pharmacovigilance (Calcul personnel et Déduit).**
  - Pour une grappe de 60 écritures au faible, le pire p bêta-binomial vaut 0,038 à 3 erreurs. Trois erreurs est donc à peu près le plus petit compte valide quel que soit ρ dans cette famille.
  - Mais un seuil en nombre ignore m : 3 sur 20 et 3 sur 60 ne pèsent pas pareil. Il ne règle pas non plus la multiplicité. C'est un filtre de détection, pas une preuve confirmatoire.
- **Formulation qui découle des sources (Déduit).** Le seuil doit porter sur k, compté dans le cadre de rééchantillonnage de la cellule, et non sur « écart type nul ». Pour les cellules d'écart type nul avec k ≥ 2 (taux identiques), le plus cohérent avec 5.13 est de remplacer le repli ponctuel par la borne exacte du plan.

### Gaps
- Aucune source trouvée sur un nombre minimal de grappes propre aux tests de dépassement d'un taux rare ; la plage 5 à 11 ne repose que sur la simulation du projet.
- La justification du seuil df < 8 du NCHS n'a pas été lue dans le rapport complet (Parker et al., 2017) ; seul le résumé de Ward (2019) l'a été.
- Pratique de la démonstration de fiabilité (essais à zéro défaillance, plans MIL-HDBK-781) non recherchée : le plan l'utilise déjà pour la preuve sous la barre (annexe A2), pas pour le dépassement.
- GRADE (« taille d'information optimale ») non consulté.

## 5. Données creuses en méta-analyse clinique et en pharmacovigilance : un seul événement ou une seule étude, corrections de continuité, règles de cas minimum

### Takeaway
La méta-analyse des événements rares s'éloigne de l'ajout d'une constante (0,5). Elle préfère les méthodes sans correction ou à correction mieux choisie : Mantel-Haenszel, Peto sous 1 % d'événements à bras équilibrés, modèles bayésiens. Elle recommande des analyses de sensibilité. La pharmacovigilance refuse explicitement de signaler sur un ou deux cas. Les deux traditions convergent : une observation isolée sert à alerter et à publier, pas à conclure. Or R1 est une conclusion confirmatoire et éliminatoire, qui devrait être au moins aussi exigeante qu'un filtre de détection.

### Cited Findings
- **Sweeting, Sutton et Lambert (2004)** : par simulation de méta-analyses creuses à bras de tailles inégales, ils comparent la correction constante à deux autres, l'une fondée sur l'inverse de la taille du bras opposé, l'autre sur une estimation empirique de l'effet commun ; les deux autres battent la correction constante dans presque tous les cas ; la méthode de l'inverse de la variance se comporte mal quelle que soit la correction ; un modèle bayésien à effet fixe couvre bien ; ils conseillent une analyse de sensibilité à plusieurs méthodes et corrections — [notice Scilit, Statistics in Medicine 23:1351-1375](https://www.scilit.net/publications/3720c7fc026071ca01bb8288ed27115b) ; erratum : [UKHSA](https://researchportal.ukhsa.gov.uk/en/publications/erratum-what-to-add-to-nothing-use-and-avoidance-of-continuity-co/).
- Kuss (2014) soutient que les méthodes qui écartent les études à double zéro ou qui utilisent des corrections de continuité ne devraient plus être employées — [notice Zendy, Statistics in Medicine](https://zendy.io/title/10.1002/sim.6383).
- **Bradburn, Deeks, Berlin et Localio (2007)** : 12 méthodes comparées par simulation ; la plupart sont biaisées quand les données sont creuses ; le biais est le plus fort pour l'inverse de la variance et DerSimonian-Laird (rapport de cotes et différence de risques) ; sous 1 % d'événements, la méthode de Peto est la moins biaisée et la plus puissante, avec des bras équilibrés et des effets modérés — [University of Birmingham, notice](https://research.birmingham.ac.uk/en/publications/much-ado-about-nothing-a-comparison-of-the-perfomance-of-meta-ana/) (Statistics in Medicine 26(1):53-77).
- **Pharmacovigilance** : au moins 3 cas (Evans et al., 2001) ; 3 ou 5 selon la surveillance (EMA) ; voir section 4. Une source secondaire explique que les trois conditions vont ensemble parce qu'un rapport élevé bâti sur un ou deux cas est le plus souvent du bruit — [CASRAI](https://www.casrai.org/guides/signal-detection-in-pharmacovigilance) ou [MetricGate](https://metricgate.com/docs/proportional-reporting-ratio-prr/) (la recherche ne dit pas laquelle des deux ; sources secondaires, non lues).
- Rétrécissement des rapports observé ÷ attendu contre les associations factices des événements rares : [Norén et al., notice Scilit](https://scilit.com/publications/99eca2586d9346be24e8f52bc885b843) ; EBGM et EB05 : [R Journal 2017](https://journal.r-project.org/archive/2017/RJ-2017-063).

### Inferences
- **Correspondance (Déduit).**
  - Le repli actuel (estimation ponctuelle > budget, sans variance) est l'analogue d'un rapport observé ÷ attendu brut sans rétrécissement ni compte minimal, c'est-à-dire ce que la pharmacovigilance évite.
  - Avec 1 « cas » (une erreur, une tâche), aucune des règles citées ne lèverait de signal, même comme simple filtre.
- **Correction de continuité (Déduit).** Ajouter des pseudo-tâches ou des pseudo-écritures pour rendre le bootstrap non dégénéré serait une correction arbitraire, de la famille de la constante 0,5 critiquée par Sweeting et al. et par Kuss. À écarter.
- **Une seule étude (Déduit).**
  - La méta-analyse ne sait pas estimer l'hétérogénéité avec une étude.
  - De même, une cellule à une tâche ne permet pas d'estimer la variation entre tâches. Les sources lues ne proposent pas de l'inventer : elles recommandent des méthodes sans correction, des modèles qui empruntent (bayésiens) ou la sensibilité.
  - Transposé : publier l'estimation et la mention, éventuellement une analyse de sensibilité (la borne sous indépendance, 0,086/100, et la borne à ρ = 1), sans effet sur l'étiquette. C'est l'esprit de l'option (b).
- **Niveau de preuve (Déduit).** Les seuils de pharmacovigilance (3 ou 5 cas, borne basse > 1) sont des filtres de détection qui ouvrent une enquête. R1 clôt une question. Un critère confirmatoire ne devrait pas être plus permissif qu'un filtre de détection, alors que le repli actuel l'est.

### Gaps
- La façon dont Cochrane ou GRADE traitent une méta-analyse réduite à une seule étude ou à un seul événement n'a pas été vérifiée dans le manuel.
- Les textes complets de Sweeting et al. (2004) et de Bradburn et al. (2007) n'ont pas été lus ; seuls leurs résumés et notices l'ont été.
- Aucune source trouvée sur l'usage, en pharmacovigilance, d'un cas unique comme preuve confirmatoire. L'idée qu'un cas unique ne vaut que comme alerte est déduite des seuils, pas lue.
