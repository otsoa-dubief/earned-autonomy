# Earned autonomy for AI agents: priority record of the working state (5 November 2026)

**This is not the preregistration of the experiment.** It is a timestamped record of the state of the project on 5 November 2026. The frozen experiment plan will be registered separately, before any confirmatory data are collected (planned for 18 November 2026).

- Author: Otsoa Dubief (ORCID [0009-0002-7322-7575](https://orcid.org/0009-0002-7322-7575)).
- Code and documents were written with the help of Claude (Anthropic), under the author's direction.
- Working language of the documents: French. The article will be in English.

## Research question

Which open protocol would let any organisation delegate progressively to an AI agent, per type of action, on verified evidence, with guarantees that can be checked and revoked?

The rule under test grants autonomy on an action type after a run of verified successes whose length is computed in advance from an error budget, and withdraws it at the first error. It is replayed offline on recorded agent episodes from public benchmarks (τ-bench 2.0, WorkBench). Every write action is judged by exact comparison with the task's expected actions, without any AI judge.

## What this record contains

| Path | Content |
|---|---|
| `REGLE.md` | The rule and all dated design decisions (4 and 5 November 2026). |
| `PLAN_EXPERIENCE.md` | Draft experiment plan (**not frozen**): open questions, replay engine specification, cost estimate. |
| `JOURNAL_CHANGEMENTS.md` | Every change made after the pilot, with its reason and who decided it. |
| `simulation/` | Exploratory simulation E1 (plan, code, results) that selected the rule family before any real data. |
| `banc/` | Benchmark instrumentation: per-action verdicts, action typing table, cost accounting, pilot launchers, alert review tools, frozen tool definitions, tests. |
| `reports/` | Literature reports written for the project. |

The pilot (`pilote/` in the repository) used only development tasks, drawn by a separate agent and excluded from any confirmatory analysis.

## What is committed by hash only

The project is versioned with git. This record is extracted from commit:

- commit `e82fb54ff24ddedba990c8d94d2ef23dbbe722f4`
- tree `64de79b0757db720414a6d79d5241006a070a117`

The commit hash commits to the whole repository. The following entries of that commit are **not** included here; their git object hashes commit to their exact content, which can be revealed and checked later (`git ls-tree e82fb54`):

| Entry | Git object |
|---|---|
| `ATTENTE.md` (personal planning notes) | blob `a1507a9167d96fdfbdab05d3879d636bcc6c169b` |
| `CADRE.md` (framing, budget, earlier field study) | blob `4930f7e55b69f68c02cdf27029e70c0921976e78` |
| `SUIVI.md` (working log) | blob `6c0bc9f58be6d8db3ea00e86bfd7e9fc2da281d0` |
| `donnees/` (sealed file and confidential field data) | tree `091445e3ceb8dee52b7484e7b4b86fa331062615` |
| `lectures/` (reading notes) | tree `290ec08df0fad4d095f01832ad2fac6e293985de` |
| `notes/` (field note on confidential logs) | tree `8c01b50ee879b5d2398c695be35e5d917f847ca2` |
| `pilote/` (pilot outputs, development tasks only) | tree `3d7a7a9b17a8e3be7654665df445c83d181bb0c7` |
| `research_notes/` (raw research notes) | tree `e6b4d891c26602ba712915eb0245082af8aa566b` |
| `revues/` (independent reviews of the protocol) | tree `3f313f7e54ee4628bd04623a866fd2b5290e268e` |

`MANIFEST_SHA256.txt` gives the SHA-256 of every file extracted from the commit (all files here except this README, `LICENSE-CODE.txt`, `THIRD_PARTY_NOTICES.txt` and the manifest itself).

## Licence

- Documents and data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Code (`banc/`, `simulation/`): MIT License, see `LICENSE-CODE.txt`.
- Files derived from the public benchmarks remain under their own MIT licenses, reproduced in `THIRD_PARTY_NOTICES.txt`:
  - τ-bench 2.0 (sierra-research/tau2-bench, commit 033bf08): `banc/outils_agent/aviation.json`, `banc/outils_agent/commerce.json`, `banc/outils_agent/banque.json`, `banc/refus_banque.json`.
  - WorkBench (olly-styles/WorkBench, commit 49c7dfd): `banc/outils_agent/workbench.json`, `banc/tests/fixtures/pilote_workbench/`.

## Résumé en français

Dépôt d'antériorité, daté du 5 novembre 2026 : ce n'est pas le préenregistrement. Il contient la règle, le plan d'expérience en projet (non figé), la simulation exploratoire E1, le code de l'instrument et les rapports de lecture. Le reste du dépôt git est engagé par ses empreintes. Les fichiers tirés de τ-bench et de WorkBench gardent leur licence MIT d'origine. Le plan figé sera déposé à part, avant toute donnée de confirmation.
