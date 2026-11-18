# Audit de contrôle : déclaration de financement, suites d'audit, T49, T50 (18/11/2026)

Périmètre : commits a92858e, 99b2e59, 967b196, f524f76. Audit indépendant, lecture seule. Aucun fichier modifié sauf ce rapport. Aucun appel réseau.

**Verdict : pas de constat bloquant ; les empreintes, les comptes et la déclaration sont cohérents ; quatre points à corriger avant le dépôt (T51), dont deux touchent `DATA_README.md`, donc `SHA256SUMS.txt`.**

Non lu, par règle : `donnees/`, `pilote/`, `data/`, les dossiers de vagues, `audit_sans_alerte/`, `retraits_motif_a/`, `rejeu_final/`, `exploratoire/` (dans le dépôt comme dans la copie propre), le contenu du zip, `~/.config/autonomie-meritee/`. Les noms privés ne sont pas écrits ici : ce rapport est dans `revues/`, dossier publié.

## Ce qui a été lancé et ce que cela donne

| Contrôle | Commande | Sortie |
|---|---|---|
| SHA-256 du zip | `shasum -a 256 ~/dev/autonomie-meritee-archives/paquet_donnees_2026-11-18/earned_autonomy_data_2026-11-18.zip` | `10cc671914bae68472015a3497f21c243f6fe6cea2e06c818c158d7f5c7a3f6a` : égal à `SHA256SUMS.txt:1` et à `FICHE_PAQUET.md:6` |
| Taille du zip | `stat -f %z` | 928 873 781 octets : égal à `FICHE_PAQUET.md:6` |
| Manifeste | `shasum -a 256 experience/manifeste_verdicts.txt` | `904aa8d3829b890c147d548718fe3ae78cd088b9f4402b3af1d2aff3487ff88d` ; même empreinte pour la copie du paquet et celle de la copie propre |
| Autres fichiers du paquet | `shasum -a 256` sur `DATA_README.md`, `LICENSE-TEXT`, `THIRD_PARTY_NOTICES` (paquet et dépôt) | égaux aux lignes 2, 4 et 5 de `SHA256SUMS.txt` ; `DATA_README.md` du paquet = celui du dépôt (`57f57ccd…`) |
| Copie T9 | `cd /Volumes/T9/autonomie-meritee/paquet_donnees_2026-11-18 && shasum -a 256 -c SHA256SUMS.txt` | 5 lignes « OK » |
| Comptes du manifeste | `wc -l`, puis `awk` sur les chemins | 68 990 lignes ; vague1 5 609, vague2 63 310, `audit_sans_alerte` 67 (6 + 40 `fiches/` + 21 `reponses/`), `retraits_motif_a` 3, `gel_plan.json` 1 : égal au tableau de `DATA_README.md:18-24` |
| Forme du manifeste | `grep`, `sort`, `uniq -d` sur les chemins | 0 ligne mal formée, 0 doublon, 0 doublon à la casse près, 0 chemin absolu ou avec `..`, 0 espace, 0 caractère non ASCII, longueur maximale 152 |
| Noms de fichiers du tableau « In each wave folder » | liste des entrées de 3e niveau du manifeste | tous présents ; `vague2.json` dans la vague 1 seulement |
| Fichiers cités par `DATA_README.md:30-45` | `[ -e ]` sur les 11 chemins de `banc/` ; `grep` des choix 18, 19, 26, 40 dans `banc/CHOIX_LANCEUR.md` | tous présents |
| Date de cusv6 | `grep 08:17:47 depots/2026-11-14_gel_verdicts_v2/FICHE_DEPOT.md` | `2026-11-14T08:17:47.424176+00:00` : égal à `DATA_README.md:9` |
| Commande du rejeu | `sed -n 40,50p depots/2026-11-14_gel_verdicts_v2/paquet/README.md` | chemins `experience/vague1/2026-11-10_06-19-06`, `experience/vague2/2026-11-10_19-53-13`, etc. : cohérents avec le préfixe `experience/` du zip |
| Empreintes des 4 relectures | `git ls-tree gel-2026-11-09 revues/` et `git ls-tree HEAD revues/` ; `git log --follow` | 4 empreintes égales à `publication/ANCRES.md:51-54` ; un seul commit par fichier, présent dès le premier commit (b5e76cc) |
| Ancres dans la copie | `git rev-parse HEAD:banc HEAD:gel HEAD:simulation/rejeu HEAD:simulation/tests` | `bf7c6ba7…`, `2173537f…`, `dcf6c17f…`, `f4e8fee2…` : égaux à `ANCRES.md` |
| Liste de la copie | `diff` de `publication/CONTENU_PUBLIE.txt` contre `git ls-files` de la copie ; `shasum -c` sur 619 lignes (hors les 4 sous-dossiers interdits) | seule différence : `CONTENU_PUBLIE.txt` lui-même ; 0 écart d'empreinte |
| Nom commercial dans la copie | `grep -rIil <motif demandé>` et `find -iname` (hors `.git` et les 4 sous-dossiers interdits) ; même chose sur les fichiers binaires (`grep -rail`) | 0 fichier, 0 nom de fichier. Les deux autres noms que le caviardage remplace (vus dans le `diff` copie/dépôt) : 0 |
| `/Users/` dans la copie, hors `banc/`, `gel/`, `simulation/`, `experience/` | `grep -rIl '/Users/'` | 3 fichiers : `PLAN_SUITE.md:397` et `publication/RAPPORT_SECRETS.md:7,23` (texte littéral « /Users/… »), `publication/preparer_copie.sh:17` (le motif de remplacement lui-même) |
| PDF | `pdftotext article/latex/main.pdf - \| grep -A4 'Funding and competing'` | nouveau texte, identique à `brouillon.md:419` |

