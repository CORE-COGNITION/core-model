# Chunkwise kernel for the delta_value rule (CoreModel, --learning_rule delta_value); see naive.py for the recurrence.
#
# Per chunk of C tokens and per head, with the state S_0 at the chunk start, gamma_t the log-decay summed within
# the chunk, K~ = k * exp(gamma) (keys seen from the chunk start), K^ = k * exp(gamma_C - gamma) (keys seen from
# the chunk end) and the decayed Gram matrix G[t, i] = sum_d k_td k_id exp(gamma_td - gamma_id) (i < t), the writes
# u_t = beta_t * (v_t - S~_t^T k_t) solve, for every value channel j,
#
#   (I + Diag(beta_j) G) u_j = beta_j * (v_j - K~ S_0[:, j])                                   (1)
#
# G is shared by the value channels, only the row scaling differs. Forward:
#   prep    (parallel over chunks): gamma, K~, K^, Q~ = q * exp(gamma), G and A[t, i] = sum_d q_td k_id exp(.) (i <= t)
#   inverse (parallel): M_j = (I + Diag(beta_j) G)^-1 Diag(beta_j), C x C per value channel
#   scan    (sequential over the chunks of a sequence): u_j = M_j (v_j - K~ S_0[:, j]), S_C = Diag(exp(gamma_C)) S_0 + K^^T u
#   output  (parallel): o = scale * (Q~ S_0 + A u)
# Backward: the adjoint of (1) is M_j^T, so it is the same scan over the chunks in reverse with M transposed and
# K~, K^ swapped, between an output-backward and an assemble kernel that turn do into dq, dk, dv, dg, dbeta.
# The Triton kernels read and write the packed token layout [T, H, D] directly (every sequence is cut into its own
# chunks, tok_start / tok_len per chunk); in between everything lives per chunk, [NC, H, C, ...]. Every step has a
# PyTorch twin with the same formulas (used off-GPU and in float64, and as the test reference).

import torch

try:
    import triton
    import triton.language as tl
except ImportError:  # CPU-only box without Triton: PyTorch paths only
    triton = None

# Launch parameters of the Triton kernels (bench_delta_value.py sweeps them): threads per program (num_warps * 32)
# and the value channels per program (the columns of the state are independent given k and the decay).
TUNING = {"chunk_warps": 4, "inverse_warps": 1, "inverse_value_block": 4, "scan_warps": 4, "scan_value_block": 16}


# ---------------------------------------------------------------------------------------------------------------
# Chunk layout
# ---------------------------------------------------------------------------------------------------------------

def _chunk_layout(cu_seqlens, T, C):
    """Every sequence is cut into its own chunks of C slots (the last one zero-padded). Nothing here syncs with the
    GPU: NC is an upper bound of the number of chunks, the chunks past the last sequence are empty (tok_len 0)."""
    cu = cu_seqlens.long()
    lens = cu[1:] - cu[:-1]
    n_chunks = (lens + C - 1) // C
    first = torch.cumsum(n_chunks, 0) - n_chunks
    N = lens.numel()
    NC = T // C + N
    chunk = torch.arange(NC, device=cu.device)
    seq = torch.searchsorted(first + n_chunks, chunk, right=True).clamp(max=N - 1)
    local = chunk - first[seq]
    return {
        "NC": NC,
        "first": first.int(), "n_chunks": n_chunks.int(),                       # per sequence
        "tok_start": cu[seq] + local * C,                                       # per chunk
        "tok_len": (lens[seq] - local * C).clamp(0, C).int(),
    }


def _slots(layout, T, C):
    """Token -> slot in the padded chunk layout (PyTorch paths)."""
    valid = torch.arange(C, device=layout["tok_len"].device)[None, :] < layout["tok_len"][:, None]    # [NC, C]
    tok = layout["tok_start"][:, None] + torch.arange(C, device=valid.device)[None, :]
    slot = torch.empty(T, dtype=torch.long, device=valid.device)
    slot[tok[valid]] = torch.nonzero(valid.reshape(-1)).squeeze(-1)
    return slot


def _pad(x, slot, NC, C):      # [T, H, D] -> [NC, H, C, D]
    return x.new_zeros(NC * C, *x.shape[1:]).index_copy(0, slot, x).view(NC, C, *x.shape[1:]).transpose(1, 2).contiguous()


def _unpad(x, slot):           # [NC, H, C, D] -> [T, H, D]
    return x.transpose(1, 2).reshape(-1, x.shape[1], x.shape[3]).index_select(0, slot)


# ---------------------------------------------------------------------------------------------------------------
# PyTorch twins of the chunk-parallel steps (padded layout, any dtype)
# ---------------------------------------------------------------------------------------------------------------

