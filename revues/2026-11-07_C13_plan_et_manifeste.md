# C13 · Relecture indépendante du plan figé et du manifeste du gel

7 novembre 2026, soir. Relecteur : un agent Claude qui n'a pas suivi les échanges. Mandat : `PLAN_EXPERIENCE.md`, section 7, étape 7 (seconde relecture indépendante et courte, juste avant le gel).

## Résumé

- **Verdict : gelable après corrections.** Le plan n'est pas gelable en l'état.
- **21 constats** : 2 bloquants pour le gel, 11 à corriger avant le gel, 8 mineurs.
- **Bloquant 1.** Le manifeste du gel des verdicts n'a ni contenu écrit, ni code, ni contrôle au rejeu final. Or son empreinte fait la graine du partage.
- **Bloquant 2.** L'impulsion désignée paraît 24 heures après le dépôt OSF. Or un administrateur peut annuler un enregistrement OSF pendant 48 heures : le tirage peut donc être refait.
- **Ce qui tient.** Le calcul de l'étiquette est cohérent entre le plan, `REGLE.md`, le code et le contrôle 3 : ordre des étiquettes, R4 et « preuves insuffisantes », max-T et cellule non testable, B2, méthode d'intervalle, barres et longueurs N.
- **Ce qui ne tient pas, en dehors des bloquants.**
  - Des définitions remplacées restent écrites comme si elles étaient en vigueur.
  - Le texte et le code divergent sur les parties exclues par le lanceur.
  - Rien ne lie techniquement l'exécution (vagues, rejeu final) au code figé.

## Périmètre et méthode

**Versions relues.** Commit 22fe82a (07/11, 20 h 51). Empreintes SHA-256 : `PLAN_EXPERIENCE.md` 344f6326…, `REGLE.md` 90fb8661…, `JOURNAL_CHANGEMENTS.md` 9047f826…, `gel/manifeste.py` 61694ab1….

**Lu en entier**
- `PLAN_EXPERIENCE.md`, `REGLE.md`, `JOURNAL_CHANGEMENTS.md`.
- `gel/manifeste.py`.
- `banc/tirage/tirage_public.py`, `banc/tirage/paires.py`.
- `banc/relecture/accord.py`, `banc/relecture/decisions.py`, `banc/relecture/CONSIGNE_RELECTURE.md`.
- `simulation/rejeu/decision.py`, `maxt.py`, `bout_en_bout.py`, `config_rejeu.json`, `CHOIX_AMENDEMENT_R4.md`.
- Le rapport du contrôle 3, sections 9.3 à 11.
- Les suites du contrôle 1.

**Lu en partie**
- `classes.py` (fonctions de décision), `analyse.py` (oracle), `pipeline.py`, `entrees.py` (retraits).
- `banc/lanceur.py` : en-tête, réduction, post-traitement, plan de jeu.
- `banc/CHOIX_LANCEUR.md` : choix 1 à 16 et 27 à 45, section 5.
- En-têtes de `fiches.py`, `tirage_aveugle.py` et `audit_sans_alerte.py`.
- `depots/construire_depot.py`.
- `SUIVI.md` (dernier état).

**Non ouvert**
- `donnees/`, `pilote/` et les résultats publiés des bancs.
- Certains tests de la suite lisent des sorties du pilote : je n'ai vu que leur verdict.

