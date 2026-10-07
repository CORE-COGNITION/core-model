---
tags:
- paradigm:cue-integration
- cognitive-modeling:pass
- text-format:pass
- simulator:pass
- js-experiment:pass
- psych-101
- psych-201
- verification:needs-review
---
# binz_2022_heuristics

- Paper: https://doi.org/10.1037/rev0000330
- Data source: https://github.com/marcelbinz/HeuristicsFromBMLI
- PDF: https://osf.io/5du2b/download/
- Full text: https://psyarxiv.com/5du2b
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Online experiment

Static jsPsych v8 ports of all four text simulators live under `experiments/`
(`exp0/`-`exp3/`), reproducing the cued paired-comparison task and its on-screen
language verbatim. The headless `?mode=simulate` round trip passed for all four:
each saved CSV matches its `expN.csv` schema (30 tasks x 10 trials per
participant, exact column names and codings). Cosmetic browser-only defaults
were assumed (between-round Continue screen, 900 ms feedback, 200 ms inter-trial
gap); `exp2` omits the phantom `x2`/`x3` columns exactly as `simulate2.py` does.

## Citation
Binz, M., Gershman, S. J., Schulz, E., & Endres, D. (2022). Heuristics from bounded meta-learned inference. Psychological Review, 129(5), 1042-1077.

## Experiment summary
Four experiments use a cued two-alternative forced-choice inference task: on each task participants repeatedly compare two options described by a set of features (cues), predict which option contains the target, and receive feedback, learning the cue-target association over 10 evidence steps within each task. The experiments vary the number of features and their validity/correlation structure: Exp 1 (N=28) and Exp 2 (N=24) use ranking-as-attribute and direction-of-preference contexts, Exp 3 (N=27) uses 2 features, and Exp 3b (N=23) uses 4 features. Response type is a binary choice per step; `time` holds the cumulative session time. The research question is whether simple decision-making heuristics emerge from a bounded meta-learned inference (metalearned RL) model rather than from unbounded rational inference; a bounded meta-RL model was fit to the behavioral data (cognitive-modeling paper).

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (0..27), as string |
| task_id | Task id, 0..29; each task is a fresh paired-comparison inference problem (own cue-target weights) |
| trial | 0..9 within each (participant_id, task_id); sequential evidence step within a task |
| response | Participant binary choice, 0/1, same option coding as `target` |
| target | Correct answer, 0/1; 1 = option A (the minuend of the `x` differences) is the better option (source coding, see Notes) |
| correct | 1 if response == target, else 0 |
| x0 | Difference in feature 0, option A minus option B |
| x1 | Difference in feature 1, option A minus option B |
| x2 | Difference in feature 2, option A minus option B |
| x3 | Difference in feature 3, option A minus option B |
| time | Total time passed since the start of the session, in milliseconds (source: "total time passed"; increases monotonically across tasks within a participant) |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (0..23), as string |
| task_id | Task id, 0..29; each task is a fresh paired-comparison inference problem (own cue-target weights) |
| trial | 0..9 within each (participant_id, task_id); sequential evidence step within a task |
| response | Participant binary choice, 0/1, same option coding as `target` |
| target | Correct answer, 0/1; 1 = option B (the subtrahend of the `x` differences) is the better option: the source generator flips the target in the direction condition (see Notes) |
| correct | 1 if response == target, else 0 |
| x0 | Difference in feature 0, option A minus option B |
| x1 | Difference in feature 1, option A minus option B |
| x2 | Difference in feature 2, option A minus option B |
| x3 | Difference in feature 3, option A minus option B |
| time | Total time passed since the start of the session, in milliseconds (source: "total time passed"; increases monotonically across tasks within a participant) |

#### exp2
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (0..26), as string |
| task_id | Task id, 0..29; each task is a fresh paired-comparison inference problem (own cue-target weights) |
| trial | 0..9 within each (participant_id, task_id); sequential evidence step within a task |
| response | Participant binary choice, 0/1, same option coding as `target` |
| target | Correct answer, 0/1; 1 = option A (the minuend of the `x` differences) is the better option (source coding, see Notes) |
| correct | 1 if response == target, else 0 |
| x0 | Difference in feature 0, option A minus option B |
| x1 | Difference in feature 1, option A minus option B |
| time | Total time passed since the start of the session, in milliseconds (source: "total time passed"; increases monotonically across tasks within a participant) |

