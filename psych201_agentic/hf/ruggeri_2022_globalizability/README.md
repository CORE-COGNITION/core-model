---
tags:
- paradigm:temporal-discounting
- psych-101
- text-format:pass
- js-experiment:pass
- simulator:pass
---

# ruggeri_2022_globalizability

- Paper: https://doi.org/10.1038/s41562-022-01392-w
- Data source: https://osf.io/njd62
- PDF: https://pure.uva.nl/ws/files/115659231/s41562_022_01392_w.pdf
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Ruggeri, K., Panin, A., Vdović, M., Većkalov, B., et al. (2022). The globalizability of temporal discounting. Nature Human Behaviour, 6(10), 1386–1397. https://doi.org/10.1038/s41562-022-01392-w

## Experiment summary
One large cross-national survey (60+ countries, ~10k+ participants) measuring temporal discounting via binary choices between immediate and delayed monetary rewards across multiple questionnaire blocks (small-gain, pay/loss, large-gain conditions at several delay lengths), plus risk-preference and other decision "anomaly" items (common-difference/present bias, absolute magnitude, gain-loss asymmetry, delay-speedup, subadditivity, interval markup, discretionary spending, time-versus-money). The transformed dataset is exp0.csv with 24,813 participants and 372,363 responses (attention-pass sample), one row per participant×item. Primary responses are binary discounting choices (verbatim choice text) and Likert/allocative judgments. The research question is whether temporal discounting globalizes — i.e., how discounting and these anomalies relate to country-level wealth (GDP), income inequality (GINI), inflation, and individual resources, using hierarchical generalized additive and Bayesian regression models. All three headline effects reproduced on exp0: gains are discounted more than losses (sign effect), delayed-gain preference increases with absolute magnitude (small vs large gains), and self-reported assets inversely predict discounting.

## Notes

### Columns

### exp0

Source: raw/999_2_data_original_1_10_2021.csv (OSF osf.io/njd62). One row per (participant, item) response, pivoted long from the wide questionnaire. Items in the adaptive survey are hidden when not administered, so each participant answers a subset.

| column | description |
|--------|-------------|
| participant_id | Original Qualtrics ResponseId (e.g. R_...) from source CSV |
| trial | 0..N-1 within each (participant_id, task_id), following the instrument's question order within each block (numeric Q-number for the titration blocks). Note: the anomaly-section blocks were displayed in per-participant randomized order (recorded verbatim in `Anomalies_DO`), so for those blocks `trial` reflects the canonical instrument order, not each participant's display order. |
| item | Source column name of the question (Q2..Q16, Common difference, Subadditivity, Delay-speedup 1/2, Interval markup, Risk preference, Discretionary spend_2..5, Time vs Money) |
| response | Raw response value: verbatim choice text (e.g. "Receiving $500 right now") for discounting/anomaly/risk/interval/time_vs_money; numeric dollar amount (raw units) for discretionary spend_2..5 |
| block | 0-indexed survey block: 0=small gain (Q2..Q6), 1=pay/loss (Q7..Q11), 2=large gain (Q12..Q16), 3=Common difference, 4=Subadditivity, 5=Delay-speedup 1&2, 6=Interval markup, 7=Risk preference, 8=Discretionary spend, 9=Time vs Money |
| task_id | 0-indexed task type: 0=temporal discounting, 1=anomaly items, 2=interval markup, 3=risk preference, 4=discretionary spend, 5=time vs money |
| phase | snake_case grouping: discounting / anomaly / interval_markup / risk_preference / discretionary_spend / time_vs_money |
| StartDate | Qualtrics start timestamp of survey session |
| EndDate | Qualtrics end timestamp |
| Status | Qualtrics status ("IP Address") |
| Progress | Qualtrics completion progress 0-100 |
| duration | Survey duration in seconds (renamed from "Duration (in seconds)") |
| Finished | Qualtrics finished flag (TRUE/FALSE) |
| RecordedDate | Qualtrics recorded timestamp |
| DistributionChannel | Qualtrics distribution channel ("anonymous") |
| UserLanguage | Qualtrics survey language code (e.g. ES, EN) |
| Consent | Consent response ("CONSENT") |
| Attention check | Attention/comprehension check result ("PASS"/...), verifies attentive responding |
| Q24 | Financial expectation item response (raw text) |
| Q25 | Bills/expense item response (raw text) |
| Q26_1 | Self-reported income (ordinal/numeric code, raw) |
| Q26_2 | Self-reported debt (ordinal/numeric code, raw) |
| Q26_3 | Self-reported assets (ordinal/numeric code, raw) |
| Q27 | 2020 financial situation change item (raw text) |
| Q28 | Debt situation item (raw text) |
| Q29 | Financial situation vs childhood item (raw text) |
| Q30 | Birth year used to compute Age (2021 - Q30) |
| Q31 | Gender (raw text: Man/Woman/Other/prefer) |
| Q31_3_TEXT | Open-text other-gender response |
| Q32 | Education level completed (raw text) |
| Q33 | Employment status (raw text) |
| Q34 | Ethnic background (raw text; may be comma-list) |
| Q34_16_TEXT,Q34_12_TEXT,Q34_10_TEXT,Q34_1_TEXT,Q34_9_TEXT,Q34_6_TEXT,Q34_12_TEXT - Topics,Q34_5_TEXT,Q34_21_TEXT,Q34_7_TEXT,Q34_11_TEXT,Q34_4_TEXT,Q34_19_TEXT,Q34_2_TEXT | Open-text ethnic-background responses (per-country open fields) |
| REGION | Country region string from Qualtrics |
| Anomalies_DO | Pipe-separated anomaly block display-order list |
| Demographics_DO | Pipe-separated demographics block display-order list |
| Q_RecaptchaScore | Qualtrics reCAPTCHA score |
| Q41 | Country-currency free-text item (raw) |
| Japan_pay | Japan paid/unpaid sample marker |
| Province | Subnational region province text |
| Residence | Full country name (e.g. Argentina) |

