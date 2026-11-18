# Exploration E1 · résultats

> Exploration annoncée comme telle (`PLAN_EXPLORATION_E1.md`, révision 1). Elle ne change pas le verdict de la deuxième passe (`resultats/`). Écrit le 04/11/2026 à 19:20 par `ecrire_resultats_e1.py`, à partir des CSV de ce dossier.
> Horizons : court 3000 actions × 5000 répétitions ; long 150000 actions × 1000 répétitions (blocs de 200). Graine maîtresse 20261104. 108 tâches, 3 relances, 23,1 min. Gel : `GEL_E1.txt`.

## En tête : la règle retenue (section 4, appliquée mécaniquement)

Lecture : amendement E1-a : budget sur tout l'horizon, fenêtre après le changement jugée à l'horizon long seulement, au plus une erreur constatée avant le retrait (décision 5).

**Règle retenue : B-régulier.** Charge hors lectures la plus basse parmi les règles qui tiennent le budget.

| règle | tient le budget et la décision 5 | charge hors lectures (court, couples délégables) | couples | marge de la pire cellule | pire cellule | cellules relancées |
|--|--|--|--|--|--|--|
| A½ | oui | 78,6 | 55 | 0,739 | A2, service client, long, faible | 0 |
| A¼ | oui | 78,0 | 55 | 0,770 | A2, service client, long, faible | 0 |
| A-dégâts | non (6 cellule(s) de budget) | 64,4 | 55 | −0,166 | bordD_fort_3barre, bureau, long, fort, après le changement | 3 |
| B-régulier | oui | 63,8 | 55 | 0,049 | bordD_faible_pireBreg, bureau, long, faible, après le changement | 0 |
| B-tout | oui | 72,7 | 55 | 0,545 | bordD_fort_1.5barre, bureau, long, fort, après le changement | 0 |

- A-dégâts échoue au budget, par exemple : bordD_fort_3barre, bureau, long, fort, après le changement (1,17 × budget (borne haute ; moyenne 1,15), échoue) ; bordD_fort_pireBreg, bureau, long, fort, après le changement (1,15 × budget (borne haute ; moyenne 1,13), échoue) ; bordD_fort_3barre, service client, long, fort, après le changement (1,15 × budget (borne haute ; moyenne 1,13), échoue) ; bordD_fort_pireBreg, service client, long, fort, après le changement (1,12 × budget (borne haute ; moyenne 1,10), échoue).
- Alerte 4.5 (tests de résistance) : **oui**. mode rate10 : 9 échec(s) contre 0 pour A½, pire cellule 1,05 contre 0,27 × budget ; mode rate10 : 9 échec(s) contre 0 pour A¼, pire cellule 1,05 contre 0,25 × budget ; mode rate10 : 9 échec(s) contre 0 pour B-tout, pire cellule 1,05 contre 0,51 × budget ; mode difficiles : 75 échec(s) contre 0 pour A½, pire cellule 2,26 contre 0,67 × budget ; mode difficiles : 75 échec(s) contre 0 pour A¼, pire cellule 2,26 contre 0,58 × budget ; mode difficiles : 75 échec(s) contre 6 pour B-tout, pire cellule 2,26 contre 1,22 × budget ; mode retard10 : 48 échec(s) contre 14 pour A½, pire cellule 0,95 contre 0,26 × budget ; mode retard10 : 48 échec(s) contre 16 pour A¼, pire cellule 0,95 contre 0,23 × budget ; mode retard10 : 48 échec(s) contre 36 pour B-tout, pire cellule 0,95 contre 0,46 × budget. À signaler à Otsoa avant de valider le choix.
- Rapporté à part (lecture d'avant l'amendement E1-a : fenêtre après le changement éliminatoire aux deux horizons, sans le critère de la décision 5) : règle retenue B-tout (choix différent). L'amendement E1-a a été décidé par Otsoa après l'essai de vérification à petite taille (`explorations/essai_e1_phase1/`, chiffres sans valeur), sur le principe de la décision 5 : à l'horizon court, la fenêtre après la dérive fait 1 500 actions, et le budget moyen n'y permet que 0,75 erreur, si bien que l'erreur unique acceptée par la décision 5 suffisait à éliminer une règle.
  | règle | tient (ancienne lecture) | cellules hors budget |
  |--|--|--|
  | A½ | oui | 0 |
  | A¼ | oui | 0 |
  | A-dégâts | non | 16 |
  | B-régulier | non | 7 |
  | B-tout | oui | 0 |
- Classement lu à l'horizon long (couples délégables de l'horizon long) : B-régulier (même choix).
- Volume de l'expérience réelle (section 4.6) : quelques milliers d'actions par agent, à confirmer avec le banc d'essai. L'horizon court (3 000 actions) est cette lecture : c'est lui qui sert au classement.

## La prédiction de la section 0, confrontée aux résultats

1. « B gagnera sur la charge, par construction » : **confirmée**. Meilleure B (B-régulier) : 63,8 ; meilleure A réglée sur la barre (A¼) : 78,0 validations hors lectures pour 100 actions (horizon court, couples délégables). A-dégâts : 64,4.
2. « À 3 000 actions, A n'atteint le palier 3 ni à enjeu moyen ni à enjeu fort » (A½ et A¼) : **confirmée** (part maximale du temps au palier 3 sur DUR, EXE, SOR, ARG : 0,000 %). A-dégâts, réglé autrement, atteint l'enjeu moyen : 78,3 % au plus.
3. « À 150 000 actions, A½ n'atteint toujours pas le palier 3 à enjeu fort » : **confirmée** (part maximale : 0,000 %).
4. « Avec quelques milliers d'actions par agent, aucune règle n'atteindra le palier 3 à enjeu fort » : **confirmée** (part maximale au court : 0,000 %).
5. « La comparaison s'y jouera à enjeu faible, et à enjeu moyen pour B-régulier » : règles qui atteignent le palier 3 à enjeu moyen au court : A-dégâts, B-régulier, B-tout.

