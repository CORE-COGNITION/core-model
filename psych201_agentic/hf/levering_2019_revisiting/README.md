---
tags:
- paradigm:category-learning
- cognitive-modeling:pass
- psych-101
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---

# levering_2019_revisiting

- Paper: https://doi.org/10.3758/s13421-019-00972-y
- Data source: https://osf.io/x3gqe/
- PDF: https://link.springer.com/content/pdf/10.3758/s13421-019-00972-y.pdf
- Full text: https://link.springer.com/article/10.3758/s13421-019-00972-y
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Levering, K. R., Conaway, N., & Kurtz, K. J. (2020). Revisiting the linear separability constraint: New implications for theories of human category learning. Memory & Cognition, 48(3), 335-347. https://doi.org/10.3758/s13421-019-00972-y

## Experiment summary
One between-subjects category-learning experiment (N = 270; 144 LS, 126 NLS participants) comparing a linearly separable (LS) and a nonlinearly separable (NLS) category structure, a conceptual replication of Medin & Schwanenflugel (1981). In each session, 25 training blocks present randomly selected exemplars requiring an Alpha/Beta category-membership classification with accuracy feedback and RT per trial, followed by a single-exemplar typicality-rating test (classify then rate 1–9) and a paired-exemplar typicality-choice test. The authors test whether NLS structures are as easy to learn as LS structures and compare human learning curves to ALCOVE, SUSTAIN, PROTO-ALCOVE, and DIVA cognitive models, finding NLS categories easier to learn and prototype (PROTO-ALCOVE) accounts incompatible with the observed data.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Lab subject code per participant: `"{group}_{subject}"` where the second part is the original subject number from the raw `lsnls2-*` filenames (a `b` suffix disambiguates a second participant who shared a subject number, e.g. `34b`). `group` is 1 (LS) or 2 (NLS). 270 participants total (144 LS, 126 NLS). |
| group | Raw group field from the source data rows: 1 = LS (linearly separable) category structure, 2 = NLS (nonlinearly separable). |
| condition | Between-subject condition derived from `group`: `ls` or `nls`. |
| phase | Phase within the session as labeled in the source: `training` (25 blocks x 6 exemplars, feedback given), `singletypicality` (test: classify each of the 8 exemplars then rate its typicality 1-9), `pairedtypicality` (choose which of two exemplars is more typical). |
| response_type | Which judgement the row records: `classification` (Alpha/Beta), `typicality_rating` (1-9), or `typicality_choice` (which of two exemplars). |
| trial | 0-indexed response counter, 0..N-1 within each participant (does not restart across phases). |
| block | 0-indexed group label: training block (0..24) for `phase=training`; paper-trial index (0..7) for `singletypicality` (its 2 responses share one block value); paper-trial index (0..5) for `pairedtypicality`. |
| response | The participant's response: 0/1 category classification (0=Alpha, 1=Beta), raw 1-9 typicality rating, or 0/1 paired choice (0=first-listed exemplar, 1=second-listed). |
| response_label | Verbatim category label (`Alpha`/`Beta`) of the participant's classification response; empty on rating/choice rows. |
| rt | Reaction time in **milliseconds** (source recorded seconds; multiplied by 1000). For `singletypicality` there is one row with the classification RT and one with the rating RT. |
| correct | 0/1 whether the classification was correct (training rows from the source's own correctness column; singletypicality classification rows derived by comparing the response to the per-participant trained category map). Empty on rows without a ground truth (ratings, paired choices) and for the 2 untrained test items whose category is unknown. |
| stimulus | Picture filename of the exemplar shown (`*.jpg`), e.g. `1-111.jpg`; one of 8 physical pictures shared by all participants. The three digits encode the physical stimulus, not the logical `feature1`-`feature3` values (the two coincide for only 14 of 270 participants). |
| exemplar_id | Logical exemplar index recorded in the source: the binary code of (`feature1`, `feature2`, `feature3`), 1 = `111` ... 8 = `222`, constant across participants; which physical picture (`stimulus`) it maps to is counterbalanced per participant. |
| feature1 | First logical feature value (1/2) of the shown exemplar, as recorded. |
| feature2 | Second logical feature value (1/2) of the shown exemplar, as recorded. |
| feature3 | Third logical feature value (1/2) of the shown exemplar, as recorded. |
| correct_category | Verbatim `Alpha`/`Beta` label of the exemplar's category: the source's own label on training rows; for `singletypicality` rows it is carried over from that participant's training map (empty for the two untrained exemplars). |
| trained | 1/0 whether the exemplar was among the six this participant trained on (only set on `singletypicality` rows). |
| stimulus1 | Picture filename of the first exemplar presented in a paired typicality trial (only `pairedtypicality` rows). |
| exemplar1_id | Logical exemplar index of the first presented exemplar (paired rows only). |
| exemplar1_feature1 | First feature value (1/2) of the first exemplar (paired rows only). |
| exemplar1_feature2 | Second feature value (1/2) of the first exemplar (paired rows only). |
| exemplar1_feature3 | Third feature value (1/2) of the first exemplar (paired rows only). |
| stimulus2 | Picture filename of the second exemplar presented in a paired typicality trial (paired rows only). |
| exemplar2_id | Logical exemplar index of the second presented exemplar (paired rows only). |
| exemplar2_feature1 | First feature value (1/2) of the second exemplar (paired rows only). |
| exemplar2_feature2 | Second feature value (1/2) of the second exemplar (paired rows only). |
| exemplar2_feature3 | Third feature value (1/2) of the second exemplar (paired rows only). |
| response_exemplar | Verbatim logical exemplar index the participant chose in a paired typicality trial (`exemplar1_id` or `exemplar2_id`); paired rows only. |
| cbal_a | First counterbalancing value from the source's per-participant header line; meaning not documented in the source, preserved verbatim. |
| cbal_b | Second counterbalancing value from the source's per-participant header line; preserved verbatim. |
| cbal_c | Third counterbalancing value from the source's per-participant header line; preserved verbatim. |
| cbal_d | Fourth counterbalancing value from the source's per-participant header line; meaning not documented in the source, preserved verbatim. |
| dim_a | First dimension of the feature-to-physical counterbalancing order (e.g. `Shape`), from the source header line. |
| dim_b | Second dimension of the feature order (e.g. `Color`), from the source header line. |
| dim_c | Third dimension of the feature order (e.g. `Size`), from the source header line. |

Raw per-participant files (`lsnls2-*.csv` from LS/NLS subject zips) each hold one participant's whole session; participant_id `{group}_{subject}` merges the 144 LS + 126 NLS rows into a single long format. Two participants shared subject numbers and are disambiguated with a `b` suffix, matching the paper's totals. RT was converted from source seconds to milliseconds per schema convention.

## Text-format conversion

Transcribed `exp0.csv` (the only experiment) into `transcripts0.jsonl` (270 participants). The category-learning task is textifiable: exemplars vary on three nameable binary features (Shape, Color/shading, Size) and participants must learn the Alpha/Beta mapping from accuracy feedback, which text preserves. The single- and paired-exemplar typicality tests are likewise nameable. Note that the physical value labels (e.g. whether Shape 1 is square or triangle) were counterbalanced and are not recoverable, so feature values are rendered as 1/2. No experiments skipped.

Sample transcript (one participant, up to the first response):

```
You will learn to classify geometric shapes into two categories, Alpha and Beta. Each shape has three features: Shape, Color, and Size, each taking value 1 or 2. On each trial, a shape appears and you decide which category it belongs to: press A for Alpha or B for Beta. After each answer you are told whether you were correct. You train over 25 blocks, each covering all six training shapes once.
You see a shape with Shape 2, Color 1, Size 1. You decide it belongs to [HUMAN_RESPONSE]A[/HUMAN_RESPONSE]. …
```

Fixed 2026-09-15: the paired typicality-choice line stated the chosen shape ('the first/second') before the response marker; the marker now comes first, transcripts rebuilt, simulator mirrored.

Run: deepseek/deepseek-v4-flash-0731, 2026-08-24

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: ALCOVE (exemplar reference points) and PROTO-ALCOVE (category-prototype reference points), each grid-searched over (c, lambda_w, lambda_a, phi) to fit the aggregate per-block human learning curves for the LS and NLS structures; the check metric is the best-fit predicted NLS advantage (mean NLS acc - mean LS acc).
Reproduced: nls_advantage_exemplar_vs_prototype (best-fit ALCOVE predicts an NLS advantage, best-fit PROTO-ALCOVE does not).
Not reproduced: none.
Numeric mismatch: reproduced ALCOVE NLS advantage +0.052 and PROTO-ALCOVE -0.055, matching the paper's qualitative claim that the exemplar model captures the NLS advantage while the prototype model does not. The paper additionally states PROTO-ALCOVE never predicts an NLS advantage under any parameterization; in our grid ~40% of PROTO-ALCOVE parameterizations predicted a small NLS advantage (a weaker exemplar/prototype separation than the paper's Fig. 8), so that stronger wording does not fully reproduce.
Partial validation: N=270 (full sample).
Indeterminate: DIVA is a backpropagation autoencoder (a neural-network cognitive model) and was not implemented; SUSTAIN is a corroborating model and not the basis of the checked result. The checked exemplar-vs-prototype result is non-neural and independent of both.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Built a static online experiment at `experiments/exp0/` (single experiment; no `simulateN.py` existed, so it was ported from the paper and `exp0.csv`). It reproduces the task (25 training blocks × 6 exemplars with feedback, then an 8-exemplar classify+rate-1-9 single typicality test, then a 6-pair typicality choice test, for both the LS and NLS structures) and saves the session as a CSV in `exp0.csv`'s exact 36-column schema. The headless `?mode=simulate` round trip was run for both LS and NLS and passes (172 rows/participant, schema, codings, `rt` from the browser). Assumption surfaced: the source counterbalances physical features onto the logical structure and the physical labels are not recoverable, so this experiment assigns a per-participant counterbalance (Shape/Color/Size order + value flip, recorded in `dim_a..c`/`cbal_a..d`) and renders the geometric shapes as inline SVG; the repo's text transcript says "six blocks" but the paper and data specify 25, so the on-screen instruction says 25 blocks.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

