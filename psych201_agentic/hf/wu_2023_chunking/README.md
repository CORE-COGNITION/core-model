---
tags:
- paradigm:serial-reaction-time-task
- cognitive-modeling:needs-review
- psych-101
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---
# wu_2023_chunking

- Paper: https://doi.org/10.1038/s41598-023-31500-3
- Data source: https://github.com/swu32/experimental_chunking
- PDF: https://www.nature.com/articles/s41598-023-31500-3.pdf
- Full text: https://www.nature.com/articles/s41598-023-31500-3
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Wu, S., Éltető, N., Dasgupta, I., & Schulz, E. (2023). Chunking as a rational solution to the speed–accuracy trade-off in a serial reaction time task. Scientific Reports, 13, 7680. https://doi.org/10.1038/s41598-023-31500-3

## Experiment summary
Two serial reaction time experiments on Amazon Mechanical Turk where participants pressed a key matching an instructed cue on each trial. In Experiment 1 (n=142, 10 blocks) participants were randomly assigned to an independent, size-2, or size-3 chunk condition to study chunk generation, while in Experiment 2 (n=116, 12 blocks) participants were assigned to a fast or accurate instruction condition to study illusory chunks. The research question is whether chunking is a rational solution to the speed–accuracy trade-off, tested by comparing the qualitative predictions of a rational chunking model against behavioral chunking measures (chunky boost, chunkiness, chunk counts from a Gaussian-mixture classification of reaction times, chunk reuse); no model is fit to the trial data. Response is a keypress (D/F/J/K); both response and reaction time (ms) are recorded per trial.

## Notes

### Columns

Both experiments are serial reaction time tasks: on each trial a cue key is shown and the participant presses the corresponding key.

#### exp0 (Experiment 1: chunk generation — independent / size-2 / size-3)

| column | description |
|--------|-------------|
| participant_id | Anonymized participant code (`P000`, `P001`, ... in first-appearance order); replaces the raw source ID (`MturkID`) |
| trial | 0..999 within each participant, across all 10 blocks (0-indexed) |
| block | 0..9, the 100-trial block within the session (blocks 2-7 are training) |
| phase | baseline (blocks 0-1), training (blocks 2-7), test (blocks 8-9) |
| response | The key the participant actually pressed (D/F/J/K) |
| rt | Reaction time in ms (source column `timecollect`) |
| correct | 0/1, whether the pressed key matched the instructed key (source `correctcollect`) |
| condition | Between-subject group: 0=independent, 1=size-3 (ABC), 2=size-2 (AB) |
| keyassignment | JSON list of the 4 instruction keys (the A/B/C/D to key layout) for this participant |
| trialcollect | Trial number 1..100 within the 100-trial block (source column as recorded) |
| trialinstruction | Instruction code; all "n" (normal) in Experiment 1 |
| instructioncollect | The instructed/target key (D/F/J/K) shown on that trial |

Note: exp0 includes one author test session (carried through from the source data as one of the 142 participants).

#### exp1 (Experiment 2: speed vs accuracy — illusory chunks)

| column | description |
|--------|-------------|
| participant_id | Participant number from the source CSV (`id`, 1-based integer) |
| trial | 0..1199 within each participant, across all 12 blocks (0-indexed) |
| block | 0..11, the 100-trial block within the session (blocks 2-7 are training) |
| phase | baseline (0-1), training (2-7), test (8-9), practice (10), instruction (11) |
| response | The key the participant actually pressed (D/F/J/K) |
| rt | Reaction time in ms (source column `timecollect`) |
| correct | 0/1, whether the pressed key matched the instructed key (source `correctcollect`) |
| condition | Between-subject group: 0=fast, 1=accurate |
| keyassignment | JSON list of the 4 instruction keys (the A/B/C/D to key layout) for this participant |
| trialcollect | Trial number 1..100 within the 100-trial block (source column as recorded) |
| trialinstruction | Instruction/phase code: n=normal (baseline/test), a=accurate training, f=fast training, p=practice, i=instruction/free-press |
| instructioncollect | The instructed/target key (D/F/J/K), or O/fp/FreePress special codes in the practice/instruction phases |

