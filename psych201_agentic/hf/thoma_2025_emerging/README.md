---
tags:
- paradigm:bandit
- cognitive-modeling:pass
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---
# thoma_2025_emerging

- Paper: https://doi.org/10.1037/xge0001747
- Data source: https://osf.io/47fa9/
- PDF: https://pure.mpg.de/rest/items/item_3639596_13/component/file_3645047/content
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation

Thoma, A. I., Newell, B. R., & Schulze, C. (2025). Emerging adaptivity in probability learning: How young minds and the environment interact. Journal of Experimental Psychology: General, 154(6), 1523-1544. https://doi.org/10.1037/xge0001747

## Experiment summary

A single child-friendly probability-learning (two-option bandit) experiment with N = 483 participants across four age bands (3-4, 6-7, 9-11 years, adults) making 100 binary choices (5 blocks of 20 trials) between two probabilistically rewarded options. Each participant was assigned to one of three between-subjects statistical environments (static_high, static_random, ecologically-plausible dynamic). Trial-level rows record the chosen option, whether a reward was delivered, the scheduled/target (correct) location, and post-choice numeric estimates of each option's reward rate. The study asks when adaptive (exploitative vs exploratory) repeated-choice behavior emerges in development, and hierarchical RL + perseveration models (Stan) provide converging evidence for perseveration in 3-4-year-olds and diversification from age 6 onward.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original random participant ID from source CSV (int, kept as string) |
| condition | Between-subjects statistical environment: static_high, static_random, or ecol_dyn (source cond) |
| age_group | Age band: 3-4 years, 6-7 years, 9-11 years, adult |
| age | Participant age in years (decimal; months as fraction of year); NaN for 3 participants (392, 685, 921) |
| gender | lowercased: f = female, m = male (mapped from source female/male) |
| education | Parent-reported schooling level, free text (German; "Nicht zutreffend" = not applicable) |
| grade | School grade, int; 0 = none indicated; column has mixed types in source |
| trial | 0..99 within participant (source trial 1-100 minus 1) |
| block | 0..4, 5 blocks of 20 trials (source block 1-5 minus 1); within-task subdivision, not a reset |
| majority_location | Location of the high-probability option, 0 = left, 1 = right; static_random has no high-probability option and the source codes 1 on every row |
| scheduled_left | Whether a reward was scheduled to appear at the left, 0/1 |
| scheduled_right | Whether a reward was scheduled to appear at the right, 0/1 |
| target_left | Whether a reward was available to collect at the left, 0/1 |
| target_right | Whether a reward was available to collect at the right, 0/1 |
| keypress | String form of the choice: left/right |
| response | The chosen option (source button_pressed): 0 = left, 1 = right |
| reward | Whether the participant received a reward on the trial (source correct): 0/1 delivered magnitude |
| ml_correct | Whether the participant selected the high-probability (majority-location) option, 0/1 |
| estimate_ml | Post-choice identification of the high-probability option, 0 = left, 1 = right; repeated on every row of the participant |
| estimate_left | Numeric estimate of the number of animals (rewards) at the left option, 0-100 (source codebook; the two estimates sum to 100); repeated on every participant row |
| estimate_right | Numeric estimate of the number of animals (rewards) at the right option, 0-100; repeated on every participant row (NaN for participant 579) |

`exp0` maps to the paper's single "Experiment 1": a 2-option probability-learning (bandit) task with 100 trials across 5 blocks, three between-subjects statistical environments, and four age groups.

## Text-format conversion

The experiment `exp0.csv` was transcribed (a single two-option probabilistic-reward task in a child-friendly zoo-animal cover story). Textifiable: participants repeatedly chose between two probabilistically-rewarded houses and saw the full feedback of both options, which preserves the choice-and-learning operation. No experiments were skipped. `transcripts0.jsonl` holds one natural-language transcript per participant (483 total; all 100 choices per participant are free responses).

Sample transcript (participant 301, condition `static_high`):

