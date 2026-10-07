---
tags:
- paradigm:creative-exploration-game
- cognitive-modeling:needs-review
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
---
# brndle_2023_empowerment

- Paper: https://doi.org/10.1038/s41562-023-01661-2
- Data source: https://github.com/franziskabraendle/alchemy_empowerment (also https://keeper.mpdl.mpg.de/d/28c50dc3a6bf4d10995d/ and https://zenodo.org/record/8010316)
- PDF: https://gershmanlab.com/pubs/Brandle23.pdf
- Full text: https://www.nature.com/articles/s41562-023-01661-2
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Brändle, F., Stocks, L. J., Tenenbaum, J. B., Gershman, S. J., & Schulz, E. (2023). Empowerment contributes to exploration behaviour in a creative video game. Nature Human Behaviour, 7(9), 1481–1489. https://doi.org/10.1038/s41562-023-01661-2

## Experiment summary
Human players combine two elements from their growing inventory on each trial of a Little-Alchemy-style game, choosing which pair to combine and receiving an outcome; the key manipulation is semantics, comparing Tiny Alchemy (recognizable meanings, N=97) against Tiny Pixels (scrambled non-semantic stimuli, N=98) on Mechanical Turk, plus a validation experiment (N=103) with free-play, link-prediction and empowerment-rating tasks. The research question is whether people explore to increase empowerment—their ability to create even more new objects—and whether world knowledge drives this behaviour. The chosen element pair is the primary response; success and the element created are recorded per trial.

## Notes

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | Original integer subject number from source CSV (0..96, Tiny Alchemy / semantic game) |
| trial | 0-indexed trial number within participant (source `trial`); one trial = one element combination |
| response | JSON list `[first, second]` of the two element-index choices the participant combined that trial |
| inventory | Number of distinct elements in the participant's inventory at that trial |
| first | Element index chosen as first element of the combination (0-indexed node in the game tree) |
| second | Element index chosen as second element of the combination |
| success | `1` if the combination produced a new element, `0` otherwise |
| results | Outcome of the combination: JSON list of the created element index (e.g. `[314]`), or `-1` for failure (no new element). `-1` is a valid failed attempt, not missing data |

### exp1
| column | description |
|--------|-------------|
| participant_id | Original integer subject number from source CSV (0..97, Tiny Pixels / non-semantic scrambled game) |
| trial | 0-indexed trial number within participant (source `trial`); one trial = one element combination |
| response | JSON list `[first, second]` of the two element-index choices the participant combined that trial |
| inventory | Number of distinct elements in the participant's inventory at that trial |
| first | Element index chosen as first element of the combination (0-indexed node in the game tree) |
| second | Element index chosen as second element of the combination |
| success | `1` if the combination produced a new element, `0` otherwise |
| results | Outcome of the combination: JSON list of the created element index (e.g. `[314]`), or `-1` for failure (no new element). `-1` is a valid failed attempt, not missing data |

### exp2
| column | description |
|--------|-------------|
| participant_id | Remapped participant number from validation JSON key `'1'..'103'` to integer 0..102 |
| task_id | Task type within the validation session: `0`=free-play, `1`=link-prediction rating + element choice, `2`=empowerment rating |
| trial | 0-indexed response trial within (participant_id, task_id); for task 1, counts the two responses per combination (link then element) |
| phase | snake_case task label: `free_play`, `link_element`, `empowerment` |
| playedLA | `1` if participant had played Little Alchemy before, `0` otherwise (per-participant, repeated on each row) |
| response | Task-specific response: free_play = JSON list `[elem1, elem2]` of the two elements chosen; link_element = link-rate row is the 1-7 slider rating of how likely the combination succeeds (element-choice row is the chosen element string); empowerment = 1-7 empowerment rating |
| element1 | First element the participant chose in free-play (task 0) |
| element2 | Second element the participant chose in free-play (task 0) |
| outcome | Resulting element string from the free-play combination, or `none` if the combination failed (task 0) |
| block | Paper-trial index 0..19 within task 1, grouping the two responses (link rating then element choice) of the same combination |
| currentcombination | JSON list `[elem1, elem2]` of the combination shown for rating/choice (task 1) |
| elementoptions | JSON list of the four element options the participant chose from (task 1) |
| element_answer | The element string the participant chose among the four options (task 1) |
| empowerment_element | The single element string whose empowerment the participant rated (task 2) |

