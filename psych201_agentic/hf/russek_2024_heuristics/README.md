---
tags:
- paradigm:risky-choice
- cognitive-modeling:pass
- psych-101
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:pass
---
# russek_2024_heuristics

- Paper: https://doi.org/10.1038/s41467-024-48547-z
- Data source: https://doi.org/10.5281/zenodo.10950132
- PDF: https://www.nature.com/articles/s41467-024-48547-z.pdf
- Full text: https://www.nature.com/articles/s41467-024-48547-z
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Russek, E. M., Moran, R., Liu, Y., Dolan, R. J., & Huys, Q. J. M. (2024). Heuristics in risky decision-making relate to preferential representation of information. Nature Communications, 15(1), 4269.

## Experiment summary
Two experiments link risky-decision heuristics to the neural reactivation of option value and probability information. Experiment 1 (exp0, N=21): participants in MEG made accept/reject choices between a sure safe option and a two-outcome gamble on each trial, across gain and loss blocks, with reaction times recorded; the paper analyzes 19 of them after excluding two who chose the same action on more than 80% of trials (p. 10). Experiment 2 (exp1, N=97): participants completed a detection/recognition priming task in which they detected and responded to object images on a subset of trials and otherwise made accept/reject gamble choices, with reaction times recorded; the paper recruited 100, lost 3 to recording errors, and analyzes 88 after excluding 5 who chose the same action on more than 80% of trials and 4 who failed to respond on detection trials (p. 14). The research question is whether the weights participants place on probability versus reward in their (additive-heuristic) choice strategy predict which information they preferentially reactivate/represent.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (`sub`, 1..21) as string |
| trial | 0-indexed trial counter per participant, in chronological order (ranked by source trial_number; 0..N-1) |
| response | Accept/reject choice: 1 = accept the gamble, 0 = reject and collect the safe option |
| block_number | Source block/run index (8..15); the 8 decision-task runs of the MEG session |
| safe_val_actual | Delivered points of the safe option on this trial (gain positive / loss negative after noise) |
| safe_val_base | Base points of the safe option before uniform(0,20)/(0,-20) noise was added |
| trigger_val_actual | Delivered points of the trigger outcome (O1 or O2) after noise |
| trigger_val_base | Base points of the trigger outcome before noise (from {47.5,60,75} or their negatives) |
| other_noise | The random noise value added to the non-trigger outcome (0 + noise) |
| o1_trigger | 1/0 whether O1 was the trigger option on this trial (else O2) |
| gl_type | gain / loss block type |
| accept | Raw accept/reject response (0/1), same as response |
| rt | Reaction time for the choice, in milliseconds |
| phase | Session phase, all "test" (source "TEST") |
| p_trigger | Probability of the trigger outcome given acceptance (0.2/0.4/0.6/0.8) |
| p_o1 | Probability that O1 is experienced given acceptance |
| o1_val | Points paired with outcome 1 (0 if non-trigger, trigger value + noise if trigger) |
| o2_val | Points paired with outcome 2 |
| safe_val | Points paired with the safe option (same as safe_val_actual) |
| outcome_reached | 1/2/3 which outcome was actually delivered on the trial (outcome index) |
| choice_number | 1..4 within-trial choice/outcome position counter from source |
| trial_number | Source trial counter across the session (1..~358, non-contiguous, gaps present) |
| task_block_number | Source block index 1..8 within the task |
| gain_trial | 1/0 whether this is a gain-block trial |
| loss_trial | 1/0 whether this is a loss-block trial |
| rt_sec | Reaction time for the choice, in seconds (same as rt/1000) |
| block | 0-indexed block within the task (source task_block_number 1..8, minus 1) |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (`sub`, 1..97) as string |
| trial | 0-indexed trial counter per participant (source trial_number 1..288, minus 1) |
| response | Accept/reject choice on choice trials (`accept`: 1 = accept gamble, 0 = reject/safe); empty on detection trials (the source records only whether the arrow-direction report was correct, see `correct`) and on choice trials with no recorded response |
| block_number | Source block/run index (8..11); the 4 blocks of the detection task |
| safe_val_actual | Delivered points of the safe option (loss blocks, negative) |
| safe_val_base | Base points of the safe option before noise |
| trigger_val_actual | Delivered points of the trigger outcome after noise |
| trigger_val_base | Base points of the trigger outcome before noise |
| other_noise | Noise value added to the non-trigger outcome |
| o1_trigger | 1/0 whether O1 was the trigger option |
| gl_type | gain / loss block type |
| accept | Raw accept/reject response on choice trials (0/1), NaN on detection trials |
| rt | Reaction time in milliseconds (choice RT on choice trials, arrow-detection RT on detection trials) |
| phase | Session phase, all "test" (source "TEST") |
| p_trigger | Probability of the trigger outcome given acceptance |
| p_o1 | Probability that O1 is experienced given acceptance |
| o1_val | Points paired with outcome 1 |
| o2_val | Points paired with outcome 2 |
| safe_val | Points paired with the safe option |
| outcome_reached | 1/2/3 which outcome was delivered on the trial |
| choice_number | 1..4 within-trial counter from source |
| trial_number | Source trial counter per participant (1..288) |
| recognition_number | 0 on choice trials; 1/2/3 = which of the three outcome stimuli was the probed (arrow) stimulus on detection trials |
| correct_recognition | 1/0 whether the arrow-direction response was correct on detection trials, NaN on choice trials |
| o1_image | Image file path used for outcome 1 |
| o2_image | Image file path used for outcome 2 |
| safe_image | Image file path used for the safe option |
| stim_pos_y | Vertical screen position code (1 or 2) of the probed stimulus |
| block | 0-indexed block within the task (source block_number 8..11, minus 8) |
| condition | choice if a gamble accept/reject was required, detection if an arrow-detection response was required |
| correct | 1/0 whether the arrow-direction report was correct on detection trials (same as `correct_recognition`), empty on choice trials and on missed detection trials |
| valid | 1 if a response was recorded on this trial, 0 if the trial has no response (missed) |

