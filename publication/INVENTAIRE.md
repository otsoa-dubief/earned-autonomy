# Ce qui sera publié (PLAN_SUITE T44, 17/11/2026) — à valider par Otsoa (Q8, Q9)

Tailles relevées par `du` le 17/11 (noms et tailles seulement pour `donnees/` et `pilote/`, jamais leur contenu).

| Dossier ou fichier | Taille | Publié ? | Où | Raison |
|---|---|---|---|---|
| `simulation/` (moteur de rejeu, simulations ; sans `.venv/`) | 727 Mo dont 183 Mo de `.venv` et 515 Mo de sorties de simulation dans `controle3/` (à mettre dans l’archive Zenodo plutôt que sur GitHub) | oui, sans `.venv/` ni caches | GitHub + Zenodo (code) | code figé du rejeu ; nécessaire à la vérification |
| `banc/` (instrument, lanceur, tirage, tests) | 4,5 Mo | oui | GitHub + Zenodo | code figé de l'instrument |
| `gel/` (manifestes et scripts du gel) | 0,4 Mo | oui | GitHub + Zenodo | preuves du gel |
| `outils/` (tables, figures, analyses, dépôts) | 0,2 Mo | oui | GitHub + Zenodo | produit l'article à partir des sorties |
| `depots/` (fiches, README, manifestes ; zips hors git) | 197 Mo (zips compris) | oui, sans les zips (déjà archivés sur OSF et Zenodo) | GitHub | traçabilité des dépôts |
| `article/` (brouillon, LaTeX, figures, tables, contrôles) | 1,5 Mo | oui | GitHub ; PDF sur OSF Preprints | l'article et ses sources |
| `REGLE.md`, `PLAN_EXPERIENCE.md`, `JOURNAL_CHANGEMENTS.md`, `LANCEMENT_VAGUES.md` | petits | oui | GitHub | règle, plan figé, écarts |
| `SUIVI.md`, `PLAN_SUITE.md` | petits | oui, à relire (aucune adresse de tiers ; décisions et incidents datés) | GitHub | journal de travail, utile à la transparence |
| `CADRE.md`, `ATTENTE.md` | petits | **non** (notes personnelles, budget, étude de terrain antérieure) | – | hors de l'étude publiée |
| `revues/` (audits) | 0,9 Mo | oui, sauf `dossier_relecteur_exterieur/` (adresses de personnes) et les quatre relectures du 04/11 (étude de terrain antérieure, confidentielle ; décision d'Otsoa du 17/11) | GitHub | audits indépendants, utiles à la confiance |
| `lectures/` (fiches de lecture) | 0,2 Mo | oui | GitHub | sources de l'article |
| `reports/`, `research_notes/` | 0,5 + 1,7 Mo | en partie : seulement les recherches liées à l'étude ; **non** pour « Plan de lancement article et Tenure » et autres sans rapport | GitHub | contexte des décisions |
| `notes/` | 36 Ko | **non** pour `messages_diffusion.md` (adresses de personnes) ; `parrains_arxiv.md` non | – | données de tiers |
| `presentation/` | 3,8 Mo | **non** | – | hors étude |
| `experience/rejeu_final/`, `exploratoire/`, `tirage/`, fichiers d'empreintes et journaux | 3,3 Mo | oui (déjà sur Zenodo, sous embargo) | GitHub + Zenodo | sorties de l'étude |
| `experience/vague1/`, `vague2/` (traces des parties, relectures) | 4,3 Go ; les 68 990 fichiers du manifeste des verdicts font 4,41 Go | **selon Q8** (recommandé : oui, tels quels, archive Zenodo séparée) | Zenodo (données) | rend l'étude vérifiable de bout en bout ; licences des bancs à vérifier (T46) |
| `experience/audit_sans_alerte/`, `retraits_motif_a/` | petits | oui (dans le manifeste) | avec les données | décisions de l'instrument |
| `donnees/` | 264 Ko | **non** (fichier scellé et données confidentielles de terrain) | – | confidentiel |
| `pilote/` | 71 Mo | **non** par défaut (sorties du pilote, tâches de développement) | – | décision à part |
| `externe/` (bancs tiers clonés) | 3,5 Go | **non** (on renvoie aux dépôts officiels et à leurs commits) | – | code tiers, déjà public |
| `.git/` (historique, 214 commits) | 72 Mo | **selon Q9** (recommandé : oui, si T45 ne trouve aucun secret) | GitHub | rend vérifiables les commits cités sur OSF |
| `.claude/`, `.pytest_cache/`, `__pycache__/` | petits | non | – | outils locaux |

**Taille estimée** : code et documents, environ 20 Mo hors `.venv` et données ; archive des données (si Q8 = oui), environ 4,4 Go avant compression (limite Zenodo : 50 Go par dépôt, à relire en ligne en T50).

**Décisions d’Otsoa (17/11)** : Q8 = oui, traces publiées sur Zenodo (sous réserve de T45 et T46) ; Q9 = historique complet (sous réserve de T45).

**Q9 révisée (17/11, après T45 et la recherche « Publier un dépôt git nettoyé »)** : copie propre sans historique, avec une table d’ancres (empreintes git des dossiers publics pour chaque commit cité sur OSF) et une archive chiffrée de l’historique complet (empreinte publiée, gardée hors ligne).
