---
tags:
- paradigm:lexical-production
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
---
# pugacheva_2024_lexical

- Paper: https://doi.org/10.1016/j.jml.2023.104477
- Data source: https://osf.io/4xn83
- PDF: https://files.osf.io/v1/resources/7x8sb/providers/osfstorage/64ab12d519252701f7c7a517
- Full text: https://psyarxiv.com/7x8sb
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Pugacheva, V., & Günther, F. (2024). Lexical choice and word formation in a taboo game paradigm. Journal of Memory and Language, 135, 104477. https://doi.org/10.1016/j.jml.2023.104477

## Experiment summary
Three experiments on word choice and coining in a taboo-game paradigm. In Exps 1-2, participants produced a single-word substitute (single-word substitutions) for target words, potentially coining novel compounds; Exp 2 varied the instruction (generic vs semantic-relate cues: existing-word, novel-compound, or completely-novel blocks). 199 participants in Exp 1 and 194 in Exp 2, each responding to ~48 target words with free-text words. In Exp 3 (377 participants), new participants saw prior responses and made 3 guesses each of the original target and rated how well the word substitutes it, testing how guessable / well-matched speakers' chosen or coined words are. Analyses relate produced responses (existing vs novel) to semantic distance from targets via distributional semantic models (fastText).

## Notes

**All-empty columns dropped (2026-08-25).** `anything_weird` in exp2.csv (the source "anything weird?" free-text field) was empty for every row and has been removed.

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | Remapped participant ID (P000..P198) in first-appearance order; source held 24-char hex Prolific-style IDs which are dropped as PII |
| trial | 0..47 within each participant_id (48 target words, in source order) |
| stimulus | The target word the participant had to produce a one-word substitute for |
| response | The participant's produced word (free-text) |
| cosine | fastText cosine similarity between response vector and target vector |
| existence | Response classification: existing / novel / compl_novel (source's coding) |
| rank | fastText neighbourhood rank of the response relative to the target |
| centroid | Semantic-space centroid/neighbourhood summary value from the model |

### exp1
| column | description |
|--------|-------------|
| participant_id | Remapped participant ID (P000..P193) in first-appearance order; source 24-char hex Prolific-style IDs dropped as PII |
| trial | 0..N within each participant_id (target words in source order) |
| stimulus | The target word the participant had to produce a one-word substitute for |
| response | The participant's produced word (free-text) |
| instruction_type | Source instruction code (0,1,2) naming which word type block to produce |
| condition | Symbolic label of instruction_type: existing_word / novel_compound / completely_novel |
| count | Frequency count of how many participants produced this exact response |
| cosine | fastText cosine similarity between response and target |
| rank | fastText neighbourhood rank of the response |
| existence | Response classification: novel compounds / existing / completely novel (source coding) |
| centroid | Semantic-space centroid value from the model |

### exp2
| column | description |
|--------|-------------|
| participant_id | Source per-participant data filename (e.g. taboogame_reverse_105013.csv); kept verbatim, not a platform ID |
| block | 0..25 within each participant_id, one value per paper-trial (26 trials); the 3 guess-responses of a trial share a block |
| trial | 0..77 within each participant_id; counts responses (3 guesses x 26 trials) sequentially |
| stimulus | The produced word (from Exp 1/2) shown to the participant |
| existence | Classification of the stimulus word: existing / novel compound / completely novel |
| original_target | The actual original target word participants were trying to guess |
| response | One of the participant's 3 free-text guesses of the original target |
| gender | Participant gender recoded to f / m / nb (source used female/male/nonbinary plus typos) |
| age | Participant age in years |
| language | Self-reported language (source values, e.g. english) |
| use_data | Source consent flag (yes; empty where unrecorded) |
| rating | Fit rating 0-100 (slider) of how well the stimulus substitutes the original target; trial-level, repeated per block |
| correct_guess | 0/1 whether any of the 3 guesses exactly matched original_target; trial-level, repeated per block |

For Exps 1-2 the fastText data file was used as the source (over the dissect variant), because dissect drops completely-novel responses not representable in the w2v+CAOSS space while fastText keeps every behavioral trial. exp0 maps to the paper's Experiment 1, exp1 to Experiment 2, exp2 to Experiment 3.

## Text-format conversion

All three experiments were transcribed into natural language, since each is a text-based word (producing or guessing single words, plus a numeric fit rating): exp0 (Experiment 1, free single-word substitutes), exp1 (Experiment 2, instructed word-type substitutes), and exp2 (Experiment 3, guessing original words and rating fit). No experiment was skipped.

Sample transcript (exp0, participant P000), from the start up to and including the first free response:

```
You will be shown different single words one at a time. Your task is to come up with a single-word substitute for each one, so that other people can later identify the original word from your answer. You must refer to the given word without using that word itself, and you may not use any word that contains it. You may give an existing word or coin a novel one. Type exactly one word (letters only, with a hyphen allowed for compounds); do not use spaces or punctuation.
You see the target word "epic". You need a single-word substitute. You type [HUMAN_RESPONSE]awesome[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

Simulators were written for all three experiments (`simulate0.py`, `simulate1.py`, `simulate2.py`); each passes the round-trip check against `build_jsonl.py` (byte-identical text). `simulate1.py` follows the data's empirical instruction mix (~41% existing / ~54% novel compound / ~5% completely novel per participant) rather than the paper's stated 16/16/16 Latin-square blocks, and `simulate2.py` drops demographics (fresh `taboogame_reverse_<6digits>.csv` participant filenames).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

All three experiments got a buildable `experiments/expN/` (`experiments/exp0`, `experiments/exp1`, `experiments/exp2`); the headless round trip passed for each (schema subset, dtypes, and row counts match the shipped CSVs). No experiment was skipped. Because a browser cannot compute the fastText model outputs, `exp0`/`exp1` omit `cosine`/`existence`/`rank`/`centroid` (and `exp1` also `count`), and `exp2` omits the demographics (`gender`, `age`, `language`, `use_data`, `anything_weird`) that `simulate2.py` also drops; the browser reproduces the remaining schema columns exactly. `exp1` draws `instruction_type` from the empirical marginal (0.41/0.54/0.05) per `simulate1.py`, not the paper's 16/16/16 blocks; a participant is assigned one stimulus set at random in all three, and 0-100 rating uses the slider. Presentation cosmetics (colors, 400 ms ITI, layout) are browser defaults.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
