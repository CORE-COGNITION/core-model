---
tags:
- paradigm:behavioral-propensity-rating
- psych-201
- js-experiment:pass
- text-format:pass
- simulator:pass
---
# hussain_2024_novel

- Paper: https://doi.org/10.1140/epjds/s13688-024-00478-x
- Data source: https://osf.io/gu9df/ (gu9df - 'Semantic Accounts of Risk Perception' repository; direct files: https://osf.io/download/bgq38/, https://osf.io/download/hsyr7/)
- PDF: https://epjdatascience.springeropen.com/counter/pdf/10.1140/epjds/s13688-024-00478-x
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Hussain, Z., Mata, R., & Wulff, D. U. (2024). Novel embeddings improve the prediction of risk perception. EPJ Data Science, 13(1). https://doi.org/10.1140/epjds/s13688-024-00478-x

## Experiment summary
This paper introduces the Basel Risk Norms, a large survey dataset of risk-perception judgments for 1004 everyday risk sources (from concreting to nuclear bomb) collected online via Prolific, and compares classical psychometric and distributional-semantic (embedding) models for predicting those ratings. In the risk survey (exp0, N=1506), each participant rated 100 risk sources on a -100 (very safe) to +100 (very risky) continuous slider, producing 150,600 trial-level ratings; attention checks and response-timing metadata were recorded. In the psychometric survey (exp1, N=2360), participants judged a subset of 20 risk sources on nine classic psychometric dimensions (dread, fatal, controllable, known_science, new_old, etc.) on 1-7 Likert scales, producing 424,800 ratings (9 dimensions per item, 20 items). Primary behavioral findings reproduced here: a dominant two-component PCA structure in the psychometric ratings and a strong positive correlation between the dread factor and mean risk-perception ratings (r~.75 vs. the paper's r=.82). The paper's central modeling result—that novel word-association/distributional-semantic embeddings rival or beat classic psychometric predictors in cross-validated elastic-net/gradient-boosting regression of risk ratings—requires the external embedding features and is not assessed from these raw survey data alone.

## Notes

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | P000..P505, anonymized participant identifier (order of appearance in source) |
| trial | 0..99 within each participant, presentation order from Qualtrics block display order columns |
| response | Risk-perception rating on a -100 (very safe) to +100 (very risky) slider, continuous |
| stimulus | Name of the risk source being rated (e.g. 'America', 'grinder', 'nuclear bomb') |
| phase | Always 'test' — the survey has no practice/warmup phase |
| timing_first_click_s | Time in seconds to first click on that item's page element (Qualtrics timing) |
| timing_last_click_s | Time in seconds of last click on that item's page element |
| timing_page_submit_s | Time in seconds when the page containing that item was submitted |
| timing_click_count | Number of clicks on that item's page element |
| attention_check_1 | Response to first attention check ('select -100'), raw value |
| attention_check_2 | Response to second attention check ('select 100'), raw value |
| attention_check_3 | Response to third attention check ('select 0'), raw value |
| counter | Number of questions in the survey (always 100) |
| q_order | Qualtrics QID-based randomization order string encoding which items were shown and in what order |
| counterbalancing | Qualtrics block randomizer display order (e.g. FL_47\|FL_48 or FL_48\|FL_47) |
| status | Qualtrics response status (e.g. APPROVED) |
| started_at | Timestamp when the participant started the survey (ISO 8601) |
| completed_at | Timestamp when the participant completed the survey (ISO 8601) |
| time_taken_s | Total survey duration in seconds |
| completion_code | Prolific completion code (e.g. C1HCT0A3); same for all participants |
| approval_rate | Participant's Prolific approval rate (integer 0-100) |
| age | Age band from Prolific demographic data (e.g. '20s', '30s'); empty if DATA_EXPIRED |
| gender | f / m / na (mapped from Female / Male / Prefer not to say) |
| ethnicity_simplified | Simplified ethnicity category from Prolific (e.g. 'White') |
| country_of_birth | Participant's country of birth |
| country_of_residence | Participant's country of residence |
| nationality | Participant's nationality |
| language | Participant's language (usually 'English') |
| student_status | Whether the participant is a student ('Yes' / 'No') |
| employment_status | Employment status from Prolific (e.g. 'Full-Time', 'Student'); empty if DATA_EXPIRED |
| attention_passed | 1 if the participant passed the attention-check criteria, else 0 |

### exp1
| column | description |
|--------|-------------|
| participant_id | P000..P359, anonymized participant identifier (order of appearance in source) |
| trial | 0..179 within each participant, one per (item, psychometric dimension) pair |
| response | Likert-scale rating (1-7) for the given psychometric dimension; empty if skipped |
| stimulus | Name of the risk source being rated (e.g. 'America', 'grinder') |
| psychometric_dimension | Which psychometric dimension: voluntary_involuntary, fatal, immediate_delayed, dread, chronic_catastrophic, controllable, known_science, known_individuals, new_old |
| block | 0..19, groups the 9 dimension rows belonging to the same item |
| phase | Always 'test' |
| counterbalancing | Qualtrics block randomizer display order |
| status | Qualtrics response status (e.g. APPROVED) |
| started_at | Timestamp when the participant started the survey (ISO 8601) |
| completed_at | Timestamp when the participant completed the survey (ISO 8601) |
| time_taken_s | Total survey duration in seconds |
| completion_code | Prolific completion code (e.g. C1B5G8ZJ); same for all participants |
| approval_rate | Participant's Prolific approval rate (integer 0-100) |
| age | Age band from Prolific demographic data (e.g. '20s', '30s'); empty if DATA_EXPIRED |
| gender | f / m / na (mapped from Female / Male / Prefer not to say) |
| ethnicity_simplified | Simplified ethnicity category from Prolific (e.g. 'White') |
| country_of_birth | Participant's country of birth |
| country_of_residence | Participant's country of residence |
| nationality | Participant's nationality |
| language | Participant's language (usually 'English') |
| student_status | Whether the participant is a student ('Yes' / 'No') |
| employment_status | Employment status from Prolific (e.g. 'Full-Time', 'Student'); empty if DATA_EXPIRED |
| attention_passed | 1 if the participant passed the attention-check criteria, else 0 |

Source data are wide-format Qualtrics exports transformed to long form using the Qualtrics block display-order columns (the Multi-Choice Hack) so that `trial` reflects true item presentation order per participant. The ~57% response rate in exp1 reflects incomplete survey responses in the source (items/dimensions skipped by some participants are left as empty `response` cells). An invented `psychometric_dimension` column (not in the base schema) was added to record which of the nine Likert dimensions a rating belongs to; all original raw columns are carried through. `completion_code`, `age`, and some demographic fields contain identical values across rows because they are survey-level constants.

## Online experiment

Both surveys were re-authored as static jsPsych v8 experiments: `experiments/exp0/` (risk-perception slider, 100 ratings/participant) and `experiments/exp1/` (nine 1–7 psychometric scales, 20 items/participant). The headless jsPsych "data-only" round trip passed for both, confirming the saved CSV matches each `expN.csv` schema (100 and 180 rows; column names, codings, and block/trial structure verified). No experiment was skipped. Browser-only choices are flagged with `ASSUMPTION:` comments in each `index.html`: the slider/Likert pole labels were inferred (the Qualtrics export leaves the scale statements as placeholders), the pseudo-random item draw is a uniform shuffle of the 1004-item pool, the two item-presentation orders were not recovered, and Qualtrics/Prolific survey metadata (status, demographics, `q_order`, `counterbalancing`) is left blank because an anonymous browser participant cannot provide it.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Text-format conversion

Both experiments were transcribed to natural language (`transcripts0.jsonl` from `exp0.csv`, `transcripts1.jsonl` from `exp1.csv`). No experiment was skipped: exp0 (100 continuous -100..+100 risk-perception ratings per participant) and exp1 (nine 1-7 psychometric Likert dimensions per item, 20 items) are both word-stimulus rating tasks, so a text version preserves all task-relevant information. For exp1, the 1/7 pole orientation of each scale is inferred (1 = first-named pole, 7 = second-named pole) and stated in the transcript instructions, as the Qualtrics export left the scale statements as placeholders. Skipped (empty) exp1 ratings are narrated as unanswered. Attention checks in exp0 are participant-level columns carried as metadata fields; no `forced_choice` trials occur.

Sample transcript (exp0, first participant, up to the first response):

```
You are taking a survey about risk perception. In each question you are asked how risky or safe a certain thing or activity is (for example 'nuclear bomb', 'motorbike', or 'gossip'). For each item you move a slider from -100 (very safe) to +100 (very risky). You answer by typing a single number between -100 and +100. The survey also contains a few attention checks that ask you to set the slider to a specific value.
You are asked: how risky or safe is 'hippie'? You rate it [HUMAN_RESPONSE]2[/HUMAN_RESPONSE]. …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Both experiments got a text simulator: `simulate0.py` (risk-perception survey, 100 ratings/participant from the recovered 1004-item pool) and `simulate1.py` (psychometric survey, 9 dimensions x 20 items/participant). Each round-tripped byte-identically through `build_jsonl.py`. ASSUMPTIONS: per-participant item sets are uniform random subsets of the 1004-item pool; exp1 skipped (unanswered) ratings are not simulated (the agent always answers); and response-timing / attention / Prolific-Qualtrics survey-metadata columns are dropped as not text-producible.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25