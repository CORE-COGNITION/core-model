---
tags:
- paradigm:risky-choice
- cognitive-modeling:needs-review
- psych-201
- js-experiment:needs-review
- text-format:pass
- simulator:pass
- verification:pass
---
# spektor_2024_absolute

- Paper: https://doi.org/10.1037/xge0001513
- Data source: https://osf.io/28qzs/
- PDF: https://wrap.warwick.ac.uk/180848/1/WRAP-absolute-and-relative-stability-of-loss-aversion-across-contexts-AAM-Spektor-2023.pdf
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Spektor, M. S., Kellen, D., Rieskamp, J., & Klauer, K. C. (2024). Absolute and relative stability of loss aversion across contexts. Journal of Experimental Psychology: General. https://doi.org/10.1037/xge0001513

## Experiment summary
Three experiments investigated whether loss aversion (and choice consistency) is stable across two gambling contexts—a loss-aversion condition (LAC) and a gain-seeking condition (GSC)—with the order of the two counterbalanced context blocks varied (starting condition). In every trial participants chose between two binary 50/50 lotteries (most pairs had equal expected value and differed in variance/risk); choices and reaction times were recorded. The loss-aversion context drew its outcomes from a wider range of gains than of losses, and the gain-seeking context from the mirrored ranges (all signs flipped). Experiments 1 (N=40), 2 (N=185, two sessions ~1 week apart × 49 trials), and 3 (N=57, two sessions × 360 trials) were analyzed with hierarchical-Bayesian prospect-theory/CPT models to estimate loss-aversion and choice-sensitivity (consistency) parameters; Experiment 3 was preregistered. exp0 / exp1 / exp2 map to paper Experiments 1 / 2 / 3 respectively, and response is coded 0 = chose gamble X, 1 = chose gamble Y.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number from source exp1.csv |
| trial | 0..351 within each participant (source `trial`, 1-indexed, minus 1); presentation order |
| response | 0 if chose gamble X, 1 if chose gamble Y (from source `rsp`) |
| rt | Reaction time to choice (source `chrt`, seconds, converted to ms) |
| condition | `gain_seeking` (GSC) or `loss_aversion` (LAC) |
| valid | 1 = all source rows carry a response |
| block | 0/1 counterbalanced context block inside the single session ((source `trial` minus 1)//176) |
| gamble | trial/gamble number 1..176 within block |
| X1 | outcome 1 magnitude of gamble X (raw) |
| X2 | outcome 2 magnitude of gamble X (raw) |
| Y1 | outcome 1 magnitude of gamble Y (raw) |
| Y2 | outcome 2 magnitude of gamble Y (raw) |
| YPos | screen position of gamble Y (left/right) |
| cclk | number of clicks made on the trial |
| fchrt | first-click reaction time, seconds |
| chrt | choice reaction time, seconds |
| okrt | OK/confirm reaction time, seconds |
| choice | which gamble label was clicked (Left/Right position) |
| order | starting-context ordering (`goodfirst`/`badfirst`) |
| ur | outcome in the upper cell of the right-hand lottery box (raw; which of X/Y is on the right varies by trial) |
| dr | outcome in the lower cell of the right-hand lottery box (raw) |
| ul | outcome in the upper cell of the left-hand lottery box (raw) |
| dl | outcome in the lower cell of the left-hand lottery box (raw) |
| liste | context label (`GSC`/`LAC`, raw) |
| trialWithinBlocks | 1..176 trial counter within block |
| rsp | chosen gamble (`X`/`Y`, raw) |
| X_ev | expected value of gamble X (raw) |
| Y_ev | expected value of gamble Y (raw) |
| Xvar | spread of gamble X: sample SD of its two outcomes (raw) |
| Yvar | spread of gamble Y: sample SD of its two outcomes (raw) |
| trial_definition | semicolon string of the four outcomes presented |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Original subject number from source exp2.csv |
| trial | 0..48 within each (participant_id, task_id); source `trial_no` order |
| response | 0 if chose gamble X, 1 if chose gamble Y (from source `choice`) |
| task_id | 0/1 experimental session (source `session_no` minus 1), sessions ~1 wk apart |
| rt | reaction time (source `RT`, ms) |
| RT | reaction time (raw, ms; identical to `rt`) |
| condition | `gain_seeking` (GSC) or `loss_aversion` (LAC) |
| valid | 1 = all source rows carry a response |
| trial_no | 1..49 within session (raw) |
| trial_id | 1..49 lottery-pair id within session (raw) |
| Xout1 | outcome 1 magnitude of gamble X (raw) |
| Xout2 | outcome 2 magnitude of gamble X (raw) |
| Yout1 | outcome 1 magnitude of gamble Y (raw) |
| Yout2 | outcome 2 magnitude of gamble Y (raw) |
| Xloc | screen location of gamble X (right/left) |
| choice_loc | chosen side (A/B position, raw) |
| choice | chosen gamble (`X`/`Y`, raw) |
| session_no | 1/2 weekly experimental session (raw) |
| firstbatch | 1/0 whether this was the first batch (raw) |
| XEV | expected value of gamble X (raw) |
| YEV | expected value of gamble Y (raw) |
| EVdiff | expected-value difference XEV-YEV (raw) |
| trial_definition | semicolon string of the four outcomes presented |
| Xvar | spread of gamble X: sample SD of its two outcomes (raw) |
| Yvar | spread of gamble Y: sample SD of its two outcomes (raw) |
| order | starting-context ordering (`goodfirst`/`badfirst`) |
| riskychoice | whether chosen gamble was the riskier (`safe`/`risky`) |

#### exp2
| column | description |
|--------|-------------|
| participant_id | Original subject number from source exp3.csv |
| trial | 0..359 within each (participant_id, task_id); source `trial` order |
| response | 0 if chose gamble X, 1 if chose gamble Y (from source `rsp`) |
| task_id | 0/1 experimental session (source `Session` minus 1), sessions ~1 wk apart |
| rt | reaction time to choice (source `chrt`, seconds, converted to ms) |
| condition | `gain_seeking` (GSC) or `loss_aversion` (LAC) |
| valid | 1 = all source rows carry a response |
| block | 0/1 half of the session (source `Block` minus 1) |
| Session | 1/2 weekly experimental session (raw) |
| gamble | trial/gamble number 1..180 within session |
| X1 | outcome 1 magnitude of gamble X (raw) |
| X2 | outcome 2 magnitude of gamble X (raw) |
| Y1 | outcome 1 magnitude of gamble Y (raw) |
| Y2 | outcome 2 magnitude of gamble Y (raw) |
| cclk | number of clicks made on the trial |
| fchrt | first-click reaction time, seconds |
| chrt | choice reaction time, seconds |
| okrt | OK/confirm reaction time, seconds |
| order | starting-context ordering (`GSC`/`LAC`, which context first) |
| ur | outcome in the upper cell of the right-hand lottery box (raw; which of X/Y is on the right varies by trial) |
| dr | outcome in the lower cell of the right-hand lottery box (raw) |
| ul | outcome in the upper cell of the left-hand lottery box (raw) |
| dl | outcome in the lower cell of the left-hand lottery box (raw) |
| liste | context label (`GSC`/`LAC`, raw) |
| trialWithinBlocks | 1..180 trial counter within block |
| Block | 1/2 half of the session (raw) |
| rsp | chosen gamble (`X`/`Y`, raw) |
| start_condition | 0/1 coding of which context block was presented first |
| var_X | half-range of gamble X, abs(X1 - X2)/2 (raw) |
| var_Y | half-range of gamble Y, abs(Y1 - Y2)/2 (raw) |
| right_risky | True/False whether gamble Y is the riskier of the pair (Yvar > Xvar; raw, not the screen side) |
| rsp_risky | 0/1 whether the risky gamble was chosen |
| Xvar | spread of gamble X: sample SD of its two outcomes (raw) |
| Yvar | spread of gamble Y: sample SD of its two outcomes (raw) |
| Xout1 | outcome 1 magnitude of gamble X (raw) |
| Xout2 | outcome 2 magnitude of gamble X (raw) |
| Yout1 | outcome 1 magnitude of gamble Y (raw) |
| Yout2 | outcome 2 magnitude of gamble Y (raw) |
| trial_definition_1 | semicolon outcome string, X outcomes then Y outcomes (Xout1;Xout2;Yout1;Yout2) |
| trial_definition_2 | semicolon outcome string, Y outcomes then X outcomes |
| trial_definition | semicolon outcome string; equals trial_definition_1 or _2, fixed per lottery pair across participants and sessions (raw) |

## Text-format conversion

All three experiments were transcribed into natural-language sessions
(`transcripts0.jsonl`, `transcripts1.jsonl`, `transcripts2.jsonl`). The task —
choosing between two binary 50/50 lotteries described by their two outcomes —
is textifiable: stating the two outcomes of each lottery preserves all the
information a participant uses, so a reader of the text makes the same choice.
No experiment was skipped. Sample transcript (exp0, from the start up to the
first recorded response):

```text
Welcome. In this study you will repeatedly choose between two lotteries, one labeled X and one labeled Y. Each lottery has two possible outcomes, each occurring with 50% probability. For example, 'X: win 10 or lose 6' means lottery X pays 10 or -6 with equal chance. On each round, press B to choose lottery X and A to choose lottery Y. You can take short breaks during each half, and there is a longer break between the two halves; the second half and its lotteries are completely independent of the first. One decision from each of the two halves of the study is drawn at random afterwards and the lottery you chose is played out for real; a share of the resulting outcome is added to or subtracted from your show-up fee of CHF 20, so your final payoff ranges from CHF 12.50 to CHF 27.50.
First half.
X: win 16 or lose 9. Y: win 22 or lose 15. You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE]
 …
```
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling — attempted a per-participant bounded-MLE fit of the streamlined CPT (power value, loss-aversion lambda) per condition, but non reproduced.
Reproduced: none.
Not reproduced: none (see Indeterminate).
Numeric mismatch: n/a.
Indeterminate: The paper's headline modeling results (the within-subject contrast of lambda between LAC and GSC contexts, and the relative-stability correlation of individual lambda estimates across contexts) are estimates of a hierarchical-Bayesian CPT fit (shared MVN(μ,Σ) over α,λ,θ per condition, NUTS in Stan). A faithful reproduction of these parameter claims requires the hierarchical model; the only tractable implementation here was a flat per-participant MLE of the same CPT likelihood, which is a material simplification of the paper's model. Under the flat fit, converged per-participant lambda estimates are noisier and the cross-context correlation of individual lambdas largely collapses (r≈0.03–0.28, mostly p>.05), so the paper's reported stability correlations (r=.46/.60/.92) do not reproduce. The behavioral (non-model) risky-choice-proportion stability correlations do reproduce with the same data, but behavioral effects are out of modeling scope.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Static jsPsych v8 browser ports of all three experiments were added under
`experiments/exp0/`, `experiments/exp1/`, and `experiments/exp2/` (built from the
paper + data; no text simulator exists). The headless `?mode=simulate` round trip
reproduced each schema exactly (column names, 0/1 response coding, and the correct
row counts 352 / 98 / 720, with `trial` restarting per `task_id` where the source
does), so `validated: true` and the visual rendering check found no breakage
(`visual_ok: true`). No participants or trials were dropped. Deviations worth
surfacing: `exp1`/`exp2` run their two weekly sessions back-to-back (the study's ≥1
week gap cannot be reproduced across one sitting); the instruction wording is
reconstructed from the paper's Method (no verbatim text is available); `exp1`'s
`firstbatch` is set to 0. All lotteries are reproduced verbatim from the dataset's
own per-condition pools. See `experiments/README.md` for details.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

All three experiments got a text simulator (`simulate0.py`, `simulate1.py`,
`simulate2.py`); the round-trip check passed for each — the `text` produced by
`build_jsonl.py` from the simulated DataFrame is byte-identical to the
simulator's own prompt. Stimuli are the verbatim per-condition lottery pools
from `exp0.csv`/`exp1.csv`/`exp2.csv` in a randomized presentation order
(each exp0 block presents the condition's 176 lottery pairs once each in a
random order, as in the data).
No experiment was skipped.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 9, minor 6; fixed 13, open 2).