Ce qu'E1 peut vraiment apprendre (section 0) :

- B-régulier et les agents bord (à son pire cas et au-delà) : 270 cellules sur 270 tiennent le budget ; pire cellule bordD_faible_pireBreg, bureau, long, faible, après le changement, 0,95 × budget (borne haute ; moyenne 0,95).
- B-tout et les agents bord (à son pire cas et au-delà) : 270 cellules sur 270 tiennent le budget ; pire cellule bordD_fort_1.5barre, bureau, long, fort, après le changement, 0,45 × budget (borne haute ; moyenne 0,44).
- Coût en garantie de B-régulier : un type au-dessus de la barre atteint le palier 3 jusqu'à 100,0 % des répétitions (A0d, DUR, bureau, long, phase apres).
- Coût en garantie de B-tout : un type au-dessus de la barre atteint le palier 3 jusqu'à 100,0 % des répétitions (A1, DUR, bureau, long, phase tout).
- Coût en garantie de A-dégâts : un type au-dessus de la barre atteint le palier 3 jusqu'à 100,0 % des répétitions (A0d, DUR, bureau, long, phase apres).
- Coût au retrait (dérives silencieuses, types au palier 3 au changement) : erreurs passées avant le retrait, en moyenne : A½ 1,65 ; A¼ 1,54 ; A-dégâts 1,77 ; B-régulier 0,99 ; B-tout 1,04.
- Wald réglé sur les dégâts (A-dégâts) : ne tient pas le budget partout (6 cellule(s) hors budget) ; charge 64,4 contre 63,8 pour B-régulier.

## 1. Budget (mesure 1, éliminatoire)

