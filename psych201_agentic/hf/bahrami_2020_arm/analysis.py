# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy"]
# ///
"""Check the primary behavioral effects of a restless 4-arm bandit task (Daw et al. 2006
paradigm; Bahrami/Navajas 4-Arm Bandit dataset) against any dataset in the Psych-301
unified schema (see schema.md).

Effects tested:
- best_choice_above_chance (exp0): participants choose the arm with the highest true
  reward (reward_c*) more often than chance (25%); one-sample t-test of per-participant
  best-choice rate vs 0.25, expected direction: > 0.25.
- choice_accuracy_improves (exp0): the rate of choosing the highest-reward arm rises
  over trials (learning/exploitation); paired t-test of late-trials (>100) minus
  early-trials (<50) best-choice rate, expected direction: late > early.
- exploratory_slower_rt (exp0): choices that do not select the current highest-reward
  arm (more exploratory / higher payoff-uncertainty) take longer than choices that do;
  paired t-test of per-participant mean RT for non-best vs best choices, expected
  direction: non-best RT > best RT.
"""
from __future__ import annotations

import argparse
import pandas as pd
import numpy as np
from scipy import stats

EXPERIMENTS = ["exp0"]

ARM_REWARD_COLS = ["reward_c1", "reward_c2", "reward_c3", "reward_c4"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    Required columns per experiment:
      exp0: participant_id, trial, choice, response, reward, rt (and: reward_c1..c4)
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _prep(df: pd.DataFrame) -> pd.DataFrame:
    """Drop missed trials (no response) and flag the best (highest-reward) arm."""
    d = df.dropna(subset=["choice", "reward"]).copy()
    d["_best"] = d[ARM_REWARD_COLS].idxmax(axis=1).map(
        {f"reward_c{i}": i for i in [1, 2, 3, 4]}
    )
    d["_isbest"] = (d["_best"] == d["choice"]).astype(int)
    return d


def check_best_choice_above_chance(data: dict[str, pd.DataFrame]) -> dict:
    """Participants pick the highest-likelihood-of-reward arm more than chance (Daw et al.
    2006 4-arm bandit: reward deliveries above chance because options have drifting,
    learnable values). p.N/A, Task/Description."""
    d = _prep(data["exp0"])
    acc = d.groupby("participant_id")["_isbest"].mean()
    t, p = stats.ttest_1samp(acc, 0.25)
    reproduced = acc.mean() > 0.25 and p < 0.05
    return {
        "effect_name": "best_choice_above_chance",
        "experiment": "exp0",
        "original_effect_size": 0.25,
        "effect_size": float(acc.mean()),
        "t": float(t), "p": float(p), "n_participants": int(len(acc)),
        "reproduced": bool(reproduced),
    }


def check_choice_accuracy_improves(data: dict[str, pd.DataFrame]) -> dict:
    """Reward-following strengthens over trials as option values are learned, so the rate
    of exploiting the current best arm rises across the session. p.N/A, Task/Description."""
    d = _prep(data["exp0"])
    d["_phase"] = np.where(
        d["trial"] < 50, "early", np.where(d["trial"] >= 100, "late", "mid")
    )
    pv = (
        d[d["_phase"].isin(["early", "late"])]
        .pivot_table(index="participant_id", columns="_phase", values="_isbest", aggfunc="mean")
        .dropna()
    )
    t, p = stats.ttest_rel(pv["late"], pv["early"])
    reproduced = pv["late"].mean() > pv["early"].mean() and p < 0.05
    return {
        "effect_name": "choice_accuracy_improves",
        "experiment": "exp0",
        "original_effect_size": 0.0,
        "effect_size": float(pv["late"].mean() - pv["early"].mean()),
        "late": float(pv["late"].mean()), "early": float(pv["early"].mean()),
        "t": float(t), "p": float(p), "n_participants": int(len(pv)),
        "reproduced": bool(reproduced),
    }


def check_exploratory_slower_rt(data: dict[str, pd.DataFrame]) -> dict:
    """Exploration under payoff uncertainty takes longer: when a participant does not
    exploit the current best (highest-reward) arm, deliberation/RT is slower than when
    they do. p.N/A, Task/Description."""
    d = _prep(data["exp0"])
    rtb = d.groupby(["participant_id", "_isbest"])["rt"].mean().unstack().dropna()
    t, p = stats.ttest_rel(rtb[0], rtb[1])
    reproduced = rtb[0].mean() > rtb[1].mean() and p < 0.05
    return {
        "effect_name": "exploratory_slower_rt",
        "experiment": "exp0",
        "original_effect_size": 0.0,
        "effect_size": float(rtb[0].mean() - rtb[1].mean()),
        "nonbest_rt": float(rtb[0].mean()), "best_rt": float(rtb[1].mean()),
        "t": float(t), "p": float(p), "n_participants": int(len(rtb)),
        "reproduced": bool(reproduced),
    }


EFFECTS = [check_best_choice_above_chance, check_choice_accuracy_improves, check_exploratory_slower_rt]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources.get(exp, '(default — local ./%s.csv)' % exp)}")
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