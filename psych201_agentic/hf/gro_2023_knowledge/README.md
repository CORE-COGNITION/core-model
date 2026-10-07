---
tags:
- paradigm:belief-updating
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
---

# gro_2023_knowledge

- Paper: https://doi.org/10.1037/xge0001452
- Data source: https://osf.io/va2jf/ (OSF project "Connecting hindsight bias and seeding effects"; components Experiment 1 https://osf.io/2sbpe, Experiment 2 https://osf.io/jz23n)
- Full text: https://portal.fis.tum.de/en/publications/knowledge-updating-in-real-world-estimation-connecting-hindsight-/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Groß, J., Kreis, B. K., Blank, H., & Pachur, T. (2023). Knowledge updating in real-world estimation: Connecting hindsight bias and seeding effects. Journal of Experimental Psychology: General, 152(11), 3167-3188. https://doi.org/10.1037/xge0001452

## Experiment summary
Participants make numeric population estimates for country names. Experiment 1 (N=208) has OJ (original judgment), ROJ (recall of original judgment), OJnew (new country) and OJagain phases across three between-subject feedback conditions (control/no feedback, concurrent feedback, preceding feedback); feedback moves recalled estimates toward the true population (hindsight bias/seeding), and this skill transfers to new items. Experiment 2 (N=285) uses OJScreen, CJScreen (actual values shown, no judgment), ROJScreen and OJNScreen phases across Control, Feedback, Domain (transfer) and Irrelevant feedback groups with three counterbalanced country sets. Response type is a per-participant per-country typed numeric estimate; the ordering metric is order-of-magnitude error (OME = |log10(estimate) − log10(population)|). The research question links hindsight bias to seeding/knowledge-updating in real-world estimates. Analysis is standard inferential statistics (no formal cognitive modeling).

## Notes

### Columns
### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject ID from source CSV (0-indexed), as string |
| trial | 0..N within each participant_id, in presentation order (phase then sequence) |
| phase | Task phase: `oj` (original judgment), `roj` (recall of original judgment), `ojnew` (new item judgment), `ojagain` (re-judgment) |
| condition | Between-subject feedback group: `control` (no feedback), `concurrent_feedback`, `preceding_feedback` |
| item | Country name (German) the participant estimated |
| sequence | Within-phase presentation order of items, 0-indexed |
| itemtype | 0=control item, 1=experimental (feedback) item |
| response | Participant's numeric population estimate for the item (raw value) |
| population | True population of the country (raw value) |

### exp1
| column | description |
|--------|-------------|
| participant_id | Original subject ID from source CSV, as string |
| trial | 0..N within each participant_id, in recorded (phase-blocked) file order |
| idn | Country number 1-96 identifying one of the 96 countries |
| name | Country name (German) |
| condition | Between-subject group: `control`, `feedback`, `domain`, `irrelevant` |
| phase | Phase: `ojscreen` (judge), `cjscreen` (actual values shown, no judgment — response empty), `rojscreen` (recall of original judgment), `ojnscreen` (new judgment) |
| set_number | Which item set (1, 2, or 3) was presented in this phase |
| counter_balance | Comma-separated order in which the 3 item sets were presented (e.g. "1,3,2") |
| response | Participant's numeric population estimate (empty for CJScreen where no judgment was made) |
| population | True population of the country (raw value) |

Exp0 maps to the paper's Experiment 1 and exp1 to Experiment 2. The `HB_excl_CR` raw files (excluding correct recollections in the ROJ task) were not used; the `HB_all*` all-cases files are the source for both experiments. In exp1, CJScreen rows are legitimate observations where the actual value was shown and no judgment was made, so `response` is intentionally empty there.

## Text-format conversion

Both experiments were transcribed (exp0 -> transcripts0.jsonl, exp1 -> transcripts1.jsonl). The task is fully textifiable: participants type a numeric population estimate for a country name, and feedback items reveal the true population as a number, so no information is lost in text. No experiment was skipped. Sample transcript (exp0, first response):

```
You take part in a study on estimating the populations of countries. For each country name you are shown, you type your best estimate of how many people currently live there, as a plain number (for example 50000000 means 50 million). In this condition you receive no feedback; you never see the true populations.
You are asked to estimate the population of die Niederlande. You type [HUMAN_RESPONSE]50000000[/HUMAN_RESPONSE] …
```

Run: deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments got a runnable static jsPsych v8 build (`experiments/exp0/`, `experiments/exp1/`); no experiment was skipped. The headless round trip (simulation mode) passed for every condition of both experiments — the saved CSV matches each `expN.csv` schema (columns, dtypes, codings, counts: exp0 = 184 rows, exp1 = 96/128 rows). Assumptions recorded as `ASSUMPTION:` comments in each `index.html`: per-participant randomization of which countries are original/new and which originals are experimental (the paper counterbalances across participants), the cosmetic feedback/timing/colors, and the irrelevant group's CJScreen values presented as film budgets. The paper (JEP:G) is paywalled, so participant-facing wording is recovered from the dataset's text format. The visual rendering check was not run (text-only model, no image inspection); the data round trip is what is validated.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Both experiments got a text simulator: `simulate0.py` (Experiment 1) and `simulate1.py` (Experiment 2). The round-trip check through `build_jsonl.py` passed for every condition of both experiments, and the DataFrame schemas match the repo CSVs. No experiment was skipped. `ASSUMPTION:` the per-participant assignment of which countries are original vs new, and which original countries are experimental (receive feedback), is randomized per participant (the paper counterbalances across participants); the response is a free numeric estimate, so the agent's `choice_options` is unconstrained.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25