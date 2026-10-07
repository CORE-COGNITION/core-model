---
tags:
- paradigm:bandit
- cognitive-modeling:pass
- psych-201
- js-experiment:needs-review
- text-format:pass
- simulator:pass
- verification:pass
---
# chambon_2020_information

- Paper: https://doi.org/10.1038/s41562-020-0919-5
- Data source: https://github.com/spalminteri/agency
- Full text: https://www.nature.com/articles/s41562-020-0919-5
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Chambon, V., Théro, H., Vidal, M., Vandendriessche, H., Haggard, P., & Palminteri, S. (2020). Information about action outcomes differentially affects learning from self-determined versus imposed choices. Nature Human Behaviour. https://doi.org/10.1038/s41562-020-0919-5

## Experiment summary
Four experiments (N = 24, N = 24, N = 30 and N = 17 data files, respectively) test how the source of an action (free vs forced choice), outcome contingencies (high vs low reward; 50/50 vs 70/30), outcome information (factual vs counterfactual) and motor requirements (key press vs no key press, i.e. go vs no-go) modulate a confirmation/valence bias in learning. In each, participants perform a probabilistic two-armed bandit learning task in blocks that each use a fresh pair of symbols, with free vs forced choice trials (Experiments 1-3), factual vs counterfactual outcome presentation (Experiment 2), and (in Experiment 4) symbol selection by a key press or by withholding it; the response is a symbol choice plus reaction times, with RL models fit to estimate learning rates. Each experiment is delivered as a separate `expN.csv`; `task_id` is the 0-indexed block (a fresh symbol pair, i.e. a task reset) and `condition_code` the source's condition number. Analyses here reproduce the confirmation-bias free-choice learning (Exp 1), the counterfactual-feedback learning benefit (Exp 2), and go/no-go motor-independence of learning (Exp 4).

## Notes

### Columns

#### exp0
Experiment 1 (24 participants) — classic free-vs-forced-choice confirmation-bias bandit task. Rows are trials from the `M` matrix of each `passymetrieI_SujN.mat` file, in presentation order.
| column | description |
|--------|-------------|
| participant_id | Remapped subject number (`SujN` -> `P000`, `P001`, ... in file-name order). |
| subject_number | Original subject number from the source file name (`SujN`; 1..24). |
| session | Session number (1..3). Each participant had breaks between sessions. |
| condition_code | Condition number 1..4. 1 & 2 = high-reward blocks (reward probs 90%/60%), 3 & 4 = low-reward blocks (40%/10%). Conditions 1 & 3 = free-choice-only blocks; conditions 2 & 4 = free- and forced-choice trials intermixed. |
| trial_in_block | Trial number within a block (1-indexed, resets at each block start). |
| outcome_best | Outcome (+1 win / -1 loss) of the best-rewarded stimulus; 0 = forced-choice trial where the best symbol was not shown. |
| outcome_least | Outcome (+1 / -1) of the least-rewarded symbol; 0 = forced-choice trial where it was not shown. |
| response | Participant's choice: 1 = chose the best-rewarded symbol, 0 = chose the least-rewarded one. |
| forced_choice | 1 = forced-choice (experimenter-imposed) trial, 0 = free-choice trial (source column 7 inverted; the source codes free = 1). |
| rt | Reaction time in milliseconds for selecting the symbol (source seconds x 1000; values below 1 ms occur in the source and are kept as recorded). |
| rt_confirm | Reaction time in milliseconds for confirming the outcome (source seconds x 1000; recorded on every trial, also in free-choice-only blocks). |
| task_id | 0-indexed block within the participant (12 blocks; every block is a fresh pair of symbols, i.e. a task reset), in presentation order. |
| trial | 0-indexed trial within each (participant_id, task_id) block (= trial_in_block - 1). |

