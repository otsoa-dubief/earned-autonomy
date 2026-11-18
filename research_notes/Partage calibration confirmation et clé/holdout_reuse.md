# « Utilisé une seule fois » : réutilisation de holdout, essais répétés, jeux de test privés, préenregistrement, rejeu hors ligne

Date de la recherche : 5 novembre 2026. Recherche web uniquement (13 pages lues ou résumées via l'outil de fetch, qui passe par un petit modèle de résumé ; plusieurs PDF n'ont pas pu être lus, voir les Gaps). Les citations « entre guillemets » sont des extraits de pages ou des paraphrases fidèles du fetch ; je les marque comme telles.

## Q1. Théorie du surapprentissage adaptatif : le danger est-il l'analyse répétée (choix informés par les regards précédents) plutôt que la génération répétée de données ? Que protège « utiliser le test une fois » ?

### Takeaway
Dans la littérature (Dwork et al., Blum & Hardt), le danger formel est l'adaptativité : le choix des hypothèses ou des analyses dépend de résultats antérieurs obtenus sur le même holdout. Un holdout est une estimation valide pour un ensemble d'hypothèses fixé indépendamment de lui, même nombreuses. « Une seule fois » protège donc contre une boucle de rétroaction (regarder, ajuster, regarder), pas contre le nombre de lignes de données issues de lui.