def _decay_ref(gam, strict):
    """exp(gam_t - gam_i) on the lower triangle (strict: i < t), zero elsewhere: [..., t, i, K]."""
    C = gam.shape[-2]
    mask = torch.ones(C, C, dtype=torch.bool, device=gam.device).tril(-1 if strict else 0)[..., None]
    return (gam.unsqueeze(-2) - gam.unsqueeze(-3)).masked_fill(~mask, 0).exp() * mask


def _prep_ref(q, k, g):
    gam = g.cumsum(-2)
    last = gam[..., -1:, :]
    G = (k.unsqueeze(-2) * k.unsqueeze(-3) * _decay_ref(gam, True)).sum(-1)
    A = (q.unsqueeze(-2) * k.unsqueeze(-3) * _decay_ref(gam, False)).sum(-1)
    return gam, G, A, k * gam.exp(), k * (last - gam).exp(), q * gam.exp(), last.squeeze(-2).exp()


def _output_ref(Qt, A, u, S_before, scale):
    return (Qt @ S_before + A @ u) * scale


def _output_bwd_ref(do, Qt, A, u, S_before, scale):
    do = do * scale
    return A.transpose(-1, -2) @ do, Qt.transpose(-1, -2) @ do, (do @ u.transpose(-1, -2)).tril(), do @ S_before.transpose(-1, -2)


def _assemble_ref(q, k, v, gam, G, u, yp, du, S_before, dS_next, dA, dQt):
    """All input gradients of a chunk from the adjoint writes yp = beta * y (y the adjoint of (1)), the output-side
    write gradient du, the state gradients dS_next (after the chunk) and the output-side gradients dA, dQt."""
    last = gam[..., -1:, :]
    E, E2 = gam.exp(), (last - gam).exp()
    y = du + (k * E2) @ dS_next - G.transpose(-1, -2) @ yp
    e = v - (k * E) @ S_before - G @ u                     # prediction errors, u = beta * e
    dG = -(yp @ u.transpose(-1, -2)).tril(-1)
    dKt = -(yp @ S_before.transpose(-1, -2))
    dKh = u @ dS_next.transpose(-1, -2)
    dGam = (dS_next * S_before).sum(-1)
    wG, wA = dG.unsqueeze(-1) * _decay_ref(gam, True), dA.unsqueeze(-1) * _decay_ref(gam, False)
    dxG, dyG = (wG * k.unsqueeze(-3)).sum(-2), (wG * k.unsqueeze(-2)).sum(-3)
    dxA, dyA = (wA * k.unsqueeze(-3)).sum(-2), (wA * q.unsqueeze(-2)).sum(-3)
    dk = dKt * E + dKh * E2 + dxG + dyG + dyA
    dq = dQt * E + dxA
    dgam = dKt * k * E + dQt * q * E - dKh * k * E2 + k * (dxG - dyG) + q * dxA - k * dyA
    dgam[..., -1, :] += (dKh * k * E2).sum(-2) + dGam * last.squeeze(-2).exp()
    dg = dgam.flip(-2).cumsum(-2).flip(-2)
    return dq, dk, yp, dg, y * e


