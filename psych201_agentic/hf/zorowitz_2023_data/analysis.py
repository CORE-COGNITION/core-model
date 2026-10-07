# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Zorowitz & Niv (unpublished; gamified
two-step / Daw task pilot) against any dataset in the Psych-301 unified schema.

Dataset note: this is an UNPUBLISHED pilot dataset (N=149 Prolific: exp1 N=50,
exp2 N=50, exp3 N=49) with no paper PDF. The verified effects are the standard,
well-established two-step-task signatures that any valid two-step dataset must
reproduce.

Effects tested:
- reward_model_free_effect (exp0, exp1, exp2): P(stay | reward) > P(stay | no
  reward); a paired one-sample t-test on per-participant stay-differences,
  expected positive (model-free repetition after reward).
- reward_transition_interaction (exp0, exp1, exp2): the stay-probability reward
  boost is larger after COMMON transitions than uncommon transitions (classic
  two-step model-based signature); one-sample t-test on per-participant
  (reward-diff among common) - (reward-diff among uncommon), expected positive.
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1", "exp2"]


def _trials(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse two-row (stage1+stage2) trial blocks into one row per trial
    with `stay`, `reward`, and `transition`."""
    df = df[df["phase"] == "test"]
    s1 = df[df["stage"] == "stage1"].copy()
    s1["next_resp"] = s1.groupby("participant_id")["response"].shift(-1)
    s1["stay"] = (s1["next_resp"] == s1["response"]).astype(float)
    s1 = s1.dropna(subset=["next_resp"])
    s2 = df[df["stage"] == "stage2"][["participant_id", "block", "reward", "transition"]]
    return s1[["participant_id", "block", "stay"]].merge(s2, on=["participant_id", "block"])


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}."""
    sources = sources or {}
    out = {}
    for exp in EXPERIMENTS:
        path = sources.get(exp, f"./{exp}.csv")
        out[exp] = _trials(pd.read_csv(path))
    return out


def _agg(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return pd.concat([data[e].assign(experiment=e) for e in EXPERIMENTS], ignore_index=True)


def check_reward_model_free_effect(data: dict[str, pd.DataFrame]) -> dict:
    """Standard two-step task: participants repeat their first-stage choice more
    after a rewarded trial than after an unrewarded trial — P(stay | reward) >
    P(stay | no reward). Zorowitz & Niv (unpublished, gamified two-step pilot)."""
    df = _agg(data)
    diffs = df.groupby("participant_id").apply(
        lambda g: g[g["reward"] == 1]["stay"].mean() - g[g["reward"] == 0]["stay"].mean(),
        include_groups=False,
    ).dropna()
    t, p = stats.ttest_1samp(diffs, 0)
    p_stay_r = df[df["reward"] == 1]["stay"].mean()
    p_stay_nr = df[df["reward"] == 0]["stay"].mean()
    effect_size = (p_stay_r - p_stay_nr)
    return {
        "effect_name": "reward_model_free_effect",
        "experiment": "exp0+exp1+exp2",
        "original_effect_size": 0.0,
        "effect_size": float(effect_size),
        "stat": float(t),
        "p": float(p),
        "reproduced": bool(effect_size > 0 and p < 0.05),
    }


def check_reward_transition_interaction(data: dict[str, pd.DataFrame]) -> dict:
    """Classic two-step model-based signature: the stay-probability reward boost
    is larger following COMMON transitions than uncommon transitions (stay reward
    x transition interaction). Zorowitz & Niv (unpublished, gamified two-step pilot)."""
    df = _agg(data)
    mix = []
    for _, g in df.groupby("participant_id"):
        com = g[g["transition"] == 1]
        unc = g[g["transition"] == 0]
        d_com = com[com["reward"] == 1]["stay"].mean() - com[com["reward"] == 0]["stay"].mean()
        d_unc = unc[unc["reward"] == 1]["stay"].mean() - unc[unc["reward"] == 0]["stay"].mean()
        mix.append(d_com - d_unc)
    mix = np.array(mix)
    mix = mix[~np.isnan(mix)]
    t, p = stats.ttest_1samp(mix, 0)
    effect_size = float(mix.mean())
    return {
        "effect_name": "reward_transition_interaction",
        "experiment": "exp0+exp1+exp2",
        "original_effect_size": 0.0,
        "effect_size": effect_size,
        "stat": float(t),
        "p": float(p),
        "reproduced": bool(effect_size > 0 and p < 0.05),
    }


EFFECTS = [check_reward_model_free_effect, check_reward_transition_interaction]


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
    print(f"{'effect':<{w}}  {'exp':<15}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<15}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
