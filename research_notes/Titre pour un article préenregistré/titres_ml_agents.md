# Conventions de titre des articles influents 2023-2026 sur la fiabilité, l'autonomie, la délégation, la supervision humaine et l'évaluation des agents IA

Méthode : titres vérifiés mot pour mot via l'API arXiv (export.arxiv.org, `id_list`) le 17/11/2026, sauf mention contraire. Lien de chaque article : `https://arxiv.org/abs/<id>`. Nombres de citations Semantic Scholar non obtenus (API en erreur 429, limite de débit) : voir Lacunes.

## Q1. Quels motifs de titre utilisent les articles très cités ou très discutés sur les agents et l'évaluation ?

### Takeaway
Les quatre motifs dominants sont : (1) « Nom-bench : description » ou « Nom : sous-titre » (benchmarks, outils) ; (2) titre déclaratif court qui énonce une thèse (« AI Agents That Matter », « Fully Autonomous AI Agents Should Not be Developed ») ; (3) question (« Can Language Models Resolve… ? », « Why Do Multi-Agent LLM Systems Fail? ») ; (4) terme forgé ou métaphore (« AI Control », « Sleeper Agents », « The Leaderboard Illusion », « Ctrl-Z »). Les articles méthodologiques de groupes très visibles (Princeton, METR, Anthropic, Redwood) privilégient le titre déclaratif court ou le terme forgé ; les benchmarks, le motif à deux-points.

### Cited Findings

