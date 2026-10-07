---
tags:
- paradigm:memory
- psych-101
- text-format:pass
- simulator:pass
- js-experiment:pass
---
# popov_2023_intent

- Paper: https://doi.org/10.1037/xge0001272
- Data source: https://github.com/venpopov/intentional-incidental-ltm-paradox
- PDF: https://osf.io/jf2en/download
- Full text: https://psyarxiv.com/jf2en
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Popov, V., & Dames, H. (2023). Intent matters: Resolving the intentional versus incidental learning paradox in episodic long-term memory. Journal of Experimental Psychology: General, 152(1), 268–300.

## Experiment summary
Eleven experiments test whether intent to remember boosts episodic long-term memory, contrasting intentional vs incidental (deep-processing size-judgment) learning in mixed-list (within-subject) and pure-list (between-subject) designs. During encoding participants judged word size, performed arithmetic/mental-math distractor blocks, then free recalled or recalled cued items; the primary behavioral response is free recall (plus study/test RTs and per-trial recall accuracy). The headline finding — reproduced on these CSVs — is an intent (remember > process) recall advantage in mixed-list designs but not pure-list designs, resolved via a selective threshold-shifting account. Analyzed participant counts per experiment: E1=55, E2=54, E3=58, E8=34, E4=47, E9=47, E5=82, E6=180, E7=56, E10(mixed)=63, E9(pure)=80, E12=117 (differing experiment order reflects the paper's reported numbering; see table below).

## Notes

### Columns

# popov_2023_intent — transform notes & column reference

## Raw-directory → output mapping

The repo's data files use the **original experiment-run numbering**, which differs from the
paper's reported order (per `raw/README.md` and `raw/important-information-about-numbering-of-experiments.md`).

| output | raw dir | reported experiment |
|--------|---------|---------------------|
| exp0   | exp1    | 1 |
| exp1   | exp2    | 2 |
| exp2   | exp3    | 3 |
| exp3   | exp4    | 8 |
| exp4   | exp5    | (companion of 8; not separately reported) |
| exp5   | exp6    | 4 |
| exp6   | exp7    | 9 |
| exp7   | exp8    | 5 |
| exp8   | exp9    | 6 |
| exp9   | exp10   | 7 |
| exp10  | exp11_corrected | 10 (mixed-list / within-subject part) |
| exp11  | exp12   | 10 (pure-list / between-subject part) |
| exp12  | exp15   | (Dames & Popov 2023 — different paper) |

Note: reported Experiment 10 (4AFC location source-memory paradigm) uses both
`exp11_corrected` (mixed-list within-subject) and `exp12` (pure-list between-subject).
`exp4`/`exp5` are both 2AFC-recognition runs differing in foil type (new words vs. List-2
words); only `exp4` is separately reported (as Experiment 8). Reported Experiment 11
(3AFC scene selection, per the paper) is not present in this raw-data snapshot — its stimuli
(`materials/scenes.zip`) exist but no preprocessed trial data was released.

`source_experiment` = original raw dir; `reported_experiment` = paper experiment number where
applicable (NaN otherwise, e.g. exp4/exp12).

## Common columns

Every experiment is in long, one-row-per-response form. A session's study, math-distractor, and
test/cued/recognition phases are all retained. `task_id` separates the distinct task types
(0=study, 1=distractor, 2=recall/test, 3=cued_test, 4=recognition); `trial` is 0-indexed inside
each `(participant_id, task_id)`; `block` = `listid - 1` (0-indexed list).

- `participant_id`: original participant number from the source (`id` column), as string.
- `trial`: 0-indexed response counter within `(participant_id, task_id)`.
- `response`: the participant's choice for that row. Coding depends on `phase`:
  - study: size judgment, verbatim `"larger"` / `"smaller"` (of the two objects/word vs. football).
  - distractor: the arithmetic answer the participant typed.
  - recall/cued_test: the recalled word (`typed_word`) — free/cued recall output; blank if none.
  - recognition: the 1–6 key-press confidence rating (Dames & Popov subset).
- `source_experiment`: original raw-experiment directory.
- `reported_experiment`: paper experiment number (where applicable).
- `task_id`: 0-indexed task-type code (see above).
- `phase`: `study` / `distractor` / `recall` / `cued_test` / `recognition`.
- `block`: 0-indexed list number = `listid - 1`.
- `rt`: reaction time in ms for that response (mirrors `studyRT`/`duration`/`testRT`).
- `correct`: `1`/`0`. For distractor rows = (answer == cresp). For study rows it is the
  source's `acc` (per-item recall-accuracy) carried into the canonical `correct` name.
- `source_file`: the raw CSV the row came from.

Columns not listed below are carried through verbatim from the source CSV (values in original
units/coding); see the raw files for details.

### exp0 (reported 1) — words & word-pairs, six blocks (~), colors cued at onset
| column | description |
|--------|-------------|
| listid | study list number, 1–3 |
| eq_id | arithmetic-equation index within the distractor block |
| question | the arithmetic equation shown (e.g. "(4 + 4) * 4") |
| duration | distractor response time in ms |
| expect_test | "No"/"yes": post-task whether participant expected a test on all items |
| use_help | "No"/"Yes": whether participant used an aid to remember |
| cresp | correct solution of the arithmetic equation |
| study_position | 1-based serial position of the word in its list |
| color_condition | assigned memory-color for the participant ("red"/"blue") |
| trial_condition | item instruction: "process" (Process-only) / "remember" (Remember) |
| stimulus_condition | "words" / "pairs" (single word vs. word pair) |
| presented_color | border color shown on the trial (red/blue) |
| word1 | first (or only) word presented |
| word2 | second word of a pair (NaN for single words) |
| studyRT | size-judgment RT in ms (== rt on study rows) |
| exp_duration | participant's total experiment duration (min) |
| output_pos1 / output_pos2 | serial recall-output position(s) for the item |
| testRT1 / testRT2 | recall RT in ms for the output(s) |
| acc1 / acc2 | recall accuracy (0/1) for first/second output position |
| exclude | True/False: participant flagged for exclusion |
| cue_prioritem1 / cue_prioritem | instruction of the immediately preceding study item |
| cue_consec_value | running value of consecutive preceding items of same instruction |
| cue_consec_lab | label for cue_consec_value ("processN"/"rememberN") |
| math_acc | overall arithmetic accuracy of the participant |
| n | number of arithmetic equations administered |
| output_position | (test rows) 0/1-indexed output slot for a recalled word |

### exp1 (reported 2)
Same columns as exp0 plus `ended_on` (test-phase marker of how the recall screen ended).

### exp2 (reported 3)
Same columns as exp0 plus `ended_on`.

### exp3 (reported 8) — individual words + free recall then 2AFC item recognition
| column | description |
|--------|-------------|
| listid | list number 1–3 |
| study_position, color_condition, trial_condition, stimulus_condition, presented_color | as exp0 (single words only) |
| word1 | the studied word |
| studyRT | size-judgment RT (ms) |
| recall_all_q | "Yes"/"No": tried to recall all words in final test |
| output_pos1 / testRT1 / recall_acc | free-recall output position / RT (ms) / accuracy (0/1) |
| tested_word_left / tested_word_right | the two words in the 2AFC recognition pair (List 3; NaN on earlier lists) |
| recog_response | recognition choice: "left"/"right" (NaN on free-recall lists) |
| recogRT | recognition RT (ms) |
| old_pos | "left"/"right": side of the studied (old) word |
| recog_pos | serial position of the old word's study trial |
| recog_acc | recognition accuracy 0/1 |
| exclude | True/False exclusion flag |
| cue_prioritem1 / cue_prioritem / cue_consec_value / cue_consec_lab | preceding-item instruction coding (as exp0) |
| math_acc, n, exp_duration, expect_test, use_help | as exp0 |

### exp4 (raw exp5; companion of reported 8) — 2AFC recognition, List-2 foils
Same columns as exp3, plus:
| column | description |
|--------|-------------|
| rep | repetition index for the studied item |
| l2_recall | marker that the foil word came from List 2 (vs. a new word in exp3) |

No `reported_experiment` (not separately reported in the paper).

### exp5 (reported 4) — words & word-pairs, delayed cue
Columns match exp0 (listid 1–3, words/pairs), recalling after a distractor; includes
`recall_all_q`. Values coded as in exp0.

### exp6 (reported 9) — pure-list between-subject (individual words)
| column | description |
|--------|-------------|
| btw_cond | between-subject instruction group ("remember_all" / "process_all") |
| study_position, color_condition, trial_condition, presented_color, word1, studyRT | as exp0 |
| recall_all_q | Yes/No tried-to-recall-all |
| output_pos1 / testRT1 / acc1 | free-recall output position / RT (ms) / accuracy (0/1) |
| exclude | exclusion flag |
| cue_prioritem1 / cue_prioritem / cue_consec_value / cue_consec_lab | preceding-item coding |
| math_acc, n | as exp0 |

### exp7 (reported 5) — output-interference / recall-by-color
| column | description |
|--------|-------------|
| study_position | serial position |
| color_condition, trial_condition, presented_color | as before (no Remember/Process split; trial_condition still coded) |
| test_first | which color tested first, or "all" (control) |
| word1, studyRT | studied word, size-judgment RT (ms) |
| testid, test_color | test block id / color tested in that block |
| output_pos1 / abs_output_position | recall output position / absolute output slot |
| testRT | recall RT (ms) |
| strict_acc | strict recall accuracy (0/1) |
| color_intrusions | whether recalled item was from the other color |
| output_position, n | as elsewhere |

### exp8 (reported 6) — relational size-judgment (word vs previous word)
| column | description |
|--------|-------------|
| word1 | studied word |
| resp | size judgment relative to previous item ("larger"/"smaller") |
| X | trial-level index in source |
| larger_p | model/probability that previous item is larger (0–1) |
| sizeRT | RT of the relational judgment (ms) |
| size_group | 0/1/2 size-bin of the word |
| lp_prioritem / sizeg_prioritem1 / sizeg_prioritem | size info of the preceding item |
| size_diff | signed size difference to preceding item |
| output_pos1 / testRT / acc | free-recall output position / RT (ms) / accuracy (0/1) |
| cue_... , presented_color, trial_condition, listid, study_position, studyRT, expect_test, use_help | as exp0 |

### exp9 (reported 7) — relational encoding + relational size judgment, cued recall
Same relational columns as exp8, plus the cued-recall source (`preproc_mem_data_cue_test.csv`
and `preproc_memdat3.csv`, phase `cued_test`):
| column | description |
|--------|-------------|
| presented_word1 | word shown at study in the cue-test file |
| test1RT / output_order1 / acc1 | first cued-recall output RT (ms) / order / accuracy |
| test2RT / output_order2 / acc2 | second cued-recall output (e.g. the paired word) |
| test_cue | cue word in the memdat3 cued-recall file |
| cue_output_order / cue_study_position | output order / study position of the cue |
| cue_condition | instruction of the cue ("remember"/"process") |
| resp_study_position / resp_cond | study position / condition of the recalled word |
| word_prioritem / cue_postitem / word_postitem | preceding item's word, following cue and word |

### exp10 (reported 10, mixed-list / within-subject) — 4AFC location source memory
| column | description |
|--------|-------------|
| presented_position | screen quadrant/position shown during study (1–4) |
| loc_resp | location response at test (1–4 quadrant) |
| loc_rt | location-test RT (ms) |
| loc_test_serial_position | serial position of the location test trial |
| loc_acc | location source-memory accuracy (0/1; NaN where not tested) |
| pos_prioritem1 / pos_prioritem | position/instruction of preceding item |
| main1_joint / sub1_joint / main2_joint / sub2_joint | post-experiment strategy questionnaire codes (from `strategies_final.csv`), joined by participant |
| [listid, study_position, color_condition, trial_condition, presented_color, word1, studyRT, exp_duration, recall_all_q, output_pos1, testRT1, recall_acc, exclude, cue_..., math_acc, n] | as exp0 |

### exp11 (reported 10, pure-list / between-subject)
Same location source-memory columns as exp10 (with `presented_position`, `loc_resp`, `loc_rt`,
`loc_acc`, `pos_prioritem`...), plus `btw_cond` (between-subject group, "remember_all" /
"process_all"). No strategy-questionnaire columns.

### exp12 (raw exp15; Dames & Popov 2023 — different paper) — confidence-rated recognition
| column | description |
|--------|-------------|
| age | participant age band ("young"/"old") |
| stimulus_condition | word type |
| response | 6-point confidence rating (1–6) in the old/new recognition test |
| tested_word | word shown in the recognition trial |
| test_trial_type | "old" (studied) vs "new" (foil) |
| trial_condition | "remember"/"process" (or NaN for new/foil trials) |
| recog_pos | serial position of the recognition trial |
| listid, color_condition, duration, expect_test, use_help, recall_all_q | as elsewhere |

## Update (2026-08-13)
- Chronology fix (rows reordered; only the `trial` column renumbered, no other cell changed): the
  previous transform ordered rows within each `(participant_id, task_id)` by `study_position`
  alone, omitting `listid`. Because `study_position` is the 1-based position *within a list*, the
  study-phase trials of every participant were interleaved across lists (list1-pos1, list2-pos1,
  list3-pos1, list1-pos2, ...). Rows are now ordered within each `(participant_id, task_id)` by
  original source row order, which in every raw file is participant-contiguous and ordered by
  `listid` then within-list position (`study_position` / `eq_id` / `output_position`), so each
  list's trials are contiguous and in presentation order, and each list's study trials precede that
  list's test trials.
- `trial` renumbered 0..N-1 within `(participant_id, task_id)` in the corrected order.
- Affected files: exp0-exp6, exp8-exp11 (11 of 13; every participant reordered except 3 in exp10).
  exp7.csv and exp12.csv were already in source order and are byte-identical to the previous
  release. Row counts, participant counts, and per-participant row multisets unchanged in all files.
- Verified by re-running the (fixed) transform against the original raw GitHub data: the previous
  transform byte-reproduces the previous CSVs, the fixed transform byte-produces the new ones.

CSVs fixed in place from the previous release; transform.py updated to produce the same output
from raw. The previous version remains in the repo's git history.

## Text-format conversion

All 13 experiments (exp0–exp12) were transcribed to one natural-language string per participant:
`transcripts0.jsonl`–`transcripts12.jsonl`, produced by `build_jsonl.py`. Each transcript narrates
the whole session in order (study size-judgements, arithmetic distractors, and free recall /
cued-recall / recognition / source-memory tests), wrapping free responses in
`[HUMAN_RESPONSE]...[/HUMAN_RESPONSE]`. No experiment was skipped as untextifiable — the tasks are
word/size orienting with typed or key responses, expressible in text. Note exp12 is from a separate
(Dames & Popov) paper bundled in the repo; it retains its own recognition-narration.

Sample transcript (exp0, first participant, up to the first marked response):

```
You are taking part in a memory experiment. You study one list of words at a time (several lists). For each item, judge whether its referent is larger or smaller than a football; answer with the exact token 'larger' or 'smaller'. An item whose border is red must be remembered for a later memory test; items with the other border color are only processed. After each list you solve a one-minute arithmetic distractor and type each answer, followed by a free-recall test in which you type the words you remember.

You study church inside a blue border. Only process this word. You judge whether its referent is larger or smaller than a football. You answer: [HUMAN_RESPONSE]larger[/HUMAN_RESPONSE]
```

## Simulators

All 13 experiments (exp0-exp12) got a simulator (`simulate0.py`-`simulate12.py`).
Each produces a long-format DataFrame matching its `expN.csv` schema (minus
unproduced columns) and a transcript that round-trips byte-identically through
`build_jsonl.py`. Stimulus words are sampled from the 180-item pool, distractor
arithmetic is generated as `(x+y)/z = ?`, and free responses (size judgements,
arithmetic answers, recalled words, recognition/location/rating choices) come
from the supplied agent.

ASSUMPTION: which items are recalled, and the exact arithmetic answers /
recognition, location and confidence choices, are free agent decisions (the
smoke test uses a uniform-random agent); the number of distractor equations and
of recalled items per participant is a random draw. exp8 (reported 6) narrates
only study + distractor because its `trans_89(cued=False)` does so. A few
unproduced columns (RTs, `exclude` boolean coding, `correct` on study rows) are
kept as NaN / simplified to match the schema.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

All 13 experiments got a static jsPsych v8 online port under `experiments/expN/`
(one per `expN.csv`), reproducing each simulator's task and wording and saving a
session to that experiment's own CSV schema. The headless `?mode=simulate` round
trip passed for every experiment (exact column names, dtypes/codings, structural
counts). No experiment was skipped. Assumptions surfaced: the block transition
screens and the one-word-per-line recall text-area are browser-only renderings
(the one-minute distractor is approximated by an equation count in the source
range); per-item recall accuracy on study rows is computed from the
participant's typed outputs. See `experiments/README.md`.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
