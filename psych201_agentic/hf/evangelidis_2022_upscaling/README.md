---
tags:
- paradigm:decoy-effect
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:needs-review
---
# evangelidis_2022_upscaling

- Paper: https://doi.org/10.1093/jcr/ucac059
- Data source: https://researchbox.org/55
- PDF: https://merit.url.edu/ws/portalfiles/portal/46734000/The_Upscaling_Effect.pdf
- Full text: https://academic.oup.com/jcr/article/50/3/492/6935792
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Evangelidis, I., Levav, J., & Simonson, I. (2022). The upscaling effect: How the decision context influences tradeoffs between desirability and feasibility. Journal of Consumer Research, 50(3), 492-509. https://doi.org/10.1093/jcr/ucac059

## Experiment summary
Participants choose between a high-desirability (HD) and a high-feasibility (HF) option across varied consumer stimuli (backpacks, speakers, hard drives, hotels, TVs). Some choice sets add a symmetrically dominated decoy (C) and/or a "search for other options" no-choice option; the key manipulation is presence/absence of the decoy, which increases HD choice share — the upscaling effect. Public trial-level data cover Studies 1–7 plus a Study 5 follow-up: Study 1 (N=2014, one choice/participant), Study 2 (N=506, within-subject two choices), Study 3 (N=809, hotel + free-text explanations), Study 4 (N=1609, speaker + justification measures), Study 5 (N=2016, hard drive, HD-price manipulation), Study 5 Follow-up (N=302, justifiability ratings), Study 6 (N=2018, decoy placement), Study 7 (N=805, same/different page presentation). Response is discrete choice between the alternatives; Study 5 Follow-up uses a 1–7 justifiability rating. The paper reports 19 studies total; only studies 1–7 and the Study 5 follow-up publish public trial-level data.

## Notes

### Columns

#### exp0 (Study 1)
| column | description |
|--------|-------------|
| participant_id | P000..P2013 in first-appearance (source row) order |
| trial | 0 for every participant (single between-subject choice) |
| condition | two_options (no decoy) or three_options (decoy C added) |
| stimulus | product category: backpack, speaker, harddrive, hotel, tv |
| n_options | number of response alternatives including the no-choice slot: 3 (two products + search) or 4 (three products + search) |
| choice_set | JSON list of option slots for that choice set |
| response | 0-indexed chosen alternative; last index = no-choice (deferral) |
| deferral | 0/1, 1 = chose "search for other options" |
| code | raw source response code (Qualtrics) for that column |
| age | participant age in years (self-report) |
| gender | f / m (1=Female, 2=Male in source) |

#### exp1 (Study 2)
| column | description |
|--------|-------------|
| participant_id | P000..P505 |
| trial | 0 = first (two-option) choice, 1 = second (three-option) choice |
| condition | two_options (trial 0) or three_options (trial 1) |
| n_options | number of response alternatives including the no-choice slot (3 or 4) |
| choice_set | JSON list of option slots |
| response | 0-indexed chosen alternative (last slot = no-choice) |
| deferral | 0/1 no-choice flag |
| Liking_1 / Liking_2 | rating (1..20 slider) of liking brand A / brand B |
| BeliefsDom | which option is clearly better than decoy C: 1=A, 2=B, 3=both A and B |
| SelfConstrual_1..10 | 7-pt Likert self-construal scale (Singelis 1994), filler task |
| age | years |
| gender | f / m / nb (1=Female,2=Male,3=Non-Binary) |

#### exp2 (Study 3)
| column | description |
|--------|-------------|
| participant_id | P000..P808 |
| trial | 0 |
| condition | two_options / three_options |
| version | counterbalancing of A/B labels: v1 (A=$89 3-star HF), v2 (A=$119 4-star HD) |
| n_options | number of response alternatives including the no-choice slot (3 or 4) |
| choice_set | JSON list of option slots |
| response | 0-indexed chosen alternative (last slot = no-choice) |
| deferral | 0/1 no-choice flag |
| explanation | free-text explanation of the participant's reasons (before choosing) |
| SimilarPriceBetterRating | rater-coded dummy: invoked reason "higher quality same price as decoy" (0/1) |
| SimilarRatingLowerPrice | rater-coded dummy: invoked reason "same quality lower price than decoy" (0/1) |
| Justifiability | rater-coded dummy: found it hard to justify paying more for HD (0/1) |
| age | years |
| gender | f / m / nb |

