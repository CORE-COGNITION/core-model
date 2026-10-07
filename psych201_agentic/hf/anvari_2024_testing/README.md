---
tags:
- paradigm:bandit
- psych-201
- text-format:pass
- js-experiment:needs-review
- simulator:pass
- verification:pass
---
# anvari_2024_testing

- Paper: https://doi.org/10.1038/s41467-024-51685-z
- Data source: https://doi.org/10.17605/OSF.IO/F62MY
- PDF: https://www.nature.com/articles/s41467-024-51685-z.pdf
- Full text: https://www.nature.com/articles/s41467-024-51685-z
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Anvari, F., Billinger, S., Analytis, P. P., Franco, V. R., & Marchiori, D. (2024). Testing the convergent validity, domain generality, and temporal stability of selected measures of people’s tendency to explore. Nature Communications, 15(1), 7721. https://doi.org/10.1038/s41467-024-51685-z

## Experiment summary
A registered report testing whether five explore–exploit behavioural tasks converge on a general tendency to explore, generalize across task domains, and are stable over about one month. 678 UK Prolific participants completed the whole study at time1 (April 2023) and 254 of them repeated it at time2 about one month later. Each CSV pools both waves (`session`), and one `participant_id` identifies the same person in both waves and in all five experiments, so the paper's test–retest and cross-task analyses can be run from these files. Participants who failed a task's comprehension check six times skipped that task and have no rows in that experiment. exp0 (N = 672): five-armed bandit, per wave 1 practice block of 20 trials and 4 incentivized blocks of 40 trials. exp1 (N = 671): sampling paradigm, per wave 1 practice and 5 incentivized blocks of free sampling (2 to 100 samples) closed by the choice of the button to be paid from. exp2 (N = 674): observe-or-bet, per wave 1 practice block of 25 trials and 2 incentivized blocks of 50 trials. exp3 (N = 678): optional stopping with recall, per wave 1 practice and 8 incentivized blocks of up to 20 box openings. exp4 (N = 675): alien game (search on an NK payoff landscape), per wave 1 practice block of 3 trials and 3 incentivized blocks of 10 trials, each opened by a displayed starting combination. The paper's headline analyses are CFA/latent-factor SEM and cross-task correlations; two within-task convergent-validity effects reproduce from the trial-level data (bandit switch rate with exploit-complement, paper r = 0.47; alien Hamming distance with active search, paper r = 0.52).

## Notes

The source is the oTree export of the main study on OSF (`<task>_2023-04-28_out.csv` = time1, `<task>_2023-06-02_out.csv` = time2, one file per task and wave). `transform.py` keeps every recorded observation: all participants who completed the study, both waves, the practice blocks (`phase`), and every raw column that is not all-blank or a platform id (the MTurk/Prolific id columns and the internal `participant.code` are dropped; dots in raw names become underscores). Rows are sorted by participant, session, task_id, trial. Per-task notes:

- exp0: none beyond the columns. One time1 participant has 19 practice trials and two have 39 trials in one block (inside the source).
- exp1: the source stores 100 rows per block and marks the rows after the participant stopped sampling with `player.selection = 0`; those padding rows are dropped, so the number of sample rows per block is the paper's exploration measure. The end-of-block choice of the button to be paid from (`player.sampling_option`) becomes one extra row per block with `final_choice = 1`. The source does not record what each sample paid.
- exp2: none beyond the columns.
- exp3: rows are box openings; the trailing blank padding rows the app emitted after a participant stopped searching are dropped, so the number of rows per block is the number of boxes opened (the exploration measure).
- exp4: the first row of every block is the starting combination the app displayed, flagged `forced_choice = 1`; the participant's 3 (practice) or 10 submissions follow it. The combinations are read as text so their leading zeros survive.

The pilot CSVs (`*_allPilots.csv`) on OSF are an earlier precursor study and are not part of the five experiments. The questionnaire files (self-report exploration scales, BFI-2, age, gender) are not included.

### Columns