Non vérifié : le contenu du zip (interdit), donc ni « 0 écart » ni les décomptes de la recherche par motif (`FICHE_PAQUET.md:9`, `DATA_README.md:49`) ; la limite de Zenodo ; les nombres de tests de l'essai (tests non relancés) ; le script `construire_paquet_donnees.py` n'a pas été relancé (il lit les dossiers interdits).

## À corriger

### C1. La commande de vérification du `DATA_README` échoue dans le cas qu'il décrit

`depots/2026-11-18_donnees/DATA_README.md:14` : `cd experience && shasum -a 256 -c ../manifeste_verdicts.txt`, « from the repository root ».

Le manifeste n'est pas dans le zip (0 ligne « manifeste » dans le manifeste). Dans le dépôt de code, il est dans `experience/` (`preparer_copie.sh:13` ; présent dans la copie). `../manifeste_verdicts.txt` désigne donc la racine du dépôt, où il n'y a rien, sauf si le lecteur y a posé le fichier du dépôt de données, ce que le texte ne dit pas.

Essai sur une arborescence factice (deux fichiers, manifeste dans `experience/`) :

```
$ cd experience && shasum -a 256 -c ../manifeste_verdicts.txt
shasum: ../manifeste_verdicts.txt: No such file or directory
$ cd experience && shasum -a 256 -c manifeste_verdicts.txt
vague1/f.txt: OK
gel_plan.json: OK
```

Avec le manifeste copié à la racine, la commande d'origine passe. Correction : écrire `shasum -a 256 -c manifeste_verdicts.txt`, ou dire où poser le manifeste téléchargé. Aussi : « To check a file » alors que la commande vérifie les 68 990 fichiers. Le format du manifeste (deux espaces, chemins relatifs à `experience/`) convient à `shasum -c`.

### C2. La prochaine copie propre réécrira `DATA_README.md` et `FICHE_PAQUET.md`