#### exp3 (Study 4)
| column | description |
|--------|-------------|
| participant_id | P000..P1608 |
| trial | 0 |
| condition | two_options / three_options |
| version | counterbalancing v1 / v2 of A/B labels |
| n_options | number of response alternatives including the no-choice slot (3 or 4) |
| choice_set | JSON option slots |
| response | 0-indexed chosen alternative (last slot = no-choice) |
| deferral | 0/1 no-choice flag |
| JustifA / JustifB | 7-pt "how easy to justify choosing A / B" (1=not at all easy .. 7=very easy) |
| ExplA / ExplB | free-text justification for choosing A / B |
| justif_before_choice | 0/1, 1 = justifications required before (vs after) the choice |
| age | years |
| gender | f / m / nb / other |

#### exp4 (Study 5)
| column | description |
|--------|-------------|
| participant_id | P000..P2015 |
| trial | 0 |
| condition | two_options / three_options |
| version | counterbalancing v1 / v2 of A/B labels |
| hd_price | HD option price level: high ($79.99) or low ($42.99) |
| n_options | number of response alternatives including the no-choice slot (3 or 4) |
| choice_set | JSON option slots |
| response | 0-indexed chosen alternative (last slot = no-choice) |
| deferral | 0/1 no-choice flag |
| age | years |
| gender | f / m / nb |

#### exp5 (Study 5 Follow-up)
| column | description |
|--------|-------------|
| participant_id | P000..P301 |
| trial | 0 = justifiability of option A, 1 = justifiability of option B |
| block | same as trial (0 for A, 1 for B) |
| option | A or B, which option was rated |
| version | counterbalancing v1 / v2 of A/B labels |
| hd_price | HD option price level: high / low |
| response | 7-pt justifiability rating (1=not at all easy .. 7=very easy) |
| age | years |
| gender | f / m / nb |

#### exp6 (Study 6)
| column | description |
|--------|-------------|
| participant_id | P000..P2017 |
| trial | 0 |
| condition | two_options / three_options |
| stimulus | product category: backpack, harddrive, hotel, speaker, tv |
| decoy_loc | decoy placement: next_to_hd or next_to_hf |
| n_options | number of response alternatives including the no-choice slot (3 or 4) |
| choice_set | JSON option slots |
| response | 0-indexed chosen alternative (last slot = no-choice) |
| deferral | 0/1 no-choice flag |
| age | years |
| gender | f / m |

#### exp7 (Study 7)
| column | description |
|--------|-------------|
| participant_id | P000..P804 |
| trial | 0 |
| condition | two_options / three_options |
| presentation | options shown on same page ("same") or different pages ("different") |
| n_options | number of response alternatives including the no-choice slot (3 or 4) |
| choice_set | JSON option slots |
| response | 0-indexed chosen alternative (last slot = no-choice) |
| deferral | 0/1 no-choice flag |
| age | years |
| gender | f / m / nb |

### Mapping
exp0–exp7 map to the paper's Studies 1, 2, 3, 4, 5, 5-Follow-up, 6, and 7, respectively. `response` is coded as a 0-indexed position among the alternatives as displayed (0=A, 1=B, 2=decoy C in 3-option sets), with the last index being the "search for other options" no-choice; when `deferral`=1 the participant chose the no-choice option. The paper reports 19 studies; only these studies publish accessible public trial-level data, so the remaining studies are not represented here.

## Text-format conversion

All 8 experiments (exp0–exp7, Studies 1–7 + Study 5 follow-up) were transcribed: each is a consumer choice (or a justifiability rating in exp5) between text-described HD/HF alternatives, sometimes with a dominated decoy — fully expressible in language, so nothing was skipped. Responses are single letters (A/B/C) for choice, `S` for the "search for other options" deferral, and numerals for ratings/Likert/free text is verbatim.

Sample transcript (Study 1, exp0, first response):