if triton is not None:

    @triton.jit
    def _mm(a, b, DOT: tl.constexpr):
        if DOT:
            return tl.dot(a, b, input_precision="ieee")
        else:
            return tl.sum(a[:, :, None] * b[None, :, :], axis=1)

    @triton.jit
    def _prep_kernel(q, k, v, g, beta, tok_start, tok_len, gam, G, A, Kt, Kh, Qt, Gam, vp, bp,
                     H: tl.constexpr, C: tl.constexpr, K: tl.constexpr, V: tl.constexpr,
                     BK: tl.constexpr, BV: tl.constexpr):
        i_n = tl.program_id(0).to(tl.int64)
        i_h = tl.program_id(1).to(tl.int64)
        ts = tl.load(tok_start + i_n).to(tl.int64)
        tn = tl.load(tok_len + i_n)
        o_c = tl.arange(0, C)
        o_k = tl.arange(0, BK)
        o_v = tl.arange(0, BV)
        m_k = (o_c[:, None] < C) & (o_k[None, :] < K)
        m_v = (o_c[:, None] < C) & (o_v[None, :] < V)
        m_tk = (o_c[:, None] < tn) & (o_k[None, :] < K)
        m_tv = (o_c[:, None] < tn) & (o_v[None, :] < V)
        p_tk = ((ts + o_c[:, None]) * H + i_h) * K + o_k[None, :]              # packed tokens
        p_tv = ((ts + o_c[:, None]) * H + i_h) * V + o_v[None, :]
        base = i_n * H + i_h
        p_ck = base * C * K + o_c[:, None] * K + o_k[None, :]                   # padded chunks
        p_cv = base * C * V + o_c[:, None] * V + o_v[None, :]
        p_cc = base * C * C + o_c[:, None] * C + o_c[None, :]
        b_q = tl.load(q + p_tk, mask=m_tk, other=0.0).to(tl.float32)
        b_k = tl.load(k + p_tk, mask=m_tk, other=0.0).to(tl.float32)
        b_g = tl.load(g + p_tk, mask=m_tk, other=0.0).to(tl.float32)
        tl.store(vp + p_cv, tl.load(v + p_tv, mask=m_tv, other=0.0).to(tl.float32), mask=m_v)
        tl.store(bp + p_cv, tl.load(beta + p_tv, mask=m_tv, other=0.0).to(tl.float32), mask=m_v)
        b_gam = tl.cumsum(b_g, axis=0)
        b_last = tl.sum(tl.where((o_c == C - 1)[:, None], b_gam, 0.0), axis=0)
        b_E = tl.exp(b_gam)
        m_lo = o_c[:, None] >= o_c[None, :]
        b_dec = tl.exp(tl.where(m_lo[:, :, None], b_gam[:, None, :] - b_gam[None, :, :], 0.0)) * b_k[None, :, :]
        b_A = tl.where(m_lo, tl.sum(b_q[:, None, :] * b_dec, axis=2), 0.0)
        b_G = tl.where(o_c[:, None] > o_c[None, :], tl.sum(b_k[:, None, :] * b_dec, axis=2), 0.0)
        tl.store(gam + p_ck, b_gam, mask=m_k)
        tl.store(G + p_cc, b_G)
        tl.store(A + p_cc, b_A)
        tl.store(Kt + p_ck, b_k * b_E, mask=m_k)
        tl.store(Kh + p_ck, b_k * tl.exp(b_last[None, :] - b_gam), mask=m_k)
        tl.store(Qt + p_ck, b_q * b_E, mask=m_k)
        tl.store(Gam + base * K + o_k, tl.exp(b_last), mask=o_k < K)

    @triton.jit
    def _output_kernel(Qt, A, u, S_before, o, tok_start, tok_len, scale,
                       H: tl.constexpr, C: tl.constexpr, K: tl.constexpr, V: tl.constexpr,
                       BK: tl.constexpr, BV: tl.constexpr, DOT: tl.constexpr):
        i_n = tl.program_id(0).to(tl.int64)
        i_h = tl.program_id(1).to(tl.int64)
        ts = tl.load(tok_start + i_n).to(tl.int64)
        tn = tl.load(tok_len + i_n)
        o_c = tl.arange(0, C)
        o_k = tl.arange(0, BK)
        o_v = tl.arange(0, BV)
        base = i_n * H + i_h
        b_Qt = tl.load(Qt + base * C * K + o_c[:, None] * K + o_k[None, :],
                       mask=(o_c[:, None] < C) & (o_k[None, :] < K), other=0.0)
        b_A = tl.load(A + base * C * C + o_c[:, None] * C + o_c[None, :])
        b_u = tl.load(u + base * C * V + o_c[:, None] * V + o_v[None, :],
                      mask=(o_c[:, None] < C) & (o_v[None, :] < V), other=0.0)
        b_S = tl.load(S_before + base * K * V + o_k[:, None] * V + o_v[None, :],
                      mask=(o_k[:, None] < K) & (o_v[None, :] < V), other=0.0)
        b_o = (_mm(b_Qt, b_S, DOT) + _mm(b_A, b_u, DOT)) * scale
        tl.store(o + ((ts + o_c[:, None]) * H + i_h) * V + o_v[None, :], b_o,
                 mask=(o_c[:, None] < tn) & (o_v[None, :] < V))

    @triton.jit
    def _output_bwd_kernel(do, Qt, A, u, S_before, du, dS, dA, dQt, tok_start, tok_len, scale,
                           H: tl.constexpr, C: tl.constexpr, K: tl.constexpr, V: tl.constexpr,
                           BK: tl.constexpr, BV: tl.constexpr, DOT: tl.constexpr):
        i_n = tl.program_id(0).to(tl.int64)
        i_h = tl.program_id(1).to(tl.int64)
        ts = tl.load(tok_start + i_n).to(tl.int64)
        tn = tl.load(tok_len + i_n)
        o_c = tl.arange(0, C)
        o_k = tl.arange(0, BK)
        o_v = tl.arange(0, BV)
        m_ck = (o_c[:, None] < C) & (o_k[None, :] < K)
        m_cv = (o_c[:, None] < C) & (o_v[None, :] < V)
        m_kv = (o_k[:, None] < K) & (o_v[None, :] < V)
        base = i_n * H + i_h
        p_ck = base * C * K + o_c[:, None] * K + o_k[None, :]
        p_cv = base * C * V + o_c[:, None] * V + o_v[None, :]
        p_cc = base * C * C + o_c[:, None] * C + o_c[None, :]
        p_kv = base * K * V + o_k[:, None] * V + o_v[None, :]
        b_do = tl.load(do + ((ts + o_c[:, None]) * H + i_h) * V + o_v[None, :],
                       mask=(o_c[:, None] < tn) & (o_v[None, :] < V), other=0.0).to(tl.float32) * scale
        b_Qt = tl.load(Qt + p_ck, mask=m_ck, other=0.0)
        b_A = tl.load(A + p_cc)
        b_u = tl.load(u + p_cv, mask=m_cv, other=0.0)
        b_S = tl.load(S_before + p_kv, mask=m_kv, other=0.0)
        tl.store(du + p_cv, _mm(tl.trans(b_A), b_do, DOT), mask=m_cv)
        tl.store(dS + p_kv, _mm(tl.trans(b_Qt), b_do, DOT), mask=m_kv)
        tl.store(dA + p_cc, tl.where(o_c[:, None] >= o_c[None, :], _mm(b_do, tl.trans(b_u), DOT), 0.0))
        tl.store(dQt + p_ck, _mm(b_do, tl.trans(b_S), DOT), mask=m_ck)

    @triton.jit
    def _assemble_kernel(q, k, vp, gam, G, u, yp, du, S_before, dS_next, dA, dQt, dq, dk, dv, dg, dbeta,
                         tok_start, tok_len,
                         H: tl.constexpr, C: tl.constexpr, K: tl.constexpr, V: tl.constexpr,
                         BK: tl.constexpr, BV: tl.constexpr, DOT: tl.constexpr):
        i_n = tl.program_id(0).to(tl.int64)
        i_h = tl.program_id(1).to(tl.int64)
        ts = tl.load(tok_start + i_n).to(tl.int64)
        tn = tl.load(tok_len + i_n)
        o_c = tl.arange(0, C)
        o_k = tl.arange(0, BK)
        o_v = tl.arange(0, BV)
        m_ck = (o_c[:, None] < C) & (o_k[None, :] < K)
        m_cv = (o_c[:, None] < C) & (o_v[None, :] < V)
        m_kv = (o_k[:, None] < K) & (o_v[None, :] < V)
        m_tk = (o_c[:, None] < tn) & (o_k[None, :] < K)
        m_tv = (o_c[:, None] < tn) & (o_v[None, :] < V)
        p_tk = ((ts + o_c[:, None]) * H + i_h) * K + o_k[None, :]
        p_tv = ((ts + o_c[:, None]) * H + i_h) * V + o_v[None, :]
        base = i_n * H + i_h
        p_ck = base * C * K + o_c[:, None] * K + o_k[None, :]
        p_cv = base * C * V + o_c[:, None] * V + o_v[None, :]
        p_cc = base * C * C + o_c[:, None] * C + o_c[None, :]
        p_kv = base * K * V + o_k[:, None] * V + o_v[None, :]
        b_q = tl.load(q + p_tk, mask=m_tk, other=0.0).to(tl.float32)
        b_k = tl.load(k + p_tk, mask=m_tk, other=0.0).to(tl.float32)
        b_gam = tl.load(gam + p_ck, mask=m_ck, other=0.0)
        b_G = tl.load(G + p_cc)
        b_u = tl.load(u + p_cv, mask=m_cv, other=0.0)
        b_v = tl.load(vp + p_cv, mask=m_cv, other=0.0)
        b_yp = tl.load(yp + p_cv, mask=m_cv, other=0.0)
        b_du = tl.load(du + p_cv, mask=m_cv, other=0.0)
        b_S = tl.load(S_before + p_kv, mask=m_kv, other=0.0)
        b_dSn = tl.load(dS_next + p_kv, mask=m_kv, other=0.0)
        b_dA = tl.load(dA + p_cc)
        b_dQt = tl.load(dQt + p_ck, mask=m_ck, other=0.0)

        b_last = tl.sum(tl.where((o_c == C - 1)[:, None], b_gam, 0.0), axis=0)
        b_E = tl.exp(b_gam)
        b_E2 = tl.exp(b_last[None, :] - b_gam)
        b_Kh = b_k * b_E2
        b_y = b_du + _mm(b_Kh, b_dSn, DOT) - _mm(tl.trans(b_G), b_yp, DOT)
        b_e = b_v - _mm(b_k * b_E, b_S, DOT) - _mm(b_G, b_u, DOT)
        tl.store(dbeta + p_tv, b_y * b_e, mask=m_tv)
        tl.store(dv + p_tv, b_yp, mask=m_tv)
        b_dG = tl.where(o_c[:, None] > o_c[None, :], -_mm(b_yp, tl.trans(b_u), DOT), 0.0)
        b_dKt = -_mm(b_yp, tl.trans(b_S), DOT)
        b_dKh = _mm(b_u, tl.trans(b_dSn), DOT)
        b_dGam = tl.sum(b_dSn * b_S, axis=1)

        m_lo = o_c[:, None] >= o_c[None, :]
        b_dec = tl.exp(tl.where(m_lo[:, :, None], b_gam[:, None, :] - b_gam[None, :, :], 0.0))
        w_G = b_dG[:, :, None] * b_dec                       # dG, dA are zero outside their triangles
        w_A = b_dA[:, :, None] * b_dec
        dxG = tl.sum(w_G * b_k[None, :, :], axis=1)
        dyG = tl.sum(w_G * b_k[:, None, :], axis=0)
        dxA = tl.sum(w_A * b_k[None, :, :], axis=1)
        dyA = tl.sum(w_A * b_q[:, None, :], axis=0)
        b_dk = b_dKt * b_E + b_dKh * b_E2 + dxG + dyG + dyA
        b_dq = b_dQt * b_E + dxA
        b_dgam = b_dKt * b_k * b_E + b_dQt * b_q * b_E - b_dKh * b_Kh + b_k * (dxG - dyG) + b_q * dxA - b_k * dyA
        b_dlast = tl.sum(b_dKh * b_Kh, axis=0) + b_dGam * tl.exp(b_last)
        b_dgam += tl.where((o_c == C - 1)[:, None], b_dlast[None, :], 0.0)
        b_dg = tl.cumsum(b_dgam, axis=0, reverse=True)
        tl.store(dq + p_tk, b_dq, mask=m_tk)
        tl.store(dk + p_tk, b_dk, mask=m_tk)
        tl.store(dg + p_tk, b_dg, mask=m_tk)


