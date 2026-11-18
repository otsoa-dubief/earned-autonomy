# Publier l'instantané, garder l'historique sous scellé

> **Résumé en cinq lignes**
> 1. Recommandation : option (a). Publier un **instantané propre sans historique**, accompagné de ses empreintes, et y ajouter trois éléments de l'option (c).
> 2. Ces trois éléments : une **table qui relie chaque commit cité à l'empreinte des dossiers publics**, un **bundle chiffré de l'historique complet** déposé en accès restreint, et un horodatage OpenTimestamps facultatif.
> 3. L'option (b) est à écarter. Les fichiers interdits sont présents dès le premier commit, donc la réécriture **change l'identifiant des 214 commits** : aucun identifiant cité sur OSF ne se retrouverait dans le dépôt publié.
> 4. Aucune revue ni aucun cadre (PLOS, Springer Nature, TOP 2025) n'exige l'historique git. Tous demandent une **version figée, déposée et citée**. La preuve d'antériorité vient de l'horodatage OSF, pas des dates de commit, que l'on peut falsifier.
> 5. Point à vérifier d'urgence : le manifeste de 68 990 fichiers, figé sur OSF, deviendra public à la levée de l'embargo. Il faut contrôler **ce qu'il révèle sur les fichiers retenus** (noms, empreintes de petits fichiers).

Le chercheur doit concilier deux exigences. Il veut publier code et données sur GitHub et Zenodo. Il doit aussi permettre à n'importe qui de vérifier que ce qu'il publie correspond à ce qu'il a déclaré sur OSF : des identifiants de commits, une étiquette de gel et des empreintes SHA-256. Une « empreinte » (ou hash) est une suite de caractères calculée à partir du contenu d'un fichier : elle change dès qu'un seul octet change. La bonne réponse découle d'un fait technique simple. **Git identifie un commit par une empreinte qui inclut celle de son parent.** Toucher le premier commit revient donc à changer l'identité de tous les suivants. Les empreintes des fichiers et des dossiers non modifiés, elles, restent identiques quelle que soit l'option choisie. Le rapport montre pourquoi l'instantané l'emporte, comment rendre les commits cités vérifiables sans rien révéler, quelles commandes lancer (non testées), et quoi écrire dans le README.

## Réécrire l'historique change l'identité des 214 commits

Dans git, chaque objet porte un nom calculé à partir de son contenu. Un fichier (un « blob ») est identifié par l'empreinte de ses octets, sans tenir compte de son nom ni de son emplacement. Un dossier (un « tree ») est identifié par la liste de ses entrées (nom, droits, empreinte de chaque élément). Un commit est identifié par l'empreinte du dossier racine, de ses parents, de l'auteur, des dates et du message ([Git Book](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)). Le manuel de git filter-repo en tire la conséquence : l'identifiant d'un commit change même s'il n'a pas été modifié, car **« the fact that you changed any of its ancestors is also a change that counts »** ([man git-filter-repo](https://man.archlinux.org/man/git-filter-repo.1.en)).

