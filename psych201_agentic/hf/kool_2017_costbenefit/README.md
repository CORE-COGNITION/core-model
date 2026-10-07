---
tags:
- paradigm:two-step-task
- cognitive-modeling:pass
- psych-101
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:pass
---
# kool_2017_costbenefit

- Paper: https://doi.org/10.1177/0956797617708288
- Data source: https://osf.io/6z5rs/ (mirror URL stated in the paper: https://osf.io/yg82m/)
- PDF: https://web.archive.org/web/2019id_/http://pdfs.semanticscholar.org/0f3f/caa694f61599829b4f2db1d85a4bc6e15578.pdf
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Kool, W., Gershman, S. J., & Cushman, F. A. (2017). Cost-benefit arbitration between multiple reinforcement-learning systems. Psychological Science, 28(9), 1321–1333. https://doi.org/10.1177/0956797617708288

## Experiment summary
Two Amazon Mechanical Turk experiments (Experiment 1: N=102 subjects in the file, 98 analyzed; Experiment 2: N=100) ask how people decide moment-to-moment whether to use model-based (planning) vs model-free (habitual) control. Participants performed a two-step reinforcement-learning task: each trial opens with a choice between two first-stage spaceships (binary keypress choice, 0/1 coding with RTs), which leads via common/rare transitions to one of two second-stage states offering scalar point rewards; a per-trial "stakes" cue multiplies all points by 1 or 5 on ~50% of trials, creating a cost-benefit incentive to deploy more model-based control under high stakes. Experiment 1 has a single genuine first-stage decision per trial (one row per trial in exp0.csv); Experiment 2 uses the Daw (2011) variant with two responses per trial, split into per-stage rows again grouped by `block`. Both experiments used 25 practice + 200 test trials per subject. The paper tests an arbitration account of metacontrol, finding that behavior is more model-based on high-stakes than low-stakes trials in Experiment 1 but not Experiment 2, and fits dual-system RL models (standard vs exhaustive variants) to the choice data.

## Notes

### Columns

Both experiments are the stakes ("cost-benefit") variants of the Kool et al. (2016) two-step RL task. `exp0.csv` = paper Experiment 1 (single first-stage choice per trial); `exp1.csv` = paper Experiment 2 (two choices per paper-trial, stage-1 then stage-2, split into two rows grouped by `block`).

**Divergence from `Hugging-Brain/kool_2016_when`:** the source here is CSV, not .mat, and `subinfo` has only `age`/`gender`. I additionally carry the per-subject fitted dual-system model parameters from each `groupdata.csv` (minus its redundant `id`; its `score` renamed `score_final` to avoid colliding with the per-trial running `score`). Experiment/phase structure differs (25 practice + 200 test trials here). All kool_2016_when behavioral columns are preserved under the same names.

Common codings:
- `participant_id`: subject label from the source `ID` column (e.g. `Sub1`; one Experiment-1 subject arrived with a raw MTurk worker ID instead of a `SubN` label and has been relabeled `Sub102`). Subjects run but excluded from paper analysis (the paper keeps 98/101) are still present.
- `phase`: `practice` (25 trials, no response deadline) or `test` (200 trials, 1500 ms deadline), derived from the raw `practice` flag.
- `response`: 0-indexed, `0` = chose the left-hand stimulus (`stim_left`/`stim_1_left`), `1` = chose the right-hand stimulus (`stim_right`/`stim_2_right`); NaN where the participant timed out (raw `choice == -1`) and, on exp1 stage-2 rows, where no stage-2 key was pressed (raw `responsekey2 == -1`).
- `stake`: per-trial point multiplier cue, `1` (low) or `5` (high), ~50% each.
- `-1` in raw columns (`rt1`, `rt2`, `choice1`, `choice2`, `state2`, `responsekey*`) is the source's "no response" sentinel; it is written as an empty cell (NaN) in every such column (`rt`, `rt1`, `rt2`, `choice1`, `choice2`, `state2`, `responsekey1`, `responsekey2`).
- Model-fit parameters (`beta`, `learning_rate`, `lambda`, `w_low`/`w_high`, stickiness terms, `*_exhaustive`, `behavioral_mbcomponent_*`, `rewardrate*`, `score_final`, `nr_missed_trials`) are per-subject constants from `groupdata.csv`, repeated on every row of that participant. `beta` = softmax inverse temperature, `learning_rate` = alpha, `lambda` = eligibility-trace parameter, `w_low`/`w_high` = model-based arbitration weight on low/high stakes, `behavioral_mbcomponent_*` = behavioral model-based index per stakes level, `nr_missed_trials` = count of timed-out trials.

