#!/usr/bin/env python
"""Reduce simulation latents (*_latents.pth) to compact per-press aggregates.

One streaming pass per experiment; plotting/fig3_latents.py reads only the cache (press order, CSV row join).
Read-only w.r.t. results_simulations/. Run from core-model/: python plotting/build_cache.py

Per press k (the k-th PRESS_* token of a participant) we store [L, H] fp16:
  beta_press, la_press   beta / log_alpha AT the press token
  beta_pre,  a_pre, la_pre    means over the pre segment  (press k-1, press k)
  beta_post, a_post, la_post  means over the post segment (press k, press k+1)
(post segment = feedback of trial k + next trial's stimulus; last post segment
runs to end of sequence; a_* = mean alpha, la_* = mean log_alpha.)

Join to the sim CSV: row_index gives the CSV row of press k (-1 if unknown).
Alignment: per participant, rows==presses -> 1:1 in order; wilson2014humans:
presses map to rows with forced==0 (forced trials have no <<X>> marker).

Also per experiment: event-locked mean beta/alpha around presses (offsets
ETA_OFFS), and per-participant whole-sequence means.

Output: plotting/cache_2209/<experiment>.npz + printed alignment table.
"""
import argparse
import glob
import os
import re

import numpy as np
import pandas as pd
import torch

RE_FNAME = re.compile(r"experiment=(?P<exp>.+?)_agent=(?P<agent>.+?)_latents\.pth$")
ETA_OFFS = np.arange(-30, 41)


def seg_mean(csp, a, b):
    """Mean over tokens a..b inclusive from padded cumsum csp [L, T+1, H];
    nan if the segment is empty."""
    if b < a:
        return np.full((csp.shape[0], csp.shape[2]), np.nan, dtype=np.float32)
    return (csp[:, b + 1, :] - csp[:, a, :]) / (b - a + 1)


def row_indices(exp, df, filter_rows=True):
    """participant -> CSV row positions that correspond to presses, in order."""
    if exp.startswith("wilson2014humans"):
        free = df["forced"].to_numpy() == 0
        return {p: idx[free[idx]] for p, idx in
                df.groupby("participant", sort=False).indices.items()}
    if "participant" in df.columns:
        return dict(df.groupby("participant", sort=False).indices)
    # Psych-201-agentic simulators: participant_id in any format (P000, sim0, 1000, ...);
    # the i-th id in order of first appearance is latents participant i (checked via rows == presses)
    # rows without a press: forced choices (chambon, dubois, feng), invalid trials (feherdasilva)
    keep = np.ones(len(df), dtype=bool)
    if not filter_rows:
        pass
    elif "forced_choice" in df.columns:
        keep &= df["forced_choice"].to_numpy() == 0
    elif "valid" in df.columns:
        keep &= df["valid"].to_numpy() == 1
    groups = df.groupby("participant_id", sort=False).indices
    return {i: groups[pid][keep[groups[pid]]] for i, pid in enumerate(df["participant_id"].unique())}


