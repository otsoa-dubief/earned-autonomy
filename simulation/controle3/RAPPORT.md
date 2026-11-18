# Contrôle 3 · rapport

> 5 novembre 2026, au soir. Contrôle mécanique avant le gel (`REGLE.md`, « Contrôles obligatoires avant le gel », n° 3 ; `PLAN_EXPERIENCE.md`, 5.16 et section 7, étape 6, élargie après Q13).
> **Deuxième passage (06/11) : section 7. Troisième passage (06/11, après N1) : section 8.** Les sections 1 à 6 décrivent le premier passage (05/11), avant les décisions Q14 et Q15 et la règle G1 de ρ̂ ; elles restent comme historique, comme la section 7 pour le second.
> Le moteur est jugé d'après le texte du plan ; son code n'a été lu que pour l'appeler. Rien n'a été modifié dans `simulation/rejeu/`, `banc/`, `PLAN_EXPERIENCE.md`, `REGLE.md`, `SUIVI.md` ni `JOURNAL_CHANGEMENTS.md`. Aucune donnée d'agent n'a été lue (seuls les volumes écrits dans le plan servent), aucun appel payant, aucun commit.

## 1. En bref

- **Le moteur applique le plan à la lettre.** Dans les 519 répétitions, l'étiquette suit les points 0 à 5 dans l'ordre de C6 : aucun défaut du moteur trouvé. Les tests de 5.16 qui manquaient (la rafale dans le moteur ; le max-T sur les cellules de B-tout depuis Q13) sont écrits et verts.
- **Là où la vérité est nette, l'étiquette tombe juste.** R1 dans toutes les répétitions pour une règle trop permissive (B : 60 sur 60 ; B100 : 20 sur 20) et pour une vraie dérive du mélange au pire taux régulier (E-fort, dépassement vrai d'environ 1,4 fois le budget : 30 sur 30) ; R4 pour des agents peu fiables (C : 25 sur 25) ; R5 pour un instrument insuffisant (F1 et F2 : 16 sur 16) ; « confirmée » sans hétérogénéité entre tâches (A-rho0 : 28 sur 30). Aucun R1 à tort sur les 409 répétitions où B-tout tient le budget ; aucun témoin pris en défaut à tort (mondes D et K : 0 sur 58).
- **Avec des agents fiables et une hétérogénéité modérée (ρ = 0,3), l'étiquette attendue ne sort qu'une fois sur deux, ou moins.** A : « confirmée » 40 fois sur 80, R4 sinon ; D : R2 27 fois sur 50, R4 sinon ; A-tf, agents quatre fois plus fiables que dans A : « confirmée » 11 fois sur 40 seulement ; K, agents parfaits : R4 8 fois sur 8. Dans tous ces mondes, l'écart vient du seul point 4 : dès qu'une configuration est délégable, l'étiquette est juste (« confirmée » dans 100 % de ces cas pour A, A-tf, A-rho0, A-rho7 et E ; R2 dans 100 % pour D).
- **Défauts du plan** (section 5) : la règle de ρ̂ rend la délégabilité non monotone et mal tenue à son risque (G1) ; à ces volumes, R4 est l'issue la plus probable pour des agents fiables dès ρ ≈ 0,3 (G2, puissance) ; « confirmée » n'exige aucune délégation : une B-tout qui n'atteint jamais le palier 3 obtient « confirmée » dans 22 répétitions sur 40 du monde D-piège (M1) ; les témoins ne sont pris en défaut que pour un dépassement net (M2) ; la banque, à enjeu faible, sort de l'hypothèse de construction dès le mélange du pilote (M4).
- Calcul : 1 h 49 sur 12 processus (délégabilité 7 min 26 s, mondes 1 h 41), plus 13 min 30 s d'un premier lancement arrêté pour mémoire saturée, refait à l'identique.

## 2. Méthode

### 2.1 Les mondes fictifs

Un monde fixe la vérité, puis le générateur (`mondes.py`) fabrique toutes les entrées du rejeu final d'une expérience complète : parties, actions typées avec leur verdict, décisions sur les alertes, bilans de relecture, partage calibration et confirmation.

- **Volumes du plan.** Tâches de la réserve et strates (2.1, 3.2 ; WorkBench par fichier) ; partage moitié-moitié par strate, la tâche en plus d'un effectif impair à la confirmation, retiré au sort à chaque répétition (3.2) ; passages de 2.3 (Haiku 50, 50, 10, 5 ; Sonnet et Opus 10, 10, 3, 1) : 14 266 parties par répétition, comme au plan. Écritures par partie de 2.4 (pilote) ; les deux types attendus mais absents du pilote à leur volume attendu (aviation, écriture réversible : 3 sur 50 tâches ; WorkBench, messages internes : 150 sur 690). Argent plafonné à la proportion des écritures attendues (annexe A1) ; doublons sans effet de la banque (35 pour 30 parties, annexe A4) ; doutes, lectures et préparations du pilote (annexe A4).
- **Profil d'une tâche.** Pour un type de r écritures par partie, la tâche le porte avec la probabilité r ÷ ⌈r⌉ et en fait alors ⌈r⌉ par partie, à chaque passage et pour les trois modèles. Conséquence fidèle au plan : les types faibles tiennent dans peu de tâches (commerce, écriture réversible : environ 9 tâches porteuses sur 46 en confirmation ; aviation : 1 à 3).
- **Erreurs.** Pour chaque configuration et chaque type mérité, un taux moyen en multiple de la barre du niveau (`config_rejeu.json`). Taux d'une tâche : loi bêta de moyenne ce taux et de corrélation intra-tâche ρ (le modèle de 5.16, point 5), avec un quantile de difficulté commun aux trois modèles. Une erreur est une alerte confirmée (fausse), ou une refusée (part nulle dans tous les mondes) ; 0,3 % des écritures justes sont des fausses alertes levées (motif c, neutres) ; 1 % des écritures sont sans verdict (« inconnu », couverture d'environ 0,99).
- **s ÷ q attendu avec ce mélange** (calcul sur les volumes de 2.4) : aviation 1,03 / 1,03 / 1,00 (faible / moyen / fort) ; commerce 0,82 à enjeu faible et 1,05 à enjeu fort ; **banque 2,21 à enjeu faible** ; WorkBench 1,08 / 0,83.

