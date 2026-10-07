# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Bavard et al. (2021), "Two sides of the same coin:
beneficial and detrimental consequences of range adaptation in human reinforcement learning",
Sci Adv, 7(14):eabe0340, against any dataset in the unified Psych-301 schema (see schema.md).

Effects tested:
- learning_above_chance (exp0..exp7 pooled): correct response rate in the learning phase is
  significantly above chance 0.5. One-sample t-test per-participant mean correct > 0.5.
- magnitude_context_difference (exp0..exp7 pooled): correct choice rate is higher in high-
  magnitude (7.50_vs_2.50, dEV=5.0) than low-magnitude (0.75_vs_0.25, dEV=0.5) learning
  contexts, i.e. the within-participant difference is positive. One-sample t-test > 0.
- transfer_conflict_below_chance (exp0..exp7 pooled): in the diagnostic transfer context
  (2.50_vs_0.75, dEV=1.75) correct response rate is significantly BELOW chance 0.5, i.e.
  participants express expected-value-minimizing (range-adapted, extrapolation) preferences.
  One-sample t-test per-participant mean correct < 0.5.
"""
from __future__ import annotations

import argparse
from typing import Optional

import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp

EXPERIMENTS = [f"exp{i}" for i in range(8)]


def load_data(sources: Optional[dict[str, str]] = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}, each with a unique participant key added
    (participant IDs collide across experiments, so they are prefixed by the experiment name
    to allow correct n=800 pooled participant-level averaging)."""
    sources = sources or {}
    out = {}
    for exp in EXPERIMENTS:
        df = pd.read_csv(sources.get(exp, f"./{exp}.csv"))
        df["pid"] = exp + "_" + df["participant_id"].astype(str)
        out[exp] = df
    return out


def _pool(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return pd.concat(data.values(), ignore_index=True)


def check_learning_above_chance(data: dict[str, pd.DataFrame]) -> dict:
    """"In the learning phase, the average correct response rate was significantly higher than
    chance level 0.5 [0.69 +/- 0.16, t(799) = 32.49, P < 0.0001]." -- Bavard 2021, p.5, Results:
    Overall correct response rate."""
    df = _pool(data)
    learn = df[(df.phase == "learning") & (df.valid == 1)]
    per = learn.groupby("pid")["correct"].mean().dropna()
    t, p = ttest_1samp(per, 0.5)
    reproduced = float(t) > 0 and p < 0.05
    return {
        "effect_name": "learning_above_chance",
        "experiment": "exp0..exp7",
        "original_effect_size": 32.49,
        "effect_size": float(t),
        "reproduced": bool(reproduced),
    }


def check_magnitude_context_difference(data: dict[str, pd.DataFrame]) -> dict:
    """"we also observed a moderate but significant effect of the choice contexts, where the
    correct choice rate was higher in the dEV = 5.0 compared to the dEV = 0.5 contexts (0.71 +/- 0.18
    versus 0.67 +/- 0.18; t(799) = 6.81, P < 0.0001)." -- Bavard 2021, p.5, Results: Overall correct
    response rate."""
    df = _pool(data)
    g = df[(df.phase == "learning") & (df.valid == 1)]
    hi = g[g.context_label == "7.50_vs_2.50_learning"].groupby("pid")["correct"].mean()
    lo = g[g.context_label == "0.75_vs_0.25_learning"].groupby("pid")["correct"].mean()
    diff = (hi - lo).dropna()
    t, p = ttest_1samp(diff, 0)
    reproduced = float(t) > 0 and p < 0.05
    return {
        "effect_name": "magnitude_context_difference",
        "experiment": "exp0..exp7",
        "original_effect_size": 6.81,
        "effect_size": float(t),
        "reproduced": bool(reproduced),
    }


def check_transfer_conflict_below_chance(data: dict[str, pd.DataFrame]) -> dict:
    """"in the dEV = 1.75 context, we found that participants' average correct choice rate was
    significantly below chance level (0.42 +/- 0.30, t(799) = -7.25, P < 0.0001), thus demonstrating
    that participants express suboptimal preferences in this context." -- Bavard 2021, p.5-6,
    Results: Overall correct response rate."""
    df = _pool(data)
    conf = df[(df.context_label == "2.50_vs_0.75_transfer") & (df.valid == 1)]
    per = conf.groupby("pid")["correct"].mean().dropna()
    t, p = ttest_1samp(per, 0.5)
    reproduced = float(t) < 0 and p < 0.05
    return {
        "effect_name": "transfer_conflict_below_chance",
        "experiment": "exp0..exp7",
        "original_effect_size": -7.25,
        "effect_size": float(t),
        "reproduced": bool(reproduced),
    }


EFFECTS = [
    check_learning_above_chance,
    check_magnitude_context_difference,
    check_transfer_conflict_below_chance,
]


def run_analysis(sources: Optional[dict[str, str]] = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. Pure return value."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources.get(exp, '(default - local ./{exp}.csv)')}")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<10}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<10}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()