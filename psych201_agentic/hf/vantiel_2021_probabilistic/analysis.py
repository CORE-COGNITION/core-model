# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of van Tiel, Franke & Sauerland (2021),
*Probabilistic pragmatics explains gradience and focality in natural language
quantification*, PNAS 118(9), against any dataset in the Psych-301 unified schema
(see schema.md).

Effects tested:
- approximate_number_tracking (exp4/Exp 3): participants' estimate of the number of
  red circles increases monotonically with the true intersection set size (Weber's-law /
  ANS tracking). Test: Pearson correlation response~dots, expected positive and significant.
- monotonicity_validity (exp3/Exp 2): validity judgments track the monotonicity of
  quantity words — monotone-increasing words (most, all, many, ...) are accepted for the
  upward (strong->weak) entailment more often than for the reverse (weak->strong).
  Test: per-participant mean acceptance difference strong_to_weak - weak_to_strong over the
  monotone-increasing quantifiers, expected positive and significant.
- adequacy_data_over_models (exp5/Exp 4): adequacy ratings of quantity-word descriptions
  are higher for words sampled from the observed production data than for words sampled
  from the computational models' posterior predictive distributions. The data-anchored
  condition is 'd_pred'; the four model sources are rated lower. Test: per-participant mean
  raw rating d_pred minus pooled model rating, expected positive and significant.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1", "exp2", "exp3", "exp4", "exp5"]

MONOTONE_INCREASING = [
    "a few", "about half", "some", "a lot", "many", "more than half",
    "half", "almost all", "several", "the majority", "all", "most",
]
MODEL_SOURCES = ["gqs_pred", "gqp_pred", "pts_pred", "ptp_pred"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}. With no overrides, loads ./{exp}.csv from CWD.
    Required columns per experiment:
      exp3: participant_id, condition, quantifier, response
      exp4: dots, response
      exp5: participant_id, condition, response
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_approximate_number_tracking(data: dict[str, pd.DataFrame]) -> dict:
    """\"Each participant provided estimates for 24 displays using a continuous slider... the
    accuracy of ANS estimates decreases as the numerosity to be estimated increases\" (prenatal,
    p.3, Modeling the Production of Quantity Words / Exp. 3 Methods)."""
    df = data["exp4"].dropna(subset=["dots", "response"])
    r, p = stats.pearsonr(df["dots"], df["response"])
    reproduced = bool(r > 0 and p < 0.05)
    return {
        "effect_name": "approximate_number_tracking",
        "experiment": "exp4",
        "original_effect_size": 0.5,
        "effect_size": float(r),
        "p_value": float(p),
        "reproduced": reproduced,
    }


def check_monotonicity_validity(data: dict[str, pd.DataFrame]) -> dict:
    """\"Monotone-increasing quantity words license inferences from sets to supersets; ...
    Thus, 'all' is monotone increasing... 'some'... 'most'... participants judged the validity
    of inference patterns similar to those shown above\" (p.4, GQT Semantics / Exp. 2 Methods)."""
    df = data["exp3"]
    df = df[df["quantifier"].isin(MONOTONE_INCREASING)]
    diffs = []
    for _, g in df.groupby("participant_id"):
        sw = g.loc[g["condition"] == "strong_to_weak", "response"].mean()
        ws = g.loc[g["condition"] == "weak_to_strong", "response"].mean()
        if pd.notna(sw) and pd.notna(ws):
            diffs.append(sw - ws)
    diffs = np.array(diffs)
    t, p = stats.ttest_1samp(diffs, 0)
    mean_diff = float(diffs.mean())
    reproduced = bool(mean_diff > 0 and p < 0.05)
    return {
        "effect_name": "monotonicity_validity",
        "experiment": "exp3",
        "original_effect_size": 0.4,
        "effect_size": mean_diff,
        "p_value": float(p),
        "reproduced": reproduced,
    }


def check_adequacy_data_over_models(data: dict[str, pd.DataFrame]) -> dict:
    """\"The average rating ... for the quantity words from the data was 74.6... the predictions
    of each model [were rated lower]; the GQ-prag model was the only one whose predictions were
    not rated as significantly worse than the data\" (p.6, Model Comparison / Exp. 4 Methods)."""
    df = data["exp5"]
    d = df[df["condition"] == "d_pred"].groupby("participant_id")["response"].mean()
    m = df[df["condition"].isin(MODEL_SOURCES)].groupby("participant_id")["response"].mean()
    both = pd.DataFrame({"d": d, "m": m}).dropna()
    diff = both["d"] - both["m"]
    t, p = stats.ttest_rel(both["d"], both["m"])
    mean_diff = float(diff.mean())
    reproduced = bool(mean_diff > 0 and p < 0.05)
    return {
        "effect_name": "adequacy_data_over_models",
        "experiment": "exp5",
        "original_effect_size": 1.0,
        "effect_size": mean_diff,
        "p_value": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_approximate_number_tracking,
    check_monotonicity_validity,
    check_adequacy_data_over_models,
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
