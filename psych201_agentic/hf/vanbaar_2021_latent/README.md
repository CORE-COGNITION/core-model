---
tags:
- paradigm:economic-game
- cognitive-modeling:pass
- psych-201
- text-format:pass
- js-experiment:needs-review
- simulator:pass
---

# vanbaar_2021_latent

- Paper: https://doi.org/10.1038/s41562-021-01207-4
- Data source: https://github.com/jeroenvanbaar/NHB_motives_structure
- Full text: https://www.nature.com/articles/s41562-021-01207-4
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
van Baar, J. M., Nassar, M. R., Deng, W., & FeldmanHall, O. (2021). Latent motives guide structure learning during adaptive social choice. Nature Human Behaviour, 6(3), 404-414. https://doi.org/10.1038/s41562-021-01207-4

## Experiment summary
Across 4 experiments (N=501 MTurk participants), participants predicted a simulated player's choices in repeated economic games (Prisoner's Dilemma, Stag Hunt, and related games) that differed in social tension, giving a predicted choice and a confidence rating on each trial. The key manipulation was the latent motivational structure underlying each player's actions (e.g. optimal vs pessimistic motives) and the introduction of new/context-shifting player types. Results show people learn the stable motivational structure behind changing actions and generalize this learned structure to novel players and contexts. exp0 (N=150), exp1 (eye-tracking replication, N=50), and exp2 (new player types, N=153) are the prediction game experiment; exp3 (N=153) comprises an inference game with both a sequential-prediction task (SPG) and a work-for-inspection (WS) task. The paper additionally fits a FeatureRL (feature-based reinforcement-learning) computational model to the trial-level choice data.

## Notes

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | P000.. remapped from source `subID` (Study1 MTurk subject number, 2003 etc.) in first-appearance order |
| trial | 0..15 within each (participant_id, task_id); source `Trial` (prediction trials per block) |
| task_id | 0..3, source `Block`; each block presents a new simulated player whose latent motive must be learned |
| response | 0/1: participant's predicted choice of the other player (0=defect, 1=cooperate); from source `GivenAns` |
| given_ans | raw source coding of the participant's prediction (`def`/`coop`) |
| corr_ans | raw source coding of the other player's actual/ground-truth choice (`def`/`coop`) |
| correct | 0/1 whether given_ans == corr_ans (prediction match) |
| player | which simulated opponent the participant sees this block (G.P., D.T., F.A., E.B.) |
| type | latent-motive type label of opponent (`opt`/`pess`) |
| variant | variant label (`nat`/`inv`) |
| type_total | combined type+variant token (e.g. `opt_nat`) |
| s | row index of the payoff matrix cell in the game (0/3/7/10) |
| t | column index of the payoff matrix cell in the game (5/8/12/15) |
| game_type | economic game this trial (PD/HG/SH/SG) |
| colors | JSON list of the two response-button colors offered on the trial |
| confidence | participant's confidence rating in their prediction, 10..100 |
| score | 0/1 whether the participant got this trial's points |
| rt_radio | reaction time (ms) to select the radio response |
| rt_submit | reaction time (ms) to submit the response |
| self_report | free-text strategy self-report (per session/participant) |

### exp1
| column | description |
|--------|-------------|
| participant_id | P000.. remapped from source `subID` (Study2 subject number, 5005 etc.) |
| trial | 0..15 within each (participant_id, task_id); source `Trial` |
| task_id | 0..7, source `Block`; each block = a latency-to-observe/player context |
| response | 0/1: participant's predicted choice (0=defect, 1=cooperate); from `GivenAns` |
| given_ans | raw source prediction code (`def`/`coop`) |
| corr_ans | raw source ground-truth code (`def`/`coop`) |
| correct | 0/1 whether given_ans == corr_ans |
| player | opponent label (all N.N. in Study2) |
| type | latent-motive type (`opt`/`pes`) |
| variant | variant label (`nat`/`inv`/`_nat`/`_inv`) |
| type_total | combined type+variant token |
| s | payoff-matrix row index |
| t | payoff-matrix column index |
| game_type | economic game this trial (PD/HG/SH/SG) |
| colors | JSON list of the two response-button colors |
| confidence | confidence rating in the prediction, 0..100 |
| score | 0/1 whether the participant got this trial's points |
| rt_radio | reaction time (ms) to select the radio response |
| rt_submit | reaction time (ms) to submit |
| self_report | strategy self-report (all "not defined" in Study2) |

