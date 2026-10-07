---
tags:
- paradigm:compound-interpretation
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---
# gnther_2020_trying

- Paper: https://doi.org/10.1177/1747021820902019
- Data source: https://doi.org/10.6084/m9.figshare.7867772.v1
- PDF: https://osf.io/72szg/download
- Full text: https://europepmc.org/article/PPR/PPR331249
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Günther, F., & Marelli, M. (2020). Trying to make it work: Compositional effects in the processing of compound "nonwords". Quarterly Journal of Experimental Psychology, 73(7), 1082–1091. https://doi.org/10.1177/1747021820902019

## Experiment summary
Two large-scale behavioral studies measured reaction times to hundreds of novel compound nonwords in English. Experiment 1 (N=145) used a timed sensibility judgment task and Experiment 2 (N=146) used a lexical decision task; participants decided whether each novel compound (e.g. "actionlike") was a word/sensible. A fully implemented distributional-semantics computational model quantified each compound's degree of semantic compositionality (modifier/head cosine similarity to the compositional meaning), and RTs were regressed on these model-derived predictors. Both experiments showed slower rejections for more compositional nonwords, with no reliable difference between tasks, indicating automatic compositional processing even when not required. Response type: RT-based sensibility/word-nonword decisions (key C/N).

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original numeric subject ID from the source file (3–6 digits; kept as-is as it is a non-PII numeric ID) |
| trial | 0..249 within each participant_id, numbered in the participant's file-encounter order, which is alphabetical by `comp` because the source file is sorted by stimulus (the source records no presentation/timestamp column, so the randomized true order is not recoverable) |
| comp | The novel compound nonword stimulus presented (string, e.g. "actionlike") |
| rt | Reaction time in milliseconds (raw, incl. extreme/outlier values; one 0 ms value is present in the source) |
| response | Raw key-press response code: 67 = 'C', 78 = 'N'; for these all-nonword trials 'N' = "not a word / not sensible" (correct), 'C' = "word / sensible" (the key pressed) |
| word_validity | Source label for stimulus status; all values "nonword" (novel compound nonword) |
| correct_response | The key the participant was instructed to press for a correct answer; all "n" |
| correct | 0/1 whether the response was correct (1 = pressed 'N'/78) |
| age | Participant age in years as integer |
| gender_raw | Participant self-indicated gender as free text from source (male/female, plus a few glitched numeric cells); not remapped to canonical letters |
| lang | Participant native language; all "english" |
| Handedness | Participant handedness (right/left) |
| mod | The modifier (first constituent) of the compound stimulus |
| head | The head (second constituent) of the compound stimulus |
| famsize_mod | Modifier's morphological family size (integer) |
| famsize_head | Head's family size (integer) |
| as_mod_freq | Frequency of the modifier occurring as a compound modifier (count) |
| mod_free | Frequency of the modifier as a free word (count) |
| as_head_freq | Frequency of the head occurring as a compound head (count) |
| head_free | Frequency of the head as a free word (count) |
| simuv | Cosine similarity between modifier meaning (u) and head meaning (v), 0..1 scatter |
| simuco | Cosine similarity between modifier meaning (u) and compositional compound meaning (co) |
| simvco | Cosine similarity between head meaning (v) and compositional compound meaning (co) |
| length | Compound length in letters (integer) |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Original numeric subject ID from the source file (3–6 digits; kept as-is as it is a non-PII numeric ID) |
| trial | 0..249 within each participant_id, numbered in the participant's file-encounter order, which is alphabetical by `comp` because the source file is sorted by stimulus (the source records no presentation/timestamp column, so the randomized true order is not recoverable) |
| comp | The novel compound nonword stimulus presented (string, e.g. "actionlike") |
| rt | Reaction time in milliseconds (raw, incl. extreme/outlier values; the source carries two 0 ms values and six negative values for participant 210309, kept as-is) |
| response | Raw key-press response code: 67 = 'C', 78 = 'N'; for these all-nonword trials 'N' = "not a word / not sensible" (correct), 'C' = "word / sensible" (the key pressed) |
| word_validity | Source label for stimulus status; all values "nonword" (novel compound nonword) |
| correct_response | The key the participant was instructed to press for a correct answer; all "n" |
| correct | 0/1 whether the response was correct (1 = pressed 'N'/78) |
| age | Participant age in years as integer |
| gender_raw | Participant self-indicated gender as free text from source (male/female, plus a few glitched numeric cells); not remapped to canonical letters |
| lang | Participant native language; all "english" |
| Handedness | Participant handedness (right/left/ambidextrous/both) |
| mod | The modifier (first constituent) of the compound stimulus |
| head | The head (second constituent) of the compound stimulus |
| famsize_mod | Modifier's morphological family size (integer) |
| famsize_head | Head's family size (integer) |
| as_mod_freq | Frequency of the modifier occurring as a compound modifier (count) |
| mod_free | Frequency of the modifier as a free word (count) |
| as_head_freq | Frequency of the head occurring as a compound head (count) |
| head_free | Frequency of the head as a free word (count) |
| simuv | Cosine similarity between modifier meaning (u) and head meaning (v), 0..1 scatter |
| simuco | Cosine similarity between modifier meaning (u) and compositional compound meaning (co) |
| simvco | Cosine similarity between head meaning (v) and compositional compound meaning (co) |
| length | Compound length in letters (integer) |

