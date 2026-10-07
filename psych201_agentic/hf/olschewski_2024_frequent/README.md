---
tags:
- paradigm:risky-choice
- cognitive-modeling:pass
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:pass
---
# olschewski_2024_frequent

- Paper: https://doi.org/10.1073/pnas.2317751121
- Data source: https://osf.io/aqjdz/ (DOI: https://doi.org/10.17605/OSF.IO/AQJDZ)
- PDF: https://wrap.warwick.ac.uk/id/eprint/184083/2/WRAP-frequent-winners-explain-apparent-skewness-preferences-experience-based-decisions-2024.pdf
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Olschewski, S., Spektor, M. S., & Le Mens, G. (2024). Frequent winners explain apparent skewness preferences in experience-based decisions. Proceedings of the National Academy of Sciences, 121(12), e2317751121. https://doi.org/10.1073/pnas.2317751121

## Experiment summary
Across seven decision-from-experience experiments, participants repeatedly sample outcomes from two (or more) lotteries of varying payouts and skewness and then choose between them. Studies 1–4 (exp0–exp3, N=99, 250, 250, 500) use a sampling-then-choice "broker game" in which participants sample 30 outcomes per option per game before making a single choice, with normal/catch/disskewed/conskewed conditions. Studies 5–7 (exp4–exp6, N=71, 85, 45) use repeating multi-armed bandit games (30 or 60 trials) where participants learn option values across trials. The paper tests whether apparent skewness preferences reflect intrinsic skewness seeking or simply a preference for frequent winners (aiming more wins than losses), and shows a reinforcement-learning model capturing frequent winning plus intrinsic skewness provides the best account of choices.

## Notes

### Columns

