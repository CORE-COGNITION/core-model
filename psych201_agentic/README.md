# Psych-201-agentic

The Hugging-Brain `psych-301` collections (agentically transcribed datasets) rebuilt as a
Psych-201-discrete-style dataset: button-press responses only, one participant transcript per
row, per-study train/test split. Built 2026-09-08 by `build_dataset.py`, rebuilt 2026-09-15 at the Hub commits after
the `auto-exp-verify` pass (62 of the 93 included repos changed; `needs-review` datasets are included on purpose) and
again the same day after our own fixes to 11 repos (below), and rebuilt 2026-09-16 from the fixed vandendriessche_2022
transcript (Limits, last Hub fix; same rows and presses, only that study's text changed) and, the same day, with the
source markers kept instead of ` <<X>>` (Transform); sources
and their commits are pinned in `manifest.json` (with each repo's `verification:` tag), per-study counts are in `data/build_log.json`.

## Files

- `build_dataset.py`: lists the three collections (`psych-301-pass`, `-needs-review`, `-fail`), keeps datasets tagged
  `psych-101` or `psych-201` that have `transcripts<i>.jsonl` files (minus `EXCLUDE`: pedroni_2017_risk, xiong_2023_neural),
  downloads them, applies the discrete transform, splits, writes `data/`. `--skip_download` rebuilds from `data/raw`.
- `manifest.json`: every dataset of the three collections (639 on 2026-09-15) with tags, commit, transcript files, and included / why not.
- `data/` (gitignored, 3.1 GB): `raw/<study>/transcripts<i>.jsonl` (sources), `train.jsonl`, `test.jsonl`, `build_log.json`.

Columns: `text`, `study` (Hugging-Brain dataset name), `experiment` (`<study>/exp<i>.csv`), `participant`,
`is_psych101`, `is_psych201` (tags), `n_choices` (button presses in the row), `meta` (json string of the other source fields).
Load with `load_dataset("json", data_files="psych201_agentic/data/train.jsonl")["train"]` or `utils.load_data()` (the only
training data of the repo since 2026-09-16; the text format differs from `marcelbinz/Psych-201-discrete` in the response markers only, see Transform).

## Transform

Source responses are `[HUMAN_RESPONSE]X[/HUMAN_RESPONSE]`. As in `psych201_push_to_hub.py`,
only a single uppercase letter counts as a button press, any other response keeps
its text and loses the markers, and a row without a letter response is dropped. Unlike Psych-201-discrete, the letter
responses keep the source markers (since 2026-09-16; the earlier builds wrote ` <<X>>` and normalised the space before
`<<` and stray chevrons, `letters_not_preceded_by_space` / `stray_chevrons_in_source` in old build logs). `utils.build_tokenizer`
adds `[HUMAN_RESPONSE]` and `[/HUMAN_RESPONSE]` to both tokenizers as single tokens after `PRESS_A..Z`, `utils.load_data` rewrites `[HUMAN_RESPONSE]X` to `[HUMAN_RESPONSE]PRESS_X`,
and the completion-only collator keys on the two marker tokens (`utils.MARKERS`), so the loss sits on the `PRESS_X`
token alone. The phoneme tokenizer tokenizes `press [HUMAN_RESPONSE]PRESS_A[/HUMAN_RESPONSE].` exactly like it did
`press <<PRESS_A>>.` (the space before the marker is the same word-boundary token either way, also after `(`); the BPE
tokenizer spends one extra space token per response. No source row has marker text outside a response (`stray_markers`
in the log). Checked 2026-09-16 on every row of the build: every `[HUMAN_RESPONSE]` opens a letter response and their
count equals `n_choices`; tokenized, every `PRESS_X` sits between the two marker tokens (2 rows per experiment, both tokenizers).

Excluded although tagged: `pedroni_2017_risk` is the same Basel-Berlin Risk Study as `frey_2017_risk` (verified: for all
1,507 participants its response sequence equals the concatenation of frey exp0, exp1, exp2, exp4), kept once to avoid leakage;
`xiong_2023_neural` has 33 rows of ~440k chars (~438k phoneme tokens), longer than the 304,500-token training pack
(excluded at build since 2026-09-15, dropped at load time before).

## Split

Psych-201-discrete's rule, inferred from the Hub sets (fits 90 of 103 studies; the rest lost rows after splitting):
per study, rows shuffled with seed 0, `min(100, floor(0.1 * rows))` to test, sampled at row level (a participant with
several experiments can appear in both splits, as in the original).

## Result

| | datasets | studies with presses | experiments | rows | choices |
|---|---|---|---|---|---|
| tagged in the three collections | 143 of 639 (104 pass, 14 needs-review, 25 fail) | | | | |
| with transcripts (all in `pass`) | 95 | | | | |
| included (pedroni, xiong excluded) | 93 | 62 | 137 | 83,352 of 140,999 | 7,634,315 (4,829,382 non-letter responses stripped) |
| train / test | | | | 80,452 / 2,900 | |
| Psych-201-discrete train + test | 103 studies | | 176 | 136,258 | 19,637,667 |

Largest contributors: chen_2018_agedependent 1.11M choices (26,532 rows), dubois_2022_valuefree 0.92M,
garcia_2023_experiential 0.40M, shahar_2019_improving 0.35M, flesch_2018_comparing 0.34M (anvari_2024_testing went from
0.72M to 0.26M with its verification fix; suthaharan_2021 gained 172 rows, cheung_2024 exp1/exp2 and vandendriessche_2022
became letter-only, xiong_2023 is excluded: 8.22M -> 7.63M choices).
13 of the 62 studies are not in Psych-201 (1.88M choices): chen_2018 1,114k, moutoussis_2018 207k, schulz_2020 143k,
jagadish_2023 135k, nussenbaum_2024_sensitivity 133k, christian_2026 41k, barnby_2022 38k, feherdasilva_2023 28k,
gnther_2022_patterns 22k, dentella_2023 9k, vantiel_2021 8k, cheung_2024 4k, xu_2021_novelty 3k.

## Psych-201 studies not recovered (49 of 103 studies, 89 of 176 experiments, 14.1M of 19.6M choices)

Matched by first author and year, confirmed by row and choice counts. Choice counts are the Psych-201-discrete ones.

- Not in any collection (1.57M): rutledge2023happiness 870k, frey2017cct 676k (frey_2017_risk has no Columbia Card Task),
  pirrone_unpublished_food 13k, guenther2023grammaticality 9k.
- `needs-review`, repo has `transform.py` but no data or transcripts (3.00M): agrawal2024stress 1,767k, gillan2016 944k,
  awad2018moral 196k, hu2023lmpragmatics 63k, rosenbaum2022 13k, busch2024_navon 8k, palminteri2017 8k, frankedegen2016 2k.
- `fail`, README only, "no public data" although Psych-101 had trial-level data (3.44M): peterson2021using 1,214k,
  wulff2018sampling 1,124k, wulff2018description 31k, sandbrink2024 265k, aggarwal2023iag 216k, wilson2014humans 157k,
  nasioulas2024 144k, zhu2024games 93k, somerville2017 52k, gershman2020reward 47k, ludwig2023 37k, potter2017 22k,
  waltz2020 16k, lefebvre2017 8k, hilbig2014 8k, speekenbrink2008 5k, thoma2025riskychoice 3k.
- `pass` but `text-format:fail`, CSV without transcripts (3.52M): hebart2023things 2,877k, enkavi2019 x4 447k,
  pirrone_2018_dots 76k, phaneuf-hadd_2025 71k, spektor2019 35k, marshall_2022 12k.
- Transcripts exist but responses are not single letters, recoverable by re-lettering (2.57M): frey2017risk (BART as pump
  counts) 1,690k, tomov2020 + tomov2021 (station ids) 335k, ruggeri2022 (verbal options) 158k, anllo2024 (left/right) 142k,
  pike2023 (pump counts) 129k, nussenbaum2020twostep (0/1) 60k, bavard2023 (cue ids) 37k, popov2023, baar2022, franke2024 24k.
- Present but smaller (0.56M lost): frey2017dfe 330k to 12k (only the 8 final choices, no sampling presses),
  krueger2022 280k to 85k (mouselab reveals stripped), suthaharan2021 loses 246 participants, decker2016 loses 21.

Two matches rest on identical counts: plonsky2018when = plonsky_2025_predicting exp0 (240 rows, 180,000 choices),
pirrone_unpublished_lottery = pirrone_2024_subjective (62 rows, 27,900 choices).

## Simulators and analyses (CoreModel)

The source repos ship one text simulator per experiment (`simulate<i>.py`, class with
`simulate(agent, n, max_chars)` returning `(df, prompts)`, prompts in the source format) and one
`analysis.py` per study (`EFFECTS` list of checks on `{exp: DataFrame}`). Set up 2026-09-09, refreshed 2026-09-15
at the verified commits (99 of 135 script copies changed, cheung_2024 exp1/exp2 new); verbatim copies, nothing changed on the Hub:

- `fetch_hf_scripts.py [--with_csv [study ...]]`: downloads them at the manifest commit into `hf/<study>/`
  (136 simulators, 93 analyses; the human `exp<i>.csv` only on request, 1.3 GB for the 45 candidate studies, gitignored)
  and writes `experiments.json` (index, study, exp, task class, participants, presses, non-letter responses).
- `simulate_core.py <model_dir> --selected | --index i | --experiment study/exp<i> | --all`: runs the simulators with a
  `run_core.py` checkpoint (`--random`: uniform agent, no model). The decision-time prompt is rewritten
  exactly as training saw it: `build_dataset.to_discrete`, then `[HUMAN_RESPONSE]X` -> `[HUMAN_RESPONSE]PRESS_X` (`utils.load_data`),
  ending in the `[HUMAN_RESPONSE]` cue (checked 2026-09-15 on every call of a random-agent run of all 136 experiments: the cue plus
  the response is a prefix of the participant's final training text, and one call per marked response; 134 pass after
  the Hub fixes below, cox_2018's recall misses and xu_2021's endless loop remain).
  Participants per experiment = source count capped at 1000 (14,361 of 42,932). Since 2026-09-17 the agent continues a prompt that
  extends the previous call's prompt from the stored memory state (fla recurrent-state cache), tokenizing only the new text, so a
  participant costs one pass over their transcript instead of one per choice (`--no-cache`: the old agent; `--check_cache N`, default
  10, also runs the first N calls of each experiment uncached and records the largest logit difference in the json; tokenizing in
  increments is exact for both tokenizers, 0 mismatches on 184 test transcripts). Writes `results_simulations/experiment=<study>_<exp>_agent=<agent>.{csv,jsonl,json,_latents.pth}`.
- `score_agentic.py --agent <agent> | --human`: runs each study's `analysis.py` effects on those CSVs (or on
  the human CSVs), reports the curated effects (below; `--all_effects` for every effect), writes
  `results_effects/<agent>.{json,md}`. Human data of the 45 studies with a letter-only experiment (2026-09-15):
  133 / 133 effects that run reproduce; the bavard_2021 and zorowitz_2023 analyses error on their own CSVs
  (`pid` / `stay` columns missing).

### Selection (2026-09-16; first made 2026-09-09)

`experiments.json` marks 47 experiments of 32 studies `selected`, with the usable `effects` (74 experiment-effect pairs,
66 distinct study-effect pairs); every other entry carries a `note` with the reason. Criteria, checked with a random agent
(uncapped, seed 0): (1) the source transcript has no stripped non-letter response and the simulator only ever asks for
single letters (91 of 136; 18 ask free text, 26 numbers or words, xu_2021 never ends); (2) on every call the `[HUMAN_RESPONSE]` cue
built from the decision-time prompt, plus the response, is a prefix of the participant's final text as training saw
it, with one agent call per marked response (all 91, after the fixes below; before them 14 failed: olschewski_2024 x6,
kool_2017 x2, jansen x2, heffner called the agent before narrating the trial, steingroever x3 and suthaharan x2 stated
the chosen deck before the marker, `You pick deck A. You press <<A>>`, which also gave the press away in training,
levering on 12 calls, and thoma_2025 never called the agent: every choice was `np.random.choice`); (3) the effect runs on
the simulator's own output (30 participants) and none of the columns it depends on (found by dropping columns one at
a time) is a reaction time, age, gender, rating, a clinical group the simulator assigns at random, or constant in the
simulation other than `valid`; (4) the effect reproduces on the study's human CSVs (`score_agentic.py --human`): 64 / 64.
Of the 91: 43 have no effect at all or only effects that error on simulator output or use age/rt/group.
`fetch_hf_scripts.py` keeps the selection fields when it regenerates the file.

