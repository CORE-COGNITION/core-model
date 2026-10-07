#!/usr/bin/env python
"""Fig. 3 of the paper: learning rates and memory timescales of CORE (run 2209, temperature 1).

  A-B  distributions of the learning rate beta and the memory timescale tau per layer, over all tokens of the
       simulated experiments (every experiment has equal weight), pooled over the four heads
  C-D  single layer-5 channels over the course of a game and at the boundary to the next game

Steps (run from core-model/, with env_full):
  python plotting/fig3_latents.py reduce <latents.pth> ...  # A-B: histograms -> plotting/gate_cache/<experiment>__<agent>.npz
  python plotting/fig3_latents.py channels                  # C-D: per-channel curves and table -> plotting/gate_cache/channels_fb.*
  python plotting/fig3_latents.py plot                      # -> paper/figures/fig3_latents.{pdf,png}; numbers -> plotting/gate_cache/fig3_latents.txt

Inputs
  A-B  psych201_agentic/results_simulations/*_latents.pth of one agent (simulate_core.py): per-token gates of every
       simulated participant, fp16 [num_layers, T, num_heads], each the mean over the head's 32 channels.
       tau = -1 / log_alpha in tokens (1/e decay time of the head's mean log retention).
  C-D  *_channels.npz (psych201_agentic/replay_channels.py, scripts/replay_channels.sh; the 18 game experiments,
       no dubois_2022): per press and channel (6 layers x 4 heads x 32), the gates over the feedback of the press
       (beta_fb, la_fb) and over the post segment (beta_post, la_post); the per-press cache
       plotting/cache_2209 (press order, game structure; plotting/build_cache.py); the press positions of the *_latents.pth
       (post-segment lengths, cached in plotting/gate_cache/post_len/).

Definitions (C-D)
  games     first CSV column of task, game_id, task_id, block, context (>= 4 games per participant, >= 5 presses
            in the game of the median press); games with >= NBIN presses. For some experiments a game is a block.
  feedback  the tokens after a press up to the end of its feedback line (the phoneme tokenizer drops line breaks;
            replay_channels.py finds the end by tokenizing the feedback text alone).
  x         fraction of the game in NBIN bins of press position / (game length - 1), every press of the game
            (the last press is in the last bin); points at the bin edges (.2 ... 1).
  boundary  the text after the feedback of a game's last press up to the first press of the next game (its intro
            and first stimulus), for games that another game follows:
            (n_post * post - n_fb * fb) / (n_post - n_fb) from the saved means (checked against direct token means).
  averaging participant mean per bin, then mean over participants, then over experiments; tau as mean log10 tau.
            Band / error bar: ± SEM over experiments of the within-participant change (the participant's mean over
            the bins subtracted).
  pick      the channel of layer LAYER_CD with the largest mean change among the channels where >= AGREE of the
            experiments agree: largest decrease of beta over the game (first -> last fifth), largest drop of tau
            from the last fifth to the boundary.
Caveat: the gates depend on the input tokens; the boundary text differs from the feedback text, so part of the drop
at the boundary may be text (a layer-1 channel also drops there).
"""
import argparse
import glob
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CACHE = os.path.join(HERE, "gate_cache")
OUT = os.path.join(REPO, "paper", "figures", "fig3_latents")
SIM_DIR = os.path.join(REPO, "psych201_agentic", "results_simulations")
EXPERIMENTS_JSON = os.path.join(REPO, "psych201_agentic", "experiments.json")
AGENT = "trained_core-phoneme-d128-L6-fgT-wd0.5-h4-lrdelta-2209_temp1"

CACHE_2209 = os.path.join(HERE, "cache_2209")        # per-press cache of the agent (build_cache.py)

# A-B
BETA_EDGES = np.linspace(0.0, 1.0, 101)
LOGTAU_EDGES = np.linspace(-1.0, 5.0, 121)  # log10 tau in tokens; outside values go to the end bins
# C-D
LAYER_CD = 5            # 1-based
NBIN = 5
AGREE = 0.8             # share of experiments that must agree for a channel to be picked
TAU_CAP = 1e4           # tokens; log alpha is clipped at -1/TAU_CAP
MIN_ALIGNED = 0.9       # experiments whose presses join their CSV (bahrami, cohen do not)
END_X = 1.2             # x of the boundary point
MEASURES = ("beta", "logtau")


# ---------------------------------------------------------------- per-press cache and games

