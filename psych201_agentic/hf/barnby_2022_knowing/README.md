---
tags:
- paradigm:belief-updating
- cognitive-modeling:pass
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:pass
---
# barnby_2022_knowing

- Paper: https://doi.org/10.1016/j.cognition.2022.105098
- Data source: https://github.com/josephmbarnby/Barnby_etal_2021_SVO
- PDF: https://osf.io/download/j74c6/
- Full text: https://osf.io/preprints/psyarxiv/an5kp_v1/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Barnby, J. M., Raihani, N., & Dayan, P. (2022). Knowing me, knowing you: Interpersonal similarity improves predictive accuracy and reduces attributions of harmful intent. Cognition, 225, 105098. https://doi.org/10.1016/j.cognition.2022.105098

## Experiment summary
Single online social-value-orientation (SVO) experiment with N = 697 Prolific participants across two phases. In Phase 1 (decider), participants made 18 choices between payoff allocations labelled prosocial/individualist/competitive; in Phase 2 (recipient), they predicted which of two options a partner would choose over 36 trials with correctness feedback, then rated the partner's harmful intent (HI) and self-interest (SI) and completed paranoia (R-GPTS) and cognitive-ability (ICAR) questionnaires. The research question is how people integrate priors about others into Bayesian belief updating about a partner's social preferences, whether one's own SVO shapes these priors, and whether participant-partner preference alignment improves prediction accuracy and reduces attributions of harmful intent. Responses are 1/2 option choices in both phases.

## Notes

