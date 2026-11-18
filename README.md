# Earned Autonomy for AI Agents

Code, documents and outputs of the pre-registered study *Earned Autonomy for AI Agents: A Pre-registered Error-Budget Test of Per-Action-Type Delegation* (Otsoa Dubief, independent researcher, ORCID 0009-0002-7322-7575). A French version of this file is `LISEZMOI.md`.

## The result

No configuration reached the pre-registered level of evidence required for delegation (pre-registered verdict R4). Only one of twelve configurations had enough volume to be judged; its error rate, 8.6% (lower bound 4.1%), is established above the 0.76% threshold. The other eleven had too little effective volume to conclude either way. Descriptively, 20 of 40 action types have an error rate established above their threshold; 13 show no observed error but too little volume to conclude. The rule was not refuted, but it was hardly put to the test, and its usefulness could not be judged. These rates count action errors confirmed by review against a single expected path per task. An exploratory check after the verdict found that 48 of the 79 errors of the judged type are one plot end-date discrepancy that the reviewers decided both ways; lifting it throughout keeps the excess established by two errors only (see the paper, Section 6.7 and Table X8).

The paper (`article/latex/main.pdf`) states the result, its limits and every deviation from the pre-registration.

## Chain of evidence

1. **Priority record** (OSF 7ju3c, 5 November 2026) and **preregistration** (OSF vycge, 10 November 2026, 05:00 UTC; frozen plan at git tag `gel-2026-11-09`, commit a8eb1aae). The registrations are under embargo until the paper is posted.
2. **Data collection** in two waves (10 to 13 November), every automated alert reviewed on blind sheets.
3. **Verdict freeze** (OSF cusv6, 14 November 2026, 08:17:47 UTC): SHA-256 manifest of every input of the final computation (`experience/manifeste_verdicts.txt`, 68,990 files, hash `904aa8d3…f88d`).
4. **Public draw** of the calibration/confirmation split from NIST beacon pulse 2031457 (17 November 2026, 08:18:00 UTC).
5. **Final replay**, run once with the deposited command (`experience/rejeu_final/`). It crashed once on a formatting defect of the frozen code; the fix replaced one function in memory and does not affect the label (`experience/NOTE_CORRECTIF_REJEU_FINAL.md`).
6. **Outputs deposited on Zenodo** on 17 November 2026: doi:10.5281/zenodo.24321214 (files under embargo until the paper is posted).
7. **Code and raw data**: this repository (https://github.com/otsoa-dubief/earned-autonomy), archived on Zenodo as doi:10.5281/zenodo.24331243; raw data (the 68,990 files of the verdict-freeze manifest) as doi:10.5281/zenodo.24331245.

## Repository layout

| Folder | Content |
|---|---|
| `REGLE.md`, `PLAN_EXPERIENCE.md` | the rule and the frozen plan (French, binding) |
| `JOURNAL_CHANGEMENTS.md` | dated log of every change and deviation |
| `banc/` | instrument: launcher, per-action verdicts, alert review, public draw |
| `simulation/` | replay engine (`simulation/rejeu/`) and pre-freeze simulations |
| `gel/` | freeze manifests and scripts |
| `experience/rejeu_final/`, `experience/exploratoire/`, `experience/tirage/` | final replay outputs, exploratory analyses (not pre-registered), draw files |
| `outils/` | scripts that build the paper's tables, figures and checks from the outputs |
| `article/` | the paper (Markdown sources, LaTeX, figures, tables, number register) |
| `revues/` | independent audits of the plan, the results and the paper |
| `depots/` | records of the OSF and Zenodo deposits |

## How to check

Requirements: Python 3.12 or later with numpy, scipy and matplotlib (the study used Python 3.14.9, numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2).

```bash
# 1. Check the public draw (add --en-ligne to re-read the NIST pulse online)
python banc/tirage/tirage_public.py verifier --dossier experience/tirage --manifeste experience/manifeste_verdicts.txt

# 2. Rebuild the paper's tables and figures from the replay outputs, then compare with article/
python outils/tables_article.py experience/rejeu_final /tmp/check
python outils/tables_exploratoires.py experience/exploratoire /tmp/check/tables_exploratoires.md
python outils/figures_article.py experience/rejeu_final /tmp/check
diff /tmp/check/tables.md article/resultats/tables.md

# 3. Check every number of the paper against its source file
python outils/verifier_chiffres.py
```

Expected answers: "tirage vérifié"; identical tables and figures; "Écarts : 0".

The final replay itself (`python -m rejeu.bout_en_bout`, command in the cusv6 registration and in the Zenodo README) needs the episode traces, published separately on Zenodo (doi:10.5281/zenodo.24331245), and about 75 minutes on 12 processes.

## What is not provided, and why

- Confidential field data and a sealed file from an earlier, separate study; personal notes; e-mail addresses of third parties.
- Four review documents dated 4 November 2026 and the notes `CADRE.md`, `ATTENTE.md` and `notes/`: they concern the earlier, separate field study and quote its confidential figures. The git hashes of the four reviews are listed in `publication/ANCRES.md`.
- Pilot outputs on development tasks (`pilote/`).
- The benchmarks themselves: use the official repositories at the commits named in `banc/INSTALLATION.md`.
- The full git history: it contains the files above. This repository is a clean snapshot; the commits cited in the registrations are anchored by the hashes of their public folders (see `publication/`), and the full history is kept, encrypted, by the author.

## Licences and citation

Code: MIT (`LICENSE`). Texts, tables, figures and data: CC BY 4.0 (`LICENSE-TEXT`). Benchmark material: see `THIRD_PARTY_NOTICES`. How to cite: `CITATION.cff`. Code, documents and the paper were written with the help of Claude (Anthropic), under the author's direction. Funding and competing interests: the API costs were covered by credits from Anthropic's startup programme; see the declaration in the paper.

Contact: Otsoa Dubief, otsoa.dubief@gmail.com.