Both files contain only nonword stimuli (all rejected/word-validity "nonword"); every trial is a rejection decision. `exp0` maps to the paper's Experiment 1 (timed sensibility), `exp1` to Experiment 2 (lexical decision). `response` carries the raw key code (67='C', 78='N'); the correct answer for every nonword trial was 'N' (78).

## Text-format conversion

Both experiments are textifiable: the stimulus is a written letter string (a novel compound such as "actionlike"), which is exactly representable in text, and each trial is a free binary C/N keypress judgment. Transcribed `exp0.csv` (timed sensibility judgment) and `exp1.csv` (lexical decision) into `transcripts0.jsonl` and `transcripts1.jsonl`, one line per participant (145 and 146 transcripts).

Sample transcript (exp0, start up to the first marked response):

```
In this experiment you will be shown novel compound words one at a time, like "actionlike". For each one, judge as quickly as possible whether it has a sensible interpretation (you can build a sensible meaning from its parts). Press the C key if you judge it sensible, or the N key if you judge it not sensible.
You see the compound "actorloss". You press [HUMAN_RESPONSE]N[/HUMAN_RESPONSE] (not sensible), in 784 ms (correct; the correct answer was N (not sensible)). …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`experiments/exp0` (Experiment 1, timed sensibility) and `experiments/exp1`
(Experiment 2, lexical decision) are runnable static jsPsych v8 ports; the
headless `?mode=simulate` round trip passed for both and reproduces the exact
`expN.csv` schema (24 columns, correct codings, `rt` filled, no outbound data
requests). No experiment was skipped. One documented assumption: the paper's
fuller session also interleaved existing (real word) and catch compounds, but
those are absent from the dataset/schema (`word_validity` is always `"nonword"`),
so the experiments present the ~250 novel-compound rejection trials the data
actually contains. See `experiments/README.md`.

## Simulators

Both experiments got a simulator (`simulate0.py`, `simulate1.py`); the
round-trip check through `build_jsonl.py` passed byte-identical for both. Each
simulated participant draws one of the 6 counterbalanced stimulus lists and
judges it item-by-item; the per-comp lexical predictors are taken verbatim from
the dataset. Two assumptions: the paper randomizes presentation order but every
participant on a list in the shipped data shares the canonical sequence, which
the simulators follow; and RTs are simulated log-normally (per-experiment fit),
so `rt` is generated rather than observed. Demographics
(`age`/`gender_raw`/`lang`/`Handedness`) are dropped as a text simulator cannot
produce them. No experiment skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 0, minor 11; fixed 7, open 4).

Checked: paper (10.1177/1747021820902019, author preprint osf.io/72szg), original data (https://doi.org/10.6084/m9.figshare.7867772.v1: nonword_data_TS.txt, nonword_data_LDT.txt, R scripts), exp0-exp1, transform re-run (byte-identical), transcripts (build_jsonl.py rebuild byte-identical), simulators (simulate0.py, simulate1.py run; round trip through build_jsonl.py byte-identical; stimulus lists and predictors match the CSVs verbatim), analysis (analysis.py: all three effects reproduce), citation (Crossref), logs. Skipped: none.

Fixed:
- README rt descriptions now note the source-internal artifacts kept as-is: one 0 ms RT in exp0 (participant 299235) and, in exp1, two 0 ms RTs and six negative RTs (participant 210309, -10784 to -12536 ms); all are in the figshare source and fall under the paper's RT < 100 ms exclusion.
- README trial descriptions and the transform.py comment now say the trial order is the source file order, which is alphabetical by comp (the paper, p. 11, randomized presentation order; the source records no order). Output CSVs unchanged.
- README participant_id: 'Original 6-digit subject number ... coded to a string' corrected; IDs have 3-6 digits and are plain integers.
- README exp0 age: removed the claim of glitched age cells; age is a clean integer (19-72) on every row. The glitch is in gender_raw (one participant per experiment carries a number).
- README summary: 'grammaticality/word-nonword decisions' corrected to 'sensibility/word-nonword decisions'.
- README: added the missing 'Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24' line to the Text-format conversion section (from logs/auto-exp-transcribe.sessions.json).
- README: Columns headings changed from '### expN' to the template's '#### expN'.

Open:
- minor: check_repo flags other dataset names in logs/auto-exp-sim.sessions.json and transcripts/auto-exp-sim.log; they come from a listing of the batch queue inside this dataset's own session (the only session in the file, titled 'Run auto-exp-sim on gnther_2020_trying'), so there is no foreign session to prune.
- minor: column names deviate from the schema (comp instead of stimulus; gender_raw with raw male/female strings instead of gender f/m/na; Handedness capitalized). Documented in the README; left unchanged because the transcripts, simulators and online experiment reproduce this 24-column schema.
- minor: the figshare source ships only the novel-compound trials. Each session also had about 250 existing compounds and 20 catch items (paper p. 10). The complete Experiment 1 data incl. real-word trials is at https://osf.io/7kynq/ (TS_dataset_OSF.txt); no such file exists for Experiment 2. The README discloses the nonword-only content.
- minor: the exp0 transcript and simulator instructions say 'you will be shown novel compound words', which discloses that every item is novel; the real session mixed existing compounds. A consequence of the nonword-only source; documented under Online experiment.

Run: claude-fable-5-1, 2026-09-10