```
Suppose you consider buying a new TV. You pass by an electronics store that is having a one-day clearance sale. You have the following options: Brand A, resolution 1920x1080, picture quality good, price $199; Brand B, resolution 3840x2160, picture quality excellent, price $399. What would you do? Press the letter of the option you choose, or S to search for other options.
You press [HUMAN_RESPONSE]S[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

All 8 experiments (exp0–exp7) got a runnable static jsPsych v8 experiment under `experiments/expN/` (one per `expN.csv`), built from the repo's `transcriptsN.jsonl`/`build_jsonl.py` wording and the dataset schema (this repo has no `simulateN.py`, so the transcription source was used). The headless round trip passed for all 8: the saved CSV matches each `expN.csv`'s columns exactly, response/deferral codings are reproducible, and no data is POSTed by default (each session ends with a CSV download via the `saveData` seam). Block-agnostic cosmetic choices (button scales, cosmetics, a demographics screen recording self-reported age/gender, and the uniform-random between-subject assignment of stimulus/condition/version) are documented in `experiments/README.md`; the browser cannot reproduce the source-specific `code` column (exp0) or the rater-coded `SimilarPriceBetterRating`/`SimilarRatingLowerPrice`/`Justifiability` dummies (exp2), which are left blank. Free-text and `ExplA`/`ExplB` fields are empty in simulate mode (the simulator leaves them blank) but are recorded from real typing.

Run: openrouter/deepseek/deepseek-v4-flash-vision-exp, 2026-08-25

## Simulators

All 8 experiments (exp0–exp7, `simulate0.py`–`simulate7.py`) got a text simulator whose generated participant text is format-identical to `transcriptsN.jsonl`: the headless round trip through `build_jsonl.py` passed byte-identical for all 8. Each simulator randomly assigns the between-subject factors (choice-set condition, stimulus, version, HD price, decoy location, presentation) and asks an agent for the choice/ratings/free-text. `ASSUMPTION:` since the CSVs give no between-subject probabilities, all factors are drawn uniformly at random (matching the observed ~50/50 and ~20%-per-stimulus frequencies). The `code` (exp0), rater-coded dummies (exp2), and demographics `age`/`gender` columns are dropped (a text simulator cannot produce them).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: needs-review (critical 1, major 4, minor 5; fixed 5, open 5).

Checked: paper (https://doi.org/10.1093/jcr/ucac059, PDF), original data (https://researchbox.org/55, ResearchBox_55.zip: 8 SAV files, codebooks, survey materials), exp0-exp7 against Tables 1-7 and every Method section, transform re-run (byte-identical before the fixes), transcripts (build_jsonl.py rebuild, token-to-row mapping for every participant), simulators (simulate0-7 smoke run and build_jsonl.py round trip), analysis (3 effects reproduce), logs. Skipped: none.

Fixed:
- critical: transform.py study2() stacked the Study 2 Age/Gender columns twice instead of repeating them per participant, so every second row of exp1.csv carried the next participant's demographics (P000 trial 1 had age 34, the source row 0 says 45). Fixed; exp1.csv regenerated (only age/gender changed, counts unchanged: 285 m / 219 f / 2 nb); transcripts1.jsonl rebuilt and now carries age/gender metadata like the other experiments (build_jsonl.py no longer excludes them).
- major: the Study 4 source stores one long free-text answer (TwoVer2ExplA) in 255-character pieces _1/_2/_3 (codebook: 'additional text for'); transform.py read only _1, so 16 ExplA texts in exp3.csv ended mid-word ('...it will be wor'). Fixed by joining the pieces (trimmed trailing spaces padded back to 255); exp3.csv regenerated (16 cells), transcripts3.jsonl rebuilt (16 lines).
- major: transcripts6.jsonl described the Study 6 TVs with 'picture quality good/excellent', an attribute the Study 6 stimuli do not have (paper Table 6 p. 15 and survey materials pp. 29-31 list only resolution and price; Study 1 had it). Fixed in build_jsonl.py and simulate6.py; transcripts6.jsonl rebuilt (405 TV lines); simulator round trip still byte-identical.
- major: README described n_options as '2 or 3 products; excluding the no-choice' (exp0) / 'number of product alternatives shown'; the values are 3 and 4 and include the no-choice slot (choice_set lists option_0..option_3). Descriptions corrected in every experiment.
- minor: README experiment headings used '### expN' where the template uses '#### expN' (8 headings).

Open:
- major: exp1.csv, exp2.csv and exp3.csv keep the liking ratings, 10 self-construal items and dominance belief (Study 2), the free-text explanation (Study 3) and the two justifiability ratings and explanations (Study 4) as per-participant columns instead of one row per response (schema rule), while the transcripts mark them as free responses; check_repo therefore counts 15 / 2 / 5 marked responses against 2 / 1 / 1 CSV rows. Every token was verified against the CSV (letters map onto the rows, numbers and texts onto the columns, 0 mismatches), so the data and transcripts agree; restructuring would cascade through transform.py, README, build_jsonl.py, the simulators and analysis.py and needs a human decision.
- minor: check_repo flags transcripts5.jsonl because rating tokens 2-6 never appear literally before the first response; the instruction says 'Rate from 1 (not at all easy) to 7 (very easy)', which declares the range, so this is judged a false positive of the token heuristic (the same phrasing is used for the ratings in exp1 and exp3).
- minor: exp0.csv P1582 has age 0.63; the value is in the source (Study 1 Data.sav row 1582) and is kept as is.
- minor: transcripts0/6 simplify the story sentence ('You have the following options' for every product; the survey says 'In your search, you find the following options' for speakers/hotels and 'They offer the following products' for TVs) and transcripts6 labels backpacks/hotels 'Brand A' instead of 'Backpack A'/'Hotel A'; cosmetic.
- minor: check_repo flags near-empty column descriptions in the README (trial '0', age 'years', gender 'f / m') for exp1-exp7; accurate but terse.

Run: claude-fable-5-1, 2026-09-10
