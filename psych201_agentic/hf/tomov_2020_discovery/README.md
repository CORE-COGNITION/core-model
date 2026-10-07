---
tags:
- paradigm:planning
- cognitive-modeling:needs-review
- psych-101
- text-format:pass
- js-experiment:pass
- simulator:pass
---
# tomov_2020_discovery

- Paper: https://doi.org/10.1371/journal.pcbi.1007594
- Data source: https://github.com/tomov/chunking
- PDF: https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1007594&type=printable
- Full text: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1007594
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation

Tomov, M. S., Yagati, S., Kumar, A., Yang, W., & Gershman, S. J. (2020). Discovery of hierarchical representations for efficient planning. PLoS Computational Biology, 16(4), e1007594.

## Experiment summary

The paper asks whether humans spontaneously discover hierarchical (cluster) representations of the environment to enable efficient planning. Across multiple online navigation experiments, participants drove a virtual "subway" graph one state-to-state move at a time (each move logged with a reaction time) to reach goal stations; the experiments varied the training task distribution, full-map visibility, reward structure, and (in a learning-dynamics study) staged training with interleaved probe trials. The dependent measure is the first move on a test navigation from state 6 to state 1, i.e. whether participants move first to state 5 (crossing fewer cluster boundaries) or state 7. Six experiments with human data are provided: exp0 = Experiment 1 (N=87), exp1 = Experiment 2 (N=241, bad/control/good conditions), exp2 = Experiment 3 (N=127, learning/relearning with probes), exp3 = Experiment 4 (N=77, full map), exp4 = Experiment 5 (N=386, full-map bad/control1/control2/good), and exp5 = Experiment 7 (N=174, reward-driven clusters). Experiment 6 (paper-based reward-generalization questionnaire, N=32) has no data file, and Experiment 8 (active-exploration) is simulation-only in the repo, so neither is included here. Results are explained by a Bayesian hierarchical-planner model fit via MCMC sampling (cognitive modeling).

## Notes

### Columns

One row per actual **move** (a navigation with L path nodes yields L-1 rows). `response` is the 1-indexed node number the participant moved TO on that move; `block` groups the moves of one navigation trip; `trial` is the 0-indexed move counter within a participant. The final per-navigation value of `RTs`/`keys` is the goal-completion (spacebar) press and is a passive acknowledgment, so it is not emitted as a response row.

Experiment files map to the paper as exp0=Exp1, exp1=Exp2, exp2=Exp3, exp3=Exp4, exp4=Exp5, exp5=Exp7.

#### exp0 (paper Experiment 1; subway10_repro)
| column | description |
|--------|-------------|
| group | Experimenter group/counterbalancing label (A/B) for the participant. |
| start | Start node number of the navigation (1-indexed). |
| goal | Target node number (1-indexed); -1 means free choice (no specified goal). |
| path | Full space-separated node sequence visited in the navigation (source path). |
| length | Number of nodes in the path (source length). |
| RTs | Space-separated per-move reaction times in ms (raw source string). |
| keys | Space-separated raw keycodes (raw source string). |
| participant_id | Stable per-participant id (source subj_id, unchanged, as string). |
| phase | Session phase (source stage): train or test. |
| rt_total | Total reaction time for the whole navigation in ms (source RT_tot). |
| trial | 0-indexed move/response counter within participant (one per actual move; a navigation with L path nodes yields L-1 rows). |
| block | 0-indexed navigation-trial counter within participant grouping the moves of one trip. |
| response | The node number the participant moved TO on this move (nodes[m+1] of the path); raw 1-indexed node as recorded (not re-indexed). |
| rt | Per-move reaction time in ms = m-th value of source RTs (the final value, the goal-completion press, is not a move and is not emitted); NaN where RTs too short. |
| key | Per-move raw keycode = m-th value of source keys (goal-completion spacebar press 32 is not emitted as a move); NaN where unavailable. |

