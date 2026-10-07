---
tags:
- paradigm:bandit
- cognitive-modeling:needs-review
- psych-201
- js-experiment:pass
- text-format:pass
- simulator:pass
---

# witte_2024_exploring

- Paper: https://doi.org/10.31234/osf.io/td8xh
- Data source: https://github.com/KristinWitte/worried_exploration
- PDF: https://osf.io/td8xh/download
- Full text: https://osf.io/preprints/psyarxiv/td8xh
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Witte, K., Wise, T., Huys, Q. J. M., & Schulz, E. (2024). Exploring the Unexplored: Worry as a Catalyst for Exploratory Behavior in Anxiety and Depression. PsyArXiv. https://doi.org/10.31234/osf.io/td8xh

## Experiment summary
Three online Prolific studies examined how anxiety-depression symptoms relate to exploration in an 11x11 multi-armed bandit grid with spatially correlated rewards, where some rounds were risky (a below-threshold "kraken" square wiped out that round's rewards). Study1 (N=220) and the preregistered Study3 replication (N=462) were correlational, linking symptom questionnaires to novelty-directed exploration; Study2 (N=75) added a worry-reduction vs control intervention to test causal effects on exploration. Response was a click on one of 121 grid squares (coded as cell index 0..120).

## Notes

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | Original participant number from source master.csv (Prolific IDs removed/remapped; here original sequential integer from source) |
| task_id | 0-indexed round/block (source `blocknr` 1..11 -> 0..10); each round is a fresh 11x11 reward grid |
| trial | 0..N within each (participant_id, task_id); source `click` (1..11) -> 0-indexed |
| x | x-coordinate (0..10) of the clicked square |
| y | y-coordinate (0..10) of the clicked square |
| reward | reward/fish obtained on that click (source `z`); NA after kraken caught or on filler rows |
| krakenPres | condition code, 0 = safe, 1 = risky (kraken may be present) |
| krakenCaught | 1 if that round the participant clicked a square below threshold and lost all rewards that round |
| rowindex | source row counter within participant (presentation order) |
| distance | Euclidean distance to the previously clicked square |
| STICSA | State-Trait Anxiety Inventory total score |
| STICSAcog | STICSA cognitive subscale score |
| STICSAsoma | STICSA somatic subscale score |
| IUS | Intolerance of Uncertainty Scale score |
| CAPE_depressed | CAPE depressed subscale score |
| CAPE_positive | CAPE positive subscale score |
| CAPE_negative | CAPE negative subscale score |
| RRQ | Rumination-Reflection Questionnaire score |
| PID5_negativeAffect | PID-5 Negative Affect domain score |
| age | participant age in years |
| gender | participant sex, mapped from source 0/1/2 codes: 0=m, 1=f, 2=other |
| edu | education level code |
| attention | number of attention checks passed (constant per participant) |
| condition | safe / risky derived from krakenPres |
| response | 0-indexed cell index = x*11 + y of the clicked square (NA on filler/no-click rows) |
| valid | 1 if a square was clicked (x not NA), 0 for filler rows after the round ended |

### exp1
| column | description |
|--------|-------------|
| participant_id | Original participant number from source Master.csv |
| task_id | 0-indexed round/block (source `block` 1..11 -> 0..10); fresh reward grid each round |
| trial | 0..N within each (participant_id, task_id); source `trial` (1..26) -> 0-indexed |
| x | x-coordinate (0..10) of the clicked square |
| y | y-coordinate (0..10) of the clicked square |
| reward | fish/reward obtained on that click (source `z`); NA after kraken found or filler rows |
| krakenFound | 1 if the participant clicked a below-threshold square and lost that round's rewards |
| time | time in ms for that block (per-block, not per-trial); NA on first block |
| condition | intervention group: control or intervention (source `cond`) |
| env | index of the reward grid/environment seen that round |
| tp | timepoint: pre / post (before vs after the intervention) |
| STICSAcog | STICSA cognitive subscale score |
| STICSAsoma | STICSA somatic subscale score |
| MCQ | Meta-Cognitions Questionnaire total score |
| MCQpos | MCQ positive-beliefs subscale |
| MCQneg | MCQ negative-beliefs subscale |
| MCQconf | MCQ cognitive-confidence subscale |
| MCQcontrol | MCQ need-to-control subscale |
| MCQselfcons | MCQ cognitive-self-consciousness subscale |
| MWQfreq | Metacognitive Worry frequency score |
| MWQbelief | Metacognitive Worry belief score |
| CASpre | Cognitive Attentional Syndrome score before intervention |
| CASpost | CAS score after intervention |
| CASchange | CAS change (post - pre) |
| PHQ | Patient Health Questionnaire depression score |
| unique | 1 if the clicked square had not been clicked before in that round, 0 otherwise (NA on filler) |
| phase | pre_intervention / post_intervention derived from tp |
| response | 0-indexed cell index = x*11 + y of the clicked square (NA on filler rows) |
| valid | 1 if a square was clicked (x not NA), 0 for filler rows after the round ended |

### exp2
| column | description |
|--------|-------------|
| participant_id | Original participant number from source Master_strict.csv |
| task_id | 0-indexed round/block (source `block` 1..11 -> 0..10); fresh reward grid each round |
| trial | 0..N within each (participant_id, task_id); source `trial` (0..10) kept 0-indexed |
| x | x-coordinate (0..10) of the clicked square |
| y | y-coordinate (0..10) of the clicked square |
| reward | fish/reward obtained on that click (source `z`); NA after kraken found or filler rows |
| kraken_present | condition code, 0 = safe, 1 = risky (source `krakenPresent`) |
| krakenFound | 1 if the participant clicked a below-threshold square and lost that round's rewards |
| env | index of the reward grid/environment seen that round |
| nervous | self-reported nervousness rating 0-100 given after some rounds (only on safe rounds / one per round) |
| CAPE | CAPE composite score |
| IUS | Intolerance of Uncertainty Scale score |
| PID | PID scale score |
| PSWQ | Penn State Worry Questionnaire score |
| RRQ | Rumination-Reflection Questionnaire score |
| STICA_T_c | STICSA trait cognitive subscale |
| STICA_T_s | STICSA trait somatic subscale |
| edu | education level code |
| age | participant age in years |
| diagnosis_2 | self-reported diagnosis code |
| kraken_2 | code indicating awareness of kraken mechanics |
| meds_3 | medication code |
| gender | participant sex, mapped from source Sex_0: 0=m, 1=f, 2=other |
| motivation_1 | motivation rating |
| income_0 | income band code |
| condition | safe / risky derived from kraken_present |
| response | 0-indexed cell index = x*11 + y of the clicked square (NA on filler rows) |
| valid | 1 if a square was clicked (x not NA), 0 for filler rows after the round ended |

### Experiment mapping

- `exp0` = Study1 (N=220, correlational, 11 rounds of 11 clicks each)
- `exp1` = Study2 (N=75, intervention: worry-reduction vs control, 11 rounds of 26 clicks each)
- `exp2` = Study3 (N=462, preregistered replication, strict-inclusion sample)

All three experiments used the same 11x11 spatial multi-armed bandit task with correlated rewards. Filler rows (no-click rows inserted after a kraken catch ended the round early) are retained with `valid=0` and `response` empty.

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Partial validation: none.
Indeterminate: The paper's modeling is a Gaussian-Process learning model (RBF kernel, free
length scale) fit hierarchically with NumPyro NUTS and compared by 5-fold-CV exceedance
probability; the headline results are the winning novelty-bonus model and Bayesian
mixed-effects regressions of the fitted novelty-bonus parameter on nervousness. A
faithful hierarchical fit to N=220-462 is computationally infeasible in the budget
(GP likelihood ~9 s/participant/model, tens of participants per model already exceed the
timeout). The only budget-feasible approximation, per-participant bounded L-BFGS MLE,
produced degenerate fits: the softmax temperature pinned at its upper bound for every
participant and the novelty bonus at a bound for most, exactly the identifiability
problem the paper cites as its reason for hierarchical estimation. Per-participant
parameter estimates (and hence the nervousness-eta regression and the model comparison)
cannot be trusted, so the run was left indeterminate rather than reporting a false
reproduction.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Static jsPsych v8 ports of all three experiments are in `experiments/`
(`exp0/` = Study1, `exp1/` = Study2, `exp2/` = Study3). The headless
`?mode=simulate` round trip ran and passed for all three: each reproduces its
`expN.csv` column set exactly, the per-block row counts (11 / 26 / 11), the task
indices (exp2 omits the bonus round task_id 4), and the value codings (filler
`valid=0` rows, `response = x*11+y`, `condition` vs `krakenPres`/`kraken_present`).
There is no text simulator (the task is visual), so each experiment was rebuilt
from the paper + the Data source task code + `expN.csv`; browser-only defaults
(thresholds are fixed by the study, timings/layout are cosmetic) are marked
`ASSUMPTION:` in each `index.html`. The experiment ships only the task, so
questionnaire/demographic columns are left blank.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Text-format conversion

