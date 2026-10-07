---
tags:
- paradigm:language-comprehension
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---
# dentella_2023_systematic

- Paper: https://doi.org/10.1073/pnas.2309583120
- Data source: https://osf.io/7ajxr/
- PDF: https://ddd.uab.cat/pub/artpub/2023/287647/pnas_a2023v120n51art2309583120.pdf
- Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC10743380/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Dentella, V., Günther, F., & Leivada, E. (2023). Systematic testing of three Language Models reveals low language accuracy, absence of response stability, and a yes-response bias. Proceedings of the National Academy of Sciences, 120(51), e2309583120. https://doi.org/10.1073/pnas.2309583120

## Experiment summary
This study evaluates whether large language models (ChatGPT-3.5, GPT-4, GLM-130B) exhibit human-like grammatical competence, using grammar-adherence and meaning-adherence tests; the human comparison experiment (the only human behavioral data, uploaded here, n=80 native English Prolific speakers) is a binary grammaticality-judgment task. Each participant was assigned one of 8 counterbalanced lists, i.e. one linguistic phenomenon: its 5 grammatical and 5 ungrammatical sentences were each presented 10 times to measure response stability, plus 2 attention-check sentences presented 5 times each, giving 110 trials per participant and 8,800 trial-level rows. The research question is whether LMs match human accuracy, absence of yes-response bias, and response stability in grammaticality judgments.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number, extracted from the source `participant` value (`<phenomenon>__LLM_<id>.csv`) as the numeric `<id>`; 80 unique human participants (native English Prolific speakers) |
| trial | 0..109, 0-indexed within each participant; source row order, which is sorted by `test_item` and `repetition` (the source does not record the random presentation order) |
| response | Reconstructed binary grammaticality judgment, 1 = "yes" (judged grammatical), 0 = "no" (judged ungrammatical); derived from `accuracy`+`condition` exactly as the paper's RScript does (no raw keypress is recorded in the source) |
| sentence | The stimulus sentence judged on that presentation |
| test_item | Item label in the source (e.g. `TS 1`..`TS 10`, `CHECK1`, `CHECK2`) |
| phenomenon | Linguistic phenomenon category of the sentence: one of the 8 phenomena or `attention check` |
| condition | Whether the sentence is `grammatical` or `ungrammatical` (ground truth) |
| correct | `accuracy` from source, 1 = response matched grammaticality, 0 = mismatch |
| repetition | Presentation count 1..10 within each (participant, test_item) — 1..5 for attention checks; each sentence was judged 10 times to measure stability |
| stability | 0/1 whether the judgment changed from the previous presentation of the same sentence (1 = change, 0 = no change, the paper's oscillation coding; NA/empty on first presentation, `repetition`=1) |
| gender | Participant gender normalized to f/m/na from source (`female`/`woman`/`male`) |
| age | Participant age in years |
| language | Self-reported native/known language as typed in the source (78 `english`, 1 `engliish`, 1 `shona`) |
| speech_therapy | Self-reported speech-therapy history, `no`/`yes` string from the source; `no` for all 80 participants |
| mental_conditions | Self-reported mental health conditions, `no`/`yes` string from the source; `no` for all 80 participants |

This dataset contains only the human-participant data from the paper's comparison experiment (`humans_grammaticality_data.csv`). The LM responses are not human behavioral data and are excluded. Because the raw source records only `accuracy`/`stability` and no raw keypress, the binary `response` is reconstructed from `accuracy` and `condition` following the paper's RScript (a response is "yes"/grammatical when the participant judged the sentence grammatical). The demographic variables (gender, age, language, speech_therapy, mental_conditions) come from a self-report questionnaire appended to the source rows. The source rows are sorted by `test_item` and `repetition` within each participant; the random presentation order used in the experiment (paper p. 3) is not recorded, so `trial` and the transcripts follow the source order, not the order the participant saw.

## Text-format conversion

The single experiment (exp0, grammaticality judgments) is textifiable: each trial's stimulus is the sentence itself, and the binary judgment is a discrete C/N response. All 110 trials per participant (the 10 sentences of the participant's phenomenon list, each shown 10 times, plus the 2 attention checks shown 5 times each) were transcribed in source row order (grouped by sentence; the random presentation order is not recorded in the source), one line of `transcripts0.jsonl` per participant, with the free C/N judgment wrapped in `[HUMAN_RESPONSE]`. No experiment was skipped.

