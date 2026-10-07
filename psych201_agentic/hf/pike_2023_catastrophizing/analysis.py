# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Pike et al. (2023) Catastrophizing and
Risk-Taking against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- cost_manipulation_effect (exp1): participants pump fewer times in high-cost vs low-cost blocks of the BART (Welch t-test on per-participant means excluding burst trials); expected: fewer pumps in high-cost.
- catastrophizing_lc_correlation (exp1): negative correlation between catastrophizing scores and mean pumps in the low-cost block (Pearson r on sqrt-transformed per-participant means excluding burst trials); expected: negative r.
- cost_catastrophizing_interaction (exp1): cost level moderates the relationship between catastrophizing and pumps (mixed model with cost × catastrophizing, random intercept of participant); expected: significant interaction with more negative relationship in LC.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, ttest_ind
import statsmodels.formula.api as smf

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_cost_manipulation_effect(data: dict[str, pd.DataFrame]) -> dict:
    """"there was a significant difference in the mean number of pumps in each block (low cost mean = 8.44 (sd = 2.25), high cost mean = 7.14(2.56), t474.34 = 5.97, p < 0.001)" — Pike et al. 2023, p.7, Main Study Results, Model-free analysis."""
    df = data["exp1"]
    df = df[(df["task"] == "bart") & (df["phase"] == "test") & (df["explosion"] == 0)]
    lc = df[df["condition"] == "low_cost"].groupby("participant_id")["response"].mean()
    hc = df[df["condition"] == "high_cost"].groupby("participant_id")["response"].mean()
    common = lc.index.intersection(hc.index)
    t_stat, p_val = ttest_ind(lc[common], hc[common], equal_var=False)
    reproduced = bool((lc[common].mean() > hc[common].mean()) and (p_val < 0.05))
    return {
        "effect_name": "cost_manipulation_effect",
        "experiment": "exp1",
        "original_effect_size": 5.97,
        "original_stat": "t(474.34)=5.97, p<.001",
        "effect_size": float(t_stat),
        "p_value": float(p_val),
        "reproduced": reproduced,
    }


def check_catastrophizing_lc_correlation(data: dict[str, pd.DataFrame]) -> dict:
    """"We found a significant correlation between Catastrophizing scores and the transformed mean number of pumps in the LC block (r260 = -0.156, p = .012, Figure 3A)" — Pike et al. 2023, p.7-8, Main Study Results, Model-free analysis."""
    df = data["exp1"]
    df = df[(df["task"] == "bart") & (df["phase"] == "test") & (df["explosion"] == 0)]
    lc = df[df["condition"] == "low_cost"].groupby("participant_id")["response"].mean()
    cat = df.groupby("participant_id")["total_catastrophizing"].first()
    common = lc.index.intersection(cat.dropna().index)
    lc_vals = lc[common].values
    cat_vals = cat[common].values
    max_lc = lc_vals.max()
    trans_lc = np.sqrt(max_lc - lc_vals)
    r, p = pearsonr(trans_lc, cat_vals)
    # sqrt(max-x) reverses rank order, so the reported sign is in the
    # original (untransformed) direction: higher catastrophizing → fewer pumps.
    # Check reproduction against raw (untransformed) correlation.
    r_raw, _ = pearsonr(lc_vals, cat_vals)
    reproduced = bool((r_raw < 0) and (p < 0.05))
    return {
        "effect_name": "catastrophizing_lc_correlation",
        "experiment": "exp1",
        "original_effect_size": -0.156,
        "original_stat": "r(260)=-0.156, p=.012",
        "effect_size": float(r),
        "p_value": float(p),
        "reproduced": reproduced,
    }


def check_cost_catastrophizing_interaction(data: dict[str, pd.DataFrame]) -> dict:
    """"cost level was a moderator of the effect of number of pumps on catastrophizing in a mixed model including cost, Catastrophizing score, and a random intercept of participant (F1,243.73 = 4.45; p = 0.036)" — Pike et al. 2023, p.8, Main Study Results, Model-free analysis."""
    df = data["exp1"]
    df = df[(df["task"] == "bart") & (df["phase"] == "test") & (df["explosion"] == 0)]
    lc = df[df["condition"] == "low_cost"].groupby("participant_id")["response"].mean()
    hc = df[df["condition"] == "high_cost"].groupby("participant_id")["response"].mean()
    cat = df.groupby("participant_id")["total_catastrophizing"].first()
    common = lc.index.intersection(hc.index).intersection(cat.dropna().index)
    lc_vals = lc[common]
    hc_vals = hc[common]
    max_lc = lc_vals.max()
    max_hc = hc_vals.max()
    lc_trans = np.sqrt(max_lc - lc_vals)
    hc_trans = np.sqrt(max_hc - hc_vals)
    cat_vals = cat[common]
    long = pd.DataFrame({
        "participant_id": list(common) * 2,
        "condition": ["low_cost"] * len(common) + ["high_cost"] * len(common),
        "mean_pumps": list(lc_trans) + list(hc_trans),
        "cat": list(cat_vals) * 2,
    })
    long["cat_c"] = long["cat"] - long["cat"].mean()
    md = smf.mixedlm("mean_pumps ~ condition * cat_c", long, groups=long["participant_id"])
    mdf = md.fit()
    coef_name = "condition[T.low_cost]:cat_c"
    coef_val = mdf.params[coef_name]
    p_val = mdf.pvalues[coef_name]
    reproduced = bool((p_val < 0.05))
    return {
        "effect_name": "cost_catastrophizing_interaction",
        "experiment": "exp1",
        "original_effect_size": None,
        "original_stat": "F(1,243.73)=4.45, p=.036",
        "effect_size": float(coef_val),
        "p_value": float(p_val),
        "reproduced": reproduced,
    }


EFFECTS = [check_cost_manipulation_effect, check_catastrophizing_lc_correlation, check_cost_catastrophizing_interaction]


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
        if exp in sources:
            print(f"{exp}: {sources[exp]}")
        else:
            print(f"{exp}: (default — local ./{exp}.csv)")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    header = f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  {'p':>8}  reproduced"
    print(header)
    for r in results:
        orig = r.get("original_effect_size", "N/A")
        orig_str = f"{orig:>10.3f}" if isinstance(orig, float) else f"{str(orig):>10}"
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  {orig_str}  {r['effect_size']:>10.3f}  {r['p_value']:>8.4f}  {'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()