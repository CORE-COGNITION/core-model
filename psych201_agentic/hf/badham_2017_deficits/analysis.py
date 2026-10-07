# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Badham, Sanborn & Maylor (2017),
"Deficits in Category Learning in Older Adults: Rule-Based Versus Clustering
Accounts" (Psychology and Aging) against any dataset in the Psych-301 unified
schema (see schema.md).

Effects tested:
- learning_over_blocks (exp0): classification accuracy should improve across the
  6 learning blocks; a paired t-test of block 5 vs block 0 per participant should
  show a positive increase (p < .05).
- age_main_effect (exp0): young adults should be more accurate than older adults
  overall; an independent-samples t-test on per-participant mean accuracy should
  show younger > older (p < .05).
- structure_complexity (exp0): Type I (one relevant dimension) should be learned
  better than the more complex Types II-IV; a paired t-test of mean Type I
  accuracy vs mean of Types II-IV per participant should show Type I > others.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0"]

ACC_COL = "correct"


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns per experiment:
      exp0: participant_id, condition, block, age_group, correct
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _participant_means(df: pd.DataFrame, groupby: list[str]) -> pd.DataFrame:
    return df.groupby(groupby)[ACC_COL].mean().reset_index()


def check_learning_over_blocks(data: dict[str, pd.DataFrame]) -> dict:
    """\"A main effect of block showed that performance improved over time, F(3.31,
    311.55) = 138.91, ... BF > 10^12\" — Badham et al. 2017, p.16, Results."""
    df = data["exp0"]
    first = df[df["block"] == df["block"].min()].groupby("participant_id")[ACC_COL].mean()
    last = df[df["block"] == df["block"].max()].groupby("participant_id")[ACC_COL].mean()
    # a participant who reached the stop criterion in every condition has no last block
    common = first.index.intersection(last.index)
    first, last = first.loc[common], last.loc[common]
    t, p = stats.ttest_rel(last, first)
    effect_size = float(last.mean() - first.mean())
    reproduced = bool(effect_size > 0 and p < 0.05)
    return {
        "effect_name": "learning_over_blocks",
        "experiment": "exp0",
        "original_effect_size": 0.60,  # eta^2 of the block main effect
        "effect_size": effect_size,
        "reproduced": reproduced,
        "p": float(p),
        "t": float(t),
    }


def check_age_main_effect(data: dict[str, pd.DataFrame]) -> dict:
    """\"Young adults were more accurate than older adults, F(1, 94) = 48.86, ...
    BF = 3.16 x 10^12\" — Badham et al. 2017, p.15, Results."""
    df = data["exp0"]
    means = _participant_means(df, ["participant_id", "age_group"])
    young = means.loc[means["age_group"].astype(str).str.lower().isin(["young", "younger"]), ACC_COL]
    older = means.loc[means["age_group"].astype(str).str.lower().isin(["old", "older"]), ACC_COL]
    t, p = stats.ttest_ind(young, older)
    effect_size = float(young.mean() - older.mean())
    reproduced = bool(effect_size > 0 and p < 0.05)
    return {
        "effect_name": "age_main_effect",
        "experiment": "exp0",
        "original_effect_size": 0.34,  # eta^2 of the age main effect
        "effect_size": effect_size,
        "reproduced": reproduced,
        "p": float(p),
        "t": float(t),
    }


def check_structure_complexity(data: dict[str, pd.DataFrame]) -> dict:
    """\"There was a main effect of condition ... with Type I learned better than
    all other conditions\" — Badham et al. 2017, p.15-16, Results."""
    df = data["exp0"]
    means = _participant_means(df, ["participant_id", "condition"])
    type1 = means.loc[means["condition"] == "type_1"].set_index("participant_id")[ACC_COL]
    others = (
        means.loc[means["condition"] != "type_1"]
        .groupby("participant_id")[ACC_COL]
        .mean()
    )
    common = type1.index.intersection(others.index)
    t, p = stats.ttest_rel(type1.loc[common], others.loc[common])
    effect_size = float((type1.loc[common] - others.loc[common]).mean())
    reproduced = bool(effect_size > 0 and p < 0.05)
    return {
        "effect_name": "structure_complexity",
        "experiment": "exp0",
        "original_effect_size": 0.58,  # eta^2 of the condition main effect
        "effect_size": effect_size,
        "reproduced": reproduced,
        "p": float(p),
        "t": float(t),
    }


EFFECTS = [check_learning_over_blocks, check_age_main_effect, check_structure_complexity]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing — pure return value."""
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
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
