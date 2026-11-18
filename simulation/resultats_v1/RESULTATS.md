# Simulation de niveau 1 · résultats (4 novembre 2026)

> Agents fictifs de fiabilité connue, aucun agent réel, aucune donnée réelle, aucun modèle d'IA, aucun appel réseau. Plan : `PLAN_SIMULATION.md` (fait foi). Règle : `../REGLE.md`. Code : `config.py`, `flux.py`, `regle.py`, `temoins.py`, `mesures.py`, `executer.py`, `rapport.py`, `ecrire_resultats.py` ; tests : `tests/`. Graine maîtresse 20261104. Durée de la grille : 176 s. Ce n'est pas l'expérience de confirmation.

## Résumé

1. **Tests** : 26 sur 26 passent ; les nombres des fiches tombent juste (35 ; 54 ; 2 erreurs ; 2,97 % et 4,89 % ; 0,358), à condition de lire « sous ln B » comme « au plus ln B ».
2. **Garantie** : tenue pour les agents mauvais stables à stricte α=5 %, stricte α=20 %, départ α=5 %, souple α=5 % (pire couple au départ α = 5 % : A3 SOR, 2,8 % [2,4 ; 3,3], n = 5 000), indécise à départ α=20 %, souple α=20 %. Elle cède en dérive silencieuse (A6b EXE, 23,3 % [22,1 ; 24,5]) et, au réglage souple, avec le doute calibré (A4 DUR, 6,8 % [5,4 ; 8,5]).
3. **Charge** : A1 passe au départ en bureau (39,8 [39,5 ; 40,1] pour 100 actions) mais pas en service client hors lectures (56,6 [56,2 ; 56,9]) ; A2 échoue à tous les réglages (79 à 94 pour 100, contre 50 exigé).
4. **Dégâts** : marges 0 et 0,1 intenables à enjeu faible pour A1 et A2 (excès de 0,08 à 0,17 pour 100 actions) ; marge 0,5 tenue pour les 13 agents à tous les réglages.
5. **Liste fixe et tri par le risque** : la règle ne les bat jamais. Dans 312 comparaisons sur 312 (6 réglages × 2 témoins × 26 couples agent-mélange), elle fait moins de dégâts faibles et plus de dégâts moyens et forts : un compromis, interdit de compensation par la pièce 2. Les deux témoins échouent eux aussi au critère de charge hors lectures.
6. **Hasard** : pour un agent stable, mêmes dégâts faibles que la règle et moins de charge (le coût des épreuves) : la règle perd. Elle ne gagne qu'en dérive (A6b, dégâts faibles −0,259 [−0,262 ; −0,255] pour 100 actions).
7. **Réactivité** (dérive silencieuse A6b) : retrait en 113 actions (médiane), 495 au 95e centile en bureau ; 1 414 en service client, où 4,0 % des types promus ne sont pas retirés avant l'horizon. Avec un changement déclaré (A6a), retrait immédiat.
8. **Ce qui surprend le plus** : la règle éteint l'autonomie de tous les agents avec le temps (A1 bureau : 78,6 % d'actions sans validation préalable au plus haut, 41,2 % en fin d'horizon ; A2 : 56,6 % puis 4,1 %). Cause : r plafonné et s jamais oublié, donc la 2e erreur d'un type ferme son palier 3 pour toute la configuration.
9. Autres surprises : α ne change presque rien ; un agent qui s'améliore (A7) n'est jamais récompensé, à cause d'une contradiction entre le plan et REGLE.md, pièce 8 ; au réglage strict, l'argent en bureau est presque hors d'atteinte ; le palier du milieu ne coûte aucun dégât.
10. **Verdict** : dans ce monde idéal, aucun réglage de la grille ne passe les trois épreuves ; l'utilité échoue partout. Interprétation, appuyée par un essai hors plan : le levier principal est le plancher (plancher glissant : charge d'A2 de 82 à 33 pour 100 en bureau), pas les réglages (pb ; pm).

## Comment lire les chiffres

- **Dénominateurs** : une répétition = un agent sur 3 000 actions. 5 000 répétitions pour le réglage de départ α = 5 % et pour tous les témoins ; 1 000 pour les autres réglages, les ablations et les sensibilités. Charge et dégâts : pour 100 actions du flux (3 000 par répétition). Proportions (garantie, « jamais promu ») : sur les répétitions.
- **Intervalles à 95 %** entre crochets, toujours. Moyennes : approximation normale ; proportions : Wilson ; écarts : appariés (mêmes tirages pour toutes les règles).
- **Validateur à 5 %** partout, sauf dans la section qui fait varier e.
- Les nombres viennent des fichiers CSV de ce dossier ; ce fichier est écrit par `ecrire_resultats.py`, sans recopie à la main.

## Contrôles du code (tests de la section 8)

Lancés avant toute production de résultats : `.venv/bin/python -m pytest tests/` → **26 tests, 26 passés** (`executer.py --verifier-tests` refuse de produire des résultats sinon).

| contrôle | attendu (fiche de lecture) | obtenu |
|--|--|--|
| réussites pour monter depuis zéro (pb 2 %, pm 10 %, α = β = 5 %) | 35 | 35 (formule et règle complète, type DUR) |
| réussites de plus avec une erreur dans le compteur | 54 | 54 (compteur seul, et règle complète après épreuve réussie) |
| erreurs rapprochées qui font descendre depuis le plancher | 2 | 2 (la 1re ramène le score exactement à ln B) |
| risque réel de rejeter à tort, p = 2 %, test sans borne | 2,97 % | calcul exact 2,97 % ; Monte-Carlo 2,94 % [2,89 ; 2,99], n = 400 000 |
| risque réel d'accepter à tort, p = 10 % | 4,89 % | calcul exact 4,89 % ; Monte-Carlo 4,84 % [4,77 ; 4,90], n = 400 000 |
| taille moyenne d'échantillon (p = 2 % ; 10 %) | 54,6 ; 38,3 | 54,58 ; 38,30 |
| enchaîner 20 réussites à 5 % d'erreur | 0,95^20 = 0,358 | tirage du moteur : 0,360 [0,353 ; 0,367], n = 20 000 |
| erreur à enjeu moyen ou fort | palier 1, r = 0, s + 1, épreuve | vérifié (version de référence et moteur, 4 types) |
| actions plafonnées | jamais autonomes | vérifié pour la règle, ses 5 variantes et tous les témoins sauf « tout approuver » |
| doute | ne change ni r ni s | vérifié (un agent qui doute de tout reste à r = s = 0 ; doute abusif : r et s ne comptent que les actions jugées) |
| remises à zéro | ne touchent s que par une épreuve réussie après changement | vérifié (consigne, changement de modèle, épreuves réussies et ratées) |
| cohérence | le moteur vectorisé = la version de référence | identique action par action sur 9 agents × 12 variantes × 4 répétitions |

Les nombres de référence tombent juste. Deux d'entre eux (54 réussites, 2 erreurs depuis le plancher) ne tombent juste que si « sous ln B » se lit **« au plus ln B »** : avec le plancher du plan, une erreur ramène le score *exactement* à ln B, et 54 réussites après une erreur l'y ramènent aussi. Avec une inégalité stricte, une seule erreur ferait descendre, et un type qui a une erreur ne pourrait plus jamais monter. L'erreur ne vient donc ni du code ni de la référence : la règle est sur le fil, et la lecture « au plus » est la seule compatible avec les deux nombres. Elle est retenue (choix 1).

## Ce que la règle exige, calcul exact

Calculé à partir des réglages, sans simulation. « Erreurs tolérées » : nombre d'erreurs que le type peut porter dans une même configuration en restant à ce palier, une fois r au plafond. Comme s n'est jamais oublié et que r est plafonné, **une erreur de plus ferme ce palier jusqu'au prochain changement de configuration**.

| réglage | ln B | enjeu | palier 3 : réussites depuis zéro | palier 3 : erreurs tolérées | palier 2 : réussites depuis zéro | palier 2 : erreurs tolérées |
|--|--|--|--|--|--|--|
| stricte α=5 % | −2,944 | faible | 37 | 1 | 27 | 2 |
| stricte α=5 % | −2,944 | moyen | 72 | 1 | 37 | 4 |
| stricte α=5 % | −2,944 | fort | 146 | 1 | sans objet | sans objet |
| stricte α=20 % | −2,773 | faible | 35 | 1 | 25 | 2 |
| stricte α=20 % | −2,773 | moyen | 68 | 1 | 35 | 4 |
| stricte α=20 % | −2,773 | fort | 137 | 1 | sans objet | sans objet |
| départ α=5 % | −2,944 | faible | 18 | 1 | 12 | 3 |
| départ α=5 % | −2,944 | moyen | 35 | 1 | 18 | 4 |
| départ α=5 % | −2,944 | fort | 72 | 1 | sans objet | sans objet |
| départ α=20 % | −2,773 | faible | 17 | 1 | 12 | 3 |
| départ α=20 % | −2,773 | moyen | 33 | 1 | 17 | 4 |
| départ α=20 % | −2,773 | fort | 68 | 1 | sans objet | sans objet |
| souple α=5 % | −2,944 | faible | 11 | 1 | 7 | 3 |
| souple α=5 % | −2,944 | moyen | 23 | 1 | 11 | 4 |
| souple α=5 % | −2,944 | fort | 47 | 1 | sans objet | sans objet |
| souple α=20 % | −2,773 | faible | 10 | 1 | 7 | 3 |
| souple α=20 % | −2,773 | moyen | 21 | 1 | 10 | 4 |
| souple α=20 % | −2,773 | fort | 45 | 1 | sans objet | sans objet |

Actions vérifiables par type sur l'horizon (3 000 actions × part du type × 95 %) :

| mélange | LEC | ECR | DUR | EXE | MSG | SOR | ARG |
|--|--|--|--|--|--|--|--|
| bureau | 1 282 | 428 | 228 | 228 | 171 | 274 | 114 |
| service client | 1 140 | 142 | 570 | 57 | 86 | 342 | 319 |

Deux conséquences se lisent directement. (1) Au palier 3, la deuxième erreur d'un type est définitive dans la configuration, quel que soit le nombre de réussites autour. (2) Au réglage strict, ARG en « bureau » demande 146 réussites vérifiées d'affilée (α = 5 % ; 137 à α = 20 %) pour 114 actions vérifiables en moyenne sur tout l'horizon : il n'est promu que dans les rares répétitions où l'argent est inhabituellement fréquent.

## Verdict de la pièce 1, réglage par réglage (validateur à 5 %)

