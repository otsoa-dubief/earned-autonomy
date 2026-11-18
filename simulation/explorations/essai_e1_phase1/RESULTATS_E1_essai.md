# Exploration E1 · résultats

> Exploration annoncée comme telle (`PLAN_EXPLORATION_E1.md`, révision 1). Elle ne change pas le verdict de la deuxième passe (`resultats/`). Écrit le 04/11/2026 à 18:33 par `ecrire_resultats_e1.py`, à partir des CSV de ce dossier.
> Horizons : court 3000 actions × 200 répétitions ; long 150000 actions × 40 répétitions (blocs de 20). Graine maîtresse 20261104. 108 tâches, 19 relances, 2,0 min. Gel : `GEL_E1.txt` (absent).
> **ESSAI À PEU DE RÉPÉTITIONS : ces chiffres ne valent rien comme résultat.**

## En tête : la règle retenue (section 4, appliquée mécaniquement)

**Règle retenue : B-tout.** Charge hors lectures la plus basse parmi les règles qui tiennent le budget.

| règle | tient le budget partout | charge hors lectures (court, couples délégables) | couples | marge de la pire cellule | pire cellule | cellules relancées |
|--|--|--|--|--|--|--|
| A½ | oui | 78,6 | 55 | 0,732 | A2, service client, long, faible | 0 |
| A¼ | oui | 78,0 | 55 | 0,714 | bordD_faible_1.5barre, service client, court, faible, après le changement | 0 |
| A-dégâts | non (20 cellule(s)) | 64,4 | 55 | −0,990 | bordD_moyen_3barre, bureau, court, moyen, après le changement | 15 |
| B-régulier | non (7 cellule(s)) | 63,8 | 55 | −0,787 | bordD_moyen_3barre, bureau, court, moyen, après le changement | 6 |
| B-tout | oui | 72,7 | 55 | 0,507 | bordD_fort_3barre, bureau, long, fort, après le changement | 0 |

- A-dégâts échoue, par exemple : bordD_moyen_3barre, bureau, court, moyen, après le changement (1,99 × budget (borne haute ; moyenne 1,87), échoue) ; bordD_moyen_pireBreg, bureau, court, moyen, après le changement (1,84 × budget (borne haute ; moyenne 1,71), échoue) ; bordD_moyen_3barre, service client, court, moyen, après le changement (1,40 × budget (borne haute ; moyenne 1,28), échoue) ; bordD_moyen_1.5barre, bureau, court, moyen, après le changement (1,37 × budget (borne haute ; moyenne 1,25), échoue).
- B-régulier échoue, par exemple : bordD_moyen_3barre, bureau, court, moyen, après le changement (1,79 × budget (borne haute ; moyenne 1,65), échoue) ; bordD_moyen_pireBreg, bureau, court, moyen, après le changement (1,68 × budget (borne haute ; moyenne 1,55), échoue) ; bordD_moyen_1.5barre, bureau, court, moyen, après le changement (1,28 × budget (borne haute ; moyenne 1,16), échoue) ; bordD_moyen_3barre, service client, court, moyen, après le changement (1,23 × budget (borne haute ; moyenne 1,13), échoue).
- Alerte 4.5 (tests de résistance) : **oui**. mode rate10 : 0 cellule(s) hors budget contre 0 pour A½, pire cellule 0,57 contre 0,27 × budget ; mode rate10 : 0 cellule(s) hors budget contre 0 pour A¼, pire cellule 0,57 contre 0,33 × budget ; mode difficiles : 11 cellule(s) hors budget contre 0 pour A½, pire cellule 1,41 contre 0,73 × budget ; mode difficiles : 11 cellule(s) hors budget contre 0 pour A¼, pire cellule 1,41 contre 0,87 × budget ; mode retard10 : 0 cellule(s) hors budget contre 0 pour A½, pire cellule 0,84 contre 0,27 × budget ; mode retard10 : 0 cellule(s) hors budget contre 0 pour A¼, pire cellule 0,84 contre 0,42 × budget. À signaler à Otsoa avant de valider le choix.
- Lecture stricte de la section 1.5 (sans les agents bord qui dérivent, voir les choix d'implémentation) : règle retenue B-régulier (choix différent : à trancher par Otsoa).
- Classement lu à l'horizon long (couples délégables de l'horizon long) : B-tout (même choix).
- Volume de l'expérience réelle (section 4.6) : quelques milliers d'actions par agent, à confirmer avec le banc d'essai. L'horizon court (3 000 actions) est cette lecture : c'est lui qui sert au classement.

## La prédiction de la section 0, confrontée aux résultats

1. « B gagnera sur la charge, par construction » : **confirmée**. Meilleure B (B-régulier) : 63,8 ; meilleure A réglée sur la barre (A¼) : 78,0 validations hors lectures pour 100 actions (horizon court, couples délégables). A-dégâts : 64,4.
2. « À 3 000 actions, A n'atteint le palier 3 ni à enjeu moyen ni à enjeu fort » (A½ et A¼) : **confirmée** (part maximale du temps au palier 3 sur DUR, EXE, SOR, ARG : 0,000 %). A-dégâts, réglé autrement, atteint l'enjeu moyen : 78,5 % au plus.
3. « À 150 000 actions, A½ n'atteint toujours pas le palier 3 à enjeu fort » : **confirmée** (part maximale : 0,000 %).
4. « Avec quelques milliers d'actions par agent, aucune règle n'atteindra le palier 3 à enjeu fort » : **confirmée** (part maximale au court : 0,000 %).
5. « La comparaison s'y jouera à enjeu faible, et à enjeu moyen pour B-régulier » : règles qui atteignent le palier 3 à enjeu moyen au court : A-dégâts, B-régulier, B-tout.

