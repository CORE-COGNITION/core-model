# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Christian, Russek, & Griffiths (2026),
"Resolving Feynman's restaurant problem reveals optimal solutions and human
strategies", Proc Natl Acad Sci USA 123(23):e2509612123, against any dataset
in the Psych-301 unified schema (see schema.md).

Effects tested:
- exploit_increases_as_nights_remaining_decreases (exp0): logistic regression of
  exploit choice (response==1, freely-chosen valid trials only) on nights_remaining;
  expected negative coefficient (people explore early, exploit late).
- exploit_timing_across_horizons (exp0): the same negative effect reproduces within
  each total_nights horizon (7, 14, 28); each subgroup's coefficient must be negative
  and significant.
- runtime_balance (exp0): total_nights is balanced across participants (equal counts
  of 7/14/28-night sequences); a chi-square test of equal participant counts should
  not reject balance.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import chi2_contingency

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, trial, response, total_nights, nights_remaining, valid
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    out = df[df["valid"] == 1].copy()
    out["exploit"] = (out["response"] == 1).astype(int)
    return out


def check_exploit_increases_as_nights_remaining_decreases(data: dict[str, pd.DataFrame]) -> dict:
    """\"...people adopt thresholds that decrease linearly with the proportion of
    trials remaining...\" — Christian et al. 2026, p. e2509612123-2, Results /
    Abstract. Exploitation (returning to the best seen) rises as nights remaining
    falls: logistic regression of exploit on nights_remaining should have a
    negative, significant coefficient."""
    df = _clean(data["exp0"])
    X = sm.add_constant(df["nights_remaining"])
    model = sm.Logit(df["exploit"], X).fit(disp=0)
    beta = float(model.params["nights_remaining"])
    p = float(model.pvalues["nights_remaining"])
    reproduced = bool(beta < 0 and p < 0.05)
    return {
        "effect_name": "exploit_increases_as_nights_remaining_decreases",
        "experiment": "exp0",
        "original_effect_size": -0.073,
        "effect_size": beta,
        "pvalue": p,
        "reproduced": reproduced,
    }


def check_exploit_timing_across_horizons(data: dict[str, pd.DataFrame]) -> dict:
    """\"...thresholds that decrease linearly with the proportion of trials
    remaining... [holding across] all twelve combinations of total-nights and
    distribution conditions\" — Christian et al. 2026, p. e2509612123-5, Results /
    Effects of Distribution. The exploit-as-nights-decrease effect must hold in
    every total_nights horizon (7, 14, 28)."""
    df = _clean(data["exp0"])
    results = {}
    for T in sorted(df["total_nights"].unique()):
        d = df[df["total_nights"] == T]
        model = sm.Logit(d["exploit"], sm.add_constant(d["nights_remaining"])).fit(disp=0)
        results[int(T)] = {"beta": float(model.params["nights_remaining"]),
                           "p": float(model.pvalues["nights_remaining"])}
    slope = np.mean([r["beta"] for r in results.values()])
    reproduced = bool(all(r["beta"] < 0 and r["p"] < 0.05 for r in results.values()))
    return {
        "effect_name": "exploit_timing_across_horizons",
        "experiment": "exp0",
        "original_effect_size": -0.073,
        "effect_size": slope,
        "pvalue": max(r["p"] for r in results.values()),
        "per_horizon": results,
        "reproduced": reproduced,
    }


def check_runtime_balance(data: dict[str, pd.DataFrame]) -> dict:
    """\"The total number of nights was also varied across participants (7, 14, or
    28)\" — Christian et al. 2026, p. e2509612123-4, Results/Identifying Human
    Policies. Participant counts per total_nights should be balanced across the
    three horizons (chi-square of equal counts n.s.)."""
    df = data["exp0"]
    counts = df.groupby("total_nights")["participant_id"].nunique()
    observed = counts.reindex(sorted(counts.index)).values.astype(float)
    expected = np.full_like(observed, observed.mean())
    chi2, p = chi2_contingency([observed, expected])[:2]
    effect = float(np.std(observed) / observed.mean() + 1e-9)
    reproduced = bool(p >= 0.05)
    return {
        "effect_name": "runtime_balance",
        "experiment": "exp0",
        "original_effect_size": 0.0,
        "effect_size": effect,
        "pvalue": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_exploit_increases_as_nights_remaining_decreases,
    check_exploit_timing_across_horizons,
    check_runtime_balance,
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
