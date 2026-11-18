# Métadonnées du dépôt arXiv (PLAN_SUITE T55, 18/11/2026)

Paquet : `article/arxiv/paquet.tar.gz`, construit par `outils/construire_arxiv.py` (30 fichiers ; compile seul avec pdfLaTeX dans un dossier vide, sans BibTeX grâce à `main.bbl` ; 55 pages ; 0 débordement, 0 référence manquante). À reconstruire après toute modification de l'article : `python3 outils/construire_latex.py && (cd article/latex && latexmk -pdf main.tex) && python3 outils/construire_arxiv.py`.

Règles lues le 18/11/2026 : https://info.arxiv.org/help/submit_tex.html (fournir le .bbl ; compilation depuis la racine du paquet), https://info.arxiv.org/help/prep.html (résumé de 1 920 caractères au plus ; champ « Comments »), https://info.arxiv.org/help/moderation/index.html (usage de l'IA générative à déclarer dans l'article : fait, « Use of AI tools »).

| Champ | Valeur (à coller tel quel) |
|---|---|
| Title | Earned Autonomy for AI Agents: A Pre-registered Error-Budget Test of Per-Action-Type Delegation |
| Authors | Otsoa Dubief |
| Primary category | cs.AI |
| Cross-lists (proposition) | cs.LG ; stat.AP |
| Comments | 55 pages, 3 figures. Pre-registered on OSF (https://osf.io/vycge/). Code: https://github.com/otsoa-dubief/earned-autonomy ; data: doi:10.5281/zenodo.24331245 ; results: doi:10.5281/zenodo.24321214 |
| License | CC BY 4.0 |
| Abstract (1525 caractères) | voir ci-dessous |

## Abstract

Which actions may an AI agent take without human sign-off? We propose an open rule: an agent earns autonomy on one action type after N consecutive verified successes and loses it at the first confirmed error; N is derived from an error budget fixed in advance per stakes level by adapting the unrestricted AOQL of continuous sampling plans, with a conditional bound on the extra errors delegation lets through. We test it in a pre-registered replay: three Claude 5.5 models on four public benchmarks (τ-bench airline, retail and banking; WorkBench), 14,265 episodes played (13,623 analysed), writes checked by exact comparison (98.7% coverage) and alerts reviewed blind. No configuration reached the pre-registered level of evidence required for delegation (pre-registered verdict R4). Only one of twelve configurations had enough volume to be judged; its error rate, 8.6% (lower bound 4.1%), is established above the 0.76% threshold. The other eleven had too little volume to conclude either way. Descriptively, 20 of 40 action types have an error rate established above their threshold; 13 show no observed error but too little volume. The rule was not refuted, but it was hardly put to the test, and its usefulness could not be judged. These rates count action errors confirmed by review against a single expected path per task; in a blind sample reviewed by the author, 3 of 10 confirmed alerts were lifted. Earning autonomy under such budgets takes far more verified actions than these benchmarks provide at our volumes.

## En français, pour Otsoa

- **Titre** : « L'autonomie méritée pour les agents d'IA : un test préenregistré, par budget d'erreurs, de la délégation par type d'action ».
- **Catégorie principale** : cs.AI (intelligence artificielle). **Catégories secondaires proposées** : cs.LG (apprentissage automatique) et stat.AP (statistique appliquée). À confirmer par Otsoa au dépôt (T56).
- **Commentaire** : nombre de pages et de figures, lien du préenregistrement, du code et des données.
- **Licence** : CC BY 4.0, la même que sur Zenodo.
- **Résumé** : celui de l'article, mot pour mot (traduction dans `article/controle_fr.md`).

## À faire avant le dépôt (T56)

- Remplacer « Draft, 17 November 2026 » (`article/latex/main.tex`, ligne 55) par la date du jour J, ajouter dans le commentaire le DOI Zenodo de l'article (T43 bis), puis reconstruire le paquet.
- Le parrainage (T53, T54) est nécessaire pour un premier dépôt en cs.AI.
