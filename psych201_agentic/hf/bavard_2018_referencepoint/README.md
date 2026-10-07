---
tags:
- paradigm:bandit
- cognitive-modeling:fail
- psych-201
- js-experiment:pass
- text-format:pass
- simulator:pass
- verification:needs-review
---
# bavard_2018_referencepoint

- Paper: https://doi.org/10.1038/s41467-018-06781-2
- Data source: https://github.com/sophiebavard/Magnitude
- PDF: https://www.nature.com/articles/s41467-018-06781-2.pdf
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Bavard, S., Lebreton, M., Khamassi, M., Coricelli, G., & Palminteri, S. (2018). Reference-point centering and range-adaptation enhance human reinforcement learning at the cost of irrational preferences. Nature Communications, 9(1), 4503. https://doi.org/10.1038/s41467-018-06781-2

## Experiment summary
A probabilistic instrumental learning task in which participants repeatedly choose between two cues within each context; contexts cross valence (reward/loss) and magnitude (big/small). Exp1 (N=20) uses a 2x2 design; Exp2 (N=40) adds partial vs complete (counterfactual) feedback. Every participant completes 160 learning trials (two 80-trial sessions presenting 4 cue pairs 20 times each) followed by a 112-trial transfer test with novel cue pairs to probe generalization. Responses are binary choices between the two cues, and feedback on the chosen (and in Exp2, optionally unchosen) outcome is delivered on each learning trial. The paper asks how reference-point centering and range adaptation in state-dependent value normalization shape reinforcement learning and produce irrational preferences.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Index number as recorded in the raw `subjects` array (201..220), reduced to string. |
| task_id | 0-indexed task reset: 0 = learning sessions (160 trials, continuous state), 1 = transfer test (112 trials). |
| phase | Phase label: `learning` (task_id 0) or `transfer` (task_id 1, no feedback). |
| trial | 0-indexed trial within each (participant_id, task_id); learning iterates all 160 trials in presentation order, transfer 0..111. |
| block | Sub-boundary inside the continuous learning task marking the two 80-trial sessions: 0 = session 1, 1 = session 2. NaN in transfer. |
| context_code | Raw `con` code 1..8 = context across both sessions (session1: 1..4, session2: 5..8); NaN in transfer. |
| context | Context within a session (`con2`), 1..4 = the four cue pairs: 1 reward/big, 2 reward/small, 3 loss/big, 4 loss/small; NaN in transfer. |
| valence | reward / loss, derived from `context`; NaN in transfer. |
| magnitude | big / small, derived from `context`; NaN in transfer. |
| cho | Raw choice code on learning trials: 1 = unfavorable (incorrect) option, 2 = favorable (correct) option; the source records learning choices as correct/incorrect, not by screen side. NaN in transfer. |
| aa | Raw choice code (1 or 2 = left/right option) on transfer trials; NaN in learning. |
| response | Learning trials (task_id 0): 0 = unfavorable option, 1 = favorable option (source `cho` - 1; the screen side is not recorded). Transfer trials (task_id 1): 0 = left cue (`stimulus_left`), 1 = right cue (`stimulus_right`) (source `aa` - 1). |
| reward | Delivered payoff of the chosen option (raw `out`) in euros: 0, +1 (big reward), +0.1 (small reward), -1 (big loss), -0.1 (small loss). NaN in transfer. |
| outcome_binary | Raw `out2`, the outcome on the context-relative scale: 1 = the better outcome of the pair (a gain in reward contexts, 0 in loss contexts), 0 = the worse one (0 in reward contexts, a loss in loss contexts); NaN in transfer. |
| stimulus_left | Transfer-trial identity (1..8) of the cue shown on the left (`ss[:,0]`); NaN in learning. Identities follow the authors' fitting code: 1/2 = favorable/unfavorable cue of the session-2 reward/big pair (context_code 5), 3/4 = reward/small (6), 5/6 = loss/big (7), 7/8 = loss/small (8). |
| stimulus_right | Transfer-trial identity (1..8) of the cue shown on the right (`ss[:,1]`); NaN in learning. |
| choice_set | JSON [left, right] cue identities presented on transfer trials; NaN in learning. |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Index number as recorded in the raw `subjects` array (e.g. 55, 56, 59...), reduced to string. |
| task_id | 0-indexed task reset: 0 = learning sessions (160 trials, continuous state), 1 = transfer test (112 trials). |
| phase | Phase label: `learning` (task_id 0) or `transfer` (task_id 1, no feedback). |
| trial | 0-indexed trial within each (participant_id, task_id); learning iterates all 160 trials in presentation order, transfer 0..111. |
| block | Sub-boundary inside the continuous learning task marking the two 80-trial sessions: 0 = session 1, 1 = session 2. NaN in transfer. |
| context_code | Raw `con` code 1..8 = context across both sessions (session1: 1..4, session2: 5..8); NaN in transfer. |
| context | Context within a session (`con2`), 1..4 = the four cue pairs: 1 reward/big, 2 reward/small, 3 loss/big, 4 loss/small; NaN in transfer. |
| valence | reward / loss, derived from `context`; NaN in transfer. |
| magnitude | big / small, derived from `context`; NaN in transfer. |
| cho | Raw choice code on learning trials: 1 = unfavorable (incorrect) option, 2 = favorable (correct) option; the source records learning choices as correct/incorrect, not by screen side. NaN in transfer. |
| aa | Raw choice code (1 or 2 = left/right option) on transfer trials; NaN in learning. |
| response | Learning trials (task_id 0): 0 = unfavorable option, 1 = favorable option (source `cho` - 1; the screen side is not recorded). Transfer trials (task_id 1): 0 = left cue (`stimulus_left`), 1 = right cue (`stimulus_right`) (source `aa` - 1). |
| reward | Delivered payoff of the chosen option (raw `out`) in euros: 0, +1, +0.1, -1, -0.1. NaN in transfer. |
| outcome_binary | Raw `out2`, the outcome on the context-relative scale: 1 = the better outcome of the pair (a gain in reward contexts, 0 in loss contexts), 0 = the worse one (0 in reward contexts, a loss in loss contexts); NaN in transfer. |
| feedback_info | Raw `con3`: 0 = complete feedback (chosen AND unchosen outcome shown), 1 = partial feedback (chosen outcome only). Fixed per cue pair: in each session two pairs give complete and two partial feedback (context_code 1,3,6,8 or 2,4,5,7, counterbalanced across participants). NaN in transfer. |
| counterfactual_reward | Raw `cou`: outcome of the unchosen (forgone) option in euros, recorded on every learning trial but shown to the participant only under complete feedback (feedback_info = 0); NaN in transfer. |
| counterfactual_binary | Raw `cou2`: the unchosen option's outcome on the context-relative scale (1 = the better outcome of the pair, 0 = the worse), as for `outcome_binary`. NaN in transfer. |
| stimulus_left | Transfer-trial identity (1..8) of the cue shown on the left (`ss[:,0]`); NaN in learning. Identities follow the authors' fitting code: 1/2 = favorable/unfavorable cue of the session-2 reward/big pair (context_code 5), 3/4 = reward/small (6), 5/6 = loss/big (7), 7/8 = loss/small (8). |
| stimulus_right | Transfer-trial identity (1..8) of the cue shown on the right (`ss[:,1]`); NaN in learning. |
| choice_set | JSON [left, right] cue identities presented on transfer trials; NaN in learning. |
## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: ABSOLUTE, RELATIVE, HYBRID, UTILITY, POLICY (per-participant bounded
MLE, compared on per-participant BIC, eq. 11; the released fitting code
github.com/sophiebavard/Magnitude was ported and validated against its committed
optimization outputs).
Reproduced: hybrid_best_overall (HYBRID has the lowest pooled per-participant BIC on
the 272-trial "both" fit; mean BIC hybrid=287.4 vs absolute=314.8, relative=312.9,
utility=300.1, policy=319.9; paired t-tests vs each competitor p<.05) and
counterfactual_rel_value (Exp 1: NLL(ABS)-NLL(REL) = -16.8 per subject, ABSOLUTE
fits better, t=-2.8, p=0.012; Exp 2: +9.9, RELATIVE fits better, t=2.6, p=0.013).
Not reproduced: relative_encoding_emerges (trial-by-trial log-likelihood difference
REL-ABS over the learning session is of the paper's direction — mean -0.011 over
trials 1-40, +0.007 over trials 41-80 — but neither per-half one-sample t-test
reaches p<.05: p=0.19 / 0.61, and the paired first-vs-second-half difference is
p=0.12; the paper's per-half T(59)=2.1, P=0.036/0.039, does not reproduce, nor from
the authors' own committed fit parameters under any session alignment tried).
Numeric mismatch: absolute/relative/hybrid/utility mean BICs match Table 3 within
+/-1; the POLICY model (eq. 10, divisive policy) only reproduces its reported ~308/333
BICs once the divisive denominator is taken as |Q_b|+|Q_a| (the literal Q_b+Q_a
denominator is numerically unstable and fits ~50 BIC worse); with that variant policy
BIC is 304/328 vs reported 308/333.
Partial validation: none.
Indeterminate: POLICY's exact released form is not in the published code (only
ABSOLUTE/RELATIVE/HYBRID are committed); the |Q|-sum divisive variant was adopted as
the closest faithful reading after matching the published BICs.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Added static jsPsych v8 experiments `experiments/exp0/` (Exp 1, partial feedback) and
`experiments/exp1/` (Exp 2, partial vs complete counterfactual feedback). Each reproduces
the paper's design: two learning sessions (4 novel cue-pairs × 20 → 160 trials) then a
112-trial transfer test; the saved CSV uses the exact `expN.csv` columns, dtypes and
0-indexed codings (per participant 160 learning + 112 transfer rows, `trial` restarting per
`task_id`). The headless `?mode=simulate` round trip passed for both and the rendering-
sanity check found no gross breakage. Assumption surfaced: the paper does not reprint the
verbatim instruction text, so on-screen instructions are reconstructed from the described
briefing, and the Agathodaimon cues are rendered as SVG glyphs; feedback/ITI timing, colors
and layout follow the paper as cosmetic defaults.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Text-format conversion