def process(path, out_dir):
    payload = torch.load(path, map_location="cpu", weights_only=False, mmap=True)  # dubois_2022 is 13.5 GB
    assert payload["schema_version"] == 1, f"{path}: unknown schema"
    exp, agent = payload["experiment"], payload["agent"]
    parts = payload["participants"]
    L, H = parts[0]["beta"].shape[0], parts[0]["beta"].shape[2]

    csv_path = path[: -len("_latents.pth")] + ".csv"
    df = pd.read_csv(csv_path)
    rows_of = row_indices(exp, df)
    rows_all = row_indices(exp, df, filter_rows=False)  # fallback where the filter drops press rows (christian: valid == 0 rows are presses)

    per_press = {k: [] for k in ["beta_press", "la_press", "beta_pre", "a_pre",
                                 "la_pre", "beta_post", "a_post", "la_post"]}
    participant_id, press_idx, press_class, row_index = [], [], [], []
    eta_beta = np.zeros((len(ETA_OFFS), L, H)); eta_alpha = np.zeros_like(eta_beta)
    eta_cnt = np.zeros(len(ETA_OFFS), dtype=np.int64)
    part_mean_beta, part_mean_alpha, part_mean_la = [], [], []
    part_T, part_npress = [], []
    n_aligned = 0

    for i, part in enumerate(parts):
        beta = part["beta"].float().numpy()            # [L, T, H]
        log_alpha = part["log_alpha"].float().numpy()
        alpha = np.exp(log_alpha)
        T = beta.shape[1]
        pp = part["press_positions"].long().numpy()
        P = len(pp)

        rows = np.asarray(rows_of.get(i, []), dtype=np.int64)
        if len(rows) != P and len(rows_all.get(i, [])) == P:
            rows = np.asarray(rows_all[i], dtype=np.int64)
        aligned = len(rows) == P
        n_aligned += aligned

        csp_b = np.zeros((L, T + 1, H)); csp_b[:, 1:, :] = beta.cumsum(axis=1)
        csp_a = np.zeros((L, T + 1, H)); csp_a[:, 1:, :] = alpha.cumsum(axis=1)
        csp_l = np.zeros((L, T + 1, H)); csp_l[:, 1:, :] = log_alpha.cumsum(axis=1)

        for k, p in enumerate(pp):
            pre_a = (pp[k - 1] + 1) if k else 0
            post_b = (pp[k + 1] - 1) if k + 1 < P else T - 1
            per_press["beta_press"].append(beta[:, p, :].copy())  # copy: a view keeps the [L, T, H] array alive
            per_press["la_press"].append(log_alpha[:, p, :].copy())
            per_press["beta_pre"].append(seg_mean(csp_b, pre_a, p - 1))
            per_press["a_pre"].append(seg_mean(csp_a, pre_a, p - 1))
            per_press["la_pre"].append(seg_mean(csp_l, pre_a, p - 1))
            per_press["beta_post"].append(seg_mean(csp_b, p + 1, post_b))
            per_press["a_post"].append(seg_mean(csp_a, p + 1, post_b))
            per_press["la_post"].append(seg_mean(csp_l, p + 1, post_b))
        participant_id.extend([i] * P)
        press_idx.extend(range(P))
        press_class.extend(part["press_classes"].tolist())
        row_index.extend(rows.tolist() if aligned else [-1] * P)

        pos = pp[None, :] + ETA_OFFS[:, None]          # [O, P]
        valid = (pos >= 0) & (pos < T)
        for o in range(len(ETA_OFFS)):
            idx = pos[o][valid[o]]
            eta_beta[o] += beta[:, idx, :].sum(axis=1)
            eta_alpha[o] += alpha[:, idx, :].sum(axis=1)
            eta_cnt[o] += len(idx)

        part_mean_beta.append(beta.mean(axis=1)); part_mean_alpha.append(alpha.mean(axis=1))
        part_mean_la.append(log_alpha.mean(axis=1))
        part_T.append(T); part_npress.append(P)

    out = {k: np.stack(v).astype(np.float16) for k, v in per_press.items()}
    out.update(
        participant=np.asarray(participant_id, dtype=np.int32),
        press_idx=np.asarray(press_idx, dtype=np.int32),
        press_class=np.asarray(press_class, dtype=np.int16),
        row_index=np.asarray(row_index, dtype=np.int64),
        eta_offsets=ETA_OFFS,
        eta_beta=(eta_beta / np.maximum(eta_cnt, 1)[:, None, None]).astype(np.float32),
        eta_alpha=(eta_alpha / np.maximum(eta_cnt, 1)[:, None, None]).astype(np.float32),
        eta_cnt=eta_cnt,
        part_mean_beta=np.stack(part_mean_beta).astype(np.float32),
        part_mean_alpha=np.stack(part_mean_alpha).astype(np.float32),
        part_mean_la=np.stack(part_mean_la).astype(np.float32),
        part_T=np.asarray(part_T, dtype=np.int64),
        part_npress=np.asarray(part_npress, dtype=np.int64),
        experiment=exp, agent=agent, num_layers=L, num_heads=H,
        csv_path=csv_path,
    )
    np.savez_compressed(os.path.join(out_dir, f"{exp}.npz"), **out)
    return exp, len(parts), n_aligned, len(participant_id)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default="psych201_agentic/results_simulations")
    ap.add_argument("--agent", default="trained_core-phoneme-d128-L6-fgT-wd0.5-h4-lrdelta-2209_temp1",
                    help="substring the agent field must contain")
    ap.add_argument("--out-dir", default="plotting/cache_2209")
    ap.add_argument("--experiment", default="",
                    help="substring the experiment name must contain (default: all)")
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(args.data_dir, "experiment=*_latents.pth")))
    paths = [p for p in paths
             if (m := RE_FNAME.search(os.path.basename(p))) and args.agent in m["agent"] and args.experiment in m["exp"]]
    if not paths:
        raise SystemExit(f"no *_latents.pth matching {args.agent!r}")
    os.makedirs(args.out_dir, exist_ok=True)

    print(f"{'experiment':<38} {'parts':>5} {'aligned':>8} {'presses':>9}")
    for path in paths:
        exp, n, n_ok, n_press = process(path, args.out_dir)
        print(f"{exp:<38} {n:>5} {n_ok:>8} {n_press:>9,}", flush=True)


if __name__ == "__main__":
    main()
