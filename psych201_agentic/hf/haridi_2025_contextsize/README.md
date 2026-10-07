---
tags:
- paradigm:memory
- cognitive-modeling:needs-review
- psych-201
- text-format:pass
- js-experiment:needs-review
- simulator:pass
---
# haridi_2025_contextsize

- Paper: https://doi.org/10.31234/osf.io/keuw7_v1
- Data source: https://github.com/susanneharidi/memoryscaling
- PDF: https://osf.io/download/ymh3t/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Haridi, S., Schulz, E., & Thalmann, M. (2025). Context-size and set size effects: The relevance of specific cues when searching long-term memory. PsyArXiv. https://doi.org/10.31234/osf.io/keuw7_v1

## Experiment summary
Three cued-recall experiments test how set size (number of studied word pairs) and retrieval-cue characteristics shape long-term memory search. Participants studied cue-target word pairs and recalled the target when cued, with response accuracy and RT recorded on every trial. Experiment 1 (N=174) varied set size (15/20/30 pairs) between-subject; Experiment 2 (N=151) added visual context images (no reliable effect); Experiment 3 (N=116) manipulated semantic context size in addition to set size. Across experiments, larger set sizes slowed RTs and reduced accuracy, while higher cue-target semantic similarity facilitated retrieval; larger semantic contexts hindered recall, consistent with a sequential search model of memory retrieval through a semantic network. This flag is set because the paper fits and evaluates such a sequential sampling model.

## Notes

### Columns

### exp0

| column | description |
|--------|-------------|
| participant_id | Anonymized participant ID (P000..P173) mapped from random jsPsych-generated subject IDs in original order of appearance |
| trial | 0..N within each participant_id, in chronological order (by time_elapsed) |
| response | Typed word for LearningResponse/RecallResponse phases; "0" for CuePresentation space-press; NaN for stimulus-only rows |
| phase | Lowercased Phase label from source: learning, learningresponse, cuepresentation, recallresponse, letterpresentation, letterrecallresponse |
| block | 0-indexed study-test block (original Block 1..4 mapped to 0..3; block 4 in source = 4 here, an end-of-experiment label) |
| rt | Reaction time in milliseconds (source units, already ms) |
| stimulus | HTML stimulus shown to participant, or NaN |
| correct | 1 if recall/learning response matches target, 0 otherwise, NaN for non-response rows |
| valid | 1 for recall test rows (CuePresentation + RecallResponse where source validTrials=True), 0 otherwise |
| cue | Cue word for recall/learning trials, NaN otherwise |
| target | Target word for recall/learning trials, NaN otherwise |
| ListLength | Number of word pairs in the study set for this block (the set-size manipulation) |
| Trial_index | Original 1-indexed trial counter from source (resets per participant), as nullable Int64 |
| trial_index_source | Original jsPsych trial_index (1-indexed), as nullable Int64 |
| word1 | First word of the studied pair |
| word2 | Second word of the studied pair |
| key_press | jsPsych key code for keyboard responses (32 = space), NaN otherwise |
| trial_type | jsPsych plugin type: html-keyboard-response or typed-response |
| time_elapsed | Cumulative ms from session start |
| internal_node_id | jsPsych internal node identifier |
| SequenceLength | Number of items in a letter sequence (letter recall task), NaN otherwise |
| sequence | The actual letter sequence shown, NaN otherwise |
| letterSeen | The individual letter shown in LetterPresentation, NaN otherwise |
| queriedPosition | Position queried in letter recall, NaN otherwise |
| Stimulus_type | Source stimulus type marker; "end_of_experiment" marks final row |
| TrialType | Source trial type label |
| timeMs | Same value as rt (duplicate column in source) |
| timeMin | RT expressed in minutes (timeMs / 60000) |
| score | Source score column (always 1.0 for LearningResponse rows with correct input) |
| correct_01 | Alternate correctness indicator (1.0/0.0), redundant with correct |
| date | Session date string |
| save | Boolean flag from source (always True) |
| experimental_phase | Source ExperimentalPhase column recoded as integer (0/1) |
| W2VWordPairsSim | Word2vec cosine similarity between word1 and word2 (merged from W2VSim file) |
| SimBins | Binned similarity category (1..5, from W2VSim file) |
| Error_type | Error classification: "Omission" or "Intrusion" for incorrect recall trials (merged from ErrorType file) |
| validTrials | Boolean flag from source indicating which rows belong to test trials |
| validID | Boolean flag from source (inverse of validTrials in some phases) |

### exp1

