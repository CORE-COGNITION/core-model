---
tags:
- paradigm:purchase-deferral
- psych-201
- js-experiment:pass
- text-format:pass
- simulator:pass
- verification:pass
---
# gunadi_2022_impact

- Paper: https://doi.org/10.1177/00222437211060359
- Data source: https://researchbox.org/402&PEER_REVIEW_passcode=IVIRNT (ResearchBox #402, also mirrored on https://zenodo.org/records/15032921)
- PDF: https://merit.url.edu/ws/portalfiles/portal/46734087/The_Impact_of_Historical_Price_Information_on_Purchase_Deferral.pdf
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation

Gunadi, M. P., & Evangelidis, I. (2022). The impact of historical price information on purchase deferral. Journal of Marketing Research, 59(3), 623–640. https://doi.org/10.1177/00222437211060359

## Experiment summary

Six preregistered studies (N = 5,713) test how the direction and frequency of historical price changes affect consumers' decision to defer a purchase (buy now vs. later). Study 1a (N=802) and Study 1b (N=800) use between-subjects 2(direction) x 2(frequency) flight-price scenarios where participants choose buy now vs. defer (Study 1b is a sequential-page design where deferral is recorded page by page until buy-now or the final page). Study 2 (N=802) adds a belief/agreement and a price-expectation measure to test the future-price-expectation mechanism; Study 3 (N=1506) and Study 4 (N=1506) test moderators (monotonicity and timing of the price change), each with a choice plus price-prediction measure. Study 5 (N=297, business-school students) uses actual purchase decisions for 4 products, each with a free-text rationale and follow-up ratings. The core research question is whether prior price decreases (vs. increases) and more frequent price changes raise the likelihood of deferring purchase, mediated by expectations that prices will continue to drop. Response types are binary buy-now/defer choices, rated expectations, open-ended price predictions, and free text. All headline effects (price-decrease-direction effect, frequency moderation, and the consequential-choice effect in Study 5) reproduce in the local data (all p < 1e-11).

## Notes

### Columns

#### exp0 (Study 1a)
| column | description |
|--------|-------------|
| participant_id | Assigned ID P000..P801, first-appearance order (original data has no subject ID) |
| trial | Always 0, one purchase decision per participant |
| response | Purchase decision: 0 = buy now, 1 = buy later (defer). Recoded from raw Qualtrics 1/2 (1=buy now, 2=buy later). |
| variable | Original source column holding this participant's response (DecrLow/DecrHigh/IncrLow/IncrHigh) |
| condition | 2(direction) x 2(frequency): dec_single, dec_multiple, inc_single, inc_multiple (Low=single change, High=multiple changes) |
| age | Participant age in years (float) |
| gender | f / m (raw 1=female, 2=male) |

#### exp1 (Study 1b)
| column | description |
|--------|-------------|
| participant_id | Assigned ID P000..P799 |
| trial | 0..n-1 for each participant, one per page answered (sequence continues page-by-page until buy-now or final page) |
| response | Page decision: 0 = buy now (study terminates), 1 = buy later / defer. Recoded from raw 1/2. |
| variable | Original source column for this page (DL1-4/IL1-4/DH1-4/IH1-4) |
| page | 0-indexed page number within the scenario (0..3) |
| condition | 2(direction) x 2(frequency): DL=dec_single, IL=inc_single, DH=dec_multiple, IH=inc_multiple |
| age | Participant age in years (float) |
| gender | f / m / nb (raw 1=female, 2=male, 3=non-binary) |

#### exp2 (Study 2)
| column | description |
|--------|-------------|
| participant_id | Assigned ID P000..P801 |
| trial | 0=choice, 1=agreement, 2=prediction, within each participant |
| response | Value depends on measure: choice = 0 buy now / 1 buy later (recoded); agreement = belief that price continues same direction, 1=strongly disagree .. 7=strongly agree (raw); prediction = estimated price in $ one week from now (raw, open-ended) |
| variable | Original source column for this response |
| measure | choice / agreement / prediction — which response of the participant's trial |
| condition | dec_single, inc_single, dec_multiple, inc_multiple |
| age | Participant age in years (float) |
| gender | f / m / nb (raw 1/2/3) |

#### exp3 (Study 3)
| column | description |
|--------|-------------|
| participant_id | Assigned ID P000..P1505 |
| trial | 0=choice, 1=prediction, within each participant |
| response | choice = 0 buy now / 1 buy later (recoded); prediction = estimated price in $ one week from now (raw, 0-150). |
| variable | Original source column for this response |
| measure | choice / prediction |
| condition | 2(direction) x 3(frequency): dec_single, inc_single, dec_monotonic, inc_monotonic, dec_nonmonotonic, inc_nonmonotonic (Mo=monotonic multiple, Non=nonmonotonic multiple) |
| age | Participant age in years (float) |
| gender | f / m / nb (raw 1/2/3) |

