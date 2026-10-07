---
tags:
- paradigm:bandit
- cognitive-modeling:pass
- psych-101
- text-format:pass
- js-experiment:needs-review
- simulator:pass
- verification:pass
---
# garcia_2023_experiential

- Paper: https://doi.org/10.1038/s41562-022-01496-3
- Data source: https://github.com/bsgarcia/RetrieveAndCompareAnalysis
- PDF: https://www.researchsquare.com/article/rs-1361189/latest.pdf
- Full text: https://www.nature.com/articles/s41562-022-01496-3
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Garcia, B., Lebreton, M., Bourgeois-Gironde, S., & Palminteri, S. (2023). Experiential values are underweighted in decisions involving symbolic options. Nature Human Behaviour, 7(4), 611-626.

## Experiment summary
Across 9 experiments (N = 102-128 each), participants performed a two-option reinforcement-learning task contrasting experiential options (learned through feedback) with symbolic options (described by explicit probabilities), in either interleaved or blocked designs. Each trial recorded a binary choice between the two options, reaction time, and reward outcome, with phases tagged LE (experiential learning only), ES (experiential vs symbolic), EE (experiential vs experiential), SP (symbolic-only probability estimation), and condition-specific deactivate-option variants (exps 6-7). The research question asks whether experiential values are underweighted when options also carry symbolic/described information, which the paper tests with Q-learning and logistic choice models; the reproduced headline effects are experiential learning accuracy (LE > chance), accuracy rising with decision value, and reduced probability of choosing the experiential option as the symbolic option's expected value rises.

## Notes

### Columns

All 9 experiments (exp0..exp8) share the same column schema, carried 1:1 from `raw/data/behavior/reformat/exp_{n}_*.csv` (exp_1..exp_9).

| column | description |
|--------|-------------|
| participant_id | Original subject identifier from the source CSV (`sub_id`, a large stable integer recoded as a string). |
| task_id | 0-indexed per-participant grouping over distinct `(sess, phase)` runs in order of first appearance; each value is a self-contained run (session x phase) where trial state starts fresh. |
| phase | Experiment phase within a run. `LE`=experiential learning only, `ES`=experiential+symbolic, `EE`=experiential+experiential, `SP`=symbolic-only estimation, `EA`/`SA`=deactivate-option variants (exps 6-7). |
| trial | 0-indexed trial counter restarted within each `(participant_id, task_id)` (`trial` recomputed as 0..N-1 in source row order). |
| response | The participant's raw choice. `2.0`=option 2, `1.0`=option 1 in LE/ES/EE/EA/SA phases; in `SP` phase it is the reported probability value 0-100 (percent). Keep raw (mixed types). |
| rt | Reaction time in milliseconds (source `rtime`). |
| reward | Delivered outcome of the chosen option (`out`): `1.0` = win, `-1.0` = lose. |
| condition | Condition code (`cond`): `3`=60/40, `2`=70/30, `1`=80/20, `0`=90/10 reward-ratio lottery; NaN in phases without a described ratio (ES/EE/EA/SA/SP). |
| correct | Correctness vs expected value (`corr`): `1` if EV(chosen)>=EV(unchosen) else `0`. |
| sess | Session identifier: `-2`/`-1` = training sessions, `0`/`1` = test sessions 1/2. |
| cfout | Counterfactual outcome of the unchosen option; `-1` when unknown (SP). |
| chose_right | `1` if the participant chose the rightmost on-screen option, else `0`. |
| rew | Cumulative total reward received (running sum). |
| op1 | Identifier of option 1 (`E`=experiential, `S`/value=symbolic; empty when absent). |
| op2 | Identifier of option 2 (`E`/`S`; empty when absent, e.g. NaN in SP). |
| p1 | P(win) / described probability of option 1. |
| p2 | P(win) / described probability of option 2 (NaN in SP). |
| ev1 | Expected value of option 1. |
| ev2 | Expected value of option 2. |
| catch_trial | `1` if this trial is an attention catch trial, else `0`. |
| reversed | `1` if option presentation order was reversed (option 1 shown right instead of left), else `0`. |
| index | Original per-file source row index from the reformat CSV. |

