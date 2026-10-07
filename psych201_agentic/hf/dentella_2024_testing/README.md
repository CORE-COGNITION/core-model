---
tags:
- paradigm:language-comprehension
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
---

# dentella_2024_testing

- Paper: https://doi.org/10.1038/s41598-024-79531-8
- Data source: https://osf.io/dfgmr/
- PDF: https://www.nature.com/articles/s41598-024-79531-8.pdf
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Dentella, V., Günther, F., Murphy, E., Marcus, G., & Leivada, E. (2024). Testing AI on language comprehension tasks reveals insensitivity to underlying meaning. Scientific Reports, 14, 28083. https://doi.org/10.1038/s41598-024-79531-8

## Experiment summary
401 human participants (and multiple LLMs, excluded here) answered yes/no comprehension questions about constructed sentences probing several levels of linguistic analysis, with each of 22 items repeated three times. Two independent settings split by response format — one-word (`exp0`, N=201) and open-length (`exp1`, N=200) — give per-trial accuracy (`correct`) against a ground-truth answer and a per-item `stability` index across the three repetitions. The research question is whether AI language comprehension is sensitive to underlying meaning; human data show ~89% accuracy and ~92% stability, well above chance and indistinguishable between the two response settings.

## Notes

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | Internal participant file/ID string from source (e.g. `COMPR_1word_108385.csv`), one-word response setting |
| trial | 0..65 within each participant_id, in source presentation order |
| response | Participant's free-text answer to the comprehension question (e.g. `yes`, `no`) |
| item | Full comprehension item (sentence + question) the participant answered |
| gender | Canonical self-reported gender (`f`/`m`/`na`, normalized from free text `female/male/woman/females/man/m/make/38`) |
| age | Participant age in years (NaN where source missing) |
| language | Self-reported native language string (free text, e.g. `english`) |
| speech_therapy | Self-report whether received speech therapy (`no`) |
| mental_conditions | Self-report of mental conditions (`no`) |
| sentence_text | The constructed sentence shown |
| sentence_question | The comprehension question asked |
| sentence_question_full | The question text including response-format instruction |
| attention_check | 0/1 whether the item was an attention check item |
| version | Response-setting label (`1word` = one-word setting) |
| repetition | Presentation ordinal (1..6) reused per-session; each item seen 3x |
| correct_answer | Ground-truth answer (`yes`/`no`) |
| correct | 0/1 whether response matched correct_answer (source `accuracy`) |
| stability | 1 if all 3 answers to the item matched, 0 otherwise, NaN on first presentation |

### exp1
| column | description |
|--------|-------------|
| participant_id | Internal participant file/ID string from source (e.g. `COMPR_open_101822.csv`), open-length response setting |
| trial | 0..65 within each participant_id, in source presentation order |
| response | Participant's free-text answer to the comprehension question |
| item | Full comprehension item (sentence + question) the participant answered |
| gender | Canonical self-reported gender (`f`/`m`/`na`, normalized from free text) |
| age | Participant age in years (NaN where source missing) |
| language | Self-reported native language string (free text) |
| speech_therapy | Self-report whether received speech therapy (`no`) |
| mental_conditions | Self-report of mental conditions (`no`) |
| sentence_text | The constructed sentence shown |
| sentence_question | The comprehension question asked |
| sentence_question_full | The question text including response-format instruction |
| attention_check | 0/1 whether the item was an attention check item |
| version | Response-setting label (`open` = open-length setting) |
| repetition | Presentation ordinal (1..6) reused per-session; each item seen 3x |
| correct_answer | Ground-truth answer (`yes`/`no`) |
| correct | 0/1 whether response matched correct_answer (source `accuracy`) |
| stability | 1 if all 3 answers to the item matched, 0 otherwise, NaN on first presentation |

The LLM data (`LLM_comprehension_data.xlsx`) from the OSF repository is not human and is excluded. The two experiments correspond to the paper's response-format settings (`1word` vs `open`); each item was presented three times per participant in a fixed order.

## Online experiment

Both experiments got a runnable static online experiment: `experiments/exp0/`
(one-word setting) and `experiments/exp1/` (open-length setting), built from the
paper, the CSV schema, and the transcript wording. The headless `?mode=simulate`
round trip passed for both, confirming their CSV output matches `exp0.csv` /
`exp1.csv` (column names, 66 rows per participant, trial 0..65, repetition
1/2/3, `stability` blank on first presentation, `version` `1word` / `open`). No
experiments were skipped. The only assumption worth surfacing: each session is
randomly assigned one of the two item lists (the paper gives each list to half
the subjects; the schema has no list column). The stimulus pools split
40 comprehension items + 2 attention checks into two lists of 22.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Text-format conversion

Both experiments (exp0 one-word, exp1 open-length) were transcribed; the stimuli are already natural-language sentences and questions, so no modality is lost in text. Each participant's session is narrated as the sentences and questions they saw, with their free answers wrapped in `[HUMAN_RESPONSE]...[/HUMAN_RESPONSE]`. No experiment was skipped.

Sample transcript (exp0, first response):

```
You take a language comprehension test. For each prompt you are shown a sentence and a question about it, and you must answer the question using just one word. On each trial, read the sentence, then answer the question that follows by typing the one word that answers it.
Sentence: Alice calls Flavia and Flavia is called by Molly. Molly is kissed by Alice. Question: In this context, was Molly kissed? (Answer using just one word) You type [HUMAN_RESPONSE]yes[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

Both experiments got a simulator (`simulate0.py` for the one-word setting, `simulate1.py` for the open-length setting). Each builds a participant's session from one of the two counterbalanced 22-item lists (20 comprehension + 2 shared attention checks, fixed order, each item 3 times = 66 trials); the only free response is the yes/no answer to each question. The round-trip through `build_jsonl.py` passed for both (`text` identical to the regenerated transcripts). Assumptions surfaced: list assignment is a fair 50/50 coin flip; the `repetition` column (irregular in the source, unused by the transcript) is emitted as the regular `1,2,3`; exp1's free-length replies are constrained to yes/no since ground truth is yes/no.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
