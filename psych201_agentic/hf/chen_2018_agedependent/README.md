---
tags:
- paradigm:risky-choice
- cognitive-modeling:needs-review
- psych-201
- js-experiment:pass
- text-format:pass
- simulator:pass
- verification:pass
---
# chen_2018_agedependent

- Paper: https://doi.org/10.1371/journal.pcbi.1006304
- Data source: https://osf.io/fu9be/
- PDF: https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1006304&type=printable
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Chen, X., Rutledge, R. B., Brown, H. R., Dolan, R. J., Bestmann, S., & Galea, J. M. (2018). Age-dependent Pavlovian biases influence motor decision-making. PLOS Computational Biology, 14(7), e1006304.

## Experiment summary
In an app-based motor decision-making task (exp0, N=26532 across six age bands), each trial presents a gamble of playing (tap 5 targets along a path) for a stake worth -100 to +100 points versus skipping for a small guaranteed gain/loss; 42 trials per participant vary reward/punishment magnitude, target-size difficulty (7 levels), and random sine-curve paths, and record the skip/gamble choice, success/failure outcome, RT, and touch coordinates along with gender/education/device/screen-size covariates. A control estimation study (exp1, N=120) validates perceived success probability with trial-level motor-outcome and self-reported probability ratings. The paper fits Approach-Avoidance and Prospect Theory computational models to choices across age groups to explain age-dependent Pavlovian attraction toward reward.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Anonymized subject identifier (P00000..P26531), assigned in first-appearance order from the source's `id` field. Use `id` field in appDataNew.mat to cross-reference with original IDs. |
| trial | 0..41, 0-indexed trial number within participant. Source records 42 trials per participant in fixed order. |
| response | 0 = skipped (chose not to play), 1 = gambled/played. |
| reward | Actual points received on that trial. If skipped: `skipscore` (-10 or +10). If gambled and failed (outcome=2): `losescore` (-100,-60,-20,0). If gambled and succeeded (outcome=1): `winscore` (0,20,60,100). |
| rt | Reaction time in milliseconds. First touch timestamp from the 5-point `time` array, converted from seconds to ms. NaN when participant did not touch the screen. One source trial (P03889, trial 9) carries a negative first timestamp (-3.17 s) and is kept as is. |
| age | Age band code: 1=18-24, 2=25-29, 3=30-39, 4=40-49, 5=50-59, 6=60+. |
| age_group | Descriptive age band label matching the code in `age`. |
| gender | Participant gender: m (source code 0), f (source code 1). |
| education | Education level code as recorded in source: 0 = school (GCSE or similar), 1 = school (A-levels or similar), 2 = university degree, 3 = advanced degree (MA, PhD, etc.). |
| level | Target-size difficulty level, 1 (easiest, largest target) to 7 (hardest, smallest target). |
| radius | Target radius in pixels (68–128, for iPhone 4/4S/5 form factor; scaled on other devices). |
| winscore | Points if the participant plays and succeeds (0, 20, 60, 100). |
| losescore | Points if the participant plays and fails (-100, -60, -20, 0). |
| skipscore | Points if the participant skips (-10 or +10). |
| RPscore | Trial-type stake value: positive for reward trials (20,60,100), negative for punishment trials (-100,-60,-20). |
| gamble | Raw source gamble flag: 0=skip, 1=play/gamble. Same as `response` but in source's original coding. |
| outcome | Performance outcome: 0=skipped, 1=played and succeeded, 2=played and failed. |
| amplitude | Sine-curve amplitude (-0.9 to -0.3 and 0.3 to 0.9) controlling the width of the target path. |
| angle | Sine-curve angle in degrees (90–359), controlling the path's sinusoidal section. |
| screen_size_raw | Raw device screen size in inches (e.g. 3.5, 4.7, 9.7). |
| screen_size | Screen size rounded to even inches (4, 6, 8, 10). |
| point_final | Total accumulated points at end of session. |
| device_type | Hardware string identifying the device model (e.g. "iPhone4,1", "iPad3,1"). |
| location | Numeric location code from source. |
| time_stamps | JSON array of 5 timestamps (seconds) for the five sequential touches; NaN entries where fewer than 5 touches occurred. First element = RT in seconds. |
| touch_x | JSON array of 5 x-coordinates (0–640) of the participant's touches. |
| touch_y | JSON array of 5 y-coordinates (0–960) of the participant's touches. |
| button_x | JSON array of 5 x-coordinates of the target-button centers. |
| button_y | JSON array of 5 y-coordinates of the target-button centers. |
| valid | Always 1: the source records a choice on every trial. Gambles where the participant did not start tapping within 7 s are failed gambles (outcome=2, rt NaN), as in the source's own analyses. |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Anonymized subject identifier (P00000..P00119), assigned in first-appearance order across all 6 age-group files. |
| trial | 0..41, 0-indexed trial number within participant. |
| response | Participant's self-reported rating of success probability (0–10, steps of 10%) given before the tapping action. NaN where source recorded no response. |
| execute | Motor outcome on that trial, source column `execute`: 0 = failed to hit all targets, 1 = successfully hit all targets. NaN where source recorded no response. |
| age | Age band code: 1=18-24, 2=25-29, 3=30-39, 4=40-49, 5=50-59, 6=60+. |
| age_group | Descriptive age band label matching the code in `age`. |
| gender | Participant gender: m (source code 0), f (source code 1). |
| screen_size | Device screen size in inches, read from screenSizeAllSubj.xlsx matched by age group and within-group subject order. The source lists the sizes without participant IDs (21 rows for age group 25-29, 19 for 30-39, 20 for the others), so the within-group order match is an assumption and the 20th participant of the 30-39 group gets NaN. |
| valid | 1 = response and execute both non-missing, 0 = either missing. |

