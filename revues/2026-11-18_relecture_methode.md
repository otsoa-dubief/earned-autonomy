# Relecture méthode et statistiques · 18 novembre 2026

Article : « Earned Autonomy for AI Agents » (`article/latex/main.pdf`, 51 pages, version du 17 novembre).
Angle : méthode et statistiques seulement. Comparé à lui-même, puis à `PLAN_EXPERIENCE.md`, `REGLE.md`, `JOURNAL_CHANGEMENTS.md`, `simulation/rejeu/classes.py`, `outils/analyses_exploratoires.py`.
Non ouvert : `experience/`, `donnees/`, `pilote/`, `data/`, `notes/`. Aucun chiffre n'a été confronté aux sorties.

## Verdict

**Révisions mineures, mais nombreuses.** Aucun chiffre faux trouvé, la borne est juste et ses conditions sont dites ; l'étiquette R4 suit le plan figé.
Neuf points de rédaction statistique sont à corriger avant dépôt, dont trois qui changent ce que le lecteur croit (I1, I2, I3). Aucun constat bloquant.

## Ce qu'un relecteur exigeant reprocherait en premier

1. **La mesure de l'erreur.** 3 alertes confirmées sur 10 levées par l'auteur. L'intervalle (7 à 65 %) dépasse la tolérance du seul type qui porte R4 (63 %). Voir I3.
2. **R4 tient à un fil, et ce fil dépend d'un ρ̂ estimé.** À ρ = 1, le type n'est pas jugeable. Voir I1 et I2.
3. **Résultat nul sans puissance.** c* = 7,0, aucune cellule démontrée. L'article le dit ; rien à ajouter.
4. **Le palier 2 fait toute la baisse de charge sur WorkBench** sans compter de dégât. L'article le dit (limite 26).

## Constats importants

### I1. La jugeabilité se lit à ρ̂, le dépassement à ρ = 1 ; la table 6 mélange les deux
- Endroit : p. 3 (section 5) ; p. 30 (table 6 et sa note) ; `article/atelier.md:35`.
- Citations : « a type is judgeable if zero errors would bring it under its bar (n_eff × bar ≥ 0.6905, about ln 2) ». Table 6, ligne WorkBench/Haiku ECR : « n_eff (ρ=1) 81.6 … n_eff × bar 0.740 ».
- Vérifié : 81,6 × 0,00757 = 0,618, pas 0,740. Le 0,740 vient d'un n_eff à ρ̂ = 0,819 (97,7). Pour Opus et Sonnet (ρ̂ = 1), les deux colonnes concordent (0,606 ; 0,604).
- Conséquence : à ρ = 1, le type qui porte R4 n'est pas jugeable (0,618 < 0,6905). L'étiquette repose donc sur une corrélation estimée, alors que le texte met en avant « at ρ = 1 ».
- C'est conforme au plan (5.13, N3 : décisions au taux médian sous ρ̂, preuves à ρ = 1). Ce n'est pas un écart. C'est non dit.
- Correction : dire en section 5 et en note de table que la jugeabilité utilise n_eff sous ρ̂. Ajouter une colonne « n_eff (ρ̂) ». Écrire en 6.2 : « at ρ = 1 the type would not be judgeable (0.618) ».

### I2. L'intervalle de ρ̂ (table X6) n'est pas calculé avec l'estimateur du moteur
- Endroit : p. 4 (6.2), p. 22 (C.6.2), p. 47 (table X6), p. 49 (limite 21) ; `outils/analyses_exploratoires.py:250-256` ; `outils/tables_exploratoires.py:99`.
- Citations : « Appendix D, Table X6: 9.6 % of bootstrap draws exceed 0.885 » ; note de X6 : « engine estimator classes.rho_anova ».
- Vérifié : le ρ̂ de l'étiquette vient de `rho_fc_strates` (Fleiss–Cuzick stratifié, grappes tâche × type ; `classes.py:383-404`). X6 rééchantillonne `rho_anova` sur des grappes par tâche, tous types réunis. Le plan a justement écarté cet estimateur (5.13, N3 : il « diluait les erreurs groupées d'un type »).
- Conséquence : la loi bootstrap est centrée sur 0,800, pas 0,819. Le seuil 0,885 est donc plus loin qu'en réalité. Le « 9,6 % » sous-estime probablement le risque de bascule vers « preuves insuffisantes ».
- Correction : refaire X6 avec `rho_fc_strates` sur les strates du moteur. À défaut, retirer « engine estimator », dire que l'estimateur diffère, et ne plus citer 9,6 % dans le corps.

