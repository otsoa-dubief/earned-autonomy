# Technique git : publier un historique nettoyé ou un instantané (état fin 2026)

Contexte de la demande : dépôt **local uniquement, jamais poussé**. Des commits sont cités ailleurs (rapports, Zenodo). Fichiers privés à retirer (ex. `donnees/`, notes privées).

## Q1. Ce que filter-repo / BFG conservent et ce qu'ils cassent (blobs, trees, commits, correspondance)

### Takeaway
Le hachage git est adressé par le contenu. Un blob ou un tree dont les octets ne changent pas garde son identifiant. Chaque commit qui a un ancêtre réécrit change d'identifiant, et tous ses descendants avec lui. filter-repo écrit `.git/filter-repo/commit-map` (ancien → nouveau). Un tiers ne peut pas vérifier cette table sans voir au moins les objets de métadonnées des anciens commits.

### Cited Findings
- Tout objet git est nommé par `SHA-1("<type> <taille>\0" + contenu)`. Un blob se hache avec l'en-tête `blob <taille>\0` suivi des octets du fichier, sans nom de fichier ni chemin. Exemple : `printf 'blob 16\0what is up, doc?' | sha1sum` = `bd9dbf5a…`. — [Git Book, Git Internals – Git Objects](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- Un tree liste des entrées (mode, nom, SHA d'un blob ou d'un sous-tree). Deux répertoires ayant les mêmes modes, noms et hachages d'entrées ont donc le même hachage de tree. Un commit contient le tree racine, les parents, l'auteur et le committer avec leurs horodatages, puis le message. — [Git Book](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)
- La spécification SWHID formalise le même calcul : `cnt` = SHA1 de "blob longueur\0 octets", `dir` = SHA1 de "tree" et des entrées `mode nom\0 id20octets` triées, `rev` = SHA1 de "commit" et du tree racine, des parents, de l'auteur, du committer et du message. Ces quatre types sont « compatibles avec la façon dont Git calcule actuellement ses objets », mais la spec dit que cette compatibilité est fortuite et non garantie à l'avenir. — [SWHID spec v1.2 §5](https://www.swhid.org/specification/v1.2/5.Core_identifiers/)
- filter-repo : l'ID d'un commit change même s'il n'est pas édité, car « the fact that you changed any of its ancestors is also a change that counts ». — [man git-filter-repo (Arch, Git 2.47.1, 27/11/2024)](https://man.archlinux.org/man/git-filter-repo.1.en)
- Le même manuel cite d'autres causes de changement : les signatures de commits et de tags sont supprimées (un tag signé devient un tag annoté), les en-têtes de commit étendus sont retirés, un commit sans auteur reçoit le committer comme auteur, et les messages sont ré-encodés en UTF-8 sauf avec `--preserve-commit-encoding`. Les hachages d'anciens commits cités dans les messages sont remplacés par les nouveaux, sauf avec `--preserve-commit-hashes`, et ce remplacement change à son tour le hachage. — [man git-filter-repo](https://man.archlinux.org/man/git-filter-repo.1.en)
- Le manuel indique que les commits « in range of the rewrite will be listed, even commits that are unchanged » dans la commit-map. Il ne dit pas explicitement que les commits antérieurs au premier commit touché gardent leur hachage. — [Documentation filter-repo](https://raw.githubusercontent.com/newren/git-filter-repo/main/Documentation/git-filter-repo.txt)
- Fichiers que filter-repo écrit dans `$GIT_DIR/filter-repo/` :
  - `commit-map` : en-tête "old new". Un hachage nul dans la colonne new signifie que le commit a été supprimé (devenu vide).
  - `ref-map` : en-tête "old new ref".
  - `changed-refs` : refs pour lesquelles old ≠ new.
  - `first-changed-commits` : « commits that got rewritten and which had no parents that were also rewritten ».
  - `already_ran` : contourne la vérification « fresh clone » lors des passes suivantes.

  — [Documentation filter-repo](https://raw.githubusercontent.com/newren/git-filter-repo/main/Documentation/git-filter-repo.txt)
- `--prune-empty auto`, la valeur par défaut, élague les commits devenus vides (par exemple un commit qui ne touchait que `donnees/`). Ils apparaissent alors avec un new nul dans la commit-map. — [Documentation filter-repo](https://raw.githubusercontent.com/newren/git-filter-repo/main/Documentation/git-filter-repo.txt)
- `--replace-refs` peut créer des refs `refs/replace/<ancien>` pour que les anciens IDs restent utilisables localement. Le défaut est `update-no-add`. — [Documentation filter-repo](https://raw.githubusercontent.com/newren/git-filter-repo/main/Documentation/git-filter-repo.txt)
- BFG, comportement par défaut : « doesn't modify the contents of your latest commit on your master (or HEAD) branch ». Les commits protégés gardent leurs fichiers, mais leur ID change s'ils suivent des commits nettoyés : « only the SHA-1 id of the filesystem-tree will remain the same ». `--no-blob-protection` lève cette protection. BFG s'utilise sur un `git clone --mirror`. — [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- BFG écrit `object-id-map.old-new.txt`, une ligne « SHA d'origine, SHA réécrit » par objet, dans un dossier `<repo>.bfg-report/<date>/<heure>/`. GitLab s'en sert côté serveur pour purger ses refs internes. La source est secondaire, faute de documentation BFG officielle sur ce point. — [Gitaly cleanup service (Mintlify)](https://www.mintlify.com/tnir/gitaly/api/cleanup-service) ; [Gitaly internalrefs](https://pkg.go.dev/gitlab.com/gitlab-org/gitaly@v1.68.0/internal/service/cleanup/internalrefs)
- GitHub recommande désormais filter-repo ≥ 2.47 avec `--sensitive-data-removal`. Sa page ne mentionne pas BFG. — [GitHub Docs, Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

### Inferences
- **Blobs non touchés** : hachage identique, puisqu'il ne dépend que des octets. Ceci vaut pour filter-repo comme pour BFG, sauf si `--replace-text` ou un `--blob-callback` modifie le contenu.
- **Trees de sous-répertoires qui ne contenaient aucun chemin retiré** : hachage identique, puisque leurs entrées sont inchangées. Par exemple, `git rev-parse <commit>:simulation` donne le même SHA avant et après si rien n'a été retiré sous `simulation/`.
- Les trees ancêtres d'un chemin retiré changent : le tree racine et tout répertoire parent d'un fichier supprimé.
- **Commits** : un commit change dès que son tree racine change (il contenait un chemin retiré), ou dès qu'un parent a changé, puisque l'ID du parent est écrit dans l'objet commit. Tous les commits à partir de `first-changed-commits` changent donc, de proche en proche jusqu'aux pointes des branches.
- Si `donnees/` existe dès le commit racine, **tous les commits changent**, y compris le premier. Les commits antérieurs à la première apparition d'un chemin retiré gardent en principe leur hachage, sauf effets de bord : commit signé, en-tête étendu, encodage non UTF-8, ou message citant un hachage réécrit. Il faut le vérifier en comparant `git rev-parse` avant et après (voir le Gap ci-dessous).
- **Vérifier la commit-map sans le dépôt privé** est impossible dans le cas général. Un tiers voit le nouveau commit et une affirmation « ancien X = nouveau Y ». Pour recalculer X, il lui faut l'objet commit ancien (tree racine, parents, auteur, dates, message), puis l'objet tree racine ancien.
- **Solution partielle, une preuve de type Merkle** : publier les objets bruts `git cat-file commit <ancien>` et `git cat-file -p` du tree racine ancien et des trees intermédiaires. Ces objets ne contiennent que des noms et des hachages, jamais le contenu des fichiers privés. Le tiers recalcule alors :
  1. les hachages des sous-trees publics à partir des fichiers publiés ;
  2. le tree racine ancien, en insérant les hachages opaques des entrées privées ;
  3. le SHA du commit ancien.

  Limites de cette méthode :
  - les **noms** de fichiers privés et les messages de commit sont révélés ;
  - un fichier privé court ou devinable peut être confirmé par force brute de son hachage de blob ;
  - pour vérifier toute la chaîne de parents, il faut publier tous les objets commit anciens.
- Une commit-map publiée aujourd'hui ne prouve rien sur la date de l'historique d'origine. Seul un ancrage antérieur (tag signé, horodatage, archive tierce) fait foi.

### Gaps
- Aucune source primaire n'affirme noir sur blanc que les commits antérieurs au premier commit touché gardent leur hachage avec filter-repo. Une source secondaire (guide Mintlify) cite aussi les « non-canonical trees » corrigés par fast-import comme cause de changements inattendus. Ce n'est pas confirmé dans le manuel officiel.
- La documentation officielle du format complet du dossier `.bfg-report` reste introuvable.

## Q2. Rendre les commits cités vérifiables plus tard sans publier les fichiers privés

### Takeaway
Les meilleurs ancres sont des hachages de contenu indépendants de l'historique : trees de sous-répertoires inchangés, et SWHID `dir`/`cnt`, qui sont des hachages git. On peut les compléter par des horodatages (OpenTimestamps), des tags signés, et un dépôt chiffré de l'historique complet. Software Heritage n'archive que du public.

### Cited Findings
- SWHID = ISO/IEC 18670:2025, « SoftWare Hash IDentifier (SWHID) Specification V1.2 », publiée le 23/04/2025, au contenu identique à la v1.2 GitHub. La norme couvre le format de l'identifiant, pas la résolution (retrouver l'objet). — [ISO 89985](https://www.iso.org/standard/89985.html) ; [annonce swhid-discuss](https://groups.google.com/g/swhid-discuss/c/hsxbEPEaCkY) ; [OpenChain, 29/04/2025](https://openchainproject.org/news/2025/04/29/from-heritage-to-hash-swhid-becomes-a-global-iso-iec-standard)
- Un SWHID `swh:1:dir:<sha1>` est le hachage du tree git. `swh:1:cnt:` est le hachage du blob et `swh:1:rev:` celui du commit. — [SWHID spec v1.2](https://www.swhid.org/specification/v1.2/5.Core_identifiers/)
- `swh identify` (paquet `swh.model[cli]`) calcule un SWHID **localement**, sans archivage, sur un fichier ou un répertoire. Il accepte `--exclude` et `--verify` pour contrôler un objet contre un SWHID attendu. Un SWHID calculé localement est égal à celui de l'archive pour le même contenu. — [SWH CLI docs](https://docs.softwareheritage.org/devel/swh-model/cli.html)
- « Save Code Now » est réservé aux dépôts publics git, hg et svn. Une origine inconnue passe en file de modération. Le « deposit » est une API authentifiée pour déposer des archives avec métadonnées. — [SWH FAQ](https://docs.softwareheritage.org/user/faq/) ; [SWH Deposit](https://docs.softwareheritage.org/devel/swh-deposit/index.html)
- OpenTimestamps s'intègre à git via `gpg.program` = `ots-git-gpg-wrapper.sh`. On l'utilise avec `git commit -S` / `git tag -s`, puis `git tag -v` ou `git log --show-signature` pour vérifier. La preuve est ajoutée après la signature PGP et GnuPG l'ignore. L'horodatage reste incomplet tant qu'il n'est pas ancré dans Bitcoin, ce qui prend des heures. Jusque-là il dépend des serveurs calendrier, et `--wait` produit une preuve autonome. — [opentimestamps-client, git-integration.md](https://github.com/opentimestamps/opentimestamps-client/blob/master/doc/git-integration.md) ; [Peter Todd, 2016](https://petertodd.org/2016/opentimestamps-git-integration)
- Ce qui est signé et horodaté, c'est « simply the commit minus the signature itself », donc l'objet commit avec son SHA-1 de tree. — [Peter Todd, 2016](https://petertodd.org/2016/opentimestamps-git-integration)
- Des outils tiers horodatent aussi des commits : `tstamp` stocke les `.ots` sous `refs/timestamps`, et `git-ots` existe. Leur maturité n'a pas été vérifiée. — [tstamp](https://www.github.com/barkyq/tstamp) ; [git-ots (PyPI)](https://pypi.org/project/git-ots/)
- filter-repo supprime les signatures : un tag signé devient un tag annoté. Un tag signé posé sur l'historique privé ne survit donc pas à la réécriture. — [man git-filter-repo](https://man.archlinux.org/man/git-filter-repo.1.en) ; [GitHub Docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

### Inferences
- **Ancre la plus robuste pour le dépôt nettoyé** : publier, pour chaque commit cité, la table `ancien commit → git rev-parse <ancien>:simulation` (et les autres sous-répertoires publics). Chaque hachage de cette table doit se retrouver tel quel dans le dépôt nettoyé, via `git rev-parse <nouveau>:simulation`. N'importe qui peut le vérifier avec `swh identify` ou `git` sur l'instantané publié, et Software Heritage le résoudra une fois le dépôt public archivé.
- Pour l'option instantané, ce même SWHID `dir` du répertoire publié sert d'empreinte.
- **Horodater avant de réécrire** : lancer `ots stamp` sur un fichier listant les anciens IDs de commit et les hachages de trees publics, ou poser un tag signé et horodaté sur l'ancien historique, puis le conserver hors dépôt. Une fois la preuve ancrée dans Bitcoin, on peut montrer que ces hachages existaient à cette date.
- Rappel : le dépôt Zenodo du 04/11/2030 sous embargo (commit `8c09578`) est déjà un ancrage daté tiers, si son contenu inclut des hachages.
- **Bundle chiffré** : `git bundle create full.bundle --all`, puis chiffrement (age ou gpg) et dépôt (Zenodo restreint, coffre). On publie le SHA-256 du fichier chiffré et le SHA-1 des pointes. On peut ensuite révéler la clé à un évaluateur, qui contrôle avec `git bundle verify` et retrouve les anciens IDs. C'est la seule voie qui permet une vérification **complète** de la commit-map sans publication. Cette procédure n'a pas été vérifiée dans une source pendant cette recherche.
- SHA-1 : git utilise SHA-1 avec détection de collisions, et la spec SWHID v1.2 repose sur SHA1. Pour un horodatage durable, mieux vaut horodater aussi un SHA-256 de l'archive. C'est une inférence, non sourcée ici.

### Gaps
- Je n'ai pas trouvé de source officielle sur une option OpenTimestamps qui re-hacherait les trees en SHA-256 (souvenir d'un `--rehash-trees`, non confirmé).
- Aucune source officielle ne mentionne un embargo ou un dépôt privé chez Software Heritage.
- Le statut de maintenance d'opentimestamps-client en 2026 n'a pas été vérifié.

## Q3. Risques de fuite résiduelle après réécriture, et comment vérifier la propreté

### Takeaway
Les anciens objets survivent dans les reflogs, les objets non référencés ou empaquetés, les stashes, les autres refs (branches, tags, `refs/original`, `refs/replace`, notes), les clones et les copies de sauvegarde. Le dépôt n'a jamais été poussé, donc forks, caches de PR et refs GitHub sont hors sujet. Le plus sûr est de publier depuis un **clone neuf** du dépôt filtré, puis de scanner tous les objets.

### Cited Findings
- Après réécriture, filter-repo exécute `git reset --hard`, `git reflog expire --expire=now --all` (« Reflogs will hold on to old history »), puis `git gc --prune=now` (« to avoid mixing new and old history »). Il supprime aussi le remote `origin`. — [man git-filter-repo](https://man.archlinux.org/man/git-filter-repo.1.en) ; [Documentation filter-repo](https://raw.githubusercontent.com/newren/git-filter-repo/main/Documentation/git-filter-repo.txt)
- filter-repo exige un « fresh clone », qu'il juge « an imperfect but quite reasonable proxy ». `--force` passe outre, mais « It is a really bad idea to get in the habit of always specifying --force ». Pour cloner depuis le disque local, il faut passer `--no-local`. — [man git-filter-repo](https://man.archlinux.org/man/git-filter-repo.1.en)
- `--sensitive-data-removal` récupère toutes les refs (y compris hors branches et tags), signale les premiers commits modifiés et les objets LFS orphelins. `--no-fetch` saute ce fetch, avec l'avertissement que le fetch « may discard » des changements locaux non poussés. — [Documentation filter-repo](https://raw.githubusercontent.com/newren/git-filter-repo/main/Documentation/git-filter-repo.txt)
- Pour un dépôt hébergé, GitHub liste les risques suivants :
  - recontamination par un collaborateur qui pull puis push ;
  - données toujours accessibles dans les forks, les clones, les PR et les « cached views » via leur SHA ;
  - signatures perdues ;
  - anciens clones qui « mènent » aux données retirées ;
  - nettoyage serveur (PR, gc, caches) faisable seulement par le support GitHub.

  — [GitHub Docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- BFG recommande d'exécuter ensuite `git reflog expire --expire=now --all && git gc --prune=now --aggressive`. — [BFG](https://rtyley.github.io/bfg-repo-cleaner/)
- Gitleaks : `gitleaks git <chemin>` scanne l'historique via `git log -p`, avec `--log-opts` transmis à git log (exemple : `--log-opts="--all"`). `gitleaks dir <chemin>` scanne un répertoire. Le format de rapport se choisit avec `-f json|csv|junit|sarif|template` et le fichier avec `-r <fichier>`. La commande `detect` est dépréciée depuis la v8.19.0. Le projet se dit « feature complete », et seuls des correctifs de sécurité sont prévus. — [gitleaks README](https://github.com/gitleaks/gitleaks)
- TruffleHog : `trufflehog git file://<repo> --results=verified,unknown` clone d'abord le dépôt dans un répertoire temporaire, sauf avec `--trust-local-git-config`. `trufflehog filesystem <dir>` scanne un répertoire. La vérification teste la validité des secrets contre les API des services, et `--no-verification` la désactive. — [TruffleHog README](https://github.com/trufflesecurity/trufflehog)

### Inferences
- Le dépôt n'a jamais été poussé. Les vecteurs propres à GitHub (forks, `refs/pull/*`, vues en cache, support) **ne s'appliquent pas**. Restent les copies locales :
  - le dépôt d'origine lui-même, à garder privé et à ne jamais pousser vers le remote public ;
  - les sauvegardes, Time Machine et worktrees ;
  - les clones pris par des agents.
- Un nouveau remote ne doit recevoir **que** le clone filtré.
- `--no-fetch` est pertinent sans remote : il n'y a rien à récupérer, et on évite tout effet de bord.
- Une branche, un tag ou un stash oubliés porteraient l'ancien historique. Il faut donc filtrer **toutes** les refs, ce que filter-repo fait par défaut sur toutes les refs. Il faut aussi vérifier `git stash list` et `git for-each-ref` avant et après.
- Contrôle de propreté indépendant de l'état du dépôt de travail :
  1. faire un clone neuf (`git clone --no-local`) ou un `--mirror` du dépôt filtré ;
  2. dans ce clone, vérifier qu'aucun chemin interdit n'apparaît dans les objets (`rev-list --all --objects | grep`) ;
  3. scanner les secrets avec gitleaks et trufflehog ;
  4. contrôler les messages de commit, qui ne sont pas filtrés par `--invert-paths` et peuvent contenir des noms ou des extraits (ici, « notes privées »). Au besoin, utiliser `--message-callback` ou `--replace-message`.
- Les métadonnées d'auteur (nom, e-mail) restent dans tous les commits. Si c'est un problème, utiliser un `.mailmap` avec `--use-mailmap`, ou `--name-callback` / `--email-callback`.
- Les noms de fichiers retirés n'apparaissent plus dans les trees, mais ils peuvent figurer dans des messages de commit ou dans des fichiers publics (README, notes) qui les citent.

### Gaps
- gitleaks et trufflehog (mode `git`) ne documentent pas clairement s'ils couvrent par défaut toutes les refs ou seulement HEAD. Côté gitleaks, il faut passer explicitement `--log-opts="--all"`.

## Q4. Commandes recommandées (historique nettoyé et option instantané)

### Takeaway
Pour l'historique nettoyé : analyser, filtrer dans un clone neuf, vérifier dans un second clone neuf, scanner, puis publier vers un remote vierge. Pour l'instantané : `git archive` d'un commit, puis un manifeste SHA-256 par fichier et un SWHID `dir`. Ne jamais prendre comme empreinte le hachage d'un `.tar.gz`, dont la stabilité n'est pas garantie.

### Cited Findings
- `git filter-repo --analyze` ne modifie pas le dépôt. Il écrit des rapports dans `.git/filter-repo/analysis/` (chemins, renommages, tailles par chemin, répertoire, extension et blob ; par exemple `path-deleted-sizes.txt`). — [Documentation filter-repo](https://raw.githubusercontent.com/newren/git-filter-repo/main/Documentation/git-filter-repo.txt)
- `--path` désigne des chemins exacts (fichier ou répertoire). `--path-glob` accepte des globs, et `--invert-paths` inverse la sélection. Un fichier déplacé ou renommé exige un `--path` par ancien chemin. — [Documentation filter-repo](https://raw.githubusercontent.com/newren/git-filter-repo/main/Documentation/git-filter-repo.txt) ; [GitHub Docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- Commande documentée par GitHub : `git-filter-repo --sensitive-data-removal --invert-paths --path PATH`. Repérer `NOTE: First Changed Commit(s)` dans la sortie. — [GitHub Docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- Depuis Git 2.38, `git archive` compresse le `.tar.gz` en interne au lieu d'appeler `gzip`. Le tar non compressé reste identique, mais le gzip diffère, donc la somme de contrôle change. GitHub a dû annuler son changement du 30/01/2023. Il ne garantissait la stabilité de ses archives que pendant au moins un an à partir du 21/02/2023, et conseille d'attacher les archives aux Releases. — [GitHub Changelog 30/01/2023](https://github.blog/changelog/2023-01-30-git-archive-checksums-may-change/) ; [GitHub Blog 21/02/2023](https://github.blog/open-source/git/update-on-the-future-stability-of-source-code-archives-and-hashes/) ; [LWN](https://lwn.net/Articles/921787)
- Le hachage d'un tree est vérifiable par n'importe qui avec `swh identify --verify`. — [SWH CLI](https://docs.softwareheritage.org/devel/swh-model/cli.html)

### Inferences — procédure proposée (non exécutée, à adapter ; chemins à confirmer avec `--analyze`)
```bash
# 0. Ancrer AVANT réécriture (dans le dépôt d'origine, lecture seule)
for c in <commits cités>; do
  printf '%s %s %s\n' "$c" "$(git rev-parse $c^{tree})" "$(git rev-parse $c:simulation)"
done > ancres-avant.txt
git bundle create ../historique-complet.bundle --all     # puis chiffrer : age -r <clé> ...
ots stamp ancres-avant.txt                                # OpenTimestamps (optionnel)

# 1. Clone neuf de travail (jamais le dépôt d'origine)
git clone --no-local /chemin/autonomie-meritee /tmp/am-filtre && cd /tmp/am-filtre
git filter-repo --analyze            # lire .git/filter-repo/analysis/path-*.txt
git stash list; git for-each-ref     # rien d'inattendu

# 2. Filtrer (un --path par chemin et par ancien nom)
git filter-repo --invert-paths \
  --path donnees/ --path notes-privees/ --path-glob '*.secret' \
  --no-fetch          # pas de remote ; ou --sensitive-data-removal --no-fetch
# Garder .git/filter-repo/{commit-map,ref-map,first-changed-commits} HORS du dépôt publié

# 3. Vérifier dans un SECOND clone neuf
git clone --no-local /tmp/am-filtre /tmp/am-verif && cd /tmp/am-verif
git rev-list --all --objects | grep -E '^[0-9a-f]+ (donnees/|notes-privees/)' && echo FUITE
git log --all --format='%H %s%n%b' | grep -iE 'donnees|privé'      # messages
gitleaks git . --log-opts="--all" -r gitleaks.json -f json
trufflehog git file://$PWD --results=verified,unknown
# Ancres : chaque tree public doit être identique
while read old _ t; do new=$(awk -v o=$old '$1==o{print $2}' commit-map)
  [ "$(git rev-parse $new:simulation)" = "$t" ] || echo "DIVERGE $old"; done < ancres-avant.txt

# 4. Publier : remote VIERGE, seulement les refs voulues
git remote add public <url> && git push public main --tags
```
Option instantané :
```bash
git archive --format=tar --prefix=autonomie-meritee/ <commit> -- simulation reports ... > snapshot.tar
# Empreinte stable : manifeste par fichier, pas le .tar.gz
mkdir s && tar -xf snapshot.tar -C s && cd s
find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > ../MANIFEST.sha256
swh identify --no-filename autonomie-meritee     # SWHID dir == git rev-parse <commit>:<chemin> si même sélection
git rev-parse <commit>:simulation                 # à publier avec le commit privé cité
```
- `git archive <commit> -- <chemins>` ne copie que les chemins choisis, et le tar ne contient pas de `.git`. Attention toutefois aux attributs `export-ignore` et `export-subst` de `.gitattributes`, qui modifient le contenu archivé. Dans ce cas, le SWHID du répertoire extrait peut différer du tree git.
- Le tar non compressé contient l'ID du commit dans un en-tête pax global (`git get-tar-commit-id`). C'est bien pour la traçabilité, mais cela **révèle l'ID privé**, ce qui est voulu si l'on veut le citer.
- Instantané ou historique nettoyé : le hachage du tree d'un sous-répertoire public est identique dans les deux cas. C'est ce point commun qui rend les deux options vérifiables de la même façon pour les fichiers publics. Seul l'historique nettoyé montre en plus la chronologie, avec des IDs de commit nouveaux.

### Gaps
- Les commandes ci-dessus ont été assemblées à partir des docs et n'ont pas été testées (consigne : ne rien exécuter). Les noms de chemins (`notes-privees/`, etc.) sont des exemples à remplacer par le résultat de `--analyze` et par l'inventaire T44/T45.
- Je n'ai pas vérifié si Git a rétabli `gzip` externe par défaut pour `git archive` après 2023. Il faut donc s'appuyer sur un manifeste par fichier ou un tar non compressé.
