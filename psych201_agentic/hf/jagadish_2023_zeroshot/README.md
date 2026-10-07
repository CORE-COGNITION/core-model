---
tags:
- paradigm:bandit
- cognitive-modeling:needs-review
- psych-101
- psych-201
- js-experiment:needs-review
- text-format:pass
- simulator:pass
- verification:pass
---
# jagadish_2023_zeroshot

- Paper: https://doi.org/10.31234/osf.io/ymve5
- Data source: https://github.com/akjagadish/resource-rational-compositional-RL
- PDF: https://osf.io/ymve5/download
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Jagadish, A. K., Binz, M., Saanum, T., Wang, J. X., & Schulz, E. (2023). Zero-shot compositional reasoning in a reinforcement learning setting. PsyArXiv Preprints. https://doi.org/10.31234/osf.io/ymve5

## Experiment summary
Two online Prolific experiments using a compositional multi-armed bandit paradigm. Each task contains three 6-arm sub-tasks (5 arm-choice trials each); participants first learn two latent reward functions (linear or periodic) and must then compose them on a final sub-task, under an additive composition rule (exp 1, N=289) or a change-point rule (exp 2, N=300). Participants were randomly assigned to a curriculum condition (20 tasks; 300 trials) or a non-curriculum condition (100 trials, only the compositional sub-task). The primary response is a discrete arm choice (0-5) with the received reward. The study asks whether people can perform zero-shot compositional inference in reinforcement learning, finds that they can but deviate from optimality, and an eight-model computational comparison (Bayesian mean-tracking, GP regression, meta-learned RL2 / resource-rational RR-RL2) shows the resource-rational model fits behavior best.

## Notes

- Sample: the paper (p. 12) reports 200 participants for experiment 1 (103 female, mean age 28.90) and 211 for experiment 2 (96 female, mean age 27.58); the source ships 289 and 300. The difference is the `loocompositional` condition (89 participants per experiment), a held-out-composition curriculum variant present in the task code but not described in the paper. Restricted to `experiment` in {`compositional`, `noncompositional`} the CSVs give exactly N=200 (103 f, mean age 28.90) and N=211 (96 f, mean age 27.58), and the paper's first-trial means reproduce (exp0 regret 2.163/4.055, exp1 1.937/3.096). The source's processed `data/experiment1.csv`/`experiment2.csv` hold only 274 and 286 participants; this dataset uses the raw per-participant JSON files in full.
- `env`: for 204 of 13020 sub-task blocks in exp0 (19 participants) and 83 of 13920 in exp1 (19 participants), the environment file at the recorded path in the source does not reproduce `maxreward`/`bestoption` (likely an asynchronous-load artefact of the original task software). `reward`, `regret`, `maxreward`, and `bestoption` are the values the task software actually used and are consistent with each other on every row (reward = max(0, y + N(0, 0.1)); regret = max(y) - y[chosen]).

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Anonymized participant code (`P000`, `P001`, ... in first-appearance order, assigned per experiment file); replaces the raw Prolific subject ID |
| task_id | 0..N-1 per participant; each value is one 6-arm bandit sub-task (a fresh state reset), blocks in presentation order |
| trial | 0..4 within each (participant_id, task_id); arm-choice index within a sub-task |
| response | Selected arm, 0..5 (which of the 6 slot-machine arms was chosen) |
| reward | Numeric reward (coins) actually received on that trial, raw source value |
| rt | Reaction time in milliseconds for that arm choice (source `times`) |
| regret | Per-trial regret = (max reward of sub-task) - (noise-free reward of the chosen arm), raw source value; 0 iff the chosen arm is `bestoption` |
| condition | Reward-function label of this sub-task, e.g. `neg`/`pos` (linear), `odd`/`even` (periodic), or composed `negeven`/`posodd`/`negodd`/`poseven` |
| composition | JSON list of the task's three sub-task function labels [f1, f2, composition] (non-curriculum: one-element list with the composed label only); repeated across that task's rows |
| task | 0..19, the casino/task number (20 per session); task = task_id // 3 (curriculum) or // 1 (non-curriculum) |
| subtask | Position within task: curriculum 0,1,2; non-curriculum set to 2 (they only played the compositional sub-task) |
| phase | `curriculum` (60 blocks, 300 trials) or `non_curriculum` (20 blocks, 100 trials) |
| experiment | Raw source label: `compositional`/`loocompositional` (curriculum) or `noncompositional` (non-curriculum) |
| instcounter | Raw per-participant integer counter flag from source |
| age | Participant age in years (self-reported integer) |
| gender | `f`/`m`/`other` mapped from source coding 0=Female, 1=Male, 2=Diverse |
| hand | Self-reported hand handedness flag 0/1 from source |
| money | Total money earned (GBP, string) from source |
| maxreward | (per sub-task) maximum reward available across its 6 arms (source `maxrewards`) |
| bestoption | (per sub-task) index of the optimal arm 0..5 (source `bestoptions`) |
| env | Path of the bandit environment JSON for this sub-task (e.g. `envs/add/negeven/negeven45.json`) |
| eval | JSON list of composed functions used for evaluation for this participant |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Anonymized participant code (`P000`, `P001`, ... in first-appearance order, assigned per experiment file); replaces the raw Prolific subject ID |
| task_id | 0..N-1 per participant; each value is one 6-arm bandit sub-task (a fresh state reset), blocks in presentation order |
| trial | 0..4 within each (participant_id, task_id); arm-choice index within a sub-task |
| response | Selected arm, 0..5 (which of the 6 slot-machine arms was chosen) |
| reward | Numeric reward (coins) actually received on that trial, raw source value |
| rt | Reaction time in milliseconds for that arm choice (source `times`) |
| regret | Per-trial regret = (max reward of sub-task) - (noise-free reward of the chosen arm), raw source value; 0 iff the chosen arm is `bestoption` |
| condition | Reward-function label of this sub-task, e.g. `neg`/`pos` (linear), `odd`/`even` (periodic), or composed `oddneg`/`oddpos`/`evenneg`/`evenpos` |
| composition | JSON list of the task's three sub-task function labels [f1, f2, composition] (non-curriculum: one-element list with the composed label only); repeated across that task's rows |
| task | 0..19, the casino/task number (20 per session); task = task_id // 3 (curriculum) or // 1 (non-curriculum) |
| subtask | Position within task: curriculum 0,1,2; non-curriculum set to 2 (they only played the compositional sub-task) |
| phase | `curriculum` (60 blocks, 300 trials) or `non_curriculum` (20 blocks, 100 trials) |
| experiment | Raw source label: `compositional`/`loocompositional` (curriculum) or `noncompositional` (non-curriculum) |
| instcounter | Raw per-participant integer counter flag from source |
| age | Participant age in years (self-reported integer) |
| gender | `f`/`m`/`other` mapped from source coding 0=Female, 1=Male, 2=Diverse |
| hand | Self-reported hand handedness flag 0/1 from source |
| money | Total money earned (GBP, string) from source |
| rewardorder | 0/1 flag: randomized order of the two halves in the change-point composition rule |
| maxreward | (per sub-task) maximum reward available across its 6 arms (source `maxrewards`) |
| bestoption | (per sub-task) index of the optimal arm 0..5 (source `bestoptions`) |
| env | Path of the bandit environment JSON for this sub-task (e.g. `envs/changepoint/oddneg/neg40.json`) |
| eval | JSON list of composed functions used for evaluation for this participant |

