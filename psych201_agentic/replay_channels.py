"""Replay the simulated transcripts of a trained CoreModel and save channel-level gates per press.

simulate_core.py saves the gates as per-head channel means (*_latents.pth). This script replays the
same transcripts (the `prompt` of every participant in the latents file; no new choices are made)
with the attention layers' stash_channels flag on, and reduces the full [T, heads, head_dim] gates
per press, as plotting/build_cache.py does for the head means:
  beta_press, la_press   beta / log_alpha AT the press token
  beta_post,  la_post    means over the tokens after press k up to press k+1 (exclusive; the last
                         press runs to the end of the transcript); NaN if the segment is empty
  beta_fb,    la_fb      means over the feedback of press k only: the tokens after press k up to the end
                         of its line (the first line break of the text after its closing marker; the
                         next trial or the next game's header starts after it). The phoneme tokenizer
                         drops line breaks, so the end is found by tokenizing the feedback text alone;
                         a press whose whole segment tokenizes to another length than in the stream
                         gets NaN (counted in the log)
Rows: participant i, press k, in order (the row order of build_cache.py).

Checks (the experiment fails loudly otherwise): the token ids equal the saved ones, and the channel
means of the replayed gates equal the saved head means (max abs difference <= --tol).

Output (--out_dir): experiment=<exp>_agent=<agent>_channels.npz
  beta_press, la_press, beta_post, la_post, beta_fb, la_fb: fp16 [N, num_layers, num_heads, head_dim]
  fb_len (int32): feedback tokens per press (-1 where NaN)
  participant, press_idx (int32), press_class (int16); max_diff_beta, max_diff_log_alpha

Usage:
  python psych201_agentic/replay_channels.py trained_models/<run> --temperature 1 --experiment <exp> [<exp> ...]
"""
import argparse
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from simulate_core import CLOSE, DEFAULT_OUT_DIR, OPEN, TrainedAgent, training_text  # noqa: E402


def replay_participant(agent, rec):
    """Gates of every layer for one saved participant: (beta, log_alpha), each [L, T, H, D] on the device."""
    torch = agent.torch
    input_ids = agent.tokenizer(training_text(rec["prompt"]), return_tensors="pt").input_ids.to(agent.device)
    if not torch.equal(input_ids[0].cpu().to(torch.int32), rec["token_ids"]):
        raise RuntimeError("token ids differ from the saved ones")
    with torch.no_grad():
        agent.model(input_ids=input_ids, logits_to_keep=1, use_cache=False)   # as capture_latents
    stash = {"beta": [], "log_alpha": []}
    for _, module in agent.model.named_modules():                              # layer order of capture_latents
        if getattr(module, "stash_channels", False):
            stash["beta"].append(module.last_beta[0].float())
            stash["log_alpha"].append(module.last_log_alpha[0].float())
    return torch.stack(stash["beta"]), torch.stack(stash["log_alpha"])


def feedback_ends(tokenizer, rec):
    """Exclusive token end of the feedback of every press ([K] int64, -1 if unknown): the press's closing
    marker, then the tokens of the text up to the first line break after it."""
    pp = rec["press_positions"].tolist()
    T = len(rec["token_ids"])
    segs = [s.split(OPEN)[0] for s in training_text(rec["prompt"]).split(CLOSE)[1:]]
    if len(segs) < len(pp):
        raise RuntimeError(f"{len(segs)} closing markers for {len(pp)} presses")
    segs = segs[:len(pp)]
    fbs = [s if s.find("\n") < 0 else s[:s.find("\n")] for s in segs]
    n_seg = [len(x) for x in tokenizer(segs, add_special_tokens=False).input_ids]
    n_fb = [len(x) for x in tokenizer(fbs, add_special_tokens=False).input_ids]
    ends = []
    for k, p in enumerate(pp):
        stream = (pp[k + 1] - 1 if k + 1 < len(pp) else T) - (p + 2)            # tokens between close and next open marker
        ends.append(p + 2 + n_fb[k] if n_seg[k] == stream or k + 1 == len(pp) else -1)
    return np.array(ends, dtype=np.int64)


