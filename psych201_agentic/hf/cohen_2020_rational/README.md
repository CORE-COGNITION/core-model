---
tags:
- paradigm:bandit
- cognitive-modeling:pass
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:needs-review
---
# cohen_2020_rational

- Paper: https://doi.org/10.1038/s41539-020-00075-3
- Data source: https://github.com/hartleylabnyu/dev-causal-inference (trial-level anonymized_mining_data.csv); also https://osf.io/mjy8w/ (supplement)
- PDF: https://www.nature.com/articles/s41539-020-00075-3.pdf
- Full text: https://www.nature.com/articles/s41539-020-00075-3
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Cohen, A. O., Nussenbaum, K., Dorfman, H. M., Gershman, S. J., & Hartley, C. A. (2020). The rational use of causal inference to guide reinforcement learning strengthens with age. npj Science of Learning, 5(1), 16. https://doi.org/10.1038/s41539-020-00075-3

## Experiment summary
A single two-armed reinforcement-learning task in 90 usable participants (N = 101 in the dataset; the 11 excluded are retained with valid=0) aged 7–25 years. On each of 150 trials (3 blocks of 50), participants chose between two mines (0/1), received binary gold/rocks feedback, and indicated a latent belief about whether a hidden agent caused the outcome. Three territory conditions (Robber/Millionaire/Sheriff) manipulated whether a hidden agent intervened on 30% of trials to cause negative, positive, or random outcomes. The question was whether rational use of inferred causal structure (discounting externally-caused outcomes) to guide RL strengthens with age; the authors fit computational RL models with mfit, so the data are suitable for cognitive modeling.

## Notes

### Columns

This dataset reflects a single experiment (exp0).