Ce qu'E1 peut vraiment apprendre (section 0) :

- B-régulier et les agents bord (à son pire cas et au-delà) : 317 cellules sur 324 tiennent le budget ; pire cellule bordD_moyen_3barre, bureau, court, moyen, après le changement, 1,79 × budget (borne haute ; moyenne 1,65).
- B-tout et les agents bord (à son pire cas et au-delà) : 324 cellules sur 324 tiennent le budget ; pire cellule bordD_fort_3barre, bureau, long, fort, après le changement, 0,49 × budget (borne haute ; moyenne 0,43).
- Coût en garantie de B-régulier : un type au-dessus de la barre atteint le palier 3 jusqu'à 100,0 % des répétitions (A0d, DUR, bureau, long, phase apres).
- Coût en garantie de B-tout : un type au-dessus de la barre atteint le palier 3 jusqu'à 100,0 % des répétitions (A0d, EXE, bureau, long, phase apres).
- Coût en garantie de A-dégâts : un type au-dessus de la barre atteint le palier 3 jusqu'à 100,0 % des répétitions (A0d, DUR, bureau, long, phase apres).
- Coût au retrait (dérives silencieuses, types au palier 3 au changement) : erreurs passées avant le retrait, en moyenne : A½ 1,67 ; A¼ 1,57 ; A-dégâts 1,79 ; B-régulier 1,00 ; B-tout 1,06.
- Wald réglé sur les dégâts (A-dégâts) : ne tient pas le budget partout (20 cellule(s) hors budget) ; charge 64,4 contre 63,8 pour B-régulier.

## 1. Budget (mesure 1, éliminatoire)

Excès de dégâts pour 100 actions du flux, niveau par niveau, apparié avec « tout faire valider » ; intervalle retenu : l'union de l'intervalle normal à 95 % et de l'intervalle bootstrap (2 000 tirages), pour les événements rares. Verdict sur tout l'horizon et, pour les agents qui changent, sur la fenêtre qui va du changement à la fin. Épreuves jouées à blanc (décision d'Otsoa) ; la colonne « avec épreuves » les compte comme en deuxième passe, pour information.

| règle ou témoin | cellules | passe | échoue | indécis | hors budget au final | pire cellule (borne haute ÷ budget) | où | hors budget avec épreuves |
|--|--|--|--|--|--|--|--|--|
| A½ | 468 | 468 | 0 | 0 | 0 | 0,27 | A2, service client, long, faible | 45 |
| A¼ | 468 | 468 | 0 | 0 | 0 | 0,29 | bordD_faible_1.5barre, service client, court, faible, après le changement | 46 |
| A-dégâts | 468 | 441 | 12 | 15 | 20 | 1,99 | bordD_moyen_3barre, bureau, court, moyen, après le changement | 77 |
| B-régulier | 468 | 458 | 4 | 6 | 7 | 1,79 | bordD_moyen_3barre, bureau, court, moyen, après le changement | 56 |
| B-tout | 468 | 468 | 0 | 0 | 0 | 0,49 | bordD_fort_3barre, bureau, long, fort, après le changement | 45 |
| liste_fixe | 468 | 432 | 34 | 2 | 36 | 4,33 | A4, bureau, court, faible | — |
| tri_risque | 468 | 419 | 49 | 0 | 49 | 6,09 | A4, bureau, court, faible | — |
| trois_reussites | 468 | 265 | 193 | 10 | 203 | 404,63 | A4, service client, court, fort | — |
| oracle_p2 | 468 | 468 | 0 | 0 | 0 | 0,87 | bordD_faible_pireBreg, service client, court, fort, après le changement | — |
| tout_approuver | 468 | 252 | 205 | 11 | 216 | 862,17 | A4, service client, court, fort | — |
| hasard_A½ | 468 | 464 | 4 | 0 | 4 | 1,48 | bordD_faible_3barre, service client, long, faible, après le changement | — |
| hasard_A¼ | 468 | 462 | 4 | 2 | 6 | 1,50 | bordD_faible_3barre, service client, long, faible, après le changement | — |
| hasard_A-dégâts | 468 | 416 | 33 | 19 | 52 | 8,55 | A0d, service client, long, fort, après le changement | — |
| hasard_B-régulier | 468 | 425 | 34 | 9 | 43 | 7,62 | A0d, service client, long, fort, après le changement | — |
| hasard_B-tout | 468 | 450 | 15 | 3 | 18 | 3,01 | A0d, service client, long, fort, après le changement | — |

## 2. Charge (mesure 2)

Validations, corrections et doutes pour 100 actions hors lectures (sans la charge des épreuves, comptée à part), en moyenne sur les couples (agent, mélange) où au moins un type est sous la barre. Le détail couple par couple est dans `charges.csv`.

| règle | court : hors lectures | avec épreuves | totale | couples | long : hors lectures | avec épreuves | couples |
|--|--|--|--|--|--|--|--|
| A½ | 78,6 | 80,4 | 46,1 | 55 | 59,0 | 59,6 | 46 |
| A¼ | 78,0 | 79,8 | 45,8 | 55 | 57,5 | 58,2 | 46 |
| A-dégâts | 64,4 | 66,2 | 37,9 | 55 | 31,6 | 32,2 | 46 |
| B-régulier | 63,8 | 65,6 | 37,5 | 55 | 33,8 | 34,5 | 46 |
| B-tout | 72,7 | 74,5 | 42,7 | 55 | 45,0 | 45,7 | 46 |
| oracle_p2 | 40,9 | 40,9 | 24,3 | 55 | 31,1 | 31,1 | 46 |
| liste_fixe | 82,6 | 82,6 | 48,4 | 55 | 82,2 | 82,2 | 46 |
| tri_risque | 74,8 | 74,8 | 43,9 | 55 | 74,2 | 74,2 | 46 |
| trois_reussites | 15,9 | 15,9 | 9,8 | 55 | 11,9 | 11,9 | 46 |
| tout_valider | 100,0 | 100,0 | 58,1 | 55 | 100,0 | 100,0 | 46 |

Quelques couples de l'horizon court (hors lectures, sans épreuves) :

| agent | mélange | A½ | A¼ | A-dégâts | B-régulier | B-tout | oracle | liste fixe | tri |
|--|--|--|--|--|--|--|--|--|--|
| A1 | bureau | 62,2 | 61,7 | 50,8 | 49,7 | 55,3 | 47,4 | 72,8 | 61,9 |
| A1 | service_client | 90,3 | 89,2 | 74,4 | 77,0 | 85,9 | 83,3 | 91,6 | 86,6 |
| A2 | bureau | 68,9 | 68,8 | 63,8 | 61,0 | 65,1 | 47,6 | 72,8 | 61,9 |
| A2 | service_client | 91,3 | 90,8 | 87,2 | 86,4 | 88,1 | 83,3 | 91,6 | 86,6 |
| A3 | bureau | 75,6 | 75,7 | 74,8 | 70,5 | 74,5 | 60,3 | 72,8 | 61,9 |
| A3 | service_client | 92,7 | 92,7 | 89,7 | 88,4 | 90,6 | 83,4 | 91,6 | 86,6 |
| A5 | bureau | 69,2 | 69,0 | 63,7 | 61,0 | 65,4 | 47,6 | 72,8 | 61,9 |
| A5 | service_client | 91,4 | 90,8 | 87,3 | 86,4 | 88,2 | 83,3 | 91,6 | 86,6 |

## 3. Réussite au sens de la décision 3, et part du gain de l'oracle (mesures 3 et 4)

Pour chaque couple (horizon, mélange, agent) : la règle tient-elle le budget dans ce couple, et demande-t-elle moins de validations hors lectures que la liste fixe et que le tri par le risque (différence appariée, intervalle à 95 % tout sous 0) ? Un témoin qui dépasse le budget dans le couple compte comme battu. Part du gain de l'oracle : (100 − charge) ÷ (100 − charge de l'oracle avec palier 2), seulement si l'oracle gagne au moins un point.

