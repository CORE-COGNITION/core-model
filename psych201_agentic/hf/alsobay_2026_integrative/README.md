---
tags:
- paradigm:economic-game
- psych-201
- text-format:pass
- js-experiment:needs-review
- simulator:pass
---

# alsobay_2026_integrative

- Paper: https://doi.org/10.1126/science.aeb5280
- Data source: https://osf.io/2d56w/ (open-access OSF reproducibility package; raw + processed data for both waves, config files, and prediction survey)
- Full text: Paywalled (Science). PDF reconstructed from the abstract only; raw data served as the primary source of truth.
- Run: openrouter/deepseek/deepseek-v4-flash-0731, before 2026-08-24

## Citation
Alsobay, M., Rand, D. G., Watts, D. J., & Almaatouq, A. (2026). Integrative experiments identify how punishment affects welfare in public goods games. Science, 388(…). doi:10.1126/science.aeb5280

## Experiment summary
Two large online public-goods-game waves (a learning wave and a validation wave; exp0 and exp1 here) spanning ~7,100 participants and ~147,000 decisions vary 14 design parameters across 360 conditions. In each game, players repeatedly contribute coins to a public fund (response, 0–20 coins per round) and may spend coins to punish and/or reward other players, with manipulations of communication (chat), game length, outcome visibility, and the cost/magnitude of reward and punishment technologies. N = 3,958 (learning) and 4,083 (validation). The central research question is which game features determine whether peer punishment enhances or reduces social welfare.

## Notes

### Columns

### exp0
| column | description |
|--------|-------------|
| participant_id | Anonymized random Empirica playerId (20-char alphanumeric); not a platform/worker ID |
| trial | 0..N round index within each participant (presentation order) |
| response | Player's per-round contribution to the public fund in coins (0..20); empty where no contribution was recorded |
| _id | Raw player-round record id from source |
| batchId | Batch (session run) id the game was launched in |
| playerId | Same anonymized player id as participant_id |
| roundId | Id of the PGG round |
| gameId | Id of the public-goods game (one game per participant) |
| createdAt | Round start timestamp (ISO 8601) |
| punishedBy | JSON object {punisherPlayerId: coins} punishing this player this round |
| punished | JSON object {targetPlayerId: coins} this player spent punishing others this round |
| rewardedBy | JSON object {rewarderPlayerId: coins} rewarding this player this round |
| rewarded | JSON object {targetPlayerId: coins} this player spent rewarding others this round |
| contribution | Same as response (coin amount contributed) |
| costs | Total coins the player spent on punishment this round |
| penalties | Total coins the player received as punishment this round |
| rewards | Total coins the player received as reward this round |
| remainingEndowment | Coins the player kept from the round endowment |
| roundPayoff | Player's resulting payoff that round (coins) |
| treatmentId | Id of the treatment (design-factor combination) assigned to the game |
| treatmentName | Treatment label e.g. `NN_T` / `NN_C` (N=configId, C=control, T=punishment) |
| configId | Design-config id into the wave's config table |
| playerCount | Number of players in the game (design factor) |
| numRounds | Number of rounds in the game (design factor) |
| showNRounds | Whether total round count is shown to players (bool, design factor) |
| endowment | Coins given each round (design factor, always 20 here) |
| multiplier | Multiplier on total contribution to public fund (design factor) |
| allOrNothing | Whether players must contribute all or nothing (bool, design factor) |
| chat | Whether players could chat (bool, design factor) |
| defaultContribProp | Default contribution proportion (design factor) |
| punishmentExists | Whether punishment technology was available (bool, design factor) |
| punishmentCost | Cost in coins per punishment imposed (design factor) |
| punishmentMagnitude | Coins deducted per punishment inflicted (design factor) |
| rewardExists | Whether reward technology was available (bool, design factor) |
| rewardCost | Cost in coins per reward granted (design factor) |
| rewardMagnitude | Coins added per reward granted (design factor) |
| showOtherSummaries | Whether others' round summaries are shown (bool, design factor) |
| showPunishmentId | Whether punisher identity is shown (bool, design factor) |
| showRewardId | Whether rewarder identity is shown (bool, design factor) |
| contributionDuration | Allowed contribution-stage seconds (design factor) |
| outcomeDuration | Allowed outcome-stage seconds (design factor) |
| summaryDuration | Allowed summary-stage seconds (design factor) |
| basePay | Flat participation pay (design factor) |
| conversionRate | Coins-to-currency conversion rate (design factor) |