| column | description |
|--------|-------------|
| participant_id | Original subject number (1..101) from source CSV, as string. |
| trial | 0-indexed trial number 0..149 within each participant, sequential across all 3 blocks. |
| block | 0-indexed block number 0..2 (source block_num 1..3); each block is a territory. |
| trial_in_block | Raw 1-indexed position (1..50) of the trial within its block, kept as in source. |
| condition | Territory (hidden-agent) condition, mapped from source condition 1/2/3: 1=robber (agent causes negative outcomes), 2=millionaire (positive), 3=sheriff (random). |
| version | Task version label (A..F) = one of six territory/trial orders selected from 50 generated orders; kept as raw source string (mixed case; the authors' R code folds b/c/d into B/C/D). |
| mine_prob_win_left | Underlying probability (0.2/0.8) the left mine yields gold that block. |
| mine_prob_win_right | Underlying probability (0.2/0.8) the right mine yields gold that block. |
| response | Participant's mine choice: 1 = left mine, 0 = right mine (source subj_choice key; A/B in the transcripts). |
| feedback | Delivered outcome: 0 = rocks (loss), 1 = gold (win). Binary; no magnitude recorded in source. |
| latent_guess | Participant's belief about hidden-agent intervention (0/1), kept as raw source value. |
| optimal_choice | Whether the participant chose the better (0.8) mine that trial: 0 = no, 1 = yes (source key). |
| rt | Choice reaction time in milliseconds (source choice_RT was in seconds). |
| valid | 1 where the source marked the subject usable, 0 for the 11 unusable/excluded subjects (source usable=NaN; also NaN gender). |
| age | Participant age in years (continuous float). |
| age_group | Participant age band (kid/teen/adult), from source age_group. |
| gender | Participant gender mapped from source 0/1 codes (0=male, 1=female), unlabeled -> na. |

## Text-format conversion

exp0.csv was transcribed into transcripts0.jsonl (101 participants, one string each). Each trial renders the mine choice (response: A=left mine, B=right mine, following the source key where subj_choice 1=left/0=right) and the latent-agent attribution (latent_guess: Y=yes, N=no), both of which are free responses; the gold/rocks feedback is narrated as the outcome. No experiments were skipped.

Sample transcript:

```
You are a gold miner in the Wild West. Each time you find gold you earn a small real bonus; each time you find rocks you lose a small amount. On every trial you see two mines, one on the left and one on the right, and you choose one in which to dig. Within each block one mine gives gold most of the time and the other rarely does; the mines stay on the same side for the whole block, so try to figure out which mine is better and keep choosing it. Press A to choose the left mine or B to choose the right mine. After you choose, you see either gold or rocks appear in front of the mine you selected. You play in three different territories, each with its own hidden agent that sometimes intervenes. In millionaire territory a nice millionaire sometimes puts gold in both mines. In robber territory a mean robber sometimes replaces the gold with rocks. In sheriff territory a sneaky sheriff sometimes randomly puts rocks and gold in either mine. The hidden agents intervene only on a small number of trials. After every outcome you indicate whether you think the hidden agent caused that outcome by pressing Y for yes or N for no.
A new block begins. You are in millionaire territory.
You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

`simulate0.py` simulates the mining task (150 trials, 3 territories, hidden agents on 30% of trials; A/B mine choice and Y/N attribution are free responses, feedback is generated from the 0.8/0.2 base probabilities or the agent's forced outcome). The round-trip through `build_jsonl.py` matches the transcripts byte-for-byte after token normalization. `optimal_choice` follows the source key (1 = the chosen mine was the block's good (0.8) mine). `ASSUMPTION:` demographics are sampled from the shipped data distributions. No experiments skipped.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`experiments/exp0/` builds the mining task as a static jsPsych v8 experiment (instructions → 3 blocks × 50 trials). The headless `?mode=simulate` round trip passed: it reproduces the 17 exp0.csv columns exactly, all value codings, and 150 rows/participant, and no outbound data request fired in simulate mode. No experiments skipped. ASSUMPTIONs worth surfacing: `participant_id` is a generated session id (the shipped int64 subject numbers are the source's, not recoverable online); `version`/`valid`/`age`/`age_group`/`gender` are sampled from the shipped data's distributions as in `simulate0.py` (replace with a real demographics form in a deployment); `optimal_choice` is the block's good mine (the source definition is unrecoverable); the paper's experimenter-corrected practice phase is omitted. `rt` is filled from the browser, which the text simulator could not record.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: one_lr, two_lr, three_lr, empirical_bayesian_by_territory, adaptive_bayesian, noisy_bayesian, empirical_bayesian (per-participant MAP via jaxopt LBFGSB, 8 restarts, priors/bounds from fit_models.m); comparison on the paper's metric: PXP from random-effects BMS (Stephan 2009 / Rigoux 2014, ported from mfit_bms/bms.m) on -0.5*BIC per age group (90 participants: 30 kid, 30 teen, 30 adult).
Reproduced: children_best_model (one_lr, PXP 0.98 vs paper 0.98), adolescents_best_model (adaptive_bayesian, PXP 0.886 vs paper 0.89), adults_best_model (empirical_bayesian, PXP 0.748 vs paper 0.75).
Not reproduced: none.
Numeric mismatch: none (PXP values match the reported 0.98 / 0.89 / 0.75 to within ~0.01).
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: needs-review (critical 0, major 4, minor 5; fixed 5, open 4).

Checked: paper (https://doi.org/10.1038/s41539-020-00075-3), original data (https://github.com/hartleylabnyu/dev-causal-inference anonymized_mining_data.csv; OSF mjy8w holds only the supplement PDF), exp0, transform re-run, transcripts, simulators, modeling, analysis, logs. Skipped: none.

Fixed:
- README Columns table gave response as 0 = left / 1 = right; the source key is subj_choice 0 = right, 1 = left (exp0.csv: P(gold | response=1, left mine good) = 0.71; build_jsonl.py maps 1 to A = left). Row corrected.
- README Columns table described optimal_choice as the side of the better mine (0 = left, 1 = right); the source key is 'whether the subject chose the better mine (0 = no, 1 = yes)', and the raw CSV matches that definition on all 15147 rows (mean 0.80). Row corrected.
- simulate0.py wrote optimal_choice as the block's good side and its docstring said the source definition was not recoverable; it is in the source README. The simulator now records 1 when the chosen mine is the 0.8 mine; the README Simulators sentence follows; smoke test (-n 2 --seed 0) and the build_jsonl.py round trip re-verified byte-identical.
- README Experiment summary had no 'N = <count>' phrase; now 'N = 101 in the dataset' (90 valid = 1, 11 valid = 0), matching exp0.csv.
- README version row said 'one of 50 generated trial orders'; the paper (p. 7) selected six versions from 50 generated orders, and the authors' R code folds the lowercase b/c/d labels into B/C/D. Wording corrected; values kept raw.

Open:
- major: each exp0.csv row holds two free responses (response = mine choice, latent_guess = yes/no attribution), so every transcript marks 300 responses against 150 rows (check_repo). schema.md asks for one row per response. Data and transcripts are complete and consistent; restructuring would change exp0.csv, transcripts0.jsonl, simulate0.py, model.py, analysis.py and the out-of-scope experiments/, so it is left for review.
- minor: the paper (p. 6) excludes 12 additional participants; the source ships 11 subjects with usable = NaN (kept with valid = 0, age NaN, gender na). Inside the source.
- minor: the paper (p. 7) describes 5 directed practice trials plus 5 practice trials per territory; the source CSV contains no practice rows. Not in the source.
- minor: participant 40 has 147 trials (trial_num 148-150 absent in the source); all other participants have 150. Inside the source.

Run: claude-fable-5-1, 2026-09-09
