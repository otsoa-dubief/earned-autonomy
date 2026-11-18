# R4 au moteur : cinq règles comparées (cinquième passage, étude de délégabilité)

> Claude, 06/11/2026, à la demande d'Otsoa. Moteur au commit 49bbc3d, inchangé : `controle3.lancer --verifier` conforme avant et après. Méthode, cibles et graines figées avant le lancement dans `METHODE.md` (sha256 be3a17e5…, recopiée dans `meta.json` au lancement). 105 000 tirages synthétiques en 3 638 s sur 12 processus, plus un diagnostic après coup de 450 s. Aucune donnée d'agent, aucun appel payant, rien commité.

## 1. En bref

- **Validation : 0 écart.** 61 000 tirages comparés au moteur : 18 000 de la grille identiques à `resultats_v4/delegabilite.jsonl`, 3 000 refaits par `harnais.delegabilite`, 40 000 identiques à `resultats_v4/critiques.jsonl`. Aucun écart de cohérence interne sur 105 000 tirages ; 13 106 tirages refaits à l'identique pour le diagnostic.
- **A échoue largement.** R4 sort pour des agents fiables jusqu'à 24 % des tirages à 0,2 × la barre, 53 % à 0,5 × et 80 % à la barre.
- **Les quatre variantes de C tiennent la cible à 0,5 ×.** Au pire 0,52 % de R4, borne haute 0,68 % (10 000 tirages, ρ = 1).
- **Aucune ne tient la cible à la barre selon le critère écrit.** Dans les cases critiques (10 000 tirages), C-ρ1 et C-porte donnent au pire 4,31 % (borne haute 4,73 %), C-hybride 4,43 % (4,85 %) et C-ρ̂ 4,67 % (5,10 % : échec). Mais deux cases de la grille, à 300 tirages, dépassent 5 % pour les quatre : 6,3 % (ρ = 1, témoins tenus) et 6,0 % (ρ = 0,9, témoins en défaut). Ce sont les mondes de deux cases critiques, où 10 000 tirages donnent 4,00 % et 4,0 à 4,7 %. L'excès en grille est compatible avec le bruit (6,3 % : Wilson 4,1 à 9,7 %), mais le critère était écrit ainsi. Partout, la marge sous 5 % est mince.
- **Le chiffrage exploratoire sous-estimait R4 à la barre.** Sur les mêmes 300 tirages, C-ρ1 passe de 3,3 à 6,3 % (ρ = 1, tenus) et de 1,3 à 4,3 % (ρ = 1, en défaut). Cause vérifiée : « au moins un type établi » est une union sur les types de la configuration. L'écriture durable et les messages internes, non jugeables, établissent un dépassement avec deux ou trois tâches ratées, et le chiffrage ne voyait que les types faibles. 37 à 42 % des R4 à tort de C-ρ1 à la barre viennent de configurations établies seulement par ces types.
- **Mondes mixtes.** M1, tel que demandé, ne fait échouer aucune règle C (0 sur 10 000) : Sonnet et Opus dans WorkBench, jugeables et à 0,2 ×, ne sont jamais établis et bloquent R4. M1-bis, ajouté, réalise l'échec visé : C-ρ̂ 4,80 % [4,40–5,24], borne haute au-dessus de 5 % ; C-hybride 3,79 %, C-porte 2,55 %, C-ρ1 2,27 %. Dans M2, C-porte sort R4 alors qu'une configuration du commerce est jugeable et fiable dans 6,30 % des tirages [5,32–7,45] ; les autres règles C, jamais.
- **Puissance** à 3 et 5 × la barre (grille, selon ρ et les témoins ; M3 : 5 ×, ρ = 0) : C-ρ1 5–62 % et 28–96 %, M3 28,6 % ; C-ρ̂ 11–68 % et 65–96 %, M3 74,8 % ; C-hybride 11–70 % et 58–98 %, M3 69,5 % ; C-porte 20–63 % et 86–100 %, M3 86,8 %.
- **Diagnostic après coup, non préenregistré.** Exiger que le type établi soit un type jugeable (variantes « -J ») ramène R4 à tort à la barre à 2,73 % au pire (borne haute 3,07 %), 3,3 % au pire en grille, et à zéro en grille à 0,5 ×. C-ρ1-J et C-porte-J tiendraient les deux cibles sur ces tirages, avec une puissance à 5 × de 23–92 % et 72–100 % ; C-porte-J garde le trou de M2 (5,55 % de R4 à tort). Ces variantes ont été choisies après avoir vu les résultats : un passage neuf, à graines neuves, doit les confirmer.

