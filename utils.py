import hashlib
import json
import os
import re
import shutil
import socket
import string
from collections import defaultdict

import tokenizers
import torch
import torch.nn.functional as F
import transformers
from datasets import load_dataset, load_from_disk
from transformers import AutoTokenizer, Trainer, Wav2Vec2PhonemeCTCTokenizer
from packed_collator import PackedIterableDataset

def latest_checkpoint(load_path):
    """Return path to the highest-numbered checkpoint-N subdir under load_path,
    or load_path itself if it has no such subdirs (e.g. the user already passed
    a checkpoint dir, or the model dir contains a top-level save).
    """
    if not os.path.isdir(load_path):
        return load_path
    best = None
    for entry in os.listdir(load_path):
        m = re.match(r"^checkpoint-(\d+)$", entry)
        if m:
            step = int(m.group(1))
            if best is None or step > best[0]:
                best = (step, os.path.join(load_path, entry))
    return best[1] if best else load_path

# The data: the Psych-201-agentic split on the Hugging Face Hub (built by psych201_agentic/build_dataset.py), pinned to a commit.
# Each letter response is `[HUMAN_RESPONSE]X[/HUMAN_RESPONSE]`; load_data
# rewrites it to `[HUMAN_RESPONSE]PRESS_X[/HUMAN_RESPONSE]` and DataCollatorForCompletionOnlyLM keys on the two
# single-token markers (added to the vocabulary by build_tokenizer), so the loss sits on PRESS_X alone.
DATA_REPOS = {  # split -> (Hub dataset, revision)
    "train": ("marcelbinz/Psych-201-discrete-agentic", "6666b2215983f3ed081814c619a7ecb4941b5c85"),
    "test": ("marcelbinz/Psych-201-discrete-agentic-test", "8db062045e2b063ba27e3050a76a369a9bec0034"),
}
MARKERS = {"open": "[HUMAN_RESPONSE]", "close": "[/HUMAN_RESPONSE]"}


# Tokenized splits written by load_data, one subdir per cache key (gitignored).
TOKENIZED_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tokenized_cache")
# Part of the cache key: bump when tok_fn or the row filtering in load_data changes, so old caches are not reused.
TOKENIZE_VERSION = 3


def load_split(split):
    """The 'train' or 'test' split of Psych-201-agentic from the Hub, at the pinned revision (one row = one session)."""
    repo, revision = DATA_REPOS[split]
    return load_dataset(repo, revision=revision, split="train")


def _tokenizer_identity(tokenizer):
    """Everything about the tokenizer that can change its token ids, as a json-able dict (part of the cache key)."""
    identity = {
        "class": type(tokenizer).__name__,
        "name_or_path": tokenizer.name_or_path,
        "vocab_sha256": hashlib.sha256(json.dumps(tokenizer.get_vocab(), sort_keys=True).encode()).hexdigest(),
        "transformers": transformers.__version__,
        "tokenizers": tokenizers.__version__,
    }
    if getattr(tokenizer, "do_phonemize", False):
        import phonemizer
        from phonemizer.backend import EspeakBackend
        identity["phonemizer_lang"] = tokenizer.phonemizer_lang
        identity["phonemizer_backend"] = tokenizer.phonemizer_backend
        identity["phonemizer"] = phonemizer.__version__
        identity["espeak"] = ".".join(str(v) for v in EspeakBackend.version())
    return identity


def load_data(tokenizer, num_proc=16, add_press=True):
    """Train/test splits of the Psych-201-agentic data (DATA_REPOS on the Hugging Face Hub).
    add_press: rewrite each letter response `[HUMAN_RESPONSE]X[/HUMAN_RESPONSE]` to `[HUMAN_RESPONSE]PRESS_X[/HUMAN_RESPONSE]`.
    Tokenized once and cached under TOKENIZED_CACHE_DIR, keyed by a hash of the Hub datasets and revisions, the tokenizer,
    and the arguments; changed data gets a new cache dir."""
    def tok_fn(ex):
        text = ex["text"]
        if add_press:
            text = text.replace(MARKERS["open"], MARKERS["open"] + "PRESS_")
        return tokenizer(text, truncation=False)

    print(f"data: {DATA_REPOS}")

    cache_key = {
        "tokenize_version": TOKENIZE_VERSION,
        "data_repos": DATA_REPOS,
        "add_press": add_press,
        "markers": MARKERS,
        "tokenizer": _tokenizer_identity(tokenizer),
    }
    key_hash = hashlib.sha256(json.dumps(cache_key, sort_keys=True).encode()).hexdigest()[:12]
    cache_dir = os.path.join(TOKENIZED_CACHE_DIR, f"{os.path.basename(tokenizer.name_or_path)}-{key_hash}")

    if not os.path.isdir(cache_dir):
        print(f"tokenized cache miss, building {cache_dir}")
        train_set = load_split("train")
        test_set = load_split("test")

        train_set = train_set.map(tok_fn, batched=False, num_proc=num_proc)
        test_set = test_set.map(tok_fn, batched=False, num_proc=num_proc)

        # Write to a job-private tmp dir, then rename: concurrent jobs (e.g. grid cells) never read a partial cache.
        tmp_dir = f"{cache_dir}.tmp-{socket.gethostname()}-{os.getpid()}"
        train_set.save_to_disk(os.path.join(tmp_dir, "train"))
        test_set.save_to_disk(os.path.join(tmp_dir, "test"))
        with open(os.path.join(tmp_dir, "cache_key.json"), "w") as f:
            json.dump(cache_key, f, indent=2)
        try:
            os.rename(tmp_dir, cache_dir)
        except OSError:
            if not os.path.isdir(cache_dir):
                raise
            shutil.rmtree(tmp_dir)  # a concurrent job renamed its identical cache into place first

    print(f"tokenized cache: {cache_dir}")
    train_set = load_from_disk(os.path.join(cache_dir, "train"))
    print(train_set)

    test_set = load_from_disk(os.path.join(cache_dir, "test"))
    print(test_set)

    return train_set, test_set


