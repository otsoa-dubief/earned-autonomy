# Simulation de niveau 1 · deuxième passe, règle amendée (A1), 4 novembre 2026

> Agents fictifs de fiabilité connue, aucun agent réel, aucune donnée réelle, aucun modèle d'IA, aucun appel réseau. Plan : `PLAN_SIMULATION.md`, avec son amendement A1 (fait foi). Règle : `../REGLE.md`, section « Amendements », A1. Première passe : `../resultats_v1/` (archivée, non modifiée). Code : `config.py`, `flux.py`, `regle.py`, `temoins.py`, `mesures.py`, `executer.py`, `rapport.py`, `ecrire_resultats.py` ; tests : `tests/`. Version de la règle : v2. Graine maîtresse 20261104. Durée de la grille : 169 s. Ce n'est pas l'expérience de confirmation.

## Résumé

1. **Tests** : 43 passés, 0 en échec, dont les cinq ajoutés pour l'amendement (35 ; 54 ; ⌈a/b⌉ ; 2 erreurs ; pas d'extinction à 2 %). Le chemin v1 du code reproduit `resultats_v1/` au chiffre près.
2. **Extinction** : disparue. A2 en bureau finit à 70,6 % [70,4 ; 70,8] d'actions sans validation préalable (v1 : 4,1 % [4,0 ; 4,3]).
3. **Garantie** : agents mauvais stables, passe à stricte α=5 %, stricte α=20 %, départ α=5 %, souple α=5 % (pire couple au départ α = 5 % : A3 SOR, 2,9 % [2,5 ; 3,4]) ; échoue en dérive ou autour d'un changement à stricte α=5 %, stricte α=20 %, départ α=5 %, départ α=20 %, et avec le doute calibré à souple α=5 %, souple α=20 %.
4. **Charge** (A1 et A2, en tout et hors lectures, ≤ 50) : passe à aucun réglage. Au départ α = 5 %, A2 hors lectures : 58,2 [58,0 ; 58,3] en bureau, 85,5 [85,3 ; 85,7] en service client.
5. **Dégâts** (départ α = 5 %, A1 et A2) : plus petite marge de la grille qui passe, enjeu faible aucune (> 1), moyen 0,1, fort 0,1 pour 100 actions. À lire contre la marge fixée par Otsoa.
6. **Liste fixe et tri par le risque** : compromis 312 sur 312 comparaisons (6 réglages × 2 témoins × 26 couples).
7. **Réactivité** (A6b, départ α = 5 %) : 95e centile 997 actions en bureau, 1 500 en service client, tous types promus ; sur les types devenus mauvais, 381 et 1 353.
8. **Ce qui surprend** : la dérive silencieuse est retirée plus lentement qu'en v1 ; au pm exact, la garantie à enjeu faible s'effrite ; le palier 2 se mérite pour un agent à 15 % sur les types à enjeu faible.
9. **Ce qui ne change pas** : le hasard fait aussi bien que la règle pour un agent stable ; le palier 2 ne coûte aucun dégât ; α compte peu ; au réglage strict, l'argent en bureau reste presque hors d'atteinte.
10. **Les trois épreuves ensemble** : la charge hors lectures d'A2 dépasse 50 à tous les réglages ; aucun réglage ne passe donc l'épreuve d'utilité, quelle que soit la marge de dégâts retenue. Garantie (tous couples) et charge ensemble : aucun réglage.

## Comment lire les chiffres

- **Dénominateurs** : une répétition = un agent sur 3 000 actions. 5 000 répétitions pour le réglage de départ α = 5 % et pour tous les témoins ; 1 000 pour les autres réglages et les ablations. Charge et dégâts : pour 100 actions du flux. Proportions : sur les répétitions.
- **Intervalles à 95 %** entre crochets, toujours. Moyennes : approximation normale ; proportions : Wilson ; écarts : appariés (mêmes tirages pour toutes les règles, et pour les deux versions).
- **Validateur à 5 %** partout, sauf dans la section qui fait varier e.
- Ce fichier est écrit par `ecrire_resultats.py` à partir des CSV, sans recopie à la main.

## Contrôles du code (tests de la section 8, adaptés au score réfléchi)

Lancés avant toute production de résultats : `.venv/bin/python -m pytest tests/` → **43 tests passés, 0 en échec** (`executer.py --verifier-tests` refuse de produire des résultats sinon). Le contrôle de cohérence moteur contre version de référence tourne sur les deux versions ; le chemin v1 du code reproduit `resultats_v1/` au chiffre près (vérifié sur A2, A6a et A7, deux mélanges).

| contrôle | attendu | obtenu |
|--|--|--|
| réussites pour monter depuis L = 0 (pb 2 %, pm 10 %, α = β = 5 %) | 35 | 35 (type DUR, réglage de départ) |
| réussites pour remonter après une erreur à enjeu moyen ou fort (L = a) | 54 | 54, que l'erreur arrive depuis L = 0 ou depuis le plancher |
| réussites pour absorber une erreur au plancher : ⌈a/b⌉ | ⌈a/b⌉ pour 6 jeux (pb ; pm) | égal dans les 6 cas ; LEC : 9 au palier 3, 5 au palier 2 |
| erreurs à enjeu faible rapprochées qui font descendre depuis le plancher | 2, d'un seul palier | 2 (LEC : 3 → 2 ; MSG : 3 → 1) ; séparées par ⌈a/b⌉ réussites, 20 erreurs ne font pas descendre |
| agent stable à 2 % : part d'actions sans validation préalable, fin (2 500-2 999) contre milieu (1 250-1 749) | écart relatif ≤ 10 % (critère fixé avant la passe) | v2 : 70,8 % contre 71,3 % ; la v1 donnait 4,8 % contre 13,9 % (le test les sépare) |
| risque réel de rejeter à tort, p = 2 %, test sans borne | 2,97 % | exact 2,97 % ; Monte-Carlo 2,94 % [2,89 ; 2,99], n = 400 000 |
| risque réel d'accepter à tort, p = 10 % | 4,89 % | exact 4,89 % ; Monte-Carlo 4,84 % [4,77 ; 4,90], n = 400 000 |
| taille moyenne d'échantillon (p = 2 % ; 10 %) | 54,6 ; 38,3 | 54,58 ; 38,30 |
| enchaîner 20 réussites à 5 % d'erreur | 0,95^20 = 0,358 | 0,360 [0,353 ; 0,367], n = 20 000 |
| erreur à enjeu moyen ou fort | palier 1, L = max(L, 0) + a, épreuve | vérifié (référence et moteur, 4 types) ; le score ne bouge pas tant que l'épreuve est ouverte |
| actions plafonnées | jamais autonomes | vérifié pour la règle, ses 5 variantes et tous les témoins sauf « tout approuver » |
| doute | ne change ni le score ni s | vérifié (un agent qui doute de tout reste à L = 0 ; doute abusif : L rejoué à la main sur les seules actions jugées) |
| remises à zéro (A1) | consigne : L/2 si L < 0 ; changement de modèle : L = 0, erreurs moyennes ou fortes en épreuves, erreurs faibles effacées | vérifié (référence ; moteur sur A6a et A8) |
| cohérence | moteur vectorisé = version de référence | identique action par action, v2 et v1, 9 agents × 8 à 10 variantes × 4 répétitions |

Les nombres tombent juste. Avec le score réfléchi, plus rien n'est sur le fil : après 54 réussites, le score est nettement sous ln B (la v1 l'y ramenait exactement). Une erreur au plancher ramène toujours le score exactement à ln B, d'où la lecture « au plus ln B », gardée (choix 1).

Une incohérence de texte, sans effet sur le code : REGLE.md, A1, écrit qu'une erreur « est absorbée par environ a/b réussites nouvelles », soit 8 à enjeu faible, 19 à enjeu moyen et 39 à enjeu fort. C'est exact pour une erreur à enjeu faible (L + a). Pour une erreur à enjeu moyen ou fort, l'opération écrite juste au-dessus, L = max(L, 0) + a, efface le crédit : il faut 54 réussites (moyen) et 111 (fort) pour revenir au palier 3, après l'épreuve. La simulation suit l'opération écrite ; le test d'absorption porte donc sur les erreurs à enjeu faible.

## Ce que la règle amendée exige, calcul exact

Calculé à partir des réglages, sans simulation. Score réfléchi par palier visé : une réussite retire b, le score ne descend pas sous ln B − a ; une erreur à enjeu faible ajoute a ; une erreur à enjeu moyen ou fort remet le score à max(L, 0) + a.

| réglage | ln B | enjeu | palier 3 : réussites depuis L = 0 | palier 2 : réussites depuis L = 0 | palier 3 : réussites après une erreur à enjeu moyen ou fort | erreur à enjeu faible au plancher : réussites pour l'absorber (palier 3 ; palier 2) |
|--|--|--|--|--|--|--|
| stricte α=5 % | −2,944 | faible | 37 | 27 | sans objet | 18 ; 10 |
| stricte α=5 % | −2,944 | moyen | 72 | 37 | 111 | sans objet (le crédit est effacé) |
| stricte α=5 % | −2,944 | fort | 146 | sans objet | 225 | sans objet (le crédit est effacé) |
| stricte α=20 % | −2,773 | faible | 35 | 25 | sans objet | 18 ; 10 |
| stricte α=20 % | −2,773 | moyen | 68 | 35 | 107 | sans objet (le crédit est effacé) |
| stricte α=20 % | −2,773 | fort | 137 | sans objet | 216 | sans objet (le crédit est effacé) |
| départ α=5 % | −2,944 | faible | 18 | 12 | sans objet | 9 ; 5 |
| départ α=5 % | −2,944 | moyen | 35 | 18 | 54 | sans objet (le crédit est effacé) |
| départ α=5 % | −2,944 | fort | 72 | sans objet | 111 | sans objet (le crédit est effacé) |
| départ α=20 % | −2,773 | faible | 17 | 12 | sans objet | 9 ; 5 |
| départ α=20 % | −2,773 | moyen | 33 | 17 | 52 | sans objet (le crédit est effacé) |
| départ α=20 % | −2,773 | fort | 68 | sans objet | 107 | sans objet (le crédit est effacé) |
| souple α=5 % | −2,944 | faible | 11 | 7 | sans objet | 5 ; 3 |
| souple α=5 % | −2,944 | moyen | 23 | 11 | 35 | sans objet (le crédit est effacé) |
| souple α=5 % | −2,944 | fort | 47 | sans objet | 73 | sans objet (le crédit est effacé) |
| souple α=20 % | −2,773 | faible | 10 | 7 | sans objet | 5 ; 3 |
| souple α=20 % | −2,773 | moyen | 21 | 10 | 34 | sans objet (le crédit est effacé) |
| souple α=20 % | −2,773 | fort | 45 | sans objet | 70 | sans objet (le crédit est effacé) |

Actions vérifiables par type sur l'horizon (3 000 actions × part du type × 95 %, en moyenne) :

| mélange | LEC | ECR | DUR | EXE | MSG | SOR | ARG |
|--|--|--|--|--|--|--|--|
| bureau | 1 282 | 428 | 228 | 228 | 171 | 274 | 114 |
| service client | 1 140 | 142 | 570 | 57 | 86 | 342 | 319 |

Il n'y a plus de budget d'erreurs : une erreur à enjeu faible isolée est absorbée en quelques réussites, et le palier 3 n'est jamais fermé pour toute la configuration. Ce qui ne change pas : au réglage strict, ARG en « bureau » demande 146 réussites vérifiées d'affilée (α = 5 %) pour 114 actions vérifiables en moyenne sur l'horizon.

## Verdict de la pièce 1, réglage par réglage (validateur à 5 %)

