# τ-bench 2.0 : banking_knowledge (et brièvement intake, sous-ensembles texte gelés) comme source d'actions à enjeu élevé

Convention : [REPO] = lu dans le clone local (commit 033bf08, v2.0.0), chemin relatif à `.../scratchpad/tau2_src/tau2-bench/` ; [PAPIER] = affirmé par l'article arXiv 2603.04370 (https://arxiv.org/html/2603.04370), non revérifié dans le dépôt. Les comptages [REPO] viennent de scripts `python3 -I` qui lisent seulement les JSON (aucun code du banc exécuté).

## 1. Structure des tâches banking_knowledge et contenu de evaluation_criteria

### Takeaway
97 tâches, 1 seul mode de grading dominant : égalité de hash de l'état de la base (DB) après rejeu, pas de NL assertions ni de juge LLM. Les actions attendues existent (nom + arguments exacts) mais ne servent qu'à fabriquer l'état « or » ; il n'y a aucun `compare_args` : il faut donc recalculer soi-même les verdicts par action.

### Cited Findings
- `data/tau2/domains/banking_knowledge/tasks.json` : 97 tâches ; clés par tâche : id, description, user_scenario, initial_state (null), evaluation_criteria, annotations, user_tools, required_documents. evaluation_criteria = `actions`, `reward_basis`, parfois `communicate_info` (24 tâches, tous vides `[]`). [REPO]
- reward_basis : `["DB"]` pour 88 tâches, `["ACTION"]` pour 9 (task_004, 008, 012, 014, 032, 033, 034, 035, 083). COMMUNICATE et NL_ASSERTION ne sont dans aucune reward_basis. [REPO]
- Total 955 actions attendues : 853 `assistant`, 102 `user`. Par outil (assistant) : call_discoverable_agent_tool 456, unlock_discoverable_agent_tool 274, log_verification 81, give_discoverable_user_tool 21, transfer_to_human_agents 13, get_referrals_by_user 4, get_credit_card_accounts_by_user 3, change_user_email 1. Par outil (user) : call_discoverable_user_tool 62, apply_for_credit_card 19, request_human_agent_transfer 13, submit_referral 7, submit_transaction 1. [REPO]
- Actions attendues : champs `name`, `arguments`, `requestor`, `action_id` seulement ; aucun `compare_args` rencontré. Pour `call_discoverable_agent_tool`, `arguments` = `{"agent_tool_name": ..., "arguments": "<chaîne JSON>"}` (la sous-charge est une chaîne, ex. `"{\"transaction_id\": \"txn_a8f1c2d3e403\", \"new_rewards_earned\": \"6300 points\"}"`). [REPO]
- Le grading DB (`src/tau2/evaluator/evaluator_env.py`) : rejoue la trajectoire de l'agent dans un env prédit, rejoue les actions or dans un env or, compare `get_db_hash()` et `get_user_db_hash()` ; reward 1.0 si les deux concordent, sinon 0. Tout ou rien par tâche. [REPO]
- Le grading ACTION (`src/tau2/evaluator/evaluator_action.py`) : reward 1 seulement si toutes les actions or ont un appel correspondant (`all(action_match)`) ; la comparaison `Action.compare_with_tool_call` (src/tau2/data_model/tasks.py l.182-195) teste le nom puis l'égalité des arguments (tous si compare_args=None). Pour un wrapper, l'argument imbriqué `arguments` est une chaîne comparée littéralement : `14.00` vs `14.0` ou un ordre de clés différent donnerait un faux négatif. [REPO]
- Écritures AGENT attendues, définies comme (a) `log_verification`, (b) `change_user_email`, (c) `call_discoverable_agent_tool` dont l'outil sous-jacent est `@is_discoverable_tool(ToolType.WRITE)` : 343 au total (81 + 1 + 261) sur 97 tâches ; 16 tâches sans aucune écriture agent attendue (task_001, 002, 003, 004, 006, 007, 008, 012, 014, 015, 024, 025, 032, 033, 034, 035) ; 33 tâches sans écriture hors `log_verification`. Max d'actions par tâche jusqu'à 34 actions (toutes catégories). [REPO, mon script classe les 48 outils découvrables par regex : 34 WRITE, 11 READ, 3 GENERIC]
- Écritures par outil sous-jacent (nb d'appels attendus / nb de tâches) : file_credit_card_transaction_dispute_4829 46/10 ; open_bank_account_4821 28/19 ; file_debit_card_transaction_dispute_6281 23/8 ; close_debit_card_4721 21/13 ; unfreeze_debit_card_3893 15/6 ; order_debit_card_5739 15/12 ; freeze_debit_card_3892 14/5 ; update_transaction_rewards_3847 10/2 ; order_replacement_credit_card_7291 10/8 ; close_bank_account_7392 9/8 ; apply_checking_account_credit_5829 9/3 ; apply_savings_account_credit_6831 9/5 ; submit_interest_discrepancy_report_7294 9/5 ; log_credit_card_closure_reason_4521 8/6 ; submit_credit_limit_increase_request_7392 6/5 ; pay_credit_card_from_checking_9182 4/4 ; apply_statement_credit_8472 4/4 ; approve_credit_limit_increase_5847 4/4 ; transfer_funds_between_bank_accounts_7291 4/2 ; reset_debit_card_pin_6284 4/3 ; close_credit_card_account_7834 2/2 ; deny_credit_limit_increase_5848 2/2 ; activate_debit_card_8292 2/2 ; clear_debit_card_fraud_alert_4892, apply_credit_card_account_flag_6147, request_temporary_debit_card_limit_increase_8374 1/1 chacun ; log_verification 81/81 ; change_user_email 1/1 (task_005). [REPO]
- Écritures côté utilisateur simulé (hors périmètre « agent ») : apply_for_credit_card 19, submit_referral 7, submit_transaction 1, plus call_discoverable_user_tool 62 (surtout submit_cash_back_dispute_0589 48, get_card_last_4_digits 10, deposit_check_3847 3). `submit_transaction` est donc un outil de l'utilisateur simulé, pas de l'agent. [REPO, tools.py l.4690 dans KnowledgeUserTools]
- Épisode type [PAPIER] : 97 tâches, 18.6 documents requis en moyenne par tâche, 9.52 appels d'outils requis en moyenne (min 1, max 33), 51 outils découvrables et 14 outils agent permanents. Le dépôt compte 48 outils découvrables par regex (écart avec 51 non résolu : voir Gaps).

### Inferences
- Le jeu « actions attendues » est dense (≈3,5 écritures agent/tâche en moyenne, 343/97) mais dominé par `log_verification` (24 %), qui est une écriture d'audit d'identité, pas une action à enjeu.
- Comme le grading officiel est un hash de fin d'épisode, il n'existe pas de verdict par action fourni par le banc : il faut le reconstruire en appariant chaque appel agent (nom sous-jacent + arguments parsés) aux actions or, ce qui est faisable car les arguments or sont complets et déterministes.

### Gaps
- Pas vérifié si certaines actions or sont des écritures « conditionnelles » (ex. freeze puis unfreeze dans task_077, présents tous deux dans l'or) ; l'ordre importe-t-il pour le hash ? Non analysé.

## 2. Outils découvrables : ce que call_discoverable_agent_tool atteint

### Takeaway
C'est un wrapper générique : l'agent doit d'abord `unlock_discoverable_agent_tool` (GENERIC, mutates_state) après lecture de la base de connaissances, puis appeler `call_discoverable_agent_tool(agent_tool_name, arguments=<chaîne JSON>)`. Pour classer par type d'action et par enjeu, il faut déplier le nom sous-jacent et parser la chaîne JSON.

### Cited Findings
- `src/tau2/domains/banking_knowledge/tools.py` l.602-700 : `unlock_discoverable_agent_tool` (GENERIC, mutates_state) ; `call_discoverable_agent_tool` (WRITE) échoue si l'outil est inconnu, non déverrouillé, ou si le JSON est invalide ; il convertit tous les nombres JSON en float (`parse_int=float`). [REPO]
- Journalisation pour l'évaluation : l'appel est enregistré dans la table `agent_discoverable_tools` seulement si l'outil sous-jacent mute l'état OU s'il figure dans la `read_log_allowlist` de la tâche (lectures exigées par l'or). [REPO, tools.py l.686-700 ; CHANGELOG 1.0.1]
- Le wrapper est typé WRITE même pour les lectures sous-jacentes (11 outils découvrables READ comme get_bank_account_transactions_9173, get_all_user_accounts_by_user_id_3847, get_debit_cards_by_account_id_7823). Sur les 456 appels or au wrapper, 261 visent un outil WRITE, 3 un outil GENERIC (initial_transfer_to_human_agent_0218/1822 : 4+1, emergency_credit_bureau_incident_transfer_1114 : 1) et le reste des lectures. [REPO, calcul sur tasks.json]
- Les actions or nomment bien l'outil sous-jacent (`agent_tool_name`) et ses arguments dans la chaîne `arguments` ; aucun appel or sans `agent_tool_name`. [REPO]
- Chaque outil sous-jacent a une docstring qui sert de source de vérité de la description/paramètres. [REPO, tools.py l.717-720]

### Inferences
- Classification recommandée : clé d'action = nom sous-jacent (pas call_discoverable_agent_tool), type = READ/WRITE/GENERIC du décorateur `is_discoverable_tool`, enjeu = table manuelle sur les 27 outils sous-jacents écrits (voir section 3). Appariement : nom sous-jacent + égalité des arguments parsés (dict JSON, nombres normalisés en float).
- Un wrapper unique signifie que les statistiques par type d'outil de premier niveau (wrapper) seraient trompeuses : 456 appels, tous du même « type ».

### Gaps
- Je n'ai pas vérifié si l'agent doit aussi suivre un ordre (unlock avant call) pour le verdict par action ; le hash n'en tient pas compte sauf l'état « déverrouillé » (stocké en mémoire, non lu dans le détail).

## 3. Enjeux de chaque outil d'écriture

### Takeaway
La banque ajoute de vraies actions à enjeu : mouvements d'argent (virement, paiement de carte, crédits, relèvement de limite), fermeture de comptes/cartes, changement de PIN, changement d'e-mail. Mais tout est simulé dans une base JSON, sans notion d'annulation : le niveau d'enjeu est un jugement par nature de l'action, pas une propriété mesurée.

### Cited Findings (code lu, [REPO] `src/tau2/domains/banking_knowledge/tools.py`)
- `change_user_email(user_id, new_email)` (l.424) : met à jour `users.email` sans autre contrôle dans l'outil ; la politique impose la vérification d'identité (2 champs sur 4) via `log_verification` (l.481 : « after you have verified a user by confirming 2 out of 4 identity fields »). Une seule occurrence or (task_005). L'e-mail étant un des quatre champs de vérification, c'est une écriture de sécurité de compte (prise de contrôle possible). [REPO]
- `log_verification` : écrit un enregistrement d'audit dans `verification_history` ; ne modifie pas le compte. Dans task_005 les arguments or sont des valeurs fictives (« 9K2X7M4P1N8Q3R5T6A ») pour plusieurs champs. [REPO]
- Argent : `transfer_funds_between_bank_accounts_7291(source_account_id, destination_account_id, amount)` ; `pay_credit_card_from_checking_9182(user_id, checking_account_id, credit_card_account_id, amount)` ; `apply_statement_credit_8472` ; `apply_checking_account_credit_5829` ; `apply_savings_account_credit_6831` ; `update_transaction_rewards_3847` (points de récompense) ; `approve_credit_limit_increase_5847(new_credit_limit)`. [REPO, arguments d'exemple lus dans tasks.json]
- Sécurité de compte / carte : `reset_debit_card_pin_6284` ; `freeze/unfreeze_debit_card` ; `close_debit_card_4721` ; `close_credit_card_account_7834` ; `close_bank_account_7392` ; `clear_debit_card_fraud_alert_4892` ; `request_temporary_debit_card_limit_increase_8374` ; `order_replacement_credit_card_7291` ; `order_debit_card_5739`. [REPO]
- Litiges et dossiers : `file_credit_card_transaction_dispute_4829`, `file_debit_card_transaction_dispute_6281`, `submit_interest_discrepancy_report_7294`, `submit_credit_limit_increase_request_7392`, `log_credit_card_closure_reason_4521`, `apply_credit_card_account_flag_6147`, `deny_credit_limit_increase_5848`. [REPO]
- `submit_transaction` (l.4690) crée une transaction carte COMPLETED avec points de récompense ; appelé par l'utilisateur simulé (1 occurrence), pas par l'agent. [REPO]
- Réversibilité : les outils lus ne comportent pas d'opération d'annulation générique ; certaines paires existent (freeze/unfreeze). L'enregistrement d'IDs déterministes (`generate_*_id`) fait qu'une répétition identique échoue (« Record ID may already exist ») pour submit_transaction. [REPO, extraits lus]

### Inferences (proposition de stratification, à valider par le coordinateur)
- Haut : transfer_funds (4), pay_credit_card_from_checking (4), apply_statement_credit (4), apply_checking_account_credit (9), apply_savings_account_credit (9), approve_credit_limit_increase (4), reset_debit_card_pin (4), change_user_email (1), close_bank_account (9), close_credit_card_account (2), close_debit_card (21), clear_debit_card_fraud_alert (1), request_temporary_debit_card_limit_increase (1) ≈ 73 actions.
- Moyen : open_bank_account (28), order_debit_card (15), order_replacement_credit_card (10), freeze/unfreeze (29), dossiers de litige (69), update_transaction_rewards (10), approve/deny/submit limite (12), activate_debit_card (2) ≈ 175.
- Bas : log_verification (81), log_credit_card_closure_reason (8), submit_interest_discrepancy_report (9), apply_credit_card_account_flag (1) ≈ 99.
- Les nombres de haut/moyen/bas sont mes décomptes sur la table de la section 1 et mon choix de classement, pas une donnée du banc.

### Gaps
- Les montants et seuils (ex. quels transferts dépassent combien) varient par tâche ; je n'ai pas extrait la distribution des montants.

## 4. Fiabilité du grading et défauts connus

### Takeaway
Grading déterministe (hash DB), donc reproductible, mais exigeant et historiquement défectueux : la version 1.0.1 a corrigé des faux négatifs (lectures supplémentaires qui annulaient le reward) et une valeur or (task_074). Les scores d'avant 1.0.1 ne sont pas comparables. Le hash tout-ou-rien par tâche limite la valeur directe du reward pour des verdicts par action.

### Cited Findings
- CHANGELOG 1.0.1 (2026-07-15) : les corrections de grading font monter les scores « only upward », jusqu'à ~9 points pass^1 selon le modèle (GPT-5.5 xhigh : 37.37 → 46.39 ; GPT-5.4 xhigh : 30.67 → 39.43). Un correctif de donnée (task_074, #374) change la valeur or du remboursement : 8.00 $ → 14.50 $ (franchises ATM). [REPO CHANGELOG.md l.341-420]
- Correctif #329 : `call_discoverable_agent_tool` journalisait toutes les lectures, ce qui faisait entrer une lecture de vérification « prudente » dans le hash DB et mettait le reward à 0 ; maintenant les écritures sont toujours journalisées, les lectures seulement si exigées par l'or (allowlist par tâche). « Accounts for nearly all of the score movement. » [REPO CHANGELOG]
- Correctif #397 : normalisation int/float des arguments numériques (25 vs 25.0) pour les IDs et hash. Correctif #403 : transactions renvoyées en ordre antichronologique (doc_018), sans changement de scores. Correctif #402 : tâches 077-086 (carte perdue/volée) rendues réalisables par l'agent (lectures de listing de comptes ajoutées à l'or). Fuites d'annotations (« SHOULD BE FREE ») retirées des descriptions de frais ATM (12 + 4 lignes). Document Platinum Rewards contradictoire corrigé (#388). [REPO CHANGELOG]
- `tau2 evaluate-trajs --fresh-tasks` re-note des trajectoires avec les tâches actuelles. Dernier commit à l'ancien comportement : `b51a6d6`, tag `pre-v1.0.1`. [REPO CHANGELOG]
- Le hachage des actions or est reconstitué par rejeu de l'or sur la base ; les erreurs d'actions or sont seulement loggées (`logger.warning`), donc une action or qui lève une exception n'invalide pas le calcul. [REPO evaluator_env.py]
- Qualité des tâches [PAPIER] : simulateur utilisateur GPT-5.2 (raisonnement bas), 4 erreurs critiques sur 194 trajectoires annotées ; deux relecteurs indépendants ont audité toutes les tâches et jeux de documents or ; le nombre d'erreurs de définition de tâches trouvées n'est pas rapporté dans la partie lue.
- Contexte de défauts de tâches ailleurs dans τ-bench : le README renvoie à l'article de corrections (https://arxiv.org/abs/2512.07850) pour les « 75+ task fixes » de v1.0 ; je ne l'ai pas lu.

### Inferences
- Pour des verdicts par action, la bonne source n'est pas le reward : c'est l'appariement des écritures or/agent. Les faux négatifs de type « lecture en plus » ne concernent pas les verdicts d'écriture. Il reste un risque de verdict « faux » quand un agent fait une écriture alternative légitime mais absente de l'or (le hash la compte comme erreur).
- Les scores de référence exploitables sont ceux ≥ 1.0.1 ; l'article (mars 2026) précède le correctif de juillet 2026.

### Gaps
- Je n'ai pas lu l'article SABER/τ-bench Verified (2512.07850) ; pas de décompte d'annotations défectueuses pour banking_knowledge hors CHANGELOG. Pas consulté le classement taubench.com.

## 5. Scores rapportés, longueur d'épisode, coût

### Takeaway
Tâches difficiles : ~25 % pass^1 au mieux avec récupération réaliste, et jusqu'à ~40 % avec les documents or (Claude 4.5 Opus) ; épisodes longs (≈9 à 29 appels de recherche/outils, plusieurs centaines de milliers de jetons). Coût élevé pour un enregistrement unique, mais rien n'est chiffré en euros.

### Cited Findings [PAPIER, https://arxiv.org/html/2603.04370 Table 2, pass^1 %, version pré-1.0.1 du grading (article du 4 mars 2026)]
- Claude-4.5-Opus (High) : documents or 39.69 ; text-embedding-3-large 18.30 ; Qwen3-emb-8b 19.59 ; BM25 17.78 ; terminal 24.74. Claude-4.5-Sonnet (High) : 33.76 ; 17.53 ; 17.78 ; 16.75 ; 22.42. GPT-5.2 (High) : 32.73 ; 23.45 ; 24.74 ; 24.48 ; 25.52. Moyennes : 32.18 / 16.88 / 17.11 / 17.04 / 19.20.
- Meilleur pass^4 : 13.40 (GPT-5.2 High, Qwen3-emb-8b) ; Claude-4.5-Opus avec documents or : pass^4 26.80 ; sans connaissance ~2 % pass^1 ; contexte long (KB entière) pic ~12 %.
- KB : 698 documents, 194,562 jetons (cl100k_base), 278.7 jetons/document ; 21 catégories, 71 sujets. Récupération : top 10 documents par `KB_search` ; terminal = shell (grep, cat, find).
- Efficacité : Claude-4.5-Opus ≈ 8.7 appels KB_search par tâche (GPT-5.2 High : 18.5) ; recherches par tâche : dense 9.9-10.1, BM25 11.4, grep 14.5 ; configuration terminal 28.8 appels shell par tâche ; génération totale ≈ 0.7 M (Claude) vs 1.2 M (GPT) sans unité claire ; troncature de contexte 1-3 % des runs (GPT-5.2 High). Aucun coût en dollars ni longueur moyenne en tours rapportés.
- Analyse d'erreurs (§7.2) : interdépendances complexes ~14.5 % ; ordre implicite des sous-tâches ~5 % ; trop de confiance dans l'utilisateur ~4 % ; inefficacité de recherche et hypothèses injustifiées ~23 % ; reste (~53 %) non détaillé dans le texte lu.
- Variantes de récupération disponibles dans le dépôt : no_knowledge, full_kb, golden_retrieval, qwen/openai embeddings (+reranker, +grep), bm25, grep_only, terminal_use(_write), alltools. [REPO src/tau2/domains/banking_knowledge/retrieval.py] Variante par défaut : voir DEFAULT_RETRIEVAL_VARIANT (non lue).
- Le leaderboard v1.0.1 cite des scores banking plus élevés après correctif (GPT-5.5 xhigh 46.39 pass^1). [REPO CHANGELOG]

### Inferences
- Avec ~1 réussite sur 5 à 4, un enregistrement Claude produira beaucoup d'échecs par tâche : bon pour avoir des verdicts négatifs ET positifs par action, mais le reward tout-ou-rien est un mauvais proxy ; le niveau par action est plus généreux (un agent peut réussir 8 écritures sur 9).
- Utiliser `golden_retrieval` (documents requis dans le contexte, `required_documents` par tâche) réduirait fortement la longueur et le coût, au prix de supprimer la difficulté de recherche (39.69 vs ~18-25 pour Opus). C'est un choix de protocole à décider, pas testé ici.
- Les prompts et la KB inline (full_kb ≈ 195 k jetons de contexte par épisode) rendent les épisodes chers ; je n'ai pas de mesure de coût.

### Gaps
- Pas de coût en dollars ni de nombre de tours moyen ; scores Claude plus récents (Opus 4.x/5, Sonnet 4.6+) non cherchés sur taubench.com. Appendix G (pass^2/3) non lu. Seuls les 100 000 premiers caractères de l'article ont été lus (sur 144 867).

## 6. Adéquation aux verdicts exacts par action

### Takeaway
Bonne adéquation pour les écritures (arguments complets, déterministes), à condition de parser la sous-charge JSON du wrapper et de gérer les écritures alternatives ; mauvaise pour le reward fourni (hash de tâche). Le mode texte est disponible : le dépôt cite un `--retrieval-config` ; je n'ai pas vérifié l'exécution.

### Cited Findings
- `data/tau2/benchmarks/banking.json` : `benchmark_version: voice-v2-banking`, `mode: voice`, 6 langues, sous-ensemble `banking_knowledge_97` (census, stratifier none, seed 42, créé 2026-10-16). Il n'existe pas de benchmark banking en mode texte gelé ; `text.json` (text-v1) ne contient que airline_50, retail_50, telecom_50. [REPO]
- README : « `banking_knowledge` in voice. The retrieval domain from v1.0 now also runs as a custom voice run », ce qui implique l'exécution texte comme domaine ordinaire depuis v1.0 (domaine listé dans `Available domains`) ; installation avec `uv sync --extra knowledge`. [REPO README.md l.32, 134, 163]
- Chaque action or banque `requestor=assistant` ou `user` : pour des verdicts d'agent, filtrer `requestor == "assistant"` (853 actions, dont 343 écritures). [REPO]

### Inferences
- Appariement proposé : pour chaque appel agent d'écriture (log_verification, change_user_email, ou sous-jacent WRITE du wrapper), verdict = présence d'une action or de même nom sous-jacent avec arguments parsés égaux ; « écriture hors or » = faux (ou à juger séparément si l'or l'omet à tort).
- Risque d'échantillon : 73 actions à enjeu élevé sur 97 tâches, très concentrées (close_debit_card 21 ; crédits ; paiements) ; seulement 1 change_user_email, 2 close_credit_card_account : peu de données par type à enjeu rare.

### Gaps
- Non vérifié : compatibilité texte réelle sans extra voice, dépendances des embeddings (clés payantes pour openai/qwen ? bm25_grep, grep_only, terminal_use semblent sans embeddings payants mais non confirmé).

## 7. Domaine intake (τ-Entity), bref

### Takeaway
200 tâches, une écriture `submit_fields` par tâche, enjeu faible (saisie d'enregistrements clinique/garage/hôtel). Exécutable en texte seulement avec la stratégie `scaffolded`. Peu d'intérêt pour des actions à enjeu.

### Cited Findings
- `data/tau2/domains/intake/split_tasks.json` : split base = 200 tâches (ex. `intake_person_names_easy_01`) ; pas de tasks.json ; les tâches sont générées (`src/tau2/domains/intake/tasks/generator.py`). `task_subsets/intake_200.json` : census, créé 2026-10-16. [REPO]
- docs/elicitation.md : 10 familles d'entités × 2 niveaux × 10 tâches ; un champ manquant par tâche ; reward = base finale vs base produite par rejeu de la soumission or ; texte « requires `--elicitation-strategy scaffolded` » ; stratégie agent_directed par défaut = voix seulement. [REPO]
- Outil WRITE : `submit_fields(record_id, fields, confirmed_with_user)` ; `log_capture` et `end_call` sont GENERIC ; `get_today` READ. [REPO src/tau2/domains/intake/tools.py]

### Inferences
- Un seul type d'action (donc un seul « type » pour le suivi par type), une écriture par tâche : ne répond pas à la question des actions à enjeu élevé ; sert au mieux de contrôle à enjeu bas.

### Gaps
- Contenu `evaluation_criteria` des tâches intake non lu (tâches générées à l'exécution) ; non vérifié l'exécution texte.

## 8. Sous-ensembles texte gelés (text-v1)

### Takeaway
`text.json` (text-v1, revision regional-release-data-v16) référence airline_50, retail_50, telecom_50. Retail et telecom sont tirés par échantillonnage stratifié (seed 42) sur les 114 tâches de base ; les « 50 remplacements relus » sont exactement ces 50 tâches, et leurs critères d'évaluation sont identiques à `domains/*/tasks.json`.

### Cited Findings
- airline_50 : census des 50 tâches de base (stratifier none) ; retail_50 : stratified, stratifier `write_profile` (type d'écriture/nombre d'écritures), 19 strates (ex. exchange_delivered_order_items/1 : 20 tâches en base, 9 tirées ; read_only/0 : 10 tâches, 4 tirées), cadre 114, seed 42, créé 2026-07-27 ; telecom_50 : stratified, stratifier `issue_persona`, 9 strates en cadre 114 (ex. mms_issue/easy 15→7, mms_issue/hard 17→8, mms_issue/none 17→7). retail_114 et telecom_114 : census, créés 2026-10-09, git_commit 986f751. banking_knowledge_97 et intake_200 : census, créés 2026-10-16, git_commit 9a5bc85. [REPO data/tau2/task_subsets/*.json]
- Les remplacements sont dans `data/tau2/multilingual/en/retail_tasks_en.json` et `telecom_tasks_en.json` (50 tâches chacun, mêmes IDs, tous inclus dans retail_50/telecom_50). Mon comparaison avec `domains/<d>/tasks.json` : `evaluation_criteria` identiques (0 différence) et `actions` identiques (0) pour les 50 + 50 ; `user_scenario` diffère pour les 100 ; `initial_state` diffère pour les 50 telecom (noms de client distincts du « John Smith » partagé, avec dossiers correspondants), identique pour retail ; `description` identique. [REPO, script python3 -I sur les JSON]
- docs/language-packs.md l.158-161 : retail et telecom en anglais diffèrent du registre « only by the retail "Name details" caller block and the telecom caller-name swap ». CHANGELOG « Upgrading from 1.x » : « English pack replaces 50 of the 114 base tasks per domain with same-ID versions ». [REPO]
- Dans 2.0, les contrôles de communication sont jugés par LLM sémantique, juge NL gpt-5.4-mini-2026-03-17 (CHANGELOG ligne ~99-115) : non concerné par un verdict d'écriture exact. [REPO README]
- Les décomptes déjà vérifiés par le coordinateur (airline 49 écritures, retail 176, telecom 103 base / 2 256 complet) ne sont pas recalculés ici.

### Inferences
- Rejouer sur les 114 tâches de base avec `domains/*/tasks.json` donne les mêmes actions or que les 50 remplacées ; les seules différences à connaître sont le texte du scénario utilisateur (et l'état initial telecom).

### Gaps
- Ensemble exact des 50 IDs par domaine non recopié ici (dans `task_subsets/*_50.json` champ `task_ids`).

## Synthèse pour la décision du coordinateur
- banking_knowledge ajoute des actions réelles à enjeu élevé (argent, sécurité de carte, e-mail), 73 actions environ sur 343 écritures agent, mais seulement 97 tâches et ~25 % de réussite des meilleurs modèles dans l'article ; coût d'épisode élevé avec récupération complète.
- Verdicts exacts possibles par reconstruction (nom sous-jacent + arguments JSON parsés) ; ne pas utiliser le reward de tâche comme verdict.
- Points à décider : variante de récupération (golden_retrieval moins chère, moins réaliste), prise en compte des écritures alternatives hors or, rareté de certains types.
