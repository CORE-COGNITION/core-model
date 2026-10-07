---
tags:
- paradigm:two-step-task
- cognitive-modeling:pass
- psych-101
- text-format:pass
- simulator:pass
- verification:pass
---

# kool_2016_when

- Paper: https://doi.org/10.1371/journal.pcbi.1005090
- Data source: https://github.com/wkool/tradeoffs (repo archived; accessed via GitHub archive tarball)
- PDF: https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1005090&type=printable
- Full text: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005090
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Kool, W., Cushman, F. A., & Gershman, S. J. (2016). When does model-based control pay off? PLoS Computational Biology, 12(8), e1005090. https://doi.org/10.1371/journal.pcbi.1005090

## Experiment summary
Two two-step sequential decision experiments test when model-based control pays off. In each trial participants make a stage-1 choice between two stimuli that transition (common/rare, 70/30) to a second stage, then choose among two options yielding points with drifting reward probabilities (Gaussian random walk). Experiment 1 (exp0, N=206 in data; paper reports 207) uses the original Daw two-step structure; Experiment 2 (exp1, N=200 in data; 199 completers reported) uses a novel task with four stage-1 choices and integer reward magnitudes from -4 to +5 points, designed so model-based planning yields an accuracy-demand trade-off; participants spontaneously increased model-based control there. Responses are stage-1 and stage-2 stimulus choices (plus RTs); the paper shows by simulation that standard two-step tasks lack this trade-off and fits hybrid model-based/model-free reinforcement-learning models (weighted Q-values, softmax) to quantify each participant's reliance on model-based control.

## Notes

### Columns

#### exp0 (Experiment 1, Daw two-step paradigm; 206 subjects x 150 trials, 2 responses/trial)

| column | description |
|--------|-------------|
| participant_id | Original subject ID from the source .mat, `subject_1`..`subject_206` (matches subinfo.mat) |
| trial | 0..299, sequential response index within participant (2 responses per paper-trial; whole session: practice then test) |
| block | 0..149, paper-trial index within participant; the two rows of a block are the stage-1 then stage-2 response of one trial |
| stage | Which decision of the two-step trial this row records: `stage1` (spaceship choice) or `stage2` (alien choice) |
| phase | `practice` = 25 self-paced warm-up trials (no time limit); `test` = 125 timed trials (2 s per stage) |
| response | 0/1, 0-indexed identity of the stimulus chosen at that stage (0 = stimulus coded 1, 1 = stimulus coded 2), NOT screen position (see stim_*_left/right); empty when that stage timed out |
| rt | Reaction time in ms for this row's stage response (`rt_1` on stage1 rows, `rt_2` on stage2 rows); empty on a timed-out stage |
| state | 0-indexed stage context: 0 on stage-1 rows, `state2`-1 on stage-2 rows |
| reward | Binary win at stage 2 (0/1); empty on a timed-out stage-2 and on stage-1 rows (reward delivered after the stage-2 response) |
| valid | 1 unless this row's response timed out (the source's `rt_1`/`rt_2` == -1; those cells are empty here) |
| stim_1_left | Stage-1 spaceship identity (1/2) shown on the left (side shuffled per trial) |
| stim_1_right | Stage-1 spaceship identity (1/2) shown on the right |
| choice1 | Raw stage-1 choice as recorded by the task: 1/2 = chosen spaceship identity; empty on a timeout |
| rt_1 | Raw stage-1 reaction time in ms; empty on a timeout |
| stim_2_left | Stage-2 alien identity (1/2) shown on the left |
| stim_2_right | Stage-2 alien identity (1/2) shown on the right |
| choice2 | Raw stage-2 choice: 1/2 = chosen alien identity; empty on a timeout |
| rt_2 | Raw stage-2 reaction time in ms; empty on a timeout |
| state2 | Raw second-stage planet reached (1/2); empty on a missed trial |
| common | Transition type: 1 = common (rocket1 -> planet1 or rocket2 -> planet2, the 70% pairing), 0 = rare (the 30% cross); empty on a missed trial |
| score | Running total of points at trial end (each win adds 1) |
| ps1a1 | Win probability on this trial for state2=1 alien 1 (drifting Gaussian random walk, bounded 0.25..0.75) |
| ps1a2 | Win probability for state2=1 alien 2 |
| ps2a1 | Win probability for state2=2 alien 1 |
| ps2a2 | Win probability for state2=2 alien 2 |
| trial_number | Source trial index, 0-indexed, restarting within each phase (0..24 practice, 0..124 test) |
| time_elapsed | jsPsych `time_elapsed` in ms at the end of this trial (elapsed since page load) |
| age | Participant age in years from subinfo.mat |
| gender | Participant sex from subinfo.mat: `f` / `m` |
| score_final | Final session score (total points) from subinfo.mat; equals the last trial's `score` |
| time_total_ms | Total session elapsed time in ms recorded at the demographics/save step (subinfo.mat `time_elapsed`) |