def per_press(torch, x, pp, fb_end):
    """x [L, T, H, D] -> (value at the press tokens, mean over the post segments, mean over the feedback),
    each [K, L, H, D]; fb_end = exclusive feedback ends (-1 -> NaN)."""
    L, T, H, D = x.shape
    csum = torch.zeros(L, T + 1, H, D, device=x.device, dtype=torch.float64)
    csum[:, 1:] = x.double().cumsum(dim=1)
    a = pp + 1                                                                 # first token after press k
    b = torch.cat([pp[1:], torch.tensor([T], device=pp.device)])               # next press (exclusive)
    n = (b - a).clamp(min=0)
    seg = (csum[:, b] - csum[:, a]) / n.view(1, -1, 1, 1)                      # n = 0 -> nan
    e = torch.minimum(fb_end.clamp(min=0), b)
    nf = torch.where(fb_end >= 0, (e - a).clamp(min=0), torch.zeros_like(e))
    fb = (csum[:, e] - csum[:, a]) / nf.view(1, -1, 1, 1)                     # nf = 0 -> nan
    return x[:, pp].permute(1, 0, 2, 3), seg.float().permute(1, 0, 2, 3), fb.float().permute(1, 0, 2, 3)


def run_experiment(agent, exp, args):
    torch = agent.torch
    stem = os.path.join(args.out_dir, f"experiment={exp}_agent={agent.name}")
    payload = torch.load(stem + "_latents.pth", weights_only=False, map_location="cpu", mmap=True)
    assert payload["agent"] == agent.name, (payload["agent"], agent.name)
    out = {k: [] for k in ("beta_press", "la_press", "beta_post", "la_post", "beta_fb", "la_fb")}
    participant, press_idx, press_class, fb_len = [], [], [], []
    max_diff = {"beta": 0.0, "log_alpha": 0.0}
    t0 = time.time()
    for i, rec in enumerate(payload["participants"]):
        beta, log_alpha = replay_participant(agent, rec)
        for name, x in (("beta", beta), ("log_alpha", log_alpha)):
            saved = rec[name].to(agent.device).float()                           # [L, T, H], fp16 channel means
            max_diff[name] = max(max_diff[name], (x.mean(-1) - saved).abs().max().item())
        pp = rec["press_positions"].to(agent.device).long()
        ends = feedback_ends(agent.tokenizer, rec)
        fb_len.append(np.where(ends >= 0, ends - (rec["press_positions"].numpy() + 1), -1).astype(np.int32))
        fb_end = torch.from_numpy(ends).to(agent.device)
        for key, x in (("beta", beta), ("la", log_alpha)):
            at, post, fb = per_press(torch, x, pp, fb_end)
            out[f"{key}_press"].append(at.half().cpu().numpy())
            out[f"{key}_post"].append(post.half().cpu().numpy())
            out[f"{key}_fb"].append(fb.half().cpu().numpy())
        participant.append(np.full(len(pp), i, dtype=np.int32))
        press_idx.append(np.arange(len(pp), dtype=np.int32))
        press_class.append(rec["press_classes"].numpy().astype(np.int16))
    if max(max_diff.values()) > args.tol:
        raise RuntimeError(f"{exp}: replayed channel means differ from the saved gates: {max_diff}")
    arrays = {k: np.concatenate(v) for k, v in out.items()}
    np.savez(stem + "_channels.npz", **arrays, participant=np.concatenate(participant),
             press_idx=np.concatenate(press_idx), press_class=np.concatenate(press_class), fb_len=np.concatenate(fb_len),
             max_diff_beta=max_diff["beta"], max_diff_log_alpha=max_diff["log_alpha"])
    fbl = np.concatenate(fb_len)
    print(f"{exp}: feedback segments: median {int(np.median(fbl[fbl >= 0]))} tokens, {int((fbl < 0).sum())} of {len(fbl)} unknown", flush=True)
    print(f"{exp}: {len(payload['participants'])} participants, {len(arrays['beta_press'])} presses, "
          f"shape {arrays['beta_press'].shape}, max diff vs saved {max_diff}, {time.time() - t0:.0f} s "
          f"-> {stem}_channels.npz", flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("model_path")
    p.add_argument("--temperature", type=float, default=1.0, help="names the agent (trained_<run>_temp<T>), as in simulate_core.py")
    p.add_argument("--experiment", nargs="+", required=True, help="<study>_<exp> names, e.g. gershman_2018_deconstructing_exp1")
    p.add_argument("--out_dir", default=DEFAULT_OUT_DIR, help="where the *_latents.pth are; the npz files go there too")
    p.add_argument("--tol", type=float, default=2e-2, help="max abs difference of the channel means vs the saved gates")
    args = p.parse_args()

    agent = TrainedAgent(args.model_path, temperature=args.temperature)
    n = 0
    for _, module in agent.model.named_modules():
        if hasattr(module, "stash_channels"):
            module.stash_channels = True
            n += 1
    if n == 0:
        raise RuntimeError("the model has no stash_channels flag (fla fork too old?)")
    print(f"agent {agent.name}: stash_channels on in {n} layers", flush=True)
    for exp in args.experiment:
        run_experiment(agent, exp, args)


if __name__ == "__main__":
    main()