exp0–exp3 (Studies 1–4) are sampling-then-choice "broker game" decisions, one row per
decision. exp4–exp6 (Studies 5–7) are repeated-choice multi-armed bandits, one row per
choice; each game (`task_id`) is a fresh bandit (30 trials in exp4/exp5, 60 in exp6). In the
source bandit files the rows are sorted by condition (`block_id`) and `block_no` is the
game's presentation position; `task_id` follows the presentation order and `condition`
carries the condition label (mapping of `block_id` from the authors' `Analyses.ipynb`).

#### exp0

Study 1. One row per broker-game decision (14 per participant).

| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (`participant.label`) |
| trial | 0..13 within each participant_id, in presentation order |
| response | 0 = chose left option, 1 = chose right option (source `player.choice`) |
| condition | `normal` / `catch` / `disskewed` / `conskewed` (source `player.gamscond`) |
| samples_left | JSON list of the 30 sampled outcome values observed for the left option |
| samples_right | JSON list of the 30 sampled outcome values observed for the right option |
| side_right | 1 if the right option is the frequent loser (right-skewed) option (source `player.loserright`), else 0 |
| valid | 1 (all rows usable) |

#### exp1

Study 2. One row per broker-game decision (18 per participant).

| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (`participant.label`) |
| trial | 0..17 within each participant_id, in presentation order |
| response | 0 = chose left option, 1 = chose right option (source `player.choice`) |
| condition | `consrightwin` / `catch` / `disleftwin` / `disrightwin` / `consleftwin` (source `player.gamscond`) |
| samples_left | JSON list of the 30 sampled outcome values observed for the left option |
| samples_right | JSON list of the 30 sampled outcome values observed for the right option |
| side_right | 1 if the right option is the right-skewed option (source `player.rightskewright`), else 0 |
| valid | 1 (all rows usable) |

#### exp2

Study 3. One row per broker-game decision (18 per participant).

| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (`participant.label`) |
| trial | 0..17 within each participant_id, in presentation order |
| response | 0 = chose left option, 1 = chose right option (source `player.choice`) |
| condition | `disequal` / `catch` / `consequal` (source `player.gamscond`) |
| samples_left | JSON list of the 30 sampled outcome values observed for the left option |
| samples_right | JSON list of the 30 sampled outcome values observed for the right option |
| side_right | 1 if the right option is the right-skewed option (source `player.rightskewright`), else 0 |
| valid | 1 (all rows usable) |

#### exp3

Study 4. One row per broker-game decision (17 per participant).

| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (`participant.label`) |
| trial | 0..16 within each participant_id, in presentation order |
| response | 0 = chose left option, 1 = chose right option (source `player.choice`) |
| condition | `disskewed` / `dismore` / `conskewed` / `catch` / `normal` / `disless` (source `player.gamscond`) |
| samples_left | JSON list of the 30 sampled outcome values observed for the left option |
| samples_right | JSON list of the 30 sampled outcome values observed for the right option |
| side_right | 1 if the right option is the frequent loser (right-skewed) option (source `player.loserright`), else 0 |
| valid | 1 (all rows usable) |

#### exp4

Study 5. Two-armed bandit, 6 games x 30 choices.

| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (`subject_id`) |
| task_id | 0..5, one value per fresh bandit game, in presentation order (source `block_no` minus 1) |
| trial | 0..29 within each (participant_id, task_id), from source `trial_no` minus 1 |
| choice | Chosen option letter from source (A/B); letters are fixed per condition across participants (B is the left-skewed / frequent-winner option, A the right-skewed one) |
| response | 0 = A, 1 = B |
| condition | `catch` / `conskewed` / `normal` / `disskewed` / `disless` / `dismore` (source `block_id` 1–6; same conditions as exp3) |
| rt | Reaction time in milliseconds |
| choice_location | Screen position of the chosen option (left/right) |
| outcomeA | Outcome of option A on that trial |
| outcomeB | Outcome of option B on that trial |
| outcomeC | `-` (no third option in this experiment) |
| chosen_reward | Reward received = outcome of the chosen option |
| option_left | Option letter shown at the left position |
| option_center | `-` (no center position in this experiment) |
| option_right | Option letter shown at the right position |
| block_no | Presentation position of the game in the source (1–6) |
| valid | 1 (all rows usable) |

#### exp5

Study 6. Two- or three-armed bandit, 6 games x 30 choices.

| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (`subject_id`) |
| task_id | 0..5, one value per fresh bandit game, in presentation order (source `block_no` minus 1) |
| trial | 0..29 within each (participant_id, task_id), from source `trial_no` minus 1 |
| choice | Chosen option letter from source (A/B/C); letters are fixed per condition across participants (B is the left-skewed option in the skewed conditions; in `normal`/`normal_tri` A is the frequently winning Gaussian option; C is the decoy) |
| response | 0 = A, 1 = B, 2 = C |
| condition | `consskewed` / `consskewed_tri` / `normal` / `normal_tri` / `disskewedthree` / `disskewed` (source `block_id` 1–6; `_tri` = with an inferior Gaussian decoy C, `disskewedthree` = three equiprobable outcomes without a rare event) |
| rt | Reaction time in milliseconds |
| choice_location | Screen position of the chosen option (left/center/right) |
| outcomeA | Outcome of option A on that trial |
| outcomeB | Outcome of option B on that trial |
| outcomeC | Outcome of the decoy option C on that trial (`-` when absent) |
| chosen_reward | Reward received = outcome of the chosen option |
| option_left | Option letter shown at the left position |
| option_center | Option letter shown at the center position (`-` with two options) |
| option_right | Option letter shown at the right position |
| block_no | Presentation position of the game in the source (1–6) |
| valid | 1 (all rows usable) |

#### exp6

Study 7. Three-armed bandit, 3 games x 60 choices. `outcome_right` / `outcome_left` name the
option's skew direction, not its screen position.

| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (`subject_id`) |
| task_id | 0..2, one value per fresh bandit game, in presentation order (source `block_no`) |
| trial | 0..59 within each (participant_id, task_id), from source `trial` minus 1 |
| choice | Chosen option code from source (0/1/2) |
| response | 0 = right-skewed core option, 1 = left-skewed core option, 2 = decoy (same as `choice`) |
| condition | `gaussian_decoy` / `leftskew_decoy` / `rightskew_decoy` (source `block_id` 0/1/2; the Gaussian-decoy game is always played first) |
| rt | Reaction time in milliseconds |
| choice_location | Screen position of the chosen option: 0 = left, 1 = center, 2 = right |
| outcome_right | Outcome of the right-skewed core option (code 0) on that trial |
| outcome_left | Outcome of the left-skewed core option (code 1) on that trial |
| outcome_decoy | Outcome of the decoy option (code 2) on that trial |
| reward | Reward received = outcome of the chosen option |
| option_left | Option code shown at the left position |
| option_center | Option code shown at the center position |
| option_right | Option code shown at the right position |
| block_no | Presentation position of the game in the source (0–2) |
| valid | 1 (all rows usable) |

## Online experiment

All seven experiments got a runnable `experiments/expN/` (jsPsych v8): `exp0`–`exp3`
are the broker games (sampling-then-choice), `exp4`–`exp6` are the repeated
multi-armed bandits. The headless `?mode=simulate` round trip passed for every
experiment: the saved CSV reproduces each `expN.csv` schema exactly (column names,
0-indexed counters, response coding, row counts) with no outbound data request,
and `rt` is recorded for exp4–exp6 where the schema has the column. No experiment
was skipped. ASSUMPTIONS surfaced in `experiments/README.md`: broker-game sample
pacing (1,250 ms/pair + 200 ms) from the paper Methods; bandit reveal 1,400 ms +
300 ms gap; A=LEFT/B=RIGHT (response is coded by position); exp5's 2-machine
layouts use left/right; exp3's `disskewed` pair ports `simulate3.py` verbatim
(the mirror of the paper's stated distribution).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Text-format conversion

All seven experiments were transcribed to natural language (`transcripts0.jsonl`–`transcripts6.jsonl`): the broker games (exp0–exp3) as a narration of the 30 dividend pairs of the two stocks followed by the stock choice (response 0/1 → randomized per-participant A/B key for left/right), and the repeated-choice bandits (exp4–exp6) as per-turn machine choices with the revealed payoff of every available machine and the received reward (machines labeled by letter in exp4–exp5, by number in exp6). No experiment was skipped; Study 4's between-subject broker vs. bag-of-balls framing is not recorded in the CSV, so all exp3 transcripts use the broker framing. Responses are all freely chosen, so every one is marked.

Sample transcript (exp4, participant 38, verbatim up to the first response):

```
In this task you earn points by repeatedly choosing among slot machines. The task is played as a series of games; each game has its own machines, and the same machines stay available for the whole game. On each turn you pick one machine; right after your pick, one draw is revealed for every available machine showing what it would have paid, and you receive the draw of the machine you chose. Name each machine by its letter shown on screen. At the end, one of your turns is chosen randomly and pays your bonus.
Game 1:
Turn 1: the machines available are A, B. You choose [HUMAN_RESPONSE]B[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

All seven experiments got a text simulator (`simulate0.py`–`simulate6.py`), one per `expN.csv`/`transcriptsN.jsonl` pair. Each passes the round-trip check: writing the simulator's DataFrame as `expN.csv` and re-running `build_jsonl.py` reproduces the simulator's transcripts byte-for-byte (modulo the per-participant A/B letter mapping, which uses the same md5-of-participant rule as the generator). No experiment was skipped. Notable `ASSUMPTION:` lines: the exact continuous-outcome generation recipes (gamma transforms and quantile procedures) are approximated by standardized gamma quantiles rescaled to the paper's means/SDs; the frequent-winner yoking of identical Gaussian pairs is realized as a cyclic pairing that gives the designated winner 20 of 30 comparisons; Study 4/5 discrete and Gaussian marginals use the frequencies measured in the shipped CSVs.

Fixed 2026-09-15: simulate0-6.py asked the agent before narrating the trial; the decision-time prompt is now the transcript text up to the open marker (check_calls.py passes).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: Guessing, Standard RL, Standard RL + Skewness, Tallying RL, Tallying RL + Skewness (complete-pooling MLE across Studies 1-3, compared on BIC).
Reproduced: winning_model (Tallying RL + Skewness wins on BIC).
Not reproduced: none.
Numeric mismatch: none (BIC values match the paper's Table 1 closely: Guessing 14398.05 vs 14398, Standard RL 13539.42 vs 13539, Standard RL+Skew 13534.70 vs 13535, Tallying RL 12956.84 vs 12957, Tallying RL+Skew 12893.56 vs 12894).
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Verification

Verdict: pass (critical 0, major 4, minor 9; fixed 6, open 5).

Checked: paper (https://doi.org/10.1073/pnas.2317751121; WRAP accepted manuscript and the OSF SI), original data (https://osf.io/aqjdz/, 26 files incl. data/study01-07.csv and the authors' notebooks), exp0-exp6, transform re-run, transcripts, simulators, modeling, analysis, logs. Skipped: none.

Fixed:
- transform.py derived task_id for exp4-exp6 from the source row order, which is sorted by condition (block_id); block_no is the presentation position (e.g. exp4 participant 38 played block_no 2,6,1,4,3,5). task_id therefore equalled block_id-1 for every row and matched the presentation order for only 18% / 15% / 54% of rows, while the README claimed presentation order. task_id now ranks block_no per participant, rows are sorted (participant, task_id, trial); exp4-exp6.csv regenerated with the same rows, transcripts4-6.jsonl rebuilt so the games appear in the order played.
- transform.py never read the source block_id (the condition), so exp4-exp6.csv had no condition column. Added `condition` with the authors' labels from Analyses.ipynb (exp4: catch/conskewed/normal/disskewed/disless/dismore; exp5: consskewed/consskewed_tri/normal/normal_tri/disskewedthree/disskewed; exp6: gaussian_decoy/leftskew_decoy/rightskew_decoy).
- README Columns section had one shared table for exp0-exp3 and one for exp4-exp6 under `###` headings (no table for exp1/2/3/5/6; exp4 rows missing for outcomeB/outcomeC/option_center/option_right). Now one `#### expN` table per experiment; exp6's outcome_right/outcome_left/outcome_decoy are documented as the draws of the right-skewed (code 0), left-skewed (code 1) and decoy (code 2) options (reward matches these columns for 100% of the corresponding choices), not screen positions.
- logs/auto-exp-sim.sessions.json carried a diff of the project file modeling_pending.txt that lists other datasets (anll_2024_comparing, badham_2017_deficits, ...); that single diff entry was removed.
- simulate4.py/simulate5.py wrote block_no as a condition tag and had no condition column; now block_no = presentation position (task_id + 1) and `condition` carries the label, matching the CSVs. simulate6.py wrote outcome_right/left/decoy by screen position with arm 0 = left-skewed and shuffled all three games; now arm 0 = right-skewed, 1 = left-skewed, 2 = decoy with identity-based outcome columns, the Gaussian-decoy game first (as for 45/45 participants in study07.csv), block_no = task_id and `condition` added. All seven simulators pass the build_jsonl.py round trip exactly.
- README title line changed from '# Olschewski 2024 Frequent' to '# olschewski_2024_frequent'.

Open:
- minor: paper p. 10 gives SD = 15.15 for Study 2's discrete distributions; the source sequences in exp1.csv (three outcomes x 10, skewness +/-0.56 as stated) have SD 19.15. Inside the source; the data is faithful.
- minor: SI p. 2 describes a between-subject framing in Study 4 (broker game vs bag of balls); study04.csv records no framing variable, so exp3.csv cannot carry it.
- minor: check_repo reads the Experiment summary's 'N=99, 250, 250, 500' as N=99 only; the counts match the CSVs (99/250/250/500/71/85/45). Text left unchanged.
- minor: the paper's model comparison (Table 1, p. 7) includes a sixth model, selective integration (BIC 12,962); model.py fits five. The winner is unaffected and all five BICs reproduce (14398.05 / 13539.42 / 13534.70 / 12956.84 / 12893.56 vs 14,398 / 13,539 / 13,535 / 12,957 / 12,894).
- minor: simulate4.py/simulate5.py randomize the option letters per participant; in study05/06.csv the letters are fixed per condition (B = left-skewed option; A = frequent winner in study06's Gaussian conditions).

Run: claude-fable-5-1, 2026-09-12
