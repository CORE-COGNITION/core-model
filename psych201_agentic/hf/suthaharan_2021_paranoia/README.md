---
tags:
- paradigm:aversive-reversal-learning
- cognitive-modeling:pass
- psych-201
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---
# suthaharan_2021_paranoia

- Paper: https://doi.org/10.1038/s41562-021-01176-8
- Data source: https://github.com/psuthaharan/covid19paranoia
- PDF: https://www.nature.com/articles/s41562-021-01176-8.pdf
- Full text: https://www.ncbi.nlm.nih.gov/pmc/articles/8458246/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Suthaharan, P., Reed, E. J., Leptourgos, P., Kenney, J. G., Uddenberg, S., Mathys, C. D., Litman, L., Robinson, J., Moss, A. J., Taylor, J. R., Groman, S. M., & Corlett, P. R. (2021). Paranoia and belief updating during the COVID-19 crisis. Nature Human Behaviour, 5(9), 1190–1202.

## Experiment summary
Adults (MTurk/CloudResearch) completed a probabilistic reversal-learning task across two between-subjects conditions: a non-social version (choosing among deck images, N = 311) and a social version (choosing which avatar 'collaborator' to trust, N = 627). Each session had 160 trials, which the paper presents as 4 blocks of 40 and the source stores as two 80-trial halves (`block` 0/1 here; the reward contingencies change at trial 80), with discrete option choices (3 options) and binary reward outcomes whose contingencies drifted and periodically reversed. Participants were recruited across US states between March and July 2020 spanning the pre-lockdown, lockdown, and post-lockdown pandemic periods, plus a replication cohort, and completed self-report questionnaires (RGPTS paranoia, BAI, BDI, DOCS, conspiracy and mask-attitude scales). The research question asks whether rising real-world uncertainty during the pandemic increased paranoia and made belief updating more erratic/volatile. Data are trial-level choices plus per-participant questionnaire and Hierarchical Gaussian Filter (HGF) fitted parameters.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Remapped participant identifier, `P000`.. in first-appearance order (source study_id / .mat key dropped as an identifier). |
| trial | 0-indexed trial number within participant, 0..159 (2 blocks x 80 trials). |
| block | 0-indexed block half of the 160-trial session (0 = trials 1-80, 1 = trials 81-160). |
| response | The participant's deck choice on that trial, 0-indexed (choice 1/2/3 -> 0/1/2). |
| reward | Binary outcome on that trial, 0 (loss) / 1 (win), from the .mat outcomes arrays. |
| phase | Session phase label; always `test` (the .mat files contain only the task trials). |
| task_type | Always `nonsocial` (this file = non-social PRL experiment). |
| month | Collection-wave index from the source: 2-3 = Mar-Apr 2020 (lockdown), 4-5 = Jun-Jul 2020 (reopening); blank for the replication cohort (Sep-Oct 2020). |
| date_collected | Collection date string (m/d/yyyy). |
| dataset | Cohort label: `pandemic` or `replication` (the 72 `elife2020` non-social participants have no choice data in the source and are not in this file). |
| period | Pandemic period: `lockdown` / `postlockdown` (the source has no prelockdown non-social choice data). |
| state | Participant's US state abbreviation. |
| region | Participant's census region (e.g. South, Northeast, West). |
| state_gini | State-level Gini index (income inequality); present only for the reopening (`postlockdown` pandemic) cohort, blank otherwise. |
| state_proactivity | State-level COVID proactivity metric. |
| state_ctl | State-level cultural tightness index. |
| state_mask_mandate | State-level mask mandate indicator. |
| demo_1..demo_10 | Self-report demographic questionnaire items (raw codes). |
| bai_1..bai_21 | Beck Anxiety Inventory item scores (blank = not administered). |
| bdi_1..bdi_21 | Beck Depression Inventory II item scores (bdi_9 absent -> all blank). |
| rgpts_ref_1..8, rgpts_per_9..18 | Revised Green et al. Paranoid Thoughts Scale item scores (ref suspicion / per persecution). |
| docs_1..docs_20 | DOCS obsessive-compulsive checklist item scores. |
| gcbs_1..gcbs_15 | Generic Conspiracist Beliefs Scale item scores. |
| qanon_political_4 | Political affiliation item. |
| qanon_rating | QAnon-belief rating. |
| covid_conspiracy_vaccine_1..5 | COVID vaccine conspiracy belief items (Likert). |
| mask_behavior_1..16 | Mask-wearing behavior belief items. |
| sabotage_decks_avatars | Whether participant believed decks/avatars deliberately sabotaged them (mostly blank for nonsocial). |
| points_earned | Total task points earned (blank for the replication cohort). |
| avg_rt_block1 / avg_rt_block2 / avg_rt_total | Mean response time (ms) per block / total. |
| reversals_block1 / reversals_block2 | Number of contingency reversals detected per block. |
| wsr_block1 / wsr_block2 | Win-switch rate per block. |
| lsr_block1 / lsr_block2 | Lose-stay rate per block. |
| mu02_1, mu03_1, kappa2_1, omega2_1, omega3_1, mu02_2, mu03_2, kappa2_2, omega2_2, omega3_2 | HGF fitted belief/volatility parameters per block (`_1` = block 1, `_2` = block 2). |
| mu02_1_precision, mu03_1_precision, kappa2_1_precision, omega2_1_precision, omega3_1_precision, mu02_2_precision, mu03_2_precision, kappa2_2_precision, omega2_2_precision, omega3_2_precision | Precision weights corresponding to the HGF parameters above. |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Remapped participant identifier, `P000`.. in first-appearance order (source study_id / .mat key dropped as an identifier). |
| trial | 0-indexed trial number within participant, 0..159 (2 blocks x 80 trials). |
| block | 0-indexed block half of the 160-trial session (0 = trials 1-80, 1 = trials 81-160). |
| response | The participant's avatar (collaborator) choice, 0-indexed (choice 1/2/3 -> 0/1/2). |
| reward | Binary outcome on that trial, 0 (loss) / 1 (win), from the .mat outcomes arrays. |
| phase | Session phase label; always `test`. |
| task_type | Always `social` (this file = social PRL experiment). |
| month | Collection-wave index from the source: 1 = Jan 2020 (prelockdown), 2-3 = Mar-Apr 2020 (lockdown), 4-5 = Jun-Jul 2020 (reopening); blank for the replication cohort (Sep-Oct 2020). |
| date_collected | Collection date string (m/d/yyyy). |
| dataset | Cohort label: `pandemic` or `replication`. |
| period | Pandemic period: `prelockdown` / `lockdown` / `postlockdown`. |
| state | Participant's US state abbreviation. |
| region | Participant's census region. |
| state_gini | State-level Gini index (income inequality); present only for the reopening (`postlockdown` pandemic) cohort, blank otherwise. |
| state_proactivity | State-level COVID proactivity metric. |
| state_ctl | State-level cultural tightness index. |
| state_mask_mandate | State-level mask mandate indicator. |
| demo_1..demo_10 | Self-report demographic questionnaire items (raw codes). |
| bai_1..bai_21 | Beck Anxiety Inventory item scores (blank = not administered). |
| bdi_1..bdi_21 | Beck Depression Inventory II item scores (bdi_9 absent -> all blank). |
| rgpts_ref_1..8, rgpts_per_9..18 | Revised Green et al. Paranoid Thoughts Scale item scores. |
| docs_1..docs_20 | DOCS obsessive-compulsive checklist item scores. |
| gcbs_1..gcbs_15 | Generic Conspiracist Beliefs Scale item scores. |
| qanon_political_4 | Political affiliation item. |
| qanon_rating | QAnon-belief rating. |
| covid_conspiracy_vaccine_1..5 | COVID vaccine conspiracy belief items (Likert). |
| mask_behavior_1..16 | Mask-wearing behavior belief items. |
| sabotage_decks_avatars | Whether participant believed decks/avatars deliberately sabotaged them. |
| points_earned | Total task points earned (blank for the replication cohort). |
| avg_rt_block1 / avg_rt_block2 / avg_rt_total | Mean response time (ms) per block / total. |
| reversals_block1 / reversals_block2 | Number of contingency reversals detected per block. |
| wsr_block1 / wsr_block2 | Win-switch rate per block. |
| lsr_block1 / lsr_block2 | Lose-stay rate per block. |
| mu02_1, mu03_1, kappa2_1, omega2_1, omega3_1, mu02_2, mu03_2, kappa2_2, omega2_2, omega3_2 | HGF fitted belief/volatility parameters per block (`_1` = block 1, `_2` = block 2). |
| mu02_1_precision, mu03_1_precision, kappa2_1_precision, omega2_1_precision, omega3_1_precision, mu02_2_precision, mu03_2_precision, kappa2_2_precision, omega2_2_precision, omega3_2_precision | Precision weights corresponding to the HGF parameters above. |

