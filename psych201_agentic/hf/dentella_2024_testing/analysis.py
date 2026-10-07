# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Dentella et al. (2024), "Testing AI on language
comprehension tasks reveals insensitivity to underlying meaning", Scientific Reports 14:28083.

Effects tested:
- human_accuracy_above_chance (exp0, exp1): per-participant mean comprehension accuracy
  is tested against chance (0.5) with a one-sample t-test; the paper's RQ1 claim is that
  humans reply accurately (intercept beta = 3.270, z = 16.190, P < .001). Expected: mean
  > 0.5 with p < .05.
- human_stability_above_chance (exp0, exp1): per-participant mean stability (all three
  replies to an item identical) tested against random (0.5) with a one-sample t-test; the
  paper's RQ2 claim is that humans give stable answers (intercept beta = 2.286, z = 17.368,
  P < .001). Expected: mean > 0.5 with p < .05.
- no_setting_effect_humans (exp0 vs exp1): human accuracy and stability do not differ
  between the one-word (exp0) and open-length (exp1) settings (accuracy beta = -0.228,
  P = .118; stability beta = -0.038, P = .717). Reproduced if the setting difference is
  not significant (p >= .05) on both metrics.
"""
from __future__ import annotations

import argparse
import pandas as pd
import numpy as np
from scipy import stats

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides, loads
    ./{exp}.csv from CWD.

    Required columns per experiment:
      exp0: participant_id, trial, response, correct, stability, attention_check
      exp1: participant_id, trial, response, correct, stability, attention_check
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _per_participant(df: pd.DataFrame, col: str) -> pd.Series:
    """Mean of `col` per participant across items, excluding attention checks."""
    d = df[df["attention_check"] == 0]
    if col == "stability":
        d = d[d[col].notna()]
    return d.groupby("participant_id")[col].mean()


def check_human_accuracy_above_chance(data: dict[str, pd.DataFrame]) -> dict:
    """\"...we tested 400 humans on the same prompts... LLMs perform at chance accuracy...
    humans... provide mostly accurate answers (RQ1)\" — the human accuracy intercept is
    beta = 3.270, z = 16.190, P < .001 (Dentella et al. 2024, p.4, 'LLMs vs humans')."""
    means = [_per_participant(data["exp0"], "correct").mean(),
             _per_participant(data["exp1"], "correct").mean()]
    zs, ps = [], []
    ds = []
    for e in EXPERIMENTS:
        m = _per_participant(data[e], "correct")
        t, p = stats.ttest_1samp(m, 0.5)
        zs.append(t)
        ps.append(p)
        ds.append(m.mean() / m.std(ddof=1))
    reproduced = (mean(means) > 0.5) and all(p < 0.05 for p in ps)
    return {
        "effect_name": "human_accuracy_above_chance",
        "experiment": "exp0, exp1 (pooled)",
        "original_effect_size": 3.270,  # paper's human accuracy intercept beta (open setting)
        "effect_size": float(mean(means)),
        "zs": [round(float(z), 2) for z in zs],
        "ps": [round(float(p), 5) for p in ps],
        "reproduced": bool(reproduced),
    }


def check_human_stability_above_chance(data: dict[str, pd.DataFrame]) -> dict:
    """\"...humans tested on the same comprehension questions provide mostly accurate
    answers (RQ1) which almost never change when a question is repeatedly prompted (RQ2)\"
    — the human stability intercept is beta = 2.286, z = 17.368, P < .001
    (Dentella et al. 2024, p.4, 'Llms vs humans')."""
    means = [_per_participant(data["exp0"], "stability").mean(),
             _per_participant(data["exp1"], "stability").mean()]
    ps = []
    for e in EXPERIMENTS:
        m = _per_participant(data[e], "stability")
        t, p = stats.ttest_1samp(m, 0.5)
        ps.append(p)
    reproduced = (mean(means) > 0.5) and all(p < 0.05 for p in ps)
    return {
        "effect_name": "human_stability_above_chance",
        "experiment": "exp0, exp1 (pooled)",
        "original_effect_size": 2.286,  # paper's human stability intercept beta (open setting)
        "effect_size": float(mean(means)),
        "ps": [round(float(p), 5) for p in ps],
        "reproduced": bool(reproduced),
    }


def check_no_setting_effect_humans(data: dict[str, pd.DataFrame]) -> dict:
    """\"...humans do not perform better in the one-word setting as opposed to the
    open-length setting (beta = -0.228, z = -1.561, P = .118)... humans are not less
    stable in the open-length setting compared to the one-word setting (beta = -0.038,
    z = -0.362, P = .717)\" — Dentella et al. 2024, p.4, 'LLMs vs humans'."""
    a0 = _per_participant(data["exp0"], "correct")
    a1 = _per_participant(data["exp1"], "correct")
    s0 = _per_participant(data["exp0"], "stability")
    s1 = _per_participant(data["exp1"], "stability")
    ta, pa = stats.ttest_ind(a0, a1)
    ts, ps = stats.ttest_ind(s0, s1)
    reproduced = bool(pa >= 0.05 and ps >= 0.05)
    return {
        "effect_name": "no_setting_effect_humans",
        "experiment": "exp0 vs exp1",
        "original_effect_size": -0.228,  # paper's setting effect on human accuracy (beta)
        "effect_size": float(a1.mean() - a0.mean()),
        "acc_p": round(float(pa), 5),
        "stab_p": round(float(ps), 5),
        "reproduced": reproduced,
    }


def mean(xs):
    return float(np.mean(list(xs)))


EFFECTS = [
    check_human_accuracy_above_chance,
    check_human_stability_above_chance,
    check_no_setting_effect_humans,
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
            print(f"{exp}: (default — local ./{exp}.csv)")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<16}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
