---
tags:
- paradigm:bandit
- cognitive-modeling:pass
- psych-101
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---

# feng_2021_dynamics

- Paper: https://doi.org/10.1038/s41598-021-82530-8
- Data source: https://github.com/sffeng/horizon_ddm (archive: https://codeload.github.com/sffeng/horizon_ddm/tar.gz/refs/heads/master)
- PDF: https://www.nature.com/articles/s41598-021-82530-8.pdf
- Full text: https://www.nature.com/articles/s41598-021-82530-8
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Feng, S. F., Wang, S., Zarnescu, S., & Wilson, R. C. (2021). The dynamics of explore–exploit decisions reveal a signal-to-noise mechanism for random exploration. Scientific Reports, 11, 3077. doi:10.1038/s41598-021-82530-8

## Experiment summary
Two two-stage horizon "explore-exploit" decision-making experiments (N=31 pilot-v1, and N=29 repeater-v1, which repeats games across two presentations) where participants repeatedly choose between two slot machines whose reward means differ, under a short (1) or long (6) free-choice horizon that manipulates the value of information. Each game begins with 4 instructed trials followed by free choices; every trial yields a binary choice and a reaction time, with reward delivered per pull. The paper characterizes random exploration via a signal-to-noise (drift-diffusion) model fit jointly to choice and RT, testing whether exploration arises from decision noise versus reward sensitivity.

## Notes

### Columns

#### exp0

| column | description |
|--------|-------------|
| participant_id | Original integer subject number from source (subjectNumber), string; 1:1 with subjectID |
| trial | 0..N-1 within each (participant_id, task_id) — position within a game's trials |
| task_id | 0-indexed game number (source `game` is 1..320), a fresh 2-armed-bandit reset per participant |
| block | 0-indexed block (source `block` 1..4), 80 games per block |
| phase | Constant `test` (all recorded games are the main task; no practice rows in source) |
| forced_choice | 1 for the first 4 instructed trials of a game, 0 for free-choice trials |
| response | 0-indexed two-alternative choice: 0 = bandit with mean m1, 1 = bandit with mean m2 |
| reward | Integer points (1..100) delivered on winning that trial's pull |
| rt | Reaction time in milliseconds (source rt1..rt10 columns were seconds) |
| horizon | Free-choice horizon = gameLength - 4; 1 or 6 |
| gameLength | Total trials in the game (5 short-horizon or 10 long-horizon) |
| uc | Information condition 1/2/3: 1=[3 1], 2=[2 2], 3=[1 3] (times bandit1/bandit2 were forced) |
| m1 | Mean points of bandit 1 for this game (40 or 60, +/− increments) |
| m2 | Mean points of bandit 2 for this game |
| subjectID | Original source subject identifier (the .mat filename); used to join demographics |
| subjectNumber | Original integer subject number from source |
| age | Participant age in years from DDM_demographics.csv |
| gender | Participant gender (m/f) from DDM_demographics.csv |

#### exp1

| column | description |
|--------|-------------|
| participant_id | Original integer subject number from source (subjectNumber), string; 1:1 with subjectID |
| trial | 0..N-1 within each (participant_id, task_id) — position within a game's trials |
| task_id | 0-indexed game number (source `game` is 1..320), a fresh 2-armed-bandit reset per participant |
| block | 0-indexed block (source `block` 1..4), 80 games per block |
| phase | Constant `test` (all recorded games are the main task; no practice rows in source) |
| forced_choice | 1 for the first 4 instructed trials of a game, 0 for free-choice trials |
| response | 0-indexed two-alternative choice: 0 = bandit with mean m1, 1 = bandit with mean m2 |
| reward | Integer points (1..100) delivered on winning that trial's pull |
| rt | Reaction time in milliseconds (source RT columns were seconds) |
| horizon | Free-choice horizon = gameLength - 4; 1 or 6 |
| gameLength | Total trials in the game (5 short-horizon or 10 long-horizon) |
| uc | Information condition 1/2/3: 1=[3 1], 2=[2 2], 3=[1 3] (times bandit1/bandit2 were forced) |
| m1 | Mean points of bandit 1 for this game (40 or 60, +/− increments) |
| m2 | Mean points of bandit 2 for this game |
| gID | Game identity for the repeated-games design; pairs the two runs of a repeated game |
| repeatNumber | 1 or 2: which presentation of a repeated game (repeater experiment repeats games) |
| subjectID | Original source subject identifier (the .mat filename); used to join demographics |
| subjectNumber | Original integer subject number from source |
| age | Participant age in years from DDM_demographics.csv |
| gender | Participant gender (m/f) from DDM_demographics.csv |

