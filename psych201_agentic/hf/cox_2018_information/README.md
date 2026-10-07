---
tags:
- paradigm:memory
- cognitive-modeling:needs-review
- psych-101
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:pass
---

# cox_2018_information

- Paper: https://doi.org/10.1037/xge0000407
- Data source: https://osf.io/dd8kp/
- PDF: https://memolab.syr.edu/wp-content/uploads/2021/04/Coxetal_2018.pdf
- Full text: https://psycnet.apa.org/fulltext/2018-17847-005.html
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Cox, G. E., Hemmer, P., Aue, W. R., & Criss, A. H. (2018). Information and processes underlying semantic and episodic memory across tasks, items, and individuals. Journal of Experimental Psychology: General, 147(4), 545-590. https://doi.org/10.1037/xge0000407

## Experiment summary
A single large study (N=462 participants in this dataset) had each participant complete five episodic/semantic memory tasks: single-item recognition, associative recognition, cued recall, free recall, and lexical decision. Each task presents word pairs or single words across study and test phases; responses are old/new recognition decisions, recalled words, and lexical decisions, recorded with reaction times and subsequently classified as hits/FAs/CR/miss or recall categories. The research question is how shared cognitive processes and item information give rise to correlations across memory tasks, addressed via hierarchical Bayesian joint analysis and fitted drift-diffusion/logistic (Wiener) models. Memory performance was above chance across all five tasks.

## Notes

### Columns

| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV, as string (1..462) |
| trial | 0..N-1 within each (participant_id, task_id), in chronological presentation order |
| response | Raw `resp` from source. `study` rows: the 1-9 association rating. `test` rows of the three binary tasks (associative recognition, lexical decision, single recognition): 0/1 = no/yes. `test` rows of cued and free recall: 0/1 = whether a word was produced (Hit/FA = 1, Miss = 0); the typed word is in `resp.string`. Free recall lists one recalled-word row per response plus one Miss row per unrecalled studied word |
| task_id | 0-indexed task type: 0=Associative recognition, 1=Cued recall, 2=Free recall, 3=Lexical decision, 4=Single recognition |
| block | 0-indexed study/test list cycle within each (participant_id, task_id) |
| phase | `study` or `test` phase of the task |
| condition | snake_case task type (same grouping as task_id) |
| rt | Reaction time in milliseconds (source `rt` is seconds, ×1000). `study` rows carry the fixed 2000 ms pair presentation, not a reaction time; empty on free-recall Miss rows |
| trial_in_block | Source `trial` 1-indexed within each source block |
| block_source | Original source `block` number (1..15) |
| stim.num.left | Numeric code of left/only stimulus |
| stim.num.right | Numeric code of right stimulus (associative only) |
| stim.string.left | Word shown on the left / the single word |
| stim.string.right | Word shown on the right (associative only) |
| stim.distractor | 0/1 whether a distractor item |
| studied | 0/1 whether item was studied (list item) |
| freq.left | TASA corpus frequency of left stimulus (source `freq`; not the HAL count of the OSF `item_properties.csv`) |
| cv.left | Context variability of left stimulus: number of TASA documents containing the word (source `cv`; not a concreteness rating) |
| old.left | OLD20 of left stimulus: mean orthographic Levenshtein distance to its 20 nearest neighbours (source `old`; equals `OLD20` in the OSF `item_properties.csv`) |
| freq.right | TASA corpus frequency of right stimulus (source `freq`) |
| cv.right | Context variability of right stimulus (source `cv`) |
| old.right | OLD20 of right stimulus (source `old`) |
| distractor.resp | 0/1 distractor response flag |
| response_raw | Copy of original `resp` column |
| resp.string | Verbatim recalled/typed response text (free recall) |
| resp.type | Hit/FA/CR/Miss classification of the response |
| resp.type.rescore | Re-scored classification (Hit/FA/Miss) |
| study.pos.left | Position of left stimulus during study list |
| study.pos.right | Position of right stimulus during study list |
| kf.left | Kucera-Francis frequency of left stimulus |
| kf.right | Kucera-Francis frequency of right stimulus |
| resp.string.corr | Correct/partner response string for the trial |
| study.partner.left.num | Numeric code of study partner of left stimulus |
| study.partner.right.num | Numeric code of study partner of right stimulus |
| study.partner.left.string | Study partner word of left stimulus |
| study.partner.right.string | Study partner word of right stimulus |
| resp.num | Numeric code of the recalled item (free recall) |
| study.partner.resp.num | Numeric code of recalled study partner |
| study.partner.resp.string | Word of recalled study partner |
| recall.type | Recall classification: Correct / Prior-list intrusion / Extralist intrusion |
| recall.list | Source list number for free recall |
| condition_block | Original condition+block label string |

