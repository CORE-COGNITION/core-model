---
tags:
- paradigm:behavioral-propensity-rating
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
---

# Singh_2022_Representing

- Paper: https://doi.org/10.1007/s42113-021-00121-2
- Data source: https://osf.io/93nfb/
- PDF: https://osf.io/download/7rf5y/
- Full text: https://osf.io/preprints/psyarxiv/kb53h_v1/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Singh, M., Richie, R., & Bhatia, S. (2022). Representing and Predicting Everyday Behavior. Computational Brain & Behavior.

## Experiment summary

The paper compiles ~4,000 common human behavior phrases and measures self-reported behavioral propensities. In the uploaded behavioral-propensity survey, 319 US-representative Prolific participants each rated a randomly-assigned block of ~247 behaviors (there were 16 blocks, 15 with 247 and 1 with 233 behaviors; 78,116 total ratings) on a 1–7 Likert scale to the statement "Relative to others, I am likely to [behavior]", then completed psychographic questionnaires (TIPI personality, Domain-Specific Risk-Taking, Barratt Impulsiveness, Self-Report Altruism, Grit, Satisfaction-with-Life, Maximization) and demographic items. The response is the raw 1–7 propensity rating; the authors used USE/BERT/Word2Vec semantic representations of the phrases plus the psychographic/demographic covariates to train ridge-regression and multilayer-perceptron models predicting propensities out-of-sample (for novel behaviors and novel participants). This single public trial-level dataset (exp0) corresponds to the propensity survey; the paper's separate phrase-validation-coding study (438 coders) is archived only as procedure materials, not raw ratings.

## Notes

### Columns

| column | description |
|--------|-------------|
| participant_id | Remapped participant number (1..319), as provided by authors in `behavior_propensity_data_remapped_pids.csv` (original Prolific IDs already anonymized by authors). |
| trial | 0..N-1 index of behaviors within each participant, in file order (the raw file is ordered primarily by phrase, cycling through participants, so no true per-participant presentation order exists). |
| response | Raw behavioral-propensity rating, Likert 1 (strongly disagree) to 7 (strongly agree). Native Likert indexing. |
| propensity_z | The z-scored version of `response` (author-normalized within each pair/training-test set). |
| phrase | The behavior verb-phrase statement text (e.g. "abandon a plan"). `phrase_id` is its numeric id. |
| male / female, hispanic_latino / not_hispanic_latino, less_than_high_school...professional_degree, $10,000...More than $150,000, Under 18...85 or older, Married...Never Married, Full-time Employment...Self-Employed, White...Other | One-hot demographic/ethnicity/education/income/age/marital/employment/race flags, constant across a participant's rows. |
| Grit, Agreeableness, Openness to Experiences, Satisfaction with Life, Risk Taking, Conscientiousness, Altruism, Impulsiveness, Maximization, Extraversion, Emotional Stability | Composite psychographic subscale scores per participant. |
| ~40 questionnaire item columns (prefixed by their item text) | Raw item responses to the psychographic questionnaires, one column per item, constant across a participant's rows. |

All psychographic/demographic columns are per-participant covariates; `response` is the only per-trial behavioral variable. Likert ratings are retained in native 1–7 units (the `propensity_z` column is a derived/normalized author-computed field, kept for reference).

## Text-format conversion

`exp0.csv` (the behavioral-propensity survey) was transcribed: each participant's ~247 verb-phrase ratings become one natural-language transcript, with each 1–7 Likert response wrapped as a `[HUMAN_RESPONSE]` token. There is only this single experiment, so nothing was skipped. Per-participant demographic and psychographic covariates are carried as metadata.

Sample transcript (start of participant 1, through the first response):

```
You will be shown a series of everyday behavior phrases. For each one, you judge how much you agree with the statement "Relative to others, I am likely to [behavior]", comparing yourself against the general population rather than only your peers. For each phrase, respond with a number from 1 to 7, where 1 means strongly disagree, 2 means disagree, 3 means somewhat disagree, 4 means neither agree nor disagree, 5 means somewhat agree, 6 means agree, and 7 means strongly agree.
Relative to others, you are likely to: abandon a plan. You rate your agreement (1-7): [HUMAN_RESPONSE]5[/HUMAN_RESPONSE].
 …
```

Run: deepseek-v4-flash-0731, 2026-08-24

## Simulators

`exp0` has a text simulator (`simulate0.py`) that reproduces the behavioral-propensity survey: each simulated participant draws one of the paper's 16 blocks (15×247, 1×233 phrases) and rates every phrase on the 1–7 Likert scale. The round-trip check through `build_jsonl.py` passes byte-identically. No experiments were skipped. Assumptions: block phrases are presented in alphabetical (file) order; blocks are drawn uniformly per participant; `propensity_z` and psychographic/demographic covariates are dropped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`exp0` (the behavioral-propensity rating survey) got a runnable static jsPsych v8 experiment at `experiments/exp0/`, built from the `simulate0.py` simulator. The headless round trip passed: a simulated session produces a CSV in `exp0.csv`'s trial-level schema (`participant_id, trial, response, phrase, phrase_id`) with 247 rows, `trial` 0-indexed and `response` in native 1–7 Likert units. No experiments were skipped. The browser experiment's saved CSV omits `exp0.csv`'s per-participant covariate columns (`propensity_z`, psychographic item/subscale scores, demographic one-hot flags), which come from a separate retrospective questionnaire phase not reproduced here — matching the simulator's own assumption.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25