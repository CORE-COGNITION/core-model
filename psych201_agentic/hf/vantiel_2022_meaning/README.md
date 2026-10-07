---
tags:
- paradigm:language-comprehension
- cognitive-modeling:fail
- psych-201
- text-format:pass
- js-experiment:needs-review
- simulator:pass
---
# vantiel_2022_meaning

- Paper: https://doi.org/10.1162/opmi_a_00066
- Data source: https://osf.io/khf3n
- Full text: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9987346/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
van Tiel, B., Sauerland, U., & Franke, M. (2022). Meaning and Use in the Expression of Estimative Probability. Open Mind, 6, 250–263.

## Experiment summary
Two experiments with human participants. Experiment 1 (N=236) had participants view vase displays of 100 red/black marbles (101 probability levels) and freely complete a sentence frame describing the probability of drawing a red marble, producing free-text words of estimative probability (WEPs) that were then coded to categories. Experiment 2 (N=50) measured numerosity estimation: participants estimated the number of red marbles in a display, giving an RT and numeric estimate per trial. The paper tests whether gradience in WEP use can arise from crisp threshold semantics by comparing threshold-based vs prototype-based computational models within the Rational Speech Act framework, fit via Bayesian inference, and tests whether autistic traits (AQ) modulate a rationality parameter in the speaker model.

## Notes

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject/exp session ID from source CSV (codedResults.csv expId) |
| trial | 0..N-1 display order within each participant (source trial, 1-based, minus 1) |
| response | Coded word of estimative probability (WEP) the participant freely produced (e.g. 'likely', 'almost certain') |
| raw | Verbatim free-text response before coding to the WEP category |
| probability | Number of red marbles out of 100 shown in the vase display (1-100, the true probability of drawing red) |
| imageURL | URL of the vase-display stimulus image shown on that trial |
| aq | Autism-Spectrum Quotient score (self-report, 10-50 scale) |
| age | Participant age in years |
| language | Participant's self-reported native/primary language |
| gender | Participant gender (f/m/na) mapped from source 'female'/'male' |

### exp1
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (0..49) |
| trial | 0..N-1 within each participant (source item, 1-based, minus 1) |
| response | Numerosity estimate — participant's estimate of the number of red marbles in the display |
| item | Source item number (1..25) within each participant |
| rt | Reaction time in milliseconds |
| probability | True number of red marbles (1-100) shown in the display |
| age | Participant age in years |
| language | Participant's self-reported language |
| gender | Participant gender (f/m) mapped from source 'female'/'male' |
| variance | Per-participant variance in responses (Weber-fraction related measure from source demographicInfo) |

Note: exp1 was transformed from the full `codedResults.csv` (all 25 displays, N=236); `selectedResults.csv` holds only the analyzed WEP subset and was not used. One source row in exp0 carries a stray 'Male' value in the age column (expId 1585607058) — a source glitch carried through as-is.

## Text-format conversion

Transcribed exp0.csv (production task, N=236): participants freely complete the sentence frame "If you randomly take a marble from this vase, ______ that it is red" with a word/phrase (no numbers), so the transcript renders the vase's red/black marble counts and the participant's free-text completion. exp1.csv was skipped as not textifiable: it is a numerosity-estimation task in which participants estimate the number of red marbles from a visual display — stating the true count would make the task trivial, removing the perceptual information the participant actually uses.

Sample transcript (first response):

```
You will see vases each containing 100 randomly distributed marbles, some red and some black. Your task is to describe the chance that a marble randomly taken from the vase is red. For each vase, freely complete the sentence frame: 'If you randomly take a marble from this vase, ______ that it is red.' Fill in the blank with a word or phrase of your choosing. Do not use numbers or percentages.
The vase has 66 red marbles and 34 black marbles. You complete the sentence 'If you randomly take a marble from this vase, ______ that it is red.' You write [HUMAN_RESPONSE]likely[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments got a static jsPsych v8 port (`experiments/exp0/`, `experiments/exp1/`; see
`experiments/README.md`). The headless `?mode=simulate` round trip **validated** both: each
reproduces its `expN.csv` schema exactly (columns, dtypes, 25 rows per participant, 0-indexed
`trial`; exp1 also fills `rt` from the browser). Visual rendering check passed.

Build is marked **needs-review** because substantive assumptions changed the data/task and
could not be recovered: (1) **stimulus content** — the vase displays are rendered
programmatically (exactly `probability` red of 100 marbles, deterministic per probability)
instead of the source's photographic images, so `imageURL` is left empty; (2) **exp0 response
coding** — `response` is the verbatim completion stripped of its leading sentence-frame filler
(a heuristic; the paper's full WEP category coding is not reproduced); (3) `aq` (exp0) and
`variance` (exp1) are left empty — the 50-item AQ items and the Weber-fraction derivation are
not available in the repo/paper text; (4) exp1 instructions are derived from the paper's
description rather than verbatim (exp1 was not transcribed).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

`simulate0.py` simulates exp0 (the production task): each participant draws 25 displays
uniformly without replacement from the 101 probability levels (0-100 red marbles, per the
paper's Exp. 1 procedure) and freely completes the sentence frame. The round-trip check
via `build_jsonl.py` passed byte-identically. exp1 was not transcribed, so it gets no
simulator. ASSUMPTIONS: the `response` column is set equal to the verbatim `raw` (the paper's
WEP category coding is not reproduced); `imageURL` and the self-report demographics (`aq`,
`age`, `language`, `gender`) are dropped as not producible by a text simulator.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling results.
Fitted models: the paper's four RSA speaker models (literal/pragmatic x threshold/prototype lexicon) plus the two-lambda AQ model, fit by Bayesian NUTS (numpyro; the paper used Stan) on per-state WEP counts, compared on the paper's held-out test elpd (loo-style posterior-predictive log pointwise predictive density); the Exp-2 Weber fraction was re-estimated by ML.
Reproduced: aq_rationality_parameter (posterior lambda_high 0.838 < lambda_low 1.003, paired t(7999)=254, p<.001; paper 1.44 < 1.64, t(31520)=206); weber_fraction (ML w=0.349; paper 0.35).
Not reproduced: speaker_model_comparison — prag_prototype is the best model (matches paper's optimal model), but prag_threshold is 43.0 elpd (se 11.0) WORSE than prag_prototype, i.e. the paper's central claim that "a threshold-based semantics explains the data equally well as a prototype-based one" (paper Table 1: prag_threshold -6.4, se 8.0) does not hold; literal models are -5.3 (lit_prototype) and -54.0 (lit_threshold) relative to the best model.
Numeric mismatch: model-comparison elpd diffs (-43.0/-5.3/-54.0) vs paper (-6.4/-13.8/-63.2); AQ lambda magnitudes (0.84/1.00 vs 1.44/1.64) differ but direction/significance match; Weber fraction matches (0.349 vs 0.35).
Partial validation: none.
Indeterminate: none (all fits ran; NUTS divergences limited to the pragmatic-prototype fit and did not change the robust ranking).
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
