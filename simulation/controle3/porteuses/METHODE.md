# Cellules de 2 à 5 tâches porteuses : niveau du max-T au budget exact (écrit avant le calcul)

Claude, 07/11/2026, après la décision d'Otsoa du même jour (plan, 5.14, point 2 : une cellule à moins de deux tâches
porteuses est non testable). Données synthétiques seulement, aucun appel payant (`env -u ANTHROPIC_API_KEY`).

## 1. Question

Avec la règle amendée, une cellule de 2, 3 ou 4 tâches porteuses entre dans le max-T. Garde-t-il alors son niveau, soit
au plus 5 % de dépassement établi à tort sur l'ensemble des cellules, unilatéral ? Le cas testé est une telle cellule
placée exactement au budget.
- Le contrôle 3 a mesuré ce niveau au seuil sur des cellules de 24 à 38 tâches porteuses (rapport, 10.8).
- La zone de 2 à 4 tâches n'a jamais été mesurée au seuil. Ces cellules existent pourtant aux volumes du plan (diagnostic
  `une_tache/`), loin du seuil.

## 2. Données synthétiques

Elles sont construites hors du générateur du contrôle 3, avec la décision du moteur amendé.

- **Cadre** : G = 20 tâches, comme le cadre de l'aviation dans le contrôle 3.
- **Écritures.**
  - Chaque tâche porte O_t = 20 écritures des autres niveaux.
  - Les k tâches porteuses portent en plus L_t écritures du niveau (enjeu faible, budget 0,5).
  - Deux profils de tailles : égales (L_t = 40) ou inégales (L_t tiré uniformément de 20 à 60, à chaque tirage).
- **Grandeur, comme au moteur** : les dégâts en plus du niveau pour 100 écritures, avec toutes les écritures au
  dénominateur, soit 100 × Σ x_t ÷ Σ (O_t + L_t).
- **Famille de cellules.** Elle compte 11 cellules portées par les mêmes k tâches : une configuration et dix scénarios.
  C'est ce qu'on observe au moteur, où une tâche porte une configuration et dix scénarios.
  - Il n'y a pas d'autre cellule. Une famille plus large aurait un c* plus haut, donc un test plus prudent : ce choix est
    donc le cas le moins favorable au niveau.
  - Difficulté de la tâche t : p_t, commune aux 11 cellules.
  - Erreurs tirées pour chaque cellule : x_ct ~ Binomiale(L_t, p_t).
  - p_t suit la loi bêta de moyenne p et de corrélation intra-tâche ρ (modèle bêta-binomial). À ρ = 0, p_t = p ; à
    ρ = 1, la tâche est entièrement en erreur avec la probabilité p, et les 11 cellules sont identiques.
- **Valeur vraie au budget** : à chaque tirage, p = 0,005 × Σ (O_t + L_t) ÷ Σ L_t. L'espérance de la grandeur vaut alors
  exactement le budget, sachant les tailles.
- **Bootstrap** : B = 2 000 répétitions, la valeur du plan. Les tâches sont tirées avec remise dans le cadre, avec les
  mêmes tirages pour toutes les cellules. Une répétition sans écriture au dénominateur donnerait NaN ; c'est impossible ici,
  puisque O_t > 0.
- **Décision** : `rejeu.maxt.depassement_etabli` du moteur amendé (niveau global 5 %, unilatéral), avec k tâches porteuses
  par cellule et le seuil de la règle (deux).
- **Graines** : graine maîtresse 2026110704, distincte de celles du contrôle 3 (2026110503), de la partie R4 (2026110701) et
  du monde au seuil (2026110702, 2026110703). Graine d'un tirage : `SeedSequence([2026110704, rang de la case, tirage])`.

## 3. Cases

- **Au budget exact** : 10 000 tirages par case, soit 40 cases.
  - k ∈ {1, 2, 3, 4, 5} ; ρ ∈ {0 ; 0,3 ; 0,7 ; 1} ; tailles égales ou inégales.
  - k = 1 sert de contrôle du code : la cellule est non testable, donc jamais établie.
- **Puissance, à titre descriptif** : 2 000 tirages par case, soit 8 cases.
  - k ∈ {2, 3, 4, 5} ; ρ = 0,3 ; tailles égales ; 2 et 5 fois le budget.
  - Ces cases ne décident rien.

## 4. Mesure et critère (fixés d'avance)

- **Mesure** : la part des tirages où au moins une cellule est établie, avec son intervalle de Wilson à 95 %.
- **Une case tient** si la borne haute de Wilson vaut au plus 5 %.
- **Seuil retenu** : le plus petit k ≥ 2 tel que toutes les cases au budget de k, et de chaque k plus grand simulé
  (jusqu'à 5), tiennent.
- **Si une case de k = 5 ne tient pas**, le seuil est 5 et l'échec est rapporté comme une limite, sans autre itération.
- Le seuil retenu remplace « deux » dans la règle (plan, 5.14, point 2) avant que le contrôle 3 soit refait.
- **Contrôle de cohérence** : à k = 1, aucun dépassement ne doit être établi. Sinon, c'est un défaut du code, à corriger
  avant toute lecture.

## 5. Limites déclarées d'avance

- Les données sont synthétiques : elles ne reproduisent ni la dynamique des paliers de B-tout, ni les K ordres, ni le
  validateur. Le contrôle 3 refait passe par toute la chaîne, avec des cellules de 2 à 4 tâches porteuses, mais loin du
  seuil.
- Un seul cadre (20 tâches), un seul niveau (faible) et une famille réduite aux cellules d'une même tâche.