# ---------------------------------------------------------------------------------------------------------------
# Per-channel inverse M_j = (I + Diag(beta_j) G)^-1 Diag(beta_j): rows x[t] = beta[t, j] * (e_t - sum_{i<t} G[t, i] x[i])
# G [NC, H, C, C] (strictly lower), beta [NC, H, C, V] -> M [NC, H, V, C, C] (lower triangular)
# ---------------------------------------------------------------------------------------------------------------

def _inverse_ref(G, beta):
    C = G.shape[-1]
    eye = torch.eye(C, dtype=G.dtype, device=G.device)
    M = G.new_zeros(*beta.shape[:-2], beta.shape[-1], C, C)
    for t in range(C):
        acc = torch.einsum('...i,...vic->...vc', G[..., t, :], M)
        M[..., t, :] = beta[..., t, :, None] * (eye[t] - acc)
    return M


if triton is not None:

    @triton.jit
    def _inverse_kernel(G, beta, M, C: tl.constexpr, V: tl.constexpr, BV: tl.constexpr):
        pid = tl.program_id(0).to(tl.int64)                             # chunk * H + head
        o_v = tl.program_id(1).to(tl.int64) * BV + tl.arange(0, BV)     # a block of BV value channels
        m_v = o_v < V
        o_c = tl.arange(0, C)
        b_x = tl.zeros([BV, C, C], dtype=tl.float32)
        for t in range(0, C):
            g_row = tl.load(G + pid * C * C + t * C + o_c)
            b_t = tl.load(beta + (pid * C + t) * V + o_v, mask=m_v, other=0.0)
            acc = tl.sum(g_row[None, :, None] * b_x, axis=1)
            x_t = b_t[:, None] * (tl.where(o_c == t, 1.0, 0.0)[None, :] - acc)
            b_x = tl.where((o_c == t)[None, :, None], x_t[:, None, :], b_x)
        tl.store(M + ((pid * V + o_v[:, None, None]) * C + o_c[None, :, None]) * C + o_c[None, None, :], b_x,
                 mask=m_v[:, None, None] & (o_c[None, :, None] < C) & (o_c[None, None, :] < C))