GAME_COLS = ("task", "game_id", "task_id", "block", "context")  # first present column defines games
# game = new, independent problem: >= 4 games per participant, >= 5 presses in the game of the median press
# (drops two-step trials, sessions, conditions and phases coded as blocks)
MIN_GAMES, MIN_GAME_LEN = 4, 5


def selected_experiments():
    """<study>_<exp> of the experiments selected in experiments.json (the effect analysis uses the same set)."""
    return {f"{x['study']}_{x['exp']}" for x in json.load(open(EXPERIMENTS_JSON)) if x.get("selected")}


def list_experiments():
    return sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(CACHE_2209, "*.npz")))


def load_cache(exp):
    """One experiment's per-press cache as a dict of arrays (+ scalars unwrapped)."""
    z = np.load(os.path.join(CACHE_2209, f"{exp}.npz"), allow_pickle=False)
    d = {k: z[k] for k in z.files}
    for k in ("experiment", "agent", "csv_path"):
        d[k] = str(d[k])
    if not os.path.isabs(d["csv_path"]):  # cache stores repo-root-relative paths
        d["csv_path"] = os.path.join(REPO, d["csv_path"])
    for k in ("num_layers", "num_heads"):
        d[k] = int(d[k])
    return d


def press_frame(d, csv_cols=()):
    """Per-press DataFrame: participant, press_idx, press_class, row_index,
    plus requested CSV columns joined via row_index (NaN where unaligned)."""
    df = pd.DataFrame({
        "participant": d["participant"],
        "press_idx": d["press_idx"],
        "press_class": d["press_class"],
        "row_index": d["row_index"],
    })
    if csv_cols:
        sim = pd.read_csv(d["csv_path"])
        cols = [c for c in csv_cols if c in sim.columns]
        ok = df["row_index"].to_numpy() >= 0
        for c in cols:
            vals = np.full(len(df), np.nan, dtype=object)
            vals[ok] = sim[c].to_numpy()[df["row_index"].to_numpy()[ok]]
            try:
                df[c] = pd.to_numeric(pd.Series(vals))
            except (ValueError, TypeError):
                df[c] = vals
    return df


def game_structure(d):
    """Per-press game structure from the first CSV column of GAME_COLS, or None if the experiment has no game
    structure. Returns int arrays aligned with presses: game (id), pos (press position within the game, 0-based),
    glen (presses in that game), first/last (bool: the participant's first/last game)."""
    df = press_frame(d, csv_cols=GAME_COLS)
    col = next((c for c in GAME_COLS if c in df.columns and not df[c].isna().all()), None)
    if col is None:
        return None
    df["task"] = df[col]
    if df.groupby("participant")["task"].nunique().median() < MIN_GAMES:
        return None
    grp = df.groupby(["participant", "task"])
    pos = grp.cumcount().to_numpy()
    glen = grp["press_idx"].transform("size").to_numpy()
    if np.median(glen) < MIN_GAME_LEN:  # median over presses (horizon tasks: 1- and 6-choice games)
        return None
    pg = df.groupby("participant")["task"]
    return {
        "game": df["task"].to_numpy(),
        "pos": pos,
        "glen": glen,
        "first": (df["task"] == pg.transform("first")).to_numpy(),
        "last": (df["task"] == pg.transform("last")).to_numpy(),
    }


# ---------------------------------------------------------------- style (dataviz reference palette)

LAYER = ["#86b6ef", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281"]  # layers 1..6, light -> dark
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"


def apply_style():
    import matplotlib as mpl
    mpl.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "axes.edgecolor": "#c3c2b7",
        "axes.labelcolor": INK2,
        "axes.titlecolor": INK,
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "legend.frameon": False,
        "lines.linewidth": 1.6,
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"],
    })


# ---------------------------------------------------------------- A-B: distributions over all tokens

