# arXiv LaTeX compilation environment and ML workshop templates (status at 17 Nov 2026)

## Which TeX Live does arXiv use in 2026, and what is its update schedule? Which engines?

### Takeaway
As of mid-November 2026, arXiv's official help pages still list only **TeX Live 2025 (the default; tree frozen 2025-08-03) and TeX Live 2023**. TeX Live 2026 (released March 2026) has **not** been announced on arXiv. The safe engine is **pdfLaTeX**. XeLaTeX was added in November 2025 but does not reliably show up in the UI. LuaLaTeX is not supported.

### Cited Findings
- "arXiv supports TeX Live 2023 and TeX Live 2025, with 2025 being the default." The trees are dated 2023-05-21 (TL2023) and 2025-08-03 (TL2025) — [arXiv TeX Live FAQ](https://info.arxiv.org/help/faq/texlive.html)
- After a tree goes into production, arXiv does not update it with tlmgr, except for critical bug fixes. The stated policy is to update "every few years". All past trees are kept so that papers are rebuilt with the tree in effect when they were submitted — [arXiv TeX Live FAQ](https://info.arxiv.org/help/faq/texlive.html)
- The 10 Sep 2025 blog post announced TeX Live 2025 on arXiv. It says arXiv will follow the annual releases and offer only the two most recent versions: "When TeX Live 2026 is released, the choices will be 2025 and 2026" and TL2023 will be dropped — [arXiv blog, 2025-09-10](https://blog.arxiv.org/2025/09/10/tex-live-2025-on-arxiv). Note the tension with "every few years" in the FAQ.
- TeX Live 2026 was released in March 2026 — [N. Preining blog](https://www.preining.info/blog/2026/03/tex-live-2026-released/). Overleaf warns that projects that compiled under TL2025 can fail under TL2026 because of kernel and package changes — [Overleaf blog](https://www.overleaf.com/blog/tex-live-2026-is-now-available)
- I checked the arXiv blog's first page (posts from 28 Jul to 6 Nov 2026). None of them mention TeX Live 2026 or the compilers. They cover the October 2026 cloud database migration and the arXiv-CE modernization — [arXiv blog](https://blog.arxiv.org/)
- The `00README` page (JSON) lists `texlive_version`: `2025` (current) and `2023` (previous) — [arXiv 00README](https://info.arxiv.org/help/00README.html)
- AutoTeX (Submission 1.0) was retired in April 2025 when Submission System 1.5 rolled out — [arXiv submit_tex](https://info.arxiv.org/help/submit_tex.html); [arXiv blog Submission 1.5](https://blog.arxiv.org/2025/09/10/attention-authors-submission-1-5-and-other-updates). The current system is no longer formally called "AutoTeX".
- Supported processors: TeX, LaTeX (DVI), LaTeX (PDF mode), and pdfLaTeX ("fully supported", detected automatically) — [arXiv submit_tex](https://info.arxiv.org/help/submit_tex.html). Values accepted by `process.compiler`: `tex`, `pdftex`/`pdfetex`, `latex`, `pdflatex`, `xelatex` — [arXiv 00README](https://info.arxiv.org/help/00README.html)
- XeLaTeX and direct PDF(e)TeX output for plain TeX were added in November 2025. LuaTeX is "under consideration", not supported — [arXiv blog, 2025-11-05](https://blog.arxiv.org/2025/11/05/attention-authors-updates-for-bib-file-processing-and-tex-in-arxiv-submissions). A reader comment from 26 Nov 2025 says xelatex is missing from the "Select Compiler" menu (only tex, latex, pdflatex appear) — same page.
- **Contradiction**: the "Common mistakes" page still says "XeTeX, LuaTeX, LyX, and PDFTeX aren't supported". That page is out of date compared with the November 2025 blog post — [arXiv mistakes](https://info.arxiv.org/help/faq/mistakes.html)
- Known TL2025 incompatibilities:
  - `cleveref` was not updated, so every `\cref` shows the same name. Workaround: `zref-clever`, `\crefalias`, or select TL2023.
  - `array`: workaround is `\usepackage{array}[=2016-10-06]`.
  - Loading a package inside a group (e.g. `setspace`) is now an error.
  - `minted` v3.
  - `hyperxmp` must be loaded after `hyperref`.
  - Source: [arXiv TeX Live FAQ](https://info.arxiv.org/help/faq/texlive.html)
- Aside: arXiv's HTML version is produced by LaTeXML (latexml_oxide) on an embedded "TL2023 dump", for example in a log dated 2026-08-24. That pipeline is separate from PDF compilation — [arXiv log 2603.03091](https://arxiv.org/html/2603.03091v1/__stdout.txt)

### Inferences
- To reproduce arXiv locally: target **TeX Live 2025 + pdfLaTeX**. An up-to-date local TL2026 (MacTeX 2026) is *newer* than arXiv. A document that uses TL2026-only features (new kernel, tagging) may fail on arXiv. The reverse is less likely but possible because of the kernel changes Overleaf reported.
- Option 1: install MacTeX/TeX Live **2025** (historic archive) alongside 2026. Option 2: test with Overleaf set to TL2025.
- If arXiv adds TL2026 (per the 2025 policy), TL2025 will remain selectable, so targeting TL2025 stays valid either way.
- The one-tree-per-submission rule means updates (v2, v3) are rebuilt with the TL chosen at upload time. Pin it with `texlive_version` in `00README`.

### Gaps
- I found no official arXiv announcement, as of 17 Nov 2026, on whether or when TL2026 will be offered. Only the first page of the blog was checked, but it covers July–November 2026.
- I found no precise list of the package versions in arXiv's TL2025 tree (beyond biblatex/biber, see below).

## How does arXiv handle .bib vs .bbl? natbib vs biblatex/biber

### Takeaway
Since November 2025, arXiv **runs BibTeX/Biber itself** if you upload the `.bib`, so a `.bbl` is optional. If you upload a `.bbl`, arXiv uses it as is. It must then carry the same name as the main `.tex`, come from the same tool (BibTeX vs Biber), and, for biblatex, use **bbl format 3.3 (biblatex 3.20 / Biber 2.20, TL2025)**. natbib + BibTeX (`.bst`) is the robust path. A natbib `.bbl` has no format version.

### Cited Findings
- "Authors no longer need to upload precompiled .bbl files". Upload the `.bib` and arXiv runs the right programs (effective week of 5 Nov 2025) — [arXiv blog, 2025-11-05](https://blog.arxiv.org/2025/11/05/attention-authors-updates-for-bib-file-processing-and-tex-in-arxiv-submissions)
- If a `.bbl` is uploaded, arXiv uses it. It must share the main `.tex` file's name. With no `.bbl`, if a needed `.bib` is missing, the submission is blocked. bibtex8/upbibtex require a precompiled `.bbl` — [arXiv submit_tex](https://info.arxiv.org/help/submit_tex.html)
- arXiv runs the backend declared in biblatex (biber, bibtex, bibtex8), otherwise bibtex. "Your paper and `.bbl` must come from the same program" — don't mix Biber and BibTeX output — [arXiv submit_tex](https://info.arxiv.org/help/submit_tex.html)
- biblatex versions:
  - TL2025: biblatex 3.20, Biber 2.20, bbl format 3.3 (**only 3.3 accepted**).
  - TL2023: biblatex 3.19, Biber 2.19, bbl format 3.2 (3.2 and 3.3 accepted).
  - An incompatible `.bbl` produces a warning.
  - Source: [arXiv submit_tex](https://info.arxiv.org/help/submit_tex.html); same rule on [arXiv mistakes](https://info.arxiv.org/help/faq/mistakes.html)
- A bundled old `biblatex.sty` causes "Patching \MakeUppercase failed" — [arXiv TeX Live FAQ](https://info.arxiv.org/help/faq/texlive.html)
- Community reports of `numeric-comp.dbx` / `authoryear.dbx` not found and "wrong format version" errors on arXiv — [tex.SE arxiv tag (mirror)](https://backiee.wasmer.app/https_tex_stackexchange_com/questions/tagged/arxiv); [DEV Community](https://dev.to/saurabh_shah/arxiv-doesnt-run-bibtex-thats-why-your-references-show-as--55i0). The DEV post title says "arXiv doesn't run BibTeX", which predates or contradicts the November 2025 change, so it is outdated.

### Inferences
- natbib + BibTeX (which NeurIPS and ICLR use) avoids the bbl-format trap. The `.bbl` generated by BibTeX + `.bst` is plain LaTeX, compatible across versions. Safest: upload `.bib` **and** a `.bbl` regenerated locally, named like the main file.
- A local TL2026 produces biblatex `.bbl` files in a newer format. biblatex/biber in TL2026 are probably > 3.20/2.20, but I did not verify the exact version. That `.bbl` would risk rejection on TL2025. Another reason to avoid biblatex for these templates.
- Don't mix biblatex with the ICLR/NeurIPS templates: both load natbib by default (NeurIPS has `nonatbib`, ICLR has no option).

### Gaps
- I found no source on which bibtex/`.bst` versions are installed on arXiv (presumably the ones in TL2025).
- When a `.bib` **and** a `.bbl` are both present, priority isn't explicit beyond "If you upload a .bbl, arXiv uses it".

## Figures, files and known rejection causes

### Takeaway
pdfLaTeX on arXiv accepts only **PDF, PNG, JPG**, with no automatic conversion (no EPS). Relative paths, file names without spaces or special characters, no shell-escape, every non-TL file included, auxiliary files excluded.

### Cited Findings
- pdfLaTeX: JPEG, PNG, PDF only; "no automatic conversion". DVI/TeX: PS/EPS only. `psfig` is unsupported — [arXiv submit_tex](https://info.arxiv.org/help/submit_tex.html); [arXiv mistakes](https://info.arxiv.org/help/faq/mistakes.html)
- Rejection causes:
  - Absolute paths.
  - Spaces, `/ \ : &` in names, which get converted to `_`.
  - `\include` from a subdirectory, since only the top level is writable; use `\input`.
  - Missing custom `.sty`/`.cls`.
  - Modified standard packages.
  - Interactive prompts.
  - `\ifx\pdfoutput\undefined` (use `ifpdf`).
  - hyperref pdfmarks on long papers (`bookmarks=false`).
  - `\Bbbk` already defined (newtxmath + amssymb).
  - `\cite` in `\caption` without `\protect`.
  - minted with `--shell-escape` or a `.minted-cache` directory.
  - Source: [arXiv mistakes](https://info.arxiv.org/help/faq/mistakes.html)
- Exclude `.aux/.log/.pdf`. Include `.bbl/.ind/.gls` if needed. Compile from the root. Hidden files are deleted at announcement. Avoid `\today` and double-spaced referee mode. You must view the generated PDF before finishing — [arXiv submit_tex](https://info.arxiv.org/help/submit_tex.html)
- TL2020+: sources must be UTF-8 by default — [arXiv TeX Live FAQ](https://info.arxiv.org/help/faq/texlive.html)

### Inferences
- matplotlib figures exported to PDF: check that their fonts are embedded (Type 42/TrueType embedded or Type 1), because NeurIPS rejects Type 3 fonts (see below). `pdf.fonttype=42` in matplotlib is the usual fix. This is general knowledge and not covered by the sources above.

### Gaps
- I did not check arXiv's size limits (overall and per file).

## Workshop templates: NeurIPS 2026 and ICLR 2026 — packages, engine, natbib, fonts

### Takeaway
Both templates assume **LaTeX2e + pdfLaTeX**, **natbib** (author-year for ICLR), **Times** through PostScript fonts (`ptm`/`phv`, provided by TeX Live's base fonts), and **US Letter**. NeurIPS requires **only Type 1 or embedded TrueType fonts (no Type 3)** and recommends `pdflatex` directly. The NeurIPS 2026 template has a built-in workshop option (`dblblindworkshop`/`sglblindworkshop` + `\workshoptitle`). ICLR 2026 does not, so workshops tweak the header.

### Cited Findings
**NeurIPS 2026**
- Official style zip: https://media.neurips.cc/Conferences/NeurIPS2026/Formatting_Instructions_For_NeurIPS_2026.zip — [NeurIPS 2026 CfP](https://neurips.cc/Conferences/2026/CallForPapers)
- `\ProvidesPackage{neurips_2026}[2026-01-29 ...]`.
  - Options: `final`, `preprint`, `nonatbib`, `main`, `position`, `eandd`, `creativeai`, `sglblindworkshop` (not anonymous), `dblblindworkshop` (anonymous), `nonanonymous`.
  - `\workshoptitle{...}` sets the workshop name.
  - Loads `environ`, `natbib` (unless `nonatbib`), `geometry[letterpaper]`, and `lineno` (submission only).
  - Doesn't load `times`; sets `\rmdefault=ptm`, `\sfdefault=phv`.
  - Only `\NeedsTeXFormat{LaTeX2e}`, no named engine.
  - Source: copy of `neurips_2026.sty` hosted at [UVic](https://web.uvic.ca/~nmehta/incentives_and_machine_learning_spring2026/neurips_2026.sty) (a third-party copy, not the official neurips.cc file)
- Formatting instructions:
  - "Times New Roman is the preferred typeface throughout, and will be selected for you by default".
  - natbib is loaded by default.
  - Author-year or numeric citations, any reference style as long as it's consistent.
  - `\PassOptionsToPackage{options}{natbib}` before loading.
  - US Letter.
  - "Your PDF file must only contain Type 1 or Embedded TrueType fonts".
  - "You should directly generate PDF files using pdflatex".
  - Check with `pdffonts`.
  - Avoid `\bbold` (bitmap fonts); use `amsfonts` `\mathbb`.
  - "If your file contains type 3 fonts or non embedded TrueType fonts, we will ask you to fix it".
  - `\usepackage[pdftex]{graphicx}`.
  - 9 content pages. The checklist is mandatory for the main track.
  - `preprint` option for arXiv: non-anonymized, footer "Preprint. Work in progress.".
  - Source: [Formatting Instructions For NeurIPS 2026 (Overleaf PDF)](https://www.overleaf.com/latex/templates/formatting-instructions-for-neurips-2026/bjdwqfdkyftc.pdf)
- **Version conflict**: the Overleaf PDF lists only 3 options (`final`, `preprint`, `nonatbib`), while the 2026-01-29 `.sty` defines the track and workshop options. Mirrors mix older drafts — [search summary / Overleaf pages](https://www.overleaf.com/latex/templates/formatting-instructions-for-neurips-2026/bjdwqfdkyftc.pdf). Check against the official zip.

**ICLR 2026**
- Repo [ICLR/Master-Template](https://github.com/ICLR/Master-Template) contains `iclr2026/` and already an `iclr2027/` folder (plus `iclr2027.zip`).
- `iclr2026_conference.sty`:
  - Loads `eso-pic`, `fancyhdr`, `natbib` (no options).
  - `\setcitestyle{authoryear,round,citesep={;},aysep={,},yysep={;}}`.
  - Font `phvb` for the line-number ruler.
  - No `times` loaded in the `.sty`.
  - No workshop option; only `\iclrfinalcopy`, which switches the header "Under review as..." to "Published as a conference paper at ICLR 2026".
  - Source: [iclr2026_conference.sty](https://raw.githubusercontent.com/ICLR/Master-Template/master/iclr2026/iclr2026_conference.sty)
- `iclr2026_conference.tex`:
  - `\usepackage{iclr2026_conference,times}`, `hyperref`, `url`, `\input{math_commands.tex}`.
  - `\bibliographystyle{iclr2026_conference}` (`.bst` supplied), `\citet`/`\citep`.
  - "pdflatex is recommended", PDF figures instead of EPS.
  - US Letter.
  - 9 pages (10 for camera-ready).
  - Don't change margins or sizes.
  - No mention of Type 1 fonts or workshops.
  - Source: [iclr2026_conference.tex](https://raw.githubusercontent.com/ICLR/Master-Template/master/iclr2026/iclr2026_conference.tex)

### Inferences
- Minimum local requirements for both templates: pdfLaTeX, the packages `natbib`, `fancyhdr`, `eso-pic`, `geometry`, `lineno`, `environ`, `times`/`psnfss` (ptm/phv fonts, Type 1 via URW), `hyperref`, `url`, `graphicx`, `amsfonts`/`amssymb`, `booktabs`. All are in TL2025, but this wasn't verified package by package. A full MacTeX covers them; BasicTeX would require `tlmgr install` for some.
- No conflict with arXiv: same engine (pdfLaTeX), natbib + BibTeX, PDF/PNG figures. The `.sty` and `.bst` files must be **uploaded with the source**. They aren't in TeX Live.
- ML workshops (NeurIPS 2026 / ICLR 2027) usually publish their own variant of the conference `.sty`. Check each workshop's CfP. Don't confuse ICLR 2026 (April 2026, already past) with ICLR 2027 (template already available).
- For the arXiv version of a NeurIPS paper: `\usepackage[preprint]{neurips_2026}`. Use `final` only if the paper is accepted, and possibly `dblblindworkshop,final` + `\workshoptitle{...}` for an accepted workshop paper. This is inferred from the option semantics in the `.sty`.

### Gaps
- I couldn't read the official neurips.cc zip directly. The `.sty` cited is a third-party copy dated 2026-01-29.
- The precise `iclr2027` contents (changes vs 2026) weren't checked.
- I found no official ICLR rule on Type 1 fonts (only NeurIPS states one).

## arXiv's recommendations for checking a submission locally

### Takeaway
arXiv publishes no dedicated "local check" procedure. Its advice: compile the **final** source exactly as submitted, from the root, with the same TL version, and review the log and the PDF generated by arXiv before finishing.

### Cited Findings
- Recompile the final source before submitting ("untested last-minute edits") — [arXiv mistakes](https://info.arxiv.org/help/faq/mistakes.html)
- Review the processing log and the PDF; viewing the PDF is mandatory before completing submission — [arXiv submit_tex](https://info.arxiv.org/help/submit_tex.html); [arXiv blog 2025-09-10](https://blog.arxiv.org/2025/09/10/tex-live-2025-on-arxiv)
- If you develop with an older or newer biblatex, regenerate the `.bbl` with the same TL as arXiv — [arXiv mistakes](https://info.arxiv.org/help/faq/mistakes.html)
- `00README` (JSON) pins the compiler, top-level file, TL version and ignored files. Example: `{"texlive_version": 2025, "process": {"compiler": "pdflatex"}, "sources": [{"filename": "main.tex", "usage": "toplevel"}]}`. The system generates it at upload and may override the TL value. There's a key spelling inconsistency, `keep_comments` vs `keep_comment` — [arXiv 00README](https://info.arxiv.org/help/00README.html)
- Overleaf publishes an arXiv checklist — [Overleaf docs](https://docs.overleaf.com/troubleshooting-and-support/checklist-for-arxiv-submissions) (not read in detail)

### Inferences
Suggested local checklist:
1. Use TL2025 + pdflatex.
2. Clean build in a fresh copy of the folder containing only the files to upload (`latexmk -pdf`, then remove the aux files but keep the `.bbl`).
3. Check that `pdffonts` shows no Type 3 fonts and that every font is embedded.
4. No absolute paths, no `\include` from subfolders, no shell-escape.
5. Look for "wrong format version" or undefined citation warnings in the log.
6. Compare the PDF arXiv produces with the local PDF.

### Gaps
- I found no official arXiv tool for reproducing its compilation locally (no Docker image or published script).