All three experiments were transcribed (`exp0` = Study1, `exp1` = Study2, `exp2` = Study3): each is a spatial 11x11 multi-armed bandit in which participants choose a grid square each turn, so the choice is fully expressible as a square number (response = `x*11+y`) and the revealed fish counts carry all feedback. The Kraken outcome is narrated once per round from the round's `krakenCaught`/`krakenFound` flag; filler rows (`valid=0`) encode an early round end and are not recounted. exp0's bonus round is transcribed as a normal safe round; exp2's unrecorded bonus round (task_id 4) is skipped. The nervousness slider after exp2 rounds 1,5,7,9 and the Study2 intervention/control phase transition are transcribed; the intervention's open-ended answers were not recorded and are not marked.

Sample transcript (Study1, exp0), from the start through the first free response:

```
In this game you are a sailor catching fish from the ocean. You see an 11-by-11 grid of ocean squares, and on each turn you fish one square and see how many fish you catch there. ... To fish a square, type the square's number. Squares are numbered 0 to 120 from the top-left, row by row: the square in row r and column c (each from 0 to 10, with row 0 at the top and column 0 at the left) is number r*11 + c. ...

Round 1. The warning above the ocean reads: 'The kraken is nearby!'
A square is revealed for you: row 2, column 8 — it contains 62 fish.
You fish row 4, column 4 (square 48). [HUMAN_RESPONSE]48[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Each experiment got a text simulator (`simulate0.py` = Study1, `simulate1.py` = Study2, `simulate2.py` = Study3), all passing the round-trip check against the repo's `build_jsonl.py` byte-for-byte; none skipped. The simulators use the studies' actual `sample_grid.json` reward grids, the task's reward noise `round(N(0,1))`, and the data-confirmed Kraken rule (a round ends on the first click whose true grid value is at/below the safety threshold; Study3 nervousness sliders are free 0-100 responses recorded after rounds 2/5/7/9). ASSUMPTIONS: Study2's reward fields are floored to integers; questionnaire/demographic columns and Study2's per-block `time` are dropped (a text simulator cannot produce them).
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25