def reduce(paths):
    import torch
    os.makedirs(CACHE, exist_ok=True)
    for path in paths:
        d = torch.load(path, weights_only=False, map_location="cpu", mmap=True)  # dubois is 13.5 GB
        L, _, H = d["participants"][0]["beta"].shape
        hb = np.zeros((L, H, len(BETA_EDGES) - 1))
        ht = np.zeros((L, H, len(LOGTAU_EDGES) - 1))
        n = 0
        for p in d["participants"]:
            beta = p["beta"].float().numpy()
            la = p["log_alpha"].float().numpy()
            logtau = np.log10(1.0 / np.maximum(-la, 1e-12))
            logtau = np.clip(logtau, LOGTAU_EDGES[0], LOGTAU_EDGES[-1] - 1e-9)
            for l in range(L):
                for h in range(H):
                    hb[l, h] += np.histogram(beta[l, :, h], BETA_EDGES)[0]
                    ht[l, h] += np.histogram(logtau[l, :, h], LOGTAU_EDGES)[0]
            n += beta.shape[1]
        out = os.path.join(CACHE, f"{d['experiment']}__{d['agent']}.npz")
        np.savez(out, beta_hist=hb, logtau_hist=ht, beta_edges=BETA_EDGES, logtau_edges=LOGTAU_EDGES,
                 n_tokens=n, n_participants=len(d["participants"]))
        print(f"{d['experiment']}: {len(d['participants'])} participants, {n} tokens -> {out}", flush=True)


def load_hist(agent):
    selected = selected_experiments()
    files = sorted(f for f in glob.glob(os.path.join(CACHE, f"*__{agent}.npz"))
                   if os.path.basename(f).split("__")[0] in selected)
    if not files:
        raise SystemExit(f"no cache files for {agent} in {CACHE}")
    hb, ht = [], []
    for f in files:
        z = np.load(f)
        b = z["beta_hist"].sum(axis=1)       # [L, bins], heads pooled
        t = z["logtau_hist"].sum(axis=1)
        hb.append(b / b.sum(axis=1, keepdims=True))
        ht.append(t / t.sum(axis=1, keepdims=True))
    return np.mean(hb, axis=0), np.mean(ht, axis=0), len(files)


def weighted_median(p, edges):
    c = np.cumsum(p)
    i = np.searchsorted(c, 0.5)
    lo = c[i - 1] if i > 0 else 0.0
    return edges[i] + (0.5 - lo) / (c[i] - lo) * (edges[i + 1] - edges[i])


def ridges(axes, pb, pt):
    """Panels A-B: one ridge per layer, deep layers on top; black ticks at the medians."""
    L = pb.shape[0]
    step = 1.0     # vertical offset between layers
    height = 1.3   # peak height relative to the offset (ridges overlap slightly)
    panels = [
        (axes[0], pb, BETA_EDGES, r"learning rate $\beta$", False),
        (axes[1], pt, LOGTAU_EDGES, r"memory timescale $\tau$", True),
    ]
    for ax, p, edges, xlabel, logx in panels:
        centers = 0.5 * (edges[:-1] + edges[1:])
        x = 10 ** centers if logx else centers
        for l in reversed(range(L)):          # deep layers at the top, drawn first
            y0 = l * step
            s = p[l]  # no smoothing: layer 1 gates take few distinct values (one per phoneme)
            y = y0 + s * height * step / s.max()  # each layer scaled to its own peak
            color = LAYER[l]
            ax.fill_between(x, y0, y, color=color, alpha=0.85, linewidth=0, zorder=2 * (L - l))
            ax.plot(x, y, color=SURFACE, linewidth=1.2, zorder=2 * (L - l) + 1)
            m = weighted_median(p[l], edges)
            mx = 10 ** m if logx else m
            ax.plot([mx, mx], [y0, y0 + 0.35 * step], color=INK, linewidth=1.0,
                    zorder=2 * (L - l) + 1, solid_capstyle="butt")
        if logx:
            ax.set_xscale("log")
            used = np.nonzero(p.max(axis=0) > 1e-4)[0]  # bins with mass in any layer
            ax.set_xlim(10 ** np.floor(edges[used[0]]), 10 ** np.ceil(edges[used[-1] + 1]))
            ticks = [t for t in (0.1, 1, 10, 100, 1000) if ax.get_xlim()[0] <= t <= ax.get_xlim()[1]]
            ax.set_xticks(ticks, [str(t) for t in ticks])
        else:
            ax.set_xlim(edges[0], edges[-1])
        ax.set_xlabel(xlabel)
        ax.grid(axis="y", visible=False)
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)
    axes[0].set_yticks([l * step for l in range(L)])
    axes[0].set_yticklabels([f"layer {l + 1}" for l in range(L)], color=INK2, fontsize=8)
    axes[0].set_ylim(-0.1, (L - 1) * step + height * 1.05)


# ---------------------------------------------------------------- C-D: channels over a game

