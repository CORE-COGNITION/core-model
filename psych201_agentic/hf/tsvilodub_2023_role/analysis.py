# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Tsvilodub, van Tiel & Franke (2023,
"The role of relevance, competence, and priors for scalar inferences") against any
dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- competence_raises_inference_some (exp0): on 'some'-inference trials, the participant's
  competence rating of the speaker (0-100) should predict higher scalar-inference
  strength ratings; regression slope positive (paper: P=1, positive).
- prior_lowers_inference_some (exp0): on 'some'-inference trials, a higher prior
  probability that the stronger alternative ('all') is true should predict lower
  scalar-inference strength ratings; regression slope negative (paper: P=0.999, negative).
- competence_raises_inference_or (exp0): on 'or'-inference trials, the participant's
  competence rating of the speaker should predict higher scalar-inference strength
  ratings; regression slope positive (paper: P=0.993, positive).
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd

from statsmodels.formula.api import ols

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, trial, response, condition, trial_type, trigger,
            item_id (relevance, competence, prior ratings on rel/comp/pri rows)
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _build_ratings_table(df: pd.DataFrame) -> pd.DataFrame:
    """Merge, per (participant, item), the scalar-inference strength rating
    (trial_type 'some'/'xor' rows) with the factor ratings (rel/comp/pri rows)."""
    crit = df[df["condition"] == "critical"].copy()
    inf = crit[crit["trial_type"].isin(["some", "xor"])].copy()
    fac = crit[crit["trial_type"].isin(["rel", "comp", "pri"])].copy()
    ratings = fac.pivot_table(
        index=["participant_id", "item_id"],
        columns="trial_type",
        values="response",
    ).rename(columns={"rel": "rel_rat", "comp": "comp_rat", "pri": "pri_rat"})
    t = inf.merge(ratings, on=["participant_id", "item_id"], how="left")
    t["trigger"] = t["trial_type"]
    for col in ["response", "rel_rat", "comp_rat", "pri_rat"]:
        t[col + "_z"] = t.groupby("participant_id")[col].transform(
            lambda s: (s - s.mean()) / s.std() if s.std() > 0 else np.nan
        )
    return t


def _trigger_slope(tab: pd.DataFrame, trigger: str, predictor: str) -> tuple[float, float]:
    """Cluster-robust OLS slope of z-scored inference rating on a z-scored
    predictor rating, restricted to one trigger. Returns (slope, pvalue)."""
    tt = tab[
        (tab["trigger"] == trigger)
        & tab["response_z"].notna()
        & tab[predictor].notna()
    ]
    model = ols(f"response_z ~ {predictor}", data=tt).fit(
        cov_type="cluster", cov_kwds={"groups": tt["participant_id"]}
    )
    return float(model.params[predictor]), float(model.pvalues[predictor])


def check_competence_raises_inference_some(data: dict[str, pd.DataFrame]) -> dict:
    """"for the trigger 'some', we found a clear positive effect for speaker competence (P = 1, Fig. 3B, Competence (some), green color)" — Tsvilodub et al. 2023, p.295, Results 4.1."""
    tab = _build_ratings_table(data["exp0"])
    slope, p = _trigger_slope(tab, "some", "comp_rat_z")
    return {
        "effect_name": "competence_raises_inference_some",
        "experiment": "exp0",
        "original_effect_size": 1.0,
        "effect_size": slope,
        "p": p,
        "n": int(((tab["trigger"] == "some") & tab["comp_rat_z"].notna()).sum()),
        "reproduced": bool(slope > 0 and p < 0.05),
    }


def check_prior_lowers_inference_some(data: dict[str, pd.DataFrame]) -> dict:
    """"Consistent with predictions of the standard account, for the trigger 'some', we found a clear negative effect of prior probability of the stronger alternative 'all' being true, as indicated by the probability of the negative effect of prior being P = 0.999" — Tsvilodub et al. 2023, p.295, Results 4.1."""
    tab = _build_ratings_table(data["exp0"])
    slope, p = _trigger_slope(tab, "some", "pri_rat_z")
    return {
        "effect_name": "prior_lowers_inference_some",
        "experiment": "exp0",
        "original_effect_size": 0.999,
        "effect_size": slope,
        "p": p,
        "n": int(((tab["trigger"] == "some") & tab["pri_rat_z"].notna()).sum()),
        "reproduced": bool(slope < 0 and p < 0.05),
    }


def check_competence_raises_inference_or(data: dict[str, pd.DataFrame]) -> dict:
    """"for the trigger 'or', we only found a positive effect of competence (P = 0.993, Fig. 3B, Competence (or), green color)" — Tsvilodub et al. 2023, p.295, Results 4.1."""
    tab = _build_ratings_table(data["exp0"])
    slope, p = _trigger_slope(tab, "xor", "comp_rat_z")
    return {
        "effect_name": "competence_raises_inference_or",
        "experiment": "exp0",
        "original_effect_size": 0.993,
        "effect_size": slope,
        "p": p,
        "n": int(((tab["trigger"] == "xor") & tab["comp_rat_z"].notna()).sum()),
        "reproduced": bool(slope > 0 and p < 0.05),
    }


EFFECTS = [
    check_competence_raises_inference_some,
    check_prior_lowers_inference_some,
    check_competence_raises_inference_or,
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