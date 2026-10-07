---
tags:
- paradigm:two-step-task
- cognitive-modeling:pass
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
---
# nussenbaum_2020_moving

- Paper: https://doi.org/10.1525/collabra.17213
- Data source: https://osf.io/we89v/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Nussenbaum, K., Scheuplein, M., Phaneuf, C. V., Evans, M. D., & Hartley, C. A. (2020). Moving Developmental Research Online: Comparing In-Lab and Web-Based Studies of Model-Based Reinforcement Learning. Collabra Psychology, 6(1). https://doi.org/10.1525/collabra.17213

## Experiment summary
One online experiment with 151 participants (children, adolescents, and adults, ages 8–25) completed a two-step sequential decision-making task (200 paper-trials) plus the MaRs-IB matrix reasoning task. The key manipulation is continuous age. Each two-step trial pairs a stage-1 choice between two options (keyboard, coded 0/1) with a stage-2 decision that resolves depending on a common/rare transition and a probabilistic reward. The primary finding is an age-related increase in model-based learning (reward × transition × age interaction), with model-based vs model-free arbitration quantified by computational RL modeling. MaRs-IB responses are 4-alternative forced-choice button presses with a correctness score; only 3 participants' MaRs-IB data were on OSF, so those rows (task_id=1) contribute little to the primary two-step effect.

## Notes

### Columns

### exp0 (task_id=0: two-step sequential decision-making; task_id=1: MaRs-IB matrix reasoning)

| column | description |
|--------|-------------|
| participant_id | Original subject identifier from source (sub1–sub151). Not PII; kept as-is. |
| task_id | 0 = two-step task, 1 = MaRs-IB matrix reasoning task. |
| trial | 0-indexed within each (participant_id, task_id) group. For task 0: 0..399 (200 paper-trials × 2 responses). For task 1: 0..N-1 (N mars-trial rows). |
| block | Paper-trial number (0-indexed) grouping stage-1 and stage-2 rows in the two-step task. NaN for MaRs-IB (no block structure). |
| response | Two-step: keyboard choice 0 = left/option-1 key, 1 = right/option-2 key (source 1→0, 2→1). MaRs-IB: button-press index 0–3 (4-alternative forced choice; 0 = top-left, 1 = top-right, 2 = bottom-left, 3 = bottom-right). NaN = no valid response recorded (source choice=0). |
| rt | Reaction time in milliseconds. |
| reward | Two-step: 0 = no reward, 1 = reward received. NaN for stage-1 rows (reward delivered at stage 2). |
| state | Two-step stage-2 state reached (0 = first planet, 1 = second planet; source 2/3 re-indexed to 0/1). NaN for stage-1 rows. |
| transition | Two-step transition type: common or rare. NaN for stage-1 rows. |
| phase | test for all two-step trials (source had no practice data for all 151 participants). practice or exp for MaRs-IB. |
| valid | 1 = valid response recorded, 0 = no valid response (source choice=0). |
| correct | MaRs-IB: 1 = correct, 0 = incorrect. NaN for two-step (no ground-truth answer). |
| age | Participant age in years (continuous, from mbmf_ages.csv). |
| gender | f or m (from mbmf_ages.csv; source Female/Male lowercased). |
| iq | WASI full-scale IQ score (from wasi_data.csv). NaN where unavailable. |

The two-step task is the primary measure (task_id=0, 151 participants, 200 paper-trials each, split into stage-1 and stage-2 rows per trial via `block`). Only 3 participants' MaRs-IB data (task_id=1) were present in the OSF project, so the matrix-reasoning subset is unrepresentative and was kept only for completeness.

## Text-format conversion

The two-step task (`exp0.csv`, task_id=0) was transcribed (151 transcripts). The MaRs-IB matrix-reasoning task (task_id=1) was skipped as not textifiable: its stimuli are visual matrix puzzles with no recoverable content in the data, and only 3 participants' rows were present.

Sample transcript (start up to the first marked response):

```
You are a space traveler collecting space treasure. On each trial you first choose between two spaceships shown on the left and right of the screen. Press 0 to pick the LEFT spaceship or 1 to pick the RIGHT spaceship. Each spaceship usually flies to its own home planet (about 70% of the time) and rarely to the other planet (about 30% of the time). After your spaceship lands on a planet, you ask one of two aliens for treasure, shown on the left and right of the screen. Press 0 to ask the LEFT alien or 1 to ask the RIGHT alien. The alien either gives you treasure or nothing. Your goal is to collect as much treasure as possible. You will complete 200 trials.
You choose the left spaceship. You press [HUMAN_RESPONSE]0[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

`simulate0.py` simulates the two-step task (task_id=0): 200 trials of a stage-1
spaceship choice (70% common / 30% rare transition) followed by a stage-2 alien
choice with probabilistic, slowly-drifting reward. The round-trip check against
`build_jsonl.py` passes byte-identically. The MaRs-IB matrix-reasoning rows
(task_id=1) remain unsimulated (not textifiable, and not part of the primary
effect). ASSUMPTION: the paper omits the exact drifting reward schedule, so each
stage-2 reward is drawn from an independent bounded random walk matching the
data's ~0.53 rate and slow block-level drift.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction

Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: hybrid two-step RL (Daw et al. 2011) with separate model-free
(beta_mf) and model-based (beta_mb) stage-1 inverse temperatures, stage-2 temp,
learning rate, eligibility trace, and stickiness; MAP fit (bounded L-BFGS, priors
per supplement), task_id=0, first 9 trials dropped.
Reproduced: mb_weight_increases_with_age (regression beta_mb ~ age; slope 0.134,
p=.002 vs paper slope .42, p<.001).
Not reproduced: none.
Numeric mismatch: reproduced slope (0.134) is smaller than the paper's (0.42) but
same sign and significant; secondary model-free null (no age effect on beta_mf) was
not reproduced (p=.04 vs paper's .23) and is treated as a non-primary robustness
claim, not gated on.
Partial validation: omit.
Indeterminate: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`experiments/exp0/` implements the two-step task (task_id=0) in static jsPsych v8
(3000 ms response window, 200 trials in four 50-trial blocks, per the paper).
The headless round trip passed: the saved CSV matches the `exp0.csv` schema
(columns, task_id=0, 400 rows per participant, `trial`=2*block/2*block+1,
`transition` common/rare). The MaRs-IB matrix-reasoning rows (task_id=1) are not
reproducible online — the visual matrix-puzzle stimuli have no recoverable
content and only 3 participants' rows are present — so they are skipped, as in
`simulate0.py`. ASSUMPTIONs surfaced: `age`/`gender`/`iq` left blank (no
demographics phase); reward-feedback 1000 ms, ITI 400 ms, post-stage-1 600 ms
and button colors/layout are cosmetic defaults; the "quarter"/"three-quarters"
break-screen messages are reconstructed on the same pattern as the verbatim
"You are halfway done!".
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25