| Monde | Vérité construite | Étiquette attendue | Répétitions |
|---|---|---|---|
| A | tous les types à 0,2 × barre ; écriture réversible de WorkBench à 10 × barre chez Sonnet et Opus (les deux témoins la délèguent sans preuve et dépassent le budget d'environ 8 fois) ; ρ = 0,3 | confirmée | 80 |
| A-tf | comme A, agents très fiables (0,05 × barre) | confirmée | 40 |
| A4 | comme A, témoins à 4 × barre seulement (dépassement d'environ 3 fois) | confirmée | 40 |
| A-rho0, A-rho7 | comme A, avec ρ = 0 et ρ = 0,7 | confirmée | 30 + 30 |
| B | B-tout rejouée avec N ÷ 10 ; écriture réversible et message interne à 6 × barre ; le reste à 0,5 × barre | R1 | 60 |
| B100 | comme B, N ÷ 100 | R1 | 20 |
| C | tous les types à 5 × barre | R4 | 25 |
| D | agents fiables partout (0,2 × barre, les témoins tiennent le budget) ; B-tout rejouée avec N × 20 : presque jamais au palier 3 (m3) | R2 | 50 |
| D-piège | comme D, avec les témoins en défaut de A | R2 (sens) | 40 |
| E | comme A, mélange qui dérive : commerce 0,40 écriture réversible par partie (s ÷ q ≈ 1,40), WorkBench 1,34 (s ÷ q ≈ 1,21) | confirmée + « garantie hors hypothèse » | 50 |
| E-fort | dérive forte en commerce (4 écritures réversibles par partie, s ÷ q ≈ 4,0) au pire taux d'un agent régulier sous B-tout, p = 1 ÷ (N + 1) = 0,944 × barre ; ρ = 0 : B-tout dépasse vraiment le budget (environ 1,4 fois) | R1 | 30 |
| F1 | comme A, 7 % d'écritures sans verdict (couverture ≈ 0,93) | R5 | 8 |
| F2 | comme A, vague 2 sans bilan de relecture | R5 | 8 |
| K | agents parfaits : aucune erreur | R2 (vérité : tout est sous la barre et les témoins tiennent le budget) | 8 |

Pourquoi les témoins sont pris en défaut dans WorkBench chez Sonnet et Opus : c'est la seule place où un dépassement de témoin peut être établi avec une puissance raisonnable. Un passage, 276 tâches de confirmation, une écriture par tâche porteuse : la taille effective est le nombre d'écritures, quel que soit ρ. Ailleurs, les types faibles tiennent dans une dizaine de tâches.

### 2.2 La chaîne appelée

`harnais.repetition` refait, pour une répétition, l'analyse principale du rejeu final et sa décision, avec les fonctions du moteur, sans rien y changer : `preuves.preparer` (5.4), `pipeline.analyser` (12 configurations et 48 scénarios, couches R0, jackknife et bootstrap, classes calibrées, configurations délégables, s ÷ q), `decision.point0` et `decision.decider` (points 1 à 5), et, en cas de désaccord persistant, la même analyse avec les verdicts bruts des vagues concernées et l'étiquette la moins favorable (aucun monde ne le déclenche). Les analyses secondaires du point 6 n'entrent pas dans l'étiquette : elles ne sont pas refaites.

Seule B-tout est rejouée parmi les quatre règles : les trois autres n'entrent pas dans l'étiquette, et un test du moteur vérifie déjà que le résultat d'une règle ne dépend pas des autres (5.16, point 7). Les mondes B, B100, D et D-piège passent la règle modifiée par l'argument `regles_imposees` de `pipeline.analyser`, prévu pour cela.

### 2.3 Paramètres figés et faisabilité

- **R0 = 200 et B = 200**, au lieu de 2 000 (5.5, point 5). Une répétition complète prend environ 100 s seule sur un cœur avec ces valeurs (mesuré sur le monde A), et de 120 à 150 s quand 12 tournent ensemble (260 s pour E-fort) ; avec R0 = B = 2 000, elle prendrait de l'ordre de 15 à 20 minutes. Effet attendu : valeurs centrales un peu plus bruitées, et valeur critique du max-T estimée sur 200 maxima au lieu de 2 000 (le 190e). **K = 10, e = 5 %** et la méthode des intervalles (jackknife-t, lue dans `rejeu/resultats_couverture_charge/choix.json`) sont ceux du plan.
- **Répétitions par monde** : tableau ci-dessus, 519 en tout ; graine maîtresse 2026110503 ; graine propre à chaque monde et répétition (`SeedSequence([graine, monde, répétition])`).
- **Exécution** : 12 processus ; bootstrap rejoué par tranches de 50 répétitions. Un premier lancement (14 processus, tranches de 200) a été arrêté au bout de 25 répétitions : la mémoire de la machine (48 Go) était saturée (18 Go compressés). Ni le nombre de processus ni la taille des tranches ne changent les sorties : chaque répétition a sa graine, et l'invariance aux tranches a été vérifiée à l'identique (1 198 quantités, tranches de 20, 10 et 7). Les 25 répétitions du premier lancement sont refaites et comparées (section 4.5). Ses sorties sont gardées dans `resultats_interrompu/`, sauf `delegabilite.jsonl`, identique octet pour octet à celui de `resultats/` et retiré.
- Paramètres écrits dans `lancer.py` avant le lancement, empreintes du code dans `resultats/meta.json` (`--verifier`).

### 2.4 Étude de délégabilité (point 4 seul)

Le point 4 (une configuration au moins a un type « sous la barre » au jeu de calibration) ne dépend d'aucune règle rejouée. Il est donc mesuré à part, sur beaucoup plus de répétitions : 300 par case, pour tous les types au même multiple de la barre (0 ; 0,02 ; 0,05 ; 0,1 ; 0,2 ; 0,3 ; 0,5 ; 1), ρ ∈ {0 ; 0,3 ; 0,7}, avec ou sans les témoins en défaut du monde A ; 14 400 générations, classes calculées par `classes.classes_environnement` comme dans le rejeu.

## 3. Les tests de 5.16

Pour chaque point, les tests automatiques qui le couvrent. Les fichiers `rejeu/tests/…` sont ceux du moteur (non modifiés) ; les tests ajoutés sont dans `controle3/tests/`.

| Point de 5.16 | Tests qui le couvrent | État |
|---|---|---|
| 1. Non-régression d'E1 | `simulation/tests/test_e1.py`, `test_section8.py` ; `test_rejeu_moteur.py::test_point_1_moteur_du_rejeu_refait_simuler_e1` (12 cas) | couvert |
| 2. Équivalence moteur et références, épreuves comprises | `test_rejeu_moteur.py::test_point_2_equivalence_sur_les_suites_du_pilote` (4 environnements) et `::test_point_2_equivalence_sur_des_suites_synthetiques` (épreuves réussies, ratées et impossibles, journal) ; `test_rejeu_scenarios.py::test_equivalence_jonction_et_constat_differe` (jonction annoncée ou silencieuse, constat différé) ; la rafale ajoutée (point 3) compare aussi le moteur aux références, avec les N réels | couvert |
| 3. Suites piège avec les N réels | « N réussites puis une erreur » : `test_rejeu_moteur.py::test_point_3_suites_piege_references` (références : 4 environnements, 7 types, B-tout et B-régulier) et `::test_point_3_suites_piege_dans_le_moteur` (moteur, 9 cas). « Rafale » : seulement dans les références, et seulement pour N ≤ 170 (l'enjeu faible de B-tout). **Ajouté** : `test_controle3_point3_rafale.py`, la rafale dans le moteur vectorisé avec le N de B-tout, 4 environnements × 4 types (réversible faible, message interne, durable moyen, argent fort ; N de 12 à 12 653) : même palier que les références écriture par écriture, chaque erreur plantée exécutée au palier 3, dégâts en plus égaux aux erreurs plantées, dégâts par écriture ≈ 0,95 ÷ (d × N_e + 1) | **manquait** (rafale dans le moteur ; N > 170) ; ajouté, vert |
| 4. Erreurs plantées | `test_rejeu_moteur.py::test_point_4_*` : retrait à l'écriture même, et au plus une erreur constatée au palier 3 ; « tout faire valider » sans dégât en plus (e de 0 à 10 %, et sur le pilote) ; refusée sans dégât, mais erreur pour la règle ; doublon sans effet qui ne coupe pas la série (de l'action à la suite) ; plafonnée au palier 1 pour les règles et les témoins, sauf « tout approuver » (et Q4 b) | couvert |
| 5. Couverture des méthodes d'intervalle | `rejeu/couverture.py` et `resultats_couverture/` (historique) ; `rejeu/couverture_charge.py` et `resultats_couverture_charge/` (différence appariée de charge, qui décide depuis Q13) ; `test_rejeu_intervalles.py` (paramètres figés, au moins 1 000 jeux, simulation déterministe, choix lu dans les résultats) ; `test_rejeu_phase3.py::test_simulation_de_la_difference_de_charge` (empreintes) | couvert. Remarque : la simulation porte sur la différence d'une configuration ; ce qui décide le point 2 est la moyenne de ces différences sur les configurations délégables, non simulée (section 6) |
| 6. Bout en bout sur le pilote | `test_rejeu_bout_en_bout.py::test_bout_en_bout_toutes_les_tables_et_determinisme` ; ajouté : `test_controle3_mondes.py::test_une_repetition_de_bout_en_bout` (toute la chaîne aux volumes de l'expérience) | couvert |
| 7. Déterminisme | `test_rejeu_moteur.py::test_point_7_memes_graines_memes_sorties_par_empreinte`, `test_rejeu_bout_en_bout.py` (empreintes), `test_rejeu_phase3.py::test_parallelisation_deterministe` ; ici : invariance aux tranches du bootstrap (2.3), générateur déterministe (`test_controle3_mondes.py`), répétitions refaites à l'identique (4.5) | couvert |
| 8. Dépassement établi par max-T | `test_rejeu_maxt.py` : mécanique, dépassement planté détecté, au plus 8,5 % de rejets à tort sur 400 jeux, sur les cellules synthétiques du module `maxt` seulement. Depuis Q13, le même max-T décide le budget de B-tout. **Ajouté** : `test_controle3_point8_b_tout.py`, par toute la chaîne : dépassement planté dans une cellule de B-tout établi ; rien d'établi sans dépassement ; cellule jamais au palier 3 hors de m. Fréquence des R1 à tort aux volumes de l'expérience : section 4 | **manquait** pour les cellules de B-tout ; ajouté, vert |
| Étape 6 élargie : l'étiquette tombe juste quand la vérité est connue | mondes fictifs (sections 2 et 4) | fait ici |

Défauts rendus exécutables : `test_controle3_defauts.py` (section 5 ; comportement actuel en vert, propriété attendue en `xfail` strict).

Suite complète : `env -u ANTHROPIC_API_KEY simulation/.venv/bin/python -m pytest simulation gel/tests simulation/controle3 -q -p no:cacheprovider` → 256 réussis et 2 échecs attendus (`xfail` : les propriétés attendues de G1 et de M1), en 72 s.

## 4. Résultats

### 4.1 Fréquences des étiquettes

⚠ : l'étiquette attendue n'est pas la plus fréquente, ou sort moins de 80 % du temps pour A, B, C ou F (consigne). Intervalle de Wilson à 95 %.

| Monde | Attendu | n | R5 | R1 | R4 | R2 | confirmée | Attendue la plus fréquente ? | Part de l'attendue (IC 95 %) |
|---|---|---|---|---|---|---|---|---|---|
| A | confirmée | 80 | 0 | 0 | 40 | 0 | 40 | égalité avec R4 **⚠** | 50 % (39–61) |
| A-tf | confirmée | 40 | 0 | 0 | 29 | 0 | 11 | non **⚠** | 28 % (16–43) |
| A4 | confirmée | 40 | 0 | 0 | 21 | 16 | 3 | non **⚠** | 8 % (3–20) |
| A-rho0 | confirmée | 30 | 0 | 0 | 2 | 0 | 28 | oui | 93 % (79–98) |
| A-rho7 | confirmée | 30 | 0 | 0 | 23 | 0 | 7 | non **⚠** | 23 % (12–41) |
| B | R1 | 60 | 0 | 60 | 0 | 0 | 0 | oui | 100 % (94–100) |
| B100 | R1 | 20 | 0 | 20 | 0 | 0 | 0 | oui | 100 % (84–100) |
| C | R4 | 25 | 0 | 0 | 25 | 0 | 0 | oui | 100 % (87–100) |
| D | R2 | 50 | 0 | 0 | 23 | 27 | 0 | oui | 54 % (40–67) |
| D-piège | R2 (sens) | 40 | 0 | 0 | 15 | 0 | 25 | non **⚠** | 0 % (0–9) |
| E | confirmée + mention | 50 | 0 | 0 | 11 | 0 | 39 | oui | 78 % (65–87) |
| E-fort | R1 | 30 | 0 | 30 | 0 | 0 | 0 | oui | 100 % (89–100) |
| F1 | R5 | 8 | 8 | 0 | 0 | 0 | 0 | oui | 100 % (68–100) |
| F2 | R5 | 8 | 8 | 0 | 0 | 0 | 0 | oui | 100 % (68–100) |
| K | R2 | 8 | 0 | 0 | 8 | 0 | 0 | non **⚠** | 0 % (0–32) |

### 4.2 Diagnostics par monde

| Monde | point 1 non tenu | ≥ 1 délégable | Haiku WorkBench délégable | les deux témoins battus par le budget | m moyen (B-tout) | mention hors hypothèse sur une cellule jugée hors banque | durée moyenne |
|---|---|---|---|---|---|---|---|
| A | 0 % | 50 % | 36 % | 100 % | 45 | 15 % | 126 s |
| A-tf | 0 % | 28 % | 15 % | 100 % | 44 | 15 % | 127 s |
| A4 | 0 % | 48 % | 38 % | 22 % | 49 | 15 % | 128 s |
| A-rho0 | 0 % | 93 % | 60 % | 100 % | 46 | 17 % | 130 s |
| A-rho7 | 0 % | 23 % | 17 % | 100 % | 44 | 23 % | 127 s |
| B | 100 % | 2 % | 0 % | 92 % | 89 | 30 % | 138 s |
| B100 | 100 % | 0 % | 0 % | 90 % | 111 | 15 % | 139 s |
| C | 0 % | 0 % | 0 % | 68 % | 37 | 12 % | 141 s |
| D | 0 % | 54 % | 48 % | 0 % | 0 | 0 % | 127 s |
| D-piège | 0 % | 62 % | 52 % | 100 % | 1 | 0 % | 128 s |
| E | 0 % | 78 % | 68 % | 100 % | 46 | 100 % | 153 s |
| E-fort | 100 % | 87 % | 57 % | 100 % | 45 | 100 % | 262 s |
| F1 | 0 % | 38 % | 38 % | 100 % | 45 | 0 % | 127 s |
| F2 | 0 % | 62 % | 50 % | 100 % | 42 | 25 % | 126 s |
| K | 0 % | 0 % | 0 % | 0 % | 51 | 12 % | 121 s |

Étiquette quand au moins une configuration est délégable : A 40 sur 40 « confirmée » ; A-tf 11 sur 11 ; A-rho0 28 sur 28 ; A-rho7 7 sur 7 ; E 39 sur 39 ; A4 3 « confirmée » et 16 R2 sur 19 ; D 27 R2 sur 27 ; D-piège 25 « confirmée » sur 25.

Valeur critique du max-T (médianes) : B-tout 1,95 dans A (m ≈ 45), 2,23 dans B (m ≈ 84) ; témoins 2,54 dans A (m = 60).

Charge hors lectures, différence appariée B-tout moins témoin, en moyenne sur les configurations délégables (médianes, en validations pour 100 actions hors lectures) : face au tri par le risque, + 8,7 (A), + 9,0 (A4), + 18,6 (D) : jamais battu par la charge, comme le prévoit Q6 ; face à la liste fixe, − 4,7 (A) et − 6,2 (A4), battue par la charge dans 22 répétitions délégables sur 40 et 12 sur 19 (explication déduite, non décomposée : B-tout finit par déléguer les messages internes de WorkBench, que la liste fixe garde au palier 1), mais + 0,8 dans D (intervalle médian de 0,65 à 0,91), où B-tout ne délègue presque rien.

### 4.3 Mondes signalés et cause

| Monde | Signal | Cause |
|---|---|---|
| A | « confirmée » 50 %, à égalité avec R4 | point 4 seul (aucune configuration délégable dans 40 répétitions) : plan (G1) et puissance (G2). Haiku dans WorkBench : sans erreur et ρ̂ de l'environnement dans 19 répétitions (non certifié) ; une erreur ou plus et non certifié dans 31 |
| A-tf | « confirmée » 28 %, R4 72 % | plan (G1) : Haiku n'a fait aucune erreur sur l'écriture réversible de WorkBench dans 31 répétitions sur 40 ; dans 28, il a reçu le ρ̂ de l'environnement, tiré des erreurs de Sonnet et d'Opus, et n'a pas été certifié |
| A4 | « confirmée » 8 %, R4 52 %, R2 40 % | puissance : témoins à environ 3 fois le budget, établis dans 22 % des répétitions seulement (M2) ; plus G1 et G2 pour le point 4 |
| A-rho7 | « confirmée » 23 % | puissance (G2) : à ρ = 0,7, la taille effective fond |
| D | R2 54 %, R4 46 % | point 4 seul : G1 et G2 |
| D-piège | « confirmée » 62 % au lieu de R2 | plan (M1) : 22 de ces 25 « confirmée » viennent d'une B-tout sans aucun palier 3 ; R4 sinon (G1, G2) |
| K | R4 100 % au lieu de R2 | plan (G1) : sans aucune erreur, ρ̂ = 1 et rien n'est certifiable |
| E | « confirmée » 78 % ; mention dans 100 % | attendu ; les 22 % de R4 viennent du point 4 (G1, G2). La mention sort sur WorkBench à enjeu faible (s ÷ q ≈ 1,21) dans 50 répétitions sur 50, sur le commerce (s ÷ q ≈ 1,40, peu de tâches porteuses) dans 19 sur 50 |

Aucun monde n'a montré de défaut du moteur.

### 4.4 Délégabilité (point 4 seul, 300 répétitions par case)

Part des répétitions avec au moins une configuration délégable, et entre parenthèses Haiku dans WorkBench délégable, selon le multiple de la barre commun à tous les types.

Sans témoin en défaut :

| ρ | 0 × | 0,02 × | 0,05 × | 0,1 × | 0,2 × | 0,3 × | 0,5 × | 1 × |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 % (0 %) | 48 % (21 %) | 76 % (41 %) | 94 % (63 %) | 97 % (71 %) | 94 % (64 %) | 66 % (31 %) | 8 % (4 %) |
| 0,3 | 0 % (0 %) | 13 % (10 %) | 27 % (22 %) | 41 % (34 %) | 51 % (39 %) | 51 % (39 %) | 56 % (30 %) | 36 % (8 %) |
| 0,7 | 0 % (0 %) | 4 % (4 %) | 7 % (6 %) | 13 % (10 %) | 20 % (18 %) | 29 % (22 %) | 30 % (23 %) | 21 % (9 %) |

Avec les témoins en défaut du monde A : à peu près les mêmes valeurs (tableau complet dans `resultats/delegabilite.csv`).

Écriture réversible de Haiku dans WorkBench, à ρ = 0,3 : classée « sous la barre » dans 4 à 31 % des répétitions sans erreur (0,02 à 0,2 × barre), contre 71 à 77 % avec une ou deux erreurs. Taux de certification à tort d'un type exactement à la barre (1 × barre) : section 5, G1.

### 4.5 Reproductibilité

- Les 25 répétitions du premier lancement (14 processus, tranches de 200) sont identiques, champ par champ (hors durées), à celles du second (12 processus, tranches de 50).
- `delegabilite.jsonl` a la même empreinte SHA-256 dans les deux lancements.
- `lancer.py --verifier` : empreintes du code conformes à celles du lancement.

## 5. Défauts trouvés, par gravité

Aucun défaut du moteur n'a été trouvé : dans chaque monde, l'étiquette suit la lettre du plan (points 0 à 5, dans l'ordre de C6). Les écarts à la vérité viennent du plan ou de la puissance des données.

### Graves

**G1. La classe « sous la barre » n'est ni monotone en les erreurs, ni tenue à son risque : c'est la règle de ρ̂ qui décide de R4.** Cause : le plan (5.13), codé à la lettre.
- Ce que dit le plan : ρ̂ « estimée par configuration, tous types mérités réunis. Si elle n'est pas calculable (aucune erreur, ou une seule tâche), on prend celle de l'environnement, tous modèles réunis ; si elle ne l'est toujours pas, ρ̂ = 1 » ; et (section 8) des bornes à zéro erreur « sur la taille effective ou au niveau des tâches, jamais sur les écritures brutes ».
- **Zéro erreur dans un environnement** : ρ̂ = 1, la taille effective devient le nombre de tâches porteuses (environ 185 pour l'écriture réversible de WorkBench en calibration, pour 394 exigées à enjeu faible, annexe A2 ; bien moins ailleurs). Aucune configuration de cet environnement ne peut être « sous la barre ». Des agents parfaits donnent R4 : 0 % de configurations délégables à 0 × barre dans l'étude, quel que soit ρ ; monde K : R4 dans 8 répétitions sur 8, alors que B-tout y atteint le palier 3 dans 51 cellules en moyenne.
- **Zéro erreur dans la configuration** : elle prend le ρ̂ de l'environnement, fait des erreurs des autres modèles. Sonnet et Opus n'ont qu'un passage dans WorkBench : leurs grappes ont une écriture, et une seule de leurs erreurs donne ρ̂ = 1 (test `test_g1_la_meme_erreur_chez_un_autre_modele_decide_de_la_classe_de_haiku`). Dans le monde A-tf, c'est le cas de 28 répétitions sur 40 : Haiku, sans erreur sur l'écriture réversible de WorkBench, reçoit le ρ̂ de l'environnement et n'est pas certifié.
- **Une ou deux erreurs dispersées** dans des tâches de plusieurs écritures : ρ̂ = 0, la borne est calculée sur les écritures brutes. Un type **exactement à la barre** est alors certifié « sous la barre » à tort, à ρ = 0,3, dans 23 % des répétitions (commerce, Haiku ; IC à 95 % : 18 à 28 %), 15 % (aviation, Haiku ; 11 à 20 %) et 8 % (WorkBench, Haiku ; 5 à 11 %), au lieu de 5 % au plus ; à ρ = 0, le risque est tenu (0,5 à 3,7 %). Ce sont surtout ces trois configurations : ailleurs, le volume manque même avec ρ̂ = 0.
- **Conséquence sur l'étiquette** : la probabilité qu'au moins une configuration soit délégable n'est pas monotone en la fiabilité des agents. À ρ = 0,3, sans témoin en défaut : 0 % (agents parfaits), 13 % (0,02 × barre), 27 % (0,05), 41 % (0,1), 51 % (0,2 et 0,3), 56 % (0,5), et encore 36 % à 1 × barre, où toute certification est à tort. Des agents plus fiables obtiennent donc plus souvent R4 : monde A-tf (0,05 × barre), « confirmée » 11 fois sur 40 (28 %), contre 40 sur 80 (50 %) dans le monde A (0,2 × barre) ; agents parfaits, R4 toujours.
- Pistes, à trancher par Otsoa (aucune n'est appliquée) : une taille effective qui ne dépend pas de la présence d'erreurs (ρ fixé d'avance, par exemple la borne haute de la plage de 5.16, ou ρ̂ borné en dessous par cette valeur) ; ou une borne par bootstrap des tâches. Toute retouche se revérifie avec l'étude de délégabilité (`harnais.delegabilite`, environ 8 minutes) et ces mondes.

**G2. À ces volumes, R4 est l'issue la plus probable pour des agents fiables dès que l'hétérogénéité entre tâches est modérée.** Cause : limite de puissance des données (volumes de 2.3 et 2.4, partage moitié-moitié, Clopper-Pearson unilatéral à 5 % sur la taille effective), aggravée par G1. Ce n'est pas un défaut du moteur.
- Une seule configuration peut atteindre le volume de certification à enjeu faible : Haiku dans WorkBench (5 passages, environ 920 écritures réversibles en calibration, pour 394 écritures effectives exigées, annexe A2), et seulement si ρ̂ est petit. Les autres ne le peuvent pas, quelle que soit la fiabilité des agents (banque, Haiku : 154 et 193 écritures pour 257 ; WorkBench, Sonnet et Opus : 184 pour 394 ; commerce, Sonnet et Opus : environ 90 pour 112), sauf par la voie à tort de G1 (ρ̂ = 0 avec une ou deux erreurs, commerce et aviation chez Haiku).
- Étude (0,2 × barre, sans témoin en défaut) : au moins une configuration délégable dans 97 % des répétitions à ρ = 0, 51 % à ρ = 0,3, 20 % à ρ = 0,7. Mondes (0,2 × barre) : au moins une configuration délégable dans 93 % des répétitions à ρ = 0 (A-rho0), 50 % à ρ = 0,3 (A) et 23 % à ρ = 0,7 (A-rho7) ; dans D, 54 %.
- Effet : R4 « rien à déléguer » sort alors que des types sont sous la barre, et même tous (mondes D et K). Ce que R4 mesure ici est « délégabilité non démontrée à ces volumes », pas « rien à déléguer » (1.5).
- Piste : écrire avant le gel ce que R4 peut signifier et ce qu'il ne peut pas signifier, comme RF3 pour R1 et « confirmée » (1.4) ; et annoncer que l'étiquette dépendra surtout de la certification de Haiku dans WorkBench.

### Moyens

**M1. « Confirmée » n'exige aucune délégation de B-tout.** Cause : le plan (5.14, points 2 et 5). Monde D-piège : « confirmée » dans 25 répétitions sur 40, dont 22 où B-tout n'atteint le palier 3 dans aucune cellule (m = 0) ; R4 dans les 15 autres. Le point 2 bat un témoin dès que son dépassement est établi, sans regarder ce que B-tout délègue ; « tout faire valider » obtiendrait la même étiquette. Le plan le dit à moitié (1.4 : « confirmée » ne garantit rien aux niveaux où B-tout n'a rien délégué), mais la question 1 (« la règle donne-t-elle l'autonomie là où elle est méritée ? ») n'est alors pas tranchée. En pratique, le cas extrême est rare à ces volumes : quand Haiku est certifié dans WorkBench, B-tout y atteint en général le palier 3 (N = 138 pour environ 900 écritures). Mais l'étiquette ne dit pas combien B-tout délègue. Pistes : exiger aussi une baisse des validations établie par rapport à « tout faire valider » sur les configurations délégables (5.12, point 7), ou un palier 3 atteint dans au moins une configuration délégable ; ou l'écrire comme limite en 1.4.

**M2. Les témoins ne sont pris en défaut que pour un dépassement net, sur un type à beaucoup d'écritures indépendantes.** Cause : puissance. Monde A (témoins à 10 × barre, dépassement vrai d'environ 8 fois le budget) : les deux témoins sont battus par le budget dans 100 % des répétitions (borne max-T la plus haute : médiane 4,0 fois le budget). Monde A4 (4 × barre, environ 3 fois le budget) : 22 % seulement, d'où R2 dans 16 des 19 répétitions où une configuration est délégable. Ces mondes placent le défaut des témoins là où la puissance est la plus grande (WorkBench, Sonnet et Opus : 276 tâches, une écriture par tâche) ; dans le commerce ou l'aviation, avec une dizaine de tâches porteuses ou moins, il faudrait des dépassements bien plus grands (déduit, non simulé). Conséquence : « confirmée » demande, en pratique, un témoin qui dépasse le budget de plusieurs fois sur un type à beaucoup d'écritures indépendantes ; sinon R2, puisque le tri par le risque, là où il tient le budget, demande forcément moins de validations (Q6).

**M3. R1 n'est établi que pour une violation nette ; jamais à tort ici.** Cause : puissance, conforme à la limite déclarée de Q13. B (N ÷ 10, dépassement vrai de 3 à 6 fois le budget) : R1 60 fois sur 60 ; B100 : 20 sur 20 ; E-fort (dépassement vrai d'environ 1,4 fois, valeurs centrales de 1,35 à 1,47 fois le budget) : 30 sur 30. E-fort est le cas le plus favorable à la détection (ρ = 0, quatre fois plus d'écritures réversibles qu'en 2.4, soit 9 200 pour Haiku en commerce) ; avec de l'hétérogénéité entre tâches, la puissance baisserait (non simulé). Aucun R1 à tort sur 409 répétitions où B-tout tient le budget. Une seule fois (F2), une cellule de B-tout a dépassé le budget en valeur centrale (1,49 fois) : une seule erreur dans une petite configuration (aviation, Sonnet ou Opus, environ 190 écritures : le budget y vaut moins d'une erreur) ; non établi, à juste titre.

**M4. Le mélange du pilote met déjà la banque, à enjeu faible, hors de l'hypothèse de construction.** Cause : le plan (q vient des écritures attendues ; au pilote, les agents de la banque n'écrivent que des types faibles, 2.4 et annexe A4). Avec ce mélange, s ÷ q = 364 ÷ 165 ≈ 2,21 : la borne de construction vaut 0,95 × 2,21 ≈ 2,1 fois le budget, et la mention « garantie hors hypothèse » sort dans presque toutes les répétitions où la banque a des cellules jugées (421 répétitions sur 421 où la cellule de Haiku dans la banque, à enjeu faible, est jugée). Sans effet sur l'étiquette : un agent régulier ne dépasse pas le budget même ainsi (au plus environ 0,77 fois, calcul de l'AOQL régulier avec N = 90). Mais 1.4 (« tenu par construction ») ne couvre pas la banque à enjeu faible : à écrire avant le gel (test `test_m4_s_sur_q_de_la_banque_a_enjeu_faible_avec_le_melange_de_2_4`).

### Mineurs

**m1. Mention « garantie hors hypothèse » aussi sur des cellules « tenue, non mise à l'épreuve ».** Le moteur la calcule pour toute cellule qui n'est pas « sans objet » ; 1.4 lie l'écart de mélange aux niveaux où B-tout atteint le palier 3. C'est le cas dans 441 répétitions sur 519, surtout pour Sonnet et Opus dans la banque. Texte du plan ambigu ; effet seulement descriptif. Piste : ne la publier que pour les cellules jugées.

**m2. Deux tests de 5.16 manquaient** (rafale dans le moteur et pour N > 170 ; max-T sur les cellules de B-tout depuis Q13) : ajoutés, verts (section 3).

**m3. Le monde D n'est pas tout à fait « jamais au palier 3 ».** Avec N × 20, B-tout atteint encore le palier 3 dans quelques répétitions, en aviation à enjeu faible (N = 240 pour 50 à 300 écritures réversibles selon les tâches tirées) et dans quelques scénarios. C'est un défaut de construction du monde, pas du moteur ; B-tout atteint le palier 3 dans 2 répétitions sur 50 de D (aviation, Haiku) et dans 4 sur 40 de D-piège ; les 22 « confirmée » sans aucun palier 3 de D-piège sont comptées à part.


## 6. Ce qui reste

1. **Décisions d'Otsoa avant le gel** (aucune correction n'est faite ici) :
   - G1 : la règle de ρ̂ pour les classes de 5.12 (point 4) : garder, ou rendre la taille effective indépendante de la présence d'erreurs ;
   - G2 : ce que R4 peut signifier et ce qu'il ne peut pas signifier, à écrire en 1.4 et 1.5 ; et, s'il le souhaite, revoir le critère de délégabilité ;
   - M1 : faut-il qu'une délégation de B-tout soit exigée pour « confirmée » ;
   - M4 : écrire en 1.4 que la banque, à enjeu faible, sort de l'hypothèse de construction si le mélange du pilote se maintient.
2. **Après une retouche de G1, G2 ou M1** : relancer l'étude de délégabilité (8 minutes) et les mondes (environ 1 h 45 sur 12 processus) ; le code est prêt (`lancer.py`, nouveau dossier de résultats).
3. **Non couvert par ce contrôle** :
   - le désaccord persistant (B2) dans un monde complet (seul le test du moteur le couvre) ; les refusées (part nulle) ; les analyses secondaires du point 6 et les mentions « fragile », sans effet sur l'étiquette ;
   - R0 = B = 2 000 : non rejoués ; effet attendu faible sur les étiquettes, sauf aux marges du max-T ;
   - la couverture de la moyenne des différences de charge sur les configurations délégables, qui décide le point 2 quand un témoin n'est pas battu par le budget (5.16, point 5, ne simule qu'une configuration)  ; dans ces mondes, quand le point 2 s'est joué sur la charge, l'écart était net (section 4.2) ;
   - le lanceur (`banc/`, autre agent) et l'instrument : hors de ce contrôle.
4. **Seconde relecture indépendante du plan figé** (section 7, étape 7) : lui transmettre ce rapport, en particulier G1, G2 et M1.

## 7. Deuxième passage (06/11)

> Après les décisions d'Otsoa sur Q14 (délégable sur la meilleure estimation) et Q15 (« tout faire valider » en troisième témoin), et la règle G1 de ρ̂ (plancher 0,3 par environnement), codées dans le moteur (phase 4, commit 07ae30d). Le premier passage est au commit bbbaa72. Mêmes interdits ; aucun appel payant, aucun commit.

### 7.1 En bref

- **Les corrections tiennent.** Les mondes A, A-tf, A-rho0, A-rho7 et E donnent « confirmée » dans 100 % des répétitions (premier passage : 23 à 93 %) ; K (agents parfaits) et D donnent R2, « délégation inférieure à un témoin », dans 100 % ; D-piège donne « confirmée » dans 100 %, légitimement (délégation au palier 2) ; le nouveau monde D-inerte (règle bloquée au palier 1, témoins en défaut) donne R2, « aucune délégation établie », dans 40 répétitions sur 40. B, B100 et E-fort : R1 à 100 % ; F1 et F2 : R5 à 100 % ; aucun R1 à tort (0 sur 449), aucun témoin battu à tort (0 sur 58).
- **Le classement prouvé est monotone et tient son risque** : un type pile à la barre n'est certifié à tort que dans 0 à 3,7 % des répétitions (premier passage : jusqu'à 23 %) ; les agents parfaits sont certifiés dans 92 à 93 %.
- **Deux mondes restent signalés** : A4 (« confirmée » 22 %, R2 sinon : témoins à environ 3 fois le budget, limite de puissance déjà connue, M2) et C (agents 5 fois au-dessus de toutes les barres : R4 jamais ; R2 dans 15 répétitions sur 25, « confirmée » dans 10).
- **Deux défauts nouveaux, du plan** (7.7) : **N1**, R4 n'est plus atteignable à ces volumes (une configuration est délégable dans 100 % des répétitions, même à 10 fois la barre, par des types à enjeu fort ou moyen sans erreur faute de volume) ; **N2**, l'oracle aligné sur Q14 délègue sans preuve l'argent et l'écriture durable, et dépasse le budget dans 256 répétitions sur 559, ce qui fausse la part du gain de l'oracle. Un résidu mineur de G1 : les grappes d'une écriture de Sonnet et d'Opus dominent ρ̂ de WorkBench.
- Aucun défaut du moteur.

### 7.2 Ce qui a changé, et ce que j'ai mis à jour

