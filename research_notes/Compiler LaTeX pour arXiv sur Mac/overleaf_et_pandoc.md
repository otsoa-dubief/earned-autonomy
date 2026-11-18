# Non-local / conversion routes to an arXiv-ready LaTeX paper: Overleaf and pandoc (as of Nov 2026)

## Overleaf: free-plan limits, TeX Live version, arXiv export, privacy, self-hosted alternative

### Takeaway
Overleaf's free plan works for a solo author with a short paper, but it has three limits that matter here: a 10-second compile timeout, no Git or GitHub sync, and only 24 hours of history. New projects compile with TeX Live 2026 (released on Overleaf 18 Aug 2026). arXiv was last confirmed to support TeX Live 2025 and 2023, so the versions may not match. Privacy terms say content is not used to train AI unless you opt in. Data sits on Google Cloud, mostly in the US. The self-hosted Community Edition (AGPL, Docker) keeps everything local, but it is a heavy server stack.

### Cited Findings
**Plan limits (plans page fetched Nov 2026)**
- Free plan: "Basic" compile timeout, 1 collaborator per project, **no Git or GitHub sync**, history limited to the previous 24 hours, 5 AI uses per day, no track changes, offline editing limited to 2 minutes — [Overleaf plans](https://www.overleaf.com/user/subscription/plans)
- Paid plans (EUR): Student €7.25/mo billed yearly (€87/yr), Standard €15/mo yearly (€179/yr), Pro €30.75/mo yearly (€369/yr). All paid plans get "24x Basic" compile time, Git and GitHub integration, and full history. Student requires a degree-granting institution — [Overleaf plans](https://www.overleaf.com/user/subscription/plans)
- The free compile timeout is **10 seconds** and the paid timeout is 4 minutes (blog post of 16 June 2025). The post gives conflicting effective dates: the body says 8 Sept 2025, and a 16 July 2025 update says enforcement moved to 25 Aug 2025. A 2023 adjustment came before it — [Overleaf blog](https://www.overleaf.com/blog/changes-to-free-compile-timeout)
- Older figures of 20 s, and a competitor's claim of 60 s, are outdated or unreliable. I found no 2026 change to the 10-second limit — [Overleaf learn (old plan-limits page)](https://cs.sharelatex.com/learn/how-to/What_is_the_maximum_compilation_time%2C_file_number_and_project_size_allowed_on_free_vs_paid_plans%3F); [trybibby (competitor)](https://www.trybibby.com/blog/overleaf-alternative-2026)
- Overleaf suggests "Stop on first error" and "Fast [draft]" compile modes to work around timeouts — [Overleaf docs: compile timeouts](https://docs.overleaf.com/troubleshooting-and-support/fixing-and-preventing-compile-timeouts)

**TeX Live and compilers**
- TeX Live 2026 became available on Overleaf on **18 Aug 2026**. Existing projects keep the TeX Live version they were created with. `tabu`, `tabls` and `varioref` with KOMA-Script break under TL 2026 — [Overleaf blog TL2026](https://www.overleaf.com/blog/tex-live-2026-is-now-available)
- New and copied projects compile with the latest TeX Live installed on Overleaf by default. The version can be changed per project under Settings > Compiler. pdfLaTeX is the default compiler; LaTeX, XeLaTeX and LuaLaTeX are also offered — [Overleaf docs: TeX Live](https://docs.overleaf.com/troubleshooting-and-support/tex-live); [Overleaf docs: selecting TL version](https://docs.overleaf.com/getting-started/recompiling-your-project/selecting-a-tex-live-version-and-latex-compiler.md)

**arXiv export**
- The **Submit > "Submit to arXiv"** option does not submit anything. It produces a zip in the format arXiv expects, including generated files such as the `.bbl` — [Overleaf docs: arXiv checklist](https://docs.overleaf.com/troubleshooting-and-support/checklist-for-arxiv-submissions.md); [Overleaf docs: generated files](https://docs.overleaf.com/navigating-in-the-editor/generated-files)
- Overleaf's checklist (written Feb 2026): arXiv uses TL 2025 (snapshot 2025-08-03, the default) or TL 2023. Overleaf's TL 2025 image is 2025-10-27, so features newer than arXiv's snapshot may compile differently. Other points: put the main `.tex` in the project root; arXiv loads hyperref itself, so use plain `\usepackage{hyperref}` plus `\hypersetup{...}` to avoid an option clash, or add a `00README.XXX` file containing `nohypertex`; arXiv runs pdfLaTeX and cannot use `.eps`, so use `.pdf` figures. If a journal template hides the arXiv option, make a copy of the project — [Overleaf docs: arXiv checklist](https://docs.overleaf.com/troubleshooting-and-support/checklist-for-arxiv-submissions.md)
- arXiv supports TL 2023 and 2025, with 2025 as the default since Sept 2025 (Submission 1.5). It says it will track annual TeX Live releases and drop 2023 once 2026 arrives. Known issues under TL 2025: cleveref was not updated, and minted changed — [arXiv blog Sept 2025](https://blog.arxiv.org/2025/09/10/tex-live-2025-on-arxiv); [arXiv help: TeX submissions](https://info.arxiv.org/help/submit_tex.html)
- Since **5 Nov 2025**, arXiv runs BibTeX/biber itself, so you can upload the `.bib` instead of a precompiled `.bbl` — [arXiv blog Nov 2025](https://blog.arxiv.org/2025/11/05/attention-authors-updates-for-bib-file-processing-and-tex-in-arxiv-submissions)
- There is no "resubmit" button. For a new arXiv version, download the zip again and replace the changed files — [Hugh Osborn blog (2023, older)](https://www.hughosborn.co.uk/2023/06/07/uploading-an-overleaf-paper-to-arxiv/)

**Privacy and data hosting (Terms dated 5 May 2026, Privacy Notice 11 Jun 2026)**
- Storage is on **Google Cloud Platform**. Much of the infrastructure is in the US, and data can go to other locations where affiliates and processors operate. No specific region is named. Named sub-processors include Netsuite, Salesforce and Qualtrics — [Overleaf legal](https://www.overleaf.com/legal)
- Overleaf does not share content unless you direct or authorize it. On managed (institutional) accounts, the organization has admin rights over content. Overleaf may disclose decrypted content when legally required. Deletion after account closure is "quickly," but "backed-up versions might persist" — [Overleaf legal](https://www.overleaf.com/legal)
- AI: "We will not use your Inputs or Outputs to train or develop AI models except where this is part of the Services" (consent wording is ambiguous). Contracts with LLM providers bar them from training on your content — [Overleaf legal](https://www.overleaf.com/legal)
- Trust page: "Your data never trains our models - unless you opt in." A warning appears before any feature sends content to a third-party model. The page also shows a label "documents sold to third parties" with no figure, which contradicts its own "never sold" claim and looks like a page artifact — [Overleaf trust](https://trust.overleaf.com/)
- Writefull (Overleaf's AI layer) can use its own models or OpenAI/Anthropic. Your email and user ID are shared with Writefull to link accounts. All AI, including Error Assist, can be switched off under Account Settings > Integrations — [Writefull privacy](https://writefull.com/privacy); [Overleaf learn: Writefull integration](https://overleaf.com/learn/how-to/Writefull_integration)

**Self-hosted Community Edition**
- Overleaf CE is AGPL v3 and installed through the **Overleaf Toolkit** (Docker). It has **no sandboxed compiles**, so it suits trusted users only. Server Pro adds SSO, admin tools and tracked changes — [GitHub overleaf/overleaf](https://github.com/overleaf/overleaf)
- Server Pro uses TeX Live images selected with `TEX_LIVE_DOCKER_IMAGE` and `ALL_TEX_LIVE_DOCKER_IMAGES`. A TL 2026 image is offered — [Overleaf blog TL2026](https://www.overleaf.com/blog/tex-live-2026-is-now-available)

### Inferences
- With a 10 s free timeout, a NeurIPS-style paper with many PDF figures and BibTeX can time out on a full compile. Draft mode helps. A local TeX install avoids the problem entirely.
- No Git on the free plan means the Python-generated `.tex` tables cannot be synced from a repo automatically. They must be re-uploaded by hand after each script run. This is a real friction point for a script-driven workflow.
- TeX Live mismatch: a new Overleaf project defaults to TL 2026, while arXiv was last confirmed on TL 2025/2023. Setting the Overleaf project to TL 2025 by hand gives the closest match to arXiv.
- Preregistered, unpublished paper: the risk is low (no training by default, AI can be disabled, contractual limits on LLM providers). But the content is stored on US GCP and kept in backups after deletion. If that matters, use a local TeX install or Overleaf CE rather than overleaf.com, and turn off AI integrations if you use overleaf.com.
- Overleaf CE in Docker is more machinery than a solo author needs. A local TeX distribution gives the same privacy with less effort. CE makes sense only if you want the Overleaf web editor offline.

### Gaps
- No exact free-plan compile timeout is printed on the 2026 plans page ("Basic"). The 10 s figure comes from the June 2025 blog post.
- I could not confirm whether arXiv has added TL 2026 as of Nov 2026. Check arXiv's TeX submission help page.
- I found no official Overleaf statement on internal staff access to project content, or on a specific GCP region or EU hosting option for individual accounts.
- The latest CE release number and the TeX Live scheme installed in the CE image were not found.

## pandoc: Markdown→LaTeX quality for academic papers, templates, workflow

### Takeaway
pandoc produces usable LaTeX. Math passes through verbatim, raw LaTeX passes through, `--natbib` gives `\citep`/`\citet`, and tables use longtable with booktabs. Native cross-references to figures and tables are missing (that needs the pandoc-crossref filter), and longtable tables do not float, which clashes with conference styles. There is no official NeurIPS or ICLR pandoc template. The sensible route is a one-shot conversion to get a first `.tex`, then editing that `.tex` by hand inside the official template. pandoc needs a TeX engine to produce a PDF.

### Cited Findings
- Versions: pandoc 3.8 shipped 6 Sept 2025 and 3.8.3 on 1 Dec 2025. A release tracker lists 3.9, 3.10 and 3.10.1 after that, but I did not read those release notes — [Hackage changelog](https://hackage.haskell.org/package/pandoc-3.8/src/changelog.md); [releasealert](https://releasealert.dev/github/jgm/pandoc)
- PDF output: "By default, pandoc will use LaTeX to create the PDF, which requires that a LaTeX engine be installed." `--pdf-engine` accepts pdflatex (the default), xelatex, lualatex, tectonic and latexmk — [pandoc manual](https://pandoc.org/MANUAL.html)
- `--natbib` is "intended for use in producing a LaTeX file that can be processed with bibtex", and the same goes for `--biblatex` with bibtex or biber. Both are "not for use with the --citeproc option or with PDF output." `--citeproc` renders citations as text itself, from CSL. The bibliography must be BibTeX for natbib or BibLaTeX for biblatex — [pandoc manual](https://pandoc.org/MANUAL.html)
- Citation mapping: `[@key]` becomes `\citep{key}` and `@key` becomes `\citet{key}` under natbib — [bookdown citations](https://pkg.yihui.org/bookdown/citations)
- Tables: "By default, pandoc will render tables in LaTeX using the `longtable` environment." They do not float, though a `float` class makes them floating tables. The manual lists longtable, booktabs and multirow among the required packages. `--table-caption-position` defaults to above — [pandoc manual](https://pandoc.org/MANUAL.html); [pandoc man page](https://man.archlinux.org/man/pandoc.1.en.txt)
- Math: "It will appear verbatim surrounded by `\(...\)` (for inline math) or `\[...\]` (for display math)" — [pandoc manual](https://pandoc.org/MANUAL.html)
- Raw LaTeX: "pandoc allows raw LaTeX, TeX, and ConTeXt to be included in a document" (`raw_tex`). Environments such as `tabular` are passed through. `header-includes` adds preamble content — [pandoc manual](https://pandoc.org/MANUAL.html)
- Figures: an image alone in a paragraph with alt text becomes a captioned figure. LaTeX placement can be set with an attribute — [pandoc manual](https://pandoc.org/MANUAL.html)
- Cross-references: native support covers only heading references (implicit header references). `native_numbering` applies only to odt and docx. **pandoc-crossref** handles numbering and references for figures, equations and tables, emits LaTeX `\label`/`\ref` (optionally cleveref), and must match the pandoc version it was built against — [pandoc manual](https://pandoc.org/MANUAL.html); [pandoc-crossref](https://github.com/lierdakil/pandoc-crossref)
- Templates: `--template FILE` takes a custom LaTeX template. The usual approach is `pandoc -D latex > mytemplate.tex`, then editing it. Custom author fields such as affiliation and email fail with the default template — [pandoc manual](https://pandoc.org/MANUAL.html); [Danny Quah gist (2020, older)](https://gist.github.com/DannyQuah/04b46cd583f0e87cea7b5009adfb9c5d)
- There is no official pandoc template for NeurIPS. A community Quarto extension exists, and its author says the PDF route takes the most work to meet the guidelines. NeurIPS 2026 ships `neurips_2026.sty`, and editing the style files can lead to desk rejection — [quarto-neurips-template](https://stevengogogo.github.io/quarto-neurips-template); [thesify (third party, unverified)](https://www.thesify.ai/templates/neurips-2026-latex-template)

### Inferences
- Pandoc's default template is not compatible with `neurips_2026.sty` or the ICLR style. A full build would need a custom template that loads the official `.sty`, with author blocks and the checklist adapted. That is a lot of work for one paper.
- A one-shot conversion is more efficient: `pandoc paper.md --natbib -t latex -o body.tex`, without `-s`, gives the body only. Paste it into the official `main.tex`, then fix by hand: replace longtable with `table`/`tabular` floats (or `\input` the Python-generated tables), add `\label`/`\ref`, and check `\citep`/`\citet`. After that, maintain the `.tex` as the source of truth rather than re-running pandoc. Running two sources in parallel causes drift.
- `--citeproc` should be avoided for NeurIPS, ICLR and arXiv. Venues expect natbib with BibTeX (`\bibliographystyle`). Since Nov 2025, arXiv can process the `.bib` itself.
- Workshop versions mostly change the style (`\usepackage[...]{neurips_2026}` or the ICLR `.sty`) and the page limit. Once the source is `.tex`, moving from arXiv to a workshop is a template swap, which pandoc would make harder, not easier.

### Gaps
- The pandoc 3.9 and 3.10 changelogs were not read. Changes in 2026 to table or cross-reference output are not verified.
- I found no 2024–2026 community benchmark comparing pandoc conversion against writing `.tex` directly for ML papers.
- I could not confirm the official NeurIPS 2026 and ICLR 2026/2027 workshop style details from primary sources (neurips.cc, iclr.cc).

## Writing tables from Python directly as .tex (booktabs)

### Takeaway
Generating booktabs tables straight from the Python script with pandas `Styler.to_latex(hrules=True, ...)`, then pulling them in with `\input{tables/x.tex}`, is more reliable than converting Markdown tables. It gives floating `table` environments with caption and label that fit the official templates, and the tables regenerate whenever the data changes.

### Cited Findings
- pandas 3.1.1 `Styler.to_latex`: `hrules=True` adds `\toprule`, `\midrule` and `\bottomrule` (booktabs). It also takes `caption` (as a string or as (full, short)), `label` for `\label{}`, `position` (e.g. `[h!]`), `position_float="centering"`, `column_format`, `siunitx=True` (numeric columns as `S`), and `environment="longtable"` optionally — [pandas docs](https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.to_latex.html)
- Required packages: booktabs for hrules, multirow for sparse rows, siunitx, `xcolor[table]` for colors, longtable when used — [pandas docs](https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.to_latex.html)
- Example: `s.to_latex(column_format="rrrrr", position="h", position_float="centering", hrules=True, label="table:5", caption="...")` yields a `table` environment with `\centering`, caption, label and booktabs rules — [pandas docs](https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.to_latex.html)
- By contrast, pandoc's default Markdown-table output is a non-floating longtable — [pandoc manual](https://pandoc.org/MANUAL.html)

### Inferences
- Recommended: the script writes `tables/*.tex` (a booktabs `table` float, `\label{tab:...}`, numbers formatted in Python). The paper uses `\input{tables/...}` and `\ref{tab:...}`. NeurIPS and ICLR styles already recommend booktabs-style tables. Add `\usepackage{booktabs}` if the template does not load it.
- Escaping: underscores and `%` in column names must be LaTeX-escaped (Styler has `escape` options through `format`, not verified here). Bold for best results can be applied via Styler, which needs `etoolbox`/`\robustify` with siunitx.
- With Overleaf free (no Git), every table regeneration means a manual upload. Locally, or on Overleaf with Git (paid), the tables stay in sync automatically.

### Gaps
- The `DataFrame.to_latex` page (vs `Styler.to_latex`) was not read. Its exact `escape` and booktabs defaults in pandas 3.x are not verified.
- I found no source on whether NeurIPS or ICLR checkers flag longtable. That longtable inside a two-column or limited-page style is a problem is an inference, not a sourced fact.