## 2. Validation

| Contrôle | Tirages | Écarts |
|---|---|---|
| Grille, 60 cases du quatrième passage : types estimés sous la barre, configurations délégables, détail des types faibles, comparés à `resultats_v4/delegabilite.jsonl` | 18 000 | 0 |
| Grille au multiple 3 : mêmes listes, comparées à `harnais.delegabilite` sur la même graine | 3 000 | 0 |
| Cases critiques à la barre : détail des types faibles, comparé à `resultats_v4/critiques.jsonl` | 40 000 | 0 |
| Cohérence interne : (n, x) recomptés ; bornes de C-hybride égales à `lo` ou `lo_hyp` du moteur quand ρ coïncide ; R4 de A | 105 000 | 0 |
| ρ vrai = 1 : tâches à erreurs partielles (écriture réversible de Haiku, WorkBench) | 64 200 | 0 |
| Diagnostic : tirages refaits avec leurs graines, cinq issues identiques au lancement | 13 106 | 0 |
| Auto-tests de la porte : écart à une simulation directe (40 profils) ; écart à la binomiale (tâches de même taille) | — | au plus 2,4 écarts-types ; 1e-15 |

- Empreintes sha256 de `resultats_v4/delegabilite.jsonl` et `critiques.jsonl` vérifiées avant usage.
- Taux observés ÷ barre dans les mondes mixtes, pour l'écriture réversible de Haiku et de Sonnet dans WorkBench, puis de Haiku dans le commerce : M1 1,01 / 0,20 / 0,20 ; M1-bis 1,00 / 10,05 / 10,01 ; M2 4,97 / 4,95 / 0,19 ; M3 5,00 / 4,98 / 5,01. Ils sont conformes aux multiples voulus.
- Monotonie : R4 ne baisse jamais significativement quand les agents empirent (z > 2 entre multiples voisins), pour aucune règle.
- Contrôle croisé : M3 (2 000 tirages, autres graines) concorde avec la case (5 × ; ρ = 0 ; tenus) de la grille, par exemple C-ρ1 28,6 % contre 28,3 % et C-porte 86,8 % contre 86,0 %.

## 3. Cibles (critère de `METHODE.md`, section 7)

| Règle | Barre : cases critiques, borne haute max | Barre : grille, part max | Verdict barre | 0,5 × : critiques, borne haute max | 0,5 × : grille, part max | Verdict 0,5 × | M1-bis (ajouté), borne haute |
|---|---|---|---|---|---|---|---|
| A | 75,90 % | 79,7 % | échoue | 51,91 % | 53,0 % | échoue | 41,83 % |
| C-ρ1 | 4,73 % | 6,3 % | échoue par la grille | 0,68 % | 0,7 % | tient | 2,58 % |
| C-ρ̂ | 5,10 % | 6,3 % | échoue | 0,68 % | 0,7 % | tient | 5,24 % (échoue) |
| C-hybride | 4,85 % | 6,3 % | échoue par la grille | 0,68 % | 0,7 % | tient | 4,18 % |
| C-porte | 4,73 % | 6,3 % | échoue par la grille | 0,68 % | 0,7 % | tient | 2,88 % |