- **Moteur** (phase 4, commit 07ae30d, lu seulement pour l'appeler) : délégable = au moins un type mérité dont le taux estimé au jeu de calibration est au plus la barre (Q14) ; ρ̂ par environnement avec un plancher de 0,3, une configuration d'au moins 10 erreurs dans au moins 5 tâches prenant le plus grand des deux, un environnement sans erreur prenant le ρ̂ de tous les environnements réunis, plus de ρ̂ = 1 par défaut (G1) ; « tout faire valider » en troisième témoin, battu seulement par la charge (intervalle strictement sous 0), et mention de R2 : « aucune délégation établie » ou « délégation inférieure à un témoin » (Q15) ; mention « garantie hors hypothèse » sur les seules cellules jugées (m1).
- **Tests du contrôle 3** (`tests/test_controle3_defauts.py`, `tests/test_controle3_mondes.py`) :
  - G1 : l'ancien test du repli (ρ̂ = 1 sans erreur, ρ̂ = 0 avec une erreur) devient `test_g1_regle_du_06_11_plancher_sans_erreur_et_avec_une_erreur` ; `test_g1_propriete_attendue_monotonie` perd sa marque `xfail` (0, 1, 2 puis 5 erreurs : la classe ne devient jamais plus favorable) ; `test_g1_la_meme_erreur…` devient `test_g1_residu_…`, qui décrit le résidu de 7.7 ;
  - M1 : `test_m1_regle_sans_palier_3_delegue_au_palier_2_et_obtient_confirmee` (décision 4 : la règle du premier passage délègue au palier 2, bat « tout faire valider » et obtient « confirmée », légitimement) ; la propriété attendue devient `test_m1_propriete_attendue_regle_inerte_r2_aucune_delegation_etablie`, sans marque : une règle bloquée au palier 1 obtient R2, « aucune délégation établie » ; `test_regle_inerte_du_harnais` ;
  - `test_une_repetition_de_bout_en_bout` : trois témoins au point 2 ;
  - nouveau : N1 (7.7), comportement actuel en vert et propriété attendue en `xfail` strict.
- **Harnais** : règle inerte (N = 10⁹ et aucun palier 2), mention de R2 et oracle (descriptif) dans les sorties ; l'étude de délégabilité suit la règle du rejeu (G1 et Q14, `classes.classes_tous_environnements`) et relève à part le classement prouvé.
- **5.16, point 9 (règle inerte, nouveau)** : couvert par le test du moteur `test_rejeu_phase4.py::test_regle_inerte_donne_r2_aucune_delegation_etablie`, par `test_m1_propriete_attendue_regle_inerte_r2_aucune_delegation_etablie` (ici) et par le monde D-inerte, aux volumes de l'expérience (7.5).

### 7.3 Étiquettes attendues revues

| Monde | Premier passage | Second passage | Pourquoi |
|---|---|---|---|
| D (agents à 0,2 × barre, B-tout avec N × 20, témoins qui tiennent le budget) | R2 | R2, « délégation inférieure à un témoin » | B-tout n'atteint presque jamais le palier 3, mais agit au palier 2 sur les écritures réversibles. C'est une délégation (décision 4 ; 5.14, point 2, lecture du 06/11) : seules les corrections entrent dans la charge, et B-tout bat « tout faire valider ». Les témoins tiennent le budget, et le tri par le risque demande forcément moins de validations (Q6). |
| D-piège (D avec les témoins en défaut de A) | R2 (au sens du premier passage) | confirmée | Même délégation au palier 2, et les deux témoins dépassent le budget : B-tout délègue de façon établie, avec moins de validations que « tout faire valider ». « Confirmée » est la réponse du plan, et elle est légitime. |
| D-inerte (nouveau : D-piège avec B-tout bloquée au palier 1) | — | R2, « aucune délégation établie » | Ni palier 3 (N = 10⁹) ni palier 2 : la règle ne délègue rien. Les témoins dépassent le budget, mais « tout faire valider » n'est pas battu (Q15 ; 5.16, point 9). |
| K (agents parfaits) | R2 | R2, « délégation inférieure à un témoin » | B-tout délègue ; les témoins tiennent le budget. |
| C (5 × barre partout) | R4 | R4, au sens de 1.5 | Inchangé : 1.5 dit que R4 « signale des agents nettement peu fiables ». Voir N1. |

### 7.4 Lancement

- Mêmes réglages figés : R0 = B = 200, K = 10, e = 5 %, jackknife-t, même graine ; 12 processus, tranches de 50. 559 répétitions : les 519 du premier passage et 40 pour D-inerte. Étude de délégabilité : 300 répétitions par case, les multiples 2, 5 et 10 ajoutés (19 800 tirages).
- Les 15 mondes du premier passage gardent leurs données et les graines du moteur (D-inerte est ajouté en dernier) : chaque répétition est appariée à celle du premier passage, et seul le moteur change.
- Durée : 2 h 21 (délégabilité 11 min ; mondes 2 h 10), plus longue qu'au premier passage : une machine virtuelle extérieure à ce contrôle occupait six cœurs pendant une partie du lancement. `lancer.py --verifier` : empreintes conformes. Les 519 répétitions appariées ont bien les mêmes volumes et la même graine du moteur qu'au premier passage.

### 7.5 Fréquences des étiquettes

⚠ : l'étiquette attendue n'est pas la plus fréquente, ou sort moins de 80 % du temps pour A, B, C ou F. Pour R2, la mention attendue est comptée.

| Monde | Attendu (revu) | n | R5 | R1 | R4 | R2 (aucune délégation / inférieure à un témoin) | confirmée | Attendue la plus fréquente ? | Part de l'attendue (IC 95 %) | Premier passage, même étiquette |
|---|---|---|---|---|---|---|---|---|---|---|
| A | confirmée | 80 | 0 | 0 | 0 | 0 | 80 | oui | 100 % (95–100) | 50 % |
| A-tf | confirmée | 40 | 0 | 0 | 0 | 0 | 40 | oui | 100 % (91–100) | 28 % |
| A4 | confirmée | 40 | 0 | 0 | 0 | 31 (0 / 31) | 9 | non **⚠** | 22 % (12–38) | 8 % |
| A-rho0 | confirmée | 30 | 0 | 0 | 0 | 0 | 30 | oui | 100 % (89–100) | 93 % |
| A-rho7 | confirmée | 30 | 0 | 0 | 0 | 0 | 30 | oui | 100 % (89–100) | 23 % |
| B | R1 | 60 | 0 | 60 | 0 | 0 | 0 | oui | 100 % (94–100) | 100 % |
| B100 | R1 | 20 | 0 | 20 | 0 | 0 | 0 | oui | 100 % (84–100) | 100 % |
| C | R4 (au sens de 1.5) | 25 | 0 | 0 | 0 | 15 (7 / 8) | 10 | non **⚠** | 0 % (0–13) | 100 % |
| D | R2, délégation inférieure | 50 | 0 | 0 | 0 | 50 (0 / 50) | 0 | oui | 100 % (93–100) | R2 54 % |
| D-piège | confirmée | 40 | 0 | 0 | 0 | 0 | 40 | oui | 100 % (91–100) | 62 % |
| E | confirmée + mention | 50 | 0 | 0 | 0 | 0 | 50 | oui | 100 % (93–100) ; mention hors banque 100 % | 78 % |
| E-fort | R1 | 30 | 0 | 30 | 0 | 0 | 0 | oui | 100 % (89–100) | 100 % |
| F1 | R5 | 8 | 8 | 0 | 0 | 0 | 0 | oui | 100 % (68–100) | 100 % |
| F2 | R5 | 8 | 8 | 0 | 0 | 0 | 0 | oui | 100 % (68–100) | 100 % |
| K | R2, délégation inférieure | 8 | 0 | 0 | 0 | 8 (0 / 8) | 0 | oui | 100 % (68–100) | 0 % (R4 100 %) |
| D-inerte (nouveau) | R2, aucune délégation | 40 | 0 | 0 | 0 | 40 (40 / 0) | 0 | oui | 100 % (91–100) | — |

Passages appariés (mêmes données, même graine du moteur) : R4 → « confirmée » dans A (40), A-tf (29), A-rho7 (23), A-rho0 (2), E (11), D-piège (15), A4 (6) ; R4 → R2 dans A4 (15), D (23), K (8) ; C : R4 → « confirmée » (10), R2 « délégation inférieure » (8), R2 « aucune délégation » (7). Aucune répétition de B, B100, E-fort, F1 ou F2 ne change.

Mondes signalés et cause :

| Monde | Signal | Cause |
|---|---|---|
| A4 | « confirmée » 22 % ; R2 « délégation inférieure à un témoin » 78 % | puissance (M2, déjà connue) : les témoins dépassent le budget d'environ 3 fois, établi dans 22 % des répétitions ; « tout faire valider » est toujours battu, la liste fixe et le tri par le risque ne le sont pas par la charge (B-tout demande 3,5 et 12,5 validations de plus pour 100 actions, médianes). Plus de R4 : la part du point 4 a disparu |
| C | R4 jamais ; R2 60 % (7 « aucune délégation établie », 8 « délégation inférieure à un témoin ») ; « confirmée » 40 % | plan (N1) : des configurations deviennent délégables par des types à enjeu fort ou moyen sans erreur (4 à 11 configurations sur 12 selon la répétition) ; l'étiquette passe au point 2. « Confirmée » sort quand une configuration de WorkBench ou de la banque est parmi les délégables (9 fois sur 10) : B-tout y agit au palier 2 sur les écritures réversibles (décision 4 ; 3,8 à 5,8 % d'erreurs, sous le taux « bon » du palier 2, 10 %), bat « tout faire valider », et les témoins dépassent le budget. C'est la lettre du plan du 06/11 ; mais « confirmée » ne dit alors rien du palier 3 : aucun type n'y est sous sa barre |

Autres vérifications : « garantie hors hypothèse » sur aucune cellule non jugée (m1 corrigé) ; la cellule de Haiku dans la banque, à enjeu faible, porte la mention chaque fois qu'elle est jugée (421 sur 421, M4).

### 7.6 Délégabilité et classement prouvé

Part des répétitions où au moins une configuration est délégable selon Q14 / délégable par un type faible seulement / délégable selon le classement prouvé (borne haute au plus la barre ; publié, sans décider R4). Tous les types au même multiple de la barre, sans témoin en défaut, 300 répétitions par case.

| ρ | 0 × | 0,05 × | 0,2 × | 0,5 × | 1 × | 2 × | 5 × | 10 × |
|---|---|---|---|---|---|---|---|---|
| 0 | 100 / 100 / 92 % | 100 / 100 / 60 % | 100 / 100 / 18 % | 100 / 100 / 1 % | 100 / 100 / 0 % | 100 / 99 / 0 % | 100 / 38 / 0 % | 100 / 5 / 0 % |
| 0,3 | 100 / 100 / 93 % | 100 / 100 / 71 % | 100 / 100 / 30 % | 100 / 100 / 9 % | 100 / 100 / 1 % | 100 / 99 / 0 % | 100 / 58 / 0 % | 100 / 15 / 0 % |
| 0,7 | 100 / 100 / 92 % | 100 / 100 / 79 % | 100 / 100 / 44 % | 100 / 100 / 21 % | 100 / 100 / 4 % | 100 / 99 / 0 % | 100 / 78 / 0 % | 100 / 37 / 0 % |

Tableau complet (multiples 0,02, 0,1 et 0,3 ; avec témoins en défaut) : `resultats_v2/delegabilite.csv`.

- **Monotone ?** Oui : aucune case ne monte quand la fiabilité baisse. Mais la délégabilité de Q14 est plate : 100 % des répétitions ont au moins une configuration délégable, de 0 à 10 fois la barre, à tout ρ, avec ou sans témoins en défaut (N1, 7.7).
- **Agents parfaits** : délégables dans 100 % des répétitions (au lieu de 0 % au premier passage) ; le classement prouvé les certifie dans 92 à 93 % des répétitions.
- **Agents pile à la barre** : délégables dans 100 % des répétitions selon Q14 (un taux estimé tombe sous la barre environ une fois sur deux, et il y a une trentaine de types) ; le classement prouvé ne les certifie presque jamais (0 à 4 % des répétitions, toutes configurations).
- **Types qui rendent une configuration délégable quand les agents sont nettement peu fiables** (ρ = 0,3, 5 × barre ; configurations × répétitions) : argent en aviation (845 sur 900) et en commerce (829), écriture durable en aviation (575) et dans WorkBench (346) ; les types faibles bien moins (banque, réversible 115 ; WorkBench, messages 65). À 10 × barre : argent en aviation encore 832 sur 900. Ce sont des types sans erreur faute de volume : à 5 × barre, l'argent de l'aviation attend moins d'une erreur sur toute la calibration de Haiku.

**Certification à tort par le classement prouvé, nouvelle règle de ρ̂** (type exactement à la barre, 1 × barre, sans témoin en défaut ; part des répétitions où il est dit « sous la barre » ; nominal 5 % au plus) :

| ρ | WorkBench, Haiku, réversible | commerce, Haiku, réversible | aviation, Haiku, réversible | tous les types faibles réunis |
|---|---|---|---|---|
| 0 | 0,3 % (1 sur 300 ; IC 0,1–1,9 %) | 0 % (0 sur 300) | 0 % (0 sur 216) | 1 sur 5 148 |
| 0,3 | 1 % (3 sur 300 ; IC 0,3–2,9 %) | 0 % (0 sur 300) | 0 % (0 sur 218) | 3 sur 5 154 |
| 0,7 | 3,7 % (11 sur 300 ; IC 2,1–6,4 %) | 0 % (0 sur 300) | 0 % (0 sur 205) | 11 sur 5 115 |

