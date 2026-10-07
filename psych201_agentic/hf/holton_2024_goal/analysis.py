# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Holton et al. (2024), "Goal commitment
is supported by vmPFC through selective attention", Nature Human Behaviour 8,
1351-1365, against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested (all from the healthy fMRI study, exp0, the incremental
goal-pursuit 'fishing-net' decision task):
- goal_commitment_bias (exp0): participants overpersist with the current goal —
  the probability of abandoning is below 0.5 at the model's indifference point
  (tree-search switch value = 0). Logistic regression of abandonment on the
  tree-search switch value; expected P(abandon) < 0.5 at switch value = 0.
- persistence_increases_with_progress (exp0): the more of the net already filled
  (goal progress), the less likely participants are to abandon the goal.
  Logistic regression of abandonment on proportion-of-net-completed; expected
  negative coefficient (p < .05).
- alternative_discounts_with_progress (exp0): over the course of goal pursuit,
  sensitivity to the value of attractive alternatives ('temptation') fades more
  rapidly than sensitivity to the value of the current goal ('frustration').
  Logistic regression of abandonment on current-goal value x progress and
  best-alternative value x progress; expected alternative*xprogress slope
  (negative) well below current*xprogress slope.

The lesion study (exp1) headline effect concerns a vmPFC-damaged patient
subgroup whose membership is not recoverable from the CSV (no lesion-location
column), so it is not included here.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
import statsmodels.api as sm

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD -- cd into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, task_id, trial, response, prop_filled, switch_trial,
            prosp_switch_value_3, mag_goal_item, mag_best_alt
      exp1: participant_id, condition, trial, response, switch_trial
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _decision_trials(df: pd.DataFrame) -> pd.DataFrame:
    """Non-edge decision rows: exclude the very first trial of a goal, where the
    participant has no choice about persisting, and require real progress > 0."""
    return df[(df["prop_filled"] > 0) & (df["trial"] >= 1)].copy()


def check_goal_commitment_bias(data: dict[str, pd.DataFrame]) -> dict:
    """"Participants showed a universal 'goal commitment' bias towards persisting
    with their current goal... green dots indicate indifference to abandonment"
    (Holton et al. 2024, p.1353, Decision task)."""
    df = _decision_trials(data["exp0"]).dropna(subset=["prosp_switch_value_3"]).copy()
    X = sm.add_constant(df["prosp_switch_value_3"])
    m = sm.Logit(df["switch_trial"], X).fit(disp=0)
    b, c = float(m.params.iloc[1]), float(m.params.iloc[0])
    p_abandon_0 = 1.0 / (1.0 + np.exp(-(c + b * 0.0)))
    original_effect_size = 0.5
    reproduced = bool(p_abandon_0 < 0.5)
    return {
        "effect_name": "goal_commitment_bias",
        "experiment": "exp0",
        "original_effect_size": 0.5,
        "effect_size": float(p_abandon_0),
        "reproduced": reproduced,
        "n_trials": int(len(df)),
        "p_abandon_at_indifference": float(p_abandon_0),
    }


def check_persistence_increases_with_progress(data: dict[str, pd.DataFrame]) -> dict:
    """"Compared with the optimal model, people were more reluctant to abandon
    their goal the more progress they made towards finishing (main effect of
    proportion of net completed... X2(1, N=30) = 5.27, P = 0.022)"
    (Holton et al. 2024, p.1353, Decision task)."""
    df = _decision_trials(data["exp0"]).dropna(subset=["prop_filled"]).copy()
    df["sw"] = df["switch_trial"]
    X = sm.add_constant(df["prop_filled"])
    m = sm.Logit(df["sw"], X).fit(disp=0)
    beta = float(m.params.iloc[1])
    pval = float(m.pvalues.iloc[1])
    reproduced = bool(beta < 0 and pval < 0.05)
    return {
        "effect_name": "persistence_increases_with_progress",
        "experiment": "exp0",
        "original_effect_size": -1.0,
        "effect_size": beta,
        "reproduced": reproduced,
        "n_trials": int(len(df)),
        "p": pval,
    }


def check_alternative_discounts_with_progress(data: dict[str, pd.DataFrame]) -> dict:
    """"over the course of goal pursuit, the impact of temptation from
    alternatives fades more rapidly than the impact of frustration with the
    current goal" (Holton et al. 2024, p.1354, Goal abandonment due to
    'temptation' versus 'frustration')."""
    df = _decision_trials(data["exp0"]).dropna(
        subset=["mag_goal_item", "mag_best_alt", "prop_filled"]
    ).copy()
    df["sw"] = df["switch_trial"]
    df["cur"] = df["mag_goal_item"]
    df["alt"] = df["mag_best_alt"]
    df["prog"] = df["prop_filled"]
    df["curp"] = df["cur"] * df["prog"]
    df["altp"] = df["alt"] * df["prog"]
    X = sm.add_constant(df[["cur", "alt", "prog", "curp", "altp"]])
    m = sm.Logit(df["sw"], X).fit(disp=0)
    alt_slope = float(m.params["altp"])
    cur_slope = float(m.params["curp"])
    reproduced = bool(alt_slope - cur_slope < 0 and alt_slope < 0)
    return {
        "effect_name": "alternative_discounts_with_progress",
        "experiment": "exp0",
        "original_effect_size": -4.0,
        "effect_size": float(alt_slope - cur_slope),
        "reproduced": reproduced,
        "n_trials": int(len(df)),
        "alt_vs_cur_slope_diff": float(alt_slope - cur_slope),
    }


EFFECTS = [
    check_goal_commitment_bias,
    check_persistence_increases_with_progress,
    check_alternative_discounts_with_progress,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing."""
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
            print(f"{exp}: (default -- local ./{exp}.csv)")
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