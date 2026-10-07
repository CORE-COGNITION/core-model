---
tags:
- paradigm:bandit
- cognitive-modeling:pass
- psych-201
- js-experiment:pass
- text-format:pass
- simulator:pass
- verification:pass
---
# breslav_2022_shuffle

- Paper: https://doi.org/10.1177/09567976211042007
- Data source: https://osf.io/7bfy9 (Data component: cgt_data.xlsx, cgt_data.h5)
- Full text: https://www.ncbi.nlm.nih.gov/pmc/articles/9096196
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Breslav, A. D. S., Zucker, N., Schechter, J. C., Majors, A., Bidopia, T., Fuemmeler, B. F., Kollins, S. H., & Huettel, S. A. (2022). Shuffle the Decks: Children Are Sensitive to Incidental Nonrandom Structure in a Sequential-Choice Task. Psychological Science, 33(4), 550–562.

## Experiment summary
Single experiment (exp0, N = 304): 304 children (ages 4–13) each completed 50 trials of a sequential-choice task choosing between an advantageous and a disadvantageous deck (one backed with stripes, the other with dots; which pattern was the advantageous deck was randomly assigned per child and is not recorded) under partial feedback of M&M wins/losses. Both decks carried hidden alternating win/loss structure (incidental nonrandom sequences), and the key question was whether children's choices track this incidental structure versus the decks' expected value. The binary deck choice per trial is the response; the paper also fits a formal switch model to switching behavior, with θ-binning of individual differences across development (hence the cognitive-modeling tag).

## Notes