- `simulate0.py`: exp0 (the only experiment) got a text simulator that reproduces a full session — 25 training blocks of Alpha/Beta classification with feedback, the 8-exemplar classify-and-rate (1–9) single typicality test, and the 6-pair typicality-choice test — for both the LS and NLS category structures (Medin & Schwanenflugel's structures recovered from the data). The round-trip check against `transcripts0.jsonl` passes byte-identical. No experiments skipped.
- ASSUMPTIONS: the paired typicality-choice phase is present in the data but not described in the paper's Method, so six random distinct shape pairs per participant are used; group is drawn 50/50 (the paper randomly assigned 144 LS / 126 NLS); physical counterbalancing codes (dim_a/b/c order, cbal_a-d) are drawn at random since they are not textually recoverable.
Fixed 2026-09-15: simulate0.py mirrors the rebuilt transcripts (check_calls.py passes).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 1, major 2, minor 9; fixed 9, open 3).

Checked: paper (https://doi.org/10.3758/s13421-019-00972-y), original data (https://osf.io/x3gqe/: LS Subjects.zip, NLS Subjects.zip, both JASP sheets), exp0, transform re-run, transcripts, simulators, modeling, analysis, logs. Skipped: none.

Fixed:
- critical: transform.py keyed the per-participant training map by the source subject number; raw files lsnls2-34-1.csv and lsnls2-34b-1.csv both carry subject 34 with different counterbalancing, so participant 1_34 got 34b's map. Eight singletypicality rows of 1_34 (trials 152-165) had wrong trained / correct_category / correct. Map now keyed by file; exp0.csv regenerated (only those 8 rows changed). LS test-phase accuracy is now .838, matching the paper (p. 5) and the source's JASP sheet.
- major: transcript instructions said 'You train over six blocks'; the paper (p. 5) and the CSV (blocks 0-24) have 25. build_jsonl.py and simulate0.py corrected, transcripts0.jsonl rebuilt, README sample transcript updated.
- major: 251/270 transcripts used a typicality-rating token (2-8) that never appeared in the text before it. The test instruction in build_jsonl.py and simulate0.py now lists 1-9; transcripts rebuilt, simulator round trip byte-identical.
- minor: README Columns heading '### exp0' -> '#### exp0'.
- minor: README named the raw files lsnls2-*.txt; the OSF zips ship lsnls2-*.csv.
- minor: README said cbal_d differs between the two runs of subject 34/22; in the source cbal_d is equal in both pairs (34: 14,0,1,0 vs 34b: 10,1,0,0; 22 and 22b identical). Parenthetical removed.
- minor: README said the stimulus filename digits encode the feature values; they encode one of 8 physical pictures shared by all participants, and equal feature1-3 for only 14/270 participants. Description corrected.
- minor: README described exemplar_id as a per-participant permutation; it is the fixed binary code of feature1-3 (111 -> 1 ... 222 -> 8). Description corrected.
- minor: model.py docstring described bounded L-BFGS / jaxopt fitting while the code grid-searches PARAM_GRID (as the README states). Docstring corrected; results unchanged (ALCOVE +0.052, PROTO-ALCOVE -0.055, reproduced).

Open:
- minor: check_repo.py reports 270/270 transcripts 'marked tokens do not map one-to-one onto the CSV response sequence'. The checker orders rows by block (which restarts per phase) and requires one token-to-value bijection across response types, but classification B -> 1 and rating 1 -> 1 share the CSV value 1. Verified per response type in trial order: every transcript maps exactly. No change (schema-conforming coding).
- minor: 115 training rows and 3 paired-typicality rows have rt below 50 ms (minimum 0.186 ms). The source records these values (e.g. lsnls2-242-1.csv, trial 43: 0.000230 s); kept verbatim.
- minor: the paper (p. 5) reports t(264) for the test-phase LS/NLS comparison, implying 266 participants; the source ships complete test data for all 270 and its JASP sheets (144 + 126 rows) have no missing test values. The paper's means (.838 / .923) match the CSV.

Run: claude-fable-5-1, 2026-09-10