## Update (2026-08-13)
- Chronology fix (rows reordered; no cell values changed outside `task_id`/`trial`): the previous
  release assigned `task_id` from lexicographic category codes of `sess_phase` strings and sorted by
  it, which placed each session's `ES` transfer block before the `LE` learning block that feeds it,
  artificially un-interleaved the mixed `ES`/`EE`(/`EA`/`SA`) transfer trials of exps 4-8, and left
  per-participant `task_id` sequences with gaps. Rows are now ordered within each participant by the
  source `index` column — the source reformat CSV is a wall-clock event log (concurrent online
  participants interleave in real time), so `index` is the true presentation order.
- Phase/session order this yields, validated against the cumulative-reward column `rew` (continuous
  running sum across phase boundaries in the new order): within each session `LE` first, then the
  transfer trials (`ES`, and in exps 4-8 `EE`/`EA`/`SA` genuinely interleaved with `ES`), then `SP`;
  sessions in the order `-1` (first training), `-2` (repeat training, present only for participants
  who redid training — all 68 such participants ran `-2` strictly after `-1` in the source log),
  then test sessions `0`, `1`.
- `task_id` reassigned as 0-indexed first-appearance order of distinct `(sess, phase)` combos per
  participant (contiguous 0..K-1, matching the column description above); `trial` renumbered
  0..N-1 within each `(participant_id, task_id)` in the new order. All 9 files affected;
  1037 of 1050 participants (~99%) had rows reordered; per-participant row multisets, row and
  participant counts unchanged.

CSVs fixed in place from the previous release; transform.py updated to produce the same output
from raw. The previous version remains in the repo's git history.

## Text-format conversion

All 9 experiments (exp0-exp8) share the same two-option bandit paradigm, so each was transcribed
into its own `transcriptsN.jsonl` (none skipped). Each transcript narrates every trial in order:
choice phases (LE/ES/EE/EA/SA) render both options and wrap the chosen option (`A`=option 1,
`B`=option 2) in `[HUMAN_RESPONSE]...[/HUMAN_RESPONSE]`, and SP probability-estimation trials wrap
the reported 0-100 estimate (a scale in steps of 5, as in the paper). The source does not record
identifiers for the individual experiential symbols, but within a session every symbol has its own
p(win), so each distinct E p(win) of a session is narrated as `experiential symbol <k>` (numbers
shuffled per participant and session; every session uses new symbols). Following the Methods,
outcomes are narrated only in the LE phase (the chosen option's outcome in exp0-exp1, both options'
outcomes from exp2 on = complete feedback) and never in the ES/EE/EA/SA/SP phases, whose guides say
so; ES catch trials are narrated as choices between two lotteries. Symbolic lotteries are fully
described by their stated win probability.

### Sample transcript

