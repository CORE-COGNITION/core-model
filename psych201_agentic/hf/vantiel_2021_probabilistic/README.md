---
tags:
- paradigm:language-comprehension
- cognitive-modeling:pass
- psych-201
- text-format:pass
- js-experiment:needs-review
- simulator:pass
- verification:pass
---
# vantiel_2021_probabilistic

- Paper: https://doi.org/10.1073/pnas.2005453118
- Data source: https://osf.io/hsytk/
- Full text: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7936277/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
van Tiel, B., Franke, M., & Sauerland, U. (2021). Probabilistic pragmatics explains gradience and focality in natural language quantification. Proceedings of the National Academy of Sciences, 118(9), e2005453118.

## Experiment summary
Six experiments test whether quantity words (e.g., "some", "all", "most") have truth-conditional or prototype-based semantics, explained by Bayesian probabilistic-pragmatic models. Exp 1a (N=596) and 1b (N=201) collect free-text quantity-word productions in response to displays of 432 red/black circles; Exp 2a (N=50) and 2b (N=150) collect binary validity judgments (with RTs) of monotonicity arguments; Exp 3 (N=21) collects continuous slider proportion estimates of red circles; Exp 4 (N=194) collects slider adequacy ratings of quantity-word descriptions. Response types span open production, binary validity judgments, and continuous ratings. The data reproduce the paper's headline effects: approximate-number tracking in estimation, monotonicity-based validity judgments, and adequacy ratings where the observed data outperform model predictions, supporting a gradience/prototype account of quantity-word meaning.

## Notes

### Columns

#### exp0 (Experiment 1a: quantity-word production, training sample)
| column | description |
|--------|-------------|
| participant_id | Original SUBJECT number from source exp1a.csv |
| trial | 0..9, within-participant presentation order (source TRIAL 1..10, minus 1) |
| response | Verbatim free-text quantity-word production ("How many of the circles are red?") |
| dots | Number of red circles in the 432-circle display shown (intersection set size) |
| code_l1 | Coded response, level 1 (operator-level grouping; source CODE.L1) |
| code_l2 | Coded response, level 2 (fine-grained, distinguishes 'few'/'a few'; source CODE.L2) |

#### exp1 (Experiment 1b: quantity-word production, test sample)
| column | description |
|--------|-------------|
| participant_id | Original SUBJECT number from source exp1b.csv (MTurk worker ID column dropped as PII) |
| trial | 0..9, within-participant presentation order (source TRIAL 1..10, minus 1) |
| response | Verbatim free-text quantity-word production |
| dots | Number of red circles in the display (intersection set size) |
| code | Coded quantity-word response (source CODE) |
| code_raw | Raw un-grouped coded response (source CODE.RAW) |
| age | Participant age in years (self-report) |
| mothertongue | Self-reported native language (verbatim, incl. typos) |
| countlanguage | Language participant usually counts in (verbatim; empty where unanswered) |
| gender | Participant gender, normalized (f / m) |

#### exp2 (Experiment 2a: monotonicity pretest)
| column | description |
|--------|-------------|
| participant_id | Original subject ID from source exp2a.csv (whitespace file, leading index token dropped) |
| trial | 0..N, within-participant presentation order (source trial 1..50, minus 1) |
| response | Validity judgment: 0 = argument judged invalid, 1 = valid |
| condition | Argument direction: `strong_to_weak` / `weak_to_strong` |
| predicate | Predicate of the argument (e.g. "saw a tree") |
| rt | Reaction time in milliseconds |
| error | Whether the validity judgment was an error (0/1) per the pretest coding |

#### exp3 (Experiment 2b: monotonicity)
| column | description |
|--------|-------------|
| participant_id | Original subject ID from source exp2b.csv (leading index token dropped) |
| trial | 0..N, within-participant presentation order (source trial, minus 1) |
| response | Validity judgment: 0 = invalid, 1 = valid |
| condition | Argument direction: `strong_to_weak` / `weak_to_strong` |
| quantifier | Quantity word at issue (e.g. "most", "some") |
| predicate | Predicate of the argument (e.g. "ordered meat") |
| rt | Reaction time in milliseconds |

#### exp4 (Experiment 3: approximate-number estimation)
| column | description |
|--------|-------------|
| participant_id | Original submission_id from source exp3.csv |
| trial | 0..25, within-participant order (re-enumerated from source row order) |
| phase | `practice` for the two warm-up trials that precede the 24 items (rows 0-1 of each participant), `test` otherwise |
| response | Slider estimate of the number of red circles (0..432, source rating_slider) |
| age | Participant age in years |
| dots | Actual number of red circles in the display (source dots_number) |
| education | Self-reported education level (verbatim: graduated_college / graduated_high_school / higher_degree) |
| gender | Participant gender, normalized (f / m / other) |
| languages | Self-reported counting language (verbatim, incl. typos) |
| trial_number | Raw trial_number column from source (1..2 for the warm-up trials, then 1..24 for the items; shown for provenance, not used as trial) |