Experiment mapping: exp0 = non-social PRL (paper's non-social condition), exp1 = social PRL (paper's social condition). Trial-level choices/outcomes come from the GitHub `.mat` HGF files; the replication `.mat` files map internal participant keys (TP/VM/E) to `R#` study_ids positionally via the filename ranges, and `pandemic_postlockdown_TP694_TP865_172.mat` likewise stores its 172 participants under `R100..R271` keys and is mapped positionally onto `TP694..TP865`. Both mappings were verified against the per-participant win-switch / lose-stay rates and points that the source's Qualtrics file records (r > 0.99). `scid_group` (SCID-II grouping, recorded only for the 72 `elife2020` participants) and `bdi_9` (empty in the source) are dropped because they are empty for every participant with choice data. Participant IDs are remapped to `P000`.. to avoid shipping MTurk/Prolific identifiers. The `response` column is 0-indexed (1/2/3 -> 0/1/2).




## Text-format conversion

For dataset `suthaharan_2021_paranoia` (Psych-301 schema): each experiment was transcribed into natural language, one transcript per participant. Both the non-social and social probabilistic reversal-learning experiments (3 options, binary reward) were textifiable; no experiment was skipped.

**Sample transcript** (verbatim from the start through the first `[/HUMAN_RESPONSE]`, truncated with ` …`):