### Mapping to paper experiments (exp0/exp1)
`exp0.csv` = Experiment 1, `exp1.csv` = Experiment 2. Source files are `data_exp1.csv` and `data_exp2.csv`, respectively; both are the raw per-trial files carried in full (all blocks/phases). The repo also contains cleaned/filtered/chunk-classified and model-comparison derivatives that were not used as the source of truth. In Experiment 2, the speed–accuracy trade-off reproduces (fast group faster, p=.0005, and less accurate, p=.0001); the Experiments' chunking-metric effects depend on GMM/within-between classification not derivable from the raw columns.

## Update (2026-08-13)
- PII removal: exp0.csv `participant_id` remapped from raw MTurk worker IDs (plus one author test session id) to anonymized codes `P000`, `P001`, ... in first-appearance order (142 participants; all 142,000 rows kept). exp1.csv ids were already plain integers and are unchanged.

CSVs fixed in place from the previous release; transform.py updated to produce the same output
from raw. The previous version remains in the repo's git history.

## Text-format conversion
Both experiments (exp0, exp1) are serial reaction time tasks and were transcribed into natural
language (`transcripts0.jsonl`, `transcripts1.jsonl`). Each trial shows one key cue (D/F/J/K) and
the participant presses a key; the pressed key is the free response, with correctness and reaction
time narrated as feedback. In exp1 the practice/instruction blocks cue no key ("No key is cued")
and the free keypress is still recorded. No experiments were skipped as non-textifiable.

