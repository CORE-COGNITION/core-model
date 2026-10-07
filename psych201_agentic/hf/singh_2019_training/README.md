---
tags:
- paradigm:phishing-detection
- psych-201
- text-format:pass
- simulator:pass
- js-experiment:pass
- verification:needs-review
---
# singh_2019_training

- Paper: https://doi.org/10.1177/1071181319631355
- Data source: https://osf.io/r83ag/ (PhishingDataset_HFES2019); mirrored at https://github.com/DDM-Lab/PhishingTrainingTask
- Full text: https://journals.sagepub.com/doi/10.1177/1071181319631355
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Singh, K., Aggarwal, P., Rajivan, P., & Gonzalez, C. (2019). Training to detect phishing emails: Effects of the frequency of experienced phishing emails. Proceedings of the Human Factors and Ergonomics Society Annual Meeting, 63(1), 453-457.

## Experiment summary
Participants classified emails as phishing vs. ham across three phases: pre_training (10 emails, 20% phishing, no feedback), training (40 emails with outcome feedback), and post_training (10 emails, 20% phishing, no feedback). Three experiments (exp0: outcome feedback, N=296; exp1: incentive manipulation, N=299; exp2: detail feedback, N=223) manipulated the frequency of phishing emails during training (25/50/75%) between subjects, each drawing from a shared 239-email database. Per email trial participants gave three responses: a binary phishing decision, a confidence rating (50–100), and an intended action (1–6). The research question was whether the frequency of experienced phishing emails during training affects detection performance (hit rates, false-alarm rates, signal-detection d' and criterion) at post-test.

## Notes

### Columns
The three experiments share the same column set.

| column | description |
|--------|-------------|
| participant_id | Remapped MTurk worker ID, P000..P295 (exp0) / P000..P298 (exp1) / P000..P222 (exp2) in first-appearance order (original Axxx worker IDs dropped as PII) |
| trial | 0..N sequential response counter within participant; three rows per email trial (one per action) |
| block | paper-trial index within participant (0..61 exp0, includes check attention trials; 0..59 exp1/exp2); the 3 response rows of one email share a block |
| response_type | Which action the row holds: phishing_decision / confidence / reaction |
| response | The value of that action: phishing_decision 0=No 1=Yes; confidence 50..100 (not confident..fully confident); reaction 1=Respond 2=Click link/attachment 3=Check sender 4=Check link 5=Delete 6=Report |
| email_type | Stimulus category: ham / phishing / check (attention check, exp0 only) |
| email_id | Nonzero integer ID of the email stimulus (key into PhishingDataset_HFES2019) |
| phase | pre_training (1) / training (2) / post_training (3) |
| condition | Between-subject manipulation base_rate: 25/50/75_OutFeed (exp0), 25/50/75_Inc (exp1), 25/50/75_DetFeed (exp2) |
| trial_in_phase | Source trial number (1..10 pre/post, 1..40 training; chN for an exp0 check trial, shown right before training trial N) |
| time | Source timestamp (MM/DD/YYYY HH:MM, exp0/exp2; DD-MM-YYYY HH:MM, exp1) |
| score | Point awarded on that email trial: 1=correct, 0=incorrect (exp0/exp2), 1=correct / -1=incorrect (exp1, incentive experiment penalizes wrong answers) |
| cum_score | Cumulative score up to that email trial |

Multi-response email trials (3 actions each) are split into one row per response, grouped by `block`. All phases and all three response types are retained.

Rows are in chronological order: phase, then source trial number (a check chN right before training trial N). The source timestamps have minute resolution and the incentive-manipulation source file is sorted by the trial label as text, so `time` is not used for ordering.

## Text-format conversion

All three experiments (exp0.csv, exp1.csv, exp2.csv) were transcribed. Emails are inherently text, so each trial shows the email (sender, subject, body) and the participant's three free responses — phishing decision (Y/N), confidence (50–100), and reaction (A–F, randomized mapping per participant). During training the participant saw feedback (correct/incorrect for exp0/exp2; points for exp1); pre/post gave none. exp0's two attention-check emails carry their instruction in the email body and are narrated like every other email, with the three responses marked. Phase labels follow the block position (10 pre / 40 training / 10 post), which matches the `phase` column.

Sample transcript (exp0, participant P000, up to the first response):

```
You are taking part in a study on detecting phishing emails. Phishing emails are fraudulent messages that try to trick you into revealing personal information or clicking malicious links. You will be shown a series of emails, one at a time, and you will answer three questions about each:
1. Q1 - Is this a phishing email? Press Y if you think it is phishing, or N if you think it is a legitimate email.
2. Q2 - How confident are you in that answer? Type a number from 50 (not confident at all) to 100 (fully confident).
3. Q3 - What would you do if you received this email? Choose one action: A=Respond to the email; D=Click the link or open the attachment; B=Check the sender; F=Check the link; C=Delete the email; E=Report the email.
During the training phase you will receive feedback on your answers. During the pre-training and post-training phases you will not receive any feedback.
Phase: pre-training.
Email: From: discount@eddiebauer.com. Subject: STARTS TODAY! 40% Off Everything!. Save on everything you need for your next adventure.
Eddie Bauer Est 1920,Offers exclude sleeping bags, tents, and non-Eddie Bauer brand products. Offers at Eddie Bauer Outlet and Retail stores may vary, see store for details. Offers may not be valid in stores outside the United States. Additional exclusions may apply. Does not include and cannot be applied to previous or pending purchases, credit card balances, taxes, monogramming charges, gift cards, or gift boxes. Unless explicitly stated above, offers cannot be combined with any other offer. Offer details, including end date, are subject to change or cancellation without notice. 
For discount, visit Eddie Bauer (http://www.eddiebauer.com)
All prices in U.S. dollars.
Q1 Is this email phishing? You press [HUMAN_RESPONSE]N[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Simulators

All three experiments (exp0.csv, exp1.csv, exp2.csv) received a text simulator
(`simulate0.py`, `simulate1.py`, `simulate2.py`), each of which draws distinct
emails from the shared 239/241-email database per simulated participant and
produces transcripts format-identical to the repo's `transcriptsN.jsonl`. The
round-trip check (regenerating each transcript from the simulated DataFrame via
`build_jsonl.py`) passed byte-identically for all three experiments. On the two
exp0 attention-check emails the simulated agent answers like on any other email;
score is 1 when the instructed answers are given, and the check leaves the
cumulative score unchanged.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

All three experiments got a runnable static jsPsych v8 port under
`experiments/expN/` (shared email database in `experiments/stimulus/emails.js`),
and the headless `?mode=simulate` round trip passed for each: the saved CSV
matches `expN.csv`'s schema exactly (columns, codings, 3 rows per block,
`trial = block*3 + k`, phase/condition/trial-in-phase structure), so a browser
session's data is drop-in compatible. None were skipped. Assumption: Q2
confidence is answered on a 50–100 slider (recorded integer value unchanged);
`time` is filled from the browser in the source's format.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: needs-review (critical 1, major 1, minor 10; fixed 7, open 5).

Checked: paper (doi:10.1177/1071181319631355; closed access, see skipped), original data (https://osf.io/r83ag/: experiment1/2/3 CSVs, PhishingDataset_HFES2019.csv, DataInformation.txt; GitHub mirror DDM-Lab/PhishingTrainingTask, identical experiment-1 file), exp0-exp2, transform re-run (original transform.py reproduces all three CSVs byte for byte), transcripts (rebuild), simulators (smoke test and build_jsonl.py round trip), analysis (all six effects reproduce, t = 3.09 to 9.08), logs. Skipped: paper (closed access: publisher, ResearchGate incl. the direct PDF link on the CMU DDMLab page, Academia.edu and the Wayback Machine refused; no open-access copy in CORE, OpenAlex, Unpaywall or Semantic Scholar. Design facts were taken from the abstract, the OSF data dictionary, the authors' GitHub README and Cranford et al. 2021, ICCM, p. 2; participants, payment and exclusions could not be checked).

Fixed:
- critical: transform.py sorted rows by a minute-resolution timestamp with ties in source order. The incentive-manipulation source file is sorted by the trial label as text, so exp1.csv had trials out of order for 293/299 participants (2698 rows moved, phase non-monotonic for 219, 1959 cum_score chain breaks). In exp0.csv 338/589 attention-check rows sat after the training trial they preceded (timestamps and cum_score place check chN right before training trial N in 589/589 cases). transform.py now sorts by phase, trial number and check-before-trial; exp0.csv and exp1.csv regenerated (same rows, only trial/block changed; 0 chain breaks, 0 timestamp decreases), exp2.csv unchanged, transcripts0.jsonl and transcripts1.jsonl rebuilt.
- major: build_jsonl.py narrated the two exp0 attention-check emails as 'You are told to answer' with the participant's own values and no markers, although the instruction is in the email body, confidence is not instructed, and 7/589 check rows deviate from the instruction; every exp0 transcript had 180 marked responses vs 186 free rows. The three responses are now marked like on every other email; transcripts0.jsonl rebuilt (296/296 counts match).
- minor: simulate0/1/2.py mirrored the old check narration, always answered checks correctly, added the check score to cum_score (source: unchanged) and labelled the second check ch(N+1) (source: chN = the next training trial). The agent now answers check emails, score is 1 when the instructed answers are given, cum_score is unchanged, trial_in_phase is ch<next trial>. Round trip through build_jsonl.py: 4/4 byte-identical per experiment. README Simulators note updated.
- minor: simulate0/1/2.py docstrings had unfilled template placeholders (__EXP.csv, exp0_p, __cond_suffix_); filled.
- minor: README claimed a 'noisy per-row phase column (non-monotonic in exp1)'; the column was right and the row order was wrong. Sentence rewritten; the chronological order and the chN semantics are documented under Notes.
- minor: README sample transcript truncated the first email body mid-excerpt; replaced with the verbatim excerpt up to the first response.
- minor: README Text-format section had no Run line; added (openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24, from transcripts/auto-exp-transcribe.log).

Open:
- minor: check_repo.py reports 'marked tokens do not map one-to-one onto the CSV response sequence' for 169/296, 166/299 and 148/223 transcripts. Its token-to-value map spans all three response types: decision value 1 maps to Y and reaction value 1 (Respond) maps to a letter, so every participant who ever chose Respond trips it. Per response type the mapping is one-to-one for all 818 transcripts and token counts equal free-row counts. Not fixable without changing the response coding.
- minor: check_repo.py reports confidence tokens (integers 50-100) as 'never declared'; the instructions state the range, and every confidence token lies within 50..100.
- minor: exp1.csv score = -1 is the point loss of the incentive experiment (4680 source rows), not a missing-value sentinel; the README documents it. The OSF data dictionary lists score as 1/0 only.
- minor: exp2.csv has one cum_score chain break inside the source (participant A2VUU6C8P07V4X, training trial 29 to 30: 27 to 29 with score 1); the data is faithful to the source.
- minor: the authors' GitHub README states 297 participants for experiment 1; the OSF file and the repo README have 296 (98/99/99). The paper was not available to settle it.

Run: claude-fable-5-1, 2026-09-12
