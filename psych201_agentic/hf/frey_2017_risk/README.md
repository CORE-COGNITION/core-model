---
tags:
- paradigm:risky-choice
- cognitive-modeling:needs-review
- psych-101
- psych-201
- text-format:pass
- js-experiment:needs-review
- simulator:pass
- verification:needs-review
---

# frey_2017_risk

- Paper: https://doi.org/10.1126/sciadv.1701381
- Data source: https://osf.io/rce7g (Basel-Berlin Risk Study; Codebook.pdf included in repo)
- PDF: https://edoc.unibas.ch/server/api/core/bitstreams/95012933-c7ba-4701-975d-1d71a18c3cdb/content
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Frey, R., Pedroni, A., Mata, R., Rieskamp, J., & Hertwig, R. (2017). Risk preference shares the psychometric structure of major psychological traits. Science Advances, 3(10), e1701381.

## Experiment summary
The Basel-Berlin Risk Study is one large single-session battery in which ~1507 healthy adults (Basel and Berlin labs) completed 39 risk-taking measures spanning three measurement traditions: self-reported propensity (questionnaires), incentivized behavior (trial-level choice tasks), and frequency of real-world risky activities. The five transformed experiments cover the trial-level behavioral tasks for the full main sample: exp0 = adaptive lotteries/ABCT (N=1507, 50 lottery choices per participant), exp1 = Multiple Price List (N=1507, 66 MPL choices, including a Holt–Laury-style price list), exp2 = Balloon Analogue Risk Task (N=1507, ~30 balloon trials; number of pumps per trial), exp3 = Decisions from Description (N=1507, 8 A/B gamble problems), and exp4 = Decisions from Experience (N=1507, 8 sampled A/B gamble problems). Participants thus made per-trial risky choices and RTs across lottery choice, risk-taking, and description/experience gambles, with gain and loss domains. The central research question is whether a general factor R of risk preference exists (mirroring g), whether correlations between propensity and behavioral measures are weak, and whether such a general factor generalizes to real-world risky activities. The OSF data release additionally includes Expected-Utility and Cumulative-Prospect-Theory model-parameter fits (`modelpars.csv`), which are not reported in the paper.

## Notes

### Columns

Source for all experiments: `raw/main/` (Basel-Berlin Risk Study). Five trial-level behavioral tasks were transformed (the 5 experiment files map 1:1 to `raw/main/lotteries/`, `raw/main/mpl/`, `raw/main/bart/`, `raw/main/dfd/`, `raw/main/dfe/`). The source also ships trial-level data of a sixth behavioral task, the Columbia Card Task (`raw/main/cct/cct.csv`, 84 rounds per participant), which was not transformed.

#### exp0  (adapted from `raw/main/lotteries/lotteries.csv`)
| column | description |
|--------|-------------|
| participant_id | Original partid (alphanumeric, e.g. "64000401") |
| trial | 0..49, within each participant_id (50 decision rows each), in presentation order (ranked by Presentation_Order) |
| response | Decision_X: 1 = chose lottery X, 0 = chose lottery Z (0/1) |
| Dec_ID | Decision identifier (1..25) |
| Stage | Stage of adaptive staircase (2=preselect, 3/4) |
| Substage | Substage within stage |
| External_Dec_ID | External decision index (unique per trial across participants) |
| V_Decision | Indicator, 1 = decision for variable lottery was recorded |
| X1 | Magnitude of lottery X outcome 1 |
| X2 | Magnitude of lottery X outcome 2 |
| PX1 | Percent probability of X1 |
| Z1 | Magnitude of lottery Z outcome 1 |
| Z2 | Magnitude of lottery Z outcome 2 |
| PZ1 | Percent probability of Z1 |
| Maxstage | Maximal number of stages |
| Presentation_Order | Presentation order index |
| Presentation_XZ | 1 = X presented left/right flag (0/1) |
| rt | Decision_Time: decision reaction time in ms |
| Decision_X | Same as response (kept as source column) |
| Inconsistent | 1 if inconsistent choice trial |
| Change_X | Whether the X lottery was adapted (=1) |
| Threshold_Up | Upper iterate boundary |
| Threshold_Lo | Lower iterate boundary |
| R | 1 = risky (higher-variance) lottery chosen (0/1) |

#### exp1  (adapted from `raw/main/mpl/mpl.csv`)
| column | description |
|--------|-------------|
| participant_id | Original partid |
| trial | 0..N-1, within each participant_id (66 rows typical; 2 participants have 1 all-NaN row) |
| response | choice: 0 = left option, 1 = right option (0/1; NaN for the 2 failed rows). The sides were fixed: `R` is a deterministic function of `dp` and `choice` for every participant, so 1 is always lottery A of the source price lists (`mplProblems.csv`) and 0 is lottery B |
| dp | Decision problem / price list (1..7; dp=1 classic Holt-Laury, dp=2..7 new MPLs) |
| decision | Decision index within price list |
| choice | Same as response (kept as source column) |
| R | 1 = risky (higher-variance) gamble chosen (0/1) |

