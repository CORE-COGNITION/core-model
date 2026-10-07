---
tags:
- paradigm:goal-pursuit
- cognitive-modeling:pass
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
---
# holton_2024_goal

- Paper: https://doi.org/10.1038/s41562-024-01844-5
- Data source: https://osf.io/mvquk/
- PDF: https://www.nature.com/articles/s41562-024-01844-5.pdf
- Full text: https://www.nature.com/articles/s41562-024-01844-5
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Holton, E., Grohn, J., Ward, H., Manohar, S. G., O'Reilly, J. X., & Kolling, N. (2024). Goal commitment is supported by vmPFC through selective attention. Nature Human Behaviour, 8, 1351–1365. https://doi.org/10.1038/s41562-024-01844-5

## Experiment summary
In an incremental goal-pursuit decision task, participants repeatedly chose among three continuously-offered goods (random-walk point magnitudes with occasional large shifts) to fill a progress "net," deciding each trial whether to persist with the current goal or abandon progress for a better alternative. A spatial-attention task (outside the scanner) measured goal-directed attention through recall of stimulus locations. Across two studies — an fMRI study (exp0, here n=10 of a reported ~30) and a vmPFC lesion patient study with age-matched controls (exp1, here n=20 of a reported ~26) — participants showed a persistent over-commitment to their current goal (abandoning less than optimal), with persistence increasing with accumulated goal progress and sensitivity to alternative-value fading faster than sensitivity to the current goal's value. Response type was a per-trial choice among 3 options plus spatial-location reports; the key manipulation was goal progress/goal size and current-vs-alternative goal value.

## Online experiment

A static jsPsych v8 online experiment was built for both experiments (`experiments/exp0/`
and `experiments/exp1/`), porting the text simulators: the goal-pursuit "fishing net" task
(exp0, 300 scan + 100 post-scan trials; exp1, one 250-trial session). The headless
`?mode=simulate` round trip passed for both — the saved CSV matches `expN.csv`'s schema
(column names, codings, counts; exp0 → 400 rows, exp1 → 250 rows). No experiment was
skipped. Two categories of columns are left blank and noted in `experiments/README.md`:
the `myopic_*`/`prosp_*`/`sampler_*` cognitive-model predictions and the omitted
spatial-attention subtask columns, neither of which a fresh data-collection run produces;
exp1's `condition`/`participant` and exp0's `participant` are placeholders (`CONFIG`),
and cosmetic timings/layout are documented defaults.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Text-format conversion

The goal-pursuit ("fishing net") decision task is transcribed for both experiments
(exp0: 10 fMRI participants, 4000 decisions across the in-scanner and post-scan
sessions; exp1: 20 patient/control participants, 5000 decisions). The interleaved
spatial-attention subtask — reporting the flashed on-screen location of each
creature — is **not** textifiable (stating the location makes it trivial; omitting
it makes the response unknowable), so it is excluded. The three offered goods are
identified in the data only by a 1/2/3 item index (screen order was randomised per
trial), so a fixed assumption is used: item 1 = crab, item 2 = octopus, item 3 =
fish; this does not change the recorded persistence/abandonment structure.

Sample transcript (exp0, first response):