Trois verdicts possibles pour chaque critère : **passe** (tout l'intervalle à 95 % est du bon côté du seuil), **échoue** (tout l'intervalle est du mauvais côté), **indécis** (l'intervalle chevauche le seuil). Réglage de départ α = 5 % : 5 000 répétitions ; les cinq autres réglages : 1 000 répétitions (les 1 000 premières des mêmes tirages).

### Synthèse

| réglage | 1. garantie : agents stables | 1. garantie : doute (A4) | 1. garantie : dérive et changements | 2. charge ≤ 50 (A1 et A2, en tout et hors lectures) | 2. dégâts ≤ tout valider + 0 / + 0,1 / + 0,5 (A1, A2) | 2. bat la liste fixe | 2. bat le tri par le risque | 3. réactivité A6b : 95e centile du délai (bureau ; service client) |
|--|--|--|--|--|--|--|--|--|
| stricte α=5 % | passe | passe | échoue | échoue | échoue / échoue / passe | non (compromis) | non (compromis) | 523 (non retiré : 0,0 %) ; 1 262 (non retiré : 2,1 %) |
| stricte α=20 % | passe | passe | échoue | échoue | échoue / échoue / passe | non (compromis) | non (compromis) | 521 (non retiré : 0,0 %) ; 1 270 (non retiré : 2,1 %) |
| départ α=5 % | passe | passe | échoue | échoue | échoue / échoue / passe | non (compromis) | non (compromis) | 495 (non retiré : 0,0 %) ; 1 414 (non retiré : 4,0 %) |
| départ α=20 % | indécis | passe | échoue | échoue | échoue / échoue / passe | non (compromis) | non (compromis) | 496 (non retiré : 0,0 %) ; 1 422 (non retiré : 4,1 %) |
| souple α=5 % | passe | échoue | indécis | échoue | échoue / échoue / passe | non (compromis) | non (compromis) | 525 (non retiré : 0,0 %) ; 1 420 (non retiré : 4,0 %) |
| souple α=20 % | indécis | échoue | passe | échoue | échoue / échoue / passe | non (compromis) | non (compromis) | 538 (non retiré : 0,0 %) ; 1 421 (non retiré : 4,1 %) |

Lecture : **aucun réglage ne passe les trois épreuves.** Garantie pour les agents mauvais stables : passe à stricte α=5 %, stricte α=20 %, départ α=5 %, souple α=5 % ; indécise à départ α=20 %, souple α=20 %. Avec le doute calibré d'A4 : échoue à souple α=5 %, souple α=20 %. En dérive silencieuse ou autour d'un changement : échoue à stricte α=5 %, stricte α=20 %, départ α=5 %, départ α=20 % ; au réglage souple, les types à enjeu moyen ne comptent plus A6b comme mauvais (pm = 15 %), d'où un pire couple plus bas. L'utilité échoue à stricte α=5 %, stricte α=20 %, départ α=5 %, départ α=20 %, souple α=5 %, souple α=20 % : la charge d'A2 reste au-dessus de la moitié, la marge 0,1 est dépassée à enjeu faible, et la règle ne bat jamais la liste fixe ni le tri par le risque. La réactivité ne se juge pas encore : K n'est pas fixé ; la colonne donne le K qu'il faudrait pour la tenir 95 fois sur 100.

### 1. Garantie

Agent « mauvais » sur un type : son vrai taux d'erreur est au moins le pm du palier 3 de ce niveau d'enjeu, au réglage considéré (choix 21). Mesure : part des répétitions où ce type atteint le palier 3 avant l'horizon. Le verdict porte sur le **pire couple** (agent, type), le plus prudent ; la part groupée est donnée aussi. Avec une cinquantaine de couples, le pire couple est un peu biaisé vers le haut.

| réglage | couples mauvais (stables / doute / non stables) | part groupée, tous couples | pire couple, agents stables (A3, A4, A5) | pire couple, doute (A4 calibré ou abusif) | pire couple, phases non stables (A6a après, A6b après, A7 avant) |
|--|--|--|--|--|--|
| stricte α=5 % | 24 / 28 / 42 | 0,80 % [0,75 ; 0,86] | A3 sur EXE (bureau) : 2,5 % [1,7 ; 3,7], n = 1 000 → **passe** | A4-calibre sur MSG (service client) : 2,5 % [1,7 ; 3,7], n = 1 000 → **passe** | A6b sur MSG (service client, après t = 1 500) : 26,0 % [23,4 ; 28,8], n = 1 000 → **échoue** |
| stricte α=20 % | 24 / 28 / 42 | 0,91 % [0,85 ; 0,98] | A3 sur EXE (bureau) : 3,0 % [2,1 ; 4,3], n = 1 000 → **passe** | A4-calibre sur MSG (service client) : 3,0 % [2,1 ; 4,3], n = 1 000 → **passe** | A6b sur MSG (service client, après t = 1 500) : 25,0 % [22,4 ; 27,8], n = 1 000 → **échoue** |
| départ α=5 % | 14 / 16 / 24 | 1,18 % [1,14 ; 1,22] | A3 sur SOR (service client) : 2,8 % [2,4 ; 3,3], n = 5 000 → **passe** | A4-calibre sur EXE (bureau) : 1,7 % [1,4 ; 2,1], n = 5 000 → **passe** | A6b sur EXE (service client, après t = 1 500) : 23,3 % [22,1 ; 24,5], n = 5 000 → **échoue** |
| départ α=20 % | 14 / 16 / 24 | 1,32 % [1,23 ; 1,42] | A3 sur SOR (service client) : 3,8 % [2,8 ; 5,2], n = 1 000 → **indécis** | A4-calibre sur DUR (service client) : 2,5 % [1,7 ; 3,7], n = 1 000 → **passe** | A6b sur EXE (service client, après t = 1 500) : 22,9 % [20,4 ; 25,6], n = 1 000 → **échoue** |
| souple α=5 % | 10 / 16 / 12 | 1,51 % [1,40 ; 1,64] | A4 sur EXE (bureau) : 2,8 % [1,9 ; 4,0], n = 1 000 → **passe** | A4-calibre sur DUR (service client) : 6,8 % [5,4 ; 8,5], n = 1 000 → **échoue** | A6b sur ARG (bureau, après t = 1 500) : 4,3 % [3,2 ; 5,7], n = 1 000 → **indécis** |
| souple α=20 % | 10 / 16 / 12 | 1,87 % [1,73 ; 2,01] | A4 sur EXE (bureau) : 4,2 % [3,1 ; 5,6], n = 1 000 → **indécis** | A4-calibre sur EXE (bureau) : 9,5 % [7,8 ; 11,5], n = 1 000 → **échoue** | A6b sur ARG (bureau, après t = 1 500) : 2,4 % [1,6 ; 3,5], n = 1 000 → **passe** |

La courbe complète (part promue selon le vrai taux q, type par type) est dans `fig2_garantie_bureau.png` et `fig2_garantie_service_client.png` (agents à taux constant, 1 000 répétitions par point, `garantie_courbe.csv`).

### 2. Utilité

**Charge** pour 100 actions (validations, corrections, doutes, et variantes d'épreuve), en tout et hors lectures. « Tout faire valider » vaut 100 dans les deux cas. Seuil : 50.

| réglage | A1 bureau : tout ; hors lectures | A1 service client | A2 bureau | A2 service client |
|--|--|--|--|--|
| stricte α=5 % (n = 1 000) | 55,1 [54,4 ; 55,9] échoue ; 53,8 [53,3 ; 54,4] échoue | 63,1 [62,4 ; 63,9] échoue ; 71,3 [70,5 ; 72,0] échoue | 90,1 [89,8 ; 90,4] échoue ; 89,4 [88,9 ; 89,8] échoue | 94,3 [94,1 ; 94,6] échoue ; 97,5 [97,3 ; 97,8] échoue |
| stricte α=20 % (n = 1 000) | 54,5 [53,7 ; 55,2] échoue ; 52,8 [52,2 ; 53,3] échoue | 62,3 [61,5 ; 63,0] échoue ; 69,9 [69,2 ; 70,6] échoue | 89,7 [89,4 ; 90,0] échoue ; 88,8 [88,3 ; 89,3] échoue | 94,0 [93,7 ; 94,2] échoue ; 97,1 [96,8 ; 97,3] échoue |
| départ α=5 % (n = 5 000) | 39,8 [39,5 ; 40,1] passe ; 38,2 [38,0 ; 38,4] passe | 48,4 [48,0 ; 48,8] passe ; 56,6 [56,2 ; 56,9] échoue | 82,0 [81,8 ; 82,1] échoue ; 79,0 [78,7 ; 79,2] échoue | 88,0 [87,9 ; 88,2] échoue ; 90,8 [90,6 ; 90,9] échoue |
| départ α=20 % (n = 1 000) | 39,5 [38,7 ; 40,2] passe ; 37,4 [36,9 ; 37,9] passe | 47,2 [46,4 ; 48,0] passe ; 55,0 [54,2 ; 55,8] échoue | 81,7 [81,3 ; 82,1] échoue ; 78,6 [78,0 ; 79,2] échoue | 87,6 [87,3 ; 88,0] échoue ; 90,3 [90,0 ; 90,7] échoue |
| souple α=5 % (n = 1 000) | 36,2 [35,4 ; 36,9] passe ; 31,8 [31,3 ; 32,3] passe | 43,5 [42,7 ; 44,3] passe ; 49,0 [48,2 ; 49,8] passe | 79,3 [78,9 ; 79,7] échoue ; 74,6 [74,0 ; 75,2] échoue | 85,6 [85,3 ; 86,0] échoue ; 87,3 [87,0 ; 87,7] échoue |
| souple α=20 % (n = 1 000) | 35,8 [35,1 ; 36,6] passe ; 31,1 [30,6 ; 31,6] passe | 43,1 [42,3 ; 43,9] passe ; 48,4 [47,6 ; 49,2] passe | 79,1 [78,6 ; 79,5] échoue ; 74,1 [73,5 ; 74,7] échoue | 85,4 [85,1 ; 85,7] échoue ; 86,9 [86,5 ; 87,3] échoue |

Pour comparer : la liste fixe coûte 40,0 [40,0 ; 40,0] en tout et 72,7 [72,7 ; 72,8] hors lectures (bureau), le tri par le risque 34,0 [34,0 ; 34,0] et 61,8 [61,8 ; 61,8] : **les deux témoins simples échouent aussi au critère hors lectures**, ce que le plan voulait justement rendre visible.

**Dégâts** : écart apparié avec « tout faire valider », pour 100 actions du flux, par niveau d'enjeu. Verdict sur A1 et A2, puis sur les 13 agents (deux mélanges chaque fois).

| réglage | A1 et A2 : marge 0 / 0,1 / 0,5 | plus grand écart chez A1 et A2 | 13 agents : marge 0 / 0,1 / 0,5 | plus grand écart, 13 agents |
|--|--|--|--|--|
| stricte α=5 % (n = 1 000) | échoue / échoue / passe | A1, enjeu faible (bureau) : 0,122 [0,120 ; 0,125] | échoue / échoue / passe | A4-calibre, enjeu fort (service client) : 0,125 [0,121 ; 0,129] |
| stricte α=20 % (n = 1 000) | échoue / échoue / passe | A1, enjeu faible (bureau) : 0,123 [0,121 ; 0,126] | échoue / échoue / passe | A2-calibre, enjeu faible (bureau) : 0,127 [0,124 ; 0,130] |
| départ α=5 % (n = 5 000) | échoue / échoue / passe | A2, enjeu faible (bureau) : 0,153 [0,152 ; 0,155] | échoue / échoue / passe | A6b, enjeu faible (bureau) : 0,159 [0,158 ; 0,160] |
| départ α=20 % (n = 1 000) | échoue / échoue / passe | A2, enjeu faible (bureau) : 0,155 [0,152 ; 0,157] | échoue / échoue / passe | A6b, enjeu faible (bureau) : 0,161 [0,158 ; 0,163] |
| souple α=5 % (n = 1 000) | échoue / échoue / passe | A2, enjeu faible (bureau) : 0,168 [0,165 ; 0,170] | échoue / échoue / passe | A6b, enjeu faible (service client) : 0,175 [0,172 ; 0,177] |
| souple α=20 % (n = 1 000) | échoue / échoue / passe | A2, enjeu faible (bureau) : 0,170 [0,167 ; 0,172] | échoue / échoue / passe | A6b, enjeu faible (service client) : 0,177 [0,175 ; 0,180] |

Une marge nulle est intenable pour toute règle qui accorde de l'autonomie : sous « tout faire valider », 95 % des erreurs sont arrêtées ; une action autonome fausse part toujours. La marge 0,5 tient pour tous les agents et tous les réglages.

**Bat-elle les concurrents simples ?** Critère (choix 23) : sur les mêmes tirages, meilleure sur au moins une mesure parmi la charge et les dégâts des trois niveaux (intervalle de l'écart tout sous 0), pire sur aucune (aucun intervalle tout au-dessus de 0). Comptes sur les 26 couples agent × mélange.

| réglage | contre la liste fixe | contre le tri par le risque | contre le hasard |
|--|--|--|--|
| stricte α=5 % | compromis 26 | compromis 26 | compromis 4, perd 21, égalité 1 |
| stricte α=20 % | compromis 26 | compromis 26 | compromis 5, perd 20, égalité 1 |
| départ α=5 % | compromis 26 | compromis 26 | compromis 5, perd 21 |
| départ α=20 % | compromis 26 | compromis 26 | compromis 5, perd 19, égalité 2 |
| souple α=5 % | compromis 26 | compromis 26 | compromis 7, perd 17, égalité 2 |
| souple α=20 % | compromis 26 | compromis 26 | compromis 6, perd 18, égalité 2 |

« Compromis » : la règle est meilleure sur une mesure et pire sur une autre. Le détail est dans la section suivante et dans `comparaisons.csv`.

### 3. Réactivité

Couples (répétition, type) au palier 2 ou 3 à t = 1 500, au moment où le taux passe de 2 % à 10 %. Délai : actions de l'agent (tous types) jusqu'au retour au palier 1 ; un type non revenu à l'horizon compte pour 1 500 et figure dans « non retiré ». Dégâts : erreurs parties sur ce type pendant le délai (par couple promu). Intervalles des centiles par rééchantillonnage (400 tirages).

| réglage | agent | mélange | couples promus à t = 1 500 | délai médian | 95e centile | non retiré avant l'horizon | dégâts pendant le délai, par couple |
|--|--|--|--|--|--|--|--|
| stricte α=5 % | A6b | bureau | 1 037 (sur 1 000 × 7) | 115 [104 ; 124] | 523 [495 ; 570] | 0,0 % [0,0 ; 0,4] | 0,335 [0,300 ; 0,370] |
| stricte α=5 % | A6b | service client | 1 316 (sur 1 000 × 7) | 304 [289 ; 328] | 1 262 [1 183 ; 1 343] | 2,1 % [1,4 ; 3,0] | 0,772 [0,728 ; 0,816] |
| stricte α=20 % | A6b | bureau | 1 062 (sur 1 000 × 7) | 114 [104 ; 124] | 521 [491 ; 557] | 0,0 % [0,0 ; 0,4] | 0,330 [0,295 ; 0,364] |
| stricte α=20 % | A6b | service client | 1 398 (sur 1 000 × 7) | 314 [296 ; 339] | 1 270 [1 208 ; 1 352] | 2,1 % [1,5 ; 3,0] | 0,773 [0,731 ; 0,815] |
| départ α=5 % | A6b | bureau | 7 572 (sur 5 000 × 7) | 113 [110 ; 117] | 495 [476 ; 508] | 0,0 % [0,0 ; 0,1] | 0,236 [0,224 ; 0,247] |
| départ α=5 % | A6b | service client | 12 277 (sur 5 000 × 7) | 413 [404 ; 423] | 1 414 [1 387 ; 1 441] | 4,0 % [3,7 ; 4,4] | 0,582 [0,569 ; 0,596] |
| départ α=20 % | A6b | bureau | 1 517 (sur 1 000 × 7) | 110 [103 ; 119] | 496 [460 ; 530] | 0,0 % [0,0 ; 0,3] | 0,249 [0,223 ; 0,275] |
| départ α=20 % | A6b | service client | 2 476 (sur 1 000 × 7) | 418 [399 ; 440] | 1 422 [1 372 ; 1 492] | 4,1 % [3,4 ; 4,9] | 0,570 [0,541 ; 0,599] |
| souple α=5 % | A6b | bureau | 1 925 (sur 1 000 × 7) | 116 [107 ; 124] | 525 [501 ; 560] | 0,0 % [0,0 ; 0,2] | 0,205 [0,184 ; 0,226] |
| souple α=5 % | A6b | service client | 2 595 (sur 1 000 × 7) | 402 [390 ; 427] | 1 420 [1 368 ; 1 481] | 4,0 % [3,4 ; 4,9] | 0,551 [0,523 ; 0,580] |
| souple α=20 % | A6b | bureau | 1 923 (sur 1 000 × 7) | 117 [110 ; 124] | 538 [503 ; 567] | 0,0 % [0,0 ; 0,2] | 0,207 [0,186 ; 0,228] |
| souple α=20 % | A6b | service client | 2 598 (sur 1 000 × 7) | 402 [390 ; 427] | 1 421 [1 367 ; 1 484] | 4,1 % [3,4 ; 4,9] | 0,551 [0,522 ; 0,579] |
| tous les réglages | A6a | les deux | 7 510 au départ α = 5 %, bureau | 0 | 0 | 0,0 % | 0,000 |
| trois réussites | A6b | bureau | 32 964 | 72 [70 ; 73] | 444 [434 ; 451] | 0,0 % [0,0 ; 0,1] | 0,052 [0,049 ; 0,054] |
| trois réussites | A6b | service client | 32 974 | 75 [74 ; 77] | 777 [757 ; 790] | 1,0 % [0,9 ; 1,1] | 0,053 [0,051 ; 0,056] |
| trois réussites | A6a | bureau | 32 964 | 72 [70 ; 73] | 444 [434 ; 451] | 0,0 % [0,0 ; 0,1] | 0,052 [0,049 ; 0,054] |
| trois réussites | A6a | service client | 32 974 | 75 [74 ; 77] | 777 [757 ; 790] | 1,0 % [0,9 ; 1,1] | 0,053 [0,051 ; 0,056] |
| règle sans remise à zéro | A6b | bureau | 1 490 | 112 [104 ; 120] | 503 [469 ; 526] | 0,0 % [0,0 ; 0,3] | 0,250 [0,224 ; 0,276] |
| règle sans remise à zéro | A6b | service client | 2 475 | 418 [397 ; 441] | 1 422 [1 382 ; 1 484] | 4,1 % [3,4 ; 4,9] | 0,569 [0,540 ; 0,598] |
| règle sans remise à zéro | A6a | bureau | 1 483 | 109 [102 ; 117] | 495 [460 ; 530] | 0,0 % [0,0 ; 0,3] | 0,251 [0,224 ; 0,277] |
| règle sans remise à zéro | A6a | service client | 2 465 | 418 [399 ; 443] | 1 423 [1 377 ; 1 484] | 4,1 % [3,4 ; 5,0] | 0,571 [0,542 ; 0,601] |
| oracle | A6b | bureau | 25 000 | 0 [0 ; 0] | 0 [0 ; 0] | 0,0 % [0,0 ; 0,0] | 0,000 [0,000 ; 0,000] |
| oracle | A6b | service client | 25 000 | 0 [0 ; 0] | 0 [0 ; 0] | 0,0 % [0,0 ; 0,0] | 0,000 [0,000 ; 0,000] |
| oracle | A6a | bureau | 25 000 | 0 [0 ; 0] | 0 [0 ; 0] | 0,0 % [0,0 ; 0,0] | 0,000 [0,000 ; 0,000] |
| oracle | A6a | service client | 25 000 | 0 [0 ; 0] | 0 [0 ; 0] | 0,0 % [0,0 ; 0,0] | 0,000 [0,000 ; 0,000] |

A6a (changement de modèle déclaré) perd toute autonomie à l'instant même : la remise à zéro fait le travail. A6b (rien de déclaré) ne la perd qu'erreur après erreur ; le délai dépend surtout du volume du type (les types rares du mélange « service client », EXE à 2 % et MSG à 3 %, sont lents à trahir la dérive). Par type : `reactivite.csv` et `fig4_reactivite.png`.

**Consigne modifiée (A8).** À t = 1 500, r de SOR est divisé par deux. Parmi les répétitions où SOR était au palier 3 juste avant (réglage de départ, α = 5 %), comparées à A2 sur les mêmes tirages :

| mélange | agent | SOR au palier 3 à t = 1 500 | palier 3 perdu à la première sortie suivante | jamais revenu avant l'horizon | délai médian du retour |
|--|--|--|--|--|--|
| bureau | A8 | 414 sur 5 000 | 100,0 % [99,1 ; 100,0] | 33,6 % [29,2 ; 38,3] | 217 [206 ; 222] |
| bureau | A2 | 421 sur 5 000 | 0,0 % [0,0 ; 0,9] | sans objet | sans objet |
| service client | A8 | 290 sur 5 000 | 100,0 % [98,7 ; 100,0] | 43,8 % [38,2 ; 49,5] | 169 [160 ; 178] |
| service client | A2 | 303 sur 5 000 | 0,0 % [0,0 ; 1,3] | sans objet | sans objet |

Le calcul le prévoit : au plafond, diviser r par deux remonte le score au-dessus de ln B, et il faut 17 réussites de SOR pour y revenir (la fiche de Wald disait 17). La consigne modifiée retire donc toujours l'autonomie d'un type à enjeu fort déjà promu, puis la rend après quelques centaines d'actions, si aucune erreur ne survient entre-temps.

## Comparaison avec la liste fixe et le tri par le risque

Réglage de départ, α = 5 %, validateur à 5 %, 5 000 répétitions de 3 000 actions, mêmes tirages pour toutes les règles. Valeurs pour 100 actions, intervalle à 95 %.

### Valeurs absolues

| mélange | agent | règle | charge | charge hors lectures | dégâts faibles | dégâts moyens | dégâts forts |
|--|--|--|--|--|--|--|--|
| bureau | A1 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,017 [0,016 ; 0,017] | 0,004 [0,004 ; 0,005] | 0,004 [0,004 ; 0,005] |
| bureau | A1 | liste fixe | 40,0 [40,0 ; 40,0] | 72,7 [72,7 ; 72,8] | 0,303 [0,300 ; 0,306] | 0,004 [0,004 ; 0,005] | 0,004 [0,004 ; 0,005] |
| bureau | A1 | tri par le risque | 34,0 [34,0 ; 34,0] | 61,8 [61,8 ; 61,8] | 0,332 [0,329 ; 0,335] | 0,004 [0,004 ; 0,005] | 0,004 [0,004 ; 0,005] |
| bureau | A1 | **la règle** | 39,8 [39,5 ; 40,1] | 38,2 [38,0 ; 38,4] | 0,151 [0,150 ; 0,152] | 0,049 [0,048 ; 0,050] | 0,027 [0,026 ; 0,027] |
| bureau | A1 | hasard | 39,4 [39,3 ; 39,4] | 37,4 [37,3 ; 37,4] | 0,149 [0,147 ; 0,151] | 0,049 [0,048 ; 0,051] | 0,027 [0,026 ; 0,028] |
| bureau | A1 | oracle | 4,4 [4,4 ; 4,4] | 8,0 [8,0 ; 8,0] | 0,332 [0,329 ; 0,335] | 0,080 [0,079 ; 0,082] | 0,068 [0,067 ; 0,069] |
| bureau | A1 | trois réussites | 6,6 [6,5 ; 6,6] | 10,5 [10,5 ; 10,5] | 0,326 [0,323 ; 0,329] | 0,078 [0,077 ; 0,080] | 0,066 [0,065 ; 0,067] |
| bureau | A1 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 0,332 [0,329 ; 0,335] | 0,080 [0,079 ; 0,082] | 0,089 [0,087 ; 0,090] |
| bureau | A2 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,066 [0,065 ; 0,068] | 0,016 [0,015 ; 0,016] | 0,018 [0,017 ; 0,019] |
| bureau | A2 | liste fixe | 40,0 [40,0 ; 40,0] | 72,7 [72,7 ; 72,8] | 1,205 [1,200 ; 1,211] | 0,016 [0,015 ; 0,016] | 0,018 [0,017 ; 0,019] |
| bureau | A2 | tri par le risque | 34,0 [34,0 ; 34,0] | 61,8 [61,8 ; 61,8] | 1,319 [1,313 ; 1,325] | 0,016 [0,015 ; 0,016] | 0,018 [0,017 ; 0,019] |
| bureau | A2 | **la règle** | 82,0 [81,8 ; 82,1] | 79,0 [78,7 ; 79,2] | 0,220 [0,218 ; 0,221] | 0,069 [0,068 ; 0,070] | 0,038 [0,037 ; 0,039] |
| bureau | A2 | hasard | 80,0 [80,0 ; 80,0] | 75,5 [75,4 ; 75,5] | 0,222 [0,219 ; 0,224] | 0,062 [0,061 ; 0,063] | 0,032 [0,031 ; 0,033] |
| bureau | A2 | oracle | 18,0 [18,0 ; 18,0] | 32,7 [32,7 ; 32,8] | 1,319 [1,313 ; 1,325] | 0,320 [0,317 ; 0,323] | 0,018 [0,017 ; 0,019] |
| bureau | A2 | trois réussites | 10,7 [10,7 ; 10,7] | 14,5 [14,5 ; 14,5] | 1,240 [1,235 ; 1,246] | 0,298 [0,296 ; 0,301] | 0,258 [0,256 ; 0,261] |
| bureau | A2 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 1,319 [1,313 ; 1,325] | 0,320 [0,317 ; 0,323] | 0,361 [0,357 ; 0,364] |
| bureau | A4 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,493 [0,490 ; 0,497] | 0,121 [0,119 ; 0,122] | 0,136 [0,134 ; 0,137] |
| bureau | A4 | liste fixe | 40,0 [40,0 ; 40,0] | 72,7 [72,7 ; 72,8] | 9,048 [9,034 ; 9,063] | 0,121 [0,119 ; 0,122] | 0,136 [0,134 ; 0,137] |
| bureau | A4 | tri par le risque | 34,0 [34,0 ; 34,0] | 61,8 [61,8 ; 61,8] | 9,905 [9,890 ; 9,921] | 0,121 [0,119 ; 0,122] | 0,136 [0,134 ; 0,137] |
| bureau | A4 | **la règle** | 101,4 [101,4 ; 101,4] | 103,0 [103,0 ; 103,0] | 0,505 [0,502 ; 0,509] | 0,166 [0,164 ; 0,168] | 0,174 [0,172 ; 0,176] |
| bureau | A4 | hasard | 99,5 [99,5 ; 99,5] | 99,5 [99,5 ; 99,5] | 0,506 [0,502 ; 0,509] | 0,121 [0,119 ; 0,122] | 0,136 [0,134 ; 0,137] |
| bureau | A4 | oracle | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,493 [0,490 ; 0,497] | 0,121 [0,119 ; 0,122] | 0,136 [0,134 ; 0,137] |
| bureau | A4 | trois réussites | 41,8 [41,7 ; 41,8] | 44,2 [44,2 ; 44,3] | 6,241 [6,233 ; 6,249] | 1,501 [1,496 ; 1,505] | 1,306 [1,302 ; 1,310] |
| bureau | A4 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 9,905 [9,890 ; 9,921] | 2,399 [2,391 ; 2,407] | 2,705 [2,697 ; 2,713] |
| bureau | A5 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,066 [0,065 ; 0,068] | 0,016 [0,015 ; 0,016] | 0,096 [0,095 ; 0,098] |
| bureau | A5 | liste fixe | 40,0 [40,0 ; 40,0] | 72,7 [72,7 ; 72,8] | 1,205 [1,200 ; 1,211] | 0,016 [0,015 ; 0,016] | 0,096 [0,095 ; 0,098] |
| bureau | A5 | tri par le risque | 34,0 [34,0 ; 34,0] | 61,8 [61,8 ; 61,8] | 1,319 [1,313 ; 1,325] | 0,016 [0,015 ; 0,016] | 0,096 [0,095 ; 0,098] |
| bureau | A5 | **la règle** | 82,4 [82,2 ; 82,5] | 79,7 [79,5 ; 80,0] | 0,220 [0,218 ; 0,221] | 0,068 [0,067 ; 0,069] | 0,130 [0,128 ; 0,131] |
| bureau | A5 | hasard | 80,5 [80,4 ; 80,5] | 76,3 [76,2 ; 76,3] | 0,221 [0,218 ; 0,223] | 0,063 [0,062 ; 0,064] | 0,101 [0,100 ; 0,103] |
| bureau | A5 | oracle | 18,0 [18,0 ; 18,0] | 32,7 [32,7 ; 32,8] | 1,319 [1,313 ; 1,325] | 0,320 [0,317 ; 0,323] | 0,096 [0,095 ; 0,098] |
| bureau | A5 | trois réussites | 13,8 [13,8 ; 13,8] | 20,1 [20,1 ; 20,2] | 1,240 [1,235 ; 1,246] | 0,298 [0,296 ; 0,301] | 0,996 [0,992 ; 0,999] |
| bureau | A5 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 1,319 [1,313 ; 1,325] | 0,320 [0,317 ; 0,323] | 1,921 [1,914 ; 1,928] |
| service client | A1 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,012 [0,011 ; 0,013] | 0,005 [0,005 ; 0,006] | 0,008 [0,007 ; 0,008] |
| service client | A1 | liste fixe | 55,0 [55,0 ; 55,0] | 91,7 [91,7 ; 91,7] | 0,225 [0,223 ; 0,227] | 0,005 [0,005 ; 0,006] | 0,008 [0,007 ; 0,008] |
| service client | A1 | tri par le risque | 52,0 [52,0 ; 52,0] | 86,7 [86,7 ; 86,7] | 0,239 [0,237 ; 0,242] | 0,005 [0,005 ; 0,006] | 0,008 [0,007 ; 0,008] |
| service client | A1 | **la règle** | 48,4 [48,0 ; 48,8] | 56,6 [56,2 ; 56,9] | 0,105 [0,104 ; 0,106] | 0,054 [0,053 ; 0,054] | 0,053 [0,053 ; 0,054] |
| service client | A1 | hasard | 47,7 [47,7 ; 47,7] | 55,4 [55,4 ; 55,4] | 0,104 [0,103 ; 0,106] | 0,053 [0,052 ; 0,055] | 0,053 [0,051 ; 0,054] |
| service client | A1 | oracle | 6,8 [6,8 ; 6,8] | 11,3 [11,3 ; 11,3] | 0,239 [0,237 ; 0,242] | 0,110 [0,109 ; 0,112] | 0,118 [0,116 ; 0,120] |
| service client | A1 | trois réussites | 8,9 [8,9 ; 8,9] | 13,7 [13,7 ; 13,7] | 0,234 [0,232 ; 0,236] | 0,108 [0,106 ; 0,109] | 0,115 [0,114 ; 0,117] |
| service client | A1 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 0,239 [0,237 ; 0,242] | 0,110 [0,109 ; 0,112] | 0,151 [0,149 ; 0,153] |
| service client | A2 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,048 [0,047 ; 0,050] | 0,022 [0,021 ; 0,022] | 0,030 [0,029 ; 0,031] |
| service client | A2 | liste fixe | 55,0 [55,0 ; 55,0] | 91,7 [91,7 ; 91,7] | 0,901 [0,896 ; 0,905] | 0,022 [0,021 ; 0,022] | 0,030 [0,029 ; 0,031] |
| service client | A2 | tri par le risque | 52,0 [52,0 ; 52,0] | 86,7 [86,7 ; 86,7] | 0,957 [0,952 ; 0,962] | 0,022 [0,021 ; 0,022] | 0,030 [0,029 ; 0,031] |
| service client | A2 | **la règle** | 88,0 [87,9 ; 88,2] | 90,8 [90,6 ; 90,9] | 0,177 [0,175 ; 0,178] | 0,062 [0,061 ; 0,063] | 0,060 [0,059 ; 0,061] |
| service client | A2 | hasard | 84,8 [84,8 ; 84,8] | 85,4 [85,4 ; 85,4] | 0,175 [0,173 ; 0,177] | 0,052 [0,051 ; 0,053] | 0,050 [0,049 ; 0,051] |
| service client | A2 | oracle | 30,0 [30,0 ; 30,0] | 50,0 [50,0 ; 50,0] | 0,957 [0,952 ; 0,962] | 0,440 [0,437 ; 0,443] | 0,030 [0,029 ; 0,031] |
| service client | A2 | trois réussites | 13,0 [12,9 ; 13,0] | 17,5 [17,5 ; 17,6] | 0,899 [0,895 ; 0,904] | 0,412 [0,409 ; 0,415] | 0,442 [0,439 ; 0,445] |
| service client | A2 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 0,957 [0,952 ; 0,962] | 0,440 [0,437 ; 0,443] | 0,601 [0,597 ; 0,605] |
| service client | A4 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,361 [0,358 ; 0,364] | 0,165 [0,163 ; 0,167] | 0,224 [0,222 ; 0,226] |
| service client | A4 | liste fixe | 55,0 [55,0 ; 55,0] | 91,7 [91,7 ; 91,7] | 6,768 [6,756 ; 6,781] | 0,165 [0,163 ; 0,167] | 0,224 [0,222 ; 0,226] |
| service client | A4 | tri par le risque | 52,0 [52,0 ; 52,0] | 86,7 [86,7 ; 86,7] | 7,193 [7,180 ; 7,206] | 0,165 [0,163 ; 0,167] | 0,224 [0,222 ; 0,226] |
| service client | A4 | **la règle** | 102,3 [102,3 ; 102,3] | 104,2 [104,2 ; 104,3] | 0,374 [0,371 ; 0,378] | 0,226 [0,224 ; 0,229] | 0,289 [0,286 ; 0,292] |
| service client | A4 | hasard | 99,5 [99,5 ; 99,5] | 99,6 [99,6 ; 99,6] | 0,375 [0,372 ; 0,378] | 0,165 [0,163 ; 0,167] | 0,224 [0,222 ; 0,226] |
| service client | A4 | oracle | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,361 [0,358 ; 0,364] | 0,165 [0,163 ; 0,167] | 0,224 [0,222 ; 0,226] |
| service client | A4 | trois réussites | 43,2 [43,2 ; 43,3] | 46,2 [46,2 ; 46,3] | 4,529 [4,521 ; 4,536] | 2,074 [2,069 ; 2,079] | 2,239 [2,234 ; 2,244] |
| service client | A4 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 7,193 [7,180 ; 7,206] | 3,301 [3,292 ; 3,310] | 4,503 [4,493 ; 4,514] |
| service client | A5 | tout faire valider | 100,0 [100,0 ; 100,0] | 100,0 [100,0 ; 100,0] | 0,048 [0,047 ; 0,050] | 0,022 [0,021 ; 0,022] | 0,127 [0,125 ; 0,129] |
| service client | A5 | liste fixe | 55,0 [55,0 ; 55,0] | 91,7 [91,7 ; 91,7] | 0,901 [0,896 ; 0,905] | 0,022 [0,021 ; 0,022] | 0,127 [0,125 ; 0,129] |
| service client | A5 | tri par le risque | 52,0 [52,0 ; 52,0] | 86,7 [86,7 ; 86,7] | 0,957 [0,952 ; 0,962] | 0,022 [0,021 ; 0,022] | 0,127 [0,125 ; 0,129] |
| service client | A5 | **la règle** | 88,5 [88,3 ; 88,6] | 91,5 [91,4 ; 91,6] | 0,177 [0,175 ; 0,178] | 0,062 [0,061 ; 0,063] | 0,175 [0,173 ; 0,178] |
| service client | A5 | hasard | 85,3 [85,3 ; 85,3] | 86,3 [86,3 ; 86,3] | 0,176 [0,174 ; 0,178] | 0,052 [0,051 ; 0,054] | 0,137 [0,135 ; 0,139] |
| service client | A5 | oracle | 30,0 [30,0 ; 30,0] | 50,0 [50,0 ; 50,0] | 0,957 [0,952 ; 0,962] | 0,440 [0,437 ; 0,443] | 0,127 [0,125 ; 0,129] |
| service client | A5 | trois réussites | 16,9 [16,8 ; 16,9] | 24,0 [24,0 ; 24,1] | 0,899 [0,895 ; 0,904] | 0,412 [0,409 ; 0,415] | 1,368 [1,364 ; 1,372] |
| service client | A5 | tout approuver | 0,0 [0,0 ; 0,0] | 0,0 [0,0 ; 0,0] | 0,957 [0,952 ; 0,962] | 0,440 [0,437 ; 0,443] | 2,552 [2,544 ; 2,561] |

Les autres agents sont dans `mesures.csv` ; les figures `fig1_charge_degats_*.png` placent toutes les règles et tous les réglages dans le plan charge contre dégâts, niveau par niveau.

### Écarts appariés : la règle moins le témoin

Négatif = la règle fait mieux. Verdict selon le critère du choix 23.

| mélange | agent | contre | charge | dégâts faibles | dégâts moyens | dégâts forts | verdict |
|--|--|--|--|--|--|--|--|
| bureau | A1 | liste fixe | −0,2 [−0,5 ; 0,1] | −0,153 [−0,155 ; −0,150] | 0,045 [0,044 ; 0,046] | 0,022 [0,022 ; 0,023] | compromis |
| bureau | A1 | tri | 5,8 [5,5 ; 6,2] | −0,181 [−0,184 ; −0,179] | 0,045 [0,044 ; 0,046] | 0,022 [0,022 ; 0,023] | compromis |
| bureau | A2 | liste fixe | 42,0 [41,8 ; 42,1] | −0,986 [−0,991 ; −0,980] | 0,053 [0,052 ; 0,054] | 0,020 [0,019 ; 0,020] | compromis |
| bureau | A2 | tri | 48,0 [47,8 ; 48,2] | −1,100 [−1,106 ; −1,094] | 0,053 [0,052 ; 0,054] | 0,020 [0,019 ; 0,020] | compromis |
| bureau | A3 | liste fixe | 57,0 [56,9 ; 57,1] | −2,752 [−2,761 ; −2,743] | 0,032 [0,031 ; 0,033] | 0,019 [0,019 ; 0,020] | compromis |
| bureau | A3 | tri | 63,0 [62,9 ; 63,1] | −3,037 [−3,046 ; −3,027] | 0,032 [0,031 ; 0,033] | 0,019 [0,019 ; 0,020] | compromis |
| bureau | A4 | liste fixe | 61,4 [61,4 ; 61,4] | −8,543 [−8,557 ; −8,529] | 0,046 [0,045 ; 0,047] | 0,039 [0,038 ; 0,040] | compromis |
| bureau | A4 | tri | 67,4 [67,4 ; 67,5] | −9,400 [−9,415 ; −9,385] | 0,046 [0,045 ; 0,047] | 0,039 [0,038 ; 0,040] | compromis |
| bureau | A5 | liste fixe | 42,4 [42,2 ; 42,5] | −0,986 [−0,991 ; −0,980] | 0,052 [0,051 ; 0,053] | 0,033 [0,032 ; 0,034] | compromis |
| bureau | A5 | tri | 48,4 [48,2 ; 48,6] | −1,100 [−1,106 ; −1,094] | 0,052 [0,051 ; 0,053] | 0,033 [0,032 ; 0,034] | compromis |
| bureau | A6a | liste fixe | 45,9 [45,7 ; 46,0] | −3,284 [−3,293 ; −3,275] | 0,051 [0,050 ; 0,052] | 0,024 [0,024 ; 0,025] | compromis |
| bureau | A6a | tri | 51,9 [51,7 ; 52,0] | −3,627 [−3,637 ; −3,617] | 0,051 [0,050 ; 0,052] | 0,024 [0,024 ; 0,025] | compromis |
| bureau | A6b | liste fixe | 45,1 [44,9 ; 45,2] | −3,262 [−3,271 ; −3,252] | 0,064 [0,062 ; 0,065] | 0,028 [0,028 ; 0,029] | compromis |
| bureau | A6b | tri | 51,1 [50,9 ; 51,2] | −3,605 [−3,614 ; −3,595] | 0,064 [0,062 ; 0,065] | 0,028 [0,028 ; 0,029] | compromis |
| bureau | A7 | liste fixe | 62,5 [62,5 ; 62,6] | −3,386 [−3,395 ; −3,376] | 0,030 [0,029 ; 0,031] | 0,023 [0,023 ; 0,024] | compromis |
| bureau | A7 | tri | 68,5 [68,5 ; 68,6] | −3,729 [−3,739 ; −3,719] | 0,030 [0,029 ; 0,031] | 0,023 [0,023 ; 0,024] | compromis |
| bureau | A8 | liste fixe | 42,1 [41,9 ; 42,2] | −0,986 [−0,991 ; −0,980] | 0,053 [0,052 ; 0,054] | 0,017 [0,017 ; 0,018] | compromis |
| bureau | A8 | tri | 48,1 [47,9 ; 48,2] | −1,100 [−1,106 ; −1,094] | 0,053 [0,052 ; 0,054] | 0,017 [0,017 ; 0,018] | compromis |
| bureau | A2-calibre | liste fixe | 32,7 [32,5 ; 32,9] | −0,642 [−0,646 ; −0,637] | 0,061 [0,060 ; 0,062] | 0,026 [0,025 ; 0,026] | compromis |
| bureau | A2-calibre | tri | 38,4 [38,2 ; 38,6] | −0,722 [−0,727 ; −0,717] | 0,061 [0,060 ; 0,062] | 0,026 [0,025 ; 0,026] | compromis |
| bureau | A2-abusif | liste fixe | 25,7 [25,6 ; 25,9] | −0,653 [−0,658 ; −0,649] | 0,047 [0,046 ; 0,048] | 0,016 [0,015 ; 0,016] | compromis |
| bureau | A2-abusif | tri | 29,9 [29,8 ; 30,1] | −0,733 [−0,738 ; −0,728] | 0,047 [0,046 ; 0,048] | 0,016 [0,015 ; 0,016] | compromis |
| bureau | A4-calibre | liste fixe | 59,5 [59,5 ; 59,6] | −5,956 [−5,969 ; −5,944] | 0,091 [0,089 ; 0,092] | 0,078 [0,077 ; 0,080] | compromis |
| bureau | A4-calibre | tri | 65,2 [65,2 ; 65,3] | −6,558 [−6,571 ; −6,545] | 0,091 [0,089 ; 0,092] | 0,078 [0,077 ; 0,080] | compromis |
| bureau | A4-abusif | liste fixe | 44,2 [44,1 ; 44,2] | −5,974 [−5,986 ; −5,961] | 0,065 [0,063 ; 0,066] | 0,056 [0,054 ; 0,057] | compromis |
| bureau | A4-abusif | tri | 48,4 [48,4 ; 48,4] | −6,572 [−6,585 ; −6,560] | 0,065 [0,063 ; 0,066] | 0,056 [0,054 ; 0,057] | compromis |
| service client | A1 | liste fixe | −6,6 [−7,0 ; −6,2] | −0,120 [−0,122 ; −0,117] | 0,048 [0,047 ; 0,049] | 0,046 [0,045 ; 0,047] | compromis |
| service client | A1 | tri | −3,6 [−4,0 ; −3,3] | −0,134 [−0,136 ; −0,132] | 0,048 [0,047 ; 0,049] | 0,046 [0,045 ; 0,047] | compromis |
| service client | A2 | liste fixe | 33,0 [32,9 ; 33,2] | −0,724 [−0,729 ; −0,719] | 0,040 [0,040 ; 0,041] | 0,030 [0,029 ; 0,031] | compromis |
| service client | A2 | tri | 36,0 [35,9 ; 36,2] | −0,781 [−0,786 ; −0,776] | 0,040 [0,040 ; 0,041] | 0,030 [0,029 ; 0,031] | compromis |
| service client | A3 | liste fixe | 43,6 [43,5 ; 43,7] | −2,033 [−2,041 ; −2,026] | 0,038 [0,037 ; 0,039] | 0,032 [0,031 ; 0,033] | compromis |
| service client | A3 | tri | 46,6 [46,5 ; 46,7] | −2,175 [−2,182 ; −2,167] | 0,038 [0,037 ; 0,039] | 0,032 [0,031 ; 0,033] | compromis |
| service client | A4 | liste fixe | 47,3 [47,3 ; 47,4] | −6,394 [−6,406 ; −6,381] | 0,061 [0,060 ; 0,063] | 0,065 [0,063 ; 0,066] | compromis |
| service client | A4 | tri | 50,3 [50,3 ; 50,3] | −6,819 [−6,832 ; −6,806] | 0,061 [0,060 ; 0,063] | 0,065 [0,063 ; 0,066] | compromis |
| service client | A5 | liste fixe | 33,5 [33,3 ; 33,6] | −0,724 [−0,729 ; −0,719] | 0,041 [0,040 ; 0,041] | 0,049 [0,048 ; 0,050] | compromis |
| service client | A5 | tri | 36,5 [36,3 ; 36,6] | −0,781 [−0,786 ; −0,776] | 0,041 [0,040 ; 0,041] | 0,049 [0,048 ; 0,050] | compromis |
| service client | A6a | liste fixe | 36,4 [36,3 ; 36,5] | −2,462 [−2,470 ; −2,454] | 0,053 [0,052 ; 0,054] | 0,045 [0,044 ; 0,046] | compromis |
| service client | A6a | tri | 39,4 [39,2 ; 39,5] | −2,633 [−2,641 ; −2,625] | 0,053 [0,052 ; 0,054] | 0,045 [0,044 ; 0,046] | compromis |
| service client | A6b | liste fixe | 35,1 [35,0 ; 35,2] | −2,404 [−2,412 ; −2,396] | 0,061 [0,060 ; 0,062] | 0,046 [0,045 ; 0,047] | compromis |
| service client | A6b | tri | 38,1 [38,0 ; 38,2] | −2,575 [−2,583 ; −2,566] | 0,061 [0,060 ; 0,062] | 0,046 [0,045 ; 0,047] | compromis |
| service client | A7 | liste fixe | 49,4 [49,3 ; 49,4] | −2,528 [−2,536 ; −2,520] | 0,036 [0,035 ; 0,037] | 0,037 [0,036 ; 0,038] | compromis |
| service client | A7 | tri | 52,4 [52,3 ; 52,4] | −2,698 [−2,706 ; −2,690] | 0,036 [0,035 ; 0,037] | 0,037 [0,036 ; 0,038] | compromis |
| service client | A8 | liste fixe | 33,1 [33,0 ; 33,2] | −0,724 [−0,729 ; −0,719] | 0,041 [0,040 ; 0,042] | 0,029 [0,028 ; 0,030] | compromis |
| service client | A8 | tri | 36,1 [36,0 ; 36,2] | −0,781 [−0,786 ; −0,776] | 0,041 [0,040 ; 0,042] | 0,029 [0,028 ; 0,030] | compromis |
| service client | A2-calibre | liste fixe | 27,4 [27,2 ; 27,5] | −0,476 [−0,480 ; −0,472] | 0,051 [0,050 ; 0,051] | 0,044 [0,043 ; 0,045] | compromis |
| service client | A2-calibre | tri | 30,2 [30,0 ; 30,4] | −0,516 [−0,520 ; −0,512] | 0,051 [0,050 ; 0,051] | 0,044 [0,043 ; 0,045] | compromis |
| service client | A2-abusif | liste fixe | 21,6 [21,5 ; 21,7] | −0,487 [−0,491 ; −0,483] | 0,038 [0,037 ; 0,039] | 0,029 [0,028 ; 0,030] | compromis |
| service client | A2-abusif | tri | 23,7 [23,6 ; 23,8] | −0,527 [−0,531 ; −0,523] | 0,038 [0,037 ; 0,039] | 0,029 [0,028 ; 0,030] | compromis |
| service client | A4-calibre | liste fixe | 47,1 [47,1 ; 47,2] | −4,458 [−4,469 ; −4,447] | 0,123 [0,122 ; 0,125] | 0,130 [0,128 ; 0,131] | compromis |
| service client | A4-calibre | tri | 50,0 [49,9 ; 50,0] | −4,755 [−4,766 ; −4,744] | 0,123 [0,122 ; 0,125] | 0,130 [0,128 ; 0,131] | compromis |
| service client | A4-abusif | liste fixe | 35,0 [35,0 ; 35,0] | −4,474 [−4,484 ; −4,463] | 0,088 [0,086 ; 0,089] | 0,093 [0,091 ; 0,095] | compromis |
| service client | A4-abusif | tri | 37,1 [37,1 ; 37,1] | −4,771 [−4,782 ; −4,760] | 0,088 [0,086 ; 0,089] | 0,093 [0,091 ; 0,095] | compromis |

### Illustration seulement : un barème 1, 10, 100

REGLE.md, pièce 2 : un barème peut illustrer, jamais servir de critère. Dégâts pondérés = faibles + 10 × moyens + 100 × forts, pour 100 actions, avec leur intervalle.

| mélange | agent | tout faire valider | liste fixe | tri par le risque | la règle |
|--|--|--|--|--|--|
| bureau | A1 | 0,50 [0,47 ; 0,54] | 0,79 [0,75 ; 0,82] | 0,82 [0,78 ; 0,85] | 3,32 [3,26 ; 3,39] |
| bureau | A2 | 2,03 [1,96 ; 2,10] | 3,17 [3,10 ; 3,24] | 3,28 [3,21 ; 3,35] | 4,69 [4,59 ; 4,78] |
| bureau | A3 | 5,17 [5,07 ; 5,28] | 8,03 [7,92 ; 8,13] | 8,31 [8,20 ; 8,42] | 7,54 [7,41 ; 7,67] |
| bureau | A4 | 15,25 [15,07 ; 15,44] | 23,81 [23,63 ; 23,99] | 24,67 [24,48 ; 24,85] | 19,59 [19,38 ; 19,80] |
| bureau | A5 | 9,86 [9,70 ; 10,01] | 11,00 [10,84 ; 11,15] | 11,11 [10,96 ; 11,27] | 13,86 [13,68 ; 14,04] |
| service client | A1 | 0,83 [0,79 ; 0,88] | 1,04 [1,00 ; 1,09] | 1,06 [1,01 ; 1,10] | 5,99 [5,90 ; 6,08] |
| service client | A2 | 3,27 [3,18 ; 3,36] | 4,12 [4,03 ; 4,21] | 4,18 [4,09 ; 4,27] | 6,83 [6,71 ; 6,95] |
| service client | A3 | 8,12 [7,98 ; 8,26] | 10,26 [10,12 ; 10,40] | 10,40 [10,26 ; 10,54] | 11,82 [11,66 ; 11,99] |
| service client | A4 | 24,42 [24,17 ; 24,66] | 30,82 [30,58 ; 31,07] | 31,25 [31,01 ; 31,49] | 31,52 [31,24 ; 31,79] |
| service client | A5 | 12,95 [12,77 ; 13,13] | 13,80 [13,62 ; 13,98] | 13,86 [13,68 ; 14,04] | 18,34 [18,13 ; 18,55] |

Avec ce barème, la règle ferait mieux que les deux témoins simples pour les agents mauvais ou moyens (elle leur retire l'autonomie à enjeu faible), et moins bien pour les bons agents (elle leur donne de l'autonomie à enjeu moyen et fort, que les témoins ne donnent jamais). C'est une lecture, pas un verdict.

## Variantes du validateur : 0, 2, 5 et 10 %

Réglage de départ, α = 5 %, 5 000 répétitions. La trajectoire de la règle ne dépend pas de e (le contrôle automatique voit tout) ; seuls changent les dégâts et les corrections.

| e | mélange | agent | charge | écart de dégâts avec tout valider : faibles ; moyens ; forts | dégâts ≤ tout valider + 0,1 | + 0,5 | contre liste fixe | contre tri |
|--|--|--|--|--|--|--|--|--|
| 0 % | bureau | A1 | 39,8 [39,5 ; 40,1] | 0,141 [0,140 ; 0,142] ; 0,047 [0,046 ; 0,048] ; 0,023 [0,023 ; 0,024] | échoue | passe | compromis | compromis |
| 0 % | bureau | A2 | 82,0 [81,8 ; 82,2] | 0,162 [0,161 ; 0,163] ; 0,049 [0,048 ; 0,050] ; 0,015 [0,015 ; 0,016] | échoue | passe | compromis | compromis |
| 0 % | bureau | A4 | 101,4 [101,4 ; 101,4] | 0,013 [0,012 ; 0,014] ; 0,000 [0,000 ; 0,000] ; 0,000 [0,000 ; 0,000] | passe | passe | compromis | compromis |
| 0 % | service client | A1 | 48,4 [48,1 ; 48,8] | 0,098 [0,097 ; 0,099] ; 0,050 [0,049 ; 0,051] ; 0,048 [0,047 ; 0,048] | passe | passe | compromis | compromis |
| 0 % | service client | A2 | 88,0 [87,9 ; 88,2] | 0,134 [0,133 ; 0,136] ; 0,033 [0,032 ; 0,033] ; 0,021 [0,021 ; 0,022] | échoue | passe | compromis | compromis |
| 0 % | service client | A4 | 102,3 [102,3 ; 102,3] | 0,014 [0,013 ; 0,015] ; 0,000 [0,000 ; 0,000] ; 0,000 [0,000 ; 0,000] | passe | passe | compromis | compromis |
| 2 % | bureau | A1 | 39,8 [39,5 ; 40,1] | 0,138 [0,137 ; 0,139] ; 0,046 [0,046 ; 0,047] ; 0,023 [0,022 ; 0,024] | échoue | passe | compromis | compromis |
| 2 % | bureau | A2 | 82,0 [81,8 ; 82,2] | 0,158 [0,157 ; 0,160] ; 0,050 [0,049 ; 0,051] ; 0,017 [0,016 ; 0,018] | échoue | passe | compromis | compromis |
| 2 % | bureau | A4 | 101,4 [101,4 ; 101,4] | 0,013 [0,012 ; 0,013] ; 0,018 [0,017 ; 0,018] ; 0,016 [0,016 ; 0,017] | passe | passe | compromis | compromis |
| 2 % | service client | A1 | 48,4 [48,0 ; 48,8] | 0,096 [0,095 ; 0,097] ; 0,049 [0,049 ; 0,050] ; 0,047 [0,046 ; 0,048] | passe | passe | compromis | compromis |
| 2 % | service client | A2 | 88,0 [87,9 ; 88,2] | 0,132 [0,131 ; 0,133] ; 0,036 [0,035 ; 0,036] ; 0,025 [0,024 ; 0,026] | échoue | passe | compromis | compromis |
| 2 % | service client | A4 | 102,3 [102,3 ; 102,3] | 0,014 [0,013 ; 0,014] ; 0,025 [0,024 ; 0,026] ; 0,026 [0,025 ; 0,026] | passe | passe | compromis | compromis |
| 5 % | bureau | A1 | 39,8 [39,5 ; 40,1] | 0,134 [0,133 ; 0,135] ; 0,045 [0,044 ; 0,046] ; 0,022 [0,022 ; 0,023] | échoue | passe | compromis | compromis |
| 5 % | bureau | A2 | 82,0 [81,8 ; 82,1] | 0,153 [0,152 ; 0,155] ; 0,053 [0,052 ; 0,054] ; 0,020 [0,019 ; 0,020] | échoue | passe | compromis | compromis |
| 5 % | bureau | A4 | 101,4 [101,4 ; 101,4] | 0,012 [0,012 ; 0,013] ; 0,046 [0,045 ; 0,047] ; 0,039 [0,038 ; 0,040] | passe | passe | compromis | compromis |
| 5 % | service client | A1 | 48,4 [48,0 ; 48,8] | 0,093 [0,092 ; 0,094] ; 0,048 [0,047 ; 0,049] ; 0,046 [0,045 ; 0,047] | passe | passe | compromis | compromis |
| 5 % | service client | A2 | 88,0 [87,9 ; 88,2] | 0,128 [0,127 ; 0,129] ; 0,040 [0,040 ; 0,041] ; 0,030 [0,029 ; 0,031] | échoue | passe | compromis | compromis |
| 5 % | service client | A4 | 102,3 [102,3 ; 102,3] | 0,013 [0,013 ; 0,014] ; 0,061 [0,060 ; 0,063] ; 0,065 [0,063 ; 0,066] | passe | passe | compromis | compromis |
| 10 % | bureau | A1 | 39,8 [39,5 ; 40,1] | 0,127 [0,126 ; 0,128] ; 0,043 [0,042 ; 0,044] ; 0,022 [0,021 ; 0,022] | échoue | passe | compromis | compromis |
| 10 % | bureau | A2 | 82,0 [81,8 ; 82,1] | 0,145 [0,144 ; 0,146] ; 0,057 [0,056 ; 0,058] ; 0,024 [0,024 ; 0,025] | échoue | passe | compromis | compromis |
| 10 % | bureau | A4 | 101,4 [101,4 ; 101,4] | 0,012 [0,011 ; 0,012] ; 0,089 [0,088 ; 0,091] ; 0,078 [0,077 ; 0,080] | passe | passe | compromis | compromis |
| 10 % | service client | A1 | 48,4 [48,0 ; 48,8] | 0,089 [0,088 ; 0,090] ; 0,046 [0,045 ; 0,047] ; 0,044 [0,043 ; 0,045] | passe | passe | compromis | compromis |
| 10 % | service client | A2 | 88,0 [87,9 ; 88,2] | 0,122 [0,120 ; 0,123] ; 0,048 [0,047 ; 0,049] ; 0,039 [0,038 ; 0,040] | échoue | passe | compromis | compromis |
| 10 % | service client | A4 | 102,3 [102,3 ; 102,3] | 0,013 [0,012 ; 0,013] ; 0,125 [0,123 ; 0,126] ; 0,131 [0,129 ; 0,132] | échoue | passe | compromis | compromis |

Le validateur change peu le tableau. Plus il est mauvais, plus « tout faire valider » laisse passer d'erreurs, et plus l'écart à enjeu faible des bons agents se resserre ; il reste au-dessus de 0,1 à tous les e. Pour A4, l'écart à enjeu moyen et fort grandit avec e : il vient presque entièrement des variantes d'épreuve, que le validateur laisse passer comme les autres actions (choix 5).

## Ablations

Réglage de départ, α = 5 %, validateur à 5 %, 1 000 répétitions (les 1 000 premières des mêmes tirages que la règle). Écarts appariés : l'ablation moins la règle complète.

| ablation | charge A1 bureau ; service client | charge A2 bureau ; service client | écart de charge A2 bureau | écart de dégâts A2 bureau : faibles ; moyens ; forts | agent le plus touché (bureau) : écart charge ; dégâts faibles ; moyens ; forts | garantie, pire couple stable | bat liste fixe / tri (26 couples) |
|--|--|--|--|--|--|--|--|
| règle complète (référence, mêmes 1 000 répétitions pour les écarts) | 39,8 [39,5 ; 40,1] ; 48,4 [48,0 ; 48,8] | 82,0 [81,8 ; 82,1] ; 88,0 [87,9 ; 88,2] | — | — | — | A3 sur SOR (service client) : 2,8 % [2,4 ; 3,3], n = 5 000 → **passe** | — |
| sans remise à zéro | 39,9 [39,2 ; 40,7] ; 47,7 [46,9 ; 48,5] | 81,9 [81,5 ; 82,3] ; 87,9 [87,6 ; 88,2] | −0,0 [−0,1 ; 0,1] | 0,000 [0,000 ; 0,000] ; 0,000 [−0,001 ; 0,002] ; 0,000 [−0,001 ; 0,001] | A6a : −0,7 [−0,8 ; −0,7] ; 0,023 [0,022 ; 0,025] ; 0,013 [0,010 ; 0,016] ; 0,003 [0,000 ; 0,005] | A3 sur ARG (service client) : 3,1 % [2,2 ; 4,4], n = 1 000 → **passe** | compromis 26 / compromis 26 |
| sans pondération par l'enjeu | 32,5 [31,7 ; 33,2] ; 40,2 [39,5 ; 41,0] | 78,7 [78,2 ; 79,1] ; 85,7 [85,4 ; 86,1] | −3,3 [−3,5 ; −3,1] | −0,038 [−0,041 ; −0,036] ; −0,000 [−0,002 ; 0,001] ; 0,026 [0,024 ; 0,028] | A1 : −7,5 [−7,8 ; −7,1] ; −0,010 [−0,011 ; −0,009] ; −0,000 [−0,001 ; 0,000] ; 0,015 [0,013 ; 0,016] | A4 sur MSG (service client) : 0,9 % [0,5 ; 1,7], n = 1 000 → **passe** | compromis 26 / compromis 26 |
| sans doute gratuit | 40,0 [39,2 ; 40,7] ; 47,7 [46,9 ; 48,5] | 82,0 [81,6 ; 82,4] ; 87,9 [87,6 ; 88,2] | 0,0 [−0,1 ; 0,1] | 0,000 [0,000 ; 0,000] ; −0,001 [−0,002 ; 0,001] ; 0,001 [−0,001 ; 0,002] | A2-calibre : 23,1 [22,7 ; 23,6] ; −0,140 [−0,143 ; −0,138] ; −0,055 [−0,057 ; −0,052] ; −0,020 [−0,021 ; −0,018] | A3 sur SOR (bureau) : 3,1 % [2,2 ; 4,4], n = 1 000 → **passe** | compromis 26 / compromis 26 |
| sans palier du milieu | 58,0 [57,3 ; 58,8] ; 60,9 [60,2 ; 61,7] | 90,6 [90,3 ; 90,9] ; 93,7 [93,4 ; 93,9] | 8,6 [8,4 ; 8,9] | 0,000 [0,000 ; 0,000] ; −0,000 [−0,002 ; 0,001] ; 0,000 [−0,001 ; 0,001] | A1 : 18,1 [17,5 ; 18,7] ; 0,000 [0,000 ; 0,000] ; −0,000 [−0,001 ; 0,000] ; −0,000 [−0,000 ; 0,000] | A3 sur ARG (service client) : 3,2 % [2,3 ; 4,5], n = 1 000 → **passe** | compromis 26 / compromis 26 |
| sans épreuve | 39,3 [38,5 ; 40,0] ; 46,8 [46,1 ; 47,6] | 79,1 [78,8 ; 79,5] ; 84,4 [84,1 ; 84,7] | −2,8 [−2,9 ; −2,7] | 0,000 [0,000 ; 0,000] ; −0,002 [−0,004 ; −0,001] ; −0,005 [−0,006 ; −0,004] | A4 : −1,9 [−1,9 ; −1,9] ; 0,000 [0,000 ; 0,000] ; −0,046 [−0,049 ; −0,044] ; −0,038 [−0,040 ; −0,036] | A3 sur SOR (bureau) : 3,4 % [2,4 ; 4,7], n = 1 000 → **passe** | compromis 26 / compromis 26 |

Réactivité des ablations (A6a, changement de modèle déclaré ; A6b, dérive silencieuse ; 95e centile du délai et part non retirée, bureau) :

| variante | A6a bureau | A6b bureau | A6a service client | A6b service client |
|--|--|--|--|--|
| règle complète | 0 [0 ; 0], non retiré 0,0 % | 495 [476 ; 508], non retiré 0,0 % | 0 [0 ; 0], non retiré 0,0 % | 1 414 [1 387 ; 1 441], non retiré 4,0 % |
| sans remise à zéro | 495 [460 ; 530], non retiré 0,0 % | 503 [469 ; 526], non retiré 0,0 % | 1 423 [1 377 ; 1 484], non retiré 4,1 % | 1 422 [1 382 ; 1 484], non retiré 4,1 % |
| sans épreuve | 0 [0 ; 0], non retiré 0,0 % | 491 [457 ; 521], non retiré 0,0 % | 0 [0 ; 0], non retiré 0,0 % | 1 421 [1 373 ; 1 483], non retiré 4,0 % |
| sans palier du milieu | 0 [0 ; 0], non retiré 0,0 % | 542 [503 ; 597], non retiré 0,0 % | 0 [0 ; 0], non retiré 0,0 % | 1 249 [1 181 ; 1 351], non retiré 2,4 % |
| sans pondération | 0 [0 ; 0], non retiré 0,0 % | 546 [506 ; 577], non retiré 0,0 % | 0 [0 ; 0], non retiré 0,0 % | 1 500 [1 458 ; 1 500], non retiré 5,6 % |

Ce que montrent les ablations, mesuré :

- **Sans remise à zéro** : ne change rien hors changement de configuration. Pour A6a, la dégradation annoncée n'est plus vue : dégâts faibles en plus 0,023 [0,022 ; 0,025] pour 100 actions, et le délai de retrait devient celui de la dérive silencieuse.
- **Sans pondération par l'enjeu** : moins de charge pour A1 (−7,5 [−7,8 ; −7,1]) mais plus de dégâts forts (0,015 [0,013 ; 0,016]) : les sorties et l'argent montent plus vite.
- **Sans doute gratuit** : l'agent honnête qui doute paie cher (A2 calibré : charge 23,1 [22,7 ; 23,6]), mais l'abus du doute est fermé : pire couple « doute » de la garantie 0,7 % [0,3 ; 1,4] (n = 1 000) contre 1,7 % [1,4 ; 2,1] (n = 5 000) avec la règle ; A4 calibré fait moins de dégâts forts (−0,040 [−0,044 ; −0,036]).
- **Sans palier du milieu** : A1 paie 18,1 [17,5 ; 18,7] de charge en plus pour des dégâts inchangés (faibles 0,000 [0,000 ; 0,000]). Dans ce modèle, une correction après coup arrête l'erreur aussi bien qu'une validation avant : le palier 2 est gratuit.
- **Sans épreuve** : moins de charge et moins de dégâts pour les mauvais agents (A4 : charge −1,9 [−1,9 ; −1,9], dégâts forts −0,038 [−0,040 ; −0,036]), parce que les variantes d'épreuve sont comptées comme de vraies tâches (choix 5) ; la garantie ne bouge pas de façon décelable.

Interprété : dans ce monde, l'épreuve ne protège de rien que le compteur ne protège déjà ; avec le plancher du plan, la deuxième erreur ferme de toute façon le palier 3. Son rôle prévu, effacer les erreurs d'avant un changement de configuration, ne joue qu'après un changement.

## Agents bons laissés de côté, délai de promotion

Règle au réglage de départ, α = 5 %, 5 000 répétitions. « Jamais » : part des répétitions où le type n'atteint jamais le palier 3 avant l'horizon (intervalle de Wilson). Délai : numéro de l'action (tous types confondus) de la première promotion au palier 3, parmi les répétitions promues (centiles : intervalle par rééchantillonnage). « Bon » : q au plus pb du palier 3 (A2 n'est pas bon à enjeu fort, où pb = 1 %).

| mélange | agent | type | bon ? | jamais promu au palier 3 | répétitions promues | délai moyen | délai médian | 90e centile |
|--|--|--|--|--|--|--|--|--|
| bureau | A1 | LEC | oui | 0,6 % [0,4 ; 0,9] | 4 969 | 43 [42 ; 43] | 41 [41 ; 41] | 55 [55 ; 56] |
| bureau | A1 | ECR | oui | 0,7 % [0,5 ; 1,0] | 4 964 | 130 [129 ; 131] | 126 [125 ; 127] | 173 [171 ; 176] |
| bureau | A1 | DUR | oui | 4,6 % [4,0 ; 5,2] | 4 772 | 529 [523 ; 535] | 470 [468 ; 473] | 791 [740 ; 833] |
| bureau | A1 | EXE | oui | 4,2 % [3,7 ; 4,8] | 4 789 | 523 [517 ; 529] | 467 [464 ; 470] | 784 [730 ; 825] |
| bureau | A1 | MSG | oui | 0,8 % [0,6 ; 1,0] | 4 962 | 328 [326 ; 331] | 316 [314 ; 319] | 439 [433 ; 445] |
| bureau | A1 | SOR | oui | 14,0 % [13,1 ; 15,0] | 4 299 | 950 [939 ; 961] | 808 [804 ; 812] | 1 606 [1 555 ; 1 636] |
| bureau | A1 | ARG | oui | 28,3 % [27,1 ; 29,6] | 3 583 | 1 913 [1 904 ; 1 921] | 1 886 [1 876 ; 1 894] | 2 212 [2 196 ; 2 228] |
| bureau | A2 | LEC | oui | 8,4 % [7,7 ; 9,2] | 4 580 | 46 [46 ; 46] | 43 [43 ; 44] | 64 [63 ; 64] |
| bureau | A2 | ECR | oui | 9,6 % [8,9 ; 10,5] | 4 518 | 140 [139 ; 141] | 132 [131 ; 133] | 196 [194 ; 199] |
| bureau | A2 | DUR | oui | 37,7 % [36,4 ; 39,1] | 3 115 | 581 [571 ; 591] | 481 [477 ; 486] | 971 [936 ; 994] |
| bureau | A2 | EXE | oui | 38,1 % [36,7 ; 39,4] | 3 097 | 573 [564 ; 583] | 482 [478 ; 487] | 952 [918 ; 974] |
| bureau | A2 | MSG | oui | 9,4 % [8,6 ; 10,2] | 4 532 | 351 [348 ; 353] | 337 [333 ; 341] | 492 [485 ; 499] |
| bureau | A2 | SOR | non | 71,1 % [69,9 ; 72,4] | 1 443 | 960 [941 ; 979] | 808 [800 ; 814] | 1 568 [1 505 ; 1 620] |
| bureau | A2 | ARG | non | 74,7 % [73,5 ; 75,9] | 1 264 | 1 917 [1 902 ; 1 932] | 1 884 [1 869 ; 1 901] | 2 216 [2 192 ; 2 251] |
| service client | A1 | LEC | oui | 0,7 % [0,5 ; 1,0] | 4 965 | 48 [48 ; 48] | 46 [46 ; 47] | 63 [62 ; 63] |
| service client | A1 | ECR | oui | 0,6 % [0,4 ; 0,8] | 4 972 | 395 [392 ; 398] | 381 [378 ; 384] | 528 [522 ; 537] |
| service client | A1 | DUR | oui | 3,6 % [3,1 ; 4,1] | 4 822 | 206 [204 ; 208] | 186 [185 ; 187] | 291 [267 ; 309] |
| service client | A1 | EXE | oui | 14,8 % [13,9 ; 15,8] | 4 259 | 1 864 [1 854 ; 1 874] | 1 833 [1 822 ; 1 843] | 2 296 [2 279 ; 2 322] |
| service client | A1 | MSG | oui | 0,7 % [0,5 ; 1,0] | 4 964 | 656 [652 ; 661] | 637 [631 ; 643] | 882 [870 ; 893] |
| service client | A1 | SOR | oui | 14,2 % [13,2 ; 15,2] | 4 292 | 772 [763 ; 781] | 652 [648 ; 655] | 1 308 [1 281 ; 1 340] |
| service client | A1 | ARG | oui | 12,4 % [11,5 ; 13,3] | 4 380 | 814 [805 ; 823] | 693 [689 ; 698] | 1 374 [1 333 ; 1 402] |
| service client | A2 | LEC | oui | 8,9 % [8,1 ; 9,7] | 4 557 | 52 [52 ; 52] | 49 [48 ; 50] | 72 [71 ; 73] |
| service client | A2 | ECR | oui | 8,7 % [8,0 ; 9,5] | 4 564 | 424 [421 ; 428] | 404 [400 ; 408] | 602 [590 ; 608] |
| service client | A2 | DUR | oui | 37,1 % [35,8 ; 38,4] | 3 146 | 227 [223 ; 230] | 191 [189 ; 193] | 371 [360 ; 383] |
| service client | A2 | EXE | oui | 49,3 % [47,9 ; 50,7] | 2 535 | 1 875 [1 862 ; 1 889] | 1 837 [1 820 ; 1 852] | 2 330 [2 296 ; 2 358] |
| service client | A2 | MSG | oui | 9,2 % [8,4 ; 10,0] | 4 540 | 705 [699 ; 711] | 675 [668 ; 681] | 992 [972 ; 1 003] |
| service client | A2 | SOR | non | 70,7 % [69,4 ; 71,9] | 1 467 | 772 [757 ; 787] | 661 [653 ; 667] | 1 245 [1 199 ; 1 286] |
| service client | A2 | ARG | non | 70,5 % [69,2 ; 71,7] | 1 477 | 807 [791 ; 822] | 693 [687 ; 701] | 1 306 [1 237 ; 1 352] |

Les autres réglages sont dans `promotion.csv` et dans `fig3_delai_promotion.png`. Le délai est surtout une affaire de volume : un type rare met longtemps à accumuler ses réussites (ARG en bureau : 72 réussites vérifiées d'affilée pour environ 38 actions vérifiables par tranche de 1 000).

## Épreuves : réussite comparée aux tâches ordinaires

Réglage de départ, α = 5 %, 5 000 répétitions. Réussite d'une épreuve : les 3 variantes justes. Variante : une seule. Tâches ordinaires : actions vérifiables des types à enjeu moyen ou fort, issues réelles du tirage (n : nombre de ces tâches, toutes répétitions). Intervalle des rapports par la méthode delta, répétition par répétition ; « 3 tâches » : la réussite d'une tâche au cube, bornes comprises.

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

Les épreuves sont beaucoup plus dures que les tâches ordinaires, comme voulu (tirées des cas difficiles), et elles séparent nettement les agents : un bon agent les réussit souvent, un mauvais presque jamais. Leur coût : de 0,5 à 6 validations pour 100 actions (`mesures.csv`, colonne `charge_epreuve`).

## Ce qui surprend

Chaque point sépare ce qui est **mesuré** de ce qui est **interprété**.

**1. La règle retire peu à peu l'autonomie à tous les agents, même excellents.**  
Mesuré (fig5_autonomie_temps.png, 5 000 répétitions, part des actions d'une fenêtre de 100 exécutées au palier 2 ou 3) : en « bureau », A1 (0,5 % d'erreurs) culmine à 78,6 % [78,1 ; 79,0] (actions 800 à 899), puis 41,2 % [40,7 ; 41,7] sur les 100 dernières ; A2 (2 %) passe de 56,6 % [56,4 ; 56,9] à 4,1 % [4,0 ; 4,3]. En « service client » : A1 de 72,7 % [72,2 ; 73,1] à 30,8 % [30,3 ; 31,3], A2 de 44,4 % [44,0 ; 44,9] à 6,1 % [6,0 ; 6,2]. La pente ne s'arrête pas à l'horizon.  
Interprété : c'est le plancher du plan. r est plafonné, s n'est jamais oublié ; le score monte donc sans limite avec les erreurs, et chaque type a un budget d'erreurs fini par configuration : une erreur tolérée au palier 3, 2 à 4 au palier 2 selon le réglage et l'enjeu (section « Ce que la règle exige »). Tout agent dont le taux n'est pas nul finit au palier 1 partout ; le seul paramètre est le temps. Le verdict d'utilité dépend donc de l'horizon : plus on mesure longtemps, plus il est mauvais. Cela contredit l'intention écrite dans REGLE.md, pièce 7 (« ce n'est pas une punition à vie ») : avec ce plancher, dans une même configuration, la deuxième erreur sur un type en est une pour le palier 3. L'essai hors plan (plancher glissant, dernière section) va dans le même sens : sans rien changer d'autre, l'autonomie se stabilise au lieu de s'éteindre.

**2. Le hasard fait aussi bien que la règle pour tout agent stable.**  
Mesuré : A2, bureau, écart règle moins hasard : dégâts faibles −0,002 [−0,005 ; 0,000], charge 1,95 [1,78 ; 2,12], soit la charge des épreuves (1,95 [1,94 ; 1,97]). Les écarts de dégâts moyens et forts (0,007 [0,005 ; 0,008] ; 0,006 [0,005 ; 0,007]) font ensemble les dégâts des variantes d'épreuve (0,012 [0,012 ; 0,013]). La règle ne bat le hasard qu'en dérive : A6b, dégâts faibles −0,259 [−0,262 ; −0,255].  
Interprété : dans ce monde, les erreurs sont indépendantes et le taux est constant ; le passé d'un agent stable ne dit rien de sa prochaine action. Le hasard du plan reprend la part de temps de la règle, type par type : il hérite donc de tout ce que la règle sait sur « qui mérite quoi », et ne teste que le *moment* des promotions. Ce moment n'a de valeur que si l'agent change. L'exigence « battre le hasard » (REGLE.md, pièce 1) ne peut être remplie, dans cette simulation, que sur les agents qui changent.

**3. Un agent qui s'améliore n'est jamais récompensé.**  
Mesuré : A7 (10 %, puis 2 % après un changement de modèle déclaré) n'exécute jamais plus de 0,4 % [0,3 ; 0,4] de ses actions sans validation préalable, par fenêtre de 100, après t = 1 500 (bureau). Il fait pire que le hasard sur tout (charge 4,2 [4,1 ; 4,2], dégâts faibles 0,015 [0,014 ; 0,016]) : son peu d'autonomie tombe dans sa mauvaise période. Avec la lecture de REGLE.md, pièce 8 (les erreurs à enjeu faible disparaissent au changement de modèle), sa charge passe de 102,5 [102,5 ; 102,6] à 89,4 [89,2 ; 89,7] (1 000 répétitions).  
Interprété : le plan (test de la section 8 : « les remises à zéro ne touchent jamais s ») et REGLE.md, pièce 8, se contredisent sur les erreurs à enjeu faible. La simulation suit le plan ; la lecture de REGLE.md est nettement plus favorable à l'agent qui progresse. Même alors, les types à enjeu moyen ou fort restent longtemps fermés : chaque erreur passée devient une épreuve à réussir une par une, avec 50 actions d'attente après chaque échec (choix 4).

**4. La garantie cède quand l'agent dérive sans le dire, ou quand il doute à bon escient.**  
Mesuré : au réglage de départ, A6b (2 % puis 10 %, rien d'annoncé) est promu au palier 3 sur EXE (service client) après la dérive dans 23,3 % [22,1 ; 24,5] des répétitions (n = 5 000). Au réglage souple, A4 avec doute calibré l'est sur DUR (service client) dans 6,8 % [5,4 ; 8,5] (n = 1 000).  
Interprété : A6b est promu sur des réussites accumulées avant la dérive, sur un type rare qui n'avait pas fini de les réunir ; aucun test qui cumule les preuves ne l'évite sans oubli ou sans annonce du changement. Le doute calibré retire des preuves surtout les cas difficiles, là où sont les erreurs : par le calcul, A4 paraît se tromper 11,1 fois sur 100 au lieu de 15, sous le pm du réglage souple (15 %) ; A2 paraît à 1,47 % au lieu de 2 %. Le doute « gratuit » est donc exploitable, comme le craignait la pièce 4.

**5. α ne sert presque à rien.**  
Mesuré : ln B vaut −2,944 à α = 5 % et −2,773 à α = 20 % ; la charge d'A2 (bureau) passe de 82,0 [81,8 ; 82,1] à 81,7 [81,3 ; 82,1], celle d'A1 de 39,8 [39,5 ; 40,1] à 39,5 [38,7 ; 40,2].  
Interprété : dans le test de Wald, α règle surtout le seuil de rejet ln A ; la règle n'en a pas, elle n'utilise que ln B, où α n'entre que par 1 − α. Le « risque de laisser de côté un bon agent » n'est pas piloté par α mais par l'horizon et le plancher.

**6. Les deux concurrents simples ne passent pas l'utilité non plus.**  
Mesuré : hors lectures, la liste fixe coûte 72,7 [72,7 ; 72,8] et le tri par le risque 61,8 [61,8 ; 61,8] (bureau) ; en « service client », la liste fixe coûte 55,0 [55,0 ; 55,0] en tout. Leurs dégâts faibles dépassent la marge 0,1 même pour l'agent excellent : A1 en bureau, liste fixe 0,303 [0,300 ; 0,306] contre 0,017 [0,016 ; 0,017] pour tout faire valider ; A2, 1,205 [1,200 ; 1,211] contre 0,066 [0,065 ; 0,068].  
Interprété : le critère « hors lectures » fait ce que le plan voulait. Aucune règle de ce tableau, témoins compris, ne passe l'utilité avec les marges 0 et 0,1. La question de la pièce 1 n'est donc pas seulement « la règle bat-elle les témoins ? » mais « quelle marge de dégâts accepte-t-on ? ».

**7. Au réglage strict, l'argent en « bureau » est presque hors d'atteinte.**  
Mesuré : au réglage strict, ARG en bureau est promu dans 0,14 % [0,10 ; 0,19] des répétitions, tous taux q confondus de 0,25 % à 30 % (n = 26 000, fig2_garantie_bureau.png). Calcul : 146 réussites vérifiées d'affilée pour 114 actions vérifiables en moyenne sur l'horizon.  
Interprété : à volume faible, un réglage strict revient à un plafond de fait.

## Limites

- **Monde idéal, par construction.** Erreurs indépendantes d'une action à l'autre, taux constant dans chaque phase, contrôle automatique parfait sur les actions vérifiables, validateur qui rate 5 % des erreurs au hasard (ni fatigue, ni complaisance). Une vraie mission corrèle ses actions ; un vrai contrôle se trompe.
- **Même taux sur tous les types** (sauf A5). La règle ne peut alors rien gagner à répartir l'autonomie entre les types d'un même agent : c'est son principal avantage espéré sur une liste fixe, et cette simulation ne le met presque pas à l'épreuve (seul A5 le fait).
- **Un seul horizon (3 000 actions).** Le retrait progressif de l'autonomie (surprise 1) dépend de l'horizon ; un horizon plus long donnerait une charge plus haute aux bons agents.
- **Une seule forme de dérive** (2 % à 10 % d'un coup à t = 1 500) et une seule amélioration.
- **Les variantes d'épreuve sont comptées comme de vraies tâches** (charge et dégâts), choix prudent qui pénalise la règle ; leur part est isolée (`charge_epreuve`, `degats_epreuve`).
- **« Bon » et « mauvais » sont des définitions de travail** (q au plus pb, q au moins pm) : le plan les laisse à fixer après simulation. Les courbes de garantie (fig2) permettent d'en choisir d'autres.
- **Dégâts comptés pour 100 actions du flux entier**, pas pour 100 actions du niveau : un niveau rare pèse peu dans ce compte.
- **Statistiques** : intervalles par l'approximation normale (moyennes), Wilson (proportions), méthode delta (rapports), rééchantillonnage (centiles). Aucune correction pour comparaisons multiples : sur des dizaines de couples et de critères, quelques « indécis » ou « échoue » isolés peuvent être du bruit ; les conclusions ci-dessus reposent sur des écarts nets et répétés.
- **Réglages autres que celui de départ à 1 000 répétitions** : intervalles environ deux fois plus larges, d'où quelques « indécis ».
- **Ce n'est pas l'expérience de confirmation** ; aucun agent réel, aucune donnée réelle.

## Choix d'implémentation

Points où le plan laisse un choix ; à chaque fois, l'option la plus simple et la plus prudente.

1. **« Sous ln B » lu « au plus ln B »** (tolérance 1e−9). Seule lecture compatible avec les tests (54 ; 2 erreurs depuis le plancher).
2. **r plafonné à r_max réel** (53,44 pour pb 2 %, pm 10 %) : r ← min(r + 1, r_max). Le plafond se calcule sur le test du palier 3 ; il sert aussi au test du palier 2.
3. **Mise à jour du palier.** Une réussite ne peut que faire monter (au plus haut palier dont le score est au plus ln B). Le palier ne descend que sur une erreur (un cran pour l'enjeu faible, palier 1 pour l'enjeu moyen ou fort) ou sur un changement de configuration (recalcul complet). L'action est exécutée au palier d'avant sa propre preuve.
4. **Épreuves.** Une par erreur à enjeu moyen ou fort, passées une à une, à l'arrivée de la prochaine action du type ; après un échec, nouvel essai après 50 actions du type. Une nouvelle erreur ne remet pas ce délai à zéro ; un changement de modèle, si. Une épreuve ratée n'ajoute pas d'erreur. Dans la même configuration, une épreuve réussie n'efface rien ; après un changement, elle efface son erreur (s − 1). r ne compte pas tant qu'une épreuve reste ouverte.
5. **Variantes d'épreuve** : 3 cas difficiles (taux min(0,9 ; 6q) du moment), en plus des 3 000 actions, exécutées au palier 1 : elles comptent dans la charge (une validation chacune) et dans les dégâts (ratées avec la probabilité e), pas dans le dénominateur. Le doute de l'agent s'y applique : variante en doute neutre et remplacée (règle) ; comptée comme ratée (sans doute gratuit).
6. **Erreurs à enjeu faible au changement de modèle : s gardé** (test de la section 8 du plan), contre REGLE.md, pièce 8, qui les fait disparaître. La lecture de REGLE.md tourne en sensibilité (`regle_oubli_faibles`).
7. **Consigne modifiée** : r divisé par deux sur le type, palier recalculé (il peut descendre de plusieurs crans).
8. **Plafonnés** : trois sources (plafonds absolus 1 %, 20 % de SOR, 20 % d'ARG) ; taux d'erreur de la source (plafonds absolus : taux « partout » de l'agent) ; enjeu fort pour les dégâts ; toujours au palier 1, sauf sous « tout approuver ».
9. **Doute** : une validation (charge), aucune preuve ; au palier 1, c'est la validation déjà comptée. Doute calibré : sur une action difficile, une fois sur deux, indépendamment de l'issue. Doute abusif : 30 % de toutes les actions. Une action en doute est validée : l'erreur est arrêtée avec la probabilité 1 − e.
10. **Invérifiable** : 5 % des actions, tirées au hasard, indépendamment du reste.
11. **Validateur** : un même nombre aléatoire par action pour toutes les règles et toutes les valeurs de e (erreur ratée si ce nombre est sous e).
12. **Tout approuver** : tout part sans validation, plafonnés compris ; les doutes sont ignorés.
13. **Liste fixe et tri par le risque** : « agir seul » = palier 3.
14. **Trois réussites** : palier 3 après 3 réussites vérifiées d'affilée (doute et invérifiable n'interrompent pas la série), palier 1 à la première erreur vérifiée ; pas de palier 2, pas de remise à zéro, plafonnés au palier 1.
15. **Oracle** : palier 3 si et seulement si le vrai q du moment est au plus pb du palier 3 du réglage ; pas de palier 2. Calculé pour les pb stricte, de départ et souple.
16. **Hasard** : pour chaque type, les mêmes parts de palier 2 et de palier 3 que la règle, en moyenne sur les répétitions, tirées action par action. Une première version reprenait la part de la même répétition : elle donnait au hasard une information sur les erreurs de la répétition (une erreur fait baisser la part de la règle), donc un avantage injuste. Remplacée avant les résultats ci-dessus.
17. **Sans remise à zéro** : on ignore les changements de configuration (pièce 8). La remise de r à zéro après une erreur à enjeu moyen ou fort (pièce 7) reste.
18. **Sans pondération** : les réglages de l'enjeu moyen pour tous les types ; le traitement des erreurs ne change pas.
19. **Sans épreuve** : erreur à enjeu moyen ou fort → palier 1, r = 0, s + 1, et r recompte aussitôt ; au changement de modèle, r = 0 et s reste (rien ne l'efface).
20. **Droits élargis** : codés et testés (version de référence) ; aucun scénario du plan ne les utilise.
21. **Agent mauvais** sur un type : q au moins pm du palier 3 de son niveau d'enjeu, au réglage considéré ; **bon** : q au plus pb. Couples comptés pour la garantie : agents stables (A3, A4, A5 et les doutes d'A4), plus les phases mauvaises d'A6a (après la remise à zéro), d'A6b (après la dérive) et d'A7 (avant le changement).
22. **Verdicts** trivalués sur les intervalles à 95 % : passe, échoue, indécis.
23. **« Bat »** : écarts appariés ; meilleure sur au moins une mesure parmi la charge et les dégâts des trois niveaux, pire sur aucune. La charge hors lectures n'entre pas dans ce critère ; elle ne changerait aucun verdict (la règle est toujours pire sur au moins un niveau de dégâts).
24. **Utilité jugée sur A1 et A2**, les agents à qui l'autonomie est due ; le critère de dégâts est aussi donné pour les 13 agents.
25. **Dégâts** pour 100 actions du flux, par niveau d'enjeu.
26. **Réactivité** : couples (répétition, type) au palier 2 ou 3 à t = 1 500 ; délai jusqu'au premier retour au palier 1 ; censure à l'horizon (compté 1 500, part « non retiré » donnée).
27. **Répétitions** : 5 000 pour le réglage de départ α = 5 % et tous les témoins ; 1 000 pour les cinq autres réglages, les ablations et les sensibilités (les 1 000 premières des mêmes tirages). La grille entière tourne en 3 minutes environ : aucune réduction n'a été nécessaire.
28. **Graines** : graine maîtresse 20261104 ; flux SeedSequence([20261104, 1, mélange]) ; épreuves [20261104, 2, agent, mélange, lot] ; validateur des épreuves [20261104, 3, …] ; rééchantillonnage [20261104, 4] ; hasard [20261104, 5, agent, mélange, réglage] ; balayage de garantie [20261104, 6, mélange, q].

## Hors plan : une piste sur le plancher (exploratoire, pas un verdict)

Ajouté parce que la surprise 1 vient d'un seul mécanisme. Ce n'est pas un réglage de la grille et cela ne change aucun verdict ci-dessus. Variante : le plafond de r monte avec les erreurs, r ≤ r_max + s·a/b. Le score ne descend toujours pas sous ln B − a, mais après une erreur, les réussites suivantes le ramènent au plancher (score « réfléchi », proche d'un CUSUM) au lieu d'être perdues. Réglage de départ, α = 5 %, 1 000 répétitions.

- Charge (bureau) : A1 20,0 [19,7 ; 20,2], A2 33,1 [32,9 ; 33,3] ; hors lectures, A1 35,5 [35,1 ; 35,9], A2 59,3 [58,9 ; 59,7]. En service client, hors lectures : A1 49,7 [49,0 ; 50,3], A2 87,5 [87,2 ; 87,9].
- Prix en dégâts faibles, écart avec la règle du plan : A1 0,171 [0,166 ; 0,177], A2 1,033 [1,021 ; 1,045] pour 100 actions.
- Garantie, pire couple stable : A3 sur ARG (service client) : 3,1 % [2,2 ; 4,4], n = 1 000 → **passe** ; avec doute : A4-calibre sur DUR (service client) : 2,3 % [1,5 ; 3,4], n = 1 000 → **passe** ; dérive silencieuse : A6b sur EXE (service client, après t = 1 500) : 22,9 % [20,4 ; 25,6], n = 1 000 → **échoue**.
- Contre la liste fixe (26 couples) : compromis 26.

Lecture : ce plancher garde l'autonomie des bons agents (fig6_hors_plan_plancher.png) sans dégrader la garantie mesurée, mais il ne règle ni la dérive silencieuse ni la comparaison avec la liste fixe. À décider par Otsoa, avant le gel, s'il faut changer le plancher : la simulation montre seulement que c'est le levier principal de la charge.

## Fichiers

- `mesures.csv` : charge et dégâts (moyenne, intervalle) pour chaque mélange, agent, règle, réglage et e.
- `comparaisons.csv` : écarts appariés (la règle, ses ablations et quelques témoins contre les autres).
- `verdict.csv` : chaque critère de la pièce 1, réglage par réglage.
- `garantie.csv`, `garantie_courbe.csv` : promotions au palier 3, par couple et selon le vrai taux q.
- `promotion.csv` : délais de première promotion ; `reactivite.csv` ; `epreuves.csv` ; `autonomie_temps.csv`.
- Figures : `fig1_charge_degats_bureau.png`, `fig1_charge_degats_service_client.png` (charge contre dégâts par niveau d'enjeu, toutes les règles) ; `fig2_garantie_*.png` ; `fig3_delai_promotion.png` ; `fig4_reactivite.png` ; `fig5_autonomie_temps.png` ; `fig6_hors_plan_plancher.png` (exploratoire).
- `meta.json` : graine, horizon, répétitions, durée, version de numpy.
- Reproduire (3 minutes environ, depuis `simulation/`) : `.venv/bin/python executer.py --verifier-tests && .venv/bin/python rapport.py && .venv/bin/python ecrire_resultats.py`.
