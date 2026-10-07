---
tags:
- paradigm:image-learning
- cognitive-modeling:pass
- psych-101
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---
# flesch_2018_comparing

- Paper: https://doi.org/10.1073/pnas.1800755115
- Data source: https://github.com/summerfieldlab/Flesch_etal_2018
- PDF: https://europepmc.org/articles/PMC6217400?pdf=render
- Full text: https://europepmc.org/articles/PMC6217400
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Flesch, T., Balaguer, J., Dekker, R., Nili, H., & Summerfield, C. (2018). Comparing continual task learning in minds and machines. Proceedings of the National Academy of Sciences, 115(44), E10313–E10322. https://doi.org/10.1073/pnas.1800755115

## Experiment summary
Participants categorized naturalistic tree images (parametrized continuously along branchiness × leafiness) into two orthogonal classification rules learned by trial and error with point-reward feedback. Four human experiments are included: Experiment 1a (cardinal reward axis, n=176) and 1b (diagonal, n=166) compared blocked (200-, 20-, or 2-trial runs) vs randomly interleaved training followed by an interleaved no-feedback test; Experiment 2a (cardinal, n=138) and 2b (diagonal, n=103) added pre- and post-training dissimilarity-placement rating sessions around the same main task (B200 and interleaved groups only). Responses are binary accept/reject categorization choices with reaction times. The research question asks whether blocked training promotes factorized (task-segregated) representations that protect learned knowledge against interference, evaluated via choice matrices, representational similarity analysis, and Bayesian comparison of 1- vs 2-boundary psychophysical choice models — contrasted against deep CNNs that suffer catastrophic forgetting (simulation experiments, excluded here).

