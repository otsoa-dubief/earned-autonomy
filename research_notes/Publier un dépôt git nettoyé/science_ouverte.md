# Science ouverte : publier code et données d'une étude préenregistrée quand le dépôt de travail contient du non-publiable (état fin 2026)

Recherche web du 17/11/2026. 16 appels outils. Plusieurs pages primaires étaient inaccessibles (page Turing Way « exposing data » en 404, doc Software Heritage derrière un anti-bot Anubis, page DCAS restricted data en 404) : ce qu'elles disent est rapporté d'après les extraits de recherche et signalé comme tel.

## Q1. Que recommandent les guides de référence (Turing Way, rOpenSci, COS/OSF, Software Heritage, Zenodo/GitHub, revues) sur l'historique, les données sensibles et l'archivage d'un instantané avec DOI ?

### Takeaway
Les politiques actuelles (Springer Nature, PLOS 2026, TOP 2025, NeurIPS) demandent toutes la même chose : un **instantané versionné, déposé dans un dépôt pérenne avec identifiant persistant (DOI/SWHID), et cité**. Aucune n'exige l'historique git complet. Les guides git (Turing Way, GitHub) traitent la réécriture d'historique comme une opération de rattrapage risquée, pas comme une méthode de publication.

### Cited Findings
**Revues et cadres de politique**
- Springer Nature / Nature Portfolio : déclaration de disponibilité du code obligatoire pour tout article de recherche qui développe du code nécessaire. Le code doit aller dans un dépôt qui attribue un identifiant permanent (Code Ocean, Zenodo) et être cité en références. « providing a GitHub link only is not sufficient ». Quand le partage public est impossible (p. ex. données de participants), « Code availability should still be stated in the manuscript along with any conditions for access ». Les relecteurs peuvent exiger l'accès au code. — [Springer Nature code policy](https://springernature.com/gp/open-science/code-policy)
- PLOS Biology : politique de partage du code obligatoire pour toute soumission depuis le **1er janvier 2026**. Si le code est sur un dépôt non pérenne comme GitHub, il faut archiver un **instantané** dans un dépôt pérenne (Zenodo, Code Ocean, Software Heritage) et citer à la fois l'instantané archivé et la version vivante. Un code central qui ne peut pas être partagé peut motiver un rejet. — [PLOS Biology code availability](https://journals.plos.org/plosbiology/s/code-availability)
- PLOS Medicine : politique lancée le **22 avril 2026**. Les exemptions sont approuvées par un éditeur et doivent être demandées à la soumission. Dépôt avec DOI fortement recommandé. Une formulation provisoire est admise si le DOI n'est émis qu'à la publication. — [PLOS Medicine code availability](https://journals.plos.org/plosmedicine/s/code-availability)
- Guide PLOS de partage du code : indiquer **la version** du code partagé plus un lien vers le code vivant. README et LICENSE requis (pas de licence Creative Commons pour du code). Restriction expliquée dans la lettre d'accompagnement, puis voie d'accès décrite dans la Data Availability Statement (procédure de demande, contact nommé, dépôt à accès contrôlé). Le code n'a pas à être public pendant la relecture, mais doit être accessible aux relecteurs (lien privé). — [PLOS Biology Code Sharing Guidance](https://journals.plos.org/plosbiology/s/code-sharing-guidance)
- Le guide PLOS de partage du code ne dit rien de l'historique git. Il raisonne entièrement en « version partagée » plus « lien vivant ». — [PLOS Code Sharing Guidance](https://journals.plos.org/plosbiology/s/code-sharing-guidance)
- TOP 2025 (COS, article Grant et al. publié en 2026) : trois niveaux par pratique : Disclose / Share and Cite / Certify. *Study Registration*, niveau Disclose : « Authors stated whether or not a study was registered—and, if so, where and when it was registered » ; niveau Certify : une partie indépendante vérifie que l'enregistrement était opportun et complet. *Analysis Code Transparency*, niveau Share and Cite : code cité dans un « trusted repository ». Pratiques de vérification : *Results Transparency* (une partie indépendante vérifie l'absence de rapport sélectif) et *Computational Reproducibility*. — [COS TOP Guidelines](https://www.cos.io/initiatives/top-guidelines) ; structure confirmée par [Metascience 2025 panel](https://nomadit.co.uk/conference/metascience2025/p/16526)
- NeurIPS 2025 : le code et les données sont soumis **anonymisés**, en une seule archive zip en supplément, ou via une URL anonyme pour les gros jeux de données. — [NeurIPS Code Submission Policy](https://neurips.cc/public/guides/CodeSubmissionPolicy) ; [NeurIPS 2025 CfP](https://neurips.cc/Conferences/2025/CallForPapers)
- Item 5 de la checklist NeurIPS (« Open access to data and code ») : on peut répondre Oui, Non ou NA. « Non » est acceptable, sauf si le code est central à la contribution. On attend les commandes exactes et l'environnement d'exécution. (Source secondaire : checklist reproduite dans un article arXiv.) — [arXiv 2510.01303](https://arxiv.org/pdf/2510.01303)

**Archivage : OSF, Zenodo, Software Heritage**
- OSF : une registration est « a frozen version of your project that can never be edited or deleted ». On ne peut que la retirer, de façon irréversible, et il reste alors des métadonnées. Les fichiers du projet, y compris ceux des add-ons de stockage, sont archivés automatiquement jusqu'à 5 Go. Une registration publique reçoit automatiquement un DOI. L'embargo peut durer jusqu'à 4 ans, et le DOI n'est attribué qu'à la levée. Date de création = date de soumission, même si l'approbation vient plus tard. — [OSF Help : Create a preregistration](https://help.osf.io/article/158-create-a-preregistration) ; [OSF Registration FAQ](https://help.osf.io/category/549-registration-and-preregistration-faqs)
- GitHub/Zenodo : Zenodo archive le dépôt et émet un nouveau DOI **à chaque release GitHub**. Le dépôt doit être public. — [GitHub Docs : Referencing and citing content](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content)
- Avec l'intégration GitHub, on ne peut pas réserver le DOI à l'avance. Avec un dépôt manuel sur Zenodo, on peut. — [HKUST Library](https://library.hkust.edu.hk/news-events/news/github-repo-doi-ten-minutes-make-your-code-citable)
- La doc Zenodo actuelle indique qu'un enregistrement Software créé depuis GitHub est aussi archivé dans Software Heritage (champ « Archived in »). — [Zenodo help : GitHub upload](https://help.zenodo.org/docs/github/archive-software/github-upload/)
- Software Heritage : un SWHID est un identifiant **intrinsèque**, calculé à partir de l'objet lui-même : n'importe qui peut le recalculer localement avec `swh-identify`. Pour un objet `rev`, le hash est l'identifiant du commit git. L'identifiant d'un commit dépend de son arbre, de son parent et de ses métadonnées : réécrire un commit ancien change tous les identifiants qui suivent. Le schéma est normalisé ISO/IEC 18670. Pour la citation académique, on recommande souvent un SWHID de type **répertoire** (`dir`). — [Di Cosmo, arXiv 2004.00514](https://arxiv.org/pdf/2004.00514) ; [SWH citation docs](https://docs.softwareheritage.org/devel/architecture/citation.html) ; [SWHID docs](https://docs.softwareheritage.org/devel/swh-model/persistent-identifiers.html) (page bloquée par un anti-bot ; contenu tiré des extraits de recherche)

**Guides git et données sensibles**
- The Turing Way a une page « What do you do if you inadvertently expose sensitive data on GitHub? ». Elle avertit qu'il est plus difficile qu'on ne croit de retirer des données une fois exposées. Page complète en 404 au moment de la recherche. — [Turing Way, extrait](https://book.the-turing-way.org/project-design/sdpw/pd-sdp-exposing-data)
- The Turing Way, page « données et contrôle de version » : un fichier ajouté par erreur « needs to be purged ». Elle renvoie à la procédure GitHub de suppression des données sensibles. Avec git-annex, le contenu de l'annexe n'est pas poussé vers GitHub. — [Turing Way : vcs-data](https://book.the-turing-way.org/reproducible-research/vcs/vcs-data)
- GitHub : `git rm` ne retire pas un fichier de l'historique. La réécriture se fait avec git-filter-repo ou BFG, puis un force-push. Les clones existants gardent les données. — [GitHub Docs : removing sensitive data](https://docs.github.com/en/enterprise-server@3.18/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- Imperial College : si le dépôt a été public ou cloné, considérer les données comme exposées. — [Imperial data storage guidelines](https://imperialcollegelondon.github.io/docs/security/data_storage_guidelines)
- The Turing Way, chapitre contrôle de version : la VCS sert à tracer la provenance et à expliquer après coup pourquoi une analyse a été faite. — [Turing Way : Version Control](https://book.the-turing-way.org/reproducible-research/vcs)

### Inferences
- Les revues raisonnent en « version citée et figée » (release, DOI, SWHID), jamais en « historique complet ». Pour se conformer, un instantané propre avec DOI suffit (option a).
- Point technique : un historique réécrit change tous les hashes de commit, donc tous les SWHID `rev`. Tout hash de commit déjà cité ailleurs (préenregistrement, carnet) ne correspondra plus à rien dans le dépôt réécrit. Les hash de contenu (`cnt`) et d'arbre (`dir`) de fichiers inchangés restent identiques. C'est donc eux, ou un sha256 de fichier, qu'il faut utiliser comme preuve stable.
- Réécrire l'historique ne fait pas disparaître ce qui a déjà été poussé, cloné, ou archivé par Software Heritage, qui moissonne les dépôts publics. Le nettoyage doit précéder toute publication du dépôt.

### Gaps
- rOpenSci : rien trouvé de spécifique sur l'historique ou les données sensibles. Le guide « Packages » n'a pas été consulté, faute de budget.
- Page Turing Way « exposing data » non lue en entier (404) : les étapes précises qu'elle recommande restent non vérifiées.
- Contenu exact de l'archive Zenodo-GitHub (zip de l'arbre au tag, sans `.git`) : non confirmé par une doc primaire lue dans cette recherche.
- ICLR 2026 : checklist non consultée.

## Q2. L'historique git complet est-il attendu ou valorisé par les relecteurs d'études préenregistrées, ou un enregistrement horodaté plus des sommes de contrôle suffit-il ?

### Takeaway
La preuve reconnue d'un préenregistrement est l'**horodatage par un tiers** (registration OSF figée, datée, avec DOI). TOP 2025 demande de dire « où et quand ». Les dates de commit git sont falsifiables : un historique git ne vaut au mieux que preuve complémentaire, et les auteurs qui s'en servent le qualifient eux-mêmes de plus faible qu'un enregistrement externe. Les travaux « git comme carnet de labo » valorisent git pour la reproductibilité et la provenance, pas comme preuve d'antériorité.

### Cited Findings
- La registration OSF est un « time-stamped, read-only version of your study plan ». Elle n'est ni modifiable ni supprimable. — [OSF Help](https://help.osf.io/article/158-create-a-preregistration)
- TOP 2025, Study Registration, niveau Disclose : dire où et quand l'étude a été enregistrée. Niveau Certify : vérification indépendante que l'enregistrement était « timely and complete ». — [COS TOP](https://www.cos.io/initiatives/top-guidelines)
- Les dates de commit git peuvent être fixées arbitrairement : un commit peut sembler antérieur au dépôt qui le contient. — [Checkmarx](https://checkmarx.com/blog/unverified-commits-are-you-unknowingly-trusting-attackers-code/) ; [Hacker News, GitHub Commit Forgery](https://news.ycombinator.com/item?id=17681890)
- Un article arXiv de 2026 qui appuie son préenregistrement sur l'historique du dépôt écrit : « we regard that as weaker than an external registration ». Un autre reconnaît que ses horodatages git « constrain us but [were] not externally validated ». — [arXiv 2608.12895](https://arxiv.org/pdf/2608.12895) (préprints, non relus par des pairs)
- Pratique plus forte relevée dans un préprint de 2026 : hacher le paquet figé, le committer, ancrer le hash via OpenTimestamps et le déposer sur OSF **avant** l'expérience. Le même préprint précise qu'un dépôt OSF postérieur est « an archival record checkable against the pre-run commitment; it is not a preregistration ». — rapporté par la recherche web ; article exact non identifié, à vérifier
- Peikert, van Lissa & Brandmaier (2021, *Psych* 3(4):836–867) : flux reproductible combinant Git, Make, Docker et R Markdown. Ils proposent le « Preregistration as Code » (PAC) : le préenregistrement est écrit comme du code reproductible. Git y sert à prendre des instantanés identifiés de manière unique. — [MDPI Psych 3/4/53](https://mdpi.com/2624-8611/3/4/53) (2021, antérieur à 2025)
- Vuorre & Curley (2018, *AMPPS*), « Curating Research Assets: A Tutorial on the Git Version Control System » : git comme outil pour conserver, partager et collaborer sur les ressources de recherche. Ils ne présentent pas git comme une preuve de préenregistrement. — [APS AMPPS](https://www.psychologicalscience.org/journals/ampps/2515245918754826/) (2018, antérieur)
- OSF archive les add-ons de stockage connectés au moment de la registration. Les sources consultées ne disent pas si l'historique des commits d'un add-on GitHub est conservé. — [OSF Registration FAQ](https://help.osf.io/category/549-registration-and-preregistration-faqs)

### Inferences
- Schéma défendable :
  1. Registration OSF horodatée, qui contient le plan et des hash (sha256 ou SWHID `cnt`/`dir`) des fichiers clés (script d'analyse, plan) ;
  2. tag git figé dans le dépôt de travail ;
  3. instantané public avec DOI, dont les fichiers recalculés donnent les mêmes hash.

  La preuve d'antériorité vient de l'horodatage OSF ; l'identité des fichiers vient des hash. L'historique git n'ajoute rien de plus que l'auteur ne puisse fabriquer.
- Si le préenregistrement OSF cite un **hash de commit**, une réécriture de l'historique casse cette correspondance. Si l'on publie un instantané, on publie le hash d'arbre ou de fichier tel quel et on peut vérifier qu'il correspond. C'est un argument technique en faveur de l'option (a).
- Les relecteurs valorisent l'historique quand il montre ce qui s'est passé après l'enregistrement : écarts, essais. Une alternative à l'historique brut : un journal des écarts au plan, documenté (cf. Q4).

### Gaps
- Aucune enquête ou politique trouvée indiquant que des relecteurs d'études préenregistrées *demandent* l'historique git.
- Pas trouvé l'article « preregistration via GitHub » de référence. Pas de doc COS sur l'add-on GitHub d'OSF et la conservation de l'historique.
- Le préprint OpenTimestamps n'a pas été identifié nommément.

## Q3. Exemples réels d'études préenregistrées ou de Registered Reports qui ont publié un dépôt nettoyé ou un instantané à cause de données confidentielles

### Takeaway
Pas d'exemple nommé et vérifié d'un Registered Report ayant publié un historique git *réécrit*. Le schéma documenté dans la pratique est l'**instantané de code plus des données restreintes ou synthétiques**, avec une déclaration d'accès.

### Cited Findings
- Quintana (eLife 2020), primer sur les données synthétiques (R, synthpop). C'est une méthode conçue à l'origine pour partager des données de recensement confidentielles. Les matériaux sont sur OSF (osf.io/z524n) : modèle de documentation « code ouvert, données synthétiques ». — [eLife 53275](https://elifesciences.org/articles/53275v1) (2020, antérieur)
- Exemple de directive auteur pour Registered Reports (SAGE) : confirmer le partage des données brutes anonymisées, des matériaux et du code d'analyse. — [SAGE RR guidelines](https://visus-us.sagepub.com/en-us/nam/node/1621282)
- Une étude des gabarits OSF de Registered Reports en génie logiciel constate qu'aucun ne couvre entièrement les recommandations de documentation : sections à compléter soi-même. — [arXiv 2602.09292](https://arxiv.org/html/2602.09292v1)
- Économie : le README des Social Science Data Editors (DOI 10.5281/zenodo.7293838) est la norme de fait (AEA, REStud) pour les dossiers de réplication avec données « open-access, restricted-use, or confidential ». — [SSDE template README](https://social-science-data-editors.github.io/template_README) ; [AEA Data Editor](https://aeadataeditor.github.io/posts/2020-12-08-template-readme)

### Inferences
- Le précédent le plus solide n'est pas « dépôt réécrit » mais « dossier de réplication » au sens AEA/SSDE : instantané du code plus README qui liste chaque source, ce qui est fourni, ce qui ne l'est pas, et pourquoi.

### Gaps
- Aucun cas concret trouvé d'auteurs expliquant avoir purgé l'historique git d'un dépôt de Registered Report. Il faudrait une recherche dans OSF Registries ou GitHub, hors budget.

## Q4. Bonnes pratiques pour documenter les omissions et gérer les données confidentielles

### Takeaway
Consensus : on **déclare toujours** (disponibilité, où, conditions d'accès), on justifie la restriction auprès de l'éditeur, et on décrit dans un README structuré ce qui est fourni, ce qui est retenu, pourquoi, et comment y accéder. Données de remplacement possibles : synthétiques ou factices.

### Cited Findings
- Springer Nature : même quand le code ne peut pas être partagé, déclarer sa disponibilité et les conditions d'accès. — [SN code policy](https://springernature.com/gp/open-science/code-policy)
- PLOS : expliquer la restriction dans la lettre d'accompagnement, puis décrire la voie d'accès dans la DAS (procédure de demande, contact, dépôt à accès contrôlé). PLOS Comp Biol : « authors must indicate how others may request access to the code ». — [PLOS Code Sharing Guidance](https://journals.plos.org/plosbiology/s/code-sharing-guidance) ; [PLOS Comp Biol code availability](https://journals.plos.org/ploscompbiol/s/code-availability)
- README SSDE, en trois parties : Data and Code Availability Statement, Computational Requirements, Instructions. La partie disponibilité indique la provenance des données, les restrictions d'accès et les licences. Elle précise les conditions d'accès pour (a) les auteurs actuels et (b) les futurs utilisateurs : inscription, adhésion, procédure de candidature, coût. — [SSDE template README](https://social-science-data-editors.github.io/template_README) ; [SSDE guidance](https://social-science-data-editors.github.io/guidance)
- Guide dédié du Labor Dynamics Institute pour la reproductibilité quand « (some) data are confidential ». — [LDI reproducibility-confidential](https://labordynamicsinstitute.github.io/reproducibility-confidential-expanded/_sources/20-the-readme.md)
- TOP 2025, niveau 1 « Disclose » : simple déclaration d'existence et de lieu. C'est le minimum même quand rien n'est partagé. — [COS TOP](https://www.cos.io/initiatives/top-guidelines)
- Données synthétiques comme substitut reproductible. — [Quintana, eLife](https://elifesciences.org/articles/53275v1)

### Inferences
Pour un instantané nettoyé, prévoir :
1. une section « Ce qui n'est pas publié » avec une ligne par catégorie retenue (motif : vie privée, confidentialité commerciale, notes personnelles) ;
2. un manifeste de sommes de contrôle sha256 des fichiers publiés ;
3. la liste des hash des fichiers retenus, si on veut prouver leur existence sans en publier le contenu ;
4. un renvoi croisé : DOI de l'instantané, DOI ou date de la registration OSF, tag du dépôt de travail ;
5. une procédure d'accès restreint, ou « non disponible », assumée explicitement.

### Gaps
- Page DCAS « Restricted data » en 404 : son contenu exact n'a pas été vérifié.
- Pas de recommandation officielle trouvée sur la publication de *hash* de fichiers retenus comme preuve d'existence. C'est une pratique déduite, non sourcée.