exp0 maps to the paper's Experiment/Risky-Decision MEG task (N=21); exp1 maps to the Detection/Recognition task (N=97). Both source files are the Zenodo behavioral data; the MEG, code, and analysis notebooks in the archive were not transformed. In exp1, `response` codes accept/reject on choice trials and is empty on detection trials, where the source records only the correctness of the arrow-direction report (`correct`); the trial type is given by `condition`; rows with no recorded response are tagged `valid=0`.
## Update (2026-08-13)
- Chronology fix, exp0.csv: the Zenodo source stores each participant's blocks out of chronological order (task_block_number 3..8 then 1..2), and `trial` had been assigned by cumcount over that scrambled row order, making it chronologically wrong for all 21 participants. Rows are now sorted per participant by the source `trial_number` (the true session counter) and `trial` renumbered 0..N-1 in that order (6,037 of 6,037 cells changed; `trial` now increases with `trial_number` for every participant).
- Chronology fix, exp1.csv: `trial` values were already correct (source trial_number − 1) but rows were stored in scrambled block order (block_number 10, 11, 8, 9). Rows re-sorted per participant by `trial`; no values changed (0 cells).
- No other column touched; per-participant row multisets identical to the previous release in both files.

CSVs fixed in place from the previous release; transform.py updated to produce the same output
from raw. The previous version remains in the repo's git history.

## Text-format conversion

Both experiments were transcribed to natural language (pass): exp0.csv (MEG risky decision, N=21) and exp1.csv (detection/recognition, N=97). Each participant's whole session is one string; free choices (accept/reject on choice trials) are wrapped in `[HUMAN_RESPONSE]` markers; detection trials (arrow-report correctness) and missed trials (`valid=0`) are narrated with no marker. No experiment was skipped — both risky-choice and arrow-detection trials are expressible in text without losing the decision information.

Sample transcript (exp0.csv, participant 1, from the start through the first response):
```
You are taking part in a risky decision-making task. On each trial you are offered a gamble and you must decide whether to accept it or reject it. The gamble has two possible outcomes, O1 and O2: if you accept the gamble, you receive one of them by chance. If you reject it, you instead collect a fixed safe outcome. First, three banknote images appear, each showing the number of points its outcome is worth: O1, O2, and the safe option. Then a probability symbol appears showing how likely you are to get O1 if you accept the gamble. Press A to accept the gamble, or press R to reject it and take the safe outcome. Your bonus is based on the points you collect. On gain blocks the points are positive; on loss blocks the points are negative (losses).
(gain block) O1 is worth 85 points, O2 is worth 16 points, the safe option is worth 46 points. If you accept, you have a 80% chance of O1 and a 20% chance of O2. You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE] …
```
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: Expected Value (Eq. 1) and Additive Heuristic (Eq. 2) logit choice models, per-participant bounded MLE (multi-start L-BFGS-B), compared by summed BIC on exp0 (Methods, "Computational models of choice data").
Reproduced: additive_over_ev (additive heuristic model is the lower-BIC winner over expected value), both_components_used (beta_prob > 0, p<.0001; beta_rew > 0, p=.0032, one-sample t-test).
Not reproduced: none.
Numeric mismatch: paper compares models with an integrated group BIC from a hierarchical EM fit; we use summed per-participant BIC from independent MLE fits (faithful approximation — same likelihood, same parameters, same comparison metric).
Partial validation: omitted.
Indeterminate: no blockers.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators
Both experiments got a text simulator: `simulate0.py` (exp0, MEG risky decision, 8 alternating gain/loss blocks) and `simulate1.py` (exp1, 4 blocks of choice and arrow-detection trials). Each regenerates the repo's `transcriptsN.jsonl` format byte-for-byte through the round-trip check (simulated `expN.csv` → `build_jsonl.py` → text equals the simulator's prompts; `rt`/`rt_sec`/`choice_number`/`trial_number` dropped as timing/source bookkeeping). No experiment was skipped. Assumptions: block type ordering random per participant (gain- or loss-first), 36 trials/block in exp0, P(detection)=1/3 in exp1, small per-condition miss probabilities in exp1, and P(correct)=0.928 on exp1 detection trials (narrated, the agent is not queried).
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment
Both experiments got a static jsPsych v8 online experiment: `experiments/exp0/` (MEG risky decision, 8×36) and `experiments/exp1/` (perceptual detection, 4×72). The headless round trip passed for both (schema-column check, dtypes/codings, row counts = 288, no console errors), and the visual check found no gross rendering breakage. Nothing was skipped. Note: `rt` (and `rt_sec` in exp0) are recorded by the browser; `choice_number`/`trial_number` are source bookkeeping the design does not produce and are omitted. Browser pacing not fixed by the paper (feedback/ITI durations, max response windows) and the 36-trials-per-block / P(detection)=1/3 draws follow the simulators' documented assumptions.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 1, major 1, minor 7; fixed 5, open 4).