#### exp1
Experiment 2 (24 participants) — factual-only vs factual-and-counterfactual outcome-information version. Rows are trials from each `passymetrieII_SujN.mat` file.
| column | description |
|--------|-------------|
| participant_id | Remapped subject number (`SujN` -> `P000`, `P001`, ...). |
| subject_number | Original subject number from the file name (`SujN`; 1..24). |
| session | Session number (1..4). |
| condition_code | Condition 1..4. 1 & 2 = high-reward blocks, 3 & 4 = low-reward blocks; conditions 1 & 3 show only the factual outcome, conditions 2 & 4 show both factual and counterfactual outcomes. |
| trial_in_block | Trial number within a block (1-indexed). |
| outcome_best | Outcome (+1 / -1) of the best-rewarded stimulus (recorded on every trial, forced trials included; never 0 in this experiment). |
| outcome_least | Outcome (+1 / -1) of the least-rewarded symbol (recorded on every trial, forced trials included; never 0 in this experiment). |
| response | Participant's choice: 1 = chose best-rewarded symbol, 0 = chose least-rewarded. |
| forced_choice | 1 = forced-choice (experimenter-imposed) trial, 0 = free-choice trial (source column 7 inverted; the source codes free = 1). |
| rt | Reaction time in milliseconds for selecting the symbol (source seconds x 1000; values below 1 ms occur in the source and are kept as recorded). |
| rt_confirm | Reaction time in milliseconds for confirming the outcome (source seconds x 1000; recorded on every trial, also in free-choice-only blocks). |
| task_id | 0-indexed block within the participant (16 blocks; every block is a fresh pair of symbols, i.e. a task reset), in presentation order. |
| trial | 0-indexed trial within each (participant_id, task_id) block (= trial_in_block - 1). |

#### exp2
Experiment 3 (30 participants) — variant that does not record an outcome-confirmation reaction time. Rows are trials from each `Bias_N.mat` file.
| column | description |
|--------|-------------|
| participant_id | Remapped subject number (`Bias_N` -> `P000`, `P001`, ...). |
| subject_number | Original subject number from the file name (`Bias_N`; 1..30). |
| session | Session number (1..3). |
| condition_code | Condition 1..4. 1 & 2 = random blocks (both symbols win 50% of the time), 3 & 4 = instrumental blocks (the better symbol wins 70%, the other 30%); conditions 1 & 3 = free-choice-only blocks of 20 trials, 2 & 4 = intermixed free- and forced-choice blocks of 40 trials. The source readme's high/low-reward description covers Experiments 1-2 only; this mapping was recovered from the data (`outcome_best` wins on 50% of the trials in conditions 1-2 and on 70% in conditions 3-4). |
| trial_in_block | Trial number within a block (1-indexed). |
| outcome_best | Outcome (+1 / -1) of the best-rewarded stimulus (recorded on every trial, forced trials included). |
| outcome_least | Outcome (+1 / -1) of the least-rewarded symbol (recorded on every trial, forced trials included). |
| response | Participant's choice: 1 = chose best-rewarded symbol, 0 = chose least-rewarded. |
| forced_choice | 1 = forced-choice (experimenter-imposed) trial, 0 = free-choice trial (source column 7 inverted; the source codes free = 1). |
| rt | Reaction time in milliseconds for selecting the symbol (source seconds x 1000). (Outcome-confirmation RT was not recorded in this experiment, so `rt_confirm` is absent.) |
| task_id | 0-indexed block within the participant (12 blocks; every block is a fresh pair of symbols, i.e. a task reset), in presentation order. A block starts where `trial_in_block` is 1; in 11 participants the source's `session` number changes inside one block (its trials 21-40 carry the next session number). |
| trial | 0-indexed trial within each (participant_id, task_id) block (= trial_in_block - 1). |

