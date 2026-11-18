# Amendement de R4 : choix de codage (07/11)

Décision d'Otsoa du 07/11, avant toute donnée d'évaluation : la règle recommandée après la simulation des règles
candidates au moteur (`simulation/controle3/options_r4/`). Texte de la règle : `PLAN_EXPERIENCE.md`, 1.5 et 5.14,
point 4 ; `REGLE.md` ; `JOURNAL_CHANGEMENTS.md` (ancienne et nouvelle définitions côte à côte).

## 1. Ce qui change dans le moteur

- `classes.depassement_etabli` : borne basse unilatérale de Clopper-Pearson à 95 %, sur la taille effective à ρ = 1,
  au-dessus de la barre, soit la classe prouvée « au-dessus » déjà calculée (aucune machinerie nouvelle pour la preuve).
- `classes.statut_configuration` : délégable, jugeable, établie (un type **jugeable** établi), établie sous le ρ̂
  propre, ρ̂ propre, ρ de lecture, plus grand ρ* des types jugeables. `pipeline.familles_analyse` le calcule pour chaque
  configuration, sur le jeu de calibration (`Analyse.statuts`) ; `delegables` et `jugeables` en sont tirés, sans
  changement.
- `classes.rho_propre` : extrait de `rho_par_configuration`, qui l'appelle (même résultat).
- `classes.borne_basse`, `classes.rho_bascule`, `classes.taches_pour_etablir` : publication.
- `decision.point4` : R4 si `etablie` ; sinon « preuves insuffisantes » (`PREUVES_INSUFFISANTES`), avec son motif ;
  `decision.mention` publie le motif avec l'étiquette ; `decision.combiner_statuts` pour l'échange des rôles.
- Sorties : `ecart.csv` (borne basse sous ρ̂, dépassement établi, ρ*, statut, tâches pour établir cinq fois la barre) ;
  `decision.csv` (`sorties.lignes_point4` : dépassement établi ou motif, ρ* et ρ̂ propre des configurations non
  établies). `bout_en_bout` porte la mention jusqu'à l'étiquette finale.
- Contrôle 3 : `lancer.ETIQUETTES` et `rapport_tableaux.ETIQ` sont ceux du moteur ; « volume insuffisant », dans les
  résultats des passages précédents, se lit « preuves insuffisantes ».

## 2. Choix (Tranché par Claude)

1. **Ordre des motifs.** « Aucun type jugeable » d'abord. Puis « dépassement établi sous ρ̂ propre, pas à ρ = 1 » si
   chaque configuration jugeable non établie l'est sous son ρ̂ propre. Sinon « dépassement non établi ». Le troisième
   motif est donc exactement la différence entre la règle hybride et la règle retenue (options_r4, C-hybride-J et
   C-ρ1-J), puisqu'un dépassement établi à ρ = 1 l'est à tout ρ plus petit.
2. **Lecture au ρ̂ propre.** ρ = max(0,3 ; ρ̂ propre) pour une configuration d'au moins 10 erreurs dans au moins 5 tâches
   dont le ρ̂ propre se calcule ; ρ = 1 sinon. C'est la règle C-hybride de `options_r4/METHODE.md` : l'éligibilité seule
   compte, pas la condition du moteur « plus grand que la valeur commune ».
3. **ρ*.** Le dépassement est établi pour tout ρ < ρ* (inégalité stricte, comme « au-dessus ») ; ρ* = 1 s'il l'est à
   ρ = 1 ; aucun ρ* s'il ne l'est pas à ρ = 0. La borne basse décroît avec ρ (testé sur une grille).
4. **Une analyse sans statuts n'établit rien.** `point4` ne donne R4 que si l'établissement est connu ; une analyse
   fabriquée sans `statuts` donne « preuves insuffisantes ». Un constat négatif doit être prouvé.
5. **Échange des rôles (secondaire).** Délégable ou jugeable si la configuration l'est dans l'un des deux plis ;
   dépassement établi s'il l'est dans chaque pli où elle est jugeable ; ρ* : le plus petit de ces plis.
6. **Désaccord persistant (B2).** La mention suit l'étiquette retenue : celle des verdicts bruts si leur étiquette
   l'emporte.
7. **Tâches pour établir cinq fois la barre.** Plus petit nombre de tâches de même taille (taille effective à ρ = 1) pour
   lequel un taux observé de cinq fois la barre donne une borne basse à 95 % au-dessus de la barre.
8. **Configurations hors du constat** (ajouté le 07/11, cinquième passage du contrôle 3). Sans configuration délégable,
   `decision.point4` nomme les configurations sans type jugeable (`sans_type_jugeable`), et `decision.csv` les publie
   avec R4 ou avec les motifs « dépassement non établi » et « établi sous ρ̂ propre » : « hors du constat, aucun type
   jugeable : … ». Raison : R4 ne dit rien d'elles (plan, 1.5) ; dans le monde mixte M2, R4 sort dans 34 % des tirages,
   toujours quand le commerce n'a aucun type jugeable. Rien ne change dans l'étiquette.

## 3. Tests

`tests/test_rejeu_amendement_r4.py` (17 tests, dont 2 pour le point 8) : trois cas construits passés par le pipeline (dispersées et nettes : R4 ;
groupées sur trois tâches : « preuves insuffisantes », dépassement non établi, là où l'ancienne règle donnait R4 ;
indépendantes à environ deux fois la barre : établi sous le ρ̂ propre seulement), type non jugeable établi qui ne compte
pas, bornes basses égales à `lo` et `lo_hyp`, ρ*, échange des rôles, sorties. Tests mis à jour :
`test_rejeu_decision.py` (ordre, garde-fou), `test_rejeu_bout_en_bout.py` (mention), et
`controle3/tests/test_controle3_etiquettes.py` (nouveau). Rejeu, contrôle 3 et E1 : 302 réussis, 1 échec attendu (xfail
strict de M1, inchangé).

## 4. Empreintes

Le moteur change : `controle3.lancer --verifier` comparait le code aux empreintes du quatrième passage
(`resultats_v4/meta.json`, code du commit 49bbc3d) et signalait les fichiers changés, comme prévu. Le cinquième passage
a écrit les siennes (`controle3/resultats_v5/meta.json`, moteur des commits 6c02d69 et 04b3c55 ; contrôle complet
commité en 258bd4f) : `--verifier` les déclare conformes le 07/11.
