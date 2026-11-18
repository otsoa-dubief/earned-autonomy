# Installation des bancs pour le pilote « autonomie méritée »

Écrit le 2026-11-04. Rien de payant n'a été lancé : aucune clé dans l'environnement, aucun appel réseau vers un fournisseur de modèle.

*Chemins (09/11, audit avant le gel, O10)* : les commandes utilisent `RACINE`, la racine du dépôt (`RACINE=$(git rev-parse --show-toplevel)`), au lieu d'un chemin propre à la machine d'Otsoa.

## 1. Ce qui est installé

| Banc | Dépôt (commit) | Dossier | Environnement |
|---|---|---|---|
| τ-bench 2.0 (tau2) | sierra-research/tau2-bench (033bf08) | `externe/tau2-bench/` | `.venv` (Python 3.12, `uv sync` puis `uv sync --extra knowledge`, LiteLLM 1.81.11) |
| WorkBench | olly-styles/WorkBench (49c7dfd) | `externe/WorkBench/` | `.venv` (`uv sync`) |

- `externe/` est ajouté à `.gitignore`.
- `uv` 0.11.2 déjà présent (`~/.local/bin/uv`). Rien d'installé en global, rien via brew.
- Dossiers d'essai créés sous `externe/` (ignorés par git) : `externe/workbench-run/` (sorties WorkBench séparées des résultats publiés), et dans `externe/tau2-bench/data/simulations/` les parties factices `essai-blanc-*`. À supprimer avant le vrai pilote si on veut un dossier propre.
- Deux petits pilotes ajoutés dans `banc/` : `tau2_sans_juge.py` et `workbench_pilote.py` (raisons plus bas).

## 2. Règle de lancement (toujours)

Pour un essai à blanc : aucune clé.

```
env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u GOOGLE_API_KEY -u GEMINI_API_KEY -u XAI_API_KEY -u AZURE_API_KEY -u MISTRAL_API_KEY -u OPENROUTER_API_KEY <commande>
```

Pour le vrai pilote : ne laisser que `ANTHROPIC_API_KEY`. Ne jamais laisser `OPENAI_API_KEY` ni `OPENROUTER_API_KEY` (voir pièges).

Variable utile : `LITELLM_LOCAL_MODEL_COST_MAP=True` (évite que LiteLLM télécharge la carte des prix à chaque lancement).

## 3. τ-bench (tau2)

### 3.1 Régler les modèles

