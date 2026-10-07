---
tags:
- paradigm:two-step-task
- cognitive-modeling:needs-review
- psych-101
- js-experiment:pass
- text-format:pass
- simulator:pass
---
# tomov_2021_multitask

- Paper: https://doi.org/10.1038/s41562-020-01035-y
- Data source: https://github.com/tomov/MTRL
- PDF: https://gershmanlab.com/pubs/Tomov21.pdf
- Full text: https://www.biorxiv.org/content/10.1101/815332v1
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Tomov, M. S., Schulz, E., & Gershman, S. J. (2021). Multi-task reinforcement learning in humans. Nature Human Behaviour, 5(6), 764-773.

## Experiment summary
Participants completed a two-step decision-making task (MTurk) in which they navigate from a start state to a terminal state by repeatedly choosing one of three doors, then land on a dish/restaurant state and receive a reward. Reward weights are assigned to multi-feature state feature-vectors, and these weights change across a set of training tasks (permuted per participant) before a novel transfer task tests which terminal state participants generalize to, pitting model-based, model-free, and successor-feature (SF&GPI / UVFA) RL strategies. Experiment 1 (N=232 collected; 226 reported) established the transfer effect; Experiment 2 (N=276; 202 reported) replicated with nuisance features and larger feature ranges; Experiment 3 (N=245; 200 reported) replicated the core transfer result; Experiment 4 (preregistered, N=500; 303 included) added a fully preregistered test of the transfer prediction (81 chose the SF&GPI-predicted state 12, 46 chose state 7). Response types are sequential key-press door choices with reaction times and per-trial rewards. The paper also fits computational RL models (SF&GPI, UVFAs, model-based, model-free) to these data, so behavior is tagged for cognitive modeling.

## Notes

### Columns

### exp0 / exp1 / exp2 (experiments 1–3, full per-keypress data)
| column | description |
|--------|-------------|
| participant_id | Original MTurk subject id from the source CSV filename / `subj_id` column (string of digits). |
| trial | 0-indexed response counter within each participant (one row per door choice). |
| block | 0-indexed paper-trial index within each participant (groups the door-choice rows of one navigation trial). |
| response | Door choice, 0-indexed: 0=door 1 (key 1/numpad 1), 1=door 2 (key 2/numpad 2), 2=door 3 (key 3/numpad 3). |
| rt | Reaction time (ms) for that door choice, from the matching position of the source `RTs` vector. |
| state | 0-indexed state at which the choice was made (source `path` position − 1; states 0–12). |
| reward | Total reward (points) for the trial, delivered by the final door choice; NaN on non-final rows of the block. |
| group | Between-subject counterbalancing label from source (always "A" in these folders). |
| phase | `training` (source `stage`="train") or `test` (source `stage`="test"). |
| start | Source start state index (1-indexed) of the trial. |
| goal | The task reward-weight vector for the trial (3 features), as JSON array (source `goal` like "[1 -1 0]" re-serialized as JSON). |
| path | Space-separated sequence of states visited (source `path`), 1-indexed. |
| length | Number of states in `path` (source `length`). |
| RTs | Full space-separated per-key reaction-time string for the trial (source `RTs`), ms. |
| keys | Full space-separated keycodes pressed for the trial (source `keys`); 32=space confirm, 49/50/51 and 97/98/99 = door keys 1/2/3. |
| valid_keys | Space-separated indices (into `keys`) of the door-choice presses (source `valid_keys`). |
| RT_tot | Total reaction time (ms) summed over the trial (source `RT_tot`). |
| timestamp | Unix time (float seconds) logged at trial end (source `timestamp`). |
| datetime | Human-readable timestamp string (source `datetime`). |
| check_fails | Instruction-check failure count (source `check_fails`). |
| cheated | 0/1 flag from the `_extra.csv` file marking participants the authors excluded as cheaters (0=no, 1=yes). Present in exp1/exp2 only (the column is absent from exp0, which has no `_extra` files); empty for exp1/exp2 participants without an `_extra` file. |

### exp3 (experiment 4, preregistered summary)
| column | description |
|--------|-------------|
| participant_id | Source prereg subject id (1–500, kept as string). |
| trial | 0-indexed trial number within each participant (source `trial` 1–101, re-zero-indexed). |
| response | Final terminal state reached, 0-indexed (source `fstate` 1–13, minus 1). |
| fstate | Source final-state index (1-indexed, terminal states 5–13). |
| reward | Reward (points) on that trial (source `reward`, source units). |
| rt | Reaction time (ms) on that trial (source `rt`). |
| phase | `training` for trial 1–100, `test` for trial 101 (from the paper; the 101st trial is the crucial w=test=[1,1,1] trial). |