`publication/preparer_copie.sh:15-17` remplace `ROOT` par `ROOT` dans tous les `.md` hors dossiers figés, donc dans `depots/2026-11-18_donnees/`. Ces fichiers ne sont pas encore dans la copie (elle date d'avant T50).

```
$ perl -pe 's#ROOT#ROOT#g; …' depots/2026-11-18_donnees/DATA_README.md | shasum -a 256
8b28e7ea6cc46068436e2bb8055676b673b14dcd2cfcc6ae0646f5ec4ec87449
50c50
< … the author's local path to the repository (`ROOT`) …
> … the author's local path to the repository (`ROOT`) …
```

Deux effets : la phrase qui prévient le lecteur du chemin local perd son sens (`DATA_README.md:50`, `FICHE_PAQUET.md:9`) ; le `DATA_README.md` du dépôt GitHub n'aura plus l'empreinte `57f57ccd…` de `SHA256SUMS.txt:2`. Correction : exclure `depots/2026-11-18_donnees/` de la réécriture, ou écrire le chemin autrement dans les deux fichiers.

Toute correction de `DATA_README.md` (C1, C2) change son empreinte : refaire `SHA256SUMS.txt`, la copie dans `~/dev/autonomie-meritee-archives/…` et celle de T9.

### C3. `ESSAI_REPRODUCTION.md` se contredit sur `pilote/`

- `publication/ESSAI_REPRODUCTION.md:3` : « no file from `donnees/`, `pilote/` or `data/` read ».
- `:20` et `:22` : les mêmes tests lancés dans le dépôt complet, « engine 319 passed » ; ces tests « replay the pilot outputs » dans `pilote/etape2/`.

15 fichiers de `simulation/rejeu/tests` citent `pilote` (`grep -rln pilote simulation/rejeu/tests simulation/tests`). Les 319 succès dans le dépôt complet supposent que les tests ont lu `pilote/`. La ligne 3 n'est vraie que pour l'essai dans la copie. À reformuler ; et à confronter à la règle du projet sur `pilote/`.

### C4. La copie propre est en retard sur HEAD

La copie (commit dca4c21, 653 fichiers) n'a ni `publication/ESSAI_REPRODUCTION.md`, ni `depots/2026-11-18_donnees/`, ni `outils/construire_paquet_donnees.py` ; `SUIVI.md` et `PLAN_SUITE.md` y sont antérieurs (boucle `[ -e ]` sur `git ls-files`, puis `cmp`). `SUIVI.md:445` dit encore « 556 fichiers, arbre a7c01d93… » ; la copie actuelle a l'arbre `80877be1…`. À refaire avant T51, après C1 et C2, et relancer la recherche de motifs dessus.

## Remarques

### R1. Script du paquet : la garantie tient, avec des limites

`outils/construire_paquet_donnees.py`. Lecture du code seulement.

Ce qui tient : chaque fichier est haché sur les octets mêmes qui sont écrits (`:50-56`) ; `check()` exige l'égalité des ensembles de noms et l'absence de doublon (`:68`), puis relit chaque entrée et compare au manifeste (`:70-76`). « Identique au manifeste, rien en plus » est donc garanti pour les entrées du répertoire central, telles que `zipfile` de Python les lit.

Limites :
- `:19`, `:41` : le manifeste est contrôlé sur 8 caractères (`startswith("904aa8d3")`), soit 32 bits. Mettre l'empreinte entière.
- Écriture et relecture par la même bibliothèque. Aucun essai avec un autre outil. 68 990 entrées dépassent 65 535 : l'archive est forcément au format ZIP64. À essayer une fois avec `unzip -tqq` et l'Utilitaire d'archive (non fait ici : interdit).
- `:84-87` : le script ne copie pas `DATA_README.md` et n'écrit pas `SHA256SUMS.txt` ; ces deux étapes sont manuelles et ne sont pas décrites dans la fiche.
- `:59` : un zip déjà présent est remplacé sans avertir ; un `.partial` reste après un échec.
- `:21`, `:55` : dates fixées au 18/11 et droits 0644 ; les dates d'origine des fichiers sont perdues (sans effet sur les empreintes).
- `:8` : « Nothing is opened » est faux au sens strict (chaque fichier est lu) ; lire « rien n'est affiché ».
- Aucun test pour ce script.

### R2. `preparer_copie.sh`

- Pas de régression vue : la liste de la copie est conforme à `CONTENU_PUBLIE.txt`, les ancres sont bonnes.
- `:8`, `resultats[^/]*/` : les 9 dossiers `simulation/controle3/resultats*` sont bien absents de la copie ; le reste de `controle3` y est (9,3 Mo, dont 4 fichiers `b_seuil/seconde_mesure*.jsonl` de 2 Mo chacun, soit 8,3 Mo : ce sont des mesures, pas du « code et notes » comme le dit `ESSAI_REPRODUCTION.md:30`).
- `:8` : l'audit du 17/11 est exclu parce qu'il décrit ce qui n'est pas publié, mais `SUIVI.md:441-446`, publié, en donne le résumé (ancienne déclaration citée, « ne veut pas des phrases sur l'origine… », renvoi au fichier exclu, micro-entreprise nommée puis caviardée en `[company]`). Exclusion trop étroite ou assumée : à trancher par l'auteur.
- `:20` : l'arrêt si le fichier de caviardage manque est correct (`DEST` est neuf, `rm -rf` sans danger), mais il arrive après la copie ; le placer en tête.
- `:17` : le nouveau motif ne couvre que la forme `-Users-Otsoa-dev-<nom>-workspace`. C'est la seule présente (`git grep -Iho` : 4 occurrences, toutes de cette forme). Fragile si une autre forme apparaît.
- `:15`, `:21` : le caviardage des noms ne traite que `.md`, `.txt`, `.py` ; les chemins, sept extensions. `.sh`, `.tex`, `.json` (pour les noms) ne sont pas couverts. Aucune fuite constatée aujourd'hui (voir tableau).
- `:17` : la réécriture en `ROOT` casse des scripts publiés : `research_notes/Corrélation intra tâche par strates/scripts/verif_rapport/*.py` ont `sys.path.insert(0, "ROOT/simulation")` dans la copie. Antérieur à aujourd'hui (T48).
- `:9` : `xargs tar | tar -xf -` ne lit que la première archive si `xargs` découpe la liste. Pas le cas à 653 fichiers. Pas de `pipefail`.
- Le commit de la copie porte l'adresse `recherche@autonomie-meritee.local`, qui n'existe pas (`git log --format=%ae`).

