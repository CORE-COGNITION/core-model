---
tags:
- paradigm:two-step-task
- cognitive-modeling:fail
- psych-101
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---

# zorowitz_2023_data

- Paper: https://osf.io/2tgjd/
- Data source: https://osf.io/2tgjd/ (OSF project "Data from two-step task pilots"; data.csv + demographics.csv)
- Full text: the OSF project README (https://osf.io/2tgjd/) which documents the task, methods, and data dictionary (no standalone paper PDF exists — this is unpublished pilot data from "Zorowitz & Niv (unpublished)")
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Zorowitz, S., & Niv, Y. (unpublished). Data from two-step task pilots. OSF. https://osf.io/2tgjd/

## Experiment summary
Unpublished pilot data from 149 participants recruited on Prolific (Aug–Dec 2021, online, gamified "space-themed" two-step task code available from the Niv lab jspsych-demos repo). Each participant completed 201 two-stage trials: a first-stage choice between two stimuli, a probabilistic (common 70% / uncommon 30%) transition to one of two second states, a second-stage choice between the two stimuli of the state reached (four second-stage stimuli in total), and a reward (0/1) determined by drifting contingencies (drift_ix schedules). Three experiments manipulate whether first- and second-stage stimuli occupy random or fixed left/right screen positions: Experiment 1 (N=50) = full randomization, Experiment 2 (N=50) = fixed positions, Experiment 3 (N=49) = first-stage randomized, second-stage fixed. Two-step (Daw) task: sequential decision-making under uncertainty, assessing model-based vs model-free reinforcement learning. Standard signatures reproduce when the three experiments are pooled (model-free reward effect and reward x transition interaction; see `analysis.py`); per experiment, see the Modeling reproduction section. Data collected for task piloting purposes.

## Online experiment

A static jsPsych v8 port was built for each experiment under `experiments/`
(`exp0/` complete randomization, `exp1/` fixed positions, `exp2/` first-stage
randomization only), from the original task code (nivlab/jspsych-demos/tasks/two-step)
and the Daw et al. (2011) drift schedules. Each finishes into one CSV in this
dataset's schema (`trial = block*2 + (stage=='stage2')`, response identity coding,
`rt` in ms, `state_1_rt`/`state_2_rt` in seconds, `reward` blank on the stage1
row) so its data is drop-in compatible with `expN.csv`. The headless
`?mode=simulate` round trip passed for all three (schema and per-condition
randomization reproduced; demographic columns written blank as they are not part
of the in-browser task). No experiment was skipped. ASSUMPTION: the source's
space-themed SVG stimuli and arrow-key responses are presented as colored
letter-labeled buttons (rockets A/B, aliens A–D) chosen by arrow key or click;
instruction+quiz blocks are shown once and practice runs a fixed 10 trials — see
`experiments/README.md`.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Notes

### Columns

#### exp0 (Experiment 1 — complete randomization)
| column | description |
|--------|-------------|
| participant_id | De-identified participant identifier from source `subject` column |
| trial | 0..N-1 response counter (2 responses per paper-trial, per participant) |
| block | 0..200 paper-trial index within participant; groups the stage1+stage2 rows of a trial |
| phase | Session phase, always `test` (no practice recorded in source) |
| stage | Which response in the trial: `stage1` (state-1 choice) or `stage2` (state-2 choice) |
| response | Chosen stimulus identity: state-1 is 0/1; state-2 is 0..3 (source coding, already 0-indexed) |
| rt | Reaction time in milliseconds (source seconds * 1000) |
| state | 0-indexed state: 0 for stage 1, 0/1 for stage 2 |
| reward | Outcome reward on stage2 row (0/1); NaN on stage1 row (reward delivered at stage2) |
| trial_number | Original 1..201 trial number from source |
| experiment | Source experiment code (1) |
| condition | Snake_case label of the experiment's randomization condition (`complete_randomization`) |
| drift_ix | Drifting-probability schedule set (1, 2, 3, 4) |
| state_1_key | Stage-1 response side: 0=left, 1=right |
| state_1_choice | Stage-1 chosen stimulus identity (0/1) |
| state_1_rt | Stage-1 response time in seconds (raw source value) |
| transition | Transition type: 1=common (70%), 0=uncommon (30%) |
| state_2 | Second-state identity (0/1) |
| state_2_key | Stage-2 response side: 0=left, 1=right |
| state_2_choice | Stage-2 chosen stimulus identity (0..3) |
| state_2_rt | Stage-2 response time in seconds (raw source value) |
| outcome | Stage-2 reward: 1=reward, 0=nonreward |
| age | Participant age in years (from demographics) |
| gender | Canonical gender: f/m/other/na (mapped from Man/Woman/Other/Rather not say) |
| gender_free_response | Free-text gender response, if provided (blank otherwise) |
| ethnicity | Snake_case ethnicity (hispanic_or_latino / not_hispanic_or_latino / rather_not_say / unknown) |
| race | Snake_case race token, or a JSON list of tokens for a multiracial selection (e.g. `["asian", "white"]`) |
| education | Self-reported education category (raw string, e.g. Bachelor degree) |

