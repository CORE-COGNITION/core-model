---
tags:
- paradigm:risky-choice
- cognitive-modeling:needs-review
- psych-101
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:pass
---
# krueger_2024_identifying

- Paper: https://doi.org/10.1037/rev0000456
- Data source: https://github.com/fredcallaway/rational-heuristics-risky-choice/
- PDF: https://osf.io/mg7dn/download
- Full text: https://psyarxiv.com/mg7dn/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Krueger, P. M., Callaway, F., Gul, S., Griffiths, T. L., & Lieder, F. (2024). Identifying resource-rational heuristics for risky choice. Psychological Review, 131(4), 905–951. https://doi.org/10.1037/rev0000456

## Experiment summary
In this mouselab risky-choice study, participants (2,368 in Experiment 1 and 404 in Experiment 2, MTurk adults) sequentially reveal payoff cells of a 4-outcome x 6-gamble payoff matrix by paying a per-click cost, then choose one gamble. Experiment 2 additionally manipulates whether expected values are displayed (EV-display, con vs exp). Both experiments record every trial across instruction blocks (practice) and the test block, with per-trial clicks, click times, reaction time, gambles, payoffs, and choice. The paper derives resource-rational heuristics via machine-learning/meta-RL strategy distillation and tests when people rely on heuristic vs rational strategies, fitting strategy-selection/RL cognitive models to the click-and-choice data.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number (pid) from source participant CSV |
| trial | 0..N-1 sequential trial index within participant, in time order |
| response | Chosen gamble index 0..5 (column of the 4x6 payoff matrix) |
| time_elapsed | Session time in ms (continues across blocks/phases) |
| rt | Reaction time of the gamble choice, ms |
| trial_type | Always "mouselab" |
| click_cost | Total points paid for clicks on this trial (cost x nr clicks) |
| click_times | JSON list of per-click times in ms since trial start |
| probabilities | JSON list: outcome probabilities of the 4 outcomes |
| cost | Per-click cost in points |
| payoff_index | Which outcome occurred 0..3 |
| net_payoff | payoff_value minus click_cost (points) |
| payoff_value | Payoff of the chosen gamble on the occurred outcome |
| problem_id | Unique problem (payoff-matrix) identifier string |
| payoff_matrix | JSON 4x6 matrix: payoff of each outcome (row) x gamble (col) |
| clicks | JSON list of clicked cell indices 0..23 (row-major into matrix) |
| flag | "dominating" when problem had a dominating gamble, else empty |
| block | 0..3 0-indexed phase block (instruct1=0, instruct2=1, instruct3=2, test=3) |
| trial_index | Original per-block trial counter within phase (0-indexed) |
| sigma | Stakes: payoffs are drawn from N(0, sigma^2) |
| alpha | Dispersion: outcome probabilities are drawn from Dirichlet(alpha) |
| mu | Problem-generator mean parameter |
| bonus_rate | Bonus conversion rate (dollars per point) |
| n_comprehension | Number of comprehension-check questions |
| bonus | Bonus actually paid in dollars |
| total_time | Total session duration in ms |
| params | JSON dict of full problem-generator parameters (subset of the above) |
| start_time | UTC ISO timestamp of session start |
| browser | User-agent string of participant's browser |
| version | Experiment/version label (1.0) |
| gender | f / m / other (mapped from source female/male/other) |
| age | Participant age in years |
| education | Self-reported education label (none/primary/secondary/college/grad) |
| wage | Free-text self-reported hourly wage (unstructured) |
| pass_check1 | Whether passed comprehension check 1 (0/1) |
| pass_check2 | Whether passed comprehension check 2 (0/1) |
| pass_instruct1 | Pass score for instruction block 1: a fraction in {0, 1/3, 2/3, 1} (the source does not document the scoring) |
| pass_instruct2 | Pass score for instruction block 2: a fraction in {0, 1/3, 2/3, 1} (the source does not document the scoring) |
| pass_instruct3 | Pass score for instruction block 3: a fraction in {0, 1/3, 2/3, 1} (the source does not document the scoring) |
| instruct_time | Time spent on instruction blocks (s) |
| phase | instruct1 / instruct2 / instruct3 / test phase label |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Original subject number (pid) from source participant CSV |
| trial | 0..N-1 sequential trial index within participant, in time order |
| response | Chosen gamble index 0..5 (column of the 4x6 payoff matrix) |
| rt | Reaction time of the gamble choice, ms |
| trial_type | Always "mouselab" |
| time_elapsed | Session time in ms (continues across blocks/phases) |
| payoff_index | Which outcome occurred 0..3 |
| display_ev | 0/1 whether expected values were displayed (EV-display manipulation) |
| cost | Per-click cost in points |
| click_times | JSON list of per-click times in ms since trial start |
| revealed_points | JSON 4x6 matrix of revealed cell payoffs (0 = cell never clicked) |
| min_trial_secs | Minimum enforced time per trial, seconds |
| payoff_matrix | JSON 4x6 matrix: payoff of each outcome (row) x gamble (col) |
| problem_id | Unique problem (payoff-matrix) identifier string |
| net_payoff | payoff_value minus click_cost (points) |
| clicks | JSON list of clicked cell indices 0..23 (row-major into matrix) |
| probabilities | JSON list: outcome probabilities of the 4 outcomes |
| payoff_value | Payoff of the chosen gamble on the occurred outcome |
| click_cost | Total points paid for clicks on this trial (cost x nr clicks) |
| e_vs | JSON list of expected values of the 6 gambles |
| flag | "dominating" when problem had a dominating gamble, else empty |
| block | 0..3 0-indexed phase block (instruct1=0, instruct2=1, instruct3=2, test=3) |
| trial_index | Original per-block trial counter within phase (0-indexed) |
| sigma | Stakes: payoffs are drawn from N(0, sigma^2) |
| alpha | Dispersion: outcome probabilities are drawn from Dirichlet(alpha) |
| bonus_rate | Bonus conversion rate (dollars per point) |
| shuffle_trials | 0/1 whether trial order was shuffled |
| n_comprehension | Number of comprehension-check questions |
| mu | Problem-generator mean parameter |
| bonus | Bonus actually paid in dollars |
| start_time | UTC ISO timestamp of session start |
| browser | User-agent string of participant's browser |
| total_time | Total session duration in ms |
| params | JSON dict of full problem-generator parameters (subset of the above) |
| version | Experiment/version label (2.3) |
| gender | f / m / other (mapped from source female/male/other) |
| age | Participant age in years |
| education | Self-reported education label (none/primary/secondary/college/grad) |
| wage | Free-text self-reported hourly wage (unstructured) |
| pass_check1 | Whether passed comprehension check 1 (0/1) |
| pass_check2 | Whether passed comprehension check 2 (0/1) |
| pass_instruct1 | Pass score for instruction block 1: a fraction in {0, 1/3, 2/3, 1} (the source does not document the scoring) |
| pass_instruct2 | Whether allowed to proceed past instruction block 2 (0/1) |
| pass_instruct3 | Pass score for instruction block 3: a fraction in {0, 1/3, 2/3, 1} (the source does not document the scoring) |
| instruct_time | Time spent on instruction blocks (s) |
| phase | instruct1 / instruct2 / instruct3 / test phase label |
| condition | con (no EV display) vs exp (EV displayed) participant condition |

