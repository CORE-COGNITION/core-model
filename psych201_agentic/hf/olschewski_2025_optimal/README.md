---
tags:
- paradigm:risky-choice
- cognitive-modeling:needs-review
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:pass
---

# olschewski_2025_optimal

- Paper: https://doi.org/10.1016/j.cogpsych.2025.101716
- Data source: https://osf.io/7duw9/
- PDF: https://wrap.warwick.ac.uk/id/eprint/189632/7/1-s2.0-S0010028525000040-main.pdf
- Full text: https://www.sciencedirect.com/science/article/pii/S0010028525000040
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Olschewski, S., Mullett, T. L., & Stewart, N. (2025). Optimal allocation of time in risky choices under opportunity costs. Cognitive Psychology, 157, 101716. https://doi.org/10.1016/j.cogpsych.2025.101716

## Experiment summary
Two preregistered online (Prolific) studies investigated how people allocate deliberation time to risky choices under opportunity costs. In Study 1 (exp0, N=127) participants rated 60 single lotteries and then chose between pairs of them, with the utility difference between the lotteries either known or unknown across blocked conditions; in Study 2 (exp1, N=240) they chose between lotteries under a manipulated opportunity cost, either with or without a time limit per block. Response type is a binary choice (Lottery A/B) with per-trial reaction times; the rating phase itself is not in the data, only the resulting ratings of each pair. The authors fit drift-diffusion models with constant versus collapsing decision bounds to ask whether decision-makers adaptively adjust their evidence-accumulation threshold to the environment's cost structure.

## Notes

### Columns

#### exp0

| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (`participant.label`, 1..127) |
| trial | 0..N-1 within each participant_id, in presentation order (derived from `subsession.round_number`) |
| response | `player.choice`: 0 = Lottery A, 1 = Lottery B; empty where the source has no choice (see `valid`) |
| block | `player.block` 0-indexed (1..8 in source → 0..7) |
| rt | `player.rt` response time in msec |
| reward | `player.payoff` bonus-payment amount in ECU, recorded on the app's final round (0 before the end-of-experiment bonus draw; 0 on every row for the 22 participants whose final round was a filler pair the source omits; `participant.payoff` holds the bonus for everyone) |
| condition | Known vs unknown utility difference (from `cond`): `known_utility` / `unknown_utility` |
| valid | 1 if a choice was recorded; 0 if the source has none: the authors blanked the choice and RT of each participant's 5% fastest and 5% slowest responses per condition (`player.input_keyboard`/`player.page_submit` still present), the block timer ran out during the trial (`player.timedout` = 1), or the pair was never shown (`player.display_count` = 0) |
| participant.id_in_session | Session-internal participant index (1-based in source) |
| participant.label | Original participant ID (1..127); duplicates participant_id |
| participant._is_bot | 0/1 bot flag |
| participant._index_in_pages | oTree page index |
| participant._max_page_index | oTree max page index |
| participant._current_app_name | oTree app name |
| participant._current_page_name | oTree page name |
| participant.time_started | Session start timestamp |
| participant.visited | Visited-pages count |
| participant.payoff | Total payoff for participant |
| player.id_in_group | oTree player id in group |
| player.stimuid | Stimulus ID |
| player.gameidA | Lottery A ID (1..60) |
| player.gameidB | Lottery B ID (1..60) |
| player.ratingdiff | Absolute rating difference between Lottery A and B (1..4) |
| player.ratingA | Rating of Lottery A (1..7) |
| player.ratingB | Rating of Lottery B (1..7) |
| player.oa1 | Lottery A first outcome (2..96) |
| player.oa2 | Lottery A second outcome (2..96) |
| player.pa1 | Lottery A probability of first outcome (25..75%) |
| player.pa2 | Lottery A probability of second outcome (25..75%) |
| player.ob1 | Lottery B first outcome (2..96) |
| player.ob2 | Lottery B second outcome (2..96) |
| player.pb1 | Lottery B probability of first outcome (25..75%) |
| player.pb2 | Lottery B probability of second outcome (25..75%) |
| player.blockround | Trial number within a block (1..20 known / 1..47 unknown) |
| player.blocktotal | Number of trials in the block (20 known / 47 unknown) |
| player.reversed_presentation | 0 = Lottery A left/B right; 1 = Lottery A right/B left |
| player.input_keyboard | 0 = mouse click, 1 = keyboard |
| player.timedout | 0/1 whether the response window timed out |
| player.page_load | Page-load timestamp (msec) |
| player.page_submit | Page-submit timestamp (msec) |
| player.display_count | Display counter |
| player.paychoice | Choice chosen for the bonus draw (0/1) |
| player.payo1 | Paid outcome 1 of Lottery A |
| player.payo2 | Paid outcome 2 of Lottery A |
| player.payp1 | Paid probability 1 of Lottery A |
| player.payp2 | Paid probability 2 of Lottery A |
| player.nopayo1 | Non-paid outcome 1 of Lottery A |
| player.nopayo2 | Non-paid outcome 2 of Lottery A |
| player.nopayp1 | Non-paid probability 1 of Lottery A |
| player.nopayp2 | Non-paid probability 2 of Lottery A |
| group.id_in_subsession | oTree group id in subsession |
| subsession.round_number | oTree round number (presentation order) |
| session.is_demo | 0/1 demo flag |
| eva | Expected value of Lottery A |
| evb | Expected value of Lottery B |
| evd | Expected value difference (B - A) |
| sda | Standard deviation of Lottery A |
| sdb | Standard deviation of Lottery B |
| sdd | Standard deviation difference (B - A) |
| errcho | 1 if choice inconsistent with average-rating direction, 0 if consistent |
| difficulty | 0/1 difficulty flag |
| avrating | Average of ratings for Lottery A and B (1..7) |
| ratediff | Rating difference |
| evm | Average expected value of both lotteries |
| rtsec | Response time in seconds |