Changes vs 2026-09-09 (46 experiments, 66 effects): olschewski_2024 exp0-2 (3 effects), steingroever exp1 (2) and
thoma_2025 exp0 (1) failed criterion (2), which had not been checked before (their 0809 simulations are affected;
thoma's are random behaviour), and are back in after the Hub fixes;
cheung_2024 exp1/exp2 (framing effects, letter-only since the verification) added; vandendriessche_2022 exp0
(`learning_accuracy_above_chance`; its two other effects need the clinical group) added 2026-09-16 after our fix of its
learning-phase transcript (Limits): before it the text never identified the symbols, so nothing could be predicted.

Removed 2026-09-21 (49 -> 48 experiments, 69 -> 67 effects): dezfouli_2019
`reward_decreases_stay` (needs a null in the bipolar group, which the simulator assigns at random and never shows to the
agent, criterion 3) and pirrone_2024 `variance_preference_magnitude` (its only effect, so exp0 is deselected: effect of
~1e-4, reproduces on only 75 % of participant-resampled human data).

Removed 2026-09-29 (48 -> 47 experiments, 33 -> 32 studies): dezfouli_2019
`best_action_above_chance` (needs the effect in each of the three clinical groups, which the simulator assigns at random
and never shows to the agent, criterion 3). It was the study's only effect, so exp0 is deselected.

No char cap (2026-09-09; the option itself removed 2026-09-16): `run_core.py` and the baselines train and evaluate on the
full transcripts and `simulate_core.py` runs every participant to the end of the experiment (the Hub simulators'
`max_chars` argument is never set). Rows of the 2026-09-15 build: max 236,116 chars (dubois_2022, ~203k phoneme
tokens), 99th percentile 134,634, median 8,678; the longest selected simulation prompt is 276,450 chars (dubois).

Limits (all from the source scripts; counts from a `--random --on_nonletter random --all -n 3` sweep):
- The model only emits `PRESS_A..Z`. 18 experiments ask for free text (`choice_options=None`: cox_2018,
  evangelidis_2022 exp2-3, flesch_2018 exp2-3, garcia_2023 x9, gunadi_2022 exp2-5) and 26 for numbers or words
  in some calls (akata_2025, barnby_2022, bavard_2018 x2, cheung_2024 exp0, ciranka_2025, evangelidis_2022 exp1,
  fan_2022 exp1, heffner_2022, jansen_2021 x2, krueger_2024 x2, levering_2019, nussenbaum_2024 x2, schulz_2020 x5,
  singh_2019 x3, witte_2024_how, xu_2023): such a call raises and the experiment is skipped; `--on_nonletter random`
  answers the call at random instead (count in the run json). 91 experiments run fully with letters; they are
  exactly the ones whose transcripts have no stripped response.
- Hub fixes pushed 2026-09-15 (one commit per repo, simulators mirrored, CSVs untouched, `## Verification` sections
  untouched): simulators asked the agent before the trial text (olschewski_2024 x7, kool_2017 x2, jansen x2,
  heffner x4 line break, gunadi exp5, cox free recall) or never at all (thoma_2025); transcripts stated the choice
  before the marker (steingroever x3, suthaharan x2, levering paired-typicality line: `build_jsonl.py` changed and
  the transcripts rebuilt, press counts unchanged); barnby offered raw option strings but wrote canonical labels.
  Not fixed: cox's recall misses roll the cue back by design; xu_2021 loops until a goal.
- Hub fix 2026-09-16 (vandendriessche_2022_contextual, the one fix that changes a CSV): the learning lines said only
  `Rich context. Two abstract symbols appear.`, so neither the symbols nor the better one's side could be read from
  the text and the model could not track symbol values in either phase (test NLL 0.567 vs 0.693 chance in the 1509
  run); the rich/poor labels also told the reader what participants were never told. The ids are recoverable: the
  transfer ids 1-8 index the session stimulus lists in a fixed order and the authors' `data_depression.Rmd`
  harmonises them (poor pair (1,2) / (5,6), rich pair (3,4) / (7,8), the odd id is the better option; good learners
  prefer the odd id in the transfer phase: 3 vs 4 20/21, 5 vs 6 14/14, 7 vs 8 27/27), and `correct` says whether the
  chosen side held the better one (the `.mat` `gain` schedule reproduces `feedback` on all 11,200 trials). `transform.py`
  now fills `symbol_left` / `symbol_right` for the learning rows (no other cell changes, the three effects unchanged),
  `build_jsonl.py` writes `Options: symbol 4 (left), symbol 3 (right). You press [HUMAN_RESPONSE]B[/HUMAN_RESPONSE] (left:
  symbol 4). You get +1
  point (green smiley).` and describes two fixed pairs per session instead of contexts; `simulate0.py` mirrored (round
  trip byte-identical, `check_calls.py` passes); presses unchanged (56 rows, 17,472). The Hub commit was pending when this was written:
  `manifest.json` still pins f90904b7 while `data/raw/vandendriessche_2022_contextual/transcripts0.jsonl` and
  `hf/vandendriessche_2022_contextual/{simulate0.py,exp0.csv}` are the fixed files; re-run `build_dataset.py` and
  `fetch_hf_scripts.py` after the push to re-pin.
- Hub fix 2026-09-21 (bahrami_2020_arm, simulator only, commit 25bbbb9c, re-pinned here by hand in `manifest.json`,
  `experiments.json` and `hf/bahrami_2020_arm/simulate0.py`): the study used three fixed payoff schedules (in `exp0.csv`
  `reward_c1..c4` are identical on every trial for all participants of a `version`, and the reward equals the chosen
  arm's payoff on all 139,816 answered trials), but the simulator drew a fresh Gaussian walk per participant from the
  first-trial payoffs. Its best-arm gap stayed constant, the humans' gap narrows mid-session and widens late, so
  `choice_accuracy_improves` (a property of those schedules) was not comparable. `simulate0.py` now replays the
  schedules (`PAYOFFS[version][trial]`, inline); miss rate, version assignment, columns and text unchanged (round trip
  byte-identical, `check_calls.py` passes; a random agent fails both curated effects). Transcripts, CSV and analysis
  untouched, so the training data does not change; bahrami simulations before this date used the random walks.
- xu_2021_novelty loops until a goal is reached (prompt > 400,000 chars with the random agent); run it with
  `--max_prompt_chars` so it fails loudly. olschewski_2025_optimal's simulators read the human
  `exp0/1.csv` (21 MB, `--with_csv olschewski_2025_optimal`; copy to the cluster like `data/`).
- Simulators drop columns (rt, age, ...) that some analyses need: with the random agent 49 of 174 effects
  error and 10 have no data (`results_effects/<agent>.md` lists them per effect).
