---
tags:
- paradigm:bandit
- cognitive-modeling:fail
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:needs-review
---
# vandendriessche_2022_contextual

- Paper: https://doi.org/10.1017/s0033291722001593
- Data source: https://github.com/hrl-team/Data_depression
- PDF: https://hal.science/hal-04224767/document
- Full text: https://hal.science/hal-04224767
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Vandendriessche, H., Demmou, A., Bavard, S., Yadak, J., Lemogne, C., Mauras, T., & Palminteri, S. (2023). Contextual influence of reinforcement learning performance of depression: evidence for a negativity bias? Psychological Medicine, 53(10), 4696-4706. https://doi.org/10.1017/S0033291722001593

## Experiment summary
In a single experiment (N=56: 26 controls, 30 depressed patients), participants performed a two-armed bandit reinforcement-learning task in two contexts — a "rich" context with positive expected value and a "poor" context with negative expected value — over 2 sessions of 100 trials each, followed by a 112-trial no-feedback transfer (generalization) phase over the same stimuli. On each trial participants made a left/right choice (with response time) and received binary feedback (+1 or -1 point on screen, stored as 1/0). The paper tests whether reinforcement-learning performance depends on the value of the context, reporting reduced learning in the poor context in patients, consistent with a negativity bias at the learning-rate level, and a seeking-vs-avoiding asymmetry in the transfer phase.

## Notes

### Columns

Column descriptions below cover exp0, which contains both the learning and transfer phases for all 56 participants (separated by the `phase` column).

| column | description |
|--------|-------------|
| participant_id | Anonymized subject number as string (source subject number, e.g. `2`). Same participant across both phases. |
| group | `control` / `patient` clinical group, from the codebook in the paper's analysis script. |
| phase | `learning` = training/learning phase (2 sessions x 100 trials); `transfer` = no-feedback transfer/generalization phase (112 trials). |
| trial | 0-indexed trial number in true presentation order within participant (learning session 1, session 2, then transfer), 0..311 per participant. |
| trial_raw | Original trial index from the source `.mat`: 1–100 for learning, 1–112 for transfer. |
| subject_number | Duplicate of the raw source subject number (column 1 of the .mat data matrix). |
| session | Learning-phase task session: `session1` / `session2` (NaN for transfer, which has no session). |
| session_number | Raw session number (1 or 2) from the learning .mat file (column 2). |
| context | Learning-phase contextual condition: `rich` (positive expected value) or `poor` (negative expected value); coded from source column 4 (1=poor, 2=rich). NaN for transfer. |
| context_code | Raw context code: 1 = poor, 2 = rich (source column 4). |
| response | 0 (left) / 1 (right) choice. Schema-standard 2AFC recoding of `choice_raw` (-1->0, 1->1). |
| choice_raw | Raw choice from the source: -1 = left, 1 = right. |
| correct | Learning-phase only: 0 = incorrect, 1 = correct (source column 6). NaN for transfer. |
| rt | Response time in milliseconds. |
| feedback | Learning-phase outcome code (source column 8): 0 = negative outcome (-1 point on screen), 1 = positive outcome (+1 point). NaN for transfer. |
| reward | Equal to `feedback`: the source's 0/1 outcome code (1 = +1 point won, 0 = -1 point lost); the source stores no signed outcome. |
| rt2 | Learning-phase outcome observation time in ms. |
| checktime | Learning-phase timestamp of stimulus onset in ms. |
| checktime2 | Learning-phase timestamp of outcome onset in ms. |
| trial_in_session | 0-indexed trial within each (participant, session): source trial 1–100 recoded to 0–99. NaN for transfer. |
| trial_in_transfer | 0-indexed trial within the transfer phase: source trial 1–112 recoded to 0–111. NaN for learning. |
| symbol_left | Symbol identity (1–8) shown on the left. Transfer phase: source column 3. Learning phase (filled 2026-09-16): derived, see Notes. |
| symbol_right | Symbol identity (1–8) shown on the right. Transfer phase: source column 4. Learning phase (filled 2026-09-16): derived, see Notes. |
| time | Transfer-phase timestamp (ms) of stimulus onset (source column 5). |

R's data comes in MatLab `.mat` files (`Test<S>_Session<1|2>.mat` for the two learning sessions and `PostTraining<S>.mat` for the transfer phase), which required adding `scipy` to the transform's dependencies for parsing. BOTH the learning phase and the transfer phase are included in `exp0.csv`, tagged by `phase`. `response` recodes the raw left/right choice to the schema-standard 0/1; transfer-phase `response` is coded 0=left symbol, 1=right symbol.

