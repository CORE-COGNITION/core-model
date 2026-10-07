# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Kool, Gershman, & Cushman (2017),
"Cost-Benefit Arbitration Between Multiple Reinforcement-Learning Systems"
(Psychological Science, 28(9), 1321-1333) against any dataset in the
Psych-301 unified schema (see schema.md).

The paper's headline claim is a cost-benefit arbitration account of
metacontrol: people deploy MORE model-based (planning) control on trials where
stakes are high (point multiplier 5 vs 1) — but ONLY when model-based control
actually confers a reward advantage (Exp1's novel two-step task). When
model-based control offers no accuracy advantage (Exp2's Daw two-step task),
the stake-size effect disappears.

Effects tested:
- exp1_arbitration_weight_stakes (exp0): model-fit arbitration weight w is
  greater on high- than low-stakes trials. Paired difference test; expect
  positive mean difference, p < .05.
- exp1_mb_component_stakes (exp0): behavioral model-based choice component is
  greater on high- than low-stakes trials. Paired difference test; expect
  positive mean difference, p < .05.
- exp2_no_stakes_effect (exp1): model-fit arbitration weight w does NOT differ
  between high- and low-stakes trials (null effect). Paired difference test;
  reproduced iff p >= .05 (and small direction).
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required per-subject columns: w_low, w_high, behavioral_mbcomponent_low,
    behavioral_mbcomponent_high (present on every row; take one per participant).
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _per_subject(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    return df[["participant_id"] + cols].drop_duplicates("participant_id").dropna()


def check_exp1_arbitration_weight_stakes(data: dict[str, pd.DataFrame]) -> dict:
    """"
    ...the degree of model-based control was significantly greater on
    high-stakes trials (mean w = .76) compared with low-stakes trials (mean
    w = .54), t(97) = 4.67, p < .001, Cohen's d = 0.47 (Fig. 3)."
    -- Kool et al., 2017, p.1325, Experiment 1 Results.
    """
    p = _per_subject(data["exp0"], ["w_low", "w_high"])
    t, pval = stats.ttest_rel(p["w_high"], p["w_low"])
    n = len(p)
    d = t / np.sqrt(n)
    reproduced = bool(d > 0 and pval < 0.05)
    return {
        "effect_name": "exp1_arbitration_weight_stakes",
        "experiment": "exp0",
        "original_effect_size": 0.47,
        "effect_size": float(d),
        "p_value": float(pval),
        "reproduced": reproduced,
    }


def check_exp1_mb_component_stakes(data: dict[str, pd.DataFrame]) -> dict:
    """"
    ...the model-based choice component ... was significantly higher on
    high-stakes trials than on low-stakes trials, t(97) = 3.70, p < .001,
    d = 0.37."
    -- Kool et al., 2017, p.1327, Experiment 1 Behavioral performance.
    """
    p = _per_subject(
        data["exp0"],
        ["behavioral_mbcomponent_low", "behavioral_mbcomponent_high"],
    )
    t, pval = stats.ttest_rel(p["behavioral_mbcomponent_high"], p["behavioral_mbcomponent_low"])
    n = len(p)
    d = t / np.sqrt(n)
    reproduced = bool(d > 0 and pval < 0.05)
    return {
        "effect_name": "exp1_mb_component_stakes",
        "experiment": "exp0",
        "original_effect_size": 0.37,
        "effect_size": float(d),
        "p_value": float(pval),
        "reproduced": reproduced,
    }


def check_exp2_no_stakes_effect(data: dict[str, pd.DataFrame]) -> dict:
    """"
    ...we observed no difference in model-based control in the high-stakes
    trials (mean w = .39) compared with the low-stakes trials (mean w = .41),
    t(99) = -0.38, p = .71, d = -0.04 (Fig. 3), in contrast with the increase
    in model-based control in Experiment 1."
    -- Kool et al., 2017, p.1330, Experiment 2 Results.
    """
    p = _per_subject(data["exp1"], ["w_low", "w_high"])
    t, pval = stats.ttest_rel(p["w_high"], p["w_low"])
    n = len(p)
    d = t / np.sqrt(n)
    reproduced = bool(pval >= 0.05)
    return {
        "effect_name": "exp2_no_stakes_effect",
        "experiment": "exp1",
        "original_effect_size": -0.04,
        "effect_size": float(d),
        "p_value": float(pval),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_exp1_arbitration_weight_stakes,
    check_exp1_mb_component_stakes,
    check_exp2_no_stakes_effect,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. Pure return."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources.get(exp, '(default - local ./' + exp + '.csv)')}")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  {'p':>8}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{r['p_value']:>8.4f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()