# Chiffrage des options de R4 sur les tirages du 4e passage (Claude, 06/11/2026)

## Méthode
- Données : `simulation/controle3/resultats_v4/delegabilite.jsonl` (44 400 tirages : mécanismes bêta, logit-normal, ρ hétérogène ; témoins tenus ou en défaut ; ρ vrai 0 à 1 ; multiples 0 à 10 de la barre ; 300 tirages par case). Aucune donnée d'agent.
- Pour chaque type faible d'un tirage, le moteur écrit : erreurs x, écritures n, borne haute à 95 % à ρ = 1 (rapportée à la barre), ρ̂. On reconstruit n_eff à ρ = 1 depuis la borne, puis m̄ = n / n_eff(ρ=1), puis n_eff(ρ̂) = n / (1 + (m̄ − 1) ρ̂).
- **Contrôle** : la liste des types « estimés sous la barre » recalculée (taux médian Clopper-Pearson à 50 % sur n_eff(ρ̂)) égale celle du moteur dans les **44 400 tirages sur 44 400**.
- **Limite** : les bornes basses sont approchées. Dans 53 899 cas, n_eff à ρ = 1 vient d'une grille faute de changement de signe (bornes arrondies à 4 décimales). Tout chiffre ci-dessous est exploratoire : à confirmer par un passage du moteur si une option est retenue.
- Script : `scratchpad/options_r4.py` (session du 06/11), sortie `scratchpad/options_r4.json`.

## Options chiffrées
- **A, règle actuelle** : R4 si aucune configuration n'est délégable (aucun type au taux médian ≤ barre) et qu'au moins un type est jugeable (n_eff(ρ̂) × barre ≥ ln 2).
- **B1, un établi (global)** : A, et au moins un type jugeable « établi au-dessus » (borne basse unilatérale à 95 % > barre, à ρ = 1).
- **C, par configuration** : A, et **chaque configuration** qui a un type jugeable a au moins un type établi au-dessus de sa barre (borne basse unilatérale à 95 % > barre), à ρ̂ (C-ρ̂) ou à ρ = 1 (C-ρ1). Sinon : « preuves insuffisantes ».
- **D, tous établis** : A, et **tous** les types jugeables établis au-dessus.

## Résultats (part des tirages qui donnent R4 ; bêta sauf mention)

Témoins tenus (tous les types au même multiple de leur barre) :

| ρ vrai | multiple | A | B1 | C-ρ̂ | C-ρ1 |
|---|---|---|---|---|---|
| 0 | 0,5 | 0,7 % | 0 % | 0 % | 0 % |
| 0 | 1 | 32 % | 1,7 % | 0 % | 0 % |
| 0 | 2 | 85 % | 37 % | 0,3 % | 0 % |
| 0 | 5 | 100 % | 100 % | 62 % | 24 % |
| 0,3 | 0,5 | 5 % | 0 % | 0 % | 0 % |
| 0,3 | 5 | 100 % | 100 % | 58 % | 44 % |
| 0,7 | 0,2 | 11 % | 0 % | 0 % | 0 % |
| 0,7 | 0,5 | 25 % | 0,3 % | 0 % | 0 % |
| 0,7 | 1 | 48 % | 3,7 % | 0,3 % | 0,3 % |
| 0,7 | 5 | 99 % | 96 % | 79 % | 78 % |
| 0,9 | 0,2 | 17 % | 0 % | 0 % | 0 % |
| 0,9 | 0,5 | 39 % | 0 % | 0 % | 0 % |
| 0,9 | 1 | 63 % | 3,0 % | 1,7 % | 1,0 % |
| 0,9 | 5 | 100 % | 92 % | 82 % | 82 % |
| 1 | 0,2 | 24 % | 0 % | 0 % | 0 % |
| 1 | 0,5 | 50 % | 0 % | 0 % | 0 % |
| 1 | 1 | 80 % | 3,7 % | 3,3 % | 3,3 % |
| 1 | 5 | 100 % | 83 % | 81 % | 81 % |
| 1 | 10 | 100 % | 100 % | 100 % | 100 % |

Témoins en défaut (un type faible de Sonnet et Opus à 10 × sa barre dans WorkBench) :

| ρ vrai | multiple | A | B1 | C-ρ̂ | C-ρ1 |
|---|---|---|---|---|---|
| 0 | 1 | 63 % | 63 % | 0,3 % | 0 % |
| 0 | 5 | 100 % | 100 % | 84 % | 31 % |
| 0,7 | 0,2 | 16 % | 16 % | 0 % | 0 % |
| 0,9 | 0,5 | 43 % | 43 % | 0 % | 0 % |
| 1 | 0,2 | 24 % | 24 % | 0 % | 0 % |
| 1 | 1 | 76 % | 76 % | 1,3 % | 1,3 % |
| 1 | 5 | 100 % | 100 % | 86 % | 86 % |

Autres mécanismes : avec C, 0 % de R4 à 0,5 fois la barre (logit-normal et ρ hétérogène) ; à la barre, 0 à 2,3 % ; à 5 fois, logit-normal 54 à 76 % (C-ρ1) et 61 à 76 % (C-ρ̂).

D (tous établis), témoins tenus, ρ = 0 : 13 % (ρ1) et 56 % (ρ̂) à 5 fois la barre ; 85 à 100 % à 10 fois.

## Lecture
1. **A** donne R4 à des agents fiables : 11 à 24 % à 0,2 fois la barre dès ρ ≥ 0,7, et 25 à 53 % à 0,5 fois.
2. **B1** corrige quand tous les agents se ressemblent, mais rien quand un autre modèle est mauvais. Dès qu'une seule configuration est établie au-dessus, B1 redonne A, alors que Haiku reste fiable.
3. **C** supprime les R4 à tort pour des agents fiables : 0 % à 0,2 et 0,5 fois la barre, quels que soient ρ, les témoins et le mécanisme. À la barre, au plus 3,3 %, sous les 5 % nominaux, même à ρ = 1. Ce qui reste devient « preuves insuffisantes ».
4. **Prix de C : la puissance pour des agents mauvais.** À 5 fois la barre, R4 sort 58 à 93 % du temps avec ρ̂, mais seulement 24 à 44 % avec ρ = 1 quand ρ vrai ≤ 0,3. Les petites configurations (Sonnet et Opus : 1 partie par tâche dans WorkBench, 10 en commerce) n'établissent pas souvent un dépassement à ρ = 1. C'est l'effet produit d'un test intersection-union (toutes les configurations doivent passer).
5. **D** est trop exigeant (13 à 56 % à 5 fois, ρ = 0).
6. ρ̂ ou ρ = 1 pour « établi au-dessus » : avec ρ̂, le faux R4 à la barre reste ≤ 3,3 % dans toutes les cases mesurées (ρ̂ est juste depuis N3). ρ = 1 est la lecture prudente, cohérente avec « prouver à ρ = 1 », mais elle coûte de la puissance quand les erreurs sont indépendantes.
