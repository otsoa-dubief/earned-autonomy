# Cost and practical effort of running agent benchmarks at volume with Claude models (November 2026)

All fetches below were made on 2026-11-04 (system date confirmed by `date`: Wed Nov 4 2026). Prices come only from the official Anthropic pages fetched that day. Benchmark token counts and dollar figures come from third-party pages and papers and are flagged as such.

Notation used in formulas:
- p_in, p_out = price per million input / output tokens (USD/MTok)
- T_in, T_out = billed input / output tokens per episode (T_in is cumulative over all turns of the loop, since every turn resends the context)
- N = tasks, k = repetitions, M = model configurations
- Cost per episode = (T_in x p_in + T_out x p_out) / 1,000,000

---

## 1. Official Anthropic prices, caching, batch (fetched 2026-11-04)

### Takeaway
Sonnet 5.5 is $2 in / $10 out per MTok, Opus 5.5 $4 / $20, Haiku 5.5 $0.10 / $0.50 (up to 100k-token prompts), Fable 5.1 $10 / $50. Batch is -50 percent on both input and output. Cache reads cost only 5 percent of input on Sonnet 5.5 / Opus 5.5 (2.5 percent on Fable 5.1, 10 percent on Haiku 5.5). Batch technically accepts multi-turn requests, but an agent loop needs one batch round-trip per step, so it is a poor fit for interactive episodes.

### Cited Findings
- Model price table (per MTok), fetched 2026-11-04 — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing):

| Model | Input | 5m cache write | 1h cache write | Cache read | Output | Batch in / out |
|---|---|---|---|---|---|---|
| Fable 5.1 | $10 | $12.50 | $20 | $0.25 (0.025x) | $50 | $5 / $25 |
| Fable 5 | $10 | $12.50 | $20 | $1 | $50 | $5 / $25 |
| Mythos 5.1 (limited availability, verified orgs only) | $10 | $12.50 | $20 | $0.25 | $50 | $5 / $25 |
| Opus 5.5 | $4 | $5 | $8 | $0.20 (0.05x) | $20 | $2 / $10 |
| Opus 5 / 4.8 / 4.7 / 4.6 / 4.5 | $5 | $6.25 | $10 | $0.50 | $25 | $2.50 / $12.50 |
| Sonnet 5.5 | $2 | $2.50 | $4 | $0.10 (0.05x) | $10 | $1 / $5 |
| Sonnet 5 | $2 | $2.50 | $4 | $0.20 | $10 | $1 / $5 |
| Sonnet 4.6 / 4.5 | $3 | $3.75 | $6 | $0.30 | $15 | $1.50 / $7.50 |
| Haiku 5.5, prompt <= 100k tokens | $0.10 | $0.125 | $0.20 | $0.01 | $0.50 | $0.05 / $0.25 |
| Haiku 5.5, prompt > 100k tokens | $0.50 | $0.625 | $1 | $0.05 | $2.50 | $0.25 / $1.25 |
| Haiku 4.5 | $1 | $1.25 | $2 | $0.10 | $5 | $0.50 / $2.50 |

