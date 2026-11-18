# Distributions LaTeX locales sur Mac Apple Silicon (fin 2026) : Tectonic, BasicTeX, MacTeX, TinyTeX, Docker texlive

Contexte : article scientifique en pdfLaTeX + BibTeX/natbib, figures PDF, tableaux produits par script, cible arXiv. Recherche web faite le 17/11/2026. tug.org a renvoyé 403 à la récupération directe : les chiffres MacTeX/BasicTeX viennent de résultats de recherche qui citent les pages TUG/CTAN.

## Q1. Taille d'installation, sudo, commandes, obtention des paquets manquants, comportement hors ligne

### Takeaway
BasicTeX (environ 134 Mo) et MacTeX (6,4 Go) passent par un installeur .pkg système sous /Library/TeX : il faut le mot de passe administrateur, et `tlmgr install` demande en général sudo. TinyTeX et Tectonic s'installent sans sudo dans le dossier utilisateur. Tectonic télécharge les paquets à la demande, ce qui suppose le réseau à la première compilation. Docker embarque tout (2,6 Go pour l'image complète) et fonctionne ensuite hors ligne.

### Cited Findings
**MacTeX (complet)**
- MacTeX-2026 : téléchargement de 6,4 Go (date TUG : 24/03/2026), environ 6,87 milliards d'octets sur les miroirs CTAN. Demande macOS 11 ou plus récent et tourne nativement sur Intel et sur Arm — [TUG currentpackages](https://www.tug.org/mactex/currentpackages-tug.html), [CTAN mactex dir](https://ctan.org/texarchive/systems/mac/mactex/)
- Pas de cask MacTeX consulté directement. Le cask `basictex` déclare un conflit avec les casks `mactex` et `mactex-no-gui`, ce qui confirme qu'ils existent — [Homebrew basictex](https://formulae.brew.sh/cask/basictex)

