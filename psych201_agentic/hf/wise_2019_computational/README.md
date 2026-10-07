---
tags:
- paradigm:aversive-reversal-learning
- cognitive-modeling:pass
- psych-101
- text-format:pass
- js-experiment:pass
- simulator:pass
---

# wise_2019_computational

- Paper: https://doi.org/10.1371/journal.pcbi.1007341
- Data source: https://osf.io/b4e72/
- PDF: https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1007341&type=printable
- Full text: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007341
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Wise, T., Michely, J., Dayan, P., & Dolan, R. J. (2019). A computational account of threat-related attentional bias. PLoS Computational Biology, 15(10), e1007341. https://doi.org/10.1371/journal.pcbi.1007341

## Experiment summary
One aversive reversal-learning task (65 recruited, 61 in the uploaded trial-level data): on each of 4 blocks of 40 trials, two fractal stimuli are shown with a decaying/evolving shock-outcome probability, and participants rate each stimulus's probability of an upcoming electric shock on a 0-1 slider, then observe the shock/no-shock outcome separately per stimulus. Across blocks the shock probabilities change (reversal learning), and a valid shock can be delivered seconds after the outcome. The paper asks whether visual attention is driven by aversive value versus uncertainty and whether attention in turn biases threat learning, testing this by fitting 5 hierarchical computational models (Rescorla-Wagner and variants) to the trial-by-trial shock-probability ratings. The primary behavioral effects (threat overestimation and asymmetric learning from shock) reproduce on these CSVs.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (zero-padded 2-digit string, e.g. "00"). |
| task_id | 0-indexed task block (source `run` 0-3); each of the 4 blocks is a fresh learning task with new stimuli and shock-probability sequence. |
| trial | 0..N response counter within each (participant_id, task_id); each paper-trial contributes two responses (stimulus A and B), so trial advances by 2 per paper-trial. |
| block | 0-indexed paper-trial index within each task; groups the two response rows (A, B) that belong to the same source trial. |
| stimulus | Which stimulus the row's response refers to: "A" or "B". |
| response | Participant's slider rating of shock probability (0-1) for that stimulus on that trial (continuous rating). |
| shock | Delivered shock outcome for that stimulus on that trial: 0 = no shock, 1 = shock, NaN = not recorded (probe marker rows). |
| shocked | Mirror of source `A_shocked`/`B_shocked`; identical to `shock` on real trials, differs only on probe marker rows. |
| shock_prob | True generative shock probability for that stimulus on that trial (0-1). |
| error | Prediction error for that stimulus = source `A_error`/`B_error` (= shock_prob - response). |
| trial_number | Original 1-based trial counter from source (1-160); value 999 marks probe/shock-delivery marker rows. |
| run | Original source run/block index (0-3), kept verbatim. |
| shock_level | Per-participant calibrated shock intensity level recorded on every row (e.g. 95, 141, 195). |
| Choice_image_L | Stimulus identity ("A" or "B") shown on the left during the choice/rating phase. |
| Choice_image_R | Stimulus identity ("A" or "B") shown on the right during the choice/rating phase. |
| Outcome_image_L | Stimulus identity ("A" or "B") shown on the left during the outcome phase. |
| Outcome_image_R | Stimulus identity ("A" or "B") shown on the right during the outcome phase. |
| phase | "test" for real rating trials; "probe" for trial_number==999 marker rows (non-rating shock-delivery markers). |
| age | Participant age in years from questionnaire_data (NaN if questionnaire missing). |
| gender | Participant sex coded f/m from questionnaire `Sex_0` (1=female, 0=male); NaN if questionnaire missing. |

Each source "paper-trial" split into two response rows (stimulus A and B), grouped by `block`. The eye-tracking data (gaze/fixation bias) was excluded from the uploaded dataset because it exceeded the size cap; the headline eye-tracking effects are therefore not testable from these CSVs, but the ratings/outcome behavioral effects are. The `simulated_data/` files contain model-predicted parameter distributions (not human responses) and were excluded. Subject IDs 12 and 26 are absent from the source (excluded/not analyzed).

