"""Simulate the Psych-201-agentic experiments with a CoreModel trained by run_core.py.

The simulators are the Hugging-Brain ones fetched by fetch_hf_scripts.py into hf/<study>/
(inventory: experiments.json). They narrate in the source format, i.e. every response is
`[HUMAN_RESPONSE]X[/HUMAN_RESPONSE]` and the prompt handed to `agent(prompt, choice_options)`
ends where the response goes (most end with the open `[HUMAN_RESPONSE]`, some add the marker
after the call). The agent rewrites the prompt into what the model saw in training (the
build_dataset.to_discrete transform, then `[HUMAN_RESPONSE]X[/HUMAN_RESPONSE]` ->
`[HUMAN_RESPONSE]PRESS_X[/HUMAN_RESPONSE]` as in utils.load_data) and ends it with the
`[HUMAN_RESPONSE]` cue, so the model predicts the next PRESS_* class.

The agent keeps the memory state of the previous call (fla's recurrent-state cache): when a prompt
extends the previous one, as every call but the first of a participant does, only the new text is
tokenized and run from the stored state, so a participant costs one pass over their transcript
instead of one pass per choice. Tokenizing in these increments is exact (each increment starts with
a PRESS_* token and the stored text ends with the cue token, and both tokenizers phonemize/merge the
text between special tokens independently; verified on 184 test transcripts of all studies).
--check_cache N recomputes the first N calls of every experiment without the cache and records the
largest logit difference in the run's json (bf16 rounding of the chunk vs recurrent kernels, ~1e-2);
--no-cache is the old one-full-pass-per-call agent.

The model only emits PRESS_A..Z. A call whose options are not single uppercase letters
(free text, numbers, words) raises UnsupportedChoice and the experiment is skipped
(--on_nonletter random answers such calls uniformly at random instead, counted in the run's
json). Every participant runs to the end of the experiment (no character cap anywhere);
--max_prompt_chars makes a prompt longer than that raise PromptTooLong and fail the experiment
loudly (a guard against runaway simulators such as xu_2021's endless loop).

Outputs (per experiment, in --out_dir):
  experiment=<study>_<exp>_agent=<agent>.csv           the simulator's DataFrame
  experiment=<study>_<exp>_agent=<agent>.jsonl         one {"participant", "text"} per participant, source format
  experiment=<study>_<exp>_agent=<agent>.json          run metadata (args, seconds, agent calls, cache stats, status)
  experiment=<study>_<exp>_agent=<agent>_latents.pth   per-token gates of the replayed prompts (--save-latents, default on)

Which experiments are worth simulating is curated in experiments.json ("selected", with the
usable "effects"; the README's "Selection" section says how): --selected runs exactly those.

Usage:
  python psych201_agentic/simulate_core.py --list
  python psych201_agentic/simulate_core.py trained_models/<run> --selected --temperature 1 --seed 0
  python psych201_agentic/simulate_core.py trained_models/<run> --index 3 --temperature 1 --seed 0
  python psych201_agentic/simulate_core.py trained_models/<run> --experiment kool_2016_when/exp0 -n 5
  python psych201_agentic/simulate_core.py --random --index 3 -n 2          # no model; smoke test
"""
import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

import argparse
import importlib.util
import json
import random
import re
import string
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)   # utils.py
sys.path.insert(0, HERE)   # build_dataset.py
from build_dataset import to_discrete  # noqa: E402

OPEN = "[HUMAN_RESPONSE]"
CLOSE = "[/HUMAN_RESPONSE]"
CLOSED_LETTER = re.compile(r"\[HUMAN_RESPONSE\]([A-Z])\[/HUMAN_RESPONSE\]")
DEFAULT_OUT_DIR = os.path.join(HERE, "results_simulations")


class UnsupportedChoice(ValueError):
    """The simulator asked for a response the model cannot give (not single A-Z letters)."""


class PromptTooLong(RuntimeError):
    """The simulator's prompt exceeded --max_prompt_chars."""


def training_text(text):
    """Source-format text -> the text the model was trained on (build_dataset.to_discrete, then
    `[HUMAN_RESPONSE]X[/HUMAN_RESPONSE]` -> `[HUMAN_RESPONSE]PRESS_X[/HUMAN_RESPONSE]` as
    utils.load_data does; the char cap of training is not applied)."""
    return CLOSED_LETTER.sub(f"{OPEN}PRESS_\\1{CLOSE}", to_discrete(text)[0])