#### exp0 (Experiment 1)
One row per source trial; a single genuine first-stage decision (second-stage "space bar" press is a passive acknowledgment, not a separate response).

| column | description |
|--------|-------------|
| participant_id | Subject ID from source `ID` column, `Sub1`..`Sub102`; `Sub102` was relabeled from a raw MTurk worker ID in the source and is absent from `subinfo.csv`/`groupdata.csv`, so its age/gender/model-fit columns are empty. |
| trial | 0..224 within each participant, 0-indexed across practice+test in source order. |
| block | 0..224, same as one-row-per-trial paper-trial index. |
| phase | `practice` (25) or `test` (200). |
| response | 0 = chose `stim_left`, 1 = chose `stim_right`; NaN on timed-out trials (468). |
| rt | Choice reaction time in ms (`rt1`), empty on timed-out trials. |
| valid | 1 if a first-stage choice was made (raw `choice1 > 0`), else 0. |
| state | First-stage state, `state1 - 1` (0/1). |
| reward | Delivered second-stage reward = raw `points` (treasure pieces, 0..9; base value NOT yet multiplied by `stake`). |
| state1 | Raw first-stage state (1/2). |
| state2 | Raw second-stage state encountered (1/2, empty on timed-out trials). |
| stim_left, stim_right | IDs of the two spaceships shown left/right (each 1..4). |
| choice1 | Raw chosen-spaceship ID (1..4, empty if timed out). |
| rt1, rt2 | Stage-1 choice RT and stage-2 spacebar-press RT in ms (empty = none). |
| responsekey1 | jsPsych key code of the stage-1 press (70='F', 74='J', empty if none). |
| points | Raw scalar reward delivered (0..9). |
| rews_s1, rews_s2 | Current scalar reward values of the two second-stage states (drifting random walk, 0..9). |
| stake | Point-multiplier cue (1 or 5). |
| score | Running cumulative point total after this trial. |
| practice | Raw binary practice flag (1=practice). |
| trial_nr | Raw trial counter, 0..24 practice / 0..199 test. |
| time_elapsed | Cumulative ms since experiment start. |
| age | Participant age in years (from `subinfo.csv`). |
| gender | `f`/`m` (from `subinfo.csv`). |
| beta | Softmax inverse temperature of the standard dual-system model fit (per-subject MAP estimate from `groupdata.csv`; empty for subjects the authors did not fit). |
| learning_rate | Learning rate (alpha) of the standard model fit. |
| lambda | Eligibility-trace decay of the standard model fit. |
| w_low | Model-based arbitration weight on low-stakes (x1) trials in the standard model fit (0 = model-free, 1 = model-based). |
| w_high | Model-based arbitration weight on high-stakes (x5) trials in the standard model fit. |
| response_stickiness | Perseveration weight on the previous response key (left/right) in the standard model fit. |
| stimulus_stickiness | Perseveration weight on the previously chosen stimulus in the standard model fit. |
| beta_low_exhaustive, beta_high_exhaustive | Inverse temperature on low-/high-stakes trials in the exhaustive model fit, in which every parameter varies with the stakes. |
| learning_rate_low_exhaustive, learning_rate_high_exhaustive | Learning rate per stakes level, exhaustive model fit. |
| lambda_low_exhaustive, lambda_high_exhaustive | Eligibility-trace decay per stakes level, exhaustive model fit. |
| w_low_exhaustive, w_high_exhaustive | Model-based arbitration weight per stakes level, exhaustive model fit. |
| stimulus_stickiness_low_exhaustive, stimulus_stickiness_high_exhaustive | Stimulus stickiness per stakes level, exhaustive model fit. |
| response_stickiness_low_exhaustive, response_stickiness_high_exhaustive | Response stickiness per stakes level, exhaustive model fit. |
| behavioral_mbcomponent_low, behavioral_mbcomponent_high | Behavioral model-based choice component on low-/high-stakes test trials: P(revisit the previous second-stage state) after a positive minus after a non-positive model-derived second-stage prediction error on the previous trial (`groupanalysis.m`; missed and post-missed trials excluded). |
| rewardrate | Mean `points` per test trial. |
| avg_rewarddistribution | Mean of the two drifting planet reward values (`rews_s1`, `rews_s2`) over the test trials, i.e. the chance level. |
| rewardrate_corrected | `rewardrate` minus `avg_rewarddistribution`. |
| score_final | Running score after the last test trial (source `groupdata.csv` column `score`). |
| nr_missed_trials | Number of test trials with a first-stage or space-bar timeout (raw `rt1 == -1` or `rt2 == -1`); subjects with 40 or more are absent from `groupdata.csv`. |

