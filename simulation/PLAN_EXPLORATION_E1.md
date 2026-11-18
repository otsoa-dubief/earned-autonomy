# Exploration E1 · plan (4 novembre 2026, au soir), révisé après relecture

> **Statut : exploration, annoncée comme telle.**
> - Elle ne change pas le verdict de la deuxième passe (`resultats/`), qui reste publié tel quel.
> - Elle sert à choisir la règle de l'expérience réelle, selon une règle de choix écrite avant de lancer (`../REGLE.md`, « Décisions prises après la deuxième passe »).
> - Aucun agent réel, aucune donnée réelle, aucun appel réseau.
> - Résultats dans `resultats_e1/`, sans toucher `resultats/` ni `resultats_v1/`.
> - **Révision 1** : après la relecture indépendante (`../revues/plan_exploration_E1_relecture.md`, verdict « lançable après corrections »). La table de correspondance est en fin de fichier.
> - Les quatre points laissés à Otsoa ont été tranchés le 04/11 au soir, tous selon la recommandation :
>   - épreuves jouées à blanc ;
>   - tests de résistance à part, avec alerte ;
>   - départage par la prudence, puis par la simplicité ;
>   - les trois ajouts validés.

## 0. Prédiction datée, écrite avant de lancer

- **B gagnera sur la charge, par construction.** Wald réglé sur la barre est très lent. Pour un agent sans erreur, il faut 15 213 réussites d'affilée (A½) à enjeu fort en bureau, contre 2 719 pour B-tout. À 3 000 actions, A n'atteint le palier 3 ni à enjeu moyen ni à enjeu fort. À 150 000 actions, A½ ne l'atteint toujours pas à enjeu fort.
- **Ce qu'E1 peut vraiment apprendre** :
  - si B tient le budget, y compris pour des agents placés à son pire cas ;
  - ce que B coûte en garantie : B donne l'autonomie à des agents au-dessus de la barre, sans dépasser le budget ;
  - ce que B coûte au retrait ;
  - si un Wald réglé lui aussi sur les dégâts fait mieux.
- **Pour l'expérience réelle** : avec quelques milliers d'actions par agent, aucune règle n'atteindra le palier 3 à enjeu fort. La comparaison s'y jouera à enjeu faible, et à enjeu moyen pour B-régulier. La mesure de l'écart, elle, vaut à tous les niveaux.

## 1. Ce qui change pour toutes les règles

1. **Lectures sans effet** (décision 4) :
   - une erreur de lecture (LEC) ne compte plus dans les dégâts ;
   - LEC agit seule dès le départ, pour toutes les règles, témoins compris ;
   - la charge principale se lit hors lectures ;
   - tout cela passe par un interrupteur, pour que le chemin v2 reproduise `resultats/` au chiffre près.