def channel_experiments():
    """The 2209 experiments with a channel file whose presses join their CSV rows."""
    out = []
    selected = selected_experiments()
    for e in list_experiments():
        if e not in selected:
            continue
        if not os.path.exists(os.path.join(SIM_DIR, f"experiment={e}_agent={AGENT}_channels.npz")):
            continue
        if (load_cache(e)["row_index"] >= 0).mean() >= MIN_ALIGNED:
            out.append(e)
    return out


def game_fraction(d):
    """(bins, xbin, end): presses of games with >= NBIN presses, their bin, and the last presses of games that
    another game follows (they give the boundary point)."""
    gs = game_structure(d)
    ok = gs["glen"] >= NBIN
    end = ok & (gs["pos"] == gs["glen"] - 1) & ~gs["last"]
    xbin = np.minimum((gs["pos"] / np.maximum(gs["glen"] - 1, 1) * NBIN).astype(int), NBIN - 1)
    return ok, xbin, end


def bin_means(v, part, bins, xbin, end, v_end):
    """v [N, K] per press -> participant mean per bin, then mean over participants: raw and delta [NBIN, K]
    (delta = minus the participant's mean over the bins); v_end at the end presses -> raw_end, delta_end [K]
    against the same participant baseline; level [K] = mean over participants and bins."""
    f = pd.DataFrame(v[bins])
    f["p"], f["x"] = part[bins], xbin[bins]
    pm = f.groupby(["p", "x"]).mean().unstack("x").stack("x", future_stack=True)   # participant x bin
    base = pm.groupby(level="p").mean()                                            # participant baseline
    dl = pm - pm.groupby(level="p").transform("mean")
    fe = pd.DataFrame(v_end[end])
    fe["p"] = part[end]
    pe = fe.groupby("p").mean()
    both = pe.index.intersection(base.index)
    return {"raw": pm.groupby(level="x").mean().reindex(range(NBIN)).to_numpy(),
            "delta": dl.groupby(level="x").mean().reindex(range(NBIN)).to_numpy(),
            "raw_end": pe.loc[both].mean().to_numpy(),
            "delta_end": (pe.loc[both] - base.loc[both]).mean().to_numpy(),
            "level": pm.mean().to_numpy()}


def post_len(exp):
    """Tokens of the post segment of every press ([N], row order of the cache): press k + 1 up to the next
    press (exclusive), or to the end of the transcript."""
    path = os.path.join(CACHE, "post_len", f"{exp}_post_len.npy")
    if os.path.exists(path):
        return np.load(path)
    import torch
    lat = torch.load(os.path.join(SIM_DIR, f"experiment={exp}_agent={AGENT}_latents.pth"),
                     weights_only=False, map_location="cpu", mmap=True)
    out = []
    for rec in lat["participants"]:
        pp = rec["press_positions"].numpy().astype(np.int64)
        out.append(np.r_[pp[1:], len(rec["token_ids"])] - pp - 1)
    out = np.concatenate(out).astype(np.int32)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.save(path, out)
    return out


def boundary_values(z, rows, n_post):
    """{measure: [n, L, H, D]} gates over the boundary text of the given presses: after the feedback up to the
    next press; NaN where there is no such text."""
    n_all = n_post[rows][:, None, None, None].astype(np.float64)
    n_fb = z["fb_len"][rows][:, None, None, None].astype(np.float64)
    n_bd = n_all - n_fb
    with np.errstate(invalid="ignore", divide="ignore"):
        beta = (n_all * z["beta_post"][rows] - n_fb * z["beta_fb"][rows]) / n_bd
        la = (n_all * z["la_post"][rows] - n_fb * z["la_fb"][rows]) / n_bd
    ok = (n_bd > 0) & (z["fb_len"][rows][:, None, None, None] >= 0)
    beta, la = np.where(ok, beta, np.nan), np.where(ok, la, np.nan)
    la = np.minimum(la, -1.0 / TAU_CAP)
    return {"beta": beta.astype(np.float32), "logtau": np.log10(-1.0 / la).astype(np.float32)}


