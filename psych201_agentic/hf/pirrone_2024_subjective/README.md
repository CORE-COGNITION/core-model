---
tags:
- paradigm:risky-choice
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:pass
---
# pirrone_2024_subjective

- Paper: https://osf.io/xvnjd/
- Data source: https://osf.io/xvnjd/ (folder Psyc-201_process: data_Pirrone_unpublished_utility.csv, data_Pirrone_utility_Psych-201.csv, create201data.m, README.md)
- Full text: https://osf.io/xvnjd/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Pirrone, A. (2024). Subjective utility modulates the effect of overall stimulus intensity on decision-making [Unpublished manuscript; OSF data]. https://osf.io/xvnjd/

## Experiment summary
Single experiment, N = 62 human participants (450 trials each, 27,900 trial-level rows). On each trial participants made a binary choice between two two-outcome lotteries presented side by side (the left lottery resolved to either x0 or x1, the right to either x2 or x3, selected at random) while reaction time was recorded. Key manipulations are encoded in derived columns: overall stimulus intensity/magnitude (`magnitude`, `magnitude_difference`), lottery variance (`variance_left`, `variance_difference`, `prefer_variance`), and subjective utility (`nonlinear_preference`); accuracy is scored against the lottery with the higher expected outcome (`max_ev_lottery`). The research question is whether subjective utility modulates the effect of overall stimulus intensity on decision-making. This is unpublished data (no preprint exists); the OSF project also carries the same rows reformatted into the Psych-201 schema.

## Text-format conversion

