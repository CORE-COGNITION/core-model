---
tags:
- paradigm:bandit
- cognitive-modeling:pass
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:needs-review
---
# nussenbaum_2024_sensitivity

- Paper: https://doi.org/10.1177/09567976241256961
- Data source: https://osf.io/69rs8/
- Full text: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11693699/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Nussenbaum, K., Katzman, P. L., Lu, H., Zorowitz, S., & Hartley, C. A. (2024). Sensitivity to the instrumental value of choice increases across development. Psychological Science, 35(8), 933-947. https://doi.org/10.1177/09567976241256961

## Experiment summary
Two experiments test developmental changes in sensitivity to the instrumental value of choice — the extent to which the act of choosing is valued for its own sake — from childhood to adulthood. Experiment 1 (in-person, N=92, ages 10-25) used a computer bandit task with an agency manipulation (free vs forced choice, with token offers to forgo agency) alongside a reward-sensitivity task and an explicit-knowledge task; Experiment 2 (online, preregistered, N=150) used a slot-machine/arcade paradigm with the same agency manipulation plus an explicit task. The key manipulation is whether a trial allows the participant to choose freely (free agency) versus a forced/forfeit offer, and the intrinsic value of the offered options; responses are button/keyboard choices and RTs with binary token rewards. Across both experiments the central finding is that sensitivity to the instrumental value of choice increases with age — older children/adolescents/adults show a greater preference for options accompanied by free choice (relative to forfeiting agency), a developmental increase reproduced here directionally and with significance. Behavior was additionally fit with a family of reinforcement-learning models (agency-bonus and alpha/beta variants) compared via AIC/BIC.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number (vocXXX) from the Experiment 1 `voc_sub_info.csv` |
| task_id | 0 = bandit/agency task, 1 = reward-sensitivity task, 2 = explicit-knowledge task |
| trial | 0..N within each (participant_id, task_id); for the 2-response bandit task, counts responses |
| response | Bandit task, stage='agency': 1 = chose agency, 0 = forgo (from agencyResp 2/1); stage='bandit': 1 = left machine, 0 = right (from banditResp 1/2); reward-sensitivity: 1 = left, 0 = right (from banditKeyResp 1/2); explicit: probability rating 1..9 |
| rt | Reaction time in ms (converted from source seconds) |
| RT | Raw RT in seconds for the reward-sensitivity and explicit-knowledge tasks (as in source) |
| stage | 'agency' or 'bandit' — which decision stage of a bandit-task paper-trial this row is (block groups the two stages of one trial) |
| block | 0-indexed bandit-task paper-trial index grouping the agency+bandit stage rows |
| condition | Bandit-room condition: bandits5050 / bandits7030 / bandits9010 |
| leftBandit | Bandit name shown on the left in the bandit/agency task |
| rightBandit | Bandit name shown on the right in the bandit/agency task |
| tokenOffer | Token amount (0-6) offered to forgo agency (bandit task) |
| agencyResp | Bandit-task agency-stage keypad response (1 = forgo/accept offer, 2 = choose agency) |
| agency | 0 = forgo agency, 1 = chose agency (bandit task) |
| agencyRT | Raw agency-stage RT in seconds (as in source) |
| selectedBandit | Bandit name chosen (or computer-chosen when agency=0) |
| nonSelectedBandit | Bandit name not selected |
| banditResp | Bandit-task machine-stage keypad response (1 = left, 2 = right) |
| banditRT | Raw machine-stage RT in seconds (as in source) |
| reward | Whether the machine paid out this trial: 0 / 1 (bandit task) |
| tokensEarned | Total tokens earned on the trial, incl. any forgo offer (bandit task) |
| trialOfCond | Within-condition trial number (1-indexed, 1..105) |
| ev_choice | Expected value of choosing (max machine EV): 5, 7, or 9 |
| ev_comp | Expected value of the computer choice = 5 + tokenOffer |
| voc | Value of choice = ev_choice - ev_comp |
| stage_2_acc | Machine-selection accuracy (1 selected higher-prob bandit, 0 lower, NaN for 50/50 or when not meaningful) |
| banditKeyResp | Reward-sensitivity-task keypad response (1/2 = which bandit) |
| rs_accuracy | Reward-sensitivity task outcome coding: 1 = chose higher-value, -1 = chose lower-value, 0 = equal (0.5 vs 0.5); renamed from source `accuracy` (reserved synonym) |
| diff | Absolute probability difference between the two bandits (0..0.8) |
| correct | Reward-sensitivity: 1 if chose the higher-value bandit, else 0 (source-derived) |
| bandit | Explicit-knowledge task bandit name (also carried as `stimulus`) |
| stimulus | Explicit-knowledge task bandit name (same as `bandit`) |
| trueProb | True bandit win probability (0.1..0.9) |
| error | \|response - trueProb\| (explicit-knowledge task) |
| age | Participant age in years (continuous, from voc_sub_info.csv) |
| gender | 'm' / 'f' (lowercased from M/F) |
| valid | 1 normally; 0 where the source response is missing |
| forced_choice | 1 on bandit-stage rows where agency was forgone (the coin flip picked the machine and the participant pressed its key), else 0 |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Original subject number (numeric ID) from the Experiment 2 `voc_sub_info.csv` |
| task_id | 0 = slot-machine/arcade (learning) task, 1 = explicit-knowledge task |
| trial | 0..N within each (participant_id, task_id); for the 2-response arcade task, counts responses |
| response | For arcade rows: 1 = chose agency / 0 = forgo (stage='agency'), or 1 = left machine / 0 = right (stage='bandit'); for explicit: probability rating 1..9 |
| rt | Reaction time in ms (source already in ms) |
| stage | 'agency' or 'bandit' — which decision stage of an arcade paper-trial this row is (block groups them) |
| block | 0-indexed arcade paper-trial index grouping the agency+bandit stage rows |
| arcade_block | Source block label 1..7 (7 blocks of 45 trials), constant across the two stage rows of a trial |
| reward | Tokens won on the trial: 0 or 10 (stage_3_outcome), placed on the 'bandit' stage row only |
| context | Arcade context / machine pair index (0,1,2) |
| offer | Token amount (0-6) offered to forgo agency |
| arcade_color_L / arcade_color_R | Hex color of the left/right arcade machine |
| arcade_id_L / arcade_id_R | Machine id number of the left/right arcade machine |
| reward_prob_L / reward_prob_R | Win probability (0.1..0.9) of the left/right machine |
| stage_1_choice | Raw agency-stage choice (1 = agency, 0 = forgo), same as response on stage='agency' rows |
| stage_1_rt | Raw agency-stage RT in ms |
| stage_2_choice | Raw machine-stage choice (1 = left, 0 = right), same as response on stage='bandit' rows |
| stage_2_rt | Raw machine-stage RT in ms |
| stage_3_outcome | Tokens won (0 or 10), = reward |
| phase | 'experiment' for arcade task, 'explicit' for explicit task |
| valid | 1 normally; 0 where the source choice is missing (missed trial) |
| forced_choice | 1 on bandit-stage rows where agency was forgone (the coin flip picked the machine and the participant pressed its key), else 0 |
| stimulus | Explicit-task stimulus image path (machine1..machine6) |
| red/blue/orange/green/pink/purple | Reward probability of each machine color (for explicit task) |
| true_prob | True win probability of the stimulus machine |
| error | \|response - true_prob\| (explicit task) |
| age | Participant age in years (continuous) |
| gender | 'm' / 'f' / 'other' (lowercased from Male/Female/Other) |