### Cited Findings
- Dwork et al. : l'analyse classique suppose la procédure fixée avant de voir les données ; en pratique l'analyse est adaptative, les nouvelles analyses étant générées à partir de l'exploration et des résultats d'analyses précédentes sur les mêmes données. — [Penn / Roth, page du projet](https://cis.upenn.edu/~aaroth/reusable.html), [arXiv 1506.02629](https://arxiv.org/pdf/1506.02629)
- Selon le texte ar5iv (lu via fetch résumé) : les méthodes de holdout statique échouent « if the choice of hypotheses depends on previous analyses performed on the dataset » ; cette dépendance « invalidates the generalization guarantees ... potentially leading to overfitting ». Si l'ensemble des hypothèses testées est connu et indépendant du holdout, la correction de tests multiples est simple. — [Dwork et al., ar5iv](https://ar5iv.labs.arxiv.org/html/1506.02629)
- Même source : « Reusing a holdout set adaptively multiple times can easily lead to overfitting to the holdout set itself. » Le mot clé est « adaptively ». — [ar5iv 1506.02629](https://ar5iv.labs.arxiv.org/html/1506.02629)
- Mécanisme proposé (Thresholdout) : l'analyste utilise librement le jeu d'entraînement ; le holdout n'est accessible que via un algorithme différentiellement privé. Un budget de surapprentissage B décroît chaque fois que l'estimation d'entraînement et celle du holdout divergent au-delà d'un seuil ; une fois épuisé, l'algorithme cesse de répondre. Le nombre de requêtes adaptatives peut être exponentiel en n si B reste sous-quadratique ; le coût en échantillon est de l'ordre de celui de m requêtes non adaptatives (Théorème 25, d'après le fetch). — [ar5iv 1506.02629](https://ar5iv.labs.arxiv.org/html/1506.02629) ; résumé grand public : [Google Research blog](https://www.research.google/blog/the-reusable-holdout-preserving-validity-in-adaptive-data-analysis/) (le nombre d'usages croît en gros comme le carré de la taille du holdout, pour la version simple)
- Blum & Hardt (Ladder) : dans une compétition, le processus est séquentiel et adaptatif ; les participants peuvent tester des soumissions de façon répétée et « may begin to overfit to the holdout data ». Les remèdes habituels (limiter la précision ou le rythme de soumission) sont décrits comme des heuristiques mal comprises. — [arXiv 1502.04585](https://arxiv.org/abs/1502.04585)
- Recht et al. 2019 : en recréant de nouveaux jeux de test CIFAR-10 et ImageNet, les auteurs concluent que la baisse de précision (3 à 15 % sur CIFAR-10, 11 à 14 % sur ImageNet) n'est « not caused by adaptivity » mais par des images un peu plus difficiles / un décalage de distribution ; les gains sur l'ancien test se transfèrent, plus faibles. Ils alertent néanmoins sur « the danger of overfitting to excessively re-used test sets ». — [arXiv 1902.10811](https://arxiv.org/abs/1902.10811)
- Roelofs et al. 2019 (NeurIPS) : méta-analyse de plus de cent compétitions Kaggle, comparant classement public (holdout réutilisé) et classement final sur un jeu séparé ; « little evidence of substantial overfitting », résultat décrit comme « somewhat surprising », qui appuie la robustesse de la méthode holdout. — [NeurIPS 2019](https://papers.nips.cc/paper/9117-a-meta-analysis-of-overfitting-in-machine-learning)

### Inferences
- Lecture défendable de « passé une seule fois » : ce qui est protégé, c'est l'indépendance entre (a) les décisions de conception, de gel, de choix de seuils ou de verdict et (b) les résultats observés sur le jeu de confirmation. Ce n'est pas le nombre d'épisodes générés. Rien dans Dwork et al. ne dit que rejouer la même tâche donne un holdout « usé » ; l'usure vient de requêtes dont le choix dépend de réponses précédentes.
- Cependant, cette conclusion est une inférence : les papiers traitent des requêtes (statistiques calculées sur le holdout), pas de génération d'échantillons supplémentaires sur les mêmes items. La génération répétée devient un problème d'adaptativité seulement si elle est décidée en fonction de résultats vus (ex. rejouer plus de fois les tâches où le verdict déplaît, arrêt optionnel).
- Corollaire pour la règle : sont à interdire, sur le jeu de confirmation, toute analyse ou rejeu dont le résultat a pu influencer une modification de la règle, des seuils, du protocole, du choix des épisodes ou du nombre de rejeux. Sont autorisés : la génération des épisodes (jouer 50 fois) si le plan de jeu est fixé à l'avance et non conditionné aux résultats, et l'unique analyse finale.
- Le point de vigilance honnête : si les épisodes de confirmation sont consultés (scores, taux d'erreur) pendant leur génération pour décider de la suite, c'est de l'adaptativité même sans « analyse » formelle.

### Gaps
- Aucune source trouvée qui discute explicitement la génération répétée d'échantillons (essais multiples par item) comme forme de « réutilisation » au sens de Dwork. Le texte ne le dit ni ne l'exclut.
- Je n'ai pas pu lire le PDF de Dwork et al. en entier (fetch partiel : les 100 000 premiers caractères de la version ar5iv sur 152 739).

## Q2. Générer beaucoup d'épisodes sur les mêmes items (essais répétés, graines) : est-ce de la réutilisation ? Pratiques (pass@k, pass^k, graines) et rapport

### Takeaway
Les praticiens traitent les essais répétés d'une même tâche comme des mesures répétées de cette tâche, et la tâche comme l'unité d'analyse ; ce n'est pas présenté comme de la réutilisation du jeu de test. Le risque statistique est autre : la corrélation intra-tâche (pseudo-réplication), qui impose de découper par tâche et de ne pas compter les épisodes comme indépendants.

### Cited Findings
- τ-bench définit pass^k comme « the chance that all k i.i.d. task trials are successful, averaged across tasks », estimé par E_tâche[C(c,k)/C(n,k)] ; chaque tâche est jouée plusieurs fois (au moins 3 essais dans les résultats principaux), même consigne et même état initial de base ; la variation vient de l'échantillonnage des modèles (agent à température 0,0, utilisateur simulé à 1,0). La tâche est l'unité de moyenne ; pass^1 = récompense moyenne. — [τ-bench, ar5iv](https://ar5iv.labs.arxiv.org/html/2406.12045)
- Objectif de pass^k : évaluer la fiabilité sur plusieurs essais ; un seul succès peut être de la chance ; gpt-4o réussit moins de la moitié des tâches, avec pass^8 sous 25 % en retail. — [τ-bench, résumé arXiv](https://arxiv.org/abs/2406.12045)
- Cadre « Adding Error Bars to Evals » : les questions d'évaluation sont conçues comme tirées d'une super-population ; le fetch n'a pas permis de lire les passages sur le rééchantillonnage et les erreurs-types groupées. — [arXiv 2411.00640](https://arxiv.org/abs/2411.00640)
- Kaggle (compétitions) : plusieurs soumissions sont autorisées sur le split public, mais une sélection limitée (souvent 2) est rescorée sur le privé ; sources secondaires (forums, cours), pas les règles officielles. — voir Q3.

### Inferences
- Le partage par tâche (calibration vs confirmation) est cohérent avec la pratique : la tâche est l'unité, les 50 essais d'une tâche restent dans le même jeu. Ne jamais répartir les essais d'une même tâche entre calibration et confirmation (fuite de l'item).
- Les 50 épisodes d'une tâche ne sont pas 50 observations indépendantes : l'incertitude doit se calculer au niveau de la tâche (groupement/bootstrap par tâche). Inférence à partir de la définition de pass^k et du cadre « super-population », à confirmer par lecture du texte complet de Miller 2024.
- Pour la règle : « une seule fois » ne doit pas être lu comme « un seul essai par modèle ». Rien trouvé qui établisse cette lecture dans les benchmarks d'agents, où plusieurs essais par tâche sont la norme.

### Gaps
- Pas de source sur la manière dont SWE-bench ou d'autres benchmarks d'agents rapportent le nombre d'essais sur un jeu de test caché (non recherché en profondeur, non trouvé).
- Convention pass@k de Chen et al. (HumanEval) non vérifiée ici.

## Q3. Pratiques des mainteneurs de jeux de test privés ou cachés

### Takeaway
Les mainteneurs encadrent l'accès (qui voit, combien de fois, quel fournisseur) et surveillent l'écart public/privé. La notion de « use » est la soumission d'un système à évaluer par un tiers, jamais le nombre de rejeux internes de la même évaluation.

### Cited Findings
- ARC Prize : trois niveaux (public ouvert ; semi-privé pour les modèles de pointe, envoyé à des API tierces, avec reconnaissance d'une « possibility of limited leakage over time » ; privé « extremely restricted to a small number of trusted parties » pour le classement de compétition). Scores vérifiés : « A single run is used, we do not average scores across runs. » Plafond de 10 000 USD par run. Pas d'attente d'optimisation itérative des fournisseurs à partir du retour d'ARC Prize ; accords de confidentialité et de zéro rétention de données ; pas d'outils ni de recherche web pour les ARC-AGI-1 et 2 ; surveillance de l'écart public/semi-privé comme signal de fuite ou de surapprentissage ; nouvelles versions environ chaque année ; invalidation et exclusion possibles en cas de violation. — [ARC Prize policy](https://arcprize.org/policy)
- Humanity's Last Exam : questions publiques, plus un jeu privé « to assess model overfitting » ; la page ne dit pas comment il est administré. Selon Scale, aucune métrique de modèle n'est publiée sur le jeu privé. — [lastexam.ai](https://lastexam.ai), [Scale Labs](https://labs.scale.com/leaderboard/humanitys_last_exam) (via recherche web). Un chiffre de 500 questions circulant sur un wiki communautaire n'est pas confirmé par une source officielle.
- Kaggle : le jeu de test est mélangé, les participants prédisent tout, le serveur ne montre que le score du split public ; à la clôture, les soumissions sélectionnées (souvent deux) sont scorées sur le privé qui décide du classement ; certaines plateformes (DrivenData) prennent la meilleure soumission sur le privé sans sélection. Sources : forums, cours, blogs, pas les règles officielles ; à vérifier par concours. — [résultats de recherche : DrivenData](https://community.drivendata.org/t/setting-final-submissions/5150), [Blum & Hardt, blog Hardt](https://blog.mrtz.org/2015/03/09/competition.html)

### Inferences
- Chez ARC Prize, « un run unique » est une règle de reporting de score (pas de moyenne entre runs), ce qui est plus proche de « un seul essai par tâche et par modèle » : c'est le point de comparaison qui irait contre la lecture proposée. À signaler honnêtement au rédacteur : une règle ARC « single run » existe, mais elle est motivée par le coût et l'intégrité d'un classement public, et non par une théorie de l'adaptativité.
- Dans toutes ces pratiques, ce qui est limité est le retour d'information vers les concepteurs (nombre de soumissions, pas de résultats détaillés publiés) ; c'est une protection contre l'adaptativité, confirmant la lecture de Q1.

### Gaps
- SWE-bench (Verified, Pro, variantes privées) : non traité, aucune source récupérée.
- Règles officielles de Kaggle non lues directement.
- Nombre exact d'évaluations autorisées sur le jeu privé d'ARC Prize (compétition) non trouvé.

## Q4. Préenregistrement et rapports enregistrés : définition de « analysé une seule fois » ; analyses secondaires ou exploratoires ensuite

### Takeaway
Le standard est : l'analyse confirmatoire est spécifiée à l'avance ; tout ce qui s'écarte du plan, ou vient après, est étiqueté exploratoire et séparé. Les stratégies split-sample formalisent un jeu de confirmation tenu en réserve pendant l'exploration.

### Cited Findings
- COS (préenregistrement) : analyses confirmatoires = hypothèses spécifiées d'avance ; exploratoires = recherche de motifs, plus tentatives, besoin de nouvelles données pour confirmer. Si l'on change la façon dont un test planifié est exécuté, il devient exploratoire. Séparer confirmatoire et exploratoire dans la rédaction, avec lien vers le préenregistrement. Tout est rapporté, pas seulement le significatif. Avant l'analyse des résultats on peut mettre à jour le plan ; après les premiers résultats, les changements sont étiquetés exploratoires ; un document « Transparent Changes » est conseillé en cours d'étude ; analyses conditionnelles acceptées si le plan contient des règles SI-ALORS ; « a plan, not a prison ». — [COS, préenregistrement](https://www.cos.io/initiatives/prereg)
- Rapports enregistrés : après l'acceptation de principe, l'étude est menée selon le protocole ; les analyses non enregistrées sont permises dans une section distincte « Exploratory Analyses » ; ne pas suivre le protocole peut faire retirer l'acceptation (donc les écarts doivent être déclarés et justifiés). Analyses dépendantes des données préenregistrables sous forme d'arbre de décision. — [COS, registered reports](https://www.cos.io/initiatives/registered-reports)
- Anderson & Magruder (NBER w23544) : une fraction des données est retenue comme « confirmation sample » ; le chercheur explore librement le reste, puis enregistre un court plan pour les hypothèses à tester sur l'échantillon retenu ; la version améliorée obtient environ 90 % des rejets d'un plan préenregistré optimal ; une conception hybride préspécifie les hypothèses à fort poids et teste les autres par split. — [NBER w23544](https://www.nber.org/papers/w23544), [synthèse World Bank blog](https://blogs.worldbank.org/en/impactevaluations/trouble-pre-analysis-plans-try-these-three-weird-tricks)

### Inferences
- Notre cas est un split-sample dont le plan est gelé avant les données, donc plus strict que Anderson & Magruder (pas d'exploration libre côté calibration qui informe les hypothèses). La règle « un script final unique après gel de tous les verdicts » correspond à l'esprit de ces standards ; les analyses postérieures étiquetées « exploratoires » et datées correspondent exactement à la pratique COS.
- Ces sources ne définissent pas « analysé une fois » en nombre d'exécutions de script : la définition opérationnelle est « une analyse confirmatoire préspécifiée dont le résultat ne retro-agit pas sur le plan ». Le nombre d'exécutions techniques (relancer pour corriger un bug) n'est pas traité ; à écrire dans la règle (par exemple : relance autorisée seulement pour un défaut d'exécution, sans modification de logique, déclarée dans un document de changements transparent).
- Dater et étiqueter les analyses exploratoires suit COS ; ajouter : toute analyse exploratoire ne peut ni modifier un verdict gelé ni servir à justifier un changement de règle sans nouvelle donnée.

### Gaps
- Aucune source trouvée sur la définition exacte de « confirmatory sample analysed once » (formulation littérale) ; c'est une construction des documents ci-dessus.
- Fafchamps & Labonne (split-sample, cité par le blog World Bank) non lu.

## Q5. Évaluation hors ligne (rejeu) de politiques adaptatives : séparation vérité terrain / évaluation, nombre d'usages

### Takeaway
Les travaux sur le rejeu et l'OPE garantissent l'absence de biais pour une évaluation sur données journalisées sous des conditions strictes (journalisation uniformément aléatoire, i.i.d.), mais ne limitent pas le nombre d'usages des données d'évaluation. La séparation entraînement/validation/test y relève de la bonne pratique de sélection de modèle, pas du théorème.

### Cited Findings
- Li, Chu, Langford, Wang (WSDM 2011) : méthode de rejeu pour bandits contextuels, non biaisée, sur données Yahoo, validée contre des tests en ligne ; les événements concordant avec le choix de l'algorithme sont conservés. Théorème 1 : flux d'événements i.i.d. issus d'une politique de journalisation uniformément aléatoire. Les expériences violent l'hypothèse i.i.d. (articles qui entrent et sortent, utilisateurs non indépendants). Les paramètres de l'algorithme étaient « fixed to reasonable values » (ε=0,4, α=1) ; l'article ne décrit pas de jeu de réglage séparé ni de limite du nombre d'usages du jeu de rejeu, et ne traite pas le risque de réglage répété sur les mêmes données de rejeu (d'après le fetch de la version ar5iv). Il dit que l'on peut répéter l'évaluation et moyenner. — [arXiv 1003.5956](https://arxiv.org/pdf/1003.5956), [ar5iv](https://ar5iv.labs.arxiv.org/html/1003.5956)
- Tang & Wiens (MLHC 2021) : en RL hors ligne, la validation habituelle nécessite d'exécuter la politique dans l'environnement réel (infaisable en santé) ; ils étudient un pipeline de sélection de modèle où l'OPE sert de proxy de la performance de validation (sepsis) ; FQE donne le meilleur classement mais coûte cher ; ils proposent une approche en deux étapes. — [arXiv 2107.11003](https://arxiv.org/abs/2107.11003v1), [PMLR 149](https://proceedings.mlr.press/v149/tang21a.html)

### Inferences
- Dans notre dispositif, la « vérité terrain » (taux d'erreur vrais par type, oracle) vient de la calibration, et la confirmation sert au verdict ; cela correspond à la structure entraînement/validation de Tang & Wiens (le validation set OPE est utilisé pour choisir ; un test final sert à rapporter), mais je n'ai pas pu lire leur protocole exact de données (voir Gaps).
- L'absence de limite dans Li et al. ne vaut pas autorisation : leur garantie d'absence de biais suppose une politique fixée indépendamment des données de rejeu. Régler la règle sur le rejeu puis rapporter la même performance réintroduit le biais d'adaptativité de Q1. Notre règle est gelée sans paramètre ajusté, ce qui satisfait cette condition.
- La contrainte i.i.d. de Li et al. est aussi un point de vigilance pour nous : les épisodes d'une même tâche ne sont pas indépendants.

### Gaps
- PDF de Tang & Wiens illisible via l'outil : partition exacte train/validation/test et nombre d'usages non vérifiés.
- Aucune source trouvée qui limite explicitement le nombre d'usages du jeu d'évaluation en OPE ; non couvert, non trouvé.
- Off-policy evaluation hors bandits (Thomas, Brunskill, Voloshin et al.) non explorée.