2. **Budget d'erreurs d'Otsoa** (fixé à l'aveugle le 04/11 à 15 h 42) : faible 0,5 ; moyen 0,05 ; fort 0,005 erreur en plus pour 100 actions du flux.
3. **Barres** (décision 2) :
   - barre = budget ÷ (0,95 × 100 × part) ;
   - « part » désigne la part du flux occupée par les types du niveau qui peuvent agir seuls (LEC et parts plafonnées exclues).

   | mélange | faible (ECR + MSG) | moyen (DUR + EXE) | fort (SOR et ARG hors plafonds) |
   |--|--|--|--|
   | bureau | 1 sur 39,9 | 1 sur 304 | 1 sur 2 584 |
   | service client | 1 sur 15,2 | 1 sur 418 | 1 sur 4 408 |

4. **Épreuves** (décidé par Otsoa le 04/11 au soir). Dans la deuxième passe, les variantes d'épreuve s'ajoutaient au flux au palier 1, et 5 % de leurs erreurs passaient. « Tout faire valider » n'en a pas. À elles seules, elles dépassaient le budget fort : 1,1 fois pour A2 en bureau, jusqu'à 26 fois pour A4-calibré en service client.
   - **Décision** : une épreuve est un test joué à blanc, sans effet réel. Elle ne fait aucun dégât ; sa charge est comptée à part.
   - Le verdict du budget et la charge sont donnés avec et sans épreuves.
   - Même déclencheur pour toutes les règles : une erreur à enjeu moyen ou fort, quel que soit le palier (pièce 7, code v2).
5. **Agents** :
   - les 13 agents de la deuxième passe, ajoutés en fin de liste pour garder leurs graines ;
   - **A0 et A0d** (validés par Otsoa), à l'horizon long. A0 se trompe 1 fois sur 10 000 sur tous les types ; A0d fait de même, puis dérive en silence vers 1 sur 200 au milieu de l'horizon ;
   - **agents « bord »** (validés par Otsoa), aux deux horizons. Sur un seul niveau, q prend trois valeurs : le pire cas de B-régulier, soit 1/(N + 1), puis 1,5 fois et 3 fois la barre. Ailleurs, q reste au taux d'A0. Sans eux, le critère du budget est presque vide, car un agent sous la barre ne peut dépasser le budget avec aucune règle.
6. **Horizons et répétitions** :
   - **court** : 3 000 actions ;
   - **long** : 150 000 actions, pour A0, A0d, A1, A2, A6b et les agents bord. Les changements y sont placés au milieu de l'horizon ;
   - toutes les règles ont le même nombre de répétitions, sur les mêmes tirages : 5 000 à l'horizon court, 1 000 à l'horizon long (par blocs de 200) ;
   - le code est paramétré par l'horizon (`lignes_reactivite`, instantané de `simuler_regle`, `lignes_consigne`).
7. **Validateur** : il laisse passer 5 % des erreurs.
8. **Pannes injectées** (décision 3) : elles ne sont pas simulées ici. Les changements simulés sont ceux d'A6a, A6b, A7, A8 et A0d.

## 2. Règles comparées

Toutes gardent les pièces 3, 4, 5 et 8, et la pièce 7 telle qu'elle est transposée ci-dessous. Le palier 2 garde le score de Wald, avec les réglages de départ.

- **A½, Wald réglé sur la barre** : la règle v2 (amendement A1), avec α = 5 %, pm3 = barre et pb3 = barre ÷ 2.
- **A¼** : la même, avec pb3 = barre ÷ 4.
- **A-dégâts, Wald réglé sur les dégâts** (validé par Otsoa) : pb3 = pm3 ÷ 2, avec pm3 choisi pour que l'excès du pire agent régulier égale le budget. Ce pm3 est étalonné par simulation avant E1. C'est un concurrent loyal de B, qui poursuit le même objectif.
- **B, les séries** (règle entièrement spécifiée) :
  1. le palier 3 s'obtient après N réussites vérifiées d'affilée sur le type ;
  2. toute erreur, à n'importe quel palier, remet le compteur à 0 ;
  3. une erreur au palier 3 retire l'autonomie. À enjeu moyen ou fort, retour au palier 1 et épreuve. À enjeu faible, descente au palier 2 si le type est réversible, au palier 1 sinon ;
  4. **pièce 7.3, l'erreur reste** : après une erreur à enjeu moyen ou fort, la montée suivante exige ⌈1,25 × N⌉ réussites. C'est le même allongement que A½, environ 24 %. Les montées suivantes, sans nouvelle erreur, exigent N ;
  5. le compteur ne bouge pas tant qu'une épreuve est ouverte, comme le score v2 ;
  6. le compteur est plafonné à N. Une consigne modifiée le ramène à ⌊N/2⌋, ce qui fait perdre le palier 3, comme A, où L/2 fait repasser au-dessus de ln B ;
  7. changement de modèle ou droits élargis : le compteur revient à 0 ; les erreurs moyennes ou fortes gardées en mémoire deviennent des épreuves, et les faibles disparaissent (pièce 8, v2) ;
  8. les actions invérifiables et les doutes sont neutres.
- **Longueurs N exactes**, calculées en fractions et épinglées dans les tests (voir la note datée de REGLE.md, décision 2) :

  | | bureau faible | bureau moyen | bureau fort | SC faible | SC moyen | SC fort |
  |--|--|--|--|--|--|--|
  | **B-régulier** : plus petit N tel que N^N ÷ (N + 1)^(N + 1) ≤ d × barre | 15 | 118 | 1 001 | 6 | 162 | 1 707 |
  | **B-tout** : N = 1 ÷ (d × barre) − 1 | 41 | 319 | 2 719 | 15 | 439 | 4 639 |

  d = 0,95 : c'est la part des erreurs constatées, compte tenu des 5 % d'actions invérifiables.
- **Témoins** :
  - tout faire valider ;
  - liste fixe (LEC et ECR agissent seules) ;
  - tri par le risque (tout l'enjeu faible agit seul) ;
  - trois réussites ;
  - hasard, apparié à chacune des règles comparées ;
  - tout approuver ;
  - **oracle avec palier 2** : palier 3 si le vrai taux du moment est au plus la barre ; sinon palier 2 si le type est réversible ; sinon palier 1. LEC agit toujours seule.

## 3. Mesures

1. **Budget (éliminatoire)** :
   - mesure : dégâts en plus pour 100 actions du flux, niveau par niveau, intervalle à 95 % apparié avec « tout faire valider » ;
   - le verdict est donné sur tout l'horizon et, pour les agents qui changent, sur la fenêtre qui va du changement à la fin ;
   - « passe » : l'intervalle est sous le budget ; « échoue » : il est au-dessus ;
   - « indécis » : on relance la cellule avec 4 fois plus de répétitions ; si elle reste indécise, elle compte comme un échec ;
   - pour les événements rares, intervalles par bootstrap.
2. **Charge** :
   - hors lectures (et charge totale), couple par couple ;
   - avec et sans la charge des épreuves.
3. **Réussite au sens de la décision 3** : pour chaque couple, à budget tenu, la règle demande-t-elle moins de validations que la liste fixe et que le tri par le risque ? Une règle simple qui dépasse le budget compte comme battue. Le résultat est rapporté pour chaque règle.
4. **Part du gain de l'oracle**, hors lectures : (100 − charge de la règle) ÷ (100 − charge de l'oracle avec palier 2). On ne la calcule que si l'oracle gagne au moins un point.
5. **Retrait**, pour A6a, A6b, A0d et les agents bord qui changent :
   - délai entre le changement et le retrait ;
   - erreurs passées pendant ce délai ;
   - part du temps passé au palier 3 après la dérive, sur les types devenus mauvais (vrai taux au-dessus de la barre).
6. **Garantie « au plus 5 fois sur 100 »**, pour toutes les règles et aux deux horizons : part des répétitions où un type dont le vrai taux dépasse la barre atteint le palier 3. Pour B, c'est le coût principal.
7. **Volume pour mériter**, type par type, à l'horizon long : médiane, 95e centile, et part des répétitions qui n'atteignent jamais le palier 3. La table analytique de la relecture (I10) est jointe.
8. **Bornes de la règle B**, sur deux suites piège :
   - « N réussites puis une erreur » : dégâts en plus de 0,95 ÷ (N + 1) ;
   - « rafale », soit N réussites puis des erreurs jusqu'au retrait : dégâts en plus d'environ 0,95 ÷ (d × N + 1).
9. **Tests de résistance**, pour toutes les règles, hors du choix, avec l'alerte de la section 4.5 (décidé par Otsoa) :
   - le contrôle automatique rate 10 % des erreurs, tirées au hasard, sur une graine à part ;
   - pire cas : il rate toutes les erreurs des cas difficiles ;
   - le constat arrive k = 10 actions du type après l'erreur. Avec k = 100, la borne est vide à enjeu faible : on le signale sans le simuler.

   Une erreur ratée compte comme une réussite : c'est ce que voit un contrôle imparfait.
10. **Retrait comparé au meilleur détecteur possible** : pour chaque règle, le point (fréquence mesurée des fausses alertes, délai mesuré) est placé sur la courbe du CUSUM optimal, pour les mêmes taux avant et après le changement. Ce point remplace la comparaison au plancher de Lorden, qui était trompeuse : la règle B lance une fausse alerte à chaque erreur.
11. **Certification** (pour la question « mesure » de la décision 1) : réussites sans erreur nécessaires pour établir que le taux est sous la barre, selon la règle de trois, environ 3 ÷ barre. Cela donne environ 7 750 à enjeu fort en bureau et 13 200 en service client.

## 4. Règle de choix

1. **Ne garder que les règles qui tiennent le budget** dans tous les cas simulés sous les hypothèses du protocole : tous les agents, mélanges, niveaux et horizons, fenêtre après changement comprise, épreuves selon la décision d'Otsoa.
2. **Classement** (décidé par Otsoa) : la charge hors lectures, en moyenne sur les couples où au moins un type est sous la barre (ceux où déléguer est possible), donnée aussi couple par couple.
3. **À égalité** (décidé par Otsoa), c'est-à-dire moins d'un point de charge hors lectures pour 100 actions d'écart : d'abord la plus prudente, celle qui laisse la plus grande marge au budget dans sa pire cellule ; puis la plus simple.
4. **Si aucune règle ne tient**, aucune n'est retenue : on le rapporte, et Otsoa décide.
5. **Alerte** : si la règle retenue tient nettement moins bien les tests de résistance qu'une autre règle restée en lice, on le signale à Otsoa avant de valider le choix.
6. **Volume** : le choix est aussi lu au volume prévu pour l'expérience réelle. Ce volume sera fixé avec le banc d'essai : quelques milliers d'actions par agent en ordre de grandeur, à confirmer.

## 5. Contrôles du code

- Les 43 tests existants restent verts : le chemin v2 reproduit `resultats/` au chiffre près, grâce aux interrupteurs.
- Une implémentation de référence de la règle B, `RegleUnTypeB`, et un test de cohérence avec le moteur, action par action, comme pour la v2.
- Les N épinglés.
- Les suites piège de la mesure 8.
- L'oracle avec palier 2.
- LEC hors des dégâts.
- La graine à part pour le contrôle imparfait.

## 6. Gel avant lancement

L'empreinte sha256 du plan et du code est écrite dans ce fichier avant de lancer. Si Otsoa donne son accord, le dossier passe aussi sous git local.

## 7. Livrables

- `resultats_e1/RESULTATS_E1.md`, écrit par un script à partir des CSV ;
- les CSV et les figures ;
- en tête, la règle retenue selon la règle de choix, ou aucune, et la prédiction de la section 0 confrontée aux résultats.

## Amendement E1-a (4 novembre au soir, après l'essai de vérification ; décision d'Otsoa)

- **Contexte.** La phase 1 a ajouté neuf agents « bordD », pour la mesure 5 : un agent A0, puis une dérive silencieuse au milieu de l'horizon, jusqu'à une valeur de bord. À l'horizon court, la fenêtre après la dérive fait 1 500 actions. Le budget moyen n'y permet que 0,75 erreur, si bien que l'erreur unique acceptée par la décision 5 suffit à éliminer une règle qui avait déjà donné l'autonomie avant la dérive.
- **Transparence.** La décision est prise après un essai de vérification à petite taille (`explorations/essai_e1_phase1/`, chiffres sans valeur). Cet essai montrait l'effet : avec les bordD jugés sur la fenêtre courte, B-tout était retenue ; sans eux, B-régulier. La décision est tranchée sur le principe de la décision 5, et non sur ce résultat.
- **Décision.** Les bordD comptent dans le choix, et la dérive se juge selon la décision 5 :
  1. à enjeu moyen et fort, au plus une erreur constatée passe avant le retrait, par type et par épisode de dérive. Ce critère est éliminatoire ;
  2. le budget se lit sur tout l'horizon ;
  3. la fenêtre après le changement n'est jugée qu'à l'horizon long (75 000 actions).
- Le choix obtenu avec l'ancienne lecture (fenêtre courte) est rapporté à part.

## Correspondance avec la relecture

| point | traitement |
|--|--|
| B1 (épreuves) | section 1.4, décidé : tests à blanc ; colonnes avec et sans épreuves |
| B2 (N de B-régulier) | N exacts (section 2) ; note datée dans REGLE.md |
| I1 (pièce 7.3, trous de B) | B entièrement spécifiée (points 1 à 8) ; 7.3 transposée par l'allongement de 1,25 |
| I2 (issue connue d'avance) | section 0 (prédiction) ; A-dégâts, validé |
| I3 (garantie pour B) | mesure 6 |
| I4 (mesure 8 hors du choix) | mesure 9 et alerte 4.5 ; hors du choix, décidé par Otsoa avec la vraie raison (hypothèse du protocole) |
| I5 (oracle sans palier 2) | oracle avec palier 2 |
| I6 (couverture des cas) | agents bord, validés |
| I7 (répétitions, indécis) | mesure 1 et section 1.6 |
| I8 (critère penché vers B) | section 4.2 et 4.3, décidé |
| I9 (dérive diluée) | mesure 1, fenêtre après changement |
| I10 (expérience réelle, réussite) | section 0, mesures 3 et 7, section 4.6 |
| I11 (Lorden) | mesure 10 |
| M1 à M12 | intégrés : N, α, interrupteurs et graines, horizon paramétré, tests, mesures 5 à 7, hasard apparié, bootstrap, gel, certification, pannes non simulées |
