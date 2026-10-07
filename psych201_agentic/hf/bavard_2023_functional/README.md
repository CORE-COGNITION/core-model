---
tags:
- paradigm:bandit
- cognitive-modeling:pass
- psych-101
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
---
# bavard_2023_functional

- Paper: https://doi.org/10.7554/eLife.83891
- Data source: https://github.com/hrl-team/3options
- PDF: https://cdn.elifesciences.org/articles/83891/elife-83891-v2.pdf
- Full text: https://doi.org/10.7554/eLife.83891
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Bavard, S., & Palminteri, S. (2023). The functional form of value normalization in human reinforcement learning. eLife, 12, e83891. https://doi.org/10.7554/eLife.83891

## Experiment summary
The paper asks how option values are normalized during human reward-based learning by comparing competing computational implementations (e.g., normalization by the sum vs. the value range of available options). Across three behavioral experiments (exp0 N=150, exp1 N=150, exp2 N=200; plus pilot 3a/3b), participants learned to choose among binary/trinary options presented in narrow vs. wide outcome ranges (learning phases with forced and free trials) and then performed a choice transfer phase with new option combinations; choices and reaction times were recorded per trial. The research question is whether divisive value normalization follows a specific functional form, addressed via formal model comparison and fitting of reinforcement-learning models. Both headline effects (anti-divisive set-size effect; wider outcome range boosting high-value transfer-choice rate) reproduced on exp0.

## Notes

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | Anonymous participant code (source COLUMN 14), str |
| participant_number | Sequential subject number from source COLUMN 1 (1..150) |
| participant_code | Same value as participant_id, kept as source COLUMN 14 (raw) |
| task_id | 0-indexed task reset = phase number (0 training, 1 learning, 2 transfer); trial restarts here |
| phase | Phase label derived from phase_code (training / learning / transfer) |
| phase_code | Raw source COLUMN 2: 0 training, 1 learning, 2 transfer |
| trial | 0..N within each (participant_id, task_id), re-derived contiguous |
| trial_raw | Source COLUMN 3 trial counter as recorded |
| condition_code | Source COLUMN 4: signed context; sign<0 => forced choice, magnitude = context, 0 = transfer |
| context | Context number = abs(condition_code); 1 WT(86/50/14), 2 WB(86/-/14), 3 NT(50/32/14), 4 NB(50/-/14); 0 in transfer |
| forced_choice | 1 if trial choice was experimenter-forced (condition_code<0), else 0 |
| left_option | Source COLUMN 5, option identity shown on the left (0 = none presented) |
| middle_option | Source COLUMN 6, option identity shown in the middle (0 = none) |
| right_option | Source COLUMN 7, option identity shown on the right (0 = none) |
| choice_set | JSON [left, middle, right] of the three presented options |
| response | Choice, 0-indexed left=0 / middle=1 / right=2 (source COLUMN 8 was -1/0/1) |
| correct | 1 if choice was correct (optimal option), else 0 (source COLUMN 9) |
| choice_accuracy | Raw source COLUMN 9 accuracy (kept verbatim) |
| outcome_chosen | Source COLUMN 10, delivered outcome of the chosen option (NaN in transfer) |
| outcome_unchosen1 | Source COLUMN 11, outcome of first unchosen option (NaN in transfer) |
| outcome_unchosen2 | Source COLUMN 12, outcome of second unchosen option (NaN in transfer) |
| reward | Delivered payoff = outcome_chosen (NaN in transfer) |
| rt | Reaction time in milliseconds (source COLUMN 13), NaN in transfer |
| rt_raw | Raw source COLUMN 13 reaction time (kept verbatim) |
| version | Source COLUMN 15, per-participant task-version/counterbalance code (1/2/3) used for forced-choice pairing |
| exp_code | Source COLUMN 16, constant experiment-level code (2 in exp0) |