## Notes
Data are original, public (CC BY-NC-SA), human, and trial-level. The `response` column is `resp_category` (1 = accept/plant, 0 = reject) on main-task rows and a JSON `[x_final, y_final]` placement on rating rows (Exp2a/b). `condition` (b200/b20/b2/interleaved) is derived from training-context run-lengths; it agrees with the source group code for every participant (`subcode_0` = 3 marks the interleaved group, `subcode_4` the blocked groups' block length). Reaction time is carried raw (`resp_reactiontime`) because the source mixes units and contains implausible/negative values. Exp3/Exp4 of the paper are CNN/β-VAE simulations and are excluded; only the human `allData_*.mat` and `data_dissim/*.mat` files are included. `transform.py` requires scipy to read the MATLAB `.mat` sources.

### Columns

# Columns

All four experiments share the main gardening-task (600 trials: 400 training, 200 test) from MATLAB struct `allData_*.mat`. `response` is the binary accept/reject categorization (`resp_category`: 1 = accept/plant, 0 = reject; NaN = missed/no response), in source coding (the task code sets `resp_reward = expt_rewardIDX × resp_category`, so 1 is the planted tree); the counterbalanced left/right arrow-key assignment is `subcode_3`. RTs are carried raw as `resp_reactiontime` (source stores seconds, with some implausible/negative values in Exp1b/Exp2a) rather than rescaling to the schema's `rt`; units are ambiguous in the source so no conversion was applied. `condition` (b200/b20/b2/interleaved) is derived per subject from the run-length mode of `expt_contextIDX` over the 400 training trials (it agrees with the source group code for every participant: `subcode_0` = 3 ⟺ interleaved). `participant_id` is the source's per-assignment subject code (`subExp` / `expt_subject`).

#### exp0 (Exp1a — cardinal reward axis, n=176)
| column | description |
|--------|-------------|
| participant_id | Source subject code (subExp) per MTurk assignment, e.g. `1wkS9pIkBILv` |
| trial | 0..599 sequential trial within participant (training 0..399, test 400..599) |
| phase | `training` (session 1, blocks 1-2) or `test` (session 2, block 3, no feedback) |
| condition | Training regime, derived from context run-lengths: `b200` / `b20` / `b2` / `interleaved` |
| block | Source expt_block 0-indexed (0..2; 200 trials each) |
| state | Garden/rule context (north=0, south=1), 0-indexed expt_contextIDX |
| session_index | Source expt_sessIDX (1=training session, 2=test session) |
| context_index | Raw garden cue code 1..2 (north/south garden) |
| branch_index | Tree branchiness index 1..5 (B1..B5) |
| leaf_index | Tree leafiness index 1..5 (L1..L5) |
| reward_index | Reward-magnitude level of the category, -50/-25/0/25/50 points |
| category_index | Stimulus category code -1/0/1 (position along the boundary) |
| exemplar | Image exemplar variant a..h among the 8 per (B,L) cell |
| stimulus | Image name `B{branch}L{leaf}_{exemplar}.png` (ArenaTrees files) |
| response | Accept/reject choice (resp_category): 1 = accept (plant), 0 = reject; empty (NaN) when no response was recorded |
| correct | resp_correct 0/1 (also scored on test trials offline; 0 where no response) |
| reward | resp_reward in points (-50..50); empty when no response recorded |
| return | resp_return, cumulative reward points over the session |
| optimal_reward | expt_rewardOPT, reward magnitude of the optimal response (0..50) |
| optimal_return | expt_returnOPT, optimal cumulative return |
| resp_reactiontime | Raw reaction time as stored (seconds; unmodified, some negative values present) |
| resp_timestamp | Response timestamp, ms epoch (e.g. 1.484e12) |
| age | Age-band midpoint from source subAge (18-20→19, 21-30→25, 31-40→35, 41-50→45, 51-60→55, 61+→65; `data_getAllData.m`), not an exact age |
| gender_code | Source subGender: 0 = male, 1 = female (`data_getAllData.m`; the paper's totals of 352 male / 231 female, p. 9, match the four experiments' counts under this coding) |
| subacc | Source subAcc: fraction correct over all 600 trials, excluding boundary stimuli (category_index 0) and scoring responses slower than 5 s as errors (reproduced exactly for all 176 participants) |
| subcode_0 | Source subCodes[0], training curriculum: 1 = blocked, north garden first; 2 = blocked, south garden first; 3 = interleaved (`expt_parameters.js`; the source analyses use `subCodes(1,:)==3` for the interleaved group) |
| subcode_1 | Source subCodes[1], reward-sign flag of the north-garden rule: 0 = reward increases with leafiness, 1 = decreases (verified on the training rewards) |
| subcode_2 | Source subCodes[2], reward-sign flag of the south-garden rule: 0 = reward increases with branchiness, 1 = decreases (verified on the training rewards) |
| subcode_3 | Source subCodes[3], arrow-key assignment: 0 = left arrow rejects / right arrow accepts, 1 = left accepts / right rejects (inferred from the id-code layout in `expt_parameters.js`; not checkable from the trial data) |
| subcode_4 | Source subCodes[4] = training block length (200/20/2); the interleaved group also carries 200 |
| subcode_5 | Source subCodes[5], boundary type: 0 = cardinal, 1 = diagonal (`data_getAllData.m`); constant within each experiment |
| subcode_6 | Source subCodes[6], boundary/reward-sign code 1..4 = f(subcode_1, subcode_2) with (0,0)→1, (1,1)→2, (1,0)→3, (0,1)→4 (`data_add_boundarycodes.m`) |
| report_north | Post-experiment free-text: what the participant learned for the north garden |
| report_south | Post-experiment free-text: what the participant learned for the south garden |

#### exp1 (Exp1b — diagonal reward axis, n=166)
| column | description |
|--------|-------------|
| participant_id | Source subject code (subExp) per MTurk assignment, e.g. `1wkS9pIkBILv` |
| trial | 0..599 sequential trial within participant (training 0..399, test 400..599) |
| phase | `training` (session 1, blocks 1-2) or `test` (session 2, block 3, no feedback) |
| condition | Training regime, derived from context run-lengths: `b200` / `b20` / `b2` / `interleaved` |
| block | Source expt_block 0-indexed (0..2; 200 trials each) |
| state | Garden/rule context (north=0, south=1), 0-indexed expt_contextIDX |
| session_index | Source expt_sessIDX (1=training session, 2=test session) |
| context_index | Raw garden cue code 1..2 (north/south garden) |
| branch_index | Tree branchiness index 1..5 (B1..B5) |
| leaf_index | Tree leafiness index 1..5 (L1..L5) |
| reward_index | Reward-magnitude level of the category, -50/-25/0/25/50 points |
| category_index | Stimulus category code -1/0/1 (position along the boundary) |
| exemplar | Image exemplar variant a..h among the 8 per (B,L) cell |
| stimulus | Image name `B{branch}L{leaf}_{exemplar}.png` (ArenaTrees files) |
| response | Accept/reject choice (resp_category): 1 = accept (plant), 0 = reject; empty (NaN) when no response was recorded |
| correct | resp_correct 0/1 (also scored on test trials offline; 0 where no response) |
| reward | resp_reward in points (-50..50); empty when no response recorded |
| return | resp_return, cumulative reward points over the session |
| optimal_reward | expt_rewardOPT, reward magnitude of the optimal response (0..50) |
| optimal_return | expt_returnOPT, optimal cumulative return |
| resp_reactiontime | Raw reaction time as stored (seconds; unmodified, some negative values present) |
| resp_timestamp | Response timestamp, ms epoch (e.g. 1.484e12) |
| age | Age-band midpoint from source subAge (18-20→19, 21-30→25, 31-40→35, 41-50→45, 51-60→55, 61+→65; `data_getAllData.m`), not an exact age |
| gender_code | Source subGender: 0 = male, 1 = female (`data_getAllData.m`; the paper's totals of 352 male / 231 female, p. 9, match the four experiments' counts under this coding) |
| subacc | Source subAcc: fraction correct over the 200 test trials, excluding boundary stimuli (category_index 0) and scoring responses slower than 5 s as errors (`data_getAllData.m`; reproduced exactly for all 166 participants) |
| subcode_0 | Source subCodes[0], training curriculum: 1 = blocked, north garden first; 2 = blocked, south garden first; 3 = interleaved (`expt_parameters.js`; the source analyses use `subCodes(1,:)==3` for the interleaved group) |
| subcode_1 | Source subCodes[1], reward-sign flag of the north-garden rule: 0 = reward increases with leafiness + branchiness, 1 = decreases (verified on the training rewards) |
| subcode_2 | Source subCodes[2], reward-sign flag of the south-garden rule: 0 = reward increases with branchiness − leafiness, 1 = decreases (verified on the training rewards) |
| subcode_3 | Source subCodes[3], arrow-key assignment: 0 = left arrow rejects / right arrow accepts, 1 = left accepts / right rejects (inferred from the id-code layout in `expt_parameters.js`; not checkable from the trial data) |
| subcode_4 | Source subCodes[4] = training block length (200/20/2); the interleaved group also carries 200 |
| subcode_5 | Source subCodes[5], boundary type: 0 = cardinal, 1 = diagonal (`data_getAllData.m`); constant within each experiment |
| subcode_6 | Source subCodes[6], boundary/reward-sign code 5..8 = 4 + f(subcode_1, subcode_2) with (0,0)→1, (1,1)→2, (1,0)→3, (0,1)→4 (`data_add_boundarycodes.m`) |
| report_north | Post-experiment free-text: what the participant learned for the north garden |
| report_south | Post-experiment free-text: what the participant learned for the south garden |

#### exp2 (Exp2a — cardinal axis, n=138, B200 + interleaved only)
Main-task columns are the same as exp0/exp1 minus the demographics block (`age`, `gender_code`, `subacc` are absent from this experiment's source struct), plus the rating-session columns below. The rating phase (`rating_pre`, `rating_post`, 150 trials each) holds the dissimilarity-placement task: participants dragged each tree onto a 2D canvas; the placement coordinates are the rating. Rows are in chronological session order within each participant — `rating_pre` (trial 0..149), `training` (150..549), `test` (550..749), `rating_post` (750..899) — with `trial` numbering that order 0..899; `phase` marks the phase. The order is established by the timestamps (`rating_start_time` <= all main-task `resp_timestamp` <= `rating_finish_time` for every participant); the rating sources carry only session-level timestamps, so within each rating phase the source row order is kept.

| column | description |
|--------|-------------|
| participant_id | Source subject code (expt_subject) per MTurk assignment, e.g. `1wkS9pIkBILv` |
| trial | 0..899 sequential trial within participant (rating_pre 0..149, training 150..549, test 550..749, rating_post 750..899) |
| phase | `rating_pre` / `training` / `test` / `rating_post` in session order |
| condition | `b200` or `interleaved` (only these two groups in Exp2), taken from the dissim filename |
| block | Source expt_block 0-indexed (0..2; 200 trials each) on main-task rows; rating rows carry 0 (rating_pre) and 3 (rating_post) so that (block, trial) orders each participant's session chronologically — block 0 therefore spans rating_pre and the first training block; use `phase` to separate them |
| state | Garden/rule context (north=0, south=1), 0-indexed expt_contextIDX |
| session_index | Source expt_sessIDX (1=training session, 2=test session) |
| context_index | Raw garden cue code 1..2 (north/south garden) |
| branch_index | Tree branchiness index 1..5 (B1..B5) |
| leaf_index | Tree leafiness index 1..5 (L1..L5) |
| reward_index | Reward-magnitude level of the category, -50/-25/0/25/50 points |
| category_index | Stimulus category code -1/0/1 (position along the boundary) |
| exemplar | Image exemplar variant a..h among the 8 per (B,L) cell |
| stimulus | Image name `B{branch}L{leaf}_{exemplar}.png` (ArenaTrees files) |
| response | Rating rows: JSON `[x_final, y_final]`; main rows: 1 = accept (plant), 0 = reject |
| correct | resp_correct 0/1 (also scored on test trials offline; 0 where no response) |
| reward | resp_reward in points (-50..50); empty when no response recorded |
| return | resp_return, cumulative reward points over the session |
| optimal_reward | expt_rewardOPT, reward magnitude of the optimal response (0..50) |
| optimal_return | expt_returnOPT, optimal cumulative return |
| resp_reactiontime | Raw reaction time as stored (seconds; unmodified, some negative values present) |
| resp_timestamp | Response timestamp, ms epoch (e.g. 1.484e12) |
| subcode_0 | Source subCodes[0], training curriculum: 1 = blocked, north garden first; 2 = blocked, south garden first; 3 = interleaved (`expt_parameters.js`; the source analyses use `subCodes(1,:)==3` for the interleaved group) |
| subcode_1 | Source subCodes[1], reward-sign flag of the north-garden rule: 0 = reward increases with leafiness, 1 = decreases (verified on the training rewards) |
| subcode_2 | Source subCodes[2], reward-sign flag of the south-garden rule: 0 = reward increases with branchiness, 1 = decreases (verified on the training rewards) |
| subcode_3 | Source subCodes[3], arrow-key assignment: 0 = left arrow rejects / right arrow accepts, 1 = left accepts / right rejects (inferred from the id-code layout in `expt_parameters.js`; not checkable from the trial data) |
| subcode_4 | Source subCodes[4] = training block length (200/20/2); the interleaved group also carries 200 |
| subcode_5 | Source subCodes[5], boundary type: 0 = cardinal, 1 = diagonal (`data_getAllData.m`); constant within each experiment |
| subcode_6 | Source subCodes[6], boundary/reward-sign code 1..4 = f(subcode_1, subcode_2) with (0,0)→1, (1,1)→2, (1,0)→3, (0,1)→4 (`data_add_boundarycodes.m`); equals `boundary_index` |
| report_north | Post-experiment free-text: what the participant learned for the north garden |
| report_south | Post-experiment free-text: what the participant learned for the south garden |
| rating_index | Source trial number 1..150 within the rating session |
| x_orig / y_orig | Random initial canvas position of the stimulus |
| x_final / y_final | Participant's final placement coordinates (the dissimilarity rating) |
| boundary_index | Source boundaryIDX, 1..4 (the cardinal boundary/reward-sign variants); identical to subcode_6 for every participant |
| rating_sex | Participant sex as self-reported at rating time (`female`, ...) |
| rating_age | Participant age band as self-reported (`31-40`, ...) |
| rating_task | Source expt_task code, e.g. `timo/240617_tt_r_PreMainPost` |
| rating_start_time / rating_finish_time | Rating-session wall-clock timestamps, ms epoch |

#### exp3 (Exp2b — diagonal axis, n=103, B200 + interleaved only)
| column | description |
|--------|-------------|
| participant_id | Source subject code (expt_subject) per MTurk assignment, e.g. `1wkS9pIkBILv` |
| trial | 0..899 sequential trial within participant (rating_pre 0..149, training 150..549, test 550..749, rating_post 750..899) |
| phase | `rating_pre` / `training` / `test` / `rating_post` in session order |
| condition | `b200` or `interleaved` (only these two groups in Exp2), taken from the dissim filename |
| block | Source expt_block 0-indexed (0..2; 200 trials each) on main-task rows; rating rows carry 0 (rating_pre) and 3 (rating_post) so that (block, trial) orders each participant's session chronologically — block 0 therefore spans rating_pre and the first training block; use `phase` to separate them |
| state | Garden/rule context (north=0, south=1), 0-indexed expt_contextIDX |
| session_index | Source expt_sessIDX (1=training session, 2=test session) |
| context_index | Raw garden cue code 1..2 (north/south garden) |
| branch_index | Tree branchiness index 1..5 (B1..B5) |
| leaf_index | Tree leafiness index 1..5 (L1..L5) |
| reward_index | Reward-magnitude level of the category, -50/-25/0/25/50 points |
| category_index | Stimulus category code -1/0/1 (position along the boundary) |
| exemplar | Image exemplar variant a..h among the 8 per (B,L) cell |
| stimulus | Image name `B{branch}L{leaf}_{exemplar}.png` (ArenaTrees files) |
| response | Rating rows: JSON `[x_final, y_final]`; main rows: 1 = accept (plant), 0 = reject |
| correct | resp_correct 0/1 (also scored on test trials offline; 0 where no response) |
| reward | resp_reward in points (-50..50); empty when no response recorded |
| return | resp_return, cumulative reward points over the session |
| optimal_reward | expt_rewardOPT, reward magnitude of the optimal response (0..50) |
| optimal_return | expt_returnOPT, optimal cumulative return |
| resp_reactiontime | Raw reaction time as stored (seconds; unmodified, some negative values present) |
| resp_timestamp | Response timestamp, ms epoch (e.g. 1.484e12) |
| subcode_0 | Source subCodes[0], training curriculum: 1 = blocked, north garden first; 2 = blocked, south garden first; 3 = interleaved (`expt_parameters.js`; the source analyses use `subCodes(1,:)==3` for the interleaved group) |
| subcode_1 | Source subCodes[1], reward-sign flag of the north-garden rule: 0 = reward increases with leafiness + branchiness, 1 = decreases (verified on the training rewards) |
| subcode_2 | Source subCodes[2], reward-sign flag of the south-garden rule: 0 = reward increases with branchiness − leafiness, 1 = decreases (verified on the training rewards) |
| subcode_3 | Source subCodes[3], arrow-key assignment: 0 = left arrow rejects / right arrow accepts, 1 = left accepts / right rejects (inferred from the id-code layout in `expt_parameters.js`; not checkable from the trial data) |
| subcode_4 | Source subCodes[4] = training block length (200/20/2); the interleaved group also carries 200 |
| subcode_5 | Source subCodes[5], boundary type: 0 = cardinal, 1 = diagonal (`data_getAllData.m`); constant within each experiment |
| subcode_6 | Source subCodes[6], boundary/reward-sign code 5..8 = 4 + f(subcode_1, subcode_2) with (0,0)→1, (1,1)→2, (1,0)→3, (0,1)→4 (`data_add_boundarycodes.m`); equals `boundary_index` |
| report_north | Post-experiment free-text: what the participant learned for the north garden |
| report_south | Post-experiment free-text: what the participant learned for the south garden |
| rating_index | Source trial number 1..150 within the rating session |
| x_orig / y_orig | Random initial canvas position of the stimulus |
| x_final / y_final | Participant's final placement coordinates (the dissimilarity rating) |
| boundary_index | Source boundaryIDX, 5..8 (the diagonal boundary/reward-sign variants); identical to subcode_6 for every participant |
| rating_sex | Participant sex as self-reported at rating time (`female`, ...) |
| rating_age | Participant age band as self-reported (`31-40`, ...) |
| rating_task | Source expt_task code, e.g. `timo/240617_tt_r_PreMainPost` |
| rating_start_time / rating_finish_time | Rating-session wall-clock timestamps, ms epoch |

Notes:
- `condition` is derived from trial structure; it agrees with the source group code (`subcode_0` = 3 ⟺ interleaved) for every participant, and the counts match the paper's group sizes (exp1a: 48/41/40/47, consistent with the t-test degrees of freedom on p. 3; exp2a: 68/70; exp2b: 55/48).
- The source ships only the participants the paper retained (768 recruited, >55% test-accuracy inclusion criterion, 583 included, p. 9): 176 + 166 + 138 + 103 = 583, and the paper's 352 male / 231 female totals are reproduced by `gender_code`/`rating_sex`. The paper's age range 19–55 (p. 9) refers to the `age` band midpoints; exp1 also holds seven participants in the 61+ band (65). One exp0 participant has `subacc` 0.515 and 12 participants across the four experiments have a test-phase `correct` mean ≤ 0.55, so the criterion was evidently not applied to these exact quantities.
- Exp3/Exp4 in the paper are CNN / β-VAE simulations and are excluded; only human `allData_*.mat` and `data_dissim/*.mat` files are included.
- scipy is a required dependency of transform.py because the raw sources are MATLAB `.mat` files (loaded with `scipy.io.loadmat`).

## Update (2026-08-13)
- PII: dropped the `worker_id` column (raw MTurk worker IDs, source `subTurker` / `expt_turker`) from all four exp files (exp0..exp3). `participant_id` (per-assignment subject code) is unchanged; no rows or other values touched.
- Chronology (exp2.csv and exp3.csv only): each participant's rows were previously stored as main task (training+test, trial 0..599) followed by `rating_post` then `rating_pre` (each trial 0..149). Rows are now re-sorted into true chronological order per participant — `rating_pre`, `training`, `test`, `rating_post` — verified with the timestamp columns (`rating_start_time` <= all main `resp_timestamp` <= `rating_finish_time` for all 138 exp2 and 103 exp3 participants), and `trial` renumbered 0..899 within each participant. Within-phase row order is unchanged (rating sources have session-level timestamps only; main-task order is the source trial order). exp2 retains 7 single backwards `resp_timestamp` steps inside the main task (one each for 7 participants, 2-8 min; a source clock artifact, 4 of them tied to the documented negative `resp_reactiontime` values) — those rows are kept in source trial-order position. exp0/exp1 order was already correct.

CSVs fixed in place from the previous release; transform.py updated to produce the same output
from raw. The previous version remains in the repo's git history.

## Text-format conversion

All four experiments (exp0..exp3) were transcribed to natural language. Each trial's
stimulus is the tree's two nameable features (branchiness, leafiness), and the response
is the accept/reject choice (1 = accept in the source coding), rendered as a single letter
whose assignment to accept/reject is randomized per participant (the letters are arbitrary
labels; the source's left/right arrow-key assignment is `subcode_3`). exp2/exp3 additionally include the pre/post dissimilarity-placement rating
phases, where the free response is the drag-to-position coordinate.

Sample transcript (exp0, first participant, through the first response):

```
You manage two gardens, a north and a south garden. In each garden some trees grow well and others do not. Each trial you visit one garden and see one tree; trees vary in branchiness (how many branches) and leafiness (how many leaves). Decide whether to plant the tree in that garden. Press A to accept (plant) the tree or B to reject it. You learn which trees grow well in each garden by trial and error: good choices gain points and bad choices lose points.
You first complete 400 training trials with points feedback, then 200 test trials without feedback.
In the south garden you see a tree with branchiness 1, leafiness 4. You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE] …
```

Run: deepseek-v4-flash-0731, 2026-08-24
## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: psychophysical decision-boundary model — unconstrained 2-boundary (8 free params: boundary angle + logistic offset/slope/lapse per task) vs constrained 1-boundary (4 free params), fit to no-feedback test choices by MLE and compared via per-group summed BIC (log model evidence = -0.5*BIC).
Reproduced: two_boundary_wins_all_groups_cardinal; b200_factorization_advantage_cardinal; diagonal_factorized_b200_not_interleaved.
Not reproduced: none.
Numeric mismatch: none (paper's reported protected exceedance probabilities were not recomputed; the per-group summed-BIC winner for Experiment 1a and the B200-vs-Interleaved factorized advantage, and for Experiment 1b the B200 2-boundary vs Interleaved 1-boundary preference, all reproduce).
Partial validation: none.
Indeterminate: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24


## Online experiment

Four static jsPsych v8 experiments under `experiments/expN/` (exp0=Exp1a cardinal,
exp1=Exp1b diagonal, exp2=Exp2a cardinal+rating, exp3=Exp2b diagonal+rating) were
built from the paper + the dataset's CSVs (no simulator exists in this repo). The
generative rule, recovered directly from the data, is reproduced exactly (verified:
0 category/reward/feedback mismatches over 70k+ exp0/exp1 training trials). The
headless Chromium round trip (`?mode=simulate`) passed for all four experiments:
saved-CSV column names match `expN.csv` exactly and row counts are correct
(600 rows/session for exp0/exp1, 900 for exp2/exp3), with no outbound requests.
Rating rows for exp2/exp3 use `response = "[x_final, y_final]"` and blank
main-task fields, matching the data. Note (recoverable design, not an assumption):
the on-screen tree is the dataset's own arena-tree PNG set; accept/reject is
presented as `A` / left-arrow = accept (recorded as response 1) and `B` /
right-arrow = reject (response 0), a presentational choice since the source's
key↔accept mapping is counterbalanced and not recoverable. Cosmetic browser defaults (800 ms
cue, 1200 ms feedback, 300 ms ITI, optional demographics/report form) do not
change the task or data. `exp2/exp3` rating only covers B200 + interleaved, as in
the source. No data-collection backend is shipped — `saveData` offers the finished
CSV as a download (see `experiments/README.md`).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

All four experiments received a text simulator: `simulate0.py` (Exp1a cardinal),
`simulate1.py` (Exp1b diagonal), `simulate2.py` (Exp2a cardinal + pre/post
dissimilarity-placement rating), `simulate3.py` (Exp2b diagonal + rating). Each
reproduces the paper's design (400 training + 200 test trials in 200-trial
blocks; B200/B20/B2/interleaved garden run-structures in Exp1, B200/interleaved
only in Exp2; rating phases of 150 trials = 6 passes over the 25 cells) and the
data-derived generative process: a balanced (context × branch × leaf) stimulus
deck using training exemplars a-d (each cell × 2 per garden) and test exemplars
e-h (each combination exactly once), the counterbalanced cardinal/diagonal
reward rule (accept pays signed reward_index, reject pays 0, boundary pays 0),
and block-wise cumulative `return`/`optimal_return` (first trial of each block
recorded as 0). The accept/reject response is the single letters A/B assigned
per participant by the same md5-of-participant_id policy as build_jsonl.py, so
each simulated transcript is byte-identical to the build_jsonl.py round trip
(verified for all four experiments). Assumptions: missed (no-response) trials
are not modeled; reaction times, timestamps, demographics, the free-text
reports and the rating-session metadata are dropped as not producible by a text
simulator; rating initial canvas positions and rating-stimulus exemplars are
drawn at random (neither enters the transcript).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 2, major 6, minor 2; fixed 8, open 2).

Checked: paper (https://doi.org/10.1073/pnas.1800755115, Europe PMC PDF), original data (https://github.com/summerfieldlab/Flesch_etal_2018 at eb84270, allData_*.mat + data_dissim/*.mat, plus the task and analysis code), exp0-exp3, transform re-run (byte-identical before the block fix), transcripts (rebuilt byte-for-byte), simulators (run + round trip, byte-identical for all four), modeling (all 3 results reproduced on the full sample), analysis (all 3 effects reproduced), logs. Skipped: none.

Fixed:
- critical: build_jsonl.py (and simulate0-3.py) randomized per participant which response value counts as accept, but the source coding is fixed: the task code sets resp_reward = expt_rewardIDX x resp_category (Experiments/Exp1/js/expt_response.js) and every training trial of exp0/exp1 has reward == reward_index when response = 1 and reward == 0 when response = 0. 97/176 (exp0), 91/166 (exp1), 67/138 (exp2) and 49/103 (exp3) transcripts narrated the reject letter followed by non-zero points. Set accept_val = 1 (only the letter is randomized), regenerated transcripts0-3.jsonl (no such trial remains), fixed the same policy in all four simulators; round trips byte-identical.
- critical: transcripts2/3.jsonl narrated the pre-training rating phase after the test phase (from line 603), because build_jsonl.py sorts by (block, trial) and the rating rows had an empty block. transform.py now sets block 0 on rating_pre and 3 on rating_post rows (only the block column of the 41400 + 30900 rating rows of exp2/exp3.csv changed; (block, trial) now equals the chronological trial order), transcripts2/3 rebuilt (rating_pre, training, test, rating_post), simulate2/3.py emit the same blocks and phase order, README block rows updated.
- major: README described gender_code as undocumented and age as years 19..55; the source's data_getAllData.m codes male = 0 / female = 1 (the paper's 352 male / 231 female, p. 9, are reproduced exactly) and stores age-band midpoints (18-20 -> 19, ..., 61+ -> 65; exp1 holds 65). Rows corrected.
- major: README described subacc as the fraction correct over 600 trials; the source computes it excluding boundary stimuli (category_index 0) and scoring RT > 5 s as errors, over the 200 test trials in exp1 (reproduced 166/166) and over all 600 trials in exp0 (reproduced 176/176). Rows corrected per experiment.
- major: README called subcode_0..6 undocumented; the source task code (expt_parameters.js), data_getAllData.m and data_add_boundarycodes.m decode them and the data confirm: subcode_0 = curriculum (1/2 blocked with north/south first, 3 interleaved; matches the derived condition for all 583 participants), subcode_1/2 = reward-sign flags of the north/south rule (verified on the training rewards in all four experiments), subcode_3 = arrow-key assignment (inferred from the id layout), subcode_4 = block length (the interleaved group carries 200, not blank), subcode_5 = 0 cardinal / 1 diagonal, subcode_6 = boundary code f(subcode_1, subcode_2) + 4*subcode_5. Rows corrected.
- major: README gave boundary_index as a single value (1 in exp2, 5 in exp3); the data hold 1..4 and 5..8 and equal subcode_6 for every participant. Rows corrected.
- major: README Notes, Columns intro and Text-format section claimed the interleaved group is not labelled in the source and that the accept/reject coding is not recoverable; both are (subcode_0 = 3; resp_category 1 = accept). Text corrected, sample transcript updated (first token B -> A), a provenance note on the paper's inclusion criterion and sample added.
- major: logs/auto-exp-verify.sessions.json and transcripts/auto-exp-verify.log mentioned two other datasets (371 + 115 occurrences inside the previous run's tool output); the names were replaced by <other-dataset>.

Open:
- minor (inside the source): the paper reports an age range of 19-55 y and a >55% test-accuracy inclusion criterion (p. 9); the source ships seven exp1 participants coded 65 (61+ band), one exp0 participant with subacc 0.515, and 12 participants across the four experiments with a test-phase correct mean <= 0.55. The data are faithful to the source; noted in the README.
- minor (checker limitation): transcripts2.jsonl (138/138) and transcripts3.jsonl (103/103) use rating-phase tokens (the participant's placement coordinates, e.g. [785.92, 522.92]) that cannot appear in the instructions; the instructions describe the response format, the tokens map one-to-one onto the CSV, and the transcribe rules allow numeric/free-form tokens for continuous responses.

Run: claude-fable-5-1, 2026-09-14
