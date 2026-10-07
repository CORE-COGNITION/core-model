---
tags:
- paradigm:cue-integration
- cognitive-modeling:fail
- psych-101
- text-format:pass
- js-experiment:needs-review
- simulator:pass
---

# collsi_2023_numerical

- Paper: https://doi.org/10.1016/j.cognition.2023.105584
- Data source: https://osf.io/qx6gt
- PDF: https://uu.diva-portal.org/smash/get/diva2:1793142/FULLTEXT01.pdf
- Full text: https://uu.diva-portal.org/smash/record.jsf?pid=diva2:1793142
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Collsiöö, A., Juslin, P., & Winman, A. (2023). Is numerical information always beneficial? Verbal and numerical cue-integration in additive and non-additive tasks. Cognition, 240, 105584. https://doi.org/10.1016/j.cognition.2023.105584

## Experiment summary
Three multiple-cue judgment experiments in which participants estimate a hormone-criterion (Caldionine) from two cues across training blocks plus a test phase with old and new items, responding on a 9-step rating scale (criterion in 10-unit steps) with response times recorded throughout. Exp1 (N=80, mother tongue sample) factorially crosses cue format (verbal vs numeric) with cue-criterion relationship (additive vs non-additive) across 10 training blocks and a 2-block test; Exp2 (N=80) separates cue vs criterion format in a 2x2 verbal/numeric design (criterion format opposite the cue format); Exp3 (N=100 MTurk workers) uses a complete factorial of cue and criterion format in a non-additive task (training only, 6 blocks). The research question is whether numerical information is always beneficial in judgment learning given people's default linear-additive integration bias, with the non-additive (multiplicative) task expected to hurt learning relative to additive. The paper finds a format-by-task crossover in Exp1, worse non-additive performance in Exp2, and a verbal benefit in non-additive tasks in Exp3; it additionally fits cue-abstraction (CAM), exemplar-based (EBM), and PNP cognitive models per participant via BIC. Note: participant counts are the recruited sample present in the raw data, not the smaller analyzed N after exclusions; Exp3 excludes a test phase (not present in source).

## Notes

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (Fp, e.g. 101..180) as string |
| trial | 0..279 within each participant; training trials 0..229, test trials 230..279 |
| phase | `training` (10 blocks) or `test` (2 blocks, old + new items) |
| block | 0-indexed source Block; 0..9 in training, 10..11 in test |
| stimulus | Item ID (1..25) from source Stimulus/Stim column |
| cue1 | Cue value for hormone 1 (Progladine); Swedish verbal label or numeric `1`..`5` string depending on condition |
| cue2 | Cue value for hormone 2 (Amalydine); Swedish verbal label or numeric `1`..`5` string depending on condition |
| criterium | True criterion from source, as presented: Swedish verbal label or numeric `10`..`90` string depending on condition |
| criterium_numeric | True criterion value in numeric units (10,20,...,90) |
| response | Participant's judgment of the criterion on the 9-step scale, in numeric units (10,20,...,90) |
| rt | Response time in milliseconds (source gave seconds); NaN none here |
| condition_code | Source Condition code 1=verbal-additive, 2=numeric-additive, 3=verbal-nonadditive, 4=numeric-nonadditive |
| condition | snake_case label of condition_code (e.g. `verbal_additive`) |
| new_item | Test-phase only; source New_item flag (0..3), NaN in training; signals new vs old items per condition |
| age | Participant age in years, from Experiment1_test_processed.csv; NaN for participants absent from that file |
| gender | `f`/`m`/`other` (source Female/Male/Other), from Experiment1_test_processed.csv; NaN if absent |

### exp1
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (Fp/FP, e.g. 201..280) as string |
| trial | 0..279 within each participant; training trials 0..229, test trials 230..279 |
| phase | `training` (10 blocks) or `test` (2 blocks, old + new items) |
| block | 0-indexed source Block; 0..9 in training, 10..11 in test |
| stimulus | Item ID (1..25) from source Stim column |
| cue1 | Cue value for hormone 1; Swedish verbal label or numeric `1`..`5` string depending on condition |
| cue2 | Cue value for hormone 2; Swedish verbal label or numeric `1`..`5` string depending on condition |
| criterium | True criterion as presented: Swedish verbal label or numeric `10`..`90` string depending on condition |
| criterium_numeric | True criterion value in numeric units (10,20,...,90) |
| response | Participant's judgment of the criterion on the 9-step scale, in numeric units (10,20,...,90) |
| rt | Response time in milliseconds (source gave seconds) |
| condition_code | Source Cond code 1=numeric cues-additive, 2=verbal cues-additive, 3=numeric cues-nonadditive, 4=verbal cues-nonadditive (criterion format is the opposite of cue format) |
| condition | snake_case label of condition_code (e.g. `numeric_cues_additive`) |
| new_item | Test-phase only; source New_item flag (0..3), NaN in training |
| age | Participant age in years, from Experiment2_test_processed.csv; NaN if absent |
| gender | `f`/`m`/`other` (source Female/Male/Other), from Experiment2_test_processed.csv; NaN if absent |

### exp2
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (ID, e.g. 403..576) as string |
| trial | 0..137 within each participant, in source row order |
| phase | `training` (all rows; 6 blocks) |
| block | 0-indexed source Block (0..5) |
| stimulus | Item ID (2..13) from source Stimulus column |
| criterium | True criterion value in numeric units (10,20,...,90) |
| response | Participant's judgment of the criterion on the 9-step scale, in numeric units (10,20,...,90) |
| condition | `verbal` or `numerical` (all-verbal vs all-numerical cue+criterion format, non-additive task) |
| age | Participant age in years, from Experiment3_training_processed.csv; NaN if absent |
| gender | `f`/`m`/`other` (source Female/Male/Other), from Experiment3_training_processed.csv; NaN if absent |

