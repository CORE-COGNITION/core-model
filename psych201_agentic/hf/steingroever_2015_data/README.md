---
tags:
- paradigm:iowa-gambling-task
- psych-101
- text-format:pass
- js-experiment:pass
- simulator:pass
- verification:pass
---

# steingroever_2015_data

- Paper: https://doi.org/10.5334/jopd.ak
- Data source: https://osf.io/8t7rm
- PDF: https://openpsychologydata.metajnl.com/articles/15/files/submission/proof/15-1-144-4-10-20160628.pdf
- Full text: https://openpsychologydata.metajnl.com/articles/10.5334/jopd.ak/
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Steingroever, H., Davis, H., Fridberg, D. J., Horstmann, A., Kjome, K. L., Kumari, V., Lane, S. D., Maia, T. V., McClelland, J. L., Pachur, T., Premkumar, P., Stout, J. C., Wetzels, R., Wood, S., Worthy, D. A., & Wagenmakers, E.-J. (2015). Data from 617 healthy participants performing the Iowa gambling task: A "Many Labs" collaboration. Journal of Open Psychology Data, 3(1), e5. https://doi.org/10.5334/jopd.ak

## Experiment summary
This data-pooling paper benchmarks healthy adult Iowa Gambling Task (IGT) performance across 10 independent studies, providing a "super control group" of N=617 participants. The data are trial-level: on each of 95–150 trials participants choose one of four decks (A–D) and receive win/loss feedback; the choice and resulting win and loss amounts are recorded per trial, along with a subject-to-study index. The three experiment files correspond to the three trial-count groups: exp0 (95 trials, N=15, all from Fridberg), exp1 (100 trials, N=504, from Horstmann/Kjome/Maia/Premkumar/SteingroverInPrep/Wood/Worthy), and exp2 (150 trials, N=98, from Steingroever2011/Wetzels). The dataset supports benchmarking healthy IGT performance and computational model-comparison of decision-making under uncertainty.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Globally unique subject id; 95-trial group subjects are 1..15 |
| source_subject | Original subject number in the 95-trial source file (1..15) |
| trial | 0-indexed trial number, 0..94 within each participant |
| response | Deck chosen that trial, 1=A, 2=B, 3=C, 4=D |
| deck_choice | Same as response (deck chosen, 1-4) |
| win | Win amount for that trial (0 or positive, e.g. 50/100) |
| loss | Loss amount for that trial (0 or negative, e.g. -25/-50/-150/-250/-1250) |
| study | Source study name (all "Fridberg" in this group) |

#### exp1
| column | description |
|--------|-------------|
| participant_id | Globally unique subject id; 100-trial group subjects are 1001..1504 |
| source_subject | Original subject number in the 100-trial source file (1..504) |
| trial | 0-indexed trial number, 0..99 within each participant |
| response | Deck chosen that trial, 1=A, 2=B, 3=C, 4=D |
| deck_choice | Same as response (deck chosen, 1-4) |
| win | Win amount for that trial (0 or positive) |
| loss | Loss amount for that trial (0 or negative) |
| study | Source study name (Horstmann/Kjome/Maia/Premkumar/SteingroverInPrep/Wood/Worthy) |

#### exp2
| column | description |
|--------|-------------|
| participant_id | Globally unique subject id; 150-trial group subjects are 2001..2098 |
| source_subject | Original subject number in the 150-trial source file (1..98) |
| trial | 0-indexed trial number, 0..149 within each participant |
| response | Deck chosen that trial, 1=A, 2=B, 3=C, 4=D |
| deck_choice | Same as response (deck chosen, 1-4) |
| win | Win amount for that trial (0 or positive) |
| loss | Loss amount for that trial (0 or negative) |
| study | Source study name (Steingroever2011/Wetzels) |

The three experiment files map to the paper's three trial-count groups, not to the 10 individual studies: exp0 = 95-trial group, exp1 = 100-trial group (largest, N=504), exp2 = 150-trial group. Subject numbers restart within each source file, so participant_id was offset per group (95-group: 1..15, 100-group: 1001..1504, 150-group: 2001..2098) to keep ids globally unique. The `study` column carries the original study label. Outcomes are reported as `win` (≥0) and `loss` (≤0) per trial; the net outcome per trial is win+loss.

## Text-format conversion

All three experiments (exp0, exp1, exp2) are the same Iowa Gambling Task paradigm differing only in trial count and source study, so a single transcriber covers them. Each was transcribed into `transcriptsN.jsonl` (one line per participant, one trial per line, deck choice marked as a free response). No experiment was skipped — the whole paradigm is textifiable.

Sample transcript (from exp0, up to the first free response):

```
You are taking part in the Iowa gambling task. You are given a loan of $2000 in play money. In front of you are four decks of cards, labeled A, B, C, and D. On each trial you pick one card from one of the four decks by pressing the letter of that deck: A, B, C, or D. After each choice you win some money, and sometimes you also lose some money. Some decks are better overall than others. Your goal is to win as much money as possible, so choose the decks you think are best.
You pick deck [HUMAN_RESPONSE]B[/HUMAN_RESPONSE] …
```