| column | description |
|--------|-------------|
| participant_id | Anonymized participant ID (P000..P150) mapped from random jsPsych-generated subject IDs in original order of appearance |
| trial | 0..N within each participant_id, in chronological order (by time_elapsed) |
| response | Typed word for LearningResponse/RecallResponse; "0" for CuePresentation space-press; NaN for stimulus-only rows |
| phase | Lowercased Phase label from source: learning, learningresponse, cuepresentation, recallresponse, letterpresentation, letterrecallresponse |
| block | 0-indexed study-test block (original Block 1..5 mapped to 0..4) |
| rt | Reaction time in milliseconds (source units, already s) |
| correct | 1 if recall/learning response matches target, 0 otherwise, NaN for non-response rows |
| valid | 1 if source validity=True, 0 otherwise |
| gender | Participant gender: f / m / other |
| age | Participant age in years |
| cue | Cue word for recall/learning trials, NaN otherwise |
| target | Target word for recall/learning trials, NaN otherwise |
| ListLength | Number of word pairs in the study set for this block (set-size: 15 or 30) |
| Trial_index | Original 1-indexed trial counter from source, as nullable Int64 |
| word1 | First word of the studied pair |
| word2 | Second word of the studied pair |
| Context | Path to context image file used during study (e.g., ./images/lake.png) |
| Context_position | Position of context image relative to word pair |
| ContextSize | Number of word pairs sharing the same context image |
| key_press | jsPsych key code for keyboard responses (32 = space), NaN otherwise |
| time_elapsed | Cumulative ms from session start |
| internal_node_id | jsPsych internal node identifier |
| SequenceLength | Number of items in a letter sequence (letter recall task), NaN otherwise |
| sequence | The actual letter sequence shown, NaN otherwise |
| letterSeen | The individual letter shown in LetterPresentation, NaN otherwise |
| queriedPosition | Position queried in letter recall, NaN otherwise |
| correct_01 | Alternate correctness indicator (1.0/0.0), redundant with correct |
| date | Session date string |
| Cheated_pairs | Source flag for cheating on pair learning |
| Cheated_letters | Source flag for cheating on letter recall |
| Error_type | Error classification: "Omission" or "Intrusion" for incorrect recall trials (merged from ErrorType file) |
| validity | Boolean validity flag from source (True for rows passing checks) |

### exp2

| column | description |
|--------|-------------|
| participant_id | Anonymized participant ID (P000..P115) mapped from random jsPsych-generated subject IDs in original order of appearance |
| trial | 0..N within each participant_id, in chronological order (by time_elapsed) |
| response | Typed word for LearningResponse/RecallResponse; JSON string for Commitment/UnknownWords questionnaires; NaN for stimulus-only rows |
| phase | Lowercased Phase label from source: commitment, unknownwords, learning, learningresponse, cuepresentation, recallresponse, letterpresentation, letterrecallresponse |
| block | 0-indexed block (original Block 1..4 → 0..3); NaN for questionnaire phases |
| rt | Reaction time in seconds (source units) |
| correct | 1 if recall/learning response matches target, 0 otherwise, NaN for non-response rows |
| valid | 1 if source validity=True, 0 otherwise |
| gender | Participant gender: f / m / other |
| age | Participant age in years |
| cue | Cue word for recall/learning trials, NaN otherwise |
| target | Target word for recall/learning trials, NaN otherwise |
| ListLength | Number of word pairs in the study set (always 20 in Exp3) |
| Trial_index | Original 1-indexed trial counter from source, as nullable Int64 |
| word1 | First word of the studied pair |
| word2 | Second word of the studied pair |
| Context | Path to context image file (e.g., ./images/jobs.jpg) |
| ContextLabel | Semantic category label for the context (e.g., jobs, animals) |
| Context_position | Position of context cue in trial display |
| ContextSize | Number of word pairs sharing this context (semantic set size) |
| responses | Raw JSON string from questionnaire phases (Commitment, UnknownWords) |
| question_order | JSON array of question order for questionnaire phases |
| type | Source type label: Commitment, UnknownWordsYesNo, UnknownWords |
| key_press | jsPsych key code, NaN otherwise |
| time_elapsed | Cumulative ms from session start |
| internal_node_id | jsPsych internal node identifier |
| SequenceLength | Number of items in a letter sequence, NaN otherwise |
| sequence | The actual letter sequence shown, NaN otherwise |
| letterSeen | Individual letter shown, NaN otherwise |
| queriedPosition | Position queried in letter recall, NaN otherwise |
| correct_01 | Alternate correctness indicator (1.0/0.0), redundant with correct |
| date | Session date string |
| Cheated_pairs | Source flag for cheating on pair learning |
| Cheated_letters | Source flag for cheating on letter recall |
| validity | Boolean validity flag from source |
| validity_rt | Boolean RT validity flag from source |
| NoneListType | Type of the no-context list ("lowSimList" or "highSimPairs") |
| Error_type | Error classification from ErrorType file (merged) |
| RoughContextSize | Binned context size label ("0_NoneLowSim", "1_small", "2_medium", "3_large", "0_NoneHighSim", merged from ErrorType file) |