| règle | horizon | couples | réussite (sans épreuves) | réussite (avec épreuves) | part du gain de l'oracle (médiane) | étendue |
|--|--|--|--|--|--|--|
| A½ | court | 62 | 28 | 28 | 0,45 | 0,04 à 0,72 |
| A½ | long | 46 | 45 | 43 | 0,63 | 0,29 à 0,96 |
| A¼ | court | 62 | 31 | 31 | 0,46 | 0,04 à 0,73 |
| A¼ | long | 46 | 44 | 43 | 0,65 | 0,29 à 0,96 |
| A-dégâts | court | 62 | 40 | 38 | 0,60 | 0,26 à 1,53 |
| A-dégâts | long | 46 | 37 | 35 | 0,99 | 0,68 à 1,89 |
| B-régulier | court | 62 | 51 | 41 | 0,68 | 0,32 à 1,38 |
| B-régulier | long | 46 | 46 | 43 | 0,95 | 0,68 à 1,65 |
| B-tout | court | 62 | 49 | 45 | 0,54 | 0,13 à 0,85 |
| B-tout | long | 46 | 44 | 43 | 0,81 | 0,57 à 1,06 |

## 5. Retrait (mesure 5)

Agents qui se dégradent (A6a, changement annoncé ; A6b, A0d et agents bord qui dérivent, en silence), types dont le nouveau taux dépasse la barre et qui sont au palier 3 au moment du changement. Pour chaque règle : délai médian jusqu'à la perte du palier 3, en actions du type (pire type), part jamais retirée avant la fin (pire type), erreurs passées pendant le délai (moyenne) ; « — » : aucun type au palier 3 au changement. Détail, 95e centile et part du temps au palier 3 après le changement : `retrait.csv`.