def infer_tokenizer_name(load_path):
    """Infer 'bpe' or 'phoneme' from a model directory name."""
    m = re.search(r"-(bpe|phoneme)-", load_path)
    if m is None:
        raise ValueError(
            f"Impossible to infer tokenizer from load path {load_path!r}; expected "
            f"a substring like 'core-phoneme-'."
        )
    return m.group(1)


def build_tokenizer(name):
    """The tokenizer ('bpe' or 'phoneme') with the single-token PRESS_A..Z response vocabulary and the
    `[HUMAN_RESPONSE]`/`[/HUMAN_RESPONSE]` response markers added."""
    if name == "bpe":
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B-Base", use_fast=True)
    elif name == "phoneme":
        tokenizer = Wav2Vec2PhonemeCTCTokenizer.from_pretrained("facebook/wav2vec2-xlsr-53-espeak-cv-ft")
    else:
        raise ValueError(f"Unknown tokenizer {name!r}; expected 'bpe' or 'phoneme'.")
    tokenizer.add_special_tokens({"additional_special_tokens": [f"PRESS_{c}" for c in string.ascii_uppercase]})
    tokenizer.add_special_tokens({"additional_special_tokens": [MARKERS["open"], MARKERS["close"]]})
    return tokenizer


def template_token_ids(tokenizer):
    """Token-ids of the open (response template) and close (instruction template) markers, both single tokens."""
    l_id = tokenizer(MARKERS["open"], add_special_tokens=False).input_ids
    r_id = tokenizer(MARKERS["close"], add_special_tokens=False).input_ids
    assert len(l_id) == 1 and len(r_id) == 1, "Please ensure single token markers."
    return l_id, r_id


def response_token_ids(tokenizer):
    """Token-ids of PRESS_A..Z, asserting each is a single token."""
    response_token_ids = []
    for ch in string.ascii_uppercase:
        ids = tokenizer.encode("PRESS_" + ch, add_special_tokens=False)
        assert len(ids) == 1, f"'PRESS_{ch}' is not a single token with this tokenizer."
        response_token_ids.append(ids[0])
    return response_token_ids


def load_packed_datasets(tokenizer, l_id, r_id, pack_target_tokens):
    """Train/test splits plus their packed training views."""
    train_unpacked, test_unpacked = load_data(tokenizer)

    train_set = PackedIterableDataset(
        train_unpacked, tokenizer,
        response_template=l_id, instruction_template=r_id,
        target_tokens=pack_target_tokens, shuffle=True, seed=0,
    )
    test_set = PackedIterableDataset(
        test_unpacked, tokenizer,
        response_template=l_id, instruction_template=r_id,
        target_tokens=pack_target_tokens, shuffle=False, seed=0,
    )
    return train_unpacked, test_unpacked, train_set, test_set