### exp1
| column | description |
|--------|-------------|
| participant_id | Anonymous participant code (source COLUMN 14), str |
| participant_number | Sequential subject number from source COLUMN 1 (1..150) |
| participant_code | Same value as participant_id, kept as source COLUMN 14 (raw) |
| task_id | 0-indexed task reset = phase number (0 training, 1 learning, 2 transfer); trial restarts here |
| phase | Phase label derived from phase_code (training / learning / transfer) |
| phase_code | Raw source COLUMN 2: 0 training, 1 learning, 2 transfer |
| trial | 0..N within each (participant_id, task_id), re-derived contiguous |
| trial_raw | Source COLUMN 3 trial counter as recorded |
| condition_code | Source COLUMN 4: signed context; sign<0 => forced choice, magnitude = context, 0 = transfer |
| context | Context number = abs(condition_code); 1 WT(86/50/14), 2 WB(86/-/14), 3 NT(86/68/50), 4 NB(86/-/50); 0 in transfer |
| forced_choice | 1 if trial choice was experimenter-forced (condition_code<0), else 0 |
| left_option | Source COLUMN 5, option identity shown on the left (0 = none presented) |
| middle_option | Source COLUMN 6, option identity shown in the middle (0 = none) |
| right_option | Source COLUMN 7, option identity shown on the right (0 = none) |
| choice_set | JSON [left, middle, right] of the three presented options |
| response | Choice, 0-indexed left=0 / middle=1 / right=2 (source COLUMN 8 was -1/0/1) |
| correct | 1 if choice was correct (optimal option), else 0 (source COLUMN 9) |
| choice_accuracy | Raw source COLUMN 9 accuracy (kept verbatim) |
| outcome_chosen | Source COLUMN 10, delivered outcome of the chosen option (NaN in transfer) |
| outcome_unchosen1 | Source COLUMN 11, outcome of first unchosen option (NaN in transfer) |
| outcome_unchosen2 | Source COLUMN 12, outcome of second unchosen option (NaN in transfer) |
| reward | Delivered payoff = outcome_chosen (NaN in transfer) |
| rt | Reaction time in milliseconds (source COLUMN 13), NaN in transfer |
| rt_raw | Raw source COLUMN 13 reaction time (kept verbatim) |
| version | Source COLUMN 15, per-participant task-version/counterbalance code (1/2/3) used for forced-choice pairing |
| exp_code | Source COLUMN 16, constant experiment-level code (1 in exp1) |

### exp2
| column | description |
|--------|-------------|
| participant_id | Anonymous participant code (source COLUMN 14), str |
| participant_number | Sequential subject number from source COLUMN 1 (1..200) |
| participant_code | Same value as participant_id, kept as source COLUMN 14 (raw) |
| task_id | 0-indexed task reset = phase number (0 training, 1 learning, 2 transfer); trial restarts here |
| phase | Phase label derived from phase_code (training / learning / transfer) |
| phase_code | Raw source COLUMN 2: 0 training, 1 learning, 2 transfer |
| trial | 0..N within each (participant_id, task_id), re-derived contiguous |
| trial_raw | Source COLUMN 3 trial counter as recorded |
| condition_code | Source COLUMN 4: signed context; sign<0 => forced choice, magnitude = context, 0 = transfer |
| context | Context number = abs(condition_code); both 1 and 2 = WT(86/50/14), both 3 and 4 = NT(50/32/14); 0 in transfer |
| forced_choice | 1 if trial choice was experimenter-forced (condition_code<0), else 0 |
| left_option | Source COLUMN 5, option identity shown on the left (0 = none presented) |
| middle_option | Source COLUMN 6, option identity shown in the middle (0 = none) |
| right_option | Source COLUMN 7, option identity shown on the right (0 = none) |
| choice_set | JSON [left, middle, right] of the three presented options |
| response | Choice, 0-indexed left=0 / middle=1 / right=2 (source COLUMN 8 was -1/0/1) |
| correct | 1 if choice was correct (optimal option), else 0 (source COLUMN 9) |
| choice_accuracy | Raw source COLUMN 9 accuracy (kept verbatim) |
| outcome_chosen | Source COLUMN 10, delivered outcome of the chosen option (NaN in transfer) |
| outcome_unchosen1 | Source COLUMN 11, outcome of first unchosen option (NaN in transfer) |
| outcome_unchosen2 | Source COLUMN 12, outcome of second unchosen option (NaN in transfer) |
| reward | Delivered payoff = outcome_chosen (NaN in transfer) |
| rt | Reaction time in milliseconds (source COLUMN 13), NaN in transfer |
| rt_raw | Raw source COLUMN 13 reaction time (kept verbatim) |