### Columns
#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number (integer) from source choices table |
| trial | 0..49 within each participant_id, derived from 1-indexed source trial |
| response | Deck choice: 0 = disadvantageous (DIS) deck, 1 = advantageous (ADV) deck (source choose_adv). The source records only ADV/DIS; which back pattern (stripes or dots) was the ADV deck was randomly assigned per child (paper p. 552) and is not recorded. The transcripts and the simulator use stripe = ADV, dot = DIS as a fixed convention. |
| reward | Net M&M payoff on that trial (win + lose, with lose stored as a non-positive number), source net_outcome |
| adv_top_card | Card index of the ADV deck's top card that trial (a04-a53; cards 1-3 were the examples, a51-a53 are cards 1-3 re-drawn after the deck ran out) |
| dis_top_card | Card index of the DIS deck's top card that trial (d04-d50) |
| chosen_card_id | Card index actually chosen that trial (a## or d##) |
| choose_adv | Raw source deck-choice flag: 1 = ADV chosen, 0 = DIS chosen |
| win | Total M&Ms won that trial (1 or 2) |
| lose | Total M&Ms lost that trial, stored as a non-positive number (0,-1,-4,-5,-6); one source row (card a53) carries +1 |
| net_outcome | Net M&Ms (win + lose) that trial; identical to reward |
| switch | 0 if the same deck was chosen as on the previous trial, 1 if switched; NaN on first trial |
| last_chosen_card | Card index chosen on previous trial; NaN on first trial |
| last_trial_win | Won (+1) or lost (-1) previous trial based on net outcome; NaN on first trial |
| last_trial_choose_adv | Chose ADV (+1) or DIS (-1) previous trial; NaN on first trial |
| age | Participant age in years (source age_years truncated to integer) |

### Notes
- One experiment corresponds to the paper's single study; all 50 trials per child are included (no practice/warmup phase in the source).
- The `response` (deck choice) coding follows the schema's two-alternative bandit convention; the source-mirroring `choose_adv` and M&M payoff columns (win/lose/net_outcome) that are specific to this task are kept.
- Child ages are reported as whole years (source `age_years` truncated).

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: logistic switch model (null, abundance-only, switch-only, both) fit per participant; AIC comparison + θ-binning.
Reproduced: both_model_has_lowest_aic, theta_binning_groups.
Not reproduced: none.
Numeric mismatch: both AIC 16030.4 (paper 16030); θ mean/sd 0.07/0.34 (paper 0.06/0.40); groups 89/136/79 (paper 90/136/78) — differences from optimizer choice (L-BFGS-B vs paper's SLSQP) moving boundary cases.
Indeterminate: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`experiments/exp0/` is a static jsPsych v8 port of the single experiment (50
choices, dot vs stripe deck). The headless `?mode=simulate` round trip passed
(schema, codings, dtypes, 50 rows, no data leaves the page) and the visual check
found no rendering breakage. No experiments were skipped. `age` is left blank
per participant (a browser session collects no such phase); the deck-back
assignment and the feedback/ITI timings are cosmetic defaults.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Text-format conversion

The single experiment (exp0.csv: 50 sequential choices between a stripe-backed
and a dot-backed deck, deterministic fixed card order, M&M wins/losses) is
textifiable — naming the decks does not trivialize the choice, remove the
information a participant uses, or change the decision process. exp0.csv was
transcribed into transcripts0.jsonl (304 transcripts, one per child). No
experiments were skipped.

### Sample transcript (participant 226, exp0.csv)

```
You are playing a card game for M&M's with a grown-up on the other side of the table. A cylinder on the table already holds your 10 M&M's. Two face-down decks sit in front of you: one deck of cards is backed with black and white stripes, the other is backed with black dots on a white background. On each of 50 turns you pick one whole deck and the grown-up turns over that deck's top card. Every card shows, on its top half, how many M&M's you win, and on its bottom half, how many M&M's you lose; the difference between the two is the net M&M's you keep. The grown-up adds or removes M&M's from your cylinder to match. Your goal is to finish with as many M&M's as possible. As a demonstration you are first shown three example cards from each deck, never scored: the stripe deck's examples give +1, +1 and 0 net M&M's; the dot deck's examples give +2, +2 and -2 net M&M's.
On each turn press A for the dot-backed deck or B for the stripe-backed deck.
You press [HUMAN_RESPONSE]B[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

`simulate0.py` simulates the single experiment (50 child choices between a
stripe- and a dot-backed deck, fixed card order, M&M wins/losses; decks advance
on choice). The round-trip check passed byte-for-byte (8/8 simulated
participants re-transcribe identically through `build_jsonl.py`). No experiments
were skipped.

`ASSUMPTION:` the shipped data reveal only 47 disadvantageous-deck cards
(d04..d50); for a 48th to 50th DIS choice the simulator restarts the deck at cards
1-3 (+2, +2, -2), following the source's restart rule for the ADV deck (a51-a53) —
unreachable under random play. A single real data typo (card a53 records lose=1
for a 0 net) is not reproduced; the simulator derives lose = net - win.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 5, minor 10; fixed 10, open 5).

Checked: paper (https://doi.org/10.1177/09567976211042007, Europe PMC PDF of PMC9096196), original data (https://osf.io/7bfy9, Data component u8m7d: cgt_data.h5, cgt_data.xlsx; authors' Task, Analysis Code components), exp0, transform re-run (exp0.csv byte-identical; all 15,200 rows and 14 source columns carried, age_years truncated to whole years, which matches the paper's M = 7.43, SD = 1.95 on p. 552), transcripts (build_jsonl.py rebuilds transcripts0.jsonl byte-for-byte), simulator (smoke test, 8/8 round trip through build_jsonl.py, deck sequences equal to the data), modeling (full model.py run: both wins on AIC 16030.4 vs the authors' 16030.4, null 20650.2 = paper; Theta bins 89/136/79 vs 90/136/78; the abundance-only and DR-only AICs come out lower than the paper's 16,921 / 17,878 because the multi-start L-BFGS-B finds better optima than the authors' SLSQP, ordering unchanged), analysis (all 3 effects reproduce: trial x age negative, DR-group win-shift bias, age effect only in the DR group; cf. Tables S1/S2), logs. Skipped: none.

Fixed:
- major: README citation gave Psychological Science 33(3), 402-414; the paper header and Crossref give 33(4), 550-562.
- major: README described `switch` as 1 = same deck, 0 = switched; the source data dictionary and all 14,896 scored rows have 0 = same deck, 1 = switched.
- major: README stated dot = DIS and stripe = ADV as recorded fact; the paper (p. 552) randomly assigned the back pattern per child and the source records only ADV/DIS. README reworded; the stripe = ADV, dot = DIS mapping in the transcripts and simulator is documented as a convention (the child cannot tell which deck is advantageous, so no information is lost).
- major: README summary said one deck carried the hidden alternating structure; the paper (pp. 553-554) shows both decks alternate excessively.
- major: simulate0.py clamped the DIS deck at d50 (net -4) for a 48th-50th DIS choice; per the source's restart rule (a51-a53 = cards 1-3) the deck restarts at cards 1-3 (+2, +2, -2). Three restart outcomes appended to the DIS stack; docstring and README Simulators note updated; smoke test, all-DIS agent and 8/8 round trip re-checked.
- minor: README title '# Breslav 2022 Shuffle' -> '# breslav_2022_shuffle'.
- minor: README summary now labels the experiment 'exp0, N = 304'.
- minor: README described reward/net_outcome as 'win - lose' although `lose` is stored as a non-positive number (net = win + lose on 15,199 rows).
- minor: README card ranges a01-a50 / d01-d50 corrected to the shipped a04-a53 / d04-d50 (cards 1-3 are the examples; a51-a53 are cards 1-3 re-drawn after the ADV deck ran out).
- minor: README Notes cited an unrelated dataset (`thoma_2025_emerging`) as the response-coding convention; reference removed.

Open:
- minor: `last_trial_win` and `last_trial_choose_adv` use -1 for loss / DIS (flagged as a sentinel by the mechanical check); this is the source's coding and the paper's o_{t-1} in {1, -1} (p. 554), with the first trial empty. Kept as raw source values.
- minor: card a53 (participant 54, trial 49) carries lose = +1 with net 0; the source adv_cards table has the same +1 on a03 and a53 (sign typo inside the source). Data faithful; noted in the README column table.
- minor: logs/auto-exp-modeling.sessions.json, logs/auto-exp-sim.sessions.json, logs/auto-exp-transcribe.sessions.json and transcripts/auto-exp-modeling.log mention `thoma_2025_emerging`; each file holds one session of this dataset and every mention quotes the former README note. Nothing foreign to prune; logs left as records.
- minor: model.py docstrings cite 'p.405' / 'p.406'; the model comparison and Theta binning are on journal pp. 555-556 (docstring only, results unaffected).
- minor: analysis.py docstring says 'mixed-effects logistic regression' but fits a plain GLM logit on whole-year age without a participant random intercept (Tables S1/S2 used glmer with scaled age_years); all three effects reproduce in direction and significance.

Run: claude-fable-5-1, 2026-09-09
