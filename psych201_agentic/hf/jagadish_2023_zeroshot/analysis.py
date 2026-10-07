# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Jagadish, Binz, Saanum, Wang & Schulz (2023),
"Zero-shot compositional reasoning in a reinforcement learning setting", against any
dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- zero_shot_above_chance (exp0, exp1): probability of choosing the optimal arm on trial 0 of
  the final (compositional) sub-task in the curriculum condition is greater than chance
  (1/6); one-sample t-test on per-participant means.
- curriculum_beats_noncurriculum (exp0, exp1): mean regret on trial 0 of the final
  sub-task is lower in the curriculum than in the non-curriculum condition; independent
  two-sample t-test on per-participant means.
- learning_continues_in_composition (exp0, exp1): within the final sub-task (curriculum
  condition), regret decreases across trials 0..4 (participants keep learning instead of
  performing perfect zero-shot inference); one-sample t-test on per-participant mean
  trial slopes.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1"]
CHANCE = 1 / 6.0


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame} for ./{exp}.csv in CWD or --<exp> overrides.

    Required columns: participant_id, task_id, trial, response, regret, phase,
    subtask, bestoption.
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _first_trial_final(df: pd.DataFrame, phase: str) -> pd.DataFrame:
    """One row per participant: mean optimal-choice probability & mean regret on
    trial 0 of the final (compositional) sub-task for the given phase."""
    sub = df[(df["phase"] == phase) & (df["subtask"] == 2) & (df["trial"] == 0)]
    per = sub.groupby("participant_id", as_index=False).apply(
        lambda g: pd.Series({
            "opt_prob": float((g["response"] == g["bestoption"]).mean()),
            "regret": float(g["regret"].mean()),
        })
    )
    return per


def check_zero_shot_above_chance(data: dict[str, pd.DataFrame], exp: str) -> dict:
    """\"We see from the regrets that people performed better than chance right from the
    outset for the curriculum condition (Mean (M)=2.163, Standard Error (SE)=0.116;
    t=-19.57, p<0.001) whereas they start at chance-level for the non-curriculum
    condition\" — Jagadish et al., p.3, Results/Experiment 1."""
    per = _first_trial_final(data[exp], "curriculum")
    t, p = stats.ttest_1samp(per["opt_prob"], CHANCE)
    effect_size = per["opt_prob"].mean() - CHANCE
    return {
        "effect_name": f"zero_shot_above_chance_{exp}",
        "experiment": exp,
        "original_effect_size": 0.215 if exp == "exp0" else 0.170,
        "effect_size": effect_size,
        "reproduced": bool(effect_size > 0 and p < 0.05),
    }


def check_curriculum_beats_noncurriculum(data: dict[str, pd.DataFrame], exp: str) -> dict:
    """\"This analysis revealed that participants in the curriculum condition had a
    significantly lower regret on the first trial of the final sub-task than participants
    in the non-curriculum condition (β = -1.18 ± 0.115; z = -10.24, p < 0.001)\" —
    Jagadish et al., p.3, Results/Experiment 1."""
    cur = _first_trial_final(data[exp], "curriculum")
    non = _first_trial_final(data[exp], "non_curriculum")
    t, p = stats.ttest_ind(cur["regret"], non["regret"], equal_var=False)
    effect_size = cur["regret"].mean() - non["regret"].mean()
    return {
        "effect_name": f"curriculum_beats_noncurriculum_{exp}",
        "experiment": exp,
        "original_effect_size": -1.18,
        "effect_size": effect_size,
        "reproduced": bool(effect_size < 0 and p < 0.05),
    }


def check_learning_continues_in_composition(data: dict[str, pd.DataFrame], exp: str) -> dict:
    """\"The results of this model showed a significant fixed effect of trial number
    (β = -0.32 ± 0.02; z = -13.88, p < 0.001) on to regret, confirming that the
    performance of participants improved with additional interactions. The observed
    improvement in the curriculum condition (β = -0.21 ± 0.02; z = -12.26, p < 0.001) was
    generally weaker than that in the non-curriculum condition\" — Jagadish
    et al., p.3, Results/Experiment 1."""
    fin = data[exp][(data[exp]["phase"] == "curriculum") & (data[exp]["subtask"] == 2)]
    slopes = (
        fin.groupby(["participant_id", "task"])
        .apply(lambda g: np.polyfit(g["trial"], g["regret"], 1)[0])
        .groupby("participant_id")
        .mean()
    )
    t, p = stats.ttest_1samp(slopes, 0.0)
    effect_size = slopes.mean()
    return {
        "effect_name": f"learning_continues_in_composition_{exp}",
        "experiment": exp,
        "original_effect_size": -0.21 if exp == "exp0" else -0.216,
        "effect_size": effect_size,
        "reproduced": bool(effect_size < 0 and p < 0.05),
    }


EFFECTS = [
    lambda data: check_zero_shot_above_chance(data, "exp0"),
    lambda data: check_zero_shot_above_chance(data, "exp1"),
    lambda data: check_curriculum_beats_noncurriculum(data, "exp0"),
    lambda data: check_curriculum_beats_noncurriculum(data, "exp1"),
    lambda data: check_learning_continues_in_composition(data, "exp0"),
    lambda data: check_learning_continues_in_composition(data, "exp1"),
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing — pure return value."""
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