Learning-phase symbol identities (added 2026-09-16): the source records no symbol per learning trial, but the transfer ids 1–8 index each session's stimulus list in a fixed order (`stimuliTot` of `PostTraining<S>.mat` = session 1 `stimuli` + session 2 `stimuli`, poor pair first, rich pair second; the `.bmp` names are shuffled image labels), and the authors' `data_depression.Rmd` harmonises 5–8 to 1–4 and 3, 4, 1, 2 to A, B, C, D (reward probabilities 0.9, 0.6, 0.4, 0.1). So the poor pair is (1, 2) in session 1 and (5, 6) in session 2, the rich pair (3, 4) / (7, 8), and the odd id is the better option; `correct` (source column 6) says whether the chosen side held the better option (the `.mat` `gain` schedule reproduces `feedback` under that reading on all 11,200 trials), which fixes the sides. `transform.py` fills `symbol_left` / `symbol_right` for the learning rows this way (exactly 25 left / 25 right per participant, session and context); all other cells of `exp0.csv` are unchanged, `analysis.py` gives the same three effect sizes. Check in the data: participants with learning accuracy >= 0.75 on a pair prefer its odd id in the transfer phase (3 vs 4: 20 of 21, 5 vs 6: 14 of 14, 7 vs 8: 27 of 27).

## Text-format conversion

`exp0.csv` (the only experiment) was transcribed to `transcripts0.jsonl` (56 transcripts, one per participant). The two-armed bandit with abstract symbols, binary left/right choice and +/-1 point feedback is textifiable: the task's information (which symbol is better, learned via feedback) survives verbal description. Responses in both phases are rendered as randomized per-participant letter tokens (A/B for left/right); every trial line names the two symbols on offer (symbol 1–8, see Notes) with their sides and, after the token, the chosen symbol. No experiment was skipped.

Sample transcript (start through the first response):