#### exp1 (paper Experiment 2; subway9 + controls)
| column | description |
|--------|-------------|
| group | Experimenter group/counterbalancing label (A/B) for the participant. |
| start | Start node number of the navigation (1-indexed). |
| goal | Target node number (1-indexed); -1 means free choice (no specified goal). |
| path | Full space-separated node sequence visited in the navigation (source path). |
| length | Number of nodes in the path (source length). |
| RTs | Space-separated per-move reaction times in ms (raw source string). |
| keys | Space-separated raw keycodes (raw source string). |
| timestamp | Source epoch-seconds timestamp of the navigation trial. |
| datetime | Source human-readable local time of the navigation trial. |
| participant_id | Stable per-participant id (source subj_id, unchanged, as string). |
| phase | Session phase (source stage): train or test. |
| rt_total | Total reaction time for the whole navigation in ms (source RT_tot). |
| condition | Chunk-condition label: bad / control / good (subway9 / subway9_control / subway9_goodchunks). |
| trial | 0-indexed move/response counter within participant (one per actual move; a navigation with L path nodes yields L-1 rows). |
| block | 0-indexed navigation-trial counter within participant grouping the moves of one trip. |
| response | The node number the participant moved TO on this move (nodes[m+1] of the path); raw 1-indexed node as recorded (not re-indexed). |
| rt | Per-move reaction time in ms = m-th value of source RTs (the final value, the goal-completion press, is not a move and is not emitted); NaN where RTs too short. |
| key | Per-move raw keycode = m-th value of source keys (goal-completion spacebar press 32 is not emitted as a move); NaN where unavailable. |

#### exp2 (paper Experiment 3; exp_v2_3_subway10_unlearn_circ)
| column | description |
|--------|-------------|
| group | Experimenter group/counterbalancing label (A/B) for the participant. |
| start | Start node number of the navigation (1-indexed). |
| goal | Target node number (1-indexed); -1 means free choice (no specified goal). |
| path | Full space-separated node sequence visited in the navigation (source path). |
| length | Number of nodes in the path (source length). |
| RTs | Space-separated per-move reaction times in ms (raw source string). |
| keys | Space-separated raw keycodes (raw source string). |
| valid_keys | Source set of keycodes judged valid for the navigation. |
| timestamp | Source epoch-seconds timestamp of the navigation trial. |
| datetime | Source human-readable local time of the navigation trial. |
| participant_id | Stable per-participant id (source subj_id, unchanged, as string). |
| phase | Session phase (source stage): train or test. |
| rt_total | Total reaction time for the whole navigation in ms (source RT_tot). |
| raw_trial | Source 1-indexed trial number within participant (source trial column). |
| trial | 0-indexed move/response counter within participant (one per actual move; a navigation with L path nodes yields L-1 rows). |
| block | 0-indexed navigation-trial counter within participant grouping the moves of one trip. |
| response | The node number the participant moved TO on this move (nodes[m+1] of the path); raw 1-indexed node as recorded (not re-indexed). |
| rt | Per-move reaction time in ms = m-th value of source RTs (the final value, the goal-completion press, is not a move and is not emitted); NaN where RTs too short. |
| key | Per-move raw keycode = m-th value of source keys (goal-completion spacebar press 32 is not emitted as a move); NaN where unavailable. |

#### exp3 (paper Experiment 4; subway10_map)
| column | description |
|--------|-------------|
| group | Experimenter group/counterbalancing label (A/B) for the participant. |
| start | Start node number of the navigation (1-indexed). |
| goal | Target node number (1-indexed); -1 means free choice (no specified goal). |
| path | Full space-separated node sequence visited in the navigation (source path). |
| length | Number of nodes in the path (source length). |
| RTs | Space-separated per-move reaction times in ms (raw source string). |
| keys | Space-separated raw keycodes (raw source string). |
| timestamp | Source epoch-seconds timestamp of the navigation trial. |
| datetime | Source human-readable local time of the navigation trial. |
| participant_id | Stable per-participant id (source subj_id, unchanged, as string). |
| phase | Session phase (source stage): train or test. |
| rt_total | Total reaction time for the whole navigation in ms (source RT_tot). |
| trial | 0-indexed move/response counter within participant (one per actual move; a navigation with L path nodes yields L-1 rows). |
| block | 0-indexed navigation-trial counter within participant grouping the moves of one trip. |
| response | The node number the participant moved TO on this move (nodes[m+1] of the path); raw 1-indexed node as recorded (not re-indexed). |
| rt | Per-move reaction time in ms = m-th value of source RTs (the final value, the goal-completion press, is not a move and is not emitted); NaN where RTs too short. |
| key | Per-move raw keycode = m-th value of source keys (goal-completion spacebar press 32 is not emitted as a move); NaN where unavailable. |