#### exp1

| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (`participant.label`, 1..240) |
| trial | 0..N-1 within each participant_id, in presentation order (derived from `subsession.round_number`) |
| response | `player.choice`: 0 = Lottery A, 1 = Lottery B; empty where the source has no choice (see `valid`) |
| block | `player.block` 0-indexed (1..8 in source → 0..7) |
| rt | `player.rt` response time in msec |
| reward | `player.payoff` bonus-payment amount in ECU, recorded on the app's final round (0 before the end-of-experiment bonus draw; 0 on every row for the 116 participants whose final round was an unrated pair the source omits; `participant.payoff` holds the bonus for everyone) |
| condition | Time-limit condition (from `timed`): `no_time_limit` / `time_limit` |
| valid | 1 if a choice was recorded; 0 if the source has none: the authors blanked the choice and RT of each participant's 5% fastest and 5% slowest responses per condition (`player.input_keyboard`/`player.page_submit` still present), the block timer ran out during the trial (`player.timedout` = 1), or the pair was never shown (`player.display_count` = 0) |
| participant.label | Original participant ID (1..240); duplicates participant_id |
| player.sid | Choice problem ID (1..80) |
| player.rating.x | First rating (-100..+100) |
| player.rating.y | Second rating (-100..+100) |
| eva | Expected value of Lottery A |
| evb | Expected value of Lottery B |
| evd | Expected value difference (B - A) |
| absevd | Absolute expected value difference |
| sda | Standard deviation of Lottery A |
| sdb | Standard deviation of Lottery B |
| sdd | Standard deviation difference (B - A) |
| rare | 1 if lotteries contained rare events, else 0 |
| avg_rating | Average of the two ratings (-100..+100) |
| absdev | Absolute difference between the two ratings (0..200) |
| participant.id_in_session | Session-internal participant index (1-based in source) |
| participant._is_bot | 0/1 bot flag |
| participant._index_in_pages | oTree page index |
| participant._max_page_index | oTree max page index |
| participant._current_app_name | oTree app name |
| participant._current_page_name | oTree page name |
| participant.time_started | Session start timestamp |
| participant.visited | Visited-pages count |
| participant.payoff | Total payoff for participant |
| player.id_in_group | oTree player id in group |
| player.oa1 | Lottery A first outcome |
| player.oa2 | Lottery A second outcome |
| player.pa1 | Lottery A probability of first outcome |
| player.pa2 | Lottery A probability of second outcome |
| player.ob1 | Lottery B first outcome |
| player.ob2 | Lottery B second outcome |
| player.pb1 | Lottery B probability of first outcome |
| player.pb2 | Lottery B probability of second outcome |
| player.blockround | Trial number within a block (1..20) |
| player.blocktotal | Number of trials in the block (20 no time limit / 40 time limit) |
| player.input_keyboard | 0 = mouse click, 1 = keyboard |
| player.timedout | 0/1 whether the response window timed out |
| player.page_load | Page-load timestamp (msec) |
| player.page_submit | Page-submit timestamp (msec) |
| player.display_count | Display counter |
| player.paychoice | Choice chosen for the bonus draw (0/1) |
| player.payo1 | Paid outcome 1 of Lottery A |
| player.payo2 | Paid outcome 2 of Lottery A |
| player.payp1 | Paid probability 1 of Lottery A |
| player.payp2 | Paid probability 2 of Lottery A |
| player.nopayo1 | Non-paid outcome 1 of Lottery A |
| player.nopayo2 | Non-paid outcome 2 of Lottery A |
| player.nopayp1 | Non-paid probability 1 of Lottery A |
| player.nopayp2 | Non-paid probability 2 of Lottery A |
| group.id_in_subsession | oTree group id in subsession |
| subsession.round_number | oTree round number (presentation order) |
| session.is_demo | 0/1 demo flag |
| errcho | 1 if choice inconsistent with average-rating direction, 0 if consistent |
| absavg_rating | Absolute average rating (0..100) |
| rtsec | Response time in seconds |
| lagchoice | Choice lag |
| rtrank | Reaction-time rank within a round |
| rtbins | Reaction-time bin |

