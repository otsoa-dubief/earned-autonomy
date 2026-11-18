# Exploratory analyses (not preregistered; no effect on the label R4)

All analyses below were run after the verdict, by `outils/analyses_exploratoires.py` (X1 to X6, 17 November 2026) and `outils/analyses_exploratoires_2.py` with `outils/analyses_exploratoires_2_dates.py` (X7 and X8, 18 November 2026), reading the frozen engine's outputs and functions without modifying them. The ρ = 1 lower bound recomputed by the script reproduces the engine's bound for all 20 established excesses.

## Table X1. Episodes excluded for an empty agent message, counted as errors (Exploratory, dated 17 November 2026; `A_ecart_avec_exclusions.csv`)

91 episodes were excluded after two failed attempts, all caused by an empty agent message (9 in wave 1, 82 in wave 2). On the calibration half, counting each as one confirmed error at the highest-stakes write type expected by its task adds 24 errors (2 episodes without an identifiable expected type), all in banking. Established excesses go from 20 to 21; the new one rests on 5 writes.

| environment | model | type | level | added | rate before | rate after | established before | established after |
|---|---|---|---|---|---|---|---|---|
| banking | haiku-5-5 | DUR | medium | 14 | 44.9 % | 47.3 % | True | True |
| banking | haiku-5-5 | MSG | low | 1 | 27.7 % | 27.9 % | True | True |
| banking | haiku-5-5 | ARG | high | 7 | 53.5 % | 55.0 % | True | True |
| banking | opus-5-5 | GAR | high | 2 | 0.0 % | 40.0 % | False | True |

## Table X2. Sensitivity of established excesses to false confirmations (Exploratory, dated 17 November 2026; `C_sensibilite_fausses_confirmations.csv`)

Largest share of confirmed errors that could be false alerts while the excess stays established (same ρ = 1 bound as the engine). For reference, in the author's blind review, agreement with the first reviewer was 13 of 15 in each wave, and 3 of the 10 confirmed alerts he reviewed were lifted.

| environment | model | type | level | writes | confirmed errors | bar | max share of false confirmations |
|---|---|---|---|---|---|---|---|
| banking | opus-5-5 | MSG | low | 124 | 10 | 1.161 % | 0 % |
| banking | sonnet-5-5 | MSG | low | 124 | 14 | 1.161 % | 30 % |
| airline | opus-5-5 | ARG | high | 71 | 6 | 0.008319 % | 31 % |
| WorkBench | opus-5-5 | ECR | low | 182 | 10 | 0.7575 % | 41 % |
| banking | sonnet-5-5 | ECR | low | 89 | 29 | 1.161 % | 45 % |
| WorkBench | sonnet-5-5 | ECR | low | 181 | 11 | 0.7575 % | 47 % |
| airline | sonnet-5-5 | ARG | high | 72 | 8 | 0.008319 % | 48 % |
| airline | haiku-5-5 | ARG | high | 308 | 41 | 0.008319 % | 55 % |
| WorkBench | haiku-5-5 | ECR | low | 914 | 79 | 0.7575 % | 63 % |
| retail | opus-5-5 | ARG | high | 492 | 32 | 0.008822 % | 70 % |
| retail | sonnet-5-5 | ARG | high | 496 | 33 | 0.008822 % | 71 % |
| banking | haiku-5-5 | MSG | low | 358 | 99 | 1.161 % | 73 % |
| banking | haiku-5-5 | ILL | high | 2 | 2 | 0.04076 % | 77 % |
| banking | opus-5-5 | DUR | medium | 123 | 35 | 0.157 % | 79 % |
| retail | haiku-5-5 | ARG | high | 2511 | 231 | 0.008822 % | 79 % |
| banking | sonnet-5-5 | DUR | medium | 128 | 53 | 0.157 % | 84 % |
| banking | haiku-5-5 | DUR | medium | 314 | 141 | 0.157 % | 85 % |
| banking | opus-5-5 | ARG | high | 80 | 38 | 0.04076 % | 89 % |
| banking | haiku-5-5 | ARG | high | 202 | 108 | 0.04076 % | 90 % |
| banking | sonnet-5-5 | ARG | high | 75 | 42 | 0.04076 % | 91 % |

## Table X3. Confirmed action errors and task success (Exploratory, dated 17 November 2026; `D_erreurs_et_reussite.csv`)

Whole reserve (calibration and confirmation halves), kept episodes, removed tasks excluded. An action error does not always mean a failed task, especially on WorkBench, which scores the final state only.

