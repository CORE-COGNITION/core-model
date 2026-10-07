---
tags:
- paradigm:bandit
- cognitive-modeling:pass
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:pass
---
# christian_2026_resolving

- Paper: https://doi.org/10.1073/pnas.2509612123
- Data source: https://osf.io/da5hw/ (OSF project "Feynman Restaurant Study", 10.17605/OSF.IO/DA5HW)
- Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC13250586/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Christian, B., Russek, E. M., & Griffiths, T. L. (2026). Resolving Feynman's restaurant problem reveals optimal solutions and human strategies. Proceedings of the National Academy of Sciences, 123(23), e2509612123. https://doi.org/10.1073/pnas.2509612123

## Experiment summary
One preregistered online experiment (N=2520) on Feynman's restaurant problem, an optimal-stopping task, with one sequence of nights per participant (horizon 7, 14, or 28). On each night a participant chose to explore a new restaurant or exploit the best one seen so far, with hidden restaurant quality values drawn from one of four distributions (uniform, exponential, power law, triangular) varied between subjects. Responses are discrete choices logged per night (with best-known value and reward), and the paper tests whether humans use stopping thresholds that decline linearly with nights remaining, fitting linear-threshold and hierarchical Bayesian models plus reinforcement-learning baselines.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV, as string ("0".."2519"). |
| trial | 0..N within each participant_id = Night (0-indexed night of the sequence). |
| response | 0=Explore (visited a new restaurant), 1=Exploit (returned to the best seen so far), 2=Mistake (returned to a seen-but-not-best restaurant, excluded from paper's main analysis). |
| total_nights | 7, 14, or 28; total number of nights (restaurant visits) in the participant's sequence. |
| nights_remaining | Number of nights left including the current one (T - Night): equals total_nights on the first night and 1 on the last night. |
| action | Original raw category string from source ("Explore"/"Exploit"/"Mistake"); verbatim copy of the categorize-the-choice label. |
| best_known | Best restaurant value seen so far (b) before this night's choice; NaN on the first night (none seen yet). |
| reward | Reward/score obtained on this night from the visited restaurant (raw quality value). |
| clamp | Clamping condition (0-6); new-restaurant values were clamped to [0, tn) for the first (clamp/7) fraction of the sequence. |
| quiz_failures | Number of quiz attempt failures before the participant passed the comprehension quiz. |
| condition | Rating distribution the participant's hidden values were drawn from: triangular/uniform/exponential/power_law. |
| valid | 1 normally; 0 when response==2 (Mistake), which the paper excludes from its main analysis. |

The single experiment maps to the paper's "Experiment 1" (preregistered online study). Mistake trials (response==2) are retained but flagged valid=0, matching the paper's decision to exclude them from the main (explore/exploit) analysis. Best-known value on the first night has no prior and is empty.

## Text-format conversion

exp0 is transcribed to `transcripts0.jsonl` (2,520 transcripts). All rows, including Mistake (valid=0) trials, are retained. The response letter set (A/B/C mapped to Explore/Exploit/Mistake) is randomized per participant and spelled out in each transcript's instructions.

Sample transcript (start up to the first marked response):

```
You are about to spend 7 nights in a new city. Restaurants in the city vary in quality: you cannot know a restaurant's quality until you visit it, and once you visit it its quality never changes. Quality scores are distributed randomly with a mean of 50. Before your trip you saw 84 sample scores from this city to get a sense of how scores are distributed. Your goal is to maximize the total score of the restaurants you visit across all your nights, and you will earn a bonus proportional to your total score.
On each of the 7 nights you choose a restaurant. On every night respond with a single letter: press B to visit a NEW restaurant you have not been to before, press C to return to the BEST restaurant you have found so far, or press A to return to some other restaurant you have already visited.
Night 1 of 7, 7 night(s) remaining. You have not visited any restaurant yet. You press [HUMAN_RESPONSE]B[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction

Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: pooled-MLE logistic decision-threshold models fit on all scored trials (valid=1 with a non-missing best_known; N=37,771), compared on BIC exactly as the paper does. The paper's Eq. 5 logistic P(exploit)=1/(1+exp(-beta*(b-t))) is fit for: the optimal closed-form threshold (Eqs. 1-4, only beta free), optimal+intercept, and the linear threshold models t=a+m*x over {nights remaining n, proportion n/T, nights elapsed T-n} with slope/intercept shared or varying over total-nights x distribution conditions; plus the best linear model augmented with the exponentially decaying early-exploration bonus (Eqs. 6-7). Because beta and a/m enter as a product (non-convex, degenerate beta->0 basin), each model is fit in the convex linear-logistic parameterization (logit = w_b*b - c - mtilde*x; beta=w_b, a=c/beta, m=mtilde/beta) that spans the identical likelihood surface; 8 multi-start jaxopt L-BFGS runs are jit-compiled and vmapped over restarts, all converging to the same optimum.
Reproduced: best_linear_model; distribution_intercepts; early_exploration_bonus.
Not reproduced: none.
Numeric note: the BIC comparison deltas are exactly twice the paper's (slope-varies deltaBIC 52.4 here vs 26.2 reported; intercept-T-only deltaBIC 227.5 vs 113.7 reported; bonus deltaBIC 159.3 vs 79.7 reported) because the paper's OSF archive (`model_comparison_summary.csv`) scores BIC as NLL + (k/2) ln N, half of the conventional 2 NLL + k ln N used here; the fitted negative log-likelihoods match the archive to 0.01 (best linear model 20364.52, N=37,771). Fitted distribution intercepts order Exponential, PowerLaw > Uniform > Triangular (means -11.4, 1.2, 13.4, 17.0) and decrease across total-nights 7/14/28 (33.6, 6.8, -25.2), matching the paper's Fig. 2D and equal to the archive's fitted parameters (`linear_proportion_model_All_Subs_Included_Mistakes_Removed.csv`) to 0.1.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Online experiment

`experiments/exp0/` is a static jsPsych v8 port of Experiment 1 (Feynman's restaurant problem), built from the simulator and reproducing the task and its verbatim wording. The headless `?mode=simulate` round trip passed: the saved CSV matches `exp0.csv`'s schema exactly (columns, codings, 0-indexed `trial`, `response` by action, `valid=0` on Mistake), and a uniform-random participant is statistically indistinguishable from `simulate0.py`'s random-agent output (horizons/conditions/clamps uniform, quiz_failures and reward distributions match). ASSUMPTIONS surfaced in `experiments/exp0/index.html`: the A/B/C letter keys are assigned per participant (only valid actions offered) and are cosmetic — `response` is coded by action, not letter; on a Mistake the participant returns to a random seen-but-not-best restaurant (the source records only the delivered reward); feedback ~1500 ms / inter-night gap ~500 ms and the button layout/labels are cosmetic browser-only defaults. No experiments were skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

exp0 got a text simulator (`simulate0.py`) whose output is format-identical to `transcripts0.jsonl` (round-trip check through `build_jsonl.py` passes byte-for-byte). Restaurant values are drawn from the paper's four rescaled distributions, with new-restaurant values truncated to the optimal-threshold window `[0, tn)` during each participant's clamped fraction. ASSUMPTIONS: values are rounded to integers; `quiz_failures` is sampled from the empirical distribution in `exp0.csv`; invalid choices (Exploit/Mistake with no eligible seen restaurant) are excluded from the agent's option set; the paper's noted exponential clamping-bound numerical error is not reproduced. No experiments were skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Verification

Verdict: pass (critical 0, major 3, minor 4; fixed 6, open 1).

Checked: paper (https://doi.org/10.1073/pnas.2509612123; PMC full text, the PDF endpoints returned HTML), original data (https://osf.io/da5hw/: FeynmanStudyData.csv, FeynmanStudySamplesObserved.csv, feynman-reproducibility.zip; the OSF CSV and the archive copy are identical in content), exp0, transform re-run (byte-identical), transcripts (rebuilt byte-identical), simulators (simulate0.py runs; round trip through build_jsonl.py 12/12 byte-identical), modeling (model.py, 20 min: best_linear_model, distribution_intercepts, early_exploration_bonus all reproduce; negative log-likelihoods match the OSF model_comparison_summary.csv to 0.01), analysis (analysis.py: all 3 effects reproduce), logs. Paper facts that match the data, README, transcripts and simulator: N=2,520 = 4 distributions x 3 horizons x 7 clamp conditions x 30; 84 sample values; distributions rescaled to mean 50; bonus proportional to total score; clamp for the first clamp/7 of the nights (clamped Explore rewards fall below the optimal threshold in 100% of uniform, triangular and power-law trials and 93.8% of exponential trials, the numerical error the paper reports); Mistake choices excluded from the main analysis; preregistration https://osf.io/9e5g7. Skipped: none.

Fixed:
- README described nights_remaining as the nights left after the current one (T-1-Night); exp0.csv holds T-Night (7 on the first of 7 nights, 1 on the last), which is the paper's n and what the transcripts narrate. Column description corrected.
- exp0.csv named the per-night payoff column `Reward`; schema.md names that column `reward` and lists duplicate names as an anti-pattern. transform.py now renames it; exp0.csv regenerated (header only, body byte-identical); build_jsonl.py and simulate0.py read/write `reward`; README column table updated; transcripts0.jsonl rebuilt byte-identical; simulator round trip 12/12 byte-identical.
- logs/auto-exp-transcribe.sessions.json carried two project-workspace diff snapshots unrelated to this dataset (another paper's extracted text, 6,531 lines, and modeling_pending.txt, a 74-name dataset queue), which check_repo flagged as cross-run contamination. The two diff entries were removed; the session messages are unchanged.
- README experiment summary wrote N=2,520, which check_repo parsed as N=2; now N=2520 (the CSV has 2,520 participants).
- README columns heading `### exp0` changed to the template's `#### exp0`.
- README modeling note called the 2x BIC deltas a rough numeric mismatch. The OSF model_comparison_summary.csv scores BIC as NLL + (k/2) ln N, so the paper's deltas (26.2, 113.7, 79.7) are exactly half of model.py's conventional 2 NLL + k ln N values (52.4, 227.5, 159.3); model.py's NLLs match the archive to 0.01 and its intercept means equal the archive's fitted parameters. The note now states this.

Open:
- minor: the paper (Materials and Methods) reports 2,530 submissions with data beyond 30 per condition ignored; the OSF FeynmanStudyData.csv ships exactly 2,520 participants (30 per cell), so the 10 surplus submissions are not in the source. The data is faithful to its source.

Run: claude-fable-5-1, 2026-09-09
