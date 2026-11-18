# Niveau du max-T de B-tout : choix d'une correction (écrit avant le calcul)

Claude, 07/11/2026, après la relecture indépendante C13 du code du verdict (constat M1, numéroté C1 dans le rapport
`revues/2026-11-07_C13_moteur_verdict.md`), et après sa vérification sur des tirages neufs : 18,5 % de faux
dépassements (37 sur 200) pour la famille du monde A sous l'hypothèse nulle complète, et 7,5 % avec T* recentré.
Données synthétiques seulement, aucun appel payant. **La correction est à trancher par Otsoa ; cette mesure la
prépare.**

## 1. Cause

- Le max-T centre T* sur la valeur centrale R0 : T*_bc = (estimation*_bc − estimation_c) ÷ écart type_c.
- Avec le tirage des tâches avec remise, une tâche tirée deux fois rejoue deux fois ses erreurs. Les dégâts en plus de
  B-tout croissent moins vite que le nombre d'erreurs, puisque chaque erreur coupe la série de réussites. Les
  répétitions bootstrap tombent donc en moyenne sous la valeur centrale : de 0,2 à 1,3 écart type.
- Résultat : la loi de T* est décalée vers le bas, c* sort trop petit et le max-T rejette trop souvent.
- Le principe du bootstrap demande que T* imite (estimation − vraie valeur). Dans le monde du bootstrap, la « vraie
  valeur » est la moyenne des répétitions, pas l'estimation de départ.

## 2. Corrections comparées

Dans les cinq formules, une cellule n'est testable que dans deux conditions : au moins deux tâches porteuses, et un
écart type utilisé défini et non nul (plan, 5.14, point 2).

| Formule | T* (répétition b, cellule c) | Borne basse | c* |
|---|---|---|---|
| F0 (actuelle) | (θ*_bc − θ̂_c) ÷ sd_c | θ̂_c − c* sd_c | 95e centile du maximum |
| F1 (recentrée) | (θ*_bc − θ̄*_c) ÷ sd_c | θ̂_c − c* sd_c | 95e centile, au moins 0 |
| F2 (bootstrap-t recentré) | (θ*_bc − θ̄*_c) ÷ se*_bc | θ̂_c − c* se_c | 95e centile, au moins 0 |
| F3 (recentrée, prudente) | comme F1 | comme F1 | 97,5e centile, au moins 0 |
| F4 (jackknife) | Z ~ normale multivariée de corrélation jackknife | θ̂_c − c* sd_jack,c | 95e centile du maximum de Z (20 000 tirages), au moins 0 |

Notations :
- θ̂_c : valeur centrale R0 ;
- θ*_bc, θ̄*_c : répétitions bootstrap et leur moyenne ;
- sd_c : écart type des répétitions ;
- se_c, se*_bc : écarts types linéarisés de la valeur centrale et de chaque répétition (`Quantite.se`, `se_boot`) ;
- sd_jack,c : écart type jackknife, une tâche retirée à la fois, non stratifié (donc un peu prudent).
- Corrélations jackknife : entre cellules d'un même environnement, qui ont les mêmes tâches retirées ; nulles d'un
  environnement à l'autre.

## 3. Régimes mesurés

Toutes les répétitions passent par le moteur (paliers, K ordres, validateur), avec les réglages du contrôle 3
(R0 = B = 200, K = 10, e = 5 %). Graine maîtresse 2026110705 ; graine d'une répétition :
`SeedSequence([2026110705, rang du régime, répétition])`.

**Hypothèse nulle complète** : chaque budget est posé au θ_G de sa cellule (moyenne des valeurs centrales sur les
répétitions du régime), donc toutes les cellules sont à leur frontière, le cas le moins favorable. C'est la définition
du monde B-seuil (rapport du contrôle 3, 10.6).

| Régime | Monde, budgets | Répétitions | Rôle |
|---|---|---|---|
| N1 | A (agents à 0,2 fois la barre), hypothèse nulle complète, famille entière | 200 | niveau |
| N2 | E-fort, hypothèse nulle complète, famille entière | 100 | niveau |
| P2 | B-seuil à la dérive 1,40 (au seuil exact), vrais budgets | 120 | niveau au vrai budget |
| P1 | B-seuil à la dérive 1,56 (Haiku à 1,05 fois le budget), vrais budgets | 60 | puissance |
| P3 | E-fort (commerce de 1,35 à 1,47 fois le budget), vrais budgets, mêmes répétitions que N2 | 100 | puissance |
| P4 | B (règle trop permissive), vrais budgets | 30 | puissance |

À titre descriptif, on donne aussi le niveau de chaque cellule seule (m = 1) dans N1 et N2, et sa pire cellule.

## 4. Mesures et règle de choix (fixées d'avance)

- **Mesure.** Pour chaque formule et chaque régime : la part des répétitions où au moins un dépassement est établi,
  avec son intervalle de Wilson.
- **Acceptable.** Une formule est acceptable si sa part observée vaut au plus 5 % dans N1, N2 et P2.
- **Choix.** Parmi les formules acceptables, la plus puissante en P1, puis en P3, puis en P4 ; à égalité, la plus
  simple, dans l'ordre F1, F3, F2, F4.
- **Aucune formule acceptable.** On retient celle dont la pire part observée en N1, N2 et P2 est la plus basse, et son
  niveau mesuré est déclaré avec R1.
- **Ce que la mesure ne décide pas.** Le choix est une recommandation pour Otsoa, qui tranche. La formule retenue
  s'applique aussi aux témoins (même max-T, plan, 5.14, point 2).
- **Ensuite.** Moteur et tests, puis contrôle 3, B-seuil et cellules à 2 à 5 tâches porteuses refaits avec la formule
  retenue.

## 5. Limites déclarées d'avance

- θ_G est estimé sur les répétitions mêmes du régime : erreur d'environ 7 % d'un écart type pour 200 répétitions.
- 100 à 200 répétitions par régime : l'intervalle de Wilson d'une part de 5 % va d'environ 2 à 10 %. La règle juge sur
  la part observée, et l'intervalle est publié.
- Le jackknife de F4 n'est pas stratifié, et il retire une tâche des K premiers ordres seulement, comme dans le
  moteur.