#### exp4 (paper Experiment 5; subway9_map + controls)
| column | description |
|--------|-------------|
| group | Experimenter group/counterbalancing label (A/B) for the participant. |
| start | Start node number of the navigation (1-indexed). |
| goal | Target node number (1-indexed); -1 means free choice (no specified goal). |
| path | Full space-separated node sequence visited in the navigation (source path). |
| length | Number of nodes in the path (source length). |
| RTs | Space-separated per-move reaction times in ms (raw source string). |
| keys | Space-separated raw keycodes (raw source string). |
| timestamp | Source epoch-seconds timestamp of the navigation trial. |
| datetime | Source human-readable local time of the navigation trial. |
| participant_id | Stable per-participant id (source subj_id, unchanged, as string). |
| phase | Session phase (source stage): train or test. |
| rt_total | Total reaction time for the whole navigation in ms (source RT_tot). |
| condition | Chunk-condition label: bad / control1 / control2 / good (subway9_map / subway9_map_control_1 / subway9_map_control_2 / subway9_map_goodchunks). |
| trial | 0-indexed move/response counter within participant (one per actual move; a navigation with L path nodes yields L-1 rows). |
| block | 0-indexed navigation-trial counter within participant grouping the moves of one trip. |
| response | The node number the participant moved TO on this move (nodes[m+1] of the path); raw 1-indexed node as recorded (not re-indexed). |
| rt | Per-move reaction time in ms = m-th value of source RTs (the final value, the goal-completion press, is not a move and is not emitted); NaN where RTs too short. |
| key | Per-move raw keycode = m-th value of source keys (goal-completion spacebar press 32 is not emitted as a move); NaN where unavailable. |

#### exp5 (paper Experiment 7; mines10_map)
| column | description |
|--------|-------------|
| group | Experimenter group/counterbalancing label (A/B) for the participant. |
| start | Start node number of the navigation (1-indexed). |
| goal | Target node number (1-indexed); -1 means free choice (no specified goal). |
| path | Full space-separated node sequence visited in the navigation (source path). |
| length | Number of nodes in the path (source length). |
| RTs | Space-separated per-move reaction times in ms (raw source string). |
| keys | Space-separated raw keycodes (raw source string). |
| reward | Numeric mine reward value delivered for that navigation trial. |
| timestamp | Source epoch-seconds timestamp of the navigation trial. |
| datetime | Source human-readable local time of the navigation trial. |
| participant_id | Stable per-participant id (source subj_id, unchanged, as string). |
| phase | Session phase (source stage): train or test. |
| rt_total | Total reaction time for the whole navigation in ms (source RT_tot). |
| trial | 0-indexed move/response counter within participant (one per actual move; a navigation with L path nodes yields L-1 rows). |
| block | 0-indexed navigation-trial counter within participant grouping the moves of one trip. |
| response | The node number the participant moved TO on this move (nodes[m+1] of the path); raw 1-indexed node as recorded (not re-indexed). |
| rt | Per-move reaction time in ms = m-th value of source RTs (the final value, the goal-completion press, is not a move and is not emitted); NaN where RTs too short. |
| key | Per-move raw keycode = m-th value of source keys (goal-completion spacebar press 32 is not emitted as a move); NaN where unavailable. |


## Text-format conversion

