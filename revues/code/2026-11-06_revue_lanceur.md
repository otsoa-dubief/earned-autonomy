# Revue indépendante du lanceur de l'expérience

Rédigée le 6 novembre 2026 par Claude, agent neuf qui n'a pas écrit le code (revue locale décidée par Otsoa, QCM).

**Objet.** `banc/lanceur.py` (commit cd0ee78) et ce qu'il appelle : `pilote_etape1.py` (`Comptable`, `FRACTION_ARRET`, enfants, clé, environnement), `pilote_etape2.py`, `usage_tau2.py`, `usage_wrap.py`, `cout_v2.py`, `outils_agent.py` ; tests `banc/tests/test_lanceur.py`. Référence : `PLAN_EXPERIENCE.md` (2.2, 2.3, 2.5, 4.7 points 2 et 5, Q10 du 05/11, décision du 06/11 sur l'arrêt de la vague 2, `JOURNAL_CHANGEMENTS.md` du 06/11) et `banc/CHOIX_LANCEUR.md`. Pour vérifier ce que le lanceur suppose des bancs, lu aussi : τ-bench (033bf08 : orchestrateur, relances, CLI) et WorkBench (49c7dfd : inférence, agent, outils).

**Méthode.** Lecture, puis chaque constat reproduit par un test ou un script : exécuteur factice ou enfant simulé (`pe.executer_enfant` remplacé), fausse clé dans un fichier temporaire, bancs redirigés, aucun réseau.

**Respect des interdits.** Aucun appel réel, aucun `--reel` contre l'API ; `~/.config/autonomie-meritee/anthropic.env` jamais lu ; rien lu sous `donnees/` ni dans les résultats publiés des bancs ; aucun fichier existant modifié ; aucun commit. `externe/tau2-bench/data/simulations/` : liste identique avant et après (aucun essai à blanc avec les vrais bancs n'a été nécessaire).

**Reproductions** (`revues/code/lanceur/`) :
- `test_revue_lanceur.py` : un test par constat ; chaque test **passe tant que le défaut est présent** et affiche sa preuve (option `-s`) ;
- `demo_dotenv.py`, `demo_workbench_contexte.py`, `demo_workbench_exception_outil.py` : scripts lancés dans le venv d'un banc, sans appel ;
- `test_verifications_sans_constat.py` : vérifications indépendantes qui n'ont rien trouvé.

```
cd ROOT
E="env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u OPENROUTER_API_KEY"
$E simulation/.venv/bin/python -m pytest -q -s -p no:cacheprovider revues/code/lanceur/
```
Résultat : 35 passed (17 reproductions, 18 vérifications). `banc/tests/test_lanceur.py` : 95 passed, inchangé.

## Synthèse

| n° | Gravité | Constat | Endroit | Reproduction |
|---|---|---|---|---|
| 1 | **bloquant** | Rien ne relie deux lancements : relancer la vague ouvre un second plafond ; deux reprises du même dossier jouent les mêmes parties | lanceur.py:1660-1684, 1715 | R2, R2b, R2c |
| 2 | à corriger | Parties WorkBench lancées après l'arrêt (seuil, Ctrl-C, nom changé…) | lanceur.py:1077-1086, 675-682 | R1, R1b |
| 3 | à corriger | Reprise de la vague 1 permise après la vague 2 : mêmes parties jouées et payées deux fois | lanceur.py:1500-1506, 1535 | R3 |
| 4 | à corriger | WorkBench : usage absent après des appels : coût nul, partie gardée, aucun arrêt | lanceur.py:712 | R4 |
| 5 | à corriger | WorkBench : une erreur de l'agent devient un échec technique, rejouée puis exclue | lanceur.py:743 | demo_workbench_exception_outil |
| 6 | à corriger | τ-bench se relance lui-même 3 fois, sans déclaration ; dépassement de contexte jamais « arrêtée » | lanceur.py:564-567, 750-751 | R9 |
| 7 | à corriger (risque non prouvé) | Référence du nom de modèle commune à τ-bench et à WorkBench | lanceur.py:776-786 | R7 |
| 8 | mineur | Filet de 35 min sur une simulation finie : « arrêtée (30 minutes) » et gardée, quelle que soit la terminaison | lanceur.py:731-732, 1037 | R8 |
| 9 | mineur | WorkBench « Context window exceeded » : partie gardée sans aucune de ses actions | lanceur.py:741-742 | demo_workbench_contexte |
| 10 | mineur | τ-bench planté sans simulation ni usage : coût nul, aucun arrêt | lanceur.py:529-536 | R5 |
| 11 | mineur | Coût inconnu : la reprise repart sans le compter ni l'exiger | lanceur.py:826-836, 1685 | R6 |
| 12 | mineur | `.env` au-dessus du banc chargé par τ-bench, non contrôlé | pilote_etape1.py:162-166 | demo_dotenv |
| 13 | mineur | Erreurs hors du `try` de `main` : traceback et code 1 au lieu de « REFUS » | lanceur.py:1671, 1698 | R13, R2c |

## Constats

### 1. Bloquant : rien ne relie deux lancements de la même vague

**Endroit.** lanceur.py:1668-1671 (sans `--reprendre`, nouveau dossier à chaque lancement), 1517-1521 (graine retirée au hasard), 1683 (comptable neuf, à zéro). Reprise : 1660-1667 (même dossier, aucun verrou), 1684 (`Registre` construit sur les lignes lues au départ), 1715 (`cout.json` final réécrit depuis ces seules lignes).

**Constat.**
- La même commande relancée sans `--reprendre` (historique du shell après une coupure SSH, agent qui « réessaie » après un code 4) crée un second dossier de la même vague, avec une autre graine (donc une autre vague 1) et un plafond neuf. Le plafond et l'accord d'Otsoa bornent un lancement, pas la vague : à la vague 2, une relance pourrait dépenser jusqu'à un second seuil d'arrêt (570 $ pour un plafond de 600 $).
- Deux `--reprendre` du même dossier en même temps (processus resté vivant dans tmux, second terminal) : le second prend la tentative en cours pour une interruption, puis les deux jouent la même file, chacun sous son propre plafond. Le `cout.json` final du premier ignore les lignes et le coût du second ; or la vague 2 lit la vague 1 dans `cout.json` (`charger_vague`).
- Aparté : un second lancement dans la même seconde plante sur `FileExistsError` (constat 13).