- The page states Sonnet 5's $2/$10 was introductory pricing but is now standard (the planned rise to $3/$15 on 2026-09-01 will not occur) — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Haiku 5.5 is priced by prompt length: a request whose prompt (including cache reads and writes) exceeds 100,000 tokens pays the higher price, per request. Other 4.6+ models include the 1M context at flat price — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Cache multipliers: 5-minute write 1.25x, 1-hour write 2x, read 0.1x base, except 0.05x on Opus 5.5 and Sonnet 5.5 and 0.025x on Fable 5.1 / Mythos 5.1. These stack with the Batch discount and data residency — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Models 4.7 and later use a newer tokenizer that "produces approximately 30% more tokens for the same text" than Sonnet 4.6 and earlier — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Tool-use adds a hidden system prompt: Opus 5.5 286 tokens (auto/none); bash tool +325 tokens on 4.7 and later — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- US-only inference (`inference_geo`) is a 1.1x multiplier on everything. Fast mode (Opus 5.5 only among current models) is $8 / $40 and is not available with Batch — [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- Batch API: 50 percent off input and output; up to 100,000 requests or 256 MB per batch; "most batches completing within 1 hour", expire after 24 hours; results kept 29 days; supports tool use, system messages, multi-turn conversations, extended thinking; each request is processed independently. The docs recommend the 1-hour cache with batches because they can take more than 5 minutes — [Anthropic batch docs](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
- Batch models supported include fable-5-1, opus-5-5, sonnet-5-5, haiku-5-5 — [Anthropic batch docs](https://platform.claude.com/docs/en/build-with-claude/batch-processing)

### Inferences
- Batch for agent loops: each request is independent and the next step depends on the tool result of the previous one. An episode of S steps therefore needs S sequential batch round-trips, each taking from minutes to up to 24 h. Practical only with a "lock-step waves" runner (all episodes advance one step per batch, with local deterministic tool execution between). Expect wall-clock of S x (up to 1 h typical). The docs do not describe agent loops on Batch; this is my reading of the constraints. For the main experiment, standard API plus caching is simpler; batch is useful for LLM-judge passes and any offline re-scoring of saved trajectories (single-shot requests).
- Caching formula (per model). Let h = share of billed input tokens that are cache reads, U = (1 - h) x T_in unique tokens written once at 1.25x (5m cache). Input cost = p_in x [1.25 x (1-h) + r x h] x T_in / 1e6, with r = 0.05 (Sonnet 5.5, Opus 5.5), 0.1 (Haiku 5.5), 0.025 (Fable 5.1). With h = 0.8: Sonnet 5.5 factor = 0.25 + 0.04 = 0.29, so effective input price = $2 x 0.29 = $0.58/MTok (-71 percent). Opus 5.5: $4 x 0.29 = $1.16. Haiku 5.5: $0.10 x (0.25 + 0.08) = $0.033. Fable 5.1: $10 x (0.25 + 0.02) = $2.70. Output is not reduced, so for output-heavy episodes total savings are smaller (see section 3 worked numbers).
- Using batch AND cache read together: halve the figures again (multipliers stack).

### Gaps
- I did not find a statement that a 5-minute cache stays warm across the sequential steps of one episode on Batch (not applicable anyway if not batching the loop).
- Usage-tier deposit requirements (how fast a new org reaches Build or Scale) were not on the rate-limit page; see section 5.

---

## 2. Published total costs and leaderboards

### Takeaway
HAL spent about $40,000 on 21,730 rollouts (about $1.84 each on average, mixed benchmarks). On HAL tau-bench Airline (50 tasks, 1 run) Claude entries cost $15 to $180 per full run on old models at old prices; HAL warns some costs are inflated by exactly 2x. TheAgentCompany measured $4.1 to $6.3 per task on Claude Sonnets (175 tasks).

### Cited Findings
- HAL: about $40,000 for 21,730 agent rollouts across 9 models and 9 benchmarks; hundreds of VMs in parallel; "from weeks to hours"; logs cover 2.5B tokens of LM calls — [HAL paper abstract, arXiv 2510.11977](https://arxiv.org/abs/2510.11977)
- HAL tau-bench Airline (50 tasks, 1 run per row), cost as reported — [HAL TAU-bench Airline](https://hal.cs.princeton.edu/taubench_airline):
  - Claude 3.7 Sonnet, TAU-bench Tool Calling scaffold: 44 percent, $15.45 (about $0.31 per task)
  - Claude 3.7 Sonnet High: 52 percent, $31.94
  - Claude Opus 4.1: 50 percent, $69.78 (about $1.40 per task); Opus 4.1 High 52 percent, $149.98
  - HAL Generalist Agent + Claude 3.7 Sonnet: 56 percent, $42.11; + Opus 4.1: 54 percent, $180.49
  - Cheap references: Gemini 2.0 Flash High $0.31; DeepSeek V3 $5.43
- Same page caveats: costs "may be overstated", some models inflated by exactly 2x due to double-counted trace spans (affected rows not identified); costs exclude caching benefits; HAL Generalist accuracy is a lower bound; each row has 1 run — [HAL TAU-bench Airline](https://hal.cs.princeton.edu/taubench_airline)
- HAL TAU-bench Retail, Claude 3.7 Sonnet entry: 72.17 percent, $45.89 total (per a search-result summary of the HAL page; I did not open the page) — [HAL TAU-bench Retail](https://hal.cs.princeton.edu/taubench_retail)
- Other HAL Claude costs (top-3 view of the home page, not per-run labelled): CORE-Bench Hard Claude Code Opus 4.5 $87.16; GAIA Sonnet 4.5 $178.20; SWE-bench Verified Mini SWE-Agent Sonnet 4.5 $505.92; Online Mind2Web Sonnet 4 $1,577.26; ScienceAgentBench Sonnet 4.5 High $7.47 — [HAL home](https://hal.cs.princeton.edu/)
- TheAgentCompany (175 tasks, OpenHands), average steps and cost per task: Claude 3.5 Sonnet 29.2 steps / $6.3; Claude 3.7 Sonnet 27.8 / $4.1; Gemini 2.5 Pro 27.2 / $4.2; Gemini 2.0 Flash 39.9 / $0.6; GPT-4o 14.6 / $1.3. Success rates 24.0, 26.3, 30.3, 11.4, 8.6 percent — [TheAgentCompany paper](https://arxiv.org/html/2412.14161)
- tau2-bench paper (secondary quote from search): with gpt-4.1 as agent and as user simulator, per-task cost $0.086 agent and $0.059 simulator; all domains, 1 trial per task, about $40 — [tau2-bench, arXiv 2506.07982](https://arxiv.org/pdf/2506.07982)
- ToolEmu README: running plus evaluating one test case costs about $1.2, about $170 for the whole dataset (GPT-4 era; model version and price not stated in the snippet) — [ToolEmu repository](https://github.com/ryoungj/toolemu)
- Third-party cost calculator (order-of-magnitude, per-token only, Sonnet 4.6 at $3/$15, reasoning on, "actuals can differ by 1.5x or more"), tokens per task: tau-bench Retail 115 tasks 18k in / 6k out ($17); Airline 50 tasks 22k / 7k ($9); AppWorld 750 tasks 28k / 9k ($164); AssistantBench 214 tasks 30k / 7k; GAIA 466 tasks 25k / 8k. Its own FAQ is inconsistent on SWE-bench ($285 in table vs "low thousands") — [benchmarkingagents.com calculator](https://benchmarkingagents.com/agent-eval-cost-calculator)
- AppWorld run totals reported on a third-party comparison: $276.73 (Claude Code), $168.76, $135.74; task count and tokens not stated (search snippet only) — [evomap](https://evomap.ai/es/research/evox-benchmark-claude-code-codex)
- A 2026 paper on efficient agent benchmarking exists (section titles read: "A Theory of Why Rankings Are Easier Than Scores", "Easiest-k vs. Mid-Range Overlap"); body text unreadable in my fetch — [arXiv 2603.23749](https://arxiv.org/pdf/2603.23749)

### Inferences
- Cross-check of the calculator against HAL: calculator Airline 22k in + 7k out at $3/$15 = 22,000 x 3/1e6 + 7,000 x 15/1e6 = 0.066 + 0.105 = $0.171 per task; HAL Claude 3.7 Sonnet reports $0.309 per task ($15.45 / 50). Gap 1.8x, consistent with HAL's 2x double-counting warning or with more turns than the calculator assumes. Use the calculator tokens as a floor and multiply by 1.5 to 2 for safety.
- Old HAL/TAC dollar numbers are at older, higher prices (Sonnet at $3/$15, Opus 4.1 at $15/$75). They must be re-priced with current tokens, not reused as dollars.
- Re-pricing the old token volumes to the new tokenizer: add up to about +30 percent tokens for models 4.7 and later (Anthropic's statement), if the old numbers came from Sonnet 4.6 or earlier tokenizers.

### Gaps
- No published full-run dollar figure for any Claude 5.x model on tau-bench, AgentDojo, AppWorld or TheAgentCompany was found.
- AgentDojo: no cost or runtime figure found in the paper search results or the repository README.
- HAL per-run token counts per row are not shown on the page (aggregate chart only).
- HAL AppWorld page URL I tried returned 404; no verified HAL AppWorld numbers.

---

## 3. Per-environment cost per episode and per run (with formulas)

### Takeaway
At current prices, one tau-bench episode (agent only, no cache) costs about $0.005 (Haiku 5.5), $0.10 to $0.11 (Sonnet 5.5), $0.19 to $0.23 (Opus 5.5), $0.48 to $0.57 (Fable 5.1). A 3-model design (Haiku / Sonnet / Opus) at k = 8 costs about $140 (Airline 50 tasks) to $270 (Retail 115 tasks) before safety margin. TheAgentCompany is about 20 to 40 times more expensive per episode and is the only candidate that can break a $500 to $1,000 monthly spend cap.

### Cited Findings
(sources in sections 1 and 2; the calculations below are mine)

Token inputs used (third-party estimates, section 2): Airline 22k in / 7k out; Retail 18k / 6k; AppWorld 28k / 9k. These are for a single pass at 1 trial.

Per-episode cost without caching, table computed as T_in x p_in/1e6 + T_out x p_out/1e6:

| Environment (T_in / T_out) | Haiku 5.5 | Sonnet 5.5 | Opus 5.5 | Fable 5.1 |
|---|---|---|---|---|
| tau Airline (22k / 7k) | 0.0022 + 0.0035 = $0.0057 | 0.044 + 0.070 = $0.114 | 0.088 + 0.140 = $0.228 | 0.220 + 0.350 = $0.570 |
| tau Retail (18k / 6k) | 0.0018 + 0.0030 = $0.0048 | 0.036 + 0.060 = $0.096 | 0.072 + 0.120 = $0.192 | 0.180 + 0.300 = $0.480 |
| AppWorld (28k / 9k) | 0.0028 + 0.0045 = $0.0073 | 0.056 + 0.090 = $0.146 | 0.112 + 0.180 = $0.292 | 0.280 + 0.450 = $0.730 |

Run formula: C_run = k x N x sum over models m of (T_in x p_in,m + T_out x p_out,m)/1e6 + C_user_sim + C_judge.

Worked designs (agent tokens only, no cache, 3 configs Haiku 5.5 / Sonnet 5.5 / Opus 5.5):
- tau Airline, N = 50, k = 8: episodes per config 400. Sum of per-episode = 0.0057 + 0.114 + 0.228 = 0.3477. Total = 400 x 0.3477 = **$139**. With +30 percent tokens: $181. With Fable 5.1 instead of Opus: (0.0057 + 0.114 + 0.570) = 0.6897 x 400 = $276.
- tau Retail, N = 115, k = 8: 920 episodes per config. Sum = 0.0048 + 0.096 + 0.192 = 0.2928. Total = 920 x 0.2928 = **$269**. With +30 percent: $350.
- Same with k = 4: halve the totals ($70 Airline, $135 Retail).
- AppWorld test-normal (168 tasks, task count per my knowledge of the benchmark; not verified in this session; calculator says 750 tasks across splits), Sonnet 5.5 only, 1 run: 168 x 0.146 = $24.5 (calculator at Sonnet 4.6 prices would give 168 x 0.219 = $36.8). 3 configs, k = 4: 672 x (0.0073 + 0.146 + 0.292 = 0.4453) = **$299**.
- TheAgentCompany (175 tasks): measured $4.1 per task with Claude 3.7 Sonnet at $3/$15. Price ratio Sonnet 5.5 / Sonnet 3.7 = 2/3 on both input and output, so about $2.73 per task if token counts are unchanged. Opus 5.5 = 2x Sonnet 5.5 prices, so about $5.47; Haiku 5.5 = 0.10/2 = 0.05x, so about $0.14. Sum per task over three configs = 2.73 + 5.47 + 0.14 = $8.34. k = 4: 700 x 8.34 = **$5,838**; k = 8: **$11,676**. Add +30 percent tokenizer effect for 4.7+ models: $7.6k at k = 4. A single Sonnet-5.5-only pass over 175 tasks = 175 x 2.73 = $478. Assumes same step counts as the paper's agents (27 to 29 steps); newer models may use more or fewer.
- ToolEmu: $1.2 per case (GPT-4 era) x 144 cases (case count not confirmed by the sources I read) = $173. With Claude, the emulator and evaluator are both LLM calls per step, so cost is a multiple of the agent cost; re-price from tokens, not from the $1.2.

User-simulator cost (tau-bench / tau2-bench):
- Measured ratio with identical models: simulator $0.059 vs agent $0.086, so simulator token cost is about 0.69x the agent's (paper figure, gpt-4.1 both sides). If the simulator is Haiku 5.5 and token volume is about 0.69x the agent's: Airline = 0.69 x 0.0057 = about $0.004 per episode, i.e. 0.69 x 0.0057 x 1200 episodes (50 x 8 x 3 configs) = about $4.7 for the whole design. With Sonnet 5.5 as simulator: 0.69 x 0.114 = $0.079 per episode, about $94 for 1200 episodes.
- The simulator model must be the same across all agent configurations (otherwise the comparison between configs is confounded). It adds variance: the user is itself an LLM at non-zero temperature.

LLM judge cost:
- tau-bench / tau2-bench text: reward is computed against the expected database state and action matching; no LLM judge for text domains. The tau2 README says judges (`tau2 judges`) matter only for voice-v2 submission and "don't change the task reward" — [tau2-bench repo](https://github.com/sierra-research/tau2-bench). (Statement that the text reward is DB-based comes from my background knowledge of the benchmark; not verified in this session beyond the README.)
- TheAgentCompany: 51 of 175 tasks (29 percent) use LLM-based evaluation, typically as fallback after keyword matching, with Claude-3.5-Sonnet-20241022 as evaluator — [TheAgentCompany paper](https://arxiv.org/html/2412.14161). Judge cost not reported separately; for a short grading prompt of say 5k in / 0.5k out on Sonnet 5.5 it would be 5000 x 2/1e6 + 500 x 10/1e6 = $0.015 per judged task (my assumption, tokens not sourced), i.e. negligible vs $2.7 agent cost.
- ToolEmu: LLM emulator plus LLM evaluators (safety and helpfulness) per case; cost bundled into the $1.2 per case — [ToolEmu repository](https://github.com/ryoungj/toolemu).
- AgentDojo: utility and security checks are programmatic functions of the environment state (background knowledge; not verified here), so no judge cost.

### Inferences
- Output tokens dominate: at Sonnet 5.5, 7k output tokens cost $0.070 vs $0.044 for 22k input. Caching, which only cuts input, therefore saves under 30 percent on tau-bench. Worked: Sonnet 5.5 Airline with h = 0.8: input = 22,000 x 0.58/1e6 = $0.01276, plus output $0.070 = $0.0828 vs $0.114 uncached (-27 percent). Opus 5.5: 22,000 x 1.16/1e6 = 0.0255 + 0.140 = $0.1655 vs $0.228 (-27 percent). Haiku 5.5: 22,000 x 0.033/1e6 = 0.0007 + 0.0035 = $0.0042 vs $0.0057.
- Extended thinking tokens are billed as output (the calculator assumes reasoning on); turning thinking off or capping it is the biggest cost lever for Sonnet and Opus.
- Model-change reruns ("a few runs after a model or prompt change"): budget each rerun as one config x N x k x per-episode cost. For Sonnet 5.5, Airline, N = 50, k = 8: 400 x 0.114 = $45.6 per rerun.
- The Start-tier monthly spend cap is $500 and Build $1,000 (section 5); all tau-bench and AppWorld designs above fit within one month on Start or Build, TheAgentCompany with three configs does not.

### Gaps
- No measured turns-per-episode for tau-bench/AppWorld/AgentDojo under Claude 5.x. The only turn data found: TheAgentCompany steps 27 to 29 for Sonnets (OpenHands).
- No measured tokens per AgentDojo episode (no source found). Rough prior from structure only (97 user tasks, 27 injection tasks, 629 security cases per search result summaries of the paper) — do not budget from this without a pilot of 10 episodes.
- AppWorld task counts and per-task token counts: only the 750-task calculator row (28k/9k).

---

## 4. Practical effort: setup, infrastructure, runtime

### Takeaway
tau-bench / tau2-bench and AgentDojo are pure-Python, API-only, no Docker or GPU: the cheapest to set up. TheAgentCompany needs a Docker sandbox plus self-hosted intranet services (heavier ops). Per-episode wall-clock was not reported by any source I could open; run a pilot to measure it.

### Cited Findings
- tau2-bench: Python >= 3.12 and < 3.14, install with `uv`; LiteLLM so any provider works (API keys in `.env`); Docker and GPU not mentioned; 50 tasks each for airline, retail, telecom in text-v1; `--dry-run` prints the plan without calls; a 12-call smoke test via `--domain retail --num-tasks 2`; `--num-trials` exists (example uses 1); `--user-llm` selects the simulator (example gpt-4.1). Voice mode is separate and needs extra system packages — [tau2-bench repo](https://github.com/sierra-research/tau2-bench)
- AgentDojo: `pip install agentdojo`; run with `python -m agentdojo.scripts.benchmark` with `-s` suite, `-ut` user task, `--model`, `--defense`, `--attack`; omitting suite/task runs everything. The README states the API is still under development and may change — [AgentDojo repo](https://github.com/ethz-spylab/agentdojo)
- TheAgentCompany: local workspace is a sandboxed Docker environment; intranet services (self-hosted open-source software) are "reproducible and reset-able"; hardware specs, reset time and per-task runtime not reported — [TheAgentCompany paper](https://arxiv.org/html/2412.14161)
- HAL: parallel VMs ("hundreds") cut evaluation time from weeks to hours — [HAL paper abstract](https://arxiv.org/abs/2510.11977)
- Rate limits, standard tiers, Claude API (fetched 2026-11-04) — [Anthropic rate limits](https://platform.claude.com/docs/en/api/rate-limits):

| Tier | Monthly spend cap | Sonnet 5.5 RPM / ITPM / OTPM | Haiku 5.5 | Opus 5.5 | Fable 5.x (shared 5 and 5.1) |
|---|---|---|---|---|---|
| Start | $500 | 4,000 / 2M / 400k | 4,000 / 2M / 400k | 4,000 / 2M / 400k | 4,000 / 500k / 100k |
| Build | $1,000 | 10,000 / 5M / 1M | same | same | 10,000 / 1.5M / 300k |
| Scale | $200,000 | 13,000 / 10M / 2M | same | same | 13,000 / 4M / 800k |

  Cache-read tokens do not count toward ITPM for these models (only uncached input and cache writes do). New organizations may start in an Evaluation tier with lower limits. Reaching the spend cap returns HTTP 429 with no `retry-after` until the next month (00:00 UTC on the 1st). Batch limits: 1,000 / 2,000 / 4,000 batch-API RPM and 200k / 300k / 500k queued batch requests (Start / Build / Scale).

### Inferences
- Throughput check, tau Airline on Sonnet 5.5, Start tier: ITPM 2,000,000 / 22,000 tokens per episode = about 91 episodes per minute if nothing is cached; OTPM 400,000 / 7,000 = about 57 episodes per minute is the binding limit. 1,200 episodes (50 x 8 x 3) at 57 per minute = about 21 minutes of pure API capacity, so rate limits are not the bottleneck; episode latency (sequential LLM calls) is. Concurrency of 16 to 32 workers is enough.
- Wall-clock per episode: not found. Rough structure: a loop of S sequential model calls plus a simulated-user call per turn; no sourced timing. Measure on 5 pilot episodes per config.
- Infrastructure sizing: tau/AgentDojo run on a laptop (all work is API wait). TheAgentCompany needs a machine able to run Docker with the intranet services (Gitlab, chat, etc. per the paper's description of self-hosted services) per parallel instance; exact RAM not reported, so plan for a pilot.
- Setup effort ranking (my estimate): tau2-bench < AgentDojo < AppWorld (local environment server) < ToolEmu (needs its own LLM emulator and evaluator, hence 3 model roles) < TheAgentCompany (Docker plus self-hosted services).

### Gaps
- Deposit/usage history needed to move from Start to Build/Scale not found on the fetched page.
- Per-episode wall-clock for all candidates; Docker image sizes and RAM for TheAgentCompany; AppWorld server footprint; AgentDojo parallelism options.
- Anthropic-model support in AgentDojo's README: not listed in the page I read (only gpt-4o example); the repository may have additional model entries.

---

## 5. Cheapest valid setup

### Takeaway
Use tau2-bench (text domains Airline plus Retail, 100 to 165 tasks) with Haiku 5.5 as the fixed user simulator, standard API with prompt caching, thinking capped, and run the expensive model (Opus 5.5 or Fable 5.1) on a stratified task subset; reserve TheAgentCompany for a small pilot.

### Cited Findings
- Cost calculator advice for regression testing: a 10 to 25 task subset with a fixed seed, greedy decoding, reasoning off — [benchmarkingagents.com calculator](https://benchmarkingagents.com/agent-eval-cost-calculator)
- tau2-bench exposes `--num-tasks` and `--num-trials`, so subsets and repetitions are native — [tau2-bench repo](https://github.com/sierra-research/tau2-bench)
- Multi-run settings multiply cost by k (pass^k or pass@k), multi-seed by the number of seeds — [benchmarkingagents.com calculator](https://benchmarkingagents.com/agent-eval-cost-calculator)
- HAL notes that higher reasoning effort reduced accuracy in the majority of runs, so lower thinking budgets may cost less without losing accuracy — [HAL paper abstract](https://arxiv.org/abs/2510.11977)

### Inferences
- Levers, largest first:
  1. Thinking tokens: cap or disable (output at $10/MTok on Sonnet 5.5 dominates).
  2. Pick the number of expensive-model episodes by statistical need: for a per-action-type success rate, the variance depends on episodes per action type, not on model count. Spend k on the configuration you actually need to discriminate.
  3. Prompt caching (-27 percent on tau-bench per the worked example; larger on input-heavy TheAgentCompany-like loops).
  4. Cheap fixed user simulator (Haiku 5.5: about $5 for the whole 1,200-episode Airline design vs about $94 with Sonnet 5.5; assumptions in section 3). The simulator's role is to play the customer, so a smaller model is acceptable, but fix it and document it; changing it later breaks comparability.
  5. Batch (-50 percent) only for offline judge/re-scoring passes, not for the interactive loop.
  6. Task subsets: tau2 has 50 frozen tasks per domain, which is already small; subsetting below ~50 hurts the confidence interval more than it saves money.
- Reference budget for the plan in the brief (3 configs Haiku / Sonnet / Opus 5.5, tau Airline + Retail, N = 165, k = 6, Haiku simulator, no cache): per-episode sums Airline 0.3477, Retail 0.2928 => 6 x (50 x 0.3477 + 115 x 0.2928) = 6 x (17.385 + 33.672) = 6 x 51.057 = $306; plus simulator about 0.69 x (Haiku cost) per episode = 0.69 x 6 x (50 x 0.0057 + 115 x 0.0048) x 3 = 0.69 x 6 x 0.837 x 3 = about $10.4 (assuming simulator is called 3 times, once per agent config, with Haiku-priced tokens); total about $317; times 1.5 to 2 safety = $475 to $635. Add three rerun waves on Sonnet only (each 6 x (50 x 0.114 + 115 x 0.096) = 6 x 16.74 = $100): +$300. Everything fits within one Build-tier month ($1,000) but not comfortably within Start ($500).

### Gaps
- No empirical study found on the minimum number of episodes per action type needed for an autonomy-grant rule; this is a statistical-power question for the experiment design, not a cost fact.
- Inspect-evals also has a tau2 port (seen in search results: ukgovernmentbeis.github.io/inspect_evals/evals/tau2); not opened, so its cost/runtime behavior is unverified.
- The Amazon "tau2-bench-verified" fork (github.com/amazon-agi/tau2-bench-verified, seen in search) reports a run with about 27.46M total tokens and $7.38 using gpt-5.1 as simulator; not opened, so I cannot say what it contains.