```
You are playing a computer game and your goal is to earn as many points as possible. On the black screen two abstract symbols appear, side by side. One of the two symbols is the better one and you must learn which it is through trial and error; the reward probability attached to each symbol is never told to you. Here the symbols are called symbol 1 to symbol 8. On each trial press a key to pick the left or the right symbol. Press B to pick the left symbol and A to pick the right symbol. After every choice you get feedback: a green smiley face with '+1 point' means you won that trial, and a red sad face with '-1 point' means you lost that trial. To move to the next trial, press the up key after a win and the down key after a loss. You will do two sessions of 100 trials each. In each session the symbols come in two fixed pairs, and each pair is shown 50 times in a random order.
After the two sessions comes a transfer phase. The eight symbols you saw are now shown to you two at a time, in all pairings, including ones you have not seen together before. For each pair, pick the symbol you think is the more rewarding one, and use your instinct if you are unsure. In the transfer phase you receive no feedback at all.

Options: symbol 4 (left), symbol 3 (right). You press [HUMAN_RESPONSE]B[/HUMAN_RESPONSE] ...
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

Fixed 2026-09-16: the learning-phase lines said only 'Rich context. Two abstract symbols appear.', so neither the symbols nor the side of the better one could be read from the text (the verification's open item), and the rich/poor labels told the reader what participants were never told. `build_jsonl.py` now writes `Options: symbol 4 (left), symbol 3 (right). You press [HUMAN_RESPONSE]B[/HUMAN_RESPONSE] (left: symbol 4). You get +1 point (green smiley).` from the derived `symbol_left` / `symbol_right` (Notes), and the instructions describe two fixed pairs per session instead of rich and poor contexts; transfer lines, response tokens and metadata are unchanged; `transcripts0.jsonl` rebuilt (56 transcripts, 312 responses each).

## Simulators

`simulate0.py` simulates the only experiment (exp0). It reproduces the paper's
generative design (2 sessions x 100 trials, 50 rich + 50 poor per session; reward
probabilities 10%/40% poor and 60%/90% rich; 112-trial no-feedback transfer over
all 8 symbols) and passed the round-trip check through `build_jsonl.py` byte-identically
(56 participants, format-identical transcript text). ASSUMPTION:
learning trial order and transfer pair order are randomized per participant.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

Fixed 2026-09-16: mirrors the new learning lines. The symbol ids follow `exp0.csv` (poor pair (1, 2) / (5, 6), rich pair (3, 4) / (7, 8), odd = better), every learning line names both symbols and their sides, and the better symbol is on the left on exactly 25 of the 50 trials of each context and session, in a random order, as in the data; `correct` and `reward` follow the chosen symbol. Round trip through `build_jsonl.py` byte-identical (4 random-agent participants); decision-time check (`check_calls.py`, 3 participants, 936 calls) passes.

`exp0/` (the only experiment) got a static jsPsych v8 port at `experiments/exp0/`,
built from the paper and the authors' task code (this repo has no `simulate0.py`).
The headless `?mode=simulate` round trip passed: the saved CSV matches `exp0.csv`'s
schema and structure (312 rows/session = 200 learning + 112 transfer; 50/50
rich/poor per session; every ordered symbol pair shown twice). Browser-only timing
columns (`rt`, `rt2`, `checktime`/`checktime2`, `time`) are filled; `group` and
`subject_number` are left blank for an anonymous online participant. ASSUMPTION
(cosmetic/documented): abstract-symbol glyphs, the per-participant A/B key mapping,
and the session/transfer intro screens are browser defaults that do not change the
task or recorded data.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: asymmetric Rescorla-Wagner (separate alpha+ and alpha- learning rates,
logistic temperature), per-participant MAP fit (bounded L-BFGS, weakly-informative
priors) on the transfer-phase choices, Q-values carried through the learning phase.
Reproduced: none.
Not reproduced: learning_rate_asymmetry — fitted learning rates put alpha- > alpha+ for
BOTH groups (controls most negative: mean alpha- - alpha+ = +0.31 controls, +0.10
patients), inverting the paper's claimed control positivity bias; the model is
under-identified for learning-rate valence on this two-armed contextual bandit (the
likelihood surface prefers alpha- > alpha+ even for data generated with alpha+ > alpha-),
so the reported valence-by-group learning-rate direction cannot be recovered faithfully.
Numeric mismatch: paper reports a significant valence-by-group interaction (p=0.007) with
patients more negative and controls positive; the same interaction is significant in our
fit (p~0.03) but with the opposite group direction.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Verification

Verdict: needs-review (critical 1, major 3, minor 6; fixed 4, open 6).

Checked: paper (PsyArXiv preprint of doi:10.1017/S0033291722001593 via https://osf.io/s8bf7/download; the HAL PDF sits behind a bot check and the Cambridge version is not open access), original data (https://github.com/hrl-team/Data_depression, 168 .mat files, 56 participants), exp0, transform re-run (byte-identical), transcripts (rebuild byte-identical), simulator (smoke test and round trip, 3/3 exact), modeling section and tag against the paper (no model.py), analysis (3/3 effects reproduce), logs. Skipped: model.py re-run (the repo ships no model.py: cognitive-modeling:fail uploads none; the section's paper claims were checked against the preprint, p135/p38, and agree).

Fixed:
- critical: transcripts0.jsonl marked transfer choices as 'symbol N', which does not map one-to-one onto response 0/1 (56/56 transcripts). build_jsonl.py now writes the left/right letter token and names the chosen symbol after it; transcripts0.jsonl regenerated (rebuild byte-identical); simulate0.py mirrored (round trip 3/3 exact).
- major: README said feedback was 0/1 points. The paper (preprint p73) shows '+1pts' / '-1pts' on screen and the .mat 'points' equals wins minus losses; the source stores a 0/1 code. Summary, 'feedback' and 'reward' rows corrected.
- minor: simulate0.py built the transfer pairs as combinations x 4, so the larger symbol index was never on the left; the data show each ordered pair twice per participant. Fixed to each ordered pair twice.
- minor: README and simulate0.py said the better symbol's side is 'not recoverable from the paper or data'; it follows from correct x response (exactly 25 left / 25 right per context and session). Reworded to 'not narrated in the transcript'.

Open:
- major: logs/auto-exp-modeling.sessions.json carries, in the first message's summary.diffs, four file diffs from another job (SLURM 39826947: vantiel_2022_meaning README.md, exp0.csv, exp1.csv, paper.html). Pruning was denied by the run's permission classifier; remove them by hand.
- major: the learning-phase transcript never names the symbols (only 'Rich context' / 'Poor context'), while the transfer phase names symbols 1-8 that were never introduced, so transfer choices cannot be predicted from the text; the rich/poor labels also tell the reader the contexts' expected value, which participants were not told (preprint p69). The pairs are recoverable from the source ('stimuli' lists in the .mat files plus the Rmd harmonization: session 1 poor = symbols 1,2 (better 1), rich = 3,4 (better 3); session 2 poor = 5,6 (better 5), rich = 7,8 (better 7); the better symbol's side follows from correct x response). Re-transcribing is a design change left to a human.
- minor: check_repo flags -1 in choice_raw as a sentinel; it is the source's documented left code (-1 left / 1 right), valued on all 17472 rows and bijective with response. Kept as a raw column.
- minor: check_repo flags '100 trials' in the instructions against 312 rows per participant; the text says two sessions of 100 trials plus a transfer phase (200 + 112 = 312) and is correct.
- minor: the paper's Figure 1 caption (p266) mentions a 16-trial practice with letter stimuli; the source ships no practice data.
- minor (note): the source's data_depression.Rmd defines transfer 'correct' with the choice sign inverted relative to its own README (-1 = left), giving 0.39 accuracy; analysis.py uses the coding consistent with the paper (0.61 accuracy, patients seek A 0.73 vs avoid D 0.50, controls 0.63 vs 0.63). exp0.csv follows the source README, confirmed by symbol choice rates (A 67%, D 40%).

Run: claude-fable-5-1, 2026-09-13
