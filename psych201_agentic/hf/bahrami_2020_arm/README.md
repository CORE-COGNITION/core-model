---
tags:
- paradigm:bandit
- cognitive-modeling:needs-review
- psych-101
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:pass
---
# bahrami_2020_arm

- Paper: https://osf.io/f3t2a/
- Data source: https://osf.io/f3t2a/ (public OSF depository: 4ArmBanditDescription.pdf + DataAllSubjectsRewards.csv)
- PDF: https://osf.io/download/fwqmc/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Bahrami, B., Navajas, J., Wang, Y., & Wang, S. (2020). 4 Arm Bandit Task Dataset [Data set]. OSF. https://osf.io/f3t2a/

## Experiment summary
One online restless multi-armed (4-arm) bandit task following the Daw et al. (2006) paradigm, run with N = 965 participants who each completed 150 trials. On each trial a participant chooses one of four arms and receives reward feedback; the true reward of each arm drifts over time under one of three predefined drift schedules (between-subject, mapped to `version`). Responses are discrete choices (arms 1-4, 0-indexed in `response`) plus reaction times in milliseconds. The research question concerns how humans balance exploration versus exploitation when the value of options changes continuously. Primary behavioral findings reproduced on this data: best-arm selection well above the 25% chance baseline, reward-following choice accuracy improving over trials, and slower reaction times on exploratory (non-best) compared with best choices.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject id from the source CSV. |
| trial | 0..149 trial number within each participant (source orders 150 trials per id; trial was implicit). |
| choice | Raw arm choice as recorded (1-4; NaN on missed/aborted trials). |
| response | 0-indexed arm choice (choice-1; 0=arm1 ... 3=arm4; NaN where choice is NaN). |
| reward | Payoff received on that trial (source units, NaN where no response/feedback recorded). |
| rt | Reaction time in milliseconds. |
| version | Drift schedule (payoff_group 2/3/4 recoded to 0/1/2). |
| reward_c1 | True reward of arm 1 on that trial per schedule. |
| reward_c2 | True reward of arm 2 on that trial per schedule. |
| reward_c3 | True reward of arm 3 on that trial per schedule. |
| reward_c4 | True reward of arm 4 on that trial per schedule. |

The source CSV records 965 participants × 150 trials (144,750 rows); trials where a participant failed to respond within 4 s are retained as rows with NaN choice/reward/rt (the source records them). `response` follows the gershman_2018_deconstructing bandit convention (0-indexed choice). No `task_id`/`block` is used: this is a single continuous drifting bandit per participant, with the drift schedule (a between-subject variant) captured in `version`.

## Text-format conversion

`exp0.csv` (the 4-arm bandit) was transcribed to `transcripts0.jsonl` (965 transcripts, one per participant, all 150 trials in order). Responses are the freely chosen arm (a single letter A/B/C/D, 1:1 with the 0-indexed `response`); missed trials are narrated as skipped trials. No experiment was skipped.

Sample transcript (start up to the first marked response):

```
Welcome to the 4-Arm Bandit experiment.
On each trial you will see four slot machines, labeled A, B, C, and D. Choose exactly one machine by pressing the corresponding key. After your choice you will see the reward you obtained from that machine. You will not see the rewards the other machines would have paid. Each machine's payoff drifts slowly over time, so keep trying different machines to find out which is paying well, while mostly choosing the ones that have been good recently. You have 4 seconds to respond; if you do not respond in time the trial is skipped and you earn no reward. The task lasts 150 trials. Press one of A, B, C, or D to choose a machine.

Trial 1: You choose machine [HUMAN_RESPONSE]A[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24.

## Simulators

`simulate0.py` simulates the 4-arm bandit (exp0) and passes the round-trip check through `build_jsonl.py` byte-for-byte. No experiment skipped. The simulator replays the three fixed payoff schedules of the study, one per version (`PAYOFFS` in `simulate0.py`, read from exp0.csv: `reward_c1`..`reward_c4` are identical on every trial for all participants of a version, and the received reward equals the chosen arm's payoff on all 139,816 answered trials), so a simulated participant faces the same bandit as the human participants. Miss rate ~0.034 and uniform version assignment are recovered from exp0.csv since the paper does not give them — see the ASSUMPTION lines in the class docstring. Until 2026-09-21 the simulator drew a fresh integer Gaussian walk (step SD ~6, clipped to [1, 98]) from the version's first-trial payoffs; its best-arm gaps differed from the participants' schedules, so effects that depend on the schedule (`choice_accuracy_improves`) were not comparable to the human data.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24.

## Online experiment

`experiments/exp0/` is a static jsPsych v8 port of the 4-arm bandit (150 trials,
4 machines A/B/C/D, 4 s response window). The headless `?mode=simulate` round trip
passed (schema columns match `exp0.csv` exactly; `rt` filled from the browser).
No experiment skipped. Browser-only assumptions surfaced in the experiment's README:
machine colors, Begin button, feedback/ITI timings, and that missed trials arise from
the 4 s timeout (the text simulator's `p_miss` is a text-agent artifact, not
injected). Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25.
## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Indeterminate: the paper is an OSF data note (4ArmBanditDescription.pdf) that describes the 4-arm bandit task and data structure but contains no computational-modeling result — no formal cognitive model is fit or compared anywhere; the only reported findings are descriptive behavioral effects (best-arm selection above chance, learning-curve improvement, RT differences vs best choice), which are out of scope.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 0, minor 7; fixed 4, open 3).

Checked: paper (4ArmBanditDescription.pdf, https://osf.io/download/fwqmc/), original data (DataAllSubjectsRewards.csv, https://osf.io/download/ez8nw/, 144,750 rows), exp0, transform re-run (exp0.csv byte-identical), transcripts (build_jsonl.py rebuild byte-identical), simulators (simulate0.py runs; round trip through build_jsonl.py byte-identical), modeling (no model.py; the paper reports no cognitive model, section and cognitive-modeling:needs-review tag agree), analysis (analysis.py: all 3 effects reproduce), logs. Skipped: none.

Fixed:
- README citation listed Hertz, U. as an author; OSF marks Uri Hertz as a non-bibliographic contributor and its APA citation omits him, and the PDF (p. 1) names Bahrami and Navajas as the collectors. Removed from the citation.
- README Experiment summary stated no N; now N = 965 (the CSV has 965 participants).
- README Columns heading for exp0 used '###'; changed to '#### exp0'.
- README '## Text-format conversion' had its Run line inside the paragraph; moved to the last line of the section.

Open:
- minor: the paper (p. 1) reports 975 participants; the source CSV ships ids 1..965 with no gaps and 150 rows each, and documents no exclusions. The CSV is faithful to the source.
- minor: exp0.csv keeps one negative reaction time (participant 864, trial 63, rt = -10777 ms); the source CSV records the same value, so it is kept as shipped (schema: preserve raw values).
- minor: 931 trials with a recorded choice have rt > 4000 ms (max 81,634 ms) although the paper (p. 1) states a 4 s deadline; identical in the source, kept as shipped.

Run: claude-fable-5-1, 2026-09-09