The economic-decision `.mat` file (`happyapp_aafit_5oct2015_joe.mat`) contains per-subject model-fitting summary data used for the cross-domain generalization analysis (Figure 7), not trial-level choice data, so it was not transformed into an experiment CSV.

## Text-format conversion

Both experiments were transcribed to natural language (`transcripts0.jsonl`, `transcripts1.jsonl` via `build_jsonl.py`); none were skipped. exp0 (motor gambling) and exp1 (success estimation) are both verbalisable — the stimulus is a stakes/target-size description and the decisions are a skip-vs-gamble go/no-go or a 0-10 probability rating, neither of which depends on non-reportable visual features. The letter used to indicate skip/gamble is randomized per participant and pinned down in each transcript's instructions.

**Sample transcript** (exp0, participant P00000, start up to first marked response):

```
Welcome to the motor gamble game. Your goal is to accumulate as many points as possible; you begin with 250 points. In each trial you see a path of 5 targets and a stake for that trial. Target difficulty runs from level 1 (largest, easiest target) to level 7 (smallest, hardest target). On a reward trial, skipping gives you +10 points; gambling means tapping all 5 targets from bottom to top within 1.2 seconds to win a bigger prize (+20, +60, or +100 points), or 0 points if you fail. On a punishment trial, skipping costs you -10 points; gambling avoids the punishment (0 points) if you succeed but you lose a bigger amount (-20, -60, or -100) if you fail. If you gamble, tap the 5 targets in order, from bottom to top, as quickly and accurately as you can. On each trial press A to skip the trial or B to take the gamble.
Reward trial: skip +10, gamble +60 or 0. Target difficulty level 2 (radius 118 px). You press [HUMAN_RESPONSE]B[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Online experiment

Both experiments got a runnable jsPsych v8 build under `experiments/` (`exp0/` and `exp1/`), and the headless round trip (random-agent, `?mode=simulate`) passed for both: each outputs a CSV matching the dataset schema (same column names, dtypes/codings, 42 rows, `trial` 0-41, correct `response`/`outcome`/`reward` codings, and the level/radius/amplitude/angle groupings). Set up and use the files from `experiments/README.md`.

ASSUMPTION worth surfacing: the original app's internal pixel-placement constant that maps (angle, amplitude) to the 5 target positions is not in the public datashare (which holds data + MATLAB analysis code only), so targets are placed with `x = 320 + 200*amplitude*sin(angle°*j/4)` (y evenly spaced). This is a visual-layout approximation only and does not change the data schema, the decision task, the reward/feedback process, or the block/trial structure. Per-trial feedback, the demographics form, button labels/colors and pacing are browser-only cosmetic defaults.

The step-8 visual rendering check was not run (text-only model; the data round trip passed).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Both experiments got a Python text simulator (`simulate0.py`, `simulate1.py`), and the round-trip check passed for each: regenerating transcripts from the simulator's DataFrame via `build_jsonl.py` returns byte-identical text to the simulator's prompts. No experiments were skipped. ASSUMPTIONs worth surfacing: per-target-size motor success and "did not start in time" probabilities are derived from exp0.csv (level 1->7, P(success | started) = .735/.725/.679/.636/.552/.451/.363; P(no start) = .010/.015/.024/.041/.068/.103/.152) since the paper publishes only Fig 1G's success-by-target-size; amplitude is uniform over ±0.3..±0.9 (step .1) and angle over 90-359 degrees, as seen in exp0.csv (paper: 0-360); exp1 (no per-trial target size in the CSV) draws motor success as Bernoulli(p=0.62), the aggregate empirical rate, and drops rating/motor for ~1.2% of trials (valid=0); participant covariates are sampled from the empirical marginal distributions. All failed gambles narrate "You fail to tap all 5 targets in time...", matching build_jsonl.py (the source codes "did not start in time" trials as ordinary failed gambles).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction

Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: approach-avoidance [alpha, mu, delta+, delta-] (winning model, id=10) vs prospect-theory [alpha, mu], per-participant MLE (16-restart bounded L-BFGS-B, jax-vectorized), compared on summed BIC; age effects as partial Spearman correlations of fitted parameters with age, controlling gender and education (paper's `partialcorr` approach).
Reproduced: aa_beats_prospect_theory (AA summed BIC 148293 < PT 165662), age_delta_plus (partial r=-0.139 vs paper -0.138), age_alpha (partial r=-0.115 vs paper -0.115).
Not reproduced: none.
Numeric mismatch: none material (partial correlations track the paper's reported values closely).
Partial validation: N=3400.
Indeterminate:
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 1, major 3, minor 8; fixed 8, open 4).

Checked: paper (https://doi.org/10.1371/journal.pcbi.1006304), original data (https://osf.io/fu9be/, appDataNew.mat and the six dataProbEstimateN.xlsx files), exp0-exp1, transform re-run (byte-identical before the fixes), transcripts (build_jsonl.py regenerates both files byte-for-byte), simulators (smoke test and round trip byte-identical), modeling (model.py --max-participants 3400, the same partial N as the section; the full fit of 26532 participants would exceed the time cap), analysis (all three effects reproduce), logs. Skipped: none.

Fixed:
- critical: exp1.csv had `response` = motor outcome (source `execute`) and the 0-10 rating in `estimate`, so the transcripts' marked tokens did not map onto `response`. transform.py now writes `response` = rating and `execute` = motor outcome; exp1.csv regenerated, build_jsonl.py and simulate1.py updated, transcripts1.jsonl rebuilt.
- major: exp0.csv flagged 38622 gamble trials with no tap within 7 s as `valid`=0. The source's own scripts (main.m, Figure3_dataSave.m, individualAccuracy.m) fit and count all 42 trials and the paper (p. 13) calls these failed actions; analysis.py and model.py were dropping them. Flag removed in transform.py, exp0.csv regenerated (only `valid` differs), simulate0.py and the README valid row updated; transcripts0.jsonl is unchanged byte-for-byte.
- major: transcripts1.jsonl used rating tokens 1-9 that the instructions never listed; build_jsonl.py and simulate1.py now list 0..10 in the instructions.
- major: README summary said N=26,532 (read as 26 by the checker) and 'tap a moving target'; the targets are static (paper p. 13: tap 5 sequential targets along a path). Corrected.
- minor: README column headings used '###' instead of '####'.
- minor: README did not document the education codes (source READ_ME p. 2: 0 GCSE, 1 A-levels, 2 degree, 3 advanced degree). Added.
- minor: exp1 `screen_size` is matched to participants by age group and within-group order, but the source screenSizeAllSubj.xlsx has no participant IDs and 21/19 rows for age groups 25-29/30-39 (data: 20 each), so one participant gets NaN. README now states the assumption.
- minor: `## Modeling reproduction` numbers came from fits that excluded the flagged trials; re-fitted on the corrected exp0.csv (N=3400): AA BIC 148293 < PT 165662, delta+ partial r=-0.139, alpha partial r=-0.115. Section updated; cognitive-modeling:needs-review kept because the validation is still partial.

Open:
- minor: exp0.csv rt = -3170 ms for P03889 trial 9; the source time array holds -3.17 s for that trial. Kept as the source value, noted in the README.
- minor: the paper (p. 12) reports 49 males among the 120 control participants; the source xlsx files code 60 participants as 0 and 60 as 1 and do not document the coding for these files. The transform follows the main dataset's convention (0 = m, 1 = f).
- minor: the paper (p. 13) says the second 60 control participants used a 5.1-inch device; rows 61-120 of the source screenSizeAllSubj.xlsx are all 4.7.
- minor: exp0 `participant_id` is the first-appearance index (P00000..) rather than the source's unique `id` field; the README documents the cross-reference. Re-keying would change every file and the transcript letter assignment, so it was left as is.

Run: claude-fable-5-1, 2026-09-10