`exp0` maps to the paper's Experiment 1; `exp1` to Experiment 2 (which includes the con/exp EV-display manipulation in `condition`/`display_ev`). All instruction blocks (practice) and the test phase are included, tagged by `phase`. The `processed/*.csv` files in the source repo (model-strategy analysis tables) and `click_embeddings` pickle files were not carried into the transform, which uses the base `trials.csv` per participant.

## Text-format conversion

Both experiments (exp0, exp1) were transcribed; neither was skipped. The mouselab risky-choice task is textified by rendering each round as a 4-outcome x 6-gamble table: gambles are labeled A-F (left to right), outcomes 1-4 (top to bottom), outcome chances as percentages, and cell labels are the gamble letter plus outcome number (e.g. A1). Each free response — every cell reveal and the final gamble choice — is marked; revealed values, the drawn outcome, and the payoff/net are narrated as plain text. Experiment 2's experimental group additionally narrates the running expected-value display and the 20-second wait, per `condition`/`display_ev`.

Sample transcript (participant 0, exp0; excerpt ends at the first marked response):

```
You are choosing between gambles to earn points. Your bonus is $0.01 for every 5 points you earn.
On each round, 6 gambles labeled A, B, C, D, E, F (left to right) are on offer. Each gamble pays off in one of 4 possible outcomes, numbered 1 to 4 from top to bottom. Each outcome has a chance of occurring, shown as a percentage. The payoff of each gamble under each outcome is shown in a cell of the table, but all cells start hidden.
To reveal a cell, type its label: the gamble letter followed by the outcome number (e.g. A1 is gamble A under outcome 1). Each reveal costs 4 points. Revealed cells stay visible for the rest of the round, and you may reveal as many or as few as you like, in any order.
When you are ready, choose a gamble by typing its letter: A, B, C, D, E, or F. The outcome is then drawn at random according to the chances, and you earn that gamble's payoff for that outcome minus the 4 points you paid for each reveal.
Instruction block 1 (practice):
Trial 1. Chances: 1:1%, 2:4%, 3:1%, 4:94%.
You choose gamble [HUMAN_RESPONSE]A[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators
Text simulators `simulate0.py` (Experiment 1) and `simulate1.py` (Experiment 2) were added and pass the round-trip check against `build_jsonl.py` (regenerated transcripts byte-match the simulated prompts). Both implement the generative process from the paper (payoffs `N(0, sigma^2)`, outcome probabilities `Dirichlet(alpha)` integerized to 100 balls, per-click cost `lambda`, EV display for the exp group of Experiment 2). Notable `ASSUMPTION:` lines: click counts/orders come from a uniform-random agent draw (0–12 reveals per trial) rather than a learned policy; outcome probabilities are integerized via the largest-remainder method; dominating-gamble (`flag`) trials are not simulated.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Indeterminate: The paper's only formal model is the resource-rational meta-MDP solved with BMPS (Bayesian meta-level policy search), a machine-learning/meta-RL strategy-search method (out of scope: neural-net/meta-RL). The human-data analyses are descriptive/inferential (k-means strategy clustering; logistic/linear mixed-effects regressions of strategy frequencies and click features on environment parameters; a performance decomposition that simulates the BMPS model) — none involve fitting a formal non-neural cognitive model (RL/Bayesian/DDM/prospect-theory) to the responses with per-participant parameter estimation and model comparison. No standalone non-neural modeling result is identifiable.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments got a static jsPsych v8 online port under `experiments/` (shared mouselab reveal-and-choose plugin in `experiments/stimulus/`). The headless `?mode=simulate` round trip passed for both: exp0 writes 31 rows, exp1 writes 29 rows, schema columns and codings match the source (`response` 0..5, `click_cost = cost * len(clicks)`, probs sum to 1, 4x6 matrix, exp1 `display_ev`/`e_vs`/`condition`), and 45 simulated participants per experiment reproduce the simulator's design constants and uniform-agent behaviour. No experiment was skipped. Assumption worth surfacing: the browser mouselab reveals cells by clicking rather than the text simulator's typed cell labels, and `problem_id` is a per-trial random id — neither changes the task or the recorded data.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 4, minor 7; fixed 5, open 6).

Checked: paper (https://doi.org/10.1037/rev0000456; PDF https://osf.io/mg7dn/download), original data (https://github.com/fredcallaway/rational-heuristics-risky-choice/ data/human/1.0 and 2.3), exp0-exp1, transform re-run (byte-identical), transcripts (rebuilt byte-identical; marked tokens verified against clicks and choices), simulators (run and round trip byte-identical), modeling (no model.py by design; section and cognitive-modeling:needs-review tag agree with the paper's BMPS-only modeling), analysis (all 3 effects reproduce), logs. Skipped: none.

Fixed:
- README described click_cost, cost, and net_payoff in "pence"; the task pays in points (paper p. 24: $0.01 per 5 points). Both column tables corrected.
- README described alpha as a "click-cost sensitivity parameter" and sigma as "outcome noise"; alpha is the Dirichlet dispersion of the outcome probabilities and sigma the stakes (SD of payoffs N(0, sigma^2)), paper pp. 23-24. Both tables corrected.
- README described pass_instruct1-3 as 0/1; exp0.csv holds {0, 1/3, 2/3, 1} in all three, exp1.csv in pass_instruct1 and pass_instruct3. Descriptions now give the fractional values.
- README Columns headings used '### expN'; template is '#### expN'.
- logs/auto-exp-sim.sessions.json: the first message's file-diff summary carried a patch of the project's modeling_pending.txt listing other dataset names; that entry was pruned (the session itself is this dataset's run).

Open:
- minor: check_repo reports marked-response counts that differ from the CSV rows (participant 0: 100 marks vs 31 rows). By design: each trial row holds the click sequence in `clicks`, and every click plus the final choice is marked. Verified for all 2,368 (exp0) and 404 (exp1) participants that the marked tokens equal clicks + choices per trial.
- minor: check_repo says the Experiment summary states no N; it states 2,368 and 404 in prose.
- minor: the paper (p. 24) says three practice trials; the source ships three instruction blocks with 3/5/3 (Exp 1) and 3/3/3 (Exp 2) practice trials before the 20 test trials. Source-internal; all kept under `phase`.
- minor: the paper (p. 40) reports 250 males in Experiment 2; the source has 249 m, 154 f, 1 other. Source-internal.
- minor: exp0.csv has one participant with age 600 (source typo); kept as recorded, the paper's mean 37.6 and SD 16.4 reproduce.
- minor: analysis.py regresses on the raw cost value (0-8 points) while the paper's B = -1.9 and -0.073 (pp. 29-30) are per condition-rank step; sign and significance reproduce (-0.77, -0.035), the magnitudes are not on the same scale.

Run: claude-fable-5-1, 2026-09-10