The two experiments map to the paper's experiments as follows: exp0 = pilot-v1, exp1 = repeater-v1 (the repeated-games experiment). Trials are 0-indexed within each (participant_id, task_id). The `response` coding is 0 = bandit 1 (mean `m1`), 1 = bandit 2 (mean `m2`); `rt` was converted from seconds (source) to milliseconds, and `task_id`/`block` from 1-indexed source values to 0-indexed. `gID`/`repeatNumber` are omitted for exp0 (pilot-v1 has no repeated games, so these are all-NaN in the source); one repeater-v1 subject has a missing age in the source demographics.

## Text-format conversion

Both experiments (exp0 = pilot-v1, exp1 = repeater-v1) are the two-armed-bandit Horizon Task and were transcribed into text. The bandits are labeled A and B (response 0 = Bandit A, response 1 = Bandit B, mapping randomized per participant); games of 5 or 10 pulls, the first 4 instructed and the rest free. Each pull's reward is narrated. Nothing was skipped.

Sample transcript (exp0, participant 1, start through the first free choice):

```
You are playing a series of games with two slot machines, or bandits, labeled A and B. Each machine pays out points on each pull. On average, one machine is always better than the other, but you are not told which one, and the variability of the payouts is the same for both. Your goal is to earn as many points as possible. Each game lasts either 5 or 10 pulls; the number of slots on the bandits shows how long the game is. The first 4 pulls of every game are instructed: you are told which bandit to play and cannot play the other. After those, you freely choose which bandit to play each pull. On free pulls, press A to play Bandit A or B to play Bandit B.
A new game begins. It has 5 pulls.
Pull 1: you are told to play Bandit A. You win 66 points.
Pull 2: you are told to play Bandit A. You win 80 points.
Pull 3: you are told to play Bandit B. You win 29 points.
Pull 4: you are told to play Bandit A. You win 75 points.
Pull 5: you choose. You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments got a runnable `experiments/expN/` (exp0 = pilot-v1, exp1 = repeater-v1), built as static jsPsych v8 pages from the paper and CSV (no simulator was present). The headless round trip (`?mode=simulate`) passed for both: the produced CSV matches each `expN.csv` schema — same column names, dtypes, codings, 320 games/participant in 4 blocks of 80, `trial` restarting at 0 per `task_id`, `response` 0/1 coded by mean (0 = m1 bandit), `reward` = round(N(mean, 8)) clamped to [1, 99], and for exp1 `gID` present exactly twice with `repeatNumber` 1/2. Assumptions (browser-only, do not change the data/task): fixed A=left=m1 and B=right=m2 layout (the transcript randomizes the letter mapping per participant; response is coded by mean here); ~1200 ms new-game splash, 800 ms reward feedback, 400 ms ITI; machine colors/slot layout as cosmetic defaults. `subjectID`, `subjectNumber`, `age`, `gender` are left blank (source demographics not captured in a browser session).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Both experiments (exp0 = pilot-v1, exp1 = repeater-v1) got a text simulator: `simulate0.py` and `simulate1.py`, each generating 320 games per simulated participant from the paper's generative design (Methods: one bandit mean always 40 or 60, the other 4/8/12/20/30 points higher or lower; reward = round(N(mean, 8)) truncated to integers 1..100; first 4 pulls instructed; short/long horizons; uc 1:2:1). The round-trip check passed for both: `build_jsonl.py` run on each simulated `expN.csv` reproduces the simulator's prompts byte-identically. exp1 repeats each of its 160 games twice (repeatNumber 1/2 sharing gID, means, and the instructed pulls with their rewards; free-choice outcomes are redrawn). Per-participant A/B bandit labels are randomized with the same pid-seeded RNG as `build_jsonl.py`. Assumptions (data-grounded): the exact 320-game factorial and the exp1 repeated-game pairing were recovered from the CSVs; simulated `rt` and demographics (subjectID/subjectNumber/age/gender) are dropped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result: that random exploration in the Horizon Task is driven primarily by the signal-to-noise ratio (drift rate) and not the threshold, as shown by a value-based drift-diffusion model (DDM) fit jointly to first-free-choice choice and RT.
Fitted models: 10-parameter value DDM per (subject, horizon) (drift/threshold/bias linear in dR and dI, logistic bias link, non-decision time T0, noise SD fixed to 1; 20 parameters per subject) via per-subject MLE with bounded L-BFGS (Navarro-Fuss 2009 first-passage density, log-space), on the paper's 46-subject modeling sample (df = 45).
Reproduced: snr_decreases_with_horizon (t(45)=6.65, p<0.0001; paper t(45)=6.65); info_bonus_increases_with_horizon (t(45)=6.55; paper 6.55); threshold_decreases_with_horizon (t(45)=3.55, p<0.001; paper 3.55); sensitivity_snr_dominates (c_mu_R h6/h1 ratio 0.645 vs c_beta_0 ratio 0.933, paired p<0.0001; paper 0.645 vs 0.933).
Not reproduced: none.
Numeric mismatch: none — reproduced values match the paper's reported numbers to two decimal places.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 2, minor 5; fixed 4, open 3).

Checked: paper (doi:10.1038/s41598-021-82530-8, Nature PDF), original data (https://github.com/sffeng/horizon_ddm: allHorizonData_cut.csv + DDM_demographics.csv), exp0-exp1 (design vs. paper Methods p. 12: means 40/60 +/- 4/8/12/20/30, horizons 1:1, uc 1:2:1, 4 instructed pulls, 320 games in 4 blocks), transform re-run (both CSVs byte-identical), transcripts (build_jsonl.py rebuild byte-identical), simulators (run, build_jsonl.py round trip byte-identical, factorial and repeat structure cross-checked against the CSVs), modeling (partial, see below; the paper's exclusion rule, RT in (0.1, 3) s and >= 131 first free choices per horizon, reproduces model.py's 46-subject set exactly), analysis (both effects reproduce), logs. Skipped: modeling, full 46-subject fit (model.py timed out after 6 h on this 2-CPU node; the --max-participants 8 re-run finished in 95 min with conv=1.00, bnd=0.00 and all four effects in the paper's direction: c_mu_R 0.067 -> 0.049, c_mu_I -0.11 -> 0.38, c_beta_0 0.93 -> 0.83, ratio 0.813 vs 0.895; n=8 is too small for the t(45) tests. The full fit reproduced all four results in the auto-exp-modeling run and in the 2026-09-13 verification run on record under logs/).

Fixed:
- simulate0.py, simulate1.py: `_game_specs` indexed the information condition over the whole mean-condition block while horizon split that block in half, so simulated horizon-1 games only had uc 1/2 and horizon-6 games only uc 2/3; exp0.csv/exp1.csv cross horizon with uc fully (per participant 40/80/40 games in each horizon). Fixed by indexing uc within each horizon half; `-n 2 --seed 0` runs and the build_jsonl.py round trip stays byte-identical; the simulated cross-tab is now 1:2:1 in both horizons.
- simulate1.py and README (Simulators): in exp1.csv every repeated game (gID) replays the same 4 instructed responses and the same 4 instructed rewards on repeatNumber 2 (4640 of 4640 pairs), while free-choice rewards are redrawn (identical in 10% of same-choice pulls); the simulator redrew the instructed order and rewards and the README said 'redrawing rewards and free choices'. Fixed: the simulator stores the instructed order and rewards per gID on the first presentation and replays them on the repeat; the docstring ASSUMPTION and the README sentence were updated.
- README (Notes): replaced 'The `response` coding (0 = band-1, 1 = band-2) follows the matched `sadeghiyeh_2020_temporal` convention' with a self-contained statement (0 = bandit 1 with mean m1, 1 = bandit 2 with mean m2); this cross-reference was the source of every foreign-dataset string in the repo's logs.
- README (exp0 Columns, rt): '(source rt*RT columns were seconds)' -> '(source rt1..rt10 columns were seconds)'.

Open:
- minor: simulate1.py plays all 160 first presentations before the 160 repeats; exp1.csv presents each repeat 6..318 games after its first run (median 95; repeat-2 share per block 0.11/0.39/0.61/0.89). The paper does not describe the repeater design, so the ordering rule is not recoverable.
- minor: check_repo flags the string sadeghiyeh_2020_temporal in logs/auto-exp-{modeling,sim,transcribe,verify}.sessions.json and transcripts/auto-exp-{transcribe,verify}.log as cross-run contamination. Every hit quotes the README sentence fixed above (or a grep for it in the 2026-09-13 verification run); each export holds one root session whose first message names feng_2021_dynamics and each transcript ends with a result JSON naming it. Heuristic false positive; the audit logs were left unedited.
- minor: the paper (p. 12) reports '30 participants (11 male, 20 female, ages 18-24, mean 19.7)' and 'an additional 30 participants (9 male, 20 female, ages 18-50, mean 22.7)'; the source and the CSVs hold 31 (11 m, 20 f, 18-24, mean 19.7) and 29 (9 m, 20 f, 18-50, mean 22.7). The paper's gender counts sum to 31 and 29; the CSVs are faithful to the source (transform re-run byte-identical).

Run: claude-fable-5-1, 2026-09-14