def experiment_curves(exp):
    """{measure: (delta, raw) [NBIN + 1, L, H, D], level [L, H, D]} for one experiment; index NBIN = boundary."""
    d = load_cache(exp)
    df = press_frame(d)
    z = np.load(os.path.join(SIM_DIR, f"experiment={exp}_agent={AGENT}_channels.npz"))
    assert np.array_equal(z["participant"], d["participant"]) and np.array_equal(z["press_idx"], d["press_idx"]), exp
    la = np.minimum(z["la_fb"].astype(np.float32), -1.0 / TAU_CAP)
    g = {"beta": z["beta_fb"].astype(np.float32), "logtau": np.log10(-1.0 / la)}
    bins, xbin, end = game_fraction(d)
    part = df["participant"].to_numpy()
    n_post = post_len(exp)
    assert len(n_post) == len(df), exp
    rows = np.nonzero(end)[0]
    bd = boundary_values(z, rows, n_post)
    out = {}
    for m, v in g.items():
        shape = v.shape[1:]
        v_end = np.full(v.shape, np.nan, dtype=np.float32)
        v_end[rows] = bd[m]
        r = bin_means(v.reshape(len(v), -1), part, bins, xbin, end, v_end.reshape(len(v), -1))
        out[m] = (np.vstack([r["delta"], r["delta_end"]]).reshape(NBIN + 1, *shape),
                  np.vstack([r["raw"], r["raw_end"]]).reshape(NBIN + 1, *shape),
                  r["level"].reshape(shape))
    print(f"{exp}: {bins.sum()} presses, {end.sum()} game boundaries", flush=True)
    return out


def tau_pct(x):
    return 100 * (10 ** x - 1)


