---
tags:
- paradigm:bandit
- cognitive-modeling:needs-review
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---
# witte_2024_how

- Paper: https://doi.org/10.31234/osf.io/tzuey
- Data source: https://osf.io/ra7su/ (backing OSF project "Measuring Exploration Strategies"; also https://osf.io/ra7su/files/osfstorage/67532a75b1db55362bbbfec8/)
- PDF: https://osf.io/tzuey/download
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Witte, K., Thalmann, M., & Schulz, E. (2024). How should we measure exploration? [Preprint]. PsyArXiv. https://doi.org/10.31234/osf.io/tzuey

## Experiment summary
Two-session online retest study (Prolific; N=238 with at least one session, 236 in session 1, 177 in session 2) measuring human exploration across three few-armed bandit tasks: a Horizon task (80 rounds of 4 forced + 1/6 free slot choices, information and horizon conditions), a two-armed bandit (30 rounds x 10 free choices under Stable/Drifting reward conditions), and a restless 4-arm bandit (200 consecutive choices among drifting arms). Participants also completed three working-memory tasks (updating, operation span, symmetry span) and exploration/mood/anxiety/depression questionnaires. Responses are keyboard arm choices with RT and reward per trial, Likert-scale questionnaire items, and WM accuracy scores. The research goal was the psychometric reliability, convergent/external validity, and improved computational modeling (UCB/directed/random exploration, hierarchical Bayesian and ML fits) of model-based exploration measures.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV (final* CSV's ID column), kept as-is — anonymous integer not a Prolific hex ID |
| trial | 0-indexed trial counter restarting within each (participant_id, task_id); continues across sessions; follows source order within each file |
| response | Chosen arm: 0/1 for Horizon and 2-armed bandits, 0/1/2/3 for Restless bandit; Likert-scale item score for questionnaires (task_id=4, native indexing retained); WM accuracy/proportion score for task_id=3; NA for horizon=5 placeholder trials (valid=0) |
| task_id | 0=Horizon bandit, 1=Two-armed bandit, 2=Restless bandit, 3=Working memory (wm-performance.csv), 4=Questionnaires |
| session | Data-collection wave: "session1" (initial, N=236) or "session2" (retest, N=177) |
| phase | "questionnaire" (task_id=4), "working_memory" (task_id=3); NaN for bandit tasks |
| block | 0-indexed game/block number: Horizon 0..79 (80 games), 2-armed 0..29 (30 games per session); NA for Restless, WM, questionnaires |
| reward | Reward/payoff received on that trial in source units (points); NA for horizon=5 placeholder rows |
| rt | Reaction time in milliseconds (source already in ms); NA for horizon=5 placeholder rows and non-bandit task rows |
| info | Horizon task information condition: -1, 0, 1 coding per original task; only on task_id=0 rows |
| reward1 | Pre-generated reward value for arm 1 on that trial (bandit tasks); NA for WM/questionnaires |
| reward2 | Pre-generated reward value for arm 2 on that trial (bandit tasks); NA for WM/questionnaires |
| reward3 | Pre-generated reward value for arm 3 (Restless bandit only); NA otherwise |
| reward4 | Pre-generated reward value for arm 4 (Restless bandit only); NA otherwise |
| horizon | Horizon task game length (5 or 10 trials); only on task_id=0 rows |
| forced_choice | 1 for first 4 trials of each Horizon game (experimenter-instructed/forced), 0 for free-choice trials; only on task_id=0 rows |
| valid | 0 for horizon=5 placeholder rows (trials 6-10 never presented), 1 for all actual observations |
| condition | 2-armed bandit condition: "SS" (both stable), "SF" (arm1 stable/arm2 drifting), "FF" (both drifting), "FS" (arm1 drifting/arm2 stable); only on task_id=1 rows |
| questionnaire | Questionnaire name: "PANAS" (20 items), "STICSA" (22 = 21 items + the embedded attention-check item at item_index 9, "I know how to read and write"), "BIG_5" (6), "PHQ_9" (10 = 9 items + the embedded attention-check item at item_index 6, "Failure to read these survey questions?"), "CEI" (4); only on task_id=4 rows |
| item_index | 0-indexed item number within each questionnaire; only on task_id=4 rows |
| motiv_mem_0 | Self-reported motivation for memory tasks (0–100 scale); only on task_id=4 rows |
| motiv_slot_0 | Self-reported motivation for slot-machine/bandit tasks (0–100 scale); only on task_id=4 rows |
| mem_aid_0 | Whether participant used memory aids (0/1); only on task_id=4 rows |
| slot_aid_0 | Whether participant used slot-machine aids (0/1); only on task_id=4 rows |
| gender | Participant gender: "m" (Sex_0=0, source label "Male"), "f" (Sex_0=1, "Female"), "other" (Sex_0=2, "Other"); mapping taken from the source task code (questionnaires.html stores the label index); only on task_id=4 rows |
| feedback | Free-text feedback response; only on task_id=4 rows |
| age | Self-reported age in years, asked in each session; three source entries are implausible typos (339, 3318, 43121212) and are kept as shipped; only on task_id=4 rows |
| edu | Self-reported education (free-text: years, categorical labels, or numeric); only on task_id=4 rows |
| income_0 | Average monthly income after tax, band 0–8 from the source task code: 0 = <$500, 1 = $500–1000, 2 = $1000–1500, 3 = $1500–2000, 4 = $2000–2500, 5 = $2500–3000, 6 = $3000–3500, 7 = $3500–4000, 8 = >$4000; only on task_id=4 rows |
| questionnaire_duration | Total time spent on the whole questionnaire page, in minutes as recorded by the source (one value per participant and session, repeated on every task_id=4 row of that session) |
| attention1 | Number of the two embedded attention-check items answered as instructed (STICSA item_index 9 = 3, PHQ_9 item_index 6 = 0); constant 2 because the source ships only participants who passed both; only on task_id=4 rows |
| wm_measure | Working-memory measure name: "OS_recall", "SS_recall", "WMU_recall", "OS_processing", "SS_processing", "prop_timeout_os_processing", "prop_timeout_ss_processing", "rt_os", "rt_ss"; only on task_id=3 rows |

All five task types (Horizon, two-armed, restless bandits; WM; questionnaires) are combined into a single exp0.csv with `task_id` distinguishing them; `session` distinguishes the two retest waves. The `.Rda` files (`banditsWave1.Rda`, `banditsWave2.Rda`) duplicate the CSV data and were not ingested separately. Horizon games with horizon=5 only present 10 trials in the source; trials 6–10 of such games are placeholder rows marked `valid=0`. Two of the 177 session-2 participants (IDs 42 and 177) were excluded from session 1 for incomplete data (`exclusions1_noPID.csv`) and have no session-1 task rows, only their session-1 working-memory scores from `wm-performance.csv`; the 175 participants with both sessions are the paper's final sample (p. 11). The practice rounds of the three bandit tasks are not in the source data files.

## Text-format conversion

Transcribed as `transcripts0.jsonl` (238 participants, one line each covering both sessions). All five sub-tasks (Horizon, two-armed, restless bandits; working-memory scores; questionnaires) are textifiable and included; no experiment was skipped. Horizon `valid=0` placeholder rows (trials never presented) are omitted from the narrative. Response tokens: S/K for the two-armed and Horizon tasks, S/D/K/L for the restless bandit (keys from the paper's methods), and a bare Likert integer for the questionnaire items. Only the payoff received on the chosen arm is narrated, since the unpicked arm's reward was never shown.

Sample transcript (start to the first `[/HUMAN_RESPONSE]`):

```
You take part in a two-session study on decision-making and memory.
You are m, age 34, education code 17, income band 0.
Session session1
In the memory phase you complete three working-memory tasks in a row: an operation-span task, a symmetry-span task, and an updating task. In each you recall items while doing a concurrent processing task. The scores below are your recorded results for the phase.
Your recall accuracy on the operation-span task was 0.869444.
Your recall accuracy on the symmetry-span task was 0.925.
Your recall accuracy on the updating task was 0.8.
Your processing accuracy on the operation-span task was 0.988889.
Your processing accuracy on the symmetry-span task was 1.
Your proportion of timed-out processing responses on the operation-span task was 0.0111111.
Your proportion of timed-out processing responses on the symmetry-span task was 0.
Your mean processing reaction time on the operation-span task was 10342.1 ms.
Your mean processing reaction time on the symmetry-span task was 4647 ms.
You now play the Horizon task.
In this task you play many rounds with two slot machines: left = S, right = K. A message above the machines tells you whether this is a long round (10 picks) or a short round (5 picks). In the first four picks of every round one machine is highlighted and you must press that machine's key; after that you choose freely. After every pick you see the points that machine paid out.
Round 1: long, information condition 0.
The S machine is highlighted, so you press S. You win 54 points.
The K machine is highlighted, so you press K. You win 46 points.
The S machine is highlighted, so you press S. You win 66 points.
The K machine is highlighted, so you press K. You win 35 points.
The machines disappear, reminding you how many free choices remain.
You are told you can make six free choices.
You press [HUMAN_RESPONSE]S[/HUMAN_RESPONSE] …
```

Run: deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling (the Restless-bandit UCB and Horizon Wilson per-participant MLE fits are degenerate / non-identifiable).
Reproduced: none.
Not reproduced: none (the only reliably evaluable claim, the two-armed bandit negative value-guided/random-exploration parameter correlation, reproduced with r ~ -0.97; the Restless and Horizon claims could not be evaluated faithfully).
Numeric mismatch: none.
Indeterminate: The paper's headline modeling results are psychometric (test-retest reliability ICC, convergent validity, SEM factor structure) and out of this pipeline's scope. The remaining concrete cognitive-model parameter claims require hierarchical Bayesian fitting (brms/Stan) that this pipeline's per-participant MLE cannot faithfully reproduce: the Restless bandit UCB fit degenerates (directed-exploration beta saturates at the bound for all participants, under both the code's and the paper's Eq-7 parameterization, with tau collapsing toward 0), and the Horizon task per-participant logistic fits are separation-prone with no significant long-vs-short value-guided difference (p=0.32). Only the two-armed bandit value-guided/random negative parameter correlation reproduced.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`experiments/exp0/` is a static jsPsych v8 port of one session (session1) of the
full battery — working-memory tasks (operation span, symmetry span, updating),
the three bandit tasks (Horizon, two-armed, restless), and the five
questionnaires. Because the repo carries no simulator, it was built from the
paper and the original OSF task code; the experiment ships a `?mode=simulate`
headless round trip, and the saved CSV was confirmed to match `exp0.csv`'s
exact schema for a single participant-session (column names, per-task counts,
0-indexed trial restart, response codings, reward consistency, pre-sampled
reward sequences, Horizon `valid=0` placeholders, questionnaire item order).
See `experiments/README.md` for setup, the `saveData` data seam, and notes.
The WMU updating-task digit sequences are drawn from the source's generative
rules (the pre-sampled sequences are not in the uploaded materials), so those
trials are not byte-identical to the source's; the recorded WM summary rows are
performance-derived and unaffected. Browser-only cosmetic defaults (machine
colors, feedback/ITI timings, Continue steps) are documented there.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

- `simulate0.py`: one text simulator for the full two-session battery — the
  Horizon, two-armed and restless bandits, the working-memory scores, and the
  five questionnaires — format-identical to `transcripts0.jsonl`
  (`[HUMAN_RESPONSE]` markers, instruction wording, block separators and number
  formatting all mirror `build_jsonl.py`). The round-trip check (simulate →
  `exp0.csv` → `build_jsonl.py` → compare against `prompts[i]`) passes
  byte-for-byte for every simulated participant.
- The bandit reward sets are pre-sampled once per session and are identical for
  every participant, mirroring the paper's "pre-sampled and the same for all
  participants" design; only the agent's choices and the demographics/WM/
  questionnaire/feedback draws differ between participants.
- ASSUMPTIONs (audit in `simulate0.py`'s docstring): reward sets are drawn
  afresh from the paper's generative processes (the OSF pre-sampled sets are
  not shipped); session2 present with p = 177/238 and the WM block with
  p = 354/413 as in exp0.csv; demographics are sampled from exp0.csv's
  empirical distributions (age ~ N(34.2, 7.8), clipped 18-66), and the last
  participant of each run gets a free-text education code so the CSV column
  stays object-typed (as in the real data).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 1, major 1, minor 8; fixed 6, open 4).

Checked: paper (DOI 10.31234/osf.io/tzuey, PDF from osf.io/tzuey/download, 22 pages), original data (OSF ra7su: data/final{Horizon,2armedBandit,Restless,QuestionnaireData}Session{1,2}.csv, wm-performance.csv, exclusions{1,2}_noPID.csv, task code and reward JSON files), exp0, transform re-run (byte-identical before the fixes), transcripts (rebuild byte-for-byte; per-task decode of all 238 transcripts against the CSV), simulator (smoke run and byte-identical round trip through build_jsonl.py), modeling section/tag consistency (no model.py; cognitive-modeling:needs-review matches the indeterminate section), analysis (all 4 effects reproduce), logs. Skipped: none.

Fixed:
- critical: gender was reversed. The source task code (questionnaires.html) stores the label index of ['Male','Female','Other'], so Sex_0 0=male, 1=female, 2=other; transform.py mapped 0->f, 1->m, 2->nb. The paper (p. 11) reports 84 females among the 175 two-session participants, which is exactly the number of 'm' the old CSV had in that group. transform.py now maps 0->m, 1->f, 2->other; exp0.csv regenerated (only gender differs), transcripts0.jsonl rebuilt (only the 'You are <gender>' token changes), simulate0.py gender pool relabeled, README gender row and sample transcript updated.
- major: the 25,606 questionnaire rows (task_id=4) carried the source's whole-page completion time in minutes (median 4.0) in `rt`, which the schema defines as per-response milliseconds and which the README said is NA on non-bandit rows. transform.py now writes it to a new column questionnaire_duration (minutes, source units) and leaves rt empty on those rows; README row added. All other columns are byte-identical to the previous CSV.
- minor: the paper (p. 12) gives STICSA 21 and PHQ-9 9 items while the source ships 22 and 10; the source questionnaires.json shows the extra items are the two attention checks (STICSA item_index 9 'I know how to read and write', PHQ_9 item_index 6 'Failure to read these survey questions?') and attention1 counts them (constant 2). README questionnaire and attention1 rows now say so.
- minor: income_0 bands were undocumented; the README now lists the source's nine monthly-income bands (<$500 .. >$4000).
- minor: three implausible self-reported ages in the source (339, 3318, 43121212) are now noted in the README age row; the values are kept as shipped.
- minor: the paper (p. 11) reports 175 session-2 participants, the source 177. IDs 42 and 177 were excluded in session 1 for incomplete data (exclusions1_noPID.csv) and have no session-1 task rows (only session-1 working-memory scores); the 175 with both sessions are the paper's final sample. Noted in the README.

Open:
- minor: check_repo flags 177/238 transcripts with fewer marked responses than CSV free rows (e.g. participant 10: 1684 vs 1702). The difference is the 18 working-memory summary rows (9 measures x 2 sessions), which are recorded scores narrated as statements, not choices. Per-task decoding matches the CSV for all 238 transcripts.
- minor: check_repo flags 61/238 transcripts for tokens not mapping one-to-one onto the CSV response sequence. The transcripts use the paper's per-task keys (p. 11: S/K for the Horizon and two-armed tasks, S/D/K/L for the restless bandit) plus bare Likert integers, so no single global token mapping exists; per-task decoding, including forced-choice narration and rewards, shows 0 mismatches.
- minor: the questionnaire items are narrated by number only; the item wording exists in the source task code (task/bandit task questionnaires/questionnaires.json) but not in exp0.csv or the transcripts.
- minor: the paper (p. 11) describes one practice round per bandit task; the source data files ship only the 80/30/200 task rounds, so no practice trials could be ingested.

Run: claude-fable-5-1, 2026-09-14