## Update (2026-08-13)
- PII removal: `participant_id` remapped from raw 24-hex Prolific IDs to anonymized codes `P000`, `P001`, ... in first-appearance order, independently per file (no ID appeared in both files; exp0: 289 participants, exp1: 300 participants).
- PII removal: dropped the `studyID` column (Prolific study ID) from exp0.csv and exp1.csv.

CSVs fixed in place from the previous release; transform.py updated to produce the same output
from raw. The previous version remains in the repo's git history.

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Indeterminate: The only formal modeling results are a Bayesian model comparison among eight models and RR-RL2 description-length regressions. The winning model (RR-RL2; exceedance probability 0.99, posterior model frequency 0.704/0.741) and the runner-up meta-RL agent (RL2) are GRU-based meta-reinforcement-learning neural networks, which are out of scope. The paper reports no standalone non-neural modeling result, so every modeling claim depends on a neural-net candidate.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments got a static jsPsych v8 build: `experiments/exp0/`
(additive composition) and `experiments/exp1/` (change-point composition),
rebuilt from the paper and the original task code (no `simulateN.py` exists for
this dataset). Both reproduce the source task structure (per-condition
curriculum / non-curriculum, 6-arm bandits, 5 trials per sub-machine,
composition rules) and log the exact `exp0.csv` / `exp1.csv` schemas; the
headless `?mode=simulate` round trip passed for both (columns, 0-indexing,
task/subtask mapping, counts, `money`). `result` `needs-review`: the reward
environments are **regenerated in the browser** from the source's generative
families rather than shipping the original pre-generated env corpus (which a
static site cannot contain) — an assumption about stimulus content, not about
the task structure, response coding, or schema. Reward magnitudes were
calibrated to the observed population means. Cosmetic browser defaults
(feedback/ITI timing, button colors, layout) are noted in
`experiments/README.md`.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Text-format conversion