def channels():
    """Per-channel curves (gate_cache/channels_fb.npz) and table (gate_cache/channels_fb.csv): change over the game
    (last minus first fifth) and at the boundary (boundary minus last fifth); beta raw, tau in percent."""
    exps = channel_experiments()
    res = [experiment_curves(e) for e in exps]
    E = len(exps)
    delta = {m: np.array([r[m][0] for r in res]) for m in MEASURES}     # [E, NBIN + 1, L, H, D]
    raw = {m: np.array([r[m][1] for r in res]) for m in MEASURES}
    level = {m: np.array([r[m][2] for r in res]) for m in MEASURES}     # [E, L, H, D]
    os.makedirs(CACHE, exist_ok=True)
    np.savez(os.path.join(CACHE, "channels_fb.npz"), experiments=np.array(exps),
             **{f"delta_{m}": delta[m] for m in MEASURES}, **{f"raw_{m}": raw[m] for m in MEASURES})
    _, _, L, H, D = delta["beta"].shape
    need = int(np.ceil(AGREE * E))
    rows = []
    for m in MEASURES:
        ch = delta[m][:, NBIN - 1] - delta[m][:, 0]                      # [E, L, H, D]
        mean = ch.mean(axis=0)
        same = (np.sign(ch) == np.sign(mean)[None]).sum(axis=0)
        bd = delta[m][:, NBIN] - delta[m][:, NBIN - 1]                   # boundary minus last fifth
        bd_mean, bd_down = np.nanmean(bd, axis=0), (bd < 0).sum(axis=0)
        lvl = level[m].mean(axis=0)
        f = tau_pct if m == "logtau" else (lambda x: x)
        for l in range(L):
            for h in range(H):
                for c in range(D):
                    rows.append({"measure": m, "layer": l + 1, "head": h + 1, "channel": c + 1,
                                 "level": 10 ** lvl[l, h, c] if m == "logtau" else lvl[l, h, c],
                                 "change": f(mean[l, h, c]), "n_same_sign": int(same[l, h, c]),
                                 "boundary_change": f(bd_mean[l, h, c]), "n_boundary_down": int(bd_down[l, h, c]),
                                 "n_exp": E})
    tab = pd.DataFrame(rows)
    tab["consistent"] = tab["n_same_sign"] >= need
    tab["boundary_consistent_down"] = tab["n_boundary_down"] >= need
    tab.to_csv(os.path.join(CACHE, "channels_fb.csv"), index=False)
    print(f"\n{E} experiments; consistent = >= {need} agree. Consistent channels per layer "
          f"(over the game: down / up; at the boundary: down):")
    for m in MEASURES:
        t = tab[tab.measure == m]
        for l in range(1, L + 1):
            tl = t[t.layer == l]
            print(f"  {m} layer {l}: {int((tl.consistent & (tl.change < 0)).sum())} / "
                  f"{int((tl.consistent & (tl.change > 0)).sum())}; {int(tl.boundary_consistent_down.sum())}")

    # replication: split the studies in two halves (200 random splits, seed 0); per layer, Spearman r of the
    # channel changes between the halves, and the share of the top-20 channels of one half (layers 4-6)
    # whose change has the same sign in the other half
    from scipy.stats import spearmanr
    study = [e.rsplit("_exp", 1)[0] for e in exps]
    studies = sorted(set(study))
    rng = np.random.default_rng(0)
    print(f"\nsplit-half replication over {len(studies)} studies (median r over 200 splits; top-20 sign agreement)")
    for m in MEASURES:
        ch = delta[m][:, NBIN - 1] - delta[m][:, 0]
        rs, hits = [], []
        for _ in range(200):
            half = set(rng.permutation(studies)[:len(studies) // 2])
            a = ch[[i for i, s in enumerate(study) if s in half]].mean(axis=0).reshape(L, -1)
            b = ch[[i for i, s in enumerate(study) if s not in half]].mean(axis=0).reshape(L, -1)
            rs.append([spearmanr(a[l], b[l]).statistic for l in range(L)])
            fa, fb = a[3:].ravel(), b[3:].ravel()
            top = np.argsort(-np.abs(fa))[:20]
            hits.append((np.sign(fa[top]) == np.sign(fb[top])).mean())
        print(f"{m}: r per layer {np.round(np.median(rs, axis=0), 2)}, top-20 sign agreement {np.mean(hits):.2f}")


def test(change):
    """Per-experiment changes -> (n decrease, n increase, sign-test p, t, t-test p, degrees of freedom)."""
    from scipy.stats import binomtest, ttest_1samp
    change = change[np.isfinite(change)]
    n_dec, n_inc = int((change < 0).sum()), int((change > 0).sum())
    tt = ttest_1samp(change, 0)
    return n_dec, n_inc, binomtest(n_dec, n_dec + n_inc).pvalue, tt.statistic, tt.pvalue, len(change) - 1


def pick(t, col, rule_col, lines, what):
    """Channel with the smallest value of col among rows where rule_col holds (all rows if none)."""
    if not t[rule_col].any():
        lines.append(f"  note: no channel meets the rule for '{what}'; picked among all channels")
        return t.sort_values(col).iloc[0]
    return t[t[rule_col]].sort_values(col).iloc[0]


def channel_panel(ax, cur, m, r, lines):
    """Panels C-D: one channel in raw units over the game (solid) and, for tau, the boundary (dashed)."""
    import matplotlib
    l, h, c = int(r.layer) - 1, int(r["head"]) - 1, int(r.channel) - 1
    raw, dl = cur[f"raw_{m}"][:, :, l, h, c], cur[f"delta_{m}"][:, :, l, h, c]   # [E, NBIN + 1]
    E = len(raw)
    boundary = m == "logtau"
    mean = np.nanmean(raw, axis=0)
    sem = np.nanstd(dl, axis=0, ddof=1) / np.sqrt(np.isfinite(dl).sum(axis=0))
    lo, hi, per_exp = mean - sem, mean + sem, raw
    if m == "logtau":
        mean, lo, hi, per_exp = 10 ** mean, 10 ** lo, 10 ** hi, 10 ** raw
    xs = (np.arange(NBIN) + 1.0) / NBIN
    color = LAYER[l]
    for v in per_exp:
        ax.plot(xs, v[:NBIN], color=MUTED, lw=0.6, alpha=0.5)
        if boundary:
            ax.plot([xs[-1], END_X], [v[NBIN - 1], v[NBIN]], color=MUTED, lw=0.6, alpha=0.5, ls="--")
    ax.plot(xs, mean[:NBIN], color=color, lw=2.2, marker="o", ms=4)
    ax.fill_between(xs, lo[:NBIN], hi[:NBIN], color=color, alpha=0.25, lw=0)
    ticks, labels = list(xs), [f"{t:g}".lstrip("0") if t < 1 else "1" for t in xs]
    if boundary:
        ax.plot([xs[-1], END_X], [mean[NBIN - 1], mean[NBIN]], color=color, lw=1.5, ls="--")
        ax.errorbar(END_X, mean[NBIN], yerr=[[mean[NBIN] - lo[NBIN]], [hi[NBIN] - mean[NBIN]]], color=color,
                    marker="s", ms=5, lw=1.5, capsize=2)
        ticks, labels = ticks + [END_X], labels + ["boundary"]
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%g"))
        ax.yaxis.set_minor_locator(matplotlib.ticker.LogLocator(subs=(2, 3, 5)))
        ax.yaxis.set_minor_formatter(matplotlib.ticker.FormatStrFormatter("%g"))
    ax.set_xticks(ticks, labels)
    ax.set_xlim(xs[0] - 0.04, (END_X if boundary else 1.0) + 0.08)
    ax.set_xlabel("fraction of game")
    ax.set_ylabel(r"learning rate $\beta$" if m == "beta" else r"memory timescale $\tau$")

    name, unit = ("learning rate beta", "") if m == "beta" else ("timescale tau", " tokens")
    game = test(dl[:, NBIN - 1] - dl[:, 0])
    lines.append(f"{name}, layer {l + 1} head {h + 1} channel {c + 1}:")
    lines.append(f"  over the game: first fifth {mean[0]:.3f}{unit} -> last fifth {mean[NBIN - 1]:.3f}{unit}: "
                 f"{100 * (mean[NBIN - 1] / mean[0] - 1):+.1f}%; experiments {game[0]} decrease, {game[1]} increase; "
                 f"sign test p = {game[2]:.2g}; t({game[5]}) = {game[3]:.2f}, p = {game[4]:.2g}")
    if boundary:
        bd = test(dl[:, NBIN] - dl[:, NBIN - 1])
        lines.append(f"  at the boundary: last fifth {mean[NBIN - 1]:.3f}{unit} -> boundary {mean[NBIN]:.3f}{unit}: "
                     f"{100 * (mean[NBIN] / mean[NBIN - 1] - 1):+.1f}%; experiments {bd[0]} drop, {bd[1]} rise; "
                     f"sign test p = {bd[2]:.2g}; t({bd[5]}) = {bd[3]:.2f}, p = {bd[4]:.2g}")


# ---------------------------------------------------------------- figure

def plot(agent):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    apply_style()
    pb, pt, E_ab = load_hist(agent)
    tab = pd.read_csv(os.path.join(CACHE, "channels_fb.csv"))
    cur = np.load(os.path.join(CACHE, "channels_fb.npz"))
    E_cd = len(cur["experiments"])
    t = tab[tab.layer == LAYER_CD].copy()
    t["consistent_down"] = t.consistent & (t.change < 0)
    lines = [f"Panels A-B: {E_ab} experiments, agent {agent}."]
    for l in range(pb.shape[0]):
        lines.append(f"  layer {l + 1}: median beta {weighted_median(pb[l], BETA_EDGES):.3f}, "
                     f"median tau {10 ** weighted_median(pt[l], LOGTAU_EDGES):.1f} tokens")
    lines.append(f"Panels C-D: layer {LAYER_CD}, {E_cd} game experiments, gates over the feedback; channels picked "
                 f"among those where >= {int(np.ceil(AGREE * E_cd))} of {E_cd} experiments agree.")
    beta_row = pick(t[t.measure == "beta"], "change", "consistent_down", lines, "beta decrease")
    tau_row = pick(t[t.measure == "logtau"], "boundary_change", "boundary_consistent_down", lines, "tau flush")

    fig = plt.figure(figsize=(7.0, 6.8))
    gs = fig.add_gridspec(2, 2, height_ratios=[3.6, 3.0], hspace=0.45)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1], sharey=ax_a)
    ax_c, ax_d = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])
    ridges([ax_a, ax_b], pb, pt)
    plt.setp(ax_b.get_yticklabels(), visible=False)
    channel_panel(ax_c, cur, "beta", beta_row, lines)
    channel_panel(ax_d, cur, "logtau", tau_row, lines)
    for ax, letter in zip((ax_a, ax_b, ax_c, ax_d), "ABCD"):
        ax.text(-0.02, 1.02, letter, transform=ax.transAxes, fontsize=11, fontweight="bold",
                color=INK, ha="right", va="bottom")
    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300, bbox_inches="tight")
    txt = "\n".join(lines)
    print(txt)
    open(os.path.join(CACHE, "fig3_latents.txt"), "w").write(txt + "\n")
    print(f"-> {os.path.normpath(OUT)}.pdf/.png")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("reduce")
    r.add_argument("paths", nargs="+")
    sub.add_parser("channels")
    q = sub.add_parser("plot")
    q.add_argument("--agent", default=AGENT)
    a = p.parse_args()
    if a.cmd == "reduce":
        reduce(a.paths)
    elif a.cmd == "channels":
        channels()
    else:
        plot(a.agent)


if __name__ == "__main__":
    main()