**Preuve.** `$E simulation/.venv/bin/python -m pytest -q -s -p no:cacheprovider revues/code/lanceur/test_revue_lanceur.py -k R2`
```
R2 codes : [4, 4] ; dossiers : ['2026-11-06_04-19-33', '2026-11-06_04-19-34'] ; graines : [3040207725301888901, 9095133007627070349]
R2 dépense par dossier : [2.4, 2.4] ; total : 4.8 USD pour plafond = accord = 3 USD
R2b codes : [('seconde', 0), ('premiere', 0)] ; jouées par la 1re : 10 ; par la 2de : 10 ; jouées deux fois : 10
R2b tentatives.jsonl : parties gardées deux fois : 10 ; cout.json final : 12 lignes pour 23 fins dans tentatives.jsonl
```
(R2b simule deux processus entrelacés : la seconde reprise est lancée pendant la première tentative de la première.)

**Correction minimale.**
- En réel, sans `--reprendre`, refuser le lancement s'il existe déjà sous `<racine de sortie>/vague<N>/` un dossier réel (sans `-blanc`) de cette vague ; une option explicite pour passer outre, notée au plan de jeu.
- Verrou exclusif dans le dossier de vague : `os.open(sortie / "verrou", O_CREAT | O_EXCL)` avec le PID, pris avant toute partie, refus s'il appartient à un processus vivant, retiré à la fin.

### 2. À corriger : parties WorkBench lancées après l'arrêt

**Endroit.** lanceur.py:1077-1086 : le seuil est vérifié avant de retirer la partie de la file ; la tentative est notée « début », puis l'exécuteur est appelé. lanceur.py:675-682 : `_executer_workbench` attend `verrou_wb`, puis lance l'enfant sans revérifier l'arrêt.

**Constat.** Avec deux ou trois parties à la fois, une partie WorkBench retirée de la file attend le verrou pendant que la partie WorkBench en cours joue (jusqu'à 30 min). Si l'arrêt tombe entre-temps (seuil, Ctrl-C, nom de modèle changé, coût non compté, trois échecs), elle démarre quand même : jusqu'à deux parties de plus, l'une après l'autre. Cela contredit le choix 9 (« aucune nouvelle tentative n'est lancée une fois le seuil d'arrêt atteint »), le choix 16 c (« Ctrl-C : plus aucune nouvelle partie ») et le journal (l. 1108 : « aucune nouvelle partie n'est lancée »). Après Ctrl-C, ces enfants démarrent après le signal : ils ne le reçoivent pas et jouent jusqu'au bout. Après un nom changé, ils recevront sans doute le nouveau nom : payés pour être exclus. Coût borné à deux parties WorkBench, dans la réserve de 15 $.

**Preuve.** `... -k "R1_ or R1b"`
```
R1 départs des enfants WorkBench : [(False, 0.0), (True, 4.0), (True, 8.0)]
R1 arrêt : coût cumulé 4.000000 USD >= seuil d'arrêt 4.000000 USD (80 % du plafond) ; cumul final : 12.0 USD ; plafond : 5.0 USD
R1b départs : [False, True, True] ; statuts : ['terminée', 'terminée', 'terminée']
```
(pour chaque enfant : arrêt déjà décidé à son démarrage, cumul à ce moment. R1b pose l'arrêt comme le gestionnaire de Ctrl-C, `compta.arreter`.)

**Correction minimale.** Mettre `compta` dans `ctx` ; dans `_executer_workbench`, juste après avoir pris `verrou_wb`, si `compta.doit_arreter()`, ne pas lancer l'enfant et rendre la tentative « non lancée » : coût nul, non comptée comme tentative, remise en file pour la reprise (le traitement d'« interrompue » convient).

### 3. À corriger : reprise de la vague 1 après la vague 2

**Endroit.** lanceur.py:1500-1506 : une reprise ne contrôle que vague, mode et réserve. lanceur.py:1535 : la vague 2 n'exige que `fin` dans le `cout.json` de la vague 1. Rien ne marque la vague 1 comme reprise par la vague 2.

**Constat.** La vague 2 joue les parties de la vague 1 restées sans fin (choix 5 : non lancées, relances dues, interrompues, exclusions à rejouer). Une reprise de la vague 1 lancée ensuite (le journal annonce des « parties restantes », code 4) les rejoue aussi : deux tentatives gardées, deux dossiers `parties/`, payées deux fois. Le moteur, quand il réunira les deux vagues (question ouverte 1 de CHOIX), aura deux fois la même partie.

**Preuve.** `... -k R3`
```
R3 codes : 4 0 0 ; reprise de la vague 1 a joué : ['WorkBench-opus-p01-email_1']
R3 tentatives gardées de WorkBench-opus-p01-email_1 : vague 1 [('WorkBench-opus-p01-email_1', 1, 0.04)] ; vague 2 [('WorkBench-opus-p01-email_1', 2, 0.01)]
```

**Correction minimale.** Au premier lancement de la vague 2, écrire dans le dossier de la vague 1 un marqueur (`vague2.json` : dossier de la vague 2, horodatage) ; refuser `--reprendre` d'un dossier de vague 1 qui le porte.

### 4. À corriger : WorkBench, usage absent après des appels, coût nul et aucun arrêt

**Endroit.** lanceur.py:712 : `appels_faits=res["delai_depasse"] or (res["trace"] and not res["terminaison"])`.

**Constat.** Le garde-fou du choix 16 b (« JSONL absent alors que des appels ont eu lieu : arrêt ») ne joue que si le champ `error` de WorkBench est vide. Une partie arrêtée par la limite de 20 itérations ou par la fenêtre de contexte a forcément appelé le modèle ; sans ligne d'usage, elle est gardée (« arrêtée ») avec un coût nul, et le lanceur continue. Même chose après une erreur d'API survenue après des appels réussis. Ce coût nul entre dans le coût moyen mesuré, qui fixe l'estimation et la réduction de la vague 2. En pratique, une capture en panne serait vite vue sur une partie normale ; le défaut reste un trou dans le seul mur.

**Preuve.** `... -k R4`
```
R4 [Agent stopped due to iteration] statut=arrêtée ok=True usage=absent cout_usd=None cumul=0.0 arret=None
R4 [Context window exceeded] statut=arrêtée ok=True usage=absent cout_usd=None cumul=0.0 arret=None
R4 [Error code: 529 overloaded] statut=échec technique ok=False usage=absent cout_usd=None cumul=0.0 arret=None
```
Témoin (`test_R4_temoin_sans_erreur_le_garde_fou_joue`) : sans texte d'erreur, arrêt « coût non compté ».

**Correction minimale.** `appels_faits=res["delai_depasse"] or res["trace"]` : une prédiction écrite suppose que l'agent a tourné. Une erreur d'authentification au premier appel arrêtera aussi le lanceur, ce qui est souhaitable.

### 5. À corriger : WorkBench, une erreur de l'agent devient un échec technique, rejouée puis exclue