### Columns
| column | description |
|--------|-------------|
| participant_id | Original subject id (1..697) from the source CSVs `Intentions_Phase1.csv` / `Intentions_Phase2.csv` |
| trial | 0..53 within each participant, continuous across the session; decider phase = trials 0-17, recipient phase = trials 18-53 (matches the paper's combined `Intentions_BothPhase.csv` trial numbering 1-54) |
| phase | Session phase: `decider` (Phase 1, 18 SVO choice trials) or `recipient` (Phase 2, 36 partner-prediction trials) |
| condition | Assigned partner SVO type as coded in source `PartnerPolicy`: `Prosocial`, `Individualist`, `Competative` (source's own spelling of competitive) |
| rt | Response/reaction time in ms (source `Intentions_RT`) |
| game | Stage label: `Choose` (decider phase) or `Guess` (recipient phase) |
| trial_source | Original per-phase trial number from the source (1..18 decider, 1..36 recipient) |
| agency | Rating of how much participant believed their partner was a real person (0-100, source `Agency`) |
| control | Task-comprehension control-question score per phase (0/1, source `Control`); summed across phases in the paper's analysis |
| age | Participant age in years |
| gender | Participant sex recoded from source `Sex` (`Female`->`f`, `Male`->`m`, `Non-Binary`->`nb`) |
| education | Highest education level, verbatim source `Education` category string |
| ethnicity | Ethnicity category string from source `Ethnicity` (UK census categories) |
| religion | Self-reported religion string from source `Religion` |
| persec | R-GPTS persecution subscale total (source `Persec`) |
| socref | R-GPTS social reference subscale total (source `SocRef`) |
| iq | ICAR matrix total correct (0-10, source `ICARTot`) |
| icar_rt | ICAR response time in ms (source `ICARrt`) |
| response | Which of the two presented options the participant chose (decider phase) or predicted the partner would choose (recipient phase): `1` = Option 1, `2` = Option 2 (source coding; see README `PPT Choice/Prediction`) |
| option1_ppt | Points to the participant if Option 1 is selected (source `Option1_PPT`) |
| option1_partner | Points to the partner if Option 1 is selected (source `Option1_Partner`) |
| option2_ppt | Points to the participant if Option 2 is selected (source `Option2_PPT`) |
| option2_partner | Points to the partner if Option 2 is selected (source `Option2_Partner`) |
| type1 | SVO category label of Option 1 (Prosocial / Individual / Competative) |
| type2 | SVO category label of Option 2 (Prosocial / Individual / Competative/Competitive) |
| diff1 | Source `Diff1` as shipped: the self-minus-other payoff difference of one option of the pair. It equals `option1_ppt - option1_partner` on 27 of the 54 option pairs and is swapped with `diff2` on the other 27 (source coding quirk; recompute from the option columns if needed) |
| diff2 | Source `Diff2` as shipped: the self-minus-other payoff difference of the other option of the pair (see `diff1`; equals `option2_ppt - option2_partner` on 27 of the 54 pairs, swapped on the other 27) |
| choice | SVO label of the option actually chosen in the decider phase (Phase 1 only, source `Choice`); NaN in recipient phase |
| choice_action | Categorical code of the chosen SVO in the decider phase: 1=Prosocial, 2=Individual, 3=Competative (source `ChoiceAction`); NaN in recipient phase |
| answer | Partner's actual choice on that trial in the recipient phase (`1`=Option 1, `2`=Option 2, source `Answer`); NaN in decider phase |
| guess | SVO label the participant predicted the partner would choose in the recipient phase (source `Guess`); NaN in decider phase |
| guess_action | Categorical code of the predicted SVO in the recipient phase: 1=Prosocial, 2=Individual, 3=Competative (source `GuessAction`); NaN in decider phase |
| correct | Whether the participant's prediction matched the partner's actual choice (0/1, source `Correct`); NaN in decider phase. On 5 rows (the first recipient trial of participants 233, 350, 386, 557, 659) the source has 0 although `response` equals `answer` |
| incorrect | Complement of `correct` (0/1, source `Incorrect`); NaN in decider phase |
| hi | Post-phase-2 rating of the partner's harmful intent (0-100 slider, source `HI`) |
| si | Post-phase-2 rating of the partner's self-interest (0-100 slider, source `SI`) |
| final_guess | Post-phase-2 3-option forced choice about the partner's motive (verbatim source `Final_Guess`; participant 555 has the unanswered placeholder `Please select an option`) |
| cumulative_cor | Running count of correct predictions so far in the recipient phase (source `CumulativeCor`) |
| propab | Source `Propab`: `cumulative_cor` / 32 on every row (a fixed-denominator running accuracy, not a proportion of any option type) |
| proprel | Source `Proprel`: `cumulative_cor` / `trial_source` on every row, i.e. the running proportion of correct predictions so far |
| sum | Total number of correct predictions over the 36 recipient trials (source `Sum`; constant per participant) |
| percentage_cor | Source `PercentageCor`: `sum` / 32 (constant per participant; the source divides by 32, not 36, so values can exceed 1) |

### Notes on transforms
Both phases were merged per participant into a single `exp0.csv` with continuous 0-53 trial numbering (`phase` distinguishes decider vs recipient). All 42 source columns were carried through, renamed to schema conventions where one applies (e.g. `Age`->`age`, `Sex`->`gender`, `Intentions_RT`->`rt`, `ICARTot`->`iq`). No platform IDs were present (subject ids are 1-697), so participant IDs were kept as-is. `response` retains the source 1/2 option coding for both phases.

## Text-format conversion

Transcribed `exp0.csv` (all 697 participants): both phases are textifiable. Phase 1 is an 18-trial SVO task where the participant chooses between two point allocations (Option 1 / Option 2, each giving points to self and partner). Phase 2 is a 36-trial task where the participant predicts which option their partner chose, receives correct/incorrect feedback, then rates the partner's harmful intent (HI) and self-interest (SI) on 0-100 sliders and answers a 3-option forced choice about the partner's motive. No experiments were skipped.

**Sample transcript** (participant 1, through the first response):
```
You are taking part in an online economic decision-making study. You have been matched with two anonymous partners, one for each phase of the study. The points you earn are pooled over a series of tasks and contribute to an overall total that enters a financial lottery.

PHASE 1 - DECIDER. You are the decider. On each of 18 trials you see two options that each allocate points to you and your partner, and you choose the option you prefer. The options are shown as Option 1 and Option 2. Press A to select Option 1, or press B to select Option 2.

Trial 1. Option 1 (You: 8, Partner: 8); Option 2 (You: 10, Partner: 5). You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

`simulate0.py` simulates exp0 (both phases) and passes the round-trip check against `build_jsonl.py`. The partner's choices are fixed per option pair and partner type, taken from the source's Task Specifications files, which match the `answer` column of `exp0.csv` on every item (the paper's verbal rule for the individualist partner does not hold on 5 of the 36 pairs). Item order is randomized per participant per the paper.

Fixed 2026-09-15: simulate0.py offered the raw final-guess strings as options but wrote the canonical labels; the options are now the labels the transcript uses.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`experiments/exp0/` ports `simulate0.py` (the full two-phase SVO task: 18 decider choices, 36 recipient predictions with Correct/Incorrect feedback, two 0-100 slider ratings and a 3-option forced choice) to a static jsPsych v8 experiment. The headless `?mode=simulate` round trip passed: it emits one CSV matching `exp0.csv`'s 42-column schema (54 rows per participant, `trial` 0..53, `response` 1/2, `trial_source` 1..18 / 1..36) and reproduces the simulator's shuffled item sets and deterministic partner SVO rule exactly. `rt` (browser), the per-item `type1`/`type2`, `choice`/`choice_action`, `guess`/`guess_action`, the running `cumulative_cor` and the ratings are filled; the source's analysis-time running summaries (`propab`, `proprel`, `sum`, `percentage_cor`), the source-only ratings (`agency`, `control`) and demographics/questionnaires the task does not collect (`age`, `gender`, `education`, `ethnicity`, `religion`, `persec`, `socref`, `iq`, `icar_rt`) stay blank, exactly as in `simulate0.py`. Cosmetic browser defaults (feedback ~1000 ms, ~300 ms gaps, option colors/layout, slider value shown before first click) are documented in `experiments/README.md`. No experiments were skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: Model 1 (beta-only Bayesian updating), Model 2 (full 4-parameter Bayesian updating, the paper's winner), Model 3 (participant ignores the partner), Model 11 (Q-learning heuristic); per-participant bounded-L-BFGS MAP with the paper's hierarchical prior (N(0, 7.5) on raw params), compared on summed BIC as a faithful approximation of the paper's hierarchical CBM responsibility comparison.
Reproduced: Model 2 wins the comparison (summed BIC 29933 vs 35655 beta-only, 37215 ignores-partner, 60223 Q-learning); alpha_ppt > -beta_ppt, mean alpha_ppt + beta_ppt = 3.77, t-test p < 0.05 (paper reports 5.05).
Not reproduced: none.
Numeric mismatch: alpha_ppt + beta_ppt = 3.77 here vs 5.05 reported (paper: alpha 11.13, beta -6.08); the MAP prior and the coarser belief grid (0.5-step vs 0.125/0.25) shrink parameter magnitudes while preserving both qualitative directions.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 6, minor 5; fixed 9, open 2).

Checked: paper (10.1016/j.cognition.2022.105098, preprint PDF), original data (https://github.com/josephmbarnby/Barnby_etal_2021_SVO), exp0, transform re-run (byte-identical), transcripts (rebuilt byte-identical), simulator (smoke test and round trip), modeling (full run), analysis, logs. Skipped: none.

Fixed:
- simulate0.py: the individualist partner rule (max own payoff, else the more equal option) disagreed with the source's Task Specifications on 5 of the 36 option pairs (1162 of 8388 individualist rows). Replaced by a per-item lookup table taken from the source's ProsocialPartner/IndividualistPartner/CompetitivePartner.csv, which matches the `answer` column of exp0.csv on all 108 partner-type x item cells; round trip through build_jsonl.py re-verified; README Simulators note updated.
- README: `diff1`/`diff2` were described as the per-option self-minus-other differences; they equal that on 27 of the 54 option pairs and are swapped between the two options on the other 27 (source Diff1/Diff2 quirk, also in the spec files). Descriptions corrected.
- README: `propab` was described as a running proportion of absolute-payoff-maximising predictions; it equals `cumulative_cor`/32 on every row. Description corrected.
- README: `proprel` was described as a running proportion of relative-payoff-maximising predictions; it equals `cumulative_cor`/`trial_source` on every row. Description corrected.
- README: `sum` was described as cumulative; it is the per-participant total of correct predictions (constant per participant). Description corrected.
- README: `percentage_cor` was described as the percentage of correct predictions; it is `sum`/32 (values up to 1.125). Description corrected.
- README: noted on `correct` that 5 rows (first recipient trial of participants 233, 350, 386, 557, 659) carry 0 although response equals answer; identical in the raw Intentions_Phase2.csv, so the data is faithful.
- README: noted on `final_guess` that participant 555 has the unanswered placeholder `Please select an option` (as in the raw file).
- README: Experiment summary now states N = 697.

Open:
- minor: check_repo counts 57 marked responses per transcript against 54 CSV rows; the 3 extra are the post-task harmful-intent, self-interest and final-guess responses, which exp0.csv stores as the per-participant columns `hi`, `si`, `final_guess` (as the source does). README, build_jsonl.py and simulate0.py agree; left as is.
- minor: documented schema deviations kept as in the source: `response` coded 1/2 (schema: 0/1), `condition` labels Prosocial/Individualist/Competative (not snake_case), `education` as the verbatim source string. Every generated file uses this coding.

Run: claude-fable-5-1, 2026-09-09