def cue_text(prompt):
    """Simulator prompt at decision time -> model input ending with the `[HUMAN_RESPONSE]` cue of
    the next response (a trailing open marker of the prompt is dropped first, so the cue is
    placed exactly once)."""
    if prompt.endswith(OPEN):
        prompt = prompt[: -len(OPEN)]
    return training_text(prompt) + OPEN


def is_letter_options(choice_options):
    return choice_options is not None and len(list(choice_options)) > 0 and all(
        isinstance(c, str) and len(c) == 1 and c in string.ascii_uppercase for c in choice_options)


class TrainedAgent:
    """A CoreModelForCausalLM checkpoint as a choice-emitting agent (see simulate_core.py).

    The lm_head is restricted to the 26 PRESS_* classes (A..Z order), so logits[..., i] scores
    letter chr(ord('A') + i). A prompt that extends the previous call's prompt is continued from the
    stored memory state (see the module docstring); any other prompt is run in full.
    """

    def __init__(self, model_path, tokenizer_kind=None, device=None, dtype="bf16", temperature=1.0,
                 greedy=False, seed=None, max_prompt_chars=None, on_nonletter="fail",
                 use_cache=True, check_cache=10):
        import torch
        from fla.models import CoreModelForCausalLM
        from utils import build_tokenizer, infer_tokenizer_name, latest_checkpoint

        self.torch = torch
        self.temperature = temperature
        self.greedy = greedy
        self.max_prompt_chars = max_prompt_chars
        self.on_nonletter = on_nonletter
        self.n_calls = 0
        self.n_nonletter = 0
        self.fallback_rng = random.Random(seed)  # own stream: must not touch the simulators' RNG

        ckpt_tag = os.path.basename(os.path.normpath(model_path))
        decode = "greedy" if greedy else f"temp{temperature:g}"
        self.name = f"trained_{ckpt_tag}_{decode}"

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        tokenizer_kind = tokenizer_kind or infer_tokenizer_name(model_path)
        print(f"Tokenizer: {tokenizer_kind}")
        self.tokenizer = build_tokenizer(tokenizer_kind)

        # run_core.py saves the final (schedule-free eval-mode) weights at the top level after training
        # and evaluates those; fall back to the newest checkpoint-N of an unfinished run.
        resolved = model_path if os.path.exists(os.path.join(model_path, "config.json")) else latest_checkpoint(model_path)
        print(f"Loading model from: {resolved}")
        kwargs = {"torch_dtype": torch.bfloat16} if dtype == "bf16" else {}
        self.model = CoreModelForCausalLM.from_pretrained(resolved, **kwargs)
        if self.model.num_response_classes != 26:
            raise RuntimeError(f"expected 26 response classes (PRESS_A..Z), got {self.model.num_response_classes}")
        self.model.to(self.device)
        self.model.eval()

        self.generator = None
        if seed is not None:
            self.generator = torch.Generator(device=self.device).manual_seed(seed)

        self.use_cache = use_cache
        self.check_cache = check_cache      # calls per experiment that are also run without the cache
        self.cache_text = None              # model input of the previous call (ends with the cue)
        self.cache_state = None             # fla Cache: memory state of every layer after cache_text
        self.cache_logits = None            # class logits after cache_text
        self.n_hits = self.n_misses = 0
        self.reset_cache_stats()

    def reset_cache_stats(self):
        """Forget the stored state and restart the --check_cache self-test (called per experiment)."""
        self.cache_text = self.cache_state = self.cache_logits = None
        self.checked_calls = 0
        self.max_logit_diff = 0.0

    def class_logits(self, text, cached=None):
        """Logits over the 26 PRESS_* classes after `text` (the model input, ending with the cue).
        With the cache, only the part of `text` beyond the previous call's input is tokenized and run,
        starting from the stored memory state; otherwise the whole text is run from the empty state."""
        torch = self.torch
        cached = self.use_cache if cached is None else cached
        hit = cached and self.cache_text is not None and text.startswith(self.cache_text)
        if hit and len(text) == len(self.cache_text):
            self.n_hits += 1                # the same prompt again: nothing new to read in
            return self.cache_logits
        if hit:
            # the increment starts with a special token (PRESS_X) and the stored text ends with one (the cue),
            # so its tokens are exactly those of the full prompt beyond the stored text
            increment = text[len(self.cache_text):]
            input_ids = self.tokenizer(increment, add_special_tokens=False, return_tensors="pt").input_ids
        else:
            input_ids = self.tokenizer(text, return_tensors="pt").input_ids    # as in training (utils.load_data)
        with torch.no_grad():
            out = self.model(input_ids=input_ids.to(self.device), past_key_values=self.cache_state if hit else None,
                             use_cache=cached, logits_to_keep=1)
        logits = out.logits[0, -1]
        if cached:
            self.cache_text, self.cache_state, self.cache_logits = text, out.past_key_values, logits
            self.n_hits += int(hit)
            self.n_misses += int(not hit)
        return logits

    def __call__(self, prompt, choice_options=None):
        torch = self.torch
        self.n_calls += 1
        if not is_letter_options(choice_options):
            if self.on_nonletter == "random" and choice_options is not None and len(list(choice_options)) > 0:
                self.n_nonletter += 1
                return self.fallback_rng.choice(list(choice_options))
            raise UnsupportedChoice(f"choice options {choice_options!r} are not single A-Z letters; "
                                    "the model only emits PRESS_A..Z")
        if self.max_prompt_chars is not None and len(prompt) > self.max_prompt_chars:
            raise PromptTooLong(f"prompt has {len(prompt)} chars > --max_prompt_chars {self.max_prompt_chars}")
        options = list(choice_options)
        class_indices = torch.tensor([ord(c) - ord("A") for c in options], dtype=torch.long, device=self.device)

        text = cue_text(prompt)
        logits = self.class_logits(text)
        if self.use_cache and self.checked_calls < self.check_cache:
            self.checked_calls += 1
            reference = self.class_logits(text, cached=False)
            self.max_logit_diff = max(self.max_logit_diff, float((logits.float() - reference.float()).abs().max()))
        choice_logits = logits[class_indices]
        if self.greedy:
            idx = int(choice_logits.argmax().item())
        else:
            probs = torch.softmax(choice_logits.float() / self.temperature, dim=-1)
            idx = int(torch.multinomial(probs, num_samples=1, generator=self.generator).item())
        return options[idx]