### exp1
| column | description |
|--------|-------------|
| participant_id | Anonymized random Empirica playerId (20-char alphanumeric); not a platform/worker ID |
| trial | 0..N round index within each participant (presentation order) |
| response | Player's per-round contribution to the public fund in coins (0..20); empty where no contribution was recorded |
| _id | Raw player-round record id from source |
| batchId | Batch (session run) id the game was launched in |
| playerId | Same anonymized player id as participant_id |
| roundId | Id of the PGG round |
| gameId | Id of the public-goods game (one game per participant) |
| createdAt | Round start timestamp (ISO 8601) |
| punishedBy | JSON object {punisherPlayerId: coins} punishing this player this round |
| punished | JSON object {targetPlayerId: coins} this player spent punishing others this round |
| rewardedBy | JSON object {rewarderPlayerId: coins} rewarding this player this round |
| rewarded | JSON object {targetPlayerId: coins} this player spent rewarding others this round |
| contribution | Same as response (coin amount contributed) |
| costs | Total coins the player spent on punishment this round |
| penalties | Total coins the player received as punishment this round |
| rewards | Total coins the player received as reward this round |
| remainingEndowment | Coins the player kept from the round endowment |
| roundPayoff | Player's resulting payoff that round (coins) |
| treatmentId | Id of the treatment (design-factor combination) assigned to the game |
| treatmentName | Treatment label e.g. `VALIDATION_N_T` / `VALIDATION_N_C` (N=configId, C=control, T=punishment) |
| configId | Design-config id into the wave's config table |
| playerCount | Number of players in the game (design factor) |
| numRounds | Number of rounds in the game (design factor) |
| showNRounds | Whether total round count is shown to players (bool, design factor) |
| endowment | Coins given each round (design factor, always 20 here) |
| multiplier | Multiplier on total contribution to public fund (design factor) |
| allOrNothing | Whether players must contribute all or nothing (bool, design factor) |
| chat | Whether players could chat (bool, design factor) |
| defaultContribProp | Default contribution proportion (design factor) |
| punishmentExists | Whether punishment technology was available (bool, design factor) |
| punishmentCost | Cost in coins per punishment imposed (design factor) |
| punishmentMagnitude | Coins deducted per punishment inflicted (design factor) |
| rewardExists | Whether reward technology was available (bool, design factor) |
| rewardCost | Cost in coins per reward granted (design factor) |
| rewardMagnitude | Coins added per reward granted (design factor) |
| showOtherSummaries | Whether others' round summaries are shown (bool, design factor) |
| showPunishmentId | Whether punisher identity is shown (bool, design factor) |
| showRewardId | Whether rewarder identity is shown (bool, design factor) |
| contributionDuration | Allowed contribution-stage seconds (design factor) |
| outcomeDuration | Allowed outcome-stage seconds (design factor) |
| summaryDuration | Allowed summary-stage seconds (design factor) |
| basePay | Flat participation pay (design factor) |
| conversionRate | Coins-to-currency conversion rate (design factor) |
| age | Participant's self-reported age in years (from end-of-game survey) |
| education | Participant's self-reported education category (bachelor/high-school/master/other) |
| gender | Participant's self-reported gender canonicalized to f/m/nb/na/other (free-text survey answers) |

The transformed CSVs cover both waves (exp0 = learning wave, exp1 = validation wave), one row per player-round, carrying all design-factor columns for each condition alongside per-round outcome and payoff variables. Note the transformed CSVs include only the punishment-treatment (T) games, not the no-technology control (C) games, so a direct punishment-vs-control comparison is not computable from columns alone; the reproduced headline effects are the paper's named cooperation-increasing factors (communication and game length), which reproduce with consistent signs at p < .001 / p < .03 across both waves.

## Text-format conversion

Both experiments (exp0 = learning wave, exp1 = validation wave) are a repeated
public-goods game (contribute coins, spend coins to punish/reward other players,
optional chat); both are fully textifiable and were transcribed
(`transcripts0.jsonl`, `transcripts1.jsonl`). No experiments were skipped.
The game code's instruction screens and payoffs (from the OSF Empirica platform,
osf.io/2d56w) drove the narration; paper full text is paywalled.

