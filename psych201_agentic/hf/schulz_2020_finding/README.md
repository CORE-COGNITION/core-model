---
tags:
- paradigm:bandit
- cognitive-modeling:needs-review
- psych-101
- js-experiment:needs-review
- text-format:pass
- simulator:pass
- verification:pass
---
# schulz_2020_finding

- Paper: https://doi.org/10.1016/j.cogpsych.2019.101261
- Data source: https://github.com/nicktfranklin/StructuredBandits (raw per-trial CSVs under `Data/exp_*/`; five read by transform.py — `lindata.csv`, `datascrambled.csv`, `datashifted_withoffset.csv`, `datasrs.csv`, `changepoint.csv` — while `datashifted.csv` duplicates `datashifted_withoffset.csv` without the `int`/`cond` columns)
- PDF: https://www.biorxiv.org/content/10.1101/432534v2.full.pdf
- Full text: https://www.biorxiv.org/content/10.1101/432534v2
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Schulz, E., Franklin, N. T., & Gershman, S. J. (2020). Finding structure in multi-armed bandits. Cognitive Psychology, 119, 101261. https://doi.org/10.1016/j.cogpsych.2019.101261

## Experiment summary
Five online multi-armed bandit experiments, each run on mechanical Turk: participants repeatedly choose among 8 arms arranged spatially (left-to-right), collecting noisy rewards whose expected value follows a latent function of arm position — linear gradient (Exp 1, N=119), scrambled rewards (Exp 2, N=82), linear with per-round random intercept (Exp 3, N=131), dynamics of structure learning with SRS/RSR block schedules (Exp 4, N=113), and change-point functions (Exp 5, N=159). Responses are single-key arm choices on each of 10 trials per round, with 30 fresh bandits (rounds) per participant; reward outcome and sometimes response time are recorded per trial. The research question is whether humans detect and exploit latent functional structure among options to guide exploration–exploitation (learning-to-learn across rounds); analysis compares hierarchical Bayesian models of Gaussian-process function learning, clustering of reward distributions, and uncertainty-guided exploration, and all three headline effects of Experiment 1 (structure reward benefit, within-round learning, and learning across rounds) reproduce on these files.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (lindata.csv, 1..119), Experiment 1 (Linear structure) |
| task_id | 0-indexed round (source `round` 1..30); each round is a fresh bandit with a new latent reward function |
| trial | 0..9 within each (participant_id, task_id), source `trial` 1..10 |
| response | 0-indexed chosen arm (source `arm` 1..8, grid keys A S D F J K L ;); 0 = leftmost arm |
| condition | Source `cond`: `ran` = random, `pos` = increasing linear gradient, `neg` = decreasing linear gradient |
| round | Raw source round number 1..30 (duplicate of task_id+1, kept verbatim) |
| arm | Raw source chosen arm 1..8 (response+1, kept verbatim) |
| reward | Raw delivered reward (`out`) in points, noisy sample of the latent arm value |
| rt | Source `time` in ms, kept verbatim; the source does not document what it is measured from (trial 1 of a round has a median of ~1.2 s, later trials ~0.33 s, below the paper's 2-s outcome display) |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (datascrambled.csv, 1..82), Experiment 2 (Scrambled; middle arms' rewards shuffled) |
| task_id | 0-indexed round (source `round` 1..30); each round is a fresh bandit with a new latent reward function |
| trial | 0..9 within each (participant_id, task_id), source `trial` 1..10 |
| response | 0-indexed chosen arm (source `arm` 1..8); 0 = leftmost arm |
| round | Raw source round number 1..30 (duplicate of task_id+1, kept verbatim) |
| arm | Raw source chosen arm 1..8 (response+1, kept verbatim) |
| reward | Raw delivered reward (`out`) in points, noisy sample of the latent arm value |

#### exp2
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (datashifted_withoffset.csv, 1..131), Experiment 3 (Linear structure with random intercepts). Source `datashifted.csv` is the same dataset without per-round intercept and condition columns, so the superset file is used |
| task_id | 0-indexed round (source `round` 1..30); each round is a fresh bandit with a new latent function and a new random intercept |
| trial | 0..9 within each (participant_id, task_id), source `trial` 1..10 |
| response | 0-indexed chosen arm (source `arm` 1..8); 0 = leftmost arm |
| round | Raw source round number 1..30 (duplicate of task_id+1, kept verbatim) |
| arm | Raw source chosen arm 1..8 (response+1, kept verbatim) |
| reward | Raw `out` value in points: the un-shifted latent-function sample f(arm) + noise, in ~[1, 49]. The round's intercept is stored separately in `intercept`; the value shown on screen was `reward + intercept` (paper p. 22; the source's own modeling code, `get_bayesian_gp_means_std.py`, uses `out + int` as the reward), and the bonus was computed without the intercept |
| intercept | Source `int`: the round's random intercept beta_0 ~ U[0,50] that was added on screen to every arm's reward that round; constant within a round and not included in `reward` |
| condition | Source `cond` (`ran`/`pos`/`neg`), kept verbatim. Caution: this column does not label the round's actual latent function. It is one fixed 30-round sequence, identical for all 131 participants (the paper, p. 22, interleaved the conditions at random), and the per-round rank correlation between arm and reward is centred on 0 under every label (in `pos` rounds where both extreme arms were sampled, the right arm paid more in 374 of 815). The source's own notebook (`Posterior Predictive Checks.ipynb`) discards it and reconstructs the condition from the rewards |