Both experiments (exp0 = Exp 1 partial-feedback; exp1 = Exp 2 partial/complete feedback) are textifiable and were transcribed to `transcripts0.jsonl` (N=20) and `transcripts1.jsonl` (N=40): the abstract Agathodaimon cues are renamed to letters (Session 1: A-H) and numbers (Session 2 + transfer: 1-8); the favorable cue within each fixed pair is not revealed by the source data for Session 1 (learning responses code correct/incorrect only), so it is assigned randomly per participant and kept constant. All 160 learning + 112 transfer trials per participant are included in order; transfer responses are marked as free choices. Learning responses map to the favorable/unfavorable symbol of the pair. Note: `feedback_info` follows the raw `con3` coding used by the authors' fitting code (0 = complete feedback, both outcomes shown; 1 = partial).

Sample transcript (exp0, participant 201, up to the first response):
```
You are taking part in an experiment in which you can win or lose money. Your goal is to maximize your payoff: seeking monetary rewards and avoiding monetary losses are equally important.
On each trial you see two abstract symbols, one on the left and one on the right of a central fixation cross. Each symbol is associated with a chance of producing a monetary outcome, and your task is to learn, from the outcomes you receive, which symbol is more advantageous and to choose it.
To make your choice, press the button that matches the side of the chosen symbol (leftmost or rightmost) within 3 seconds. A red pointer then marks your selection and the outcome of the chosen symbol is shown: '+1.0€', '+0.1€', '0.0€', '-0.1€' or '-1.0€'.
In this transcript every symbol has a label, and your choice is recorded as the label of the symbol you selected.
--- Session 1 begins. ---
Session 1 uses four pairs of symbols, which are labeled as follows in this transcript:
- reward/big pair: Symbol A and Symbol B
- reward/small pair: Symbol C and Symbol D
- loss/big pair: Symbol E and Symbol F
- loss/small pair: Symbol G and Symbol H
When you make a choice, type the label (A, B, C, D, E, F, G or H) of the symbol you choose.
The loss/big pair (Symbol E and Symbol F) is presented. You press [HUMAN_RESPONSE]F[/HUMAN_RESPONSE]
 …
```
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Both experiments got a simulator: `simulate0.py` (Exp 1) and `simulate1.py` (Exp 2). Each regenerates the two 80-trial learning sessions plus the 112-trial transfer test and passed the round-trip check (re-running `build_jsonl.py` on the simulated DataFrames reproduces the simulator's prompts byte-identically). No experiment was skipped as not simulatable. Design parameters (75/25 outcome probabilities, 20 reps of each of 4 contexts per session, 4 reps of each of the 28 transfer pairs) come from the paper (Methods). Assumption surfaced: Session-1 favorable letters are assigned per participant via the same (participant, context) hash as build_jsonl.py, since the raw data codes those choices as correct/incorrect only; per-session context order is a uniform permutation with no run longer than 4 (matching exp0.csv; exp1.csv has runs up to 6).
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: needs-review (critical 0, major 7, minor 7; fixed 12, open 2).

Checked: paper (10.1038/s41467-018-06781-2), original data (github.com/sophiebavard/Magnitude), exp0-exp1, transform re-run (both CSVs byte-identical), transcripts (rebuild byte-identical; 0 token or narration mismatches in an independent check of all 60), simulators (run, round trip byte-identical), analysis, logs; the CSVs reproduce the authors' committed per-subject log-likelihoods (Magnitude_Optimization_expe1/2.mat, ABSOLUTE/RELATIVE/HYBRID) to within 1e-11, which confirms every column coding. Skipped: modeling (no model.py in the repo: the cognitive-modeling:fail contract ships none, so the Reproduced: results of the modeling section could not be re-run; the authors' committed fits give pooled mean BICs of 315.3/313.9/288.5 for ABSOLUTE/RELATIVE/HYBRID, within 1.1 of the section's 314.8/312.9/287.4).

Fixed:
- README described cho and response on learning trials as the screen side (0 = leftmost, 1 = rightmost); the source codes cho as 1 = incorrect / 2 = correct (Magnitude_Behavioral_Analyses.m; in the CSV the better outcome follows response=1 on 74% of trials vs 21% for response=0). Column notes corrected: learning response = 0 unfavorable / 1 favorable, transfer response = 0 left / 1 right cue.
- README described outcome_binary and counterfactual_binary as non-zero-outcome indicators; out2/cou2 are the context-relative scale (1 = the better outcome of the pair, e.g. 0 EUR in a loss context). Column notes corrected.
- README gave feedback_info as 1 = complete / 0 = partial; the source's con3 is 0 = complete (the fitting code updates the counterfactual only when con3 == 0) and is fixed per cue pair (context_code 1,3,6,8 or 2,4,5,7 per participant). Column note corrected.
- analysis.py SYMBOL_EV swapped the loss/big and loss/small transfer symbols (5-8): the authors' fitting code maps symbols 5/6 to loss/big and 7/8 to loss/small, and the paper's 0.56 choice rate for the loss/small favorable cue (p. 3) matches symbol 7. Fixed; transfer_above_chance now t = 12.11 (was 11.76), all four effects reproduce.
- simulate0.py and simulate1.py always put the lower-numbered cue on the left in the transfer test; the CSVs present each ordered pair exactly twice (paper p. 10: equal left/right presentation). Fixed; the round trip through build_jsonl.py stays byte-identical.
- simulate1.py drew feedback_info at random per trial; the source fixes it per cue pair with two counterbalanced patterns (exp1.csv). Fixed.
- logs/auto-exp-modeling.sessions.json carried, in its first message's workspace-diff summary, a README diff from another run's workdir (jansen_2021_rational). That entry was removed; the rest of the file is unchanged.
- Column headings for exp0/exp1 raised from '###' to '####'.
- transform.py comment claimed a screen-position coding taken from a sister dataset; replaced by the source's actual coding. The CSV output is unchanged (re-run byte-identical).
- simulate0.py and simulate1.py: --seed did not seed Python's random, so the context order was not reproducible. Fixed.
- simulate1.py docstring and the README Simulators note claimed no context run longer than 4 in the shipped CSVs; exp1.csv has runs up to 6. Claim corrected.
- The Text-format note called the con3 coding 'the opposite of the transform README's earlier column note'; with the column note corrected, the clause was removed.

Open:
- minor: check_repo.py flags the transcripts as 'marked tokens do not map one-to-one onto the CSV response sequence'. The tokens are cue labels (A-H, 1-8) while response codes favorable/unfavorable in learning and left/right in transfer, so no bijection exists; an independent check of all 60 transcripts finds 0 token or narration mismatches over 272 responses each. Not a defect.
- minor: logs/auto-exp-transcribe.sessions.json names bavard_2023_functional. The mentions come from the old transform.py comment the run read and from its reasoning about the sister dataset; the session is this dataset's own, so nothing was pruned.

Run: claude-fable-5-1, 2026-09-09
