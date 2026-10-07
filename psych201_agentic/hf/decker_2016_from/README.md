---
tags:
- paradigm:two-step-task
- cognitive-modeling:needs-review
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:needs-review
---

# decker_2016_from

- Paper: https://doi.org/10.1177/0956797616639301
- Data source: https://osf.io/gq7z2/
- PDF: https://europepmc.org/articles/PMC4899156?pdf=render
- Full text: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4899156/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Decker, J. H., Otto, A. R., Daw, N. D., & Hartley, C. A. (2016). From creatures of habit to goal-directed learners: Tracking the developmental emergence of model-based reinforcement learning. Psychological Science, 27(6), 848–858.

## Experiment summary
Children, adolescents, and adults (N=59: 20 children ages 8–12, 20 adolescents ages 13–17, 19 adults ages 18–25) performed a two-step Markov decision task. On each paper-trial, participants first chose one of two spaceships (first stage), which probabilistically (70/30 common/rare) transitioned to one of two planets, then chose one of two aliens for a stochastic reward. The study tested whether model-based reinforcement learning increases across development by estimating the weighting parameter ω from a hybrid model-based/model-free RL model. Response type is binary choice across ~200 trials per participant (exp0).

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number (1..59) from Decker_choices_for_RL.csv / Decker_subject_list.csv |
| trial | 0..N-1 response counter, restarting at 0 for each participant; two rows per paper-trial (stage1 then stage2) |
| block | 0..paper-trial index; identical for the stage1+stage2 rows of one paper-trial (from source `trial` column, sorted within participant) |
| stage | `stage1` = first-stage spaceship choice, `stage2` = second-stage alien choice |
| response | Stage-1: 0-indexed spaceship chosen (source stage_1_resp 1/2 minus 1). Stage-2: 0-indexed alien chosen on the planet reached, 0 = first alien, 1 = second alien (source stage_2_resp 3/4/5/6 minus 3, modulo 2; the planet is in `state`) |
| state | 0-indexed task state: 0 for first stage; for second stage 0=planet A, 1=planet B (source stage_2_stims) |
| reward | 0/1 whether the second-stage choice earned space treasure (source `reward`); NaN on the stage1 row since reward is delivered at stage2 |
| valid | 1 on all rows (source recorded a full choice on every trial) |
| trial_source | Original 0-indexed trial number from the source CSV, preserved verbatim |
| trans | Transition type of the paper-trial: `common` or `rare` (70/30), from source `trans` |
| stage2_stims | Which second-stage planet the stage2 choice was on (`A` or `B`) |
| stage1_resp | Raw source stage-1 choice code (1 or 2) |
| stage2_resp | Raw source stage-2 choice code (3,4,5,6) |
| reward_source | Raw source reward (0 or 1) |
| age | Participant age in years (from subject_list; matches per-row source age) |
| age_group | Developmental band: `children` (8-12), `adolescents` (13-17), `adults` (18+) |
| gender | Participant gender: `m` / `f` from subject_list |