#### exp0 (Multi-armed bandit)
| column | description |
|--------|-------------|
| participant_id | Person id `P000`..`P677`, assigned from the anonymized Prolific id in the source's `initial_app_*.csv` files (time1 file order); the same person keeps this id at time1 and time2 and in all five CSVs |
| session | Collection wave: `time1` (April 2023, source files dated 2023-04-28) or `time2` (retest about one month later, files dated 2023-06-02) |
| task_id | Block counted across waves: 0 = time1 practice (20 trials), 1..4 = time1 incentivized blocks (40 trials each), 5 = time2 practice, 6..9 = time2 incentivized; every block has five new buttons (fresh payoff means) |
| trial | 0-indexed trial within each (participant_id, task_id) |
| response | 0-indexed button chosen: 0..4 (0 = Button 1) |
| phase | `practice` for the first block of each wave, `test` for the incentivized blocks |
| participant__is_bot | oTree bot flag; 0 on every row |
| participant__index_in_pages | oTree page index the participant had reached when the data were exported |
| participant__max_page_index | number of pages in the oTree session; constant |
| participant__current_app_name | oTree app the participant was on at export; `finishing_app` on every row (everyone completed the study) |
| participant__current_page_name | oTree page the participant was on at export |
| participant_time_started | date and time the participant started the study session of that wave |
| participant_visited | oTree flag; 1 on every row |
| participant_payoff | the participant's total points over all incentivized blocks of all five tasks in that wave |
| player_id_in_group | oTree id within the single-player group; 1 on every row |
| player_payoff | points accumulated in this block (sum of player_payoff_1; 0 in the practice block); repeated on every row of the block |
| player_selection | raw button chosen (1..5); equals response + 1 |
| player_payoff_1 | points revealed for this click (the source's per-trial `player.payoff` column) |
| player_comp_num_blocks | answer to the comprehension question on the number of buttons (open response; correct answer 5) |
| player_comp_click_button | answer to the comprehension question on what a click shows (options 1..3; correct answer 2) |
| player_comp_trials | answer to the comprehension question on the number of trials per block (options 1..3; correct answer 1) |
| player_comprehension_times | number of attempts (1 to 6) the participant needed to pass this task's three comprehension questions |
| player_bandit_1_average_payoff | average points per click displayed for Button 1 after this trial (0 before its first click) |
| player_bandit_2_average_payoff | average points per click displayed for Button 2 after this trial (0 before its first click) |
| player_bandit_3_average_payoff | average points per click displayed for Button 3 after this trial (0 before its first click) |
| player_bandit_4_average_payoff | average points per click displayed for Button 4 after this trial (0 before its first click) |
| player_bandit_5_average_payoff | average points per click displayed for Button 5 after this trial (0 before its first click) |
| player_start_time | Unix time in seconds at which the participant started this task |
| player_end_time | not filled by the app; 0 on every row |
| player_total_time_spent | seconds spent in the task as recorded by the app (0 where the app did not fill it) |
| player_submission_times | seconds between the previous submission and this one (a response time) |
| player_instructions_completion_time | seconds spent on the task's instruction page |
| player_comprehension_completion_time | seconds spent on the task's comprehension check |
| group_id_in_subsession | oTree group id; 1 on every row |
| session_code | oTree session code of the wave |
| session_is_demo | oTree demo flag; 0 on every row |
| player_weight0 | mean of the Gaussian payoff distribution of Button 1 in this block (an integer 43..60; the click payoffs scatter around it with SD about 5) |
| player_weight1 | mean of the Gaussian payoff distribution of Button 2 in this block (an integer 43..60; the click payoffs scatter around it with SD about 5) |
| player_weight2 | mean of the Gaussian payoff distribution of Button 3 in this block (an integer 43..60; the click payoffs scatter around it with SD about 5) |
| player_weight3 | mean of the Gaussian payoff distribution of Button 4 in this block (an integer 43..60; the click payoffs scatter around it with SD about 5) |
| player_weight4 | mean of the Gaussian payoff distribution of Button 5 in this block (an integer 43..60; the click payoffs scatter around it with SD about 5) |

#### exp1 (Sampling paradigm)
| column | description |
|--------|-------------|
| participant_id | Person id `P000`..`P677`, assigned from the anonymized Prolific id in the source's `initial_app_*.csv` files (time1 file order); the same person keeps this id at time1 and time2 and in all five CSVs |
| session | Collection wave: `time1` (April 2023, source files dated 2023-04-28) or `time2` (retest about one month later, files dated 2023-06-02) |
| task_id | Block counted across waves: 0 = time1 practice, 1..5 = time1 incentivized blocks, 6 = time2 practice, 7..11 = time2 incentivized |
| trial | 0-indexed step within (participant_id, task_id): the samples in order, then the final choice as the last row |
| response | action at this step: 0 = sample Button 1, 1 = sample Button 2, 2 = stop and be paid from Button 1, 3 = stop and be paid from Button 2 |
| phase | `practice` for the first block of each wave, `test` for the incentivized blocks |
| final_choice | 1 on the one row per block that records the end-of-block choice of the button to be paid from, 0 on sample rows |
| reward | points the final draw paid, on the final_choice row; empty on sample rows because the source does not record the outcome of the individual samples |
| participant__is_bot | oTree bot flag; 0 on every row |
| participant__index_in_pages | oTree page index the participant had reached when the data were exported |
| participant__max_page_index | number of pages in the oTree session; constant |
| participant__current_app_name | oTree app the participant was on at export; `finishing_app` on every row (everyone completed the study) |
| participant__current_page_name | oTree page the participant was on at export |
| participant_time_started | date and time the participant started the study session of that wave |
| participant_visited | oTree flag; 1 on every row |
| participant_payoff | the participant's total points over all incentivized blocks of all five tasks in that wave |
| player_id_in_group | oTree id within the single-player group; 1 on every row |
| player_payoff | points credited for this block (the final draw; 0 in the practice block) |
| player_sampling_option | button the participant chose to be paid from in this block (1 or 2); repeated on every row of the block |
| player_sampler_payoff | points the chosen button paid at the end of this block; repeated on every row of the block |
| player_selection | raw sampled button on sample rows (1 or 2; equals response + 1); empty on the final_choice row |
| player_comp_num_buttons | answer to the comprehension question on the number of buttons (open response; correct answer 2) |
| player_comp_minimum_samples | answer to the comprehension question on the minimum samples per button (options 1..3; correct answer 2) |
| player_comp_learn_payout | answer to the comprehension question on how to learn the payouts (options 1..3; correct answer 3) |
| player_comprehension_times | number of attempts (1 to 6) the participant needed to pass this task's three comprehension questions |
| player_option_1_probability | payoff scheme of Button 1 as `<points>_<probability>`: `10_0.1` pays 10 points with probability 0.1 and 0 otherwise |
| player_option_2_probability | payoff scheme of Button 2, same format |
| player_final_choice | payoff scheme of the button chosen to be paid from (equals option 1 or option 2 of the block) |
| player_start_time | Unix time in seconds at which the participant started this task |
| player_end_time | not filled by the app; 0 on every row |
| player_total_time_spent | seconds spent in the task as recorded by the app (0 where the app did not fill it) |
| player_submission_times | seconds between the previous submission and this one (a response time) |
| player_instructions_completion_time | seconds spent on the task's instruction page |
| player_comprehension_completion_time | seconds spent on the task's comprehension check |
| player_presentation_order | id of the block's option pair: 1 = practice (1_1.0 vs 10_0.1), 2 = 3_1.0 vs 4_0.8, 3 = 3_1.0 vs 16_0.2, 4 = 3_0.25 vs 4_0.2, 5 = 3_1.0 vs 32_0.1, 6 = 9_1.0 vs 10_0.9; the incentivized pairs come in random order and random left/right position |
| group_id_in_subsession | oTree group id; 1 on every row |
| session_code | oTree session code of the wave |
| session_is_demo | oTree demo flag; 0 on every row |

#### exp2 (Observe-or-bet)
| column | description |
|--------|-------------|
| participant_id | Person id `P000`..`P677`, assigned from the anonymized Prolific id in the source's `initial_app_*.csv` files (time1 file order); the same person keeps this id at time1 and time2 and in all five CSVs |
| session | Collection wave: `time1` (April 2023, source files dated 2023-04-28) or `time2` (retest about one month later, files dated 2023-06-02) |
| task_id | Block counted across waves: 0 = time1 practice (25 trials), 1..2 = time1 incentivized blocks (50 trials each), 3 = time2 practice, 4..5 = time2 incentivized |
| trial | 0-indexed trial within each (participant_id, task_id) |
| response | per-trial decision: `observe`, `bet_red`, or `bet_blue` |
| phase | `practice` for the first block of each wave, `test` for the incentivized blocks |
| participant__is_bot | oTree bot flag; 0 on every row |
| participant__index_in_pages | oTree page index the participant had reached when the data were exported |
| participant__max_page_index | number of pages in the oTree session; constant |
| participant__current_app_name | oTree app the participant was on at export; `finishing_app` on every row (everyone completed the study) |
| participant__current_page_name | oTree page the participant was on at export |
| participant_time_started | date and time the participant started the study session of that wave |
| participant_visited | oTree flag; 1 on every row |
| participant_payoff | the participant's total points over all incentivized blocks of all five tasks in that wave |
| player_id_in_group | oTree id within the single-player group; 1 on every row |
| player_payoff | points credited for this block: correct minus incorrect guesses, floored at 0 (0 in the practice block); repeated on every row of the block |
| player_comp_lights_in_task | answer to the comprehension question on the number of lights (open response; correct answer 1) |
| player_comp_what_if_observe | answer to the comprehension question on what happens when observing (options 1..3; correct answer 2) |
| player_comp_what_if_guess_red_blue | answer to the comprehension question on what happens when guessing (options 1..3; correct answer 3) |
| player_selection | same string as response |
| player_light_colour | colour the light turned on in this trial (`red`/`blue`), recorded on every trial; the participant saw it only after `observe` |
| player_comprehension_times | number of attempts (1 to 6) the participant needed to pass this task's three comprehension questions |
| player_prob_red | probability that the light turns red in this block (practice 0.45 or 0.55; incentivized 0.3, 0.4, 0.6, or 0.7) |
| player_start_time | Unix time in seconds at which the participant started this task |
| player_end_time | not filled by the app; 0 on every row |
| player_total_time_spent | seconds spent in the task as recorded by the app (0 where the app did not fill it) |
| player_submission_times | seconds between the previous submission and this one (a response time) |
| player_instructions_completion_time | seconds spent on the task's instruction page |
| player_comprehension_completion_time | seconds spent on the task's comprehension check |
| player_presentation_order | id of the block design: 1 = practice, 2 and 3 = the two incentivized designs, shown in random order |
| group_id_in_subsession | oTree group id; 1 on every row |
| session_code | oTree session code of the wave |
| session_is_demo | oTree demo flag; 0 on every row |

#### exp3 (Optional stopping with recall)
| column | description |
|--------|-------------|
| participant_id | Person id `P000`..`P677`, assigned from the anonymized Prolific id in the source's `initial_app_*.csv` files (time1 file order); the same person keeps this id at time1 and time2 and in all five CSVs |
| session | Collection wave: `time1` (April 2023, source files dated 2023-04-28) or `time2` (retest about one month later, files dated 2023-06-02) |
| task_id | Block counted across waves: 0 = time1 practice, 1..8 = time1 incentivized blocks, 9 = time2 practice, 10..17 = time2 incentivized |
| trial | 0-indexed box opening within (participant_id, task_id); the number of rows per block is the number of boxes opened |
| response | 0..19 index of the box opened (counted left to right, top row first); same as player_chest_selection |
| phase | `practice` for the first block of each wave, `test` for the incentivized blocks |
| participant__is_bot | oTree bot flag; 0 on every row |
| participant__index_in_pages | oTree page index the participant had reached when the data were exported |
| participant__max_page_index | number of pages in the oTree session; constant |
| participant__current_app_name | oTree app the participant was on at export; `finishing_app` on every row (everyone completed the study) |
| participant__current_page_name | oTree page the participant was on at export |
| participant_time_started | date and time the participant started the study session of that wave |
| participant_visited | oTree flag; 1 on every row |
| participant_payoff | the participant's total points over all incentivized blocks of all five tasks in that wave |
| player_id_in_group | oTree id within the single-player group; 1 on every row |
| player_payoff | block points credited by the app; 0 on nearly every row (the block payoff is player_round_payoff) |
| player_chest_selection | raw index of the box opened (0..19) |
| player_chest_payoff | value revealed in that box (0 to 10) |
| player_accumulated_cost | search cost paid so far in this block (boxes opened so far times the cost per box) |
| player_current_best_payoff | highest box value seen so far in this block |
| player_round_payoff | block payoff = best value minus total cost; repeated on every row of the block |
| player_comp_num_boxes | answer to the comprehension question on the number of boxes (open response; correct answer 20) |
| player_comp_cost_search | answer to the comprehension question on the search cost (options 1..3; correct answer 3) |
| player_comp_boxes_values | answer to the comprehension question on the range of box values (options 1..3; correct answer 3) |
| player_comprehension_times | number of attempts (1 to 6) the participant needed to pass this task's three comprehension questions |
| player_start_time | Unix time in seconds at which the participant started this task |
| player_end_time | not filled by the app; 0 on every row |
| player_submission_times | seconds between the previous submission and this one (a response time) |
| player_instructions_completion_time | seconds spent on the task's instruction page |
| player_comprehension_completion_time | seconds spent on the task's comprehension check |
| player_total_time_spent | seconds spent in the task as recorded by the app (0 where the app did not fill it) |
| player_cost_order | cost per box opening in this block (0.05, 0.1, 0.2, or 0.4); constant within a block |
| group_id_in_subsession | oTree group id; 1 on every row |
| session_code | oTree session code of the wave |
| session_is_demo | oTree demo flag; 0 on every row |

#### exp4 (Alien game)
| column | description |
|--------|-------------|
| participant_id | Person id `P000`..`P677`, assigned from the anonymized Prolific id in the source's `initial_app_*.csv` files (time1 file order); the same person keeps this id at time1 and time2 and in all five CSVs |
| session | Collection wave: `time1` (April 2023, source files dated 2023-04-28) or `time2` (retest about one month later, files dated 2023-06-02) |
| task_id | Block counted across waves: 0 = time1 practice (1 starting combination + 3 trials), 1..3 = time1 incentivized blocks (1 starting combination + 10 trials each), 4 = time2 practice, 5..7 = time2 incentivized; every block is a new payoff landscape (a new alien) |
| trial | 0-indexed trial within each (participant_id, task_id) |
| response | the 10-digit attribute combination as a string of 0/1 with leading zeros, e.g. `0110110110`; on the forced_choice row it is the starting combination the app displayed |
| phase | `practice` for the first block of each wave, `test` for the incentivized blocks |
| forced_choice | 1 on the first row of each block: the starting combination displayed by the app, not a choice; 0 on the participant's submissions |
| participant__is_bot | oTree bot flag; 0 on every row |
| participant__index_in_pages | oTree page index the participant had reached when the data were exported |
| participant__max_page_index | number of pages in the oTree session; constant |
| participant__current_app_name | oTree app the participant was on at export; `finishing_app` on every row (everyone completed the study) |
| participant__current_page_name | oTree page the participant was on at export |
| participant_time_started | date and time the participant started the study session of that wave |
| participant_visited | oTree flag; 1 on every row |
| participant_payoff | the participant's total points over all incentivized blocks of all five tasks in that wave |
| player_id_in_group | oTree id within the single-player group; 1 on every row |
| player_payoff | points accumulated in this block (rounded sum of player_landscape_payoff; 0 in the practice block); repeated on every row of the block |
| player_comp_creature_buying | answer to the comprehension question on who buys the art (open response; correct answer 'alien') |
| player_comp_symbol_changes | answer to the comprehension question on how many symbols can change per trial (options 1..3; correct answer 1) |
| player_comp_symbols_buy | answer to the comprehension question on how many pictures the alien buys (options 1..3; correct answer 3) |
| player_comprehension_times | number of attempts (1 to 6) the participant needed to pass this task's three comprehension questions |
| player_nk_landscape | raw 10-digit combination, same as response |
| player_landscape_id | index of the combination among the landscape's 1024 configurations: int(combination, 2) + 1 |
| player_landscape_payoff | points the landscape pays for this combination |
| player_search_distance | the app's Hamming distance from the best-paying earlier combination of the block, recorded as 0 whenever this combination sets a new block best (analysis.py recomputes the paper's measure from the strings) |
| player_active_search | the app's flag for a combination not submitted before in the block (1) or a repeat (0); 0 on the starting combination |
| player_start_time | Unix time in seconds at which the participant started this task |
| player_end_time | not filled by the app; 0 on every row |
| player_total_time_spent | seconds spent in the task as recorded by the app (0 where the app did not fill it) |
| player_submission_times | seconds between the previous submission and this one (a response time) |
| player_instructions_completion_time | seconds spent on the task's instruction page |
| player_comprehension_completion_time | seconds spent on the task's comprehension check |
| player_presentation_order | id of the block's landscape (1..4, each with its own fixed starting combination), shown in random block order |
| group_id_in_subsession | oTree group id; 1 on every row |
| session_code | oTree session code of the wave |
| session_is_demo | oTree demo flag; 0 on every row |

