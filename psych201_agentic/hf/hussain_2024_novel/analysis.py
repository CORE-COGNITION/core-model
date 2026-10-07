# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Hussain, Mata & Wulff (2024), "Novel
embeddings improve the prediction of risk perception", EPJ Data Science 13:38,
against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- psychometric_two_component_structure (exp1): PCA of the nine psychometric
  dimensions' item-means; the leading principal components account for the
  majority of variance and are dominated by the first component (PC1 > PC2,
  first two beyond 50%).
- dread_risk_relation (exp0 + exp1): the first principal component of the nine
  psychometric dimensions (oriented to risk, i.e. dread/fatal-related) correlates
  positively and significantly with the mean risk-perception rating per item.
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1"]

PSYCH_DIMS = [
    "voluntary_involuntary", "fatal", "immediate_delayed", "dread",
    "chronic_catastrophic", "controllable", "known_science",
    "known_individuals", "new_old",
]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Return {experiment: DataFrame}. Loads ./{exp}.csv from CWD by default or
    the --<exp> CLI override path.

    Required columns:
      exp0: participant_id, trial, response (risk rating -100..100), stimulus
      exp1: participant_id, trial, response (Likert 1..7), stimulus,
            psychometric_dimension
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _item_mean_psychometrics(df1: pd.DataFrame) -> pd.DataFrame:
    """Long exp1 -> item x dimension matrix of mean ratings (complete items only)."""
    p = (
        df1.dropna(subset=["response"])
        .groupby(["stimulus", "psychometric_dimension"])["response"]
        .mean()
        .unstack()
    )
    return p[p.notna().all(axis=1)]


def check_psychometric_two_component_structure(data: dict[str, pd.DataFrame]) -> dict:
    """\"consistent with previous findings, two components [...] accounted for the
    majority of the psychometric variance (almost 80%) [but this is] predominantly
    due to the first principal component\" - Hussain et al. 2024, p.3, Results sec 2.1."""
    df = data["exp1"]
    p = _item_mean_psychometrics(df)
    X = p.values
    Xc = X - X.mean(axis=0)
    _, s, _ = np.linalg.svd(Xc, full_matrices=False)
    var = s ** 2 / np.sum(s ** 2)
    pc1_ratio = float(var[0])
    two_ratio = float(var[0] + var[1])
    reproduced = bool(pc1_ratio > var[1] and two_ratio > 0.5)
    return {
        "effect_name": "psychometric_two_component_structure",
        "experiment": "exp1",
        "original_effect_size": 0.80,  # majority, "almost 80%", two components
        "effect_size": float(two_ratio),
        "pc1_variance_ratio": pc1_ratio,
        "reproduced": reproduced,
    }


def check_dread_risk_relation(data: dict[str, pd.DataFrame]) -> dict:
    """\"Next to a highly correlated first component (r=.82) ... related to risk
    perception\" - Hussain et al. 2024, p.4, Results sec 2.1 (the first component
    captures the dread/fatal dimensions: r, centered on a positive correlation
    between perceived riskiness and its dominant psychometric dimension)."""
    p = _item_mean_psychometrics(data["exp1"])
    risk = (
        data["exp0"].groupby("stimulus")["response"].mean()
        .reindex(p.index)
    )
    Xc = p.values - p.values.mean(axis=0)
    _, s, Vt = np.linalg.svd(Xc, full_matrices=False)
    pc1 = np.matmul(Xc, Vt[0])
    if np.corrcoef(pc1, risk.values)[0, 1] < 0:
        pc1 = -pc1
    r, pval = stats.pearsonr(pc1, risk.values)
    reproduced = bool(r > 0 and pval < 0.05)
    return {
        "effect_name": "dread_risk_relation",
        "experiment": "exp0+exp1",
        "original_effect_size": 0.82,
        "effect_size": float(r),
        "p": float(pval),
        "reproduced": reproduced,
    }


EFFECTS = [check_psychometric_two_component_structure, check_dread_risk_relation]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}")
    args = ap.parse_args()
    for exp in EXPERIMENTS:
        print(f"{exp}: {getattr(args, exp) or '(default - local ./'+exp+'.csv)'}")
    results = run_analysis({exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)})
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<8}  {'orig':>8}  {'this':>8}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<8}  "
              f"{r['original_effect_size']:>8.3f}  {r['effect_size']:>8.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()