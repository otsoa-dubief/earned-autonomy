# Audit avant le gel (09/11) : suites

Verdict de l'audit indépendant : **prêt sous réserve**. Otsoa est d'accord pour faire la mise au propre. Rien n'est gelé, tiré, étiqueté ni déposé.

## Corrigé (le fond ne change pas)

- **O2** : `depots/construire_depot.py` donne maintenant un zip reproductible. Tous les fichiers du paquet prennent la date du commit et des droits fixes, et entrent dans le zip dans l'ordre trié. Tests : deux constructions donnent le même SHA-256, et tous les fichiers portent la date du commit.
  - L'antériorité du 05/11 **ne retrouve pas** son SHA déposé `77c7a11e…` : une reconstruction donne `e44f1985…`. L'objet reproductible est le manifeste. La fiche du 05/11 le dit maintenant, et le SHA du zip se note tel que déposé.
- **O3** : la promesse de vérification du README du gel est réécrite :
  - les lignes du manifeste hors `externe/` se vérifient dans le paquet ;
  - les lignes `externe/` se vérifient avec des clones des bancs aux commits `033bf08` et `49c7dfd` ;
  - `externe/workbench-run/` n'est vérifiable que sur la machine de l'auteur ;
  - les commits des bancs sont dans `GEL.json`, pas dans le manifeste.
