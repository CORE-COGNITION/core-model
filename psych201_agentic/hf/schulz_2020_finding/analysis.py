# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Schulz, Franklin, & Gershman (2020),
"Finding structure in multi-armed bandits" (Cognitive Psychology) — bioRxiv preprint
doi:10.1101/432534 — against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- structure_reward_benefit (exp0): mean reward per participant is higher on linear-positive
  and linear-negative rounds than on random rounds (paired t-tests, both p < .05; paper
  reports pos>ran: t(115)=7.71, d=0.72; neg>ran: t(115)=11.46, d=1.06).
- within_round_learning (exp0): per-participant Spearman correlation between trial number
  and reward is positive on average (one-sample t-test, p < .05; paper: mean rho = 0.29,
  t(115)=34.6, p < .001).
- learning_to_learn_across_rounds (exp0): per-participant Spearman correlation between
  round number and reward is positive on average (one-sample t-test, p < .05; paper:
  mean rho = 0.10, t(115)=6.78, p < .001), indicating learning-to-learn across rounds.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1", "exp2", "exp3", "exp4"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, task_id, trial, response, condition, round, reward
      exp1: participant_id, task_id, trial, response, round, reward
      exp2: participant_id, task_id, trial, response, condition, round, reward
      exp3: participant_id, task_id, trial, response, round, reward
      exp4: participant_id, task_id, trial, response, condition, round, reward
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _subj_spearman(g: pd.DataFrame, xcol: str) -> float:
    """Spearman rho between column xcol and reward, per participant (paper's pooled measure)."""
    x = g[xcol].to_numpy(dtype=float)
    y = g["reward"].to_numpy(dtype=float)
    return float(stats.spearmanr(x, y)[0])


def check_structure_reward_benefit(data: dict[str, pd.DataFrame]) -> dict:
    """"Participants performed better in linear-positive than in random rounds ... and better
    during linear-negative than during random rounds" — Schulz et al. 2020, p.11-12,
    Experiment 1 Results and discussion."""
    df = data["exp0"]
    means = df.groupby(["participant_id", "condition"])["reward"].mean().unstack()
    d_pos, p_pos = stats.ttest_rel(means["pos"], means["ran"])
    d_neg, p_neg = stats.ttest_rel(means["neg"], means["ran"])
    effect = float(np.mean(means["pos"]) - np.mean(means["ran"]))
    reproduced = bool(
        np.mean(means["pos"]) > np.mean(means["ran"])
        and np.mean(means["neg"]) > np.mean(means["ran"])
        and p_pos < 0.05
        and p_neg < 0.05
    )
    return {
        "effect_name": "structure_reward_benefit",
        "experiment": "exp0",
        "original_effect_size": 0.72,  # Cohen's d for linear-positive vs random (paper)
        "effect_size": effect,
        "p_pos_vs_random": float(p_pos),
        "p_neg_vs_random": float(p_neg),
        "reproduced": reproduced,
    }


def check_within_round_learning(data: dict[str, pd.DataFrame]) -> dict:
    """"Participants improved over trials, with a mean correlation between trials and rewards
    of rho = 0.29, t(115) = 34.6, p < .001" — Schulz et al. 2020, p.12, Experiment 1
    Results and discussion."""
    df = data["exp0"]
    rhos = df.groupby("participant_id", group_keys=False).apply(
        lambda g: _subj_spearman(g, "trial")
    )
    t, p = stats.ttest_1samp(rhos, 0)
    reproduced = bool(np.mean(rhos) > 0 and p < 0.05)
    return {
        "effect_name": "within_round_learning",
        "experiment": "exp0",
        "original_effect_size": 0.29,  # mean Spearman rho(trial, reward) (paper)
        "effect_size": float(np.mean(rhos)),
        "t": float(t),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_learning_to_learn_across_rounds(data: dict[str, pd.DataFrame]) -> dict:
    """"Participants improved over rounds. The mean correlation between rounds and rewards
    was rho = 0.10 (t(115) = 6.78, p < .001 ...), indicating that participants showed some
    characteristics of learning-to-learn" — Schulz et al. 2020, p.12, Experiment 1
    Results and discussion."""
    df = data["exp0"]
    rhos = df.groupby("participant_id", group_keys=False).apply(
        lambda g: _subj_spearman(g, "round")
    )
    t, p = stats.ttest_1samp(rhos, 0)
    reproduced = bool(np.mean(rhos) > 0 and p < 0.05)
    return {
        "effect_name": "learning_to_learn_across_rounds",
        "experiment": "exp0",
        "original_effect_size": 0.10,  # mean Spearman rho(round, reward) (paper)
        "effect_size": float(np.mean(rhos)),
        "t": float(t),
        "p": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_structure_reward_benefit,
    check_within_round_learning,
    check_learning_to_learn_across_rounds,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing — pure return value
    so downstream simulators / model evaluators can call this programmatically."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        if exp in sources:
            print(f"{exp}: {sources[exp]}")
        else:
            print(f"{exp}: (default — local ./{exp}.csv)")
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