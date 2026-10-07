---
tags:
- paradigm:self-assessment
- cognitive-modeling:pass
- psych-101
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:pass
---
# jansen_2021_rational

- Paper: https://doi.org/10.1038/s41562-021-01057-0
- Data source: https://osf.io/er9ms/
- Full text: https://www.nature.com/articles/s41562-021-01057-0
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Jansen, R. A., Rafferty, A. N., & Griffiths, T. L. (2021). A rational model of the Dunning–Kruger effect supports insensitivity to evidence in low performers. Nature Human Behaviour, 5(6), 756–763. https://doi.org/10.1038/s41562-021-01057-0

## Experiment summary
Two large online studies replicate a seminal Dunning–Kruger experiment: N = 4083 participants in exp0 (Grammar) and N = 4081 in exp1 (Logical Reasoning / LSAT) each answer 20 five-option multiple-choice questions and, both before and after the test, estimate how many of the 20 they will/did answer correctly (0-20), rate their ability and their performance relative to the other participants (0-100 percentile sliders), and rate the task's difficulty for themselves and for the average participant (1-10), together with two comprehension checks and demographics. The paper fits a rational Bayesian self-assessment model (ability prior plus sensitivity to evidence ε) and shows that comparing model variants supports asymmetric sensitivity to correctness evidence — low performers are less sensitive — over biased priors as the mechanism behind the Dunning–Kruger effect. Response type: one multiple-choice answer per question plus numeric self-ratings (0-20 count, 0-100 percentiles, 1-10 difficulty).

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Qualtrics ResponseId (R_...) from source CSV, unique per participant |
| trial | 0..19 within each participant, question number (Q1→0 ... Q20→19) |
| response | The answer phrase the participant selected for that grammar question (free text of chosen multiple-choice alternative) |
| question | Source question id, Q1..Q20 |
| StartDate / EndDate / RecordedDate | Qualtrics session timestamps |
| Progress | Participant completion progress percent in Qualtrics |
| Duration (in seconds) | Session duration in seconds |
| Finished | Qualtrics completion flag (TRUE/FALSE text) |
| ResponseId | Redundant Qualtrics participant id (same as participant_id) |
| consent | Consent text response |
| attcheck1 / attcheck2 | Attention-check answers (study subject / underlining instruction) |
| attcheck12 / attcheck22 | Second attempt at the two comprehension checks, shown only to participants who failed the first attempt (blank otherwise) |
| grammarAssess0_1 / grammarAssess1_1 | Pre-/post-test percentile rating of one's overall ability to recognize correct grammar relative to the other participants (slider 0-100) |
| absAssess0 / absAssess1 | Pre-/post-test estimate of how many of the 20 questions the participant will/did answer correctly (drop-down 0-20); absAssess1 is the self-assessment the paper analyses |
| relAssess0_1 / relAssess1_1 | Pre-/post-test percentile rating of how well the participant will do/did compared to the other participants (slider 0-100) |
| diffSelf0_1 / diffSelf1_1 | Pre-/post-test rated difficulty of the task for the participant (1 = very easy ... 10 = very difficult) |
| diffOther0_1 / diffOther1_1 | Pre-/post-test rated difficulty of the task for the average participant (1 = very easy ... 10 = very difficult) |
| age | Participant age in years |
| gender | Recoded gender: f / m / other / na (from Man/Woman/Other/Prefer not to say) |
| gender_3_TEXT | Free text for gender "Other" |
| race | Race category text |
| race_6_TEXT | Free text for race "Other" |
| education | Highest education level (free text, e.g. "Some college but no degree") |
| numSemesters | Number of semesters of college completed (0, 1, 2, 3, 4, 5 or more) |
| profession | Reported profession category text |
| nativeEnglish | Native English speaker status text |
| taughtGrammar | Whether participant taught grammar (yes/no) |
| praxisNTE / teacherExam | Whether the participant studied for or took a Praxis teacher test (Yes/No), and free text naming any other teacher exam taken (blank when not applicable) |
| SC0 | Qualtrics score: number of the 20 questions answered correctly (0-20), the paper's 'score' |
| random | Per-participant random integer drawn by a Qualtrics web-service call at survey start and stored as embedded data (its use is not documented in the survey). Not the option-order seed: Qualtrics randomized the option order internally and did not export it; build_jsonl.py uses this value only to seed the transcripts' option lettering |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Qualtrics ResponseId (R_...) from source CSV, unique per participant |
| trial | 0..19 within each participant, question number (Q1→0 ... Q20→19) |
| response | The answer phrase the participant selected for that LSAT logic question (free text of chosen alternative) |
| question | Source question id, Q1..Q20 |
| StartDate / EndDate / RecordedDate | Qualtrics session timestamps |
| Progress | Participant completion progress percent in Qualtrics |
| Duration (in seconds) | Session duration in seconds |
| Finished | Qualtrics completion flag (TRUE/FALSE text) |
| ResponseId | Redundant Qualtrics participant id (same as participant_id) |
| consent | Consent text response |
| attcheck1 / attcheck2 | Attention-check answers (study subject / which-choice instruction) |
| attcheck12 / attcheck22 | Second attempt at the two comprehension checks, shown only to participants who failed the first attempt (blank otherwise) |
| logicAssess0_1 / logicAssess1_1 | Pre-/post-test percentile rating of one's general logical reasoning ability relative to the other participants (slider 0-100) |
| absAssess0 / absAssess1 | Pre-/post-test estimate of how many of the 20 questions the participant will/did answer correctly (drop-down 0-20); absAssess1 is the self-assessment the paper analyses |
| relAssess0_1 / relAssess1_1 | Pre-/post-test percentile rating of how well the participant will do/did compared to the other participants (slider 0-100) |
| diffSelf0_1 / diffSelf1_1 | Pre-/post-test rated difficulty of the task for the participant (1 = very easy ... 10 = very difficult) |
| diffOther0_1 / diffOther1_1 | Pre-/post-test rated difficulty of the task for the average participant (1 = very easy ... 10 = very difficult) |
| age | Participant age in years |
| gender | Recoded gender: f / m / other / na (from Man/Woman/Other/Prefer not to say) |
| gender_3_TEXT | Free text for gender "Other" |
| race | Race category text |
| race_6_TEXT | Free text for race "Other" |
| education | Highest education level (free text) |
| numSemesters | Number of semesters of college completed (0, 1, 2, 3, 4, 5 or more) |
| fluentEnglish | Native English speaker status text |
| profession | Reported profession category text |
| lawSchool | Whether participant attended law school (yes/no) |
| LSAT | Whether participant took the LSAT (yes/no) |
| SC0 | Qualtrics score: number of the 20 questions answered correctly (0-20), the paper's 'score' |
| random | Per-participant random integer drawn by a Qualtrics web-service call at survey start and stored as embedded data (its use is not documented in the survey). Not the option-order seed: Qualtrics randomized the option order internally and did not export it; build_jsonl.py uses this value only to seed the transcripts' option lettering |

