---
tags:
- paradigm:category-learning
- cognitive-modeling:pass
- psych-101
- js-experiment:pass
- text-format:pass
- simulator:pass
- verification:pass
---
# badham_2017_deficits

- Paper: https://doi.org/10.1037/pag0000183
- Data source: https://osf.io/M7TCK/
- PDF: http://irep.ntu.ac.uk/id/eprint/30691/1/8441_Badham.pdf
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Badham, S. P., Sanborn, A. N., & Maylor, E. A. (2017). Deficits in category learning in older adults: Rule-based versus clustering accounts. Psychology and Aging, 32(5), 473-488. https://doi.org/10.1037/pag0000183

## Experiment summary
Ninety-six participants (48 younger, 48 older adults) performed four Shepard–Hovland–Jenkins category-learning structures (Types I–IV, varying in rule complexity) as binary two-choice classification tasks with feedback across up to 6 blocks of 16 trials each (a structure ended early once two consecutive blocks were perfect; N=96 total). Each trial records the stimulus features (size, colour, form), the participant's category response, feedback, correctness, and reaction time. The study asks whether age-related category-learning deficits are best explained by rule-based accounts (e.g., COVIS) or a clustering account in which older adults build fewer/less differentiated prototypes, adjudicated by fitting 16 variants of the Rational Model of Categorization (differing in which parameters vary between age groups) and by analyses of single-dimensional rule use (Hamming distances, consecutive-trial consistency); COVIS, exemplar, and prototype models are discussed but not fitted.

## Notes

