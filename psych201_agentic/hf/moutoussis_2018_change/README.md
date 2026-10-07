---
tags:
- paradigm:go-nogo
- cognitive-modeling:needs-review
- psych-201
- js-experiment:pass
- text-format:pass
- simulator:pass
- verification:needs-review
---

# moutoussis_2018_change

- Paper: https://doi.org/10.1371/journal.pcbi.1006679
- Data source: https://figshare.com/articles/dataset/Change_stability_and_instability_in_the_Pavlovian_guidance_of_behaviour_from_adolescence_to_young_adulthood/7537757
- PDF: https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1006679&type=printable
- Full text: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1006679
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Moutoussis, M., Bullmore, E. T., Goodyer, I. M., Fonagy, P., Jones, P. B., Dolan, R. J., Dayan, P., & on behalf of The Neuroscience in Psychiatry Network Research Consortium. (2018). Change, stability, and instability in the Pavlovian guidance of behaviour from adolescence to young adulthood. PLOS Computational Biology, 14(12), e1006679. https://doi.org/10.1371/journal.pcbi.1006679

## Experiment summary
Participants aged 14-24 (exp0 N=817, exp1 N=556) performed a Go-NoGo task with 144 trials across 4 conditions (Win-Go, Win-NoGo, Lose-Go, Lose-NoGo), requiring Go/NoGo responses to fractal cues for monetary win / null / loss outcomes (the paper states no per-trial amount). The study examined whether Pavlovian biases (action/valence congruency effects) act as stable traits or change during adolescence, using a longitudinal design with baseline and ~18-month follow-up sessions; the 6-month short follow-up session of 61 participants is included in exp0 as task_id = 1 (session = short_follow_up).

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Source participant code: the 5-digit NSPN number that starts each .mat file name (the paper's fit code uses it as the ID); the same code identifies a person in exp0 and exp1 |
| trial | 0-indexed trial number (0-143), restarts per (participant_id, task_id) |
| task_id | 0-indexed run counter: 0 = baseline run, 1 = the 6-month short follow-up run of the 61 participants in S2 Data |
| session | Data-collection wave: baseline (S1 Data) or short_follow_up (S2 Data, 153-247 days after baseline) |
| condition_code | Source cue code: 1=Go-to-Win, 2=Go-to-Avoid-Loss, 3=NoGo-to-Win, 4=NoGo-to-Avoid-Loss (S4 Data ll*.m: codes 1 and 3 are win-context cues, codes 1 and 2 are Go-correct cues) |
| condition | Snake_case label for the cue type: win_go, win_nogo, lose_go, lose_nogo |
| cue_onset_time | Time (ms since task start) when the fractal cue appeared |
| response_cue1 | 1 if a response occurred during the cue phase (premature), else 0 |
| cue_target_interval | Wait interval (ms, uniform 250-3500) between the cue and the target (Fig 1A) |
| target_onset_time | Time (s since task start) when the target appeared |
| response_cue2 | Always 0 (unused column) |
| sham | Always 0 (unused placeholder column) |
| target_position | Always 1 (single target at a fixed position) |
| key_pressed | Raw key code: 0 = no press, 71 = the Go key; a few NoGo trials (148 in exp0, 61 in exp1) record another key code without a timed press |
| keypress_time | Time (ms since task start) of the Go key press, 0 if none; rt = keypress_time - 1000 * target_onset_time |
| rt | Reaction time in ms from target onset; 0 = NoGo (no press). One exp0 trial holds the source value -1, which the paper's fit code counts as a Go |
| response_raw | Source response code: 0 = no press, 1 = press within 700 ms, 3 = late press (RT 700-817 ms), which the task scored as a wrong response; the paper's fit code counts code 3 as Go |
| target_display_duration | Fixed target display duration (800 ms) |
| outcome_onset_time | Time (ms since task start) when the outcome was shown |
| intertrial_interval | Inter-trial interval (ms, 250-500) |
| reward | Outcome: -1 = loss, 0 = null, 1 = win (source column 17; the paper states no per-trial amount) |
| valid | 1=usable trial, 0=invalid response (source response_raw == 3) |
| response | 0=NoGo (RT == 0), 1=Go (RT > 0) |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Source participant code: the 5-digit NSPN number that starts each .mat file name (the paper's fit code uses it as the ID); the same code identifies a person in exp0 and exp1 |
| trial | 0-indexed trial number (0-143), restarts per (participant_id, task_id) |
| task_id | 0-indexed run counter (0 for all but participant 38943, whose two follow-up runs on the same day are task_id 0 and 1) |
| session | Data-collection wave: long_follow_up (S3 Data, ~18 months after baseline) for every row |
| condition_code | Source cue code: 1=Go-to-Win, 2=Go-to-Avoid-Loss, 3=NoGo-to-Win, 4=NoGo-to-Avoid-Loss (S4 Data ll*.m: codes 1 and 3 are win-context cues, codes 1 and 2 are Go-correct cues) |
| condition | Snake_case label for the cue type: win_go, win_nogo, lose_go, lose_nogo |
| cue_onset_time | Time (ms since task start) when the fractal cue appeared |
| response_cue1 | 1 if a response occurred during the cue phase (premature), else 0 |
| cue_target_interval | Wait interval (ms, uniform 250-3500) between the cue and the target (Fig 1A) |
| target_onset_time | Time (s since task start) when the target appeared |
| response_cue2 | Always 0 (unused column) |
| sham | Always 0 (unused placeholder column) |
| target_position | Always 1 (single target at a fixed position) |
| key_pressed | Raw key code: 0 = no press, 71 = the Go key; a few NoGo trials (148 in exp0, 61 in exp1) record another key code without a timed press |
| keypress_time | Time (ms since task start) of the Go key press, 0 if none; rt = keypress_time - 1000 * target_onset_time |
| rt | Reaction time in ms from target onset; 0 = NoGo (no press). One exp0 trial holds the source value -1, which the paper's fit code counts as a Go |
| response_raw | Source response code: 0 = no press, 1 = press within 700 ms, 3 = late press (RT 700-817 ms), which the task scored as a wrong response; the paper's fit code counts code 3 as Go |
| target_display_duration | Fixed target display duration (800 ms) |
| outcome_onset_time | Time (ms since task start) when the outcome was shown |
| intertrial_interval | Inter-trial interval (ms, 250-500) |
| reward | Outcome: -1 = loss, 0 = null, 1 = win (source column 17; the paper states no per-trial amount) |
| valid | 1=usable trial, 0=invalid response (source response_raw == 3) |
| response | 0=NoGo (RT == 0), 1=Go (RT > 0) |

exp0 holds the baseline session (S1 Data, 817 participants) and, as task_id = 1, the 6-month short follow-up session (S2 Data) of 61 of them; exp1 holds the long (~18-month) follow-up session (S3 Data, 556 participants; the paper's Methods count 557 follow-up datasets, 542 of good quality). participant_id links the waves: 554 of the 556 exp1 participants also have a baseline run in exp0 (41517 and 48231 do not). The source does not document the response_cue1 flag; "premature press during the cue" is the transform's reading of it.

## Text-format conversion

Both experiments (exp0, exp1) are textifiable Go-NoGo learning tasks: the four abstract fractal cues are labeled cue A-D, and each trial is narrated as the cue shown, the participant's Go (G) / NoGo (N) press, and the win / null / loss outcome. Both transcribed with `build_jsonl.py`; no experiments skipped.

Sample transcript (first response):

```
You are playing a game for real money. On each trial you see one of four abstract fractal patterns (cue A, cue B, cue C or cue D) on screen, then a target appears shortly afterwards. Your job is to decide whether to press the button (Go) or to withhold the press (NoGo). Each cue has a fixed, unknown rule about whether pressing is better, so you must learn the rules by trial and error as the game goes on; the right answers gradually sink in. The outcome probabilities are 80% and 20%, and you can win or lose money. To choose Go (press the button), type G. To choose NoGo (do not press), type N. After your choice you see the outcome.
Task 1.
You see cue C. You press [HUMAN_RESPONSE]G[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Both experiments (exp0, exp1) got a text simulator (`simulate0.py`, `simulate1.py`); the round-trip check through `build_jsonl.py` passed byte-identically for each. Each simulator recovers the Go-NoGo generative process: a uniform permutation of 36 trials per condition per 144-trial run, the 0.8/0.2 outcome contingency per condition (following the paper's Go/NoGo condition naming), and the empirical premature-press and second-run rates.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Online experiment

Both experiments (`experiments/exp0/`, `experiments/exp1/`) are built as static jsPsych v8
Go-NoGo tasks. Each headless `?mode=simulate` round trip passed (schema, dtypes, codings
and the 144-trial / 4-condition counts all match), and the real-mode screens render
cleanly. The 0.8/0.2 reward contingency and the condition→correct-action mapping were
recovered from the data (the data's label↔action mapping differs from the paper's standard
Go/NoGo naming); instructions were reconstructed from the paper (it quotes no verbatim
text). See `experiments/README.md` for the full list of cosmetic/source-gap assumptions.

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: valued-learning vs valued-sensitivity Go/NoGo RL models; per-participant bounded L-BFGS-B MLE (4 restarts), compared on summed per-participant BIC (an approximation of the paper's hierarchical-EM integrated BIC).
Reproduced: none.
Not reproduced: valued_learning_model_wins (the valued-sensitivity model has the lower summed BIC at both waves at N=100).
Numeric mismatch: the paper reports the valued-learning model ahead by 255.7 (baseline, N=817) / 275.6 (follow-up, N=556) iBIC units, a per-participant advantage of only 0.15 units (paired Wilcoxon p = 0.09 at baseline) from a hierarchical EM fit with group priors; model.py's unregularised per-participant fits (93-98% of them at a parameter bound) put the valued-sensitivity model ahead by ~404 (exp0) / ~235 (exp1) summed-BIC units at N=100, so this method does not resolve the paper's margin. An earlier run reported the paper's winner (~442 / ~268 units), but that used the swapped cue codes 2 and 3 of the original transform.py.
Partial validation: N=100 (the full-N fit exceeded the compute budget).
Indeterminate: longitudinal claims (Pavlovian-bias change over session, temporal stability, latent-change-score) are not tested by model.py, which fits each wave independently; participant_id (the source NSPN code) links baseline and follow-up, but no age/IQ/mood columns exist, so the external-validity claims (IQ, age, MFQ) cannot be tested.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-26

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: needs-review (critical 1, major 7, minor 9; fixed 13, open 4).

Checked: paper (10.1371/journal.pcbi.1006679, PDF), original data (figshare 7537757, S1-S4 Data), exp0-exp1, transform re-run (byte-identical to the uploaded CSVs), transcripts (build_jsonl.py rebuild byte-identical), simulators (smoke test and round trip through build_jsonl.py), modeling (model.py at N=100 per wave), analysis, logs. Skipped: model.py at full N (partial: 100 participants per wave; the full-N fit exceeded the compute budget).

Fixed:
- critical: transform.py mapped cue code 2 to win_nogo and 3 to lose_go; the source fit code (S4 Data ll*.m: rho = sum(ss==[1 3]) marks win cues, go = ss<3 marks Go cues) and the outcomes in the data (code 2 yields only 0/-1, code 3 only 0/+1) give 2 = lose_go and 3 = win_nogo. COND_MAP fixed, exp0.csv and exp1.csv regenerated, transcripts rebuilt, simulators relabelled, README and analysis inputs corrected (congruency effect 0.146/0.108 instead of the inflated 0.380/0.456).
- major: participant_id was renumbered P000.. per file, which dropped the 5-digit NSPN codes in the .mat file names that the paper's fit code uses as IDs; the codes now serve as participant_id and link 554 of the 556 exp1 participants to their exp0 baseline run.
- major: exp0 task_id = 1 rows come from S2 Data, the 6-month short follow-up session (file dates 153-247 days after baseline), not from 'multiple baseline sessions'; a session column (baseline / short_follow_up / long_follow_up) was added by transform.py and the README corrected.
- major: transcripts0/1.jsonl and simulate0/1.py were present without the text-format:pass and simulator:pass tags and without their README sections; the transcribe and sim logs show both were set and then overwritten by the concurrent modeling run. Tags and sections restored.
- major: transcripts and simulators said 'you can win or lose 20 pence' and 'You win 20p.'; the paper, Fig 1 and S1-S16 state no per-trial amount (only 'real money', about five pounds for excellent performance). Wording made amount-free in build_jsonl.py and both simulators; transcripts rebuilt, round trip re-passed.
- major: model.py deviated from Eq 3 and the source ll*.m: the go bias was multiplied by the valence sensitivity rho_v and the go_bias / pavlovian parameters were swapped in the code. Fixed and re-fitted.
- major: the README's 'Reproduced: valued_learning_model_wins (~442/~268)' rested on the swapped cue codes; with correct labels the valued-sensitivity model has the lower summed BIC at N=100 (~404 exp0 / ~235 exp1 units). Section rewritten to Reproduced: none, Not reproduced: valued_learning_model_wins; the note that participant_id cannot link the waves removed.
- minor: README described the timing columns as 'MATLAB serial date centiseconds'; they are ms since task start (target_onset_time in s; rt = keypress_time - 1000*target_onset_time exactly), with cue_target_interval 250-3500 ms and intertrial_interval 250-500 ms as in Fig 1A.
- minor: README said key_pressed is 0 or 71; 148 exp0 and 61 exp1 NoGo trials record other key codes without a timed press. Documented.
- minor: one exp0 trial has rt = -1 in the source (GNGmodelFit2.m: 'count it as a go'); the transform codes it as Go like the source. Documented in the rt description.
- minor: response_raw = 3 (2469 exp0 / 1277 exp1 trials) are presses with RT 700-817 ms that the task scored as wrong responses (bad outcome with p 0.8 in all four conditions); the paper's fit code counts them as Go. README description corrected ('invalid' -> late press).
- minor: '### exp0' / '### exp1' column headings changed to '#### exp0' / '#### exp1'.
- minor: the README Experiment summary and reward description repeated the unsupported 20p amount; reworded.

Open:
- major: the paper's primary modeling result (valued-learning model ahead by 255.7 / 275.6 iBIC units, only 0.15 units per participant, hierarchical EM with group priors, p. 7-8) does not reproduce with model.py's per-participant MLE and summed BIC: at N=100 per wave the valued-sensitivity model is ahead by ~404 / ~235 units and 93-98% of fits sit at a parameter bound. A hierarchical fit like the paper's is needed; model.py keeps the cognitive-modeling:needs-review tag.
- minor: the paper counts 557 follow-up datasets of which 542 good quality (p. 17) and reports N = 556 (p. 7); the source ships 557 files for 556 IDs (38943 twice). S2 Data is described as 62 participants (p. 24) but holds 61 files. Inside the source; the CSVs ship every file.
- minor: two exp1 participants (41517, 48231) have no baseline file in S1 Data, so they cannot be linked to exp0.
- minor: the source does not document the response_cue1 flag (col 4 of LearnVerData); the README and transcripts read it as a premature press during the cue. The flag is dense in early trials (participant 10009: 10 of the first 12 trials) and raises the Go rate from 0.56 to 0.77, which fits that reading but does not prove it.

Run: claude-fable-5-1, 2026-09-10