**A. Motif « Nom (souvent -bench) : description de ce que c'est / pour quoi »**
- « SWE-bench: Can Language Models Resolve Real-World GitHub Issues? » — arXiv 2310.06770, 2023 (ICLR 2024). Hybride nom + question. — [arXiv](https://arxiv.org/abs/2310.06770)
- « $τ$-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains » — arXiv 2406.12045, 2024. — [arXiv](https://arxiv.org/abs/2406.12045)
- « GAIA: a benchmark for General AI Assistants » — arXiv 2311.12983, 2023. — [arXiv](https://arxiv.org/abs/2311.12983)
- « AgentBench: Evaluating LLMs as Agents » — arXiv 2308.03688, 2023. — [arXiv](https://arxiv.org/abs/2308.03688)
- « WebArena: A Realistic Web Environment for Building Autonomous Agents » — arXiv 2307.13854, 2023. — [arXiv](https://arxiv.org/abs/2307.13854)
- « TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks » — arXiv 2412.14161, 2024. — [arXiv](https://arxiv.org/abs/2412.14161)
- « RE-Bench: Evaluating frontier AI R&D capabilities of language model agents against human experts » — arXiv 2411.15114, 2024 (METR). — [arXiv](https://arxiv.org/abs/2411.15114)
- « Holistic Agent Leaderboard: The Missing Infrastructure for AI Agent Evaluation » (HAL) — arXiv 2510.11977, 2025. Sous-titre argumentatif (« The Missing… »), pas seulement descriptif. — [arXiv](https://arxiv.org/abs/2510.11977)
- « Signal and Noise: A Framework for Reducing Uncertainty in Language Model Evaluation » — arXiv 2508.13144, 2025. Motif exact « X: a Y for Z ». — [arXiv](https://arxiv.org/abs/2508.13144)
- « AI Control: Improving Safety Despite Intentional Subversion » — arXiv 2312.06942, 2023. Terme forgé + sous-titre qui dit le résultat. — [arXiv](https://arxiv.org/abs/2312.06942)
- « Ctrl-Z: Controlling AI Agents via Resampling » — arXiv 2504.10374, 2025. Jeu de mots + méthode. — [arXiv](https://arxiv.org/abs/2504.10374)
- « Lost in the Middle: How Language Models Use Long Contexts » — arXiv 2307.03172, 2023. Formule-choc + sous-titre explicatif. — [arXiv](https://arxiv.org/abs/2307.03172)
- « Sleeper Agents: Training Deceptive LLMs that Persist Through Safety Training » — arXiv 2401.05566, 2024 (Anthropic). — [arXiv](https://arxiv.org/abs/2401.05566)
- « Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations » — arXiv 2411.00640, 2024. — [arXiv](https://arxiv.org/abs/2411.00640)
- « When Benchmarks are Targets: Revealing the Sensitivity of Large Language Model Leaderboards » — arXiv 2402.01781, 2024 (allusion à la loi de Goodhart). — [arXiv](https://arxiv.org/abs/2402.01781)
- « The Oversight Game: Learning to Cooperatively Balance an AI Agent's Safety and Autonomy » — arXiv 2510.26752, 2025. — [arXiv](https://arxiv.org/abs/2510.26752)
- « AI and Human Oversight: A Risk-Based Framework for Alignment » — arXiv 2510.09090, 2025. — [arXiv](https://arxiv.org/abs/2510.09090)
- « Oversight Has a Capacity: Calibrating Agent Guards to a Subjective, Fatiguing Human » — arXiv 2606.08919, 2026. Thèse déclarative + deux-points + méthode. — [arXiv](https://arxiv.org/abs/2606.08919)
- « Human oversight of agentic systems in practice: Examining the oversight work, challenges, and heuristics of developers using software agents » — arXiv 2606.05391, 2026 (cs.SE, style HCI/étude empirique, titre long). — [arXiv](https://arxiv.org/abs/2606.05391)

**B. Motif déclaratif court (thèse ou constat, sans deux-points)**
- « AI Agents That Matter » — arXiv 2407.01502, 2024 (Kapoor, Narayanan et al., Princeton). 4 mots, aucun sous-titre. — [arXiv](https://arxiv.org/abs/2407.01502)
- « Fully Autonomous AI Agents Should Not be Developed » — arXiv 2502.02649, 2025. Thèse normative. — [arXiv](https://arxiv.org/abs/2502.02649)
- « Levels of Autonomy for AI Agents » — arXiv 2506.12469, 2025. Nominal, cadre conceptuel. — [arXiv](https://arxiv.org/abs/2506.12469)
- « Visibility into AI Agents » — arXiv 2401.13138, 2024. — [arXiv](https://arxiv.org/abs/2401.13138)
- « Intelligent AI Delegation » — arXiv 2602.11865, 2026. — [arXiv](https://arxiv.org/abs/2602.11865)
- « Towards a Science of AI Agent Reliability » — arXiv 2602.16666, 2026. Formule « Towards a science of X ». — [arXiv](https://arxiv.org/abs/2602.16666)
- « Authenticated Delegation and Authorized AI Agents » — arXiv 2501.09674, 2025. — [arXiv](https://arxiv.org/abs/2501.09674)
- « Establishing Best Practices for Building Rigorous Agentic Benchmarks » — arXiv 2507.02825, 2025. — [arXiv](https://arxiv.org/abs/2507.02825)
- « Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity » — arXiv 2507.09089, 2025 (essai randomisé METR). Titre purement descriptif, sans révéler le résultat (ralentissement), alors que l'article a été très médiatisé. — [arXiv](https://arxiv.org/abs/2507.09089)
- « Measuring AI Ability to Complete Long Software Tasks » — arXiv 2503.14499, 2025 (METR, « horizon temporel »). Titre de la v4 ; le titre a donc été révisé au fil des versions (voir Lacunes). — [arXiv](https://arxiv.org/abs/2503.14499)
- « Frontier Models are Capable of In-context Scheming » — arXiv 2412.04984, 2024 (Apollo). Constat déclaratif = résultat principal. — [arXiv](https://arxiv.org/abs/2412.04984)
- « Large Language Models Often Know When They Are Being Evaluated » — arXiv 2505.23836, 2025. Constat déclaratif. — [arXiv](https://arxiv.org/abs/2505.23836)
- « LLM Evaluators Recognize and Favor Their Own Generations » — arXiv 2404.13076, 2024. Constat déclaratif. — [arXiv](https://arxiv.org/abs/2404.13076)
- « Alignment faking in large language models » — arXiv 2412.14093, 2024 (Anthropic). Terme forgé + domaine. — [arXiv](https://arxiv.org/abs/2412.14093)
- « The Leaderboard Illusion » — arXiv 2504.20879, 2025. Terme forgé seul, 3 mots. — [arXiv](https://arxiv.org/abs/2504.20879)
- « Quantifying Variance in Evaluation Benchmarks » — arXiv 2406.10229, 2024. — [arXiv](https://arxiv.org/abs/2406.10229)
- « Model evaluation for extreme risks » — arXiv 2305.15324, 2023 (DeepMind et al.). — [arXiv](https://arxiv.org/abs/2305.15324)
- « Sabotage Evaluations for Frontier Models » — arXiv 2410.21514, 2024 (Anthropic). — [arXiv](https://arxiv.org/abs/2410.21514)
- « Log analysis is necessary for credible evaluation of AI agents » — ICML 2026, atelier « Failure Modes in Agentic AI: Reproducible Triggers, Trace Diagnostics, and Verified Fixes » (Kirgis, Kapoor, … Narayanan). Thèse déclarative « X is necessary for Y ». — [ICML 2026](https://icml.cc/virtual/2026/77910)

**C. Motif question**
- « Are Emergent Abilities of Large Language Models a Mirage? » — arXiv 2304.15004, 2023 (NeurIPS 2023, prix d'article exceptionnel selon ma connaissance, non revérifié ici). Question + métaphore. — [arXiv](https://arxiv.org/abs/2304.15004)
- « Why Do Multi-Agent LLM Systems Fail? » — arXiv 2503.13657, 2025. — [arXiv](https://arxiv.org/abs/2503.13657)
- « SWE-bench: Can Language Models Resolve Real-World GitHub Issues? » (cf. A). — [arXiv](https://arxiv.org/abs/2310.06770)
- Ateliers NeurIPS 2026 eux-mêmes titrés en question : « Who Verifies the Agents? Toward Reliable Agent Development » et « Can We Trust AI Evaluation? Robustness, Causality, and Risk in Modern AI Assessment ». — [NeurIPS 2026 W1](https://neurips.cc/virtual/2026/workshop/137488) ; [NeurIPS 2026 W2](https://neurips.cc/virtual/2026/workshop/137525)

**D. Titres acceptés dans un atelier NeurIPS 2026 sur l'évaluation (échantillon, page du programme)** — atelier « Can We Trust AI Evaluation? » — [NeurIPS 2026](https://neurips.cc/virtual/2026/workshop/137525)
- « Position: AI Evaluations Should be Grounded on a Theory of Capability »
- « Benchmark Error Tracks the Perturbation, Not the Construct »
- « Your Benchmark Is an Empirical Measure Over Difficulty »
- « Dutch Books for Language Models »
- « Mind the Tokenizer: Why a Single Space Decides What Multiple-Choice Evaluations Measure »
- « Can We Trust Small Language Models as Judges? »

### Inferences
- Les articles « de positionnement » les plus discutés du domaine agents (Princeton : « AI Agents That Matter », « Log analysis is necessary… ») utilisent un titre déclaratif court, sans deux-points, qui énonce la thèse.
- Les benchmarks/outils utilisent quasi systématiquement « Nom: … » ; le deux-points sert à donner un nom mémorisable à un artefact. Sans artefact nommé, le deux-points sert plutôt à coller une formule-choc à un sous-titre descriptif (« Lost in the Middle: … », « Signal and Noise: … », « Oversight Has a Capacity: … »).
- Les titres de constat (« Frontier Models are Capable of In-context Scheming », « LLMs Often Know When They Are Being Evaluated », « Benchmark Error Tracks the Perturbation, Not the Construct ») donnent le résultat dans le titre ; c'est le motif dominant dans l'échantillon d'atelier 2026.
- Contre-exemple notable : l'essai randomisé METR, très médiatisé, a un titre neutre et descriptif (« Measuring the Impact of… ») ; un titre neutre n'a pas empêché l'attention, portée par le résultat contre-intuitif et la marque METR.
- Les mots « autonomy », « delegation », « oversight », « reliability » apparaissent tels quels dans les titres récents (2025-2026), en général dans un titre nominal court (« Levels of Autonomy for AI Agents », « Intelligent AI Delegation », « Towards a Science of AI Agent Reliability »).

### Gaps
- Nombres de citations Semantic Scholar non obtenus (erreur 429 répétée). Le classement « très cité » repose donc sur la notoriété connue (SWE-bench, τ-bench, AI Control, Sleeper Agents, METR) et non sur des chiffres vérifiés ici.
- Titre original de 2503.14499 : la v4 dit « Long Software Tasks » ; la v1 s'intitulait, selon ma connaissance, « Measuring AI Ability to Complete Long Tasks » — non revérifié dans cette session.
- Venue exacte de plusieurs préprints (2602.11865, 2602.16666, 2506.12469, 2510.11977) non vérifiée.

## Q2. Comment les articles statistiquement rigoureux ou préenregistrés titrent-ils ?

### Takeaway
Deux familles : (a) titres de méthode/outil statistique au motif deux-points (« Adding Error Bars to Evals: A Statistical Approach… », « Signal and Noise: A Framework… ») ; (b) en 2026, des préprints qui mettent « Preregistered / Pre-Registered » dans le titre, souvent en sous-titre après une formule (« Clean Engineering, Unstable Measurement: A Preregistered Reliability Failure… »). Le mot « preregistration » en titre reste rare et récent.

### Cited Findings
- « Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations » — arXiv 2411.00640, 2024 (formule-image + sous-titre de méthode). — [arXiv](https://arxiv.org/abs/2411.00640)
- « Quantifying Variance in Evaluation Benchmarks » — arXiv 2406.10229, 2024. — [arXiv](https://arxiv.org/abs/2406.10229)
- « Signal and Noise: A Framework for Reducing Uncertainty in Language Model Evaluation » — arXiv 2508.13144, 2025. — [arXiv](https://arxiv.org/abs/2508.13144)
- « Preregistration for Experiments with AI Agents » — arXiv 2606.11217, 2026 ; un site d'annotations le classe en ICML 2026 (non vérifié sur icml.cc). Plaide pour figer prompts d'évaluateur et versions de modèles et rapporter tous les modèles testés. — [arXiv](https://arxiv.org/abs/2606.11217) ; [papernotes](https://en.papernotes.org/ICML2026/llm_nlp/preregistration_for_experiments_with_ai_agents/)
- « Mitigating LLM-based p-Hacking by Preregistering for the Next LLM » — arXiv 2606.27687, 2026 (CMU d'après la presse spécialisée). — [arXiv](https://arxiv.org/abs/2606.27687) ; [AI Weekly](https://aiweekly.co/node/5579)
- « Clean Engineering, Unstable Measurement: A Preregistered Reliability Failure of Black-Box LLM Observers on Shared Endpoints » — arXiv 2609.04198, 2026. Annonce un résultat négatif préenregistré dans le titre. — [arXiv](https://arxiv.org/abs/2609.04198)
- « Scaffold, Not Vocabulary? A Controlled, Two-Tier, Pre-Registered Study of a Popperian Code-Generation Skill » — arXiv 2606.06454, 2026. Question-thèse + sous-titre qui empile les qualificatifs de design. — [arXiv](https://arxiv.org/abs/2606.06454)
- Les ateliers NeurIPS de préenregistrement datent de 2020 (« The pre-registration experiment: an alternative publication model for machine learning research ») et 2021 (« The pre-registration workshop: an alternative publication model for machine learning research ») ; le format demandait un article sans résultats, décrivant un protocole à exécuter après acceptation. Actes 2021 dans PMLR vol. 181 (ex. « Benchmarking Real-Time Reinforcement Learning »). Aucune édition 2023-2026 trouvée. — [NeurIPS 2020](https://neurips.cc/virtual/2020/workshop/16158) ; [NeurIPS 2021](https://neurips.cc/virtual/2021/workshop/21885) ; [PMLR v181](https://proceedings.mlr.press/v181)

### Inferences
- « Preregistered » fonctionne surtout comme qualificatif de crédibilité dans le sous-titre, pas comme accroche principale.
- Annoncer un résultat négatif ou un échec dans le titre (« A Preregistered Reliability Failure… ») est accepté en 2026 et cohérent avec l'esprit du préenregistrement (publier quel que soit le résultat).
- Empiler les qualificatifs de design (« Controlled, Two-Tier, Pre-Registered ») allonge le titre ; les exemples les plus visibles (« Adding Error Bars to Evals ») restent courts et imagés.

### Gaps
- Pas de mesure de l'audience des titres « preregistered » 2026 (préprints récents, citations non obtenues).
- Pas trouvé d'atelier dédié au préenregistrement en ML après 2021.

## Q3. Les titres du domaine utilisent-ils un terme forgé, et cela aide-t-il ?

### Takeaway
Oui, et plusieurs des articles les plus connus sont portés par un terme forgé devenu nom de sous-domaine ou de phénomène (« AI Control », « Sleeper Agents », « Alignment faking », « In-context Scheming », « The Leaderboard Illusion », « Lost in the Middle »). Aucune étude trouvée ne mesure causalement l'effet du terme forgé en ML ; les études bibliométriques générales sont mitigées sur les titres « accrocheurs » et les questions.

### Cited Findings
- Termes forgés en titre : « AI Control » (2312.06942), « Sleeper Agents » (2401.05566), « Alignment faking » (2412.14093), « In-context Scheming » (2412.04984), « The Leaderboard Illusion » (2504.20879), « Lost in the Middle » (2307.03172), « Ctrl-Z » (2504.10374). — [arXiv 2312.06942](https://arxiv.org/abs/2312.06942) ; [arXiv 2401.05566](https://arxiv.org/abs/2401.05566) ; [arXiv 2412.14093](https://arxiv.org/abs/2412.14093) ; [arXiv 2412.04984](https://arxiv.org/abs/2412.04984) ; [arXiv 2504.20879](https://arxiv.org/abs/2504.20879) ; [arXiv 2307.03172](https://arxiv.org/abs/2307.03172) ; [arXiv 2504.10374](https://arxiv.org/abs/2504.10374)
- Étude en économie (347 197 articles, attractivité du titre notée par ML) : titres attractifs associés à +1,925 citations en moyenne et à des revues mieux notées. Domaine non-ML. — [Attraction is All You Need (PDF)](https://kororinpas.github.io/files/Attraction_is_All_You_Need%20.pdf)
- Titres en question : effet sur les citations non significatif dans une étude de 2 400 titres en communication ; une étude de 2024 en sciences sociales (2 200 titres) trouve que les questions attirent des lecteurs mais contribuent moins aux citations que les titres déclaratifs ou créatifs. Synthèse rapportée par le moteur de recherche, sources primaires non ouvertes. — [Nature Index](https://www.nature.com/nature-index/news/five-features-highly-cited-scientific-article) ; [EBSCO](https://www.ebsco.com/articles/education/928070a8-7e8d-594e-bc21-b4a111e24768/article-titles-matter-in-download-and-citation-metrics-refining-descriptive-titles)
- Longueur : les articles très cités auraient des titres de 7 à 13 mots (Elgendi, IEEE Access, 200 articles) ; titres plus longs corrélés à moins de citations. — [UBC](https://engineering.ubc.ca/news/2019/tips-for-boosting-your-citation-count-inspired-machine-learning)

### Inferences
- Un terme forgé aide quand il nomme un phénomène ou un cadre que d'autres voudront citer par son nom (« AI control », « alignment faking ») ; il doit être compréhensible sans lire l'article ou accompagné d'un sous-titre explicite.
- Motif sûr pour un terme forgé : « Terme forgé: sous-titre descriptif » (« AI Control: Improving Safety Despite Intentional Subversion »).

### Gaps
- Pas vérifié si « earned autonomy » ou « delegation gap » existent déjà dans des titres arXiv (recherche arXiv par titre bloquée par limite de débit). À vérifier avant de forger un terme, pour éviter collision ou antériorité.
- Aucune étude spécifique aux venues ML sur l'effet des termes forgés.

## Q4. Consignes des appels d'ateliers ou guides de style sur les titres

### Takeaway
Les appels d'ateliers NeurIPS/ICML consultés ne donnent aucune consigne de titre. La seule règle formelle trouvée est celle du track « position » d'ICML : le titre doit énoncer la position et commencer par « Position: » ; cette convention déborde dans les ateliers (titres « Position: … » acceptés en atelier NeurIPS 2026).

### Cited Findings
- ICML 2025 et 2026 : « The Title should state the position and start with "Position:" » ; ICML 2024 exigeait « Position Paper: <Paper title> ». — [ICML 2026 CFP](https://icml.cc/Conferences/2026/CallForPositionPapers) ; [ICML 2025 CFP](https://icml.cc/Conferences/2025/CallForPositionPapers) ; [ICML 2024 CFP](https://icml.cc/Conferences/2024/CallForPositionPapers)
- Exemple ICML 2025 position : « Position: AI Evaluation Should Learn from How We Test Humans ». — [mlanthology](https://mlanthology.org/icml/2025/zhuang2025icml-position)
- Atelier NeurIPS 2026 « Can We Trust AI Evaluation? » : un titre « Position: AI Evaluations Should be Grounded on a Theory of Capability » accepté ; pas de consigne de soumission sur la page. — [NeurIPS 2026](https://neurips.cc/virtual/2026/workshop/137525)
- Atelier NeurIPS 2026 « Who Verifies the Agents? Toward Reliable Agent Development » : thèmes vérificateurs résistants au reward hacking, simulation ancrée comme vérité terrain, intégration latence/coût/calibration ; aucune consigne de format ou de titre sur la page. — [NeurIPS 2026](https://neurips.cc/virtual/2026/workshop/137488)
- Ateliers NeurIPS 2025 pertinents (thèmes seulement) : Scaling Environments for Agents (SEA), atelier LLM evaluation, RegML. — [SEA](https://sea-workshop.github.io/SEA-Workshop) ; [LLM eval CFP](https://sites.google.com/view/llm-eval-workshop/call-for-papers) ; [RegML CFP](https://regulatableml.github.io/cfp)
- Un article analyse les tracks position NeurIPS et ICML 2025 : « An Investigation of the NeurIPS and ICML 2025 Position Tracks » (arXiv 2608.16894, 2026), non lu. — [arXiv](https://arxiv.org/abs/2608.16894)

### Inferences
- Pour un atelier NeurIPS/ICML sur agents/sécurité/évaluation, aucun motif n'est imposé ; l'échantillon accepté 2026 penche vers le constat déclaratif et la thèse (« X Should… », « X Tracks Y, Not Z »).
- « Position: » est à réserver à un article de thèse ; pour un article empirique préenregistré, un titre de constat ou « formule: sous-titre descriptif (avec "preregistered") » colle mieux aux usages.
- Attention à l'anonymat (ateliers en double aveugle sur OpenReview en général) : un terme forgé déjà associé publiquement aux auteurs peut lever l'anonymat — inférence, non sourcée par un appel précis.

### Gaps
- Pas d'appel d'atelier consulté donnant une consigne explicite de titre ou de longueur.
- Pas consulté les pages OpenReview des ateliers 2026 pour les règles d'anonymat exactes.
