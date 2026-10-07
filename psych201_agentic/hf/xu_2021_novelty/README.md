---
tags:
- paradigm:planning
- cognitive-modeling:needs-review
- psych-101
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---

# xu_2021_novelty

- Paper: https://doi.org/10.1371/journal.pcbi.1009070
- Data source: https://github.com/EPFL-LCN/pub-xumodirshanechi2021-PlosCB
- PDF: https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1009070&type=printable
- Full text: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1009070
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
He, X., Modirshanechi, A., Lehmann, M. P., Gerstner, W., & Herzog, M. H. (2021). Novelty is not surprise: Human exploratory and adaptive behavior in sequential decision-making. PLoS Computational Biology, 17(6), e1009070. https://doi.org/10.1371/journal.pcbi.1009070

## Experiment summary
A single experiment with 12 human participants (N=12; subject 10 quit) performing a sequential grid-world decision-making task. Participants navigate from a start state to a goal across 5 episodes in each of two blocks, making one discrete 4-action choice per trial; reward arrives only on reaching the goal. Block 1 (env 3) contains many novel states to probe novelty-driven exploration; block 2 (env 4) swaps the transitions of two states to test surprise-driven re-adaptation. The paper asks whether a novelty (exploration bonus) is distinct from surprise (prediction-error-driven learning), fitting the SurNoR model-based RL algorithm and comparing 13 RL models against the 3,047 trials of choice data.

## Notes

### Columns

#### exp0

Sequential grid-world decision task (SurNoR "SwitchState" experiment, Fig 1 of Xu, Modirshanechi et al. 2021). One row per discrete action choice.

| column | description |
|--------|-------------|
| participant_id | Original subject number from source `BehavData_SwitchState.csv` column `subID` (1-9, 11-13; subject 10 absent because they quit). |
| trial | 0..N-1 response counter, continuous across the whole session within each participant (no restart at block or episode). |
| block | 0-indexed block label; source column `env` = paper block + 2, so env 3→block 0 (block 1, novelty/exploration), env 4→block 1 (block 2, transition-switch/surprise). |
| response | Chosen action, 0-indexed (`action`-1); source `action` values 1-4 map to 0-3 (left/up/down/right moves on the grid). |
| env | Raw source block code (3 or 4) kept verbatim; equal to block + 2. |
| epi | Episode number 1..5 within a block (each participant runs 5 episodes per block; each episode ends when the goal is reached, reward 1). |
| state | Current grid state before the move, 0-indexed in the paper's numbering (Fig 1B): paper states 1..10 → 0..9 (progressing states 0..6, trap states 7..9), goal G → 10 (never appears here because no action is taken at the goal). Source states 1..11 were remapped with the source ReadMe table (source 1 = goal; source 2..11 = paper 1, 8, 3, 5, 2, 9, 10, 4, 6, 7). |
| next_state | Grid state after the move, same numbering as `state` (10 = goal). |
| reward | Reward received on the trial (0 or 1; 1 = reached goal), source units. |

`HardEnvironment11s.mat` and `ActionClasses.mat` hold static environment structure (block transition matrices, episode initial states, good-vs-neutral action classes) rather than per-trial recorded behavior; the per-trial `next_state`/`reward` already witness the outcomes, so the .mat files are not merged. `EEG_Frontal.csv` is EEG data, not behavioral.

## Text-format conversion