The three `expN.csv` correspond to the paper's Experiments 1–3, respectively. All trials from the raw source files are emitted (both training and test phases); cue and criterion values keep their original presentation format (Swedish verbal labels or numeric strings) with numeric values also given in `criterium_numeric`/`criterium`.

## Text-format conversion

Transcribed Experiment 1 (`exp0.csv`) and Experiment 2 (`exp1.csv`): both are the same Caldionine multiple-cue judgment paradigm, fully expressible in words — the criterion (Caldionine) is estimated from two named cue hormones (Progladine, Amalydine) on a 9-step scale with feedback after training trials, so a text reader sees the same cue values and outcomes. Responses are the 9-step ordinal judgment rendered as the step number `10`–`90`; verbal-format cues appear verbatim (Swedish) with an English gloss. Experiment 3 (`exp2.csv`) was **skipped**: its rows record only the true criterion and the response, not the two cue levels the participant judged, so the per-trial stimulus is not recoverable from the data.

Sample transcript (Experiment 1, first participant, from the start through the first free response):

```
This is a multiple-cue judgment experiment. Your task is to judge the blood concentration of a fictitious hormone, Caldionin, in a patient, from the amounts of two other fictitious hormones in that patient's urine: Progladine and Amalydine. On each trial you see the level of Progladine and the level of Amalydine, and you estimate the concentration of Caldionin on a 9-step scale.
In this session the hormone levels are given as Swedish words, each with the same meaning throughout: Väldigt lite (very little), Lite (little), Medel (medium), Mycket (much), Väldigt mycket (a lot).
Your judgment is one of the nine steps: 10, 20, 30, 40, 50, 60, 70, 80, or 90, where 10 is the lowest concentration and 90 the highest. Give your judgment as that number.
After each training judgment you are told the correct concentration of Caldionin; during the test phase no feedback is given.
Progladine = Mycket (much), Amalydine = Väldigt mycket (a lot). You judge the concentration of Caldionin to be [HUMAN_RESPONSE]70[/HUMAN_RESPONSE]
```

Run: deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result (the PNP-model
categorization / division of labour, Experiment 1, paper Table 3).
Fitted models: PNP mixture (lambda,sigma,tau=1e-2) around additive cue abstraction, non-additive
cue abstraction, configural and non-configural exemplar (GCM) rules, and the null model,
per participant on test-phase judgments; BIC model selection with authors' parameterization
(bounds sigma>tau, BIC=-2LL+k*ln(n), support when BIC-best >2 below all others). Fit by
vmapped bounded L-BFGS-B multi-start seeded at the paper's lambda grid and normative
coefficients (50/10/10, 50/10/3, beta=5); implementation verified against the authors'
MATLAB PNP code and .mat test/exemplar/diff files on OSF qx6gt (identical likelihood, tau,
BIC, exemplars, and probe-exemplar distances).
Reproduced: none.
Not reproduced: division_labor_numeric - the paper's claim that with the numeric format the
proportion of participants best fit by an exemplar model is higher in the non-additive than
the additive task of Experiment 1 (67% vs 26%; BF10=7.368). Our fit instead yields additive
cell EBM=5/20 (25%) and non-additive cell EBM=1/20 (5%), i.e. the reverse: in the
numeric non-additive cell 18/20 participants are best fit by the non-additive cue
abstraction rule (coefficients at exactly 50/10/3) because the released test data show
very high rates of exact multiplicative-rule following (per-participant exact-match mean
~0.8; many at 48-50/50), and the analytic PNP term (tau=1e-2) then makes the non-additive
CAM model unbeatable (BIC <~ -300) for those participants. The additive cells reproduce
(paper 14/5, ours 15/5; the model machinery is faithful), but the headline
"exemplar memory dominates non-additive tasks" division of labour does not.
Numeric mismatch: EBM rate non-add sets 0.67 (paper) vs 0.05 (ours).
Partial validation: none.
Indeterminate: none.
Run: deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`experiments/exp0/` (Experiment 1) and `experiments/exp1/` (Experiment 2) got a
runnable static jsPsych v8 port of the Caldionine cue-judgment task; the headless
`?mode=simulate` round trip ran on a browser here and passed for every condition
(schema columns, 280 rows, per-condition/per-phase item sets). `exp2/`
(Experiment 3) was **not** built: its rows record the true criterion and the
response but not the two cue levels the participant judged, so the per-trial
stimulus is not recoverable (the same reason its transcription was skipped).
Assumptions surfaced: browser-only presentation defaults (1500 ms feedback, 500 ms
inter-trial gap, button layout, block-progress header, demographics screen,
training→test transition) — cosmetic, they do not change the task or the recorded
data; condition is assigned between-subject (URL `?condition=` override, else
random); cue values are shown verbatim (Swedish words, no English gloss) and
training feedback shows the criterion in its own presentation format.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

`simulate0.py` (Experiment 1) and `simulate1.py` (Experiment 2) reproduce the
Caldionine cue-judgment task: per-participant 10+2 training/test blocks, the 23
training / 25 test items permuted per block, and the exact deterministic
cue→criterion rules (additive `50+10*(c1-c2)`, non-additive `50+10*(c1-3)*(c2-3)`)
with verbal/numeric formatting per condition. Both passed the round-trip check
against `build_jsonl.py` (byte-identical text). `exp2` (Experiment 3) was not
simulated — its rows carry no cue levels. Assumptions: the README's PDF/full-text
bullets were unreachable (corrupt Diva PDF stub, Anubis-blocked page), so the
design was recovered from the shipped data; `rt`/`age`/`gender` dropped;
conditions assigned round-robin; judgment tokens fixed to the 9-step scale.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25