Notes: the game experiments (exp0/exp1) — the `*Memory.csv` files were verified to be row-subset (by trial within participant) versions of the main files for the same 97/98 participants, so only the full main files are emitted to avoid duplicate participant rows. Game-tree files `raw/playerdata/raw/*.csv` (element-name combinations) describe the ground-truth game structure, not trial-level behaviour, and are omitted. Validation (exp2) structure was derived from `main.js` and the analysis R script; the session is three sequential tasks. `-1` in game `results` marks a failed combination (kept as a row; it is a response, not missing data). The 29,493-player original Little Alchemy 2 dataset analysed in the paper is third-party data and is only available upon reasonable request, so it is not included here.

## Text-format conversion

All three experiments were transcribed (`transcripts0.jsonl`, `transcripts1.jsonl`, `transcripts2.jsonl`). exp0 (Tiny Alchemy) and exp1 (Tiny Pixels) are the element-combination game: participants freely choose two inventory elements to combine, so each combination is a free choice (rendered by element index, since the CSV stores indices not names). exp2 (validation) covers free-play combining, link-rating (1–7) plus 4-way element-choice, and empowerment-rating (1–7) — all free responses. None skipped.

Sample transcript (exp0, participant 0, up to the first response):

```
You are playing Tiny Alchemy (a Little-Alchemy-style game with recognizable element names), a game where you combine two elements at a time to try to create new elements. You start with a small inventory of basic elements. On each trial, choose two elements from your current inventory and combine them. If the combination is valid, a new element is created and added to your inventory for use in later combinations; if not, nothing new is created. You earn money for every new element you create. On each trial, type the two element index numbers you want to combine, separated by a space (for example, 0 2 means combine element index 0 and element index 2).

You have 5 elements in your inventory. You choose to combine element 0 and element 2. You press [HUMAN_RESPONSE]0 2[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction

Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Indeterminate: the primary modeling result — the mixed-effects logistic regression of combination choice on empowerment vs uncertainty model values (Fig 4d; Tiny Alchemy empowerment β=0.30, Tiny Pixels β=−0.05) — requires the empowerment predictor, which the paper defines over the semantic game tree (fasttext word vectors + neural link/element predictors, or the true `combination_table`/`parent_table` in the repo's `trueemp`/`emp` models). Those game-tree resources are deliberately omitted from this dataset (README Notes), and the CSVs record only the subset of combinations each participant actually attempted. Empowerment/success values for the randomly sampled alternative combinations in the regression design are therefore not derivable from the CSV columns; an observed-graph reconstruction would supply a purely structural predictor that is equally informative in the semantic (Tiny Alchemy) and scrambled (Tiny Pixels) conditions, collapsing the exact semantic contrast the paper's result depends on. No formal non-neural model is specifiable from the available columns.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Added `experiments/exp0/`, `experiments/exp1/` and `experiments/exp2/` — static
jsPsych v8 ports of the three experiments (Tiny Alchemy, Tiny Pixels, and the
validation session). The headless `?mode=simulate` round trip passed for all
three: each built a CSV matching its `expN.csv` schema (column names, dtypes,
0-indexed counters, `success`/`results` coding, per-task `trial`/`block`/`phase`
structure, JSON list formatting). The game-tree generative rule (combine two
elements, yield `out[0]`, add only if not already owned) was verified against the
dataset: 0 mismatches over all 48,963 (`exp0`) and 21,554 (`exp1`) rows, and the
free-play outcomes match 2060/2060 (`exp2`). Element *pictures* were replaced by
element *names* (labelled buttons) to avoid shipping ~540 image blobs; the
semantic/non-semantic manipulation is carried entirely by the names. `exp0`/`exp1`
are open-ended (player stops via "I give up"), so the harness simulates a bounded
20-round session; real sessions are open-ended.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

All three experiments got a text simulator (`simulate0.py` Tiny Alchemy,
`simulate1.py` Tiny Pixels, `simulate2.py` validation). Each embeds the verbatim
game-tree data (Little Alchemy 1, 540 elements: the 863-recipe combination table,
element names, the 1000-combination link-prediction pool and the 540-element
predicted-empowerment pool) and reproduces `build_jsonl.py`'s narration
byte-for-byte; the round trip (regenerate transcriptsN.jsonl from a simulated
`expN.csv`) passed for all three with no mismatches. Response tokens follow the
transcripts: exp0/exp1 use sorted element-index pairs (a<=b, self-pairs allowed),
exp2 free play uses space-separated element names, and the ratings/choices use the
visible option labels. ASSUMPTIONS worth surfacing: (1) exp0/exp1 sessions are
open-ended in reality, so the simulator plays a bounded, configurable number of
trials per participant (default 20); (2) `playedLA` in exp2 is only recorded as
1/-99 in the data, so it is drawn 1 with probability 0.22 (matching the 23/103
observed ratio), else -99.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
