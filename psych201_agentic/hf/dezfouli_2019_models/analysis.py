# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy"]
# ///
"""Check the primary behavioral effects of Dezfouli et al. (2019) against any dataset
in the Psych-301 unified schema (see schema.md).

Effects tested:
- best_action_above_chance (exp0): one-sample t-test of P(best_action) > 0.5 per group.
- healthy_vs_depression_best_action (exp0): independent t-test that healthy > depression
  (and healthy > bipolar) in P(best_action).
- reward_decreases_stay (exp0): paired test that P(stay|reward) < P(stay|no_reward) in
  healthy and depression groups (bipolar expected null).
"""
from __future__ import annotations

import argparse

import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _best_action_per_participant(df: pd.DataFrame) -> pd.DataFrame:
    """Return per-participant mean of best_action, with condition."""
    return df.groupby(["participant_id", "condition"])["best_action"].mean().reset_index()


def check_best_action_above_chance(data: dict[str, pd.DataFrame]) -> dict:
    """\"the probability of selecting the better action was significantly higher than the other action in all groups\" — Dezfouli 2019, p.4, Results/Performance in the task."""
    df = data["exp0"]
    per_subj = _best_action_per_participant(df)
    groups = {"healthy": "HEALTHY", "depression": "DEPRESSION", "bipolar": "BIPOLAR"}
    results = []
    all_reproduced = True
    for cond, label in groups.items():
        vals = per_subj.loc[per_subj["condition"] == cond, "best_action"].values
        t_stat, p_val = stats.ttest_1samp(vals, 0.5, alternative="greater")
        mean_pbest = float(vals.mean())
        reproduced = bool(p_val < 0.05)
        if not reproduced:
            all_reproduced = False
        results.append({
            "effect_name": "best_action_above_chance",
            "experiment": "exp0",
            "original_effect_size": {"healthy": 0.270, "depression": 0.149, "bipolar": 0.119}[cond],
            "effect_size": float(mean_pbest - 0.5),
            "reproduced": reproduced,
            "group": cond,
            "mean_best_action": mean_pbest,
            "t_stat": float(t_stat),
            "p_value": float(p_val),
        })
    return {
        "effect_name": "best_action_above_chance",
        "experiment": "exp0",
        "original_effect_size": "η=0.270/0.149/0.119",
        "effect_size": {r["group"]: r["mean_best_action"] - 0.5 for r in results},
        "reproduced": all_reproduced,
        "group_results": results,
    }


def check_healthy_vs_depression_best_action(data: dict[str, pd.DataFrame]) -> dict:
    """\"Comparing HEALTHY and DEPRESSION groups revealed that the group x action interaction had a significant effect on the probability of selecting actions [η=−0.120, SE=0.038, p=0.002]\" — Dezfouli 2019, p.5, Results/Performance in the task."""
    df = data["exp0"]
    per_subj = _best_action_per_participant(df)
    healthy = per_subj.loc[per_subj["condition"] == "healthy", "best_action"].values
    depression = per_subj.loc[per_subj["condition"] == "depression", "best_action"].values
    bipolar = per_subj.loc[per_subj["condition"] == "bipolar", "best_action"].values
    t_hd, p_hd = stats.ttest_ind(healthy, depression, alternative="greater")
    t_hb, p_hb = stats.ttest_ind(healthy, bipolar, alternative="greater")
    reproduced_hd = bool(p_hd < 0.05)
    reproduced_hb = bool(p_hb < 0.05)
    return {
        "effect_name": "healthy_vs_depression_best_action",
        "experiment": "exp0",
        "original_effect_size": "η=−0.120 (H vs D) / η=−0.150 (H vs B)",
        "effect_size": float(healthy.mean() - depression.mean()),
        "reproduced": reproduced_hd and reproduced_hb,
        "healthy_mean": float(healthy.mean()),
        "depression_mean": float(depression.mean()),
        "bipolar_mean": float(bipolar.mean()),
        "t_hd": float(t_hd),
        "p_hd": float(p_hd),
        "t_hb": float(t_hb),
        "p_hb": float(p_hb),
        "reproduced_hd": reproduced_hd,
        "reproduced_hb": reproduced_hb,
    }


def check_reward_decreases_stay(data: dict[str, pd.DataFrame]) -> dict:
    """\"earning a reward significantly decreased the probability of staying on the same action in the HEALTHY and DEPRESSION groups, but not in the BIPOLAR group\" — Dezfouli 2019, p.6, Results/The immediate effect of reward on choice."""
    df = data["exp0"].copy()
    df = df.sort_values(["participant_id", "trial"])
    df["prev_response"] = df.groupby("participant_id")["response"].shift(1)
    df["prev_reward"] = df.groupby("participant_id")["reward"].shift(1)
    df["stay"] = (df["response"] == df["prev_response"]).astype(int)
    df_valid = df.dropna(subset=["prev_response", "prev_reward"])
    groups = {"healthy": "HEALTHY", "depression": "DEPRESSION", "bipolar": "BIPOLAR"}
    group_results = []
    all_correct = True
    for cond, label in groups.items():
        sub = df_valid[df_valid["condition"] == cond]
        sub_agg = sub.groupby("participant_id").agg(
            stay_after_reward=("stay", lambda x: x.loc[sub.loc[x.index, "prev_reward"] == 1].mean()),
            stay_after_no_reward=("stay", lambda x: x.loc[sub.loc[x.index, "prev_reward"] == 0].mean()),
        ).dropna()
        diff = sub_agg["stay_after_reward"] - sub_agg["stay_after_no_reward"]
        if len(diff) < 2:
            reproduced = False
            t_stat, p_val = 0.0, 1.0
        else:
            t_stat, p_val = stats.ttest_1samp(diff, 0, alternative="less")
            reproduced = bool(p_val < 0.05)
        mean_diff = float(diff.mean())
        if cond in ("healthy", "depression") and not reproduced:
            all_correct = False
        if cond == "bipolar" and reproduced:
            all_correct = False
        group_results.append({
            "group": cond,
            "n": len(diff),
            "mean_stay_after_reward": float(sub_agg["stay_after_reward"].mean()),
            "mean_stay_after_no_reward": float(sub_agg["stay_after_no_reward"].mean()),
            "mean_diff": mean_diff,
            "t_stat": float(t_stat),
            "p_value": float(p_val),
            "reproduced": reproduced,
        })
    return {
        "effect_name": "reward_decreases_stay",
        "experiment": "exp0",
        "original_effect_size": "η=0.112/0.111/0.030",
        "effect_size": {r["group"]: r["mean_diff"] for r in group_results},
        "reproduced": all_correct,
        "group_results": group_results,
    }


EFFECTS = [
    check_best_action_above_chance,
    check_healthy_vs_depression_best_action,
    check_reward_decreases_stay,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
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
    w = max(w, 6)
    print()
    header = f"{'effect':<{w}}  {'exp':<4}  {'reproduced':>10}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  {'YES' if r['reproduced'] else 'NO':>10}")
    global_reproduced = all(r["reproduced"] for r in results)
    reproduced_list = [r["effect_name"] for r in results if r["reproduced"]]
    not_reproduced_list = [r["effect_name"] for r in results if not r["reproduced"]]
    print()


if __name__ == "__main__":
    main()