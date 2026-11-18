# Earned autonomy for AI agents: raw data of the pre-registered study

Data deposit of the study pre-registered on OSF (priority record 7ju3c, preregistration vycge, verdict freeze cusv6). This deposit: doi:10.5281/zenodo.24331245. Results deposit: doi:10.5281/zenodo.24321214. Code: https://github.com/otsoa-dubief/earned-autonomy, archived as doi:10.5281/zenodo.24331243.

## What this is

`earned_autonomy_data_2026-11-18.zip` holds exactly the 68,990 files listed in the verdict-freeze manifest, byte for byte, with no file added, removed or edited:

- the manifest is `manifeste_verdicts.txt` (copied here), SHA-256 `904aa8d3…f88d`, recorded in the verdict-freeze registration cusv6 on 14 November 2026 at 08:17:47 UTC;
- every file of the archive has the SHA-256 given for it in the manifest (checked when the archive was built, and again by re-reading the archive).

Inside the archive, paths start with `experience/`. Unzip it at the root of the code repository and every file is where the final-replay command expects it (command in the README of the results deposit and in cusv6).

To check every file against the manifest, after unzipping at the repository root: `cd experience && shasum -a 256 -c manifeste_verdicts.txt` (the code repository already holds the manifest in `experience/`; otherwise copy the deposited `manifeste_verdicts.txt` there first; its paths are relative to `experience/`). Unzipping at the root also writes the 70 files of `audit_sans_alerte/` and `retraits_motif_a/`, some of which the code repository already holds: they are the same files, with the same hashes.

The archive was also tested with a second tool (`unzip -tq`: « No errors detected in compressed data »).

## Layout

| Path (under `experience/`) | Files | Content |
|---|---|---|
| `vague1/2026-11-10_06-19-06/` | 5,609 | wave 1 (started 10 November 2026, 05:19 UTC) |
| `vague2/2026-11-10_19-53-13/` | 63,310 | wave 2 (started 10 November 2026, 18:53 UTC; ended 13 November) |
| `audit_sans_alerte/` | 67 | audit of writes without an alert (sample, blind sheets, answers, decision) |
| `retraits_motif_a/` | 3 | task withdrawals for a defective task (reason A) and the author's objections |
| `gel_plan.json` | 1 | freeze record of the plan read by the replay engine |

In each wave folder:

| Path | Content | Written by |
|---|---|---|
| `parties/` | one folder per episode: the benchmark's own output (τ-bench 2.0 `results.json`; WorkBench prediction `.csv`) | the benchmarks, copied by `banc/lanceur.py` |
| `taches/` | the WorkBench task file of each WorkBench episode | `banc/lanceur.py` |
| `logs/` | one log per attempt | `banc/lanceur.py` |
| `usage/` | one JSONL per attempt: tokens and returned model name for each API call | `banc/usage_tau2.py`, `banc/usage_wrap.py` |
| `ecartees/` | attempts excluded and declared (e.g. empty agent message), with their reason | `banc/lanceur.py` |
| `actions.csv`, `actions_typees.csv` | every agent action with its verdict by exact comparison, then its action type | `banc/verdicts_csv.py`, `banc/typage.py` |
| `cout.json` | one line per attempt: tokens, cost, status | `banc/lanceur.py`, `banc/cout_v2.py` |
| `plan_de_jeu.json`, `ordre_de_jeu.csv`, `tentatives.jsonl` | planned episodes, seeded order, start and end events of each attempt | `banc/lanceur.py` |
| `journal.log`, `journal_complet.log` | console log (does not name the model of WorkBench attempts) and full log | `banc/lanceur.py` |
| `rapport_vague.json`, `.txt` | wave report (cost, spend, stopping thresholds) | `banc/lanceur.py` |
| `modeles_renvoyes.json`, `outils_agent.json` | returned model names; agent tools seen | `banc/lanceur.py` |
| `reussite.csv`, `.json`, `.txt` | task success by state check, computed at the final replay | `banc/reussite.py` |
| `relecture/` | alert review: blind sheets, reviewers' answers, agreement, decisions | `banc/relecture/` |
| `vague2.json` (wave 1 only) | marker closing wave 1 when wave 2 started | `banc/lanceur.py` |

Formats and the reasons for each file are documented in the repository: `banc/CHOIX_LANCEUR.md` (choices 18, 19, 26, 40), `banc/INSTALLATION.md`, `banc/relecture/CONSIGNE_RELECTURE.md`. Most names and columns are in French.

## Notes

- **Personal data.** No real person's data. The e-mail addresses that appear (24 distinct `@gmail.com` addresses) are those of the benchmarks' fictitious users; all 24 are in the benchmarks' own data. Pattern search on 18 November 2026: no API key, no address of the author, no other personal name found.
- **Local paths.** Logs contain the author's local path to the repository (`/Users/Otsoa/dev/autonomie-meritee`); it carries no information beyond the folder layout. The files are not edited, so that they keep the hashes of the manifest.
- **Pilot data are not included.** The pilot on development tasks is not part of the study's evidence.
- **Licences.** Data under CC BY 4.0 (`LICENSE-TEXT`). The tasks and the benchmark outputs derive from τ-bench 2.0 (Sierra Research; its banking domain comes from τ-Knowledge) and WorkBench (Styles et al.), both under the MIT licence; their notices are in `THIRD_PARTY_NOTICES`. Please cite the benchmarks' papers along with this deposit.
- **Funding and competing interests.** The API costs of the study were covered by credits from Anthropic's startup programme (Claude for Startups), granted to the author's micro-enterprise, which builds AI-agent services and uses Claude models among others; Anthropic had no role in the study.

Contact: Otsoa Dubief, otsoa.dubief@gmail.com.
