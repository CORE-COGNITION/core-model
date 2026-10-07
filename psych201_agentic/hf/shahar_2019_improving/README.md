---
tags:
- paradigm:two-step-task
- cognitive-modeling:needs-review
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:pass
---

# shahar_2019_improving

- Paper: https://doi.org/10.1371/journal.pcbi.1006803
- Data source: https://osf.io/zc24g/
- PDF: https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1006803&type=printable
- Full text: https://doi.org/10.1371/journal.pcbi.1006803
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Shahar, N., Hauser, T. U., Moutoussis, M., Moran, R., Keramati, M., NSPN Consortium, & Dolan, R. J. (2019). Improving the reliability of model-based decision-making estimates in the two-stage decision task with reaction-times and drift-diffusion modeling. *PLOS Computational Biology*, 15(2), e1006803.

## Experiment summary
Participants (N=554, each with a baseline and a follow-up session) completed a two-stage decision task (two-step task) across two sessions a mean of 17.75 months apart (range 11.76–31.44 months). Each trial: first-stage choice between two stimuli, probabilistic transition (common/rare) to a second-stage state, then second-stage choice yielding binary reward (0/1). Trial count differed by session: 121 trials at baseline, 201 at follow-up; the source CSV ships ~118 and ~197 per participant after the authors' pre-processing (see Notes). Research question: whether combining reaction times with choices via drift-diffusion modeling improves the reliability of model-based vs model-free RL parameter estimates.

## Notes

The source CSV (`TST_nspn.csv`) is the authors' pre-processed analysis set: trial 1 of each session and trials with a reaction time below 150 ms are omitted (about 2% of the nominal 121/201 trials; paper p. 19), so `rt` ranges 150–2000 ms and the source trial numbers have gaps. `trial` and `block` re-index the remaining paper-trials contiguously; the source trial number is not carried over.

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (1..554), as string |
| trial | 0..N-1 within each (participant_id, task_id), counting responses (each paper-trial produces 2 response-rows: stage1=even, stage2=odd) |
| block | 0..N-1 paper-trial index within each (participant_id, task_id); groups the 2 response-rows belonging to one paper-trial |
| response | 0-indexed choice: 0=first stimulus, 1=second stimulus (source coded 1/2) |
| rt | Reaction time in milliseconds (source: seconds, multiplied by 1000) |
| reward | Binary reward received after second-stage choice: 0 (no reward) or 1 (reward). NaN on stage-1 rows (reward is not yet known) |
| state | 0-indexed current state: 0 on stage-1 rows (the single first-stage state); on stage-2 rows 0 = second-stage state A, 1 = second-stage state B (source coded 1/2, re-indexed to 0/1). Tell the stages apart by `reward` (NaN on stage-1 rows) or by row order within `block` |
| transition | Transition type: 0 = common (70%; `second_stage_state` equals the stage-1 `response`), 1 = rare (30%). Coding of the source CSV and of its task code `DDM_RL_TST.m` (`0-common 1-rare`) |
| second_stage_state | 0-indexed identity of the second-stage state reached (0 or 1); repeated on both stage-1 and stage-2 rows |
| session | Data-collection wave: "baseline" for measurement=1, "follow_up" for measurement=2 |
| task_id | 0-indexed task instance: 0 = baseline session, 1 = follow-up session. State resets between sessions |
| phase | Always "test" — source does not distinguish practice from test trials |

## Text-format conversion

Transcribed `exp0.csv` (the two-stage / two-step decision task). The task is textifiable: each trial is a sequence of two nameable two-alternative choices (choose the first or second first-stage stimulus, then the first or second second-stage stimulus) with binary reward, fully reproducible in text. No experiments were skipped.

Sample transcript (participant 1, up to the first response):

