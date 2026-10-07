---
tags:
- paradigm:bandit
- cognitive-modeling:pass
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---
# bavard_2021_two

- Paper: https://doi.org/10.1126/sciadv.abe0340
- Data source: https://github.com/hrl-team/range
- Full text: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11060039/?report=reader
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Bavard, S., Rustichini, A., & Palminteri, S. (2021). Two sides of the same coin: Beneficial and detrimental consequences of range adaptation in human reinforcement learning. Science Advances, 7(14), eabe0340.

## Experiment summary
Participants (N=800, 100 per experiment across 8 experiments, 414 female/366 male, one sample from the Palminteri lab) performed a probabilistic instrumental learning task choosing between pairs of symbols with different reward values, manipulating context reward range (7.50 vs 2.50 or 0.75 vs 0.25 points) to study range adaptation in reinforcement learning. Each experiment had a training phase (12–24 familiarization trials), a learning phase (120 trials where symbols were associated with binary outcomes), and a transfer phase (120 trials with re-paired cross-range symbols). Experiments varied feedback type (partial/complete/none) and trial structure (interleaved vs blocked). The response is a binary choice (0=left, 1=right) with reaction times recorded. The research question is whether adaptive value rescaling produces both within-context benefits (better discrimination) and systematic extrapolation errors when values move between contexts. The paper also fits computational RL models (Q-learning, range-adaptation, habit, and utility variants) to the choice data, establishing this as a cognitive-modeling dataset.

## Notes

### Columns

The 8 experiment files (exp0–exp7) all share the same columns; within a file, each participant has ~252 rows.

| column | description |
|--------|-------------|
| participant_id | Anonymized participant identifier (P000–P099 per experiment, assigned in order of appearance in the source). Original Prolific IDs (large integers) were remapped. |
| task_id | 0 = training and learning phases (phases 0 and 1 in source), 1 = transfer phase (phase 2). Trial restarts at 0 per (participant_id, task_id). |
| phase | `training` (12 or 24 familiarization trials; 3 participants in exp6 have one training trial fewer in the source), `learning` (120 trials learning symbol values with feedback), `transfer` (120 trials of re-paired symbols). |
| trial | 0-indexed trial number within each (participant_id, task_id). |
| context | Context number (1–8) from the source. 1–4: learning-phase contexts (two with 7.50 vs 2.50 pairs, two with 0.75 vs 0.25 pairs). 5–8: transfer-phase contexts with cross-range symbol pairs. |
| context_label | Human-readable label for the context, e.g. `7.50_vs_2.50_learning`. The numbers are the expected values of the two symbols in points (7.50 = 10 pt × 0.75, 2.50 = 10 pt × 0.25, 0.75 = 1 pt × 0.75, 0.25 = 1 pt × 0.25). |
| left_symbol | The symbol (1–8) presented on the left side of the screen. NaN on no-response trials. |
| right_symbol | The symbol (1–8) presented on the right side of the screen. NaN on no-response trials. |
| choice_set | JSON list `[left_symbol, right_symbol]` of the two options on that trial. |
| response | Binary choice: 0 = left symbol selected, 1 = right symbol selected. NaN on no-response trials (valid=0). |
| correct | 0 = incorrect, 1 = correct (relative to the symbol with higher expected value in that context). NaN on no-response trials. |
| outcome_chosen | Binary outcome of the chosen option: 0 = null outcome (0 pts), 1 = positive outcome (1 or 10 pts, depending on context). Recorded on every trial in every experiment, including the transfer phase of exp0, 2, 4, 6, where the participant did not see it. NaN on no-response trials only. |
| outcome_unchosen | Binary outcome of the unchosen option: 0 = null, 1 = positive. Recorded on every trial in every experiment; participants saw it only in the complete-feedback experiments (exp2, 3, 6, 7), and there not in the transfer phase of exp2 and exp6. NaN on no-response trials only. |
| rt | Reaction time in milliseconds. NaN on no-response trials. |
| cumulated_reward | Running cumulative point total: starts at 0 in training, resets to 0 at the start of the learning phase, and continues through the transfer phase without a reset (also in the experiments without transfer feedback). |
| trial_original | Original trial number from the source (0-indexed within each phase). |
| trial_order | 1 = interleaved trials (exps 0–3), 2 = blocked trials (exps 4–7). |
| valid | 1 = response recorded, 0 = no response (missed trial). |
| age | Participant age in years. NaN where unavailable (18 participants). |
| sex | Raw demographic sex code from the source: 0 = male (366 participants), 1 = female (414 participants). NaN where unavailable (20 participants). |
| gender | Canonical gender label: `m` for sex=0, `f` for sex=1. NaN where sex unavailable. |