#### exp3
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (0..22), as string |
| task_id | Task id, 0..29; each task is a fresh paired-comparison inference problem (own cue-target weights) |
| trial | 0..9 within each (participant_id, task_id); sequential evidence step within a task |
| response | Participant binary choice, 0/1, same option coding as `target` |
| target | Correct answer, 0/1; 1 = option A (the minuend of the `x` differences) is the better option (source coding, see Notes) |
| correct | 1 if response == target, else 0 |
| x0 | Difference in feature 0, option A minus option B |
| x1 | Difference in feature 1, option A minus option B |
| x2 | Difference in feature 2, option A minus option B |
| x3 | Difference in feature 3, option A minus option B |
| time | Total time passed since the start of the session, in milliseconds (source: "total time passed"; increases monotonically across tasks within a participant) |

Exp file to paper-experiment mapping (from the source repo README): exp0 = Exp 1 (ranking), exp1 = Exp 2 (direction), exp2 = Exp 3 (2 features), exp3 = Exp 3b (4 features). All rows are retained, with one row per evidence step per participant per task. exp2.csv carries only `x0`/`x1`: the source's `exp4.csv` has `x2`/`x3` columns, but its export code (`eval.ipynb`) never writes them for the 2-feature condition, so they hold uninitialized memory and `transform.py` drops them. Option coding of `response`/`target` follows the source generator (`environments.py`): 1 = option A (the minuend of the `x` differences) is the better option in exp0, exp2 and exp3; in exp1 the generator flips the target, so 1 = option B. Verified in the data: in exp1 `target`=1 goes with negative summed differences (all weights positive), in exp2 with the ground-truth weights stored in the source's `humans_2features.pth`. The source's PyTorch files were not transformed. `humans_2features.pth` (Exp 3) also stores the three binary end-of-task judgments per task (direction of each attribute, which attribute matters more; paper pp. 47, 50) that the source CSV omits, so exp2.csv does not contain them; `judgements.pth` is derived from those by the source's `eval.ipynb` (participant, ideal-observer and BMI judgments).

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: guessing, ideal observer, equal weighting, single cue (sequential variational probit regression, per-participant MLE of sigma over [0.01,10], BIC-based model evidence per Eq. 27).
Reproduced: single_cue_dominant_exp1, equal_weighting_dominant_exp2.
Not reproduced: none.
Numeric mismatch: none on the verification re-run (2026-09-09: single-cue winners 23/28 and equal-weighting winners 24/24, as reported); the original run gave 24/28 for Exp 1, a platform-dependent residual of the sigma grid and fixed-iteration variational inference.
Partial validation: none.
Indeterminate: none. The paper's aggregate BMI (neural meta-RL) and feedforward-network comparisons were not modeled (neural-network models are out of scope); the two heuristic claims do not depend on them.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-20

## Text-format conversion
All four experiments were transcribed (exp0-exp3). They share the alien-sports paired-comparison paradigm but differ in prior-knowledge instruction and feature count, so each got its own narrator: exp0 (known ranking, 4 features), exp1 (known direction, 4 features), exp2 (unknown, 2 features), exp3 (unknown, 4 features). None skipped. The `xN` columns hold the attribute difference (Alien 1 minus Alien 2); the response is the chosen alien and `target` is the winner, narrated with the source's option coding (1 = Alien 1 in exp0/exp2/exp3, 1 = Alien 2 in exp1; see Notes). Per-participant letter mapping is randomized.

Sample transcript (exp0, participant 0, up to the first response):
```
You are watching an alien sports competition on an unknown planet. Each round of the competition pits two aliens, Alien 1 and Alien 2, against each other. The two aliens are described by numerical attributes. Your task is to predict, for each round, which alien is more likely to win. After you decide, you are told the correct choice.
On each trial you see the difference between the two aliens' attributes, listed as Alien 1 minus Alien 2. The attributes are listed in order from the one that predicts the winner best to the one that predicts it worst; the first attribute is the most predictive and the last is the least predictive. To choose, press B for Alien 1 or A for Alien 2.
Round 1: attribute differences (Alien 1 minus Alien 2): -0.82, +0.30, -0.53, -0.32. You press [HUMAN_RESPONSE]B[/HUMAN_RESPONSE]
 …
```
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-20

