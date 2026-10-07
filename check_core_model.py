"""Numerical checks of CoreModel (fla/models/core_model) against its documented equations.

  1. delta rule == reference recurrence M_t = D_t M_{t-1} + k (beta * (v - (D_t M_{t-1})^T k))^T, o_t = M_t^T q_t * d^-0.5
  2. hebbian rule == the same recurrence without the prediction term
  3. both rules, with and without the forget gate: fwd + bwd finite, every parameter gets a gradient
  4. the delta rule's kernel (fla/ops/delta_value): output, final state and gradients == the naive recurrence
     (packed sequences, initial state, two chunk sizes, two launch variants)
  5. CoreModelForCausalLM: finite loss on the response classes, save / from_pretrained round trip reproduces the logits

On CPU the attention file is loaded on its own with the naive token-by-token reference kernel of the Hebbian rule
(fla/ops/gla/naive.py) in place of the Triton one and the PyTorch paths of fla/ops/delta_value (the fla package
itself needs a Triton driver to import); the layer must match the reference to 1e-4 (max abs). On CUDA the layer
runs its normal Triton kernels, the causal-LM checks run as well, and the criterion is upstream fla's: relative
RMS error (fla.utils.get_err_ratio) below 0.5 %, since the chunk kernels use TF32 matmuls and chunked
accumulation. --dtype bfloat16 runs the forward under bf16 autocast as training does (fp32 master weights) and
allows 2 % relative RMS, the rounding of the inputs to bf16. --op-tests also runs upstream's own kernel tests
(tests/ops/test_gla.py). Layer size as in the trained models: 4 heads of 32 (128 latents). Exit 0 when all
checks pass.

Usage:
    python check_core_model.py [--device cpu|cuda] [--dtype float32|bfloat16] [--op-tests]
"""
import argparse
import os
import subprocess
import sys
import tempfile

import torch
import torch.nn.functional as F

FLA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flash-linear-attention-040526")
FAILURES = []
HIDDEN, HEADS, HEAD_DIM = 128, 4, 32


def err_ratio(ref, out):
    """Relative RMS error, as fla.utils.get_err_ratio."""
    return ((ref - out).flatten().square().mean().sqrt() / (ref.flatten().square().mean().sqrt() + 1e-8)).item()


def load_module(name, path):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def import_layer(device):
    """The layer module. On CUDA the real fla package (Triton kernels); on CPU the fla package cannot be
    imported (its ops autotune at import time and need a Triton driver), so the attention file is loaded on
    its own with stub `fla.*` modules that provide the layer-cache helpers, route the Hebbian kernel names to
    the naive token-by-token recurrence and load fla/ops/delta_value as is (PyTorch paths off-GPU)."""
    import types
    naive_gla = load_module("naive_gla", os.path.join(FLA_DIR, "fla/ops/gla/naive.py")).naive_recurrent_gla
    if device != "cpu":
        sys.path.insert(0, FLA_DIR)
        import fla.models.core_model.core_model_attention as attn_mod
        return attn_mod

    def gla(q, k, v, g=None, gk=None, initial_state=None, output_final_state=False, cu_seqlens=None, **kw):
        assert cu_seqlens is None
        return naive_gla(q, k, v, g if g is not None else gk, initial_state=initial_state,
                         output_final_state=output_final_state)

    def stub(name, **attrs):
        mod = types.ModuleType(name)
        mod.__dict__.update(attrs)
        sys.modules[name] = mod
        return mod

    stub("fla"); stub("fla.layers"); stub("fla.ops"); stub("fla.models")
    stub("fla.layers.utils",
         get_layer_cache=lambda module, past_key_values: None if past_key_values is None else past_key_values[module.layer_idx],
         update_layer_cache=lambda module, past_key_values, **kw: None,
         get_unpad_data=None, index_first_axis=None, pad_input=None)
    stub("fla.ops.gla", chunk_gla=gla, fused_recurrent_gla=gla)
    load_module("fla.ops.delta_value", os.path.join(FLA_DIR, "fla/ops/delta_value/chunk.py"))
    stub("fla.models.utils", Cache=object)
    return load_module("core_model_attention", os.path.join(FLA_DIR, "fla/models/core_model/core_model_attention.py"))


