# Vérifications dans le moteur (coordinateur, 07/11/2026)

Ces vérifications ont été faites par le coordinateur de la recherche, en rejouant des répétitions du contrôle 3 avec leurs
graines (moteur au commit e300b0e, `simulation/`, aucun appel payant). Elles **priment sur les déductions des quatre notes
de recherche** quand elles les contredisent. Scripts : `scratchpad/v24/boot_v24.py`, `nan_A.py`, `a1_une_tache.py` (hors
dépôt) ; diagnostic versionné : `simulation/controle3/une_tache/`.

## 1. Le faux R1 du monde V vient de répliques NaN, pas d'un écart type nul

Monde V (un dixième des tâches), répétition 24. Les 11 cellules jugées de B-tout sont dans l'aviation à enjeu faible, avec
une tâche porteuse dans un cadre de 2 tâches.
- 42 répliques bootstrap sur 200 valent NaN : ce sont celles qui ne tirent pas la tâche porteuse. Le rapport est alors
  0/0 : aucune écriture au dénominateur.
- Les 158 répliques finies **varient** (par exemple de 0,58 à 0,96 dans une cellule), sous l'effet des ordres et des
  tirages du validateur.
- L'écart type (`numpy.std`, ddof = 1) vaut donc **NaN**. Dans `maxt.depassement_etabli`, `var = sd > 0` est faux pour
  NaN : la cellule part dans la branche « hors maximum, établi si l'estimation dépasse le budget ».
- Le plan (5.14, point 1) ne parle que d'un écart type **nul** (« aucune variation entre répétitions »). Le cas NaN, soit
  un écart type non défini, n'y est pas écrit : le moteur le range en silence avec le cas nul.

## 2. Aux volumes du plan, une cellule à une seule tâche ne peut pas établir de dépassement par le max-T

Monde A, répétition 1. 11 cellules jugées à une tâche porteuse, aviation, enjeu faible, cadre de 20 tâches, 20 à 60
écritures.

| Grandeur | Valeur |
|---|---|
| Répliques à 0 (celles qui ne tirent pas la tâche ; (19/20)^20 ≈ 36 % attendus) | 75 sur 200 environ |
| Répliques NaN | aucune |
| Estimation | 0,03 à 0,14 fois le budget |
| Écart type bootstrap | 0,13 à 0,19 fois le budget, soit 1,2 à 1,5 fois l'estimation |
| c* | 3,43 |
| Borne basse (estimation − c* × écart type) | de −0,33 à −0,60 fois le budget |

- Toutes ces cellules sont « non réfutées ».
- **Déduit** : l'écart type est proportionnel à l'estimation, parce que le nombre de copies de la tâche varie d'une réplique
  à l'autre. La borne basse vaut donc à peu près estimation × (1 − c* × 1,3) : elle reste négative quelle que soit la taille
  de l'estimation, tant que c* dépasse 0,8 environ. **Une seule tâche ne peut pas établir un dépassement par le max-T aux
  volumes du plan.**
- Les calculs des notes qui supposent qu'« une erreur suffit » (9,5 à 26 % de faux R1 au budget) ne valent que pour la
  branche dégénérée (section 1), pas pour le max-T.

Monde A, répétitions 0 à 3 : 35 à 46 cellules jugées par répétition, **aucune** avec une réplique NaN. Dans la répétition
3, les 11 cellules à une tâche ont un écart type nul avec une estimation nulle (aucune erreur) : la branche dégénérée est
prise, mais sans effet (0 n'est pas au-dessus du budget).

Contrôle 3 complet (799 répétitions) : la branche dégénérée n'a établi un dépassement que dans la répétition 24 de V.
Ailleurs, aucun dépassement n'est établi sur une cellule dont la borne égale l'estimation.

## 3. Autres faits vérifiés

- **« Démontrée »** (`decision.demontree`) n'utilise pas le bootstrap. C'est une borne haute de Clopper-Pearson sur la
  taille effective à ρ = 1. Une cellule à une tâche (n_eff = 1) n'est donc jamais « démontrée ». Le risque d'un intervalle
  [0 ; 0] qui ferait passer pour démontrée une cellule sans erreur n'existe pas.
- **`pipeline.taches_porteuses`** compte les tâches qui ont au moins une écriture du niveau au dénominateur. Il ne dépend
  que de la composition des parties (types et dénominateur), pas des erreurs : un filtre sur ce nombre est indépendant de
  la statistique de test sous l'hypothèse nulle.
- **Quand la branche dégénérée peut-elle établir à tort ?** Il faut une estimation au-dessus du budget et un écart type nul
  ou NaN.
  - NaN : une réplique au moins n'a aucune écriture au dénominateur. C'est le cas d'un très petit cadre, comme V.
  - Écart type nul : toutes les répliques sont égales et positives. C'est le cas d'un cadre réduit à une tâche (G = 1), ou
    de tâches aux rapports identiques.
  - Un cadre à une seule tâche dont les ordres font un peu varier les répliques entrerait au contraire dans le maximum avec
    un écart type minuscule, et une borne presque égale à l'estimation (déduit ; jamais observé dans les simulations).
- **Exposition** (diagnostic `une_tache/`, 36 répétitions) : des cellules à une tâche apparaissent dans 6 répétitions sur
  12 de A et 3 sur 12 de E, mais aux volumes du plan elles passent par le max-T ou ont une estimation nulle (section 2).

## 4. Tâches porteuses des cellules mesurées, et cellules de 2 à 4 tâches (ajout après la synthèse)

- Dans la seconde mesure du monde au seuil (`b_seuil/seconde_mesure.jsonl`), les cellules de configuration du commerce
  à enjeu faible comptent **24 à 38 tâches porteuses**, 31 à 33 le plus souvent. Le chiffre de 5 à 11, donné dans le
  cadrage de cette recherche, venait du point 4 (types du commerce à établir à ρ = 1). C'est une autre grandeur : ce
  chiffre ne vaut pas pour les cellules du point 1.
- Diagnostic `une_tache/` (A, E, D-piège, 36 répétitions) : 7 répétitions (A 3, E 4) ont des cellules jugées à 2 à 4
  tâches porteuses.
  - Aviation, enjeu faible : 60 cellules à 2 tâches et 15 à 3.
  - Aviation, enjeu moyen : 4 cellules à 4 tâches.
  - Commerce, enjeu faible : 14 cellules à 4 tâches.
  - Aucune n'établit de dépassement, mais les agents y sont à 0,2 fois la barre : le niveau du test n'y est pas mesuré.
