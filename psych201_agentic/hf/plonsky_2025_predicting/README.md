---
tags:
- paradigm:risky-choice
- cognitive-modeling:needs-review
- psych-101
- text-format:pass
- js-experiment:needs-review
- simulator:pass
- verification:pass
---
# plonsky_2025_predicting

- Paper: https://doi.org/10.1038/s41562-025-02267-6
- Data source: https://doi.org/10.17605/OSF.IO/VW2SU (https://osf.io/vw2su/)
- Full text: https://www.nature.com/articles/s41562-025-02267-6
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Plonsky, O., Apel, R., Ert, E., Tennenholtz, M., Bourgin, D., Peterson, J. C., Reichman, D., Griffiths, T. L., Russell, S., Carter, E. C., Cavanagh, J. F., & Erev, I. (2025). Predicting human decisions with behavioural theories and machine learning. Nature Human Behaviour, 9(11), 2271-2284.

## Experiment summary
This paper introduces BEAST-GB, a hybrid model that combines the BEAST behavioural theory of risky choice with gradient-boosting machine learning, and shows it outperforms neural networks and dozens of existing models at predicting human decisions under risk and uncertainty, while also refining the underlying theory. The raw human data the paper releases are two datasets. exp0 (N = 240) is Experiment 2 of the CPC18 prediction competition run by the authors, i.e. the 60 held-out competition tasks (GameID 211–270): each participant faced one cohort (Set 8 or 9) of 30 tasks in random order and chose 25 times per task between two described lotteries, Option A and Option B (multi-outcome lotteries, ambiguity of Option B, and correlated payoffs are part of the task space), with no feedback in trials 1–5 and full feedback (obtained and forgone payoff) from trial 6; the 25 trials are pooled into 5 blocks of 5 for analysis. exp1 (N = 236) is the extensive-form-game data the paper's Supplementary Information re-analyses ("Additional datasets: Extensive form games"): the two choice prediction competitions of Ert, Erev & Roth (2011), 240 one-shot two-player games in four sets of 60 (estimation and prediction set of each competition), each played by 118 Player-1 participants (Stop/Continue, "Out"/"In" in the paper) and 118 Player-2 participants (Left/Right) under the strategy method. Note that CPC18's own second track (predicting individual decision makers) is not this data. Choices13k, HAB22, and the context-generalization analyses re-analyze previously published datasets and are excluded here. The response is a binary choice between prospects/game outcomes, and the study's central aim is predicting and generalizing human choice under risk.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original SubjID from source CSV; ID per subject (240 subjects) |
| trial | 0-indexed trial within (participant_id, task_id); original Trial (1–25) minus 1 |
| response | Which option chosen; 1 = chose option B, 0 = chose option A (from B column) |
| task_id | 0-indexed presentation order of the participant's 30 games (source Order 1–30 minus 1); rows sorted by task_id, trial are chronological. The game identity is game_id |
| gender | Canonical gender vocabulary (source F/M → f/m) |
| block | 0-indexed 5-trial block of the 25 repeats (source block 1–5 minus 1) |
| button | Physical button (L/R) pressed |
| site | Source Location, lowercased (e.g. rehovot) |
| age | Participant age (years) |
| Set | Source Set: the cohort of 30 games the participant faced (8 = GameID 211–240, 9 = GameID 241–270); between-subject |
| condition | Source Condition, lowercased (always "byprob") |
| game_id | Original GameID (211–270) |
| Ha | Option A: expected value of the lottery paid with probability pHa (the single outcome when LotNumA = 1) |
| pHa | Probability (0–1) that Option A pays its lottery rather than La |
| La | Option A: outcome paid with probability 1 − pHa |
| LotShapeA | Shape of Option A's lottery around Ha: `-` (single outcome), `Symm`, `R-skew`, `L-skew` (SI pp. 5–6 give the outcome sets) |
| LotNumA | Number of outcomes of Option A's lottery (1 = degenerate) |
| Hb, pHb, Lb, LotShapeB, LotNumB | Same fields for Option B |
| Amb | 1 = Option B's probabilities were not shown to the participant (ambiguous option), 0 = fully described |
| Corr | Correlation of the two options' realized payoffs: 0 none, 1 positive, −1 negative (source design factor) |
| Order | 1–30 within-subject game presentation order |
| reward | Original Payoff, realized payoff of the chosen option |
| forgone | Original Forgone, payoff of the unchosen option |
| rt | Reaction time (ms) |
| Apay | Realized payoff drawn for Option A on this trial |
| Bpay | Realized payoff drawn for Option B on this trial |
| Feedback | 1 = obtained and forgone payoffs were shown after the choice (trials 6–25), 0 = no feedback (trials 1–5) |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Derived from set + player + sub# column (e.g. `est1_p1_sub1`) |
| trial | Always 0: exactly one response per (participant_id, task_id), so trial restarts at 0 within each task; the game identity is carried by task_id |
| response | Subject's binary choice (0/1) for that game |
| task_id | 0-indexed analysis-time game id (game_augmented minus 1) |
| set | Source set: est1 / est2 / pred1 / pred2 |
| phase | est (estimation set) or pred (competition prediction set) |
| player | Player 1 / Player 2 (two variants of each game's decision structure) |
| game | Original game number (1–60; est2 games 61–120) |
| game_augmented | Analysis-time game id; for pred2 this is game + 60 (offset used in the R analysis so pred2 games align to the est2 61–120 numbering) |
| f1, s1, f2, s2, f3, s3 | Three game-structure features f with companion state s |

The paper's headline claim is the predictive accuracy of the BEAST-GB computational model. Because that is a model-comparison benchmark fitted via machine learning, it is not reproduced from the raw choices here; instead the uploaded analysis verifies the underlying behavioral validity of the data, including expected-value sensitivity, within-session reaction-time learning, over-choice of the expected-value-advantaged option, and non-random choice in the extensive-form task. Sample sizes: exp0 has 240 participants (the paper's Experiment 2: 141 female, age 18–50, Technion and Hebrew University/Rehovot labs). exp1 participant identifiers are per (set, player, subject#) column across the 8 source files (30+30, 28+28, 33+33, 27+27), 236 participants in total; each person played one role in one set (Ert, Erev & Roth 2011: 116 students in the two estimation sets). The order in which a participant faced the 60 games is not in the source; transcripts list them by game number. Payoffs in exp1 are in US dollars.

## Update (2026-08-13)
- Chronology/trial numbering (exp1.csv): `trial` had been set equal to `task_id` (ranging 0–59 or 60–119) even though each (participant_id, task_id) pair has exactly one row; `trial` is now 0 on every exp1 row (14,034 of 14,160 cells changed; 126 were already 0). No rows and no other columns changed.
- exp0 `task_id`: at this update it was left as the raw source GameID 211–270; the 2026-09-12 verification remapped it to the 0-indexed presentation order (`Order` − 1) so that it is 0-indexed and chronological, with the raw GameID kept in `game_id`. No other exp0 column changed.

CSVs fixed in place from the previous release; transform.py updated to produce the same output
from raw. The previous version remains in the repo's git history.

## Text-format conversion

Both experiments are transcribed to natural language. exp0 (CPC18 Experiment 2): repeated binary risky choice between two described lotteries over 25 trials per game (30 games); exp1 (extensive-form games): one-shot two-player games as Player 1 (Stop/Continue) or Player 2 (Left/Right), against a human co-player who chooses simultaneously without knowing one's choice (strategy method, no feedback). Each exp0 option is described as on the CPC18 screen (paper Fig. 1): every outcome with its probability, multi-outcome lotteries expanded from `LotShape`/`LotNum` with the SI's definitions (Symm: binomial around the mean; R-/L-skew: truncated geometric), and an ambiguous Option B (`Amb` = 1) listed without probabilities; `reward`/`forgone` show the realized payoffs. The response tokens are the options themselves (A/B, Stop/Continue, Left/Right).

Sample transcript (exp0, participant 80001, up to the first response):

```
You will play a series of games. In each game you choose repeatedly between two lotteries, Option A and Option B, for 25 trials. For the first 5 trials of each game you get no feedback; from the 6th trial on, after each choice you see both the payoff you received and the payoff you would have received from the other option. In some games the probabilities of Option B's outcomes are not shown. On each trial, press A to choose Option A or B to choose Option B.
Game (presentation 1): Option A pays 98 with probability 0.0125, 97 with probability 0.05, 96 with probability 0.075, 95 with probability 0.05, 94 with probability 0.0125, otherwise 3. Option B pays 59 with probability 0.5, otherwise -19.
Trial 0: You press [HUMAN_RESPONSE]B[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Indeterminate: The headline results are supervised ML predictive-accuracy benchmarks — BEAST-GB (gradient-boosting + BEAST behavioral theory) vs neural networks and dozens of behavioural models, reported as held-out test-set MSE on CPC18/Choices13k/HAB22. These depend on neural-net competitors, require the external Choices13k and HAB22 datasets (excluded from this repo), and are not formal cognitive-model parameter fits derivable from the provided CSV columns; no standalone non-neural cognitive-modeling result is identifiable. Indeterminate per skill scope.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments got a runnable static online reproduction (jsPsych v8, CDN-pinned, no backend).
- `experiments/exp0/` — CPC18 Track 1: repeated binary risky choice, 30 games × 25 trials (randomly assigned Set 8 or 9, shuffled presentation order); first 5 trials of each game give no feedback, the rest show both the obtained and the forgone payoff.
- `experiments/exp1/` — 60 one-shot extensive-form games; randomly assigned set (`est1`/`est2`/`pred1`/`pred2`) and player role (Player 1 Stop/Continue, Player 2 Left/Right).
The headless round trip (Playwright, `?mode=simulate`) ran and passed for both: the saved CSV matches each `expN.csv` schema (column names, 0-indexed counters, response/choice coding, numeric reward; 750 rows/participant with `trial` restarting per `task_id` for exp0, 60 rows/participant for exp1). Visual rendering check passed (no clipping/overflow/blank screens). No experiment was skipped. Saving offers a CSV download; no data-collection backend ships.
ASSUMPTIONS (browser-only where the authoritative source was unavailable): reward draws (the full multi-outcome lottery shapes, `LotShape`/`LotNum`, are not in the unified schema, so the `reward`/`forgone`/`Apay`/`Bpay`/`rt` values are fresh draws, not the source's originals); on-screen instruction text uses the repo's transcribed wording because the paper's Methods are paywalled and no verbatim instruction string was recoverable. Feedback/ITI durations, colors, and layout are documented cosmetic defaults.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Text simulators were added for both experiments: `simulate0.py` (repeated binary risky choice, CPC18 Track 1) and `simulate1.py` (one-shot extensive-form games). Each emits one participant per simulation; the round-trip check (writing the simulated `expN.csv` through the repo's `build_jsonl.py`) passed byte-identical for both, so a simulated participant is indistinguishable from a real one in wording, punctuation, and response notation. Payoffs in exp0 are drawn from the full CPC18 outcome distributions implied by `LotShape`/`LotNum` (SI pp. 5–6), with `Corr` honoured through a shared luck level, and game structures for both experiments are embedded verbatim from the source CSVs. No experiment was skipped.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 4, major 5, minor 8; fixed 14, open 3).

Checked: paper (DOI 10.1038/s41562-025-02267-6; the Nature page is paywalled, so the authors' arXiv 1904.06866 working paper of 2025-03-28 and the published Supplementary Information PDF were used, plus Ert, Erev & Roth 2011 for exp1's procedure), original data (https://osf.io/vw2su/, Replication package BEAST-GB R1.zip: CPC18/rawData_Comp_All.csv and Extensive form games/Raw Data *.csv), exp0-exp1, transform re-run (both CSVs byte-identical before the fix), transcripts (build_jsonl.py rebuild), simulators (smoke run and byte-identical round trip), modeling (no model.py; section and cognitive-modeling:needs-review tag agree), analysis (4/4 effects reproduce), logs. Skipped: none.

Fixed:
- critical: transcripts0.jsonl described multi-outcome lotteries by their H/L anchors (e.g. 'Option A pays 96 with probability 0.2, otherwise 3' for a 5-outcome Symm lottery paying 94-98), so feedback payoffs never appeared in the description; participants saw every outcome with its probability (paper Fig. 1). build_jsonl.py now expands LotShape/LotNum with the SI's definitions (pp. 5-6; verified: all observed Apay/Bpay of the 120 options fall in the implied supports, frequencies within 2 pp); transcripts0.jsonl rebuilt; simulate0.py renders and draws from the same distributions and honours Corr.
- critical: transcripts0.jsonl showed Option B's probabilities in the 12 ambiguous games (Amb = 1), which 'were not revealed to the decision maker' (paper Methods, SI p. 4). Ambiguous options now list the outcomes without probabilities and the instructions mention it; simulate0.py matches.
- critical: transcripts1.jsonl told Player 1 that Player 2 'always chooses the branch that gives themself the higher payoff' and told Player 2 that 'Player 1 has already chosen Continue'; the SI (p. 28) and Ert, Erev & Roth (2011) describe human co-players choosing simultaneously by the strategy method, no feedback, whole game shown to both. Both instruction heads rewritten and the Player-2 game line now includes the Stop payoffs; transcripts1.jsonl rebuilt; simulate1.py matches (round trip byte-identical).
- critical: check_repo reported that the exp0 transcript tokens did not map onto the CSV rows sorted by task_id, because task_id was the raw GameID (211-270, also a 0-index violation) while the transcripts follow presentation order. transform.py now sets task_id = Order - 1 (0-indexed, chronological; the raw GameID stays in game_id); exp0.csv regenerated (only the task_id column changed), transcripts unchanged by this, simulate0.py and the README updated.
- major: exp0 task_id was not 0-indexed (min 211) - same fix.
- major: README called exp1 'Track 2' of CPC18; CPC18's second track predicted individual decision makers on the risky-choice data (SI pp. 9-11), whereas exp1 is the extensive-form-game data of the two 2011 Ert, Erev & Roth competitions re-analysed in the SI (p. 28). Experiment summary rewritten; analysis.py docstring attribution corrected (results unchanged).
- major: README described Corr as a 'correctness / reward-feedback manipulation flag'; it is the correlation of the two options' payoffs (0 / 1 / -1; within-game corr(Apay, Bpay) = 0.00 / +0.67 / -0.44). Row corrected; Amb, Feedback, Apay, Bpay, Set, task_id rows corrected too.
- major: README exp0 Columns table had no rows for pHa, La, LotShapeA, LotNumA (folded into the Ha row); one row per column now.
- major: logs/auto-exp-modeling.sessions.json carried five file diffs from another run's work dir (vantiel_2022_meaning README and paper.html, a different exp0/exp1.csv, analysis.Rmd) in the first message's summary; removed, nothing else changed.
- minor: Columns headings '### exp0/exp1' -> '#### exp0/exp1'.
- minor: Experiment summary gave no N per experiment; now N = 240 and N = 236.
- minor: summary phrase '30 of 60 games repeated in 5 blocks of 5' replaced by the paper's design (one cohort of 30 tasks in random order, 25 trials each, pooled into 5 blocks of 5; A p. 22-23).
- minor: README Update (2026-08-13) bullet on task_id amended to the current state.
- minor: README notes now give the exp1 sample composition (30+30, 28+28, 33+33, 27+27 = 236 participants, one role each, 116 students in the two estimation sets per Ert et al. 2011), that payoffs are in US dollars, and that the paper's Player-1 labels are Out/In (transcript tokens Stop/Continue kept).

Open:
- minor: the source does not record the order in which an exp1 participant faced the 60 games (the 2011 paper counterbalanced the order and found no order effect); transcripts list games by game number.
- minor: the exact on-screen precision of the CPC18 probabilities and the exact wording used for ambiguous options are not stated in the paper or SI; transcripts show exact probabilities (up to 6 significant digits) and 'the probabilities are not shown'.
- minor: check_repo flags the -1 level of Corr as a sentinel; it is a genuine design level (negative correlation, 1 of 60 games), so the value is kept.

Run: claude-fable-5-1, 2026-09-12