## Text-format conversion

All five experiments were transcribed (one `transcriptsN.jsonl` each); none were skipped. Each is a discrete-choice task whose options are nameable in words (five bandit buttons, two sampling buttons plus the stop-and-choose actions, observe/guess in the lightbulb task, a 0–19 box grid, and a 10-bit attribute combination), so every paradigm is textifiable. A retest participant's transcript holds both waves in order, separated by the sentence "About one month later you do the same task again, with the same instructions." In exp1 the sample lines carry no outcome because the source does not record what each sample paid; only the final draw's points are shown. In exp4 the displayed starting combination of each block is narrated without a response marker.

Sample transcript (exp0, participant P000):

```
You play a game with five buttons. On each trial you click one button and it reveals a number of points; your goal is to earn as many points as possible. The screen shows the trial number, how many times each button has been selected, the average points per click for each button, and your total points so far. For every 100 points you earn a bonus of 1p. On each trial press the letter for the button you choose: Button 1 = C, Button 2 = D, Button 3 = E, Button 4 = B, Button 5 = A.
practice block begins with five new buttons.
practice trial: you press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

All five experiments got a text simulator (`simulate0.py`–`simulate4.py`) and each passed the
round-trip check: `build_jsonl.py` re-transcribes the simulator's own `expN.csv` byte-identically
to the simulator's prompts (exp0/exp1 reproduce the per-participant letter mapping with the same
seeding as `build_jsonl.py`). No experiment was skipped. Notable assumptions: exp0 draws each
button's mean as an integer in 43..60 and pays max(0, round(Normal(mean, 5))) points per click,
the distribution seen in the data (the paper's Supplemental Information holds the design values);
exp1 plays the study's six option pairs (practice pair first, the other five in random order and
random left/right position) and lets the agent sample until it presses a stop-and-choose letter,
with every sample paying its outcome (the shipped CSV has no per-sample outcome); exp3 draws the
number of boxes opened from a geometric distribution (mean ~5, matching the data); exp4 generates
a standard N=10, K=3 NK landscape per block since the study's realized landscapes are not public,
opens each block with one of the study's four starting combinations, and sets
`player_landscape_id` to `int(combo, 2) + 1` per the data's coding. oTree session/app-metadata
columns that a simulator cannot produce are dropped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Online experiment

All five experiments got a runnable static `experiments/expN/` (jsPsych v8). The headless
`?mode=simulate` round trip passed for all five (schema, dtypes, codings, and per-`task_id`
counts match `expN.csv`). Status is `needs-review` because the `exp4` alien-game NK payoff
landscapes are not public ("available on request"), so a standard N=10, K=3 landscape is generated
(normalized to ~[0.25,1], ×24.3) — the design is reproduced but not the study's exact realized
payoff function; `player_landscape_id` was omitted (its meaning is unrecoverable). Raw oTree
session/app-metadata columns that a fresh browser session cannot produce are omitted from every
export. Cosmetic-only assumptions (button colours, header wording, pacing) are documented per
experiment in `experiments/README.md`.

Run: openrouter/deepseek/deepseek-v4-flash-vision-exp, 2026-08-25

## Verification

Verdict: pass (critical 3, major 5, minor 6; fixed 11, open 3).

Checked: paper (10.1038/s41467-024-51685-z, 23 pages), original data (https://doi.org/10.17605/OSF.IO/F62MY: the ten oTree task exports, the two initial_app files, the codebook, the authors' R code and data_final.csv), exp0-exp4, transform re-run (the original transform.py reproduced all five CSVs byte for byte; the corrected one regenerates them), transcripts (build_jsonl.py regenerates every transcriptsN.jsonl byte for byte), simulators (all five round-trip byte-identically through build_jsonl.py), analysis (both effects reproduce), logs; the repo has no model.py or cognitive-modeling stage. Skipped: none.

Fixed:
- critical, exp1.csv: transform.py took response from player.sampling_option (the button chosen at the end of a block, constant within the block) and kept all 100 raw rows per block although 84% of them are padding (player.selection = 0). The sampled button per trial is player.selection, as the codebook, the authors' R code (sum(player.selection > 0)) and data_final.csv confirm. Fixed: padding dropped, response = sampled button, one final_choice row per block (response 2/3 = stop and be paid from Button 1/2, reward = the final payout); 552,600 -> 97,938 rows; transcripts1.jsonl and simulate1.py rebuilt with four response letters.
- critical, exp4.csv: the 10-digit combinations were read as numbers, so 12,199 of 34,262 rows lost their leading zeros (0110110110 -> 110110110); player_landscape_id = int(combo, 2) + 1 confirms the source strings. Fixed with a text dtype in transform.py and build_jsonl.py; exp4.csv, transcripts4.jsonl, simulate4.py regenerated.
- critical, exp4.csv: the first row of every block is the starting combination the app displayed (codebook; submission time 0; only four distinct values; skipped by the authors' R code), but it was shipped and transcribed as a free response. Fixed: forced_choice = 1 on that row, narrated without a response marker, simulate4.py opens each block with one of the study's four start combinations.
- major, all CSVs and README: participant ids were assigned per wave and per task, and the README said the waves cannot be linked. The source's initial_app files link every oTree participant.code to an anonymized Prolific id (all 254 time2 ids are time1 ids; every task code is listed), and the schema requires participant_id to identify the person across `session`. Fixed: one participant_id per person (P000..P677) in both waves and all five experiments, task_id counting blocks across waves; a retest participant's transcript holds both waves in order.
- major, transcripts0.jsonl: the bandit transcript omitted the points revealed on every click (player_payoff_1, the source's per-trial player.payoff) and had no block boundaries although every block resets the buttons. Fixed in build_jsonl.py; simulate0.py now emits the payoffs (means 43..60, SD 5, derived from the data and documented as an assumption).
- major, transcripts1.jsonl: 606 marked responses per participant against 600 CSV rows (the final choice had no row). Fixed by the exp1 transform change.
- major, analysis.py: the exploit-complement used the same-row bandit averages, which already include the current click (Methods p. 14: the arm that paid most 'so far'; the authors' R code lags by one trial); switches crossed block boundaries; the alien measures used the app's player_search_distance (0 whenever a trial sets a new block best; 34% of rows differ from the paper's definition) and included the displayed start rows; the alien reference r was 0.50 where Fig. 1 gives 0.52. Fixed to the paper's definitions; both effects reproduce (bandit r = 0.460 vs 0.47; alien r = 0.506 vs 0.52).
- major, README: the column tables hid 26-35 columns per experiment behind an 'others' row; player_landscape_id was described as the landscape identifier (it is the combination's 1-based index among the 1024 configurations; the landscape id is player_presentation_order), player_presentation_order was called session metadata (it is the design/pair id in every task), the light colour was said to be known only on observe trials (recorded on every trial), and N was given as 921-932 per task (wave-participants counted twice). Rewritten: every column documented from the codebook, N per experiment, exp1/exp4 notes.
- minor, README: Columns headings ### -> #### expN; N per experiment stated in the summary.
- minor, simulate1-4.py wrote phase = 'incentivized' where the CSVs use 'test'; simulate2.py recorded the light colour only on observe rows although the source records it on every trial. Fixed.
- minor, exp4: the paper's 10 trials per block (3 in practice) appear as 11/4 rows in the source because of the displayed start row; resolved by the forced_choice flag and noted in the README.

Open:
- minor: exp0.csv: one time1 participant has 19 practice trials and two have 39 trials in one incentivized block (paper p. 14: 20/40); inside the source, noted in the README.
- minor: exp4.csv: the source's player_active_search is 1 on 1,883 rows whose combination had already been submitted in the block; documented as the app's flag, analysis.py recomputes the paper's measure from the strings.
- minor: exp1: the source records no outcome for the individual samples, so the sample lines of transcripts1.jsonl carry no points (only the final draw's payout); the simulator does show them. Documented in the README.

Run: claude-fable-5-1, 2026-09-09