```
Welcome. In this decision-making task, each trial presents options that can win or lose you points. Options are of three kinds: experiential symbols (numbered; you learn their value from the outcomes they deliver; each session uses a new set of symbols), symbolic lotteries (a pie chart stating an explicit win probability), and ambiguous options (value hidden). In choice phases you are shown two options: press A to choose option 1, or press B to choose option 2.
Option 1 (experiential symbol 8) is on the left; option 2 (experiential symbol 4) is on the right. You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE]. You win 1 point.
 …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

All 9 experiments (exp0-exp8) got a runnable static jsPsych v8 build under
`experiments/expN/` (shared engine in `experiments/stimulus/`), each saving data
in the dataset's own schema. The headless round trip (jsPsych simulation mode +
Playwright) ran and **passed** for every experiment: column names, dtypes and
codings match the repo, `trial` restarts at 0 per `(participant_id, task_id)`,
and the field checks pass. Rendering was inspected and is clean (visual_ok).

Design-level assumptions a reviewer should verify (recovered from the paper +
CSV, not fully specified):
- Scope: each experiment builds **one main (analyzed) session** (LE → transfer
  ES[/EE/EA/SA] → SP). The source CSV's training sessions (sess -1/-2) and the
  second test session (sess 1) of exps 5-8 are not replayed; `task_id` numbers
  this session's phases.
- Feedback: the source records the unchosen outcome (`cfout`) on every choice
  trial, so complete feedback is shown for all experiments (the paper describes
  Exp.1-2 as partial feedback — see ASSUMPTION in engine.js).
- `catch_trial`: ES choices with an extreme lottery (p 0 or 1) and SP ratings of
  the S-lottery items are flagged 1; the exact catch-item set was inferred.
- SP scoring: correct when |estimate/100 − true p| ≤ 0.1, reward +1/-1 by that
  correctness (inferred incentive rule). E-symbols are assigned to values at
  random per participant (the source does not record symbol identity).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

All 9 experiments (exp0..exp8) got a self-contained text simulator (`simulate0.py`
.. `simulate8.py`), one per experiment, that regenerates the exact transcript
format of the corresponding `transcriptsN.jsonl`. Each is a `uv`-runnable,
importable module producing a long-format DataFrame matching the repo's `expN.csv`
(minus `rt`) plus the participant transcripts; the headless round trip through
`build_jsonl.py` passed for every experiment (regenerated transcript text is
byte-identical to the simulator's own prompts). None were skipped.

Design notes / ASSUMPTIONs (recorded in each simulator's class docstring): the
simulator builds one main analyzed session (LE → transfer → SP, matching the
repo's js-build scope; training sessions and the second test session are omitted);
trial order, E-symbol-to-value assignment and left/right reversal are randomized
per participant (the source does not record symbol identity); the EA/SA
ambiguous option carries a hidden value drawn from the experiment's grids; SP
reward/correct use |estimate/100 − true p| ≤ 0.1; ES catch trials are two-lottery
choices drawn from the experiment's catch grids and SP S-items are catch trials;
outcomes are narrated only in the LE phase (both options from exp2 on) and
E-symbols are numbered exactly as in `build_jsonl.py`.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result (experiential value neglect).
Fitted models: per-participant MAP delta-rule Q-learning on the LE phase (softmax over 2Q-1, gamma(1.2,5) on temperature and beta(1.1,1.1) on learning rate; counterfactual learning for the complete-feedback exps exp2/exp3), forward-simulated to read off final Q = estimated p(win) per E-option; and per-participant logistic choice function P(chose E)=1/(1+exp(temp*(p_lottery-midpoint))) over the ES phase, the midpoint being the inferred p(win). Per-subject slope of estimated p(win) on true p(win) per modality, compared with a paired t-test.
Reproduced: le_slope_gt_es_slope_exp0, le_slope_gt_es_slope_exp1, le_slope_gt_es_slope_exp2, le_slope_gt_es_slope_exp3 (LE slopes > ES slopes, all p<.001; the paper's T values for Exp 1-4 are 6.53, 11.74, 15.8, 11.64 vs ours 6.70, 12.91, 14.49, 9.21).
Not reproduced: none.
Numeric mismatch: none. LE slopes and t-values land in the paper's range; magnitudes differ slightly because this repo keeps all participants while the paper excludes by catch-trial/RT criteria, and the p(win) coding is in probability (0-1) rather than percentage.
Partial validation: N=123/116/112/123 (all participants, uncapped).
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 3, major 7, minor 10; fixed 13, open 7).

Checked: paper (preprint https://doi.org/10.21203/rs.3.rs-1361189/v1 with its Methods supplement GarciaNHBMethodsV20.docx; published https://doi.org/10.1038/s41562-022-01496-3 abstract and data statement only, full text paywalled), original data (https://github.com/bsgarcia/RetrieveAndCompareAnalysis, branch cleaning, data/behavior/reformat/) and task code (https://github.com/bsgarcia/RetrieveAndCompare, main.js), exp0-exp8, transform re-run (all 9 CSVs byte-identical), transcripts, simulators (smoke test + build_jsonl.py round trip), modeling (model.py, full run, 135 min), analysis, logs. Skipped: none.

Fixed:
- critical: transcripts swapped the two option descriptions on reversed=1 trials ("Option 1 (lottery) is on the right"), but response 1 is always option 1 = op1 (chose_right == [response 1 & reversed] | [response 2 & not reversed] on 100% of rows; task code: choice 1 = option1 regardless of invertedPosition). build_jsonl.py now keeps the descriptions with option 1/2 and swaps only the sides; transcripts0-8.jsonl rebuilt.
- critical: transcripts narrated "You win/lose 1 point" after every ES/EE/EA/SA/SP trial; Methods: no feedback in ES, EE, EA/SA (main.js never sets a feedback image in playElicitation; SP fbdur=200). Outcomes are now narrated only in the LE phase and the transfer-phase guides say outcomes are not shown.
- critical: every E-option was "an experiential symbol you have learned about", so the learning task could not be followed in text. Within a session each symbol has its own p(win) (8 distinct LE values per participant and session, 4 in exp3; every transfer-phase E-value is in the same session's LE set), so symbols are now named "experiential symbol <k>" (numbers shuffled per participant and session, new symbols per session).
- major: complete-feedback experiments (Methods: from Exp. 3 on; fit_LE.m fits cfout for exp_num > 2, exp_9 included) narrated only the chosen outcome; the unchosen option's outcome (cfout) is now narrated in LE for exp2-exp8.
- major: ES catch trials (catch_trial=1, p1 in the catch grid) were narrated as symbol vs lottery; Methods and main.js: catch trials are choices between two lotteries. Option 1 is now narrated as a lottery on those trials.
- major: check_repo: 94-114 transcripts per experiment used an SP response token (5..95) never declared; the SP guide now lists the scale 0, 5, ..., 100 (Methods: rating scale 0-100% in 5% steps).
- major: simulate0-8.py mirrored the four narration errors above and modelled catch trials as ES choices with lottery p in {0, 1}; they now mirror build_jsonl.py (symbol numbering with the same seeding, sides-only reversal, LE-only outcomes incl. cfout for complete feedback, two-lottery catch trials from each experiment's catch grid, random agent in steps of 5). Smoke tests (-n 2 --seed 0) and the build_jsonl.py round trip pass byte-identically for all 9.
- major: simulate3.py listed 6 E-values (0.2/0.8 are SP lottery items, not symbols; LE has 4), simulate8.py merged both sessions' ladders (12 E-values, 6 LE pairs, 15 lotteries) and simulate6.py included the training-session lotteries 0.1/0.9; configs set to the main session's grids from the CSVs (exp3: 4 symbols x 11 lotteries + 4 catch = 48; exp6: 8 x 8 + 8 = 72; exp8: 8 x 11 + 8 = 96).
- major: README `Data source:` pointed to https://github.com/bsgarcia/RetrieveCompareAnalysis (GitHub 404); the paper's data statement gives https://github.com/bsgarcia/RetrieveAndCompareAnalysis.
- major: README attributed the EA/SA phases to "exps 7-8" (twice) in its own 0-indexed numbering; they are in exp6.csv and exp7.csv (source exp_7, exp_8).
- minor: README said `condition` is NaN in ES/SP; it is NaN in ES/EE/EA/SA/SP.
- minor: README gave the raw path as `exp_{n}.csv`; the source files are exp_1_interleaved_incomplete.csv ... exp_9_incentives.csv (`exp_{n}_*.csv`).
- minor: README Text-format and Simulators sections described the old narration (symbol-identity caveat, catch = extreme lottery); rewritten for the new narration, sample transcript regenerated.

Open:
- minor: exp7.csv has one rt of -85 ms (participant 8911929604, ES, source index 63703); identical in the source file exp_8_block_complete_mixed_2s_amb.csv, kept for fidelity.
- minor: check_repo flags -1 in reward/cfout/sess as sentinels: -1 is the recorded loss outcome (+1/-1 points, Methods) and the training-session code (source README); cfout = -1 on SP rows is the source's own placeholder (main.js otherReward = -1). Source coding kept.
- minor: the paper reports N after catch-trial exclusion (Exp. 1-8: 76, 71, 83, 88, 71, 66, 71, 73); the source ships every tested participant incl. incomplete sessions (123, 116, 112, 123, 112, 128, 116, 118, 102), kept per the schema; the modeling section documents this.
- minor: EA/SA phases are also present in exp6.csv (source exp_7); the Methods say ambiguity was assessed only in Exp. 8 (inside the source).
- minor: exp8.csv (source exp_9_incentives, the published paper's ninth experiment) is not described in the reachable preprint or Methods supplement (published full text paywalled); complete feedback assumed from fit_LE.m.
- minor: analysis.py's docstring cites the preprint title ("The impassable gap ..."); the README cites the published title.
- minor: `response` keeps the source's 1/2 coding for two-option choices (schema default 0/1); documented in the column table and relied on by transcripts, model.py and analysis.py.

Run: claude-fable-5-1, 2026-09-10