#### exp4 (Study 4)
| column | description |
|--------|-------------|
| participant_id | Assigned ID P000..P1505 |
| trial | 0=choice, 1=prediction, within each participant |
| response | choice = 0 buy now / 1 buy later (recoded); prediction = estimated price in $ one week from now (raw, 0-500). |
| variable | Original source column for this response |
| measure | choice / prediction |
| condition | 2(direction) x 3(timing/frequency): dec_single_late, inc_single_late, dec_single_early, inc_single_early, dec_multiple, inc_multiple (La=late single change, Ea=early single change, High=multiple) |
| age | Participant age in years (float) |
| gender | f / m / nb (raw 1/2/3) |

#### exp5 (Study 5)
| column | description |
|--------|-------------|
| participant_id | Assigned ID P000..P296 (European business school students) |
| trial | 0..3, one per product, in the columns' fixed product order |
| response | Product decision: 0 = buy now, 1 = wait / defer. Recoded from raw 1/2. |
| variable | Original source column for this product's response (S<Prod><Cond>) |
| condition | 2(direction) x 2(frequency) per product: dec_single, dec_multiple, inc_single, inc_multiple |
| product | card_holder / charger / water_bottle / laptop_bag |
| update_optin | Whether participant opted to receive a price update for this product (raw Qualtrics codes: 4 = yes, 5 = no; NaN if not asked because the participant bought now) |
| age | Participant age in years (float) |
| gender | f / m (raw 1=female, 2=male) |
| why | Free-text rationale for purchase decisions (verbatim) |
| q77_look | "How much did you like the look of the pages?" filler, 1-7 (raw) |
| q78_purchase_likely | "How likely would you purchase there?" filler, 1-7 (raw) |
| q79_recommend_likely | "How likely to recommend?" filler, 1-7 (raw) |
| q81_brand_fit | "Look fits ESADE brand/image?" filler, 1-7 (raw) |

Raw SPSS .sav files per study were sourced from ResearchBox #402. Each participant makes between-subject decisions assigned to a condition; expN maps to the paper's Study N (exp0=Study 1a, exp1=Study 1b, ..., exp5=Study 5). A bug-fix pass during verification ensured all condition arms (including the `inc_*` conditions) are correctly carried through for exp0.

## Text-format conversion

All six experiments were transcribed to natural language (text-format:pass): each study is a text-based purchase scenario, so the price histories, buy-now/wait choices, agreement and price-prediction measures, free-text rationales, and opt-in/filler ratings all render faithfully as one transcript per participant (`transcripts0.jsonl`…`transcripts5.jsonl`). No experiment was skipped. Response format (N = buy now, W = wait, plus 1–7 / dollar / free-text tokens) is pinned in the instructions before the first trial.

Sample transcript (exp0, Study 1a):

