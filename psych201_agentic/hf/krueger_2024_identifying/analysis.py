# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Krueger, Callaway, Gul, Griffiths & Lieder
(2024), "Identifying resource-rational heuristics for risky choice", against any dataset
in the Psych-301 unified schema (see schema.md).

Effects tested:
- info_gathering_decreases_with_cost (exp0): total information gathered (number of cells
  clicked on a trial) decreases as the per-click cost increases. OLS of n_clicks on cost,
  clustered by participant; expected negative slope, p < .05.
- more_attribute_based_processing_with_cost (exp0): as click cost increases participants
  shift toward attribute-based (rows/outcomes) processing, i.e. the alternative-vs-attribute
  Payne index becomes more negative. Clustered OLS of the Payne index on cost; expected
  negative slope, p < .05.
- ev_display_increases_info_gathering (exp1): participants in the experimental (EV-display
  + 20s minimum) group gather more information than those in the control group. Two-sample
  t-test of per-participant mean clicks, exp > con, p < .05.
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, trial, response, clicks, cost, phase
      exp1: participant_id, trial, response, clicks, condition, phase
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _n_clicks(x) -> int:
    if not isinstance(x, str) or x == "[]" or x == "":
        return 0
    try:
        return len(json.loads(x))
    except Exception:
        return 0


def _payne_index(x) -> float:
    """Alternative- vs attribute-based processing. Rows=outcomes, cols=gambles.
    +1 = alternative-based, -1 = attribute-based."""
    if not isinstance(x, str) or x == "[]":
        return np.nan
    try:
        clicks = json.loads(x)
    except Exception:
        return np.nan
    if len(clicks) < 2:
        return np.nan
    alt = att = 0
    for i in range(len(clicks) - 1):
        r1, c1 = clicks[i] // 6, clicks[i] % 6
        r2, c2 = clicks[i + 1] // 6, clicks[i + 1] % 6
        if r1 == r2 and c1 != c2:
            att += 1
        elif c1 == c2 and r1 != r2:
            alt += 1
    if alt + att == 0:
        return np.nan
    return (alt - att) / (alt + att)


def check_info_gathering_decreases_with_cost(data: dict[str, pd.DataFrame]) -> dict:
    """"Finally, people reduced information gathering as it became more costly to do so
    (B = −1.9, p < 0.001)." — Krueger et al., p.29, "Understanding variability in choice
    behavior"."""
    df = data["exp0"]
    df = df[df["phase"] == "test"].copy()
    df["n"] = df["clicks"].apply(_n_clicks)
    X = sm.add_constant(df["cost"].astype(float))
    m = sm.OLS(df["n"], X).fit(
        cov_type="cluster", cov_kwds={"groups": df["participant_id"]}
    )
    b = float(m.params["cost"])
    p = float(m.pvalues["cost"])
    return {
        "effect_name": "info_gathering_decreases_with_cost",
        "experiment": "exp0",
        "original_effect_size": -1.9,
        "effect_size": b,
        "n": int(len(df)),
        "p": p,
        "reproduced": bool(b < 0 and p < 0.05),
    }


def check_more_attribute_based_processing_with_cost(
    data: dict[str, pd.DataFrame],
) -> dict:
    """"they used more attribute-based processing as ... cost increased
    (B = −0.073, p < 0.001)." — Krueger et al., p.30, "Understanding variability in choice
    behavior"."""
    df = data["exp0"]
    df = df[df["phase"] == "test"].copy()
    df["pay"] = df["clicks"].apply(_payne_index)
    d = df.dropna(subset=["pay"])
    X = sm.add_constant(d["cost"].astype(float))
    m = sm.OLS(d["pay"], X).fit(
        cov_type="cluster", cov_kwds={"groups": d["participant_id"]}
    )
    b = float(m.params["cost"])
    p = float(m.pvalues["cost"])
    return {
        "effect_name": "more_attribute_based_processing_with_cost",
        "experiment": "exp0",
        "original_effect_size": -0.073,
        "effect_size": b,
        "n": int(len(d)),
        "p": p,
        "reproduced": bool(b < 0 and p < 0.05),
    }


def check_ev_display_increases_info_gathering(data: dict[str, pd.DataFrame]) -> dict:
    """"In each environment, participants in the experimental group gathered more
    information than those in the control group (two-sample t-tests; ...)". — Krueger
    et al., p.45, "Information gathering and choice behavior"."""
    df = data["exp1"]
    df = df[df["phase"] == "test"].copy()
    df["n"] = df["clicks"].apply(_n_clicks)
    g = df.groupby("participant_id").agg(
        cond=("condition", "first"), n=("n", "mean")
    )
    con = g.n[g.cond == "con"]
    exp = g.n[g.cond == "exp"]
    t, p = stats.ttest_ind(exp, con)
    d = (exp.mean() - con.mean()) / con.std(ddof=1)
    return {
        "effect_name": "ev_display_increases_info_gathering",
        "experiment": "exp1",
        "original_effect_size": 0.96,
        "effect_size": float(d),
        "n": int(len(g)),
        "p": float(p),
        "reproduced": bool(exp.mean() > con.mean() and p < 0.05),
    }


EFFECTS = [
    check_info_gathering_decreases_with_cost,
    check_more_attribute_based_processing_with_cost,
    check_ev_display_increases_info_gathering,
]


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