#### exp1 (Experiment 2 — no randomization, fixed positions)
| column | description |
|--------|-------------|
| participant_id | De-identified participant identifier from source `subject` column |
| trial | 0..N-1 response counter (2 responses per paper-trial, per participant) |
| block | 0..200 paper-trial index within participant; groups the stage1+stage2 rows of a trial |
| phase | Session phase, always `test` (no practice recorded in source) |
| stage | Which response in the trial: `stage1` (state-1 choice) or `stage2` (state-2 choice) |
| response | Chosen stimulus identity: state-1 is 0/1; state-2 is 0..3 (source coding, already 0-indexed) |
| rt | Reaction time in milliseconds (source seconds * 1000) |
| state | 0-indexed state: 0 for stage 1, 0/1 for stage 2 |
| reward | Outcome reward on stage2 row (0/1); NaN on stage1 row (reward delivered at stage2) |
| trial_number | Original 1..201 trial number from source |
| experiment | Source experiment code (2) |
| condition | Snake_case label of the experiment's randomization condition (`no_randomization`) |
| drift_ix | Drifting-probability schedule set (1, 2, 3, 4) |
| state_1_key | Stage-1 response side: 0=left, 1=right |
| state_1_choice | Stage-1 chosen stimulus identity (0/1) |
| state_1_rt | Stage-1 response time in seconds (raw source value) |
| transition | Transition type: 1=common (70%), 0=uncommon (30%) |
| state_2 | Second-state identity (0/1) |
| state_2_key | Stage-2 response side: 0=left, 1=right |
| state_2_choice | Stage-2 chosen stimulus identity (0..3) |
| state_2_rt | Stage-2 response time in seconds (raw source value) |
| outcome | Stage-2 reward: 1=reward, 0=nonreward |
| age | Participant age in years (from demographics) |
| gender | Canonical gender: f/m/other/na (mapped from Man/Woman/Other/Rather not say) |
| ethnicity | Snake_case ethnicity (hispanic_or_latino / not_hispanic_or_latino / rather_not_say / unknown) |
| race | Snake_case race token, or a JSON list of tokens for a multiracial selection (e.g. `["asian", "white"]`) |
| education | Self-reported education category (raw string, e.g. Bachelor degree) |

No `gender_free_response` column (none provided by that subsample).

