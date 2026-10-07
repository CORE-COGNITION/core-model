---
tags:
- paradigm:temporal-discounting
- cognitive-modeling:pass
- psych-201
- text-format:pass
- js-experiment:needs-review
- simulator:pass
- verification:pass
---
# haines_2020_anxiety

- Paper: https://doi.org/10.1177/2167702620929636
- Data source: https://github.com/CCS-Lab/Haines_2020_CPS (also mirrored on OSF: https://osf.io/ewzfb/)
- Full text: https://journals.sagepub.com/doi/10.1177/2167702620929636
- PDF: https://turner-mbcn.com/wp-content/uploads/2020/04/haines_clinpsychsci_final_wfigures.pdf
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Haines, N., Beauchaine, T. P., Galdo, M., Rogers, A. H., Hahn, H., Pitt, M. A., Myung, J. I., Turner, B. M., & Ahn, W.-Y. (2020). Anxiety Modulates Preference for Immediate Rewards Among Trait-Impulsive Individuals: A Hierarchical Bayesian Analysis. Clinical Psychological Science, 8(6), 1017-1036.

## Experiment summary
All participants (N=982 across three samples: 810 online MTurk, 136 student replication, 36 substance-use-disorder/treatment-seeking patients; the paper analyzed 800, 132 and 35 of them after its survey-based exclusions) completed a delay-discounting task (DDT) in which, on each trial, they chose between a smaller-sooner reward (SS, immediate) and a larger-later reward (LL, delayed). Reward amounts (in dollars; the LL reward of the adaptive trials is $800) and delays (in weeks) were titrated trial-by-trial using an adaptive algorithm; responses are binary (0=SS, 1=LL). Each participant completed two adaptive (ADO) sessions separated by a 5-min break (42 trials per session in the lab samples, 20 for MTurk). Trait impulsivity (BIS-11, incl. non-planning subscale) and state anxiety (STAI-S) were measured via survey. The research question was how trait impulsivity and state anxiety interact to modulate delay discounting, tested with hierarchical Bayesian computational models estimating reward sensitivity (α) and discounting rate (k).

## Notes

### Columns

| column | description |
|--------|-------------|
| participant_id | De-identified participant code (P000–P981; P841 is unused because that student has no trial data), remapped from MTurk worker IDs (MTURK sample) or from original lab IDs (REP/TAL samples). Raw worker IDs (A + alphanumerics) dropped for privacy. |
| trial | 0-indexed trial number, sequential within participant in session order: blocks in ascending order, and the practice trials of a block before its main/staircase trials (the source does not record the order of the ADO and staircase sessions in the lab samples). |
| response | Binary choice: 0 = smaller-sooner (left option), 1 = larger-later (right option). From source `choice` column. |
| trialNum | Raw trial number as written in the source file (0-indexed in the ADO `obs` files, 1-indexed in the `choices` files of the practice/staircase program); restarts per block. |
| matrixIndex | Index into the predefined matrix of SS/LL pairs used by the adaptive titration algorithm. |
| leftValue | Reward amount in dollars of the left option (the smaller-sooner option in ADO trials: $10–$790 in $10 steps). NaN on staircase trials whose design the source did not record. |
| leftTime | Delay in weeks for the left option (0 = immediate; non-zero on the staircase trials that showed the delayed option on the left). |
| rightValue | Reward amount in dollars of the right option ($800 in every ADO trial). |
| rightTime | Delay in weeks for the right option (ADO delay set 0.43–520 weeks, i.e. 3 days–10 years; the practice program of the lab samples wrote days, divided by 7 here). |
| phase | Session phase: `practice` (warmup trials), `main` (ADO trials), `staircase` (staircase adjustment trials). |
| block | 0-indexed block: 0=ADO1/obs1, 1=ADO2/obs2, 2=Practice (choices+design format), 3=Staircase1, 4=Staircase2. Each ADO block starts with its `practice` warm-up trials; for 60 REP participants the Staircase directories hold ADO-format files (`practobs`+`obs`), read as `practice`+`staircase` rows of blocks 3/4. |
| sample | Sample label: `mturk` (MTurk online), `rep` (student replication), `tal` (SUD patients/treatment seekers). |
| age | Participant age in years (from survey; NaN for the 13 MTurk and 3 student participants without a linked survey record). |
| sex | Participant sex, 0/1 as coded by the source's preprocessing script: 1=female for the `mturk` sample, 1=male for the `rep`/`tal` samples (the coding that matches the paper's Table 1 counts); NaN without a linked survey record. |
| BIS_1 – BIS_30 | Individual item responses on the Barratt Impulsiveness Scale (BIS-11); 30 items, 1–4 scale (from survey; NaN without a linked survey record). |
| STAI_1 – STAI_40 | Individual item responses on the State-Trait Anxiety Inventory (STAI); 40 items, 1–4 scale (from survey; NaN without a linked survey record). |
| AUDIT_1 – AUDIT_10 | Individual item responses on the Alcohol Use Disorders Identification Test (AUDIT); 10 items (from survey; NaN without a linked survey record). |
| DAST_1 – DAST_10 | Individual item responses on the Drug Abuse Screening Test (DAST-10); 10 items (from survey; NaN without a linked survey record). |
| DAST | Composite DAST-10 score (sum of DAST_1–DAST_10; from survey; NaN without a linked survey record). |
| AUDIT | Composite AUDIT score (sum of AUDIT_1–AUDIT_10; from survey; NaN without a linked survey record). |
| bis_att | BIS-11 attentional impulsiveness subscale score (from survey; NaN without a linked survey record). |
| bis_mot | BIS-11 motor impulsiveness subscale score (from survey; NaN without a linked survey record). |
| bis_noplan | BIS-11 non-planning impulsiveness subscale score (from survey; NaN without a linked survey record). |
| stai_s | STAI state anxiety score (STAI items 1–20 sum; from survey; NaN without a linked survey record). |
| stai_t | STAI trait anxiety score (STAI items 21–40 sum; from survey; NaN without a linked survey record). |

