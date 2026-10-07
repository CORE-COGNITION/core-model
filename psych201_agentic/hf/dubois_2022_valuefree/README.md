---
tags:
- paradigm:bandit
- cognitive-modeling:needs-review
- psych-101
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---

# dubois_2022_valuefree

- Paper: https://doi.org/10.1038/s41467-022-31918-9
- Data source: https://doi.org/10.5281/zenodo.6522060
- PDF: https://www.nature.com/articles/s41467-022-31918-9.pdf
- Full text: https://www.nature.com/articles/s41467-022-31918-9
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation

Dubois, M., & Hauser, T. U. (2022). Value-free random exploration is linked to impulsivity. Nature Communications, 13(1), 4542. https://doi.org/10.1038/s41467-022-31918-9

## Experiment summary

Registered report using a 3-armed Horizon ("Maggie's farm") bandit task with two horizons (short = 1 draw, long = 6 draws), four bandit types (certain-standard/standard/novel/low-value) drawn 3-of-4 per game, and tree magnitudes varying per game. N=658 online participants completed the main preregistered study (each contributing 2900 sample/choice rows across 400 games), and a separate pilot sample was run first (its public data is aggregate-only and excluded here). Participants clicked a tree among three presented to sample apple rewards; the key manipulation was horizon length and bandit type across games. Research question: whether impulsivity (and other psychiatric dimensions) is specifically linked to value-free random exploration versus directed/novelty exploration, assessed by fitting mixture reinforcement-learning models (UCB, novelty, value-free random, value-based random) to choices and correlating fitted parameters with BIS-11 impulsivity and other questionnaire dimensions.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject id from the .mat filename, e.g. "user_100" |
| block | 0-indexed game id (400 per participant; = Blocktrial - 1; the 4 source Blocks hold 100 games each); groups the rows of one bandit set with fixed horizon |
| trial | 0..2899 within each participant_id, sequential in source order (counts sample rows, not just choices) |
| phase | "test" (main task only; the log contains no separate training/warmup rows) |
| response | 0-indexed position (left=0, middle=1, right=2) of the chosen tree among the 3 presented trees; NaN on initial-sample display rows where no choice was made (forced_choice=1) |
| rt | Reaction time in milliseconds on the choice row; NaN on non-choice rows |
| reward | Apple size (2..10) obtained on that sample; the delivered reward. NaN on initial-sample display rows |
| forced_choice | 0 = free draw, 1 = initial-sample display row (revealed apple, no participant choice) |
| Block | Source block number (1..4) from the raw log |
| Blocktrial | Source game number (1..400), cumulative across the 4 Blocks (not reset per Block) |
| Horizon | Horizon code in source units (6 = short horizon 1 draw, 11 = long horizon 6 draws); nchoice rows per game match 1 vs 6 |
| Item | Item/schedule id (1..100) identifying the bandit reward configuration for the game |
| Sample | Sample step number within the game (initial samples first, then draws) |
| Size | Raw apple size (2..10) identical to reward |
| PressedKey | Raw chosen-tree position (1=left,2=middle,3=right); NaN on non-choice rows; basis for response |
| UnusedTree | Which of the 4 trees (1..4) was not presented in this game |
| TreeColGroup | Colour group id (1..8) for the tree colours of this game |
| TreeA/TreeB/TreeC/TreeD | Which tree this row's apple came from: 1 on the tree that was sampled on this row (initial sample or draw), NaN for the other three; exactly one of the four is 1 per row |
| TreeLeft/TreeMiddle/TreeRight | The tree id (1..4) placed at the left/middle/right screen position for the game |
| BlockDuration | Duration (seconds) of the block as recorded in the raw log; 20 participant-blocks carry a negative value (about -85000 s) in the source, kept as is |
| InfoRequestNo | Info-request counter from the raw log (0 on most rows; 1 or 4 for a few participants) |

The paper's headline association (value-free random exploration ~ impulsivity) requires fitted RL mixture-model parameters and questionnaire scores that are not present in the trial-level CSV; it is therefore not testable from this dataset. All directly testable preregistered horizon-exploration behavioral effects reproduce (direction and significance match).