# ---------------------------------------------------------------------------------------------------------------
# Scan over the chunks of every sequence, with the state S [K, V] carried from chunk to chunk:
#   forward:   x[:, j] = M_j   (R - Kin S)[:, j],  S <- Diag(Gam) S + Kout^T x            (x = the writes u)
#   backward:  x[:, j] = M_j^T (R + Kin S)[:, j],  S <- Diag(Gam) S - Kout^T x + add      (chunks in reverse)
# R [NC, H, C, V], Kin, Kout [NC, H, C, K], M [NC, H, V, C, C], Gam [NC, H, K], h0 [N, H, K, V], add [NC, H, K, V]
# -> x [NC, H, C, V], the state before every chunk [NC, H, K, V], the state after the last chunk [N, H, K, V]
# ---------------------------------------------------------------------------------------------------------------

def _scan_ref(R, Kin, Kout, M, Gam, first, n_chunks, h0, add, backward):
    NC, H, C, V = R.shape
    K = Kin.shape[-1]
    x = torch.zeros_like(R)
    S_before = R.new_zeros(NC, H, K, V)
    final = R.new_zeros(first.numel(), H, K, V)
    for s, (n0, nn) in enumerate(zip(first.tolist(), n_chunks.tolist())):
        S = R.new_zeros(H, K, V) if h0 is None else h0[s]
        chunks = range(n0, n0 + nn)
        for n in (reversed(chunks) if backward else chunks):
            S_before[n] = S
            if backward:
                x[n] = torch.einsum('hvic,hiv->hcv', M[n], R[n] + Kin[n] @ S)
                S = Gam[n].unsqueeze(-1) * S - Kout[n].transpose(-1, -2) @ x[n] + add[n]
            else:
                x[n] = torch.einsum('hvci,hiv->hcv', M[n], R[n] - Kin[n] @ S)
                S = Gam[n].unsqueeze(-1) * S + Kout[n].transpose(-1, -2) @ x[n]
        final[s] = S
    return x, S_before, final


