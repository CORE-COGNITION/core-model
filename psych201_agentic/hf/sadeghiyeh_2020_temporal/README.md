---
tags:
- paradigm:bandit
- cognitive-modeling:pass
- psych-101
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:pass
---

# sadeghiyeh_2020_temporal

- Paper: https://doi.org/10.1038/s41598-020-60576-4
- Data source: https://github.com/hashem20/temporal-discounting-explore-exploit
- PDF: https://www.nature.com/articles/s41598-020-60576-4.pdf
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Sadeghiyeh, H., Wang, S., Alberhasky, M. R., Kyllo, H. M., Shenhav, A., & Wilson, R. C. (2020). Temporal discounting correlates with directed exploration but not with random exploration. Scientific Reports, 10(1), 4020. https://doi.org/10.1038/s41598-020-60576-4

## Experiment summary
82 human participants (N=82) completed the 27-item Delay-Discounting Questionnaire (Kirby et al.) to estimate temporal discounting (k), and the two-armed bandit Horizon Task (256 allocated game slots per session, 25–160 games actually played; horizon 1 or 6; forced then free trials; varied mean rewards and uncertainty) to quantify directed and random exploration from per-trial choices, RTs, and rewards. exp0 contains Horizon-task trial data (57,040 rows; 82 subjects), and exp1 contains the per-item questionnaire choices and estimated discounting rates (2,214 rows; 82 subjects). The paper reports that greater temporal discounting correlates with less directed exploration — driven by lower uncertainty seeking at short (horizon 1) games — but not with random exploration; analyses fit a logistic RL model with an information-bonus and decision-noise parameter and then test individual-difference correlations with k.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number from the Horizon-task .mat filename (e.g. `164` from `P017_horizontask_sub164_...mat`), matching the last 3 digits of the questionnaire Subject ID. |
| task_id | 0-indexed game slot within the 256 allocated games of the Horizon task; each game is a fresh 2-armed bandit (new means, new reward schedule, forced trials then free draws) so `trial` restarts per game. Only games that were actually played are present (source recorded no trials for empty tail slots). |
| trial | 0-indexed draw within the game (0..game_length-1). |
| horizon | Number of free draws after the forced phase (1 = short, 6 = long); equals game_length - 4. |
| phase | Always `test` (main task; no practice phase in source). |
| forced_choice | 1 if this draw was experimenter-instructed (forced trial, `forced_trial` != 0), 0 if a free choice. |
| response | 0-indexed bandit choice: 0 = bandit A (the option whose mean is `mean_A`), 1 = bandit B (`mean_B`). Derived from raw `key` (1/2) minus 1. |
| rt | Reaction time in milliseconds (source `RT` seconds × 1000), from bandit onset to key press. |
| reward | Points delivered on this draw (source per-trial `reward` array, equal to the chosen bandit's row of the schedule). |
| correct | 1/0 whether the draw rewarded at least as much as the alternative bandit's scheduled value at that position; ties count as correct (source `correct`). |
| key | Raw response key code: 1 = bandit A, 2 = bandit B (1-indexed source coding). |
| forced_trial | Raw per-trial forced instruction: 0 = free draw, 1 or 2 = the bandit (key) the participant was instructed to pick. |
| mean_A | Expected value of the mean of bandit A's reward distribution (points, e.g. 60). |
| mean_B | Expected value of the mean of bandit B's reward distribution (points). |
| mean_offered | JSON list `[mean_A, mean_B]` of the two bandit means offered this game (raw `mean` field). |
| rewards_schedule | JSON nested list `[[bandit A draws...],[bandit B draws...]]`, the pre-generated reward outcome for each draw of each bandit in this game (raw `rewards` field, uint8 points). |
| game_length | Total draws in the game (10 for horizon 6, 5 for horizon 1). |
| nfree | Number of free draws in the game (= horizon). |
| nforced | JSON list of the bandit (1 = A, 2 = B) the participant was instructed to play on each of the four forced trials (raw `nforced` field, e.g. `[1,2,1,2]`; equals `forced_trial` on trials 0-3). |
| gID | Game identity counter from the source (per-trial repeated within a game). |
| correct_total | Total number of correct draws in the game (source `correcttot`). |
| accuracy_game | Game-level accuracy = correct_total / nfree (source `accuracy`; renamed from `accuracy` to avoid the reserved schema name). |
| time_bandit_on | MATLAB clock time (seconds) the bandit display appeared (raw `timeBanditOn`, absolute timestamps). |
| time_press_key | MATLAB clock time (seconds) the key press occurred (raw `timePressKey`). |
| time_reward_on | MATLAB clock time (seconds) the reward display appeared (raw `timeRewardOn`). |
| delta_time_press_key | Per-trial duration (seconds) of the key-press response window / between-event interval (raw `deltatimePressKey`). |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Participant ID = last 3 digits of the questionnaire Subject ID, matching `participant_id` in exp0 (e.g. `164`). |
| trial | 0-indexed MCQ item position within the questionnaire (0..26). |
| phase | Always `questionnaire` (the 27-item delay-discounting questionnaire, Kirby et al. 1999). |
| item_id | 1-indexed MCQ item number (1..27), matching the `td_N` column of the source spreadsheet. |
| response | Delay-discounting choice: 0 = smaller-sooner / today, 1 = larger-later (raw `td_N` coding). |
| age | Participant age in years (source column `age`). |
| gender | Participant sex, `m` = male / `f` = female (source coded 1 = male, 2 = female). |
| overall_k | Temporal discounting rate k estimated from all 27 items (source `Overall k`). |
| small_k | Discounting rate k for small-magnitude items (source `Small k`). |
| medium_k | Discounting rate k for medium-magnitude items (source `Medium k`). |
| large_k | Discounting rate k for large-magnitude items (source `Large k`). |
| geomean_k | Geometric mean of the small/medium/large k values (source `Geomean k`). |
| temporal_today | Count of `today` (immediate) choices across the 27 items (0..27, source `temporal_today`). |

The Horizon-task raw `.mat` files are MATLAB R2017b+ structs; only played games (with recorded trials) are emitted, so unplayed tail game slots are omitted, implying `task_id` may not be contiguous up to 255 for every subject. Gender maps from the source's 1 = male / 2 = female coding.

## Text-format conversion

Both experiments were transcribed. `exp0.csv` (Horizon Task, two-armed bandit games) was textified as sequences of draws — forced draws narrated plainly, free draws marked with the chosen machine (`A`/`B`) plus the points won. `exp1.csv` (27-item Delay Discounting Questionnaire) was textified using the verbatim item wording from the task materials, marking each today/later choice (`T`/`L`). No experiments were skipped.

**Sample transcript (exp1, participant 164):**
```
You will answer 27 questions about money. In each question you choose between a smaller amount available today and a larger amount available later. You have a 1 in 4 chance of actually receiving a payment based on the preferences you indicate; if you do receive payment, the question on which it is based is chosen at random. The 'today' choice would be paid out as soon as you complete the study, while the 'later' choice would be paid out after the number of days indicated in that question. For each question, press T for 'today' or press L for 'later'.
Question 1: Would you prefer $54 today or $55 in 117 days? You press [HUMAN_RESPONSE]T[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: Horizon-task logistic model (per 1-3/2-2 condition x horizon 1/6) with information-bonus (alpha), spatial-bias (B) and decision-noise (sigma) parameters, per-participant bounded MLE with weak regularising priors (Gaussian on alpha, exponential on sigma; multi-start L-BFGS-B); primary checks are Pearson correlations of fitted model parameters with log k.
Reproduced: model_directed_vs_discounting, model_random_vs_discounting, model_info_bonus_h1_vs_discounting, model_info_bonus_h6_vs_discounting.
Not reproduced: none.
Numeric mismatch: none (model-based r: directed -0.234, random +0.083, info-bonus h1 +0.272, info-bonus h6 -0.020; consistent with the paper's Fig. S2 model-based pattern mirroring the model-free Table 3 correlations).
Partial validation: (none; full 82-participant fit).
Indeterminate: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

Both experiments got a text simulator: `simulate0.py` (Horizon Task) and `simulate1.py` (27-item Delay Discounting Questionnaire). The round-trip check via `build_jsonl.py` passes byte-identically for both (modulo the random draws and agent choices). ASSUMPTION (exp0): reward schedule = clip(round(N(mean, 8)), 1, 99) per the paper's S.D.-of-8 and the data's observed min/max; bandit means are sampled via the paper+data's anchor model (anchor 40 or 60 plus an offset of ±4/8/12/20, random A/B assignment); correct = chosen reward >= the alternative's scheduled reward at the same position (ties count as correct). The simulators drop rt, gID, timing columns, and the questionnaire's demographics/k scores as not text-producible.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments got an online port under `experiments/` (`exp0/` Horizon Task,
`exp1/` Delay Discounting Questionnaire), built from the simulators. The headless
`?mode=simulate` round trip passed for both: schema, codings, and design counts
match `exp0.csv` / `exp1.csv` (a random agent is statistically indistinguishable
from `simulate0.py`; exp0's anchor mean set and reward residual SD ≈ 8 match the
data). No experiment was skipped and no data-changing assumption was made. Exp0
drops the tool-only columns `gID` and the four absolute MATLAB clock-time columns
(browser-unproducible) and fills `rt`; `correct_total`/`accuracy_game` follow the
actual `exp0.csv` convention (game-final correct free draws) rather than the text
simulator's running total. Exp1 does not produce the questionnaire demographics/k
scores (they need the MCQ scorer and a demographics phase the design lacks).
Cosmetic browser defaults (colors, timings, layout, 160-game session) are noted in
`experiments/README.md`.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 1, minor 4; fixed 5, open 0).

Checked: paper (https://doi.org/10.1038/s41598-020-60576-4, PDF + supplementary materials), original data (https://github.com/hashem20/temporal-discounting-explore-exploit: 82 .mat files, Temporal_Discounting_Scores.xlsx, main.m, the 27-item questionnaire docx), exp0-exp1, transform re-run, transcripts, simulators, modeling, analysis, logs. Skipped: none.

Fixed:
- README summary said the Horizon Task had 256 games per participant; the source .mat files hold 256 allocated slots but 25-160 played games per participant (7,597 games in exp0.csv).
- README described `correct` as rewarding more than the alternative; in the data correct = 1 whenever the chosen reward is at least the alternative's scheduled reward (1,153 tied draws are coded correct).
- README described `nforced` as per-trial instruction counts; it is the forced-bandit sequence of the four forced trials (equals `forced_trial` on trials 0-3 in every game).
- analysis.py computed p(low mean) from the generative means (mean_A vs mean_B); the paper's main.m uses the observed forced-draw means and skips tied games. Fixed: p(low mean) h1/h6 now 0.2883/0.3554, t(81) = 3.87, 57 participants with random exploration (paper Table 1 and p. 4), and the random-exploration correlation is r = 0.040, p = 0.720 (Table 3). All three effects still reproduce.
- README modeling section said bounded MLE and model.py said fmincon in the paper; the objective adds weak priors (Gaussian on alpha, exponential on sigma) and neither the paper nor the supplement names an optimizer. Wording corrected; model results unchanged.

Open:
- none.

Run: claude-fable-5-1, 2026-09-12
