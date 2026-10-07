---
tags:
- paradigm:reference-game
- cognitive-modeling:needs-review
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
---
# franke_2024_bayesian

- Paper: https://arxiv.org/abs/2406.09012
- Data source: https://osf.io/f6j3a/?view_only=5e820cc8bbee4549aed58dc252ba61b9
- PDF: https://arxiv.org/pdf/2406.09012.pdf
- Full text: http://arxiv.org/abs/2406.09012
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Franke, M., Tsvilodub, P., & Carcassi, F. (2024). Bayesian Statistical Modeling with Predictors from LLMs. arXiv:2406.09012.

## Experiment summary
Single experiment with 302 native-English Prolific participants who played a text-based reference game. Each trial shows 3 objects (color-shape-texture triples); in the production condition participants choose a word/expression to describe a trigger object, and in the interpretation condition they choose which object a trigger word refers to. Each participant saw 4 items (2 production, 2 interpretation), responding via forced choice with response time recorded (1,208 total trial rows). The paper evaluates how well Bayesian RSA-style models built on LLM (GPT-3.5, LLaMA2) predictions capture the human choice data at item and condition level, adducing computational cognitive modeling.

## Notes

### Columns
| column | description |
|--------|-------------|
| participant_id | Remapped sequential participant identifier (P000..P301), keyed to each unique Prolific submission_id in first-appearance order; Prolific IDs dropped as PII |
| trial | 0..3 within each participant, sequential in source row (presentation) order (derived from trial_nr) |
| item_id | Original 0-indexed stimulus/item index (0..99) from the source `trial` column identifying which reference-game item was shown |
| trial_nr | Original 1-indexed within-participant trial position (1..4) |
| response | The participant's chosen word or referring expression text (verbatim, e.g. "red", "a green circle with dots"); production condition = chosen word, interpretation = chosen object description |
| rt | Response time in milliseconds (raw `responseTime`) |
| condition | Condition label: `production` (choose word for trigger object) or `interpretation` (choose object for trigger word) |
| submission_id | Original per-submission integer identifier from source |
| experiment_duration | Total experiment duration in milliseconds |
| experiment_start_time | Unix timestamp (ms) of experiment start |
| experiment_end_time | Unix timestamp (ms) of experiment end |

The `old` variant of the human data (`data-raw-human-old.csv`) is a strict 201-participant subset and was not separately transformed; the full 302-participant dataset is used here. Both primary behavioral effects reproduce on this CSV: target-word rate is higher in production than interpretation (0.83 vs 0.53), and the target is the modal choice in both conditions. The companion `data-prepped-LLaMA2-*.csv` files (LLM-choice predictions, retained in `raw/`) are used by `analysis.py` to map choice category labels.

## Online experiment

Built `experiments/exp0/` for `exp0.csv`: a static jsPsych v8 rebuild of the reference game. The headless round trip (`?mode=simulate`) passed and the saved CSV matches `exp0.csv`'s schema (same column names and codings; `submission_id` is left blank because it is a Prolific-recruiting artifact, while every behavior/timing column — `rt`, `experiment_start_time`, `experiment_end_time`, `experiment_duration` — is recorded from the browser). `trial` 0..3, `condition` production on trials 0-1 and interpretation on trials 2-3; item content and on-screen wording reproduced verbatim from the paper's original magpie task code. ASSUMPTION: a fresh participant's 4 items are sampled without replacement from the 100-item pool and presented in drawn order (exactly what the source app does with shuffle + slice).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Text-format conversion

Transcribed the single experiment (`exp0.csv`) to natural language: a text-based reference game, so all trial content (three objects, word options, target object / trigger word) is recoverable from the stimulus text and fully textifiable. Both conditions (production and interpretation) are included; no experiment skipped. The per-item stimulus content used for narration was reconstructed from the companion `data-prepped-LLaMA2-*.csv` files (which carry `context_production`/`context_interpretation` and category labels per item) and embedded in `build_jsonl.py`.

**Sample transcript** (participant P000, up to the first marked response):
```
You are playing a conversation game with a friend. On each round you and your friend can both see the same set of three objects, each described as a color, a shape, and a texture. In a PRODUCTION round you are asked to pick a single word to make your friend identify one of the three objects, the target object. In an INTERPRETATION round your friend has picked a single word and you must guess which object your friend is referring to. You answer by typing exactly one of the choices you are shown: on a PRODUCTION round type the exact word you choose; on an INTERPRETATION round type the exact description of the object you choose.
You see three objects: a green hexagon with stripes, a red triangle with stripes, a green triangle with stripes. Make your friend pick the target object, the red triangle with stripes. Word options: red, green, hexagon, triangle. You type [HUMAN_RESPONSE]red[/HUMAN_RESPONSE] …
```
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

Simulated the single experiment with `simulate0.py`, a text-based reference-game simulator format-identical to `transcripts0.jsonl` (verified by a byte-identical round trip through `build_jsonl.py`). Per participant it samples 4 items without replacement from the 100-item pool and presents trials 0-1 as PRODUCTION and trials 2-3 as INTERPRETATION. ASSUMPTION: per-participant item draw and condition placement follow the jsPsych rebuild (README "Online experiment"); the response token is the choice itself, so the mapping is fixed. No experiment skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Indeterminate: The CSV (exp0.csv) stores free-text responses only; the response-category label (target/competitor/distractor) that every model's likelihood requires (RSA item- and condition-level, GPT-3.5 item-level, and all three condition-level aggregations) is not derivable from any column — the dataset's own analysis.py recovers it only from companion raw/ files that are absent from this repo (no raw/ directory present). Additionally, all LLM-based models (Sections 4-6) require per-item LLM scores S_kl (GPT-3.5 text-davinci-003 / LLaMA2 log-probabilities), which are not in the data and came from retired API models. Required columns/variables missing for every result: response category (target/competitor/distractor); LLM scores S_kl.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24