#### exp1 (Experiment 2, novel two-step paradigm; 200 subjects x 150 trials, 1 response/trial)

| column | description |
|--------|-------------|
| participant_id | Subject ID, `subject_1`..`subject_200`; `subject_200` was relabeled from a raw platform worker ID in the source and is absent from subinfo.mat, so its age/gender/score_final/time_total_ms are empty |
| trial | 0..149, sequential trial/response index within participant (whole session: practice then test) |
| block | 0..149, paper-trial index within participant (one response per paper-trial) |
| phase | `practice` = 25 self-paced warm-up trials (no time limit); `test` = 125 timed trials (2 s per stage) |
| response | 0/1, within-state stimulus identity chosen: 0 = lower-numbered rocket of the current state (choice1 in {1,3}), 1 = higher-numbered (choice1 in {2,4}); empty if stage-1 timed out |
| rt | Stage-1 (rocket choice) reaction time in ms; empty on timeout |
| state | 0-indexed first-stage state: `state1`-1 (0/1), i.e. which rocket-pair/planet context |
| reward | Points won on that trial, integer -4..5, delivered after the confirmatory stage-2 press (`points` column in source) |
| valid | 1 unless the trial was timed out (the source's stage-1 `rt1`==-1 or stage-2 `rt2`==-1; those cells are empty here) |
| state1 | Raw first-stage state 1/2 |
| stim_left | Identity (1..4) of the rocket shown on the left; the pair shown depends on state1 |
| stim_right | Identity (1..4) of the rocket shown on the right |
| choice1 | Raw stage-1 choice: 1..4 rocket identity; empty on a timeout |
| rt1 | Raw stage-1 reaction time in ms; empty on a timeout |
| rt2 | Raw stage-2 reaction time in ms: time to make the single confirmatory spacebar press (mine the planet) - not a choice; empty on a timeout |
| state2 | Planet reached after the transition (1/2); empty on a missed trial |
| score | Running total of points at trial end |
| rews1 | Drifting reward magnitude for reaching state2=1 on this trial (integer -4..5) |
| rews2 | Drifting reward magnitude for reaching state2=2 on this trial (integer -4..5) |
| trial_number | Source trial index, 0-indexed, restarting within each phase (0..24 practice, 0..124 test) |
| time_elapsed | jsPsych `time_elapsed` in ms at the end of this trial (elapsed since page load) |
| age | Participant age in years from subinfo.mat (empty for `subject_200`) |
| gender | Participant sex from subinfo.mat: `f` / `m` (empty for `subject_200`) |
| score_final | Final session score (total points) from subinfo.mat |
| time_total_ms | Total session elapsed time in ms at the demographics/save step (subinfo.mat `time_elapsed`) |

exp0 splits each paper-trial into two rows (one per stage decision, grouped by `block`, `stage`); exp1 has one row per paper-trial (its stage-2 response is a confirmatory keypress, not a choice). Practice (25 trials/subject) is included and tagged `phase=practice`. The data files contain one subject (exp0: 206 rows-worth, paper reports 207 — the discrepancy is in the authors' published files; exp1: 200 rows-worth, 199 completers) — N and t statistics in the paper's stay-probability analyses (Fig 16) reproduce on these CSVs (exp0 n=197 with df=196 matches the paper; exp1 keeps n=185 where the paper has df=183, i.e. 184: the extra `subject_200` is absent from subinfo.mat, so the authors' pipeline drops it). `response` codes stimulus identity (0-indexed), not screen position.

## Update (2026-08-13)
- PII scrub (exp1): one participant whose source data carried a raw platform worker ID instead of a `subject_N` label was renamed to the next unused number, `subject_200` (150 rows; participant count unchanged at 200).
- Sentinel cleanup (exp0): `rt` timeout sentinel `-1` -> empty on 1,722 cells (722 stage-1 + 1,000 stage-2 timeouts); `reward` stage-2 timeout sentinel `-1` -> empty on 1,000 cells. `response` was already empty and `valid` already 0 on all of these rows. Raw columns (`rt_1`, `rt_2`, `choice1`, `choice2`, `state2`, `common`) kept the source's `-1` sentinel at that time; since the verification pass (below) those cells are empty too.
- Sentinel cleanup (exp1): `rt` timeout sentinel `-1` -> empty on 1,024 cells. `response` was already empty and `valid` already 0 on those rows. `reward` in exp1 is untouched: `-1` there is a legitimate points value (range -4..5), and the source records 0 points on timed-out trials. Raw columns (`choice1`, `rt1`, `rt2`, `state2`) kept the source's `-1` sentinel at that time; since the verification pass (below) those cells are empty too.

CSVs fixed in place from the previous release; transform.py updated to produce the same output
from raw. The previous version remains in the repo's git history.

## Text-format conversion

Both experiments are textified (exp0: Daw two-step; exp1: novel two-step). Each paper-trial in exp0 becomes a stage-1 spaceship choice plus a stage-2 alien choice; exp1 is one spaceship choice per paper-trial plus a confirmatory spacebar press (not a choice, not marked). Free choices are the single-letter response tokens (A/B); one letter→identity mapping is drawn per participant (md5-seeded from the participant id) and shared by both stages (exp0) or both spaceship pairs (exp1), so a letter keeps one meaning within a transcript. exp1 narrates which spaceship pair appeared ("first"/"second" = `state1`). One line marks the practice→test boundary in both experiments. Timeouts are narrated as plain text ("You fail to respond in time.") with no response marker.

Sample transcript (exp0, subject_1, start):

```
You are an astronaut flying a spaceship from Earth to collect space treasure on two different planets. Each planet has two aliens on it, and each alien has its own space treasure mine. If an alien has a good mine, it is likely to share a piece of space treasure with you; if its mine is bad, it usually will not. The quality of each mine drifts slowly over time, so you must keep paying attention. On each trial, two spaceships appear. Choose one by pressing A or B. Each spaceship mostly flies to one of the planets and sometimes to the other; this does not change during the game. When you arrive at a planet, two aliens appear. Choose one by pressing A or B to ask it for treasure. You then learn whether you found space treasure (worth 1 point) or not (0 points). First you play practice trials with no time limit. Then the real game starts, with 2 seconds to make each choice. Press A or B to choose the option you want.
You see two spaceships. You press [HUMAN_RESPONSE]B[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

Both experiments got a text simulator (`simulate0.py` = exp0/Daw two-step,
`simulate1.py` = exp1/novel two-step). Each simulator regenerates the letter->
identity mapping exactly as `build_jsonl.py` does (md5-seeded from the
participant id), so the round-trip check through `build_jsonl.py` is
byte-identical for every participant. No experiment was skipped. Assumptions
surfaced: reward probabilities (exp0) and reward magnitudes (exp1) are
re-initialized at the practice/test boundary; no response timeouts are
simulated (a text simulator cannot produce reaction times), so every trial
completes and the exp1 confirmatory spacebar is always pressed (rt2 set to a
dummy 1000 to satisfy `build_jsonl.py`'s narration branch).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: hybrid model-based/model-free RL (SARSA(λ) + Bellman model-based values, softmax, weighting w) fit per-participant with bounded L-BFGS MAP using the paper's empirical priors (β~Gamma(4.82,0.88); π,ρ~N(0.15,1.42)); exp0/Daw 6 free params (β,α,λ,π,ρ,w), exp1/novel 5 free params (β,α,λ,ρ,w, no stimulus stickiness). Test-phase 125 trials, timed-out trials masked, the paper's >25-timeout participant exclusion applied.
Reproduced: model_control_higher_novel, w_reward_correlation_novel, w_reward_correlation_daw_not_sig.
Not reproduced: none.
Numeric mismatch: none (median-w novel − Daw fitted +0.276 vs reported 0.48−0.27=0.21; r(w,reward) novel 0.586 vs 0.55; r(w,reward) Daw 0.097 vs 0.10; Mann-Whitney p<0.05).
Partial validation: 
Indeterminate: 
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Verification

Verdict: pass (critical 2, major 7, minor 7; fixed 13, open 3).

Checked: paper (https://doi.org/10.1371/journal.pcbi.1005090, PLOS printable PDF), original data (https://github.com/wkool/tradeoffs, commit 6f849e1: data/daw paradigm and data/novel paradigm data.mat + subinfo.mat, task instruction text in tasks/*/additional-functions.js), exp0-exp1, transform re-run, transcripts, simulators, modeling (full model.py run, 41 min), analysis, logs. Skipped: none.

Fixed:
- transcripts1.jsonl: 107/200 transcripts failed the token-to-response bijection; build_jsonl.py drew a separate A/B map for each first-stage state and never said which spaceship pair appeared, so the start state (paper p. 21) was unrecoverable from the text. One map per participant now; every trial line starts with 'You see the first/second pair of spaceships.'; file rebuilt, simulate1.py mirrored (round trip 3/3 exact).
- transcripts0.jsonl: 89/206 transcripts failed the bijection because spaceships and aliens had independent A/B maps; one map per participant now; file rebuilt, simulate0.py mirrored (round trip 3/3 exact).
- build_jsonl.py exp0 instructions said the chosen spaceship 'determines' the planet; transitions are 70/30 and participants were told so (paper p. 22; task instructions_1d). Sentence corrected; transcripts rebuilt, simulator mirrored.
- build_jsonl.py exp1 instructions did not explain the two spaceship pairs with fixed within-pair destinations (task instructions_1c; paper p. 21). Sentence added; transcripts rebuilt, simulator mirrored.
- build_jsonl.py (both): '2 seconds to make each choice' although the 25 practice trials had no deadline (paper p. 22; task instructions_1e), and the practice-to-test screen ('new planets, new aliens and new mines') was not narrated while the reward walks restart at block 25 (exp0.csv ps columns, exp1.csv rews columns). Instructions distinguish practice from real trials; one boundary line added; simulators mirrored.
- exp0.csv/exp1.csv kept the source's -1 timeout sentinel in choice1, rt_1, choice2, rt_2, state2, common (exp0: 1444/1444/2000/2000/1444/1444 cells) and choice1, rt1, rt2, state2 (exp1: 1024/1024/1707/1024 cells); schema.md requires empty cells. transform.py fixed, both CSVs regenerated from the source; no other cell changed; analysis.py output unchanged; model.py inputs unchanged (exp0 arrays equal, exp1 likelihood equal to 0.0 at random parameters).
- transform.py wrote rt as float (1405.0) while the shipped CSVs had 1405, so its re-run was not byte-identical; rt, rt_1, rt_2, rt1, rt2 are now written as Int64 and the re-run reproduces both CSVs byte-for-byte.
- logs/auto-exp-modeling.sessions.json: message 0 carried a git-diff snapshot of another run's work dir (vantiel_2022_meaning README, CSVs, paper.html); those 4 diff entries removed.
- README said exp1 has 'four possible reward magnitudes'; exp1.csv reward and rews1/rews2 are integers -4..+5 (paper p. 21). Corrected.
- README Text-format section claimed the letter mapping is 'stated in the transcript instructions'; it is learned from the trials. Now describes the one-map-per-participant policy, the pair narration and the boundary line.
- README column tables and the 2026-08-13 update note described the raw timeout cells as -1; now 'empty'.
- README sample transcript regenerated from the rebuilt transcripts0.jsonl (subject_1).
- README notes: exp1 keeps n=185 where the paper has df=183 (184); subject_200 is absent from subinfo.mat, so the authors' make_raw_data.m drops it. Clause added. Column headings set to '####'; Run lines added to the Text-format and Simulators sections (logs: deepseek-v4-flash-0731, 2026-08-24).

Open:
- minor: the paper (p. 20-21) reports 207 Daw and 199 novel completers; the source data.mat files hold 206 and 200 subjects (the 200th labeled with a worker id, not in subinfo.mat). The discrepancy is inside the source; the README states it.
- minor: model.py deviates from the authors' MB_MF_*_rllik.m in details: after a timed-out trial the stickiness terms use the dummy action/key instead of the last real choice; the novel model writes a transition entry for the unobserved (state, action) pair; Daw transitions are assumed known (70/30) instead of the paper's count-based choice among three structures (p. 23); novel transitions are learned per (state, action) instead of per state. Only timed-out trials (avg 2.7%) and the first trials are affected; all three reported results reproduce (median w novel-Daw +0.276, r=0.586 novel, r=0.097 Daw, as the README states).
- minor: the running total score shown after each planet visit (task instructions_1e) is not narrated in the transcripts; it is derivable from the narrated rewards.

Run: claude-fable-5-1, 2026-09-09