if triton is not None:

    @triton.jit
    def _scan_kernel(R, Kin, Kout, M, Gam, h0, add, first, n_chunks, x, S_before, final,
                     H: tl.constexpr, C: tl.constexpr, K: tl.constexpr, V: tl.constexpr,
                     BK: tl.constexpr, BV: tl.constexpr, USE_H0: tl.constexpr, BACKWARD: tl.constexpr,
                     DOT: tl.constexpr):
        i_sh = tl.program_id(0).to(tl.int64)    # sequence * H + head
        i_s = i_sh // H
        i_h = i_sh % H
        n0 = tl.load(first + i_s).to(tl.int64)
        nn = tl.load(n_chunks + i_s).to(tl.int64)
        o_c = tl.arange(0, C)
        o_k = tl.arange(0, BK)
        o_v = tl.program_id(1).to(tl.int64) * BV + tl.arange(0, BV)     # a block of BV value channels
        m_k = o_k < K
        m_v = o_v < V
        m_kv = m_k[:, None] & m_v[None, :]
        m_cv = (o_c[:, None] < C) & m_v[None, :]
        m_ck = (o_c[:, None] < C) & m_k[None, :]
        m_vcc = m_v[:, None, None] & (o_c[None, :, None] < C) & (o_c[None, None, :] < C)
        o_kv = o_k[:, None] * V + o_v[None, :]
        o_cv = o_c[:, None] * V + o_v[None, :]
        o_ck = o_c[:, None] * K + o_k[None, :]
        o_vcc = (o_v[:, None, None] * C + o_c[None, :, None]) * C + o_c[None, None, :]
        if USE_H0:
            b_S = tl.load(h0 + (i_s * H + i_h) * K * V + o_kv, mask=m_kv, other=0.0)
        else:
            b_S = tl.zeros([BK, BV], dtype=tl.float32)
        for m in range(0, nn):
            if BACKWARD:
                n = n0 + nn - 1 - m
            else:
                n = n0 + m
            base = n * H + i_h
            tl.store(S_before + base * K * V + o_kv, b_S, mask=m_kv)
            b_R = tl.load(R + base * C * V + o_cv, mask=m_cv, other=0.0)
            b_Kin = tl.load(Kin + base * C * K + o_ck, mask=m_ck, other=0.0)
            b_Kout = tl.load(Kout + base * C * K + o_ck, mask=m_ck, other=0.0)
            b_M = tl.load(M + base * V * C * C + o_vcc, mask=m_vcc, other=0.0)
            b_g = tl.load(Gam + base * K + o_k, mask=m_k, other=0.0)
            if BACKWARD:
                b_r = b_R + _mm(b_Kin, b_S, DOT)
                b_x = tl.trans(tl.sum(b_M * tl.trans(b_r)[:, :, None], axis=1))               # M_j^T r[:, j]
            else:
                b_r = b_R - _mm(b_Kin, b_S, DOT)
                b_x = tl.trans(tl.sum(b_M * tl.trans(b_r)[:, None, :], axis=2))               # M_j r[:, j]
            tl.store(x + base * C * V + o_cv, b_x, mask=m_cv)
            if BACKWARD:
                b_S = b_g[:, None] * b_S - _mm(tl.trans(b_Kout), b_x, DOT) \
                    + tl.load(add + base * K * V + o_kv, mask=m_kv, other=0.0)
            else:
                b_S = b_g[:, None] * b_S + _mm(tl.trans(b_Kout), b_x, DOT)
        tl.store(final + (i_s * H + i_h) * K * V + o_kv, b_S, mask=m_kv)