### I3. La phrase sur les fausses confirmations est fausse telle qu'écrite
- Endroit : p. 6 (section 7) ; `article/atelier.md:61` ; table X2 p. 43 ; limite 23 p. 50.
- Citation : « high-stakes rates stay established with 31 % to 79 % false confirmations (exploratory, Appendix D), within what the author's blind sample allows (3 of 10 confirmed alerts lifted; 95 % interval 7 % to 65 %) ».
- Vérifié : estimation ponctuelle 30 %, borne haute 65 % (Clopper-Pearson recalculé : 6,7 à 65,2 %). Une tolérance de 31 % n'est pas « dans ce que l'échantillon permet » : elle est au ras de l'estimation et très sous la borne haute.
- Vérifié aussi : le type qui porte R4 tolère 63 %. À 65 %, sa borne basse tombe à 0,69 %, sous la barre de 0,76 % (recalcul). Il ne résiste donc pas à tout l'intervalle.
- Autre point : 5 confirmées par vague, alors que la vague 1 a 232 alertes et la vague 2 en a 2 529. Le 3 sur 10 n'est pas un taux représentatif.
- Correction : écrire que seuls les types tolérant plus de 65 % résistent à tout l'intervalle (X2 : 12 sur 20) ; que le type de R4 est à la limite (63 contre 65) ; que l'échantillon est stratifié par vague.

### I4. Les taux mis en avant viennent de la moitié la plus haute
- Endroit : p. 4 (6.4), p. 24-25 (C.6.4), tables 6 et 6 bis p. 30-31 ; `article/atelier.md:49`.
- Citations : « money-moving writes on airline and retail err 6.5 % to 13.3 % » ; « The error rates themselves, 6.5 % to 13.3 %, are the strong fact » ; « Elsewhere the pooled rates stay of the same order ».
- Vérifié par différence entre les deux tables (réserve entière moins calibration = confirmation) :

| Type ARG | Calibration | Confirmation (déduit) | Réserve entière |
|--|--|--|--|
| aviation Haiku | 41/308 = 13,3 % | 48/809 = 5,9 % | 8,0 % |
| commerce Haiku | 231/2 511 = 9,2 % | 106/2 661 = 4,0 % | 6,5 % |
| commerce Opus | 32/492 = 6,5 % | 6/520 = 1,2 % | 3,8 % |
| commerce Sonnet | 33/496 = 6,7 % | 9/532 = 1,7 % | 4,1 % |
| banque Opus | 38/80 = 47,5 % | 10/70 = 14 % | 32,0 % |
| banque Sonnet | 42/75 = 56,0 % | 5/49 = 10 % | 37,9 % |

- Conséquence : écart de 2 à 5 fois entre moitiés. « Same order » est trop généreux. L'étiquette reste liée à la calibration (plan), mais le « fait fort » descriptif doit donner les deux.
- Correction : donner en 6.4 les taux de la réserve entière à côté (3,8 à 8,0 % hors banque). Dire que l'écart entre moitiés montre l'hétérogénéité par tâche.

### I5. Les intervalles descriptifs des dégâts en plus ont une couverture connue comme mauvaise, non dite
- Endroit : p. 20 (C.5.3) ; figure 1 p. 5 ; « worst upper bound » p. 23, 26, tables p. 40-41.
- Citation : « It was selected before the freeze by a coverage simulation […] with a worst coverage of 0.933 against a 0.93 threshold ».
- Vérifié dans le plan (5.13) : ce 0,933 est mesuré sur la différence appariée de charge, avec une erreur de Monte-Carlo « d'environ 0,35 point ». Sur les cellules du budget, la première simulation donnait pour le jackknife-t une pire couverture de 0,549. C'est la raison de Q13.
- Conséquence : les barres de la figure 1, la borne « 1,67 fois le budget » et l'alerte des tests de résistance reposent sur des intervalles dont la couverture n'est pas établie. Le mot « descriptive » ne suffit pas.
- Correction : dire en C.5.3 sur quelle quantité le 0,933 a été mesuré, l'erreur de Monte-Carlo, et le 0,549 sur les cellules du budget. Écrire « nominal 95 % ».

