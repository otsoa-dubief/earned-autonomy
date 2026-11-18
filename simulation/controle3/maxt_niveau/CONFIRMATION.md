# Niveau du max-T : mesure de confirmation dans N1 (écrite avant le calcul)

Claude, 08/11/2026, après la mesure préenregistrée (`METHODE.md`, résultats : commit 9d7f9d9) et sa relecture
indépendante. Données synthétiques seulement, aucun appel payant.

## 1. Pourquoi

- La règle de `METHODE.md` (section 4) a jugé sur les seuls tirages de la mesure. F1 y est pile à 5,0 % en N1 (10 sur
  200).
- Deux tirages antérieurs mesurent la même chose, dans les mêmes conditions : monde A, hypothèse nulle complète, T*
  recentré, sans plancher (le plancher ne joue dans aucune famille mesurée).
  - relecture C13 (`revues/2026-11-07_C13_moteur_verdict.md`, C1, preuve 4) : 15 sur 200 ;
  - vérification du coordinateur (`METHODE.md`, en tête) : 15 sur 200.
- En cumul, F1 est à 40 sur 600, soit 6,7 % (Wilson 4,9 à 9,0 %). F3 n'a été mesurée que sur les 200 tirages de la
  mesure (6 sur 200, soit 3,0 %).
- Cette mesure sert à publier, avec R1, le niveau de la formule retenue, avec plus de précision. Elle ne choisit pas
  la formule : ce choix revient à Otsoa, et la recommandation de Claude (F3) est écrite avant elle.

## 2. Tirages

- Régime N1 seul : monde A, hypothèse nulle complète. Chaque budget est posé au θ_G de sa cellule, moyenne des
  valeurs centrales sur les répétitions de cette mesure.
- 400 répétitions neuves, par la fonction `une` de `maxt_niveau.py`, sans rien changer au moteur ni aux réglages
  (R0 = B = 200, K = 10, e = 5 %).
- Graine d'une répétition : `SeedSequence([2026110705, 10, répétition])`. Le rang 10 n'a servi à aucun régime de la
  mesure (rangs 0 à 4) : ces tirages sont indépendants des précédents.
- Les cinq formules sont évaluées par `decisions` de `maxt_niveau.py`, telles que mesurées.

## 3. Ce qui est publié

- Pour chaque formule : la part des 400 répétitions où au moins un dépassement est établi, avec son intervalle de
  Wilson.
- La part cumulée, avec son intervalle de Wilson :
  - F1 : tirage de la mesure, les deux tirages antérieurs et celui-ci (1 000 répétitions) ;
  - F0 : de même, avec les deux tirages antérieurs du moteur d'origine (42 et 37 sur 200) ;
  - F2, F3 et F4 : tirage de la mesure et celui-ci (600 répétitions).

## 4. Lecture, fixée d'avance

- Le niveau publié avec R1 est la part cumulée de la formule retenue par Otsoa.
- Si la part cumulée de F3 dépasse 5 %, aucune formule mesurée n'est acceptable. F3 reste la moins mauvaise : sur
  les mêmes tirages, ses rejets sont un sous-ensemble de ceux de F1, et F0, F2 et F4 sont plus hautes dans la mesure.
  On applique alors la règle de `METHODE.md` pour ce cas : la moins mauvaise est retenue, et son niveau mesuré est
  déclaré avec R1.
- Aucune autre itération : la mesure n'est pas refaite.

## 5. Limites

- θ_G est estimé sur les 400 répétitions mêmes (erreur d'environ 5 % d'un écart type).
- Les tirages antérieurs ont été faits avec le moteur du 07/11 (tolérance √ε du float64, sans plancher). Le
  recoupement (`recoupement_moteur.txt`) montre que la tolérance ne change la testabilité d'aucune cellule, et le
  plancher ne joue dans aucune famille (`descriptif_apres_mesure.txt`, section 5).
- Le cumul suppose que les quatre tirages mesurent la même quantité. Ils diffèrent par la graine seulement.