## Text-format conversion

All three experiments are textifiable cued-recall tasks (word pairs, typed recall, letter-span distractor, and — in Exp3 — verbatim questionnaires) and were transcribed: exp0, exp1, exp2 → transcripts0.jsonl, transcripts1.jsonl, transcripts2.jsonl. No experiment skipped. The visual context images in exp1 are task-irrelevant backgrounds (no reliable effect) and are narrated as such; Exp3's semantic category labels are conveyed in words.

Sample transcript (Experiment 1, participant P000), from the start through the first free response:

```
You will study lists of word pairs and later try to recall them from memory. In the study phase, each pair appears briefly; then one word is hidden and you are prompted to type the missing word (within 5s), after which you see the pair again with a smiley for feedback. Between study and test you do a letter-span distractor task: letters appear one at a time, then you type them in the presented order. In the test phase a cue word is shown; as soon as you recall the other word of its pair, press the space bar, then type that target word (the first three letters need only be correct), or type 0 if you cannot recall it. Your bonus depends on how many you get right, not on speed. On every type-the-word prompt, type the missing or target word itself, or the digit 0 if you do not know it.
Block 1 begins with 30 word pairs.
You study the pair gravy - grits.
You are shown gravy. You type the missing word. You type [HUMAN_RESPONSE]grits[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24
## Online experiment

All three experiments got an online build: `experiments/exp0/` (Exp 1, between-subject set-size versions), `experiments/exp1/` (Exp 2, visual context, 15/30 pairs), `experiments/exp2/` (Exp 3, semantic-category context + questionnaires). Each reproduces the study → letter-distractor → cued-recall structure, the source stimulus pools, and the verbatim instruction wording, and each saves a CSV in its own `expN.csv` schema (the word-embedding / R-analysis columns — `W2VWordPairsSim`, `SimBins`, `Error_type`, `validTrials`, `validID`, `gender`/`age`, `Cheated_*`, `validity*`, `NoneListType`, `RoughContextSize` — are left empty or omitted, since a browser cannot produce them). The headless round trip (jsPsych `?mode=simulate`) ran and passed the schema/dtype/count check for all three; the advisory screenshot check found no gross rendering breakage. `needs-review` because of substantive stimulus assumptions: Exp0 fixes an array-indexing inconsistency in the original list-builder (so each list is exactly its announced length and the version/random assignment are recovered rather than bug-for-bug), and Exp1/Exp2 render the task-irrelevant context images as a labelled background and re-derive the per-block pair assignment rather than shipping the binary images / exact per-participant pairing.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling. The SimSS model likelihood (Haridi et al. 2025, Eq. 4-13, Appendix C; SimSSModelFittingAndComparison.R / FunctionsSimSSModelVariation.R) requires per-trial word2vec semantic similarity between the cue and every candidate item in the list, which is not derivable from the CSV columns (only exp0 carries a cue-target-only similarity column, W2VWordPairsSim, and no within-list distractor-similarity structure is present).
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Indeterminate: required CSV columns missing - no word-embedding/semantic-similarity columns; the only specifiable variant would be the no-similarity baseline, materially simplifying the paper's model.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24
## Simulators

All three experiments got a text simulator: `simulate0.py` (Experiment 1, set-size effects), `simulate1.py` (Experiment 2, visual context), `simulate2.py` (Experiment 3, semantic context). Each regenerates its word-pair pool from the local `expN.csv`, narrates the study → letter-span distractor → cued-recall structure with the build_jsonl.py wording, and passed the byte-identical round-trip check (simulated df → build_jsonl.py → transcripts match the simulator's prompts). Assumptions worth surfacing: Experiment 1's recall queries exactly `min(set size, 10)` pairs (data-authoritative; the paper leaves the count unstated); Experiment 2's "random context size" last block is drawn as either a full-size single context or a uniform two-way partition of the set size; concrete stimuli are sampled from the repo's own CSVs rather than synthesized.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
