---
tags:
- paradigm:bandit
- cognitive-modeling
- psych-201
- js-experiment:pass
- text-format:pass
- simulator:pass
---
# giron_2023_developmental

- Paper: https://doi.org/10.1038/s41562-023-01662-1
- Data source: https://github.com/AnnaGiron/developmental_trajectory
- PDF: https://www.nature.com/articles/s41562-023-01662-1.pdf
- Full text: https://www.nature.com/articles/s41562-023-01662-1
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Giron, A. P., Ciranka, S., Schulz, E., van den Bos, W., Ruggeri, A., Meder, B., & Wu, C. M. (2023). Developmental changes in exploration resemble stochastic optimization. Nature Human Behaviour. https://doi.org/10.1038/s41562-023-01662-1

## Experiment summary
Participants perform a 2D spatial (8x8) multi-armed bandit task with 40 smooth reward environments, choosing among 64 locations per round across ~208 trials. Behavioral exploration is compared across three experiments spanning ages 5–55: a new adolescent sample (Experiment 1, N=150) plus re-analyses of the Schulz (2019) bandit dataset (Experiment 2, N=79) and the Meder (2021) bandit dataset (Experiment 3, N=52). Each trial records the chosen tile coordinates, its reward, the distance moved from the previous choice, and a Repeat/Near/Far choice category under smooth (vs. rough) reward environments. The study asks whether developmental changes in exploration (both random and directed) resemble a stochastic hill-climbing / GP-UCB optimization process, fitting formal GP-UCB and lesioned cognitive models across ages. The response type is a continuous spatial choice per trial.

## Notes

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number (1..150) from source CSV, kept as string. |
| task_id | 0..7, one per round/environment (source `round` 2..9 minus 2); each round is an independent fresh reward environment (task reset). |
| trial | 0..25 within each (participant_id, task_id), source trial 0-indexed. |
| response | 0-indexed flat index of the chosen tile on the 8x8 grid (= `chosen`-1, equivalently y*8+x), 0..63. Divergence note: source stores 1-indexed `chosen`; response is that minus one for 0-indexing. |
| x | Column coordinate (0..7) of the chosen tile. |
| y | Row coordinate (0..7) of the chosen tile. |
| chosen | Raw 1-indexed flat tile index from source (1..64). |
| z | Raw reward at the chosen tile (smooth-kernel value, can be slightly negative). |
| zscaled | Reward normalized/scaled to ~[3,47] used for the paper's normalized-reward analyses. |
| time | Unix timestamp (epoch ms) of the trial; gives true presentation order. |
| round | Source round/environment number (2..9). |
| distance | Euclidean/Manhattan distance moved from previous choice (NaN on the first trial of a round). |
| type_choice | Choice category derived from distance: Repeat / Near (dist 1) / Far (dist >1), NaN on first trial. |
| previous_reward | Reward of the previously chosen tile (NaN on first trial). |
| experiment | Dataset label, constant = "Adolescent". |
| age_years | Participant age in years (5..55). |
| age_months | Participant age in months. |
| gender | Canonical code f/m from source "Female"/"Male". |
| age_group | Age band as snake token (5_7, 7_9, 9_11, 11_14, 14_18, 18_25, 25_55), derived from source bracket label. |
| condition | Environmental roughness condition, constant = "Smooth". |
| duration | Session duration in minutes. |

### exp1
Same columns as exp0, but experiment = "Schulz (2019)", participant_id 1..79, age_group only child/adolescent bands (5_7..14_18).

### exp2
Same columns as exp0/exp1, but experiment = "Meder (2021)", participant_id 1..52, task_id 0..3 (only 4 rounds), age_group = 18_25 / 25_55, and the `time` column is absent (source recorded no timestamps for this dataset).

## Online experiment

Static jsPsych v8 ports of the three bandit experiments were added under `experiments/`
(`exp0/`, `exp1/`, `exp2/`), one folder per experiment. Each builds a CSV in the dataset's
own long-format schema on completion (offered as a download; no collection backend). The
headless `?mode=simulate` round trip passed for all three: column names, 0-indexed
`task_id`/`trial`/`response`, `chosen = response + 1`, `round = task_id + 2`, and the
round×trial row counts all match the matching `expN.csv`; reward values (`z` ≈[0,50],
`zscaled` ≈[5,45]) match the paper's generative process.

Assumptions worth surfacing: reward environments are generated fresh per round from the
paper's Gaussian-process kernel (RBF, `λ = 4`) rather than replaying the 40 raw
environments, because the per-round environment assignment was not recoverable. No verbatim
participant instruction text was available, so the on-screen instructions were reconstructed
from the paper's Methods. The paper's excluded training and bonus rounds are not reproduced
(a short unlogged practice click is included instead). Grid colours, feedback/ITI timings and
the between-round stars display are cosmetic defaults.

## Text-format conversion

All three experiments (`exp0.csv`, `exp1.csv`, `exp2.csv`) were transcribed; none were
skipped. Each is the same spatially-correlated 8x8 bandit: a participant picks a tile each
trial and sees its reward, exploring a smooth reward map to maximize cumulative reward.
Expressing each trial as "you pick tile (row,column) and gain N reward" preserves exactly
the information participants used (chosen tile rewards plus spatial adjacency), so the
search/exploration task is textifiable. The three experiments share a design and differ
only in round count (8, 8, 4).

Sample transcript (exp0), verbatim from the start through the first response:

```
You are searching an 8 by 8 grid of 64 tiles to collect as many rewards as possible. The grid has 8 rows and 8 columns, numbered 0 to 7 (row 0 is the top row, column 0 is the leftmost column). Every tile hides a reward value. Rewards are smooth: tiles near each other tend to give similar rewards, so a tile close to a tile that paid well is probably also good, and you can search for high-reward tiles by moving around the grid. A tile's value is only revealed after you pick it, so you may visit new tiles or return to ones you have seen before. The reward you receive on a tile is a number from about 5 to 45. You play 8 rounds; in each round a fresh reward map is set out and you get 26 tiles worth of choices to gather as many rewards as possible. On every trial, pick the tile you want by typing its coordinates as row,column - that is, the row number (0 to 7) followed by a comma followed by the column number (0 to 7). For example, type 2,4 to choose the tile in row 2, column 4. After you pick a tile, its reward value is shown to you.
Round 1: you pick tile (4,1). You press [HUMAN_RESPONSE]4,1[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Text simulators were written for all three experiments (`simulate0.py`, `simulate1.py`,
`simulate2.py`) and the round-trip check passed: regenerating `transcriptsN.jsonl` from each
simulated `expN.csv` via `build_jsonl.py` yields byte-identical text to the simulator's own
prompts. Each `SpatialBandit` draws fresh reward environments per round from the paper's
Gaussian-process kernel (RBF, λ = 4), with `z = round(50·env[tile] + N(0,1))` and
`zscaled = round(5 + (maxRange/50)·z)`, `maxRange ~ U(30,40)`. DataFrame columns mirror
`expN.csv` minus session/demographic fields. ASSUMPTIONS: trial 0 (the task's forced reveal)
is narrated identically by `build_jsonl.py`, so it is simulated as a free first choice;
reward environments are sampled fresh per round because the per-round assignment of the raw
environments was not recoverable.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25