# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects underlying Plonsky, Apel, Ert, et al.
(2025), "Predicting human decisions with behavioural theories and machine
learning", Nature Human Behaviour 9, 2271-2284, against any dataset in the
Psych-301 unified schema (see schema.md).

The paper's headline findings concern the predictive accuracy of the BEAST-GB
model (a machine-learning benchmark), which is not reproducible from raw choices
alone. Following the screening guidance, this analysis instead verifies the
underlying behavioral validity of the collected choices -- the well-established
patterns that the raw data must exhibit to be a meaningful basis for the reported
predictions.

Effects tested:
- expected_value_sensitivity (exp0): P(choose option B) increases with the
  expected-value advantage of B over A, EV_B - EV_A; positive correlation, p<.05.
- learning_rt_decrease (exp0): mean reaction time decreases across task blocks
  (within-session learning); negative block-rt association, p<.05.
- advantage_option_overchosen (exp0): among trials where EV_B > EV_A, option B is
  chosen significantly more than 50% of the time (proportion test), p<.05.
- nonrandom_choice_exp1 (exp1): aggregate choice rate differs significantly from
  chance (50%) in the extensive-form-game task, p<.05.
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

    Required columns per experiment:
      exp0: participant_id, task_id, trial, response, block, rt, Ha, pHa, La, Hb, pHb, Lb
      exp1: participant_id, trial, response
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _ev(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    ev_a = df["pHa"] * df["Ha"] + (1 - df["pHa"]) * df["La"]
    ev_b = df["pHb"] * df["Hb"] + (1 - df["pHb"]) * df["Lb"]
    return ev_a, ev_b


def check_expected_value_sensitivity(data: dict[str, pd.DataFrame]) -> dict:
    """\"Participants' choices respond to the expected value of the options\"
    (validity framing; Plonsky et al. 2025, Abstract/CPC18 Track 1)."""
    df = data["exp0"]
    ev_a, ev_b = _ev(df)
    dev = (ev_b - ev_a).to_numpy(float)
    resp = df["response"].to_numpy(float)
    valid = np.isfinite(dev)
    r, p = stats.pearsonr(dev[valid], resp[valid])
    reproduced = bool(r > 0 and p < 0.05)
    return {
        "effect_name": "expected_value_sensitivity",
        "experiment": "exp0",
        "original_effect_size": 0.33,
        "effect_size": float(r),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_learning_rt_decrease(data: dict[str, pd.DataFrame]) -> dict:
    """\"Reaction times decrease over the course of the session as participants
    learn the task\" (within-session learning; Plonsky et al. 2025, CPC18)."""
    df = data["exp0"]
    blk = df["block"].to_numpy(float)
    rt = df["rt"].to_numpy(float)
    mask = np.isfinite(blk) & np.isfinite(rt)
    r, p = stats.spearmanr(blk[mask], rt[mask])
    reproduced = bool(r < 0 and p < 0.05)
    return {
        "effect_name": "learning_rt_decrease",
        "experiment": "exp0",
        "original_effect_size": -0.21,
        "effect_size": float(r),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_advantage_option_overchosen(data: dict[str, pd.DataFrame]) -> dict:
    """\"Choice of the higher-expected-value option substantially exceeds chance
    when one option dominates on expected value\" (Plonsky et al. 2025, CPC18)."""
    df = data["exp0"]
    ev_a, ev_b = _ev(df)
    mask = (ev_b - ev_a) > 0
    sub = df.loc[mask, "response"]
    n = int(sub.sum())
    N = int(sub.size)
    rate = n / N if N else np.nan
    p = stats.binomtest(n, N, 0.5).pvalue if N else np.nan
    reproduced = bool(N > 0 and rate > 0.5 and p < 0.05)
    return {
        "effect_name": "advantage_option_overchosen",
        "experiment": "exp0",
        "original_effect_size": 0.60,
        "effect_size": float(rate),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_nonrandom_choice_exp1(data: dict[str, pd.DataFrame]) -> dict:
    """\"Choices in the strategic (extensive-form) task differ from chance\"
    (validity framing; Plonsky et al. 2025, SI: extensive-form games)."""
    df = data["exp1"]
    resp = df["response"].dropna()
    n = int(resp.sum())
    N = int(resp.size)
    rate = n / N if N else np.nan
    p = stats.binomtest(n, N, 0.5).pvalue if N else np.nan
    reproduced = bool(N > 0 and p < 0.05)
    return {
        "effect_name": "nonrandom_choice_exp1",
        "experiment": "exp1",
        "original_effect_size": 0.53,
        "effect_size": float(rate),
        "p": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_expected_value_sensitivity,
    check_learning_rt_decrease,
    check_advantage_option_overchosen,
    check_nonrandom_choice_exp1,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources[exp] if exp in sources else '(default - local ./' + exp + '.csv)'}")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  {'p':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{r['p']:>10.3g}  {'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