Both experiments were transcribed (exp0.csv, exp1.csv) as textifiable 6-arm
bandit sessions under the Bandit City slot-machine cover story; the arm choice
(0-5) is rendered as the corresponding keyboard letter (S/D/F/J/K/L) and wrapped
in `[HUMAN_RESPONSE]` as the free choice, with the coins won narrated as the
outcome. No experiments were skipped.

Sample transcript (exp0.csv, start through the first response):

```
You are a gambler visiting the fictional town of Bandit City. Over the session you visit a series of casinos and play slot machines, trying to win as many coins as possible. Every slot machine is made by one of two companies, Blue Lagoon and Green Geeks, and all machines from the same company pay out according to the same hidden pattern (you are not told which company has which pattern, so you learn it by playing). Each slot machine has six buttons in a row, labeled S, D, F, J, K, L. On every trial you press exactly one button to play that arm and you win some coins. For this study the manufacturers only let you play the composition slot machine. Its payout for an arm pays the sum of what the two companies' machines would have paid on that same arm. On each trial, press the letter of the arm you want to play: S, D, F, J, K, or L.

Casino 0, machine 3: You press [HUMAN_RESPONSE]S[/HUMAN_RESPONSE]
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Both experiments got a simulator (`simulate0.py` additive rule, `simulate1.py`
change-point rule), each regenerating the 6-arm compositional bandits from the
paper's generative families (eqs 2-5) plus the task code's per-trial reward
rule (reward = max(0, y + N(0, 0.1))), with the three curriculum conditions
(compositional/loocompositional/noncompositional) drawn per participant and
the change-point halves randomized per participant (`rewardorder`). The
round-trip check through `build_jsonl.py` passed byte-identically for both
(columns mirror the repo CSVs minus `rt` and demographics). ASSUMPTIONs noted
in the class docstrings: low-slope/small-amplitude rejections (|w| < 0.2,
A < 0.5) for the unpublished piloting filter, and the reward floor at 0 from
the original JS task code.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 1, minor 8; fixed 8, open 1).

Checked: paper (https://doi.org/10.31234/osf.io/ymve5; PDF https://osf.io/ymve5/download, 18 pages), original data (https://github.com/akjagadish/resource-rational-compositional-RL: 289 + 300 raw participant JSON files, env corpus, task JavaScript), exp0-exp1, transform re-run, transcripts, simulators (round trip through build_jsonl.py), modeling (no model.py; section and cognitive-modeling:needs-review tag agree), analysis, logs. Skipped: none.

Fixed:
- logs/auto-exp-modeling.sessions.json carried a README patch for another dataset (jansen_2021_rational) in the first message's summary diffs; entry removed, JSON re-serialized with the original formatting.
- README described `regret` as (max reward) - (received reward); the task code (compositionalbandit.js line 616) computes max(y) - y[chosen] without the reward noise, and regret equals maxreward - reward on 0% of rows. Column description corrected in both tables.
- README described `composition` as a three-label list; the non-curriculum rows (exp0 10800, exp1 10200) carry a one-element list such as ["poseven"]. Column description extended in both tables.
- README gave N=289 / N=300 as the samples; the paper (p. 12) reports 200 (103 female, mean age 28.90) and 211 (96 female, mean age 27.58). The difference is the `loocompositional` condition (89 participants per experiment) that the paper does not describe; compositional + noncompositional give exactly the paper's N, sex counts, mean ages, and first-trial means (exp0 regret 2.163/4.055, exp1 1.937/3.096). Notes bullet added.
- For 204 of 13020 (exp0, 19 participants) and 83 of 13920 (exp1, 19 participants) sub-task blocks the env file at the recorded `env` path does not reproduce maxreward/bestoption, while reward/regret/maxreward/bestoption agree with each other on every row (reward noise sd 0.100 on matching rows, as eq. 1). Source-internal; Notes bullet added, data unchanged.
- analysis.py original_effect_size for zero_shot_above_chance exp0 was 0.233; the paper (p. 3) gives P(optimal) = 0.382, minus chance 1/6 = 0.215. Corrected; effect still reproduces.
- analysis.py original_effect_size for learning_continues_in_composition exp0 was the pooled trial effect -0.32; the function fits curriculum-only slopes, for which the paper (p. 3) gives -0.21 (exp1 already used the curriculum-only -0.216). Corrected, docstring quote extended; effect still reproduces.
- README Columns sub-headings `### exp0` / `### exp1` set to the template's `#### exp0` / `#### exp1`.

Open:
- minor: the transcript and simulator instructions do not state that machine 1 (linear company) and machine 2 (periodic company) keep the same company in every casino; participants saw the company colour per machine (task code lines 64-81, paper p. 12-13). The sub-task order is fixed in the data, so the numbering carries the same information implicitly. Left as the transcription's wording choice.

Run: claude-fable-5-1, 2026-09-10