Experiment files map directly to the paper's Study 1 (exp0) and Study 2 (exp1). The source ships only the choice phase's rated (target) pairs: the practice block, the rating phase, the 15 filler pairs per unknown-difficulty block (exp0) and the 20 unrated pairs per time-limit block (exp1) are absent, and the authors blanked the choice and RT of each participant's 5% fastest and 5% slowest responses per condition before upload; platform (oTree/MTurk worker, code, session) identifiers and fully-empty columns were dropped; trials without a choice are kept with `valid=0` and empty `response`.

## Text-format conversion

Both experiments were transcribed (exp0, exp1). Each is a risky-choice task where participants choose between two numerically-specified lotteries (each with two outcomes and probabilities), which loses no decision-relevant information, so both are textifiable. Only the choice phase is present in the CSVs (the earlier rating sessions are not), so the transcripts cover the choice session; per-trial RT is a measured variable and is not narrated. Every block opens with a `New block` line (known blocks state their rating difference). A trial without a recorded choice is narrated by its cause: the block timer ran out during it, the authors removed it as one of the participant's 5% fastest or slowest responses, or it was never shown (one summary line per block). The closing bonus line uses `participant.payoff`. Both transcripts are in `transcripts0.jsonl` / `transcripts1.jsonl`.

Sample transcript (exp0, from the start through the first marked response):

