---
tags:
- paradigm:two-step-task
- cognitive-modeling:needs-review
- psych-101
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:needs-review
---

# feherdasilva_2023_rethinking

- Paper: https://doi.org/10.1038/s41562-023-01573-1
- Data source: https://github.com/carolfs/fmri_magic_carpet
- Full text: https://www.nature.com/articles/s41562-023-01573-1
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Feher da Silva, C., Lombardi, G., Edelson, M., & Hare, T. A. (2023). Rethinking model-based and model-free influences on mental effort and striatal prediction errors. Nature Human Behaviour, 7(6), 956-969.

## Experiment summary
A single fMRI/behavioral study (N=94) using a sequential two-stage decision task (Daw paradigm) with a between-subjects instruction manipulation: abstract vs story-based framing. Each trial (150 per participant) has a stage-1 choice, a transition to a second-stage state (common/rare), a stage-2 choice, and a binary reward outcome, with reaction times recorded; participants also gave post-task ratings (effort, understanding, complexity) and underwent eye-tracking/pupillometry. The paper tests whether more model-based behavior is associated with lower mental effort and whether striatal prediction errors are model-free rather than model-based, using hierarchical hybrid (model-based + model-free) reinforcement-learning models fit in Stan. exp0 captures the full two-step task as one row per decision (stage1 and stage2 rows grouped per paper-trial), keeping slow/missed trials flagged via `valid`/`slow`. Primary effects reproduce: model-based stay (reward × transition interaction), a story-condition increase in model-based weighting, and lower effort ratings in the story condition.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV filename (e.g. "1" from `001_story.csv`), as string |
| condition | Between-subjects instruction condition: `story` or `abstract` |
| runs | Number of fMRI runs completed by the participant (from ratings.csv, or participants.csv for participant 48, who has no ratings) |
| understanding | Post-task rating 0-4 of how well the participant understood the game |
| effort | Post-task rating 0-4 of how effortful playing the game was |
| complexity | Post-task rating 0-4 of how complex the participant thought the game was |
| block | Paper-trial index 0..149 (one stage-1 + one stage-2 row per block) |
| phase | `test` for all rows (source records no practice trials) |
| trial_number | Raw trial counter 0..149 from the source CSV |
| common | 1 if the transition was common, 0 if rare |
| reward_prob_1_1 | Reward probability of symbol 1 of second-stage state 1 |
| reward_prob_1_2 | Reward probability of symbol 2 of second-stage state 1 |
| reward_prob_2_1 | Reward probability of symbol 1 of second-stage state 2 |
| reward_prob_2_2 | Reward probability of symbol 2 of second-stage state 2 |
| isymbol_lft | Second-stage state the first-stage left symbol commonly transitions to (1 or 2) |
| isymbol_rgt | Second-stage state the first-stage right symbol commonly transitions to (1 or 2) |
| final_state | Second-stage state the participant transitioned to (1 or 2; NaN when no stage-1 choice) |
| fsymbol_lft | Second-stage symbol shown on the left (1 or 2; NaN when the stage-1 response was missed) |
| fsymbol_rgt | Second-stage symbol shown on the right (1 or 2; NaN when the stage-1 response was missed) |
| choice1 | Raw first-stage choice (1 or 2; NaN when missed) |
| choice2 | Raw second-stage choice (1 or 2; NaN when missed) |
| rt1 | First-stage reaction time in seconds (source units; NaN when missed) |
| rt2 | Second-stage reaction time in seconds (source units; NaN when missed) |
| slow | 1 if the participant failed to respond within 2 s on the trial, else 0 |
| stage | Which decision of the paper-trial this row captures: `stage1` or `stage2` |
| response | 0-indexed choice: stage1 row = choice1-1, stage2 row = choice2-1 (NaN when missed) |
| rt | Reaction time in milliseconds (rt1/rt2 x 1000; NaN when missed) |
| state | Second-stage state, 0-indexed: 0 for the stage-1 decision, final_state-1 for the stage-2 decision (NaN when the stage-1 response was missed) |
| reward | Outcome received after the second-stage choice (0 or 1; NaN on stage-1 rows) |
| valid | 0 if the participant missed the response (rt missing), else 1 |
| trial | 0..299 response counter, sequential within each participant across both stages |