### I6. La règle de ρ̂ est mal décrite
- Endroit : p. 24 (C.6.4, « Correlation ») ; `article/brouillon.md:294`.
- Citation : « it is estimated per configuration when there are at least 10 errors in at least 5 tasks, and pooled over all configurations otherwise ».
- Vérifié (`classes.py:383-395`, plan 5.13) : ρ̂ = max(plancher 0,3 ; valeur commune) ; la valeur propre ne remplace que si elle est plus grande.
- Vérifié dans la table 6 : banque/Haiku (353 erreurs) et commerce/Haiku (251 erreurs) affichent 0,402, la valeur commune, malgré plus de 10 erreurs dans plus de 5 tâches.
- Correction : écrire la règle complète, plancher compris.

### I7. Une règle préenregistrée de la relecture n'apparaît pas
- Endroit : p. 17-18 (B.4.3), p. 22 (C.6.1), limite 9 p. 48. Plan 4.4.
- Plan : « si Claude a levé une vraie erreur à enjeu fort, toutes les alertes fortes levées sont relues ».
- Article : « Of the author's four disagreements, three lifted a confirmed alert and one confirmed a lifted alert ». Le niveau d'enjeu de cette alerte n'est pas donné. La règle n'est citée nulle part (recherche dans `atelier.md` et `brouillon.md`).
- Non vérifié : si la règle s'est déclenchée. Je constate seulement le silence.
- Correction : donner le niveau de l'alerte. Si enjeu fort : dire si la relecture complète a eu lieu, sinon déclarer l'écart (D14).

### I8. Validité de la borne basse à ρ = 1 : dire d'où elle vient
- Endroit : p. 4 (section 5), p. 23 (C.6.4).
- Citation : « Classes are computed at ρ = 1, without assumption on the within-task correlation but under the effective-size approximation ».
- Vérifié : le plan ne revendique la validité sans hypothèse qu'« à zéro erreur » (borne haute). Pour une borne basse avec x_eff non entier (aviation/Opus ARG : 0,62 erreur effective), rien n'est démontré. `REGLE.md` (amendement du 7 novembre) donne une mesure : R4 à tort « au plus 2,8 % du temps à la barre ». L'article ne la cite pas.
- Correction : citer cette mesure et sa nature (simulation). Remplacer « without assumption » par « conservative under an exchangeable-correlation model ».

### I9. Deux écarts visibles, absents de l'annexe A
- **Partie non jouée.** p. 21 : « 14,265 were played […] (the remaining one was not in its plan file) ». Plan 2.5 (P20) : les parties non jouées sont publiées. Ni la configuration ni la cause ne sont données. Par arithmétique (table des réussites p. 28), toutes les tâches analysées ont leur compte ; la partie manquante est donc sur une tâche retirée, sans effet. À dire, et à inscrire en annexe A.
- **Arrêt de la vague 1.** p. 21 : « 72.10 $ spent against a 72.00 $ stop ». Avec p. 18 (« 60.53 USD », plafond 1,5 fois, arrêt à 80 %) : 72,64 $. Le plan (2.5) donne un plafond de 90,78 $, soit 72,62 $. Un arrêt à 72,00 $ suppose un plafond de 90,00 $. À expliquer ou corriger.

## Constats mineurs