Fixed 2026-09-15: the chosen deck was stated before the response marker ('You pick deck A. You press [HUMAN_RESPONSE]A...'); the marker now sits where the choice is made, transcripts rebuilt, simulators mirrored.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-24

## Online experiment

All three experiments (`exp0/`, `exp1/`, `exp2/`) get a runnable static jsPsych v8 IGT build that saves the finished session in the dataset's own CSV schema (`participant_id,source_subject,trial,response,deck_choice,win,loss,study`). The headless `?mode=simulate` round trip passed for each: same column names, `trial` 0-indexed 0..N-1, `response`/`deck_choice` coded 1-4, `win`>=0, `loss`<=0, and the correct row count per participant. Instruction text is verbatim from the source and the three IGT payoff schemes (paper Supplemental Text 1, Tables A1-A3) are reproduced faithfully. Browser-only assumptions (do not change the recorded data or the task): deck cards A-D left-to-right, feedback ~1500-1700 ms with a 400 ms inter-trial gap, and a running total shown but not recorded (no `total` column in `expN.csv`). In `exp1`, the participant's `study` is drawn proportionally to its sample size and selects the payoff scheme, matching the pooled source; `source_subject` is left blank (unrecoverable) and `participant_id` is a generated session id.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

All three experiments got a text simulator (`simulate0.py`, `simulate1.py`, `simulate2.py`) whose per-trial output is byte-identical to the repo's transcripts after the round-trip check through `build_jsonl.py`. exp0 uses the traditional fixed 40-draw scheme-1 payoff (Fridberg); exp1 draws a study per participant proportional to its sample size and applies its payoff scheme (1: Maia/Worthy, 2: Horstmann/SteingroverInPrep, 3: Kjome/Premkumar/Wood); exp2 uses the scheme-2 shuffled-10-card-block payoff with the study drawn weighted between Steingroever2011 and Wetzels. No `ASSUMPTION:` behind the paper's design: the `study` assignment follows the repo's own jsPsych experiment, and `participant_id`/`source_subject` are simulation indices rather than real subject numbers.

Fixed 2026-09-15: simulators mirror the rebuilt transcripts and ask the agent at the open marker (check_calls.py passes).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 0, major 0, minor 9; fixed 5, open 4).

Checked: paper (https://doi.org/10.5334/jopd.ak, Supplemental Text 1, correction https://doi.org/10.5334/jopd.am), original data (https://osf.io/8t7rm, IGTdataSteingroever2014.zip), exp0-exp2, transform re-run, transcripts, simulators, analysis, logs. Skipped: none.

Fixed:
- simulate0.py and simulate1.py: scheme-1 deck D loss table had -250 at draw 34 (0-indexed 33); the data (Fridberg 11/11, Maia 12/12, Worthy 6/6 draws) and Supplemental Table A1 (trial 35) put it at draw 35. Entries 33/34 swapped.
- simulate1.py: scheme-3 deck D loss table had 0 at draw 20 and -325 at draw 34; the data (Kjome 17/17, Premkumar 22/22, Wood 134/134 at draw 20) and Supplemental Table A3 give -275 at trial 20 and -325 at trial 35. Fixed; block nets are now +250..+375 as the paper states (p. 2).
- simulate1.py: scheme-3 deck B wins at draws 47-55 (160,130,150,150,150,140,150,130,140) disagreed with the data (Premkumar and Wood, unanimous) and Supplemental Table A3 (120,160,130,150,150,160,140,130,150). Fixed; block nets are now -850 and -1000 as the paper states (p. 2). All three payoff tables now match Tables A1-A3 row for row and the CSVs draw for draw (except the source variants listed under Open).
- README citation omitted Hasker Davis; the published correction (doi:10.5334/jopd.am) lists Davis as second author. Added.
- check_repo heuristic: Experiment-summary N claims [617, 15, 504, 98] vs CSV counts [15, 504, 98]. 617 is the pooled total (15+504+98); per-experiment Ns match Table 1 exactly. No change needed.

Open:
- minor: response and deck_choice are coded 1-4 (the source's coding, documented as 1=A..4=D in the README); the schema asks for 0-indexed N-alternative responses. Left as is: every downstream file (transcripts, simulators, analysis) shares the coding and the mapping is documented.
- minor: the paper (p. 3) says feedback included the current total; the transcripts show only the win and the loss of each card. The total is derivable from win+loss; left as is.
- minor (inside the source): the Worthy study's deck C losses differ from Supplemental Table A1 at draws 19, 20 and 40 (-50/0/-25 instead of 0/-50/-75; 22/20/3 draws, unanimous within Worthy). The paper (p. 2) says the studies used '(a variant of) the traditional payoff scheme'; simulate1.py follows Table A1.
- minor (inside the source): one Kjome participant (participant_id 1167) has deck B draws 21-24 shifted by one card relative to Table A3 and a 61st deck D draw (120, -750) beyond the 60-card table. The CSV reproduces the source byte for byte.

Run: claude-fable-5-1, 2026-09-14
