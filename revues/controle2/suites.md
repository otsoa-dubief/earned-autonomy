# Contrôle 2 · suites (5 novembre 2026, vers 18 h 30)

Constats de GPT (`reponse_gpt.md`) et ce qui en a été fait. Rien n'a changé une décision ; tout est déclaré.

| Constat (gravité selon GPT) | Constat de fond | Suite |
|---|---|---|
| 1. Budget non démontrable sans borne sur la détection (bloquant) | Juste : toute conclusion sur le budget est conditionnelle à d = 0,95, non observable (déjà écrit en 5.8 après RF2). | Lecture datée sous la décision 3 de `REGLE.md` ; limite ajoutée en 1.4. Sensibilité : tests à erreurs ratées et audit des tâches sans alerte. |
| 2. Rejeu sur une seule trace, sans contrefactuel (bloquant) | Juste, et déjà écrit dans le plan (section 6) ; absent de la règle seule. | Lecture datée sous la pièce 1 ; limite ajoutée en 1.4 : évaluation sur trace, un rejeu contrefactuel demanderait de rejouer chaque règle en direct. |
| 3. Un agent qui agit peu paraît sûr (à corriger) | Juste pour les conclusions absolues ; la comparaison entre règles n'en dépend pas (mêmes parties). | Lecture datée sous la pièce 1 ; limite ajoutée en 1.4 ; taux de tâches réussies rapporté à côté. |
| 4. Chaîne de détection et de rattrapage floue (à corriger) | Écrite dans le plan (5.8), absente de la règle seule. | Lecture datée sous la pièce 1, qui reprend 5.8. |
| 5. B-tout et les témoins non reproductibles depuis la règle seule (bloquant) | La spécification de B-tout est dans `REGLE.md` depuis le contrôle 1 (C3) ; les témoins et les paramètres sont dans le plan et le code. | Lecture datée en pièce 9 : règle, plan, code du moteur et table des outils sont figés et déposés ensemble, avec leurs empreintes. |
| 6. « Une seule correction » contredite par la décision 9 (à corriger) | Juste : le garde-fou d'A1 a été dépassé, avant toute donnée de confirmation. | Lecture datée sous le garde-fou : dépassement déclaré tel quel ; le préenregistrement du gel fait référence ; les deux définitions sont rapportées. |
| 7. Test statistique de l'éliminatoire absent de la règle (bloquant) | Écrit dans le plan (5.13, 5.14) ; absent de la règle seule. | Renvoi dans la lecture datée sous la décision 3 (borne haute unilatérale au plus le budget ; « tenue, non mise à l'épreuve »). |
| 8. Granularité des types non figée (à corriger) | La table v1 est exhaustive et sera figée avec son empreinte (plan, 2.1). | Lecture datée en pièce 9 ; un outil absent de la table est traité comme « effet illisible », à enjeu fort. |

**Lecture d'ensemble.** Cinq constats viennent de ce que la règle seule renvoie au plan ; ils sont réglés par des renvois et par le dépôt groupé au gel. Trois sont des limites de fond, désormais écrites dans la règle et en 1.4 : évaluation sur trace (2), garanties conditionnelles à la détection (1), omissions (3). Aucun ne demande de décision d'Otsoa.
