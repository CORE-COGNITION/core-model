# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Günther & Marelli (2020), "Trying to make it
work: Compositional effects in the processing of compound 'nonwords'", QJEP, against any
dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- modifier_composition_exp0 (exp0): in the timed-sensibility task, participants'
  log rejection RT increases with modifier composition (simuco); mixed-model coefficient
  positive, significant.
- modifier_composition_exp1 (exp1): in the lexical-decision task, participants' log
  rejection RT increases with modifier composition (simuco); mixed-model coefficient
  positive, significant.
- no_task_difference (combined): the modifier-composition effect does not differ reliably
  between tasks; the Experiment x modifier-composition interaction is not significant.
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

EXPERIMENTS = ["exp0", "exp1"]


def _rejections(df: pd.DataFrame) -> pd.DataFrame:
    """Rejection ('No'/nonword) trials, with RT outliers removed as in the paper
    (<100 ms or >5000 ms excluded)."""
    d = df[(df["correct"] == 1) & (df["rt"] > 100) & (df["rt"] < 5000)].copy()
    d["logrt"] = np.log(d["rt"])
    d["pid"] = d["participant_id"].astype(str)
    return d


def _simuco_model(d: pd.DataFrame) -> object:
    """Mixed model: log(rejection RT) ~ modifier composition (simuco), with random
    intercepts for participants (mirrors the paper's LME analyses)."""
    return smf.mixedlm("logrt ~ simuco", data=d, groups=d["pid"]).fit()


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns per experiment:
      exp0: participant_id, trial, response, rt, correct, simuco
      exp1: participant_id, trial, response, rt, correct, simuco
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_modifier_composition_exp0(data: dict[str, pd.DataFrame]) -> dict:
    """"All parameter values are positive, so higher values predict longer rejection
    times." — Günther & Marelli 2020, Experiment 1, Results (modifier composition
    b = 0.05, t = 3.09, p = .002)."""
    d = _rejections(data["exp0"])
    m = _simuco_model(d)
    b = float(m.params["simuco"])
    p = float(m.pvalues["simuco"])
    reproduced = bool(b > 0 and p < 0.05)
    return {
        "effect_name": "modifier_composition_exp0",
        "experiment": "exp0",
        "original_effect_size": 0.05,
        "effect_size": b,
        "p_value": p,
        "reproduced": reproduced,
    }


def check_modifier_composition_exp1(data: dict[str, pd.DataFrame]) -> dict:
    """"Again, the parameter is positive, and therefore higher values predict longer
    rejection times." — Günther & Marelli 2020, Experiment 2, Results (modifier
    composition b = 0.06, t = 3.62, p < .001)."""
    d = _rejections(data["exp1"])
    m = _simuco_model(d)
    b = float(m.params["simuco"])
    p = float(m.pvalues["simuco"])
    reproduced = bool(b > 0 and p < 0.05)
    return {
        "effect_name": "modifier_composition_exp1",
        "experiment": "exp1",
        "original_effect_size": 0.06,
        "effect_size": b,
        "p_value": p,
        "reproduced": reproduced,
    }


def check_no_task_difference(data: dict[str, pd.DataFrame]) -> dict:
    """"Adding an interaction parameter between Experiment and modifier composition does
    not improve this model (χ2 (1) = 1.38, p = .240) ... Thus, the final model contained
    only a task-independent main effect for modifier composition." — Günther & Marelli
    2020, Task-Interaction Analysis."""
    parts = []
    for exp, dd in data.items():
        d = _rejections(dd)
        d["exp"] = float(exp == "exp1")
        d["pid"] = d["participant_id"].astype(str) + "_" + exp
        parts.append(d)
    all_df = pd.concat(parts)
    m = smf.mixedlm(
        "logrt ~ simuco + exp + exp:simuco", data=all_df, groups=all_df["pid"]
    ).fit()
    b = float(m.params["exp:simuco"])
    p = float(m.pvalues["exp:simuco"])
    reproduced = bool(p > 0.05)
    return {
        "effect_name": "no_task_difference",
        "experiment": "exp0+exp1",
        "original_effect_size": float(p),
        "effect_size": p,
        "interaction_beta": b,
        "reproduced": reproduced,
    }


EFFECTS = [
    check_modifier_composition_exp0,
    check_modifier_composition_exp1,
    check_no_task_difference,
]


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
    print(f"{'effect':<{w}}  {'exp':<10}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<10}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
