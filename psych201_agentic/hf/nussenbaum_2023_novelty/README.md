---
tags:
- paradigm:bandit
- cognitive-modeling:fail
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---
# nussenbaum_2023_novelty

- Paper: https://doi.org/10.7554/eLife.84260
- Data source: https://osf.io/cwf2k/
- PDF: https://elifesciences.org/articles/84260.pdf
- Full text: https://elifesciences.org/articles/84260
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Nussenbaum, K., Martin, R., Maulhardt, S., Yang, Y., Bizzell-Hatcher, G., Bhatt, N. S., König, M., Rosenbaum, G., O'Doherty, J. P., Cockburn, J., & Hartley, C. A. (2023). Novelty and uncertainty differentially drive exploration across development. eLife, 12, e84260. https://doi.org/10.7554/eLife.84260

## Experiment summary
One experiment (exp0, N = 122) with participants aged 8–27. In each of 10 blocks (~15 trials each), a creature hid a coin under one of two presented stimuli and participants chose between the two; reward probabilities were re-randomized per block and the design decoupled novelty (how many times a stimulus had been seen) from uncertainty (the spread of the belief about reward). Trial-level data include the binary choice, RT, reward outcome, per-block reward probabilities, and cumulative selection/rejection/win/loss/exposure histories per stimulus, plus a surprise memory test after the task. Participants also completed WASI IQ subtests. The research question was how age moderates novelty-seeking vs. uncertainty-aversion as drivers of exploration, tested with computational reinforcement-learning models.

## Notes

### Columns

#### exp0

Both tasks from the novelty/uncertainty exploration study are in one file, distinguished by `task_id`.

| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSVs (`subID`), as string |
| task_id | 0..9 = the 10 exploration blocks (each a fresh creature = task reset; reward probs re-randomized per block); 10 = surprise memory test |
| trial | 0..14 within each exploration (participant_id, task_id); 0..9 within memory test (participant_id, task_id) |
| response | Exploration: 0 = chose `trialStimID_1`, 1 = chose `trialStimID_2`; NaN where no response (timeout). Memory: 0..4 = array position chosen (source `respKey` 1..5 minus 1); indexes into `choice_set`. |
| rt | Exploration reaction time in milliseconds (source `RT` in seconds). Memory: empty (no RT recorded). No-response trials carry the ~4000 ms timeout value. |
| reward | 1 = coin found, 0 = no coin (exploration). Empty for no-response trials and for memory-test rows. |
| valid | 1 = response recorded; 0 = exploration trial where the participant failed to respond within 4 s (`selectedStimID` empty) |
| phase | `exploration` for the main task rows, `memory` for the surprise memory-test rows |
| choice_set | JSON list of the hiding-spot image files the participant chose from, in presentation order; `response` indexes into it. Exploration: the two presented spots (stimulus ID → image from source `explo_stim_data.csv`; empty for the 2 participants without a memory-task file). Memory: the 5 array options. |
| age | Participant age in years (decimal, from source `age`) |
| gender | `f` / `m` / `nb`, lowercased from source `sex` |
| iq | WASI full-scale IQ estimate (source `IQ`) |
| WASI_mrT | WASI matrix reasoning T score |
| WASI_rawMR | WASI matrix reasoning raw score |
| WASI_rawV | WASI vocabulary raw score |
| WASI_verbalT | WASI vocabulary T score |
| blockID | Source block number, 1..10 (== task_id+1) |
| block_difficulty | 0/1 block-difficulty flag from `explo_block_difficulty.csv` (half easy, half hard blocks) |
| correct | Memory test only: 1 if the chosen array position held the creature's favorite (high-reward) hiding spot; empty on exploration rows |
| explorationBlock | Memory test only: which exploration block/creature (1..10) the memory probe refers to |
| numBlockStims | Number of stimulus slots available in that block (2 or 3) as recorded by the source |
| selectedStimID | Exploration: stimulus ID (1..12) the participant chose that trial; NaN where no response |
| rejectedStimID | Exploration: stimulus ID (1..12) not chosen that trial |
| trialStimID_1 | Exploration: stimulus ID (1..12) of the first presented choice option |
| trialStimID_2 | Exploration: stimulus ID (1..12) of the second presented choice option |
| trialID | Source trial number within block, 1..15 (== trial+1 within each task_id) |
| reward_probs_1..12 | Scheduled win frequency of each of the 12 possible stimuli within that block (source `reward_probs` = mean of the pre-drawn outcome schedule over the block's first 14 trials, so multiples of 1/14; nominal probabilities were 0.8/0.5/0.2 in easy and 0.7/0.5/0.3 in hard blocks); constant across the block, zero for stimuli not used in the block |
| selectHistory_b_1, selectHistory_b_2 | Cumulative count of selections of the first/second trial stimulus up to (and including) the current trial, per source (`selectHistory_*_t_*`) |
| selectHistory_t_1, selectHistory_t_2 | Source's per-trial selection-history variant for the two trial stimuli (carried verbatim) |
| rejectHistory_b_1, rejectHistory_b_2 | Cumulative count of rejections of the two trial stimuli up to the current trial |
| rejectHistory_t_1, rejectHistory_t_2 | Source's per-trial rejection-history variant for the two trial stimuli |
| winHistory_b_1, winHistory_b_2 | Cumulative win count for the two trial stimuli up to the current trial |
| winHistory_t_1, winHistory_t_2 | Source's per-trial win-history variant for the two trial stimuli |
| lossHistory_b_1, lossHistory_b_2 | Cumulative loss count for the two trial stimuli up to the current trial |
| lossHistory_t_1, lossHistory_t_2 | Source's per-trial loss-history variant for the two trial stimuli |
| exposureHistory_b_1, exposureHistory_b_2 | Cumulative number of times each trial stimulus has been seen up to the current trial |
| exposureHistory_t_1, exposureHistory_t_2 | Source's per-trial exposure-history variant for the two trial stimuli |
| nativeEnglish | 1 = native speaker of English, 0 = otherwise (source `nativeEnglish`) |
| memData | 1 = participant completed the memory test (has memory rows), 0 = excluded due to technical error |
| highRewImage | Memory test: filename of the creature's favorite (correct) hiding spot among the 5 options |
| medRewImage | Memory test: filename of the creature's second-favorite hiding spot |
| lowRewImage | Memory test: filename of the creature's least-favorite hiding spot |
| highRewDiffImage | Memory test: filename of a hiding spot encountered in a *different* block |
| newImage | Memory test: filename of a hiding spot never presented in the exploration task |
| imageOrder_1..5 | Memory test: permutation of 1..5 giving which option (1=highRew, 2=medRew, 3=lowRew, 4=highRewDiff, 5=new) was displayed in each of the 5 array positions |

Notes:
- Divergence from `Hugging-Brain/nussenbaum_2024_sensitivity`: that dataset's `response` held a single task's raw key presses; here we code the 2-alternative exploration choice as 0/1 (first/second presented option) and the 5-alternative memory choice as 0..4 (array position, source key minus 1), because the source records chosen/rejected stimulus IDs rather than left/right key responses.
- The exploration task is modeled per block (each creature re-randomizes reward probabilities and participants are told to reset), so each block is its own `task_id` with a fresh `trial` counter.
- 2 participants lack memory-test rows; 85 no-response exploration trials keep RT but empty response/reward with `valid=0`.

## Text-format conversion

`exp0.csv` was transcribed (`transcripts0.jsonl`, one line per participant). Both the 10-block exploration task (a 2-alternative coin-search choice with per-block re-randomized reward probabilities) and the surprise memory test (a 5-alternative recall of each creature's favorite hiding spot) are textifiable: the hiding spots are nameable, identifiably repeated choice options (by image name via `choice_set`; by source stimulus ID for the 2 participants without one), so describing them by label preserves the trial-and-error reward learning and the subsequent recall judgment. No experiments were skipped.

Sample transcript (exp0, participant 501, start through the first response):

```
An enchanted kingdom needs gold coins to build a bridge to unite two sides. Various creatures have hidden coins in hiding spots around different territories. On each trial you search one of two hiding spots for a coin. Each creature has its own favorite hiding spots, which stay stable throughout its block, but a creature does not always hide its coin in its favorite spot. Every new creature has different favorite spots, so the odds reset at each new block.

Block: a new creature hides coins in a new territory. Its favorite hiding spots are unknown to you.
You see rockPile and yellowTree (A = the first spot, B = the second). You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

`simulate0.py` reproduces exp0 (10-block novelty/uncertainty exploration + surprise memory test). The round-trip check passed: running `build_jsonl.py` on the simulated `exp0.csv` regenerates transcripts byte-identical to the simulator's prompts. Design constants (EASY/HARD reward probs, block difficulty pattern, holdout trials, 2-of-3 spot pairs) follow the paper and the OSF task code. Assumptions: familiar spots are "offered > 2 times" (threshold differs from the source's exact novelty bookkeeping) and no response-timeout rows are simulated. Columns match `exp0.csv` minus `rt` and demographics/psychometrics.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: six forgetful-Bayesian RL models (baseline, novelty_bias, uncertainty_bias, novelty_unc, famgate_unc, gate_novelty) fit per participant by MAP with the paper's prior N(0, 6.25); the paper's hierarchical PXP model selection is approximated by per-participant BIC-weight exceedance probability.
Reproduced: children novelty bias (novelty_bias model; mean fitted N = 0.975, one-sample t = 5.45, p < .001; paper 1.49, p < .001).
Not reproduced: adolescent uncertainty aversion (famgate_unc model wu: adults -1.29, p < .001, but adolescents -0.39, p = .20, n.s.; paper -0.15 both groups, p ≤ .001); per-age-group winning model (under per-participant BIC/AIC, the baseline model is most frequent in all three age groups, including children, vs paper's novelty_bias for children and familiarity-gated uncertainty model for adolescents and adults).
Numeric mismatch: children novelty bias 0.975 vs 1.49; ado/adult wu -0.39/-1.29 vs -0.15.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`experiments/exp0/` reproduces the full two-part task (10-block exploration + surprise memory test) as a static jsPsych v8 experiment (no simulator was present, so it was built from the paper, the OSF task code, and the CSV/transcripts). The headless round trip ran in `?mode=simulate`: the saved CSV matched `exp0.csv`'s schema exactly (69 columns, 160 rows = 150 exploration + 10 memory, 0-indexed counters, 15 trials per block with `trial` restarting per `task_id`, correct block-difficulty pattern, 5 distinct images per memory probe) and no outbound data request was fired. The memory-test lure is drawn from a *different* block and never from the current block's three hiding spots, as in the source.

Assumptions (browser-only and cosmetic; noted above the `<script>`): demographics/age/`gender`/`nativeEnglish` and WASI columns are left empty because the browser task does not collect them; response window 4000 ms, feedback 1500 ms, 500 ms ITI, and a minimal block-start/block-end screen are presentation defaults.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 1, major 4, minor 7; fixed 9, open 3).

Checked: paper (https://doi.org/10.7554/eLife.84260, PDF), original data (https://osf.io/cwf2k/ -> GitHub addon katenuss/exploration: data/explo_*.csv and 122 + 120 raw .mat files), exp0, transform re-run (byte-identical to the uploaded exp0.csv before the fixes), transcripts (build_jsonl.py rebuild byte-identical), simulator (smoke run and 3/3 round trip through build_jsonl.py), modeling section against the cognitive-modeling:fail tag and the paper (pp. 7-8; no model.py to re-run because the modeling stage ships none on fail), analysis (4/4 effects reproduce), logs. Skipped: none.

Fixed:
- critical: 101/122 transcripts failed the one-to-one token check: memory-test token 1 and exploration token B both mapped to CSV response 1. Memory responses are now 0-indexed and the five memory options are labeled A-E in build_jsonl.py and simulate0.py; exp0.csv and transcripts0.jsonl regenerated.
- major: memory `response` held the source key 1..5; the schema codes an N-alternative choice 0-indexed. transform.py now writes respKey - 1 (0..4); `correct` is unchanged.
- major: exploration lines named hiding spots by stimulus ID (Spot 9) while the memory probes list image names, so the memory test was unanswerable from the transcript. transform.py now reads the source's explo_stim_data.csv (stimNum -> image; its high/med/low images match the block reward ranks 1200/1200) into a `choice_set` column for exploration and memory rows; build_jsonl.py and simulate0.py name the spots by image. Participants 500 and 503 (no memory-task file) keep the Spot-ID naming.
- major: 10 README history rows written as `x_1 / _2` left the `_2` columns undocumented; rows now read `x_1, x_2`.
- major: the runner's first-message summary.diffs in logs/auto-exp-modeling.sessions.json and logs/auto-exp-transcribe.sessions.json carried a README patch from another run (vantiel_2022_meaning; gnther_2022_patterns); those entries were pruned.
- minor: Columns heading `### exp0` -> `#### exp0`.
- minor: Experiment summary now states `exp0, N = 122`.
- minor: `reward_probs_*` were described as true reward probabilities; the source (flattenTaskData.m line 48) stores the mean of the pre-drawn outcome schedule over the block's first 14 trials (values in 1/14 steps, e.g. 0.786 not 0.8). Description corrected.
- minor: modeling section typo `fampate_unc` -> `famgate_unc`; the adults' uncertainty-bias p is .001 in the paper (p. 8), now written p <= .001.

Open:
- minor: check_repo flags `nussenbaum_2024_sensitivity` in every log; the mention is this README's own cross-reference note (Notes bullet), read by each stage, not content from another run. Left as is.
- minor: check_repo flags `nussenbaum_2023_n` in the modeling log; it is a streaming-truncated fragment of this dataset's own name in one text part. Left as is.
- minor: the paper (p. 11) describes two practice blocks; neither the source CSVs nor the raw .mat task structs (2 sessions x 5 blocks) contain practice trials, so exp0.csv has none.

Run: claude-fable-5-1, 2026-09-13