```text
You are fishing, filling nets with seafood. Your goal is to fill as many nets as possible; each net you complete earns you 1 point. On every trial you see offers for three kinds of seafood, always crab, octopus and fish, each showing how much of that good you can add to your net this trial (in points; a negative value subtracts from the net, and cannot take your net below empty). Your net can hold only one kind of seafood at a time. If you choose the kind already in your net, its quantity is added to your collected amount. If you choose a different kind, you abandon the current net, losing everything you had collected, and the net restarts with just the newly chosen quantity. A net is full when its contents reach its capacity, at which point you earn a point and a fresh net opens. To choose, press the name of the seafood you want to collect: crab, octopus, or fish.
A new net opens (capacity 40.0). Offers: crab 5.3, octopus 5.3, fish 4.6 points. You start the net with [HUMAN_RESPONSE]crab[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators
Both experiments got a text simulator, `simulate0.py` (exp0, in-scanner + post-scan
sessions) and `simulate1.py` (exp1, patient/control study with a shared schedule),
that reproduce the paper's offer/block generative process (net sizes uniform 12-72,
starting offers N(6,1), Gaussian random walks sigma^2=0.8 with P=0.1 up/down jumps to
start+/-U(3,9), net filled when contents reach capacity). Both pass the round-trip
check through `build_jsonl.py` (regenerated transcripts byte-identical to the
simulated prompts). ASSUMPTIONS: schedules are generated per the paper rather than
reusing the exact shared-schedule assignment; the paper's tree-search feasibility
filter (3-15 trials) is not replicated; exp1 assigns P000-P009 patient / P010-P019
control. Note: block length is choice-agent dependent, so a uniform-random smoke-test
agent fills nets slowly (few, long blocks); a goal-directed agent fills them in the
~7-trial cadence of the real data.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: offer-max, myopic, prospective, tree-search logistic regressions on switch value (LOO-CV accuracy; per-participant IP=-b0/b1, Wilcoxon>0).
Reproduced: tree_search_best_model, persistence_bias_positive.
Not reproduced: none.
Numeric mismatch: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | Anonymized subject id P000..P009; n=10 in first-appearance order (MRI sub_0,10-18). |
| task_id | 0 = in-scanner goal-pursuit task, 1 = post-scan spatial-attention task. |
| phase | scan / post_scan session the row came from. |
| trial | 0..N-1 response index within each (participant_id, task_id), in presentation order. |
| block | 0-indexed goal block (source block-1); new progress net per block. |
| response | Participant's choice among the 3 offered goods, 0-indexed (source choice 1/2/3 -> 0/1/2). |
| participant | Original numeric participant index from the processed source CSV. |
| scheduleID | Schedule number used for this participant's goal blocks. |
| trial_number | 1-indexed trial number within a block (source). |
| total_trial_number | 1-indexed cumulative trial number across blocks (source). |
| goal_size | Net capacity (required accumulated value) for the current goal block. |
| magnitudes_1..3 | Magnitude of each of the 3 offered goods on the current trial (points). |
| choice | Raw 1/2/3 choice code (source); response = choice-1. |
| net_contents | Accumulated net contents at trial start. |
| net_contents_end | Accumulated net contents after the choice (scan only). |
| switch_trial | 1/0 whether this trial is a goal-switch trial in the schedule. |
| choice_onset_time | Onset time (ms) of the choice display (scan only). |
| deltaMagnitudes_1..3 | Change in magnitude of each goods from previous trial. |
| goal_item_idx / best_alt_idx / worst_alt_idx | 1/2/3 indices of goal item, best and worst alternative this trial. |
| mag_goal_item / mag_best_alt / mag_worst_alt | Magnitude of goal item, best and worst alternative. |
| trials_invested | Number of trials invested in current goal at trial start. |
| prop_filled | Proportion of the net filled (net_contents/goal_size). |
| raw_distance | Remaining distance to goal (goal_size - net_contents). |
| chosen_goes_negative | Whether choosing the max option would reduce net contents (0/1). |
| offer_max_value | Value of the highest current offer. |
| myopic_values_1..3, myopic_goal_item, myopic_best_alt, myopic_worst_alt, myopic_switch_value | Myopic (single-step) model predictions. |
| sampler_choice, sampler_values_1..3, sampler_goal_item, sampler_best_alt, sampler_worst_alt, sampler_uncertainty_goal_item/best_alt/worst_alt, sampler_estimated_proximity | Tree-search sampler model predictions and uncertainties. |
| prosp_goal_item_1, prosp_best_alt_1, prosp_worst_alt_1, prosp_switch_value_1 | 1-step prospection model predictions (blank when not computed). |
| in_scanner | 1 = trial from scanner run, 0 = post-scan (source field, both phases). |
| original_ID | Original paper subject number from the source CSV (e.g. 21, 32..40). |
| itm1_xloc/itm1_yloc..itm3_yloc | True (x,y) on-screen locations of the 3 goods (post_scan only). |
| itm1_xresp/itm1_yresp..itm3_yresp | Participant's reported (x,y) location recall for each good (post_scan only). |
| itm1_RT..itm3_RT | Response time (s) for each location recall (post_scan only). |
| responseOrder_1..3 | Order in which the participant selected the 3 location recalls (0/1/2). |
| itm1_err..itm3_err | Distance error between reported and true location per good (post_scan only). |
| decisionRT | Time (s) to make the goal choice (post_scan only). |

### exp1
| column | description |
|--------|-------------|
| participant_id | Anonymized subject id P000..P019 in first-appearance order (patients then controls). |
| condition | patient (lesion patient, all_patient_*) or control (elderly age-matched control). |
| trial | 0..N-1 response index within each participant, in presentation order. |
| block | 0-indexed goal block (source block-1); new progress net per block. |
| response | Participant's choice among the 3 offered goods, 0-indexed (source choice 1/2/3 -> 0/1/2). |
| participant | Original numeric participant ID from source CSV (e.g. 303, 10). |
| trial_number | 1-indexed trial number within a block (source). |
| total_trial_number | 1-indexed cumulative trial number across blocks (source). |
| goal_size | Net capacity (required accumulated value) for the current goal block. |
| magnitudes_1..3 | Magnitude of each of the 3 offered goods on the current trial (points). |
| val_itm1..3 | Presented value of each of the 3 goods (same as magnitudes here). |
| choice | Raw 1/2/3 choice code (source); response = choice-1. |
| net_contents | Accumulated net contents at trial start. |
| switch_trial | 1/0 whether this trial is a goal-switch trial in the schedule. |
| itm1_xloc/itm1_yloc..itm3_yloc | True (x,y) on-screen locations of the 3 goods. |
| itm1_xresp/itm1_yresp..itm3_yresp | Participant's reported (x,y) location recall for each good. |
| itm1_RT..itm3_RT | Response time (s) for each location recall. |
| responseOrder_1..3 | Order in which the participant selected the 3 location recalls (0/1/2). |
| itm1_err..itm3_err | Distance error between reported and true location per good. |
| decisionRT | Time (s) to make the goal choice. |
| deltaMagnitudes_1..3 | Change in magnitude of each goods from previous trial. |
| goal_item_idx / best_alt_idx / worst_alt_idx | 1/2/3 indices of goal item, best and worst alternative this trial. |
| mag_goal_item / mag_best_alt / mag_worst_alt | Magnitude of goal item, best and worst alternative. |
| trials_invested | Number of trials invested in current goal at trial start. |
| prop_filled | Proportion of the net filled (net_contents/goal_size). |
| raw_distance | Remaining distance to goal (goal_size - net_contents). |
| chosen_goes_negative | Whether choosing the max option would reduce net contents (0/1). |
| offer_max_value | Value of the highest current offer. |
| myopic_values_1..3, myopic_goal_item, myopic_best_alt, myopic_worst_alt, myopic_switch_value | Myopic (single-step) model predictions. |
| prosp_goal_item_1..3, prosp_best_alt_1..3, prosp_worst_alt_1..3, prosp_switch_value_1..3 | 1-, and multi-step prospection model predictions. |
| sampler_choice, sampler_values_1..3, sampler_goal_item, sampler_best_alt, sampler_worst_alt, sampler_uncertainty_goal_item/best_alt/worst_alt, sampler_estimated_proximity, sampler_switch_value | Tree-search sampler model predictions and uncertainties. |