#### exp3
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (datasrs.csv, 1..113), Experiment 4 (Dynamics of structure learning, SRS vs RSR group). Group (10 structured + 10 random + 10 structured rounds vs reverse) is not recorded in the file; it is recoverable from the per-round reward structure |
| task_id | 0-indexed round (source `round` 1..30); each round is a fresh bandit |
| trial | 0..9 within each (participant_id, task_id), source `trial` 1..10 |
| response | 0-indexed chosen arm (source `arm` 1..8); 0 = leftmost arm |
| round | Raw source round number 1..30 (duplicate of task_id+1, kept verbatim) |
| arm | Raw source chosen arm 1..8 (response+1, kept verbatim) |
| reward | Raw delivered reward (`out`) in points, noisy sample of the latent arm value |

#### exp4
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (changepoint.csv, 1..159), Experiment 5 (Change-point structure) |
| task_id | 0-indexed round (source `round` 1..30); each round is a fresh bandit with a new latent change-point function |
| trial | 0..9 within each (participant_id, task_id), source `trial` 1..10 |
| response | 0-indexed chosen arm (source `arm` 1..8); 0 = leftmost arm |
| condition | Source `cond`: `structure` = latent change-point kernel functions, `random` = matched scrambled (all but best arm shuffled) |
| round | Raw source round number 1..30 (duplicate of task_id+1, kept verbatim) |
| arm | Raw source chosen arm 1..8 (response+1, kept verbatim) |
| reward | Raw delivered reward (`out`) in points, noisy sample of the latent arm value |
| rt | Source `time` in ms, kept verbatim; the source does not document what it is measured from (trial 1 of a round has a median of ~1.2 s, later trials ~0.33 s, below the paper's 2-s outcome display) |

Experiment mapping: exp0–exp4 correspond to the paper's Experiments 1–5. Participant counts reported in the paper's Participants subsections (116/91/144/120/159) differ from the raw-file participant counts (119/82/131/113/159; only exp4/Experiment 5 agrees); raw files were emitted as-is. Experiment 4's SRS/RSR group assignment is not recorded in the data file.

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Indeterminate: the winning model (hybrid GP-RBF + Clustering, best by PSIS-LOO in every experiment, Tables D1–D5) cannot be reproduced faithfully in this harness. It requires a Clustering model with discrete particle variational inference over a CRP partition of rounds (non-differentiable, sequential) combined with a Gaussian Process, fit via hierarchical Bayesian MCMC (PyMC3) and compared on PSIS-LOO. The bounded per-participant MAP / jitted-JAX fit available here cannot represent the particle-based clustering or the hierarchical-Bayesian+PSIS-LOO comparison; any implementable version would materially simplify the paper's model. Required columns (participant_id, task_id, response, reward, trial) are all present; this is a model-fidelity blocker, not a data gap. Behavioral analyses (reward over trials/rounds, generative simulations) are out of scope.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

All five experiments got a runnable static jsPsych v8 build under `experiments/expN/`
(exp0–exp4), each reproducing the multi-armed bandit (8 arms, 30 rounds × 10 trials)
from the paper. The headless `?mode=simulate` round trip **passed** for all five:
the saved CSV matches each `expN.csv` schema exactly on columns, dtypes, codings and
counts (trial 0..9 per `task_id`, `arm = response + 1`, `round = task_id + 1`), and
rewards/`rt`/`intercept` are populated. No experiment was skipped.

Two caveats worth surfacing (details in `experiments/README.md`):
- **exp2 reward magnitude.** The paper (Exp 3, Fig. 10) states a random intercept
  `β0 ~ U[0,50]` is added to every arm's reward each round, so rewards reach ~100; this
  build implements that. The stored `exp2.csv` caps rewards around [2,48] and is
  essentially uncorrelated with `intercept` (a dataset-construction artifact), so this
  build matches `exp2.csv` on schema/coding/counts but not on reward magnitude.
- **Wording reconstruction.** The paper does not quote its verbatim on-screen
  instructions and the original task code (`ericschulz.github.io/explin/indexN.html`)
  is offline (all links 404), so instruction text was reconstructed from the paper's
  Design/Procedure description, and the unreadable comprehension-check figure (Fig. A1)
  was omitted. Both are documented as `ASSUMPTION:` in each `index.html`.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Text-format conversion

All five experiments (exp0–exp4, the paper's Experiments 1–5) were transcribed into
`transcripts0.jsonl`–`transcripts4.jsonl` — one natural-language transcript per
participant, covering all 30 rounds × 10 trials of the multi-armed bandit. Choices are
rendered as the keyboard keys the participant pressed (`A S D F J K L ;`); the per-round
latent condition (e.g. `pos`/`neg`/`ran`) is deliberately not narrated because participants
never saw it, and exp4's between-subjects `condition` (`structure`/`random`) is carried as a
per-line metadata field. No experiment was skipped. Note: exp2 narrates the on-screen value
`reward + intercept` (the stored `reward` excludes the round's intercept); `rt` values are
measured, not observed, so they are not narrated.

Sample transcript (exp0, participant 2, up to the first response):

```
In this game you play 30 rounds of a slot-machine task. Each round, eight boxes are arranged left to right and labeled with the keys you press to choose them: A, S, D, F, J, K, L, and ; (semicolon), leftmost to rightmost. Each round has 10 trials. On each trial you press one key to sample that box, and you then see how many points that box gave you this time. Your goal is to gain as many points as possible. After each round the game resets: the same keys can now give different points, so treat every round afresh.

Round 1 of 30.
Trial 1: You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

All five experiments got a text simulator (`simulate0.py`–`simulate4.py`), one per
transcribed `expN.csv`, and each passed the round-trip check (the simulated DataFrame
regenerated through `build_jsonl.py` reproduces the simulator's own prompts
byte-identically; the key-to-arm mapping is fixed, so no token normalization was needed).
No experiment was skipped. Design follows the paper (bioRxiv 432534): Exp 1 linear
pos/neg/ran rounds (~min U[2,10], max U[40,48]); Exp 2 scrambled middle options; Exp 3
linear + random intercept β0 ~ U[0,50] (the DataFrame's `reward` is the un-shifted value
and `intercept` = β0, as in `exp2.csv`; the narrated points are `reward + intercept`, what
participants saw); Exp 4 SRS/RSR schedules with group assigned at random per
participant (not recorded in the file); Exp 5 change-point functions with peak at each of
the six middle arms in 5 rounds each. One ASSUMPTION across experiments: the paper states
reward noise ε ~ N(0, 0.1), but the shipped data show ~0.3 within-round scatter, so
ε ~ N(0, 0.3) is used.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 1, major 3, minor 3; fixed 5, open 2).

Checked: paper (bioRxiv PDF https://doi.org/10.1101/432534, 73 pages; Cognitive Psychology DOI 10.1016/j.cogpsych.2019.101261), original data (github.com/nicktfranklin/StructuredBandits, commit db3ae4f, Data/exp_*/ five raw CSVs), exp0-exp4, transform re-run (all five CSVs byte-identical), transcripts (build_jsonl.py regenerates all five byte-for-byte), simulators (all five run; build_jsonl round trip byte-identical), modeling (no model.py; the section and the cognitive-modeling:needs-review tag agree), analysis (3 of 3 Experiment 1 effects reproduce), logs. Skipped: none.

Fixed:
- critical: transcripts2.jsonl narrated the stored `reward` (source `out`, max 48.8), but Experiment 3 participants saw the shifted value: the paper (p. 22) adds a per-round intercept beta0 ~ U[0,50] on screen, and the source's own modeling code (`get_bayesian_gp_means_std.py`, line 149) uses `out + int` as the reward. build_jsonl.py now narrates `reward + intercept` for exp2 (participant 1, round 1, trial 1: 10.21 -> 40.91 points); transcripts2.jsonl rebuilt (131 transcripts; transcripts0/1/3/4 unchanged byte-for-byte); the Text-format note updated.
- major: README exp2 `reward` and `intercept` rows called the near-zero correlation between `reward` and `intercept` (r = 0.05) a dataset-construction artifact. It holds by construction: `out` is the un-shifted function value and `int` the intercept, stored separately. Rows rewritten with the evidence.
- major: README exp2 `condition` row described source `cond` as the round's latent-function condition. The column is one fixed 30-round sequence identical for all 131 participants (paper p. 22: conditions interleaved at random), the per-round Spearman(arm, reward) is centred on 0 under every label (in `pos` rounds where both extreme arms were sampled the right arm paid more in 374 of 815), and the source notebook `Posterior Predictive Checks.ipynb` discards it and reconstructs the condition from the rewards. Column kept verbatim; the row now says it does not label the round's actual function.
- major: simulate2.py stored `reward` = f(arm) + beta0 (up to ~100) while exp2.csv stores the un-shifted value. It now stores the un-shifted reward and narrates `reward + intercept`; the build_jsonl round trip is byte-identical for 3 simulated participants; the Simulators note updated.
- minor: README exp0 and exp4 `rt` rows said 'time since previous trial onset'; the source documents no anchor, and trials 2-10 have a median of ~330 ms, below the paper's 2-s outcome display (pp. 9-10). Reworded.

Open:
- minor: the paper's Participants subsections report N = 116/91/144/120/159 (pp. 8, 16, 21, 26, 31); the source files hold 119/82/131/113/159 and document no exclusions. The transform re-run shows the CSVs are faithful to the source; noted in the README.
- minor: the paper states reward noise eps ~ N(0, 0.1) (p. 11); the within-round, within-arm reward sd in exp0 is 0.28 (median) to 0.32 (mean), which fits a variance of 0.1 rather than an sd of 0.1. Inside the source; the simulators document eps ~ N(0, 0.3).

Run: claude-fable-5-1, 2026-09-14
