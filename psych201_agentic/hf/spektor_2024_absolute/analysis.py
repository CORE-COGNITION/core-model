# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Spektor, Kellen, Rieskamp, & Klauer (2023),
"Absolute and relative stability of loss aversion across contexts", JEP:G, against any
dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- context_effect_risky_choice (exp1, Experiment 2): participants choose the riskier option
  less often in the loss-aversion condition (LAC) than in the gain-seeking condition (GSC);
  within-subject paired t-test, expected sign GSC-LAC > 0, p<.05.
- stability_risky_choice (exp1, Experiment 2): the proportion of risky choices across the
  LAC and GSC conditions is positively correlated across participants (r>0, p<.05),
  indicating stable relative individual differences.
- context_effect_risky_choice_exp3 (exp2, Experiment 3): preregistered replication of the
  within-subject context effect on risky-choice proportions (LAC < GSC), paired t-test p<.05.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1", "exp2"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp1: participant_id, trial, response, condition, valid (and: riskychoice)
      exp2: participant_id, trial, response, condition, valid (and: rsp_risky)
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _risky_props(df: pd.DataFrame, risky_col: str) -> pd.DataFrame:
    d = df[df["valid"] == 1].copy()
    col = d[risky_col]
    if pd.api.types.is_string_dtype(col.dtype) and not pd.api.types.is_bool_dtype(col.dtype):
        risky = col.astype(str).str.lower() == "risky"
    else:
        risky = col.astype(float).astype(bool)
    d["risky"] = risky
    piv = d.pivot_table(index="participant_id", columns="condition", values="risky", aggfunc="mean")
    return piv[["gain_seeking", "loss_aversion"]].dropna()


def check_context_effect_risky_choice(data: dict[str, pd.DataFrame]) -> dict:
    """"individuals in the LAC were less likely to choose the riskier option (M=.553) than
    in the GSC (M=.622), t(184)=2.655, p=.009, d_z=0.195" — Spektor et al. 2023, p.7, Exp2
    Method & Results (global across starting conditions)."""
    piv = _risky_props(data["exp1"], "riskychoice")
    t, p = stats.ttest_rel(piv["gain_seeking"], piv["loss_aversion"])
    effect_size = float(np.mean(piv["gain_seeking"]) - np.mean(piv["loss_aversion"]))
    reproduced = bool((effect_size > 0) and (p < 0.05))
    return {
        "effect_name": "context_effect_risky_choice",
        "experiment": "exp1",
        "original_effect_size": 0.195,
        "effect_size": effect_size,
        "p": float(p),
        "reproduced": reproduced,
    }


def check_stability_risky_choice(data: dict[str, pd.DataFrame]) -> dict:
    """"individual choice proportions were found to be correlated across contexts ... r(184)=.513
    (95% CI:[.399.612]), p<.001" — Spektor et al. 2023, p.7, Exp2 Method & Results."""
    piv = _risky_props(data["exp1"], "riskychoice")
    r, p = stats.pearsonr(piv["gain_seeking"], piv["loss_aversion"])
    reproduced = bool((r > 0) and (p < 0.05))
    return {
        "effect_name": "stability_risky_choice",
        "experiment": "exp1",
        "original_effect_size": 0.513,
        "effect_size": float(r),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_context_effect_risky_choice_exp3(data: dict[str, pd.DataFrame]) -> dict:
    """"people in the LAC were less likely to choose the riskier mean-preserving spreads
    (M=.340, SD=.327) than in the GSC (M=.391, SD=.341), t(56)=2.314, p=.024, d_z=0.307"
    — Spektor et al. 2023, p.9, Exp3 Method & Results (within-subject across starting conditions)."""
    piv = _risky_props(data["exp2"], "rsp_risky")
    t, p = stats.ttest_rel(piv["gain_seeking"], piv["loss_aversion"])
    effect_size = float(np.mean(piv["gain_seeking"]) - np.mean(piv["loss_aversion"]))
    reproduced = bool((effect_size > 0) and (p < 0.05))
    return {
        "effect_name": "context_effect_risky_choice_exp3",
        "experiment": "exp2",
        "original_effect_size": 0.307,
        "effect_size": effect_size,
        "p": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_context_effect_risky_choice,
    check_stability_risky_choice,
    check_context_effect_risky_choice_exp3,
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