class SafeTrainer(Trainer):
    """Trainer that skips an optimizer step whose loss or gradient is not finite.

    The delta rule's fast-weight state can blow up on a single transcript; the resulting inf loss gives
    NaN gradients, and gradient clipping then turns the whole model NaN (the 2026-09-16/17 runs died that
    way in their first 1000 steps). Here the forward/backward runs as usual, then the gradients are
    zeroed (set to None, so AdamW leaves the weights untouched) when the loss or the gradient norm is
    not finite. Each skipped step is printed and its packed batch saved to <output_dir>/nonfinite/ for
    diagnosis; the count is in ``self.nonfinite_steps``. Assumes gradient_accumulation_steps == 1."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nonfinite_steps = 0

    def training_step(self, model, inputs, num_items_in_batch=None):
        loss = super().training_step(model, inputs, num_items_in_batch)
        grads = [p.grad for p in model.parameters() if p.grad is not None]
        grad_norm = torch.norm(torch.stack([g.detach().float().norm() for g in grads])) if grads else torch.tensor(0.0)
        reason = "loss" if not torch.isfinite(loss) else ("grad" if not torch.isfinite(grad_norm) else None)
        if reason is None:
            return loss
        self.nonfinite_steps += 1
        model.zero_grad(set_to_none=True)
        step = self.state.global_step
        print(f"[SafeTrainer] step {step}: non-finite {reason} (loss {loss.item():.3e}, grad norm {grad_norm.item():.3e}); "
              f"update skipped ({self.nonfinite_steps} so far)", flush=True)
        try:
            out_dir = os.path.join(self.args.output_dir, "nonfinite")
            os.makedirs(out_dir, exist_ok=True)
            torch.save({k: v.detach().cpu() for k, v in inputs.items() if torch.is_tensor(v)},
                       os.path.join(out_dir, f"step{step}_{reason}.pt"))
        except Exception as e:  # never let the diagnostic kill the run
            print(f"[SafeTrainer] could not save the batch: {e}", flush=True)
        return loss if torch.isfinite(loss) else torch.zeros_like(loss)


def write_run_name_file(path, run_name):
    """Write the resolved run name for downstream SLURM jobs that read it at runtime."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(run_name + "\n")


def iter_study_packs(rows, mask_collator, target_tokens, pad_id, pad_to_multiple_of=64):
    """Pack lists of token ids into flat sequences of at most
    target_tokens. Yields (input_ids, labels, cu_seqlens) tensors.
    """
    def per_row_labels(ids):
        out = mask_collator([{"input_ids": ids}])["labels"][0].tolist()
        return out[: len(ids)]

    def finalize(all_ids, all_labels, cu):
        pad = (-len(all_ids)) % pad_to_multiple_of
        if pad:
            all_ids = all_ids + [pad_id] * pad
            all_labels = all_labels + [-100] * pad
            cu = cu + [len(all_ids)]
        return (
            torch.tensor(all_ids, dtype=torch.long),
            torch.tensor(all_labels, dtype=torch.long),
            torch.tensor(cu, dtype=torch.int32),
        )

    all_ids, all_labels, cu = [], [], [0]
    for ids in rows:
        ids = list(ids)
        if all_ids and len(all_ids) + len(ids) > target_tokens:
            yield finalize(all_ids, all_labels, cu)
            all_ids, all_labels, cu = [], [], [0]
        all_ids.extend(ids)
        all_labels.extend(per_row_labels(ids))
        cu.append(len(all_ids))
    if all_ids:
        yield finalize(all_ids, all_labels, cu)


def final_eval(model, splits, mask_collator, target_tokens, pad_id, *, autocast_bf16):
    device = next(model.parameters()).device
    token2class = model.token2class.to(device)

    results = {}
    with torch.inference_mode():
        for split_name, dataset in splits.items():
            by_study = defaultdict(list)
            for i, study in enumerate(dataset["study"]):
                by_study[study].append(i)

            print(f"[final_eval] evaluating split '{split_name}' "
                  f"({len(by_study)} studies)", flush=True)

            def rows_for(idxs):
                for i in idxs:
                    yield dataset[int(i)]["input_ids"]

            per_study = {}
            for study in sorted(by_study):
                nll, n_tokens = 0.0, 0
                for input_ids, labels, cu_seqlens in iter_study_packs(
                    rows_for(by_study[study]), mask_collator, target_tokens, pad_id,
                ):
                    input_ids = input_ids.unsqueeze(0).to(device)
                    labels = labels.unsqueeze(0).to(device)
                    cu_seqlens = cu_seqlens.to(device)

                    if autocast_bf16:
                        with torch.autocast(device_type=device.type, dtype=torch.bfloat16):
                            logits = model(input_ids=input_ids, cu_seqlens=cu_seqlens).logits
                        logits = logits.float()
                    else:
                        logits = model(input_ids=input_ids, cu_seqlens=cu_seqlens).logits

                    ignore_mask = labels == -100
                    labels = token2class[labels.clamp(min=0)]
                    labels[ignore_mask] = -100

                    shift_logits = logits[:, :-1, :].reshape(-1, logits.size(-1))
                    shift_labels = labels[:, 1:].reshape(-1)
                    nll += F.cross_entropy(
                        shift_logits, shift_labels, ignore_index=-100, reduction="sum",
                    ).item()
                    n_tokens += int((shift_labels != -100).sum())
                per_study[study] = (nll, n_tokens)
                print(f"[final_eval] {split_name}/{study}: nll={nll:.4f} n={n_tokens}",
                      flush=True)
            results[split_name] = per_study
    return results