### R3. Déclaration de financement : identique en substance

`git grep -n -I -i -E 'funded by|no funding|received no|fund(ed|ing)|financ|no affiliation|Claude for Startups|…'` hors `revues/`, `reports/`, `research_notes/`.

- Texte complet, mêmes quatre phrases : `article/brouillon.md:419`, `article/latex/body.tex:89`, `main.pdf`, `article/controle_fr.md:47` (traduction fidèle).
- Version courte, sans la phrase sur l'abonnement ni « proof-of-concept » : `.zenodo.json:11`, `DATA_README.md:53`. Version d'une phrase avec renvoi à l'article : `README.md:67`, `LISEZMOI.md:55`. Pas de contradiction.
- Aucune occurrence restante de « funded by the author », « no funding », « no affiliation » dans les fichiers publics, sauf :
  - `PLAN_SUITE.md:307` : « financement par l'auteur » dans l'objectif d'une ancienne tâche (publié) ;
  - `SUIVI.md:441`, `:443` : l'ancienne déclaration citée comme historique (publié, voir R2).
- « Independent researcher » reste partout (`.zenodo.json:4`, `CITATION.cff:8`, `brouillon.md:11`). Compatible avec la déclaration, puisque la micro-entreprise y est dite. À confirmer par l'auteur.
- Le dépôt Zenodo 24321214 en ligne n'a pas encore la phrase (`SUIVI.md:445` le note).

### R4. `ESSAI_REPRODUCTION.md` : explications plausibles

- Totaux cohérents : moteur 273 + 1 + 46 = 320 = 319 + 1 ; gel 15 + 1 = 16 ; revue 22 + 23 des deux côtés.
- Banc : 667 + 36 + 5 + 4 = 712 dans la copie, 714 dans le dépôt complet. L'écart de 2 s'explique : `banc/tests/test_verdicts.py:470,479` paramètre un test sur les 3 fichiers `task_issues` de τ-bench ; sans τ-bench, pytest crée un seul test, sauté. Non dit dans le compte rendu.
- 46 échecs du moteur : plausible (15 fichiers de tests citent `pilote`).
- `test_paires.py`, `test_tirage.py` : plausible. `banc/tirage/tirer.py:14-18` et `paires.py:38,61,64` lisent `externe/tau2-bench` et aussi `externe/WorkBench` ; le compte rendu (`:23`) ne cite que τ-bench.
- `test_verifier_gel…` (`banc/tests/test_lanceur_gel.py:21-28`, attend un commit de 40 caractères et l'étiquette) et `test_apercu_du_vrai_depot` (`gel/tests/test_manifeste.py:153`) : plausible.
- 23 échecs de `revues/code/lanceur` : plausible. `test_revue_lanceur.py:3` : « chaque test passe tant que le défaut est présent ».
- `test_u3_pid_reutilise…` (`banc/tests/test_revue_ultra_banc.py:97`) : « fails identically », sans cause. Le titre « Every failure explained » va donc un peu loin. Hypothèse non vérifiée : comparaison de la ligne de commande d'un processus avec `sys.executable` d'un environnement neuf.

### R5. Détails du `DATA_README` et de la fiche

- `DATA_README.md:12` : dézipper à la racine du dépôt de code écrase 10 fichiers déjà présents (`gel_plan.json`, 6 de `audit_sans_alerte/`, 3 de `retraits_motif_a/`). `gel_plan.json` est identique (`b1d124ab…` dans la copie et dans le manifeste) ; les 9 autres non comparés (interdits). Prévenir le lecteur, ou donner `unzip -o`.
- `preparer_copie.sh:12` retire `audit_sans_alerte/fiches` et `reponses` de la copie GitHub ; le zip les contient (40 + 21 fichiers). Raison non écrite dans `publication/`.
- `DATA_README.md:32-33` : « one log per attempt », « one JSONL per attempt » : vague 2, 13 227 fichiers dans `logs/`, 13 225 dans `usage/` ; 2 `.jsonl` sont dans `ecartees/`. Vague 1 : 1 195 et 1 195.
- `FICHE_PAQUET.md:3` : « le dépôt sur Zenodo est T52 » ; `PLAN_SUITE.md:438` place le brouillon Zenodo en T51, la publication en T52.
- `FICHE_PAQUET.md:6` : « Durée : 74 s » : compatible avec les dates des fichiers (dossier 05:51, zip 05:52).
