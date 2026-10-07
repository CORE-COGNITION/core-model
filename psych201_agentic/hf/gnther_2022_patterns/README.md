---
tags:
- paradigm:compound-interpretation
- cognitive-modeling:needs-review
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---
# gnther_2022_patterns

- Paper: https://doi.org/10.1016/j.cogpsych.2022.101471
- Data source: https://osf.io/ycd64/
- PDF: https://osf.io/w3zqj/download
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Günther, F., & Marelli, M. (2022). Patterns in CAOSS: Distributed representations predict variation in relational interpretations for familiar and novel compound words. Cognitive Psychology, 134, 101471. https://doi.org/10.1016/j.cogpsych.2022.101471

## Experiment summary
Two crowdsourced (Prolific) rating experiments test whether distributed semantic-vector representations (whole-word, additive, and CAOSS composition) predict people's relational interpretations of English nominal compounds. In each trial a participant selects 1 of 16 possible relational meanings (e.g., X MADE OF Y, X HAS Y) for a presented compound. Experiment 1 (familiar compounds, ~575 items, data reused from Schmidtke et al. 2018 — present only as per-item aggregate counts) and Experiment 2 (408 novel compounds, N = 400 participants at 55 items each: 51 novel compounds from one of eight lists plus 4 catch trials) both yield per-compound frequency distributions over the 16 relations; a multivariate least-squares regression mapping system trained on the vectors under leave-one-out cross-validation predicts these distributions. The available trial-level data covers Experiment 2 (400 participants × 55 trials = 22,000 rows), where participants made a 16-relation forced-choice judgment per trial. Response is the selected relational-interpretation label.

## Notes

Only Experiment 2 (novel compounds) is original trial-level human behavioral data collected for this paper; Experiment 1 reuses aggregated data from Schmidtke et al. (2018) and is therefore not emitted as an experiment file (it contains no per-participant trial rows). The paper's primary theoretical analysis is computational cognitive modeling (mapping distributed semantic vectors to human interpretation distributions), so the `cognitive-modeling` tag is set. Core behavioral effects (catch-trial compliance at 34/400 non-compliant exactly as reported, a strongly non-uniform distribution of chosen relations across items, and high interpretational variability/entropy) reproduce on the data.

### Columns

#### exp0

Experiment 2 (novel compounds). Trial-level original data from `relational_entropy_novelcomp_raw.csv`; each of 400 Prolific participants judged 55 novel English compounds, picking one of 16 relational interpretations. Note: Experiment 1 (familiar compounds, Schmidtke et al. 2018) is present only as per-item aggregated counts in `Study1_Schmidtke_etal_2018.csv`, so it is not emitted as an experiment file.