#### exp5 (Experiment 4: adequacy evaluation ratings)
| column | description |
|--------|-------------|
| participant_id | Original subject ID from source exp4.csv |
| trial | 0..N sequential response counter within participant (100 per participant = 20 displays x 5 conditions) |
| block | Display index 0..19 (source trial 1..20, minus 1); groups the 5 condition-ratings of one display |
| response | Adequacy rating (slider, 1..100, source dep) |
| item | Stimulus item id (item01..item20) |
| condition | Source of the quantity word: `d_pred` (data), `gqs_pred`/`gqp_pred` (generalized-quantifier semantics/pragmatics), `pts_pred`/`ptp_pred` (prototype-theory semantics/pragmatics) |
| quantifier | Quantity word being rated, sentence-initial capitalization as in the source (e.g. `Most`, `None`) |
| dots | Number of red circles in the display (intersection set size) |
| bin | Binned dots value used for plotting (source bin) |
| rel | Differential (recalibrated) rating = rating minus rating for the data-sampled quantity word (source rel; can be negative) |

Sample-size note: `participant_id` is the original anonymous subject code from each source file, so counts reflect the number of distinct codes (N per experiment above); some experiments report slightly fewer valid participants than raw codes, and Exp 4's 5-condition-per-display structure is grouped by the `block` column rather than split into separate experiments. In exp4 (Exp 3) `participant_id` 26 is the second submission of a participant who did the experiment twice (source `exp3.R`), so 21 codes are 20 people; in exp5 (Exp 4) participant 1597179234 has 99 rows because one rating of display 15 is missing in the source (`exp4.R`: technical issue).

## Text-format conversion

Transcribed exp0 (Exp 1a production), exp1 (Exp 1b production), exp2 (Exp 2a monotonicity pretest), exp3 (Exp 2b monotonicity), and exp5 (Exp 4 adequacy ratings) into `transcriptsN.jsonl`. Exp 4 (Exp 3 approximate-number estimation) was skipped as not textifiable: stating the true number of red circles in the text would remove the information participants actually used (they estimated it) and make the estimation task trivial. Response codings: exp0/1 free-text quantity word; exp2/3 binary validity (A = valid, B = invalid); exp5 continuous adequacy rating (1-100).

Sample transcript (exp0, participant 1, up to the first response):

