---
tags:
- paradigm:moral-dilemma
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:pass
---

# cheung_2024_large

- Paper: https://osf.io/preprints/psyarxiv/aj46b_v1
- Data source: https://osf.io/3kvjd/
- PDF: https://osf.io/aj46b/download
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Cheung, V., Maier, M., & Lieder, F. (2024). Large Language Models Amplify Human Biases in Moral Decision-Making. PsyArXiv. https://doi.org/10.31234/osf.io/aj46b

## Experiment summary
Participants across 4 studies read moral dilemmas (collective action problems pitting self-interest against the greater good, and sacrificial dilemmas pitting cost-benefit reasoning against deontological rules) and made binary choices or continuous resource allocation decisions. Study 1 (N=294 in exp0) used 22 dilemmas within-subjects and compared human responses to LLMs. Study 2 (N=501 in exp1) tested framing effects on sacrificial dilemmas between-subjects. Study 3 (N=499 in exp2) replicated framing effects on everyday moral dilemmas adapted from Reddit. Study 4 compared LLM model variants; its machine-generated data is excluded here (see Notes). The key research question was whether LLMs amplify human biases (omission bias, inaction bias, framing effects) in moral decision-making.

## Notes

**Study 4 excluded (2026-08-25).** The source repository's Study 4 data (`Exp4_Py`: Centaur / Llama 3.1 model variants answering the dilemmas) is LLM-simulation output with no human participants. Per the collection's human-only contract, its `exp3.csv` was removed from this dataset and `transform.py` no longer builds it. `exp0`–`exp2` (the three human studies) are unchanged.

**Yes/no coding of exp1 and exp2 (2026-09-10).** The Study 2 and 3 answers are yes/no button clicks, not ratings. The source export stores the Qualtrics button codes (1 or 5 = yes, 2 or 6 = no; the code pair differs between questions) and the source analysis scripts recode them (`Exp2/MainPrompts/sacrificialframingGPT.R`, `Exp3/process_data.R`). `transform.py` now applies the same recode, so `response` is 1 = yes, 0 = no as in exp0. The transcripts and simulators answer with Y/N.