Ici, les fichiers interdits figurent dès le premier commit. Le dossier racine de ce commit change donc, son identifiant aussi, puis celui de chacun des 213 commits suivants. **Tout identifiant de commit cité sur OSF pointerait vers un commit qui n'existe pas dans le dépôt publié.** L'étiquette du gel serait elle aussi déplacée vers un nouveau commit. Si elle était signée, sa signature disparaîtrait, car filter-repo transforme un tag signé en simple tag annoté ([man git-filter-repo](https://man.archlinux.org/man/git-filter-repo.1.en)). BFG se comporte de la même manière : il protège le contenu du dernier commit, mais pas son identifiant ([BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)).

filter-repo produit bien une table de correspondance, `commit-map`, qui associe chaque ancien identifiant au nouveau ([documentation filter-repo](https://raw.githubusercontent.com/newren/git-filter-repo/main/Documentation/git-filter-repo.txt)). Mais un tiers ne peut pas la vérifier. Pour recalculer un ancien identifiant, il lui faudrait l'ancien objet commit et l'ancien dossier racine. Ceux-ci révèlent les noms des fichiers privés et les messages de commit. Ils permettent aussi de confirmer par essais successifs le contenu d'un petit fichier devinable, par exemple une adresse. Publier cette table revient donc à dire « croyez-moi sur parole ». Une table publiée aujourd'hui ne prouve d'ailleurs rien sur la date de l'historique d'origine.

L'option (b) comporte aussi des risques de fuite. Les anciens objets survivent dans les reflogs, les branches oubliées, les stashes, les sauvegardes et les clones ([man git-filter-repo](https://man.archlinux.org/man/git-filter-repo.1.en)). Les messages des 214 commits ne sont pas filtrés par `--invert-paths` et peuvent citer des noms ou des extraits de notes. Le dépôt n'a jamais été poussé, ce qui écarte les forks et les caches de GitHub. Mais un historique publié par erreur ne se retire plus : Imperial College recommande de considérer comme exposée toute donnée qui a été publique ou clonée ([Imperial](https://imperialcollegelondon.github.io/docs/security/data_storage_guidelines)). Et Software Heritage moissonne les dépôts publics ([Di Cosmo, arXiv 2004.00514](https://arxiv.org/pdf/2004.00514)).

L'argument le plus fort en faveur de (b) est qu'il montre la chronologie : ce qui a changé après l'enregistrement, les essais, les écarts. Cette information a de la valeur. Elle ne justifie pourtant pas le risque, pour deux raisons. Les dates de commit se fixent à volonté, donc l'historique ne prouve rien que l'auteur n'aurait pu fabriquer ([Checkmarx](https://checkmarx.com/blog/unverified-commits-are-you-unknowingly-trusting-attackers-code/)). Et un journal des écarts au plan, rédigé dans le README, transmet la même information sous une forme lisible. Surtout, **(a) est réversible et (b) ne l'est pas**. Avec le bundle chiffré conservé, on pourra toujours publier plus tard un historique nettoyé si un relecteur l'exige, alors qu'une fuite ne se rattrape pas.

## Les revues demandent une version figée et citée, jamais l'historique

Les politiques en vigueur fin 2026 raisonnent toutes en « version déposée ». Springer Nature exige que le code soit placé dans un dépôt qui attribue un identifiant permanent, comme Zenodo, et précise que **« providing a GitHub link only is not sufficient »**. Quand le partage est impossible, la disponibilité et les conditions d'accès doivent quand même être déclarées ([Springer Nature](https://springernature.com/gp/open-science/code-policy)). PLOS Biology impose depuis le 1er janvier 2026 d'archiver un **instantané** dans un dépôt pérenne et de citer à la fois cet instantané et la version vivante ([PLOS Biology](https://journals.plos.org/plosbiology/s/code-availability)). Le guide de partage du code de PLOS ne dit rien de l'historique git ([PLOS Code Sharing Guidance](https://journals.plos.org/plosbiology/s/code-sharing-guidance)). Le cadre TOP 2025 du COS demande, pour l'enregistrement d'une étude, d'indiquer **« où et quand »** elle a été enregistrée, et, pour le code, qu'il soit cité dans un « trusted repository » ([COS TOP](https://www.cos.io/initiatives/top-guidelines)).

La preuve d'antériorité reconnue est l'horodatage par un tiers. Une registration OSF est « a frozen version of your project that can never be edited or deleted », datée du jour de sa soumission ([OSF Help](https://help.osf.io/article/158-create-a-preregistration)). Des préprints de 2026 qui s'appuient sur l'historique de leur dépôt le jugent eux-mêmes **« weaker than an external registration »** ([arXiv 2608.12895](https://arxiv.org/pdf/2608.12895), non relu par des pairs). Aucune politique ni enquête trouvée n'indique que des relecteurs d'études préenregistrées demandent l'historique git. Aucun exemple vérifié de Registered Report ayant publié un historique réécrit n'a été trouvé non plus. Le modèle documenté dans la pratique est le **dossier de réplication** des éditeurs de données en économie (AEA, REStud) : un instantané du code, accompagné d'un README qui dit ce qui est fourni, ce qui ne l'est pas et pourquoi ([SSDE template README](https://social-science-data-editors.github.io/template_README)).

## Les empreintes de dossiers relient les commits cités à l'instantané

L'instantané est vérifiable grâce à une propriété de git : **un dossier qui ne contient aucun fichier retiré garde exactement la même empreinte de dossier**, dans un historique réécrit comme dans un instantané. La commande `git rev-parse <commit>:simulation` donne la même valeur dans le dépôt de travail et dans le dépôt publié, à condition que le contenu du dossier soit identique. Cette empreinte n'est pas propre à git. C'est aussi un identifiant Software Heritage de type `swh:1:dir:`, normalisé ISO/IEC 18670:2025 ([spécification SWHID v1.2](https://www.swhid.org/specification/v1.2/5.Core_identifiers/) ; [ISO](https://www.iso.org/standard/89985.html)). N'importe qui peut le recalculer sur sa machine avec `swh identify`, et l'option `--verify` permet de le comparer à une valeur attendue ([SWH CLI](https://docs.softwareheritage.org/devel/swh-model/cli.html)).

La solution retenue combine plusieurs ancres. Le tableau indique ce que chacune prouve et à qui.

| Élément | Ce qu'il prouve | Qui peut vérifier |
|---|---|---|
| Registration OSF (déjà faite) | La date du plan, des identifiants de commits et des empreintes | Tout le monde, à la levée de l'embargo |
| Manifeste SHA-256 publié, comparé au manifeste OSF | Chaque fichier publié est identique octet pour octet à celui déclaré | Tout le monde |
| Table « commit cité → empreinte des dossiers publics » | Le dossier publié est exactement celui du commit cité | Tout le monde (git ou `swh identify`) |
| Étiquette de gel → commit cité | L'instantané est issu du commit gelé | Tout le monde, via l'en-tête du tar (`git get-tar-commit-id`) |
| Bundle chiffré de l'historique complet | La table de correspondance complète, l'intégralité des 214 commits | Un évaluateur à qui l'on confie la clé |
| OpenTimestamps (facultatif) | Que la table et l'empreinte du bundle existaient à une date donnée | Tout le monde, via la blockchain Bitcoin |
| Zenodo + Software Heritage | La pérennité et un identifiant citable (DOI, SWHID) | Tout le monde |

Le bundle chiffré est la seule voie qui permet une vérification **complète** sans rien publier. Il s'agit de l'historique entier dans un seul fichier, chiffré, dont seule l'empreinte est publique. Le jour où un relecteur reçoit la clé, `git bundle verify` lui permet de retrouver les anciens identifiants. Cette procédure n'a pas été trouvée décrite dans une source : c'est une construction à partir des outils git standard. OpenTimestamps ancre une empreinte dans Bitcoin, ce qui prend quelques heures ; avant cet ancrage, la preuve dépend des serveurs calendrier ([opentimestamps-client](https://github.com/opentimestamps/opentimestamps-client/blob/master/doc/git-integration.md)). Il est facultatif, car la registration OSF et le dépôt Zenodo sous embargo jouent déjà le rôle d'ancres datées par un tiers. Software Heritage n'archive que du public : Save Code Now est réservé aux dépôts publics ([SWH FAQ](https://docs.softwareheritage.org/user/faq/)). Un enregistrement Zenodo créé depuis GitHub est archivé chez Software Heritage automatiquement ([Zenodo help](https://help.zenodo.org/docs/github/archive-software/github-upload/)).

Deux limites sont à connaître. Si un dossier public contient ne serait-ce qu'un fichier retiré, par exemple une sortie de pilote rangée dans `simulation/`, son empreinte de dossier change. On s'appuie alors sur les empreintes SHA-256 fichier par fichier du manifeste. Ensuite, si OSF cite plusieurs commits successifs, l'instantané du seul gel ne permet de vérifier que le gel. La parade consiste à créer dans le dépôt public **un commit par version citée**, et rien d'autre : c'est un « historique des seules versions citées ». Chaque dossier public y garde l'empreinte qu'il avait dans le commit d'origine. Cette variante est une déduction, non trouvée dans les sources.

**Point d'attention sur le manifeste OSF.** Une registration OSF ne peut être ni modifiée ni supprimée, seulement retirée ([OSF Help](https://help.osf.io/article/158-create-a-preregistration)). Si le manifeste de 68 990 fichiers liste aussi les fichiers retenus, il publiera à la levée de l'embargo leurs **noms** et leurs **empreintes**. Un nom de fichier peut contenir le nom d'un tiers. L'empreinte d'un très petit fichier (une adresse, un code) peut être confirmée par essais successifs. Il faut le vérifier maintenant, tant qu'il reste du temps pour décider d'une éventuelle mention dans le README. Les empreintes des paquets zip ne sont vérifiables que si l'on publie **exactement ces fichiers zip**, et non des archives régénérées. Une archive `.tar.gz` recréée n'a pas forcément la même empreinte : GitHub a dû annuler en 2023 un changement qui modifiait les sommes de contrôle de ses archives ([GitHub Blog](https://github.blog/open-source/git/update-on-the-future-stability-of-source-code-archives-and-hashes/)). Un zip qui contient des données confidentielles reste dans le dépôt restreint.

## Les commandes de l'option retenue (non testées)

**Avertissement : ces commandes ont été assemblées à partir de la documentation et n'ont pas été exécutées.** Les chemins (`code`, `simulation`, `analyses`…) sont des exemples. Il faut les remplacer par l'inventaire des fichiers publiables, et tout lancer d'abord sur une copie. Le dépôt de travail n'est jamais modifié ni poussé. On suppose deux fichiers texte préparés à la main : `commits-cites.txt`, qui liste un identifiant par ligne dans l'ordre chronologique avec l'étiquette du gel en dernier, et `dossiers-publics.txt`, qui liste un dossier par ligne.

**Étape 1 — Relever les ancres dans le dépôt de travail (lecture seule).**

```bash
cd /chemin/depot-travail
git status --short; git stash list; git for-each-ref     # rien d'inattendu

# L'étiquette du gel désigne-t-elle bien le commit cité sur OSF ?
git cat-file -t <etiquette-gel>                # "tag" (annotée) ou "commit" (légère)
git rev-parse <etiquette-gel>^{commit}         # doit égaler l'identifiant cité sur OSF

# Table : commit cité -> empreinte de chaque dossier public
while read c; do
  while read d; do
    t=$(git rev-parse --verify -q "$c:$d" || echo ABSENT)
    printf '%s\t%s\t%s\n' "$c" "$d" "$t"
  done < dossiers-publics.txt
done < commits-cites.txt > ../ancres-commits.tsv
```

**Étape 2 — Mettre l'historique complet sous scellé.**

```bash
git bundle create ../historique-complet.bundle --all
git bundle verify ../historique-complet.bundle
age -p -o ../historique-complet.bundle.age ../historique-complet.bundle
#   (variante : gpg --symmetric --cipher-algo AES256 ../historique-complet.bundle)
shasum -a 256 ../historique-complet.bundle.age > ../empreinte-bundle.sha256
git for-each-ref --format='%(objectname) %(refname)' > ../pointes-historique.txt

# Facultatif : horodatage OpenTimestamps
ots stamp ../ancres-commits.tsv ../empreinte-bundle.sha256
#   quelques heures plus tard : ots upgrade <fichier>.ots ; ots verify <fichier>.ots
```

On conserve `historique-complet.bundle.age` hors ligne et dans un dépôt Zenodo en accès restreint. La phrase de passe est stockée séparément. On supprime ensuite le bundle en clair.

**Étape 3 — Extraire l'instantané du commit gelé.** On vérifie d'abord que `.gitattributes` ne contient ni `export-ignore` ni `export-subst`, qui modifieraient le contenu archivé.

```bash
git archive --format=tar --prefix=publication/ <etiquette-gel> code simulation analyses > ../instantane.tar
git get-tar-commit-id < ../instantane.tar      # affiche l'identifiant du commit gelé
mkdir ../publi && tar -xf ../instantane.tar -C ../publi
```

**Étape 4 — Construire le manifeste et le comparer au manifeste OSF.** La comparaison suppose que le manifeste OSF suit le même format (`empreinte  ./chemin`) et la même racine. Sinon, il faut l'adapter.

```bash
cd ../publi/publication
find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > ../MANIFEST.sha256
shasum -a 256 -c /chemin/manifeste-osf.sha256 > ../verif-osf.txt 2>&1
grep -c ': OK$' ../verif-osf.txt               # nombre de fichiers publiés vérifiés
grep ': FAILED$' ../verif-osf.txt              # DOIT être vide (fichier publié mais modifié)
grep -c 'FAILED open or read' ../verif-osf.txt # fichiers retenus, non publiés : nombre attendu
```

**Étape 5 — Contrôler la propreté avant toute mise en ligne.**

```bash
gitleaks dir . -r ../gitleaks.json -f json
trufflehog filesystem . --results=verified,unknown
grep -rEn '[[:alnum:]._%+-]+@[[:alnum:].-]+\.[a-z]{2,}' . | less          # adresses e-mail
grep -rniE 'donnees|terrain|pilote|scell|notes' . | less                   # mots révélateurs, à adapter
```

Gitleaks et TruffleHog sont documentés pour scanner un répertoire ([gitleaks](https://github.com/gitleaks/gitleaks) ; [TruffleHog](https://github.com/trufflesecurity/trufflehog)). Ils cherchent des clés et des mots de passe, pas des adresses postales de tiers. Une relecture humaine des fichiers publics reste donc indispensable.

**Étape 6 — Créer le dépôt public, sans historique, et vérifier les ancres.**

```bash
cd ../publi/publication
git init -b main
git -c core.autocrlf=false add -A
git commit -m "Instantané public issu de l'étiquette <etiquette-gel> (commit de travail <id>)"
while IFS=$'\t' read c d t; do
  [ "$c" = "<id-du-gel>" ] || continue
  [ "$(git rev-parse -q --verify "HEAD:$d")" = "$t" ] && echo "OK $d" || echo "DIVERGE $d"
done < ../../ancres-commits.tsv
pip install 'swh.model[cli]'; swh identify simulation   # = swh:1:dir:<même empreinte>
```

Un `DIVERGE` signale un dossier qui contenait un fichier retiré, ou des réglages de fin de ligne ou de droits différents. Dans ce cas, on s'en remet au manifeste fichier par fichier.

Si OSF cite plusieurs commits, on applique la variante « un commit par version citée » à la place de l'étape 6. Un `git archive` échouera si un dossier n'existe pas encore dans un commit ancien : la liste est alors à ajuster par commit.

```bash
mkdir ../public && cd ../public && git init -b main
while read c; do
  find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
  git -C /chemin/depot-travail archive --format=tar "$c" code simulation analyses | tar -xf -
  git -c core.autocrlf=false add -A
  git commit -q -m "Version publique du commit de travail $c ($(git -C /chemin/depot-travail log -1 --format=%as "$c"))"
  git tag "travail-${c:0:7}"
done < ../commits-cites.txt
```

**Étape 7 — Publier.** On ajoute `README.md`, `LICENSE`, `MANIFEST.sha256`, `ancres-commits.tsv` et `empreinte-bundle.sha256`, puis on fait un commit. On crée un dépôt GitHub **vide**, on y pousse ce dépôt, et l'on publie une release : Zenodo émet un DOI à chaque release, à condition que le dépôt soit public ([GitHub Docs](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content)). Les paquets zip déjà déclarés sur OSF, s'ils sont publiables, sont joints tels quels à la release, sans être régénérés. Les données publiables (hors terrain confidentiel) vont soit dans l'instantané, soit dans un enregistrement Zenodo distinct qui renvoie au DOI du code.

```bash
git remote add public git@github.com:<compte>/<depot>.git
git push public main --tags
```

## Ce que le README doit déclarer

Le consensus des sources est clair : on déclare toujours ce qui existe, où il se trouve et à quelles conditions on y accède, même quand rien n'est partagé ([Springer Nature](https://springernature.com/gp/open-science/code-policy) ; [PLOS Comp Biol](https://journals.plos.org/ploscompbiol/s/code-availability) ; [COS TOP](https://www.cos.io/initiatives/top-guidelines)). Le modèle SSDE découpe le README en trois parties : disponibilité des données et du code, besoins informatiques, instructions ([SSDE](https://social-science-data-editors.github.io/template_README)). Le gabarit ci-dessous l'adapte au cas présent. Les données synthétiques, générées pour imiter les vraies sans en contenir, sont une solution reconnue pour permettre de faire tourner le code sans les données de terrain ([Quintana, eLife](https://elifesciences.org/articles/53275v1)).

```markdown
## Provenance de cette publication

Ce dépôt est un **instantané** du dépôt de travail de l'étude, tiré de
l'étiquette `<etiquette-gel>` (commit de travail `<id>`, <date>). L'historique
de travail (214 commits) n'est pas publié, car il contient dès son premier
commit des fichiers qui ne peuvent pas l'être (voir plus bas). Le contenu
publié est identique, octet pour octet, aux fichiers correspondants du commit gelé.

Préenregistrement : OSF <DOI ou lien>, déposé le <date>.
Dépôt des résultats : Zenodo 10.5281/zenodo.<n>.

## Ce qui n'est pas publié, et pourquoi

| Catégorie | Motif | Accès |
|---|---|---|
| Fichier scellé | <motif> | <conditions / date prévue> |
| Données de terrain | Confidentialité des participants | Sur demande motivée à <contact>, après <accord> |
| Notes personnelles | Sans valeur pour la reproduction | Non disponible |
| Coordonnées de tiers | Vie privée | Non disponible |
| Sorties du pilote | <motif> | <conditions> |

Le manifeste OSF compte 68 990 fichiers ; <N> sont publiés ici, <M> sont retenus.
Des données synthétiques (`donnees-synthetiques/`) permettent d'exécuter le code
de bout en bout ; elles ne reproduisent pas les résultats chiffrés.

## Comment vérifier la correspondance avec les dépôts OSF

1. Fichiers : depuis la racine, `shasum -a 256 -c MANIFEST.sha256`. Chaque ligne
   de ce manifeste figure à l'identique dans le manifeste déposé sur OSF.
2. Commits cités : `ancres-commits.tsv` donne, pour chaque commit cité sur OSF,
   l'empreinte git de chaque dossier public. `git rev-parse <tag>:<dossier>`
   dans ce dépôt, ou `swh identify <dossier>`, doit redonner la même valeur.
3. Paquets zip : les fichiers joints à la release sont ceux déposés sur OSF ;
   comparer leur SHA-256 aux valeurs OSF.

## Historique de travail sous scellé

L'historique complet est conservé dans un bundle git chiffré, déposé en accès
restreint sur Zenodo (<lien>). SHA-256 du fichier chiffré : `<empreinte>`
(voir `empreinte-bundle.sha256`, horodaté par OpenTimestamps le <date>).
Sur demande d'un éditeur ou d'un relecteur, la clé peut être confiée pour une
vérification complète des identifiants de commits cités.

## Écarts au préenregistrement

<Liste datée des écarts au plan, avec leur justification.>
```

## Conclusion

La décision ne tient pas d'abord à l'outil choisi. Elle tient à ce qui fait preuve. Les identifiants de commits cités sur OSF ne survivent à aucune réécriture, alors que les empreintes de fichiers et de dossiers survivent à toutes. Mieux vaut donc publier l'objet qui porte ces empreintes intactes, et garder sous scellé ce qui ne peut ni être montré ni être vérifié par un tiers. Ce choix laisse aussi toutes les portes ouvertes : le bundle chiffré permet de produire plus tard un historique nettoyé, alors qu'un historique publié ne se retire plus.

Deux tâches comptent davantage que les commandes. La première est de vérifier dès maintenant ce que le manifeste OSF figé révélera à la levée de l'embargo. La seconde est de relire à la main les fichiers publics pour y chercher des coordonnées de tiers, ce qu'aucun scanner de secrets ne sait faire. Pour la suite, il faut retenir que le préenregistrement ne doit pas citer un identifiant de commit seul. Il est plus solide de citer aussi l'empreinte du dossier analysé, car c'est elle qui reste vérifiable.
