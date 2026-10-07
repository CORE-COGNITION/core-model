# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Tomov, Schulz & Gershman (2021),
"Multi-task reinforcement learning in humans", Nature Human Behaviour, against
any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- training_reward_improvement (exp0): mean reward during the second half of the
  100 training trials is higher than during the first half (participants learn),
  paired t-test, expected positive difference.
- transfer_sf_gpi_above_chance (exp3): among participants who learned (average
  training reward > 0), the proportion choosing the final state predicted by
  SF&GPI (paper state 12) on the novel test trial exceeds chance (1/9), exact
  one-sided binomial test, expected positive deviation (preregistered hyp 2).
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
from scipy.stats import ttest_rel, binomtest

EXPERIMENTS = ["exp0", "exp1", "exp2", "exp3"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _training_reward_by_half(df: pd.DataFrame) -> np.ndarray:
    """Per-participant [early, late] mean reward over the 100 training trials."""
    tr = df[df.phase == "training"]
    if "path" in df.columns:
        rew = (tr[tr.reward.notna()][["participant_id", "block", "reward"]]
               .sort_values(["participant_id", "block"]))
    else:
        rew = tr[["participant_id", "trial", "reward"]].sort_values(
            ["participant_id", "trial"])
    per = []
    for _, sub in rew.groupby("participant_id"):
        n = len(sub)
        if n < 2:
            continue
        h = n // 2
        per.append((np.nanmean(sub.reward.iloc[:h]), np.nanmean(sub.reward.iloc[h:])))
    arr = np.array(per, dtype=float)
    return arr[~np.isnan(arr).any(axis=1)]


def check_training_reward_improvement(data: dict[str, pd.DataFrame]) -> dict:
    """"

    Participants learn the structure and improve reward across training within
    each task (performance improves)." — Tomov et al. 2021, Results / exp1 (p.4)."""
    df = data["exp0"]
    per = _training_reward_by_half(df)
    diff = per[:, 1] - per[:, 0]
    t, p = ttest_rel(per[:, 1], per[:, 0])
    d = diff.mean() / diff.std(ddof=1) if diff.std(ddof=1) > 0 else np.nan
    reproduced = bool(diff.mean() > 0 and p < 0.05)
    return {
        "effect_name": "training_reward_improvement",
        "experiment": "exp0",
        "original_effect_size": 1.0,
        "effect_size": float(d),
        "reproduced": reproduced,
        "n": int(len(diff)),
        "late_minus_early": float(diff.mean()),
        "p": float(p),
    }


def check_transfer_sf_gpi_above_chance(data: dict[str, pd.DataFrame]) -> dict:
    """"

    The proportion of participants choosing state 12 was significantly higher
    than would have been expected under the chance level of p = 1/9 (p-hat=0.27,
    95% CI (0.22, 0.32), binomial test: P = 4.38 x 10^-14), confirming our second
    preregistered hypothesis." — Tomov et al. 2021, Experiment 4 / Results (p.8)."""
    df = data["exp3"]
    tr = df[df.phase == "training"]
    avg = tr.groupby("participant_id")["reward"].mean()
    included = avg[avg > 0].index
    tst = df[(df.phase == "test") & (df.participant_id.isin(included))]
    n = int(len(tst))
    state12 = tst["fstate"]
    k = int((state12 == 12).sum())
    pval = binomtest(k, n, 1 / 9, alternative="greater").pvalue
    prop = k / n
    reproduced = bool(prop > 1 / 9 and pval < 0.05)
    return {
        "effect_name": "transfer_sf_gpi_above_chance",
        "experiment": "exp3",
        "original_effect_size": 0.27,
        "effect_size": float(prop),
        "reproduced": reproduced,
        "n_included": n,
        "k_state12": k,
        "p": float(pval),
    }


EFFECTS = [check_training_reward_improvement, check_transfer_sf_gpi_above_chance]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources[exp] if exp in sources else '(default — local ./' + exp + '.csv)'}")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
