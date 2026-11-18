# Antécédents : plans d'échantillonnage continu (Dodge), AOQL, budgets d'erreur et autonomie progressive appliqués aux agents IA

Date de l'état des connaissances : 4 novembre 2026. Recherche web uniquement, environ 17 appels (recherches + lectures). Beaucoup de résultats sont des blogs de praticiens ; les statuts (arXiv / blog / opinion) sont indiqués. Plusieurs articles arXiv n'ont été lus que par leur résumé : signalé à chaque fois.

## 1. Verdict : la connexion Dodge / AOQL / agents IA a-t-elle déjà été faite ?

### Takeaway
Aucune source trouvée n'applique les plans d'échantillonnage continu de Dodge (CSP-1, CSP-2...) ni l'AOQL à l'autonomie d'agents IA. En revanche, l'idée voisine (promotion par séries de succès, rétrogradation immédiate à l'erreur, règles de bascule d'inspection de type MIL-STD-105 / ISO 2859) est déjà publiée en blog (juillet 2026), de sorte que « personne n'a fait le rapprochement avec l'échantillonnage d'acceptation » est faux ; « personne n'a fait le rapprochement avec garantie AOQL dérivée d'un budget » reste, à ma connaissance, vrai. Le terrain est occupé par des règles ad hoc sans garantie.

### Cited Findings
- Recherche « continuous sampling plan » + AI/agents : aucun résultat direct ; seuls remontent des blogs sur l'échantillonnage de sorties d'agents et un article arXiv qui mesure l'autonomie par le nombre d'interventions humaines, sans plan d'échantillonnage — [arXiv 2602.11416](https://arxiv.org/pdf/2602.11416), [Alpesh Nakrani, chap. sampling](https://alpeshnakrani.pages.dev/books/human-in-the-loop/06-sampling-evals-and-continuous-learning/)
- Recherche « Dodge CSP-1 AOQL » + ML/LLM/agent : uniquement de la littérature classique de contrôle qualité (Dodge 1943 ; CSP-1 à deux paramètres i et f fixés par AQL/AOQL ; Shankar & Mohapatra GERT 1994 ; extensions erreur d'inspection, runs courts, entrée markovienne non iid) — [Semantic Scholar, GERT CSP-1](https://www.semanticscholar.org/paper/GERT-ANALYSIS-OF-DODGE'S-CSP-1-CONTINUOUS-SAMPLING-Shankar-Mohapatra/cd05c80dea95d3a1ea27d7861c1fc868808bd378), [CSP-1 sous erreur d'inspection](https://www.semanticscholar.org/paper/The-Dodge-CSP-1-Continuous-Sampling-Plan-Under-Case-Bennett/7adc269c5491e37ac41b893b148bacb5b0df1a3c), [Short-run contexts and imperfect testing for CSPs](https://www.researchgate.net/publication/353434340_Short-Run_Contexts_and_Imperfect_Testing_for_Continuous_Sampling_Plans)
- Seul rapprochement logiciel trouvé : un article applique CSP-1/2/3 à un problème de sélection de tests (ratio d'échappement à AOQL 0,53 %), pas à des modèles ni à des agents ; je n'ai pas retrouvé son titre exact dans les extraits (à vérifier) — résultat d'une recherche élargie, voir [liste CSP sur ResearchGate](https://www.researchgate.net/publication/263601815_Design_of_generalized_CSP-C_continuous_sampling_plan)
- Recherche « skip-lot » / « AOQL » + language model / human oversight : rien ; uniquement ISO 2859-3 (skip-lot) et normes AQL — [ISO 2859-3:2005](https://www.evs.ee/et/iso-2859-3-2005)
- **Antécédent le plus proche (blog, 2 juillet 2026)** : « Acceptance Sampling for Agent Output » propose des lots par workflow, un AQL par type de sortie, trois niveaux d'inspection (normal / renforcé / réduit) avec règles de bascule : normal vers réduit après 10 lots acceptés consécutifs ; réduit vers normal au premier mauvais échantillon (« the first bad sample snaps you back ») ; normal vers renforcé si 2 lots rejetés sur 5 ; renforcé vers normal après 5 acceptés ; remise à normal lors d'une mise à jour de modèle. Citation : « Earned trust is revocable, instantly, by rule. » Aucune formule, ni Dodge, ni CSP, ni AOQL, ni budget d'erreur — [tianpan.co](https://tianpan.co/blog/2026-07-02-acceptance-sampling-for-agent-output-manufacturing-qa)
- Acceptance sampling appliqué à l'évaluation de LLM (et non à l'octroi d'autonomie) : Dhurandhar, Nair et al., classement de LLM sans vérité terrain avec jusqu'à environ 50 % d'échantillons en moins à garanties égales — [arXiv 2407.18370](https://arxiv.org/abs/2407.18370v1)

### Inferences
- La nouveauté défendable n'est plus « appliquer le contrôle qualité à l'autonomie d'agents » (blog tianpan, juillet 2026, règles de bascule de type MIL-STD-105) mais : (i) le choix du plan de type Dodge (échantillonnage continu, pas par lots, adapté à un flux d'actions), (ii) la dérivation de N depuis un budget d'erreur exprimé en excès d'erreurs pour 100 actions, (iii) la garantie de type AOQL robuste à une fiabilité variable, (iv) un protocole ouvert par type d'action.
- Le recoupement des termes « Dodge » et « AOQL » avec un agent IA est vide dans les moteurs utilisés ; l'absence de preuve n'est pas preuve d'absence (recherche web grand public, pas Google Scholar plein texte).
- Attention juridique/d'honnêteté : la règle B (N succès consécutifs puis retrait) est essentiellement CSP-1 inversé (Dodge : inspection à 100 % jusqu'à i pièces conformes consécutives, puis fraction f, retour à 100 % à la première non-conformité). La différence réelle est que l'AOQL de Dodge suppose un processus iid de taux p inconnu, avec « excès » mesuré après inspection ; l'adaptation à une fiabilité qui change demande l'extension aux processus non iid (littérature CSP sur entrée markovienne existe).

### Gaps
- Pas d'accès à Google Scholar ni à des recherches plein texte arXiv : un article dont le résumé ne cite pas Dodge/AOQL mais le fait dans le corps serait manqué.
- Titre/auteurs de l'article CSP sur la sélection de tests non vérifiés.
- Non vérifié : littérature de maintenance/fiabilité (« skip-lot » pour tests de logiciels), SPC appliquée à l'IA hors des sources ci-dessous.

## 2. Littérature AI control (Redwood et autres)

### Takeaway
Le contrôle d'IA donne des garanties empiriques de « sécurité » (probabilité de gagner un jeu rouge/bleu contre un adversaire intentionnel) sous un budget d'audit, pas une garantie d'excès d'erreur par 100 actions pour un agent à fiabilité dérivante. L'architecture (budget d'audit, protocole de déploiement, arrêt si trop de faux positifs) est cousine du plan de Dodge, mais aucune source n'emploie l'échantillonnage continu ni l'AOQL.

