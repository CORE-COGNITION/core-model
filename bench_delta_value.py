"""Speed of the memory layer's write rules on one GPU.

Forward + backward of one CoreModelAttention layer (4 heads of 32, bf16 autocast as in training) on a packed batch
of 98,304 tokens, for the delta rule (fla/ops/delta_value) and the Hebbian rule (fla/ops/gla); then the delta rule's
op alone under different launch parameters and a profile. Two packings: a typical one (a 40k-token transcript plus shorter ones) and one 71k-token transcript plus short
ones (the scan runs the sequences of a pack in parallel, so the longest one sets its depth).

Usage (on a GPU): python bench_delta_value.py
"""
import statistics
import sys
import os

import torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "flash-linear-attention-040526"))
from fla.models.core_model.core_model_attention import CoreModelAttention  # noqa: E402
from fla.ops.delta_value import chunk as dv  # noqa: E402

T, HIDDEN, HEADS, HEAD_DIM = 98304, 128, 4, 32
DEVICE = "cuda"
DEFAULT_TUNING = dict(dv.TUNING)


def packing(longest):
    lens = [longest, 8000, 5000, 5000]
    while sum(lens) + 2500 <= T:
        lens.append(2500)
    lens.append(T - sum(lens))
    return torch.tensor([0] + torch.tensor(lens).cumsum(0).tolist(), dtype=torch.int32, device=DEVICE)


def timeit(fn, warmup=3, iters=8):
    for _ in range(warmup):
        fn()
    torch.cuda.synchronize()
    times = []
    for _ in range(iters):
        start, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        start.record()
        fn()
        end.record()
        torch.cuda.synchronize()
        times.append(start.elapsed_time(end))
    return statistics.median(times)


def bench_layer(rule, chunk_size, cu):
    torch.manual_seed(0)
    layer = CoreModelAttention(hidden_size=HIDDEN, head_dim=HEAD_DIM, num_heads=HEADS, learning_rule=rule).to(DEVICE).train()
    layer.delta_chunk_size = chunk_size
    x = torch.randn(1, T, HIDDEN, device=DEVICE, requires_grad=True)

    def step():
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            o = layer(x, cu_seqlens=cu)[0]
        o.float().pow(2).mean().backward()

    torch.cuda.reset_peak_memory_stats()
    ms = timeit(step)
    return ms, torch.cuda.max_memory_allocated() / 2**30


def bench_op(C, cu):
    """chunk_delta_value alone (fwd+bwd, float32 inputs) under different launch parameters."""
    H, K, V = HEADS, HEAD_DIM, HEAD_DIM
    torch.manual_seed(0)
    q = torch.nn.functional.normalize(torch.randn(1, T, H, K, device=DEVICE), dim=-1).requires_grad_()
    k = torch.nn.functional.normalize(torch.randn(1, T, H, K, device=DEVICE), dim=-1).requires_grad_()
    v = torch.randn(1, T, H, V, device=DEVICE, requires_grad=True)
    g = (-0.05 * torch.rand(1, T, H, K, device=DEVICE)).requires_grad_()
    beta = torch.rand(1, T, H, V, device=DEVICE, requires_grad=True)

    def step():
        o, _ = dv.chunk_delta_value(q, k, v, g, beta, cu_seqlens=cu, chunk_size=C)
        o.pow(2).mean().backward()

    out = {}
    sweeps = [{}] \
        + [{"chunk_warps": w} for w in (1, 2, 8)] + [{"inverse_value_block": b, "inverse_warps": w} for b, w in ((2, 1), (8, 1), (8, 2))] \
        + [{"scan_value_block": b, "scan_warps": w} for b, w in ((16, 1), (16, 4), (32, 2), (32, 4), (8, 1), (2, 1))]
    for sweep in sweeps:
        dv.TUNING.update(DEFAULT_TUNING)
        dv.TUNING.update(sweep)
        try:
            out[" ".join(f"{n}={x}" for n, x in sweep.items()) or "default"] = timeit(step)
        except Exception as e:
            out[f"{sweep} FAILED {type(e).__name__}"] = float("nan")
    dv.TUNING.update(DEFAULT_TUNING)
    return out


def profile_layer(chunk_size, cu):
    torch.manual_seed(0)
    layer = CoreModelAttention(hidden_size=HIDDEN, head_dim=HEAD_DIM, num_heads=HEADS, learning_rule="delta").to(DEVICE).train()
    layer.delta_chunk_size = chunk_size
    x = torch.randn(1, T, HIDDEN, device=DEVICE, requires_grad=True)

    def step():
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            o = layer(x, cu_seqlens=cu)[0]
        o.float().pow(2).mean().backward()

    for _ in range(3):
        step()
    torch.cuda.synchronize()
    with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU, torch.profiler.ProfilerActivity.CUDA]) as prof:
        for _ in range(3):
            step()
        torch.cuda.synchronize()
    print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=30, max_name_column_width=60))


def main():
    print(f"GPU {torch.cuda.get_device_name(0)}, T={T}, {HEADS} heads of {HEAD_DIM}")
    for name, longest in (("typical pack (longest transcript 40k)", 40000), ("pack with a 71k transcript", 71000)):
        cu = packing(longest)
        print(f"\n== {name}, {cu.numel() - 1} sequences: one layer fwd+bwd ==")
        for rule, C in (("delta", 16), ("hebbian", 16)):
            tag = f"{rule:8s} C={C:<3d}"
            try:
                ms, gib = bench_layer(rule, C, cu)
                print(f"{tag}  {ms:9.1f} ms   peak {gib:6.2f} GiB", flush=True)
            except Exception as e:  # keep going: one failing config must not hide the others
                print(f"{tag}  FAILED: {type(e).__name__}: {str(e)[:300]}", flush=True)
        print(f"-- chunk_delta_value alone, fwd+bwd (ms), {name} --")
        for C in (16,):
            print(f"C={C:<3d} " + "  |  ".join(f"{n} {ms:.1f}" for n, ms in bench_op(C, cu).items()), flush=True)
    print("\n== profile, delta rule C=16, typical pack, 3 x fwd+bwd ==")
    profile_layer(16, packing(40000))


if __name__ == "__main__":
    main()