## Simulators

All four experiments got a text simulator (`simulate0.py`-`simulate3.py`), and each passed the round-trip check through `build_jsonl.py` byte-for-byte. None skipped. The task generator follows the paper's "Environments" section and the reference `environments.py` (weights, LKJ(η=2) feature covariance, probit winner draw with σ=0.1; target flipped for the direction condition, ranking realized by sorting weights by |w|). Notable assumptions: `exp2` has only `x0`/`x1` (the source's uninitialized `x2`/`x3` are dropped by `transform.py`); each participant sees the same 30-task pool in a fresh random order.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-20

## Verification

Verdict: needs-review (critical 0, major 5, minor 5; fixed 8, open 2).

Checked: paper (doi:10.1037/rev0000330; preprint PDF from osf.io/5du2b), original data (https://github.com/marcelbinz/HeuristicsFromBMLI, commit 7fedc7e), exp0-exp3, transform re-run, transcripts, simulators, modeling, analysis, logs. Skipped: none.

Fixed:
- exp2.csv carried x2/x3 with values up to 8e62: the source's eval.ipynb allocates the export array with np.empty and never writes those columns for the 2-feature condition (paper p. 47: two features). transform.py now drops them; exp2.csv regenerated (8100 rows, x0/x1 only); README exp2 table, Notes and Simulators note updated; simulate2.py docstring updated.
- The transcripts narrated target/response 1 as 'Alien 2' in every experiment, but the source generator (environments.py) codes 1 = option A (the minuend of x = A - B) and flips only the direction condition. Verified in the data: exp1 P(target=1 | sum x > 0) = 0.18; exp2 P(target=1 | w.x > 0) = 0.95 with the weights stored in the source's humans_2features.pth. build_jsonl.py now names the options per experiment (exp1 unchanged), simulate0/2/3.py narrate the same way, transcripts0/2/3.jsonl were rebuilt; the simulator round trip is byte-identical for all four experiments; the README sample transcript and the response/target/x column descriptions document the coding.
- README described `time` as cumulative within a task; it is cumulative over the session (monotone across all 30 tasks of every participant, first row about 250 s in; source README: 'total time passed'). All four tables and the summary sentence ('with reaction times') corrected.
- README called the source's judgements.pth 'model cognitive judgments, not human trial-level data'; the source's eval.ipynb derives it from the human end-of-task judgments stored in humans_2features.pth. The Notes now describe both files.
- logs/auto-exp-sim.sessions.json, logs/auto-exp-transcribe.sessions.json, transcripts/auto-exp-sim.log and transcripts/auto-exp-transcribe.log were exports of 2026-08-24 re-runs that exited with 'already processed' (the sim export also embedded a diff of castrorodrigues_2022_explicit); the four files were deleted.
- '## Modeling reproduction', '## Text-format conversion' and '## Simulators' ended without a Run line; added 'Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-20' from the top provenance bullet and the HF commit dates of those files.
- Column headings '### expN' changed to the template's '#### expN'.
- The modeling section reported a numeric mismatch (24/28 single-cue winners vs the paper's 23/28); this run of model.py gives 23/28 and 24/24, matching the paper (pp. 39, 44); the note now says so.

Open:
- major: the paper (pp. 47, 50) collects three binary end-of-task judgments per task in Exp 3 (is a positive value of each attribute advantageous; which attribute matters more). The source stores them in humans_2features.pth (direction1, direction2, ranking; 27 x 30 each), but exp2.csv, built from the source's exp4.csv, does not contain them. Adding them needs a PyTorch reader in transform.py and a judgment phase in build_jsonl.py and simulate2.py; left for the maintainer.
- minor: the exp2/exp3 instruction line carries a double space before 'To choose' (empty cover sentence in build_jsonl.py); left as is to keep the transcripts and simulators byte-identical.

Run: claude-fable-5-1, 2026-09-09
