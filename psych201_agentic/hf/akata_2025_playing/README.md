---
tags:
- paradigm:economic-game
- psych-201
- js-experiment:pass
- text-format:pass
- simulator:pass
- verification:pass
---

# akata_2025_playing

- Paper: https://doi.org/10.1038/s41562-025-02172-y
- Data source: https://github.com/eliaka/repeatedgames
- PDF: https://www.nature.com/articles/s41562-025-02172-y.pdf
- Full text: https://www.nature.com/articles/s41562-025-02172-y
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Akata, E., Schulz, L., Coda-Forno, J., Oh, S.-J., Bethge, M., & Schulz, E. (2025). Playing repeated games with large language models. Nature Human Behaviour. https://doi.org/10.1038/s41562-025-02172-y

## Experiment summary
This is a single human study (N=195 Prolific participants) in which each participant was randomly assigned to play a finitely repeated Prisoner's Dilemma (PD) and a Battle of the Sexes (BoS) game against either a base or chain-of-thought ("Prompted") GPT-4, over 20 rounds (10 PD + 10 BoS, counterbalanced). On each round participants made a binary option choice (0/1) and received a per-round payoff (score); after each game they gave an opponent-belief judgment (whether they thought the other player was human or an LLM), stored as a response row of its own. The source also ships a per-round coordination flag the authors derived from the outcome. The research question is how LLMs behave and cooperate in repeated social interactions relative to humans, prominently showing that chain-of-thought-prompted GPT-4 elicits better scores and more successful coordination from human partners than base GPT-4.

## Notes

### Columns

#### exp0
| column | description |
|--------|-------------|
| participant_id | Original subject number from source CSV `repgames.csv` (1..195), already anonymized by the authors. |
| task_id | 0 = the game played first, 1 = the game played second (file order; each game is a fresh start with a new opponent, new rules and a cleared history). Order is counterbalanced: 97 participants played PD first, 98 BoS first. |
| trial | 0..10 within each (participant_id, task_id): rounds 0..9 in presentation order, then the opponent guess at 10; the raw file has no trial column, so numbered in file order. |
| response | On `game` rows the participant's binary game choice, 0 = option F, 1 = option J (source `action`, coded 0/1). On `opponent_guess` rows the verbatim guess, `Human` or `LLM`. |
| block | Game type: 0 = Prisoner's Dilemma (PD), 1 = Battle of the Sexes (BoS); constant within a task_id. The guess row after a game carries that game's block. |
| reward | Per-round payoff received (source `score`): PD values {0,5,8,10}, BoS values {0,7,10}. Left in source units, not recoded. Empty on `opponent_guess` rows. |
| condition | Opposing LLM prompt variant (source `opponent`): `base` = GPT-4 base, `prompted` = chain-of-thought ("Prompted") GPT-4; between-subject. |
| guess | The participant's opponent-belief judgment for the game the row belongs to (source `guess`): `Human` or `LLM`. Asked once after each game, so constant within a game and repeated on its rows. |
| coordination | Outcome flag derived by the authors (source `coordination`), 0 or 1. It follows their analysis coding: PD = 1 when both players chose F (reward 5), BoS = 1 when both chose the same option (reward 7 or 10); 29 of 3900 source rows deviate from that rule and are kept as shipped. Empty on `opponent_guess` rows. |
| valid | Always 1; every recorded round is usable (no source validity flags). |
| phase | `game` for the 20 per-round choices, `opponent_guess` for the two post-game human-or-LLM guesses. |

The dataset contains only the human behavioral experiment from the paper. The LLM simulation/play data (in the `all_games`, `pd`, and `bos` directories of the source repo) is omitted here, as it is model output rather than human behavioral data. `task_id` numbers the two games in presentation order; `block` gives the game type.

## Online experiment

`experiments/exp0/` builds a runnable static jsPsych v8 of the study (two repeated games vs GPT-4, order counterbalanced) that saves a CSV in this dataset's exact `exp0` schema. The headless round trip (`?mode=simulate`) passed all schema checks (columns, dtypes/codings, 20 rows/session, per-game guess, derived coordination); no outbound requests fired. The opponent's moves come from the canned GPT-4 lookup tables shipped with the original task code, so a fresh session is internally consistent but will not re-match the live-GPT-4 rewards in `exp0.csv`. Cosmetic defaults chosen: 1500 ms feedback, 500 ms ITI (the 20 s response window and comprehension gate reproduce the source).

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

