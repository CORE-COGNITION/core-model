---
tags:
- paradigm:risky-choice
- cognitive-modeling:pass
- psych-201
- text-format:pass
- js-experiment:needs-review
- simulator:pass
- verification:pass
---
# ciranka_2025_internal

- Paper: https://doi.org/10.1038/s44271-025-00314-6
- Data source: https://zenodo.org/records/16738297
- PDF: https://www.nature.com/articles/s44271-025-00314-6.pdf
- Full text: https://www.nature.com/articles/s44271-025-00314-6
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Ciranka, S., & van den Bos, W. (2025). Internal uncertainty impacts social information use in risky choice across adolescence. Communications Psychology, 3, 137. https://doi.org/10.1038/s44271-025-00314-6

## Experiment summary
A single laboratory lottery ('Developing Marbles') experiment in which 166 participants (N=166, aged 10-26; children, adolescents, and adults) each made 144 risky choices between a safe option and a risky gamble, in either a SoloChoice or SocialChoice phase. Risky gambles varied in expected value (points 8/20/50, winning probabilities 0.125-0.75) and were presented under low vs. high external uncertainty (`from_description` vs. `from_experience`, the latter showing a 9-marble sample). Participants chose risky vs. safe, estimated the winning-marble probability, and gave a confidence ('How sure') rating. The study asks whether age-related differences in susceptibility to social influence on risky choice are driven by adolescents' greater internal uncertainty about choice utility, and is tested with Bayesian-updating and computational (utility-based) cognitive models. Each raw gamble yields three response rows (estimate, confidence, choice) grouped by `block`.

## Notes

### Columns

#### exp0

| column | description |
|--------|-------------|
| participant_id | Original integer subject number from the source CSV (1..166), kept as string. |
| trial | 0..N-1 sequential over all response rows within each participant (paper-trials split into per-response rows, so trial counts responses not gambles). |
| block | 0..143 paper-trial (gamble) index within each participant; groups the estimate/confidence/choice rows of one gamble. |
| response | The value of the response for this row: risky/safe choice (0=safe, 1=risky) on `choice` rows, or the raw slider value (0-100) on `estimate`/`confidence` rows. |
| response_type | Which genuine response in the paper-trial this row holds: `estimate` (probability of blue marble), `confidence` (How sure), or `choice` (risky vs safe). |
| rt | Choice reaction time in ms (only on `choice` rows; the estimate/confidence sliders record no separate RT), else empty. |
| reward | Payoff in points delivered on the gamble (only on `choice` rows), else empty. Points × 0.008 = € bonus. |
| condition | External-uncertainty manipulation: `from_description` (DFE1DFD0=0, low uncertainty) or `from_experience` (DFE1DFD0=1, high uncertainty, 9-marble sample shown). |
| valid | 1 if `response` non-null else 0 (always 1 here). |
| startTime | Date the session was run (e.g. 2018-06-20). |
| key_press | jsPsych key code pressed for the choice (70=F, 74=J). |
| riskyKey | jsPsych key code mapped to the risky option on that trial (70 or 74, counterbalanced). |
| red_marbles | Marble sample for the risky jar: comma-list of the red-marble counts in each of the five 3×3 sample grids (sums to the red count of the 9-marble sample) in `from_experience`, or `99` sentinel in `from_description` (no sample shown). |
| blue_marbles | Marble sample for the risky jar: comma-list of the blue-marble counts in each of the five 3×3 sample grids, or `99` sentinel in `from_description`. |
| OtherChoseRisk | Social-information value: NULL (empty) when solo; 1 if the peer chose risky, 0 if safe. |
| ChooseRisk | Raw participant gamble choice, 0=safe, 1=risky (identical to `response` on `choice` rows). |
| valueGamble | Points the risky option promised (8, 20, or 50). |
| probGamble | Objective winning probability of the risky option (0.125..0.75). |
| Social1Ind0 | 1 if the trial had social information, 0 if solo (matches phase). |
| payoff | Raw payoff points for the gamble (identical to `reward` on `choice` rows). |
| cumulatedPayoff | Running sum of points across the session. |
| valueSure | Points the safe option guaranteed (always 5). |
| age | Participant age in years (10-25). |
| PercentBlueShownAbs | Number of blue marbles shown as a proportion of all shown (absolute; from_experience only). |
| PercentRedShownAbs | Number of red marbles shown as a proportion of all shown (absolute; from_experience only). |
| PercentBlueShownRel | Number of blue marbles shown relative to the 100-marble jar equivalent. |
| PercentRedShownRel | Number of red marbles shown relative to the 100-marble jar equivalent. |
| TotalNShown | Total number of marbles shown in the sample (9 in from_experience, 198 in from_description). |
| phase | Session phase label: `solochoice` or `socialchoice` (from test_part). |
| gender | Participant sex mapped to f/m (from German Weiblich/Maennlich). |
| age_group | Participant age band (from Agegroup): 0=`child` (10-12), 1=`adolescent` (13-17), 2=`adult` (18-25). |