#### exp2  (adapted from `raw/main/bart/bart_pumps.csv`, Balloon Analogue Risk Task)
| column | description |
|--------|-------------|
| participant_id | Original partid |
| trial | 0..N-1, within each participant_id (balloon trial; ~30 per participant) |
| response | pumps: number of pumps on the trial (1..128) |
| block | Block 0..2 (3 blocks, ~10 trials each; source 1,2,3 recoded -1) |
| pumps | Same as response (kept as source column) |
| exploded | 1 if balloon exploded in trial, else 0 |
| reward | payoff: points earned on the trial (0..124) |

#### exp3  (adapted from `raw/main/dfd/dfd_perprob.csv`, Decisions From Description)
| column | description |
|--------|-------------|
| participant_id | Original partid |
| trial | 0..7, within each participant_id (8 gamble problems) |
| response | decision: "A" or "B" letter choice |
| location | Study site: "Basel" or "Berlin" |
| gamble_lab | Label of the gamble (e.g. he04_6inv) |
| domain | "gain" or "loss" |
| gamble_ind | Index of gamble within participant (1..8) |
| rt | rt_decision: decision RT in ms |
| H | 1 = higher-expected-value option chosen (0/1) |
| R | 1 = riskier (higher-variance) option chosen (0/1) |
| decision | Same as response ("A"/"B", kept as source column) |

#### exp4  (adapted from `raw/main/dfe/dfe_perprob.csv`, Decisions From Experience)
| column | description |
|--------|-------------|
| participant_id | Original partid |
| trial | 0..N-1, within each participant_id (8 gamble problems typical) |
| response | decision: "A" or "B" letter choice |
| location | Study site: "Basel" or "Berlin" |
| gamble_lab | Label of the gamble |
| domain | "gain" or "loss" |
| gamble_ind | Index of gamble within participant (1..8) |
| samples | Number of samples drawn |
| switches | Number of switches between options |
| swrate | Switching rate (0..1; NaN where no switch) |
| A_mean | Experienced mean outcome of A |
| A_var | Experienced variance of A |
| B_mean | Experienced mean outcome of B |
| B_var | Experienced variance of B |
| rare_n | Number of rare-event observations |
| rt_sample | Per-sampling RT in ms |
| rt | rt_decision: decision RT in ms |
| H | 1 = higher-expected-value option chosen (0/1) |
| Hexp | 1 = higher-experienced-mean option chosen (0/1) |
| R | 1 = riskier (higher-variance) option chosen (0/1) |
| Rexp | 1 = higher-experienced-variance option chosen (0/1) |
| decision | Same as response ("A"/"B", kept as source column) |

### Response coding summary
- exp0 LOT: response = Decision_X (choose X=1 / Z=0). Source `R` = risky (higher-variance) choice, not reward.
- exp1 MPL: response = choice (left=0 / right=1; left = lottery B, right = lottery A of `mplProblems.csv`).
- exp2 BART: response = pumps (1..128, continuous count).
- exp3/exp4 DFD/DFE: response = decision letter ("A"/"B"). The raw A/B choice is a two-alternative option label; kept verbatim.
- `choice`-like raw columns (Decision_X, choice, decision, pumps) are carried through unchanged alongside `response`.

The retest subsamples (`raw/retest_basel/`, `raw/retest_berlin/`, n=173 combined: Berlin 109 at 6 months, Basel 64 at 3 months) and aggregate-only measures (VRTTT scores, MT marbles, questionnaire scores, model parameter fits in `modelpars.csv`) were not part of the transformed trial-level experiments here; the questionnaire, frequency, and model-parameter data remain available in the OSF source. Within exp1 (MPL), two participants have a single all-NaN trial row retained for fidelity to the source.
## Update (2026-08-13)
- Chronology fix, exp0.csv only: rows had followed the adaptive staircase's decision-ID order (Dec_ID x Stage), not the order lotteries were shown on screen. Rows are now sorted per participant by `Presentation_Order` (unique per participant, strictly increasing after the fix) and `trial` renumbered 0..49 in that order (73,722 of 75,350 cells changed). No other column touched; per-participant row multisets identical to the previous release.
- exp1.csv-exp4.csv unchanged (byte-identical).

CSVs fixed in place from the previous release; transform.py updated to produce the same output
from raw. The previous version remains in the repo's git history.