Trois verdicts possibles pour chaque critère : **passe** (tout l'intervalle à 95 % est du bon côté du seuil), **échoue** (tout l'intervalle est du mauvais côté), **indécis** (l'intervalle chevauche le seuil). Réglage de départ α = 5 % : 5 000 répétitions ; les cinq autres réglages : 1 000 répétitions (les 1 000 premières des mêmes tirages). Les dégâts sont lus sur la grille de marges de l'amendement A1 : 0 ; 0,005 ; 0,01 ; 0,02 ; 0,05 ; 0,1 ; 0,2 ; 0,5 ; 1 pour 100 actions.

### Synthèse

| réglage | 1. garantie : agents stables | 1. garantie : doute (A4) | 1. garantie : dérive et changements | 2. charge ≤ 50, en tout et hors lectures (A1 et A2) | 2. plus petite marge de dégâts qui passe, A1 et A2 (faible / moyen / fort) | 2. bat la liste fixe | 2. bat le tri par le risque | 3. réactivité A6b, 95e centile : tous les types promus ; types devenus mauvais (bureau / service client) |
|--|--|--|--|--|--|--|--|--|
| stricte α=5 % | passe | passe | échoue | échoue | aucune (> 1) / 0,05 / 0,05 | non (compromis) | non (compromis) | 670 ; 670 / 1 456 ; 1 456 |
| stricte α=20 % | passe | passe | échoue | échoue | aucune (> 1) / 0,1 / 0,05 | non (compromis) | non (compromis) | 672 ; 672 / 1 492 ; 1 492 |
| départ α=5 % | passe | passe | échoue | échoue | aucune (> 1) / 0,1 / 0,1 | non (compromis) | non (compromis) | 997 ; 381 / 1 500 ; 1 353 |
| départ α=20 % | indécis | passe | échoue | échoue | aucune (> 1) / 0,1 / 0,1 | non (compromis) | non (compromis) | 994 ; 368 / 1 500 ; 1 305 |
| souple α=5 % | passe | échoue | indécis | échoue | aucune (> 1) / 0,2 / 0,1 | non (compromis) | non (compromis) | 1 458 ; 688 / 1 500 ; 263 |
| souple α=20 % | indécis | échoue | passe | échoue | aucune (> 1) / 0,2 / 0,1 | non (compromis) | non (compromis) | 1 452 ; 682 / 1 500 ; 276 |

Lecture, critère par critère. Garantie pour les agents mauvais stables : passe à stricte α=5 %, stricte α=20 %, départ α=5 %, souple α=5 % ; indécise à départ α=20 %, souple α=20 % ; échoue à aucun réglage. Avec le doute calibré d'A4 : échoue à souple α=5 %, souple α=20 %. En dérive ou autour d'un changement : échoue à stricte α=5 %, stricte α=20 %, départ α=5 %, départ α=20 %. Charge (A1 et A2, les deux mélanges, en tout et hors lectures) : passe à aucun réglage ; échoue à stricte α=5 %, stricte α=20 %, départ α=5 %, départ α=20 %, souple α=5 %, souple α=20 %. La marge de dégâts se lit dans la colonne correspondante, à comparer à la marge fixée par Otsoa. La réactivité ne se juge qu'une fois K fixé ; la colonne donne le K qu'il faudrait pour la tenir 95 fois sur 100.

### 1. Garantie

Agent « mauvais » sur un type : son vrai taux d'erreur est au moins le pm du palier 3 de ce niveau d'enjeu, au réglage considéré (choix 17). Mesure : part des répétitions où ce type atteint le palier 3 avant l'horizon. Le verdict porte sur le **pire couple** (agent, type) ; la part groupée est donnée aussi. Avec plusieurs dizaines de couples, le pire couple est un peu biaisé vers le haut.

| réglage | couples mauvais (stables / doute / non stables) | part groupée, tous couples | pire couple, agents stables (A3, A4, A5) | pire couple, doute (A4 calibré ou abusif) | pire couple, phases non stables (A6a après, A6b après, A7 avant) |
|--|--|--|--|--|--|
| stricte α=5 % | 24 / 28 / 42 | 3,50 % [3,39 ; 3,62] | A3 sur DUR (bureau) : 2,6 % [1,8 ; 3,8], n = 1 000 → **passe** | A4-calibre sur MSG (bureau) : 3,0 % [2,1 ; 4,3], n = 1 000 → **passe** | A6b sur ECR (bureau, après t = 1 500) : 46,3 % [43,2 ; 49,4], n = 1 000 → **échoue** |
| stricte α=20 % | 24 / 28 / 42 | 3,70 % [3,59 ; 3,83] | A3 sur EXE (bureau) : 3,2 % [2,3 ; 4,5], n = 1 000 → **passe** | A4-calibre sur ECR (bureau) : 3,6 % [2,6 ; 4,9], n = 1 000 → **passe** | A6b sur ECR (bureau, après t = 1 500) : 46,3 % [43,2 ; 49,4], n = 1 000 → **échoue** |
| départ α=5 % | 14 / 16 / 24 | 1,35 % [1,31 ; 1,40] | A3 sur SOR (service client) : 2,9 % [2,5 ; 3,4], n = 5 000 → **passe** | A4-calibre sur EXE (bureau) : 1,7 % [1,4 ; 2,1], n = 5 000 → **passe** | A6b sur EXE (service client, après t = 1 500) : 23,3 % [22,1 ; 24,5], n = 5 000 → **échoue** |
| départ α=20 % | 14 / 16 / 24 | 1,49 % [1,40 ; 1,60] | A3 sur SOR (service client) : 3,9 % [2,9 ; 5,3], n = 1 000 → **indécis** | A4-calibre sur DUR (service client) : 2,5 % [1,7 ; 3,7], n = 1 000 → **passe** | A6b sur EXE (service client, après t = 1 500) : 23,0 % [20,5 ; 25,7], n = 1 000 → **échoue** |
| souple α=5 % | 10 / 16 / 12 | 1,63 % [1,50 ; 1,76] | A4 sur EXE (bureau) : 2,8 % [1,9 ; 4,0], n = 1 000 → **passe** | A4-calibre sur DUR (service client) : 6,8 % [5,4 ; 8,5], n = 1 000 → **échoue** | A6b sur ARG (bureau, après t = 1 500) : 4,1 % [3,0 ; 5,5], n = 1 000 → **indécis** |
| souple α=20 % | 10 / 16 / 12 | 2,02 % [1,88 ; 2,17] | A4 sur EXE (bureau) : 4,2 % [3,1 ; 5,6], n = 1 000 → **indécis** | A4-calibre sur EXE (bureau) : 9,5 % [7,8 ; 11,5], n = 1 000 → **échoue** | A6b sur ARG (service client, après t = 1 500) : 3,6 % [2,6 ; 4,9], n = 1 000 → **passe** |

Agents à taux constant exactement au pm, types à enjeu faible (courbe de garantie, 36 points de 1 000 répétitions) : promus au palier 3 avant l'horizon dans 5,11 % [4,89 ; 5,35] des cas en moyenne ; au pire 7,3 % [5,8 ; 9,1] (LEC, service client, stricte α=20 %). La courbe complète est dans `fig2_garantie_*.png` et `garantie_courbe.csv`.

### 2. Utilité

**Charge** pour 100 actions (validations, corrections, doutes et variantes d'épreuve), en tout et hors lectures. « Tout faire valider » vaut 100 dans les deux cas. Seuil : 50.

| réglage | A1 bureau : tout ; hors lectures | A1 service client | A2 bureau | A2 service client |
|--|--|--|--|--|
| stricte α=5 % (n = 1 000) | 28,2 [28,0 ; 28,4] passe ; 49,5 [49,1 ; 49,9] passe | 41,3 [41,0 ; 41,7] passe ; 67,2 [66,6 ; 67,8] échoue | 39,6 [39,4 ; 39,8] passe ; 68,5 [68,2 ; 68,8] échoue | 59,0 [58,8 ; 59,1] échoue ; 95,2 [95,0 ; 95,5] échoue |
| stricte α=20 % (n = 1 000) | 27,6 [27,4 ; 27,8] passe ; 48,4 [48,0 ; 48,8] passe | 40,4 [40,0 ; 40,8] passe ; 65,7 [65,1 ; 66,4] échoue | 39,1 [38,9 ; 39,3] passe ; 67,9 [67,5 ; 68,2] échoue | 58,5 [58,4 ; 58,7] échoue ; 94,7 [94,4 ; 94,9] échoue |
| départ α=5 % (n = 5 000) | 19,6 [19,5 ; 19,7] passe ; 34,9 [34,7 ; 35,1] passe | 28,9 [28,8 ; 29,1] passe ; 47,5 [47,2 ; 47,7] passe | 32,6 [32,5 ; 32,7] passe ; 58,2 [58,0 ; 58,3] échoue | 51,9 [51,8 ; 52,0] échoue ; 85,5 [85,3 ; 85,7] échoue |
| départ α=20 % (n = 1 000) | 19,2 [19,0 ; 19,4] passe ; 34,1 [33,7 ; 34,5] passe | 28,1 [27,8 ; 28,4] passe ; 46,1 [45,5 ; 46,6] passe | 32,3 [32,1 ; 32,5] passe ; 57,7 [57,3 ; 58,0] échoue | 51,4 [51,1 ; 51,6] échoue ; 84,7 [84,3 ; 85,1] échoue |
| souple α=5 % (n = 1 000) | 15,5 [15,3 ; 15,7] passe ; 27,7 [27,3 ; 28,0] passe | 22,8 [22,5 ; 23,1] passe ; 37,6 [37,1 ; 38,0] passe | 29,1 [28,8 ; 29,3] passe ; 52,3 [51,9 ; 52,7] échoue | 47,2 [46,9 ; 47,5] passe ; 78,2 [77,7 ; 78,7] échoue |
| souple α=20 % (n = 1 000) | 15,0 [14,9 ; 15,2] passe ; 26,9 [26,6 ; 27,2] passe | 22,3 [22,0 ; 22,5] passe ; 36,7 [36,2 ; 37,1] passe | 28,7 [28,5 ; 29,0] passe ; 51,7 [51,3 ; 52,1] échoue | 46,7 [46,4 ; 47,0] passe ; 77,3 [76,8 ; 77,8] échoue |

Pour comparer, en bureau : liste fixe 40,0 [40,0 ; 40,0] en tout et 72,7 [72,7 ; 72,8] hors lectures ; tri par le risque 34,0 [34,0 ; 34,0] et 61,8 [61,8 ; 61,8].

**Dégâts**, écart apparié avec « tout faire valider », pour 100 actions du flux, niveau par niveau. « Plus petite marge » : la plus petite valeur de la grille telle que l'intervalle à 95 % de l'écart soit tout entier sous la marge, pour tous les couples (agent, mélange) considérés. Détail par agent : `marge_minimale.csv` ; verdict à chaque marge : `marges.csv`.

| réglage | niveau | A1 et A2 : plus petite marge qui passe | plus grand écart chez A1 et A2 | 13 agents : plus petite marge qui passe | plus grand écart, 13 agents |
|--|--|--|--|--|--|
| stricte α=5 % (n = 1 000) | faible | aucune (> 1) | A2 (bureau) : 1,037 [1,027 ; 1,047] | aucune (> 1) | A2 (bureau) : 1,037 [1,027 ; 1,047] |
| stricte α=5 % (n = 1 000) | moyen | 0,05 | A1 (service client) : 0,047 [0,046 ; 0,049] | 0,2 | A4-calibre (service client) : 0,119 [0,115 ; 0,123] |
| stricte α=5 % (n = 1 000) | fort | 0,05 | A1 (service client) : 0,023 [0,021 ; 0,024] | 0,2 | A4-calibre (service client) : 0,126 [0,122 ; 0,130] |
| stricte α=20 % (n = 1 000) | faible | aucune (> 1) | A2 (bureau) : 1,043 [1,033 ; 1,054] | aucune (> 1) | A2 (bureau) : 1,043 [1,033 ; 1,054] |
| stricte α=20 % (n = 1 000) | moyen | 0,1 | A1 (service client) : 0,049 [0,047 ; 0,050] | 0,2 | A4-calibre (service client) : 0,119 [0,115 ; 0,123] |
| stricte α=20 % (n = 1 000) | fort | 0,05 | A1 (service client) : 0,025 [0,024 ; 0,027] | 0,2 | A4-calibre (service client) : 0,126 [0,122 ; 0,130] |
| départ α=5 % (n = 5 000) | faible | aucune (> 1) | A2 (bureau) : 1,185 [1,180 ; 1,190] | aucune (> 1) | A3 (bureau) : 2,542 [2,536 ; 2,549] |
| départ α=5 % (n = 5 000) | moyen | 0,1 | A2 (service client) : 0,077 [0,075 ; 0,078] | 0,2 | A4-calibre (service client) : 0,123 [0,122 ; 0,125] |
| départ α=5 % (n = 5 000) | fort | 0,1 | A1 (service client) : 0,050 [0,049 ; 0,050] | 0,2 | A4-calibre (service client) : 0,130 [0,128 ; 0,131] |
| départ α=20 % (n = 1 000) | faible | aucune (> 1) | A2 (bureau) : 1,188 [1,176 ; 1,200] | aucune (> 1) | A3 (bureau) : 2,551 [2,536 ; 2,567] |
| départ α=20 % (n = 1 000) | moyen | 0,1 | A2 (service client) : 0,082 [0,079 ; 0,084] | 0,2 | A4-calibre (service client) : 0,120 [0,116 ; 0,123] |
| départ α=20 % (n = 1 000) | fort | 0,1 | A1 (service client) : 0,051 [0,049 ; 0,053] | 0,2 | A4-calibre (service client) : 0,127 [0,123 ; 0,131] |
| souple α=5 % (n = 1 000) | faible | aucune (> 1) | A2 (bureau) : 1,221 [1,208 ; 1,234] | aucune (> 1) | A4-calibre (bureau) : 4,263 [4,237 ; 4,288] |
| souple α=5 % (n = 1 000) | moyen | 0,2 | A2 (service client) : 0,119 [0,116 ; 0,122] | 0,2 | A2-calibre (service client) : 0,125 [0,122 ; 0,129] |
| souple α=5 % (n = 1 000) | fort | 0,1 | A1 (service client) : 0,065 [0,062 ; 0,067] | 0,2 | A4-calibre (service client) : 0,128 [0,124 ; 0,132] |
| souple α=20 % (n = 1 000) | faible | aucune (> 1) | A2 (bureau) : 1,223 [1,211 ; 1,236] | aucune (> 1) | A4-calibre (bureau) : 4,285 [4,260 ; 4,311] |
| souple α=20 % (n = 1 000) | moyen | 0,2 | A2 (service client) : 0,124 [0,120 ; 0,127] | 0,2 | A2-calibre (service client) : 0,131 [0,127 ; 0,134] |
| souple α=20 % (n = 1 000) | fort | 0,1 | A2 (service client) : 0,067 [0,064 ; 0,069] | 0,2 | A4-calibre (service client) : 0,124 [0,120 ; 0,128] |

Verdict à chaque marge de la grille, réglage de départ α = 5 % (5 000 répétitions), A1 et A2 dans les deux mélanges :

| marge (pour 100 actions) | enjeu faible | enjeu moyen | enjeu fort |
|--|--|--|--|
| 0 | échoue | échoue | échoue |
| 0,005 | échoue | échoue | échoue |
| 0,01 | échoue | échoue | échoue |
| 0,02 | échoue | échoue | échoue |
| 0,05 | échoue | échoue | indécis |
| 0,1 | échoue | passe | passe |
| 0,2 | échoue | passe | passe |
| 0,5 | échoue | passe | passe |
| 1 | échoue | passe | passe |

**Bat-elle les concurrents simples ?** Critère (choix 19) : sur les mêmes tirages, meilleure sur au moins une mesure parmi la charge et les dégâts des trois niveaux (intervalle de l'écart tout sous 0), pire sur aucune (aucun intervalle tout au-dessus de 0). Comptes sur les 26 couples agent × mélange.

| réglage | contre la liste fixe | contre le tri par le risque | contre le hasard |
|--|--|--|--|
| stricte α=5 % | compromis 26 | compromis 26 | compromis 6, perd 20 |
| stricte α=20 % | compromis 26 | compromis 26 | compromis 6, perd 20 |
| départ α=5 % | compromis 26 | compromis 26 | compromis 6, perd 20 |
| départ α=20 % | compromis 26 | compromis 26 | compromis 6, perd 20 |
| souple α=5 % | compromis 26 | compromis 26 | compromis 6, perd 20 |
| souple α=20 % | compromis 26 | compromis 26 | compromis 6, perd 20 |

« Compromis » : la règle est meilleure sur une mesure et pire sur une autre. Détail dans la section suivante et dans `comparaisons.csv`.

### 3. Réactivité

Couples (répétition, type) au palier 2 ou 3 à t = 1 500, au moment où le taux passe de 2 % à 10 %. Délai : actions de l'agent (tous types) jusqu'au retour au palier 1 ; un type non revenu à l'horizon compte pour 1 500 et figure dans « non retiré ». « Types devenus mauvais » : ceux où 10 % atteint le pm du palier 3 du réglage, que la règle doit retirer ; sur les autres types, 10 % reste sous pm et la règle n'a pas à retirer l'autonomie. Dégâts : erreurs parties sur ce type pendant le délai, par couple promu. Intervalles des centiles par rééchantillonnage (400 tirages).

| réglage | agent | mélange | types | couples promus à t = 1 500 | délai médian | 95e centile | non retiré avant l'horizon | dégâts pendant le délai, par couple |
|--|--|--|--|--|--|--|--|--|
| stricte α=5 % | A6b | bureau | tous les promus | 3 086 | 129 [123 ; 135] | 670 [630 ; 706] | 0,2 % [0,1 ; 0,4] | 1,940 [1,884 ; 1,997] |
| stricte α=5 % | A6b | bureau | devenus mauvais (LEC ECR DUR EXE MSG SOR ARG) | 3 086 | 129 [123 ; 135] | 670 [630 ; 706] | 0,2 % [0,1 ; 0,4] | 1,940 [1,884 ; 1,997] |
| stricte α=5 % | A6b | service client | tous les promus | 2 455 | 164 [154 ; 176] | 1 456 [1 371 ; 1 500] | 4,8 % [4,1 ; 5,8] | 1,867 [1,806 ; 1,928] |
| stricte α=5 % | A6b | service client | devenus mauvais (LEC ECR DUR EXE MSG SOR ARG) | 2 455 | 164 [154 ; 176] | 1 456 [1 371 ; 1 500] | 4,8 % [4,1 ; 5,8] | 1,867 [1,806 ; 1,928] |
| stricte α=20 % | A6b | bureau | tous les promus | 3 134 | 129 [122 ; 135] | 672 [641 ; 717] | 0,2 % [0,1 ; 0,4] | 1,924 [1,868 ; 1,980] |
| stricte α=20 % | A6b | bureau | devenus mauvais (LEC ECR DUR EXE MSG SOR ARG) | 3 134 | 129 [122 ; 135] | 672 [641 ; 717] | 0,2 % [0,1 ; 0,4] | 1,924 [1,868 ; 1,980] |
| stricte α=20 % | A6b | service client | tous les promus | 2 531 | 172 [160 ; 183] | 1 492 [1 408 ; 1 500] | 5,0 % [4,2 ; 5,9] | 1,869 [1,809 ; 1,928] |
| stricte α=20 % | A6b | service client | devenus mauvais (LEC ECR DUR EXE MSG SOR ARG) | 2 531 | 172 [160 ; 183] | 1 492 [1 408 ; 1 500] | 5,0 % [4,2 ; 5,9] | 1,869 [1,809 ; 1,928] |
| départ α=5 % | A6b | bureau | tous les promus | 18 472 | 178 [173 ; 181] | 997 [977 ; 1 016] | 1,4 % [1,2 ; 1,6] | 3,212 [3,162 ; 3,263] |
| départ α=5 % | A6b | bureau | devenus mauvais (DUR EXE SOR ARG) | 3 605 | 93 [89 ; 96] | 381 [368 ; 400] | 0,0 % [0,0 ; 0,1] | 0,049 [0,041 ; 0,057] |
| départ α=5 % | A6b | service client | tous les promus | 19 022 | 341 [331 ; 351] | 1 500 [1 500 ; 1 500] | 13,1 % [12,7 ; 13,6] | 2,733 [2,690 ; 2,776] |
| départ α=5 % | A6b | service client | devenus mauvais (DUR EXE SOR ARG) | 4 323 | 168 [158 ; 181] | 1 353 [1 287 ; 1 403] | 3,7 % [3,1 ; 4,3] | 0,033 [0,027 ; 0,038] |
| départ α=20 % | A6b | bureau | tous les promus | 3 702 | 174 [167 ; 183] | 994 [934 ; 1 043] | 1,1 % [0,8 ; 1,5] | 3,251 [3,135 ; 3,368] |
| départ α=20 % | A6b | bureau | devenus mauvais (DUR EXE SOR ARG) | 724 | 89 [81 ; 99] | 368 [331 ; 431] | 0,0 % [0,0 ; 0,5] | 0,050 [0,032 ; 0,067] |
| départ α=20 % | A6b | service client | tous les promus | 3 852 | 341 [325 ; 361] | 1 500 [1 500 ; 1 500] | 13,3 % [12,3 ; 14,4] | 2,703 [2,610 ; 2,797] |
| départ α=20 % | A6b | service client | devenus mauvais (DUR EXE SOR ARG) | 902 | 157 [135 ; 180] | 1 305 [1 194 ; 1 420] | 3,1 % [2,2 ; 4,4] | 0,028 [0,017 ; 0,039] |
| souple α=5 % | A6b | bureau | tous les promus | 4 194 | 240 [229 ; 255] | 1 458 [1 394 ; 1 500] | 4,6 % [4,1 ; 5,3] | 5,195 [4,992 ; 5,398] |
| souple α=5 % | A6b | bureau | devenus mauvais (SOR ARG) | 428 | 139 [122 ; 161] | 688 [605 ; 821] | 0,0 % [0,0 ; 0,9] | 0,079 [0,051 ; 0,108] |
| souple α=5 % | A6b | service client | tous les promus | 4 164 | 453 [418 ; 481] | 1 500 [1 500 ; 1 500] | 21,2 % [20,0 ; 22,5] | 4,230 [4,045 ; 4,414] |
| souple α=5 % | A6b | service client | devenus mauvais (SOR ARG) | 244 | 61 [52 ; 76] | 263 [183 ; 325] | 0,0 % [0,0 ; 1,5] | 0,029 [0,008 ; 0,050] |
| souple α=20 % | A6b | bureau | tous les promus | 4 246 | 238 [228 ; 252] | 1 452 [1 375 ; 1 500] | 4,6 % [4,0 ; 5,3] | 5,130 [4,929 ; 5,332] |
| souple α=20 % | A6b | bureau | devenus mauvais (SOR ARG) | 462 | 147 [128 ; 160] | 682 [605 ; 805] | 0,0 % [0,0 ; 0,8] | 0,067 [0,043 ; 0,091] |
| souple α=20 % | A6b | service client | tous les promus | 4 211 | 447 [412 ; 474] | 1 500 [1 500 ; 1 500] | 20,9 % [19,7 ; 22,2] | 4,183 [4,000 ; 4,366] |
| souple α=20 % | A6b | service client | devenus mauvais (SOR ARG) | 280 | 59 [50 ; 69] | 276 [197 ; 333] | 0,0 % [0,0 ; 1,4] | 0,021 [0,004 ; 0,038] |
| tous les réglages | A6a | les deux | tous les promus | 18 394 au départ α = 5 %, bureau | 0 | 0 | 0,0 % | 0,000 |
| trois réussites | A6b | bureau | tous les promus | 32 964 | 72 [70 ; 73] | 444 [434 ; 451] | 0,0 % [0,0 ; 0,1] | 0,052 [0,049 ; 0,054] |
| trois réussites | A6b | service client | tous les promus | 32 974 | 75 [74 ; 77] | 777 [757 ; 790] | 1,0 % [0,9 ; 1,1] | 0,053 [0,051 ; 0,056] |
| trois réussites | A6a | bureau | tous les promus | 32 964 | 72 [70 ; 73] | 444 [434 ; 451] | 0,0 % [0,0 ; 0,1] | 0,052 [0,049 ; 0,054] |
| trois réussites | A6a | service client | tous les promus | 32 974 | 75 [74 ; 77] | 777 [757 ; 790] | 1,0 % [0,9 ; 1,1] | 0,053 [0,051 ; 0,056] |
| règle sans remise à zéro | A6b | bureau | tous les promus | 3 681 | 175 [168 ; 186] | 994 [932 ; 1 045] | 1,1 % [0,8 ; 1,5] | 3,268 [3,152 ; 3,385] |
| règle sans remise à zéro | A6b | service client | tous les promus | 3 833 | 344 [328 ; 363] | 1 500 [1 500 ; 1 500] | 13,4 % [12,3 ; 14,5] | 2,715 [2,621 ; 2,809] |
| règle sans remise à zéro | A6a | bureau | tous les promus | 3 661 | 175 [167 ; 184] | 995 [939 ; 1 045] | 1,1 % [0,8 ; 1,5] | 3,286 [3,169 ; 3,403] |
| règle sans remise à zéro | A6a | service client | tous les promus | 3 833 | 342 [327 ; 363] | 1 500 [1 500 ; 1 500] | 13,4 % [12,3 ; 14,5] | 2,715 [2,621 ; 2,809] |
| oracle | A6b | bureau | tous les promus | 25 000 | 0 [0 ; 0] | 0 [0 ; 0] | 0,0 % [0,0 ; 0,0] | 0,000 [0,000 ; 0,000] |
| oracle | A6b | service client | tous les promus | 25 000 | 0 [0 ; 0] | 0 [0 ; 0] | 0,0 % [0,0 ; 0,0] | 0,000 [0,000 ; 0,000] |
| oracle | A6a | bureau | tous les promus | 25 000 | 0 [0 ; 0] | 0 [0 ; 0] | 0,0 % [0,0 ; 0,0] | 0,000 [0,000 ; 0,000] |
| oracle | A6a | service client | tous les promus | 25 000 | 0 [0 ; 0] | 0 [0 ; 0] | 0,0 % [0,0 ; 0,0] | 0,000 [0,000 ; 0,000] |

Par type : `reactivite.csv` et `fig4_reactivite.png`.

**Consigne modifiée (A8).** À t = 1 500, le score de SOR est divisé par deux s'il est négatif. Parmi les répétitions où SOR était au palier 3 juste avant (réglage de départ, α = 5 %), comparées à A2 sur les mêmes tirages :

| mélange | agent | SOR au palier 3 à t = 1 500 | palier 3 perdu à la première sortie suivante | jamais revenu avant l'horizon | délai médian du retour |
|--|--|--|--|--|--|
| bureau | A8 | 418 sur 5 000 | 100,0 % [99,1 ; 100,0] | 25,6 % [21,6 ; 30,0] | 218 [212 ; 227] |
| bureau | A2 | 424 sur 5 000 | 0,0 % [0,0 ; 0,9] | sans objet | sans objet |
| service client | A8 | 328 sur 5 000 | 100,0 % [98,8 ; 100,0] | 31,4 % [26,6 ; 36,6] | 171 [163 ; 183] |
| service client | A2 | 336 sur 5 000 | 0,0 % [0,0 ; 1,1] | sans objet | sans objet |

Calcul : au plancher, L = ln B − a = −4,554 ; divisé par deux, −2,277, au-dessus de ln B = −2,944. Il faut 17 réussites de SOR pour revenir au palier 3.

## Comparaison avec la liste fixe et le tri par le risque

Réglage de départ, α = 5 %, validateur à 5 %, 5 000 répétitions de 3 000 actions, mêmes tirages pour toutes les règles. Valeurs pour 100 actions, intervalle à 95 %.

### Valeurs absolues

| mélange | agent | règle | charge | charge hors lectures | dégâts faibles | dégâts moyens | dégâts forts |
|--|--|--|--|--|--|--|--|
| bureau | A1 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,017 [0,016 ; 0,017] | 0,004 [0,004 ; 0,005] | 0,004 [0,004 ; 0,005] |
| bureau | A1 | liste fixe | 40,0 [40,0 ; 40,0] | 72,7 [72,7 ; 72,8] | 0,303 [0,300 ; 0,306] | 0,004 [0,004 ; 0,005] | 0,004 [0,004 ; 0,005] |
| bureau | A1 | tri par le risque | 34,0 [34,0 ; 34,0] | 61,8 [61,8 ; 61,8] | 0,332 [0,329 ; 0,335] | 0,004 [0,004 ; 0,005] | 0,004 [0,004 ; 0,005] |
| bureau | A1 | **la règle** | 19,6 [19,5 ; 19,7] | 34,9 [34,7 ; 35,1] | 0,322 [0,319 ; 0,325] | 0,052 [0,052 ; 0,053] | 0,028 [0,027 ; 0,028] |
| bureau | A1 | hasard | 19,2 [19,2 ; 19,2] | 34,1 [34,0 ; 34,1] | 0,321 [0,319 ; 0,324] | 0,053 [0,051 ; 0,054] | 0,028 [0,027 ; 0,029] |
| bureau | A1 | oracle | 4,4 [4,4 ; 4,4] | 8,0 [8,0 ; 8,0] | 0,332 [0,329 ; 0,335] | 0,080 [0,079 ; 0,082] | 0,068 [0,067 ; 0,069] |
| bureau | A1 | trois réussites | 6,6 [6,5 ; 6,6] | 10,5 [10,5 ; 10,5] | 0,326 [0,323 ; 0,329] | 0,078 [0,077 ; 0,080] | 0,066 [0,065 ; 0,067] |
| bureau | A1 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 0,332 [0,329 ; 0,335] | 0,080 [0,079 ; 0,082] | 0,089 [0,087 ; 0,090] |
| bureau | A2 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,066 [0,065 ; 0,068] | 0,016 [0,015 ; 0,016] | 0,018 [0,017 ; 0,019] |
| bureau | A2 | liste fixe | 40,0 [40,0 ; 40,0] | 72,7 [72,7 ; 72,8] | 1,205 [1,200 ; 1,211] | 0,016 [0,015 ; 0,016] | 0,018 [0,017 ; 0,019] |
| bureau | A2 | tri par le risque | 34,0 [34,0 ; 34,0] | 61,8 [61,8 ; 61,8] | 1,319 [1,313 ; 1,325] | 0,016 [0,015 ; 0,016] | 0,018 [0,017 ; 0,019] |
| bureau | A2 | **la règle** | 32,6 [32,5 ; 32,7] | 58,2 [58,0 ; 58,3] | 1,251 [1,246 ; 1,257] | 0,083 [0,082 ; 0,084] | 0,039 [0,038 ; 0,040] |
| bureau | A2 | hasard | 30,6 [30,6 ; 30,7] | 54,6 [54,6 ; 54,7] | 1,251 [1,245 ; 1,257] | 0,075 [0,074 ; 0,077] | 0,033 [0,032 ; 0,034] |
| bureau | A2 | oracle | 18,0 [18,0 ; 18,0] | 32,7 [32,7 ; 32,8] | 1,319 [1,313 ; 1,325] | 0,320 [0,317 ; 0,323] | 0,018 [0,017 ; 0,019] |
| bureau | A2 | trois réussites | 10,7 [10,7 ; 10,7] | 14,5 [14,5 ; 14,5] | 1,240 [1,235 ; 1,246] | 0,298 [0,296 ; 0,301] | 0,258 [0,256 ; 0,261] |
| bureau | A2 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 1,319 [1,313 ; 1,325] | 0,320 [0,317 ; 0,323] | 0,361 [0,357 ; 0,364] |
| bureau | A4 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,493 [0,490 ; 0,497] | 0,121 [0,119 ; 0,122] | 0,136 [0,134 ; 0,137] |
| bureau | A4 | liste fixe | 40,0 [40,0 ; 40,0] | 72,7 [72,7 ; 72,8] | 9,048 [9,034 ; 9,063] | 0,121 [0,119 ; 0,122] | 0,136 [0,134 ; 0,137] |
| bureau | A4 | tri par le risque | 34,0 [34,0 ; 34,0] | 61,8 [61,8 ; 61,8] | 9,905 [9,890 ; 9,921] | 0,121 [0,119 ; 0,122] | 0,136 [0,134 ; 0,137] |
| bureau | A4 | **la règle** | 79,8 [79,6 ; 79,9] | 93,5 [93,4 ; 93,6] | 0,577 [0,572 ; 0,582] | 0,166 [0,164 ; 0,168] | 0,174 [0,172 ; 0,176] |
| bureau | A4 | hasard | 77,9 [77,9 ; 77,9] | 90,1 [90,0 ; 90,1] | 0,577 [0,574 ; 0,581] | 0,121 [0,119 ; 0,122] | 0,136 [0,134 ; 0,137] |
| bureau | A4 | oracle | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,493 [0,490 ; 0,497] | 0,121 [0,119 ; 0,122] | 0,136 [0,134 ; 0,137] |
| bureau | A4 | trois réussites | 41,8 [41,7 ; 41,8] | 44,2 [44,2 ; 44,3] | 6,241 [6,233 ; 6,249] | 1,501 [1,496 ; 1,505] | 1,306 [1,302 ; 1,310] |
| bureau | A4 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 9,905 [9,890 ; 9,921] | 2,399 [2,391 ; 2,407] | 2,705 [2,697 ; 2,713] |
| bureau | A5 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,066 [0,065 ; 0,068] | 0,016 [0,015 ; 0,016] | 0,096 [0,095 ; 0,098] |
| bureau | A5 | liste fixe | 40,0 [40,0 ; 40,0] | 72,7 [72,7 ; 72,8] | 1,205 [1,200 ; 1,211] | 0,016 [0,015 ; 0,016] | 0,096 [0,095 ; 0,098] |
| bureau | A5 | tri par le risque | 34,0 [34,0 ; 34,0] | 61,8 [61,8 ; 61,8] | 1,319 [1,313 ; 1,325] | 0,016 [0,015 ; 0,016] | 0,096 [0,095 ; 0,098] |
| bureau | A5 | **la règle** | 33,1 [33,0 ; 33,1] | 59,0 [58,9 ; 59,2] | 1,251 [1,246 ; 1,257] | 0,082 [0,081 ; 0,083] | 0,130 [0,128 ; 0,131] |
| bureau | A5 | hasard | 31,2 [31,1 ; 31,2] | 55,6 [55,6 ; 55,6] | 1,252 [1,246 ; 1,257] | 0,077 [0,076 ; 0,079] | 0,101 [0,100 ; 0,103] |
| bureau | A5 | oracle | 18,0 [18,0 ; 18,0] | 32,7 [32,7 ; 32,8] | 1,319 [1,313 ; 1,325] | 0,320 [0,317 ; 0,323] | 0,096 [0,095 ; 0,098] |
| bureau | A5 | trois réussites | 13,8 [13,8 ; 13,8] | 20,1 [20,1 ; 20,2] | 1,240 [1,235 ; 1,246] | 0,298 [0,296 ; 0,301] | 0,996 [0,992 ; 0,999] |
| bureau | A5 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 1,319 [1,313 ; 1,325] | 0,320 [0,317 ; 0,323] | 1,921 [1,914 ; 1,928] |
| service client | A1 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,012 [0,011 ; 0,013] | 0,005 [0,005 ; 0,006] | 0,008 [0,007 ; 0,008] |
| service client | A1 | liste fixe | 55,0 [55,0 ; 55,0] | 91,7 [91,7 ; 91,7] | 0,225 [0,223 ; 0,227] | 0,005 [0,005 ; 0,006] | 0,008 [0,007 ; 0,008] |
| service client | A1 | tri par le risque | 52,0 [52,0 ; 52,0] | 86,7 [86,7 ; 86,7] | 0,239 [0,237 ; 0,242] | 0,005 [0,005 ; 0,006] | 0,008 [0,007 ; 0,008] |
| service client | A1 | **la règle** | 28,9 [28,8 ; 29,1] | 47,5 [47,2 ; 47,7] | 0,230 [0,227 ; 0,232] | 0,076 [0,074 ; 0,077] | 0,057 [0,056 ; 0,058] |
| service client | A1 | hasard | 28,2 [28,2 ; 28,2] | 46,3 [46,3 ; 46,3] | 0,229 [0,226 ; 0,231] | 0,075 [0,074 ; 0,077] | 0,057 [0,055 ; 0,058] |
| service client | A1 | oracle | 6,8 [6,8 ; 6,8] | 11,3 [11,3 ; 11,3] | 0,239 [0,237 ; 0,242] | 0,110 [0,109 ; 0,112] | 0,118 [0,116 ; 0,120] |
| service client | A1 | trois réussites | 8,9 [8,9 ; 8,9] | 13,7 [13,7 ; 13,7] | 0,234 [0,232 ; 0,236] | 0,108 [0,106 ; 0,109] | 0,115 [0,114 ; 0,117] |
| service client | A1 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 0,239 [0,237 ; 0,242] | 0,110 [0,109 ; 0,112] | 0,151 [0,149 ; 0,153] |
| service client | A2 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,048 [0,047 ; 0,050] | 0,022 [0,021 ; 0,022] | 0,030 [0,029 ; 0,031] |
| service client | A2 | liste fixe | 55,0 [55,0 ; 55,0] | 91,7 [91,7 ; 91,7] | 0,901 [0,896 ; 0,905] | 0,022 [0,021 ; 0,022] | 0,030 [0,029 ; 0,031] |
| service client | A2 | tri par le risque | 52,0 [52,0 ; 52,0] | 86,7 [86,7 ; 86,7] | 0,957 [0,952 ; 0,962] | 0,022 [0,021 ; 0,022] | 0,030 [0,029 ; 0,031] |
| service client | A2 | **la règle** | 51,9 [51,8 ; 52,0] | 85,5 [85,3 ; 85,7] | 0,896 [0,891 ; 0,900] | 0,098 [0,097 ; 0,100] | 0,065 [0,063 ; 0,066] |
| service client | A2 | hasard | 48,6 [48,6 ; 48,7] | 80,1 [80,1 ; 80,2] | 0,896 [0,891 ; 0,901] | 0,089 [0,087 ; 0,090] | 0,054 [0,053 ; 0,055] |
| service client | A2 | oracle | 30,0 [30,0 ; 30,0] | 50,0 [50,0 ; 50,0] | 0,957 [0,952 ; 0,962] | 0,440 [0,437 ; 0,443] | 0,030 [0,029 ; 0,031] |
| service client | A2 | trois réussites | 13,0 [12,9 ; 13,0] | 17,5 [17,5 ; 17,6] | 0,899 [0,895 ; 0,904] | 0,412 [0,409 ; 0,415] | 0,442 [0,439 ; 0,445] |
| service client | A2 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 0,957 [0,952 ; 0,962] | 0,440 [0,437 ; 0,443] | 0,601 [0,597 ; 0,605] |
| service client | A4 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,361 [0,358 ; 0,364] | 0,165 [0,163 ; 0,167] | 0,224 [0,222 ; 0,226] |
| service client | A4 | liste fixe | 55,0 [55,0 ; 55,0] | 91,7 [91,7 ; 91,7] | 6,768 [6,756 ; 6,781] | 0,165 [0,163 ; 0,167] | 0,224 [0,222 ; 0,226] |
| service client | A4 | tri par le risque | 52,0 [52,0 ; 52,0] | 86,7 [86,7 ; 86,7] | 7,193 [7,180 ; 7,206] | 0,165 [0,163 ; 0,167] | 0,224 [0,222 ; 0,226] |
| service client | A4 | **la règle** | 86,3 [86,2 ; 86,5] | 102,0 [102,0 ; 102,1] | 0,428 [0,424 ; 0,432] | 0,226 [0,224 ; 0,229] | 0,289 [0,286 ; 0,292] |
| service client | A4 | hasard | 83,5 [83,5 ; 83,5] | 97,3 [97,3 ; 97,4] | 0,428 [0,425 ; 0,432] | 0,165 [0,163 ; 0,167] | 0,224 [0,222 ; 0,226] |
| service client | A4 | oracle | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,361 [0,358 ; 0,364] | 0,165 [0,163 ; 0,167] | 0,224 [0,222 ; 0,226] |
| service client | A4 | trois réussites | 43,2 [43,2 ; 43,3] | 46,2 [46,2 ; 46,3] | 4,529 [4,521 ; 4,536] | 2,074 [2,069 ; 2,079] | 2,239 [2,234 ; 2,244] |
| service client | A4 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 7,193 [7,180 ; 7,206] | 3,301 [3,292 ; 3,310] | 4,503 [4,493 ; 4,514] |
| service client | A5 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,048 [0,047 ; 0,050] | 0,022 [0,021 ; 0,022] | 0,127 [0,125 ; 0,129] |
| service client | A5 | liste fixe | 55,0 [55,0 ; 55,0] | 91,7 [91,7 ; 91,7] | 0,901 [0,896 ; 0,905] | 0,022 [0,021 ; 0,022] | 0,127 [0,125 ; 0,129] |
| service client | A5 | tri par le risque | 52,0 [52,0 ; 52,0] | 86,7 [86,7 ; 86,7] | 0,957 [0,952 ; 0,962] | 0,022 [0,021 ; 0,022] | 0,127 [0,125 ; 0,129] |
| service client | A5 | **la règle** | 52,4 [52,3 ; 52,5] | 86,4 [86,2 ; 86,6] | 0,896 [0,891 ; 0,900] | 0,098 [0,097 ; 0,100] | 0,177 [0,175 ; 0,180] |
| service client | A5 | hasard | 49,3 [49,3 ; 49,3] | 81,2 [81,2 ; 81,2] | 0,895 [0,890 ; 0,900] | 0,090 [0,089 ; 0,092] | 0,139 [0,137 ; 0,141] |
| service client | A5 | oracle | 30,0 [30,0 ; 30,0] | 50,0 [50,0 ; 50,0] | 0,957 [0,952 ; 0,962] | 0,440 [0,437 ; 0,443] | 0,127 [0,125 ; 0,129] |
| service client | A5 | trois réussites | 16,9 [16,8 ; 16,9] | 24,0 [24,0 ; 24,1] | 0,899 [0,895 ; 0,904] | 0,412 [0,409 ; 0,415] | 1,368 [1,364 ; 1,372] |
| service client | A5 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 0,957 [0,952 ; 0,962] | 0,440 [0,437 ; 0,443] | 2,552 [2,544 ; 2,561] |

Les autres agents sont dans `mesures.csv` ; `fig1_charge_degats_*.png` place toutes les règles et tous les réglages dans le plan charge contre dégâts, niveau par niveau.

### Écarts appariés : la règle moins le témoin

Négatif = la règle fait mieux. Verdict selon le critère du choix 19.

| mélange | agent | contre | charge | dégâts faibles | dégâts moyens | dégâts forts | verdict |
|--|--|--|--|--|--|--|--|
| bureau | A1 | liste fixe | −20,4 [−20,5 ; −20,3] | 0,019 [0,018 ; 0,020] | 0,048 [0,047 ; 0,049] | 0,023 [0,023 ; 0,024] | compromis |
| bureau | A1 | tri | −14,4 [−14,5 ; −14,3] | −0,010 [−0,010 ; −0,009] | 0,048 [0,047 ; 0,049] | 0,023 [0,023 ; 0,024] | compromis |
| bureau | A2 | liste fixe | −7,4 [−7,5 ; −7,3] | 0,046 [0,044 ; 0,048] | 0,067 [0,066 ; 0,068] | 0,021 [0,020 ; 0,022] | compromis |
| bureau | A2 | tri | −1,4 [−1,5 ; −1,3] | −0,068 [−0,070 ; −0,066] | 0,067 [0,066 ; 0,068] | 0,021 [0,020 ; 0,022] | compromis |
| bureau | A3 | liste fixe | 0,8 [0,8 ; 0,9] | −0,310 [−0,317 ; −0,304] | 0,033 [0,032 ; 0,033] | 0,019 [0,019 ; 0,020] | compromis |
| bureau | A3 | tri | 6,8 [6,8 ; 6,9] | −0,595 [−0,602 ; −0,588] | 0,033 [0,032 ; 0,033] | 0,019 [0,019 ; 0,020] | compromis |
| bureau | A4 | liste fixe | 39,8 [39,6 ; 39,9] | −8,472 [−8,487 ; −8,456] | 0,046 [0,045 ; 0,047] | 0,039 [0,038 ; 0,040] | compromis |
| bureau | A4 | tri | 45,8 [45,7 ; 45,9] | −9,328 [−9,345 ; −9,312] | 0,046 [0,045 ; 0,047] | 0,039 [0,038 ; 0,040] | compromis |
| bureau | A5 | liste fixe | −7,0 [−7,0 ; −6,9] | 0,046 [0,044 ; 0,048] | 0,067 [0,066 ; 0,068] | 0,033 [0,032 ; 0,034] | compromis |
| bureau | A5 | tri | −0,9 [−1,0 ; −0,9] | −0,068 [−0,070 ; −0,066] | 0,067 [0,066 ; 0,068] | 0,033 [0,032 ; 0,034] | compromis |
| bureau | A6a | liste fixe | 6,2 [6,1 ; 6,3] | −2,073 [−2,090 ; −2,056] | 0,053 [0,052 ; 0,054] | 0,024 [0,024 ; 0,025] | compromis |
| bureau | A6a | tri | 12,2 [12,1 ; 12,3] | −2,416 [−2,433 ; −2,399] | 0,053 [0,052 ; 0,054] | 0,024 [0,024 ; 0,025] | compromis |
| bureau | A6b | liste fixe | 2,7 [2,6 ; 2,8] | −1,676 [−1,692 ; −1,660] | 0,069 [0,068 ; 0,070] | 0,028 [0,028 ; 0,029] | compromis |
| bureau | A6b | tri | 8,7 [8,7 ; 8,8] | −2,019 [−2,035 ; −2,003] | 0,069 [0,068 ; 0,070] | 0,028 [0,028 ; 0,029] | compromis |
| bureau | A7 | liste fixe | 10,9 [10,8 ; 11,0] | −2,071 [−2,088 ; −2,054] | 0,030 [0,029 ; 0,031] | 0,023 [0,023 ; 0,024] | compromis |
| bureau | A7 | tri | 16,9 [16,9 ; 17,0] | −2,414 [−2,431 ; −2,396] | 0,030 [0,029 ; 0,031] | 0,023 [0,023 ; 0,024] | compromis |
| bureau | A8 | liste fixe | −7,4 [−7,5 ; −7,3] | 0,046 [0,044 ; 0,048] | 0,067 [0,066 ; 0,068] | 0,019 [0,018 ; 0,020] | compromis |
| bureau | A8 | tri | −1,4 [−1,4 ; −1,3] | −0,068 [−0,070 ; −0,066] | 0,067 [0,066 ; 0,068] | 0,019 [0,018 ; 0,020] | compromis |
| bureau | A2-calibre | liste fixe | −8,4 [−8,5 ; −8,3] | 0,040 [0,039 ; 0,042] | 0,072 [0,071 ; 0,073] | 0,027 [0,026 ; 0,027] | compromis |
| bureau | A2-calibre | tri | −2,7 [−2,8 ; −2,6] | −0,040 [−0,041 ; −0,039] | 0,072 [0,071 ; 0,073] | 0,027 [0,026 ; 0,027] | compromis |
| bureau | A2-abusif | liste fixe | −4,2 [−4,3 ; −4,2] | 0,018 [0,016 ; 0,020] | 0,052 [0,051 ; 0,053] | 0,016 [0,015 ; 0,017] | compromis |
| bureau | A2-abusif | tri | −0,0 [−0,1 ; 0,0] | −0,062 [−0,063 ; −0,060] | 0,052 [0,051 ; 0,053] | 0,016 [0,015 ; 0,017] | compromis |
| bureau | A4-calibre | liste fixe | 22,1 [22,0 ; 22,2] | −5,101 [−5,126 ; −5,077] | 0,091 [0,089 ; 0,092] | 0,078 [0,077 ; 0,080] | compromis |
| bureau | A4-calibre | tri | 27,8 [27,7 ; 28,0] | −5,703 [−5,728 ; −5,678] | 0,091 [0,089 ; 0,092] | 0,078 [0,077 ; 0,080] | compromis |
| bureau | A4-abusif | liste fixe | 29,4 [29,3 ; 29,5] | −5,908 [−5,922 ; −5,895] | 0,065 [0,063 ; 0,066] | 0,056 [0,054 ; 0,057] | compromis |
| bureau | A4-abusif | tri | 33,6 [33,5 ; 33,7] | −6,507 [−6,521 ; −6,493] | 0,065 [0,063 ; 0,066] | 0,056 [0,054 ; 0,057] | compromis |
| service client | A1 | liste fixe | −26,1 [−26,2 ; −25,9] | 0,005 [0,004 ; 0,006] | 0,070 [0,069 ; 0,071] | 0,050 [0,049 ; 0,050] | compromis |
| service client | A1 | tri | −23,1 [−23,2 ; −23,0] | −0,009 [−0,010 ; −0,009] | 0,070 [0,069 ; 0,071] | 0,050 [0,049 ; 0,050] | compromis |
| service client | A2 | liste fixe | −3,1 [−3,2 ; −3,0] | −0,005 [−0,007 ; −0,003] | 0,077 [0,075 ; 0,078] | 0,035 [0,034 ; 0,035] | compromis |
| service client | A2 | tri | −0,1 [−0,2 ; −0,0] | −0,062 [−0,063 ; −0,060] | 0,077 [0,075 ; 0,078] | 0,035 [0,034 ; 0,035] | compromis |
| service client | A3 | liste fixe | 4,4 [4,4 ; 4,5] | −0,322 [−0,328 ; −0,317] | 0,039 [0,038 ; 0,040] | 0,032 [0,031 ; 0,033] | compromis |
| service client | A3 | tri | 7,4 [7,4 ; 7,5] | −0,464 [−0,470 ; −0,458] | 0,039 [0,038 ; 0,040] | 0,032 [0,031 ; 0,033] | compromis |
| service client | A4 | liste fixe | 31,3 [31,2 ; 31,4] | −6,340 [−6,354 ; −6,327] | 0,061 [0,060 ; 0,063] | 0,065 [0,063 ; 0,066] | compromis |
| service client | A4 | tri | 34,3 [34,2 ; 34,4] | −6,765 [−6,779 ; −6,751] | 0,061 [0,060 ; 0,063] | 0,065 [0,063 ; 0,066] | compromis |
| service client | A5 | liste fixe | −2,6 [−2,7 ; −2,5] | −0,005 [−0,007 ; −0,003] | 0,077 [0,076 ; 0,078] | 0,051 [0,050 ; 0,052] | compromis |
| service client | A5 | tri | 0,4 [0,3 ; 0,5] | −0,062 [−0,063 ; −0,060] | 0,077 [0,076 ; 0,078] | 0,051 [0,050 ; 0,052] | compromis |
| service client | A6a | liste fixe | 7,1 [7,0 ; 7,2] | −1,608 [−1,623 ; −1,594] | 0,065 [0,064 ; 0,066] | 0,045 [0,044 ; 0,046] | compromis |
| service client | A6a | tri | 10,1 [10,0 ; 10,2] | −1,779 [−1,794 ; −1,765] | 0,065 [0,064 ; 0,066] | 0,045 [0,044 ; 0,046] | compromis |
| service client | A6b | liste fixe | 4,0 [3,9 ; 4,1] | −1,276 [−1,289 ; −1,262] | 0,079 [0,078 ; 0,080] | 0,047 [0,046 ; 0,048] | compromis |
| service client | A6b | tri | 7,0 [6,9 ; 7,1] | −1,446 [−1,460 ; −1,432] | 0,079 [0,078 ; 0,080] | 0,047 [0,046 ; 0,048] | compromis |
| service client | A7 | liste fixe | 12,8 [12,8 ; 12,9] | −1,613 [−1,628 ; −1,599] | 0,036 [0,035 ; 0,037] | 0,037 [0,036 ; 0,038] | compromis |
| service client | A7 | tri | 15,8 [15,8 ; 15,9] | −1,784 [−1,798 ; −1,769] | 0,036 [0,035 ; 0,037] | 0,037 [0,036 ; 0,038] | compromis |
| service client | A8 | liste fixe | −3,1 [−3,2 ; −3,0] | −0,005 [−0,007 ; −0,003] | 0,077 [0,076 ; 0,078] | 0,033 [0,032 ; 0,034] | compromis |
| service client | A8 | tri | −0,1 [−0,2 ; 0,0] | −0,062 [−0,063 ; −0,060] | 0,077 [0,076 ; 0,078] | 0,033 [0,032 ; 0,034] | compromis |
| service client | A2-calibre | liste fixe | −4,9 [−5,1 ; −4,8] | 0,003 [0,002 ; 0,004] | 0,091 [0,090 ; 0,093] | 0,050 [0,049 ; 0,051] | compromis |
| service client | A2-calibre | tri | −2,1 [−2,2 ; −2,0] | −0,037 [−0,038 ; −0,036] | 0,091 [0,090 ; 0,093] | 0,050 [0,049 ; 0,051] | compromis |
| service client | A2-abusif | liste fixe | −1,2 [−1,3 ; −1,1] | −0,016 [−0,018 ; −0,015] | 0,064 [0,063 ; 0,065] | 0,030 [0,029 ; 0,031] | compromis |
| service client | A2-abusif | tri | 0,9 [0,8 ; 1,0] | −0,056 [−0,058 ; −0,055] | 0,064 [0,063 ; 0,065] | 0,030 [0,029 ; 0,031] | compromis |
| service client | A4-calibre | liste fixe | 20,0 [19,9 ; 20,1] | −3,869 [−3,890 ; −3,848] | 0,123 [0,122 ; 0,125] | 0,130 [0,128 ; 0,131] | compromis |
| service client | A4-calibre | tri | 22,9 [22,8 ; 22,9] | −4,167 [−4,188 ; −4,145] | 0,123 [0,122 ; 0,125] | 0,130 [0,128 ; 0,131] | compromis |
| service client | A4-abusif | liste fixe | 24,2 [24,1 ; 24,3] | −4,432 [−4,444 ; −4,421] | 0,088 [0,086 ; 0,089] | 0,093 [0,091 ; 0,095] | compromis |
| service client | A4-abusif | tri | 26,3 [26,2 ; 26,4] | −4,730 [−4,741 ; −4,718] | 0,088 [0,086 ; 0,089] | 0,093 [0,091 ; 0,095] | compromis |

### Illustration seulement : un barème 1, 10, 100

REGLE.md, pièce 2 : un barème peut illustrer, jamais servir de critère. Dégâts pondérés = faibles + 10 × moyens + 100 × forts, pour 100 actions, avec leur intervalle.

| mélange | agent | tout faire valider | liste fixe | tri par le risque | la règle |
|--|--|--|--|--|--|
| bureau | A1 | 0,50 [0,47 ; 0,54] | 0,79 [0,75 ; 0,82] | 0,82 [0,78 ; 0,85] | 3,62 [3,55 ; 3,69] |
| bureau | A2 | 2,03 [1,96 ; 2,10] | 3,17 [3,10 ; 3,24] | 3,28 [3,21 ; 3,35] | 5,98 [5,89 ; 6,07] |
| bureau | A3 | 5,17 [5,07 ; 5,28] | 8,03 [7,92 ; 8,13] | 8,31 [8,20 ; 8,42] | 9,98 [9,86 ; 10,11] |
| bureau | A4 | 15,25 [15,07 ; 15,44] | 23,81 [23,63 ; 23,99] | 24,67 [24,48 ; 24,85] | 19,67 [19,45 ; 19,88] |
| bureau | A5 | 9,86 [9,70 ; 10,01] | 11,00 [10,84 ; 11,15] | 11,11 [10,96 ; 11,27] | 15,03 [14,86 ; 15,21] |
| service client | A1 | 0,83 [0,79 ; 0,88] | 1,04 [1,00 ; 1,09] | 1,06 [1,01 ; 1,10] | 6,71 [6,62 ; 6,80] |
| service client | A2 | 3,27 [3,18 ; 3,36] | 4,12 [4,03 ; 4,21] | 4,18 [4,09 ; 4,27] | 8,34 [8,22 ; 8,45] |
| service client | A3 | 8,12 [7,98 ; 8,26] | 10,26 [10,12 ; 10,40] | 10,40 [10,26 ; 10,54] | 13,54 [13,37 ; 13,70] |
| service client | A4 | 24,42 [24,17 ; 24,66] | 30,82 [30,58 ; 31,07] | 31,25 [31,01 ; 31,49] | 31,57 [31,30 ; 31,84] |
| service client | A5 | 12,95 [12,77 ; 13,13] | 13,80 [13,62 ; 13,98] | 13,86 [13,68 ; 14,04] | 19,62 [19,41 ; 19,83] |

## Variantes du validateur : 0, 2, 5 et 10 %

Réglage de départ, α = 5 %, 5 000 répétitions. La trajectoire de la règle ne dépend pas de e (le contrôle automatique voit tout) ; seuls changent les dégâts et les corrections. Marge : plus petite valeur de la grille qui passe pour l'agent dans le mélange.

| e | mélange | agent | charge | écart de dégâts avec tout valider : faibles ; moyens ; forts | plus petite marge qui passe (faible / moyen / fort) | contre liste fixe | contre tri |
|--|--|--|--|--|--|--|--|
| 0 % | bureau | A1 | 19,6 [19,5 ; 19,7] | 0,321 [0,319 ; 0,324] ; 0,051 [0,050 ; 0,052] ; 0,024 [0,024 ; 0,025] | 0,5 / 0,1 / 0,05 | compromis | compromis |
| 0 % | bureau | A2 | 32,6 [32,5 ; 32,7] | 1,248 [1,242 ; 1,253] ; 0,064 [0,063 ; 0,065] ; 0,016 [0,016 ; 0,017] | aucune (> 1) / 0,1 / 0,02 | compromis | compromis |
| 0 % | bureau | A4 | 80,0 [79,8 ; 80,1] | 0,088 [0,085 ; 0,092] ; 0,000 [0,000 ; 0,000] ; 0,000 [0,000 ; 0,000] | 0,1 / 0,005 / 0 | compromis | compromis |
| 0 % | service client | A1 | 28,9 [28,8 ; 29,1] | 0,229 [0,227 ; 0,232] ; 0,073 [0,072 ; 0,074] ; 0,051 [0,051 ; 0,052] | 0,5 / 0,1 / 0,1 | compromis | compromis |
| 0 % | service client | A2 | 51,9 [51,8 ; 52,0] | 0,892 [0,888 ; 0,897] ; 0,070 [0,069 ; 0,072] ; 0,026 [0,025 ; 0,027] | 1 / 0,1 / 0,05 | compromis | compromis |
| 0 % | service client | A4 | 86,5 [86,4 ; 86,6] | 0,071 [0,068 ; 0,074] ; 0,000 [0,000 ; 0,000] ; 0,000 [0,000 ; 0,000] | 0,1 / 0,005 / 0 | compromis | compromis |
| 2 % | bureau | A1 | 19,6 [19,5 ; 19,7] | 0,315 [0,312 ; 0,318] ; 0,050 [0,049 ; 0,050] ; 0,024 [0,023 ; 0,025] | 0,5 / 0,1 / 0,05 | compromis | compromis |
| 2 % | bureau | A2 | 32,6 [32,5 ; 32,7] | 1,222 [1,217 ; 1,228] ; 0,065 [0,064 ; 0,066] ; 0,018 [0,018 ; 0,019] | aucune (> 1) / 0,1 / 0,02 | compromis | compromis |
| 2 % | bureau | A4 | 79,9 [79,8 ; 80,0] | 0,086 [0,083 ; 0,090] ; 0,018 [0,017 ; 0,018] ; 0,016 [0,016 ; 0,017] | 0,1 / 0,02 / 0,02 | compromis | compromis |
| 2 % | service client | A1 | 28,9 [28,8 ; 29,1] | 0,225 [0,222 ; 0,227] ; 0,072 [0,071 ; 0,073] ; 0,051 [0,050 ; 0,052] | 0,5 / 0,1 / 0,1 | compromis | compromis |
| 2 % | service client | A2 | 51,9 [51,8 ; 52,0] | 0,875 [0,870 ; 0,879] ; 0,073 [0,072 ; 0,074] ; 0,029 [0,028 ; 0,030] | 1 / 0,1 / 0,05 | compromis | compromis |
| 2 % | service client | A4 | 86,4 [86,3 ; 86,5] | 0,069 [0,066 ; 0,072] ; 0,025 [0,024 ; 0,026] ; 0,026 [0,025 ; 0,026] | 0,1 / 0,05 / 0,05 | compromis | compromis |
| 5 % | bureau | A1 | 19,6 [19,5 ; 19,7] | 0,305 [0,302 ; 0,308] ; 0,048 [0,047 ; 0,049] ; 0,023 [0,023 ; 0,024] | 0,5 / 0,05 / 0,05 | compromis | compromis |
| 5 % | bureau | A2 | 32,6 [32,5 ; 32,7] | 1,185 [1,180 ; 1,190] ; 0,067 [0,066 ; 0,068] ; 0,021 [0,020 ; 0,022] | aucune (> 1) / 0,1 / 0,05 | compromis | compromis |
| 5 % | bureau | A4 | 79,8 [79,6 ; 79,9] | 0,084 [0,080 ; 0,087] ; 0,046 [0,045 ; 0,047] ; 0,039 [0,038 ; 0,040] | 0,1 / 0,05 / 0,05 | compromis | compromis |
| 5 % | service client | A1 | 28,9 [28,8 ; 29,1] | 0,218 [0,216 ; 0,220] ; 0,070 [0,069 ; 0,071] ; 0,050 [0,049 ; 0,050] | 0,5 / 0,1 / 0,1 | compromis | compromis |
| 5 % | service client | A2 | 51,9 [51,8 ; 52,0] | 0,847 [0,843 ; 0,852] ; 0,077 [0,075 ; 0,078] ; 0,035 [0,034 ; 0,035] | 1 / 0,1 / 0,05 | compromis | compromis |
| 5 % | service client | A4 | 86,3 [86,2 ; 86,5] | 0,067 [0,064 ; 0,070] ; 0,061 [0,060 ; 0,063] ; 0,065 [0,063 ; 0,066] | 0,1 / 0,1 / 0,1 | compromis | compromis |
| 10 % | bureau | A1 | 19,6 [19,5 ; 19,7] | 0,289 [0,286 ; 0,292] ; 0,046 [0,045 ; 0,047] ; 0,023 [0,022 ; 0,023] | 0,5 / 0,05 / 0,05 | compromis | compromis |
| 10 % | bureau | A2 | 32,6 [32,5 ; 32,7] | 1,122 [1,117 ; 1,127] ; 0,070 [0,069 ; 0,071] ; 0,026 [0,025 ; 0,026] | aucune (> 1) / 0,1 / 0,05 | compromis | compromis |
| 10 % | bureau | A4 | 79,6 [79,5 ; 79,7] | 0,079 [0,076 ; 0,082] ; 0,089 [0,088 ; 0,091] ; 0,078 [0,077 ; 0,080] | 0,1 / 0,1 / 0,1 | compromis | compromis |
| 10 % | service client | A1 | 28,9 [28,8 ; 29,1] | 0,207 [0,205 ; 0,209] ; 0,067 [0,066 ; 0,068] ; 0,048 [0,047 ; 0,048] | 0,5 / 0,1 / 0,05 | compromis | compromis |
| 10 % | service client | A2 | 51,9 [51,8 ; 52,0] | 0,804 [0,800 ; 0,809] ; 0,083 [0,081 ; 0,084] ; 0,043 [0,042 ; 0,044] | 1 / 0,1 / 0,05 | compromis | compromis |
| 10 % | service client | A4 | 86,2 [86,1 ; 86,3] | 0,064 [0,061 ; 0,066] ; 0,125 [0,123 ; 0,126] ; 0,131 [0,129 ; 0,132] | 0,1 / 0,2 / 0,2 | compromis | compromis |

## Ablations

Réglage de départ, α = 5 %, validateur à 5 %, 1 000 répétitions (les 1 000 premières des mêmes tirages que la règle). Écarts appariés : l'ablation moins la règle amendée.

| ablation | charge A1 bureau ; service client | charge A2 bureau ; service client | écart de charge A2 bureau | écart de dégâts A2 bureau : faibles ; moyens ; forts | agent le plus touché en charge (bureau) : écart de charge ; dégâts faibles ; moyens ; forts | garantie, pire couple stable | bat liste fixe / tri (26 couples) |
|--|--|--|--|--|--|--|--|
| règle amendée (référence) | 19,6 [19,5 ; 19,7] ; 28,9 [28,8 ; 29,1] | 32,6 [32,5 ; 32,7] ; 51,9 [51,8 ; 52,0] | — | — | — | A3 sur SOR (service client) : 2,9 % [2,5 ; 3,4], n = 5 000 → **passe** | — |
| sans remise à zéro | 19,6 [19,4 ; 19,9] ; 28,7 [28,4 ; 29,0] | 32,5 [32,3 ; 32,7] ; 51,7 [51,4 ; 51,9] | −0,1 [−0,2 ; 0,1] | 0,000 [0,000 ; 0,000] ; −0,001 [−0,003 ; 0,001] ; 0,000 [−0,001 ; 0,002] | A6a : −3,5 [−3,6 ; −3,4] ; 0,406 [0,395 ; 0,418] ; 0,016 [0,014 ; 0,019] ; 0,003 [0,001 ; 0,005] | A3 sur ARG (service client) : 3,1 % [2,2 ; 4,4], n = 1 000 → **passe** | compromis 26 / compromis 26 |
| sans pondération par l'enjeu | 17,4 [17,2 ; 17,6] ; 24,7 [24,4 ; 24,9] | 33,4 [33,2 ; 33,7] ; 50,9 [50,6 ; 51,2] | 0,9 [0,7 ; 1,0] | −0,165 [−0,172 ; −0,158] ; −0,001 [−0,003 ; 0,001] ; 0,036 [0,034 ; 0,038] | A4-calibre : 31,7 [31,6 ; 31,9] ; −0,913 [−0,946 ; −0,879] ; −0,002 [−0,006 ; 0,002] ; 0,001 [−0,003 ; 0,005] | A4 sur MSG (service client) : 1,0 % [0,5 ; 1,8], n = 1 000 → **passe** | compromis 26 / compromis 26 |
| sans doute gratuit | 19,6 [19,4 ; 19,8] ; 28,7 [28,4 ; 29,0] | 32,6 [32,4 ; 32,8] ; 51,8 [51,5 ; 52,0] | 0,0 [−0,1 ; 0,2] | 0,000 [0,000 ; 0,000] ; −0,002 [−0,004 ; −0,000] ; 0,000 [−0,001 ; 0,001] | A2-abusif : 48,7 [48,5 ; 48,9] ; −0,819 [−0,829 ; −0,810] ; −0,044 [−0,046 ; −0,042] ; −0,008 [−0,010 ; −0,007] | A3 sur ARG (service client) : 3,2 % [2,3 ; 4,5], n = 1 000 → **passe** | compromis 26 / compromis 26 |
| sans palier du milieu | 21,4 [21,2 ; 21,7] ; 29,8 [29,4 ; 30,1] | 35,6 [35,4 ; 35,8] ; 53,5 [53,3 ; 53,8] | 3,0 [2,9 ; 3,1] | 0,000 [0,000 ; 0,000] ; −0,001 [−0,004 ; 0,001] ; −0,000 [−0,001 ; 0,001] | A4-calibre : 30,1 [29,9 ; 30,3] ; 0,000 [0,000 ; 0,000] ; −0,000 [−0,004 ; 0,004] ; −0,002 [−0,006 ; 0,002] | A3 sur ARG (service client) : 3,0 % [2,1 ; 4,3], n = 1 000 → **passe** | compromis 26 / compromis 26 |
| sans épreuve | 18,9 [18,7 ; 19,1] ; 27,5 [27,2 ; 27,8] | 28,6 [28,5 ; 28,8] ; 45,5 [45,3 ; 45,7] | −3,9 [−4,0 ; −3,8] | 0,000 [0,000 ; 0,000] ; 0,013 [0,011 ; 0,015] ; −0,004 [−0,005 ; −0,003] | A7 : −7,4 [−7,5 ; −7,3] ; 0,000 [0,000 ; 0,000] ; 0,007 [0,005 ; 0,010] ; −0,019 [−0,021 ; −0,017] | A3 sur SOR (bureau) : 3,6 % [2,6 ; 4,9], n = 1 000 → **passe** | compromis 26 / compromis 26 |

Réactivité des ablations (95e centile du délai, tous les types promus, et part non retirée) :

| variante | A6a bureau | A6b bureau | A6a service client | A6b service client |
|--|--|--|--|--|
| règle amendée | 0 [0 ; 0], non retiré 0,0 % | 997 [977 ; 1 016], non retiré 1,4 % | 0 [0 ; 0], non retiré 0,0 % | 1 500 [1 500 ; 1 500], non retiré 13,1 % |
| sans remise à zéro | 995 [939 ; 1 045], non retiré 1,1 % | 994 [932 ; 1 045], non retiré 1,1 % | 1 500 [1 500 ; 1 500], non retiré 13,4 % | 1 500 [1 500 ; 1 500], non retiré 13,4 % |
| sans épreuve | 0 [0 ; 0], non retiré 0,0 % | 962 [892 ; 1 010], non retiré 1,0 % | 0 [0 ; 0], non retiré 0,0 % | 1 500 [1 500 ; 1 500], non retiré 12,8 % |
| sans palier du milieu | 0 [0 ; 0], non retiré 0,0 % | 754 [706 ; 806], non retiré 0,6 % | 0 [0 ; 0], non retiré 0,0 % | 1 500 [1 500 ; 1 500], non retiré 6,9 % |
| sans pondération | 0 [0 ; 0], non retiré 0,0 % | 644 [604 ; 676], non retiré 0,1 % | 0 [0 ; 0], non retiré 0,0 % | 1 416 [1 349 ; 1 464], non retiré 4,3 % |

Ce que montrent les ablations, mesuré (bureau) :

- **Sans remise à zéro** : rien ne change hors changement de configuration. Pour A6a, dégâts faibles en plus 0,406 [0,395 ; 0,418] et charge −3,5 [−3,6 ; −3,4] : la dégradation annoncée n'est plus vue.
- **Sans pondération par l'enjeu** : A1, charge −2,3 [−2,4 ; −2,2] et dégâts forts 0,017 [0,015 ; 0,018] ; A4, charge 21,9 [21,6 ; 22,2] et dégâts faibles −0,080 [−0,087 ; −0,072].
- **Sans doute gratuit** : l'agent qui doute à bon escient paie (A2 calibré : charge 11,7 [11,4 ; 12,0]) ; le pire couple « doute » de la garantie passe de 1,7 % [1,4 ; 2,1] (n = 5 000) à 0,7 % [0,3 ; 1,4] (n = 1 000).
- **Sans palier du milieu** : dégâts inchangés (A1, dégâts faibles 0,000 [0,000 ; 0,000]), charge en plus : A1 1,8 [1,7 ; 1,8], A4 21,7 [21,4 ; 22,0].
- **Sans épreuve** : A4, charge −1,9 [−1,9 ; −1,9] et dégâts forts −0,038 [−0,040 ; −0,036] (les variantes d'épreuve comptent comme de vraies tâches, choix 5) ; A2, dégâts moyens 0,013 [0,011 ; 0,015].

Interprété : le palier 2 ne coûte toujours aucun dégât dans ce modèle (une correction après coup vaut une validation avant). Sans épreuve, un bon agent revient plus vite au palier 3 après une erreur à enjeu moyen ou fort, d'où un peu plus de dégâts moyens ; l'épreuve garde donc un effet en v2.

## Agents bons laissés de côté, délai de promotion

Règle amendée, réglage de départ, α = 5 %, 5 000 répétitions. « Jamais » : part des répétitions où le type n'atteint jamais le palier 3 avant l'horizon (Wilson). Délai : numéro de l'action (tous types) de la première promotion au palier 3, parmi les répétitions promues (centiles : rééchantillonnage). « Bon » : q au plus pb du palier 3 (A2 n'est pas bon à enjeu fort, où pb = 1 %).

| mélange | agent | type | bon ? | jamais promu au palier 3 | répétitions promues | délai moyen | délai médian | 90e centile |
|--|--|--|--|--|--|--|--|--|
| bureau | A1 | LEC | oui | 0,0 % [0,0 ; 0,1] | 5 000 | 43 [43 ; 43] | 41 [41 ; 41] | 56 [55 ; 56] |
| bureau | A1 | ECR | oui | 0,0 % [0,0 ; 0,1] | 5 000 | 131 [130 ; 132] | 126 [125 ; 127] | 176 [172 ; 178] |
| bureau | A1 | DUR | oui | 0,1 % [0,1 ; 0,3] | 4 994 | 577 [569 ; 586] | 475 [472 ; 477] | 973 [946 ; 1 002] |
| bureau | A1 | EXE | oui | 0,1 % [0,1 ; 0,3] | 4 994 | 567 [558 ; 576] | 472 [468 ; 475] | 938 [910 ; 977] |
| bureau | A1 | MSG | oui | 0,0 % [0,0 ; 0,1] | 5 000 | 331 [328 ; 334] | 317 [314 ; 320] | 445 [438 ; 453] |
| bureau | A1 | SOR | oui | 5,0 % [4,5 ; 5,7] | 4 748 | 1 083 [1 067 ; 1 098] | 824 [819 ; 830] | 1 966 [1 931 ; 2 007] |
| bureau | A1 | ARG | oui | 28,3 % [27,1 ; 29,6] | 3 583 | 1 913 [1 904 ; 1 921] | 1 886 [1 876 ; 1 894] | 2 212 [2 196 ; 2 228] |
| bureau | A2 | LEC | oui | 0,0 % [0,0 ; 0,1] | 5 000 | 50 [49 ; 51] | 45 [44 ; 45] | 72 [71 ; 74] |
| bureau | A2 | ECR | oui | 0,0 % [0,0 ; 0,1] | 5 000 | 153 [152 ; 155] | 137 [136 ; 139] | 230 [226 ; 234] |
| bureau | A2 | DUR | oui | 22,7 % [21,6 ; 23,9] | 3 863 | 833 [813 ; 852] | 520 [515 ; 526] | 1 802 [1 729 ; 1 864] |
| bureau | A2 | EXE | oui | 22,9 % [21,8 ; 24,1] | 3 855 | 826 [807 ; 846] | 517 [511 ; 525] | 1 827 [1 732 ; 1 924] |
| bureau | A2 | MSG | oui | 0,0 % [0,0 ; 0,1] | 5 000 | 383 [379 ; 387] | 349 [345 ; 351] | 564 [555 ; 575] |
| bureau | A2 | SOR | non | 65,8 % [64,5 ; 67,1] | 1 708 | 1 180 [1 150 ; 1 210] | 842 [827 ; 853] | 2 292 [2 163 ; 2 390] |
| bureau | A2 | ARG | non | 74,7 % [73,5 ; 75,9] | 1 264 | 1 917 [1 902 ; 1 932] | 1 884 [1 869 ; 1 901] | 2 216 [2 192 ; 2 251] |
| service client | A1 | LEC | oui | 0,0 % [0,0 ; 0,1] | 5 000 | 48 [48 ; 49] | 46 [46 ; 47] | 63 [62 ; 64] |
| service client | A1 | ECR | oui | 0,0 % [0,0 ; 0,1] | 5 000 | 397 [394 ; 400] | 382 [379 ; 385] | 533 [526 ; 539] |
| service client | A1 | DUR | oui | 0,0 % [0,0 ; 0,1] | 5 000 | 222 [219 ; 226] | 188 [187 ; 189] | 353 [341 ; 371] |
| service client | A1 | EXE | oui | 14,8 % [13,9 ; 15,8] | 4 259 | 1 864 [1 854 ; 1 874] | 1 833 [1 822 ; 1 843] | 2 296 [2 279 ; 2 322] |
| service client | A1 | MSG | oui | 0,0 % [0,0 ; 0,1] | 5 000 | 661 [656 ; 666] | 638 [632 ; 645] | 890 [879 ; 903] |
| service client | A1 | SOR | oui | 2,4 % [2,0 ; 2,8] | 4 882 | 931 [916 ; 946] | 670 [665 ; 674] | 1 754 [1 675 ; 1 804] |
| service client | A1 | ARG | oui | 3,0 % [2,5 ; 3,5] | 4 852 | 944 [929 ; 958] | 708 [704 ; 712] | 1 716 [1 689 ; 1 772] |
| service client | A2 | LEC | oui | 0,0 % [0,0 ; 0,1] | 5 000 | 57 [56 ; 57] | 51 [50 ; 51] | 83 [81 ; 84] |
| service client | A2 | ECR | oui | 0,0 % [0,0 ; 0,1] | 5 000 | 461 [456 ; 466] | 419 [413 ; 423] | 690 [676 ; 701] |
| service client | A2 | DUR | oui | 11,6 % [10,7 ; 12,5] | 4 420 | 513 [496 ; 531] | 215 [212 ; 219] | 1 329 [1 251 ; 1 402] |
| service client | A2 | EXE | oui | 49,3 % [47,9 ; 50,7] | 2 535 | 1 875 [1 862 ; 1 889] | 1 837 [1 820 ; 1 852] | 2 330 [2 296 ; 2 358] |
| service client | A2 | MSG | oui | 0,0 % [0,0 ; 0,1] | 4 998 | 771 [762 ; 779] | 701 [691 ; 708] | 1 147 [1 122 ; 1 173] |
| service client | A2 | SOR | non | 63,1 % [61,7 ; 64,4] | 1 846 | 1 052 [1 023 ; 1 082] | 699 [686 ; 709] | 2 176 [2 041 ; 2 250] |
| service client | A2 | ARG | non | 63,8 % [62,5 ; 65,2] | 1 808 | 1 059 [1 030 ; 1 089] | 724 [717 ; 736] | 2 144 [2 029 ; 2 239] |

Le premier passage au palier 3 suit les mêmes seuils qu'en v1 (35 réussites, 72 à enjeu fort au départ) ; ce qui change en v2, c'est ce qui se passe ensuite (`promotion.csv`, `fig3_delai_promotion.png`).

## Épreuves : réussite comparée aux tâches ordinaires

Réglage de départ, α = 5 %, 5 000 répétitions. Réussite d'une épreuve : les 3 variantes justes. Tâches ordinaires : actions vérifiables des types à enjeu moyen ou fort (n : leur nombre, toutes répétitions). Rapports : méthode delta, répétition par répétition ; « 3 tâches » : la réussite d'une tâche au cube.

| mélange | agent | épreuves par répétition | réussite d'une épreuve | réussite d'une variante | réussite d'une tâche ordinaire | 3 tâches ordinaires | 3 tâches difficiles ordinaires |
|--|--|--|--|--|--|--|--|
| bureau | A1 | 4,5 [4,4 ; 4,5] | 91,3 % [90,9 ; 91,6] | 97,0 % [96,9 ; 97,1] | 99,50 % [99,50 ; 99,51] (n = 4 216 886) | 98,5 % [98,5 ; 98,5] | 91,4 % [91,2 ; 91,5] |
| bureau | A2 | 19,5 [19,4 ; 19,7] | 68,3 % [68,0 ; 68,6] | 88,1 % [88,0 ; 88,2] | 98,00 % [97,98 ; 98,01] (n = 4 216 886) | 94,1 % [94,1 ; 94,2] | 68,3 % [68,1 ; 68,5] |
| bureau | A3 | 25,3 [25,2 ; 25,4] | 34,4 % [34,1 ; 34,6] | 70,1 % [69,9 ; 70,2] | 94,99 % [94,97 ; 95,01] (n = 4 216 886) | 85,7 % [85,7 ; 85,8] | 34,4 % [34,2 ; 34,6] |
| bureau | A4 | 18,9 [18,9 ; 18,9] | 0,1 % [0,1 ; 0,1] | 10,0 % [9,9 ; 10,1] | 84,98 % [84,95 ; 85,02] (n = 4 216 886) | 61,4 % [61,3 ; 61,4] | 0,1 % [0,1 ; 0,1] |
| bureau | A5 | 18,9 [18,8 ; 19,0] | 46,6 % [46,3 ; 46,9] | 63,2 % [63,0 ; 63,4] | 93,77 % [93,75 ; 93,80] (n = 4 216 886) | 82,5 % [82,4 ; 82,5] | 24,7 % [24,6 ; 24,9] |
| bureau | A6a | 20,1 [20,0 ; 20,2] | 33,0 % [32,7 ; 33,2] | 60,7 % [60,6 ; 60,9] | 93,98 % [93,96 ; 94,01] (n = 4 216 886) | 83,0 % [83,0 ; 83,1] | 26,3 % [26,1 ; 26,4] |
| bureau | A6b | 18,7 [18,6 ; 18,8] | 34,6 % [34,3 ; 34,9] | 61,9 % [61,8 ; 62,1] | 93,98 % [93,96 ; 94,01] (n = 4 216 886) | 83,0 % [83,0 ; 83,1] | 26,3 % [26,1 ; 26,4] |
| bureau | A7 | 41,3 [41,1 ; 41,5] | 52,4 % [52,2 ; 52,6] | 75,7 % [75,6 ; 75,9] | 94,00 % [93,97 ; 94,02] (n = 4 216 886) | 83,1 % [83,0 ; 83,1] | 26,3 % [26,1 ; 26,5] |
| bureau | A8 | 19,5 [19,4 ; 19,6] | 68,3 % [68,0 ; 68,6] | 88,1 % [87,9 ; 88,2] | 98,00 % [97,98 ; 98,01] (n = 4 216 886) | 94,1 % [94,1 ; 94,2] | 68,3 % [68,1 ; 68,5] |
| bureau | A2-calibre | 14,2 [14,1 ; 14,3] | 68,4 % [68,1 ; 68,8] | 88,1 % [88,0 ; 88,3] | 98,00 % [97,98 ; 98,01] (n = 4 216 886) | 94,1 % [94,1 ; 94,2] | 68,3 % [68,1 ; 68,5] |
| bureau | A2-abusif | 14,2 [14,1 ; 14,4] | 68,0 % [67,6 ; 68,3] | 87,9 % [87,8 ; 88,1] | 98,00 % [97,98 ; 98,01] (n = 4 216 886) | 94,1 % [94,1 ; 94,2] | 68,3 % [68,1 ; 68,5] |
| bureau | A4-calibre | 18,7 [18,7 ; 18,7] | 0,1 % [0,1 ; 0,1] | 10,0 % [9,8 ; 10,1] | 84,98 % [84,95 ; 85,02] (n = 4 216 886) | 61,4 % [61,3 ; 61,4] | 0,1 % [0,1 ; 0,1] |
| bureau | A4-abusif | 18,7 [18,7 ; 18,7] | 0,1 % [0,1 ; 0,1] | 10,0 % [9,9 ; 10,2] | 84,98 % [84,95 ; 85,02] (n = 4 216 886) | 61,4 % [61,3 ; 61,4] | 0,1 % [0,1 ; 0,1] |
| service client | A1 | 6,9 [6,9 ; 7,0] | 91,2 % [90,9 ; 91,5] | 97,0 % [96,9 ; 97,1] | 99,50 % [99,49 ; 99,50] (n = 6 442 498) | 98,5 % [98,5 ; 98,5] | 91,3 % [91,2 ; 91,4] |
| service client | A2 | 32,2 [32,0 ; 32,4] | 68,2 % [68,0 ; 68,5] | 88,0 % [87,9 ; 88,1] | 98,00 % [97,99 ; 98,01] (n = 6 442 498) | 94,1 % [94,1 ; 94,1] | 68,2 % [68,0 ; 68,4] |
| service client | A3 | 39,1 [39,0 ; 39,2] | 34,5 % [34,3 ; 34,7] | 70,1 % [70,0 ; 70,3] | 95,00 % [94,98 ; 95,01] (n = 6 442 498) | 85,7 % [85,7 ; 85,8] | 34,3 % [34,2 ; 34,5] |
| service client | A4 | 28,1 [28,1 ; 28,1] | 0,1 % [0,1 ; 0,1] | 10,0 % [9,9 ; 10,1] | 85,00 % [84,97 ; 85,03] (n = 6 442 498) | 61,4 % [61,3 ; 61,5] | 0,1 % [0,1 ; 0,1] |
| service client | A5 | 31,2 [31,1 ; 31,4] | 52,0 % [51,8 ; 52,2] | 69,4 % [69,3 ; 69,6] | 94,55 % [94,53 ; 94,57] (n = 6 442 498) | 84,5 % [84,5 ; 84,6] | 30,5 % [30,4 ; 30,7] |
| service client | A6a | 30,8 [30,7 ; 30,9] | 35,7 % [35,5 ; 35,9] | 62,8 % [62,6 ; 62,9] | 93,99 % [93,97 ; 94,01] (n = 6 442 498) | 83,0 % [83,0 ; 83,1] | 26,2 % [26,1 ; 26,3] |
| service client | A6b | 29,6 [29,4 ; 29,7] | 36,8 % [36,6 ; 37,0] | 63,6 % [63,5 ; 63,7] | 93,99 % [93,97 ; 94,01] (n = 6 442 498) | 83,0 % [83,0 ; 83,1] | 26,2 % [26,1 ; 26,3] |
| service client | A7 | 59,9 [59,7 ; 60,2] | 52,2 % [52,0 ; 52,4] | 75,6 % [75,5 ; 75,7] | 94,00 % [93,99 ; 94,02] (n = 6 442 498) | 83,1 % [83,0 ; 83,1] | 26,2 % [26,1 ; 26,4] |
| service client | A8 | 32,4 [32,2 ; 32,5] | 68,1 % [67,8 ; 68,3] | 88,0 % [87,9 ; 88,0] | 98,00 % [97,99 ; 98,01] (n = 6 442 498) | 94,1 % [94,1 ; 94,1] | 68,2 % [68,0 ; 68,4] |
| service client | A2-calibre | 23,5 [23,3 ; 23,6] | 68,2 % [67,9 ; 68,4] | 88,0 % [87,9 ; 88,1] | 98,00 % [97,99 ; 98,01] (n = 6 442 498) | 94,1 % [94,1 ; 94,1] | 68,2 % [68,0 ; 68,4] |
| service client | A2-abusif | 23,3 [23,1 ; 23,4] | 68,3 % [68,0 ; 68,5] | 88,0 % [87,9 ; 88,1] | 98,00 % [97,99 ; 98,01] (n = 6 442 498) | 94,1 % [94,1 ; 94,1] | 68,2 % [68,0 ; 68,4] |
| service client | A4-calibre | 27,8 [27,8 ; 27,9] | 0,1 % [0,1 ; 0,1] | 10,0 % [9,9 ; 10,1] | 85,00 % [84,97 ; 85,03] (n = 6 442 498) | 61,4 % [61,3 ; 61,5] | 0,1 % [0,1 ; 0,1] |
| service client | A4-abusif | 27,8 [27,8 ; 27,9] | 0,1 % [0,1 ; 0,1] | 10,0 % [9,9 ; 10,1] | 85,00 % [84,97 ; 85,03] (n = 6 442 498) | 61,4 % [61,3 ; 61,5] | 0,1 % [0,1 ; 0,1] |

## v1 contre v2

Mêmes agents, mêmes tirages, mêmes graines ; seule la règle change (amendement A1). v1 : `resultats_v1/` (première passe, archivée, non modifiée). v2 : ce dossier. Les intervalles sont ceux de chaque passe ; les deux passes portent sur les mêmes répétitions (5 000 au réglage de départ α = 5 %, 1 000 ailleurs).

### Extinction de l'autonomie

Part des actions d'une fenêtre de 100 exécutées sans validation préalable (palier 2 ou 3), règle au réglage de départ, 5 000 répétitions (`fig6_v1_v2_autonomie.png`).

| mélange | agent | v1 : au plus haut | v1 : 100 dernières actions | v2 : au plus haut | v2 : 100 dernières actions |
|--|--|--|--|--|--|
| bureau | A1 | 78,6 % [78,1 ; 79,0] (actions 800-899) | 41,2 % [40,7 ; 41,7] | 86,6 % [86,4 ; 86,8] (actions 2 300-2 399) | 86,4 % [86,2 ; 86,6] |
| bureau | A2 | 56,6 % [56,4 ; 56,9] (actions 100-199) | 4,1 % [4,0 ; 4,3] | 73,3 % [73,1 ; 73,5] (actions 800-899) | 70,6 % [70,4 ; 70,8] |
| bureau | A3 | 38,0 % [37,5 ; 38,5] (actions 100-199) | 0,0 % [0,0 ; 0,0] | 64,1 % [63,9 ; 64,2] (actions 800-899) | 63,8 % [63,6 ; 64,0] |
| bureau | A4 | 6,6 % [6,3 ; 6,8] (actions 0-99) | 0,0 % [0,0 ; 0,0] | 27,0 % [26,6 ; 27,5] (actions 2 000-2 099) | 26,7 % [26,2 ; 27,1] |
| bureau | A7 | 15,1 % [14,8 ; 15,4] (actions 0-99) | 0,4 % [0,3 ; 0,4] | 66,2 % [66,1 ; 66,3] (actions 2 900-2 999) | 66,2 % [66,1 ; 66,3] |
| service client | A1 | 72,7 % [72,2 ; 73,1] (actions 800-899) | 30,8 % [30,3 ; 31,3] | 77,5 % [77,2 ; 77,8] (actions 1 500-1 599) | 77,0 % [76,6 ; 77,3] |
| service client | A2 | 44,4 % [44,0 ; 44,9] (actions 200-299) | 6,1 % [6,0 ; 6,2] | 54,7 % [54,4 ; 55,0] (actions 800-899) | 51,9 % [51,7 ; 52,1] |
| service client | A3 | 28,3 % [27,9 ; 28,8] (actions 100-199) | 0,8 % [0,8 ; 0,9] | 46,7 % [46,6 ; 46,9] (actions 2 300-2 399) | 46,6 % [46,4 ; 46,7] |
| service client | A4 | 5,7 % [5,5 ; 6,0] (actions 0-99) | 0,0 % [0,0 ; 0,0] | 20,4 % [20,0 ; 20,8] (actions 2 200-2 299) | 19,8 % [19,4 ; 20,2] |
| service client | A7 | 12,5 % [12,2 ; 12,8] (actions 0-99) | 0,8 % [0,7 ; 0,8] | 48,2 % [48,0 ; 48,3] (actions 2 900-2 999) | 48,2 % [48,0 ; 48,3] |

### Charge

| réglage | mélange | agent | v1 : charge ; hors lectures | v2 : charge ; hors lectures |
|--|--|--|--|--|
| stricte α=5 % (n = 1 000) | bureau | A1 | 55,1 [54,4 ; 55,9] ; 53,8 [53,3 ; 54,4] | 28,2 [28,0 ; 28,4] ; 49,5 [49,1 ; 49,9] |
| stricte α=5 % (n = 1 000) | bureau | A2 | 90,1 [89,8 ; 90,4] ; 89,4 [88,9 ; 89,8] | 39,6 [39,4 ; 39,8] ; 68,5 [68,2 ; 68,8] |
| stricte α=5 % (n = 1 000) | service client | A1 | 63,1 [62,4 ; 63,9] ; 71,3 [70,5 ; 72,0] | 41,3 [41,0 ; 41,7] ; 67,2 [66,6 ; 67,8] |
| stricte α=5 % (n = 1 000) | service client | A2 | 94,3 [94,1 ; 94,6] ; 97,5 [97,3 ; 97,8] | 59,0 [58,8 ; 59,1] ; 95,2 [95,0 ; 95,5] |
| stricte α=20 % (n = 1 000) | bureau | A1 | 54,5 [53,7 ; 55,2] ; 52,8 [52,2 ; 53,3] | 27,6 [27,4 ; 27,8] ; 48,4 [48,0 ; 48,8] |
| stricte α=20 % (n = 1 000) | bureau | A2 | 89,7 [89,4 ; 90,0] ; 88,8 [88,3 ; 89,3] | 39,1 [38,9 ; 39,3] ; 67,9 [67,5 ; 68,2] |
| stricte α=20 % (n = 1 000) | service client | A1 | 62,3 [61,5 ; 63,0] ; 69,9 [69,2 ; 70,6] | 40,4 [40,0 ; 40,8] ; 65,7 [65,1 ; 66,4] |
| stricte α=20 % (n = 1 000) | service client | A2 | 94,0 [93,7 ; 94,2] ; 97,1 [96,8 ; 97,3] | 58,5 [58,4 ; 58,7] ; 94,7 [94,4 ; 94,9] |
| départ α=5 % (n = 5 000) | bureau | A1 | 39,8 [39,5 ; 40,1] ; 38,2 [38,0 ; 38,4] | 19,6 [19,5 ; 19,7] ; 34,9 [34,7 ; 35,1] |
| départ α=5 % (n = 5 000) | bureau | A2 | 82,0 [81,8 ; 82,1] ; 79,0 [78,7 ; 79,2] | 32,6 [32,5 ; 32,7] ; 58,2 [58,0 ; 58,3] |
| départ α=5 % (n = 5 000) | service client | A1 | 48,4 [48,0 ; 48,8] ; 56,6 [56,2 ; 56,9] | 28,9 [28,8 ; 29,1] ; 47,5 [47,2 ; 47,7] |
| départ α=5 % (n = 5 000) | service client | A2 | 88,0 [87,9 ; 88,2] ; 90,8 [90,6 ; 90,9] | 51,9 [51,8 ; 52,0] ; 85,5 [85,3 ; 85,7] |
| départ α=20 % (n = 1 000) | bureau | A1 | 39,5 [38,7 ; 40,2] ; 37,4 [36,9 ; 37,9] | 19,2 [19,0 ; 19,4] ; 34,1 [33,7 ; 34,5] |
| départ α=20 % (n = 1 000) | bureau | A2 | 81,7 [81,3 ; 82,1] ; 78,6 [78,0 ; 79,2] | 32,3 [32,1 ; 32,5] ; 57,7 [57,3 ; 58,0] |
| départ α=20 % (n = 1 000) | service client | A1 | 47,2 [46,4 ; 48,0] ; 55,0 [54,2 ; 55,8] | 28,1 [27,8 ; 28,4] ; 46,1 [45,5 ; 46,6] |
| départ α=20 % (n = 1 000) | service client | A2 | 87,6 [87,3 ; 88,0] ; 90,3 [90,0 ; 90,7] | 51,4 [51,1 ; 51,6] ; 84,7 [84,3 ; 85,1] |
| souple α=5 % (n = 1 000) | bureau | A1 | 36,2 [35,4 ; 36,9] ; 31,8 [31,3 ; 32,3] | 15,5 [15,3 ; 15,7] ; 27,7 [27,3 ; 28,0] |
| souple α=5 % (n = 1 000) | bureau | A2 | 79,3 [78,9 ; 79,7] ; 74,6 [74,0 ; 75,2] | 29,1 [28,8 ; 29,3] ; 52,3 [51,9 ; 52,7] |
| souple α=5 % (n = 1 000) | service client | A1 | 43,5 [42,7 ; 44,3] ; 49,0 [48,2 ; 49,8] | 22,8 [22,5 ; 23,1] ; 37,6 [37,1 ; 38,0] |
| souple α=5 % (n = 1 000) | service client | A2 | 85,6 [85,3 ; 86,0] ; 87,3 [87,0 ; 87,7] | 47,2 [46,9 ; 47,5] ; 78,2 [77,7 ; 78,7] |
| souple α=20 % (n = 1 000) | bureau | A1 | 35,8 [35,1 ; 36,6] ; 31,1 [30,6 ; 31,6] | 15,0 [14,9 ; 15,2] ; 26,9 [26,6 ; 27,2] |
| souple α=20 % (n = 1 000) | bureau | A2 | 79,1 [78,6 ; 79,5] ; 74,1 [73,5 ; 74,7] | 28,7 [28,5 ; 29,0] ; 51,7 [51,3 ; 52,1] |
| souple α=20 % (n = 1 000) | service client | A1 | 43,1 [42,3 ; 43,9] ; 48,4 [47,6 ; 49,2] | 22,3 [22,0 ; 22,5] ; 36,7 [36,2 ; 37,1] |
| souple α=20 % (n = 1 000) | service client | A2 | 85,4 [85,1 ; 85,7] ; 86,9 [86,5 ; 87,3] | 46,7 [46,4 ; 47,0] ; 77,3 [76,8 ; 77,8] |
| départ α=5 % (n = 5 000) | bureau | A3 | 97,0 [96,9 ; 97,1] ; 98,4 [98,3 ; 98,5] | 40,8 [40,8 ; 40,9] ; 70,7 [70,6 ; 70,8] |
| départ α=5 % (n = 5 000) | bureau | A4 | 101,4 [101,4 ; 101,4] ; 103,0 [103,0 ; 103,0] | 79,8 [79,6 ; 79,9] ; 93,5 [93,4 ; 93,6] |
| départ α=5 % (n = 5 000) | bureau | A7 | 102,5 [102,5 ; 102,6] ; 105,8 [105,7 ; 105,9] | 50,9 [50,8 ; 51,0] ; 80,4 [80,4 ; 80,5] |
| départ α=5 % (n = 5 000) | service client | A3 | 98,6 [98,5 ; 98,7] ; 101,3 [101,2 ; 101,3] | 59,4 [59,4 ; 59,5] ; 96,1 [96,0 ; 96,1] |
| départ α=5 % (n = 5 000) | service client | A4 | 102,3 [102,3 ; 102,3] ; 104,2 [104,2 ; 104,3] | 86,3 [86,2 ; 86,5] ; 102,0 [102,0 ; 102,1] |
| départ α=5 % (n = 5 000) | service client | A7 | 104,4 [104,3 ; 104,4] ; 108,4 [108,4 ; 108,5] | 67,8 [67,8 ; 67,9] ; 103,0 [102,9 ; 103,1] |

### Dégâts

Écart apparié avec « tout faire valider », pour 100 actions, réglage de départ α = 5 %.

| mélange | agent | niveau | v1 | v2 |
|--|--|--|--|--|
| bureau | A1 | faible | 0,134 [0,133 ; 0,135] | 0,305 [0,302 ; 0,308] |
| bureau | A1 | moyen | 0,045 [0,044 ; 0,046] | 0,048 [0,047 ; 0,049] |
| bureau | A1 | fort | 0,022 [0,022 ; 0,023] | 0,023 [0,023 ; 0,024] |
| bureau | A2 | faible | 0,153 [0,152 ; 0,155] | 1,185 [1,180 ; 1,190] |
| bureau | A2 | moyen | 0,053 [0,052 ; 0,054] | 0,067 [0,066 ; 0,068] |
| bureau | A2 | fort | 0,020 [0,019 ; 0,020] | 0,021 [0,020 ; 0,022] |
| bureau | A3 | faible | 0,100 [0,099 ; 0,102] | 2,542 [2,536 ; 2,549] |
| bureau | A3 | moyen | 0,032 [0,031 ; 0,033] | 0,033 [0,032 ; 0,033] |
| bureau | A3 | fort | 0,019 [0,019 ; 0,020] | 0,019 [0,019 ; 0,020] |
| bureau | A4 | faible | 0,012 [0,012 ; 0,013] | 0,084 [0,080 ; 0,087] |
| bureau | A4 | moyen | 0,046 [0,045 ; 0,047] | 0,046 [0,045 ; 0,047] |
| bureau | A4 | fort | 0,039 [0,038 ; 0,040] | 0,039 [0,038 ; 0,040] |
| bureau | A7 | faible | 0,038 [0,037 ; 0,039] | 1,353 [1,342 ; 1,363] |
| bureau | A7 | moyen | 0,030 [0,029 ; 0,031] | 0,030 [0,029 ; 0,031] |
| bureau | A7 | fort | 0,023 [0,023 ; 0,024] | 0,023 [0,023 ; 0,024] |
| service client | A1 | faible | 0,093 [0,092 ; 0,094] | 0,218 [0,216 ; 0,220] |
| service client | A1 | moyen | 0,048 [0,047 ; 0,049] | 0,070 [0,069 ; 0,071] |
| service client | A1 | fort | 0,046 [0,045 ; 0,047] | 0,050 [0,049 ; 0,050] |
| service client | A2 | faible | 0,128 [0,127 ; 0,129] | 0,847 [0,843 ; 0,852] |
| service client | A2 | moyen | 0,040 [0,040 ; 0,041] | 0,077 [0,075 ; 0,078] |
| service client | A2 | fort | 0,030 [0,029 ; 0,031] | 0,035 [0,034 ; 0,035] |
| service client | A3 | faible | 0,099 [0,097 ; 0,100] | 1,810 [1,804 ; 1,815] |
| service client | A3 | moyen | 0,038 [0,037 ; 0,039] | 0,039 [0,038 ; 0,040] |
| service client | A3 | fort | 0,032 [0,031 ; 0,033] | 0,032 [0,031 ; 0,033] |
| service client | A4 | faible | 0,013 [0,013 ; 0,014] | 0,067 [0,064 ; 0,070] |
| service client | A4 | moyen | 0,061 [0,060 ; 0,063] | 0,061 [0,060 ; 0,063] |
| service client | A4 | fort | 0,065 [0,063 ; 0,066] | 0,065 [0,063 ; 0,066] |
| service client | A7 | faible | 0,037 [0,036 ; 0,038] | 0,951 [0,942 ; 0,960] |
| service client | A7 | moyen | 0,036 [0,035 ; 0,037] | 0,036 [0,035 ; 0,037] |
| service client | A7 | fort | 0,037 [0,036 ; 0,038] | 0,037 [0,036 ; 0,038] |

### Garantie

| réglage | v1 : pire couple stable ; doute ; non stable | v2 : pire couple stable ; doute ; non stable |
|--|--|--|
| stricte α=5 % | A3 EXE 2,5 % [1,7 ; 3,7] (passe) ; A4-calibre MSG 2,5 % [1,7 ; 3,7] (passe) ; A6b MSG 26,0 % [23,4 ; 28,8] (échoue) | A3 DUR 2,6 % [1,8 ; 3,8] (passe) ; A4-calibre MSG 3,0 % [2,1 ; 4,3] (passe) ; A6b ECR 46,3 % [43,2 ; 49,4] (échoue) |
| stricte α=20 % | A3 EXE 3,0 % [2,1 ; 4,3] (passe) ; A4-calibre MSG 3,0 % [2,1 ; 4,3] (passe) ; A6b MSG 25,0 % [22,4 ; 27,8] (échoue) | A3 EXE 3,2 % [2,3 ; 4,5] (passe) ; A4-calibre ECR 3,6 % [2,6 ; 4,9] (passe) ; A6b ECR 46,3 % [43,2 ; 49,4] (échoue) |
| départ α=5 % | A3 SOR 2,8 % [2,4 ; 3,3] (passe) ; A4-calibre EXE 1,7 % [1,4 ; 2,1] (passe) ; A6b EXE 23,3 % [22,1 ; 24,5] (échoue) | A3 SOR 2,9 % [2,5 ; 3,4] (passe) ; A4-calibre EXE 1,7 % [1,4 ; 2,1] (passe) ; A6b EXE 23,3 % [22,1 ; 24,5] (échoue) |
| départ α=20 % | A3 SOR 3,8 % [2,8 ; 5,2] (indécis) ; A4-calibre DUR 2,5 % [1,7 ; 3,7] (passe) ; A6b EXE 22,9 % [20,4 ; 25,6] (échoue) | A3 SOR 3,9 % [2,9 ; 5,3] (indécis) ; A4-calibre DUR 2,5 % [1,7 ; 3,7] (passe) ; A6b EXE 23,0 % [20,5 ; 25,7] (échoue) |
| souple α=5 % | A4 EXE 2,8 % [1,9 ; 4,0] (passe) ; A4-calibre DUR 6,8 % [5,4 ; 8,5] (échoue) ; A6b ARG 4,3 % [3,2 ; 5,7] (indécis) | A4 EXE 2,8 % [1,9 ; 4,0] (passe) ; A4-calibre DUR 6,8 % [5,4 ; 8,5] (échoue) ; A6b ARG 4,1 % [3,0 ; 5,5] (indécis) |
| souple α=20 % | A4 EXE 4,2 % [3,1 ; 5,6] (indécis) ; A4-calibre EXE 9,5 % [7,8 ; 11,5] (échoue) ; A6b ARG 2,4 % [1,6 ; 3,5] (passe) | A4 EXE 4,2 % [3,1 ; 5,6] (indécis) ; A4-calibre EXE 9,5 % [7,8 ; 11,5] (échoue) ; A6b ARG 3,6 % [2,6 ; 4,9] (passe) |

Agents à taux constant exactement au pm (courbe de garantie, bureau, 1 000 répétitions par point) :

| réglage | type | v1 | v2 |
|--|--|--|--|
| stricte α=5 % | LEC | 2,7 % [1,9 ; 3,9] | 4,2 % [3,1 ; 5,6] |
| stricte α=5 % | ECR | 2,9 % [2,0 ; 4,1] | 5,2 % [4,0 ; 6,8] |
| stricte α=5 % | DUR | 2,5 % [1,7 ; 3,7] | 2,5 % [1,7 ; 3,7] |
| stricte α=5 % | EXE | 2,6 % [1,8 ; 3,8] | 2,6 % [1,8 ; 3,8] |
| stricte α=5 % | MSG | 3,4 % [2,4 ; 4,7] | 4,5 % [3,4 ; 6,0] |
| stricte α=20 % | LEC | 3,5 % [2,5 ; 4,8] | 5,5 % [4,2 ; 7,1] |
| stricte α=20 % | ECR | 4,0 % [3,0 ; 5,4] | 6,2 % [4,9 ; 7,9] |
| stricte α=20 % | DUR | 2,6 % [1,8 ; 3,8] | 2,6 % [1,8 ; 3,8] |
| stricte α=20 % | EXE | 3,1 % [2,2 ; 4,4] | 3,1 % [2,2 ; 4,4] |
| stricte α=20 % | MSG | 4,3 % [3,2 ; 5,7] | 5,5 % [4,2 ; 7,1] |
| départ α=5 % | LEC | 2,7 % [1,9 ; 3,9] | 4,3 % [3,2 ; 5,7] |
| départ α=5 % | ECR | 2,9 % [2,0 ; 4,1] | 4,0 % [3,0 ; 5,4] |
| départ α=5 % | DUR | 2,3 % [1,5 ; 3,4] | 2,3 % [1,5 ; 3,4] |
| départ α=5 % | EXE | 2,8 % [1,9 ; 4,0] | 2,8 % [1,9 ; 4,0] |
| départ α=5 % | MSG | 3,5 % [2,5 ; 4,8] | 4,7 % [3,6 ; 6,2] |
| départ α=5 % | SOR | 2,9 % [2,0 ; 4,1] | 2,9 % [2,0 ; 4,1] |
| départ α=5 % | ARG | 1,4 % [0,8 ; 2,3] | 1,4 % [0,8 ; 2,3] |
| départ α=20 % | LEC | 3,2 % [2,3 ; 4,5] | 4,7 % [3,6 ; 6,2] |
| départ α=20 % | ECR | 3,6 % [2,6 ; 4,9] | 5,2 % [4,0 ; 6,8] |
| départ α=20 % | DUR | 2,8 % [1,9 ; 4,0] | 2,8 % [1,9 ; 4,0] |
| départ α=20 % | EXE | 3,1 % [2,2 ; 4,4] | 3,1 % [2,2 ; 4,4] |
| départ α=20 % | MSG | 4,0 % [3,0 ; 5,4] | 5,6 % [4,3 ; 7,2] |
| départ α=20 % | SOR | 3,2 % [2,3 ; 4,5] | 3,2 % [2,3 ; 4,5] |
| départ α=20 % | ARG | 2,3 % [1,5 ; 3,4] | 2,3 % [1,5 ; 3,4] |
| souple α=5 % | LEC | 3,4 % [2,4 ; 4,7] | 4,1 % [3,0 ; 5,5] |
| souple α=5 % | ECR | 2,6 % [1,8 ; 3,8] | 4,3 % [3,2 ; 5,7] |
| souple α=5 % | DUR | 1,9 % [1,2 ; 2,9] | 1,9 % [1,2 ; 2,9] |
| souple α=5 % | EXE | 2,8 % [1,9 ; 4,0] | 2,8 % [1,9 ; 4,0] |
| souple α=5 % | MSG | 3,3 % [2,4 ; 4,6] | 4,7 % [3,6 ; 6,2] |
| souple α=5 % | SOR | 3,2 % [2,3 ; 4,5] | 3,3 % [2,4 ; 4,6] |
| souple α=5 % | ARG | 3,4 % [2,4 ; 4,7] | 3,4 % [2,4 ; 4,7] |
| souple α=20 % | LEC | 5,1 % [3,9 ; 6,6] | 6,6 % [5,2 ; 8,3] |
| souple α=20 % | ECR | 4,0 % [3,0 ; 5,4] | 5,8 % [4,5 ; 7,4] |
| souple α=20 % | DUR | 2,2 % [1,5 ; 3,3] | 2,2 % [1,5 ; 3,3] |
| souple α=20 % | EXE | 4,2 % [3,1 ; 5,6] | 4,2 % [3,1 ; 5,6] |
| souple α=20 % | MSG | 4,9 % [3,7 ; 6,4] | 6,4 % [5,0 ; 8,1] |
| souple α=20 % | SOR | 3,6 % [2,6 ; 4,9] | 3,6 % [2,6 ; 4,9] |
| souple α=20 % | ARG | 3,7 % [2,7 ; 5,1] | 3,7 % [2,7 ; 5,1] |

### Réactivité

A6b (dérive silencieuse), tous les types promus à t = 1 500 : 95e centile du délai et part non retirée.

| réglage | mélange | v1 : 95e centile ; non retiré | v2 : 95e centile ; non retiré |
|--|--|--|--|
| stricte α=5 % | bureau | 523 [495 ; 570] ; 0,0 % [0,0 ; 0,4] | 670 [630 ; 706] ; 0,2 % [0,1 ; 0,4] |
| stricte α=5 % | service client | 1 262 [1 183 ; 1 343] ; 2,1 % [1,4 ; 3,0] | 1 456 [1 371 ; 1 500] ; 4,8 % [4,1 ; 5,8] |
| stricte α=20 % | bureau | 521 [491 ; 557] ; 0,0 % [0,0 ; 0,4] | 672 [641 ; 717] ; 0,2 % [0,1 ; 0,4] |
| stricte α=20 % | service client | 1 270 [1 208 ; 1 352] ; 2,1 % [1,5 ; 3,0] | 1 492 [1 408 ; 1 500] ; 5,0 % [4,2 ; 5,9] |
| départ α=5 % | bureau | 495 [476 ; 508] ; 0,0 % [0,0 ; 0,1] | 997 [977 ; 1 016] ; 1,4 % [1,2 ; 1,6] |
| départ α=5 % | service client | 1 414 [1 387 ; 1 441] ; 4,0 % [3,7 ; 4,4] | 1 500 [1 500 ; 1 500] ; 13,1 % [12,7 ; 13,6] |
| départ α=20 % | bureau | 496 [460 ; 530] ; 0,0 % [0,0 ; 0,3] | 994 [934 ; 1 043] ; 1,1 % [0,8 ; 1,5] |
| départ α=20 % | service client | 1 422 [1 372 ; 1 492] ; 4,1 % [3,4 ; 4,9] | 1 500 [1 500 ; 1 500] ; 13,3 % [12,3 ; 14,4] |
| souple α=5 % | bureau | 525 [501 ; 560] ; 0,0 % [0,0 ; 0,2] | 1 458 [1 394 ; 1 500] ; 4,6 % [4,1 ; 5,3] |
| souple α=5 % | service client | 1 420 [1 368 ; 1 481] ; 4,0 % [3,4 ; 4,9] | 1 500 [1 500 ; 1 500] ; 21,2 % [20,0 ; 22,5] |
| souple α=20 % | bureau | 538 [503 ; 567] ; 0,0 % [0,0 ; 0,2] | 1 452 [1 375 ; 1 500] ; 4,6 % [4,0 ; 5,3] |
| souple α=20 % | service client | 1 421 [1 367 ; 1 484] ; 4,1 % [3,4 ; 4,9] | 1 500 [1 500 ; 1 500] ; 20,9 % [19,7 ; 22,2] |

### Contre les concurrents simples

| réglage | v1 : contre liste fixe ; tri ; hasard | v2 : contre liste fixe ; tri ; hasard |
|--|--|--|
| stricte α=5 % | compromis 26 ; compromis 26 ; compromis 4, perd 21, égalité 1 | compromis 26 ; compromis 26 ; compromis 6, perd 20 |
| stricte α=20 % | compromis 26 ; compromis 26 ; compromis 5, perd 20, égalité 1 | compromis 26 ; compromis 26 ; compromis 6, perd 20 |
| départ α=5 % | compromis 26 ; compromis 26 ; compromis 5, perd 21 | compromis 26 ; compromis 26 ; compromis 6, perd 20 |
| départ α=20 % | compromis 26 ; compromis 26 ; compromis 5, perd 19, égalité 2 | compromis 26 ; compromis 26 ; compromis 6, perd 20 |
| souple α=5 % | compromis 26 ; compromis 26 ; compromis 7, perd 17, égalité 2 | compromis 26 ; compromis 26 ; compromis 6, perd 20 |
| souple α=20 % | compromis 26 ; compromis 26 ; compromis 6, perd 18, égalité 2 | compromis 26 ; compromis 26 ; compromis 6, perd 20 |

## Ce qui surprend

Chaque point sépare ce qui est **mesuré** de ce qui est **interprété**.

**1. L'extinction a disparu.**  
Mesuré : en bureau, A2 culmine à 73,3 % [73,1 ; 73,5] et finit à 70,6 % [70,4 ; 70,8] (v1 : 56,6 % [56,4 ; 56,9] puis 4,1 % [4,0 ; 4,3]) ; A1 culmine à 86,6 % [86,4 ; 86,8] et finit à 86,4 % [86,2 ; 86,6].  
Interprété : avec le score réfléchi, une erreur isolée est absorbée et le processus devient stationnaire ; l'horizon ne décide plus du verdict de charge.

**2. La réactivité se paie : la dérive silencieuse est retirée plus lentement.**  
Mesuré : A6b, bureau, tous les types promus : 95e centile 997 actions, 1,4 % non retirés à l'horizon (v1 : 495 et 0,0 %). Sur les seuls types devenus mauvais (DUR EXE SOR ARG) : 95e centile 381, 0,0 % non retirés.  
Interprété : sur un type à enjeu faible, un agent à 10 % reste sous le pm de départ (20 %) ; la dérive moyenne de son score par action vérifiée vaut −0,016, négative, donc il reste promu, comme la règle le veut. Le lent retrait mesuré « tous types » est surtout celui-là. Sur les types à enjeu moyen ou fort, la première erreur suffit toujours.

**3. Au pm exact, la garantie à enjeu faible s'effrite.**  
Mesuré : au réglage strict, A6b après la dérive (10 % = pm sur les types à enjeu faible) est promu de nouveau au palier 3 sur ECR (bureau) dans 46,3 % [43,2 ; 49,4] des répétitions (n = 1 000). Sur la courbe de garantie, la promotion au pm des types à enjeu faible monte d'environ 3 % (v1) à environ 4 à 6 % (v2) ; voir « v1 contre v2 ».  
Interprété : le seuil de Wald protège un test ; le score réfléchi refait le test après chaque descente. Au pm exact, la dérive du score reste faible devant ses pas : 0,067 par action vérifiée au réglage strict, quand une réussite retire 0,080 et une erreur ajoute 1,386 ; sur un horizon long, l'agent finit par aligner les réussites qu'il faut. La garantie de 5 % ne tient plus « à vie » pour un agent au bord du seuil ; elle tient pour les agents nettement mauvais.

**4. Le palier du milieu ouvre la porte aux agents moyens à mauvais sur les types à enjeu faible.**  
Mesuré : A4 (15 %) exécute 26,7 % [26,2 ; 27,1] de ses actions sans validation préalable en fin d'horizon (bureau) ; sa charge passe de 101,4 [101,4 ; 101,4] (v1) à 79,8 [79,6 ; 79,9].  
Interprété : le palier 2 des types à enjeu faible se mérite sous pm = 30 % ; à 15 %, la dérive du score L2 vaut −0,049 par action, négative. La garantie ne porte que sur le palier 3 : rien, dans la pièce 1, ne borne le palier 2 d'un agent mauvais. Les erreurs y sont corrigées après coup (95 % ici), ce qui limite les dégâts mais pas la charge de correction.

**5. Le hasard fait toujours aussi bien pour un agent stable ; la règle gagne sur l'agent qui change.**  
Mesuré : A2, bureau, règle moins hasard : dégâts faibles 0,000 [−0,002 ; 0,002], charge 1,95 [1,86 ; 2,04] (le coût des épreuves). A7 (amélioration annoncée) : dégâts faibles −0,833 [−0,848 ; −0,818] ; A7 retrouve 66,2 % [66,1 ; 66,3] d'actions sans validation en fin d'horizon (v1 : 0,4 % [0,3 ; 0,4]).  
Interprété : dans ce monde aux erreurs indépendantes, le moment des promotions ne vaut quelque chose que si l'agent change ; la correction de la pièce 8 (erreurs faibles effacées au changement de modèle) rend enfin justice à l'agent qui progresse.

**6. Face à la liste fixe, le compromis a changé de sens.**  
Mesuré : A1, bureau, règle moins liste fixe : charge −20,4 [−20,5 ; −20,3], dégâts faibles 0,019 [0,018 ; 0,020], moyens 0,048 [0,047 ; 0,049], forts 0,023 [0,023 ; 0,024].  
Interprété : en v1, la règle faisait moins de dégâts faibles pour plus de charge ; en v2, elle demande beaucoup moins de validations pour un bon agent, mais elle lui donne l'autonomie à enjeu moyen et fort, que la liste fixe ne donne jamais. Le critère « pas pire à aucun niveau » interdit ce troc tant que la marge à ces niveaux est nulle.

## Limites

- **Monde idéal, par construction.** Erreurs indépendantes, taux constant dans chaque phase, contrôle automatique parfait sur les actions vérifiables, validateur qui rate 5 % des erreurs au hasard.
- **Même taux sur tous les types** (sauf A5) : la règle ne peut presque rien gagner à répartir l'autonomie entre les types d'un même agent.
- **Un seul horizon (3 000 actions).** En v2 l'autonomie est stationnaire, mais l'effritement de la garantie au pm (surprise 3) grandit avec l'horizon.
- **Une seule dérive** (2 % à 10 % à t = 1 500) : sur les types à enjeu faible, elle reste sous le pm de départ ; la réactivité sur ces types n'est pas une exigence de la règle.
- **Variantes d'épreuve comptées comme de vraies tâches** (charge et dégâts) : choix prudent, isolé dans `charge_epreuve` et `degats_epreuve`.
- **« Bon » et « mauvais » sont des définitions de travail** (q au plus pb, q au moins pm) ; la garantie ne porte que sur le palier 3.
- **Dégâts pour 100 actions du flux entier**, pas pour 100 actions du niveau.
- **Statistiques** : normale (moyennes), Wilson (proportions), delta (rapports), rééchantillonnage (centiles) ; aucune correction pour comparaisons multiples. La grille de marges est lue à 95 % par couple ; avec 26 couples, un « indécis » isolé peut être du bruit.
- **Réglages autres que celui de départ à 1 000 répétitions** : intervalles environ deux fois plus larges.
- **Ce n'est pas l'expérience de confirmation** ; aucun agent réel, aucune donnée réelle.

## Choix d'implémentation

Points où le plan laisse un choix ; à chaque fois, l'option la plus simple et la plus prudente.

1. **« Sous ln B » lu « au plus ln B »** (tolérance 1e−9) : une erreur au plancher ramène le score exactement à ln B, et la règle ne doit pas descendre pour une seule erreur (test des 2 erreurs rapprochées).
2. **Score réfléchi (A1)** : un score par type et par palier visé, L3 (pb ; pm du palier 3) et L2 (palier 2, types réversibles), chacun avec son plancher ln B − a. Plus de plafond sur r. Le palier visé est le plus haut dont le score est au plus ln B.
3. **Mise à jour du palier.** Une réussite ne peut que faire monter. Le palier ne descend que sur une erreur (un cran pour l'enjeu faible, palier 1 pour l'enjeu moyen ou fort) ou sur un changement de configuration (recalcul complet). L'action est exécutée au palier d'avant sa propre preuve.
4. **Épreuves** (inchangées) : une par erreur à enjeu moyen ou fort, passées une à une à l'arrivée de la prochaine action du type ; après un échec, nouvel essai après 50 actions du type ; une nouvelle erreur ne remet pas ce délai à zéro, un changement de modèle si. Une épreuve ratée n'ajoute pas d'erreur. Tant qu'une épreuve est ouverte, les réussites ne font pas baisser le score. s compte les erreurs à enjeu moyen ou fort de la configuration : au changement de modèle, elles deviennent autant d'épreuves, et chaque épreuve réussie en efface une.
5. **Variantes d'épreuve** : 3 cas difficiles (taux min(0,9 ; 6q) du moment), en plus des 3 000 actions, au palier 1 : elles comptent dans la charge et dans les dégâts, pas dans le dénominateur. Le doute s'y applique (variante en doute neutre et remplacée ; comptée ratée sans doute gratuit).
6. **Changement de modèle (A1)** : L2 = L3 = 0 sur tous les types ; erreurs à enjeu faible effacées ; erreurs à enjeu moyen ou fort en épreuves.
7. **Consigne modifiée (A1)** : sur le type, chaque score négatif est divisé par deux ; palier recalculé.
8. **Plafonnés** : trois sources (plafonds absolus 1 %, 20 % de SOR, 20 % d'ARG) ; taux d'erreur de la source ; enjeu fort pour les dégâts ; toujours au palier 1, sauf sous « tout approuver ».
9. **Doute** : une validation (charge), aucune preuve. Doute calibré : une action difficile sur deux, indépendamment de l'issue ; abusif : 30 % de toutes les actions.
10. **Invérifiable** : 5 % des actions, au hasard. **Validateur** : un même nombre aléatoire par action pour toutes les règles et toutes les valeurs de e.
11. **Témoins** inchangés depuis la v1 : tout approuver (plafonnés compris, doutes ignorés) ; liste fixe et tri par le risque au palier 3 ; trois réussites (palier 3 après 3 réussites vérifiées d'affilée, palier 1 à la première erreur) ; oracle (palier 3 si le vrai q du moment est au plus pb) ; hasard (mêmes parts de palier 2 et 3 que la règle, type par type, en moyenne sur les répétitions, tirées action par action).
12. **Sans remise à zéro** : changements de configuration ignorés. **Sans pondération** : réglages de l'enjeu moyen partout. **Sans doute gratuit** : un doute compte comme une erreur. **Sans palier du milieu** : un seul score, celui du palier 3. **Sans épreuve** : après une erreur à enjeu moyen ou fort, le score reprend aussitôt ; au changement de modèle, L = 0 et plus rien d'autre.
13. **Les sensibilités de la v1** (erreurs faibles effacées, plancher glissant) n'ont plus d'objet : la première est devenue la règle, la seconde est le score réfléchi lui-même.
14. **Droits élargis** : codés (même traitement que le changement de modèle, sur un type) ; aucun scénario du plan ne les utilise.
15. **Version v1 gardée dans le code** (`version="v1"`, `executer.py --v1`) pour reproduire `resultats_v1/` ; le contrôle a été fait sur six cas, au chiffre près.
16. **Grille de marges (A1)** : 0 ; 0,005 ; 0,01 ; 0,02 ; 0,05 ; 0,1 ; 0,2 ; 0,5 ; 1 pour 100 actions. « Passe » à une marge : tout l'intervalle de l'écart avec « tout faire valider » est sous la marge.
17. **Agent mauvais** sur un type : q au moins pm du palier 3 de son niveau, au réglage considéré ; **bon** : q au plus pb. Couples comptés pour la garantie : agents stables (A3, A4, A5 et doutes d'A4), plus les phases mauvaises d'A6a (après la remise à zéro), d'A6b (après la dérive) et d'A7 (avant le changement).
18. **Verdicts** trivalués sur les intervalles à 95 % : passe, échoue, indécis.
19. **« Bat »** : écarts appariés ; meilleure sur au moins une mesure parmi la charge et les dégâts des trois niveaux, pire sur aucune.
20. **Utilité jugée sur A1 et A2** ; le critère de dégâts est aussi donné pour les 13 agents.
21. **Réactivité** : couples (répétition, type) au palier 2 ou 3 à t = 1 500 ; délai jusqu'au premier retour au palier 1 ; censure à l'horizon. Nouvelle ligne en v2 : les seuls types où le nouveau taux atteint pm.
22. **Répétitions** : 5 000 pour le réglage de départ α = 5 % et tous les témoins ; 1 000 pour les cinq autres réglages et les ablations. **Graines** : celles de la v1 (graine maîtresse 20261104), donc mêmes tirages.

## Fichiers

- `mesures.csv`, `comparaisons.csv`, `verdict.csv` ; `marges.csv` (verdict de dégâts à chaque marge de la grille, par réglage, mélange, agent et niveau) ; `marge_minimale.csv` (plus petite marge qui passe).
- `garantie.csv`, `garantie_courbe.csv`, `promotion.csv`, `reactivite.csv`, `epreuves.csv`, `autonomie_temps.csv`, `consigne.csv`, `meta.json`.
- Figures : `fig1_charge_degats_*.png`, `fig2_garantie_*.png`, `fig3_delai_promotion.png`, `fig4_reactivite.png`, `fig5_autonomie_temps.png`, `fig6_v1_v2_autonomie.png`.
- Reproduire (3 minutes environ, depuis `simulation/`) : `.venv/bin/python executer.py --verifier-tests && .venv/bin/python rapport.py && .venv/bin/python ecrire_resultats.py`. La première passe : `AM_DOSSIER=<autre dossier> .venv/bin/python executer.py --v1` (jamais dans `resultats_v1/`).