Both experiments' multi-stage trials (agency decision followed by machine choice) are split into one row per response, grouped by the 0-indexed `block` column. exp0 = Experiment 1 (bandit task + reward-sensitivity + explicit-knowledge), exp1 = Experiment 2 (arcade task + explicit). All phases present in the source's processed files are retained, tagged by `task_id` and `phase` (the processed files hold no practice trials).

Experiment 2 provenance: the source's processed files (`experiment2/data/processed/`) hold the 150 participants kept after the paper's preregistered exclusions (164 collected; `data_quality.csv` flags 14 with `bad_data` != 0) and only the `experiment` and `explicit` phases. The raw jsPsych files for all 164 participants, including 17 practice trials and comprehension checks per participant, are in the OSF folder `experiment2/data/task_data/` and are not parsed here.

## Text-format conversion

Both experiments were transcribed into natural language (`transcripts0.jsonl` and `transcripts1.jsonl`): exp0 covers the bandit/agency task, the reward-sensitivity task, and the explicit-knowledge task; exp1 covers the arcade/agency task and the explicit-knowledge task. No experiment was skipped. Because the source machine identities (e.g. `bandit70`) encode the win probability, machines are described in the transcripts by neutral opaque colour labels (exp0) or their actual arcade colour (exp1) so that a text reader still must learn which machine pays more through trial and error — preserving the learning operation. Free agency and machine-selection choices are wrapped in `[HUMAN_RESPONSE]`; when the participant forgoes agency and a coin flip determines the machine, that instructed selection is narrated plainly (not marked; `forced_choice` = 1 in the CSV).

Sample transcript (Experiment 1, from the start up to the first response):