**Endroit.** lanceur.py:743 : tout texte inconnu du champ `error` est un échec technique ; puis 1039-1042 et 1062-1065 : relance aussitôt, exclusion au second échec. Côté WorkBench (49c7dfd) : `Tool.__call__` ne rattrape rien (src/tools/tool.py:61-62) ; `run_agent_structured` appelle l'outil sans `try` (src/evals/agent.py:614) ; `_run_single_task` met `str(e)` dans `error` et ne recopie pas les actions déjà faites (src/evals/inference.py:112-122) ; des outils lèvent sur un argument mal formé (src/tools/calendar.py:84-88 : `pd.Timestamp`, `int(duration)` ; src/tools/email.py:83-85).

**Constat.** Une date en toutes lettres passée à `calendar.search_events`, une durée non numérique écrite plus tôt par `calendar.create_event`, un nom d'argument inventé : c'est l'agent qui se trompe, pas l'infrastructure. Le lanceur rejoue la partie (seconde chance : l'erreur disparaît si la relance réussit), puis l'exclut si elle se répète. Des erreurs de l'agent sortent ainsi des données, de façon sélective. Le choix 14 range ces exceptions avec les pannes d'API (« par exemple une erreur 529 ») sans relever cette conséquence. *Déduit* : comptés en échecs techniques par configuration au point 2 du rapport, et écrits au journal avec la partie et le modèle (« WorkBench : Unknown datetime string format… »), ils font voir des erreurs de l'agent par modèle entre deux vagues. Fréquence réelle : non mesurée.

**Preuve.**
```
cd externe/WorkBench && $E .venv/bin/python ../../revues/code/lanceur/demo_workbench_exception_outil.py
WorkBench : error = 'Unknown datetime string format, unable to parse: next week' ; function_calls = []
lanceur.classer : ('échec technique', None, 'WorkBench : Unknown datetime string format, unable to parse: next week')
```

**Correction minimale.** Ne traiter en échec technique que les erreurs d'API (texte commençant par « Error code: », ou « Connection error. », « Request timed out. ») ; toute autre exception WorkBench devient « arrêtée (exception d'outil) » sans trace exploitable (WorkBench a perdu les actions) : exclue, déclarée, jamais relancée. À inscrire à CHOIX_LANCEUR.md et au journal.

### 6. À corriger : relances internes de τ-bench, dépassement de contexte

**Endroit.** lanceur.py:564-567 : la commande ne passe pas `--max-retries`. lanceur.py:750-751 : branche `context_window_exceeded`. Côté τ-bench (033bf08) : `DEFAULT_RETRY_ATTEMPTS = 3` (src/tau2/config.py:69 ; option `--max-retries`, cli.py:235) ; `run_with_retry` rejoue toute la simulation sur n'importe quelle exception, puis écrit une simulation vide `infrastructure_error` (src/tau2/runner/progress.py:54-124) ; `CONTEXT_WINDOW_EXCEEDED` n'est jamais attribué (seulement défini, src/tau2/data_model/simulation.py:1079), un dépassement lève `ContextWindowExceededError` (LiteLLM 1.81.11, exception_mapping_utils.py:621-623) ; le délai de 30 min vaut par essai (orchestrator.py:288 et 771).

**Constat.**
- Une panne d'API pendant une partie est rejouée jusqu'à 3 fois par τ-bench, sans que le lanceur le sache : l'échec technique n'est ni compté ni déclaré, alors que Q10 dit « relancée une fois, puis exclue et déclarée ». Le coût, lui, est compté (lignes en plus dans le JSONL, admises par `croiser`).
- Un dépassement de contexte n'est jamais « arrêtée (fenêtre de contexte) » comme le prévoit le choix 14 : 4 essais dans τ-bench, échec technique, relance par le lanceur (4 essais de plus), puis exclusion. Jusqu'à 8 parties jouées jusqu'à leur point le plus cher, pour un comportement de l'agent (5.5, point 1).
- Après un essai raté, l'essai suivant repart pour 30 min ; le filet tue le processus à 35 min : la partie devient « arrêtée (30 minutes) » sans trace, exclue, non relancée, alors qu'aucun essai n'a duré 30 min.

Écart non noté dans CHOIX_LANCEUR.md. Fréquence d'un dépassement : non mesurée (aucun appel au-delà de 100 000 jetons au pilote).

**Preuve.** `... -k R9` (le test vérifie aussi l'absence de `--max-retries`, `DEFAULT_RETRY_ATTEMPTS = 3` et l'absence de `CONTEXT_WINDOW_EXCEEDED` dans l'orchestrateur ; l'enfant simulé écrit la simulation vide que τ-bench produit après 4 essais)
```
R9 lignes : [('banque-opus-p01-task_001', 'échec technique', None, None, 24.4), ('banque-opus-p01-task_001-t2', 'échec technique', None, 'échec technique (deux tentatives)', 24.4)]
```

**Correction minimale.** Ajouter `--max-retries 0` à `commande_tau2` (seule la relance du lanceur reste, déclarée) ; classer une simulation `infrastructure_error` dont `info.error_type` vaut `ContextWindowExceededError` en « arrêtée (fenêtre de contexte) », sans trace : exclue, déclarée, non relancée. À défaut, déclarer au moins les relances de τ-bench dans CHOIX_LANCEUR.md et au journal.

### 7. À corriger (risque non prouvé) : référence du nom de modèle commune aux deux bancs

**Endroit.** lanceur.py:776-786 : `Noms.examiner` indexe la référence par le seul modèle demandé (`court`, l. 182-184).

**Constat.** τ-bench appelle l'API Anthropic par LiteLLM (`model` de la réponse native) ; WorkBench appelle l'API compatible OpenAI (`model` de la réponse au format OpenAI, `usage_wrap.py`). Les deux partagent la même référence. Si les deux points d'accès ne renvoient pas la même chaîne pour le même modèle (alias d'un côté, version datée de l'autre), la première partie WorkBench est exclue et le lanceur s'arrête ; ensuite, chaque reprise exclut définitivement une partie (« … et encore au rejeu ») et s'arrête de nouveau. Rien ne l'a mesuré : à blanc, les deux renvoient le modèle demandé, et le pilote est antérieur au champ `modele_renvoye`. Découvert après le gel, il faudrait changer le code gelé.

**Preuve** (comportement du code). `... -k R7`
```
R7 statuts : [('aviation', 'terminée'), ('WorkBench', 'exclue : nom de modèle changé')] ; arret : nom de modèle renvoyé changé (claude-haiku-5-5 : claude-haiku-5-5 au lieu de claude-haiku-5-5-20261001) : arrêt ; on ne reprend que si l'ancien nom revient (2.5, point 6)
```