- **O5** : « G0 écrite dans le plan » est contrôlé strictement : la ligne doit être juste sous la puce de la graine maîtresse (5.5, point 4), au format `- valeur tirée au gel : G0 = <valeur>`, une seule fois. Le contrôle refuse le nombre écrit ailleurs, écrit deux fois ou faux (4 cas testés).
- **O6** : états périmés harmonisés :
  - plan §9 (état au 09/11) ;
  - plan 5.14 (lecture du 8e passage sous la ligne v7) ;
  - `JOURNAL_CHANGEMENTS.md` (F3 : 3,0 % sur son tirage, puis 4,7 % en cumul) ;
  - rapport du contrôle 3, 12.5 (sortie corrigée en 4ae1fce, empreintes de l'ancien et du nouveau `confirmation.py`).
- **O7, O11** : fiche du gel complétée :
  - 1 307 fichiers ;
  - `GEL.json.commit` est le commit de G0 ;
  - SHA du zip réellement déposé ;
  - relance si `paquets()` échoue ;
  - `pytest depots/tests` seul ;
  - sauvegarde de l'étiquette par `git bundle`.
- **O8** : `CHOIX_PHASE4.md` (contradiction 1 et « ce qui reste ») et `CHOIX_PHASE2.md` (l. 97) portent une ligne datée « tranché par le plan ».
- **O10** : `banc/INSTALLATION.md` et `banc/CHOIX_LANCEUR.md` utilisent `RACINE=$(git rev-parse --show-toplevel)` au lieu de `ROOT`.

## À trancher par Otsoa : textes proposés, non appliqués

### O9 · deux phrases au plan, 5.14

**Point 0 (l. 741)**, à ajouter en fin de point :

> Si la couverture de l'instrument ne peut pas être calculée (aucune écriture ; elle vaut vérifiables ÷ toutes les écritures, `simulation/rejeu/preuves.py`, l. 200), le point 0 n'est pas tenu : R5 (`simulation/rejeu/decision.py`, `point0`, l. 48 à 62).

**Point 2**, après la règle « battu sur la charge » :

> Si des configurations sont délégables mais que la différence de charge moyenne avec un témoin ne peut pas être calculée (aucune configuration où elle est définie), ce témoin n'est pas battu sur la charge ; faute aussi d'un dépassement établi, le point 2 n'est pas tenu : R2 (`simulation/rejeu/decision.py`, l. 295 à 303).

### O4 · deux limites à déclarer au §6, sous « Niveau du max-T » (l. 889)

> - *Taille du bootstrap (limite)* : le niveau publié de F3 a été mesuré avec les réglages du contrôle 3 (B = 200 répétitions bootstrap) ; l'expérience en fait 2 000 (5.5, point 5). Le 97,5e centile du maximum y est estimé plus finement. Le niveau effectif à B = 2 000 n'est pas mesuré : il est seulement supposé proche.
> - *Composition de la famille (limite)* : le niveau du max-T dépend du nombre de cellules testables et de leur corrélation. Il a été mesuré sur les familles des mondes du contrôle 3. Si, dans l'expérience, la famille d'une règle se réduit à 1 ou 2 cellules testables, le max-T revient à un test par cellule, presque sans correction. Le code de sortie publie le nombre de cellules non testables (`simulation/rejeu/sorties.py`, l. 411) ; la mention « niveau non mesuré pour cette taille de famille » sera publiée avec le rapport, hors du calcul figé.

**Choix pour Otsoa sur O4 (b), sans avis** : (1) la mention est écrite dans le rapport, hors du calcul figé, comme proposé ci-dessus ; (2) elle est ajoutée au code de sortie avant le gel (avec un test), pour qu'elle sorte du calcul figé lui-même.

## O1 · statuts ouverts, en mots simples (relecture à l'aveugle : aucun avis)

Pour chacun, la question est la même : **Décidé tel quel / à modifier / à retirer**.

**Plan**
1. **« PROJET » dans le titre (l. 1) et « Statut : projet, non figé » (l. 3).** Ces deux mentions disent que le plan n'est pas encore figé. Au gel, elles disparaissent ou deviennent « figé le … ».
1 bis. **Règle de choix réappliquée sur la confirmation (1.3, point 4, l. 64).** La règle « prudence puis simplicité », qui a servi à choisir B-tout avant le gel, serait refaite sur les données de confirmation, en résultat secondaire, pour dire si les vraies données auraient retenu la même règle.
2. **A-dégâts non reprise (l. 47).** Une des règles candidates, éliminée par la simulation de départ, n'est pas rejouée dans l'expérience. Si elle était reprise, on ajouterait une règle de plus à comparer.
3. **Empreintes à figer (l. 133).** La liste des fichiers dont on garde l'empreinte numérique au gel (tâches, outils, listes de tirage, script du tirage public). C'est ce qui permet de prouver ensuite que rien n'a bougé.
4. **Nom du modèle et définitions d'outils notés à chaque appel (l. 149).** On enregistre quel modèle a vraiment répondu, et quels outils l'agent a reçus, pour repérer un changement discret chez le fournisseur.
5. **Retrait des tâches défectueuses (l. 357, et REGLE l. 382).** Une tâche dont les propres fichiers se contredisent (cas a1 à a4 du plan, 4.5) est retirée en entier, pour tous les modèles, et chaque retrait est publié.
6. **Lanceur de l'expérience (l. 406).** Le programme qui fait jouer les agents : plafond de dépense par vague ; la vague 1 s'arrête à 80 % de son plafond, la vague 2 au plus petit de 95 % du plafond ou du plafond moins 15 $ (`banc/lanceur.py`, l. 148 à 151 et 374-375 ; plan 2.5) ; arrêt si le nom du modèle change.
7. **Graines (l. 504).** Le nombre de départ du hasard est tiré une seule fois au gel et écrit dans le plan, pour que tous les calculs soient refaisables à l'identique.
8. **Ratées groupées par tâche (l. 650).** Dans un test de résistance hors verdict, on simule que toutes les erreurs d'une tâche sur dix passent inaperçues, pour voir comment la règle tient.
9. **Traces WorkBench désalignées (4.7, point 4, l. 405 ; listé l. 22, sans statut).** Signaler les cas où le banc a enregistré un résultat d'outil vide, à cause d'un décalage.
10. **2.2 encore « Proposé » (listé l. 23).** C'est le même point que le 4 : le lanceur le fait déjà.

**REGLE**
11. **« En cours d'écriture » (l. 3) et pièce 2 « (en cours) » (l. 66).** Ces mentions disent que la règle n'est pas finie. Au gel, elles disparaissent ou deviennent « figée le … ».
12. **Épreuve de 3 variantes, « nombre à confirmer par la simulation » (l. 144).** Après une faute, l'agent doit réussir 3 variantes du cas, glissées parmi ses tâches. Le 3 n'a pas été confirmé par une simulation.
13. **Consigne modifiée : réussites comptées pour moitié, « hypothèse, à tester » (l. 164).** Quand la consigne d'un type d'action change, les réussites passées de ce type ne comptent plus que pour moitié.
14. **Points du brouillon « révisables par Otsoa » (l. 351).** Quatre classements : l'argent seulement enregistré par le simulateur compte comme de l'argent ; une suppression définitive est une écriture durable ; le journal de vérification d'identité est un message interne ; les cas mineurs D7 à D10, D12 et D14 suivent le brouillon.
15. **Rappel M6 (l. 436).** Cette ligne dit seulement qu'au gel chacun des points ci-dessus doit être décidé ou retiré : elle disparaît une fois ces choix faits.

**Configuration**
16. **`simulation/rejeu/config_rejeu.json`, « statut » : « PROJET : à figer au gel avec le plan ».** Le fichier de réglages du moteur se dit encore provisoire. Au gel, la mention est retirée en même temps que G0 est tirée.

**Chemins personnels dans des sorties archivées** (contre-vérification)
17. `simulation/rejeu/essai_a_blanc_pilote/meta.json`, `simulation/resultats_e1/journal_execution.log` et `simulation/controle3/resultats_interrompu/journal.txt` contiennent le chemin de la machine d'Otsoa, donc son nom d'utilisateur. Ce sont des sorties archivées : elles ne sont pas modifiées. Question : **accepter** qu'elles le montrent dans le paquet / les **retirer** du périmètre du gel et du paquet.
