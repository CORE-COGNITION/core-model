---
tags:
- paradigm:language-comprehension
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
---

# tessler_2018_not

- Paper: https://escholarship.org/uc/item/7p2130hr
- Data source: https://github.com/mhtess/negant (also linked via https://mhtess.github.io/projects/negant_index.html; OSF preregistration https://osf.io/p7f25/)
- PDF: https://web.archive.org/web/20260129043156/https://escholarship.org/content/qt7p2130hr/qt7p2130hr.pdf
- Full text: https://escholarship.org/uc/item/7p2130hr
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Tessler, M. H., & Franke, M. (2018). Not unreasonable: Carving vague dimensions with contraries and contradictions. In Proceedings of the 40th Annual Meeting of the Cognitive Science Society (pp. 1108-1113). Madison, WI: Cognitive Science Society.

## Experiment summary
Participants read a vignette introducing a person described with a gradable adjective (e.g., "Greg is not unhappy") and rated them on a continuous slider from "most positive" to "most antonym", testing whether uncertainty about negation markers (not, un-) lets listeners derive fine-grained interpretations. Experiment 1 (exp0, 120 participants, within-subjects) tested single utterances crossing morphological (e.g., unhappy) and lexical (e.g., short) antonyms across four sentence types (positive, antonym, negated-positive, negated-antonym), with 16 trials each. Experiment 2 (exp1, 750 participants, 2x2 between-subjects) crossed single vs. multiple utterances (trial_type) with lexical vs. morphological antonyms (antonym_type_exp2), where the multi-utterance condition presented four candidate sliders per trial. The headline finding is a consistent ordering of interpretations — e.g., negated-antononym (not unhappy) lands slightly positive — and the critical result that `unhappy` is judged as sadder than `not happy` only when antonyms are offered as alternatives in context (multiple-utterance), not when interpreted in isolation. exp1 combines four source files (single-utterance lexical/morphological and multiple-utterance lexical/morphological) into one file with the paper's 2x2 design.

## Notes

`exp0` = Experiment 1, `exp1` = Experiment 2.

### exp0

| Column | Description |
|--------|-------------|
| participant_id | De-identified participant ID (P000–P119) |
| trial | 0-indexed trial number within participant |
| response | Slider rating from 0 (most antonym endpoint) to 1 (most positive endpoint) |
| rt | Reaction time in milliseconds |
| trial_type | Always "one_slider" in this experiment |
| trial_num | 1-indexed trial number from source (1–16) |
| name | Character name in the vignette |
| positive | Positive-form of the adjective |
| endpoint_high | Label of the high/positive endpoint of the slider |
| negation | Antonym type: "lexical" or "morphological" |
| sentence_type | Adjective type: "positive", "antonym", "neg_positive", "neg_antonym" |
| adjective | Full utterance presented (e.g., "not wise") |
| referent | Always "person" |
| character_gender | Gender of the character in the vignette ("male"/"female") |
| superlative_endpoints | Whether endpoints use superlatives ("tallest") vs "most" + adj (0/1) |
| endpoint_low | Label of the low/antonym endpoint of the slider |
| antonym | The antonym of the positive adjective |
| language | Participant self-reported native language (raw string from demographics) |
| enjoyment | Self-reported enjoyment rating (1–2 scale from demographics) |
| age | Participant age in years |
| problems | Free-text field for technical problems encountered |
| comments | Free-text comments from participant |
| asses | Whether participant approved the HIT ("Yes"/"No") |
| fairprice | Free-text fair price suggestion from participant |
| education | Education level ordinal code (1–4, source coding: 1=some college, 2=associate's, 3=bachelor's, 4=postgraduate) |
| participant_gender | Participant gender normalized: "m", "f", "other", "na" |
| valid | Always 1 (no source validity flags in this dataset) |

### exp1