#### exp3
Experiment 4 (17 data files; the paper analysed 20) — go/no-go motor-requirement version: on every trial a key press within 1,500 ms takes the symbol on the participant's instructed side, no key press takes the other symbol, so whether a trial is go or no-go is the participant's own choice. Rows are trials from each `Datago_N.mat` file, which has an 11-column layout (the source readme documents columns 1-9 only), in presentation order.
| column | description |
|--------|-------------|
| participant_id | Remapped subject number (`Datago_N` -> `P000`, `P001`, ...). |
| subject_number | Original subject number from the file name (`Datago_N`). |
| session | Session number (1..3). |
| condition_code | Condition 1..2 as recorded in this experiment's files: 1 = random block (both symbols win 50% of the time), 2 = instrumental block (the better symbol wins 70%, the other 30%); recovered from the data's outcome rates (the paper says the contingencies were those of Experiment 3). |
| trial_in_block | Trial number within a block (1-indexed). |
| outcome_best | Outcome (+1 / -1) of the best-rewarded stimulus. |
| outcome_least | Outcome (+1 / -1) of the least-rewarded symbol. |
| response | Participant's choice: 1 = chose the best-rewarded symbol, 0 = chose the least-rewarded one. |
| chosen_side | Source column 7: +1 / -1 code of the side (screen position / key side) of the chosen symbol; `response` is 1 exactly when `chosen_side` equals `best_side`. The source readme calls this column go (-1) / no-go (1); in the data that holds for subjects 11-19 only, whose key press selects side -1, whereas the key press of subjects 1-10 selects side +1 (see `go`). |
| rt | Reaction time in milliseconds of the key press (source seconds x 1000); no-go trials carry the 1,500 ms response deadline (about 1,500-1,515 ms). |
| go | Source column 9: 1 = a key press within the 1,500 ms window selected the symbol (go trial), 0 otherwise. |
| nogo | Source column 10: 1 = no key press, the other symbol was selected at the deadline (no-go trial), 0 otherwise. `go` + `nogo` = 1 on 99% of the trials; 86 trials have both 0 (a key press with rt < 1.5 s that still selected the no-press symbol) and 7 have both 1 (a press at the deadline). |
| best_side | Source column 11: +1 / -1 code of the side of the best-rewarded symbol (balanced per trial); with the participant's key-press side it tells which symbol a key press would take. |
| task_id | 0-indexed block within the participant (6 blocks of 100 trials; every block is a fresh pair of symbols, i.e. a task reset), in presentation order. |
| trial | 0-indexed trial within each (participant_id, task_id) block (= trial_in_block - 1). |

Note: the paper recruited 24 participants for Experiment 4 and analysed 20 (four were excluded for pressing a key on no-go trials more than 35% of the time; Methods p. 1076 and Supplementary Table 1). The source readme says 20 data files, but the repository ships 17 (`Datago_1`-`Datago_5` and `Datago_8`-`Datago_19`: numbers 6 and 7 are missing from the 1-19 sequence and there is no 20th file); this is a source-repository limitation, not a transform error.

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: asymmetric-learning-rate Q-learning / Rescorla-Wagner with softmax choice (Chambon et al. 2020 'Computational modelling'); exp0 models q2/q3/q4 (BIC-based model selection) and exp1 models q6/q3conf.
Reproduced: confirmation_bias_free_choice (positive free-choice learning rate exceeds negative, but no significant forced-choice valence bias; exp0); parsimony_free_bias (the free-only-bias intermediate 3alpha model wins exp0 by BIC model selection); counterfactual_confirmation_model (the confirmation 3alpha model wins exp1).
Not reproduced: none.
Numeric mismatch: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Four static jsPsych v8 experiments were built under `experiments/` (exp0–exp3, one per
`expN.csv`), each recording a CSV in that file's own schema; the headless round trip
(`?mode=simulate`) ran and validated all four (column names, dtypes/codings, and trial
counts match). Status is **needs-review**: Experiments 1–3 are recovered faithfully, but
Experiment 4's go/no-go stimulus arrangement and its go/no-go → `response`/`outcome_code`
mapping are substantive reconstructions (the Nature Methods and the Psychtoolbox task
code are unavailable), and the on-screen instruction wording for all four is rebuilt from
the design rather than the authors' verbatim text. See `experiments/README.md`.
Assumption note: session/block break points and block ordering are normalized for the
online presentation; they do not change per-condition trial counts or codings.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Text-format conversion