| agent | horizon | A½ : délai ; jamais ; erreurs | A¼ : délai ; jamais ; erreurs | A-dégâts : délai ; jamais ; erreurs | B-régulier : délai ; jamais ; erreurs | B-tout : délai ; jamais ; erreurs |
|--|--|--|--|--|--|--|
| A6a | court | 0 ; 0 % ; 0,00 | 0 ; 0 % ; 0,00 | 0 ; 0 % ; 0,00 | 0 ; 0 % ; 0,00 | 0 ; 0 % ; 0,00 |
| A6b | court | 9 ; 0 % ; 2,00 | 22 ; 2 % ; 1,46 | 26 ; 23 % ; 2,33 | 14 ; 2 % ; 1,05 | 9 ; 1 % ; 1,06 |
| bord qui dérive, faible | court | 25 ; 0 % ; 1,20 | 41 ; 2 % ; 1,50 | 61 ; 31 % ; 2,56 | 21 ; 2 % ; 1,06 | 21 ; 2 % ; 1,06 |
| bord qui dérive, fort | court | — | — | — | — | — |
| bord qui dérive, moyen | court | — | — | > fin ; 54 % ; 0,70 | > fin ; 56 % ; 0,75 | — |
| A0d | long | 165 ; 0 % ; 1,10 | 175 ; 0 % ; 1,09 | 170 ; 0 % ; 1,05 | 170 ; 0 % ; 1,05 | 175 ; 0 % ; 1,05 |
| A6b | long | 14 ; 0 % ; 1,92 | 14 ; 0 % ; 1,75 | 28 ; 0 % ; 2,73 | 8 ; 0 % ; 1,05 | 7 ; 0 % ; 1,06 |
| bord qui dérive, faible | long | 46 ; 0 % ; 2,20 | 46 ; 0 % ; 2,16 | 61 ; 0 % ; 2,86 | 21 ; 0 % ; 1,06 | 21 ; 0 % ; 1,06 |
| bord qui dérive, fort | long | — | — | 1 945 ; 19 % ; 1,02 | 1 945 ; 19 % ; 1,02 | 2 022 ; 21 % ; 1,03 |
| bord qui dérive, moyen | long | 200 ; 0 % ; 1,07 | 200 ; 0 % ; 1,07 | 200 ; 3 % ; 1,06 | 200 ; 3 % ; 1,06 | 200 ; 3 % ; 1,06 |

## 6. Garantie « au plus 5 fois sur 100 » (mesure 6)

