# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy"]
# ///
"""Check the primary behavioral effects of Thoma, Newell, & Schulze (2025),
"Emerging adaptivity in probability learning" (JEP: General), against any
dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- static_high_probability_learning (exp0): mean rate of choosing the
  high-probability (majority) option is higher in the static_high condition
  than in the ecologically dynamic condition (and is above chance).
  Test: per-participant means, two-sample t-test (static_high > ecol_dyn).
- perseverance_age_youngest (exp0): 3- to 4-year-olds choose their preferred
  (most-chosen) option more often than every other age group.
  Test: per-participant preferred-option rate, 3-4y vs all others pooled.
- perseverance_condition_effect (exp0): the preferred-option choice rate is
  higher in the static_high condition (where persevering maximizes reward)
  than in the static_random condition (50/50, no superior option).
  Test: per-participant preferred-option rate, static_high > static_random.
"""
from __future__ import annotations

import argparse

import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, condition, age_group, trial, response, ml_correct
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_static_high_probability_learning(data: dict[str, pd.DataFrame]) -> dict:
    """"First, we found a significant main effect of condition, χ2(1) = 15.04, p < .001, indicating that ... participants in the static high condition made more choices of the high-probability option (M = .66) than did participants in the ecologically dynamic condition (M = .59)." — Thoma et al. 2025, p.15, Results (Probability Learning)."""
    df = data["exp0"]
    pc = df.groupby(["participant_id", "condition"])["ml_correct"].mean()
    sh = pc.loc[pc.index.get_level_values("condition") == "static_high"].values
    ed = pc.loc[pc.index.get_level_values("condition") == "ecol_dyn"].values
    t, p = stats.ttest_ind(sh, ed, equal_var=False)
    reproduced = bool(sh.mean() > ed.mean() and p < 0.05)
    return {
        "effect_name": "static_high_probability_learning",
        "experiment": "exp0",
        "original_effect_size": 0.66 - 0.59,
        "effect_size": float(sh.mean() - ed.mean()),
        "static_high_mean": float(sh.mean()),
        "ecol_dyn_mean": float(ed.mean()),
        "t": float(t),
        "p": float(p),
        "reproduced": reproduced,
    }


def _preferred_option_rate(df: pd.DataFrame) -> pd.DataFrame:
    """Per-participant proportion of trials on which they chose their
    preferred (most frequently chosen altogether) option."""
    pref = df.groupby(["participant_id", "condition", "age_group"])["response"].agg(
        lambda x: x.mode()[0]
    )
    merged = df.merge(pref.rename("pref"), on=["participant_id", "condition", "age_group"])
    rate = merged.groupby(["participant_id", "condition", "age_group"]).apply(
        lambda g: float((g["response"] == g["pref"]).mean())
    )
    return rate.rename("pref_rate").reset_index()


def check_perseverance_age_youngest(data: dict[str, pd.DataFrame]) -> dict:
    """"3- to 4-year-olds were more likely to choose their preferred option than 6- to 7-year-olds (z = 6.45, p < .001), 9- to 11-year-olds (z = 7.16, p < .001), or adults (z = 4.64, p < .001)." — Thoma et al. 2025, p.13, Results (Perseverance)."""
    df = _preferred_option_rate(data["exp0"])
    young = df.loc[df["age_group"] == "3-4 years", "pref_rate"].values
    other = df.loc[df["age_group"] != "3-4 years", "pref_rate"].values
    t, p = stats.ttest_ind(young, other, equal_var=False)
    reproduced = bool(young.mean() > other.mean() and p < 0.05)
    return {
        "effect_name": "perseverance_age_youngest",
        "experiment": "exp0",
        "original_effect_size": None,
        "effect_size": float(young.mean() - other.mean()),
        "y3_4_mean": float(young.mean()),
        "others_mean": float(other.mean()),
        "t": float(t),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_perseverance_condition_effect(data: dict[str, pd.DataFrame]) -> dict:
    """"participants in the static high condition were ... 1.48 times more likely [to choose their preferred option] than participants in the static random condition (z = 5.86, p < .001)." — Thoma et al. 2025, p.13-14, Results (Perseverance)."""
    df = _preferred_option_rate(data["exp0"])
    sh = df.loc[df["condition"] == "static_high", "pref_rate"].values
    sr = df.loc[df["condition"] == "static_random", "pref_rate"].values
    t, p = stats.ttest_ind(sh, sr, equal_var=False)
    reproduced = bool(sh.mean() > sr.mean() and p < 0.05)
    return {
        "effect_name": "perseverance_condition_effect",
        "experiment": "exp0",
        "original_effect_size": None,
        "effect_size": float(sh.mean() - sr.mean()),
        "static_high_mean": float(sh.mean()),
        "static_random_mean": float(sr.mean()),
        "t": float(t),
        "p": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_static_high_probability_learning,
    check_perseverance_age_youngest,
    check_perseverance_condition_effect,
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
        orig = r.get("original_effect_size")
        orig_s = "n/a" if orig is None else f"{orig:.3f}"
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  {orig_s:>10}  "
              f"{r['effect_size']:>10.3f}  {'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()