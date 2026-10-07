---
tags:
- paradigm:two-step-task
- cognitive-modeling:needs-review
- psych-201
- text-format:pass
- simulator:pass
---
# castrorodrigues_2022_explicit

- Paper: https://doi.org/10.1038/s41562-022-01346-2
- Data source: https://github.com/ThomasAkam/Two-step_explicit_knowledge
- PDF: null
- Full text: https://www.nature.com/articles/s41562-022-01346-2
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Castro-Rodrigues, P., Akam, T., Snorasson, I., Camacho, M., Paixão, V., Maia, A., Barahona-Corrêa, J. B., Dayan, P., Simpson, H. B., Costa, R. M., & Oliveira-Maia, A. J. (2022). Explicit knowledge of task structure is a primary determinant of human model-based action. Nature Human Behaviour.

## Experiment summary
Healthy volunteers (N=129, six conditions: fixed/changing/slow-paced task crossed with debrief/no-debrief about the transition structure, collected at Lisbon and New York sites) completed two-step reinforcement-learning sessions (four sessions each, 300 trials per session, ~170k paper-trials total across the group). Clinical groups (N=95 subsampled into exp1 as OCD and mood-and-anxiety, fixed-task with debrief) completed the same task. On each trial subjects made a first-stage choice (up/down at two locations), that was deterministically followed by a second-stage location, chose again (left/right), and received reward. Each two-step trial is split into two `response` rows discriminated by `stage`, with `block` grouping the two stages of each paper-trial. The headline claim, that explicit (debriefed) knowledge of task structure — rather than model-free reward history — is a primary determinant of model-based control, is supported by reward-dependent stay (p≈4e-25) and by a model-based (reward×transition) stay signature that rises after debriefing (p≈6.6e-5), verified on the local CSVs.

## Text-format conversion

Both experiments (exp0 healthy, exp1 clinical) use the same two-step task paradigm (stage-1 Up/Down choice, stage-2 Left/Right choice, binary reward), so both are textified with one shared transcriber. No experiment was skipped. Debriefed participants additionally receive a line noting they were told the task structure.

### Sample transcript

```
You are making a series of two-step decisions to try to obtain as many rewards as you can.
Each trial has two stages. At the first stage you choose between two options shown as two locations. You do this by pressing Up for the top location or Down for the bottom location. Your first choice takes you to a second location. At this second stage you again choose between two options, by pressing Left for the left option or Right for the right option. After your second choice you may receive a reward; your aim is to maximize the total rewards you earn. There is no penalty for wrong answers, and no response is timed.
On every first-stage decision, press either Up or Down. On every second-stage decision, press either Left or Right. Before the session you were also told how the task is structured: choosing one of the two first-stage locations reliably leads to a particular second location, so you can plan your first choice to reach the more rewarding second-stage option.

Session 1.
You choose the location by pressing [HUMAN_RESPONSE]Up[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

`simulate0.py` (healthy, exp0) and `simulate1.py` (clinical, exp1) generate format-identical two-step-task transcripts; the round-trip check through `build_jsonl.py` passes byte-identical for both. No experiment was skipped.

- ASSUMPTION: the shipped CSVs' second-stage reward depends only on (reward_block, stage-2 key), so rewards are drawn at that level (rates 0.80/0.20 by key); the transition structure (common p=0.8, mapping flips with transition block) drives the criterion-based block transitions (repo `simulation.py`) but is not observable in the transcript.
- ASSUMPTION: simulated participant IDs follow the repo's remapped scheme (exp0 P000.., exp1 P129..); sessions are fixed at 300 trials (150 for slow_paced).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Notes

### Columns

| column | description |
|--------|-------------|
| participant_id | Remapped ID (exp0: P000..P128 healthy; exp1: P129..P223 clinical), from raw integer subject IDs |
| trial | Response counter, 0..599 within each (participant_id, task_id) |
| response | Coded stage choice: 0/1 (stage1: up=0 down=1; stage2: left=0 right=1) |
| stage | 'stage1' or 'stage2' (the two responses of each two-step trial) |
| block | Paper-trial index 0..299 within each (participant_id, task_id); the two stages share a block value |
| trial_number | Original trial label from the log (1..300) |
| reward_block | Reward schedule block (0/1/2) from the trial log line |
| transition_block | Transition structure block (0) from the trial log line |
| task_id | Session index 0..3; each session is an independent 300-trial run |
| session | Same as task_id (0..3), source session number minus one |
| condition | Combined condition, e.g. 'changing_task_debrief' |
| group | Participant group: healthy / OCD / mood-and-anxiety |
| task_type | Task variant: fixed / changing / slow_paced |
| debrief | Whether task-structure instruction given: 'debrief' or 'no_debrief' |
| site | Data-collection site: 'LS' (Lisbon) or 'NY' (New York) |
| phase | All rows 'test' (no separate practice phase in logs) |
| response_key | Raw keyed response name from the log ('Up'/'Down'/'Left'/'Right') |
| rt | Reaction time in ms: triggered - stimulus-onset for that stage |
| reward | Trial outcome (1 present / 0 absent), carried on stage2 row; NaN on stage1 row |
| valid | 1 if response and onset logged, else 0 (all 1) |

Both experiments share the same column set; the columns.md breakdown lists the identical columns for exp0 and exp1. The 2-experiment split reflects the two subject populations (healthy vs clinical), matching the paper's organization. The paper's Methods section body was not openly accessible, so the experiment split follows the dataset's condition/group structure. Cognitive-modeling flag is set because the paper fits formal hybrid model-based/model-free RL models to the data.

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: MF, MBi, MF_MBi (two-step RL agents with bias+perseveration kernels, per repo Two_step/RL_agents/), fit per (healthy-volunteer, session) unit by bounded L-BFGS; model comparison on the paper's iBIC via a Huys-style hierarchical EM (coarser EM/draw settings); debriefing test on per-subject MF-vs-mixture likelihood-ratio classification at session 3, G_mb weight change session 3->4.
Reproduced: debrief_increases_model_based.
Not reproduced: none.
Numeric mismatch: debrief G_mb increase reproduced (mean +5.95, n=41, p=0.025, vs no-debrief n.s.); absolute iBIC values differ from the paper's full population fit (same relative order on the capped fit).
Partial validation: N=40.
Indeterminate: the mixture model's iBIC was numerically unstable (NaN) at full 201-session scale in this EM approximation, so the model-comparison result (fixed_task_mixture_model_wins) is validated on a capped 40-participant fit where MF_MBi wins by iBIC, matching the paper's Supp Fig 2a.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25