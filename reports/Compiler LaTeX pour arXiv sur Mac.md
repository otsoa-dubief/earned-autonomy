# Compiler en pdfLaTeX local, vérifier sur arXiv

Pour un article destiné à arXiv puis à un atelier NeurIPS ou ICLR, le meilleur choix sur un Mac Apple Silicon sans TeX est **TinyTeX**. C'est une vraie TeX Live, avec pdfLaTeX, BibTeX et `tlmgr`. Elle s'installe dans le dossier utilisateur **sans mot de passe administrateur**, pèse entre 67 et 210 Mo, et les paquets manquants s'ajoutent sans sudo ([yihui.org/tinytex](https://yihui.org/tinytex/), [tinytex-releases](https://github.com/rstudio/tinytex-releases)). Le critère qui tranche est le moteur. arXiv compile en **pdfLaTeX sous TeX Live 2025** ([arXiv TeX Live FAQ](https://info.arxiv.org/help/faq/texlive.html)), et les gabarits NeurIPS 2026 et ICLR 2026 supposent pdfLaTeX, natbib et des polices Times de type 1 ([Formatting Instructions NeurIPS 2026](https://www.overleaf.com/latex/templates/formatting-instructions-for-neurips-2026/bjdwqfdkyftc.pdf), [iclr2026_conference.tex](https://raw.githubusercontent.com/ICLR/Master-Template/master/iclr2026/iclr2026_conference.tex)). Cela écarte Tectonic, qui repose sur XeTeX avec un bundle ancien. Cela écarte aussi pandoc comme chaîne de production : il ne sert qu'à convertir une fois. Overleaf gratuit fonctionne techniquement, mais un texte préenregistré non publié y serait stocké sur Google Cloud, surtout aux États-Unis, sans synchronisation Git ([Overleaf legal](https://www.overleaf.com/legal), [Overleaf plans](https://www.overleaf.com/user/subscription/plans)). Un écart subsiste : TinyTeX fournit TeX Live 2026, arXiv TeX Live 2025. Pour un article natbib + BibTeX standard, il est faible. On le couvre en épinglant `texlive_version: 2025` dans le `00README` et en relisant le PDF qu'arXiv compile lui-même avant validation. Repli : **MacTeX complet** via Homebrew, si l'on a les droits administrateur et 6,4 Go à y consacrer.

## Trois contraintes d'arXiv suffisent à trier les sept options

arXiv propose aujourd'hui **TeX Live 2025 par défaut (arbre figé au 3 août 2025) et TeX Live 2023**. Aucune annonce officielle de TeX Live 2026 n'a été trouvée au 17 novembre 2026 ([arXiv TeX Live FAQ](https://info.arxiv.org/help/faq/texlive.html), [arXiv 00README](https://info.arxiv.org/help/00README.html)). Une fois en production, un arbre n'est plus mis à jour. Ce qu'on vise localement est donc une cible fixe. La politique publiée reste ambiguë. Le blog de septembre 2025 promet de suivre les sorties annuelles et de garder les deux dernières ([arXiv blog, 2025-09-10](https://blog.arxiv.org/2025/09/10/tex-live-2025-on-arxiv)), alors que la FAQ parle d'une mise à jour « tous les quelques ans ». Dans les deux cas, TL2025 restera sélectionnable, donc la cibler ne présente aucun risque.

Deuxième contrainte : le moteur. **pdfLaTeX est « fully supported »**. XeLaTeX est accepté depuis novembre 2025, mais un lecteur signale qu'il manque dans le menu de sélection, et LuaLaTeX n'est pas pris en charge ([arXiv submit_tex](https://info.arxiv.org/help/submit_tex.html), [arXiv blog, 2025-11-05](https://blog.arxiv.org/2025/11/05/attention-authors-updates-for-bib-file-processing-and-tex-in-arxiv-submissions)). Sous pdfLaTeX, arXiv n'accepte que des figures **PDF, PNG ou JPG**, sans conversion automatique. Vos figures PDF conviennent.

Troisième contrainte : la bibliographie. Depuis le 5 novembre 2025, **arXiv lance BibTeX ou Biber lui-même** si l'on dépose le `.bib`. Un `.bbl` déposé est utilisé tel quel, à condition de porter le nom du `.tex` principal. Avec biblatex, le `.bbl` doit être au format 3.3 exactement sous TL2025 ([arXiv submit_tex](https://info.arxiv.org/help/submit_tex.html)). C'est un piège pour qui compile en TL2026 avec biblatex. Ce n'en est pas un ici : NeurIPS et ICLR chargent **natbib** par défaut, et un `.bbl` produit par BibTeX et un `.bst` est du LaTeX ordinaire, sans numéro de format ([iclr2026_conference.sty](https://raw.githubusercontent.com/ICLR/Master-Template/master/iclr2026/iclr2026_conference.sty)). natbib + BibTeX est donc à la fois le chemin le plus sûr vers arXiv et celui qu'imposent les gabarits.

Les gabarits ne réclament rien d'exotique. `neurips_2026.sty` charge `environ`, `natbib`, `geometry[letterpaper]` et `lineno`, et règle les polices `ptm`/`phv`. La consigne exige des polices **Type 1 ou TrueType incorporées, sans Type 3**, à vérifier avec `pdffonts` ([copie tierce de neurips_2026.sty](https://web.uvic.ca/~nmehta/incentives_and_machine_learning_spring2026/neurips_2026.sty), [Formatting Instructions NeurIPS 2026](https://www.overleaf.com/latex/templates/formatting-instructions-for-neurips-2026/bjdwqfdkyftc.pdf)). Le gabarit NeurIPS 2026 a une option atelier intégrée (`dblblindworkshop`/`sglblindworkshop` et `\workshoptitle`) et une option `preprint` pour arXiv. ICLR n'a pas d'option atelier : chaque atelier publie sa variante. Le dépôt officiel propose déjà un dossier `iclr2027/` ([ICLR/Master-Template](https://github.com/ICLR/Master-Template)). Les `.sty` et `.bst` de ces gabarits ne font pas partie de TeX Live : il faut les **déposer avec les sources** sur arXiv.

## Comparaison : seules les TeX Live locales cochent toutes les cases

| Option | Moteur et TeX Live | Taille, droits | Reproductibilité, maintenance | Risques principaux | Confidentialité |
|---|---|---|---|---|---|
| **TinyTeX** | pdfLaTeX, TL2026 | 67 à 210 Mo, **sans sudo**, `~/Library/TinyTeX` | binaires mensuels ; réinstallation à chaque nouvelle année TL | paquets à ajouter un par un ; TL2026 ≠ TL2025 | locale |
| **MacTeX complet** | pdfLaTeX, TL2026, scheme-full | **6,4 Go**, mot de passe admin (.pkg système) | `tlmgr update` ; nouvelle installation chaque année | volume disque ; TL2026 ≠ TL2025 | locale |
| **BasicTeX** | pdfLaTeX, TL2026 | 134 Mo, mot de passe admin, `sudo tlmgr` pour chaque paquet | idem MacTeX | latexmk souvent absent ; sudo répété | locale |
| **Tectonic** | **XeTeX**, bundle ancien (env. TL2022, à vérifier) | formule brew, sans sudo, téléchargement au premier usage | bundle verrouillable, `SOURCE_DATE_EPOCH` | mise en page différente de pdfLaTeX ; crashs macOS corrigés en 2026 | locale (réseau au premier usage) |
| **Docker texlive** | pdfLaTeX, **TL2025 épinglable** | image complète 2,6 Go + moteur Docker à installer | **la plus forte** (tags datés) | arm64 officiel « experimental » ; émulation lente | locale |
| **Overleaf** | pdfLaTeX, TL2026 par défaut, TL2025 au choix | aucune installation | historique 24 h, pas de Git en gratuit | délai de compilation de **10 s** en gratuit | **GCP, surtout aux États-Unis** |
| **pandoc Markdown→LaTeX** | aucun : il lui faut un moteur TeX | déjà présent | double source, risque de divergence | longtable non flottante, pas de références croisées natives | locale |

Sources du tableau : [TUG currentpackages](https://www.tug.org/mactex/currentpackages-tug.html), [Homebrew basictex](https://formulae.brew.sh/cask/basictex), [Homebrew tectonic](https://formulae.brew.sh/formula/tectonic), [Docker Hub texlive/texlive](https://hub.docker.com/r/texlive/texlive), [README islandoftex](https://gitlab.com/islandoftex/images/texlive/-/raw/master/README.md), [Overleaf blog TL2026](https://www.overleaf.com/blog/tex-live-2026-is-now-available), [Overleaf blog timeout](https://www.overleaf.com/blog/changes-to-free-compile-timeout), [pandoc manual](https://pandoc.org/MANUAL.html).

**Tectonic** est la tentation naturelle : une formule brew, pas de sudo, des recompilations et BibTeX automatiques. Mais c'est un moteur **« powered by XeTeX »** ([crates.io tectonic](https://crates.io/crates/tectonic)), avec un bundle par défaut construit à partir d'une TeX Live antérieure à celle d'arXiv. L'issue #871, à propos de `tabularray`, montre que des paquets récents manquent ([bundles/src/lib.rs](https://raw.githubusercontent.com/tectonic-typesetting/tectonic/master/crates/bundles/src/lib.rs), [issue #871](https://github.com/tectonic-typesetting/tectonic/issues/871)). En XeTeX, `fontenc`, `inputenc` et `microtype` (sans expansion) se comportent autrement : les coupures de ligne et de page peuvent différer de ce que produira arXiv. Dépasser d'une ligne la limite de 9 pages d'un atelier ne se voit alors qu'au dépôt. S'y ajoutent les correctifs de crash macOS des versions 0.16.9 et 0.17.0 en 2026 ([CHANGELOG](https://github.com/tectonic-typesetting/tectonic/blob/release/CHANGELOG.md)). Tectonic convient pour un brouillon, pas pour l'article final.

**BasicTeX** ressemble à TinyTeX en plus contraignant : l'installeur `.pkg` écrit sous `/Library/TeX`, et les guides indiquent que `tlmgr` « will probably require sudo ». Chaque paquet manquant coûte donc un mot de passe, et latexmk manque souvent ([gist](https://gist.github.com/peterhurford/75957ba9335e755013b87254ec85fab1), [latexmk INSTALL](https://tug.ctan.org/support/latexmk/INSTALL)). **MacTeX complet** supprime la chasse aux paquets, mais il coûte 6,4 Go et les droits administrateur pour un article qui utilise peut-être trente paquets. **Docker** est en théorie le plus fidèle : des tags datés `TL{année}-AAAA-MM-JJ` et `TL{année}-historic` permettent de reproduire TL2025 ([README islandoftex](https://gitlab.com/islandoftex/images/texlive/-/raw/master/README.md)). En pratique, il faut d'abord installer un moteur Docker. Le README officiel qualifie encore les builds ARMv8 d'**« experimental »**. Il reste l'émulation amd64 ou une image tierce, à qui l'on confie le texte. Le nom exact du tag `TL2025-historic` est déduit du schéma de nommage, pas vu en tant que tel.

**Overleaf** gère bien le dépôt arXiv : le menu Submit produit un zip conforme, `.bbl` compris, et l'on peut choisir TL2025 par projet ([Overleaf docs: arXiv checklist](https://docs.overleaf.com/troubleshooting-and-support/checklist-for-arxiv-submissions.md), [Overleaf docs: TeX Live](https://docs.overleaf.com/troubleshooting-and-support/tex-live)). Pour ce projet, trois points jouent contre lui. La version gratuite n'a **ni Git ni synchronisation GitHub**, donc chaque régénération des tables par script impose un téléversement manuel. Le délai de compilation gratuit est de **10 secondes**, ce qu'un article avec de nombreuses figures PDF peut dépasser ([Overleaf blog timeout](https://www.overleaf.com/blog/changes-to-free-compile-timeout)). Surtout, le texte d'une étude préenregistrée encore non publiée serait hébergé sur Google Cloud, surtout aux États-Unis, avec des sauvegardes qui « might persist » après suppression ([Overleaf legal](https://www.overleaf.com/legal)). Overleaf n'entraîne pas de modèles sur le contenu sans accord explicite ([Overleaf trust](https://trust.overleaf.com/)), et ses fonctions d'IA se désactivent dans Account Settings > Integrations ([Writefull integration](https://overleaf.com/learn/how-to/Writefull_integration)). Le risque reste modéré, mais il est inutile quand une installation locale fait le même travail. L'édition auto-hébergée (Community Edition) règle la confidentialité au prix d'une pile de serveurs Docker, disproportionnée pour un auteur seul ([GitHub overleaf/overleaf](https://github.com/overleaf/overleaf)).

**pandoc** ne compile rien : pour sortir un PDF, il lui faut lui-même un moteur LaTeX ([pandoc manual](https://pandoc.org/MANUAL.html)). Il traduit `[@clé]` en `\citep` avec `--natbib` et laisse passer les mathématiques et le LaTeX brut. En revanche, ses tableaux sortent en `longtable` non flottante, il ne gère pas les références croisées de figures et de tableaux sans le filtre pandoc-crossref, et il n'existe aucun modèle officiel NeurIPS ou ICLR ([pandoc-crossref](https://github.com/lierdakil/pandoc-crossref), [quarto-neurips-template](https://stevengogogo.github.io/quarto-neurips-template)). Son seul usage raisonnable ici est une conversion unique du brouillon Markdown en corps de `.tex` sans `-s`, collé dans le `main.tex` officiel. Le `.tex` devient ensuite la seule source.

## Recommandation : TinyTeX, tables écrites en .tex par le script

TinyTeX réunit tout ce qui compte : pdfLaTeX et BibTeX d'une vraie TeX Live, aucun droit administrateur, une installation légère et une désinstallation propre (supprimer `~/Library/TinyTeX`). Ses limites sont connues. TinyTeX n'installe pas automatiquement les paquets manquants hors de R : on les cherche avec `tlmgr search --global --file`. Et chaque nouvelle année TeX Live demande une réinstallation ([yihui.org/tinytex](https://yihui.org/tinytex/)). Pour un article ponctuel, ces deux limites pèsent peu.

Les tables doivent être produites par le script directement en LaTeX, plutôt qu'en Markdown converti. `Styler.to_latex(hrules=True, caption=..., label=..., position_float="centering")` de pandas produit un environnement `table` flottant avec les filets booktabs, une légende et une étiquette. Le papier l'inclut par `\input{tables/x.tex}` ([pandas docs](https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.to_latex.html)). L'échappement des `_` et `%` dans les noms de colonnes reste à vérifier dans le script.

**Installation** (commandes reconstituées à partir de la documentation, non exécutées sur cette machine) :

```bash
# 1. TinyTeX, variante intermédiaire (~210 Mo), sans sudo.
#    Si l'installeur demande un mot de passe pour /usr/local/bin, refuser : seuls les liens échouent.
curl -sL "https://tinytex.yihui.org/install-bin-unix.sh" | TINYTEX_INSTALLER=TinyTeX sh

# 2. PATH (zsh)
echo 'export PATH="$HOME/Library/TinyTeX/bin/universal-darwin:$PATH"' >> ~/.zshrc
source ~/.zshrc
which pdflatex bibtex tlmgr

# 3. Paquets requis par NeurIPS/ICLR + tables booktabs (sans sudo)
tlmgr install latexmk natbib fancyhdr eso-pic geometry lineno environ trimspaces \
  psnfss times helvetic courier symbol zapfding \
  booktabs multirow siunitx xcolor hyperref url amsfonts amsmath units microtype etoolbox caption

# 4. Paquet manquant signalé à la compilation (« File `x.sty' not found ») :
tlmgr search --global --file "/x.sty"     # donne le nom du paquet
tlmgr install <paquet>

# 5. pdffonts pour vérifier les polices (exigence NeurIPS)
brew install poppler
```

La liste de l'étape 3 est déduite des `\usepackage` des deux gabarits. Elle n'a pas été vérifiée paquet par paquet contre TinyTeX : si `tlmgr` refuse un nom, retirez-le et passez par l'étape 4.

**Compilation et paquet arXiv** :

```bash
cd papier/
python scripts/make_tables.py            # régénère tables/*.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
grep -nE "Citation .* undefined|Reference .* undefined|Overfull" main.log
pdffonts main.pdf                        # aucune ligne « Type 3 », colonne emb = yes partout

# Dossier propre, uniquement ce qui part sur arXiv, puis recompilation à blanc
rm -rf ../arxiv && mkdir -p ../arxiv
cp main.tex main.bbl refs.bib *.sty *.bst math_commands.tex ../arxiv/ 2>/dev/null
cp -R figures tables ../arxiv/
cat > ../arxiv/00README <<'EOF'
{"texlive_version": 2025, "process": {"compiler": "pdflatex"},
 "sources": [{"filename": "main.tex", "usage": "toplevel"}]}
EOF
(cd ../arxiv && latexmk -pdf -interaction=nonstopmode main.tex && latexmk -c && rm -f main.pdf)
(cd ../arxiv && zip -r ../arxiv.zip . -x '.*')
```

Le format JSON de `00README` vient de la documentation arXiv, qui précise que le système peut écraser la valeur de TeX Live ([arXiv 00README](https://info.arxiv.org/help/00README.html)). Le dossier doit respecter les règles de rejet connues : chemins relatifs, noms sans espace ni `& : \`, `\input` plutôt que `\include` depuis un sous-dossier, pas de shell-escape, pas de `.aux`, `.log` ni `.pdf` ([arXiv mistakes](https://info.arxiv.org/help/faq/mistakes.html)). Pour la version arXiv, utilisez `\usepackage[preprint]{neurips_2026}`, puis `final` (ou `dblblindworkshop,final` avec `\workshoptitle{...}`) pour l'atelier. Cette correspondance est déduite de la sémantique des options du `.sty`, à confirmer dans le zip officiel. Les versions du gabarit en circulation divergent sur la liste des options. Pour les figures matplotlib, réglez `pdf.fonttype = 42` afin d'éviter les polices Type 3. C'est une pratique courante, pas une consigne tirée des sources consultées.

La dernière vérification se fait sur arXiv même. L'écart TL2026 local contre TL2025 distant n'a pas d'outil de contrôle local officiel : arXiv ne publie ni image Docker ni script de reproduction. La consigne est de relire le journal et le PDF générés au dépôt, étape d'ailleurs obligatoire avant de finaliser ([arXiv submit_tex](https://info.arxiv.org/help/submit_tex.html)). Les incompatibilités TL2025 à surveiller sont connues : `cleveref` affiche le même nom pour chaque `\cref`, `hyperxmp` doit être chargé après `hyperref`, et charger un paquet dans un groupe produit désormais une erreur ([arXiv TeX Live FAQ](https://info.arxiv.org/help/faq/texlive.html)). Un article NeurIPS ou ICLR classique évite le premier problème en utilisant `\ref`, ou en préférant `zref-clever` à cleveref.

## Repli : MacTeX complet, si les droits administrateur sont disponibles

Si la recherche de paquets dans TinyTeX devient pénible (un atelier qui charge un paquet rare, un co-auteur qui ajoute `algorithm2e` ou `tikz`), le repli est MacTeX en scheme-full. C'est la même TeX Live 2026, le même pdfLaTeX, avec latexmk inclus. Il demande **6,4 Go** et le mot de passe administrateur, car l'installeur est un `.pkg` système ([TUG currentpackages](https://www.tug.org/mactex/currentpackages-tug.html)). Le cask Homebrew `mactex` existe, puisque le cask `basictex` le déclare en conflit ([Homebrew basictex](https://formulae.brew.sh/cask/basictex)). La variante `mactex-no-gui` évite TeXShop et les autres applications :

```bash
# Désinstaller TinyTeX d'abord, pour éviter deux pdflatex dans le PATH
tlmgr path remove; rm -rf ~/Library/TinyTeX     # puis retirer la ligne PATH de ~/.zshrc
brew install --cask mactex-no-gui               # demande le mot de passe administrateur
eval "$(/usr/libexec/path_helper)"
which pdflatex latexmk                          # attendu : /Library/TeX/texbin/...
```

Les commandes de compilation restent identiques. Pour coller exactement à TL2025, il reste l'image Docker épinglée (`texlive/texlive:TL2025-historic`, nom à confirmer). On ne la réserve qu'au cas où le PDF compilé par arXiv diverge du PDF local sans explication. Il faut alors installer un moteur Docker et accepter le statut expérimental de l'arm64 ou l'émulation amd64. Overleaf réglé sur TL2025 rend le même service, sous réserve de l'hébergement aux États-Unis, à n'envisager qu'après publication de la préinscription ou avec l'accord des co-auteurs.

## Conclusion

Le choix ne se joue pas sur la commodité d'installation, critère qui favoriserait Tectonic ou Overleaf. Il se joue sur la fidélité au compilateur d'arXiv, puis aux 9 pages d'un atelier. Comme arXiv fige ses arbres TeX Live et lance désormais BibTeX lui-même, une chaîne natbib + BibTeX + pdfLaTeX produit presque à coup sûr le même document localement et sur arXiv. La différence d'année entre TL2026 et TL2025 compte moins que la différence de moteur entre pdfLaTeX et XeTeX. D'où une règle simple : n'importe quelle TeX Live locale récente avec pdfLaTeX, la plus légère possible, et la compilation d'arXiv comme arbitre final.

Trois points restent ouverts au 17 novembre 2026. arXiv n'a pas annoncé l'arrivée de TL2026 : relire sa page d'aide avant le dépôt, car si TL2026 devient le défaut, l'écart avec TinyTeX disparaît. Le gabarit NeurIPS 2026 n'a été lu que dans une copie tierce : vérifier le zip officiel de neurips.cc. Enfin, la variante propre à l'atelier visé (souvent dérivée du gabarit ICLR 2027 ou NeurIPS 2026) l'emporte sur tout ce qui précède dès sa publication.
