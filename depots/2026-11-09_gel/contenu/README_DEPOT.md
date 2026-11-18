# Earned autonomy for AI agents: preregistration of the frozen experiment plan (9 November 2026)

**This is the preregistration of the experiment.** The plan, the rule, the replay engine, the benchmark instrumentation and the freeze manifest are frozen at git tag `gel-2026-11-09` (commit `a8eb1aae06d237ff094933f30d4a9ddf045d4898`), before any confirmatory data are collected. An earlier priority record of the working state was registered on OSF on 5 November 2026 (https://osf.io/7ju3c/).

- Author: Otsoa Dubief (ORCID [0009-0002-7322-7575](https://orcid.org/0009-0002-7322-7575)).
- Code and documents were written with the help of Claude (Anthropic), under the author's direction.
- Working language of the documents: French. The article will be in English.

## Research question

Which open protocol would let any organisation delegate progressively to an AI agent, per type of action, on verified evidence, with guarantees that can be checked and revoked?

The rule under test grants autonomy on an action type after a run of verified successes whose length is computed in advance from an error budget, and withdraws it at the first error. It is replayed offline on recorded agent episodes from public benchmarks (τ-bench 2.0, WorkBench). Every write action is judged by exact comparison with the task's expected actions, without any AI judge.

## The freeze

- Git tag: `gel-2026-11-09`; commit `a8eb1aae06d237ff094933f30d4a9ddf045d4898`; tree `589cea1d9a4701e256173049c619626f63ed3222`.
- Master seed G0, drawn once at the freeze and written in the plan: `9879107140414210923`.
- SHA-256 of `gel/MANIFESTE_SHA256.txt` (the freeze manifest, which lists the SHA-256 of every frozen file): `88715a0d790cd5228b6a247b8e10b74d2c1c1ea022d47fbc9386949e263b9600`.
- The commits of the two benchmarks (τ-bench 2.0 `033bf08`, WorkBench `49c7dfd`) and the Python environments are recorded in `gel/GEL.json` and `gel/environnements/`, not in the manifest.
- Check: the manifest lines outside `externe/` can be checked in this deposit (`shasum -a 256 -c` on those lines, from the deposit root). The `externe/` lines need clones of the benchmarks at commits `033bf08` (sierra-research/tau2-bench) and `49c7dfd` (olly-styles/WorkBench), placed under `externe/`; the `externe/workbench-run/` lines are local run files of the WorkBench benchmark, outside both git repositories, checked on the author's machine and revealed on request. In a full checkout of the tag with those clones, `gel/manifeste.py --verifier` also compares the packages of the three Python environments (`gel/environnements/`) and the files of `externe/workbench-run/`: it reports no difference only with the same environments and the same run files; otherwise it lists them as differences.

## What this deposit contains

| Path | Content |
|---|---|
| `REGLE.md` | The rule and all dated design decisions. |
| `PLAN_EXPERIENCE.md` | The **frozen** experiment plan: hypotheses, analysis, decision rules, replay engine specification, budget. |
| `JOURNAL_CHANGEMENTS.md` | Every change made after the pilot, with its reason and who decided it (state at the freeze). |
| `simulation/` | Simulations (E1 and the control-3 checks of the verdict) and the replay engine that computes the confirmatory analysis. |
| `banc/` | Benchmark instrumentation: per-action verdicts, action typing, cost accounting, launcher, review tools, tests. |
| `gel/` | Freeze manifest, Python environments and the freeze script. |
| `reports/` | Literature reports written for the project. |

The pilot (`pilote/` in the repository) used only development tasks, excluded from any confirmatory analysis.

## What is committed by hash only

The following entries of the tagged commit are **not** included here; their git object hashes commit to their exact content (`git ls-tree a8eb1aa`):

| Entry | Git object |
|---|---|
| `ATTENTE.md` (personal planning notes) | blob `5bcf1e6c9660b333d81937f288f758a46d78796b` |
| `CADRE.md` (framing, budget, earlier field study) | blob `6ef154f65b51bcd03d8f1a2d338c53553a40185c` |
| `SUIVI.md` (working log) | blob `2d38f40f709b3da2b46e8faaa9bd03b4100943d2` |
| `donnees/` (sealed file and confidential field data) | tree `091445e3ceb8dee52b7484e7b4b86fa331062615` |
| `lectures/` (reading notes) | tree `290ec08df0fad4d095f01832ad2fac6e293985de` |
| `notes/` (field note on confidential logs) | tree `8c01b50ee879b5d2398c695be35e5d917f847ca2` |
| `pilote/` (pilot outputs, development tasks only) | tree `3d7a7a9b17a8e3be7654665df445c83d181bb0c7` |
| `research_notes/` (raw research notes) | tree `bcfe317a02aaa61c0deebbc7ab3ffd3d86d16fdd` |
| `revues/` (independent reviews of the protocol) | tree `7d0739d37b95d3d5cfa8ae0cf28e2c0bb115704e` |
| `depots/` (OSF deposit records (sheets and package builder)) | tree `2e8410bbee32f0ba79ade5642db5d4a389dbd704` |

`MANIFEST_SHA256.txt` gives the SHA-256 of every file extracted from the commit (all files here except this README, `LICENSE-CODE.txt`, `THIRD_PARTY_NOTICES.txt` and the manifest itself).

## Licence

- Documents and data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Code (`banc/`, `simulation/`, `gel/`): MIT License, see `LICENSE-CODE.txt`.
- Files derived from the public benchmarks remain under their own MIT licenses, reproduced in `THIRD_PARTY_NOTICES.txt`:
  - τ-bench 2.0 (sierra-research/tau2-bench, commit 033bf08): `banc/outils_agent/aviation.json`, `banc/outils_agent/commerce.json`, `banc/outils_agent/banque.json`, `banc/refus_banque.json`.
  - WorkBench (olly-styles/WorkBench, commit 49c7dfd): `banc/outils_agent/workbench.json`, `banc/tests/fixtures/pilote_workbench/`.

## Résumé en français

Préenregistrement, daté du 9 novembre 2026 : plan d'expérience figé, règle, moteur de rejeu, instrument et manifeste du gel, à l'étiquette git `gel-2026-11-09`, avant toute donnée de confirmation. Le reste du dépôt git est engagé par ses empreintes. Les fichiers tirés de τ-bench et de WorkBench gardent leur licence MIT d'origine.
