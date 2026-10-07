# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy", "numpy"]
# ///
"""Check the primary behavioral effects of Cheung et al. (2024) "Large Language Models
Amplify Human Biases in Moral Decision-Making" against any dataset in the Psych-301
unified schema (see schema.md).

Effects tested:
- omission_bias_study1 (exp0): Omission bias in humans — higher proportion of utilitarian
  (CBR) choices when sacrificial dilemmas are omission-framed vs action-framed. Paired
  t-test on within-subject per-participant mean CBR choice rates.
- framing_effect_study2 (exp1): Framing (base/yesno/omission) affects binary choice in
  sacrificial dilemmas (Study 2). Chi-square test of independence.
- framing_effect_study3 (exp2): Framing (base/yesno/omission) affects binary choice in
  everyday dilemmas (Study 3). Chi-square test of independence.
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
from scipy.stats import ttest_rel, chi2_contingency

EXPERIMENTS = ["exp0", "exp1", "exp2"]

FRAMING_MAP = {
    "Endow": "cbr", "Ladder": "cbr", "Lifeboat": "cbr",
    "Medicine": "rule", "Operations": "cbr", "RAF": "rule",
    "Ransom": "rule", "RobinHood": "cbr", "Rwanda": "rule",
    "Suicide": "cbr", "Tax": "cbr", "Tyran": "cbr", "Vet": "rule",
}

YES = {1}  # response coding: 1 = yes, 0 = no


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _to_binary(response: pd.Series) -> pd.Series:
    return response.isin(YES).astype(int)


def check_omission_bias_study1(data: dict[str, pd.DataFrame]) -> dict:
    df = data["exp0"]
    md = df[df["dilemma_type"] == "moral_dilemma"].copy()
    md["framing"] = md["dilemma"].map(FRAMING_MAP)
    md["cbr_choice"] = md["response"]
    md.loc[md["framing"] == "rule", "cbr_choice"] = 1 - md.loc[md["framing"] == "rule", "cbr_choice"]

    pivot = md.pivot_table(index="participant_id", columns="framing", values="cbr_choice", aggfunc="mean")
    t_stat, p_val = ttest_rel(pivot["cbr"], pivot["rule"])
    d = pivot["rule"].mean() - pivot["cbr"].mean()
    n = len(pivot)
    cohens_d = t_stat / np.sqrt(n)
    return {
        "effect_name": "omission_bias_study1",
        "experiment": "exp0",
        "original_effect_size": 0.053,
        "effect_size": round(d, 4),
        "statistic": float(t_stat),
        "p_value": float(p_val),
        "cohens_d": float(cohens_d),
        "reproduced": bool(p_val < 0.05 and d > 0),
    }


def check_framing_effect_study2(data: dict[str, pd.DataFrame]) -> dict:
    df = data["exp1"].copy()
    df["choice"] = _to_binary(df["response"])
    df = df[df["choice"].isin([0, 1])]
    ct = pd.crosstab(df["framing"], df["choice"])
    chi2, p_val, dof, expected = chi2_contingency(ct)
    n = ct.values.sum()
    cramer_v = np.sqrt(chi2 / (n * min(ct.shape) - 1)) if n > 0 else 0.0
    return {
        "effect_name": "framing_effect_study2",
        "experiment": "exp1",
        "original_effect_size": 0.150,
        "effect_size": round(float(cramer_v), 4),
        "statistic": float(chi2),
        "p_value": float(p_val),
        "reproduced": bool(p_val < 0.05),
    }


def check_framing_effect_study3(data: dict[str, pd.DataFrame]) -> dict:
    df = data["exp2"].copy()
    df["choice"] = _to_binary(df["response"])
    df = df[df["choice"].isin([0, 1])]
    ct = pd.crosstab(df["framing"], df["choice"])
    chi2, p_val, dof, expected = chi2_contingency(ct)
    n = ct.values.sum()
    cramer_v = np.sqrt(chi2 / (n * min(ct.shape) - 1)) if n > 0 else 0.0
    return {
        "effect_name": "framing_effect_study3",
        "experiment": "exp2",
        "original_effect_size": 0.250,
        "effect_size": round(float(cramer_v), 4),
        "statistic": float(chi2),
        "p_value": float(p_val),
        "reproduced": bool(p_val < 0.05),
    }


EFFECTS = [check_omission_bias_study1, check_framing_effect_study2, check_framing_effect_study3]


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
            print(f"{exp}: (default \u2014 local ./{exp}.csv)")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<4}  {'p_value':>8}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['p_value']:>8.4f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()