**BasicTeX**
- BasicTeX 2026 : 134 Mo (date TUG : 02/03/2026). Une page de bugs TUG annonce environ 120 Mo, chiffre plus ancien ou arrondi — [TUG currentpackages](https://www.tug.org/mactex/currentpackages-tug.html), [TUG bugs](https://tug.org/texlive/bugs.html)
- Cask Homebrew `basictex` en version 2026.0301 ; commande `brew install --cask basictex`. Il installe `mactex-basictex-20260301.pkg`. Caveat : relancer le terminal, ou exécuter `eval "$(/usr/libexec/path_helper)"` — [Homebrew basictex](https://formulae.brew.sh/cask/basictex)
- Les binaires sont sous `/Library/TeX/texbin`. Les guides indiquent que `tlmgr` « will probably require sudo » (`sudo tlmgr update --self`, `sudo tlmgr install latexmk ...`) — [synthèse de guides, gist](https://gist.github.com/peterhurford/75957ba9335e755013b87254ec85fab1), [latexmk INSTALL](https://tug.ctan.org/support/latexmk/INSTALL)
- Les paquets manquants ne s'installent pas automatiquement : on les ajoute un par un avec `tlmgr install <pkg>`.

**TinyTeX**
- Installation sur macOS : `curl -sL "https://tinytex.yihui.org/install-bin-unix.sh" | sh`, sans droits administrateur. L'installeur ne demande sudo que si `/usr/local/bin` n'est pas inscriptible, pour les liens du PATH, et on peut refuser. Emplacement : `~/Library/TinyTeX` — [yihui.org/tinytex](https://yihui.org/tinytex/)
- Variantes et tailles pour macOS : TinyTeX-0 (infraonly) 2 Mo ; TinyTeX-1 (environ 100 paquets, variante par défaut) 67 Mo ; TinyTeX 210 Mo ; TinyTeX-2 (scheme-full, publiée en quotidienne seulement) 2,0 Go. Choix par `TINYTEX_INSTALLER` et `TINYTEX_VERSION` — [tinytex-releases](https://github.com/rstudio/tinytex-releases)
- Paquets manquants : installation automatique seulement depuis R (`tinytex::pdflatex()`). En ligne de commande, il faut chercher puis installer : `tlmgr search --global --file "/times.sty"` puis `tlmgr install psnfss` — [yihui.org/tinytex](https://yihui.org/tinytex/)

**Tectonic**
- Formule Homebrew `tectonic` en 0.17.0. Bottles arm64 listées : tahoe, sequoia et « golden gate » (libellé recopié tel quel), pas de bottle sonoma. Dépendances d'exécution : freetype, graphite2, harfbuzz, icu4c@79, libpng. Environ 4 800 installations sur 30 jours — [Homebrew tectonic](https://formulae.brew.sh/formula/tectonic)
- Le paquet est livré sans bundle TeX : il en télécharge un au premier usage, puis récupère automatiquement les fichiers de support dont un document a besoin — [buildsmith PR](https://github.com/nekrozis/buildsmith/pull/13), [site Tectonic](https://tectonic-typesetting.github.io/en-US/index.html)
- Hors ligne : `--only-cached` / `-C` compile uniquement avec le cache local — [doc compile](https://tectonic-typesetting.github.io/book/latest/v2cli/compile.html)
- Depuis la 0.17.0 (27/07/2026), le cache du bundle ne revérifie le serveur distant qu'une fois par semaine — [CHANGELOG release](https://github.com/tectonic-typesetting/tectonic/blob/release/CHANGELOG.md)

**Docker texlive (image officielle Island of TeX, `texlive/texlive` ou `registry.gitlab.com/islandoftex/images/texlive`)**
- Image `latest` : 2,6 Go (installation complète sans documentation) — [Docker Hub texlive/texlive](https://hub.docker.com/r/texlive/texlive)
- Schemes disponibles : `minimal`, `basic`, `small`, `medium`, `full`, `context` (par exemple `latest-small`). Sans scheme précisé, c'est `full`. Saveurs : `X`, `X-doc`, `X-src`, `X-doc-src` — [README islandoftex](https://gitlab.com/islandoftex/images/texlive/-/raw/master/README.md)
- Utilisateur root par défaut. Un utilisateur `texlive` sans droit d'installation est fourni et recommandé ; en mode non-root, il peut falloir ajuster les permissions des bind-mounts — [README islandoftex](https://gitlab.com/islandoftex/images/texlive/-/raw/master/README.md)
- **ARM : le README parle d'« ARMv8 builds as experimental releases »**, avec des binaires qui peuvent ne pas fonctionner. Plusieurs images tierces publient du linux/arm64 (mrchoke/texlive, zhongruoyu/texlive, ayaka-notes/texlive-full 2025/2026) — [README islandoftex](https://gitlab.com/islandoftex/images/texlive/-/raw/master/README.md), [mrchoke](https://hub.docker.com/r/mrchoke/texlive), [ayaka-notes](https://gh.r-mj.com/ayaka-notes/texlive-full)

### Inferences
- Pour un poste sans droits admin, ou pour éviter sudo à chaque `tlmgr` : TinyTeX ou Tectonic. Avec BasicTeX, chaque paquet manquant coûte un `sudo tlmgr install`.
- Docker sur Apple Silicon demande en plus un moteur (Docker Desktop, OrbStack, colima), qui n'est pas installé. Si l'image arm64 officielle reste expérimentale, il faut passer par l'émulation amd64 (Rosetta/QEMU, plus lente) ou par une image tierce.
- Docker et MacTeX sont les seules options utilisables entièrement hors ligne dès l'installation. Tectonic ne l'est qu'une fois le cache rempli.

### Gaps
- Pas trouvé le mécanisme exact de sudo dans le cask (Homebrew lance `installer` en sudo pour les .pkg en général, mais la page ne le dit pas).
- Taille installée de MacTeX sur disque (et pas seulement du téléchargement) non vérifiée. Taille du cache Tectonic pour un article type non trouvée.
- Statut arm64 du tag `latest` de `texlive/texlive` fin 2026 : rien de plus récent que la mention « experimental » du README.

## Q2. Année de TeX Live en 2026, écart avec arXiv, moteur Tectonic, BibTeX/biber, problèmes connus

### Takeaway
arXiv compile par défaut avec TeX Live 2025 (arbre figé le 03/08/2025) et propose encore TL2023. MacTeX, BasicTeX, TinyTeX et Docker `latest` fournissent TL2026 ; Docker permet aussi d'épingler TL2025 à l'identique d'arXiv. Tectonic n'est pas pdfLaTeX : c'est un moteur dérivé de XeTeX avec un bundle figé, plus ancien (TL2022 à 2024 selon les sources). C'est l'option la plus éloignée d'arXiv pour un article en pdfLaTeX.

### Cited Findings
- arXiv : « arXiv currently supports TeX Live 2023 and TeX Live 2025, with 2025 being the default ». Arbres : TL2023 au 21/05/2023, TL2025 au 03/08/2025. Un arbre en production n'est plus mis à jour par tlmgr. Problèmes TL2025 connus (`cleveref`, `array`), avec repli sur TL2023. Processeurs : `pdflatex`, `latex` (DVI), `xelatex` (ajouté en novembre 2025) — [arXiv TeX Live FAQ](https://info.arxiv.org/help/faq/texlive.html)
- TeX Live 2025 est sorti le 08/03/2025 ; la sortie PDF passe à la version 1.7 — [Wikipedia TeX Live](https://en.wikipedia.org/wiki/TeX_Live)
- MacTeX-2026 (24/03/2026) et BasicTeX 2026.0301 correspondent à TeX Live 2026 — [TUG currentpackages](https://www.tug.org/mactex/currentpackages-tug.html), [Homebrew basictex](https://formulae.brew.sh/cask/basictex)
- Docker : `latest` est la release courante, reconstruite chaque semaine. Des tags datés `TL{année}-AAAA-MM-JJ` existent pour la reproductibilité ou le retour arrière, et `TL{année}-historic` pour les années passées depuis 2013 (reconstruits mensuellement pour l'OS) — [README islandoftex](https://gitlab.com/islandoftex/images/texlive/-/raw/master/README.md)
- TinyTeX : binaires publiés chaque mois ; le message « Remote repository newer than local » impose de réinstaller — [yihui.org/tinytex](https://yihui.org/tinytex/)
- Tectonic : moteur « powered by XeTeX and TeX Live » — [crates.io tectonic](https://crates.io/crates/tectonic)
- URL du bundle par défaut construite à partir de la version de format : `https://relay.fullyjustified.net/default_bundle_v{N}.tar`. Selon le code, le format 32 correspond à TeX Live 2021 et le numéro de format suit à peu près les années TeX Live. Le bundle peut être figé au moment de la compilation avec `TECTONIC_BUNDLE_LOCKED` ou `TECTONIC_BUNDLE_PREFIX` — [bundles/src/lib.rs](https://raw.githubusercontent.com/tectonic-typesetting/tectonic/master/crates/bundles/src/lib.rs)
- Un wrapper tiers (tecgonic) télécharge par défaut un bundle Tectonic « version 33 » — [tecgonic](https://pkg.go.dev/github.com/mgilbir/tecgonic)
- Tectonic 0.16.0 (11/04/2026) : bundles entièrement retravaillés, « A new bundle added for texlive 2024 », préférence pour un exécutable `tectonic-biber` s'il est présent. 0.16.9 (17/04/2026) : correctif d'un crash macOS au réglage de la police principale. 0.17.0 (27/07/2026) : correctif du SIGBUS macOS sur `\setmainfont`, d'un segfault sur `\XeTeXglyphname`, et d'une panique de BibTeX sur un `@string` vide. 0.15.0 (05/02/2024) : BibTeX porté en Rust pur — [CHANGELOG release](https://github.com/tectonic-typesetting/tectonic/blob/release/CHANGELOG.md)
- Historique : la 0.9.0 (avril 2022) passait le bundle par défaut à TL2021.3. Le dépôt de génération des bundles mentionne texlive2023-20230313 — [recherche CHANGELOG / tectonic-texlive-bundles](https://github.com/tectonic-typesetting/tectonic-texlive-bundles)
- Retard du bundle : plaintes récurrentes, par exemple l'issue #871 (paquet `tabularray` absent du bundle) et le fil « The texlive bundle wasn't updated since 2018? » — [issue #871](https://github.com/tectonic-typesetting/tectonic/issues/871), [forum Tectonic](https://tectonic.newton.cx/t/the-texlive-bundle-wasnt-updated-since-2018/245)
- Biber : Tectonic n'embarque pas biber ; c'est le biber du système qui sert. D'où des incompatibilités de version avec le biblatex du bundle (discussion #988, issue #1136 : un utilisateur macOS n'arrive pas à rétrograder vers biber 2.17). Nixpkgs fournit un biber dédié à Tectonic — [discussion #988](https://www.github.com/tectonic-typesetting/tectonic/discussions/988), [issue #1136](https://www.github.com/tectonic-typesetting/tectonic/issues/1136), [nixpkgs](https://git.uninsane.org/colin/nixpkgs/commits/commit/c65681125fe643e10ecca54e4102b708e91de927/pkgs/tools/typesetting)
- BibTeX : intégré à Tectonic (port Rust) et lancé automatiquement ; `--pass bibtex_first` et `-Z min-crossrefs` sont disponibles — [doc compile](https://tectonic-typesetting.github.io/book/latest/v2cli/compile.html)

### Inferences
- Le bundle par défaut de la 0.17 est probablement v33, soit environ TL2022, d'après la règle « format 32 = TL2021 » et l'indice tecgonic. Le bundle TL2024 de la 0.16 n'est pas confirmé comme bundle par défaut. **À vérifier** avec `tectonic -X bundle` après installation, ou dans `Tectonic.toml`. Dans les deux cas, ce bundle est plus ancien que le TL2025 d'arXiv.
- Moteur XeTeX ≠ pdfLaTeX : polices traitées par fontspec/OpenType, et `\pdfoutput`, `microtype` (protrusion seulement, pas d'expansion en XeTeX), `inputenc`/`fontenc` se comportent différemment. Les sauts de ligne et de page peuvent donc différer de la compilation pdflatex d'arXiv. Tectonic convient pour un brouillon, pas pour vérifier ce que produira arXiv. (Inférence tirée de propriétés connues de XeTeX ; pas de source 2026 comparant précisément les sorties.)
- natbib + BibTeX (pas de biber) est le cas favorable pour Tectonic, puisque le problème de biber ne se pose pas.
- TL2026 en local contre TL2025 sur arXiv : écart faible pour un article standard. Pour coller exactement, `texlive/texlive:TL2025-historic` (tag déduit du schéma de nommage, non vu explicitement).
- Les correctifs macOS successifs de la 0.16.9 et de la 0.17.0 (segfault sur les polices) montrent une fragilité de Tectonic sur macOS en 2026.

### Gaps
- Bundle par défaut exact de Tectonic 0.17 non confirmé par une source primaire.
- Pas de liste officielle des paquets absents du bundle Tectonic en 2026.
- Pas de source TUG directe sur la date de sortie de TL2026 : la date de MacTeX (mars 2026) sert d'indice.

## Q3. Reproductibilité (SOURCE_DATE_EPOCH), maintenance, désinstallation

### Takeaway
Tectonic affiche la reproductibilité (SOURCE_DATE_EPOCH suffit d'ordinaire ; mode `-Z deterministic-mode`). Docker avec un tag daté épingle la version de TeX Live, ce qui est la reproductibilité la plus forte entre machines. Les distributions TeX Live locales évoluent avec chaque `tlmgr update`.

### Cited Findings
- Tectonic : « setting `SOURCE_DATE_EPOCH` is usually sufficient for reproducible builds ». `-Z deterministic-mode` force un environnement déterministe mais « breaks SyncTeX's auxiliary files ». Le bundle peut être verrouillé, et `TECTONIC_BUNDLE_LOCKED` est présenté comme utile pour les builds reproductibles — [doc compile](https://tectonic-typesetting.github.io/book/latest/v2cli/compile.html), [bundles/src/lib.rs](https://raw.githubusercontent.com/tectonic-typesetting/tectonic/master/crates/bundles/src/lib.rs)
- Docker : tags hebdomadaires datés « for reproducible builds or rollbacks » ; les historic sont figés côté TeX mais reconstruits côté OS — [README islandoftex](https://gitlab.com/islandoftex/images/texlive/-/raw/master/README.md)
- arXiv garde l'arbre en vigueur à la soumission et ne le met plus à jour une fois en production — [arXiv TeX Live FAQ](https://info.arxiv.org/help/faq/texlive.html)
- TinyTeX : désinstallation par `tlmgr path remove`, puis suppression de `~/Library/TinyTeX`. Quand TeX Live passe à l'année suivante, il faut réinstaller — [yihui.org/tinytex](https://yihui.org/tinytex/)
- BasicTeX ou MacTeX via cask : désinstallation `brew uninstall --cask basictex`. La page Homebrew ne détaille pas ce qui est supprimé — [Homebrew basictex](https://formulae.brew.sh/cask/basictex)
- Tectonic : `brew uninstall tectonic`, plus le cache utilisateur à supprimer (non documenté sur les pages consultées).

### Inferences
- pdfTeX, dans TeX Live récent, respecte aussi SOURCE_DATE_EPOCH (avec `FORCE_SOURCE_DATE=1` pour `\today`). C'est une connaissance antérieure, non revérifiée ici en 2026, à signaler comme telle.
- MacTeX et BasicTeX : la mise à jour annuelle impose une nouvelle installation (nouvelle année TeX Live). L'ancienne année reste dans `/usr/local/texlive/20XX` et prend de la place (connaissance générale, non sourcée ici).

### Gaps
- Pas de test public 2026 « même PDF octet pour octet » pour aucune des options.
- Procédure de désinstallation complète de MacTeX (pkgutil, /usr/local/texlive, /Library/TeX) non récupérée : tug.org en 403.

## Q4. Disponibilité de latexmk

### Takeaway
latexmk est inclus dans MacTeX complet et dans l'image Docker `full`. Il manque souvent dans BasicTeX (`sudo tlmgr install latexmk`) et sans doute dans TinyTeX-1. Il ne sert pas avec Tectonic, qui gère lui-même les recompilations et BibTeX.

### Cited Findings
- latexmk INSTALL : « if you have only installed a subset of packages, e.g., because you installed BasicTeX, then the subset may not include latexmk ». Correctif habituel : `sudo tlmgr install latexmk` — [latexmk INSTALL](https://tug.ctan.org/support/latexmk/INSTALL), [gist](https://gist.github.com/peterhurford/75957ba9335e755013b87254ec85fab1)
- Signalement en mars 2026 sur macosx-tex : avec le paquet `latexmk.universal-darwin`, le script `latexmk.pl` et son dossier manquent — [macosx-tex mars 2026](https://email.esm.psu.edu/pipermail/macosx-tex/2026-March/059196.html)
- Docker : scheme `full` par défaut, donc tous les paquets. Hors `full`, ajouter un paquet binaire par `tlmgr install <binaire> && tlmgr path add` — [README islandoftex](https://gitlab.com/islandoftex/images/texlive/-/raw/master/README.md)
- Tectonic : relance automatique du moteur (`--reruns`) et passe BibTeX intégrée — [doc compile](https://tectonic-typesetting.github.io/book/latest/v2cli/compile.html)

### Inferences
- TinyTeX : `tlmgr install latexmk` sans sudo, plus `tlmgr path add`.
- MacTeX complet contient scheme-full, donc latexmk (connaissance générale, cohérente avec scheme-full).

### Gaps
- Présence de latexmk dans les bundles TinyTeX-1 et TinyTeX non confirmée (liste des paquets non consultée).
- Le signalement de mars 2026 sur `latexmk.universal-darwin` n'a pas été lu en entier : impact réel sur BasicTeX inconnu.