All four experiments were transcribed (exp0.csv → transcripts0.jsonl, 24; exp1.csv →
transcripts1.jsonl, 24; exp2.csv → transcripts2.jsonl, 30; exp3.csv → transcripts3.jsonl,
17). Each is a two-armed bandit with abstract symbol stimuli that carry no nameable
features, so describing the pair in words neither trivializes the choice nor removes the
information participants learned from; free-vs-forced choice (Exps 1–3) and the key-press
vs no-key-press selection mode (Exp 4, whose free choice of symbol is preserved) are both
expressible in text. None skipped. Because the source never names the two symbols, each
transcript uses one letter pair per participant (pair and letter→best mapping randomized
per participant and stated in the instructions, so the response token set is recoverable
from the text alone); the same two letters name the fresh symbol pair of every block.
Blocks are narrated in presentation order (`task_id`), each opened by a "Block begins"
line with the session number; the block's reward schedule is not stated, because
participants were told only that one symbol wins more often than the other. Free choices
are marked with [HUMAN_RESPONSE]; forced trials are narrated as instructed ("You are
instructed to take D. D wins a point.") and the instructions say that their outcome is not
added to the participant's points, as in the paper. In Exp 2's complete blocks the
unchosen symbol's outcome is narrated on free and forced trials alike. In Exp 4 every
trial states which symbol the key press takes (from `best_side` and the participant's
key-press side, recovered from the `go` trials), the participant's pick is the marked
response, and the outcome is the chosen symbol's outcome.

Sample transcript (exp0, participant P000, from the start up to the first marked response):

```
Your task is to learn which of the two symbols in front of you is more rewarding. Each symbol has a hidden, fixed probability of winning you a point (+1) or losing you a point (-1) that stays the same for a whole block; at the start of each block a fresh pair of symbols is used, so the hidden probabilities can differ between blocks. In every block the two symbols are called A and Z. On each trial the block's two symbols are shown, and you choose one by typing its single-letter name (A or Z). After your choice the outcome is revealed. On some trials the choice is imposed rather than free: you are instructed to take a specified symbol, and you must take it; the outcome of an imposed trial is shown to you but is not added to your points. After each outcome you press the confirm key, and then the next trial begins.
Block begins (Session 1): a fresh pair of symbols, called A and Z.
Symbols A and Z shown. You press [HUMAN_RESPONSE]Z[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

All four experiments were simulated (`simulate0.py`–`simulate3.py`); each round-trip check passed — the simulator output re-run through `build_jsonl.py` is byte-identical to the simulator's own prompts. Reward contingencies follow the paper (Exps 1-2: 90/60 & 40/10; Exps 3-4: 50/50 & 70/30), with the block/session layout taken from the data (one block per condition per session, in random order). Notable assumptions: Exp 3's condition→schedule mapping was recovered from the data (conditions 1&2 are the 50/50 random schedule, 3&4 the 70/30 instrumental one), and so was Exp 4's (condition 1 random, condition 2 instrumental); in Exp 4 the best symbol sits on the key-press side on a random half of the trials and the key-press side code is +1 for every simulated participant. `rt` (and `rt_confirm`) are simulated as uninformative noise in milliseconds; in Exp 4 go trials get an rt below the 1,500 ms deadline and no-go trials an rt at the deadline. None skipped.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 2, major 14, minor 8; fixed 16, open 6).

Checked: paper (doi 10.1038/s41562-020-0919-5, HAL accepted manuscript hal-03039404 and the Springer supplementary PDF), original data (https://github.com/spalminteri/agency, cloned), exp0-exp3, transform re-run (byte-identical to the uploaded CSVs before the fixes), transcripts (rebuild and token mapping), simulators (smoke test and byte-identical round trip through build_jsonl.py), modeling (model.py re-run: all three results reproduce), analysis (analysis.py: all three effects reproduce), logs. Skipped: none.

Fixed:
- critical: transcripts3.jsonl narrated source column 11 (named outcome_code) as the outcome, but it is a +/-1 side code unrelated to the chosen symbol's outcome, and the intro announced GO/NO-GO cues although the paper (p. 1069, p. 1077) makes go/no-go the participant's own way of selecting a symbol; build_jsonl.py now narrates which symbol the key press takes and the chosen symbol's outcome; transcripts3.jsonl rebuilt, simulate3.py mirrored.
- critical: transcripts2.jsonl block labels were inverted (conditions 1-2 called high-reward while outcome_best wins 50% there, 3-4 called low-reward while they are 70/30; the same inversion in transcripts3.jsonl); the block line now states only the session, since the paper (p. 1077) says participants got no information about the probabilities; transcripts0-1.jsonl likewise no longer state the 90/60 and 40/10 probabilities.
- major: transcripts randomized the letters per block and always named the better symbol first; now one letter pair per participant in pool order with the best letter randomized per participant, so the token-to-response mapping is one-to-one within a transcript (checker: 95/95 transcripts map).
- major: transcripts1.jsonl showed the counterfactual outcome on free trials only; the paper (p. 1077) shows it on every complete trial and model.py updates the unchosen option on forced trials too; now narrated on forced trials as well.
- major: forced (observer) trials were narrated as 'You win a point' although their outcome is not added to the participant's points (p. 1077); now 'You are instructed to take D. D wins a point.' with the rule stated in the instructions.
- major: transcripts were ordered by condition, not presentation order, which merged two consecutive same-condition blocks of Experiment 3 into one; blocks now start at trial_in_block == 1 in file order.
- major: rt and rt_confirm were in seconds (medians 0.37-1.5); transform.py converts to milliseconds; README, simulators updated.
- major: exp0-exp2 carried free_choice (1 = free) instead of the schema's forced_choice; transform.py now writes forced_choice = 1 - free_choice; build_jsonl.py, simulators, model.py, analysis.py and README updated.
- major: exp3.csv named source columns 7, 9, 10, 11 go_nogo, nogo_response, go_response, outcome_code; the data show column 9 = key press within 1.5 s (go; rt < 1.5 s on 100% of these rows), column 10 = no press (rt at the 1.5 s deadline), response == (column 7 == column 11) on 10,200/10,200 rows, column 11 balanced +/-1 (side of the best symbol) and column 7 the side of the chosen symbol (key-press side +1 for subjects 1-10, -1 for 11-19); renamed chosen_side, go, nogo, best_side and documented; analysis.py's go/no-go test now uses go/nogo (still reproduces, effect 0.143 vs 0.15).
- major: task_id was the condition (4 values) with trial running across the fresh-symbol blocks of a condition; the schema makes every fresh pair a task reset, so task_id is now the 0-indexed block in presentation order (12/16/12/6 per participant) and trial = trial_in_block - 1; model.py takes the complete blocks from condition_code and analysis.py the conditions from condition_code; all modeling and analysis results still reproduce.
- major: README described exp2 conditions 1-2 as high-reward and 3-4 as low-reward; they are the random 50/50 and the instrumental 70/30 blocks (data; paper p. 1077).
- major: README's Experiment 4 note said subjects 6, 7, 14-17 are absent and 18 were analysed; the source ships Datago_1-5 and 8-19 (17 files) and the paper analysed 20 of 24 (p. 1076, Supplementary Table 1).
- major: README Simulators section gave Experiment 4 a single 70/30 schedule and the Text-format section called the Exp 4 outcome linkage unrecoverable; both rewritten (condition 1 is 50/50, condition 2 is 70/30).
- major: logs/auto-exp-modeling.sessions.json carried a README diff of jansen_2021_rational from a stale work dir in its first message; that diff entry was removed.
- minor: README title, '####' column headings, per-experiment N claims and the sample transcript brought in line with the template and the rebuilt transcripts.
- minor: README exp1 outcome rows said 0 marks a forced trial; both outcomes are recorded on every trial of Experiment 2.

Open:
- minor: the paper recruited 24 and analysed 20 participants in Experiment 4 (p. 1076); the source readme says 20 files, the repository ships 17 (numbers 6, 7 and 20 missing); documented in the README.
- minor: the training block (60 trials in Exp 1, 40 in Exps 2-4, at 0.5 reward probability; p. 1077) is not in the source.
- minor: the paper's Methods say Experiment 2 had eight blocks of 40 trials per condition (p. 1077), while its Supplementary Table 1 and the data have four per condition (640 trials); the data agree with the table.
- minor: in 11 participants of Experiment 3 the source's session number changes inside one 40-trial block; kept as recorded and documented.
- minor: rt values below 1 ms (5th percentile about 1 ms) and rt_confirm medians of 30-100 ms in Experiments 1-2 are kept as recorded; the source gives no timing reference.
- note: the checker's eight 'sentinel value -1' findings on outcome_best, outcome_least, chosen_side and best_side are false positives; -1 is a legitimate loss or side code in two-valued columns.

Run: claude-fable-5-1, 2026-09-09
