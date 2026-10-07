---
tags:
- paradigm:adaptive-feedback-task
- cognitive-modeling:needs-review
- psych-201
- text-format:pass
- js-experiment:needs-review
- simulator:pass
- verification:pass
---

# xu_2023_augmenting

- Paper: https://doi.org/10.1145/3544548.3580905
- Data source: https://github.com/songlinxu/TimeCare
- Full text: https://dl.acm.org/doi/fullHtml/10.1145/3544548.3580905
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Xu, S., & Zhang, X. (2023). Augmenting Human Cognition with an AI-Mediated Intelligent Visual Feedback. In Proceedings of the 2023 CHI Conference on Human Factors in Computing Systems (CHI '23), April 23–28, 2023, Hamburg, Germany. ACM. https://doi.org/10.1145/3544548.3580905

## Experiment summary
N=79 participants (40 RL-agent group, 39 random baseline group) performed a modular arithmetic verification task (decide whether AB ≡ CD mod E, respond True/False). Each participant completed practice trials, then counterbalanced Control (no feedback) and Feedback sessions. The RL group received adaptive time-pressure feedback from a trained DRL agent (using a Drift-Diffusion Model simulation); the Random group received 50% random feedback. Key measures: binary choice accuracy, response time (ms), and self-reported attention and anxiety ratings (1-7) given once after each 100-trial test session. Research question: can a dual-DRL framework learn adaptive visual feedback to augment human cognitive performance?

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Numeric user ID from the source, kept as string |
| trial | 0-indexed trial counter, global per participant across all phases |
| response | Participant's binary response: 0=False, 1=True (derived from accuracy and truth) |
| correct | Whether response was correct: 0=incorrect, 1=correct |
| rt | Response time in milliseconds (resptime * 1000) |
| stimulus | The modular arithmetic problem shown, formatted as "A ≡ B (mod C)" |
| truth | Ground-truth correct answer: 0=False, 1=True |
| feedback | Feedback delivered: 0 or 1 |
| phase | Experiment phase: practice (calibration) or test |
| session | Source session label: calib or formal |
| step | Trial step number within session from source |
| condition | Between-subject group: rl (RL-agent feedback) or random (baseline) |
| order | Counterbalancing order: 0 or 1 |
| task | Source task indicator: -1 (practice), 0 or 1 (two formal task sets) |
| attention | Self-reported attention rating (1-7); NaN when not asked (practice trials) |
| attentiontime | Time spent on attention rating in seconds; NaN when not asked |
| anxiety | Self-reported anxiety rating (1-7); NaN when not asked (practice trials) |
| anxietytime | Time spent on anxiety rating in seconds; NaN when not asked |

### Pre-upload cleanup

Practice trails are included as-is. Sentinels (-1) in attention/anxiety columns were recoded to NaN. The `response` column was derived from `accuracy` and `truth`: when accurate, response = truth; when inaccurate, response = 1−truth.

The paper reports two feedback sessions per participant (Control and Feedback). The `session` column distinguishes calib (practice) from formal (test phase). The `condition` column encodes group assignment (rl vs. random). The `order` column captures counterbalancing order.

## Text-format conversion

`exp0.csv` was transcribed to natural language (one string per participant in `transcripts0.jsonl`). The task is textifiable: each trial shows a symbolic congruence "AB ≡ CD (mod E)" and the participant makes a free binary True/False judgment, which transfers directly to text. Per block the participant also gives free 1-7 attention and anxiety ratings. The time-pressure progress bar (visual) is present/absent per trial per the `feedback` column and is narrated rather than marked. No experiment was skipped.

**Sample transcript** (start, up to the first marked response):

```
You take part in a study on math problem solving. For each question you will see a congruence statement of the form "AB ≡ CD (mod E)", where AB and CD are two two-digit numbers and E is a one-digit number. To answer, first subtract CD from AB, then judge whether the result is divisible by E. If it is, the statement is true; otherwise it is false. Take accuracy as your first priority, then answer as quickly as you can. You answer by pressing the button for True or False: press T for True, press F for False.
In some blocks a progress bar may appear at the top of the screen while you are answering. It fills by one unit per second and resets after 5 seconds. It is only there to convey a sense of passing time; there is no penalty associated with it.
First you complete a practice block to get familiar with the task. Then you complete two main blocks of 100 questions each. After each main block you will be asked to rate your current attention level and your current anxiety level, each on a scale from 1 to 7 (1 = lowest, 7 = highest); to answer, type a single number from 1 to 7.
The practice block begins. You work through 10 practice problems. No progress bar is shown.
You see the problem: 89 ≡ 71 (mod 9). You press [HUMAN_RESPONSE]T[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

`simulate0.py` simulates the single experiment (`exp0`) as a modular-arithmetic verification task. The round-trip check passed: the simulator's per-participant prompts are byte-identical to what `build_jsonl.py` regenerates from the simulated `exp0.csv`. No experiment was skipped. ASSUMPTION: the RL group's Feedback block is controlled by a trained PPO agent whose weights are not published, so a documented RT-based heuristic (running-mean + last-10 RT buffer) is substituted, matching the shipped js experiment; practice length is sampled from the data (single 1-10-trial session, not the paper's two-10-trial sessions); `rt`/`attentiontime`/`anxietytime` are dropped as a text simulator cannot produce them.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Online experiment

`experiments/exp0/` built (the paper has a single experiment). The headless round trip ran and the saved CSV matched `exp0.csv`'s schema; no experiment was skipped. ASSUMPTION: the `rl` group's Feedback block is controlled by a trained PPO agent whose weights are not published, so it is substituted here with a documented heuristic on the same observation (see `experiments/README.md`).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction

Attempted to reproduce the paper's primary computational-modeling result.

Fitted models: none; blocked before modeling.

Reproduced: none.

Not reproduced: none.

Numeric mismatch: none.

Indeterminate: the paper's only formal models are the dual-DRL framework — an LSTM math-answer agent, an SVM baseline predictor (SVC/SVR), and two PPO deep-RL agents (simulation and regulation) — all neural-network/deep-RL models that the skill does not implement. The headline RL-vs-Random result is a two-way between-subjects ANOVA on raw response-time data (a behavioral effect needing no model fit), so no standalone non-neural cognitive-modeling result is identifiable.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 2, minor 8; fixed 5, open 5).

Checked: paper (doi:10.1145/3544548.3580905; the ACM site blocks fetchers, so the PDF was taken from the Wayback Machine copy of the ACM PDF), original data (https://github.com/songlinxu/TimeCare, dataset/exp1.csv, identical in content to dataset/timecare_raw.csv), exp0, transform re-run (byte-identical), transcripts (rebuild byte-identical), simulator (smoke test and build_jsonl.py round trip), modeling (no model.py; the cognitive-modeling:needs-review tag and the Indeterminate section agree with the paper, whose only models are deep-RL/LSTM/SVM), analysis (both effects reproduce), logs (no secrets). Skipped: none.

Fixed:
- README Columns table gave the attention and anxiety ratings as 1-10; exp0.csv holds 1-7, the paper (p. 8) uses a 7-point Likert scale, and the source UI offers buttons 1-7. Changed to 1-7.
- README Experiment summary called the attention/anxiety ratings per-trial; the paper (p. 8) collects them once after each 100-trial test session, and exp0.csv carries one value per participant and test session, repeated on every trial row. Reworded.
- README Columns heading for exp0 used '###'; the template level is '####'.
- README Experiment summary stated no N per experiment; now 'N=79'.
- simulate0.py counted `step` globally across practice and test; exp0.csv restarts it at the formal session (calib 1-10, formal 1-200). Reset added; the smoke test runs and the build_jsonl.py round trip on 3 simulated participants is byte-identical.

Open:
- minor: check_repo.py reports 126 marked responses vs 122 free rows per transcript (participant 12350632). The 4 extra marks are the two attention and two anxiety ratings, which exp0.csv stores in the `attention`/`anxiety` columns (one value per test session) rather than as rows; the marked values equal the CSV values and build_jsonl.py regenerates transcripts0.jsonl byte-for-byte. Left as is: a row layout for the ratings would change the CSV, the transcripts, the simulator and the analysis.
- minor: the source file dataset/exp1.csv already lacks trials with response time < 0.8 s or > 10 s (the paper, p. 10, removes them as abnormal; shipped RT range 803-9999 ms): 2304 of 15800 formal trials and 138 of 790 practice trials are absent, so participants have 93-200 test rows. exp0.csv is faithful to the source.
- minor: the paper (p. 8) describes two 10-trial practice sessions; the source logging code (data_collection/modular_math_new.py) saves only the second one, so exp0.csv holds 1-10 practice trials per participant.
- minor: the transcripts narrate 'block of 100 questions' and 'You work through N practice problems' while a block holds 45-100 recorded trials, a consequence of the source's trial filter.
- minor: analysis.py tests the Group effect with a one-sided independent t-test instead of the paper's two-way Group x Order ANOVA (p. 10); the RL-group means reproduce exactly (-0.297 s absolute, -0.053 relative).

Run: claude-fable-5-1, 2026-09-13
