---
tags:
- paradigm:belief-updating
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
---
# burton_2022_optimism

- Paper: https://doi.org/10.1016/j.cognition.2021.104939
- Data source: https://osf.io/8q74m
- PDF: https://eprints.bbk.ac.uk/id/eprint/46927/5/46927.pdf
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Burton, J. W., Harris, A. J. L., Shah, P., & Hahn, U. (2022). Optimism where there is none: Asymmetric belief updating observed with valence-neutral life events. Cognition, 218, 104939.

## Experiment summary
Four preregistered studies use the classic belief-updating paradigm with valence-neutral life events. In each trial participants first estimate the probability an event will occur (E1), receive a base rate (BR), re-estimate (E2), and rate the event's valence. The studies test whether asymmetric (optimism-like) belief updating persists even for neutral events, finding that apparent asymmetries are unreliable and largely attributable to statistical artefacts rather than motivation. N per experiment: 100 (Study 1), 100 (Study 2), 100 (Study 3), 200 (Study 4). Responses are probability estimates (0-100) and valence ratings (1-5). Each event is split into four rows (he initial estimate, eBR base-rate estimate, E2 revised estimate, valence rating), grouped by block, with the presented base rate carried as a column.

## Notes

### Columns
### exp0
| column | description |
|--------|-------------|
| participant_id | Original study-internal participant number (1-100), stringified. Study 1. |
| trial | 0-indexed sequential response counter within participant (0..203). |
| block | 0-indexed event/trial id (0..50); 4 responses per block. |
| phase | Which response within the event: `e1` initial probability estimate, `ebr` base-rate estimate, `e2` revised estimate, `valence` valence rating. |
| response | The participant's value for that phase: E1/eBR/E2 = probability estimate 0-100; valence = 1-5 Likert (1=extremely negative .. 5=extremely positive). |
| E1 | Initial probability estimate (0-100). |
| eBR | Participant's estimate of the base rate (0-100). |
| BR | Presented base rate statistic (11-82). |
| E2 | Revised probability estimate (0-100). |
| Valence | Valence rating 1-5 (1=extremely negative, 2=somewhat negative, 3=neither, 4=somewhat positive, 5=extremely positive). |

### exp1
Same columns and coding as exp0, but `participant_id` is the Study 2 participant number (1-100).

### exp2
Same columns and coding as exp0, but `participant_id` is the Study 3 participant number (1-100).

### exp3
| column | description |
|--------|-------------|
| participant_id | Original study-internal participant number (1-200), stringified. Study 4. |
| trial | 0-indexed sequential response counter within participant (0..79). |
| block | 0-indexed event/trial id (0..19); 4 responses per block. |
| phase | Which response within the event: `e1`, `ebr`, `e2`, `valence`. |
| response | The participant's value for that phase: E1/eBR/E2 = probability estimate 0-100; valence = 1-5 Likert (1=extremely negative .. 5=extremely positive). |
| E1 | Initial probability estimate (0-100). |
| eBR | Participant's estimate of the base rate (0-100). |
| BR | Presented base rate statistic (11-78). |
| E2 | Revised probability estimate (0-100). |
| Valence | Valence rating 1-5 (source column `val`). |

The four `expN.csv` files map to the paper's Study 1-4 (exp0 -> Study 1, exp1 -> Study 2, exp2 -> Study 3, exp3 -> Study 4). The source `agg-data.csv` (aggregated across studies) was skipped as a meta file; all per-studiment trial-level data is carried in the four per-study CSVs.

## Text-format conversion

All four experiments (Studies 1-4, exp0-exp3) were transcribed (`transcripts0-3.jsonl`, one transcript per participant). They all use the classic belief-updating ("update method") paradigm with valence-neutral life events: participants read a life event, estimate its probability for themselves (E1) and for the average person (eBR) on a 0-100 scale, are shown the base rate, re-estimate (E2), and rate the event's valence on a 1-5 Likert scale. All stimuli are natural-language life events and all responses are numeric, so no perceptual information is lost in text. No experiment was skipped.

Notes on reconstruction: the CSVs record each event's four responses in event-ID order (block = event ID - 1, mapping to SI Table S1), so transcripts narrate events in that order — the original presentation order within each part was randomized per participant and is not recorded. Each event's responses appear in chronological within-event order (E1, eBR, base rate shown, E2, valence; Study 3 rates valence before E2, and Studies 1/2/4 collect E2 and valence in separate parts). The E1/eBR question order was counterbalanced between subjects but is not recorded, so E1 is narrated first. The forced base-rate recall (type the base rate back) is not recorded in the data and appears in the instructions only. Base rates are taken from the data's BR column, which is what participants actually saw (e.g. event 6's mistakenly presented 29%).

Sample transcript (Study 1, exp0, participant 1):

```text
You are taking part in a study about how people estimate the likelihood of everyday life events. You will be presented with 51 life events, one at a time in random order. For each event you are asked two questions (in random order): 'Please estimate how likely this event is to happen to you' and 'Please estimate how likely this event is to happen to the average person.' Answer each by typing a whole number from 0 to 100, your percentage estimate. You are then shown the base rate, the actual percentage of people the event happens to, and asked to type that number back correctly. After seeing the base rate you re-estimate how likely this event is to happen to you personally, again typing a whole number from 0 to 100. After all 51 events are completed, each event is shown again in random order and you are asked 'How would you feel about experiencing this event?' Answer with a whole number from 1 to 5, where 1 = extremely negative, 2 = somewhat negative, 3 = neither positive nor negative, 4 = somewhat positive, 5 = extremely positive. For every question, enter just the number.
Event: Be exactly the same weight in 10 years' time. You estimate how likely this event is to happen to you: [HUMAN_RESPONSE]10[/HUMAN_RESPONSE] ...
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

All four experiments got a text simulator (`simulate0.py`-`simulate3.py`, Study 1-4). Each generates format-identical participant text to the repo's transcripts0-3.jsonl — the round-trip check through `build_jsonl.py` passes byte-identically for all four. The simulations keep the paper's generative design: the 51 (Study 4: 20) life-event stimuli and their presented base rates (BR column) are fixed material, and the free numeric responses E1/eBR/E2 (0-100) and valence (1-5) are the agent's choices. No experiment skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

All four experiments got a static, browser-run port (`experiments/exp0/`-`exp3/`,
Study 1-4), built from the simulators/transcripts in a jsPsych v8 online
experiment. The headless `?mode=simulate` round trip passed for all four: the
saved CSV reproduces the matching `expN.csv` schema exactly (same columns,
dtypes, running `trial` counter, four-row-per-event structure, `response` =
phase-column equivalence). See `experiments/README.md` for how to run and wire a
backend. No experiment skipped. ASSUMPTION: the base-rate recall ("write the base
rate back correctly") is in the instructions and the paper but is not recorded or
narrated, so the browser shows the base rate and logs no recall response; the
study's `parts` are presented as per-event contiguous narration as the
transcripts do.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
