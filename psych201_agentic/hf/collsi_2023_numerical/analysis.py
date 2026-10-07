# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Collsiöö, Juslin, & Winman (2023,
"Is numerical information always beneficial? Verbal and numerical cue-integration
in additive and non-additive tasks", Cognition 240, 105584) against any dataset
in the Psych-301 unified schema (see schema.md).

Judgment learning task: participants estimate a criterion (Caldionine) from two
cues over 10 (Exp3: 6) training blocks plus a test phase, responding on a 9-step
rating scale. Performance is indexed by per-participant RMSE between the numeric
response and the true criterion; we replicate the paper's outlier-removal rule
(participants with RMSE > Q3 + 1.5*IQR within a cell are dropped, as in the
paper's footnotes 2/11).

Effects tested:
- format_task_crossover_exp1 (exp0): Exp1 headline — the predicted format-by-task
  crossover interaction in learning. 2x2 ANOVA on training-phase per-participant
  RMSE (and confirmatory check on the test phase): a numeric format is
  advantageous in additive but detrimental in non-additive tasks, i.e. RMSE is
  lower for numeric than verbal in the additive task and lower for verbal than
  numeric in the non-additive task; interaction significant.
- nonadditive_worse_than_additive_exp2 (exp1): Exp2 — main effect of task at
  test: RMSE is higher (performance worse) in the non-additive than the additive
  task.
- verbal_benefits_nonadditive_exp3 (exp2): Exp3 — in the non-additive task, a
  verbal format produces lower RMSE during training than a numerical format,
  replicating the verbal benefit in non-additive tasks.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

EXPERIMENTS = ["exp0", "exp1", "exp2"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, condition, phase, block, response, criterium_numeric
      exp1: participant_id, condition, phase, block, response, criterium_numeric
      exp2: participant_id, condition, phase, block, response, criterium
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _crit_col(df: pd.DataFrame) -> str:
    return "criterium_numeric" if "criterium_numeric" in df.columns else "criterium"


def _per_participant_rmse(df: pd.DataFrame) -> pd.DataFrame:
    """Per-participant mean RMSE of response vs. criterion, with condition label."""
    d = df.dropna(subset=["response", _crit_col(df)]).copy()
    d["se"] = (d["response"] - d[_crit_col(d)]) ** 2
    rmse = np.sqrt(d.groupby("participant_id")["se"].mean())
    cond = d.groupby("participant_id")["condition"].first()
    return pd.DataFrame({"rmse": rmse, "condition": cond}).reset_index()


def _drop_upper_outliers(per: pd.DataFrame) -> pd.DataFrame:
    """Paper's rule (fn 2/11): drop participants with RMSE > Q3 + 1.5*IQR,
    computed within each experimental cell."""
    keep = np.zeros(len(per), dtype=bool)
    for cond, g in per.groupby("condition"):
        s = g["rmse"].values
        q1, q3 = np.percentile(s, [25, 75])
        hi = q3 + 1.5 * (q3 - q1)
        keep |= (per["condition"] == cond) & (per["rmse"] <= hi)
    return per[keep]


def _task(cond: str) -> str:
    return "nonadditive" if "nonadditive" in cond else "additive"


def _format(cond: str) -> str:
    return "numeric" if "numeric" in cond else "verbal"


def check_format_task_crossover_exp1(data: dict[str, pd.DataFrame]) -> dict:
    """\"This predicts that, relative to a verbal format, a numerical format should
    be advantageous for learning in additive tasks, but detrimental for learning
    in non-additive tasks.\" — Collsiöö et al. 2023, Abstract & §2.2.1 (training
    interaction), test-phase interaction in §2.2.2. Interaction size D = (verbal_add
    - numeric_add) - (verbal_na - numeric_na), positive => predicted crossover."""
    df = data["exp0"]
    p_inters, dps = [], []
    for phase in ["training", "test"]:
        per = _per_participant_rmse(df[df.phase == phase])
        per = _drop_upper_outliers(per)
        per = per.copy()
        per["task"] = per["condition"].map(_task)
        per["format"] = per["condition"].map(_format)
        m = smf.ols("rmse ~ C(format) * C(task)", data=per).fit()
        inter = [n for n in m.params.index if "C(format)" in n and "C(task)" in n]
        p_inter = m.pvalues[inter[0]]
        v_a = per[(per.format == "verbal") & (per.task == "additive")].rmse.mean()
        n_a = per[(per.format == "numeric") & (per.task == "additive")].rmse.mean()
        v_n = per[(per.format == "verbal") & (per.task == "nonadditive")].rmse.mean()
        n_n = per[(per.format == "numeric") & (per.task == "nonadditive")].rmse.mean()
        p_inters.append(p_inter)
        dps.append((v_a - n_a) - (v_n - n_n))
    # Paper's implied D from the §2.2.1 training means (8.753, 5.650, 14.412, 16.885)
    original = (8.753 - 5.650) - (14.412 - 16.885)
    directions_ok = all(dp > 0 for dp in dps) and dps[1] > 0
    reproduced = bool(p_inters[0] < 0.05 and directions_ok)
    return {
        "effect_name": "format_task_crossover_exp1",
        "experiment": "exp0",
        "original_effect_size": original,
        "effect_size": dps[0],
        "training_interaction_p": p_inters[0],
        "test_interaction_p": p_inters[1],
        "reproduced": reproduced,
    }


def check_nonadditive_worse_than_additive_exp2(data: dict[str, pd.DataFrame]) -> dict:
    """\"The support for a main effect of task is the standard finding that people
    find it more difficult to learn non-additive than additive tasks ... better
    performance in the additive task (M = 3.416, SD = 3.756) than in the
    non-additive task (M = 13.499, SD = 7.424)\" — Collsiöö et al. 2023, §3.2.2."""
    per = _per_participant_rmse(data["exp1"][data["exp1"].phase == "test"])
    per = _drop_upper_outliers(per)
    per = per.copy()
    per["task"] = per["condition"].map(_task)
    add = per.loc[per.task == "additive", "rmse"]
    na = per.loc[per.task == "nonadditive", "rmse"]
    t, p = stats.ttest_ind(add, na, equal_var=False)
    reproduced = bool(na.mean() > add.mean() and p < 0.05)
    return {
        "effect_name": "nonadditive_worse_than_additive_exp2",
        "experiment": "exp1",
        "original_effect_size": 13.499 - 3.416,
        "effect_size": na.mean() - add.mean(),
        "t": float(t),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_verbal_benefits_nonadditive_exp3(data: dict[str, pd.DataFrame]) -> dict:
    """\"The quicker learning of a non-additive task with a verbal (M = 16.665, SD
    = 6.383) rather than numerical (M = 19.639, SD = 5.447) format ... replicates
    the result in Experiment 1 for an all-verbal format.\" — Collsiöö et al. 2023,
    §4.2 (Exp3 training, non-additive task)."""
    per = _per_participant_rmse(data["exp2"])
    per = _drop_upper_outliers(per)
    verbal = per.loc[per.condition == "verbal", "rmse"]
    numeric = per.loc[per.condition == "numerical", "rmse"]
    t, p = stats.ttest_ind(verbal, numeric, equal_var=False)
    reproduced = bool(verbal.mean() < numeric.mean() and p < 0.05)
    return {
        "effect_name": "verbal_benefits_nonadditive_exp3",
        "experiment": "exp2",
        "original_effect_size": 19.639 - 16.665,
        "effect_size": numeric.mean() - verbal.mean(),
        "t": float(t),
        "p": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_format_task_crossover_exp1,
    check_nonadditive_worse_than_additive_exp2,
    check_verbal_benefits_nonadditive_exp3,
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