- **M1. Le seuil 0,6905 n'est pas général.** p. 3, p. 30. Critère exact : 1 − 2^(−1/n_eff) ≤ barre. Équivalent en n_eff × barre : 0,6905 pour la barre de WorkBench faible seulement ; 0,689 (banque), 0,684 (commerce), 0,663 (aviation). Aucune classe ne change (vérifié sur la table 6). Écrire « about ln 2 (0.6905 for this bar) ».
- **M2. Niveau de l'intervalle non dit.** p. 24 : « Haiku 8.6 % [4.1 ; 15.6] ». Recalcul : ce sont deux bornes unilatérales à 95 %, donc un intervalle bilatéral à 90 %. Le dire, aussi en légende de la figure 2.
- **M3. Intervalles dégénérés.** Table G p. 34-36 : « 0.043 [0.000* ; 1.000*] », « 0.004 [0.004 ; 0.004] ». Table 7 p. 33 : « 90.1 [69.6 ; 110.5] » pour une charge bornée à 100. Marquer « non informatif » ou « non calculable » ; une largeur nulle n'est pas une incertitude nulle.
- **M4. La borne, là où elle est invoquée sans conditions.** p. 1 (introduction) : « Without any assumption of statistical control, such a plan bounds outgoing quality […] and a cycle argument gives a bound on the extra errors ». Ajouter « under immediate detection of the errors the check sees ». p. 3 : « The bound holds for detected errors » est ambigu, car 1/(1 + N d) compte toutes les erreurs ; écrire « provided misses are random ».
- **M5. « 40 action types ».** p. 1, 2, 4. Ce sont 40 couples configuration × type. Écrire « 40 configuration–type pairs ».
- **M6. « Secondary rules had no established excess ».** p. 6. Vrai en analyse principale. Table 9 p. 41 : B-regular, delay10, 4 dépassements établis. Préciser.
- **M7. 1 991 alertes confirmées contre 1 779 erreurs.** La somme de la table 6 bis donne 1 779. L'écart (212) n'est pas expliqué. Une phrase suffit.
- **M8. « 72.10 $ » puis « 72.13 $ »** pour la vague 1 (p. 21, deux paragraphes). Dire que l'un est le montant à l'arrêt.
- **M9. « per 100 such writes ».** p. 6 et 25. La table X5 compte pour 100 écritures du type, pas pour 100 écritures au palier 2.
- **M10. Reste de français.** Table p. 40 : « charge moyenne non calculable (aucune configuration délégable) ».
- **M11. Chapeau de l'annexe A.** p. 11 : « None of it changes the frozen code ». D12 remplace une fonction figée en mémoire. Écrire « the frozen files ».
- **M12. Taux de réussite.** Table p. 28 : méthode de l'intervalle non dite. Plan 5.13 : réunion de Wilson et du bootstrap par tâches.

## Vérifié, sans constat

- **Borne.** Argument par cycles refait : (1/d) ÷ (N + 1/d) = 1/(1 + N d). Forme de Lieberman (1 − f)/(1 + i f) correcte, facteur (1 − f) retiré à bon droit. 1/(1 + N d) ≤ 1/(d (N + 1)) ≤ barre. Passage au niveau : budget × s/q, puis 0,95 × budget × s/q. Conditions dites en section 3 et en B.3.4 (constat immédiat, erreurs vues, ratés non ciblés, long terme si d < 1, mélange s/q).
- **Table 1.** Les douze N recalculés depuis les barres : tous justes. Volumes de certification 7 348, 33 956, 36 009 : justes (ln 20 ÷ barre). 598 écritures : juste.
- **Clopper-Pearson.** Bornes recalculées sur cinq lignes de la table 6 : identiques. 0/21 → 13,3 % : juste. 3/10 → 7 à 65 % : juste.
- **Comptes.** 180 = 21 + 108 + 51 ; 51 = 11 + 11 + 14 + 15 ; 6 non testables ; 27 « fragiles » ; 40 types = 20 + 13 + 7 ; 41 types et 22 au-dessus (6 bis) ; 1 067 erreurs en calibration ; 104 refusées ; 2 761 = 1 991 + 770 ; 770 = 75 + 78 + 331 + 283 + 3 ; 14 266 planifiées ; 13 623 analysées (somme de deux tables) ; 91 exclusions = 77 + 10 + 2 + 2.
- **Max-T.** 28/600 = 4,7 %, 40/600 = 6,7 %, 27/200 : conformes au plan (5.14 et section 6). Écart de choix F1/F3 déclaré.
- **Écarts D0 à D13.** Chaque ligne du journal postérieure au gel (lignes 55 à 71) a son écart. Ordre des étiquettes, seuil 13/15, 0,93, non-testabilité, R4 : conformes au plan.