| Column | Description |
|--------|-------------|
| participant_id | De-identified participant ID (P000–P749) |
| trial | 0-indexed response number within participant; for 4-slider condition, each paper-trial gives 4 consecutive trials |
| response | Slider rating from 0 (antonym endpoint) to 1 (positive endpoint) |
| block | Paper-trial grouping for multi-utterance condition (0–11); NA for single-utterance rows |
| rt | Reaction time in milliseconds; for 4-slider, this is the total display time for all 4 sliders |
| trial_type | "one_slider" for single-utterance, "four_sliders" for multi-utterance |
| trial_num | 1-indexed trial number from source (1–12) |
| name | Character name in the vignette |
| lexant | Lexical antonym of the positive adjective |
| positive | Positive-form of the adjective |
| endpoint_high | Label of the high endpoint of the slider (HTML <br> tags from source) |
| morphant | Morphological antonym (un- prefixed) of the positive adjective |
| adjective | Full utterance presented (e.g., "not sad", "happy") |
| referent | Always "person" |
| adjective_type | Type of utterance: "positive", "lexant"/"morphant", "neg_positive", "neg_lexant"/"neg_morphant" |
| antonym_type | Source's antonym-type label: "lexant" for lexical files, "morphant" for morphological files |
| character_gender | Gender of the character in the vignette ("male"/"female") |
| endpoint_low | Label of the low endpoint of the slider (HTML <br> tags from source) |
| utterance_type | "single" for single-utterance, "multiple" for multi-utterance condition |
| antonym_type_exp2 | "lexical" or "morphological" — the paper's 2x2 condition factor |
| language | Participant self-reported native language (raw string; may contain data-entry errors) |
| enjoyment | Self-reported enjoyment rating (1–2 scale from demographics) |
| age | Participant age in years |
| problems | Free-text field for technical problems |
| comments | Free-text comments from participant |
| asses | Whether participant approved the HIT ("Yes"/"No"/NA) |
| fairprice | Free-text fair price suggestion |
| education | Education level ordinal code (1–4, same coding as exp0) |
| participant_gender | Participant gender normalized: "m", "f", "other", "na" |
| slider_position | Slider slot (1–4) for multi-utterance condition; NA for single-utterance |
| valid | Always 1 |

The `expN` files follow a de-identified participant ID: MTurk worker IDs were remapped to P000, P001, ... in first-appearance order and worker/assignment IDs were dropped; all original perceptual columns are preserved. exp1 combines four source files (7_1slider_lex, 7_1slider_morph, 8_4slider_lex, 8_4slider_morph) into a single file with the paper's 2x2 design encoded by utterance_type and antonym_type_exp2. Pilot/development folders in the source repo (0_L1, 1_S0, 2_L1_oneslider, 3_L1_expandstims, 5_L1_4sliders, 5_L1a_4sliders, 6_antonym-elicitation) were not reported in the paper and are excluded.

## Text-format conversion

Both experiments transcribed: exp0 (Experiment 1, single utterances) and exp1 (Experiment 2, single vs. multiple utterances). Both are language-comprehension tasks — read a statement like "Gabriel is not wise" and rate the person on a 0–1 slider — fully expressible in text. Responses are the slider position (a number from 0 to 1).

Sample transcript (exp0, participant P000, start through first response):

```
In this experiment, your friend tells you about a friend of theirs and describes them with a phrase, like "Gabriel is not wise." On each trial you place that person on a scale. The scale always runs from 0 at the low/antonym label to 1 at the high/positive label. Report your rating as a number from 0 to 1.
Your friend tells you about their friend: Gabriel. "Gabriel is not wise." Where would you place Gabriel? Scale: 0 = the most foolish person, 1 = the most wise person. You set the slider to [HUMAN_RESPONSE]0.42[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments got a runnable static jsPsych build under `experiments/exp0/`
(Experiment 1, single utterances) and `experiments/exp1/` (Experiment 2, 2x2
between-subjects: single vs. multiple utterances × lexical vs. morphological).
The headless `?mode=simulate` round trip validated each against the dataset
schema: `exp0` (16 rows, 2 per negation × sentence_type) and all four `exp1`
cells (single: 12 rows / 3 per sentence type; multiple: 12 blocks × 4 sliders,
shared block rt). Browser-only defaults (colors, intro advance button, slider
start 0.5, the `?utterance=`/`?antonym=` cell selector for `exp1`) are noted in
`experiments/README.md` and do not change the task or recorded data. Visual
rendering check passed (no gross breakage).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Both experiments got a text simulator: `simulate0.py` (Experiment 1, single
utterances, 16 trials, 2 per negation × sentence_type) and `simulate1.py`
(Experiment 2, 2x2 between-subjects: single vs. multiple utterances × lexical vs.
morphological antonyms). Stimulus pools (adjective dimensions, person names,
slider endpoints) are taken verbatim from the CSVs; each simulated participant's
condition/item draws, name assignments, and trial order are randomized. The
round-trip check passed for both: `build_jsonl.py` regenerates transcripts
byte-identical to the simulators' prompts. `simulate1.py` draws a participant's
cell uniformly from the four 2x2 conditions; neither simulator produces reaction
times or demographics. No experimental deviations beyond these assumptions.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
