# Mesures du projet : courbes d'efficacité des règles de délégabilité candidates (06/11)

Source : simulation du coordinateur, `simulation/controle3/options_n1/oc_delegabilite.py` et `oc_delegabilite.csv`
(SHA-256 du CSV : f6a5e37b9b53bab43df8210356fd08985ffd023fcd0994b052c3c40ea54b88d6). Données synthétiques du
contrôle 3 (mêmes mondes que son étude de délégabilité : volumes prévus de l'expérience, 4 environnements × 3 modèles =
12 configurations, jusqu'à 9 types par configuration ; agents à `multiple` fois la barre sur tous les types ;
corrélation intra-tâche ρ ; « témoins en défaut » = Sonnet et Opus se trompent dans WorkBench). 150 répétitions par case
(incertitude d'environ ± 4 points sur une part de 50 %, ± 2 points près de 0 ou 1). Aucune règle n'est rejouée ; seule
la condition de délégabilité est mesurée.

## Règles comparées (un type « compte » si…)

- `est` (règle actuelle, Q14) : taux estimé x/n au plus la barre.
- `faible` : `est`, mais seulement sur les types à faible enjeu.
- `jeff` : médiane a posteriori de Jeffreys, Bêta(x_eff + ½, n_eff − x_eff + ½), au plus la barre.
- `ub50` : borne haute unilatérale de Clopper-Pearson à 50 % au plus la barre (à zéro erreur : 1 − 0,5^(1/n_eff) ≈ 0,69 ÷ n_eff ; porte implicite n_eff × barre ≥ ln 2 ≈ 0,69).
- `obs1`, `obs2`, `obs3` : `est` et n_eff × barre ≥ 1, 2 ou 3 (au moins c erreurs attendues à la barre).
- `ub80` : borne haute à 80 % au plus la barre.
- `prouve` : borne haute à 95 % au plus la barre (le « classement prouvé »).

Une configuration est délégable si au moins un de ses types compte. Deux estimations de ρ̂ : celle du moteur, et une
variante qui n'estime ρ̂ que sur les tâches d'au moins deux écritures (correction du « résidu de G1 » : les tâches d'une
seule écriture de Sonnet et Opus dans WorkBench faisaient monter ρ̂ de l'environnement).

## Part des répétitions avec au moins une configuration délégable (ρ̂ corrigé)

Fourchettes sur ρ ∈ {0 ; 0,3 ; 0,7} et témoins en défaut ou non.

| Agents à … la barre | est | faible | jeff | ub50 | obs1 | obs2 | obs3 | ub80 | prouve |
|---|---|---|---|---|---|---|---|---|---|
| 0 (parfaits) | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 | 0,37–0,93 | 1,00 | 0,41–0,96 |
| 0,1 | 1,00 | 1,00 | 1,00 | 0,97–1,00 | 0,99–1,00 | 0,95–1,00 | 0,37–0,88 | 0,84–0,99 | 0,22–0,61 |
| 0,3 | 1,00 | 1,00 | 1,00 | 0,91–1,00 | 0,93–1,00 | 0,80–1,00 | 0,36–0,87 | 0,59–0,70 | 0,06–0,33 |
| 0,5 | 1,00 | 1,00 | 1,00 | 0,86–0,97 | 0,86–1,00 | 0,72–0,96 | 0,40–0,85 | 0,34–0,49 | 0,03–0,19 |
| 1 | 1,00 | 1,00 | 1,00 | 0,43–0,77 | 0,61–0,97 | 0,40–0,60 | 0,25–0,48 | 0,02–0,23 | 0,00–0,05 |
| 2 | 1,00 | 0,96–0,99 | 0,94–1,00 | 0,01–0,36 | 0,12–0,55 | 0,01–0,17 | 0,01–0,09 | 0,00–0,05 | 0,00–0,01 |
| 5 | 1,00 | 0,36–0,81 | 0,34–0,77 | 0,00–0,07 | 0,00–0,05 | 0,00 | 0,00 | 0,00 | 0,00 |
| 10 | 1,00 | 0,03–0,36 | 0,03–0,31 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |

Avec le ρ̂ du moteur (sans la correction), quand les témoins sont en défaut : `obs2` ne rend délégables des agents
parfaits que dans 31 à 38 % des répétitions (au lieu de 100 %), `obs3` et `prouve` dans 0 % ; `ub50` reste à 100 %
(0,77 à 0,87 à 0,5 fois la barre). `ub50` est donc robuste à une mauvaise estimation de ρ̂, `obs2` ne l'est pas.

## Nombre moyen de configurations délégables sur 12 (ρ̂ corrigé)

| Agents à … la barre | est | faible | ub50 | obs1 | obs2 | prouve |
|---|---|---|---|---|---|---|
| 0, témoins tenus | 12 | 10,9–11,2 | 4,6–5,0 | 3,2–3,4 | 1,0 | 0,9–1,0 |
| 0, témoins en défaut | 12 | 11,1–11,2 | 1,5–1,6 | 1,0–1,1 | 1,0 | 0,4 |
| 0,3 | 11,9–12 | 10,2–10,8 | 1,6–3,6 | 1,0–3,2 | 0,8–1,0 | 0,06–0,33 |
| 2 | 8,7–11,0 | 2,8–7,1 | 0,01–0,6 | 0,1–0,7 | 0,01–0,2 | 0 |
| 5 | 6,0–8,7 | 0,4–2,9 | 0,00–0,13 | 0,00–0,06 | 0 | 0 |

Avec `obs2`, une seule configuration (WorkBench × Haiku, la seule assez volumineuse) peut être délégable : le point 2
(comparaison de la charge de validations, en moyenne sur les configurations délégables) ne porterait que sur elle.

## Ce que ces mesures montrent (déduit)

- La règle actuelle ne discrimine pas du tout : R4 ne peut jamais sortir.
- `faible` et `jeff` discriminent mal : agents 2 fois au-dessus de la barre délégables dans 94 à 100 % des cas.
- `prouve`, `ub80` et `obs3` sont trop stricts : des agents 3 à 10 fois meilleurs que la barre sont souvent jugés non délégables (contraire au sens voulu de R4 : « des agents nettement peu fiables, pas un manque de preuve »).
- Deux règles se détachent : `ub50` (une seule règle, pas de paramètre à choisir, robuste à ρ̂, ~1,5 à 5 configurations délégables, mais jusqu'à 36 % de délégables à 2 fois la barre quand ρ = 0,7) et `obs2` (meilleur rejet à 2 fois la barre, 17 % au plus, et 0 % à 5 fois ; mais une seule configuration délégable, moins de puissance à 0,5 fois la barre, 72 à 96 %, et dépendante de la correction de ρ̂).
- Limites : mondes synthétiques ; part par répétition, sans les étiquettes finales (le contrôle 3 complet doit être relancé après le choix) ; « au moins un parmi 12 configurations » n'est pas corrigé pour la multiplicité dans ces règles.