This is a single experiment (the DDT) applied across three samples (`mturk`, `rep`, `tal`), encoded as one exp0.csv with a `sample` column. All phases and blocks are preserved: practice/warmup trials (`practobs.txt`), ADO main trials (`obs1.txt`/`obs2.txt`), and staircase trials. Survey measures (BIS-11, STAI, AUDIT, DAST, demographics) were merged from the preprocessed file by participant ID for all three samples (797 of 810 MTurk, 133 of 136 student and all 36 patient participants have a record; one MTurk and one student record lack the BIS/STAI scores). Six MTurk IDs have two survey records in the source; the first is kept, so no trial row is duplicated. Repeated header lines inside restarted session files are dropped. The staircase `design_exp.txt` lists only the last trial of each of its seven delay points (delays 1, 2, 4, 26, 52, 156, 520 weeks), so the other staircase trials have NaN amounts and delays. The practice program of the lab samples wrote its delays in days (365 = 1 year); they are divided by 7 so the column is in weeks throughout. One student participant (ADD101) has header-only files and contributes no rows. MTURK `obs2.txt` files were headerless in the source and were parsed with explicit column assignment.

## Text-format conversion

The delay-discounting task (exp0.csv) was transcribed to transcripts0.jsonl; no experiments were skipped. The whole session is narrated in order — the practice, ADO main, and staircase trials — with each trial stating the two reward options (amounts in dollars, delays in natural units) and the participant's binary choice (key A = left option, key B = right option, mapping randomized per participant). Staircase trials whose options the source did not record are narrated as "the two reward options are not recorded".

Sample transcript (verbatim through the first response):