Source data is trial-level across all five memory tasks, with study and test phases preserved. Task mapping to the paper's task labels: task_id 0=Associative recognition, 1=Cued recall, 2=Free recall, 3=Lexical decision, 4=Single (item) recognition.

The paper (p. 4) reports 462 participants, 72 of whom did not finish the session, and excludes 9 participants who always gave the same response in one of the three binary-choice tasks, analysing 453. All 462 are kept here. The criterion of the OSF model script (hit rate 0 or false-alarm rate 1 in lexical decision, single recognition or associative recognition) marks participant_id 47, 50, 134, 206, 274, 279, 357, 415, 424.

## Update (2026-08-13)
- Chronology fix: rows had been re-sorted phase-major (all `study` rows of a task, then all its `test` rows), destroying the session's interleaved study/test cycle order. Rows are now sorted chronologically per participant by (`block_source`, `phase` [study before test], `trial_in_block`), restoring the session-global block order in which the five tasks interleave.
- `trial` renumbered 0..N-1 within each (`participant_id`, `task_id`) in the restored order (165,908 of 276,754 cells changed). `block` recomputed the same way and was unchanged (0 cells). No other column touched; per-participant row multisets identical to the previous release.

CSVs fixed in place from the previous release; transform.py updated to produce the same output
from raw. The previous version remains in the repo's git history.

## Text-format conversion

The single experiment (`exp0.csv`) is fully textifiable and was transcribed in full: all five tasks (single-item recognition, associative recognition, cued recall, free recall, lexical decision) use word stimuli, so a text rendering is lossless. Each of the 15 study/test blocks is narrated in session order with its task label and study-phase association rating (1-9), plus the old/new or word/nonword judgments and typed recall words as marked responses. Nothing was skipped.

### Sample transcript

