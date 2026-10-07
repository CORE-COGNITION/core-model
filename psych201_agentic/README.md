# Psych-201-agentic

The Hugging-Brain `psych-301` collections (agentically transcribed datasets) rebuilt as a
Psych-201-discrete-style dataset: button-press responses only, one participant transcript per row,
per-study train/test split. The result is on the Hugging Face Hub
([train](https://huggingface.co/datasets/marcelbinz/Psych-201-discrete-agentic),
[test](https://huggingface.co/datasets/marcelbinz/Psych-201-discrete-agentic-test)); `utils.load_split` loads it.

## Files

- `build_dataset.py`: lists the three collections (`psych-301-pass`, `-needs-review`, `-fail`), keeps datasets tagged
  `psych-101` or `psych-201` that have `transcripts<i>.jsonl` files, downloads them at the pinned commits,
  applies the transform, splits, and writes `data/` (`train.jsonl`, `test.jsonl`, `build_log.json`).
- `manifest.json`: every dataset of the three collections with tags, pinned commit, transcript files, and whether it is included.
- `hf/<study>/`: each study's simulators (`simulate<i>.py`), effect analyses (`analysis.py`), and dataset card (`README.md`),
  as used in the paper. They are copies of the Hugging-Brain repositories at the commits pinned in `manifest.json`,
  except for one local fix (see Known limits).
- `fetch_hf_scripts.py`: downloads `hf/` again from the Hub and writes `experiments.json` (needs `data/build_log.json`
  from `build_dataset.py`).
- `experiments.json`: one entry per experiment with a simulator; `selected` and `effects` mark the experiments and
  effects used in the paper, `note` gives the reason for every other entry.
- `simulate_core.py`: simulates participants with a trained model (`--selected`, `--index i`, `--experiment study/exp<i>`;
  `--random` for a uniform agent). Participants per experiment = source count, capped at 1,000.
- `score_agentic.py`: runs each study's effects on the simulated data (`--agent <agent>`) or the human data (`--human`)
  and writes `results_effects/<agent>.{json,md}`.
- `replay_channels.py`: replays simulated transcripts and records the gates of every channel (Fig. 3C-D).

Columns: `text`, `study`, `experiment` (`<study>/exp<i>.csv`), `participant`, `is_psych101`, `is_psych201`,
`n_choices` (button presses in the row), `meta` (json string of the other source fields).

## Transform and split

Source responses are `[HUMAN_RESPONSE]X[/HUMAN_RESPONSE]`. Only a single uppercase letter counts as a button press;
any other response keeps its text and loses the markers, and a row without a letter response is dropped.
`utils.load_data` rewrites each press to the single token `PRESS_X`, and the loss sits on that token alone.
Split: per study, rows shuffled with seed 0, `min(100, floor(0.1 * rows))` to test.
Excluded although tagged: `pedroni_2017_risk` (same participants as `frey_2017_risk`) and `xiong_2023_neural`
(rows longer than the training pack).

Result: 62 studies, 137 experiments, 83,352 sessions (80,452 train / 2,900 test), 7,634,315 choices.

## Selection

47 experiments of 32 studies are `selected`, with 67 effects. An effect is used if
(1) the experiment only asks for single letters,
(2) every prompt to the model matches the participant's transcript as seen in training,
(3) the effect does not depend on reaction times, age, gender, ratings, or a clinical group, and
(4) the effect reproduces on the study's human data (`score_agentic.py --human`).

## Known limits

- `vandendriessche_2022_contextual`: `hf/` holds a fixed simulator (`simulate0.py`) that identifies the symbols in the
  learning phase. This fix was not yet on the Hub when its commit was pinned, so `fetch_hf_scripts.py` may download the earlier version.
- `xu_2021_novelty` loops until a goal is reached; run it with `--max_prompt_chars`.
- `olschewski_2025_optimal`'s simulators read the human CSVs (`fetch_hf_scripts.py --with_csv olschewski_2025_optimal`).