#### exp1 (Experiment 2)
Two rows per paper-trial (stage-1 and stage-2 rows), grouped by `block`; `trial` numbers responses 0..449. This is the Daw (2011) two-step task with one first-stage state, binary (win/lose) rewards, and continuously drifting win probabilities.

| column | description |
|--------|-------------|
| participant_id | Original subject ID (`Sub1`..`Sub100`). |
| trial | 0..449 within each participant; numbers each stage-response row. |
| block | 0..224 within each participant; one value per paper-trial (both stage rows share it). |
| stage | `stage1` (first-stage choice) or `stage2` (second-stage choice) row of the block. |
| phase | `practice` (25) or `test` (200). |
| response | 0 = chose the left stimulus, 1 = right; NaN where no response was made: stage-1 on the 294 timed-out trials, stage-2 on the 823 trials with no stage-2 keypress (raw `responsekey2 == -1`). |
| rt | Choice RT in ms for this stage (`rt1` on stage-1 rows, `rt2` on stage-2 rows); empty when -1. |
| valid | 1 if a choice was actually made on this stage-row (stage-1: `choice1 > 0`; stage-2: `responsekey2 != -1`), else 0. |
| state | Current state: 0 for the single stage-1 state; `state2 - 1` (0/1) on stage-2 rows. |
| reward | Delivered reward: NaN on stage-1 rows; raw `win` (0/1) on stage-2 rows with a stage-2 keypress; NaN on the 823 no-keypress stage-2 rows (the running `score` never increments on those trials, so no reward was delivered — the raw `win` column keeps the source's stale value there). |
| stim_left, stim_right | IDs of the two options shown left/right for THIS stage (1/2). |
| stim_1_left, stim_1_right, stim_2_left, stim_2_right | Raw stage-1 and stage-2 option IDs (trial-level, repeated on both rows). |
| choice1, choice2 | Raw chosen-option IDs (1/2; `choice1` empty on the 294 timed-out stage-1 trials; `choice2` is never missing in the source, but on the 823 no-keypress trials (`responsekey2 == -1`) it holds a stale carried-over value — 99% equal to the previous trial's `choice2` — not a real choice). |
| rt1, rt2 | Stage-1 and stage-2 response RTs in ms (empty = none). |
| responsekey1, responsekey2 | jsPsych key codes (70='F', 74='J', empty if none). |
| win | Raw binary reward outcome (0/1); on the 823 no-keypress stage-2 trials it is a stale undelivered value (running `score` never increments there). |
| state2 | Raw second-stage state (1/2, empty on the 294 timed-out stage-1 trials). |
| stake | Point-multiplier cue (1 or 5). |
| score | Running cumulative point total after this trial. |
| practice | Raw binary practice flag. |
| trial_number | Raw trial counter, 0..24 practice / 0..199 test. |
| p_win_state1_action1, p_win_state1_action2 | Drifting P(win) for each stage-1 action. |
| p_win_state2_action2, p_win_state2_action2_1 | Drifting P(win) for stage-2 outcomes (source column `p_win_state2_action2.1`; dot renamed to `_1`). |
| time_elapsed | Cumulative ms since experiment start. |
| age, gender | Participant demographics from `subinfo.csv`. |
| beta | Softmax inverse temperature of the standard dual-system model fit (per-subject MAP estimate from `groupdata.csv`). |
| learning_rate | Learning rate (alpha) of the standard model fit. |
| lambda | Eligibility-trace decay of the standard model fit. |
| w_low | Model-based arbitration weight on low-stakes (x1) trials in the standard model fit (0 = model-free, 1 = model-based). |
| w_high | Model-based arbitration weight on high-stakes (x5) trials in the standard model fit. |
| response_stickiness | Perseveration weight on the previous response key (left/right) in the standard model fit. |
| stimulus_stickiness | Perseveration weight on the previously chosen stimulus in the standard model fit. |
| beta_low_exhaustive, beta_high_exhaustive | Inverse temperature on low-/high-stakes trials in the exhaustive model fit, in which every parameter varies with the stakes. |
| learning_rate_low_exhaustive, learning_rate_high_exhaustive | Learning rate per stakes level, exhaustive model fit. |
| lambda_low_exhaustive, lambda_high_exhaustive | Eligibility-trace decay per stakes level, exhaustive model fit. |
| w_low_exhaustive, w_high_exhaustive | Model-based arbitration weight per stakes level, exhaustive model fit. |
| stimulus_stickiness_low_exhaustive, stimulus_stickiness_high_exhaustive | Stimulus stickiness per stakes level, exhaustive model fit. |
| response_stickiness_low_exhaustive, response_stickiness_high_exhaustive | Response stickiness per stakes level, exhaustive model fit. |
| behavioral_mbcomponent_low, behavioral_mbcomponent_high | Behavioral model-based choice component on low-/high-stakes test trials: the reward x transition interaction on first-stage stay probability, mean of P(stay \| rewarded, common) and P(stay \| unrewarded, rare) minus mean of P(stay \| rewarded, rare) and P(stay \| unrewarded, common) (`groupanalysis.m`; missed and post-missed trials excluded). |
| rewardrate | Proportion of test trials with a win. |
| avg_probabilitydistribution | Mean of the four drifting win probabilities (`p_win_*`) over the test trials, i.e. the chance level; replaces Experiment-1's `avg_rewarddistribution`. |
| rewardrate_corrected | `rewardrate` minus `avg_probabilitydistribution`. |
| score_final | Running score after the last test trial (source `groupdata.csv` column `score`). |
| nr_missed_trials | Number of test trials with a stage-1 timeout or no stage-2 keypress (raw `rt1 == -1` or `rt2 == -1`). |

## Text-format conversion

Both experiments (exp0 = Experiment 1, exp1 = Experiment 2) were transcribed as natural language; they are two-step reinforcement-learning tasks that are fully textifiable (choosing between named spaceships/aliens by F/J keys, learning the reward and transition structure from narrated outcomes). None skipped. Response tokens are the actual keys `F` (left) and `J` (right); spaceship/alien/planet identities are given by their stimulus IDs since the on-screen color/label assignment is not recorded in the CSV.

Sample transcript (exp0, first response):

```
You are flying a spaceship between planets to collect space treasure. At the start of every round a cue shows the stakes for that round: all points earned are multiplied by 1 (low stakes) or by 5 (high stakes). You begin in one of two starting points; each shows a different pair of spaceships side by side. One spaceship of each pair always flies to one of the two planets, and the other always flies to the other planet. Press F to choose the left spaceship and J to choose the right. You then fly to that planet, where an alien works in a space mine; press the space bar within the time limit to collect the treasure it pays out. The alien is sometimes in a good part of the mine (paying many pieces, up to 9) and sometimes in a bad spot (fewer pieces); these amounts drift slowly over the session. Your points this round are the pieces of treasure times the round's stake multiplier, added to your running score in the top-right corner.
Stakes x1. Two spaceships appear: Ship 4 on the left and Ship 3 on the right. You press [HUMAN_RESPONSE]F[/HUMAN_RESPONSE] ...
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

Both experiments got a text simulator (`simulate0.py`, `simulate1.py`); the round-trip check through `build_jsonl.py` reproduces each simulated participant's transcript byte-for-byte. Key assumptions (full list in each class docstring as `ASSUMPTION:` lines): practice-phase trials are always low-stakes (x1); the test-only response timeouts use the per-trial rates observed in the data (exp0: 468 first-stage + 580 space-bar → reward 0; exp1: 294 stage-1 + 823 stage-2); the running `score` resets at the practice→test boundary; exp1's win probabilities and exp0's drifting scalar rewards follow the paper's Gaussian random walks (σ=0.025 in [0.25,0.75]; σ=2 reflected at 0 and 9). No experiment skipped.

Fixed 2026-09-15: simulate0-1.py asked the agent before narrating the trial; the decision-time prompt is now the transcript text up to the open marker (check_calls.py passes).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Update (2026-08-13)
- PII scrub (exp0): one participant whose source data carried a raw MTurk worker ID instead of a `SubN` label was renamed to the next unused number, `Sub102` (225 rows; participant count unchanged at 102). This participant is absent from `subinfo.csv`/`groupdata.csv`, so its demographic and model-fit columns remain empty.
- Phantom stage-2 responses (exp1): 823 stage-2 rows had no stage-2 keypress (raw `responsekey2 == -1`, `rt2` missing) yet carried a populated `response`/`reward` and `valid=1`. Inspection shows these are genuine no-response trials: raw `choice2` there is a stale carried-over value (99% identical to the previous trial's `choice2`), the running `score` never increments on those trials although `win*stake` would predict an increment on 391 of them (on all 21,495 keypress stage-2 trials the score increments by exactly `win*stake`), and the authors' own `nr_missed_trials` equals stage-1-timeout + stage-2-no-keypress trial counts for all 100 subjects. Fixed: `response` -> empty (823 cells), `reward` -> empty (823 cells; the reward was not delivered), `valid` -> 0 (823 cells). `rt` was already empty on those rows. Raw `choice2`/`win` are retained unchanged; `responsekey2` keeps its key codes (its `-1` sentinel is now an empty cell, see Verification).
- exp0 checked for the same pattern: absent (all 468 `responsekey1 == -1` trials already have `response`/`rt` empty and `valid=0`).

CSVs fixed in place from the previous release; transform.py updated to produce the same output
from raw. The previous version remains in the repo's git history.

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result (the dual-system
RL model of Kool, Gershman & Cushman, 2017).
Fitted models: dual-system RL arbitration model (model-free TD with eligibility traces +
model-based planning, softmax choice, stakes-dependent weight w_low/w_high, beta/lr/lambda/
response+stimulus stickiness), MAP with the paper's empirical priors (beta ~ Gamma(4.82,
0.88); stickiness ~ Normal(0.15, 1.42)), per-participant bounded L-BFGS in JAX; model
implementation validated to ~1e-12 log-likelihood against the paper's own MATLAB
`MB_MF_rllik.m` (OSF 6z5rs). Checks: paired t-tests on per-participant w_low vs w_high and
a two-sample t-test of the stakes delta between experiments, exactly as the paper reports.
Reproduced: exp1_stakes_increase_model_based_control (w_high > w_low in Experiment 1),
exp2_no_stakes_effect_on_control (no stakes difference in Experiment 2),
stakes_delta_greater_in_experiment_1 (stakes-induced increase in model-based control
larger in Experiment 1 than Experiment 2).
Not reproduced: none.
Numeric mismatch: means of the same direction and close to the paper — Experiment 1
w_high 0.76 vs 0.76 reported, w_low 0.58 vs 0.54; stakes delta (w_high - w_low) 0.19 vs
0.22 reported (paired t p < .001); Experiment 2 delta -0.03 vs -0.02 reported (n.s.);
between-experiment delta difference 0.23 vs 0.24 (p < .001). As in the paper, most w
estimates sit at their [0,1] bounds, so per-participant recovery is boundary-dominated
(paper's own note 2 on w/beta non-identifiability); group-level claims reproduce.
Partial validation: none.
Indeterminate: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments got a runnable static jsPsych v8 online experiment
(`experiments/exp0/` for Experiment 1, `experiments/exp1/` for Experiment 2). The
headless round trip passed for both: a random-agent simulation produced a CSV
matching the task-producible columns, codings and row counts of `exp0.csv` /
`exp1.csv` (225 rows for exp0, 450 two-stage rows for exp1), and every screen
rendered without breakage; no network requests are made.

The saved CSV carries the task-producible columns only. Per-subject columns from
the repo's external tables are not produced by the task and are deliberately
omitted: `age` / `gender` (from `subinfo.csv`) and the fitted dual-system model
parameters `beta` … `nr_missed_trials` (from `groupdata.csv`).

Assumptions surfaced: generative design follows the simulators (`simulate0.py` /
`simulate1.py`), which initialise the drifting reward/probability values once and
keep test stakes at ~50% from trial 0 — the original OSF task resets them at the
practice→test boundary and keeps the first 5 test trials low-stakes; the running
`score` is reset at that boundary (as the sim docstrings and the CSVs record).
Timings follow the OSF task code (500 ms feedback, 500 ms ITI, 1500 ms response
deadline in the test phase, none in practice); the stimuli are redrawn as
CSS shapes (spaceship/alien cards, planet text) rather than the original PNGs,
which is cosmetic and does not change the task or the recorded data.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 4, minor 4; fixed 5, open 3).

Checked: paper (https://doi.org/10.1177/0956797617708288, PDF via web.archive.org), original data (OSF 6z5rs, data/experiment 1|2: data.csv, subinfo.csv, groupdata.csv, groupanalysis.m, make_raw_data.m, standard/exhaustive set_params.m), exp0-exp1, transform re-run, transcripts, simulators, modeling, analysis, logs. Skipped: none.

Fixed:
- transform.py wrote the source's -1 'no response' sentinel into choice1, choice2, state2, responsekey1 and responsekey2 (exp0: 468 timed-out trials; exp1: 294 stage-1 timeouts, 823 no-keypress stage-2 rows); the schema wants empty cells. SENTINEL_COLS added to finalize(), exp0.csv/exp1.csv regenerated (the transform re-run on the OSF source was byte-identical before and after), build_jsonl.py now keeps the raw responsekey1/responsekey2 columns out of the per-participant metadata (Sub50 in exp1 always pressed F, so the column became constant and the transcript key sets diverged); the rebuilt transcripts0.jsonl/transcripts1.jsonl are byte-identical to the uploaded ones, simulate0.py/simulate1.py emit an empty state2 on timeouts; README column notes updated.
- README Columns tables listed the 26 per-subject groupdata.csv columns (beta .. nr_missed_trials) as one shorthand row in exp0 and exp1; one row per column written from groupanalysis.m / set_params.m (model parameters, exhaustive-model variants, behavioral model-based component, reward rate and its chance correction, final score, missed-trial count).
- README Columns headings used '### exp0' / '### exp1'; changed to '####'.
- logs/auto-exp-modeling.sessions.json: the export's summary.diffs metadata carried four diff entries (815 KB) from another run's scratch directory (the vantiel_2022_meaning README, CSVs and paper); removed.
- logs/auto-exp-sim.sessions.json: the same metadata carried a diff of the project's modeling_pending.txt naming ~70 other datasets; removed.

Open:
- minor: check_repo still reports 'kool_2016_when' in the modeling, sim and transcribe session logs. It is this README's own 'Divergence from Hugging-Brain/kool_2016_when' note, read by every run; each log holds a single root session named for this dataset. Not contamination; the README cross-reference is correct and kept.
- minor: the paper (p. 1323, 1329) states a 1,500 ms response deadline in the test phase, but the OSF data.csv holds 45 (exp0) and 4 (exp1) test trials with rt1 > 1500 ms (max 5,478 / 2,034 ms) and 62 / 21 with rt2 > 1500 ms. Inside the source; the CSVs are faithful to it.
- minor: the paper (p. 1322) reports 101 participants in Experiment 1; the OSF data.csv holds 102 IDs, one a raw MTurk worker ID absent from subinfo.csv and groupdata.csv (relabeled Sub102, documented in the README). Inside the source; kept.

Run: claude-fable-5-1, 2026-09-09
