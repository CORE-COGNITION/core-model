---
tags:
- paradigm:bandit
- cognitive-modeling:needs-review
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---

# dezfouli_2019_models

- Paper: https://doi.org/10.1371/journal.pcbi.1006903
- Data source: https://journals.plos.org/ploscompbiol/article/file?type=supplementary&id=10.1371/journal.pcbi.1006903.s031
- PDF: https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1006903&type=printable
- Full text: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006903
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Dezfouli A, Griffiths K, Ramos F, Dayan P, Balleine BW (2019) Models that learn how humans learn: The case of decision-making and its disorders. PLoS Comput Biol 15(6): e1006903.

## Experiment summary
N = 101 participants (34 healthy, 34 unipolar depression, 33 bipolar depression) completed a two-armed bandit instrumental learning task across 12 blocks with varying reward probabilities (0.25/0.125/0.08 vs 0.05). On each trial, participants chose left (R1) or right (R2) buttons for food rewards. The dataset covers 132,251 trials. The paper fits RNN, Q-learning variants (QL, QLP, GQL), and logistic regression models to compare learning strategies and predict diagnostic labels across groups.

## Notes

### Columns
| column | description |
|--------|-------------|
| participant_id | Anonymized participant identifier (P000–P100), in order of first appearance in the raw data. |
| trial | 0-indexed trial number, contiguous within each participant, derived from row order in the source. |
| response | Chosen arm; 0 = R1 (left button), 1 = R2 (right button). |
| block | Block number, 0-indexed (source 1–12 → 0–11). Reward probabilities vary across blocks. |
| reward | Binary reward outcome; 0 = no reward, 1 = reward received. |
| condition | Diagnostic group (between-subject); one of `healthy`, `depression`, `bipolar`. |
| best_action | Whether the chosen key is the optimal action for this block; 0 = FALSE, 1 = TRUE. |

Mapping from `exp0` to the paper's "Experiment 1": the single experiment corresponds to the main two-armed bandit task in the paper. No practice/warmup trials were recorded separately in the source.

## Text-format conversion

Transcribed `exp0.csv` (the two-armed bandit task) into `transcripts0.jsonl` (101 transcripts, one per participant, 132,251 trials in total). The task is textifiable: each trial is a free choice between pressing the left or right button, followed by a visible reward outcome. No experiment was skipped. Below is a sample transcript verbatim from the start up to and including the first `[/HUMAN_RESPONSE]`; the instructions alone fully determine the response token (`L` or `R`).

```
You see two buttons side by side: a left button and a right button. Your task is to press one button on each trial to try to earn food rewards. On a trial, press the left button by typing L, or the right button by typing R. Pressing a button sometimes earns you a food reward (an M&M chocolate or a BBQ-flavoured cracker) and sometimes earns you nothing. The chance of earning a reward from each button changes from time to time, so pay attention to what happens and try to earn as many rewards as you can.
You press [HUMAN_RESPONSE]R[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

Added `simulate0.py`, a text simulator for the two-armed bandit (`exp0`) that reproduces the reward process (12 blocks; better-action reward probability 0.25/0.125/0.08, other action 0.05) and the fixed L/R response coding. Round-trip check through `build_jsonl.py` passed (byte-identical transcripts). `exp0.csv` has no `rt` column (no reaction-time process). ASSUMPTION: blocks are 40 s self-paced in the real data, so each block's trial count is drawn from `round(N(109, 34))`; the six (better-prob, better-side) pairs are shuffled and each repeated twice, matching the paper's "six pairs repeated twice" rule.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Online experiment

Built `experiments/exp0/` (the two-armed bandit) as a static jsPsych v8 port of the paper
(NB: the repo has no text simulator, so the task was reproduced from the paper + CSV, not
from a `simulate0.py`). The headless `?mode=simulate` round trip passed: 12 self-paced 40 s
blocks × 60 simulated rows, schema columns match `exp0.csv` exactly plus a browser-only
`rt`, `trial` contiguous, no outbound POST. `condition` is fixed to `healthy` (a fresh
online participant's diagnostic group is unknown and the paper pre-assigns it in-task);
all other columns, the reward process, block schedule, and response coding match the paper.
No experiments were skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling (primary results are RNN/LSTM-based).
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Partial validation: none.
Indeterminate: every primary modeling result (rnn action-prediction accuracy beating ql/qlp/gql/lin baselines in leave-one-out CV; off-policy simulations; diagnostic-label prediction) depends on a recurrent neural network (LSTM) cognitive model, which is out of scope for auto-exp-modeling. No standalone non-neural primary modeling result exists to implement.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Verification

Verdict: pass (critical 0, major 0, minor 6; fixed 3, open 3).

Checked: paper (https://doi.org/10.1371/journal.pcbi.1006903), original data (S1 Data ZIP, for_plos.csv, https://journals.plos.org/ploscompbiol/article/file?type=supplementary&id=10.1371/journal.pcbi.1006903.s031), exp0, transform re-run (byte-identical), transcripts (rebuild byte-identical; all 101 transcripts match the CSV rows), simulators (runs; round trip through build_jsonl.py byte-identical), modeling (no model.py; the section and the cognitive-modeling:needs-review tag agree that the paper's primary modeling results are RNN-based), analysis (all 3 effects reproduce), logs. Skipped: none.

Fixed:
- README Experiment summary gave no 'N =' claim; it now reads 'N = 101 participants' (exp0.csv: 101 participants, 34 healthy, 34 depression, 33 bipolar, matching the paper p. 18 and Table 2).
- README Simulators section said '`rt` is dropped'; exp0.csv has no rt column, so the wording now says so.
- simulate0.py docstring gave sd=27 for the per-block trial count while the code uses 34 (data: mean 109.1, sd 33.8 trials per participant-block); docstring corrected, no code change.

Open:
- minor: the source codes the keys as R1/R2, and neither the source nor the paper (p. 20: keyboard keys 'Z' and '?' designated L and R) states which of R1/R2 is the left key; the README's R1 = left, R2 = right assignment and the L/R tokens in transcripts0.jsonl are an assumption. The 0/1 coding of response is unaffected.
- minor: the paper (p. 20) describes a 0.25-contingency practice block, food pleasantness ratings, inter-block causal ratings, and an fMRI vs keyboard setting (14 HEALTHY and 13 BIPOLAR participants in fMRI); the source for_plos.csv holds only the 12 training blocks (ID, key, block, reward, diag, best_action). The data is faithful to its source. Per-group mean trials per block (109.46 / 114.92 / 102.80) match the paper (109.45 / 114.91 / 102.79, p. 20).
- minor: the modeling section states that no non-neural primary modeling result exists; the paper (p. 8) also reports GQL beating QLP in the DEPRESSION and BIPOLAR groups in leave-one-out cross-validation, a comparison among the baseline models that the modeling stage did not attempt.

Run: claude-fable-5-1, 2026-09-10