Sample transcript (exp0, participant P000, from the start through the first response):
```
You take part in a serial reaction time experiment. On each trial, one of the four keys D, F, J, or K is displayed as the instruction cue, and you must press the corresponding key on the keyboard. Press D for the key labeled D, F for F, J for J, and K for K. Respond as fast and accurately as possible; your bonus depends on both your reaction time and your accuracy.
The session has 2 baseline blocks, then 6 training blocks, then 2 test blocks; each block has 100 trials. After each trial you see your reaction time and whether you were correct, then the next trial begins after a short interval.

You begin the baseline blocks.

This is the baseline phase.
Trial 1: A D cue is shown. You press [HUMAN_RESPONSE]D[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Indeterminate: the paper's rational chunking model (with the LBA reaction-time simulation) is a normative simulation, not a model fit to participant data. The free speed-accuracy parameter `w` is never estimated from the CSVs; predictions are explicitly qualitative ("our model's predictions were primarily qualitative, and we did not compare across a more extensive set of alternative models", Discussion). The quantitative results (chunky boost, chunkiness, chunk-count, reuse probability, and the RT regression) are descriptive behavioral measures and standard mixed-effects regressions, not formal fitted-model comparisons, so no computational-modeling result is specifiable in this skill's sense.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments got a runnable static jsPsych v8 experiment under `experiments/`
(`exp0/` = Experiment 1, `exp1/` = Experiment 2). The headless `?mode=simulate`
round trip passed for both: the saved CSV reproduces the exact schema, dtypes,
codings, and row counts (1000 rows/participant in exp0, 1200 in exp1), and the
recovered sequence statistics (illusory baseline/test matrix, condition-specific
training matrices, the exp1 free-press position set) match the source data.

The repo carries no `simulateN.py`, so the design, stimulus generators, and
on-screen wording were recovered from the paper (Methods, Fig. 1) and the CSVs.
Key point worth surfacing: the participant is not told their chunk condition in
exp0, and no-cue free-press trials (exp1 practice/instruction blocks) are recorded
as `correct = 1` (the source's practice-block "O" trials show a non-recoverable
~50% correct). Both are cosmetic/auxiliary choices that do not change the
analyzed baseline/training/test blocks or the recorded columns. No experiment was
skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Both experiments got simulators (simulate0.py, simulate1.py) and the round-trip
check through build_jsonl.py passed byte-identically for each. Generators
recovered from the paper (Fig. 1c "illusory" transition matrix; exp0
condition-specific training chunks; exp1 free-press practice/instruction
blocks) reproduce the transcript narration. None skipped. ASSUMPTION: reaction
time is a physical measure a text simulator cannot reproduce, so a plausible
log-normal RT is drawn per trial purely so the narrated feedback reads
naturally; exp1 free-press trials are recorded correct=1 and block 11's code is
written "fp".

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 3, minor 9; fixed 8, open 4).

Checked: paper (https://doi.org/10.1038/s41598-023-31500-3, PDF), original data (https://github.com/swu32/experimental_chunking, data/data_exp1.csv and data/data_exp2.csv), exp0-exp1, transform re-run (byte-identical), transcripts (rebuild byte-identical), simulators (smoke test and round trip through build_jsonl.py), modeling (no model.py; the section, the cognitive-modeling:needs-review tag and the paper's modeling claims agree), analysis (speed-accuracy trade-off reproduces: rt p=.0005, accuracy p=.0001), logs. Skipped: none.

Fixed:
- README citation named Reynolds, te Nijenhuis and Griffiths as co-authors; the paper (p. 1) is by Wu, Éltető, Dasgupta and Schulz. Corrected.
- README Experiment summary said the paper compares rational chunking and PARSER models fit to per-trial reaction times; the paper (Discussion, p. 13) fits no model to the data and compares no alternative models, its predictions are qualitative. Sentence rewritten.
- exp0 transcripts opened with 'Your condition is size-2 (AB)' (or independent / size-3 (ABC)); the paper (p. 7) gives all three groups the same instruction and never discloses the chunk structure, which is what participants learn. Sentence removed from build_jsonl.py, transcripts0.jsonl rebuilt (142 transcripts, exp1 unchanged), simulate0.py aligned, round trip through build_jsonl.py identical; the condition stays in the transcript metadata.
- README heading '### exp0/exp1 mapping to paper experiments' matched the per-experiment heading pattern and hid the exp0 Columns table from the checker; renamed to 'Mapping to paper experiments (exp0/exp1)'.
- Columns headings for exp0 and exp1 used '###'; changed to '####' as in the template.
- '## Text-format conversion' had no Run line; added from transcripts/auto-exp-transcribe.log (deepseek-v4-flash-0731, 2026-08-24).
- '## Modeling reproduction' Run line started with a space and was not recognized; space removed.
- README sample transcript (exp0, P000) did not match transcripts0.jsonl; replaced with the rebuilt transcript's start through the first response.

Open:
- minor: the paper (p. 14) excludes 20 of 142 participants in Experiment 1 (mean RT > 1000 ms or accuracy < 90%) and 26 of 116 in Experiment 2 (13 fast-group participants slower than 750 ms, 10 accurate-group participants below 90% accuracy, 3 failed attention checks). The CSVs keep all 142 and 116 as the source ships them; the source carries no exclusion flag and the attention checks are not in the data, so no valid column was added.
- minor: the paper (p. 11) describes Experiment 2 as 10 blocks of 100 trials; the source ships 2 extra blocks per participant after the test blocks (trialinstruction p: 75 cued and 25 'O' trials; i: 100 fp/FreePress free-press trials), which the source's own analysis file exp2chunkclassified.csv drops. exp1.csv keeps them as phase practice (block 10) and instruction (block 11); their purpose and chronological position are not documented in the paper or the source.
- minor: exp0 transcripts announce the baseline, training and test phases; the paper (p. 7) says the Experiment 1 instructions were identical throughout and does not say participants saw phase labels.
- minor: exp1 transcripts narrate correctness and reaction time on every training trial for both groups; the paper (p. 11) says the fast group got reaction-time feedback and the accurate group correctness feedback during training (the fixation cross colour, p. 2, showed correctness to both).

Run: claude-fable-5-1, 2026-09-13
