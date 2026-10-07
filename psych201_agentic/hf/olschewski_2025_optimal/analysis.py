# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Olschewski, Mullett & Stewart (2025),
"Optimal allocation of time in risky choices under opportunity costs",
Cognitive Psychology 157, 101716, against any dataset in the Psych-301 unified
schema (see schema.md).

Effects tested:
- rt_error_positive_known (exp0): positive relation between mean-standardized RT
  and the rate of choosing the lower-rated lottery (an "error") in the known
  utility-difference condition; logistic regression, expected positive slope.
- error_higher_unknown (exp0): higher error rate when the utility difference is
  unknown vs known (Study 1 block manipulation), controlling for standardized RT
  and rating difference; logistic regression, expected positive coefficient on
  the unknown-difficulty indicator.
- time_limit_increases_error (exp1): higher error rate under a block time limit
  (higher opportunity cost) vs no time limit, controlling for standardized RT and
  rating; logistic regression, expected positive coefficient on the time-limit
  indicator.
"""
from __future__ import annotations

import argparse
import pandas as pd
import numpy as np
import statsmodels.api as sm

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, trial, response, errcho, rt, condition,
            player.ratingdiff, valid
      exp1: participant_id, trial, response, errcho, rt, condition,
            player.rating.x, player.rating.y, valid
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _prep(df: pd.DataFrame) -> pd.DataFrame:
    """Keep valid free choices, drop the 5% slowest and fastest RTs per
    participant per condition (as the paper pre-registered), and add the
    participant mean-standardized RT."""
    df = df[df["valid"] == 1].copy()
    df = df.dropna(subset=["rt", "errcho"])
    df["rt"] = df["rt"].astype(float)
    keep = []
    for _, g in df.groupby(["participant_id", "condition"]):
        if len(g) < 20:
            keep.append(g)
            continue
        lo, hi = g["rt"].quantile(0.05), g["rt"].quantile(0.95)
        keep.append(g[(g["rt"] >= lo) & (g["rt"] <= hi)])
    out = pd.concat(keep)
    out["stdrt"] = out["rt"] / out.groupby("participant_id")["rt"].transform("mean")
    return out


def _logit_coef(df: pd.DataFrame, y: str, predictors: list[str]) -> tuple:
    X = sm.add_constant(df[predictors])
    m = sm.Logit(df[y], X).fit(disp=0)
    return float(m.params[predictors[-1]]), float(m.pvalues[predictors[-1]])


def check_rt_error_positive_known(data: dict[str, pd.DataFrame]) -> dict:
    """\"There was a positive relation between RT and error rate in both conditions
    ... in the known difficulty condition it reached significance (Cohen's d = 0.28,
    see Table 1 Model 1)\" — Olschewski et al. 2025, p.8, Study 1 behavioral analyses."""
    df = _prep(data["exp0"])
    k = df[df["condition"] == "known_utility"]
    slope, p = _logit_coef(k, "errcho", ["stdrt"])
    return {
        "effect_name": "rt_error_positive_known",
        "experiment": "exp0",
        "original_effect_size": 0.16,   # Stan.-RT logistic coefficient, Table 1 Model 1
        "effect_size": slope,
        "p": p,
        "reproduced": bool(slope > 0 and p < 0.05),
    }


def check_error_higher_unknown(data: dict[str, pd.DataFrame]) -> dict:
    """\"when contrasting the known and unknown difficulty blocks, we see that for
    every given mean-standardized RT and rating difference, the error rate was higher
    when the rating difference was unknown compared to known (d = 0.41, Table 1 Model 3)\"
    — Olschewski et al. 2025, p.8, Study 1 behavioral analyses."""
    df = _prep(data["exp0"])
    df["unknown"] = (df["condition"] == "unknown_utility").astype(int)
    coef, p = _logit_coef(df, "errcho", ["stdrt", "player.ratingdiff", "unknown"])
    return {
        "effect_name": "error_higher_unknown",
        "experiment": "exp0",
        "original_effect_size": 0.26,   # Unknown logistic coefficient, Table 1 Model 3
        "effect_size": coef,
        "p": p,
        "reproduced": bool(coef > 0 and p < 0.05),
    }


def check_time_limit_increases_error(data: dict[str, pd.DataFrame]) -> dict:
    """\"Regarding the effect of opportunity costs, we found a significant positive
    main effect of the time limit condition on error rates, while controlling for RTs
    and ratings (d = 0.63; ... Table 3, Model 5)\" — Olschewski et al. 2025, p.11,
    Study 2 behavioral analyses."""
    df = _prep(data["exp1"])
    df["rating"] = df["player.rating.x"] - df["player.rating.y"]
    df["time_limit"] = (df["condition"] == "time_limit").astype(int)
    coef, p = _logit_coef(df, "errcho", ["stdrt", "rating", "time_limit"])
    return {
        "effect_name": "time_limit_increases_error",
        "experiment": "exp1",
        "original_effect_size": 0.30,   # Time limit logistic coefficient, Table 3 Model 5
        "effect_size": coef,
        "p": p,
        "reproduced": bool(coef > 0 and p < 0.05),
    }


EFFECTS = [check_rt_error_positive_known, check_error_higher_unknown,
           check_time_limit_increases_error]


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
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  {'p':>8}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{r['p']:>8.2e}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()