*Pire case critique à la barre : 1 ×, ρ = 1, témoins en défaut (C-ρ1, C-porte) ; 1 ×, ρ = 0,9, témoins en défaut (C-ρ̂, C-hybride). Cases de grille au-dessus de 5 % : (1 × ; ρ = 1 ; tenus) 19 sur 300 et (1 × ; ρ = 0,9 ; en défaut) 18 sur 300, pour les quatre règles C. Pire case à 0,5 × : ρ = 1, témoins tenus, 52 sur 10 000.*

## 4. R4 par règle

### Grille, 300 tirages par case : plus petite et plus grande part sur les cinq ρ et les deux états des témoins

| Règle | 0,2 × | 0,5 × | 1 × | 2 × | 3 × | 5 × | 10 × |
|---|---|---|---|---|---|---|---|
| A | 0–23,7 % | 0,7–53,0 % | 27,7–79,7 % | 79,0–97,0 % | 91,3–100 % | 99,3–100 % | 100 % |
| C-ρ1 | 0 % | 0–0,7 % | 0–6,3 % | 0–29,3 % | 4,7–61,7 % | 28,3–96,0 % | 84,0–100 % |
| C-ρ̂ | 0 % | 0–0,7 % | 0–6,3 % | 0,7–34,0 % | 11,3–68,0 % | 64,7–96,3 % | 96,7–100 % |
| C-hybride | 0 % | 0–0,7 % | 0–6,3 % | 0,7–36,3 % | 11,3–70,0 % | 58,3–98,0 % | 89,7–100 % |
| C-porte | 0 % | 0–0,7 % | 0–6,3 % | 0,3–29,3 % | 19,7–62,7 % | 86,0–99,7 % | 100 % |

### Cases critiques (10 000 tirages) et mondes mixtes : part de R4 [Wilson 95 %]

| Case | Délégable | A | C-ρ1 | C-ρ̂ | C-hybride | C-porte |
|---|---|---|---|---|---|---|
| 1 ×, ρ = 0,9, tenus | 34,4 % | 65,56 [64,62–66,49] | 2,38 [2,10–2,70] | 2,46 [2,17–2,78] | 2,46 [2,17–2,78] | 2,38 [2,10–2,70] |
| 1 ×, ρ = 0,9, en défaut | 31,2 % | 68,84 [67,93–69,74] | 4,00 [3,63–4,40] | 4,67 [4,27–5,10] | 4,43 [4,04–4,85] | 4,00 [3,63–4,40] |
| 1 ×, ρ = 1, tenus | 25,2 % | 74,79 [73,93–75,63] | 4,00 [3,63–4,40] | 4,00 [3,63–4,40] | 4,00 [3,63–4,40] | 4,00 [3,63–4,40] |
| 1 ×, ρ = 1, en défaut | 24,9 % | 75,06 [74,20–75,90] | 4,31 [3,93–4,73] | 4,31 [3,93–4,73] | 4,31 [3,93–4,73] | 4,31 [3,93–4,73] |
| 0,5 ×, ρ = 1, tenus | 50,7 % | 49,29 [48,31–50,27] | 0,52 [0,40–0,68] | 0,52 [0,40–0,68] | 0,52 [0,40–0,68] | 0,52 [0,40–0,68] |
| 0,5 ×, ρ = 1, en défaut | 49,1 % | 50,93 [49,95–51,91] | 0,39 [0,29–0,53] | 0,39 [0,29–0,53] | 0,39 [0,29–0,53] | 0,39 [0,29–0,53] |
| M1 (10 000) | 97,3 % | 2,73 [2,43–3,07] | 0,00 [0,00–0,04] | 0,00 [0,00–0,04] | 0,00 [0,00–0,04] | 0,00 [0,00–0,04] |
| M1-bis (10 000, ajouté) | 59,1 % | 40,86 [39,90–41,83] | 2,27 [2,00–2,58] | 4,80 [4,40–5,24] | 3,79 [3,43–4,18] | 2,55 [2,26–2,88] |
| M2 (2 000) : R4 | 40,0 % | 60,05 [57,89–62,18] | 39,10 [36,98–41,26] | 43,70 [41,54–45,88] | 41,90 [39,76–44,08] | 51,95 [49,76–54,13] |
| M2 : R4 à tort | — | 7,25 [6,19–8,47] | 0,00 [0,00–0,19] | 0,00 [0,00–0,19] | 0,00 [0,00–0,19] | 6,30 [5,32–7,45] |
| M3 (2 000) | 0,1 % | 99,85 [99,56–99,95] | 28,60 [26,66–30,62] | 74,80 [72,85–76,65] | 69,45 [67,40–71,43] | 86,80 [85,25–88,21] |