Part des répétitions où un type dont le vrai taux dépasse la barre atteint le palier 3 (agents constants : tout l'horizon ; agents qui changent : avant, et après le changement pour une nouvelle promotion). Intervalle de Wilson ; « échoue » si l'intervalle est tout au-dessus de 5 %.

| règle | horizon | couples (type au-dessus de la barre) | au-dessus de 5 % | indécis | pire part | où |
|--|--|--|--|--|--|--|
| A½ | court | 234 | 7 | 0 | 57,0 % [50,1 ; 63,7] | bordD_faible_1.5barre, ECR, bureau, apres |
| A½ | long | 116 | 9 | 107 | 40,0 % [26,3 ; 55,4] | bordD_faible_1.5barre, MSG, bureau, apres |
| A¼ | court | 234 | 10 | 2 | 35,0 % [28,7 ; 41,8] | bordD_faible_1.5barre, ECR, bureau, apres |
| A¼ | long | 116 | 14 | 102 | 30,0 % [18,1 ; 45,4] | A6b, ECR, service_client, apres |
| A-dégâts | court | 234 | 75 | 14 | 99,0 % [96,4 ; 99,7] | bord_moyen_1.5barre, DUR, service_client, tout |
| A-dégâts | long | 116 | 91 | 25 | 100,0 % [91,2 ; 100,0] | A0d, DUR, bureau, apres |
| B-régulier | court | 234 | 86 | 11 | 100,0 % [98,1 ; 100,0] | A3, ECR, bureau, tout |
| B-régulier | long | 116 | 93 | 23 | 100,0 % [91,2 ; 100,0] | A0d, DUR, bureau, apres |
| B-tout | court | 234 | 50 | 7 | 100,0 % [98,1 ; 100,0] | bord_faible_1.5barre, ECR, service_client, tout |
| B-tout | long | 116 | 79 | 37 | 100,0 % [91,2 ; 100,0] | A0d, EXE, bureau, apres |

## 7. Volume pour mériter (mesure 7)

Horizon long, agent A0 (1 sur 10 000 partout) : actions du flux avant le premier palier 3, médiane et 95e centile, et part des répétitions qui ne l'atteignent jamais ; entre parenthèses, le volume analytique d'un agent sans erreur (relecture, I10). Les autres agents constants de l'horizon long sont dans `volume.csv`.

| mélange | type | A½ : médiane / 95e centile ; jamais (analytique) | A¼ : médiane / 95e centile ; jamais (analytique) | A-dégâts : médiane / 95e centile ; jamais (analytique) | B-régulier : médiane / 95e centile ; jamais (analytique) | B-tout : médiane / 95e centile ; jamais (analytique) |
|--|--|--|--|--|--|--|
| bureau | ECR | 1 633 / 1 783 ; 0 % (1 621) | 1 070 / 1 260 ; 0 % (1 088) | 488 / 588 ; 0 % (498) | 98 / 160 ; 0 % (105) | 283 / 343 ; 0 % (288) |
| bureau | DUR | 23 546 / 34 892 ; 0 % (23 500) | 15 723 / 26 090 ; 0 % (15 684) | 1 022 / 1 185 ; 0 % (1 053) | 1 521 / 1 716 ; 0 % (1 553) | 4 230 / 6 998 ; 0 % (4 197) |
| bureau | EXE | 24 116 / 48 990 ; 0 % (23 500) | 15 877 / 36 075 ; 0 % (15 684) | 1 046 / 1 213 ; 0 % (1 053) | 1 529 / 1 735 ; 0 % (1 553) | 4 144 / 8 313 ; 0 % (4 197) |
| bureau | MSG | 4 070 / 4 590 ; 0 % (4 053) | 2 812 / 3 252 ; 0 % (2 719) | 1 288 / 1 506 ; 0 % (1 246) | 270 / 351 ; 0 % (263) | 740 / 946 ; 0 % (719) |
| bureau | SOR | jamais / jamais ; 100 % (166 809) | jamais / jamais ; 62 % (111 217) | 8 218 / 15 059 ; 0 % (8 235) | 10 940 / 18 705 ; 0 % (10 976) | 29 924 / 51 124 ; 0 % (29 814) |
| bureau | ARG | jamais / jamais ; 100 % (400 342) | jamais / jamais ; 100 % (266 921) | 19 887 / 32 367 ; 0 % (19 763) | 26 559 / 40 245 ; 0 % (26 342) | 72 036 / jamais ; 8 % (71 553) |
| service_client | ECR | 1 787 / 2 139 ; 0 % (1 811) | 1 206 / 1 609 ; 0 % (1 221) | 512 / 692 ; 0 % (526) | 95 / 253 ; 0 % (126) | 304 / 445 ; 0 % (316) |
| service_client | DUR | 13 038 / 24 373 ; 0 % (12 937) | 8 692 / 20 864 ; 0 % (8 626) | 624 / 689 ; 0 % (616) | 854 / 972 ; 0 % (853) | 2 317 / 3 193 ; 0 % (2 311) |
| service_client | EXE | 128 940 / jamais ; 22 % (129 368) | 86 766 / jamais ; 8 % (86 263) | 6 128 / 6 962 ; 0 % (6 158) | 8 455 / 9 555 ; 0 % (8 526) | 23 185 / 26 052 ; 0 % (23 105) |
| service_client | MSG | 3 047 / 3 357 ; 0 % (3 018) | 2 041 / 2 269 ; 0 % (2 035) | 869 / 1 109 ; 0 % (877) | 198 / 319 ; 0 % (211) | 524 / 752 ; 0 % (526) |
| service_client | SOR | jamais / jamais ; 100 % (227 667) | jamais / jamais ; 100 % (151 781) | 11 365 / 23 497 ; 0 % (11 263) | 15 049 / 28 374 ; 0 % (14 974) | 41 320 / 96 092 ; 2 % (40 693) |
| service_client | ARG | jamais / jamais ; 100 % (243 929) | jamais / jamais ; 100 % (162 622) | 12 157 / 18 644 ; 0 % (12 068) | 16 210 / 32 215 ; 0 % (16 043) | 66 333 / 119 761 ; 2 % (43 600) |

## 8. Bornes de la règle B sur deux suites piège (mesure 8)

Référence `RegleUnTypeB`, épreuves toujours réussies. « N réussites puis une erreur » : borne 0,95 ÷ (N + 1) ; à enjeu moyen ou fort, l'allongement de la pièce 7.3 donne 0,95 ÷ (⌈1,25 N⌉ + 1). « Rafale » : N réussites puis des erreurs, constatées chacune avec la probabilité d = 0,95, jusqu'au retrait : environ 0,95 ÷ (d × N + 1). Dernière colonne : rapport à l'excès par action qu'autorise le budget (0,95 × barre).

| mélange | règle | niveau | N | piège 1 : mesuré (attendu) | rafale : mesurée (attendue) | piège 1 ÷ budget | rafale ÷ budget |
|--|--|--|--|--|--|--|--|
| bureau | B-régulier | faible | 15 | 0,0594 (0,0594) | 0,0621 (0,0623) | 2,49 | 2,61 |
| bureau | B-régulier | moyen | 118 | 0,0064 (0,00638) | 0,0066 (0,00671) | 2,05 | 2,11 |
| bureau | B-régulier | fort | 1001 | 0,000761 (0,000758) | 0,000782 (0,000798) | 2,07 | 2,13 |
| bureau | B-tout | faible | 41 | 0,0226 (0,0226) | 0,0237 (0,0238) | 0,95 | 1,00 |
| bureau | B-tout | moyen | 319 | 0,00238 (0,00237) | 0,00251 (0,0025) | 0,76 | 0,80 |
| bureau | B-tout | fort | 2719 | 0,000281 (0,000279) | 0,000306 (0,000294) | 0,76 | 0,83 |
| service_client | B-régulier | faible | 6 | 0,136 (0,136) | 0,144 (0,142) | 2,17 | 2,30 |
| service_client | B-régulier | moyen | 162 | 0,00468 (0,00466) | 0,00485 (0,0049) | 2,06 | 2,13 |
| service_client | B-régulier | fort | 1707 | 0,000447 (0,000445) | 0,000465 (0,000468) | 2,07 | 2,16 |
| service_client | B-tout | faible | 15 | 0,0594 (0,0594) | 0,0619 (0,0623) | 0,95 | 0,99 |
| service_client | B-tout | moyen | 439 | 0,00173 (0,00173) | 0,00182 (0,00182) | 0,76 | 0,80 |
| service_client | B-tout | fort | 4639 | 0,000164 (0,000164) | 0,000168 (0,000172) | 0,76 | 0,78 |

## 9. Tests de résistance (mesure 9, hors du choix)

Le contrôle automatique rate 10 % des erreurs au hasard (graine à part), ou toutes les erreurs des cas difficiles (pire cas), ou constate 10 actions du type après l'action. Une erreur ratée compte comme une réussite. Avec un constat 100 actions plus tard, la borne (1 + k) ÷ (N + 1) dépasse 1 à enjeu faible (N = 15 ou 41) : elle est vide, ce qui est signalé sans être simulé.

| règle | base : hors budget ; pire cellule (× budget) | rate10 : hors budget ; pire cellule (× budget) | difficiles : hors budget ; pire cellule (× budget) | retard10 : hors budget ; pire cellule (× budget) |
|--|--|--|--|--|
| A½ | 0 / 468 ; pire 0,27 | 0 / 468 ; pire 0,27 | 0 / 468 ; pire 0,73 | 0 / 468 ; pire 0,27 |
| A¼ | 0 / 468 ; pire 0,29 | 0 / 468 ; pire 0,33 | 0 / 468 ; pire 0,87 | 0 / 468 ; pire 0,42 |
| A-dégâts | 20 / 468 ; pire 1,99 | 39 / 468 ; pire 2,07 | 115 / 468 ; pire 4,11 | 29 / 468 ; pire 2,20 |
| B-régulier | 7 / 468 ; pire 1,79 | 19 / 468 ; pire 1,86 | 104 / 468 ; pire 2,78 | 14 / 468 ; pire 1,79 |
| B-tout | 0 / 468 ; pire 0,49 | 0 / 468 ; pire 0,57 | 11 / 468 ; pire 1,41 | 0 / 468 ; pire 0,84 |

## 10. Retrait comparé au meilleur détecteur possible (mesure 10)

Pour chaque règle et chaque type devenu mauvais en silence (A6b, A0d, agents bord qui dérivent) : fréquence mesurée des fausses alertes avant le changement (actions au palier 3 par perte du palier 3), délai moyen mesuré du retrait, et délai du CUSUM optimal (Page, mêmes taux avant et après) réglé sur la même fréquence de fausses alertes. Rapport > 1 : la règle est plus lente que le meilleur détecteur.

| règle | agent | mélange | horizon | type | actions entre fausses alertes | délai mesuré | délai du CUSUM | rapport |
|--|--|--|--|--|--|--|--|--|
| A-dégâts | A0d | bureau | long | DUR | 16 733 | 194 | 220 | 0,88 |
| A-dégâts | A0d | bureau | long | EXE | 8 342 | 224 | 167 | 1,34 |
| A-dégâts | A0d | bureau | long | SOR | 14 095 | 204 | 216 | 0,95 |
| A-dégâts | A0d | bureau | long | ARG | 9 971 | 208 | 199 | 1,04 |
| A-dégâts | A0d | service_client | long | DUR | 10 464 | 198 | 209 | 0,95 |
| A-dégâts | A0d | service_client | long | EXE | 9 018 | 250 | 181 | 1,38 |
| A-dégâts | A0d | service_client | long | SOR | 13 469 | 213 | 215 | 0,99 |
| A-dégâts | A0d | service_client | long | ARG | 7 514 | 191 | 151 | 1,27 |
| A-dégâts | A6b | bureau | long | ECR | 183 | 19 | 20 | 0,94 |
| A-dégâts | A6b | bureau | long | DUR | 54 | 6 | 11 | 0,56 |
| A-dégâts | A6b | bureau | long | EXE | 52 | 5 | 10 | 0,48 |
| A-dégâts | A6b | bureau | long | MSG | 182 | 21 | 20 | 1,06 |
| A-dégâts | A6b | service_client | long | ECR | 504 | 40 | 31 | 1,31 |
| A-dégâts | A6b | service_client | long | MSG | 466 | 29 | 30 | 0,95 |
| A-dégâts | A6b | bureau | court | ECR | 138 | 24 | 17 | 1,43 |
| A-dégâts | A6b | bureau | court | DUR | 65 | 11 | 11 | 0,97 |
| A-dégâts | A6b | bureau | court | EXE | 50 | 13 | 10 | 1,26 |
| A-dégâts | A6b | bureau | court | MSG | 86 | 14 | 13 | 1,11 |
| A-dégâts | A6b | service_client | court | ECR | 258 | 27 | 24 | 1,14 |
| A-dégâts | A6b | service_client | court | DUR | 44 | 15 | 9 | 1,72 |
| A-dégâts | A6b | service_client | court | MSG | 100 | 19 | 14 | 1,35 |
| A-dégâts | bordD_fort_1.5barre | bureau | long | SOR | 14 095 | 1 785 | 2 027 | 0,88 |
| A-dégâts | bordD_fort_1.5barre | bureau | long | ARG | 9 971 | 1 137 | 1 718 | 0,66 |
| A-dégâts | bordD_fort_1.5barre | service_client | long | SOR | 13 469 | 2 537 | 3 513 | 0,72 |
| A-dégâts | bordD_fort_1.5barre | service_client | long | ARG | 7 514 | 2 361 | 2 208 | 1,07 |
| A-dégâts | bordD_fort_3barre | bureau | long | SOR | 14 095 | 1 070 | 975 | 1,10 |
| A-dégâts | bordD_fort_3barre | bureau | long | ARG | 9 971 | 879 | 859 | 1,02 |
| A-dégâts | bordD_fort_3barre | service_client | long | SOR | 13 469 | 1 205 | 1 683 | 0,72 |
| A-dégâts | bordD_fort_3barre | service_client | long | ARG | 7 514 | 1 683 | 1 104 | 1,52 |
| A-dégâts | bordD_fort_pireBreg | bureau | long | SOR | 14 095 | 1 373 | 1 142 | 1,20 |
| A-dégâts | bordD_fort_pireBreg | bureau | long | ARG | 9 971 | 874 | 999 | 0,87 |
| A-dégâts | bordD_fort_pireBreg | service_client | long | SOR | 13 466 | 1 263 | 1 972 | 0,64 |
| A-dégâts | bordD_fort_pireBreg | service_client | long | ARG | 7 514 | 1 819 | 1 284 | 1,42 |
| A-dégâts | bordD_moyen_1.5barre | bureau | long | DUR | 16 733 | 194 | 223 | 0,87 |
| A-dégâts | bordD_moyen_1.5barre | bureau | long | EXE | 8 342 | 227 | 169 | 1,34 |
| A-dégâts | bordD_moyen_1.5barre | service_client | long | DUR | 10 464 | 270 | 292 | 0,93 |
| A-dégâts | bordD_moyen_1.5barre | service_client | long | EXE | 9 018 | 287 | 251 | 1,14 |
| A-dégâts | bordD_moyen_1.5barre | service_client | court | DUR | 11 535 | 143 | 296 | 0,48 |
| A-dégâts | bordD_moyen_3barre | bureau | long | DUR | 16 733 | 92 | 110 | 0,84 |
| A-dégâts | bordD_moyen_3barre | bureau | long | EXE | 8 342 | 103 | 85 | 1,22 |
| A-dégâts | bordD_moyen_3barre | service_client | long | DUR | 10 464 | 151 | 146 | 1,04 |
| A-dégâts | bordD_moyen_3barre | service_client | long | EXE | 9 018 | 179 | 126 | 1,42 |
| A-dégâts | bordD_moyen_3barre | service_client | court | DUR | 11 535 | 108 | 147 | 0,74 |
| A-dégâts | bordD_moyen_pireBreg | bureau | long | DUR | 16 733 | 107 | 129 | 0,83 |
| A-dégâts | bordD_moyen_pireBreg | bureau | long | EXE | 8 342 | 115 | 99 | 1,15 |
| A-dégâts | bordD_moyen_pireBreg | service_client | long | DUR | 10 464 | 168 | 171 | 0,98 |
| A-dégâts | bordD_moyen_pireBreg | service_client | long | EXE | 9 018 | 201 | 147 | 1,37 |
| A-dégâts | bordD_moyen_pireBreg | service_client | court | DUR | 11 535 | 113 | 173 | 0,66 |
| A¼ | A0d | bureau | long | DUR | 16 799 | 196 | 220 | 0,89 |
| A¼ | A0d | bureau | long | EXE | 8 727 | 216 | 175 | 1,24 |
| A¼ | A0d | service_client | long | DUR | 12 341 | 201 | 213 | 0,94 |
| A¼ | A6b | service_client | long | ECR | 130 | 16 | 16 | 1,01 |
| A¼ | A6b | service_client | long | MSG | 115 | 14 | 15 | 0,93 |
| A¼ | A6b | bureau | court | ECR | 62 | 32 | 11 | 2,83 |
| A¼ | A6b | service_client | court | ECR | 68 | 14 | 12 | 1,16 |
| A¼ | bordD_faible_1.5barre | bureau | court | ECR | 12 038 | 49 | 28 | 1,76 |
| A¼ | bordD_faible_3barre | bureau | court | ECR | 12 038 | 24 | 14 | 1,72 |
| A¼ | bordD_faible_pireBreg | bureau | court | ECR | 12 038 | 28 | 17 | 1,68 |
| A¼ | bordD_moyen_1.5barre | bureau | long | DUR | 16 799 | 196 | 223 | 0,88 |
| A¼ | bordD_moyen_1.5barre | bureau | long | EXE | 8 727 | 220 | 177 | 1,24 |

(153 lignes de plus dans `cusum.csv`.)

## 11. Certification (mesure 11), barres, N, étalonnage d'A-dégâts

| mélange | niveau | barre | N B-régulier | N B-tout | ⌈1,25 N⌉ B-rég. | ⌈1,25 N⌉ B-tout | pm3 d'A-dégâts |
|--|--|--|--|--|--|--|--|
| bureau | faible | 1 sur 39,9 | 15 | 41 | 19 | 52 | 1 sur 12,7 (3,14 barre) |
| bureau | moyen | 1 sur 304,0 | 118 | 319 | 148 | 399 | 1 sur 14,3 (21,23 barre) |
| bureau | fort | 1 sur 2 584,0 | 1001 | 2719 | 1252 | 3399 | 1 sur 128,1 (20,17 barre) |
| service_client | faible | 1 sur 15,2 | 6 | 15 | 8 | 19 | 1 sur 4,9 (3,11 barre) |
| service_client | moyen | 1 sur 418,0 | 162 | 439 | 203 | 549 | 1 sur 20,5 (20,44 barre) |
| service_client | fort | 1 sur 4 408,0 | 1707 | 4639 | 2134 | 5799 | 1 sur 218,8 (20,15 barre) |

Réussites sans erreur pour établir que le taux est sous la barre (risque 5 %) :

| mélange | niveau | exact : (1 − barre)^n ≤ 0,05 | règle de trois, 3 ÷ barre |
|--|--|--|--|
| bureau | faible | 119 | 120 |
| bureau | moyen | 910 | 912 |
| bureau | fort | 7 740 | 7 752 |
| service_client | faible | 45 | 46 |
| service_client | moyen | 1 251 | 1 254 |
| service_client | fort | 13 204 | 13 224 |

Étalonnage d'A-dégâts (`etalonnage_e1.py`) : pm3 tel que l'excès stationnaire du pire agent régulier égale le budget, pb3 = pm3 ÷ 2 ; simulation d'un type isolé, fidèle au moteur ; contrôle hors échantillon à ±0,5 %.

| mélange | niveau | pm3 | pm3 ÷ barre | pire q ÷ barre | excès max ÷ budget | itérations |
|--|--|--|--|--|--|--|
| bureau | faible | 0.078734 | 3,14 | 1,42 | 0,9985 | 2 |
| bureau | moyen | 0.069835 | 21,23 | 2,53 | 1,0010 | 3 |
| bureau | fort | 0.0078039 | 20,17 | 2,67 | 1,0003 | 2 |
| service_client | faible | 0.20476 | 3,11 | 1,42 | 1,0018 | 2 |
| service_client | moyen | 0.048891 | 20,44 | 2,55 | 0,9975 | 2 |
| service_client | fort | 0.004571 | 20,15 | 2,74 | 0,9995 | 2 |

## Choix d'implémentation et points du plan tranchés

- Chemin v2 intact : aucun fichier de la deuxième passe n'est modifié ; E1 vit dans config_e1.py, regle_e1.py, etalonnage_e1.py, executer_e1.py, ecrire_resultats_e1.py. Le moteur E1, réglé comme la v2, refait exactement le moteur v2 (test). Interrupteurs d'E1 : `lec_autonome` (règles et témoins) et `lec_sans_effet` (comptabilité).
- Le plan (1.5) définit les agents bord comme constants, mais la mesure 5 parle des « agents bord qui changent » et la relecture (I9) attend l'effet de la fenêtre après changement « fort avec les agents bord ». Lecture retenue, la plus prudente : chaque agent bord a aussi une variante qui part du taux d'A0 et dérive en silence vers la valeur bord au milieu de l'horizon (bordD_*). Elles entrent dans le critère éliminatoire ; RESULTATS_E1.md donne aussi le choix sans elles.
- Classement (4.2) : les couples sont ceux de l'horizon court (agent × mélange), qui est aussi le volume de l'expérience réelle (4.6) ; le classement à l'horizon long est donné à part. La charge de classement est hors lectures et sans la charge des épreuves (« comptée à part », décision 6) ; la version avec épreuves est donnée.
- Prudence (4.3) : marge = 1 − (borne haute de l'excès ÷ budget) dans la pire cellule de la règle (toutes cellules, après relance) ; égalité de prudence à 0,001 près, puis simplicité : B-tout, B-régulier, A½, A¼, A-dégâts.
- Intervalles : l'union de l'intervalle normal et de l'intervalle bootstrap (percentile, 2 000 tirages), pour toutes les cellules : c'est plus prudent que l'un ou l'autre (une cellule indécise est relancée, puis compte comme un échec).
- Règle B, points laissés ouverts par le plan : la consigne modifiée divise le compteur par deux (⌊c/2⌋, soit ⌊N/2⌋ au palier 3, comme écrit dans le plan) ; le compteur est plafonné à la longueur exigée (⌈1,25 N⌉ pendant une montée allongée, N sinon) ; l'allongement ne se cumule pas ; après un changement de modèle, plus d'allongement (nouvel agent ; les erreurs deviennent des épreuves) ; sous le palier 3, le palier 2 suit le score de Wald v2.
- Tests de résistance : une variante d'épreuve est jugée par le même contrôle (10 % de ses erreurs ratées ; toutes, dans le pire cas, puisque les variantes sont des cas difficiles) ; avec le constat différé, l'épreuve est jugée aussitôt, seules les preuves des actions ordinaires arrivent 10 actions du type plus tard.
- Garantie après un changement : seules les nouvelles promotions au palier 3 comptent (comme en v2) ; un type déjà au palier 3 au changement relève du retrait (mesure 5).
- Alerte 4.5 : critère fixé avant le lancement (plus de cellules hors budget qu'une autre survivante dans un mode, ou une pire cellule au moins 1,25 fois plus haute et au moins à la moitié du budget).
- Pannes injectées : non simulées (décision 3). A8 est vide à l'horizon court (aucune règle n'atteint SOR au palier 3 avant t = 1 500) ; il n'y a pas d'A8 à l'horizon long dans le plan.

## Figures

- `fig1_charge_budget.png`
- `fig2_garantie.png`
- `fig3_volume.png`