Checked: paper (10.1038/s41467-024-48547-z), original data (https://doi.org/10.5281/zenodo.10950132, Data/MEG_behavioral_data.csv and Data/Detection_Task_Data.csv), exp0-exp1, transform re-run (byte-identical), transcripts, simulators (round trip), modeling, analysis, logs. Skipped: none.

Fixed:
- critical: exp1 `response` mixed the accept/reject choice (choice trials) with the correctness of the arrow-direction report (detection trials), both coded 0/1, so the four transcript tokens A/R/correct/incorrect could not map onto the response values (92/97 transcripts). transform.py now leaves `response` empty on detection trials (the source records no key, only `correct_recognition`) and adds the schema column `correct`; `valid` is computed from `accept`/`correct_recognition` and is unchanged (857 rows with valid=0). exp1.csv regenerated (only `response` changed, `correct` added; 27,936 rows, 97 participants). build_jsonl.py narrates detection trials without a marker ('Your arrow report is correct/incorrect.'); transcripts1.jsonl rebuilt (tokens A/R only, 18,482 marked choices). simulate1.py no longer queries the agent on detection trials (P(correct)=0.928, observed) and carries `correct`; round trip byte-identical. README exp1 columns and notes updated.
- major: logs/auto-exp-sim.sessions.json carried project-directory diffs from concurrent runs (modeling_pending.txt naming five other datasets, main.m, sub164.mat) in the session summary; pruned to this run's own entry.
- minor: '## Text-format conversion' had no Run line; added 'Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24' (date from logs/auto-exp-transcribe.sessions.json).
- minor: Experiment summary stated no N per experiment and read 'Experimen 1'; now 'Experiment 1 (exp0, N=21)' and 'Experiment 2 (exp1, N=97)'.
- minor: the paper analyzes 19 of 21 MEG participants (two chose the same action on >80% of trials, p. 10) and 88 of 100 online participants (3 lost to recording errors, 5 same-action, 4 no detection responses, p. 14); the source ships 21 and 97 with no exclusion flag; the Experiment summary now states these exclusions.

Open:
- minor: the paper is internally inconsistent about the outcome values: Fig. 1C caption (p. 3) gives trigger values {45, 65, 75} and safe values {20, 32, 44, 56}, Methods (p. 11) gives trigger {47.5, 60, 75} and safe {20, 40, 60, 80}; the source and both CSVs have trigger {47.5, 60, 75} and safe {20, 32, 44, 56}. Data faithful to the source.
- minor: Methods (p. 11) describe catch trials on 10% of MEG trials (report a reward, no probability stimulus) and a 6 s response window; the source holds only the 288 choice trials (283-288 rows per participant; the gaps in `trial_number` mark the catch trials and missed choices). Not in the source.
- minor: exp1.csv has 4 choice rows (participant 35 trials 268-269, participant 55 trials 1-2) with valid=0 and no `accept` but a recorded `rt` of about 5.2 s; kept as the source records them.
- minor: check_repo reports `response` empty on 34% of exp1 rows; these are the 9,313 detection rows (no choice recorded, see `correct`) and 141 missed choices. By design, documented in the README.

Run: claude-fable-5-1, 2026-09-10
