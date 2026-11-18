# L'autonomie méritée pour les agents d'IA

Code, documents et sorties de l'étude préenregistrée *Earned Autonomy for AI Agents: A Pre-registered Error-Budget Test of Per-Action-Type Delegation* (Otsoa Dubief, chercheur indépendant, ORCID 0009-0002-7322-7575). La version anglaise de ce fichier est `README.md`.

## Le résultat

Aucune des douze configurations n'a atteint le niveau de preuve fixé à l'avance pour qu'on lui délègue des actions (verdict préenregistré R4). Une seule avait assez d'actions pour être jugée : son taux d'erreurs, 8,6 % (borne basse 4,1 %), est établi au-dessus du seuil de 0,76 %. Pour les onze autres, le volume effectif est trop faible pour conclure, dans un sens comme dans l'autre. À titre descriptif, 20 types d'actions sur 40 ont un taux établi au-dessus de leur seuil ; 13 n'ont aucune erreur observée, mais trop peu de volume pour conclure. La règle n'est pas réfutée, mais elle a peu été mise à l'épreuve, et son utilité n'a pas pu être jugée. Ces taux comptent des erreurs d'action confirmées par relecture, avec un seul chemin attendu par tâche. Une vérification exploratoire faite après le verdict montre que 48 des 79 erreurs du type jugé sont un même écart de date sur des graphiques, tranché dans les deux sens par les relecteurs ; en le levant partout, le dépassement ne reste établi qu'à deux erreurs près (voir l'article, section 6.7 et tableau X8).

L'article (`article/latex/main.pdf`) donne le résultat, ses limites et tous les écarts au préenregistrement.

## La chaîne de preuves

1. **Antériorité** (OSF 7ju3c, 5 novembre 2026) et **préenregistrement** (OSF vycge, 10 novembre 2026, 05:00 UTC ; plan figé à l'étiquette git `gel-2026-11-09`, commit a8eb1aae). Les enregistrements sont sous embargo jusqu'à la mise en ligne de l'article.
2. **Collecte** en deux vagues (10 au 13 novembre), chaque alerte automatique relue sur fiche à l'aveugle.
3. **Gel des verdicts** (OSF cusv6, 14 novembre 2026, 08:17:47 UTC) : manifeste SHA-256 de toutes les entrées du calcul final (`experience/manifeste_verdicts.txt`, 68 990 fichiers, empreinte `904aa8d3…f88d`).
4. **Tirage public** du partage calibration/confirmation, sur l'impulsion NIST 2031457 (17 novembre 2026, 08:18:00 UTC).
5. **Rejeu final**, lancé une fois avec la commande déposée (`experience/rejeu_final/`). Il a échoué une fois sur un défaut de mise en forme du code figé ; le correctif a remplacé une fonction en mémoire, sans effet sur l'étiquette (`experience/NOTE_CORRECTIF_REJEU_FINAL.md`).
6. **Sorties déposées sur Zenodo** le 17 novembre 2026 : doi:10.5281/zenodo.24321214 (fichiers sous embargo jusqu'à la mise en ligne de l'article).
7. **Code et données brutes** : ce dépôt (https://github.com/otsoa-dubief/earned-autonomy), archivé sur Zenodo sous doi:10.5281/zenodo.24331243 ; données brutes (les 68 990 fichiers du manifeste des verdicts) sous doi:10.5281/zenodo.24331245.

## Arborescence

| Dossier | Contenu |
|---|---|
| `REGLE.md`, `PLAN_EXPERIENCE.md` | la règle et le plan figé (en français, font foi) |
| `JOURNAL_CHANGEMENTS.md` | journal daté de chaque changement et écart |
| `banc/` | l'instrument : lanceur, verdicts par action, relecture des alertes, tirage public |
| `simulation/` | moteur de rejeu (`simulation/rejeu/`) et simulations d'avant le gel |
| `gel/` | manifestes et scripts du gel |
| `experience/rejeu_final/`, `experience/exploratoire/`, `experience/tirage/` | sorties du rejeu final, analyses exploratoires (non préenregistrées), fichiers du tirage |
| `outils/` | scripts qui produisent les tables, les figures et les contrôles de l'article à partir des sorties |
| `article/` | l'article (sources Markdown, LaTeX, figures, tables, registre des chiffres) |
| `revues/` | audits indépendants du plan, des résultats et de l'article |
| `depots/` | fiches des dépôts OSF et Zenodo |

## Vérifier

Il faut Python 3.12 ou plus récent, avec numpy, scipy et matplotlib (l'étude a utilisé Python 3.14.9, numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2). Les commandes sont celles du `README.md` :

1. vérifier le tirage public : `python banc/tirage/tirage_public.py verifier --dossier experience/tirage --manifeste experience/manifeste_verdicts.txt` (ajouter `--en-ligne` pour relire l'impulsion du NIST) ; réponse attendue : « tirage vérifié » ;
2. refaire les tables et les figures à partir des sorties, puis les comparer à `article/` : elles doivent être identiques ;
3. vérifier chaque chiffre de l'article dans son fichier source : `python outils/verifier_chiffres.py` ; réponse attendue : « Écarts : 0 ».

Le rejeu final lui-même demande les traces des parties, publiées à part sur Zenodo (doi:10.5281/zenodo.24331245), et environ 75 minutes sur 12 processus.

## Ce qui n'est pas fourni, et pourquoi

- Des données de terrain confidentielles et un fichier scellé d'une étude antérieure distincte ; des notes personnelles ; des adresses de tiers.
- Quatre relectures datées du 4 novembre 2026 et les notes `CADRE.md`, `ATTENTE.md` et `notes/` : elles portent sur l'étude de terrain antérieure et distincte, et citent ses chiffres confidentiels. Les empreintes git des quatre relectures sont dans `publication/ANCRES.md`.
- Les sorties du pilote sur les tâches de développement (`pilote/`).
- Les bancs eux-mêmes : utiliser les dépôts officiels aux commits indiqués dans `banc/INSTALLATION.md`.
- L'historique git complet : il contient les fichiers ci-dessus. Ce dépôt est un instantané propre ; les commits cités dans les enregistrements sont ancrés par les empreintes de leurs dossiers publics (voir `publication/`), et l'historique complet est conservé, chiffré, par l'auteur.

## Licences et citation

Code : MIT (`LICENSE`). Textes, tables, figures et données : CC BY 4.0 (`LICENSE-TEXT`). Éléments des bancs : voir `THIRD_PARTY_NOTICES`. Pour citer : `CITATION.cff`. Le code, les documents et l'article ont été écrits avec l'aide de Claude (Anthropic), sous la direction de l'auteur. Financement et intérêts : les coûts d'API ont été couverts par des crédits du programme startup d'Anthropic ; voir la déclaration de l'article.

Contact : Otsoa Dubief, otsoa.dubief@gmail.com.