```
<Experiment 1> You win tokens by playing slot machines that pay out 10 tokens with different probabilities. Tokens convert to a cash bonus.
<Agency task>Your goal is to win as many tokens as possible by playing slot machines that pay out 10 tokens with different probabilities. The tokens will be converted to a cash bonus at the end. Each trial you enter an arcade room holding two slot machines, and first the computer offers you some tokens to let it choose the machine for you. Press A to choose the machine for yourself, or press B to accept the offer and let the computer choose for you.
<Machine selection>If you chose to play for yourself, you then pick a machine: press A for the left machine, or press B for the right machine.
You stand before the door to a room holding two slot machines: the blue machine on the left and the yellow machine on the right. The computer offers you 5 tokens to let it choose for you.
You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE]. …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: the paper's 16 RL agency-bonus variants (1/2/4 learning rates x 1/2 inverse temperatures x with/without agency bonus), per-participant bounded MLE (multi-start L-BFGS-B), compared on summed AIC; plus regression/paired-t checks on fitted parameters.
Reproduced: model_comparison_four_two_beta (exp0, exp1); confirmation_bias_choice (exp0, exp1); no_comp_confirmation_bias (exp0, exp1); beta_agency_increases_with_age (exp0, exp1).
Not reproduced: none.
Numeric mismatch: minor. fourAlpha_twoBeta wins on AIC in both experiments (exp0 AIC 37686.8, exp1 60494.0). Confirmation bias alpha_choice_p - alpha_choice_m = +0.164 (exp0) / +0.174 (exp1); no bias after computer selections (-0.070 / -0.066). beta_agency regressed on age: slope +0.30 (exp0) / +0.30 (exp1), both positive and significant (paper: b=.24 p=.056, b=.25 p=.008). Parameter magnitudes are of the same order/direction as the paper; exact values differ somewhat because we use per-participant MLE (paper used MAP with common gamma/normal priors).
Partial validation: none.
Indeterminate: none. Note: ~25% of exp0 per-participant fits sit at the beta=30 bound and do not reach a strict L-BFGS convergence tolerance (conv 0.72-0.74), a boundary artifact of the paper's own fit setup; the reported effects are robust across experiments and match the paper.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments got a runnable static jsPsych online version: `experiments/exp0/`
(Exp 1: agency/bandit + reward-sensitivity + explicit) and `experiments/exp1/`
(Exp 2: arcade/agency + explicit). The headless round trip passed for both — the
saved CSV matches `exp0.csv` / `exp1.csv` column-for-column and codes correctly
(726 rows per participant for exp0, 636 for exp1; `trial` restarts at 0 per
`task_id`; agency/machine, reward-sensitivity and explicit codings, `reward`,
`tokensEarned`, `ev_comp`/`voc`, `trialOfCond`, `stage_2_acc` and
`arcade_block` all recovered). No experiment was skipped. ASSUMPTIONS (all
browser-only presentation, none change the task or recorded data): machine colour
hexes, per-task transition screens and the 1.5 s outcome screen are cosmetic
defaults; the exp1 explicit task renders the six machines as coloured boxes even
though the `stimulus` column records the `machineN.png` path; per-participant
demographics (`age`, `gender`) are left blank because they have no in-task source.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Both experiments got a text simulator (`simulate0.py` = Experiment 1
agency/bandit + reward-sensitivity + explicit; `simulate1.py` = Experiment 2
arcade/agency + explicit). Each is a single self-contained `uv`-runnable
simulator that produces one `[HUMAN_RESPONSE]...[/HUMAN_RESPONSE]` participant
transcript byte-identical to `transcripts0.jsonl` / `transcripts1.jsonl`. The
round-trip check passed for both: regenerating the transcripts from the
simulated DataFrames through `build_jsonl.py` matches the simulator's own
prompts exactly. ASSUMPTIONS: the reward-sensitivity schedule (30 ordered
distinct-machine pairs x 3) and the bandit/arcade trial order (3 machine-pair
rooms x 7 offers) are taken from the shipped CSVs rather than the paper, which
does not fully specify them; exp1 assigns arcade colours to the six machine
probabilities randomly per participant.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: needs-review (critical 1, major 8, minor 6; fixed 11, open 4).

Checked: paper (https://doi.org/10.1177/09567976241256961, PMC11693699 full text), original data (https://osf.io/69rs8/, all 1937 files of experiment1/ and experiment2/), exp0-exp1, transform re-run (original transform.py reproduces the uploaded CSVs byte-for-byte from the OSF processed files), transcripts, simulators (smoke run and byte-identical round trip through build_jsonl.py), modeling (partial, see skipped), analysis (3/3 effects reproduce), logs. Skipped: model.py full fit (needs about 11.7 h per the previous run's log, longer than the compute job left; stopped after 1.5 h. Run with --max-participants 8 on the fixed CSVs instead, and --max-participants 4 gives byte-identical output on the original and the fixed CSVs; model.py reads only block, stage, the raw choice columns and valid, none of which changed. The previous full run in transcripts/auto-exp-modeling.log reports all 8 results reproduced with the numbers quoted in the Modeling section.); Supplemental Material of the paper (task details of the reward-sensitivity and explicit tasks, exclusion criteria) not retrievable; the OSF task code and data_quality.csv were used instead.

Fixed:
- critical: transform.py sorted the two stage rows of each paper-trial with `stage` descending, so the machine-selection row came before the agency-decision row (exp0 voc017a trials 0/1, exp1 11669 trials 0/1); the paper (Fig. 1, Methods) has the agency decision first. Sort fixed, exp0.csv/exp1.csv regenerated from the OSF processed files (all other columns identical after alignment), transcripts0/1.jsonl rebuilt.
- major: bandit-stage rows after forgoing agency (exp0: 11411 rows, exp1: 15769 rows) hold the key press instructed by the coin flip but carried no flag, so 92/92 and 148/150 transcripts had fewer marked responses than free CSV rows. `forced_choice` column added in transform.py (1 on those rows), README rows added, simulators emit it.
- major: exp0 `response` held raw keypad codes 1/2 (agency: 2 = choose, 1 = forgo; machine and reward-sensitivity: 1 = left, 2 = right), against the schema's 0/1 coding, and letter A mapped to 2 in one stage and 1 in the other. Recoded to 1 = chose agency / left machine, 0 = forgo / right machine (same as exp1 and the transcripts' A/B); raw agencyResp/banditResp/banditKeyResp columns kept; README row and simulate0.py updated.
- major: the explicit-task instruction said 'Use keys 1 to 9', so tokens 7 and 8 never appeared before their first use (78/92 and 117/150 transcripts); the instruction now lists keys 1-9 explicitly in build_jsonl.py, simulate0.py, simulate1.py; transcripts rebuilt.
- major: a missing explicit rating (voc034a, task 2 trial 1, valid=0) was marked `[HUMAN_RESPONSE]None[/HUMAN_RESPONSE]`; build_jsonl.py now writes 'You make no response.' for a missing reward-sensitivity/explicit response (0 None tokens remain); simulator mirror functions updated.
- major: README described exp1 `arcade_block` as '7 blocks of 21 trials'; each source block holds 45 trials (315/7). Corrected.
- major: exp0 column `RT` (raw seconds of the reward-sensitivity and explicit tasks) had no Columns-table row. Row added.
- major: logs/auto-exp-modeling.sessions.json and logs/auto-exp-transcribe.sessions.json carried workspace diffs of unrelated files (wiki/*.md, another run's WORK dir, modeling_pending.txt) naming other datasets in message 0 `info.summary.diffs`; 18 and 2 diff entries removed, conversation messages untouched.
- minor: README said exp1 machine choice '0/1' without the side; the task code (jspsych-fcp-trial.js: valid_responses_s2 = [37 left, 39 right], first key -> 1) gives 1 = left, 0 = right. Documented for `response` and `stage_2_choice`.
- minor: Columns headings `### exp0`/`### exp1` changed to `####` (template).
- minor: README claimed practice trials are retained; the source's processed files hold none. Reworded, and an Experiment 2 provenance note added (see open findings).