### exp2
| column | description |
|--------|-------------|
| participant_id | P000.. remapped from source `subID` (Study3 subject number, 6001 etc.); source `worker`/`assignment` MTurk IDs dropped as PII |
| trial | 0..15 within each (participant_id, task_id); source `Trial` |
| task_id | 0..3, source `Block`; each block = a new/context-shifting player type |
| response | 0/1: participant's predicted choice (0=defect, 1=cooperate); from `GivenAns` |
| given_ans | raw source prediction code (`def`/`coop`) |
| corr_ans | raw source ground-truth code (`def`/`coop`) |
| correct | 0/1 whether given_ans == corr_ans |
| player | opponent label (all n.a. in Study3) |
| type | latent-motive type (`env`/`opt`/`pess`/`trust`) |
| variant | variant label (all `nat` in Study3) |
| type_total | combined type+variant token |
| s | payoff-matrix row index |
| t | payoff-matrix column index |
| game_type | economic game this trial (PD/HG/SH/SG) |
| colors | JSON list of response-button colors (all "n.a." in Study3) |
| confidence | confidence rating in the prediction, 10..100 |
| score | 0/1 whether the participant got this trial's points |
| score_cumul_block | cumulative block score (points accumulated across the block) |
| rt_radio | reaction time (ms) to select the radio response |
| rt_submit | reaction time (ms) to submit |
| self_report | strategy self-report (all n.a. in Study3) |

### exp3
| column | description |
|--------|-------------|
| participant_id | P000.. remapped from source `subID` (Study4 subject number, 2001 etc.); both tasks share the same participant set |
| task_id | 0 = Sequential Prediction Game (SPG), 1 = Work-for-Inspection (WS); two tasks within Study4 merged into one file |
| trial | 0..N within each (participant_id, task_id); source per-task trial counter (SPG 0..31, WS 0..29), presentation order |
| block | 0..1, task phase within each task (source `block`) |
| response | 0/1: SPG = predicted choice (0=defect, 1=cooperate from `choice`); WS = inspect choice (source `choice_num`, 0=not inspect, 1=inspect) |
| choice | raw source choice string: SPG `coop`/`def`; WS `inspect`/`not inspect` |
| choice_num | WS-only numeric choice code (0/1) |
| correct | 0/1 whether response matched ground truth (SPG only) |
| s | SPG payoff-matrix row index |
| t | SPG payoff-matrix column index |
| game_type | SPG ground-truth game this trial (PD/HG/SH/SG); source `gt` |
| player_type | motive type of opponent / worker (`pess`/`opt`) |
| confidence | SPG confidence (`%` string); WS work_confidence is separate column |
| work_confidence | WS-only confidence rating (0..100) for the inspection decision |
| cost | WS-only cost of inspecting (points/dollars) |
| pay_inspect | WS-only payoff if inspecting |
| score | points received that trial (SPG 0/1; WS cumulative point value) |
| score_cumul | SPG-only cumulative score across trials |
| rt_radio | SPG reaction time (ms) selecting the response |
| rt_submit | SPG reaction time (ms) to submit |
| self_report | SPG free-text strategy self-report |
| batch | data-collection batch (batch1..batch8) |
| mode | run mode (all "live") |
| psiturk_status | psiTurk status code (3/4/6) |
| data_status | data status (all "complete") |
| bonus | monetary bonus paid to the participant |

Data are the four studies from the authors' public GitHub repository. `exp0`/`exp1`/`exp2` map to the paper's prediction-game studies (Study 1 MTurk, Study 2 eye-tracking, Study 3 new player types); `exp3` maps to Study 4 (inspection game), which combines the sequential-prediction game (task_id=0) and work-for-inspection task (task_id=1) for the same participants. MTurk worker/assignment IDs were dropped as PII and `participant_id` was re-coded as P000.. in first-appearance order.