The transform used the `_noexclusions` participant files (all participants, including QC-excluded ones); the two Qualtrics metadata header rows were dropped, and participants without a valid ResponseId were dropped. The source files are UTF-8 text that was mis-decoded as cp1252 and re-saved as Mac Roman, so the curly quotes in the logic items arrive as three-byte mojibake; the transform maps those byte triplets back to ’ “ ” before parsing. exp0 = Grammar study, exp1 = Logic/LSAT study, mapping to the paper's Study 1 and Study 2. `response` holds the chosen-answer text; there is no per-question `correct` column. `SC0` is the total number correct, and the per-question answer key is the Qualtrics scoring in the two `.qsf` survey files under `Study Materials` on the OSF project (for every participant SC0 equals the number of responses matching that key).

## Text-format conversion

Both experiments were transcribed (exp0.csv, exp1.csv); none skipped. Each is a 20-item text multiple-choice task (grammar rephrasing / LSAT logical reasoning) with pre- and post-test self-assessment, so it is fully textifiable. Transcripts narrate consent, instructions, comprehension checks, pre/post self-assessment, all 20 items, and demographics; each item lists its 5 options in a participant-seeded shuffled order and marks the chosen letter. An item or rating the participant never answered (drop-outs) is narrated as 'You give no answer.' with no response marker; only the first attempt at each comprehension check is narrated.

Sample transcript (exp0, first response):