```
You are playing a game where you try to win as many play pounds as possible; you get a bonus based on your total. Each round has two stages. In the first stage you see two first-stage stimuli: press A for the first stimulus or B for the second. Your choice moves you to one of two second-stage states. In the second stage you see two second-stage stimuli in that state: press A for the first stimulus or B for the second. Win as many play pounds as you can.

You begin the first session.
You see two first-stage stimuli. You press [HUMAN_RESPONSE]B[/HUMAN_RESPONSE]. …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

`simulate0.py` reproduces the two-stage decision task for exp0 (one simulator per experiment; none skipped). The round-trip check passed: regenerating transcripts from a simulated `exp0.csv` via `build_jsonl.py` yields byte-identical text. Notable `ASSUMPTION:` lines: the data encode transition 0 as common (70%) and 1 as rare (30%), as the OSF task code does; reward probabilities are shared across participants (single random-walk trajectory per bandit, per the OSF `rndwlk.m`); session trial counts are the nominal 121/201 with a ~2% random drop.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`experiments/exp0/` is a static jsPsych v8 port of the two-stage decision task built
from `simulate0.py` / `transcripts0.jsonl`. The headless `?mode=simulate` round trip
passed: the produced CSV matches `exp0.csv`'s schema exactly (columns, codings,
two-rows-per-trial structure, `trial` restart per `task_id`, ~70/30 common/rare
transition, binary reward from a clipped drift walk), and no outbound request fires
in simulate mode. No experiments were skipped. The browser records `rt` (ms), which
the text simulator could not. Notable `ASSUMPTION:` worth surfacing: the reward random
walk is generated fresh per participant session (the source shares one walk per session
across participants), which does not change the task a participant experiences.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: Daw et al. (2011) two-stage RL model, 5- vs 7-parameter versions, per-(participant, session) bounded L-BFGS MLE, compared on summed BIC.
Reproduced: rl_seven_param_wins_bic (the 7-parameter RL model is favored over the 5-parameter model by BIC, matching the paper's choice of model for all w-parameter estimates).
Not reproduced: none.
Numeric mismatch: the paper reports hierarchical BIC_int (e.g. baseline 134738.6 vs 134194.7); here summed per-participant BIC (22,184 vs 21,585) reproduces the same direction/winner but different scale (individual vs hierarchical fit).
Partial validation: N=60 (participant, session) units, i.e. participants 1–30 in both sessions (full 554-participant fit exceeds the run's compute budget; the capped fit reproduces the result).
Indeterminate: none. The paper's headline reliability/parameter-recovery claims require simulation with known ground-truth parameters and are not directly checkable from the empirical CSVs; the checkable model-selection result (5 vs 7 parameter RL model) was used as the primary result.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 7, minor 4; fixed 11, open 0).

Checked: paper (https://doi.org/10.1371/journal.pcbi.1006803, PDF), original data (https://osf.io/zc24g/: TST_nspn.csv, task code, R script), exp0, transform re-run (exp0.csv byte-identical), transcripts (build_jsonl.py rebuild byte-identical), simulator (smoke test and build_jsonl.py round trip byte-identical), modeling (model.py capped at 60 (participant, session) units; the full 1108-unit fit extrapolated to ~15 h on this node and was stopped after 53 min), analysis (3 of 3 effects reproduce), logs. Skipped: none.

Fixed:
- model.py split each block's rows by state (0 = stage 1, 1 = stage 2), but stage-2 rows carry state 0 or 1 (the second-stage identity), so on 88,132 of 174,754 blocks the stage-2 choice was misread (a2=0, s2=0, reward unobserved). Rows are now split by reward (NaN = stage 1). Capped refit (60 units): BIC 22,184 (5-param) vs 21,585 (7-param), the 7-parameter model still wins; README modeling numbers updated (were 24,185 vs 23,946).
- README summary gave N=554 at baseline and N=379 at follow-up; the source CSV and exp0.csv have 554 participants in both sessions (paper p. 18-19: 554 with complete data at both time points).
- README summary gave sessions ~9 months apart; the paper (p. 18) reports a mean gap of 17.75 months (range 11.76-31.44).
- README summary gave ~200 baseline / ~411 follow-up trials; the paper (p. 19) states 121 and 201; exp0.csv has 118.5 and 196.9 blocks per participant on average.
- README transition column said 0 = rare, 1 = common; in the source 100% of transition=0 rows reach second_stage_state == choice1 (70.3% of trials) and the OSF task code DDM_RL_TST.m codes 0-common 1-rare. README fixed; the simulate0.py docstring and the README Simulators note no longer call the README note inverted.
- README state column said 1/2 for the second-stage states; exp0.csv codes them 0/1 (transform: second_stage_state - 1; state 0 on stage-1 rows), the convention of the collection's other two-step datasets. README now describes the actual coding.
- logs/auto-exp-sim.sessions.json carried diff patches of unrelated project-root files (.work_path, main.m, modeling_pending.txt naming other datasets, sub164.mat); the diffs list was emptied.
- Citation author order: the paper (p. 1) lists NSPN consortium before Dolan, R. J.
- Columns heading '### exp0' changed to the template's '#### exp0'.
- README Notes now state that the source CSV omits trial 1 of each session and RT < 150 ms trials (2.05% / 2.03% of the nominal 121/201 trials; paper p. 19), that rt spans 150-2000 ms, and that trial/block re-index contiguously without the source trial number. Data unchanged (faithful to the source).
- README modeling section said 'first 60 participants'; model.py caps (participant, session) units, so N=60 means participants 1-30 in both sessions. Wording fixed.

Open:
- none.

Run: claude-fable-5-1, 2026-09-14
