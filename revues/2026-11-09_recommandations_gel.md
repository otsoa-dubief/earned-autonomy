# Recommandations avant le gel (09/11)

À la demande d'Otsoa : sur le plan, le gel et le dépôt, nos recommandations passent en premier, argumentées. La relecture à l'aveugle ne vaut que pour le jugement des sorties d'agents. Rien n'est appliqué : ce sont des recommandations. Ni `donnees/`, ni le scellé, ni le pilote brut, ni les résultats de banc n'ont servi.

Appuis : **MESURÉ** (sortie de simulation ou test du dépôt), **DÉDUIT** (raisonnement sur des textes ou du code écrits), **SOURCE** (pratique ou littérature extérieure).

## Choix pratiques déjà faits par Otsoa (notés)

- `presentation/` reste hors du dépôt.
- Formulaire OSF **structuré complet** (OSF Preregistration), pas Open-Ended : réponses champ par champ dans `depots/gel_brouillon/FORMULAIRE_OSF_PREREG.md`.
- Embargo comme le 05/11 (jusqu'au 04/11/2030, levable plus tôt).
- Les trois sorties archivées qui contiennent un chemin personnel sont déposées telles quelles.

## Tableau

| # | Décision | Recommandation | Confiance |
|---|---|---|---|
| 1 | « PROJET » dans le plan | Retirer au gel (formalité) | forte |
| 1 bis | Règle de choix refaite sur la confirmation | Garder, passer à « Décidé » | moyenne |
| 2 | A-dégâts non reprise | Garder, passer à « Décidé » | forte |
| 3 | Empreintes à figer | Modifier : renvoyer au manifeste | forte |
| 4 | Nom du modèle et outils notés | Garder, « Décidé (fait) » | forte |
| 5 | Retrait des tâches défectueuses | Garder, « Décidé » | forte |
| 6 | Lanceur | Garder, « Décidé (fait) » | forte |
| 7 | Graines | Garder, « Décidé » | forte |
| 8 | Ratées groupées | Garder, « Décidé » | forte |
| 9 | Traces WorkBench désalignées | Modifier : limite déclarée | moyenne |
| 10 | 2.2 encore « Proposé » | Fusionner avec le 4 (formalité) | forte |
| 11 | REGLE « en cours d'écriture » | Retirer au gel (formalité) | forte |
| 12 | Épreuve de 3 variantes | Modifier le statut : « fixé à 3, non confirmé » | moyenne (goût) |
| 13 | Consigne modifiée, moitié | Modifier : « non testé par cette expérience » | forte |
| 14 | Quatre classements du brouillon | Garder, « Décidé » | moyenne |
| 15 | Rappel M6 | Retirer une fois tranché (formalité) | forte |
| 16 | `config_rejeu.json`, « PROJET » | Retirer au gel (formalité) | forte |
| O9-0 | Couverture non calculable → R5 | Ajouter la phrase | forte |
| O9-2 | Charge non calculable → R2 | Ajouter la phrase | forte |
| O4 (a) | Niveau mesuré à B = 200 | Ajouter la limite | forte |
| O4 (b) | Famille de 1 ou 2 cellules | Ajouter la limite, mention **dans le code de sortie** | moyenne |

## Détail

### Formalités (1, 10, 11, 15, 16)

- **1, 11, 16** : retirer « PROJET », « Statut : projet, non figé », « En cours d'écriture », « (en cours) » et le `statut` de `config_rejeu.json`, et les remplacer par « figé le <date>, étiquette <étiquette> ». *Appui* : DÉDUIT, plan l. 19 (« chaque statut encore ouvert passe à Décidé ou disparaît »). *Risque* : aucun.
- **10** : le point 2.2 et le point 4 sont le même ; garder une seule mention, « Décidé (fait) ». *Risque* : aucun.
- **15** : la ligne de rappel M6 disparaît dès que les autres sont tranchés. *Risque* : aucun.

### 1 bis · Règle de choix refaite sur la confirmation (1.3, point 4)

- **Recommandation** : garder tel quel, passer à « Décidé », en précisant « résultat secondaire, sans effet sur l'étiquette ».
- **Pourquoi** : B-tout a été choisie avant le gel, sur la simulation puis sur une alerte. Refaire le même choix sur les vraies données dit simplement si les données auraient retenu la même règle. C'est une vérification honnête, déjà codée, qui ne coûte rien. Un résultat différent ne change pas le verdict, mais il serait publié, ce qui est le but d'un préenregistrement.
- **Appui** : DÉDUIT, le code existe et est branché (`simulation/rejeu/decision.py`, `regle_de_choix`, appelé par `bout_en_bout.py`, l. 199). SOURCE, le formulaire OSF demande de déclarer d'avance les analyses secondaires et exploratoires (champ « Exploratory analysis »).
- **Risque si on se trompe** : un lecteur pressé lit « une autre règle aurait gagné » comme un échec ; le libellé « secondaire » le limite.
- **Confiance** : moyenne. On pourrait aussi la retirer sans rien perdre sur le verdict ; je la garde parce qu'elle est déjà codée et dit quelque chose d'utile.

### 2 · A-dégâts non reprise (1.2)

- **Recommandation** : garder, passer à « Décidé ».
- **Pourquoi** : la simulation de départ l'a éliminée, avec 6 cellules hors budget. Son réglage a été étalonné sur des mélanges fictifs, pas sur les vrais environnements. La rejouer ajouterait une règle de plus à comparer, sans rôle dans la décision, et donc du bruit dans les résultats secondaires.
- **Appui** : MESURÉ, `simulation/resultats_e1/RESULTATS_E1.md` (6 cellules hors budget). DÉDUIT, plan 1.2.
- **Risque si on se trompe** : on perd une comparaison descriptive. Elle reste faisable plus tard, hors préenregistrement, puisque le rejeu est hors ligne.
- **Confiance** : forte.

### 3 · Empreintes à figer (2.1, l. 133)

- **Recommandation** : modifier. Texte proposé : « **Décidé** : les fichiers figés et leurs SHA-256 sont ceux de `gel/MANIFESTE_SHA256.txt`, écrits par `gel/manifeste.py --ecrire` ; les commits des bancs et les environnements Python sont dans `gel/GEL.json` et `gel/environnements/`. »
- **Pourquoi** : la liste écrite à la main dans le plan a été dépassée par le vrai mécanisme du gel, qui fige davantage. Dire « c'est le manifeste qui fait foi » évite deux listes qui pourraient diverger.
- **Appui** : MESURÉ, `--apercu` fige 1 304 fichiers, 1 307 avec GEL.json et les environnements. DÉDUIT, plan l. 133 (« Mécanisme réel, 07/11 »).
- **Risque si on se trompe** : aucun sur le fond ; un fichier oublié par le manifeste le serait de toute façon.
- **Confiance** : forte.

### 4 · Nom du modèle et définitions d'outils notés (2.2, l. 149)

- **Recommandation** : garder, « Décidé (fait) ».
- **Pourquoi** : le lanceur note déjà le modèle qui a vraiment répondu à chaque appel, et s'arrête s'il change. Il vérifie aussi l'empreinte des outils avant de jouer, et s'arrête si elle diffère. C'est ce qui protège contre un changement discret du fournisseur pendant l'expérience.
- **Appui** : DÉDUIT, `banc/lanceur.py` (l. 50-51, l. 66 `modeles_renvoyes.json`, `outils_agent.json`), revu et testé le 06/11.
- **Risque si on se trompe** : aucun ; le retirer enlèverait une protection déjà en place.
- **Confiance** : forte.

### 5 · Retrait des tâches défectueuses (4.5, l. 357 ; REGLE l. 382)

- **Recommandation** : garder, « Décidé ».
- **Pourquoi** : le critère est objectif. On ne retire qu'une tâche dont les propres fichiers se contredisent (cas a1 à a4), pas une tâche où l'agent échoue. On la retire en entier, pour tous les modèles et toutes les règles, et chaque retrait est publié. Garder une tâche dont la « bonne réponse » est fausse ferait compter comme erreurs des actions justes, ou l'inverse.
- **Appui** : DÉDUIT, plan 4.5 (cas a1 à a4) ; le registre refuse une levée a sans preuve commençant par son cas (`decisions.py`). SOURCE, c'est la pratique courante des bancs d'agents : SWE-bench Verified a retiré, après relecture humaine, les tâches mal posées ou aux tests erronés (OpenAI, août 2024).
- **Risque si on se trompe** : si le critère était appliqué de façon partiale, on pourrait retirer surtout des tâches gênantes. Le critère fermé, les preuves exigées et la publication de chaque retrait limitent ce risque.
- **Confiance** : forte.

### 6 · Lanceur (4.7, point 5, l. 406)

- **Recommandation** : garder, « Décidé (fait) ».
- **Pourquoi** : le lanceur est écrit, testé, relu par un agent indépendant (1 bloquant et 6 corrections, toutes faites et contre-vérifiées), et essayé à blanc sur deux vagues. Ses arrêts reprennent tes décisions : vague 1 à 80 % du plafond, vague 2 au plus petit de 95 % du plafond ou du plafond moins 15 $.
- **Appui** : MESURÉ, tests du banc (737 réussis avec `gel` et `depots/tests`), essais à blanc de 40 et 30 parties. DÉDUIT, `banc/lanceur.py`, l. 148 à 151 et 374-375 ; plan 2.5.
- **Risque si on se trompe** : un défaut du lanceur coûterait de l'argent, pas un faux verdict ; le plafond codé reste le mur.
- **Confiance** : forte.

### 7 · Graines (5.5, point 4, l. 504)

- **Recommandation** : garder, « Décidé ».
- **Pourquoi** : on tire une seule fois le nombre de départ du hasard, au gel, et on l'écrit dans le plan. Tous les tirages en découlent, donc tout le calcul se refait à l'identique. Et personne ne peut choisir un tirage favorable après coup, puisqu'il est tiré au moment du gel.
- **Appui** : DÉDUIT, `gel/manifeste.py --tirer-g0` (tirage unique, refusé une seconde fois, testé) et le contrôle strict de son écriture dans le plan (09/11). SOURCE, fixer et publier les graines avant l'analyse est une recommandation classique de reproductibilité des calculs.
- **Risque si on se trompe** : aucun d'identifié.
- **Confiance** : forte.

### 8 · Ratées groupées par tâche (5.11, point 4, l. 650)

- **Recommandation** : garder, « Décidé ».
- **Pourquoi** : c'est un test de résistance hors verdict. On fait comme si toutes les erreurs d'une tâche sur dix passaient inaperçues, ce qui ressemble à la réalité, où certaines tâches piègent le relecteur. Il est déjà codé, et il dit à quel point la règle tient si la vérification a des angles morts.
- **Appui** : DÉDUIT, code présent (`simulation/rejeu/analyse.py`, l. 363-364 ; `bout_en_bout.py`, l. 178). Plan 5.11 : c'est l'équivalent réel des « cas difficiles » de la simulation.
- **Risque si on se trompe** : aucun sur l'étiquette ; au pire, une ligne de plus dans les tableaux secondaires.
- **Confiance** : forte.

### 9 · Traces WorkBench désalignées (4.7, point 4, l. 405)

- **Recommandation** : modifier, en limite déclarée. Texte proposé : « **Décidé (limite)** : quand une trace WorkBench est désalignée, le résultat d'outil d'un appel vaut `None`. Le code figé traite alors l'appel sans résultat d'outil (test `banc/tests/test_verdicts.py::test_pilote_traces_desalignees_ne_donnent_pas_de_resultat`). Ces cas ne sont pas comptés à part : limite déclarée. »
- **Pourquoi** : le point était resté « à faire plus tard », sans statut. Le comportement du code est connu et testé ; seul le comptage manque. Ajouter un compteur maintenant demanderait du code neuf juste avant le gel, pour une information descriptive.
- **Appui** : DÉDUIT, le test cité ; `SUIVI.md`, l. 196.
- **Risque si on se trompe** : si ces cas étaient nombreux, on ne le saurait pas en lisant les sorties. Il faudrait les compter après coup, hors préenregistrement.
- **Confiance** : moyenne. L'alternative, ajouter le compteur avant le gel, est défendable si tu préfères que tout sorte du calcul figé.

### 12 · Épreuve de 3 variantes, « nombre à confirmer par la simulation » (REGLE l. 144)

- **Recommandation** : modifier le statut. Texte proposé : « 3 variantes (**Décidé** ; nombre fixé par conception, non confirmé par une simulation ; sans effet sur le verdict principal, plan Q3) ».
- **Pourquoi** : la simulation de départ a toujours utilisé 3, sans essayer d'autres nombres : la promesse « à confirmer par la simulation » n'a pas été tenue. Une épreuve ne suit qu'une erreur à enjeu moyen ou fort, et B-tout n'atteint pas l'autonomie à ces enjeux aux volumes prévus. Le nombre ne touche donc que les analyses secondaires. Mieux vaut le dire franchement que laisser une promesse ouverte.
- **Appui** : MESURÉ, `simulation/config.py`, `EPREUVE_VARIANTES = 3`, jamais varié dans E1. DÉDUIT, plan Q3 (« la question ne touche pas le verdict principal »).
- **Risque si on se trompe** : un autre nombre aurait peut-être donné d'autres résultats secondaires ; on ne le saura pas.
- **Confiance** : moyenne. Le nombre 3 lui-même est un choix de goût, sans bonne réponse démontrée.

### 13 · Consigne modifiée, réussites comptées pour moitié (REGLE l. 164)

- **Recommandation** : modifier. Texte proposé : « réussites de ce type comptées pour moitié (**Décidé comme règle de conception ; non mis à l'épreuve par cette expérience**, où les consignes des bancs ne changent pas) ».
- **Pourquoi** : dans l'expérience, les consignes des agents sont celles des bancs et ne changent jamais : cette ligne du tableau ne s'y applique pas. La garder comme « hypothèse, à tester » laisserait croire qu'on la teste. Elle reste utile pour le plugin et la suite.
- **Appui** : DÉDUIT, aucun code du rejeu ne traite une consigne modifiée ; les scénarios de 5.10 ne changent que le modèle.
- **Risque si on se trompe** : aucun sur le verdict ; la règle du « moitié » reste une hypothèse non testée, dite comme telle.
- **Confiance** : forte sur le constat. La garder ou la retirer du tableau est un choix de goût.

### 14 · Quatre classements « révisables par Otsoa » (REGLE l. 351)

- **Recommandation** : garder, « Décidé ».
- **Pourquoi** : trois des quatre classements vont dans le sens prudent. L'argent enregistré par le simulateur compte comme de l'argent, et une suppression définitive est une écriture durable : ces actions passent à un enjeu plus élevé. Ces classements ont servi au pilote. Les changer maintenant reviendrait à retoucher le typage des actions après avoir vu des données, ce que le préenregistrement cherche justement à éviter.
- **Appui** : DÉDUIT, `REGLE.md`, l. 351-355 ; `banc/TABLE_OUTILS.md`.
- **Risque si on se trompe** : le journal de vérification d'identité, rangé en message interne (enjeu plus bas), pourrait être sous-classé. L'effet est limité, puisque ce n'est pas une action d'argent ni une écriture durable.
- **Confiance** : moyenne.

### O9 · Deux phrases au plan (5.14)

- **Recommandation** : ajouter les deux, mot pour mot, comme dans `revues/2026-11-09_audit_gel_suites.md`.
  - Point 0 : couverture non calculable (aucune écriture) → R5 (`decision.py`, `point0`, l. 48 à 62).
  - Point 2 : différence de charge non calculable → témoin non battu sur la charge → R2 (`decision.py`, l. 295 à 303).
- **Pourquoi** : tu as décidé le 08/11 que le code figé fait le calcul confirmatoire (P8). Le texte doit donc dire ce que fait le code, y compris dans les cas limites. Ces deux phrases décrivent le comportement actuel du code, sans rien changer ; elles ferment deux angles morts entre le texte et le code.
- **Appui** : DÉDUIT, le code cité ; décision P8 du 08/11.
- **Risque si on se trompe** : aucun sur le verdict ; sans ces phrases, un lecteur trouverait un écart entre le texte et le code.
- **Confiance** : forte.

### O4 (a) · Niveau mesuré à B = 200, expérience à B = 2 000

- **Recommandation** : ajouter la limite, mot pour mot comme proposé.
- **Pourquoi** : le niveau publié de F3 (4,7 % en cumul) a été mesuré avec 200 tirages bootstrap par répétition, faute de temps de calcul ; l'expérience en fera 2 000. Avec plus de tirages, le seuil est estimé plus finement : on s'attend à un niveau proche, mais ce n'est pas mesuré. Il faut le dire, parce que le chiffre publié vient de l'autre réglage.
- **Appui** : MESURÉ, rapport du contrôle 3, 12.5 (réglages R0 = B = 200). DÉDUIT, plan 5.5, point 5 (B = 2 000).
- **Risque si on se trompe** : si le niveau réel à B = 2 000 s'écartait nettement, le chiffre publié serait trompeur ; la limite déclarée prévient le lecteur.
- **Confiance** : forte pour la déclarer. Mesurer à B = 2 000 avant le gel ne coûte rien en argent, seulement du calcul, mais retarderait le gel ; ce n'est pas nécessaire pour être honnête.

### O4 (b) · Famille de 1 ou 2 cellules testables

- **Recommandation** : ajouter la limite, et **ajouter la mention au code de sortie avant le gel** (option 2), avec un test.
- **Pourquoi** : la mention dit au lecteur que le niveau du max-T n'a pas été mesuré pour une si petite famille. Si elle n'est écrite que dans le rapport, on décide de l'écrire après avoir vu les résultats. Si elle sort du calcul figé, elle apparaît d'office dès que la famille compte 1 ou 2 cellules. C'est plus conforme à ta décision P8 (le code figé fait le calcul confirmatoire), pour quelques lignes de code et un test.
- **Appui** : DÉDUIT, `simulation/rejeu/sorties.py`, l. 411 publie déjà le nombre de cellules non testables ; il suffit d'y ajouter la mention quand la famille compte au plus 2 cellules testables. Décision P8 du 08/11.
- **Risque si on se trompe** : toucher au code juste avant le gel peut introduire une erreur ; un test ciblé et la relance des suites la rendent peu probable. Avec l'option 1, le risque est d'oublier la mention ou d'y être accusé de choix après coup.
- **Confiance** : moyenne. Les deux options sont honnêtes ; l'option 2 est plus robuste, l'option 1 plus rapide.

## Ce qui reste vraiment incertain

- **Le nombre 3 des épreuves (12)** et **la moitié en cas de consigne modifiée (13)** sont des choix de conception sans preuve. L'expérience ne les met pas à l'épreuve. Les déclarer comme tels est la seule réponse honnête.
- **Le niveau réel du max-T à B = 2 000 (O4 a)**, et pour une famille de 1 ou 2 cellules (O4 b), n'est pas mesuré.
- **Le classement du journal de vérification d'identité (14)** est le seul point où la prudence pourrait jouer dans l'autre sens.
- **L'antériorité du 05/11** ne se refait pas octet pour octet : son zip déposé (`77c7a11e…`) n'est pas reproductible, seul le manifeste l'est. C'est noté dans sa fiche.

Sources extérieures :
- OSF Preregistration, champs du formulaire, d'après des copies : [modèle LaTeX](https://www.overleaf.com/latex/templates/osf-preregistration-template/ycwdkjhjpgfy) ; [preregr, OSF Prereg form v1](https://cran.r-universe.dev/preregr/doc/form_OSFprereg_v1.html) ; [VU Amsterdam, pre-registration](https://rdm.vu.nl/topics/pre-registration.html).
- SWE-bench Verified (OpenAI, août 2024) : retrait des tâches mal posées après relecture humaine (connaissance générale, non revérifiée en ligne ce jour).