```text
You are helping find zoo animals that have escaped and are hiding behind two houses. The experimenter shows you 50 escaped animals on a sheet and explains that you should find as many as possible by guessing which house an animal is hiding behind. There are two identical houses, a left house and a right house. On each trial, press B to choose the left house or press A to choose the right house. After each choice the houses turn transparent so you can see exactly where animals are hiding, and a checkmark or a cross shows whether your choice was correct. Every correct choice fills one tenth of a blue circle in the corner; each full circle earns you a token.

Block 1 begins.
You tap [HUMAN_RESPONSE]B[/HUMAN_RESPONSE].
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

`exp0/` got a runnable static jsPsych v8 experiment (child-friendly two-option
probability-learning task). The repo has no `simulate0.py`, so the design and
wording were built from the paper and `exp0.csv` (with the transcript narrative for
on-screen text). The headless `?mode=simulate` round trip passed: its CSV matches
`exp0.csv`'s 21-column schema with 100 rows, `trial` 0–99, `block` 0–4, and 0/1
`response`/`reward`; no experiments skipped. Browser-only assumptions are listed in
`experiments/README.md` (cosmetics: house rendering, block transitions, blue-circle
meter, Continue pacing, demographic widgets; `estimate_*`/demographics collected
on-screen and repeated per row).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Modeling reproduction

Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: gradual-perseverance RL (learning rate, inverse temperature, decay rate, perseverance), simple RL, perseverance-only, and impulsive-perseverance RL, by per-participant bounded L-BFGS maximum likelihood on the static_high and ecol_dyn conditions (static_random excluded, as in the paper). The paper's hierarchical-Bayesian ELPD-LOO model comparison was approximated by summed per-participant BIC; the same model likelihood, parameterization, and comparison logic are kept. All fits converged (frac_converged = 1.00).
Reproduced: rl_perseverance_beats_learning, adult_adaptive_perseverance, young_child_perseveration.
Not reproduced: none.
Numeric mismatch: under our per-participant BIC, impulsive-perseverance (35405) is marginally ahead of gradual-perseverance (35996), though both clearly beat simple RL (40732) and perseverance-only (39359); the paper reported gradual numerically best (with no credible difference vs impulsive in 3 of 8 age-condition cells). Adult perseverance means: static_high = +1.43 (paper +1.30), ecol_dyn = -1.97 (paper -0.83); adaptive difference 3.40, p < 0.01.
Partial validation: none.
Indeterminate: none.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

`simulate0.py` is a text simulator for `exp0.csv` / `transcripts0.jsonl`. It
reproduces the paper's three statistical environments (static_high 70/30,
static_random 50/50, and ecol_dyn with the reward-hold mechanism verified 100%
against the shipped `scheduled_*` → `target_*` data) in the transcript format,
and passes the round-trip check through `build_jsonl.py` (simulated transcripts
byte-identical modulo the per-participant token mapping). Assumptions (recorded
in the class docstring): scheduled rewards draw independently per trial/side;
static_random's `majority_location` is set to 1 as in the data; sampled
demographics / post-hoc `estimate_*` values are inert placeholders. No
experiments skipped.

Fixed 2026-09-15: simulate0.py drew every choice with np.random and never called the agent; it now asks the agent at the response marker (`You tap [HUMAN_RESPONSE]`), and the returned prompt is stripped like build_jsonl.py's text (check_calls.py and the round trip pass).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 3, minor 12; fixed 11, open 4).

Checked: paper (doi:10.1037/xge0001747, postprint PDF), original data (https://osf.io/47fa9/: behavioral_data.csv, codebook, Stan code), exp0, transform re-run (exp0.csv byte-identical; all 21 source columns read, 48300 rows = 483 x 100, nothing dropped), transcripts (rebuild byte-identical), simulator (simulate0.py -n 2 runs; round trip through build_jsonl.py 4/4 byte-identical), modeling (full model.py run, 2 h 47 min on one core: BIC gradual 35996, impulsive 35405, simple RL 40732, perseverance-only 39359; adult phi SH +1.43, ED -1.97, difference 3.40; all three named results reproduce; all fits converged; matches the README section), analysis (3/3 effects reproduce; static_high-ecol_dyn difference 0.067 vs paper .66-.59), logs. Sample: 483 participants equal the paper (p. 9) and Table A1 (p. 39) cell by cell; age M/SD, gender %, adult range 18-51 match p. 9; codings match the codebook; reward equals the target of the chosen side on every row; model.py likelihood, bounds, and both-option value update match hier_rl_pers_noncentered.stan. The one remaining automated log flag ('thoma_2025_emerg' in logs/auto-exp-transcribe.sessions.json) is this dataset's own name truncated inside a reasoning text, not another dataset. Skipped: none.

Fixed:
- major: the transcript instructions said 'You will complete 100 choices in five blocks of 20 trials.'; the paper (p. 11) states the procedure informed participants 'that there were many trials without revealing the total number'. Sentence removed from build_jsonl.py and simulate0.py, transcripts0.jsonl regenerated (483), README sample transcript updated; rebuild and simulator round trip byte-identical.
- major: logs/auto-exp-modeling.sessions.json carried 12 project-tree diff entries of other runs in its first message (another dataset's work dir with the vantiel_2022_meaning README, analysis.Rmd, *.log, osf_*); emptied summary.diffs, formatting kept.
- major: logs/auto-exp-transcribe.sessions.json carried 4 such entries (modeling_pending.txt listing 74 other datasets, another run's paper.txt); emptied summary.diffs.
- minor: README columns heading '### exp0' -> '#### exp0'.
- minor: README experiment summary now states N = 483.
- minor: README estimate_left/estimate_right described as '0-100 percent'; the codebook and paper (p. 11) define them as the estimated number of animals (0-100; the two sum to 100 for all 482 complete participants).
- minor: README said estimate_right is 'NaN on some first rows'; it is NaN on all 100 rows of participant 579 only.
- minor: README age row now notes NaN for participants 392, 685, 921.
- minor: README majority_location row now notes that static_random has no high-probability option and the source codes 1 on every row (161/161).
- minor: README modeling section said 'L-BFGS MAP'; model.py fits bounded maximum likelihood without a prior.
- minor: model.py docstrings cited 'Throws et al.' (5x) -> 'Thoma et al.'; docstrings only, script re-run.

Open:
- minor: the paper (p. 9) excludes 19 children who terminated prematurely; the OSF file ships only the 483 complete participants (100 trials each). Inside the source; data faithful.
- minor: the paper (p. 11) has 2 practice trials (3 in ecol_dyn) before the 100 trials; the source does not contain them.
- minor: transcripts narrate 'Block N begins.' every 20 trials (source block column); the paper (p. 13) uses trial block as an analysis factor and does not state whether block boundaries were visible. Not settled; left as is.
- minor: simulate0.py draws scheduled rewards iid per trial (documented assumption); the data has exactly 70/30 (static_high) and 50/50 (static_random) scheduled rewards per participant and 69-70 in ecol_dyn, i.e. fixed-count schedules. Format unaffected.

Run: claude-fable-5-1, 2026-09-13