Excès de dégâts pour 100 actions du flux, niveau par niveau, apparié avec « tout faire valider » ; intervalle retenu : l'union de l'intervalle normal à 95 % et de l'intervalle bootstrap (2 000 tirages), pour les événements rares. Amendement E1-a : le budget se lit sur tout l'horizon ; la fenêtre qui va du changement à la fin n'est éliminatoire qu'à l'horizon long ; à l'horizon court, elle est mesurée et rapportée (deuxième tableau), sans éliminer. Épreuves jouées à blanc (décision d'Otsoa) ; la colonne « avec épreuves » les compte comme en deuxième passe, pour information.

Cellules éliminatoires (tout l'horizon, aux deux horizons ; fenêtre après le changement à l'horizon long) :

| règle ou témoin | cellules | passe | échoue | indécis | hors budget au final | pire cellule (borne haute ÷ budget) | où | hors budget avec épreuves |
|--|--|--|--|--|--|--|--|--|
| A½ | 390 | 390 | 0 | 0 | 0 | 0,26 | A2, service client, long, faible | 35 |
| A¼ | 390 | 390 | 0 | 0 | 0 | 0,23 | A2, service client, long, faible | 35 |
| A-dégâts | 390 | 381 | 6 | 3 | 6 | 1,17 | bordD_fort_3barre, bureau, long, fort, après le changement | 47 |
| B-régulier | 390 | 390 | 0 | 0 | 0 | 0,95 | bordD_faible_pireBreg, bureau, long, faible, après le changement | 35 |
| B-tout | 390 | 390 | 0 | 0 | 0 | 0,45 | bordD_fort_1.5barre, bureau, long, fort, après le changement | 35 |
| liste_fixe | 390 | 361 | 27 | 2 | 29 | 4,30 | A4, bureau, court, faible | — |
| tri_risque | 390 | 351 | 39 | 0 | 39 | 6,01 | A4, bureau, court, faible | — |
| trois_reussites | 390 | 227 | 161 | 2 | 163 | 403,98 | A4, service client, court, fort | — |
| oracle_p2 | 390 | 390 | 0 | 0 | 0 | 0,80 | A2, bureau, court, faible | — |
| tout_approuver | 390 | 220 | 169 | 1 | 170 | 857,95 | A4, service client, court, fort | — |
| hasard_A½ | 390 | 386 | 4 | 0 | 4 | 1,46 | bordD_faible_3barre, service client, long, faible, après le changement | — |
| hasard_A¼ | 390 | 385 | 5 | 0 | 5 | 1,48 | bordD_faible_3barre, service client, long, faible, après le changement | — |
| hasard_A-dégâts | 390 | 362 | 25 | 3 | 28 | 8,26 | A0d, service client, long, fort, après le changement | — |
| hasard_B-régulier | 390 | 362 | 28 | 0 | 28 | 7,48 | A0d, service client, long, fort, après le changement | — |
| hasard_B-tout | 390 | 377 | 12 | 1 | 13 | 2,98 | A0d, service client, long, fort, après le changement | — |

Fenêtre après le changement, horizon court (mesurée, non éliminatoire depuis l'amendement E1-a) :

| règle ou témoin | cellules | passe | échoue | indécis | hors budget au final | pire cellule (borne haute ÷ budget) | où | hors budget avec épreuves |
|--|--|--|--|--|--|--|--|--|
| A½ | 78 | 78 | 0 | 0 | 0 | 0,13 | bordD_faible_1.5barre, bureau, court, faible, après le changement | 8 |
| A¼ | 78 | 78 | 0 | 0 | 0 | 0,28 | bordD_faible_1.5barre, bureau, court, faible, après le changement | 8 |
| A-dégâts | 78 | 68 | 10 | 0 | 10 | 1,84 | bordD_moyen_3barre, bureau, court, moyen, après le changement | 19 |
| B-régulier | 78 | 71 | 7 | 0 | 7 | 1,66 | bordD_moyen_3barre, bureau, court, moyen, après le changement | 15 |
| B-tout | 78 | 78 | 0 | 0 | 0 | 0,45 | bordD_faible_1.5barre, service client, court, faible, après le changement | 8 |
| liste_fixe | 78 | 71 | 7 | 0 | 7 | 2,88 | A6a, bureau, court, faible, après le changement | — |
| tri_risque | 78 | 68 | 10 | 0 | 10 | 4,02 | A6a, bureau, court, faible, après le changement | — |
| trois_reussites | 78 | 40 | 38 | 0 | 38 | 324,89 | A6a, service client, court, fort, après le changement | — |
| oracle_p2 | 78 | 78 | 0 | 0 | 0 | 0,81 | A7, bureau, court, faible, après le changement | — |
| tout_approuver | 78 | 40 | 38 | 0 | 38 | 574,69 | A6a, service client, court, fort, après le changement | — |
| hasard_A½ | 78 | 78 | 0 | 0 | 0 | 0,07 | bordD_faible_1.5barre, bureau, court, faible, après le changement | — |
| hasard_A¼ | 78 | 78 | 0 | 0 | 0 | 0,41 | bordD_faible_3barre, bureau, court, faible, après le changement | — |
| hasard_A-dégâts | 78 | 69 | 8 | 1 | 9 | 1,50 | bordD_moyen_3barre, service client, court, moyen, après le changement | — |
| hasard_B-régulier | 78 | 67 | 11 | 0 | 11 | 1,88 | bordD_faible_3barre, bureau, court, faible, après le changement | — |
| hasard_B-tout | 78 | 74 | 3 | 1 | 4 | 1,29 | bordD_faible_3barre, service client, court, faible, après le changement | — |

## 1 bis. Dérive : au plus une erreur constatée avant le retrait (amendement E1-a, décision 5)

Agents dont le taux monte au changement (A6a, annoncé ; A6b, A0d et agents bord qui dérivent, en silence). Épisode : chaque période au palier 3 après le changement, sur un type dont le taux monte. On compte les erreurs constatées qui passent pendant l'épisode (exécutées au palier 3, sur une action vérifiable). À enjeu moyen et fort, le critère est éliminatoire : au plus une, dans chaque épisode de chaque répétition (mode base). Les erreurs sur des actions invérifiables, qui ne déclenchent pas le retrait, sont exclues du critère et rapportées à part ; à enjeu faible, les chiffres sont donnés pour information.

| règle | enjeu | cellules (agent, mélange, horizon, type) | répétitions avec épisode | erreurs constatées dans un épisode, au plus | cellules hors critère | erreurs constatées passées (moyenne) | erreurs invérifiables passées (moyenne, à part) | invérifiables, au plus |
|--|--|--|--|--|--|--|--|--|
| A½ | moyen et fort | 80 | 9395 | 1 | 0 | 1,000 | 0,053 | 3 |
| A½ | faible (information) | 40 | 28637 | 34 | — | 5,097 | 0,271 | 9 |
| A¼ | moyen et fort | 80 | 11117 | 1 | 0 | 0,999 | 0,054 | 3 |
| A¼ | faible (information) | 40 | 52563 | 25 | — | 3,436 | 0,180 | 9 |
| A-dégâts | moyen et fort | 80 | 78125 | 1 | 0 | 4,454 | 0,235 | 7 |
| A-dégâts | faible (information) | 40 | 101339 | 55 | — | 16,968 | 0,896 | 27 |
| B-régulier | moyen et fort | 80 | 75338 | 1 | 0 | 3,511 | 0,185 | 7 |
| B-régulier | faible (information) | 40 | 119560 | 1 | — | 25,005 | 1,320 | 27 |
| B-tout | moyen et fort | 80 | 34010 | 1 | 0 | 1,896 | 0,099 | 4 |
| B-tout | faible (information) | 40 | 104712 | 1 | — | 7,862 | 0,415 | 12 |

## 2. Charge (mesure 2)

Validations, corrections et doutes pour 100 actions hors lectures (sans la charge des épreuves, comptée à part), en moyenne sur les couples (agent, mélange) où au moins un type est sous la barre. Le détail couple par couple est dans `charges.csv`.

| règle | court : hors lectures | avec épreuves | totale | couples | long : hors lectures | avec épreuves | couples |
|--|--|--|--|--|--|--|--|
| A½ | 78,6 | 80,4 | 46,1 | 55 | 59,3 | 60,0 | 46 |
| A¼ | 78,0 | 79,8 | 45,7 | 55 | 57,8 | 58,5 | 46 |
| A-dégâts | 64,4 | 66,2 | 37,9 | 55 | 31,4 | 32,1 | 46 |
| B-régulier | 63,8 | 65,6 | 37,5 | 55 | 33,6 | 34,3 | 46 |
| B-tout | 72,7 | 74,5 | 42,7 | 55 | 44,9 | 45,6 | 46 |
| oracle_p2 | 40,9 | 40,9 | 24,3 | 55 | 31,1 | 31,1 | 46 |
| liste_fixe | 82,6 | 82,6 | 48,3 | 55 | 82,2 | 82,2 | 46 |
| tri_risque | 74,8 | 74,8 | 43,9 | 55 | 74,2 | 74,2 | 46 |
| trois_reussites | 15,9 | 15,9 | 9,7 | 55 | 11,9 | 11,9 | 46 |
| tout_valider | 100,0 | 100,0 | 58,1 | 55 | 100,0 | 100,0 | 46 |

Quelques couples de l'horizon court (hors lectures, sans épreuves) :

| agent | mélange | A½ | A¼ | A-dégâts | B-régulier | B-tout | oracle | liste fixe | tri |
|--|--|--|--|--|--|--|--|--|--|
| A1 | bureau | 62,2 | 61,7 | 50,5 | 49,4 | 55,3 | 47,3 | 72,7 | 61,8 |
| A1 | service_client | 90,3 | 89,3 | 74,4 | 76,9 | 86,0 | 83,4 | 91,7 | 86,7 |
| A2 | bureau | 68,9 | 68,9 | 63,8 | 60,8 | 65,1 | 47,5 | 72,7 | 61,8 |
| A2 | service_client | 91,4 | 91,0 | 87,3 | 86,5 | 88,3 | 83,4 | 91,7 | 86,7 |
| A3 | bureau | 75,5 | 75,5 | 74,7 | 70,2 | 74,3 | 60,2 | 72,7 | 61,8 |
| A3 | service_client | 92,9 | 92,8 | 89,9 | 88,7 | 90,8 | 83,5 | 91,7 | 86,7 |
| A5 | bureau | 68,9 | 68,9 | 63,7 | 60,8 | 65,1 | 47,5 | 72,7 | 61,8 |
| A5 | service_client | 91,4 | 91,0 | 87,3 | 86,5 | 88,3 | 83,4 | 91,7 | 86,7 |

## 3. Réussite au sens de la décision 3, et part du gain de l'oracle (mesures 3 et 4)

Pour chaque couple (horizon, mélange, agent) : la règle tient-elle le budget dans ce couple, et demande-t-elle moins de validations hors lectures que la liste fixe et que le tri par le risque (différence appariée, intervalle à 95 % tout sous 0) ? Un témoin qui dépasse le budget dans le couple compte comme battu. Part du gain de l'oracle : (100 − charge) ÷ (100 − charge de l'oracle avec palier 2), seulement si l'oracle gagne au moins un point.

| règle | horizon | couples | réussite (sans épreuves) | réussite (avec épreuves) | part du gain de l'oracle (médiane) | étendue |
|--|--|--|--|--|--|--|
| A½ | court | 62 | 29 | 28 | 0,45 | 0,04 à 0,72 |
| A½ | long | 46 | 45 | 43 | 0,63 | 0,29 à 0,96 |
| A¼ | court | 62 | 32 | 31 | 0,46 | 0,04 à 0,73 |
| A¼ | long | 46 | 44 | 43 | 0,65 | 0,29 à 0,96 |
| A-dégâts | court | 62 | 41 | 39 | 0,60 | 0,24 à 1,54 |
| A-dégâts | long | 46 | 40 | 37 | 0,98 | 0,68 à 1,90 |
| B-régulier | court | 62 | 52 | 41 | 0,68 | 0,31 à 1,39 |
| B-régulier | long | 46 | 46 | 43 | 0,96 | 0,68 à 1,66 |
| B-tout | court | 62 | 49 | 45 | 0,52 | 0,13 à 0,85 |
| B-tout | long | 46 | 44 | 43 | 0,82 | 0,58 à 1,07 |

## 5. Retrait (mesure 5)

Agents qui se dégradent (A6a, changement annoncé ; A6b, A0d et agents bord qui dérivent, en silence), types dont le nouveau taux dépasse la barre et qui sont au palier 3 au moment du changement. Pour chaque règle : délai médian jusqu'à la perte du palier 3, en actions du type (pire type), part jamais retirée avant la fin (pire type), erreurs passées pendant le délai (moyenne) ; « — » : aucun type au palier 3 au changement. Détail, 95e centile et part du temps au palier 3 après le changement : `retrait.csv`.

| agent | horizon | A½ : délai ; jamais ; erreurs | A¼ : délai ; jamais ; erreurs | A-dégâts : délai ; jamais ; erreurs | B-régulier : délai ; jamais ; erreurs | B-tout : délai ; jamais ; erreurs |
|--|--|--|--|--|--|--|
| A6a | court | 0 ; 0 % ; 0,00 | 0 ; 0 % ; 0,00 | 0 ; 0 % ; 0,00 | 0 ; 0 % ; 0,00 | 0 ; 0 % ; 0,00 |
| A6b | court | 7 ; 3 % ; 1,24 | 8 ; 1 % ; 1,34 | 23 ; 24 % ; 2,32 | 8 ; 1 % ; 1,05 | 8 ; 1 % ; 1,05 |
| bord qui dérive, faible | court | 19 ; 0 % ; 1,15 | 35 ; 1 % ; 1,46 | 62 ; 33 % ; 2,52 | 20 ; 4 % ; 1,04 | 20 ; 4 % ; 1,04 |
| bord qui dérive, fort | court | — | — | — | — | — |
| bord qui dérive, moyen | court | — | — | > fin ; 57 % ; 0,68 | > fin ; 56 % ; 0,74 | — |
| A0d | long | 150 ; 0 % ; 1,05 | 149 ; 0 % ; 1,05 | 159 ; 0 % ; 1,05 | 157 ; 0 % ; 1,05 | 157 ; 0 % ; 1,05 |
| A6b | long | 15 ; 0 % ; 1,98 | 14 ; 0 % ; 1,86 | 22 ; 0 % ; 2,65 | 8 ; 0 % ; 1,05 | 8 ; 0 % ; 1,05 |
| bord qui dérive, faible | long | 49 ; 0 % ; 2,17 | 49 ; 0 % ; 2,13 | 64 ; 0 % ; 2,84 | 20 ; 0 % ; 1,05 | 20 ; 0 % ; 1,05 |
| bord qui dérive, fort | long | — | — | 2 142 ; 20 % ; 1,02 | 2 200 ; 19 % ; 1,02 | 2 145 ; 20 % ; 1,02 |
| bord qui dérive, moyen | long | 210 ; 0 % ; 1,05 | 207 ; 0 % ; 1,05 | 214 ; 1 % ; 1,05 | 215 ; 1 % ; 1,05 | 214 ; 1 % ; 1,05 |

## 6. Garantie « au plus 5 fois sur 100 » (mesure 6)

Part des répétitions où un type dont le vrai taux dépasse la barre atteint le palier 3 (agents constants : tout l'horizon ; agents qui changent : avant, et après le changement pour une nouvelle promotion). Intervalle de Wilson ; « échoue » si l'intervalle est tout au-dessus de 5 %.

| règle | horizon | couples (type au-dessus de la barre) | au-dessus de 5 % | indécis | pire part | où |
|--|--|--|--|--|--|--|
| A½ | court | 234 | 7 | 0 | 53,5 % [52,1 ; 54,8] | bordD_faible_1.5barre, ECR, bureau, apres |
| A½ | long | 116 | 10 | 4 | 36,7 % [33,8 ; 39,7] | A6b, ECR, service_client, apres |
| A¼ | court | 234 | 12 | 0 | 36,8 % [35,5 ; 38,1] | bordD_faible_1.5barre, ECR, bureau, apres |
| A¼ | long | 116 | 13 | 2 | 40,2 % [37,2 ; 43,3] | bordD_moyen_1.5barre, EXE, service_client, apres |
| A-dégâts | court | 234 | 79 | 5 | 99,6 % [99,4 ; 99,7] | bord_moyen_1.5barre, DUR, service_client, tout |
| A-dégâts | long | 116 | 95 | 1 | 100,0 % [99,6 ; 100,0] | A0d, DUR, bureau, apres |
| B-régulier | court | 234 | 86 | 3 | 100,0 % [99,9 ; 100,0] | A3, ECR, bureau, tout |
| B-régulier | long | 116 | 94 | 1 | 100,0 % [99,6 ; 100,0] | A0d, DUR, bureau, apres |
| B-tout | court | 234 | 53 | 1 | 99,5 % [99,2 ; 99,6] | bord_faible_1.5barre, ECR, bureau, tout |
| B-tout | long | 116 | 82 | 4 | 100,0 % [99,6 ; 100,0] | A1, DUR, bureau, tout |

## 7. Volume pour mériter (mesure 7)

Horizon long, agent A0 (1 sur 10 000 partout) : actions du flux avant le premier palier 3, médiane et 95e centile, et part des répétitions qui ne l'atteignent jamais ; entre parenthèses, le volume analytique d'un agent sans erreur (relecture, I10). Les autres agents constants de l'horizon long sont dans `volume.csv`.

| mélange | type | A½ : médiane / 95e centile ; jamais (analytique) | A¼ : médiane / 95e centile ; jamais (analytique) | A-dégâts : médiane / 95e centile ; jamais (analytique) | B-régulier : médiane / 95e centile ; jamais (analytique) | B-tout : médiane / 95e centile ; jamais (analytique) |
|--|--|--|--|--|--|--|
| bureau | ECR | 1 617 / 1 824 ; 0 % (1 621) | 1 090 / 1 250 ; 0 % (1 088) | 495 / 594 ; 0 % (498) | 103 / 149 ; 0 % (105) | 284 / 362 ; 0 % (288) |
| bureau | DUR | 23 644 / 46 818 ; 0 % (23 500) | 15 738 / 29 261 ; 0 % (15 684) | 1 044 / 1 266 ; 0 % (1 053) | 1 545 / 1 800 ; 0 % (1 553) | 4 202 / 4 794 ; 0 % (4 197) |
| bureau | EXE | 23 695 / 50 042 ; 0 % (23 500) | 15 772 / 33 264 ; 0 % (15 684) | 1 042 / 1 255 ; 0 % (1 053) | 1 543 / 1 793 ; 0 % (1 553) | 4 204 / 4 737 ; 0 % (4 197) |
| bureau | MSG | 4 063 / 4 617 ; 0 % (4 053) | 2 725 / 3 141 ; 0 % (2 719) | 1 241 / 1 498 ; 0 % (1 246) | 256 / 380 ; 0 % (263) | 717 / 905 ; 0 % (719) |
| bureau | SOR | jamais / jamais ; 100 % (166 809) | jamais / jamais ; 63 % (111 217) | 8 265 / 12 979 ; 0 % (8 235) | 11 022 / 19 963 ; 0 % (10 976) | 30 049 / 67 771 ; 0 % (29 814) |
| bureau | ARG | jamais / jamais ; 100 % (400 342) | jamais / jamais ; 100 % (266 921) | 19 833 / 28 969 ; 0 % (19 763) | 26 433 / 43 151 ; 0 % (26 342) | 72 092 / jamais ; 7 % (71 553) |
| service_client | ECR | 1 803 / 2 138 ; 0 % (1 811) | 1 213 / 1 496 ; 0 % (1 221) | 514 / 705 ; 0 % (526) | 118 / 218 ; 0 % (126) | 307 / 463 ; 0 % (316) |
| service_client | DUR | 13 020 / 28 551 ; 0 % (12 937) | 8 665 / 20 241 ; 0 % (8 626) | 615 / 704 ; 0 % (616) | 852 / 957 ; 0 % (853) | 2 312 / 2 610 ; 0 % (2 311) |
| service_client | EXE | 130 096 / jamais ; 22 % (129 368) | 86 672 / jamais ; 13 % (86 263) | 6 136 / 7 146 ; 0 % (6 158) | 8 519 / 9 744 ; 0 % (8 526) | 23 094 / 25 923 ; 0 % (23 105) |
| service_client | MSG | 3 003 / 3 578 ; 0 % (3 018) | 2 024 / 2 504 ; 0 % (2 035) | 865 / 1 187 ; 0 % (877) | 195 / 371 ; 0 % (211) | 518 / 758 ; 0 % (526) |
| service_client | SOR | jamais / jamais ; 100 % (227 667) | jamais / jamais ; 99 % (151 781) | 11 318 / 21 150 ; 0 % (11 263) | 15 043 / 29 525 ; 0 % (14 974) | 41 154 / 114 161 ; 2 % (40 693) |
| service_client | ARG | jamais / jamais ; 100 % (243 929) | jamais / jamais ; 100 % (162 622) | 12 122 / 23 233 ; 0 % (12 068) | 16 133 / 33 770 ; 0 % (16 043) | 44 101 / 125 218 ; 2 % (43 600) |

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

| règle | base : hors budget ; pire cellule (× budget) ; épisodes hors décision 5 | rate10 : hors budget ; pire cellule (× budget) ; épisodes hors décision 5 | difficiles : hors budget ; pire cellule (× budget) ; épisodes hors décision 5 | retard10 : hors budget ; pire cellule (× budget) ; épisodes hors décision 5 |
|--|--|--|--|--|
| A½ | 0 / 390 ; pire 0,26 ; décision 5 : 0 (1 au plus) | 0 / 390 ; pire 0,27 ; décision 5 : 0 (1 au plus) | 0 / 390 ; pire 0,67 ; décision 5 : 0 (1 au plus) | 0 / 390 ; pire 0,26 ; décision 5 : 14 (3 au plus) |
| A¼ | 0 / 390 ; pire 0,23 ; décision 5 : 0 (1 au plus) | 0 / 390 ; pire 0,25 ; décision 5 : 0 (1 au plus) | 0 / 390 ; pire 0,58 ; décision 5 : 0 (1 au plus) | 0 / 390 ; pire 0,23 ; décision 5 : 16 (3 au plus) |
| A-dégâts | 6 / 390 ; pire 1,17 ; décision 5 : 0 (1 au plus) | 23 / 390 ; pire 1,28 ; décision 5 : 0 (1 au plus) | 92 / 390 ; pire 2,69 ; décision 5 : 0 (1 au plus) | 11 / 390 ; pire 1,17 ; décision 5 : 48 (6 au plus) |
| B-régulier | 0 / 390 ; pire 0,95 ; décision 5 : 0 (1 au plus) | 9 / 390 ; pire 1,05 ; décision 5 : 0 (1 au plus) | 75 / 390 ; pire 2,26 ; décision 5 : 0 (1 au plus) | 0 / 390 ; pire 0,95 ; décision 5 : 48 (6 au plus) |
| B-tout | 0 / 390 ; pire 0,45 ; décision 5 : 0 (1 au plus) | 0 / 390 ; pire 0,51 ; décision 5 : 0 (1 au plus) | 6 / 390 ; pire 1,22 ; décision 5 : 0 (1 au plus) | 0 / 390 ; pire 0,46 ; décision 5 : 36 (3 au plus) |

Cellules éliminatoires de l'amendement E1-a. Avec le constat différé, les erreurs exécutées pendant le délai passent : la décision 5 suppose un constat immédiat. Avec un contrôle qui rate des erreurs, celles-ci ne sont pas constatées : elles passent sans compter dans le critère (colonne « ratées » de `derive.csv`).

## 10. Retrait comparé au meilleur détecteur possible (mesure 10)

Pour chaque règle et chaque type devenu mauvais en silence (A6b, A0d, agents bord qui dérivent) : fréquence mesurée des fausses alertes avant le changement (actions au palier 3 par perte du palier 3), délai moyen mesuré du retrait, et délai du CUSUM optimal (Page, mêmes taux avant et après) réglé sur la même fréquence de fausses alertes. Rapport > 1 : la règle est plus lente que le meilleur détecteur.

| règle | agent | mélange | horizon | type | actions entre fausses alertes | délai mesuré | délai du CUSUM | rapport |
|--|--|--|--|--|--|--|--|--|
| A-dégâts | A0d | bureau | long | DUR | 10 380 | 210 | 208 | 1,01 |
| A-dégâts | A0d | bureau | long | EXE | 10 001 | 210 | 200 | 1,05 |
| A-dégâts | A0d | bureau | long | SOR | 10 751 | 211 | 211 | 1,00 |
| A-dégâts | A0d | bureau | long | ARG | 11 054 | 218 | 211 | 1,03 |
| A-dégâts | A0d | service_client | long | DUR | 10 092 | 212 | 202 | 1,05 |
| A-dégâts | A0d | service_client | long | EXE | 10 534 | 198 | 211 | 0,94 |
| A-dégâts | A0d | service_client | long | SOR | 11 100 | 212 | 211 | 1,00 |
| A-dégâts | A0d | service_client | long | ARG | 10 332 | 199 | 207 | 0,96 |
| A-dégâts | A6b | bureau | long | ECR | 182 | 22 | 20 | 1,10 |
| A-dégâts | A6b | bureau | long | DUR | 52 | 11 | 10 | 1,06 |
| A-dégâts | A6b | bureau | long | EXE | 52 | 9 | 10 | 0,85 |
| A-dégâts | A6b | bureau | long | MSG | 180 | 22 | 20 | 1,10 |
| A-dégâts | A6b | service_client | long | ECR | 457 | 32 | 30 | 1,07 |
| A-dégâts | A6b | service_client | long | EXE | 56 | 8 | 11 | 0,76 |
| A-dégâts | A6b | service_client | long | MSG | 454 | 32 | 30 | 1,08 |
| A-dégâts | A6b | bureau | court | ECR | 132 | 21 | 16 | 1,29 |
| A-dégâts | A6b | bureau | court | DUR | 53 | 11 | 11 | 1,00 |
| A-dégâts | A6b | bureau | court | EXE | 51 | 10 | 10 | 0,99 |
| A-dégâts | A6b | bureau | court | MSG | 62 | 17 | 11 | 1,50 |
| A-dégâts | A6b | service_client | court | ECR | 215 | 25 | 22 | 1,11 |
| A-dégâts | A6b | service_client | court | DUR | 54 | 10 | 11 | 0,96 |
| A-dégâts | A6b | service_client | court | MSG | 115 | 19 | 15 | 1,23 |
| A-dégâts | bordD_faible_1.5barre | bureau | long | ECR | 11 180 700 | 86 | 77 | 1,13 |
| A-dégâts | bordD_faible_1.5barre | bureau | long | MSG | 4 424 490 | 87 | 68 | 1,29 |
| A-dégâts | bordD_faible_1.5barre | service_client | long | ECR | 3 720 160 | 33 | 22 | 1,51 |
| A-dégâts | bordD_faible_1.5barre | service_client | long | MSG | 1 111 630 | 34 | 18 | 1,87 |
| A-dégâts | bordD_faible_1.5barre | bureau | court | ECR | 53 659 | 72 | 30 | 2,41 |
| A-dégâts | bordD_faible_1.5barre | bureau | court | MSG | 9 738 | 38 | 26 | 1,46 |
| A-dégâts | bordD_faible_1.5barre | service_client | court | ECR | 48 568 | 26 | 11 | 2,37 |
| A-dégâts | bordD_faible_1.5barre | service_client | court | MSG | 23 200 | 19 | 11 | 1,80 |
| A-dégâts | bordD_faible_3barre | bureau | long | ECR | 11 180 700 | 35 | 35 | 0,99 |
| A-dégâts | bordD_faible_3barre | bureau | long | MSG | 4 424 490 | 35 | 30 | 1,15 |
| A-dégâts | bordD_faible_3barre | service_client | long | ECR | 3 720 160 | 12 | 11 | 1,15 |
| A-dégâts | bordD_faible_3barre | service_client | long | MSG | 1 111 630 | 13 | 7 | 1,76 |
| A-dégâts | bordD_faible_3barre | bureau | court | ECR | 53 659 | 33 | 14 | 2,27 |
| A-dégâts | bordD_faible_3barre | bureau | court | MSG | 9 738 | 26 | 13 | 2,00 |
| A-dégâts | bordD_faible_3barre | service_client | court | ECR | 48 568 | 13 | 5 | 2,32 |
| A-dégâts | bordD_faible_3barre | service_client | court | MSG | 23 200 | 12 | 5 | 2,21 |
| A-dégâts | bordD_faible_pireBreg | bureau | long | ECR | 11 180 700 | 43 | 43 | 1,01 |
| A-dégâts | bordD_faible_pireBreg | bureau | long | MSG | 4 424 490 | 43 | 37 | 1,15 |
| A-dégâts | bordD_faible_pireBreg | service_client | long | ECR | 3 720 160 | 20 | 15 | 1,34 |
| A-dégâts | bordD_faible_pireBreg | service_client | long | MSG | 1 111 630 | 20 | 11 | 1,78 |
| A-dégâts | bordD_faible_pireBreg | bureau | court | ECR | 53 659 | 42 | 18 | 2,38 |
| A-dégâts | bordD_faible_pireBreg | bureau | court | MSG | 9 738 | 30 | 16 | 1,91 |
| A-dégâts | bordD_faible_pireBreg | service_client | court | ECR | 48 568 | 18 | 7 | 2,45 |
| A-dégâts | bordD_faible_pireBreg | service_client | court | MSG | 23 200 | 16 | 7 | 2,12 |
| A-dégâts | bordD_fort_1.5barre | bureau | long | SOR | 10 751 | 1 632 | 1 827 | 0,89 |
| A-dégâts | bordD_fort_1.5barre | bureau | long | ARG | 11 054 | 1 111 | 1 845 | 0,60 |
| A-dégâts | bordD_fort_1.5barre | service_client | long | SOR | 11 100 | 2 618 | 3 175 | 0,82 |
| A-dégâts | bordD_fort_1.5barre | service_client | long | ARG | 10 332 | 2 516 | 3 036 | 0,83 |
| A-dégâts | bordD_fort_3barre | bureau | long | SOR | 10 751 | 891 | 911 | 0,98 |
| A-dégâts | bordD_fort_3barre | bureau | long | ARG | 11 054 | 783 | 917 | 0,85 |
| A-dégâts | bordD_fort_3barre | service_client | long | SOR | 11 100 | 1 525 | 1 573 | 0,97 |
| A-dégâts | bordD_fort_3barre | service_client | long | ARG | 10 332 | 1 513 | 1 518 | 1,00 |
| A-dégâts | bordD_fort_pireBreg | bureau | long | SOR | 10 751 | 1 026 | 1 060 | 0,97 |
| A-dégâts | bordD_fort_pireBreg | bureau | long | ARG | 11 054 | 870 | 1 068 | 0,82 |
| A-dégâts | bordD_fort_pireBreg | service_client | long | SOR | 11 100 | 1 775 | 1 832 | 0,97 |
| A-dégâts | bordD_fort_pireBreg | service_client | long | ARG | 10 332 | 1 737 | 1 765 | 0,98 |
| A-dégâts | bordD_moyen_1.5barre | bureau | long | DUR | 10 379 | 214 | 210 | 1,02 |
| A-dégâts | bordD_moyen_1.5barre | bureau | long | EXE | 10 001 | 212 | 203 | 1,05 |

(228 lignes de plus dans `cusum.csv`.)

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
- Agents bord qui changent (mesure 5) : chaque agent bord a une variante qui part du taux d'A0 et dérive en silence vers la valeur bord au milieu de l'horizon (bordD_*). Ajoutés en phase 1 ; leur place est tranchée par l'amendement E1-a (décision d'Otsoa) : ils comptent dans le choix, et leur dérive se juge selon la décision 5.
- Amendement E1-a (décision d'Otsoa, après l'essai de vérification) : critère de la décision 5 compté par période au palier 3 après le changement (la période en cours au changement, puis chaque nouvelle promotion), sur les types dont le taux monte ; « constatée » : erreur sur une action vérifiable, que le contrôle voit (aussitôt, ou 10 actions plus tard en mode retard) ; erreurs invérifiables et erreurs ratées par un contrôle imparfait exclues du critère, rapportées à part. Les cellules indécises de la fenêtre courte sont encore relancées, pour que l'ancienne lecture soit calculée comme avant.
- Classement (4.2) : les couples sont ceux de l'horizon court (agent × mélange), qui est aussi le volume de l'expérience réelle (4.6) ; le classement à l'horizon long est donné à part. La charge de classement est hors lectures et sans la charge des épreuves (« comptée à part », décision 6) ; la version avec épreuves est donnée.
- Prudence (4.3) : marge = 1 − (borne haute de l'excès ÷ budget) dans la pire cellule de la règle (toutes cellules, après relance) ; égalité de prudence à 0,001 près, puis simplicité : B-tout, B-régulier, A½, A¼, A-dégâts.
- Intervalles : l'union de l'intervalle normal et de l'intervalle bootstrap (percentile, 2 000 tirages), pour toutes les cellules : c'est plus prudent que l'un ou l'autre (une cellule indécise est relancée, puis compte comme un échec).
- Règle B, points laissés ouverts par le plan : la consigne modifiée divise le compteur par deux (⌊c/2⌋, soit ⌊N/2⌋ au palier 3, comme écrit dans le plan) ; le compteur est plafonné à la longueur exigée (⌈1,25 N⌉ pendant une montée allongée, N sinon) ; l'allongement ne se cumule pas ; après un changement de modèle, plus d'allongement (nouvel agent ; les erreurs deviennent des épreuves) ; sous le palier 3, le palier 2 suit le score de Wald v2.
- Tests de résistance : une variante d'épreuve est jugée par le même contrôle (10 % de ses erreurs ratées ; toutes, dans le pire cas, puisque les variantes sont des cas difficiles) ; avec le constat différé, l'épreuve est jugée aussitôt, seules les preuves des actions ordinaires arrivent 10 actions du type plus tard.
- Garantie après un changement : seules les nouvelles promotions au palier 3 comptent (comme en v2) ; un type déjà au palier 3 au changement relève du retrait (mesure 5).
- Alerte 4.5 : critère fixé avant le lancement (plus d'échecs qu'une autre survivante dans un mode, ou une pire cellule au moins 1,25 fois plus haute et au moins à la moitié du budget), appliqué aux cellules éliminatoires de l'amendement E1-a ; les échecs comptent les cellules hors budget et les épisodes hors décision 5.
- Pannes injectées : non simulées (décision 3). A8 est vide à l'horizon court (aucune règle n'atteint SOR au palier 3 avant t = 1 500) ; il n'y a pas d'A8 à l'horizon long dans le plan.

## Figures

- `fig1_charge_budget.png`
- `fig2_garantie.png`
- `fig3_volume.png`
