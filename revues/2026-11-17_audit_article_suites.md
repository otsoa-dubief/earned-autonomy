# Suites de l'audit indépendant de l'article (PLAN_SUITE T36, 17/11/2026)

Rapport traité : `revues/2026-11-17_audit_article.md` (3 bloquants, 10 importants, 22 mineurs). Après corrections : PDF recompilé sans erreur ni référence indéfinie (55 pages), `outils/verifier_chiffres.py` : 0 écart.

## Bloquants et importants

| Constat | Réponse | Endroit |
|---|---|---|
| B1 crochet [VERIFY] des relecteurs | retiré ; les noms seront ajoutés en T39 s'ils acceptent | brouillon, déclarations |
| B2 table X2, barre tronquée | barre écrite en % à 4 chiffres significatifs (0,008319 %, 0,008822 %) | `outils/tables_exploratoires.py` |
| B3 table de décision en français, « battu » | retirée du PDF (gardée dans `tables.md` pour la traçabilité, avec une note : « battu » est le libellé du critère, point 2 non jugé) ; la table de décision anglaise est la table 2 (6.2) ; renvoi « breakdown by reason » réorienté vers `decision.csv` | `outils/tables_article.py`, `outils/tables_latex.py` |
| I1 table G | B-tout seul (100 lignes au lieu de 400), bornes hors de [0, 1] ramenées avec astérisque et note | `outils/tables_article.py` |
| I2 libellés français des tables | traduits à la conversion (airline, banking, retail, above, undetermined, scenario, announced, silent, B-regular, delay10…) ; « keeps budget » → « no established excess » | `outils/tables_latex.py`, `outils/tables_article.py` |
| I3 chiffres post hoc sans étiquette dans le corps | « post hoc » pour ρ̂ = 0,885 ; « exploratory, Appendix D » pour 31 % à 79 % | `article/atelier.md` 6.2, 7 |
| I4 statut des dépôts OSF | dit : sous embargo jusqu'au 04/11/2030, rendus publics le jour de la mise en ligne (T43) ; « are public » → « will be public » | annexe F, conclusion, déclarations |
| I5 sorties secondaires non rapportées | paragraphe ajouté en C.6.7 (tout approuver, trois réussites, oracle rétrospectif, charge avec épreuves, ordre des parties) avec les valeurs de `budget.csv` et `charges.csv` ; renvoi dans le corps | brouillon 6.7, atelier 6.7 |
| I6 harnais de la vague 1, analyses suggérées | D7 : harnais non noté, analyses suggérées non faites | annexe A |
| I7 D1 « presentation » | D1 réécrit : « with effects on the task », les quatre différences, page figée jamais utilisée | annexe A |
| I8 retraits de la banque | D11 : pas d'analyse de sensibilité ; task_082 dite la moins nette | annexe A |
| I9 version non anonyme, gabarit `article` | **désaccord partiel** : cette version est celle d'arXiv, signée par choix ; l'anonymisation et le gabarit de l'atelier sont prévus par la tâche d'adaptation à l'atelier (PLAN_SUITE, après le choix Q14) | – |
| I10 « protocol that could fail » | contribution 3 reformulée : protocole à issue ouverte, qui montre les volumes nécessaires ; le plan prévoyait l'absence de certification sous la barre | atelier, introduction |

## Mineurs

| Constat | Réponse |
|---|---|
| M1 | 2,34 en retard10 ajouté (corps 6.7) |
| M2, M15 | D4 : le troisième cas n'est pas décrit ; pas d'analyse de sensibilité (3 alertes sur 2 761) |
| M3 | non corrigé : 72,10 $ (journal) et 72,13 $ (rapport, coûts majorés) sont deux comptes du lanceur ; l'arrêt à 72,00 $ est 80 % du plafond accordé de 90 $ (accord d'Otsoa), pas 0,8 × 1,5 × 60,53 ; à préciser en B.4.4 avant la mise en page |
| M4 | description des 27 mentions « fragile » corrigée (5 configurations, 22 scénarios) |
| M5 | légendes de X3 (réserve entière) et X5 (taux de la réserve entière × part au palier 2 de la confirmation) précisées |
| M6, M7 | gardés : colonnes et intervalles tels que sortis du moteur ; à annoter à la mise en page |
| M8 | renvois vers la version longue : à lever à la mise en page (préfixes B., C.) |
| M9 | D12 : aucune sortie du premier passage lue ; identité vérifiée par empreintes SHA-256 (`revues/2026-11-17_identite_six_tables.md`) |
| M10, M18, M21 | annexe F : script du tirage et sa spécification (`banc/tirage/`), journal du rejeu final, dépendance à l'historique git publié |
| M11 | Haiku 5.5 dans `execution.jsonl` : non vérifié (dossier de vague hors périmètre des relecteurs) ; à ajouter en D7 si confirmé |
| M12, M13 | kappa (environ 0,70) et intervalle de 13/15, comptes d'alertes (a) par tâche retirée : à ajouter en C.6.1 avant la mise en page |
| M14 | « about 10 % of Haiku's banking episodes » ajouté |
| M16 | E.2 : redite Zhang et Zhang, à fondre à la mise en page |
| M17 | 05:00 UTC est l'heure d'enregistrement OSF (SUIVI) ; le commit de 06:03 heure de Paris (05:03 UTC) est postérieur : pas de contradiction |
| M19, M20 | lisibilité (table 6, étiquettes de la figure 2, titre d'axe de la figure 3) et lignes trop larges : à reprendre au gabarit de l'atelier |
| M22 | « secondary reading » ajouté (corps 6.6) |

Désaccords à montrer à Otsoa : I9 (version arXiv signée, anonymisation reportée à l'adaptation à l'atelier) ; M3 (le seuil d'arrêt vient du plafond accordé, pas de la formule) ; M17 (pas de contradiction d'horaire).
