---
tags:
- paradigm:bandit
- cognitive-modeling:pass
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
---
# anll_2024_comparing

- Paper: https://doi.org/10.1038/s41562-024-01894-9
- Data source: https://osf.io/yebm9/ (also code at https://github.com/hrl-team/WEIRDbandit)
- Full text: https://www.nature.com/articles/s41562-024-01894-9
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Anlló, H., Bavard, S., Benmarrakchi, F., Bonagura, D., et al. (2024). Comparing experience- and description-based economic preferences across 11 countries. Nature Human Behaviour, 8(8), 1554-1567.

## Experiment summary
A cross-cultural study across 11 countries (N=561) comparing economic preferences under two modes of decision-making. In the experience-based (reinforcement-learning/bandit) task (exp0), participants make repeated binary choices between two options that differ in reward probability and magnitude across gain/loss contexts (training, learning, and transfer phases), receiving stochastic feedback; in the description-based lottery task (exp1), they make risky choices between a certain option and a gamble described in terms of probabilities and magnitudes. Both experiments record trial-level choice (left/right), response time, stochastic reward, and whether the value-maximizing option was chosen. The research question asks whether outcome context-dependence and risk/preference patterns (RL learning, probability weighting, loss aversion) generalize beyond WEIRD samples, with reinforcement-learning and description-based (prospect theory) cognitive models fitted to the choice data.

## Notes

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | Remapped subject code `P000`..`P560` (first-appearance order). Raw Prolific-style IDs (`1692327`, `9089552870`, masked public IDs) were dropped as PII. |
| task_id | 0-indexed decision block per session×phase: training (session -1, or -2 repeat training when present), learning, transfer. Trial state resets per task_id. |
| phase | `training` / `learning` / `transfer`, from source `WhichPhase` (0/1/2). |
| which_phase | Raw source `WhichPhase` value (0/1/2) as text. |
| trial | 0-indexed trial within each `(participant_id, task_id)`, in source presentation order. |
| response | Chose left/right symbol, raw `ChoseLorR`: -1=left, 1=right (a valid choice code, not missing). |
| rt | `ResponseTime` in milliseconds (1 row has an anomalous small negative value preserved from source). |
| reward | `RewardGoodorBad`: whether the chosen option paid out this trial (0/1, stochastic). |
| correct | `ChoseGoodorBad`: whether the participant chose the higher-expected-value option (0/1). |
| condition | Decision context 1-8 (source `Condition`); each maps to a [prob,magnitude] pair vs its competitor (see README_CDEP.txt). |
| Participant.Starting.Group | Testing-session group label per country (e.g. `Group_AR`). |
| TrialNumber | Source trial number by phase (1-indexed). |
| SymbolLeft / SymbolRight | Integer symbol identity shown left/right. |
| Reward | Source cumulative reward in points (running total within session). |
| OtherRewardGoodorBad | Whether the unchosen option would have paid out (0/1). |
| Session | Session index (-2 repeat training, -1 training, 0 main). |
| Proba1 / Proba2 | Reward probability of option 1/2. |
| Magnitude1 / Magnitude2 | Reward magnitude (points) of option 1/2. |
| Valence, Information, InvertedPosition | DEPRECATED columns carried verbatim from source. |
| Option1 / Option2 | Chosen-symbol integer for option 1/2. |
| ChoiceTime | System time of the choice (ms). |
| TrialPerCond | Cumulative trial count. |
| Language | UI/instructions language code (e.g. `es`). |
| Age | Participant age in years. |
| gender | Sex lowercased (`f`/`m`). |
| FinalPayment | Final points payment to participant. |
| CRT | Score on 7-item Cognitive Reflection Test. |
| CvIHorInd / CvIVerInd / CvIHorCol / CvIVerCol | Horizontal/Vertical Individualism/Collectivism scores. |
| RelIntellect / RelIdeology / RelPub / RelPriv / RelExp | Centrality-of-Religiosity dimension scores. |
| TIPIAgr / TIPIOpen / TIPIEmostab / TIPICons / TIPIExtra | TIPI personality dimension scores. |
| SESInfant / SESAdult / SESsubj | Perceived SES (childhood, adult, subjective). |
| deltaEV | Difference in expected value between the two options in the context. |
| deltaEVfactor | Same EV difference, doubled, treated as a factor in the source (levels `0.5`,`1.5`,...). |
| Country | Participant country. |