Sample transcript (exp0, first response):

```
Y o u   j o i n   a   g r o u p   o f   5   p l a y e r s   i n   a   r e p e a t e d   p u b l i c - g o o d s   g a m e   l a s t i n g   2 3   r o u n d s .   E a c h   r o u n d   y o u   r e c e i v e   2 0   c o i n s ,   w h i c h   y o u   m a y   k e e p   o r   c o n t r i b u t e   a l l   2 0   o f   t h e m   t o   t h e   g r o u p   p u b l i c   f u n d ,   o r   n o n e .   T h e   t o t a l   g r o u p   c o n t r i b u t i o n   i s   m u l t i p l i e d   b y   3 . 1   a n d   t h e n   p a i d   o u t   t o   e a c h   o f   t h e   5   p l a y e r s   e q u a l l y .   A f t e r   c o n t r i b u t i o n s   a r e   s h o w n ,   y o u   m a y   s p e n d   c o i n s   t o   a f f e c t   o t h e r s :   e a c h   d e d u c t i o n   u n i t   y o u   p l a c e   o n   a   p l a y e r   c o s t s   y o u   2   c o i n s   a n d   d e d u c t s   6   c o i n s   f r o m   t h e m ,   a n d   e a c h   r e w a r d   u n i t   y o u   p l a c e   o n   a   p l a y e r   c o s t s   y o u   2   c o i n s   a n d   g i v e s   t h e m   2   c o i n s .   Y o u   m a y   a l s o   c h a t   w i t h   t h e   o t h e r   p l a y e r s .   A t   t h e   e n d   y o u r   c o i n s   c o n v e r t   t o   a   c a s h   b o n u s   o f   $ 1   p e r   3 0 0   c o i n s ,   i n   a d d i t i o n   t o   y o u r   f l a t   p a r t i c i p a t i o n   f e e .   B e f o r e   t h e   g a m e   y o u   a n s w e r   c o m p r e h e n s i o n   q u e s t i o n s   a b o u t   t h e s e   r u l e s   a n d   t y p e   A G R E E   t o   c o n f i r m   y o u   w i l l   s t a y   f o r   t h e   w h o l e   g a m e .   O n   t h e   c o n t r i b u t i o n   s t a g e ,   t y p e   t h e   n u m b e r   o f   c o i n s   y o u   c o n t r i b u t e ;   i n   t h e   o u t c o m e   s t a g e ,   w h e n   y o u   a f f e c t   a n o t h e r   p l a y e r ,   t y p e   t h e   n u m b e r   o f   d e d u c t i o n   o r   r e w a r d   u n i t s   y o u   p l a c e   o n   t h e m .
Round 1: you keep 20 coins and contribute [HUMAN_RESPONSE]0[/HUMAN_RESPONSE] …
```

## Online experiment

Both experiments (exp0 = learning wave, exp1 = validation wave) got a static jsPsych v8
build at `experiments/exp0/` and `experiments/exp1/`; the headless round trip passed for
both — each generated CSV matches its `expN.csv` schema exactly (column names, dtypes,
codings; numRounds rows per participant; integer-rounded payoffs) and the visual check
found no gross rendering breakage. `needs-review` because there is no `simulateN.py` and
the paper full text is paywalled, so each build implements one replayed condition (the
participant plays a single real game; co-players' contributions and their punishment/reward
of the seat are replayed verbatim from `expN.csv` rather than generated) — an assumption
about the reward/feedback process and condition scope. See `experiments/README.md`.

Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25

## Simulators

Both experiments got a text simulator: `simulate0.py` (learning wave) and `simulate1.py` (validation wave). Each simulates one repeated public-goods game per participant: free responses are the per-round contribution and the per-other-player deduction/reward units (typed as numbers, exactly as in `build_jsonl.py`); co-players' contributions and their units on this seat are the generated environment driving each round's payouts. The headless round trip through `build_jsonl.py` passed for both — regenerated transcripts are byte-identical to the simulators' prompts. `ASSUMPTION:` co-player contributions/reward and punishment of this seat are drawn from simple distributions (uniform 0..endowment contributions; reward/punishment arrivals at small probabilities), and design factors are sampled from the ranges observed in the CSVs (the paper full text is paywalled); the payout arithmetic and narration are exact.
Run: openrouter/deepseek/deepseek-v4-flash-0731, 2026-08-25