All 12 participants of exp0.csv were transcribed into transcripts0.jsonl (3,047 free actions total). The grid-world navigation task is textifiable: states are rendered as neutral room numbers and the four grey action buttons as A/B/C/D, preserving the sequential decision-making and transition-learning structure (each trial's state, chosen action, resulting state, and reward). No experiments were skipped.

### Sample transcript

```
You are navigating a maze of 11 rooms, each shown as an image on screen. One of the rooms is the goal image; your task is to find the shortest path to it. At each room you see four grey buttons below the image. Button 1 is pressed with D, button 2 with A, button 3 with C, button 4 with B. Pressing a button moves you to the next room. You receive no feedback along the way; when you reach the goal image you earn a reward and the episode ends. You will run several episodes, each starting in a new room.
Episode 1 starts in a new room.
You are in room 5. You press [HUMAN_RESPONSE]B[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

`exp0` got a text simulator (`simulate0.py`) that reproduces `transcripts0.jsonl`
format-identically: the round-trip check through `build_jsonl.py` passed
byte-for-byte. No experiments were skipped. Assumptions surfaced: the per-episode
start rooms are fixed to the shipped values {1:5, 2:8, 3:3, 4:4, 5:7} (the paper
says "chosen randomly, but fixed across participants" and lists them as i(1)=6,
i(2)=9, i(3)=4, i(4)=5, i(5)=8 in its 1-based numbering, p. 21), and the deterministic
env-3 / env-4 transition tables are taken from `exp0.csv`, whose per-trial
`next_state` fully witnesses them (the paper's main text prints only the
schematic graph).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none run.
Indeterminate: The SurNoR model family (18-parameter model-based/hybrid RL with a
surprise-modulated Bayesian world model, novelty Q-learning, eligibility traces and a
hybrid policy) was implemented in a JAX forward pass transcribed from the authors'
reference code (EPFL-LCN/pub-xumodirshanechi2021-PlosCB). The forward is internally
self-consistent, but with the paper's own Overall fitted parameters it achieves a
log-likelihood of about -3554 on the 3047 choices, far from the -2891.97 the paper
reports for the same fit; a careful cross-check could not be reconciled, and an
ablation (pure model-free) even looked better than full SurNoR at the paper's params.
Because the forward's faithfulness could not be established, no trustable model
comparison could be run, and the model was not fitted/uploaded.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Online experiment

`exp0/` got a runnable static jsPsych v8 experiment (`experiments/exp0/`). The
headless round trip passed: it reproduces the dataset schema exactly
(`participant_id,trial,block,response,env,epi,state,next_state,reward`), the
deterministic transition matrices, the `reward` coding, and the 5-episodes-per-block
structure, and the visual check found no rendering breakage. No experiments were
skipped. Assumption surfaced: the original image stimuli are not in the dataset
(only the `.mat` environment and CSV), so each state is shown as a distinct,
neutral coloured "room" card; timing defaults from the paper (700–1700 ms blank
after each response) are applied. This is browser-only presentation and does not
change the data or the task.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 2, minor 4; fixed 5, open 1).

Checked: paper (https://doi.org/10.1371/journal.pcbi.1009070, PDF), original data (https://github.com/EPFL-LCN/pub-xumodirshanechi2021-PlosCB, SurNoR_2020/data/BehavData_SwitchState.csv, 3,047 rows, 12 participants), exp0, transform re-run (byte-identical to exp0.csv before and after the fix), transcripts (build_jsonl.py rebuild byte-identical), simulator (simulate0.py -n 2 --seed 0 runs; round trip through build_jsonl.py byte-identical; its transition tables and start states match exp0.csv), analysis (analysis.py: all 3 effects reproduce), modeling (no model.py; the section reports nothing reproduced and the cognitive-modeling:needs-review tag agrees), logs (no secrets). Skipped: none.

Fixed:
- exp0.csv `state`/`next_state` used the source's 1-based numbering (goal = 1, states 2..11); the schema requires 0-indexed states. transform.py now maps them to the paper's numbering 0-indexed (paper states 1..10 → 0..9, goal G → 10) with the source ReadMe table; exp0.csv regenerated, every other column unchanged. Cross-checked against the paper: episode start states i(1..5) = 6, 9, 4, 5, 8 (p. 21) → 5, 8, 3, 4, 7 in the data; progressing states 0..6 and trap states 7..9 (Fig 1B); swapped states 2 and 6 (paper 3 and 7, p. 4); the neutral action in state 0 is action 1 and in state 2 is action 2 (p. 4).
- transcripts0.jsonl announced 'Block 1 begins.' and 'Block 2 begins: you keep exploring the maze…' at the state swap; the paper (p. 4) says the block division and the swap were unknown to the participants and not announced. build_jsonl.py now numbers the episodes 1..10 without block lines; transcripts0.jsonl rebuilt (3,047 responses, unchanged), simulate0.py mirrored (round trip byte-identical), README sample transcript updated.
- README Experiment summary said the choices came 'with reward feedback'; the paper (p. 4) gives no intermediate reward or sign of progress. Reworded to 'reward arrives only on reaching the goal'.
- README Columns heading '### exp0' → '#### exp0' (template).
- README Simulators note and the simulate0.py docstring quoted the episode start rooms in the old numbering as an assumption; the paper's Methods (p. 21) list them (i(1)=6, i(2)=9, i(3)=4, i(4)=5, i(5)=8) and they match the data. Values updated to the new numbering with the page reference.

Open:
- minor: the paper (p. 4) reports 34–214 actions (mean 118, std 54) in block 1 episode 1 and 68 ± 16 in block 2 episode 1; the data give 33–213 (mean 117.0, std 54.2) and 67.0 ± 15.9, one action fewer per episode. The raw source has the same counts, so the paper counts one more than the recorded actions (a constant +1 convention); the data is faithful to its source. The other paper numbers match: 12 participants (14 joined, 2 quit, p. 20), 5 episodes per block, 8 of 12 participants met state 6 (paper 7) in block 2 episode 1 (Fig 6), 4 participants avoided the trap states there (Fig 2).

Run: claude-fable-5-1, 2026-09-13
