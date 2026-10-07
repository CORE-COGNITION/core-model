# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Feng, Wang, Zarnescu & Wilson (2021),
"The dynamics of explore-exploit decisions reveal a signal-to-noise mechanism for
random exploration" (Scientific Reports 11:3077), against any dataset in the Psych-301
unified schema (see schema.md).

Effects tested:
- directed_exploration_horizon (exp0, exp1): in the unequal [1 3] information condition,
  participants choose the more informative option more often on the first free-choice trial
  in horizon 6 than horizon 1 (lifed differences in observed mean reward); paired t-test,
  expected positive (information seeking increases with horizon).
- random_exploration_horizon (exp0, exp1): behavioral variability (decision noise, the
  inverse of the choice-curve slope w.r.t. observed mean reward) is larger in horizon 6 than
  horizon 1; paired t-test of per-subject choice-curve slope, expected smaller (more random)
  slope in horizon 6.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides, loads
    ./{exp}.csv from CWD.

    Required columns per experiment:
      exp0: participant_id, task_id, trial, forced_choice, response, reward, uc, horizon
      exp1: participant_id, task_id, trial, forced_choice, response, reward, uc, horizon
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _first_free_choice_with_observed_reward(df: pd.DataFrame) -> pd.DataFrame:
    """Per-game first free-choice row with the observed mean reward difference dR
    (bandit-2 mean minus bandit-1 mean, computed from the forced/instructed trials)."""
    forced = df[df["forced_choice"] == 1].copy()
    forced["r1"] = np.where(forced["response"] == 0, forced["reward"], np.nan)
    forced["r2"] = np.where(forced["response"] == 1, forced["reward"], np.nan)
    means = forced.groupby(["participant_id", "task_id"]).agg(
        mu1=("r1", "mean"), mu2=("r2", "mean")
    ).reset_index()
    first = (
        df[df["forced_choice"] == 0]
        .sort_values(["participant_id", "task_id", "trial"])
        .groupby(["participant_id", "task_id"])
        .first()
        .reset_index()
    )
    d = first.merge(means, on=["participant_id", "task_id"])
    d["dR"] = d["mu2"] - d["mu1"]
    return d


def _pooled(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return pd.concat([_first_free_choice_with_observed_reward(df).assign(exp=k)
                      for k, df in data.items()], ignore_index=True)


def check_directed_exploration_horizon(data: dict[str, pd.DataFrame]) -> dict:
    """"Consistent with directed exploration, in the [1 3] condition participants are more
    likely to choose the more informative option in horizon 6 than horizon 1, as indicated by
    a shift in the indifference point of the choice curves" -- Feng et al. 2021,
    p.3, Results ("Information seeking and behavioral variability increase with horizon").
    """
    d = _pooled(data)
    un = d[d["uc"] != 2].copy()
    un["moreinfo"] = np.where(
        ((un["response"] == 1) & (un["uc"] == 1)) | ((un["response"] == 0) & (un["uc"] == 3)),
        1, 0,
    )
    piv = un.groupby(["participant_id", "exp", "horizon"])["moreinfo"].mean().unstack(fill_value=np.nan)
    piv = piv.dropna(subset=[1, 6])
    diff = piv[6] - piv[1]
    t, p = stats.ttest_rel(piv[6], piv[1])
    d_eff = diff.mean()
    reproduced = (d_eff > 0) and (p < 0.05)
    return {
        "effect_name": "directed_exploration_horizon",
        "experiment": "exp0/exp1 (pooled)",
        "original_effect_size": 0.100,
        "effect_size": float(d_eff),
        "p_value": float(p),
        "t_stat": float(t),
        "reproduced": bool(reproduced),
    }


def check_random_exploration_horizon(data: dict[str, pd.DataFrame]) -> dict:
    """"Consistent with random exploration, people's behavior is less predictable (more random)
    in horizon 6 than horizon 1, as indicated by a lower slope of the choice curves in the
    horizon 6 condition" -- Feng et al. 2021, p.3, Results ("Information seeking and
    behavioral variability increase with horizon").
    """
    d = _pooled(data)
    rows = []
    for (pid, h), g in d.groupby(["participant_id", "horizon"]):
        if len(g) < 20:
            continue
        x = g["dR"].values
        y = g["response"].values
        if np.std(x) == 0:
            continue
        beta = np.cov(x, y)[0, 1] / np.var(x)
        rows.append((pid, h, beta))
    s = pd.DataFrame(rows, columns=["participant_id", "horizon", "slope"])
    piv = s.pivot(index="participant_id", columns="horizon", values="slope").dropna(subset=[1, 6])
    t, p = stats.ttest_rel(piv[6], piv[1])
    d_eff = piv[6].mean() - piv[1].mean()
    reproduced = (d_eff < 0) and (p < 0.05)
    return {
        "effect_name": "random_exploration_horizon",
        "experiment": "exp0/exp1 (pooled)",
        "original_effect_size": -0.010,
        "effect_size": float(d_eff),
        "p_value": float(p),
        "t_stat": float(t),
        "reproduced": bool(reproduced),
    }


EFFECTS = [check_directed_exploration_horizon, check_random_exploration_horizon]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing -- pure return value."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources.get(exp, '(default -- local ./{exp}.csv)')}")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<20}  {'orig':>10}  {'this':>10}  {'p':>8}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<20}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{r['p_value']:>8.4f}  {'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()