All six experiments were transcribed — exp0/exp1/exp2 (hidden-map navigation), exp3/exp4 (full-map navigation) and exp5 (gold-mine reward navigation). These are graph-navigation planning tasks (which adjacent station or mine to move to next), so each move is a freely chosen, nameable response and the task is fully expressible in text. None were skipped. Each transcript retells the cover story and instructions, every trip, each move (a `[HUMAN_RESPONSE]...[/HUMAN_RESPONSE]` node number), and the outcome; exp0/exp1 also carry the "unreliable trips" warning and interrupted test trips.

**Sample transcript (exp0):**

```
Imagine you are a tourist and you have to navigate the subway network of an unfamiliar town; there are 10 stations, numbered 1 to 10 (the numbers stand for the city names you were shown). On each trip you travel from a starting station to a goal station, which are shown for 2 seconds at the start of the trip. During the trip you see the name of the current station in the middle of the screen, surrounded by the names of its neighbouring stations in the four directions (a circle means no station in that direction). Navigate with the arrow keys; a countdown gives you a moment to plan your route before you can move. When you reach the goal station, press the space bar to end the trip. Your moves are recorded as the number of the station you move to; report each move as that single number.
Trip 1: travel from station 10 to goal station 7.
You are at station 10. Its neighbouring stations are shown: 1, 9. You move to [HUMAN_RESPONSE]9[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

All six experiments (exp0–exp5) got a runnable `experiments/expN/` static jsPsych v8 build (Tomov et al. 2020, subway + gold-mine navigation). The headless round trip (`?mode=simulate`) passed for each: the produced CSV matches the corresponding `expN.csv` columns and the design trip counts (80 train / 3 test for exp0; 80 / 1 for exp1 and exp3, with per-condition counts for exp4; 103 + 143 two-stage with 6 probes for exp2; 100 / 1 for exp5), and no experiment was skipped. Browser-only defaults (2 s instruction, 3 s plan countdown, ~1 s success/gap, node-number display instead of shuffled city names, per-participant graph rotation/flip) are documented in `experiments/README.md`. On exp2 the opaque `valid_keys`/`raw_trial` source fields use documented inferred encodings; on exp5 the design drives the paper's exactly 60 free + 40 forced trips (the dataset's variable free-trip counts are a source-file artifact). Visual check not run (headless run, no pixel inspection).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Indeterminate: the paper never fits a cognitive model to participant behavior. All model parameters are picked by hand and held constant across simulations and experiments (Tomov et al. 2020, p.13, Choices), and the MCMC hierarchy sampler draws hierarchies over the environment (graph, tasks, rewards), not over participants' observed choices. Every human-data result is a standard inferential claim on raw choices/RTs (one/two-tailed binomial tests, chi-square tests of independence, logistic and mixed-effects linear regressions) that requires no model fit — out of scope for auto-exp-modeling. There is no fitted-model comparison (AIC/BIC/WAIC/LOO/parameter recovery) to reproduce.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

All six experiments got a text simulator (`simulate0.py`–`simulate5.py`), each runnable with `uv run simulateN.py -n 3`. For every experiment the round trip passed: a simulated `expN.csv` fed through `build_jsonl.py` reproduces the simulator's own transcript text byte-for-byte. Participants navigate with goal-directed moves (neighbour minimizing distance to the goal, equal-distance neighbours chosen with equal probability, which reproduces the study's 6→5 vs 6→7 choice); per-experiment design details (Exp1: 20× (10→7)/(1→3)/(4→6) + 20 random tasks and 3 interrupted test trips; Exp2: bad/control/good training protocols; Exp3: two 103/143-trip training stages with six interleaved 6→1 probe trips; Exp4: full-map condition; Exp5: full-map bad/control1/control2/good; Exp7: 60 free + 40 forced days with a 0–300 reward landscape) are implemented and documented per file. Nothing was skipped. ASSUMPTIONS surfaced: navigation is goal-directed with no detours; on Exp7 free days the intended mine is the currently most-points mine; Exp7 rewards are resampled per free day with p=0.2 and drawn fresh per participant as the paper prescribes.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