**Correction minimale.** Indexer la référence par banc et modèle (`f"{banc_de(env)}:{court(dem)}"` ; `conclure` connaît l'environnement de la tentative). Ou relever avant le gel le `model` renvoyé par chaque point d'accès : un appel de chaque, pour moins d'un centime, avec l'accord d'Otsoa.

### 8. Mineur : filet de 35 minutes sur une simulation finie

**Endroit.** lanceur.py:731-732 (`delai_depasse` testé en premier), 1037 (`gardee` lit `trace`), 633-636.

**Constat.** Processus τ-bench tué à 35 min alors que `results.json` contient une simulation finie (processus resté vivant après l'enregistrement) : la partie est « arrêtée (30 minutes) » et gardée, quelle que soit sa terminaison. Un `infrastructure_error` (échec technique, simulation vide) est gardé ; un `user_stop` est étiqueté « 30 minutes ». Le choix 13 ne prévoit le filet que sans trace.

**Preuve.** `... -k R8`
```
R8 [infrastructure_error] statut=arrêtée arret=30 minutes ok=True terminaison=infrastructure_error dossier=parties/tau2-aviation-opus-p01-1
R8 [user_stop] statut=arrêtée arret=30 minutes ok=True terminaison=user_stop dossier=parties/tau2-aviation-opus-p01-1
```

**Correction minimale.** Dans `classer`, ne rendre « arrêtée (30 minutes) » sur `delai_depasse` que sans trace ; avec une trace, classer sur la terminaison comme d'habitude (et calculer `ok` sans `delai_depasse` dans ce cas).

### 9. Mineur : WorkBench « Context window exceeded », partie gardée sans ses actions

**Endroit.** lanceur.py:741-742 ; WorkBench src/evals/inference.py:112-122 (actions recopiées seulement en l'absence d'exception).

**Constat.** Sur ce texte, WorkBench a perdu toutes les actions de la partie, déjà exécutées ; le lanceur la garde comme « arrêtée (fenêtre de contexte) » : une partie gardée vide, dont d'éventuelles erreurs ont disparu. C'est le cas de la contradiction 4 de CHOIX (« partie arrêtée sans trace exploitable »), à exclure et déclarer.

**Preuve.**
```
cd externe/WorkBench && $E PILOTE_HORS_LIGNE=2 .venv/bin/python ../../revues/code/lanceur/demo_workbench_contexte.py
WorkBench : error = 'Context window exceeded' ; function_calls = [] ; actions faites : ['email.send_email']
lanceur.classer : ('arrêtée', 'fenêtre de contexte', None)
```

**Correction minimale.** Dans `_executer_workbench`, `res["trace"] = False` quand la terminaison vaut `WB_MESSAGE_CONTEXTE` : la partie devient « arrêtée sans trace exploitable », exclue, déclarée, non relancée.

### 10. Mineur : τ-bench planté sans simulation ni usage, coût nul et aucun arrêt

**Endroit.** lanceur.py:529-536 (`if reel and (present or de_results)`).

**Constat.** En réel, τ-bench sorti en erreur avec un `results.json` sans simulation et sans JSONL d'usage : coût nul, aucun arrêt (relance, puis exclusion). Sans simulation, le croisement est impossible : si la capture était en panne, rien ne le signale, alors que le choix 16 b vise ce cas.

**Preuve.** `... -k R5`
```
R5 lignes : [('aviation-opus-p01-1', 'échec technique', 'absent', None), ('aviation-opus-p01-1-t2', 'échec technique', 'absent', None)] ; arret : None
```

**Correction minimale.** En réel, usage absent alors que `results.json` existe (τ-bench a commencé la partie) : `cout_inconnu`, donc arrêt.

### 11. Mineur : coût inconnu, la reprise repart comme s'il était nul

**Endroit.** lanceur.py:835-836 : `cout_inconnu` ne fait qu'arrêter, la ligne ne le note pas ; 1685 : la reprise somme les `cout_usd`. Même effet pour un modèle inconnu dans l'usage (l. 826-829 : coût nul, sans majorant depuis `results.json`).

**Constat.** L'arrêt est bon, mais rien n'oblige à examiner ni à chiffrer ce coût avant `--reprendre` : il est perdu pour le plafond.

**Preuve.** `... -k R6`
```
R6 1er lancement : 4 tentative aviation-haiku-p01-1 : usage illisible, coût non compté 0.0 ; reprise : 0 cumul 2.28 ; ligne : absent None
```

**Correction minimale.** Noter `cout_inconnu` dans la ligne ; refuser la reprise tant qu'une telle ligne n'a pas reçu un montant retenu (option du type `--cout-retenu ID=USD`, ajouté au cumul et noté dans `reprises`).

### 12. Mineur : `.env` au-dessus du banc chargé par τ-bench, non contrôlé

**Endroit.** pilote_etape1.py:162-166 : `verifier_pas_de_dotenv` ne regarde que `externe/tau2-bench/.env` et `externe/workbench-run/.env` (appel : lanceur.py:1648). τ-bench src/tau2/utils/utils.py:14 : `load_dotenv()` sans chemin.

**Constat.** python-dotenv remonte du dossier du module jusqu'à `/` : 10 dossiers, aucun `.env` aujourd'hui. Un `.env` posé plus tard dans `externe/`, le dépôt, `~/dev` ou `~` (partagés avec d'autres projets) réintroduirait dans les enfants τ-bench toute variable absente de l'environnement nettoyé (clé d'un autre fournisseur, `ANTHROPIC_BASE_URL`, `LITELLM_*`), après `verifier_env_enfant`. À blanc, toujours aucun appel (réponses factices) ; en réel, l'environnement des enfants n'est plus garanti.

**Preuve.**
```
$E externe/tau2-bench/.venv/bin/python revues/code/lanceur/demo_dotenv.py
verifier_pas_de_dotenv : aucun refus
variable chargée par load_dotenv() : chargee
dossiers fouillés pour le vrai τ-bench : 10 ; contrôlés par le lanceur : 1 (externe/tau2-bench)
```

**Correction minimale.** `env["PYTHON_DOTENV_DISABLED"] = "1"` dans l'environnement des enfants : `load_dotenv` le respecte dans les deux venvs (python-dotenv 1.2.4 pour τ-bench, 1.2.2 pour WorkBench ; vérifié dans leur source).

### 13. Mineur : erreurs hors du `try` de `main`

**Endroit.** lanceur.py:1698 (`recuperer_interrompues`), 1671 (`mkdir(exist_ok=False)`).

**Constat.** L'usage illisible d'une tentative orpheline lève `ErreurPilote` (« à examiner avant de reprendre ») hors du `try` : traceback et code 1 au lieu de « REFUS : » et du code 2, après avoir déjà mis à l'écart les orphelines précédentes et écrit `outils_agent.json` et le journal. Un second lancement dans la même seconde lève `FileExistsError` de la même façon. Aucun argent en jeu (rien n'est lancé ; la reprise suivante repart juste).

**Preuve.** `... -k "R13 or R2c"`
```
R13 exception non rattrapée : ErreurPilote reprise : usage illisible de la tentative interrompue commerce-haiku-p01-11 ...
R13 après coup : orphelines restantes ['commerce-haiku-p01-11'] ; interruptions écrites ['aviation-haiku-p01-3-interrompue-2026-11-06_04-21-43']
```
R2c : `FileExistsError` attendu et levé.

**Correction minimale.** Lire et valider tous les usages des orphelines, et créer le dossier, à l'intérieur du `try` de `main` (ou rattraper `ErreurPilote` et `FileExistsError` autour).

## Limites non prouvées (impossibles à reproduire sans appel réel)

- **Appels coupés côté client puis relancés.** WorkBench abandonne un appel au bout de 75 s et le relance, jusqu'à 10 essais (src/evals/agent.py:87, 377, 388) ; LiteLLM aussi, après son propre délai. Si l'API facture l'appel abandonné, ce coût n'est dans aucun JSONL. Seul recours : le recoupement avec la console après chaque vague (4.7, point 5), dans la marge de 20 % (vague 1) ou de 15 $ (vague 2).
- **WorkBench, JSONL incomplet** (moins de lignes que d'appels) : indétectable, aucun croisement contrairement à τ-bench.
- **Enfants orphelins.** Si le lanceur seul est tué (`kill -9`), un enfant peut continuer à appeler l'API et à écrire dans `usage/<id>.jsonl` ou dans `workbench-run/data/results/`, puis se mêler à la tentative rejouée. Les enfants restent dans le groupe de processus du lanceur (pas de `start_new_session`), donc Ctrl-C et la fermeture du terminal les atteignent ; `kill -9` non.
- **Constat 7** : dépend de ce que renvoient les deux points d'accès.

## Vérifié sans constat

Argent :
- **Prix de 2.2** (calculs refaits à la main, `test_verifications_sans_constat.py`) : Haiku 0,10/0,50, puis 0,50/2,50 strictement au-delà de 100 000 jetons d'invite, cache compris dans le seuil ; Sonnet 2/10 ; Opus 4/20 ; écriture en cache 1,25 ; lecture 0,1 (0,05 pour Opus) ; le client simulé est compté, à son prix, dans la même tentative. LiteLLM 1.81.11 met bien le cache dans `prompt_tokens` (llms/anthropic/chat/transformation.py:1373-1396).
- **Seuils** : 80 % à la vague 1 ; le plus petit de 95 % et du plafond moins 15 $ à la vague 2 ; refus d'un plafond dont le seuil serait nul.
- **Refus** : plafond au-delà de l'accord, de 1,5 fois l'estimation (vague 1), de 1,25 fois l'estimation refaite ou du budget restant (vague 2) ; valeurs nulles, négatives, NaN ou infinies ; accord obligatoire dans tous les modes ; plafond et accord redonnés et recontrôlés à chaque reprise. Vague 1 du plan : 1 430 parties, 60,53 $, plafond permis 90,78 $.
- **Réduction C9** : identique, sur 300 tirages (coûts, parties déjà jouées, budgets), à une recherche par force brute écrite à part : plus grand facteur au centième, arrondi inférieur exact, au moins un passage, 1,25 fois le total au plus le budget, refus si impossible.
- **Comptable** : le seuil est lu avant chaque retrait de la file, sous le même verrou que l'ajout du coût ; le coût de chaque tentative est compté (échecs, relances, interruptions) ; en reprise séquentielle, le coût déjà dépensé est compté une seule fois (lignes de `tentatives.jsonl`, orphelines lues dans leur usage) et le cumul égale la somme des lignes.
- **Essai à blanc** : clé jamais lue (`lire_cle` seulement avec `--reel`) ; environnement des enfants sans clé ni redirection d'URL, proxys cassés, `PILOTE_HORS_LIGNE=2`, refus si une clé y reste ; extraction des outils toujours sans clé ; post-traitement dans le processus du lanceur sans aucun module réseau (verdicts_csv et typage n'affichent que le nombre d'actions).
- **Mode réel** : impossible sans `--reel`, sans accord, avec `--limite` ou avec une autre réserve.

Données :
- **Identifiants** : 14 266 identifiants uniques ; tentatives suffixées `-t<k>`, interruptions suffixées ; `ok` vrai si et seulement si le dossier est dans `parties/` ; le reste va dans `ecartees/`.
- **Ordre** : SHA-256 de « graine|environnement|passage|tâche », sans `random` ; chaque passage joue toute la réserve ; rang relatif ; la vague 1 est exactement le début de chaque configuration (refait à part sur la vraie réserve).
- **Passage et vague** notés à chaque tentative et lus par `entrees.charger_parties`.
- **Définitions d'outils** : extraction relancée à chaque lancement, empreintes et commit comparés, refus au moindre écart ; `--retrieval-config bm25_grep` du lancement et `retrieval_variant` de l'extraction désignent la même chose (τ-bench src/tau2/runner/build.py:558-560).
- **Délai** : `--timeout` existe dans τ-bench (cli.py:154) et donne la terminaison `timeout` (orchestrator.py:247), vérifiée entre deux pas (l. 771 : un pas qui finit plus de 5 min après les 30 min tombe sur le filet) ; WorkBench est tué à 30 min.
- **WorkBench** : le nom des prédictions est pris au lancement (src/evals/inference.py:309-310), donc l'attente d'une seconde du choix 23 suffit ; le champ `error` vaut "", le message d'arrêt, « Context window exceeded » ou `str(e)` (l. 108-122) : le classement suit bien ces textes (sauf constats 5 et 9).
- **Nom de modèle** : relevé à chaque appel, exclusion, rejeu une fois, référence jamais changée : conformes au choix 12. Remarque, sans défaut de code : comme on ne peut savoir sans jouer si l'ancien nom est revenu, chaque reprise faite trop tôt exclut définitivement la partie rejouée.
- **Rapport de vague** : aucun décompte de verdicts ni d'alertes ; seule l'existence d'un verdict est lue (`instrument`) ; ni `resume.*` ni taux de réussite (réserve : constat 5).

## Contre-vérification du 06/11

Faite par le même agent, à la demande du coordinateur, sur le commit 13bdc94 (« corrections des 13 constats ») : `banc/lanceur.py`, `banc/CHOIX_LANCEUR.md` (choix 24 à 35, contradictions 8 et 9), `banc/tests/test_lanceur_revue.py` (29 tests) et les retouches de `banc/tests/test_lanceur.py` (adaptations à la référence par banc et à `--max-retries 0`, sans assertion affaiblie).

**Méthode.**
- Mes 35 reproductions relancées.
- Les tests de l'auteur relancés, puis soumis à des mutations : chaque correction est défaite dans une copie du lanceur, et on regarde si son test échoue.
- Contournements cherchés, chacun reproduit dans un nouveau test.
- Un essai à blanc de 16 parties avec les vrais bancs.
- Le majorant WorkBench confronté aux 30 parties WorkBench du pilote.

**Interdits.** Mêmes interdits que pour la revue : aucun appel réel, aucune clé lue, rien sous `donnees/`, aucun fichier existant modifié hors de cette section, pas de commit. Les 12 dossiers `essai-blanc-vague1-*` laissés par l'essai à blanc dans `externe/tau2-bench/data/simulations/` ont été supprimés (liste revenue à l'état d'avant) ; `externe/workbench-run/data/results/` est resté vide ; les dépôts des bancs sont propres.

**Nouvelles reproductions** (`revues/code/lanceur/`) :
- `test_contre_verification.py` : 10 tests, qui passent tant que le défaut est présent ;
- `mutations_corrections.py` : les 21 mutations ;
- `verif_majorant_workbench_pilote.py` : le majorant face au pilote ;
- `demo_workbench_exception_muette.py` : une exception sans message dans WorkBench.

```
cd ROOT
env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u OPENROUTER_API_KEY \
  simulation/.venv/bin/python -m pytest -q -s -p no:cacheprovider revues/code/lanceur/test_contre_verification.py
env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN -u OPENAI_API_KEY -u OPENROUTER_API_KEY \
  simulation/.venv/bin/python revues/code/lanceur/mutations_corrections.py
```
Résultats :
- `banc/tests/` : 633 passed ;
- `test_contre_verification.py` : 10 passed ;
- mutations : 21 tuées sur 21.

### 1. Mes reproductions : 16 échecs, tous dus aux corrections

Les 19 qui passent sont le témoin R4 (un usage absent avec un champ `error` vide arrête toujours) et les 18 vérifications sans constat (prix, seuils, refus, C9, ordre, environnement à blanc) : leur comportement n'a pas changé. Chaque échec tient à la correction attendue, et à elle seule :

| Reproduction | Échec observé | Correction en cause |
|---|---|---|
| R1, R1b | un seul enfant WorkBench lancé (`[False]` au lieu de `[False, True, True]`) | choix 25 |
| R2 | codes `[4, 2]` : second lancement refusé, un seul dossier | choix 24 |
| R2b | seconde reprise refusée (code 2), rien joué deux fois, `cout.json` = 12 lignes pour 12 fins | choix 24 (verrou) |
| R2c | plus de `FileExistsError` : refus propre | choix 35 |
| R3 | reprise de la vague 1 refusée (code 2) | choix 26 |
| R4 (×3) | arrêt « coût non compté » | choix 27 |
| R5 | une seule tentative : arrêt sur coût inconnu | choix 33 |
| R6 | reprise refusée sans `--cout-retenu` | choix 33 |
| R7 | les deux parties terminées | choix 30 |
| R8 (×2) | `infrastructure_error` : échec technique relancé (2 lignes) ; `user_stop` : terminée | choix 31 |
| R9 | `--max-retries` présent dans la commande | choix 29 |
| R13 | plus d'exception : refus propre | choix 35 |

### 2. Les tests de non-régression voient-ils le défaut ? Oui : 21 mutations, 21 tuées

Pour chaque correction, `mutations_corrections.py` défait la correction dans une copie temporaire du lanceur, la charge à la place de `lanceur`, et relance les seuls tests du constat (`-k test_c<n>_`). Témoin sans mutation : 29 passed. Les 21 mutations sont tuées, chacune par le test du constat (test qui échoue entre parenthèses) :

1. refus du second dossier réel (`test_c1_relancer…`) ; processus vivant du verrou ignoré (`test_c1_verrou_vivant…`, deux tests) ;
2. arrêt non revérifié après le verrou WorkBench (`test_c2_…`) ;
3. marqueur non lu (`test_c3_reprise…`) ; marqueur écrit quel que soit le mode (`test_c3_vague_2_a_blanc…`) ;
4. « appels faits » seulement si `error` est vide (`test_c4_…`, trois cas) ; pas de majorant tiré des traces (`test_c4_…_majore…`) ;
5. exception d'outil traitée en échec technique (`test_c5_exception…`, `test_c5_…_en_serie`) ; pas d'arrêt sur la série (`test_c5_…_en_serie`) ; « LLM call exceeded » hors des erreurs d'API (`test_c5_erreurs_d_api…`) ;
6. sans `--max-retries 0`, ou dépassement de contexte classé en échec technique (`test_c6_tau2…`) ;
7. référence de nom commune aux deux bancs (`test_c7_…`) ;
8. filet sans regarder la trace (`test_c8_…`, deux cas) ;
9. fenêtre de contexte WorkBench gardée (`test_c9_…`) ;
10. `results.json` n'est plus une preuve de départ (`test_c10_…`) ;
11. reprise sans montant retenu, ou montant retenu hors du cumul (`test_c11_cout_inconnu…`) ; vague 2 malgré un coût inconnu en vague 1 (`test_c11_vague_2…`) ;
12. enfants sans `PYTHON_DOTENV_DISABLED` (`test_c12_…`) ;
13. orphelines illisibles non examinées d'avance (`test_c13_orpheline…`).

Nuance sur le constat 13 : la mutation n'est tuée que par la seconde moitié du test (le `--cout-retenu` y devient « étranger »). Avec une seule orpheline, rien ne peut être déplacé avant l'erreur : le test ne vérifie pas directement « rien de laissé à moitié fait ». Il faudrait une orpheline lisible devant l'illisible, comme dans R13.

### 3. Bilan par constat

| Constat | Soldé ? | Réserve |
|---|---|---|
| 1 | **non, en partie** | La relance à l'identique et la double reprise sont soldées (verrou). Mais `--sortie-racine` contourne le refus (nouveau constat A), et deux lancements qui se chevauchent passent tous les deux (B). |
| 2 | oui | — |
| 3 | oui pour le cas prouvé | course résiduelle avec une reprise de la vague 1 qui démarre (D) |
| 4 | oui | Le majorant n'est pas un majorant prouvé (G). |
| 5 | oui (plus de relance, rapport compté par environnement) | Le journal désigne quand même la partie et le modèle, par élimination (E). Frontière API / outil imparfaite (I). |
| 6 | oui | `--max-retries 0` accepté par le vrai τ-bench (essai à blanc). Le type `ContextWindowExceededError` est bien celui que τ-bench enregistre : LiteLLM le lève pour « prompt is too long » (exception_mapping_utils.py:621-623), τ-bench le relance tel quel (llm_utils.py:684-686) et note son nom (runner/progress.py:130). |
| 7, 8, 9 | oui | — |
| 10 | oui | Règle trop large : arrêt et montant à saisir pour des tentatives sans aucun appel (F). |
| 11 | oui | Montant « lu dans la console » : la console ne donne pas le coût d'une tentative (F). |
| 12 | oui | `demo_dotenv.py` relancé avec `PYTHON_DOTENV_DISABLED=1` : aucune variable chargée, dans les deux venvs. |
| 13 | oui | voir la nuance de la section 2 |

### 4. Nouveaux constats

Les constats A, B, D, E, F et G viennent des corrections, ou de leurs limites. C, H et I préexistaient, sans avoir été vus à la revue.

**A. À corriger : `--sortie-racine` contourne le refus d'un second dossier réel (constat 1 rouvert).**
- **Endroit.** lanceur.py:1820-1823 : le refus ne regarde que la racine donnée, et l'option reste libre en réel.
- **Constat.** La même commande avec une autre racine ouvre un second dossier réel, une autre graine et un second plafond. Le contournement tient à une seule option, déjà là, et le premier refus pousse à la chercher.
- **Preuve.** `test_CV1` : `codes : même racine 4 puis 2 ; autre racine 4 ; dossiers réels : ['s/vague1/…', 'ailleurs/vague1/…'] ; dépense totale 4.80 USD pour plafond = accord = 3`.
- **Correction minimale.** En réel, refuser `--sortie-racine` s'il ne désigne pas `experience/` (`SORTIE_RACINE`).

**B. À corriger : deux lancements réels qui se chevauchent ouvrent deux dossiers.**
- **Endroit.** Le contrôle a lieu dans `preparer` (l. 1823), le dossier est créé dans `mettre_en_place` (l. 2006). Entre les deux : la clé et l'extraction des outils (quelques secondes en réel, jusqu'à 900 s).
- **Constat.** Une commande lancée deux fois de suite, ou un agent qui « réessaie » pendant ce temps, passe le même contrôle.
- **Preuve.** `test_CV2` : `codes : second [4], premier 4 ; dossiers réels de la vague 1 : ['…05-28-51', '…05-28-52'] ; dépense 4.80 USD pour plafond = accord = 3`.
- **Correction minimale.** Refaire le contrôle et créer le dossier sous un `flock` du dossier `vague<N>/` de la racine (même mécanisme que `prendre_verrou`).

**C. À corriger (antérieur aux corrections) : WorkBench écrit dans un dossier commun à tous les lanceurs.**
- **Endroit.** lanceur.py:756 : `verrou_wb` ne vaut que dans un processus, et le verrou du choix 24 que sur un dossier de vague. Or tous les lanceurs font écrire WorkBench dans le même `externe/workbench-run/data/results/` et y ramassent « les fichiers nouveaux ».
- **Constat.** Un essai à blanc lancé pendant la vague réelle (« plusieurs essais restent permis », choix 24) fait ramasser ses fichiers par une partie réelle, ou l'inverse. Cas général : deux csv, échec technique et relance. Pire cas, même modèle, même domaine et même seconde : la prédiction factice écrase la vraie, et la partie réelle la garde comme terminée. Une donnée fausse entre dans `parties/`.
- **Preuve.** `test_CV8` : `partie réelle : ok=True classée terminée ; sa prédiction contient FACTICE ; partie à blanc : csv de prédictions absent`.
- **Correction minimale.** Un `fcntl.flock` exclusif sur un fichier de `workbench-run/data/results/`, tenu pendant toute la partie WorkBench, en plus de `verrou_wb`. Il sérialise les parties WorkBench entre processus.

**D. Mineur : une vague 2 lancée pendant la mise en route d'une reprise de la vague 1.**
- **Endroit.**
  - La reprise de la vague 1 lit `vague2.json` dans `preparer` (l. 1838), sous son verrou.
  - La vague 2 écrit ce marqueur (l. 2021) sans prendre ce verrou, et n'exige que `fin` dans le `cout.json` de la vague 1 (l. 1877).
  - Ce `cout.json` reste celui du lancement précédent tant que la reprise n'a pas fini sa mise en route.
- **Constat.** Les deux jouent les parties restantes de la vague 1. Il faut deux gestes dans les mêmes secondes.
- **Preuve.** `test_CV3` : `codes : vague 2 [0], reprise de la vague 1 0 ; marqueur posé : True ; la reprise a joué ['WorkBench-opus-p01-email_1'] ; gardée en vague 1 […], en vague 2 […]`.
- **Correction minimale.** Pour `--vague 2` (hors aperçu), prendre aussi le verrou du dossier de la vague 1 avant `preparer`, comme pour `--reprendre`, et le garder pendant la vague 2.

**E. Mineur : le journal désigne quand même la partie et le modèle d'une exception d'outil.**
- **Endroit.** lanceur.py:1257 (ligne « début », qui nomme partie et modèle) et l. 1278 (fin anonyme).
- **Constat.** Toutes les autres fins sont nommées, et les parties WorkBench passent une à une : la tentative WorkBench restée sans fin nommée est celle de l'exception. Le journal s'affiche à la console, sous les yeux de l'opérateur, et Otsoa est le relecteur à l'aveugle.
- **Preuve.** `test_CV4`, deux parties à la fois, τ-bench intercalé : `fins anonymes au journal : 1 ; tentatives sans fin nommée, avec leur modèle : {'WorkBench-sonnet-p01-email_1': 'claude-sonnet-5-5'} ; exceptions d'outil réelles : ['WorkBench-sonnet-p01-email_1']`.
- **Correction minimale.** Pour les tentatives WorkBench, des lignes « début » et « fin » au journal sans partie ni modèle (le détail reste dans `tentatives.jsonl` et `cout.json`).

**F. Mineur : la « preuve de départ » de τ-bench est trop large.**
- **Endroit.** lanceur.py:566 et 721 : `results_existe`. Or τ-bench écrit `results.json` (sans simulation) dès la préparation du lot, avant tout appel (runner/checkpoint.py, `try_resume`, l. 74).
- **Constat.** Sont traitées en coût inconnu, avec arrêt du lanceur et montant à saisir à la reprise, des tentatives qui n'ont fait aucun appel facturé :
  - un premier appel en échec : avec `--max-retries 0`, simulation vide `infrastructure_error`, et pas de JSONL puisque l'échec n'est pas facturé ;
  - un Ctrl-C pendant le démarrage (chargement, index bm25 de la banque), avec deux ou trois parties en vol.

  Le choix 33 demande un montant « lu dans la console », qui ne donne pas le coût d'une tentative : l'opérateur saisira 0 en lisant `logs/<id>.log`. L'argent n'est pas en jeu. Mais lors d'une panne d'API, ou après chaque Ctrl-C, il faudra une saisie à la main, sans repère dans le code.
- **Preuve.**
  - `test_CV5` : `statut=échec technique cout_inconnu=True terminaison='infrastructure_error (InternalServerError)' ; arret : … reprendre avec --cout-retenu …` ;
  - `test_CV5b` : `statut=interrompue cout_inconnu=True ; en suspens : ['banque-opus-p01-task_001-interrompue-t']`.
- **Correction minimale.** Ne tenir pour coût inconnu que l'absence de JSONL après une simulation avec messages, ou après le filet. Une capture en panne serait de toute façon vue à la partie normale suivante, par le croisement. À défaut, donner au journal la règle de saisie (« 0 $ si `logs/<id>.log` ne montre aucun appel abouti ») au lieu de la console.

**G. Mineur : le majorant WorkBench n'est pas un majorant prouvé.**
- **Endroit.** lanceur.py:588-605 ; choix 27 (« ne peut que surestimer »).
- **Constat.** La borne de sortie (octets visibles plus 1 000) ignore les jetons de raisonnement, facturés en sortie mais absents des traces. Au pilote, un appel Haiku a facturé 6 409 jetons de sortie, quand la plus longue sortie tracée de la partie fait 460 octets. Le majorant a tenu sur les 30 parties (rapport minimal 5,2), seulement grâce à la borne d'entrée, très large (définitions d'outils et invite du mode texte comptées à chaque appel). Un appel à long raisonnement sur une invite courte le dépasserait.
- **Preuve.** `verif_majorant_workbench_pilote.py` :
  - `WorkBench-haiku-6 : jetons de sortie facturés par appel [127, 282, 6409, 5389] ; octets de sortie tracés par étape [130, 152, 156, 154, 154, 238, 460]` ;
  - de même `opus-6` (1 997 jetons contre 733 octets au plus) et `sonnet-6` (2 553 contre 332) ;
  - `parties où le majorant est sous le coût réel : 0 sur 30`.
- **Correction minimale.** Borner la sortie de chaque appel par le maximum de sortie du modèle (valeur à relever pour les modèles 5.5), et non par les octets visibles. À défaut, retirer « majorant » et « ne peut que surestimer » du choix 27 : c'est une estimation prudente, suivie d'un arrêt.

**H. Mineur (antérieur) : une erreur interne laisse une orpheline dans une vague 1 « finie », et la vague 2 ne la voit pas.**
- **Endroit.** lanceur.py:1877-1884 : la vague 2 n'exige que `fin` et aucun coût inconnu dans les lignes du `cout.json` de la vague 1. Or après une erreur interne (choix 16 e), le lanceur finit normalement et écrit `fin`, mais la tentative reste commencée sans fin dans `tentatives.jsonl`.
- **Constat.** Le coût de l'orpheline, dont le JSONL existe, n'est compté nulle part. Une tentative au plus, et la partie est rejouée par la vague 2.
- **Preuve.** `test_CV6` : `vague 1 : code 4, fin=True, orphelines ['WorkBench-haiku-p01-email_15'] ; vague 2 : code 0 ; vague 1 payée 8.00 USD, comptée 7.96 USD`.
- **Correction minimale.** La vague 2 refuse une vague 1 dont `tentatives.jsonl` contient une orpheline (« reprendre d'abord la vague 1 »).

**I. Mineur, limite : la frontière entre erreur d'API et exception d'outil.**
- **Endroit.** lanceur.py:184 (`WB_ERREURS_API`).
- **Constat.** Des anomalies côté API absentes de la liste deviennent des « exceptions d'outil » (erreurs de l'agent, jamais relancées) : `APIResponseValidationError` (« Data returned by API invalid… ») ou une réponse sans choix (« list index out of range »), preuve `test_CV7`. À l'inverse, une exception sans message donne un champ `error` vide : la partie est « terminée » et gardée, sans ses actions (`demo_workbench_exception_muette.py` : `error = '' ; function_calls = [] ; actions faites : ['email.send_email']` puis `('terminée', None, None)`). Aucun déclencheur réel trouvé (les `assert` et `[0]` des outils sont gardés ; reste `assert tc.type == "function"`, agent.py:256).
- **Correction minimale.** Aucune urgente. Déclarer la limite au choix 28.

### 5. Les quatre ajouts de l'auteur

1. **« LLM call exceeded » rangé parmi les erreurs d'API : juste.** C'est le délai de WorkBench lui-même (agent.py:163), levé après les 10 essais de tenacity (agent.py:388) : une panne côté API, pas l'agent.
2. **Arrêt après 3 exceptions d'outil de suite : juste, comme filet** contre une définition d'outil cassée. Le message ne nomme pas de modèle. Coût : des arrêts sans panne, à reprendre à la main, environ N × p³ sur les ~3 900 parties WorkBench (p = taux d'exceptions d'outil des agents ; 0 sur 30 au pilote, donc inconnu : environ 0,5 arrêt si p = 5 %, 4 si p = 10 %).
3. **Aucune option pour passer outre au refus d'un second dossier réel : juste dans l'esprit** (repartir de zéro reste un geste d'Otsoa). Mais `--sortie-racine` en tient lieu tant qu'elle reste libre en réel (constat A).
4. **Marqueur `vague2.json` écrit seulement par une vague 2 du même mode : juste.** Une vague 2 à blanc sur une vague 1 réelle ne joue rien pour de vrai et ne doit pas bloquer la reprise réelle. Une vague 2 réelle sur une vague 1 à blanc est refusée de toute façon. Testé (`test_c3_vague_2_a_blanc…`, tué par la mutation).

### 6. Vérifié sans constat

- **Essai à blanc avec les vrais bancs** après les corrections (`--limite 16`, concurrence 3, sortie hors du dépôt) :
  - 16 parties, sans échec technique : Haiku dans les 4 environnements, Sonnet et Opus en commerce ;
  - `--max-retries 0` accepté par τ-bench ; `PYTHON_DOTENV_DISABLED` sans effet sur les bancs ;
  - nom renvoyé noté par banc (`tau2:…`, `workbench:…`) ;
  - verrou retiré à la fin ;
  - 15 s.
- **Rapport** : par configuration, ni gardées ni terminées, et les exceptions d'outil comptées ni dans les arrêtées ni dans les exclues. On ne peut donc pas retrouver leur nombre par modèle par différence : `tentatives` moins les catégories affichées donne « terminées + exceptions d'outil », sans les séparer. Les nouvelles lignes « coût retenu » ne comptent ni comme partie ni comme tentative (`section_cout`, `section_deroulement`, `historique_parties`). Le moteur et `reussite.py` lisent `cout.json` par identifiant, depuis les dossiers de `parties/` : sans effet pour eux.
- **Argent** :
  - après un `--cout-retenu`, le cumul égale la somme des lignes (montant entré par une ligne et par `deja`) ; un identifiant étranger est refusé, un même montant ne se donne qu'une fois ;
  - un verrou orphelin est repris sous `flock`, un verrou vivant ou d'une autre machine refusé, le verrou retiré après un refus ;
  - seuils, plafonds et C9 inchangés (mes 18 vérifications passent).
- **Tentative « non lancée »** : refermée dans `tentatives.jsonl` sans ligne ni coût, remise en file sous le même numéro, jouée à la reprise.
