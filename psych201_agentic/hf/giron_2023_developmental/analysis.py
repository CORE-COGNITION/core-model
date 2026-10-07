# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Giron et al. (2023), Developmental changes in
exploration resemble stochastic optimization, Nature Human Behaviour, against any dataset
in the Psych-301 unified schema (see schema.md).

Effects tested:
- performance_age (exp0+exp1+exp2): mean normalized reward should increase monotonically
  with age across participants (Pearson r); expected positive direction.
- unique_options_age (exp0+exp1+exp2): the number of unique options sampled per round
  should decrease with age (Kendall rank correlation); expected negative direction.
- search_distance_reward_modulation_age (exp0+exp1+exp2): per-participant regression slope
  of search distance on previous reward should become more negative (stronger win-stay /
  lose-shift) with age; expected negative direction.
"""
from __future__ import annotations

import argparse
import pandas as pd
import numpy as np
from scipy.stats import pearsonr, kendalltau, linregress

EXPERIMENTS = ["exp0", "exp1", "exp2"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns per experiment:
      exp0..exp2: participant_id, task_id, trial, response, zscaled, distance,
                  previous_reward, age_years
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _pooled(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Concatenate all experiments into one long frame for participant-level analyses."""
    return pd.concat(data.values(), ignore_index=True)


def _participant_age(df: pd.DataFrame) -> pd.Series:
    return df.groupby("participant_id")["age_years"].first()


def check_performance_age(data: dict[str, pd.DataFrame]) -> dict:
    """\"Participants monotonically achieved higher rewards as a function of age
    (Pearson correlation: r = 0.51, P < 0.001, BF > 100)\" — Giron et al., 2023,
    p.1957 (Results, Behavioural analyses, Performance)."""
    df = _pooled(data).dropna(subset=["zscaled"])
    per = df.groupby("participant_id").agg(
        age=("age_years", "first"), reward=("zscaled", "mean")
    )
    r, p = pearsonr(per["age"], per["reward"])
    reproduced = bool(r > 0 and p < 0.05)
    return {
        "effect_name": "performance_age",
        "experiment": "|".join(EXPERIMENTS),
        "original_effect_size": 0.51,
        "effect_size": float(r),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_unique_options_age(data: dict[str, pd.DataFrame]) -> dict:
    """\"The number of unique options decreased strongly as a function of age
    (r_tau = -0.33, P < 0.001, BF > 100)\" — Giron et al., 2023, p.1958
    (Results, Behavioural patterns)."""
    df = _pooled(data).dropna(subset=["response"])
    uniq = df.groupby(["participant_id", "task_id"])["response"].nunique()
    per_round = uniq.groupby("participant_id").mean()
    age = _participant_age(df)
    m = pd.DataFrame({"age": age, "unique": per_round}).dropna()
    rtau, p = kendalltau(m["age"], m["unique"])
    reproduced = bool(rtau < 0 and p < 0.05)
    return {
        "effect_name": "unique_options_age",
        "experiment": "|".join(EXPERIMENTS),
        "original_effect_size": -0.33,
        "effect_size": float(rtau),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_search_distance_reward_modulation_age(data: dict[str, pd.DataFrame]) -> dict:
    """\"We found a negative linear relationship in all age groups ... This trend
    becomes stronger over the lifespan, with monotonically more negative slopes over
    the lifespan\" — Giron et al., 2023, p.1958 (Results, Behavioural patterns),
    Supplementary Table 3."""
    df = _pooled(data).dropna(subset=["distance", "previous_reward"])
    age = _participant_age(df)
    slopes = {}
    for pid, g in df.groupby("participant_id"):
        if len(g) > 5:
            slopes[pid] = linregress(g["previous_reward"], g["distance"]).slope
    s = pd.Series(slopes, dtype=float)
    m = pd.DataFrame({"age": age, "slope": s.reindex(age.index)}).dropna()
    r, p = pearsonr(m["age"], m["slope"])
    reproduced = bool(r < 0 and p < 0.05)
    return {
        "effect_name": "search_distance_reward_modulation_age",
        "experiment": "|".join(EXPERIMENTS),
        "original_effect_size": 0.0,
        "effect_size": float(r),
        "p": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_performance_age,
    check_unique_options_age,
    check_search_distance_reward_modulation_age,
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
        print(f"{exp}: {sources[exp]}" if exp in sources else f"{exp}: (default — local ./{exp}.csv)")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<14}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<14}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