class RandomAgent:
    """Uniform over the letter options, with the model agent's --on_nonletter and --max_prompt_chars
    rules; for smoke tests without a model."""

    def __init__(self, seed=None, max_prompt_chars=None, on_nonletter="fail"):
        self.name = "random_agent"
        self.rng = random.Random(seed)
        self.max_prompt_chars = max_prompt_chars
        self.on_nonletter = on_nonletter
        self.n_calls = 0
        self.n_nonletter = 0

    def __call__(self, prompt, choice_options=None):
        self.n_calls += 1
        if not is_letter_options(choice_options):
            if self.on_nonletter == "random" and choice_options is not None and len(list(choice_options)) > 0:
                self.n_nonletter += 1
                return self.rng.choice(list(choice_options))
            raise UnsupportedChoice(f"choice options {choice_options!r} are not single A-Z letters")
        if self.max_prompt_chars is not None and len(prompt) > self.max_prompt_chars:
            raise PromptTooLong(f"prompt has {len(prompt)} chars > --max_prompt_chars {self.max_prompt_chars}")
        return self.rng.choice(list(choice_options))


def capture_latents(agent, prompts):
    """Replay each participant's final prompt (teacher-forced) and harvest the per-token gates
    every CoreModelAttention layer stashes on forward: log_alpha (channel-wise log decay, <= 0)
    and beta (channel-wise learning rate in (0, 2)), each as per-head channel means, fp16
    [num_layers, T, num_heads]. Also token_ids, press_positions (token index of each PRESS_* =
    the k-th agent call) and press_classes (0..25). Returns None if the model exposes no stashes."""
    from tqdm import tqdm
    torch = agent.torch
    records = []
    for i, prompt in enumerate(tqdm(prompts, desc="capture_latents")):
        text = training_text(prompt)
        input_ids = agent.tokenizer(text, return_tensors="pt").input_ids.to(agent.device)
        with torch.no_grad():
            agent.model(input_ids=input_ids, logits_to_keep=1, use_cache=False)
        stash = {"log_alpha": [], "beta": []}
        for _, module in agent.model.named_modules():
            for key in stash:
                t = getattr(module, "last_" + key, None)
                if t is not None:
                    stash[key].append(t.to(torch.float16).cpu().clone())
        if not all(stash.values()):
            print("WARNING: model exposes no last_log_alpha/last_beta stashes; skipping latent capture.")
            return None
        gates = {k: torch.cat(v, dim=0) for k, v in stash.items()}  # [num_layers, T, num_heads]
        ids = input_ids[0]
        if gates["log_alpha"].shape[1] != ids.shape[0]:
            raise RuntimeError(f"latent seq len {gates['log_alpha'].shape[1]} != token count {ids.shape[0]}")
        classes = agent.model.token2class.to(ids.device)[ids]
        press_positions = (classes >= 0).nonzero(as_tuple=True)[0]
        press_classes = classes[press_positions]
        expected = [ord(c) - ord("A") for c in CLOSED_LETTER.findall(to_discrete(prompt)[0])]
        if press_classes.tolist() != expected:
            raise RuntimeError(f"participant {i}: {len(press_classes)} PRESS tokens vs {len(expected)} letter responses")
        records.append({
            "prompt": prompt,
            "token_ids": ids.to(torch.int32).cpu(),
            "press_positions": press_positions.to(torch.int32).cpu(),
            "press_classes": press_classes.to(torch.int32).cpu(),
            **gates,
        })
    return records