### Cited Findings
- Greenblatt et al. 2023 : audit initial (« upfront auditing ») des 2 % premiers problèmes par humain ; arrêt (retour au modèle de confiance) si une porte dérobée est trouvée ; moniteur de confiance avec audit des 2 % d'actions les plus suspectes ; sécurité 15 % (upfront) vs 62 % (trusted monitoring) vs 92 % avec report vers le modèle de confiance à 20 % ; pour le moniteur non fiable, évaluation initiale sur entrées synthétiques et arrêt si taux de faux positifs trop élevé (test d'un taux attendu, vérification de type binomiale) — [arXiv 2312.06942](https://arxiv.org/pdf/2312.06942) (texte lu : lignes sur audit 2 %, arrêt, évaluation du moniteur)
- Control Tax (Terekhov et al., 2025, ICLR 2026) : modèle analytique reliant ROC du moniteur et budget d'audit à la sécurité, en lots et en séquentiel (SNAC) ; la stratégie d'audit optimale dépense davantage tôt ; sécurité mesurée comme probabilité d'attraper la première porte dérobée à 5 % de budget — [arXiv 2506.05296](https://arxiv.org/pdf/2506.05296)
- Ctrl-Z (Bhatt et al., 2025) : rééchantillonnage pour agents ; budget d'audit à calendrier exponentiel nettement supérieur à l'allocation uniforme (uniforme : 22 % de sécurité dans leurs expériences, selon le résumé de recherche) — [arXiv 2504.10374](https://arxiv.org/pdf/2504.10374)
- Combinaison de moniteurs sous contrainte de coût (rapports de vraisemblance de type Neyman-Pearson, budget sur les faux positifs) — [arXiv 2507.15886](https://arxiv.org/pdf/2507.15886) ; post Redwood sur le budget d'audit autour de 1e-4 (1 audit sur 10 000 actions) — [Redwood blog](https://blog.redwoodresearch.org/p/logit-rocs-monitor-tpr-is-linear-in-fpr-in-logit-space)
- Limites des moniteurs marginaux : un article note que les tests séquentiels comme le SPRT se réduisent à des statistiques de vraisemblance marginales sous indépendance — [arXiv 2606.10456](https://arxiv.org/html/2606.10456) (résumé uniquement)
- Calibrated Collective Oversight (Overman & Bayati, mai 2026) : calibrage en ligne du conservatisme par Conformal Decision Theory, taux de violation sous un seuil fixé par l'utilisateur avec bornes en temps fini sans hypothèse distributionnelle ; sert à contraindre un agent plus fort par des superviseurs plus faibles, pas à accorder de l'autonomie — [arXiv 2605.28807](https://www.gsb.stanford.edu/faculty-research/working-papers/calibrating-conservatism-scalable-oversight)

### Inferences
- Différence structurelle : en AI control, le risque est un adversaire (sabotage rare, catastrophique) et la mesure est une probabilité de victoire ; dans le protocole visé, le risque est une erreur ordinaire d'un agent honnête, mesurée en excès par 100 actions. Les garanties AI control ne se transposent pas telles quelles, ni l'inverse (un plan de Dodge ne protège pas contre un agent qui attend la fin de l'inspection).
- CCO (conformal decision theory) est le voisin formel le plus proche pour « taux de violation borné en ligne, temps fini », donc un concurrent crédible à la règle A/B à citer.

### Gaps
- Non lus en entier : Ctrl-Z, Control Tax, 2606.10456, travaux AI control de 2026 (seulement via résumés de recherche). Pas de balayage Alignment Forum systématique.

## 3. Revue humaine par échantillonnage de sorties ML/LLM en production

### Takeaway
Beaucoup de pratique (échantillonnage stratifié, calibrage de juges LLM, tests anytime-valid) et quelques garanties de type conformal, mais aucune approche de type audit statistique (AICPA / PCAOB) ou Dodge qui module le taux de revue humaine par type d'action avec une garantie de qualité sortante.

### Cited Findings
- Selective evaluation, « Trust or Escalate » (Jung, Brahman, Choi, ICLR 2025, oral) : le juge LLM s'abstient et escalade, avec garantie probabiliste d'accord avec l'humain à un niveau fixé — [arXiv 2407.18370](https://arxiv.org/html/2407.18370v1) [attention : l'identifiant 2407.18370 a été renvoyé par la recherche pour deux contenus ; vérifier] ; [ICLR page](https://iclr.cc/virtual/2025/oral/31838)
- Deferral conforme (Babbar) : garantie de contrôle du risque sur les cas automatisés et du taux d'erreur de l'expert sur les cas déférés — [thèse Babbar](https://varunbabbar.github.io/files/Varun_Babbar_MEng_Thesis.pdf)
- E-valuator : vérification séquentielle d'agents par e-processes, valide à tout arrêt — via recherche [papers.cool 2605.28807 voisin] ; non vérifié individuellement
- AgentAssay : SPRT pour tester qu'un agent respecte un taux de réussite ; environ 52 essais attendus si conforme, 34 si régression, contre environ 109 en test à taille fixe ; sert aux tests de régression, pas à l'octroi d'autonomie — [arXiv 2603.02601](https://arxiv.org/pdf/2603.02601)
- Dérive du juge : jeu d'ancrage humain figé et test anytime-valide, avec critique du z-test à α fixe répété — [arXiv 2606.15474](https://arxiv.org/pdf/2606.15474)
- Audit comptable : seulement du contenu praticien. Un guide d'éditeur recommande échantillonnage lourd tant que l'IA est nouvelle, plus léger quand la confiance est acquise, revue totale au-dessus d'un seuil de risque — [Stampli](https://www.stampli.com/resources/human-in-loop-ai/) ; un article d'assurance critique les revues « 10 % fixes » — [Insurance Thought Leadership](https://www.insurancethoughtleadership.com/ai-machine-learning/why-human-audits-ai-decisions-fail). Aucune citation de texte AICPA/PCAOB applicable aux décisions d'IA n'a été vérifiée.
- Billet Galileo : l'échantillonnage de traces rate les échecs de longue traîne, préconise la couverture totale — [Plushcap/Galileo](https://www.plushcap.com/content/galileo/blog/galileo-the-hidden-cost-of-sampling-in-agent-observability)

### Inferences
- L'idée « juge automatique sur chaque action » (hypothèse du protocole) s'oppose à l'argument Galileo : dans le protocole, la vérification est exhaustive mais automatique ; ce qui est échantillonné est l'accord humain préalable. À expliciter pour éviter la confusion.
- Conformal/selective prediction répond à « quand s'abstenir par action selon la confiance », pas à « combien de preuves avant de retirer la validation d'un type d'action ».

### Gaps
- Pas de source primaire sur la modération de contenu / annotation QA (taux de revue adaptatif) ; non cherché en profondeur.
- Pas de texte AICPA/PCAOB AU-C 530 / AS 2315 vérifié.

## 4. Autonomie progressive / graduée des agents

### Takeaway
Le concept d'« earned autonomy » est largement publié (blogs, quelques préprints 2026), souvent avec des seuils arbitraires (90 % sur 8 échantillons, 500 opérations, 30 cas consécutifs). Aucun ne dérive les seuils d'une garantie statistique ; un seul blog emprunte explicitement le contrôle qualité (règles de bascule), un autre le SPC.

### Cited Findings
- Anthropic, « Measuring AI agent autonomy in practice » (18 février 2026) : auto-approve complet environ 20 % des sessions avant 50 sessions, plus de 40 % vers 750 sessions ; interruptions 5 % des tours vers 10 sessions contre environ 9 % pour les utilisateurs expérimentés ; recommande la surveillance post-déploiement et de ne pas imposer l'approbation de chaque action (« friction without necessarily producing safety benefits ») ; confiance observée, aucune garantie — [Anthropic](https://www.anthropic.com/research/measuring-agent-autonomy)
- Claude Code mode auto : retour à l'invite après 3 refus consécutifs ou 20 au total (non configurable) ; règle fixe, sans fondement statistique publié — [support Anthropic](https://support.claude.com/en/articles/17316089) (via résumé de recherche ; non lu directement)
- Feng, McDonald, Zhang, « Levels of Autonomy for AI Agents » (2025) : 5 niveaux (opérateur à observateur), certificats d'autonomie délivrés par un tiers, fondés sur des « autonomy cases » ; aucun mécanisme statistique — [arXiv 2506.12469](https://arxiv.org/pdf/2506.12469)
- « Are You Still the Agent I Authorized? » (Zhang & Zhang, 26 juillet 2026) : plafond d'effets immuable, l'autorité peut croître sous le plafond selon des conditions de preuve ; garanties déterministes sous hypothèses ; critique le fait de laisser la performance relever le plafond — [arXiv 2607.23586](https://arxiv.org/abs/2607.23586) (résumé)
- « The Digital Apprentice » (Weber & Taneja, 3 juin 2026) : autonomie par compétence, « seulement quand la preuve empirique le justifie », approbation humaine ; fenêtres d'évaluation où une proportion p doit passer le seuil ; aucun test statistique nommé dans le résumé — [arXiv 2606.04321](https://arxiv.org/abs/2606.04321)
- Teamvince (blog/hackathon) : autonomie par type d'action, promotion à 90 % de réussite sur au moins 8 échantillons puis 95 % sur 12, avec accord humain ; rétrogradation immédiate à tout échec d'évaluation, un palier à la fois — [teamvincev5](https://teamvincev5.pages.dev/blog/earned-autonomy-eval-gated-agent)
- tianpan (avril 2026) : promotion si erreur d'écriture sous 0,5 %, override sous 3 %, sur 500 opérations ou 30 jours ; rétrogradation dure si erreur plus de 5 % sur 1 h ; avertit que promouvoir après 20 succès, c'est décider sur du bruit ; ne cite ni Dodge, ni test séquentiel, ni budget d'erreur — [tianpan](https://tianpan.co/blog/2026-04-17-earned-autonomy-ai-agents-progressive-supervision)
- attacca-forge : porte à 90 % d'accord sur 30 cas consécutifs — [progressive-autonomy.md](https://cdn.jsdelivr.net/npm/attacca-forge@0.6.0/docs/methodology/progressive-autonomy.md) (via extrait)
- SemiWiki (Govindaram, octobre 2026, opinion) : autorité par classe de décision, perte automatique d'un échelon quand une métrique franchit une limite de contrôle ou qu'une règle de Western Electric se déclenche ; SPC appliquée à l'agent, sans plan d'échantillonnage ni garantie formelle — [SemiWiki](https://semiwiki.com/eda/375060-who-gets-to-move-the-recipe-how-autonomous-agents-earn-decision-authority-in-the-fab/) (via résumé de recherche ; page en 403 à la lecture directe)
- AWS (26 août 2026), autonomie graduée en cinq dimensions à partir d'un palier lecture seule — [aws-news](https://aws-news.com/article/2026-08-26-closing-the-ai-agent-trust-gap-with-graduated-autonomy) (extrait uniquement)

### Inferences
- Le terme « earned autonomy » est déjà largement employé ; ne pas le présenter comme une invention. Les seuils publiés (8, 12, 30, 500, 20 échantillons) sont arbitraires : c'est l'écart que comble une dérivation par budget/AOQL.
- Teamvince et tianpan (juillet) sont les deux antériorités à citer pour « par type d'action » et « rétrogradation immédiate à l'échec ».

### Gaps
- Pas de lecture intégrale des préprints 2607.23586 et 2606.04321 (conditions de preuve exactes non vérifiées).
- Pas de recherche sur la documentation OpenAI / Google DeepMind / METR sur les modes de permission ; pas de recherche sur la littérature IHM de la confiance (cs.HC) au-delà d'Anthropic.

## 5. Budgets d'erreur (SRE) appliqués aux agents / systèmes ML

### Takeaway
L'extension du budget d'erreur SRE à l'autonomie d'agents existe déjà (préprint août 2026 et blogs), sous forme de niveaux d'autonomie selon le budget restant ; elle ne cite ni échantillonnage de Dodge ni garantie AOQL.

### Cited Findings
- CASE (Telukunta, Lilis, Baron, 10 août 2026) : les budgets d'erreur étendus à la qualité de décision, l'autonomie devenant une variable contrôlée qui monte quand le budget est sain et se resserre à l'épuisement ; modèle de maturité à cinq niveaux ; mécanisme, seuils et formules non visibles dans le résumé — [arXiv 2608.10153](https://arxiv.org/abs/2608.10153)
- Blogs : états du budget (sain à épuisé) qui restreignent les actions autorisées ; budgets multiples fiabilité / sécurité / coût ; bascule en conservateur à l'épuisement, remise à zéro mensuelle ; exemple de politique exigeant plus de 25 % de budget restant — [channel.tel](https://www.channel.tel/blog/sre-ai-agents-slo-error-budget-cx), [Gravitee](https://gravitee.io/corpus/gen-1700/software-quality/slos-and-error-budgets-for-agents.html), [agent.ceo](https://agent.ceo/blog/agent-error-budgets-sre-cyborgenic), [DEV, pricing de l'agent AIOps](https://dev.to/pradeep_kandepaneni/the-autonomy-boundary-pricing-your-aiops-agent-in-both-error-budget-and-dollars-e2a)

### Inferences
- Le budget d'erreur SRE est une consommation d'un budget sur fenêtre (l'agent perd des droits en dépensant), pas un dimensionnement d'une règle d'échantillonnage depuis un budget (N dérivé du budget). Ce sens inverse est la partie la plus originale, mais il faut lire CASE en entier avant de l'affirmer.

### Gaps
- Mécanisme exact de CASE non vérifié (résumé seulement).
- Aucune source SRE primaire (Google SRE Book) rapprochée de l'IA.

## 6. Requêtes exécutées (liste demandée)

Recherches : « continuous sampling plan » + AI agents autonomy ; « acceptance sampling » + LLM outputs human review guarantee ; « earned autonomy » + AI agents sequential test permissions ; AI control audit budget trusted monitoring sequential auditing 2025 ; Anthropic measuring agent autonomy ; error budget SRE AI agents autonomy levels ; Dodge continuous sampling plan CSP-1 AOQL + ML/LLM/AI agent (mode étendu) ; skip-lot / AOQL + language model human oversight ; SPRT + AI agent autonomy human approval ; conformal risk control agent actions human escalation ; AI control online setting audit budget FPR ; Levels of Autonomy Feng 2025 ; Claude Code auto mode fallback ; adaptive human review AICPA audit sampling ML ; « consecutive » successes agent autonomy promotion ; fab agents statistical process control authority ; Dodge / continuous sampling + LLM judge audit drift.
Lectures : tianpan (acceptance sampling), arXiv 2607.23586, 2606.04321, 2608.10153, Teamvince, Stanford GSB (CCO), AI control 2312.06942 (PDF), tianpan (earned autonomy), page Anthropic. Échec : SemiWiki (403).
Résultat des recherches Dodge / AOQL / skip-lot / continuous sampling avec IA : aucun résultat direct.
