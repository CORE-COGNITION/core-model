---
tags:
- paradigm:language-comprehension
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
---

# tsvilodub_2023_role

- Paper: https://journals.linguisticsociety.org/proceedings/index.php/ELM/article/view/5375
- Data source: https://github.com/magpie-ea/magpie-xor-experiment
- PDF: https://journals.linguisticsociety.org/proceedings/index.php/ELM/article/download/5375/5099
- Full text: https://journals.linguisticsociety.org/proceedings/index.php/ELM/article/view/5375
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Tsvilodub, P., van Tiel, B., & Franke, M. (2023). The role of relevance, competence, and priors for scalar inferences. Experiments in Linguistic Meaning, 2, 288–298. https://doi.org/10.3765/elm.2.5375

## Experiment summary
A single web-based rating experiment (N=277; 80 trials per participant including practice, comprehension checks, attention checks, and 32 critical trials) tested whether contextual factors modulate scalar inference strength for 'some' (some→not-all) and 'or' (or→not-both). Participants read vignettes varying speaker relevance, competence, and prior probability (2×2×2×2 within-subjects) and rated the inference on a 0–100 slider. The paper reports that speaker competence positively predicts and prior probability negatively predicts inference strength for both triggers.

## Text-format conversion

All trials of the single experiment (exp0.csv) were transcribed: the practice examples, comprehension checks, relevance/competence/prior context ratings, the critical some/xor inference ratings, and the attention checks. The task is a fully text-based story + statement rating on a 0-100 slider, so no trial is skipped as non-textifiable.

Sample transcript (start through the first marked response):

```
You will be presented with 16 short stories. Read them very carefully, even if they appear repeated and you think you remember them well enough. You will be asked to rate statements about each story. Please indicate, using an adjustable slider from 0 (certainly false) to 100 (certainly true), how likely it is that a statement is true based on what you have read. ... You give your rating as a number from 0 (certainly false) to 100 (certainly true).
Example. Story: Joe went shopping yesterday, while his wife Sue was at home with the kids. He bought flowers for his wife on the way home. Statement: Joe and Sue have no children. How likely is it true? You rate [HUMAN_RESPONSE]0[/HUMAN_RESPONSE].
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Notes

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | Original anonymous subject number from Prolific submission (string) |
| trial | 0..79 within each participant, sequential presentation order |
| response | Scalar inference rating on a 0 (certainly false) to 100 (certainly true) slider |
| age | Participant age in years (1% missing) |
| comments | Free-text comments left by participant at end of study (84% missing) |
| competence | Speaker competence condition (0 = low, 1 = high); NA on non-critical trials |
| condition | Trial type: example (practice), test (comprehension check), critical (experimental), attention_check |
| critical_question | The utterance evaluated on critical some/xor trials; NA on non-critical trials |
| education | Self-reported education level (e.g. "Graduated High School", "Some College") |
| expected | Expected correct response for attention check trials (0, 50, 100); NA otherwise |
| factor_code | Coding of the 2×2×2 (relevance×competence×prior) manipulation as h/l triples (e.g. "hhl"); NA on non-critical trials |
| gender | Participant gender: f, m, other, na |
| item_id | Story vignette identifier (1–64); NA on non-critical rows |
| languages | Self-reported languages spoken |
| optionLeft | Left slider anchor (always "certainly false") |
| optionRight | Right slider anchor (always "certainly true") |
| prior | Prior probability condition (0 = low, 1 = high); NA on non-critical trials |
| prompt | The inference statement rated (scalar inference for some/xor, relevance/competence/prior context for context ratings) |
| question | Question text displayed above the slider |
| relevance | Relevance condition (0 = low, 1 = high); NA on non-critical trials |
| rt | Reaction time in milliseconds |
| story | Full vignette/story text (QUD) |
| test_question | Comprehension check question code (test_true1/2, test_false1/2, test_uncertain1/2, no); NA on non-test rows |
| timeSpent | Total time spent on the experiment in minutes, repeated on every row |
| title | HTML-formatted title displayed on the trial |
| trial_name | Source trial name ('example' for practice, 'main_trials' for all others) |
| trial_number | Original 1-indexed trial number from source (not globally unique per participant — duplicates across blocks) |
| trial_type | Type of rating/block: practice, test_question1–4, rel (relevance rating), comp (competence rating), pri (prior probability rating), some (some-inference), xor (or-inference), attention_check |
| trigger | Logical trigger: 'some' vs 'xor'; NA on practice/comprehension/attention-check trials |

The transform keeps all 277 participants from the source (paper reports N=275 after exclusion of 2 participants who failed attention checks — no exclusions applied here to preserve full raw data). The single experiment (`exp0`) maps to the paper's main experiment. Three separate pilots (`results_58_*`, `results_63_*`, `results_63_*`) are present in the raw directory but excluded from the transform because they used different procedures and stimuli; they are available on the source GitHub repository.

## Online experiment

`experiments/exp0/` is a static jsPsych v8 port of the single rating experiment (built from the paper and the Data-source code, since the repo carries no `simulateN.py`). A session reproduces the source's counterbalancing: 8 items (4 `xor` + 4 `some`, one per factor type) each yielding a comprehension check, a rel/comp/pri context block (2 prior questions for `xor`, 1 for `some`), 3 more comprehension checks and the inference, with 8 attention checks interspersed and 4 practice examples. The headless `?mode=simulate` round trip passed — the built CSV matches `exp0.csv`'s 29 columns, dtypes and codings (0-indexed `trial`, `response` 0–100, `trial_number` restarting per view, `critical_question` only on inference rows, `expected` only on attention checks).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
## Simulators

- `simulate0.py` simulates the single rating experiment (`transcripts0.jsonl` / `exp0.csv`). The round-trip check passed: running a simulated `exp0.csv` through the repo's `build_jsonl.py` reproduces the simulator's prompts byte-for-byte.
- Design follows the source task (`magpie-ea/magpie-xor-experiment`): 4 practice examples first, then 8 item blocks (4 `xor` + 4 `some`, one item per 2x2x2 factor type sampled from the 64-vignette pool) with 8 attention checks shuffled between blocks. Each block = one comprehension check, the rel/comp/pri context ratings in random order (`pri` twice for `xor`, drawn from the item's prior-statement pair), three further comprehension checks (4 of the item's 6 drawn per participant), then the critical inference rating. All trials are 0-100 slider ratings.
- ASSUMPTION: session randomizations are drawn uniformly, matching the marginals observed in `exp0.csv` (all 8 factor codes exactly once per participant, 4 xor + 4 some items, 4 distinct comprehension questions per item, 8 distinct attention checks). The 4th practice example (the only one with an utterance) is fixed to be shown last, as in the source task code. Columns `rt`, the demographics, and `timeSpent` are dropped (not producible by a text simulator).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
