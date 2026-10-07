"""Centaur on the Psych-201-agentic test split. Centaur's own format frames a choice as ` <<X>>` (Psych-101), so
the `[HUMAN_RESPONSE]X[/HUMAN_RESPONSE]` markers of the data are mapped to `<<X>>` before tokenization and the
completion-only collator keys on Centaur's ` <<` / `>>` tokens; no PRESS_ rewrite (Centaur scores the letter). A response
followed directly by a newline (cox_2018) becomes `<<X>>.\n`, because Llama 3's tokenizer merges `>>\n` into one token, which
hides the `>>` marker from the collator. The decoder is called directly with xformers' causal mask (unsloth's causal-LM wrapper
builds it; without it xformers attention is bidirectional).
A transcript longer than Centaur's context (--max_seq_length tokens) is cut after its last response that fits; with
Llama 3.1's native 131,072 tokens none is (longest test transcript 66,254 tokens, measured 2026-09-23). Logits are
computed at the response positions only (full-vocab logits of a 66k-token transcript would not fit next to the model)."""
import argparse
import os
from collections import defaultdict

import torch
import torch.nn.functional as F
from trl import DataCollatorForCompletionOnlyLM
from unsloth import FastLanguageModel
from xformers.ops.fmha.attn_bias import LowerTriangularMask

from utils import MARKERS, load_split

parser = argparse.ArgumentParser()
parser.add_argument("--max_seq_length", type=int, default=131072, help="Centaur's context in tokens; longer transcripts are cut after the last response that fits.")
args = parser.parse_args()

model_name = "marcelbinz/Llama-3.1-Centaur-70B-adapter"
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_name,
    max_seq_length=args.max_seq_length,
    dtype=None,
    load_in_4bit=True,
)

model.eval()

# unsloth builds a shorter RoPE cache than max_seq_length; grow it to the full context once
x = torch.empty(1, device=model.device, dtype=torch.bfloat16)
for module in model.modules():
    if hasattr(module, "extend_rope_embedding"):
        module.extend_rope_embedding(x, seq_len=args.max_seq_length)

l_id = tokenizer(" <<", add_special_tokens=False).input_ids
r_id = tokenizer(">>", add_special_tokens=False).input_ids
assert len(l_id) == 1 and len(r_id) == 1, "Centaur's ` <<` / `>>` markers must be single tokens."
collator = DataCollatorForCompletionOnlyLM(response_template=l_id, instruction_template=r_id, tokenizer=tokenizer)


def to_centaur_format(ex):
    text = ex["text"].replace(MARKERS["close"] + "\n", ">>.\n").replace(MARKERS["open"], "<<").replace(MARKERS["close"], ">>")
    enc = tokenizer(text, truncation=False)
    ids = enc["input_ids"]
    if len(ids) > args.max_seq_length:
        # keep everything up to and including the last `>>` inside the context
        cut = max(i for i in range(min(len(ids), args.max_seq_length)) if ids[i] == r_id[0]) + 1
        enc = {"input_ids": ids[:cut], "attention_mask": enc["attention_mask"][:cut], "truncated": True}
    else:
        enc = {"input_ids": ids, "attention_mask": enc["attention_mask"], "truncated": False}
    return enc


test_set = load_split("test").map(to_centaur_format, batched=False)
n_truncated = int(sum(test_set["truncated"]))
print(f"[final_eval] {n_truncated} of {len(test_set)} transcripts cut to Centaur's {args.max_seq_length}-token context", flush=True)

# the LoRA-wrapped decoder and its output head: running them separately avoids the full [T, vocab] logits
base_model = model.get_base_model()
decoder, lm_head = base_model.model, base_model.lm_head

by_study = defaultdict(list)
for i, study in enumerate(test_set["study"]):
    by_study[study].append(i)
print(f"[final_eval] evaluating split 'test' ({len(by_study)} studies)", flush=True)

view = test_set.with_format("torch", columns=["input_ids", "attention_mask"])

results = {}       # study -> (nll, n_tokens)
per_token = {}     # study -> per-response-token losses
with torch.inference_mode():
    for study in sorted(by_study):
        sub_set = view.select(by_study[study])
        dataloader = torch.utils.data.DataLoader(dataset=sub_set, collate_fn=collator, batch_size=1)

        all_losses = []
        for inputs in dataloader:
            inputs = {k: v.to(model.device) for k, v in inputs.items()}

            labels = inputs.pop("labels")
            # batch size 1, no padding: no attention_mask, so no [T, T] mask is built at long contexts; the causal mask
            # is xformers' implicit one, as in unsloth's _CausalLM_fast_forward
            hidden = decoder(input_ids=inputs["input_ids"], causal_mask=LowerTriangularMask(), use_cache=False).last_hidden_state

            shift_labels = labels[0, 1:]
            pos = (shift_labels != -100).nonzero(as_tuple=True)[0]  # position t predicts token t + 1
            logits = lm_head(hidden[0, pos]).float()

            loss = F.cross_entropy(logits, shift_labels[pos], reduction='none')
            all_losses.append(loss.cpu())

        all_losses = torch.cat(all_losses) if all_losses else torch.empty(0)
        per_token[study] = all_losses
        results[study] = (float(all_losses.sum()), int(all_losses.numel()))
        nll, n = results[study]
        
        print(f"[final_eval] test/{study}: nll={nll:.4f} n={n}", flush=True)

suffix = model_name.replace("/", "-")
results_dir = "results_evals"
os.makedirs(results_dir, exist_ok=True)
torch.save({"test": per_token}, os.path.join(results_dir, "results_" + suffix + ".pth"))

nll_test = sum(nll for nll, _ in results.values())
n_test = sum(n for _, n in results.values())

print("\n=== final eval: test ===")
print(f"{'study':<40} {'n_tokens':>10} {'nll':>14} {'mean':>8}")
for study, (nll, n) in sorted(results.items()):
    mean = nll / n if n else float("nan")
    print(f"{study:<40} {n:>10} {nll:>14.4f} {mean:>8.4f}")
test_mean = nll_test / n_test if n_test else float("nan")
print(f"{'TOTAL':<40} {n_test:>10} {nll_test:>14.4f} {test_mean:>8.4f}")

run_name = suffix
os.makedirs("results_reports", exist_ok=True)
md = [
    f"# {run_name}",
    "",
    f"- model: `{model_name}`",
    f"- context: {args.max_seq_length} tokens; transcripts cut to it: {n_truncated} of {len(test_set)}",
    "",
    "## NLL",
    "",
    "| study | n (test) | nll (test) | mean (test) |",
    "|---|---:|---:|---:|",
]
for study, (nll, n) in sorted(results.items()):
    mean = nll / n if n else float("nan")
    md.append(f"| {study} | {n} | {nll:.4f} | {mean:.4f} |")
md.append(f"| **TOTAL** | {n_test} | {nll_test:.4f} | {test_mean:.4f} |")
md.append("")

md_path = os.path.join("results_reports", run_name + ".md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(f"Wrote report to {md_path}")