### exp1
| column | description |
|--------|-------------|
| participant_id | Remapped subject code `P000`..`P560`, identical to exp0 (same source order). |
| task_id | Always 0 within exp1: one lottery phase per participant. |
| phase | `lottery` (source `WhichPhase` 3). |
| which_phase | Raw source `WhichPhase` value (3) as text. |
| trial | 0-indexed trial within each `(participant_id, task_id)` (0..31). |
| response | Chose left/right symbol, raw `ChoseLorR`: -1=left, 1=right (valid choice code). |
| rt | `ResponseTime` in milliseconds. |
| reward | `RewardGoodorBad`: whether the chosen option paid out (0/1). |
| correct | `ChoseGoodorBad`: chose the higher-expected-value option (0/1). |
| condition | Decision context 9-12 (source `Condition`; description-based lotteries, plus 5-8 recorded here). |
| All other columns | Identical meanings to exp0 (see table above); this file holds only lottery-phase rows. |

Both experiments derive from the single source CSV `WEIRD__CDep_NoExclusions.csv` (OSF, `https://osf.io/yebm9/`). `exp0.csv` = experience-based / reinforcement-learning phases (source `WhichPhase` 0/1/2: training, learning, transfer; decision contexts 1-8, 142,303 rows). `exp1.csv` = description-based risky (lottery) phase (source `WhichPhase` 3, 17,952 rows). The OSF repo also contains simulated/model-derived files (SimmedataSCALINGRL.csv, SimmedataSCALINGLOT.csv, LOTSimmChoices.csv), worldcities.csv, and supplementary materials which are not human behavioral trial data and were not transformed. All 561 participants completed both phases (within-subject).

## Text-format conversion

Both experiments were transcribed (561 transcripts each). exp0 (experience-based RL bandit) is narrated with the abstract cues given stable numeric identities: because the screen left/right placement of each cue is not recoverable from the source columns, the marked response is the chosen cue's number, recovered from `correct` plus the expected-value ordering (no ties in exp0). Rewards (and counterfactual outcomes in the learning phase) are narrated as points; the transfer phase receives no feedback, as in the original. exp1 (description-based lottery) shows each option's explicit probability and magnitude and records the left/right choice. No experiment was skipped.

### Sample transcript (exp0)

```
You are playing an economic decision-making game. Over many trials you choose between two options, trying to maximize the total points you earn; your points are converted into a bonus payment at the end. You are not told the reward chance or amount of each option in advance -- you must learn which option pays off from the feedback you get after each choice. On each trial two cues appear, each labeled by a number. Press the number of the cue you want to choose. After you choose, you see how many points you gained. Later the same cues are rearranged into new pairs, and you choose based on what you learned, this time receiving no feedback.
Training phase. You see cue 10 and cue 4. You press [HUMAN_RESPONSE]10[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

Text-based simulators `simulate0.py` (experience-based RL task) and `simulate1.py` (description-based lottery) reproduce the transcripts' format exactly: the round-trip check (simulated `expN.csv` run through `build_jsonl.py` regenerates the simulator's own prompts byte-for-byte) passes for both. The simulators follow the README_CDEP condition→[probability, magnitude] mapping; rewards (and counterfactual outcomes in learning) are drawn stochastically; transfer/lottery phases give no feedback. ASSUMPTION: the transfer phase re-pairs fresh distinct cue identities rather than the source's specific 8-cue re-pairing; cue labels are arbitrary participant integers, so transcript format is unaffected. No experiment was skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments got a static jsPsych v8 port under `experiments/exp0/` (experience-based RL task) and `experiments/exp1/` (description-based lottery). The headless `?mode=simulate` round trip passed for both: the saved CSV reproduces the exact 53-column schema of the repo's `expN.csv` (`task_id` 0/1/2 with `trial` restarting at 0, `response` -1/1, `reward`/`correct` 0/1, `Reward` cumulative), with `rt` filled from the browser and no outbound data requests. Participant-level metadata (age, gender, country, questionnaire scores, payment, language, starting group) is not collected by the task and is left blank, matching `simulate0.py`/`simulate1.py`. The transfer phase re-pairs the four learning cues as in `simulate0.py`. Only cosmetic browser defaults were chosen (cue/gamble color, phase-Continue screens, 1200 ms feedback, 600 ms inter-trial gap); no assumption changes the task or the recorded data.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: SCALING-RL Q-learning (beta, alpha, nu, forget; MAP with beta~Gamma(1.2,5), alpha/nu/forget~Beta(1.1,1.1)) on exp0 learning+transfer; SCALING-lottery expected-value softmax (beta, nu) on exp1, per-participant bounded L-BFGS (per-participant, then one-way ANOVA / Pearson across countries).
Reproduced: nu_RL_invariant_across_countries (p=0.05 vs paper p=0.07, n.s.); nu_LOT_differences_by_country (p=0.001 vs paper p<0.01); nu_LOT_decorrelated_from_nu_RL (r=0.03, p=0.53 vs paper r=0.08, p=0.24).
Not reproduced: none.
Numeric mismatch: none material.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
