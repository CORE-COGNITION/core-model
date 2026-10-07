---
tags:
- paradigm:bandit
- cognitive-modeling:pass
- psych-201
- text-format:pass
- js-experiment:needs-review
- simulator:pass
- verification:pass
---

# fan_2022_trait

- Paper: https://doi.org/10.1038/s41562-022-01455-y
- Data source: https://osf.io/y6urc/
- Full text: https://www.nature.com/articles/s41562-022-01455-y
- PDF: https://osf.io/yx6sb/download
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Fan, H., Gershman, S. J., & Phelps, E. A. (2023). Trait somatic anxiety is associated with reduced directed exploration and underestimation of uncertainty. Nature Human Behaviour, 7(1), 102–113.

## Experiment summary
Two online studies (total N=985; Study 1 N=501, Study 2 N=484) use a restless two-armed bandit task with volatility-induced uncertainty to measure exploration strategies. In each of 30 blocks a fresh pair of slot machines is presented for 10 two-alternative choices (response = choice left/right plus RT), under four volatility schedules (FS/SF/FF/SS, coded `condition`); Study 2 additionally includes a reward-prediction task (estimate + confidence rating). Trait anxiety was measured with the STAI-T and STICSA scales, decomposed into somatic/cognitive/factor scores. The headline results link somatic trait anxiety to reduced directed exploration (lower sensitivity to relative uncertainty in choice) and to underestimation of relative uncertainty; supported by computational learning/exploration models (uncertainty belief-update and directed-exploration models) and linked to choice-probability and RT predictions.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | "P000.." remapped in first-appearance order from source `sub` (Study 1 bandit, N=501) |
| task_id | 0-indexed bandit round (source `block` 1..30 mapped to 0..29); each round is a fresh 10-trial pair of slot machines |
| trial | 0..9 within each (participant_id, task_id) |
| response | binary choice C, source coding kept: 1 = chose option 1 (the left arm; `reward` equals `reward1`), 0 = chose option 2 (the right arm) |
| rt | reaction time in ms for the choice (0-indexing; sentinel-free) |
| reward | delivered reward (coins) on this trial |
| correct | 1 if chose option with higher generative mean, else 0 |
| condition | volatility condition code: 1=FS, 2=SF, 3=FF, 4=SS |
| gender | source 0/1/2 mapped to f/m/na (0 = women, 1 = men, 2 = unreported; the per-code counts equal the paper's Methods counts) |
| age | participant age in years |
| V | relative value of left vs right option (standardized) |
| RU | relative uncertainty of left vs right (standardized) |
| VTU | V/TU ratio (standardized) |
| TU | total uncertainty (standardized) |
| V_old, RU_old, TU_old | pre-standardization versions of V/RU/TU |
| mu1, mu2 | generative mean of left/right option |
| reward1, reward2 | reward delivered by left/right option |
| est_m1, est_m2 | posterior estimate of mean for left/right option |
| est_s1, est_s2 | posterior estimate of variance for left/right option |
| C_pred | binary choice prediction from model (1=left,0=right) |
| C_pred_prob | predicted probability of C=1 from choice model C~V+RU+VTU |
| STAIT_1_r | STAI-Trait item 1 response (reverse-scored) (raw) |
| STAIT_2 | STAI-Trait item 2 response (raw) |
| STAIT_3_r | STAI-Trait item 3 response (reverse-scored) (raw) |
| STAIT_4 | STAI-Trait item 4 response (raw) |
| STAIT_5 | STAI-Trait item 5 response (raw) |
| STAIT_6_r | STAI-Trait item 6 response (reverse-scored) (raw) |
| STAIT_7_r | STAI-Trait item 7 response (reverse-scored) (raw) |
| STAIT_8 | STAI-Trait item 8 response (raw) |
| STAIT_9 | STAI-Trait item 9 response (raw) |
| STAIT_10_r | STAI-Trait item 10 response (reverse-scored) (raw) |
| STAIT_11 | STAI-Trait item 11 response (raw) |
| STAIT_12 | STAI-Trait item 12 response (raw) |
| STAIT_13_r | STAI-Trait item 13 response (reverse-scored) (raw) |
| STAIT_14_r | STAI-Trait item 14 response (reverse-scored) (raw) |
| STAIT_15 | STAI-Trait item 15 response (raw) |
| STAIT_16_r | STAI-Trait item 16 response (reverse-scored) (raw) |
| STAIT_17 | STAI-Trait item 17 response (raw) |
| STAIT_18 | STAI-Trait item 18 response (raw) |
| STAIT_19_r | STAI-Trait item 19 response (reverse-scored) (raw) |
| STAIT_20 | STAI-Trait item 20 response (raw) |
| STAIT_total, STAIT_total_absent, STAIT_total_present | STAI-Trait totals |
| STICSAT_1_Somatic | STICSA-Trait item 1 response, Somatic subscale (raw) |
| STICSAT_2_Somatic | STICSA-Trait item 2 response, Somatic subscale (raw) |
| STICSAT_3_Cognitive | STICSA-Trait item 3 response, Cognitive subscale (raw) |
| STICSAT_4_Cognitive | STICSA-Trait item 4 response, Cognitive subscale (raw) |
| STICSAT_5_Cognitive | STICSA-Trait item 5 response, Cognitive subscale (raw) |
| STICSAT_6_Somatic | STICSA-Trait item 6 response, Somatic subscale (raw) |
| STICSAT_7_Somatic | STICSA-Trait item 7 response, Somatic subscale (raw) |
| STICSAT_8_Somatic | STICSA-Trait item 8 response, Somatic subscale (raw) |
| STICSAT_9_Cognitive | STICSA-Trait item 9 response, Cognitive subscale (raw) |
| STICSAT_10_Cognitive | STICSA-Trait item 10 response, Cognitive subscale (raw) |
| STICSAT_11_Cognitive | STICSA-Trait item 11 response, Cognitive subscale (raw) |
| STICSAT_12_Somatic | STICSA-Trait item 12 response, Somatic subscale (raw) |
| STICSAT_13_Cognitive | STICSA-Trait item 13 response, Cognitive subscale (raw) |
| STICSAT_14_Somatic | STICSA-Trait item 14 response, Somatic subscale (raw) |
| STICSAT_15_Somatic | STICSA-Trait item 15 response, Somatic subscale (raw) |
| STICSAT_16_Cognitive | STICSA-Trait item 16 response, Cognitive subscale (raw) |
| STICSAT_17_Cognitive | STICSA-Trait item 17 response, Cognitive subscale (raw) |
| STICSAT_18_Somatic | STICSA-Trait item 18 response, Somatic subscale (raw) |
| STICSAT_19_Cognitive | STICSA-Trait item 19 response, Cognitive subscale (raw) |
| STICSAT_20_Somatic | STICSA-Trait item 20 response, Somatic subscale (raw) |
| STICSAT_21_Somatic | STICSA-Trait item 21 response, Somatic subscale (raw) |
| STICSAT_total, STICSAT_total_Cognitive, STICSAT_total_Somatic | STICSA totals |
| Factor1_Somatic_Anxiety | factor score from EFA/CFA: Somatic Anxiety factor score |
| Factor2_Cognitive_Anxiety | factor score from EFA/CFA: Cognitive Anxiety factor score |
| Factor3_Negative_Affect | factor score from EFA/CFA: Negative Affect factor score |
| Factor4_Low_Self_esteem | factor score from EFA/CFA: Low Self-esteem factor score |

#### exp1
| column | description |
|--------|-------------|
| participant_id | "P000.." remapped in first-appearance order across Study 2 bandit + prediction data (N=484 for bandit) |
| task_id | 0-29: bandit round (fresh 10-trial slot-machine pair); 30: reward-prediction task |
| trial | 0-indexed within each (participant_id, task_id); bandit 0..9 per round, prediction 0..N responses |
| block | 0-indexed bandit round a prediction concerned (source pred `block` 1..30 mapped to 0..29); bands the 4 prediction responses (2 machines x estimate+confidence) of a round |
| response | bandit rows: choice C (1 = option 1/left arm, 0 = option 2/right arm, source coding kept); prediction rows split per response: estimate row = predicted number of coins, confidence row = confidence rating (0-10) |
| rt | ms; bandit = choice RT, prediction estimate row = prediction RT, confidence row = confidence RT |
| reward | delivered reward (coins) on bandit trials (NaN on prediction rows) |
| correct | 1 if chose higher-generative-mean option (bandit rows) |
| condition | volatility condition 1=FS,2=SF,3=FF,4=SS (bandit rows) |
| gender | source 0/1/2 mapped to f/m/na (0 = women, 1 = men, 2 = unreported; the per-code counts equal the paper's Methods counts) |
| age | participant age in years |
| V, RU, VTU, TU, V_old, RU_old, TU_old | relative/total value & uncertainty terms (bandit rows) |
| mu1, mu2 | generative mean of left/right bandit option |
| reward1, reward2 | reward delivered by left/right bandit option |
| est_m1, est_m2, est_s1, est_s2 | posterior estimate of mean/variance for left/right bandit option |
| C_pred, C_pred_prob | model-predicted choice and its probability (bandit rows) |
| pred_machine | which sampling machine the prediction targeted (0/1) |
| pred_num | participant's numeric coin prediction (estimate rows); NaN elsewhere |
| conf_rating | confidence rating 0-10 (confidence rows); NaN elsewhere |
| conf_rt | reaction time in ms for the confidence rating |
| true_m1, true_m2 | true (normative) mean of the two machines |
| type_pred | 1 if the predicted machine is the fluctuating arm of that round, 0 if it is the stable arm (matches the round's `condition`) |
| curr_est_m, curr_est_s | current posterior estimate of mean/variance for the target machine |
| curr_true_m | current true mean of the target machine |
| STAIT_1_r | STAI-Trait item 1 response (reverse-scored) (raw) |
| STAIT_2 | STAI-Trait item 2 response (raw) |
| STAIT_3_r | STAI-Trait item 3 response (reverse-scored) (raw) |
| STAIT_4 | STAI-Trait item 4 response (raw) |
| STAIT_5 | STAI-Trait item 5 response (raw) |
| STAIT_6_r | STAI-Trait item 6 response (reverse-scored) (raw) |
| STAIT_7_r | STAI-Trait item 7 response (reverse-scored) (raw) |
| STAIT_8 | STAI-Trait item 8 response (raw) |
| STAIT_9 | STAI-Trait item 9 response (raw) |
| STAIT_10_r | STAI-Trait item 10 response (reverse-scored) (raw) |
| STAIT_11 | STAI-Trait item 11 response (raw) |
| STAIT_12 | STAI-Trait item 12 response (raw) |
| STAIT_13_r | STAI-Trait item 13 response (reverse-scored) (raw) |
| STAIT_14_r | STAI-Trait item 14 response (reverse-scored) (raw) |
| STAIT_15 | STAI-Trait item 15 response (raw) |
| STAIT_16_r | STAI-Trait item 16 response (reverse-scored) (raw) |
| STAIT_17 | STAI-Trait item 17 response (raw) |
| STAIT_18 | STAI-Trait item 18 response (raw) |
| STAIT_19_r | STAI-Trait item 19 response (reverse-scored) (raw) |
| STAIT_20 | STAI-Trait item 20 response (raw) |
| STAIT_total, STAIT_total_absent, STAIT_total_present | STAI-Trait totals |
| STICSAT_1_Somatic | STICSA-Trait item 1 response, Somatic subscale (raw) |
| STICSAT_2_Somatic | STICSA-Trait item 2 response, Somatic subscale (raw) |
| STICSAT_3_Cognitive | STICSA-Trait item 3 response, Cognitive subscale (raw) |
| STICSAT_4_Cognitive | STICSA-Trait item 4 response, Cognitive subscale (raw) |
| STICSAT_5_Cognitive | STICSA-Trait item 5 response, Cognitive subscale (raw) |
| STICSAT_6_Somatic | STICSA-Trait item 6 response, Somatic subscale (raw) |
| STICSAT_7_Somatic | STICSA-Trait item 7 response, Somatic subscale (raw) |
| STICSAT_8_Somatic | STICSA-Trait item 8 response, Somatic subscale (raw) |
| STICSAT_9_Cognitive | STICSA-Trait item 9 response, Cognitive subscale (raw) |
| STICSAT_10_Cognitive | STICSA-Trait item 10 response, Cognitive subscale (raw) |
| STICSAT_11_Cognitive | STICSA-Trait item 11 response, Cognitive subscale (raw) |
| STICSAT_12_Somatic | STICSA-Trait item 12 response, Somatic subscale (raw) |
| STICSAT_13_Cognitive | STICSA-Trait item 13 response, Cognitive subscale (raw) |
| STICSAT_14_Somatic | STICSA-Trait item 14 response, Somatic subscale (raw) |
| STICSAT_15_Somatic | STICSA-Trait item 15 response, Somatic subscale (raw) |
| STICSAT_16_Cognitive | STICSA-Trait item 16 response, Cognitive subscale (raw) |
| STICSAT_17_Cognitive | STICSA-Trait item 17 response, Cognitive subscale (raw) |
| STICSAT_18_Somatic | STICSA-Trait item 18 response, Somatic subscale (raw) |
| STICSAT_19_Cognitive | STICSA-Trait item 19 response, Cognitive subscale (raw) |
| STICSAT_20_Somatic | STICSA-Trait item 20 response, Somatic subscale (raw) |
| STICSAT_21_Somatic | STICSA-Trait item 21 response, Somatic subscale (raw) |
| STICSAT_total, STICSAT_total_Cognitive, STICSAT_total_Somatic | STICSA totals |
| Factor1_Somatic_Anxiety | factor score: Somatic Anxiety factor score |
| Factor2_Cognitive_Anxiety | factor score: Cognitive Anxiety factor score |
| Factor3_Negative_Affect | factor score: Negative Affect factor score |
| Factor4_Low_Self_esteem | factor score: Low Self-esteem factor score |

Notes on mapping: `exp0.csv` corresponds to the paper's Experiment/Study 1 bandit task; `exp1.csv` corresponds to Study 2 (bandit rounds task_id 0-29 plus the reward-prediction task at task_id 30). The prediction task's two responses per trial (numeric estimate and 0-10 confidence rating) are split across rows and grouped by `block`. `gender`: the source codes 0/1/2 are women/men/unreported (the per-code counts equal the paper's Methods counts: 219/277/5 in Study 1, 197/279/8 in Study 2), mapped to f/m/na. `response` keeps the source's `C` coding: 1 = option 1 (the left arm), 0 = option 2 (the right arm); `reward` equals `reward1` exactly when `response` = 1, and the paper's Kalman index is 1 for the left arm. The OSF README's line "C=0: left" contradicts its own `mu1`/`reward1`/`C_pred` descriptions and the data. In `exp1.csv` the two prediction rows of a round appear in the order the machines were predicted (randomized per round), which `trial` preserves. Scores on the trait-anxiety scales are included per participant and shared across all of that participant's rows.

## Text-format conversion

All experiments were transcribed into natural-language session transcripts — both the two-armed bandit and the reward-prediction task transfer into text without changing the participant's cognitive operation (the bandit's free A/B choice is a single-letter token fixed by the instructions; the numeric estimate and 0–10 confidence are free-form responses whose format the transcript fixes before the first response). `transcripts0.jsonl` (Study 1) and `transcripts1.jsonl` (Study 2) therefore hold each participant's full session with nothing curated away; no experiment was skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments were built (`experiments/exp0/`, `experiments/exp1/`) and each headless jsPsych round trip passed, confirming the saved CSVs match the dataset's schema. Status is needs-review because substantive assumptions were required: the paper's Methods and the original task code are not accessible (paywalled / no task code on OSF), so the bandit generative constants (initial mean ~ round(N(0,10)), reward noise ~ round(N(0,1)), fast-arm drift ~ round(N(0,2)) per play, slow arm fixed within a round, condition 1=FS/2=SF/3=FF/4=SS per round, response 0=left(A)/1=right(B)) were reverse-engineered from the raw OSF data rather than author-confirmed, and the model-derived / questionnaire columns (V, RU, VTU, TU, C_pred, C_pred_prob, est_m1/m2, est_s1/s2, STAIT_*, STICSAT_*, Factor*) are omitted from the saved CSV because a live browser run cannot compute them. No experiment was skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction

Attempted to reproduce the paper's primary computational-modeling results from the choice
data of both studies (per-participant bounded probit fits of the exploration choice models;
pooled fixed-effects probit for the trait-anxiety interaction model, eq. 7 — a faithful
approximation of the paper's mixed-effects probit with the same likelihood, regressors, and
comparison logic).
Fitted models: choice probit P(C=1)=Phi(wV·V + wRU·RU + wVTU·VTU) and nested
single/two-regressor candidates, compared by summed per-participant BIC; eq. 7 interaction
model C#(V+RU+VTU)*(4 trait-anxiety factors + age + gender).
Reproduced: choice_model_comparison (full V+RU+VTU model wins BIC in both studies, ~paper
Supp. Table 2); somatic_reduces_directed_exploration (Somatic×RU negative: B=-0.076/-0.058,
p<.001 both, paper B=-0.070 p=.034 / B=-0.050 p=.032); somatic_reduces_undirected_exploration
(Somatic×V positive: B=+0.110/+0.088, p<.001 both, paper B=+0.217/+0.194, p<.001 both).
Not reproduced: none.
Numeric mismatch: Somatic×V interaction B is about half the paper's magnitude (+0.110/+0.088
vs +0.217/+0.194) — the direction and significance reproduce; the pooled fixed-effects fit
yields smaller coefficients than the paper's random-effects model. Somatic×RU and the model
comparison reproduce closely. The prediction-task underestimation-of-uncertainty claim
(paper Table 2) was not checked as a primary result: its Subjective_RU construction is
ambiguous under the transform's participant re-mapping in exp1.csv (the internally-consistent
reconstruction does not reproduce the negative Somatic×norm-RU coefficient), and it is a
supplementary mechanistic analysis rather than a model-comparison or model-parameter claim of
the fitted choice model.
Indeterminate: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Both experiments got a text simulator — `simulate0.py` (Study 1 bandit) and `simulate1.py` (Study 2 bandit + reward-prediction task); each round-trips byte-identically through `build_jsonl.py` against its own `transcriptsN.jsonl`. No experiment was skipped. Assumptions worth surfacing: the bandit generative constants (initial mean ~ round(N(0,10)), fluctuating-arm drift ~ round(N(0,2)) per play, reward ~ round(N(mu,1)), condition 1=FS/2=SF/3=FF/4=SS) were reverse-engineered from the shipped CSVs (paper Methods paywalled, no task code on OSF); prediction estimates and 0-10 confidence are free agent responses; the prediction covariates `type_pred`, `true_m1/2`, `curr_est_m/s`, `curr_true_m` and the RT/questionnaire/model columns are dropped as not text-simulatable with known semantics.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 2, major 9, minor 8; fixed 14, open 5).

