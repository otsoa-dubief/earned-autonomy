# Bancs d'essai et bacs à sable existants pour agents LLM à outils (état au 2026-11-04)

Méthode : lecture des pages GitHub, de l'API GitHub (champ `pushed_at`) et des résumés arXiv via un outil de lecture qui renvoie un extrait. Les pages README n'affichent pas toujours les chiffres : ce qui n'est pas dans la page est classé en Gaps, pas deviné. Les "Inferences" sont de moi.

## Q1. Quels environnements existent, et leurs caractéristiques (tâches, pièges, notation, rejeux, journal, licence, maintenance, installation, Claude)

### Takeaway
Trois familles utiles. (a) Bancs à état déterministe avec tâches de sécurité : AgentDojo (messagerie/agenda/fichiers, injections), τ²-bench (politiques de service client, notation par état de base), AppWorld (état + dégâts collatéraux). (b) Bancs riches à services réels mais conçus pour une exécution lourde : TheAgentCompany (repo figé depuis nov. 2025), OpenAgentSafety (mêmes services, avec cas adversariaux), OSWorld/OS-Harm (écran). (c) Bancs de sécurité à juge LLM ou à outils émulés (ToolEmu, Agent-SafetyBench, ST-WebAgentBench) : moins fiables pour un décompte automatique. Les nouveautés 2026 (AgentS4D, INFUSE) sont prometteuses mais le code n'est pas confirmé publié pour AgentS4D.

### Cited Findings

