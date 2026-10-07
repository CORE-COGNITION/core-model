# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Haines et al. (2020), "Anxiety Modulates
Preference for Immediate Rewards Among Trait-Impulsive Individuals: A Hierarchical
Bayesian Analysis", Clinical Psychological Science 8(6), against any dataset in the
Psych-301 unified schema (see schema.md).

Effects tested:
- delay_discounting_gradient (exp0): participants discount delayed rewards — as the
  delay to the larger-later reward (rightTime) increases, and as the smaller-sooner
  amount (leftValue) increases, the probability of choosing the larger-later option
  (response=1) decreases. Test: pooled logistic regression of response on leftValue
  and rightTime; both coefficients expected negative and p < .05.
- impulsivity_discounting_correlation (exp0): higher trait impulsivity (BIS-NP)
  predicts steeper delay discounting (higher k / lower proportion of larger-later
  choices). Test: Pearson correlation between participant-level BIS-NP and their
  proportion of larger-later (LL) choices; expected negative (i.e., steeper
  discounting with higher impulsivity) and p < .05.
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

EXPERIMENTS = ["exp0"]

NUMERIC = ["leftValue", "leftTime", "rightValue", "rightTime"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}. Required cols for exp0:
    participant_id, phase, response, leftValue, rightValue, rightTime, sample,
    bis_noplan."""
    sources = sources or {}
    out = {}
    for exp in EXPERIMENTS:
        df = pd.read_csv(sources.get(exp, f"./{exp}.csv"), low_memory=False)
        for c in NUMERIC:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["response"] = pd.to_numeric(df["response"], errors="coerce")
        out[exp] = df
    return out


def check_delay_discounting_gradient(data: dict[str, pd.DataFrame]) -> dict:
    """\""Given the high heritability of impulsivity and its associations ... Steeper
    discounting rates have been observed among individuals with ... delay-discounting
    tasks (DDTs)... discounting rates, which describe how precipitously they discount
    rewards as a function of increasing time delay to receipt of reward.\"" — Haines
    et al., 2020, p.2-3, Introduction; Method (DDT)."""
    df = data["exp0"]
    ms = df[(df["phase"] == "main") & df["response"].notna()].copy()
    X = pd.DataFrame({
        "ss": ms["leftValue"],
        "delay": ms["rightTime"],
    })
    X = sm.add_constant(X)
    y = ms["response"].astype(float)
    fit = sm.Logit(y, X).fit(disp=0)
    ss_coef = fit.params["ss"]
    delay_coef = fit.params["delay"]
    ss_p = fit.pvalues["ss"]
    delay_p = fit.pvalues["delay"]
    reproduced = (ss_coef < 0 and ss_p < 0.05 and delay_coef < 0 and delay_p < 0.05)
    return {
        "effect_name": "delay_discounting_gradient",
        "experiment": "exp0",
        "original_effect_size": -1.0,
        "effect_size": float(delay_coef),
        "reproduced": bool(reproduced),
        "details": {"ss_coef": float(ss_coef), "ss_p": float(ss_p),
                    "delay_p": float(delay_p)},
    }


def check_impulsivity_discounting_correlation(data: dict[str, pd.DataFrame]) -> dict:
    """\""In addition, we found a positive association between BIS-NP and k such that
    increases in trait impulsivity predicted increases in delay discounting (95% HDI
    on \u03b2k1 = [0.20, 0.40])."" — Haines et al., 2020, p.12, Results (Explanatory
    models)."""
    df = data["exp0"]
    ms = df[(df["phase"] == "main") & df["response"].notna()].copy()
    ms = ms[ms["sample"].isin(["rep", "tal"])]  # lab samples (student and SUD groups)
    g = ms.groupby("participant_id").agg(
        ll=("response", "mean"),
        bis=("bis_noplan", "first"),
    ).dropna(subset=["bis"])
    if len(g) < 10:
        return {"effect_name": "impulsivity_discounting_correlation",
                "experiment": "exp0", "original_effect_size": 0.2,
                "effect_size": float("nan"), "reproduced": False,
                "details": {"n": int(len(g)), "reason": "too few BIS observations"}}
    r = stats.pearsonr(g["ll"], g["bis"])
    # Higher BIS-NP -> fewer LL choices = steeper discounting => negative r
    reproduced = bool(r.statistic < 0 and r.pvalue < 0.05)
    return {"effect_name": "impulsivity_discounting_correlation",
            "experiment": "exp0", "original_effect_size": 0.2,
            "effect_size": float(r.statistic), "reproduced": reproduced,
            "details": {"p": float(r.pvalue), "n": int(len(g))}}


EFFECTS = [check_delay_discounting_gradient, check_impulsivity_discounting_correlation]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. Pure return value."""
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