The source records no practice trials, so all rows are tagged `phase: test`. The eye-tracking and fMRI data from the source repository are not behavioral trial-level responses and are excluded here; the two-stage task behavior and post-task ratings are retained. The per-participant post-task questionnaire text files (`data/questionnaire/*.txt`: two comprehension questions about the first-stage symbols, the three ratings, and a free-text strategy description) are not transformed beyond the ratings. `participant_id` values are drawn from the per-subject task_behaviour CSV filenames.

## Text-format conversion

The single experiment (exp0) is the Daw two-stage decision task with a between-subjects instruction manipulation (abstract vs story framing). Both conditions were transcribed: each participant's 150 flights/trials (a stage-1 carpet/box choice, a transition to a mountain/state, a stage-2 lamp choice, and a coin-or-nothing reward) become one natural-language transcript covering the whole session in order, including missed (slow) trials. No experiment was skipped. The two symbols at each stage are named A and B, with the letter-to-symbol assignment drawn per participant from a seed fixed by the participant id; the marked token is the letter of the chosen symbol (`response` 0 = symbol 1, 1 = symbol 2), and each trial line states which symbol was on the left and which on the right. Sample transcript (participant 1, story condition), verbatim from the start up to and including the first marked free response:

```
You will take 150 flights to the mountains and get paid for every gold coin the genies give you. You have two magic carpets. The symbol written on each carpet says which mountain it normally flies to, but if the wind is too dangerous the carpet lands on the other mountain instead. The carpets are shown on the left and right sides of the screen, and their borders glow for 2 seconds while you choose. The two carpets are marked with the symbols A and B; to choose a carpet press its symbol. The carpet flies you to a mountain, and when you wake up two lamps are glowing on that mountain, shown on the left and right. Each lamp has the name of the genie that lives inside written on it. On each mountain the two lamps are marked with the symbols A and B; to rub a lamp press its symbol. If a genie is interested in music he comes out and gives you a gold coin; otherwise he stays inside. A genie's interest may change over time, and each carpet lands more often on the mountain whose name is written on it. You must choose within 2 seconds at every step; if you are too slow the genies go to sleep and you get nothing. At every choice, press the symbol, A or B, of the option you choose.
Two carpets appear: the left one has symbol B, the right one has symbol A. You press [HUMAN_RESPONSE]B[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`experiments/exp0/` is a static jsPsych v8 port of the two-stage "magic carpet" task,
built from the paper and the original task code (the repo carries no `simulateN.py`).
The headless round trip passed in Chromium: the saved CSV matches `exp0.csv`'s schema
exactly (300 rows: 150 blocks, one stage-1 + one stage-2 row each), and the slow-trial
(missed-response) paths were checked separately. Browser-recorded columns the text
source could not produce are filled: `rt` (ms), the `slow`/`valid` flags, and the
post-task ratings (`understanding`/`effort`/`complexity`, 0-4). `runs` (fMRI runs) has
no browser analogue and is left blank. Assumption: the source reward-probability
"diffusion" step is reproduced as a plain reflected random walk (gauss(0, 0.025) on
[0.25, 0.75]), which matches `exp0.csv`'s distribution; the source's `incr % 1`
reflection does not.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

`simulate0.py` recreates the two-stage task for both conditions and passes the round trip through `build_jsonl.py` (regenerated transcripts byte-identical, both slow-trial paths exercised). Assumptions surfaced in the class docstring: reward-probability drift as a plain reflected gaussian(0, 0.025) random walk on [0.25, 0.75], per-block random symbol placement, ~1% miss probability per stage, and per-participant ratings/runs drawn from exp0.csv's distributions.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none (no primary computational-modeling result could be verified).
Numeric mismatch: none.
Indeterminate: the paper's full text is paywalled (nature.com; no OA copy, preprint, or
institutional deposit reachable), so the paper's primary modeling claims and reported
numbers could not be identified. The authors' analysis code (github.com/carolfs/fmri_magic_carpet)
shows a hierarchical hybrid model-based/model-free RL model fit in Stan whose fitted RPE
regressors feed fMRI BOLD analyses (striatal model-free vs model-based prediction errors),
which require neural data absent from exp0.csv; the paper's behavioral mediators (stay
probability from a logistic regression; effort ratings via ordered-logit comparison) are
standard inferential claims on raw choices/ratings, which are out of scope. No in-scope
formal modeling result could therefore be faithfully reconstructed.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: needs-review (critical 1, major 1, minor 7; fixed 7, open 2).

Checked: paper (https://doi.org/10.1038/s41562-023-01573-1: abstract, figure captions, data/code availability, and the Supplementary Information PDF; the main text is paywalled), original data (https://github.com/carolfs/fmri_magic_carpet, commit 3555bd1: data/task_behaviour/*.csv, data/ratings.csv, code/analysis/participants.csv, code/task/run.py, model.py, config.py, the instruction text files), exp0, transform re-run (byte-identical to the shipped exp0.csv before the runs fix), transcripts, simulators, analysis (all three effects reproduce), logs. Skipped: paper Methods (full text paywalled on nature.com; no open copy via Unpaywall, Europe PMC, OpenAlex or Semantic Scholar; sample, design and response format were taken from the figure captions, the Supplementary Information and the authors' task code instead); modeling (no model.py: the repo is tagged cognitive-modeling:needs-review and its modeling section reports the run as indeterminate, so there was nothing to re-run).

Fixed:
- critical: transcripts0.jsonl marked the key side (A = left, B = right) while exp0.csv `response` codes the chosen symbol (choice1/choice2 minus 1; the source's run.py records the symbol via code_to_bin, not the key), so check_repo flagged 94/94 transcripts as not one-to-one with the CSV response sequence. build_jsonl.py now names the two symbols of each stage A and B per participant (assignment drawn from a seed fixed by the participant id; 46 of 94 reversed), marks the letter of the chosen symbol, states the left/right layout in every trial line, and the instructions declare the tokens accordingly; transcripts0.jsonl rebuilt (rebuild byte-identical, 0/94 bijection failures), simulate0.py mirrored (round trip through build_jsonl.py 4/4 identical with both slow-trial paths exercised), README sample transcript updated.
- minor: exp0.csv had an empty `runs` for participant 48 (story), who is absent from data/ratings.csv, although code/analysis/participants.csv records runs = 3 for them and the README said the column came from the ratings/participants CSVs. transform.py now falls back to participants.csv; exp0.csv regenerated (only the 300 `runs` cells of participant 48 changed), transcripts0.jsonl rebuilt, README `runs` row updated.
- minor: the abstract-condition instructions omitted the trial count ("You perform trials"); the source's abstract_game_instructions.txt says "You will perform [num_trials] trials". Now "You perform 150 trials".
- minor: the abstract-condition stage-1 miss line used the story wording ("the boxes fly away without you"); now "You fail to respond within 2 seconds and get nothing." (23 lines; the 24 story lines are unchanged).
- minor: answered stage-2 lines said "You land on the mountain 2" while missed ones said "You land on mountain 2"; unified to the latter.
- minor: README rows for fsymbol_lft, fsymbol_rgt and state said NaN "when no stage-2 choice"; the source (run.py) records them whenever the stage-1 response was made, so they are empty only in the 47 blocks with a missed stage-1 response and present in the 81 blocks with a missed stage-2 response. Rows corrected.
- minor: README columns heading `### exp0` changed to `#### exp0`.

Open:
- major: the `## Modeling reproduction` section states that the paper's modeling claims and numbers could not be identified because the full text is paywalled; the freely downloadable Supplementary Information reports them (Supplementary Table 1: hybrid RL parameters per condition, model-based weight w = 0.60 [0.46, 0.75] abstract vs 0.73 [0.58, 0.86] story, higher for story with 0.89 probability; Supplementary Table 2: AIC sums, hybrid model best in both conditions), and the source ships the Stan code (hybrid_hier.stan, hybrid_bayesian.py on beh_noslow.csv). No model.py was written here (out of this skill's scope); the cognitive-modeling:needs-review tag is kept.
- minor: the source's data/questionnaire/*.txt (93 files; none for participant 48) hold two post-task comprehension answers about the first-stage symbols and a free-text strategy description per participant; transform.py reads only the ratings, so these responses are not in exp0.csv. A README Notes sentence now says so.

Run: claude-fable-5-1, 2026-09-10
