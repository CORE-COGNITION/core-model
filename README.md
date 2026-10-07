# CORE: COntextual Retrieval and Encoding

Detailed results (per-study likelihoods, behavioral effects, example transcripts):
https://core-cognition.github.io/core-model/results/

## Contents

- `run_core.py`, `run_gdn.py`, `run_transformer.py` — train, evaluate, and report one model each.
- `eval_centaur.py` — evaluation of Centaur (`marcelbinz/Llama-3.1-Centaur-70B-adapter`).
- `utils.py` (data loading, tokenizers), `packed_collator.py` (batch packing), `laplace.py` (Laplace log marginal likelihood), `reporting.py` (writes `results_reports/<run>.md`).
- `check_core_model.py` — numerical checks of the memory layer and its kernel against the equations; `bench_delta_value.py` — kernel speed.
- `flash-linear-attention-040526/` — pruned fork of [flash-linear-attention](https://github.com/fla-org/flash-linear-attention) with the `CORE` model (`fla.models.core_model`) and its Triton kernel (`fla.ops.delta_value`).
- `psych201_agentic/` — data set construction, simulation of participants, and scoring of behavioral effects (see its README).
- `plotting/` — figure scripts of the paper.
- `results_browser/` — builds the static results browser.
- `results_reports/`, `psych201_agentic/results_effects/` — the results reported in the paper.

## Installation

Python 3.13, a CUDA GPU (training used one NVIDIA H100), and the packages
`torch`, `triton`, `transformers`, `trl`, `datasets`, `huggingface_hub`, `einops`, `numpy`, `pandas`, `matplotlib`,
and `phonemizer` with the `espeak-ng` backend (phoneme tokenizer).

```bash
pip install -e flash-linear-attention-040526
```

## Data

The training and test sets are on the Hugging Face Hub:
[Psych-201-discrete-agentic](https://huggingface.co/datasets/marcelbinz/Psych-201-discrete-agentic) and
[Psych-201-discrete-agentic-test](https://huggingface.co/datasets/marcelbinz/Psych-201-discrete-agentic-test).
The code loads them directly from the Hub, pinned to a revision (`DATA_REPOS` in `utils.py`).
`psych201_agentic/build_dataset.py` rebuilds both splits from the source repositories.

The simulators and effect analyses of the individual studies are downloaded at pinned commits with
`python psych201_agentic/fetch_hf_scripts.py` (into `psych201_agentic/hf/`).

## Usage

Train the reference model (phonemes, 6 layers, 4 heads, delta rule, forgetting):

```bash
python run_core.py --tokenizer phoneme --num_latents 128 --num_layers 6 --num_heads 4 \
    --weight_decay 0.5 --learning_rule delta --pack_target_tokens 304500
```

Ablations: `--num_layers 1` (no hierarchy), `--no_forget_gate` (no forgetting), `--learning_rule hebbian` (no prediction errors),
`--tokenizer bpe` (no phonemes). Each run writes `trained_models/<run>/` and `results_reports/<run>.md`.

Simulate participants and score the behavioral effects:

```bash
python psych201_agentic/simulate_core.py trained_models/<run> --selected --temperature 1 --seed 0
python psych201_agentic/score_agentic.py --agent trained_<run>_temp1
```

## License

MIT (see `LICENSE`). The flash-linear-attention fork keeps its own MIT license.