The primary behavioral effects reproduce on the local CSVs: choice accuracy is above chance overall (learning), choice behavior differs across narrow vs wide reward-range contexts (partial range adaptation), and choices in the transfer phase systematically go below chance for the highest-conflict cross-range pair (extrapolation error). Source data is a single MATLAB `data.mat`; experiment identity is carried in the trial-order/blocking structure and the per-participant phase structure, and the 100 participants per experiment are already separated in the source.

## Text-format conversion

All 8 experiments (exp0–exp7) were transcribed (one `transcriptsN.jsonl` per experiment). They share the same textifiable design: a two-armed probabilistic learning task with abstract-symbol stimuli and left/right click responses. Each transcript narrates the session in order (training → learning → transfer), naming the two symbols per trial and rendering the freely chosen click as `L`/`R`. Outcome narration follows the paper's per-experiment feedback design: the chosen outcome is narrated in the learning phase for all experiments (and in the transfer phase only for exp1,3,5,7, which provided transfer feedback), and the unchosen/counterfactual outcome is narrated only for the complete-feedback experiments (exp2,3,6,7). No experiment was skipped.

**Sample transcript** (exp0, first participant, truncated at first response):
```
Welcome. You are about to take part in an economic decision-making task. You will repeatedly see two abstract symbols on the screen, one on the left and one on the right. Each symbol is associated with points: some symbols can earn you 10 points, others can earn you 1 point, and on every trial you can earn the symbol's full value or 0 points. Your task is to learn, by trial and error, which symbols pay more. On each trial, two symbols appear. Click on the symbol of your choice. After your choice, the outcome is revealed: you see the number of points you won on that trial. The possible outcomes are 0, 1, and 10 points. Your final payoff depends on the points you earn (1 point = 0.005 GBP). Press L to choose the left symbol or R to choose the right symbol.
Trial 0: symbol 2 is on the left and symbol 1 is on the right. You press [HUMAN_RESPONSE]R[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result: the RANGE
model outperforming the ABSOLUTE model on out-of-sample log-likelihood (model
comparison). Both are delta-rule + softmax Q-learning models with per-symbol Q-values
carried across the learning and transfer phases; RANGE additionally normalizes each
context's rewards by its running maximum (alpha_R).
Fitted models: ABSOLUTE and RANGE, per-participant MLE (multi-start bounded L-BFGS),
compared on out-of-sample NLL — learning phase by 2-fold cross-validation over the
learning contexts, transfer phase by fitting on all learning trials and predicting the
transfer phase.
Reproduced: learning_range_over_absolute, transfer_range_over_absolute (RANGE wins the
out-of-sample NLL comparison in both phases).
Not reproduced: none.
Numeric mismatch: the learning-phase out-of-sample advantage reproduces only
directionally (RANGE 107.88 vs ABSOLUTE 109.14 out-of-sample NLL, t=0.58, p=0.56), much
weaker than the paper's reported t(799)=6.89, d=0.24; the transfer-phase advantage
reproduces robustly (RANGE 155.0 vs ABSOLUTE 201.5, t=6.15, p<0.0001, vs paper t(799)=
8.56, d=0.30).
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24
## Online experiment

All 8 experiments got a runnable static jsPsych v8 site under `experiments/expN/`
(one per `expN.csv`), rebuilt from the paper Methods and the CSV schema (the repo
has no `simulateN.py`). The headless round trip passed for all 8: each session
produces a CSV with the exact `expN.csv` columns and the correct per-`task_id`
trial counts (12 training + 120 learning in `task_id` 0, 120 transfer in
`task_id` 1). Timings (500 ms pre-feedback blank, 1000 ms outcome) are the
paper's; the cue glyphs, colors, and L/R click layout are cosmetic browser-only
defaults. Demographics (`age`/`sex`/`gender`) are left blank (the browser task
records only choices), and `rt` is recorded live in ms; the `saveData` seam
defaults to a CSV download with no backend.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

All 8 experiments got a text simulator (`simulate0.py`–`simulate7.py`), one per
`expN.csv` / `transcriptsN.jsonl`. Each builds a session-narration `prompt` (as in
the transcripts, gating feedback on the experiment's design) while drawing symbols,
outcomes (win probability 0.75 odd / 0.25 even symbols; payable magnitude 10 or 1),
context order (interleaved exps 0–3 / blocked exps 4–7), and left/right placement
from the generative process. The round-trip check passed for all 8: re-running the
repo's `build_jsonl.py` on each simulated DataFrame reproduces the simulated
prompts byte-for-byte. `ASSUMPTION` notes (familiarization length 12/24, p=0.5
left/right placement, `cumulated_reward` reset rule, no missed trials) are in each
class docstring.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 3, minor 7; fixed 6, open 4).

Checked: paper (10.1126/sciadv.abe0340, PMC11060039), original data (https://github.com/hrl-team/range: data.mat, demog.mat), exp0-exp7, transform re-run, transcripts, simulators (incl. round trip), modeling, analysis, logs. Skipped: none.

Fixed:
- logs/auto-exp-modeling.sessions.json embedded a git-status diff of another dataset's work dir (vantiel_2022_meaning README, exp0/exp1.csv, paper.html) in its first message and two patch parts; the foreign entries were removed.
- transform.py read ./mat_extract/{data,age,sex,subj}.npy, which the source does not ship (it has data.mat and demog.mat); it now loads raw/data.mat and raw/demog.mat with scipy.io. The re-run reproduces exp0-exp7.csv byte-for-byte.
- README said outcome_chosen/outcome_unchosen are NaN where no feedback was shown; the CSVs record both outcomes on every trial in every experiment (NaN only on the 34 no-response rows). The two rows now state what is recorded and which experiments displayed it.
- README gave 12-36 training trials; the data has 12 or 24 (3 participants in exp6 have 11 or 23 rows in the source). Summary and phase row corrected.
- README said cumulated_reward runs within the phase; it starts at 0 in training, resets at the start of learning, and continues through transfer (798/800 and 799/800 participants, the rest start a phase with a no-response row; every increment equals magnitude x outcome). Row corrected.
- README called the context_label numbers reward-point values; they are expected values (10 pt x 0.75 = 7.50 etc.); outcomes are 10, 1, or 0 points. Row corrected.

Open:
- minor: check_repo cannot map the summary's N=800 to the eight files of 100; the claim is correct (paper p. 13: 8 x 100) and was left as is.
- minor: the paper (p. 14) says each cue appeared equally often on the left and the right; in the source, per participant and context, the lower-numbered symbol is on the left 6-25 times out of 30. The data is faithful to the source; the simulators draw the side at p = 0.5, which matches the data.
- minor: 3 participants in exp6 have 11 or 23 training rows (one row missing, no no-response marker) in the source data.mat; kept as is and noted in the README phase row.
- minor: the transcript intro says the outcome is revealed after every choice and does not mention that exp0/2/4/6 show no outcome in the transfer phase or that exp2/3/6/7 also show the forgone outcome (paper p. 14 says participants were told). The narration itself is gated correctly per experiment; not changed.

Run: claude-fable-5-1, 2026-09-09
