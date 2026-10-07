import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

import argparse
import glob

from transformers import TrainingArguments, set_seed
from fla.models import CoreModelConfig, CoreModelForCausalLM
from trl import DataCollatorForCompletionOnlyLM
from packed_collator import pack_passthrough_collator
from utils import (
    SafeTrainer,
    build_tokenizer,
    final_eval,
    load_packed_datasets,
    template_token_ids,
    response_token_ids,
    write_run_name_file,
)
from laplace import fit_laplace_lml
from reporting import write_train_report

parser = argparse.ArgumentParser()
parser.add_argument("--num_layers", type=int, default=6)
parser.add_argument("--num_latents", type=int, default=128)
parser.add_argument("--num_heads", type=int, default=4, help="Number of attention heads.")
parser.add_argument("--learning_rule", type=str, default="delta", choices=["delta", "hebbian"], help="Memory write rule: gated delta rule (default; the learning rate gates the prediction error per value channel) or gated Hebbian rule (no prediction term).")
parser.add_argument("--pack_target_tokens", type=int, default=304500, help="Token capacity per packed batch row; effective compute size per step.")
parser.add_argument("--num_workers", type=int, default=8)
parser.add_argument("--load_path", type=str, default=None)
parser.add_argument("--resume_latest", action="store_true", help="Resume from the newest checkpoint in trained_models/<run_name>/ if one exists (per-variant alternative to --load_path).")
parser.add_argument("--tokenizer", type=str, default="phoneme", choices=["bpe", "phoneme"])
parser.add_argument("--no_forget_gate", dest="use_forget_gate", action="store_false", help="Disable the input-dependent channel-wise decay of the memory (default: on).")
parser.add_argument("--weight_decay", type=float, default=0.5, help="AdamW weight decay.")
parser.add_argument("--num_train_epochs", type=float, default=100, help="Number of training epochs.")
parser.add_argument("--run_name_suffix", type=str, default="", help="Optional suffix appended to the run name and thus the output dir.")
parser.add_argument("--run_name_file", type=str, default=None, help="Path to write the resolved run name to; the simulation and report jobs read it at runtime to find the model dir.")
parser.add_argument("--seed", type=int, default=42, help="Seed for weight init and training RNG.")
args = parser.parse_args()

set_seed(args.seed)

assert args.num_heads >= 1, f"--num_heads must be >= 1, got {args.num_heads}."
assert args.num_latents % args.num_heads == 0, f"--num_heads ({args.num_heads}) must divide --num_latents ({args.num_latents}) evenly."
tokenizer = build_tokenizer(args.tokenizer)
l_id, r_id = template_token_ids(tokenizer)
response_ids = response_token_ids(tokenizer)

run_name = (
    "core-" + args.tokenizer
    + "-d" + str(args.num_latents)
    + "-L" + str(args.num_layers)
    + "-fg" + ("T" if args.use_forget_gate else "F")
    + "-wd" + f"{args.weight_decay:g}"
    + "-h" + str(args.num_heads)
    + "-lr" + args.learning_rule
)

if args.run_name_suffix:
    run_name += "-" + args.run_name_suffix

if args.run_name_file:
    write_run_name_file(args.run_name_file, run_name)

if args.resume_latest:
    assert args.load_path is None, "--resume_latest and --load_path are mutually exclusive."
    checkpoints = glob.glob(os.path.join("trained_models", run_name, "checkpoint-*"))
    if checkpoints:
        args.load_path = max(checkpoints, key=lambda p: int(p.rsplit("-", 1)[-1]))
        print(f"[resume_latest] resuming from {args.load_path}")
    else:
        print("[resume_latest] no checkpoint found; training from scratch")

if args.load_path is None:
    config = CoreModelConfig(
        vocab_size=len(tokenizer),
        hidden_size=args.num_latents,
        num_hidden_layers=args.num_layers,
        num_heads=args.num_heads,
        head_dim=args.num_latents // args.num_heads,
        learning_rule=args.learning_rule,
        use_forget_gate=args.use_forget_gate,
        response_token_ids=response_ids,
        bos_token_id=tokenizer.bos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )
    model = CoreModelForCausalLM(config)
else:
    model = CoreModelForCausalLM.from_pretrained(args.load_path)

print(model)

train_unpacked, test_unpacked, train_set, test_set = load_packed_datasets(tokenizer, l_id, r_id, args.pack_target_tokens)

training_args = TrainingArguments(
    output_dir="trained_models/" + run_name,
    seed=args.seed,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    gradient_accumulation_steps=1,
    optim="schedule_free_adamw",
    learning_rate=1e-3,
    lr_scheduler_type="constant",
    weight_decay=args.weight_decay,
    max_grad_norm=10.0,
    warmup_steps=0,
    num_train_epochs=args.num_train_epochs,
    eval_strategy="steps",
    eval_steps=10000,
    save_strategy="steps",
    save_steps=10000,
    logging_steps=1000,
    fp16=False,
    bf16=True,
    tf32=True,
    torch_compile=False,
    gradient_checkpointing=False,
    dataloader_num_workers=args.num_workers,
    dataloader_pin_memory=True,
    dataloader_persistent_workers=True,
    remove_unused_columns=False,
    accelerator_config={"dispatch_batches": False},
    report_to="wandb",
)

trainer = SafeTrainer(
    model=model,
    args=training_args,
    train_dataset=train_set,
    eval_dataset=test_set,
    data_collator=pack_passthrough_collator,
    processing_class=tokenizer,
)

trainer.train(resume_from_checkpoint=args.load_path)
print(f"[SafeTrainer] {trainer.nonfinite_steps} non-finite steps skipped", flush=True)

trainer.optimizer.eval()
trainer.save_model()

model.eval()

mask_collator = DataCollatorForCompletionOnlyLM(response_template=l_id, instruction_template=r_id, tokenizer=tokenizer)
results = final_eval(
    model,
    {"train": train_unpacked, "test": test_unpacked},
    mask_collator,
    args.pack_target_tokens,
    tokenizer.pad_token_id,
    autocast_bf16=False,
)

lml = fit_laplace_lml(model, train_unpacked, mask_collator)

write_train_report(
    run_name=run_name,
    output_dir=training_args.output_dir,
    model=model,
    results=results,
    lml=lml,
    trainer=trainer,
)