Le risque est tenu (premier passage : jusqu'à 23 % en commerce à ρ = 0,3). ρ̂ médian 0,30 (plancher) à ρ = 0 et 0,3 ; 0,33 à 0,42 à ρ = 0,7 : le plancher couvre ρ = 0,3 mais pas ρ = 0,7, d'où les 3,7 % de WorkBench à ρ = 0,7, encore sous 5 % (mais l'intervalle va jusqu'à 6,4 %). Toutes les certifications à tort sont dans WorkBench, chez Haiku.

**Avec les témoins en défaut** (erreurs de Sonnet et d'Opus sur l'écriture réversible de WorkBench), le classement prouvé ne certifie plus rien dans WorkBench, même pour un Haiku parfait : 0 % dans toutes les cases (ρ̂ médian de Haiku 0,62 à 0,67 au lieu de 0,30). Voir le résidu de G1, 7.7.

### 7.7 Défauts, après correction

**Corrigés et vérifiés** : G1 (le classement prouvé est monotone et tient son risque : 7.6 ; agents parfaits délégables), G2 (R4 ne sort plus pour des agents fiables : aucun R4 dans A, A-tf, A4, A-rho0, A-rho7, D, E ni K), M1 (la règle inerte obtient R2, « aucune délégation établie », 40 fois sur 40 dans le monde D-inerte), m1 (la mention « garantie hors hypothèse » ne sort plus que sur des cellules jugées : aucune mention sur une cellule non jugée, sur 559 répétitions). Aucun défaut du moteur : dans chaque monde, l'étiquette suit la lettre du plan du 06/11.

**N1 (nouveau, moyen à grave ; cause : le plan, Q14) : R4 n'est plus atteignable à ces volumes.**
- Q14 rend une configuration délégable dès qu'un type mérité, n'importe lequel, a un taux estimé au plus la barre. Les types à enjeu fort, et souvent à enjeu moyen, n'ont presque jamais d'erreur à ces volumes, quelle que soit la fiabilité : à 5 × barre, l'argent de l'aviation attend moins d'une erreur sur toute la calibration de Haiku (environ 830 écritures pour une barre de 1/12 020). Leur taux estimé est alors 0, « sous la barre » par manque de données.
- Étude (7.6) : au moins une configuration délégable dans 100 % des répétitions, de 0 à 10 fois la barre sur tous les types, à tout ρ. Monde C (5 × barre partout) : R4 jamais (0 sur 25) ; R2 dans 15 répétitions et « confirmée » dans 10. 1.5 annonce que R4 « signale des agents nettement peu fiables » : ce n'est plus vrai, R4 ne peut presque plus sortir.
- Même restreinte aux types faibles, la meilleure estimation laisse délégables des agents 2 fois au-dessus de la barre dans 98 à 99 % des répétitions, et 5 fois au-dessus dans 38 à 78 % (selon ρ) : peu de tâches porteuses et de l'hétérogénéité font souvent tomber le taux estimé sous la barre.
- Effet sur l'étiquette : elle passe au point 2. Dans C, R2 (15 fois sur 25 : 7 « aucune délégation établie », 8 « délégation inférieure à un témoin ») ou « confirmée » (10 fois), quand une configuration de WorkBench ou de la banque est parmi les délégables : B-tout y agit au palier 2 sur les écritures réversibles, bat « tout faire valider », et les témoins dépassent le budget (7.5). C'est cohérent avec la décision 4 et avec la lecture de Q14 (une configuration délégable par chance ne rend pas « confirmée » plus facile : il faut encore battre les trois témoins). Mais R4 et son sens disparaissent, et « confirmée » peut sortir sans qu'aucun type soit sous la barre du palier 3 : à écrire en 1.4 si la règle est gardée.
- Pistes, à trancher par Otsoa : ne compter que les types dont le volume permet de voir au moins quelques erreurs à la barre (par exemple n_eff × barre ≥ 3) ; ou les seuls types où B-tout peut atteindre le palier 3 à ces volumes (l'enjeu faible, 2.4) ; ou garder la règle et écrire en 1.5 que R4 n'est plus atteignable à ces volumes. Tests : `test_n1_…` (comportement actuel) et `test_n1_propriete_attendue_…` (`xfail` strict).

**N2 (nouveau, moyen ; cause : le plan, Q14, « l'oracle délègue de même ») : l'oracle délègue au palier 3, sans preuve, l'argent et l'écriture durable.**
- Aligné sur Q14, l'oracle donne le palier 3 à tout type au taux estimé sous la barre, donc aux types à enjeu fort ou moyen sans erreur faute de volume : dans 100 % des répétitions de tous les mondes, il délègue à enjeu moyen ou fort (7.5).
- Monde C (agents 5 fois au-dessus de toutes les barres), essai sur une répétition hors lancement : l'oracle demande 40 à 52 validations pour 100 actions en aviation et en commerce, contre 91 à 100 pour B-tout, parce qu'il exécute seul l'argent ; dans WorkBench, chez Sonnet, il dépasse le budget moyen de 5,9 fois. Sur le lancement : la plus haute valeur centrale des dégâts en plus de l'oracle dépasse le budget dans 256 répétitions sur 559 (C : 18 sur 25, médiane 6 fois le budget ; D : 29 sur 50 ; A : 24 sur 80). Au premier passage, l'oracle ne déléguait que les types prouvés.
- Effet : aucun sur l'étiquette ; mais la part du gain de l'oracle, publiée avec son intervalle (1.3, point 5 ; 5.12, point 6), se calcule contre un oracle qui délègue de l'argent sans preuve et peut dépasser le budget. Elle paraîtra petite pour de mauvaises raisons. Piste : un oracle sur le classement prouvé (comme au premier passage), ou sur la vraie valeur quand elle est connue (mondes fictifs), ou restreint aux types où la délégation est atteignable.

**Résidu de G1 (mineur depuis Q14 ; cause : l'estimateur d'analyse de variance, 5.13) : les grappes d'une écriture dominent ρ̂ de l'environnement.**
- Sonnet et Opus n'ont qu'un passage dans WorkBench. Une seule de leurs erreurs, dans une grappe d'une écriture, donne ρ̂ = 1 pour tout l'environnement (`test_g1_residu_…`) ; avec les témoins en défaut, ρ̂ de Haiku vaut 0,62 à 0,67 (médiane) même quand Haiku ne fait aucune erreur, et le classement prouvé ne certifie plus rien dans WorkBench (0 % dans toutes les cases de l'étude avec témoins en défaut, 7.6).
- Effet : aucun sur l'étiquette (Q14) ; le classement prouvé publié, la garantie et les types devenus mauvais en dépendent (ils deviennent très prudents dans WorkBench dès que Sonnet ou Opus se trompent). Piste : estimer ρ̂ sans les grappes d'une écriture, qui n'apportent aucune information sur la corrélation intra-tâche.

**Toujours vrais** (premier passage) : M2 (témoins pris seulement pour un dépassement net : A4, témoins à environ 3 fois le budget, battus par le budget dans 22 % des répétitions), M3 (R1 seulement pour une violation nette ; jamais à tort : B, B100 et E-fort à 100 % ; 0 sur 449 à tort), M4 (banque à enjeu faible hors hypothèse de construction : mention dans 421 répétitions sur 421 où la cellule de Haiku dans la banque, à enjeu faible, est jugée).

### 7.8 Ce qui reste

1. **Décisions d'Otsoa avant le gel** :
   - N1 : garder la délégabilité de Q14 sur tous les types (R4 n'est plus atteignable à ces volumes, à écrire en 1.5) ou la restreindre aux types dont le volume permet de voir des erreurs à la barre ;
   - N2 : l'oracle de référence de la part du gain (Q14 aligné, classement prouvé, ou restreint aux types atteignables) ;
   - écrire en 1.4 que « confirmée » peut venir de la seule délégation au palier 2, sans aucun type sous la barre du palier 3 (monde C), puisque la décision 4 compte le palier 2 comme délégation.
2. **Résidu de G1** : sans effet sur l'étiquette ; à corriger si le classement prouvé, la garantie et les types devenus mauvais doivent rester informatifs dans WorkBench.
3. **Après une retouche** : relancer `lancer.py` dans un nouveau dossier (étude de délégabilité environ 11 minutes, mondes environ 2 heures sur 12 processus).
4. **Non couvert**, comme au premier passage : le désaccord persistant (B2) dans un monde complet, les refusées, R0 = B = 2 000, les analyses secondaires, la couverture de la moyenne des différences de charge. Le lanceur et ses deux vagues (`entrees.charger_entrees_vagues`) : hors de ce contrôle.

## 8. Troisième passage (06/11)

> Après N1 (délégabilité lue sur le taux médian, tranché par la recherche à la demande d'Otsoa, rapport `reports/Délégabilité et strates sans données.md`), le correctif du résidu de G1 (ρ̂ estimé sans les grappes d'une écriture), l'oracle aligné sur la même règle (N2) et le garde-fou « volume insuffisant » : moteur au commit 3514d34. Le second passage est au commit 305f37a. Mêmes réglages, mêmes données, mêmes graines du moteur : chaque répétition est appariée à celle du second passage. Aucun appel payant.

### 8.1 En bref

- **N1 est corrigé.** Le monde C (agents 5 fois au-dessus de toutes les barres) donne R4 dans 25 répétitions sur 25 (second passage : 0). « Volume insuffisant » ne sort jamais : aux volumes prévus, il y a toujours un type jugeable.
- **R4 sort aussi dans 2 des 310 répétitions où « confirmée » est attendue** (A-rho7 : 1 sur 30 ; E : 1 sur 50 ; second passage : aucune). Dans les deux, Haiku dans WorkBench, la configuration qui porte la délégabilité, tire bien plus d'erreurs d'écriture réversible que son taux vrai : 10 sur 893 pour 1,4 attendues, puis 15 sur 1 884 pour 2,9 attendues, groupées dans 2 et 6 tâches.
  - Dans A-rho7, c'est l'aléa seul, le prix de N1 aux volumes du plan : aucun type ne compte, quel que soit le ρ̂ permis par la règle (au moins 0,3). L'étude de délégabilité donne le même ordre de grandeur : à 0,2 fois la barre, aucune configuration délégable dans 0 à 6 % des répétitions selon ρ et les témoins.
  - Dans E, le cas est à la limite. Les messages internes de Haiku (0 erreur sur 263) ont un taux médian à 1,01 fois la barre, avec un ρ̂ de 0,48 pour un ρ vrai de 0,3. Avec le vrai ρ, ils compteraient (0,76 fois la barre) et R4 ne sortirait pas : c'est N3 (8.7).
- **Les autres étiquettes ne bougent pas.** Sur les 559 répétitions appariées, 27 changent : les 25 de C (R2 → R4 : 15 ; « confirmée » → R4 : 10) et les deux ci-dessus. Les points 0 et 1 donnent exactement les mêmes nombres. Le point 2 bouge sans changer d'étiquette : la charge se compare sur les configurations délégables, moins nombreuses depuis N1 (8.5).
- **La délégabilité discrimine.** Part des répétitions avec au moins une configuration délégable (second passage : 100 % partout) :
  - agents parfaits : 100 % ;
  - 0,5 fois la barre : 88 à 99 % ;
  - à la barre : 50 à 74 % ;
  - 2 fois la barre : 4 à 40 % ;
  - 5 fois la barre : 0 à 7 % ;
  - 10 fois la barre : 0 à 1 %.

  À ces volumes, seuls les types à faible enjeu comptent : sur les 19 800 tirages, aucun type à enjeu moyen ou fort n'a rendu une configuration délégable.
- **N2 est corrigé.** L'oracle ne délègue plus l'argent ni l'écriture durable (0 répétition sur 559 ; second passage : 559). Sa plus haute valeur centrale dépasse encore le budget dans 32 répétitions (second passage : 256). E-fort en compte 11 sur 30, par la dérive du mélange qui donne R1 à B-tout ; les 21 autres sont isolées. C'est descriptif, sans effet sur l'étiquette.
- **Le résidu de G1 est corrigé.** Avec les témoins en défaut, le classement prouvé certifie de nouveau un Haiku parfait dans WorkBench : 34 à 41 % des répétitions (second passage : 0 %).
- **N3, nouveau et mineur** (8.7). ρ̂ ne mesure pas la corrélation intra-tâche quand il réunit des configurations ou des types aux taux très différents. Il vaut 0,43 pour un ρ vrai de 0 quand les témoins sont en défaut, et 0,32 à 0,42 pour un ρ vrai de 0,7. Il est trop prudent dans le premier cas et pas assez dans le second. Il change une étiquette sur 559, dans le sens prudent : E n° 25, R4 au lieu de « confirmée ». Sa correction se fera avec les retours de la revue de code.
- **A4 reste signalé** (M2, puissance, déjà connu) : « confirmée » 22 %, R2 sinon, comme au second passage.

### 8.2 Ce qui a changé

- **Moteur** (commit 3514d34) :
  - `classes.py` :
    - taux médian (`mediane_haute`, borne haute de Clopper-Pearson à 50 % sur (x_eff, n_eff)) ;
    - `estime_sous` : le type compte pour la délégabilité si son taux médian est au plus la barre ;
    - `jugeable` : zéro erreur suffirait, soit n_eff × barre ≥ ln 2 ;
    - `rho_anova` écarte les grappes d'une écriture.
  - `pipeline.py` : types jugeables par configuration.
  - `decision.py` : étiquette « volume insuffisant » (après R1, avant R4) quand aucun type n'est jugeable.
  - `sorties.py` : nouvelles colonnes dans `ecart.csv` (taux médian, erreurs attendues à la barre, « jugeable », « compte pour la délégabilité »).
  - L'oracle suit la même règle (`analyse.palier_par_type` lit `classes.estime_sous`).
- **Contrôle 3** :
  - `lancer.py` écrit dans `resultats_v3/` et compte « volume insuffisant » ;
  - tests réécrits : `test_n1_corrige_…`, la propriété attendue de N1 sans marque `xfail`, `test_g1_residu_corrige_…`, `test_parametres_figes` ;
  - `rapport_tableaux.py` lit le troisième passage par défaut, l'apparie au second et ajoute trois éléments : la colonne « volume insuffisant », le nombre moyen de configurations délégables et le tableau du ρ̂ emprunté (8.7).
- **Plan et règle** : 1.5, ordre des étiquettes, 5.13 (lecture de Q14), point 4 et étiquette finale ; `REGLE.md` ; `JOURNAL_CHANGEMENTS.md`.

### 8.3 Étiquettes attendues

Elles sont inchangées (7.3). R4, attendu dans C « au sens de 1.5 », redevient atteignable. Aucun monde n'attend « volume insuffisant » : ce garde-fou vise des volumes plus petits que ceux du plan. Les tests du moteur le couvrent (`test_rejeu_decision.py::test_point4_garde_fou_volume_insuffisant`, `test_rejeu_phase4.py::test_n1_jugeables_par_configuration_dans_le_pipeline`).

### 8.4 Lancement

- **Réglages** : les mêmes, figés (7.4). R0 = B = 200, K = 10, e = 5 %, jackknife-t, même graine ; 12 processus, tranches de 50 ; 559 répétitions. Étude de délégabilité : 300 répétitions par case, soit 19 800 tirages.
- **Durée** : 2 h 12 (délégabilité 11 min 42 s ; mondes 2 h 01).
- **Vérifications** : `lancer.py --verifier` donne des empreintes conformes. Les 559 répétitions gardent les volumes, la graine du moteur et les points 0 et 1 du second passage.
- **Tests après le lancement** :
  - simulation : 268 réussis, plus 1 échec attendu (contradiction déjà notée dans `CHOIX_PHASE4.md`) ;
  - banc : 677 ;
  - gel : 6.

### 8.5 Fréquences des étiquettes

⚠ : l'étiquette attendue n'est pas la plus fréquente, ou sort moins de 80 % du temps pour A, B, C ou F. Pour R2, la mention attendue est comptée.

| Monde | Attendu | n | R5 | R1 | volume insuffisant | R4 | R2 (aucune délégation / inférieure à un témoin) | confirmée | Attendue la plus fréquente ? | Part de l'attendue (IC 95 %) | Second passage, même étiquette |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | confirmée | 80 | 0 | 0 | 0 | 0 | 0 | 80 | oui | 100 % (95–100) | 100 % |
| A-tf | confirmée | 40 | 0 | 0 | 0 | 0 | 0 | 40 | oui | 100 % (91–100) | 100 % |
| A4 | confirmée | 40 | 0 | 0 | 0 | 0 | 31 (0 / 31) | 9 | non **⚠** | 22 % (12–38) | 22 % |
| A-rho0 | confirmée | 30 | 0 | 0 | 0 | 0 | 0 | 30 | oui | 100 % (89–100) | 100 % |
| A-rho7 | confirmée | 30 | 0 | 0 | 0 | 1 | 0 | 29 | oui | 97 % (83–99) | 100 % |
| B | R1 | 60 | 0 | 60 | 0 | 0 | 0 | 0 | oui | 100 % (94–100) | 100 % |
| B100 | R1 | 20 | 0 | 20 | 0 | 0 | 0 | 0 | oui | 100 % (84–100) | 100 % |
| C | R4 (au sens de 1.5) | 25 | 0 | 0 | 0 | 25 | 0 | 0 | oui | 100 % (87–100) | 0 % |
| D | R2, délégation inférieure | 50 | 0 | 0 | 0 | 0 | 50 (0 / 50) | 0 | oui | 100 % (93–100) | 100 % |
| D-piège | confirmée | 40 | 0 | 0 | 0 | 0 | 0 | 40 | oui | 100 % (91–100) | 100 % |
| E | confirmée + mention | 50 | 0 | 0 | 0 | 1 | 0 | 49 | oui | 98 % (90–100) ; mention hors banque 100 % | 100 % |
| E-fort | R1 | 30 | 0 | 30 | 0 | 0 | 0 | 0 | oui | 100 % (89–100) | 100 % |
| F1 | R5 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | oui | 100 % (68–100) | 100 % |
| F2 | R5 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | oui | 100 % (68–100) | 100 % |
| K | R2, délégation inférieure | 8 | 0 | 0 | 0 | 0 | 8 (0 / 8) | 0 | oui | 100 % (68–100) | 100 % |
| D-inerte | R2, aucune délégation | 40 | 0 | 0 | 0 | 0 | 40 (40 / 0) | 0 | oui | 100 % (91–100) | 100 % |

**Passages appariés** (mêmes données, même graine du moteur) :
- **Étiquettes.** C : R2 → R4 (15) et « confirmée » → R4 (10). A-rho7 et E : « confirmée » → R4, une répétition chacun. Aucune autre répétition ne change.
- **Points 0 et 1** : identiques dans les 559 répétitions.
- **Point 2.** La charge se compare sur les configurations délégables (5.12). Depuis N1, il y en a 0 à 5,6 sur 12 en moyenne selon le monde, contre 7 à 12 avant. Dans A4, la liste fixe est maintenant battue dans 32 répétitions sur 40, dont 29 par la charge (second passage : 9, aucune par la charge). Le tri par le risque reste battu dans 9 seulement, d'où la même étiquette. Sans configuration délégable (B, B100, C et les deux R4), « tout faire valider » n'est plus battu.
- **Point 3.** Il devient « non calculable » dans ces mêmes cas, et « répartie » passe à « sans objet » dans 46 répétitions. Ce point est sans effet sur l'étiquette.

**R4 hors de C** : les deux répétitions, type par type. Barre de WorkBench : 1/132.

| Répétition | Haiku, WorkBench, écriture réversible | Haiku, WorkBench, messages internes | Le reste |
|---|---|---|---|
| A-rho7, n° 18 (ρ vrai 0,7) | 10 erreurs sur 893, dans 2 tâches, 5 chacune (1,4 attendues) ; ρ̂ 0,53 ; taux médian 1,8 fois la barre | 1 sur 263 ; non jugeable (n_eff × barre = 0,65) | Sonnet et Opus dans WorkBench au-dessus (environ 9 fois) ; aucun autre type jugeable |
| E, n° 25 (ρ vrai 0,3) | 15 sur 1 884, dans 6 tâches (2,9 attendues) ; ρ̂ 0,48 ; 1,3 fois la barre | 0 sur 263 ; taux médian 1,01 fois la barre ; non jugeable (0,68) | commerce : Haiku 25 erreurs dans 3 tâches (5 attendues), Sonnet et Opus 3 dans une tâche (1 attendue), tous au-dessus ; aucun autre type jugeable |

ρ̂ de WorkBench selon les estimations de 8.7 (script `options_n3/rho_estimateurs.py`), et ce qu'elles changent :

| Répétition | G1 (moteur) | sommes de carrés par configuration | configuration par configuration | type par type | ρ vrai |
|---|---|---|---|---|---|
| A-rho7, n° 18 | 0,53 | 0,53 | 0,40 | 0,91 | 0,7 |
| E, n° 25 | 0,48 | 0,46 | 0,34 | 0,60 | 0,3 |

- **A-rho7** : R4 sort avec toutes ces valeurs. Les messages internes de Haiku ne compteraient qu'avec ρ̂ = 0, sous le plancher.
- **E** : avec le ρ vrai (0,3) ou l'estimation configuration par configuration (0,34), les messages internes de Haiku compteraient (0,76 et 0,82 fois la barre) et R4 ne sortirait pas. Avec G1 ou l'estimation type par type, R4 sort.

**Monde signalé et cause** : A4 seul, comme au second passage. Cause : puissance (M2, déjà connue). Les témoins dépassent le budget d'environ 3 fois ; ce dépassement n'est établi que dans 22 % des répétitions. Le tri par le risque n'est pas battu par la charge (B-tout demande 6,1 validations de plus pour 100 actions, médiane).

**Autres vérifications** :
- « Garantie hors hypothèse » ne sort sur aucune cellule non jugée.
- La cellule de Haiku dans la banque, à enjeu faible, porte la mention chaque fois qu'elle est jugée (421 sur 421, M4).
- Aucun R1 à tort : 0 sur 449.

### 8.6 Délégabilité et classement prouvé

Part des répétitions où au moins une configuration est délégable (taux médian au plus la barre) / délégable selon le classement prouvé (borne haute au plus la barre ; publié, sans décider R4). Tous les types sont au même multiple de la barre, avec 300 répétitions par case. « Délégable par un type faible seulement » est identique à la première valeur dans toutes les cases.

Sans témoin en défaut :

| ρ | 0 × | 0,05 × | 0,2 × | 0,5 × | 1 × | 2 × | 5 × | 10 × |
|---|---|---|---|---|---|---|---|---|
| 0 | 100 / 92 % | 100 / 59 % | 100 / 20 % | 99 / 3 % | 68 / 0 % | 15 / 0 % | 0 / 0 % | 0 / 0 % |
| 0,3 | 100 / 93 % | 100 / 73 % | 99 / 29 % | 95 / 9 % | 74 / 1 % | 21 / 0 % | 0 / 0 % | 0 / 0 % |
| 0,7 | 100 / 92 % | 98 / 77 % | 94 / 43 % | 88 / 20 % | 69 / 4 % | 40 / 0 % | 7 / 0 % | 1 / 0 % |

Avec les témoins en défaut (écriture réversible de WorkBench à 10 fois la barre chez Sonnet et Opus) :

| ρ | 0 × | 0,05 × | 0,2 × | 0,5 × | 1 × | 2 × | 5 × | 10 × |
|---|---|---|---|---|---|---|---|---|
| 0 | 100 / 41 % | 100 / 35 % | 100 / 16 % | 95 / 1 % | 50 / 0 % | 4 / 0 % | 0 / 0 % | 0 / 0 % |
| 0,3 | 100 / 40 % | 100 / 39 % | 100 / 17 % | 96 / 7 % | 70 / 0 % | 22 / 0 % | 0 / 0 % | 0 / 0 % |
| 0,7 | 100 / 34 % | 100 / 36 % | 97 / 28 % | 88 / 12 % | 68 / 2 % | 39 / 0 % | 4 / 0 % | 0 / 0 % |

Nombre moyen de configurations délégables, sur 12 (second passage : 12 pour des agents parfaits, encore 4,3 à 8,7 à 5 et 10 fois la barre) :

| ρ, témoins | 0 × | 0,05 × | 0,1 × | 0,2 × | 0,5 × | 1 × | 2 × | 5 × |
|---|---|---|---|---|---|---|---|---|
| 0, tenus | 5,02 | 4,72 | 4,28 | 3,63 | 2,28 | 0,94 | 0,16 | 0,00 |
| 0,3, tenus | 4,74 | 4,45 | 4,31 | 3,87 | 2,86 | 1,63 | 0,31 | 0,00 |
| 0,7, tenus | 4,96 | 4,57 | 4,16 | 3,63 | 2,73 | 1,61 | 0,72 | 0,10 |
| 0, en défaut | 1,47 | 2,28 | 2,35 | 2,18 | 1,35 | 0,53 | 0,04 | 0,00 |
| 0,3, en défaut | 1,48 | 1,68 | 1,80 | 1,91 | 1,84 | 0,97 | 0,27 | 0,00 |
| 0,7, en défaut | 1,43 | 1,52 | 1,53 | 1,55 | 1,51 | 1,08 | 0,63 | 0,05 |

Tableau complet (multiples 0,02 et 0,3 en plus) : `resultats_v3/delegabilite.csv`.

- **Monotone, à l'aléa près.** La part des répétitions avec au moins une configuration délégable ne monte jamais de plus d'un point quand la fiabilité baisse. Avec les témoins en défaut, deux choses ne sont pas monotones, et c'est N3 (8.7) :
  - le classement prouvé remonte de 4 points à ρ = 0,7 entre 0 et 0,02 fois la barre (34 → 38 %) ;
  - le nombre moyen de configurations délégables passe de 1,47 pour des agents parfaits à 2,35 à 0,1 fois la barre (ρ = 0).
- **Discriminante.** R4 (aucune configuration délégable) sort dans 93 à 100 % des répétitions à 5 fois la barre, 60 à 96 % à 2 fois, 26 à 50 % à la barre et 1 à 12 % à 0,5 fois. Il ne sort jamais pour des agents parfaits.
- **Seuls les types à faible enjeu comptent.** Sur les 19 800 tirages, on compte les types estimés sous la barre, par configuration et par tirage :
  - écriture réversible : 37 078 (WorkBench 23 498, commerce 10 801, aviation 2 711, banque 68) ;
  - messages internes : 11 707 (WorkBench 10 785, banque 922) ;
  - jamais l'écriture durable ni l'argent, dont le volume prévu ne permet pas de juger (1.5 l'écrit déjà : « R4 ne dit rien des types à enjeu moyen ou fort »).
- **Classement prouvé** (sa règle est inchangée). Avec les témoins en défaut, un Haiku parfait est de nouveau certifié dans WorkBench : 41, 40 et 34 % des répétitions à ρ = 0 ; 0,3 ; 0,7 (second passage : 0 %). Son ρ̂ médian vaut 0,34 à 0,35 au lieu de 0,67 : le résidu de G1 est corrigé.

**Certification à tort par le classement prouvé.** Type exactement à la barre (1 × barre), sans témoin en défaut. On compte la part des répétitions où il est dit « sous la barre » ; le nominal est de 5 % au plus.

| ρ | WorkBench, Haiku, réversible | commerce, Haiku, réversible | aviation, Haiku, réversible | tous les types faibles réunis | second passage, WorkBench |
|---|---|---|---|---|---|
| 0 | 0,3 % (1 sur 300 ; IC 0,1–1,9 %) | 0 % (0 sur 300) | 0 % (0 sur 216) | 1 sur 5 148 | 1 sur 300 |
| 0,3 | 1 % (3 sur 300 ; IC 0,3–2,9 %) | 0 % (0 sur 300) | 0 % (0 sur 218) | 3 sur 5 154 | 3 sur 300 |
| 0,7 | 4 % (12 sur 300 ; IC 2,3–6,9 %) | 0 % (0 sur 300) | 0 % (0 sur 205) | 12 sur 5 115 | 11 sur 300 |

Le risque est tenu à ρ = 0 et 0,3. À ρ = 0,7, il atteint 4 % dans WorkBench : c'est sous les 5 % nominaux, mais l'intervalle va jusqu'à 6,9 %. ρ̂ médian y vaut 0,38 pour un ρ vrai de 0,7 : c'est la seconde face de N3 (8.7).

### 8.7 Défauts, après correction

**Corrigés et vérifiés** :
- **N1.** R4 sort dans C 25 fois sur 25. La délégabilité discrimine (8.6). « Volume insuffisant » ne sort jamais aux volumes du plan ; le garde-fou est testé dans le moteur (8.3). Le prix : R4 dans une des 310 répétitions où « confirmée » est attendue, par l'aléa seul (A-rho7), du même ordre que dans l'étude de délégabilité. Une autre (E) vient en partie de N3 (8.5).
- **N2.** L'oracle ne délègue plus à enjeu moyen ou fort (0 sur 559). Sa plus haute valeur centrale dépasse encore le budget dans 32 répétitions :
  - 11 sur 30 dans E-fort, par la dérive du mélange qui donne R1 à B-tout ;
  - 21 ailleurs, au plus 5 par monde (E 5, D 4, A-rho0 3, D-inerte 3, A-rho7 2, D-piège 2, A4 1, F2 1).

  C'est le maximum d'au plus 36 valeurs centrales sans intervalle (12 configurations × 3 niveaux), donc descriptif et sans effet sur l'étiquette.
- **Résidu de G1** (grappes d'une écriture) : corrigé, voir 8.6.

**N3 (nouveau, mineur ; cause : l'estimateur d'analyse de variance, 5.13, appliqué à des grappes dont les taux diffèrent). ρ̂ ne mesure pas la corrélation intra-tâche quand il réunit des configurations ou des types aux taux très différents.** Il a deux faces.

- **Trop haut quand les configurations réunies ont des taux très différents** (le côté prudent).
  - Le cas : un environnement sans erreur emprunte le ρ̂ de tous les environnements réunis (G1). Avec les témoins en défaut, les seules erreurs sont celles de Sonnet et d'Opus, dans les petites tâches de WorkBench (une à trois écritures). Elles sont réunies avec les grandes tâches sans erreur des autres configurations (jusqu'à près de 150 écritures). L'estimateur suppose le même taux partout ; il lit cet écart comme une corrélation.
  - Mesuré, agents parfaits : ρ̂ réuni médian 0,43, que le ρ vrai soit 0, 0,3 ou 0,7. Estimé configuration par configuration, il vaut 0,00 à 0,01.
  - Dans les mondes où les témoins sont en défaut, le ρ̂ emprunté médian vaut :
    - 0,35 à 0,49 pour un ρ vrai de 0,3 (A, A-tf, A4, D-piège, D-inerte, E, F1, F2) ;
    - 0,42 pour un ρ vrai de 0,7 (A-rho7).

    Il vaut 0,30, le plancher, dans D, où les témoins tiennent, et dans A-rho0 (ρ vrai 0).
  - Effet : moins de configurations délégables quand les agents sont parfaits et que les témoins se trompent ailleurs (1,4 à 1,5 au lieu de 4,7 à 5,0). Le nombre n'est pas monotone : une seule erreur rend à l'environnement son propre ρ̂, au plancher (8.6). Un ρ̂ trop grand ne fait que retirer des types de la délégabilité et du classement prouvé.
- **Trop bas quand ρ est fort** (le côté non prudent).
  - Le cas : les grappes réunissent tous les types mérités d'une tâche. Les erreurs groupées d'un type y sont diluées parmi des écritures d'autres types qui ne se trompent presque jamais.
  - Mesuré à 0,2 et 0,5 fois la barre, sur 40 tirages par case. ρ̂ de tous les environnements réunis : 0,16 à 0,24 pour un ρ vrai de 0,3 ; 0,34 à 0,41 pour 0,7. Estimé type par type : 0,23 à 0,28 et 0,57 à 0,61.
  - Effet : le plancher de 0,3 couvre ρ = 0,3, pas ρ = 0,7. D'où la certification à tort de 4 % dans WorkBench à ρ = 0,7 (8.6 ; 3,7 % au second passage), et une délégabilité un peu trop facile quand ρ est fort.
- **Effet sur les étiquettes.** Une étiquette sur 559 : E n° 25, R4 au lieu de « confirmée », un cas à la limite (8.5). Avec un ρ̂ juste à ρ = 0,7, R4 serait un peu plus fréquent pour des agents fiables (déduit, non simulé).
- **Ce qui ne corrige pas, vérifié hors moteur** : réunir les sommes de carrés par configuration (analyse de variance stratifiée). Avec les témoins en défaut, ρ̂ passe seulement de 0,43 à 0,41 ou 0,42. La variance interne et la taille moyenne des grappes restent dominées par les grandes tâches sans erreur.
- **Ce qui corrige en partie, vérifié hors moteur** :
  - combiner des estimations faites configuration par configuration (moyenne pondérée par les erreurs). Avec les témoins en défaut, ρ̂ tombe à 0,00 ou 0,01, donc au plancher. Mais dans les cas ordinaires, ρ̂ descend encore (0,12 pour un ρ vrai de 0,3 ; 0,30 à 0,32 pour 0,7) ;
  - estimer type par type, qui corrige en partie la seconde face. Avec les témoins en défaut, ce ρ̂ n'est pas calculable : leurs erreurs sont toutes dans des grappes d'une écriture.

  Tableau complet : `options_n3/rho_estimateurs.csv`.
- **Piste.** Estimer ρ̂ par configuration et par type, puis combiner les estimations d'une façon qui tienne compte des taux différents. La méthode reste à trancher par la recherche : estimateurs de la corrélation intra-grappe pour des événements binaires rares, par strate. Elle sera codée avec les retours de la revue de code, pour une seule relance.

**Toujours vrais** :
- **M2** : A4, témoins à environ 3 fois le budget, battus par le budget dans 22 % des répétitions.
- **M3** : R1 seulement pour une violation nette, jamais à tort (0 sur 449).
- **M4** : la banque à enjeu faible sort de l'hypothèse de construction. La mention apparaît dans 421 répétitions sur 421 où la cellule de Haiku dans la banque, à enjeu faible, est jugée.

### 8.8 Ce qui reste

1. **Revue de code « ultra »** sur la copie propre, sans historique ni `donnees/`. Otsoa la lance depuis une session ouverte dans la copie.
2. **N3 et les retours de la revue.** D'abord une recherche sur l'estimation de ρ̂, puis une seule série de corrections, puis un quatrième passage (environ 2 h 15).
3. **Avant le gel** : grille élargie (ρ = 0,9, mondes mixtes, 1 000 répétitions par case), relecture indépendante C13, relecture finale d'Otsoa, puis gel le 18/11.
4. **Non couvert**, comme aux passages précédents :
   - le désaccord persistant (B2) dans un monde complet ;
   - les refusées ;
   - R0 = B = 2 000 ;
   - les analyses secondaires ;
   - la couverture de la moyenne des différences de charge ;
   - le lanceur et ses deux vagues.

## 9. Quatrième passage (06/11)

> Après N3 (ρ̂ par type : Fleiss–Cuzick stratifié par (configuration, type), corrigé du petit échantillon, borné à [0, 1] ; preuves à 95 % à ρ = 1 ; tranché par la recherche à la demande d'Otsoa, rapport `reports/Corrélation intra tâche par strates.md`) et les corrections de la revue de code « ultra » : moteur au commit 712a7a7, empreintes vérifiées (`controle3.lancer --verifier` : conformes). Mêmes réglages (R0 = B = 200, K = 10, e = 5 %), graine maîtresse 2026110503, répétitions appariées avec les passages précédents. Ajouts jugés sur la pire case : trois mondes (A-rho9, A-logit, A-het ; 30 répétitions chacun), ρ = 0,9 et 1 dans l'étude de délégabilité, deux mécanismes de corrélation (logit-normal, ρ hétérogène), sept cases critiques à 10 000 répétitions. 649 répétitions ; durées : délégabilité 1 513 s, cases critiques 2 421 s, mondes 7 921 s, sur 12 processus. Dossier `resultats_v4/`.

### 9.1 En bref

- **Cases critiques : aucune certification à tort, mais c'est mécanique.** Type exactement à la barre (écriture réversible de Haiku dans WorkBench), 10 000 répétitions par case. La classe prouvée (ρ = 1) ne certifie jamais « sous la barre » : 0 sur 10 000 dans les 7 cases. Aux volumes du plan, elle ne peut d'ailleurs rien certifier, ni à tort ni à raison : il faudrait environ 394 tâches porteuses, il y en a environ 185 (étude de délégabilité : 0 % même pour des agents parfaits). La lecture sous hypothèse (ρ̂) certifie à tort 2,6 % et 2,1 % à ρ = 0,7 (témoins tenus, en défaut), 4,5 % à ρ = 0,9, 5,9 % et 6,1 % à ρ = 1, 1,5 % en logit-normal à ρ = 0,9 ; tous les types faibles réunis : 0,09 à 0,36 %. Elle ne dépasse le risque nominal qu'à ρ = 1 : elle reste publiée à côté, jamais comme preuve (`critiques.csv`).
- **N3 corrige ρ̂ et coûte de la puissance.** ρ̂ médian de Haiku dans WorkBench dans les cases critiques : 0,66 pour un ρ vrai de 0,7 (troisième passage : 0,38), 0,91 pour 0,9, 1,00 pour 1 ; 0,51 en logit-normal à 0,9. Avec une taille effective honnête, des agents fiables sont moins souvent retenus quand leurs erreurs sont groupées : à 0,2 fois la barre, au moins une configuration délégable dans 100 % des répétitions à ρ = 0, 99 % à 0,3, 89 % à 0,7, 83 % à 0,9 et 76 % à 1 (témoins tenus).
- **R4 sort plus souvent là où « confirmée » est attendue : 16 répétitions sur 400** (troisième passage : 2 sur 310). A : 1 sur 80 ; A-rho7 : 6 sur 30 ; A-rho9 : 6 sur 30 ; A-het : 3 sur 30. E n'en donne plus (50 sur 50 ; son cas n° 25 du troisième passage relevait de N3). D et D-inerte donnent aussi R4, 2 et 1 fois, là où R2 est attendu.
  - Mécanisme, vérifié sur les 16 répétitions : Haiku dans WorkBench, la configuration qui porte la délégabilité, tire 4 à 12 erreurs d'écriture réversible groupées dans peu de tâches. Avec ρ̂ de 0,60 à 1, la taille effective tombe vers 180 à 280 écritures, et le taux médian passe au-dessus de la barre (taux observé : 0,6 à 1,7 fois la barre). Les messages internes ne prennent pas le relais : leur taille effective va de 52 à 89, sous les 92 qu'il faudrait pour juger un type sans erreur (trois répétitions ont en plus une à trois erreurs).
  - Ce n'est pas un défaut du moteur : c'est la conséquence attendue d'un ρ̂ juste. Mais cela touche le sens de R4 décidé en Q14 (« R4 signale des agents nettement peu fiables, pas un manque de preuve ») : à ρ ≥ 0,7, R4 sort jusqu'à une fois sur quatre pour des agents cinq fois meilleurs que la barre. **À trancher par Otsoa** (9.3, point 1).
- **Le reste ne bouge pas.** Aucun R1 à tort : 0 sur 539 répétitions où B-tout tient le budget. B, B100 et E-fort donnent R1 à chaque fois ; F1 et F2, R5 ; C, R4 25 fois sur 25 ; K, R2. A4 reste à 9 sur 40 (intervalle de Wilson : 12 à 38 %), limite de puissance M2. A-logit : 29 sur 30, une R2. L'étiquette attendue est la plus fréquente dans 18 mondes sur 19 (exception : A4) ; 598 répétitions conformes sur 649.
- **Vérifications.** `controle3.lancer --verifier` : empreintes conformes. Tests : 189 réussis et 1 échec attendu (simulation), 704 réussis (banc, gel).

### 9.2 Délégabilité (point 4 seul ; 300 tirages par case ; mécanisme bêta ; témoins tenus)

Part des répétitions avec au moins une configuration délégable (taux médian au plus la barre), selon le taux vrai de tous les types rapporté à leur barre :

| ρ vrai | 0 × | 0,2 × | 1 × | 2 × | 5 × | Haiku WorkBench seul à 1 × | sous hypothèse : 0 × / 1 × |
|---|---|---|---|---|---|---|---|
| 0 | 100 % | 100 % | 68 % | 15 % | 0 % | 39 % | 92 % / 0,3 % |
| 0,3 | 100 % | 99 % | 72 % | 20 % | 0 % | 55 % | 93 % / 1,0 % |
| 0,7 | 100 % | 89 % | 52 % | 21 % | 0,7 % | 44 % | 92 % / 1,3 % |
| 0,9 | 100 % | 83 % | 37 % | 12 % | 0 % | 34 % | 91 % / 3,7 % |
| 1 | 100 % | 76 % | 20 % | 7 % | 0 % | 20 % | 89 % / 6,0 % |

- Classe prouvée (ρ = 1) : 0 % dans toutes les cases, agents parfaits compris.
- Taux de R4 (aucune configuration délégable), témoins tenus et en défaut réunis : jamais pour des agents parfaits ; 0 à 24 % à 0,2 fois la barre (0 à 16 % si ρ ≤ 0,7) ; 1 à 53 % à 0,5 fois (1 à 25 % si ρ ≤ 0,7) ; 28 à 80 % à la barre ; 79 à 97 % à 2 fois ; 99 à 100 % à 5 fois. Troisième passage, ρ ≤ 0,7 : 1 à 12 % à 0,5 fois, 26 à 50 % à la barre, 93 à 100 % à 5 fois.
- Autres mécanismes, à 0,5 fois la barre : logit-normal 80 à 98 % délégable ; ρ hétérogène 83 à 89 %.

### 9.3 Points ouverts avant le gel

1. **Sens de R4 (à trancher par Otsoa).** Garder la règle et déclarer qu'un R4 ne prouve pas que les agents sont peu fiables quand les erreurs sont très groupées ; ou la changer pour retrouver l'intention de Q14 (par exemple : R4 seulement si le dépassement de la barre est établi, sinon « volume insuffisant »), ce qui demande une recherche et un cinquième passage. Recommandation de Claude : la seconde voie colle à Q14, mais la première suffit si le texte de R4 le dit. **Tranché par Otsoa le 07/11** : seconde voie, sous la forme recommandée après la simulation de cinq règles au moteur (`options_r4/`) : R4 seulement si chaque configuration jugeable compte un type jugeable dont le dépassement est établi à ρ = 1 ; sinon « preuves insuffisantes », avec son motif (plan, 1.5 ; moteur, commit 6c02d69). Confirmation sur de nouveaux tirages : section 10.
2. **Niveau du max-T au seuil exact.** Aucun monde n'a de dépassement vrai d'exactement 1,0 fois le budget : « 0 R1 à tort » est mesuré loin du seuil (relevé par la relecture extérieure du deck, 06/11). À ajouter à la grille élargie (monde « B-seuil »). *Mesuré au cinquième passage : au seuil exact, 0 R1 sur 120 (borne haute 3,1 %) ; 10.7 (première mesure, une cellule au-dessus du seuil) et 10.8 (seconde mesure).*
3. **« Volume insuffisant ».** Aucun monde ne le produit ; à tester par un monde à volumes réduits. *Devenu le motif « aucun type jugeable » de « preuves insuffisantes » (07/11) ; monde à volumes réduits au cinquième passage (section 10).*
4. **PLAN_EXPERIENCE.md, R4 (1.5).** Nombres du troisième passage remplacés par ceux du quatrième le 06/11 ; le texte du sens de R4 attend le point 1. *Texte amendé le 07/11 (point 1).*
5. **Cellules portées par une seule tâche (point 1 ; à trancher par Otsoa, 07/11).**
   - **Ce que dit le plan** (5.14, point 1) : une cellule sans variation bootstrap n'entre pas dans le maximum ; son dépassement est établi si son estimation dépasse le budget.
   - **Le défaut.** Quand la loi bootstrap d'une cellule est dégénérée, son dépassement est jugé sur la seule estimation : une erreur dans une seule tâche peut alors « établir » un dépassement, donc R1, l'étiquette éliminatoire, sans aucune mesure de l'incertitude. C'est contraire à l'esprit de la section 8 du plan (bornes au niveau des tâches, jamais sur les écritures brutes). Le moteur prend aussi cette branche quand l'écart type n'est pas défini : une réplique sans aucune écriture (0/0) donne NaN, cas que le plan n'écrit pas.
   - **Constaté** dans le monde V : un faux R1 sur 30 (10.7). Les estimations y valaient 1,9 à 3,8 fois le budget, tirées d'une seule tâche.
   - **Exposition aux volumes du plan** (`une_tache/`, 36 répétitions rejouées, étiquettes identiques au contrôle complet).
     - Au moins une cellule jugée de B-tout est portée par une seule tâche dans 6 répétitions sur 12 du monde A et 3 sur 12 de E ; aucune dans D-piège.
     - Toujours dans l'aviation à enjeu faible, de 20 à 60 écritures : l'écriture réversible n'y apparaît que dans 3 tâches sur 50.
     - **Mais aux volumes du plan, ces cellules passent par le max-T, et une seule tâche ne peut pas y établir de dépassement** (vérifié dans la répétition 1 de A, corrigé le 07/11 : une première version disait qu'une erreur pourrait suffire près de la barre).
       - Les répliques qui ne tirent pas la tâche valent 0 (environ 75 sur 200, dans un cadre de 20 tâches).
       - L'écart type vaut 1,2 à 1,5 fois l'estimation, et c* = 3,43.
       - La borne basse est donc négative, quelle que soit l'estimation.
       - Aucune réplique NaN dans les répétitions 0 à 3 de A (35 à 46 cellules jugées chacune).
     - La branche dégénérée ne joue qu'avec un cadre minuscule (monde V : 2 tâches, répliques à 0/0), ou avec un cadre réduit à une tâche.
   - **Recherche approfondie** (07/11, `reports/Cellules portées par une seule tâche.md`).
     - Aucun logiciel de tests multiples lu (multtest, libcoin, rwolf2, boot) et aucune méthode n'établit un dépassement sur une estimation seule.
     - Une hypothèse non testable sort du compte et n'est jamais rejetée (Tarone). Les logiciels de sondage refusent de même une variance pour une strate à une seule unité (R `survey`, Stata).
   - **La phrase en cause est au point 2 de 5.14**, dans la définition du dépassement établi, que le point 1 reprend : elle vaut aussi pour les témoins.
   - **Options.**
     - (a) Garder la règle et déclarer la limite. Le cas d'un écart type non défini reste à écrire.
     - (b) Amender, dans la version élargie que recommande la recherche. Une cellule est « non testable » si elle est portée par une seule tâche, ou si son écart type bootstrap est nul ou non défini. Elle sort du maximum, n'établit aucun dépassement, et se publie avec sa valeur centrale, son nombre de tâches porteuses et son motif. Effet attendu : seule la répétition 24 de V change (R1 → « preuves insuffisantes »), car toutes les autres répétitions R1 ont une cellule établie hors de l'aviation ; c* peut baisser un peu ailleurs (à mesurer).
   - **Recommandation de Claude : (b) élargie.** Coût : gratuit.
     - Plan, moteur et tests amendés.
     - Contrôle 3 refait en entier (environ 3 h).
     - Avant le gel, niveau du test mesuré sur des cellules de 2 à 4 tâches porteuses, avec un critère de bascule écrit d'avance.
   - **Tranché par Otsoa le 07/11 : (b) élargie.** Plan, 5.14, point 2 ; moteur au commit 0a908cf ; seuil de deux tâches confirmé par la mesure des cellules de 2 à 5 tâches ; sixième passage : section 11.

## 10. Cinquième passage (07/11)

> Après l'amendement de R4 (décision d'Otsoa du 07/11 ; plan, 1.5 ; moteur au commit 6c02d69). Sans configuration délégable, R4 n'est donné que si chaque configuration jugeable compte un type jugeable dont le dépassement est établi à ρ = 1 ; sinon l'étiquette est « preuves insuffisantes », avec son motif. La règle a été choisie après avoir vu les tirages du quatrième passage (`options_r4/`, section 7) ; ce passage la confirme sur des tirages neufs. Il a deux parties. La première porte sur la règle seule, point 4 et étiquette, avec de nouvelles graines (10.1 à 10.5). La seconde est le contrôle 3 complet, sur toute la chaîne (10.6 et 10.7), suivi d'une seconde mesure du monde au seuil (10.8).

### 10.1 En bref (partie R4)

- **Cibles tenues, sur des tirages neufs.**
  - Douze cases critiques à 10 000 tirages, avec une graine maîtresse neuve (2026110701). La méthode et le script ont été figés avant le lancement (commit a4e6e2a, qui n'ajoute au moteur de 6c02d69 que ces deux fichiers).
  - R4 à tort dans la pire case à la barre : 2,83 % (borne haute de Wilson 3,17 %), mécanisme bêta, ρ = 1, témoins en défaut.
  - À 0,5 fois la barre : 0,31 % (borne haute 0,44 %). M1-bis : 2,35 % (borne haute 2,67 %). M2 : jamais (0 sur 10 000).
  - Les cibles d'Otsoa sont d'au plus 5 % à la barre et d'au plus 1 % à 0,5 fois. Les chiffres du 06/11, mesurés sur les tirages qui ont servi à choisir la règle, étaient de 2,73 % (borne haute 3,07 %) et 0,3 % (borne haute 0,4 %).
- **Puissance à 5 fois la barre : 28 à 93 %**, selon le mécanisme, ρ et les témoins (bêta : 28 à 93 % ; logit-normal : 32 à 90 %). Elle va de 83 à 100 % à 10 fois et de 0 à 23 % à 2 fois.
  - La plus faible est à ρ = 0 ou 0,3, témoins tenus.
  - Le motif « établi sous ρ̂ propre, pas à ρ = 1 » y prend 12 à 49 % des tirages. La lecture hybride les aurait classés R4 ; ils sont publiés, jamais comme preuve.
- **Agents fiables : « délégable » ou « preuves insuffisantes », presque jamais R4.**
  - Aucun R4 dans les 28 000 tirages aux multiples 0 et 0,2 de la barre.
  - « Preuves insuffisantes » : 0 % à 0 fois, 0 à 26 % à 0,2 fois (la part croît avec ρ), 2 à 51 % à 0,5 fois.
- **Volumes réduits.** Avec un dixième des tâches de calibration, l'issue est « preuves insuffisantes », motif « aucun type jugeable », dans 900 tirages sur 900, comme attendu.
- **Une limite, rapportée : des tâches de tailles très inégales.**
  - Tailles tirées d'une loi de Pareto d'indice 1,5 (de 1 à 200 écritures par tâche). La borne à ρ = 1 établit à tort le dépassement d'un type du commerce à la barre dans 5,04 % des cas (borne haute 5,13 %), pour un risque nominal de 5 %.
  - Le critère écrit (borne haute au plus 5 %) n'est pas tenu pour ce profil, de 0,04 point.
  - Les quatre autres profils restent entre 0,2 et 3,9 %.
- **Monotonie** : aucune alerte.
- **Validation.**
  - Les 1 800 tirages refaits de l'étude du 06/11 ne donnent aucun écart.
  - La cohérence interne est contrôlée à chaque tirage.
  - Le recomptage indépendant de `tirages.csv` donne des chiffres identiques.

### 10.2 Méthode

**Méthode figée.** Elle est décrite dans `passage5_r4/METHODE.md`, figé avant le lancement ; son empreinte sha256 (7ba12a50cf76…) est inscrite dans `meta.json`.

**Moteur appelé tel quel.** Chaque tirage passe par le moteur : génération (`mondes.generer`), classes et statut de chaque configuration (`classes.statut_configuration`), point 4 et étiquette (`decision.point4`, `decision.etiquette`). La règle n'est pas réimplémentée.

**Mondes.** Ce sont ceux de l'étude de délégabilité du quatrième passage : tous les types sont au même multiple de la barre. Les témoins sont tenus, ou en défaut (écriture réversible de Sonnet et Opus dans WorkBench à 10 fois la barre).

| Lot | Cases | Tirages par case | Rôle |
|---|---|---|---|
| Grille A | 64 (bêta, ρ de 0 à 1 ; logit-normal ; ρ hétérogène ; multiples de 0 à 1) | 1 000 | R4 à tort ; repère les cases à mesurer |
| Cases critiques | 11 (à la barre, à 0,5 fois, M1-bis, M2), plus 1 ajoutée par la deuxième étape | 10 000 | jugement des cibles |
| Grille B | 62 (multiples de 2 à 10) | 300 | puissance et motifs |
| Volumes réduits | 6 (1/10 et 1/3 des tâches de calibration ; multiples 0,2, 1 et 5) | 300 | motif « aucun type jugeable » |
| Tailles inégales | 5 profils × 3 barres × 2 taux | 200 000 | risque de la borne à ρ = 1, hors générateur |

**Deuxième étape**, réglée avant le lancement : une case de la grille A devient une case critique, si elle ne l'est pas déjà, quand elle dépasse 3 % à la barre, ou 0,5 % aux multiples 0 à 0,5.
- Une seule case a été ajoutée : bêta, 0,5 fois, ρ = 0,9, témoins en défaut (0,6 % sur 1 000 tirages).
- Deux autres cases dépassaient le seuil, mais elles étaient déjà critiques : bêta, ρ = 1, à la barre, témoins tenus (3,2 %) ; bêta, ρ = 1, à 0,5 fois, témoins en défaut (0,6 %).

**Volume de calcul** : 204 400 tirages, en 6 509 s sur 12 processus.

### 10.3 Cibles : cases critiques

| Case | n | R4 à tort | borne haute | cible | tenue |
|---|---|---|---|---|---|
| bêta, à la barre, ρ = 0,7, témoins tenus | 10 000 | 69 (0,69 %) | 0,87 % | 5 % | oui |
| bêta, à la barre, ρ = 0,7, témoins en défaut | 10 000 | 177 (1,77 %) | 2,05 % | 5 % | oui |
| bêta, à la barre, ρ = 0,9, témoins tenus | 10 000 | 155 (1,55 %) | 1,81 % | 5 % | oui |
| bêta, à la barre, ρ = 0,9, témoins en défaut | 10 000 | 222 (2,22 %) | 2,53 % | 5 % | oui |
| bêta, à la barre, ρ = 1, témoins tenus | 10 000 | 249 (2,49 %) | 2,81 % | 5 % | oui |
| bêta, à la barre, ρ = 1, témoins en défaut | 10 000 | 283 (2,83 %) | 3,17 % | 5 % | oui |
| logit-normal, à la barre, ρ = 0,9, témoins tenus | 10 000 | 25 (0,25 %) | 0,37 % | 5 % | oui |
| bêta, 0,5 fois, ρ = 1, témoins tenus | 10 000 | 18 (0,18 %) | 0,28 % | 1 % | oui |
| bêta, 0,5 fois, ρ = 1, témoins en défaut | 10 000 | 31 (0,31 %) | 0,44 % | 1 % | oui |
| bêta, 0,5 fois, ρ = 0,9, témoins en défaut (ajoutée) | 10 000 | 14 (0,14 %) | 0,23 % | 1 % | oui |
| M1-bis | 10 000 | 235 (2,35 %) | 2,67 % | 5 % | oui |
| M2 | 10 000 | 0 (0,00 %) | 0,04 % | 5 % | oui |

*R4 à tort : tout R4 dans une case au plus à la barre, et dans M1-bis ; dans M2, un R4 alors qu'une configuration du commerce est jugeable. Borne haute : intervalle de Wilson à 95 %.*

**M2.**
- M2 donne R4 dans 33,7 % des tirages, toujours quand aucune configuration du commerce n'est jugeable, ce qui arrive dans 50,4 % des tirages.
- La règle le prévoit : R4 ne dit rien des configurations sans type jugeable (plan, 1.5).

**Grille A, pour mémoire.**
- Aucun R4 aux multiples 0 et 0,2 (28 cases).
- Au plus 0,6 % de R4 à 0,5 fois.
- Au plus 3,2 % à la barre (bêta, ρ = 1, sur 1 000 tirages) ; la case critique correspondante donne 2,49 % sur 10 000.

### 10.4 Puissance et motifs (grille B)

| Mécanisme, ρ, témoins | R4 à 2 × | 3 × | 5 × | 10 × | à 5 × : non établi | à 5 × : établi sous ρ̂ propre |
|---|---|---|---|---|---|---|
| bêta, 0, tenus | 0,0 % | 4,7 % | 27,7 % | 90,0 % | 41,0 % | 31,3 % |
| bêta, 0, en défaut | 1,0 % | 16,7 % | 30,3 % | 87,7 % | 20,3 % | 49,3 % |
| bêta, 0,3, tenus | 1,0 % | 14,3 % | 42,7 % | 84,3 % | 45,3 % | 11,7 % |
| bêta, 0,3, en défaut | 7,7 % | 21,0 % | 49,7 % | 83,3 % | 30,0 % | 20,0 % |
| bêta, 0,7, tenus | 9,3 % | 32,3 % | 77,7 % | 99,7 % | 22,0 % | 0,0 % |
| bêta, 0,7, en défaut | 18,0 % | 54,7 % | 93,0 % | 99,3 % | 3,3 % | 3,7 % |
| bêta, 0,9, tenus | 15,7 % | 39,7 % | 81,3 % | 100 % | 17,3 % | 0,7 % |
| bêta, 0,9, en défaut | 20,7 % | 49,3 % | 90,7 % | 100 % | 8,0 % | 1,3 % |
| bêta, 1, tenus | 23,0 % | 41,7 % | 82,3 % | 100 % | 17,7 % | 0,0 % |
| bêta, 1, en défaut | 20,7 % | 48,0 % | 87,7 % | 100 % | 12,3 % | 0,0 % |
| logit-normal, 0,3, tenus | 0,0 % | 6,3 % | 31,7 % | — | 48,0 % | 20,3 % |
| logit-normal, 0,3, en défaut | 3,0 % | 19,7 % | 37,0 % | — | 28,3 % | 34,7 % |
| logit-normal, 0,7, tenus | 1,3 % | 13,0 % | 53,7 % | — | 39,3 % | 6,0 % |
| logit-normal, 0,7, en défaut | 5,7 % | 32,0 % | 66,7 % | — | 24,0 % | 8,7 % |
| logit-normal, 0,9, tenus | 6,0 % | 31,0 % | 73,0 % | — | 25,0 % | 1,3 % |
| logit-normal, 0,9, en défaut | 14,0 % | 48,0 % | 90,0 % | — | 7,7 % | 2,3 % |
| ρ hétérogène, tenus | 6,0 % | 20,7 % | — | — | — | — |
| ρ hétérogène, en défaut | 12,0 % | 40,3 % | — | — | — | — |

*Part des tirages, 300 par case. Les deux dernières colonnes donnent les motifs de « preuves insuffisantes » à 5 fois la barre ; le reste est délégable (au plus 1 %). La grille B ne donne jamais le motif « aucun type jugeable ».*

**Où la puissance manque.**
- Elle est la plus faible à ρ = 0 ou 0,3, témoins tenus, et le motif « non établi » y domine (41 à 48 % à 5 fois).
- Le mécanisme a été vérifié au quatrième passage (`options_r4.md`, section 7). Les petites configurations hors WorkBench, le commerce surtout, restent jugeables. Elles doivent alors établir un dépassement avec cinq à onze tâches porteuses, à ρ = 1.

**Ce que la lecture hybride aurait ajouté.** Le motif « établi sous ρ̂ propre » est ce que la règle hybride aurait compté comme R4 : jusqu'à 49 % des tirages à ρ = 0, presque rien à ρ ≥ 0,7. L'écart avec la règle retenue est donc confirmé : il porte sur les erreurs peu groupées.

**Agents fiables (grille A).**
- Aucun R4 aux multiples 0 et 0,2.
- « Preuves insuffisantes » : 0 à 26 % à 0,2 fois (croît avec ρ), 2 à 51 % à 0,5 fois, 25 à 73 % à la barre (38 à 72 % dans les cases critiques). Le reste est délégable.

### 10.5 Volumes réduits, tailles inégales, monotonie

**Volumes réduits** (bêta, ρ = 0,3, témoins tenus ; 300 tirages par case ; une fraction des tâches de calibration de chaque environnement, tirée au hasard, sans remise) :

| Fraction | Multiple | délégable | R4 | aucun type jugeable | non établi | établi sous ρ̂ propre |
|---|---|---|---|---|---|---|
| 1/10 | 0,2 | 0 | 0 | 300 | 0 | 0 |
| 1/10 | 1 | 0 | 0 | 300 | 0 | 0 |
| 1/10 | 5 | 0 | 0 | 300 | 0 | 0 |
| 1/3 | 0,2 | 225 | 0 | 4 | 71 | 0 |
| 1/3 | 1 | 74 | 0 | 17 | 206 | 3 |
| 1/3 | 5 | 1 | 147 | 9 | 71 | 72 |

- **À un dixième des tâches**, aucun type n'est jugeable : le motif sort à coup sûr.
- **À un tiers**, la règle fonctionne encore : R4 sort dans la moitié des tirages à 5 fois, jamais à la barre ni en dessous.
- **Délégabilité des bons agents** : elle baisse à un tiers des tâches (75 % à 0,2 fois, contre 99 % aux volumes du plan dans la grille A).

**Tâches de tailles inégales** (hors générateur ; ρ = 1, chaque tâche échoue en entier avec la probabilité p ; part des 200 000 répétitions où le dépassement est établi ; `tailles_inegales.csv`) :

| Profil | n_eff à ρ = 1 | p = barre : WorkBench faible | commerce faible | WorkBench moyen | p = 0,5 × barre : WorkBench faible | commerce faible | WorkBench moyen |
|---|---|---|---|---|---|---|---|
| 300 tâches de 7 écritures | 300 | 2,80 % | 3,00 % | 1,57 % | 0,11 % | 0,01 % | 0,23 % |
| 300 tâches, taille géométrique de moyenne 3 | 176 | 3,26 % | 3,93 % | 2,86 % | 0,47 % | 0,09 % | 1,10 % |
| 300 tâches, taille de Pareto (indice 1,5, de 1 à 200) | 75 | 3,32 % | **5,04 %** | 1,70 % | 1,35 % | 1,13 % | 0,76 % |
| 100 tâches d'une écriture et 1 de 100 | 4,0 | 0,76 % | 2,62 % | 0,18 % | 0,36 % | 1,34 % | 0,09 % |
| 100 tâches d'une écriture et 3 de 100 | 5,3 | 2,22 % | 2,28 % | 0,51 % | 1,11 % | 0,24 % | 0,27 % |

- **La borne garde son risque dans 14 lignes sur 15** (au plus 5 %, jugé sur la borne haute de Wilson).
  - Exception : profil de Pareto, barre faible du commerce, 5,04 % (borne haute 5,13 %).
  - L'écart au nominal (0,04 point) est du même ordre que l'erreur Monte-Carlo (0,05 point), mais le critère écrit n'est pas tenu.
  - **Limite rapportée**, sans changement de règle (méthode, section 7).
- **Cause (déduite, non testée à part).** La borne traite x · n_eff ÷ n comme un compte binomial sur n_eff tâches. Quand quelques grandes tâches portent l'essentiel des écritures, x n'est plus qu'une somme de quelques gros paquets. Sa loi est plus heurtée qu'une binomiale de même variance, et la borne de Clopper-Pearson, prudente pour une vraie binomiale, perd alors un peu de sa prudence.
- **Portée.**
  - Ces profils sont hors du générateur, qui donne des tailles presque égales dans un type.
  - La part de R4 à tort au niveau de la configuration n'est pas mesurée sous ces profils. R4 exige en plus que chaque configuration jugeable soit établie, ce qui la réduit.
  - À 0,5 fois la barre, le dépassement d'un type est établi à tort dans 1,1 à 1,35 % des cas sous trois profils à queue lourde. La cible de 1 % porte sur R4, au niveau de la configuration, pas sur un type : rapporté.

**Monotonie.** Dans chaque série (mécanisme, ρ, témoins), aucune alerte : ni baisse de la part de R4, ni hausse de la part délégable de plus de deux erreurs types quand le multiple augmente.

Le plan (1.5) porte désormais les chiffres de la partie R4, sans la mention « à confirmer ».

### 10.6 Contrôle 3 complet (seconde partie) : méthode

> **Moteur.** Amendement de R4 (6c02d69), plus un ajout de sortie sans effet sur l'étiquette : sans configuration délégable, le point 4 nomme les configurations sans type jugeable, hors du constat de R4 (tranché par Claude, 07/11 ; `rejeu/CHOIX_AMENDEMENT_R4.md`, point 8).
>
> **Réglages.** Ce sont ceux du quatrième passage (R0 = B = 200, K = 10, e = 5 %), avec la même graine maîtresse (2026110503). Les 19 mondes du quatrième passage gardent donc leurs données et leurs graines du moteur, d'où une comparaison appariée. Dossier : `resultats_v5/`.
>
> Tout ce qui suit est fixé et commité avant le lancement.

**Monde C.** L'étiquette attendue devient « R4 ou preuves insuffisantes » : rien n'est délégué dans les deux cas. La part de R4 mesure la puissance ; la partie R4 en laisse attendre environ 43 % (bêta, 5 fois la barre, ρ = 0,3, témoins tenus).

**Monde B-seuil** (120 répétitions, ajouté en dernier). C'est E-fort, avec une dérive du commerce de 1,56 écriture réversible par partie au lieu de 4.
- **Étalonnage** (`b_seuil/`, méthode écrite avant le calcul, graine 2026110702). On mesure la valeur centrale de B-tout dans les cellules de configuration du commerce à enjeu faible, rapportée au budget.

  | Écritures réversibles par partie | 1 | 1,75 | 2,5 | 3,25 |
  |---|---|---|---|---|
  | Valeur centrale ÷ budget | 0,81 | 1,07 | 1,21 | 1,31 |

  L'interpolation donne 1,56. Contrôle sur 12 répétitions à 1,56 : 0,997 fois le budget (± 0,042).
- **Près du seuil, le max-T est puissant** : à 1,07 fois le budget, R1 sort déjà dans 3 répétitions sur 6.
- **Attendu** : R1 dans au plus 5 % des répétitions (niveau global du max-T) ; sans R1, « confirmée ». La part de R1 est lue avec la valeur centrale obtenue dans les mêmes répétitions.

**Monde V** (30 répétitions, ajouté en dernier). C'est A, à un dixième des tâches de la réserve (au moins deux par strate). Attendu : « preuves insuffisantes », motif « aucun type jugeable ».

**Tableaux.**
- L'attendue est comptée avec sa mention, et elle peut regrouper plusieurs étiquettes (`mondes.conforme`).
- Les motifs de « preuves insuffisantes » sont comptés.
- Chaque répétition garde aussi la valeur centrale ÷ budget de chaque cellule de configuration jugée, et la liste des configurations sans type jugeable.

**Pas refaites ici** : l'étude de délégabilité et les cases critiques (partie R4, 10.1 à 10.5).

**Volume de calcul** : 799 répétitions, environ 3 h prévues sur 12 processus.

### 10.7 Contrôle 3 complet : résultats

> 799 répétitions en 10 498 s (2 h 55) sur 12 processus ; `resultats_v5/`, commit 258bd4f. Empreintes conformes (`lancer.py --verifier`). Tableaux : `.venv/bin/python -m controle3.rapport_tableaux` (cinquième passage apparié au quatrième).

**En bref.**
- **L'amendement ne change que ce qu'il doit changer.**
  - Les 19 mondes du quatrième passage comptent 649 répétitions appariées. 32 changent d'étiquette, toutes de R4 à « preuves insuffisantes » ; les 617 autres gardent la leur.
  - Le nombre de configurations délégables et l'oracle ne bougent dans aucun monde.
- **R4 ne sort plus que dans C, où il est juste.** Les 19 R4 à tort du quatrième passage deviennent « preuves insuffisantes », motif « dépassement non établi » : A 1, A-rho7 6, A-rho9 6, A-het 3, D 2, D-inerte 1.
- **Monde C : 100 % conforme** à l'attendue mise à jour (« R4 ou preuves insuffisantes »).
  - 12 R4 (48 %, IC 30–67 %), pour environ 43 % attendus.
  - 13 « preuves insuffisantes » : 10 « non établi », 3 « établi sous ρ̂ propre ».
- **Monde V : 29 répétitions sur 30** sortent « preuves insuffisantes, aucun type jugeable ». La trentième est un R1 tiré d'une seule tâche, par la règle du plan pour les cellules sans variation bootstrap (ci-dessous).
- **Monde B-seuil : R1 dans 10 répétitions sur 120 (8,3 %, IC 4,6–14,7 %)**, au-dessus des 5 % attendus.
  - Mais la cellule de Haiku est à 1,050 fois le budget, et les 10 R1 portent tous sur des cellules où Haiku intervient : ces R1 sont justes.
  - Le monde n'était donc pas au seuil exact. Seconde mesure : 10.8.
- **Aux volumes du plan, aucun faux R1** dans les 539 répétitions où B-tout tient son budget (au plus 0,6 %, règle de trois).

**Étiquettes.**

| Monde | Attendu | n | R5 | R1 | preuves insuffisantes | R4 | R2 | confirmée | Part de l'attendue (IC 95 %) |
|---|---|---|---|---|---|---|---|---|---|
| A | confirmée | 80 | 0 | 0 | 1 | 0 | 0 | 79 | 99 % (93–100) |
| A-tf | confirmée | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 100 % (91–100) |
| A4 | confirmée | 40 | 0 | 0 | 0 | 0 | 31 | 9 | 22 % (12–38) **⚠** |
| A-rho0 | confirmée | 30 | 0 | 0 | 0 | 0 | 0 | 30 | 100 % (89–100) |
| A-rho7 | confirmée | 30 | 0 | 0 | 6 | 0 | 0 | 24 | 80 % (63–90) |
| B | R1 | 60 | 0 | 60 | 0 | 0 | 0 | 0 | 100 % (94–100) |
| B100 | R1 | 20 | 0 | 20 | 0 | 0 | 0 | 0 | 100 % (84–100) |
| C | R4 ou preuves insuffisantes | 25 | 0 | 0 | 13 | 12 | 0 | 0 | 100 % (87–100) |
| D | R2 (délégation inférieure à un témoin) | 50 | 0 | 0 | 2 | 0 | 48 | 0 | 96 % (87–99) |
| D-piege | confirmée | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 100 % (91–100) |
| E | confirmée + garantie hors hypothèse | 50 | 0 | 0 | 0 | 0 | 0 | 50 | 100 % (93–100) |
| E-fort | R1 | 30 | 0 | 30 | 0 | 0 | 0 | 0 | 100 % (89–100) |
| F1 | R5 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 100 % (68–100) |
| F2 | R5 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 100 % (68–100) |
| K | R2 (délégation inférieure à un témoin) | 8 | 0 | 0 | 0 | 0 | 8 | 0 | 100 % (68–100) |
| D-inerte | R2 (aucune délégation établie) | 40 | 0 | 0 | 1 | 0 | 39 | 0 | 98 % (87–100) |
| A-rho9 | confirmée | 30 | 0 | 0 | 6 | 0 | 0 | 24 | 80 % (63–90) |
| A-logit | confirmée | 30 | 0 | 0 | 0 | 0 | 1 | 29 | 97 % (83–99) |
| A-het | confirmée | 30 | 0 | 0 | 3 | 0 | 0 | 27 | 90 % (74–97) |
| B-seuil | confirmée | 120 | 0 | 10 | 0 | 0 | 0 | 110 | 92 % (85–95) |
| V | preuves insuffisantes (aucun type jugeable) | 30 | 0 | 1 | 29 | 0 | 0 | 0 | 97 % (83–99) |

- A4 (22 % « confirmée ») et A-logit (1 R2) sortent exactement comme au quatrième passage. A4 reste la limite de puissance des témoins (M2) : témoins à environ 3 fois le budget, battus dans 22 % des répétitions.
- Dans A-rho7, A-rho9 et A-het, la part de l'attendue ne bouge pas, mais l'écart change de nature : la règle ne dit plus « agents peu fiables », elle dit qu'elle manque de preuve.

**Monde V : le R1 tiré d'une seule tâche.**
- **Rejouée** (répétition 24) : les 11 cellules jugées de B-tout sont dans l'aviation à enjeu faible. Chacune n'a qu'une tâche porteuse (2 tâches, 20 à 60 écritures).
- 42 répliques bootstrap sur 200 n'y tirent pas la tâche porteuse : 0 écriture au dénominateur, donc 0/0, stocké en NaN. Les autres répliques varient (ordres et validateur), mais l'écart type calculé vaut NaN. Le test `sd > 0` du moteur est faux pour NaN : les 11 cellules sont traitées comme « sans variation », et c* n'est pas calculable (vérifié en rejouant la répétition ; corrigé le 07/11 : une première version de ce paragraphe disait « écart type nul »).
- **Le plan prévoit ce cas** (5.14, point 1) : « Une cellule dont l'écart type bootstrap est nul (aucune variation entre répétitions) n'entre pas dans le maximum ; son dépassement n'est établi que si son estimation dépasse le budget. » Le moteur fait exactement cela (`maxt.depassement_etabli`, test `test_max_t_mecanique`).
- **Dix cellules dépassent le budget** (1,9 à 3,8 fois), d'où un R1 tiré des erreurs d'une seule tâche. B-tout tient pourtant son budget dans V, comme dans A : c'est un faux R1.
- **Part** : 1 sur 30 (3,3 %, IC 0,6–16,7 %), dans la cible de 5 % de faux R1.
- **Aux volumes du plan** : dans les 769 répétitions hors V, aucun dépassement n'est établi sur une cellule sans variation. Les cellules à une tâche y passent par le max-T, et une seule tâche ne peut pas y établir de dépassement (9.3, point 5).
- **Limite rapportée.** Exposition et suite : 9.3, point 5.

**Monde B-seuil : les R1 sont justes.**

| Cellule de configuration (commerce, enjeu faible) | Valeur centrale ÷ budget (120 répétitions, ± 1,96 erreur type) |
|---|---|
| Haiku | 1,050 ± 0,009 |
| Opus | 1,001 ± 0,013 |
| Sonnet | 0,998 ± 0,012 |
| Moyenne des trois (grandeur de l'étalonnage) | 1,016 ± 0,009 |

- **Les 10 R1 portent tous sur Haiku.** Dans 6 d'entre eux, sa configuration est établie avec des scénarios de changement de modèle où il intervient ; dans les 4 autres, seulement ces scénarios. Bornes basses de 1,000 à 1,056 fois le budget ; c* de 2,0 à 2,6.
- **Lecture.** B-tout dépasse vraiment son budget de 5 % chez Haiku. La part de 8 % mesure la puissance du max-T contre un dépassement de 5 % dans une configuration, pas son niveau au seuil.
- **Cause.** L'étalonnage (`b_seuil/METHODE.md`, section 2) visait la moyenne des trois cellules, et une moyenne au seuil peut laisser une cellule au-dessus. Son contrôle sur 12 répétitions montrait déjà l'écart (Haiku 1,032, Opus 0,959, Sonnet 1,001), que le critère de moyenne ne regardait pas.
- **Suite** (tranché par Claude) : seconde mesure, avec la méthode écrite et commitée avant le calcul (`b_seuil/METHODE.md`, section 4 ; commit 258bd4f). Dérive 1,40, cellule la plus haute visée à 0,99–1,00, graine neuve, 120 répétitions : 10.8.

**Durées** : 201 s par répétition dans B-seuil, 19 s dans V, 135 à 307 s ailleurs.

### 10.8 Monde au seuil du max-T : seconde mesure

> Méthode écrite et commitée avant le calcul (`b_seuil/METHODE.md`, section 4 ; commit 258bd4f). Monde B-seuil à la dérive 1,40, graine neuve (2026110703), 120 répétitions en 1 957 s sur 12 processus. Même chemin de calcul que le contrôle 3, vérifié par un test (`tests/test_controle3_b_seuil.py`). Sorties : `b_seuil/seconde_mesure.jsonl`, `seconde_mesure.md`, `seconde_mesure_meta.json`.

**Résultat : 0 R1 sur 120** (IC de Wilson 0–3,1 %). Les 120 répétitions sortent « confirmée ».

**Le monde est bien au seuil.**
- La cellule la plus haute est à 1,006 ± 0,010 fois le budget (scénario Sonnet puis Haiku, changement silencieux). La configuration de Haiku est à 1,003 ± 0,010.
- Les neuf cellules où Haiku intervient sont entre 0,994 et 1,006 ; les six autres entre 0,955 et 0,988.
- La lecture fixée d'avance s'applique donc (plus haute cellule entre 0,98 et 1,02) : la part de R1 est le niveau du max-T au seuil.

**Lecture.**
- **Le max-T tient son niveau au seuil** : aucun R1, borne haute 3,1 %, pour une cible d'au plus 5 %. Le point 2 de 9.3 est mesuré.
- **Il est prudent, mais il voit les dépassements nets.** Toutes les mesures de ce passage, du seuil vers le haut :

| Dépassement vrai de la cellule la plus haute | R1 |
|---|---|
| 1,006 (seconde mesure) | 0 sur 120 (0–3,1 %) |
| 1,050 (Haiku, première mesure, 10.7) | 10 sur 120 (4,6–14,7 %) |
| environ 1,09 (Haiku, étalonnage à la dérive 1,75) | 3 sur 6 |
| 1,35 à 1,47 (E-fort) | 30 sur 30 |

- **Portée.** Ces mesures portent sur des cellules du commerce à 24 à 38 tâches porteuses. Le niveau n'est pas mesuré sur des cellules à très peu de tâches. Aux volumes du plan, une cellule portée par une seule tâche passe par le max-T sans pouvoir y établir de dépassement ; seule la branche des lois bootstrap dégénérées établit sans mesure (9.3, point 5).

## 11. Sixième passage (07/11, soir) : cellules non testables

> Après la décision d'Otsoa du 07/11 (9.3, point 5 ; plan, 5.14, point 2). Une cellule est non testable si elle compte moins de deux tâches porteuses, ou si son écart type bootstrap est nul ou non défini. Elle sort du maximum, n'établit aucun dépassement, et est publiée avec son motif. Moteur : commit 0a908cf ; choix de mise en œuvre : `rejeu/CHOIX_CELLULES_NON_TESTABLES.md` ; recherche : `reports/Cellules portées par une seule tâche.md`.

### 11.1 Cellules de 2 à 5 tâches porteuses au budget exact

> Méthode écrite et commitée avant le calcul (`porteuses/METHODE.md`, commit 9a229c6). Graine 2026110704 ; 40 cases de 10 000 tirages, et 8 cases de puissance de 2 000 tirages ; B = 2 000 ; 13 s sur 12 processus. Sorties : `porteuses/porteuses.csv`, `porteuses.md`, `meta.json`.

**Montage.**
- Cadre de 20 tâches, comme l'aviation.
- Une famille de 11 cellules (une configuration et dix scénarios) portées par les mêmes k tâches, placées exactement au budget de l'enjeu faible.
- Corrélation intra-tâche ρ de 0 à 1 (modèle bêta-binomial) ; tailles des tâches égales (40 écritures) ou inégales (20 à 60).
- Décision : le max-T du moteur amendé.
- Aucune autre cellule dans la famille : c* y est le plus bas possible, ce qui est le cas le moins favorable au niveau.

**Résultat : toutes les cases tiennent, avec une très large marge.**

| Tâches porteuses | Dépassement établi à tort, pire case (ρ et tailles) | Borne haute de Wilson | Cellules testables, en moyenne sur 11 |
|---|---|---|---|
| 1 (contrôle) | 0 sur 80 000 | 0,04 % par case | 0 |
| 2 | 0,09 % | 0,17 % | 0,6 à 10,0 |
| 3 | 0,15 % | 0,25 % | 0,7 à 10,2 |
| 4 | 0,10 % | 0,18 % | 0,8 à 10,4 |
| 5 | 0,10 % | 0,18 % | 0,7 à 10,5 |

- **Seuil retenu, selon la règle écrite d'avance : deux tâches porteuses**, celui de la décision.
- **Le max-T est très prudent sur ces cellules.** Il ne les sort qu'avec plusieurs tâches en erreur, parce que le bootstrap fait varier le nombre de copies de chaque tâche. C'est ce qu'on voyait déjà sur les cellules à une tâche aux volumes du plan (9.3, point 5).
- **Le prix : la puissance est faible**, à titre descriptif (ρ = 0,3, tailles égales) :

| Tâches porteuses | 2 fois le budget | 5 fois le budget |
|---|---|---|
| 2 | 0,1 % | 0,9 % |
| 3 | 0,5 % | 4,9 % |
| 4 | 0,4 % | 7,2 % |
| 5 | 0,7 % | 6,2 % |

- **Limites, déclarées d'avance** :
  - données synthétiques, sans les paliers de B-tout, les K ordres ni le validateur ;
  - un seul cadre, un seul niveau.

### 11.2 Contrôle 3 refait (sixième passage)

> Mêmes mondes, mêmes réglages et même graine que le cinquième passage (2026110503) : comparaison appariée, seul le moteur change. `resultats_v6/`, lancé le 07/11 à 17 h 24. Puis la mesure au seuil refaite avec les graines de la seconde mesure (`b_seuil/seconde_mesure_v6.*`).

799 répétitions en 9 896 s (2 h 45) sur 12 processus ; empreintes conformes (`lancer.py --verifier`). Tableaux : `.venv/bin/python -m controle3.rapport_tableaux` (sixième passage apparié au cinquième).

**En bref.**
- **Une seule étiquette change sur 799 : la répétition 24 de V**, de R1 à « preuves insuffisantes, aucun type jugeable ». Le monde V est conforme dans 30 répétitions sur 30.
- **Les 769 autres répétitions gardent leur étiquette**, B-seuil compris : toujours 10 R1 sur 120, justes, puisque la cellule de Haiku y est à 1,05 fois le budget (10.7).
- **Au seuil exact** (seconde mesure refaite, mêmes graines) : toujours 0 R1 sur 120 (borne haute 3,1 %), et 120 « confirmée ».

**Ce qui change sous les étiquettes.**
- **c\* baisse dans 93 répétitions** (écart médian −0,33) et ne monte jamais : les cellules à une seule tâche, qui entraient dans le maximum avec un écart type positif, n'y comptent plus.
- **Cellules établies** : B et B100, où le dépassement est réel, en gagnent de 1 à 15 dans 15 et 4 répétitions, sans en perdre aucune. V perd les 10 cellules de son faux R1.
- **Témoins battus** : trois changements, sans effet sur l'étiquette.
  - Dans la répétition 13 de V, la liste fixe et le tri par le risque étaient battus par des cellules dégénérées : ils ne le sont plus. C'était un autre faux constat de l'ancienne règle, côté témoins.
  - Dans la répétition 23 de C, le tri par le risque devient battu, c* ayant baissé ; les agents de C sont à 5 fois la barre.
- **Cellules non testables, par motif** (répétitions 1 de A, 0 de B et 0 de E, rejouées) :

| Répétition | Cellules jugées | Testables | Moins de 2 tâches porteuses | Aucune variation bootstrap |
|---|---|---|---|---|
| A, 1 | 46 | 33 | 11 (aviation, estimation positive) | 2 (estimation nulle) |
| B, 0 | 84 | 45 | 15 (aviation, estimation positive) | 24 (estimation nulle) |
| E, 0 | 36 | 19 | 0 | 17 (estimation nulle) |

  - Les cellules « aucune variation bootstrap » sont des cellules sans aucune erreur : estimation nulle, rien à établir. L'ancienne règle les jugeait déjà sur leur estimation, sans effet.
  - Aucun écart type non défini aux volumes du plan : ce cas n'apparaît que dans V.

**Lecture.** L'amendement ferme la seule voie par laquelle un faux R1 est sorti du contrôle 3, et le faux constat symétrique côté témoins. Il ne change aucune autre étiquette. Il rend le max-T un peu plus puissant ailleurs, sans toucher à son niveau au seuil (0 sur 120).

**Pas refaits** : la partie R4 du cinquième passage (`passage5_r4/`). Elle n'appelle que le point 4 et l'étiquette, que l'amendement ne touche pas.

## 12. Max-T recentré (08/11) : septième passage (F1) et huitième (F3)

> Après la relecture indépendante C13 du code du verdict (constat C1, M1 au suivi : `revues/2026-11-07_C13_moteur_verdict.md`) et la mesure préenregistrée des corrections (`maxt_niveau/`, méthode commitée avant le calcul ; résultats : commit 9d7f9d9). T* est recentré sur la moyenne des répétitions de chaque cellule, et c* est ramené à 0 s'il est négatif. **Otsoa a retenu le 97,5e centile (F3) le 08/11** ; le septième passage (F1, 95e centile) sert de comparaison. Avec cette correction : le motif « estimation non définie » (C5) et la tolérance d'un écart type nul portée à quatre epsilon du float32 (C6). Moteur F1 : commit 5e87ae0 ; choix de mise en œuvre : `rejeu/CHOIX_MAXT_RECENTRE.md` ; plan, 5.14, point 2. Une relecture indépendante de ces changements (08/11) a relevé que deux tirages antérieurs devaient être cumulés avec la mesure : 12.1.

### 12.1 Niveau du max-T : la mesure

> Méthode : `maxt_niveau/METHODE.md`, écrite avant le calcul. Graine 2026110705 ; réglages du contrôle 3 (R0 = B = 200, K = 10) ; 510 répétitions en 7 567 s sur 12 processus. Sous l'hypothèse nulle complète, chaque budget est posé à la moyenne des valeurs centrales de sa cellule : toutes les cellules sont à leur frontière. C'est la configuration d'hypothèses la moins favorable dans un monde donné, pas le pire monde possible. Sorties : `maxt_niveau/maxt_niveau.md`, `maxt_niveau.csv`, `meta.json` ; données brutes non versionnées, empreintes dans `meta.json`.

**Part des répétitions où au moins un dépassement est établi** (cible : au plus 5 % dans N1, N2 et P2) :

| Formule | N1 : monde A, nulle complète (200) | N2 : E-fort, nulle complète (100) | P2 : seuil exact (120) | P1 : 1,05 fois le budget (60) | P3 (100) et P4 (30) : franc dépassement |
|---|---|---|---|---|---|
| F0, d'origine | **15,5 %** (11,1–21,2) | 3 % | 0,8 % | 3 sur 60 | 100 % |
| F1, recentrée | 5,0 % (2,7–9,0) | 1 % | 0 % | 2 sur 60 | 100 % |
| F2, bootstrap-t recentré | 15,0 % | 9 % | 1,7 % | 2 sur 60 | 100 % |
| F3, recentrée, 97,5e centile | 3,0 % (1,4–6,4) | 0 % | 0 % | 1 sur 60 | 100 % |
| F4, jackknife | 9,0 % | 8 % | 0 % | 0 sur 60 | 100 % |

Entre parenthèses : intervalle de Wilson à 95 %. En P3 et P4, les bornes basses de Wilson valent 96,3 % et 88,6 % : la puissance y est entière pour les cinq formules, ce qui ne les départage pas.

- **Sur les seuls tirages de la mesure, F1 et F3 sont acceptables, et la règle écrite d'avance retient F1**, la plus puissante en P1 et la plus simple. F1 y est pile à 5,0 % (10 sur 200) : un rejet de plus, et elle n'était plus acceptable. En P1, l'écart avec F3 tient à une répétition sur 60.
- **Deux tirages antérieurs mesurent la même quantité** : monde A, hypothèse nulle complète, T* recentré, sans plancher (le plancher ne joue dans aucune famille, voir plus bas).
  - relecture C13 (C1, preuve 4) : 15 sur 200 ; moteur d'origine 42 sur 200 ;
  - vérification du coordinateur (en tête de `METHODE.md`) : 15 sur 200 ; moteur d'origine 37 sur 200.
- **En cumul, F1 est à 40 sur 600, soit 6,7 % (Wilson 4,9 à 9,0 %)** : elle ne tient probablement pas 5 %. Le tirage de la mesure est le plus bas des trois. Appliquée à tous les tirages, la règle retient F3. Sur les mêmes tirages, les rejets de F3 sont un sous-ensemble de ceux de F1.
- **Recommandation de Claude : F3 ; décidé par Otsoa le 08/11.** Une mesure de confirmation (400 tirages neufs de N1, `maxt_niveau/CONFIRMATION.md`, écrite avant le calcul) donnera le niveau publié avec R1, sans choisir la formule.
- **D'où vient l'excès restant** : descriptif, calculé après la mesure (`maxt_niveau/descriptif_apres_mesure.py`, sortie `descriptif_apres_mesure.txt`). La cause n'est pas établie.
  - Sur les 10 rejets de F1 en N1, 6 portent sur des cellules de WorkBench à enjeu faible, 2 sur la banque, 1 sur l'aviation et 1 sur le commerce (14 cellules à la fois). Sur les 6 rejets de F3, 5 portent sur WorkBench.
  - Testée seule, une cellule de scénario de WorkBench à enjeu faible est déclarée en dépassement à tort dans 32 répétitions sur 200 avec F1. Elle n'est testable que dans 154 d'entre elles : 32 sur 154. Avec F3, la pire cellule seule rejette 27 fois sur 200.
  - Le recentrage corrige le décalage moyen des répétitions (−0,4 écart type en médiane ; −0,7 à −0,8 pour deux cellules de la banque), pas leur dispersion. Pour 8 cellules de scénario de WorkBench et 2 de la banque, l'écart type bootstrap ne vaut que 0,60 à 0,82 fois l'écart type réel de la valeur centrale entre répétitions. Pour les autres cellules mesurées, de 0,99 à 1,21, dont la configuration de Haiku dans WorkBench (0,99), pourtant la pire cellule seule de F3.
  - Une cellule n'est testable que si elle a des erreurs (sans erreur, son écart type est nul). Quand elle est testable, sa valeur centrale vaut en moyenne 1,30 à 1,48 fois θ_G pour les cellules de WorkBench qui rejettent le plus, et 1,54 à 1,96 fois pour celles de la banque dans N2.
  - Le niveau dépend du monde et de la composition de la famille : 5,0 % dans A, 1 % dans E-fort, 16 % pour une cellule de WorkBench testée seule. Les familles de N1 comptent de 2 à 38 cellules testables (médiane 18) ; celles de N2, de 17 à 54. Les 16 répétitions de N1 à deux cellules n'ont donné aucun rejet, ce qui laisse une borne haute de Wilson de 19 %.
  - **Plancher de c\*** : le centile brut n'a été négatif dans aucune famille des 510 répétitions. Pour une cellule testée seule, il l'est dans 0 à 3,3 % des cas selon le régime ; la borne vaut alors l'estimation (limite déclarée au plan).
- **Recoupement** (`maxt_niveau/recoupement_moteur.py`, sortie `recoupement_moteur.txt`). Sur les 510 répétitions (610 évaluations, P3 réutilisant celles de N2), le moteur corrigé et la formule F1 mesurée prennent les mêmes décisions, cellule par cellule. La nouvelle tolérance ne change la testabilité d'aucune cellule.

### 12.2 Cellules de 2 à 5 tâches porteuses, refaites

> Même méthode, mêmes graines et mêmes cases que 11.1, avec le moteur F1. `porteuses/porteuses.py --lancer --suffixe v7` (13 s) ; sorties `porteuses_v7.csv`, `porteuses_v7.md`, `meta_v7.json`, `journal_v7.txt`.

| Tâches porteuses | Dépassement établi à tort, pire case : sixième passage | Septième passage | Borne haute de Wilson (septième) |
|---|---|---|---|
| 1 (contrôle) | 0 sur 80 000 | 0 sur 80 000 | 0,04 % par case |
| 2 | 0,09 % | 0,09 % | 0,17 % |
| 3 | 0,15 % | 0,11 % | 0,20 % |
| 4 | 0,10 % | 0,05 % | 0,12 % |
| 5 | 0,10 % | 0,07 % | 0,14 % |

- **Le seuil de deux tâches porteuses tient**, toujours avec une très large marge.
- **La puissance descriptive baisse** (ρ = 0,3, tailles égales ; 2 000 tirages par case) : à cinq fois le budget, 3 sur 2 000 pour 2 tâches (18 avant, six fois moins), 3,4 % pour 3 (4,9 %), 5,5 % pour 4 (7,2 %), 5,5 % pour 5 (6,2 %). *Déduit* : une part de l'ancienne puissance venait du décentrage, qui faisait aussi les faux dépassements.
- **Refaites avec F3** (huitième passage) : fin de 12.3.

### 12.3 Huitième passage du contrôle 3 (F3), apparié au septième (F1)

> Mêmes mondes, mêmes réglages et même graine (2026110503) depuis le cinquième passage : comparaison appariée, seule la formule du max-T change (F1, 95e centile, au septième passage ; F3, 97,5e centile, au huitième). Septième passage : `resultats_v7/`, moteur 5e87ae0, 799 répétitions en 9 745 s (2 h 42) sur 12 processus ; résultats commités en 5a0a678, pas décrits jusqu'ici. Huitième : `resultats_v8/`, moteur 228c522, lancé le 08/11 à 5 h 02 ; 799 répétitions en 12 351 s (3 h 26) sur 8 processus ; empreintes conformes (`lancer.py --verifier`) ; résultats commités en bb45168. Tableaux : `.venv/bin/python -m controle3.rapport_tableaux` (huitième passage apparié au septième ; `rapport_tableaux resultats_v7 resultats_v6` pour le septième apparié au sixième).

**En bref.**
- **12 étiquettes changent sur 799** ; les 787 autres gardent la leur.
  - 11 passent de « confirmée » à R2, « délégation inférieure à un témoin », dans cinq mondes où « confirmée » est attendue : A4 5, A-rho9 3, A-tf 1, A-rho7 1, A-het 1.
  - 1 passe de R1 à « confirmée », dans B-seuil (répétition 40).
- **R1 ne sort que là où il est juste.** B 60 sur 60, B100 20 sur 20, E-fort 30 sur 30, comme au septième passage. B-seuil : 4 sur 120 (IC 95 % 1,3–8,3 %), contre 5 au septième passage et 10 au sixième ; ces R1 sont justes, la cellule de Haiku y étant à 1,05 fois le budget (10.7). Aucun R1 dans les 17 autres mondes.
- **Monde V** : toujours conforme, 30 répétitions sur 30.
- Pour mémoire, le septième passage apparié au sixième : dans A4, une répétition passe de « confirmée » à R2 et une autre de R2 à « confirmée » ; dans B-seuil, 5 R1 deviennent « confirmée » (de 10 à 5 sur 120) ; aucun autre changement.

**Étiquettes** (huitième passage). R2 vaut « délégation inférieure à un témoin », sauf dans D-inerte (« aucune délégation établie »).

| Monde | Attendu | n | R5 | R1 | preuves insuffisantes | R4 | R2 | confirmée | Part de l'attendue (IC 95 %) | Septième passage (F1) | Changements appariés |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | confirmée | 80 | 0 | 0 | 1 | 0 | 0 | 79 | 99 % (93–100) | 99 % (93–100) | aucun |
| A-tf | confirmée | 40 | 0 | 0 | 0 | 0 | 1 | 39 | 98 % (87–100) | 100 % (91–100) | confirmée → R2 : 1 |
| A4 | confirmée | 40 | 0 | 0 | 0 | 0 | 36 | 4 | 10 % (4–23) **⚠** | 22 % (12–38) **⚠** | confirmée → R2 : 5 |
| A-rho0 | confirmée | 30 | 0 | 0 | 0 | 0 | 0 | 30 | 100 % (89–100) | 100 % (89–100) | aucun |
| A-rho7 | confirmée | 30 | 0 | 0 | 6 | 0 | 1 | 23 | 77 % (59–88) | 80 % (63–90) | confirmée → R2 : 1 |
| B | R1 | 60 | 0 | 60 | 0 | 0 | 0 | 0 | 100 % (94–100) | 100 % (94–100) | aucun |
| B100 | R1 | 20 | 0 | 20 | 0 | 0 | 0 | 0 | 100 % (84–100) | 100 % (84–100) | aucun |
| C | R4 ou preuves insuffisantes | 25 | 0 | 0 | 13 | 12 | 0 | 0 | 100 % (87–100) | 100 % (87–100) | aucun |
| D | R2 (délégation inférieure à un témoin) | 50 | 0 | 0 | 2 | 0 | 48 | 0 | 96 % (87–99) | 96 % (87–99) | aucun |
| D-piege | confirmée | 40 | 0 | 0 | 0 | 0 | 0 | 40 | 100 % (91–100) | 100 % (91–100) | aucun |
| E | confirmée + garantie hors hypothèse | 50 | 0 | 0 | 0 | 0 | 0 | 50 | 100 % (93–100) | 100 % (93–100) | aucun |
| E-fort | R1 | 30 | 0 | 30 | 0 | 0 | 0 | 0 | 100 % (89–100) | 100 % (89–100) | aucun |
| F1 | R5 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 100 % (68–100) | 100 % (68–100) | aucun |
| F2 | R5 | 8 | 8 | 0 | 0 | 0 | 0 | 0 | 100 % (68–100) | 100 % (68–100) | aucun |
| K | R2 (délégation inférieure à un témoin) | 8 | 0 | 0 | 0 | 0 | 8 | 0 | 100 % (68–100) | 100 % (68–100) | aucun |
| D-inerte | R2 (aucune délégation établie) | 40 | 0 | 0 | 1 | 0 | 39 | 0 | 98 % (87–100) | 98 % (87–100) | aucun |
| A-rho9 | confirmée | 30 | 0 | 0 | 6 | 0 | 3 | 21 | 70 % (52–83) | 80 % (63–90) | confirmée → R2 : 3 |
| A-logit | confirmée | 30 | 0 | 0 | 0 | 0 | 1 | 29 | 97 % (83–99) | 97 % (83–99) | aucun |
| A-het | confirmée | 30 | 0 | 0 | 3 | 0 | 1 | 26 | 87 % (70–95) | 90 % (74–97) | confirmée → R2 : 1 |
| B-seuil | confirmée | 120 | 0 | 4 | 0 | 0 | 0 | 116 | 97 % (92–99) | 96 % (91–98) | R1 → confirmée : 1 |
| V | preuves insuffisantes (aucun type jugeable) | 30 | 0 | 0 | 30 | 0 | 0 | 0 | 100 % (89–100) | 100 % (89–100) | aucun |

**Ce qui change sous les étiquettes** (lu dans `repetitions.jsonl` des deux passages, répétition par répétition).
- **Seul c\* change.** La testabilité des cellules, les configurations délégables et le verdict du témoin « tout faire valider » sont les mêmes dans les 799 répétitions.
- **c\* de B-tout monte dans les 632 répétitions où il est défini**, de 0,27 en médiane (de 0,03 à 6,34), et ne baisse jamais : sur les mêmes répétitions bootstrap, le 97,5e centile ne peut pas être sous le 95e. Il n'est défini dans aucun des deux passages pour les 167 autres (D, D-inerte, D-piege, V et K : aucune cellule jugée, ou aucune testable).
- **Cellules établies de B-tout.** B en perd dans 24 répétitions (1 à 12 chacune ; 1 871 → 1 770 au total), B100 dans 13 (1 à 14 ; 471 → 394), B-seuil dans 4 (2 à 8 ; 30 → 13). E-fort n'en perd aucune (449). Aucune cellule nouvelle : celles de F3 sont toujours parmi celles de F1. B, B100 et E-fort restent en R1 dans toutes leurs répétitions.
- **Témoins.** Leur c\* monte aussi (liste fixe : 785 répétitions ; tri par le risque : 788), et leurs cellules établies baissent, de 6 753 à 6 134 pour la liste fixe et de 7 537 à 6 767 pour le tri, toutes répétitions réunies. Aucun témoin ne devient battu.
- **Les 11 « confirmée » perdues.** Dans chacune, un témoin battu par le budget au septième passage ne l'est plus : ses cellules établies, 1 à 6, tombent à 0, et la charge de B-tout ne le bat pas non plus. C'est le tri par le risque dans 8 cas, la liste fixe dans 2, les deux dans 1. Dans A4, les deux témoins sont battus par le budget dans 10 % des répétitions, au lieu de 22 %.
- **La répétition 40 de B-seuil** : ses deux cellules établies avec F1 ne le sont plus avec F3.
- **Sans effet sur l'étiquette**, un témoin cesse aussi d'être battu par le budget dans 14 autres répétitions : 6 de B (R1), 4 de C (R4 ou « preuves insuffisantes »), et une de A-het, de A-rho9, de D-inerte et de V (« preuves insuffisantes » ou R2 « aucune délégation établie »).

**Lecture.**
- F3 rend le max-T plus prudent partout, chez B-tout comme chez les témoins, sans toucher au reste du calcul.
- Le prix, dans le contrôle 3 : 11 « confirmée » de moins dans cinq mondes, dont 5 dans A4, où les témoins ne dépassent le budget que d'environ 3 fois (M2) ; et un R1 juste de moins sur 120 dans B-seuil, à 1,05 fois le budget.
- Aucun R1 à tort n'apparaît. Le niveau de F3 est mesuré à part : au seuil exact en 12.4, sous l'hypothèse nulle complète en 12.5.

**Cellules de 2 à 5 tâches porteuses, refaites avec F3.** Même méthode, mêmes graines et mêmes cases que 11.1 et 12.2, moteur 228c522 : `porteuses/porteuses.py --lancer --suffixe v8` (16 s sur 12 processus) ; sorties `porteuses_v8.csv`, `porteuses_v8.md`, `meta_v8.json`, `journal_v8.txt`.

| Tâches porteuses | Dépassement établi à tort, pire case : septième passage (F1) | Huitième (F3) | Borne haute de Wilson (huitième) |
|---|---|---|---|
| 1 (contrôle) | 0 sur 80 000 | 0 sur 80 000 | 0,04 % par case |
| 2 | 0,09 % | 0 sur 80 000 | 0,04 % par case |
| 3 | 0,11 % | 0,01 % | 0,06 % |
| 4 | 0,05 % | 0,02 % | 0,07 % |
| 5 | 0,07 % | 0 sur 80 000 | 0,04 % par case |

- **Le seuil de deux tâches porteuses tient**, avec une marge plus large encore ; le contrôle de cohérence (une tâche, jamais établi) tient.
- **La puissance descriptive baisse encore** (ρ = 0,3, tailles égales ; 2 000 tirages par case). À cinq fois le budget : 0 sur 2 000 pour 2 tâches (3 avec F1), 0,7 % pour 3 (3,4 %), 2,1 % pour 4 (5,5 %), 2,2 % pour 5 (5,5 %). À deux fois : de 0 à 0,1 % (de 0,1 à 0,5 % avec F1).

### 12.4 Monde au seuil exact, refait (F3)

> Même méthode et mêmes graines que la seconde mesure (10.8) : dérive 1,40, graine 2026110703, 120 répétitions ; moteur 228c522. `b_seuil/seconde_mesure.py --lancer --suffixe v8`, lancé le 08/11 à 8 h 28 ; 2 411 s sur 8 processus. Sorties : `seconde_mesure_v8.jsonl`, `seconde_mesure_v8.md`, `seconde_mesure_v8_meta.json`, `journal_seconde_mesure_v8.txt`.

**Résultat : 0 R1 sur 120** (IC de Wilson 0–3,1 %), et 120 « confirmée ». Aucune étiquette ne change par rapport aux sixième et septième passages.

- **Même monde, mêmes données** : la plus haute cellule reste à 1,006 ± 0,010 fois le budget (scénario Sonnet puis Haiku, changement silencieux). La lecture fixée d'avance s'applique (plus haute cellule entre 0,98 et 1,02) : la part de R1 est le niveau du max-T au seuil.
- **Sous l'étiquette** (lu dans `seconde_mesure_v7.jsonl` et `seconde_mesure_v8.jsonl`) : c\* monte dans les 120 répétitions, de 0,22 en médiane. La plus haute borne basse du max-T, rapportée au budget, reste sous 1 partout : au plus 0,979, contre 0,989 avec F1.
- **Lecture.** Au seuil exact, F3 tient la cible de 5 % : aucun R1, borne haute 3,1 %. La mesure du niveau (12.1, P2, sur d'autres tirages) donnait aussi 0 sur 120. Portée inchangée : des cellules du commerce à 24 à 38 tâches porteuses (10.8).

### 12.5 Niveau du max-T : confirmation (F3)

> Méthode : `maxt_niveau/CONFIRMATION.md`, écrite et commitée avant le calcul (54d923c). Régime N1 seul : monde A, hypothèse nulle complète, chaque budget posé au θ_G de sa cellule. 400 répétitions neuves (graine 2026110705, rang 10, qu'aucun régime de la mesure n'avait utilisé) ; réglages du contrôle 3 (R0 = B = 200, K = 10) ; les cinq formules évaluées par `maxt_niveau.py`, telles que mesurées. Lancée le 08/11 à 9 h 08 ; 5 883 s sur 8 processus. Sorties : `confirmation.csv`, `confirmation_meta.json`, `journal_confirmation.txt` ; données brutes non versionnées, empreinte dans `confirmation_meta.json` ; résultats commités en bb45168.

**Part des répétitions où au moins un dépassement est établi à tort** (cible : au plus 5 %) :

| Formule | Tirage neuf : rejets sur 400 | Part (Wilson) | Cumul | Part cumulée (Wilson) |
|---|---|---|---|---|
| F0, d'origine | 84 | 21,0 % (17,3–25,3) | 194 sur 1 000 | 19,4 % (17,1–22,0) |
| F1, recentrée | 31 | 7,8 % (5,5–10,8) | 71 sur 1 000 | 7,1 % (5,7–8,9) |
| F2, bootstrap-t recentré | 72 | 18,0 % (14,5–22,1) | 102 sur 600 | 17,0 % (14,2–20,2) |
| **F3, retenue** | **22** | **5,5 % (3,7–8,2)** | **28 sur 600** | **4,7 % (3,2–6,7)** |
| F4, jackknife | 40 | 10,0 % (7,4–13,3) | 58 sur 600 | 9,7 % (7,6–12,3) |

Cumul fixé d'avance (`CONFIRMATION.md`, section 3) : pour F0 et F1, le tirage de la mesure, les deux tirages antérieurs (12.1) et celui-ci ; pour F2, F3 et F4, le tirage de la mesure et celui-ci. Pour F3 : 6 sur 200, puis 22 sur 400.

**Niveau publié avec R1** (lecture fixée d'avance, section 4) : la part cumulée de F3, **4,7 %, soit 28 répétitions sur 600 (Wilson 3,2 à 6,7 %).**

**Face à la cible de 5 %.**
- La part cumulée est sous 5 %. Le cas prévu pour une part cumulée de F3 au-dessus de 5 % (« aucune formule acceptable ») ne s'applique donc pas.
- La marge est mince, et l'intervalle passe au-dessus de 5 % : sa borne haute vaut 6,7 %. La mesure ne montre pas que F3 tient 5 %.
- Sur le seul tirage neuf, F3 est au-dessus de la cible : 22 sur 400, soit 5,5 % (Wilson 3,7 à 8,2 %).
- Le 3,0 % cité lors du choix (12.1 ; plan, section 6 ; `REGLE.md`) venait du seul tirage de la mesure, le plus bas des deux. Le niveau publié est 4,7 %.

**Pour le choix de F3.**
- La mesure ne choisit pas la formule (`CONFIRMATION.md`, section 1), et elle n'est pas refaite (section 4). F3 reste la formule décidée par Otsoa le 08/11.
- Sur les 400 tirages neufs, F3 reste la plus basse des cinq : 22 rejets, contre 31 à 84.
- F1 est écartée plus nettement qu'au moment du choix : 7,1 % sur 1 000 tirages, et même la borne basse de son intervalle (5,7 %) est au-dessus de 5 %.
- En cumul, aucune formule mesurée n'a une borne haute sous 5 %. Celle de F3 est la plus basse (6,7 %).

**Limites.**
- Un seul monde, A, toutes les cellules à leur frontière : le cas le moins favorable dans ce monde, pas le pire monde possible. Le niveau dépend du monde et de la composition de la famille (12.1).
- θ_G est estimé sur les 400 répétitions mêmes, avec une erreur d'environ 5 % d'un écart type (`CONFIRMATION.md`, section 5).
- Le cumul suppose que les tirages mesurent la même quantité ; ils ne diffèrent que par la graine (même section).
- Réglages du contrôle 3 : 200 répétitions bootstrap, et non les 2 000 du plan.
- Les formules sont calculées par `maxt_niveau.py`. Leur recoupement avec le moteur, cellule par cellule, porte sur les 510 répétitions de la mesure (`recoupement_moteur.txt`, F3 : aucun écart) ; il n'est pas refait sur ces 400 répétitions.

**Méthode écrasée, puis restaurée.**
- En fin de calcul, `confirmation.py` écrit son tableau dans `confirmation.md`. Sur ce disque, insensible à la casse, c'est le même fichier que `CONFIRMATION.md` : la méthode a été remplacée par le tableau.
- Elle est restaurée telle que commitée en 54d923c. Son empreinte (2f5d7e84…) est celle que `confirmation_meta.json` a relevée au lancement : c'est bien le texte présent quand le calcul est parti.
- Le tableau imprimé reste dans `journal_confirmation.txt`, et les valeurs dans `confirmation.csv`.
- Relancer `--evaluer` écraserait de nouveau la méthode. Le script n'était pas changé ici, pour garder l'empreinte relevée au lancement (SHA-256 de l'ancien `confirmation.py` : `8417426480de480fa0da575517a62307915a015ba70b725b4b852281e52c1957`, celle de `confirmation_meta.json`). *Corrigé le 08/11 (4ae1fce)* : la sortie s'appelle `confirmation_resultats.md`, avec une garde anti-écrasement ; empreinte du script corrigé `36e54076…`. (Mis à jour le 09/11, audit avant le gel, O6 et O11.)

## Annexe · fichiers et reproduction

- Code : `mondes.py` (mondes et générateur), `harnais.py` (une répétition, étude de délégabilité), `lancer.py` (lancement unique, tableaux, empreintes), `rapport_tableaux.py` (tableaux de ce rapport, sans calcul du moteur).
- Tests : `tests/` (aide `aide_controle3.py`).
- Troisième passage : `resultats_v3/` (mêmes fichiers ; `delegabilite.jsonl`, environ 24 Mo, n'est pas versionné : son empreinte est dans `delegabilite.jsonl.sha256`, et `lancer.py --lancer` le régénère, graines fixes). Tableaux : `.venv/bin/python -m controle3.rapport_tableaux` (troisième passage apparié au second ; `rapport_tableaux resultats_v2 resultats` pour le second apparié au premier). Diagnostic de N3 : `options_n3/rho_estimateurs.py` (environ 15 secondes sur 12 processus), qui écrit `options_n3/rho_estimateurs.csv`.
- Second passage : `resultats_v2/` (mêmes fichiers ; `delegabilite.jsonl` au format compact : par type faible, [classe prouvée, erreurs, écritures, borne haute ÷ barre, ρ̂, source de ρ̂], et la liste des types estimés sous la barre). Tableaux : `.venv/bin/python -m controle3.rapport_tableaux resultats_v2 resultats` ; le premier passage reste dans `resultats/`, avec le code du commit bbbaa72.
- Résultats bruts : `resultats/repetitions.jsonl` (une ligne par répétition : étiquette, points 0 à 4, cellules établies, classes calibrées, mentions), `resultats/delegabilite.jsonl`, tableaux `frequences.csv` et `delegabilite.csv`, `meta.json`, `journal.txt`.
- Taille : `resultats/` fait environ 51 Mo, dont 47 Mo pour `delegabilite.jsonl` (détail des classes de chaque répétition).
- Refaire les tableaux : `cd simulation && .venv/bin/python -m controle3.lancer --resumer` puis `.venv/bin/python -m controle3.rapport_tableaux`.
- Cinquième passage, partie R4 : `passage5_r4/` (`METHODE.md`, `passage5_r4.py`, `meta.json`, `passage5_r4.csv`, `tailles_inegales.csv`, `passage5_r4.md`, `journal.txt`). `tirages.csv` (22 Mo) n'est pas versionné : son empreinte est dans `tirages.csv.sha256`. Refaire : `cd simulation && env -u ANTHROPIC_API_KEY .venv/bin/python controle3/passage5_r4/passage5_r4.py --lancer` (environ 1 h 50 sur 12 processus). Le script refuse de partir si `meta.json` existe ou si le moteur a des modifications non commitées. Résumé seul, depuis `tirages.csv` : `--resumer`.
- Cinquième passage, contrôle complet : `resultats_v5/` (`repetitions.jsonl`, environ 10 Mo, versionné ; `frequences.csv`, `meta.json`, `journal.txt`). Refaire : `cd simulation && env -u ANTHROPIC_API_KEY .venv/bin/python -m controle3.lancer --lancer` (environ 2 h 55 sur 12 processus), puis `.venv/bin/python -m controle3.rapport_tableaux` (apparié à `resultats_v4/`). Contrôle du code : `lancer --verifier`.
- Monde au seuil du max-T : `b_seuil/` (`METHODE.md`, écrite avant chaque calcul ; étalonnage : `etalonnage.py`, `etalonnage.jsonl`, `etalonnage.md` ; seconde mesure : `seconde_mesure.py --lancer` (environ 33 min), `seconde_mesure.jsonl`, `seconde_mesure.md`, `seconde_mesure_meta.json`, `journal_seconde_mesure.txt`).
- Cellules portées par une seule tâche (9.3, point 5) : `une_tache/une_tache.py --lancer` (environ 8 min), `une_tache.jsonl`, `une_tache.md`, `journal.txt`.
- Sixième passage : `resultats_v6/` (mêmes fichiers que `resultats_v5/`, environ 2 h 45) ; mesure au seuil refaite : `b_seuil/seconde_mesure.py --lancer --suffixe v6` (`seconde_mesure_v6.*`, `journal_seconde_mesure_v6.txt`) ; cellules de 2 à 5 tâches porteuses : `porteuses/porteuses.py --lancer` (13 s ; `METHODE.md`, `porteuses.csv`, `porteuses.md`, `meta.json`, `journal.txt`).
- Septième et huitième passages (08/11) : `resultats_v7/` (F1) et `resultats_v8/` (F3), mêmes fichiers que `resultats_v5/` (environ 2 h 42 sur 12 processus et 3 h 26 sur 8) ; mesure au seuil : `b_seuil/seconde_mesure.py --lancer --suffixe v7` ou `v8` ; cellules de 2 à 5 tâches porteuses : `porteuses/porteuses.py --lancer --suffixe v7` ou `v8`. Niveau du max-T : `maxt_niveau/` (`METHODE.md` et `maxt_niveau.py --lancer` pour la mesure, 12.1 ; `CONFIRMATION.md` et `confirmation.py --lancer`, environ 1 h 38 sur 8 processus, pour la confirmation, 12.5) ; données brutes non versionnées, empreintes dans `meta.json` et `confirmation_meta.json`. `confirmation.py --evaluer` écrit `confirmation_resultats.md` (corrigé le 08/11 : l'ancien nom `confirmation.md` écrasait `CONFIRMATION.md` sur un disque insensible à la casse, 12.5).