`exp0.csv` was transcribed to `transcripts0.jsonl` (62 transcripts, one per participant; each covers all 450 trials). The risky-choice task is textifiable: each trial presents two two-outcome lotteries with explicitly stated outcome values, and the participant picks the lottery they judge the better gamble. No experiment was skipped. Response format: a single letter per trial — `A` or `B`, mapped to the left/right lottery and alternated by participant-id parity (pinned in each transcript's instructions).

Sample transcript (participant 1):

```
You are choosing between pairs of lotteries. On each trial two lotteries are shown side by side; each lottery has two equally likely outcomes. Pick the lottery that seems to you like the better gamble overall. Press B to choose the left lottery or A to choose the right lottery.
You see two lotteries. The left pays either 97 or 8; the right pays either 52 or 53. You press [HUMAN_RESPONSE]A[/HUMAN_RESPONSE].
```

Run: deepseek-v4-flash, 2026-08-24

## Simulators

`simulate0.py` reproduces the risky-choice task (450 two-outcome-lottery choices per participant) with a data-driven generative stimulus process and passes the round-trip check against `build_jsonl.py`. No experiments were skipped. NOTE: the simulator follows the source coding (`response` 1 = left lottery, `max_ev_lottery` = `o1+o2 > o3+o4`, `prefer_variance` 1 = chose the higher-variance lottery) so the round trip is byte-exact.

Run: deepseek-v4-flash, 2026-08-24

## Notes

### Columns

#### exp0

Source: `raw/data_unpublished.csv` (primary). The companion `raw/data_psych201.csv` holds the same 27,900 rows reformatted for the Psych-201 schema (`participant` = id-1, `step` = trial, `x0..x3` = `o1..o4`, `target` = `best`, `time` = `rt`*1000 ms) and was dropped as a duplicate encoding with no additional information.

| column | description |
|--------|-------------|
| participant_id | Original subject number from source `id`, 1..62 (62 participants), kept as string. |
| trial | 0..449, within-participant trial number in presentation order (450 lottery choices per participant; no phases, no task resets). |
| response | Binary lottery choice (source `choice`, kept verbatim): 1 = left lottery (`o1`/`o2`), 0 = right lottery (`o3`/`o4`). The source's `accuracy_unequal` equals the share of unequal trials with `response == max_ev_lottery`, which pins this mapping. |
| rt | Reaction time in milliseconds (source `rt` was in seconds, converted x1000). |
| o1 | Outcome of the left lottery if outcome 1 is drawn (source `o1`). |
| o2 | Outcome of the left lottery if outcome 2 is drawn (source `o2`). |
| o3 | Outcome of the right lottery if outcome 1 is drawn (source `o3`). |
| o4 | Outcome of the right lottery if outcome 2 is drawn (source `o4`). |
| magnitude_difference | Difference in overall stimulus intensity / magnitude between the two lotteries (sum of left-lottery outcomes minus sum of right-lottery outcomes). |
| magnitude | Overall stimulus intensity: sum of the four outcome values of a trial. |
| variance_left | 1 if the left lottery had higher variance than the right, else 0. |
| nonlinear_preference | Per-participant derived proxy of nonlinear (subjective) utility preference, constant within a participant (float). |
| max_ev_lottery | Accuracy target (source `best`): 1 = left lottery has the higher expected outcome (`o1+o2 > o3+o4`), 0 = right lottery has the higher or an equal expected outcome. Renamed from `best` to avoid confusion with reserved `accuracy`/`correct` naming. |
| accuracy_unequal | Per-participant accuracy (share of choices matching `max_ev_lottery`) on trials where magnitudes were unequal, constant within a participant (float). |
| variance_difference | Absolute difference in outcome spread between the two lotteries: abs(abs(`o1`-`o2`) - abs(`o3`-`o4`)), always >= 0 (source column, kept verbatim). |
| prefer_variance | 1 if the participant chose the higher-variance lottery on that trial, else 0 (equals `response == variance_left`; on the 606 equal-spread trials it is 1 when the right lottery was chosen). |

No manuscript PDF exists (this is unpublished data); `paper.pdf` in the pipeline was reconstructed from the OSF README and project metadata for effect-identification purposes. Behavioral effects verified on this data: magnitude affects decision time, non-linear utility preference modulates the magnitude effect on RT, and preferences for higher-variance options increase with overall magnitude.

## Online experiment

`experiments/exp0/` ports the risky-choice task (450 two-outcome-lottery choices) as a static jsPsych v8 experiment. The headless `?mode=simulate` round trip passed: the saved CSV matches `exp0.csv` exactly (column names, dtypes, and codings) and reproduces the simulator's generative process and distributions. `rt` is filled from the browser; `nonlinear_preference` (a fitted per-participant latent) is shipped blank, as the text simulator also drops it; the letter-to-side mapping is randomly counterbalanced per participant. No experiment was skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 1, major 6, minor 4; fixed 10, open 1).

Checked: paper (no manuscript exists; the OSF project page, README and create201data.m at https://osf.io/xvnjd/ served as the paper; Crossref and OSF preprint searches on 2026-09-10 found no preprint), original data (https://osf.io/xvnjd/ folder Psyc-201_process, 4 files, 27,900 rows x 62 ids; the Psych-201 CSV is an exact re-encoding of the primary CSV), exp0, transform re-run (byte-identical), transcripts (rebuild byte-identical), simulators (smoke test, round trip byte-identical, agent-semantics check), analysis (3/3 effects reproduce), logs; modeling not applicable (no model.py, no cognitive-modeling tag). Skipped: none.

Fixed:
- critical: build_jsonl.py mapped response 0 to the left lottery, so every transcript reported the opposite choice. The source codes choice 1 = left (o1/o2): its accuracy_unequal equals the share of unequal trials with choice == best exactly, best = 1 iff o1+o2 > o3+o4, P(choice = 1 | left sum larger) = .77 vs .22 when the right sum is larger, and accuracy rises from .59 to .89 with the expected-value gap. build_jsonl.py fixed (response 1 -> left letter), transcripts0.jsonl regenerated, README sample transcript updated. The Psych-201 prompt script for this dataset (pirrone_unpublished_lottery/generate_prompts.py) uses the same 0 = left mapping.
- major: README response row said 0 = left, 1 = right; now 1 = left (o1/o2), 0 = right (o3/o4).
- major: README max_ev_lottery row said 0 = left has the higher expected outcome, 1 = right; the data have 1 iff o1+o2 > o3+o4 and 0 on all 16,822 equal trials.
- major: simulate0.py coded the left letter as response 0 and prefer_variance as 1 - chose_higher_variance; its docstring and the README Simulators note claimed the data columns were coded opposite to the prose. Now response 1 = left and prefer_variance = chose_higher_variance; smoke test, round trip (byte-identical, 3/3) and agent checks pass (an expected-value maximizer scores accuracy_unequal 1.0, a variance seeker scores prefer_variance 1.0).
- major: README variance_difference row said signed 'left minus right' variance; the column is abs(abs(o1-o2) - abs(o3-o4)), always >= 0.
- major: logs/auto-exp-sim.sessions.json carried project-root diffs (main.m, modeling_pending.txt, sub164.mat) from other runs that named 5 other datasets; the 3 diff entries were removed.
- major: typo `pipirrone_2024_subjective` in transcripts/auto-exp-sim.log (line 2425) and 7 places in logs/auto-exp-sim.sessions.json, flagged as cross-run contamination; corrected.
- minor: README Columns heading '### exp0' -> '#### exp0'.
- minor: README said the response letters are randomized per participant; build_jsonl.py alternates them by participant-id parity.
- minor: README prefer_variance row now documents the 606 equal-spread trials (there it is 1 when the right lottery was chosen).

Open:
- minor: no manuscript or preprint exists (OSF README: 'Unpublished data and no pre-print ready yet'; Crossref and OSF preprint searches on 2026-09-10 empty). Sample, instructions, trial structure and exclusions are not stated in any source and could not be verified.

Run: claude-fable-5-1, 2026-09-10