```
You will see displays, each made of 432 circles that are either red or black. For every display you must say how many of the circles are red by completing the sentence '___ of the circles are red'. Do not type numbers or number words; instead type a quantity expression such as 'most', 'half', or 'few'.
A display shows 432 circles, 92 of them red. You complete the sentence: [HUMAN_RESPONSE]half[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Static jsPsych v8 experiments were built for all six experiments under
`experiments/expN/` (see `experiments/README.md`). No simulator exists for this
dataset, so each was rebuilt from the paper (Methods + verbatim instruction
text), the `transcriptsN.jsonl` wording, and the `expN.csv` schema. The headless
`?mode=simulate` round trip ran on this machine and confirmed every generated CSV
matches its `expN.csv` schema (column names, 0-indexed `trial`, per-participant
row counts: exp0 10, exp1 10, exp2 50, exp3 34, exp4 26, exp5 100).

Assumptions worth surfacing (each is recorded with an `ASSUMPTION:` comment):
the source's exact 432-circle display set and its per-participant draws are not
published, so the displayed number of red circles is drawn uniformly in [0, 432];
exp5's quantity words are sampled from the empirical per-condition, per-bin
distribution derived from `exp5.csv` (the four models' exact posterior predictive
draws are not recoverable); the post-hoc coding columns (exp0/1 `code*`) and the
provenance `trial_number` (exp4) are not produced by a fresh participant. These
affect stimulus content, so this run is marked needs-review (the task structure,
wording, and schema are faithfully reproduced).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Text simulators (`simulate0.py`–`simulate3.py`, `simulate5.py`) were written
for all five transcribed experiments (exp0/1 production, exp2/3 monotonicity,
exp5 adequacy). Each produced DataFrames matching the repo `expN.csv` schema
(minus `rt`, post-hoc `code*` coding, and demographics), and all passed the
round-trip check: `build_jsonl.py` regenerated transcripts byte-identical to
each simulator's prompts. exp4 (estimation) was not transcribed and is not
simulated. Assumptions: exp0/1 `dots` drawn uniformly in [0, 432] (display set
unpublished); exp5 quantity words sampled from the empirical per-condition
marginal from exp5.csv (model posterior predictives unrecoverable).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction

Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: GQ-lit, GQ-prag, PT-lit, PT-prag; multi-start bounded L-BFGS MAP
(faithful approximation of the paper's Stan/MCMC posterior fit) on the pooled
Exp-1a production counts; compared on test log-likelihood of Exp-1b (paper's
posterior-expected test log-lik in Table 1).
Reproduced: gq_prag_best_fit (GQ-prag offers the best fit; ranking
GQ-prag > PT-lit > PT-prag > GQ-lit matches Table 1).
Not reproduced: none.
Numeric mismatch: reproduced test log-lik = GQ-lit -1717.3, PT-lit -1640.0,
GQ-prag -1622.0, PT-prag -1657.1 vs reported -1717.0, -1660, -1625, -1675
(GQ-lit essentially exact; the pragmatic and prototype models within ~20 units;
ranking and winner match). Uses the paper's exact priors, incl. the
Dirichlet(50) salience prior of the literal models and Dirichlet(1) of the
pragmatic ones.
Partial validation: none.
Indeterminate: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-26

## Verification

Verdict: pass (critical 3, major 4, minor 11; fixed 8, open 7).

Checked: paper (https://doi.org/10.1073/pnas.2005453118, main text + OSF supplement.pdf), original data (https://osf.io/hsytk/, data-and-analysis/), exp0-exp5, transform re-run, transcripts, simulators (round trip exp0/1/2/3/5), modeling, analysis, logs. Skipped: none.

Fixed:
- build_jsonl.py stripped whitespace from free-text responses: exp1 participant 1596053705 typed 'A few ' and 'A few', so two CSV values mapped to one token; the transcriber now marks the CSV value verbatim; transcripts1.jsonl rebuilt.
- build_jsonl.py read the CSVs with pandas' default missing-value strings, so the typed responses 'None' (5 exp0 rows with dots 0/0/0/7/42, 1 exp1 row) and 'NA' (3 exp0 rows) became 'nan' in transcripts0/1, and the quantity word 'None' (84 exp5 rows, dots 0-149) was narrated as 'a quantity-word description' in transcripts5; the script now reads with keep_default_na=False; transcripts0/1/5 rebuilt.
- transform.py did not label the two warm-up trials of Exp 3 (supplement p. 18; source trial_number 1, 2, then 1..24); exp4.csv now carries phase=practice/test (other columns byte-identical); README exp4 table updated; analysis.py still reproduces all three effects.
- README described exp5 quantifier as 'blank where unrecorded'; the 84 'blank' values are the word 'None'.
- simulate5.py's empirical per-condition quantity-word distribution omitted 'None' for the same reason; counts added (d_pred 16, gqp_pred 19, gqs_pred 7, ptp_pred 25, pts_pred 17); round trip through build_jsonl.py passes.
- logs/auto-exp-transcribe.sessions.json carried a workspace diff of modeling_pending.txt naming 74 other datasets; the diff entry was removed.
- README: Columns headings '### expN' changed to the template's '#### expN'; 'Run:' line added to '## Text-format conversion' (date from the session log).
- README sample-size note now explains exp4 N=21 (participant 26 is a second submission, source exp3.R) and exp5 participant 1597179234's 99 rows (one rating missing in the source, exp4.R).

Open:
- minor: exp0 participants 54, 57, 178 have response 'NA' (source RESP 'NA', coded 'na'); the unquoted raw file cannot tell a typed 'NA' from a missing value, so it is kept verbatim.
- minor: Exp 2a arguments were about a random named person (supplement p. 10-11, 'Angela owns a dog'); the source stores only the predicate, so transcripts2.jsonl reads 'saw an oak. Therefore, saw a tree.'
- minor: the main text (p. 6) says 120 participants for Exp 2; the supplement and the source have 50 (2a) + 150 (2b).
- minor: the source ships post-exclusion samples for Exp 1a (596 of 600; 4 answered nothing) and Exp 4 (194 of 200; 6 non-native speakers); the R-script exclusions (numbers-only, all/none-only, >50% error, all-accept/reject) are not applied and those rows are present.
- minor: exp4 education is the source's verbatim category string, not the schema's ordinal int code.
- minor: check_repo still reports 7 exp0 and 1 exp1 transcripts with a marked-response count different from the CSV 'free rows' and undeclared tokens for exp0/1/5: it reads 'None'/'NA' as missing on its side, and free-text production and a 1-100 rating cannot enumerate every token.
- minor: model.py re-run (19 min) reproduces the named result (GQ-prag best; ranking GQ-prag > PT-lit > PT-prag > GQ-lit as in Table 1) with test log-lik GQ-prag -1617.7, PT-lit -1640.6, PT-prag -1688.5, GQ-lit -1717.3; the README's own run reported -1622.0, -1640.0, -1657.1, -1717.3, so the MAP values vary by run (optimizer convergence flag 0.00 for three models) while the winner and ranking do not.

Run: claude-fable-5-1, 2026-09-13