## Text-format conversion

The single experiment (`exp0.csv`) was transcribed to natural language (`transcripts0.jsonl`,
one line per participant, whole session in order). The whole survey is textifiable: every item
is a verbalizable monetary choice (receive/pay now vs later, choice-anomaly, interval markup,
risk preference, discretionary-spend amount, time-vs-money). No experiment was skipped.

Sample transcript (from the start, up to and including the first response):

```
You take part in a survey about how people make financial decisions over time. You are asked to make a series of monetary choices, each offering two options. For each choice, type exactly the text of the option you prefer. On the items that ask for a dollar amount, type the number you would spend. There are no right or wrong answers.

Now a new section of the survey begins.

Discounting, small gains: for each choice you compare receiving an amount right now with receiving an amount in 12 months.
Options: Receiving $500 right now or Receiving $550 in 12 months. You press [HUMAN_RESPONSE]Receiving $500 right now[/HUMAN_RESPONSE]
 …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24
- Trial-order fix (rows reordered; only the `trial` column renumbered, no other cell changed): the
  previous release sorted items lexicographically by the `item` string, so in the pay/loss
  titration block (block 1) Q10 and Q11 came before the block opener Q7 (and Q8, Q9), and `trial`
  numbered that wrong order — contradicting the column table's claim that `trial` follows item
  order. Rows are now sorted within each `(participant_id, task_id, block)` by the instrument's
  question order (numeric part of the Q label); `trial` renumbered 0..N-1 within
  `(participant_id, task_id)`.
- Affected: 44,187 rows (block-1 Q7-Q11 rows) across 16,136 of 24,813 participants; row count,
  participant count, and per-participant row multisets unchanged; all other columns byte-identical.
- Caveat now documented in the `trial` row above: the anomaly-section blocks (blocks 3-9) were
  displayed in per-participant randomized order (kept verbatim in `Anomalies_DO`); `trial` orders
  them by the canonical instrument order, not each participant's display order.

CSVs fixed in place from the previous release; transform.py updated to produce the same output
from raw. The previous version remains in the repo's git history.

## Online experiment

One runnable static experiment, `experiments/exp0/` (a jsPsych v8 port of the original
Qualtrics instrument "Temporal Discounting Global Base ENGLISH", OSF osf.io/njd62 — the base
English / US$ version the cross-national fields were adapted from). The headless `?mode=simulate`
round trip passed: it reproduces `exp0.csv`'s exact 55-column schema, the adaptive titration
cascade, 0-indexed `trial` resets per task, and the indifference-point personalization of the
four choice-anomaly items (verified at 99.9–100% against the dataset). The real (non-simulated)
flow runs end-to-end in a headless browser. Assumptions: single base currency US$ and base
English wording; Qualtrics-internal / unused free-text columns left blank or filled from the live
session. See `experiments/README.md`.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

`simulate0.py` (in this repo) generates text-format-identical participant sessions for `exp0`.
The round-trip check passed: a simulated DataFrame fed back through `build_jsonl.py` reproduces the
simulator's own prompt text byte-for-byte. Simulators reflect the paper's choice-driven titration
and the empirical per-block administration rates, with two modelling assumptions surfaced in the
class docstring: (1) which non-always blocks a participant sees is drawn from the empirical presence
rates rather than the (unrecoverable) adaptive survey logic; (2) the anomaly/interval/risk/time-vs-money
chosen option text is drawn from the frequency-weighted distribution of the real responses in
`exp0.csv` (indifference-point and currency personalization is not reproduced).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25