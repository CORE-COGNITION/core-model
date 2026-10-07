---
tags:
- paradigm:economic-game
- psych-201
- js-experiment:pass
- text-format:pass
- simulator:pass
- verification:needs-review
---

# heffner_2022_probabilistic

- Paper: https://doi.org/10.1038/s41467-022-29372-8
- Data source: https://github.com/jpheffne/NC_emotion_classify
- PDF: https://www.nature.com/articles/s41467-022-29372-8.pdf
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Heffner, J., Son, J.-Y., & FeldmanHall, O. (2022). A probabilistic map of emotional experiences during competitive social interactions. Nature Communications, 13, 1718.

## Experiment summary
Across three economic games with MTurk participants — Ultimatum Game (exp0, N=715), Prisoner's Dilemma (exp1, N=306), and Public Goods Game (exp2, N=470) — participants rated their emotional state on a valence-arousal affect grid before making a decision each round (UG: accept/punish over 20 rounds; PD: $0–1 contribution over 22 rounds; PGG: $0–1 contribution over 62 rounds, two recorded responses per round). Participants additionally completed a feeling-word (emotion) classification task rating 20 words on the same valence-arousal grid (exp3, N=1491). Classifiers trained on the classification task were then applied to the game ratings to derive probabilistic emotion attributions, revealing that heterogeneous emotions — especially muted high-arousal negative ones like sadness and disappointment — drive punishment, defection, and free riding, rather than anger alone. Response types are discrete accept/punish choices (UG) and continuous contribution ratings (PD, PGG, emotion grid).

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Remapped subject code (original numeric MTurk-industry subject id); `P000`..`P714` in first-appearance order. |
| trial | 0-indexed Ultimatum Game round (0..19); presentation order. |
| response | Income phase decision: 0 = accept, 1 = punish/reject. Already 0-indexed in source. |
| unfairness | Offer unfairness = dollar amount the proposer keeps from the $1 pot (0.50 fair .. 0.95 highly unfair). |
| valence | Affect-grid rating, -250 (unpleasant) .. +250 (pleasant), response to "How do you feel about the Proposer's offer?". |
| arousal | Affect-grid rating, -250 (low) .. +250 (high). |
| study | Experiment tag, always `ug`. |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Remapped subject code; `P000`..`P305` in first-appearance order. |
| trial | 0-indexed Prisoner's Dilemma round (0..21); presentation order. |
| response | Continuous sub_contribution: dollars given to the collective pot, 0.0..1.0 in $0.10 increments. |
| partner_contribution | Partner's contribution to the pot, 0.0 (defect) .. 1.0 (full cooperation). |
| valence | Affect-grid rating, -250..+250, response to "How do you feel about your partner's contribution?". |
| arousal | Affect-grid rating, -250..+250. |
| sub_contribution_binary | `sub_contribution` binarized by the source: `cooperate` (>=0.50), `defect` (<0.50). |
| study | Experiment tag, always `pd`. |

#### exp2
| column | description |
|--------|-------------|
| participant_id | Remapped subject code; `P000`..`P469` in first-appearance order. |
| trial | 0-indexed sequential response counter (0..123) in presentation order. Source recorded two data rows per game round; each row is one response. |
| block | 0-indexed game round (0..61) grouping the two rows of the same Public Goods round. |
| response | Continuous sub_contribution: dollars given to the collective pot, 0.0..1.0 in $0.10 increments. |
| partners_contribution | Collective amount contributed by the three partners, 0.0 (none) .. 3.0 (full $3 total). |
| valence | Affect-grid rating, -250..+250, response to "How do you feel about your partners' contribution?". |
| arousal | Affect-grid rating, -250..+250. |
| sub_contribution_binary | `sub_contribution` binarized by the source: `cooperate` (>=0.50), `defect` (<0.50). |
| study | Experiment tag, always `pgg`. |

#### exp3
| column | description |
|--------|-------------|
| participant_id | Remapped subject code; `P000`..`P1490` in first-appearance order. Same participants appear in the emotional-classification task across all three experiments. |
| trial | 0-indexed feeling-word rating (0..19); presentation order. |
| response | The participant's behavioral rating: the valence coordinate of their affect-grid placement for the shown word, -250..+250. |
| emotion | The feeling word shown that trial (one of 20: neutral, surprised, aroused, peppy, enthusiastic, happy, satisfied, relaxed, calm, sleepy, still, quiet, sluggish, sad, disappointed, disgusted, annoyed, angry, afraid, nervous). |
| valence | Affect-grid valence rating, -250 (unpleasant) .. +250 (pleasant); identical to `response`. |
| arousal | Affect-grid arousal rating, -250 (low) .. +250 (high). |
| study | Origin experiment of the rater: `ug`, `pd`, or `pgg`. |

exp0–exp2 map to the paper's Experiments 1–3 (UG, PD, PGG). exp3 holds the emotion-classification training ratings (the same 1491 participants), which in the paper were used to train classifiers later applied to the game ratings. Trial numbering in exp2 counts each of the two source rows per round as a separate response (0..123), grouped into the 62 game rounds via `block`. The two rows of a round carry independent affect ratings and, in 13154 of the 29140 rounds, different contributions; the paper (p. 9) describes 62 rounds and does not explain the second row. The paper (p. 8) reports that 543 UG participants played as the Responder and 172 as a third party; the source has no role column, so exp0 pools both roles and the transcripts describe every participant as the Responder. The source ships only the final samples; the 329 participants the paper excluded (p. 8) are not in it.

## Online experiment

