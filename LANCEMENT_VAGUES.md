# Lancer une vague de l'expérience

Procédure écrite le 10/11/2026, après l'audit final avant la vague 1 (feu vert avec réserves). Elle ne change rien au plan figé : elle met dans l'ordre ce que demandent `PLAN_EXPERIENCE.md` (2.5, 4.7, section 7) et l'en-tête de `banc/lanceur.py`. En cas d'écart, le plan et le code figés font foi.

Toutes les commandes se tapent **par Otsoa**, dans **tmux**, sur le Mac mini, à la racine du dépôt (`cd ~/dev/autonomie-meritee`). Une session SSH qui tombe ne coupe pas tmux.

## Avant la vague 1

1. **Second accord écrit** (plan, section 7) : une ligne datée dans `SUIVI.md`, avec le montant accordé pour la vague 1, puis commit. Sans elle, on ne lance pas.
2. **Console Anthropic** (Otsoa) : la clé de l'espace « autonomie-meritee » est active ; le crédit prépayé couvre au moins 91 $. Noter la dépense affichée avant le lancement. Aucune limite n'est posée dans la console (Q10) : le plafond du lanceur est le seul mur.
   - Pourquoi : une clé refusée ou un crédit vide fait échouer les parties ; chaque partie en échec est relancée une fois puis exclue pour de bon, et trois échecs de suite arrêtent tout. Une panne franche coûte donc environ 2 parties sur 1 430.
3. **Le gel est intact** :
   ```
   simulation/.venv/bin/python gel/manifeste.py --verifier
   ```
   Attendu : `Conforme au gel.` Sinon, on s'arrête.
4. **Aperçu, sans rien jouer ni écrire** :
   ```
   env -u ANTHROPIC_API_KEY simulation/.venv/bin/python banc/lanceur.py --vague 1 --apercu
   ```
   Attendu : 1 430 parties, environ 60,53 $, plafond permis 90,78 $.

## Lancer la vague 1

5. Dans tmux :
   ```
   caffeinate -i simulation/.venv/bin/python banc/lanceur.py --vague 1 --reel --plafond-usd 90 --accord-otsoa-usd 90
   ```
   - Remplacer 90 par le montant de l'accord ; le plafond ne peut pas dépasser l'accord ni 90,78 $.
   - Deux parties à la fois (défaut, comme au pilote). L'ordre de jeu est tiré et noté par le lanceur.
   - Durée attendue : 5 à 8 heures, hors limites de débit de l'API.
   - Arrêt automatique avant toute nouvelle partie à 80 % du plafond (72 $ pour 90 $).
6. **Dans les dix premières minutes** : `journal.log` du dossier `experience/vague1/<horodatage>/` ne montre pas d'échecs en série ; `modeles_renvoyes.json` porte les noms attendus (`claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5`, ou la forme notée au pilote). Le lanceur prend pour référence le premier nom observé : un changement survenu entre le pilote (05/11) et aujourd'hui ne l'arrête pas, d'où ce contrôle à l'œil.

## Pendant la vague

7. **Ne toucher à rien** dans `banc/`, `simulation/`, `gel/`, `externe/`, ni aux trois environnements Python, jusqu'à la fin de la vague 2 : la reprise revérifie le gel et refuse tout écart.
8. **Ne lire que `journal.log`** et, à la fin, `rapport_vague.txt`. Ne pas ouvrir `journal_complet.log`, `parties/`, `actions*.csv`, ni rien d'autre du dossier (plan 2.5 : « on ne regarde rien d'autre »). À rappeler à toute session Claude ouverte dans ce dépôt.

## À la fin, selon le code de sortie

- **0** : vague jouée en entier. Passer à l'étape 9.
- **4** : vague arrêtée avant la fin. Lire la ligne « ARRÊT » de `journal.log`.
  - **Seuil de 80 % atteint** : c'est prévu ; le reste sera joué par la vague 2. Ne pas reprendre la vague 1.
  - **Interruption, coupure, échecs techniques en série, crédit épuisé** : régler la cause (crédit, réseau), puis reprendre le même dossier :
    ```
    caffeinate -i simulation/.venv/bin/python banc/lanceur.py --vague 1 --reel --reprendre "$PWD/experience/vague1/<horodatage>" --plafond-usd 90 --accord-otsoa-usd 90
    ```
    Le coût déjà dépensé compte dans le plafond.
  - **Coût non compté** : chiffrer la tentative dans la console, puis reprendre en ajoutant `--cout-retenu <ID>=<USD>` pour chaque tentative citée.
  - **Nom de modèle changé** : ne pas reprendre tout de suite. On ne reprend que si l'ancien nom revient ; les parties jouées sous le nouveau nom sont exclues et rejouées une fois à la reprise (plan 2.5, point 6).
  - **Après un arrêt brutal** (machine coupée, processus tué) : vérifier qu'aucun banc ne tourne encore, ou attendre 35 minutes. Si la reprise refuse un fichier « nouveau, hors gel » dans `externe/workbench-run/data/results/`, c'est la sortie d'une partie WorkBench coupée en plein jeu : la déplacer hors du dépôt (ne pas la supprimer, ne pas l'ouvrir), puis relancer la reprise.
- **2** : refus avant tout lancement (vague déjà lancée, dossier verrouillé, coût inconnu non chiffré…). Rien n'a été joué ni dépensé ; lire le message.
- **3** : post-traitement échoué. Les parties sont jouées ; ne rien relancer, demander un diagnostic.

## Après la vague

9. Recouper la dépense de `rapport_vague.txt` avec la console Anthropic.
10. **Copier `experience/vague1/` sur un second support** : ces données ne se refont pas, et `experience/` n'est pas dans git.
11. Vérifier qu'aucune clé n'a fui dans les sorties, sans rien afficher d'autre que des noms de fichiers : `grep -rl 'sk-ant-' experience/` doit ne rien rendre.
12. Noter dans `SUIVI.md` : dates, code de sortie, dépense lue dans le rapport et dans la console, emplacement de la copie.
13. Faire les six vérifications d'entre deux vagues (plan 2.5), **et rien d'autre**, avant la vague 2 (second accord, estimation refaite, commande de l'en-tête de `banc/lanceur.py`).