**Hors mandat.** La revue ligne à ligne du code du verdict (une autre revue s'en charge).

**Réseau.** Une seule lecture : l'aide d'OSF, pour le constat 2.

**Écriture.** Aucun fichier du dépôt n'est modifié, sauf ce rapport. `git status` est identique avant et après. Les tests ont pu réécrire des caches `__pycache__`, que git ignore.

**Gravités** (celles du contrôle 1, élargies)
- **Bloquant pour le gel** : une étape n'est pas calculable telle qu'elle est écrite, ou une garantie annoncée du protocole ne tient pas.
- **À corriger avant le gel** : deux lectures écrites, ou un trou ; il existe une lecture par défaut, ou l'effet sur l'étiquette est indirect.
- **Mineur** : forme, ou effet limité aux mesures secondaires.

**Étiquettes** : [vérifié] = lu ou exécuté ; [déduit] = raisonnement de ma part.

## Vérifications exécutées

Toutes les commandes ont été lancées sans clé (`env -u ANTHROPIC_API_KEY`). Fichiers temporaires dans le bac à sable du mandat.

| Vérification | Résultat |
|---|---|
| `simulation/.venv/bin/python gel/manifeste.py --apercu` | 351 fichiers (plan 1, règle 1, banc 66, gel 2, simulation 279, externe 2). Seul empêchement : G0 pas tirée. Bancs aux commits 033bf08 et 49c7dfd, sans modification locale |
| `pytest -q -p no:cacheprovider gel/tests banc/tests simulation/rejeu/tests simulation/tests simulation/controle3/tests` (sans `ANTHROPIC_API_KEY` ni `OPENAI_API_KEY`) | 1 027 réussis, 1 échec attendu (xfail strict de M1, documenté en 5.14, point 2), en 177 s |
| Barres, N de B-tout, N de B-régulier, N allongés et volumes de certification, recalculés depuis q de `config_rejeu.json` en fractions exactes | identiques au fichier, au tableau de 1.2, à l'annexe A2 et au point 9 de `REGLE.md` |
| `table_outils_sha256` de `config_rejeu.json` | égale à l'empreinte actuelle de `banc/table_outils.json` (d4a8e29b…) |
| `paires.py` relancé vers le bac à sable | `paires.json` identique octet pour octet (053e091b…). Empreintes internes à jour (table, réserve). 379 paires, 2 tâches seules (commerce, banque) : conforme au tableau de 3.2 |
| Effectifs et coûts, recalculés depuis `lanceur.py` (`PASSAGES`, `COUT_PILOTE`) et `reserve.json` | 760 tâches, 14 266 parties, 595,73 $. Vague 1 : 1 430 parties, 60,53 $, plafond permis 90,788 $ (écrit 90,78 $, arrondi vers le bas) |
| `git status --ignored` dans les deux bancs, résultats publiés exclus | aucun fichier d'entrée hors suivi ; seulement des `__pycache__` et `data/simulations/` (sorties). `tau2` et `workbench` sont installés en mode éditable : leur code est couvert par le commit |
| Versions des trois environnements | τ-bench : Python 3.12.13, LiteLLM 1.81.11. WorkBench : Python 3.14.9. Simulation : Python 3.14.9 |
| Chiffres de 1.5, de 5.14 (point 2) et de 5.16 (points 10 et 11) | conformes au rapport du contrôle 3 (10.1 à 10.8, 11.1, 11.2) |

## Constats

### 1 · Bloquant · Le manifeste du gel des verdicts n'existe pas

**Emplacements** : PLAN_EXPERIENCE.md:277, :282, :358, :405, :412, :853 ; REGLE.md:195 ; banc/tirage/tirage_public.py:372 ; simulation/rejeu/bout_en_bout.py:285, :303, :381.

**Écrit**
- La graine du partage est le SHA-256 de « l'empreinte du manifeste du gel (verdicts confirmés, tâches retirées, script final) » et de la valeur de la balise (3.4, point 2).
- « Les entrées 1 à 4 sont figées, avec leur empreinte, avant le tirage public » (5.2).

**Problème**
- [vérifié] Aucun texte ne dit quels fichiers forment ce manifeste, ni sous quel format.
- [vérifié] Aucun code ne le construit (recherche dans `banc/`, `simulation/` et `gel/`). `tirage_public.py tirer --manifeste` prend une chaîne hexadécimale libre.
- [vérifié] Le rejeu final prend ses entrées en arguments libres : `--dossier`, `--vague NOM=decisions.csv,alertes.json,accord.json` et `--retirees`. Il note leurs empreintes dans `meta.json`, mais ne les compare à rien.
- [vérifié] `--retirees` (« tâches retirées hors motif a ») accepte n'importe quelle liste. Le plan ne prévoit que les retraits du motif a, dont ceux de l'audit, et n'exige pas leur fichier.
- [vérifié] `reussite.csv`, qui fait partie de l'entrée 1 de 5.2, est calculé au rejeu final s'il manque, donc après le tirage.
- [déduit] Après le tirage, rien n'empêche techniquement de rejouer avec d'autres décisions, une autre liste de retraits ou une vague incomplète. Seul un recoupement manuel avec un dépôt au contenu non défini le montrerait.
- [déduit] Ce code s'exécute après la collecte. S'il est écrit après le 18/11, il est postérieur au gel.

**Correction**
- Écrire en 3.4 et en 5.2 la liste exacte des fichiers du manifeste :
  - par vague : `actions_typees.csv`, `actions.csv`, `cout.json`, `tentatives.jsonl`, `plan_de_jeu.json`, les traces de `parties/`, `reussite.csv` (calculé à ce moment, sans affichage), `decisions.csv`, `alertes.json`, `accord.json`, les tirages de la relecture et la relecture des alertes fortes ;
  - pour l'audit : `audit_tirage.json`, `audit_conclusion.json`, `taches_retirees_audit.json` ;
  - la liste des retraits du motif a et les oppositions d'Otsoa (constat 9) ;
  - l'empreinte de `gel/MANIFESTE_SHA256.txt` et le commit du gel du plan.
- Écrire et figer avant le 18/11 le script qui construit ce manifeste, au format « sha256  chemin » trié. `tirage_public.py` lit ce fichier et calcule lui-même son empreinte.
- Au rejeu final :
  - refuser toute entrée dont l'empreinte diffère du manifeste désigné par `empreinte_manifeste` dans `partage.json` ;
  - retirer `--retirees`, ou le limiter au fichier de l'audit inscrit au manifeste.

### 2 · Bloquant · Vingt-quatre heures après le dépôt, l'enregistrement OSF est encore annulable

**Emplacements** : PLAN_EXPERIENCE.md:282 ; REGLE.md:196 ; banc/tirage/tirage_public.py:40 (`DELAI = timedelta(hours=24)`) et :142.

**Écrit** : « la première impulsion de la balise du NIST […] datée d'au moins 24 heures après l'horodatage du dépôt par OSF. Ce nombre n'existe pas au moment du dépôt : personne ne peut choisir le tirage. »

**Problème**
- [vérifié, [aide d'OSF](https://help.osf.io/article/164-submit-your-draft-registration)] Après la soumission d'un enregistrement, les administrateurs ont 48 heures pour l'approuver ou l'annuler. Un refus le renvoie en brouillon. La date retenue est celle de la soumission.
- [déduit] L'impulsion désignée paraît à 24 heures, alors que l'enregistrement est encore annulable. Avec les données et le code en main, on peut calculer le partage, annuler, puis resoumettre : nouvelle date, donc nouvelle impulsion. Un brouillon annulé ne laisse aucune trace publique. Si le dépôt est un simple fichier, il peut être supprimé ou remplacé.
- [vérifié] Le plan ne dit pas non plus :
  - quel objet OSF est déposé (enregistrement ou fichier) ;
  - quel horodatage fait foi (soumission ou approbation) ;
  - qu'un seul dépôt compte.
- [vérifié] `--depot` est saisi à la main.

**Correction**
- Désigner l'impulsion au moins 24 heures après que le dépôt est devenu irrévocable. Par exemple : 72 heures après la soumission (`DELAI` = 72 h), ou 24 heures après l'approbation, Otsoa approuvant aussitôt.
- Écrire trois règles :
  - un seul enregistrement du gel des verdicts compte ; tout autre, annulé ou non, est déclaré ;
  - l'identifiant OSF et les deux horodatages vont dans `impulsion.json` ;
  - `verifier --en-ligne` les relit.
- Le délai est un choix « Tranché par Claude » (3.4) : il se change avant le gel sans demander de décision à Otsoa.

### 3 · À corriger · Rien ne lie l'exécution au code figé

**Emplacements** : gel/manifeste.py:17 ; banc/lanceur.py:1515-1527 et :2251-2276 ; simulation/rejeu/bout_en_bout.py:104 et :212 ; PLAN_EXPERIENCE.md:284-285 ; REGLE.md:193, clause (3).

**Écrit**
- Le code est figé.
- « Le rejeu final tourne une seule fois, d'un seul script. »
- Une relance n'est permise que pour une panne, « et elle est notée ».

**Problème**
- [vérifié] Ni le lanceur ni le rejeu final n'appellent `manifeste.py --verifier`. Ni l'un ni l'autre ne note le commit du dépôt ou l'empreinte du manifeste (`plan_de_jeu.json`, `meta.json`).
- [vérifié] Les verdicts et le typage sont calculés par le lanceur à chaque vague (post-traitement : `verdicts_csv`, puis typage). Le rejeu final relit ces CSV sans les recalculer.
- [vérifié] Le rejeu final écrit dans un dossier existant (`exist_ok=True`) et ne tient aucun journal de ses lancements.
- [déduit] Un code modifié entre deux vagues, ou un rejeu final lancé plusieurs fois, ne laisse aucune trace automatique.

**Correction**
- En réel, le lanceur (à chaque lancement et à chaque reprise) et le rejeu final appellent `verifier()` et refusent de partir au moindre écart. Ils notent le commit, l'étiquette git et le SHA-256 du manifeste.
- Le rejeu final refuse un dossier de sortie non vide. Il ajoute chaque lancement (heure, empreintes des entrées, code de sortie) à un journal déposé avec les résultats.
- Au gel des verdicts, recalculer `actions_typees.csv` depuis les traces avec le code figé, et comparer.

### 4 · À corriger · `tirage_public.py` peut donner deux partages pour une même impulsion

**Emplacements** : banc/tirage/tirage_public.py:22-24, :375-376, :393-395 ; PLAN_EXPERIENCE.md:279.

**Écrit** : « paires, retenues » ; le plus petit rang de chaque paire va à la calibration.

**Problème**
- [vérifié] `--paires` est facultatif et n'a pas de valeur par défaut. Sans lui, le script fait le partage simple.
- [vérifié] `--reserve` et `--manifeste` sont libres. `verifier` refait le tirage avec les fichiers qu'on lui donne, sans les comparer au manifeste du gel.
- [déduit] Une même impulsion donne deux partages, avec et sans `--paires`. Le choix ne se voit que dans `empreinte_paires` de `partage.json`.

**Correction**
- `--paires` pointe par défaut sur `banc/tirage/paires.json` et devient obligatoire ; la réserve est fixe.
- `tirer` et `verifier` comparent les empreintes de `reserve.json` et de `paires.json` à `gel/MANIFESTE_SHA256.txt`.
- Le manifeste est lu comme un fichier (constat 1).

### 5 · À corriger · Des définitions remplacées restent écrites comme si elles étaient en vigueur

**(a) Oracle et délégabilité.** Emplacements : PLAN_EXPERIENCE.md:263, :527, :630, :663, :729 (phrase d'ouverture), :779, :1006 ; simulation/rejeu/temoins.py:109-117 ; simulation/rejeu/rejeu.py:73-75.
- **En vigueur** (PLAN :662 ; décisions Q14 et N1) : la délégabilité et l'oracle se lisent sur le taux médian. Le code du rejeu final fait cela (`analyse.py:65-72`, `palier_par_type`, qui appelle `estime_sous`).
- **Encore écrit** :
  - l'oracle et « délégable » lisent la classe prouvée « sous la barre » (borne haute au plus la barre) ;
  - « ce classement est le seul » (:630) ;
  - un type « indéterminé » n'est pas délégué par l'oracle (:1006).
- Seule la ligne :663 est précédée d'un « remplace la lecture suivante ».
- [vérifié] Le code figé contient aussi l'ancien oracle (`temoins.paliers_oracle`). `rejeu.py`, module de la phase 1, l'appelle ; le rejeu final n'appelle pas `rejeu.py`, que seuls des tests utilisent.
- **Effet** : la part du gain de l'oracle, qui est descriptive. Pas l'étiquette.

**(b) Relance et « indécise = échec ».**
- **Encore écrit** :
  - PLAN :55 : « Une cellule « indécise » après relance compte comme un échec » ;
  - PLAN :668-669 : relance à 8 000 répétitions, et « si elle reste indécise, elle compte comme un échec ».
- **En vigueur** : PLAN :98 et :665-666 (Q13 ; « le code n'a plus de relance »).

**(c) Témoins obligatoires.**
- **Encore écrit** : PLAN :57-58 ne cite que la liste fixe et le tri par le risque.
- **En vigueur** : depuis Q15, « tout faire valider » est un troisième témoin obligatoire (PLAN :725 ; REGLE :284).

**(d) Réduction des passages.**
- **Deux lectures** :
  - PLAN :205 : on réduit « si le total refait dépasse le budget restant », jusqu'à ce que ce total tienne ;
  - PLAN :204 (décision d'Otsoa du 06/11) et le code (`lanceur.py:446-461`) : 1,25 fois le total réduit doit tenir dans le budget restant.
- **Exemple** : avec 700 $ de budget restant, :205 ne réduit rien, alors que le code réduit (`CHOIX_LANCEUR.md`, choix 10).

**Correction** : une seule définition par point, écrite au présent. L'ancienne va dans une note « Définition remplacée (date, décision) », comme en 1.5 pour R4. Retirer ou marquer l'ancien oracle dans le code de la phase 1.

### 6 · À corriger · Dans `REGLE.md`, l'ordre de B2 ignore « preuves insuffisantes »

**Emplacement** : REGLE.md:370. **En regard** : PLAN_EXPERIENCE.md:109 et :737 ; simulation/rejeu/decision.py:32.

**Écrit** : « l'on garde l'étiquette la moins favorable des deux, dans l'ordre R5, R1, R4, R2, puis « confirmée » ».

**Problème** [vérifié]
- Ni « volume insuffisant » (N1) ni « preuves insuffisantes » (07/11) ne figurent dans cet ordre.
- Le plan et le code placent « preuves insuffisantes » entre R1 et R4, et la font l'emporter sur R4.
- Or `REGLE.md` fait foi sur la règle (PLAN :6).

**Correction** : ajouter au point 7 de `REGLE.md` une lecture datée qui donne l'ordre complet.

### 7 · À corriger · Parties exclues pour exception d'outil ou fenêtre de contexte : le plan dit autre chose que le code

**Emplacements** : PLAN_EXPERIENCE.md:389 et :459 ; JOURNAL_CHANGEMENTS.md:36 ; banc/CHOIX_LANCEUR.md:32 (choix 14), :46 (choix 28), :47 (choix 29), :50 (choix 32), :119-129 ; banc/lanceur.py:55-58.

**Écrit dans le plan**
- Une « exception de WorkBench » est un échec technique : relancée une fois, puis exclue.
- G(c, S) ne retire que les tâches retirées et les échecs techniques ; les parties arrêtées sont gardées.

**Fait par le code** (choix 28, 29 et 32) : deux cas deviennent des parties « arrêtées sans trace exploitable », exclues et jamais relancées :
- une exception d'outil dans WorkBench (« le plus souvent une erreur de l'agent ») ;
- un dépassement de la fenêtre de contexte, dans les deux bancs.

**Problème**
- [vérifié] Il y a deux définitions écrites. La section 5 de `CHOIX_LANCEUR.md` se dit « inscrite par le coordinateur » au journal et au plan, mais ses lignes 128-129 n'y sont pas.
- [déduit] Ces exclusions portent sur des comportements de l'agent, perdus avec toute leur partie. Les taux d'erreur de WorkBench sont donc biaisés vers le bas, dans le sens qui favorise la délégation. Or c'est sur WorkBench que porte le poids confirmatoire (section 8).
- Aucune limite n'est déclarée en section 6.

**Correction**
- Réécrire 4.7 (point 5) et 5.5 (point 1) avec les trois catégories.
- Déclarer la limite en section 6.
- Publier, après la dernière vague, le nombre de ces parties par configuration.
- Envisager une sensibilité écrite d'avance : par exemple, compter chaque exception d'outil comme une erreur refusée du type de l'outil cité, quand il est identifiable.
- Compléter le journal.

### 8 · À corriger · Aucune règle ne dit qui l'emporte entre le texte et le code figé

**Emplacements** : REGLE.md:177 et :193 ; PLAN_EXPERIENCE.md:6.

**Problème**
- [vérifié] Les constats 5 et 7 montrent des écarts entre le texte et le code. Aucune règle ne dit lequel fait le calcul confirmatoire.
- [déduit] Un écart trouvé après le tirage permettrait de choisir la lecture au vu des résultats.

**Correction** : écrire, en pièce 9 ou en section 0, une règle unique, par exemple : « le code figé fait le calcul confirmatoire ; tout écart au texte est déclaré, et le calcul selon le texte est publié comme exploratoire ». Préciser que les fichiers `CHOIX_*.md` figés en font partie.

### 9 · À corriger · Retraits du motif a : l'opposition d'Otsoa n'a pas de chemin, et le cas n'est pas contrôlé

**Emplacements** : PLAN_EXPERIENCE.md:357-360 ; simulation/rejeu/entrees.py:335-344 ; banc/relecture/decisions.py:62-79 ; banc/relecture/CONSIGNE_RELECTURE.md:36.

**Écrit** : la liste des retraits, avec leurs preuves et leurs cas, est montrée à Otsoa avant le gel des verdicts ; « il peut s'opposer à un retrait, et la tâche reste ».

**Problème** [vérifié]
- Pour les retraits issus de la relecture des alertes, aucun outil ne produit cette liste, et aucune entrée ne porte une opposition jusqu'au rejeu final. Une seule alerte levée pour le motif a retire la tâche d'office. L'audit, lui, a une option `--oppositions`.
- `decisions.py` n'exige pas le cas (a1 à a4) en tête de la preuve. La consigne le demande, et l'audit le contrôle.
- Rien ne règle le cas d'une tâche dont une alerte est levée pour le motif a et une autre confirmée.

**Correction**
- Un outil qui liste les retraits du motif a, avec preuve et cas, sans décompte par modèle.
- Un fichier d'oppositions, inscrit au manifeste du gel des verdicts et lu par le rejeu final.
- Le sort des alertes d'une tâche gardée sur opposition : par exemple, relues pour les motifs b à d, et confirmées sinon.
- Le contrôle du cas dans `decisions.py`.

### 10 · À corriger · Les fiches ne montrent pas les sources que le critère du motif a exige

**Emplacements** : PLAN_EXPERIENCE.md:350-354 et :884 ; banc/relecture/CONSIGNE_RELECTURE.md:16-28 et :89-90 ; banc/relecture/fiches.py:139-171 ; banc/relecture/audit_sans_alerte.py:224-237 et :266.

**Écrit** : un défaut se prouve par le règlement, « les données initiales de l'environnement », la consigne et les actions attendues. Le cas a2 vise un objet absent des données ; le cas a4, un argument introuvable « dans les données accessibles par les outils ».

**Problème**
- [vérifié] La fiche d'une alerte montre seulement les paragraphes du règlement qui citent l'outil. Elle ne montre aucune donnée initiale.
- [vérifié] Pour la banque, aucun document de la base de connaissances n'y figure (« Les règles d'outils détaillées sont dans la base de connaissances »). WorkBench n'a pas de règlement.
- [vérifié] La consigne interdit de chercher ailleurs et dit « Dans le doute, tu confirmes ».
- [vérifié] La fiche d'audit montre, elle, le règlement entier et l'état initial propre à la tâche.
- [déduit] Les cas a1, a2 et a4 et le motif c ne s'appliquent qu'en partie aux alertes, et pas de la même façon selon le banc, ni entre les alertes et l'audit.
- [déduit] Une alerte non levée compte comme une erreur. Cela aide aussi B-tout à battre les témoins : c'est la raison même de B2.

**Correction**
- Soit donner aux fiches d'alerte ce que le critère cite : le règlement entier, les données initiales utiles, les documents bancaires cités par les actions attendues.
- Soit écrire dans le plan et dans la consigne qu'un défaut qu'on ne peut pas prouver sur la fiche ne se lève pas, et déclarer l'asymétrie.
- Dans les deux cas, préciser comment lire le motif c pour WorkBench.

### 11 · À corriger · Les relectures et les tirages peuvent être refaits sans trace

**Emplacements** : PLAN_EXPERIENCE.md:320-321, :337 et :366 ; banc/relecture/tirage_aveugle.py:12 ; banc/relecture/audit_sans_alerte.py:11.

**Problème**
- [vérifié] « Un tirage ne se refait pas » n'est contrôlé que dans le dossier de sortie : un autre dossier permet d'en refaire un.
- [vérifié] Rien n'interdit de relancer la relecture d'un lot d'alertes et de garder le résultat préféré. Aucun journal des lots n'est tenu.
- [déduit] Les décisions sur les alertes et l'accord d'Otsoa sont les seuls leviers encore ouverts après le gel. Ils sont pris au vu des conversations.

**Correction**
- Chaque lot est relu une seule fois. Sa composition, l'empreinte de l'invite et celle de la sortie sont inscrites dans un journal.
- Une relance n'est permise que pour une sortie mal formée, et elle est notée.
- Tous les tirages (relecture, alertes fortes, audit) s'écrivent dans un dossier unique par vague. Le journal entre dans le manifeste du gel des verdicts.

### 12 · À corriger · Le contenu du dépôt OSF du gel n'est écrit nulle part

**Emplacements** : gel/manifeste.py:16 ; depots/construire_depot.py:21 ; PLAN_EXPERIENCE.md:5 ; REGLE.md:199.

**Problème** [vérifié]
- Le manifeste dit « ensuite commit, étiquette git, dépôt OSF », sans liste.
- L'outil de dépôt existant (`INCLUS`) prend `REGLE.md`, le plan, le journal, `simulation/`, `banc/` et `reports/`, mais pas `gel/`. Il manquerait donc le manifeste, `GEL.json`, les environnements et G0.

**Correction**
- Écrire la liste et la procédure du dépôt du gel : `gel/`, le commit, l'étiquette, et le SHA-256 du manifeste dans le texte du dépôt.
- Ajouter `gel` à `INCLUS`.

### 13 · À corriger · Statuts à clore, et texte de 2.1 qui ne décrit pas ce que fait le manifeste

**Emplacements** : PLAN_EXPERIENCE.md:1, :3, :19, :128, :139, :385 ; REGLE.md:3, :66, :432 ; simulation/rejeu/config_rejeu.json:3.

**Problème** [vérifié]
- **Statuts encore ouverts**
  - Les 8 « Proposé » de la section 0.
  - Dans `REGLE.md`, les quatre statuts de M6. Hors de la liste M6 : la pièce 2, marquée « (en cours) », et l'en-tête « En cours d'écriture ».
  - « PROJET », dans le titre du plan et dans `config_rejeu.json`.
  - 4.7, point 4 (traces WorkBench désalignées), sans statut.
  - 2.2, toujours « Proposé », alors que le lanceur le fait déjà.
- **Texte de 2.1.** 2.1 annonce les « empreintes sha256 des fichiers de tâches et des fichiers d'outils des deux bancs ». Le manifeste fige autre chose : le commit des bancs et l'absence de modification locale des fichiers suivis. Il ne prend pas d'empreinte fichier par fichier.

**Correction**
- Clore chaque statut par une décision d'Otsoa (étape 8). Ajouter la pièce 2 à la liste M6.
- En 2.1, écrire le mécanisme réel, ou ajouter au manifeste les empreintes des fichiers de tâches, de données et d'outils des bancs. Je recommande l'ajout : ces fichiers sont peu nombreux, et l'empreinte git est un SHA-1.

### 14 · Mineur · Couverture du manifeste

**Emplacements** [vérifié] : gel/manifeste.py:39, :42, :86-92, :102-105, :108-111.

**Constats**
- **Fichiers non suivis ou ignorés des bancs** : ils ne sont pas contrôlés (`--untracked-files=no`), sauf dans `externe/workbench-run`. Aujourd'hui, il n'y en a aucun qui serve d'entrée (vérifié).
- **Environnements** : le manifeste fige le nom et la version des paquets, pas leur contenu. Ni la plateforme ni le processeur ne sont notés.
- **Verrou** : `externe/workbench-run/data/results.verrou`, un verrou vide, est figé. S'il est supprimé, `--verifier` échoue sans vraie raison.
- **Sources de décisions** : `CADRE.md`, que le plan cite pour des décisions (budget, second accord, trois jeux), n'est pas dans `VIVANTS`. `reports/` non plus.

**Correction**
- Passer à `--untracked-files=normal`, en excluant les sorties connues (`data/simulations`).
- Noter dans `GEL.json` la plateforme (`platform`) et la sortie de `numpy.show_config()`.
- Retirer le verrou de `EXTERNES`.
- Ajouter `CADRE.md` à `VIVANTS`.

### 15 · Mineur · Versions de Python

**Emplacement** : PLAN_EXPERIENCE.md:126 (« LiteLLM 1.81.11 ; Python 3.12 »).

**Problème** [vérifié]
- τ-bench tourne en 3.12.13 ; WorkBench et la simulation, en 3.14.9.
- LiteLLM n'est pas installé dans l'environnement de WorkBench.

**Correction** : donner une version par environnement. Le manifeste les notera de toute façon.

### 16 · Mineur · Les « tests de symétrie » ne sont jamais définis

**Emplacements** : PLAN_EXPERIENCE.md:348, :368 et :884.

**Problème** [vérifié] Ils sont cités trois fois, sans grandeur, sans test et sans code (recherche dans le dépôt).

**Correction** : les définir (par exemple : retraits, tâches jouées et écritures attendues par type, dans chaque moitié), ou retirer la mention.

### 17 · Mineur · L'amendement de la cellule non testable n'est pas reporté partout

- `REGLE.md:280` le place sous la réussite (les témoins) seulement. La lecture de Q13 (`REGLE.md:274`), qui juge B-tout par le même max-T, n'y renvoie pas.
- Les limites de puissance de 1.4 (PLAN :83-84) ne disent pas deux choses : une cellule portée par une seule tâche ne peut pas réfuter B-tout ; et, avec 2 à 5 tâches porteuses, la puissance n'est que de 1 à 7 % à cinq fois le budget (PLAN :723).
- 5.16, point 10 (PLAN :767), renvoie à « 5.14, point 1 » pour la règle remplacée, qui était au point 2.
- 5.15 (PLAN :745) ne cite pas `decision.csv`, que le code écrit et que 5.13 (PLAN :662) cite.

### 18 · Mineur · L'amendement de R4 n'est pas reporté partout

- Q14, en section 8 (PLAN :984-990), ne renvoie ni à N1 ni à l'amendement du 07/11.
- `REGLE.md:281` dit que la délégabilité « décide seulement R4 ». Depuis le 07/11, elle ne suffit plus à décider R4.
- PLAN :101 : « R4 ne dit rien des types à enjeu moyen ou fort » est une conséquence des volumes (aucun de ces types n'est jugeable), pas une règle. Il faut l'écrire comme une conséquence.
- Dans l'échange des rôles, les statuts du point 4 sont combinés selon `CHOIX_AMENDEMENT_R4.md`, choix 5. Le plan ne le dit pas.

### 19 · Mineur · Autres passages périmés

- **5.13, PLAN :656** : la première simulation (repli sur le bootstrap-t, « fragile » sous 90 tâches) est remplacée par :667, sans marque à cet endroit.
- **5.13, PLAN :670** : « fragile » y est défini par une seconde méthode, pour toute cellule. Pour B-tout, PLAN :702 le définit autrement, et le code suit :702.
- **5.13, PLAN :685** : les proportions « suivent la méthode (i) ». Ce passage date du moment où la méthode (ii) était retenue ; le code applique la méthode retenue aujourd'hui, la (iii).
- **4.4, PLAN :341** : le renvoi à « `JOURNAL_CHANGEMENTS.md`, dernière ligne » ne vise plus la dernière ligne.

### 20 · Mineur · L'arrêt manuel de la collecte n'est pas réglé

**Emplacements** : PLAN_EXPERIENCE.md:196-205 ; REGLE.md:193, clause (1).

**Problème** La clause (1) interdit d'ajouter des parties au vu des résultats. Elle n'interdit pas d'en retirer en arrêtant la collecte.

**Correction** : écrire que toutes les parties du plan de jeu sont jouées, sauf arrêt par le plafond ou par un garde-fou écrit, et qu'un arrêt définitif décidé à la main est déclaré avec sa raison.

### 21 · Mineur · Journal des changements

**Emplacements** : JOURNAL_CHANGEMENTS.md:40 et :41.

**Problème** Deux lignes du 06/11 (le code de l'audit ; N1) n'ont pas de colonne « Décidé par ». Les lignes manquantes du lanceur sont traitées au constat 7.

## Vérifié sans défaut

- **Barres, N, N allongés, B-régulier et volumes de certification** : identiques entre la configuration, 1.2, l'annexe A2 et le point 9 de `REGLE.md`. Calcul exact refait.
- **Paires** : l'algorithme de `paires.py` suit 3.4, point 2 (profil d'écritures attendues, types rares d'abord, total, identifiant, voisines). Le fichier se refait à l'identique, et ses empreintes sont à jour.
- **`tirage_public.py`**, conforme à 3.4, points 2 à 6 :
  - le calcul : graine, rangs, strates, moitié arrondie vers le bas pour la calibration, paires, tâche seule envoyée à la confirmation ;
  - le choix de l'impulsion : NIST, fenêtre d'une heure, secours drand seulement sur absence constatée dans l'archive, recoupement par l'adresse de chaîne, hasard de drand égal au SHA-256 de la signature ;
  - la vérification, hors ligne et en ligne.
- **Effectifs et coûts** de 2.3 et de 2.5 : recalculés à l'identique depuis le lanceur.
- **Étiquette**
  - Ordre : R5, R1, « preuves insuffisantes », R4, R2, « confirmée ».
  - Point 4 :
    - une configuration est délégable si un type a un taux médian sous la barre ;
    - R4 exige que chaque configuration jugeable ait un type jugeable dont le dépassement est établi à ρ = 1 ;
    - « preuves insuffisantes » a trois motifs ;
    - la borne se lit à max(0,3 ; ρ̂ propre) si la configuration compte 10 erreurs dans au moins 5 tâches, à ρ = 1 sinon ;
    - ρ* est publié.
  - Concordent sur tout cela : le plan (1.5 et 5.14), `REGLE.md:283` et le code (`decision.point4`, `etiquette`, `classes.statut_configuration`, `depassement_etabli`, `borne_basse`, `rho_bascule`).
- **Cellule non testable** : trois cas ; tolérance (racine de l'epsilon machine, relative au plus grand de l'estimation et du budget) ; sortie du maximum ; c* calculé sur les seules cellules testables ; motif publié. Conforme dans `maxt.py`, dans `decision.cellules` et `depassement_temoin`, et dans les sorties.
- **B2**
  - Seuils : 13 sur 15 et 26 sur 30, au prorata, arrondis vers le haut.
  - La décision d'Otsoa l'emporte sur les cas qu'il a relus.
  - Un désaccord persistant donne un double calcul et l'étiquette la moins favorable, sans R5.
  - Conforme dans `accord.py`, `entrees.py`, `preuves.py` (vue « bruts_vague ») et `bout_en_bout.py`.
- **Méthode d'intervalle** : `resultats_couverture_charge/choix.json` (méthode iii, pire couverture 0,933, seconde méthode « percentile ») est suivi par git et lu par le rejeu final. Conforme à 5.13.
- **Garde-fous du rejeu final**
  - G0 nulle refusée ; R0, B et K figés ; graine de développement pour les essais ; sortie hors du périmètre figé.
  - Graines tirées par répétition (`SeedSequence`), donc indépendantes de `--tranche` [déduit du code].
  - Résultat identique avec un ou deux processus (testé).
- **Manifeste**
  - Il fige les fichiers suivis du périmètre. Un fichier non suivi dans le périmètre est signalé par `--verifier` et bloque `--ecrire`.
  - Bancs : commit et fichiers suivis sans modification.
  - `externe/workbench-run` : ses liens symboliques mènent dans le dépôt WorkBench, couvert par son commit.
  - Trois environnements Python.
  - G0 est tirée une seule fois et doit être écrite dans le plan. Le script refuse un second gel. `donnees/` n'est jamais lu.
- **Lanceur, au regard du plan** : composition et coût de la vague 1 ; seuils d'arrêt (80 %, puis le plus petit de 95 % et du plafond moins 15 $) ; réduction des passages au facteur 1,25 (décision du 06/11) ; au moins un passage par tâche et par modèle ; ordre de jeu ; nom du modèle renvoyé ; réextraction des définitions d'outils ; rapport de vague sans décompte d'erreurs.
- **Critère du motif a** : quatre cas, exclusions, preuve sur les seuls fichiers de la tâche. Texte identique dans le plan (4.5), dans `REGLE.md` (:380) et dans la consigne.

## Réponses aux six questions

1. **Cohérence.**
   - Oui pour le calcul de l'étiquette : le plan, `REGLE.md`, le code et le contrôle 3 concordent.
   - Non sur plusieurs points : les passages périmés (constat 5), l'ordre de B2 dans `REGLE.md` (6), les exclusions du lanceur (7), le moment où `reussite.csv` est calculé (1), les versions de Python (15).
2. **Une seule définition en vigueur ?**
   - Non pour l'oracle et la délégabilité, la relance, les témoins obligatoires et la réduction des passages (constat 5).
   - R4 et la cellule non testable, eux, gardent leur ancienne version marquée « remplacée ».
3. **Les amendements récents.**
   - Ils sont écrits sans ambiguïté dans le plan (1.5 ; 5.14, points 2 et 4) et dans le code.
   - Ils ne sont pas reportés à `REGLE.md:370` (constat 6), ni, plus mineur, à `REGLE.md:274`, en 1.4, en 5.15 et en Q14 (constats 17 et 18).
4. **Le manifeste.**
   - Il fige ce que le plan nomme, avec trois réserves : le contenu du dépôt OSF n'est pas écrit (12) ; les empreintes par fichier des bancs annoncées en 2.1 ne sont pas prises (13) ; les détails du constat 14.
   - Rien ne l'appelle pendant l'exécution (3).
5. **Les failles.**
   - Le manifeste du gel des verdicts n'est ni défini ni contrôlé (constat 1).
   - Le tirage peut être refait en annulant le dépôt OSF (2).
   - Les paires sont facultatives (4).
   - Les exécutions ne sont pas liées au gel (3).
   - Les relectures et les tirages peuvent être refaits (11).
   - Les écarts entre le texte et le code n'ont pas de règle de préséance (8).
6. **Ce qui manque pour geler.**
   - Corriger les constats 1 et 2, en texte et en code, avant le 18/11 ; puis les constats 3 à 13.
   - Tirer G0 et l'écrire dans le plan.
   - Clore les statuts (étape 8).
   - Relancer `--apercu` et les tests, puis relire brièvement les passages changés.

## Verdict

**Gelable après corrections ; non gelable en l'état**, à cause des deux constats bloquants (1 et 2).

Pour geler le 18/11, il faut corriger les deux bloquants, puis les onze constats à corriger. Ensuite, inutile de refaire un contrôle complet : une relecture courte des passages changés et du nouveau script du manifeste des verdicts suffit.

Source extérieure : [aide d'OSF, « Submit Your Draft Registration »](https://help.osf.io/article/164-submit-your-draft-registration), consultée le 07/11/2026.