Open:
- major: the paper reports 164 Experiment 2 participants collected and 150 kept after preregistered exclusions (browser interactions > 20 or > 30 missed choices, e2_1_voc_process_data.Rmd); the dataset holds the 150 in the source's processed files (`experiment2/data/processed/`, `data_quality.csv` flags 14 with bad_data != 0; the OSF README also states 150). Raw jsPsych files for all 164 participants, with 17 practice trials and comprehension checks each, exist in `experiment2/data/task_data/` but are not parsed: that is a transform rewrite, not a minimal fix. Documented in the README Notes.
- minor: check_repo reports 'marked tokens do not map one-to-one onto the CSV response sequence' for 28/92 (exp0) and 22/150 (exp1) transcripts. These are exactly the participants who gave an explicit rating of 1: the rating token '1' and the binary code 1 (token A) share the CSV value 1, so no global token-value bijection exists for a multi-task transcript. Per task the mapping is exact for every participant (A = 1, B = 0 on all agency, machine and reward-sensitivity rows; digits 1-9 map to themselves). Not a data or transcript error.
- minor: exp0 `reward` is the source's 0/1 payout indicator (10 tokens per win; `tokensEarned` holds the delivered total) while exp1 `reward` is 0/10; both documented, left as in the source.
- minor: source folders not read by transform.py: `experiment1/data/scored_surveys/` (BDI, LOC, DOC, STAI questionnaires) and the per-participant raw `task_data/` files of Experiment 1 (same 92 participants and trials as the processed files, no practice phase).

Run: claude-fable-5-1, 2026-09-13
