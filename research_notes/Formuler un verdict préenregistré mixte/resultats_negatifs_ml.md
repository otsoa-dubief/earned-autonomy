# Comment les venues ML/IA titrent, cadrent et rédigent les résultats négatifs, nuls ou non concluants

Note de méthode : les résumés arXiv ci-dessous ont été récupérés en texte brut via l'API arXiv (export.arxiv.org), et les résumés PMLR directement sur les pages PMLR. Les citations sont donc exactes. Les textes des appels à contributions (CFP) viennent d'un outil de lecture web qui ne rend que des extraits courts : ce sont des fragments exacts, mais pas des paragraphes complets.

## 1. Les ateliers ICBINB (« I Can't Believe It's Not Better ») : langage des appels et exemples acceptés

### Takeaway
ICBINB existe depuis 2020 (NeurIPS 2020-2023, puis ICLR 2025 et ICLR 2026). L'atelier accueille explicitement les résultats négatifs, avec une exigence implicite : une hypothèse claire et, de préférence, une explication de l'échec. Les titres acceptés sont affirmatifs et précis : ils nomment la limite (« X fails to… », « The Limits of… », « … is Not a Free Lunch »). Beaucoup détournent le nom de l'atelier (« I Can't Believe It's Not Robust »).

### Cited Findings
**Éditions et thèmes**
- NeurIPS 2020 : « Bridging the gap between theory and empiricism in probabilistic machine learning ». NeurIPS 2021 : « A Workshop for "beautiful" ideas that _should_ have worked ». NeurIPS 2022 : « Understanding Deep Learning Through Empirical Falsification ». NeurIPS 2023 : « Failure Modes in the Age of Foundation Models » — [Site ICBINB](https://i-cant-believe-its-not-better.github.io/)
- L'édition 2021 (« I (Still) Can't Believe It's Not Better! ») demandait des idées qui ne donnent pas les résultats attendus, mais dont les auteurs savent expliquer pourquoi. Les soumissions étaient non archivées ; les papiers exemplaires étaient proposés pour PMLR — [Archive de l'appel, liste UAI](https://go.mail-archive.com/uai@engr.orst.edu/msg13370.html) (résumé du moteur de recherche, non vérifié mot à mot)

**Langage des appels (fragments exacts)**
- Appel 2022 : les soumissions doivent « explicitly formulate a hypothesis related to deep learning or its applications », puis « empirically falsify it through experiments ». Les organisateurs « further encourage submissions to go a layer deeper and investigate the causes of an initial idea not working as expected ». L'appel affirme aussi que « negative results offer important learning opportunities », et cite Popper : « Confirmations should count only if they are the result of risky predictions » — [ICBINB 2022](https://sites.google.com/view/icbinb-2022/)
- Appel ICLR 2025 : « Why don't deep learning approaches always deliver as expected in the real world? » ; « this workshop aims to focus on understanding through negative results » ; constat d'un manque, « lacking a platform to systematically collect real-world failure cases » — [ICBINB 2025](https://sites.google.com/view/icbinb-2025)
- Appel ICLR 2026, centré sur les LLM : « We invite papers that focus on the negative results… ». Il vise « any well-supported finding that challenges prevailing assumptions or exposes key limitations of LLMs », ainsi que les travaux qui « aim to overcome such current limitations through a promising approach but struggled to do so ». Un axe porte sur les **agents** : « challenges in multi-step planning, tool use, memory, and self-reflection » — [ICBINB 2026](https://sites.google.com/view/icbinb-2026)
- ICLR 2026 prévoyait deux prix : l'« Entropic Award » (le résultat négatif le plus surprenant) et le « Didactic Award » (le papier le mieux expliqué, le plus pédagogique) — [résumé de recherche sur ICBINB 2026](https://sites.google.com/view/icbinb-2026/submit) (le fetch de la page d'accueil ne montre pas ces prix : à vérifier)

**Titres acceptés à ICBINB ICLR 2026 (56 papiers, extraits pertinents)** — [liste des papiers ICBINB 2026](https://sites.google.com/view/icbinb-2026/papers)
- « The Limits of Long-Context Reasoning in Automated Bug Fixing »
- « Spatial Reasoning is Not a Free Lunch: A Controlled Study on LLaVA »
- « Style over Substance: LLM-as-a-Judge Fails to Evaluate Multi-Party Social Dialogue »
- « One Step Forward, Two Steps Back: Regression Errors and Cost Inefficiencies in LLM Iterative Refinement for Code Generation »
- « Synthetic Error Injection Fails to Elicit Self-Correction In Language Models »
- « Random Is Hard to Beat: Active Selection in Online DPO with Modern LLMs »
- « Bigger Is Not Better Under Differential Privacy: Optimization Failure at Eleven-Billion Scale… »
- « I Can't Believe It's Not Robust: Catastrophic Collapse of Safety Classifiers under Embedding Drift » ; « I Can't Believe It's Not Safer: Preference–Safety Disassociation in Clinical LLM Evaluation »
- Titres-questions : « When can you TRUST Large Language Models? » ; « Is Evaluation Awareness Just Format Sensitivity? Limitations of Probe-Based Evidence under Controlled Prompt Structure » ; « Can Multi-Modal LLMs Provide Live Step-by-Step Task Guidance? »
- La page affiche une section « Award Winners » sous forme d'images sans texte : les lauréats n'ont pas pu être identifiés.

**ICBINB NeurIPS 2021, publié dans PMLR v163** — [PMLR v163](https://proceedings.mlr.press/v163/)
- Titre : « Addressing Bias in Active Learning with Depth Uncertainty Networks... or Not ». Résumé : « They should therefore see an increase in performance with bias correction. Surprisingly, they do not. We propose that this negative result, as well as the results Farquhar et al. [2021], can be explained via the lens of the bias-variance decomposition of generalisation error. » — [Murray et al., PMLR v163](https://proceedings.mlr.press/v163/murray22a.html)
- Titre : « Is the Number of Trainable Parameters All That Actually Matters? ». Dernière phrase : « We find that the scaling relationship between test loss and compute depends only on the actual number of trainable parameters; scaling laws cannot be deceived by spurious parameters. » — [Chatelain et al., PMLR v163](https://proceedings.mlr.press/v163/chatelain22a.html)

### Inferences
- Le modèle ICBINB tient en trois temps : hypothèse attendue, constat qu'elle ne tient pas (souvent avec « Surprisingly, … not »), puis explication ou piste. Un papier qui dit « les agents n'atteignent pas le niveau de preuve requis » s'y prête bien s'il formule le seuil comme une hypothèse risquée posée à l'avance (le vocabulaire popperien de l'appel 2022).
- Une phrase d'aveu courte, à la première personne et au présent (« Surprisingly, they do not. ») est acceptée et même valorisée.
- Le prix « Didactic » suggère que la clarté d'exposition d'un résultat négatif est un critère de mérite à part entière.

### Gaps
- Les lauréats ICBINB 2026 n'ont pas pu être identifiés (images sans texte).
- Les résumés des papiers ICBINB 2026 sur les agents et la fiabilité n'ont pas été récupérés.
- Un fait reste non vérifié dans le texte de l'appel : le caractère archivé ou non des éditions ICLR.

## 2. Autres venues : préenregistrement, reproductibilité, TMLR, checklist NeurIPS

### Takeaway
Aucune de ces venues ne donne de consignes de formulation propres aux résultats négatifs. Les règles qui s'en approchent le plus sont : (a) TMLR juge si les affirmations sont soutenues par les preuves, pas leur importance ; (b) la checklist NeurIPS demande que les affirmations du résumé correspondent au périmètre réel, avec des objectifs aspirationnels signalés comme non atteints, et promet de ne pas pénaliser l'honnêteté sur les limites ; (c) l'atelier de préenregistrement publie un résultat négatif si l'expérience prévue a été menée de bonne foi.

### Cited Findings
**Atelier de préenregistrement (NeurIPS 2020, 2021 ; ICCV 2019)** — [preregister.science](https://preregister.science/)
- « Pre-registration changes the incentives by _reviewing and accepting a paper before experiments are conducted_. »
- Il « separates hypothesis-generating (exploratory) from hypothesis-testing (confirmatory) research ».
- Étape 1 : les relecteurs vérifient « whether the experiment plan can adequately prove or disprove one (or more) hypotheses ». Étape 2 : la relecture « will aim to ensure that the authors have performed a good-faith attempt to complete the experiments described in their proposal paper ».
- « Some results will be negative, and this is welcomed. » ; « good ideas that do not work will get published, instead of filed away and wastefully replicated. »
- Constat de départ : les relecteurs « can be tempted to prioritise incremental improvements in benchmarks to the detriment of other scientific criteria ».
- Les papiers complets de NeurIPS 2020 sont publiés dans PMLR v148 — [PMLR v148](https://proceedings.mlr.press/v148/)

**TMLR** — [critères d'acceptation TMLR](https://jmlr.org/tmlr/acceptance-criteria.html)
- Critère 1 : « Are the claims made in the submission supported by accurate and convincing evidence? » Critère 2 : l'intérêt pour une partie du public, et la clarté de la communication.
- « novelty of the studied method is not a necessary criterion for acceptance in TMLR ». Un papier ne doit pas être rejeté faute de résultats « significant » ou « impactful » (par exemple un nouvel état de l'art). La page ne mentionne pas explicitement les résultats négatifs.

**ML Reproducibility Challenge (MLRC)** — [reproml.org](https://reproml.org/)
- Les papiers sont d'abord acceptés à TMLR (« Each paper was first accepted at the Transactions on Machine Learning Research (TMLR) »), passent ensuite par « a light compatibility review by the MLRC committee », puis sont présentés comme « an official track of NeurIPS 2026 ».
- La page ne donne aucune consigne de ton ni de formulation pour les échecs de reproduction.

**Checklist NeurIPS** — [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist)
- « The paper's contributions should be clearly stated in the abstract and introduction. »
- « It is fine to include aspirational goals as motivation », à condition d'indiquer clairement que « these goals are not attained by the paper ».
- « Reviewers will be specifically instructed to not penalize honesty concerning limitations. »
- Statistiques : « The factors of variability that the error bars are capturing should be clearly stated » ; préciser « whether the error bar is the standard deviation or the standard error of the mean ».

### Inferences
- Pour un verdict du type « niveau de preuve non atteint sous budget d'erreur fixé à l'avance », le cadre le plus légitime est celui du préenregistrement : la publication tient à l'exécution de bonne foi du plan, pas au signe du résultat. Citer explicitement cette logique en introduction protège contre la lecture « échec du projet ».
- La règle NeurIPS sur les objectifs aspirationnels s'applique directement : l'objectif « déléguer l'autonomie » peut motiver le papier, à condition que le résumé dise noir sur blanc qu'il n'est pas atteint.

### Gaps
- Je n'ai pas trouvé de consignes de formulation propres au track NeurIPS Datasets & Benchmarks pour les résultats négatifs (page non consultée faute de budget).
- Je n'ai trouvé aucune consigne écrite de MLRC sur le ton à adopter envers les auteurs originaux.

## 3. Papiers d'évaluation des LLM et des agents : comment ils disent « pas assez fiable »

### Takeaway
Les papiers d'agents les plus cités annoncent la non-fiabilité par un **chiffre borné associé à un qualificatif** (« succeed on <50% », « pass^8 <25% », « a mere 1.96% »). Ils terminent par une phrase tournée vers l'avenir (« point to the need for… »). Les papiers de fiabilité de 2026 font de l'écart entre capacité et fiabilité la thèse elle-même (« capability gains have only yielded small improvements in reliability »).

### Cited Findings
**τ-bench (Yao et al., 2024)** — [arXiv:2406.12045](https://arxiv.org/abs/2406.12045)
- « We also propose a new metric (pass^k) to evaluate the reliability of agent behavior over multiple trials. Our experiments show that even state-of-the-art function calling agents (like gpt-4o) succeed on <50% of the tasks, and are quite inconsistent (pass^8 <25% in retail). Our findings point to the need for methods that can improve the ability of agents to act consistently and follow rules reliably. »

**τ²-bench (2025)** — [arXiv:2506.07982](https://arxiv.org/abs/2506.07982)
- « our experiments show significant performance drops when agents shift from no-user to dual-control, highlighting the challenges of guiding users. » (formulation qualitative, sans chiffre dans le résumé)

**SWE-bench (Jimenez et al.)** — [arXiv:2310.06770](https://arxiv.org/abs/2310.06770)
- Titre-question : « SWE-bench: Can Language Models Resolve Real-World GitHub Issues? » Résumé : « Our evaluations show that both state-of-the-art proprietary models and our fine-tuned model SWE-Llama can resolve only the simplest issues. The best-performing model, Claude 2, is able to solve a mere $1.96$% of the issues. »

**Analyses critiques de SWE-bench**
- « Are "Solved Issues" in SWE-bench Really Solved Correctly? An Empirical Study » : « Combined, the different weaknesses lead to an inflation of reported resolution rates by 6.2 absolute percent points. Our findings are a call to arms for more robust and reliable evaluation of issue-solving tools. » — [arXiv:2503.15223](https://arxiv.org/abs/2503.15223)
- SWE-Bench+ : « When we filtered out these problematic issues, the resolution rate of SWE-Agent+GPT-4 dropped from 12.47% to 3.97%. » — [arXiv:2410.06992](https://arxiv.org/abs/2410.06992)

**« AI Agents That Matter » (Kapoor, Stroebl, Siegel, Nadgir, Narayanan, 2024)** — [arXiv:2407.01502](https://arxiv.org/abs/2407.01502)
- « Our analysis of current agent benchmarks and evaluation practices reveals several shortcomings that hinder their usefulness in real-world applications. »
- « many agent benchmarks have inadequate holdout sets, and sometimes none at all. This has led to agents that are fragile because they take shortcuts and overfit to the benchmark in various ways. »
- Conclusion : « We hope that the steps we introduce for addressing these shortcomings will spur the development of agents that are useful in the real world and not just accurate on benchmarks. »

**« Establishing Best Practices for Building Rigorous Agentic Benchmarks » (ABC)** — [arXiv:2507.02825](https://arxiv.org/abs/2507.02825)
- « For example, SWE-bench Verified uses insufficient test cases, while TAU-bench counts empty responses as successful. Such issues can lead to under- or overestimation of agents' performance by up to 100% in relative terms. »

**Papiers de fiabilité des agents (2026)**
- « Towards a Science of AI Agent Reliability » (Rabanser et al.) : « While rising accuracy scores on standard benchmarks suggest rapid progress, many agents still continue to fail in practice. » ; « compressing agent behavior into a single success metric obscures critical operational flaws » ; « Grounded in safety-critical engineering… » ; « we find that recent capability gains have only yielded small improvements in reliability. By exposing these persistent limitations… » — [arXiv:2602.16666](https://arxiv.org/abs/2602.16666)
- « Beyond pass@1: A Reliability Science Framework for Long-Horizon LLM Agents » : « Existing benchmarks measure capability -- whether a model succeeds on a single attempt -- but production deployments require reliability -- consistent success across repeated attempts » ; « pass@1 on short tasks is structurally blind to this divergence » ; « These results motivate reliability as a first-class evaluation dimension alongside capability. » — [arXiv:2603.29231](https://arxiv.org/abs/2603.29231)
- « On the Reliability of Computer Use Agents » : « Yet even when the task and model are unchanged, an agent that succeeds once may fail on a repeated execution of the same task. This raises a fundamental question: if an agent can succeed at a task once, what prevents it from doing so reliably? » — [arXiv:2604.17849](https://arxiv.org/abs/2604.17849)
- ReliabilityBench : « Perturbations alone reduce success from 96.9% at $ε=0$ to 88.1% at $ε=0.2$. » ; le benchmark se présente comme « a systematic framework for assessing production readiness of LLM agents ». — [arXiv:2601.06112](https://arxiv.org/abs/2601.06112)

**Résultat négatif empirique très médiatisé : l'essai randomisé de METR** — [arXiv:2507.09089](https://arxiv.org/abs/2507.09089)
- « Surprisingly, we find that allowing AI actually increases completion time by 19%--AI tooling slowed developers down. This slowdown also contradicts predictions from experts in economics (39% shorter) and ML (38% shorter). »
- Réserve explicite : « Although the influence of experimental artifacts cannot be entirely ruled out, the robustness of the slowdown effect across our analyses suggests it is unlikely to primarily be a function of our experimental design. »
- Titre neutre et daté : « Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity ».

### Inferences
- Le registre dominant tient en trois éléments : un **chiffre avec borne** (« <50% », « pass^8 <25% »), un **qualificatif modéré** (« quite inconsistent », « only the simplest », « only… small improvements »), puis une **phrase d'ouverture** (« point to the need for », « motivate… »). C'est directement transposable : « aucun agent n'atteint la borne supérieure de X % d'erreur fixée à l'avance ; l'intervalle observé est [a, b] ».
- METR montre qu'un résultat contraire aux attentes gagne en crédibilité quand il est confronté aux prévisions faites avant l'expérience (« contradicts predictions from experts ») et que la réserve méthodologique figure dans le résumé. C'est l'analogue d'un seuil préenregistré.
- METR date le titre (« Early-2025 AI ») : le constat négatif est borné dans le temps, ce qui évite qu'on le lise comme « l'IA ne marchera jamais ». Ce procédé convient bien à « pas encore au niveau de preuve requis ».

### Gaps
- Je n'ai pas trouvé de papier d'agents qui formule exactement « n'atteint pas le niveau de preuve requis sous un budget d'erreur préenregistré ». La formulation la plus proche reste « production readiness » (ReliabilityBench) et le cadrage « safety-critical engineering » (Rabanser et al.).

## 4. Le préenregistrement en ML : comment les papiers ont rapporté des hypothèses non confirmées

### Takeaway
Les papiers préenregistrés de PMLR v148 rapportent les hypothèses non confirmées avec des formules prudentes et symétriques : « could not conclusively prove », « did not significantly improve », « suggest that… is a difficult optimization problem ». Ils mentionnent souvent le préenregistrement dans le résumé, puis enchaînent sur une piste positive (« showed interesting trends that merit deeper investigation »).

### Cited Findings
- Chandra et al., « On Initial Pools for Deep Active Learning » : « The setup, hypotheses, methodology, and implementation details were evaluated by peer review before experiments were conducted. Experimental results could not conclusively prove that intelligently sampled initial pools are better for AL than random initial pools in the long run, although a Variational Autoencoder-based initial pool sampling strategy showed interesting trends that merit deeper investigation. » — [PMLR v148](https://proceedings.mlr.press/v148/chandra21a.html)
- Martinez et al., « Confronting Domain Shift in Trained Neural Networks » : « While the method as proposed did not significantly improve predictions, our results did show potential for modifications that could improve models' predictions… » — [PMLR v148](https://proceedings.mlr.press/v148/martinez21a.html)
- Palm et al., « Testing the Genomic Bottleneck Hypothesis in Hebbian Meta-Learning » (titre en « Testing the … Hypothesis ») : « The results in this paper suggest that simultaneously learning the Hebbian learning rules and their assignment to synapses is a difficult optimization problem, leading to poor performance in the environments tested. […] How to best implement a "genomic bottleneck" algorithm is thus an important research direction that warrants further investigation. » — [PMLR v148](https://proceedings.mlr.press/v148/palm21a.html)
- Contre-exemple : Alves et al. (« An Empirical Study of the Discreteness Prior in Low-Rank Matrix Completion ») rapportent une confirmation conditionnelle, « capable of retrieving such an underlying… structure with high accuracy if it is present. » — [PMLR v148](https://proceedings.mlr.press/v148/alves21a.html)
- Aucun des titres de v148 n'annonce le résultat négatif. Ils sont neutres ou descriptifs (« On Initial Pools… », « Confronting Domain Shift… », « Testing the … Hypothesis ») — [PMLR v148](https://proceedings.mlr.press/v148/)

### Inferences
- Dans ces papiers, le titre décrit la question et le résumé porte le verdict. « Testing the X Hypothesis » est un modèle sobre et honnête pour un verdict préenregistré mixte.
- La formule « could not conclusively prove… » distingue correctement « pas de preuve suffisante » et « preuve du contraire ». C'est exactement la nuance requise pour « niveau de preuve non atteint ».
- Ces papiers enchaînent presque tous sur une piste positive. Cela atténue le verdict, mais risque d'être lu comme une manière de l'enjoliver ; il vaut mieux étiqueter cette piste comme exploratoire, puisque le préenregistrement sépare confirmatoire et exploratoire.

### Gaps
- Je n'ai trouvé aucune étude de suivi sur l'audience (citations, presse) des papiers préenregistrés de v148. Je ne peux donc pas affirmer qu'ils ont « reçu de l'attention ».
- Les papiers de l'édition 2021 (résultats remis en 2022) n'ont pas été localisés.

## 5. Schémas de titres : questions, « X is not enough », « no evidence », etc. Ce qui est juste et ce qui est racoleur

### Takeaway
Les titres négatifs qui ont marqué sont soit des **questions dont le résumé donne la réponse** (« Do ImageNet Classifiers Generalize to ImageNet? », « Are We Done with MMLU? »), soit des **assertions bornées** (« …Cannot Self-Correct Reasoning Yet », « A Metric Learning Reality Check »). Les assertions absolues, ou les métaphores fortes (« The Illusion of Thinking »), attirent beaucoup d'attention mais aussi des réfutations. Lipton et Steinhardt donnent le cadre normatif : ne pas confondre explication et spéculation, et ne pas employer des termes aux connotations familières.

### Cited Findings
**Questions avec réponse dans le résumé**
- « Are We Done with MMLU? » — le résumé commence par « Maybe not. » — [arXiv:2406.04127](https://arxiv.org/abs/2406.04127)
- « Do ImageNet Classifiers Generalize to ImageNet? » : « We evaluate a broad range of models and find accuracy drops of 3% - 15% on CIFAR-10 and 11% - 14% on ImageNet. » Le résumé ajoute une nuance qui va contre la lecture racoleuse : « However, accuracy gains on the original test sets translate to larger gains on the new test sets. » — [arXiv:1902.10811](https://arxiv.org/abs/1902.10811)
- « SWE-bench: Can Language Models Resolve Real-World GitHub Issues? » — [arXiv:2310.06770](https://arxiv.org/abs/2310.06770)

**Assertions bornées (« yet », « reality check »)**
- « Large Language Models Cannot Self-Correct Reasoning Yet » : « our research indicates that LLMs struggle to self-correct their responses without external feedback, and at times, their performance even degrades after self-correction. » Le titre est catégorique, le résumé modéré (« struggle »), et « Yet » borne le constat dans le temps — [arXiv:2310.01798](https://arxiv.org/abs/2310.01798)
- « A Metric Learning Reality Check » : « We find flaws in the experimental methodology of numerous metric learning papers, and show that the actual improvements over time have been marginal at best. » — [arXiv:2003.08505](https://arxiv.org/abs/2003.08505)
- « LLMs Can't Plan, But Can Help Planning in LLM-Modulo Frameworks » : une assertion négative compensée par une contrepartie positive dans le titre lui-même. C'est un papier de position — [arXiv:2402.01817](https://arxiv.org/abs/2402.01817)
- « GSM-Symbolic: Understanding the Limitations of Mathematical Reasoning in Large Language Models » : titre neutre (« Understanding the Limitations »), mais le résumé avance une hypothèse forte : « We hypothesize that this decline is because current LLMs cannot perform genuine logical reasoning » — [arXiv:2410.05229](https://arxiv.org/abs/2410.05229)

**Titre métaphorique et réfutation**
- « The Illusion of Thinking… » : « we show that LRMs face a complete accuracy collapse beyond certain complexities. » — [arXiv:2506.06941](https://arxiv.org/abs/2506.06941)
- Le « Comment on The Illusion of Thinking » répond : « We demonstrate that their findings primarily reflect experimental design limitations rather than fundamental reasoning failures. » Il signale notamment des instances de River Crossing « mathematically impossible… yet models are scored as failures for not solving these unsolvable problems » — [arXiv:2506.09250](https://arxiv.org/abs/2506.09250)

**Cadre normatif (Lipton et Steinhardt, « Troubling Trends in Machine Learning Scholarship »)** — [arXiv:1807.03341](https://arxiv.org/abs/1807.03341)
- Quatre dérives : « (i) failure to distinguish between explanation and speculation; (ii) failure to identify the sources of empirical gains… (iii) mathiness… and (iv) misuse of language, e.g., by choosing terms of art with colloquial connotations or by overloading established technical terms. »
- Ils relèvent des « often-misaligned incentives between scholarship and short-term measures of success (e.g., bibliometrics, attention, and entrepreneurial opportunity) ».

**Gabarits relevés dans les titres ICBINB 2026** — [ICBINB 2026 papers](https://sites.google.com/view/icbinb-2026/papers)
- « X Fails to Y », « The Limits of X », « X is Not a Free Lunch », « Bigger Is Not Better… », « Random Is Hard to Beat », « When X Fails: Hidden Failure Modes… », « Challenges in… », « Barriers to… ».

### Inferences
- **Formulations justes** : (1) une question dont le résumé donne la réponse chiffrée ; (2) une assertion bornée par un périmètre (« under a pre-registered error budget », « on N tasks ») ou une date (« Yet », « Early-2025 ») ; (3) un titre descriptif (« Testing the X Hypothesis », « Measuring… »).
- **Formulations à risque** : une métaphore absolue (« Illusion »), un verbe sans borne (« cannot »), ou une généralisation à « LLMs » ou « agents » à partir d'un banc limité. Ce sont elles qui attirent les commentaires-réfutations (Illusion of Thinking, et dans une moindre mesure GSM-Symbolic).
- « We find no evidence » ou « insufficient evidence » distingue proprement l'absence de preuve de la preuve d'absence. C'est la formulation la plus fidèle pour un verdict « niveau de preuve non atteint », plus juste que « agents are not reliable » si l'intervalle de confiance chevauche encore le seuil.
- Pour un verdict mixte (certains critères atteints, d'autres non), le modèle « LLMs Can't Plan, But Can Help… » (négatif plus contrepartie dans le titre) et la phrase « However, … » d'ImageNet montrent comment éviter qu'on lise le papier comme un échec total.

### Gaps
- Je n'ai trouvé aucune étude empirique (bibliométrique) qui compare l'audience des titres-questions et des titres assertifs pour les résultats négatifs en ML.
- Aucun papier ML trouvé ne porte « We Find No Evidence » ou « Insufficient Evidence » dans le titre. Ces formulations sont recommandées par inférence, sans exemple sourcé.
- Le statut du « Comment on The Illusion of Thinking » (arXiv:2506.09250) est à vérifier : sa première version aurait eu un caractère en partie parodique, ou un modèle d'IA parmi les auteurs. Je ne l'ai pas confirmé ; à citer avec prudence.