## Text-format conversion

All four experiments were transcribed (`transcripts0..3.jsonl`). `exp0`-`exp2` and the `exp3` sequential-prediction game share the Social Prediction Game design (predict cooperation/defection across four economic games and rate confidence); `exp3` also includes the work-for-inspection task (decide whether to pay a cost to inspect a worker). No experiment was skipped; all involve choice/prediction decisions that a text version preserves.

Sample transcript (exp0, participant P000, start):

```
You will play a series of economic games against other players. Each player has a hidden, stable motive that drives their choices across all the games you play against them. On each trial you are shown one of four games - Prisoner's Dilemma, Harmony Game, Stag Hunt, or Snowdrift - and you must predict whether the other player will cooperate or defect, then rate your confidence as a number from 10 to 100. Type coop to predict the other player will cooperate, or def to predict they will defect, then type your confidence as a number. You earn a point for each correct prediction.
You see a Prisoner's Dilemma. You predict [HUMAN_RESPONSE]def[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: FeatureRL (van Baar et al. 2021, Fig. 3) with motive basis (Coop, Greed, Risk, Nash), game-type basis (Coop, Harmony, StagHunt, Snowdrift, Prisoners), and S/T-cell one-hot basis; per-participant joint choice+confidence SSE fits; comparison on the paper's joint-normal BIC (lower better).
Reproduced: motive_features_best_fit (motive-based FeatureRL beats game-feature models on BIC).
Not reproduced: none.
Numeric mismatch: mean BIC all_motives 23.72 [paper 23.72], game_types 29.71 [29.72], games 79.52 [79.16]; per-subject BIC matches the paper's published fits to <0.1.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment
This repo has no text simulator, so the four experiments were built directly from the data and the authors' analysis/modeling code (the paper is paywalled). `experiments/exp0/..exp3/` are static jsPsych v8 ports: exp0 (Study 1), exp1 (Study 2), exp2 (Study 3) are the Social Prediction Game, and exp3 (Study 4) adds the Work-for-Inspection task. Each builds a session CSV in the expN.csv schema; see `experiments/README.md`. The headless `?mode=simulate` round trip passed for all four (columns exactly match, no outbound POSTs).

ASSUMPTIONS surfaced (do not change the recorded data or task): (1) the on-screen payoff-matrix orientation (You rows × Other columns) is reconstructed from the authors' basis functions — the four payoff numbers (10, s, t, 5) and every (s,t)→game_type assignment are verbatim from the data; (2) exp3's Work-for-Inspection `cost` values are drawn uniformly 0..30 per trial since the paper's exact per-trial schedule is not recoverable from the CSV; (3) exp3 SPG `correct` is emitted as 0 on every row (verbatim to the dataset); (4) confidence ranges follow each experiment's recorded data (exp1 is 0-100; the shared transcript text says "10 to 100"); (5) button colors/sliders/feedback timings are cosmetic defaults.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

All four experiments got a text simulator (`simulate0.py`..`simulate3.py`); the round-trip check against `build_jsonl.py` passed byte-identically for every experiment (uniform-random agent, 3 participants each). No experiment was skipped. Simulators recover the generative structure from the data (the paper is paywalled): each block presents the 16 payoff-matrix cells once; the opponent's ground-truth move is deterministic given the latent-motive type (Study 3 `env` cooperates iff the participant's payoff s exceeds the opponent's t; `trust` always cooperates; note the Study 1/2 `opt` and `pess` types are observationally identical in the shipped data). Notable assumptions: exp0's player-name/motive pairing is a per-participant random bijection; exp3 WS `cost`/`pay_inspect` are drawn uniformly 0..30 (per-trial/block schedule not recoverable); exp3 SPG `correct` is forced to 0 verbatim to the dataset, so the narrated SPG outcome is always "Incorrect."; exp3 WS payoffs follow the data rule (pess worker trusts→40 / inspects→40-cost; opt worker trusts→0 / inspects→30-cost).
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