Added a static jsPsych v8 port for all four tasks: `experiments/exp0` (UG), `experiments/exp1` (PD), `experiments/exp2` (PGG), `experiments/exp3` (emotion classification). The headless `?mode=simulate` round trip passed for each: column names, order, dtypes and row counts match the corresponding `expN.csv` (20 / 22 / 124 / 20 rows per participant). No simulator exists in this repo, so the tasks were built from the paper's Methods and the CSV schema; instruction screens are reconstructed from the paper (no verbatim text available), and `exp2`'s two-rows-per-round encoding is reproduced by carrying the single per-round rating + contribution onto both rows (see `experiments/README.md`). No experiment was skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Added one text simulator per experiment, each format-identical to the corresponding `transcriptsN.jsonl` and passing the round trip through `build_jsonl.py`: `simulate0.py` (UG), `simulate1.py` (PD), `simulate2.py` (PGG), `simulate3.py` (emotion classification). Simulators reproduce the papers' even offer/contribution distributions (each level exactly twice across the rounds) and per-round valence/arousal ratings plus the discrete or continuous choice. ASSUMPTIONS surfaced in the class docstrings: the within-participant presentation order of offers/partner contributions is a random permutation (the paper only specifies the "even distribution"), exp2 emits two rating-plus-contribution responses per round to mirror its 124-row layout, and exp3 assigns each participant a `study` uniformly rather than matching their real economic game. No experiment was skipped.

Fixed 2026-09-15: simulate0-3.py asked the agent with the trial line but without the line break of the final transcript (`prompt + line` vs `prompt + "\n" + line`); the decision-time prompt is now the transcript text up to the open marker (check_calls.py passes).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Text-format conversion

All four experiments (exp0 UG, exp1 PD, exp2 PGG, exp3 emotion classification) were transcribed: offers and contributions are numeric economic choices and the stimuli are feeling words, all expressible in text without changing the task. Each participant's transcript reports their affect-grid valence and arousal ratings and their decision/contribution in order; no experiment was skipped. Below is a sample transcript (exp0, start up to the first response).

```
You will play 20 one-shot rounds of the Ultimatum Game as the Responder. Each round you are paired with a new Proposer who receives $1 and splits it with you: the Proposer keeps part of it and offers you the rest. After you see the offer, On an affect grid you report how you feel by typing two integers: first your valence rating, an integer from -250 (extremely unpleasant) to +250 (extremely pleasant); then your arousal rating, an integer from -250 (very calm) to +250 (very aroused). Then you decide whether to accept the offer (type A) or reject it (type R), in which case neither of you receives anything.
A proposer keeps $0.50 and offers you $0.50. You rate how you feel on the affect grid: valence [HUMAN_RESPONSE]167[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: needs-review (critical 1, major 2, minor 6; fixed 4, open 5).

Checked: paper (10.1038/s41467-022-29372-8, PDF and Supplementary Information), original data (https://github.com/jpheffne/NC_emotion_classify, commit 5ece09e), exp0-exp3, transform re-run (all four CSVs byte-identical), transcripts (build_jsonl.py rebuild), simulators (simulate0-3.py smoke test and round trip through build_jsonl.py), analysis (analysis.py, 3 of 3 effects reproduce), logs. Skipped: modeling (no model.py and no cognitive-modeling tag in this repo).

Fixed:
- critical: build_jsonl.py narrated only the first of the two contributions the source records per Public Goods round (pgg_data.csv has two rows per trial index; the contributions differ in 13154 of 29140 rounds), so about 45% of the recorded contributions were missing from transcripts2.jsonl and each round read as one decision. transcribe_exp2 now narrates every row as a rating plus a contribution; transcripts2.jsonl rebuilt, simulate2.py emits the same two responses per round, the round trip through build_jsonl.py is byte-identical, README Simulators wording updated.
- major: the exp3 instruction said 'report how the word makes you feel' and each trial 'You rate how you feel', but the paper (p. 2, p. 8) has participants place 20 labeled emotion terms on the grid by the term's valence and arousal. build_jsonl.py and simulate3.py now say 'rate the feeling it names' and 'You place the word on the affect grid'; transcripts3.jsonl rebuilt; round trip byte-identical.
- minor: README Columns headings used '### expN' under '### Columns'; changed to '#### expN'.
- minor: README Notes did not mention the 329 excluded participants (paper p. 8), the two Ultimatum Game roles, or that the two exp2 rows per round differ; three sentences added.

Open:
- major: transcripts0.jsonl and simulate0.py tell every participant they play 'as the Responder'; the paper (p. 8) reports 543 Responders and 172 third parties, and ug_data.csv has no role column, so the role cannot be assigned per participant. Documented in the README Notes.
- minor: analysis.py original_effect_size values 0.52 / 0.41 / 0.61 are not the paper's statistics for the tested correlations (0.41 and 0.61 are Cohen's d for sadness-vs-anger paired t-tests on p. 7; 0.52 does not appear in the paper); the reproduced flags do not depend on them.
- minor: check_repo.py flags every transcript because valence, arousal and the decision are each marked as a response (3 marks per CSV row in exp0-exp2, 2 in exp3); this is by design and consistent with the CSVs.
- minor: the paper (p. 8) excluded 329 participants (UG 191, PD 89, PGG 49); the source ships only the final 715 / 306 / 470, so they cannot be kept with valid=0.
- minor: the paper (p. 9) describes 62 Public Goods rounds; the source records 124 responses per participant (each of the 62 trial indices twice, same partners' contribution, independent ratings) and its README calls the PGG '22 trials'. The data is faithful to the source; the second response per round is not explained anywhere.

Run: claude-fable-5-1, 2026-09-10
