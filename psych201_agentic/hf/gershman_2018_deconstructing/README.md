---
tags:
- paradigm:bandit
- cognitive-modeling:pass
- text-format:pass
- simulator:pass
- js-experiment:pass
- psych-101
- verification:pass
---
# gershman_2018_deconstructing

- Paper: https://doi.org/10.1016/j.cognition.2017.12.014
- Data source: https://github.com/sjgershm/exploration
- Full text: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5801139/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Gershman, S. J. (2018). Deconstructing the human algorithms for exploration. Cognition, 173, 34-42.

## Experiment summary
Two two-armed bandit experiments on Amazon Mechanical Turk (Exp 1: N = 45; Exp 2: N = 44) in which participants chose between two slot machines for 20 blocks of 10 trials each, with Gaussian reward feedback and each block introducing a fresh bandit (newly drawn arm means). In Exp 1 a stochastic arm (mean ~ N(0,10), variance 10) competed with a fixed 0-point arm; in Exp 2 both arms were stochastic with means ~ N(0,100). Per trial the data record the participant's choice, reward in points, and response time. The paper tests whether human exploration reflects directed exploration (UCB-style uncertainty bonuses, visible as a bias shift in a probit regression) and random exploration (Thompson sampling, visible as a slope shift), using per-block Kalman-filter value/uncertainty estimates; Bayesian model comparison favors a hybrid of UCB and Thompson sampling.

## Notes

### Columns
#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (1..45), as string |
| task_id | 0..19, one per 20-trial block; each block is a fresh bandit with newly drawn arm means (source `block` 1..20, 0-indexed) |
| trial | 0..9, trial number within each (participant_id, task_id); source `trial` 1..10, 0-indexed |
| mu1 | True mean reward of arm 1 for this bandit (stochastic arm; points; the paper states it is drawn ~N(0, variance 10), the shipped values have variance ~1.1, see Notes) |
| mu2 | True mean reward of arm 2 for this bandit (fixed 0 points) |
| choice | Raw arm chosen: 1 = arm 1, 2 = arm 2 (as recorded) |
| response | Response recoded 0-indexed: 0 = arm 1, 1 = arm 2 |
| reward | Points received on the trial (source values, e.g. -5..5) |
| rt | Response time in milliseconds (source RT) |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (1..44), as string |
| task_id | 0..19, one per 20-trial block; each block is a fresh bandit with newly drawn arm means (source `block` 1..20, 0-indexed) |
| trial | 0..9, trial number within each (participant_id, task_id); source `trial` 1..10, 0-indexed |
| mu1 | True mean reward of arm 1 for this bandit (points; the paper states it is drawn ~N(0, variance 100), the shipped values have variance ~66, see Notes) |
| mu2 | True mean reward of arm 2 for this bandit (points; the paper states it is drawn ~N(0, variance 100), the shipped values have variance ~65, see Notes) |
| choice | Raw arm chosen: 1 = arm 1, 2 = arm 2 (as recorded) |
| response | Response recoded 0-indexed: 0 = arm 1, 1 = arm 2 |
| reward | Points received on the trial (source values, e.g. -31..32) |
| rt | Response time in milliseconds (source RT) |

Exp0 maps to the paper's Experiment 1, exp1 to Experiment 2. The source repository's MATLAB scores/simulation files were not transformed; only the two trial-level CSVs (data1.csv, data2.csv) were used. The paper found substantially more random exploration than directed exploration in both experiments.

Source-level discrepancies with the paper (the CSVs are faithful to the source files):
- Sample sizes: the paper's Participants section (3.1) states 44 participants in Experiment 1 and 45 in Experiment 2; the source files (and these CSVs) hold 45 subjects in data1.csv (exp0) and 44 in data2.csv (exp1). The paper's own degrees of freedom (t(44) for Experiment 1, t(43) for Experiment 2) match the source files, so the two numbers in 3.1 appear to be swapped.
- Reward scale: the paper (3.2) states mean-reward variances of 10 (Exp 1) and 100 (Exp 2) and a reward-noise variance of 10; in the source files all `mu1`/`mu2`/`reward` values are integers, the block means have variance ~1.1 (exp0) and ~66/~65 (exp1), and the reward residuals around the chosen arm's mean have variance ~1.1 in both. The source's own model code (`model_comparison.m`) nevertheless uses the paper's variances.
- Trial exclusion: the source's `load_data.m` drops trials with a response time of 20000 ms or more before modeling (10 rows from 7 participants in exp0, none in exp1); the paper does not mention this. The CSVs keep every row; filter on `rt` to replicate the source's analysis.

## Text-format conversion

Both experiments (exp0, exp1) were transcribed to natural language: each transcript recounts the slot-machine instructions verbatim, then walks through all 20 bandit games and 200 trials in order, rendering each free arm choice as a letter (A/B, randomized mapping per participant, stated in the instructions) and the point feedback the participant saw. No experiment was skipped.

Sample transcript (exp0, participant 1):