```text
You will play a card game. Three decks of cards are in front of you: deck A, deck B, and deck C. Each deck holds a mix of winning and losing cards - winning cards add 100 points, losing cards take away 50 points. Your job is to find the best deck and earn as many points as possible. The best deck can change, so keep testing your choices. On each trial, type A, B, or C to pick the deck you want to draw from.
You draw a card from deck [HUMAN_RESPONSE]A[/HUMAN_RESPONSE] …
```

Fixed 2026-09-15: the chosen deck/partner was stated before the response marker ('You draw a card from deck A. You type [HUMAN_RESPONSE]A...'); the marker now sits where the choice is made, transcripts rebuilt, simulators mirrored.

Run: `openrouter/deepseek/deepseek-v4-flash-0731`, `2026-08-24`

## Modeling reproduction
Attempted to reproduce the paper's primary computational-modeling result.
Fitted models: Hierarchical Gaussian Filter (HGF) fitted parameters (mu30/kappa/omega2) recorded in the dataset; high-vs-low R-GPTS paranoia group t-tests.
Reproduced: volatility_prior_higher_in_high_paranoia, coupling_kappa_higher_in_high_paranoia, omega2_lower_in_high_paranoia.
Not reproduced: none.
Numeric mismatch: none (qualitative group directions match the paper's F-statistics).
Partial validation: <omit>.
Indeterminate: <none>.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

Both experiments were ported to static jsPsych v8 sites under `experiments/` (`exp0/` non-social
decks, `exp1/` social avatars) and validated headless: each `?mode=simulate` round trip exported
a CSV whose schema matches its `expN.csv` exactly (174 columns; `trial` 0-159, `block` 0/1,
`response` 0/1/2, `reward` 0/1, `task_type`, plus computed `points_earned` / `avg_rt_*`), so no
experiment was skipped. The participant-constant columns (demographics, questionnaires,
period/state, HGF parameters, derived `wsr`/`lsr`/`reversals`) come from the original cohort and
cannot be produced by a fresh browser session, so they are left blank (missing) per the schema.
ASSUMPTION: the paper fixes the reward schedule (90/50/10 then 80/40/20, reversal after 9-of-10
rewards) but not the initial best option / rotation order nor the exact reversal trigger; these
are implemented as A-first, rotating A->B->C, with a sliding 9-of-10 window on observed
best-option rewards — defaults that do not change the recorded schema.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Both experiments got a text simulator (`simulate0.py` non-social decks, `simulate1.py` social partners); the round-trip check passed — regenerating transcripts from each simulated CSV with `build_jsonl.py` reproduces the simulator prompts byte-for-byte. No experiment was skipped. ASSUMPTION: reward schedule 90/50/10 then 80/40/20 with the best deck/partner starting at A and rotating A->B->C after 9 wins in a 10-trial sliding window (same defaults as the repo's js-port).
Fixed 2026-09-15: simulators mirror the rebuilt transcripts and ask the agent at the open marker (check_calls.py passes).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 1, major 3, minor 7; fixed 10, open 1).

Checked: paper (https://doi.org/10.1038/s41562-021-01176-8, PDF), original data (https://github.com/psuthaharan/covid19paranoia: qualtricsPRL/pandemicPRL.csv and the 8 hgfPRL .mat files), exp0-exp1, transform re-run, participant mapping against the source's own per-participant win-switch/lose-stay rates and points, transcripts, simulators (smoke test and build_jsonl.py round trip), modeling, analysis, logs. Skipped: none.

Fixed:
- critical: transform.py joined the 172 participants of pandemic_postlockdown_TP694_TP865_172.mat to the wrong questionnaire rows. That file stores its participants under R100..R271 keys, not their TP study_ids; the script used the key as the Qualtrics study_id, so postlockdown choices were attached to replication participants R100..R271 (wrong task_type, period, R-GPTS and HGF values) and the true choices of R100..R271 were skipped as duplicates. Evidence: with the direct key match the per-participant win-switch rate recomputed from the choices does not match the source's wsr_block1 (r = -0.08, points_earned exact in 0 %); mapped positionally onto TP694..TP865 it matches (r = 0.999, points exact in 100 %), and the task_type split becomes 93 non-social / 79 social as the paper reports (p. 1199). Fix: non-TP keys are mapped positionally onto the filename's TP range; exp0.csv (218 -> 311 participants) and exp1.csv (548 -> 627) regenerated, state_gini (recorded only for the reopening cohort) now present, transcripts0/1.jsonl rebuilt. After the fix every row's wsr/lsr/points match its own trial data (r > 0.998; points exact for all pandemic participants).
- minor: transform.py iterated glob.glob() in filesystem order, so a re-run reproduced exp1.csv with a different participant order (same data, different P-ids); globs are now sorted.
- major: simulate0.py / simulate1.py drew the reward as probs[response], so option A kept P(reward) = 0.9 through the whole block (measured 0.89 early, 0.90 late) and the 9-of-10 reversal the docstring and the README describe never changed the contingencies; the probability now follows the current best option (probs[(response - best) % 3]). Round trip through build_jsonl.py still byte-identical; late-block reward rates now move (A: 0.89 -> 0.36).
- minor: simulator docstrings cited 'Behavioural tasks', p. 1199; the section is on p. 1200.
- minor: model.py docstring cited F(1,198) = 8.673 for the volatility prior; the paper (Fig. 2, p. 1192) gives 8.566.
- major: README gave 218 / 548 participants; the CSVs now hold N = 311 (exp0) and N = 627 (exp1), matching the paper's per-period counts (p. 1199: 119 + 93 non-social, 130 + 112 + 79 social) plus the replication cohort (99 non-social, 306 social).
- minor: README said '2 blocks of 80 trials'; the paper (p. 1200) presents 160 trials as 4 blocks of 40 and the source stores two 80-trial halves (HGF fit per half) - the summary now says both.
- major: README Columns tables: heading level ### -> ####; a scid_group row for a column not in the CSVs removed (recorded only for the 72 elife2020 participants, who have no choice data); the group rows 'mu02_1/2, ...' and '*_precision' expanded to the 20 HGF column names; state_gini row added; month, dataset and period descriptions corrected for exp0 (no elife2020 / prelockdown non-social choice data in the source); points_earned noted as blank for the replication cohort.
- minor: the README sample transcript showed an em dash where the transcripts use ' - '.
- minor: the README referred to another dataset's transform ('matched wise_2019_computational'), and logs/auto-exp-{modeling,sim,transcribe}.sessions.json and transcripts/auto-exp-transcribe.log carried other datasets' names from the harness context (check_repo: cross-run contamination); the clauses were dropped from the README and the foreign names redacted to [other-dataset] in those four log files.

Open:
- minor: the paper reports 1,010 participants (p. 1199); the source ships choice data for 938. The 72 elife2020 non-social prelockdown participants are questionnaire-only in the GitHub repo (their task data belongs to a previous publication), so exp0 has no prelockdown cohort. Inside the source; documented in the README.

Run: claude-fable-5-1, 2026-09-13
