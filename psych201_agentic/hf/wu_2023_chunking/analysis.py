# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Wu et al. (2023), "Chunking as a rational
solution to the speed-accuracy trade-off in a serial reaction time task", Sci Rep 13:7680,
against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- exp2_speed_accuracy_tradeoff (exp1): In the training blocks of Experiment 2, the group
  instructed to act fast must respond significantly faster (lower mean RT) while also being
  significantly less accurate (lower mean correctness) than the group instructed to act
  accurately. This is the paper's behavioral demonstration of the speed-accuracy trade-off
  and its manipulation check that instructions shifted performance (two independent
  independent-samples t-tests, both expected significant and in the stated directions).

NOTE: The paper's other headline chunking metrics (chunky boost, chunkiness, chunk increase,
reaction-time regression) depend on a mixture-of-Gaussians within/between-chunk RT
classification and Wasserstein-distance computations that are not derivable faithfully from
the raw columns alone, so they are not checked here.
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
      exp0: participant_id, trial, response, rt, correct, condition, phase, ...
      exp1: participant_id, trial, response, rt, correct, condition, phase, ...
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_exp2_speed_accuracy_tradeoff(data: dict[str, pd.DataFrame]) -> dict:
    """"Fitting a linear mixed-effects regression onto participants' reaction times ...
    showed a significant effect of group (chi^2(1)=9.84, p=.002), showing that participants
    in the fast group responded faster during the training blocks than participants in the
    accurate group (beta-hat=81.71, t=3.19, p=.0001). We also fitted a mixed-effects logistic
    regression of group ... showing a significant effect of group ..., with participants in the
    accurate group responding on average more accurately during the training blocks than
    participants in the fast group (beta-hat=0.54, z=3.18, p=.001)."
    -- Wu et al. 2023, p.11, "Experiment 2: Manipulation check".

    In the transformed data condition==0 is the "fast" group and condition==1 is the
    "accurate" group (matches the description in columns.md).
    """
    df = data["exp1"]
    tr = df[df["phase"] == "training"]
    subj = (
        tr.groupby(["participant_id", "condition"])
        .agg(rt=("rt", "mean"), acc=("correct", "mean"))
        .reset_index()
    )
    fast = subj[subj["condition"] == 0]
    accurate = subj[subj["condition"] == 1]

    rt_t, rt_p = stats.ttest_ind(fast["rt"], accurate["rt"])
    acc_t, acc_p = stats.ttest_ind(fast["acc"], accurate["acc"])

    rt_diff = accurate["rt"].mean() - fast["rt"].mean()   # > 0 -> fast is faster
    acc_diff = accurate["acc"].mean() - fast["acc"].mean()  # > 0 -> fast is less accurate

    rt_reproduced = rt_diff > 0 and rt_p < 0.05
    acc_reproduced = acc_diff > 0 and acc_p < 0.05
    reproduced = bool(rt_reproduced and acc_reproduced)

    return {
        "effect_name": "exp2_speed_accuracy_tradeoff",
        "experiment": "exp1",
        "original_effect_size": float(81.71),   # RT beta for fast-vs-accurate (paper)
        "effect_size": float(rt_diff),           # accurate RT - fast RT (ms), this dataset
        "reproduced": reproduced,
        "rt_diff_ms": float(rt_diff),
        "rt_p": float(rt_p),
        "acc_diff": float(acc_diff),
        "acc_p": float(acc_p),
        "n_fast": int(len(fast)),
        "n_accurate": int(len(accurate)),
    }


EFFECTS = [check_exp2_speed_accuracy_tradeoff]


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
        print(f"{exp}: {sources[exp]}" if exp in sources else f"{exp}: (default -- local ./{exp}.csv)")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")
        for k in ("rt_diff_ms", "rt_p", "acc_diff", "acc_p"):
            if k in r:
                print(f"    {k}: {r[k]:.4f}")


if __name__ == "__main__":
    main()