`simulate0.py` simulates the full session (two repeated games vs GPT-4, order counterbalanced) with the format-identical round trip through `build_jsonl.py` passing. The opponent's moves come from the shipped GPT-4 lookup tables (temperature-0 canned strategy) with the participant's base/prompted table fixed for the session as the paper describes; the source task code re-drew that table on every round, so simulated rewards are internally consistent but need not re-match the values in `exp0.csv`; `coordination` follows the source analysis coding (PD: reward == 5; BoS: reward != 0). No experiment skipped.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Text-format conversion

`exp0.csv` was transcribed to `transcripts0.jsonl` (195 transcripts, one per participant). The whole session is textifiable: each round is a binary choice between the named options F and J (typed F/J), followed by the points won, and each game ends with a free human-or-LLM guess. The repeated games preserve their order and rules exactly as presented; no experiment was skipped.

Sample transcript (start up to the first marked response):

```
You are going to play two games against an artificial agent or another fellow human. Your opponent is randomly assigned and changes at the start of each game. Your goal is to gain as many points as possible in both games.
Each game is a 2x2 game played with 2 players: you and the other player each choose between two options, Option F and Option J. Each game consists of 10 rounds. On each round, choose one of the two options by typing F or J (type F to choose Option F, J to choose Option J). You have 20 seconds to choose.
After each game you will be asked whether you think your opponent was a human or an artificial agent; answer by typing Human or LLM.
The game is a Prisoner's Dilemma. The rules are:
If you choose J and the other player chooses J, you win 8 points and the other wins 8 points.
If you choose J and the other player chooses F, you win 0 points and the other wins 10 points.
If you choose F and the other player chooses J, you win 10 points and the other wins 0 points.
If you choose F and the other player chooses F, you win 5 points and the other wins 5 points.
You will play 10 rounds.
Round 1: you press [HUMAN_RESPONSE]F[/HUMAN_RESPONSE] …
```

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Verification

Verdict: pass (critical 1, major 3, minor 7; fixed 6, open 5).

Checked: paper (https://doi.org/10.1038/s41562-025-02172-y, PDF), original data (https://github.com/eliaka/repeatedgames, human_experiment/analysis/repgames.csv and the task code), exp0, transform re-run, transcripts, simulators, analysis, logs. Skipped: none.

Fixed:
- exp0.csv used `block` (0 = PD, 1 = BoS) as the only game index; 98 participants played BoS first, so the block order was not the presentation order and the transcript tokens did not map onto the CSV rows for 92/195 participants. Each game is a fresh start, so transform.py now writes `task_id` (0 = first game played, 1 = second) with `trial` restarting at 0 per game; `block` stays the game type. exp0.csv regenerated, build_jsonl.py sorts by task_id then trial, simulate0.py emits task_id; transcripts0.jsonl unchanged byte for byte.
- The post-game human-or-LLM guess was marked as a response in every transcript (22 per participant) but exp0.csv had only the 20 round rows with the guess as a column. transform.py now adds one `opponent_guess` row after each game (response = Human/LLM, reward and coordination empty, new `phase` column); build_jsonl.py, simulate0.py and analysis.py updated; simulator round trip passes; all three analysis effects reproduce.
- README Experiment summary said participants gave 'an explicit per-round coordination measure'; `coordination` is an outcome flag the authors derived (their R script: PD = both F, BoS = same option). Column description corrected.
- README described `guess` as per-round; the question was asked once after each game (task page 'First game is over!'). Column description corrected.
- README columns heading '### exp0' changed to the template's '#### exp0'.
- README Simulators section and simulate0.py docstring said exp0.csv rewards came from live GPT-4; the source task code (script.js) reads the opponent's move from the shipped lookup tables. Wording corrected.

Open:
- minor: the source task code (script.js) re-draws the base/prompted lookup table inside begintrial(), i.e. on every round, while the paper (Fig. 7a, Methods) describes one fixed assignment per participant. The recorded scores agree: of the 1156 rounds where the two tables give different moves, 602 follow the labeled `condition` table and 551 the other; 12 rounds match neither. The data are faithful to repgames.csv.
- minor: `coordination` follows PD = both F, BoS = same option on 3871/3900 rows; 29 source rows deviate and are kept as shipped.
- minor: the paper's PD 'joint cooperation' effect (p. 1386: beta = 0.24, z = 2.54, P = 0.01) reproduces only with score == 5, which is both players choosing F (mutual defection under the displayed matrix, J/J = 8/8); score == 8 gives beta = -0.04, z = -0.45. analysis.py mirrors the authors' R coding.
- minor: the paper (p. 1387) excludes 21 participants who missed the 20 s window; the source ships only the 195 retained, so they cannot be kept with valid = 0.
- minor: transcript round feedback gives the participant's points only; the task screen also showed the other player's move, which is recoverable from the rules and the points.

Run: claude-fable-5-1, 2026-09-09