```
In this study you complete a series of choices about money. Each trial shows you two reward options side by side. In the main part of the task the left option is a smaller reward available immediately (now), and the right option is a larger reward available only after a delay (later). You press the key A to choose the option on the left, or the key B to choose the option on the right. There are no right or wrong answers; pick the option you would genuinely prefer. The full session also includes practice and staircase trials with the same key layout.
You compare: you get $220 now or $800 in 5 years. You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

`exp0` got a text simulator (`simulate0.py`) whose generated participant text is format-identical to `transcripts0.jsonl` (round-trip check through `build_jsonl.py` passed for 5 simulated participants). The ADO adaptation is approximated: each SS amount and LL delay is drawn uniformly at random from the recovered design space ($10–$790 in $10 steps; the observed delay set, in weeks), since the ADO selection algorithm is not recoverable. Sample is fixed to `mturk`; survey/demographic columns are dropped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Online experiment

`exp0/` is a static jsPsych v8 port of the delay-discounting task (a browser
reproduction of the **MTurk** session: practice + two 20-trial adaptive sessions
separated by a break). The headless `?mode=simulate` round trip passed and the
saved CSV reproduces the `exp0.csv` schema exactly (111 columns, dtypes,
codings, 0-indexed counters, blank survey columns). The run is
**needs-review**, not a clean pass: the paper's ADO algorithm (Ahn et al., 2020)
that selects each trial's dollar-day pair is **not recoverable** from the paper,
the Data-source repo (only R/Stan analysis code), or `exp0.csv`, so this build
draws each trial's amount/delay uniformly at random from the recovered design
space instead. It preserves the trial structure, phases, instruction wording,
response coding, and the dollar-day design space; only the adaptive selection
trajectory is approximated. This MTurk build presents no staircase trials (the
source's instruction text mentions them, reproduced verbatim). Cosmetic defaults
(option-card colors/layout, an advance screen instead of a timed 5-min break,
short feedback/ITI gaps) were chosen where the source does not fix them.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling results (hierarchical
Bayesian delay-discounting models: descriptive base/trait; explanatory base/trait/
incongruent). Fitted models: base & trait descriptive per group (hyperbolic discounting
with choice-sensitivity c, hierarchical MAP); explanatory trait/base/incongruent
(V = A^alpha / (1+k t), regression of alpha on STAI-S and k on BIS-NP), compared by
leave-one-group-out LPPD on SUD.
Reproduced: descriptive_trait_wins_looic; explanatory_trait_wins_lppd;
explanatory_stai_alpha_negative; explanatory_bis_k_positive.
Not reproduced: none.
Numeric mismatch: LOOIC/LPPD magnitudes differ from the paper's (approximate
leave-one-participant-out IC and MAP-based predictive densities instead of full MCMC
LOOIC/LPPD), but the model ordering and parameter directions match (trait descriptive
< base in all three groups; trait explanatory best on SUD LPPD; beta_a1 < 0, beta_k1 > 0
with p < 0.05).
Partial validation: no.
Indeterminate: no.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 4, major 3, minor 7; fixed 12, open 2).

Checked: paper (10.1177/2167702620929636; the SAGE full text is paywalled, the accepted manuscript from the co-author's lab site was used and its PDF link added), original data (https://github.com/CCS-Lab/Haines_2020_CPS; OSF ewzfb holds only the supplement), exp0, transform re-run (the original transform.py reproduces the uploaded exp0.csv byte-for-byte), transcripts (rebuilt byte-for-byte), simulator (round trip through build_jsonl.py, 5 participants), modeling (model.py, all 4 results reproduce), analysis (2/2 effects reproduce), logs. Skipped: none.

Fixed:
- critical: exp0.csv had 283 duplicate (participant, block, trial) rows: six MTurk ids (P111, P271, P320, P363, P437, P573) appear twice in the source survey file Data/Preprocessed/0_preprocessed_allgroups_allscales.txt and the left merge doubled every trial row. transform.py keeps the first survey record per participant; exp0.csv regenerated (66595 -> 66453 rows).
- critical: 34 rows held the column names as values (response NaN): 20 source files contain a repeated header line after a restarted session (e.g. TAL/TAL018/ADO1/practobs.txt, REP/ADD138/Staircase1/obs.txt). transform.py drops rows with a non-numeric trialNum.
- critical: staircase rows (blocks 3-4) carried amounts forward-filled from design_exp.txt, which only lists the last trial of each delay point (P810 trials 11-15 showed the $787/$800 design of trial 10), and the recorded delays were dropped. transform.py merges without forward fill and keeps leftTime/rightTime.
- critical: transcripts narrated amounts as cents and delays as days ('$2.20 now or $8 in 37 weeks'); the task used dollars (Ahn et al. 2020: larger-later reward fixed at $800) and weeks (paper p. 18: 't is the time delay measured in weeks'; the delay set 0.43-520 = 3 days-10 years). build_jsonl.py fixed, transcripts0.jsonl rebuilt ('$220 now or $800 in 5 years'); README units corrected (cents -> dollars, days -> weeks).
- major: trial order interleaved the practice and main trials of a block (sort by trialNum) and scrambled restarted sessions; transcripts followed that order. transform.py sorts by (participant, block, practice first) with file order kept; build_jsonl.py narrates by trial.
- major: README said the survey columns are NaN for MTurk (797/810 MTurk participants have a survey record) and 'sex: 1=female, 2=male' (values are 0/1; per the paper's Table 1 counts 1=female for mturk, 1=male for rep/tal). Rows rewritten.
- major: README gave 137 student participants; the CSV has 136 (REP/ADD101 has header-only files). The paper's analyzed N (132/800/35) added.
- minor: transform.py skipped REP/ADD189's 'Staircase1 (haines.175@osu.edu)' directory (43 trials), the Staircase*/practobs.txt of 60 REP participants, and Practice/choices.txt when design_exp.txt is absent; all read now.
- minor: the practice program of the lab samples wrote delays in days (365 = 1 year, 730 = 2 years) while every other file uses weeks; divided by 7 in transform.py and documented (inferred from the values).
- minor: analysis.py comment claimed surveys are linked only for the lab samples; comment corrected (the test itself unchanged, both effects still reproduce).
- minor: simulate0.py mirrored the wrong units ($0.10-$8.00, days) and the interleaved order, and wrote response as float / matrixIndex as int; aligned with build_jsonl.py and exp0.csv, round trip passes.
- minor: paper N (132/800/35, Table 1) vs CSV (136/810/36): the CSV keeps every participant with trial data, the paper excluded MTurk attention-check failures and 8 participants without BIS/STAI; documented in the Experiment summary.

Open:
- minor: the source's preprocessed survey file codes sex 0/1 with 1=female in the MTurk sample but 1=male in the student/SUD samples (paper Table 1: 363 m/437 f MTurk, 61 m/71 f students, 25 m/10 f SUD); values kept as in the source and documented.
- minor: the paper (p. 16) describes only two ADO sessions of 42 (lab) or 20 (MTurk) trials; the practice trials, the practice program and the staircase sessions of the lab samples are not mentioned, and the source does not record the order of the ADO and staircase sessions, so `trial` numbers the ADO blocks first (documented).

Run: claude-fable-5-1, 2026-09-10
