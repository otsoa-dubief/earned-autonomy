# Reproduction trial on the clean snapshot (PLAN_SUITE T49, 18 November 2026)

Snapshot: `~/dev/autonomie-meritee-publication`, built by `publication/preparer_copie.sh`. Fresh virtual environment outside the repository: Python 3.14.7 (the study used 3.14.9), numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2, pytest 9.2.0, installed from PyPI in 8 s. No paid call. The snapshot run reads no file from `donnees/`, `pilote/` or `data/`; the comparison run in the full repository (below) reads `pilote/etape2/` through the engine tests.

## Results

| Step | Command (from the snapshot root) | Time | Result |
|---|---|---|---|
| Draw, offline | `python banc/tirage/tirage_public.py verifier --dossier experience/tirage --manifeste experience/manifeste_verdicts.txt` | < 1 s | « tirage vérifié » |
| Draw, online | same, with `--en-ligne` (re-reads NIST pulse 2031457) | a few s | « tirage vérifié » |
| Tables and figures | `outils/tables_article.py`, `outils/tables_exploratoires.py`, `outils/figures_article.py` (README, step 2) | 2.6 s | 7 files byte-identical to `article/`: `tables.md`, `tables_exploratoires.md`, `fig_budget.png`, `fig_gap.png`, `fig1_budget.pdf`, `fig2_gap.pdf`, `fig3_load.pdf` |
| Numbers of the paper | `python outils/verifier_chiffres.py` | < 1 s | « Écarts : 0 » |
| Engine tests | `cd simulation; python -m pytest -q rejeu/tests tests` | 24 s | 273 passed, 1 xfailed, 46 failed |
| Bench tests | `python -m pytest -q banc/tests` | 13 s | 667 passed, 36 skipped, 5 failed, 4 errors |
| Freeze tests | `python -m pytest -q gel/tests` | 8 s | 15 passed, 1 failed |
| Review reproductions | `python -m pytest -q revues/code/lanceur` | 13 s | 22 passed, 23 failed |

## Every failure accounted for

Same environment, same tests, run in the full working repository for comparison: engine 319 passed, 1 xfailed; bench 713 passed, 1 failed; freeze 16 passed; review reproductions 22 passed, 23 failed.

- **Engine, 46 failures**: all `FileNotFoundError` on `pilote/etape2/…`. These tests replay the pilot outputs, which are not published (README, « What is not provided »). All 319 pass in the full repository.
- **Bench, 4 errors and 3 failures** (`test_paires.py`, `test_tirage.py`): they read the benchmark checkouts in `externe/` (τ-bench 2.0 and WorkBench), which are not shipped; install them at the commits named in `banc/INSTALLATION.md`. Without them, one test parametrised over three τ-bench files is collected differently, hence 712 tests in the snapshot against 714 in the full repository.
- **Bench, 1 failure** (`test_lanceur_gel.py::test_verifier_gel_rend_le_commit_et_l_empreinte`) and **freeze, 1 failure** (`test_manifeste.py::test_apercu_du_vrai_depot`): they query the git tag `gel-2026-11-09` and the repository history; the snapshot has a single commit (the frozen folders are anchored instead, `publication/ANCRES.md`).
- **Bench, 1 failure** (`test_revue_ultra_banc.py::test_u3_pid_reutilise_n_est_pas_pris_pour_une_partie`): fails identically in the full repository, so it is not caused by the snapshot; its cause was not investigated.
- **Review reproductions, 23 failures**: identical in the full repository. These files reproduce the findings of the 6 November launcher review (`revues/code/2026-11-06_revue_lanceur.md`); they are kept as a record, not as a test suite of the final code.

## Change made to the snapshot during the trial

The first run stopped on `ModuleNotFoundError: aide_controle3`: the snapshot excluded the whole `simulation/controle3/` folder for its size. The script now excludes only its output folders `simulation/controle3/resultats*/` (simulation outputs, about 64 MB, for the Zenodo archive); the code, notes and small measurement files (9.3 MB, of which 8.3 MB of `.jsonl` measurements) are included. No secret or personal path in them (pattern search: only the text `env -u ANTHROPIC_API_KEY`).

## Not run here

The final replay itself (`python -m rejeu.bout_en_bout`, about 75 minutes on 12 processes) needs the wave folders, which are not in the snapshot; they belong to the data package (T50).