```
You are shopping for a flight ticket for your upcoming holidays. Only one airline flies directly to your destination, so you must fly with it. The airline shows you the ticket's historical prices: $200 (4 weeks ago), $250 (3 weeks ago), $300 (2 weeks ago), $350 (1 week ago). Currently, the ticket costs $400.
On each decision you press N if you would buy the ticket now, or W if you would wait to buy it later (defer the purchase).
You decide whether to buy the $400 ticket now or wait. You press [HUMAN_RESPONSE]N[/HUMAN_RESPONSE].
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

All six experiments got a text simulator (`simulate0.py` … `simulate5.py`), and the
round-trip check passed for each: regenerating the transcripts through `build_jsonl.py`
from a simulated `expN.csv` matches the simulator's own prompts byte-for-byte.
Columns and dtypes match the repo's `expN.csv` (demographics `age`/`gender` dropped).
Each simulator assigns conditions uniformly at random; Study 5 uses the CSV's fixed
product order and Study 2/Study 4 the CSV's fixed measure order (the paper's random
orders are not recoverable from the data). No experiment was skipped.

Fixed 2026-09-15: simulate5.py asked for the free-text explanation before the response marker; the cue now ends with the open marker (check_calls.py passes).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Online experiment

All six studies now have a static jsPsych v8 online experiment under `experiments/expN/`
(exp0 = Study 1a … exp5 = Study 5), rebuilt verbatim from the paper and the
ResearchBox #402 survey materials (this dataset has no text simulator). The headless
`?mode=simulate` round trip passed for every experiment — each run's CSV matches
the matching `expN.csv` column names, dtypes, codings, and per-participant row
counts. A visual rendering check found no gross breakage (a button-overflow on the
long-option screens was fixed by wrapping). The experiments ship with `saveData`
offering a CSV download and no data-collection backend. See `experiments/README.md`.

Assumptions surfaced: browser-only cosmetic defaults (layout, colors, button
styling); Study 5 omits product photographs (kept as title/price/description text)
and presents products in the fixed order the CSVs use for `trial`; the Study 5
training/comprehension questions are shown once as written (their answers are not in
the schema). `saveData` is the seam for wiring a real collection endpoint.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 1, minor 11; fixed 5, open 7).

Checked: paper (https://doi.org/10.1177/00222437211060359, preprint PDF, 50 pp.), original data (ResearchBox #402 via the Zenodo mirror https://zenodo.org/records/15032921: six SPSS .sav files, codebooks, survey materials), exp0-exp5 against the paper's Table 1/Table 2 (every per-condition N, deferral rate, prediction mean/SD and the Study 1b deferral counts match exactly), transform re-run (byte-identical exp0-exp5.csv from the .sav files), transcripts (build_jsonl.py regenerates all six files byte-for-byte; exp2/exp4/exp5 tokens re-checked against the CSVs with a measure-aware mapping), simulators (simulate0-5.py run; round trip through build_jsonl.py byte-identical; columns and dtypes match the CSVs minus age/gender), analysis (all three effects reproduce), logs. Modeling: not applicable (no model.py, no cognitive-modeling tag). Skipped: none.

Fixed:
- major: transcripts5.jsonl, build_jsonl.py and simulate5.py rendered the Study 5 product prices in dollars; the paper (Table 2, p. 46) and the survey materials (pp. 38-39) price them in euros. Added _eur() in build_jsonl.py and simulate5.py, rebuilt transcripts5.jsonl (297 transcripts, only file that changed), round trip re-verified byte-identical.
- minor: README said all headline effects reproduce with p < 1e-12; the exp0 logistic direction x frequency interaction has p = 1.6e-12 (the two chi-square tests have p < 1e-20). Changed to p < 1e-11.
- minor: README did not say which raw update_optin code is yes/no; the .sav value labels are 4 = Yes, 5 = No, and it is NaN exactly when the participant bought now. Documented.
- minor: the six per-experiment Columns headings used ### instead of the template's ####. Changed the heading level.
- minor: transform.py read raw/converted/Study N.csv files that the source does not ship (ResearchBox #402 ships .sav files). load() now converts raw/Study N - Data.sav with pyreadstat when the CSV is missing; re-run from the six .sav files alone gives byte-identical exp0-exp5.csv.

Open:
- minor (checker artifact): check_repo reports 55/802 (transcripts2) and 1/1506 (transcripts4) transcripts whose marked tokens do not map one-to-one onto the CSV responses. These are exactly the participants whose numeric answer equals the choice code (e.g. W = 1 next to an agreement rating of 1, or a $1 price prediction); a measure-aware comparison finds 0 mismatches in all 802 + 1506 transcripts.
- minor (checker artifact): check_repo reports undeclared response tokens in transcripts2/3/4 (434, 621, 592 transcripts). These are open-ended price predictions (and 2-6 on the exp2 agreement scale), which cannot be enumerated; the instructions declare the ranges ($0-$150, $0-$500, 1 to 7) and N/W.
- minor: exp5.csv keeps the price-update opt-in (update_optin), the rationale (why) and the four filler ratings as columns of the four product rows instead of separate response rows, so check_repo counts 12 marked responses against 4 rows per participant. All 297 transcripts agree with the CSV columns; the layout is documented in the Columns table and left unchanged.
- minor: the exp2 agreement prompt paraphrases the statement ('Rate your agreement that 'continue to decrease in the future'') and omits the middle anchor (survey materials p. 14: 'The price will continue to decrease in the future', 1 = strongly disagree, 4 = neither agree nor disagree, 7 = strongly agree).
- minor: transcripts5 asks the price-update opt-in right after each wait decision; the survey asked it after all four products and the rationale (survey materials p. 60). The Q78/Q79 filler anchors were 'not at all likely / very likely' (p. 61); the transcript uses 'not at all / very much' for all four fillers.
- minor: age outliers are present in the source and kept for fidelity (exp1: one participant with age 400; exp4: one with age 4).
- minor (checker artifact): check_repo parses 'N = 5,713' in the Experiment summary as 5; the text is correct (802 + 800 + 802 + 1506 + 1506 + 297 = 5713).

Run: claude-fable-5-1, 2026-09-10
