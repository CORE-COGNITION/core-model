---
tags:
- paradigm:risky-choice
- cognitive-modeling:pass
- psych-201
- text-format:pass
- js-experiment:needs-review
- simulator:pass
---
# pike_2023_catastrophizing

- Paper: https://doi.org/10.5334/cpsy.91
- Data source: https://doi.org/10.17605/OSF.IO/Z2RGK
- PDF: https://cpsyjournal.org/articles/91/files/submission/proof/91-1-1170-1-10-20230117.pdf
- Full text: https://doi.org/10.5334/cpsy.91
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Pike, A. C., Alves Anet, A., Peleg, N., & Robinson, O. J. (2023). Catastrophizing and Risk-Taking. Computational Psychiatry, 7(1), 1-13. https://doi.org/10.5334/cpsy.91

## Experiment summary
Two online Balloon Analogue Risk Task (BART) studies examined the relationship between catastrophizing (a tendency to overestimate threat and negative outcomes) and risk-taking under high versus low burst cost. The pilot study (exp0, N=69) combined BART with a separate cards estimation task; the main study (exp1, N=265) ran BART alone. In BART each balloon trial records the number of pumps (0..20) chosen and whether the balloon burst, with the cost of an explosion manipulated between a high-cost block (large penalty) and a low-cost block (no penalty beyond lost balloon points). Participants also completed questionnaires capturing catastrophizing, anxiety (STAI, GAD-7), depression (PHQ-8), and worry (PSWQ). The data support computational cognitive modeling (PAR4, prospect theory, and EWMV models are fit to BART choices), and the primary effects — the cost manipulation on pumping, catastrophizing risk-taking correlations, and their interaction — all reproduce conceptually.

## Text-format conversion

Both experiments were transcribed to natural language. exp0 (pilot, 69 participants) covers the BART task (task_id 0, 60 balloons: 30 high-cost + 30 low-cost) followed by the cards estimation task (task_id 1, 5 blocks of 4 estimation responses); exp1 (main, 265 participants) covers the BART task alone. In the BART, the free response is the number of pumps (whole number 0–20); in the cards task, free responses are the points estimates (-600..600) and confidence ratings (0–100). All responses were free (no forced-choice trials), and every row of every participant was transcribed, including participants who completed only one block and the partial high-cost block of participant 173.

Sample transcript (participant 1, exp0, through the first response):