def report(name, ok, detail=""):
    print(f"[{'ok' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILURES.append(name)


def reference(layer, x, rule):
    """The documented recurrence in float64 from the layer's own projections."""
    x64 = x.double()
    d, H = layer.head_dim, layer.num_heads
    q = F.normalize(F.silu(x64 @ layer.q_proj.weight.double().T).view(*x.shape[:2], H, d), dim=-1)
    k = F.normalize(F.silu(x64 @ layer.k_proj.weight.double().T).view(*x.shape[:2], H, d), dim=-1)
    v = x64.view(*x.shape[:2], H, d)
    beta = torch.sigmoid(x64 @ layer.b_proj.weight.double().T).view(*x.shape[:2], H, d)
    if layer.use_forget_gate:
        log_alpha = -torch.exp(layer.A_log.double()) * F.softplus(x64 @ layer.a_proj.weight.double().T + layer.dt_bias.double())
        alpha = log_alpha.exp().view(*x.shape[:2], H, d)
    else:
        alpha = torch.ones_like(beta)
    B, T = x.shape[:2]
    M = torch.zeros(B, H, d, d, dtype=torch.float64)
    o = torch.zeros(B, T, H, d, dtype=torch.float64)
    for t in range(T):
        M = M * alpha[:, t].unsqueeze(-1)                                        # D_t M_{t-1}
        if rule == "delta":
            M = M - k[:, t].unsqueeze(-1) * (beta[:, t] * (k[:, t].unsqueeze(-1) * M).sum(-2)).unsqueeze(-2)  # - k (beta * M^T k)^T
        M = M + k[:, t].unsqueeze(-1) * (beta[:, t] * v[:, t]).unsqueeze(-2)      # + k (beta v)^T
        o[:, t] = (q[:, t].unsqueeze(-1) * M).sum(-2) * d ** -0.5
    return o.reshape(B, T, H * d)


def check_layer(device, dtype, rule, use_forget_gate, T, training, tol):
    torch.manual_seed(0)
    layer = ATTN.CoreModelAttention(hidden_size=HIDDEN, head_dim=HEAD_DIM, num_heads=HEADS, learning_rule=rule,
                                    use_forget_gate=use_forget_gate).to(device)
    layer.train(training)
    x = torch.randn(2, T, HIDDEN, device=device)
    # as in training: fp32 master weights, the forward under bf16 autocast for dtype=bfloat16
    with torch.no_grad(), torch.autocast(device_type=device, dtype=dtype, enabled=dtype != torch.float32):
        o = layer(x)[0].float().cpu()
    ref = reference(layer.cpu(), x.cpu(), rule).float()
    err = (o - ref).abs().max().item()
    ratio = err_ratio(ref, o)
    tag = f"{rule} fg={use_forget_gate} T={T} {'short' if T <= 64 and not training else 'chunk'} {dtype}"
    on_abs = device == "cpu" and dtype == torch.float32
    ok = err < tol if on_abs else ratio < tol
    report(f"layer == reference ({tag})", ok,
           f"max abs err {err:.2e}, rel rms err {ratio:.2e} (tol {tol:g} on {'max abs' if on_abs else 'rel rms'})")
    return layer.to(device), x


def check_delta_op(device):
    """chunk_delta_value (Triton kernels on CUDA in float32, PyTorch paths in float64) against the naive
    recurrence in float64: output, final state, gradients; packed sequences with an initial state."""
    naive = load_module("naive_delta_value", os.path.join(FLA_DIR, "fla/ops/delta_value/naive.py")).naive_recurrent_delta_value
    import importlib
    dv = sys.modules["fla.ops.delta_value"] if device == "cpu" else importlib.import_module("fla.ops.delta_value.chunk")
    chunk, default_tuning = dv.chunk_delta_value, dict(dv.TUNING)
    # launch variants of the Triton scan (float32 on CUDA only): tl.dot on 16-channel blocks, broadcast sums on 2-channel blocks
    variants = [{}, {"scan_value_block": 2, "scan_warps": 1}]
    torch.manual_seed(4)
    H, d = 2, HEAD_DIM
    for dtype in ([torch.float64] if device == "cpu" else [torch.float64, torch.float32]):
        for C, lens in ((16, [5, 16, 1, 40, 23]), (16, [200]), (64, [70, 130])):
            T = sum(lens)
            cu = torch.tensor([0] + torch.tensor(lens).cumsum(0).tolist(), dtype=torch.int32)
            q = F.normalize(torch.randn(1, T, H, d, dtype=torch.float64), dim=-1)
            k = F.normalize(torch.randn(1, T, H, d, dtype=torch.float64), dim=-1)
            v = torch.randn(1, T, H, d, dtype=torch.float64)
            g = -torch.rand(1, T, H, d, dtype=torch.float64) * torch.tensor([0.05, 3.0], dtype=torch.float64).view(1, 1, H, 1)
            beta = torch.rand(1, T, H, d, dtype=torch.float64)
            h0 = torch.randn(len(lens), H, d, d, dtype=torch.float64)
            xs = [x.requires_grad_() for x in (q, k, v, g, beta)]
            ref = [naive(*[x[:, a:b] for x in xs], initial_state=h0[s:s + 1], output_final_state=True)
                   for s, (a, b) in enumerate(zip(cu[:-1].tolist(), cu[1:].tolist()))]
            o_ref, f_ref = torch.cat([r[0] for r in ref], 1), torch.cat([r[1] for r in ref], 0)
            do = torch.randn_like(o_ref)
            g_ref = torch.autograd.grad((o_ref * do).sum(), xs)
            for variant in (variants if dtype == torch.float32 else variants[:1]):
                dv.TUNING.update(default_tuning)
                dv.TUNING.update(variant)
                ys = [x.detach().to(device, dtype).requires_grad_() for x in xs]
                o, f = chunk(*ys, initial_state=h0.to(device, dtype), output_final_state=True, cu_seqlens=cu.to(device),
                             chunk_size=C)
                g_out = torch.autograd.grad((o.double() * do.to(device)).sum(), ys)
                pairs = [("o", o_ref, o), ("state", f_ref, f)] + [(f"d{n}", a, b) for n, a, b in zip("q k v g beta".split(), g_ref, g_out)]
                ratios = {n: err_ratio(a, b.detach().double().cpu()) for n, a, b in pairs}
                worst = max(ratios, key=ratios.get)
                tol = 1e-9 if dtype == torch.float64 else 5e-3
                report(f"chunk_delta_value == naive recurrence (C={C} lens={lens} {dtype} {variant or ''})", ratios[worst] < tol,
                       f"worst rel rms err {ratios[worst]:.2e} ({worst})")
            dv.TUNING.update(default_tuning)


def check_grads(device, dtype, rule, use_forget_gate):
    torch.manual_seed(2)
    layer = ATTN.CoreModelAttention(hidden_size=HIDDEN, head_dim=HEAD_DIM, num_heads=HEADS, learning_rule=rule,
                                    use_forget_gate=use_forget_gate).to(device)
    layer.train()
    x = torch.randn(2, 96, HIDDEN, device=device, requires_grad=True)
    with torch.autocast(device_type=device, dtype=dtype, enabled=dtype != torch.float32):
        o = layer(x)[0]
    loss = o.float().pow(2).mean()
    loss.backward()
    missing = [n for n, p in layer.named_parameters() if p.grad is None]
    nonfinite = [n for n, p in layer.named_parameters() if p.grad is not None and not torch.isfinite(p.grad).all()]
    ok = torch.isfinite(loss).item() and not missing and not nonfinite and torch.isfinite(x.grad).all().item()
    report(f"fwd+bwd ({rule} fg={use_forget_gate} {dtype})", ok,
           f"loss {loss.item():.4f}" + (f" missing grads {missing}" if missing else "") + (f" nonfinite {nonfinite}" if nonfinite else ""))


def check_causal_lm(device):
    if device == "cpu":
        print("[skip] CoreModelForCausalLM checks need the fla package (GPU box)")
        return
    from fla.models import CoreModelConfig, CoreModelForCausalLM
    torch.manual_seed(3)
    response_ids = list(range(10, 36))
    for rule in ("delta", "hebbian"):
        config = CoreModelConfig(vocab_size=40, hidden_size=HIDDEN, num_heads=HEADS, head_dim=HEAD_DIM, num_hidden_layers=2,
                                 learning_rule=rule, response_token_ids=response_ids, pad_token_id=0)
        model = CoreModelForCausalLM(config).to(device).eval()
        ids = torch.randint(0, 40, (1, 80), device=device)
        labels = torch.where((ids >= 10) & (ids < 36), ids, torch.full_like(ids, -100))
        with torch.no_grad():
            out = model(input_ids=ids, labels=labels)
        ok = torch.isfinite(out.loss).item() and out.logits.shape[-1] == 26
        with tempfile.TemporaryDirectory() as tmp:
            model.save_pretrained(tmp)
            reloaded = CoreModelForCausalLM.from_pretrained(tmp).to(device).eval()
            with torch.no_grad():
                out2 = reloaded(input_ids=ids)
        err = (out.logits.float() - out2.logits.float()).abs().max().item()
        report(f"CoreModelForCausalLM {rule}: loss finite, 26 classes, save/load round trip", ok and err < 1e-5,
               f"loss {out.loss.item():.4f}, reload max abs logit diff {err:.2e}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--dtype", default="float32", choices=["float32", "bfloat16"])
    p.add_argument("--op-tests", action="store_true", help="also run upstream's tests/ops/test_gla.py (CUDA)")
    args = p.parse_args()
    dtype = getattr(torch, args.dtype)
    device = args.device
    global ATTN
    ATTN = import_layer(device)
    print(f"{device}: layer from {ATTN.__file__}" + (" with PyTorch reference kernels" if device == "cpu" else " with Triton kernels"))
    # fp32: max abs 1e-4 against the naive kernels (CPU), rel RMS 0.5 % against the Triton kernels (upstream's
    # criterion); bf16 (autocast, inputs rounded to bf16 before the recurrence): rel RMS 2 %, any device.
    tol = 2e-2 if dtype == torch.bfloat16 else (1e-4 if device == "cpu" else 5e-3)
    for rule in ("delta", "hebbian"):
        for fg in (True, False):
            check_layer(device, dtype, rule, fg, T=40, training=False, tol=tol)   # short inference step (generation)
            check_layer(device, dtype, rule, fg, T=200, training=True, tol=tol)   # chunk path
            check_grads(device, dtype, rule, fg)
    check_delta_op(device)
    check_causal_lm(device)
    if args.op_tests:
        tests = [os.path.join(FLA_DIR, "tests", "ops", "test_gla.py")]
        rc = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *tests], cwd=FLA_DIR).returncode
        report("upstream op tests (tests/ops/test_gla.py)", rc == 0, f"pytest exit {rc}")
    print("ALL OK" if not FAILURES else f"FAILED: {FAILURES}")
    sys.exit(1 if FAILURES else 0)


if __name__ == "__main__":
    main()