| environment | model | episodes | successful | with ≥1 confirmed error | of which successful | share successful among those |
|---|---|---|---|---|---|---|
| WorkBench | haiku-5-5 | 2760 | 2648 | 155 | 99 | 63.9 % |
| WorkBench | opus-5-5 | 552 | 542 | 19 | 15 | 78.9 % |
| WorkBench | sonnet-5-5 | 552 | 542 | 22 | 18 | 81.8 % |
| airline | haiku-5-5 | 1950 | 1656 | 77 | 8 | 10.4 % |
| airline | opus-5-5 | 390 | 356 | 18 | 1 | 5.6 % |
| airline | sonnet-5-5 | 388 | 351 | 16 | 2 | 12.5 % |
| banking | haiku-5-5 | 657 | 130 | 280 | 1 | 0.4 % |
| banking | opus-5-5 | 214 | 98 | 59 | 0 | 0.0 % |
| banking | sonnet-5-5 | 210 | 74 | 63 | 1 | 1.6 % |
| retail | haiku-5-5 | 4250 | 3675 | 316 | 45 | 14.2 % |
| retail | opus-5-5 | 850 | 758 | 41 | 0 | 0.0 % |
| retail | sonnet-5-5 | 850 | 763 | 38 | 0 | 0.0 % |

## Table X4. Refused writes among confirmed errors (Exploratory, dated 17 November 2026; `E_refusees_parmi_erreurs.csv`)

104 of 1067 confirmed errors (9.7 %) are writes refused by the tool, which the frozen rule counts as errors without damage.

| environment | model | type | level | confirmed errors | of which refused | share |
|---|---|---|---|---|---|---|
| WorkBench | haiku-5-5 | DUR | medium | 2 | 0 | 0.0 % |
| WorkBench | haiku-5-5 | ECR | low | 79 | 5 | 6.3 % |
| WorkBench | haiku-5-5 | MSG | low | 2 | 0 | 0.0 % |
| WorkBench | opus-5-5 | ECR | low | 10 | 0 | 0.0 % |
| WorkBench | sonnet-5-5 | ECR | low | 11 | 0 | 0.0 % |
| airline | haiku-5-5 | ARG | high | 41 | 7 | 17.1 % |
| airline | haiku-5-5 | DUR | medium | 1 | 0 | 0.0 % |
| airline | opus-5-5 | ARG | high | 6 | 0 | 0.0 % |
| airline | sonnet-5-5 | ARG | high | 8 | 0 | 0.0 % |
| banking | haiku-5-5 | ARG | high | 108 | 2 | 1.9 % |
| banking | haiku-5-5 | DUR | medium | 141 | 41 | 29.1 % |
| banking | haiku-5-5 | ECR | low | 3 | 0 | 0.0 % |
| banking | haiku-5-5 | ILL | high | 2 | 2 | 100.0 % |
| banking | haiku-5-5 | MSG | low | 99 | 2 | 2.0 % |
| banking | opus-5-5 | ARG | high | 38 | 0 | 0.0 % |
| banking | opus-5-5 | DUR | medium | 35 | 3 | 8.6 % |
| banking | opus-5-5 | ECR | low | 12 | 0 | 0.0 % |
| banking | opus-5-5 | MSG | low | 10 | 0 | 0.0 % |
| banking | sonnet-5-5 | ARG | high | 42 | 0 | 0.0 % |
| banking | sonnet-5-5 | DUR | medium | 53 | 14 | 26.4 % |
| banking | sonnet-5-5 | ECR | low | 29 | 0 | 0.0 % |
| banking | sonnet-5-5 | MSG | low | 14 | 0 | 0.0 % |
| retail | haiku-5-5 | ARG | high | 231 | 28 | 12.1 % |
| retail | haiku-5-5 | ECR | low | 20 | 0 | 0.0 % |
| retail | opus-5-5 | ARG | high | 32 | 0 | 0.0 % |
| retail | opus-5-5 | ECR | low | 5 | 0 | 0.0 % |
| retail | sonnet-5-5 | ARG | high | 33 | 0 | 0.0 % |

## Table X5. Errors executed then flagged at tier 2 under B-all, approximation (Exploratory, dated 17 November 2026; `F_erreurs_palier2_approx.csv`)

Whole-reserve error rate × share of writes at tier 2 on the confirmation half, per 100 writes of the type. At tier 2 these errors are executed before being flagged.

| environment | model | type | share at tier 2 | error rate (whole reserve) | errors per 100 writes |
|---|---|---|---|---|---|
| retail | haiku-5-5 | ECR | 34.0 % | 2.41 % | 0.819 |
| retail | sonnet-5-5 | ECR | 19.9 % | 0.00 % | 0.0 |
| retail | opus-5-5 | ECR | 42.6 % | 3.66 % | 1.56 |
| banking | haiku-5-5 | ECR | 69.4 % | 3.23 % | 2.24 |
| banking | sonnet-5-5 | ECR | 27.8 % | 30.00 % | 8.346 |
| banking | opus-5-5 | ECR | 52.8 % | 12.30 % | 6.487 |
| WorkBench | haiku-5-5 | ECR | 63.0 % | 9.88 % | 6.223 |
| WorkBench | sonnet-5-5 | ECR | 81.3 % | 6.25 % | 5.083 |
| WorkBench | opus-5-5 | ECR | 81.2 % | 5.71 % | 4.637 |