```
You are taking part in a memory experiment with five tasks: single-item recognition, associative recognition, cued recall, free recall, and lexical decision. Each task (except lexical decision) begins with a study phase in which 20 word pairs are presented one at a time, each for 2 seconds. Immediately after each pair you rate how associated the two words are on a scale from 1 to 9, by typing the number. The study phase is followed by a 45-second math distractor task, and then a memory test. Each of the five tasks is repeated three times, for 15 study/test blocks in total; the tasks appear in a different order each time.
Block 1: Associative recognition.
You study the word pair FILE GERMAN. You rate how associated the two words are (1-9): [HUMAN_RESPONSE]6[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

`exp0` got a simulator (`simulate0.py`) covering all five tasks across the 15 study/test blocks; the round-trip check passed (transcribing the generated DataFrame with the repo's `build_jsonl.py` reproduces the simulator's prompts byte-identically). No experiment was skipped. ASSUMPTIONs worth noting: free recall is modelled as one row per studied word (extra-list intrusions omitted); stimuli are sampled from the word pool recovered from `exp0.csv`; non-narratable columns (`rt`, item-property and post-hoc classification columns) are dropped.

Fixed 2026-09-15: the free-recall call asked the agent before the 'You type [HUMAN_RESPONSE]' cue; the cue now precedes the call (a miss still rolls the cue back, so a call without a marker is expected there).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: none; blocked before modeling.
Reproduced: none.
Not reproduced: none.
Numeric mismatch: none.
Partial validation: none.
Indeterminate: The paper's sole modeling result is a single hierarchical Bayesian joint measurement model (Wiener/diffusion likelihood for the three binary-choice tasks plus multinomial-logistic likelihoods for cued/free recall, with item and participant random effects, LKJ correlation priors, and posterior correlation-matrix PCA). The headline outputs (individual- and item-level correlation structure; 4-factor PCA solutions; 70%/83% variance) exist only after the full joint hierarchical fit with item parameters shared across participants and MCMC posterior sampling.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`exp0` got a runnable static jsPsych v8 experiment under `experiments/exp0/`, reproducing the design and on-screen language of `simulate0.py`. The headless round trip passed: a simulated random participant produced a 600-row CSV whose column names, dtypes and codings match `exp0.csv` (0-indexed `trial` restarts per `(participant, task)`; task counts 0:120, 1:120, 2:180, 3:60, 4:120; `rt` NaN only on free-recall Miss rows). No experiment was skipped. ASSUMPTIONs: browser-only pacing (2 s per study pair, 45 s digit distractor) and layout are cosmetic defaults; free recall is one row per studied word with extra-list intrusions dropped (per `simulate0.py`); the item-property / numeric-code / study-position / study-partner columns cannot be produced by a browser and are omitted (see `experiments/README.md`).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 5, minor 9; fixed 9, open 2).

Checked: paper (https://doi.org/10.1037/xge0000407, PDF), original data (https://osf.io/dd8kp/: Data/all_data_studytest.csv, Stimuli/item_properties.csv, Model scripts), exp0, transform re-run (byte-identical to exp0.csv), transcripts (rebuilt byte-identically from build_jsonl.py; marked-token sequence matches the CSV for 462/462 participants), simulator (runs; build_jsonl.py round trip identical), modeling section and tag (no model.py; section and cognitive-modeling:needs-review agree), analysis (3/3 effects reproduce), logs. Skipped: none.

Fixed:
- README column table said participant_id runs 2..464; the source `subject` column and exp0.csv run 1..462.
- README described old.left/right as an age-of-acquisition rating; the values equal OLD20 (orthographic Levenshtein distance 20) in the OSF item_properties.csv for all 924 words. Description corrected.
- README described cv.left/right as a concreteness rating; the values are integer counts (0-500, no relation to the Concr column, r = -0.01) that the OSF load_word_properties.r pairs with TASA context variability. Description corrected; freq.left/right clarified as the TASA frequency (not HAL, r = 0.03).
- README described `response` as 0/1 new/old at test and a keypress code at study; study rows hold the 1-9 association rating and recall test rows hold 0/1 = word produced (Hit/FA = 1, Miss = 0) with the typed word in resp.string. Description corrected; rt note added (study rows carry the fixed 2000 ms presentation).
- README note added: the paper (p. 4) excludes 9 participants who always gave the same response in a binary task (453 analysed); all 462 are kept, and the OSF model-script criterion marks participant_id 47, 50, 134, 206, 274, 279, 357, 415, 424.
- README title line set to `# cox_2018_information`; Modeling reproduction section: `Run:` moved to its own line, `Partial validation: (omit)` set to `none`.
- build_jsonl.py and simulate0.py: cued-recall instruction said `type DON'T KNOW`; the paper (p. 6) says `click DON'T REMEMBER`, and 141 rows carry typed `don't remember` variants. transcripts0.jsonl rebuilt.
- build_jsonl.py: 219 free-recall rows with a typed entry scored Miss (rt present, e.g. `fgh`) were narrated as `You do not recall FGH.`; they are now marked typed responses. Unrecalled-word rows (no rt) unchanged. transcripts0.jsonl rebuilt (+219 marked tokens); simulator round trip still identical.
- logs/auto-exp-sim.sessions.json: two deletion patches of castrorodrigues_2022_explicit files (from a reused work dir) removed from the session summary.

Open:
- minor (check_repo reports major): marked-response count differs from the CSV row count (participant 1: 434 marked vs 585 rows). The unmarked rows are the free-recall Miss rows (one per unrecalled studied word, no rt, response = 0) and cued-recall null responses (no typed word); the marked sequence (ratings, Y/N, typed words) matches the CSV in order for 462/462 participants, so no claim is wrong.
- minor: transcript wording says `by typing the number` and `press Y/N`; the paper (pp. 5-6) has participants click numbered boxes, YES/NO boxes, or mouse buttons. Modality wording only; tokens unchanged.

Run: claude-fable-5-1, 2026-09-10