def load_experiments():
    return json.load(open(os.path.join(HERE, "experiments.json")))


def load_task(x):
    spec = importlib.util.spec_from_file_location(f"sim_{x['study']}_{x['exp']}", os.path.join(HERE, x["simulator"]))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, x["task_class"])()


def run_experiment(x, agent, args):
    """Simulate one experiment; returns 'ok', 'skipped' or 'failed'."""
    n = args.num_simulations or min(x["participants"], args.max_participants)
    tag = f"{x['study']}/{x['exp']}"
    print(f"\n=== [{x['index']}] {tag}: {x['task_class']}, n={n} (source: {x['participants']} "
          f"participants, {x['choices']} presses, {x['stripped']} non-letter responses)", flush=True)
    np.random.seed(args.seed)
    random.seed(args.seed)
    calls0, nonletter0 = agent.n_calls, agent.n_nonletter
    cache = None
    if isinstance(agent, TrainedAgent):
        agent.reset_cache_stats()
        hits0, misses0 = agent.n_hits, agent.n_misses
    task = load_task(x)
    t0 = time.time()
    try:
        df, prompts = task.simulate(agent, n)
    except UnsupportedChoice as e:
        print(f"SKIPPED {tag} after {agent.n_calls - calls0} agent calls: {e}", flush=True)
        return "skipped"
    except PromptTooLong as e:
        print(f"FAILED {tag} after {agent.n_calls - calls0} agent calls: {e}", flush=True)
        return "failed"
    secs = time.time() - t0
    if isinstance(agent, TrainedAgent):
        cache = {"enabled": agent.use_cache, "hits": agent.n_hits - hits0, "misses": agent.n_misses - misses0,
                 "checked_calls": agent.checked_calls, "max_logit_diff": agent.max_logit_diff}
        if agent.use_cache and agent.max_logit_diff > 0.5:
            print(f"WARNING: cached vs uncached class logits differ by up to {agent.max_logit_diff:.3g} "
                  f"over {agent.checked_calls} checked calls (expected ~1e-2 from bf16 rounding)", flush=True)

    os.makedirs(args.out_dir, exist_ok=True)
    stem = os.path.join(args.out_dir, f"experiment={task.name}_agent={agent.name}")
    df.to_csv(stem + ".csv", index=False)
    with open(stem + ".jsonl", "w", encoding="utf-8") as f:
        for i, p in enumerate(prompts):
            f.write(json.dumps({"participant": i, "text": p}) + "\n")
    meta = {
        "study": x["study"], "exp": x["exp"], "hf_id": x["hf_id"], "sha": x["sha"], "task_class": x["task_class"],
        "agent": agent.name, "model_path": args.model_path, "n": n, "seed": args.seed,
        "temperature": args.temperature, "greedy": args.greedy, "dtype": args.dtype,
        "max_prompt_chars": args.max_prompt_chars,
        "on_nonletter": args.on_nonletter, "agent_calls": agent.n_calls - calls0,
        "nonletter_random_calls": agent.n_nonletter - nonletter0, "cache": cache, "rows": int(len(df)),
        "prompt_chars": [len(p) for p in prompts], "seconds": round(secs, 1), "status": "ok",
    }
    json.dump(meta, open(stem + ".json", "w"), indent=1)
    print(f"Shape: {df.shape}  columns: {df.columns.tolist()}\n{df.head(5)}\n"
          f"{meta['agent_calls']} agent calls ({meta['nonletter_random_calls']} random non-letter), "
          f"cache {cache}, {secs:.0f} s -> {stem}.csv", flush=True)

    if args.save_latents and isinstance(agent, TrainedAgent):
        participants = capture_latents(agent, prompts)
        if participants is not None:
            payload = {"schema_version": 1, "experiment": task.name, "agent": agent.name, "sim_args": meta,
                       "layer_order": "model.layers.0..L-1 (named_modules order)",
                       "gates": "log_alpha, be, w: fp16 [num_layers, T, num_heads]", "participants": participants}
            agent.torch.save(payload, stem + "_latents.pth")
            print(f"Saved latents for {len(participants)} participants -> {stem}_latents.pth", flush=True)
    return "ok"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("model_path", nargs="?", default=None, help="trained CoreModel dir (trained_models/<run>)")
    p.add_argument("--list", action="store_true", help="print experiments.json and exit")
    p.add_argument("--random", action="store_true", help="uniform-random agent instead of a model (smoke test)")
    p.add_argument("--index", type=int, nargs="*", default=None, help="experiment indices (experiments.json)")
    p.add_argument("--experiment", nargs="*", default=None, help="experiments as <study>/exp<i>")
    p.add_argument("--selected", action="store_true", help="the experiments marked selected in experiments.json")
    p.add_argument("--all", action="store_true", help="every experiment in experiments.json")
    p.add_argument("-n", "--num-simulations", type=int, default=None,
                   help="participants per experiment (default: the source count, capped at --max_participants)")
    p.add_argument("--max_participants", type=int, default=1000)
    p.add_argument("--max_prompt_chars", type=int, default=None,
                   help="abort the experiment if a prompt exceeds this (default: no limit; a guard against runaway simulators)")
    p.add_argument("--on_nonletter", choices=["fail", "random"], default="fail",
                   help="non-letter choice options: skip the experiment (default) or answer uniformly at random")
    p.add_argument("--tokenizer", default=None, choices=["bpe", "phoneme"], help="default: inferred from the model path")
    p.add_argument("--dtype", default="bf16", choices=["bf16", "fp32"])
    p.add_argument("--temperature", type=float, default=1.0)
    p.add_argument("--greedy", action="store_true")
    p.add_argument("--seed", type=int, default=0, help="seed for the simulators' numpy/random RNGs and the sampling")
    p.add_argument("--device", default=None)
    p.add_argument("--out_dir", default=DEFAULT_OUT_DIR)
    p.add_argument("--save-latents", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--cache", action=argparse.BooleanOptionalAction, default=True,
                   help="continue a prompt that extends the previous one from the stored memory state (default)")
    p.add_argument("--check_cache", type=int, default=10,
                   help="calls per experiment that are also run without the cache; the largest logit difference goes into the json")
    args = p.parse_args()

    experiments = load_experiments()
    if args.list:
        print(f"{'idx':>3}  {'study/exp':<42} {'class':<32} {'N':>6} {'presses':>8} {'non-letter':>10}  selected: effects / note")
        for x in experiments:
            tail = ", ".join(x["effects"]) if x["selected"] else "no: " + x["note"]
            print(f"{x['index']:>3}  {x['study'] + '/' + x['exp']:<42} {x['task_class']:<32} "
                  f"{x['participants']:>6} {x['choices']:>8} {x['stripped']:>10}  {tail}")
        print(f"{sum(x['selected'] for x in experiments)} selected experiments, "
              f"{sum(len(x['effects']) for x in experiments)} effects")
        return

    selected = []
    if args.all:
        selected = experiments
    if args.selected:
        selected += [x for x in experiments if x["selected"]]
    if args.index:
        selected += [experiments[i] for i in args.index]
    if args.experiment:
        by_key = {f"{x['study']}/{x['exp']}": x for x in experiments}
        selected += [by_key[k] for k in args.experiment]
    if not selected:
        p.error("select experiments with --selected, --index, --experiment or --all")

    if args.random:
        agent = RandomAgent(seed=args.seed, max_prompt_chars=args.max_prompt_chars, on_nonletter=args.on_nonletter)
    elif args.model_path:
        agent = TrainedAgent(args.model_path, tokenizer_kind=args.tokenizer, device=args.device, dtype=args.dtype,
                             temperature=args.temperature, greedy=args.greedy, seed=args.seed,
                             max_prompt_chars=args.max_prompt_chars, on_nonletter=args.on_nonletter,
                             use_cache=args.cache, check_cache=args.check_cache)
    else:
        p.error("give a model_path or --random")

    status = {x["index"]: run_experiment(x, agent, args) for x in selected}
    print("\nSUMMARY: " + ", ".join(f"[{i}] {s}" for i, s in status.items()))
    sys.exit(1 if "failed" in status.values() else 0)


if __name__ == "__main__":
    main()
