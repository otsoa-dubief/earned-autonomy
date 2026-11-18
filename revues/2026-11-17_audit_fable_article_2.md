# Second audit de l'article : vérification des corrections du commit 0db883e

Date : 17 novembre 2026. Relecteur : Claude (Fable 5.2), contexte neuf.
Objet : `article/brouillon.md` et `article/controle_fr.md` après le commit 0db883e, au regard des points 1 à 10 de la liste « À corriger avant la validation d'Otsoa » du premier audit (`revues/2026-11-17_audit_fable_article.md`).

## Périmètre et méthode

- Lu : le premier audit ; `git diff a400a4c..0db883e -- article/` ; `article/brouillon.md` (l. 17 à 40, 196 à 412) ; `article/controle_fr.md` ; `experience/rejeu_final/` (`retrait.csv`, `budget.csv`, `garantie.csv`, `ecart.csv`, `reussite_taches.csv`, `decision.csv`, `derive.csv`, en-tête de `volume.csv`) ; `experience/exploratoire/C_sensibilite_fausses_confirmations.csv` ; `PLAN_EXPERIENCE.md` (5.10, 5.12 point 8) ; `PLAN_SUITE.md` (section 0) ; `SUIVI.md` (l. 370 à 382 et fin) ; `JOURNAL_CHANGEMENTS.md` (lignes des 13 et 14/11).
- Non ouvert : `donnees/`, `pilote/`, `data/`, `experience/vague1/`, `experience/vague2/`, `banc/`, `simulation/`, `gel/`, `externe/`, `~/.config/`. Aucun appel payant, rien d'installé, aucun fichier existant modifié, aucun commit.
- Calculs : relecture des CSV en Python (module `csv`, lignes « # » écartées), scipy pour l'intervalle exact.
- Limite : le sens exact de la colonne `part_autonomies_nouvelles` (part des répétitions ?) n'est pas vérifiable sans le code du moteur (`simulation/`, interdit). Je garde la lecture du premier audit.
- Les numéros de ligne renvoient à `article/brouillon.md` après correction, sauf mention contraire.

## Résultat en une ligne

Six points sur dix sont faits et exacts. Trois sont faits mais à retoucher. Un contient une phrase fausse (mesure de la garantie, « at most 0.4 % »). Aucune formule interdite par R8 n'a été introduite. Aucun chiffre porteur n'est touché.

---

## Chiffres recalculés

| chiffre du texte | source | valeur recalculée | verdict |
|---|---|---|---|
| délai médian 61 et 40 écritures | `retrait.csv`, B-tout, commerce, ECR, silencieux, `delai_med` | 61,0 (→ Haiku) ; 40,0 (→ Opus) | exact |
| 95e centile 226 et 108 | idem, `delai_p95` | 226 ; 108 | exact |
| une erreur passée en moyenne | idem, `erreurs_passees_moy` | 1,0 ; 1,0 | exact |
| promus dans les 2 000 répétitions | idem, `n_promus` | 2 000 sur 2 000 (4 lignes) | exact |
| 85 % à 100 % | idem, `part_autonomies_nouvelles` | 0,848 (→ Opus, silencieux) ; 1,0 (les 3 autres) | exact (sens « des répétitions » non vérifiable) |
| 3,2 % et 3,8 % contre 2,6 % | `ecart.csv`, commerce ECR | 20/632 = 3,16 % ; 5/132 = 3,79 % ; barre 2,65 % | exact |
| lecture principale : aucun promu | `retrait.csv`, B-tout, `lecture` = principal | 8 lignes (banque), `n_promus` = 0 partout | exact |
| enjeu moyen et fort : aucune période | `derive.csv`, B-tout | 200 lignes (100 principale, 100 retard10), toutes « passe », `periodes_moy` max 0 | exact |
| 44 cellules de scénario jugées (10/12/10/12) | `budget.csv`, B-tout, principale, e = 0,05, « non réfutée », scénario | WorkBench 10, banque 12, aviation 10, commerce 12 | exact |
| 22 fragiles | idem, `fragile` | aviation 10 + commerce 12 ; WorkBench et banque : 0 | exact |
| 24 cellules sur 51 (11 WorkBench, 13 banque) | idem, 51 cellules jugées, `s_sur_q` > 1/0,95 | 24 ; WorkBench 11, banque 13 ; mêmes 24 cellules que `borne_construction` > budget | exact |
| jusqu'à 1,08 fois | `borne_construction` ÷ `budget` | 1,025 à 1,084 | exact |
| s ÷ q 0,72 à 1,14 | `s_sur_q`, 51 cellules | 0,718 à 1,141 | exact |
| aucune « garantie hors hypothèse » | `garantie_hors_hypothese` ; `s_sur_q_lo` | False × 51 ; borne basse max 0,975 | exact |
| 14 sur 15 en banque | banque, faible : 15 cellules | 14 « non réfutée », 1 « tenue, non mise à l'épreuve » (Haiku, constante) | exact |
| s ÷ q 1,04 à 1,14 en banque | idem | 1,044 à 1,141 | exact |
| palier 3 : 0,2 % à 12 % en banque | `part_rep_palier3`, 14 cellules jugées | 0,002 à 0,1195 | exact |
| 4,3 % | `garantie.csv`, B-tout, banque/Opus MSG, constante | 0,0425 | exact |
| 11,8 % | idem, Sonnet → Opus, silencieux, après la jonction | 0,118 | exact |
| « at most 0.4 % » (MSG de banque, autres modèles) | idem, lignes MSG où le modèle jugé n'est pas Opus | **0,0825** (Opus → Sonnet, silencieux) ; sinon 0,0005 à 0,004 | **faux** (voir point 5) |
| « at most 0.2 % » (WorkBench ECR) | idem, WorkBench ECR, 15 lignes | max 0,002 (Sonnet → Opus, silencieux) | exact |
| 8,1 % (banque/Opus MSG) | `ecart.csv` | 10/124 = 8,06 % | exact |
| 13 623 | `reussite_taches.csv`, somme de `parties` | 6 752 + 6 871 = 13 623 | exact |
| 98,7 % | `decision.csv`, couverture | 0,98684 | exact |
| 13 / 7 / 20 | `ecart.csv`, principal, 40 types avec données | 13 indéterminés sans erreur, 7 indéterminés avec erreurs, 20 au-dessus | exact |
| un seul type jugeable parmi les 20 | idem, `jugeable` | WorkBench/Haiku ECR seul | exact |
| 70 % à 79 % (commerce) | `C_sensibilite…csv`, commerce ARG | 0,70 ; 0,71 ; 0,79 | exact |
| 31 % à 55 % (aviation) | idem, aviation ARG | 0,31 ; 0,48 ; 0,55 | exact |
| intervalle exact 7 % à 65 % pour 3/10 | Clopper-Pearson bilatéral 95 % | 6,67 % à 65,25 % | exact |
| seuil 0,6905 | 1 − 2^(−1/n_eff) ≤ barre, barre 0,0075748 | n_eff seuil 91,160 ; n_eff × barre = 0,69052 | exact |
| 0,6930 (WorkBench/Opus, verdicts bruts) | `ecart.csv`, verdicts bruts | 0,693008 ; jugeable = True | exact |
| marge de 0,4 % | 0,693008 ÷ 0,690519 | 0,36 % | exact |
| 0,740 | `ecart.csv`, principal | 0,74022 | exact |
| 28 % des alertes levées | 770 ÷ 2 761 | 27,9 % | exact |
| environ 32 s par lot | 2 h 05 × 6 instances ÷ 1 428 lots | 31,5 s | exact |
| 3 confirmées levées, 1 levée confirmée | `SUIVI.md` l. 378 et journal (vague 1 : fiches 2 et 4 ; vague 2 : fiches 14 et 1) | 3 et 1 | conforme aux fichiers autorisés |

---

## Les dix points

### Point 1 — Supprimer la ligne périmée (constat 1) : **fait et exact**
- Preuve : la phrase « No results yet… » a disparu ; la section 6 s'ouvre sur 6.1 (l. 228 à 230).

### Point 2 — Section 6.6, limite 29, contrôle français l. 26 (constat 2) : **fait et exact**
- Preuve : l. 314, l. 380, `controle_fr.md` l. 26. Tous les chiffres recalculés (table ci-dessus).
- Remarque de forme, l. 314 : « At these levels (medium and high stakes…) » arrive avant que les niveaux soient nommés. Proposition : « At medium and high stakes, the scope of decision 5, the pass is empty: … ».
- Voir le point 10 pour deux précisions manquantes dans le contrôle français.

### Point 3 — Deux phrases fausses sur les cellules jugées (constats 3 et 4) : **fait et exact**
- Preuve : l. 314 (10, 12, 10, 12 ; 22 fragiles) ; l. 340 (14 sur 15, s ÷ q 1,04 à 1,14, palier 3 de 0,2 % à 12 %). Tout recalculé.
- La section 6.2 (l. 270, 27 mentions « fragile ») reste cohérente : 5 configurations + 22 scénarios.

### Point 4 — Borne de construction dans 24 cellules, limite 12 (constat 5) : **fait, à retoucher**
- Fait et exact : l. 340 (section 7) et l. 363 (limite 12). 24, 11, 13 et 1,08 recalculés.
- Reste : la section 6.3 (l. 274) n'a pas été touchée. Elle dit encore « the budget can only be exceeded if the actual share s […] exceeds the expected share q by about 5 % », sans dire que cette condition est remplie dans 24 des 51 cellules jugées. Le lecteur de 6.3 seul garde l'impression que la borne protège partout. Le premier audit citait cette ligne.
- Incohérence avec le français : `controle_fr.md` l. 23 place le constat des 24 cellules en « Sécurité (6.3) ». Le texte anglais ne le porte qu'en section 7 et en limite 12.
- Correction proposée, à ajouter l. 274 après « (plan 1.4) » : « That condition was met: in 24 of the 51 judged cells (11 on WorkBench, 13 on banking) s/q exceeds 1/0.95, so the construction bound there is up to 1.08 times the budget, and compliance rests only on the absence of an established excess (Section 7). »

### Point 5 — Mesure de la garantie, nuance de la l. 312 (constat 6) : **faux sur une proposition ; le reste exact**
- Exact : 4,3 %, 11,8 %, 8,1 %, « at most 0.2 % » pour WorkBench ; la nuance de 6.5 (l. 310).
- Faux, l. 316 : « banking internal messages of other models in at most 0.4 % ».
- Preuve : `garantie.csv`, B-tout, banque, MSG, après la jonction, Opus → Sonnet, silencieux : `part_rep_palier3` = 0,0825. La mesure après la jonction porte sur le type du modèle d'arrivée : les lignes ECR de banque n'existent que vers Sonnet, les lignes ILL que vers Haiku, seuls modèles où ces types sont « au-dessus ». La ligne Opus → Sonnet mesure donc les messages internes de Sonnet (11,3 % d'erreurs). Selon le plan (5.12, point 8), une autonomie déjà acquise à la jonction et non perdue compte : ces 8,3 % sont surtout de l'autonomie héritée d'Opus.
- Détail par modèle (MSG de banque, B-tout) : Opus 4,3 % en constante, 4,0 % à 11,8 % après la jonction ; Sonnet 0,2 % en constante, 0,3 % à 0,4 % après un changement annoncé ou depuis Haiku, **8,3 % après un changement silencieux depuis Opus** ; Haiku 0 % en constante, au plus 0,35 %.
- Sens de l'erreur : la phrase minimise une faiblesse de la règle. Le contrôle français ne porte pas ce chiffre, donc l'erreur n'y figure pas ; l'omission y figure.
- Correction proposée (l. 316) : « … banking/Opus internal messages (8.1 % errors) in 4.3 % of replays as a constant configuration and in up to 11.8 % after a silent change from Sonnet; banking/Sonnet internal messages (11.3 % errors) in 0.2 % as a constant configuration but in 8.3 % after a silent change from Opus, where autonomy earned by Opus was carried across the junction; banking/Haiku internal messages in at most 0.4 %; WorkBench reversible writes in at most 0.2 %. The other types classed above their bar never reached tier 3. »
- `controle_fr.md` l. 26, à compléter : « (banque/Opus, messages internes : 4,3 % des répétitions, jusqu'à 11,8 % après un changement silencieux ; banque/Sonnet : 8,3 % après un changement silencieux depuis Opus) ».
- Forme, l. 310 : après l'insertion, « It is not true of every type… » et « They are not a success of B-tout » n'ont plus de référent clair. Proposition : « This does not hold for every type above its bar: banking/Opus internal messages reached tier 3 in 4.3 % of replays (Section 6.6, guarantee measure). The witnesses' excesses are not a success of B-tout. »
- Non fait, sans gravité : la section 5 ne décrit toujours pas cette mesure (remarque du constat 6). Une ligne en 5.2 suffirait.

### Point 6 — Résumé (constats 7 et 8) : **fait et exact**
- Preuve : l. 21. 13 623, 98,7 %, « its usefulness could not be judged », phrase sur le sens d'une erreur, 3 sur 10. Conclusion (l. 388) : même ajout, plus « none of the twelve » (constat 24, en prime).
- À savoir : le résumé fait 245 mots (cible 200, limite arXiv tenue ; `SUIVI.md`). À décider par Otsoa, pas une erreur.
- « Results in brief » (l. 37) n'a pas reçu la phrase sur le sens d'une erreur. Ce n'était pas demandé. Pas de contradiction.

### Point 7 — Discussion (constats 9, 10, 15) : **fait et exact**
- Constat 9, l. 344 : 13 / 7 / 20, un seul jugeable. Exact.
- Constat 10, l. 342 : « a different way to tie autonomy to a budget » ; « Our data say nothing about CASE's mechanism ». Conforme à la correction demandée et à la section 2.
- Constat 15, l. 338 : 70 % à 79 %, 31 % à 55 %, 7 % à 65 %. Exact.
- Réserve reprise du premier audit, non levée : rien dans les fichiers autorisés ne dit que les trois levées de l'auteur portent sur l'enjeu fort. La phrase ne l'affirme pas ; elle reste juste.

### Point 8 — Limite sur la relecture (constat 12) : **fait et exact**
- Preuve : l. 360 (limite 9). 32 s, 3 et 1, 28 % : vérifiés.
- Remarque : D7 (l. 403) donne « about 2 h 05 with six instances » sans la réserve, mais renvoie à la limite 9. Suffisant.

### Point 9 — Critère de jugeabilité exact (constat 16) : **fait, à retoucher (hors du brouillon)**
- Fait et exact dans le brouillon : l. 256, 326, 372, 381 ; `controle_fr.md` l. 22.
- Non fait : `article/FORMULATION_VERDICT.md` l. 30 (« n_eff × barre ≥ ln 2 = 0,693 ») et `article/resultats/tables.md` l. 134 (« n_eff × bar ≥ ln 2 = 0.693 »). Le premier audit demandait la retouche du premier. La note de la table 6 ira en annexe : elle contredira le texte (0,69301 < 0,69315 et pourtant jugeable).
- Correction : « n_eff × barre ≥ 0,6905 (critère exact 1 − 2^(−1/n_eff) ≤ barre ; environ ln 2) » dans les deux fichiers. La table se régénère par `outils/tables_article.py`.

### Point 10 — Report dans `controle_fr.md` : **fait, à retoucher**
- Fait : corrections 2 (l. 26), 4 (l. 23 et 31), 5 (l. 26), 6 (résumé, l. 11), CASE et 13 / 7 / 20 (l. 31), 32 s (l. 35), 0,6905 (l. 22), « au plus 0,38 » (l. 23, constat 22).
- Manque 1 : la robustesse à enjeu fort (constat 15, partie de la correction 7) n'est pas en français. Ajouter l. 31 : « Les taux à enjeu fort gardent leur ordre de grandeur : en commerce, ils restent établis même si 70 à 79 % des erreurs confirmées étaient fausses ; en aviation la marge est plus mince (31 à 55 %), dans ce que ta relecture n'exclut pas (3 sur 10, intervalle exact de 7 à 65 %). »
- Manque 2 : la conclusion française (l. 43) n'a pas la phrase ajoutée en anglais. Ajouter : « Les erreurs comptées sont des erreurs d'action confirmées contre un seul chemin attendu par tâche ; 3 alertes confirmées sur 10 ont été levées dans ta relecture. »
- Manque 3, l. 26 : dire « en lecture secondaire seulement (estimation au-dessus de la barre) » et « l'autonomie est redonnée ensuite dans 85 à 100 % des répétitions ». Sans cela, le retrait paraît plus solide qu'il n'est.
- Manque 4 : le point 5 ci-dessus (8,3 % pour banque/Sonnet).
- Placement : l. 23 range les 24 cellules en 6.3 ; voir le point 4.

---

## Régressions

**R1. Phrase fausse introduite (l. 316).** Voir le point 5. Seule affirmation nouvelle contredite par un CSV.

**R2. Section 6.3 contre section 7.** Voir le point 4. Pas une contradiction logique, mais 6.3 énonce une condition sans dire qu'elle est remplie, alors que la section 7 et la limite 12 disent qu'elle l'est dans 24 cellules.

**R3. Limite 21 contre 6.6, incohérence rendue visible (l. 372).** « B-tout did delegate (tier 3 on retail and airline, tier 2 on WorkBench and banking) ». Le texte corrigé dit maintenant que le palier 3 est atteint en banque (0,2 % à 12 % des répétitions, l. 340) et que 10 cellules de scénario de WorkBench sont jugées (l. 314). `budget.csv` : WorkBench/Haiku, enjeu faible, palier 3 dans 31 % des répétitions en configuration constante, jusqu'à 49 % en scénario (ce n'est pas le type ECR, que `garantie.csv` donne à 0,05 % ; sans doute les messages internes, 2 erreurs sur 292). La phrase était là avant le commit ; elle n'est pas fausse (« did delegate »), mais incomplète.
- Correction : « (tier 3 on retail and airline, and in a minority of replays on WorkBench and banking; tier 2 on WorkBench and banking) ».

**R4. « Mainly volume, and in part the mix » (l. 340).** Un peu fort. Le mélange n'a limité aucun résultat : aucun dépassement, valeur centrale au plus à 0,38 fois le budget. Il a seulement affaibli la garantie dans 24 cellules. Le français (« surtout le volume ; dans 24 cellules jugées, la borne seule ne garantit pas le budget ») est plus juste.
- Correction : « Volume. The mix did not bind either, but it weakened the guarantee: … ».

**R5. Règle R8.** Aucune formule interdite introduite. Vérifié par recherche : « nothing to delegate » seulement comme nom préenregistré ou nié (l. 35 reste à traiter, constat 23, mineur) ; « keeps the budget » seulement dans l'énoncé de H1 (l. 196) et nié en limite 22 ; aucune fourchette « times the bar » ; aucun classement des modèles (la phrase « replaced by Haiku or Opus (3.2 % and 3.8 %) » donne deux taux sans les ordonner). `controle_fr.md` l. 31 : « ni qu'il n'y a rien à déléguer », en négation.

**R6. Phrases plus fortes que les données.** Aucune autre. « Almost never grants tier 3 to WorkBench reversible writes (at most 0.2 % of replays) » est exact. « Withdrawal took a median of 61 and 40 writes » est exact et bien borné par « secondary reading only ».

**R7. Registre des sources (R6 du plan).** Les chiffres nouveaux (61, 40, 226, 108, 85 %, 4,3 %, 11,8 %, 24, 1,08, 14 sur 15, 13 623, 0,6905, 0,6930, 7 % à 65 %, 32 s, 28 %) n'ont pas de ligne dans `article/sources_chiffres.csv` (68 lignes, inchangé). Le constat 13 ne s'aggrave pas en nature, mais s'allonge. À faire avant la mise en page.

**R8. Section 6.1.** Elle ne donne pas 13 623, que le résumé cite. Ajouter une phrase l. 234 : « 13,623 episodes enter the analysis (6,752 calibration, 6,871 confirmation; `reussite_taches.csv`). »

Points « avant la mise en page » (annexes, registre, mineurs 17 à 38) : aucun ne devient plus grave, sauf l'allongement noté en R7 et la note de la table 6 (point 9).

---

## Cohérence anglais / français

- Résumé : fidèle, phrase à phrase.
- 6.1, 6.2, 6.4, 6.5, 6.7 : cohérents.
- 6.3 : le français porte les 24 cellules, l'anglais non (point 4).
- 6.6 : cohérent sur les chiffres ; le français omet « lecture secondaire », la ré-attribution (85 à 100 %), et les messages internes de Sonnet (points 5 et 10).
- Section 7 : le français omet la robustesse à enjeu fort ; il est plus juste que l'anglais sur « ce qui a limité l'étude » (R4).
- Section 9 : le français omet la phrase sur le sens d'une erreur.
- Limites : cohérent ; la remarque du constat 36 (trois marques, pas deux) reste ouverte, mineure.

---

## Verdict

**Fond validable, à une condition** : corriger d'abord la phrase de la l. 316 (point 5) et la reporter dans `controle_fr.md` l. 26, puisque c'est le texte français qu'Otsoa valide. L'étiquette R4, la jugeabilité, le point 1, l'écart de délégation et tous les chiffres porteurs sont exacts et inchangés. Les corrections bloquantes du premier audit (constats 1 et 2) sont faites et exactes.

### Retouches, par ordre d'importance

1. l. 316 et `controle_fr.md` l. 26 : banque/Sonnet, messages internes, 8,3 % après un changement silencieux depuis Opus ; « at most 0.4 % » ne vaut que pour Haiku (point 5).
2. l. 274 (6.3) : dire que la condition s ÷ q > 1/0,95 est remplie dans 24 cellules jugées (point 4).
3. `controle_fr.md` : ajouter la robustesse à enjeu fort (l. 31), la phrase de conclusion (l. 43), « lecture secondaire » et « 85 à 100 % » (l. 26) (point 10).
4. l. 372 (limite 21) : palier 3 aussi atteint, rarement, en WorkBench et en banque (R3).
5. l. 340 : « Mainly volume, and in part the mix » à adoucir (R4).
6. l. 310 : référents de « It » et « They » (point 5).
7. `FORMULATION_VERDICT.md` l. 30 et `resultats/tables.md` l. 134 : 0,6905 au lieu de ln 2 = 0,693 (point 9).
8. l. 234 : citer 13 623 en 6.1 ; inscrire les chiffres nouveaux au registre (R7, R8).
