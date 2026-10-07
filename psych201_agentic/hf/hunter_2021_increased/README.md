---
tags:
- paradigm:bandit
- cognitive-modeling:fail
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
---

# hunter_2021_increased

- Paper: https://doi.org/10.1038/s41562-021-01180-y
- Data source: https://github.com/ndawlab/patentrace
- Full text: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9849449
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Hunter, L. E., Meer, E. A., Gillan, C. M., Hsu, M., & Daw, N. D. (2021). Increased and biased deliberation in social anxiety. Nature Human Behaviour, 6(1), 146–154.

## Experiment summary
In two large general-population samples (experiment 1, N=412; experiment 2, N=331; 743 total) subjects played the socially framed Patent Race game — a two-armed (multi-level) model-based reinforcement-learning task. On each of ~80 trials a subject chose a patent-investment move among options (source `s1`, 1..5) against an opponent move (`s2`, 1..6) and received a payoff from a payoff matrix. The authors fitted a computational learning model (inverse temperature, learning rate, counterfactual-updating parameter) via expectation-maximization to subject choices, then regressed per-subject parameters on psychiatric self-report covariates (LSAS social anxiety and other symptom factors). The headline finding is that self-reported social anxiety predicts increased deliberative/model-based evaluation, specifically for upward-counterfactual feedback, linking social-anxiety rumination to reinforcement-learning mechanisms.

## Notes

### Columns

Both experiments share the same columns (exp0 = paper Experiment 1, exp1 = paper Experiment 2).

### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (string of integer `sub`, 1..743) |
| trial | 0..79, sequential response order within each participant |
| response | Participant's patent-investment choice `s1`, 0-indexed (0..4 = source s1 1..5) |
| s1 | Raw participant investment move (1..5) from source |
| s2 | Opponent move (1..6) from source, used to compute the payoff |
| reward | Payoff delivered, from payoff matrix M[s1,s2] (source `r`) |
| exp | Experiment marker from mergedcovars (1 = experiment 1) |
| ravens | Raven's matrices score (per-subject covariate) |
| lsas | Liebowitz Social Anxiety Scale total score |
| lsasZ | Z-scored LSAS |
| iq | IQ estimate (per-subject covariate) |
| iqZ | Z-scored IQ |
| age | Participant age in years |
| ageZ | Z-scored age |
| f1 | Symptom factor score 1 |
| f2 | Symptom factor score 2 |
| f3 | Symptom factor score 3 |
| trial_raw | Raw 1-indexed trial counter `t` from source |

### exp1
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (string of integer `sub`, 1..743) |
| trial | 0..79, sequential response order within each participant |
| response | Participant's patent-investment choice `s1`, 0-indexed (0..4 = source s1 1..5) |
| s1 | Raw participant investment move (1..5) from source |
| s2 | Opponent move (1..6) from source, used to compute the payoff |
| reward | Payoff delivered, from payoff matrix M[s1,s2] (source `r`) |
| exp | Experiment marker from mergedcovars (2 = experiment 2) |
| ravens | Raven's matrices score (per-subject covariate) |
| lsas | Liebowitz Social Anxiety Scale total score |
| lsasZ | Z-scored LSAS |
| iq | IQ estimate (per-subject covariate) |
| iqZ | Z-scored IQ |
| age | Participant age in years |
| ageZ | Z-scored age |
| f1 | Symptom factor score 1 |
| f2 | Symptom factor score 2 |
| f3 | Symptom factor score 3 |
| trial_raw | Raw 1-indexed trial counter `t` from source |

`exp0.csv` maps to the paper's Experiment 1 and `exp1.csv` to Experiment 2 (per the `exp` marker in `mergedcovars.csv`). The model-fitted per-subject parameters (inverse temperature, learning rate, counterfactual-updating) are not included in the uploaded CSVs; the covariate and raw-choice data needed to re-fit them are present.

## Text-format conversion

Both experiments (exp0 = Experiment 1, exp1 = Experiment 2) were transcribed: each participant's 80 Patent Race rounds as instructions, then per-round investment choice, opponent reveal, and payoff. No experiment was skipped — the game is fully textifiable (fixed discrete options with explicit payoffs). Sample transcript (start through first response):

```
You are a small company competing against a larger rival firm in a patent race. On each of 80 rounds, both you and your rival decide how much money to invest in developing a new patent. The firm that invests strictly more wins the $10 prize for that round; if you both invest the same amount, nobody wins the prize. You are endowed with $4 each round, which you may invest in whole dollars: $0, $1, $2, $3, or $4. Your rival is endowed with $5 and may invest any whole dollar amount from $0 to $5. Whatever you do not invest you keep, whether or not you win. To choose, type the number of dollars you want to invest: 0 for $0, 1 for $1, 2 for $2, 3 for $3, or 4 for $4. After you invest, your rival's investment is revealed, and you receive the prize if you invested strictly more.
You press [HUMAN_RESPONSE]0[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

Both experiments got a text simulator (`simulate0.py`, `simulate1.py`), each passed the round-trip check through `build_jsonl.py` (regenerated transcript texts byte-identical to the simulator prompts, fixed token mapping). No experiment was skipped. The opponent's move is sampled per round from the empirical per-round distribution recovered from the pooled data, since the paper specifies no opponent-strategy constants (an `ASSUMPTION:` recorded in the simulator class docstrings).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments got a static jsPsych v8 port (`experiments/exp0/`, `experiments/exp1/`) of the Patent Race game: 80 rounds, invest $0–$4 against the opponent drawn from the embedded per-round distribution. The headless `?mode=simulate` round trip passed for both (80 rows, `trial` 0–79, `response` 0–4, `s1 = response + 1`, `s2` 1–6, `reward`/`exp`/`trial_raw` in the source coding). `ASSUMPTION:` the per-subject questionnaire/covariate columns (`ravens`, `lsas`, `lsasZ`, `iq`, `iqZ`, `age`, `ageZ`, `f1`, `f2`, `f3`) are not generated by the game and are left blank; the opponent-reveal interval and button styling are cosmetic browser defaults. Each session saves one CSV in the dataset schema, offered as a download (no data-collection backend).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction

Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: standard EWA (`delta`) and valenced EWA (`delta+`/`delta-`) via an
empirical-Bayes EM (Huys et al. 2011 / ndawlab `em`), each fit on exp0, exp1 and the
pooled 743; compared by integrated BIC (iBIC); per-subject parameters regressed on
within-cohort z-scored LSAS and IQ (OLS and mixed-effects for the delta+/delta- test).
Reproduced: valenced EWA fits better than standard EWA by iBIC (merged 34026 -> 32559,
and in each experiment); LSAS positively predicts `delta` (pooled est .034, t=4.27,
p=2e-5; paper .029, t=3.61) and positively predicts `delta+` (p=5e-5).
Not reproduced: the valence-specific claims fail to reach significance as the paper
reports -- `delta-` comes out marginally positively associated with LSAS (pooled
p=.041; null per-experiment, p=.13/.15, so the paper's "no significant relationship
with delta-" holds only per-experiment), and the `delta+` vs `delta-` LSAS contrast
(paper: p<.0014 combined) does not reach p<.05 here (pooled LME interaction p=.053).
Numeric mismatch: iBIC magnitudes differ from the paper (paper merged 57511 vs 56225;
ours 34026 vs 32559) -- direction matches, absolute scale differs.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
