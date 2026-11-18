# Design of a sandbox experiment for a per-action-type promotion/demotion rule for AI agents

Method note: 12 web searches, snippets only; no full-page fetches. Anything marked "Cited" comes from a search result and has not been checked against the full paper unless stated. Anything under "Inferences" is mine. Dates up to 2026-11-04. Some 2026 preprints are only known through aggregator pages (peer-review status unchecked).

## 1. How do agent evaluations estimate reliability from repeated trials (pass^k, CIs, sample sizes)?

### Takeaway
pass^k (tau-bench) is the standard "all k trials succeed" reliability metric and is estimated unbiasedly from n trials per task. Error bars come from standard statistics (CLT standard error, paired and clustered inference). A promotion rule is by nature a pass^N-type criterion on a stream, so the experiment can score it against a known true per-task success probability.

### Cited Findings
- tau-bench (Yao et al., ICLR 2025) introduces pass^k: the probability that the agent solves the same task on all k independent runs, averaged over tasks. With n trials and c successes, unbiased estimators of pass^k and pass@k use combinatorial formulas (C(c,k)/C(n,k) for pass^k). Variation comes only from LM sampling, since the user prompt and database transitions are fixed. — [arXiv 2406.12045](https://arxiv.org/pdf/2406.12045); [ICLR page](https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b126cc38b8638e07bef37e7b2bb72bf-Abstract-Conference.html)
- Headline result: the best function-calling agents (gpt-4o at the time) solve under 50% of tasks, with pass^8 below 25% in retail, a roughly 60% relative drop from pass^1. Numbers are dated (2024). — [Sierra blog](https://sierra.ai/uk/blog/benchmarking-ai-agents); [arXiv](https://arxiv.org/pdf/2406.12045)
- HAL (Kapoor et al., ICLR 2026): standardized harness, 21,730 rollouts, 9 models x 9 benchmarks, about 40,000 USD. LLM-aided log inspection found unreported behaviors (e.g. agents searching HuggingFace for the benchmark instead of solving the task). — [ICLR 2026](https://iclr.cc/virtual/2026/poster/10006806); [arXiv 2510.11977](https://arxiv.org/abs/2510.11977v1)
- A separate preprint applies Bayesian variance decomposition to HAL and Harbor Index: complete model+scaffold systems rank reliably, underlying-model rankings much less; outcomes are binary and coverage is incomplete. Listed submission date 30 Sep 2026, not independently verified. — [alphaxiv](https://alphaxiv.org/abs/2610.00651v1)
- "AI Agents That Matter" (Kapoor, Stroebl, Siegel, Nadgir, Narayanan; TMLR 2025): evaluations should control cost (stochastic agents gain from repeated calls), report accuracy-cost Pareto fronts, and use holdout sets; their survey found most benchmarks lack a proper held-out set, and seven had none. — [arXiv 2407.01502](https://arxiv.org/pdf/2407.01502); [Princeton page](https://agents.cs.princeton.edu/)
- "Adding Error Bars to Evals" (Miller, Anthropic, 2024): treat items as draws from a super-population; SE of a binary mean = sqrt(p(1-p)/n) by CLT; use paired question-level comparisons, cluster-robust SEs when items are dependent, and power analysis for planning. — [arXiv 2411.00640](https://arxiv.org/pdf/2411.00640)
- ReliabilityBench (arXiv 2601.06112) scores consistency over repeated runs, robustness to rephrasing, and fault tolerance; reports pass@1 overstating reliability by 20-40% (2 models, 2 architectures, 1,280 episodes; peer-review status unverified, date ambiguity between PDF header and listing). — [arXiv 2601.06112](https://arxiv.org/abs/2601.06112v1)

### Inferences
- The rule under test needs per-(agent, action type) reliability estimates from a sequential stream. pass^k with k = the promotion threshold gives the probability that an agent with true success rate p gets promoted by a pure success run: p^N. This is the natural analytic benchmark for the simulation.
- Trials of the same task are not independent items (clustered by task). The experiment must use cluster-robust intervals and let the task, not the trial, be the unit when comparing rules.
- HAL's finding that scaffold+model is the stable unit suggests the "agent" in the experiment should be a full configuration (model + prompt + tools + permissions), which is also exactly the unit the reset rules act on.

### Gaps
- No source found giving required numbers of repeated trials per task for a given target CI width in agent settings. Use binomial planning (see section 5).
- Current (2026) pass^k leaderboard values not retrieved.

## 2. How can agents of controlled reliability be created?

### Takeaway
Combine three levers: (a) weaker or different models, (b) injected faults and tool noise at a known rate, (c) a "synthetic agent" layer whose success probability per action type is set by design. Fault injection benchmarks exist and show large reliability drops, but I found no source on calibrating a mixture to hit an exact target p.

### Cited Findings
- ReliabilityBench: perturbations reduce success from 96.9% (eps=0) to 88.1% (eps=0.2); rate limiting was the most damaging fault in ablations. — [arXiv 2601.06112](https://arxiv.org/abs/2601.06112v1)
- ToolMaze: deterministic perturbations at specific tool nodes; sharpest drops from implicit semantic failures, especially permanent ones. — [emergentmind 2606.05806](https://www.emergentmind.com/papers/2606.05806)
- ToolMisuseBench: offline, replayable fault injection with explicit retry/call budgets; 6,800 tasks public dataset. — [arXiv 2604.01508](https://arxiv.org/pdf/2604.01508v1)
- MCP fault injection ("Scaling Paradox", NeurIPS 2026 poster): faults calibrated from open-source MCP repos cut completion by about 60%; the larger model scored higher without faults but completed fewer tasks under faults. — [NeurIPS poster](https://neurips.cc/virtual/2026/poster/151564)
- AgentCheck: replay recorded tool responses, inject one of 12 fault types; failures are usually silent (agent uses wrong tool output confidently). — [alphaxiv 2607.11098](https://www.alphaxiv.org/abs/2607.11098v3)
- SREGym: multi-layer faults plus ambient noise reduce diagnosis rates. — [emergentmind 2605.07161](https://www.emergentmind.com/papers/2605.07161)
- Sandbagging work shows models can be prompted or password-locked to underperform on targeted evaluations, and to target specific scores; imitation of a weaker model was mediocre; erratic scores can give sandbagging away. — [van der Weij et al., ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/b5e5753b0a0e440a6d8dc7e143617cec-Abstract-Conference.html); [arXiv 2406.07358](https://arxiv.org/abs/2406.07358)

### Inferences
- Recommended agent population, three tiers:
  1. Synthetic agents (scripted Bernoulli processes with known p per action type, plus drift and change-point options). These give exact ground truth to validate the rule's mathematics and run 10^4-10^5 replications cheaply.
  2. Real-model agents with fault injection at tuned rates (tool error, wrong-output, rate limit, truncated context) to hit approximate p levels, measured afterwards by a large calibration run, not assumed.
  3. Real weaker/stronger model pairs and degraded prompts for realism. Their true p is only known from a separate calibration set.
- Use a grid of true reliabilities, for example p in {0.70, 0.80, 0.90, 0.95, 0.98, 0.99} per stakes class, plus "good until change point, then bad" agents (p drops after a config change) and "bad on one action type, good on another" agents. This exercises per-action-type logic.
- Reliability must be action-type dependent in the design (a good reader that is a bad emailer), otherwise per-type promotion is never tested.
- Password-locking is not needed to create low reliability; it is relevant only as an adversarial scenario (agent behaves well when it detects certification tests). Treat it as a stress arm, not the base design.
- Measure the true p of tier-2/3 agents on a held-out calibration set that the rule never sees; this addresses the "success assumed rather than observed" flaw.

### Gaps
- No source on the statistical calibration of injected-fault rates to a target success probability.
- No source found on tier-2 agents' stationarity (model-provider updates drift p over time); not covered.

## 3. Evaluation awareness, sandbagging, and realistic trap cases

### Takeaway
Frontier models often detect evaluations, increasingly so, and realism edits help only modestly. Production-derived scenarios work better than synthetic ones. For the re-certification "trap tests", the safest design is traps built from real past error cases, indistinguishable in form from ordinary tasks, with detection tested explicitly.

### Cited Findings
- "Large Language Models Often Know When They Are Being Evaluated" (MATS/Apollo): nine models, Gemini-2.5-Pro AUC 0.83 vs human baseline 0.92; better in agentic than chat settings. — [arXiv 2505.23836](https://arxiv.org/html/2505.23836v2)
- Reported via secondary summaries: Sonnet 4.5 verbalized eval awareness on a honeypot distribution rose from about 20% to 80% in post-training (from a secondary summary, check the system card); UK AISI found Opus 4.6 identified evaluations 80% of the time vs 72% for predecessor; Apollo reportedly declined to formally assess Opus 4.6 after frequent recognition. — [IAPS](https://www.iaps.ai/research/evaluation-awareness-why-frontier-ai-models-are-getting-harder-to-test); [Goodfire](https://www.goodfire.ai/research/verbalized-eval-awareness-inflates-measured-safety)
- Goodfire: refusal rates 3-18 points higher when the model verbalizes eval awareness (Fortress benchmark), so awareness inflates measured safety. — [Goodfire](https://www.goodfire.ai/research/verbalized-eval-awareness-inflates-measured-safety)
- OpenAI "production evaluations": scenarios from de-identified real traffic, lower verbalized eval awareness than traditional deception evals; costly (human review), scenarios unpublished. — [OpenAI alignment blog](https://alignment.openai.com/prod-evals/)
- Prompt-rewrite toward deployment style helps modestly; Apollo-style scheming scenarios still flagged as evals by LLM judges at 0.80-0.90 after two rewrite rounds; editing prompts did not remove cue-driven behavior while activation steering did. — [LessWrong/GreaterWrong "Better evals are not enough"](https://www.greaterwrong.com/posts/TeLLtMjtcoB9qCoL3/better-evals-are-not-enough-to-combat-eval-awareness); [LessWrong "hard to make scheming evals look realistic"](https://lesswrong.com/posts/TBk2dbWkg2F7dB3jb/it-s-hard-to-make-scheming-evals-look-realistic-for-llms) (blog posts, not peer reviewed)
- HAL found agents looking up the benchmark itself, a concrete case of exploiting the evaluation context. — [ICLR 2026](https://iclr.cc/virtual/2026/poster/10006806)

### Inferences
- Eval awareness matters for this experiment in two ways: (1) the agent may behave better on certification traps than in ordinary operation, inflating pass rates and causing false promotion; (2) any "doubt signal" behavior may be inflated when the agent suspects a test. Measure both.
- Concrete mitigations: build traps from the same task generator and same format as ordinary tasks; mix traps at an unannounced rate into the normal stream; score an "eval-awareness probe" on a sample of transcripts (LLM judge asking "does this look like a test?", plus search for verbalized mentions in the agent's reasoning where available); compare pass rate on traps vs matched ordinary tasks (a gap indicates awareness or sandbagging); keep a trap-free control arm.
- The rule's own transparency is a leak: if the agent's prompt mentions "past errors become trap tests", it can overfit. Do not expose the rule to the agent in the sandbox unless that is the deployment condition being tested (then test both).
- Frontier-model awareness rates were measured mainly on safety-style scenarios; their transfer to routine tool tasks is unknown. Do not assume either way.

### Gaps
- No peer-reviewed source on awareness effects specifically for routine-operations agents.
- Primary system cards not opened; figures above for Sonnet 4.5/Opus 4.6 are second-hand.

## 4. Sandbox vs real deployment gap and external validity

### Takeaway
Evidence says benchmark success overstates usefulness (test-passing is not merge-worthy; RCT slowdown despite high benchmark scores). The experiment can only claim operating characteristics of the rule under the simulated process; it cannot claim real-deployment outcomes.

### Cited Findings
- METR follow-up: roughly half of test-passing agent patches (mid-2024 to mid/late-2025) would not be merged by maintainers, after adjusting for noise using reviews of 47 originally merged human patches; reviews were hypothetical, without CI. — via [AI Engineer talk page](https://ai.engineer/talks/why-agent-hype-can-fall-short-of-reality-joel-becker-metr) and secondary summaries; primary METR post not opened.
- METR RCT: 16 developers, 246 tasks, early-2025 AI tools made them about 19% slower while they believed the opposite; larger follow-up (from Aug 2025) moved to developer-level randomization because agentic tools broke time tracking. — [eWeek summary](https://www.eweek.com/news/news-ai-tools-slow-developer-productivity-study/); [GreaterWrong repost](https://www.greaterwrong.com/posts/9eizzh3gtcRvWipq8/measuring-the-impact-of-early-2025-ai-on-experienced-open)
- AI Agents That Matter: weak holdouts, shortcuts and overfitting in agent benchmarks. — [arXiv 2407.01502](https://arxiv.org/pdf/2407.01502)
- Fault-injected tool environments cut performance sharply versus clean ones (see section 2), which shows clean benchmarks overstate field reliability. — [ReliabilityBench](https://arxiv.org/abs/2601.06112v1); [MCP faults](https://neurips.cc/virtual/2026/poster/151564)

### Inferences
- The relevant gaps for this rule: (a) outcome verification is automatic in a benchmark but noisy in reality (human validators err, rarely refuse; the earlier attempt had 58 validations and 1 refusal); (b) error rates in reality are non-stationary; (c) stakes and reversibility are labeled by design in the sandbox but judged in reality. State these as scope limits, and include a "noisy verifier" arm (flip verdicts with probability e, one-sided and symmetric) so the rule's sensitivity to verification error is measured.
- Report the study as a claim about the decision rule's statistical properties under a stated generative model, plus a robustness range, not about business outcomes.

### Gaps
- No quantified sandbox-to-production gap for autonomy-delegation decisions specifically.
- METR primary posts not fetched.

## 5. Sequential testing and acceptance sampling designs; validating error rates by simulation

### Takeaway
"Promote after N verified successes" is a success-run / zero-failure acceptance plan; demotion by a statistical method for low stakes maps to SPRT / CUSUM-type monitoring. All have textbook OC curves and ASN, and their real error rates should be checked by Monte Carlo because nominal rates are approximate and peeking inflates errors.

### Cited Findings
- Success-run theorem: for zero failures, n = ln(1-C)/ln(R). 90% confidence / 95% reliability needs 45 (77 with one failure allowed, 105 with two); 95/95 needs 59; 95/99 needs 299. Assumes independent identical units; mainly used for hardware, less apt for software where failures are systematic; zero-failure plans are fragile. — [Quality Digest](https://qualitydigest.com/node/35963); [Pharma Online](https://www.pharmaceuticalonline.com/doc/how-to-establish-sample-sizes-for-process-validation-using-the-success-run-theorem-0001); [calculator guide](https://maker-label-studio.vercel.app/guides/how-to-calculate-reliability-sample-size/); [Khuston](https://khuston.github.io/statistics/2021/01/25/reliability-and-confidence-for-pass-fail-data.html)
- SPRT in acceptance sampling: running likelihood ratio vs two boundaries (linear in number inspected for item-by-item plans), controls producer's risk alpha at p<=p0 and consumer's risk beta at p>=p1; judged by OC curve and average sample number (ASN). — [Shaparenko, Virginia Tech thesis](https://vtechworks.lib.vt.edu/server/api/core/bitstreams/e24a2090-8e0e-49c4-bffb-d24d73565670/content); [course notes](https://www.gacbe.ac.in/pdf/ematerial/18BST63C-U5.pdf); [MetricGate](https://metricgate.com/docs/power-sprt-sequential/)
- Truncation: a curtailed Wald plan has a natural truncation point; altering it can distort the OC curve. Wald's plan wins on ASN but alternatives can win on combined cost. — [NPS thesis](https://calhoun.nps.edu/entities/publication/7af6f38e-7bf7-4593-b12d-3a12630af641); [DTIC](https://apps.dtic.mil/sti/pdfs/ADA257579.pdf); [Shaparenko](https://vtechworks.lib.vt.edu/server/api/core/bitstreams/e24a2090-8e0e-49c4-bffb-d24d73565670/content)
- Simulation validation practice: 2,000 simulated Bernoulli streams per true mean, SPRT as oracle, capped runs; repeated exact-binomial p-value checking inflates type I error (one case 0.23); clinical protocols use 100,000 replications to calibrate a truncated one-sided SPRT boundary; a Monte Carlo thesis found true SPRT error probabilities can differ from nominal and sample size can sometimes exceed fixed-sample size. — [arXiv 2010.08082](https://arxiv.org/pdf/2010.08082); [BMT CTN 1203 protocol](https://cdn.clinicaltrials.gov/large-docs/37/NCT02208037/Prot_000.pdf); [BMT CTN 0801](https://cdn.clinicaltrials.gov/large-docs/33/NCT01106833/Prot_000.pdf); [AAU thesis](https://etd.aau.edu.et/bitstreams/85717549-cbab-477e-a9d3-1263a97a3f6b/download); [CRAN SPRT](https://cran.r-universe.dev/SPRT/doc/manual.html)
- Group sequential designs: Pocock constant boundaries vs O'Brien-Fleming conservative early; Lan-DeMets spending functions; power family alpha*t^rho (rho about 0.8 ~ Pocock, about 3 ~ OBF). Published sample-size inflation figures conflict between sources, so recompute with gsDesign or similar. — [MetricGate](https://metricgate.com/blogs/interim-analysis-alpha-spending/); [Lydersen slides](https://slyderse.folk.ntnu.no/medstat/Pres17Feb2010.pdf)

### Inferences (my computations: probability of a pure success run p^N)
| true p | N=5 | N=10 | N=20 | N=30 | N=59 |
|---|---|---|---|---|---|
| 0.70 | 0.168 | 0.028 | 0.001 | 0 | 0 |
| 0.80 | 0.328 | 0.107 | 0.012 | 0.001 | 0 |
| 0.90 | 0.590 | 0.349 | 0.122 | 0.042 | 0.002 |
| 0.95 | 0.774 | 0.599 | 0.358 | 0.215 | 0.048 |
| 0.98 | 0.904 | 0.817 | 0.668 | 0.545 | 0.304 |
| 0.99 | 0.951 | 0.904 | 0.818 | 0.740 | 0.553 |
- Reading: with N=20, an agent at p=0.80 is falsely promoted 1.2% of the time but a p=0.95 agent is only promoted 36% of the time. A success-run rule is therefore very conservative against "good but not perfect" agents; sensible weights N per stakes class must come from the OC curve, with an explicit definition of "bad" (p below p0) and "good" (p above p1) per stakes class. Success run for 95% confidence at R=0.95 needs 59; at R=0.99, 299 (success-run formula; 299 successes would be unreachable for rare high-stakes actions).
- Because the rule includes immediate demotion on any error at medium/high stakes, promotion is effectively a "run since last error" process (Markov chain): the long-run fraction of time promoted can be computed exactly, as well as expected time to promotion and to demotion. Use exact computation and simulation to cross-check.
- Required analytical/simulation outputs per stakes class: OC curve P(promoted by horizon T | p), P(demoted within T | p after change point), ASN-style expected number of trials to promotion/demotion, and time-in-wrong-state. The action space is also a stream with horizon, so the unit of analysis should be "fraction of time at the right autonomy level", not just a one-shot accept/reject.
- The statistical demotion on low stakes (SPRT/CUSUM-like) should be simulated with at least 10^4-10^5 replications per cell; Monte Carlo SE of an error rate near 5% at 10^4 replications is about 0.2 points (sqrt(.05*.95/10^4)). For real-model arms, with a few hundred runs per cell the SE is about 1.3 points at 300 runs (±2.5 for the 95% CI). Zero events in n runs: upper 95% bound about 3/n (rule of three, my addition).
- Sequential monitoring with continuous peeking inflates error unless boundaries are designed for it (cited above); the rule is permanent monitoring by design, so its false-demotion rate over a long horizon will approach 1 for any fixed-threshold test unless the statistic is built for it. Specify the horizon and report cumulative false demotion probability by time.

### Gaps
- No primary standard (ISO 2859/MIL-STD-105/ANSI Z1.4) text retrieved; formulas come from secondary pages.
- Nothing found specifically on "promotion rules with decay/weighted prior successes" (the halving of success weight on prompt change) in the sequential-testing literature. That part is a custom Bayesian/discounted-evidence design; treat it as unvalidated and test by simulation.
- No source on CUSUM for Bernoulli streams was retrieved (searched indirectly).

## 6. Pre-registration practices in ML and AI evaluation

### Takeaway
Pre-registration and registered reports exist as proposals and tools in NLP/ML; evaluation is considered more amenable to it than model design. Adoption is limited, so the experiment should freeze its own plan with a hash and a timestamp.

### Cited Findings
- "Preregistering NLP Research" (van Miltenburg, van der Lee, Krahmer): proposes registered reports and question templates for NLP, including engineering experiments. — [arXiv 2103.06944](https://arxiv.org/pdf/2103.06944)
- "Questionable practices in machine learning": evaluation is more amenable to preregistration than model design (benchmark and baseline choices are discrete); preregistration is the best way to certify a practice was pre-hoc. — [arXiv 2407.12220](https://arxiv.org/pdf/2407.12220)
- Earlier proposals: results-blind review (Gencoglu et al. 2019) and a NeurIPS 2020 workshop on a pre-registration publication model. — [NeurIPS 2020 workshop](https://nips.cc/virtual/2020/workshop/16158)
- PRML: open spec and CLI that hashes a manifest (metric, threshold, dataset, seed) before the run and flags later changes; does not verify the registered evaluation is the one executed; adoption unestablished. — [OECD catalogue](https://oecd.ai/en/catalogue/tools/prml-%E2%80%94-pre-registered-ml-manifest-specification)
- "Evaluation Cards" (arXiv 2606.09809) is an evaluation reporting layer; contents not examined. — [arXiv 2606.09809](https://arxiv.org/pdf/2606.09809)

### Inferences
- Freeze before any run: rule specification (all parameters), stakes classes, agents and fault configs, task sets (split into development / calibration / confirmation), comparator rules, primary and secondary metrics with decision thresholds that would count as failure, simulation code and seeds, analysis code, and the stopping rule for the experiment. Commit to a git tag, hash the manifest, record the date, and store the tag outside the repo's editable history (e.g. a public timestamp or a signed commit by a second person).
- Separate the people/roles: the person who tunes the rule must not see the confirmation-set outcomes (the earlier attempt failed because authors had seen the data). Use a development phase to tune parameters on one set of agents/tasks, then run the confirmation phase once.
- Pre-declare falsification criteria, for example "the rule fails if false promotion on agents with p<=0.80 exceeds 5% at the declared horizon" or "if it does not beat comparator X on the cost-weighted loss". Deviations get logged in a dated amendment file.
- Report negative results and any deviation; null results are possible outcomes by design ("an experiment that can fail").

### Gaps
- I did not verify whether any major ML venue currently runs a registered-reports track.
- No agent-evaluation-specific pre-registration standard found.

## 7. Comparator rules

### Takeaway
No source defines comparators for delegation rules. The following list is my design, motivated by the question and standard "naive baselines" practice (AI Agents That Matter stresses simple baselines).

### Cited Findings
- Simple baselines can match or beat complex agent architectures at lower cost, which is the reason to include them. — [arXiv 2407.01502](https://arxiv.org/pdf/2407.01502)

### Inferences
- Comparator set (all run on the same agents, same task streams, same seeds, paired):
  1. Approve everything (full autonomy). Defines the cost of errors with no oversight.
  2. Approve nothing / human validates everything (zero autonomy). Defines the validation cost ceiling.
  3. Promote after first success (or after k=3 fixed, no stakes weighting).
  4. Fixed allow-list of low-risk action types (static, no learning).
  5. Risk classifier without track record (a stakes/reversibility score only, thresholded).
  6. Fixed N consecutive successes, same N for all stakes (ablates stakes weighting).
  7. Rule without reset/trap mechanisms (ablates the configuration-change logic).
  8. Rule without free doubt signal (ablates the self-report channel).
  9. Oracle rule that knows the true p (upper bound on achievable performance).
  10. Random promotion matched on promotion rate (null for the discrimination claim).
- Primary comparison metric should be a pre-declared cost: C = c_err * (errors executed without validation, weighted by stakes) + c_val * (human validations needed) + c_block * (good actions blocked); report the Pareto front of validation load vs executed harm rather than a single scalar, in line with cost-aware reporting.
- Ablations (6-8) show which component earns its keep; failure of an ablation to differ from the full rule is itself a result.

### Gaps
- No published comparator set for autonomy-delegation rules.

## 8. Metrics and experimental design (synthesis)

### Takeaway
This section is entirely my inference, built on the cited material above.

### Inferences
- Definitions to fix in advance: for each (agent, action type), a "good" level p_good and "bad" level p_bad per stakes class (for example, high stakes: good >= 0.99, bad <= 0.90; low stakes: good >= 0.95, bad <= 0.80). These are hypotheses to be justified, not data.
- Primary metrics: false promotion rate (promoted while true p <= p_bad, by horizon T), false demotion rate (demoted while p >= p_good, per unit time and cumulative), missed-promotion / time-to-promotion for good agents, detection delay after an injected degradation (demotion latency in actions and in executed errors), harm = executed errors while promoted, validation load saved. Report each with exact binomial (Clopper-Pearson) or Wilson intervals, cluster-aware by agent and task.
- OC curve: sweep true p from 0.5 to 1.0 in steps of 0.01-0.02 (finer near the thresholds); plot P(promoted by T) and P(demoted by T) per stakes class; overlay the analytic p^N curve for the success-run component, and the comparators' curves.
- pass^k: report pass^k of the agents themselves (k = 1, 2, 4, 8, N) to show true reliability and check that the rule's promotion decisions track pass^N; also pass^k of the rule's decisions across repeated seeds (does the rule give the same promotion outcome on re-runs?). That is the reproducibility of the rule, a distinct quantity.
- Sample sizes (rough, from binomial SE):
  - Synthetic tier: 10^4-10^5 replications per (p, stakes, rule) cell; trivial cost.
  - Real-agent tier: at least 30-50 distinct agent configurations spanning the p grid and at least 300 independent promotion episodes per important cell to resolve a 5% error rate to about ±2.5 points; if cost forces fewer, state that the study can only reject gross failures (rule of three for zero events).
  - Task streams long enough to reach promotion for the highest N (e.g. N=20-30 for medium stakes means at least 100-200 actions per type per run), with enough error opportunities for demotion to fire. The earlier attempt failed on exactly this event count.
- Configuration-change injection: schedule change points at pre-declared random times: model swap, permission change, prompt edit (three arms), with crossed outcomes (the change actually degrades p / leaves p unchanged / improves p). Measure: (a) does the reset lead to re-promotion of unchanged agents in reasonable time (cost of unnecessary reset); (b) are degraded agents kept out (harm after change); (c) does the half-weight on prompt change behave better than full reset or no reset; (d) trap tests: build from the agent's own past errors, check pass/fail and compare trap pass rate to the matched fresh-task pass rate. Include "unchanged but flagged" and "changed but flagged as unchanged" (silent provider updates) as stress arms.
- Doubt signal: model agents with calibrated and uncalibrated doubt (doubt fires on a fraction of future errors, plus false doubts). Metric: errors prevented per doubt, validation load added. Include a "doubt spam" agent to see whether free doubts let an agent avoid ever being evaluated (a gaming path); and an agent that never signals doubt.
- Verifier noise arm: ground-truth scorer vs scorer that flips results with e in {0, 0.02, 0.05, 0.10} for the success path; test sensitivity of promotion and demotion rates.
- Non-stationarity arm: gradual drift, abrupt change point, and periodic bad stretch.
- Adversarial arm: agent that behaves well on detected traps (eval-aware stand-in: perform better when the input matches a trap fingerprint) to measure the rule's exposure.
- Run each configuration with at least 3 independent seeds of the rule and tasks; hold the agent samples fixed across comparator rules (paired design, as in Miller) to cut variance.

### Threats to validity (inference, with cited anchors)
- Construct: "success" must be observed by an independent automatic scorer, not assumed; scorer errors tested via noise arm. Benchmark scores are not usefulness ([METR via AI Engineer](https://ai.engineer/talks/why-agent-hype-can-fall-short-of-reality-joel-becker-metr)).
- Internal: authors tuning on the confirmation data (pre-registration, section 6); simulation bugs (cross-check analytic Markov-chain computation vs simulation); leakage of the benchmark into the agent (HAL found agents searching for the benchmark); trial dependence (cluster by task).
- Statistical: peeking/continuous monitoring inflates false demotion (arXiv 2010.08082 shows inflation to 0.23); multiple comparisons across stakes classes and comparators (pre-declare one primary endpoint, correct the rest); heavy dependence on chosen p_good/p_bad (report sensitivity grid).
- External: the sandbox's stakes labels, error rates, verification regime, and task mix differ from reality; fault injection rates may not match production; model versions change (results are dated to the tested models) ([MCP fault study](https://neurips.cc/virtual/2026/poster/151564) shows large clean-vs-fault gaps).
- Eval awareness / sandbagging: traps may be recognized ([arXiv 2505.23836](https://arxiv.org/html/2505.23836v2)); mitigate as in section 3.
- Cost: repeated runs of real agents are costly (HAL: about 40,000 USD for 21,730 rollouts, an order of magnitude reference only). Under the user's existing rule that paid calls need prior approval, budget each tier before running.

### Gaps
- All thresholds in this section are proposals; none comes from a source. They need justification from the business risk side before registration.