Sample composition: the raw data ships 658 per-participant .mat logs (each 2900 rows, 400 games); the transform keeps every shipped participant per the fidelity rule, so the CSV has 658. The paper's data_collection.log lists 657 ids (580 retained + 77 excluded by its quality criteria, e.g. chance-level score / mean first-draw RT < 1500 ms / failed attention check) plus one id (user_199) absent from the log; the paper's analyzed final sample is N = 580. A note on Horizon coding: source Horizon values 6 (short, 1 draw) and 11 (long, 6 draws) were kept in source units and are only decoded in the README/model scripts, not in the CSV.

## Text-format conversion

exp0.csv (the single experiment) was transcribed to transcripts0.jsonl (658 transcripts, one per participant). It is a 3-armed "Maggie's Farm" apple-tree bandit task: each round opens with a line stating its horizon (ONE draw or SIX draws, which participants saw on screen), then participants see initial-sample apples on the three trees and make their free draws, with numeric apple-size rewards. Describing the option values in words does not change the cognitive operation, so it is textifiable.

Sample transcript (start up to the first response):

```
You are on a farm with apple trees. On each round, three trees are presented: one on the left, one in the middle, and one on the right. Before you choose, you are shown apples that were already picked from some of the trees (initial samples), telling you roughly how good each tree is. Your goal is to pick apples so that the total size of the apples you collect is as large as possible.
On each round you either make just ONE draw (pick one tree) or SIX draws (pick a tree up to six times, seeing the apple you get after each pick).
To pick a tree, press the letter for its position: press A for the middle tree, B for the right tree, and C for the left tree.
A new round starts. You have SIX draws in this round.
You see an initial sample: an apple of size 6.0 is hanging on the middle tree.
You see an initial sample: an apple of size 4.0 is hanging on the right tree.
You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

`simulate0.py` simulates exp0 (Maggie's Farm Horizon task): 100 reward items per participant, each used 4x (2 short + 2 long horizon) for 400 games of initial samples + free draws, rewards ~ round(N(mu, 0.8)) truncated to [2,10]. The round-trip check passes byte-identically against `build_jsonl.py`. Assumptions surfaced in the class docstring: fixed type->tree mapping (A=cs, B=std, C=novel, D=low) with a balanced omitted type per item, initial samples fixed per item with the low-value sample regenerated strictly smallest, and `rt`/`BlockDuration` (measured columns) dropped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Online experiment

An online experiment was added for exp0 (the Maggie's Farm Horizon task) at
`experiments/exp0/` (static jsPsych v8, one self-contained `index.html`). It
reproduces the task from the paper's Methods and the transcript narration: 100
reward schedules, each used 4x (2 short / 2 long horizon) → 400 rounds; 3 of 4
bandit types presented per round; rewards `round(N(mu,0.8))` truncated to [2,10];
the low-value initial sample is kept smallest. The saved CSV matches `exp0.csv`'s
26-column schema and dtypes. The headless `?mode=simulate` round trip passed on
this machine (2900 rows/participant, all codings and counts consistent) and the
visual check found no rendering breakage. `rt` and `BlockDuration` are
browser-measured (the raw log could not record them). The paper's comprehension /
training phase is not recorded (exp0.csv contains only `phase="test"` rows), so it
is a cosmetic ASSUMPTION not to log it. Since this repo had no `simulateN.py`, the
task language was taken verbatim from `transcripts0.jsonl` and the generative
process from the Methods.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling results.
Fitted models: thompson, thompson_eps, thompson_eta, thompson_eps_eta, ucb_eps_eta
(stationary-Kalman posterior, Thompson/softmax choice rules, value-free epsilon-greedy
and novelty-bonus heuristics; Q0 shared, sigma0/epsilon/eta fit per horizon); BIC model
comparison + Wilcoxon signed-rank on per-participant horizon parameters. Only the first
draw of each game is modelled, as in the paper.
Reproduced: winning_model_thompson_eps_eta, epsilon_higher_long, eta_higher_long.
Not reproduced: none.
Numeric mismatch: none (Thompson+eps+eta lowest BIC; epsilon and eta increase in the
long horizon, both p < .05).
Partial validation: N=64.
Indeterminate: none (headline impulsivity correlation is not testable — BIS/ASRS
questionnaire scores are absent from exp0.csv; the full 658-participant fit exceeds the
wall-clock budget, so a capped N=64 fit is reported; the UCB+eps+eta comparator is
unreliable, frac-at-bound ~1).
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-26

## Verification

Verdict: pass (critical 1, major 2, minor 7; fixed 7, open 3).

Checked: paper (https://doi.org/10.1038/s41467-022-31918-9, Nature PDF), original data (https://doi.org/10.5281/zenodo.6522060: 658 raw/user_*.mat, data_collection.log, data_for_figs), exp0, transform re-run (byte-identical exp0.csv), transcripts (rebuild), simulators (smoke test and round trip), modeling (partial re-run), analysis (3/3 effects reproduce), logs. Skipped: modeling full N=64 re-run (model.py --max-participants 64 did not finish within the 4 h cap on the 2 CPUs of this session; the run that produced the README section had 20 CPUs and took 49 min). Partial re-run with --max-participants 16 finished in 57 min and matches the previous run's logged N=16 table digit for digit (BIC 8989.17 / 8540.23 / 8653.83 / 8001.61 / 8118.78; winner thompson_eps_eta YES; epsilon_higher_long NO (0.020, underpowered at N=16, as in the previous run); eta_higher_long YES (1.047)), so model.py is deterministic and the logged N=64 table (all three results YES) that the README section reports is the output of this script..

Fixed:
- critical: the transcripts never stated a round's horizon, although participants saw it on screen (crate slots and sun, Fig. 1 caption; Methods p. 11) and it is the manipulated variable. build_jsonl.py now writes 'A new round starts. You have ONE draw/SIX draws in this round.' before each round's initial samples (Horizon 6/11); simulate0.py writes the same line; transcripts0.jsonl regenerated (658 transcripts, +400 lines each, otherwise unchanged); round trip through build_jsonl.py byte-identical for 3 simulated participants; README sample transcript and text-format note updated.
- major: README described Blocktrial as 'within Block (1..100)'; the CSV holds 1..400 cumulative across the 4 Blocks (block = Blocktrial - 1 on every row). Row corrected.
- major: README described TreeA..TreeD as presence indicators; in the CSV exactly one of the four is 1 per row and marks the tree the row's apple came from (build_jsonl.py, model.py and analysis.py rely on this). Row corrected.
- minor: README said InfoRequestNo is 'constant 1'; the CSV holds 0 (1,863,960 rows), 1 (41,340) and 4 (2,900). Row corrected.
- minor: README row for BlockDuration now notes that 20 participant-blocks carry a negative value (about -85,000 s) in the raw .mat, kept as is.
- minor: README row for block said '4 Blocks x 100 Blocktrials', which implied a per-Block reset; now 'block = Blocktrial - 1'.
- minor: the previous ## Verification section claimed the TreeA..TreeD table row had been split; it had not (the checker accepts the grouped row). Section replaced.

Open:
- minor: logs/auto-exp-verify.sessions.json holds 2 root sessions; both first messages name this dataset. Attempt 1 (2026-09-13 16:07-16:16 UTC) died mid-run before touching the repo and the runner retried (attempt 2, 16:16-18:21, produced the result); lib/oc_run.sh exports every session of one run. Not cross-run contamination; kept as the faithful record.
- minor: transcripts0.jsonl records carry TreeA..TreeD = 1 as metadata (constant after dropna in build_jsonl.py's generic metadata rule); no participant-level meaning, harmless.
- minor: response is empty on 52% of rows: the initial-sample rows (forced_choice = 1) that the schema requires keeping; documented in the README.

Run: claude-fable-5-1, 2026-09-14