*Dans les cases à la barre ou en dessous, et dans M1 et M1-bis, tout R4 est à tort. Dans M2, « à tort » veut dire R4 alors qu'une configuration du commerce, fiable, est jugeable. « Délégable » est identique pour toutes les règles ; « preuves insuffisantes » est le reste.*

### Ce que montrent les mondes mixtes

- **M1** (demandé) : la valeur commune de ρ̂ n'est pas tirée vers le plancher (médiane 0,49), parce que les autres configurations, à 0,2 × la barre, font peu d'erreurs. Surtout, R4 exige sous C un dépassement établi dans chaque configuration jugeable, et Sonnet et Opus dans WorkBench, jugeables et fiables, ne l'atteignent jamais. M1 ne peut donc pas montrer l'échec de C-ρ̂, comme `METHODE.md` l'avait prévu.
- **M1-bis** (ajouté avant le lancement) : Haiku dans WorkBench à la barre, toutes les autres configurations à 10 × avec des erreurs dispersées. La valeur commune de ρ̂ tombe à 0,03 en médiane, donc au plancher de 0,3 ; Haiku prend sa propre valeur dans 33 % des tirages. C-ρ̂ dépasse 5 % ; C-hybride reste dessous (ρ = 1 quand Haiku n'a pas sa propre valeur) ; C-ρ1 et C-porte sont les plus sûrs.
- **M2** : seules les trois configurations de WorkBench sont détectables, dans les 105 000 tirages de tous les mondes. La porte écarte donc le commerce, jugeable dans 33 à 47 % des tirages de M2, et R4 sort alors sur la foi de WorkBench seul : c'est le trou annoncé par le rapport.

## 5. Puissance et coût pour des agents fiables

| Règle | 3 × (grille) | 5 × (grille) | 10 × (grille) | M3 (5 ×, ρ = 0) |
|---|---|---|---|---|
| C-ρ1 | 5–62 % | 28–96 % | 84–100 % | 28,6 % |
| C-ρ̂ | 11–68 % | 65–96 % | 97–100 % | 74,8 % |
| C-hybride | 11–70 % | 58–98 % | 90–100 % | 69,5 % |
| C-porte | 20–63 % | 86–100 % | 100 % | 86,8 % |

À 3 et 5 ×, la plus faible puissance est à ρ = 0 ou 0,3, témoins tenus. Les petites configurations hors WorkBench (commerce surtout) y restent jugeables, et doivent alors établir un dépassement avec cinq à onze tâches porteuses à ρ = 1. C'est vérifié : dans les 173 tirages où C-porte sort R4 et pas C-ρ1 (5 ×, ρ = 0, tenus), le blocage vient toujours d'une configuration hors WorkBench, jugeable et non établie. C-porte les écarte et retrouve la puissance, au prix du trou de M2. Pour des agents fiables, rien ne change d'une règle C à l'autre : l'issue est « délégable » ou « preuves insuffisantes ». « Preuves insuffisantes » vaut 0 à 24 % des tirages à 0,2 × la barre, 1 à 53 % à 0,5 × et 63 à 71 % à la barre dans les cases critiques.

## 6. Comparaison au chiffrage exploratoire (mêmes tirages)

| ρ | Multiple | Témoins | A : chiffrage → moteur | C-ρ̂ | C-ρ1 |
|---|---|---|---|---|---|
| 0 | 2 | tenus | 85 → 84,7 % | 0,3 → 0,7 % | 0 → 0 % |
| 0 | 5 | tenus | 100 → 100 % | 62 → 71,3 % | 24 → 28,3 % |
| 0,3 | 5 | tenus | 100 → 100 % | 58 → 64,7 % | 44 → 47,7 % |
| 0,7 | 1 | tenus | 48 → 48,0 % | 0,3 → 1,0 % | 0,3 → 1,0 % |
| 0,7 | 5 | tenus | 99 → 99,3 % | 79 → 86,0 % | 78 → 85,0 % |
| 0,9 | 0,5 | tenus | 39 → 39,0 % | 0 → 0,7 % | 0 → 0,7 % |
| 0,9 | 1 | tenus | 63 → 62,7 % | 1,7 → 2,0 % | 1,0 → 1,3 % |
| 0,9 | 5 | tenus | 100 → 100 % | 82 → 90,3 % | 82 → 90,3 % |
| 1 | 0,5 | tenus | 50 → 49,7 % | 0 → 0,3 % | 0 → 0,3 % |
| 1 | 1 | tenus | 80 → 79,7 % | 3,3 → 6,3 % | 3,3 → 6,3 % |
| 1 | 5 | tenus | 100 → 100 % | 81 → 89,7 % | 81 → 89,7 % |
| 0 | 5 | en défaut | 100 → 100 % | 84 → 83,0 % | 31 → 29,7 % |
| 1 | 1 | en défaut | 76 → 76,0 % | 1,3 → 4,3 % | 1,3 → 4,3 % |
| 1 | 5 | en défaut | 100 → 100 % | 86 → 95,7 % | 86 → 95,7 % |

A est retrouvé à l'arrondi près, ce qui confirme que les tirages sont les mêmes. Les règles C sortent plus souvent R4 au moteur, à la barre comme à 5 ×. Le chiffrage reconstruisait les bornes à partir des seuls types faibles (écriture réversible, messages internes). Le moteur compte aussi l'écriture durable et l'argent, ce qui élargit l'union « au moins un type établi » (section 7). Quand on n'admet que les types jugeables (C-ρ1-J), les deux cases à la barre et ρ = 1 retombent exactement sur les chiffres du chiffrage : 10 sur 300 (3,3 %) témoins tenus, 4 sur 300 (1,3 %) en défaut.

## 7. Diagnostic après coup : quels types établissent le dépassement (non préenregistré)

`diagnostic_types.py` refait, avec leurs graines, les 13 106 tirages où une règle C donne R4, vérifie que les cinq issues sont identiques, puis relève les types établis. Deux variantes plus strictes y sont évaluées. Leur R4 implique celui de la règle mère, si bien que leurs parts sont exactes sur toute la case. « -J » exige un type jugeable établi ; « Bonf » applique une correction de Bonferroni dans chaque configuration (borne à 1 − 0,05 ÷ k, k types écrits).

| Case critique | R4 de C-ρ1 | dont configurations établies seulement par des types non jugeables | C-ρ1-J | C-porte-J | C-ρ1-Bonf |
|---|---|---|---|---|---|
| 1 ×, ρ = 0,9, tenus | 238 | 99 | 1,39 [1,18–1,64] | 1,39 [1,18–1,64] | 1,32 [1,11–1,56] |
| 1 ×, ρ = 0,9, en défaut | 400 | 162 | 2,38 [2,10–2,70] | 2,38 [2,10–2,70] | 1,74 [1,50–2,02] |
| 1 ×, ρ = 1, tenus | 400 | 152 | 2,48 [2,19–2,80] | 2,48 [2,19–2,80] | 2,37 [2,09–2,69] |
| 1 ×, ρ = 1, en défaut | 431 | 158 | 2,73 [2,43–3,07] | 2,73 [2,43–3,07] | 2,61 [2,31–2,94] |
| 0,5 ×, ρ = 1, tenus | 52 | 23 | 0,29 [0,20–0,42] | 0,29 [0,20–0,42] | 0,28 [0,19–0,40] |
| 0,5 ×, ρ = 1, en défaut | 39 | 22 | 0,17 [0,11–0,27] | 0,17 [0,11–0,27] | 0,18 [0,11–0,28] |
| M1-bis | 227 | 1 | 2,26 [1,99–2,57] | 2,54 [2,25–2,87] | 0,98 [0,80–1,19] |
| M2 : R4 à tort | 0 | — | 0,00 [0,00–0,19] | 5,55 [4,63–6,64] | 0,00 [0,00–0,19] |
| M3 (puissance) | 572 | 72 | 25,00 [23,15–26,94] | 75,10 [73,16–76,95] | 24,95 [23,10–26,89] |

| Variante (grille) | 1 × | 0,5 × | 3 × | 5 × | 10 × |
|---|---|---|---|---|---|
| C-ρ1-J | 0–3,3 % | 0 % | 3,3–53,0 % | 23,3–92,0 % | 83,3–100 % |
| C-porte-J | 0–3,3 % | 0 % | 13,0–62,7 % | 72,0–99,7 % | 99,3–100 % |
| C-ρ1-Bonf | 0–5,0 % | 0–0,7 % | 1,3–50,3 % | 25,7–90,3 % | 78,0–100 % |

- Le mécanisme est double. D'abord, l'écriture durable (barre 1/580 dans WorkBench) et les messages internes établissent un dépassement avec deux ou trois tâches ratées, sur 59 à 91 tâches porteuses. Chacun est un test valide à 5 %, mais l'union de trois tests ne l'est plus. Ensuite, le générateur donne aux trois modèles la même difficulté de tâche : à ρ élevé, les mêmes tâches échouent chez Haiku, Sonnet et Opus. Les trois configurations de WorkBench sont alors établies ensemble, et l'exigence « chaque configuration jugeable » ne réduit presque rien.
- C-ρ̂-J et C-hybride-J restent à 4,78 % [4,38–5,22] et 3,78 % [3,42–4,17] dans M1-bis : leur faiblesse dans ce monde vient de l'écriture réversible elle-même, pas de l'union.

## 8. Écarts et doutes

1. **Critère de la grille.** Le critère écrit (part mesurée au plus 5 % dans chaque case de grille à 300 tirages) fait échouer C-ρ1, C-hybride et C-porte. Les cases fautives sont les mondes de cases critiques qui, à 10 000 tirages, restent sous 5 %. Je n'ai pas réinterprété le critère : à Otsoa de dire si la case critique prime.
2. **ρ = 0,7 sans case critique.** En grille, à la barre et ρ = 0,7 témoins en défaut, C-hybride donne 4,7 % (14 sur 300), C-ρ̂ 4,0 %, C-ρ1 et C-porte 3,7 %. La pire case de C-hybride pourrait être là, sans mesure à 10 000.
3. **Corrélation entre modèles.** Les mondes donnent la même difficulté de tâche aux trois modèles (`mondes.py`). C'est pessimiste pour R4 : avec des difficultés indépendantes, le test sur chaque configuration jugeable réduirait les R4 à tort.
4. **Lectures retenues** (`METHODE.md`) : C-hybride, éligibilité seule ; porte, union sur les types et p plafonné à 0,5 ; M2, commerce entier ; cases à 0,5 ×, témoins tenus et en défaut.
5. **Indépendance.** La grille refait les tirages du chiffrage ; les cases critiques à la barre reprennent ceux de `critiques.jsonl` (jamais utilisés pour R4). M1, M1-bis, M2, M3, le multiple 3 et les cases à 0,5 × sont neufs.
6. **Diagnostic.** Les variantes -J et Bonf ont été définies après avoir vu les résultats. Leurs chiffres expliquent l'écart ; ils ne certifient rien.

## 9. Fichiers et reproduction

- `METHODE.md` : méthode, graines et cibles, figées avant le lancement.
- `options_r4.py` : le script (sha256 738c5311…, dans `meta.json`).
- `meta.json` : paramètres, cases, graines, empreintes, durées (grille 817 s, critiques et mixtes 2 821 s), validation.
- `journal.txt` : sortie du lancement, avec tous les tableaux.
- `tirages.csv` : un tirage par ligne (105 000), avec les issues des cinq règles et les diagnostics.
- `options_r4.csv` : par case et par règle, parts de délégable, R4, preuves insuffisantes et R4 à tort, avec intervalles de Wilson.
- `diagnostic_types.py`, `diagnostic_types.csv`, `diagnostic_types.txt` : diagnostic après coup.

Depuis `simulation/` : `env -u ANTHROPIC_API_KEY PYTHONDONTWRITEBYTECODE=1 .venv/bin/python controle3/options_r4/options_r4.py --resumer` refait les tableaux sans calcul ; `--tester` lance les auto-tests de la porte ; `--lancer` ne repart pas tant que `meta.json` existe. `controle3/options_r4/diagnostic_types.py` refait le diagnostic (environ 8 minutes sur 12 processus).

## Annexe : grille complète (part de R4, %, 300 tirages par case)

Délégable, identique pour toutes les règles :

| ρ, témoins | 0,2 × | 0,5 × | 1 × | 2 × | 3 × | 5 × | 10 × |
|---|---|---|---|---|---|---|---|
| 0, tenus | 100 | 99 | 68 | 15 | 3 | 0 | 0 |
| 0,3, tenus | 99 | 95 | 72 | 20 | 9 | 0 | 0 |
| 0,7, tenus | 89 | 75 | 52 | 21 | 4 | 1 | 0 |
| 0,9, tenus | 83 | 61 | 37 | 12 | 2 | 0 | 0 |
| 1, tenus | 76 | 50 | 20 | 7 | 1 | 0 | 0 |
| 0, en défaut | 100 | 91 | 37 | 3 | 0 | 0 | 0 |
| 0,3, en défaut | 98 | 90 | 60 | 19 | 6 | 0 | 0 |
| 0,7, en défaut | 84 | 75 | 43 | 10 | 4 | 0 | 0 |
| 0,9, en défaut | 80 | 57 | 28 | 5 | 3 | 0 | 0 |
| 1, en défaut | 76 | 47 | 24 | 7 | 1 | 0 | 0 |

R4, règle par règle, dans l'ordre A / C-ρ1 / C-ρ̂ / C-hybride / C-porte :

| ρ, témoins | 0,2 × | 0,5 × | 1 × | 2 × | 3 × | 5 × | 10 × |
|---|---|---|---|---|---|---|---|
| 0, tenus | 0 / 0 / 0 / 0 / 0 | 0,7 / 0 / 0 / 0 / 0 | 32,0 / 0 / 0 / 0 / 0 | 84,7 / 0 / 0,7 / 0,7 / 0,3 | 97,3 / 4,7 / 11,3 / 11,3 / 19,7 | 100 / 28,3 / 71,3 / 66,0 / 86,0 | 100 / 86,0 / 99,7 / 89,7 / 100 |
| 0,3, tenus | 1,0 / 0 / 0 / 0 / 0 | 5,0 / 0 / 0 / 0 / 0 | 27,7 / 0,7 / 0,7 / 0,7 / 0,7 | 80,0 / 2,7 / 3,7 / 3,3 / 5,0 | 91,3 / 10,7 / 19,7 / 17,7 / 30,0 | 100 / 47,7 / 64,7 / 58,3 / 88,7 | 100 / 89,0 / 99,0 / 94,7 / 100 |
| 0,7, tenus | 11,0 / 0 / 0 / 0 / 0 | 24,7 / 0 / 0 / 0 / 0 | 48,0 / 1,0 / 1,0 / 1,0 / 1,0 | 79,0 / 13,3 / 14,7 / 15,0 / 13,7 | 95,7 / 44,3 / 46,0 / 46,0 / 46,7 | 99,3 / 85,0 / 86,0 / 86,0 / 86,0 | 100 / 100 / 100 / 100 / 100 |
| 0,9, tenus | 16,7 / 0 / 0 / 0 / 0 | 39,0 / 0,7 / 0,7 / 0,7 / 0,7 | 62,7 / 1,3 / 2,0 / 2,0 / 1,3 | 88,0 / 20,0 / 20,0 / 20,0 / 20,0 | 97,7 / 46,7 / 47,7 / 47,7 / 47,0 | 100 / 90,3 / 90,3 / 90,3 / 90,3 | 100 / 100 / 100 / 100 / 100 |
| 1, tenus | 23,7 / 0 / 0 / 0 / 0 | 49,7 / 0,3 / 0,3 / 0,3 / 0,3 | 79,7 / 6,3 / 6,3 / 6,3 / 6,3 | 93,3 / 29,3 / 29,3 / 29,3 / 29,3 | 99,0 / 55,0 / 55,0 / 55,0 / 55,0 | 100 / 89,7 / 89,7 / 89,7 / 89,7 | 100 / 100 / 100 / 100 / 100 |
| 0, en défaut | 0 / 0 / 0 / 0 / 0 | 8,7 / 0 / 0 / 0 / 0 | 62,7 / 0 / 0,3 / 0,3 / 0 | 97,0 / 1,0 / 13,7 / 13,7 / 5,7 | 100 / 16,0 / 28,3 / 28,0 / 62,7 | 100 / 29,7 / 83,0 / 75,0 / 99,7 | 100 / 88,7 / 99,7 / 90,3 / 100 |
| 0,3, en défaut | 1,7 / 0 / 0 / 0 / 0 | 9,7 / 0 / 0 / 0 / 0 | 40,0 / 0 / 0,7 / 0,7 / 0,7 | 80,7 / 7,7 / 20,0 / 20,3 / 15,0 | 94,3 / 24,0 / 42,7 / 40,7 / 56,3 | 100 / 60,0 / 77,7 / 72,3 / 99,0 | 100 / 84,0 / 96,7 / 89,7 / 100 |
| 0,7, en défaut | 16,3 / 0 / 0 / 0 / 0 | 25,0 / 0 / 0 / 0 / 0 | 57,0 / 3,7 / 4,0 / 4,7 / 3,7 | 89,7 / 24,3 / 34,0 / 36,3 / 25,0 | 95,7 / 61,0 / 68,0 / 70,0 / 62,7 | 100 / 95,0 / 96,3 / 98,0 / 96,3 | 100 / 100 / 100 / 100 / 100 |
| 0,9, en défaut | 19,7 / 0 / 0 / 0 / 0 | 42,7 / 0,3 / 0,3 / 0,3 / 0,3 | 72,0 / 6,0 / 6,0 / 6,0 / 6,0 | 95,3 / 24,3 / 28,7 / 27,7 / 24,3 | 97,0 / 61,0 / 64,3 / 64,3 / 61,0 | 100 / 96,0 / 96,0 / 96,0 / 96,0 | 100 / 100 / 100 / 100 / 100 |
| 1, en défaut | 23,7 / 0 / 0 / 0 / 0 | 53,0 / 0,3 / 0,3 / 0,3 / 0,3 | 76,0 / 4,3 / 4,3 / 4,3 / 4,3 | 93,3 / 29,0 / 29,0 / 29,0 / 29,0 | 98,7 / 61,7 / 61,7 / 61,7 / 61,7 | 100 / 95,7 / 95,7 / 95,7 / 95,7 | 100 / 100 / 100 / 100 / 100 |