#### exp2 (Experiment 3 — first-stage randomization only)
| column | description |
|--------|-------------|
| participant_id | De-identified participant identifier from source `subject` column |
| trial | 0..N-1 response counter (2 responses per paper-trial, per participant) |
| block | 0..200 paper-trial index within participant; groups the stage1+stage2 rows of a trial |
| phase | Session phase, always `test` (no practice recorded in source) |
| stage | Which response in the trial: `stage1` (state-1 choice) or `stage2` (state-2 choice) |
| response | Chosen stimulus identity: state-1 is 0/1; state-2 is 0..3 (source coding, already 0-indexed) |
| rt | Reaction time in milliseconds (source seconds * 1000) |
| state | 0-indexed state: 0 for stage 1, 0/1 for stage 2 |
| reward | Outcome reward on stage2 row (0/1); NaN on stage1 row (reward delivered at stage2) |
| trial_number | Original 1..201 trial number from source |
| experiment | Source experiment code (3) |
| condition | Snake_case label of the experiment's randomization condition (`s1_randomization`) |
| drift_ix | Drifting-probability schedule set (1, 2, 3, 4) |
| state_1_key | Stage-1 response side: 0=left, 1=right |
| state_1_choice | Stage-1 chosen stimulus identity (0/1) |
| state_1_rt | Stage-1 response time in seconds (raw source value) |
| transition | Transition type: 1=common (70%), 0=uncommon (30%) |
| state_2 | Second-state identity (0/1) |
| state_2_key | Stage-2 response side: 0=left, 1=right |
| state_2_choice | Stage-2 chosen stimulus identity (0..3) |
| state_2_rt | Stage-2 response time in seconds (raw source value) |
| outcome | Stage-2 reward: 1=reward, 0=nonreward |
| age | Participant age in years (from demographics) |
| gender | Canonical gender: f/m/other/na (mapped from Man/Woman/Other/Rather not say) |
| ethnicity | Snake_case ethnicity (hispanic_or_latino / not_hispanic_or_latino / rather_not_say / unknown) |
| race | Snake_case race token, or a JSON list of tokens for a multiracial selection (e.g. `["asian", "white"]`) |
| education | Self-reported education category (raw string, e.g. Bachelor degree) |

No `gender_free_response` column (none provided by that subsample).

Each source trial is split into two rows (stage1 and stage2 responses), grouped by the `block` value so the two responses of a single paper-trial can be reassembled; `trial` counts the number of responses per participant across the session. `reward`/`outcome` and the full second-stage outcome are recorded on the stage2 row.

## Text-format conversion

All three experiments (exp0/exp1/exp2) were transcribed: the two-step (Daw) task is a sequential decision-making task over nameable colored stimuli (rockets and aliens), so it transfers to text without losing the information participants use. Each transcript narrates all 201 trials in order: the two rockets on screen (stage-1 choice), the transition to a planet, the two aliens there (stage-2 choice), and the treasure/junk outcome. The four aliens are labeled A–D by a random per-participant bijection and each rocket takes the letter of the alien with the same identity index, so every response value maps onto one token; each trial names which rocket letter stands on the left and on the right, and the response format is fixed in the instructions. No experiment was skipped. None of the experiments record free text.

Sample transcript (exp0, up to first response):