## Text-format conversion
Transcribed four of the five trial-level experiments into natural-language session transcripts (`transcripts0/1/2/4.jsonl`, one line per participant, one per experiment): exp0 adaptive lotteries, exp1 multiple price lists, exp2 Balloon Analogue Risk Task, and exp4 decisions from experience. Each transcript starts with the cover story and exact response format, then narrates every trial (stimuli, free response, and outcome) in order. exp3 (decisions from description) was not transcribed: the transformed CSV records only the gamble label and the participant's A/B choice, not the described gambles. The described gambles are recoverable, though: the paper's supplement (p. 3) states that DFD presented the same 8 problems as DFE, with their outcomes and probabilities, and the `H`/`R` columns of `exp3.csv` match those A/B specifications for all 8 problems. In exp1 (MPL), the codebook codes `choice` as 0 = left / 1 = right, and `R` (risky = higher-variance choice) is a deterministic function of `dp` and `choice` for all 1505 participants with data, so the sides were fixed: `choice` 1 is always lottery `A` of the source price lists and 0 is lottery `B`. The transcription therefore shows lottery `B` as the left option (`L`, response 0) and lottery `A` as the right option (`R`, response 1).

Sample transcript (exp0, participant 64000401, through the first response):
```
In this task you repeatedly choose between two lotteries, X and Z. Each lottery has two possible payoffs (a gain or a loss) with stated chances. On every screen you see both lotteries and decide which you prefer. One of your decisions is paid out for real at the end, so your choices can win or lose you bonus money. On each trial press X to choose lottery X, or Z to choose lottery Z.
Lottery X pays 25 with a 70% chance and 15 with a 30% chance. Lottery Z pays 40 with a 65% chance and 10 with a 35% chance. You press [HUMAN_RESPONSE]Z[/HUMAN_RESPONSE] …
```
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Indeterminate: The paper's only formal modeling result is a psychometric bifactor latent-factor model (SEM/CFA via lavaan) fit to 39 aggregate risk-taking measures spanning propensity (questionnaires), behavioral (7 tasks), and frequency traditions. The transformed CSVs here contain only 5 trial-level behavioral tasks (exp0 LOT, exp1 MPL, exp2 BART, exp3 DFD, exp4 DFE); all propensity and frequency measures (and behavioral CCT/MT/VRTTT) are absent, so the model's variables are not derivable from the CSV columns. The paper fits no per-trial CPT/EU/choice model in the main text (the README's CPT/EU note is not supported by the paper). Any implementable version would reduce the 39-measure bifactor to a 5-behavioral-measure factor analysis, discarding the central claim that R loads on propensity/frequency but not behavioral measures.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Added static jsPsych v8 online versions of four of the five trial-level tasks under
`experiments/exp1/` (Multiple Price List), `experiments/exp2/` (BART), `experiments/exp3/`
(Decisions From Description) and `experiments/exp4/` (Decisions From Experience); each
builds its session into a CSV in the repo's own schema and was verified end-to-end with the
headless `?mode=simulate` round trip. `experiments/exp0/` (Adaptive Lotteries) was **not**
built: the adaptive-staircase stimulus generator (Rieskamp 2008) is not recoverable from
`exp0.csv`, the paper, or OSF. The exp3/exp4 gamble distributions and the exp2 per-pump
burst probability were reconstructed from OSF/CSV (see `experiments/README.md`); this run is
therefore `js-experiment:needs-review` until exp0 is rebuilt faithfully.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Text simulators for exp1 (Multiple Price List), exp2 (BART) and exp4 (Decisions From
Experience) are uploaded as `simulate1.py`, `simulate2.py`, `simulate4.py`. Each passes
the round-trip check: regenerating the transcripts from the simulated CSVs with
`build_jsonl.py` yields byte-identical `text` fields. exp0 (adaptive lotteries) and exp3
(decisions from description) are skipped as not simulatable — exp0's adaptive-staircase
stimulus generator is not recoverable from `exp0.csv`, the paper, or OSF, and exp3 has no
transcripts to mirror (its gambles are the 8 DFE problems of the supplement, p. 3; see the
transcription note above).
Assumptions worth surfacing: in exp4 the per-trial sample count follows a negative-binomial
fit to the observed marginal, the box-sampling sequence is a two-state Markov chain with a
per-trial switch probability drawn from Beta(1.5, 12), and for ≥30 draws both boxes are
forced to be sampled (matching the observed data, whose single-box trials never exceed 28
draws). In exp1 the sides of the transcription are mirrored (lottery B left = `L` = response
0, lottery A right = `R` = response 1, per the codebook and the data), and the source `R`
column is reproduced by the higher-variance rule (tie in the last Holt-Laury row: R = 1 for
lottery B), which matches every value in `exp1.csv`. In exp2 each participant's 30 balloons
take the 30 explosion points listed in the supplement (p. 2) in a random order, as in
`exp2.csv`, where no participant repeats an explosion value.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: needs-review (critical 1, major 5, minor 9; fixed 7, open 8).

Checked: paper (DOI 10.1126/sciadv.1701381, edoc.unibas.ch PDF) and its supplement (1701381_SM.pdf via Europe PMC), original data (OSF rce7g data/main incl. Codebook.pdf), exp0-exp4, transform re-run (all five CSVs byte-identical), transcripts rebuild, simulators (smoke run and round trip), modeling section vs tag (no model.py), analysis (3/3 effects reproduce), logs. Skipped: none.

Fixed:
- critical: transcripts1.jsonl showed the wrong lottery on each side. The codebook codes choice 0 = left / 1 = right, and exp1.csv's R (risky = higher variance) is a deterministic function of dp and choice for all 1505 participants: in the Holt-Laury list 96% pick choice 0 where B (3.85 sure) dominates and 97% pick choice 1 where A (2 / 1.6) is safe, so choice 1 is lottery A and choice 0 is lottery B. The transcript rendered lottery A as the left option and response 0 as L. build_jsonl.py now shows B left / A right; transcripts1.jsonl rebuilt; simulate1.py mirrors the sides and reproduces R with the higher-variance rule (tie at dp1 decision 10: R = 1 for B), verified on all 99,330 rows.
- major: build_jsonl.py read mplProblems.csv, which is not in the repo, so the transcripts could not be rebuilt from the repo alone. The 66-row table is now embedded (identical to OSF data/main/mpl/mplProblems.csv); transcripts0/2/4 rebuild byte-for-byte.
- major: README (Text-format, Simulators, exp1 columns) claimed the MPL left/right side was randomized per participant and not recoverable; reworded to the codebook coding and the fixed sides shown by the data.
- major: README claimed exp3's described gambles cannot be reproduced; the supplement (p. 3) states DFD presented the same 8 problems as DFE with outcomes and probabilities, and exp3.csv's H/R columns match those A/B specifications for all 8 problems. Reworded.
- major: README said only trial-level behavioral tasks were transformed; the source also ships trial-level Columbia Card Task data (data/main/cct/cct.csv). Reworded to name it.
- minor: simulate2.py drew explosion points uniformly with replacement; the supplement (p. 2) lists 30 fixed explosion points presented in randomized order and no participant in exp2.csv repeats an exploded pump value. Each participant now gets a permutation of the 30 points; round trip passes.
- minor: the previous verification run's transcript log and session export (transcripts/auto-exp-verify.log, logs/auto-exp-verify.sessions.json, verdict pass) contradicted the new tag; removed. This run's files are pushed by the runner.

Open:
- major: the source ships trial-level Columbia Card Task data (cct.csv, 126,505 rows = 84 rounds x 1506 participants + 1; codebook p. 4), one of the paper's eight behavioral tasks (Table 1), which is not transformed. Adding an exp5.csv needs a transform change plus README, transcript, simulator and online-experiment updates; left for a transform run.
- minor: check_repo flags transcripts2.jsonl (BART) response tokens as undeclared; the response is a free pump count (115 distinct values, 1..128) that cannot be enumerated in the instructions. build_jsonl.py regenerates the file byte-for-byte and the simulator round trip passes.
- minor: exp3/exp4 code response as the letters A/B (schema: 0/1 for a two-alternative choice); kept verbatim from the source and documented in the README.
- minor: transform.py never reads bart_rts.csv (per-pump RTs), bart_riskperc.csv (per-trial explosion-risk ratings 0-100, 17,114 rows) or dfe_samples.csv (317,942 per-sample draws with side, option, outcome and RT); exp2/exp4 keep the per-balloon / per-problem grain of bart_pumps.csv / dfe_perprob.csv.
- minor: 80 participants have 27-29 balloons in exp2 (source bart_pumps.csv; the supplement says 30) and trial is renumbered by cumcount, so the source balloon index (1..30, gaps most often at balloons 5 and 1) is not kept.
- minor: the supplement (p. 4) reports 84 adaptive-lottery choices per participant; the source lotteries.csv ships 50 per participant (Stage 3: 25 each; Stages 2 and 4 vary). Inside the source; exp0.csv is faithful to it.
- minor: the supplement (p. 5) says the first LOT option (table S8 option A) is the fixed reference; in the source the option A values are lottery X, which is the adapted one (X varies within every Dec_ID, Z never does; Change_X). Inside the source; the README describes the data correctly.
- minor: exp3 is transcribable from the supplement's 8 problems and the recorded A/B choices, but transcripts3.jsonl and simulate3.py were not built (new artifacts, outside a verification fix).

Run: claude-fable-5-1, 2026-09-14