def _scan(R, Kin, Kout, M, Gam, first, n_chunks, h0=None, add=None, backward=False, use_triton=False):
    if not use_triton:
        return _scan_ref(R, Kin, Kout, M, Gam, first, n_chunks, h0, add, backward)
    NC, H, C, V = R.shape
    K = Kin.shape[-1]
    N = first.numel()
    x = torch.empty_like(R)                  # chunks past the last sequence are never read into a result
    S_before = R.new_empty(NC, H, K, V)
    final = R.new_empty(N, H, K, V)
    BK = triton.next_power_of_2(K)
    # the block M [BV, C, C] of a program must stay small (16 value channels at C = 16)
    BV = max(1, min(TUNING["scan_value_block"], triton.next_power_of_2(V), 4096 // (C * C)))
    _scan_kernel[(N * H, triton.cdiv(V, BV))](R, Kin, Kout, M, Gam, h0, add, first, n_chunks, x, S_before, final,
                                              H=H, C=C, K=K, V=V, BK=BK, BV=BV, USE_H0=h0 is not None,
                                              BACKWARD=backward, DOT=min(C, BK, BV) >= 16,
                                              num_warps=TUNING["scan_warps"])
    return x, S_before, final


# ---------------------------------------------------------------------------------------------------------------
# The op: packed tokens in, packed tokens out, hand-derived backward
# ---------------------------------------------------------------------------------------------------------------

class _ChunkDeltaValue(torch.autograd.Function):
    """q, k, g [T, H, K], v, beta [T, H, V] -> o [T, H, V] (float32 / float64), final states [N, H, K, V]."""

    @staticmethod
    def forward(ctx, q, k, v, g, beta, h0, cu_seqlens, C, scale):
        T, H, K = k.shape
        V = v.shape[-1]
        use_triton = triton is not None and k.is_cuda and k.dtype != torch.float64
        dtype = torch.float64 if k.dtype == torch.float64 else torch.float32
        lay = _chunk_layout(cu_seqlens, T, C)
        NC, first, n_chunks = lay["NC"], lay["first"], lay["n_chunks"]
        if use_triton:
            q, k, v, g, beta = q.contiguous(), k.contiguous(), v.contiguous(), g.contiguous(), beta.contiguous()
            BK, BV = triton.next_power_of_2(K), triton.next_power_of_2(V)
            dims = dict(H=H, C=C, K=K, V=V, BK=BK, BV=BV)
            new = lambda *shape: torch.empty(*shape, dtype=dtype, device=k.device)   # noqa: E731
            gam, Kt, Kh, Qt = new(NC, H, C, K), new(NC, H, C, K), new(NC, H, C, K), new(NC, H, C, K)
            G, A, Gam, vp, bp = new(NC, H, C, C), new(NC, H, C, C), new(NC, H, K), new(NC, H, C, V), new(NC, H, C, V)
            _prep_kernel[(NC, H)](q, k, v, g, beta, lay["tok_start"], lay["tok_len"], gam, G, A, Kt, Kh, Qt, Gam, vp, bp,
                                  **dims, num_warps=TUNING["chunk_warps"])
            M = new(NC, H, V, C, C)
            BVI = min(TUNING["inverse_value_block"], BV)
            _inverse_kernel[(NC * H, triton.cdiv(V, BVI))](G, bp, M, C=C, V=V, BV=BVI, num_warps=TUNING["inverse_warps"])
            slot = None
        else:
            slot = _slots(lay, T, C)
            qp, kp, vp, gp, bp = (_pad(x.to(dtype), slot, NC, C) for x in (q, k, v, g, beta))
            gam, G, A, Kt, Kh, Qt, Gam = _prep_ref(qp, kp, gp)
            M = _inverse_ref(G, bp)
        u, S_before, final = _scan(vp, Kt, Kh, M, Gam, first, n_chunks, h0=h0, use_triton=use_triton)
        if use_triton:
            o = new(T, H, V)
            _output_kernel[(NC, H)](Qt, A, u, S_before, o, lay["tok_start"], lay["tok_len"], scale, **dims,
                                    DOT=min(C, BK, BV) >= 16, num_warps=TUNING["chunk_warps"])
        else:
            o = _unpad(_output_ref(Qt, A, u, S_before, scale), slot)
        ctx.save_for_backward(q, k, vp, gam, G, A, Kt, Kh, Qt, Gam, M, u, S_before, first, n_chunks,
                              lay["tok_start"], lay["tok_len"], slot)
        ctx.use_triton, ctx.scale = use_triton, scale
        ctx.dtypes = (q.dtype, k.dtype, v.dtype, g.dtype, beta.dtype)
        ctx.mark_non_differentiable(final)
        return o, final

    @staticmethod
    def backward(ctx, do, _):
        (q, k, vp, gam, G, A, Kt, Kh, Qt, Gam, M, u, S_before, first, n_chunks, tok_start, tok_len, slot) = ctx.saved_tensors
        NC, H, C, K = gam.shape
        T, V = k.shape[0], u.shape[-1]
        if ctx.use_triton:
            do = do.contiguous()
            BK, BV = triton.next_power_of_2(K), triton.next_power_of_2(V)
            dims = dict(H=H, C=C, K=K, V=V, BK=BK, BV=BV, DOT=min(C, BK, BV) >= 16, num_warps=TUNING["chunk_warps"])
            du, dS, dA, dQt = torch.empty_like(u), torch.empty_like(S_before), torch.empty_like(A), torch.empty_like(Qt)
            _output_bwd_kernel[(NC, H)](do, Qt, A, u, S_before, du, dS, dA, dQt, tok_start, tok_len, ctx.scale, **dims)
        else:
            du, dS, dA, dQt = _output_bwd_ref(_pad(do.to(gam.dtype), slot, NC, C), Qt, A, u, S_before, ctx.scale)
        # With du_j = du_ext_j + Kh dS_next[:, j] (known only inside the reverse scan) and the adjoint of the solve
        # y_j = (I + Diag(beta_j) G)^-T du_j:  yp_j = beta_j * y_j = M_j^T du_j, and the state gradient follows
        # dS = Diag(Gam) dS_next + dS_ext - Kt^T yp: the forward scan with M transposed and Kt, Kh swapped.
        yp, dS_next, _ = _scan(du, Kh, Kt, M, Gam, first, n_chunks, h0=None, add=dS, backward=True,
                               use_triton=ctx.use_triton)
        if ctx.use_triton:
            dq, dk, dg = (torch.empty(T, H, K, dtype=gam.dtype, device=gam.device) for _ in range(3))
            dv, dbeta = (torch.empty(T, H, V, dtype=gam.dtype, device=gam.device) for _ in range(2))
            _assemble_kernel[(NC, H)](q, k, vp, gam, G, u, yp, du, S_before, dS_next, dA, dQt, dq, dk, dv, dg, dbeta,
                                      tok_start, tok_len, **dims)
        else:
            qp, kp = _pad(q.to(gam.dtype), slot, NC, C), _pad(k.to(gam.dtype), slot, NC, C)
            grads = _assemble_ref(qp, kp, vp, gam, G, u, yp, du, S_before, dS_next, dA, dQt)
            dq, dk, dv, dg, dbeta = (_unpad(x, slot) for x in grads)
        grads = tuple(x.to(dt) for x, dt in zip((dq, dk, dv, dg, dbeta), ctx.dtypes))
        return (*grads, None, None, None, None)


def chunk_delta_value(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    g: torch.Tensor,
    beta: torch.Tensor,
    scale: float | None = None,
    initial_state: torch.Tensor | None = None,
    output_final_state: bool = False,
    cu_seqlens: torch.Tensor | None = None,
    chunk_size: int = 16,
):
    """Chunkwise delta_value rule (recurrence in naive.py).

    Args:
        q, k: [B, T, H, K], already L2-normalised. v, beta: [B, T, H, V], beta in (0, 1). g: log-decay [B, T, H, K].
        scale: read-out scale, default K ** -0.5.
        initial_state: optional [N, H, K, V] (no gradient), N sequences.
        cu_seqlens: [N + 1] sequence boundaries of a packed batch (B == 1).
        chunk_size: power of two; the inverses cost O(chunk_size^2) per token, the scan T / chunk_size steps.

    Returns:
        o [B, T, H, V] in v's dtype, final state [N, H, K, V] (float32) or None.
    """
    B, T, H, K = k.shape
    V = v.shape[-1]
    assert chunk_size & (chunk_size - 1) == 0, f"chunk_size must be a power of two, got {chunk_size}."
    if scale is None:
        scale = K ** -0.5
    if cu_seqlens is None:
        cu_seqlens = torch.arange(B + 1, device=q.device) * T
    else:
        assert B == 1, "cu_seqlens needs a packed batch of size 1."
    h0 = None
    if initial_state is not None:
        h0 = initial_state.detach().to(torch.float64 if k.dtype == torch.float64 else torch.float32).contiguous()
    with torch.autocast(device_type=q.device.type, enabled=False):
        o, final = _ChunkDeltaValue.apply(q.reshape(B * T, H, K), k.reshape(B * T, H, K), v.reshape(B * T, H, V),
                                          g.reshape(B * T, H, K), beta.reshape(B * T, H, V), h0, cu_seqlens,
                                          chunk_size, scale)
    return o.view(B, T, H, V).to(v.dtype), (final if output_final_state else None)