Checked: paper (https://doi.org/10.1037/xge0001513, WRAP author manuscript), original data (https://osf.io/28qzs/, data/exp1.csv, data/exp2.csv, data/exp3.csv), exp0-exp2, transform re-run (all three CSVs byte-identical), transcripts (build_jsonl.py rebuild byte-identical), simulators (smoke run and round trip through build_jsonl.py), modeling (no model.py; the Modeling reproduction section and the cognitive-modeling:needs-review tag agree that nothing was reproduced), analysis (3 of 3 effects reproduce), logs. Skipped: none.

Fixed:
- Transcripts leaked the experimenter-only condition label: every block/session boundary line ended with 'Condition: loss-aversion.' or 'Condition: gain-seeking.' (paper p. 5: participants were only told the next block is independent). Removed from build_jsonl.py and simulate0-2.py; transcripts0-2.jsonl regenerated; README sample transcript updated.
- simulate0.py drew 176 trials with replacement from a 170-pair pool ('ASSUMPTION ... 170-pool + ~6 repeats'). exp0.csv has 176 distinct lottery pairs per condition, each shown exactly once per block for every participant (176 unique gamble ids per participant x block; OSF trials/exp1.csv lists 176 per condition); the 170 came from keying the pool by trial_definition, which is empty for 5 pairs and duplicated for 2. Pool now keyed by the source gamble id (176 per condition), one pass in random order; the simulated gamble column carries the pair id (also in simulate2.py); docstrings and the README Simulators note updated; round trip re-passed.
- README summary called the GSC a 'gains-savings condition'; the paper (p. 4-5) calls it the gain-seeking condition.
- README summary said every trial had equal expected value and that each context paired a sure option against a risky gamble. Paper p. 5: two binary equiprobable lotteries side by side, 142 of 176 trials equal-EV; data: 81% / 90% / 94% equal-EV rows in exp0/exp1/exp2 and no lottery with two identical outcomes. Rewritten (wider gain than loss range in the LAC, mirrored in the GSC, confirmed in all three CSVs).
- README exp1 Columns table lacked a row for the CSV column RT (raw ms, identical to rt); row added.
- README exp0/exp2 described ur/dr as gamble X and ul/dl as gamble Y. In exp0 {ur, dr} equals the right-hand lottery's outcomes in 100% of rows (via YPos) and gamble X in only 50%; rows now describe the right-hand / left-hand box cells.
- README exp2 described right_risky as 'the gamble on the right was the riskier'. right_risky == (Yvar > Xvar) in 100% of rows and is unrelated to the ur/dr side (50%); now described as 'gamble Y is the riskier'.
- README exp0 described YPos as 'screen position of the riskier/option label'; YPos is the side of gamble Y (choice/rsp/YPos consistent in 100% of rows).
- logs/auto-exp-modeling.sessions.json: the first user message's diff summary listed 4 files from another run's work dir including the vantiel_2022_meaning README (cross-run contamination); those 4 entries removed.
- README called Xvar/Yvar 'variance' (they are the sample SD of the two outcomes; exp0 rounded to 0.1, exp1 to an integer) and var_X/var_Y a 'variance estimate' (abs(X1 - X2)/2); wording corrected.
- README exp2 called trial_definition the 'actual presentation order'; it is constant per lottery pair across all participants and sessions while the ur/dr side varies per trial. Now described as fixed per pair; trial_definition_1/_2 described as X-then-Y / Y-then-X.
- README exp0: liste described as 'empty wait listing col' (it is the GSC/LAC context label) and the block formula given as trial//176 (actual (trial - 1)//176).
- README Columns headings '### expN' changed to the template's '#### expN'.

Open:
- minor: exp0.csv trial_definition is empty for 5 of the 176 pairs per condition (400 rows); the source data/exp1.csv has the same gaps. Data faithful to the source.
- minor: exp2.csv has 215 rows with rt below 100 ms (minimum 2 ms), as in the source data/exp3.csv; the paper reports no RT exclusions. Data faithful to the source.

Run: claude-fable-5-1, 2026-09-13