exp0, exp1, exp2 correspond to the paper's Experiments 1, 2, and 3 respectively. Separate explicit-rating files (`data_expeN_explicit.csv`) record a post-task option-value rating phase with a different participant indexing and were not merged into these choice files; only the main choice data matrix per experiment is used here. In transfer-phase trials there is no delivered outcome, so `reward`/`rt` are NaN.

## Text-format conversion

exp0, exp1, and exp2 (Experiments 1, 2, and 3) are all transcribed. Each is the same probabilistic instrumental-learning (multi-armed bandit) paradigm — participants choose among two or three abstract cues, each linked to a hidden point value, learn from the point outcome they receive, and later complete a transfer phase in which pairs of cues are shown and they indicate the higher-value one. This is textifiable because the reward feedback, not the cue's perceptual identity, drives learning; the abstract cues are referred to by a stable number. Per the paper, no outcome is shown during the transfer (elicitation) phase, so no reward is narrated there even though the CSV records the (never-displayed) option outcomes. No experiment skipped.

Sample transcript (start to first response):
```
You are playing a points game. On each trial, two or three abstract symbols (each referred to here by a number) appear on screen, arranged left, middle, and right. Each symbol is secretly linked to a number of points (0-100). You choose a symbol by clicking it; after your choice, you see the points that symbol awarded you. Try to earn as many points as possible. You first complete a short training session to learn the response controls, then the main learning phase, and finally a transfer phase in which pairs of symbols are shown and you indicate which one you think has the higher value. To answer on every trial, type the number of the symbol you choose.
Training session:
Symbols shown: 2, 1, 3. You press [HUMAN_RESPONSE]2[/HUMAN_RESPONSE] ...
```
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

simulate0.py, simulate1.py, and simulate2.py generate full participant sessions for Experiments 1, 2, and 3 (exp0, exp1, exp2) in the exact wording of the transcripts; the round-trip check (simulated DataFrame through `build_jsonl.py` → transcript text) passes for all three. Options, positions, and trial order are randomized per participant; forced-choice trials and exp2's availability trials ("You are told to choose symbol X.") are narrated plainly. Design notes / ASSUMPTIONs are in each simulator's class docstring; shared: outcome = round(N(option value, 4)) clipped to [1, 100]; version (exp0/exp1), exp2 availability probability (50% vs 75% per participant) drawn uniform-random. `rt`/`rt_raw` are not simulated.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: UNBIASED (Q-learning), DIVISIVE, RANGE, RANGE(omega) on exp0/exp1; UNBIASED, RANGE, RANGE(omega), RANGE(omega+) on exp2. Metric: per-participant out-of-sample log-likelihood of transfer choices (params fit on learning phase), t-tests on paired oosLL.
Reproduced: range_wins_exp1, range_omega_wins_exp1, omega_gt_1_exp1, range_omega_plus_wins_exp3, omega_c_lt_omega_u_exp3.
Not reproduced: none.
Numeric mismatch: none (exp0 oosLL means UNBIASED -278.4, DIVISIVE -143.2, RANGE -116.6, RANGE(omega) -97.5 vs paper Table 2: -275.3, -143.4, -116.7, -97.7).
Partial validation: omit.
Indeterminate: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Online experiment

Static jsPsych v8 online versions of all three experiments are under
`experiments/exp0/`, `experiments/exp1/`, `experiments/exp2/` (no backend; the
session CSV is offered as a download via the `saveData` seam). The headless
round trip (Chromium + Playwright, `?mode=simulate`) passed for all three: each
produces a CSV matching its `expN.csv` schema (same column names, 0-indexed
counters and response coding, and per-design row counts: exp0 12/230/180, exp1
12/180/180, exp2 6/180/132 per participant for training/learning/transfer). No
experiment skipped. Cosmetic defaults recorded as `ASSUMPTION:` in each file:
the response window is self-paced, a 500 ms choice-outcome delay and a 1000 ms
outcome display (paper Methods), forced trials (exp0/exp1 versions 2/3) and
availability trials (exp2 contexts 2/4) shown with the unavailable cue(s)
shaded, and the abstract cues rendered as numbered buttons (the source refers
to each cue by a number). In simulate mode, `rt` is drawn as a placeholder;
a live run records the real reaction time.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