### Provenance and trials kept
`transform.py` reads two files of OSF M7TCK: the `data` table of `model_comparison_rmc_redo_reconciled.RData` (exported with R as `raw/trial_by_trial_data.csv`; it carries the authors' trial coding and RMC model outputs) and the E-Prime export `Badham_Sanborn_Maylor_2017_trial_by_trial_data.csv` (the trials actually run, with reaction times). A condition ended after six blocks or as soon as two consecutive blocks were perfect (paper p. 14); 80 of the 384 condition runs ended early. The authors' script `fitting_analysis_rmc.R` pads those runs to 96 trials with imputed all-correct rows, which the paper scores as 100% correct (p. 15). `exp0.csv` keeps only the 33,792 trials the participants actually ran; the 3,072 imputed rows are not observations and are dropped. Participant 73 is absent from the source (ids run 1..97).

### Columns

| column | description |
|--------|-------------|
| participant_id | Original subject number from source (str of "Subject"), 1..97 (no 73) |
| task_id | 0-indexed position of the condition in the session (= source "Block"-1); the four structures were run in one of 24 counterbalanced orders |
| condition | Shepard-Hovland-Jenkins category structure run in this task: type_1..type_4 = Type I..IV (= source "type") |
| block | 0-indexed learning block 0..5 within each (participant_id, task_id); = source "learning.block"-1 |
| trial | 0-indexed trial within each (participant_id, task_id), 32..96 trials per run; = source "Trial"-1 |
| size | Stimulus size, 0 = large / 1 = small (source coding: Big=0, Small=1) |
| colour | Stimulus colour, 0 = black / 1 = white |
| form | Stimulus form, 0 = triangle / 1 = square |
| response | Participant's category choice, 0 = Alpha (key F) / 1 = Beta (key J) |
| feedback | Correct category shown as feedback, 0 = Alpha / 1 = Beta |
| type.block | Source block label within a type, 1..6 (identical to learning.block) |
| stim.rep | Stimulus repetition number, 1..12 |
| stim.num | Stimulus identity number, 1..8 = 1 + 4*size + 2*colour + form |
| age_group | "younger" or "older" participant cohort (scheme age.group) |
| correct | Whether response was correct, 0/1 (scheme resp.acc) |
| rt | Reaction time in ms from stimulus onset to the key press (source Slide*.RT) |
| centrality | Stimulus centrality category: "central" / "peripheral" / NaN (NaN on Type I and Type II trials) |
| Block | Source block label, 1..4 = task_id+1 (position of the condition in the session) |
| prediction.1..16 | RMC model category-1 probability predictions per cluster-count model (floats) |
| pred.acc.1..16 | Corresponding RMC predicted accuracy per model, 0..1 |
| n.clusters.1..16 | Number of clusters used in each RMC model fit |
| cluster.assignment.1..16 | Cluster index the stimulus was assigned to in that model |
| purity.1..16 | Cluster purity / partition quality for that model |
| prediction.switch | RMC prediction for the switch model (floats) |
| n.clusters.switch | Number of clusters in the switch model |
| cluster.assignment.switch | Cluster assignment in the switch model |
| pred.acc.switch | Predicted accuracy of the switch model, 0..1 |

Per-paper primary effects verified on the transformed data (trials actually run): accuracy improves across learning blocks (0.59→0.72); younger adults outperform older adults (0.76 vs 0.63); accuracy declines with structure complexity (Type I 0.85 > Types II–IV 0.65–0.67).

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: Rational Model of Categorization (Anderson, 1991) group fits; the 16 age-group variants of Table 1, compared on summed NLL with AIC/BIC weights; multi-start bounded L-BFGS-B (scipy, finite-difference gradients).
Reproduced: model_comparison (Model 14 — sP, c, r differ between age groups; sL shared — wins by both AIC and BIC weights), coupling_older_higher (older adults' coupling c > young adults', i.e. fewer clusters).
Not reproduced: none.
Numeric mismatch: the fit scores the 33,792 trials the participants ran (n_obs of AIC/BIC), whereas the paper's Table 1 likelihoods (Model 14: 20178.4) sum over the authors' padded table of 36,864 trials that includes 3,072 imputed all-correct rows, so the values are not directly comparable. On the trials run, Model 14 reaches a negative log likelihood of 19757.2 and wins by both AIC and BIC weights (Model 16 second); the paper's Table 2 parameters score 19786.3 on the same trials. Coupling: c_older - c_young = 0.065 (paper: 0.241); the direction reproduces. The greedy-argmax RMC likelihood is piecewise-flat and multi-modal (its predictions change suddenly with small parameter changes, as the authors note), so the multi-start search is required.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment
The single experiment (`exp0`) is reproduced as a static jsPsych v8 task at `experiments/exp0/` (SHJ Types I–IV category learning: 8 shapes, F=Alpha / J=Beta keys, Correct!/Incorrect! feedback with the answer, 6 blocks of 16 trials, early stop at two consecutive perfect blocks). The headless round trip passed: its saved CSV matches `exp0.csv`'s participant-facing schema (columns `participant_id, task_id, block, trial, size, colour, form, response, feedback, type.block, stim.rep, stim.num, correct, Block`, plus a browser-only `rt`), with 96 rows per type and `correct == (response == feedback)`. No experiments were skipped. ASSUMPTIONs: the full verbatim Kurtz et al. (2013) rule-based instruction text is not in the open data, so the instruction screen reproduces the paper's described content without revealing the hidden structure; the concrete feature 0/1 semantics (small/white/square vs large/black/triangle) and the random per-type dimension permutation/alpha–beta assignment (the paper's counterbalancing) are browser instantiations; and the RMC model-output columns, the `age_group` cohort, and the derived `centrality` label are analysis-time quantities the design cannot produce and are therefore omitted.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Text-format conversion
`exp0` (SHJ Types I–IV category learning) is textifiable: the stimuli are nameable binary feature combinations (size, colour, form) and the responses are the two category choices, so a reader learns the hidden rule exactly as participants did. All four conditions are transcribed into `transcripts0.jsonl` (one transcript per participant covering every trial the participant ran in the four conditions, in the order they were run). Feature semantics (the authors' coding in `fitting_analysis_rmc.R`): size 0=large/1=small, colour 0=black/1=white, form 0=triangle/1=square; response token `A`=Alpha (0, key F), `B`=Beta (1, key J). The per-trial RMC model-output, `centrality`, and `Block` columns are analysis-time quantities, not participant-facing, and are omitted. No experiments skipped. Sample transcript (through the first response):

```
This is a category-learning task. Your goal is to learn a rule that allows you to tell whether each example belongs in the alpha or beta category: four of the shapes you will see belong in the alpha category and four belong in the beta category. On each trial a shape appears in the middle of the screen. Press A if you think it belongs in the alpha category, or press B if you think it belongs in the beta category. The words Alpha and Beta appear at the bottom corners of the screen to remind you which is which. After each response you get feedback: the same shape reappears with Correct! or Incorrect! followed by the correct answer (Answer = Alpha or Answer = Beta), and this will gradually teach you the rule. You will go through several conditions, and each one has its own new rule; you may take a break between conditions if you wish.
You see a large black square. You press [HUMAN_RESPONSE]B[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

`exp0` was given a text simulator (`simulate0.py`): each simulated participant
learns the four Shepard–Hovland–Jenkins structures (Types I–IV) in a random
order over up to 6 blocks of 16 trials each (a structure ends after two
consecutive perfect blocks), with a per-participant counterbalanced rule (sampled from
the structure families actually observed in `exp0.csv`: 6 / 6 / 24 / 8
realizations for Types I / II / III / IV) and randomized within-block stimulus
order (two copies of each of the 8 shapes per block; blocks 1-2 = two
permutations of the 8, later blocks unconstrained), matching the paper's
Methods and the shipped transcripts. The round-trip check passed: regenerating
`transcripts0.jsonl` from the simulated `exp0.csv` through `build_jsonl.py`
reproduces the simulator's prompts byte-identically. No experiments skipped.
ASSUMPTIONs: the source version counterbalancing (type order, per-type
permutation, alpha/beta labels) is not recoverable from the transcripts, so
rules are sampled uniformly from the data's observed structure families and
the order of the four types (task_id = position, condition = type) from a
random permutation; the stop criterion (two consecutive perfect blocks) is
implemented; the reaction time, the analysis-time RMC model predictions and
the derived `centrality` label are omitted (a text simulator cannot produce
them). The `age_group` cohort (48/48) and the A/B + Alpha/Beta
token semantics follow `build_jsonl.py`'s fixed neutral mapping.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 1, major 6, minor 8; fixed 13, open 2).

Checked: paper (https://doi.org/10.1037/pag0000183, author manuscript PDF), original data (https://osf.io/M7TCK/: E-Prime trial export, aggregate file, RData tables, R scripts), exp0, transform re-run, transcripts, simulator, modeling, analysis, logs. Skipped: none.

Fixed:
- critical: exp0.csv carried 3,072 rows (80 of 384 condition runs, 192 blocks) that were never run: the OSF E-Prime export has 33,792 trials, and the authors' fitting_analysis_rmc.R pads every condition ended at the criterion (two consecutive perfect blocks, paper p. 14) with all-correct rows (response = feedback, random stimulus order); transcripts0.jsonl narrated them as key presses. transform.py now reads the E-Prime export too and keeps only the trials run; exp0.csv regenerated (33,792 rows), transcripts rebuilt.
- major: build_jsonl.py and simulate0.py described every stimulus with the opposite words: the source coding (fitting_analysis_rmc.R) is size 0 = Big, colour 0 = Black, form 0 = Triangle, and the transcripts said small / white / square (verified on all 33,792 observed rows against the E-Prime FileName). Maps corrected in both scripts and in the README.
- major: transcripts narrated the four conditions in Type I..IV order; participants ran them in one of 24 counterbalanced orders (source Block, paper p. 12). task_id is now the position of the condition in the session (source Block - 1) and the new column condition holds the structure (type_1..type_4); transcripts follow task_id order; simulate0.py runs the types in random order; analysis.py selects Type I via condition.
- major: transform.py read raw/trial_by_trial_data.csv, which is not the OSF file of that name (the E-Prime export; the script fails on it with KeyError 'type') but the `data` table of model_comparison_rmc_redo_reconciled.RData exported with R (the export reproduces the old exp0.csv byte-for-byte). Provenance documented in transform.py and the README.
- major: logs/auto-exp-modeling.sessions.json listed four files of another run (vantiel_2022_meaning) in the first message's summary diffs; the four entries were removed, the rest of the log is unchanged.
- major: simulate0.py always ran six blocks and the README said the shipped data contain all 96 trials per type; the simulator now stops a condition after two consecutive perfect blocks, and the round trip through build_jsonl.py is byte-identical (random and memorizing agents, 2 + 2 participants).
- major: the Modeling reproduction note compared the Model 14 likelihood with the paper's 20178.4, which sums over the padded 36,864-trial table. model.py (unchanged) re-run on the trials run: Model 14 wins by AIC and BIC weights (NLL 19757.2, Model 16 second), c_older - c_young = 0.065 > 0; both results reproduce and the note was rewritten.
- minor: README said participant_id runs 1..96; the source has ids 1..97 without 73 (absent from the E-Prime export and the aggregate file).
- minor: README claimed the 0/1 to Alpha/Beta assignment is not recoverable; the source fixes it (response and CorrectResp f = 0, j = 1; paper p. 13: F = Alpha, J = Beta; the raw Alpha column equals feedback == 0 on every row).
- minor: README said centrality is NaN on Type I trials; it is NaN on Types I and II.
- minor: the E-Prime export records the reaction time of every trial (Slide*.RT, ms; it matches the OSF aggregate file on 33,789 of 33,792 trials) and exp0.csv had none; rt added.
- minor: README summary said 96 trials per structure, 'reaction-relevant information', and that the paper compares the RMC against COVIS, exemplar, and prototype models (the paper fits only RMC variants, pp. 21-24, 28); corrected.
- minor: analysis.py crashed on the trials run (one participant reached the criterion in every condition and has no last block; ttest_rel shape error); the paired test now aligns on common participants. All three effects reproduce (0.136, 0.124, 0.209; p < .05).

Open:
- minor: the paper (pp. 12-13) says Type III was reduced to 3 permutations; exp0.csv contains all 24 distinct Type III structures (4 participants each). Inside the source; noted in the simulate0.py docstring.
- minor: the OSF aggregate file carries per-participant AGE, SEX, EDUCATION (years), MHA vocabulary and DSST scores that exp0.csv does not carry.

Run: claude-fable-5-1, 2026-09-09