## Text-format conversion

`exp0.csv` was transcribed to `transcripts0.jsonl` (61 transcripts, one per participant): the 0–1 per-stimulus shock-probability ratings are free responses, the square/circle shock outcomes are narrated, and the shock-delivery probe rows are included as plain text. No experiments were skipped; the eye-tracking data is absent from the upstream CSVs so nothing else was textifiable.

Sample transcript (instructions through the first rating):

```
You are taking part in an aversive learning task. In each of four blocks you see two fractal stimuli, one on the left and one on the right. Each stimulus has its own chance of delivering an electric shock, and these probabilities change over time and across blocks. Your job is to keep track of these probabilities and report them accurately.
On each trial you rate how likely each stimulus is to deliver a shock by moving a slider from 0 (definitely no shock) to 1 (definitely a shock). Type your rating as a number between 0 and 1 (for example 0.5 means a 50% chance). Then you see the outcome for each stimulus: a square around a stimulus means it delivered a shock, a circle means it did not. You should update your ratings as the probabilities change.

A new block begins. The shock probabilities have changed; disregard what you learned in the previous block.
You rate the chance that stimulus A on the left shocks you: [HUMAN_RESPONSE]0.5[/HUMAN_RESPONSE]
 ```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`experiments/exp0/` is a static jsPsych v8 port of the aversive reversal-learning task (4 blocks x 40 trials; on each trial two stimuli are rated on two 0-1 sliders, then the square/circle outcomes and the shock delivery are shown). The headless `?mode=simulate` round trip passed: the saved CSV matches `exp0.csv`'s schema exactly (all 20 columns, two rows per trial grouped by `block`, `trial` restarting per `task_id`, end-of-block probe rows on blocks 0-2). Browser-only `ASSUMPTION`s: no physical shock is delivered (the outcome is shown as the paper's square/circle plus a lightning icon), and `shock_level`/`age`/`gender` are left blank (no shock-calibration or in-session questionnaire phase); fractal art is replaced by coloured A/B shapes.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

`simulate0.py` simulates the aversive reversal-learning task (4 blocks x 40 trials, two rated stimuli per trial, square/circle shock outcomes narrated, shock-delivery probe rows after blocks 0-2). The rating (0-1) is the free response; shock probabilities follow a per-block changepoint random walk on the empirical value set (hazard 0.1, mean ~0.36). The round-trip check through `build_jsonl.py` passed byte-identical. `ASSUMPTION`: the paper does not specify the exact probability-generating rule or which stimulus per block is the variable one, so both are drawn independently from the changepoint process; the probe rows appear only after blocks 0-2, matching `exp0.csv`. `age`/`gender`/`shock_level` are not produced (per-subject metadata).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction

Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: M1 RW single alpha, M2 RW dual alpha+/-, M3/M4 Pearce-Hall/RW hybrids, M5 symmetric leaky beta, M6 asymmetric leaky beta (all with cross-stimulus omega); per-participant MLE by bounded L-BFGS, compared by summed AIC/BIC as a point-estimate proxy for the paper's hierarchical WAIC; Gaussian observation of the 0-1 ratings with fixed SD (common across models, so it cancels out of comparisons).
Reproduced: model_comparison_best (M6 asymmetric leaky beta is the best-fitting model: AIC 5398.6 vs M2 8630.0, BIC 6148.9 vs 9192.8, n=61); asymmetric_tau_gt_tau_minus (paired t(60)=5.34, p<0.001, paper: t(47)=7.09).
Not reproduced: none.
Numeric mismatch: paper compares by hierarchical WAIC from MCMC (M6 best); here per-participant MLE summed AIC/BIC give the same M6 winner, and the reported t differs (5.34 vs 7.09) because the paper excluded 14 subjects and used hierarchical posteriors; sign and significance match.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25