Format LiteLLM, préfixe `anthropic/` :
- agent : `--agent-llm anthropic/claude-haiku-5-5` (ou `claude-sonnet-5-5`, `claude-opus-5-5`) ;
- client simulé : `--user-llm anthropic/claude-haiku-5-5` ;
- arguments : aucun réglage `temperature` (le banc met 0.0 par défaut, mais l'API le refuse sur les modèles 5.5 : on passe `--agent-llm-args '{}'` et `--user-llm-args '{}'`, voir section 8.3 et `JOURNAL_CHANGEMENTS.md`, 05/11 à 7 h 23).

### 3.2 Juges IA : où ils sont et comment les couper

Dans une partie texte, deux juges existent. Aucun n'est utilisé en banque.

| Juge | Où | Domaines concernés | Moyen de le couper |
|---|---|---|---|
| Assertions en langage naturel | `evaluator_nl_assertions.py`, modèle codé en dur `gpt-5.4-mini-2026-03-17` (`config.py` ligne 49), pas de réglage CLI | retail : 112 tâches sur 114 ont `NL_ASSERTION` dans `reward_basis` | Forcer `evaluation_type=ENV` : le CLI ne l'expose pas, d'où `banc/tau2_sans_juge.py` (remplace `run_tasks` par une version avec `EvaluationType.ENV`, puis appelle le vrai `tau2.cli.main`) |
| Contrôle de la communication (sémantique) | `--communicate-scorer semantic` par défaut | airline : les 50 tâches ont `COMMUNICATE` | `--communicate-scorer substring` (mots recherchés tels quels, aucun modèle) |

Autres juges inactifs par défaut en texte : `--auto-review` (faux par défaut), contrôle d'hallucination (voix full-duplex seulement), `--hallucination-retries` sans effet en texte.

Avec `tau2_sans_juge.py`, le score affiché est celui de l'état de la base (DB) seulement. On ne s'en sert pas : on lit les parties enregistrées.

### 3.3 Commandes du pilote (À NE PAS LANCER MAINTENANT)

À exécuter depuis `externe/tau2-bench/`, avec `ANTHROPIC_API_KEY` seule dans l'environnement :

```
cd "$RACINE"/externe/tau2-bench
export LITELLM_LOCAL_MODEL_COST_MAP=True
P="$RACINE"/banc/tau2_sans_juge.py

# airline
.venv/bin/python $P run --domain airline --agent-llm anthropic/claude-sonnet-5-5 --user-llm anthropic/claude-haiku-5-5 \
  --communicate-scorer substring --num-trials 1 --max-concurrency 3 --save-to pilote-airline-sonnet

# retail
.venv/bin/python $P run --domain retail --agent-llm anthropic/claude-sonnet-5-5 --user-llm anthropic/claude-haiku-5-5 \
  --num-trials 1 --max-concurrency 3 --save-to pilote-retail-sonnet

# banque (variante sans clé payante, voir 3.5)
.venv/bin/python $P run --domain banking_knowledge --retrieval-config bm25_grep \
  --agent-llm anthropic/claude-sonnet-5-5 --user-llm anthropic/claude-haiku-5-5 \
  --num-trials 1 --max-concurrency 3 --save-to pilote-banque-sonnet
```

Options utiles : `--num-tasks N`, `--task-ids ...`, `--seed`, `--max-steps` (200 par défaut), `--max-errors`, `--task-split-name`. Pour les trois modèles d'agent, changer `--agent-llm` et `--save-to`.

### 3.4 Où et comment les parties sont enregistrées

- Fichier : `externe/tau2-bench/data/simulations/<save-to>/results.json` (JSON unique pour le texte ; sans `--save-to`, nom horodaté).
- Structure : `info` (agent, client, seed, `retrieval_config`, politique), `tasks`, `simulations[]`.
- Chaque simulation contient `messages[]` dans l'ordre (`role` assistant, user, tool, `turn_idx`), avec pour l'agent les `tool_calls` (id, nom, arguments) et pour chaque résultat d'outil un message `role: tool` avec `id`, `content` (résultat complet), `error` (booléen). Vérifié sur parties factices : appels d'outils et résultats y sont tous, y compris les résultats de `KB_search` et `grep` de la banque (15 et 22 Ko).
- Aussi : `termination_reason`, `agent_cost`, `user_cost`, `agent_usage`, `reward_info`, `policy` (invite système de la partie), `seed`, `duration`. Le champ `raw_data` de chaque message d'agent garde la réponse brute de LiteLLM (usage en jetons).
- La table des outils n'est PAS dans `results.json` : `info.environment_info.tool_defs` est vide. Elle s'obtient à part : `registry.get_env_constructor(domaine)().get_tools()` (airline : 14 outils, retail : 16). À écrire avant de regarder des performances.
- Les parties publiées de `data/tau2/results` n'ont pas été ouvertes. `data/tau2/simulations/` (nos sorties) est un dossier distinct.

### 3.5 Banque : variantes de recherche documentaire (`--retrieval-config`)

Défaut du banc : `alltools`, qui exige une clé OpenAI. Il faut donc le régler explicitement.

| Variante | Clé payante ? | Vérification |
|---|---|---|
| `bm25`, `bm25_grep` | Non | Exécutées en mode factice : `KB_search` et `grep` répondent hors ligne |
| `grep_only` | Non | Partie factice OK |
| `golden_retrieval` (documents fournis dans l'invite) | Non | Partie factice OK |
| `full_kb` (toute la base dans l'invite), `no_knowledge` | Non | Résolution à blanc OK. Parties factices non lancées pour `full_kb` (invite probablement très longue : coût en jetons, à mesurer) |
| `terminal_use`, `terminal_use_write` | Pas de clé, mais l'outil `srt` manque | Bloqué : `srt` (sandbox-runtime) absent de la machine |
| `*_reranker*` | Oui (OpenAI) : reranker LLM `gpt-5.2` codé en dur | Lu dans le code, non lancé |
| `openai_embeddings*`, `alltools` | Oui (OpenAI, `text-embedding-3-large`) | Lu dans le code, non lancé |
| `qwen_embeddings*`, `alltools-qwen` | Oui (OpenRouter) | Lu dans le code, non lancé |

Recommandation : `bm25_grep` (recherche + grep, aucun appel tiers) comme variante principale ; `golden_retrieval` en variante témoin.

## 4. WorkBench

### 4.1 Particularités

- Tout passe par l'API de chat « compatible OpenAI » (`openai` SDK). Pour Claude en direct : `https://api.anthropic.com/v1`, clé `ANTHROPIC_API_KEY`.
- Piège de routage (`resolve_route`) : si `ANTHROPIC_API_KEY` est absente, le banc bascule sur OpenRouter et lit `OPENROUTER_API_KEY`. Avec cette clé présente, les appels partiraient chez OpenRouter. Ne garder que `ANTHROPIC_API_KEY`.
- Les modèles 5.5 ne sont pas dans `MODEL_REGISTRY` (il s'arrête à `claude-fable-5`, `claude-opus-4.8`, `claude-haiku-4.5`). `banc/workbench_pilote.py` les enregistre : `claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5` (identifiant envoyé = le nom tel quel).
- Il n'y a pas de client simulé dans WorkBench : une tâche = une consigne, l'agent agit seul.
- Le banc lit un `.env` du dossier courant (`load_dotenv`). Aucun `.env` n'a été créé.

### 4.2 Mode hors ligne

Le banc n'en a pas. `workbench_pilote.py` avec `PILOTE_HORS_LIGNE=1` en fournit un : il remplace la résolution de route et les deux fonctions d'appel du modèle par des réponses factices (un appel d'outil `company_directory.find_email_address`, puis une réponse finale). Aucun client HTTP n'est créé, aucune clé n'est lue.

Essai à blanc réalisé (3 tâches, modes ReAct et `--structured_outputs`) :

```
cd "$RACINE"/externe/workbench-run
PILOTE_HORS_LIGNE=1 env -u OPENROUTER_API_KEY "$RACINE"/externe/WorkBench/.venv/bin/python \
  "$RACINE"/banc/workbench_pilote.py --model_name claude-haiku-5-5 \
  --tasks_path mini_email_tasks_and_outcomes.csv --workers 1 --log_traces
```

### 4.3 Commandes du pilote (À NE PAS LANCER MAINTENANT)

Toujours depuis `externe/workbench-run/` : les données y sont en liens symboliques (le banc lit `data/processed` et `data/raw` relatifs au dossier courant) et les sorties vont dans `./data/results/`, à part des résultats publiés du dépôt.

```
cd "$RACINE"/externe/workbench-run
W="$RACINE"/externe/WorkBench
for d in email calendar analytics project_management customer_relationship_manager multi_domain; do
  $W/.venv/bin/python "$RACINE"/banc/workbench_pilote.py \
    --model_name claude-sonnet-5-5 \
    --tasks_path $W/data/processed/tasks_and_outcomes/${d}_tasks_and_outcomes.csv \
    --tool_selection all --workers 8 --log_traces --structured_outputs
done
```

Seule `ANTHROPIC_API_KEY` dans l'environnement. `--structured_outputs` = appel d'outils natif (sinon boucle ReAct en texte) : choix de conception à trancher. `--act_without_confirmation` existe aussi. Le dossier `tasks_and_outcomes/` contient aussi des sous-dossiers de versions (`v1`, `v2026-...`) ; ici on prend les fichiers de la racine (version courante, `ground_truth_version` = v2).

Note : le CSV de tâches contient aussi la colonne `outcome` (vérité terrain). L'agent ne lit que `task` (et `domains` en mode `--tool_selection domains`).

### 4.4 Où sont écrites les prédictions

`./data/results/<domaine>/<modèle>_<sélection>_<AAAA-MM-JJ_HH-MM-SS>.csv` (domaine = début du nom du fichier de tâches), colonnes `task, function_calls, full_response, error`. À côté :
- `..._meta.json` : modèle, route, URL de base, options, invite système type, horodatages ;
- `..._traces.json` (avec `--log_traces`) : pour chaque tâche, chaque étape avec `llm_input`, `llm_output`, `action`, `action_input`, `observation`. Vérifié : appels d'outils et résultats y sont (ReAct comme structuré).
- Pas de jetons ni de coût enregistrés par WorkBench (voir bloquants).

Le CSV est aussi relu par `workbench-evaluate` / `calculate_metrics` pour le score. Les résultats publiés (`data/results/`, `item_level_results*`) n'ont pas été ouverts.

## 5. Vérifié / non vérifié

Vérifié (exécuté ou lu dans le code, sans clé) :
- Installation des deux bancs (Python 3.12, commits demandés).
- tau2 : `--dry-run` pour airline, retail, banking_knowledge (toutes les variantes de 3.5), modèles `anthropic/claude-haiku-5-5` pris en compte dans la configuration.
- tau2 : parties complètes factices (LiteLLM `mock_response` / `mock_tool_calls`, qui renvoie avant tout appel HTTP ; clés retirées et proxy HTTP volontairement cassé) en airline (avec appels d'outils, et jusqu'à l'évaluation), retail, banque `bm25_grep`, `golden_retrieval`, `grep_only`, et `KB_search` + `grep` réels hors ligne.
- Enregistrement des appels d'outils et résultats (3.4) ; termes des deux juges et leur contournement (3.2).
- WorkBench : essai factice complet, ReAct et structuré, écriture des prédictions et traces, échec propre sans clé (erreur `OPENROUTER_API_KEY` avant tout réseau).

Non vérifié :
- Aucun appel réel à Claude : acceptation par l'API de `temperature` pour les trois modèles 5.5 (tau2 envoie `temperature: 0.0` ; WorkBench ne l'envoie pas si `supports_temperature` est faux, ce qui est le réglage par défaut du pilote, `PILOTE_TEMPERATURE=1` pour l'envoyer). Des modèles récents refusent ce paramètre.
- Comportement réel de tau2 avec les noms `claude-*-5-5` via LiteLLM 1.81.11 (qui ne les connaît pas : voir bloquants), et de l'endpoint OpenAI-compatible d'Anthropic avec les outils (WorkBench).
- Dynamique réelle d'une partie : durée, taux d'erreurs, limites de débit, nombre de jetons par partie (donc coût).
- Variantes de banque avec clé payante et `terminal_use` (outil `srt` absent).
- `full_kb` en partie factice ; domaines tau2 hors airline, retail, banking_knowledge.
- Suites de tests des deux dépôts (non lancées).

## 6. Bloquants et points d'attention

1. **Coût non enregistré correctement.** LiteLLM 1.81.11 (version verrouillée) ne connaît pas les prix des modèles `claude-*-5-5` : tau2 enregistrera `agent_cost`/`user_cost` à 0 (ou n/a) avec une erreur dans le journal. WorkBench n'enregistre ni jetons ni coût. Pour le budget du pilote il faudra lire `usage` dans `raw_data` des messages tau2 et calculer soi-même ; pour WorkBench, l'usage n'est pas conservé (il faudrait modifier `agent.py` ou envelopper `_create_with_deadline` dans `workbench_pilote.py`). À décider avant le lancement. **Mis à jour le 05/11** : tau2 garde `usage` (jetons d'entrée et de sortie) sur chaque message assistant et user de `results.json`, lu par `banc/pilote_etape1.py` ; pour WorkBench, `banc/usage_wrap.py` enveloppe `_create_with_deadline` (activé par `PILOTE_USAGE_FILE`, voir section 7) sans changer le comportement.
2. **Juge retail codé en dur** sur un modèle OpenAI : contourné par `tau2_sans_juge.py` (score ENV seulement). Si le score complet des assertions retail est un jour voulu, il faudra une clé OpenAI, ce qui n'est pas prévu.
3. **Banque : `alltools` par défaut exige OpenAI** ; toujours passer `--retrieval-config`. `terminal_use` bloqué tant que `srt` (`npm install -g @anthropic-ai/sandbox-runtime@0.0.23`) n'est pas installé : installation globale, donc non faite. Un préfixe npm local est possible, à valider.
4. **WorkBench bascule sur OpenRouter sans `ANTHROPIC_API_KEY`** : ne jamais exporter `OPENROUTER_API_KEY` pour le pilote.
5. **WorkBench : sorties** à garder dans `externe/workbench-run/` (le banc écrit dans `data/results/` du dossier courant, où se trouvent les résultats publiés si on lance depuis `externe/WorkBench/`).
6. **Réglage `supports_temperature` des modèles 5.5 inconnu** (voir ci-dessus) : à fixer au premier appel réel, sur une tâche seule.
7. Les parties factices de tau2 (`data/simulations/essai-blanc-*`) ne sont pas des données : ne pas les mêler aux parties du pilote.

## 7. Pilote étape 1 : lancement réel (À NE PAS LANCER avant relecture par le coordinateur)

Script : `banc/pilote_etape1.py`. Tests : `banc/tests/test_pilote_etape1.py`.

Contenu : 3 parties par environnement (aviation = airline, commerce = retail, banque = banking_knowledge avec `bm25_grep`, WorkBench), sur les 3 premières tâches de chaque liste de `banc/tirage/developpement.json` (lu à l'exécution), 1 essai par tâche, `claude-haiku-5-5` pour l'agent et pour le client simulé, 1 partie à la fois par défaut. tau2 passe par `tau2_sans_juge.py` (évaluation ENV seule, aucun juge OpenAI ; `--communicate-scorer substring` en aviation ; `--retrieval-config bm25_grep` en banque). WorkBench tourne depuis `externe/workbench-run/` avec `--tool_selection all --structured_outputs --log_traces`, un process par partie. Les parties sont lancées intercalées par rang (tâche 1 des quatre environnements, puis tâche 2, puis tâche 3).

### Essai à blanc (mode par défaut : ni clé, ni réseau)

```
cd "$RACINE"
env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u GOOGLE_API_KEY -u GEMINI_API_KEY -u XAI_API_KEY -u AZURE_API_KEY -u MISTRAL_API_KEY -u OPENROUTER_API_KEY \
  simulation/.venv/bin/python banc/pilote_etape1.py
```

Les bancs tournent sur leurs réponses factices (tau2 `mock_response`, WorkBench `PILOTE_HORS_LIGNE=2`), proxys cassés. Sortie : `pilote/etape1/<horodatage>-blanc/`. Si `developpement.json` manque, liste factice de test.

### Lancement réel

Prérequis : `~/.config/autonomie-meritee/anthropic.env`, permissions `600`, une ligne `ANTHROPIC_API_KEY=...` non vide. Aucun `.env` dans `externe/tau2-bench/` ni `externe/workbench-run/` (refus sinon).

```
cd "$RACINE"
simulation/.venv/bin/python banc/pilote_etape1.py --reel --plafond-usd 1.00
```

Options : `--concurrence 2` (défaut 1), `--developpement CHEMIN`, `--sortie-racine CHEMIN`. `--reel` sans `--plafond-usd` est refusé ; tout plafond supérieur à 1.00 aussi. La clé n'est jamais passée en argument ni écrite : elle n'existe que dans l'environnement des enfants, nettoyé de toute autre clé de fournisseur (donc WorkBench ne peut pas basculer sur OpenRouter).

Codes de sortie : 0 terminé ; 2 refus avant tout lancement ; 3 post-traitement échoué ; 4 terminé mais arrêté avant la fin (plafond à 80 %, usage illisible ou partie en échec : voir `journal.log` et `cout.json`).

Sorties dans `pilote/etape1/<horodatage>/` : `journal.log`, `cout.json` (réécrit après chaque partie), `resume.json`, `resume.txt`, `actions.csv` (banc/verdicts_csv.py), `actions_typees.csv` (+ typage banc/typage.py), `parties/` (copies de `results.json` tau2 ; CSV, `_meta`, `_traces` WorkBench), `logs/` (sortie des enfants, clé purgée), `usage/` (jetons WorkBench), `taches/` (CSV d'une tâche par partie WorkBench).

Coût : 0,10 $ / million de jetons en entrée, 0,50 $ en sortie ; un appel de plus de 100 000 jetons d'entrée est compté au double et signalé. Arrêt avant toute nouvelle partie à 80 % du plafond.

Avant les parties, le mode réel supprime `externe/tau2-bench/data/simulations/essai-blanc-*` (point 6).

## 8. Pilote étapes 2a et 2 : compteur précis, cache, lancement réel (À NE PAS LANCER avant relecture par le coordinateur)

Écrit le 2026-11-05. Rien de payant n'a été lancé : essais à blanc seulement, clés retirées.

Fichiers : `banc/cout_v2.py` (prix, palier, cache), `banc/usage_tau2.py` (callback LiteLLM), `banc/pilote_etape2.py` (2a et 2), `banc/tau2_sans_juge.py` (enregistre le callback). Tests : `banc/tests/test_cout_v2.py`, `banc/tests/test_pilote_etape2.py`. `banc/pilote_etape1.py` n'est pas modifié (ses fonctions de clé, d'environnement, de journal, de comptable et de typage sont réutilisées).

### 8.1 Compteur précis

- `tau2_sans_juge.py` enregistre un callback de succès LiteLLM. Si `PILOTE_USAGE_FILE` est définie, il ajoute une ligne JSON par appel : `modele, prompt_tokens, completion_tokens, cache_creation_input_tokens, cache_read_input_tokens, horodatage`. Aucun contenu de message, aucune clé. Sans la variable : aucun effet (l'étape 1 est inchangée).
- Vérifié dans `litellm/llms/anthropic/chat/transformation.py` (`calculate_usage`) : `usage.prompt_tokens` = input_tokens + écriture + lecture, il INCLUT déjà le cache. Le reste non caché = `prompt_tokens - écriture - lecture`. La fonction de coût s'appuie là-dessus : pas de double compte.
- Vérifié hors réseau (faux transport HTTP, `tau2.utils.llm_utils.generate` réel) : usage `input 10 / écriture 100 / lecture 200` devient `prompt_tokens 310` dans la ligne du callback.
- Aussi vérifié de bout en bout avec les vraies parties factices (`mock_response`) : le callback écrit bien le JSONL, 1 ligne par appel, modèle `claude-haiku-5-5` (sans préfixe `anthropic/`).
- `PILOTE_USAGE_FILE` est posée sur l'environnement de chaque enfant APRÈS `env_enfant` (qui retire les `PILOTE_*`), pour tau2 comme pour WorkBench. Un fichier par partie : `usage/<id>.jsonl`.

### 8.2 Coût v2 (`banc/cout_v2.py`)

| Modèle | Entrée / sortie ($ par M) | Remarque |
|---|---|---|
| claude-haiku-5-5 | 0,10 / 0,50 | au-delà de 100 000 jetons d'invite totale (cache compris) : 0,50 / 2,50 |
| claude-sonnet-5-5 | 2 / 10 | |
| claude-opus-5-5 | 4 / 20 | lecture de cache 0,05 x (0,20 $/M) |

Écriture de cache 1,25 x, lecture 0,1 x (Haiku, Sonnet), appliquées au prix d'entrée du palier. Le coût est calculé par appel et par modèle (agent et client simulé n'ont pas le même modèle). Modèle inconnu : erreur, donc arrêt. En réel, JSONL absent, vide, illisible, ou qui ne couvre pas `results.json` (moins de lignes ou moins de jetons que tau2 n'en a enregistré) : arrêt. À blanc : l'usage manquant est estimé (caractères / 4) et marqué `estime`.

### 8.3 Cache

- `--cache` ajoute `{"cache_control_injection_points": [{"location":"message","role":"system"},{"location":"message","index":-1}]}` à `--agent-llm-args` ET `--user-llm-args` de tau2 (2 points, 4 au plus). Syntaxe lue dans `litellm/integrations/anthropic_cache_control_hook.py` : `index` négatif accepté (-1 = dernier), `role` cible tous les messages de ce rôle. Les outils sont couverts par le point système (le préfixe Anthropic est : outils, système, messages).
- Vérifié hors réseau : le corps de requête Anthropic reçoit `cache_control` sur le bloc système et sur le dernier message (texte, et résultat d'outil `tool_result`).
- En réel sans cache, les réglages restent vides (`{}`) : les modèles 5.5 refusent `temperature`.
- WorkBench : pas de cache. Son client est le SDK OpenAI pointé sur l'endpoint compatible d'Anthropic ; aucun point d'injection n'y est possible sans modifier `agent.py`, et l'endpoint compatible n'est pas connu pour honorer `cache_control` (non vérifié, pas de réseau). WorkBench reste peu coûteux.
- Longueur minimale cachable des modèles 5.5 : 512 jetons ; les invites du pilote (5 000 à 15 000 jetons par appel à l'étape 1) la dépassent.

### 8.4 Étape 2a : mini-essai du cache (réel : à lancer par le coordinateur)

2 parties claude-haiku-5-5 avec cache : aviation (première tâche de la liste, 11) et banque (première tâche, task_003), comme à l'étape 1. Plafond 0,10 $ (refus au-delà), arrêt à 80 %.

```
cd "$RACINE"
env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u GOOGLE_API_KEY -u GEMINI_API_KEY -u XAI_API_KEY -u AZURE_API_KEY -u MISTRAL_API_KEY -u OPENROUTER_API_KEY \
  simulation/.venv/bin/python banc/pilote_etape2.py --etape 2a                              # à blanc (essai déjà fait)

simulation/.venv/bin/python banc/pilote_etape2.py --etape 2a --reel --plafond-usd 0.10      # RÉEL
```

Sortie : `pilote/etape2a/<horodatage>/` (`cout.json`, `rapport_2a.txt` et `.json`, `resume.txt`, `actions_typees.csv`, `usage/`, etc.). `rapport_2a` donne, par partie, jetons de cache écrits et lus, part de l'invite lue en cache, coût v2, comparé à l'étape 1 (aviation-1 : 0,0153169 $ ; banque-1 : 0,0158345 $). Les deux exécutions ne sont pas identiques (dialogue non déterministe) : la comparaison est indicative.

### 8.5 Étape 2 (réel : à lancer par le coordinateur, après lecture du rapport 2a)

3 modèles d'agent x 4 environnements x 10 tâches = 120 parties. Client simulé : claude-haiku-5-5. Tâches : les 10 premières de chaque liste de `developpement.json` (aviation, commerce, banque) ; WorkBench en tourniquet sur email, calendar, customer_relationship_manager, project_management, analytics, multi_domain (chaque fichier dans l'ordre de la liste, 10 tâches). Mêmes tâches pour les 3 modèles. Ordre : par rang, puis environnement, puis modèle. Concurrence 2 par défaut, 3 au plus. Plafond obligatoire en réel, 40 $ au plus ; arrêt avant toute nouvelle partie à 80 % du plafond (32 $ si 40). 100 tours au plus par partie tau2, délai de 30 minutes par partie.

```
cd "$RACINE"
simulation/.venv/bin/python banc/pilote_etape2.py --etape 2 --cache                                       # à blanc (clés retirées avec env -u, comme ci-dessus)

simulation/.venv/bin/python banc/pilote_etape2.py --etape 2 --cache --reel --plafond-usd 40 --concurrence 2   # RÉEL (plafond à fixer par le coordinateur, 40 au plus)
```

Prérequis du réel : `~/.config/autonomie-meritee/anthropic.env` (600, `ANTHROPIC_API_KEY=...`), aucun `.env` dans `externe/tau2-bench/` ni `externe/workbench-run/`. Le réel supprime les `essai-blanc-*` de `externe/tau2-bench/data/simulations/` avant de commencer.

Sortie : `pilote/etape2/<horodatage>/` : `journal.log`, `cout.json` (réécrit après chaque partie : jetons, cache écrit et lu, coût v2), `resume.txt` / `resume.json` (par environnement et par modèle : parties, actions, écritures par verdict et par type, jetons dont cache, coût ; puis par modèle), `actions.csv`, `actions_typees.csv`, `parties/`, `logs/`, `usage/`, `taches/`.

Codes de sortie : 0 terminé ; 2 refus avant tout lancement ; 3 post-traitement échoué ; 4 arrêté avant la fin (plafond à 80 %, usage illisible ou incomplet, modèle inconnu, ou partie en échec).

Ordre de grandeur (estimation grossière, NON mesurée) : en reprenant les jetons des 12 parties de l'étape 1 (3 tâches par environnement, sans cache) et en multipliant par 10/3, le coût sans cache serait d'environ 0,6 $ (Haiku), 11 $ (Sonnet) et 23 $ (Opus), soit environ 35 $. Les tâches de rang 4 à 10 peuvent être plus longues ou plus courtes ; les parties Opus sont les plus risquées. Le cache devrait réduire ce montant ; l'étape 2a le mesure.