Tableau récapitulatif (dates = champ `pushed_at` de l'API GitHub lu le 2026-11-04, sauf mention) :

| Banc | Domaine / outils | Tâches | Pièges / sécurité | Notation | Licence | Dernier push / tickets ouverts | Installation |
|---|---|---|---|---|---|---|---|
| AgentDojo | Agents à outils : client mail, e-banking, voyages (par l'abstract) | 97 tâches utilisateur, 629 cas de sécurité | Injections de prompt indirectes, attaques et défenses | Vérifs d'état (voir Gaps pour détail) | MIT | 2026-06-02 / 98 | `pip install agentdojo` |
| τ²-bench (τ³) | airline, retail, telecom, banking_knowledge, + voix, intake | 50 tâches/domaine en text-v1 (6 langues), voice-v1 : 50 / 114 / 114 | Politiques de domaine à respecter | Comparaison d'état + actions attendues ; juges séparés | MIT | 2026-11-02 / 340 | `uv`, Python 3.12-3.13, LiteLLM |
| TheAgentCompany | Entreprise simulée : GitLab, Plane, ownCloud, RocketChat | 175 images de tâches | Non mentionné dans le README | Résultat + sous-points ; évaluateurs déterministes ET LLM | MIT | 2025-11-17 / 28 | Docker Compose, 30+ Go, réseau hôte |
| AppWorld | 9 applis (Amazon, Spotify, Venmo...), 457 API | Non indiqué dans la page (splits train/dev/test_normal/test_challenge) | "Dégâts collatéraux" vérifiés | Tests unitaires sur état de la base | Apache-2.0 | 2026-09-04 / 16 | `pip install appworld`, données à télécharger ; Docker facultatif |
| OSWorld | Bureau Ubuntu/Windows/macOS en VM | Non indiqué dans la page | Aucun (OSWorld lui-même) | Évaluateurs par exécution | Apache-2.0 | 2026-11-02 / 170 | VMware/VirtualBox/Docker+KVM/AWS/Modal/Daytona |
| OS-Harm | Sur OSWorld : mail, éditeur de code, navigateur | 150 | Mésusage voulu, injection, mauvaise conduite du modèle | Juge automatique (accord F1 0,76 / 0,79 avec humains) | à vérifier | non lu | comme OSWorld |
| WorkArena | ServiceNow via BrowserGym | L1 : 33 tâches atomiques (19 912 instances) ; L2 (++) : 682 | Aucun | `validate()` -> reward | NOASSERTION (fichier LICENSE non lu) | 2026-09-28 / 27 | Accès à une instance via jeu de données Hugging Face à accès contrôlé |
| ST-WebAgentBench | Web (apps WebArena) | 222 tâches avec politiques | 6 dimensions de fiabilité (ex. consentement, robustesse) | CuP (achevé sous politique), Risk Ratio | NOASSERTION | 2026-03-12 / 2 | non lu |
| Agent-SafetyBench | 349 environnements | 2 000 cas | 8 catégories de risque, 10 modes de défaillance | Modèle-juge (détail non lu) | MIT | 2025-08-11 / 2 | non lu |
| ToolEmu | 36 outils émulés par un LLM | 144 cas | Outils à haut risque | Évaluateur LLM (68,8 % des échecs signalés jugés valides par des humains) | Apache-2.0 | 2024-03-22 / 2 | non lu |
| OpenAgentSafety | Navigateur, exécution de code, fichiers, bash, messagerie | plus de 350 tâches multi-tours | Intentions bénignes et adverses | Règles + juge LLM | MIT (dépôt `sani903/OpenAgentSafety`, à confirmer que c'est le bon dépôt) | 2026-08-10 / 0 | non lu |
| INFUSE | Agent bash dans Docker | 40 tâches longues, 56 attaques en 5 catégories | Exfiltration, manipulation de données, élévation de privilèges, corruption, chaîne d'approvisionnement | ASR-H heuristique sur artefacts + ASR-L juge LLM ; tests bash pour l'utilité | MIT (code), CC-BY-4.0 (trajectoires) | non lu | Docker |
| AgentS4D | Espace de travail synthétique : web, mail, messagerie, API factices, dépôt | 328 cas dérivés de 76 tâches | 6 sources de risque, 6 stratégies, 9 types de dommage | Prédicats/signaux côté hôte ; Sûr / Non sûr / Non concluant | non précisée | code non confirmé publié | conteneur par run |

Détails sourcés par banc :

- AgentDojo : 97 tâches réalistes (gestion de mail, e-banking, réservations) et 629 cas de sécurité ; arXiv 2406.13352, v1 19 juin 2024, version courante v3 du 24 nov. 2024 — [arXiv](https://arxiv.org/abs/2406.13352). Dépôt MIT, 987 étoiles, non archivé, `pushed_at` 2026-06-02 (mise à jour du dépôt le 2026-11-04), 98 tickets ouverts d'après l'API — [API GitHub](https://api.github.com/repos/ethz-spylab/agentdojo). Le README montre un CLI `benchmark` avec choix de suite, tâches, modèle, défense (`tool_filter`), attaque (`tool_knowledge`) ; la doc renvoie à des pages pour créer ses propres pipelines, modèles, attaques et suites de tâches — [doc](https://agentdojo.spylab.ai/). La doc cite l'usage par les AISI américain et britannique pour montrer la vulnérabilité de Claude 3.5 Sonnet (nouveau) — [doc](https://agentdojo.spylab.ai/). L'enquête 2026 sur les bancs de sécurité le classe au niveau "action" de granularité — [arXiv 2605.16282](https://arxiv.org/html/2605.16282v1).
- τ-bench / τ²-bench : τ-bench (arXiv 2406.12045, 17 juin 2024, v1 seule) introduit pass^k ; la notation compare l'état de la base de données en fin de conversation à l'état-objectif annoté ; pass^8 < 25 % en retail pour gpt-4o — [arXiv](https://arxiv.org/abs/2406.12045). τ²-bench : domaines airline, retail, telecom, banking_knowledge, mock, intake ; v1.0.1 du 2026-07-15 corrige la notation de banking_knowledge (résultats antérieurs non comparables) ; v2.0 (τ-i18n) ajoute 6 langues ; résultats dans `data/simulations/`, visionneuse `tau2 view`, reprise possible ; LiteLLM donc tout fournisseur ; MIT ; 333 commits — [GitHub](https://github.com/sierra-research/tau2-bench). `pushed_at` 2026-11-02, 340 tickets ouverts, 2 393 étoiles — [API GitHub](https://api.github.com/repos/sierra-research/tau2-bench).
- TheAgentCompany : 175 tâches, services GitLab/Plane/ownCloud/RocketChat à données pré-chargées ; notation par résultat + sous-points, évaluateurs déterministes et LLM ; Docker + 30 Go ; passe par OpenHands, LiteLLM pour modèle agent et modèle d'environnement ; arXiv 2412.14161 — [GitHub](https://github.com/TheAgentCompany/TheAgentCompany). `pushed_at` 2025-11-17 (donc aucun commit depuis près d'un an), 28 tickets — [API GitHub](https://api.github.com/repos/TheAgentCompany/TheAgentCompany).
- AppWorld : 9 applis du quotidien, 457 API, plus de 100 tables, environ 100 personnes simulées ; tests unitaires sur l'état de la base "sans dégâts collatéraux" ; journaux par run : `logs/api_calls.jsonl`, `logs/environment_io.md`, fichiers de changements par appli `dbs/*.jsonl`, rapports ; Apache-2.0 ; configs de modèles jusqu'à fin 2025 dont Claude Sonnet 4.5 ; serveur et client MCP — [GitHub](https://github.com/StonyBrookNLP/appworld). `pushed_at` 2026-09-04, 16 tickets — [API GitHub](https://api.github.com/repos/StonyBrookNLP/appworld).
- OSWorld : OSWorld-Verified publié le 2025-07-28 (corrections, AWS, parallélisation) ; fournisseurs VMware, VirtualBox, Docker+KVM, Modal, Daytona, AWS ; le dépôt mentionne OSWorld-MCP ; aucune tâche de sécurité dans OSWorld lui-même — [GitHub](https://github.com/xlang-ai/OSWorld). `pushed_at` 2026-11-02, 170 tickets, 3 251 étoiles — [API GitHub](https://api.github.com/repos/xlang-ai/OSWorld).
- OS-Harm : 150 tâches construites sur OSWorld (mail, éditeur de code, navigateur) ; trois catégories : mésusage, injection de prompt, mauvaise conduite ; juge automatique ; testés : o4-mini, Claude 3.7 Sonnet, Gemini 2.5 Pro ; NeurIPS 2025 D&B (spotlight) ; v1 17 juin 2025, v2 29 oct. 2025 — [arXiv 2506.14866](https://arxiv.org/abs/2506.14866).
- WorkArena : L1 33 tâches atomiques / 19 912 instances, L2 (WorkArena++) 682 tâches ; accès via jeu de données Hugging Face à accès contrôlé ; `validate()` renvoie la récompense ; passe par BrowserGym/AgentLab — [GitHub](https://github.com/ServiceNow/WorkArena). `pushed_at` 2026-09-28 — [API GitHub](https://api.github.com/repos/ServiceNow/WorkArena).
- ST-WebAgentBench : 222 tâches avec politiques, 6 dimensions, CuP et Risk Ratio ; la complétion moyenne sous politique est inférieure aux deux tiers de la complétion nominale ; ICLR 2026 ; v7 du 4 juin 2026 — [arXiv](https://arxiv.org/abs/2410.06703). Dépôt `segev-shlomov/ST-WebAgentBench`, `pushed_at` 2026-03-12, 31 étoiles, licence NOASSERTION — [API GitHub](https://api.github.com/repos/segev-shlomov/ST-WebAgentBench).
- Agent-SafetyBench : 2 000 cas, 349 environnements, 8 catégories de risque, 10 modes de défaillance ; aucun des 16 agents testés au-dessus de 60 % de score de sécurité ; v1 19 déc. 2024, v2 20 mai 2025 — [arXiv](https://arxiv.org/abs/2412.14470). Dépôt `thu-coai/Agent-SafetyBench`, MIT, `pushed_at` 2025-08-11 — [API GitHub](https://api.github.com/repos/thu-coai/Agent-SafetyBench).
- ToolEmu : 144 cas, 36 outils à enjeu élevé émulés par un LLM, évaluateur de sécurité LLM ; même le meilleur agent échoue 23,9 % du temps selon l'évaluateur ; v1 25 sept. 2023, v2 17 mai 2024 — [arXiv](https://arxiv.org/abs/2309.15817). Dépôt `ryoungj/ToolEmu`, dernier push 2024-03-22 — [API GitHub](https://api.github.com/repos/ryoungj/ToolEmu).
- OpenAgentSafety : plus de 350 tâches multi-tours, vrais outils (navigateur, exécution de code, fichiers, bash, messagerie) ; règles + juge LLM ; v1 8 juillet 2025, v2 16 fév. 2026 ; ICLR 2026 — [arXiv](https://arxiv.org/abs/2507.06134). Le résumé arXiv ne donne pas de lien de dépôt ; le dépôt `sani903/OpenAgentSafety` (MIT, push 2026-08-10, 39 étoiles) a été trouvé par essai d'URL, son identité avec le banc de l'article n'est pas vérifiée — [API GitHub](https://api.github.com/repos/sani903/OpenAgentSafety).
- INFUSE (arXiv 2610.20776, oct. 2026) : 40 tâches longues, 56 attaques (11 exfiltration, 13 manipulation de données, 12 élévation de privilèges, 10 corruption, 10 chaîne d'approvisionnement) ; Docker à système de fichiers racine en lecture seule et sortie réseau restreinte ; trace JSONL typée de chaque action ; transfert testé vers Claude Code et Codex CLI ; code MIT sur `github.com/judydnguyen/infuse`, trajectoires CC-BY-4.0 — [arXiv HTML](https://arxiv.org/html/2610.20776v1).
- AgentS4D (arXiv 2607.27294, juillet 2026) : 328 cas à risque injecté dérivés de 76 tâches Workspace-Bench ; 4 harnais (Hermes, OpenClaw, Claude Code, Codex) x 5 modèles = 20 configurations, 6 560 runs ; fraîche conteneur par run avec services contrôlés web/mail/messagerie/API factices ; vérificateur côté hôte caché à l'agent ; verdicts par run, pas par étape ; le texte arXiv ne contient pas de code ni de licence — [arXiv HTML](https://arxiv.org/html/2607.27294).
- Enquête sur 40 bancs de sécurité (arXiv 2605.16282, mai 2026) : pas de concordance de classement entre AgentHarm, AgentDojo, InjecAgent et ODCV-Bench sur 12 modèles (W de Kendall = 0,10, p = 0,94) — [arXiv HTML](https://arxiv.org/html/2605.16282v1).
- Autres titres 2026 vus en résultats de recherche sans lecture : LivePI (2605.17986), SABER (2606.01317), SkillSafetyBench (2605.12015), GuardianAgentBench (2607.20982), NetInjectBench (2607.10490), MCP-SafetyBench, WASP — [recherche](https://arxiv.org/pdf/2605.17986), [GuardianAgentBench](https://arxiv.org/pdf/2607.20982).

### Inferences
- Compatibilité Claude : tous les bancs à LiteLLM (τ²-bench, TheAgentCompany via OpenHands) ou à pipeline modulaire (AgentDojo, AppWorld avec configs Claude Sonnet 4.5) acceptent Claude sans difficulté. Pour AgentDojo et ToolEmu je n'ai pas vu le détail dans les pages lues ; d'après le résultat des AISI, Claude y a déjà été testé.
- Maintenance : actifs en 2026 = τ²-bench, OSWorld, AppWorld, WorkArena, AgentDojo (dernier push juin 2026, pas de release déclarée sur la page). Dormants = TheAgentCompany (nov. 2025), ToolEmu (mars 2024), Agent-SafetyBench (août 2025). Le nombre de tickets ouverts est élevé sur τ²-bench (340) et OSWorld (170), ce qui reflète l'activité autant que la dette.
- Le fait que la corrélation entre bancs soit quasi nulle (W = 0,10) plaide pour ne pas dépendre d'un banc public unique pour juger un agent : un banc maison à tâches et pièges maîtrisés est plus défendable pour l'expérience.

### Gaps
- Nombre de tâches d'injection d'AgentDojo, liste des suites (la connaissance antérieure parle de workspace, slack, banking, travel mais ce n'est pas confirmé par les pages lues) et support officiel d'Anthropic dans le code : non lus (README et doc n'affichent pas ces éléments).
- Nombre exact de tâches OSWorld et AppWorld, licence de WorkArena, installation et journal de ST-WebAgentBench, Agent-SafetyBench, ToolEmu, OpenAgentSafety : non lus.
- Les versions de τ-bench d'origine (dépôt `sierra-research/tau-bench`) n'ont pas été consultées ; seule τ²-bench l'a été.
- Dates de dernier commit : j'ai le `pushed_at`, qui peut inclure des branches autres que la principale.

## Q2. Lesquels collent au travail de back-office d'une petite entreprise (mail, agenda, documents, registres, publication, fusion de code, délégation) ?

### Takeaway
Aucun banc ne couvre tout. Le plus proche pour mail + agenda + fichiers est AgentDojo (suite d'espace de travail) ; pour registres internes et état de base, τ²-bench et AppWorld ; pour GitLab/chat/documents partagés, TheAgentCompany et OpenAgentSafety ; pour contrôle d'écran, OSWorld/OS-Harm. Publication web, fusion de code avec relecture, et délégation à des sous-agents ne sont couvertes proprement par aucun d'eux.

### Cited Findings
- AgentDojo : gestion de mail, e-banking, réservation de voyages — [arXiv](https://arxiv.org/abs/2406.13352).
- τ²-bench : domaines de service client avec politiques ; notation par état de base — [GitHub](https://github.com/sierra-research/tau2-bench), [arXiv τ-bench](https://arxiv.org/abs/2406.12045).
- AppWorld : 9 applis, 457 API, état de base et dégâts collatéraux — [GitHub](https://github.com/StonyBrookNLP/appworld).
- TheAgentCompany : GitLab (code), Plane (tickets), ownCloud (documents), RocketChat (chat interne) — [GitHub](https://github.com/TheAgentCompany/TheAgentCompany).
- OpenAgentSafety : navigateur, code, fichiers, bash, messagerie, avec intentions adverses — [arXiv](https://arxiv.org/abs/2507.06134).
- OS-Harm : mail, éditeur de code, navigateur sur OSWorld — [arXiv](https://arxiv.org/abs/2506.14866).
- AgentS4D : conteneur avec web, mail, messagerie, API factices, dépôt par run ; pas d'agenda dans le texte lu ; les harnais testés incluent Claude Code — [arXiv HTML](https://arxiv.org/html/2607.27294).
- INFUSE : tâches de gestion de fichiers/données, déploiement, développement avec exfiltration et manipulation — [arXiv HTML](https://arxiv.org/html/2610.20776v1).

### Inferences
- Mail à des tiers : AgentDojo, AppWorld (si la messagerie y figure, non confirmé), AgentS4D.
- Agenda : AgentDojo (suite d'espace de travail, d'après ma connaissance antérieure, non confirmée par les pages lues).
- Documents / registres internes : ownCloud + Plane (TheAgentCompany), tables d'AppWorld, base de τ²-bench.
- Fusion de code : GitLab de TheAgentCompany/OpenAgentSafety donne une base, mais la notion de "fusion sans relecture" devrait être ajoutée par vous.
- Publication et délégation à des sous-agents : à construire. La publication peut se simuler comme un outil `publish_post` avec effet visible dans l'état ; la délégation comme un outil `delegate_task` dont le sous-agent est un script.
- Contrôle d'écran : OSWorld + OS-Harm, mais VM lourdes ; pas adapté à des milliers d'épisodes sans AWS.

### Gaps
- Je n'ai pas confirmé la présence d'un outil agenda dans AppWorld, TheAgentCompany ou OpenAgentSafety.
- Aucun banc trouvé pour "publication" ni "délégation à sous-agents" avec notation automatique ; absence non démontrée, seulement non trouvée dans ce que j'ai lu.

## Q3. Lesquels permettent de définir des types d'action à enjeux et réversibilité différents, pour compter les preuves par type d'action ?

### Takeaway
Les environnements dont les outils sont du code Python que vous contrôlez et dont l'état est observable (AgentDojo, AppWorld, τ²-bench) sont les seuls où l'on peut étiqueter chaque outil avec un type, un enjeu et une réversibilité sans toucher au banc. Ceux à juge LLM ou à outils émulés (ToolEmu, Agent-SafetyBench) ne le permettent qu'au prix d'une confiance moindre.

### Cited Findings
- AgentDojo documente la création de ses propres suites de tâches, pipelines, défenses et attaques — [doc](https://agentdojo.spylab.ai/). L'enquête 2026 classe AgentDojo et InjecAgent comme niveau "action" — [arXiv 2605.16282](https://arxiv.org/html/2605.16282v1).
- AppWorld enregistre chaque appel d'API (`api_calls.jsonl`) et chaque changement de base par appli (`dbs/*.jsonl`) — [GitHub](https://github.com/StonyBrookNLP/appworld).
- τ²-bench vérifie `evaluation_criteria.actions` selon `reward_basis` — [GitHub](https://github.com/sierra-research/tau2-bench).
- INFUSE écrit chaque action et observation dans une trace JSONL typée — [arXiv HTML](https://arxiv.org/html/2610.20776v1).
- ToolEmu émule les outils par un LLM, donc l'état n'est pas réel — [arXiv](https://arxiv.org/abs/2309.15817).
- L'enquête 2026 n'a pas codé la réversibilité par banc ; elle n'en discute que sur le principe — [arXiv 2605.16282](https://arxiv.org/html/2605.16282v1).

### Inferences
- Aucun banc lu ne fournit un étiquetage enjeu/réversibilité prêt à l'emploi : il faudra une table maison `outil -> type d'action, enjeu, réversible ?` appliquée aux journaux. C'est faisable sur AgentDojo/AppWorld/τ²-bench car les outils sont des fonctions Python nommées.
- Exemples de correspondance : lecture de fichier = enjeu nul réversible ; envoi de mail à une adresse externe = enjeu moyen irréversible ; paiement (Venmo d'AppWorld, virement d'AgentDojo/e-banking) = enjeu élevé irréversible. Ces correspondances sont mon proposition, pas un fait des bancs.

### Gaps
- Je n'ai pas trouvé de banc qui annote déjà la réversibilité.

## Q4. Succès et dommage sont-ils attribuables par action ou seulement par tâche ? Comment dériver des verdicts par action ?

### Takeaway
Par défaut, ces bancs notent par run ou par tâche (état final). Les journaux d'appels existent dans AppWorld, INFUSE et τ²-bench, ce qui permet de reconstruire des verdicts par action par règles, mais il faut les écrire vous-même.

### Cited Findings
- AgentS4D : verdict par run, pas par étape ; les étiquettes de point de contrôle K1-K7 sont diagnostiques et ne changent pas le verdict — [arXiv HTML](https://arxiv.org/html/2607.27294).
- AppWorld : journaux d'appels et diffs de base par appli ; la notation d'état vérifie les dégâts collatéraux — [GitHub](https://github.com/StonyBrookNLP/appworld).
- τ-bench : notation par comparaison d'état final — [arXiv](https://arxiv.org/abs/2406.12045).
- ST-WebAgentBench : CuP ne crédite que les complétions respectant toutes les politiques ; Risk Ratio compte les violations par dimension — [arXiv](https://arxiv.org/abs/2410.06703).
- INFUSE : ASR-H par artefacts concrets, ASR-L par juge LLM, avec validation humaine du juge — [arXiv HTML](https://arxiv.org/html/2610.20776v1).
- L'enquête 2026 distingue les niveaux action / résultat / motif / disposition — [arXiv 2605.16282](https://arxiv.org/html/2605.16282v1).

### Inferences
Pistes de dérivation (de moi, non éprouvées) :
1. Verdict d'action par règle sur le journal : pour chaque appel d'outil, un prédicat (destinataire externe ? montant ? cible hors périmètre ? injection présente dans le contexte récent ?). L'action est "dangereuse" si le prédicat fire.
2. Verdict d'action par diff d'état : comparer la base avant/après chaque appel (possible avec AppWorld qui écrit déjà des diffs par appli). Une modification hors du périmètre de la tâche = dégât collatéral par action.
3. Verdict de succès par action : succès si l'effet attendu est présent dans l'état final ET qu'aucune règle de danger n'a fire sur l'action ; sinon échec.
4. Pièges rejoués : une erreur passée devient un cas de test avec prédicat déterministe, pour éviter tout juge LLM.
5. Pour ToolEmu/INFUSE-L, ne pas compter les verdicts de juge LLM comme preuves de promotion sans validation humaine.

### Gaps
- Je n'ai trouvé aucun banc qui publie des verdicts par action prêts à l'emploi.
- Le support de pass^k : τ-bench le définit ; je n'ai pas confirmé dans le README de τ²-bench, AgentDojo ou AppWorld qu'ils calculent pass^k (la page τ²-bench consultée ne le mentionne pas) ; la répétition de runs par script reste possible mais n'est pas documentée ici.
- Coût d'un épisode et temps d'exécution : non mesurés.