## Table X6. Uncertainty on ρ̂ (Exploratory, dated 17 November 2026; `G_intervalle_rho.csv`)

Task-level bootstrap, 2,000 draws, seed 20261117, estimator `classes.rho_anova` pooled over types, not the engine's stratified Fleiss–Cuzick estimator, so the share of draws above 0.885 likely understates the risk. The reconstruction of clusters is approximate (0.800 here against 0.819 in the engine); the engine's value is the one of record. The single type that carries R4 stays judgeable while ρ̂ ≤ 0.885.

| environment | model | tasks | ρ̂ (reconstructed) | 95 % interval | share of draws above 0.885 |
|---|---|---|---|---|---|
| WorkBench | haiku-5-5 | 225 | 0.8 | [0.66 ; 0.924] | 9.6 % |
| WorkBench | opus-5-5 | 209 | 1.0 | [1.0 ; 1.0] | 100.0 % |
| WorkBench | sonnet-5-5 | 209 | 1.0 | [1.0 ; 1.0] | 100.0 % |
| airline | haiku-5-5 | 10 | 0.151 | [0.019 ; 0.321] | 0.0 % |
| airline | opus-5-5 | 10 | 0.231 | [0.007 ; 0.31] | 0.0 % |
| airline | sonnet-5-5 | 9 | 0.384 | [0.0 ; 0.516] | 0.0 % |
| banking | haiku-5-5 | 30 | 0.227 | [0.135 ; 0.303] | 0.0 % |
| banking | opus-5-5 | 29 | 0.294 | [0.19 ; 0.354] | 0.0 % |
| banking | sonnet-5-5 | 30 | 0.279 | [0.135 ; 0.41] | 0.0 % |
| retail | haiku-5-5 | 39 | 0.342 | [0.134 ; 0.463] | 0.0 % |
| retail | opus-5-5 | 37 | 0.407 | [0.028 ; 0.544] | 0.0 % |
| retail | sonnet-5-5 | 38 | 0.443 | [0.021 ; 0.678] | 0.0 % |

## Table X7. Task success and confirmed action errors, both directions (Exploratory, dated 18 November 2026; `exploratoire_2/I_success_and_action_errors.csv`)

Whole reserve, kept episodes, removed tasks excluded. Task-level and action-level scores disagree in both directions.

| environment | model | episodes | with ≥1 confirmed error | of which successful tasks | failed episodes | of which without confirmed error |
|---|---|---|---|---|---|---|
| WorkBench | haiku-5-5 | 2760 | 155 | 63.9 % | 112 | 50.0 % |
| WorkBench | opus-5-5 | 552 | 19 | 78.9 % | 10 | 60.0 % |
| WorkBench | sonnet-5-5 | 552 | 22 | 81.8 % | 10 | 60.0 % |
| airline | haiku-5-5 | 1950 | 77 | 10.4 % | 294 | 76.5 % |
| airline | opus-5-5 | 390 | 18 | 5.6 % | 34 | 50.0 % |
| airline | sonnet-5-5 | 388 | 16 | 12.5 % | 37 | 62.2 % |
| banking | haiku-5-5 | 657 | 280 | 0.4 % | 527 | 47.1 % |
| banking | opus-5-5 | 214 | 59 | 0.0 % | 116 | 49.1 % |
| banking | sonnet-5-5 | 210 | 63 | 1.6 % | 136 | 54.4 % |
| retail | haiku-5-5 | 4250 | 316 | 14.2 % | 575 | 52.9 % |
| retail | opus-5-5 | 850 | 41 | 0.0 % | 92 | 55.4 % |
| retail | sonnet-5-5 | 850 | 38 | 0.0 % | 87 | 56.3 % |

## Table X8. WorkBench plots: inconsistent alert review and sensitivity of the judged type (Exploratory, dated 18 November 2026; `exploratoire_2/M_plots_review.csv`, `M_plots_sensitivity.csv`)

`analytics.create_plot` alerts often differ from the expected action only by the end date (the agent plots up to 30 November, "today", where the benchmark expects 29 November). The reviewing instances decided that case both ways: confirmed, end on 30 Nov: 144; confirmed, other: 11; lifted, end on 30 Nov: 177; lifted, other: 19; 40 of 46 plot tasks had alerts decided both ways. Below, the judged type (WorkBench/Haiku, reversible writes, calibration half; every confirmed plot error read and classified) under consistent decisions; lower bound at ρ = 1 as in Table X2.

| scenario | confirmed errors | writes | rate | lower bound (ρ = 1) | bar | established |
|---|---|---|---|---|---|---|
| engine decisions | 79 | 914 | 8.6 % | 4.14 % | 0.76 % | yes |
| end-date-only cases lifted | 31 | 914 | 3.4 % | 0.86 % | 0.76 % | yes |
| end-date and window-shift cases lifted | 27 | 914 | 2.9 % | 0.66 % | 0.76 % | no |
| no plot error counted | 23 | 914 | 2.5 % | 0.46 % | 0.76 % | no |