```
Your aim in this task is to win points by pumping up a balloon. You may pump the balloon up as many times as you wish by pressing the 'Air' button: every pump gives you 10 more points, but it also increases the risk of the balloon bursting. The speed at which you pump does not affect the likelihood of the balloon bursting. If the balloon bursts you lose the points you have accumulated for that balloon and also lose 200 points as a penalty. You can stop pumping at any point and collect the points you have earned by pressing the 'Collect Points' button. You are shown your total points at the end of each balloon.
On each balloon, you decide how many times to pump it up before either the balloon bursts or you collect. Type the number of pumps as a whole number from 0 to 20 (each balloon starts at 0 points and each pump adds 10 points).

Block 1, high-cost block: if the balloon bursts you lose the points for that balloon and also lose 200 points as a penalty. There are 30 balloons in this block.
Balloon 1 of 30. You pump the balloon [HUMAN_RESPONSE]2[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: van Ravenzwaaij 4-parameter BART model (hBayesDM bart_par4: phi=prior belief, eta=updating rate, gam=risk-taking, tau=inverse temperature), fit per cost block per participant by multi-start bounded L-BFGS (per-participant MAP approximation of the paper's hierarchical MCMC), then Pearson correlation of the fitted gam (risk-taking) parameter with Catastrophizing scores.
Reproduced: risk_taking_main_low, risk_taking_main_high, risk_taking_pilot_low, risk_taking_pilot_high (all non-significant, matching the paper's reported null correlations).
Not reproduced: none.
Numeric mismatch: r/p values differ somewhat in magnitude from the paper's (e.g. main LC r=0.087 p=0.162 vs paper r=0.016 p=0.809; main HC r=-0.006 p=0.929 vs r=-0.037 p=0.575; pilot LC r=-0.103 p=0.401 vs r=-0.211 p=0.082; pilot HC r=-0.022 p=0.856 vs r=-0.147 p=0.227) but all are non-significant, matching the qualitative null claim.
Partial validation: omit.
Indeterminate: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Notes

### Columns

### exp0 (pilot)
| column | description |
|--------|-------------|
| participant_id | Original researcher-assigned participant number (1..69), from source id column |
| trial | 0-indexed trial number within each (participant_id, task_id) |
| response | BART: number of pumps on that balloon (integer 0..20). Cards task: points estimate (integer -600..600) or confidence rating (0..100) depending on response_type |
| explosion | BART only: 0 = balloon did not burst (participant cashed out), 1 = balloon burst |
| condition | BART block condition: "high_cost" (burst penalty in pilot = -200 pts) or "low_cost" (burst penalty = 0 pts beyond lost balloon points) |
| task | "bart" for BART balloons, "cards" for the cards estimation task |
| task_id | 0 = BART, 1 = cards; trial restarts at 0 within each (participant_id, task_id) |
| phase | "test" for BART; "block" or "end" for cards phases |
| block | BART: 0 = high_cost block, 1 = low_cost block. Cards: 0-indexed paper-trial grouping the 4 response rows per balloon |
| total_catastrophizing | Sum score on the Catastrophizing Questionnaire (range 24..120) |
| age | Participant age in years |
| Sex | "Male" or "Female" — source capitalisation preserved |
| Student.Status | "Yes" or "No" |
| prolific_score | Prolific pre-screening score (0..100) |
| total_stai | State-Trait Anxiety Inventory total score |
| total_gad7 | Generalized Anxiety Disorder 7-item scale total |
| total_phq8 | Patient Health Questionnaire-8 total (depression) |
| total_pswq | Penn State Worry Questionnaire total |
| covid_worry | COVID worry rating (0..100 scale) |
| covid_highrisk_self | Self-rated high-risk status due to COVID: "Yes", "No" |
| covid_highrisk_family | Family high-risk status: text categories |
| covid_impact | COVID impact rating (0..100) |
| covid_handwashing | Handwashing frequency rating (0..100) |
| covid_distancing | Social distancing rating (0..100) |
| employment | Employment status category |
| household_size | Household size (integer or "6+") |
| precovid_catastrophizing | Retrospective pre-COVID catastrophizing score |
| diagnosis_general | "Yes" / "No" for any diagnosis |
| diagnosis_anxdep | Anxiety/depression diagnosis category |
| medication_general | Medication status category |
| medication_anxdep | Anxiety/depression medication category |
| cards_Response_block_points | Pilot-data aggregate: mean block-points response (cards) |
| cards_Response_block_conf | Pilot-data aggregate: mean block confidence (cards) |
| cards_Response_end_points | Pilot-data aggregate: mean end-points response (cards) |
| cards_Response_end_conf | Pilot-data aggregate: mean end confidence (cards) |
| cards_Reaction.Time_block_points | Pilot-data aggregate: mean RT for block points (ms) |
| cards_Reaction.Time_block_conf | Pilot-data aggregate: mean RT for block confidence (ms) |
| cards_Reaction.Time_end_points | Pilot-data aggregate: mean RT for end points (ms) |
| cards_Reaction.Time_end_conf | Pilot-data aggregate: mean RT for end confidence (ms) |
| cards_block_delta | Pilot-data aggregate: mean block delta (cards outcome) |
| cards_end_delta | Pilot-data aggregate: mean end delta (cards outcome) |
| maths_subjective_ability | Self-rated maths ability (0..100) |
| maths_subjective_performance | Self-rated maths performance (0..100) |
| maths_subjective_difficulty | Self-rated maths difficulty (0..100) |
| maths_actual_performance | Actual maths test performance (proportion correct) |
| lc_mean_pumps | Participant's mean pumps in low-cost BART block |
| lc_bursts | Participant's total burst count in low-cost BART block |
| hc_mean_pumps | Participant's mean pumps in high-cost BART block |
| hc_bursts | Participant's total burst count in high-cost BART block |
| trial_paper | Cards only: 0-indexed paper-trial number (0..4) |
| response_type | Cards only: "points" or "confidence" — distinguishes what the response value represents |
| rt | Cards only: reaction time in milliseconds |
| reward | Cards only: outcome/delta (block_delta or end_delta) in points |

### exp1 (main study)
| column | description |
|--------|-------------|
| participant_id | Original researcher-assigned participant number (1..267), from source id column |
| trial | 0-indexed trial number within each (participant_id, task_id) |
| response | Number of pumps on that BART balloon (integer 0..20) |
| explosion | 0 = balloon did not burst (participant cashed out), 1 = balloon burst |
| condition | "high_cost" (burst penalty in main = -1000 pts) or "low_cost" (burst penalty = 0 pts beyond lost balloon points) |
| task | "bart" |
| task_id | 0 (single task, no cards in main study) |
| phase | "test" |
| block | 0 = high_cost block, 1 = low_cost block |
| total_catastrophizing | Sum score on Catastrophizing Questionnaire (24..120) |
| age | Age in years |
| Sex | "Male" or "Female" |
| Student.Status | "Yes" / "No" |
| prolific_score | Prolific pre-screening score (0..100) |
| total_stai | STAI total |
| total_gad7 | GAD-7 total |
| total_phq8 | PHQ-8 total |
| total_pswq | PSWQ total |
| covid_worry | COVID worry (0..100) |
| covid_highrisk_self | Self high-risk status |
| covid_highrisk_family | Family high-risk status |
| covid_impact | COVID impact (0..100) |
| covid_handwashing | Handwashing (0..100) |
| covid_distancing | Distancing (0..100) |
| employment | Employment category |
| household_size | Household size |
| diagnosis_general | Diagnosis status |
| diagnosis_anxdep | Anxiety/depression diagnosis |
| medication_general | Medication status |
| medication_anxdep | Anxiety/depression medication |
| lc_mean_pumps | Mean pumps in low-cost block |
| lc_bursts | Burst count in low-cost block |
| hc_mean_pumps | Mean pumps in high-cost block |
| hc_bursts | Burst count in high-cost block |
| cq1..cq24 | Individual Catastrophizing Questionnaire items (1..5 Likert) |
| stairesponse-2..stairesponse-21 | Individual STAI items (1..4 Likert) |
| gad7response-1..gad7response-7 | Individual GAD-7 items (0..3 Likert) |
| phq8response-1..phq8response-8 | Individual PHQ-8 items (0..3 Likert) |
| pswqresponse-2..pswqresponse-17 | Individual PSWQ items (1..5 Likert) |

## Online experiment

Both experiments were ported to static online jsPsych v8 tasks (`experiments/exp0/` = pilot BART + cards estimation task; `experiments/exp1/` = main-study BART). The headless `?mode=simulate` round trip passed for both (`validated: true`): exp0 reproduces the reference per-participant row counts (60 BART + 20 cards) and exp1 reproduces 60 BART rows, with the reference column names and codings. The saved CSV omits the per-participant questionnaire/demographic columns (instrument item text is not in the dataset). One data-affecting assumption is documented in `experiments/README.md`: the pilot **cards task** card values and block/end deltas are not recorded in the dataset, so they are generated (uniform in [−25, 25]) and the reward/feedback computed from them. Cosmetic defaults (balloon colours, block-transition step, feedback/ITI timings, integer `response` vs the reference's float upcast) do not change the data or task.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Both experiments got a text simulator (`simulate0.py` = pilot BART + cards estimation task; `simulate1.py` = main-study BART), and both passed the round-trip check: regenerating the transcripts from the simulated `expN.csv` via `build_jsonl.py` reproduces the simulator's prompts byte-identically (both experiments, several simulations each). The free response is the typed pump count (BART, 0..20) or the points/confidence estimate (cards). Burst points are drawn uniformly from the paper's reported per-block ranges ([1,19] for HC / main blocks, [6,18] for the pilot LC block), reshuffled per participant — an `ASSUMPTION` since the exact arrays are not in the data. The pilot cards-task card values and block/end deltas are likewise generated (uniform in [-25,25]) as in the js port.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