The four experiments map from raw folders as: exp0 = Experiment 1 (`usfa_v1_1h`), exp1 = Experiment 2 (`usfa_v1_1j`), exp2 = Experiment 3 (`usfa_v1_1l`), exp3 = Experiment 4 (`preregdat.csv`). The per-participant CSVs are named by MTurk id; participant counts exceed the paper's reported N because the authors excluded participants (and, in exp1/exp2, flagged cheaters via the `cheated` column which is carried through). Pilot/preliminary/alternate result folders (`usfa_v1_prelim`, `usfa_v1_1d_prelim`, `usfa_v1_1f`, `usfa_v1_1g*`, `usfa_v1_1h_long`, `usfa_v1_1i`, `usfa_v1_1k`, and `ARCHIVE/` batches, which duplicate `results/`) and `bonus*.csv` payment logs were deliberately not included.

## Update (2026-08-13)
- PII removal: dropped the `assignment_id` and `worker_id` columns (MTurk platform ids; the two source columns were swapped relative to their names) from exp1.csv (51,494 rows, 276 participants) and exp2.csv (46,668 rows, 245 participants). exp0.csv and exp3.csv never had these columns and are unchanged. `participant_id` (numeric codes) and all other columns are unchanged.

CSVs fixed in place from the previous release; transform.py updated to produce the same output
from raw. The previous version remains in the repo's git history.

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling — the paper's RL models (SF&GPI, UVFA,
model-based, model-free) are simulated with fixed hyperparameters (gamma=0.99, alpha=0.1,
eps=0.9, beta=10) in the authors' MATLAB code, not fitted to participant data, so there is
no fitted-model comparison to reproduce. The only data fit is the Experiment 4 Bayesian
multi-level logistic regression predicting test-trial state-12 choice from training
experience variables (evaluated via standardized LOO r2 and Bayes factors), which is a
standard inferential claim about raw choices (out of scope).
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Indeterminate: no formal non-neural model is fit to the behavioral data in the paper; the
RL candidate models are simulation predictions, and the sole data fit is a standard
logistic regression on the raw test choice.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`experiments/` contains a static jsPsych v8 port of the Medieval Trading task,
one folder per experiment: `exp0/` (Experiment 1), `exp1/` (Experiment 2),
`exp2/` (Experiment 3) and `exp3/` (Experiment 4, per-trial rows). The headless
`?mode=simulate` round trip passed for all four: each reproduces its `expN.csv`
schema exactly (column order, 0-indexed counters, 2 door-choice rows per block
for exp0/1/2, one per-trial row for exp3) and the delivered rewards recompute
exactly from `phi(terminal) . w` (max error 0). Nothing was skipped. Design was
recovered from the paper plus the original task code (tomov/MTRL); see
`experiments/README.md` for the cosmetic assumptions (door pictures replaced by
numbered doors, blank `cheated`, canonical `goal` ordering for exp0).
Run: openrouter/deepseek/deepseek-v4-flash-vision-exp, 2026-08-25

## Text-format conversion

Transcribed exp0.csv, exp1.csv and exp2.csv (Experiments 1-3, the Medieval
Trading door-choice task): each trial narrates today's market prices, both door
presses (free responses, keys 1/2/3), the room entered, the terminal room's
resource quantities, and the points earned. exp3.csv (preregistered Experiment
4) was skipped as not textifiable: it records only the terminal state and reward
per trial, with no per-trial market prices (weights) to narrate, so the
information participants used to choose is unrecoverable. Resource names are
kept in canonical order (position 0 = wood, 1 = stone, 2 = iron); the raw
per-participant resource assignment wasn't recorded, and for the raw-permuted
exp0 `goal` column the per-participant permutation was recovered from the
recorded rewards before narrating.

Sample transcript (start of one exp0 participant, including the first response):

```
Imagine you are a tradesperson scavenging a medieval castle for resources to
trade. There are three resources -- wood, stone, and iron -- that you can sell
at different prices. Some resources cannot be sold but must be disposed of at a
cost; those prices are shown as negative. Each day you first see today's market
price for each resource, then you enter the castle. The castle has different
rooms. You always start in room 1. In a room with doors, you choose a door by
pressing the number key 1, 2, or 3 (door 1, 2, or 3); the same door always
leads to the same next room. After two door choices you reach a room holding
resources, which you sell (or dispose of) at today's prices to earn points for
that day. The castle layout and the amount of each resource in each room never
change; only today's prices change across the days. Your goal is to earn as
much as you can each day. There are about 101 days in the experiment.

Day 1 (training). Today's market prices: wood $+1, stone $-1, iron $+0. In room
1 you press [HUMAN_RESPONSE]1[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Text simulators `simulate0.py`, `simulate1.py` and `simulate2.py` were written
for exp0-exp2 (Experiments 1-3) and pass the round-trip check against their
`transcriptsN.jsonl` (byte-identical text, modulo random draws). exp3
(preregistered Experiment 4) is not simulated: it records only the terminal
state and reward with no per-trial market prices, so the info participants used
is unrecoverable (same reason it was skipped by the text transcription).
ASSUMPTION: the per-participant door->room permutation and resource<->weight
assignment are not recorded; like build_jsonl.py, the simulators fix canonical
resource order and draw a fresh random door map per participant.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
