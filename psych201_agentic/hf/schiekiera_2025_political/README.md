---
tags:
- paradigm:abstract-rating
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
---
# Schiekiera 2025 Political Bias in Historiography

- Paper: https://doi.org/10.12688/f1000research.160170.1
- Data source: https://osf.io/download/6eqwx/ (project DOI https://doi.org/10.17605/OSF.IO/QCDV8)
- PDF: https://f1000research.com/articles/14-320/pdf
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Schiekiera, L., & Niemeyer, N. (2025). Political bias in historiography - an experimental investigation of preferences for publication as a function of political orientation. F1000Research, 14, 320. https://doi.org/10.12688/f1000research.160170.1

## Experiment summary
A single within-subjects experiment (75 participants, 17 trials each) in which participants read research abstracts about political-historical events and judged their likelihood of submission (I/)for publication, using an initial intuitive decision, a Feeling-of-Rightness rating, a considered decision, and a binary rethink response. The key manipulation was the political stance of the abstract (conservative vs progressive), testing whether participants' political orientation biases publication preferences. Response types are scalar likelihood ratings (0-100%), scalar confidence-type ratings (0-6), binary decisions, and reaction times; the research question concerns partisan bias in historiography.

## Notes

### Columns
| column | description |
|--------|-------------|
| participant_id | Original anonymized subject number from source CSV (1..76, 75 participants) |
| trial | 0..67 sequential response index within each participant (4 responses x 17 abstract trials) |
| block | 0..16, 0-indexed abstract/trial group within each participant; groups the 4 response rows of one abstract |
| phase | `test` — all rows are from the main experimental phase (no practice phase recorded) |
| response_type | Which of the 4 responses in the block: `decision1` (initial intuitive ILoS), `for` (Feeling of Rightness), `decision2` (considered CLoS), `rethink` (binary change-of-mind) |
| response | That response's raw value: ILoS/CLoS 0-100 (%), FOR 0-6, rethink 0/1 |
| rt | Reaction time in ms corresponding to that response |
| abstract | 0-indexed-by-paper abstract-pair number 1..17 (kept in source units) |
| treatment | Abstract political stance code: 1 = conservative, -1 = progressive (source coding) |
| treatment_string | Abstract political stance label: `conservative` / `progressive` (source coding) |
| general_topic | Topic of the abstract pair (string) |
| abstract_title | Generated title of the specific abstract shown |
| abstract_text | Full text of the abstract shown |
| stimulus | jsPsych stimulus HTML path, e.g. `text/1b.html_decision1` |
| read1_rt | Reading time (ms) for the first reading screen |
| read2_rt | Reading time (ms) for the second reading screen (NA = missing in source) |
| study_duration_minutes | Total session duration in minutes for that participant |
| decision1_resp | Raw ILoS rating (0-100) for the decision1 response |
| decision1_rt | Raw decision1 reaction time (ms) |
| for_resp | Raw Feeling of Rightness rating (0-6) |
| for_resp_factor | FOR rating shifted to (1-7), i.e. for_resp + 1 |
| for_rt | Raw FOR reaction time (ms) |
| decision2_resp | Raw CLoS rating (0-100) for the decision2 response |
| decision2_rt | Raw decision2 reaction time (ms) |
| rethink_resp | Raw rethink response (0/1) |
| rethink_rt | Raw rethink reaction time (ms) |

Each abstract trial produced 4 genuine responses (decision1, for, decision2, rethink), so each abstract is split into 4 rows grouped by `block`. The primary stance effect (conservative vs progressive abstracts on initial likelihood of submission) reproduces (p < .05). The paper's interaction between abstract stance and participant political orientation could not be tested because political-orientation data was not shared publicly for sensitivity reasons.

## Text-format conversion

`exp0.csv` is textified into `transcripts0.jsonl` (75 transcripts). The task's stimulus is already natural language (research abstracts), and every response is a self-reported rating, so nothing is lost in text. No experiment skipped. The rethink binary (0/1 keep-vs-change) is rendered as a letter token (K/C) fixed in the instructions.

Sample transcript (up to the first free response):

```
You are a historian reviewing papers submitted to your university journal. Because of limited page capacity, you can only accept a certain proportion of the submissions. You will read 17 abstracts written by researchers and decide how likely you would be to submit each for publication, based on the abstract alone. For each abstract you first give an initial, intuitive likelihood (a number from 0 to 100, where 0 means you would definitely not submit it and 100 means you definitely would). Then you rate how certain you felt about that initial judgment on a scale from 0 (very uncertain) to 6 (very certain). After a chance to reconsider, you give a final, considered likelihood from 0 to 100. Finally you decide whether to change your answer, pressing K to keep it as it is or C to change it.
You read an abstract titled "Focus on Chipko (ecofeminists)", reflecting a progressive historical interpretation:
This article examines the cultural reception of the Chipko Movement within 1970s Indian media, focusing on its portrayal as an early ecofeminist movement. The Chipko Movement, known for its mass participation of female villagers, represented a unique confluence of ecological conservation and feminist advocacy. Although freedom of speech was curtailed during the emergency rule of Indira Gandhi, a large amount of media coverage from that time shows how the movement was framed in terms of its innovative approach to combining environmentalism with women's rights, reflecting broader societal shifts towards recognizing the interconnectedness of gender equality and environmental sustainability. The article reveals the critical role of Indian media in shaping public perceptions of ecofeminism during a decade characterized by social discord.
You give your initial intuitive likelihood of submission (0-100): [HUMAN_RESPONSE]18[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`exp0/` got a runnable static jsPsych v8 online experiment (the main abstract-evaluation phase).
The headless round trip passed: the saved CSV matches `exp0.csv`'s schema exactly (26 columns,
68 rows per participant, correct 0-indexed `trial`/`block`, and `response`/FOR/rethink codings),
and the visual rendering check found no gross breakage. The study's consent and instruction
screens are reproduced verbatim; the post-task demographics/BFI-2-S questionnaire is not
logged because it is outside `exp0.csv`'s schema. `read1_rt`/`read2_rt` and
`study_duration_minutes` are now recorded in the browser (the text simulator could not).

Run: openrouter/deepseek/deepseek-v4-flash-vision-exp, 2026-08-25

## Simulators

`exp0` got a text simulator (`simulate0.py`). The round-trip check passed: `build_jsonl.py` on a simulated `exp0.csv` regenerates transcripts byte-identical to the simulator's prompts. ASSUMPTION: the FOR scale is 0-6 (shipped data coding; the paper states 1-7); the 8-conservative/9-progressive assignment and presentation order are randomized per participant. Reaction-time columns and `study_duration_minutes` are dropped (a text simulator cannot produce them).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