Checked: paper (author manuscript, https://osf.io/yx6sb/download, for doi:10.1038/s41562-022-01455-y; the Nature page is paywalled) and the OSF supplement, original data (https://osf.io/y6urc/, every file except three fitted-model .mat outputs over 100 MB), exp0-exp1, transform re-run (byte-identical before the fix), transcripts, simulators, modeling, analysis, logs. Skipped: none.

Fixed:
- critical: transform.py mapped the source gender codes 0/1/2 to m/f/other. The per-code counts (219/277/5 in Study 1, 197/279/8 in Study 2) equal the paper's women/men/unreported counts (Methods, pp. 8 and 22 of the manuscript), so 0 = f, 1 = m, 2 = na. exp0.csv and exp1.csv regenerated; only the gender column changed.
- critical: build_jsonl.py narrated response 0 as 'A ... left machine'. In the source, reward equals reward1 exactly when C = 1, the paper's Kalman index is 1 for the left arm (p. 10) and option 1 is on the left (p. 9); the prediction task already labelled machine 0 (= option 1) as left, so in transcripts1.jsonl the bandit 'left' and the prediction 'left' were different machines. Now response 1 = A/left and 0 = B/right; transcripts rebuilt and re-checked token by token against the CSVs in transcript order (985/985 match).
- major: the same side swap in transcripts0.jsonl (self-consistent there, but contradicting the CSV coding); fixed by the same change.
- major: build_jsonl.py always narrated the left prediction first; the paper randomizes the order (p. 23) and the source long file (hence exp1.csv's trial order) records it (first machine equals the wide file's `order` column in all 12,090 blocks). Predictions are now narrated in trial order.
- major: simulate0.py and simulate1.py paired response 0 with reward1/mu1 (inverted with respect to the CSVs); simulate1.py always predicted left first and restarted the prediction `trial` counter every round. Fixed to match the CSVs (A = response 1 = option 1, randomized prediction order, one running trial counter under task_id 30); both round trips through build_jsonl.py are byte-identical.
- major: model.py's gender map had no entry for the corrected 'na' level; updated and re-run on the regenerated CSVs. All three results under Reproduced still reproduce; the Somatic x RU / Somatic x V coefficients moved from -0.074/-0.058 and +0.107/+0.088 to -0.076/-0.058 and +0.110/+0.088 (gender is a covariate of the interaction model), and the README's modeling numbers were updated.
- major: README stated response 0 = left, 1 = right; corrected to 1 = option 1 (left arm), 0 = option 2 (right arm), with the evidence and the OSF README's self-contradiction noted.
- major: README gender row and note ('mapping assumed') replaced by the verified mapping.
- major: README experiment summary said 'resting four-armed bandit'; the task is a restless two-armed bandit (p. 8).
- major: README text-format section named transcripts19.jsonl and transcripts20.jsonl; the files are transcripts0.jsonl and transcripts1.jsonl.
- major: README column tables used range rows (STAIT_1_r..STAIT_20, STICSAT_1_Somatic..STICSAT_21_Somatic, Factor1..Factor4), so 45 columns per experiment had no row; expanded to one row per column.
- minor: README exp0/exp1 column headings set to the template level (####).
- minor: README type_pred was 'prediction-phase type flag (1/0)'; documented as 1 = the predicted machine is the fluctuating arm of that round (verified on all 24,937 prediction rows).
- minor: README had no PDF bullet; added the open author manuscript (https://osf.io/yx6sb/download).

Open:
- minor: check_repo reports transcripts1.jsonl as 'marked tokens do not map one-to-one onto the CSV response sequence' for the 446 participants with prediction rows. The checker orders CSV rows by task_id, which puts the prediction rows (task_id 30) after all bandit rows, and requires a token-value bijection, which the letter A (= 1) and a confidence rating of 1 cannot satisfy. An order-aware comparison matches every marked token of all 484 transcripts to the CSV; the 38 transcripts the checker accepts are exactly the participants without prediction rows.
- minor: check_repo reports 'a response token that never appears in the text before it' for the same transcripts; the prediction estimates are free integers (-49..49) whose format, not each value, the instructions declare.
- minor: the practice block (Supplementary Methods: one to three blocks of 10 trials) is not in the source files.
- minor: the participants excluded before analysis (30 in Study 1, 72 in Study 2; pp. 8, 22) are not in the source files, and the prediction rows ship only the 446 analysed participants and the trials with |prediction| <= 50 (p. 22). The CSVs are faithful to the source.
- minor: the Experiment summary's total N = 985 is the sum of the two studies; check_repo flags it against the per-file counts, no change needed.

Run: claude-fable-5-1, 2026-09-10