| column | description |
|--------|-------------|
| participant_id | Prolific participant number from the source `subject` column (integer labels 110435, 110436, ...), kept as a string. |
| trial | 0..54, sequential position of the judgment within the participant (derived by ranking source `trial_index`, which runs 5..59). |
| response | The selected relational interpretation, a 16-category label from the source `selected` column (e.g. `H_for_M`, `H_made_of_M`, `H_is_M`, `H_location_is_M`). Not a numeric scale. |
| rt | Reaction time in milliseconds (source `rt`), time between trial onset and button press (jsPsych survey-multi-choice). |
| trial_type | jsPsych plugin that presented the trial; constant `survey-multi-choice`. |
| trial_index | jsPsych global trial index (5..59 per participant). |
| time_elapsed | jsPsych cumulative milliseconds elapsed since the session started. |
| internal_node_id | jsPsych internal node path identifying the trial's presentation node. |
| responses | jsPsych response string, the compound plus the chosen relation written out (e.g. `stove LOCATION IS rear`); redundant with `response` + `stim` but kept verbatim. |
| question_order | jsPsych display-order array for the choice options; constant `[0]`. |
| mod | The modifier word (first element) of the compound. |
| head | The head word (second element) of the compound. |
| type | Item type label from the source: `intrain` (novel compound sharing at least one constituent with the Experiment 1 familiar compounds, 204 items), `outtrain` (no shared constituent, 204 items; the paper's two subset analyses, pp. 10-11), or `catch` (one of the 4 attention catch trials). Not a task reset. |
| gender_raw | Participant self-reported gender as free text from the source (e.g. `female`, `male`, `non-binary`); kept verbatim under a non-schema name because it is not in the canonical letter vocabulary. |
| age | Participant age in years (float). |
| lang | Participant language; constant `english`. |
| stim | The full stimulus compound as shown (space-separated modifier and head, e.g. `rear stove` = modifier `rear`, head `stove`). |
| comp | The compound spelling (concatenated, e.g. `rearstove`). |

## Text-format conversion

Experiment 2 (exp0.csv) was transcribed to text: each participant's 55 chosen relations are rendered as letter responses mapped to a per-participant shuffled legend of the 16 relations. No experiments were skipped.

Sample transcript (start through first response):

```
You are taking part in a study of how people interpret novel English compounds: words made of two familiar words combined, which you have almost certainly never seen before. In each trial you see one such novel compound written as two words. The FIRST word is the modifier; the SECOND word is the head. You must choose the one relation that best expresses what the whole compound means, from sixteen possibilities:
A: the head makes the modifier
B: the modifier has the head
C: the head is the modifier
D: the head causes the modifier
E: the head uses the modifier
F: the head is by the modifier
G: the head has the modifier
H: the head is for the modifier
I: the head is from the modifier
J: the head is located at the modifier
K: the head is used by the modifier
L: the head is about the modifier
M: the modifier is located at the head
N: the head is during the modifier
O: the head is caused by the modifier
P: the head is made of the modifier
You answer by typing the letter that names the relation you choose, e.g. type the single letter next to your chosen relation.
You see the novel compound 'rear stove'. What does it mean? You press [HUMAN_RESPONSE]J[/HUMAN_RESPONSE]
 …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Indeterminate: the paper's sole modeling result is a least-squares multivariate multiple regression ("mapping system") predicting each compound's 16-relation frequency distribution from 400-dimensional semantic vectors (whole-word / additive / CAOSS). Its predictor variables are those semantic vectors, induced from an external 2.8B-word corpus, and its training rows are the 575 Experiment-1 familiar compounds (per-item aggregate counts, not emitted as an experiment file). Neither the per-compound vector dimensions nor the Experiment-1 training data are present in or derivable from exp0.csv, so the model cannot be specified from the available columns.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment
Built `experiments/exp0/` (Experiment 2, novel compounds) from the paper + `exp0.csv` — the repo has no `simulate0.py` (transcribed but no text simulator). The headless `?mode=simulate` round trip passed: the produced CSV matches `exp0.csv`'s schema and counts (55 rows/session, `trial` 0..54, 16-relation coding, all 4 catch items present). No experiments skipped. ASSUMPTIONs surfaced: the 408 novel compounds are embedded and each session samples 51 + the 4 catch items in a random order (no per-participant list is recorded); `age`/`gender_raw`/`lang` are collected on a short demographic screen because the original pulled them from the Prolific profile; on-screen relation order and the progress/advance UI are cosmetic (do not change recorded data).
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

`simulate0.py` simulates Experiment 2 (exp0) and passed the round-trip check: transcripts regenerated from a simulated DataFrame via `build_jsonl.py` are byte-identical to the simulator's prompts. Each simulated participant is assigned one of the eight 51-item lists recovered from `exp0.csv` (the 400 participants' item sets form exactly eight disjoint lists) plus the 4 fixed catch items, in a random trial order. ASSUMPTION: no generative choice model is reported, so the chosen relation is left to the injected agent.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 3, minor 5; fixed 6, open 2).

Checked: paper (https://doi.org/10.1016/j.cogpsych.2022.101471, author preprint from https://osf.io/w3zqj/download, 22 pages), original data (https://osf.io/ycd64/: relational_entropy_novelcomp_raw.csv, the aggregated CSV, Study1_Schmidtke_etal_2018.csv, the two CAOSS .dm vector files and both analysis R scripts; baroni.rda, the 714 MB semantic space, not downloaded because transform.py does not read it), exp0, transform re-run (exp0.csv byte-identical to the re-run on the OSF raw file; the transform drops only the three all-empty jsPsych columns stimulus, key_press, button_pressed), transcripts (build_jsonl.py regenerates transcripts0.jsonl byte-for-byte; README sample transcript matches participant 110435), simulators (simulate0.py runs; round trip through build_jsonl.py byte-identical; item lists, catch items and type labels match exp0.csv), modeling (no model.py; the Modeling reproduction section, the cognitive-modeling:needs-review tag and the paper agree that no model was fitted), analysis (analysis.py: 34/400 non-compliant = paper p. 10; non-uniform relation distribution; mean item entropy 1.92 nats vs paper 2.338 bits, both above the test threshold), logs. Paper vs data, all matching: 400 participants; 251 female, 141 male, 8 other or missing; age 18-88, M 35.0, SD 13.5; median session 16.8 min; 408 novel compounds, 204 intrain + 204 outtrain; 8 lists of 51 items; 4 catch trials per participant; 34 non-compliant participants; 44-50 responses per compound after exclusion; man FROM snow 61 and man IS snow 18. Skipped: none.

Fixed:
- major: simulate0.py built the jsPsych `responses` string as '{head} PHRASE {mod}' for all 16 relations; exp0.csv writes '{mod} HAS {head}' and '{mod} LOCATION IS {head}' for M_has_H and M_location_is_H (2461 of 22000 rows). Fixed the order for the two M_ codes; round trip re-run.
- major: simulate0.py and the README Simulators note claimed the eight-list partition is not recoverable and sampled 51 random compounds per participant; exp0.csv holds exactly eight disjoint 51-item sets covering all 408 compounds (49-51 participants each). The simulator now assigns one of the eight recovered lists per participant; docstring and README updated; smoke test and round trip re-run.
- major: README described `type` as a train/test split of the modeling; the paper (p. 10) and Study2_Analysis.R define intrain = shares at least one constituent with an Experiment 1 compound (204 items) and outtrain = shares none (204 items). Description corrected.
- minor: README described `stim` as 'head and modifier'; the source and paper put the modifier first (rear stove: mod = rear, head = stove). Corrected.
- minor: README Experiment summary said '55 items each, plus catch trials' (the 55 already include the 4 catch trials) and gave no 'N =' per experiment. Now 'N = 400 participants at 55 items each: 51 novel compounds from one of eight lists plus 4 catch trials'.
- minor: README Columns heading for exp0 used '###'; set to the template's '#### exp0'.

Open:
- minor: the paper (p. 10) says each of the eight lists was presented to 50 participants; the source (and exp0.csv) has 50, 50, 49, 51, 50, 51, 49, 50 participants per list. The data is faithful to its source.
- minor: the Modeling reproduction section says the mapping-system inputs are not in exp0.csv, which is true; the OSF project ships them (Study1_Schmidtke_etal_2018.csv, COMPOSED_SS.FullAdditive.compset_relent.txt.dm, COMPOSED_SS.FullAdditive.novel_cmplist.txt.dm, baroni.rda, Study2_Analysis.R), so a model.py could be built from the source in a modeling run.

Run: claude-fable-5-1, 2026-09-10