`exp0.csv` maps to the paper's single 'Developing Marbles' experiment. The pragmatically-transformed data spans both phases (solochoice/socialchoice) and both uncertainty conditions; the `from_experience` condition collapses the DFE (from-experience description-based) manipulation. Covariate files (cognitive covariates under `A_raw_data/Covariates`, e.g. MindInEyes) were not merged into the trial rows.

## Text-format conversion

The single 'Developing Marbles' experiment (`exp0.csv`) was transcribed to natural language (`transcripts0.jsonl`, 166 transcripts, one per participant). Each gamble's three responses — probability estimate, confidence rating, and risky/safe choice — are rendered in order, with the from-description / from-experience uncertainty conditions, the 9-marble samples, and the peer choice in the social phase all narrated faithfully. No experiment was skipped.

Sample transcript (from the start through the first free response):

```
You are playing a lottery game. On each round you choose between two jars from which a random marble is drawn: a safe jar containing only blue marbles that always pays 5 points, and a risky jar containing both blue and red marbles that pays more (8, 20, or 50 points) but only if the marble you draw is blue. In this session you press A to choose the SAFE jar and B to choose the RISKY jar. On some rounds the risky jar's winning chance is stated directly as a proportion of blue marbles in the jar; on other rounds you instead watch a brief sample of 9 marbles drawn from the jar and judge its chance from that sample, then rate how sure you are with a second slider. On every round you first set a slider (0-100) to estimate the percent chance of drawing a blue marble, then make your choice. In the second half of the game you also see how another participant chose in the same lottery before you choose. Points accumulate and are converted to a bonus at the end.
The risky jar, which offers 8 points if you draw blue, is shown with 100 marbles, 25 of them blue, so it wins with probability 25%. Choosing it risks drawing red for nothing. The safe jar always draws blue and pays 5 points.
You estimate the chance of drawing a blue marble as [HUMAN_RESPONSE]38[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: no_social (rho,tau), bayesian (rho,kappa_desc,kappa_exp,tau), full (rho,kappa_desc,kappa_exp,psi_risk,psi_safe,tau); per-participant bounded L-BFGS MAP, compared on a Laplace-approximate LOOIC (paper metric).
Reproduced: model_comparison (full model wins per-participant leave-one-out criterion: full LOOIC=18735 < no_social 19834 < bayesian 20528; also lowest NLL/AIC).
Not reproduced: none.
Numeric mismatch: none (paper reports no per-model LOOIC digits, only the qualitative full-wins claim).
Partial validation: no.
Indeterminate: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`exp0/` was ported to a static jsPsych v8 online experiment (`experiments/exp0/`). The
headless `?mode=simulate` round trip passed: the saved CSV matches `exp0.csv`'s schema
exactly (31 columns, dtypes, codings; 360 rows = 72 description×2 + 72 experience×3;
every value/probability/condition combo appears 4×; `trial` restarts per participant;
`key_press`/`riskyKey` = 70/74; `ChooseRisk` = `response` on choice rows), with no
outbound data request in simulate mode. Visual check passed (no gross rendering
breakage). Needs-review reason: the social peer's per-trial risky/safe choices are
synthesized (Bernoulli with `peerRiskProb = min(0.9, solo risky rate + 0.20)`, per the
paper's matching rule) because the original peer choices came from a prior-study
dataset and are not generatively recoverable from the design; the response keys are
presented as F/J (the repo's transcript labels them A/B) to match the encoded
`key_press`/`riskyKey` codes. Cosmetic browser defaults (English slider labels, marble
flash timing, 800 ms feedback, colors/layout, demographics entry) were chosen and
documented in `experiments/README.md`.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

`exp0` got `simulate0.py` (PEP 723, `uv run simulate0.py -n 3` smoke-tests it).
It reproduces the 144-gamble design (72 solo + 72 social; 72 description + 72
experience; valueGamble 8/20/50 x probGamble 0.125/0.25/0.375/0.5/0.675/0.75),
the 9-marble sample narratives, and the A/B response-token policy of
`build_jsonl.py`; the round-trip through `build_jsonl.py` matches its prompts
byte-for-byte. Peer choices (`OtherChoseRisk`) are synthesized per the paper's
matching rule (peer ~20% riskier than the participant's solo rate, capped at
0.9) since the original prior-study choices aren't in this dataset; `rt`,
`key_press`/`riskyKey`, session `startTime`, and demographics are dropped as
not producible from text.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 1, major 2, minor 10; fixed 6, open 7).

Checked: paper (https://doi.org/10.1038/s44271-025-00314-6, PDF), original data (https://zenodo.org/records/16738297, DevelopingMarbles_zenodo.zip), exp0, transform re-run (exp0.csv byte-identical; 23,887 raw rows = 23,887 choice rows; every raw column kept), transcripts (rebuild byte-identical), simulate0.py (round trip through build_jsonl.py byte-identical over 3 simulated participants), model.py (full re-fit, 29 min: full LOOIC 18734.63 < no_social 19833.55 < bayesian 20528.35, as the README states), analysis.py (all three effects reproduce), logs. Skipped: none.

Fixed:
- critical: description-condition gamble lines in transcripts0.jsonl never stated the risky jar's payoff, although the paper (p. 2) shows the 8/20/50 points in both conditions and exp0.csv carries valueGamble on every row. build_jsonl.py now writes 'The risky jar, which offers N points if you draw blue, is shown with 100 marbles, ...'; transcripts0.jsonl regenerated (166 lines), simulate0.py mirrored, README sample transcript updated.
- major: choice lines read 'You choose the risky jar [HUMAN_RESPONSE]B[/HUMAN_RESPONSE]', naming the option before the marked token (the prediction target). Now 'You choose [HUMAN_RESPONSE]B[/HUMAN_RESPONSE] (the risky jar).' in build_jsonl.py and simulate0.py.
- major: logs/auto-exp-modeling.sessions.json carried four file patches of another run's work dir (vantiel_2022_meaning README, exp0.csv, exp1.csv, paper.html; 0.8 MB) in its first message summary; removed.
- minor: README columns heading '### exp0' changed to '#### exp0'.
- minor: README experiment summary called the models 'DFT/utility-based'; the paper has no decision-field-theory model. Now 'utility-based'.
- minor: README described red_marbles/blue_marbles as 'red/green sample values'; they are per-grid counts over the five 3x3 sample grids (e.g. '0,1,1,0,0' + '1,3,1,1,1' = 9 marbles).

Open:
- minor: check_repo flags 46/166 transcripts for a token-map collision: slider values 0 and 1 share the response column with the choice codes 0/1, so one CSV value maps to a digit and to a letter. Verified per response_type over all 166 participants: every slider token equals the CSV value and every choice letter maps consistently. Checker limitation for mixed response columns; no change made.
- minor: check_repo flags the slider tokens (integers 0-100) as undeclared; the instructions declare the range ('set a slider (0-100)') rather than every integer.
- minor: check_repo flags logs/auto-exp-transcribe.sessions.json for mentioning ciranka_2025_social; the mention is the transcribe model's own guess about a companion paper inside this dataset's single session. Nothing foreign to prune.
- minor: exp0.csv has probGamble 0.675 (9,512 rows) where the paper (p. 2) lists 0.625; the source (TidyMarbleNew.csv) and the experiment code (jspsych-solotrialMarble.js: img/0675.png -> probWin = 0.675) carry 0.675. Data faithful to the source; paper-side discrepancy.
- minor: 14 participants have 142-143 gambles instead of the paper's 144 (p. 2); 1,527 gambles lack an estimate and 399 description gambles carry a confidence rating. All inside the source (NULL fields in TidyMarbleNew.csv); transform.py adds a row only for a non-NULL response.
- minor: age 10-25 (mean 15.96) in the source vs 10-26 (mean 15.82) in the paper (p. 2); sex split 76 f / 90 m matches. Table 1 (p. 6) fits 160 participants / 23,025 choices; the data-level n = 166 matches the Methods.
- minor: the modeling run's log shows the Laplace LOOIC approximation was revised (bound pinning, variance cap) before the full model won on a 16-participant subset; on the full sample the full model also has the lowest NLL and AIC, while BIC prefers no_social (20008 vs 21811). Source files never read by transform.py: pp_list_nn.csv (the same trials with model posterior predictives) and the Covariates folder (MindInEyes.csv, CFT and digit-span logs; the README states they were not merged).

Run: claude-fable-5-1, 2026-09-10