**Participants the source excludes flagged (2026-09-10).** `valid` = 0 marks the participants the source analysis scripts drop for a failed attention check (exp0: both `Attn_*` answers must be correct; exp1/exp2: the shown vignette's `*_Attn` must be 1). No rows were removed.

**All-empty columns dropped (2026-08-25).** Columns entirely empty in an expN.csv were removed (Qualtrics export fields never populated): 16 from exp0 (e.g., Country_of_birth, Nationality, Recipient*, Rule_Order, Status_x, U_s__political_affiliation), 12 from exp1 (a subset of the same fields), 9 from exp2 (incl. Birthday_Attn). All were Qualtrics/Prolific metadata fields; no behavioral columns were affected.

### Columns

#### exp0 (Study 1)
| column | description |
|--------|-------------|
| participant_id | Anonymized participant ID (P000–P293) |
| trial | 0-indexed trial number (0–21) |
| response | `moral_dilemma` rows: 1 = yes, 0 = no. `collective_action` rows: the slider value in the dilemma's own units and range (Firm_Donation, Rec_Letter, Whistleblowing: 0–100 %; Language_Course: 0–40 hours; Organizational_Citizenship: 0–20 hours; Lottery_Choice: 0–3000 $; Common_Goods: 0–1000 $; Drought: −100–100 %; Note_Taking: 0–5) |
| dilemma | Dilemma name (e.g., Firm_Donation, Language_Course, Tyran, Lifeboat) |
| dilemma_type | `collective_action` or `moral_dilemma` |
| phase | Always `test` |
| StartDate | Qualtrics survey start timestamp |
| EndDate | Qualtrics survey end timestamp |
| Progress | Qualtrics completion percentage (constant 100) |
| Duration__in_seconds_ | Qualtrics session duration in seconds |
| Finished | Qualtrics finished flag (constant true) |
| RecordedDate | Qualtrics recorded timestamp |
| DistributionChannel | Qualtrics distribution channel (constant `anonymous`) |
| UserLanguage | Qualtrics interface language (constant `EN`) |
| Consent | Consent item (constant: all consented) |
| Q* | Qualtrics page-timing fields, four per vignette page: `Q<id>_First_Click`, `Q<id>_Last_Click`, `Q<id>_Page_Submit` (seconds since page load) and `Q<id>_Click_Count` (clicks); `<id>` is the Qualtrics question id of that page, empty when the page was not shown |
| Attn_Donate, Attn_Tyran | Attention checks (multiple-choice text: what the previous dilemma was about); the source analysis keeps only participants with both correct, see `valid` |
| Instr_Test | Instruction comprehension item (constant: all correct) |
| WW2, ethics, torture, sweatshop, organ, prisoner | Unpopulated multi-select fields of the source export (constant False; carry no information) |
| Status_y | Prolific submission status (APPROVED / AWAITING REVIEW / RETURNED) |
| Custom_study_tncs_accepted_at | Prolific field (constant `Not Applicable`) |
| Started_at | Prolific submission start timestamp |
| Completed_at | Prolific submission completion timestamp |
| Reviewed_at | Prolific review timestamp (empty when not reviewed) |
| Archived_at | Prolific archive timestamp |
| Time_taken | Prolific time taken in seconds |
| Completion_code | Prolific completion code (constant) |
| Total_approvals | Prolific: the participant's total number of approved submissions |
| valid | 1 = both attention checks (`Attn_Donate`, `Attn_Tyran`) answered correctly; 0 = the 9 participants the source analysis excludes |
| age | Participant age in years (Prolific) |
| gender | `f` or `m` (Prolific sex); `na` when not shared |

#### exp1 (Study 2)
| column | description |
|--------|-------------|
| participant_id | Anonymized participant ID (P000–P500) |
| trial | Always 0 (one trial per participant, between-subjects design) |
| response | Yes/no answer to the sacrificial dilemma: 1 = yes, 0 = no (the source stores the Qualtrics button codes 1/5 = yes, 2/6 = no; recoded as in the source analysis scripts) |
| dilemma | Dilemma name (Suicide, Medicine, RAF, Ransom, Vet, Endow) |
| framing | `base`, `yesno`, or `omission` |
| phase | Always `test` |
| StartDate | Qualtrics survey start timestamp |
| EndDate | Qualtrics survey end timestamp |
| Status_x | Qualtrics response type (constant 0 = normal response) |
| Progress | Qualtrics completion percentage (constant 100) |
| Duration__in_seconds_ | Qualtrics session duration in seconds |
| Finished | Qualtrics finished flag (constant true) |
| RecordedDate | Qualtrics recorded timestamp |
| DistributionChannel | Qualtrics distribution channel (constant `anonymous`) |
| UserLanguage | Qualtrics interface language (constant `EN`) |
| Consent | Consent item (constant: all consented) |
| Instr_Test | Instruction comprehension item (constant: all correct) |
| Q* | Qualtrics page-timing fields, four per vignette page: `Q<id>_First_Click`, `Q<id>_Last_Click`, `Q<id>_Page_Submit` (seconds since page load) and `Q<id>_Click_Count` (clicks); `<id>` is the Qualtrics question id of that page, empty when the page was not shown |
| Suicide_Attn, Medicine_Attn, RAF_Attn, Ransom_Attn, Vet_Attn, Endow_Attn | Attention check of the shown vignette (Qualtrics code: 1 = correct, other = wrong; empty for the vignettes not shown); the source analysis keeps only participants with 1, see `valid` |
| WW2, ethics, torture, sweatshop, organ, prisoner | Unpopulated multi-select fields of the source export (constant False; carry no information) |
| Status_y | Prolific submission status (APPROVED / AWAITING REVIEW / RETURNED) |
| Custom_study_tncs_accepted_at | Prolific field (constant `Not Applicable`) |
| Started_at | Prolific submission start timestamp |
| Completed_at | Prolific submission completion timestamp |
| Reviewed_at | Prolific review timestamp (empty when not reviewed) |
| Archived_at | Prolific archive timestamp |
| Time_taken | Prolific time taken in seconds |
| Completion_code | Prolific completion code (constant) |
| Total_approvals | Prolific: the participant's total number of approved submissions |
| Ethnicity_simplified | Prolific self-reported ethnicity (Asian, Black, Mixed, Other, White; DATA_EXPIRED) |
| valid | 1 = the shown vignette's attention check (`*_Attn` = 1) passed; 0 = the 27 participants the source analysis excludes |
| age | Participant age in years (Prolific) |
| gender | `f` or `m` (Prolific sex); `na` when not shared |

#### exp2 (Study 3)
| column | description |
|--------|-------------|
| participant_id | Anonymized participant ID (P000–P498) |
| trial | Always 0 (one trial per participant, between-subjects design) |
| response | Yes/no answer to the everyday dilemma: 1 = yes, 0 = no (the source stores the Qualtrics button codes 1/5 = yes, 2/6 = no; recoded as in the source analysis scripts) |
| dilemma | Dilemma name (FamilyDog, Roommate, Outfit, Pregnant, Christmas, Notetaking) |
| framing | `base`, `yesno`, or `omission` |
| phase | Always `test` |
| StartDate | Qualtrics survey start timestamp |
| EndDate | Qualtrics survey end timestamp |
| Status_x | Qualtrics response type (constant 0 = normal response) |
| Progress | Qualtrics completion percentage (constant 100) |
| Duration__in_seconds_ | Qualtrics session duration in seconds |
| Finished | Qualtrics finished flag (constant true) |
| DistributionChannel | Qualtrics distribution channel (constant `anonymous`) |
| UserLanguage | Qualtrics interface language (constant `EN`) |
| Consent | Consent item (constant: all consented) |
| Instr_Test | Instruction comprehension item (constant: all correct) |
| Q* | Qualtrics page-timing fields, four per vignette page: `Q<id>_First_Click`, `Q<id>_Last_Click`, `Q<id>_Page_Submit` (seconds since page load) and `Q<id>_Click_Count` (clicks); `<id>` is the Qualtrics question id of that page, empty when the page was not shown |
| FamilyDog_Attn, Roommate_Attn, Outfit_Attn, Pregnant_Attn, Christmas_Attn, Notetaking_Attn | Attention check of the shown vignette (Qualtrics code: 1 = correct, other = wrong; empty for the vignettes not shown); the source analysis keeps only participants with 1, see `valid` |
| demo_religion | Qualtrics demographic item: religion, source's numeric code (code mapping not in the source) |
| demog_income | Qualtrics demographic item: income band, source's numeric code (code mapping not in the source) |
| demog_edu | Qualtrics demographic item: education level, source's numeric code (code mapping not in the source) |
| WW2, ethics, torture, sweatshop, organ, prisoner | Unpopulated multi-select fields of the source export (constant False; carry no information) |
| Time_taken | Prolific time taken in seconds |
| Total_approvals | Prolific: the participant's total number of approved submissions |
| Fluent_languages | Prolific self-reported fluent languages (comma-separated) |
| U_s__political_affiliation | Prolific self-reported U.S. political affiliation (Democrat, Independent, Republican) |
| Ethnicity_simplified | Prolific self-reported ethnicity (Asian, Black, Mixed, Other, White; DATA_EXPIRED) |
| valid | 1 = the shown vignette's attention check (`*_Attn` = 1) passed; 0 = the 8 participants the source analysis excludes |
| age | Participant age in years (Prolific) |
| gender | `f` or `m` (Prolific sex); `na` when not shared |

Note: The CSVs hold every participant of the source exports (294, 501, 499). `valid` = 0 marks the participants the source analysis scripts exclude for a failed attention check (9, 27, 8); the remaining `valid` = 1 samples (285, 474, 491) are the final samples of the paper's Methods (pp. 19, 21, 23). The paper's own counts are inconsistent elsewhere: the abstract gives N = 490 and 493 for Studies 2 and 3, the Methods say 11 and 4 exclusions and 497 recruited for Study 3, while the source export holds 499 Study 3 rows.

## Text-format conversion

Transcribed the three human experiments in this dataset (all are textified web surveys): exp0.csv (Study 1, 13 sacrificial + 9 collective-action dilemmas, `transcripts0.jsonl`), exp1.csv (Study 2, sacrificial dilemmas with base/yesno/omission framing, `transcripts1.jsonl`), and exp2.csv (Study 3, everyday AITA dilemmas, `transcripts2.jsonl`). Study 4 (LLM-simulation data) has no human sessions to transcribe; its data was later removed from the dataset entirely (see Notes).

**Sample transcript** (participant P000, exp0, start up to first response):

```text
In this part of the study, you will be shown different everyday scenarios that one might encounter in their lives, and you must make a decision about what to do. Read each scenario carefully and choose what you would do based on the options presented. There are no objectively right or wrong answers; you may choose whichever option you think is best. For each scenario you respond by entering a number on the continuous scale described in the scenario.

In this part of the study, you will be shown different moral scenarios based on historical or realistic situations where some problem occurs, and you must decide what to do. Usually the conflict is between sacrificing the lives of a small number of people (or breaking a moral norm) and saving a larger group of people. Read each scenario carefully and choose what you would do. There are no objectively right or wrong answers; you may choose whichever option you think is best. In every scenario, you (the decision-maker) would not be affected by the decision; only other people would be affected. You answer each question by pressing Y for yes or N for no.

Scenario (Firm_Donation): You are the CEO of a company. This year your company has done quite well, in particular your profit is $100,000 higher than expected. There seems to be two equally valid options: paying a $1,000 bonus to each employee or donating the money to the Against Malaria Foundation, a highly effective and transparent charity which, on average, saves the life of a child every $5000 donated (according to several independent reports). You could also split the money by giving part to your employees and part to the charity. No matter what you choose, your employees won't know what alternative decisions you could have made. What do you do with the $100,000 extra profit? How much do you give to the charity? Please indicate the percentage of extra profit you would donate to the charity, on a continuous scale of 0% being nothing (and give everything as a bonus to each employee), and 100% being donating everything to the highly effective charity. Please answer only with a number between 0 and 100.
You set the slider to [HUMAN_RESPONSE]50[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

`simulate0.py` (Study 1), `simulate1.py` (Study 2) and `simulate2.py` (Study 3) reproduce the transcripts format-identically: the round-trip through `build_jsonl.py` is byte-identical for all three. Study 4 (LLM data, no human participants, since removed from the dataset) is not simulated. Key ASSUMPTIONs: Study 1's dilemma order follows the shipped CSV (fixed, not the paper's randomized order); Study 2/3 assign (dilemma, framing) uniformly over the 18 vignettes and draw the yes/no answer (Y/N) uniformly.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Static jsPsych v8 experiments (see `experiments/README.md`): `experiments/exp0/` (Study 1, 22 trials), `experiments/exp1/` (Study 2, 1 framed dilemma), `experiments/exp2/` (Study 3, 1 everyday dilemma). The headless `?mode=simulate` round trip passed the schema/coding/count checks against `expN.csv`; each session records the core schema columns plus an `rt` field (the text simulator could not record timing). Study 4 (LLM simulation data with no human participant, since removed from the dataset) has no online experiment. ASSUMPTIONs surfaced: browser-only presentation defaults (instruction Continue screens, slider/button response controls, scrollable vignette text); exp0 keeps the CSV's fixed vignette order; the Qualtrics metadata/demographic columns in the raw CSVs are not reproducible by a static run and are omitted; the exp2 `FamilyDog`/`yesno` vignette's lack of a space before "Please answer only..." is reproduced verbatim from the source simulator.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 1, major 5, minor 4; fixed 7, open 4).

Checked: paper (https://doi.org/10.31234/osf.io/aj46b, 56-page PDF from https://osf.io/aj46b/download), original data (https://osf.io/3kvjd, Data&Code/R Exp1-3 archives: Exp1/data_p.csv 294 rows, Exp2/data_p.csv 501 rows, Exp3/dataExp3.csv 499 rows), exp0-exp2, transform re-run (byte-identical to the uploaded CSVs before the fixes below), transcripts (build_jsonl.py rebuild byte-for-byte; every exp0 transcript compared per trial with the CSV), simulators (simulate0-2 run; round trip through build_jsonl.py exact), analysis (analysis.py: 3/3 effects reproduce, also on valid=1 only), logs. No model.py and no cognitive-modeling tag, so no modeling check applies. Skipped: none.

Fixed:
- critical: exp1/exp2 response held the Qualtrics yes/no button codes (1 or 5 = yes, 2 or 6 = no; per dilemma only {1,2} or {5,6} occur) while the README, the transcripts ("you give a rating from 1 to 6") and simulate1/2.py treated it as a Likert 1-6 rating. The source scripts Exp2/MainPrompts/sacrificialframingGPT.R and Exp3/process_data.R recode 1|5 -> yes, 2|6 -> no, and with that map the paper's Study 2 human yes-no figures reproduce (60% vs 56%, p. 9). transform.py now recodes to 1 = yes / 0 = no as in exp0; exp1.csv and exp2.csv regenerated; build_jsonl.py answers Y/N and transcripts1/2.jsonl rebuilt; simulate1/2.py answer Y/N (round trip exact); analysis.py counts response 1 as yes; README columns and Notes updated.
- major: valid was 1 for every row although the source analysis scripts exclude participants for a failed attention check (exp0: Attn_Donate/Attn_Tyran must both be correct, 9 fail; exp1: the shown vignette's *_Attn must be 1, 27 fail; exp2: 8 fail). The remaining 285/474/491 equal the paper's final samples (pp. 19, 21, 23). transform.py now sets valid = 0 for them; no rows removed; exp0-2.csv and transcripts0-2.jsonl regenerated.
- major: the README Columns tables used a '*Qualtrics metadata*' placeholder and left about 110-130 columns per experiment undocumented; replaced by one row per column (group rows for the Q<id> page-timing fields, the six constant-False fields and the attention checks).
- major: README described the exp0 collective-action response as 'continuous 0-100'; the slider range differs per dilemma (0-100 %, 0-40 h, 0-20 h, 0-3000 $, 0-1000 $, -100..100 %, 0-5; source socialdilemmas.csv and vignettes_social.pdf). Row rewritten.
- major: transcripts1/2.jsonl used response tokens (5, 6) never declared in the text (197/501 and 239/499 transcripts); resolved by the Y/N fix.
- major: the README sample-size note said the paper reports 285/490/493 and that no exclusion criteria were applied; rewritten around the valid flag and the paper's Methods counts.
- minor: analysis.py docstring cited the paper under a wrong title; corrected.

Open:
- minor: the paper is inconsistent with itself: Study 2 abstract N = 490 vs Methods N = 474 and 'excluded 11' (501 - 27 = 474 under the source's rule); Study 3 'recruited 497, excluded 4, N = 491' vs 499 export rows, 8 fail, 491 pass. The data is faithful to the source; the README note states this.
- minor: the paper (p. 20) randomized the vignette order and counterbalanced the order of the two dilemma types in Study 1; the Qualtrics export records no presentation order, so exp0 trial 0-21 follows the export's fixed column order (already stated in the README Simulators section).
- minor: exp1/exp2 keep the Prolific and Qualtrics demographics under their source names (Ethnicity_simplified, demog_edu, demog_income, demo_religion, U_s__political_affiliation) instead of the schema's ethnicity/education/income, and the source gives no code mapping for demog_*.
- note (not a defect): check_repo.py reports for transcripts0.jsonl that the marked tokens do not map one-to-one onto the CSV (196/294) and that a token is not declared beforehand (294/294). Both are artifacts of one session mixing Y/N moral-dilemma answers (CSV 1/0) with slider answers that can also be 0 or 1, and of continuous slider values that cannot be enumerated; every exp0 transcript was compared per trial with the CSV (294/294 equal; Y = 1, N = 0, slider numbers verbatim, dilemma order equal).

Run: claude-fable-5-1, 2026-09-09