```
You are taking part in a study on how people perceive their own abilities. You first read an informed-consent statement and then decide to continue. The task instructions say: 'In this task, you're going to be answering a set of 20 questions about grammar. In each question, some part of each sentence is underlined; sometimes the whole sentence is underlined. Five choices for rephrasing the underlined part follow each sentence; one choice repeats the original, and the other four are different. For each sentence, consider the requirements of standard written English. Your choice should be a correct and effective expression, not awkward or ambiguous. Focus on grammar, sentence structure, punctuation, wordiness, and word choice. If a choice changes the meaning of the original sentence, do not select it.' On every question you press the letter of the option you choose (A, B, C, ...). First you must pass a short comprehension test. Question: 'What subject are you going to be answering questions about?' Options: A) Grammar B) Logical reasoning C) Creative writing You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE]
 …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

Both experiments (exp0 Grammar, exp1 Logical Reasoning/LSAT) got a text simulator (`simulate0.py`, `simulate1.py`). Each generates a full session — consent, instructions, comprehension checks, pre/post self-assessment, and all 20 multiple-choice items — with the option lettering shuffled per participant from the stored `random` seed exactly as `build_jsonl.py` does. Round-trip through `build_jsonl.py` is byte-identical for both.

ASSUMPTIONS (see class docstrings): the article Methods is paywalled, so the session structure is taken from the shipped transcripts/`build_jsonl.py`; no answer key is in the data, so correctness is not modeled — the agent freely picks among the 5 options (format identity, not accuracy, is the contract). Comprehension-check and self-assessment free responses are drawn uniformly over their valid ranges.

Fixed 2026-09-15: simulate0.py and simulate1.py asked the agent before the cue text (` You press [HUMAN_RESPONSE]` / ` Question: ... You answer [HUMAN_RESPONSE]` were appended after the call); the decision-time prompt is now the transcript text up to the open marker (check_calls.py passes).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: rational Bayesian self-assessment model, two variants compared by grid-search SSE and the paper's BIC (Gaussian-error likelihood, k=3 vs k=4): bayesian_inference (mu_theta, eps) vs performance_dependent (mu_theta, eps0, alpha). The paper's MCMC is replaced by exact jitted Gauss-Hermite/trapezoid quadrature over the same likelihood, parameterization, grid, and SSE/BIC logic (documented approximation).
Reproduced: performance_dependent_wins_exp0, performance_dependent_wins_exp1.
Not reproduced: none.
Numeric mismatch: BIC is computed on the full no-exclusions sample (n=3933 exp0, n=3966 exp1), so absolute BIC values differ from the paper's excluded-sample figures (exp0 here 21,805.13 vs 21,767.99; paper 19,303.07 vs 19,274.29. exp1 here 22,333.39 vs 22,280.96; paper 19,846.55 vs 19,797.82). The qualitative comparison — performance-dependent estimation fits better than constant-epsilon Bayesian inference — reproduces in both studies, consistent with the paper's statement that results are substantially the same without exclusions.
Partial validation: none.
Indeterminate: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Static [jsPsych](https://www.jspsych.org) v8 online experiments were added for both studies:
`experiments/exp0/` (Grammar, Study 1) and `experiments/exp1/` (Logical Reasoning / LSAT,
Study 2). Each reproduces the full session — consent, instructions, two comprehension
checks, five pre-test self-assessments, 20 five-option multiple-choice items (option
lettering shuffled per participant from the logged `random` seed), five post-test
self-assessments, and the demographics note — from the simulators' wording. The headless
`?mode=simulate` round trip passed for both (schema columns, 0-indexed `trial` 0..19,
`Q1`..`Q20` `question`, phrase `response`, 20 rows per participant; no outbound requests).
Saved CSV is a drop-in subset of `expN.csv` — the Qualtrics system/metadata columns, the
duplicate attention-check columns, and the demographic/background responses are not
recorded (not produced by the source simulator either); demographics appears only as the
source's narrator line. ASSUMPTIONs: no answer key (correctness is neither modeled nor
shown, as in the simulator); self-assessments are entered on a 0..max slider; consent is
a single "I agree" step; `random` is written as an integer seed.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 5, minor 7; fixed 7, open 5).

Checked: paper (10.1038/s41562-021-01057-0; PDF taken from the authors' code repo github.com/racheljansen/self-assessment, nature.com is paywalled), original data (https://osf.io/er9ms/: Data/GrammarData_noexclusions, Data/LogicData_noexclusions, the two *_deidentified.csv files, Study Materials/*.qsf), exp0-exp1, transform re-run, transcripts, simulators, modeling, analysis, logs. Skipped: none.

Fixed:
- exp1.csv / transform.py: 8,078 response cells carried mojibake (e.g. 'isn\x89Ûªt'). The OSF files are UTF-8 that was mis-decoded as cp1252 and re-saved as Mac Roman; the transform fell back to latin-1. transform.py now maps the three byte triplets back to the curly quotes before parsing; exp1.csv regenerated (only those cells differ, exp0.csv byte-identical). With the fix SC0 equals the number of responses matching the .qsf answer key for all 3,985 exp1 participants (before: 1,311), as it already did for all 3,959 in exp0.
- transcripts0/1.jsonl / build_jsonl.py: the 2,888 (exp0) and 2,201 (exp1) items a participant never answered were marked 'You press [HUMAN_RESPONSE]no option[/HUMAN_RESPONSE]' (124 / 96 drop-outs never reached the items). Now narrated as 'You give no answer.' with no marker, like the unanswered ratings already were. Transcripts rebuilt; every text change is one of the two intended edits.
- build_jsonl.py, simulate0.py, simulate1.py, transcripts: the difficulty prompts said '(0 = very easy, 10 = very difficult)' and the simulators drew 0..10; the survey scale is 1..10 (data minimum 1). Anchors changed to 1 and the simulator range to 1..10; the round trip through build_jsonl.py is byte-identical for both simulators.
- analysis.py: tested the pre-test relative-ability percentile (grammarAssess0_1) as 'self-assessed percent correct' and cited original effect sizes 0.21 / 0.15 / 0.20 as reported by the paper, which reports no such values and analyses only the post-test estimated score (p. 8). Effects rewritten per experiment on absAssess1 vs SC0: mean estimate above mean score (paper 12.49 vs 10.17 and 10.86 vs 9.45; here +2.69 / +1.78), worst score quartile overestimates most (Fig. 5b/6b; here +6.36 / +7.40 gap to the top quartile), quadratic beats linear (paper F = 34.25 / 56.87; here 37.10 / 64.09). All six reproduce.
- README.md column tables (evidence: the .qsf survey files and the data ranges): absAssess is the 0-20 drop-down estimate of the number correct, not 'Likert 1-7'; diffSelf/diffOther are 1-10 task-difficulty ratings for oneself / the average participant, not 'self-vs-other difference ratings (1-7)'; grammarAssess/logicAssess are 0-100 percentile ratings of ability relative to other participants, not 'percent correct'; attcheck12/attcheck22 are the second attempt at the comprehension checks, not duplicate columns; SC0 is the Qualtrics score (number correct), not a 'score counter'; random is a web-service random number, not the option-order seed (Qualtrics randomized the order internally and did not export it); numSemesters is semesters of college; teacherExam is free text. Summary and Notes reworded to match, N stated per experiment, answer-key location corrected (Qualtrics scoring in the .qsf files on OSF).
- README.md: '## Text-format conversion' had no Run line (added from transcripts/auto-exp-transcribe.log: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24); Columns headings use '####'; the section now states how unanswered items and the comprehension-check retries are narrated.
- logs/auto-exp-modeling.sessions.json, logs/auto-exp-sim.sessions.json: the runner's diff snapshot in the first message listed another run's work files (schiekiera_2025_political's README.md, build_jsonl.py, transcripts0.jsonl) and the project queue file modeling_pending.txt naming other datasets. Those diff entries were removed; the sessions themselves are this dataset's and are otherwise unchanged.

Open:
- minor: each transcript marks 32 responses while the CSV has 20 rows per participant: the two comprehension checks and the ten pre/post self-assessments are genuine responses stored as per-participant columns rather than rows (check_repo flags this as major). Every marked value comes from a CSV column, so data and transcripts agree; changing the layout would cascade into every artefact, so it is left as a documented layout choice.
- minor: only the first attempt at each comprehension check is narrated; the second attempt (attcheck12/attcheck22, 483 exp0 and 498 exp1 participants) is omitted from the transcripts and simulators.
- minor: no per-trial `correct` column although the .qsf files hold the answer key; SC0 carries the total (verified equal to the key count for every participant in both experiments).
- minor: the paper (p. 7) counts 3,860 / 3,901 responses before exclusions; the no-exclusions source holds 3,929 / 3,968 finished sessions (4,083 / 4,081 including drop-outs). The deidentified files match the paper's analysed 3,515 / 3,543 exactly, so the data is the paper's.
- minor: the paper (p. 7) describes the difficulty ratings as a 0-10 scale; the survey and the data use 1-10.

Run: claude-fable-5-1, 2026-09-10