```
You are playing the Space Treasure game, where you visit alien planets to collect treasure. Each planet has aliens on it, and when you trade with an alien it gives you either treasure or junk. Treasure is valuable; junk is worthless. An alien may not give you treasure every time, and some aliens are more likely to give you treasure than others. Your goal is to figure out which aliens are most likely to give you treasure and trade with them. To reach a planet, you first pick a rocket ship: each rocket has a planet it usually flies to, but sometimes it goes to the other one. To pick a rocket or an alien you press the single letter shown beside it. At the end, your total treasure is converted into a performance bonus, so try to collect as much as you can.
The left/right screen positions of the rockets and aliens are reshuffled at random on every trial. Trial by trial:
Two rockets appear, one on the left (letter B) and one on the right (letter A). You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: stay/switch logistic regression on reward, transition, and reward x transition (per-participant MLE, bounded L-BFGS; group-level one-sample t-test).
Reproduced: model_free_reward_effect_exp0, model_free_reward_effect_exp1, model_based_interaction_exp1, model_based_interaction_exp2.
Not reproduced: model_based_interaction_exp0 (mean -0.60, one participant pulls the sign negative; median +0.06, pooled interaction +0.22 p=0.06, so the canonical model-based signature does not robustly reproduce in the full-randomization condition), model_free_reward_effect_exp2 (mean +0.55, p=0.20). Under a pooled clustered (GEE) analysis the reward main effect is not significant in any experiment.
Numeric mismatch: none published (unpublished pilot; no reported numbers).
Indeterminate: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

Text simulators added for all three experiments: `simulate0.py` (complete randomization), `simulate1.py` (no randomization), `simulate2.py` (s1 randomization). Each reproduces the two-step generative process (201 trials, 70%/30% common/uncommon transitions with the mean kept in 0.6-0.8, drift_ix 1-4 reward schedules from Daw et al. 2011, per-condition stage-1/stage-2 side randomization) and the round-trip check through `build_jsonl.py` passed byte-identically for every experiment. No experiment was skipped. Column drops (text-recoverable only): `rt`, `state_1_rt`, `state_2_rt` (browser timings), `state_2_key` (the transcript never records alien screen side), and demographics. Per-participant alien letter labels (the rockets share the letters of aliens 0/1) are seeded from the participant id exactly as in `build_jsonl.py` (`zlib.crc32`); each experiment's condition sentence (complete / fixed / stage-1-only randomization) and the per-trial left/right rocket letters mirror `build_jsonl.py`.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 1, major 5, minor 6; fixed 10, open 2).

Checked: paper (OSF README and wiki at https://osf.io/2tgjd/; no PDF exists), original data (https://osf.io/2tgjd/: data.csv, demographics.csv), exp0-exp2, transform re-run (byte-identical to the uploaded CSVs), transcripts (rebuilt and diffed), simulators (smoke test and byte-identical round trip), modeling (section and tag consistency; no model.py on the cognitive-modeling:fail path; independent stay/switch fit), analysis (both effects reproduce), logs. Skipped: none.

Fixed:
- critical: transcripts0/2 narrated rocket_letter[0] on the left on every trial; in exp0 5031 of 10050 and in exp2 4892 of 9849 trials the letter named on the left was not the one pressed 'for the left rocket' (state_1_key). build_jsonl.py now names the rocket on each side per trial; transcripts0-2 rebuilt; simulate0-2 mirror it.
- major: the exp2 condition sentence said rockets and aliens are reshuffled every trial; the OSF wiki randomizes first-state stimuli only in Experiment 3. build_jsonl.py and simulate2.py got their own s1_randomization sentence; the README Simulators note no longer carries the assumption.
- major: marked tokens were not one-to-one with the response column (46/50, 44/50, 46/49 transcripts) because rockets and aliens used separate letter bijections; per-stage tokens were correct. Rocket r now takes alien r's letter in build_jsonl.py and simulate0-2.py.
- major: transform.py turned the multiracial source value 'Asian; White' into 'asian;_white' (7 participants). race is now a JSON list of tokens per the schema; exp0-2.csv regenerated (only the race column changed), transcripts rebuilt, README row updated.
- major: README documented ethnicity as hispanic_latino / not_hispanic_latino; the CSVs hold hispanic_or_latino / not_hispanic_or_latino.
- major: README had no Columns table for exp1 and exp2 (a 'same as exp0 except' sentence); full tables added.
- minor: Experiment summary said 'second-stage choice among four stimuli'; per trial the choice is between the two stimuli of the state reached (OSF data dictionary).
- minor: Experiment summary claimed 'Standard signatures reproduce' without qualification while the Modeling section lists per-experiment failures; now stated as pooled across the three experiments (analysis.py).
- minor: 'N=149' in the Experiment summary was read as a per-experiment N claim; now '149 participants'.
- minor: transcripts said 'a uncommon route'; now 'an uncommon route' (build_jsonl.py, simulate0-2.py).

Open:
- minor: education is kept as the source's category string (e.g. 'Bachelor degree'); the schema asks for an ordinal integer code, but the source defines none.
- minor: the Modeling reproduction section cannot be re-run because no model.py is in the repo (the cognitive-modeling:fail path uploads none). An independent per-participant stay/switch logistic fit agrees that exp0's reward x transition interaction is not significant (mean -0.14, p=0.26) but finds exp2's reward effect significant (mean +0.46, p=0.01) where the section reports p=0.20; the difference is implementation-dependent.

Run: claude-fable-5-1, 2026-09-13