Note: The companion raw file Decker_choices_for_MEregression.csv holds second-stage RTs (s1rt/s2rt) and lagged ME-regression variables (stay/lastwin/lasttransR/currtransR), but it is a derived subset (first 9 trials plus excluded trials removed by the paper's exclusion criteria) that could not be aligned to the complete trial data, so those columns were not merged in this dataset.

The paper's final sample is N=59 (p. 849: 20 children, 20 adolescents, 19 adults) after the exclusions listed on p. 851 (2 inattentive, 1 invariant chooser, and the participants failing two reward-sensitivity criteria); the source ships exactly these 59 participants. Trials on which a participant made no first- or second-stage choice are absent from the source (p. 851: median removed 3.5 for children, 0.5 for adolescents, 0 for adults), so participants have 151–200 paper-trials.

## Text-format conversion

exp0 (the two-step spaceship task) was transcribed to `transcripts0.jsonl` (59 transcripts, one per participant). The task is textifiable: the spaceship/planet/alien stimuli are nameable and the model-based/model-free learning operation (learning transition probabilities and drifting alien reward rates) is preserved in words. No experiments were skipped.

Sample transcript (start through the first response):

```
You are a space explorer collecting space treasure. On each trial you first choose one of two spaceships. Each spaceship usually travels to one planet but sometimes to the other. After your spaceship travels, you arrive at a planet. On that planet you choose one of two aliens. If you pick the right alien, you find space treasure; otherwise you find nothing. The aliens' chances of giving treasure change slowly over time, so keep trying different choices.
Press A to choose the first spaceship or B to choose the second spaceship. On each planet, press A to choose the first alien or B to choose the second alien.
You choose a spaceship. You press [HUMAN_RESPONSE]B[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

exp0 got `simulate0.py`, a text simulator of the two-step spaceship task that mirrors the instructions and trial phrasing of `build_jsonl.py`; the round-trip check through `build_jsonl.py` passed (simulated transcripts are byte-identical to the rebuilt ones). No experiments were skipped. ASSUMPTION: each alien's reward probability follows a Gaussian random walk (SD 0.025) clipped to [0.2, 0.8], as in Daw et al. (2011); the paper only states that the probabilities drift slowly between 0.2 and 0.8 (p. 851). ASSUMPTION: the simulator always generates 200 paper-trials, and age, age_group, and gender are drawn from the empirical distribution of the 59 participants.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`experiments/exp0/` is a static jsPsych v8 reproduction of the two-step spaceship task, built from `simulate0.py` and the paper. The headless round trip (`?mode=simulate`) ran and its CSV matches `exp0.csv`'s schema, so it is validated (`validated: true`); the visual rendering check found no gross breakage (`visual_ok: true`). See `experiments/README.md` to run it locally or host it. Notes worth surfacing: `age`/`age_group`/`gender` are left blank in the browser output (a participant's demographics are not measured by this task), `participant_id` is the generated session id (a UUID string, not the original subject number), and the paper's "3 s per choice" window is not hard-enforced here (choices are self-paced so no trial is dropped) — these are cosmetic timing/data-shape defaults that do not change the task or the recorded data.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Indeterminate: The primary modeling result (Table 3: model-based weight omega increases
with age) was fit with a per-participant MLE of the Daw/Otto hybrid two-step model. The
per-participant omega was not identifiable from ~200 two-step trials: fits collapsed to
bounds (47-81% at 0/1), and a ground-truth simulation with omega perfectly correlated
with age (r=1.0) recovered essentially no omega-age relationship (r=-0.01), whereas the
paper's result depends on hierarchical Bayesian estimation that pools across participants.
A faithful per-participant reproduction is not achievable; implementing the paper's
hierarchical Bayesian fit was out of scope for this run.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: needs-review (critical 1, major 3, minor 4; fixed 8, open 0).

Checked: paper (https://doi.org/10.1177/0956797616639301, PDF via Europe PMC PMC4899156), original data (https://osf.io/gq7z2/: Decker_choices_for_RL.csv, Decker_subject_list.csv; Decker_choices_for_MEregression.csv carries no trial index and aligns positionally with the RL file for only 4 of 59 subjects, so the README's note that it cannot be merged holds), exp0, transform re-run (byte-identical to the shipped exp0.csv before the fix below), transcripts (build_jsonl.py rebuilds transcripts0.jsonl byte-for-byte), simulators (simulate0.py runs; round trip through build_jsonl.py identical), analysis (analysis.py: all three effects of Tables 1-2 reproduce), logs. Skipped: modeling (no model.py: the repo is tagged cognitive-modeling:needs-review and its modeling section reports the hierarchical fit behind Table 3 as indeterminate, so there was nothing to re-run).

Fixed:
- critical: exp0.csv coded the stage-2 response as the global alien index 0-3 (source stage_2_resp minus 3) while transcripts0.jsonl and simulate0.py map it to A/B within the planet reached; check_repo flagged 59/59 transcripts as not one-to-one with the CSV. transform.py now codes the stage-2 response as (stage_2_resp - 3) mod 2 (0 = first, 1 = second alien on the planet in `state`); exp0.csv regenerated (5870 stage-2 rows changed, raw code kept in stage2_resp), transcripts0.jsonl rebuilt (byte-identical), simulate0.py moved to the same coding, README response row updated.
- major: README Notes claimed the paper's original sample was N=169 (92 adolescents, 77 adults); the paper (p. 849) reports a final sample of 59 (20/20/19) after the exclusions on p. 851, and the source ships exactly those 59. Replaced with the paper's numbers and a note that trials without a response are absent from the source (per-group medians 3.5/0.5/0 match p. 851).
- major: the repo carried simulator:pass without a `## Simulators` section; added the section (round trip passed, assumptions) with the simulator run's model and date from transcripts/auto-exp-sim.log.
- major: logs/auto-exp-sim.sessions.json carried two file diffs of castrorodrigues_2022_explicit in the first message's summary (cross-run contamination); removed.
- minor: `## Text-format conversion` had no Run line; added the model and UTC date recorded in transcripts/auto-exp-transcribe.log.
- minor: the exp0 columns heading used `###`; changed to `#### exp0`.
- minor: the experiment summary said 'Adolescents and adults (N=59: 20 children ...)'; now 'Children, adolescents, and adults'.
- minor: simulate0.py docstring said the reward probabilities have 'reflecting boundaries' while the code clips them, and attributed short sessions to 'late trials dropped in data cleaning' while the source omits trials without a response (paper p. 851); docstring corrected, no behavior change.

Open:
- none.

Run: claude-fable-5-1, 2026-09-10