```
Welcome. In this task you have a choice between two slot machines, represented by colored buttons. When you choose the left (variable) machine, you will win or lose points. The left machine will not always give you the same points, but it will tend to give points around its average value. When you choose the right (fixed) machine, you will always get 0 points. Your goal is to choose the slot machine that will give you the most points. After making your choice, you will receive feedback about the outcome. You will play 20 games, each with a different left (variable) slot machine (the right, fixed machine will always stay the same). Each game will consist of 10 trials. Press A to choose the left (variable) machine and B to choose the right (fixed) machine.
Game 1: a new pair of slot machines appears.
You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Simulators

Both experiments got a text simulator — `simulate0.py` (exp0, paper Exp 1) and `simulate1.py` (exp1, paper Exp 2) — generated by the auto-exp-sim skill. Each one draws 20 games of 10 trials with fresh arm means per game, assigns per-participant A/B response tokens, and round-trips byte-identical through `build_jsonl.py` (modulo the randomized token mapping). None were skipped. ASSUMPTION worth surfacing: the shipped `mu`/`reward` values contradict the paper's stated variances (the paper says variance 10/100 for means and 10 for reward noise; the data measure ~unit-variance rounded Gaussians for the noise, and mean-variances ~1.13 for exp0 and ~66 for exp1), so each simulator uses the data-derived generative parameters declared in its class docstring.

Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Online experiment

Both experiments got a runnable static jsPsych v8 experiment under `experiments/exp0/` and
`experiments/exp1/` (auto-exp-js). The headless round trip (jsPsych simulation mode in Chromium) passed for
both: the produced CSV matches the `expN.csv` schema exactly (same columns and codings, 20 task_ids × 10
trials per participant, `choice = response + 1`, `rt` filled from the browser, no outbound data request).
The letter-to-arm mapping is fixed A-left / B-right (the simulators randomize it to counterbalance
response-key bias; here response is coded by position, so the data schema is unchanged). Cosmetic
presentation defaults not fixed by the source — machine colors, the between-game Continue step, 1200 ms
feedback, 600 ms inter-trial gap — are documented in `experiments/README.md`. The experiment ships no
data-collection backend; `saveData` in `index.html` offers a CSV download by default and is the seam for
wiring a collection endpoint. No experiment was skipped.

## Modeling reproduction

Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: probit regressions (UCB, Thompson, hybrid, value-directed) on Kalman-filter regressors V/RU/V-TU; random-effects model selection on per-participant BIC evidence (protected exceedance probability).
Reproduced: hybrid_wins_exp0, hybrid_wins_exp1, directed_and_random_choice.
Not reproduced: none.
Numeric mismatch: reported vs reproduced — the protected exceedance probability magnitudes and the hybrid coefficient t-statistics differ in magnitude from the paper's Figure 4 / Section 4.1 (e.g. Exp1 V/TU t=14.2 vs reported 5.02), but the direction and significance (hybrid favored; RU and V/TU positive and significant) match. The model comparison used the paper's own per-participant BIC evidences and a Python port of the VBA groupBMC random-effects procedure (Rigoux et al. 2014 / Stephan et al. 2009).
Partial validation: none.
Indeterminate: none.

## Verification
Verdict: pass (critical 0, major 1, minor 7; fixed 8, open 0).
Checked: paper (https://doi.org/10.1016/j.cognition.2017.12.014, PMC5801139 full text), original data (https://github.com/sjgershm/exploration, data1.csv and data2.csv), exp0-exp1, transform re-run (both CSVs byte-identical; every source row and column kept), transcripts (build_jsonl.py regenerates both files byte-for-byte), simulators (simulate0.py and simulate1.py run and round-trip through build_jsonl.py), analysis (all 4 effects reproduce), logs. Skipped: none.
Fixed:
- major: logs/auto-exp-transcribe.sessions.json and transcripts/auto-exp-transcribe.log were a stub export of a 2026-08-24 re-run that exited with "already processed", not the transcription run; both removed.
- minor: exp0 instructions in build_jsonl.py and simulate0.py paraphrased the paper (section 3.2: "you will win or lose points. The left machine will not always give you the same points, ..."); made verbatim, transcripts0.jsonl regenerated (only the instruction line changed), README sample transcript updated.
- minor: README title was "# Gershman_2018_deconstructing"; lowercased.
- minor: "## Text-format conversion" and "## Simulators" had no "Run:" line; added.
- minor: the paper (3.1) states 44 participants in Experiment 1 and 45 in Experiment 2; the source and the CSVs hold 45 (exp0) and 44 (exp1), matching the paper's own t(44)/t(43); noted under Notes.
- minor: the paper (3.2) states mean-reward variances 10/100 and reward-noise variance 10; the source values are integers with block-mean variance ~1.1 (exp0) and ~66 (exp1) and residual variance ~1.1; the README column table said "drawn ~N(0,10)"; column descriptions corrected and the source-level discrepancy noted.
- minor: the source's load_data.m drops trials with rt >= 20000 ms (10 rows, 7 participants in exp0), which the paper does not state; the CSVs keep them; noted under Notes.
Open:
- none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-09-09