```text
You will be shown 110 sentences in random order. For each sentence, indicate whether the sentence is grammatically correct in English. The question is always: "Is the following sentence grammatically correct in English?" Press C if the sentence is grammatically correct, or press N if it is not grammatically correct.
Sentence: "The new door is red". You press [HUMAN_RESPONSE]C[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

exp0 got a static jsPsych v8 online experiment (`experiments/exp0/`): a faithful port of the human grammaticality-judgment task (one of the 8 counterbalanced lists, 110 sentences in random order, C/N judgments, no feedback), built from the paper + `exp0.csv` (no simulator present). The headless `?mode=simulate` round trip passed: column names/order, 110 rows, and the `response`/`correct`/`repetition`/`stability` codings all match `exp0.csv`. No experiment skipped. ASSUMPTIONS: list assigned at random (rather than 10-per-list), true random presentation order, and the demographic-question wording (not given in the paper) is a minimal self-report screen. Note `stability` follows the paper's oscillation coding (1 = changed from the previous presentation of the same sentence).

## Simulators

exp0 got a text simulator (`simulate0.py`): each simulated participant draws one of the 8 phenomena uniformly, then judges its 10 test sentences 10 times plus the 2 attention checks 5 times (110 trials, shuffled). The round-trip check through `build_jsonl.py` passed byte-identical (fixed C/N mapping). Demographic columns are dropped. ASSUMPTION: phenomenon assignment and 110-trial presentation order are uniformly random per participant (the paper reports 8 counterbalanced lists with 5M/5F each and random presentation order).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 4, minor 10; fixed 9, open 5).

Checked: paper (https://doi.org/10.1073/pnas.2309583120, PDF), original data (https://osf.io/7ajxr/: humans_grammaticality_data.csv, RScript.R), exp0, transform re-run (exp0.csv byte-identical), transcripts (build_jsonl.py rebuild byte-identical), simulator (simulate0.py runs; 82/82 stimuli match exp0.csv; round trip through build_jsonl.py byte-identical), analysis (analysis.py: 3/3 effects reproduce), logs; no model.py and no cognitive-modeling tag, so no modeling check applies. Skipped: none.

Fixed:
- README Columns: `stability` was described as 1 = the judgment matched the previous presentation. The source codes 1 = change (stability equals accuracy != previous accuracy in all 7,840 coded rows) and the paper (p. 2) says the same. Description corrected.
- README Columns: `trial` was described as the presentation order. The source rows are sorted by `test_item` and `repetition` (CHECK1, CHECK2, TS 1, TS 10, TS 2, ...), and the paper (p. 3) says the 110 sentences were shown in random order. Column description and Notes now say the presentation order is not recorded.
- README summary and Text-format section said each participant judged 110 different sentences across all 8 phenomena, each shown once. exp0.csv and the paper (p. 2-3): each participant got one phenomenon list, 10 sentences x 10 repetitions + 2 attention checks x 5 = 110 trials. Both passages corrected.
- README Columns: `language` said all `english`; exp0.csv has 78 `english`, 1 `engliish`, 1 `shona`. Corrected.
- README Columns: `gender` source values now include `woman` (1 participant, mapped to f).
- README Columns: `speech_therapy` and `mental_conditions` now state that both are `no` for all 80 participants.
- README Columns: `sentence` lost the meaningless phrase "(precedes each test sentence)".
- README Text-format section had no `Run:` line; added the model and date the transcribe run wrote (transcripts/auto-exp-transcribe.log: deepseek-v4-flash-0731, 2026-08-24).
- README Columns heading `### exp0` changed to the template's `#### exp0`.

Open:
- minor: transcripts0.jsonl renders the 110 trials in the source's sentence-grouped order after the participant instruction "in random order" (paper p. 3); the source does not record the presentation order. Documented in the README, transcripts unchanged.
- minor: the paper (p. 2) says all participants were native English speakers; the source has one participant with language `shona` and one with `engliish`.
- minor: the paper (p. 3) says 5 male and 5 female participants per list; the source lists are unbalanced (Anaphora 4 F / 6 M, Comparative Illusion 6 F / 4 M, ...). The totals 38 F / 42 M match the paper (p. 2).
- minor: the paper (p. 3) excluded 14 participants for failed attention checks; the source ships only the 80 analyzed participants (attention-check accuracy 1.0 for all), so the excluded rows cannot be kept with valid=0.
- minor: `speech_therapy` and `mental_conditions` are the source's constant `no` strings rather than 0/1 booleans; left as in the source.

Run: claude-fable-5-1, 2026-09-10