```
You take part in a risky-choice experiment. Earlier you rated 60 lotteries on a scale from 1 (least attractive) to 7 (most attractive). Now you choose between pairs of lotteries. On each trial you see Lottery A and Lottery B. Press A to choose Lottery A, or press B to choose Lottery B. At the end, one trial is selected and the chosen lottery played out, paying a bonus in experimental pounds converted to sterling at 20 to 1.
New block: all pairs in this block have the same rating difference of 1.0 and there is no time limit.
Lottery A: 70 at 38%, or 60 at 62%. Lottery B: 46 at 34%, or 69 at 66%. You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

Text simulators were written for both experiments (`simulate0.py` for Study 1, `simulate1.py` for Study 2). Each passes the round-trip check: its simulated `expN.csv` fed through `build_jsonl.py` regenerates transcripts byte-identical to the simulator's own prompts (modulo the random lottery draws and agent choices). Stimuli are resampled per trial from the real CSV's `player.o*`/`player.p*` columns grouped by `player.ratingdiff` (exp0) or `condition`+`rare` (exp1), so the narrated lottery lines read exactly like real ones. Assumptions surfaced: unknown/time-limit blocks are narrated at the CSV's analysed trial counts (32 / 20 per block, not the source blocktotal of 47 / 40); the end-of-session bonus is the drawn outcome of one played-out lottery stored on the final row; timeouts are not modelled (the uniform test agent always responds). No experiments were skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments got a runnable static [jsPsych](https://www.jspsych.org) v8 port under `experiments/` (`exp0/` = Study 1, `exp1/` = Study 2), built from the text simulators. The headless `?mode=simulate` round trip passed for both, matching the repo schema and the design counts (exp0 208 rows, exp1 160 rows, reward only on the final row). Omitted columns are oTree/session bookkeeping and rating-session/demographic fields an online participant cannot observe; the only consumer-facing assumption is a fixed Lottery-A-left / Lottery-B-right layout (response is coded by lottery identity, so the data is unaffected).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: constant- and collapsing-boundary drift-diffusion models (b/θ/ndt and g/θ/h/ndt), fit per participant per condition, compared by a group likelihood-ratio test on the summed deviance.
Reproduced: none (indeterminate).
Not reproduced: none — the direction reproduced everywhere (collapsing boundaries favored by large likelihood-ratio in all four conditions), but the fits themselves are unreliable.
Numeric mismatch: the model-comparison likelihood ratios reproduce directionally, but fitted parameters do not match the paper's estimates (e.g. accumulation noise θ pins at the search bound).
Partial validation: none.
Indeterminate: the paper's likelihood is Monte-Carlo simulated (R=10000 walks per evaluation) and is fit with a global differential-evolution optimizer, whose zero-sample-cell penalties structure the landscape toward the paper's reported parameter regime. The skill requires an exact, differentiable likelihood fit by bounded L-BFGS; that pipeline drives the accumulation-noise parameter θ to the search bound for essentially every participant (frac_at_bound≈1.0) and gives the collapsing model low convergence (frac_converged≈0.5). The resulting fits converge to a near-coin-flip regime that does not faithfully represent the paper's fitted models, so the reproduction could not be certified despite the qualitative model-comparison direction matching.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 2, major 5, minor 9; fixed 13, open 3).

Checked: paper (10.1016/j.cogpsych.2025.101716, Warwick WRAP PDF), original data (https://osf.io/7duw9/: study1_finaldata.csv, study2_finaldata.csv, data keys, R scripts), exp0-exp1, transform re-run (byte-identical), transcripts (rebuilt byte-identical), simulators (smoke run and round trip through build_jsonl.py), modeling section and cognitive-modeling:needs-review tag (consistent with each other and with the paper; no model.py because auto-exp-modeling exited indeterminate), analysis (3 of 3 effects reproduce), logs. Skipped: none.

Fixed:
- build_jsonl.py emitted a 'New block' header only at condition changes, so the second known block of each pair (always a different rating difference; the paper, p. 6-7, announces the difference before every block) was narrated under the previous block's header and the two timed blocks of a pair shared one timer line. Now one header per block in build_jsonl.py, simulate0.py and simulate1.py; transcripts0/1.jsonl rebuilt; simulator round trip byte-identical.
- Transcripts said 'You make no choice.' on 5452 (exp0) / 5448 (exp1) trials. The authors blanked the choice and RT of each participant's 5% fastest and 5% slowest responses per condition before upload (paper p. 7 and p. 11; exactly 8 of 80 untimed trials per participant; their R scripts trim nothing): 1999 / 3834 of these trials still carry player.input_keyboard and player.page_submit, 110 / 234 timed out (player.timedout = 1), and 3343 / 1380 were never displayed (player.display_count = 0) although their lotteries were narrated. build_jsonl.py now narrates each cause and replaces never-shown pairs with one summary line per block.
- The closing bonus line read 0 experimental pounds for 22 (exp0) / 116 (exp1) participants: reward (player.payoff) sits on the app's final round, which the source omits exactly when the last block ends on a filler or unrated pair; participant.payoff holds the bonus and equals reward wherever reward > 0. build_jsonl.py now uses participant.payoff; the derived 'payoff' metadata key that carried the same wrong value was removed.
- README said 'online (MTurk) studies'; the paper recruited through Prolific (p. 7; Study 2 from the same pool, p. 10).
- README said Study 1 participants 'rated pairs of lotteries'; they rated 60 single lotteries on a 7-point scale (p. 6); pairs were rated in Study 2 (p. 10).
- README described response and valid as 'no response' trials; the column rows for exp0 and exp1 now name the three causes of an empty choice (source-side RT blanking, timeout, never shown) with the columns that distinguish them.
- README described reward as 0 only before the bonus draw; it is 0 on every row for the 22 (exp0) / 116 (exp1) participants whose final round is not in the source, and participant.payoff holds the bonus for everyone.
- README summary claimed reaction times were 'also recorded during a pure rating phase'; no rating-phase rows exist in the data.
- README Notes sentence 'Only the analyzed main phase is a choice/rating block' replaced by what the source omits (practice block of 8 trials, rating phase, 15 filler pairs per unknown-difficulty block, 20 unrated pairs per time-limit block) and the source-side RT blanking.
- README exp0 said participant.id_in_session is 0-based in the source; the data runs 1..147.
- README title line '# Olschewski 2025 Optimal' set to '# olschewski_2025_optimal'.
- README column headings '### exp0' / '### exp1' set to '#### exp0' / '#### exp1'.
- README '## Text-format conversion' lacked a Run line; added 'Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24' (model and date from logs/auto-exp-transcribe.sessions.json).

Open:
- minor: the source omits the practice block (8 trials, p. 6), the rating phase, the 15 filler pairs per unknown-difficulty block (p. 7) and the 20 unrated pairs per time-limit block (p. 10); the transform re-run is byte-identical, so the CSVs are faithful to the source.
- minor: response is empty on 21% (exp0) / 14% (exp1) of rows; inherent to the source (blanked, timed-out and never-shown trials), kept with valid = 0.
- minor: the exp1 instructions map -100/+100 to the left/right lottery; the paper (p. 10) does not state which end of the rating bar is which. In the data a positive avg_rating goes with choosing Lottery B (errcho agrees on 99.3% of choices; the rest have avg_rating = 0).

Run: claude-fable-5-1, 2026-09-12
